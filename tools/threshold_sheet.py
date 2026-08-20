"""Grade a distilled threshold sheet against the guideline it claims to come from.

    python tools/threshold_sheet.py <sheet.md> [--recs <key>=<recs.json> ...] [--pdf-root <dir>]
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

    **One recommendation record per SOURCE, not per sheet** --
    [#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177). It took
    one ``--recs`` for the whole sheet and never filtered ``known`` by ``row.source``,
    so a sheet citing two societies had the named source's omissions checked and the
    other's silently not; the count that would have surfaced it was derived from
    ``recs is None`` and could not exceed 1 however many sources were skipped. #83
    decision 3 makes multi-source the normal case -- one row per society with a
    ``CONFLICT`` block where they disagree -- so the first sheet carrying ADA beside
    AHA/ACC would have hit it, and hit it reading green. ``--recs`` is
    ``<source key>=<path>`` now and ``--recs-root`` resolves ``recs-<source key>.json``,
    and a sheet where **any** source has no record exits 2.

``RANGE``   refuses
    Per-quantity bounds. A BP target of 1300, an eGFR of 450, a dose three orders of
    magnitude off. Decimal-place and unit errors are the highest-consequence
    extraction failures and the cheapest to catch, because catching them needs no
    understanding of the guideline at all. **It also refuses a value carrying a
    character that is not a comparison operator** -- a Symbol-font ``\u00a3`` or
    ``\u2021`` where the source meant ``<=`` or ``>=``. The mis-encoded slots are
    imported from ``guidelines_extract.SYMBOL_FONT_OPERATORS`` rather than listed
    here, and **two of them no gate in this file can reach**: see
    ``UNREACHABLE_IN_A_TABLE_CELL``. How many there are is that table's to say.

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
- **A row citing a ``rec_id`` its source's record does not carry.** ``COVERAGE``
  subtracts what was cited from what the record holds, so an identifier belonging to
  nothing simply reduces nothing -- and the class check declines rather than inventing
  a disagreement, because there is no class to compare against. Named here when the
  rows were partitioned by source on #177; it was equally true of the one-record
  version and equally invisible.
- **Anything at all about a ``bound`` source.** ``COVERAGE`` warns and moves on.

**Deliberately not built, because it would pass for the wrong reason**: any gate
that re-extracts a value and compares it to the sheet through the path that wrote
the sheet. ``tools/test_icd10.py`` runs against committed excerpts and never against
the shipped database for precisely this reason. It is the most natural check to
write here and it is worthless.

Exit status
-----------

``0`` clean. ``1`` a gate that refuses found something. ``2`` **every way of not
having graded** -- no sheet, no rows in it, an unreadable Sources table, **any source
with no recommendation record**, and a ``--recs`` argument naming a source the sheet
does not declare. A sheet whose rows were written in a shape the parser does not read
would otherwise report zero violations and look like a pass, which is
`differential_scan.py`'s ruling and the shape #153 caught in the wild at 2.4%
coverage reading green.

Where 1 and 2 both hold, **1 wins**, and the message names every source that was not
graded so the finding reads as a floor rather than the whole.

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

import guidelines_extract
from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent
SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"

# Where `recs-<key>.json` is looked for when `--recs-root` is not given. A module
# constant rather than an inline default so the literal can be graded: an env var
# can change what `parse_args` produces, and a test reading that would be measuring
# the machine it ran on.
DEFAULT_RECS_ROOT = "C:/codeing/guidelines-index"

# **This module takes no write guard, and #176 asked for that to be a decision
# rather than an absence** -- its own first comment: *"an absent guard is easy to
# read as an oversight when it is a choice."* Ruled while consolidating the four,
# 2026-08-19.
#
# The three writers and `name_index` all refuse a *write* inside a checkout. This
# module only ever reads: `bind_recs` opens `recs-<key>.json` and nothing here
# creates one. Guarding a read would refuse a record that already exists, which
# prevents nothing -- whatever put it there was the guarded step, and refusing to
# read it turns one module's escaped artifact into a second module's failure.
#
# **What is enforceable is the default, and one property of it is.** A *relative*
# default resolves against the working directory, and the working directory when
# these tools are run is a checkout -- so a relative default is the convention
# encoded wrong, silently, in the one place the ticket named as encoding it
# without enforcing it. `test_write_guards.py` grades that.
#
# **What is not enforceable is the value.** `DEFAULT_RECS_ROOT` names a directory
# on the maintainer's machine, and asserting `enclosing_checkout` finds no
# checkout above it would be asserting a fact about *that* machine -- on a POSIX
# runner the drive-letter form resolves under the working directory and the check
# would fail for a reason that has nothing to do with the convention. Declared
# rather than half-checked.
WHY_NO_WRITE_GUARD = (
    "threshold_sheet reads recs-<key>.json and never writes one, so it takes no "
    "write guard. What it shares with the four writers is the convention about "
    "where such a record lives, and the enforceable half of that is that its "
    "default is absolute -- a relative one would resolve inside the checkout the "
    "command was run from."
)

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
# the corpus rather than about taste: two fonts in it render a comparison operator
# through a slot their own encoding does not describe, so what a reader hands back
# is a pound sign, a double dagger or a control code. A sheet is allowed to hold
# the fact and must not hold the mis-encoding, because those sort and compare
# differently from `<=` and only one of them is readable back to a clinician.
#
# **The mis-encoded slots are imported rather than listed**, on
# `test_spelling_scan.py`'s reasoning: `guidelines_extract` is where they are
# measured and where a sixth would be added, and a gate holding its own copy of
# that list is one that reads as agreement while covering less.
#
# **It covered less until #172.** Written by hand, it blocked `\u00a3` and `\u00b3` -- and
# `\u00b3` is a slot the corpus does not contain, while the double dagger carrying most
# of that corpus's greater-or-equal signs was not blocked at all. So the guard #172
# was told to rely on refused the character the ticket named and passed the one the
# ticket had missed. **Every count behind that sentence lives on
# `SYMBOL_FONT_OPERATORS` and none is restated here** -- a first draft of this
# comment copied two of them in, which is #143 arriving inside the paragraph
# arguing that a copied list reads as agreement while covering less.
#
# `\u00b3` stays. It is the Symbol font's greater-or-equal slot decoded through cp1252,
# which is what a *different* reader on a *different* machine would hand back from
# the same PDFs -- a sheet is transcribed by a person who may not be using this
# module's extraction at all.

# Two of the extractor's slots that no gate in this file can reach, named here so
# the coverage claim above is not read as wider than it is. Both are Python's
# doing rather than this module's, and `TwoSlotsNoGateHereCanReach` in
# `tools/test_threshold_sheet.py` demonstrates each rather than asserting it:
#
#   U+001F  `str.strip()` counts U+001C to U+001F as whitespace, so `_cells`
#           removes it and the row reads as a bare number -- the corpus defect
#           reproduced inside the artifact built to refuse it.
#   U+001E  `str.splitlines()` breaks on it, so the row is two half-lines, neither
#           is a table row, and the sheet parses clean with the row simply gone.
#           That is worse than a wrong value: nothing is left to be wrong.
#
# Not repaired here, because both repairs are wider than the ticket that found
# them: `strip(" \t")` changes what every cell in every sheet may carry, and
# nothing about `splitlines` is local to this file. The exposure is what #172
# narrowed -- the only path that put such a character in front of a transcriber
# was the extracted corpus, and `guidelines_extract` writes `<=` and `>=` there
# now. What is left is a paste from a raw reader.
UNREACHABLE_IN_A_TABLE_CELL = ("\u001e", "\u001f")
# A blocklist and deliberately not an allowlist. An allowlist of operators was
# written here first and never referenced by any gate, while the docstring claimed
# it was enforced -- which is `test_spelling_scan.py`'s failure mode exactly: a rule
# that has drifted from the file a reader opens reads as agreement. It was removed
# rather than wired up, because a value legitimately carries no operator at all
# (`81 mg/day`, `monthly`, `3-6 months`) and an allowlist would have to permit the
# empty case, at which point it permits everything.
# How each of the extractor's replacements is written in ASCII, which is the form a
# value cell must use. A plain lookup rather than a conditional inside the message,
# for two reasons. A conditional labels every future replacement as whichever branch
# is the `else`, silently; a lookup raises. And a backslash inside an f-string
# *expression* is a syntax error before 3.12 -- the first version of this wrote
# `f"{'<=' if replacement == '\u2264' else '>='}"`, which parses here and would not
# have parsed on the 3.10 floor ADR 0002 sets. `ast.parse(feature_version=(3, 10))`
# does not see it, which is the same blindness CLAUDE.md already records for
# `int | None`, and the only interpreter on this machine is 3.14. Caught by review.
ASCII_OPERATOR = {"\u2264": "<=", "\u2265": ">="}

FORBIDDEN_IN_VALUE = {
    "\u2264": "a Unicode <=; write the ASCII <=",
    "\u2265": "a Unicode >=; write the ASCII >=",
    "\u00b3": "a Symbol-font mis-encoding of >=; write >=",
    **{
        glyph: f"a Symbol-font mis-encoding of {ASCII_OPERATOR[replacement]}; "
               f"write {ASCII_OPERATOR[replacement]}"
        for mapping in guidelines_extract.SYMBOL_FONT_OPERATORS.values()
        for glyph, replacement in mapping.items()
    },
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


def bind_recs(
    sheet: Sheet, arguments: list[str], recs_root: Path | None
) -> tuple[dict[str, dict | None], dict[str, str], list[str]]:
    """Which recommendation record answers for each source the sheet declares.

    Returns ``({source key: record or None}, {source key: why there is none},
    [argument errors])``.

    **Per source and not per sheet, which is #177.** A sheet citing two societies used
    to be graded against whichever single record ``--recs`` named, and the other
    source's omissions went unchecked with nothing saying so -- the ungraded signal
    was derived from ``recs is None`` and so could not exceed 1 however many sources
    were skipped. The `source` column exists because #83 decision 3 makes
    multi-source the normal case: one row per society, with a ``CONFLICT`` block where
    they disagree.

    An argument is ``KEY=PATH``, or a bare path **only** where the sheet declares
    exactly one source. A bare path on a two-source sheet is an error rather than a
    guess, because guessing which source a record answers for is the defect this
    function exists to remove.

    **The lookup stays outside the repo.** ``recs_root`` resolves ``recs-<key>.json``
    and there is deliberately no fallback to the sheet's own directory: a record holds
    the society's recommendation text in full, which is the copyrighted expression the
    sheet format exists to avoid committing, and ``repo_root.ensure_outside_checkout``
    refuses to write one inside a checkout. A convenience that looked beside the sheet
    would quietly invite someone to put one there to make ``--all`` work.
    """
    errors: list[str] = []
    explicit: dict[str, Path] = {}
    for argument in arguments or ():
        key, separator, raw = str(argument).partition("=")
        if not separator:
            if len(sheet.sources) != 1:
                errors.append(
                    f"--recs {argument} names no source key, and the sheet declares "
                    f"{len(sheet.sources)} sources ({', '.join(sorted(sheet.sources)) or 'none'}), "
                    "so which source it answers for is unknowable. Write --recs <key>=<path>."
                )
                continue
            key, raw = next(iter(sheet.sources)), argument
        if key not in sheet.sources:
            errors.append(
                f"--recs names source '{key}', which the sheet does not declare under "
                f"'## Sources' ({', '.join(sorted(sheet.sources)) or 'none'}). A record "
                "bound to nothing checks nothing."
            )
            continue
        if key in explicit:
            errors.append(f"--recs names source '{key}' twice")
            continue
        explicit[key] = Path(raw)

    records: dict[str, dict | None] = {}
    why_not: dict[str, str] = {}
    for key in sorted(sheet.sources):
        path = explicit.get(key)
        named = path is not None
        if path is None and recs_root is not None:
            path = recs_root / f"recs-{key}.json"
        records[key] = None
        if path is None:
            why_not[key] = "no --recs given for this source, so omission was not checked"
        elif not path.is_file():
            # The typo and the never-built record are not the same event, which is
            # `TheExitStatusSaysWhichKindOfNotGraded`'s finding read one level down: a
            # path somebody typed that does not resolve is a mistake, and a record
            # nobody has built yet is a machine without the corpus.
            why_not[key] = (
                f"no such file: {path}" if named else f"no recommendation record at {path}"
            )
        else:
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                why_not[key] = f"unreadable recommendation record {path}: {error}"
            else:
                # **A file that parses and is not a record is the same event as one
                # that does not parse**, and it arrives through a door that looks
                # legitimate: `null` and `[]` are valid JSON. Untyped, `null` left
                # `records[key]` None with no `why_not` entry and the report raised a
                # KeyError, and `[]` reached `gate_coverage` and raised there. A
                # traceback out of the pre-commit hook is not a verdict.
                if isinstance(loaded, dict):
                    records[key] = loaded
                else:
                    why_not[key] = (
                        f"unreadable recommendation record {path}: "
                        f"the file holds a JSON {type(loaded).__name__}, not a record"
                    )
    # **The invariant the report reads is that every absent record says why**, and it
    # is pinned by a test rather than asserted here: it was false for one branch --
    # the JSON `null` above -- and the symptom was a KeyError in `grade` rather than
    # anything a reader could act on. `EveryAbsentRecordSaysWhy` walks all four ways
    # of not having one.
    return records, why_not, errors


def _record_built_from_another_document(recs: dict, source: dict[str, str]) -> str:
    """The PDF the record came from, when that is not the one this source names.

    Empty where they agree and where either side is silent -- so this refuses only a
    knowable disagreement, which is the mode cross-check's own rule.

    **The hazard is one #177's own fix introduces.** The record lookup is keyed on a
    source key that is *sheet-local*, so two sheets using ``aha`` for different
    guidelines resolve the same ``recs-aha.json`` and each is graded against the
    other's document -- silently, because a ``rec_id`` absent from the record is never
    counted as omitted and every other gate reads the sheet alone.

    **It reads the record's ``source`` and deliberately NOT its ``doc_id``, and that
    is the one thing to know before "fixing" this.** ``doc_id`` is whatever
    ``guidelines_recs.py --doc-id`` was given and is free text: the record behind the
    committed hypertension sheet carries ``AHA ACC/jones-et-al-2025`` while the sheet's
    ``document`` cell carries the full stem, and comparing those would refuse the one
    correct sheet in the repo. ``source`` is the PDF path, which is the same file the
    ``document`` cell names -- tier 2 opens ``pdf_root / f"{document}.pdf"``, so the
    suffix convention is the sheet format's already and not invented here.

    Compared on the FILENAME alone: where the corpus was mounted when the record was
    built is not a finding.
    """
    built_from = Path(str(recs.get("source") or "").replace("\\", "/")).name
    document = Path(source.get("document", "").strip().replace("\\", "/")).name
    if not built_from or not document:
        return ""
    return "" if built_from.lower() == f"{document.lower()}.pdf" else built_from


def gate_coverage(
    sheet: Sheet, records: dict[str, dict | None]
) -> tuple[list[str], list[str], list[str]]:
    """Gate 2. Returns (refusals, warnings, the source keys that were not graded).

    Refuses on an ``exact`` source and warns on a ``bound`` one, and **the mode is
    read off the recommendation record rather than decided here** -- what makes a
    count enforceable is that the recommendations were ruled into a table, not that
    the number looked tidy.

    **Every check in here is per source since #177**: ``known`` is filtered to the
    rows citing that source, the mode cross-check compares a source's declaration
    against its own record, and the class check reads the record of the source the row
    cites. A ``rec_id`` is unique within a document and nothing makes it unique across
    two, so a row citing one society could otherwise discharge another's omission.
    """
    refusals: list[str] = []
    warnings: list[str] = []
    ungraded: list[str] = []

    for key in sorted(sheet.sources):
        recs = records.get(key)
        if recs is None:
            ungraded.append(key)
            continue

        mode = recs.get("mode")
        known = {record["rec_id"] for record in recs.get("recommendations", ())}
        rows = [row for row in sheet.rows if row.source == key]
        unaccounted = sorted(known - {row.rec for row in rows} - set(sheet.scoped_out))

        # **Structural findings, and they refuse whatever the mode is.** The
        # refuse-or-warn split exists because a marker COUNT over-reports; it says
        # nothing about whether a sheet's own declarations are self-consistent.
        # Routing these through it would let a bound source declare itself exact and
        # carry a mis-pinned class unremarked.

        # **The sheet's declared mode must agree with the record's, and a disagreement
        # is a refusal rather than a preference for one of them.** README.md tells a
        # reader that `mode` is what decides whether omissions are refused or warned
        # about; a sheet declaring `exact` over a `bound` record would make that
        # sentence false while every gate passed. Neither value is trusted over the
        # other because only the disagreement is knowable -- what produced it is not.
        built_from = _record_built_from_another_document(recs, sheet.sources[key])
        if built_from:
            refusals.append(
                f"{sheet.path.name}  source '{key}' names document "
                f"'{sheet.sources[key].get('document', '').strip()}' but its recommendation "
                f"record was built from '{built_from}'. A record bound to the wrong source "
                "grades that source against another guideline."
            )

        declared = sheet.sources[key].get("mode", "").strip().lower()
        if declared and mode and declared != mode:
            refusals.append(
                f"{sheet.path.name}  source '{key}' declares mode '{declared}' but its "
                f"recommendation record is '{mode}'. README.md says mode decides whether "
                f"omission refuses or warns, so these cannot disagree."
            )

        # A row's class must be the class of the recommendation it cites. This is the
        # one thing here that catches a row pinned to the WRONG recommendation --
        # every other gate would pass such a row, because its number is real and its
        # snippet is on the page it names. It is not a substitute for reading: a row
        # can cite the right recommendation and still describe it wrongly, which stays
        # in the holes list.
        classes = {
            record["rec_id"]: str(record.get("cor") or "").lower()
            for record in recs.get("recommendations", ())
        }
        for row in rows:
            expected = classes.get(row.rec)
            if expected and row.klass.strip().lower() != expected:
                refusals.append(
                    f"{sheet.path.name}:{row.line}  class '{row.klass}' does not match "
                    f"{row.rec}, which is class '{expected}'"
                )

        # The #153 lesson, from this ticket's own comment: count the unread and put it
        # in the exit status, and fire on ANY unread item rather than on total
        # absence. A gate that only fires when nothing was covered reads green over
        # 2.4% coverage.
        if not unaccounted:
            continue

        message = (
            f"{sheet.path.name}  source '{key}': {len(unaccounted)} of {len(known)} "
            f"recommendations in {recs.get('doc_id')} are neither a row nor scoped out: "
            + ", ".join(unaccounted[:6])
            + (f", and {len(unaccounted) - 6} more" if len(unaccounted) > 6 else "")
        )
        if mode == "exact":
            refusals.append(message)
        else:
            warnings.append(message + "  (source mode is 'bound', so this over-reports)")

    return refusals, warnings, ungraded


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


def grade(
    sheet_path: Path,
    recs_arguments: list[str] | None,
    pdf_root: Path | None,
    quiet: bool = False,
    recs_root: Path | None = None,
) -> int:
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
    # produce the same absent record and they are not the same event: one is a run
    # that never intended to check omission, the other is a run that meant to and
    # silently did not. The first version collapsed them by testing `recs_path is
    # None` at the bottom, so `--recs <a path that does not exist>` graded four gates,
    # printed nothing about the fifth, and exited 0. That is this ticket's own #153
    # lesson failing on this ticket's own gate, and it was found by review rather than
    # by a test -- so `TheExitStatusSaysWhichKindOfNotGraded` now pins all three.
    # Since #177 the distinction is drawn per source, in `bind_recs`, and kept in
    # `why_not` so the report can say which source and which of the two it was.
    records, why_not, recs_errors = bind_recs(sheet, recs_arguments or [], recs_root)

    schema = gate_schema(sheet)
    tier1 = gate_citation_tier1(sheet)
    tier2, tier2_skip, rendered_rows = gate_citation_tier2(sheet, pdf_root)
    coverage_refusals, coverage_warnings, ungraded_sources = gate_coverage(sheet, records)
    ranges, ungraded_rows = gate_range(sheet)
    # An argument naming a source the sheet does not declare, or naming one twice, is
    # a typo and never a decision -- and it is a way of not having graded even when
    # every declared source resolved from `--recs-root`, because the run asked for
    # something and got nothing.
    # A sheet declaring no source has nothing for COVERAGE to iterate, which is a way
    # of not having graded and not a clean gate. SCHEMA refuses it too, so 1 wins --
    # this is what keeps the *report* from saying otherwise.
    not_graded = bool(ungraded_sources) or bool(recs_errors) or not sheet.sources

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
    #
    # **And it names how many sources, which is #177.** The count used to be derived
    # from `recs is None` and so could only ever be 0 or 1: a sheet citing four
    # societies with one record printed the same line as a sheet with one source and
    # one record. A partly checked sheet gets the unchecked half FIRST in the line,
    # because a count printed ahead of the caveat is read as the verdict.
    total_sources = len(sheet.sources)
    if not total_sources:
        # A sheet whose Sources table did not parse. SCHEMA refuses every row for an
        # undeclared source key, so the status is already 1 -- but the body line would
        # read `0 refusing, 0 warning`, which is byte for byte what a clean coverage
        # pass prints over a gate that had nothing to iterate.
        report("  COVERAGE        NOT RUN -- the sheet declares no source to check against")
    elif ungraded_sources and len(ungraded_sources) == total_sources:
        report(
            f"  COVERAGE        NOT RUN -- omission was not checked for any of "
            f"{total_sources} source(s): {', '.join(ungraded_sources)}"
        )
    elif ungraded_sources:
        report(
            f"  COVERAGE        NOT RUN for {len(ungraded_sources)} of {total_sources} "
            f"sources ({', '.join(ungraded_sources)}) -- {len(coverage_refusals)} refusing, "
            f"{len(coverage_warnings)} warning over the rest, so that is a floor"
        )
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

    for message in recs_errors:
        print(f"  COVERAGE        NOT RUN -- {message}", file=sys.stderr)
    for key in ungraded_sources:
        print(f"  COVERAGE        NOT RUN for source '{key}' -- {why_not[key]}", file=sys.stderr)
    if ungraded_sources or recs_errors:
        print("  Omission was not checked for the source(s) above. A source with no", file=sys.stderr)
        print("  recommendation record is not a source that passed, and a --recs path", file=sys.stderr)
        print("  that does not resolve is a typo rather than a decision.", file=sys.stderr)

    if refusals:
        # 1 wins over 2 where both hold, and the message names the ungraded part so
        # the finding reads as a floor rather than the whole. Returning 2 would file
        # the strongest thing known about the sheet under the weakest heading --
        # `differential_scan.py`'s ordering, for its reason.
        if not_graded:
            print(
                "  note: COVERAGE did not run on every source, so the count above is a floor.",
                file=sys.stderr,
            )
        return 1
    if not_graded:
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The command line, built apart from ``main`` so a test can read its defaults.

    `TheRecordsStayOutsideTheRepo` asserts against ``--recs-root``'s default here, and
    a default only a running command can observe is one no test pins.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sheet", type=Path, nargs="?", help="the sheet to grade")
    parser.add_argument("--all", action="store_true", help="grade every sheet in reference/thresholds/ (resolves from --recs-root; takes no --recs)")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the report; findings and the tier-2 banner still print",
    )
    parser.add_argument(
        "--recs",
        action="append",
        metavar="KEY=PATH",
        default=None,
        help=(
            "guidelines_recs.py JSON for one source, keyed by its '## Sources' key. "
            "Repeatable. A bare path is accepted only where the sheet declares exactly "
            "one source."
        ),
    )
    parser.add_argument(
        "--recs-root",
        type=Path,
        default=Path(os.environ.get("CLINICAL_GUIDELINES_RECS", DEFAULT_RECS_ROOT)),
        help="where recs-<source key>.json is looked for (outside the repo, always)",
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
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.all:
        # **`--all` takes no `--recs`, and refusing is cheaper than explaining.** A
        # bare path binds to *the* source of a one-source sheet, so one society's
        # record would bind to every sheet that cites one source; a keyed one binds by
        # a key that is sheet-local, so it lands on every sheet declaring that key and
        # exits 2 on every sheet that does not. Neither is a thing anybody means. The
        # directory mode resolves from `--recs-root` and nothing else.
        if args.recs:
            parser.error(
                "--all resolves recs-<source key>.json from --recs-root and takes no "
                "--recs: a source key is sheet-local, so which sheet's source a "
                "record answers for is unknowable across a directory. Name the sheet, "
                "or point --recs-root at the records."
            )

        sheets = sorted(SHEET_ROOT.glob("*.md"))
        sheets = [path for path in sheets if path.name.lower() != "readme.md"]
        if not sheets:
            print(f"no sheet under {SHEET_ROOT}", file=sys.stderr)
            return 2
        worst = 0
        for path in sheets:
            worst = max(worst, grade(path, [], args.pdf_root, args.quiet, args.recs_root))
        return worst

    if not args.sheet:
        parser.error("give a sheet, or --all")
    # `--recs-root` applies here too, and it did not before #177: `--all` resolved a
    # record and a named sheet did not, so the same sheet graded differently depending
    # on which way it was reached. One rule, and the root stays outside the repo --
    # see `bind_recs` for why there is no fallback beside the sheet.
    return grade(args.sheet, args.recs, args.pdf_root, args.quiet, args.recs_root)


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
