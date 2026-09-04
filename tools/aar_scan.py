#!/usr/bin/env python3
"""Extract and grade the private after-action review for one submission.

    python tools/aar_scan.py <run-directory> --transcript <session.jsonl> \
        --submission <submission-key> --memory-index <MEMORY.md> --extract
    python tools/aar_scan.py <run-directory> --submission <submission-key> [--show]
    python tools/aar_scan.py --session-end

The first form writes a reduced, private review packet under ``<run>/aar/``.
It keeps human turns, assistant text, subagent result bodies, and tool names and
statuses. Tool-result bodies are otherwise dropped. The packet fixes the
candidate population; a fresh adversarial reader, not this command, classifies
which candidates are observed corrections and writes the review record.

The second form grades that record. Counts are safe to paste; ``--show`` names
private findings and must not be pasted. A run directory and every artifact
under ``aar/`` are private working material.

The complete coverage boundary is ``DECLARED_LIMITS``. This docstring points at
that object and does not maintain a second copy of its rows. #814.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from console_codec import use_utf8
import git_paths
import repo_root
import run_grader


NOT_GRADED = run_grader.NOT_GRADED


SCOPED_SKILLS = frozenset(
    {
        "batch-shift",
        "clinical-note",
        "course-assignment",
        "discussion-post",
        "discussion-reply",
        "icd10-cpt",
        "practicum-case-study",
    }
)
EXPECTED_ROW = "the after-action review"
DISPOSITIONS = frozenset({"skill-file", "tracker-ticket", "memory-write", "check"})
CORRECTORS = frozenset({"clinician", "agent-or-tool", "orchestrator"})
PRIVATE_TEXT_SUFFIXES = frozenset({".md", ".txt", ".json"})
SUBAGENT_TOOLS = frozenset({"Agent", "Task", "Monitor", "TaskStop"})

ROWS: Mapping[str, str] = MappingProxyType(
    {
        "missing-review": "the submission has no review record",
        "unscannable-review": "the review record or its evidence cannot be scanned",
        "missing-header-field": "a required review header field is absent",
        "wrong-submission": "the review names another submission",
        "non-numeric-coverage": "the population or unread count is not numeric",
        "population-mismatch": "the review and extract populations disagree",
        "unread-candidates": "the review leaves candidate records unread",
        "watermark-mismatch": "the review and extract watermarks disagree",
        "transcript-mismatch": "the review and extract transcript sets disagree",
        "missing-correction-verdict": "the correction population has no verdict",
        "contradictory-correction-verdict": "correction records contradict a none verdict",
        "missing-sustain-verdict": "the sustain population has no verdict",
        "contradictory-sustain-verdict": "sustain records contradict a none verdict",
        "bad-orphan-pointer": "an orphan pointer cannot be read",
        "unknown-correction-event": "a correction names no extracted candidate",
        "missing-correction-field": "a correction lacks a required field",
        "unknown-corrector": "a correction names no declared corrector",
        "unknown-error-party": "a correction names no declared party in error",
        "unknown-disposition": "a correction names no declared disposition",
        "unlanded-ticket": "a tracker-ticket correction has no landed ticket",
        "unlanded-memory": "a memory correction has no changed memory target",
        "unlanded-check": "a check correction has no changed tracked check",
        "unknown-sustain-event": "a sustain names no extracted candidate",
        "bare-sustain": "a sustain lacks substantive classification",
        "missing-gh-call": "a tracker disposition has no successful GitHub call",
    }
)
KINDS = tuple(ROWS)

DECLARED_LIMITS = (
    (
        "semantic classification",
        "The command fixes the candidate population and cannot decide whether a candidate is a correction or whether the classifier's disposition is right.",
    ),
    (
        "tool-result-only correction",
        "Ordinary tool-result bodies are dropped; a correction that lived only there and was silently acted on is not extractable.",
    ),
    (
        "uncorrected error",
        "An error nobody contradicted is not an observed correction and cannot enter this review.",
    ),
    (
        "orchestrator veto",
        "The grader records disagreements but cannot prevent an orchestrator from overruling every unflattering classification.",
    ),
    (
        "subagent silence",
        "A subagent error never contradicted in the main transcript remains invisible.",
    ),
    (
        "transcript flush",
        "Claude Code writes transcripts asynchronously; a final entry not flushed before extraction or SessionEnd is outside the measured population.",
    ),
    (
        "run-key discovery",
        "SessionEnd can point only to an existing run directory named in a retained tool call; a scoped sitting that never named one cannot be pointed at safely.",
    ),
)
NOT_REACHED = tuple(reason for _subject, reason in DECLARED_LIMITS)

HEADER_FIELDS = (
    "SUBMISSION",
    "TRANSCRIPTS",
    "POPULATION",
    "UNREAD",
    "WATERMARK",
    "MEMORY-INDEX",
    "CLASSIFIER",
    "DISAGREEMENTS",
)
CORRECTION_FIELDS = (
    "CORRECTOR",
    "IN-ERROR",
    "SUMMARY",
    "CLASSIFIER",
    "ORCHESTRATOR",
    "DISPOSITION",
    "TARGET",
    "LANDING",
)

FIELD = re.compile(r"^(?P<name>[A-Z][A-Z-]*):\s*(?P<value>.*)$")
CORRECTION_HEADING = re.compile(r"^## CORRECTION:\s*(?P<event>\S+)\s*$")
SUSTAIN_HEADING = re.compile(r"^## SUSTAIN:\s*(?P<event>\S+)\s*$")
RUN_REFERENCE = re.compile(
    r"(?i)(?:[A-Za-z]:)?[^\s\"'<>|]*scratch[\\/]runs[\\/](?P<key>[^\\/\s\"'<>|]+)"
)
GH_ISSUE = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/[0-9]+\Z")


@dataclass(frozen=True)
class Candidate:
    identifier: str
    transcript_id: str
    kind: str
    text: str


@dataclass(frozen=True)
class Correction:
    event: str
    fields: Mapping[str, str]


@dataclass(frozen=True)
class Sustain:
    event: str
    fields: Mapping[str, str]


@dataclass(frozen=True)
class Review:
    path: Path
    fields: Mapping[str, str]
    corrections: tuple[Correction, ...]
    sustains: tuple[Sustain, ...]
    corrections_none: bool
    sustains_none: bool


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    detail: str


@dataclass(frozen=True)
class Scan:
    submission: str
    records: int
    population: int
    corrections: int
    sustains: int
    unread: int
    orphaned: int
    findings: tuple[Finding, ...]


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _content_blocks(message: Any) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    return [row for row in content if isinstance(row, dict)] if isinstance(content, list) else []


def read_transcript(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read transcript {path.name}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on transcript line {number}") from exc
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _tool_index(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    tools: dict[str, str] = {}
    for row in rows:
        if row.get("type") != "assistant":
            continue
        for block in _content_blocks(row.get("message")):
            if block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                tools[block["id"]] = _text(block.get("name")) or "unknown-tool"
    return tools


def _result_status(block: Mapping[str, Any]) -> str:
    return "failed" if block.get("is_error") is True else "completed"


def _human_text(row: Mapping[str, Any]) -> str:
    message = row.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        value = content.strip()
    elif isinstance(content, list):
        value = "\n".join(
            _text(block.get("text"))
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    else:
        return ""
    if value.startswith("<command-message>") or value.startswith("<local-command-caveat>"):
        return ""
    return value


def reduce_transcript(path: Path) -> list[Candidate]:
    """The fixed candidate population, in transcript order."""
    rows = read_transcript(path)
    tools = _tool_index(rows)
    transcript_id = path.stem
    candidates: list[Candidate] = []
    for ordinal, row in enumerate(rows, 1):
        uuid = _text(row.get("uuid")) or f"line-{ordinal}"
        if row.get("type") == "user":
            human = _human_text(row)
            if human:
                candidates.append(Candidate(uuid, transcript_id, "clinician", human))
            for index, block in enumerate(_content_blocks(row.get("message")), 1):
                if block.get("type") != "tool_result":
                    continue
                tool_id = _text(block.get("tool_use_id"))
                tool = tools.get(tool_id, "unknown-tool")
                if tool in SUBAGENT_TOOLS:
                    body = block.get("content")
                    if isinstance(body, list):
                        body = "\n".join(
                            _text(part.get("text"))
                            for part in body
                            if isinstance(part, dict) and part.get("type") == "text"
                        )
                    body = _text(body).strip()
                    if body:
                        candidates.append(
                            Candidate(
                                f"{uuid}#subagent-{index}",
                                transcript_id,
                                "subagent-result",
                                body,
                            )
                        )
                candidates.append(
                    Candidate(
                        f"{uuid}#status-{index}",
                        transcript_id,
                        "tool-status",
                        f"{tool}: {_result_status(block)}",
                    )
                )
        elif row.get("type") == "assistant":
            for index, block in enumerate(_content_blocks(row.get("message")), 1):
                if block.get("type") == "text" and _text(block.get("text")).strip():
                    candidates.append(
                        Candidate(
                            f"{uuid}#text-{index}",
                            transcript_id,
                            "assistant",
                            _text(block.get("text")).strip(),
                        )
                    )
                elif block.get("type") == "tool_use":
                    candidates.append(
                        Candidate(
                            f"{uuid}#tool-{index}",
                            transcript_id,
                            "tool-call",
                            _text(block.get("name")) or "unknown-tool",
                        )
                    )
    return candidates


def _safe_submission(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    if not safe:
        raise ValueError("submission key has no filename-safe characters")
    return safe


def review_path(run: Path, submission: str) -> Path:
    return run / "aar" / f"{_safe_submission(submission)}.md"


def extract_path(run: Path, submission: str) -> Path:
    return run / "aar" / f"{_safe_submission(submission)}.extract.md"


def baseline_path(run: Path, submission: str) -> Path:
    return run / "aar" / f"{_safe_submission(submission)}.baseline.json"


def orphan_paths(run: Path) -> tuple[Path, ...]:
    root = run / "aar"
    return tuple(sorted(root.glob("orphaned-*.json"))) if root.is_dir() else ()


def _read_pointer(path: Path) -> tuple[Path, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable orphan pointer {path.name}") from exc
    if not isinstance(payload, dict) or set(payload) != {"transcript_path", "run_key"}:
        raise ValueError(f"orphan pointer {path.name} does not have exactly two fields")
    transcript = payload.get("transcript_path")
    run_key = payload.get("run_key")
    if not isinstance(transcript, str) or not isinstance(run_key, str):
        raise ValueError(f"orphan pointer {path.name} has a non-text field")
    return Path(transcript), run_key


def _hash(path: Path) -> str | None:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _tracked_files() -> tuple[Path, ...]:
    """Tracked files used for landing evidence; untracked files are not visible."""
    root = Path(__file__).resolve().parent.parent
    return tuple(
        root / path
        for path in git_paths.read_path_records(root, "ls-files", "-z")
    )


def _memory_files(index: Path) -> tuple[Path, ...]:
    root = index.parent
    return tuple(sorted(path for path in root.rglob("*") if path.is_file()))


def snapshot(memory_index: Path) -> dict[str, str | None]:
    paths = (*_tracked_files(), *_memory_files(memory_index))
    return {str(path.resolve()): _hash(path) for path in paths}


def _last_watermarks(run: Path) -> dict[str, str]:
    watermarks: dict[str, str] = {}
    root = run / "aar"
    if not root.is_dir():
        return watermarks
    for path in sorted(root.glob("*.md")):
        if path.name.endswith(".extract.md"):
            continue
        try:
            review = read_review(path)
        except ValueError:
            continue
        transcripts = [value.strip() for value in review.fields.get("TRANSCRIPTS", "").split(",")]
        if transcripts and review.fields.get("WATERMARK"):
            watermarks[transcripts[-1]] = review.fields["WATERMARK"]
    return watermarks


def _after_watermark(candidates: list[Candidate], watermark: str | None) -> list[Candidate]:
    if watermark is None:
        return candidates
    indexes = [index for index, row in enumerate(candidates) if row.identifier == watermark]
    if not indexes:
        raise ValueError("prior watermark is not in its transcript population")
    return candidates[indexes[-1] + 1 :]


def collect_population(run: Path, transcript: Path) -> tuple[list[Candidate], tuple[Path, ...]]:
    transcripts: list[Path] = []
    pointers = orphan_paths(run)
    for pointer in pointers:
        orphan, run_key = _read_pointer(pointer)
        if run_key != run.name:
            raise ValueError(f"orphan pointer {pointer.name} names another run")
        if orphan.resolve() != transcript.resolve():
            transcripts.append(orphan)
    transcripts.append(transcript)
    watermarks = _last_watermarks(run)
    population: list[Candidate] = []
    seen: set[str] = set()
    for source in transcripts:
        if source.stem in seen:
            continue
        seen.add(source.stem)
        rows = reduce_transcript(source)
        population.extend(_after_watermark(rows, watermarks.get(source.stem)))
    return population, tuple(transcripts)


def write_extract(
    run: Path,
    transcript: Path,
    submission: str,
    memory_index: Path,
) -> tuple[Path, int]:
    population, transcripts = collect_population(run, transcript)
    if not population:
        raise ValueError("candidate population is empty")
    destination = extract_path(run, submission)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# PRIVATE AAR EXTRACT",
        f"SUBMISSION: {submission}",
        "TRANSCRIPTS: " + ", ".join(path.stem for path in transcripts),
        "TRANSCRIPT-PATHS: " + " | ".join(str(path.resolve()) for path in transcripts),
        f"POPULATION: {len(population)}",
        f"WATERMARK: {population[-1].identifier}",
        f"MEMORY-INDEX: {memory_index.resolve()}",
        "",
    ]
    for row in population:
        lines.extend(
            [
                f"## ENTRY: {row.identifier}",
                f"TRANSCRIPT: {row.transcript_id}",
                f"KIND: {row.kind}",
                "TEXT:",
                row.text,
                "",
            ]
        )
    destination.write_text("\n".join(lines), encoding="utf-8")
    baseline_path(run, submission).write_text(
        json.dumps(snapshot(memory_index), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination, len(population)


def _parse_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    for line in lines:
        match = FIELD.match(line)
        if match:
            current = match.group("name")
            fields[current] = match.group("value").strip()
        elif current and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields


def read_review(path: Path) -> Review:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read review {path.name}") from exc
    header: list[str] = []
    corrections: list[Correction] = []
    sustains: list[Sustain] = []
    current_event: str | None = None
    current_lines: list[str] = []
    mode = "header"

    def close() -> None:
        nonlocal current_event, current_lines
        if mode == "correction" and current_event is not None:
            corrections.append(
                Correction(current_event, MappingProxyType(_parse_fields(current_lines)))
            )
        elif mode == "sustain" and current_event is not None:
            sustains.append(
                Sustain(current_event, MappingProxyType(_parse_fields(current_lines)))
            )
        current_event, current_lines = None, []

    for line in lines:
        correction = CORRECTION_HEADING.match(line)
        sustain = SUSTAIN_HEADING.match(line)
        if correction:
            close()
            mode, current_event = "correction", correction.group("event")
        elif sustain:
            close()
            mode, current_event = "sustain", sustain.group("event")
        elif mode == "header":
            header.append(line)
        else:
            current_lines.append(line)
    close()
    fields = _parse_fields(header)
    return Review(
        path=path,
        fields=MappingProxyType(fields),
        corrections=tuple(corrections),
        sustains=tuple(sustains),
        corrections_none=fields.get("CORRECTIONS", "").casefold() == "none",
        sustains_none=fields.get("SUSTAINS", "").casefold() == "none",
    )


def _extract_metadata(path: Path) -> tuple[dict[str, str], set[str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read extract {path.name}") from exc
    fields = _parse_fields(lines[:8])
    identifiers = {
        line.partition(":")[2].strip()
        for line in lines
        if line.startswith("## ENTRY:")
    }
    return fields, identifiers


def _substance(value: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9]{3}", value))


def _baseline(run: Path, submission: str) -> dict[str, str | None]:
    try:
        payload = json.loads(baseline_path(run, submission).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("baseline is absent or unreadable") from exc
    if not isinstance(payload, dict):
        raise ValueError("baseline is not an object")
    return {str(key): value if isinstance(value, str) else None for key, value in payload.items()}


def _target_changed(target: str, baseline: Mapping[str, str | None]) -> bool:
    path = Path(target).expanduser().resolve()
    return _hash(path) is not None and _hash(path) != baseline.get(str(path))


def _tracked_diff_names() -> set[Path]:
    root = Path(__file__).resolve().parent.parent
    return {
        (root / path).resolve()
        for path in git_paths.read_path_records(
            root, "diff", "-z", "--name-only", "--", "."
        )
    }


def _successful_gh_call(transcripts: Iterable[Path]) -> bool:
    for transcript in transcripts:
        rows = read_transcript(transcript)
        tools = _tool_index(rows)
        gh_ids: set[str] = set()
        for row in rows:
            if row.get("type") != "assistant":
                continue
            for block in _content_blocks(row.get("message")):
                command = block.get("input", {}).get("command") if isinstance(block.get("input"), dict) else None
                if block.get("type") == "tool_use" and isinstance(command, str) and re.search(r"(?:^|[;&|]\s*)gh\s+", command):
                    gh_ids.add(_text(block.get("id")))
        for row in rows:
            if row.get("type") != "user":
                continue
            for block in _content_blocks(row.get("message")):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in gh_ids and block.get("is_error") is not True:
                    return True
        if any(tool == "Bash" for tool in tools.values()) and gh_ids:
            # Older transcript rows omit ``is_error`` on a successful result.
            continue
    return False


def survey(run: Path, submission: str) -> Scan:
    findings: list[Finding] = []
    record_path = review_path(run, submission)
    records = int(record_path.is_file())
    if not records:
        return Scan(submission, 0, 0, 0, 0, 0, len(orphan_paths(run)), (Finding("missing-review", submission),))
    try:
        review = read_review(record_path)
        extract_fields, identifiers = _extract_metadata(extract_path(run, submission))
        baseline = _baseline(run, submission)
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, len(orphan_paths(run)), (Finding("unscannable-review", str(exc)),))

    for field in HEADER_FIELDS:
        value = review.fields.get(field, "")
        present = bool(value.strip()) if field in {"POPULATION", "UNREAD"} else _substance(value)
        if not present:
            findings.append(Finding("missing-header-field", field))
    if review.fields.get("SUBMISSION") != submission:
        findings.append(Finding("wrong-submission", review.fields.get("SUBMISSION", "")))
    try:
        population = int(review.fields.get("POPULATION", ""))
        unread = int(review.fields.get("UNREAD", ""))
    except ValueError:
        population, unread = 0, -1
        findings.append(Finding("non-numeric-coverage", "POPULATION or UNREAD"))
    expected_population = len(identifiers)
    if population != expected_population or review.fields.get("POPULATION") != extract_fields.get("POPULATION"):
        findings.append(Finding("population-mismatch", f"record {population}; extract {expected_population}"))
    if unread != 0:
        findings.append(Finding("unread-candidates", str(unread)))
    if review.fields.get("WATERMARK") != extract_fields.get("WATERMARK") or review.fields.get("WATERMARK") not in identifiers:
        findings.append(Finding("watermark-mismatch", review.fields.get("WATERMARK", "")))
    if review.fields.get("TRANSCRIPTS") != extract_fields.get("TRANSCRIPTS"):
        findings.append(Finding("transcript-mismatch", review.fields.get("TRANSCRIPTS", "")))
    if not review.corrections and not review.corrections_none:
        findings.append(Finding("missing-correction-verdict", "neither records nor CORRECTIONS: none"))
    if review.corrections and review.corrections_none:
        findings.append(Finding("contradictory-correction-verdict", "records and CORRECTIONS: none"))
    if not review.sustains and not review.sustains_none:
        findings.append(Finding("missing-sustain-verdict", "neither records nor SUSTAINS: none"))
    if review.sustains and review.sustains_none:
        findings.append(Finding("contradictory-sustain-verdict", "records and SUSTAINS: none"))

    transcript_paths = [
        Path(value.strip())
        for value in extract_fields.get("TRANSCRIPT-PATHS", "").split("|")
        if value.strip()
    ]
    for pointer in orphan_paths(run):
        try:
            transcript_paths.append(_read_pointer(pointer)[0])
        except ValueError as exc:
            findings.append(Finding("bad-orphan-pointer", str(exc)))

    diff_names = _tracked_diff_names()
    for correction in review.corrections:
        if correction.event not in identifiers:
            findings.append(Finding("unknown-correction-event", correction.event))
        for field in CORRECTION_FIELDS:
            if not _substance(correction.fields.get(field, "")):
                findings.append(Finding("missing-correction-field", f"{correction.event}: {field}"))
        if correction.fields.get("CORRECTOR") not in CORRECTORS:
            findings.append(Finding("unknown-corrector", correction.fields.get("CORRECTOR", "")))
        if correction.fields.get("IN-ERROR") not in CORRECTORS:
            findings.append(Finding("unknown-error-party", correction.fields.get("IN-ERROR", "")))
        disposition = correction.fields.get("DISPOSITION", "")
        if disposition not in DISPOSITIONS:
            findings.append(Finding("unknown-disposition", disposition or correction.event))
            continue
        target = correction.fields.get("TARGET", "")
        landing = correction.fields.get("LANDING", "")
        if disposition in {"skill-file", "tracker-ticket"}:
            if not GH_ISSUE.fullmatch(landing):
                findings.append(Finding("unlanded-ticket", correction.event))
            elif transcript_paths and not _successful_gh_call(transcript_paths):
                findings.append(Finding("missing-gh-call", correction.event))
        elif disposition == "memory-write":
            if not _target_changed(target, baseline):
                findings.append(Finding("unlanded-memory", correction.event))
        elif disposition == "check":
            resolved = Path(target).expanduser().resolve()
            if resolved not in diff_names or not _target_changed(target, baseline):
                findings.append(Finding("unlanded-check", correction.event))

    for sustain in review.sustains:
        if sustain.event not in identifiers:
            findings.append(Finding("unknown-sustain-event", sustain.event))
        if not _substance(sustain.fields.get("SUMMARY", "")):
            findings.append(Finding("bare-sustain", sustain.event))
    orphaned = len(orphan_paths(run))
    return Scan(
        submission=submission,
        records=records,
        population=population,
        corrections=len(review.corrections),
        sustains=len(review.sustains),
        unread=unread,
        orphaned=orphaned,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = [
        f"after-action review over {source}",
        "",
        f"  review records                  {scan.records}",
        f"  candidate population            {scan.population}",
        f"  correction records              {scan.corrections}",
        f"  sustain records                 {scan.sustains}",
        f"  unread candidates               {scan.unread}",
        f"  orphaned sittings               {scan.orphaned}",
        f"  findings                        {len(scan.findings)}",
    ]
    if show and scan.findings:
        lines.extend(["", "  findings (private - read, do not paste):"])
        lines.extend(f"    {row.kind}: {row.detail}" for row in scan.findings)
    lines.extend(["", "  declared limits:"])
    lines.extend(f"    {subject}" for subject, _reason in DECLARED_LIMITS)
    return "\n".join(lines)


def completion_finding(run: Path, submissions: Iterable[str]) -> str | None:
    """The expected row shared by the six completion graders."""
    for submission in submissions:
        scan = survey(run, submission)
        if scan.findings or scan.unread or scan.orphaned:
            return f"{EXPECTED_ROW} is incomplete for {submission}"
    return None


def is_live_run(run: Path) -> bool:
    root = (repo_root.scratch_root() / "runs").resolve()
    try:
        return run.resolve().is_relative_to(root)
    except OSError:
        return False


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    """Grade the shared expected row only for an explicitly terminal submission."""
    if submission is None:
        return False, f"{EXPECTED_ROW}: {NOT_GRADED} - --submission was not supplied"
    finding = completion_finding(run, (submission,))
    return (finding is not None, f"{EXPECTED_ROW}: {'finding - ' + finding if finding else 'clean'}")


def consume_orphans(run: Path) -> None:
    for path in orphan_paths(run):
        path.unlink()


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _strings(nested)


def _attributed_scoped(rows: Iterable[dict[str, Any]]) -> bool:
    return any(row.get("attributionSkill") in SCOPED_SKILLS for row in rows)


def discover_run_directories(rows: Iterable[dict[str, Any]]) -> tuple[Path, ...]:
    root = repo_root.scratch_root() / "runs"
    found: set[Path] = set()
    for row in rows:
        if row.get("type") != "assistant":
            continue
        for block in _content_blocks(row.get("message")):
            if block.get("type") != "tool_use":
                continue
            for value in _strings(block.get("input")):
                for match in RUN_REFERENCE.finditer(value):
                    candidate = (root / match.group("key")).resolve()
                    if candidate.is_dir() and candidate.is_relative_to(root.resolve()):
                        found.add(candidate)
    return tuple(sorted(found))


def locate_transcript(run: Path) -> Path:
    """The newest main transcript that names this existing run directory."""
    root = Path.home() / ".claude" / "projects"
    candidates: list[Path] = []
    for path in sorted(root.rglob("*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True):
        if path.parent.name == "subagents":
            continue
        try:
            rows = read_transcript(path)
        except ValueError:
            continue
        if _attributed_scoped(rows) and run in discover_run_directories(rows):
            candidates.append(path)
            break
    if not candidates:
        raise ValueError("no current scoped transcript names this run directory")
    return candidates[0]


def session_end(payload: Mapping[str, Any]) -> int:
    if payload.get("hook_event_name") != "SessionEnd":
        return 2
    if payload.get("agent_id") is not None:
        return 0
    transcript_value = payload.get("transcript_path")
    session_id = payload.get("session_id")
    if not isinstance(transcript_value, str) or not isinstance(session_id, str):
        return 2
    transcript = Path(transcript_value)
    rows = read_transcript(transcript)
    if not _attributed_scoped(rows):
        return 0
    for run in discover_run_directories(rows):
        drained = False
        if (run / "aar").is_dir():
            for path in (run / "aar").glob("*.md"):
                if path.name.endswith(".extract.md"):
                    continue
                try:
                    review = read_review(path)
                    submission = review.fields.get("SUBMISSION", "")
                    scan = survey(run, submission)
                except ValueError:
                    continue
                drained = (
                    review.fields.get("TRANSCRIPTS", "").split(",")[-1].strip()
                    == transcript.stem
                    and not scan.findings
                    and scan.unread == 0
                    and scan.orphaned == 0
                )
                if drained:
                    break
        if drained:
            continue
        destination = run / "aar" / f"orphaned-{_safe_submission(session_id)}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {"transcript_path": str(transcript.resolve()), "run_key": run.name},
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    return 0


USAGE = (
    "usage: aar_scan.py <run-directory> --submission <key> "
    "[--transcript <jsonl> --memory-index <path> --extract] [--show]"
)


def validate(parsed: run_grader.Parsed) -> str | None:
    if not parsed.value("--submission"):
        return "--submission is required"
    if parsed.enabled("--extract") and not parsed.value("--memory-index"):
        return "--extract requires --memory-index"
    return None


def load(parsed: run_grader.Parsed) -> Path:
    run = Path(parsed.source).expanduser().resolve()
    if not run.is_dir():
        raise run_grader.SourceError(f"no directory named {run.name}")
    return run


def grade(run: Path, parsed: run_grader.Parsed) -> run_grader.Grade[Scan] | run_grader.EarlyExit:
    submission = parsed.value("--submission")
    assert submission is not None  # validate owns this invocation requirement
    if parsed.enabled("--extract"):
        transcript_value = parsed.value("--transcript")
        memory_value = parsed.value("--memory-index")
        assert memory_value is not None  # validate owns this invocation requirement
        try:
            transcript = (
                Path(transcript_value).expanduser().resolve()
                if transcript_value
                else locate_transcript(run)
            )
            destination, count = write_extract(
                run, transcript, submission, Path(memory_value).expanduser().resolve()
            )
        except (OSError, ValueError, subprocess.SubprocessError, git_paths.GitPathError) as exc:
            return run_grader.EarlyExit(
                2,
                stderr=(f"after-action review NOT SCANNED: {exc}",),
            )
        return run_grader.EarlyExit(
            0,
            stdout=(
                f"after-action review extract over {run.name}",
                f"  candidate population            {count}",
                f"  private extract written         {destination.name}",
            ),
        )

    scan = survey(run, submission)
    return run_grader.Grade(
        scan=scan,
        source=run.name,
        findings_failed=bool(scan.findings),
    )


# No exit_2_limbs: the exact SessionEnd branch below has two exit-2 routes
# outside the runner. A partial vocabulary would claim the whole command
# surface. The hook is not a reader in the grader family (ADR 0117).
GRADER = run_grader.Grader(
    usage=USAGE,
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--show"),
        run_grader.Option(
            "--submission", takes_value=True, missing_value="--submission needs a key"
        ),
        run_grader.Option("--transcript", takes_value=True),
        run_grader.Option("--memory-index", takes_value=True),
        run_grader.Option("--extract"),
    ),
    validate=validate,
    source_error_to_stdout=False,
    allow_extra_positionals=True,
)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--session-end"]:
        try:
            payload = json.load(sys.stdin)
            return session_end(payload)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            return 2
    status = run_grader.run(GRADER, arguments)
    if status == 0:
        # Re-parse only arguments the runner already accepted. Keeping this
        # post-report preserves the recoverable failure direction ruled in
        # ADR 0117: a crash cannot erase both the pointer and its report.
        parsed = run_grader.parse(GRADER, arguments)
        if not parsed.enabled("--extract"):
            consume_orphans(Path(parsed.source).expanduser().resolve())
    return status


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
