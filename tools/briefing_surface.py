"""Derive and grade briefing surfaces in ``skills/*/SKILL.md``.

The population is derived twice. ``briefed_skill_paths`` finds skill files with
spawn-shaped prose, while ``surface_findings`` finds each detector line and
requires its own Markdown paragraph to name standing rule 6 and exactly one of
the three glossary kinds. A declaration therefore cannot hide a later,
undeclared surface in the same skill.

``briefing_surface.DECLARED_LIMITS`` is the complete boundary of the check. The
line detector is a floor: wording beyond its recognized forms is invisible. Fenced
examples are not prose and are not inspected. A declared kind is a membership
claim, not proof that the surface behaves as that kind or obtained an
independent context. The graded population is only ``skills/*/SKILL.md``;
briefing surfaces in tickets, ADRs, registries, or nested skill support files
remain ungraded.
"""

from __future__ import annotations

import re
from pathlib import Path

import run_grader


DETECTOR = re.compile(
    r"fan[ -]out|second reader|grader handoff|fresh (?:reader|checker|context|adversarial)|"
    r"non-authoring|a different (?:agent|context)",
    re.IGNORECASE,
)
KIND = re.compile(r"\b(Fan-out brief|Second reader|Grader handoff)\b", re.IGNORECASE)
RULE_NAME = re.compile(r"\bstanding rule 6\b", re.IGNORECASE)
RULE_HOME = re.compile(r"(?:\]\(\.\./\.\./AGENTS\.md(?:#[^)]*)?\)|\bAGENTS\.md\b)", re.IGNORECASE)
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
RULE_SIX = re.compile(r"(?ms)^6\. \*\*.*?(?=^7\. \*\*|\Z)")
LOCAL_COPY = re.compile(
    r"orchestrat(?:or|ing context)(?: alone)? writes (?:it|the\b)|sole writer|"
    r"return(?:s|ed)? (?:its|their|the) record[^.]{0,40}do not write|"
    r"one context never grades|fresh non-authoring|new non-authoring|"
    r"(?:try|briefed) to (?:break|disprove)[^.]{0,80}(?:not to )?confirm|"
    r"no subagent tool[^.]{0,160}one at a time in the main context",
    re.IGNORECASE | re.DOTALL,
)
SHARED_FLOORS = (
    (
        "missing prewrite floor",
        re.compile(r"Fan-out brief.*?writes .*?heading for every expected record", re.IGNORECASE),
    ),
    ("missing adversarial refutation floor", re.compile(r"refute rather than confirm", re.IGNORECASE)),
    (
        "missing serial fan-out floor",
        re.compile(r"parallelism is unavailable.*?one at a time.*?self-authored", re.IGNORECASE),
    ),
    (
        "missing no-second-context floor",
        re.compile(r"Second reader.*?does not complete.*?no second context", re.IGNORECASE),
    ),
    (
        "missing grader fallback floor",
        re.compile(
            r"Grader handoff.*?author.*?raw result.*?verbatim.*?(?:not|rather than) summarized",
            re.IGNORECASE,
        ),
    ),
    (
        "missing one-writer floor",
        re.compile(r"passes return them.*?sole writer", re.IGNORECASE),
    ),
)

DECLARED_LIMITS = (
    (
        "alternate delegation vocabulary",
        "the line detector is a floor and wording outside it is invisible",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "fenced examples",
        "fenced examples are not prose and are not inspected",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "truth of a declared kind or independence",
        "membership prose proves neither behavior nor a second context",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "briefing surfaces outside top-level skill files",
        "tickets, ADRs, registries, and nested support files remain ungraded",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
)


def _prose_lines(text: str) -> tuple[tuple[int, str], ...]:
    """Return one-based non-fenced lines without changing their coordinates."""

    prose = []
    closing: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)[0]
            if closing is None:
                closing = marker
            elif marker == closing:
                closing = None
            continue
        if closing is None:
            prose.append((number, line))
    return tuple(prose)


def _paragraphs(text: str) -> tuple[tuple[range, str], ...]:
    lines = text.splitlines()
    prose_numbers = {number for number, _line in _prose_lines(text)}
    paragraphs = []
    start: int | None = None
    for number, line in enumerate(lines, 1):
        belongs = number in prose_numbers and bool(line.strip())
        if belongs and start is None:
            start = number
        if start is not None and not belongs:
            paragraphs.append((range(start, number), "\n".join(lines[start - 1 : number - 1])))
            start = None
    if start is not None:
        paragraphs.append((range(start, len(lines) + 1), "\n".join(lines[start - 1 :])))
    return tuple(paragraphs)


def detector_lines(text: str) -> tuple[tuple[int, str], ...]:
    return tuple((number, line) for number, line in _prose_lines(text) if DETECTOR.search(line))


def briefed_skill_paths(skills: Path) -> tuple[Path, ...]:
    """Derive the top-level skill-file partition from detector hits."""

    return tuple(
        path
        for path in sorted(skills.glob("*/SKILL.md"))
        if detector_lines(path.read_text(encoding="utf-8"))
    )


def surface_findings(path: Path, text: str) -> tuple[str, ...]:
    """Report detector lines whose own paragraph lacks one valid declaration."""

    paragraphs = _paragraphs(text)
    findings = []
    detected_paragraphs: dict[int, str] = {}
    for number, _line in detector_lines(text):
        match = next(((span, body) for span, body in paragraphs if number in span), None)
        paragraph = match[1] if match is not None else ""
        kinds = {match.casefold() for match in KIND.findall(paragraph)}
        if (
            len(kinds) != 1
            or RULE_NAME.search(paragraph) is None
            or RULE_HOME.search(paragraph) is None
        ):
            findings.append(
                f"{path.as_posix()}:{number}: detector line is outside a declared briefing surface"
            )
        elif match is not None:
            detected_paragraphs[match[0].start] = paragraph
    for number, paragraph in detected_paragraphs.items():
        if LOCAL_COPY.search(paragraph):
            findings.append(f"{path.as_posix()}:{number}: briefing surface copies standing rule 6")
    return tuple(findings)


def standing_rule_findings(agents: str) -> tuple[str, ...]:
    """Report shared floors absent from standing rule 6 itself."""

    match = RULE_SIX.search(agents)
    if match is None:
        return ("missing standing rule 6",)
    rule = " ".join(match.group(0).split())
    return tuple(name for name, pattern in SHARED_FLOORS if pattern.search(rule) is None)
