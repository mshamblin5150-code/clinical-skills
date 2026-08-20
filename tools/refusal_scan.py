#!/usr/bin/env python3
"""Grade the mechanical refusal-record row in ``icd10-cpt`` worksheets.

The scanner reads only ``--- NOT CODED, NOTHING ESTABLISHED IT ---``. A refusal
inside that block must weld ``NOT CODED`` to its code and nonempty descriptor,
state what would establish the code, and name what the encounter supports instead.
It cannot judge whether descriptor text is official. Codes in the differential are
outside the block and do not inflate the refusal count.

Default output is counts only. ``--show`` prints code-level findings and is PHI on
the same terms as the repo's other scanners. Exit 0 means the scanned records are
complete, 1 means at least one finding, and 2 means no worksheet refusal was
scanned or the input could not be read.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8


CODE = r"(?:[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?|[0-9]{5})"
REFUSAL_HEADING = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?---[ \t]*NOT CODED, NOTHING ESTABLISHED IT[ \t]*---[ \t]*$",
    re.IGNORECASE,
)
MARK = re.compile(rf"^[ \t]*NOT CODED:[ \t]*({CODE})\b[ \t]+(\S.*)$")
NEEDS = re.compile(r"^[ \t]*needs:[ \t]*\S", re.IGNORECASE)
SUBSTITUTE = re.compile(r"^[ \t]*proposed instead:[ \t]*\S", re.IGNORECASE)
MARK_MENTION = re.compile(r"^[ \t]*NOT CODED:", re.IGNORECASE)
MARKDOWN_HEADING = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]+|---[ \t]+\S.*---[ \t]*$)"
)
ENTRY = re.compile(
    rf"^[ \t]*(?:ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+({CODE})\b",
    re.IGNORECASE,
)
NOT_FOR_ENTRY = re.compile(r"NOT FOR ENTRY[ \t]*$", re.IGNORECASE)

MISSING_NEEDS = "missing needs"
MISSING_SUBSTITUTE = "missing proposed instead"
MISSING_BLOCK = "missing refusal block"
PROPOSED_AND_REFUSED = "proposed and refused"
MALFORMED_MARK = "malformed NOT CODED mark"


@dataclass(frozen=True)
class Refusal:
    code: str
    descriptor: str
    has_needs: bool
    has_substitute: bool


@dataclass(frozen=True)
class Finding:
    kind: str
    code: str = "unknown"


@dataclass(frozen=True)
class Worksheet:
    refusals: tuple[Refusal, ...]
    proposed: frozenset[str]
    differential: frozenset[str]
    malformed_marks: int = 0
    has_block: bool = False


@dataclass(frozen=True)
class Scan:
    worksheets: int
    with_block: int
    refusals: int
    per_worksheet: tuple[int, ...]
    findings: tuple[Finding, ...] = ()

    @property
    def subjects(self) -> int:
        return self.refusals


def _block_lines(lines: list[str]) -> tuple[list[str], bool]:
    start = next((i for i, line in enumerate(lines) if REFUSAL_HEADING.search(line)), None)
    if start is None:
        return [], False

    block: list[str] = []
    for line in lines[start + 1 :]:
        if MARKDOWN_HEADING.match(line):
            break
        block.append(line)
    return block, True


def _entry_sets(lines: list[str]) -> tuple[set[str], set[str]]:
    proposed: set[str] = set()
    differential: set[str] = set()
    in_differential = False

    for line in lines:
        if "DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY" in line.upper():
            in_differential = True
            continue
        if REFUSAL_HEADING.search(line):
            break

        match = ENTRY.match(line)
        if match is None:
            continue
        code = match.group(1).upper()
        if in_differential or NOT_FOR_ENTRY.search(line):
            differential.add(code)
        else:
            proposed.add(code)

    return proposed, differential


def read_worksheet(text: str) -> Worksheet:
    lines = text.splitlines()
    block, has_block = _block_lines(lines)
    proposed, differential = _entry_sets(lines)

    marks: list[tuple[int, re.Match[str]]] = []
    malformed = 0
    for index, line in enumerate(block):
        match = MARK.match(line)
        if match is not None:
            marks.append((index, match))
        elif MARK_MENTION.match(line):
            malformed += 1

    refusals: list[Refusal] = []
    for position, (index, match) in enumerate(marks):
        end = marks[position + 1][0] if position + 1 < len(marks) else len(block)
        fields = block[index + 1 : end]
        refusals.append(
            Refusal(
                code=match.group(1).upper(),
                descriptor=match.group(2).strip(),
                has_needs=any(NEEDS.match(line) for line in fields),
                has_substitute=any(SUBSTITUTE.match(line) for line in fields),
            )
        )

    return Worksheet(
        refusals=tuple(refusals),
        proposed=frozenset(proposed),
        differential=frozenset(differential),
        malformed_marks=malformed,
        has_block=has_block,
    )


def worksheet_findings(sheet: Worksheet) -> list[Finding]:
    findings: list[Finding] = []
    if not sheet.has_block:
        findings.append(Finding(MISSING_BLOCK))
    findings.extend(Finding(MALFORMED_MARK) for _ in range(sheet.malformed_marks))
    for refusal in sheet.refusals:
        if not refusal.has_needs:
            findings.append(Finding(MISSING_NEEDS, refusal.code))
        if not refusal.has_substitute:
            findings.append(Finding(MISSING_SUBSTITUTE, refusal.code))
        if refusal.code in sheet.proposed:
            findings.append(Finding(PROPOSED_AND_REFUSED, refusal.code))
    return findings


def survey(sheets: list[Worksheet]) -> Scan:
    findings = tuple(finding for sheet in sheets for finding in worksheet_findings(sheet))
    return Scan(
        worksheets=len(sheets),
        with_block=sum(sheet.has_block for sheet in sheets),
        refusals=sum(len(sheet.refusals) for sheet in sheets),
        per_worksheet=tuple(len(sheet.refusals) for sheet in sheets),
        findings=findings,
    )


def format_report(result: Scan, source: str, show: bool = False) -> str:
    lines = [
        f"refusal scan: {source}",
        f"worksheets                       {result.worksheets}",
        f"worksheets carrying block        {result.with_block}",
        f"refusal records                  {result.refusals}",
        "records per worksheet             "
        + ",".join(str(count) for count in result.per_worksheet),
        f"findings                         {len(result.findings)}",
    ]
    if show:
        lines.extend(f"{finding.kind}: {finding.code}" for finding in result.findings)
    return "\n".join(lines)


def read_worksheets(directory: Path) -> list[str]:
    return [
        path.read_text(encoding="utf-8")
        for path in sorted(directory.glob("*.md"))
        if path.name.lower() != "readme.md"
    ]


def main(argv: list[str]) -> int:
    show = False
    args = list(argv)
    if "--show" in args:
        show = True
        args.remove("--show")
    if len(args) != 1:
        print("usage: python tools/refusal_scan.py <worksheet-directory> [--show]")
        return 2

    directory = Path(args[0])
    if not directory.is_dir():
        print(f"no directory named {directory.name}")
        return 2

    texts = read_worksheets(directory)
    if not texts:
        print(f"no worksheets found in {directory.name}")
        return 2

    result = survey([read_worksheet(text) for text in texts])
    print(format_report(result, source=directory.name, show=show))
    if result.findings:
        return 1
    if result.subjects == 0:
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
