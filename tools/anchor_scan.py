"""Grade the mechanical limbs of ``fixtures/filled-anchor``'s ANCHOR class.

    python tools/anchor_scan.py <a run directory> [--show]

[#46] reversed the rule that set exists for. A code resting on a filled value is
no longer withheld -- it is **proposed and marked**, ``SOURCE: filled`` on the
code's own line *and* listed again under ``CODED, ANCHOR WAS FILLED``. The skill's
Completion section is explicit that it is **both, not one instead of the other**,
and that sentence is the whole of what this scans.

**Two tests, and neither needs a reader.**

- **The mark and the listing agree.** Every code carrying ``SOURCE: filled`` in the
  proposed list appears in ``icd10-cpt`` step 4's block, and every code that block
  lists carries ``SOURCE: filled`` on its entry. Either direction alone is the
  failure: a heading does not survive a line being copied out of the list, and a
  mark with no block entry is a disclosure the clinician's summary never shows.
  This is A1's, A2's and A5's fail condition with the reading taken out of it.
- **A pediatric band names the CDC computation.** [#123] retired the old test
  forbidding an ICD-only verification claim. Its replacement checks the evidence
  the new rule requires: every for-entry ``Z68.5-`` carries the affirmative line
  ``verified against ICD-10-CM FY2026 and CDC 2022 Extended BMI-for-Age`` in
  ``CONFIDENCE``. A bare ``verify this number`` -- or a sentence merely naming an
  unavailable table -- proves the calculator was skipped.

**What it cannot reach is the rest of ANCHOR, and that is permanent.** Whether a
note's BMI *had* a filled input, whether ``I10`` was rightly absent on a filled
pressure, whether case 4's ``Z68.25`` rests on two given values -- each is a
comparison of a worksheet to a note, and a note is not in this directory. **A clean
scan is not a walked row.** It says the marking is internally consistent, which is
what a copied line loses; it says nothing about whether the right codes were
marked. ``fixtures/filled-anchor``'s A3 in particular is invisible here: a run that
stopped coding the family altogether marks nothing, lists nothing, and is reported
below as **not having been scanned** rather than as clean.

**That last behavior is the point rather than an edge case.** Run 1 refused every
filled anchor it was offered and wrote them under the pre-#46 heading,
``NOT CODED, ANCHOR WAS FILLED``. This parser does not read that as the block --
the lookbehind on ``NOT`` is deliberate -- so a run reproducing run 1 reads as
having marked nothing and exits 2. A scanner that scored it clean would report a
pass for the exact behavior #46 reversed.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record; a
code with the value it rests on is a measurement attached to an encounter. Nothing
but integers is printed unless ``--show`` asks, and **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, on
``specificity_scan.py``'s arrangement and ``guidelines_search.py``'s before it: 0
when the marks and the listings agree, 1 on a violation, and **2 for every way of
not having scanned** -- no argument, no directory, no worksheets in it, and **no
marked code, listed code or pediatric band in any worksheet read.**

Since #405, a run with no gradeable subject prints its counts-only report before
the not-scanned diagnostic and exit 2. Earlier versions returned first and printed
no report; the moved stdout makes the coverage failure inspectable and puts this
grader on the shared finding-over-coverage ordering.

Extractor limits worth knowing before quoting a number:

- **A listing is a line whose code is pinned by a dash**, ``<code> - <value>``,
  which is ``icd10-cpt`` step 4's own form. It is deliberately not a substring
  search over the block: ``fixtures/filled-anchor``'s *Still unresolved* names the
  hazard, a run writing *"Z68.25 needs no SOURCE line, the inputs were given"*
  **inside** the block and putting the string exactly where a substring search
  looks. A run that lists its codes some other way -- a table, a prose paragraph
  -- reads here as having listed nothing, and every mark it carries then fails.
  That is a floor on the shapes this reads, not a floor on the exit status.
- **An entry opens on a line beginning ``ICD-10``, ``CPT`` or ``HCPCS``** followed
  by a code and a descriptor, and a ``SOURCE`` or ``CONFIDENCE`` line pairs with
  the most recent entry above it -- ``specificity_scan.py``'s pairing, for its
  reason.
- **A ``NOT FOR ENTRY`` entry is not a proposed code.** A differential carries
  three parts and no ``SOURCE``, so it has nothing to mark and nothing to list.
- **A ``SOURCE`` line marks its code when its value says ``filled``.** The skill
  writes ``SOURCE`` only on a filled anchor, but its opening sentence describes the
  line as saying *recorded or filled*, so a run writing ``SOURCE: recorded`` on an
  ordinary code is read as having marked nothing rather than as having marked it.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import run_grader

# ``ICD-10  Z68.36  Body mass index [BMI] 36.0-36.9, adult``. Shared with
# ``specificity_scan.py`` by shape rather than by import: the two read the same
# worksheet and each states its own pairing, so neither silently inherits the
# other's idea of what an entry is.
ENTRY = re.compile(
    r"(?mi)^[ \t]*(?:ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    r"([A-Z0-9][A-Z0-9.]*)[ \t]+(.+?)[ \t]*$"
)
SOURCE = re.compile(r"(?mi)^[ \t]*SOURCE[ \t]*:[ \t]*(.*?)[ \t]*$")
CONFIDENCE = re.compile(r"(?mi)^[ \t]*CONFIDENCE[ \t]*:[ \t]*(.*?)[ \t]*$")

# A code's own parts. These close an entry's header, so ``NOT FOR ENTRY`` is
# looked for above the first of them and never in the prose below.
FIELD = re.compile(r"(?mi)^[ \t]*(?:ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:")

# ``NOT FOR ENTRY`` at the end of any line of the entry's header, not only the
# code's own. An official descriptor can run past a line -- ``K27.9 Peptic ulcer,
# site unspecified, unspecified as acute or chronic, without hemorrhage or
# perforation`` is 96 characters -- and the mark then lands on the continuation.
# **A single-line reading counts four of this run's differential codes as proposed
# for entry**, which is exactly the defect [#70] describes: mandating a per-entry
# marker does not remove the ambiguity, it moves it from *what is an entry* to
# *what is a line*. Found by a reader after the suite was green.
NOT_FOR_ENTRY = re.compile(r"(?mi)[ \t]NOT FOR ENTRY[ \t]*$")

FILLED = re.compile(r"(?i)\bfilled\b")
CDC_COMPUTED = re.compile(
    r"(?i)^verified against ICD-10-CM FY2026 and "
    r"CDC 2022 Extended BMI-for-Age\.?$"
)

# ``icd10-cpt`` step 4's heading. The lookbehind is the load-bearing part: ``NOT
# CODED, ANCHOR WAS FILLED`` is the pre-#46 heading, and reading it as this block
# would score a run that refused every filled anchor as one that marked them all.
BLOCK_HEADING = re.compile(r"(?i)(?<!not )\bcoded,[ \t]*anchor[ \t]+was[ \t]+filled\b")

# Any other ``--- ... ---`` or Markdown heading closes the block.
OTHER_HEADING = re.compile(r"^[ \t]*(?:-{3,}|#{1,6}[ \t])")

# ``Z68.36 - BMI 36.4 ...``, with an optional bullet, optional bold markers and an
# optional code-set name in front. The code is pinned at the start of its line by a
# dash, which is what makes this a line format rather than a substring search.
#
# **Three code shapes, and the second two are why this is not the ICD-10 pattern.**
# A CPT code is five digits and a HCPCS code is a letter and four, so a pattern
# written for ``Z68.36`` reads a marked ``99406`` as unlistable and fails a run that
# listed it correctly. ``icd10-cpt`` step 3 says CPT entries take the same shape as
# ICD-10 ones, so a filled-anchored procedure owes the same block line.
CODE = r"(?:[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?|[0-9]{5}|[A-Z][0-9]{4})"
LISTING = re.compile(
    rf"^[ \t]*(?:[-*+][ \t]+)?\*{{0,2}}(?:(?:ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+)?"
    rf"({CODE})\b\*{{0,2}}[ \t]+(?:--?|[–—])[ \t]+\S"
)

PEDIATRIC_BAND = re.compile(r"(?i)^Z68\.5")

UNLISTED_MARK = "marked-not-listed"
UNMARKED_LISTING = "listed-not-marked"
PEDIATRIC_NOT_COMPUTED = "pediatric-not-computed"

ROWS = {
    UNLISTED_MARK: "fixtures/filled-anchor A1/A2/A5 - marked, not listed",
    UNMARKED_LISTING: "fixtures/filled-anchor A1/A2/A5 - listed, not marked",
    PEDIATRIC_NOT_COMPUTED: "fixtures/filled-anchor A1 - CDC computation",
}
KINDS = tuple(ROWS)


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    """One code failing one of the two tests."""

    code: str
    detail: str


@dataclass(frozen=True)
class Worksheet:
    """What one worksheet says about its filled anchors."""

    proposed: int
    marked: frozenset[str]
    listed: frozenset[str]
    has_block: bool
    pediatric: tuple[str, ...]
    pediatric_not_computed: tuple[str, ...]


@dataclass(frozen=True)
class Scan:
    """Counts over a run, plus the findings ``--show`` prints."""

    worksheets: int
    proposed: int
    marked: int
    listed: int
    with_block: int
    pediatric_bands: int
    unlisted_marks: int
    unmarked_listings: int
    pediatric_not_computed: int
    findings: tuple[Finding, ...] = ()

    @property
    def subjects(self) -> int:
        """How much there was to grade. Zero means nothing was scanned."""
        return self.marked + self.listed + self.pediatric_bands


def _block_lines(text: str) -> tuple[list[str], bool]:
    """The ``icd10-cpt`` step-4 block's lines, and whether its heading was found."""
    lines = text.splitlines()
    collected: list[str] = []
    found = False
    inside = False
    for line in lines:
        if BLOCK_HEADING.search(line):
            found = True
            inside = True
            continue
        if inside:
            if OTHER_HEADING.match(line):
                inside = False
                continue
            collected.append(line)
    return collected, found


def read_worksheet(text: str) -> Worksheet:
    """Parse one worksheet into its marks, listings and pediatric bands."""
    found = list(ENTRY.finditer(text))

    def header(index: int) -> str:
        """One entry's lines up to its first field line or the next entry.

        The span rather than the line, because a descriptor that wraps puts
        ``NOT FOR ENTRY`` on the continuation. Bounded on both sides so the mark
        cannot be borrowed from the entry below or from prose beneath the code.
        """
        start = found[index].start()
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        field = FIELD.search(text, start, end)
        return text[start : field.start() if field else end]

    entries = [
        (match.start(), match.group(1), not NOT_FOR_ENTRY.search(header(index)))
        for index, match in enumerate(found)
    ]

    def owner(position: int) -> tuple[int, str, bool] | None:
        """The entry a detail line belongs to -- the nearest one above it."""
        owned = None
        for index, (start, code, for_entry) in enumerate(entries):
            if start < position:
                owned = (index, code, for_entry)
            else:
                break
        return owned

    marked: set[str] = set()
    for match in SOURCE.finditer(text):
        held = owner(match.start())
        if held and held[2] and FILLED.search(match.group(1)):
            marked.add(held[1])

    pediatric_entries = [
        (index, code)
        for index, (_start, code, for_entry) in enumerate(entries)
        if for_entry and PEDIATRIC_BAND.match(code)
    ]
    pediatric_indexes = {index for index, _code in pediatric_entries}
    computed: set[int] = set()
    for match in CONFIDENCE.finditer(text):
        held = owner(match.start())
        if held and held[2] and held[0] in pediatric_indexes and CDC_COMPUTED.fullmatch(match.group(1)):
            computed.add(held[0])

    block, has_block = _block_lines(text)
    listed = {m.group(1) for line in block for m in [LISTING.match(line)] if m}

    return Worksheet(
        proposed=sum(1 for *_rest, for_entry in entries if for_entry),
        marked=frozenset(marked),
        listed=frozenset(listed),
        has_block=has_block,
        pediatric=tuple(code for _index, code in pediatric_entries),
        pediatric_not_computed=tuple(
            code for index, code in pediatric_entries if index not in computed
        ),
    )


def worksheet_findings(sheet: Worksheet) -> list[Finding]:
    """The two tests, applied to one worksheet."""
    found = [
        Finding(UNLISTED_MARK, code, "carries SOURCE: filled, absent from the icd10-cpt step-4 block")
        for code in sorted(sheet.marked - sheet.listed)
    ]
    found += [
        Finding(UNMARKED_LISTING, code, "listed under CODED, ANCHOR WAS FILLED, carries no SOURCE line")
        for code in sorted(sheet.listed - sheet.marked)
    ]
    found += [
        Finding(
            PEDIATRIC_NOT_COMPUTED,
            code,
            "pediatric band does not name CDC 2022 Extended BMI-for-Age computation",
        )
        for code in sorted(sheet.pediatric_not_computed)
    ]
    return found


def survey(sheets: list[Worksheet]) -> Scan:
    """Count across a run. Takes parsed worksheets rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift."""
    found = [finding for sheet in sheets for finding in worksheet_findings(sheet)]
    return Scan(
        worksheets=len(sheets),
        proposed=sum(sheet.proposed for sheet in sheets),
        marked=sum(len(sheet.marked) for sheet in sheets),
        listed=sum(len(sheet.listed) for sheet in sheets),
        with_block=sum(1 for sheet in sheets if sheet.has_block),
        pediatric_bands=sum(len(sheet.pediatric) for sheet in sheets),
        unlisted_marks=sum(1 for f in found if f.kind == UNLISTED_MARK),
        unmarked_listings=sum(1 for f in found if f.kind == UNMARKED_LISTING),
        pediatric_not_computed=sum(1 for f in found if f.kind == PEDIATRIC_NOT_COMPUTED),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no code unless ``show``."""
    # Plain ASCII throughout, on ``specificity_scan.py``'s reasoning: this prints
    # to a Windows console, where anything outside cp1252 comes back as a question
    # mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"anchor scan over {source}",
        "",
        f"  worksheets read                    {scan.worksheets}",
        f"    with an icd10-cpt step-4 block   {scan.with_block}",
        f"  codes proposed for entry           {scan.proposed}",
        f"    carrying SOURCE: filled          {scan.marked}",
        f"  codes listed in the block          {scan.listed}",
        f"  pediatric Z68.5- bands             {scan.pediatric_bands}",
        "",
        f"  A1/A2/A5 - marked, not listed      {scan.unlisted_marks}",
        f"  A1/A2/A5 - listed, not marked      {scan.unmarked_listings}",
        f"  A1 - pediatric not computed        {scan.pediatric_not_computed}",
    ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(f"    {finding.kind:<24} {finding.code:<9} {finding.detail}")
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    directory: Path
    texts: tuple[str, ...]


def _load(parsed: run_grader.Parsed) -> Source:
    directory = Path(parsed.source)
    if not directory.is_dir():
        raise run_grader.SourceError(f"no directory named {directory.name}")
    texts = tuple(run_grader.read_run_directory(directory))
    if not texts:
        raise run_grader.SourceError(f"no worksheets found in {directory.name}")
    return Source(directory, texts)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey([read_worksheet(text) for text in source.texts])
    diagnostics: list[str] = []
    if not scan.subjects:
        diagnostics.append(
            f"no marked code, listed code or pediatric band in"
            f" {scan.worksheets} worksheet(s) in {source.directory.name}."
            " Nothing was scanned -- this is not a clean run."
        )
    if scan.findings:
        diagnostics.append(
            f"\n{len(scan.findings)} code(s) fail fixtures/filled-anchor ANCHOR."
            " Re-run with --show to see which, and do not paste that output."
        )
    return run_grader.Grade(
        scan=scan,
        source=source.directory.name,
        findings_failed=bool(scan.findings),
        coverage_failed=not scan.subjects,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage="usage: anchor_scan.py <a run directory> [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
