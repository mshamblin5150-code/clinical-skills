"""Pin the ruling [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94) settled.

**The defect was a box with no legal value.** ``SOAP.md`` writes the slot as
``Allergies (reaction): <allergen - reaction; NKDA if none>``, and where the
shorthand gives an allergen and no reaction three rules bound it shut at once:
the box demands a value, the grounding rule supplies none, and drift row 12 bans
the hedge. **Three independent runs reached for the banned string**, one of them
committed under ``fixtures/filled-anchor/``, which carries the class **18 times
across six files** in **five** phrasings -- a figure this file's own prose twice
got wrong by running ``grep -c`` on one literal, which counts lines rather than
occurrences and misses the paraphrases outright.

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

**Two classes here are not about the ruling, and they are here rather than in a
file of their own because #200 is what moved the figures they guard.**
``TheRulingCohortIsClosed`` pins the promotion of ``R6`` to ``B23``, and
``TheSetTotalIsReDerivedRatherThanTyped`` pins day-b's row total and its FILLED
class count against the tables. That is a second subject in one module, and it
is the trade this repo has taken before: a guard living beside the change that
needed it gets read, and a guard filed by subject gets written once and never
opened. Move them if a third subject arrives.
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

    #: The 8, split the way the disclosure floor is drawn. **Not a partition:**
    #: ``day-b`` cases 7 and 11 name an environmental allergen *as well* as a
    #: drug one, so 4 inputs name a drug and **6** name an environmental -- the
    #: set below is the environmental-*only* four, which is what the published
    #: figure says and what the name now records. A reader taking the two counts
    #: for complements has the wrong denominator for either. No committed input
    #: names a **food** allergen; ``peds-bp`` case 5's lactose intolerance is an
    #: enzyme deficiency rather than an allergy, and whether it reaches the box
    #: at all is #96's question rather than this one's.
    DRUG = {
        "fixtures/day-b/shorthand/case-07.md",
        "fixtures/day-b/shorthand/case-11.md",
        "fixtures/duration-span/shorthand/case-01.md",
        "fixtures/duration-span/shorthand/case-02.md",
    }
    ENVIRONMENTAL_ONLY = {
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

    def test_the_eight_split_four_drug_and_four_environmental_only(self) -> None:
        """The split the disclosure floor rests on, pinned by path not by count."""
        named = self.census()["named_paths"]
        self.assertEqual(named, self.DRUG | self.ENVIRONMENTAL_ONLY)
        self.assertEqual(len(self.DRUG), 4)
        self.assertEqual(len(self.ENVIRONMENTAL_ONLY), 4)

    #: Every place a figure is published, and the label it is published under.
    #: Markdown emphasis and backticks are stripped before matching, so a
    #: rewrite that re-bolds a sentence does not break the pin.
    PUBLISHED = {
        "inputs": r"(\d+) committed inputs",
        "allergy_clause": r"(\d+) carry an allergy clause",
        "nkda": r"(\d+) say NKDA",
        "names_allergen": r"(\d+) name an allergen",
    }

    def test_the_prose_copies_agree_with_the_re_derivation(self) -> None:
        """Pin the **published** figures, not only the computed ones.

        ``test_the_published_figures_still_hold`` guards fixtures against
        ``EXPECTED``; nothing guarded ``EXPECTED`` against the prose, so editing
        a ``37`` to a ``38`` in either document failed no test. That is exactly
        the residual gap [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)
        describes -- a figure kept true in one place and copied to two others --
        and it is this ticket's own ``31 / 16 / 11 / 5`` waiting to happen again.
        Found in the tracker sweep.
        """
        for path in (SKILL, REPO_ROOT / "fixtures" / "day-b" / "assertions.md"):
            plain = read(path).replace("*", "").replace("`", "")
            for sentence in self.fixture_sentences(plain):
                for key, pattern in self.PUBLISHED.items():
                    for written in re.findall(pattern, sentence):
                        with self.subTest(path=path.name, figure=key):
                            self.assertEqual(
                                int(written),
                                self.EXPECTED[key],
                                f"{path.name} publishes {key}={written}, "
                                f"re-derivation gives {self.EXPECTED[key]}",
                            )

    @staticmethod
    def fixture_sentences(plain: str) -> list[str]:
        """Sentences about the **committed inputs**, not about the corpus.

        Both denominators live in these files and both are counted with the same
        verb: ``20 carry an allergy clause`` over 37 fixtures, and ``284`` over
        551 corpus encounters. A pattern blind to which one it matched read the
        corpus figure as a stale fixture figure -- the first run of this test
        failed on exactly that, which is the two-denominators confusion #143
        names, arriving in the guard written against it.
        """
        return [
            sentence
            for sentence in re.split(r"(?<=[.])\s", plain)
            if "committed inputs" in sentence
        ]

    def test_each_figure_is_actually_published_somewhere(self) -> None:
        """A pin matching nothing passes for the wrong reason."""
        plain = read(SKILL).replace("*", "").replace("`", "")
        for key, pattern in self.PUBLISHED.items():
            if key == "nkda":
                continue  # SKILL.md states this one only via the corpus split
            with self.subTest(figure=key):
                self.assertTrue(re.search(pattern, plain), f"{key} unpublished")

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



class TheRulingCohortIsClosed(unittest.TestCase):
    """[#200](https://github.com/mshamblin5150-code/clinical-skills/issues/200):
    ``R6`` was promotable *for want of a run* and now has one.

    **A promotion is two claims, not one**, and the tests here hold them apart.
    The first is that a **valid** score exists -- output produced while the #94
    rule was in force, graded by a pass that did not write it -- which is why
    the verdict has to carry a commit and a date rather than only a word. The
    second is that promoting it did not quietly dilute the rule: the binary row
    has to carry the limbs ``R6`` carried, or the cohort closed by weakening.

    **The historical row stays.** ``fixtures/README``'s *append, never insert*
    reaches rows across a promotion exactly as it reaches a drift matrix -- a
    reader arriving at ``R6`` from #94, from #95 or from ``SKILL.md`` has to
    land on the row those documents cite, marked with where it went.
    """

    DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"
    SUCCESSOR = "B23"

    def day_b(self) -> str:
        return read(self.DAY_B)

    def row(self, ident: str) -> str:
        """The one table line whose first cell is ``ident``."""
        for line in self.day_b().splitlines():
            if line.startswith(f"| {ident} |"):
                return line
        self.fail(f"day-b/assertions.md holds no {ident} row")

    def test_the_historical_row_survives_the_promotion(self) -> None:
        """#94, #95 and this file all cite ``R6`` by name. It may not vanish."""
        self.assertTrue(self.row("R6"))

    def test_the_historical_row_names_its_successor(self) -> None:
        """A row a reader arrives at from a ticket has to say where it went."""
        self.assertIn(
            self.SUCCESSOR,
            self.row("R6"),
            "R6 is promoted and does not say so -- a reader arriving from #94 "
            "would read a counted row and miss the enforced one",
        )

    def test_the_successor_is_in_the_binary_class(self) -> None:
        """``B`` is FILLED's prefix, and the prefix follows the bar here."""
        self.assertTrue(self.row(self.SUCCESSOR))

    def test_the_verdict_carries_a_commit_and_a_date(self) -> None:
        """A verdict with no commit is not a valid score, it is an opinion.

        The rule was in force from 2026-08-16; a score belongs to the commit it
        was produced on, which is the whole of what runs 1 through 3 could not
        say about this row.
        """
        row = self.row("R6")
        self.assertRegex(row, r"\b(PASS|FAIL)\b", "no explicit verdict on the R6 row")
        self.assertRegex(
            row,
            r"\b(PASS|FAIL)\b.{0,120}?`[0-9a-f]{7}`",
            "the verdict names no commit -- a score with no commit belongs to none",
        )
        self.assertRegex(
            row,
            r"\b20[0-9]{2}-[01][0-9]-[0-3][0-9]\b",
            "the verdict names no scoring date",
        )
        self.assertIn("targeted scoring", self.day_b())

    def test_the_promotion_did_not_dilute_the_rule(self) -> None:
        """Every limb ``R6`` carried survives into the enforced row."""
        row = self.row(self.SUCCESSOR)
        for limb in ("inferred reaction", "no tier word", "FILLED·asserted"):
            with self.subTest(limb=limb):
                self.assertIn(limb, row)
        self.assertRegex(
            row,
            r"never licenses|licenses a drug",
            "the never-discharge limb is the one clause the ruling rests on",
        )

    def test_the_split_or_clarify_check_is_recorded(self) -> None:
        """A promotion that skipped the check reads exactly like one that passed it.

        ``fixtures/README`` -- from #79's branch, where the promotion policy is
        written -- requires that *a row asking two things is split or clarified
        before it is promoted, never promoted whole and read down later.* #56 is
        the worked instance, and the failure it names is a bar meaning less than
        it reads. **The check leaves no trace in the promoted row**, so nothing
        but a recorded outcome distinguishes a row that was examined from one
        that was waved through -- which is why this pins the record rather than
        the row.
        """
        text = self.day_b()
        self.assertIn(
            "split or clarified before it is promoted",
            text,
            "the criterion the promotion was checked against is not quoted",
        )
        self.assertRegex(
            text,
            rf"\| R6 . {self.SUCCESSOR} \|",
            "no split-or-clarify outcome is recorded for the promoted row",
        )

    def test_the_promoted_row_leaves_later_reported_denominators(self) -> None:
        """A rule graded twice under one fraction is a fraction nobody can read.

        The historical fractions are the other half and are pinned above: run
        3's ``REPORTED 1/4`` still means the four rows it meant in 2026-08-12.
        """
        self.assertRegex(
            self.day_b(),
            r"What a future scorecard grades under .REPORTED. is R5\b",
            "REPORTED still counts the promoted row in its live denominator",
        )

    def test_the_last_complete_run_fraction_is_untouched(self) -> None:
        """A targeted score is not a run, and folding it in would redate one.

        Run 3 graded twenty-four rows on ``b65b9f6``. The cohort scored here is
        two encounters of twelve on a later commit, so it can no more move that
        fraction than #95's re-score moved run 2's.
        """
        self.assertIn(
            "`DRIFT 7/7` · `FILLED 10/11` · `CODING 2/2` · `REPORTED 1/4`",
            self.day_b(),
            "run 3's scorecard has moved -- a targeted verdict may not touch it",
        )


class TheSetTotalIsReDerivedRatherThanTyped(unittest.TestCase):
    """The denominator guard, added by the change that moved the denominator.

    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is
    one figure going stale in many places at once, and day-b's row total is its
    worst instance: it was typed in **eight** places across two files and three
    consecutive commits were spent chasing it. Nothing recomputed it.

    **The tables are the source and the prose is the copy**, which is the method
    the merge conflict on this file forced -- count the row identifiers, then
    check every published total against the count. It is the only method that
    catches a *wrong starting figure* rather than a stale one.

    **Row totals are matched by the word ``rows`` following them**, deliberately.
    Both denominators live in these files: thirty-six rows over one set, and
    thirty-seven committed inputs over all of them. A pattern blind to which one
    it matched is the confusion #143 names, and ``TheFixturesStillPoseTheQuestion``
    already failed on exactly that once.
    """

    DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"
    README = REPO_ROOT / "fixtures" / "README.md"

    #: Enough of the range to survive a few more rows without an edit here.
    SPELLED = {
        15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
        19: "nineteen", 20: "twenty", 21: "twenty-one", 22: "twenty-two",
        23: "twenty-three", 24: "twenty-four", 25: "twenty-five",
        26: "twenty-six", 27: "twenty-seven", 28: "twenty-eight",
        29: "twenty-nine",
        30: "thirty", 31: "thirty-one", 32: "thirty-two", 33: "thirty-three",
        34: "thirty-four", 35: "thirty-five", 36: "thirty-six",
        37: "thirty-seven", 38: "thirty-eight", 39: "thirty-nine", 40: "forty",
        41: "forty-one", 42: "forty-two", 43: "forty-three", 44: "forty-four",
        45: "forty-five",
    }

    ROW_ID = re.compile(r"^\| ([DBCGR][0-9]+) \|")

    def row_ids(self) -> set[str]:
        found = set()
        for line in read(self.DAY_B).splitlines():
            match = self.ROW_ID.match(line)
            if match:
                found.add(match.group(1))
        return found

    def test_the_identifiers_are_readable(self) -> None:
        """A guard that parsed nothing would pass for the wrong reason."""
        self.assertGreaterEqual(len(self.row_ids()), 35)

    def test_every_published_total_agrees_with_the_tables(self) -> None:
        """Both files, every spelled total, against one re-derivation."""
        expected = self.SPELLED[len(self.row_ids())]
        for path in (self.DAY_B, self.README):
            plain = read(path).replace("*", "").replace("`", "")
            for written in re.findall(r"\b((?:thirty|forty)-?\w*) rows\b", plain):
                with self.subTest(path=path.name, written=written):
                    self.assertEqual(
                        written,
                        expected,
                        f"{path.name} publishes {written} rows, the tables hold "
                        f"{len(self.row_ids())} -- re-derive both files together",
                    )

    def test_the_total_is_published_at_all(self) -> None:
        """A pin matching nothing passes for the wrong reason -- twice over."""
        expected = self.SPELLED[len(self.row_ids())]
        for path in (self.DAY_B, self.README):
            plain = read(path).replace("*", "").replace("`", "")
            with self.subTest(path=path.name):
                self.assertIn(f"{expected} rows", plain)

    def test_the_sets_table_cell_agrees_too(self) -> None:
        """The numeric copy, which the spelled pattern above cannot see.

        ``fixtures/README``'s ``Sets`` table reports day-b as ``N of M rows``.
        Every other set reports its own M in the same column, so this is scoped
        to the one line rather than matched across the table -- ``day-a``'s
        ``31 of 31`` is a correct figure about a different set.
        """
        for line in read(self.README).splitlines():
            if not line.startswith("| [day-b]"):
                continue
            written = re.search(r"(\d+) of (\d+) rows", line)
            self.assertTrue(written, "day-b's Sets row states no row count")
            self.assertEqual(
                int(written.group(2)),
                len(self.row_ids()),
                "the Sets table and the tables disagree about how many rows "
                "day-b holds -- re-derive from the identifiers, not from the cell",
            )
            return
        self.fail("fixtures/README.md holds no day-b row in the Sets table")

    def test_the_filled_class_count_agrees_with_its_own_rows(self) -> None:
        """The denominator that three sweeps missed, pinned where it lives.

        ``These nineteen do not move with wording`` is a count of the ``B``
        rows, written into the middle of a paragraph rather than into a
        scorecard -- which is why every sweep that went looking for a stale
        figure walked past it while it said *sixteen* against eighteen rows.
        """
        b_rows = len([r for r in self.row_ids() if r.startswith("B")])
        expected = self.SPELLED[b_rows]
        self.assertIn(
            f"These {expected} do not move with wording",
            read(self.DAY_B),
            f"the FILLED class holds {b_rows} rows and the prose disagrees",
        )


if __name__ == "__main__":
    unittest.main()
