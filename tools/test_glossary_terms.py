"""Require every ``**Term**:`` heading in ``CONTEXT.md`` to be unique.

Ticket #499 and ADR 0041. Redundant definitions are a mechanical deletion;
contested definitions are resolved under ADR 0037 by a clinician rather than by
file position.

What this cannot reach
----------------------

A single-word heading whose word appears in another heading is narrowed by
``test_glossary_collisions.py``. A term heading that collides with a word live
only in the file's prose remains a heading-against-prose collision, and neither
check sees it; ADR 0088's ``Form coverage`` entry is the live instance. This
check also does not decide whether a unique definition is correct, protect this
module from deletion, or inspect any glossary other than ``CONTEXT.md``.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


TERM_HEADING = re.compile(
    r"^\*\*(?P<term>[^*\r\n]+)\*\*:[ \t]*\r?$",
    re.MULTILINE,
)
BLOCK_BOUNDARY = re.compile(
    r"^(?:#{1,6}[ \t]+|\*\*[^*\r\n]+\*\*:[ \t]*\r?$)",
    re.MULTILINE,
)
CONTEXT = Path(__file__).resolve().parent.parent / "CONTEXT.md"


def glossary_definitions(text: str) -> dict[str, list[str]]:
    """Return each term's exact post-heading body slices in file order."""
    definitions: dict[str, list[str]] = {}
    for heading in TERM_HEADING.finditer(text):
        boundary = BLOCK_BOUNDARY.search(text, heading.end())
        end = len(text) if boundary is None else boundary.start()
        body = text[heading.end() : end]
        definitions.setdefault(heading.group("term"), []).append(body)
    return definitions


def assert_glossary_terms_unique(text: str) -> None:
    """Raise with the ruled remedy for every repeated term heading."""
    findings: list[str] = []
    for term, bodies in glossary_definitions(text).items():
        if len(bodies) == 1:
            continue
        if len(set(bodies)) == 1:
            findings.append(
                f"redundant glossary term {term!r}: byte-identical bodies; delete one"
            )
        else:
            findings.append(
                f"contested glossary term {term!r}: definitions differ; ADR 0037 — "
                "the higher ADR number keeps the term, and the losing concept is renamed "
                "by a clinician"
            )
    if findings:
        raise AssertionError("\n".join(findings))


CLEAN_GLOSSARY = """\
### First section

**Alpha**:
The first definition.
_Avoid_: first

**Beta**:
The second definition.
_Avoid_: second
"""


class EveryGlossaryTermIsDefinedOnce(unittest.TestCase):
    def test_context_has_no_repeated_term_heading(self) -> None:
        assert_glossary_terms_unique(CONTEXT.read_bytes().decode("utf-8"))


class TheInstrumentIsLive(unittest.TestCase):
    def test_a_clean_glossary_passes(self) -> None:
        assert_glossary_terms_unique(CLEAN_GLOSSARY)

    def test_a_redundant_duplicate_fails_and_names_the_mechanical_remedy(self) -> None:
        duplicate = """\

### Second section

**Alpha**:
The first definition.
_Avoid_: first

**Gamma**:
The third definition.
_Avoid_: third
"""
        with self.assertRaisesRegex(
            AssertionError,
            r"redundant.*Alpha.*delete one",
        ):
            assert_glossary_terms_unique(CLEAN_GLOSSARY + duplicate)

    def test_a_contested_duplicate_fails_and_names_the_ruled_remedy(self) -> None:
        duplicate = """\

### Second section

**Alpha**:
A competing definition.
_Avoid_: first
"""
        with self.assertRaisesRegex(
            AssertionError,
            r"contested.*Alpha.*ADR 0037.*higher ADR number keeps the term.*"
            r"losing concept is renamed",
        ):
            assert_glossary_terms_unique(CLEAN_GLOSSARY + duplicate)

    def test_a_body_that_differs_only_by_a_blank_line_is_contested(self) -> None:
        duplicate = """\

### Second section

**Alpha**:

The first definition.
_Avoid_: first
"""
        with self.assertRaisesRegex(AssertionError, r"contested.*Alpha"):
            assert_glossary_terms_unique(CLEAN_GLOSSARY + duplicate)

    def test_a_body_that_differs_only_by_a_trailing_blank_line_is_contested(self) -> None:
        duplicate = """\

### Second section

**Alpha**:
The first definition.
_Avoid_: first


**Gamma**:
The third definition.
_Avoid_: third
"""
        with self.assertRaisesRegex(AssertionError, r"contested.*Alpha"):
            assert_glossary_terms_unique(CLEAN_GLOSSARY + duplicate)

    def test_crlf_headings_are_inspected(self) -> None:
        contested = (CLEAN_GLOSSARY + """\

### Second section

**Alpha**:
A competing definition.
_Avoid_: first
""").replace("\n", "\r\n")
        with self.assertRaisesRegex(AssertionError, r"contested.*Alpha"):
            assert_glossary_terms_unique(contested)


if __name__ == "__main__":
    unittest.main()
