"""Cover ``tools/block_scan.py`` against synthetic tier blocks.

Built in this file and a temp directory, on ``test_specificity_scan.py``'s
reasoning: **there is no committed `clinical-note` run** whose tier block this
could be tested against, and there will not be one -- a run directory is a
patient record.

Two shapes are pinned deliberately, because the scanner's whole reading rests on
telling them apart: an entry that **opens** with a field name, and a wrapped line
that merely mentions one. ``day-a`` run 2's notes wrap GAPS prose at the aligned
column, and an earlier draft of the scanner called three such sentences failures.

One class reads ``skills/clinical-note/SKILL.md`` and asserts the rules the
scanner checks are still written there, on ``test_spelling_scan.py``'s reasoning:
a scanner that has drifted from the file a reader opens is worse than none,
because it reads as agreement.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import block_scan

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"

# The label is repeated per entry and prose wraps at the aligned column, which is
# what ``day-a`` run 2 produced.
CLEAN = """\
# Encounter

Subjective ... Objective ... Assessment ... Plan ...

```
DERIVED           BMI 37.1 = 230 lb / (66 in)^2 x 703
FILLED·asserted   Race/Ethnicity - African American/Black (declared rule)
FILLED·asserted   Primary Payment Method - Medicaid (declared rule)
FILLED·asserted   Non-smoker
FILLED·proposed   Urinalysis with culture
FLAG              BP 141/93 undiscussed
GAPS              Marital status
GAPS              Site and preceptor. Not in the source. The site also decides
                  the payment method above.
UNKNOWN           (none)
```
"""

MARITAL = "GAPS              Marital status"
RACE_ENTRY = "FILLED·asserted   Race/Ethnicity - African American/Black (declared rule)\n"

# The field opens its own GAPS entry: what each row actually bans.
PAYMENT_UNDER_GAPS = CLEAN.replace(
    MARITAL, MARITAL + "\nGAPS              Primary Payment Method"
)
TIMES_UNDER_GAPS = CLEAN.replace(MARITAL, "GAPS              Start/End estimated")
RACE_MISSING = CLEAN.replace(RACE_ENTRY, "")
RACE_UNDER_GAPS = RACE_MISSING.replace(
    MARITAL, MARITAL + "\nGAPS              Race/Ethnicity"
)

NO_BLOCK = "# Encounter\n\nSubjective ... Plan ...\n"


def write_run(notes: dict[str, str]) -> tempfile.TemporaryDirectory:
    """A throwaway run directory holding ``notes``, filename -> text."""
    handle = tempfile.TemporaryDirectory()
    for name, text in notes.items():
        (Path(handle.name) / name).write_text(text, encoding="utf-8")
    return handle


def rows(scan: block_scan.Scan) -> list[str]:
    return sorted(f.row for f in scan.findings)


class TheFixturesInThisFileAreWhatTheySay(unittest.TestCase):
    """Each constant is built by string surgery on ``CLEAN``; a typo in one would
    silently produce a fixture that tests nothing. Pin them once."""

    def test_the_edits_landed(self) -> None:
        self.assertIn("Race/Ethnicity", CLEAN)
        self.assertNotIn("Race/Ethnicity", RACE_MISSING)
        self.assertIn("Race/Ethnicity", RACE_UNDER_GAPS)
        self.assertIn("Primary Payment Method", RACE_MISSING)
        self.assertNotIn("Marital status", TIMES_UNDER_GAPS)
        for altered in (PAYMENT_UNDER_GAPS, TIMES_UNDER_GAPS, RACE_MISSING):
            self.assertNotEqual(CLEAN, altered)


class TheParserReadsTheBlock(unittest.TestCase):
    def test_every_label_is_found(self) -> None:
        block = block_scan.read_block(CLEAN)
        self.assertEqual(
            set(block),
            {
                "DERIVED",
                "FILLED·asserted",
                "FILLED·proposed",
                "FLAG",
                "GAPS",
                "UNKNOWN",
            },
        )

    def test_a_repeated_label_accumulates(self) -> None:
        block = block_scan.read_block(CLEAN)
        self.assertEqual(len(block["FILLED·asserted"]), 3)
        self.assertEqual(len(block["GAPS"]), 2)

    def test_an_indented_line_wraps_the_entry_above_it(self) -> None:
        block = block_scan.read_block(CLEAN)
        site = block["GAPS"][1]
        self.assertEqual(site.wraps, ("the payment method above.",))
        self.assertIn("decides the payment method above.", site.text)

    def test_a_bullet_opens_a_new_entry(self) -> None:
        text = CLEAN.replace(MARITAL, "GAPS\n  - Marital status\n  - Occupation")
        block = block_scan.read_block(text)
        self.assertEqual([e.head for e in block["GAPS"]][:3], ["", "Marital status", "Occupation"])

    def test_a_hyphen_separator_reads_as_the_middle_dot(self) -> None:
        block = block_scan.read_block(CLEAN.replace("·", "-"))
        self.assertIn("FILLED·asserted", block)
        self.assertIn("FILLED·proposed", block)

    def test_a_bolded_label_reads(self) -> None:
        block = block_scan.read_block(CLEAN.replace("GAPS  ", "**GAPS**  "))
        self.assertIn("Marital status", [e.head for e in block["GAPS"]])

    def test_unindented_prose_does_not_join_the_last_section(self) -> None:
        text = CLEAN + "\nPrimary Payment Method was filled from the declared rule.\n"
        block = block_scan.read_block(text)
        self.assertEqual([e.head for e in block["UNKNOWN"]], ["(none)"])

    def test_a_note_with_no_block_reads_as_none(self) -> None:
        self.assertEqual(block_scan.read_block(NO_BLOCK), {})

    def test_prose_opening_with_a_label_word_is_not_a_label(self) -> None:
        """The label match is case-sensitive, and that is load-bearing.

        An earlier version carried ``re.IGNORECASE``, so these sentences each
        opened a section. Any note containing one then read as carrying a block,
        and the exit-2 limb could not fire on a run this parser cannot read.
        """
        for line in (
            "Unknown whether the patient smokes.",
            "Gaps in the history remain.",
            "- Derived from the height and weight above.",
            "Flag this for the preceptor.",
        ):
            with self.subTest(line=line):
                self.assertEqual(block_scan.read_block(line + "\n"), {})

    def test_a_note_of_pure_prose_still_exits_two(self) -> None:
        prose = (
            "# Encounter\n\nUnknown whether the patient smokes.\n"
            "Gaps in the history remain.\n"
        )
        with write_run({"case-01.md": prose, "case-02.md": prose}) as run:
            self.assertEqual(block_scan.main([run]), 2)

    def test_the_filled_suffix_may_be_any_case(self) -> None:
        for suffix in ("asserted", "ASSERTED", "Asserted"):
            with self.subTest(suffix=suffix):
                block = block_scan.read_block(f"FILLED·{suffix}   Race/Ethnicity - x\n")
                self.assertIn("FILLED·asserted", block)


class TheThreeRowsFireOnWhatOpensAnEntry(unittest.TestCase):
    def test_a_clean_note_fails_nothing(self) -> None:
        scan = block_scan.survey([block_scan.read_block(CLEAN)])
        self.assertEqual(scan.notes_with_block, 1)
        self.assertEqual(scan.failing_notes, 0)
        self.assertEqual(scan.findings, ())

    def test_a_mention_inside_an_entry_is_not_a_failure(self) -> None:
        """``day-a`` run 2's real shape, and the false positive that forced this.

        The entry's subject is the site; the payment method was filled, and the
        sentence explains the dependency.
        """
        scan = block_scan.survey([block_scan.read_block(CLEAN)])
        self.assertEqual(scan.f1_failures, 0)
        self.assertEqual(scan.gaps_wrapped_lines, 1)

    def test_prose_mid_sentence_is_not_even_a_candidate(self) -> None:
        """``the payment method above.`` continues a sentence about the site.

        A candidate is a line that would have *opened* a matching entry, not any
        line the field's name appears on -- otherwise every note explaining the
        declared rule would carry one.
        """
        scan = block_scan.survey([block_scan.read_block(CLEAN)])
        self.assertEqual(scan.candidates, ())

    def test_an_aligned_line_opening_with_the_field_is_a_candidate(self) -> None:
        """The canonical form, where several entries share one label.

        Only the first opens the entry this grades, so the rest are reported and
        not scored -- #127's ambiguity, made visible instead of picked.
        """
        text = CLEAN.replace(
            MARITAL, MARITAL + "\n                  Primary Payment Method"
        )
        scan = block_scan.survey([block_scan.read_block(text)])
        self.assertEqual(scan.f1_failures, 0)
        self.assertEqual([c.row for c in scan.candidates], ["F1"])

    def test_a_candidate_does_not_change_the_exit_status(self) -> None:
        text = CLEAN.replace(
            MARITAL, MARITAL + "\n                  Primary Payment Method"
        )
        with write_run({"case-01.md": text}) as run:
            self.assertEqual(block_scan.main([run]), 0)

    def test_f1_fires_on_payment_opening_an_entry(self) -> None:
        scan = block_scan.survey([block_scan.read_block(PAYMENT_UNDER_GAPS)])
        self.assertEqual(rows(scan), ["F1"])
        self.assertEqual(scan.failing_notes, 1)

    def test_f2_fires_on_start_end_estimated(self) -> None:
        scan = block_scan.survey([block_scan.read_block(TIMES_UNDER_GAPS)])
        self.assertEqual(rows(scan), ["F2"])

    def test_f2_fires_on_start_time_and_on_end_time(self) -> None:
        for opener in ("Start time", "End times", "Visit start/end", "Start and end"):
            text = CLEAN.replace(MARITAL, f"GAPS              {opener} not recorded")
            with self.subTest(opener=opener):
                scan = block_scan.survey([block_scan.read_block(text)])
                self.assertEqual(rows(scan), ["F2"])

    def test_a_shift_start_time_is_a_real_absent_input_and_not_f2(self) -> None:
        """``Shift start time and shift length not supplied`` opens with ``Shift``.

        It is an input the day file genuinely did not carry, not the note's own
        start and end -- which the same entry goes on to say were estimated.
        """
        text = CLEAN.replace(
            MARITAL,
            "GAPS              Shift start time and shift length not supplied, so the\n"
            "                  visit times are estimated from an assumed 07:00 start.",
        )
        scan = block_scan.survey([block_scan.read_block(text)])
        self.assertEqual(scan.f2_failures, 0)

    def test_f3_fires_twice_when_race_is_dropped_and_reported(self) -> None:
        scan = block_scan.survey([block_scan.read_block(RACE_UNDER_GAPS)])
        self.assertEqual(rows(scan), ["F3", "F3"])

    def test_f3_fires_when_race_is_simply_absent(self) -> None:
        """The row has two limbs and only one is about GAPS.

        ``Race/Ethnicity`` is filled from a declared rule, so a block naming it
        nowhere has not passed by omission -- it dropped a field the reference
        file says is always filled.
        """
        scan = block_scan.survey([block_scan.read_block(RACE_MISSING)])
        self.assertEqual(rows(scan), ["F3"])

    def test_race_named_in_a_wrap_under_asserted_satisfies_the_second_limb(self) -> None:
        text = RACE_MISSING.replace(
            "FILLED·asserted   Non-smoker",
            "FILLED·asserted   Non-smoker, and the declared\n                  race/ethnicity rule applied",
        )
        scan = block_scan.survey([block_scan.read_block(text)])
        self.assertEqual(rows(scan), [])

    def test_race_under_another_label_is_not_the_asserted_limb(self) -> None:
        text = RACE_MISSING.replace(
            "UNKNOWN           (none)", "UNKNOWN           Race/Ethnicity token"
        )
        scan = block_scan.survey([block_scan.read_block(text)])
        self.assertEqual(rows(scan), ["F3"])

    def test_a_note_failing_two_rows_counts_once(self) -> None:
        text = TIMES_UNDER_GAPS.replace(
            "GAPS              Start/End estimated",
            "GAPS              Start/End estimated\nGAPS              Primary Payment Method",
        )
        scan = block_scan.survey([block_scan.read_block(text)])
        self.assertEqual(rows(scan), ["F1", "F2"])
        self.assertEqual(scan.failing_notes, 1)

    def test_a_note_with_no_block_is_counted_and_grades_nothing(self) -> None:
        scan = block_scan.survey([block_scan.read_block(NO_BLOCK)])
        self.assertEqual(scan.notes_read, 1)
        self.assertEqual(scan.notes_with_block, 0)
        self.assertEqual(scan.findings, ())


class TheReportCarriesNoNoteText(unittest.TestCase):
    def test_counts_only_by_default(self) -> None:
        scan = block_scan.survey([block_scan.read_block(PAYMENT_UNDER_GAPS)])
        report = block_scan.format_report(scan, source="a-run")
        self.assertNotIn("Medicaid", report)
        self.assertNotIn("African American", report)
        self.assertNotIn("141/93", report)

    def test_show_reveals_the_entry(self) -> None:
        scan = block_scan.survey([block_scan.read_block(PAYMENT_UNDER_GAPS)])
        report = block_scan.format_report(scan, source="a-run", show=True)
        self.assertIn("Primary Payment Method", report)
        self.assertIn("PHI", report)

    def test_the_report_is_plain_ascii(self) -> None:
        """It prints to a Windows console, where a middle dot outside cp1252
        comes back as a question mark -- ``specificity_scan.py``'s reasoning."""
        scan = block_scan.survey([block_scan.read_block(CLEAN)])
        block_scan.format_report(scan, source="a-run").encode("ascii")


class TheExitStatusSaysWhichKindOfNothing(unittest.TestCase):
    def test_clean_run_exits_zero(self) -> None:
        with write_run({"case-01.md": CLEAN, "case-02.md": CLEAN}) as run:
            self.assertEqual(block_scan.main([run]), 0)

    def test_a_violation_exits_one(self) -> None:
        with write_run({"case-01.md": CLEAN, "case-02.md": TIMES_UNDER_GAPS}) as run:
            self.assertEqual(block_scan.main([run]), 1)

    def test_no_argument_exits_two(self) -> None:
        self.assertEqual(block_scan.main([]), 2)

    def test_a_missing_directory_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            self.assertEqual(block_scan.main([str(Path(parent) / "nope")]), 2)

    def test_an_empty_directory_exits_two(self) -> None:
        with write_run({}) as run:
            self.assertEqual(block_scan.main([run]), 2)

    def test_notes_carrying_no_block_at_all_exits_two(self) -> None:
        """Not having scanned, distinguished from having found nothing.

        A run whose tier block was written in a shape the parser does not read
        would otherwise report zero violations and look like a pass.
        """
        with write_run({"case-01.md": NO_BLOCK, "case-02.md": NO_BLOCK}) as run:
            self.assertEqual(block_scan.main([run]), 2)

    def test_a_readme_is_not_a_note(self) -> None:
        with write_run({"README.md": CLEAN, "case-01.md": CLEAN}) as run:
            self.assertEqual(len(block_scan.read_notes(Path(run))), 1)


class TheCommittedNotesReadClean(unittest.TestCase):
    """The one real set this can be pointed at, pinned.

    ``fixtures/filled-anchor/notes`` is a committed set of finished
    ``clinical-note`` output — `day-b` run 1 byte for byte — so unlike a run
    directory it is not a patient record and not going to vanish.
    ``CLAUDE.md``'s *Differential scan* sets the precedent for recording what a
    scanner does against it and pinning the figure with a test.

    **This is the test that would have caught both parser bugs.** Before the
    label match was anchored to the left margin, case 11's wrapped
    ``DERIVED line. Lands in the overweight band`` re-opened a section and
    captured the ``Race/Ethnicity`` line 32 lines below it, so this set scored
    two F3 failures it does not have.
    """

    NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

    def setUp(self) -> None:
        self.blocks = [
            block_scan.read_block(text)
            for text in block_scan.read_notes(self.NOTES)
        ]

    def test_all_twelve_carry_a_readable_block(self) -> None:
        self.assertEqual(len(self.blocks), 12)
        self.assertEqual(sum(1 for b in self.blocks if b), 12)

    def test_the_set_passes_f1_to_f3(self) -> None:
        scan = block_scan.survey(self.blocks)
        self.assertEqual(scan.findings, ())
        self.assertEqual(block_scan.main([str(self.NOTES)]), 0)

    def test_every_note_names_race_under_asserted(self) -> None:
        """The limb the margin bug broke, asserted directly rather than through
        the exit status, so a regression names the right thing."""
        for index, block in enumerate(self.blocks):
            with self.subTest(note=index):
                self.assertTrue(
                    any(
                        block_scan.RACE_ANYWHERE.search(entry.text)
                        for entry in block.get(block_scan.ASSERTED, [])
                    )
                )


class TheSkillStillSaysWhatThisChecks(unittest.TestCase):
    """A scanner that has drifted from the file a reader opens reads as agreement."""

    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")

    def test_the_gaps_exclusions_are_still_written_down(self) -> None:
        self.assertIn("**What never goes under GAPS:**", self.skill)
        self.assertIn("**Start and end times.**", self.skill)
        self.assertIn("Estimated by design", self.skill)

    def test_the_two_declared_rule_fields_are_still_named(self) -> None:
        self.assertIn("`Primary Payment Method`, `Race/Ethnicity`", self.skill)
        self.assertIn("filled from that rule rather than reported missing", self.skill)

    def test_a_declared_administrative_value_still_belongs_to_asserted(self) -> None:
        self.assertIn(
            "A declared administrative value is a claim about the patient, so it "
            "belongs under `FILLED·asserted`",
            self.skill,
        )

    def test_the_block_labels_are_still_the_six_this_parses(self) -> None:
        for label in block_scan.LABELS:
            self.assertIn(label, self.skill)


if __name__ == "__main__":
    unittest.main()
