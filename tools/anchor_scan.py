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

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import run_grader
from worksheet_grammar import CODE, ENTRY, ENTRY_CANDIDATE, entry_is_for_entry, paired_entry

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
        "ADR 0230 leaves this declared because no admissible candidate population spans marks, listings, and pediatric bands.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "E/M descriptor agreement",
        "E/M lines are counted and excluded because their descriptors cannot settle place of service, patient status, and decision-making level.",
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
    unread_remainder: int = 0
    excluded_em: int = 0


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
        ),
        excluded_em=len(EM_LINE.findall(text)),
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
DIFFERENTIAL_HEADING = re.compile(
    r"(?mi)^(?:---[ \t]*|#{1,6}[ \t]+)DIFFERENTIAL,?[ \t]+DOCUMENTS MDM,?[ \t]+NOT FOR ENTRY(?:[ \t]*---)?[ \t]*$"
)
REFUSAL_HEADING = re.compile(
    r"(?mi)^(?:---[ \t]*|#{1,6}[ \t]+)NOT CODED,?[ \t]+NOTHING ESTABLISHED IT(?:[ \t]*---)?[ \t]*$"
)


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


def _official_descriptor(system: str, code: str) -> str | None:
    if system.upper().startswith("ICD"):
        import icd10_lookup

        connection = icd10_lookup.open_database()
        try:
            match = icd10_lookup.describe(connection, code)
            return match.long if match else None
        finally:
            connection.close()
    import procedure_codes_lookup

    connection = procedure_codes_lookup.open_database()
    try:
        match = procedure_codes_lookup.describe(connection, code)
        return match.description if match else None
    finally:
        connection.close()


def _valid_route(subject: AgreementSubject, route: str) -> bool:
    if route == "descriptor words":
        return True
    if subject.system != "ICD-10":
        return False
    import icd10_lookup

    normalized = subject.code.replace(".", "").upper()
    connection = icd10_lookup.open_database()
    try:
        paths = connection.execute(
            "SELECT path FROM index_entry WHERE code = ? ORDER BY path",
            (normalized,),
        ).fetchall()
    finally:
        connection.close()
    expected = {
        f"{path} -> code {icd10_lookup.dotted(normalized)}" for (path,) in paths
    }
    return route in expected


def _preceding_support(text: str, position: int) -> str:
    before = text[:position].splitlines()
    return next((line.strip() for line in reversed(before) if line.strip() and not line.startswith("---")), "")


def _agreement_subjects(text: str) -> tuple[tuple[AgreementSubject, ...], int, int]:
    entries = list(ENTRY.finditer(text))
    differential_match = DIFFERENTIAL_HEADING.search(text)
    refusal_match = REFUSAL_HEADING.search(text)
    differential = differential_match.start() if differential_match else -1
    refusal = refusal_match.start() if refusal_match else -1
    subjects: list[AgreementSubject] = []
    unread = max(0, len(list(ENTRY_CANDIDATE.finditer(text))) - len(entries))

    for index, match in enumerate(entries):
        start = match.start()
        if refusal >= 0 and start >= refusal:
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
        anchor = AGREEMENT_ANCHOR.search(text, match.end(), end)
        if system in {"CPT", "HCPCS"} and not anchor:
            # Procedure-code prose can begin with ``CPT 12345`` while explicitly
            # declining to propose it. Only a worksheet entry with its required
            # quotation belongs to the agreement population.
            continue
        support = (
            "\n".join((_preceding_support(text, start), descriptor))
            if is_differential
            else (anchor.group(1) if anchor else "")
        )
        official = _official_descriptor(system, code)
        if official is not None:
            subjects.append(AgreementSubject(system, code, official, role, support))
        else:
            unread += 1

    if refusal >= 0:
        for match in REFUSAL_MARK.finditer(text, refusal):
            code = match.group("code").upper()
            official = _official_descriptor("ICD-10", code)
            if official is not None:
                subjects.append(
                    AgreementSubject(
                        "ICD-10", code, official, "refused", _preceding_support(text, match.start())
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


def _pair_agreement_sources(worksheets: Path, notes: Path) -> tuple[list[AgreementPair], int]:
    worksheet_files = _markdown_files(worksheets)
    note_files = _markdown_files(notes)
    stems = sorted(set(worksheet_files) & set(note_files))
    unread = len(set(worksheet_files) ^ set(note_files))
    pairs: list[AgreementPair] = []
    for stem in stems:
        worksheet = worksheet_files[stem].read_text(encoding="utf-8", errors="replace")
        note = note_files[stem].read_text(encoding="utf-8", errors="replace")
        subjects, worksheet_em, subject_unread = _agreement_subjects(worksheet)
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
    return pairs, unread


def _brief_payload(pairs: list[AgreementPair], unread: int) -> dict:
    return {
        "mode": "descriptor agreement blind brief",
        "instructions": (
            "For every code, record agreeing_words, route, encounter_evidence, "
            "open_status_evidence, threshold, and waits_on_result; use 'none' when absent. "
            "Agreement requires note words that state the descriptor or reach it through an "
            "official alphabetic-index path; topical relation is insufficient. A differential "
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
    }


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
        f"{pair.stem}: {label} bind differs"
        for label, note_side, worksheet_side in comparisons
        if note_side != worksheet_side
    ]
    substitutes = {
        match.group("code").upper() for match in PROPOSED_INSTEAD.finditer(pair.worksheet)
    }
    if not substitutes <= proposed_icd:
        findings.append(f"{pair.stem}: proposed-instead code is absent from for-entry proposals")
    return findings


def _agreement_report(pairs: list[AgreementPair], findings: list[str], unread: int) -> str:
    waits = sum(" entry waits on " in finding for finding in findings)
    missing = sum("has no agreeing words" in finding for finding in findings)
    verbatim = sum("agreeing words are not verbatim" in finding for finding in findings)
    route = sum("has no descriptor or index route" in finding for finding in findings)
    binds = sum(
        "bind differs" in finding or "proposed-instead" in finding for finding in findings
    )
    return "\n".join(
        (
            "descriptor agreement read",
            "",
            f"  paired notes and worksheets          {len(pairs)}",
            f"  codes read                           {sum(len(pair.subjects) for pair in pairs)}",
            f"  E/M lines excluded                  {sum(pair.excluded_em for pair in pairs)}",
            f"  agreement findings                 {len(findings)}",
            f"    codes with no agreeing words      {missing}",
            f"    non-verbatim agreeing words       {verbatim}",
            f"    codes with no route               {route}",
            f"    descriptors waiting on results    {waits}",
            f"    note/worksheet bind findings      {binds}",
            run_grader.format_unread_remainder(unread),
        )
    )


def _run_agreement(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="anchor_scan.py")
    parser.add_argument("worksheets", type=Path)
    parser.add_argument("--notes", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agreement-brief", action="store_true")
    mode.add_argument("--agreement-read", type=Path)
    args = parser.parse_args(argv)
    pairs, unread = _pair_agreement_sources(args.worksheets, args.notes)
    if not pairs:
        unread += 1

    if args.agreement_brief:
        print(json.dumps(_brief_payload(pairs, unread), indent=2, ensure_ascii=True))
        return 2 if unread else 0

    assert args.agreement_read is not None
    try:
        payload = json.loads(args.agreement_read.read_text(encoding="utf-8"))
        supplied_pairs = payload["pairs"]
        record_pairs: dict[str, dict] = {}
        for row in supplied_pairs:
            stem = row["stem"]
            if "codes" in row:
                record_pairs[stem] = row
            else:
                record_pairs.setdefault(stem, {"stem": stem, "codes": []})["codes"].append(row)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"descriptor agreement read: unread record ({error})")
        return 2

    findings: list[str] = []
    for pair in pairs:
        record_pair = record_pairs.get(pair.stem)
        if record_pair is None:
            unread += len(pair.subjects) or 1
            continue
        record_rows = record_pair.get("codes", [])
        records = {row.get("subject_id"): row for row in record_rows}
        expected = {subject.key: subject for subject in pair.subjects}
        unread += len(set(expected) - set(records)) + len(set(records) - set(expected))
        unread += len(record_rows) - len(records)
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
                    findings.append(f"{pair.stem}: {subject.code} has no agreeing words")
            elif words not in pair.note or words not in subject.support:
                findings.append(f"{pair.stem}: {subject.code} agreeing words are not verbatim")
            if route == "none" or not _valid_route(subject, route):
                if subject.role != "procedure":
                    findings.append(f"{pair.stem}: {subject.code} has no descriptor or index route")
            waits = record["waits_on_result"]
            if subject.role in {"entry", "differential"} and isinstance(waits, str) and waits != "none":
                findings.append(f"{pair.stem}: {subject.code} entry waits on {waits}")
        findings.extend(_binding_findings(pair))

    print(_agreement_report(pairs, findings, unread))
    if findings:
        return 1
    return 2 if unread else 0


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    if any(arg in {"--agreement-brief", "--agreement-read"} for arg in argv):
        return _run_agreement(argv)
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
