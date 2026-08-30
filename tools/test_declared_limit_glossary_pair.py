"""Bind the two halves of the declared-limit glossary distinction.

Ticket #667 and ADR 0082. This check cannot tell whether either definition is
right, and a body reworded to keep the phrase and lose the meaning passes.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from prose_bind import ProseBind
from test_glossary_terms import glossary_definitions


CONTEXT = Path(__file__).resolve().parent.parent / "CONTEXT.md"

DECLARED_LIMIT_CRITERION = """\
What may go in one is a sentence telling a reader that a clean result covers
less than it appears to.
"""
DECLARED_LIMIT_POINTER = "Distinct from a declared rationale"

DECLARED_RATIONALE_POINTER = (
    "The same shape as a declared limit and never a member of one"
)
SENTENCES_NEVER_NAMES = (
    "Which it is, is decided on the sentence and never on the constant's name"
)

CLEAN_LIMIT = """\
**Declared limit**:
What may go in one is a sentence telling a reader that a clean result covers
less than it appears to. Distinct from a **declared rationale**.
_Avoid_: caveat

"""

CLEAN_RATIONALE = """\
**Declared rationale**:
The same shape as a **declared limit** and never a member of one. Which it is,
is decided on the sentence and never on the constant's name.
_Avoid_: declared limit
"""

CLEAN_PAIR = "### Guidelines\n\n" + CLEAN_LIMIT + CLEAN_RATIONALE


class DeclaredPairAssertions(ProseBind):
    def assert_declared_pair(self, text: str) -> None:
        definitions = glossary_definitions(text)
        self.assertIn("Declared limit", definitions)
        self.assertIn("Declared rationale", definitions)
        limit = definitions["Declared limit"][0]
        rationale = definitions["Declared rationale"][0]
        self.assertProseIn(DECLARED_LIMIT_CRITERION, limit)
        self.assertProseIn(DECLARED_LIMIT_POINTER, limit)
        self.assertProseIn(DECLARED_RATIONALE_POINTER, rationale)
        self.assertProseIn(SENTENCES_NEVER_NAMES, rationale)


class TheDeclaredLimitGlossaryPairIsBound(
    DeclaredPairAssertions,
    unittest.TestCase,
):
    def test_context_carries_both_halves_of_the_distinction(self) -> None:
        self.assert_declared_pair(CONTEXT.read_text(encoding="utf-8"))


class TheInstrumentIsLive(DeclaredPairAssertions, unittest.TestCase):
    def test_a_clean_pair_passes(self) -> None:
        self.assert_declared_pair(CLEAN_PAIR)

    def test_removing_either_half_fails(self) -> None:
        for missing, entry in (
            ("Declared limit", CLEAN_LIMIT),
            ("Declared rationale", CLEAN_RATIONALE),
        ):
            broken = CLEAN_PAIR.replace(entry, "")
            with self.subTest(missing=missing):
                with self.assertRaises(AssertionError):
                    self.assert_declared_pair(broken)


if __name__ == "__main__":
    unittest.main()
