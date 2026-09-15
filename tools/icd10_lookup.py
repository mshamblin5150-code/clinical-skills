"""Query the committed ICD-10-CM database.

    python tools/icd10_lookup.py Z68.36
    python tools/icd10_lookup.py --find "body mass index" --billable
    python tools/icd10_lookup.py --index "Smoker"

This is what turns ``icd10-cpt``'s ``CONFIDENCE: verify this number`` into a
verified descriptor. It answers four things and no more: does the code exist,
what is its official descriptor, is it billable, and what notes govern it.

**Billable is the quiet one.** ``Z68.2`` is a real code with a real descriptor
that cannot be submitted — it is a header, and only its children are billable.
A proposal carrying a header code reads as correct right up to the rejection,
which is a failure mode a descriptor check alone does not catch.

**Notes are inherited, and the level is reported.** CMS writes an instruction at
the level it applies to: *"code to identify body mass index (BMI), if known"*
sits on ``E66``, three characters above ``E66.811``, the code an obesity
diagnosis actually gets. ``notes_for`` walks the ancestors so the instruction is
found, and each note reports the code it was written against so the clinician
can check it in the tabular where it really lives.

**Two searches with different claims.** ``--find`` is a substring match over
descriptors. ``--index`` is an exact final-term match over the official
alphabetic index and prints each complete path plus its direct code or referral.
A miss from either mode is not evidence that no code exists: the intended phrase
may sit under another index term or behind a referral that still needs following.

**What it prints is not all ASCII, which issue #150 assumed it was.** Measured
against the shipped FY2026 database, 2026-08-16: the 98,186 descriptors carry
**zero** non-ASCII characters, so the assumption held for the half of the output
the ticket was looking at — but the 22,988 tabular notes carry **65**, nine
distinct code points, every one an accented Latin letter out of an eponym.
cp1252 encodes all nine, so this tool was never the one that crashed. It was safe
by the accident of which accents CMS happens to use rather than by being ASCII,
and a console on cp437 or a plain ASCII stream would have taken the same
traceback ``guidelines_search.py`` did. ``use_utf8`` in ``__main__`` settles it
for every console.

Those figures are a measurement and not a test: nothing in ``tools/`` tests
against the shipped database, because a test that read it would pass for two
reasons and one of them is the builder and the test being wrong together.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from icd10_build import Code, IndexEntry, Note

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = REPO_ROOT / "reference" / "icd10cm-2026.sqlite"

# ICD-10-CM codes run three to seven characters, the first three being the
# category. Nothing shorter than a category can carry a note that applies here.
CATEGORY_LENGTH = 3


def normalize(code: str) -> str:
    """``Z68.36``, ``z68.36`` and `` Z6836 `` are the same code."""
    return code.strip().replace(".", "").upper()


def open_database(path: Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"no code database at {path}. It is committed to this repo; if it is "
            "missing, rebuild it with tools/icd10_build.py."
        )
    return sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)


SELECT_CODE = "SELECT code, billable, long, short FROM code"


def _code(row: tuple) -> Code:
    return Code(code=row[0], billable=bool(row[1]), long=row[2], short=row[3])


def describe(connection: sqlite3.Connection, code: str) -> Code | None:
    row = connection.execute(
        f"{SELECT_CODE} WHERE code = ?", (normalize(code),)
    ).fetchone()
    return None if row is None else _code(row)


def ancestors(code: str) -> list[str]:
    """``E66811`` -> ``E66``, ``E668``, ``E6681``, ``E66811``.

    Prefixes, not string neighbors: ``R030`` never reaches ``E66``, and a code
    is its own last ancestor so a note written at its own level is included.
    """
    normalized = normalize(code)
    return [normalized[:n] for n in range(CATEGORY_LENGTH, len(normalized) + 1)]


def notes_for(connection: sqlite3.Connection, code: str) -> list[Note]:
    tree = ancestors(code)
    if not tree:
        return []
    placeholders = ",".join("?" * len(tree))
    rows = connection.execute(
        f"SELECT code, kind, text FROM note WHERE code IN ({placeholders}) "
        "ORDER BY length(code), kind, text",
        tree,
    ).fetchall()
    return [Note(code=r[0], kind=r[1], text=r[2]) for r in rows]


def find(connection: sqlite3.Connection, phrase: str, billable_only: bool) -> list[Code]:
    sql = f"{SELECT_CODE} WHERE long LIKE ?"
    if billable_only:
        sql += " AND billable = 1"
    rows = connection.execute(sql + " ORDER BY code", (f"%{phrase}%",)).fetchall()
    return [_code(row) for row in rows]


def index_paths(connection: sqlite3.Connection, term: str) -> list[IndexEntry]:
    """Return every alphabetic-index path whose final term exactly matches."""
    rows = connection.execute(
        "SELECT term, path, code, see, see_also FROM index_entry "
        "WHERE term = ? COLLATE NOCASE ORDER BY path, code, see, see_also",
        (term.strip(),),
    ).fetchall()
    return [IndexEntry(*row) for row in rows]


def dotted(code: str) -> str:
    """Codes are stored flat and read dotted. ``Z6836`` -> ``Z68.36``."""
    return code if len(code) <= CATEGORY_LENGTH else f"{code[:3]}.{code[3:]}"


def _report(connection: sqlite3.Connection, code: str) -> int:
    # Plain ASCII throughout: printed to a Windows console, where a dash outside
    # cp1252 comes back as a question mark and reads like corruption.
    entry = describe(connection, code)
    if entry is None:
        print(f"{code}  NOT IN THE CODE SET - do not propose this number")
        return 1
    flag = "billable" if entry.billable else "NOT BILLABLE - a header; code to a child"
    print(f"{dotted(entry.code)}  {entry.long}")
    print(f"  {flag}")
    if entry.short:
        print(f"  short: {entry.short}")
    for note in notes_for(connection, entry.code):
        where = "" if note.code == entry.code else f" [on {dotted(note.code)}]"
        print(f"  {note.kind}{where}: {note.text}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("code", nargs="*", help="one or more codes, dotted or not")
    parser.add_argument("--find", help="substring match over official descriptors")
    parser.add_argument("--index", help="exact alphabetic-index term to trace")
    parser.add_argument("--billable", action="store_true", help="with --find, billable codes only")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args(argv)

    if not args.code and not args.find and not args.index:
        parser.error("give a code to verify, --find a phrase, or --index a term")
    if args.find and args.index:
        parser.error("--find and --index are separate lookup modes")
    if args.billable and not args.find:
        parser.error("--billable narrows --find; it does nothing on its own")

    try:
        connection = open_database(args.database)
    except FileNotFoundError as missing:
        raise SystemExit(str(missing)) from missing
    try:
        status = 0
        if args.find:
            matches = find(connection, args.find, args.billable)
            for entry in matches:
                mark = " " if entry.billable else "*"
                print(f"{mark}{dotted(entry.code):<9} {entry.long}")
            print(f"-- {len(matches)} match(es); * = not billable")
        if args.index:
            matches = index_paths(connection, args.index)
            for entry in matches:
                destination = (
                    f"code {dotted(entry.code)}" if entry.code else
                    f"see {entry.see}" if entry.see else
                    f"see also {entry.see_also}" if entry.see_also else
                    "no direct destination"
                )
                print(f"{entry.path} -> {destination}")
            print(f"-- {len(matches)} path(s)")
            if not matches:
                status = 1
        for code in args.code:
            status |= _report(connection, code)
        return status
    finally:
        connection.close()


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
