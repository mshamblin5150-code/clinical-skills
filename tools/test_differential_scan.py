"""Cover ``differential_scan``'s parser against synthetic notes built in this file.

**There is no committed ``clinical-note`` run to test against.** The one candidate
is ``fixtures/filled-anchor/notes/``, and its differential entries carry **no
ICD-10 code at all** -- twelve notes, zero coded entries, measured 2026-08-15;
they are ``day-b`` run 1 and predate issue #19, which is what put a code on every
entry. So the scanner exits 2 on them, correctly, and they are no use here. The
notes below are built in a temp directory instead, on
``test_specificity_scan.py``'s reasoning and for its reason: a scanner tested only
against a passing run learns nothing about what it does to a failing one.

One test reads ``skills/clinical-note/SKILL.md`` and asserts drift row 22 says
what this scanner checks, on ``test_spelling_scan.py``'s reasoning -- a scanner
that has drifted from the file a reader opens is worse than none, because it reads
as agreement.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import differential_scan as ds

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"

# The compliant one-line SOAP shape: label names the surviving code, refusal in
# the rationale the colon opens.
CLEAN_SOAP = """A:

Differential:
Pain in right leg - M79.604: 4/10 pain over a chronic right leg wound, tib/fib film ordered today to rule out contiguous osteomyelitis, no result. M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it. Less likely.
"""

# ``hedged-dx`` run 1's case 2, verbatim. Compliant under the row as it stood
# before #68 and a violation under row 22 -- see the module docstring on why that
# is the rule being new rather than the run being newly wrong.
SLOT_VIOLATION = """A:

Differential:
Contiguous osteomyelitis of the right tibia or fibula - M86.9 NOT CODED, nothing established it, right tibia and fibula film ordered today with no result; coded as pain in right leg - M79.604. Less likely.
"""

# Two refusals on one entry. This is the shape that breaks a naive parser: the
# refused codes and the slot code are on the same line, so anything that treats
# every code on a ``NOT CODED`` line as refused flags ``R68.83`` and fails the
# skill's own worked example.
TWO_REFUSALS = """A:

Differential:
Chills - R68.83: chills over a chronic infected wound growing a resistant Klebsiella, but afebrile at 97.3, heart rate 77 and respiratory rate 18, so no SIRS criteria are met. CBC and lactate ordered today with no result. A41.9 Sepsis, unspecified organism NOT CODED, the vitals do not support it; R78.81 Bacteremia NOT CODED, no blood culture drawn. Less likely.
"""

# The H&P branch puts the code on its own line and the refusal on the next one, so
# the refused code is never on the entry line at all.
CLEAN_HP = """Differential diagnoses with rationale:
Pain in right leg - M79.604
Less likely because the 4/10 pain sits over a chronic wound and the tib/fib film ordered today has no result. M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it.
"""

HP_SLOT_VIOLATION = """Differential diagnoses with rationale:
Contiguous osteomyelitis of the right tibia - M86.9
Less likely because the film ordered today has no result. M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it.
"""

# ``icd10-cpt`` step 4's own form, where the code follows the mark rather than
# preceding it.
WORKSHEET_FORM = """Differential:
Osteomyelitis, unspecified - M86.9: film ordered, no result. Less likely.

--- NOT CODED, NOTHING ESTABLISHED IT ---
Contiguous osteomyelitis of the right tibia, suspected on a chronic wound
  NOT CODED: M86.9  Osteomyelitis, unspecified
  proposed instead: M79.604  Pain in right leg
"""

# Row 22 exempts the final diagnosis from the naming limb and not from the slot
# limb, so a refused code landing here still fails.
FINAL_DIAGNOSIS_VIOLATION = """A:

Differential:
Shortness of breath - R06.02: diminished lung sounds. J18.9 Pneumonia, unspecified organism NOT CODED, nothing established it. Less likely.

Final diagnosis: Community-acquired pneumonia - J18.9
"""

FINAL_DIAGNOSIS_CLEAN = """A:

Differential:
Cough - R05.9: three weeks of cough. J15.7 Pneumonia due to Mycoplasma pneumoniae NOT CODED, nothing tested for the organism. Less likely.

Final diagnosis: Community-acquired pneumonia, mycoplasma suspected - J18.9
"""


def scan_text(text: str) -> ds.Scan:
    """Survey one note, the way ``main`` surveys a directory of them."""
    return ds.survey([ds.read_note(text)])


class TheParserFindsEntries(unittest.TestCase):
    def test_a_one_line_soap_entry_yields_one_slot(self):
        note = ds.read_note(CLEAN_SOAP)
        self.assertEqual([e.code for e in note.entries], ["M79.604"])

    def test_the_label_is_kept_for_show_and_is_not_graded(self):
        note = ds.read_note(CLEAN_SOAP)
        self.assertEqual(note.entries[0].label, "Pain in right leg")

    def test_a_two_line_hp_entry_yields_one_slot(self):
        note = ds.read_note(CLEAN_HP)
        self.assertEqual([e.code for e in note.entries], ["M79.604"])

    def test_a_rationale_line_is_not_an_entry(self):
        # ``Less likely because ...`` carries a code and no ``label - CODE`` form,
        # so it must not read as a second entry.
        note = ds.read_note(CLEAN_HP)
        self.assertEqual(len(note.entries), 1)

    def test_the_final_diagnosis_line_is_an_entry(self):
        note = ds.read_note(FINAL_DIAGNOSIS_CLEAN)
        self.assertIn("J18.9", [e.code for e in note.entries])

    def test_a_second_pinned_code_on_one_line_is_also_a_slot(self):
        # ``; coded as pain in right leg - M79.604`` is a second pinned label.
        note = ds.read_note(SLOT_VIOLATION)
        self.assertEqual(sorted(e.code for e in note.entries), ["M79.604", "M86.9"])


class TheParserFindsRefusals(unittest.TestCase):
    def test_a_code_before_the_mark_is_refused(self):
        note = ds.read_note(CLEAN_SOAP)
        self.assertEqual(note.refused, {"M86.9"})

    def test_two_marks_on_one_line_refuse_two_codes(self):
        note = ds.read_note(TWO_REFUSALS)
        self.assertEqual(note.refused, {"A41.9", "R78.81"})

    def test_the_slot_code_is_not_swept_up_by_a_mark_later_on_its_line(self):
        # The regression this parser exists to avoid.
        note = ds.read_note(TWO_REFUSALS)
        self.assertNotIn("R68.83", note.refused)

    def test_a_code_after_a_colon_mark_is_refused(self):
        note = ds.read_note(WORKSHEET_FORM)
        self.assertIn("M86.9", note.refused)

    def test_a_note_with_no_mark_refuses_nothing(self):
        note = ds.read_note("Differential:\nAcute bronchitis - J20.9: cough. Favored.\n")
        self.assertEqual(note.refused, set())


class TheSlotTestFires(unittest.TestCase):
    def test_a_clean_soap_note_has_no_findings(self):
        self.assertEqual(scan_text(CLEAN_SOAP).findings, ())

    def test_a_clean_hp_note_has_no_findings(self):
        self.assertEqual(scan_text(CLEAN_HP).findings, ())

    def test_two_refusals_on_one_entry_is_clean(self):
        scan = scan_text(TWO_REFUSALS)
        self.assertEqual(scan.findings, ())
        self.assertEqual(scan.entries, 1)
        self.assertEqual(scan.refused_codes, 2)

    def test_a_refused_code_in_the_slot_is_a_finding(self):
        scan = scan_text(SLOT_VIOLATION)
        self.assertEqual([f.code for f in scan.findings], ["M86.9"])

    def test_the_hp_two_line_form_fails_the_same_way(self):
        self.assertEqual([f.code for f in scan_text(HP_SLOT_VIOLATION).findings], ["M86.9"])

    def test_the_worksheet_form_fails_when_its_code_is_also_in_a_slot(self):
        self.assertEqual([f.code for f in scan_text(WORKSHEET_FORM).findings], ["M86.9"])

    def test_a_final_diagnosis_is_not_exempt_from_the_slot_limb(self):
        self.assertEqual([f.code for f in scan_text(FINAL_DIAGNOSIS_VIOLATION).findings], ["J18.9"])

    def test_a_final_diagnosis_keeping_its_hedge_is_clean(self):
        self.assertEqual(scan_text(FINAL_DIAGNOSIS_CLEAN).findings, ())


class TheReportCountsWithoutRevealing(unittest.TestCase):
    def test_the_default_report_carries_no_label_and_no_code(self):
        report = ds.format_report(scan_text(SLOT_VIOLATION), source="run-1")
        self.assertNotIn("M86.9", report)
        self.assertNotIn("osteomyelitis", report.lower())

    def test_show_carries_the_code_and_the_label(self):
        report = ds.format_report(scan_text(SLOT_VIOLATION), source="run-1", show=True)
        self.assertIn("M86.9", report)
        self.assertIn("Contiguous osteomyelitis", report)

    def test_the_source_named_is_whatever_it_was_given(self):
        # ``main`` passes the directory *name*, never the path -- a run directory's
        # path names the shift and often the site.
        self.assertIn("run-1", ds.format_report(scan_text(CLEAN_SOAP), source="run-1"))

    def test_counts_are_reported_for_a_clean_run(self):
        report = ds.format_report(scan_text(CLEAN_SOAP), source="run-1")
        self.assertIn("notes read", report)
        self.assertIn("differential entries", report)


class TheExitStatusSeparatesNotScanningFromFindingNothing(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, text: str) -> None:
        (self.root / name).write_text(text, encoding="utf-8")

    def test_no_argument_is_two(self):
        self.assertEqual(ds.main([]), 2)

    def test_a_missing_directory_is_two(self):
        self.assertEqual(ds.main([str(self.root / "absent")]), 2)

    def test_a_directory_with_no_notes_is_two(self):
        self.assertEqual(ds.main([str(self.root)]), 2)

    def test_a_directory_whose_notes_hold_no_entry_is_two(self):
        # Not zero. A run whose output landed elsewhere, or whose differential was
        # written in some shape this parser does not read, would otherwise report a
        # clean scan and look like a pass.
        self.write("case-01.md", "S:\n\nPatient reports a cough.\n")
        self.assertEqual(ds.main([str(self.root)]), 2)

    def test_a_clean_run_is_zero(self):
        self.write("case-01.md", CLEAN_SOAP)
        self.write("case-02.md", TWO_REFUSALS)
        self.assertEqual(ds.main([str(self.root)]), 0)

    def test_a_run_with_a_slot_violation_is_one(self):
        self.write("case-01.md", CLEAN_SOAP)
        self.write("case-02.md", SLOT_VIOLATION)
        self.assertEqual(ds.main([str(self.root)]), 1)

    def test_a_readme_is_not_counted_as_a_note(self):
        self.write("README.md", CLEAN_SOAP)
        self.write("case-01.md", CLEAN_SOAP)
        scan = ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)])
        self.assertEqual(scan.notes, 1)


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    """Pin the scanner to the file a reader opens.

    ``test_spelling_scan.py``'s reasoning: a scanner that has drifted from the
    rule it claims to enforce is worse than no scanner, because a clean run reads
    as agreement between two things that no longer agree.
    """

    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_the_matrix_carries_a_row_22(self):
        self.assertIn("| 22 | **Entry name** |", self.text)

    def test_row_22_states_the_slot_limb_this_scanner_checks(self):
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("NOT CODED", row)
        self.assertIn("code slot", row)

    def test_row_22_states_the_collapse_rule(self):
        # Asserted as a phrase rather than as loose words. An earlier version of
        # this test checked only that ``one`` and ``finding`` appeared in the row,
        # which the word ``none`` and the phrase ``documented finding`` satisfy
        # with the collapse rule deleted -- a code review caught it.
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("two refusals resting on one documented finding", row.lower())
        self.assertIn("**one** entry naming both", row)

    def test_row_22_names_all_three_limbs(self):
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        for limb in ("**Naming**", "**Slot**", "**Collapse**"):
            self.assertIn(limb, row)

    def test_row_22_names_both_branches_conclusion_lines(self):
        # The row exempts the conclusion line from the naming limb. It has a
        # different heading on each branch, and naming only SOAP's would fail a
        # compliant H&P for keeping the hedge the rule requires it to keep.
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("Final diagnosis", row)
        self.assertIn("Actual diagnosis/diagnoses", row)

    def test_the_skill_names_this_scanner(self):
        self.assertIn("tools/differential_scan.py", self.text)

    def test_the_skill_says_two_of_the_three_limbs_are_not_mechanical(self):
        # The scanner must not be read as covering row 22. If this sentence goes,
        # a clean scan starts looking like a walked row.
        self.assertIn(
            "The scanner reaches the slot limb and neither of the other two", self.text
        )
        self.assertIn("a clean scan is not a walked row", self.text)


if __name__ == "__main__":
    unittest.main()
