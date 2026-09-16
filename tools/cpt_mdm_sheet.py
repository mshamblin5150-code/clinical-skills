#!/usr/bin/env python3
"""Compare independent CPT MDM reads, grade their sheet, or derive a private CPT receipt."""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from git_paths import GitPathError, read_path_records


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = ROOT / "reference" / "procedure-codes-2026.sqlite"
ENTRY = re.compile(
    r"^## Entry: ([a-z0-9-]+)\n"
    r"Locator: (CPT Professional (\d{4}), p\. (\d+))\n"
    r"(?:(?:Agreement date: (\d{4}-\d{2}-\d{2})\n)"
    r"(?:SHA-256: ([0-9a-f]{64})\n))?"
    r"```text\n(.*?)\n```\s*$",
    re.S | re.M,
)
DECLARED_LIMITS = (
    "Exact agreement and digests cannot prove that either independent reader looked at the rendered page.",
    "The receipt derives database identity and date boundaries; it cannot prove authenticated reading.",
)
REQUIRED_ENTRIES = frozenset({
    "mdm-selection", "mdm-two-of-three", "table-footnote",
    "table-straightforward", "table-low", "table-moderate", "table-high",
    "definition-problem", "definition-problem-addressed", "problem-counting-guidance",
    "condition-management-risk", "definition-minimal",
    "definition-self-limited", "definition-stable-chronic", "definition-acute-uncomplicated",
    "definition-acute-uncomplicated-hospital", "definition-stable-acute",
    "definition-chronic-exacerbation", "definition-undiagnosed-new",
    "definition-acute-systemic", "definition-acute-complicated-injury",
    "definition-severe-exacerbation", "definition-threat-life-function",
    "definition-data-analyzed", "definition-data-test", "definition-data-unique",
    "definition-combination-data", "definition-external", "definition-external-clinician",
    "definition-discussion", "definition-independent-historian",
    "definition-independent-interpretation", "definition-appropriate-source",
    "definition-risk", "definition-morbidity", "definition-social-determinants",
    "definition-surgery-minor-major", "definition-surgery-elective-emergency",
    "definition-surgery-risk-factors", "definition-intensive-monitoring",
    "definition-parenteral-controlled",
})


@dataclass(frozen=True)
class Entry:
    identifier: str
    locator: str
    edition: int
    page: int
    text: str
    agreed: str | None
    digest: str | None


def normalized(value: str) -> str:
    return " ".join(value.split())


def digest(value: str) -> str:
    return hashlib.sha256(normalized(value).encode("utf-8")).hexdigest()


def read_entries(content: str, *, graded: bool = False) -> dict[str, Entry]:
    content = content.replace("\r\n", "\n")
    entries: dict[str, Entry] = {}
    chunks = re.split(r"(?=^## Entry: )", content, flags=re.M)
    if len(chunks) < 2:
        raise ValueError("no CPT MDM entries")
    for chunk in chunks[1:]:
        match = ENTRY.fullmatch(chunk.strip() + "\n")
        if not match:
            raise ValueError("unreadable entry or locator")
        identifier, locator, edition, page, agreed, expected, body = match.groups()
        if identifier in entries:
            raise ValueError(f"duplicate entry: {identifier}")
        if not normalized(body):
            raise ValueError(f"empty entry: {identifier}")
        if graded:
            if not agreed or not expected:
                raise ValueError(f"{identifier}: missing agreement date or digest")
            date.fromisoformat(agreed)
            if digest(body) != expected:
                raise ValueError(f"{identifier}: text digest changed")
        entries[identifier] = Entry(
            identifier, locator, int(edition), int(page), body, agreed, expected
        )
    return entries


def source_metadata(database: Path) -> dict[str, str]:
    connection = sqlite3.connect(database)
    try:
        row = connection.execute(
            "SELECT id, title, edition, isbn, sha256, effective_date FROM source WHERE system = 'CPT'"
        ).fetchone()
    finally:
        connection.close()
    if row is None or not all(row):
        raise ValueError("CPT source row is incomplete")
    return dict(zip(("id", "title", "edition", "isbn", "sha256", "effective_date"), row, strict=True))


def compare(first: Path, second: Path, output: Path, agreement_date: str,
            database: Path = DEFAULT_DATABASE) -> None:
    date.fromisoformat(agreement_date)
    if first.resolve() == second.resolve():
        raise ValueError("two independent transcript paths are required")
    left, right = read_entries(first.read_text(encoding="utf-8")), read_entries(second.read_text(encoding="utf-8"))
    if left.keys() != right.keys():
        raise ValueError("entry populations disagree: " + ", ".join(sorted(left.keys() ^ right.keys())))
    missing = REQUIRED_ENTRIES - left.keys()
    if missing:
        raise ValueError("MDM source coverage is incomplete: " + ", ".join(sorted(missing)))
    for identifier, entry in left.items():
        other = right[identifier]
        if entry.locator != other.locator or normalized(entry.text) != normalized(other.text):
            raise ValueError(f"{identifier}: independent transcriptions disagree")
    edition = {entry.edition for entry in left.values()}
    if len(edition) != 1:
        raise ValueError("mixed CPT editions")
    year = edition.pop()
    source = source_metadata(database)
    if date.fromisoformat(source["effective_date"]).year != year:
        raise ValueError("transcribed edition differs from CPT source row")
    lines = [
        f"# CPT E/M MDM {year}", "",
        f"Book: {source['title']}",
        f"Edition: {source['edition']}",
        f"ISBN (VitalSource ebook): {source['isbn']}",
        "Permission: Internal repository storage of the MDM grid and dependent E/M guideline definitions under the maintainer's AMA permission; no other CPT text is licensed by this sheet.",
        "",
    ]
    if year == 2026:
        lines.insert(5, "Print ISBN on copyright page: 978-1-64016-322-5")
    for entry in left.values():
        lines.extend((
            f"## Entry: {entry.identifier}",
            f"Locator: {entry.locator}",
            f"Agreement date: {agreement_date}",
            f"SHA-256: {digest(entry.text)}",
            "```text", entry.text.strip(), "```", "",
        ))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def grade_content(content: str, database: Path = DEFAULT_DATABASE) -> dict[str, Entry]:
    entries = read_entries(content, graded=True)
    missing = REQUIRED_ENTRIES - entries.keys()
    if missing:
        raise ValueError("MDM source coverage is incomplete: " + ", ".join(sorted(missing)))
    editions = {entry.edition for entry in entries.values()}
    if len(editions) != 1:
        raise ValueError("mixed CPT editions")
    year = editions.pop()
    if not content.startswith(f"# CPT E/M MDM {year}\n"):
        raise ValueError("sheet edition header disagrees with entries")
    source = source_metadata(database)
    if date.fromisoformat(source["effective_date"]).year != year:
        raise ValueError("sheet edition differs from CPT source row")
    for field in (f"Book: {source['title']}", f"Edition: {source['edition']}", f"ISBN (VitalSource ebook): {source['isbn']}", "Permission:"):
        if field not in content.split("## Entry:", 1)[0]:
            raise ValueError(f"sheet is missing {field}")
    return entries


def grade(path: Path, database: Path = DEFAULT_DATABASE) -> dict[str, Entry]:
    return grade_content(path.read_text(encoding="utf-8"), database)


def grade_staged(database: Path = DEFAULT_DATABASE) -> None:
    changes = read_path_records(
        ROOT, "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=ACDM", "-z"
    )
    sheets = [name for name in changes if re.fullmatch(r"reference/cpt-em-mdm-\d{4}\.md", name)]
    if not sheets:
        raise ValueError("no staged CPT MDM edition sheet")
    for name in sheets:
        staged = subprocess.run(
            ["git", "show", f":{name}"], cwd=ROOT, capture_output=True,
        )
        if staged.returncode:
            raise ValueError(f"staged sheet missing or removed: {name}")
        grade_content(staged.stdout.decode("utf-8"), database)


def receipt_fields(database: Path) -> dict[str, object]:
    source = source_metadata(database)
    effective = date.fromisoformat(source["effective_date"])
    return {
        "schema": 1, "source_id": source["id"], "source_edition": source["edition"],
        "source_sha256": source["sha256"],
        "valid_through": date(effective.year, 12, 31).isoformat(),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sheet", nargs="?", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("FIRST", "SECOND"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--agreement-date")
    parser.add_argument("--write-receipt", type=Path)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args(argv)
    try:
        if args.staged:
            if args.sheet or args.compare or args.output or args.write_receipt:
                raise ValueError("--staged takes no other mode")
            grade_staged(args.database)
        elif args.compare:
            if not args.output or not args.agreement_date or args.sheet or args.write_receipt:
                raise ValueError("comparison requires --output and --agreement-date only")
            compare(*args.compare, args.output, args.agreement_date, args.database)
            grade(args.output, args.database)
        elif args.write_receipt:
            if args.sheet or args.output or args.agreement_date:
                raise ValueError("receipt mode takes only --write-receipt and --database")
            destination = args.write_receipt.resolve()
            sessions = (ROOT / "scratch" / "sessions").resolve()
            if not destination.is_relative_to(sessions) or len(destination.relative_to(sessions).parts) < 2:
                raise ValueError("private CPT receipt must be inside this checkout's scratch/sessions/<key>/")
            import json

            fields = receipt_fields(args.database)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(fields, indent=2) + "\n", encoding="utf-8")
        elif args.sheet:
            grade(args.sheet, args.database)
        else:
            raise ValueError("provide a sheet, --compare, or --write-receipt")
    except (OSError, UnicodeError, ValueError, sqlite3.Error, GitPathError) as error:
        print(f"cpt-mdm-sheet: BLOCKED: {error}")
        return 1
    print("cpt-mdm-sheet: PASS")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
