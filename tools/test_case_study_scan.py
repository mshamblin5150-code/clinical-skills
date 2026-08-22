"""Cover ``case_study_scan``'s parser and rows against synthetic drafts.

Every draft here is written in this file and a temp directory. **There is no
committed case study and there will not be one** -- a finished draft lives under
``output/`` and is written about a patient, which is ``test_reference_scan``'s
position exactly, and ``test_differential_scan``'s before it.

Three classes read committed files, and each is here for a different reason.
``TheSkeletonIsTheSkillsOwn`` derives the section vocabulary from ``SKILL.md``
rather than retyping it. ``TheSkillSaysWhatThisCannotDo`` binds ``NOT_REACHED``
to the step that names the same items, on ``test_reference_scan``'s arrangement
with ``apa7.md`` section 7 -- a list in two places, each editable without failing
anything, is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).
And ``TheDocumentedShapesPass`` runs the scanner over the shapes ``style.md``
itself publishes: a documented form the grader would refuse teaches the next run
to write a draft that fails, and every substring test here would still be green.

The signature row needs a date literal in a date's shape, and one of the two
spellings it drives is the US short form the shape layer refuses. Every draft in
this file is invented and no patient is described by any of them, so:

phi-scan: synthetic

**The completeness walks are AST walks and not substring searches**, on
``test_console_codec``'s instrument and for its reason: this module's docstring
names every row it has, so a text search for a row's name is satisfied by the
prose explaining it. Both were mutation-tested before they were believed.
"""

from __future__ import annotations

import ast
import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import case_study_scan as scan
from grader_conformance import for_module

GraderConformance = for_module(scan)
import docx_write
import research_ledger

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"
STYLE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "style.md"
MODULE = Path(scan.__file__)

# A prescription table in exactly the shape ``style.md`` section 8 publishes: an
# empty three-cell header, then six rows whose cell counts are the merge pattern.
RX_TABLE = """\
| | | |
| --- | --- | --- |
| `<patient>` | DOB x-x-xxx | NPI # 1234567890 |
| Ceftriaxone 500 mg IM once |
| Disp: 1 vial |
| Sig: Inject 500 mg into the muscle one time for pelvic inflammatory disease |
| M. S. FNP-C, CEN, TCRN |
| Refill: none | DEA number on file with pharmacy |
"""

# A draft that passes every row, so a test can break one thing and know the
# finding it gets back belongs to that thing.
CLEAN = """\
## Sanity Check

Module 1 - confirmed

## Demographics

Age: 26 years. Sex: Female. Occupation: Elementary school teacher.

## Review of Systems

General: + fatigue and fever, - chills and weight loss.

All other systems reviewed and are negative.

## Physical Examination

General: Alert, in no acute distress.

## Differential Diagnoses

1. Pelvic inflammatory disease - N73.9
2. Cervicitis - N72

## Most Likely Clinical Diagnosis

Pelvic inflammatory disease, due to the cervical motion tenderness and the
purulent discharge.

## Rx:

{rx}
Third-generation cephalosporin. Monitor the injection site.

Signed by: M. S., RN, CEN, TCRN. August 19, 2026

## References

Ross, J. (2025). Pelvic inflammatory disease. UpToDate.
""".format(rx=RX_TABLE)


# One phrase per row, keyed on the module's own tuple, so a row added without a
# sentence in the skill fails here rather than becoming a rule only the scanner
# knows. ``test_checks_ledger.ROW_PHRASES``'s arrangement, and the skill's
# enumeration is the **one** copy -- ``CLAUDE.md`` points at it now rather than
# repeating it, because two hand-kept lists of a set held in code is #220.
ROW_PHRASES = {
    scan.BULLET_MARKER: "no bullet anywhere in the document",
    scan.INTAKE_TABLE: (
        "no table under Demographics, the Review of Systems or the Physical Examination"
    ),
    scan.ROS_NO_CLOSER: "the Review of Systems closing with the all-other-systems disclaimer",
    scan.EXAM_CLAIMS_UNEXAMINED: "the Physical Examination not carrying one",
    scan.SCAFFOLDING_PHRASE: "no scaffolding language",
    scan.DIAGNOSIS_ALL_BOLD: "the Most Likely Clinical Diagnosis not set wholly bold",
    scan.SIGNATURE_DATE_SPLIT: "the signature and its date on one line",
    scan.RX_TABLE_SHAPE: "the prescription table at six rows and three columns wide",
    scan.NO_STOP_CRITERION: "a drug that continues carrying a stop criterion",
}


def survey(markdown: str):
    """Grade a draft with the skeleton check satisfied, so a row test sees only its row."""
    return scan.survey(markdown, SKILL.read_text(encoding="utf-8"))


def kinds(markdown: str) -> list[str]:
    return [finding.kind for finding in survey(markdown).findings]


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = scan.main(argv)
    return status, out.getvalue(), err.getvalue()


def draft_file(markdown: str) -> tuple[tempfile.TemporaryDirectory, Path]:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "case.md"
    path.write_text(markdown, encoding="utf-8")
    return directory, path


class TheCleanDraftIsClean(unittest.TestCase):
    """The fixture every row test rests on passes, or none of them mean anything."""

    def test_no_findings(self):
        self.assertEqual(kinds(CLEAN), [])

    def test_exits_zero(self):
        directory, path = draft_file(CLEAN)
        try:
            status, out, _ = run([str(path)])
        finally:
            directory.cleanup()
        self.assertEqual(status, 0, out)

    def test_every_section_is_found(self):
        found = {section.name for section in scan.read_sections(CLEAN)[0]}
        for name in scan.INTAKE_SECTIONS:
            self.assertIn(name, found)
        self.assertIn(scan.RX, found)
        self.assertIn(scan.MOST_LIKELY, found)


class TheBulletRow(unittest.TestCase):
    """Never bullets, anywhere in the document. Ruled 2026-08-19."""

    def test_a_bullet_anywhere_fires(self):
        self.assertIn(scan.BULLET_MARKER, kinds(CLEAN + "\n- Onset: three days ago\n"))

    def test_a_numbered_list_does_not(self):
        self.assertNotIn(scan.BULLET_MARKER, kinds(CLEAN + "\n3. Appendicitis - K35.80\n"))

    def test_a_hyphen_inside_a_line_does_not(self):
        """``Module 3 - confirmed`` and ``Cervicitis - N72`` are the house forms."""
        self.assertNotIn(scan.BULLET_MARKER, kinds(CLEAN))

    def test_a_bullet_inside_a_fence_still_fires(self):
        """The renderer opens nothing on a fence, so a bullet inside one is a bullet.

        This is the one place ``spelling_scan``'s mention-versus-use rule
        deliberately does **not** transfer, and it transfers by way of the parse
        rather than by a decision here: ``docx_write.blocks`` has no fence branch.
        """
        self.assertIn(scan.BULLET_MARKER, kinds(CLEAN + "\n```\n- Onset: today\n```\n"))

    def test_the_row_reads_what_the_renderer_sets(self):
        """A bullet this counts is a ``ListParagraph`` in the document.

        The claim the row makes is about the ``.docx``, and it is only true
        because both readings come from one parser.
        """
        text = CLEAN + "\n- Onset: three days ago\n- Location: lower abdomen\n"
        counted = len([k for k in kinds(text) if k == scan.BULLET_MARKER])
        rendered = docx_write.body_xml(text).count('w:val="ListParagraph"')
        numbered = len(
            [b for b in docx_write.blocks(text) if b.kind == "numbered"]
        )
        self.assertEqual(counted, 2)
        self.assertEqual(rendered - numbered, counted)


class TheIntakeTableRow(unittest.TestCase):
    """Demographics, the ROS and the exam are defined fields, never a table."""

    TABLE = "\n| Field | Value |\n| --- | --- |\n| Age | 26 years |\n"

    def test_a_table_under_demographics_fires(self):
        text = CLEAN.replace(
            "Age: 26 years. Sex: Female. Occupation: Elementary school teacher.", self.TABLE
        )
        self.assertIn(scan.INTAKE_TABLE, kinds(text))

    def test_a_table_under_the_review_of_systems_fires(self):
        text = CLEAN.replace(
            "General: + fatigue and fever, - chills and weight loss.", self.TABLE
        )
        self.assertIn(scan.INTAKE_TABLE, kinds(text))

    def test_a_table_elsewhere_does_not(self):
        """A given result set is still a table, which is why the row is keyed on section."""
        text = CLEAN + "\n## Assessment:\n" + self.TABLE
        self.assertNotIn(scan.INTAKE_TABLE, kinds(text))

    def test_the_prescription_table_does_not(self):
        self.assertNotIn(scan.INTAKE_TABLE, kinds(CLEAN))


class TheTwoCloserRows(unittest.TestCase):
    """The ROS closes with the disclaimer and the examination does not.

    Two rows out of one ruling, and the second is the higher-stakes one: the same
    sentence under an examination claims maneuvers that were not performed.
    """

    def test_a_review_of_systems_with_no_closer_fires(self):
        self.assertIn(
            scan.ROS_NO_CLOSER,
            kinds(CLEAN.replace("\nAll other systems reviewed and are negative.\n", "\n")),
        )

    def test_the_closer_present_does_not(self):
        self.assertNotIn(scan.ROS_NO_CLOSER, kinds(CLEAN))

    def test_unremarkable_is_the_same_sentence(self):
        text = CLEAN.replace(
            "All other systems reviewed and are negative.",
            "All other systems were reviewed and are unremarkable.",
        )
        self.assertNotIn(scan.ROS_NO_CLOSER, kinds(text))

    def test_a_closer_under_the_examination_fires(self):
        text = CLEAN.replace(
            "General: Alert, in no acute distress.",
            "General: Alert. All other systems reviewed and are negative.",
        )
        self.assertIn(scan.EXAM_CLAIMS_UNEXAMINED, kinds(text))

    def test_the_examination_without_one_does_not(self):
        self.assertNotIn(scan.EXAM_CLAIMS_UNEXAMINED, kinds(CLEAN))

    def test_a_closer_written_early_in_the_section_still_passes(self):
        """Matched anywhere in the section, and the narrowing is deliberate.

        A position test would fail a document that says the thing the rule asks
        it to say, which is the outcome #215 rules out.
        """
        text = CLEAN.replace(
            "General: + fatigue and fever, - chills and weight loss.\n\n"
            "All other systems reviewed and are negative.",
            "All other systems reviewed and are negative.\n\n"
            "General: + fatigue and fever, - chills and weight loss.",
        )
        self.assertNotIn(scan.ROS_NO_CLOSER, kinds(text))


class TheScaffoldingRow(unittest.TestCase):
    """The closed set from section 1a's own table."""

    def test_every_phrase_in_the_set_fires(self):
        for phrase, _ in scan.SCAFFOLDING:
            with self.subTest(phrase=phrase):
                found = [
                    finding
                    for finding in survey(CLEAN + "\n" + phrase + " here.\n").findings
                    if finding.kind == scan.SCAFFOLDING_PHRASE
                ]
                self.assertEqual([f.what for f in found], [phrase])

    def test_the_expansion_fires_and_the_abbreviation_does_not(self):
        self.assertIn(scan.SCAFFOLDING_PHRASE, kinds(CLEAN + "\nNo known drug allergies.\n"))
        self.assertNotIn(scan.SCAFFOLDING_PHRASE, kinds(CLEAN + "\nAllergies: NKDA.\n"))

    def test_ordinary_prose_using_the_word_ordered_does_not(self):
        """The phrase is the idiom, not the word. ``Ordered`` is an ordinary verb here."""
        text = CLEAN + "\nOrdered a pregnancy test, and a urinalysis was ordered as well.\n"
        self.assertNotIn(scan.SCAFFOLDING_PHRASE, kinds(text))

    def test_a_phrase_inside_a_table_cell_fires(self):
        text = CLEAN + "\n## Assessment:\n\n| a | b |\n| --- | --- |\n| Using OLDCARTS | x |\n"
        self.assertIn(scan.SCAFFOLDING_PHRASE, kinds(text))


class TheBoldRow(unittest.TestCase):
    """The Most Likely Clinical Diagnosis is not wholly bold -- *"I don't do that."*"""

    STATEMENT = (
        "Pelvic inflammatory disease, due to the cervical motion tenderness and the\n"
        "purulent discharge."
    )

    def test_a_wholly_bold_statement_fires(self):
        text = CLEAN.replace(
            self.STATEMENT, "**Pelvic inflammatory disease, due to the tenderness.**"
        )
        self.assertIn(scan.DIAGNOSIS_ALL_BOLD, kinds(text))

    def test_body_face_does_not(self):
        self.assertNotIn(scan.DIAGNOSIS_ALL_BOLD, kinds(CLEAN))

    def test_a_bolded_phrase_inside_the_sentence_does_not(self):
        """Emphasis is left alone; only the whole statement wrapped is the defect."""
        text = CLEAN.replace(
            self.STATEMENT,
            "Pelvic inflammatory disease, due to the **cervical motion tenderness**.",
        )
        self.assertNotIn(scan.DIAGNOSIS_ALL_BOLD, kinds(text))

    def test_a_bold_statement_in_another_section_does_not(self):
        text = CLEAN + "\n## Assessment:\n\n**The urinalysis contradicts the narration.**\n"
        self.assertNotIn(scan.DIAGNOSIS_ALL_BOLD, kinds(text))


class TheSignatureRow(unittest.TestCase):
    """The signature and the date sit on one line."""

    LINE = "Signed by: M. S., RN, CEN, TCRN. August 19, 2026"

    def test_the_date_on_its_own_line_fires(self):
        text = CLEAN.replace(self.LINE, "Signed by: M. S., RN, CEN, TCRN\n\nAugust 19, 2026")
        self.assertIn(scan.SIGNATURE_DATE_SPLIT, kinds(text))

    def test_one_line_does_not(self):
        self.assertNotIn(scan.SIGNATURE_DATE_SPLIT, kinds(CLEAN))

    def test_a_numeric_date_is_a_date(self):
        text = CLEAN.replace(self.LINE, "Signed by: M. S., RN, CEN, TCRN. 08/19/2026")
        self.assertNotIn(scan.SIGNATURE_DATE_SPLIT, kinds(text))

    def test_a_heading_with_the_signature_under_it_is_read(self):
        text = CLEAN.replace(
            self.LINE, "## Signed by:\n\nM. S., RN, CEN, TCRN\n\nAugust 19, 2026"
        )
        self.assertIn(scan.SIGNATURE_DATE_SPLIT, kinds(text))

    def test_a_heading_whose_line_carries_the_date_does_not(self):
        text = CLEAN.replace(
            self.LINE, "## Signed by:\n\nM. S., RN, CEN, TCRN. August 19, 2026"
        )
        self.assertNotIn(scan.SIGNATURE_DATE_SPLIT, kinds(text))


class TheTwoPrescriptionRows(unittest.TestCase):
    """The section 8 shape, and the stop criterion in the drug row."""

    def test_the_documented_shape_passes(self):
        self.assertNotIn(scan.RX_TABLE_SHAPE, kinds(CLEAN))

    def test_a_one_column_table_fires(self):
        table = "| |\n| --- |\n| `<patient>` |\n| Ceftriaxone 500 mg IM once |\n"
        self.assertIn(scan.RX_TABLE_SHAPE, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_a_seventh_row_fires(self):
        table = RX_TABLE + "| Note: an extra row |\n"
        self.assertIn(scan.RX_TABLE_SHAPE, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_the_last_row_padded_to_three_fires(self):
        """Two cells is what puts the refill left and the DEA line right."""
        table = RX_TABLE.replace(
            "| Refill: none | DEA number on file with pharmacy |",
            "| Refill: none | DEA number on file with pharmacy | |",
        )
        self.assertIn(scan.RX_TABLE_SHAPE, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_a_recurring_order_with_no_endpoint_fires(self):
        table = RX_TABLE.replace(
            "| Ceftriaxone 500 mg IM once |", "| Ceftriaxone 1 g IV every 24 hours |"
        )
        self.assertIn(scan.NO_STOP_CRITERION, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_a_one_time_dose_states_its_own_endpoint(self):
        self.assertNotIn(scan.NO_STOP_CRITERION, kinds(CLEAN))

    def test_once_daily_is_recurring_and_not_an_endpoint(self):
        """``once`` closes an order and ``once daily`` opens one, which is the lookahead."""
        table = RX_TABLE.replace(
            "| Ceftriaxone 500 mg IM once |", "| Doxycycline 100 mg PO once daily |"
        )
        self.assertIn(scan.NO_STOP_CRITERION, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_a_duration_closes_it(self):
        for order in (
            "Doxycycline 100 mg PO BID x 14 days",
            "Doxycycline 100 mg PO BID for 14 days",
            "Ceftriaxone 1 g IV every 24 hours until the fever curve settles",
            "Ceftriaxone 1 g IV every 24 hours, continued for the admission",
        ):
            with self.subTest(order=order):
                table = RX_TABLE.replace(
                    "| Ceftriaxone 500 mg IM once |", "| " + order + " |"
                )
                self.assertNotIn(scan.NO_STOP_CRITERION, kinds(CLEAN.replace(RX_TABLE, table)))

    def test_a_table_outside_the_prescription_section_is_not_graded(self):
        text = CLEAN + "\n## Assessment:\n\n| a | b |\n| --- | --- |\n| x | y |\n"
        self.assertNotIn(scan.RX_TABLE_SHAPE, kinds(text))


class TheEmDashIsCountedAndNeverGraded(unittest.TestCase):
    """A stated preference with a stated exception, and #215's defect a third time.

    His words: *"generally I prefer not to use em dashes, just saying, though I do
    use them sometimes."* A row keyed on it would refuse a document he would have
    written himself.
    """

    def test_a_draft_full_of_them_is_clean(self):
        text = CLEAN.replace(
            "Age: 26 years. Sex: Female.",
            "Age: 26 years — a young adult — and female. Sex: Female.",
        )
        result = survey(text)
        self.assertEqual(result.findings, [])
        self.assertEqual(result.em_dashes, 2)

    def test_the_report_says_it_is_never_graded(self):
        report = scan.format_report(survey(CLEAN), "draft.md")
        self.assertIn("NEVER GRADED", report)

    def test_no_row_is_keyed_on_one(self):
        self.assertNotIn("em", [kind.split("-")[0] for kind in scan.KINDS])


class NumberingAdvisoriesAreNotRows(unittest.TestCase):
    """#402: report authored-number surprises without rejecting valid continuations."""

    def test_a_section_that_starts_above_one_is_counted(self):
        text = CLEAN.replace(
            "1. Pelvic inflammatory disease - N73.9\n2. Cervicitis - N72",
            "4. Pelvic inflammatory disease - N73.9\n5. Cervicitis - N72",
        )
        result = survey(text)
        self.assertEqual(result.numbered_sections_not_opening_at_one, 1)
        self.assertEqual(result.broken_numbered_transitions, 0)
        self.assertEqual(result.findings, [])

    def test_a_broken_sequence_is_counted(self):
        text = CLEAN.replace("2. Cervicitis - N72", "3. Cervicitis - N72")
        result = survey(text)
        self.assertEqual(result.numbered_sections_not_opening_at_one, 0)
        self.assertEqual(result.broken_numbered_transitions, 1)
        self.assertEqual(result.findings, [])

    def test_the_report_declares_both_counts_never_graded(self):
        report = scan.format_report(survey(CLEAN), "draft.md")
        self.assertIn("sections not opening at 1", report)
        self.assertIn("broken numbered transitions", report)
        self.assertEqual(report.count("COUNTED, NEVER GRADED"), 3)

    def test_an_advisory_does_not_change_the_exit_status(self):
        text = CLEAN.replace("2. Cervicitis - N72", "3. Cervicitis - N72")
        directory, path = draft_file(text)
        try:
            status, _, _ = run([str(path)])
        finally:
            directory.cleanup()
        self.assertEqual(status, 0)


class TheReportIsCountsOnlyByDefault(unittest.TestCase):
    """``--show`` is PHI, so the default report may not carry the draft's prose.

    Measured rather than argued -- ``reference_scan``'s salted-draft method, used
    here to reach the opposite conclusion, which is what makes the measurement
    worth taking either way.
    """

    MARKER = "Zzyzxqq"

    def salted(self) -> str:
        text = CLEAN
        text = text.replace("Age: 26 years", "Age: 26 years, " + self.MARKER)
        text = text.replace(
            "General: Alert, in no acute distress.",
            "General: Alert. All other systems reviewed and are negative. " + self.MARKER,
        )
        text = text.replace(
            "Pelvic inflammatory disease, due to the cervical motion tenderness and the\n"
            "purulent discharge.",
            "**Pelvic inflammatory disease, " + self.MARKER + ".**",
        )
        text = text.replace(
            "| Ceftriaxone 500 mg IM once |",
            "| Ceftriaxone 1 g IV every 24 hours " + self.MARKER + " |",
        )
        return text + "\n- " + self.MARKER + " bullet\n"

    def test_the_salted_draft_fires_several_rows(self):
        """The measurement is worthless if the rows that quote prose never fired."""
        fired = set(kinds(self.salted()))
        for kind in (
            scan.BULLET_MARKER,
            scan.EXAM_CLAIMS_UNEXAMINED,
            scan.DIAGNOSIS_ALL_BOLD,
            scan.NO_STOP_CRITERION,
        ):
            self.assertIn(kind, fired)

    def test_the_default_report_carries_none_of_it(self):
        report = scan.format_report(survey(self.salted()), "draft.md")
        self.assertNotIn(self.MARKER, report)

    def test_show_carries_it_which_is_why_it_is_phi(self):
        report = scan.format_report(survey(self.salted()), "draft.md", show=True)
        self.assertIn(self.MARKER, report)

    def test_the_default_report_says_the_detail_is_phi(self):
        report = scan.format_report(survey(self.salted()), "draft.md")
        self.assertIn("PHI", report)


class TheExitStatus(unittest.TestCase):
    """0 clean, 1 for a defect, 2 for every way of not having scanned."""

    def test_no_argument_is_two(self):
        self.assertEqual(run([])[0], 2)

    def test_an_unknown_option_is_two(self):
        self.assertEqual(run(["draft.md", "--everything"])[0], 2)

    def test_two_drafts_is_two(self):
        self.assertEqual(run(["a.md", "b.md"])[0], 2)

    def test_a_missing_file_is_two(self):
        directory = tempfile.TemporaryDirectory()
        try:
            self.assertEqual(run([str(Path(directory.name) / "gone.md")])[0], 2)
        finally:
            directory.cleanup()

    def test_a_defect_is_one(self):
        directory, path = draft_file(CLEAN + "\n- a bullet\n")
        try:
            self.assertEqual(run([str(path)])[0], 1)
        finally:
            directory.cleanup()

    def test_a_document_with_no_section_this_reads_is_two(self):
        directory, path = draft_file("## Notes\n\nSome prose with no skeleton heading.\n")
        try:
            status, out, _ = run([str(path)])
        finally:
            directory.cleanup()
        self.assertEqual(status, 2)
        self.assertIn("no section this recognizes", out)

    def test_a_defect_beats_a_not_scanned_limb(self):
        """1 wins, on ``differential_scan``'s ordering, and the banner prints beside it.

        Returning 2 would file the strongest thing known about the draft under the
        weakest heading.
        """
        result = scan.survey("- a bullet with no heading anywhere\n", SKILL.read_text("utf-8"))
        self.assertTrue(result.no_section)
        self.assertTrue(result.findings)
        report = scan.format_report(result, "draft.md")
        self.assertIn("no section this recognizes", report)

    def test_an_unreadable_skeleton_is_declared(self):
        result = scan.survey(CLEAN, None)
        report = scan.format_report(result, "draft.md")
        self.assertIn("SKILL.md was not read", report)


class TheSkeletonIsTheSkillsOwn(unittest.TestCase):
    """``SKELETON`` is what ``SKILL.md`` publishes, checked from the command.

    ``checks_ledger`` holds its vocabulary and derives it in the test;
    ``guidelines_catalog.check_legend`` parses the published Markdown in the
    command. #277's second comment records why the second is the only binding a
    **run** hits, so this does both.
    """

    def test_the_module_holds_what_the_skill_publishes(self):
        self.assertEqual(scan.read_skeleton(SKILL.read_text("utf-8")), scan.SKELETON)

    def test_the_check_is_clean_against_the_tree(self):
        self.assertEqual(scan.check_skeleton(SKILL.read_text("utf-8")), [])

    def test_the_check_is_live(self):
        """A check that says yes to everything is worse than none.

        ``TheInstrumentIsLive`` in ``test_build_artifacts_ignored`` for the same
        reason, and its first version passed three of four assertions against
        exactly such a check.
        """
        text = SKILL.read_text("utf-8").replace("**Sanity Check**", "**Sanity Checks**", 1)
        failures = scan.check_skeleton(text)
        self.assertTrue(failures)
        self.assertTrue(any("Sanity Checks" in failure for failure in failures))

    def test_a_skill_with_no_skeleton_list_is_named_as_one(self):
        self.assertEqual(
            scan.check_skeleton("# A skill with no list"),
            ["no skeleton list in SKILL.md, so the section vocabulary cannot be read"],
        )

    def test_a_reordered_skeleton_is_a_disagreement(self):
        published = scan.read_skeleton(SKILL.read_text("utf-8"))
        reordered = (published[1], published[0]) + published[2:]
        body = "The skeleton, in order:\n\n" + "".join(
            "{n}. **{name}** - a section.\n".format(n=index + 1, name=name)
            for index, name in enumerate(reordered)
        )
        self.assertTrue(scan.check_skeleton(body))

    def test_the_command_refuses_a_disagreement(self):
        directory, path = draft_file(CLEAN)
        try:
            result = scan.survey(CLEAN, "# no skeleton here")
        finally:
            directory.cleanup()
        self.assertTrue(result.skeleton_disagreement)
        self.assertIn("SKELETON DISAGREEMENT", scan.format_report(result, "draft.md"))


class SplittingADrugRowOnAndIsRefusedHere(unittest.TestCase):
    """Why ``no-stop-criterion`` reads one table cell as one order, re-derived in
    the suite a ``case_study_scan`` author runs.

    [#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300) was
    ruled a **reading** on 2026-08-20 -- the welded row goes to
    ``skills/practicum-case-study/SKILL.md`` step 9's ``the Rx blocks`` reader and
    no parser here moved. **The sibling measurement lives in
    ``test_research_ledger`` and a green run there is not one here**, which is the
    gap this class closes: the refusal was written as a comment at the grading
    site, and a comment fails nothing --
    [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

    **The counterexample that comment cited did not demonstrate the refusal, and
    that was found by running the string rather than by reading it.**
    ``metronidazole 500 mg PO TID and hold if the creatinine rises`` states a
    frequency and no endpoint this row recognizes, so it fires **whole** -- split
    or unsplit the verdict is identical, and the example proved nothing about
    splitting. ``block_scan.py``'s and ``threshold_sheet.py``'s lesson a further
    time. The order below is the property the refusal actually rests on: clean
    whole, and a false alarm once split.
    """

    ORDER = "metronidazole 500 mg PO TID and continue until the abscess resolves"
    THE_ONE_THAT_PROVED_NOTHING = "metronidazole 500 mg PO TID and hold if the creatinine rises"

    @staticmethod
    def fires(order: str) -> bool:
        """``no-stop-criterion``'s own test, read off the module rather than
        restated -- a copy of the rule here could pass while the row failed."""
        return bool(scan.RECURRING.search(order)) and not scan.ENDPOINT.search(order)

    def test_the_order_is_clean_whole(self):
        self.assertFalse(self.fires(self.ORDER))

    def test_splitting_it_on_and_fires_the_row_on_a_correct_order(self):
        """One correct order becomes two fragments and the first states no
        endpoint, which is a false alarm on a correct order --
        [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s
        outcome, and the ground the split is refused on."""
        self.assertTrue(self.fires(self.ORDER.split(" and ")[0]))

    def test_the_retired_counterexample_fires_either_way(self):
        """Stated as a passing assertion so it cannot be mistaken for an
        oversight: the string the comment used to cite is a finding whole, so it
        could never have shown what splitting costs."""
        self.assertTrue(self.fires(self.THE_ONE_THAT_PROVED_NOTHING))
        self.assertTrue(self.fires(self.THE_ONE_THAT_PROVED_NOTHING.split(" and ")[0]))

    def module_prose(self) -> str:
        """The module with its comment markers stripped, so a wrapped comment is
        searchable -- ``test_run_record_claim``'s finding, which a raw substring
        search over ``#``-prefixed continuation lines walks straight past."""
        lines = [
            re.sub(r"^\s*#\s?", "", line)
            for line in Path(scan.__file__).read_text(encoding="utf-8").splitlines()
        ]
        return " ".join(" ".join(lines).split()).lower()

    def test_the_grading_site_names_the_order_this_class_measures(self):
        """So the comment and the measurement cannot drift apart, which is the
        whole reason this class exists rather than a sentence."""
        self.assertIn(self.ORDER.lower(), self.module_prose())

    def test_the_declaration_is_still_the_one_the_skill_names(self):
        """The row stays declared -- #300 changed what a reader is asked, and
        changed nothing about what this command reaches."""
        self.assertIn(
            "a second drug welded into one drug row, discharged by the first drug's endpoint",
            scan.NOT_REACHED,
        )


class EveryDeclaredLimitHasAnEvidenceDisposition(unittest.TestCase):
    """#323's per-row split: execute what is mechanical and declare the rest.

    A name bind proves only that two declarations agree. This class instead makes
    every declared limit choose exactly one evidence disposition. The mechanically
    reachable row is driven through ``survey`` below. The other rows remain declared
    readings; this class does not claim they have the mandatory reader whose absence
    is #306's separate question.
    """

    WELDED = (
        "a second drug welded into one drug row, discharged by the first drug's endpoint"
    )
    SOURCED_DOSE = "whether a dose was sourced at all"

    def test_every_limit_has_exactly_one_known_disposition(self):
        self.assertEqual(
            [key for key, _ in scan.DECLARED_LIMITS],
            list(scan.NOT_REACHED),
        )
        for key, disposition in scan.DECLARED_LIMITS:
            with self.subTest(key=key):
                self.assertIsInstance(disposition, scan.EvidenceDisposition)
        self.assertEqual(
            [
                key
                for key, disposition in scan.DECLARED_LIMITS
                if disposition is scan.EvidenceDisposition.BEHAVIOR
            ],
            [self.WELDED, self.SOURCED_DOSE],
        )

    def test_the_welded_second_drug_really_is_discharged_by_the_first_endpoint(self):
        order = "Doxycycline 100 mg PO BID x 7 days and metronidazole 500 mg PO TID"
        table = RX_TABLE.replace("| Ceftriaxone 500 mg IM once |", "| " + order + " |")
        self.assertNotIn(scan.NO_STOP_CRITERION, kinds(CLEAN.replace(RX_TABLE, table)))

        # The control proves the row is absent because the first drug's endpoint is
        # read across the welded cell, not because the scanner cannot see a recurring
        # second order at all.
        second_only = RX_TABLE.replace(
            "| Ceftriaxone 500 mg IM once |", "| metronidazole 500 mg PO TID |"
        )
        self.assertIn(scan.NO_STOP_CRITERION, kinds(CLEAN.replace(RX_TABLE, second_only)))

    def test_the_sibling_ledger_really_grades_whether_a_dose_was_sourced(self):
        prescription = research_ledger.Prescription(
            "metronidazole", "metronidazole 500 mg PO TID", ""
        )
        unsupported = research_ledger.prescription_findings([prescription], [])
        self.assertEqual(
            [finding.kind for finding in unsupported],
            [research_ledger.UNRESEARCHED_PRESCRIPTION],
        )

        sourced = research_ledger.Record(
            "Metronidazole 500 mg by mouth three times daily is the sourced dose."
        )
        self.assertEqual(
            research_ledger.prescription_findings([prescription], [sourced]), []
        )


class TheSkillSaysWhatThisCannotDo(unittest.TestCase):
    """``NOT_REACHED`` and the step that names the same items are one list.

    ``test_reference_scan``'s binding of ``NOT_REACHED`` to ``apa7.md`` section 7,
    and it is here for #220's reason: a prose edit to either copy fails nothing,
    so the reader who is misled is whichever one they checked.

    **Compared against a whitespace-normalized block rather than the raw file**,
    on ``test_run_record_claim``'s finding: a phrase hard-wrapped across two lines
    is invisible to a substring search, and every item in this list is long enough
    to be wrapped. Written that way after the first version reported three of six
    missing from a file that named all six.
    """

    @classmethod
    def setUpClass(cls):
        text = SKILL.read_text(encoding="utf-8")
        cls.step = text[text.index("### 9. Check") :]
        cls.flat = re.sub(r"\s+", " ", cls.step)

    def test_every_item_is_named_in_the_step(self):
        for item in scan.NOT_REACHED:
            with self.subTest(item=item):
                self.assertIn(re.sub(r"\s+", " ", item), self.flat)

    def test_the_step_names_no_others(self):
        """The other direction, so a row moved out of the tuple answers in a diff."""
        opens = "what no row of that command reaches"
        block = self.step[self.step.index(opens) :]
        block = block[: block.index("\n\n")]
        named = [re.sub(r"\s+", " ", item) for item in re.findall(r"\*\*(.+?)\*\*", block, re.S)]
        self.assertEqual(sorted(named), sorted(re.sub(r"\s+", " ", i) for i in scan.NOT_REACHED))

    def test_the_step_says_a_clean_scan_is_not_a_checked_draft(self):
        self.assertIn("A clean scan is not a checked draft", self.flat)

    def test_the_step_names_the_command(self):
        self.assertIn("python tools/case_study_scan.py", self.step)

    def test_the_step_says_the_show_output_is_phi(self):
        """The PHI ruling sits in the subsection that carries the command.

        Scoped to the subsection rather than to a character window, because a
        window is a claim about how long the prose above it happens to be.
        """
        opens = "#### The house style is a command now"
        section = self.step[self.step.index(opens) :]
        section = section[: section.index("\n**One reader per row")]
        self.assertIn("python tools/case_study_scan.py", section)
        self.assertIn("**that output is PHI**: read it, do not paste it", re.sub(r"\s+", " ", section))

    def test_the_step_says_the_em_dash_is_never_graded(self):
        """The one ruling in this row set that is a decision *not* to grade."""
        self.assertIn("counted and never graded", self.flat)


class TheDocumentedShapesPass(unittest.TestCase):
    """Run the scanner over the shapes ``style.md`` itself publishes.

    A documented form the grader would refuse teaches the next run to write a
    draft that fails, and every substring test above would still be green.
    ``test_checks_ledger``'s worked-example class, one artifact over.
    """

    def test_the_section_eight_table_is_the_shape_this_grades(self):
        """The published table's row shape is ``RX_ROW_CELLS``, read out of the sheet."""
        text = STYLE.read_text("utf-8")
        block = text[text.index("## 8. Rx") :]
        block = block[: block.index("\n\n**The table is three columns")]
        rows = [b for b in docx_write.blocks(block) if b.kind == "table"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(tuple(len(row) for row in rows[0].rows[1:]), scan.RX_ROW_CELLS)

    def test_the_section_one_a_review_of_systems_example_carries_no_table(self):
        text = STYLE.read_text("utf-8")
        block = text[text.index("### The Review of Systems and the Physical Examination") :]
        block = block[: block.index("### Never bullets")]
        self.assertNotIn("| --- |", block)

    def test_the_scaffolding_set_is_the_sheets_own_table(self):
        """Every ``Written`` cell of section 1a's table is a phrase this refuses."""
        text = STYLE.read_text("utf-8")
        block = text[text.index("### No scaffolding language") :]
        block = block[: block.index("\n\n**`Ordered, not assumed`")]
        written = docx_write.table_first_cells(block)
        self.assertTrue(written)
        for cell in written:
            with self.subTest(cell=cell):
                self.assertTrue(
                    any(pattern.search(cell) for _, pattern in scan.SCAFFOLDING),
                    "section 1a forbids {c!r} and no row reads it".format(c=cell),
                )


class EveryRowIsDeclared(unittest.TestCase):
    """The report and skill still expose every row the shared walk derives."""

    def test_the_report_prints_every_row_on_a_clean_draft(self):
        """A row that fired nowhere still prints its zero, so the set is readable."""
        report = scan.format_report(survey(CLEAN), "draft.md")
        for kind in scan.KINDS:
            with self.subTest(kind=kind):
                self.assertIn(kind, report)

    def test_every_row_has_a_sentence_in_the_skill(self):
        """A row added with no sentence in the skill fails here.

        ``test_checks_ledger.ROW_PHRASES``'s arrangement, keyed on the module's own
        tuple: [AGENTS.md](AGENTS.md) classes this as a tool a skill *names* rather
        than one it depends on, and that class is defined by the instruction being
        complete without the command. **The enumeration in the skill is the one
        copy** -- ``CLAUDE.md`` points at it rather than repeating it, because two
        hand-kept lists of a set held in code is
        [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).
        """
        step = SKILL.read_text(encoding="utf-8")
        step = " ".join(step[step.index("### 9. Check") :].split())
        for kind, phrase in ROW_PHRASES.items():
            with self.subTest(row=kind):
                self.assertIn(phrase, step)

    def test_the_phrase_map_is_the_row_set(self):
        self.assertEqual(sorted(ROW_PHRASES), sorted(scan.KINDS))


class TheParserIsTheRenderers(unittest.TestCase):
    """``read_sections`` consumes ``docx_write.blocks`` and holds no copy of it.

    ``reference_scan`` imports ``REFERENCE_HEADING`` for this reason; here the
    same argument runs at the width of the whole parse, so a table this calls a
    table ends where the renderer ends it.
    """

    def compiled_patterns(self) -> list[str]:
        """Every string literal that reaches a ``re.compile`` in the module.

        **Through a concatenation and through a module constant**, which the first
        version did neither of: it called ``ast.literal_eval`` on the first
        argument, so ``re.compile(a + b)`` raised ``ValueError`` and took the test
        down rather than reading it, and a pattern assembled from a named constant
        was invisible. Found by feeding the predicate a mutant rather than by
        reading it, and both spellings are now in the tree -- ``ENDPOINT`` is built
        both ways.

        **What is still out of reach** is a pattern assembled at run time, or one
        read from a file. That is `test_ls_files_coverage.py`'s ceiling, and it is
        declared here for its reason rather than closed.
        """
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        literals = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            literals[target.id] = node.value.value
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr == "compile"
                and isinstance(func.value, ast.Name)
                and func.value.id == "re"
            ):
                continue
            for argument in node.args[:1]:
                for part in ast.walk(argument):
                    if isinstance(part, ast.Constant) and isinstance(part.value, str):
                        found.append(part.value)
                    elif isinstance(part, ast.Name) and part.id in literals:
                        found.append(literals[part.id])
        return found

    def test_the_walk_reads_the_patterns_that_are_there(self):
        """A predicate that found nothing would pass the test below saying nothing."""
        found = self.compiled_patterns()
        self.assertGreaterEqual(len(found), len(scan.KINDS))
        joined = "".join(found)
        self.assertIn("OLDCARTS", joined, "the walk is not reading the module's patterns")
        self.assertIn("month", joined, "the walk does not reach a concatenated pattern")

    def test_the_module_defines_no_markdown_pattern_of_its_own(self):
        for source in self.compiled_patterns():
            self.assertNotIn(
                "#{1,4}", source, "the heading pattern belongs to docx_write, not here"
            )
            self.assertNotIn(
                "[-*+]", source, "the bullet pattern belongs to docx_write, not here"
            )

    def test_a_heading_this_does_not_know_closes_the_section_above_it(self):
        """Without it, everything after a ``### Note`` sits inside the section above."""
        text = "## Rx:\n\n" + RX_TABLE + "\n## History of Present Illness\n\n" + RX_TABLE
        graded = [s for s in scan.read_sections(text)[0] if s.name == scan.RX]
        self.assertEqual(len(graded), 1)
        self.assertEqual(len([b for b in graded[0].blocks if b.kind == "table"]), 1)

    def test_a_deeper_unknown_heading_does_not_close_it(self):
        text = "## Rx:\n\n" + RX_TABLE + "\n### A note about the order\n\n" + RX_TABLE
        graded = [s for s in scan.read_sections(text)[0] if s.name == scan.RX]
        self.assertEqual(len([b for b in graded[0].blocks if b.kind == "table"]), 2)

    def test_a_label_paragraph_opens_a_section(self):
        """A run may write an intake subsection as a bold label rather than a heading."""
        text = "## Sanity Check\n\nModule 1 - confirmed\n\n**Review of Systems:**\n\nGeneral: + fever.\n"
        names = [section.name for section in scan.read_sections(text)[0]]
        self.assertIn(scan.REVIEW_OF_SYSTEMS, names)

    def test_a_paragraph_that_merely_opens_with_a_label_does_not(self):
        """``Signed by: <name>...`` is a signature, not an empty section."""
        text = "## Sanity Check\n\nSigned by: M. S., RN, CEN, TCRN. August 19, 2026\n"
        names = [section.name for section in scan.read_sections(text)[0]]
        self.assertNotIn(scan.SIGNED_BY, names)

    def test_a_label_section_closes_a_heading_section(self):
        """The nesting bug the stack had, pinned in the direction it silently passed.

        ``### Review of Systems`` followed by ``**Physical Examination:**`` put the
        examination *inside* the Review of Systems, so the exam's closer satisfied
        the ROS's row and ``ros-no-closer`` reported zero on a draft carrying no
        closer at all. Found by review; every section this reads is a peer.
        """
        text = (
            "## Sanity Check\n\nModule 1 - confirmed\n\n"
            "### Review of Systems\n\nGeneral: + fatigue.\n\n"
            "**Physical Examination:**\n\n"
            "General: Alert. All other systems reviewed and are negative.\n"
        )
        found = sorted(kinds(text))
        self.assertIn(scan.ROS_NO_CLOSER, found)
        self.assertIn(scan.EXAM_CLAIMS_UNEXAMINED, found)

    def test_a_heading_section_closes_a_label_section(self):
        """The same rule in the other direction, which the stack also got wrong."""
        text = (
            "## Sanity Check\n\nModule 1 - confirmed\n\n"
            "**Review of Systems:**\n\nGeneral: + fatigue.\n\n"
            "### Physical Examination\n\n"
            "General: Alert. All other systems reviewed and are negative.\n"
        )
        self.assertIn(scan.ROS_NO_CLOSER, kinds(text))

    def test_no_block_belongs_to_two_sections(self):
        """At most one recognized section is open, so a line is graded once."""
        text = (
            "## Review of Systems\n\nGeneral: + fatigue.\n\n"
            "## Physical Examination\n\nGeneral: Alert.\n"
        )
        sections = scan.read_sections(text)[0]
        seen = [block.line for section in sections for block in section.blocks]
        self.assertEqual(len(seen), len(set(seen)))


if __name__ == "__main__":
    unittest.main()
