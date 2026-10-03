"""Build the 2026 CPT/HCPCS procedure-code database.

The CMS Alpha-Numeric HCPCS quarterly public-use file supplies Level II codes and
modifiers. Licensed CPT content is accepted as a normalized CSV because a print
or VitalSource CPT Professional purchase is not itself a machine-readable data
feed. The database records both books as authorities while keeping the exact
machine source and effective dates auditable.

    python tools/procedure_codes_build.py \
        --hcpcs october-2026-alpha-numeric-hcpcs-file.zip \
        --hcpcs-effective 2026-10-01 \
        --cpt licensed-cpt-2026.csv

The CPT CSV requires ``code`` and ``description`` columns. Optional columns are
``short_description``, ``effective_date``, ``termination_date``, ``category``,
and ``locator``. Dates are ISO ``YYYY-MM-DD``. The input is a licensed internal
source; this repository's authorization does not make it a portable public data
feed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import sys
import zipfile
from contextlib import closing
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "reference" / "procedure-codes-2026.sqlite"

CPT_BOOK = {
    "id": "cpt-professional-2026",
    "system": "CPT",
    "title": "CPT Professional 2026",
    "edition": "Professional Edition 2026",
    "isbn": "9781640163232",
    "publisher": "American Medical Association",
    "url": "https://bookshelf.vitalsource.com/reader/books/9781640163232",
}

HCPCS_BOOK = {
    "id": "hcpcs-level-ii-professional-2026",
    "system": "HCPCS",
    "title": "HCPCS 2026 Level II Professional Edition",
    "edition": "Professional Edition 2026",
    "isbn": "9781640163317",
    "publisher": "Elsevier",
    "url": "https://bookshelf.vitalsource.com/reader/books/9781640163317",
}

# Exact normalized 2026 book controls. Keep licensed descriptor text in the
# private extraction files, not another tracked copy in this public repository.
CPT_CONTROL_SHA256 = {
    "87804": "026ff07a631b2cfe059a7d739aa20ee85de410fe947cbf84df50bc0e3d410f38",
    "86486": "ac9a083b7c3feca4c9c5a94d0752777d7d3242a2f8dccf1caad33e9d7dd988fe",
    "97169": "9f341305b07468be6bdb653eb6ec92e9b63f8a9fc403851977127c3d1ed1d1a3",
    "45825": "4c3a6a49ebcd5ecabd6078af56fd98ac9b79ac187c144cf6e5768ce8a42c6337",
}

# What a CPT import that builds, or builds verified, does not establish.
DECLARED_LIMITS = (
    (
        "descriptor guard",
        "The guard refuses three text shapes: a descriptor whose text before its final '; ' "
        "equals another CPT code's complete descriptor, a ';;', and a trailing colon. A stacked "
        "descriptor whose stacked stem matches no complete descriptor in the same input, and a "
        "descriptor filed under the wrong parent family, both pass it; the second reader settles "
        "family membership on the rendered page (ADR 0269).",
    ),
    (
        "verified flag",
        "cpt_descriptors = verified establishes that two recorded readings and the agreed CSV "
        "match their recorded digests, that every disagreement names a rendered-page "
        "resolution, that the named controls match their digests, and that the agreed set holds "
        "every CPT code of the database it replaces. It does not re-read the book: each "
        "resolution is taken as recorded.",
    ),
    (
        "controls",
        "The controls are digests of single descriptors, so a failing control names the code "
        "that disagrees and never what the rendered page prints. The digests were recorded "
        "before the full readings existed; a rebuild whose agreed text disagrees with one "
        "re-reads that code on the rendered page before either is trusted.",
    ),
)

AGREEMENT_METHODS = {"reader_1": "page_structure", "reader_2": "rendered_screenshots"}
# Rebuild evidence rows take their own system value so a consumer selecting the CPT
# machine-source row by system never meets them.
CPT_EVIDENCE_SYSTEM = "CPT rebuild evidence"
CPT_EVIDENCE_SOURCE_IDS = {
    "reader_1": "ama-cpt-2026-reader-1",
    "reader_2": "ama-cpt-2026-reader-2",
    "agreement": "ama-cpt-2026-agreement",
}


@dataclass(frozen=True)
class Entry:
    system: str
    code: str
    kind: str
    description: str
    short_description: str | None
    effective_date: str | None
    termination_date: str | None
    action_code: str | None
    category: str | None
    locator: str | None
    source_id: str


def _date(value: str | None, label: str) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise ValueError(f"{label} must be YYYY-MM-DD: {value!r}") from error


def _compact_date(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if not re.fullmatch(r"\d{8}", value):
        raise ValueError(f"CMS date must be YYYYMMDD: {value!r}")
    return _date(f"{value[:4]}-{value[4:6]}-{value[6:]}", "CMS date")


def parse_hcpcs_line(line: str) -> Entry | None:
    """Parse one 293-column CMS contractor record.

    Record 3 is a Level II procedure code and record 7 is a two-character
    modifier. The public file currently carries no continuation records, but a
    4 or 8 is refused by the caller rather than silently losing descriptor text.
    """
    if not line.strip():
        return None
    if len(line) < 11:
        raise ValueError(f"HCPCS record is {len(line)} columns; expected at least 11")
    record_id = line[10]
    if record_id in {"4", "8"}:
        raise ValueError("HCPCS continuation records require the stateful file parser")
    if record_id not in {"3", "7"}:
        return None
    if len(line) < 293:
        raise ValueError(f"HCPCS first record is {len(line)} columns; expected at least 293")
    kind = "code" if record_id == "3" else "modifier"
    code = (line[:5] if kind == "code" else line[3:5]).strip().upper()
    expected = r"[A-Z][0-9]{4}" if kind == "code" else r"[A-Z0-9]{2}"
    if not re.fullmatch(expected, code):
        raise ValueError(f"invalid HCPCS {kind}: {code!r}")
    description = line[11:91].strip()
    short = line[91:119].strip()
    if not description:
        raise ValueError(f"HCPCS {code} has no long description")
    return Entry(
        system="HCPCS",
        code=code,
        kind=kind,
        description=description,
        short_description=short if short and short != description else None,
        effective_date=_compact_date(line[276:284]),
        termination_date=_compact_date(line[284:292]),
        action_code=line[292].strip() or None,
        category=None,
        locator=None,
        source_id="cms-hcpcs-2026",
    )


def _hcpcs_member(archive: zipfile.ZipFile) -> str:
    matches = [
        name
        for name in archive.namelist()
        if name.lower().endswith(".txt")
        and "anweb" in name.lower()
        and "transaction" not in name.lower()
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one HCPCS ANWEB text member, found {matches}")
    return matches[0]


def read_hcpcs(path: Path) -> list[Entry]:
    with zipfile.ZipFile(path) as archive:
        text = archive.read(_hcpcs_member(archive)).decode("cp1252")
    entries: list[Entry] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if len(line) >= 11 and line[10] in {"4", "8"}:
            if not entries:
                raise ValueError(f"{path.name}:{number}: orphaned HCPCS continuation")
            continuation_kind = "code" if line[10] == "4" else "modifier"
            continuation_code = (
                line[:5] if continuation_kind == "code" else line[3:5]
            ).strip().upper()
            previous = entries[-1]
            if (previous.kind, previous.code) != (continuation_kind, continuation_code):
                raise ValueError(
                    f"{path.name}:{number}: continuation for {continuation_code!r} "
                    f"does not follow {(previous.kind, previous.code)!r}"
                )
            fragment = line[11:].strip()
            if not fragment:
                raise ValueError(f"{path.name}:{number}: empty HCPCS continuation")
            entries[-1] = replace(previous, description=f"{previous.description} {fragment}")
            continue
        try:
            entry = parse_hcpcs_line(line)
        except ValueError as error:
            raise ValueError(f"{path.name}:{number}: {error}") from error
        if entry is not None:
            entries.append(entry)
    return entries


def read_cpt_text(text: str, label: str, *, validate_descriptors: bool = True) -> list[Entry]:
    entries: list[Entry] = []
    with io.StringIO(text, newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"code", "description"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CPT CSV requires columns: {', '.join(sorted(required))}")
        for number, row in enumerate(reader, start=2):
            code = (row.get("code") or "").strip()
            description = (row.get("description") or "").strip()
            if not re.fullmatch(r"(?:\d{5}|\d{4}[FTU])", code):
                raise ValueError(f"{label}:{number}: invalid CPT code {code!r}")
            if not description:
                raise ValueError(f"{label}:{number}: CPT {code} has no description")
            short = (row.get("short_description") or "").strip()
            entries.append(
                Entry(
                    system="CPT",
                    code=code,
                    kind="code",
                    description=description,
                    short_description=short if short and short != description else None,
                    effective_date=_date(row.get("effective_date"), "effective_date"),
                    termination_date=_date(row.get("termination_date"), "termination_date"),
                    action_code=None,
                    category=(row.get("category") or "").strip() or None,
                    locator=(row.get("locator") or "").strip() or None,
                    source_id="ama-cpt-2026-licensed",
                )
            )
    if validate_descriptors:
        bad = {code for codes in descriptor_defects(entries).values() for code in codes}
        if bad:
            raise ValueError(f"{label}: defective CPT descriptors: {', '.join(sorted(bad))}")
    return entries


DESCRIPTOR_DEFECTS = ("stacked", "double semicolon", "colon-terminated")


def descriptor_defects(entries: list[Entry]) -> dict[str, set[str]]:
    """Codes carrying each refused descriptor shape, keyed by ``DESCRIPTOR_DEFECTS``."""
    descriptions = {entry.description for entry in entries}
    found: dict[str, set[str]] = {shape: set() for shape in DESCRIPTOR_DEFECTS}
    for entry in entries:
        text = entry.description
        if "; " in text and text.rsplit("; ", 1)[0] in descriptions:
            found["stacked"].add(entry.code)
        if ";;" in text:
            found["double semicolon"].add(entry.code)
        if text.endswith(":"):
            found["colon-terminated"].add(entry.code)
    return found


def read_cpt(path: Path, *, validate_descriptors: bool = True) -> list[Entry]:
    return read_cpt_text(path.read_text(encoding="utf-8-sig"), path.name, validate_descriptors=validate_descriptors)


@dataclass(frozen=True)
class CptEvidence:
    """The checked files behind a verified CPT descriptor set."""

    reader_1: Path
    reader_2: Path
    agreed: Path
    agreement: Path


def verify_cpt_controls(descriptions: dict[str, str]) -> None:
    """Refuse a control whose descriptor disagrees with its rendered-page digest."""
    bad = {
        code
        for code, expected in CPT_CONTROL_SHA256.items()
        if _text_sha256(descriptions.get(code)) != expected
    }
    if bad:
        raise ValueError(f"CPT 2026 controls disagree with rendered pages: {', '.join(sorted(bad))}")


def verify_cpt_agreement(root: Path, agreed_path: Path, record_path: Path) -> CptEvidence:
    """Check the two complete readings against the agreed CSV and page resolutions."""
    try:
        return _verify_cpt_agreement(root, agreed_path, record_path)
    except KeyError as error:
        raise ValueError(f"CPT agreement record is missing field {error}") from error
    except (TypeError, AttributeError) as error:
        raise ValueError(f"CPT agreement record is malformed: {error}") from error


def _verify_cpt_agreement(root: Path, agreed_path: Path, record_path: Path) -> CptEvidence:
    root = root.resolve()
    record_path = record_path.resolve()
    agreed_path = agreed_path.resolve()
    for path in (record_path, agreed_path):
        if path.parent != root or not path.is_file():
            raise ValueError(f"CPT agreement input must exist in {root}: {path}")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    paths: list[Path] = []
    readings: list[dict[str, str]] = []
    for key in ("reader_1", "reader_2", "agreed"):
        method = AGREEMENT_METHODS.get(key)
        item = record[key]
        path = (root / item["file"]).resolve()
        if path.parent != root or not path.is_file():
            raise ValueError(f"recorded CPT input absent or outside {root}: {item['file']}")
        if _sha256(path) != item["sha256"]:
            raise ValueError(f"recorded CPT input digest disagrees: {item['file']}")
        if method and item["method"] != method:
            raise ValueError(f"{key} must use {method}")
        entries = read_cpt(path, validate_descriptors=key == "agreed")
        codes = {entry.code: entry.description for entry in entries}
        if len(codes) != len(entries):
            raise ValueError(f"duplicate CPT codes in {item['file']}")
        if method and item["codes_read"] != len(entries):
            raise ValueError(f"{key} codes_read disagrees with {item['file']}")
        readings.append(codes)
        paths.append(path)
    if paths[2] != agreed_path:
        raise ValueError("agreement record names a different agreed CSV")
    if len(set(paths)) != 3:
        raise ValueError("CPT readers and agreed CSV must be distinct files")
    first, second, agreed = readings
    if first.keys() != second.keys() or first.keys() != agreed.keys():
        raise ValueError("CPT reader code populations differ")
    if record["unread_remainder"]:
        raise ValueError(f"CPT unread remainder: {record['unread_remainder']}")
    conflicts = {code for code in first if first[code] != second[code]}
    resolutions = record["resolutions"]
    resolved = {row["code"]: row for row in resolutions}
    if len(resolved) != len(resolutions):
        raise ValueError("CPT agreement record resolves a code twice")
    if conflicts != resolved.keys():
        unsettled = conflicts ^ resolved.keys()
        raise ValueError(f"unsettled CPT disagreements: {', '.join(sorted(unsettled))}")
    if record["disagreement_count"] != len(conflicts):
        raise ValueError(
            f"CPT agreement record counts {record['disagreement_count']} disagreements; "
            f"the readers disagree on {len(conflicts)}"
        )
    for code in first:
        if code in conflicts:
            row = resolved[code]
            if not row.get("printed_page") or agreed[code] != row["description"]:
                raise ValueError(f"CPT {code} has no matching rendered-page resolution")
        elif agreed[code] != first[code]:
            raise ValueError(f"CPT {code} differs from both agreeing readers")
    return CptEvidence(*paths, record_path)


SCHEMA = """
DROP TABLE IF EXISTS code;
DROP TABLE IF EXISTS source;
DROP TABLE IF EXISTS meta;

CREATE TABLE source (
    id TEXT PRIMARY KEY,
    system TEXT NOT NULL,
    title TEXT NOT NULL,
    edition TEXT NOT NULL,
    isbn TEXT,
    publisher TEXT NOT NULL,
    url TEXT,
    machine_source TEXT,
    sha256 TEXT,
    effective_date TEXT,
    license_scope TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE code (
    system TEXT NOT NULL,
    code TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('code', 'modifier')),
    description TEXT NOT NULL,
    short_description TEXT,
    effective_date TEXT,
    termination_date TEXT,
    action_code TEXT,
    category TEXT,
    locator TEXT,
    source_id TEXT NOT NULL REFERENCES source(id),
    PRIMARY KEY (system, kind, code)
) WITHOUT ROWID;
CREATE INDEX code_description ON code (system, description);

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
"""


def _sha256(path: Path | None) -> str | None:
    if path is None:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _text_sha256(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reference_cpt_codes(path: Path) -> set[str]:
    """Read the previously shipped code population before replacing its database."""
    if not path.is_file():
        raise ValueError(f"CPT reference database absent: {path}")
    with closing(sqlite3.connect(path)) as connection:
        codes = {row[0] for row in connection.execute("SELECT code FROM code WHERE system='CPT'")}
    if not codes:
        raise ValueError(f"CPT reference database has no codes: {path}")
    return codes


def write_database(
    path: Path,
    entries: list[Entry],
    hcpcs_path: Path,
    hcpcs_effective: str,
    cpt_machine_source: str | Path | None,
    cpt_sha256: str | None = None,
    cpt_complete: bool = False,
    cpt_evidence: CptEvidence | None = None,
    cpt_reference: Path | None = None,
) -> None:
    """Write the database; a verified build passes ``verify_cpt_agreement``'s evidence.

    ``cpt_reference`` is the database being replaced, whose CPT code population a verified
    set must contain; it defaults to the committed database.
    """
    if cpt_evidence is not None:
        if not cpt_complete:
            raise ValueError("verified CPT descriptors require --cpt-complete")
        accepted = {(entry.code, entry.description) for entry in read_cpt(cpt_evidence.agreed)}
        supplied = {(entry.code, entry.description) for entry in entries if entry.system == "CPT"}
        if accepted != supplied:
            raise ValueError("CPT database rows disagree with agreed CSV")
        verify_cpt_controls(dict(accepted))
        shipped = reference_cpt_codes(cpt_reference or DEFAULT_OUT)
        missing = shipped - {code for code, _ in accepted}
        if missing:
            raise ValueError(f"agreed CPT CSV omits previously shipped codes: {', '.join(sorted(missing))}")
    if isinstance(cpt_machine_source, Path):
        cpt_sha256 = cpt_sha256 or _sha256(cpt_machine_source)
        cpt_machine_source = cpt_machine_source.name
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        cpt_authority = (
            CPT_BOOK["title"],
            CPT_BOOK["edition"],
            CPT_BOOK["isbn"],
            CPT_BOOK["publisher"],
            CPT_BOOK["url"],
        )
        cpt_permission = "Internal repository storage under the maintainer's written AMA permission"
        sources = [
            (
                "cms-hcpcs-2026",
                "HCPCS",
                HCPCS_BOOK["title"],
                HCPCS_BOOK["edition"],
                HCPCS_BOOK["isbn"],
                "Centers for Medicare & Medicaid Services; book published by Elsevier",
                HCPCS_BOOK["url"],
                hcpcs_path.name,
                _sha256(hcpcs_path),
                hcpcs_effective,
                "CMS public-use machine file; book used as the licensed human authority",
            ),
            (
                "ama-cpt-2026-licensed",
                "CPT",
                *cpt_authority,
                cpt_machine_source,
                cpt_sha256,
                "2026-01-01",
                cpt_permission,
            ),
        ]
        if cpt_evidence is not None:
            for field, source_id in CPT_EVIDENCE_SOURCE_IDS.items():
                evidence = getattr(cpt_evidence, field)
                sources.append(
                    (source_id, CPT_EVIDENCE_SYSTEM, *cpt_authority, evidence.name, _sha256(evidence), "2026-01-01", cpt_permission)
                )
        connection.executemany("INSERT INTO source VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sources)
        connection.executemany(
            "INSERT INTO code VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    entry.system,
                    entry.code,
                    entry.kind,
                    entry.description,
                    entry.short_description,
                    entry.effective_date,
                    entry.termination_date,
                    entry.action_code,
                    entry.category,
                    entry.locator,
                    entry.source_id,
                )
                for entry in entries
            ],
        )
        counts = {
            "built_on": date.today().isoformat(),
            "hcpcs_codes": str(sum(e.system == "HCPCS" and e.kind == "code" for e in entries)),
            "hcpcs_modifiers": str(sum(e.system == "HCPCS" and e.kind == "modifier" for e in entries)),
            "cpt_codes": str(sum(e.system == "CPT" for e in entries)),
            "hcpcs_complete": "yes",
            "cpt_complete": "yes" if cpt_complete else "no",
            "cpt_descriptors": "verified" if cpt_evidence else "unverified",
        }
        connection.executemany("INSERT INTO meta VALUES (?, ?)", counts.items())
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hcpcs", type=Path, required=True, help="CMS Alpha-Numeric HCPCS ZIP")
    parser.add_argument("--hcpcs-effective", required=True, help="release effective date, YYYY-MM-DD")
    parser.add_argument(
        "--cpt",
        help="licensed normalized CPT CSV path, or - to read the live-reader extraction from stdin",
    )
    parser.add_argument(
        "--cpt-complete",
        action="store_true",
        help="assert that --cpt contains the complete licensed 2026 CPT code set",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cpt-agreement", type=Path, help="agreement JSON in the owning checkout's scratch/cpt-2026")
    parser.add_argument("--cpt-agreement-sha256", help="expected SHA-256 of the agreement JSON")
    args = parser.parse_args(argv)

    hcpcs_effective = _date(args.hcpcs_effective, "--hcpcs-effective")
    assert hcpcs_effective is not None
    if not args.hcpcs.is_file():
        raise SystemExit(f"not a file: {args.hcpcs}")
    cpt_path = None if args.cpt in {None, "-"} else Path(args.cpt)
    if cpt_path is not None and not cpt_path.is_file():
        raise SystemExit(f"not a file: {cpt_path}")
    if args.cpt_complete and args.cpt is None:
        parser.error("--cpt-complete requires --cpt")
    if args.cpt_agreement and (cpt_path is None or not args.cpt_agreement_sha256):
        parser.error("--cpt-agreement requires a CPT CSV and --cpt-agreement-sha256")

    try:
        entries = read_hcpcs(args.hcpcs)
        cpt_text = None
        cpt_machine_source = None
        if args.cpt == "-":
            cpt_text = sys.stdin.read()
            cpt_machine_source = "VitalSource live reader normalized extraction"
            entries.extend(read_cpt_text(cpt_text, "stdin"))
        elif cpt_path is not None:
            cpt_text = cpt_path.read_text(encoding="utf-8-sig")
            cpt_machine_source = cpt_path.name
            entries.extend(read_cpt_text(cpt_text, cpt_path.name))
        cpt_evidence = None
        descriptor_state = "unverified (no agreement record supplied)"
        if args.cpt_agreement:
            root = scratch_root() / "cpt-2026"
            if not args.cpt_agreement.is_file():
                raise ValueError(f"recorded CPT agreement absent: {args.cpt_agreement}")
            if args.cpt_agreement.resolve().parent != root.resolve():
                raise ValueError(f"CPT agreement must be under {root}")
            # A supplied record's inputs are checked on every path, so an absent or changed
            # recorded input refuses even when the record could not have set verified.
            checked = verify_cpt_agreement(root, cpt_path, args.cpt_agreement)
            if _sha256(args.cpt_agreement) != args.cpt_agreement_sha256:
                descriptor_state = "unverified (agreement record digest disagrees with --cpt-agreement-sha256)"
            elif not args.cpt_complete:
                descriptor_state = "unverified (--cpt-complete not asserted)"
            else:
                cpt_evidence = checked
                descriptor_state = "verified"
        write_database(
            args.out,
            entries,
            args.hcpcs,
            hcpcs_effective,
            cpt_machine_source,
            _sha256(cpt_path) if cpt_path is not None else _text_sha256(cpt_text),
            args.cpt_complete,
            cpt_evidence,
        )
    except (OSError, UnicodeError, ValueError, sqlite3.Error, zipfile.BadZipFile) as error:
        raise SystemExit(str(error)) from error

    print(f"HCPCS codes      {sum(e.system == 'HCPCS' and e.kind == 'code' for e in entries):,}")
    print(f"HCPCS modifiers  {sum(e.system == 'HCPCS' and e.kind == 'modifier' for e in entries):,}")
    print(f"CPT codes        {sum(e.system == 'CPT' for e in entries):,}")
    if args.cpt is not None:
        print(f"CPT descriptors  {descriptor_state}")
    print(f"written          {args.out}")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
