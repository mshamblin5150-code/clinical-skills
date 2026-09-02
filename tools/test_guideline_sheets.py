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
the artifacts rather than restated, which is [#143]'s lesson applied before the
figure has had a chance to drift rather than after.

**That citation read #94 and #96 when this file was written, and those are
allergy-slot rulings.** [#165] is the ticket for exactly that miscitation, it was
closed by removing the wrong number from three places in ``CLAUDE.md``, and this
file was authored in a worktree holding the pre-fix copy -- so the wrong citation
is the one the new file copied, which is the outcome #165 predicted in as many
words. Caught in the tracker sweep for #85.

That is also why every count the skill states is re-derived here rather than
pinned as a literal on both sides. **This docstring claimed that before it was
true**: the first version checked *90 of 90* and the original topic-count claim and left *143* and
*179* -- the two figures that appear in three files each -- asserted nowhere,
which is [#143]'s shape appearing in the very file written to prevent it. Caught
in review. Every figure the new prose states is now counted from the artifact, so
a corpus refresh or a second threshold sheet fails a test instead of quietly
making a sentence false.

**The omission-gate distribution is different.** It is a historical measurement
over the out-of-repo corpus, so its dated values and derivation provenance live
only in the threshold README. The skill states the decision-bearing distinction
between refusal, warning, and no gate without copying those values. The test below
checks both sides of that ownership boundary; it does not call the historical
measurement mechanically verified.

**Nothing here reads a note or a run directory.** It reads committed Markdown
only, so it needs no fixtures, touches nothing under ``scratch/`` or ``output/``,
and can print anything it finds.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from prose_bind import ProseBind
import threshold_coverage
import threshold_sheet

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTE_SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
CODE_SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"
USPSTF = REPO_ROOT / "reference" / "guidelines-uspstf.md"
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
THRESHOLDS = REPO_ROOT / "reference" / "thresholds"
COVERAGE = THRESHOLDS / "coverage.md"


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
    """The body under ``heading``, up to the next heading of the same level **or shallower**.

    The *or shallower* is the whole correctness of this helper and the first
    version did not have it. It stopped only at an equal-level heading, so
    ``_section(text, "### 6. Emit the tier block")`` ran past ``## Conventions``
    and every ``##`` after it, terminating by luck on the ``### 7`` that happens
    to follow. Move section 6 to the end of its parent and the helper would have
    returned the rest of the file -- an over-read that makes every ``assertIn``
    below it pass for the wrong reason, which is the failure mode a test helper
    can least afford.

    A fenced code block can contain a ``#`` comment at column zero, so fences are
    tracked and a heading inside one never closes the section.
    """
    depth = len(heading) - len(heading.lstrip("#"))
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return ""
    body: list[str] = []
    fenced = False
    for line in lines[start + 1 :]:
        if line.startswith("```"):
            fenced = not fenced
        if not fenced:
            stripped = line.lstrip("#")
            hashes = len(line) - len(stripped)
            if 0 < hashes <= depth and stripped.startswith(" "):
                break
        body.append(line)
    return "\n".join(body)


class TheSkillCarriesTheObligation(ProseBind, unittest.TestCase):
    """The ruling, in the file a generating pass opens."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")
        cls.section = _section(cls.text, "## Guideline sheets")

    def test_the_section_exists(self):
        self.assertIn("\n## Guideline sheets\n", self.text)
        self.assertTrue(self.section.strip(), "the section is empty")

    def test_the_obligation_fires_on_the_subject_not_on_a_stated_number(self):
        # The scope boundary, and the one the first draft got wrong: it gated the
        # obligation on the item stating a number, which is the option the
        # clinician rejected because it lets a line escape by being vague.
        self.assertIn("consulted rather than recalled", self.section)
        self.assertIn(
            "The obligation fires on the item's subject, never on whether the item states a number",
            self.section,
        )
        self.assertIn("rests on a **population or a threshold**", self.section)

    def test_the_rejected_number_gate_is_recorded_as_rejected(self):
        # Kept because the rule reads reasonable either way, so the next reader
        # needs the ruling rather than the wording alone.
        self.assertIn("was the live alternative and it was rejected", self.section)
        self.assertIn("escape by being vague", self.section)

    def test_an_item_resting_on_neither_is_outside_the_rule(self):
        self.assertIn("An item resting on neither is outside this rule entirely", self.section)

    def test_the_two_silences_are_kept_apart(self):
        # The single load-bearing distinction in the section. Collapsing it lets
        # a threshold sheet's silence read as "no guideline applies", which is
        # false and unfalsifiable from the note.
        self.assertIn("The two silences are not the same silence", self.text)
        self.assertIn("sheet does not settle it", self.section)
        self.assertIn("never `no guideline applies`", self.section)

    def test_a_complete_null_sheet_eliminates_only_the_unread_meaning(self):
        self.assertProseIn(
            "A sheet whose `## Scope` reports nothing unread has eliminated meaning 3; "
            "it has not turned either remaining meaning into a note-body verdict.",
            self.section,
        )

    def test_no_uspstf_row_is_not_a_clinical_verdict(self):
        # The reading that would do harm: a true fact about a sheet, sitting on
        # an entirely appropriate item. Zoster is the worked case.
        self.assertIn("It never says the item is not indicated", self.section)

    def test_the_citation_is_block_only(self):
        self.assertIn("Block only. It never appears in the note body", self.section)

    def test_the_tail_sits_on_the_item_line_and_says_what_that_costs(self):
        # The shape, and the #70 caveat that comes with it. A run that reads the
        # rule without the caveat will wrap a long citation and believe it complied.
        self.assertIn("The tail stays on the item's line however long", self.section)
        self.assertIn("countable, not reliably countable", self.section)

    def test_the_same_line_rule_is_scoped_to_the_tail(self):
        # Without this the DERIVED example below it reads as breaking the rule
        # stated above it, which is how a reader concludes the rule is decorative.
        self.assertIn("The rule is about **the tail**", self.section)

    def test_the_worked_examples_keep_the_tail_on_one_line(self):
        # The examples are the rule for most readers, and an example that wrapped
        # would teach the defect the paragraph beside it forbids.
        tails = [
            line for line in self.section.splitlines() if line.lstrip().startswith("FILLED·proposed")
        ]
        self.assertGreaterEqual(len(tails), 4, "the section lost its worked examples")
        for line in tails:
            # The tail closes the line, or is followed only by one of the two
            # clauses that are part of the same tail: `needs:` for a population
            # condition the encounter never established, `verify this number`
            # for one this repo cannot evaluate, or `age month filled` when the
            # committed CDC calculator used the deterministic midpoint month.
            # Nothing else may follow it -- a free-text remark after the bracket
            # is how the format erodes.
            self.assertRegex(
                line,
                r"\[[^\[\]]+\](?: (?:needs: .+|verify this number|age month filled))?$",
                f"citation not closing the item line: {line}",
            )

    def test_every_verdict_the_row_names_has_a_worked_example(self):
        # Row 24 names four outcomes. A verdict with no rendering beside it is
        # the sentiment-rather-than-shape failure #85's own comment warns about.
        self.assertIn("[uspstf: grade A", self.section)
        self.assertIn("[thresholds/hypertension: aha-2025 Class 1", self.section)
        self.assertIn("[uspstf: no row]", self.section)
        self.assertIn("[recalled, no shipped sheet; catalog lists GOLD 2026]", self.section)

    def test_the_population_is_not_optional_and_says_why(self):
        self.assertIn("The population is the field that is not optional", self.section)
        self.assertIn("fill the wrong age", self.section)
        self.assertIn("owed to a different patient population", self.section)

    def test_the_population_cell_is_copied_with_its_provenance_and_presence_limit(self):
        # The USPSTF column can come from either the statement or the document's
        # declared field. That provenance makes "quote the population" less safe
        # than it sounds even though every committed row is present.
        self.assertIn("taken from the sheet's own cell", self.section)
        self.assertIn("document's declared `POPULATION` field", self.section)
        self.assertIn("Every committed population cell is present", self.section)
        self.assertNotIn("population not stated", self.section)

    def test_a_filled_population_key_is_marked_never_withheld(self):
        self.assertIn("A filled population key is marked, never withheld", self.section)

    def test_an_unestablished_population_condition_takes_needs(self):
        self.assertIn("needs:", self.section)
        self.assertIn("10-year risk not calculated", self.section)

    def test_nothing_is_filled_in_order_to_complete_a_score(self):
        # The half of the calculate-it ruling that keeps it inside standing rule
        # 2. Without it, "compute where you have the data" invents a lipid panel.
        #
        # This read "No input to a risk score is ever filled" and was wrong twice:
        # it barred the ordinary case, and it contradicted the worked example
        # three lines below it, which runs on a filled age and a filled pressure.
        # Both halves are asserted now so a revert fails rather than reads well.
        self.assertIn("Nothing is filled in order to complete a score", self.section)
        self.assertIn("because the equation wanted it", self.section)
        self.assertProseNotIn("No input to a risk score is ever filled**:", self.section)
        self.assertIn("verify this number", self.section)

    def test_a_lipid_value_is_barred_outright(self):
        self.assertIn("A lipid value is barred outright", self.section)
        self.assertIn("is a *result*", self.section)

    def test_a_score_on_a_filled_input_carries_the_mark_into_its_citation(self):
        # The step where the disclosure was most likely to be dropped, because
        # arithmetic reads as provenance-free.
        self.assertIn("carries that up into the citation it keys", self.section)

    def test_the_population_may_be_shortened_and_never_softened(self):
        # The rule read "never paraphrased" while the statin example compresses
        # its cell -- a contradiction between a rule and the example under it,
        # which is the pair a generating pass resolves in the looser direction.
        self.assertIn("It may be shortened; it may never be softened", self.section)
        self.assertIn("Dropping the risk threshold would be softening", self.section)

    def test_a_pediatric_percentile_population_uses_the_cdc_tool(self):
        # #123 closes the hole: the population is now computed from the committed
        # chart, and a midpoint month filled from whole-year age stays disclosed.
        self.assertIn("cdc_percentile.py", self.section)
        self.assertIn("age month filled", self.section)
        self.assertIn("95th percentile for age and sex", self.section)

    def test_the_calculator_follows_the_cited_row(self):
        self.assertIn("Name the calculator the cited row keys on", self.section)

    def test_naming_a_catalog_document_is_gated_on_a_literal_match(self):
        self.assertIn("only on a literal match", self.section)
        self.assertIn("It fails closed", self.section)

    def test_applicability_is_stated_as_out_of_reach(self):
        self.assertIn("not machine-checkable", self.section)


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

    def test_row_24_exempts_an_item_resting_on_neither(self):
        row = _row(self.text, 24)
        self.assertIn("resting on neither a population nor a threshold never fails this row", row)

    def test_row_24_does_not_gate_on_a_stated_number(self):
        # The row and the section have to agree on the trigger, and the first
        # draft had both gating on a number -- the rejected option. A row that
        # drifted back would grade the opposite of what the section teaches.
        row = _row(self.text, 24)
        self.assertIn("never whether it states a number", row)
        self.assertIn("an unnumbered screening line owes this row", row)

    def test_the_append_convention_was_followed(self):
        self.assertIn("**Row 24 is appended for the reason row 23 was", self.text)

    def test_row_24_is_distinguished_from_row_21(self):
        # Both read the FILLED·proposed list. Row 21 counts landings; this one
        # asks where the number came from, and case 10 passed 21 while failing 24.
        self.assertIn("it is not row 21 widened", self.text)

    def test_the_scanner_floor_and_its_ceiling_are_stated(self):
        self.assertIn("supplies row 24's mechanical floor", self.text)
        self.assertIn("missing tails on undecidable items are candidates", self.text)
        self.assertIn("a clean scan is not a walked row 24", self.text)


class TheSkillsExamplesStillMatchTheSheets(ProseBind, unittest.TestCase):
    """The half that is not a tautology: every cited example, re-derived."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = NOTE_SKILL.read_text(encoding="utf-8")
        cls.uspstf = USPSTF.read_text(encoding="utf-8")
        cls.catalog = CATALOG.read_text(encoding="utf-8")
        cls.agents = AGENTS.read_text(encoding="utf-8")
        cls.sheet = (THRESHOLDS / "hypertension.md").read_text(encoding="utf-8")

    def test_the_guideline_artifacts_the_skill_names_are_on_disk(self):
        self.assertTrue(USPSTF.is_file())
        self.assertTrue(THRESHOLDS.is_dir())
        self.assertTrue(COVERAGE.is_file())

    def test_uspstf_is_still_complete_for_its_corpus(self):
        # The skill says 90 of 90, and the whole "no USPSTF row means something"
        # ruling rests on it. If a refresh makes it 90 of 94, the ruling changes.
        #
        # AGENTS.md is checked too and was not in the first version: it is the
        # file a consumer reads, so it is the copy that matters most and was the
        # one copy nothing guarded.
        self.assertIn("90 of 90", self.text)
        self.assertIn("90 of 90", self.uspstf)
        self.assertIn("90 of 90", self.agents)
        uspstf_docs = re.findall(r"^\| USPSTF \| ", self.catalog, re.M)
        self.assertEqual(len(uspstf_docs), 90)

    def test_the_thresholds_directory_is_derived_from_the_coverage_registry(self):
        sheets = sorted(
            p.name
            for p in THRESHOLDS.glob("*.md")
            if p.name not in {"README.md", "coverage.md", "subjects.md"}
        )
        coverage = COVERAGE.read_text(encoding="utf-8")
        registered = sorted(
            cells[3]
            for line in coverage.splitlines()
            if line.startswith("| ")
            and len(cells := [cell.strip() for cell in line.strip("|").split("|")]) == 5
            and cells[2] in threshold_coverage.STATES
            and cells[3]
        )
        self.assertEqual(sheets, registered)
        self.assertIn("thresholds/coverage.md", self.text)
        self.assertIn("thresholds/coverage.md", self.agents)

    def test_every_shipped_source_class_is_derived_from_the_catalog(self):
        source_classes, problems = threshold_sheet.load_catalog_source_classes()
        self.assertEqual(problems, [])
        for path in THRESHOLDS.glob("*.md"):
            if path.name in {"README.md", "coverage.md", "subjects.md"}:
                continue
            parsed = threshold_sheet.parse(path.read_text(encoding="utf-8"), path)
            self.assertTrue(parsed.ok, parsed.why_not)
            for source in parsed.sources.values():
                self.assertEqual(
                    source["source class"], source_classes[source["document"]]
                )

    def test_both_consumers_join_threshold_sheets_on_the_artifact_column(self):
        rule = (
            "A run joins a threshold sheet on the artifact column, "
            "whatever the row's state"
        )
        self.assertProseIn(rule, self.text)
        self.assertProseIn(rule, self.agents)

    def test_the_colorectal_example_is_a_real_uspstf_row(self):
        # One regex over the whole row, never a separate assertIn for the year --
        # "| 2021 |" alone matches any of the 143 rows and would keep passing
        # after a regrade moved this one, which is the shape of check this class
        # exists to avoid making.
        self.assertIn("[uspstf: grade A, adults 50 to 75, 2021]", self.text)
        self.assertRegex(
            self.uspstf,
            r"\| Screening for Colorectal Cancer \| all adults aged 50 to 75 years \| A \|"
            r"[^|]*\| 2021 \|",
        )

    def test_the_row_and_document_counts_are_re_derived_not_restated(self):
        # 143 is quoted in AGENTS.md and 180 in the skill. Neither was pinned
        # in the first version of this file, while its docstring claimed every
        # count was -- so both are counted here, from the artifacts.
        #
        # The catalog's society cell reads `AHA ACC`, with a space: it is the
        # corpus subdirectory name, not the society's own styling, and matching
        # on `AHA/ACC` silently drops every AHA ACC row.
        rows = [
            line
            for line in _section(self.uspstf, "## Recommendations").splitlines()
            if line.startswith("| ") and not line.startswith(("| ---", "| Topic "))
        ]
        self.assertEqual(len(rows), 143)
        societies = re.findall(
            r"^\| (USPSTF|IDSA|AHA ACC|KDIGO|ACIP|ADA|CDC|GINA|GOLD) \| ", self.catalog, re.M
        )
        self.assertEqual(len(societies), 180)
        for figure, where in (("143", self.text), ("180", self.text), ("143", self.agents)):
            self.assertIn(figure, where)

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

    def test_the_scoped_out_figures_are_the_sheets_own(self):
        # "50 of hypertension's 103, 28 of them reading exactly no number".
        #
        # The 28 is here because the first draft said all 50 read `no number`
        # and 28 do; the review that caught it proposed 40, which is also wrong.
        # Two readers, two wrong integers, and the sheet was one awk away -- so
        # the reason is counted rather than characterized from a sample.
        coverage = _section(self.sheet, "## Coverage")
        scoped_out = [line for line in coverage.splitlines() if line.startswith("- `")]
        self.assertEqual(len(scoped_out), 50)
        self.assertEqual(sum(1 for line in scoped_out if line.endswith("no number")), 28)
        self.assertIn("**103 numbered", self.sheet)
        self.assertIn("50 of hypertension's 103", self.text)
        self.assertIn("**28 of them reading exactly `no number`**", self.text)

    def test_the_other_reasons_the_skill_names_are_in_the_coverage_list(self):
        coverage = _section(self.sheet, "## Coverage")
        for reason in (
            "single-pill combination recommended",
            "shared decision-making principle",
            "no numeric trigger",
            "no threshold value",
            "no dose or duration stated",
            "footnote",
        ):
            self.assertIn(reason, coverage, f"the skill names a reason the sheet lost: {reason}")

    def test_uspstf_holds_no_immunization_row_which_is_what_the_zoster_case_rests_on(self):
        # The skill says the sheet holds zero immunization rows and uses that to
        # separate "no USPSTF row" from "not indicated". One new vaccine row
        # would make that paragraph false without touching the skill file.
        rows = _section(self.uspstf, "## Recommendations")
        for word in ("zoster", "immuniz", "vaccin"):
            self.assertNotIn(word, rows.lower())
        self.assertIn("zero** immunization rows", self.text)

    def test_every_committed_population_cell_is_present(self):
        # The skill says the current artifact is complete for presence while
        # refusing to turn that into a claim that each cell is correct.
        cells = [
            line.split("|")[2].strip()
            for line in _section(self.uspstf, "## Recommendations").splitlines()
            if line.startswith("| ") and line.count("|") > 6
        ]
        self.assertEqual(sum(1 for c in cells if c == "not stated"), 0)
        self.assertIn("**Every committed population cell is present**", self.text)
        self.assertIn("does not establish that their content is correct", self.text)

    def test_the_dated_ungated_distribution_lives_only_in_the_readme(self):
        # These are historical measurements over an out-of-repo corpus, not
        # current properties that a committed test can verify. Keep the dated
        # snapshot in its provenance-bearing home and keep exact copies out of
        # the skill that consumes only the distinction between gate outcomes.
        readme = (THRESHOLDS / "README.md").read_text(encoding="utf-8")
        self.assertIn("python tools/guidelines_build.py", readme)
        self.assertRegex(readme, r"On \d{4}-\d{2}-\d{2},")
        self.assertRegex(readme, r"\| nothing found \| — \| \*\*\d+\*\* \| \d+ \|")
        self.assertRegex(
            readme,
            r"\| `bound` \| `text-marker` \| \d+ \| [\d,]+ \|",
        )
        self.assertNotRegex(
            self.text,
            r"\b\d+ of (?:the )?\d+ documents cannot be omission-gated",
        )
        self.assertNotRegex(self.text, r"\ba further \d+ can only be warned about")
        self.assertIn("some documents cannot be omission-gated", self.text)
        self.assertIn("others can only be warned about", self.text)

    def test_the_pediatric_row_the_skill_quotes_is_real(self):
        # Quoted with a grade and a year, both of which were written before they
        # were checked. Pinned so the next edit cannot repeat that.
        self.assertRegex(
            self.uspstf,
            r"\| Interventions for High Body Mass Index in Children and Adolescents \|"
            r" children and adolescents 6 years or older with a high BMI"
            r" \(≥95th percentile for age and sex\)[^|]*\| B \|[^|]*\| 2024 \|",
        )
        self.assertIn("[uspstf: grade B, children and adolescents 6 years or older", self.text)

    def test_the_new_floors_keep_rows_23_and_24s_reader_residue(self):
        # #192 makes their line shapes runnable and must not promote either
        # mechanical floor into a clinical verdict.
        scanner = (REPO_ROOT / "tools" / "differential_scan.py").read_text(encoding="utf-8")
        self.assertIn("Drift row 23's mechanical floor", scanner)
        self.assertIn("Drift row 24's mechanical floor", scanner)
        self.assertIn("clinical likelihood order still needs a reader", self.text)
        self.assertIn("a clean scan is not a walked row 24", self.text)


class TheCoderGainsNoObligation(ProseBind, unittest.TestCase):
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
        self.assertProseNotIn("for the same reason: no guidelines ship here", self.text)
        self.assertProseNotIn("and for the same reason: no guidelines", self.text)

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
