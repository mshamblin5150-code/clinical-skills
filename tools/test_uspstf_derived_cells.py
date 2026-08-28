"""Checks the committed USPSTF derived cells against their paired statements.

The producer and its unit tests can agree on the same wrong derivation while the
committed table faithfully repeats it. This check instead reads the shipped artifact,
joins its two tables through ``guidelines_recs.parse_curated_table``, and independently
walks every interval phrase in each committed statement. It needs no corpus, PDF, or
network access.

## What this cannot reach

**Whether ``population`` is completely derived from its statement.** Population uses a
different grammar and can fall back to a document field that the committed table does
not carry. This file establishes nothing about that derived cell.

**Whether a document states a period outside the recommendation sentence.** Issue #435
owns that wider read. This check is deliberately bounded to the statement sentence the
artifact says it derives from.

Issue #432.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
