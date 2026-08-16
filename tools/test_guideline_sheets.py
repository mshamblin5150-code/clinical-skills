"""Pin [#85]'s ruling, and pin the skill's examples to the sheets they cite.

**Drift row 24 has no scanner**, for the reason the row itself gives: the limb
that matters is whether a correctly extracted recommendation applies to the
patient, and that is a clinical judgment. So the first half of this file is
``test_differential_shape.py``'s check -- *assert the rule is still written where
a reader will find it* -- because a rule with no runnable test is one a tidy can
delete without failing anything.

**The second half is the part that is not a tautology, and it is the reason this
file exists rather than a few more cases in that one.** ``skills/clinical-note``
now teaches the citation format by worked example: a colorectal row graded ``A``
for ``adults 50 to 75``, a hypertension row at ``>=140 mm Hg`` for ``adults-htn``,
a population key that expands to a PREVENT risk, a catalog that answers a grep for
``chronic obstructive`` and does not answer one for ``zoster``. **Every one of
those is a fact about a committed artifact, and every one of them can go stale
without the skill file changing a character** -- a corpus refresh, a second
threshold sheet, a regraded recommendation. So they are re-derived here against
the artifacts rather than restated, which is #94 and #96's lesson applied before
the figure has had a chance to drift rather than after.

That is also why the counts below are not written as literals in two places. The
skill says *90 of 90* and *one topic*; this file reads the sheets and checks that
the skill is still telling the truth, so a second threshold sheet fails a test
instead of quietly making a sentence false.

**Nothing here reads a note or a run directory.** It reads committed Markdown
only, so it needs no fixtures, touches nothing under ``scratch/`` or ``output/``,
and can print anything it finds.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTE_SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
CODE_SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"
USPSTF = REPO_ROOT / "reference" / "guidelines-uspstf.md"
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
THRESHOLDS = REPO_ROOT / "reference" / "thresholds"


def _row(text: str, number: int) -> str:
    """The drift matrix row numbered ``number``, as one line.

    Returns ``""`` rather than raising when the row is gone, so a deleted row
    reads as a failed assertion naming the row rather than an error in every
    test that touches it. Copied from ``test_differential_shape.py`` deliberately
    -- the two files are pinning different rows and neither should be able to
    break the other by refactoring a helper.
    """
    prefix = f"| {number} | "
    return next((line for line in text.splitlines() if line.startswith(prefix)), "")


def _section(text: str, heading: str) -> str:
    """The body under ``heading``, up to the next heading of the same level."""
    level = heading.split(" ", 1)[0]
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return ""
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith(level + " ") and not line.startswith(level + "#"):
            break
        body.append(line)
    return "\n".join(body)


class TheSkillCarriesTheObligation(unittest.TestCase):
    """The ruling, in the file a generating pass opens."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")

    def test_the_section_exists(self):
        self.assertIn("\n## Guideline sheets\n", self.text)

    def test_the_obligation_fires_on_the_sheet_and_not_the_subject(self):
        # The scope boundary. Without it the rule reads as "check a guideline",
        # which is an obligation to consult a corpus that does not travel.
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("consulted rather than recalled", section)
        self.assertIn("The obligation fires on the sheet, not on the subject", section)

    def test_an_item_with_no_number_is_outside_the_rule(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("no number in it", section)

    def test_the_two_silences_are_kept_apart(self):
        # The single load-bearing distinction in the section. Collapsing it lets
        # a threshold sheet's silence read as "no guideline applies", which is
        # false and unfalsifiable from the note.
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("The two silences are not the same silence", self.text)
        self.assertIn("sheet does not settle it", section)
        self.assertIn("never `no guideline applies`", section)

    def test_the_citation_is_block_only(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("Block only. It never appears in the note body", section)

    def test_the_tail_sits_on_the_item_line_and_says_what_that_costs(self):
        # The shape, and the #70 caveat that comes with it. A run that reads the
        # rule without the caveat will wrap a long citation and believe it complied.
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("The tail stays on the item's line however long", section)
        self.assertIn("countable, not reliably countable", section)

    def test_the_worked_examples_keep_the_tail_on_one_line(self):
        # The examples are the rule for most readers, and an example that wrapped
        # would teach the defect the paragraph beside it forbids.
        section = _section(self.text, "## Guideline sheets")
        tails = [
            line for line in section.splitlines() if line.lstrip().startswith("FILLED·proposed")
        ]
        self.assertTrue(tails, "the section lost its worked examples")
        for line in tails:
            self.assertRegex(line, r"\[[^\[\]]+\]", f"citation not on the item line: {line}")

    def test_the_population_is_not_optional_and_says_why(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("The population is the field that is not optional", section)
        self.assertIn("nine-item age-keyed screening list", section)

    def test_a_filled_population_key_is_marked_never_withheld(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("A filled population key is marked, never withheld", section)

    def test_an_unestablished_population_condition_takes_needs(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("needs:", section)
        self.assertIn("10-year risk not calculated", section)

    def test_no_input_to_a_risk_score_is_ever_filled(self):
        # The half of the calculate-it ruling that keeps it inside standing rule
        # 2. Without it, "compute where you have the data" invents a lipid panel.
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("No input to a risk score is ever filled", section)
        self.assertIn("verify this number", section)

    def test_the_calculator_follows_the_cited_row(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("Name the calculator the cited row keys on", section)

    def test_naming_a_catalog_document_is_gated_on_a_literal_match(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("only on a literal match", section)
        self.assertIn("It fails closed", section)

    def test_applicability_is_stated_as_out_of_reach(self):
        section = _section(self.text, "## Guideline sheets")
        self.assertIn("not machine-checkable", section)


class TheTierBlockKeepsCitedItemsUnderFilled(unittest.TestCase):
    """No fourth tier, and the reason -- which is what the rule rests on."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")

    def test_the_block_still_lists_exactly_the_six_lines(self):
        # A fourth tier would show up here first. #85 decided against one, and a
        # later run adding CITED to this block is the change to catch.
        #
        # Read from the fenced template alone, never from the section, and that
        # is the whole reason this helper exists: the prose below the fence names
        # `FILLED·cited` in order to rule it out, so a section-wide search finds
        # the rejected tier in the sentence rejecting it. Mention against use
        # again -- the same trap `block_scan.py` documents for a GAPS entry whose
        # subject is the rule.
        block = _section(self.text, "### 6. Emit the tier block")
        fenced = re.search(r"```\n(.*?)```", block, re.S)
        self.assertIsNotNone(fenced, "the tier block template is gone")
        template = fenced.group(1)
        labels = [line.split()[0] for line in template.splitlines() if line.strip()]
        self.assertEqual(
            labels,
            ["DERIVED", "FILLED·asserted", "FILLED·proposed", "FLAG", "GAPS", "UNKNOWN"],
        )

    def test_a_citation_rides_on_the_item_and_does_not_move_it(self):
        block = _section(self.text, "### 6. Emit the tier block")
        self.assertIn("does not move it", block)
        self.assertIn("There is no fourth tier", block)

    def test_the_reason_a_cited_item_stays_under_filled_is_recorded(self):
        # Not decoration: the whole argument against a fourth tier is that it
        # would lift cited items out of the block the clinician confirms.
        block = _section(self.text, "### 6. Emit the tier block")
        self.assertIn("a cited item stays under FILLED", block)


class TheDriftMatrixCarriesRow24(unittest.TestCase):
    """Row 24, and the append convention that put it at the bottom."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")

    def test_row_24_exists_and_is_named_guideline_backing(self):
        self.assertIn("| 24 | **Guideline backing** |", self.text)

    def test_row_24_names_all_three_verdicts(self):
        row = _row(self.text, 24)
        self.assertIn("no USPSTF row", row)
        self.assertIn("sheet does not settle it", row)
        self.assertIn("recalled, no shipped sheet", row)

    def test_row_24_requires_the_population(self):
        row = _row(self.text, 24)
        self.assertIn("**population**", row)

    def test_row_24_bars_the_note_body(self):
        row = _row(self.text, 24)
        self.assertIn("No citation appears in the note body", row)

    def test_row_24_exempts_an_item_carrying_no_number(self):
        row = _row(self.text, 24)
        self.assertIn("carrying no number never fails this row", row)

    def test_the_append_convention_was_followed(self):
        self.assertIn("**Row 24 is appended for the reason row 23 was", self.text)

    def test_row_24_is_distinguished_from_row_21(self):
        # Both read the FILLED·proposed list. Row 21 counts landings; this one
        # asks where the number came from, and case 10 passed 21 while failing 24.
        self.assertIn("it is not row 21 widened", self.text)

    def test_the_absence_of_a_scanner_is_stated(self):
        self.assertIn("Nothing checks this row", self.text)


class TheSkillsExamplesStillMatchTheSheets(unittest.TestCase):
    """The half that is not a tautology: every cited example, re-derived."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")
        cls.uspstf = USPSTF.read_text(encoding="utf-8")
        cls.catalog = CATALOG.read_text(encoding="utf-8")

    def test_both_sheets_the_skill_names_are_on_disk(self):
        self.assertTrue(USPSTF.is_file())
        self.assertTrue(THRESHOLDS.is_dir())
        self.assertTrue((THRESHOLDS / "hypertension.md").is_file())

    def test_uspstf_is_still_complete_for_its_corpus(self):
        # The skill says 90 of 90, and the whole "no USPSTF row means something"
        # ruling rests on it. If a refresh makes it 90 of 94, the ruling changes.
        self.assertIn("90 of 90", self.text)
        self.assertIn("90 of 90", self.uspstf)

    def test_the_thresholds_directory_still_holds_one_topic(self):
        # The skill says "one topic". A second sheet is good news and makes that
        # sentence false, so it fails here rather than going stale in the file.
        sheets = sorted(p.name for p in THRESHOLDS.glob("*.md") if p.name != "README.md")
        self.assertEqual(sheets, ["hypertension.md"])
        self.assertIn("**one topic**", self.text)

    def test_the_colorectal_example_is_a_real_uspstf_row(self):
        self.assertIn("[uspstf: grade A, adults 50 to 75, 2021]", self.text)
        self.assertRegex(
            self.uspstf,
            r"\| Screening for Colorectal Cancer \| all adults aged 50 to 75 years \| A \|",
        )
        self.assertIn("| 2021 |", self.uspstf)

    def test_the_hypertension_example_is_a_real_threshold_row(self):
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        self.assertIn(
            "[thresholds/hypertension: aha-2025 Class 1, adults-htn, SBP >=140]", self.text
        )
        self.assertRegex(
            sheet,
            r"\| bp-treatment-threshold-sbp \| adults-htn \| >=140 mm Hg \|.*\| aha-2025 \|.*\| 1 \|",
        )

    def test_the_population_key_the_skill_expands_is_declared_as_written(self):
        # The skill quotes adults-htn-lowrisk's verbatim to show that a key hides
        # its own definition. A regraded population would make the quote wrong.
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        verbatim = "adults with hypertension, no clinical CVD, 10-year PREVENT risk <7.5%"
        self.assertIn(f"| adults-htn-lowrisk | {verbatim} |", sheet)
        self.assertIn(verbatim, self.text)

    def test_the_two_calculators_the_skill_contrasts_are_both_real(self):
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        self.assertIn("PREVENT", sheet)
        self.assertIn("estimated 10-year CVD risk of 10% or greater", self.uspstf)

    def test_the_statin_population_the_skill_quotes_is_the_sheets_own(self):
        self.assertIn("adults 40 to 75 with 1+ risk factor and 10-year CVD risk 10%+", self.text)
        self.assertIn("adults aged 40 to 75 years who have 1 or more CVD risk factors", self.uspstf)

    def test_the_catalog_greps_the_skill_promises_still_behave(self):
        # Both directions are load-bearing: the COPD example only works because
        # the grep hits, and the zoster example only works because it does not.
        self.assertIn("chronic obstructive", self.catalog.lower())
        self.assertNotIn("zoster", self.catalog.lower())
        self.assertIn("catalog lists GOLD 2026", self.text)
        self.assertIn("GOLD", self.catalog)

    def test_the_scoped_out_figure_is_the_sheets_own(self):
        # "50 of hypertension's 103" -- both halves re-derived, because a resheet
        # moves them and the skill's argument about the second silence rests on it.
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        coverage = _section(sheet, "## Coverage")
        scoped_out = [line for line in coverage.splitlines() if line.startswith("- `")]
        self.assertEqual(len(scoped_out), 50)
        self.assertIn("**103 numbered", sheet)
        self.assertIn("50 of hypertension's 103", self.text)

    def test_the_no_number_reason_the_skill_cites_is_in_the_coverage_list(self):
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        coverage = _section(sheet, "## Coverage")
        self.assertIn("single-pill combination recommended", coverage)
        self.assertIn("shared decision-making principle", coverage)

    def test_the_not_read_limb_the_skill_leans_on_is_still_there(self):
        # The third meaning of a missing row. Without a Not read: limb in the
        # sheet, the skill's three-way silence collapses to two.
        sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")
        scope = _section(sheet, "## Scope")
        self.assertIn("**Not read:**", scope)
        self.assertIn("the narrative sections", scope)
        self.assertIn("the narrative sections, the evidence tables", self.text)

    def test_the_ungated_majority_figure_is_the_readmes_own(self):
        readme = (THRESHOLDS / "README.md").read_text(encoding="utf-8")
        self.assertIn("138", readme)
        self.assertIn("138 of the 179 documents cannot be omission-gated", self.text)


class TheCoderGainsNoObligation(unittest.TestCase):
    """icd10-cpt: the reason was corrected and the ruling was not."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CODE_SKILL.read_text(encoding="utf-8")

    def test_the_false_justification_is_gone(self):
        # It read "no guidelines ship here" in two places and two sheets ship.
        #
        # Asserted against the *use* rather than the string, because the first
        # version of this test asserted the string and failed on the replacement
        # paragraph quoting the old wording in order to retire it. That is
        # standing rule 4's mention-versus-use distinction and `spelling_scan`'s
        # rule, arriving in a test that was written the same week as both.
        self.assertNotIn("for the same reason: no guidelines ship here", self.text)
        self.assertNotIn("and for the same reason: no guidelines", self.text)

    def test_the_outpatient_rule_names_what_does_ship_and_why_it_misses(self):
        self.assertIn("CMS and NCHS document", self.text)
        self.assertIn("no CMS or NCHS coding document is among the nine societies", self.text)

    def test_the_mdm_paragraph_names_the_ama_gap(self):
        self.assertIn("**AMA CPT** document", self.text)
        self.assertIn("no AMA document is among the nine societies", self.text)

    def test_the_greppable_anchors_the_ticket_relies_on_survive(self):
        # #85 recorded four line-number stalings and settled on these two strings
        # as the durable citation. An edit that reworded them would break every
        # reference in the ticket's comment history.
        self.assertIn(
            "**The MDM phrasing here is recalled, and nothing in this repo verifies it**",
            self.text,
        )
        self.assertIn("**That is recalled, and nothing in this repo verifies it**", self.text)

    def test_no_lookup_was_added_and_the_reason_is_the_anchor_rule(self):
        self.assertIn("No lookup is added to this skill", self.text)
        self.assertIn("anchor rule running backwards", self.text)


class TheIndexTellsAConsumerWhatToInstall(unittest.TestCase):
    """AGENTS.md is what a consumer reads, and the answer is still nothing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = AGENTS.read_text(encoding="utf-8")

    def test_the_sheets_are_named_in_the_index(self):
        self.assertIn("reference/guidelines-uspstf.md", self.text)
        self.assertIn("reference/thresholds/", self.text)

    def test_the_index_says_no_tool_is_needed(self):
        # The distinction AGENTS.md already draws for icd10-cpt's database: this
        # dependency is Markdown, so nothing installs and nothing is run.
        self.assertIn("they need no tool at all", self.text)
        self.assertIn("Markdown in this repo", self.text)

    def test_the_index_keeps_the_two_silences_apart(self):
        self.assertIn("silences do not mean the same thing", self.text)


if __name__ == "__main__":
    unittest.main()
