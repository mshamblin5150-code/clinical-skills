"""Check imports against the fixed, book-located CPT 2026 reference population.

The reference is selected independently of each candidate CSV; numbering gaps
are never used as evidence. Coverage limits belong to ``DECLARED_LIMITS``.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from cpt_identity import CPT_CODE


REFERENCE = Path(__file__).resolve().parent.parent / "reference" / "cpt-population-2026.csv"

DECLARED_LIMITS = (
    "The reference population checks named book identities across sections and known omissions, "
    "not every CPT identity. An omitted code outside that population can pass; full extraction "
    "and descriptor agreement remain separate requirements.",
    "The check does not re-read the licensed book, establish medical necessity, or verify "
    "descriptors, dates, and instructions.",
)


@dataclass(frozen=True)
class Coverage:
    expected: int
    missing: tuple[str, ...]

    def report(self) -> str:
        return (
            f"CPT reference population: {self.expected - len(self.missing)}/{self.expected}; "
            f"unread remainder: {len(self.missing)}"
            + ("; " + ", ".join(self.missing) if self.missing else "")
        )


def reference_codes() -> set[str]:
    """Read the committed book identities, refusing absent or malformed evidence."""
    codes: set[str] = set()
    with REFERENCE.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["section", "code", "printed_page", "document"]:
            raise ValueError("CPT reference population has invalid columns")
        for row in reader:
            code = row["code"] or ""
            if (
                not re.fullmatch(CPT_CODE, code)
                or code in codes
                or not row["section"]
                or not (row["printed_page"] or "").isdigit()
                or not (row["document"] or "").endswith(".html")
            ):
                raise ValueError(f"CPT reference population has an invalid row: {code!r}")
            codes.add(code)
    if not codes:
        raise ValueError("CPT reference population is empty")
    return codes


def coverage(codes: set[str]) -> Coverage:
    expected = reference_codes()
    return Coverage(len(expected), tuple(sorted(expected - codes)))
