"""Resolve ``CLAUDE.md`` pointers and keep limits rows out of their sections.

ADR 0120. The limits-object population is name-keyed and declared; string
extraction is shape-blind; comparison is scoped to the ``###`` section carrying
each pointer. A clean result does not establish that unpointed sections copy no
row, that the pointer is the right one, or that non-string limits are uncopied.
Live figure instances state that ceiling precisely:
``split_census.HISTORICAL_SHAPE_FIGURES`` stores integers the walk skips, while
``guidelines_extract.ORPHANED_FIGURES`` stores strings the walk reads.
"""

from __future__ import annotations

import importlib
import re
import unittest
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from prose_bind import SHINGLE, normalized
from test_module_sections import SECTION


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
POINTER = re.compile(r"`(?P<module>[a-z_][a-z0-9_]*)\.(?P<constant>[A-Z][A-Z0-9_]*)`")
LIMIT_CONSTANTS = (
    "DECLARED_LIMITS",
    "NOT_REACHED",
    "NOT_GUARDED",
    "NOT_APPLIED",
    "NOT_STRIPPED",
    "NOT_VALIDATED_AGAINST",
    "ORPHANED_FIGURES",
)
LIMITS_ISH = re.compile(r"(?:LIMIT|^NOT_|ORPHAN)")
EXCEPTIONS = (
    (
        "guidelines_extract",
        "ORPHANED_FIGURES",
        "306",
        1,
        "the section's 306 welded-running-head lines are a different true figure",
    ),
)
EXCEPTION_CEILING = 1


class PointerOccurrence(NamedTuple):
    module: str
    constant: str
    section: str


class UnreadObject(AssertionError):
    pass


def pointer_occurrences(text: str) -> tuple[PointerOccurrence, ...]:
    boundaries = list(SECTION.finditer(text))
    found = []
    seen = set()
    for match in POINTER.finditer(text):
        owners = [
            index
            for index, heading in enumerate(boundaries)
            if heading.start() <= match.start()
        ]
        if not owners:
            continue
        index = owners[-1]
        identity = (match.group("module"), match.group("constant"), index)
        if identity in seen:
            continue
        seen.add(identity)
        end = boundaries[index + 1].start() if index + 1 < len(boundaries) else len(text)
        found.append(
            PointerOccurrence(
                match.group("module"),
                match.group("constant"),
                text[boundaries[index].start():end],
            )
        )
    return tuple(found)


def string_leaves(value: object, seen: set[int] | None = None) -> tuple[str, ...]:
    if isinstance(value, Enum):
        return ()
    if isinstance(value, str):
        return (value,)
    if value is None or isinstance(value, (int, float, complex, bytes, bool)):
        return ()
    visited = set() if seen is None else seen
    identity = id(value)
    if identity in visited:
        return ()
    visited.add(identity)
    if is_dataclass(value) and not isinstance(value, type):
        return tuple(
            leaf
            for field in fields(value)
            for leaf in string_leaves(getattr(value, field.name), visited)
        )
    if isinstance(value, dict):
        return tuple(
            leaf
            for item in value.items()
            for part in item
            for leaf in string_leaves(part, visited)
        )
    if isinstance(value, (tuple, list, set, frozenset)):
        return tuple(leaf for item in value for leaf in string_leaves(item, visited))
    return ()


def shingles(text: str) -> set[str]:
    words = normalized(text).split()
    return {
        " ".join(words[index:index + SHINGLE])
        for index in range(len(words) - SHINGLE + 1)
    }


def copied_leaves(value: object, section: str) -> tuple[tuple[str, int], ...]:
    leaves = string_leaves(value)
    if not leaves:
        raise UnreadObject("object yielded zero string leaves")
    prose = normalized(section)
    prose_shingles = shingles(prose)
    copied = []
    for leaf in leaves:
        clean = normalized(leaf)
        if not clean:
            continue
        words = clean.split()
        if len(words) < SHINGLE:
            occurrences = prose.count(clean)
            if occurrences:
                copied.append((leaf, occurrences))
        elif shingles(clean) & prose_shingles:
            copied.append((leaf, 1))
    return tuple(copied)


class EveryPointerResolves(unittest.TestCase):
    def test_every_pointer_resolves_before_any_object_is_read(self):
        missing = []
        for pointer in pointer_occurrences(CLAUDE_MD.read_text(encoding="utf-8")):
            try:
                module = importlib.import_module(pointer.module)
            except ImportError:
                missing.append(f"{pointer.module}.{pointer.constant}: module")
                continue
            if not hasattr(module, pointer.constant):
                missing.append(f"{pointer.module}.{pointer.constant}: constant")

        self.assertEqual([], missing)

    def test_limits_ish_candidates_are_deliberately_classified(self):
        candidates = {
            pointer.constant
            for pointer in pointer_occurrences(CLAUDE_MD.read_text(encoding="utf-8"))
            if LIMITS_ISH.search(pointer.constant)
        }

        self.assertEqual(set(LIMIT_CONSTANTS), candidates)


class LimitsPointersCopyNoRow(unittest.TestCase):
    def test_each_occurrence_is_clean_or_exactly_counted(self):
        self.assertLessEqual(len(EXCEPTIONS), EXCEPTION_CEILING)
        exception_map = {
            (module, constant, leaf): (occurrences, reason)
            for module, constant, leaf, occurrences, reason in EXCEPTIONS
        }
        seen_exceptions = set()
        findings = []
        for pointer in pointer_occurrences(CLAUDE_MD.read_text(encoding="utf-8")):
            if pointer.constant not in LIMIT_CONSTANTS:
                continue
            module = importlib.import_module(pointer.module)
            self.assertTrue(
                hasattr(module, pointer.constant),
                f"unresolved pointer: {pointer.module}.{pointer.constant}",
            )
            value = getattr(module, pointer.constant)
            try:
                copies = copied_leaves(value, pointer.section)
            except UnreadObject as error:
                findings.append(f"{pointer.module}.{pointer.constant}: unread: {error}")
                continue
            for leaf, occurrences in copies:
                key = (pointer.module, pointer.constant, leaf)
                if key in exception_map:
                    expected, _reason = exception_map[key]
                    if occurrences != expected:
                        findings.append(f"{key}: expected {expected} occurrences, found {occurrences}")
                    seen_exceptions.add(key)
                else:
                    findings.append(f"{pointer.module}.{pointer.constant}: {leaf!r}")

        self.assertEqual(set(exception_map), seen_exceptions, "stale declared exceptions")
        self.assertEqual([], findings)


class TheInstrumentIsLive(unittest.TestCase):
    def test_a_planted_verbatim_row_fires(self):
        row = "this planted declared limit has enough words to exercise the long comparison branch"
        self.assertTrue(copied_leaves((row,), f"### Example\n{row}"))

    def test_a_planted_nine_word_overlap_fires(self):
        row = "one two three four five six seven eight nine ten"
        self.assertTrue(copied_leaves((row,), "### Example\none two three four five six seven eight nine"))

    def test_a_section_that_only_points_passes(self):
        self.assertEqual(
            (),
            copied_leaves(
                ("a row absent from prose",),
                "### Example\n`sample.NOT_REACHED`",
            ),
        )

    def test_an_object_with_zero_leaves_is_unread(self):
        with self.assertRaisesRegex(UnreadObject, "zero string leaves"):
            copied_leaves((1, 2, 3), "### Example\n`sample.NOT_REACHED`")

    def test_a_frozen_dataclass_is_read_structurally(self):
        @dataclass(frozen=True)
        class Row:
            key: str
            limit: str

        self.assertEqual(
            ("row", "the structural leaf"),
            string_leaves(Row("row", "the structural leaf")),
        )


if __name__ == "__main__":
    unittest.main()
