"""Build the committed ICD-10-CM database that ``icd10-cpt`` verifies codes against.

    python tools/icd10_build.py <release-directory>

``<release-directory>`` holds the CMS release zips as downloaded, unextracted. The
two this reads are the code-descriptions zip (fixed-width order file) and the code
tables zip (tabular XML, alphabetic and external-cause indexes, Neoplasm Table,
and Table of Drugs and Chemicals). The addendum is deliberately not read.

The output is committed. That is unusual for a generated file and it was decided
deliberately: ``icd10-cpt`` is on the consumer's critical path, and a database
that has to be built before the skill works would make the skill's Markdown
insufficient on its own.

**What is not in here, and what that costs.**

- **Anything above the tabular's own text.** Coding *guidelines* — the FY2026
  official guidelines PDF — are not machine-readable here and are not shipped.
  This database answers "does this code exist, what does it mean, is it billable,
  and what notes govern it". It does not answer "is this the right code".

Stdlib only, like everything in ``tools/``. Its parsers are covered by
``test_icd10.py`` against committed excerpts, never against the shipped database.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

from console_codec import require_python_floor, use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "reference" / "icd10cm-2026.sqlite"

# Members inside the release zips. CMS has kept these names stable across recent
# fiscal years; a rename shows up as a clean KeyError from ``read_member`` rather
# than as a silently empty table.
ORDER_MEMBER = "Code Descriptions/icd10cm_order_2026.txt"
TABULAR_MEMBER = "Table and Index/icd10cm_tabular_2026.xml"
INDEX_MEMBER = "Table and Index/icd10cm_index_2026.xml"
EXTERNAL_CAUSE_INDEX_MEMBER = "Table and Index/icd10cm_eindex_2026.xml"
NEOPLASM_MEMBER = "Table and Index/icd10cm_neoplasm_2026.xml"
DRUG_MEMBER = "Table and Index/icd10cm_drug_2026.xml"

# The order file is fixed-width, and the columns are positional rather than
# delimited: five-digit order number, then the code, then the billable flag, then
# a 60-character short descriptor, then the long one running to end of line.
CODE_SLICE = slice(6, 13)
BILLABLE_COLUMN = 14
SHORT_SLICE = slice(16, 77)
LONG_SLICE = slice(77, None)

# The note kinds carried out of the tabular. ``inclusionTerm`` is the largest by
# far and the least directive; the four that actually constrain a code are
# excludes1, excludes2, useAdditionalCode and codeFirst.
NOTE_KINDS = (
    "inclusionTerm",
    "excludes1",
    "excludes2",
    "useAdditionalCode",
    "codeFirst",
    "codeAlso",
    "notes",
)


@dataclass(frozen=True)
class Code:
    code: str
    billable: bool
    long: str
    short: str | None  # None where the short descriptor says nothing the long one does not


@dataclass(frozen=True)
class Note:
    code: str
    kind: str
    text: str


@dataclass(frozen=True)
class IndexEntry:
    """One alphabetic-index term at its complete path."""

    term: str
    path: str
    code: str | None
    see: str | None
    see_also: str | None


def parse_order_line(line: str) -> Code:
    long = line[LONG_SLICE].strip()
    short = line[SHORT_SLICE].strip()
    return Code(
        code=line[CODE_SLICE].strip(),
        billable=line[BILLABLE_COLUMN] == "1",
        long=long,
        short=short if short != long else None,
    )


def parse_order_file(text: str) -> list[Code]:
    return [parse_order_line(line) for line in text.splitlines() if line.strip()]


def _flatten(element: ET.Element) -> str:
    """The note text with its inline markup dropped and whitespace collapsed.

    Tabular notes carry nested ``<i>`` and reference elements, so ``.text`` alone
    truncates a note at its first child — which reads as a shorter but valid note
    rather than as a parse failure.
    """
    return " ".join("".join(element.itertext()).split())


def parse_tabular(xml_text: str) -> list[Note]:
    root = ET.fromstring(xml_text)
    notes: list[Note] = []
    for diag in root.iter("diag"):
        name = diag.find("name")
        if name is None or not name.text:
            continue
        code = name.text.replace(".", "").strip().upper()
        # Direct children only. ``iter`` would pull a child code's notes up onto
        # its parent, and the whole point of the lookup's ancestor walk is that
        # the level a note sits on is information.
        for block in diag:
            if block.tag not in NOTE_KINDS:
                continue
            for entry in block:
                text = _flatten(entry)
                if text:
                    notes.append(Note(code=code, kind=block.tag, text=text))
    return notes


def parse_index(xml_text: str) -> list[IndexEntry]:
    """Read one CMS index or table into the shared lookup catalog.

    The alphabetic and external-cause indexes put a destination directly on a
    term. The Neoplasm Table and Table of Drugs and Chemicals put destinations
    in headed cells; each nonempty cell becomes a catalog entry whose final path
    step is its column heading.
    """
    root = ET.fromstring(xml_text)
    entries: list[IndexEntry] = []
    headings = {
        head.get("col"): _flatten(head)
        for head in root.findall("./indexHeading/head")
        if head.get("col") and _flatten(head)
    }

    def index_text(element: ET.Element) -> str:
        pieces = [element.text or ""]
        for child in element:
            if child.tag == "nemod":
                pieces.append(" ")
            pieces.extend(("".join(child.itertext()), child.tail or ""))
        return " ".join("".join(pieces).split())

    def walk(element: ET.Element, parents: tuple[str, ...]) -> None:
        title = element.find("title")
        if title is None:
            return
        term = index_text(title)
        if not term:
            return
        parts = (*parents, term)

        def direct_text(tag: str) -> str | None:
            child = element.find(tag)
            if child is None:
                return None
            value = _flatten(child)
            return value or None

        code = direct_text("code")
        see = direct_text("see")
        see_also = direct_text("seeAlso")
        if headings:
            if see or see_also:
                entries.append(
                    IndexEntry(term, " > ".join(parts), None, see, see_also)
                )
            for cell in element.findall("cell"):
                heading = headings.get(cell.get("col"))
                value = _flatten(cell)
                if not heading or not value or not value.strip("-"):
                    continue
                entries.append(
                    IndexEntry(
                        term=heading,
                        path=" > ".join((*parts, heading)),
                        code=value.replace(".", "").upper(),
                        see=None,
                        see_also=None,
                    )
                )
        else:
            entries.append(
                IndexEntry(
                    term=term,
                    path=" > ".join(parts),
                    code=code.replace(".", "").upper() if code else None,
                    see=see,
                    see_also=see_also,
                )
            )
        for child in element.findall("term"):
            walk(child, parts)

    for main_term in root.iter("mainTerm"):
        walk(main_term, ())
    return entries


def parse_version(xml_text: str) -> str | None:
    version = ET.fromstring(xml_text).find("version")
    if version is None or not version.text:
        return None
    return version.text.strip()


def release_string(version: str | None, source: Path) -> str:
    """What the database says it is when asked.

    The tabular's own ``<version>`` reads ``2026``, which is equally true of the
    October 2025 and the April 2026 revisions — and codes changed between them.
    So the zip that was actually read is named alongside it.
    """
    # Plain ASCII: this string is printed to a Windows console, where a dash
    # outside cp1252 comes back as a question mark and reads like corruption.
    return f"ICD-10-CM FY{version or 'unknown'}, built from {source.name}"


SCHEMA = """
DROP TABLE IF EXISTS code;
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS index_entry;
DROP TABLE IF EXISTS meta;

CREATE TABLE code (
    code     TEXT PRIMARY KEY,   -- no dots: Z6836, not Z68.36
    billable INTEGER NOT NULL,
    long     TEXT NOT NULL,
    short    TEXT
) WITHOUT ROWID;

CREATE TABLE note (
    code TEXT NOT NULL,          -- the level the note is written at, not the code it reaches
    kind TEXT NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX note_code ON note (code);

CREATE TABLE index_entry (
    term     TEXT NOT NULL COLLATE NOCASE,
    path     TEXT NOT NULL,
    code     TEXT,
    see      TEXT,
    see_also TEXT
);
CREATE INDEX index_entry_term ON index_entry (term COLLATE NOCASE);
CREATE INDEX index_entry_code ON index_entry (code);

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def write_database(
    path: Path,
    codes: list[Code],
    notes: list[Note],
    release: str,
    index: list[IndexEntry] | None = None,
    index_sources: dict[str, int] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT INTO code VALUES (?, ?, ?, ?)",
            [(c.code, int(c.billable), c.long, c.short) for c in codes],
        )
        connection.executemany(
            "INSERT INTO note VALUES (?, ?, ?)",
            [(n.code, n.kind, n.text) for n in notes],
        )
        index_rows = index or []
        connection.executemany(
            "INSERT INTO index_entry VALUES (?, ?, ?, ?, ?)",
            [(row.term, row.path, row.code, row.see, row.see_also) for row in index_rows],
        )
        meta = [
                ("release", release),
                ("codes", str(len(codes))),
                ("notes", str(len(notes))),
                ("index_entries", str(len(index_rows))),
        ]
        meta.extend(
            (f"index_{name}", str(count))
            for name, count in (index_sources or {}).items()
        )
        connection.executemany("INSERT INTO meta VALUES (?, ?)", meta)
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()


def read_member(zip_path: Path, member: str) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        return archive.read(member).decode("utf-8", errors="replace")


def find_zip(directory: Path, marker: str) -> Path:
    matches = sorted(p for p in directory.glob("*.zip") if marker in p.name.lower())
    if not matches:
        raise SystemExit(
            f"no zip matching {marker!r} in {directory}. "
            "Expected the CMS release zips, downloaded and left unextracted."
        )
    return matches[-1]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("release", type=Path, help="directory holding the CMS release zips")
    args = parser.parse_args(argv)

    if not args.release.is_dir():
        raise SystemExit(f"not a directory: {args.release}")

    descriptions = find_zip(args.release, "code-descriptions")
    tables = find_zip(args.release, "code-tables")

    tabular = read_member(tables, TABULAR_MEMBER)
    codes = parse_order_file(read_member(descriptions, ORDER_MEMBER))
    notes = parse_tabular(tabular)
    indexes = (
        parse_index(read_member(tables, INDEX_MEMBER)),
        parse_index(read_member(tables, EXTERNAL_CAUSE_INDEX_MEMBER)),
        parse_index(read_member(tables, NEOPLASM_MEMBER)),
        parse_index(read_member(tables, DRUG_MEMBER)),
    )
    index = [entry for source in indexes for entry in source]
    index_sources = dict(
        zip(("alphabetic", "external_cause", "neoplasm", "drug"), map(len, indexes))
    )
    release = release_string(parse_version(tabular), descriptions)

    write_database(DEFAULT_OUT, codes, notes, release, index, index_sources)
    size = DEFAULT_OUT.stat().st_size

    print(f"release  {release}")
    print(f"codes    {len(codes):,} ({sum(1 for c in codes if c.billable):,} billable)")
    print(f"notes    {len(notes):,}")
    print(f"index    {len(index):,} ({', '.join(f'{len(source):,}' for source in indexes)})")
    print(f"written  {DEFAULT_OUT.relative_to(REPO_ROOT)}  {size:,} bytes")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
