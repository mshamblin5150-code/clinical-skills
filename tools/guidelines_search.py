"""Query the FTS5 guideline index built by ``guidelines_index.py``.

    python tools/guidelines_search.py "blood pressure threshold"
    python tools/guidelines_search.py --society IDSA "urine culture" "urine cultures"
    python tools/guidelines_search.py --fts "pyelonephritis NEAR(fluoroquinolone, 20)"

Every hit reports **filename, page and the matching line**, which is the whole point:
a hit is checkable against the PDF of the same name in one jump. Nothing here scores
similarity, and nothing here paraphrases -- the line printed is the line on the page.

**A query is a phrase by default.** ``urine culture`` searches for those two tokens
adjacent, not for pages mentioning both somewhere. That is the literal-string currency
the index exists for; ``--fts`` opts into FTS5's own syntax (``OR``, ``NEAR``,
``term*``) when a broader sweep is wanted.

**Punctuation in a query never reaches the parser**, because the phrase is rebuilt
from its tokens rather than quoted. A hyphen, a stray double quote and a mangled en
dash all drop out on both sides, so ``130-139`` finds ``130-139`` and ``130–139``
alike -- which matters, because en dashes come out of the extraction mangled and a
threshold is the one thing that cannot be got wrong.

**What it still cannot do, measured against the real corpus.** ``130-139 mmHg``
returns nothing; ``130-139 mm Hg`` returns the AHA/ACC 2025 hypertension guideline
and KDIGO 2021, because the page writes the unit with a space. Tokens are matched,
not concepts, and no amount of query cleaning bridges that one.

**So several queries in one run is the designed use, not a convenience.** Keyword
search cannot reach "renal replacement therapy" from "kidney failure"; the agent
supplying the synonyms can. Firing six exact queries with provenance on every hit is
the answer to that, so positional arguments repeat.

**A missing index is not zero hits.** Exit status is 0 for hits, 1 for a genuine zero,
and 2 for every way of not having searched -- no index, a file that is not one, one
built by another schema version, a query that would not parse, or a ``--class`` or
``--society`` value no document in the index carries. An index that had quietly failed
to build would otherwise answer every clinical question with silence and look like a
settled negative.

**That last limb is #185's**, and it is the same defect one level up. The catalog and
the extractor held two ``class`` vocabularies overlapping on ``guideline`` alone, so
``--class recommendation-statement`` exited **1** over a corpus in which every USPSTF
document is one -- this tool affirmatively certifying an absence rather than failing to
answer. They are one set now; what is left to reach is a typo in the flag and an index
built before the vocabulary was reconciled, and neither of those is a finding about the
corpus. The figures are in ``test_class_vocabulary.py`` and deliberately not restated
here.

**``--society`` had the identical shape and kept it for one ticket** -- #271. #185's
subject was the two ``class`` vocabularies and widening the fix to a second flag in the
same commit would have been scope the ruling did not cover, so it was left, said out
loud, and filed. A society's name here is the directory it is filed under, and those are
not obvious -- one carries a space, and the corpus holds two that differ by a letter --
so a mistype is not hypothetical. ``--society IDS`` was reaching a **1**, which is this
tool certifying that IDSA is silent on a question IDSA answers on the next line. Both
flags are guarded by one table now; the decision and its ceiling are on ``FILTERS``.

**A crash while printing was reaching 1 through the back door, and that is what
``use_utf8`` is doing in ``__main__``.** On a cp1252 console the print of a hit line
carrying a threshold sign raised, the traceback escaped ``main``, and the process
exited 1 -- which the paragraph above reads as *a genuine zero*. So the one failure
these statuses exist to make visible was reachable by an accident, and the queries
likeliest to trigger it were the clinical-threshold ones, because a cut point is
written with a sign cp1252 has no code point for. Issue #150.

Stdlib only -- FTS5 is compiled into the ``sqlite3`` that ships with Python, so
querying costs no dependency at all.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8
from guidelines_index import DATABASE_ENVIRONMENT_VARIABLE, SCHEMA_VERSION, default_database

DEFAULT_LIMIT = 20

# Matches unicode61's word boundaries closely enough to pick a line out of a page:
# both split on punctuation and neither splits on digits.
TOKEN = re.compile(r"\w+", re.UNICODE)

# FTS5 operators, dropped before line attribution so `OR` does not get hunted for as
# a word on the page. **Only under --fts**: in phrase mode they are ordinary words,
# and dropping them there would attribute `near syncope` on `syncope` alone and print
# whichever line mentioned it.
FTS_KEYWORDS = frozenset({"and", "or", "not", "near"})

# Enough of the line to identify it, and no more: a page of a table can hold a very
# long line, and this is printed to a terminal.
MAX_LINE = 300


class NotAnIndex(RuntimeError):
    """The file exists but is not a usable guideline index."""


class BadQuery(ValueError):
    """The query could not be parsed. Distinct from a query that simply found nothing."""


@dataclass(frozen=True)
class Hit:
    """Filename, page and matching line -- the three things #84 asks a hit to carry.

    Society, title and document class are columns on ``document`` and narrow a search
    from the SQL side; they are deliberately not fields here. A hit that carried them
    and printed none of them would be three values nobody reads and one more thing to
    keep true.
    """

    doc_id: str  # relative path, so the PDF of the same name is one jump away
    page: int
    line: str
    from_snippet: bool  # True when no single line carried a query term; see `_best_line`


def open_index(path: Path | str | None = None) -> sqlite3.Connection:
    """Open the index read-only, or raise loudly. Never returns an empty index."""
    target = Path(path) if path is not None else default_database()
    if not target.exists():
        raise FileNotFoundError(
            f"no guideline index at {target}. Build it with "
            "`python tools/guidelines_index.py <text-dir>`, or point at an existing "
            f"one with --db or {DATABASE_ENVIRONMENT_VARIABLE}. This is not a zero-result "
            "search -- nothing was searched."
        )
    connection = sqlite3.connect(f"file:{Path(target).as_posix()}?mode=ro", uri=True)
    try:
        row = connection.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        ).fetchone()
    except sqlite3.DatabaseError as bad:
        connection.close()
        raise NotAnIndex(f"{target} is not a guideline index ({bad}).") from bad
    if row is None:
        connection.close()
        raise NotAnIndex(f"{target} has no schema version; it is not a guideline index.")
    if row[0] != str(SCHEMA_VERSION):
        connection.close()
        raise NotAnIndex(
            f"{target} was built by schema version {row[0]}, this reads "
            f"{SCHEMA_VERSION}. Rebuild it with tools/guidelines_index.py."
        )
    return connection


def tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(text)]


def phrase_query(text: str) -> str:
    """A quoted FTS5 phrase rebuilt from the query's tokens.

    Rebuilding rather than quoting is what makes the punctuation cases safe: a stray
    double quote, a hyphen or an en dash never reaches the parser, because only the
    tokens survive.
    """
    words = tokens(text)
    if not words:
        raise BadQuery(f"nothing searchable in {text!r} -- it has no words or numbers.")
    return '"' + " ".join(words) + '"'


def _best_line(text: str, wanted: set[str]) -> tuple[str | None, int]:
    """The line of ``text`` carrying the most distinct query tokens.

    Returns ``(None, 0)`` when no line carries any -- which happens when a phrase is
    wrapped across two lines by the PDF's own layout, or when an ``--fts`` query
    matched by ``NEAR`` rather than by any single line. The caller falls back to a
    snippet there and marks it, rather than printing a line that did not match.
    """
    best, best_score = None, 0
    for line in text.splitlines():
        score = len(wanted & set(tokens(line)))
        if score > best_score:
            best, best_score = line.strip(), score
    return best, best_score


SELECT_HITS = """
SELECT d.doc_id, p.number, p.text, snippet(page_fts, 0, '', '', '...', 16)
FROM page_fts
JOIN page p ON p.page_id = page_fts.rowid
JOIN document d ON d.doc_pk = p.doc_pk
WHERE page_fts MATCH ?
"""


def search(
    connection: sqlite3.Connection,
    query: str,
    *,
    limit: int = DEFAULT_LIMIT,
    society: str | None = None,
    document_class: str | None = None,
    raw: bool = False,
) -> list[Hit]:
    match = query if raw else phrase_query(query)
    sql = SELECT_HITS
    parameters: list[object] = [match]
    if society:
        sql += " AND d.society = ?"
        parameters.append(society)
    if document_class:
        sql += " AND d.document_class = ?"
        parameters.append(document_class)
    sql += " ORDER BY bm25(page_fts) LIMIT ?"
    parameters.append(limit)

    try:
        rows = connection.execute(sql, parameters).fetchall()
    except sqlite3.OperationalError as bad:
        raise BadQuery(f"{query!r} is not a valid query: {bad}") from bad

    wanted = set(tokens(query))
    if raw:
        wanted -= FTS_KEYWORDS
    hits = []
    for doc_id, page, text, snippet in rows:
        line, score = _best_line(text, wanted)
        from_snippet = score == 0
        shown = " ".join((snippet if from_snippet else line).split())
        hits.append(
            Hit(doc_id=doc_id, page=page, line=shown[:MAX_LINE], from_snippet=from_snippet)
        )
    return hits


# Every filter flag, paired with the `document` column it narrows on -- which is also
# its argparse dest, because the two are the same word for both. `main` reads the value
# with `getattr(args, column)` on the strength of that, so it is pinned by a test rather
# than relied on: a third filter whose dest parted from its column would raise, and the
# traceback would escape `main` and exit 1.
#
# #271's decision: one table rather than a copy of the guard per flag. The ticket leaned
# the other way, on the ground that #253's cost is two copies of a *rule* and two copies
# of a *shape* are not that. The table wins on two grounds it did not have. The two are
# not copies at all -- see `index_values` for the one way they differ and what a naive
# copy costs. And it makes completeness partly checkable: `test_guidelines.py` reads the
# columns off `search`'s own WHERE clauses by AST and asserts they are exactly these.
#
# **Partly, and the ceiling is named rather than left to be found.** That walk matches
# one SQL shape -- `AND d.<column> = ?`. A range filter, an `IN`, an unaliased column
# and a named parameter all pass it unseen, so it is a floor on the shapes in this file
# today and not a guarantee about the next one. Overstating it was caught in review, and
# `test_ls_files_coverage.py` records the same overstatement being priced the same way.
FILTERS = (("--society", "society"), ("--class", "document_class"))


def index_values(connection: sqlite3.Connection, column: str) -> list[str]:
    """Every value of ``column`` some document in this index actually carries.

    ``NULL`` is not a value a filter can be asked for -- a document at the root of
    the text directory has no society -- and it is dropped rather than reported. It
    cannot be left in: ``sorted`` raises ``TypeError`` on a mixed list, the traceback
    escapes ``main``, and the process exits **1**, which this module's docstring reads
    as a genuine zero. That is #150's back door reopened on the flag whose whole bug
    is a wrong 1.

    The column is interpolated, so it is checked against ``FILTERS`` first rather than
    trusted -- there is no parameter form for an identifier in SQL.
    """
    if column not in {name for _, name in FILTERS}:
        raise ValueError(f"{column!r} is not a filter column; {FILTERS} are")
    rows = connection.execute(
        f"SELECT DISTINCT {column} FROM document WHERE {column} IS NOT NULL"
    )
    return sorted(row[0] for row in rows)


def _report(connection: sqlite3.Connection, query: str, **options) -> int:
    """Print one query's hits. Returns how many there were."""
    hits = search(connection, query, **options)
    print(f"== {query}")
    for hit in hits:
        # The marker stays plain ASCII, so it reads the same on any console. That was
        # once the whole of this file's thinking about cp1252, and it covered the one
        # character here that is chosen rather than quoted: `hit.line` is a line off a
        # guideline page, full of characters cp1252 cannot encode, and printing it
        # raised. `use_utf8` in `__main__` is what makes it safe -- issue #150.
        mark = "~" if hit.from_snippet else " "
        print(f" {mark}{hit.doc_id}  p.{hit.page}  {hit.line}")
    print(f"-- {len(hits)} match(es); ~ = phrase spans lines, snippet shown")
    return len(hits)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", nargs="+", help="one or more queries; each is a phrase")
    parser.add_argument("--db", help=f"index to read (default: {default_database()})")
    parser.add_argument(
        "--society",
        help="restrict to one society, e.g. IDSA; the directory name it is filed "
        "under. A value no document carries exits 2 rather than reporting a zero",
    )
    parser.add_argument(
        "--class",
        dest="document_class",
        help="restrict to one document class; the same vocabulary "
        "reference/guidelines-catalog.md publishes. A value no document carries "
        "exits 2 rather than reporting a zero",
    )
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="hits per query")
    parser.add_argument(
        "--fts", action="store_true", help="pass the query through as FTS5 syntax"
    )
    args = parser.parse_args(argv)

    try:
        connection = open_index(args.db)
    except (FileNotFoundError, NotAnIndex) as unusable:
        print(str(unusable), file=sys.stderr)
        return 2

    options = dict(
        limit=args.limit,
        society=args.society,
        document_class=args.document_class,
        raw=args.fts,
    )
    try:
        # A filter value no document carries is not a genuine zero, and 1 would say
        # it was. #185 for `--class`, #271 for `--society`, and the docstring above
        # carries the reasoning. What is left to reach is a typo and an index built
        # by an older extractor; both are ways of not having searched, and both are 2.
        for flag, column in FILTERS:
            value = getattr(args, column)
            if not value:
                continue
            carried = index_values(connection, column)
            if value not in carried:
                print(
                    f"{flag} {value!r} is not a value any document in this index "
                    f"carries; it holds {', '.join(carried) or 'nothing'}",
                    file=sys.stderr,
                )
                return 2

        found = 0
        for query in args.query:
            try:
                found += _report(connection, query, **options)
            except BadQuery as bad:
                print(str(bad), file=sys.stderr)
                return 2
        return 0 if found else 1
    finally:
        connection.close()


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
