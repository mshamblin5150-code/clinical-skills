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

REFERENCE = (
    Path(__file__).resolve().parent.parent / "reference" / "guidelines-uspstf.md"
)
NOT_STATED = "not stated"
ALTERNATIVE_JOIN = " or "
INTERVAL_PHRASE = re.compile(
    r"\bevery \d+(?: to \d+)? (?:years?|months?|weeks?)\b"
    r"|\bbiennial(?:ly)?\b|\bannual(?:ly)?\b|\bevery year\b"
    r"|\b1-time\b|\bone-time\b|\bat least once\b|\bdaily\b"
    r"|\bperiodic(?:ally)?\b|\bat each visit\b|\brepeated\b",
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


if __name__ == "__main__":
    unittest.main()
