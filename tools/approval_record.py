"""Durable per-item approval records for skills that post graded content. #1421."""

from __future__ import annotations

from discussion_artifact import check_posted_reading

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable

import aar_scan
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
) -> ApprovalRecord:
    """Record one content go-ahead after its paired pre-post grader finds nothing."""

    root = Path(run).resolve()
    if not content_approved:
        raise ApprovalRecordError("content approval is required")
    if not root.is_dir():
        raise ApprovalRecordError("approval record needs an existing run directory")
    if not submission.strip():
        raise ApprovalRecordError("approval record needs a submission key")
    if "--submission" in grader_args:
        raise ApprovalRecordError("the pre-post grader must not receive --submission")
    resolved_sources = tuple(Path(path).resolve() for path in sources)
    if not resolved_sources or any(not path.is_file() for path in resolved_sources):
        raise ApprovalRecordError("approval record needs a nonempty readable source population")
    grade_status, grade_report = _pre_post_grade(skill, grader_args)
    if grade_status not in {0, 2}:
        raise ApprovalRecordError(f"the pre-post grade has a finding: {grade_report}")

    payload = _read(root, missing_ok=True)
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
    }
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
) -> tuple[bool, str]:
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
        reading = by_submission.get(key)
        outcomes = check_posted_reading(reading, expected)
        if outcomes:
            return True, f"{label}: finding - {outcomes[0].message}"
    return False, f"{label}: clean"


def apply_completion_gate(
    grade: run_grader.Grade[object],
    run: Path,
    skill: str,
    submission: str | None,
) -> run_grader.Grade[object]:
    """Add the approval-to-posted-reading join to one skill's terminal grade."""

    failed, report = completion_gate(run, skill, submission)
    return replace(
        grade,
        findings_failed=grade.findings_failed or failed,
        reports=(*grade.reports, report),
    )
