"""Keep the measured hanging Word methods on typed late binding."""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple


class MeasuredMethodSet(NamedTuple):
    methods: tuple[str, ...]
    ceiling: str


class Finding(NamedTuple):
    path: str
    line: int
    method: str


LATE_BOUND_WORD_METHODS = MeasuredMethodSet(
    methods=("ExportAsFixedFormat2", "SaveAs2"),
    ceiling=(
        "This is the list measured on one machine, not a rule about COM; a clean "
        "scan establishes only that no listed methods are invoked dynamically."
    ),
)


def survey(root: Path) -> tuple[Finding, ...]:
    patterns = {
        method: re.compile(
            rf"\.[ \t]*{re.escape(method)}[ \t]*\(", re.IGNORECASE
        )
        for method in LATE_BOUND_WORD_METHODS.methods
    }
    findings = []
    for path in sorted(root.glob("*.ps1")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for method, pattern in patterns.items():
                if pattern.search(line):
                    findings.append(Finding(path.name, line_number, method))
    return tuple(findings)
