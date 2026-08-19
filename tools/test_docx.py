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


if __name__ == "__main__":
    unittest.main()
