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
        """Every generated value in this repo is declared. This one is not special.

        **Pinned by shape rather than by drug name.** The first version asserted
        the literal ``ALLERGIES levofloxacin reaction`` and broke an hour later
        when the worked example moved off a fixture allergen -- a test pinning
        the example instead of the rule, which is the brittleness this file's own
        docstring forbids. Caught in review.
        """
        self.assertSays(SKILL, "FILLED·asserted")
        self.assertRegex(
            read(SKILL),
            r"ALLERGIES \w+ reaction \w+ filled",
            "SKILL.md no longer shows a tier line declaring an inferred reaction",
        )

    def test_the_ruling_says_no_gaps_entry_is_owed(self) -> None:
        """The half the clinician chose by rejecting the variant that added one.

        Asserting only that the standing *never goes under GAPS* bullet survives
        is not enough -- that bullet's subject is a whole unsupplied slot, so a
        reader is never told the **sub-field** is covered. Found in review.
        """
        self.assertSays(SKILL, "No GAPS entry")

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


class TheWorkedExampleIsNotAFixtureAnswerKey(SubstringCase):
    """[#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147)'s
    shape, caught on this ticket's own first draft.

    ``fixtures/README`` withholds a set's inputs from a generating pass, and
    ``SKILL.md`` is **the one file every generating pass is required to read**.
    The first version of *The reaction beside a given allergen* worked its
    example from a ``day-b`` case's own drug allergen **and its plan drug** --
    the pair ``fixtures/day-b`` R6 grades -- so a run scoring R6 would have read
    the answer to its own row in the instructions. #65's near-miss exactly, one
    ticket later.

    **The example is an allergen no committed input names**, which is the one
    position all three of #147's candidates agree on, so pinning it here decides
    nothing that ticket has open.

    **Two pre-existing mentions are deliberately not covered.** ``SKILL.md``'s
    ``allergic to prednisone`` and ``SOAP.md``'s ``Phenergan DM`` both predate
    this ticket and both name a committed allergen; the first is a **third
    instance #147's own table does not list**. Ruling on them is that ticket's,
    and a test that failed on them would be this ticket deciding it by stealth.
    """

    def worked_example_allergens(self) -> set[str]:
        """Drug tokens inside a committed input's allergy clause."""
        allergens: set[str] = set()
        for path in sorted(REPO_ROOT.glob("fixtures/*/shorthand/case-*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                match = re.search(r"allerg\w*[:\s]+(.*)", line, re.IGNORECASE)
                if not match:
                    continue
                for token in re.split(r"[,;.]", match.group(1)):
                    word = token.strip().lower()
                    if word.isalpha() and len(word) > 4 and word != "seasonal":
                        allergens.add(word)
        return allergens

    def test_the_population_is_readable(self) -> None:
        """A guard that matched nothing would pass for the wrong reason."""
        found = self.worked_example_allergens()
        self.assertGreaterEqual(len(found), 8, f"only parsed {sorted(found)}")

    def test_the_contaminating_pair_appears_in_no_skill_file(self) -> None:
        """The exact pair the first draft used, by name, so it cannot come back."""
        for path in (SKILL, SOAP, HP):
            for token in ("levaquin", "levofloxacin", "bactrim ds"):
                with self.subTest(path=path.name, token=token):
                    if token in read(path).lower():
                        self.fail(
                            f"{path.name} names {token!r} -- that is day-b case 11's "
                            "allergen or its plan drug, and R6 grades that case"
                        )

    def test_every_branch_works_its_example_from_the_same_allergen(self) -> None:
        """One ruling, one example. A second allergen invites a second reading."""
        for path in (SKILL, SOAP, HP):
            with self.subTest(path=path.name):
                self.assertSays(path, "enicillin - rash")


class BothBranchTemplatesAgree(SubstringCase):
    """One ruling, two templates. #90's whole subject is these drifting apart."""

    def test_both_templates_still_ask_for_a_reaction(self) -> None:
        """The labels are unchanged -- the ruling made the box satisfiable instead."""
        self.assertSays(SOAP, "Allergies (reaction):")
        self.assertSays(HP, "Allergies (with reaction)")

    def test_neither_template_carries_a_conditional_the_other_lacks(self) -> None:
        """A reaction written where supplied on one branch and inferred on the
        other is the same encounter reading two ways, which is what #90 forbids.

        The bare ``assertSays(path, "reaction")`` this replaced passed on prose
        gutted to nothing -- both templates carry the word in their heading.
        """
        for path in (SOAP, HP):
            with self.subTest(path=path.name):
                self.assertSays(path, "inferred")
                self.assertSaysNothingOf(path, "reaction where documented")

    def test_each_branch_carries_the_never_discharge_limb_itself(self) -> None:
        """Deferring to SKILL.md is right for the floor and wrong for this.

        A run reading one template must not have to follow a pointer to learn
        that a generated reaction cannot make a drug safe -- #90's *one rule
        stated at two strengths* is the failure, and silence is a strength.
        """
        for path in (SOAP, HP):
            with self.subTest(path=path.name):
                self.assertSays(path, "never licenses a drug")
                self.assertSays(path, "SKILL.md")


class DriftRowSeventeenWalksIt(unittest.TestCase):
    """A rule no row walks is a rule no run is graded on."""

    def drift_row(self, number: int) -> str:
        """The one matrix row numbered ``number``.

        One lookup rather than the two shapes the first version used -- a
        list-comprehension here and a bare ``next()`` there, which is the same
        query written twice and drifted apart by one being unguarded.
        """
        rows = [
            line
            for line in read(SKILL).splitlines()
            if line.startswith(f"| {number} ")
        ]
        self.assertEqual(len(rows), 1, f"drift row {number} should appear once")
        return rows[0]

    def test_row_seventeen_names_the_inferred_reaction(self) -> None:
        row = self.drift_row(17)
        self.assertIn("inferred reaction", row)
        self.assertIn("drug or food", row)

    def test_row_seventeen_carries_the_never_discharge_limb(self) -> None:
        """The safety clause. A row that grades the form and not this one
        would pass a note whose generated reaction licensed a drug."""
        self.assertIn("licenses a drug", self.drift_row(17))

    def test_row_seventeen_still_bans_the_hedges_it_always_banned(self) -> None:
        row = self.drift_row(17)
        for banned in ("not documented", "not reported this visit", "status unknown"):
            with self.subTest(banned=banned):
                self.assertIn(banned, row)

    def test_row_twelve_is_what_keeps_the_marker_out_of_the_note(self) -> None:
        """Scoped to row 12 rather than to the whole file.

        ``TheNoteBodyNeverSaysWhereTheValueCameFrom`` asserts each tier word
        appears *somewhere* in a 60 KB document, which passes on prose that has
        nothing to do with row 12. This reads the row.
        """
        row = self.drift_row(12)
        for word in TIER_WORDS:
            with self.subTest(word=word):
                self.assertIn(f"*{word}*", row)


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
    """The population the ruling has to be right about, **re-derived not cited**.

    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is
    one figure copied into many files and going stale in all of them, and this
    ticket's own scoping figures had done exactly that -- ``31 / 16 / 11 / 5``
    survived in ``fixtures/day-b/assertions.md`` long after every one was wrong.

    **So these are equalities, not floors.** The first version asserted
    ``>= 18`` against prose that says 20, which is a bound matching none of the
    published numbers and would have sat green through the drift it exists to
    catch -- found in review. An exact assertion fails loudly on any fixture
    change, and failing loudly is the point: the right response is to re-derive
    and update the prose, not to widen the test.
    """

    #: Re-derived 2026-08-16. Every one is published in ``SKILL.md`` under
    #: *The reaction beside a given allergen* and in ``day-b/assertions.md``.
    EXPECTED = {"inputs": 37, "allergy_clause": 20, "nkda": 12, "names_allergen": 8}

    #: The 8, split the way the disclosure floor is drawn. No committed input
    #: names a **food** allergen; ``peds-bp`` case 5's lactose intolerance is an
    #: enzyme deficiency rather than an allergy, and whether it reaches the box
    #: at all is #96's question rather than this one's.
    DRUG = {
        "fixtures/day-b/shorthand/case-07.md",
        "fixtures/day-b/shorthand/case-11.md",
        "fixtures/duration-span/shorthand/case-01.md",
        "fixtures/duration-span/shorthand/case-02.md",
    }
    ENVIRONMENTAL = {
        "fixtures/day-a/shorthand/case-06.md",
        "fixtures/day-b/shorthand/case-02.md",
        "fixtures/hedged-dx/shorthand/case-03.md",
        "fixtures/peds-bp/shorthand/case-05.md",
    }

    def census(self) -> dict[str, object]:
        inputs = sorted(REPO_ROOT.glob("fixtures/*/shorthand/case-*.md"))
        clause, nkda, named = [], [], []
        for path in inputs:
            hits = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if re.search(r"allerg|nkda", line, re.IGNORECASE)
            ]
            if not hits:
                continue
            clause.append(path)
            if any(re.search(r"n\.?k\.?d\.?a", h, re.IGNORECASE) for h in hits):
                nkda.append(path)
            for hit in hits:
                if re.search(r"allerg\w*", hit, re.IGNORECASE) and not re.search(
                    r"allerg\w*\s*:?\s*n\.?k\.?d\.?a\s*$", hit.strip(), re.IGNORECASE
                ):
                    named.append(path)
                    break
        return {
            "inputs": len(inputs),
            "allergy_clause": len(clause),
            "nkda": len(nkda),
            "names_allergen": len(named),
            "named_paths": {p.relative_to(REPO_ROOT).as_posix() for p in named},
            "clause_lines": clause,
        }

    def test_the_published_figures_still_hold(self) -> None:
        """Equalities. A fixture edit fails here rather than voiding the prose."""
        counted = self.census()
        for key, expected in self.EXPECTED.items():
            with self.subTest(figure=key):
                self.assertEqual(
                    counted[key],
                    expected,
                    f"{key} is {counted[key]}, prose says {expected} -- re-derive "
                    "and update SKILL.md and day-b/assertions.md together",
                )

    def test_the_eight_split_four_drug_and_four_environmental(self) -> None:
        """The split the disclosure floor rests on, pinned by path not by count."""
        named = self.census()["named_paths"]
        self.assertEqual(named, self.DRUG | self.ENVIRONMENTAL)
        self.assertEqual(len(self.DRUG), 4)
        self.assertEqual(len(self.ENVIRONMENTAL), 4)

    def test_no_committed_input_pairs_an_allergen_with_a_reaction(self) -> None:
        """The claim the whole ticket rests on, checked over every input.

        If this ever fails, the box is satisfiable from the shorthand for that
        case and the ruling's premise has narrowed -- which is a finding, not a
        test to relax.
        """
        for path in self.census()["clause_lines"]:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not re.search(r"\ballerg", line, re.IGNORECASE):
                    continue
                with self.subTest(case=path.name):
                    self.assertNotRegex(
                        line,
                        r"allerg\w*[^.]*\b(rash|hives|urticaria|anaphylaxis|swelling)\b",
                        "a shorthand naming a reaction would change the premise",
                    )


if __name__ == "__main__":
    unittest.main()
