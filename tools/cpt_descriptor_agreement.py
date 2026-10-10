"""Agree two independent CPT descriptor readings into the record the build verifies.

ADR 0269 rebuilds the CPT descriptor set from two readers of the rendered CPT
Professional 2026 book: reader 1 extracts each descriptor from the reader's page
structure, and reader 2 transcribes it from rendered-page screenshots. This command
joins the two readings in the owning checkout's ``scratch/cpt-2026/``:

    python tools/cpt_descriptor_agreement.py            # report only
    python tools/cpt_descriptor_agreement.py --write    # write agreed.csv and agreement.json

Inputs are ``reader-1.csv`` and ``reader-2.csv`` (``code``, ``description`` and
optional build columns) and, once disagreements have been read on their rendered
destination pages, ``resolutions.csv`` (``code``, ``description``,
``printed_page``). Every run rewrites ``disagreements.csv``, the settlement work
list naming each code the readers read differently and both readings.

A code read by only one reader, or a disagreement with no resolution, is the
unread remainder; nothing is written while it is nonzero. ``--write`` then writes
``agreed.csv``, whose descriptor is the agreed reading or the page resolution and
whose other columns come from reader 1, and ``agreement.json``, the record
``procedure_codes_build.verify_cpt_agreement`` checks. It prints the record's
SHA-256 for ``--cpt-agreement-sha256``.

Output is counts only and never a descriptor, because the readings are licensed
text kept under the maintainer's written AMA permission; the work list and the
written files stay in the private scratch directory.

Exit status: 0 for a clean agreement (written with ``--write``), 1 for a finding,
and 2 when the readings could not be read or the unread remainder is nonzero. A
finding wins over the remainder.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import procedure_codes_build
from console_codec import require_python_floor, use_utf8
from procedure_codes_build import (
    AGREEMENT_METHODS,
    DESCRIPTOR_DEFECTS,
    Entry,
    _text_sha256,
    descriptor_defects,
    read_cpt,
)
from repo_root import InsideCheckout, ensure_outside_checkout, scratch_root
from run_grader import format_unread_remainder

READINGS = {"reader_1": "reader-1.csv", "reader_2": "reader-2.csv"}
RESOLUTIONS = "resolutions.csv"
WORK_LIST = "disagreements.csv"
AGREED = "agreed.csv"
RECORD = "agreement.json"
AGREED_COLUMNS = ("code", "description", "short_description", "effective_date", "termination_date", "category", "locator")

# What a clean agreement does not establish.
DECLARED_LIMITS = (
    (
        "independence",
        "The command compares two files; it cannot tell whether reader 2 was transcribed "
        "without sight of reader 1. Independence is a property of how the readings were made.",
    ),
    (
        "shared misreading",
        "Two readers that misread a descriptor the same way agree, and the agreed text carries "
        "the misreading. Only a disagreement is sent back to the rendered page.",
    ),
    (
        "resolutions",
        "A resolution is taken as recorded: its printed page is required, but the command does "
        "not re-read that page.",
    ),
    (
        "population",
        "The denominator is the union of codes either reader read. A code neither reader reached "
        "is invisible here; the build's comparison with the database it replaces is the check "
        "for that.",
    ),
    (
        "reader-1 columns",
        "Only the descriptor is compared. The agreed CSV takes every other column from reader 1 "
        "alone, and derives a blank category from the code's shape.",
    ),
    (
        "controls",
        "A control is graded only when the agreed set carries its code. An absent control is a "
        "population question, which the build settles against the database it replaces.",
    ),
)

FINDINGS = (
    "resolution without a printed page",
    "resolution for a code the readers agree on",
    "resolution for a code no reader read",
    "control disagrees with its digest",
)

WRITTEN = (AGREED, RECORD)


class NotRead(Exception):
    """An input the command could not read."""


@dataclass
class Agreement:
    reader_1: dict[str, Entry]
    reader_2: dict[str, Entry]
    resolutions: dict[str, dict[str, str]]
    agreed: dict[str, str] = field(default_factory=dict)
    conflicts: set[str] = field(default_factory=set)
    unresolved: set[str] = field(default_factory=set)
    findings: dict[str, set[str]] = field(default_factory=lambda: {name: set() for name in FINDINGS})
    defects: dict[str, set[str]] = field(default_factory=dict)

    @property
    def only_1(self) -> set[str]:
        return self.reader_1.keys() - self.reader_2.keys()

    @property
    def only_2(self) -> set[str]:
        return self.reader_2.keys() - self.reader_1.keys()

    @property
    def unread(self) -> int:
        return len(self.only_1) + len(self.only_2) + len(self.unresolved)

    @property
    def finding_count(self) -> int:
        return sum(map(len, self.findings.values())) + sum(map(len, self.defects.values()))


def category(code: str) -> str:
    """CPT category by code shape, including MAAA administrative codes."""
    return {"F": "II", "M": "MAAA", "T": "III", "U": "PLA"}.get(code[-1], "I")


def read_reading(path: Path) -> dict[str, Entry]:
    if not path.is_file():
        raise NotRead(f"reading absent: {path}")
    try:
        entries = read_cpt(path, validate_descriptors=False)
    except (OSError, UnicodeError, ValueError) as error:
        raise NotRead(f"{path.name}: {error}") from error
    codes = {entry.code: entry for entry in entries}
    if len(codes) != len(entries):
        raise NotRead(f"{path.name}: duplicate CPT codes")
    return codes


def read_resolutions(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    try:
        # Read as the build reads its CSVs, so a line break inside a quoted resolution
        # reaches the record exactly as the build will read the agreed CSV back.
        with io.StringIO(path.read_text(encoding="utf-8-sig"), newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not {"code", "description", "printed_page"} <= set(reader.fieldnames):
                raise NotRead(f"{path.name} requires code, description, printed_page")
            rows = [{key: (row.get(key) or "").strip() for key in ("code", "description", "printed_page")} for row in reader]
    except (OSError, UnicodeError) as error:
        raise NotRead(f"{path.name}: {error}") from error
    resolved = {row["code"]: row for row in rows}
    if len(resolved) != len(rows):
        raise NotRead(f"{path.name}: a code is resolved twice")
    return resolved


def agree(reader_1: dict[str, Entry], reader_2: dict[str, Entry], resolutions: dict[str, dict[str, str]]) -> Agreement:
    result = Agreement(reader_1, reader_2, resolutions)
    both = reader_1.keys() & reader_2.keys()
    for code in sorted(both):
        first, second = reader_1[code].description, reader_2[code].description
        if first == second:
            result.agreed[code] = first
            continue
        result.conflicts.add(code)
        row = resolutions.get(code)
        if row is None or not row["description"]:
            result.unresolved.add(code)
        elif not row["printed_page"]:
            result.findings["resolution without a printed page"].add(code)
        else:
            result.agreed[code] = row["description"]
    for code in resolutions.keys() - result.conflicts:
        name = "resolution for a code the readers agree on" if code in both else "resolution for a code no reader read"
        result.findings[name].add(code)
    agreed_entries = [replace(reader_1[code], description=text) for code, text in result.agreed.items()]
    result.defects = descriptor_defects(agreed_entries)
    for code, expected in procedure_codes_build.CPT_CONTROL_SHA256.items():
        if code in result.agreed and _text_sha256(result.agreed[code]) != expected:
            result.findings["control disagrees with its digest"].add(code)
    return result


def _csv_text(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def _replace(path: Path, text: str) -> None:
    sibling = path.with_name(f"{path.name}.{os.getpid()}.building")
    sibling.write_text(text, encoding="utf-8", newline="")
    os.replace(sibling, path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_work_list(root: Path, result: Agreement) -> None:
    rows = [(code, result.reader_1[code].description, result.reader_2[code].description) for code in sorted(result.conflicts)]
    _replace(root / WORK_LIST, _csv_text(("code", "reader_1", "reader_2"), rows))


def write_agreement(root: Path, result: Agreement) -> Path:
    rows = []
    for code in sorted(result.agreed):
        source = result.reader_1[code]
        rows.append((
            code,
            result.agreed[code],
            source.short_description or "",
            source.effective_date or "",
            source.termination_date or "",
            source.category or category(code),
            source.locator or "",
        ))
    _replace(root / AGREED, _csv_text(AGREED_COLUMNS, rows))
    record = {
        **{
            key: {
                "file": READINGS[key],
                "sha256": _sha256(root / READINGS[key]),
                "codes_read": len(reading),
                "method": AGREEMENT_METHODS[key],
            }
            for key, reading in (("reader_1", result.reader_1), ("reader_2", result.reader_2))
        },
        "agreed": {"file": AGREED, "sha256": _sha256(root / AGREED)},
        "disagreement_count": len(result.conflicts),
        "resolutions": [
            {"code": code, "description": result.resolutions[code]["description"], "printed_page": result.resolutions[code]["printed_page"]}
            for code in sorted(result.conflicts)
        ],
        "unread_remainder": [],
    }
    _replace(root / RECORD, json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    return root / RECORD


def format_report(result: Agreement) -> str:
    both = len(result.reader_1.keys() & result.reader_2.keys())
    unpaged = len(result.findings["resolution without a printed page"])
    rows = [
        ("reader 1 codes read", len(result.reader_1)),
        ("reader 2 codes read", len(result.reader_2)),
        ("only reader 1", len(result.only_1)),
        ("only reader 2", len(result.only_2)),
        ("agreeing", both - len(result.conflicts)),
        ("disagreements", len(result.conflicts)),
        ("settled on a printed page", len(result.conflicts) - len(result.unresolved) - unpaged),
        ("unsettled", len(result.unresolved)),
        *((name, len(codes)) for name, codes in result.findings.items()),
        *((f"agreed descriptors {shape}", len(result.defects.get(shape, ()))) for shape in DESCRIPTOR_DEFECTS),
    ]
    lines = ["cpt-descriptor-agreement", *(f"  {label:<46}{count}" for label, count in rows)]
    lines.append(f"  {format_unread_remainder(result.unread)}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, help="rebuild directory; defaults to the owning checkout's scratch/cpt-2026")
    parser.add_argument("--write", action="store_true", help="write agreed.csv and agreement.json when clean")
    args = parser.parse_args(argv)
    root = (args.root or scratch_root() / "cpt-2026").resolve()
    try:
        # The readings are licensed text: inside a checkout they belong only under scratch/.
        ensure_outside_checkout(root, permitted=(scratch_root(),), detail="CPT readings are licensed text.")
        reader_1 = read_reading(root / READINGS["reader_1"])
        reader_2 = read_reading(root / READINGS["reader_2"])
        resolutions = read_resolutions(root / RESOLUTIONS)
    except (NotRead, InsideCheckout) as error:
        print(f"cpt-descriptor-agreement: DID NOT SCAN: {error}", file=sys.stderr)
        return 2
    result = agree(reader_1, reader_2, resolutions)
    write_work_list(root, result)
    print(format_report(result))
    status = 0
    if result.finding_count:
        print("cpt-descriptor-agreement: FINDING; nothing written", file=sys.stderr)
        status = 1
    elif not (reader_1.keys() & reader_2.keys()):
        print("cpt-descriptor-agreement: DID NOT SCAN: no code was read by both readers", file=sys.stderr)
        status = 2
    elif result.unread:
        print("cpt-descriptor-agreement: unread remainder is not zero; nothing written", file=sys.stderr)
        status = 2
    if status:
        if args.write:
            # A refused write leaves no earlier record standing beside inputs it no longer matches.
            for name in WRITTEN:
                (root / name).unlink(missing_ok=True)
        return status
    if args.write:
        record = write_agreement(root, result)
        print(f"  agreement sha256 {_sha256(record)}")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
