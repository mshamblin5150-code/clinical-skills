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

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from contextlib import closing
from dataclasses import dataclass
from enum import Enum
from functools import cache
from pathlib import Path

import run_grader
from console_codec import require_python_floor, use_utf8
from worksheet_grammar import (
    BLOCK_HEADING, CODE, DIFFERENTIAL_HEADING, ENTRY, ENTRY_CANDIDATE, FIELD,
    REFUSAL_HEADING, STEP_FOUR_START, entry_is_for_entry, heading_counts, paired_entry,
)

SOURCE = re.compile(r"(?mi)^[ \t]*SOURCE[ \t]*:[ \t]*(.*?)[ \t]*$")
CONFIDENCE = re.compile(r"(?mi)^[ \t]*CONFIDENCE[ \t]*:[ \t]*(.*?)[ \t]*$")
FILLED = re.compile(r"(?i)^filled\b")
CDC_COMPUTED = re.compile(
    r"(?i)^verified against ICD-10-CM FY2026 and "
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
        "real poisoning descriptor agreement",
        "No committed real note carries a T36-T65 poisoning code; drug-column behavior has synthetic controls only.",
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
        unread_remainder=sum(sheet.unread_remainder for sheet in sheets),
        excluded_em=sum(sheet.excluded_em for sheet in sheets),
        off_template_headings=sum(sheet.off_template_headings for sheet in sheets),
        heading_candidates=sum(sheet.heading_candidates for sheet in sheets),
        generic_differential_headings=sum(sheet.generic_differential_headings for sheet in sheets),
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
        f"  E/M lines excluded                  {scan.excluded_em}",
        f"  orphaned detail lines               {scan.orphaned_details}",
        f"  keyword heading candidates         {scan.heading_candidates}",
        f"  generic Differential headings      {scan.generic_differential_headings}",
        f"  off-template block headings        {scan.off_template_headings}",
        run_grader.format_unread_remainder(scan.unread_remainder),
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
        coverage_failed=not scan.subjects or bool(scan.unread_remainder),
        diagnostics=tuple(diagnostics),
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
PROPOSED_INSTEAD = re.compile(rf"(?mi)^[ \t]*proposed instead:[ \t]*(?P<code>{CODE})\b", re.IGNORECASE)
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
        if path.name.lower() != "readme.md"
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
    payload = json.loads(path.read_text(encoding="utf-8"))
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


def _drug_column_agrees(column: str, agreeing_words: str) -> bool:
    words = agreeing_words.lower()
    underdosing = bool(
        re.search(r"\b(?:taking|took|take|using|used) less\b|\bstopp?ed\b.*\bon (?:his|her|their) own\b", words)
    )
    adverse = bool(
        re.search(r"\b(?:properly administered|as prescribed|correctly prescribed)\b", words)
        and re.search(r"\b(?:adverse effect|reaction|side effect)\b", words)
    )
    self_harm = bool(re.search(r"\b(?:self[- ]harm|suicid(?:e|al))\b", words))
    intentional = "intentional" in words
    assault = bool(re.search(r"\b(?:assault(?:ed)?|assailant)\b", words))
    hedged_intent = bool(
        re.search(r"\b(?:possible|possibly|suspected|perhaps|may have been)\b", words)
        and (self_harm or intentional or assault)
    )
    undetermined = bool(
        re.search(r"\b(?:intent cannot be determined|undetermined intent)\b", words)
        or hedged_intent
    )
    poisoning = bool(
        re.search(
            r"\b(?:overdose|poisoning|ingestion|got into|wrong (?:drug|substance|route)|"
            r"nonprescribed|with alcohol)\b",
            words,
        )
    )

    expected = None
    if underdosing:
        expected = "Underdosing"
    elif adverse:
        expected = "Adverse effect"
    elif poisoning and undetermined:
        expected = "Poisoning Undetermined"
    elif poisoning and (self_harm or (intentional and not assault)):
        expected = "Poisoning Intentional self-harm"
    elif poisoning and assault:
        expected = "Poisoning Assault"
    elif poisoning:
        expected = "Poisoning Accidental (unintentional)"
    return column == expected


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
    placeholder = bool(re.search(r"\bby (?:site|type|substance|animal)\b", lower))
    lower = re.sub(r"\bby (?:site|type|substance|animal)(?:\b.*)?$", "", lower)
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
    if final_step in DRUG_COLUMNS and not _drug_column_agrees(final_step, agreeing_words):
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


def _anchor_findings(pairs: list[AgreementPair]) -> list[str]:
    return [
        f"{pair.stem}: {subject.key} anchor is not verbatim note text"
        for pair in pairs
        for subject in pair.subjects
        if subject.support and subject.support not in pair.note
    ]


def _brief_payload(
    pairs: list[AgreementPair], unread: int, full_pair_count: int,
    requested: list[str] | None, finding_count: int = 0,
) -> dict:
    payload = {
        "mode": "descriptor agreement blind brief",
        "instructions": (
            "For every code, record agreeing_words, route, encounter_evidence, "
            "open_status_evidence, threshold, and waits_on_result; use 'none' when absent. "
            "Copy subject_id, system, code, and role exactly. Every evidence value is a nonempty "
            "string. Route is the literal 'descriptor words' or exact index output; join a "
            "referral chain with ' | ', beginning at a term in agreeing_words and ending at the "
            "subject code. "
            "Agreement requires note words that state the descriptor or reach it through an "
            "official four-source index path; topical relation is insufficient. An index code "
            "may be the subject code's stem, but every tabular-added character still needs note "
            "evidence for laterality, site detail, placeholders, and encounter character. Ignore "
            "word order within a cross-reference; fill by-site, by-type, and by-substance "
            "placeholders from the next path; and satisfy character or code-range instructions "
            "with the subject code. Keep a real route with a still-unmatched cross-reference so "
            "the scanner can place it in the named unread remainder. For Neoplasm Table routes, "
            "a mass, lump, or nodule takes its sign code; tumor, growth, or neoplasm without "
            "behavior takes unspecified behavior; uncertain behavior needs indeterminate "
            "pathology; malignant, secondary, in-situ, and benign columns need stated behavior "
            "or a morphology routed there; and a named benign morphology does not wait for "
            "tissue. For drug-table routes, distinguish poisoning, proper-use adverse effect, "
            "and underdosing; unstated poisoning intent defaults to accidental, while hedged "
            "self-harm or assault agrees only with undetermined. A differential "
            "code is read against the diagnosis considered by its entry. A present descriptor "
            "resting on history needs note evidence that the finding remains unresolved and is "
            "addressed today. An encounter or procedure descriptor needs evidence that its purpose "
            "or act belongs to this encounter, not a later recommendation. A bare value reaches an "
            "abnormality descriptor only through a threshold stated by the note or a committed "
            "source. For every entry or differential code, name any result the descriptor still "
            "waits on. CPT and HCPCS have no index route and use descriptor words only."
        ),
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


def _section_codes(note: str, heading: str) -> set[str]:
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
        return set()
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
    return {match.group(0).upper() for match in ICD_TOKEN.finditer(section)} - refused


def _binding_findings(pair: AgreementPair) -> list[str]:
    proposed_icd = {s.code for s in pair.subjects if s.role == "entry" and s.system == "ICD-10"}
    differential_icd = {s.code for s in pair.subjects if s.role == "differential"}
    refused_icd = {s.code for s in pair.subjects if s.role == "refused"}
    procedure = {
        (s.system, s.code) for s in pair.subjects if s.role == "procedure"
    }

    note_diagnoses = _section_codes(pair.note, "preexisting diagnoses") | _section_codes(
        pair.note, "final diagnosis"
    )
    note_differential = _section_codes(pair.note, "differential")
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
    substitutes = {
        match.group("code").upper() for match in PROPOSED_INSTEAD.finditer(pair.worksheet)
    }
    if not substitutes <= proposed_icd:
        findings.append(
            f"{pair.stem}: proposed-instead code is absent from for-entry proposals: "
            f"worksheet only {sorted(substitutes - proposed_icd)}"
        )
    return findings


def _agreement_report(
    pairs: list[AgreementPair],
    findings: list[str],
    unread: int,
    unread_routes: list[str] | None = None,
    show: bool = False,
) -> str:
    waits = sum(" entry waits on " in finding for finding in findings)
    missing = sum("has no agreeing words" in finding for finding in findings)
    not_note = sum("agreeing words are not note text" in finding for finding in findings)
    wrong_place = sum("agreeing words are from the wrong place" in finding for finding in findings)
    anchors = sum("anchor is not verbatim note text" in finding for finding in findings)
    route = sum("has no descriptor or index route" in finding for finding in findings)
    encounter = sum("has no encounter evidence" in finding for finding in findings)
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
            f"    codes with no route               {route}",
            f"    codes with no encounter evidence  {encounter}",
            f"    descriptors waiting on results    {waits}",
            f"    note/worksheet bind findings      {binds}",
            run_grader.format_unread_remainder(unread),
    ]
    if show:
        lines.extend(f"    finding: {finding}" for finding in findings)
        lines.extend(f"    unread cross-reference: {route}" for route in unread_routes or ())
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
    args = parser.parse_args(argv)
    if args.stem and not args.agreement_brief:
        parser.error("--stem requires --agreement-brief")
    try:
        rendered_descriptors = _rendered_descriptors(args.rendered_descriptors)
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
        print(json.dumps(
            _brief_payload(pairs, unread, full_pair_count, args.stem, len(anchor_findings)),
            indent=2, ensure_ascii=True,
        ))
        if args.show:
            for finding in anchor_findings:
                print(f"finding: {finding}", file=sys.stderr)
        return 2 if unread else (1 if anchor_findings else 0)

    assert args.agreement_read is not None
    try:
        record_pairs: dict[str, dict] = {}
        for path in args.agreement_read:
            payload = json.loads(path.read_text(encoding="utf-8"))
            supplied_pairs = payload["pairs"]
            if not isinstance(supplied_pairs, list):
                raise TypeError("pairs is not a list")
            for row in supplied_pairs:
                if not isinstance(row, dict) or "stem" not in row:
                    unread += 1
                    continue
                stem = row["stem"]
                if stem in record_pairs or not isinstance(row.get("codes"), list):
                    unread += 1
                    continue
                record_pairs[stem] = row
        expected_stems = {pair.stem for pair in pairs}
        unread += len(set(record_pairs) - expected_stems)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"descriptor agreement read: unread record ({error})")
        return 2

    findings: list[str] = []
    unread_routes: list[str] = []
    for pair in pairs:
        findings.extend(_anchor_findings([pair]))
        record_pair = record_pairs.get(pair.stem)
        if record_pair is None:
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
            words = record["agreeing_words"]
            route = record["route"]
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
                subject, route, words, record["encounter_evidence"]
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
            if (
                _requires_encounter_evidence(subject)
                and record["encounter_evidence"] == "none"
            ):
                findings.append(f"{pair.stem}: {subject.key} has no encounter evidence")
            waits = record["waits_on_result"]
            if subject.role in {"entry", "differential"} and isinstance(waits, str) and waits != "none":
                findings.append(f"{pair.stem}: {subject.key} entry waits on {waits}")
        findings.extend(_binding_findings(pair))

    print(_agreement_report(pairs, findings, unread, unread_routes, args.show))
    if unread:
        return 2
    return 1 if findings else 0


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    if any(arg in {"--agreement-brief", "--agreement-read"} for arg in argv):
        use_utf8()
        require_python_floor()
        return _run_agreement(argv)
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
