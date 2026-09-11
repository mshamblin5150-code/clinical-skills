"""Drive the ADR-specific Markdown readers through their public interfaces."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import adr_read
from adr_read import ruling_citations, ruling_ordinals, unresolved_ruling_citations
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_reader_names_its_declared_limits_object(self) -> None:
        self.assertTrue(adr_read.DECLARED_LIMITS)
        self.assertEqual((), bind(adr_read.DECLARED_LIMITS, adr_read.__doc__, mode=NAMING))


class TheRulingOrdinalParserIsLive(unittest.TestCase):
    """#554's shared parser, driven before either tree-wide gate consumes it."""

    def test_addenda_continue_across_a_shape_change(self) -> None:
        record = next((REPO_ROOT / "docs" / "adr").glob("0049-*.md"))
        self.assertEqual(ruling_ordinals(read(record)), list(range(1, 12)))

    def test_the_bold_item_word_is_read_and_the_bare_continuation_is_not(self) -> None:
        record = """\
## Ruled 2026-01-01

**Ruling 1. A declared ruling.**
ruling 5. **The sharp reason is #545's own consequence 2 rather than the precedent.**
"""
        self.assertEqual(ruling_ordinals(record), [1])

    def test_decision_headings_are_read_but_point_and_rule_headings_are_not(self) -> None:
        record = """\
## Decision 1: a declared decision
## Point 2: citation vocabulary is not declaration vocabulary
## Rule 3: citation vocabulary is not declaration vocabulary
"""
        self.assertEqual(ruling_ordinals(record), [1])

    def test_the_alternate_declaration_spellings_belong_to_exactly_four_records(self) -> None:
        found = set()
        for record in sorted((REPO_ROOT / "docs" / "adr").glob("*.md")):
            text = read(record)
            without_alternates = "\n".join(
                ""
                if re.match(
                    r"^(?:\*\*ruling\s+\d+\.\s|#{2,4}\s+decision\s+\d+\b)",
                    line,
                    re.IGNORECASE,
                )
                else line
                for line in text.splitlines()
            )
            if ruling_ordinals(text) != ruling_ordinals(without_alternates):
                found.add(int(record.name[:4]))
        self.assertEqual(found, {94, 96, 126, 127})


class TheRulingCitationResolverIsLive(unittest.TestCase):
    """#554's four coordinate words and adjacency bound, driven synthetically."""

    def test_all_four_coordinate_words_are_read(self) -> None:
        text = "\n".join(
            (
                "AD" "R 0016 ruling 1",
                "AD" "R 0016's point 2",
                "[AD" "R 0016](0016-record.md) decision 3",
                "[AD" "R 0016](0016-record.md)'s rule 4",
            )
        )
        self.assertEqual(
            [(cite.record, cite.number, cite.word) for cite in ruling_citations(text)],
            [(16, 1, "ruling"), (16, 2, "point"), (16, 3, "decision"), (16, 4, "rule")],
        )

    def test_proximity_does_not_bind_an_ordinal_to_the_wrong_record(self) -> None:
        text = "AD" "R 0016's terms leave ruling 4 beside another subject"
        self.assertEqual(list(ruling_citations(text)), [])

    def test_a_dangling_ordinal_is_caught_against_the_shared_parser(self) -> None:
        record = next((REPO_ROOT / "docs" / "adr").glob("0030-*.md"))
        declared = {30: set(ruling_ordinals(read(record)))}
        self.assertEqual(
            unresolved_ruling_citations("AD" "R 0030 ruling 9", declared),
            ["1: AD" "R 0030 ruling 9 does not exist"],
        )


if __name__ == "__main__":
    unittest.main()
