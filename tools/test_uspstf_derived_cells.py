"""Checks the committed USPSTF derived cells against their paired statements.

The producer and its unit tests can agree on the same wrong derivation while the
committed table faithfully repeats it. This check instead reads the shipped artifact,
joins its two tables through ``guidelines_recs.parse_curated_table``, and independently
walks every interval phrase in each committed statement. It needs no corpus, PDF, or
network access.

## What this cannot reach

**Whether ``population`` content is correct.** Population uses a different grammar, and
field-quoted cells are named in the committed table's population-quotation section. This
file establishes that every committed Population cell is present; it establishes nothing
about whether a cell's content is right.

**Whether a document states a period outside the recommendation sentence.** Issue #435
owns that wider read. This check is deliberately bounded to the statement sentence the
artifact says it derives from.

Issue #432.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401

import guidelines_recs
import uspstf_table

REFERENCE = (
    Path(__file__).resolve().parent.parent / "reference" / "guidelines-uspstf.md"
)
NOT_STATED = "not stated"
ALTERNATIVE_JOIN = " or "
INTERVAL_PHRASE = re.compile(
    r"\bevery \d+(?: to \d+)? (?:years?|months?|weeks?)\b"
    r"|\bbiennial(?:ly)?\b|\bannual(?:ly)?\b|\bevery year\b"
    r"|\b1-time\b|\bone-time\b|\bat least once\b"
    r"|\bperiodic(?:ally)?\b|\bat each visit\b|\brepeated\b",
    re.I,
)
COUNT_WORD = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
COUNT = rf"(?:\d+|{COUNT_WORD})"
COUNT_RANGE = rf"{COUNT}(?:\s*(?:-|to)\s*{COUNT})?"
SUB_YEARLY_UNIT = r"(?:minutes?|hours?|days?|weeks?|months?|quarters?)"
SUB_YEARLY_ADVERB = (
    r"(?:hourly|daily|weekly|fortnightly|monthly|quarterly|biweekly|bimonthly"
    r"|semi-?annual(?:ly)?|biannual(?:ly)?)"
)
SUB_YEARLY_PERIOD = re.compile(
    rf"\b(?:every (?:(?:other|{COUNT_RANGE}) )?{SUB_YEARLY_UNIT}"
    rf"|(?:each|alternate) {SUB_YEARLY_UNIT}"
    rf"|(?:at )?{COUNT_RANGE}\s*-?\s*{SUB_YEARLY_UNIT} intervals?"
    rf"|in {COUNT_RANGE} {SUB_YEARLY_UNIT}"
    rf"|{COUNT} {SUB_YEARLY_UNIT} per {SUB_YEARLY_UNIT}"
    rf"|(?:once|twice|{COUNT} times?) "
    rf"(?:{SUB_YEARLY_ADVERB}|(?:a|per) {SUB_YEARLY_UNIT})"
    rf"|(?:twice|{COUNT} times?) (?:yearly|(?:a|per) year)"
    rf"|{SUB_YEARLY_ADVERB})\b",
    re.I,
)
DECLINED_HYPHENATED_QUALIFIER = r"[A-Za-z]+(?:\s*\([A-Z]\))?-[a-z]+"
DECLINED_WIDENED_POPULATION_PHRASE = re.compile(
    uspstf_table.POPULATION_PHRASE.pattern.replace(
        uspstf_table._POP_QUALIFIER,
        rf"(?:{uspstf_table._POP_QUALIFIER}|{DECLINED_HYPHENATED_QUALIFIER})",
    ),
    uspstf_table.POPULATION_PHRASE.flags,
)


def statement_periods(statement: str) -> list[str]:
    """Distinct interval phrases in source order, independent of ``derive_interval``."""
    return list(
        dict.fromkeys(
            match.group(0).lower()
            for match in INTERVAL_PHRASE.finditer(statement)
        )
    )


class TheCommittedIntervalsAccountForTheirStatements(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        grouped = guidelines_recs.parse_curated_table(
            REFERENCE.read_text(encoding="utf-8")
        )
        cls.rows = [row for rows in grouped.values() for row in rows]

    def test_every_interval_phrase_a_statement_names_appears_in_its_cell(self) -> None:
        for row in self.rows:
            periods = statement_periods(row.statement)
            expected = ALTERNATIVE_JOIN.join(periods) if periods else NOT_STATED
            self.assertEqual(
                row.interval,
                expected,
                f"{row.filename} page {row.page}: {row.topic}",
            )

    def test_the_multiple_period_rule_moves_exactly_the_cervical_cell(self) -> None:
        multiple = [row for row in self.rows if len(statement_periods(row.statement)) > 1]
        self.assertEqual(
            [(row.topic, row.population, row.interval) for row in multiple],
            [
                (
                    "Screening for Cervical Cancer",
                    "women aged 30 to 65 years",
                    "every 3 years or every 5 years",
                )
            ],
        )

    def test_the_ruled_interval_reach_population_has_not_moved(self) -> None:
        not_stated = [row for row in self.rows if row.interval == NOT_STATED]
        rows_by_file: dict[str, list[guidelines_recs.CuratedRow]] = {}
        for row in self.rows:
            rows_by_file.setdefault(row.filename, []).append(row)
        population = (
            len(self.rows),
            len(not_stated),
            len({row.filename for row in not_stated}),
            sum(
                all(row.interval == NOT_STATED for row in rows)
                for rows in rows_by_file.values()
            ),
        )
        self.assertEqual(
            population,
            (143, 135, 89, 83),
            "The ruled interval-reach population moved. Run "
            "tools/uspstf_interval_reach.py and review ADR 0028 before accepting "
            "a changed USPSTF artifact.",
        )

    def test_no_undeclared_sub_yearly_period_reaches_a_committed_statement(self) -> None:
        declared = {phrase.casefold() for phrase, _reason in uspstf_table.INTERVAL_EXCLUSIONS}
        reached = []
        for row in self.rows:
            for match in SUB_YEARLY_PERIOD.finditer(row.statement):
                phrase = match.group(0).casefold()
                if phrase not in declared:
                    reached.append((row.filename, row.page, row.topic, phrase))
        self.assertEqual(
            reached,
            [],
            "A sub-yearly period reached a committed USPSTF statement; the granularity "
            "argument no longer decides the case. Review ADR 0027 before changing the "
            "interval vocabulary or artifact.",
        )

    def test_the_sub_yearly_tripwire_is_independent_of_the_interval_vocabulary(self) -> None:
        statement = (
            "every 2 weeks; every 3 months; weekly; monthly; twice daily; "
            "twice weekly; every other day; every 12 hours; hourly; "
            "three times a week; once per month; every six hours; "
            "every 30 minutes; twice yearly; three times a year; every quarter; "
            "every 2-3 weeks; semi-annually; each month; alternate days; "
            "at 3-month intervals; in 6 months; two days per week"
        )
        self.assertEqual(
            [match.group(0) for match in SUB_YEARLY_PERIOD.finditer(statement)],
            [
                "every 2 weeks",
                "every 3 months",
                "weekly",
                "monthly",
                "twice daily",
                "twice weekly",
                "every other day",
                "every 12 hours",
                "hourly",
                "three times a week",
                "once per month",
                "every six hours",
                "every 30 minutes",
                "twice yearly",
                "three times a year",
                "every quarter",
                "every 2-3 weeks",
                "semi-annually",
                "each month",
                "alternate days",
                "at 3-month intervals",
                "in 6 months",
                "two days per week",
            ],
        )


class TheCommittedPopulationsArePresent(unittest.TestCase):
    def test_no_population_cell_is_not_stated(self) -> None:
        grouped = guidelines_recs.parse_curated_table(
            REFERENCE.read_text(encoding="utf-8")
        )
        rows = [row for document_rows in grouped.values() for row in document_rows]

        self.assertEqual(
            sum(row.population == NOT_STATED for row in rows),
            0,
            "The committed USPSTF artifact has a missing Population cell. Re-run "
            "tools/uspstf_table.py and review ADR 0044 before accepting a changed "
            "artifact.",
        )


class TheRuledPopulationLiteral(unittest.TestCase):
    def test_the_rh_negative_literal_reads_the_complete_population(self) -> None:
        statement = (
            "The USPSTF recommends repeated Rh (D) antibody testing for all "
            "unsensitized Rh (D)-negative women at 24-28 weeks' gestation, unless "
            "the biological father is known to be Rh (D)-negative."
        )

        self.assertEqual(
            uspstf_table.derive_population(statement),
            "all unsensitized Rh (D)-negative women at 24-28 weeks' gestation, "
            "unless the biological father is known to be Rh (D)-negative",
        )

    def test_the_declined_widening_fires_in_both_directions(self) -> None:
        """Constructed sentences are a floor; ADR 0044 records a 2026-08-26 corpus cost of zero."""
        real_population = (
            "The USPSTF recommends counseling for tobacco-dependent adults."
        )
        methodological_adjective = (
            "The USPSTF concludes the evidence is insufficient in low-quality patients."
        )

        with mock.patch.object(
            uspstf_table,
            "POPULATION_PHRASE",
            DECLINED_WIDENED_POPULATION_PHRASE,
        ):
            self.assertEqual(
                uspstf_table.derive_population(real_population),
                "tobacco-dependent adults",
            )
            self.assertEqual(
                uspstf_table.derive_population(methodological_adjective),
                "low-quality patients",
            )
        self.assertEqual(
            uspstf_table.derive_population(real_population),
            NOT_STATED,
        )
        self.assertEqual(
            uspstf_table.derive_population(methodological_adjective),
            NOT_STATED,
        )


if __name__ == "__main__":
    unittest.main()
