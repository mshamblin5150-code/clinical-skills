"""One file for the pair, the way ``test_icd10.py`` covers its builder and reader.

**The round trip is the test.** A ``.docx`` Word refuses to open is byte-for-byte
indistinguishable from a good one until Word opens it, and there is no Word here -- so
what these assert is that the archive has the parts the format requires, that every part
parses as XML, and that ``docx_read`` gets back what ``docx_write`` was given. That
catches the failure that actually happens (a malformed part, an unescaped ``&``) and
does not catch the one that cannot be checked without Word.

Nothing here opens a real document. The faculty material and the clinician's submitted
work are both outside this repo.
"""

from __future__ import annotations

import contextlib
import io
import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import docx_read
import docx_write


class TheArchiveHasTheRequiredParts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "sample.docx"
        docx_write.write_docx("# Title\n\nA paragraph.\n", self.path)

    def tearDown(self):
        self.directory.cleanup()

    def test_every_part_the_format_requires_is_present(self):
        with zipfile.ZipFile(self.path) as archive:
            names = set(archive.namelist())
        for required in (
            "[Content_Types].xml",
            "_rels/.rels",
            "word/_rels/document.xml.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/numbering.xml",
            "word/header1.xml",
        ):
            self.assertIn(required, names)

    def test_every_part_parses_as_xml(self):
        with zipfile.ZipFile(self.path) as archive:
            for name in archive.namelist():
                ElementTree.fromstring(archive.read(name))

    def test_every_declared_override_is_a_part_that_is_there(self):
        """A part declared in ``[Content_Types].xml`` and absent is a file Word rejects."""
        with zipfile.ZipFile(self.path) as archive:
            names = set(archive.namelist())
            root = ElementTree.fromstring(archive.read("[Content_Types].xml"))
        overrides = [
            node.get("PartName").lstrip("/") for node in root if node.tag.endswith("}Override")
        ]
        self.assertIn("word/header1.xml", overrides)
        for part in overrides:
            self.assertIn(part, names)

    def test_every_word_part_carries_its_own_override(self):
        """The other direction, and it has to name the Override rather than any declaration.

        ``[Content_Types].xml`` carries ``Default Extension="xml"``, so *every* part under
        ``word/`` is already declared -- as ``application/xml``, which is the wrong type
        for all of them. A test that accepted the Default would pass for a document part,
        a styles part and a header part alike, and would read as covering the failure it
        cannot see. So each one is required to carry an Override of its own.
        """
        with zipfile.ZipFile(self.path) as archive:
            names = set(archive.namelist())
            root = ElementTree.fromstring(archive.read("[Content_Types].xml"))
        overrides = {
            node.get("PartName").lstrip("/") for node in root if node.tag.endswith("}Override")
        }
        extensions = {
            node.get("Extension").lower() for node in root if node.tag.endswith("}Default")
        }
        typed = [n for n in names if n.startswith("word/") and n.endswith(".xml")]
        self.assertIn("word/header1.xml", typed)
        for name in typed:
            self.assertIn(name, overrides, name)
        for name in names - set(typed):
            self.assertIn(name.rsplit(".", 1)[-1].lower(), extensions, name)

    def test_every_relationship_the_document_names_resolves(self):
        """A ``headerReference`` naming a part that is missing is what this catches."""
        with zipfile.ZipFile(self.path) as archive:
            names = set(archive.namelist())
            rels = ElementTree.fromstring(archive.read("word/_rels/document.xml.rels"))
            document = archive.read("word/document.xml").decode("utf-8")
        targets = {node.get("Id"): node.get("Target") for node in rels}
        self.assertTrue(targets)
        for identifier, target in targets.items():
            self.assertIn("word/" + target, names, identifier)
        for identifier in re.findall(r'r:id="([^"]+)"', document):
            self.assertIn(identifier, targets)

    def test_the_header_carries_the_page_field_and_no_prose(self):
        with zipfile.ZipFile(self.path) as archive:
            header = archive.read("word/header1.xml").decode("utf-8")
        self.assertIn('w:instr="PAGE"', header)
        self.assertIn('<w:jc w:val="right"/>', header)


class TheRoundTrip(unittest.TestCase):
    def render(self, markdown):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "round.docx"
            docx_write.write_docx(markdown, path)
            return docx_read.read_docx(path)

    def test_headings_and_paragraphs_come_back(self):
        lines = self.render("# Assessment\n\nShe is 16 weeks pregnant.\n")
        self.assertIn("Assessment", lines)
        self.assertIn("She is 16 weeks pregnant.", lines)

    def test_bold_and_italic_survive_as_text(self):
        lines = self.render("A **favored** and *less likely* entry.\n")
        self.assertIn("A favored and less likely entry.", lines)

    def test_a_table_comes_back_row_by_row(self):
        lines = self.render("| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n")
        self.assertIn("Drug | Dose", lines)
        self.assertIn("Rocephin | 500 mg", lines)

    def test_the_separator_rule_is_not_a_row(self):
        lines = self.render("| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n")
        self.assertNotIn("--- | ---", lines)

    def test_list_markers_are_not_written_into_the_text(self):
        """Word draws the bullet from the numbering part, so the text must not carry one."""
        lines = self.render("- Order NAAT\n- Treat the partner\n")
        self.assertIn("Order NAAT", lines)
        self.assertNotIn("- Order NAAT", lines)

    def test_an_ampersand_does_not_break_the_part(self):
        """The one failure a round trip really does catch."""
        lines = self.render("Hsu, K., & Khosropour, C. (2026). Chlamydia <adults>.\n")
        self.assertIn("Hsu, K., & Khosropour, C. (2026). Chlamydia <adults>.", lines)


class TheReferenceStyle(unittest.TestCase):
    """APA 7's hanging indent is applied by heading, not by guessing at a line's shape."""

    def test_paragraphs_after_a_references_heading_take_the_hanging_indent(self):
        xml = docx_write.body_xml("# References\n\nRoss, J. (2025). Pelvic inflammatory disease.\n")
        self.assertIn('<w:pStyle w:val="Reference"/>', xml)

    def test_a_document_with_no_references_section_pays_nothing(self):
        xml = docx_write.body_xml("# Plan\n\nRocephin 500 mg IM once.\n")
        self.assertNotIn('w:val="Reference"', xml)

    def test_the_switch_is_case_insensitive_and_survives_a_longer_heading(self):
        xml = docx_write.body_xml("## references and evidence\n\nRoss, J. (2025).\n")
        self.assertIn('<w:pStyle w:val="Reference"/>', xml)

    def test_the_singular_reference_heading_switches_too(self):
        """APA permits ``Reference`` for a one-entry list -- ``apa7.md`` section 1."""
        xml = docx_write.body_xml("# Reference\n\nRoss, J. (2025). Pelvic inflammatory disease.\n")
        self.assertIn('<w:pStyle w:val="Reference"/>', xml)

    def test_a_heading_that_merely_begins_with_the_same_letters_does_not_switch(self):
        xml = docx_write.body_xml("# Referral\n\nSent to obstetrics.\n")
        self.assertNotIn('w:val="Reference"', xml)

    def test_the_singular_matches_only_when_it_is_the_whole_heading(self):
        """``Reference Ranges`` is a lab heading, not a reference list.

        The plural keeps its prefix match -- ``References and Evidence`` is blessed
        above, and no ordinary heading begins with the plural. The singular cannot take
        that license, because ``Reference`` opens several phrases a clinical document
        really writes, and a wrong match here does not merely indent: since #217 it also
        centers the heading and breaks the page.
        """
        for heading in ("# Reference Ranges", "# Reference Values", "## Reference List"):
            xml = docx_write.body_xml(heading + "\n\nSodium 135 to 145.\n")
            self.assertNotIn('w:val="Reference"', xml, heading)
            self.assertNotIn("<w:pageBreakBefore/>", xml, heading)
            self.assertNotIn('<w:jc w:val="center"/>', xml, heading)

    def test_a_later_heading_ends_the_reference_list(self):
        xml = docx_write.body_xml("# References\n\nRoss, J. (2025).\n\n# Appendix\n\nA note.\n")
        self.assertEqual(xml.count('<w:pStyle w:val="Reference"/>'), 1)


class TheReferenceListPageSetup(unittest.TestCase):
    """APA 7 section 2.12 -- a new page, a centered label, a page number on every page."""

    BOTH = "# Assessment\n\nText.\n\n# References\n\nRoss, J. (2025).\n"

    def test_the_references_heading_is_centered(self):
        xml = docx_write.body_xml(self.BOTH)
        heading = xml[: xml.index("References")]
        self.assertIn('<w:jc w:val="center"/>', heading.rsplit("<w:p>", 1)[-1])

    def test_the_references_heading_starts_a_new_page(self):
        xml = docx_write.body_xml(self.BOTH)
        heading = xml[: xml.index("References")]
        self.assertIn("<w:pageBreakBefore/>", heading.rsplit("<w:p>", 1)[-1])

    def test_an_ordinary_heading_gets_neither(self):
        xml = docx_write.body_xml("# Assessment\n\nText.\n\n## Plan\n\nRocephin.\n")
        self.assertNotIn("<w:pageBreakBefore/>", xml)
        self.assertNotIn('<w:jc w:val="center"/>', xml)

    def test_a_document_that_opens_on_references_does_not_lead_with_a_blank_page(self):
        """``pageBreakBefore`` on the first paragraph renders an empty first page."""
        xml = docx_write.body_xml("\n# References\n\nRoss, J. (2025).\n")
        self.assertNotIn("<w:pageBreakBefore/>", xml)
        self.assertIn('<w:jc w:val="center"/>', xml)

    def test_the_section_names_the_header_part(self):
        xml = docx_write.document_xml("# Title\n\nText.\n")
        self.assertIn('<w:headerReference w:type="default"', xml)
        self.assertIn('xmlns:r="', xml)

    def test_the_page_number_is_not_prose_the_reader_picks_up(self):
        """``docx_read`` reads ``word/document.xml`` only, so the field stays out of it."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "header.docx"
            docx_write.write_docx("# Title\n\nOne paragraph.\n", path)
            lines = docx_read.read_docx(path)
        self.assertEqual([line for line in lines if line.strip()], ["Title", "One paragraph."])


class TheHeadingLevels(unittest.TestCase):
    """APA 7 section 2.27: every level is body size, and the level shows in the styling."""

    def style(self, level):
        opening = '<w:style w:type="paragraph" w:styleId="Heading{n}">'.format(n=level)
        start = docx_write.STYLES.index(opening)
        return docx_write.STYLES[start : docx_write.STYLES.index("</w:style>", start)]

    def test_every_level_is_body_size(self):
        for level in (1, 2, 3, 4):
            self.assertIn('<w:sz w:val="24"/>', self.style(level))
        self.assertNotIn('w:val="28"', docx_write.STYLES)
        self.assertNotIn('w:val="26"', docx_write.STYLES)

    def test_every_level_is_bold(self):
        for level in (1, 2, 3, 4):
            self.assertIn("<w:b/>", self.style(level))

    def test_level_one_is_centered_and_the_rest_are_not(self):
        self.assertIn('<w:jc w:val="center"/>', self.style(1))
        for level in (2, 3, 4):
            self.assertNotIn("<w:jc ", self.style(level))

    def test_level_three_is_the_italic_one(self):
        self.assertIn("<w:i/>", self.style(3))
        for level in (1, 2, 4):
            self.assertNotIn("<w:i/>", self.style(level))

    def test_level_four_is_the_indented_one(self):
        self.assertIn('<w:ind w:left="{h}"/>'.format(h=docx_write.HANGING), self.style(4))
        for level in (1, 2, 3):
            self.assertNotIn("<w:ind ", self.style(level))

    def test_the_paragraph_properties_are_in_schema_order(self):
        """``CT_PPrBase`` is a sequence; Word declines a file that reorders it."""
        order = ["<w:keepNext/>", "<w:spacing ", "<w:ind ", "<w:jc ", "<w:outlineLvl "]
        for level in (1, 2, 3, 4):
            body = self.style(level)
            seen = [body.index(tag) for tag in order if tag in body]
            self.assertEqual(seen, sorted(seen), level)


class TheHomoglyphFold(unittest.TestCase):
    """The UpToDate paste is salted, and a search over it fails silently without this."""

    def test_a_salted_word_folds_back_to_ascii(self):
        salted = "Сerviϲitiѕ"  # Cyrillic C, Greek lunate sigma, Cyrillic dze
        self.assertNotEqual(salted, "Cervicitis")
        self.assertEqual(docx_read.normalize(salted), "Cervicitis")

    def test_plain_ascii_is_left_alone(self):
        text = "Neisseria gonorrhoeae, 16 weeks, 100.7 F"
        self.assertEqual(docx_read.normalize(text), text)

    def test_the_map_only_holds_single_characters(self):
        for key, value in docx_read.HOMOGLYPHS.items():
            self.assertEqual(len(key), 1)
            self.assertEqual(len(value), 1)
            self.assertNotEqual(key, value)


def rendered_parts(markdown):
    """Render a document and read the parts back **out of the archive**.

    ``body_xml`` and ``STYLES`` are what the module *would* write; this is what a reader
    of the file actually gets, and the two are only the same while ``write_docx`` puts
    each one where it says it does. #220's own comment names the difference -- section 6's
    rows were measured by rendering a document and reading ``word/document.xml``, and a
    test asserting against the source's output has not used that instrument. It is also
    this file's standing rule: *the round trip is the test*.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "parts.docx"
        docx_write.write_docx(markdown, path)
        with zipfile.ZipFile(path) as archive:
            return {n: archive.read(n).decode("utf-8") for n in archive.namelist()}


class TheBodyFirstLineIndent(unittest.TestCase):
    """APA 7 section 2.24 -- every body paragraph, and only a body paragraph.

    The rule has carve-outs and each one is a separate branch of ``body_xml``: a heading
    takes none, a reference entry takes the *hanging* indent instead and a first line
    would cancel it, a list item draws its indent from ``numbering.xml``, and a table
    cell is not a body paragraph at all.

    Read out of the rendered archive rather than off ``body_xml``, which is how section
    6's rows were measured and is what makes this a check on the artifact.
    """

    def document(self, markdown):
        return rendered_parts(markdown)["word/document.xml"]

    def test_a_plain_paragraph_takes_the_half_inch_first_line(self):
        xml = self.document("She is 16 weeks pregnant.\n")
        self.assertIn('<w:ind w:firstLine="{f}"/>'.format(f=docx_write.FIRST_LINE), xml)

    def test_the_indent_is_half_an_inch(self):
        self.assertEqual(docx_write.FIRST_LINE, 720)

    def test_a_heading_takes_none(self):
        self.assertNotIn("w:firstLine", self.document("# Assessment\n"))

    def test_a_reference_entry_takes_none(self):
        """The ``Reference`` style already sets ``w:ind``; a first line would cancel it."""
        xml = self.document("# References\n\nRoss, J. (2025). Pelvic disease.\n")
        self.assertIn('<w:pStyle w:val="Reference"/>', xml)
        self.assertNotIn("w:firstLine", xml)

    def test_a_list_item_takes_none(self):
        """Word draws a list item's indent from ``numbering.xml``."""
        for markdown in ("- Order NAAT\n", "1. Order NAAT\n"):
            xml = self.document(markdown)
            self.assertIn('<w:pStyle w:val="ListParagraph"/>', xml, markdown)
            self.assertNotIn("w:firstLine", xml, markdown)

    def test_a_table_cell_takes_none(self):
        xml = self.document("| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n")
        self.assertNotIn("w:firstLine", xml)

    def test_exactly_one_paragraph_of_a_mixed_document_takes_it(self):
        """The whole rule in one assertion, on a document carrying every branch."""
        xml = self.document(
            "# Assessment\n\nShe is 16 weeks pregnant.\n\n- Order NAAT\n\n"
            "| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n\n"
            "# References\n\nRoss, J. (2025). Pelvic disease.\n"
        )
        self.assertEqual(xml.count("w:firstLine"), 1)

    def test_the_indent_is_written_before_the_alignment(self):
        """``CT_PPrBase`` is a sequence: ``numPr``, then ``ind``, then ``jc``.

        No branch of ``body_xml`` asks for all three today, which is exactly why this
        drives ``para`` directly -- the order is a guarantee of the constructor rather
        than an accident of which callers happen to exist.
        """
        xml = docx_write.para("x", num_id=1, first_line=True, align="center")
        seen = [xml.index(tag) for tag in ("<w:numPr>", "<w:ind ", "<w:jc ")]
        self.assertEqual(seen, sorted(seen))


class TheTableRules(unittest.TestCase):
    """APA 7 section 7.8 -- horizontal rules only, and never a vertical one.

    Three rules and no more: above the header, below the header, below the last row.
    A full grid is what this drew until #220, and the clinician ruled it unconditional
    on 2026-08-19 rather than switchable, because the only consumer of this renderer is
    an APA document.

    Read out of the rendered archive, on ``TheBodyFirstLineIndent``'s reasoning -- and
    here it buys something specific, since the table's borders are set in two parts that
    ship in two different files.
    """

    ROWS = "| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n| Doxycycline | 100 mg |\n"

    def setUp(self):
        self.parts = rendered_parts(self.ROWS)
        self.document = self.parts["word/document.xml"]
        self.styles = self.parts["word/styles.xml"]

    def test_no_vertical_rule_is_drawn_anywhere(self):
        for edge in ("insideV", "left", "right"):
            self.assertNotIn('<w:{e} w:val="single"'.format(e=edge), self.document, edge)

    def test_the_table_is_closed_top_and_bottom(self):
        self.assertIn('<w:top w:val="single"', self.document)
        self.assertIn('<w:bottom w:val="single"', self.document)

    def test_no_rule_runs_between_the_body_rows(self):
        self.assertNotIn('<w:insideH w:val="single"', self.document)

    def test_the_header_row_carries_a_rule_beneath_it(self):
        """The one rule that is not a table edge, so it is set on the header's cells."""
        header = self.document[: self.document.index("Rocephin")]
        self.assertIn("<w:tcBorders>", header)
        self.assertIn('<w:bottom w:val="single"', header.rsplit("<w:tcBorders>", 1)[-1])

    def test_no_body_cell_carries_a_rule(self):
        self.assertNotIn("<w:tcBorders>", self.document[self.document.index("Rocephin") :])

    def test_the_cell_properties_are_in_schema_order(self):
        """``CT_TcPrBase`` is a sequence: ``tcW`` before ``tcBorders``."""
        cell = self.document[self.document.index("<w:tc>") :]
        self.assertLess(cell.index("<w:tcW "), cell.index("<w:tcBorders>"))

    def test_the_table_style_draws_no_grid_either(self):
        """``BORDERS`` overrides the style, so a grid left in it is a latent grid."""
        style = self.styles[self.styles.index('w:type="table"') :]
        for edge in ("insideV", "insideH", "left", "right"):
            self.assertNotIn('<w:{e} w:val="single"'.format(e=edge), style, edge)

    def test_the_style_is_not_called_table_grid_any_more(self):
        """A style named ``Table Grid`` that draws no grid is a lie inside the file."""
        self.assertNotIn("TableGrid", self.styles)
        self.assertNotIn("TableGrid", self.document)

    def test_the_table_names_a_style_the_shipped_styles_part_declares(self):
        """The two halves ship in different parts, which is what reading the zip buys."""
        named = re.search(r'<w:tblStyle w:val="([^"]+)"/>', self.document).group(1)
        self.assertIn('w:type="table" w:styleId="{s}"'.format(s=named), self.styles)

    def test_a_header_only_table_is_still_closed(self):
        xml = rendered_parts("| Drug | Dose |\n| --- | --- |\n")["word/document.xml"]
        self.assertIn('<w:top w:val="single"', xml)
        self.assertIn('<w:bottom w:val="single"', xml)


class TheTwoCopiesOfWhatTheRendererApplies(unittest.TestCase):
    """#220's own comment: the list lives in two files and nothing pinned them together.

    ``apa7.md`` section 6 carries it for a reader of the skill and ``docx_write.py``
    carries it for a reader of the code, and a **prose** edit to either failed nothing
    -- so the reader who was misled is the one who checked the file nearer to hand.
    The repair is ``REFERENCE_HEADING``'s: the docstring's copy stopped being a copy by
    becoming ``NOT_APPLIED``, one object, and this asserts the sheet names the same
    items.

    **Both of section 6's tables are read**, which the comment asked for and the first
    version of this class did not do -- it parsed the *not applied* table alone, so a row
    sitting in both tables at once, or wrongly promoted into the applied one, was
    invisible to it.

    **What it does not reach** is whether a row's verdict is *true*. A row moved to the
    *applied* table while the renderer still does not apply it passes every assertion
    here, and stays a behavior test's job -- ``TheBodyFirstLineIndent`` and
    ``TheTableRules`` are the two this ticket added.
    """

    SHEET = Path(__file__).resolve().parent.parent / "skills" / "practicum-case-study"
    SPLIT = "still not applied"

    def section_six(self):
        text = (self.SHEET / "reference" / "apa7.md").read_text(encoding="utf-8")
        return text[text.index("## 6.") : text.index("## 7.")]

    def first_cells(self, block):
        return docx_write.table_first_cells(block)

    def applied(self):
        return self.first_cells(self.section_six().split(self.SPLIT)[0])

    def not_applied(self):
        return self.first_cells(self.section_six().split(self.SPLIT)[1])

    def test_both_tables_are_found(self):
        """The instrument is live: a parser finding nothing would pass every row below."""
        self.assertTrue(self.applied())
        self.assertTrue(self.not_applied())

    def test_every_item_the_module_names_is_a_row_on_the_sheet(self):
        rows = self.not_applied()
        for key, _ in docx_write.NOT_APPLIED:
            self.assertEqual(len([r for r in rows if key in r]), 1, key)

    def test_the_sheet_names_nothing_the_module_does_not(self):
        self.assertEqual(len(self.not_applied()), len(docx_write.NOT_APPLIED))

    def test_no_item_sits_in_both_tables(self):
        """A row promoted by editing one table and not the other is the failure here."""
        applied = " ".join(self.applied())
        for key, _ in docx_write.NOT_APPLIED:
            self.assertNotIn(key, applied, key)

    def test_the_two_rows_this_ticket_applied_are_in_the_applied_table(self):
        """#220's rows, asserted where they are rather than only where they are not."""
        applied = " ".join(self.applied()).lower()
        for landed in ("first-line indent", "horizontal rules"):
            self.assertIn(landed, applied, landed)

    def test_every_entry_carries_a_key_and_a_reason(self):
        """The reason is what a reader of the code reads in place of the old prose."""
        for key, reason in docx_write.NOT_APPLIED:
            self.assertTrue(key.strip(), key)
            self.assertGreater(len(reason.split()), 8, key)


class TheRendererClaimsInStepSeven(unittest.TestCase):
    """#220's third comment: a fourth copy of renderer behavior, pinned by nothing.

    ``skills/practicum-case-study/SKILL.md`` step 7's defect table explains two of its
    defects by stating what the renderer does, and only the heading rule was pinned --
    by importing
    ``REFERENCE_HEADING`` rather than restating it. These two were prose with nothing
    behind them, and the comment named them as in scope here.

    Both directions are asserted, because either alone reads as agreement: the sentence
    is still in the table, **and** the renderer still behaves the way it says. A reword
    fails the first and a behavior change fails the second.
    """

    SKILL = Path(__file__).resolve().parent.parent / "skills" / "practicum-case-study"

    LIST_STYLE = "the renderer gives a list its list style and the hanging indent is lost"
    ONE_PER_LINE = "the renderer sets every non-blank line as its own paragraph"

    def skill_text(self):
        return (self.SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_the_defect_table_still_states_both(self):
        text = self.skill_text()
        self.assertIn(self.LIST_STYLE, text)
        self.assertIn(self.ONE_PER_LINE, text)

    def test_a_bullet_in_the_reference_list_really_loses_the_hanging_indent(self):
        xml = rendered_parts("# References\n\n- Ross, J. (2025). Pelvic disease.\n")[
            "word/document.xml"
        ]
        self.assertIn('<w:pStyle w:val="ListParagraph"/>', xml)
        self.assertNotIn('<w:pStyle w:val="Reference"/>', xml)

    def test_a_hard_wrapped_entry_really_becomes_two_paragraphs(self):
        xml = rendered_parts("# References\n\nRoss, J. (2025). Pelvic\ndisease. UpToDate.\n")[
            "word/document.xml"
        ]
        self.assertEqual(xml.count('<w:pStyle w:val="Reference"/>'), 2)


SKILL = Path(__file__).resolve().parent.parent / "skills" / "practicum-case-study"


def section_eight():
    """``style.md`` section 8, sliced once rather than in each class that reads it."""
    text = (SKILL / "reference" / "style.md").read_text(encoding="utf-8")
    return text[text.index("## 8.") : text.index("## 9.")]


class TheRxTableTheStyleSheetDocuments(unittest.TestCase):
    """#280: nothing bound ``style.md`` section 8 to what this renderer does with it.

    That sheet specified the ``Rx:`` block as a **one-column** table whose first row
    faked three columns with ``&#124;``, and two of the five defects the clinician found
    in the rendered Module 1 submission came out of it: the entity reached the page as
    literal text, a run that reached for the Markdown spelling instead left a backslash
    in the cell, and the whole prescription rendered into column 1. **Both were
    downstream of a documented shape that had never been rendered.**

    #293 repaired the shape and taught ``split_row`` and ``table`` the rest. **The gap
    this class closes is the one that let it happen**: every ``Rx:`` test that landed
    with those repairs uses rows typed into this file, so the sheet is still correct only
    because somebody rendered it once and looked. Here the table is **extracted from the
    sheet** and run through the renderer -- ``TheTwoCopiesOfWhatTheRendererApplies``'s
    arrangement pointed at a *shape* rather than at a list.

    **What it does not reach** is whether the six rows are the *right* six. A sheet that
    renamed ``Disp:`` to something a pharmacy will not fill passes every row below, and
    stays the clinician's reading.
    """

    def section_eight(self):
        return section_eight()

    def block(self):
        tables = docx_write.markdown_tables(section_eight())
        self.assertTrue(tables, "no table in section 8 -- the instrument is dead")
        return tables[0]

    def rows(self):
        """Every ``w:tr`` of the rendered table, as a list of its ``w:tc`` fragments."""
        xml = rendered_parts(self.block())["word/document.xml"]
        return [
            re.findall(r"<w:tc>.*?</w:tc>", row, re.DOTALL)
            for row in re.findall(r"<w:tr>.*?</w:tr>", xml, re.DOTALL)
        ]

    def span(self, cell):
        found = re.search(r'<w:gridSpan w:val="(\d+)"/>', cell)
        return int(found.group(1)) if found else 1

    def test_the_sheets_table_renders_as_a_header_band_over_six_rows(self):
        """The instrument is live: a parser finding nothing would pass every row below.

        **Seven ``w:tr`` under a heading that says six**, and the extra one is the
        blank header band the ``---`` rule needs above it. The heading counts the rows a
        prescriber fills in, which is the honest thing for it to count and is why this
        is asserted rather than left for a reader to trip over.
        """
        self.assertEqual(len(self.rows()), 7)
        band = ["".join(re.findall(r"<w:t[ >]", c)) for c in self.rows()[0]]
        self.assertEqual(band, ["", "", ""])

    def test_the_grid_is_three_columns_wide(self):
        xml = rendered_parts(self.block())["word/document.xml"]
        grid = re.search(r"<w:tblGrid>.*?</w:tblGrid>", xml, re.DOTALL).group(0)
        self.assertEqual(grid.count("<w:gridCol"), 3)

    def test_the_patient_row_declares_three_cells(self):
        """The row the entity was faking. Three real cells, none of them spanning."""
        patient = self.rows()[1]
        self.assertEqual(len(patient), 3)
        self.assertEqual([self.span(c) for c in patient], [1, 1, 1])

    def test_each_single_field_row_spans_the_whole_width(self):
        """The drug, ``Disp:``, ``Sig:`` and signature rows carry one field each.

        Sitting in column 1 with two empty cells beside it is the second half of the
        recorded defect -- *"everything was put into the left sided column"*.
        """
        rows = self.rows()
        for index in (2, 3, 4, 5):
            self.assertEqual(len(rows[index]), 1, index)
            self.assertEqual(self.span(rows[index][0]), 3, index)

    def test_the_refill_row_is_two_cells_and_the_dea_line_sits_right(self):
        refill = self.rows()[6]
        self.assertEqual(len(refill), 2)
        self.assertEqual([self.span(c) for c in refill], [1, 2])
        self.assertNotIn('<w:jc w:val="right"/>', refill[0])
        self.assertIn('<w:jc w:val="right"/>', refill[1])

    def test_no_cell_carries_a_separator_as_text(self):
        """#280's general row, asserted on the table it was recorded against."""
        self.assertEqual(docx_write.separator_artifacts(self.block()), [])

    def test_the_heading_states_the_width_the_table_renders_to(self):
        """It read *a fixed six-row table* and named no width at all, while the shape
        under it was one column faking three."""
        heading = self.section_eight().splitlines()[0]
        self.assertIn("six-row", heading)
        self.assertIn("three columns wide", heading)


class NoDocumentedTableRendersItsOwnSeparator(unittest.TestCase):
    """#280's general row: **no documented table shape in this skill may render to text
    containing its own separator syntax.**

    The ticket's open decision was whether to generalize past section 8, and it worried
    that a wider walk *"may fire on tables that document Markdown rather than prescribing
    output"*. Measured over the sheets rather than argued: every table in
    ``skills/practicum-case-study/reference/`` is a shape a run copies or a legend a run
    reads, **not one of them documents Markdown syntax**, and only section 8's ever
    carried an escape. So the wider walk costs nothing and fires on the one recorded
    defect.

    **What it does not reach** is a table outside these sheets. ``SKILL.md``'s own are
    prose about the work -- a defect table, a check table -- rather than shapes a draft
    copies, so they are outside the row's *statement* rather than merely unwalked; that
    was **measured** rather than assumed, by running this scanner over every table in
    that file and finding none that fires. #137's shape is a generalization made from
    the files a pass had open, so the fix for it is to go and look.

    A documented shape that renders cleanly and is *wrong* passes here as it does
    everywhere.
    """

    SHEETS = SKILL / "reference"

    # A floor rather than the count, on #143's terms: a sheet gaining a table must not
    # turn the suite red, and a walk that found nothing must not read as a clean sweep.
    FLOOR = 9

    def tables(self):
        found = []
        for sheet in sorted(self.SHEETS.glob("*.md")):
            for block in docx_write.markdown_tables(sheet.read_text(encoding="utf-8")):
                found.append((sheet.name, block))
        return found

    def test_the_walk_finds_tables_to_grade(self):
        """The instrument is live, on ``TheTwoCopiesOfWhatTheRendererApplies``'s row."""
        self.assertGreaterEqual(len(self.tables()), self.FLOOR)

    def test_no_sheet_documents_a_table_that_renders_its_own_separator(self):
        for name, block in self.tables():
            self.assertEqual(docx_write.separator_artifacts(block), [], name)

    def test_the_detector_fires_on_the_shape_this_ticket_retired(self):
        """A walk that could not see the recorded defect would be a clean sweep proving
        nothing. This is section 8's table as it stood.

        It fires on the **faked width** rather than on the entity, and that is why the
        row is not the one the ticket wrote: since #293 ``split_row`` decodes ``&#124;``,
        so the entity no longer reaches the page at all -- what is left is one cell
        carrying two pipes, a row saying it is three columns wide over a grid that is
        one. The same defect, one layer down.
        """
        retired = (
            "| |\n"
            "| --- |\n"
            "| `<patient placeholder>` &#124; `DOB x-x-xxx` &#124; `NPI # <number>` |\n"
        )
        self.assertIn(
            docx_write.CELL_SEPARATOR, docx_write.separator_artifacts(retired)
        )

    def test_an_escape_the_parser_never_sees_is_still_reported(self):
        """Outside a table nothing consumes either spelling, so both reach the page."""
        for escape in docx_write.PIPE_ESCAPES:
            found = docx_write.separator_artifacts(
                "A stray {e} in a sentence.\n".format(e=escape)
            )
            self.assertIn(escape, found, escape)

    def test_a_backslash_in_a_cell_is_reported(self):
        """The recorded symptom itself -- *"the patient carries a backslash"*. The
        escape limb narrows the ticket's row to a backslash **before a pipe**, because
        that is what the parser consumes, so a lone one would otherwise reach the page
        reported by nothing. Found by the spec axis of ``/code-review``."""
        markdown = "| Head |\n| --- |\n| Jane Doe FNP-C \\ |\n"
        self.assertIn(
            docx_write.CELL_BACKSLASH, docx_write.separator_artifacts(markdown)
        )

    def test_a_backslash_outside_a_table_is_left_alone(self):
        """The declared half of that narrowing, asserted rather than described: in
        running prose a backslash is somebody quoting a path or a pattern, and a
        warning that fires on those is one a run learns to skip."""
        self.assertEqual(
            docx_write.separator_artifacts("A path C:\\temp in prose.\n"), []
        )

    def test_the_prose_that_documents_the_defect_is_a_mention_and_not_a_use(self):
        """**Section 8 explains the retired shape, so both escapes are in that file** --
        one in a sentence naming the spelling that rendered as text, one in the
        clinician's quoted reading of the page.

        The unit is the **table**, so neither is seen. Pointed at the whole section the
        walk reports both, and would fail the sheet that documents the fix -- which is
        ``spelling_scan.py``'s mention-versus-use distinction and #153's *describing the
        rule broke the tool that checks the rule*, arriving here uninvited. Written down
        because the first version of this test asserted the section rather than the
        table and went red on exactly that.
        """
        section = section_eight()
        self.assertEqual(docx_write.separator_artifacts(section), ["&#124;", "\\|"])
        for block in docx_write.markdown_tables(section):
            self.assertEqual(docx_write.separator_artifacts(block), [])

    def test_every_form_the_scanner_reports_is_one_the_parser_consumes(self):
        """``PIPE_ESCAPES`` is declared for the reporting side and read by only one limb
        of ``split_row``, so nothing but this stops the two drifting -- a scanner naming
        a spelling the parser leaves alone would send a run chasing a working cell."""
        for escape in docx_write.PIPE_ESCAPES:
            self.assertEqual(
                docx_write.split_row("| a {e} b | c |".format(e=escape)),
                ["a | b", "c"],
                escape,
            )


class TheRendererWarnsAboutSeparatorArtifacts(unittest.TestCase):
    """Ruled by the clinician on 2026-08-19: the command **warns and never refuses**.

    #280's second comment is why there is a command limb at all -- a test binds the sheet
    for the next author of ``docx_write.py``, and **section 8 is copied by runs, and a
    run executes commands rather than the suite**. So the artifact is reported where a
    run would see it. Refusing was priced and declined: this renderer is on the
    consumer's critical path, and a blocked submission is a worse outcome than a
    separator on the page.

    **The warning is bounded by what the code can draw on** -- a value of
    ``PIPE_ESCAPES``, ``CELL_SEPARATOR`` or ``CELL_BACKSLASH``, and an integer, never a
    run's text -- which is ``reference_scan.py``'s discipline at the width
    ``tracker_bodies.py`` uses it at. A case study draft is written about a patient, and
    printing a cell of it would make this command's output PHI where it was not.
    """

    def render(self, markdown):
        """The written flag is read **inside** the temp directory, which is why it is a
        flag: a path handed back outlives the directory that gave it a meaning."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "draft.md"
            source.write_text(markdown, encoding="utf-8")
            written = Path(directory) / "d.docx"
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = docx_write.main([str(source), str(written)])
            return status, out.getvalue(), err.getvalue(), written.is_file()

    def test_a_clean_draft_warns_about_nothing(self):
        status, _, err, written = self.render("| a | b |\n| --- | --- |\n| one | two |\n")
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertTrue(written)

    def test_an_artifact_warns_and_the_file_is_still_written(self):
        status, out, err, written = self.render(
            "| Head |\n| --- |\n| a &#124; b |\n"
        )
        self.assertEqual(status, 0)
        self.assertIn("wrote", out)
        self.assertTrue(written)
        self.assertIn("warning", err)

    def test_the_warning_names_a_count_and_a_form_and_no_prose_of_the_document(self):
        marker = "Zzyzxine"
        status, _, err, _ = self.render(
            "| Head |\n| --- |\n| {m} &#124; {m} |\n".format(m=marker)
        )
        self.assertEqual(status, 0)
        self.assertNotIn(marker, err)
        self.assertIn("1", err)
        self.assertIn(docx_write.CELL_SEPARATOR, err)

    def test_step_eight_tells_a_run_what_the_warning_means(self):
        """A warning a run cannot read is a warning a run works around. Pinned on
        ``test_reference_scan.py``'s reasoning -- the instruction has to be complete
        without the command, and a reword would otherwise rot it in silence.

        **Whitespace-normalized, which is #221's instrument rather than a nicety.** The
        first version of this matched the line as written and went red the moment the
        paragraph was rewrapped -- a phrase pin cannot see its own sentence hard-wrapped,
        which is exactly what ``test_run_record_claim.py`` was built to get past.
        """
        skill = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn(
            "A `warning:` line from that command means a table row put a cell separator into its own text",
            skill,
        )

    def test_the_sheets_own_rx_table_renders_without_a_word_of_warning(self):
        """The end of the chain: what the sheet documents is what the command accepts."""
        _, _, err, _ = self.render(docx_write.markdown_tables(section_eight())[0])
        self.assertEqual(err, "")


class NotHavingRead(unittest.TestCase):
    """Exit 2 is every way of not having read, on ``guidelines_search.py``'s convention."""

    def test_no_argument_is_two(self):
        self.assertEqual(docx_write.main([]), 2)
        self.assertEqual(docx_read.main([]), 2)

    def test_a_file_that_is_not_a_zip_is_two(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not.docx"
            path.write_text("plain text", encoding="utf-8")
            self.assertEqual(docx_read.main([str(path)]), 2)

    def test_a_zip_with_no_document_part_is_two(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("hello.txt", "nothing here")
            self.assertEqual(docx_read.main([str(path)]), 2)

    def test_a_missing_source_is_two(self):
        self.assertEqual(docx_write.main(["no-such-file.md", "out.docx"]), 2)


class TheDefectsTheClinicianFoundInTheRenderedCaseStudy(unittest.TestCase):
    r"""#215 follow-up. The defects the clinician found by reading the rendered
    document rather than the code, every one invisible in the Markdown source.

    **The count is deliberately not in the class name.** It read ``TheFourDefects``
    for twenty minutes while the ticket, the commit message and ``style.md`` all
    said five, and while the class held more methods than either number -- because
    ``/code-review`` later added two findings of its own here. That is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
    arriving inside the change that cites #143, caught by the tracker sweep.

    They are pinned together because they were found together and because they
    share the property that makes them expensive: **the Markdown looked correct and
    the ``.docx`` did not.** ``TheRoundTrip`` above cannot see any of them --
    ``docx_read`` reads ``word/document.xml`` and three of these live in
    ``word/numbering.xml`` or in cell properties -- so each takes an assertion
    about the part that actually carries the behavior.
    """

    def test_the_bullet_glyph_is_symbol_encoded(self):
        """A box, not a bullet. The run is set in ``Symbol``, which Word looks up by
        code point *in Symbol*; it has no glyph at U+2022, so the bullet rendered as
        an empty square -- *"I don't know what those square blocks are supposed to
        be"*."""
        numbering = docx_write.numbering_xml(1)
        markers = re.findall(r'<w:lvlText w:val="([^"]*)"/>', numbering)
        bullets = [m for m in markers if not m.startswith("%")]
        self.assertTrue(bullets, "no bullet level found")
        for marker in bullets:
            self.assertEqual(marker, "")
            self.assertNotEqual(marker, "•")

    def test_each_section_gets_its_own_numbered_list(self):
        """Two lists under two headings are two ``w:num`` entries, which is the
        whole restart mechanism: Word restarts numbering per ``numId``, so lists
        sharing one are a single list however far apart they sit."""
        body, count = docx_write.render_body(
            "## One\n\n1. a\n2. b\n\n## Two\n\n1. c\n2. d\n"
        )
        self.assertEqual(count, 2)
        used = sorted(set(re.findall(r'<w:numId w:val="(\d+)"/>', body)))
        self.assertEqual(used, ["2", "3"], "the two lists must not share a numId")
        declared = re.findall(
            r'<w:num w:numId="(\d+)">', docx_write.numbering_xml(count)
        )
        self.assertEqual(declared, ["1", "2", "3"])

    def test_a_paragraph_between_items_does_not_restart_the_list(self):
        """The mirror of the rule above, and the reason the reset is keyed on a
        heading rather than on any interruption: an MDM entry may run to a second
        paragraph without becoming a second list."""
        body, count = docx_write.render_body("## One\n\n1. a\n\nprose\n\n2. b\n")
        self.assertEqual(count, 1)
        self.assertEqual(set(re.findall(r'<w:numId w:val="(\d+)"/>', body)), {"2"})

    def test_an_escaped_pipe_is_content_and_not_a_column(self):
        r"""``\|`` is a literal pipe. It used to split the cell and leave the
        backslash sitting in the text -- *"the patient carries a \ and so does the
        end of my titles"*."""
        self.assertEqual(
            docx_write.split_row(r"| `<patient>` \| `DOB x-x-xxx` |"),
            ["`<patient>` | `DOB x-x-xxx`"],
        )
        self.assertEqual(docx_write.split_row("| a | b |"), ["a", "b"])
        self.assertNotIn("\\", docx_write.split_row(r"| x \| y |")[0])

    def test_the_sheets_own_entity_spelling_is_also_a_pipe(self):
        """``style.md`` section 8 wrote the separator as ``&#124;``, which ``esc``
        would otherwise render literally -- so the sheet and a run that copies it
        both arrive at one pipe."""
        self.assertEqual(docx_write.split_row("| a &#124; b |"), ["a | b"])

    def test_a_short_row_merges_instead_of_padding_the_left_column(self):
        """The ``Rx:`` layout. One cell spans the table; a two-cell row puts the
        first on the left and the second on the right. Before this, a short row was
        right-padded with empties -- *"everything was put into the left sided
        column"*."""
        rows = [
            ["", "", ""],
            ["patient", "dob", "npi"],
            ["drug"],
            ["Refill: none", "DEA"],
        ]
        xml = docx_write.table(rows)
        spans = re.findall(r'<w:gridSpan w:val="(\d+)"/>', xml)
        self.assertEqual(spans, ["3", "2"], "one full-width merge, one right cell")
        self.assertIn('<w:jc w:val="right"/>', xml)

    def test_a_rectangular_table_gains_no_spans(self):
        """The intake and results tables must be untouched by the merge rule, which
        is what keeps this a fix rather than a second layout."""
        xml = docx_write.table([["Field", "Value"], ["Age", "26 years"]])
        self.assertNotIn("w:gridSpan", xml)
        self.assertNotIn('<w:jc w:val="right"/>', xml)

    def test_bold_carrying_an_italic_span_emits_no_literal_asterisk(self):
        """The fifth defect, and the one the clinician spotted as *"a * slipped
        past"*: an italicised organism name inside a bold statement used to have its
        asterisks rendered as text, in the Most Likely Clinical Diagnosis line."""
        xml = docx_write.runs(
            "**Acute PID due to *Neisseria gonorrhoeae*, complicating pregnancy.**"
        )
        self.assertNotIn("*", xml)
        self.assertIn("<w:b/><w:i/>", xml)
        self.assertIn("Neisseria gonorrhoeae", xml)

    def test_an_unnested_bold_span_is_unchanged(self):
        """The nesting branch must not fire on ordinary bold, which is almost all
        of it."""
        xml = docx_write.runs("**plain bold**")
        self.assertEqual(xml.count("<w:r>"), 1)
        self.assertIn("<w:b/>", xml)
        self.assertNotIn("<w:i/>", xml)

    def test_run_properties_arrive_in_schema_order(self):
        """``CT_RPr`` is a sequence -- ``rStyle``, ``rFonts``, ``b``, ``i`` -- and
        Word refuses a file whose properties arrive out of order, exactly as
        ``para``'s docstring says of ``CT_PPrBase``. Bold learning to nest made a
        bold-plus-monospace run reachable from ordinary body text for the first
        time, and it was emitting ``<w:b/>`` before ``<w:rFonts/>``."""
        for text, bold in (
            ("**see `tools/x.py` now**", False),
            ("`code`", True),
            ("**a *b* and `c`**", False),
        ):
            xml = docx_write.runs(text, bold=bold)
            for props in re.findall(r"<w:rPr>(.*?)</w:rPr>", xml):
                order = [
                    props.index(tag)
                    for tag in ("<w:rFonts", "<w:b/>", "<w:i/>")
                    if tag in props
                ]
                self.assertEqual(
                    order, sorted(order), "out of CT_RPr order: " + props
                )

    def test_the_body_is_parsed_once_per_render(self):
        """``render_body``'s docstring rejects a second pass over the same Markdown
        as a second parser to keep in step. ``write_docx`` took one anyway, for the
        numbering count, until the #215 follow-up review caught it."""
        calls = []
        original = docx_write.render_body

        def counted(markdown):
            calls.append(markdown)
            return original(markdown)

        docx_write.render_body = counted
        try:
            with tempfile.TemporaryDirectory() as directory:
                docx_write.write_docx(
                    "## A\n\n1. one\n", Path(directory) / "once.docx"
                )
        finally:
            docx_write.render_body = original
        self.assertEqual(len(calls), 1, "the body was parsed more than once")

    def test_the_rendered_document_still_opens_as_xml(self):
        """Every edit above writes into a part Word parses, and a malformed part is
        a file Word declines to open rather than one that looks wrong."""
        source = (
            "## A\n\n1. one\n\n- b\n\n| x | y | z |\n| --- | --- | --- |\n| p |\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "out.docx"
            docx_write.write_docx(source, path)
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if name.endswith(".xml"):
                        ElementTree.fromstring(archive.read(name))


if __name__ == "__main__":
    unittest.main()
