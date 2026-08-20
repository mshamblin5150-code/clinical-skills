"""Pin [#70]'s ruling to the three files a generating pass actually opens.

**This is the one rule in ``clinical-note``'s differential that has no scanner,
and the ruling is why.** The count runs to every diagnosis-shaped line in the
Assessment rather than stopping at the ``Differential:`` heading, so locating an
entry means telling a diagnosis from a line of reasoning under a heading a run
invented -- a reader's judgment. A scanner reading the labeled block would be
checking the **narrow** reading the clinician rejected, and would report clean on
exactly the note that moved an uncoded diagnosis one heading down. ``#164`` holds
what a partial one could still be worth.

So the check available here is ``test_spelling_scan.py``'s, and it is the same
check ``test_block_scan.py`` and ``test_differential_scan.py`` make against their
own rows: **assert the rule is still written where a reader will find it.** A rule
with no runnable test is one a tidy can delete without failing anything, and #70
exists because two undefined terms survived in a row for months.

Three files, because the ruling binds both branches and the fixture row is the
other half of what #70 asked for:

- ``skills/clinical-note/SKILL.md`` -- the rule, drift rows 13 and 23.
- ``skills/clinical-note/SOAP.md`` and ``HP.md`` -- the rendering, which differs.
- ``fixtures/day-b/assertions.md`` -- C1, the row the ticket was filed against.

**Nothing here reads a note.** It reads committed Markdown only, so it needs no
fixtures, touches no run directory and can print anything it finds.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
SOAP = REPO_ROOT / "skills" / "clinical-note" / "SOAP.md"
HP = REPO_ROOT / "skills" / "clinical-note" / "HP.md"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"


def _row(text: str, number: int) -> str:
    """The drift matrix row numbered ``number``, as one line.

    Returns ``""`` rather than raising when the row is gone, so a deleted row
    reads as a **failed assertion naming the row** instead of a ``StopIteration``
    error in every test that touches it. A test that errors says the suite is
    broken; a test that fails says the rule is.
    """
    prefix = f"| {number} | "
    return next((line for line in text.splitlines() if line.startswith(prefix)), "")


class TheSkillCarriesTheShapeRule(unittest.TestCase):
    """The rule itself, in the file that binds both branches."""

    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_the_section_exists(self):
        self.assertIn("### The shape of the differential", self.text)

    def test_the_list_is_numbered_and_ranked(self):
        # Both halves. "Ordered by priority" without the numerals was the live
        # alternative and was ruled against -- a ranking nobody can see is one
        # that was not made.
        self.assertIn(
            "The differential is a numbered list, ranked most likely first",
            self.text,
        )

    def test_the_favored_entry_is_number_one(self):
        self.assertIn("`1.` is the favored entry", self.text)

    def test_the_unit_is_the_item_and_not_the_line(self):
        # The two branches render an item differently -- one line on SOAP, two on
        # the H&P -- so a rule stated in lines would forbid the H&P's own shape.
        self.assertIn("One entry per numbered item", self.text)
        self.assertIn("the item is the unit rather than the line", self.text)

    def test_a_wrapped_line_does_not_open_an_item(self):
        # #124's finding: mandating a form moves the ambiguity down to what a
        # line is rather than deleting it. Four wrapped entries published a wrong
        # figure, so the mandate arrives with this sentence attached.
        self.assertIn(
            "A wrapped line belongs to the item that opened it and never opens one",
            self.text,
        )

    def test_prose_is_a_defect_rather_than_an_entry(self):
        self.assertIn(
            "A diagnosis argued down inside a paragraph is a defect, not an entry",
            self.text,
        )

    def test_the_boundary_is_wide(self):
        # The narrow reading -- count the labeled block only -- is escapable by
        # moving a line one heading down, which is why it lost.
        self.assertIn(
            "A diagnosis-shaped line anywhere in the Assessment is an entry"
            " and carries a code",
            self.text,
        )

    def test_a_body_measurement_is_a_diagnosis_and_reasoning_is_not(self):
        self.assertIn(
            "A **measurement of the patient's own body is a diagnosis for this rule**",
            self.text,
        )
        self.assertIn("A **line of reasoning is not**", self.text)

    def test_the_conflict_line_still_satisfies_row_11(self):
        # Without this the ruling reads as licensing a dropped conflict, which is
        # row 11's whole subject.
        self.assertIn("That is not an escape from drift row 11", self.text)

    def test_the_ruling_is_dated_and_attributed(self):
        self.assertIn("The clinician ruled all four of these on 2026-08-16", self.text)

    def test_the_form_is_required_rather_than_permitted(self):
        self.assertIn(
            "The `Name - CODE: rationale` form stopped being permitted"
            " and started being required",
            self.text,
        )

    def test_the_section_says_no_tool_checks_it(self):
        # If this goes, a later pass writes a scanner over the labeled block and
        # a clean run starts reading as a walked row -- on the narrow reading the
        # clinician rejected.
        self.assertIn("**So these rows are counted by a reader**", self.text)


class TheDriftMatrixCarriesBothRows(unittest.TestCase):
    """Row 13 gained the definition; row 23 makes the unit countable."""

    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_row_13_defines_an_entry(self):
        row = _row(self.text, 13)
        self.assertIn("An entry is one numbered item", row)

    def test_row_13_states_the_wide_boundary(self):
        row = _row(self.text, 13)
        self.assertIn("not bounded by the `Differential:` heading", row)

    def test_row_13_carves_out_reasoning_and_keeps_measurements(self):
        row = _row(self.text, 13)
        self.assertIn("measurement of the patient's own body is a diagnosis", row)
        self.assertIn("a line of reasoning is not", row.lower())

    def test_row_23_exists_and_is_named_ranking(self):
        self.assertIn("| 23 | **Ranking** |", self.text)

    def test_row_23_states_the_numbering_and_the_order(self):
        row = _row(self.text, 23)
        self.assertIn("numbered list ordered most likely first", row)
        self.assertIn("`1.` is the favored entry", row)

    def test_row_23_fails_a_prose_differential(self):
        row = _row(self.text, 23)
        self.assertIn("argued down inside a paragraph", row)
        self.assertIn("fails this row", row)

    def test_row_23_states_the_wrap_rule(self):
        row = _row(self.text, 23)
        self.assertIn("wrapped line belongs to the item that opened it", row)

    def test_row_23_mandates_the_hyphen_pin(self):
        # The half a numeral does not carry, and #70's fourth bullet. Without it
        # `1. COVID-19 (U07.1): ...` clears both rows while pinning nothing --
        # which is the form question the ticket asked, left half-answered.
        row = _row(self.text, 23)
        self.assertIn("the form is required rather than permitted", row)
        self.assertIn("`Name - CODE: rationale`", row)
        self.assertIn("a code in parentheses or pinned with a colon fails this row", row)

    def test_row_23_exempts_the_conclusion_line(self):
        # Row 22 reads a conclusion by position, so a colon there is already
        # governed. Two rows disagreeing about one line is worse than either.
        row = _row(self.text, 23)
        self.assertIn("The conclusion line is exempt and row 22 says why", row)

    def test_a_row_23_failure_leaves_row_13_ungraded(self):
        # The ordering when both are walked. Without it a run can report a clean
        # row 13 over a denominator it chose itself, which is #70's own defect
        # surviving the fix.
        self.assertIn(
            "a run that fails row 23 has not been graded on row 13", self.text.lower()
        )

    def test_the_append_convention_was_followed(self):
        # Rows 1 through 22 are cited by number across this file, four fixture
        # sets and ADR 0001. Inserting row 23 at its natural neighbor -- row 13 --
        # would silently redirect every one of them.
        self.assertIn("**Row 23 is appended for the reason rows 14 through 22 were.", self.text)

    def test_no_row_was_renumbered(self):
        # The cheap guard on the convention: 25 rows, numbered 1 to 25 in order.
        # Scoped to rows whose second cell is a bolded test name, which is the
        # drift matrix's own shape -- an unrelated numbered table added to this
        # file later must not fail this test for a reason that is not about it.
        #
        # The upper bound is hardcoded on purpose and an append is meant to edit
        # it. A contiguity-only check would pass an insert-at-13-and-renumber,
        # which is the exact move "append, never insert" exists to refuse, and
        # which silently redirects every citation of rows 14 and up across four
        # fixture sets and ADR 0001. Read 23 until #85 added row 24; #132 appended
        # row 25.
        numbers = [
            int(m) for m in re.findall(r"^\| (\d+) \| \*\*[^*]+\*\* \|", self.text, re.M)
        ]
        self.assertEqual(numbers, list(range(1, 26)))


class BothTemplatesRenderTheRule(unittest.TestCase):
    """The rule binds both branches; only the rendering differs.

    Checked separately from the rule itself because a generating pass reads a
    template and may never open ``SKILL.md`` -- which is how the differential
    came to be written five ways over three runs in the first place.
    """

    def test_the_soap_template_numbers_its_differential(self):
        text = SOAP.read_text(encoding="utf-8")
        self.assertIn("1. <Diagnosis - CODE: the findings that support it. Favored.>", text)

    def test_the_soap_notes_state_the_rule_and_point_at_the_skill(self):
        text = SOAP.read_text(encoding="utf-8")
        self.assertIn(
            "It is a numbered list, ranked most likely first, and one entry per line",
            text,
        )
        self.assertIn("*The shape of the differential*", text)

    def test_the_soap_notes_state_the_wide_boundary(self):
        text = SOAP.read_text(encoding="utf-8")
        self.assertIn(
            "The `Differential:` heading is where the list starts"
            " and not where the count stops",
            text,
        )

    def test_the_hp_template_numbers_its_differential(self):
        text = HP.read_text(encoding="utf-8")
        self.assertIn("1. <diagnosis - code>", text)

    def test_the_hp_notes_say_the_item_is_two_lines_on_that_branch(self):
        # The one place the branches genuinely differ. A rule stated as "one line
        # per entry" would forbid the shape the school's rubric asks for.
        text = HP.read_text(encoding="utf-8")
        self.assertIn("the numbered item is two lines", text)

    def test_the_hp_notes_do_not_claim_a_rubric_departure(self):
        # Numbering is the rubric's own "3 differential diagnoses" read plainly.
        # If this ever becomes a departure it needs naming the way the
        # `Final diagnosis` heading's does, not asserting in passing.
        text = HP.read_text(encoding="utf-8")
        self.assertIn(
            "numbering them is its own instruction read plainly,"
            " not a departure from it",
            text,
        )

    def test_both_templates_cite_the_ticket(self):
        for path in (SOAP, HP):
            self.assertIn("issues/70", path.read_text(encoding="utf-8"))


class TheFixtureRowSaysWhatItCounts(unittest.TestCase):
    """C1 is the row #70 was filed against, and the other half of the ask.

    *"Whatever is decided here has to be stated in ``SOAP.md`` as well as in the
    row, or the next run picks its own reading again."*
    """

    def setUp(self):
        self.text = DAY_B.read_text(encoding="utf-8")
        self.row = next(
            line for line in self.text.splitlines() if line.startswith("| C1 |")
        )

    def test_c1_defines_an_entry(self):
        self.assertIn("An entry is one numbered item", self.row)

    def test_c1_states_the_wide_boundary(self):
        self.assertIn("rather than stopping at the `Differential:` heading", self.row)

    def test_c1_keeps_its_two_counts(self):
        # The row's binary character is what #70 said was undermined, not what it
        # asked to remove.
        self.assertIn("Two counts that either match or do not", self.row)

    def test_c1_says_a_prose_differential_leaves_it_ungraded(self):
        self.assertIn(
            "A differential written as prose fails drift row 23"
            " and leaves this row ungraded",
            self.row,
        )

    def test_c1_names_the_row_it_cites_as_a_rule_not_a_verdict(self):
        # ADR 0001 rejects the skill's self-reported drift verdicts as fixture
        # signal. C1 cites row 23's *rule*, and this paragraph is what stops the
        # citation being read as the other thing.
        self.assertIn(
            "that is a reference to the rule rather than to a verdict", self.text
        )

    def test_neither_recorded_digit_is_restated(self):
        # #70 put re-running day-b and re-scoring either run out of scope. This
        # sentence is what stops a later pass reading the new definition as
        # license to move a recorded score.
        self.assertIn(
            "Neither run's `CODING` digit is restated here", self.text
        )

    def test_the_ruling_is_recorded_with_its_date(self):
        self.assertIn("The clinician ruled on 2026-08-16", self.text)


if __name__ == "__main__":
    unittest.main()
