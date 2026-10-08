"""Derive the shift summary's generation lines from physical tier items."""

from __future__ import annotations

import re
from pathlib import Path

from run_grader import EvidenceDisposition

ITEM = re.compile(r"^FILLED·(asserted|proposed)\s*(.*)$")
CLOSER = re.compile(r"^(?:(?:DERIVED|FLAG|GAPS|UNKNOWN|PROPOSED)\b|```|---|#{1,6}\s)")
NUMBER = re.compile(r"^\s*\d+\.\s+(.*)$")
DECLARED_LIMITS = (
    ("unnumbered legacy tier bundles",
     "One physical tier opener with unnumbered continuations counts as one item; prose bundles are not split by inference.",
     EvidenceDisposition.BEHAVIOR),
)


def generation(text: str) -> dict[str, tuple[str, ...]]:
    result: dict[str, list[str]] = {"asserted": [], "proposed": []}
    active = None
    for line in text.splitlines():
        opener = ITEM.match(line)
        if opener:
            active, content = opener.groups()
            content = content.strip()
            if content and content.casefold() not in {"none", "none.", "0"}:
                number = NUMBER.match(content)
                result[active].append(number[1] if number else content)
            continue
        if CLOSER.match(line):
            active = None
        if active and (number := NUMBER.match(line)):
            result[active].append(number[1])
    return {name: tuple(items) for name, items in result.items()}


def generation_line(name: str, counts: dict[str, tuple[str, ...]]) -> str:
    return f"GENERATION: {name} | FILLED·asserted={len(counts['asserted'])} | FILLED·proposed={len(counts['proposed'])}"


def check(run: Path, paths: tuple[Path, ...], terminal: bool, show: bool = False) -> tuple[bool, bool, str]:
    expected = [generation_line(path.name, generation(path.read_text(encoding="utf-8"))) for path in paths]
    lines = expected.copy()
    if show:
        for path in paths:
            lines.extend(f"  {path.name}: proposed {item}" for item in generation(path.read_text(encoding="utf-8"))["proposed"])
    summary = run / "shift-summary.md"
    if not summary.exists():
        lines.append("the shift summary: incomplete coverage - absent" if terminal else "the shift summary: NOT GRADED - absent")
        return False, terminal, "\n".join(lines)
    try:
        actual = [line for line in summary.read_text(encoding="utf-8").splitlines() if line.startswith("GENERATION:")]
        failed = sorted(actual) != sorted(expected)
    except (OSError, UnicodeError):
        failed = True
    lines.append(f"the shift summary: {'finding' if failed else 'clean'}")
    return failed, False, "\n".join(lines)
