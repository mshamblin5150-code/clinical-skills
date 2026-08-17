"""Pin the ruling [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94) settled.

**The defect was a box with no legal value.** ``SOAP.md`` writes the slot as
``Allergies (reaction): <allergen - reaction; NKDA if none>``, and where the
shorthand gives an allergen and no reaction three rules bound it shut at once:
the box demands a value, the grounding rule supplies none, and drift row 12 bans
the hedge. **Three independent runs reached for the banned string**, one of them
committed at ``fixtures/filled-anchor/notes/case-07.md``, which writes
``reaction not documented`` six times.

**The clinician ruled on 2026-08-16: the reaction is inferred**, written into the
box so the rubric's own ``Allergies (with reaction)`` heading is satisfied
literally, and declared in the tier block. He was shown the argument against --
that an inferred ``rash`` is exactly the value that makes a cephalosporin look
safe against a penicillin allergy, which is the question he says he asks before
giving rocephin -- and ruled anyway. **What answers that argument is the
never-discharge limb**, not the disclosure: the inferred mildness may not license
a drug.

**The tests below are substrings phrased as the ruling rather than as the
sentence**, on ``test_skill_agreement.py``'s reasoning: a test asserting a
paragraph verbatim fails on every rewrite and teaches the next session to delete
it. What each one holds is a clause that cannot be dropped without reopening the
hole, and one of them holds a **narrowing** rather than an addition --
``SKILL.md``'s *no exam finding, symptom or result will ever pass them* forbade
this ruling as written, so a file carrying both would contradict itself and the
next session would resolve it by guessing.

There is no scanner to keep parity with. This is ``test_spelling_scan.py``'s *the
scanner must not drift from the file a reader opens* with both readers being
Markdown, which is what ``test_skill_agreement.py`` is.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTE_DIR = REPO_ROOT / "skills" / "clinical-note"
SKILL = NOTE_DIR / "SKILL.md"
SOAP = NOTE_DIR / "SOAP.md"
HP = NOTE_DIR / "HP.md"

TIER_WORDS = ("given", "filled", "inferred", "derived", "asserted", "proposed")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class SubstringCase(unittest.TestCase):
    """``assertIn`` on a 60 KB file prints the file. Nobody reads that failure.

    Every check here is *does this document still say this*, so the useful report
    is the clause and the filename -- which is what these two produce. Found by
    running the first version of this file: one failing assertion emitted 700 KB.
    """

    def assertSays(self, path: Path, clause: str) -> None:
        if clause not in read(path):
            self.fail(f"{path.name} no longer says: {clause!r}")

    def assertSaysNothingOf(self, path: Path, clause: str) -> None:
        if clause in read(path):
            self.fail(f"{path.name} still says: {clause!r}")


class TheSkillCarriesTheRuling(SubstringCase):
    """``SKILL.md`` states what the reaction sub-field reads and what bounds it."""

    def test_the_reaction_is_inferred_rather_than_hedged(self) -> None:
        """The box takes a value. That is the whole of what #94 asked."""
        self.assertSays(SKILL, "reaction is inferred")

    def test_the_banned_string_is_still_named_as_banned(self) -> None:
        """#29's ban is narrowed nowhere. The hedge stays illegal in the slot."""
        self.assertSays(SKILL, "reaction not documented")

    def test_the_inferred_reaction_is_declared_in_the_tier_block(self) -> None:
        """Every generated value in this repo is declared. This one is not special."""
        self.assertSays(SKILL, "FILLED·asserted")
        self.assertSays(SKILL, "ALLERGIES levofloxacin reaction")

    def test_it_may_never_discharge_an_obligation(self) -> None:
        """The limb that answers the rocephin case. Dropping it reopens the harm."""
        self.assertSays(SKILL, "may never discharge an obligation")
        self.assertSays(SKILL, "never licenses")

    def test_the_dependency_disclosure_is_floored_at_drug_and_food(self) -> None:
        """The clinician's management test, with a spine two runs cannot differ on."""
        self.assertSays(SKILL, "drug and food")

    def test_the_floor_cites_why_the_code_set_draws_it_there(self) -> None:
        """``Z88`` has no reaction axis; ``Z91.01`` and ``T78.0-`` are chosen by one."""
        self.assertSays(SKILL, "Z88")
        self.assertSays(SKILL, "T78.0")

    def test_the_bright_line_it_narrows_is_named_rather_than_left_standing(self) -> None:
        """*No exam finding ... will ever pass them* forbade this ruling as written.

        A file carrying the old absolute and the new ruling contradicts itself,
        and a single-file reader cannot see it -- both paragraphs read as coherent
        on their own page. That is ``test_skill_agreement.py``'s finding exactly.
        """
        self.assertSaysNothingOf(
            SKILL, "no exam finding, symptom or result will ever pass them."
        )
        self.assertSays(SKILL, "historical")


class TheNoteBodyNeverSaysWhereTheValueCameFrom(SubstringCase):
    """Drift row 12 bans every tier word from the body, and this ruling obeys it.

    The clinician restated it while #94 was being built: *never write inferred
    when I am having you write a note -- you can keep it somewhere for audit but
    never in the note.* The tier block is that somewhere.
    """

    def test_row_twelve_still_bans_the_tier_words(self) -> None:
        for word in TIER_WORDS:
            with self.subTest(word=word):
                self.assertSays(SKILL, f"*{word}*")

    def test_no_template_line_writes_a_tier_word_into_the_box(self) -> None:
        """A worked example putting ``inferred`` in the slot would teach the leak."""
        for path in (SKILL, SOAP, HP):
            for number, line in enumerate(read(path).splitlines(), start=1):
                stripped = line.strip()
                if not stripped.startswith("Allergies"):
                    continue
                for word in TIER_WORDS:
                    with self.subTest(path=path.name, line=number, word=word):
                        self.assertNotRegex(stripped, rf"\b{word}\b")


class BothBranchTemplatesAgree(SubstringCase):
    """One ruling, two templates. #90's whole subject is these drifting apart."""

    def test_both_templates_still_ask_for_a_reaction(self) -> None:
        """The labels are unchanged -- the ruling made the box satisfiable instead."""
        self.assertSays(SOAP, "Allergies (reaction):")
        self.assertSays(HP, "Allergies (with reaction)")

    def test_neither_template_carries_a_conditional_the_other_lacks(self) -> None:
        """A reaction written where supplied on one branch and inferred on the
        other is the same encounter reading two ways, which is what #90 forbids."""
        for path in (SOAP, HP):
            with self.subTest(path=path.name):
                self.assertSays(path, "reaction")
                self.assertSaysNothingOf(path, "reaction where documented")

    def test_each_branch_says_the_slot_is_never_left_short(self) -> None:
        """Neither template restates the rule; both defer, as they already do."""
        for path in (SOAP, HP):
            with self.subTest(path=path.name):
                self.assertSays(path, "SKILL.md")


class DriftRowSeventeenWalksIt(unittest.TestCase):
    """A rule no row walks is a rule no run is graded on."""

    def test_row_seventeen_names_the_inferred_reaction(self) -> None:
        row = [
            line
            for line in read(SKILL).splitlines()
            if line.startswith("| 17 ")
        ]
        self.assertEqual(len(row), 1, "drift row 17 should appear exactly once")
        self.assertIn("reaction", row[0])

    def test_row_seventeen_still_bans_the_hedges_it_always_banned(self) -> None:
        row = next(
            line for line in read(SKILL).splitlines() if line.startswith("| 17 ")
        )
        for banned in ("not documented", "not reported this visit", "status unknown"):
            with self.subTest(banned=banned):
                self.assertIn(banned, row)


class TheGapsListIsUnchanged(SubstringCase):
    """The clinician chose the FILLED-only option over the one that added GAPS.

    So ``SKILL.md``'s standing *an allergy slot never earns a GAPS line* survives
    this ticket rather than being carved into, and a run writing the missing
    reaction as a gap has not found a gap -- it has failed to fill a box.
    """

    def test_an_allergy_slot_still_never_earns_a_gaps_line(self) -> None:
        self.assertSays(
            SKILL, "Any social or allergy slot the branch template enumerates"
        )


class TheFixturesStillPoseTheQuestion(unittest.TestCase):
    """The eight inputs the ruling has to be right about, re-derived not cited.

    #143 is one figure copied into many files going stale; this counts instead.
    A fixture edit that changes the population fails here rather than quietly
    voiding the ruling's scope.
    """

    def test_no_committed_input_pairs_an_allergen_with_a_reaction(self) -> None:
        """The claim the whole ticket rests on, checked over every input."""
        clauses = []
        for path in sorted(REPO_ROOT.glob("fixtures/*/shorthand/case-*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if re.search(r"\ballerg", line, re.IGNORECASE):
                    clauses.append((path.name, line))
        self.assertGreaterEqual(len(clauses), 18, "the population should not shrink")
        for name, line in clauses:
            with self.subTest(case=name):
                self.assertNotRegex(
                    line,
                    r"allerg\w*[^.]*\b(rash|hives|urticaria|anaphylaxis|swelling)\b",
                    "a shorthand naming a reaction would change this ticket's premise",
                )


if __name__ == "__main__":
    unittest.main()
