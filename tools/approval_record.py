"""Durable per-item approval records for skills that post graded content. #1421."""

from __future__ import annotations

from discussion_artifact import check_posted_reading

from dataclasses import dataclass, replace
from enum import Enum
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from typing import Iterable

import aar_scan
import entry_copy
from discussion_artifact import read_posted_readings
import run_grader


class ApprovalRecordError(ValueError):
    pass


RECORD = "posting-approvals.json"
MODULE_ROOT = Path(__file__).resolve().parent.parent
SKILLS = frozenset(
    {
        "batch-shift",
        "clinical-note",
        "discussion-post",
        "discussion-reply",
        "peer-critique",
        "practicum-case-study",
    }
)

REPLY_UNREADABLE = "approval reply transcript unreadable"


@dataclass(frozen=True)
class ReplyVerification:
    state: str
    reason: str
    matched_at: float | None = None


def verify_clinician_reply(
    run: Path, reply: str, sources: tuple[Path, ...], *, after: float | None = None,
    source_modified_at: float | None = None,
) -> ReplyVerification:
    """Match a whole human message after the sources and the preceding approval."""

    normalized = " ".join(reply.split())
    if not normalized:
        return ReplyVerification("not found", "the whole clinician reply is missing")
    try:
        boundary = (max(path.stat().st_mtime for path in sources)
                    if source_modified_at is None else source_modified_at)
        if after is not None:
            boundary = max(boundary, after)
        discovery = aar_scan.discover_transcripts(run)
    except (OSError, ValueError):
        return ReplyVerification("unreadable", "transcript discovery or source time unavailable")
    unread = bool(discovery.unread)
    matches: list[float] = []
    for path in discovery.paths:
        if "subagents" in {part.casefold() for part in path.parts}:
            continue
        try:
            rows = aar_scan.read_transcript(path)
        except (OSError, ValueError):
            unread = True
            continue
        if aar_scan._is_codex_subagent(rows):
            continue
        for row in rows:
            value = aar_scan.clinician_text(row)
            if " ".join(value.split()) != normalized:
                continue
            try:
                timestamp = datetime.fromisoformat(str(row.get("timestamp", "")).replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("timestamp has no timezone")
                written_at = timestamp.astimezone(timezone.utc).timestamp()
            except (ValueError, OverflowError):
                unread = True
                continue
            if written_at > boundary:
                matches.append(written_at)
    if matches:
        return ReplyVerification("verified", "whole clinician message matched", min(matches))
    if unread or not discovery.paths:
        return ReplyVerification("unreadable", "no complete readable transcript population")
    return ReplyVerification("not found", "no later whole clinician message matches")


def _without_reply(report: str, reply: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in reply.split())
    return re.sub(pattern, "[clinician reply withheld]", report) if pattern else report


@dataclass(frozen=True)
class CompletionResult:
    finding: bool
    report: str
    coverage: bool = False

    def __iter__(self):
        # Preserve the established two-value completion-gate interface.
        yield self.finding
        yield self.report


def _recheck_replies(
    run: Path, approvals: list[dict[str, object]], sources: tuple[Path, ...],
) -> ReplyVerification:
    after = None
    unread = False
    for approval in approvals:
        matched_at = approval.get("reply_matched_at")
        if approval.get("reply_verification") == "not verified":
            reply = approval.get("clinician_reply")
            if not isinstance(reply, str) or not reply.strip():
                return ReplyVerification("not found", "recorded whole reply is missing")
            result = verify_clinician_reply(
                run, reply, sources, after=after,
                source_modified_at=approval.get("source_modified_at"),
            )
            if result.state == "not found":
                return result
            if result.state == "unreadable":
                unread = True
            matched_at = result.matched_at
        if isinstance(matched_at, (float, int)):
            after = max(after or matched_at, matched_at)
    if unread:
        return ReplyVerification("unreadable", "a preceding approval transcript is unreadable")
    return ReplyVerification("verified", "approval replies checked", after)


class PostingRoute(str, Enum):
    AWAITING = "awaiting-posting"
    AGENT = "agent"
    CLINICIAN = "clinician"


@dataclass(frozen=True)
class ApprovalRecord:
    run: Path
    skill: str
    submission: str
    sha256: str
    sources: tuple[Path, ...]
    grader_args: tuple[str, ...]
    pregrade_report: str
    approval_revision: int


def source_sha256(paths: Iterable[Path]) -> str:
    """Hash one ordered source population exactly as its posted reading does."""

    digest = sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _write(path: Path, payload: dict[str, object]) -> None:
    # Keep this evidence writer local: its record validation and recovery contract must
    # evolve independently of course-assignment's differently shaped submission gates.
    partial = path.with_name(f"{path.name}.{os.getpid()}.building")
    partial.unlink(missing_ok=True)
    try:
        partial.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(partial, path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def _read(run: Path, *, missing_ok: bool = False) -> dict[str, object]:
    path = run / RECORD
    if missing_ok and not path.exists():
        return {"version": 1, "approval_revision": 0, "items": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as failure:
        raise ApprovalRecordError(f"could not read durable approval records: {failure}") from failure
    if not isinstance(value, dict) or not isinstance(value.get("items"), list):
        raise ApprovalRecordError("durable approval records must contain one items list")
    return value


def _grader_path(skill: str) -> Path:
    if skill not in SKILLS:
        raise ApprovalRecordError(f"unsupported posting skill: {skill}")
    return MODULE_ROOT / "tools" / f"{aar_scan.COMPLETION_GRADERS[skill]}.py"


def _pre_post_grade(skill: str, grader_args: tuple[str, ...]) -> tuple[int, str]:
    _preflight_grader(skill, grader_args)
    completed = subprocess.run(
        [sys.executable, str(_grader_path(skill)), *grader_args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    report = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    return completed.returncode, report or f"grader exited {completed.returncode}"


def _preflight_grader(skill: str, grader_args: tuple[str, ...]) -> None:
    """Refuse invocation and source errors before accepting exit 2 as coverage."""

    module_name = aar_scan.COMPLETION_GRADERS.get(skill)
    if module_name is None:
        raise ApprovalRecordError(f"unsupported posting skill: {skill}")
    module = importlib.import_module(module_name)
    grader = getattr(module, "GRADER", None)
    if not isinstance(grader, run_grader.Grader):
        raise ApprovalRecordError(f"{skill}'s paired grader is unavailable")
    try:
        parsed = run_grader.parse(grader, list(grader_args))
        grader.load(parsed)
    except (run_grader.ParseError, run_grader.SourceError) as failure:
        raise ApprovalRecordError(
            f"the pre-post grader invocation is invalid: {failure}"
        ) from failure


def approve(
    run: Path,
    *,
    skill: str,
    submission: str,
    sources: tuple[Path, ...],
    grader_args: tuple[str, ...],
    content_approved: bool,
    clinician_reply: str,
) -> ApprovalRecord:
    """Record one content go-ahead after its paired pre-post grader finds nothing."""

    root = Path(run).resolve()
    if not content_approved:
        raise ApprovalRecordError("content approval is required")
    if not isinstance(clinician_reply, str) or not clinician_reply.strip():
        raise ApprovalRecordError("approval needs the whole clinician reply")
    if not root.is_dir():
        raise ApprovalRecordError("approval record needs an existing run directory")
    if not submission.strip():
        raise ApprovalRecordError("approval record needs a submission key")
    if "--submission" in grader_args:
        raise ApprovalRecordError("the pre-post grader must not receive --submission")
    resolved_sources = tuple(Path(path).resolve() for path in sources)
    if not resolved_sources or any(not path.is_file() for path in resolved_sources):
        raise ApprovalRecordError("approval record needs a nonempty readable source population")
    if skill in {"batch-shift", "clinical-note"}:
        for source in resolved_sources:
            try:
                entry_copy.check(source.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, ValueError) as failure:
                raise ApprovalRecordError(_without_reply(
                    f"Entry copy refused: {source}: {failure}", clinician_reply,
                )) from failure
    payload = _read(root, missing_ok=True)
    previous = _matching_item(payload, skill, submission)
    history = list(previous.get("approvals", [])) if previous else []
    if previous and "clinician_reply" in previous and not history:
        history.append({name: previous[name] for name in (
            "clinician_reply", "reply_verification", "reply_reason", "reply_matched_at",
            "reply_after", "approval_revision", "source_modified_at",
        ) if name in previous})
    # Resolve pending earlier gates before accepting a later reply. Otherwise an
    # unreadable Gate 1 could be matched to Gate 2's message at completion.
    preceding = _recheck_replies(root, history, resolved_sources)
    if preceding.state == "not found":
        raise ApprovalRecordError("a preceding approval reply was not found")
    after = preceding.matched_at
    verification = verify_clinician_reply(root, clinician_reply, resolved_sources, after=after)
    if verification.state == "not found":
        raise ApprovalRecordError("the clinician approval reply was not found: " + verification.reason)
    if preceding.state == "unreadable":
        verification = preceding
    grade_status, grade_report = _pre_post_grade(skill, grader_args)
    for reply in (clinician_reply, *(row["clinician_reply"] for row in history)):
        grade_report = _without_reply(grade_report, reply)
    if grade_status not in {0, 2}:
        raise ApprovalRecordError(f"the pre-post grade has a finding: {grade_report}")

    previous_revision = payload.get("approval_revision", 0)
    revision = previous_revision + 1 if isinstance(previous_revision, int) else 1
    digest = source_sha256(resolved_sources)
    item = {
        "skill": skill,
        "submission": submission,
        "sha256": digest,
        "sources": [str(path) for path in resolved_sources],
        "grader_args": list(grader_args),
        "posting_route": PostingRoute.AWAITING.value,
        "approval_revision": revision,
        "pregrade_status": "clean" if grade_status == 0 else "incomplete",
        "clinician_reply": clinician_reply,
        "reply_verification": "verified" if verification.state == "verified" else "not verified",
        "reply_reason": verification.reason,
        "reply_matched_at": verification.matched_at,
        "reply_after": after,
        "source_modified_at": max(path.stat().st_mtime for path in resolved_sources),
    }
    history.append({name: item[name] for name in (
        "clinician_reply", "reply_verification", "reply_reason", "reply_matched_at",
        "reply_after", "approval_revision", "source_modified_at",
    )})
    item["approvals"] = history
    current_items = payload.get("items", [])
    items = [
        current
        for current in current_items
        if isinstance(current, dict)
        and (current.get("skill"), current.get("submission")) != (skill, submission)
    ]
    items.append(item)
    _write(
        root / RECORD,
        {"version": 1, "approval_revision": revision, "items": items},
    )
    return ApprovalRecord(
        root,
        skill,
        submission,
        digest,
        resolved_sources,
        grader_args,
        grade_report,
        revision,
    )


def _matching_item(
    payload: dict[str, object], skill: str, submission: str
) -> dict[str, object] | None:
    items = payload.get("items")
    if not isinstance(items, list):
        return None
    matches = tuple(
        item
        for item in items
        if isinstance(item, dict)
        and item.get("skill") == skill
        and item.get("submission") == submission
    )
    return matches[0] if len(matches) == 1 else None


def _record_posting(
    run: Path, *, skill: str, submission: str, route: PostingRoute
) -> None:
    root = Path(run).resolve()
    payload = _read(root)
    item = _matching_item(payload, skill, submission)
    if item is None:
        raise ApprovalRecordError("a posting needs an approval record")
    sources = item.get("sources")
    expected = item.get("sha256")
    if not isinstance(sources, list) or not all(isinstance(path, str) for path in sources):
        raise ApprovalRecordError("the recorded source population is unreadable")
    paths = tuple(Path(path) for path in sources)
    try:
        current = source_sha256(paths)
    except OSError as failure:
        raise ApprovalRecordError("the approved source population is unreadable") from failure
    if current != expected:
        raise ApprovalRecordError("the approved source population changed after approval")
    item["posting_route"] = route.value
    _write(root / RECORD, payload)


def record_agent_posting(run: Path, *, skill: str, submission: str) -> None:
    """Record the run's posting of one unchanged approved item."""

    _record_posting(run, skill=skill, submission=submission, route=PostingRoute.AGENT)


def record_clinician_posting(run: Path, *, skill: str, submission: str) -> None:
    """Record a clinician posting in place of the run's own posting confirmation."""

    _record_posting(
        run, skill=skill, submission=submission, route=PostingRoute.CLINICIAN
    )


def completion_gate(
    run: Path, skill: str, submission: str | None
) -> tuple[bool, str] | CompletionResult:
    """Join approved bytes to the posted reading for every requested item."""

    label = "the approval record"
    if submission is None:
        return False, f"{label}: NOT GRADED - --submission was not supplied"
    keys = tuple(value.strip() for value in submission.split(",") if value.strip())
    if not keys:
        return True, f"{label}: finding - no submission key was supplied"
    root = Path(run).resolve()
    try:
        payload = _read(root)
        readings = read_posted_readings((root / "reread.md").read_text(encoding="utf-8"))
    except (ApprovalRecordError, OSError, UnicodeError, ValueError) as failure:
        return True, f"{label}: finding - could not read approval and posted-reading evidence: {failure}"
    by_submission = {reading.artifact: reading for reading in readings}
    incomplete = False
    for key in keys:
        item = _matching_item(payload, skill, key)
        if item is None:
            return True, f"{label}: finding - {key} has no recorded content approval"
        if item.get("posting_route") not in {
            PostingRoute.AGENT.value,
            PostingRoute.CLINICIAN.value,
        }:
            return True, f"{label}: finding - {key} has no recorded posting route"
        sources = item.get("sources")
        expected = item.get("sha256")
        if (
            not isinstance(expected, str)
            or not isinstance(sources, list)
            or not all(isinstance(path, str) for path in sources)
        ):
            return True, f"{label}: finding - {key} has an unreadable approval record"
        try:
            current = source_sha256(tuple(Path(path) for path in sources))
        except OSError:
            return True, f"{label}: finding - {key}'s approved source population is unreadable"
        if current != expected:
            return True, f"{label}: finding - {key}'s approved source fingerprint changed"
        if "reply_verification" in item:
            approvals = item.get("approvals", [item])
            if not isinstance(approvals, list) or not all(isinstance(row, dict) for row in approvals):
                return True, f"{label}: finding - unreadable approval reply history"
            result = _recheck_replies(root, approvals, tuple(Path(path) for path in sources))
            if result.state == "not found":
                return True, f"{label}: finding - a whole clinician reply was not found"
            incomplete = incomplete or result.state == "unreadable"
        reading = by_submission.get(key)
        outcomes = check_posted_reading(reading, expected)
        if outcomes:
            return True, f"{label}: finding - {outcomes[0].message}"
    if incomplete:
        return CompletionResult(False, f"{label}: incomplete coverage - {REPLY_UNREADABLE}", True)
    return False, f"{label}: clean"


def apply_completion_gate(
    grade: run_grader.Grade[object],
    run: Path,
    skill: str,
    submission: str | None,
) -> run_grader.Grade[object]:
    """Add the approval-to-posted-reading join to one skill's terminal grade."""

    result = completion_gate(run, skill, submission)
    failed, report = result
    incomplete = getattr(result, "coverage", False)
    return replace(
        grade,
        findings_failed=grade.findings_failed or failed,
        coverage_failed=grade.coverage_failed or incomplete,
        coverage_limbs=grade.coverage_limbs + ((REPLY_UNREADABLE,) if incomplete else ()),
        reports=(*grade.reports, report),
    )
