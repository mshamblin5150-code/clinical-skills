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

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

import docx_write
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

    def test_a_deeper_heading_inside_the_list_does_not_close_it(self):
        text = draft(ACOG) + "\n### Note\n\n" + UPTODATE + "\n"
        self.assertEqual(len(scan.read_document(text).entries), 2)


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
    ROW_PHRASES = {
        scan.HEADING_NOT_APA: "The reference list headed anything but",
        scan.ENTRY_NOT_A_PARAGRAPH: "An entry written as a bullet or a numbered item",
        scan.ENTRY_HAS_NO_YEAR: "An entry hard-wrapped onto a second line",
        scan.CANVAS_ARTIFACT: "`Links to an external site.` welded to a URL",
        scan.LIST_NOT_SORTED: "Two entries out of alphabetical order",
        scan.MISSING_AB: "Two entries with the same author and year and no `a`/`b`",
        scan.AB_OUT_OF_TITLE_ORDER: "the letters are assigned by **title order**",
        scan.UPTODATE_NO_RETRIEVAL_DATE: "An UpToDate entry with no retrieval date",
        scan.RETRIEVAL_DATE_ON_ARCHIVED: "A retrieval date on a guideline, article or textbook",
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


if __name__ == "__main__":
    unittest.main()
