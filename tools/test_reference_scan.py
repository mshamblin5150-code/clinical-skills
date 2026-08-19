"""Cover ``reference_scan``'s parser and rows against synthetic drafts.

Every draft here is written in this file and a temp directory, the way
``test_research_ledger`` builds throwaway ledgers rather than pointing at a real
one. **There is no committed case study and there will not be one**: a finished
draft lives under ``output/`` because it is written about a patient, which is the
same reason ``test_differential_scan`` has no run to point at.

``TheSkillSaysWhatThisChecks`` is the one class that reads committed files, and it
is here for ``test_spelling_scan``'s reason: a scanner that has drifted from the
file a reader opens is worse than no scanner, because it reads as agreement. **It
runs the scanner over the skill's own worked reference list** rather than only
matching strings -- a documented list the scanner would refuse teaches the next run
to write one that fails, and every substring test here would stay green.

``TheRendererAndTheScannerAgreeOnAHeading`` is the other. #217 made the heading the
thing that *applies* the hanging indent, so the scanner and ``docx_write`` reading
that heading differently is a defect neither file can see alone. They share one
matcher, and this asserts they still do.
"""

from __future__ import annotations

import ast
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

import ast

import checks_ledger
import docx_write
import research_ledger
import reference_scan as scan

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"
APA7 = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "apa7.md"

AS_OF = date(2026, 8, 19)

ACOG = (
    "American College of Obstetricians and Gynecologists. (2023). Urinary tract "
    "infections in pregnancy (Practice Bulletin No. 91). https://doi.org/10.1000/acog.91"
)
UPTODATE = (
    "Gupta, K., & Hooton, T. M. (2025). Acute simple cystitis in adult females. "
    "*UpToDate*. Retrieved August 19, 2026, from https://www.uptodate.com/contents/cystitis"
)

BODY = """\
# Case Study

## Medical Decision Making

Nitrofurantoin is first line in the second trimester (American College of
Obstetricians and Gynecologists, 2023), and a urine culture is drawn before the
first dose (Gupta & Hooton, 2025).
"""


def draft(*entries: str, body: str = BODY, heading: str = "## References") -> str:
    """A whole draft: the body, the reference heading, then one entry per line."""
    return body + "\n" + heading + "\n\n" + "\n".join(entries) + "\n"


CLEAN = draft(ACOG, UPTODATE)


def kinds(text: str, as_of: date | None = AS_OF) -> list[str]:
    """The finding kinds one draft produces, in order."""
    return [f.kind for f in scan.findings(scan.read_document(text), as_of)]


def shown_report(text: str, as_of: date | None = AS_OF) -> str:
    """One draft's ``--show`` report, which is the string #218's ruling is about.

    One helper rather than the ``read_document`` / ``survey`` / ``format_report``
    chain written out at each call site: the rows below differ in the draft they
    pass and never in how the report is built, and three copies of the chain is
    three places for one of them to stop being the thing ``--show`` prints.
    """
    return scan.format_report(
        scan.survey(scan.read_document(text), as_of), source="case.md", show=True
    )


class TheParserReadsTheListTheRendererWouldRender(unittest.TestCase):
    def test_the_clean_draft_fails_nothing(self):
        self.assertEqual(kinds(CLEAN), [])

    def test_the_heading_is_found_and_carried(self):
        self.assertEqual(scan.read_document(CLEAN).heading, "References")

    def test_one_line_is_one_entry_because_that_is_what_the_renderer_makes(self):
        document = scan.read_document(CLEAN)
        self.assertEqual(len(document.entries), 2)
        self.assertTrue(document.entries[0].text.startswith("American College"))

    def test_a_document_with_no_reference_section_has_no_heading(self):
        self.assertIsNone(scan.read_document(BODY).heading)

    def test_the_body_stops_at_the_reference_heading(self):
        document = scan.read_document(CLEAN)
        self.assertIn("Nitrofurantoin", document.body)
        self.assertNotIn("Practice Bulletin", document.body)

    def test_a_heading_at_the_same_level_closes_the_list(self):
        text = CLEAN + "\n## Appendix\n\nNot an entry at all.\n"
        self.assertEqual(len(scan.read_document(text).entries), 2)

    def test_a_heading_of_any_level_closes_the_list_because_the_renderer_says_so(self):
        """**This test asserted the opposite when it was written**, on the guess
        that a deeper heading is a note inside the list. ``body_xml`` recomputes
        ``in_references`` on every heading, so a ``### Note`` turns the hanging
        indent off for everything below it -- and the scanner read both entries and
        exited 0 while the renderer set the second one flush. Verified against the
        renderer below rather than assumed a second time."""
        text = draft(ACOG) + "\n### Note\n\n" + UPTODATE + "\n"
        self.assertEqual(len(scan.read_document(text).entries), 1)

    def test_the_renderer_agrees_about_where_the_list_ends(self):
        text = draft(ACOG) + "\n### Note\n\n" + UPTODATE + "\n"
        styled = docx_write.body_xml(text).count('w:val="Reference"')
        self.assertEqual(styled, len(scan.read_document(text).entries))


class TheHeadingIsTheOneAPARequires(unittest.TestCase):
    def _one_citation(self) -> str:
        return "# Case Study\n\nA culture is drawn first (Gupta & Hooton, 2025).\n"

    def test_the_singular_is_permitted_for_a_one_entry_list(self):
        text = draft(UPTODATE, body=self._one_citation(), heading="## Reference")
        self.assertEqual(kinds(text), [])

    def test_works_cited_is_a_finding(self):
        text = draft(ACOG, UPTODATE, heading="## Works Cited")
        self.assertIn(scan.HEADING_NOT_APA, kinds(text))

    def test_reference_list_is_a_finding_and_the_renderer_would_not_style_it(self):
        text = draft(ACOG, UPTODATE, heading="## Reference List")
        found = [f for f in scan.findings(scan.read_document(text), AS_OF) if f.kind == scan.HEADING_NOT_APA]
        self.assertEqual(len(found), 1)
        self.assertIn("no hanging indent", found[0].detail)

    def test_references_cited_is_a_finding_the_renderer_would_still_style(self):
        text = draft(ACOG, UPTODATE, heading="## References Cited")
        found = [f for f in scan.findings(scan.read_document(text), AS_OF) if f.kind == scan.HEADING_NOT_APA]
        self.assertEqual(len(found), 1)
        self.assertNotIn("no hanging indent", found[0].detail)


class AnEntryIsOneParagraphTheRendererWillIndent(unittest.TestCase):
    def test_a_bulleted_entry_is_a_finding(self):
        text = draft("- " + ACOG, UPTODATE)
        self.assertIn(scan.ENTRY_NOT_A_PARAGRAPH, kinds(text))

    def test_a_numbered_entry_is_a_finding(self):
        text = draft("1. " + ACOG, UPTODATE)
        self.assertIn(scan.ENTRY_NOT_A_PARAGRAPH, kinds(text))

    def test_a_marked_entry_is_still_graded_on_everything_else(self):
        """The marker is stripped and the entry read, so a bulleted list does not
        report one finding and hide fourteen."""
        document = scan.read_document(draft("- " + ACOG, UPTODATE))
        self.assertTrue(document.entries[0].text.startswith("American College"))

    def test_a_hard_wrapped_entry_reads_as_a_line_with_no_year(self):
        """The renderer sets every non-blank line as its own paragraph, so a
        wrapped entry is two paragraphs and the second hangs on nothing."""
        wrapped = ACOG[:60] + "\n" + ACOG[60:]
        self.assertIn(scan.ENTRY_HAS_NO_YEAR, kinds(draft(wrapped, UPTODATE)))


class TheCanvasArtifactIsStripped(unittest.TestCase):
    def test_links_to_an_external_site_is_a_finding(self):
        text = draft(ACOG + "Links to an external site.", UPTODATE)
        self.assertIn(scan.CANVAS_ARTIFACT, kinds(text))

    def test_it_is_found_in_the_body_too(self):
        body = BODY.replace("2025)", "2025), Links to an external site.")
        self.assertIn(scan.CANVAS_ARTIFACT, kinds(draft(ACOG, UPTODATE, body=body)))


class SortedIsSorted(unittest.TestCase):
    def test_two_entries_out_of_order_are_a_finding(self):
        self.assertIn(scan.LIST_NOT_SORTED, kinds(draft(UPTODATE, ACOG)))

    def test_the_sorted_list_is_not(self):
        self.assertNotIn(scan.LIST_NOT_SORTED, kinds(CLEAN))

    def test_an_undated_work_sorts_before_its_authors_dated_ones(self):
        """APA puts ``n.d.`` first among one author's entries. Comparing the
        normalized entry alone puts ``2019`` first and fails a correct list."""
        undated = "Hooton, T. M. (n.d.). Acute cystitis. *UpToDate*. Retrieved August 19, 2026, from https://x/a"
        dated = "Hooton, T. M. (2019). Bacteriuria. *UpToDate*. Retrieved August 19, 2026, from https://x/b"
        body = "# Case\n\nBoth (Hooton, n.d.; Hooton, 2019).\n"
        self.assertNotIn(scan.LIST_NOT_SORTED, kinds(draft(undated, dated, body=body)))
        self.assertIn(scan.LIST_NOT_SORTED, kinds(draft(dated, undated, body=body)))


class SameAuthorSameYearTakesALetter(unittest.TestCase):
    A = (
        "Hooton, T. M. (2025a). *UpToDate*. Retrieved August 19, 2026, from "
        "https://www.uptodate.com/contents/aaa"
    )
    B = (
        "Hooton, T. M. (2025b). *UpToDate*. Retrieved August 19, 2026, from "
        "https://www.uptodate.com/contents/bbb"
    )

    def _body(self) -> str:
        return "# Case\n\nBoth topics say so (Hooton, 2025a, 2025b).\n"

    def test_two_undisambiguated_entries_are_a_finding(self):
        plain_a = self.A.replace("2025a", "2025").replace("aaa", "acute-cystitis")
        plain_b = self.B.replace("2025b", "2025").replace("bbb", "bacteriuria")
        text = draft(plain_a, plain_b, body="# Case\n\nBoth (Hooton, 2025).\n")
        self.assertIn(scan.MISSING_AB, kinds(text))

    def test_letters_in_title_order_pass(self):
        a = self.A.replace("*UpToDate*", "Acute cystitis. *UpToDate*")
        b = self.B.replace("*UpToDate*", "Bacteriuria. *UpToDate*")
        self.assertNotIn(scan.AB_OUT_OF_TITLE_ORDER, kinds(draft(a, b, body=self._body())))

    def test_letters_against_title_order_are_a_finding(self):
        a = self.A.replace("*UpToDate*", "Bacteriuria. *UpToDate*")
        b = self.B.replace("*UpToDate*", "Acute cystitis. *UpToDate*")
        self.assertIn(scan.AB_OUT_OF_TITLE_ORDER, kinds(draft(a, b, body=self._body())))

    def test_the_apa_worked_example_ordering_passes(self):
        """apa7.md section 3. ``The Irishman`` is ``a`` because ``Irishman``
        sorts before ``Rolling`` -- the leading article is not counted."""
        a = self.A.replace("*UpToDate*", "The irishman. *UpToDate*")
        b = self.B.replace("*UpToDate*", "Rolling thunder revue. *UpToDate*")
        self.assertNotIn(scan.AB_OUT_OF_TITLE_ORDER, kinds(draft(a, b, body=self._body())))

    def test_a_leading_article_is_not_counted(self):
        """The mirror of the row above, and the only test that can tell whether
        the article is being ignored: counting it, this ordering looks right."""
        a = self.A.replace("*UpToDate*", "Rolling thunder revue. *UpToDate*")
        b = self.B.replace("*UpToDate*", "The irishman. *UpToDate*")
        self.assertIn(scan.AB_OUT_OF_TITLE_ORDER, kinds(draft(a, b, body=self._body())))


class ARetrievalDateBelongsWhereAPAPutsOne(unittest.TestCase):
    def test_an_uptodate_entry_without_one_is_a_finding(self):
        stripped = UPTODATE.replace("Retrieved August 19, 2026, from ", "")
        self.assertIn(scan.UPTODATE_NO_RETRIEVAL_DATE, kinds(draft(ACOG, stripped)))

    def test_a_retrieval_date_on_a_doi_entry_is_a_finding(self):
        dated = ACOG.replace("https://doi.org", "Retrieved August 19, 2026, from https://doi.org")
        self.assertIn(scan.RETRIEVAL_DATE_ON_ARCHIVED, kinds(draft(dated, UPTODATE)))

    def test_a_doi_entry_with_no_retrieval_date_at_all_is_not_one(self):
        """The pre-APA-7 ``Retrieved from`` carries no date, so there is no
        retrieval date to object to and this row would name the wrong defect."""
        bare = ACOG.replace("https://doi.org", "Retrieved from https://doi.org")
        self.assertNotIn(scan.RETRIEVAL_DATE_ON_ARCHIVED, kinds(draft(bare, UPTODATE)))

    def test_a_retrieval_date_before_the_exam_date_is_a_finding(self):
        early = UPTODATE.replace("August 19, 2026", "August 19, 2025")
        self.assertIn(scan.RETRIEVAL_DATE_BEFORE_EXAM, kinds(draft(ACOG, early)))

    def test_the_same_day_is_on_or_after(self):
        self.assertNotIn(scan.RETRIEVAL_DATE_BEFORE_EXAM, kinds(CLEAN))

    def test_the_window_is_the_one_row_a_dateless_run_loses(self):
        early = UPTODATE.replace("August 19, 2026", "August 19, 2025")
        self.assertNotIn(scan.RETRIEVAL_DATE_BEFORE_EXAM, kinds(draft(ACOG, early), as_of=None))

    def test_every_other_row_still_fires_without_an_exam_date(self):
        text = draft(ACOG + "Links to an external site.", UPTODATE)
        self.assertIn(scan.CANVAS_ARTIFACT, kinds(text, as_of=None))


class ADateElementIsWellFormed(unittest.TestCase):
    def test_a_missing_space_is_a_finding(self):
        text = draft(ACOG, UPTODATE.replace("August 19", "August19"))
        self.assertIn(scan.MALFORMED_DATE, kinds(text))

    def test_a_misspelled_month_is_a_finding(self):
        text = draft(ACOG, UPTODATE.replace("August", "Augut"))
        self.assertIn(scan.MALFORMED_DATE, kinds(text))

    def test_a_retrieved_element_with_no_date_at_all_is_a_finding(self):
        text = draft(ACOG, UPTODATE.replace("Retrieved August 19, 2026, from", "Retrieved on"))
        self.assertIn(scan.MALFORMED_DATE, kinds(text))

    def test_the_pre_apa7_retrieved_from_is_not_read_as_a_broken_date(self):
        """It is a style defect a reader catches, and firing here would name the
        wrong row -- the entry is missing its retrieval date, not malforming one."""
        text = draft(ACOG, UPTODATE.replace("Retrieved August 19, 2026, from", "Retrieved from"))
        found = kinds(text)
        self.assertNotIn(scan.MALFORMED_DATE, found)
        self.assertIn(scan.UPTODATE_NO_RETRIEVAL_DATE, found)


class TheDatabaseNameIsItalicizedInExactlyOnePlace(unittest.TestCase):
    def test_an_unitalicized_entry_is_a_finding(self):
        text = draft(ACOG, UPTODATE.replace("*UpToDate*", "UpToDate"))
        self.assertIn(scan.UPTODATE_ITALICS, kinds(text))

    def test_underscores_italicize_too(self):
        text = draft(ACOG, UPTODATE.replace("*UpToDate*", "_UpToDate_"))
        self.assertNotIn(scan.UPTODATE_ITALICS, kinds(text))

    def test_bold_is_not_italic(self):
        """``**UpToDate**`` contains ``*UpToDate*``, so a matcher that only pairs
        the delimiters passes an entry the renderer will set in bold."""
        text = draft(ACOG, UPTODATE.replace("*UpToDate*", "**UpToDate**"))
        self.assertIn(scan.UPTODATE_ITALICS, kinds(text))

    def test_italics_in_running_text_are_a_finding(self):
        body = BODY.replace("a urine culture", "*UpToDate* says a urine culture")
        self.assertIn(scan.UPTODATE_ITALICS, kinds(draft(ACOG, UPTODATE, body=body)))

    def test_plain_running_text_is_not(self):
        body = BODY.replace("a urine culture", "UpToDate says a urine culture")
        self.assertNotIn(scan.UPTODATE_ITALICS, kinds(draft(ACOG, UPTODATE, body=body)))


class TheYearsAgreeAndBothDirectionsAreChecked(unittest.TestCase):
    def test_an_in_text_year_that_differs_is_a_finding(self):
        body = BODY.replace("Gupta & Hooton, 2025", "Gupta & Hooton, 2024")
        self.assertIn(scan.INTEXT_YEAR_MISMATCH, kinds(draft(ACOG, UPTODATE, body=body)))

    def test_a_narrative_citation_is_read_too(self):
        body = BODY.replace("(Gupta & Hooton, 2025)", "as Gupta and Hooton (2024) put it")
        self.assertIn(scan.INTEXT_YEAR_MISMATCH, kinds(draft(ACOG, UPTODATE, body=body)))

    def test_a_citation_wrapped_across_two_lines_is_still_one_citation(self):
        """The corpus hard-wraps its prose, so a long organizational author is
        routinely split -- reading it as two would invent an unlisted citation."""
        self.assertNotIn(scan.UNLISTED_CITATION, kinds(CLEAN))

    def test_an_entry_cited_nowhere_is_a_finding(self):
        body = "# Case\n\nOnly one source (Gupta & Hooton, 2025).\n"
        self.assertIn(scan.UNCITED_ENTRY, kinds(draft(ACOG, UPTODATE, body=body)))

    def test_a_citation_with_no_entry_is_a_finding(self):
        body = BODY.replace("Gupta & Hooton, 2025", "Nicolle et al., 2019")
        self.assertIn(scan.UNLISTED_CITATION, kinds(draft(ACOG, UPTODATE, body=body)))

    def test_et_al_resolves_to_the_first_author(self):
        body = BODY.replace("Gupta & Hooton, 2025", "Gupta et al., 2025")
        self.assertEqual(kinds(draft(ACOG, UPTODATE, body=body)), [])

    def test_a_disambiguated_year_matches_its_entry(self):
        a = "Hooton, T. M. (2025a). Acute cystitis. *UpToDate*. Retrieved August 19, 2026, from https://x/a"
        b = "Hooton, T. M. (2025b). Bacteriuria. *UpToDate*. Retrieved August 19, 2026, from https://x/b"
        body = "# Case\n\nBoth (Hooton, 2025a, 2025b).\n"
        self.assertEqual(kinds(draft(a, b, body=body)), [])


class TheCitationParserReadsTheShapesAPAActuallyWrites(unittest.TestCase):
    """Every shape here was found by pointing the parser at real APA prose rather
    than at the fixtures written for it, and each one had been read as **no
    citation at all** -- which reports a compliant entry as cited nowhere."""

    def _keys(self, body: str) -> set:
        return {(c.key, c.year) for c in scan.read_citations(body)}

    def test_several_works_in_one_parenthesis(self):
        found = self._keys("Both agree (Gupta & Hooton, 2025; Smith, 2021).")
        self.assertEqual(found, {("gupta", "2025"), ("smith", "2021")})

    def test_a_shortened_title_puts_the_comma_inside_the_quote(self):
        """An authorless work is cited by title, and APA sets the comma inside the
        closing quotation mark."""
        self.assertIn(("managing", "2024"), self._keys('As noted ("Managing hypertension," 2024).'))

    def test_a_page_locator_does_not_hide_the_citation(self):
        self.assertIn(("smith", "2021"), self._keys("One study (Smith, 2021, p. 47) found it."))
        self.assertIn(("smith", "2021"), self._keys("Smith (2021, p. 47) found it."))

    def test_a_locator_page_number_is_not_read_as_a_second_year(self):
        self.assertEqual(self._keys("One study (Smith, 2021, p. 1998) found it."), {("smith", "2021")})

    def test_an_undated_source_parses_despite_ending_on_a_period(self):
        self.assertIn(("world", "nd"), self._keys("A page (World Health Organization, n.d.) says so."))

    def test_a_parenthesis_that_is_not_a_citation_yields_nothing(self):
        self.assertEqual(self._keys("The cohort (n = 40) was small (see Table 1)."), set())

    def test_a_signal_phrase_does_not_become_the_author(self):
        """``(e.g., Hooton, 2024)`` alphabetizes under ``e`` without this, and the
        unlisted-citation row fires on a compliant draft."""
        self.assertEqual(self._keys("Others agree (e.g., Hooton, 2024)."), {("hooton", "2024")})
        self.assertEqual(self._keys("Others agree (see Gupta, 2025)."), {("gupta", "2025")})

    def test_a_lowercase_word_before_a_number_is_not_an_author(self):
        """``(<word>, <four digits>)`` is not rare in a clinical paper, and reading
        it as a citation invents a source the list cannot possibly hold."""
        self.assertEqual(self._keys("Range (systolic, 2000 to 3000) mL."), set())

    def test_a_lowercase_name_particle_still_reads_as_an_author(self):
        self.assertEqual(self._keys("One study (van der Berg, 2020) found it."), {("van", "2020")})

    def test_a_capitalized_word_before_a_parenthesized_year_is_not_a_narrative_citation(self):
        """A narrative citation's parentheses hold the year and at most a locator.
        Allowing any trailing text invented an author named Hypertension."""
        self.assertEqual(self._keys("Hypertension (2025 update) changed the target."), set())


class TheReportCarriesNoDocumentTextWithoutShow(unittest.TestCase):
    def setUp(self):
        text = draft(ACOG + "Links to an external site.", UPTODATE)
        self.scan = scan.survey(scan.read_document(text), AS_OF)

    def test_the_default_report_prints_no_entry_text(self):
        report = scan.format_report(self.scan, source="case.md")
        self.assertNotIn("Practice Bulletin", report)
        self.assertNotIn("Links to an external site.", report)

    def test_show_prints_them(self):
        report = scan.format_report(self.scan, source="case.md", show=True)
        self.assertIn("Links to an external site.", report)

    def test_every_row_is_named_in_the_report(self):
        report = scan.format_report(self.scan, source="case.md")
        for kind in scan.KINDS:
            with self.subTest(row=kind):
                self.assertIn(kind, report)


class EntriesAtFaultCountsEntries(unittest.TestCase):
    """The count read three over a two-entry list before a finding carried the
    line it is chargeable to. A group row names two lines in its own text, so
    reading the locus back off that string counted it as a third entry."""

    def test_it_never_exceeds_the_number_of_entries(self):
        text = draft("- " + UPTODATE.replace("*UpToDate*", "UpToDate"), ACOG)
        result = scan.survey(scan.read_document(text), AS_OF)
        self.assertLessEqual(result.entries_at_fault, result.entries)

    def test_an_out_of_order_pair_charges_one_entry_and_not_a_third(self):
        result = scan.survey(scan.read_document(draft(UPTODATE, ACOG)), AS_OF)
        self.assertEqual(result.entries, 2)
        self.assertEqual(result.entries_at_fault, 1)

    def test_a_heading_defect_charges_no_entry(self):
        text = draft(ACOG, UPTODATE, heading="## Works Cited")
        result = scan.survey(scan.read_document(text), AS_OF)
        self.assertEqual(result.entries_at_fault, 0)
        self.assertTrue(result.findings)


class TheCommandExitsOnWhatItFound(unittest.TestCase):
    def _run(self, text: str, *extra: str, name: str = "case.md") -> int:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = scan.main([str(path), "--as-of", "2026-08-19", *extra])
            self.last = out.getvalue() + err.getvalue()
        return status

    def test_a_clean_draft_exits_zero(self):
        self.assertEqual(self._run(CLEAN), 0)

    def test_a_failing_draft_exits_one(self):
        self.assertEqual(self._run(draft(UPTODATE, ACOG)), 1)

    def test_no_arguments_exits_two(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(scan.main([]), 2)

    def test_a_missing_file_exits_two(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(scan.main(["no-such-draft.md", "--as-of", "2026-08-19"]), 2)

    def test_a_draft_with_no_reference_section_exits_two(self):
        self.assertEqual(self._run(BODY), 2)
        self.assertIn("no reference list", self.last)

    def test_a_heading_with_no_entries_under_it_exits_two(self):
        self.assertEqual(self._run(BODY + "\n## References\n"), 2)

    def test_a_missing_exam_date_exits_two_on_an_otherwise_clean_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.md"
            path.write_text(CLEAN, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = scan.main([str(path)])
            self.assertEqual(status, 2)
            self.assertIn("--as-of", err.getvalue())

    def test_a_finding_outranks_a_missing_exam_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.md"
            path.write_text(draft(UPTODATE, ACOG), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = scan.main([str(path)])
            self.assertEqual(status, 1)
            self.assertIn("--as-of", err.getvalue())

    def test_a_bad_exam_date_exits_two(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(scan.main(["x.md", "--as-of", "yesterday"]), 2)

    def test_a_mistyped_flag_is_refused_rather_than_dropped(self):
        """A dropped ``--shwo`` prints a counts-only report, which is exactly what
        a clean run looks like -- a check that did not happen, answering like one
        that found nothing."""
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(scan.main([str(Path("x.md")), "--as-of", "2026-08-19", "--shwo"]), 2)
        self.assertIn("--shwo", err.getvalue())

    def test_as_of_does_not_swallow_the_next_flag_as_a_date(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(scan.main(["x.md", "--as-of", "--show"]), 2)
        self.assertIn("--as-of", err.getvalue())

    def test_the_path_is_never_printed_only_the_name(self):
        self._run(BODY, name="jane-doe-uti.md")
        self.assertIn("jane-doe-uti.md", self.last)
        self.assertNotIn("Temp", self.last)


class TheRendererAndTheScannerAgreeOnAHeading(unittest.TestCase):
    """#217 made the heading the thing that applies the hanging indent. A scanner
    holding its own copy of that rule could pass a document the renderer sets
    wrong, which is the failure this row exists to catch."""

    def test_one_matcher_and_the_scanner_imports_it(self):
        self.assertIs(scan.RENDERER_HEADING, docx_write.REFERENCE_HEADING)

    def test_the_two_spellings_apa_permits_are_both_styled(self):
        for text in scan.APA_HEADINGS:
            with self.subTest(heading=text):
                self.assertTrue(docx_write.REFERENCE_HEADING.match(text))

    def test_reference_ranges_is_neither_a_reference_list_nor_styled(self):
        self.assertFalse(docx_write.REFERENCE_HEADING.match("Reference Ranges"))
        text = BODY + "\n## Reference Ranges\n\nWBC 5 to 10.\n"
        self.assertIsNone(scan.read_document(text).heading)

    def test_anything_the_renderer_styles_is_found_as_a_reference_list(self):
        """``References and Resources`` takes the plural's prefix match, so the
        renderer hangs the list under it. Finding the section from a hand-typed
        list of labels answered *no reference list found* and exited 2 on a
        document whose list renders perfectly well."""
        text = draft(ACOG, UPTODATE, heading="## References and Resources")
        document = scan.read_document(text)
        self.assertEqual(document.heading, "References and Resources")
        self.assertEqual(len(document.entries), 2)
        self.assertIn(scan.HEADING_NOT_APA, kinds(text))

    def test_a_forbidden_label_the_renderer_declines_is_still_found(self):
        """What the import cannot reach, and why ``WRONG_HEADINGS`` survives it."""
        self.assertFalse(docx_write.REFERENCE_HEADING.match("Works Cited"))
        self.assertEqual(scan.read_document(draft(ACOG, UPTODATE, heading="## Works Cited")).heading, "Works Cited")


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    """``test_spelling_scan``'s rule: a scanner that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.apa7 = APA7.read_text(encoding="utf-8")

    def test_the_skill_names_the_command(self):
        self.assertIn("python tools/reference_scan.py", self.skill)

    def test_the_skill_names_the_exam_date_argument(self):
        self.assertIn("--as-of", self.skill)

    # One phrase per row, keyed on the module's own tuple, so a row added without
    # a sentence in the skill fails here rather than quietly becoming a rule only
    # the scanner knows -- which is the class ``AGENTS.md`` puts this tool in.
    #
    # **A phrase has to describe what the scanner *does*, not the wider rule the
    # table states**, and two of these did not when they were written: the
    # retrieval-date row was keyed on *"a guideline, article or textbook"* when the
    # scanner fires only on a DOI, and the no-year row was keyed on *"hard-wrapped"*
    # when an unwrapped entry with no year fires it too. Both were **green**, so the
    # check certified an agreement that was not one -- [#106]'s *"a wrong one stays
    # wrong, silently, forever"* arriving inside the mechanism built against it. The
    # table still states the wide rule, because the table is the rule; what changed
    # is that it now says beside the wide row how far the command reaches.
    ROW_PHRASES = {
        scan.HEADING_NOT_APA: "The reference list headed anything but",
        scan.ENTRY_NOT_A_PARAGRAPH: "An entry written as a bullet or a numbered item",
        scan.ENTRY_HAS_NO_YEAR: "An entry carrying no year element",
        scan.CANVAS_ARTIFACT: "`Links to an external site.` welded to a URL",
        scan.LIST_NOT_SORTED: "Two entries out of alphabetical order",
        scan.MISSING_AB: "Two entries with the same author and year and no `a`/`b`",
        scan.AB_OUT_OF_TITLE_ORDER: "the letters are assigned by **title order**",
        scan.UPTODATE_NO_RETRIEVAL_DATE: "An UpToDate entry with no retrieval date",
        scan.RETRIEVAL_DATE_ON_ARCHIVED: "The command reaches this only where the entry carries a DOI",
        scan.RETRIEVAL_DATE_BEFORE_EXAM: "Retrieval year behind the exam year",
        scan.MALFORMED_DATE: "A missing space in a date",
        scan.UPTODATE_ITALICS: "database name unitalicized",
        scan.INTEXT_YEAR_MISMATCH: "In-text year not matching the reference list year",
        scan.UNCITED_ENTRY: "An entry in the list that is cited nowhere in the body",
        scan.UNLISTED_CITATION: "A citation in the body with no entry in the list",
    }

    def test_the_skill_writes_out_every_row_the_scanner_applies(self):
        for kind in scan.KINDS:
            with self.subTest(row=kind):
                self.assertIn(kind, self.ROW_PHRASES, "row is not written into the skill")
                self.assertIn(self.ROW_PHRASES[kind], self.skill)

    def test_the_skill_says_a_clean_scan_is_not_a_checked_list(self):
        self.assertIn("A clean scan is not a checked reference list", self.skill)

    def test_the_skill_keeps_the_findings_out_of_the_clinicians_hands(self):
        """#211's ruling, which #218's fourth decision inherits: a reference
        defect is fixed by the run, not reported to him."""
        self.assertIn("its findings are not handed back", self.skill)

    def test_the_skill_writes_down_the_fallback_for_a_harness_without_subagents(self):
        """#218's second decision, taking #214's answer rather than inventing a
        second one."""
        self.assertIn("no subagent tool", self.skill)

    def test_the_post_draft_checks_write_their_headings_first(self):
        """#206's lost-record shape and the ledger's answer to it: a heading whose
        verdict never arrived is visible, and a check that never ran is not."""
        self.assertIn("scratch/case-study-checks.md", self.skill)
        self.assertIn("VERDICT", self.skill)

    def test_the_post_draft_checks_are_not_graded_by_the_pass_that_wrote_the_draft(self):
        """ADR 0001 one level up, and the sentence the ticket was filed on."""
        self.assertIn("cannot audit its own", self.skill)

    def test_the_apa_sheet_still_owns_the_rules(self):
        """The scanner is a second reader of ``apa7.md``, never a second copy of
        it, so the sheet has to still carry what the rows are derived from."""
        for phrase in ("Works Cited", "hanging indent", "assigned by placing the entries"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.apa7)

    def test_the_worked_reference_list_in_the_skill_passes_the_scanner(self):
        """**The one that catches drift a substring cannot see.** A documented
        list the scanner would refuse teaches the next run to write one that
        fails, and every string test above would still be green."""
        example = self._worked_list()
        document = scan.read_document(example)
        self.assertTrue(document.entries, "the skill's example should hold entries")
        self.assertEqual([f.kind for f in scan.findings(document, None)], [])

    def _worked_list(self) -> str:
        """The one fenced block in the skill that parses as a reference list.

        Walked line by line rather than matched with one regex: a non-greedy
        pattern over the whole file happily opens on the *closing* fence of the
        block above it, which is what ``test_research_ledger`` found first.
        """
        blocks: list[str] = []
        current: list[str] | None = None
        for line in self.skill.splitlines():
            if line.startswith("```"):
                if current is None:
                    current = []
                else:
                    blocks.append("\n".join(current) + "\n")
                    current = None
                continue
            if current is not None:
                current.append(line)
        self.assertIsNone(current, "an unclosed code fence in the skill")
        found = [b for b in blocks if scan.read_document(b).entries]
        self.assertEqual(len(found), 1, "expected exactly one worked reference list")
        return found[0]


# One token, salted onto every non-blank line of ``LEAKY``'s body. Lowercase and
# meaningless, so ``citation_key`` refuses it as an author and it cannot be carried
# into a finding by the two body rows that do name one -- which is what makes its
# absence from the report a statement about the code rather than about this string.
MARKER = "qxmarkerxq"

# Every non-blank line carries the marker, and no citation encloses one: a marker
# inside a parenthesis would be read as the first word of the author and would drop
# the citation it was put there to leave alone.
LEAKY_BODY = """\
# Case Study qxmarkerxq

## Subjective qxmarkerxq

The patient reports dysuria for three days qxmarkerxq

## Medical Decision Making qxmarkerxq

Nitrofurantoin is first line in the second trimester (American College of Obstetricians and Gynecologists, 2023). qxmarkerxq

A urine culture is drawn before the first dose (Gupta & Hooton, 2019). qxmarkerxq

Stewardship review is standing practice (Chen, 2024), and the two reviews disagree (Diaz, 2022a, 2022b). qxmarkerxq

Pathways were followed (Ibarra, 2020), and one source is cited nowhere (Nobody, 2020). qxmarkerxq

The topic was read on *UpToDate* the same morning. qxmarkerxq

Course material arrived with Links to an external site. attached. qxmarkerxq
"""

# One line per entry, chosen so every kind in ``KINDS`` fires at least once. The
# comment above each names the row it is there for.
LEAKY_ENTRIES = (
    # entry-not-a-paragraph -- a bullet, which the renderer gives the list style.
    "- American College of Obstetricians and Gynecologists. (2023). Urinary tract "
    "infections in pregnancy. https://doi.org/10.1000/acog.91",
    # entry-has-no-year, and canvas-artifact inside an entry.
    "Bauer, R. Managing pyelonephritis in pregnancy. Links to an external site.",
    # missing-ab -- one author, one year, no letters.
    "Chen, L. (2024). Antibiotic stewardship in obstetric care. Journal of Care, 12(3), 45-59.",
    "Chen, L. (2024). Bacteriuria screening intervals. Journal of Care, 12(4), 61-70.",
    # ab-out-of-title-order, and the one list-not-sorted pair.
    "Diaz, M. (2022b). Alpha review of cystitis. Journal of Care, 1, 1-9.",
    "Diaz, M. (2022a). Zebra review of cystitis. Journal of Care, 2, 10-19.",
    # uptodate-no-retrieval-date, uptodate-italics in an entry, and the entry the
    # body cites under a year it does not carry.
    "Gupta, K., & Hooton, T. M. (2025). Acute simple cystitis in adult females. "
    "UpToDate. https://www.uptodate.com/contents/cystitis",
    # retrieval-date-on-archived, retrieval-date-before-exam, and uncited-entry.
    "Hooton, T. M. (2021). Recurrent urinary tract infection in women. Journal of "
    "Medicine, 8(2), 100-115. https://doi.org/10.1000/jm.8.2 Retrieved August 1, "
    "2026, from https://example.org/hooton",
    # malformed-date -- a real month with no space after it.
    "Ibarra, P. (2020). Pyelonephritis pathways. Clinical Notes, 4(1), 5-12. "
    "Retrieved August19, 2026, from https://example.org/ibarra",
)

# heading-not-apa comes from the label. The section is still found, because
# ``Works Cited`` is one of the labels APA forbids and a document really uses.
LEAKY = draft(*LEAKY_ENTRIES, body=LEAKY_BODY, heading="## Works Cited")


class TheReportCannotCarryTheDraftsProse(unittest.TestCase):
    """#218's decision 1, ruled 2026-08-19: ``--show`` output is safe to paste.

    **The ruling rests on a property of the code, so the property gets a test or
    the ruling erodes the first time a sixteenth row arrives.** Every finding
    detail is a reference entry, a heading, a date, or a cited author's surname and
    year, and none of them can be a sentence of clinical prose. That is what this
    measures, against a draft whose every body line carries a token nothing in the
    reference list contains.

    ``test_build_artifacts_ignored.TheInstrumentIsLive`` is the precedent for the
    liveness rows here and the reason for them: its first version passed three of
    four assertions against a check that said yes to everything. A leak test over a
    draft that fires nothing passes for exactly that wrong reason.

    **The one aperture onto the body is exercised rather than avoided.** A citation
    key is the first word of anything the body writes as ``(Word, 2024)``, so one
    capitalized token of prose can reach the report -- and
    ``test_the_one_aperture_is_one_token_wide`` drives the marker through it and
    pins that what comes out is a token and a year rather than the sentence. Naming
    the limit and leaving it unmeasured is what the module's own header warns
    about.
    """

    def setUp(self):
        self.document = scan.read_document(LEAKY)
        self.findings = scan.findings(self.document, AS_OF)
        self.report = shown_report(LEAKY)

    def test_the_marker_is_really_in_the_draft_and_only_in_its_body(self):
        """The leak row is vacuous if the body was never salted -- and it would be
        measuring the wrong thing if the reference list carried the token too."""
        self.assertGreaterEqual(self.document.body.count(MARKER), 8)
        self.assertNotIn(MARKER, "\n".join(e.text for e in self.document.entries))

    def test_the_instrument_is_live(self):
        """**A floor, not an equality.** A row added to ``KINDS`` that this draft
        does not happen to fire is not a reason for this to go red."""
        fired = {f.kind for f in self.findings}
        self.assertGreaterEqual(len(fired), 12, sorted(fired))

    def test_every_declared_body_row_actually_fires(self):
        """The half of liveness that binds a future row.

        A body row this draft does not fire is a row the leak test never
        exercises, so a sixteenth one cannot arrive without being fired here.
        """
        fired = {f.kind for f in self.findings if f.where == "body"}
        self.assertLessEqual(set(scan.BODY_ROWS), fired, sorted(fired))

    def test_the_shown_report_carries_no_body_prose(self):
        """The ruling itself, measured rather than argued."""
        self.assertNotIn(MARKER, self.report)

    def test_the_shown_report_really_printed_its_findings(self):
        """And the row above is not passing because ``--show`` printed nothing."""
        self.assertIn("findings", self.report)
        for finding in self.findings:
            with self.subTest(kind=finding.kind):
                self.assertIn(finding.detail, self.report)

    def test_the_one_aperture_is_one_token_wide(self):
        """**The limit the ruling is stated against, measured rather than named.**

        A citation key is the first word of anything shaped ``(Word, 2024)``, so a
        capitalized body token does reach the report. What this pins is how much
        comes with it: the token and its year, and none of the sentence holding
        them. Saying the report can carry nothing of the body would be a claim a
        notch stronger than the code, which is the defect this file's subject
        module warns about in its own header.
        """
        sentence = (
            "The patient's daughter Qxmarkerxq was at the bedside for the whole"
            " admission and gave the history (Qxmarkerxq, 2031)."
        )
        report = shown_report(draft(ACOG, UPTODATE, body=BODY + "\n" + sentence + "\n"))
        self.assertIn("qxmarkerxq 2031", report)
        for word in ("daughter", "bedside", "admission", "gave the history"):
            with self.subTest(word=word):
                self.assertNotIn(word, report)


class NoBodyRowCanArriveUndeclared(unittest.TestCase):
    """``BODY_ROWS`` is complete, read off the module rather than off a fixture.

    **The class above measures only the rows one draft happens to fire**, so a
    fifth body row that was neither declared nor written into ``LEAKY`` would leave
    every assertion there green -- a check that could not have seen the thing it is
    named for, answering like a settled negative. This is the completeness half,
    and it is ``test_console_codec.py``'s instrument for ``test_console_codec.py``'s
    reason: an AST walk sees a call no draft reaches.
    """

    def setUp(self):
        source = (REPO_ROOT / "tools" / "reference_scan.py").read_text(encoding="utf-8")
        self.tree = ast.parse(source)

    def _body_calls(self) -> list[ast.Call]:
        """Every ``Finding(...)`` whose ``where`` is the literal ``"body"``.

        ``where`` is read positionally and by keyword, because either spelling
        constructs the same finding and a walk that saw only one would be the
        partial instrument this class exists to replace.
        """
        found: list[ast.Call] = []
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            if not (isinstance(node.func, ast.Name) and node.func.id == "Finding"):
                continue
            where: ast.expr | None = node.args[1] if len(node.args) > 1 else None
            for keyword in node.keywords:
                if keyword.arg == "where":
                    where = keyword.value
            if isinstance(where, ast.Constant) and where.value == "body":
                found.append(node)
        return found

    def test_the_walk_found_the_calls(self):
        """``TheInstrumentIsLive``'s row. A walk matching nothing passes the row
        below for the one reason that must not count."""
        self.assertGreaterEqual(len(self._body_calls()), len(scan.BODY_ROWS))

    def test_every_body_finding_in_the_module_is_declared(self):
        """**The row that matters.** A fifth row reading the draft's prose cannot
        arrive quietly, whether or not any test fires it."""
        for call in self._body_calls():
            kind = call.args[0]
            with self.subTest(line=call.lineno):
                self.assertIsInstance(kind, ast.Name, "a body row named by something other than a constant")
                self.assertIn(getattr(scan, kind.id), scan.BODY_ROWS)


class TheModuleSaysTheRulingRatherThanTheDefault(unittest.TestCase):
    """The ruling landed in three places in ``reference_scan`` itself.

    ``test_spelling_scan``'s reasoning: a module whose printed posture disagrees
    with the ruling is worse than none, because a reader takes the printed line.
    """

    def test_the_show_header_no_longer_calls_its_own_output_phi(self):
        report = shown_report(LEAKY)
        self.assertIn("findings (safe to paste):", report)
        self.assertNotIn("findings (PHI - read, do not paste):", report)

    def test_the_exit_message_no_longer_forbids_pasting(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.md"
            path.write_text(LEAKY, encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                status = scan.main([str(path), "--as-of", AS_OF.isoformat()])
        self.assertEqual(status, 1)
        self.assertIn("--show", stderr.getvalue())
        self.assertNotIn("do not paste", stderr.getvalue())

    def test_the_docstring_records_the_ruling_and_names_the_test_that_pins_it(self):
        for phrase in (
            "2026-08-19",
            "safe to paste",
            "TheReportCannotCarryTheDraftsProse",
            "Counts only by default",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, scan.__doc__ or "")

    def test_the_findings_own_docstring_agrees_that_a_detail_may_be_printed(self):
        """The sentence the ruling had to reach and first missed: ``Finding``'s
        docstring said ``detail`` was not safe to print, one screen below the
        paragraph announcing that it was.

        **Asserted on the claim the docstring now makes, not on the absence of the
        old string** -- the retired sentence is quoted there on purpose, and a test
        keyed on its absence would refuse the file for recording its own history.
        """
        self.assertIn(
            "Both ``where`` and ``detail`` are safe to print",
            " ".join((scan.Finding.__doc__ or "").split()),
        )


class TheRulingDoesNotWiden(unittest.TestCase):
    """What #218 ruled about this scanner, it ruled about nothing else.

    The module docstring and ``CLAUDE.md`` both enumerate what stays PHI. **An
    enumeration in prose is a claim nothing re-derives** -- which is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) -- so
    each name on it is read off the file it names.
    """

    # The ruling's own list, and deliberately not a sweep of ``tools/`` for
    # ``--show``: ``guidelines_recs.py`` is restrained by copyright rather than by
    # standing rule 1, and ``phi_scan.py``'s ``--show`` reveals the findings rather
    # than a scanned record.
    STAYS_PHI = (
        "research_ledger.py",
        "checks_ledger.py",
        "block_scan.py",
        "specificity_scan.py",
        "differential_scan.py",
        "anchor_scan.py",
        "filled_vitals_census.py",
    )

    def test_every_sibling_named_in_the_docstring_still_declares_its_show_phi(self):
        """Read off each sibling's **docstring**, which is the sentence a widening
        would have to edit. Five of the six also print ``PHI - read, do not paste``
        in a ``--show`` header and ``filled_vitals_census`` does not, so asserting
        the header would have graded five modules and skipped one -- found by
        pointing this at the tree rather than by reading five of them."""
        for name in self.STAYS_PHI:
            with self.subTest(module=name):
                self.assertIn(name, scan.__doc__ or "")
                source = (REPO_ROOT / "tools" / name).read_text(encoding="utf-8")
                docstring = ast.get_docstring(ast.parse(source)) or ""
                self.assertIn("``--show`` output is PHI", " ".join(docstring.split()))

    #: Every command in ``practicum-case-study`` whose ``--show`` output is PHI, in
    #: the order the skill names them. **This was pinned at one and the ruling was
    #: never about the count** -- #240 gave ``practicum-case-study`` step 9's
    #: fan-out a grader whose records
    #: are the same readers' prose one file later, and the first version of this
    #: test read that second correct line as the widening it exists to refuse.
    PHI_COMMANDS_IN_THE_SKILL = ("research_ledger.py", "checks_ledger.py")

    def test_every_phi_line_in_the_skill_belongs_to_a_tool_that_stays_phi(self):
        """**#218's build spec names the ledger's line and says leave it exactly as
        it is.** A ledger record in ``practicum-case-study`` step 3 holds a claim
        transcribed from faculty material about a patient, and a checks record in
        step 9 holds a reader's own words about the draft; neither has this
        scanner's guarantee. Asserting it in ``research_ledger.py`` would have
        guarded a different file: a sweep over the skill is what would take it, and
        the skill is where it lives.

        **Whitespace is normalized because the line is hard-wrapped**, which is
        ``test_run_record_claim``'s finding -- a phrase broken across two lines is
        invisible to a check written against the single-line form.
        """
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        sections = skill.split("**that output is PHI**")
        self.assertEqual(
            len(sections) - 1,
            len(self.PHI_COMMANDS_IN_THE_SKILL),
            "a PHI line in the skill belongs to no command on the ruling's list",
        )
        for before, after, command in zip(sections, sections[1:], self.PHI_COMMANDS_IN_THE_SKILL):
            with self.subTest(command=command):
                self.assertIn(command, before.rsplit("###", 1)[-1])
                self.assertTrue(after.lstrip(": ").startswith("read it, do not paste it."))

    def test_this_scanners_own_line_in_the_skill_is_the_other_ruling(self):
        """The half #218 settled the other way, asserted beside the half it did
        not: a sweep that took every ``--show`` line to one answer would fail one
        of these two tests whichever answer it took."""
        skill = " ".join(SKILL.read_text(encoding="utf-8").split())
        self.assertIn("Its `--show` output is **safe to paste**", skill)


class TheTwoCopiesOfWhatStaysAReading(unittest.TestCase):
    """[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241),
    and it is ``TheTwoCopiesOfWhatTheRendererApplies`` one artifact over.

    ``apa7.md`` section 7 carries *what stays a reading* for a reader of the skill and
    this module carries it for a reader of the code, and until #241 a **prose** edit to
    either failed nothing -- so the reader who was misled was the one who checked the
    file nearer to hand. #220's repair is copied whole rather than reinvented: the
    sheet's copy stopped being a copy by becoming ``NOT_REACHED``, one object, and this
    asserts the two name the same items in both directions.

    **The rows are read with ``docx_write.table_first_cells``**, which is where the
    loop lives because this class first carried its own copy of it -- the same loop as
    ``TheTwoCopiesOfWhatTheRendererApplies``, comment included, under a docstring
    asserting that a second table parser here would be the copy this class exists to
    refuse. Caught by ``/code-review``, which is the arrangement working: a docstring
    asserting the opposite of what the code does is this file's own worst defect class,
    named in ``reference_scan``'s header, and it arrived here in the change that quotes
    it.

    **What it does not reach is whether a row's verdict is true.** An item moved out of
    ``NOT_REACHED`` while the command still cannot reach it passes every assertion here,
    and stays a behavior test's job -- ``ARetrievalDateBelongsWhereAPAPutsOne`` is where
    the section 4 rows are actually exercised.
    """

    def section_seven(self):
        """Section 7 alone, bracketed rather than run to the end of the file.

        The twin in ``tools/test_docx.py`` brackets section 6 with section 7. This ran
        to the end because section 7 is last today, which is a fact about the sheet
        rather than about the rule -- an eighth section would have silently widened
        what this reads. Caught by review.
        """
        text = APA7.read_text(encoding="utf-8")
        block = text[text.index("## 7.") :]
        nxt = block.find(chr(10) + "## ", 1)
        return block if nxt == -1 else block[:nxt]

    def rows(self):
        return docx_write.table_first_cells(self.section_seven())

    def test_the_table_is_found(self):
        """The instrument is live: a parser finding nothing would pass every row
        below, which is ``TheInstrumentIsLive``'s reasoning in
        ``test_build_artifacts_ignored.py`` and this file's own ``NoBodyRowCanArriveUndeclared``."""
        self.assertTrue(self.rows())

    def test_every_item_the_module_names_is_a_row_on_the_sheet(self):
        rows = self.rows()
        for key, _ in scan.NOT_REACHED:
            # ``subTest`` because a bare loop stops at the earliest mismatch and reports
            # one key as though it were the only one -- which it did while this was
            # being written, and a partial report reads here as a complete one.
            with self.subTest(key=key):
                self.assertEqual(len([r for r in rows if key in r]), 1, key)

    def test_the_sheet_names_nothing_the_module_does_not(self):
        self.assertEqual(len(self.rows()), len(scan.NOT_REACHED))

    def test_every_entry_carries_a_key_and_a_reason(self):
        """The reason is what a reader of the code reads in place of the old prose."""
        for key, reason in scan.NOT_REACHED:
            self.assertTrue(key.strip(), key)
            self.assertGreater(len(reason.split()), 8, key)

    def test_the_unwarranted_retrieval_date_is_one_of_them(self):
        """#241's own row, asserted where it is rather than only where it is not.

        This is the item the ticket was filed over, and a sweep that quietly dropped it
        from ``NOT_REACHED`` while the command still cannot reach it would otherwise
        leave the pair agreeing about a shorter list.
        """
        self.assertIn("unwarranted retrieval date", dict(scan.NOT_REACHED))



class TheDeclinedOptionIsPinnedToTheClassesItWasRuledOver(unittest.TestCase):
    """#241 declined a cross-check against ``research_ledger.py``'s ``SOURCE`` class,
    and the reason was a count: too few of the classes settle whether a retrieval date
    belongs.

    **That count was written into three files as prose and nothing re-derived it** --
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving
    inside the commit whose subject is a list copied into two, and found by
    ``/code-review`` and the tracker sweep independently. The sharper form is theirs:
    the same commit deliberately withheld ``len(NOT_REACHED)`` on #143's terms and then
    stated the number beside it, so the discipline was applied to one figure and missed
    on its neighbour in the same paragraph.

    **The repair is the mapping becoming an object and no file stating a number.** This
    is what makes it re-derivable: a fifth ``SOURCE`` class fails here rather than
    leaving a ruling that was made over four standing unqualified in three files.
    """

    def test_the_keys_are_exactly_the_ledgers_source_classes(self):
        """A fifth class, or a renamed one, fails rather than passing quietly.

        Both directions, because either alone leaves a hole: a class the ledger gained
        and this never heard of, or one this names that the ledger has dropped.
        """
        self.assertEqual(
            set(scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE),
            set(research_ledger.SOURCE_CLASSES),
        )

    def test_the_classes_that_span_both_answers_are_the_reason_it_was_declined(self):
        """The ruling's own premise, asserted rather than described.

        ``government`` covers a USPSTF statement, which takes no retrieval date, and a
        public-health page designed to change, which takes one. ``tertiary reference``
        covers UpToDate, which takes one, and a textbook, which takes none. A row keyed
        on either fails a correct entry, which is why option 2 was declined.
        """
        for spanning in ("government", "tertiary reference"):
            with self.subTest(source_class=spanning):
                self.assertFalse(scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE[spanning])

    def test_at_least_one_class_would_have_settled_it(self):
        """The instrument is live, and it is also the honest half of the ruling.

        Declining option 2 is not the claim that no class maps -- some do, which is why
        the ticket was worth grilling rather than closing on sight. A mapping that said
        *no* would make the decline trivial and this row would stop meaning anything.
        """
        self.assertTrue(any(scan.SOURCE_CLASS_SETTLES_RETRIEVAL_DATE.values()))

    def test_the_module_does_not_import_the_ledger(self):
        """Declining option 2 shows up in the dependency graph, not only in prose.

        The class strings are literals in ``reference_scan``; the join this ticket
        declined is exactly the import that would have made them a lookup.
        """
        source = (REPO_ROOT / "tools" / "reference_scan.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("research_ledger", imported)


class TheReadingTheCommandCannotDoIsAGradedCheck(unittest.TestCase):
    """#241's ruling: the direction stays a reading, and the reading is accountable.

    Option 3 was *rule it closed and say so where it is checked*, which is a prose claim
    in two files. What makes it more than that is
    [#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240), which
    landed a grader over ``skills/practicum-case-study/SKILL.md`` step 9's fan-out: the
    row is in ``checks_ledger.EXPECTED_CHECKS``, so a run that returns no verdict on it
    fails rather than passing quietly. **This asserts the chain end to end** -- the sheet
    names the reading, the step names it in the row's reader column, and the grader
    expects that row by name.

    Rename the row in either file and this fails, which is the one way the arrangement
    could rot without anybody noticing.
    """

    ROW = "the reference list, the part no command reaches"

    def test_the_grader_still_expects_the_row_by_name(self):
        self.assertIn(self.ROW, checks_ledger.EXPECTED_CHECKS)

    def row_line(self):
        """The ``skills/practicum-case-study/SKILL.md`` step 9 table row, as one physical line.

        A table row is one line in this file, so the row and its reader column are read
        together and no cell of the row below can satisfy the assertion.
        """
        for line in SKILL.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("|") and self.ROW in stripped:
                return stripped
        return None

    def test_the_step_names_the_row(self):
        self.assertIsNotNone(
            self.row_line(),
            "skills/practicum-case-study/SKILL.md step 9 no longer carries the row",
        )

    def test_the_rows_reader_column_names_the_retrieval_direction(self):
        """The one-line edit #241 is, asserted rather than described.

        Before #241 that column scoped the reading to the UpToDate year and to whether a
        source exists and says what cites it. The unwarranted retrieval date was named in
        ``apa7.md`` section 7 and in no step a run walks, so nothing failed when a run
        never looked.
        """
        line = self.row_line()
        self.assertIsNotNone(
            line,
            "skills/practicum-case-study/SKILL.md step 9 no longer carries the row",
        )
        self.assertIn("retrieval date", line)


if __name__ == "__main__":
    unittest.main()
