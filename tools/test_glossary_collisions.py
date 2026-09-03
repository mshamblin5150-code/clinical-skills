"""Declare the ruled candidates for glossary heading sense collisions.

Ticket #702 and ADR 0092. ``DECLARED_CANDIDATES`` owns the human verdict for
each mechanically derived fire; ``DECLARED_LIMITS`` owns what that arrangement
cannot establish. A fire is never itself a defect or a gate.
"""

from __future__ import annotations

import unittest
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

import test_glossary_terms
from test_glossary_terms import TERM_HEADING, glossary_definitions


CONTEXT = Path(__file__).resolve().parent.parent / "CONTEXT.md"
CLAUDE = CONTEXT.with_name("CLAUDE.md")


class Verdict(str, Enum):
    COLLISION = "collision"
    NARROWING = "narrowing"


@dataclass(frozen=True)
class Candidate:
    heading: str
    verdict: Verdict
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, Verdict):
            raise TypeError("candidate verdict must be a Verdict")


@dataclass(frozen=True)
class HeadingCoverage:
    headings: tuple[str, ...]
    avoid_row_count: int
    unread_count: int

    @property
    def parsed_count(self) -> int:
        return len(self.headings)


DECLARED_CANDIDATES = (
    Candidate(
        "Declared",
        Verdict.COLLISION,
        "The tier is a note value; the Declared compounds name statements held as named things.",
    ),
    Candidate(
        "Drift",
        Verdict.COLLISION,
        "The bare term is a clinical finding lost across note sections; Corpus drift is divergence between the corpus and tree.",
    ),
    Candidate(
        "Topic",
        Verdict.COLLISION,
        "The bare term is a clinician's subject; Catalog topic is a document's own wording, and neither narrows the other.",
    ),
    Candidate(
        "Citation",
        Verdict.COLLISION,
        "The bare term is a tracker reference; the Citation compounds are bibliographic.",
    ),
    Candidate(
        "Disposition",
        Verdict.COLLISION,
        "The bare term is where a correction's fix lands; an Evidence disposition "
        "is how a declared limit's row is supported. A third sense is recorded in "
        "the bare entry's own body -- research_ledger's RECENCY verdicts -- so the "
        "word carries three and none narrows another.",
    ),
    Candidate(
        "Assertion",
        Verdict.NARROWING,
        "A Promoted assertion is an assertion whose bar has become binary.",
    ),
    Candidate(
        "Publish",
        Verdict.NARROWING,
        "A Publish route is one command form that performs a publish. Ruled again "
        "2026-09-01: the reason held only after Publish was widened to cover a "
        "tracker record, which the entry had previously excluded outright, so a "
        "Publish route did not perform a publish and the narrowing was between two "
        "senses that denied each other.",
    ),
    Candidate(
        "Corpus",
        Verdict.NARROWING,
        "Corpus drift is one change state of the guideline corpus.",
    ),
    Candidate(
        "Span",
        Verdict.NARROWING,
        "A Null span is a span retired after two reads found nothing.",
    ),
    Candidate(
        "Recommendation",
        Verdict.NARROWING,
        "The compound headings name records, sweeps, labels, or omissions of recommendations.",
    ),
    Candidate(
        "Packet",
        Verdict.NARROWING,
        "A Startable packet is a packet whose sequencing conditions are clear.",
    ),
)

PROSE_CLAUSES = {
    "Declared": (
        "Distinct from **Declared non-source**, **Declared limit**, "
        "**Declared rationale**, and **Declared no-binding**: each is something "
        "stated on purpose and held as a named thing, and none is a value in a note."
    ),
    "Citation": (
        "Distinct from **Citation key**, **Legal citation**, and **Stated citation**, "
        "which are bibliographic rather than tracker references."
    ),
    "Corpus drift": (
        "Distinct from **Drift**, the clinical finding carried into the Objective "
        "and absent from the Assessment and the Plan."
    ),
}

DECLARED_LIMITS = (
    "Two compound headings that share a word do not fire without a bare heading; Section read and Section number are the confirmed instance.",
    "The candidate predicate cannot decide whether a fire is a sense collision or a narrowing.",
    "The narrowing verdicts are a hand-kept list whose distinction from an allowlist is claimed rather than proved.",
    "A required distinction clause can be present and still be wrong.",
    "A glossary term that collides only with prose does not fire; Form coverage is the live instance.",
    "Only CONTEXT.md is inspected; a glossary in another file is outside this population.",
    "The independent coverage floor counts _Avoid_ rows; a future glossary entry without one can remain unread.",
)


def heading_coverage(text: str) -> HeadingCoverage:
    """Report the parsed population, independent denominator, and unread remainder."""
    matches = list(TERM_HEADING.finditer(text))
    avoid_row_count = sum(line.startswith("_Avoid_:") for line in text.splitlines())
    return HeadingCoverage(
        headings=tuple(match.group("term") for match in matches),
        avoid_row_count=avoid_row_count,
        unread_count=max(avoid_row_count - len(matches), 0),
    )


def glossary_headings(text: str) -> list[str]:
    """Return parsed headings after refusing a partial coverage report."""
    coverage = heading_coverage(text)
    if coverage.unread_count:
        noun = "entry" if coverage.unread_count == 1 else "entries"
        raise AssertionError(
            f"{coverage.unread_count} glossary {noun} unread by TERM_HEADING"
        )
    return list(coverage.headings)


def candidate_headings(text: str) -> set[str]:
    """Return bare headings whose word is also a word in another heading."""
    headings = glossary_headings(text)
    return {
        heading
        for heading in headings
        if len(heading.split()) == 1
        and any(
            heading.casefold() in {word.casefold() for word in other.split()}
            for other in headings
            if other != heading
        )
    }


def assert_candidate_population(
    text: str,
    declared: Sequence[Candidate] = DECLARED_CANDIDATES,
) -> None:
    """Raise when derived fires and human declarations differ in either direction."""
    counts = Counter(row.heading for row in declared)
    duplicates = sorted(heading for heading, count in counts.items() if count != 1)
    if duplicates:
        raise AssertionError("duplicate declared glossary candidates: " + ", ".join(duplicates))

    invalid = [
        row.heading
        for row in declared
        if not isinstance(row.verdict, Verdict) or not row.reason.strip()
    ]
    if invalid:
        raise AssertionError("invalid declared glossary candidates: " + ", ".join(invalid))

    fires = candidate_headings(text)
    headings = set(counts)
    findings: list[str] = []
    unruled = sorted(fires - headings)
    if unruled:
        findings.append("unruled glossary candidates: " + ", ".join(unruled))
    stale = sorted(headings - fires)
    if stale:
        findings.append("declared glossary candidates no longer fire: " + ", ".join(stale))
    if findings:
        raise AssertionError("\n".join(findings))


def markdown_section(text: str, heading: str) -> str:
    """Return one exact ``###`` section body, excluding the next peer heading."""
    marker = f"### {heading}\n"
    start = text.index(marker) + len(marker)
    end = text.find("\n### ", start)
    return text[start:] if end == -1 else text[start:end]


class CandidatePopulationIsDerived(unittest.TestCase):
    def test_the_context_inventory_reports_its_denominator_and_unread_remainder(self) -> None:
        coverage = heading_coverage(CONTEXT.read_text(encoding="utf-8"))
        self.assertGreater(coverage.avoid_row_count, 0)
        self.assertEqual(coverage.parsed_count, coverage.avoid_row_count)
        self.assertEqual(coverage.unread_count, 0)

    def test_a_bare_heading_fires_when_another_heading_uses_its_word(self) -> None:
        text = """\
**Alpha**:
The bare sense.
_Avoid_: first

**Alpha detail**:
The compound sense.
_Avoid_: second

**Binding**:
The bare sense.
_Avoid_: third

**Declared no-binding**:
The hyphenated shape is one word and does not fire Binding.
_Avoid_: fourth
"""

        self.assertEqual(candidate_headings(text), {"Alpha"})

    def test_an_unparsed_heading_like_line_refuses_partial_coverage(self) -> None:
        partial = """\
**Alpha**:
The bare sense.
_Avoid_: first

**Alpha detail**:
The compound sense.
_Avoid_: second

**Unread**: trailing text hides this line from the glossary grammar.
The intended entry still carries its structural denominator row.
_Avoid_: third
"""
        coverage = heading_coverage(partial)
        self.assertEqual(
            (coverage.parsed_count, coverage.avoid_row_count, coverage.unread_count),
            (2, 3, 1),
        )
        with self.assertRaisesRegex(AssertionError, r"1 glossary entry unread"):
            candidate_headings(partial)

    def test_bold_leading_prose_outside_the_heading_grammar_is_not_a_gate(self) -> None:
        text = """\
**Alpha**:
The bare sense.
_Avoid_: first

**Alpha detail**:
The compound sense.
_Avoid_: second

**Note**: emphasized prose, not a TERM_HEADING.
"""
        self.assertEqual(candidate_headings(text), {"Alpha"})


class DeclaredCandidatePopulationIsBound(unittest.TestCase):
    def test_every_fire_has_one_human_verdict_and_every_row_still_fires(self) -> None:
        assert_candidate_population(
            CONTEXT.read_text(encoding="utf-8"),
            DECLARED_CANDIDATES,
        )

    def test_deleting_a_row_makes_its_live_fire_unruled(self) -> None:
        declared = tuple(row for row in DECLARED_CANDIDATES if row.heading != "Declared")
        with self.assertRaisesRegex(AssertionError, r"unruled.*Declared"):
            assert_candidate_population(CONTEXT.read_text(encoding="utf-8"), declared)

    def test_renaming_a_heading_makes_its_declaration_stale(self) -> None:
        renamed = CONTEXT.read_text(encoding="utf-8").replace(
            "**Declared**:",
            "**Declared tier**:",
            1,
        )
        with self.assertRaisesRegex(AssertionError, r"no longer fire.*Declared"):
            assert_candidate_population(renamed)

    def test_a_new_fire_is_unruled_and_not_automatically_a_collision(self) -> None:
        new_fire = CONTEXT.read_text(encoding="utf-8") + """\

**Anchor**:
The bare sense.

**Anchor detail**:
The compound sense.
"""
        with self.assertRaises(AssertionError) as raised:
            assert_candidate_population(new_fire)

        self.assertIn("unruled glossary candidates: Anchor", str(raised.exception))
        self.assertNotIn("collision", str(raised.exception))


class RuledCollisionClausesStayAtTheirAnchors(unittest.TestCase):
    def test_each_clause_remains_in_its_own_entry_body(self) -> None:
        definitions = glossary_definitions(CONTEXT.read_text(encoding="utf-8"))
        for entry, clause in PROSE_CLAUSES.items():
            with self.subTest(entry=entry):
                self.assertEqual(len(definitions[entry]), 1)
                self.assertIn(clause, definitions[entry][0])


class DeclaredObjectsHaveOneDocumentedOwner(unittest.TestCase):
    def test_claude_points_to_both_objects_and_copies_no_row(self) -> None:
        section = markdown_section(
            CLAUDE.read_text(encoding="utf-8"),
            "Glossary sense collisions",
        )
        self.assertIn("test_glossary_collisions.DECLARED_CANDIDATES", section)
        self.assertIn("test_glossary_collisions.DECLARED_LIMITS", section)
        for row in DECLARED_CANDIDATES:
            with self.subTest(heading=row.heading):
                self.assertNotIn(row.reason, section)
        for limit in DECLARED_LIMITS:
            with self.subTest(limit=limit[:30]):
                self.assertNotIn(limit, section)

    def test_the_older_check_points_here_and_keeps_its_prose_hole_open(self) -> None:
        prose = test_glossary_terms.__doc__ or ""
        self.assertIn("test_glossary_collisions.py", prose)
        self.assertIn("heading-against-prose", prose)
        self.assertIn("Form coverage", prose)


if __name__ == "__main__":
    unittest.main()
