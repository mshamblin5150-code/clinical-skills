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
  ``verified against ICD-10-CM FY<year> and CDC 2022 Extended BMI-for-Age`` in
  ``CONFIDENCE``, where the year is the committed release's fiscal year when the
  worksheet was written (preserved records keep the year they were verified against). A bare ``verify this number`` -- or a sentence merely naming an
  unavailable table -- proves the calculator was skipped.

The complete boundary of a clean result is declared in
``anchor_scan.DECLARED_LIMITS``.

No committed real note carries a T36-T65 poisoning code, so drug-column
descriptor agreement is exercised by synthetic controls only. That missing real
poisoning note remains a declared reading limit rather than being hidden by the
synthetic coverage.

**That last behavior is the point rather than an edge case.** Run 1 refused every
filled anchor it was offered and wrote them under the pre-#46 heading,
``NOT CODED, ANCHOR WAS FILLED``. The shared heading grammar keeps that phrase
separate from the filled-anchor block, so a run reproducing run 1 reads as
having marked nothing and exits 2. A scanner that scored it clean would report a
pass for the exact behavior #46 reversed.

**Counts with checked file labels by default.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record; a
code with the value it rests on is a measurement attached to an encounter. Clinical text
is printed only when ``--show`` asks, and **``--show`` output is PHI** on
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


File attribution uses ``run_grader.artifact_label`` for pasteable output; private
``--show`` finding lines carry real filenames. See ADR 0314.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import closing
from dataclasses import dataclass, field, replace
from enum import Enum
from functools import cache
from pathlib import Path

import run_grader
import reader_remarks
import completion_checks
from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result
from block_scan import ASSERTED, read_block
from repo_root import InsideCheckout, ensure_outside_checkout, scratch_root
from console_codec import require_python_floor, use_utf8
from worksheet_grammar import (
    BLOCK_HEADING, CODE, DIFFERENTIAL_HEADING, ENTRY, ENTRY_CANDIDATE, FIELD,
    REFUSAL_HEADING, STEP_FOUR_START, detail_belongs_to_entry, entry_is_for_entry,
    heading_counts, paired_entry,
)

SOURCE = re.compile(r"(?mi)^[ \t]*SOURCE[ \t]*:[ \t]*(.*?)[ \t]*$")
CONFIDENCE = re.compile(r"(?mi)^[ \t]*CONFIDENCE[ \t]*:[ \t]*(.*?)[ \t]*$")
FILLED = re.compile(r"(?i)^filled\b")
CDC_COMPUTED = re.compile(
    r"(?i)^verified against ICD-10-CM FY20\d{2} and "
    r"CDC 2022 Extended BMI-for-Age\.?$"
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
EM_LINE = re.compile(r"(?mi)^[ \t]*E/M[ \t]*:[ \t]*(?!None\b)\S")

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
        "remarks concealed in agreement answers",
        "A remark inside threshold or another free-text answer cannot be distinguished from ordinary evidence.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "CPT or HCPCS anchor placement on the line documenting today's act",
        "Whether the quoted line documents an act done in this encounter is a reading.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
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
        "The shared grammar reads bare, Markdown-prefixed, and plain Markdown block headings.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "descriptor words agreement route",
        "A clean descriptor-words route establishes that the reader's span is note text also quoted by the worksheet; it does not establish that those words state the descriptor.",
        run_grader.EvidenceDisposition.DECLARED_READING,
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
        "ADR 0230 leaves this declared because no admissible candidate population spans marks, listings, and pediatric bands.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "E/M descriptor agreement",
        "E/M lines are counted and excluded because their descriptors cannot settle place of service, patient status, and decision-making level.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "note-side ICD-10 database membership",
        "Only code-shaped tokens resolving in the committed ICD-10-CM database participate in the bind; a prose token that is also a valid code remains indistinguishable from a code.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "real poisoning descriptor agreement",
        "No committed real note carries a T36-T65 poisoning code; drug-column behavior has synthetic controls only.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "medicine column ground relevance",
        "A column ground must be verbatim note text, but whether it describes this medicine is the reader's judgment. Proper use outside the label and ground is not checked.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "drug intent prose negation scope",
        "Only not, no, denies, denied, without, negative for, and never negate following intent words, through the next comma, semicolon, or period. And and but do not end the scope; double negation is read as a single negation.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "writer self-grade independence and comparison",
        "Descriptor-words agreement is a reading; separation from private self-records is declared, not enforced. The report-only comparison regrades supplied records against the current paired files, not a historical saved grade.",
        run_grader.EvidenceDisposition.DECLARED_READING,
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
    unread_remainder: int = 0
    excluded_em: int = 0
    off_template_headings: int = 0
    heading_candidates: int = 0
    generic_differential_headings: int = 0


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
    unread_remainder: int = 0
    excluded_em: int = 0
    off_template_headings: int = 0
    heading_candidates: int = 0
    generic_differential_headings: int = 0

    attribution: run_grader.ReportAttribution = run_grader.ReportAttribution()

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
    step_four = next(
        (match.start() for match in STEP_FOUR_START.finditer(text)), len(text)
    )
    candidate_text = text[:step_four]
    found = list(ENTRY.finditer(text))
    candidate_strict_entries = list(ENTRY.finditer(candidate_text))

    entries = [
        (match.start(), match.group("code"), entry_is_for_entry(text, found, index))
        for index, match in enumerate(found)
    ]

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
    headings = heading_counts(text)

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
        unread_remainder=max(
            0,
            len(list(ENTRY_CANDIDATE.finditer(candidate_text)))
            - len(candidate_strict_entries),
        ) + headings.unread,
        excluded_em=len(EM_LINE.findall(text)),
        off_template_headings=headings.off_template,
        heading_candidates=headings.candidates,
        generic_differential_headings=headings.generic_differential,
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
    """Count across parsed worksheets. Command loading separately binds file attribution."""
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
        unread_remainder=sum(sheet.unread_remainder for sheet in sheets),
        excluded_em=sum(sheet.excluded_em for sheet in sheets),
        off_template_headings=sum(sheet.off_template_headings for sheet in sheets),
        heading_candidates=sum(sheet.heading_candidates for sheet in sheets),
        generic_differential_headings=sum(sheet.generic_differential_headings for sheet in sheets),
    )


def locate(artifacts: tuple[run_grader.RunArtifact, ...]) -> run_grader.ReportAttribution:
    """Retain each row's subjects without changing the grading population."""
    scans = [survey([read_worksheet(artifact.text)]) for artifact in artifacts]
    return run_grader.attribute_scans(artifacts, scans, {
        "unlisted_marks": lambda scan: scan.unlisted_marks,
        "unmarked_listings": lambda scan: scan.unmarked_listings,
        "pediatric_not_computed": lambda scan: scan.pediatric_not_computed,
        "orphaned_details": lambda scan: scan.orphaned_details,
        "heading_candidates": lambda scan: scan.heading_candidates,
        "generic_differential_headings": lambda scan: scan.generic_differential_headings,
        "off_template_headings": lambda scan: scan.off_template_headings,
        "unread_remainder": lambda scan: scan.unread_remainder,
    }, ('findings',))


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
        f"  E/M lines excluded                  {scan.excluded_em}",
        f"  orphaned detail lines               {scan.orphaned_details}{scan.attribution.suffix('orphaned_details')}",
        f"  keyword heading candidates         {scan.heading_candidates}{scan.attribution.suffix('heading_candidates')}",
        f"  generic Differential headings      {scan.generic_differential_headings}{scan.attribution.suffix('generic_differential_headings')}",
        f"  off-template block headings        {scan.off_template_headings}{scan.attribution.suffix('off_template_headings')}",
        run_grader.format_unread_remainder(scan.unread_remainder) + scan.attribution.suffix("unread_remainder"),
        "",
        f"  A1/A2/A5 - marked, not listed      {scan.unlisted_marks}{scan.attribution.suffix('unlisted_marks')}",
        f"  A1/A2/A5 - listed, not marked      {scan.unmarked_listings}{scan.attribution.suffix('unmarked_listings')}",
        f"  A1 - pediatric not computed        {scan.pediatric_not_computed}{scan.attribution.suffix('pediatric_not_computed')}",
    ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for index, finding in enumerate(scan.findings):
            lines.append(f"{scan.attribution.filename('findings', index)}    {finding.kind:<24} {finding.code:<9} {finding.detail}")
    return "\n".join(lines)


@dataclass(frozen=True)
class Source:
    directory: Path
    texts: tuple[str, ...]
    artifacts: tuple[run_grader.RunArtifact, ...] = ()


def _load(parsed: run_grader.Parsed) -> Source:
    directory = Path(parsed.source)
    if not directory.is_dir():
        raise run_grader.SourceError(f"no directory named {directory.name}")
    artifacts = tuple(run_grader.read_run_artifacts(directory))
    texts = tuple(artifact.text for artifact in artifacts)
    if not texts:
        raise run_grader.SourceError(f"no worksheets found in {directory.name}")
    return Source(directory, texts, artifacts)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey([read_worksheet(text) for text in source.texts])
    scan = replace(scan, attribution=locate(source.artifacts))
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
        coverage_failed=not scan.subjects or bool(scan.unread_remainder),
        diagnostics=tuple(diagnostics),
        reports=(run_grader.run_records_report(source.directory),),
    )


GRADER = run_grader.Grader(
    usage="usage: anchor_scan.py <a run directory> [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
)


AGREEMENT_ANCHOR = re.compile(r'(?mi)^[ \t]*ANCHOR[ \t]*:[ \t]*"(.*)"[ \t]*$')
REFUSAL_MARK = re.compile(rf"(?mi)^[ \t]*NOT CODED:[ \t]*(?P<code>{CODE})\b[ \t]+(?P<descriptor>\S.*)$")
NOTE_REFUSAL = re.compile(rf"(?i)\bNOT CODED:[ \t]*(?P<code>{CODE})\b")
PROPOSED_INSTEAD = re.compile(r"(?mi)^[ \t]*proposed instead:[ \t]*(?P<value>[^\r\n]*)$")
SUBSTITUTE_CODE = re.compile(rf"\b{CODE}\b", re.IGNORECASE)
SUBSTITUTE_CONTINUATION = re.compile(r"(?m)^[ \t]+\S[^\r\n]*$")
REFUSAL_FIELD = re.compile(r"(?i)^[ \t]*(?:needs|proposed instead):")
ICD_TOKEN = re.compile(r"\b[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?\b")
RENDERED_PROCEDURE = re.compile(rf"(?mi)^[ \t]*(?P<system>CPT|HCPCS)[ \t]*:[ \t]*(?P<code>{CODE})\b")
RENDERED_EM = EM_LINE

@dataclass(frozen=True)
class AgreementSubject:
    system: str
    code: str
    descriptor: str
    role: str
    support: str
    subject_id: str = ""

    @property
    def key(self) -> str:
        return self.subject_id


@dataclass(frozen=True)
class AgreementPair:
    stem: str
    note: str
    worksheet: str
    subjects: tuple[AgreementSubject, ...]
    excluded_em: int
    unread_remainder: int = 0


def _markdown_files(directory: Path) -> dict[str, Path]:
    if not directory.is_dir():
        return {}
    return {
        path.stem: path
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and not run_grader.is_run_record(path)
    }


@cache
def _database_descriptor(system: str, code: str) -> str | None:
    if system.upper().startswith("ICD"):
        import icd10_lookup

        with closing(icd10_lookup.open_database()) as connection:
            match = icd10_lookup.describe(connection, code)
            return match.long if match else None
    import procedure_codes_lookup

    with closing(procedure_codes_lookup.open_database()) as connection:
        match = procedure_codes_lookup.describe(connection, code)
        return match.description if match else None


def _rendered_descriptors(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    payload = read_handwritten_record(path, "json").json
    rows = payload["codes"]
    if not isinstance(rows, list):
        raise ValueError("rendered descriptor codes must be a list")
    descriptors: dict[str, dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict) or any(
            not isinstance(row.get(field), str) or not row[field].strip()
            for field in ("code", "descriptor", "book", "edition", "printed_page")
        ):
            raise ValueError("each rendered descriptor needs code, descriptor, book, edition, printed_page")
        code = row["code"].strip().upper()
        if code in descriptors:
            raise ValueError(f"duplicate rendered descriptor for {code}")
        descriptors[code] = {
            field: row[field].strip()
            for field in ("descriptor", "book", "edition", "printed_page")
        }
    return descriptors


def _official_descriptor(
    system: str, code: str,
    rendered_descriptors: dict[str, dict[str, str]] | None = None,
) -> str | None:
    if system == "CPT":
        import procedure_codes_lookup

        with closing(procedure_codes_lookup.open_database()) as connection:
            match = procedure_codes_lookup.describe(connection, code)
            if match is None:
                return None
            if not procedure_codes_lookup.cpt_descriptors_verified(connection):
                page = (rendered_descriptors or {}).get(code)
                if page and (page["book"], page["edition"]) == (
                    match.source_title, match.source_edition
                ):
                    return page["descriptor"]
                return None
    return _database_descriptor(system, code)


def _cpt_page_missing(system: str, code: str, official: str | None) -> bool:
    if system != "CPT" or official is not None:
        return False
    import procedure_codes_lookup

    with closing(procedure_codes_lookup.open_database()) as connection:
        return (procedure_codes_lookup.describe(connection, code) is not None
                and not procedure_codes_lookup.cpt_descriptors_verified(connection))


def _route_tokens(value: str) -> list[str]:
    without_parentheticals = re.sub(r"\([^)]*\)", "", value)
    return [
        token
        for token in re.findall(r"[a-z0-9]+", without_parentheticals.lower())
        if token != "nec"
    ]


def _is_subsequence(needles: list[str], haystack: list[str]) -> bool:
    position = 0
    for token in haystack:
        if position < len(needles) and token == needles[position]:
            position += 1
    return position == len(needles)


class RouteStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNREAD = "unread"


@cache
def _index_route_catalog() -> dict[str, tuple[str, str | None, str | None, str | None]]:
    import icd10_lookup

    with closing(icd10_lookup.open_database()) as connection:
        rows = connection.execute(
            "SELECT path, code, see, see_also FROM index_entry ORDER BY path",
        ).fetchall()

    rendered: dict[str, tuple[str, str | None, str | None, str | None]] = {}
    for path, code, see, see_also in rows:
        destination = (
            f"code {icd10_lookup.dotted(code)}" if code else
            f"see {see}" if see else
            f"see also {see_also}" if see_also else
            "no direct destination"
        )
        rendered[f"{path} -> {destination}"] = (path, code, see, see_also)
    return rendered


@cache
def _stem_descriptors(stem: str) -> tuple[tuple[str, str], ...]:
    """Return the tabular choices beneath an index stem."""
    import icd10_lookup

    with closing(icd10_lookup.open_database()) as connection:
        rows = connection.execute(
            "SELECT code, long FROM code WHERE code LIKE ? ORDER BY code",
            (f"{stem}%",),
        ).fetchall()
    return tuple((code, descriptor) for code, descriptor in rows)


_REFERENCE_FILLER = {
    "a", "an", "and", "by", "for", "in", "index", "of", "or", "the", "to", "with",
}
_PLACEHOLDER_FILLER = _REFERENCE_FILLER | {
    "accidental", "adverse", "assault", "behavior", "benign", "ca", "cause",
    "chemicals", "contact", "drug", "drugs", "effect", "external", "injury",
    "intentional", "malignant", "nec", "neoplasm", "neoplastic", "poisoning", "primary", "secondary",
    "self", "specified", "table", "underdosing", "undetermined", "unintentional",
    "unspecified",
}
_DESCRIPTOR_FILLER = {
    "a", "an", "and", "body", "encounter", "for", "of", "the", "to", "with", "without",
}

DRUG_COLUMNS = (
    "Poisoning Accidental (unintentional)",
    "Poisoning Intentional self-harm",
    "Poisoning Assault",
    "Poisoning Undetermined",
    "Adverse effect",
    "Underdosing",
)
NEOPLASM_COLUMNS = (
    "Malignant Primary",
    "Malignant Secondary",
    "Ca in situ",
    "Benign",
    "Uncertain Behavior",
    "Unspecified Behavior",
)


DRUG_UNDERDOSING_PATTERN = r"\b(?:taking|took|take|using|used) less\b|\bstopp?ed\b.*\bon (?:his|her|their) own\b"
DRUG_PROPER_USE_PATTERN = r"\b(?:properly administered|as prescribed|correctly prescribed)\b"
DRUG_REACTION_PATTERN = r"\b(?:adverse effect|reaction|side effect)\b"
DRUG_SELF_HARM_PATTERN = r"\b(?:self[- ]harm|suicid(?:e|al))\b"
DRUG_INTENTIONAL_PATTERN = r"(?<!\bnon-)\bintentional\b"
DRUG_ASSAULT_PATTERN = r"\b(?:assault(?:ed)?|assailant)\b"
DRUG_NEGATION_PATTERN = r"\b(?:not|no|denies|denied|without|negative for|never)\b"
DRUG_HEDGE_PATTERN = r"\b(?:possible|possibly|suspected|perhaps|may have been)\b"
DRUG_UNDETERMINED_PATTERN = r"\b(?:intent cannot be determined|undetermined)\b"
DRUG_POISONING_PATTERN = (
    r"\bpoisoning\b"
)
DRUG_ACCIDENTAL_PATTERN = r"\b(?:accidental|unintentional|non-?intentional)\b"
DRUG_ADVERSE_PATTERN = r"\badverse effect\b"
DRUG_UNDERDOSING_NAME_PATTERN = r"\bunderdosing\b"
TOXIC_EFFECT_PREFIXES = tuple(f"T{number}" for number in range(51, 66))
MEDICINE_PREFIXES = tuple(f"T{number}" for number in range(36, 51))


class ColumnBasis(Enum):
    MECHANICAL = "mechanical"
    GROUND = "reader ground"
    MISSING = "missing ground"
    INVALID = "contrary evidence"


def _medicine_column(subject: AgreementSubject) -> str | None:
    code = subject.code.replace(".", "").upper()
    if (subject.system == "ICD-10" and code.startswith(MEDICINE_PREFIXES)
            and len(code) > 5 and code[5] in "123456"):
        return DRUG_COLUMNS[int(code[5]) - 1]
    return None


def _first_column_pointer(route: str) -> str:
    """Only a referral on the matched main entry can settle a column."""
    first = _index_route_catalog().get(route.split(" | ", 1)[0])
    if first is None or " > " in first[0] or first[0].lower() == "toxicity":
        return ""
    referral = (first[2] or first[3]).lower()
    if "table of drugs and chemicals" not in referral:
        return ""
    if re.search(r"\bpoisoning\b", referral):
        return "poisoning"
    if "with 6th character 5" in referral or "adverse effect" in referral:
        return "adverse effect"
    return ""


def _drug_column_basis(column: str, agreeing_words: str, subject_code: str = "",
                       column_ground: str = "none", route: str = "") -> ColumnBasis:
    words = agreeing_words.lower()
    toxic_effect = subject_code.replace(".", "").upper().startswith(TOXIC_EFFECT_PREFIXES)
    ground = "" if column_ground == "none" else column_ground.lower()
    # Intent belongs to the label; the ground supplies how the medicine was taken.
    intent_words = re.sub(DRUG_NEGATION_PATTERN + r"[^,;.]*", "", words)
    self_harm = bool(re.search(DRUG_SELF_HARM_PATTERN, intent_words))
    intentional = bool(re.search(DRUG_INTENTIONAL_PATTERN, intent_words))
    assault = bool(re.search(DRUG_ASSAULT_PATTERN, intent_words))
    undetermined = bool(re.search(DRUG_UNDETERMINED_PATTERN, intent_words) or (
        re.search(DRUG_HEDGE_PATTERN, words) and (self_harm or intentional or assault)
    ))
    underdosing = bool(re.search(DRUG_UNDERDOSING_PATTERN, words))
    proper = bool(re.search(DRUG_PROPER_USE_PATTERN, words))
    adverse = proper and bool(re.search(DRUG_REACTION_PATTERN, words))
    pointer = "" if toxic_effect else _first_column_pointer(route)
    expected = None
    if not toxic_effect:
        if column.startswith("Poisoning") and (
            proper or underdosing or re.search(DRUG_PROPER_USE_PATTERN, ground)
            or re.search(DRUG_UNDERDOSING_PATTERN, ground)
        ):
            return ColumnBasis.INVALID
        if underdosing or re.search(DRUG_UNDERDOSING_NAME_PATTERN, words):
            expected = "Underdosing"
        elif adverse or re.search(DRUG_ADVERSE_PATTERN, words) or pointer == "adverse effect":
            expected = "Adverse effect"
    poisoning = toxic_effect or bool(
        re.search(DRUG_POISONING_PATTERN, words) or pointer == "poisoning"
        or re.search(DRUG_ACCIDENTAL_PATTERN, intent_words)
        or self_harm or intentional or assault or undetermined
    )
    rests_on_ground = expected is None and not poisoning
    if rests_on_ground:
        if not ground:
            return ColumnBasis.MISSING
        if not column.startswith("Poisoning"):
            return ColumnBasis.GROUND
    if expected is None:
        if undetermined:
            expected = "Poisoning Undetermined"
        elif self_harm or (intentional and not assault):
            expected = "Poisoning Intentional self-harm"
        elif assault:
            expected = "Poisoning Assault"
        else:
            expected = "Poisoning Accidental (unintentional)"
    if column != expected:
        return ColumnBasis.INVALID
    return ColumnBasis.GROUND if rests_on_ground else ColumnBasis.MECHANICAL


def _drug_column_agrees(column: str, agreeing_words: str, subject_code: str = "",
                        column_ground: str = "none", route: str = "") -> bool:
    return _drug_column_basis(column, agreeing_words, subject_code, column_ground, route) in {
        ColumnBasis.MECHANICAL, ColumnBasis.GROUND,
    }


def _neoplasm_column_agrees(column: str, agreeing_words: str) -> bool:
    words = agreeing_words.lower()
    sign_only = bool(re.search(r"\b(?:mass|lump|nodule)\b", words))
    neoplasm_word = bool(re.search(r"\b(?:tumor|growth|neoplasm)\b", words))
    benign_morphology = bool(re.search(r"\b(?:fibroid|leiomyoma|lipoma)\b", words))
    hedged_malignancy = bool(
        re.search(r"\b(?:concerning for|possible|possibly|suspected)\b.*\b(?:malignan|cancer|carcinoma)", words)
    )
    if sign_only and not neoplasm_word and not benign_morphology and "benign" not in words:
        return False
    indeterminate_pathology = bool(
        re.search(r"\b(?:pathology|histology)\b", words)
        and re.search(r"\b(?:indeterminate|cannot determine|could not determine)\b", words)
    )
    expected = None
    if indeterminate_pathology:
        expected = "Uncertain Behavior"
    elif "in situ" in words:
        expected = "Ca in situ"
    elif not hedged_malignancy and re.search(r"\b(?:metastatic|secondary)\b", words):
        expected = "Malignant Secondary"
    elif not hedged_malignancy and re.search(
        r"\b(?:malignan\w*|cancer|carcinoma)\b", words
    ):
        expected = "Malignant Primary"
    elif "benign" in words or benign_morphology:
        expected = "Benign"
    elif neoplasm_word:
        expected = "Unspecified Behavior"
    return column == expected


def _contains_tokens(needles: list[str], haystack: list[str]) -> bool:
    wanted = Counter(needles)
    available = Counter(haystack)
    return all(available[token] >= count for token, count in wanted.items())


def _segment_alternatives(segment: str) -> list[list[str]]:
    parenthetical = [
        value
        for value in re.findall(r"\(([^()]*)\)", segment)
        if value.strip().lower() not in {"s", "es", "ies"}
    ]
    base = re.sub(r"\([^()]*\)", "", segment)
    phrases = re.split(r"\s*,\s*|\s+or\s+", base) + parenthetical
    return [
        tokens
        for phrase in phrases
        if (
            tokens := [
                token
                for token in _route_tokens(phrase)
                if token not in _PLACEHOLDER_FILLER
            ]
        )
    ]


def _reference_matches(
    referral: str,
    following_path: str,
    subject_code: str,
    note_evidence: str = "",
) -> bool:
    lower = referral.lower()
    following = _route_tokens(following_path)
    normalized = subject_code.replace(".", "").upper()
    final_step = following_path.rsplit(" > ", 1)[-1]
    validated_family_pointer = False
    if "table of drugs and chemicals" in lower:
        if not normalized.startswith(tuple(f"T{number}" for number in range(36, 66))):
            return False
        if final_step not in DRUG_COLUMNS:
            return False
        validated_family_pointer = True
        lower = lower.replace("table of drugs and chemicals", "")
    if "table of neoplasm" in lower or lower.strip() == "neoplasm":
        if final_step not in NEOPLASM_COLUMNS:
            return False
        validated_family_pointer = True
        lower = re.sub(r"\b(?:table of )?neoplasms?\b", "", lower)
    if "external cause" in lower and "index" in lower:
        if normalized[:1] not in {"V", "W", "X", "Y"}:
            return False
        validated_family_pointer = True
        lower = re.sub(r"\bindex to external causes? of injury\b", "", lower)

    # A placeholder delegates its omitted detail to the next path. The words
    # before it still have to identify the destination family.
    placeholder = bool(re.search(r"\bby (?:site|type|substance|animal|drug)\b", lower))
    lower = re.sub(r"\bby (?:site|type|substance|animal|drug)(?:\b.*)?$", "", lower)
    # Character and range instructions constrain the subject code rather than
    # spelling a destination path.
    instruction = False
    code_range = re.search(r"\b(?:categories?|codes?)\s+([a-z]\d{2})\s*[-–]\s*([a-z]\d{2})", lower)
    if code_range:
        instruction = True
        first, last = (value.upper() for value in code_range.groups())
        if not first <= normalized[:3] <= last:
            return False
    character = re.search(
        r"\bwith\s+(\d+)(?:st|nd|rd|th)\s+character\s+([a-z0-9])", lower
    )
    if character:
        instruction = True
        position = int(character.group(1)) - 1
        if position >= len(normalized) or normalized[position] != character.group(2).upper():
            return False
    lower = re.sub(r"\b(?:categories?|codes?)\s+[a-z0-9.-]+(?:\s*[-–]\s*[a-z0-9.-]+)?", "", lower)
    lower = re.sub(r"\bwith\s+\d+(?:st|nd|rd|th)\s+character\s+[a-z0-9]", "", lower)
    needed = [token for token in _route_tokens(lower) if token not in _REFERENCE_FILLER]
    available = [token for token in following if token not in _REFERENCE_FILLER]
    if not (
        (validated_family_pointer or instruction or bool(needed))
        and _contains_tokens(needed, available)
    ):
        return False
    if placeholder:
        evidence = set(_route_tokens(note_evidence))
        supplied_segments = [
            _segment_alternatives(segment)
            for segment in following_path.split(" > ")
        ]
        supplied_segments = [segment for segment in supplied_segments if segment]
        return bool(supplied_segments) and all(
            any(all(token in evidence for token in alternative) for alternative in segment)
            for segment in supplied_segments
        )
    return True


def _route_starts_in_words(
    alternatives: list[str], path: str, agreeing_words: str, subject_code: str
) -> bool:
    word_tokens = _route_tokens(agreeing_words)
    if any(_is_subsequence(_route_tokens(term), word_tokens) for term in alternatives):
        return True
    # The external-cause index classifies a cut made by an unnamed edged object
    # under Contact > sharp object NEC. The note need not repeat the abstract
    # word "contact" when it states the cut and the edged mechanism directly.
    normalized = subject_code.replace(".", "").upper()
    return bool(
        normalized[:1] in {"V", "W", "X", "Y"}
        and "sharp object" in path.lower()
        and re.search(r"\b(?:cut|edge|edged|laceration|sharp)\b", agreeing_words, re.IGNORECASE)
    )


def _stem_details_agree(
    subject: AgreementSubject,
    stem: str,
    agreeing_words: str,
    encounter_evidence: str,
) -> bool:
    normalized = subject.code.replace(".", "").upper()
    if normalized == stem:
        return True
    rows = _stem_descriptors(stem)
    selected = next((descriptor for code, descriptor in rows if code == normalized), None)
    if selected is None:
        return False
    token_sets = [
        {token for token in _route_tokens(descriptor) if token not in _DESCRIPTOR_FILLER}
        for _code, descriptor in rows
    ]
    common = set.intersection(*token_sets) if token_sets else set()
    selected_tokens = {
        token for token in _route_tokens(selected) if token not in _DESCRIPTOR_FILLER
    }
    distinguishing = selected_tokens - common
    evidence = set(_route_tokens(f"{agreeing_words} {encounter_evidence}"))
    return distinguishing <= evidence


def _route_status(
    subject: AgreementSubject,
    route: str,
    agreeing_words: str,
    encounter_evidence: str = "",
    column_ground: str = "none",
) -> RouteStatus:
    if route == "descriptor words":
        return RouteStatus.VALID
    if subject.system != "ICD-10":
        return RouteStatus.INVALID

    normalized = subject.code.replace(".", "").upper()
    rendered = _index_route_catalog()
    steps = route.split(" | ")
    if not steps or any(step not in rendered for step in steps):
        return RouteStatus.INVALID
    resolved = [rendered[step] for step in steps]
    first_main_term = resolved[0][0].split(">", 1)[0]
    alternatives = [part.strip() for part in first_main_term.split(",")]
    if not _route_starts_in_words(alternatives, resolved[0][0], agreeing_words, normalized):
        return RouteStatus.INVALID

    unmatched_reference = False
    for previous, following in zip(resolved, resolved[1:]):
        referral = previous[2] or previous[3]
        if not referral:
            return RouteStatus.INVALID
        if not _reference_matches(
            referral,
            following[0],
            normalized,
            f"{agreeing_words} {encounter_evidence}",
        ):
            unmatched_reference = True

    final_code = resolved[-1][1]
    if not final_code:
        return RouteStatus.INVALID
    stem = final_code.rstrip("-")
    if not normalized.startswith(stem):
        return RouteStatus.INVALID
    final_step = resolved[-1][0].rsplit(" > ", 1)[-1]
    if final_step in DRUG_COLUMNS and not _drug_column_agrees(
        final_step, subject.support or agreeing_words, normalized, column_ground, route
    ):
        return RouteStatus.INVALID
    if final_step in NEOPLASM_COLUMNS and not _neoplasm_column_agrees(final_step, agreeing_words):
        return RouteStatus.INVALID
    if not _stem_details_agree(subject, stem, agreeing_words, encounter_evidence):
        return RouteStatus.INVALID
    if unmatched_reference:
        return RouteStatus.UNREAD
    return RouteStatus.VALID


def _unmatched_cross_references(
    subject: AgreementSubject,
    route: str,
    agreeing_words: str,
    encounter_evidence: str,
) -> tuple[str, ...]:
    rendered = _index_route_catalog()
    steps = route.split(" | ")
    if not steps or any(step not in rendered for step in steps):
        return ()
    resolved = [rendered[step] for step in steps]
    return tuple(
        referral
        for previous, following in zip(resolved, resolved[1:])
        if (referral := previous[2] or previous[3])
        and not _reference_matches(
            referral,
            following[0],
            subject.code,
            f"{agreeing_words} {encounter_evidence}",
        )
    )


def _valid_route(
    subject: AgreementSubject,
    route: str,
    agreeing_words: str,
    encounter_evidence: str = "",
) -> bool:
    return _route_status(
        subject, route, agreeing_words, encounter_evidence
    ) is RouteStatus.VALID


def _requires_encounter_evidence(subject: AgreementSubject) -> bool:
    descriptor = subject.descriptor.lower()
    return subject.role == "procedure" or bool(
        re.search(r"\b(?:encounter for|initial encounter|subsequent encounter)\b", descriptor)
    )


def _authored_anchor(
    text: str, start: int, end: int, header: str, official: str | None,
) -> str:
    """Read only an anchor that is the first field after a code header."""
    field = FIELD.search(text, start, end)
    if field is None or field.group("field").upper() != "ANCHOR":
        return ""
    between = text[start:field.start()].splitlines()
    marker = bool(re.search(r"\bNOT FOR ENTRY$", header))
    descriptor = re.sub(r"\s+NOT FOR ENTRY$", "", header).strip()
    for line in between[1:]:
        if not line.strip() or line[0] not in " \t" or ":" in line:
            return ""
        continuation = line.strip()
        if continuation == "NOT FOR ENTRY" and not marker:
            marker = True
            continue
        if marker or official is None or not official.startswith(descriptor) or descriptor == official:
            return ""
        descriptor = f"{descriptor} {continuation}"
        if not official.startswith(descriptor):
            return ""
    anchor = AGREEMENT_ANCHOR.match(text, field.start(), end)
    return anchor.group(1) if anchor else ""


def _agreement_subjects(
    text: str, rendered_descriptors: dict[str, dict[str, str]] | None = None
) -> tuple[tuple[AgreementSubject, ...], int, int]:
    entries = list(ENTRY.finditer(text))
    differential_match = DIFFERENTIAL_HEADING.search(text)
    refusal_match = REFUSAL_HEADING.search(text)
    step_four_match = STEP_FOUR_START.search(text)
    differential = differential_match.start() if differential_match else -1
    refusal = refusal_match.start() if refusal_match else -1
    step_four = step_four_match.start() if step_four_match else -1
    subjects: list[AgreementSubject] = []
    unread = max(0, len(list(ENTRY_CANDIDATE.finditer(text))) - len(entries)) + heading_counts(text).unread

    for index, match in enumerate(entries):
        start = match.start()
        if (refusal >= 0 and start >= refusal) or (step_four >= 0 and start >= step_four):
            continue
        system = match.group("system").upper().replace("ICD10", "ICD-10")
        code = match.group("code").upper()
        descriptor = match.group("descriptor").strip()
        is_differential = differential >= 0 and start >= differential
        role = "differential" if is_differential else (
            "procedure" if system in {"CPT", "HCPCS"} else "entry"
        )
        end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
        if refusal >= 0:
            end = min(end, refusal) if end > start else end
        official = _official_descriptor(system, code, rendered_descriptors)
        support = _authored_anchor(text, match.end(), end, descriptor, official)
        if system in {"CPT", "HCPCS"} and not support:
            # Procedure-code prose can begin with ``CPT 12345`` while explicitly
            # declining to propose it. Detail fields distinguish an actual
            # unanchored proposal from such a prose mention.
            if FIELD.search(text, match.end(), end) is None and re.search(
                r"\bnot proposed\b", descriptor, re.IGNORECASE
            ):
                continue
        if not support:
            unread += 1
        if official is not None:
            subjects.append(AgreementSubject(system, code, official, role, support))
        else:
            unread += 1
            if _cpt_page_missing(system, code, official):
                subjects.append(AgreementSubject(system, code, "", role, support))

    if refusal >= 0:
        refusals = list(REFUSAL_MARK.finditer(text, refusal))
        for index, match in enumerate(refusals):
            code = match.group("code").upper()
            system = "CPT" if code.isdigit() else "ICD-10"
            official = _official_descriptor(system, code, rendered_descriptors)
            end = refusals[index + 1].start() if index + 1 < len(refusals) else len(text)
            support = _authored_anchor(
                text, match.end(), end, match.group("descriptor"), official
            )
            if not support:
                unread += 1
            if official is not None:
                subjects.append(
                    AgreementSubject(
                        system, code, official, "refused", support
                    )
                )
            else:
                unread += 1
                if _cpt_page_missing(system, code, official):
                    subjects.append(AgreementSubject(system, code, "", "refused", support))
    occurrences: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    identified: list[AgreementSubject] = []
    for subject in subjects:
        identity = (subject.system, subject.code, subject.role)
        occurrences[identity] += 1
        identified.append(
            AgreementSubject(
                subject.system,
                subject.code,
                subject.descriptor,
                subject.role,
                subject.support,
                f"{subject.system}:{subject.code}:{subject.role}:{occurrences[identity]}",
            )
        )
    return tuple(identified), len(RENDERED_EM.findall(text)), unread


def _pair_agreement_sources(
    worksheets: Path, notes: Path, rendered_descriptors: dict[str, dict[str, str]],
    requested: set[str] | None = None,
) -> tuple[list[AgreementPair], int, int]:
    worksheet_files = _markdown_files(worksheets)
    note_files = _markdown_files(notes)
    stems = sorted(set(worksheet_files) & set(note_files))
    full_pair_count = len(stems)
    unread = len(set(worksheet_files) ^ set(note_files)) if requested is None else len(requested - set(stems))
    if requested is not None:
        stems = [stem for stem in stems if stem in requested]
    pairs: list[AgreementPair] = []
    for stem in stems:
        worksheet = worksheet_files[stem].read_text(encoding="utf-8", errors="replace")
        note = note_files[stem].read_text(encoding="utf-8", errors="replace")
        subjects, worksheet_em, subject_unread = _agreement_subjects(
            worksheet, rendered_descriptors
        )
        pairs.append(
            AgreementPair(
                stem,
                note,
                worksheet,
                subjects,
                worksheet_em + len(RENDERED_EM.findall(note)),
                subject_unread,
            )
        )
        unread += subject_unread
    return pairs, unread, full_pair_count


def _code_labels(note: str, subject: AgreementSubject) -> set[str]:
    """Read the document unit pinning this subject, preserving its wording."""
    if subject.role == "refused":
        pattern = re.compile(
            rf"\bNOT CODED:[ \t]*({re.escape(subject.code)}[ \t]+"
            rf"{re.escape(subject.descriptor)})(?=,|;|\.?$)", re.MULTILINE
        )
        return {match.group(1) for match in pattern.finditer(note)}
    headings = {"entry": ("final diagnosis", "preexisting diagnoses"),
                "differential": ("differential",)}
    labels: set[str] = set()
    section = ""
    for line in note.splitlines():
        clean = line.lstrip(" #*\t")
        if re.match(r"(?i)^(?:final diagnosis|preexisting diagnoses|differential)\b", clean):
            section = clean.split(":", 1)[0].lower()
            section = next((h for h in headings[subject.role] if section.startswith(h)), "")
            line = line.split(":", 1)[1].lstrip(" *") if ":" in line else ""
        elif line.lstrip().startswith("#") or re.match(
                r"(?i)^(?:[A-Z]:|Age-appropriate screening|Coding worksheet|Proposed coding worksheet|Tier block)", clean):
            section = ""
        if not section:
            continue
        if subject.role == "differential" and not re.match(r"^\s*\d+\.\s", line):
            continue
        # A rationale cannot supply a label, including another code it mentions.
        line = line.split(":", 1)[0]
        previous_end = 0
        for token in ICD_TOKEN.finditer(line):
            if not _database_descriptor("ICD-10", token.group().upper()):
                continue
            if token.group().upper() == subject.code:
                before = line[previous_end:token.start()]
                pin = re.search(r"[ \t]+-[ \t]+[*_]*$", before)
                if pin:
                    label = before[:pin.start()].strip(" \t;*")
                    label = re.sub(r"^\d+\.[ \t]+|^[-+][ \t]+", "", label)
                    labels.add(label)
            previous_end = token.end()
    return labels


def _anchor_findings(pairs: list[AgreementPair]) -> list[str]:
    findings = []
    for pair in pairs:
        for subject in pair.subjects:
            if subject.support and subject.support not in pair.note:
                findings.append(f"{pair.stem}: {subject.key} anchor is not verbatim note text")
            if (subject.support and subject.system == "ICD-10" and subject.role in {"entry", "differential", "refused"}
                    and subject.support not in _code_labels(pair.note, subject)):
                findings.append(f"{pair.stem}: {subject.key} author anchor differs from whole code label")
    return findings


HOME_MEDICATION = re.compile(
    r"(?i)^(?:home\s+(?:meds|medications)|historical\s+medications|medications)\b"
)
CONTINUE_MEDICATION = re.compile(r"(?i)^continue\s+(?:home\s+)?")


def _filled_home_medication_evidence(evidence: str, items: list[str]) -> bool:
    """Read containment; concrete management outside the item stays a reading."""
    # Entry.text unwraps continuation lines; do the same only after the caller
    # has required the original evidence verbatim in the note.
    evidence = " ".join(evidence.split())
    items = [" ".join(item.split()) for item in items]
    if any(evidence in item for item in items):
        return True
    continuation = CONTINUE_MEDICATION.match(evidence)
    if continuation is None:
        return False
    continued = evidence[continuation.end():].rstrip(" .;")
    if continued.lower() in {"meds", "medications", "home meds", "home medications"}:
        return bool(items)
    return bool(continued) and any(continued in item for item in items)


AGREEMENT_RETRY_INSTRUCTIONS = (
    "Redo only the listed subjects under the brief's instructions and leave every other record unchanged."
)


NO_WAIT_PENDING_FORM = "none (pending: <test> could only add <what>)"
NO_WAIT_PENDING_PATTERN = re.compile(
    re.escape(NO_WAIT_PENDING_FORM)
    .replace("<test>", r"[^()\s](?:[^()\r\n]*[^()\s])?")
    .replace("<what>", r"[^()\s](?:[^()\r\n]*[^()\s])?")
)


AGREEMENT_CODE_FIELDS = frozenset({
    "subject_id", "system", "code", "role", "agreeing_words", "route",
    "encounter_evidence", "open_status_evidence", "column_ground", "threshold", "waits_on_result",
})


AGREEMENT_READER_INSTRUCTIONS = (
    "A blind reader's note entry has a remarks list of nonempty strings, empty when there are none. "
    "The Writer self-record has no remarks field. "
    "Put a problem outside the agreement question there and nowhere else; it never changes an answer. "
    "A remark about a code names that code. Retain every earlier remark when replacing a reader record. "
    "Writer self-records exist privately; do not read them or request their text as a retry hint. "
    "For every code, record agreeing_words, route, encounter_evidence, "
    "open_status_evidence, column_ground, threshold, and waits_on_result; use 'none' when absent. "
    "Writers and blind readers quote open_status_evidence verbatim from the note. "
    "Copy subject_id, system, code, and role exactly. Every evidence value is a nonempty "
    "string. Route is the literal 'descriptor words' or exact index output; join a "
    "referral chain with ' | ' and end at the subject code. The route's first index entry's "
    "main term, the part before its first '>', or one of its comma-separated spellings, "
    "must appear in agreeing_words: every word in the same order, not necessarily side by side. "
    "Words in parentheses and the word NEC are ignored on both sides. For a code beginning "
    "V, W, X or Y, a route whose first entry runs through 'sharp object' also starts in "
    "words saying cut, edge, edged, laceration or sharp. The start is the only step the "
    "scanner checks against the note. Every later step on the path, such as a site, still "
    "needs note words that reach it, and that judgment is the reader's. "
    "Agreement requires note words that state the descriptor or reach it through an "
    "official four-source index path; topical relation is insufficient. An index code "
    "may be the subject code's stem, but every tabular-added character still needs note "
    "evidence for laterality, site detail, placeholders, and encounter character. Ignore "
    "word order within a cross-reference; fill by-site, by-type, by-substance, and by-drug "
    "placeholders from the next path; and satisfy character or code-range instructions "
    "with the subject code. Keep a real route with a still-unmatched cross-reference so "
    "the scanner can place it in the named unread remainder. For Neoplasm Table routes, "
    "a mass, lump, or nodule takes its sign code; tumor, growth, or neoplasm without "
    "behavior takes unspecified behavior; uncertain behavior needs indeterminate "
    "pathology; malignant, secondary, in-situ, and benign columns need stated behavior "
    "or a morphology routed there; and a named benign morphology does not wait for "
    "tissue. For drug-table routes, the following exact patterns search agreeing_words "
    "case-insensitively: "
    f"underdosing `{DRUG_UNDERDOSING_PATTERN}`; proper use `{DRUG_PROPER_USE_PATTERN}` "
    f"together with reaction `{DRUG_REACTION_PATTERN}`; medicine poisoning `{DRUG_POISONING_PATTERN}`; "
    f"accidental `{DRUG_ACCIDENTAL_PATTERN}`; adverse-effect name `{DRUG_ADVERSE_PATTERN}`; "
    f"underdosing name `{DRUG_UNDERDOSING_NAME_PATTERN}`; "
    f"self-harm `{DRUG_SELF_HARM_PATTERN}`; intentional `{DRUG_INTENTIONAL_PATTERN}`; "
    f"assault `{DRUG_ASSAULT_PATTERN}`; hedge `{DRUG_HEDGE_PATTERN}`; "
    f"undetermined intent `{DRUG_UNDETERMINED_PATTERN}`. "
    f"For subject-code prefixes {', '.join(TOXIC_EFFECT_PREFIXES)}, the substance route "
    "establishes exposure and no poisoning word is required; only intent chooses among "
    "the four Poisoning columns, with no adverse-effect or underdosing branch. "
    "Whether the exposure caused harm remains the reader's judgment. For medicine codes, "
    "the label's column name or affirmative intent settles its family; underdosing takes "
    "precedence, then proper use together with reaction takes Adverse effect. "
    "A Table of Drugs and Chemicals poisoning or adverse-effect pointer on the first main "
    "entry also settles the family: Overdose, overdosage (drug), Medicine poisoning, "
    "Wrong drug (by accident) (given in error), or Adverse effect. A pointer on a subentry "
    "does not settle it. Toxicity and a flat denial of intent settle no medicine column. "
    "Otherwise quote column_ground verbatim from anywhere in the note showing how the "
    "medicine was taken; no ground is a finding. Check the medication list and history "
    "for proper use before quoting misuse. Proper-use and took-less patterns search only "
    "the label and ground and refuse poisoning there. Whether the ground concerns this "
    "drug remains the reader's judgment. Every column relying on a ground is counted and "
    "the check generates a reader remark naming its code and quoted ground for the clinical "
    "go-ahead's READER REMARKS block. "
    "For poisoning, undetermined intent or a hedge together with self-harm, intentional or "
    "assault takes Undetermined first; then self-harm or intentional without assault takes "
    "Intentional self-harm; then assault takes Assault; otherwise intent defaults to "
    "Accidental (unintentional), so hedged self-harm or assault agrees only with undetermined. "
    f"Before testing intent, negation `{DRUG_NEGATION_PATTERN}` removes following self-harm, "
    "intentional and assault signals up to the next comma, semicolon or period, and nothing "
    "before the cue. Negation is applied before hedging; a hedge needs a surviving intent "
    "signal. Once poisoning is established, a flat denial of every intent signal agrees "
    "only with Accidental (unintentional). A differential "
    "code is read against the diagnosis considered by its entry. A history condition takes a present-tense code only when it coexists at this encounter "
    "and required or affected this visit's care, treatment, or management. Personal-history "
    "and status codes require an effect on current care. Filled reasoning earns a code only "
    "by changing something concrete in this visit: a drug chosen or avoided, a dose adjusted, "
    "or a test or monitoring ordered because of the condition. A filled home medication, "
    "or a continue of one, never earns its condition a code. "
    "An encounter or procedure descriptor needs evidence that its purpose "
    "or act belongs to this encounter, not a later recommendation. A bare value reaches an "
    "abnormality descriptor only through a threshold stated by the note or a committed "
    "source. For every entry or differential code, name any result the descriptor still "
    "waits on. A code waits on a pending or absent result only when that result would "
    "establish something the code's own descriptor asserts. A pending film or culture "
    "does not make a diagnosis the encounter already establishes clinically wait. "
    "Where the result could only replace the code with a more specific one, the code "
    "does not wait. A descriptor stating 'without complications' or 'uncomplicated' "
    "records the documented state; an open or pending workup refuses only the "
    "complication's code. "
    f"For waits_on_result, use the literal 'none' or '{NO_WAIT_PENDING_FORM}', with "
    "nonempty test and added-code descriptions; the reason is read for its shape only. "
    "CPT and HCPCS have no index route and use descriptor words only."
    " Quote agreeing_words from the Final diagnosis or Preexisting diagnoses line pinning an "
    "entry ICD-10 code, the numbered Differential entry pinning a differential code, or the "
    "code-and-descriptor half of the welded NOT CODED: clause naming a refused code, never "
    "its reason. For entry and differential codes, stay within that code's complete label: "
    "from the beginning of the line (after a heading or list marker), or after the preceding "
    "code token that resolves in the committed ICD-10-CM code set, including a category heading, up to the hyphen pinning this code. Code-shaped tokens outside that set, such as B12 and A1C, are label text. Retain hedges and joining words and "
    "leave out the rationale following the colon. For CPT or HCPCS, quote the line documenting "
    "the act done in this encounter. "
    "Record agreeing_words as 'none' when the code's label does not state or reach its "
    "descriptor, even when other note text agrees. A refused code agrees with the diagnosis "
    "its clause considers. Hedge words document the diagnosis in general. An entry descriptor "
    "that still waits on an absent or pending result fails even when the diagnosis is hedged. "
    "A code may rest "
    "on the tier block's filled values. A disclosed estimated measurement is not a pending "
    "result for waits_on_result."
)


def _brief_payload(
    pairs: list[AgreementPair], unread: int, full_pair_count: int,
    requested: list[str] | None, finding_count: int = 0,
) -> dict:
    payload = {
        "mode": "descriptor agreement blind brief",
        "instructions": AGREEMENT_READER_INSTRUCTIONS,
        "pairs": [
            {
                "stem": pair.stem,
                "note": pair.note,
                "codes": [
                    {
                        "system": subject.system,
                        "code": subject.code,
                        "descriptor": subject.descriptor,
                        "role": subject.role,
                        "subject_id": subject.subject_id,
                    }
                    for subject in pair.subjects
                ],
            }
            for pair in pairs
        ],
        "excluded_em": sum(pair.excluded_em for pair in pairs),
        "unread remainder": unread,
        "agreement findings": finding_count,
    }
    if requested is not None:
        payload["requested_stems"] = requested
        payload["full_pair_count"] = full_pair_count
    return payload


def _section_codes(note: str, heading: str) -> tuple[set[str], list[str]]:
    lines = note.splitlines()
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if line.lstrip(" #*\t").lower().startswith(heading)
        ),
        None,
    )
    if start is None:
        return set(), []
    first = lines[start]
    selected: list[str] = [first.split(":", 1)[1].strip(" *") if ":" in first else ""]
    closing_labels = (
        "preexisting diagnoses",
        "final diagnosis",
        "age-appropriate screening",
        "p:",
        "coding worksheet",
        "proposed coding worksheet",
        "medatrax entry",
        "tier block",
        "drift matrix",
        "drift verdicts",
    )
    for line in lines[start + 1 :]:
        label = line.lstrip(" #*\t").lower()
        if any(label.startswith(candidate) for candidate in closing_labels):
            break
        selected.append(line)
    section = "\n".join(selected)
    refused = {match.group("code").upper() for match in NOTE_REFUSAL.finditer(section)}
    codes: set[str] = set()
    excluded: list[str] = []
    for match in ICD_TOKEN.finditer(section):
        token = match.group(0).upper()
        if token in refused:
            continue
        if _database_descriptor("ICD-10", token) is None:
            excluded.append(token)
        else:
            codes.add(token)
    return codes, excluded


def _binding_findings(pair: AgreementPair) -> tuple[list[str], list[str]]:
    proposed_icd = {s.code for s in pair.subjects if s.role == "entry" and s.system == "ICD-10"}
    proposed_codes = {s.code for s in pair.subjects if s.role in {"entry", "procedure"}}
    differential_icd = {s.code for s in pair.subjects if s.role == "differential"}
    refused_icd = {s.code for s in pair.subjects if s.role == "refused"}
    procedure = {
        (s.system, s.code) for s in pair.subjects if s.role == "procedure"
    }

    preexisting, preexisting_excluded = _section_codes(pair.note, "preexisting diagnoses")
    final, final_excluded = _section_codes(pair.note, "final diagnosis")
    note_diagnoses = preexisting | final
    note_differential, differential_excluded = _section_codes(pair.note, "differential")
    note_refused = {match.group("code").upper() for match in NOTE_REFUSAL.finditer(pair.note)}
    note_procedure = {
        (match.group("system").upper(), match.group("code").upper())
        for match in RENDERED_PROCEDURE.finditer(pair.note)
    }
    comparisons = (
        ("for-entry diagnosis", note_diagnoses, proposed_icd),
        ("differential", note_differential, differential_icd),
        ("refusal", note_refused, refused_icd),
        ("procedure", note_procedure, procedure),
    )
    findings = [
        f"{pair.stem}: {label} bind differs: "
        f"note only {sorted(note_side - worksheet_side)}, "
        f"worksheet only {sorted(worksheet_side - note_side)}"
        for label, note_side, worksheet_side in comparisons
        if note_side != worksheet_side
    ]
    substitutes: set[str] = set()
    for field in PROPOSED_INSTEAD.finditer(pair.worksheet):
        value = field["value"]
        for line in SUBSTITUTE_CONTINUATION.finditer(pair.worksheet, field.end()):
            if (not detail_belongs_to_entry(pair.worksheet, field, line)
                    or FIELD.match(line.group()) or REFUSAL_FIELD.match(line.group())
                    or OTHER_HEADING.match(line.group())):
                break
            value += "\n" + line.group()
        codes = {match.group().upper() for match in SUBSTITUTE_CODE.finditer(value)}
        if not codes:
            findings.append(f"{pair.stem}: proposed-instead field names no code")
        substitutes.update(codes)
    if not substitutes <= proposed_codes:
        findings.append(
            f"{pair.stem}: proposed-instead code is absent from for-entry proposals: "
            f"worksheet only {sorted(substitutes - proposed_codes)}"
        )
    excluded = [
        f"{pair.stem}: {token}"
        for token in preexisting_excluded + final_excluded + differential_excluded
    ]
    return findings, excluded


def _agreement_report(
    pairs: list[AgreementPair],
    findings: list[str],
    unread: int,
    unread_routes: list[str] | None = None,
    excluded_code_tokens: list[str] | None = None,
    show: bool = False,
) -> str:
    waits = sum(" entry waits on " in finding for finding in findings)
    missing = sum("has no agreeing words" in finding for finding in findings)
    not_note = sum("agreeing words are not note text" in finding for finding in findings)
    wrong_place = sum("agreeing words are from the wrong place" in finding for finding in findings)
    labels = sum("author anchor differs from whole code label" in finding for finding in findings)
    anchors = sum("anchor is not verbatim note text" in finding for finding in findings)
    route = sum("has no descriptor or index route" in finding for finding in findings)
    encounter = sum("has no encounter evidence" in finding for finding in findings)
    open_not_note = sum("open-status evidence is not note text" in finding for finding in findings)
    filled_medication = sum(
        "open-status evidence rests only on a filled home medication" in finding
        for finding in findings
    )
    binds = sum(
        "bind differs" in finding or "proposed-instead" in finding for finding in findings
    )
    lines = [
            "descriptor agreement read",
            "",
            f"  paired notes and worksheets          {len(pairs)}",
            f"  codes read                           {sum(len(pair.subjects) for pair in pairs)}",
            f"  E/M lines excluded                  {sum(pair.excluded_em for pair in pairs)}",
            f"  agreement findings                 {len(findings)}",
            f"    codes with no agreeing words      {missing}",
            f"    agreeing words absent from note   {not_note}",
            f"    agreeing words from wrong place  {wrong_place}",
            f"    non-verbatim anchors              {anchors}",
            f"    author code-label findings         {labels}",
            f"    open-status evidence absent from note  {open_not_note}",
            f"    open-status evidence from filled home medication  {filled_medication}",
            f"    codes with no route               {route}",
            f"    codes with no encounter evidence  {encounter}",
            f"    descriptors waiting on results    {waits}",
            f"    note/worksheet bind findings      {binds}",
            run_grader.format_unread_remainder(unread),
    ]
    missing_cpt = sum(subject.system == "CPT" and not subject.descriptor
                      for pair in pairs for subject in pair.subjects)
    lines.extend([
        f"  CPT subjects missing rendered pages  {missing_cpt}",
        f"  other unread evidence                 {unread - missing_cpt}",
    ])
    if show:
        lines.extend(f"    finding: {finding}" for finding in findings)
        if findings:
            lines.append(AGREEMENT_RETRY_INSTRUCTIONS)
        lines.extend(f"    unread cross-reference: {route}" for route in unread_routes or ())
    lines.extend([
        "",
        "  informational",
        f"    code-shaped tokens excluded from the bind  {len(excluded_code_tokens or ())}",
    ])
    if show:
        lines.extend(
            f"    excluded from bind, not a finding: {token}"
            for token in excluded_code_tokens or ()
        )
    return "\n".join(lines)


def _run_agreement(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="anchor_scan.py")
    parser.add_argument("worksheets", type=Path)
    parser.add_argument("--notes", type=Path, required=True)
    parser.add_argument("--rendered-descriptors", type=Path)
    parser.add_argument("--show", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agreement-brief", action="store_true")
    mode.add_argument("--agreement-read", type=Path, nargs="+")
    parser.add_argument("--stem", action="append", default=None)
    parser.add_argument("--submission", help="owning note's approval key for dated checks")
    parser.add_argument("--self-record", type=Path, nargs="+",
                        help="writer records for report-only blind-read comparison")
    parser.add_argument("--output", type=Path, help="write the agreement brief as BOM-free UTF-8")
    args = parser.parse_args(argv)
    if args.self_record is not None and not args.agreement_read:
        parser.error("--self-record requires --agreement-read; self-records never enter a brief")
    if args.output is not None and not args.agreement_brief:
        parser.error("--output requires --agreement-brief")
    run = args.worksheets.parent if args.worksheets.name == "worksheets" else args.worksheets
    with completion_checks.grading(run, args.submission):
        return _agreement_command(args)


def _agreement_command(args) -> int:
    descriptor_damage = ""
    try:
        rendered_descriptors = _rendered_descriptors(args.rendered_descriptors)
    except DamagedRecord as failure:
        _, descriptor_damage = damaged_record_result(failure, check="rendered descriptor record")
        rendered_descriptors = {}
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"descriptor agreement: unread rendered-page record ({error})")
        return 2
    pairs, unread, full_pair_count = _pair_agreement_sources(
        args.worksheets, args.notes, rendered_descriptors,
        set(args.stem) if args.stem else None,
    )
    if not pairs:
        unread += 1

    if args.agreement_brief:
        anchor_findings = _anchor_findings(pairs)
        brief = json.dumps(
            {**_brief_payload(pairs, unread, full_pair_count, args.stem, len(anchor_findings)),
             "run_records": run_grader.run_records_report(args.worksheets, args.notes)},
            indent=2, ensure_ascii=True,
        )
        if args.output is None:
            print(brief)
        else:
            try:
                target = ensure_outside_checkout(
                    args.output, permitted=[scratch_root()],
                    detail="Agreement briefs contain complete notes and belong under the owning checkout's scratch/ or outside every checkout.",
                )
                target.write_text(brief + "\n", encoding="utf-8", newline="\n")
            except (InsideCheckout, OSError) as error:
                print(f"descriptor agreement brief: {error}", file=sys.stderr)
                return 2
        if args.show:
            for finding in anchor_findings:
                print(f"finding: {finding}", file=sys.stderr)
        if descriptor_damage:
            print(descriptor_damage, file=sys.stderr)
            return 1
        return 2 if unread else (1 if anchor_findings else 0)

    assert args.agreement_read is not None
    try:
        run = args.worksheets.parent if args.worksheets.name == "worksheets" else args.worksheets
        with completion_checks.grading(run, args.submission):
            result = _grade_agreement(pairs, unread, args.agreement_read,
                                      set(args.stem) if args.stem else None)
            dated_report = completion_checks.report()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"descriptor agreement read: unread record ({error})")
        return 2
    print(_agreement_report(pairs, result.findings, result.unread,
                            result.unread_routes, result.excluded_code_tokens, args.show))
    print(f"  medicine columns resting on reader ground  {len(result.column_remarks)}")
    print(f"  unexpected agreement keys                 {result.unexpected_keys}")
    if dated_report:
        print(dated_report)
    for report in (*result.damage_reports, *((descriptor_damage,) if descriptor_damage else ())):
        print(report)
    for index, path in enumerate(result.unread_records, 1):
        print(f"  unread agreement record: {run_grader.artifact_label(path, index, len(result.unread_records))}")
    if args.show:
        print(reader_remarks.report((*result.remarks, *result.column_remarks)))
    print(run_grader.run_records_report(args.worksheets, args.notes))
    if result.out_of_scope_rows:
        print(f"  agreement rows outside requested stems: {result.out_of_scope_rows}")
        print("  A scoped read takes that stem's own agreement-self/<stem>.json.")
    metric: int | str = "not measured"
    self_damaged = False
    if args.self_record is not None:
        try:
            self_result = _grade_agreement(pairs, unread, args.self_record, writer_record=True)
            self_damaged = bool(self_result.damage_reports)
            for report in self_result.damage_reports:
                print(report)
            metric = ("unread self-record coverage" if self_result.unread
                      else len(self_result.passed & result.failed))
        except (OSError, ValueError, KeyError, TypeError):
            metric = "unread self-record"
    print(f"  self-pass / blind-fail subjects (report only)  {metric}")
    if result.damage_reports or descriptor_damage or self_damaged:
        return 1
    if result.unread:
        return 2
    return 1 if result.findings else 0


@dataclass
class AgreementRead:
    findings: list[str]
    unread: int
    unread_routes: list[str]
    excluded_code_tokens: list[str]
    passed: set[tuple[str, str]]
    failed: set[tuple[str, str]]
    out_of_scope_rows: int = 0
    column_remarks: list[reader_remarks.Remark] = field(default_factory=list)
    remarks: tuple[reader_remarks.Remark, ...] = ()
    unexpected_keys: int = 0
    unread_records: tuple[Path, ...] = ()
    damage_reports: tuple[str, ...] = ()


def _grade_agreement(pairs: list[AgreementPair], unread: int,
                     paths: list[Path], requested: set[str] | None = None,
                     *, writer_record: bool = False) -> AgreementRead:
    record_pairs: dict[str, dict] = {}
    out_of_scope = 0
    remarks: list[reader_remarks.Remark] = []
    unexpected_keys = 0
    unread_records: list[Path] = []
    damage_reports = []
    damaged_stems: set[str] = set()
    unknown_damaged_population = False
    for path in paths:
        try:
            payload = read_handwritten_record(path, "json").json
        except DamagedRecord as failure:
            finding, report = damaged_record_result(failure, check="descriptor agreement record")
            if finding:
                damage_reports.append(report)
                if path.parent.name == "agreement-self":
                    # The scoped self-read route declares its stem in the
                    # canonical filename, before any record content is read.
                    damaged_stems.add(path.stem)
                else:
                    # A generic file may carry several pairs. Its unavailable
                    # contents cannot establish which missing joins it owned.
                    unknown_damaged_population = True
            continue
        before_unread = unread
        before_keys = unexpected_keys
        writer = writer_record or path.parent.name == "agreement-self"
        check_keys = completion_checks.active("anchor_scan:unexpected-reader-keys")
        check_remarks = completion_checks.active("anchor_scan:reader-remarks")
        if check_keys:
            unexpected_keys += len(set(payload) - {"pairs"})
        supplied_pairs = payload["pairs"]
        if not isinstance(supplied_pairs, list):
            raise TypeError("pairs is not a list")
        for row in supplied_pairs:
            if not isinstance(row, dict) or not isinstance(row.get("stem"), str):
                unread += 1
                continue
            stem = row["stem"]
            if check_keys:
                unexpected_keys += len(set(row) - ({"stem", "codes"} if writer else {"stem", "codes", "remarks"}))
                for code_row in row.get("codes", []) if isinstance(row.get("codes"), list) else ():
                    if isinstance(code_row, dict):
                        unexpected_keys += len(set(code_row) - AGREEMENT_CODE_FIELDS)
            if not writer and check_remarks:
                read_remarks, malformed = reader_remarks.record_remarks(row.get("remarks", []), f"AGREEMENT: {stem}")
                unread += malformed
                if requested is None or stem in requested:
                    remarks.extend(read_remarks)
            if requested is not None and stem not in requested:
                out_of_scope += 1
            if stem in record_pairs or not isinstance(row.get("codes"), list):
                unread += 1
                continue
            record_pairs[stem] = row
        unread += unexpected_keys - before_keys
        if unread != before_unread:
            unread_records.append(path)
    expected_stems = {pair.stem for pair in pairs}
    unread += len(set(record_pairs) - expected_stems)

    findings: list[str] = list(damage_reports)
    unread_routes: list[str] = []
    excluded_code_tokens: list[str] = []
    passed: set[tuple[str, str]] = set()
    failed: set[tuple[str, str]] = set()
    column_remarks: list[reader_remarks.Remark] = []
    for pair in pairs:
        findings.extend(_anchor_findings([pair]))
        filled_home_medications = [
            entry.text for entry in read_block(pair.note).get(ASSERTED, [])
            if HOME_MEDICATION.match(entry.subject)
        ]
        record_pair = record_pairs.get(pair.stem)
        if record_pair is None:
            if not unknown_damaged_population and pair.stem not in damaged_stems:
                unread += len(pair.subjects) or 1
            continue
        record_rows = record_pair.get("codes", [])
        valid_rows = [row for row in record_rows if isinstance(row, dict)]
        unread += len(record_rows) - len(valid_rows)
        records = {row.get("subject_id"): row for row in valid_rows}
        expected = {subject.key: subject for subject in pair.subjects}
        unread += len(set(expected) - set(records)) + len(set(records) - set(expected))
        unread += len(valid_rows) - len(records)
        for key in set(expected) & set(records):
            subject = expected[key]
            record = records[key]
            before = (len(findings), unread)
            required = (
                "agreeing_words",
                "route",
                "encounter_evidence",
                "open_status_evidence",
                "threshold",
                "waits_on_result",
            )
            if any(
                field not in record
                or not isinstance(record[field], str)
                or not record[field]
                for field in required
            ):
                unread += 1
                continue
            if (
                record.get("system"),
                record.get("code"),
                record.get("role"),
            ) != (subject.system, subject.code, subject.role):
                unread += 1
                continue
            open_status = record["open_status_evidence"]
            if open_status != "none":
                if open_status not in pair.note:
                    findings.append(
                        f"{pair.stem}: {subject.key} open-status evidence is not note text"
                    )
                elif _filled_home_medication_evidence(open_status, filled_home_medications):
                    findings.append(
                        f"{pair.stem}: {subject.key} open-status evidence rests only on a filled home medication"
                    )
            if subject.system == "CPT" and not subject.descriptor:
                # Keep the subject and its bind, but never grade against an
                # unverified database descriptor. The page is counted above.
                continue
            words = record["agreeing_words"]
            route = record["route"]
            ground = record.get("column_ground", "none")
            if not isinstance(ground, str) or not ground:
                unread += 1
                continue
            if ground != "none" and ground not in pair.note:
                findings.append(f"{pair.stem}: {subject.key} column ground is not note text")
            column = _medicine_column(subject)
            basis = None
            if column is not None:
                basis = _drug_column_basis(column, subject.support, subject.code, ground, route)
                if basis is ColumnBasis.MISSING:
                    findings.append(f"{pair.stem}: {subject.key} has no column ground")
                elif basis is ColumnBasis.INVALID:
                    findings.append(f"{pair.stem}: {subject.key} column contradicts its label or ground")
            if not isinstance(words, str) or not words or words == "none":
                if subject.role == "procedure":
                    unread += 1
                else:
                    findings.append(f"{pair.stem}: {subject.key} has no agreeing words")
            elif words not in pair.note:
                findings.append(f"{pair.stem}: {subject.key} agreeing words are not note text")
            elif words not in subject.support:
                findings.append(f"{pair.stem}: {subject.key} agreeing words are from the wrong place")
            route_status = _route_status(
                subject, route, words, record["encounter_evidence"], ground
            )
            if route == "none" or route_status is RouteStatus.INVALID:
                if subject.role != "procedure":
                    findings.append(f"{pair.stem}: {subject.key} has no descriptor or index route")
            elif route_status is RouteStatus.UNREAD:
                unread += 1
                unread_routes.extend(
                    f"{pair.stem}: {subject.key}: {referral}"
                    for referral in _unmatched_cross_references(
                        subject,
                        route,
                        words,
                        record["encounter_evidence"],
                    )
                )
            if basis is ColumnBasis.GROUND and route_status is RouteStatus.VALID and ground in pair.note:
                column_remarks.append(reader_remarks.Remark(
                    f"AGREEMENT: {pair.stem}",
                    f'{subject.code}: {column} rests on reader column ground: "{ground}"',
                ))
            if (
                _requires_encounter_evidence(subject)
                and record["encounter_evidence"] == "none"
            ):
                findings.append(f"{pair.stem}: {subject.key} has no encounter evidence")
            waits = record["waits_on_result"]
            if (
                subject.role in {"entry", "differential"}
                and isinstance(waits, str)
                and waits != "none"
                and NO_WAIT_PENDING_PATTERN.fullmatch(waits) is None
            ):
                findings.append(f"{pair.stem}: {subject.key} entry waits on {waits}")
            if len(findings) > before[0] or (subject.support and subject.support not in pair.note):
                failed.add((pair.stem, key))
            elif unread == before[1]:
                passed.add((pair.stem, key))
        binding_findings, pair_excluded_tokens = _binding_findings(pair)
        findings.extend(binding_findings)
        excluded_code_tokens.extend(pair_excluded_tokens)

    return AgreementRead(findings, unread, unread_routes, excluded_code_tokens, passed, failed,
                         out_of_scope, column_remarks, tuple(dict.fromkeys(remarks)),
                         unexpected_keys, tuple(unread_records), tuple(damage_reports))


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    if any(arg in {"--agreement-brief", "--agreement-read", "--output"}
           or arg.startswith("--output=") for arg in argv):
        use_utf8()
        require_python_floor()
        return _run_agreement(argv)
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
