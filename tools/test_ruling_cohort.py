"""Pin [#79]'s promotion lifecycle to the files a reader actually opens.

**There is no scanner here and there cannot be one.** Promotion is a decision
about a *bar*, not a reading of a run: whether a row is enforced lives in the
heading above it and in the prose that says why. Nothing a machine reads from a
run directory can tell a counted row from a binary one, so the check available
is ``test_spelling_scan.py``'s and ``test_differential_shape.py``'s -- **assert
the rule is still written where a reader will find it.** A policy with no
runnable test is one a tidy can delete without failing anything.

Four things, because the ruling binds a glossary, a policy, an ADR and the two
sets it was applied to:

- ``CONTEXT.md`` -- the three terms, defined without implementation detail.
- ``fixtures/README.md`` -- the operating policy, which every set inherits.
- ``docs/adr/0003-...`` -- the tradeoffs and the alternatives that lost.
- ``fixtures/day-b/assertions.md`` and ``fixtures/day-a/assertions.md`` -- #29's
  cohort, promoted.

**The row totals are re-derived rather than quoted**, by counting the row
identifiers in the tables the way ``fixtures/day-b/assertions.md`` says its own
sum was re-derived. That is
`#143 <https://github.com/mshamblin5150-code/clinical-skills/issues/143>`_'s
whole ask: a figure nobody's gate re-derives is a figure that goes stale in
place, and this one had gone stale in place twice already -- once inside one
branch, and once in ``fixtures/README.md``'s own ``Sets`` column, which read
``31 of 31`` while day-a's own file read ``31 of 32``.

**It covers two of the seven sets, deliberately, and that bound is asserted
rather than left to be discovered.** #79 moved day-a's and day-b's totals and
no others, and a gate over the whole ``Sets`` column is a different ticket --
`#202 <https://github.com/mshamblin5150-code/clinical-skills/issues/202>`_, filed with the two stale figures a glob would fail on today
(``peds-bp`` reads ``6 of 11`` and holds 12 rows; ``hedged-dx`` reads ``6 of 6``
and holds 12). **The reason for saying so here is that the alternative is the
defect this module cites #143 for**: an explicit list that reads as a repo-wide
denominator gate is ``all_cases()``'s exact shape, and a silent cap reads as
coverage. ``TheCoverageBoundIsStated`` below is what makes it noisy.

**Nothing here reads a note.** It reads committed Markdown only, so it needs no
fixtures, touches no run directory and can print anything it finds.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT = REPO_ROOT / "CONTEXT.md"
FIXTURES_README = REPO_ROOT / "fixtures" / "README.md"
ADR = REPO_ROOT / "docs" / "adr" / "0003-a-ruling-cohort-promotes-when-fully-scored.md"
DAY_A = REPO_ROOT / "fixtures" / "day-a" / "assertions.md"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"

#: A row identifier opening a table line -- ``| B19 | ...``. Deliberately a
#: **set** rather than a count of matches: a promoted row is named twice, once
#: in its own class table and once in the promotion record beside its successor,
#: and counting occurrences would report a set larger than it is.
ROW_ID = re.compile(r"^\| ([A-Z]\d{1,2}) \|", re.M)

#: #29's cohort: the historical row, the successor appended for it, and the
#: first verdict the successor carries. The verdicts are the five this repo
#: already holds -- day-b run 3's ``REPORTED 1/4`` and day-a run 2's four-for-
#: four on R14 -- carried forward rather than re-measured, which is what makes
#: this a promotion and not a re-run.
class Member(NamedTuple):
    """One cohort member: where it lives, what it was, what it became."""

    fixture: Path
    historical: str
    successor: str
    verdict: str


COHORT = (
    Member(DAY_B, "R1", "B19", "FAIL"),
    Member(DAY_B, "R2", "B20", "FAIL"),
    Member(DAY_B, "R3", "B21", "PASS"),
    Member(DAY_B, "R4", "B22", "FAIL"),
    Member(DAY_A, "R14", "A1", "PASS"),
)


def _row(text: str, row_id: str) -> str:
    """The first table line opening with ``row_id``, or ``""``.

    Empty rather than raising, on ``test_differential_shape.py``'s reasoning: a
    deleted row should read as a failed assertion naming the row rather than as
    a ``StopIteration`` in every test that touches it.
    """
    prefix = "| " + row_id + " | "
    return next((line for line in text.splitlines() if line.startswith(prefix)), "")


def _row_ids(path: Path) -> set[str]:
    return set(ROW_ID.findall(path.read_text(encoding="utf-8")))


class TheGlossaryDefinesTheThreeTerms(unittest.TestCase):
    """``CONTEXT.md``, without implementation detail.

    The policy below is written in these three words and is unreadable without
    them. A term used in four files and defined in none is what #70 was filed
    over.
    """

    def setUp(self):
        self.text = CONTEXT.read_text(encoding="utf-8")

    def test_ruling_cohort_is_defined(self):
        self.assertIn("**Ruling cohort**:", self.text)
        self.assertIn(
            "assertions across one or more fixtures that express one clinician"
            " ruling and share one promotion boundary",
            self.text,
        )

    def test_valid_score_is_defined_and_excludes_unscoreable(self):
        self.assertIn("**Valid score**:", self.text)
        # The exclusion is the whole content of the term. Without it a row that
        # can never be read off a reference would block its cohort forever.
        self.assertIn("Unscoreable is not one", self.text)

    def test_promoted_assertion_is_defined(self):
        self.assertIn("**Promoted assertion**:", self.text)
        self.assertIn("kept in place as its own history", self.text)

    def test_each_term_carries_an_avoid_line(self):
        # Every other entry in this glossary does, and the list is what stops
        # four files inventing four words for one thing.
        for term in ("**Ruling cohort**", "**Valid score**", "**Promoted assertion**"):
            with self.subTest(term=term):
                start = self.text.index(term)
                block = self.text[start : start + 600]
                self.assertIn("_Avoid_:", block)


class TheFixturePolicyStatesTheLifecycle(unittest.TestCase):
    """``fixtures/README.md``, which every set inherits.

    Each clause here is a decision that was open before #79 and is closed after
    it. They are pinned by their own sentences rather than by a heading, because
    a heading survives a rewrite that removes the rule under it.
    """

    def setUp(self):
        self.text = FIXTURES_README.read_text(encoding="utf-8")

    def test_one_ruling_makes_one_cohort(self):
        self.assertIn("**One clinician ruling makes one ruling cohort**", self.text)

    def test_the_cohort_promotes_only_when_every_member_is_scored(self):
        self.assertIn(
            "**A cohort promotes when every member holds a valid score, and not"
            " before.**",
            self.text,
        )

    def test_a_fail_promotes_as_surely_as_a_pass(self):
        # The live alternative, and the one that would have deferred #29's five
        # indefinitely: three of them fail.
        self.assertIn("**A fail promotes a row exactly as a pass does.**", self.text)

    def test_retrospective_scoring_needs_the_rule_to_have_been_in_force(self):
        self.assertIn(
            "**A run may be scored retrospectively only where the rule it is"
            " graded against was already in force.**",
            self.text,
        )

    def test_an_ambiguous_row_is_split_or_clarified_first(self):
        self.assertIn(
            "**A row asking two things is split or clarified before it is promoted**",
            self.text,
        )
        # The residue has to have somewhere to go, or splitting is deletion.
        self.assertIn("the judgment-bound residue stays counted", self.text)

    def test_the_historical_row_stays_and_leaves_the_denominator(self):
        self.assertIn(
            "**The historical row stays where it is, marked promoted and pointing"
            " at its successor.**",
            self.text,
        )
        self.assertIn("out of every later `REPORTED` denominator", self.text)

    def test_the_successor_is_appended(self):
        self.assertIn(
            "**The successor is appended, never inserted and never a renumbering.**",
            self.text,
        )

    def test_a_promoted_cohort_is_closed(self):
        self.assertIn(
            "**A promoted cohort is closed, and later coverage of the same rule"
            " opens a follow-on cohort.**",
            self.text,
        )

    def test_targeted_scoring_is_defined_and_bounded(self):
        self.assertIn("**Targeted scoring is every case the row names**", self.text)
        self.assertIn(
            "**A targeted verdict never moves a complete run's fraction.**", self.text
        )

    def test_the_adr_is_cited_from_the_policy(self):
        # A policy whose reasoning is only in a ticket is a policy nobody can
        # re-open. ADR 0001's own position.
        self.assertIn("0003-a-ruling-cohort-promotes-when-fully-scored", self.text)


class TheAdrRecordsWhatLost(unittest.TestCase):
    """The alternatives, named. An ADR with no rejected option is a summary."""

    def setUp(self):
        self.assertTrue(ADR.is_file(), str(ADR) + " does not exist")
        self.text = ADR.read_text(encoding="utf-8")

    def test_it_has_a_considered_options_section(self):
        self.assertIn("## Considered options", self.text)

    def test_promote_only_on_a_pass_was_rejected(self):
        self.assertIn("**Promote only a cohort that passes.**", self.text)
        after = self.text.split("**Promote only a cohort that passes.**")[1][:900]
        self.assertIn("Rejected", after)

    def test_waiting_for_a_full_re_run_was_rejected(self):
        self.assertIn("**Wait for a complete re-run of every set involved.**", self.text)

    def test_renumbering_in_place_was_rejected(self):
        self.assertIn("**Renumber the counted row into the binary class.**", self.text)

    def test_deferring_until_the_group_stops_growing_was_rejected(self):
        # The status quo, and the one that had been winning by default: the group
        # went from five rows to ten in a single day without anybody choosing it.
        self.assertIn("**Wait until the group stops growing.**", self.text)

    def test_it_names_the_consequence_the_repo_now_carries(self):
        self.assertIn("## Consequences", self.text)


class TheCohortIsPromotedInBothSets(unittest.TestCase):
    """#29's five rows, and the five successors appended for them."""

    def test_each_historical_row_is_marked_and_points_at_its_successor(self):
        for member in COHORT:
            with self.subTest(row=member.historical):
                line = _row(
                    member.fixture.read_text(encoding="utf-8"), member.historical
                )
                self.assertTrue(line, member.historical + " is gone")
                self.assertIn("Promoted to " + member.successor, line)

    def test_each_historical_row_says_it_left_the_reported_denominator(self):
        # Marked but still counted is the arrangement that produces a denominator
        # covering the same rule twice.
        for member in COHORT:
            with self.subTest(row=member.historical):
                line = _row(
                    member.fixture.read_text(encoding="utf-8"), member.historical
                )
                self.assertIn("no longer graded under `REPORTED`", line)

    def test_each_successor_exists_in_its_set(self):
        for member in COHORT:
            with self.subTest(row=member.successor):
                self.assertTrue(
                    _row(member.fixture.read_text(encoding="utf-8"), member.successor),
                    member.successor + " is not a row",
                )

    def test_each_successor_carries_its_first_verdict(self):
        # FAIL, FAIL, PASS, FAIL, PASS -- day-b run 3's `REPORTED 1/4` and day-a
        # run 2's R14, carried forward rather than re-measured.
        for member in COHORT:
            with self.subTest(row=member.successor):
                wanted = "| %s | %s | **%s** |" % (
                    member.successor,
                    member.historical,
                    member.verdict,
                )
                self.assertIn(wanted, member.fixture.read_text(encoding="utf-8"))

    def test_the_successors_are_appended_rather_than_inserted(self):
        """Every successor outranks every row the class already held.

        Stated as an inequality rather than as ``max(...) == 22``, which was the
        first version and would fail on a legitimate B23 while testing nothing
        about appending. What an insert actually does is land a successor at or
        below an existing number, and that is what this catches.
        """
        day_b = _row_ids(DAY_B)
        # The eighteen rows the class held before #79. Named rather than derived,
        # because deriving "what it held before" from the file it now holds is
        # circular.
        for existing in range(1, 19):
            with self.subTest(row="B%d" % existing):
                self.assertIn("B%d" % existing, day_b)
        for member in COHORT:
            if member.fixture is DAY_B:
                with self.subTest(row=member.successor):
                    self.assertGreater(int(member.successor[1:]), 18)

    def test_day_a_opens_a_filled_class_for_its_one_successor(self):
        text = DAY_A.read_text(encoding="utf-8")
        self.assertIn("## FILLED — binary, all must pass", text)

    def test_the_cohort_is_named_as_one_in_both_sets(self):
        # The cross-link is what makes the group findable from either end. #96's
        # four rows are only findable from each other for the same reason.
        for path in (DAY_A, DAY_B):
            with self.subTest(fixture=path.parent.name):
                self.assertIn("#29's ruling cohort", path.read_text(encoding="utf-8"))


class TheHistoricalRecordDidNotMove(unittest.TestCase):
    """The fractions the promotion is forbidden to rewrite.

    This is the acceptance criterion most easily lost by accident: the tidy that
    makes a promoted row read consistently is one keystroke from restating what
    a past run scored.
    """

    def test_day_b_run_3_still_reads_reported_one_of_four(self):
        self.assertIn(
            "`DRIFT 7/7` · `FILLED 10/11` · `CODING 2/2` · `REPORTED 1/4`",
            DAY_B.read_text(encoding="utf-8"),
        )

    def test_day_b_run_2_still_reads_reported_zero_of_one(self):
        self.assertIn(
            "`DRIFT 7/7` · `FILLED 9/9` · `CODING 2/2` · `REPORTED 0/1`",
            DAY_B.read_text(encoding="utf-8"),
        )

    def test_day_a_run_2_still_reads_reported_thirteen_of_fourteen(self):
        self.assertIn(
            "`DRIFT 10/10` · `REPORTED 13/14` · `block 6/7`",
            DAY_A.read_text(encoding="utf-8"),
        )

    def test_no_filled_fraction_is_restated_over_the_promoted_class(self):
        """No `FILLED n/m` anywhere may have a denominator the promotion created.

        The first version of this guessed two wrong fractions by name and let
        every other wrong one through -- a check that passes for the same reason
        a vacuous row does. This reads every fraction in the file instead: the
        class held 11 rows reaching run 3's cases and holds 22 today, and **no
        past run's scorecard may be rewritten over either of the numbers this
        branch moved.**
        """
        denominators = {
            int(d)
            for d in re.findall(r"`FILLED (?:\d+)/(\d+)`", DAY_B.read_text(encoding="utf-8"))
        }
        self.assertTrue(denominators, "no FILLED fraction found at all")
        for wrong in (19, 20, 21, 22):
            with self.subTest(denominator=wrong):
                self.assertNotIn(wrong, denominators)


class TheRowTotalsAreReDerived(unittest.TestCase):
    """Count the identifiers in the tables; compare against the prose.

    ``fixtures/day-b/assertions.md`` says its own sum was re-derived this way
    rather than by adding two to nine, *"which is the only method that would
    have caught it had the arithmetic also been wrong."* This is that method,
    made a test.
    """

    def test_day_b_holds_thirty_nine_rows_and_says_so(self):
        self.assertEqual(len(_row_ids(DAY_B)), 39)
        self.assertIn(
            "24 scored, 11 unscored and 4 promoted successors is 39",
            DAY_B.read_text(encoding="utf-8"),
        )

    def test_day_a_holds_thirty_three_rows_and_says_so(self):
        self.assertEqual(len(_row_ids(DAY_A)), 33)
        self.assertIn("the set now holds 33", DAY_A.read_text(encoding="utf-8"))

    def test_the_sets_table_carries_the_same_totals(self):
        # It read `31 of 31` for day-a while day-a's own file read `31 of 32`,
        # which is the same figure stale in two files at once.
        readme = FIXTURES_README.read_text(encoding="utf-8")
        self.assertIn("**31 of 33 rows**", readme)
        self.assertIn("**24 of 39 rows**", readme)


class TheCoverageBoundIsStated(unittest.TestCase):
    """What this module does not reach, made to fail if anyone forgets.

    ``fixtures/`` holds seven sets and #79 moved two. The risk is not that the
    other five go unchecked today -- it is that a later reader takes a green run
    here as *the Sets column is gated*, which is `#137
    <https://github.com/mshamblin5150-code/clinical-skills/issues/137>`_'s
    partial instrument arriving on the table `#143
    <https://github.com/mshamblin5150-code/clinical-skills/issues/143>`_ is
    about.
    """

    def test_exactly_two_sets_are_pinned(self):
        pinned = {member.fixture for member in COHORT}
        self.assertEqual(pinned, {DAY_A, DAY_B})

    def test_the_repo_holds_more_sets_than_this_module_reads(self):
        # If this ever stops being true, the bound has closed on its own and the
        # docstring above is the thing to correct.
        every = set((REPO_ROOT / "fixtures").glob("*/assertions.md"))
        self.assertGreater(len(every), 2)
        self.assertTrue({DAY_A, DAY_B} <= every)

    def test_the_docstring_names_the_ticket_that_would_close_the_bound(self):
        # A limit recorded only in a commit message is one the next reader of
        # this file will not find.
        self.assertIn("issues/202", __doc__)


if __name__ == "__main__":
    unittest.main()
