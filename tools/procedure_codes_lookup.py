"""Query the licensed 2026 CPT/HCPCS procedure-code database.

    python tools/procedure_codes_lookup.py J1100 12001
    python tools/procedure_codes_lookup.py --system HCPCS --find dexamethasone
    python tools/procedure_codes_lookup.py --modifier 25 --on 2026-09-14

Lookup verifies existence and descriptors. It does not decide that documentation
meets a code's requirements; the CPT/HCPCS books' rules still require a human or
a screenshot-grounded VitalSource read.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from console_codec import require_python_floor, use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = REPO_ROOT / "reference" / "procedure-codes-2026.sqlite"


@dataclass(frozen=True)
class Match:
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
    source_title: str
    source_edition: str


SELECT = """
SELECT c.system, c.code, c.kind, c.description, c.short_description,
       c.effective_date, c.termination_date, c.action_code, c.category,
       c.locator, s.title, s.edition
FROM code AS c JOIN source AS s ON s.id = c.source_id
"""


def open_database(path: Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(
            f"no procedure-code database at {path}; build it with tools/procedure_codes_build.py"
        )
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def _match(row: tuple) -> Match:
    return Match(*row)


def infer_system(code: str) -> str:
    return "CPT" if re.fullmatch(r"(?:\d{5}|\d{4}[FTU])", code) else "HCPCS"


def describe(connection: sqlite3.Connection, code: str, kind: str = "code") -> Match | None:
    normalized = code.strip().upper()
    row = connection.execute(
        SELECT + " WHERE c.system = ? AND c.kind = ? AND c.code = ?",
        (infer_system(normalized), kind, normalized),
    ).fetchone()
    return None if row is None else _match(row)


def find(connection: sqlite3.Connection, phrase: str, system: str | None) -> list[Match]:
    sql = SELECT + " WHERE lower(c.description) LIKE lower(?)"
    params: list[str] = [f"%{phrase}%"]
    if system:
        sql += " AND c.system = ?"
        params.append(system)
    sql += " ORDER BY c.system, c.code"
    return [_match(row) for row in connection.execute(sql, params)]


def valid_on(entry: Match, on: str) -> bool:
    return (entry.effective_date is None or entry.effective_date <= on) and (
        entry.termination_date is None or on <= entry.termination_date
    )


def complete(connection: sqlite3.Connection, system: str) -> bool:
    row = connection.execute(
        "SELECT value FROM meta WHERE key = ?", (f"{system.lower()}_complete",)
    ).fetchone()
    return row is not None and row[0] == "yes"


def cpt_descriptors_verified(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT value FROM meta WHERE key = 'cpt_descriptors'"
    ).fetchone()
    return row is not None and row[0] == "verified"


def _report(
    connection: sqlite3.Connection, entry: Match | None, requested: str, on: str
) -> int:
    if entry is None:
        system = infer_system(requested.strip().upper())
        if not complete(connection, system):
            print(
                f"{requested}  {system} SET NOT FULLY LOADED - "
                "verify in the licensed live book"
            )
            return 2
        print(f"{requested}  NOT IN THE {system} CODE SET - do not propose this number")
        return 1
    validity = "active" if valid_on(entry, on) else f"NOT ACTIVE ON {on}"
    print(f"{entry.system} {entry.code}  {entry.description}")
    if entry.system == "CPT" and not cpt_descriptors_verified(connection):
        print("  CPT DESCRIPTORS UNVERIFIED - take descriptor from the rendered VitalSource page")
    print(f"  {validity}; {entry.kind}")
    if entry.short_description:
        print(f"  short: {entry.short_description}")
    if entry.effective_date:
        print(f"  effective: {entry.effective_date}")
    if entry.termination_date:
        print(f"  terminates: {entry.termination_date}")
    if entry.category:
        print(f"  category: {entry.category}")
    if entry.locator:
        print(f"  locator: {entry.locator}")
    print(f"  source: {entry.source_title}, {entry.source_edition}")
    return 0 if validity == "active" else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("code", nargs="*")
    parser.add_argument("--find")
    parser.add_argument("--system", choices=("CPT", "HCPCS"))
    parser.add_argument("--modifier", action="store_true")
    parser.add_argument("--on", default=date.today().isoformat(), help="service date, YYYY-MM-DD")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args(argv)
    try:
        date.fromisoformat(args.on)
    except ValueError as error:
        parser.error(f"--on must be YYYY-MM-DD: {error}")
    if not args.code and not args.find:
        parser.error("give a code to verify, or --find a phrase")

    try:
        connection = open_database(args.database)
    except FileNotFoundError as error:
        raise SystemExit(str(error)) from error
    try:
        status = 0
        if args.find:
            matches = find(connection, args.find, args.system)
            for entry in matches:
                mark = " " if valid_on(entry, args.on) else "*"
                print(f"{mark}{entry.system:<5} {entry.code:<5} {entry.description}")
                if entry.system == "CPT" and not cpt_descriptors_verified(connection):
                    print("  CPT DESCRIPTORS UNVERIFIED - take descriptor from the rendered VitalSource page")
            print(f"-- {len(matches)} match(es); * = not active on {args.on}")
            systems = (args.system,) if args.system else ("CPT", "HCPCS")
            incomplete = [system for system in systems if not complete(connection, system)]
            if incomplete:
                print(
                    "-- incomplete system(s): "
                    + ", ".join(incomplete)
                    + "; a miss is not evidence that no code exists"
                )
        for code in args.code:
            status |= _report(
                connection,
                describe(connection, code, "modifier" if args.modifier else "code"),
                code,
                args.on,
            )
        return status
    finally:
        connection.close()


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
