"""Extract a guideline's recommendations into machine-readable records.

    python tools/guidelines_recs.py <pdf> [--json <path>] [--show]

This is #83 gate 2's input, and it exists because of one measurement. The ticket
assumed a recommendation count could only ever be a bound -- "it over-counts by
nature, the way HEDGE does in corpus_census.py" -- and that assumption was made
against a flattened text stream. Read the same PDF's **ruled tables** instead and
the AHA/ACC 2025 hypertension guideline yields 103 numbered recommendations in 33
tables with **zero** rows whose Class-of-Recommendation cell fails to parse.
Measured 2026-08-16. An exact count can be enforced; a bound cannot, and the
difference decides whether gate 2 may refuse a commit.

**Two modes, and the whole honesty of this module is in telling them apart.**

``EXACT``
    Recommendations read out of a ruled table whose header row is ``COR | LOE |
    Recommendations``. Every row is one recommendation, the class is a cell rather
    than a guess, and the count is the count. AHA/ACC sets its guidelines this way.

``BOUND``
    Recommendations found by matching a marker in running text -- KDIGO's
    ``Recommendation 3.1.1`` and ``Practice Point``, ADA's ``10.5`` numbering. The
    marker also appears in tables of contents, in cross-references and in prose
    discussing another recommendation, so the count is an **over-report** and is
    labeled as one. It is still worth having: an over-report bounds the omission
    gate from the safe side, which is `corpus_census.py`'s ruling reused.

**No source is silently promoted.** A document with no ruled recommendation table
comes back ``BOUND`` even if the marker count looks clean, because the thing that
makes a count exact is the table structure and not the tidiness of the answer.

**Nothing here is PHI and standing rule 1 is not in play** -- these are published
society guidelines. Copyright is: a recommendation is the society's own expression.
So stdout prints **counts and identifiers only**, `--show` prints the text, and the
JSON is written outside every checkout on `guidelines_index.py`'s terms. Paste a
line into a ticket, never a table.

**One of the tools in ``tools/`` that is not stdlib**, because it reads a PDF:

    python -m pip install pymupdf

The import sits inside the function that opens the file, so the test suite needs
nothing installed and **nothing a consumer runs imports this at all**.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent

MODE_EXACT = "exact"
MODE_BOUND = "bound"

# The header row that makes a table a recommendation table. Matched on the cells
# rather than on the whole row so a trailing empty column -- which PyMuPDF emits
# for a merged title row -- does not defeat it.
#
# Both spellings appear: the AHA/ACC files write "COR" and "LOE", and the older
# ones spell the second column "LOE" too. Anything else is a data table, and a data
# table in a guideline is full of numbers that are not recommendations.
TABLE_HEADER = ("cor", "loe")

# The merged cell above the header, which names the table. This is the string a
# scoped-out recommendation is named by, so it has to survive into the record.
TABLE_TITLE = re.compile(r"^\s*Recommendations for\s+(?P<title>.+?)\s*$", re.DOTALL)

# A numbered recommendation inside such a table. The number restarts per table, so
# it is only unique alongside the page and title -- which is what `rec_id` welds.
NUMBERED = re.compile(r"^\s*(?P<number>\d+)\.\s*(?P<text>.+)$", re.DOTALL)

# A Class of Recommendation cell. The modern spelling is bare -- 1, 2a, 2b, 3 --
# and 3 carries a qualifier the older files spell out.
CLASS_CELL = re.compile(r"^\s*(?P<value>1|2a|2b|3)\b(?P<qualifier>.*)$", re.IGNORECASE | re.DOTALL)

# Text markers, for the sources that do not rule their recommendations into tables.
# Each is (society-independent name, pattern). These produce a BOUND count and the
# module says so in every place the number is printed.
TEXT_MARKERS = (
    ("recommendation", re.compile(r"\bRecommendation\s+(?P<ref>\d+(?:\.\d+)+)")),
    ("practice-point", re.compile(r"\bPractice Point\b")),
)

_WHITESPACE = re.compile(r"\s+")


def flatten(cell: str | None) -> str:
    """A table cell as one line. PyMuPDF wraps cell text at the rendered line."""
    return _WHITESPACE.sub(" ", (cell or "").replace("\n", " ")).strip()


def is_header_row(row: list[str | None]) -> bool:
    """Whether this row is the ``COR | LOE | Recommendations`` header."""
    cells = [flatten(cell).lower() for cell in row]
    return len(cells) >= 2 and cells[0] == TABLE_HEADER[0] and cells[1] == TABLE_HEADER[1]


def table_title(row: list[str | None]) -> str | None:
    """The ``Recommendations for X`` title out of a table's merged first row.

    Returns None for any other first row, which is how a data table is rejected
    before its numbers are ever read as recommendations.

    **Only the first rendered line of the cell.** AHA/ACC sets a second line under
    most captions -- "Referenced studies that support the recommendations are
    summarized in ..." -- inside the same merged cell. Flattening the whole cell put
    that sentence into the title and therefore into every ``rec_id`` derived from
    it, which is a citation a reader has to type. Cutting at the newline is safe
    because the caption is one rendered line by construction: it is what the
    ``Recommendations for`` prefix is attached to.
    """
    first_line = "".join(cell or "" for cell in row).split("\n")[0]
    match = TABLE_TITLE.match(flatten(first_line))
    return match.group("title") if match else None


def slug(text: str) -> str:
    """A title as a stable identifier fragment: lowercase, hyphens, no punctuation.

    Truncated, because these titles run long -- "BP Treatment Threshold and the Use
    of CVD Risk Estimation to Guide Drug Treatment of Hypertension" is one of them
    -- and a `rec_id` is written into a sheet by hand and read back by eye.
    """
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned[:48].rstrip("-")


@dataclass(frozen=True)
class Recommendation:
    """One recommendation, and enough to find it again on the page.

    ``rec_id`` is the whole point of the record: it is what a threshold sheet cites
    and what gate 2 requires to be either present or scoped out by name. It is
    built from page, table and number rather than from a running counter, so
    re-running the extractor on an unchanged PDF produces the same identifiers and
    a sheet does not silently come unpinned.
    """

    rec_id: str
    doc_id: str
    page: int
    table: str
    number: int
    cor: str | None
    loe: str | None
    text: str
    mode: str


def read_table_recommendations(page_number: int, tables: list[list[list[str | None]]], doc_id: str) -> list[Recommendation]:
    """Every numbered recommendation in the ruled tables of one page.

    A table qualifies only if it carries **both** a ``Recommendations for`` title
    and a ``COR | LOE`` header. Requiring both is deliberate: the title alone also
    matches a continuation table's repeated caption, and the header alone appears
    in the front-matter legend explaining what the classes mean.
    """
    found: list[Recommendation] = []
    for rows in tables:
        if len(rows) < 3:
            continue
        title = table_title(rows[0])
        if title is None or not is_header_row(rows[1]):
            continue
        for row in rows[2:]:
            cells = [flatten(cell) for cell in row]
            if len(cells) < 3:
                continue
            numbered = NUMBERED.match(cells[-1])
            if not numbered:
                continue
            class_cell = CLASS_CELL.match(cells[0])
            found.append(
                Recommendation(
                    rec_id=f"p{page_number}/{slug(title)}/{numbered.group('number')}",
                    doc_id=doc_id,
                    page=page_number,
                    table=title,
                    number=int(numbered.group("number")),
                    cor=class_cell.group("value").lower() if class_cell else None,
                    loe=cells[1] or None,
                    text=numbered.group("text").strip(),
                    mode=MODE_EXACT,
                )
            )
    return found


def read_marker_recommendations(page_number: int, text: str, doc_id: str) -> list[Recommendation]:
    """Marker hits on one page, as an over-reporting bound.

    Every hit is a record so the caller can print where the bound comes from. The
    ``mode`` on each says ``bound``, and nothing downstream is allowed to add an
    exact count to one of these without the total becoming a bound too.
    """
    found: list[Recommendation] = []
    for name, pattern in TEXT_MARKERS:
        for index, match in enumerate(pattern.finditer(text), start=1):
            reference = match.groupdict().get("ref") if match.groupdict() else None
            found.append(
                Recommendation(
                    rec_id=f"p{page_number}/{name}/{reference or index}",
                    doc_id=doc_id,
                    page=page_number,
                    table=name,
                    number=index,
                    cor=None,
                    loe=None,
                    text=_WHITESPACE.sub(" ", text[match.start(): match.start() + 160]).strip(),
                    mode=MODE_BOUND,
                )
            )
    return found


def extract(path: Path, doc_id: str) -> tuple[list[Recommendation], str]:
    """Every recommendation in one PDF, and the mode the count carries.

    **Tables first, and markers only if the tables found nothing.** A document that
    rules its recommendations is counted exactly; running the markers over it as
    well would add the same recommendation a second time from its own cross
    references and turn an exact count into a bound for no gain.
    """
    import pymupdf  # imported here so everything above stays importable without it

    document = pymupdf.open(str(path))
    table_hits: list[Recommendation] = []
    marker_hits: list[Recommendation] = []
    try:
        for index, page in enumerate(document, start=1):
            try:
                tables = [table.extract() for table in page.find_tables().tables]
            except Exception:  # noqa: BLE001 - a page whose tables will not parse is not a failed document
                tables = []
            table_hits.extend(read_table_recommendations(index, tables, doc_id))
            marker_hits.extend(read_marker_recommendations(index, page.get_text("text"), doc_id))
    finally:
        document.close()

    if table_hits:
        return table_hits, MODE_EXACT
    return marker_hits, MODE_BOUND


def ensure_outside_repo(path: Path) -> None:
    """Refuse to write the JSON inside any git checkout.

    `guidelines_index.py`'s guard, for its reason and one more: this file holds the
    society's own recommendation text in full, and #87 rules that stays outside.
    """
    resolved = path.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / ".git").exists():
            raise SystemExit(
                f"refusing to write inside a git checkout: {resolved}\n"
                f"  {candidate} is a repository.\n"
                "This file holds the society's recommendation text in full. #87."
            )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf", type=Path, help="the guideline PDF to read")
    parser.add_argument(
        "--doc-id",
        default=None,
        help="identifier to record (default: the file stem), matching the manifest's",
    )
    parser.add_argument("--json", type=Path, default=None, help="write full records here")
    parser.add_argument(
        "--show",
        action="store_true",
        help="print recommendation text -- the society's expression, not for pasting",
    )
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        # 2 rather than 1, on `guidelines_search.py`'s arrangement: not having read
        # a document must never be reported in the same way as having read one and
        # found no recommendations in it.
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 2

    doc_id = args.doc_id or args.pdf.stem
    records, mode = extract(args.pdf, doc_id)

    if not records:
        print(f"no recommendation found in {args.pdf.name}", file=sys.stderr)
        print("Neither a ruled COR/LOE table nor a text marker. Nothing was counted,", file=sys.stderr)
        print("which is not the same as this document having no recommendations.", file=sys.stderr)
        return 2

    tables = sorted({record.table for record in records})
    print(f"== {doc_id}")
    print(f"  mode           {mode}")
    print(f"  recommendations {len(records)}")
    print(f"  tables          {len(tables)}")
    if mode == MODE_BOUND:
        print()
        print("  claim: this is an OVER-REPORT and must not be read as a count.")
        print("  A marker is matched wherever it appears, including in a table of")
        print("  contents and in prose citing another recommendation. Gate 2 warns")
        print("  on a bound and refuses only on an exact source.")

    if args.show:
        print()
        for record in records:
            classification = f"[{record.cor or '-'}/{record.loe or '-'}]"
            print(f"  {record.rec_id}  {classification}  {record.text[:110]}")

    if args.json:
        ensure_outside_repo(args.json)
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                {
                    "doc_id": doc_id,
                    "source": str(args.pdf),
                    "mode": mode,
                    "totals": {"recommendations": len(records), "tables": len(tables)},
                    "recommendations": [asdict(record) for record in records],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"  json            {args.json}")

    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
