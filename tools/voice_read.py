#!/usr/bin/env python3
"""Grade the planted coursework voice read and its model-owned profanity row.

``DECLARED_LIMITS`` is the complete ceiling of these completion gates. The
scoped coursework graders, their skills, and ``CLAUDE.md`` point to this object and copy
no row.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping
from typing import Generic, NamedTuple, TypeVar

import repo_root
import run_grader
import voice_model_identity


PLANTED_COPY_NAME = "voice-read-planted.txt"
PLANTER_RECORD_NAME = "voice-read-planter.json"
READER_RECORD_NAME = "voice-read.json"
RECORDS_DIRECTORY = "voice-reads"
EXPECTED_ROW = "the coursework voice read"
PROFANITY_EXPECTED_ROW = "graded coursework profanity"
SCOPED_SKILLS = voice_model_identity.SCOPED_SKILLS
COMPLETION_GRADERS = MappingProxyType(dict(voice_model_identity.COMPLETION_GRADERS))
class DeclaredLimit(NamedTuple):
    """One named coverage boundary and how its evidence is maintained."""

    key: str
    limit: str
    evidence: run_grader.EvidenceDisposition


DECLARED_LIMITS = (
    DeclaredLimit(
        "consistency-is-not-identity",
        "a clean voice read establishes consistency with the model's samples, not that the draft sounds like its clinician",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "plant-genericness-is-read",
        "whether the planted rewrite is truly generic remains a reader's judgment",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "reader-judgment-is-unproven",
        "a well-formed record proves the reader compared but cannot prove every placement was judged well",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "model-gaps-remain",
        "content absent from the canonical model cannot be found by the voice read",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "ambiguous-profanity-is-read",
        "ordinary-sense words deliberately excluded from the model's profanity list remain the voice reader's judgment in context",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "presentation-intent-is-separate",
        "the voice read does not establish that a deck follows the assignment's signed audience purpose or talk style",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
)

_PAIR_SECTION = re.compile(
    r"^### Discriminating pairs\s*$\n(?P<body>.*?)(?=^### |^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_PAIR_CANDIDATE = re.compile(r"^\*\*(?P<header>[^\n]*)$", re.MULTILINE)
_PAIR_HEADING = re.compile(r"(?P<identifier>[^*\n]+?)\.\*\*(?:[^\n]*)$")
_HALF = re.compile(
    r"^- \*(?P<kind>Generic|His)(?:\s*\([^)]*\))?\*:\s*(?P<text>.*?)(?=^- \*(?:Generic|His)(?:\s*\([^)]*\))?\*:|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
_PROFANITY_SECTION = re.compile(
    r"^## Profanity — the list graded copy never carries\s*$\n(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_BACKTICK = re.compile(r"`([^`\n]+)`")
_WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
_ABBREVIATION = re.compile(
    r"(?:\b(?:mr|mrs|ms|dr|prof|sr|jr|st|vs|etc|e\.g|i\.e)|\b[A-Z])\.$",
    re.IGNORECASE,
)
_MARKDOWN_PREFIX = re.compile(r"\s*(?:(?:[-*+>]|\d+[.)]|#+)\s*)?")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_PLANTER_KEYS = frozenset(
    {
        "status",
        "draft_sha256",
        "planted_sha256",
        "pair_id",
        "original_sentence",
        "planted_sentence",
    }
)
_READER_KEYS = frozenset(
    {
        "status",
        "draft_sha256",
        "planted_sha256",
        "model_sha256",
        "suspected_plant_quote",
        "answers",
    }
)
_ANSWER_KEYS = frozenset({"pair_id", "quote", "resemblance"})
TScan = TypeVar("TScan")


@dataclass(frozen=True)
class Pair:
    identifier: str
    generic: str
    his: str


@dataclass(frozen=True)
class ModelPopulation(Generic[TScan]):
    """One independently counted model population and its readable members."""

    items: tuple[TScan, ...]
    candidates: int
    unread: int
    missing: bool = False


@dataclass(frozen=True)
class DraftSurface:
    sha256: str
    text: str
    plantable_text: str


@dataclass(frozen=True)
class CompletionGate:
    finding: bool
    coverage: bool
    reports: tuple[str, str]


@dataclass(frozen=True)
class VoiceResult:
    """One submission's self-describing voice-read result."""

    key: str
    finding: bool
    coverage: bool
    report: str


def draft_surface(
    artifacts: tuple[tuple[Path, str], ...],
    *,
    plantable_text: str | None = None,
) -> DraftSurface:
    """Bind one grader-owned artifact population to its exact voice surface."""
    text = "\n".join(item_text for _path, item_text in artifacts)
    if len(artifacts) == 1:
        digest = hashlib.sha256(artifacts[0][0].read_bytes()).hexdigest()
    else:
        digest = _digest_text(text)
    return DraftSurface(
        sha256=digest,
        text=text,
        plantable_text=text if plantable_text is None else plantable_text,
    )


def _digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _markdown_value(text: str) -> str:
    value = re.sub(r"\s+", " ", text.strip())
    if len(value) >= 2 and value[0] in {'"', '“'} and value[-1] in {'"', '”'}:
        value = value[1:-1]
    return value.strip()


def read_pairs(model_text: str) -> ModelPopulation[Pair]:
    """Derive the complete discriminating-pair population from the model."""
    sections = tuple(_PAIR_SECTION.finditer(model_text))
    if not sections:
        return ModelPopulation((), 0, 0, True)
    pairs: list[Pair] = []
    candidate_count = 0
    for section in sections:
        body = section.group("body")
        candidates = tuple(_PAIR_CANDIDATE.finditer(body))
        candidate_count += len(candidates)
        for index, match in enumerate(candidates):
            end = (
                candidates[index + 1].start()
                if index + 1 < len(candidates)
                else len(body)
            )
            candidate_body = body[match.end() : end]
            heading = _PAIR_HEADING.fullmatch(match.group("header"))
            half_matches = tuple(_HALF.finditer(candidate_body))
            halves = [
                (half.group("kind").casefold(), _markdown_value(half.group("text")))
                for half in half_matches
            ]
            if (
                heading is not None
                and len(halves) == 2
                and {kind for kind, _text in halves} == {"generic", "his"}
                and all(text for _kind, text in halves)
            ):
                by_kind = dict(halves)
                pairs.append(
                    Pair(
                        identifier=heading.group("identifier").strip(),
                        generic=by_kind["generic"],
                        his=by_kind["his"],
                    )
                )
    return ModelPopulation(tuple(pairs), candidate_count, candidate_count - len(pairs))


def read_profanity_terms(model_text: str) -> ModelPopulation[str]:
    """Read the model-owned profanity vocabulary without carrying a second list."""
    section = _PROFANITY_SECTION.search(model_text)
    if section is None:
        return ModelPopulation((), 0, 0, True)
    terms: list[str] = []
    rows = tuple(
        line for line in section.group("body").splitlines() if re.match(r"^\s*-\s+", line)
    )
    unread = 0
    for line in rows:
        values = _BACKTICK.findall(line)
        if not values:
            unread += 1
            continue
        for value in values:
            normalized = re.sub(r"\s+", " ", value.strip()).casefold()
            if normalized and normalized not in terms:
                terms.append(normalized)
    return ModelPopulation(tuple(terms), len(rows), unread)


def profanity_matches(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    """Return matched model terms; single words also fire inside compounds."""
    folded = text.casefold()
    words = tuple(match.group(0).casefold() for match in _WORD.finditer(text))
    found: list[str] = []
    for term in terms:
        matched = (
            bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", folded))
            if " " in term
            else any(term in word for word in words)
        )
        if matched:
            found.append(term)
    return tuple(found)


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _identity_digest(run: Path) -> str | None:
    payload = _read_json(run / voice_model_identity.RECORD_NAME)
    if not isinstance(payload, dict):
        return None
    value = payload.get("sha256")
    return value if isinstance(value, str) and _SHA256.fullmatch(value) else None


def _not_run(payload: object) -> bool:
    return (
        isinstance(payload, dict)
        and frozenset(payload) == {"status", "reason"}
        and payload.get("status") == "not run"
        and isinstance(payload.get("reason"), str)
        and bool(payload["reason"].strip())
    )


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _one_sentence(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped:
        return False
    terminals: list[int] = []
    for match in re.finditer(r"[.!?](?:[\"”'])?", stripped):
        punctuation = stripped[match.start()]
        if punctuation == "." and (
            _ABBREVIATION.search(stripped[: match.start() + 1])
            or (
                match.start() > 0
                and match.end() < len(stripped)
                and stripped[match.start() - 1].isdigit()
                and stripped[match.end()].isdigit()
            )
        ):
            continue
        if match.end() == len(stripped) or stripped[match.end()].isspace():
            terminals.append(match.end())
    return terminals == [len(stripped)]


def _sentence_start_boundary(text: str, start: int) -> bool:
    if start == 0:
        return True
    line_start = text.rfind("\n", 0, start) + 1
    if _MARKDOWN_PREFIX.fullmatch(text[line_start:start]):
        return True
    if not text[start - 1].isspace():
        return False
    left = text[:start].rstrip().rstrip('"”\'’)]}')
    return bool(left) and left[-1] in ".!?" and _ABBREVIATION.search(left) is None


def _verbatim_sentence(text: str, quote: str) -> bool:
    """Require an exact sentence, not merely a punctuated substring."""
    if not _one_sentence(quote):
        return False
    start = 0
    while True:
        start = text.find(quote, start)
        if start < 0:
            return False
        end = start + len(quote)
        left_boundary = _sentence_start_boundary(text, start)
        right_boundary = end == len(text) or text[end].isspace()
        if left_boundary and right_boundary:
            return True
        start += 1


def _voice_result(
    records: Path,
    run: Path,
    surface: DraftSurface,
    pairs: tuple[Pair, ...],
    model_digest: str,
) -> tuple[bool, bool, str]:
    planter = _read_json(records / PLANTER_RECORD_NAME)
    reader = _read_json(records / READER_RECORD_NAME)
    if _not_run(planter) and _not_run(reader):
        return False, True, "not scanned - recorded as not run"
    if planter is None or reader is None:
        return True, False, "finding - planter or reader record is missing or invalid"
    if not isinstance(planter, dict) or not isinstance(reader, dict):
        return True, False, "finding - planter or reader record shape is invalid"
    if planter.get("status") != "complete" or reader.get("status") != "complete":
        return True, False, "finding - planter or reader status is invalid"
    if frozenset(planter) != _PLANTER_KEYS or frozenset(reader) != _READER_KEYS:
        return True, False, "finding - planter or reader record shape is invalid"

    planted_path = records / PLANTED_COPY_NAME
    try:
        planted_bytes = planted_path.read_bytes()
        planted = planted_bytes.decode("utf-8")
    except (OSError, UnicodeError):
        return True, False, "finding - planted copy is missing or unreadable"
    planted_digest = hashlib.sha256(planted_bytes).hexdigest()
    if (
        not _valid_digest(planter.get("draft_sha256"))
        or not _valid_digest(planter.get("planted_sha256"))
        or not _valid_digest(reader.get("draft_sha256"))
        or not _valid_digest(reader.get("planted_sha256"))
        or not _valid_digest(reader.get("model_sha256"))
    ):
        return True, False, "finding - record digest shape is invalid"
    if planter["draft_sha256"] != surface.sha256 or reader["draft_sha256"] != surface.sha256:
        return True, False, "finding - draft digest moved since the read"
    if planter["planted_sha256"] != planted_digest or reader["planted_sha256"] != planted_digest:
        return True, False, "finding - planted-copy digest does not match"
    identity_digest = _identity_digest(run)
    if reader["model_sha256"] != model_digest or reader["model_sha256"] != identity_digest:
        return True, False, "finding - model digest does not match the identity record"

    original = planter.get("original_sentence")
    replacement = planter.get("planted_sentence")
    pair_id = planter.get("pair_id")
    if not all(isinstance(value, str) and value for value in (original, replacement, pair_id)):
        return True, False, "finding - planter record does not name the changed sentence"
    if surface.text.count(original) != 1 or original not in surface.plantable_text:
        return True, False, "finding - planter record does not name one plantable draft sentence"
    if (
        original == replacement
        or not _verbatim_sentence(surface.text, original)
        or not _one_sentence(replacement)
    ):
        return True, False, "finding - plant is not one replacement sentence"
    expected_planted = surface.text.replace(original, replacement, 1)
    if planted != expected_planted:
        return True, False, "finding - planted copy differs in other than the named sentence"
    if not _verbatim_sentence(planted, replacement):
        return True, False, "finding - planted sentence is not one complete sentence"

    population = {pair.identifier for pair in pairs}
    if len(population) != len(pairs):
        return False, True, "not scanned - canonical pair identifiers are not unique"
    if pair_id not in population:
        return True, False, "finding - planter pair is not in the canonical model"
    answers = reader.get("answers")
    if not isinstance(answers, list):
        return True, False, "finding - pair answers are missing"
    by_id: dict[str, dict[str, object]] = {}
    for answer in answers:
        if (
            not isinstance(answer, dict)
            or frozenset(answer) != _ANSWER_KEYS
            or not isinstance(answer.get("pair_id"), str)
        ):
            return True, False, "finding - pair answer shape is invalid"
        identifier = answer["pair_id"]
        if identifier in by_id:
            return True, False, "finding - pair population is not answered exactly once"
        by_id[identifier] = answer
    if set(by_id) != population:
        return True, False, "finding - pair population is not fully answered"

    planted_flagged = False
    real_generic = False
    for answer in by_id.values():
        resemblance = answer.get("resemblance")
        quote = answer.get("quote")
        if resemblance == "no counterpart":
            if quote is not None:
                return True, False, "finding - no-counterpart answer carries a quote"
            continue
        if resemblance not in {"generic", "his"} or not isinstance(quote, str) or not quote:
            return True, False, "finding - pair answer shape is invalid"
        if not _verbatim_sentence(planted, quote):
            return True, False, "finding - pair quote is not present or is not a verbatim sentence in the planted copy"
        if resemblance == "generic":
            if quote == replacement:
                planted_flagged = True
            else:
                real_generic = True
    if reader.get("suspected_plant_quote") != replacement or not planted_flagged:
        return True, False, "finding - planted sentence was not flagged"
    if real_generic:
        return True, False, "finding - a real draft sentence was placed on a generic half"
    return False, False, "clean"


def completion_gate(
    run: Path,
    submission: str | None,
    surface: DraftSurface | Mapping[str, DraftSurface],
) -> CompletionGate:
    """Grade both shared rows when a terminal coursework submission is named."""
    if submission is None:
        suffix = "not graded - --submission was not supplied"
        return CompletionGate(False, False, (f"{EXPECTED_ROW}: {suffix}", f"{PROFANITY_EXPECTED_ROW}: {suffix}"))
    try:
        resolved = repo_root.canonical_voice_model()
        if not resolved.exists or resolved.sha256 is None:
            suffix = "not scanned - canonical voice model is absent"
            return CompletionGate(False, True, (f"{EXPECTED_ROW}: {suffix}", f"{PROFANITY_EXPECTED_ROW}: {suffix}"))
        model_text = resolved.path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        suffix = "not scanned - canonical voice model is unreadable"
        return CompletionGate(False, True, (f"{EXPECTED_ROW}: {suffix}", f"{PROFANITY_EXPECTED_ROW}: {suffix}"))

    pair_read = read_pairs(model_text)
    profanity_read = read_profanity_terms(model_text)
    keys = tuple(value.strip() for value in submission.split(",") if value.strip())
    surfaces = (
        {Path(key).stem: surface for key in keys}
        if isinstance(surface, DraftSurface)
        else {Path(key).stem: value for key, value in surface.items()}
    )
    voice_results: list[VoiceResult] = []
    profanity_count = 0
    drafts_with_profanity = 0
    for raw_key in keys:
        key = Path(raw_key).stem
        draft = surfaces.get(key)
        if draft is None:
            voice_results.append(
                VoiceResult(
                    key,
                    False,
                    True,
                    "not scanned - submission surface is unreadable; "
                    f"pair candidates {pair_read.candidates}; "
                    f"unread remainder {pair_read.unread}",
                )
            )
            continue
        records = run / RECORDS_DIRECTORY / key
        if not pair_read.items:
            result = (False, True, "not scanned - no discriminating-pair population was read")
        else:
            result = _voice_result(records, run, draft, pair_read.items, resolved.sha256)
        finding, coverage, report = result
        if pair_read.unread:
            coverage = True
        report += (
            f"; pair candidates {pair_read.candidates}; "
            f"unread remainder {pair_read.unread}"
        )
        voice_results.append(VoiceResult(key, finding, coverage, report))
        matched = (
            profanity_matches(draft.text, profanity_read.items)
            if profanity_read.items
            else ()
        )
        profanity_count += len(matched)
        drafts_with_profanity += bool(matched)

    voice_finding = any(result.finding for result in voice_results)
    voice_coverage = any(result.coverage for result in voice_results)
    if len(voice_results) == 1:
        voice_report = voice_results[0].report
    elif voice_results and not voice_finding and not voice_coverage:
        voice_report = (
            f"clean - {len(voice_results)} submissions; "
            f"pair candidates {pair_read.candidates}; "
            f"unread remainder {pair_read.unread}"
        )
    elif voice_results:
        voice_report = "; ".join(
            f"{result.key}: {result.report}" for result in voice_results
        )
    else:
        voice_coverage = True
        voice_report = (
            "not scanned - no submission key was read; "
            f"pair candidates {pair_read.candidates}; "
            f"unread remainder {pair_read.unread}"
        )
    if not profanity_read.items:
        profanity_finding = False
        profanity_coverage = True
        profanity_report = "not scanned - canonical model carries no profanity list"
    elif profanity_count:
        profanity_finding = True
        profanity_coverage = False
        profanity_report = (
            f"finding - {profanity_count} model-owned term(s) found across "
            f"{drafts_with_profanity} submission(s)"
        )
    else:
        profanity_finding = False
        profanity_coverage = False
        profanity_report = "clean"
    if profanity_read.unread:
        profanity_coverage = True
    profanity_report += (
        f"; profanity rows {profanity_read.candidates}; "
        f"unread remainder {profanity_read.unread}"
    )
    return CompletionGate(
        finding=voice_finding or profanity_finding,
        coverage=voice_coverage or profanity_coverage,
        reports=(
            f"{EXPECTED_ROW}: {voice_report}",
            f"{PROFANITY_EXPECTED_ROW}: {profanity_report}",
        ),
    )


def apply_completion_gate(
    grade: run_grader.Grade[TScan],
    run: Path,
    submission: str | None,
    surface: DraftSurface | Mapping[str, DraftSurface],
    *,
    coverage_limb: str | None = None,
) -> run_grader.Grade[TScan]:
    """Add the voice-read and profanity rows to a completion grade."""
    gate = completion_gate(run, submission, surface)
    limbs = grade.coverage_limbs
    if gate.coverage and coverage_limb is not None:
        limbs += (coverage_limb,)
    return replace(
        grade,
        findings_failed=grade.findings_failed or gate.finding,
        coverage_failed=grade.coverage_failed or gate.coverage,
        coverage_limbs=limbs,
        reports=grade.reports + gate.reports,
    )
