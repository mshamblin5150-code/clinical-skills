"""Bind the glossary terms that declare code vocabularies to their constants.

Ticket #444. ``CONTEXT.md`` names enumerable vocabularies that code also
implements. This test reads the documentation instead of keeping another copy of
either value set, so a change on one side alone fails in either direction.

What this cannot reach
----------------------

``CODE_VOCABULARIES`` is the complete declaration this check reads. A glossary term
added outside that tuple is invisible here, even when its prose contains a
vocabulary. The list is explicit by ruling: a predicate over backticked lowercase
words also selects file extensions, command choices, and other values that are not
domain vocabularies.

``tools/test_glossary_terms.py`` makes this module's first-occurrence read
(``text.index``) sound.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401

import guidelines_recs
import threshold_coverage

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT = REPO_ROOT / "CONTEXT.md"
AGENTS = REPO_ROOT / "AGENTS.md"
THRESHOLD_README = REPO_ROOT / "reference" / "thresholds" / "README.md"

#: The glossary terms whose values this check binds to code, paired with their
#: implementations. This tuple is the ceiling: a term absent here is not inspected
#: or implied to be covered.
CODE_VOCABULARIES = (
    ("Source mode", (guidelines_recs.MODE_EXACT, guidelines_recs.MODE_BOUND)),
    ("Sweep state", threshold_coverage.STATES),
)

BACKTICKED = re.compile(r"`([^`]+)`")


def glossary_vocabulary(text: str, term: str) -> tuple[str, ...]:
    """Return each backticked value once, in its documented order."""
    heading = f"**{term}**:"
    start = text.index(heading) + len(heading)
    next_heading = text.find("\n**", start)
    body = text[start:] if next_heading == -1 else text[start:next_heading]
    return tuple(dict.fromkeys(BACKTICKED.findall(body)))


def vocabulary_mismatches(
    text: str,
    declared: tuple[tuple[str, tuple[str, ...]], ...] = CODE_VOCABULARIES,
) -> tuple[str, ...]:
    """Return every declared term whose implementation differs from its prose."""
    return tuple(
        term
        for term, implemented in declared
        if implemented != glossary_vocabulary(text, term)
    )


class TheGlossaryVocabulariesAreBoundToCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTEXT.read_text(encoding="utf-8")

    def test_every_declared_term_is_the_code_vocabulary(self) -> None:
        self.assertEqual(vocabulary_mismatches(self.text), ())

    def test_every_published_sweep_state_copy_is_the_code_vocabulary(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        readme = THRESHOLD_README.read_text(encoding="utf-8")
        agents_sentence = re.search(
            r"records every catalog topic as (?P<states>[^.]+)\.", agents
        )
        state_section = readme.split("with one of these states:", 1)[1].split(
            "The `artifact` column", 1
        )[0]
        summary_sentence = re.search(
            r"distinguishes (?P<states>`sheet`[^.]+)\.", readme
        )

        self.assertIsNotNone(agents_sentence)
        self.assertIsNotNone(summary_sentence)
        copies = (
            tuple(BACKTICKED.findall(agents_sentence.group("states"))),
            tuple(re.findall(r"(?m)^- `([^`]+)`:.*$", state_section)),
            tuple(BACKTICKED.findall(summary_sentence.group("states"))),
        )
        self.assertEqual(copies, (threshold_coverage.STATES,) * len(copies))


class TheInstrumentIsLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTEXT.read_text(encoding="utf-8")

    def test_a_term_body_is_bounded_by_the_next_term(self) -> None:
        text = "**First**:\nOne of `a` or `b`.\n**Second**:\nUse `c`.\n"
        self.assertEqual(glossary_vocabulary(text, "First"), ("a", "b"))

    def test_an_absent_declared_term_does_not_read_as_an_empty_vocabulary(self) -> None:
        with self.assertRaises(ValueError):
            glossary_vocabulary("**Another**:\nUse `value`.\n", "Missing")

    def test_each_one_sided_code_mutant_is_detected(self) -> None:
        for target, _ in CODE_VOCABULARIES:
            with self.subTest(term=target):
                mutant = tuple(
                    (term, implemented + ("mutant",))
                    if term == target
                    else (term, implemented)
                    for term, implemented in CODE_VOCABULARIES
                )
                self.assertEqual(vocabulary_mismatches(self.text, mutant), (target,))
