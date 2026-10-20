"""Parse and grade ADR 0219 heading-read records.

The caller owns sentence identification and pairing. This module grades the
recorded shape, its draft and project-context fingerprints, and each pair
against current claim headings. ``heading_read.DECLARED_LIMITS`` owns the
pairing boundary; the project-context row's ceiling belongs to
``project_context.DECLARED_LIMITS`` and is not copied here.
"""

from __future__ import annotations

import completion_checks
import re
import zipfile
import zlib
import lzma
from xml.etree.ElementTree import ParseError
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePath
from typing import NamedTuple

import reader_remarks
import file_digest
import research_ledger
import run_grader
from discussion_artifact import NUMBER
from discussion_artifact import record_unavailable
from run_grader import EvidenceDisposition
from run_record_reader import UnreadableRecord, mark_not_graded, DamagedRecord, damaged_record_result


class DeclaredLimit(NamedTuple):
    key: str
    limit: str
    evidence: EvidenceDisposition


DECLARED_LIMITS = (
    DeclaredLimit("own-figure-classification-unverified", "A listed figure cannot establish that its sentence is the clinician's own or that an item figure agrees with the opened item.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("qualifier-count-correctness-unverified", "A complete qualifier count cannot establish that the reader judged the sentence's qualifiers correctly.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("item-comparison-unverified", "An ITEM line names an opened item but cannot establish that the reader compared its claims correctly.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit(
        "pairing-correctness-unverified",
        "The record cannot prove that a reader paired each factual sentence correctly or judged that it claims no more than its heading.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "refutation-substance-unverified",
        "A current TESTED-HEADING cannot prove that the refuter actually tested the heading.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "reader-independence-unverified",
        "ROUTE cannot prove that a separate context performed the heading read.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "identical-byte-reversion-unseen",
        "A draft that changes and returns to identical bytes cannot be distinguished from an unchanged draft.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "peer-critique-certifier-pending",
        "peer_critique_scan does not disbelieve a mismatched claim record until issue 1056 lands.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "ratified-record-markers-unchanged",
        "This change adds no marker to ratified records and does not establish whether those records may be edited to carry one.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "heading-candidate-recognition-floor",
        "The candidate matcher recognizes only level-two HEADING-READ headings; an alternate spelling or heading level remains invisible.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit("item-quote-support-unverified", "A real unique quote does not establish that it supports the sentence's description.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("item-absence-search-unverified", "The absent - whole item searched sentinel cannot establish that a whole-item search took place or that the absence is true.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("service-item-quotes-ungraded", "Service ITEM lines are counted, not graded; service text is never retained for this check.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("item-text-recognition-floor", "Text files are UTF-8 source bytes including markup; Word quotes use docx_read's body paragraphs and table cells, excluding headers and other unread parts. Matching folds case and whitespace only.", EvidenceDisposition.DECLARED_READING),
    DeclaredLimit("item-quote-raw-digest-required", "An appended memory index can preserve the existing context binding while its changed raw digest leaves an ITEM quote unread until the source and heading read are refreshed.", EvidenceDisposition.BEHAVIOR),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


HEADER = re.compile(r"(?mi)^[ \t]*##[ \t]+HEADING-READ[ \t]*:[ \t]*(.*?)[ \t]*$")
HEADING_CANDIDATE = re.compile(r"(?mi)^[ \t]*##[ \t]+HEADING-READ\b.*$")
OTHER_HEADER = re.compile(r"^[ \t]*#{1,6}[ \t]+")
FIELD = re.compile(
    r"(?i)^[ \t]*(DRAFT|ROUTE|SENTENCES|PAIR|ITEM|OWN|CONTEXT-DIGEST|CONTEXT-VERDICT|VERDICT|FINDINGS|REMARK)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
SENTENCES = re.compile(
    r"(?i)^(?P<factual>[0-9]+)[ \t]+factual,[ \t]*(?P<own>[0-9]+)[ \t]+clinician's own(?:,[ \t]*(?P<item>[0-9]+)[ \t]+item)?$",
    re.ASCII,
)
PAIR = re.compile(r"^(?P<location>.+?)[ \t]+->[ \t]+(?P<prefix>[0-9a-fA-F]{8})(?:[ \t]+\|[ \t]+qualifiers (?P<read>[0-9]+) of (?P<total>[0-9]+))?$", re.ASCII)
FIGURES = rf"{NUMBER.pattern}(?:[ \t]*,[ \t]+{NUMBER.pattern})*"
OWN = re.compile(rf"^(?P<location>.+?)[ \t]+->[ \t]+(?P<figures>{FIGURES})$", re.IGNORECASE)
ITEM = re.compile(rf'^(?P<location>.+?)[ \t]+->[ \t]+(?P<item>.+?)(?:[ \t]+\|[ \t]+rests on (?P<quote>".*"|absent - whole item searched))?(?:[ \t]+\|[ \t]+figures (?P<figures>{FIGURES}))?$', re.IGNORECASE)
ROUTES = frozenset(("separate context",))

MISSING_RECORD = "missing-heading-read"
DUPLICATE_RECORD = "duplicate-heading-read"
UNKNOWN_ROUTE = "unknown-heading-read-route"
SENTENCE_COUNT_MISMATCH = "heading-read-sentence-count"
UNKNOWN_HEADING = "heading-read-unknown-heading"
DROPPED_HEADING = "heading-read-dropped-heading"
DRAFT_MISMATCH = "heading-read-draft-mismatch"
DEFECT_VERDICT = "heading-read-defect"
VERDICT_SHAPE = "heading-read-verdict-shape"
REPORTED_FINDING = "heading-read-finding"
CONTEXT_DIGEST_MISMATCH = "heading-read-context-digest"
CONTEXT_VERDICT_SHAPE = "heading-read-context-verdict-shape"
CONTEXT_DEFECT_VERDICT = "heading-read-context-defect"
QUALIFIER_COUNT = "heading-read-qualifier-count"
ITEM_COUNT = "heading-read-item-count"
UNOPENED_ITEM = "heading-read-unopened-item"
OWN_FIGURE_ABSENT = "heading-read-own-figure-absent"
ITEM_QUOTE_MISSING = "heading-read-item-quote-missing"
ITEM_QUOTE_ABSENT = "heading-read-item-quote-absent"
ITEM_QUOTE_REPEATED = "heading-read-item-quote-repeated"
ITEM_QUOTE_CHECK = "heading_read:item-quotes"
KINDS = (
    ITEM_QUOTE_MISSING,
    ITEM_QUOTE_ABSENT,
    ITEM_QUOTE_REPEATED,
    OWN_FIGURE_ABSENT,
    QUALIFIER_COUNT,
    ITEM_COUNT,
    UNOPENED_ITEM,
    MISSING_RECORD,
    DUPLICATE_RECORD,
    UNKNOWN_ROUTE,
    SENTENCE_COUNT_MISMATCH,
    UNKNOWN_HEADING,
    DROPPED_HEADING,
    DRAFT_MISMATCH,
    DEFECT_VERDICT,
    VERDICT_SHAPE,
    REPORTED_FINDING,
    CONTEXT_DIGEST_MISMATCH,
    CONTEXT_VERDICT_SHAPE,
    CONTEXT_DEFECT_VERDICT,
)


@dataclass(frozen=True)
class Record:
    artifact: str
    fields: dict[str, str] = field(default_factory=dict)
    pairs: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    items: tuple[str, ...] = ()
    remarks: tuple[str, ...] = ()
    unread: int = 0
    own: tuple[str, ...] = ()

    @property
    def own_figures(self) -> frozenset[str]:
        return frozenset(
            value.casefold()
            for lines, grammar in ((self.own, OWN), (self.items, ITEM))
            for line in lines
            for parsed in (grammar.fullmatch(line),)
            if parsed is not None and parsed.group("figures") is not None
            for value in NUMBER.findall(parsed.group("figures"))
        )

    def value(self, name: str) -> str:
        return self.fields.get(name, "")


@dataclass(frozen=True)
class Binding:
    artifact: str
    draft: bytes
    claims: tuple[research_ledger.Record, ...]
    context_digest: str
    as_of: date | None = None
    opened_items: tuple[str, ...] = ()
    other_classmate_items: tuple[str, ...] = ()
    context_run: Path | None = None
    context_available: bool = True
    claims_available: bool = True
    record_path: Path | None = None


def binding_from_context(artifact: str, draft: bytes, claims: tuple[research_ledger.Record, ...],
                         run: Path, *, as_of: date | None = None,
                         exclude_other_classmates: bool = False,
                         record_path: Path | None = None) -> Binding:
    """Keep independent heading checks available when context cannot be read."""
    import project_context
    available = not record_unavailable(run / "claims.md", artifact)
    heading_path = record_path or run / "heading-read.md"
    try:
        digest = project_context.recorded_digest(run, artifact=artifact)
        opened = project_context.recorded_opened_items(run, artifact=artifact)
        other = project_context.other_classmate_items(run, artifact) if exclude_other_classmates else ()
    except DamagedRecord as failure:
        damaged_record_result(failure, check="heading-read context comparisons", artifact=artifact)
        return Binding(artifact, draft, claims, "", as_of=as_of, context_run=run, context_available=False,
                       claims_available=available, record_path=heading_path)
    except UnreadableRecord as failure:
        mark_not_graded(failure, check="heading-read context comparisons")
        return Binding(artifact, draft, claims, "", as_of=as_of, context_run=run, context_available=False,
                       claims_available=available, record_path=heading_path)
    return Binding(artifact, draft, claims, digest, as_of=as_of, opened_items=opened,
                   other_classmate_items=other, context_run=run,
                   claims_available=available, record_path=heading_path)


def _context_matches(record: Record, binding: Binding) -> bool | None:
    if not binding.context_available:
        return None
    if binding.context_run is None:
        return record.value("CONTEXT-DIGEST").casefold() == binding.context_digest.casefold()
    import project_context
    try:
        return project_context.heading_context_matches(
            binding.context_run, record.value("CONTEXT-DIGEST").casefold(), record.artifact)
    except DamagedRecord as failure:
        damaged_record_result(failure, check="heading-read context comparisons", artifact=record.artifact)
        return None
    except UnreadableRecord as failure:
        mark_not_graded(failure, check="heading-read context comparisons")
        return None


@dataclass(frozen=True)
class Finding:
    kind: str
    artifact: str
    detail: str


@dataclass(frozen=True)
class Scan:
    records_read: int
    unread: int
    findings: tuple[Finding, ...]
    remarks: tuple[reader_remarks.Remark, ...] = ()
    unread_records: tuple[str, ...] = ()
    other_files: int | None = None
    unbound_unread: int = 0
    unread_items: int = 0
    service_items: int = 0
    absence_items: int = 0


def read_records(text: str) -> tuple[Record, ...]:
    records: list[Record] = []
    artifact: str | None = None
    fields: dict[str, str] = {}
    pairs: list[str] = []
    findings: list[str] = []
    items: list[str] = []
    own: list[str] = []
    remarks: list[str] = []
    unread = 0

    def close() -> None:
        if artifact is not None:
            records.append(Record(artifact, dict(fields), tuple(pairs), tuple(findings), tuple(items), tuple(remarks), unread, tuple(own)))

    for line in text.splitlines():
        heading = HEADER.match(line)
        if heading:
            close()
            artifact = heading.group(1).strip()
            fields, pairs, findings, items, remarks, unread, own = {}, [], [], [], [], 0, []
            continue
        if artifact is not None and OTHER_HEADER.match(line):
            close()
            artifact, fields, pairs, findings, items, remarks, unread, own = None, {}, [], [], [], [], 0, []
            continue
        if artifact is None:
            continue
        named = FIELD.match(line)
        if not named:
            unread += bool(line.strip())
            continue
        name, value = named.group(1).upper(), named.group(2).strip()
        if name == "REMARK":
            if value:
                remarks.append(value)
            else:
                unread += 1
        elif name == "PAIR":
            pairs.append(value)
        elif name == "ITEM":
            items.append(value)
        elif name == "OWN":
            if OWN.fullmatch(value):
                own.append(value)
            else:
                unread += 1
        elif name == "FINDINGS":
            findings.append(value)
        else:
            fields[name] = value
    close()
    return tuple(records)


def own_figures(text: str, artifact: str) -> frozenset[str]:
    """Return only figures listed by this artifact's heading reader."""
    return frozenset(value for record in read_records(text) if record.artifact == artifact for value in record.own_figures)


def _drifted_at(detail: str, location: str) -> bool:
    """A substantive drift finding attached to exactly this pair location."""
    return re.match(rf"(?i)drifted[ \t]+-[ \t]+{re.escape(location)},[ \t]+\S", detail) is not None


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _item_text(source) -> str:
    """Read only the exact recorded bytes; Word is rehashed after extraction."""
    raw = source.path.read_bytes()
    if file_digest.sha256_bytes(raw) != source.digest:
        raise ValueError("item fingerprint moved")
    if source.path.suffix.casefold() == ".docx":
        import docx_read
        text = "\n".join(docx_read.read_docx(source.path))
        if file_digest.sha256_bytes(source.path.read_bytes()) != source.digest:
            raise ValueError("item fingerprint moved during reading")
        return _normalized(text)
    return _normalized(raw.decode("utf-8"))


def _item_quotes(record: Record, binding: Binding, cache: dict, unread: set) -> tuple[list[Finding], int, int]:
    """Keep source-dependent coverage separate from independent record checks."""
    if not record.items or not completion_checks.active_for_item(ITEM_QUOTE_CHECK, binding.artifact):
        return [], 0, 0
    import project_context
    sources = ()
    available = binding.context_available
    try:
        if available and binding.context_run:
            sources = project_context.recorded_item_sources(binding.context_run, record.value("CONTEXT-DIGEST"), artifact=binding.artifact)
    except DamagedRecord as failure:
        damaged_record_result(failure, check="heading-read item quotes", artifact=binding.artifact)
        available = False
    except UnreadableRecord as failure:
        mark_not_graded(failure, check="heading-read item quotes")
        available = False
    except (OSError, ValueError):
        sources = ()
    found, services, absences = [], 0, 0
    for line in record.items:
        parsed = ITEM.fullmatch(line)
        if parsed is None:
            continue  # The existing item-shape row owns this finding.
        identifier = parsed.group("item").strip()
        matches = tuple({(source.path, source.digest): source for source in sources if source.identifier == identifier}.values())
        if len(matches) == 1 and matches[0].path is None:
            services += 1
            continue
        quote = parsed.group("quote")
        missing = not quote or quote.startswith('"') and not _normalized(quote[1:-1])
        if missing:
            found.append(Finding(ITEM_QUOTE_MISSING, record.artifact, "ITEM needs its supporting quote or absence sentinel"))
        if not available:
            continue
        if len(matches) != 1:
            unread.add((binding.context_run, identifier))
            continue
        source = matches[0]
        key = (source.path, source.digest)
        if key not in cache:
            try:
                cache[key] = _item_text(source)
            except (OSError, UnicodeError, ValueError, zipfile.BadZipFile, KeyError, ParseError,
                    NotImplementedError, RuntimeError, zlib.error, lzma.LZMAError, EOFError):
                cache[key] = None
        text = cache[key]
        if text is None:
            unread.add(source.path)
            continue
        if missing:
            continue
        if quote.casefold() == "absent - whole item searched":
            absences += 1
            continue
        needle = _normalized(quote[1:-1])
        occurrences = sum(text.startswith(needle, position) for position in range(len(text)))
        if occurrences != 1:
            kind = ITEM_QUOTE_ABSENT if occurrences == 0 else ITEM_QUOTE_REPEATED
            found.append(Finding(kind, record.artifact, "ITEM quote occurs " + str(occurrences) + " times in its recorded item"))
    return found, services, absences


def _record_findings(record: Record, binding: Binding) -> list[Finding]:
    found: list[Finding] = []
    artifact = record.artifact
    context_matches = _context_matches(record, binding)
    if record.value("ROUTE").casefold() not in ROUTES:
        found.append(Finding(UNKNOWN_ROUTE, artifact, record.value("ROUTE") or "ROUTE is missing"))

    sentence_match = SENTENCES.fullmatch(record.value("SENTENCES"))
    current = research_ledger.qualifiers_required(binding.as_of)
    if current and (sentence_match is None or sentence_match.group("item") is None):
        found.append(Finding(ITEM_COUNT, artifact, "SENTENCES must count item descriptions"))
    item_count = int(sentence_match.group("item") or 0) if sentence_match else 0
    if current:
        if len(record.items) != item_count:
            found.append(Finding(ITEM_COUNT, artifact, f"{len(record.items)} ITEM lines for {item_count} item sentences"))
        locations = set()
        for line in record.items:
            parsed_item = ITEM.fullmatch(line)
            if (parsed_item is None or context_matches is not None and (
                    parsed_item.group("item").strip() not in binding.opened_items
                    or parsed_item.group("item").strip() in binding.other_classmate_items)):
                found.append(Finding(UNOPENED_ITEM, artifact, line))
            if parsed_item:
                location = parsed_item.group("location").strip()
                if location in locations:
                    found.append(Finding(ITEM_COUNT, artifact, f"duplicate item location: {location}"))
                locations.add(location)
    factual = int(sentence_match.group("factual")) if sentence_match else -1
    paired_locations = {match.group("location").strip() for pair in record.pairs for match in (PAIR.fullmatch(pair),) if match}
    unpaired_findings = sum(
        not any(_drifted_at(detail, location) for location in paired_locations)
        for detail in record.findings
    )
    if factual < 0 or len(record.pairs) + unpaired_findings != factual:
        found.append(
            Finding(
                SENTENCE_COUNT_MISMATCH,
                artifact,
                f"{len(record.pairs)} pairs plus {len(record.findings)} findings; SENTENCES says {record.value('SENTENCES') or 'nothing'}",
            )
        )

    headings: dict[str, tuple[research_ledger.Record, ...]] = {}
    for claim in binding.claims:
        prefix = research_ledger.heading_digest(claim.claim)[:8]
        headings[prefix] = headings.get(prefix, ()) + (claim,)
    for pair in record.pairs if binding.claims_available else ():
        parsed = PAIR.fullmatch(pair)
        prefix = parsed.group("prefix").casefold() if parsed else ""
        matches = headings.get(prefix, ())
        if not matches:
            found.append(Finding(UNKNOWN_HEADING, artifact, pair))
        elif any("DROPPED" in claim.fields for claim in matches):
            found.append(Finding(DROPPED_HEADING, artifact, pair))
        else:
            for claim in matches:
                if "QUALIFIERS" not in claim.fields:
                    continue
                values = research_ledger.qualifiers(claim.value("QUALIFIERS"))
                read, total = parsed.group("read"), parsed.group("total")
                if values is None or total is None or int(total) != len(values) or int(read) > int(total):
                    found.append(Finding(QUALIFIER_COUNT, artifact, pair))
                elif int(read) < int(total):
                    location = parsed.group("location").strip()
                    if not any(_drifted_at(detail, location) for detail in record.findings):
                        found.append(Finding(QUALIFIER_COUNT, artifact, f"shortfall without a drifted finding: {pair}"))

    current_digest = file_digest.sha256_bytes(binding.draft)
    if record.value("DRAFT").casefold() != current_digest:
        found.append(
            Finding(
                DRAFT_MISMATCH,
                artifact,
                f"recorded {record.value('DRAFT') or 'nothing'}, current {current_digest}",
            )
        )

    recorded_context = record.value("CONTEXT-DIGEST").casefold()
    expected_context = binding.context_digest.casefold()
    if context_matches is not None and completion_checks.active("heading_read:heading-read-context-digest") and not context_matches:
        found.append(
            Finding(
                CONTEXT_DIGEST_MISMATCH,
                artifact,
                f"recorded {recorded_context or 'nothing'}, expected {expected_context or 'nothing'}",
            )
        )

    context_verdict = record.value("CONTEXT-VERDICT")
    context_keyword = context_verdict.casefold().split(maxsplit=1)[0] if context_verdict else ""
    if context_matches is not None and expected_context == "none":
        if context_verdict.casefold() != "none":
            found.append(
                Finding(
                    CONTEXT_VERDICT_SHAPE if context_keyword == "none" else CONTEXT_DEFECT_VERDICT,
                    artifact,
                    context_verdict or "CONTEXT-VERDICT is missing",
                )
            )
    elif context_matches is not None and context_verdict.casefold() != "agrees":
        shaped = re.fullmatch(
            r"(?i)(narrows|contradicts)[ \t]+-[ \t]+[^,]+,[ \t]+.+",
            context_verdict,
        )
        if shaped is None:
            conflict = re.fullmatch(
                r"(?i)sources-conflict[ \t]+-[ \t]+(?P<left>[^,]+?)[ \t]+and[ \t]+(?P<right>[^,]*),[ \t]+(?P<difference>.+)",
                context_verdict,
            )
            if conflict is not None:
                left = conflict.group("left").strip()
                right = conflict.group("right").strip()
                if left and right and left.casefold() != right.casefold():
                    shaped = conflict
        if shaped is None:
            found.append(
                Finding(
                    CONTEXT_VERDICT_SHAPE,
                    artifact,
                    context_verdict or "CONTEXT-VERDICT is missing",
                )
            )
        if context_keyword in ("narrows", "contradicts", "sources-conflict"):
            found.append(
                Finding(
                    CONTEXT_DEFECT_VERDICT,
                    artifact,
                    context_verdict,
                )
            )

    verdict = record.value("VERDICT")
    verdict_keyword = verdict.casefold().split(maxsplit=1)[0] if verdict else ""
    if verdict_keyword == "defect":
        found.append(Finding(DEFECT_VERDICT, artifact, verdict))
    if verdict.casefold() != "clean":
        if re.fullmatch(r"(?i)defect[ \t]+-[ \t]+.+", verdict) is None:
            found.append(Finding(VERDICT_SHAPE, artifact, verdict or "VERDICT is missing"))
    for detail in record.findings:
        found.append(Finding(REPORTED_FINDING, artifact, detail or "empty FINDINGS line"))
    return found


@completion_checks.dated_scan
def scan(text: str, bindings: tuple[Binding, ...]) -> Scan:
    """Grade records for the caller's expected drafts and claim scopes."""
    records = read_records(text)
    artifacts = {binding.artifact for binding in bindings}
    other_files = _other_files(text, artifacts)
    population = len(HEADING_CANDIDATE.findall(text)) - other_files
    read = 0
    found: list[Finding] = []
    expected = {binding.artifact: binding for binding in bindings}
    item_cache, unread_items = {}, set()
    service_items = absence_items = 0
    for artifact, binding in expected.items():
        if binding.record_path is not None and record_unavailable(binding.record_path, artifact):
            continue
        matches = tuple(record for record in records if record.artifact == artifact)
        if not matches:
            found.append(Finding(MISSING_RECORD, artifact, "no HEADING-READ record"))
            continue
        read += len(matches)
        if len(matches) > 1:
            found.append(
                Finding(DUPLICATE_RECORD, artifact, f"expected one record, found {len(matches)}")
            )
        for record in matches:
            found.extend(_record_findings(record, binding))
            quoted, services, absences = _item_quotes(record, binding, item_cache, unread_items)
            found.extend(quoted)
            service_items += services
            absence_items += absences
    bound_records = tuple(r for r in records if r.artifact in expected)
    unread = max(0, population - read) + sum(r.unread for r in bound_records) + len(unread_items)
    remarks = tuple(reader_remarks.Remark(f"HEADING-READ: {r.artifact}", text) for r in bound_records for text in r.remarks)
    return Scan(read, unread, tuple(found), remarks, tuple(r.artifact for r in bound_records if r.unread), other_files, max(0, population - read), len(unread_items), service_items, absence_items)


def _other_files(text: str, artifacts: set[str]) -> int:
    return sum(
        name not in artifacts and PurePath(name).suffix not in ("", ".")
        for line in HEADING_CANDIDATE.findall(text)
        if ":" in line
        for name in (line.split(":", 1)[1].strip(),)
    )


def _format_other_files(count: int) -> str:
    return f"heading-read records for other files: {count}"


def format_coverage(result: Scan, *, include_remainder: bool = True) -> str:
    return "\n".join(line for line in
        (
            f"heading-read records: {result.records_read}",
            _format_other_files(result.other_files) if result.other_files is not None else "",
            run_grader.format_unread_remainder(result.unread) if include_remainder else "",
            f"unread heading-read headings: {result.unbound_unread}" if not include_remainder and result.unbound_unread else "",
            f"unread heading-read record lines: {result.unread - result.unbound_unread - result.unread_items}" if not include_remainder and result.unread > result.unbound_unread + result.unread_items else "",
            format_item_coverage(result),
            *(f"unread reader record: HEADING-READ: {name}" for name in result.unread_records),
            reader_remarks.report(result.remarks),
        ) if line
    )


def format_item_coverage(result: Scan) -> str:
    return "\n".join(line for line in (
        f"unread item sources: {result.unread_items}" if result.unread_items else "",
        f"service-item quotes: {result.service_items} counted, not graded" if result.service_items else "",
        f"item absence claims: {result.absence_items} not graded - whole-item search unverified" if result.absence_items else "",
    ) if line)


def protocol_coverage(
    claims_text: str, heading_text: str, artifacts: tuple[str, ...], *, report_other_files: bool = True
) -> str:
    """Report the ungraded legacy populations without implying a clean zero."""
    claims = research_ledger.read_records(claims_text)
    headings = {research_ledger.heading_digest(claim.claim)[:8]: claim for claim in claims}
    records = read_records(heading_text)
    unread_pairs = sum(
        parsed is not None and (
            parsed.group("prefix").casefold() not in headings
            or "QUALIFIERS" not in headings[parsed.group("prefix").casefold()].fields
        )
        for record in records for pair in record.pairs
        for parsed in (PAIR.fullmatch(pair),)
    )
    lines = [_format_other_files(_other_files(heading_text, set(artifacts)))] if report_other_files else []
    if not research_ledger.qualifiers_required(research_ledger.ledger_date(claims_text)):
        bound_count = sum(record.artifact in artifacts for record in records)
        lines.append(f"item-description comparisons: {run_grader.NOT_GRADED} - unread {bound_count} heading-read records")
    if unread_pairs:
        lines.append(f"qualifier pair counts: {run_grader.NOT_GRADED} - unread {unread_pairs}")
    return "\n".join(lines)
