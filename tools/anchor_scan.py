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

The complete boundary of a clean result is declared in
``anchor_scan.DECLARED_LIMITS``.

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

"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import run_grader
from worksheet_grammar import CODE, ENTRY, entry_is_for_entry, paired_entry

SOURCE = re.compile(r"(?mi)^[ \t]*SOURCE[ \t]*:[ \t]*(.*?)[ \t]*$")
CONFIDENCE = re.compile(r"(?mi)^[ \t]*CONFIDENCE[ \t]*:[ \t]*(.*?)[ \t]*$")
FILLED = re.compile(r"(?i)^filled\b")
CDC_COMPUTED = re.compile(
    r"(?i)^verified against ICD-10-CM FY2026 and "
    r"CDC 2022 Extended BMI-for-Age\.?$"
)

# ``icd10-cpt`` step 4's heading. The lookbehind is the load-bearing part: ``NOT
# CODED, ANCHOR WAS FILLED`` is the pre-#46 heading, and reading it as this block
# would score a run that refused every filled anchor as one that marked them all.
BLOCK_HEADING = re.compile(
    r"(?i)^---[ \t]+CODED,[ \t]*ANCHOR[ \t]+WAS[ \t]+FILLED\b.*---[ \t]*$"
)
STEP_FOUR_START = re.compile(
    r"(?im)^---[ \t]+(?:CODED,[ \t]*ANCHOR[ \t]+WAS[ \t]+FILLED\b|"
    r"NOT[ \t]+CODED,[ \t]+NOTHING[ \t]+ESTABLISHED[ \t]+IT\b).*---[ \t]*$"
)

# Any other ``--- ... ---`` or Markdown heading closes the block.
OTHER_HEADING = re.compile(r"^[ \t]*(?:-{3,}|#{1,6}[ \t])")

# ``Z68.36 - BMI 36.4 ...``. The bare code is pinned at the start of its line by a
# dash, which is what makes this a line format rather than a substring search.
#
# **Three code shapes, and the second two are why this is not the ICD-10 pattern.**
# A CPT code is five digits and a HCPCS code is a letter and four, so a pattern
# written for ``Z68.36`` reads a marked ``99406`` as unlistable and fails a run that
# listed it correctly. ``icd10-cpt`` step 3 says CPT entries take the same shape as
# ICD-10 ones, so a filled-anchored procedure owes the same block line.
LISTING = re.compile(
    rf"^(?![^\r\n]*\*\*)[ \t]*({CODE})\b[ \t]+(?:--?|[–—])[ \t]+\S"
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

DECLARED_LIMITS = (
    (
        "whether the right codes were marked from filled note inputs",
        "Questions outside the worksheet compare it with a note that is not in the run directory.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "NOT FOR ENTRY entries",
        "An entry marked NOT FOR ENTRY is excluded from the proposed-code population.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "recognized code-entry openings",
        "Only lines beginning ICD-10, CPT, or HCPCS open entries; #1066 owns partial reads of other forms.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "recognized filled-anchor listing lines",
        "A listing is read only as a code followed by a dash and value on its own line.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "recognized SOURCE marks",
        "Only a SOURCE label whose value begins with filled marks its paired code; other values join the orphan count.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "filled-anchor block closing headings",
        "Any horizontal-rule or Markdown heading line ends the collected listing block.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "filled-anchor block opening form",
        "Only the delimited heading at line start opens the filled-anchor block; a Markdown prefix does not.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "contiguous indented detail pairing",
        "A detail belongs to the nearest entry above only across non-blank indented lines; orphans are reported, not gated.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "pediatric-band computation",
        "The command accepts the required CONFIDENCE sentence and does not recompute BMI-for-age.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "per-run gradeable coverage",
        "A worksheet with no mark, listing, or pediatric band adds nothing beside readable worksheets; #1066 owns the repair.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
)


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
    orphaned_details: int = 0


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
    orphaned_details: int = 0
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
        if BLOCK_HEADING.match(line):
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

    entries = [
        (match.start(), match.group("code"), entry_is_for_entry(text, found, index))
        for index, match in enumerate(found)
    ]

    step_four = next(
        (match.start() for match in STEP_FOUR_START.finditer(text)), len(text)
    )

    def owner(match: re.Match[str]) -> tuple[int, str, bool] | None:
        """The entry a detail line belongs to inside the pairing population."""
        if match.start() >= step_four:
            return None
        owned_match = paired_entry(text, found, match)
        if owned_match is None:
            return None
        index = found.index(owned_match)
        return index, owned_match.group("code"), entries[index][2]

    marked: set[str] = set()
    orphaned = 0
    for match in SOURCE.finditer(text):
        if match.start() >= step_four:
            continue
        held = owner(match)
        if held and held[2] and FILLED.search(match.group(1)):
            marked.add(held[1])
        elif held is None or not FILLED.search(match.group(1)):
            orphaned += 1

    pediatric_entries = [
        (index, code)
        for index, (_start, code, for_entry) in enumerate(entries)
        if for_entry and PEDIATRIC_BAND.match(code)
    ]
    pediatric_indexes = {index for index, _code in pediatric_entries}
    computed: set[int] = set()
    for match in CONFIDENCE.finditer(text):
        if match.start() >= step_four:
            continue
        held = owner(match)
        if held is None:
            orphaned += 1
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
        orphaned_details=orphaned,
    )


def worksheet_findings(sheet: Worksheet) -> list[Finding]:
    """The two tests, applied to one worksheet."""
    found: list[Finding] = []
    if sheet.has_block:
        found.extend(
            Finding(
                UNLISTED_MARK,
                code,
                "carries SOURCE: filled, absent from the icd10-cpt step-4 block",
            )
            for code in sorted(sheet.marked - sheet.listed)
        )
        found.extend(
            Finding(
                UNMARKED_LISTING,
                code,
                "listed under CODED, ANCHOR WAS FILLED, carries no SOURCE line",
            )
            for code in sorted(sheet.listed - sheet.marked)
        )
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
        orphaned_details=sum(sheet.orphaned_details for sheet in sheets),
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
        f"  orphaned detail lines               {scan.orphaned_details}",
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
