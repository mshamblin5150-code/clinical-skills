"""Grade a distilled threshold sheet against the guideline it claims to come from.

    python tools/threshold_sheet.py <sheet.md> [--recs <recs.json>] [--pdf-root <dir>]
    python tools/threshold_sheet.py --all

This is #83's gate set. A threshold sheet is the deliverable of the #80 series: per
topic, the decision points only -- drug, dose, duration, target number, referral and
follow-up threshold, staging cutoff. Facts are not copyrightable and expression is,
so a restated staging table is a thing this repo may hold and a dumped PDF is not.

**The failure being defended against is the one this repo trusts least**: an agent
producing fluent, plausible, confident text from a source only it has read. Nothing
here checks that a guideline was *understood*. Each gate eliminates one way a sheet
can be confidently wrong.

Four gates, and what each one can and cannot see
------------------------------------------------

``SCHEMA``  refuses
    Structural. Every row has all eight columns, a population key drawn from the
    sheet's own declared vocabulary, no non-ASCII comparison character in its value,
    and a source key that the Sources table defines. Every source carries a version,
    a publication date and a URL. The sheet has a ``## Scope`` section saying both
    what was read and what was **not**. **And the conflict rule**: two rows sharing a
    quantity key AND a population key with different values must be covered by a
    ``CONFLICT`` block for that quantity. Needs nothing but the sheet, so it runs
    everywhere and always.

    **What the conflict rule checks is the block's existence, not its contents.**
    This sentence used to say the block must name *both* rows; it does not, and
    nothing reads the block's prose. Corrected rather than implemented, because the
    check a reader was promised -- does this paragraph name both societies and both
    values -- is a reading, and the file two screens down deletes an allowlist for
    exactly this reason: *"a rule that has drifted from the file a reader opens reads
    as agreement."*

``CITATION`` refuses, in two tiers
    Tier 1 runs everywhere: the number in a row's ``value`` must appear in that
    row's ``snippet``. Tier 2 runs only where the PDFs are present: the snippet must
    appear on the cited page. **The two tiers are the whole answer to "what happens
    when the sources are absent"** -- there is no machine on which citation checking
    drops to zero, and the sheet header records the date tier 2 last really ran, so
    the artifact says so rather than only the console.

``COVERAGE`` refuses on an exact source, warns on a bound
    #83 gate 2, the omission check: *"everything else checks what was written, only
    this checks what was not."* Every recommendation the source carries is a row or
    is scoped out by ``rec_id``. Whether this may refuse is decided by
    ``guidelines_recs.py``'s mode and never by this module: an exact count can be
    enforced, a marker bound over-reports and can only warn.

``RANGE``   refuses
    Per-quantity bounds. A BP target of 1300, an eGFR of 450, a dose three orders of
    magnitude off. Decimal-place and unit errors are the highest-consequence
    extraction failures and the cheapest to catch, because catching them needs no
    understanding of the guideline at all. **It also refuses a value carrying a
    character that is not a comparison operator** -- a Symbol-font ``\u00a3`` where the
    source meant ``<=``, which this corpus contains 73 of.

What no gate here reaches, stated the same day the gates were built
--------------------------------------------------------------------

- **Whether the row says what the recommendation says.** ``CITATION`` proves the
  snippet is on the page. It cannot prove the row's ``quantity`` is what that
  sentence was about, and a sheet whose numbers are all real and all filed under the
  wrong heading passes every gate here.
- **Whether the population key is right.** ``SCHEMA`` checks it is *declared*. The
  key is a judgment, which is why the verbatim population text sits beside it in the
  Sources table for a reader to check the key against. A mis-keyed row hides a real
  conflict by making two rows look like different patients -- and the ruling that
  population decides this at all came from the clinician, not from the corpus.
- **A recommendation scoped out for a bad reason.** ``COVERAGE`` requires a reason
  string; it cannot grade one. ``out: not relevant`` passes.
- **Anything at all about a ``bound`` source.** ``COVERAGE`` warns and moves on.

**Deliberately not built, because it would pass for the wrong reason**: any gate
that re-extracts a value and compares it to the sheet through the path that wrote
the sheet. ``tools/test_icd10.py`` runs against committed excerpts and never against
the shipped database for precisely this reason. It is the most natural check to
write here and it is worthless.

Exit status
-----------

``0`` clean. ``1`` a gate that refuses found something. ``2`` **every way of not
having graded** -- no sheet, no rows in it, an unreadable Sources table. A sheet
whose rows were written in a shape the parser does not read would otherwise report
zero violations and look like a pass, which is `differential_scan.py`'s ruling and
the shape #153 caught in the wild at 2.4% coverage reading green.

Where 1 and 2 both hold, **1 wins**, and the message names the ungraded count so the
finding reads as a floor rather than the whole.

Stdlib only. Tier 2 needs ``pymupdf`` and says ``SKIPPED`` without it rather than
failing, which is the same hole -- named here rather than discovered later.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent
SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"

SCHEMA_MARKER = "<!-- schema: threshold-sheet/1 -->"

# The escape hatch #83 asks for by name: *"Table-derived values need an escape hatch
# on the `phi-scan: synthetic` pattern: a per-row annotation meaning read off the
# rendered page, extraction garbles this table. Declaring it is a deliberate act that
# leaves a trace."*
#
# A snippet beginning with this marker means the value was read off the PAGE AS
# TYPESET and not out of the text layer, so tier 2 cannot resolve it -- the string on
# the rendered page is not the string extraction produces, which is the whole reason
# the row needs the hatch. Those rows are counted and printed rather than passed
# silently, which is the "leaves a trace" half.
#
# **Modeled on `phi-scan: synthetic` and narrowed the same way it was.** That pragma
# has to sit alone on its own line because a bare substring test let two files exempt
# themselves merely by explaining the rule. Here the marker must START the snippet
# cell, so a row discussing the hatch in its own text cannot claim it.
RENDERED_MARKER = "RENDERED:"

# The eight columns of a threshold row, in order. Named here rather than positionally
# in the parser so a column added later fails loudly in one place.
ROW_COLUMNS = ("quantity", "population", "value", "snippet", "source", "page", "rec", "class")

# The comparison operators a value may carry. ASCII only, and that is a rule about
# the corpus rather than about taste: KDIGO's tables render the less-or-equal sign
# through a Symbol-font slot that extracts as a pound sign, 73 times across the 179
# documents, measured 2026-08-16. A sheet is allowed to hold the fact and must not
# hold the mis-encoding, because `<=` and `\u00a3` sort and compare differently and only
# one of them is readable back to a clinician.
# A blocklist and deliberately not an allowlist. An allowlist of operators was
# written here first and never referenced by any gate, while the docstring claimed
# it was enforced -- which is `test_spelling_scan.py`'s failure mode exactly: a rule
# that has drifted from the file a reader opens reads as agreement. It was removed
# rather than wired up, because a value legitimately carries no operator at all
# (`81 mg/day`, `monthly`, `3-6 months`) and an allowlist would have to permit the
# empty case, at which point it permits everything.
FORBIDDEN_IN_VALUE = {
    "\u00a3": "a Symbol-font mis-encoding of <= (73 in this corpus); write <=",
    "\u2264": "a Unicode <=; write the ASCII <=",
    "\u2265": "a Unicode >=; write the ASCII >=",
    "\u00b3": "a Symbol-font mis-encoding of >=; write >=",
}

# Sanity bounds, keyed on the UNIT a number is written in and never on the row's
# quantity name. These are deliberately WIDE: the gate exists to catch a decimal
# point in the wrong place and a unit confusion, not to second-guess a society. 1300
# for a systolic pressure and 450 for an eGFR are the failures #83 names, and both
# are an order of magnitude out.
#
# **Keyed on the unit because keying on the quantity was wrong, and it was wrong in
# the direction that matters.** The first version matched the bound by substring
# against the quantity name and then graded every number in the value against it. On
# the first real sheet it produced ten failures and all ten were false: `>=27 kg/m2`
# failed because the `2` in `m2` was read as a BMI, `>=7 days` and `15% in 24 h`
# failed because their quantity names contain `bp`, and `<160/110 mm Hg within 30 to
# 60 min` failed on the minutes. A value legitimately carries numbers in several
# units and only some of them are the threshold.
#
# Every one of those was found by running the gate against a real sheet rather than
# against the synthetic cases in tools/test_threshold_sheet.py, which is the same way
# block_scan.py's two parser bugs were found. The synthetic cases came afterwards and
# now pin each shape.
UNIT_BOUNDS = {
    "mm hg": (40.0, 250.0),
    "mg/d": (1.0, 6000.0),
    "mg/day": (1.0, 6000.0),
    "mg/g": (1.0, 6000.0),
    "mg": (1.0, 6000.0),
    "ml/min": (1.0, 150.0),
    "kg/m2": (10.0, 70.0),
    "%": (0.0, 100.0),
    "drink/d": (0.0, 10.0),
    "drinks/d": (0.0, 10.0),
    "year": (0.0, 120.0),
    "years": (0.0, 120.0),
}

# A run of numbers sharing one trailing unit. The separators are what make
# `140-159/90-109 mm Hg` four graded numbers rather than one, and `<160/<110 mm Hg`
# two -- a comparison operator may sit between them, which is how a guideline writes
# a paired systolic and diastolic bound.
#
# Units that carry NO bound above are matched anyway and then skipped, deliberately:
# matching `24 to 48 hours` is what stops those numbers being attributed to the mm Hg
# that appears earlier in the same value.
_UNIT_ALTERNATION = (
    r"mm\s*Hg|mg/d(?:ay)?|mg/g|mg|mL\s*/\s*min|kg/m2|kg|%|drinks?/d|"
    r"days?|weeks?|months?|years?|hours?|h|min(?:utes)?"
)
_MEASURED = re.compile(
    r"(?P<numbers>\d+(?:[.,]\d+)?(?:\s*(?:to|and|[-/])\s*[<>]?=?\s*\d+(?:[.,]\d+)?)*)"
    r"\s*(?P<unit>" + _UNIT_ALTERNATION + r")\b",
    re.IGNORECASE,
)

_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
_ROW_PIPE = re.compile(r"^\s*\|(?P<body>.+)\|\s*$")
_CONFLICT = re.compile(r"^\s*\*{0,2}CONFLICT\*{0,2}:\s*(?P<quantity>[a-z0-9-]+)\b(?P<rest>.*)$", re.IGNORECASE)
_OUT_LINE = re.compile(r"^\s*-\s*`(?P<rec_id>[^`]+)`\s*[-\u2014:]\s*(?P<reason>.+?)\s*$")
_RESOLVED = re.compile(r"citations resolved against\s+(?P<corpus>\S+)\s+on\s+(?P<date>\d{4}-\d{2}-\d{2})", re.IGNORECASE)


@dataclass(frozen=True)
class Row:
    quantity: str
    population: str
    value: str
    snippet: str
    source: str
    page: int | None
    rec: str
    klass: str
    line: int


@dataclass
class Sheet:
    """A parsed sheet. ``ok`` is false when it could not be read as one at all."""

    path: Path
    rows: list[Row] = field(default_factory=list)
    sources: dict[str, dict[str, str]] = field(default_factory=dict)
    populations: dict[str, str] = field(default_factory=dict)
    conflicts: dict[str, str] = field(default_factory=dict)
    scoped_out: dict[str, str] = field(default_factory=dict)
    # The prose of the ``## Scope`` section, and nothing from anywhere else. Kept as
    # its own field rather than searched for over the whole document because the two
    # phrases that satisfy it are ordinary English: a threshold row whose snippet
    # quotes "not read" would otherwise discharge the sheet's honesty clause.
    scope: str = ""
    has_scope_section: bool = False
    resolved_corpus: str | None = None
    resolved_date: str | None = None
    ok: bool = True
    why_not: str | None = None


def _cells(line: str) -> list[str] | None:
    """A Markdown table row as its cells, or None if the line is not one."""
    match = _ROW_PIPE.match(line)
    if not match:
        return None
    return [cell.strip() for cell in match.group("body").split("|")]


def _is_rule(cells: list[str]) -> bool:
    """The ``| --- | --- |`` line under a header."""
    return all(set(cell) <= set("-: ") and cell for cell in cells)


def parse(text: str, path: Path) -> Sheet:
    """Read a sheet into its parts.

    Sections are found by heading, and a row is only read inside the section that
    owns it. **That is the load-bearing choice in here.** A sheet's prose discusses
    its own rules -- this file's docstring is full of pipe characters and quantity
    keys -- and a parser matching a row shape anywhere would read the explanation of
    a conflict as a conflict. ``block_scan.py`` learned the same rule the hard way:
    a row fires on what opens a section, never on a mention inside one.
    """
    sheet = Sheet(path=path)
    if SCHEMA_MARKER not in text:
        sheet.ok = False
        sheet.why_not = f"no {SCHEMA_MARKER} marker"
        return sheet

    section: str | None = None
    source_columns: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^\s*#{1,6}\s+(?P<name>.+?)\s*$", line)
        if heading:
            section = heading.group("name").strip().lower()
            if section == "scope":
                sheet.has_scope_section = True
            continue

        if section == "scope":
            sheet.scope += line + "\n"
            # No `continue`: the `citations resolved against ...` line lives in this
            # section and is read below.

        resolved = _RESOLVED.search(line)
        if resolved:
            sheet.resolved_corpus = resolved.group("corpus")
            sheet.resolved_date = resolved.group("date")

        if section == "conflicts":
            conflict = _CONFLICT.match(line)
            if conflict:
                sheet.conflicts[conflict.group("quantity").lower()] = conflict.group("rest").strip()
            continue

        if section == "coverage":
            out = _OUT_LINE.match(line)
            if out:
                sheet.scoped_out[out.group("rec_id")] = out.group("reason")
            continue

        cells = _cells(line)
        if cells is None or _is_rule(cells):
            continue

        if section == "sources" and cells[0] == "key":
            source_columns = [cell.lower() for cell in cells]
            continue

        if section == "sources" and len(cells) >= 3 and cells[0] != "key":
            # Read by NAME against the header row rather than by position, which is
            # `ROW_COLUMNS`' rule applied to the table it was not applied to. `mode`
            # was `cells[-1]`, so appending a column to this table would silently
            # redefine the cell that decides refuse-versus-warn. Position is kept
            # only as the fallback for a sheet whose header this cannot read.
            named = dict(zip(source_columns, cells)) if source_columns else {}
            sheet.sources[cells[0]] = {
                "society": named.get("society", cells[1]),
                "document": named.get("document", cells[2]),
                "version": named.get("version", cells[3] if len(cells) > 3 else ""),
                "published": named.get("published", cells[4] if len(cells) > 4 else ""),
                "url": named.get("url", cells[5] if len(cells) > 5 else ""),
                "mode": named.get("mode", cells[-1]),
            }
        elif section == "populations" and len(cells) >= 2 and cells[0] != "key":
            sheet.populations[cells[0]] = cells[1]
        elif section == "thresholds" and len(cells) >= len(ROW_COLUMNS) and cells[0] != "quantity":
            page = re.sub(r"^p", "", cells[5], flags=re.IGNORECASE)
            sheet.rows.append(
                Row(
                    quantity=cells[0],
                    population=cells[1],
                    value=cells[2],
                    snippet=cells[3].strip('"'),
                    source=cells[4],
                    page=int(page) if page.isdigit() else None,
                    rec=cells[6],
                    klass=cells[7],
                    line=number,
                )
            )

    if not sheet.rows:
        sheet.ok = False
        sheet.why_not = "no row under a '## Thresholds' heading"
    return sheet


def gate_schema(sheet: Sheet) -> list[str]:
    """Structure, provenance, scope, declared vocabulary, and the conflict rule."""
    failures: list[str] = []

    # #83 lists the scope line among the things a sheet *carries*, and gives the
    # reason: *"so that 'absent from the sheet' is never misread as 'absent from the
    # guideline'"*. Both limbs are required and the second does the work -- `Read:`
    # alone lists coverage, only `Not read:` bounds the claim. Graded against the
    # `## Scope` section alone, never the whole document, so a row quoting either
    # phrase in its snippet cannot discharge it.
    if not sheet.has_scope_section:
        failures.append(f"{sheet.path.name}  no '## Scope' section, so nothing bounds what this sheet claims")
    else:
        scope = sheet.scope.lower()
        # The lookbehind is the whole rule, not a refinement: `not read:` CONTAINS
        # `read:`, so a plain substring test was discharged by the very sentence that
        # should have failed it -- a sheet declaring only what it skipped read as
        # having declared both.
        if not re.search(r"(?<!not )read:", scope):
            failures.append(f"{sheet.path.name}  '## Scope' never says what was read")
        if "not read:" not in scope:
            failures.append(
                f"{sheet.path.name}  '## Scope' never says what was NOT read, so an absent "
                "number cannot be told from an unread section"
            )

    # A threshold with no edition behind it is the failure the format exists to
    # prevent: societies revise, and 2017's number under 2025's heading is wrong in
    # the most expensive way. These three cells were parsed past until they were not.
    for key, source in sheet.sources.items():
        for column in ("version", "published", "url"):
            if not source.get(column):
                failures.append(f"{sheet.path.name}  source '{key}' has no {column}")

    for row in sheet.rows:
        where = f"{sheet.path.name}:{row.line}"
        if row.population not in sheet.populations:
            failures.append(
                f"{where}  population key '{row.population}' is not declared under '## Populations'"
            )
        if row.source not in sheet.sources:
            failures.append(f"{where}  source key '{row.source}' is not declared under '## Sources'")
        if row.page is None:
            failures.append(f"{where}  no page number")
        if not row.snippet:
            failures.append(f"{where}  no snippet, so tier 1 citation cannot run on this row")
        for character, why in FORBIDDEN_IN_VALUE.items():
            if character in row.value:
                failures.append(f"{where}  value contains {character!r}: {why}")

    # The conflict rule. Keyed on quantity AND population together, because two rows
    # measuring the same thing in different patients are not a disagreement -- KDIGO
    # targets SBP <120 in CKD and AHA/ACC targets <130/80 in general adults, and
    # calling that a contradiction would be the sheet inventing one. That ruling is
    # the clinician's; this is the mechanism it asked for.
    seen: dict[tuple[str, str], set[str]] = {}
    for row in sheet.rows:
        seen.setdefault((row.quantity, row.population), set()).add(row.value)
    for (quantity, population), values in sorted(seen.items()):
        if len(values) > 1 and quantity.lower() not in sheet.conflicts:
            failures.append(
                f"{sheet.path.name}  quantity '{quantity}' for population '{population}' "
                f"has {len(values)} different values ({', '.join(sorted(values))}) "
                f"and no 'CONFLICT: {quantity}' block under '## Conflicts'"
            )
    return failures


def gate_citation_tier1(sheet: Sheet) -> list[str]:
    """Every number in a row's value must appear in that row's snippet.

    Runs on every machine, which is the point. Tier 2 needs 410 MB of PDFs that live
    outside this repo, so on a fresh clone it has nothing to resolve -- and a gate
    that silently drops to zero there is the same hole `phi_scan.py`'s corpus layer
    documents and that #93 watched fire for real.
    """
    failures: list[str] = []
    for row in sheet.rows:
        wanted = _NUMBER.findall(row.value)
        if not wanted:
            continue
        present = set(_NUMBER.findall(row.snippet))
        missing = [number for number in wanted if number not in present]
        if missing:
            failures.append(
                f"{sheet.path.name}:{row.line}  value '{row.value}' has "
                f"{', '.join(missing)} which the snippet does not contain"
            )
    return failures


def gate_citation_tier2(sheet: Sheet, pdf_root: Path | None) -> tuple[list[str], str | None, int]:
    """Every snippet must appear on the page it cites.

    Returns ``(failures, skip reason, rows declared RENDERED)``. The third value is
    separate from the skip reason on purpose: "tier 2 did not run at all" and "tier 2
    ran and 3 rows opted out of it" are different events, and a sentinel smuggled
    through the skip channel would have made a sheet that declared every row rendered
    indistinguishable from one graded cleanly.

    A skip is returned rather than raised, and the caller prints it as a banner. The
    whole design of decision 2 is that this **must not be readable as passing**.
    """
    if pdf_root is None or not pdf_root.is_dir():
        return [], f"source PDFs not found at {pdf_root}", 0
    try:
        import pymupdf
    except ImportError:
        return [], "pymupdf is not installed", 0

    failures: list[str] = []
    rendered = 0
    cache: dict[tuple[str, int], str] = {}
    for row in sheet.rows:
        if row.snippet.startswith(RENDERED_MARKER):
            # Declared as read off the page as typeset. Tier 2 genuinely cannot check
            # it, and saying so beats resolving a string the page does not contain and
            # reporting a citation failure that is really an extraction failure.
            rendered += 1
            continue
        source = sheet.sources.get(row.source)
        if not source or row.page is None:
            continue  # already a SCHEMA failure; not counted twice
        relative = source["document"]
        key = (relative, row.page)
        if key not in cache:
            path = pdf_root / f"{relative}.pdf"
            if not path.is_file():
                failures.append(f"{sheet.path.name}:{row.line}  no such PDF: {path}")
                cache[key] = ""
                continue
            document = pymupdf.open(str(path))
            try:
                cache[key] = _normalize(document[row.page - 1].get_text("text"))
            except Exception as error:  # noqa: BLE001
                failures.append(f"{sheet.path.name}:{row.line}  page {row.page} unreadable: {error}")
                cache[key] = ""
            finally:
                document.close()
        page_text = cache[key]
        if page_text and _normalize(row.snippet) not in page_text:
            failures.append(
                f"{sheet.path.name}:{row.line}  snippet not on {relative} p.{row.page}"
            )
    return failures, None, rendered


def _normalize(text: str) -> str:
    """Whitespace-flattened and dash-folded, for comparing a snippet to a page.

    A snippet is copied out of a table cell and the page sets the same words with a
    line break in the middle of them; comparing raw would fail on typography rather
    than on the citation. Nothing here touches a digit.
    """
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
    text = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def gate_coverage(sheet: Sheet, recs: dict | None) -> tuple[list[str], list[str], int]:
    """Gate 2. Returns (refusals, warnings, ungraded-source-count).

    Refuses on an ``exact`` source and warns on a ``bound`` one, and **the mode is
    read off the recommendation record rather than decided here** -- what makes a
    count enforceable is that the recommendations were ruled into a table, not that
    the number looked tidy.
    """
    if recs is None:
        return [], [], 1

    mode = recs.get("mode")
    known = {record["rec_id"] for record in recs.get("recommendations", ())}
    cited = {row.rec for row in sheet.rows}
    unaccounted = sorted(known - cited - set(sheet.scoped_out))

    # **Structural findings, and they refuse whatever the mode is.** The refuse-or-warn
    # split exists because a marker COUNT over-reports; it says nothing about whether a
    # sheet's own declarations are self-consistent. Routing these through it would let
    # a bound source declare itself exact and carry a mis-pinned class unremarked.
    structural: list[str] = []

    # **The sheet's declared mode must agree with the record's, and a disagreement is
    # a refusal rather than a preference for one of them.** README.md tells a reader
    # that `mode` is what decides whether omissions are refused or warned about; a
    # sheet declaring `exact` over a `bound` record would make that sentence false
    # while every gate passed. Neither value is trusted over the other because only
    # the disagreement is knowable -- what produced it is not.
    for key, source in sorted(sheet.sources.items()):
        declared = source.get("mode", "").strip().lower()
        if declared and mode and declared != mode:
            structural.append(
                f"{sheet.path.name}  source '{key}' declares mode '{declared}' but its "
                f"recommendation record is '{mode}'. README.md says mode decides whether "
                f"omission refuses or warns, so these cannot disagree."
            )

    # A row's class must be the class of the recommendation it cites. This is the one
    # thing here that catches a row pinned to the WRONG recommendation -- every other
    # gate would pass such a row, because its number is real and its snippet is on the
    # page it names. It is not a substitute for reading: a row can cite the right
    # recommendation and still describe it wrongly, which stays in the holes list.
    classes = {
        record["rec_id"]: str(record.get("cor") or "").lower()
        for record in recs.get("recommendations", ())
    }
    for row in sheet.rows:
        expected = classes.get(row.rec)
        if expected and row.klass.strip().lower() != expected:
            structural.append(
                f"{sheet.path.name}:{row.line}  class '{row.klass}' does not match "
                f"{row.rec}, which is class '{expected}'"
            )

    # The #153 lesson, from this ticket's own comment: count the unread and put it in
    # the exit status, and fire on ANY unread item rather than on total absence. A
    # gate that only fires when nothing was covered reads green over 2.4% coverage.
    if not unaccounted:
        return structural, [], 0

    message = (
        f"{sheet.path.name}  {len(unaccounted)} of {len(known)} recommendations in "
        f"{recs.get('doc_id')} are neither a row nor scoped out: "
        + ", ".join(unaccounted[:6])
        + (f", and {len(unaccounted) - 6} more" if len(unaccounted) > 6 else "")
    )
    if mode == "exact":
        return structural + [message], [], 0
    return structural, [message + "  (source mode is 'bound', so this over-reports)"], 0


def gate_range(sheet: Sheet) -> tuple[list[str], int]:
    """Unit-keyed sanity bounds. Returns (failures, count of numbers not graded).

    The ungraded count is returned and printed rather than swallowed. A gate that
    silently grades 4 of a sheet's 200 numbers and reports a clean run is the shape
    #153 caught reading green over 2.4% coverage, and the fix there was the same:
    put the unread count where the verdict is.
    """
    failures: list[str] = []
    ungraded = 0
    for row in sheet.rows:
        graded_spans: list[tuple[int, int]] = []
        for match in _MEASURED.finditer(row.value):
            graded_spans.append(match.span("numbers"))
            bounds = UNIT_BOUNDS.get(re.sub(r"\s+", " ", match.group("unit").strip().lower()))
            if bounds is None:
                # A recognized unit with no bound -- hours, days, weeks. Matching it
                # is the point: it stops those numbers being attributed to whatever
                # unit appears elsewhere in the same value.
                ungraded += len(_NUMBER.findall(match.group("numbers")))
                continue
            low, high = bounds
            for raw in _NUMBER.findall(match.group("numbers")):
                number = float(raw.replace(",", ""))
                if not low <= number <= high:
                    failures.append(
                        f"{sheet.path.name}:{row.line}  {row.quantity} value {raw} "
                        f"{match.group('unit')} is outside the sanity range "
                        f"{low:g} to {high:g}"
                    )
        for number in _NUMBER.finditer(row.value):
            if not any(start <= number.start() < end for start, end in graded_spans):
                ungraded += 1
    return failures, ungraded


def grade(sheet_path: Path, recs_path: Path | None, pdf_root: Path | None, quiet: bool = False) -> int:
    """Grade one sheet. ``quiet`` suppresses the report, never a finding.

    That asymmetry is the whole contract of the flag: the pre-commit hook runs with
    it so a clean sheet costs the committer nothing, and a failing one still prints
    every FAIL line and the tier-2 banner. A quiet mode that could hide a refusal
    would be a way to make this gate silent, which is the thing #83's closing section
    is about.
    """
    def report(*args: object) -> None:
        if not quiet:
            print(*args)

    if not sheet_path.is_file():
        print(f"not a file: {sheet_path}", file=sys.stderr)
        return 2

    sheet = parse(sheet_path.read_text(encoding="utf-8"), sheet_path)
    report(f"== {sheet_path.name}")
    if not sheet.ok:
        print(f"  NOT GRADED  {sheet.why_not}", file=sys.stderr)
        print("  Nothing was checked. This is not a clean sheet.", file=sys.stderr)
        return 2

    # **Why the missing-file case is separated from the not-asked-for case.** They
    # produce the same `recs is None` and they are not the same event: one is a run
    # that never intended to check omission, the other is a run that meant to and
    # silently did not. The first version collapsed them by testing `recs_path is
    # None` at the bottom, so `--recs <a path that does not exist>` graded four gates,
    # printed nothing about the fifth, and exited 0. That is this ticket's own #153
    # lesson failing on this ticket's own gate, and it was found by review rather than
    # by a test -- so `TheExitStatusSaysWhichKindOfNotGraded` now pins all three.
    recs = None
    recs_missing = False
    if recs_path is not None:
        if recs_path.is_file():
            recs = json.loads(recs_path.read_text(encoding="utf-8"))
        else:
            recs_missing = True

    schema = gate_schema(sheet)
    tier1 = gate_citation_tier1(sheet)
    tier2, tier2_skip, rendered_rows = gate_citation_tier2(sheet, pdf_root)
    coverage_refusals, coverage_warnings, ungraded_sources = gate_coverage(sheet, recs)
    ranges, ungraded_rows = gate_range(sheet)

    report(f"  rows            {len(sheet.rows)}")
    report(f"  sources         {len(sheet.sources)}")
    report(f"  populations     {len(sheet.populations)}")
    report(f"  scoped out      {len(sheet.scoped_out)}")
    # `report`, not `print`: this blank line is part of the report and `--quiet`
    # promises to suppress the report and never a finding. As a bare `print` it was
    # the one piece of the report that survived --quiet, so the pre-commit hook
    # emitted a stray blank line on a clean sheet.
    report()
    report(f"  SCHEMA          {len(schema)}")
    report(f"  CITATION tier 1 {len(tier1)}")
    if tier2_skip:
        report(f"  CITATION tier 2 SKIPPED -- {tier2_skip}")
    else:
        report(f"  CITATION tier 2 {len(tier2)}")
        if rendered_rows:
            # Printed rather than only counted: the trace the escape hatch exists to
            # leave is worth nothing if the run that honors it stays silent about it.
            report(
                f"                  {rendered_rows} row(s) declared {RENDERED_MARKER} "
                "and were read off the rendered page, so tier 2 skipped them"
            )
    # **The report body has to carry this, not only stderr and the exit status.** A
    # gate that did not run printed `0 refusing, 0 warning` here, which is byte for
    # byte what a clean coverage pass prints. The notice went to stderr, so redirecting
    # stdout -- the only reason to print a report at all -- kept the reassuring line
    # and dropped the one that withdrew it. `CITATION tier 2` above already says
    # SKIPPED in the body for the same situation; this is that, for its reason.
    if recs_missing or ungraded_sources:
        report("  COVERAGE        NOT RUN -- omission was not checked")
    else:
        report(f"  COVERAGE        {len(coverage_refusals)} refusing, {len(coverage_warnings)} warning")
    report(f"  RANGE           {len(ranges)}  ({ungraded_rows} numbers carried no unit this grades)")

    if sheet.resolved_date:
        report(f"  last resolved   {sheet.resolved_date} against {sheet.resolved_corpus}")
    else:
        report("  last resolved   NOT RECORDED -- the sheet does not say when tier 2 last ran")

    if tier2_skip:
        print()
        print("  " + "=" * 66)
        print("  CITATION TIER 2 DID NOT RUN. This sheet has NOT been checked against")
        print("  the source PDFs on this machine. Tier 1 proved each value is in its")
        print("  own snippet; nothing here proved the snippet is on the page it cites.")
        print("  " + "=" * 66)

    refusals = schema + tier1 + tier2 + coverage_refusals + ranges
    for message in refusals:
        print(f"  FAIL  {message}", file=sys.stderr)
    for message in coverage_warnings:
        print(f"  WARN  {message}", file=sys.stderr)

    if recs_missing:
        print(f"  COVERAGE        NOT RUN -- no such file: {recs_path}", file=sys.stderr)
        print("  Omission was not checked. A recs path that does not resolve is a", file=sys.stderr)
        print("  typo, not a decision, and must not be graded as one.", file=sys.stderr)
    elif ungraded_sources:
        print("  COVERAGE        NOT RUN -- no --recs given, so omission was not checked", file=sys.stderr)

    if refusals:
        # 1 wins over 2 where both hold, and the message names the ungraded part so
        # the finding reads as a floor rather than the whole. Returning 2 would file
        # the strongest thing known about the sheet under the weakest heading --
        # `differential_scan.py`'s ordering, for its reason.
        if recs_missing or ungraded_sources:
            print(
                "  note: COVERAGE did not run, so the count above is a floor.",
                file=sys.stderr,
            )
        return 1
    if recs_missing or ungraded_sources:
        return 2
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sheet", type=Path, nargs="?", help="the sheet to grade")
    parser.add_argument("--all", action="store_true", help="grade every sheet in reference/thresholds/")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the report; findings and the tier-2 banner still print",
    )
    parser.add_argument("--recs", type=Path, default=None, help="guidelines_recs.py JSON for the source")
    parser.add_argument(
        "--recs-root",
        type=Path,
        default=Path(os.environ.get("CLINICAL_GUIDELINES_RECS", "C:/codeing/guidelines-index")),
        help="where --all looks for recs-<sheet>.json (outside the repo, always)",
        # Deliberately NOT a spelling of guidelines_index.py's
        # CLINICAL_GUIDELINES_INDEX, which names a database file. This names a
        # directory of recommendation records, and two env vars one word apart that
        # mean different kinds of thing is how the wrong one gets set.
    )
    parser.add_argument(
        "--pdf-root",
        type=Path,
        default=Path("C:/codeing/guidelines-src"),
        help="corpus root for citation tier 2 (absent is reported, never passed)",
    )
    args = parser.parse_args(argv)

    if args.all:
        sheets = sorted(SHEET_ROOT.glob("*.md"))
        sheets = [path for path in sheets if path.name.lower() != "readme.md"]
        if not sheets:
            print(f"no sheet under {SHEET_ROOT}", file=sys.stderr)
            return 2
        worst = 0
        for path in sheets:
            # Resolved OUTSIDE the repo, and that is not a convention. A recs file
            # holds the society's recommendation text in full -- which is the
            # copyrighted expression #83 exists to avoid committing, and which
            # `guidelines_recs.ensure_outside_repo` refuses to write here. Looking
            # for it beside the sheet would have quietly invited someone to put it
            # there to make `--all` work.
            recs = args.recs_root / f"recs-{path.stem}.json"
            worst = max(worst, grade(path, recs if recs.is_file() else args.recs, args.pdf_root, args.quiet))
        return worst

    if not args.sheet:
        parser.error("give a sheet, or --all")
    return grade(args.sheet, args.recs, args.pdf_root, args.quiet)


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
