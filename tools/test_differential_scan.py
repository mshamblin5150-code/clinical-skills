"""Cover ``differential_scan``'s parser against synthetic notes built in this file.

**There is no committed ``clinical-note`` run to test against.** The one candidate
is ``fixtures/filled-anchor/notes/``, and **zero of its twelve notes use the
``label - CODE`` slot form** -- measured 2026-08-15 and pinned below by
``TheOnlyCommittedRunHasNothingToScan``, because every limit claimed in the module
docstring rests on it. So the scanner exits 2 there, correctly, and the set is no
use for exercising the slot test.

**Do not restate that as *those notes carry no codes*.** Four of them do: case 7's
differential block carries 13 and case 8's nine, in the form
``**COVID-19 (U07.1) -- FAVORED.**`` with the code in parentheses. Six of the
twelve head no ``Differential`` at all. That heterogeneity is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s subject
and not this file's; what matters here is only that nobody pins a code with a
hyphen. **The wrong generalization was published in ``CLAUDE.md`` first and caught
by a second reader**, which is why the narrow claim is now the tested one.

The notes below are built in a temp directory instead, on
``test_specificity_scan.py``'s reasoning and for its reason: a scanner tested only
against a passing run learns nothing about what it does to a failing one.

One test reads ``skills/clinical-note/SKILL.md`` and asserts drift row 22 says
what this scanner checks, on ``test_spelling_scan.py``'s reasoning -- a scanner
that has drifted from the file a reader opens is worse than none, because it reads
as agreement.
"""

from __future__ import annotations

import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import differential_scan as ds

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"

# The compliant one-line SOAP shape: label names the surviving code, refusal in
# the rationale the colon opens, welded to the code it refuses.
CLEAN_SOAP = """A:

Differential:
Pain in right leg - M79.604: 4/10 pain over a chronic right leg wound, tib/fib film ordered today to rule out contiguous osteomyelitis, no result. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it. Less likely.
"""

# ``hedged-dx`` run 1's case 2, verbatim, and **left in the retired form on
# purpose**. It is a byte-for-byte run record, so welding it here would falsify
# the evidence #68 was settled from. What it demonstrates now is the other half
# of #153: the same note the scanner used to catch reads as *unscanned* under
# route B, because its refusal is written in a form row 22 no longer accepts.
SLOT_VIOLATION = """A:

Differential:
Contiguous osteomyelitis of the right tibia or fibula - M86.9 NOT CODED, nothing established it, right tibia and fibula film ordered today with no result; coded as pain in right leg - M79.604. Less likely.
"""

# The same clinical mistake as ``SLOT_VIOLATION``, rendered in the form row 22
# requires. This is what the scanner grades; the record above is what it reports
# as unread.
WELDED_SLOT_VIOLATION = """A:

Differential:
Contiguous osteomyelitis of the right tibia or fibula - M86.9: right tibia and fibula film ordered today with no result. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it. Less likely.
"""

# Two refusals on one entry. This is the shape that breaks a naive parser: the
# refused codes and the slot code are on the same line, so anything that treats
# every code on a ``NOT CODED`` line as refused flags ``R68.83`` and fails the
# skill's own worked example.
TWO_REFUSALS = """A:

Differential:
Chills - R68.83: chills over a chronic infected wound growing a resistant Klebsiella, but afebrile at 97.3, heart rate 77 and respiratory rate 18, so no SIRS criteria are met. CBC and lactate ordered today with no result. NOT CODED: A41.9 Sepsis, unspecified organism, the vitals do not support it; NOT CODED: R78.81 Bacteremia, no blood culture drawn. Less likely.
"""

# The H&P branch puts the code on its own line and the refusal on the next one, so
# the refused code is never on the entry line at all.
CLEAN_HP = """Differential diagnoses with rationale:
Pain in right leg - M79.604
Less likely because the 4/10 pain sits over a chronic wound and the tib/fib film ordered today has no result. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.
"""

HP_SLOT_VIOLATION = """Differential diagnoses with rationale:
Contiguous osteomyelitis of the right tibia - M86.9
Less likely because the film ordered today has no result. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.
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
Shortness of breath - R06.02: diminished lung sounds. NOT CODED: J18.9 Pneumonia, unspecified organism, nothing established it. Less likely.

Final diagnosis: Community-acquired pneumonia - J18.9
"""

FINAL_DIAGNOSIS_CLEAN = """A:

Differential:
Cough - R05.9: three weeks of cough. NOT CODED: J15.7 Pneumonia due to Mycoplasma pneumoniae, nothing tested for the organism. Less likely.

Final diagnosis: Community-acquired pneumonia, mycoplasma suspected - J18.9
"""


# ---------------------------------------------------------------------------
# #153. The four shapes the retired parser got wrong, each built here so no
# figure rests on a run directory that is about to disappear.
# ---------------------------------------------------------------------------

# The welded form, wrapped mid-rationale. Ordinary Markdown, forbidden by
# nothing. Under the retired parser the refusal vanished and the scan exited 0.
WRAPPED_REFUSAL = """A:

Differential:
Pain in right leg - M79.604: aching after a fall, no deformity, and the film is
pending. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.
"""

# A wrap falling between the mark and its code, which is the one split the
# welded pair cannot prevent by being welded.
WRAPPED_PAIR = """A:

Differential:
Pain in right leg - M79.604: aching after a fall, no deformity. NOT CODED:
M86.9 Osteomyelitis, unspecified, nothing established it.
"""

# A compliant note carrying its own drift-row-22 verdict, which is what every
# note in a run carries. Under the retired parser this sentence refused the
# note's own final diagnosis and exited 1.
VERDICT_PROSE = """A:

Differential:
Pain in right leg - M79.604: aching after a fall. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.

Final diagnosis: Contusion of right lower leg - S80.11XA

| 22 | Entry name | **Pass.** Slot: the only refusal is M86.9, and the slot after the hyphen carries M79.604, never a code marked NOT CODED. |
"""

# ``day-a`` run 2's case 7, reduced. The conclusion pins its code with a colon
# where every sibling line uses a hyphen, so the retired parser missed the slot
# on punctuation alone and reported a clean run over an asserted strep.
COLON_CONCLUSION = """A:

Differential:
Sore throat - R07.0: three days, no exudate.

Final diagnosis: Streptococcal pharyngitis, suspected: J02.0
NOT CODED: J02.0 Streptococcal pharyngitis, no rapid strep resulted.
"""

# The same conclusion written compliantly: the hedge stays, the code beside it
# is one the encounter supports, and the refusal sits on the line beneath.
CLEAN_CONCLUSION = """A:

Differential:
Sore throat - R07.0: three days, no exudate.

Final diagnosis: Streptococcal pharyngitis, suspected - J02.9
NOT CODED: J02.0 Streptococcal pharyngitis, no rapid strep resulted.
"""

# The form row 22 retired. Every note written before #153 uses it, and the
# scanner must report it as unread rather than as nothing refused.
RETIRED_FORM = """A:

Differential:
Pain in right leg - M79.604: aching after a fall. M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it.
"""

# Two refusals joined by a semicolon, which is the collapse rule's rendering and
# the shape that bounds a refusal clause.
WELDED_TWO_REFUSALS = """A:

Differential:
Chills - R68.83: afebrile at 97.3, heart rate 77, respiratory rate 18, so no SIRS criteria are met. NOT CODED: A41.9 Sepsis, unspecified organism, the vitals do not support it; NOT CODED: R78.81 Bacteremia, no blood culture drawn. Less likely.
"""

# A refusal clause must not swallow the entry that follows it on the next line.
# Both entries sit in one paragraph, so a clause running to the end of the
# paragraph would hide ``R06.02`` and miss a violation on it.
ADJACENT_ENTRIES = """A:

Differential:
Chills - R68.83: afebrile. NOT CODED: A41.9 Sepsis, unspecified organism, the vitals do not support it.
Shortness of breath - R06.02: clear lungs. NOT CODED: R06.02 Shortness of breath, nothing established it.
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

    def test_a_numbered_soap_entry_still_yields_one_slot(self):
        # [#70] made the differential a numbered list, so every entry this
        # scanner will meet from now on opens with `1.`, `2.`, `10.`. Nothing in
        # the parser was changed for it and nothing had to be -- but the skill
        # files it reads were rewritten into the numbered form, so a regression
        # here would show up as a real run exiting 2 rather than as a red test.
        note = "Differential:\n1. Acute bronchitis - J20.9: cough three weeks. Favored.\n"
        entries = ds.read_note(note).entries
        self.assertEqual([e.code for e in entries], ["J20.9"])

    def test_a_double_digit_numeral_does_not_read_as_a_code(self):
        # The label runs back to the start of the line, so the numeral is inside
        # it. `10` is not code-shaped -- CODE needs a letter first -- and this
        # pins that rather than trusting it.
        note = "10. Acute bronchitis - J20.9: cough three weeks. Less likely.\n"
        entries = ds.read_note(note).entries
        self.assertEqual([e.code for e in entries], ["J20.9"])

    def test_a_numbered_hp_entry_with_an_indented_rationale_yields_one_slot(self):
        # The H&P's numbered item is two lines. The second is a continuation and
        # must not open an entry of its own -- it carries no pinned pair, so it
        # does not, and that is what this asserts.
        note = (
            "Differential diagnoses with rationale:\n"
            "1. Pain in right leg - M79.604\n"
            "   Less likely because the film ordered today has no result."
            " NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.\n"
        )
        note_read = ds.read_note(note)
        self.assertEqual([e.code for e in note_read.entries], ["M79.604"])
        self.assertEqual(note_read.refused, frozenset({"M86.9"}))

    def test_a_second_pinned_code_on_one_line_is_also_a_slot(self):
        # ``; coded as pain in right leg - M79.604`` is a second pinned label.
        note = ds.read_note(SLOT_VIOLATION)
        self.assertEqual(sorted(e.code for e in note.entries), ["M79.604", "M86.9"])


class TheParserFindsRefusals(unittest.TestCase):
    def test_the_code_welded_to_the_mark_is_refused(self):
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
        self.assertEqual(scan.differential_entries, 1)
        self.assertEqual(scan.refused_codes, 2)

    def test_a_refused_code_in_the_slot_is_a_finding(self):
        scan = scan_text(WELDED_SLOT_VIOLATION)
        self.assertEqual([f.code for f in scan.findings], ["M86.9"])

    def test_the_run_record_of_that_mistake_now_reads_as_unscanned(self):
        # ``hedged-dx`` run 1's case 2 is the note #68 was filed over, and the
        # scanner used to catch it. Under route B its refusal is in the retired
        # form, so it is reported as unread rather than as clean -- one bare mark
        # and no refusal. **The finding is not lost, it is reclassified**: N1 is
        # still failed by that run, and it is now failed by a reader rather than
        # by this tool. Recorded in ``fixtures/hedged-dx/assertions.md``.
        note = ds.read_note(SLOT_VIOLATION)
        self.assertEqual(note.refused, set())
        self.assertEqual(note.unwelded_marks, 1)
        self.assertEqual(scan_text(SLOT_VIOLATION).findings, ())

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
        report = ds.format_report(scan_text(WELDED_SLOT_VIOLATION), source="run-1")
        self.assertNotIn("M86.9", report)
        self.assertNotIn("osteomyelitis", report.lower())

    def test_show_carries_the_code_and_the_label(self):
        report = ds.format_report(scan_text(WELDED_SLOT_VIOLATION), source="run-1", show=True)
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
        self.write("case-02.md", WELDED_SLOT_VIOLATION)
        self.assertEqual(ds.main([str(self.root)]), 1)

    def test_a_readme_is_not_counted_as_a_note(self):
        self.write("README.md", CLEAN_SOAP)
        self.write("case-01.md", CLEAN_SOAP)
        scan = ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)])
        self.assertEqual(scan.notes, 1)


class TheOnlyCommittedRunHasNothingToScan(unittest.TestCase):
    """Pin the measurement the module docstring's limits rest on.

    This is the one place the suite reads a real committed note set, and it reads
    it to assert a **negative** -- that the slot form is absent -- rather than to
    exercise the parser. If someone regenerates these notes in the current skill's
    shape, this test fails and the docstring gets rewritten, which is the point.
    """

    NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

    def test_twelve_notes_are_read(self):
        self.assertEqual(len(ds.read_notes(self.NOTES)), 12)

    def test_no_note_uses_the_slot_form(self):
        scan = ds.survey([ds.read_note(t) for t in ds.read_notes(self.NOTES)])
        self.assertEqual(scan.differential_entries, 0)

    def test_the_scanner_reports_not_having_scanned(self):
        # Exit 2, not 0. A run whose differential the parser cannot locate must
        # not read as a clean one -- this is the limb #137 asks tools to have.
        self.assertEqual(ds.main([str(self.NOTES)]), 2)


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

    def test_row_22_names_the_conclusion_line(self):
        # The row exempts the conclusion line from the naming limb. It used to
        # have a different heading on each branch and the row named both; #153
        # gave the H&P ``Final diagnosis`` too, so there is one heading to name.
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("Final diagnosis", row)
        self.assertIn("both branches", row)

    def test_row_22_says_a_bare_mark_is_not_a_refusal(self):
        # The scanner reads only the welded pair. If the row stops saying so, a
        # note can be written in the retired form while reading as compliant
        # against the file, and the scanner's exit 2 looks like breakage.
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("welded `NOT CODED: <code>`", row)

    def test_row_22_states_the_positional_conclusion_rule(self):
        row = next(line for line in self.text.splitlines() if line.startswith("| 22 |"))
        self.assertIn("whatever pins it", row)

    def test_the_skill_gives_the_welded_form_in_full(self):
        # The form a run has to write, in the file a generating pass reads.
        self.assertIn(
            "`NOT CODED: <code> <official descriptor>, <reason>`", self.text
        )

    def test_the_skill_says_the_retired_form_exits_two(self):
        # Otherwise a run rewritten in good faith reads exit 2 as a broken tool.
        self.assertIn("A run written in the retired form exits 2, not 0", self.text)

    def test_the_skill_names_this_scanner(self):
        self.assertIn("tools/differential_scan.py", self.text)

    def test_the_skill_says_two_of_the_three_limbs_are_not_mechanical(self):
        # The scanner must not be read as covering row 22. If this sentence goes,
        # a clean scan starts looking like a walked row.
        self.assertIn(
            "The scanner reaches the slot limb and neither of the other two", self.text
        )
        self.assertIn("a clean scan is not a walked row", self.text)


class TheWeldedFormIsWhatCountsAsARefusal(unittest.TestCase):
    """#153's first symptom, and the rule that replaced the guess.

    The retired parser paired a mark with *the last code before it on the same
    physical line*. That is a guess, and it failed in both directions. Row 22 now
    gives the refusal a shape -- ``NOT CODED: <code> <descriptor>, <reason>`` --
    so the pairing is a match rather than an inference.
    """

    def test_a_welded_refusal_is_found(self):
        self.assertEqual(ds.read_note(WRAPPED_REFUSAL).refused, {"M86.9"})

    def test_a_wrapped_rationale_no_longer_hides_the_refusal(self):
        # The whole of symptom 1. Under the retired parser this note reported
        # ``codes marked NOT CODED 0`` and exited 0.
        scan = scan_text(WRAPPED_REFUSAL)
        self.assertEqual(scan.refused_codes, 1)
        self.assertEqual(scan.findings, ())

    def test_a_wrap_between_the_mark_and_its_code_is_followed(self):
        # The one split welding cannot prevent, so the clause is allowed to
        # continue onto the next line when its own line yields no code.
        self.assertEqual(ds.read_note(WRAPPED_PAIR).refused, {"M86.9"})

    def test_the_retired_form_is_not_read_as_a_refusal(self):
        self.assertEqual(ds.read_note(RETIRED_FORM).refused, set())

    def test_the_retired_form_is_counted_rather_than_ignored(self):
        # Not silence. A note whose refusals are written in the retired form has
        # not been scanned, and the count is what says so.
        self.assertEqual(ds.read_note(RETIRED_FORM).unwelded_marks, 1)

    def test_a_compliant_note_has_no_unwelded_marks(self):
        self.assertEqual(ds.read_note(WRAPPED_REFUSAL).unwelded_marks, 0)

    def test_two_welded_refusals_joined_by_a_semicolon_are_both_found(self):
        self.assertEqual(ds.read_note(WELDED_TWO_REFUSALS).refused, {"A41.9", "R78.81"})

    def test_the_slot_code_is_not_swept_up_by_a_welded_mark_on_its_line(self):
        # The regression the retired parser's own docstring named, still guarded.
        self.assertNotIn("R68.83", ds.read_note(WELDED_TWO_REFUSALS).refused)

    def test_a_refusal_clause_stops_at_the_end_of_its_line(self):
        # A clause running to the end of the paragraph would swallow the entry
        # on the next line and hide a violation on it.
        scan = scan_text(ADJACENT_ENTRIES)
        self.assertEqual([f.code for f in scan.findings], ["R06.02"])


class ProseAboutTheRuleIsNotAnEntry(unittest.TestCase):
    """#153's second symptom: describing the rule is what broke it.

    Two things fix it and both are needed. The welded form means a sentence
    writing ``NOT CODED`` with no colon is not a refusal, and a Markdown table
    row is skipped outright -- in a note a pipe table is the drift matrix or a
    field block, never a differential entry.
    """

    def test_a_verdict_row_does_not_condemn_the_note_that_carries_it(self):
        self.assertEqual(scan_text(VERDICT_PROSE).findings, ())

    def test_a_verdict_row_is_not_counted_as_a_refusal(self):
        self.assertEqual(scan_text(VERDICT_PROSE).refused_codes, 1)

    def test_a_verdict_row_is_not_counted_as_an_unwelded_mark(self):
        # Otherwise every compliant note in a run reports one, and the count
        # that exists to flag the retired form is noise from the first run.
        self.assertEqual(scan_text(VERDICT_PROSE).unwelded_marks, 0)

    def test_a_table_row_yields_no_entry(self):
        note = ds.read_note("| 22 | Entry name | Pass - M79.604 carries it |\n")
        self.assertEqual(note.entries, ())

    def test_a_backticked_mark_in_a_sentence_is_a_mention(self):
        # ``spelling_scan.py``'s rule, adopted here. A table covers a drift
        # matrix; #153 also asks for **a README sentence**, and this is the limb
        # that reaches it. Without it the verdict sentence stops being a false
        # finding and becomes a false exit 2 -- quieter, not fixed.
        note = ds.read_note(
            "Pain in right leg - M79.604: aching. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.\n"
            "\n"
            "Row 22 passes: the slot carries M79.604 and never a code marked `NOT CODED`.\n"
        )
        self.assertEqual(note.unwelded_marks, 0)
        self.assertEqual(note.refused, {"M86.9"})

    def test_a_note_discussing_the_rule_in_prose_still_exits_zero(self):
        text = (
            "Differential:\n"
            "Pain in right leg - M79.604: aching. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it.\n"
            "\n"
            "Drift row 22 passes. No code marked `NOT CODED` sits in a slot.\n"
        )
        self.assertEqual(scan_text(text).unwelded_marks, 0)

    def test_the_same_sentence_unbackticked_is_reported_rather_than_ignored(self):
        # The mention rule is a span rule, not a licence for the whole file --
        # ``spelling_scan.py``'s reasoning. Prose that writes the mark bare is
        # indistinguishable from a retired-form refusal, and says so.
        note = ds.read_note(
            "Row 22 passes: the slot carries M79.604 and never a code marked NOT CODED.\n"
        )
        self.assertEqual(note.unwelded_marks, 1)

    def test_a_backticked_refusal_is_a_mention_and_not_read(self):
        # The rule cuts both ways, which is what makes it a rule rather than an
        # escape hatch: a refusal quoted inside backticks is prose about one.
        note = ds.read_note(
            "The form is `NOT CODED: M86.9 Osteomyelitis, unspecified`, mark first.\n"
        )
        self.assertEqual(note.refused, set())
        self.assertEqual(note.unwelded_marks, 0)

    def test_the_worksheet_block_heading_is_not_a_bare_mark(self):
        # ``--- NOT CODED, NOTHING ESTABLISHED IT ---`` is ``icd10-cpt`` step 4's
        # block heading. Without the carve-out any worksheet exits 2 on its own
        # scaffolding while every refusal under it is welded and readable.
        note = ds.read_note(WORKSHEET_FORM)
        self.assertEqual(note.unwelded_marks, 0)
        self.assertIn("M86.9", note.refused)


class TheConclusionIsReadByPositionNotPunctuation(unittest.TestCase):
    """#153's third symptom: a colon where the hyphen belongs hid a real slot.

    Inside the conclusion region every code that is not in a refusal clause is
    slot-held, whatever pins it. That is stricter than the hyphen rule and only
    in the one place where an unrefused code is by definition the answer.
    """

    def test_a_colon_pinned_conclusion_code_is_still_a_slot(self):
        self.assertIn("J02.0", [e.code for e in ds.read_note(COLON_CONCLUSION).entries])

    def test_a_colon_pinned_conclusion_asserting_a_refused_code_is_a_finding(self):
        self.assertEqual([f.code for f in scan_text(COLON_CONCLUSION).findings], ["J02.0"])

    def test_the_pin_is_reported_as_malformed(self):
        self.assertEqual(scan_text(COLON_CONCLUSION).malformed_pins, 1)

    def test_a_hyphen_pinned_conclusion_is_not_reported_as_malformed(self):
        self.assertEqual(scan_text(CLEAN_CONCLUSION).malformed_pins, 0)

    def test_a_compliant_conclusion_keeping_its_hedge_is_clean(self):
        self.assertEqual(scan_text(CLEAN_CONCLUSION).findings, ())

    def test_the_refused_code_beneath_the_conclusion_is_not_itself_a_slot(self):
        # ``NOT CODED: J02.0 ...`` on the line under the conclusion sits inside a
        # refusal clause, so that occurrence is a refusal and not an assertion.
        # Only the occurrence pinned to the label counts as the slot.
        scan = scan_text(CLEAN_CONCLUSION)
        self.assertEqual(scan.refused_codes, 1)
        self.assertEqual(scan.conclusion_entries, 1)

    def test_the_hp_conclusion_heading_is_still_read(self):
        # Retired from both templates by #153, and still read: every H&P run
        # written before today opens its conclusion this way, and a scanner that
        # stopped reading them would report exit 2 on a real run.
        note = ds.read_note(
            "Actual diagnosis/diagnoses with ICD-10 codes:\n"
            "Streptococcal pharyngitis, suspected: J02.0\n"
            "NOT CODED: J02.0 Streptococcal pharyngitis, no rapid strep resulted.\n"
        )
        self.assertIn("J02.0", [e.code for e in note.entries if e.conclusion])

    def test_a_conclusion_entry_is_not_counted_as_a_differential_entry(self):
        # The exit-2 limb hangs on the differential count. A run whose
        # differential this parser cannot read must not be rescued into looking
        # scanned by its conclusion line -- that is the whole of #137's ask.
        scan = scan_text(CLEAN_CONCLUSION)
        self.assertEqual(scan.differential_entries, 1)
        self.assertEqual(scan.conclusion_entries, 1)


class TheRetiredFormReadsAsUnscanned(unittest.TestCase):
    """A run written before #153 must not report a clean scan.

    Route B settled that the welded form is the only refusal row 22 reads. The
    consequence is that every existing run refuses nothing as far as this tool is
    concerned, and *nothing refused* is the same output as *row 22 satisfied by
    construction*. The unwelded count is what tells those apart.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, text: str) -> None:
        (self.root / name).write_text(text, encoding="utf-8")

    def test_a_run_in_the_retired_form_is_two(self):
        self.write("case-01.md", RETIRED_FORM)
        self.assertEqual(ds.main([str(self.root)]), 2)

    def test_a_run_that_genuinely_refused_nothing_is_zero(self):
        # No mark of either kind. Row 22 is satisfied by construction here, and
        # this is the case the limb above must not swallow.
        self.write("case-01.md", "Differential:\nAcute bronchitis - J20.9: cough. Favored.\n")
        self.assertEqual(ds.main([str(self.root)]), 0)

    def test_a_run_mixing_the_two_forms_is_also_two(self):
        # **Any** bare mark, not only a run with none welded. The weaker test
        # was written first and a real run refuted it, clearing that guard on a
        # handful of welded refusals while the rest went unread beneath a clean
        # row-22 line. The counts live in ``fixtures/day-a/assertions.md`` and
        # are not repeated here -- they were measured against a run under
        # ``scratch/``, so nothing committed can re-derive them. **This test is
        # what pins the behavior instead**, which is the durable half.
        self.write("case-01.md", WRAPPED_REFUSAL)
        self.write("case-02.md", RETIRED_FORM)
        self.assertEqual(ds.main([str(self.root)]), 2)
        scan = ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)])
        self.assertEqual(scan.unwelded_marks, 1)
        self.assertEqual(scan.refused_codes, 1)

    def test_a_confirmed_violation_outranks_an_incomplete_scan(self):
        # Both conditions hold and a status carries one. A run holding a real
        # row-22 failure *and* a bare mark is definitely not clean, so reporting
        # it as *not scanned* would file the strongest thing known about it under
        # the weakest heading. The unwelded count is printed either way.
        self.write("case-01.md", WELDED_SLOT_VIOLATION)
        self.write("case-02.md", RETIRED_FORM)
        scan = ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)])
        self.assertEqual(scan.unwelded_marks, 1)
        self.assertEqual(len(scan.findings), 1)
        self.assertEqual(ds.main([str(self.root)]), 1)

    def test_the_counts_are_still_printed_before_the_refusal_to_grade(self):
        # Exit 2 is not silence. A reader has to be able to see *how much* went
        # unread, which is the number that says whether the run needs rewriting
        # or one sentence does.
        self.write("case-01.md", RETIRED_FORM)
        report = ds.format_report(
            ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)]), source="run-1"
        )
        self.assertIn("unwelded NOT CODED marks         1", report)


class TheReportCarriesTheNewCounts(unittest.TestCase):
    def test_the_counts_are_named_in_the_report(self):
        report = ds.format_report(scan_text(COLON_CONCLUSION), source="run-1")
        for label in (
            "differential entries",
            "conclusion entries",
            "codes marked NOT CODED",
            "unwelded NOT CODED marks",
            "malformed slot pins",
        ):
            self.assertIn(label, report)

    def test_the_default_report_still_reveals_nothing(self):
        report = ds.format_report(scan_text(COLON_CONCLUSION), source="run-1")
        self.assertNotIn("J02.0", report)
        self.assertNotIn("pharyngitis", report.lower())


class TheCoverageRowSeparatesReadableFromClean(unittest.TestCase):
    """[#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162)'s
    sharper instance, found on the #85 sweep and re-derived before this was built.

    **The exit-2 *no differential entry* limb is evaluated per run, not per note**,
    so a single parsed entry rescues a whole run into a clean exit 0. A recorded
    run does exactly that -- most of its notes contributed nothing to the limb that
    produced the verdict, and nothing in the report said so. That is the
    partial-coverage-reading-as-complete shape the bare-mark limb was already
    widened for, surviving on the entry limb. **The figures are deliberately not
    stated**: they were measured against a directory under ``scratch/``, so nothing
    committed re-derives them, and one such number copied into several files is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

    **Reported, deliberately not graded** -- the clinician's ruling on 2026-08-19.
    Making the limb per-note would exit 2 on a run where one note of twelve carries
    no differential, which is most real runs, and a check that refuses the ordinary
    case is one people learn to work around. So the denominator is printed and the
    status is untouched, which is ``NOT_VALIDATED_AGAINST``'s third row.

    **It prints on the ordinary passing path and not only when short**, which is
    [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
    ruling on ``phi_scan`` and ``spelling_scan`` borrowed whole: a reader who learns
    to read a qualifier reads its absence as a stronger claim.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, text: str) -> None:
        (self.root / name).write_text(text, encoding="utf-8")

    def scan(self):
        return ds.survey([ds.read_note(t) for t in ds.read_notes(self.root)])

    def test_the_count_is_notes_and_not_entries(self):
        """One note carrying several entries is one note, and the other five are five."""
        self.write("case-01.md", TWO_REFUSALS)
        for n in range(2, 7):
            self.write(f"case-0{n}.md", "S:\n\nPatient reports a cough.\n")
        scan = self.scan()
        self.assertEqual(scan.notes, 6)
        self.assertEqual(scan.notes_with_differential, 1)

    def test_the_row_prints_on_a_fully_covered_run(self):
        self.write("case-01.md", CLEAN_SOAP)
        self.write("case-02.md", TWO_REFUSALS)
        report = ds.format_report(self.scan(), source="run-1")
        self.assertIn("notes with a differential entry", report)
        self.assertIn("2 of 2", report)

    def test_a_short_run_says_what_the_verdict_covers(self):
        self.write("case-01.md", CLEAN_SOAP)
        self.write("case-02.md", "S:\n\nPatient reports a cough.\n")
        report = ds.format_report(self.scan(), source="run-1")
        self.assertIn("1 of 2", report)
        self.assertIn("read nothing from their differential", report)

    def test_a_fully_covered_run_carries_no_qualifier(self):
        """The qualifier is a finding about the run, so a covered run must not
        carry one -- a caveat printed unconditionally is one nobody reads."""
        self.write("case-01.md", CLEAN_SOAP)
        report = ds.format_report(self.scan(), source="run-1")
        self.assertNotIn("read nothing from their differential", report)

    def test_the_status_is_unchanged(self):
        """The ruling in one assertion. Five of six notes ungraded is still 0."""
        self.write("case-01.md", CLEAN_SOAP)
        for n in range(2, 7):
            self.write(f"case-0{n}.md", "S:\n\nPatient reports a cough.\n")
        self.assertEqual(ds.main([str(self.root)]), 0)

    def test_a_conclusion_only_note_is_uncovered_and_the_report_says_it_is_graded(self):
        """**The discriminating case, and it is what shaped the wording.**

        A note carrying a ``Final diagnosis`` and no differential entry has its
        conclusion codes read by position and graded, so calling it *ungraded*
        would be false in the direction that matters. It is still uncovered by the
        row, because what went unread is its **differential** -- which is what row
        22 is about and what the exit-2 limb keys on.

        **Measured rather than reasoned**: on a recorded run the two denominators
        genuinely come apart -- most of its notes carry a conclusion and no
        differential -- so the wider count would have reported it as nearly
        covered while its differential went unread. The figures stay under
        ``scratch/`` where they were taken; what is re-derivable is this case, and
        that is why it is built here rather than cited.
        """
        self.write("case-01.md", CLEAN_SOAP)
        self.write(
            "case-02.md",
            "A:\n\nFinal diagnosis: Community-acquired pneumonia - J18.9\n",
        )
        scan = self.scan()
        self.assertEqual(scan.notes, 2)
        self.assertEqual(scan.notes_with_differential, 1)
        self.assertEqual(scan.conclusion_entries, 1)
        report = ds.format_report(scan, source="run-1")
        self.assertIn("1 of 2", report)
        self.assertIn("read nothing from their differential", report)
        self.assertIn("read by position and graded", report)

    def test_the_row_reveals_nothing(self):
        self.write("case-01.md", WELDED_SLOT_VIOLATION)
        report = ds.format_report(self.scan(), source="run-1")
        self.assertNotIn("M86.9", report)
        self.assertNotIn("osteomyelitis", report.lower())


class TheValidationSetsLimitsAreDeclared(unittest.TestCase):
    """[#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162)'s
    option 4, priced as a declared object rather than as a docstring sentence.

    That ticket's own thread re-prices it: #241 ruled a prose sentence insufficient
    because **a prose edit to it fails nothing**, and the two worked examples in the
    tree -- ``docx_write.NOT_APPLIED`` and ``reference_scan.NOT_REACHED`` -- are a
    tuple of ``(key, reason)`` bound by a test asserting the prose and the object
    name the same items in both directions.

    **The bind here is *point, never copy*.** There is no second sheet to compare
    against -- the reader-facing surface is ``CLAUDE.md``'s *Differential scan*
    section -- so what is asserted is that both surfaces name the object and
    restate no row of it, which is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
    discipline made checkable rather than promised.

    **It compares the *reasons* and not only the keys, and that is the whole
    lesson of the round this shipped in.** The first version asserted the key
    strings were absent. ``CLAUDE.md`` then restated the third row's **reason**
    almost word for word, one sentence after promising not to -- invisible to a
    key-only test, and caught by both axes of ``/code-review`` independently. A key
    is the one part of a row nobody would paste; the reason is the part somebody
    would. So the comparison is a sliding window of consecutive words, on
    ``test_run_record_claim.py``'s finding that a copy survives hard-wrapping and a
    line-wise search does not see it.

    **And every row is live**, which is what #241 asks for over a sentence. Each is
    re-derived below rather than stated -- **row 3 against a run built in this
    file, rows 1 and 2 against the committed tree** -- so a limit cannot quietly
    stop being true. That distinction is written out because the first version
    claimed all three ran against the committed tree while row 3 hand-built a
    ``Scan`` and matched a format string.
    """

    CLAUDE = REPO_ROOT / "CLAUDE.md"
    FIXTURES = REPO_ROOT / "fixtures"

    # Long enough that a shared run is a copy rather than a coincidence, short
    # enough to catch a lightly reworded one. The copy this was built after shared
    # far longer runs than this; the window is deliberately tighter than the
    # measurement so a paraphrase does not slip through.
    SHINGLE = 8

    def keys(self):
        return [key for key, _ in ds.NOT_VALIDATED_AGAINST]

    def shingles(self, text: str) -> set[str]:
        """Every window of ``SHINGLE`` consecutive words, whitespace-normalized.

        Markdown emphasis is stripped so that a row's ``**bold**`` and a prose
        copy's plain rendering of the same words are one string -- otherwise the
        formatting a copyist naturally drops is what defeats the check.
        """
        words = re.sub(r"[*_`]", "", text).split()
        return {
            " ".join(words[i : i + self.SHINGLE])
            for i in range(len(words) - self.SHINGLE + 1)
        }

    def copies_in(self, text: str) -> list[str]:
        """Every row this text restates, as ``key: what it shares``.

        **A predicate rather than a run of assertions**, so the mutation check
        below can call it and get an answer. The first version asserted inside a
        ``subTest``, which swallows the failure -- so the check written to prove the
        bind fires could not see it fire.
        """
        normalized = " ".join(text.split())
        prose = self.shingles(normalized)
        found = []
        for key, reason in ds.NOT_VALIDATED_AGAINST:
            if key in normalized:
                found.append(f"{key}: names the key")
            shared = sorted(self.shingles(reason) & prose)
            if shared:
                found.append(f"{key}: {shared[0]!r}")
        return found

    def assert_points_but_does_not_copy(self, text: str, where: str) -> None:
        self.assertIn("NOT_VALIDATED_AGAINST", " ".join(text.split()), where)
        self.assertEqual(self.copies_in(text), [], f"{where} restates a row")

    def test_every_row_carries_a_key_and_a_reason(self):
        for key, reason in ds.NOT_VALIDATED_AGAINST:
            with self.subTest(key=key):
                self.assertTrue(key.strip(), key)
                # Long enough that the shingle comparison above has something to
                # bite on: a reason shorter than one window is uncheckable.
                self.assertGreater(len(reason.split()), self.SHINGLE * 2, key)

    def test_the_keys_are_distinct(self):
        self.assertEqual(len(set(self.keys())), len(self.keys()))

    def test_the_module_docstring_points_at_the_object_and_copies_none_of_it(self):
        """One object, on #241's terms. A docstring restating a row is the second
        copy that ticket exists to refuse."""
        self.assert_points_but_does_not_copy(ds.__doc__ or "", "the module docstring")

    def test_claude_md_points_at_the_object_and_copies_none_of_it(self):
        """The reader-facing surface, and the one that failed this in review."""
        self.assert_points_but_does_not_copy(
            self.CLAUDE.read_text(encoding="utf-8"), "CLAUDE.md"
        )

    def test_the_bind_would_catch_a_copy(self):
        """**Mutation-tested in the file rather than by hand**, because a check
        that cannot fail is what this whole class is about.

        The prose surfaces are clean today, so every assertion above passes over a
        tree in which nothing was copied -- which is indistinguishable from a
        comparison that finds nothing because it is broken. This drives a real row
        through it and asserts it fires.
        """
        for key, reason in ds.NOT_VALIDATED_AGAINST:
            with self.subTest(key=key):
                # Both halves of the bind, driven separately: a surface that pastes
                # the key, and one that paraphrases only the reason. The second is
                # the one a key-only test could not see, and it is the one that
                # actually happened.
                self.assertTrue(self.copies_in(f"see the object. {key}."))
                self.assertTrue(self.copies_in(f"see the object. {reason}"))
        # And it is not simply saying yes to everything.
        self.assertEqual(self.copies_in("see NOT_VALIDATED_AGAINST for the limits."), [])

    def committed_directories(self):
        """Every committed directory this scanner can be pointed at.

        **Both levels of ``fixtures/``**, because a fixture set's own directory
        holds committed ``.md`` beside its ``notes/`` or ``shorthand/`` subdirectory
        and the scanner can be pointed at either. The first version globbed one
        level and its prose claimed every directory, which is a claim wider than the
        walk -- found by review.

        Walked rather than listed, so a run committed later is graded by the rows
        below rather than leaving them asserting something about a tree that has
        moved. ``run-2`` is an ``icd10-cpt`` worksheet set and is included on
        purpose: #162's sharp case is that the one committed artifact written in
        the mandated welded form is the one this tool is pointed away from.
        """
        found = [
            d
            for d in sorted(self.FIXTURES.glob("*")) + sorted(self.FIXTURES.glob("*/*"))
            if d.is_dir() and ds.read_notes(d)
        ]
        self.assertTrue(found, "the instrument is dead: no committed directory was read")
        return found

    def test_no_committed_input_reaches_the_failure_path(self):
        """The first row, and **the honest form of it rather than the vacuous one**.

        The first version asserted ``scan.findings == ()`` over every committed
        directory. That passes, and it passes for the wrong reason: **not one of
        those directories parses a single differential entry**, so ``findings`` is
        empty because nothing was read rather than because nothing violates. A
        check that cannot fail for the reason it names is this repo's own recurring
        shape, and it arrived inside the change whose subject is that shape --
        found by review.

        **What is actually true is stronger and is what is asserted**: a row-22
        violation needs an entry *and* a refusal of the code in it, and **no
        committed directory holds both at once**. So the failure path is
        unreachable there by construction rather than by luck, and the day a
        committed set gains both this goes red and the row is re-examined.

        The liveness guard counts what was **parsed**, not what was read: files
        read is exactly the exit-0/exit-2 distinction this module exists to make,
        and measuring the wrong one is how the first version went quiet.
        """
        self.assertIn("the exit-1 path on committed input", self.keys())
        entries = refusals = 0
        for directory in self.committed_directories():
            notes = [ds.read_note(t) for t in ds.read_notes(directory)]
            here_entries = sum(len(note.entries) for note in notes)
            here_refusals = sum(len(note.refused) for note in notes)
            entries += here_entries
            refusals += here_refusals
            with self.subTest(directory=directory.name):
                self.assertEqual(ds.survey(notes).findings, ())
                self.assertFalse(
                    here_entries and here_refusals,
                    f"{directory.name} now holds both an entry and a refusal, so the"
                    " failure path is reachable on committed input -- re-examine the"
                    " first row of NOT_VALIDATED_AGAINST",
                )
        # Neither half is zero across the walk, so the assertion above is a real
        # partition rather than a statement about an empty set.
        self.assertTrue(entries, "no committed directory parsed an entry")
        self.assertTrue(refusals, "no committed directory parsed a refusal")

    def test_the_two_committed_sets_are_both_refused(self):
        """The second row -- the aggregate the docstring's four limbs never state.

        Each exit 2 is separately correct and separately documented. What none of
        them says is that **together they leave the scanner with no committed
        material it can read at all**, which is #162's finding and the thing a
        reader infers coverage against. The ``notes`` half is re-asserted here
        although ``TheOnlyCommittedRunHasNothingToScan`` already covers it, because
        the row's claim is the **pair**: asserting either alone is the reading that
        let the aggregate go unstated in the first place.
        """
        self.assertIn("the aggregate of the exit-2 limbs", self.keys())
        for name in ("notes", "run-2"):
            with self.subTest(name=name):
                self.assertEqual(
                    ds.main([str(self.FIXTURES / "filled-anchor" / name)]), 2
                )

    def test_partial_coverage_is_reported_and_not_graded(self):
        """The third row, and the clinician's 2026-08-19 ruling in one assertion.

        **Driven through ``main`` rather than through ``format_report``**, which is
        ``CLAUDE.md``'s own recorded finding on #141: *"every test drove
        ``layer_report`` directly so nothing exercised the path that mattered."*
        The first version here hand-built a ``Scan`` and matched a format string,
        so it could not have seen a row that never reached stdout.
        """
        self.assertIn("partial coverage inside a run", self.keys())
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "case-01.md").write_text(CLEAN_SOAP, encoding="utf-8")
            for n in range(2, 7):
                (root / f"case-0{n}.md").write_text(
                    "S:\n\nPatient reports a cough.\n", encoding="utf-8"
                )
            printed = io.StringIO()
            with redirect_stdout(printed):
                status = ds.main([str(root)])
        report = printed.getvalue()
        # Reported: the row and the qualifier are on the page a reader gets.
        self.assertIn("notes with a differential entry  1 of 6", report)
        self.assertIn("read nothing from their differential", report)
        # Not graded: five of six notes ungraded is still a clean exit.
        self.assertEqual(status, 0)


class TheSkillsWorkedExamplesPassTheScanner(unittest.TestCase):
    """[#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162)'s
    fifth option, borrowed from ``research_ledger.py``'s
    ``test_the_worked_example_in_the_skill_passes_the_scanner``.

    **The catch it defends against is precise**: a documented entry shape this
    scanner would refuse teaches the next run to write a note that fails, and every
    substring test in ``TheSkillSaysWhatThisChecks`` would still be green. The thing
    under test is the file a run actually copies from.

    **What it does not reach is the exit-1 path**, and that limit is stated here
    rather than left to be discovered: a worked example is compliant by
    construction, so this exercises the clean path only. It is
    ``NOT_VALIDATED_AGAINST``'s first row that stays open, not this class that
    closes it.
    """

    FILES = ("SKILL.md", "SOAP.md", "HP.md")

    def blocks(self, name: str) -> list[str]:
        """Every fenced block in one skill file, walked line by line.

        Line by line rather than by one regex, on ``test_research_ledger.py``'s
        finding: a non-greedy pattern over the whole file opens on a *closing*
        fence and returns the prose between two code blocks.
        """
        text = (REPO_ROOT / "skills" / "clinical-note" / name).read_text(
            encoding="utf-8"
        )
        blocks: list[str] = []
        current: list[str] | None = None
        for line in text.splitlines():
            if line.startswith("```"):
                if current is None:
                    current = []
                else:
                    blocks.append("\n".join(current) + "\n")
                    current = None
                continue
            if current is not None:
                current.append(line)
        self.assertIsNone(current, f"an unclosed code fence in {name}")
        return blocks

    def readable(self) -> list[tuple[str, str]]:
        """The blocks this scanner reads as a note: an entry, a refusal, or a mark.

        Selected by what the parser finds rather than by a heading, because the
        point is to grade what the scanner sees, and a block it reads as empty
        carries no claim either way.
        """
        found: list[tuple[str, str]] = []
        for name in self.FILES:
            for index, block in enumerate(self.blocks(name)):
                note = ds.read_note(block)
                if note.entries or note.refused or note.unwelded_marks:
                    found.append((f"{name}#{index}", block))
        return found

    def test_the_instrument_is_live(self):
        """A parser finding nothing would pass every row below.

        ``TheInstrumentIsLive``'s reasoning in ``test_build_artifacts_ignored.py``.
        The floors sit well under the measurement on
        [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
        terms -- a worked example added later must not turn the suite red.
        """
        notes = [ds.read_note(block) for _, block in self.readable()]
        self.assertGreaterEqual(len(notes), 8)
        entries = [entry for note in notes for entry in note.entries]
        self.assertGreaterEqual(sum(1 for e in entries if not e.conclusion), 6)
        self.assertGreaterEqual(sum(1 for e in entries if e.conclusion), 3)
        self.assertGreaterEqual(sum(len(note.refused) for note in notes), 3)

    def test_no_worked_example_violates_row_22(self):
        for label, block in self.readable():
            with self.subTest(block=label):
                self.assertEqual(ds.note_findings(ds.read_note(block)), [])

    def test_no_worked_example_writes_a_bare_mark(self):
        """The retired form, which would teach the next run to exit 2.

        The skill's own rule is that a note discussing the mark puts it in
        backticks, so this grades the rule against the file that states it.
        """
        for label, block in self.readable():
            with self.subTest(block=label):
                self.assertEqual(ds.read_note(block).unwelded_marks, 0)

    def test_the_examples_read_as_one_note_are_clean_too(self):
        """Refusals are collected note-wide, so a block clean on its own can
        collide with a slot in another. Cheap to assert, and it is the reading a
        run produces."""
        joined = "\n".join(block for _, block in self.readable())
        self.assertTrue(joined.strip())
        self.assertEqual(ds.note_findings(ds.read_note(joined)), [])


if __name__ == "__main__":
    unittest.main()
