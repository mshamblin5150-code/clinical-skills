#!/usr/bin/env python3
"""Write and grade the canonical voice-model identity for coursework runs.

``DECLARED_LIMITS`` is the complete ceiling of what a clean identity row can
establish. Scoped graders and ``CLAUDE.md`` point here and copy no row.
"""

from __future__ import annotations

import completion_checks
import json
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import TypeVar

import coursework_run
import project_context
import aar_scan
import repo_root
import run_grader
import voice_model_scan
from console_codec import require_python_floor, use_utf8
from run_record_reader import read_tool_record, UnreadableRecord, RecordContentError, fault_report, object_record


RECORD_NAME = "voice-model-identity.json"
EXPECTED_ROW = "the canonical voice model identity"
SCOPED_SKILLS = frozenset(
    {
        "course-assignment",
        "discussion-post",
        "discussion-reply",
        "peer-critique",
        "practicum-case-study",
    }
)
COMPLETION_GRADERS = MappingProxyType(
    {skill: aar_scan.COMPLETION_GRADERS[skill] for skill in SCOPED_SKILLS}
)
DECLARED_LIMITS = (
    ("unreadable-tool-record", "An existing unreadable identity record is never a missing identity or draft observation; dependent checks are not graded and completion has incomplete coverage. Writers refuse without replacing it."),
    (
        "retrieval-before-draft-unobservable",
        "The historical first observation cannot see a draft deleted or moved before the gate, "
        "prose at other locations, or conversation prose saved only after the gates. "
        "Order waivers depend on the confirmed project-context header through its public reader.",
    ),
    (
        "resolution-is-not-use",
        "a true canonical resolution record does not establish which source the draft used",
    ),
    (
        "use-is-not-voice",
        "using the canonical model does not establish that the draft sounds like its clinician",
    ),
)
_RECORD_KEYS = frozenset({"path", "sha256", "exists"})
_SHA256 = re.compile(r"[0-9a-f]{64}")
TScan = TypeVar("TScan")


@dataclass(frozen=True)
class CompletionGate:
    finding: bool
    coverage: bool
    report: str


def write_record(run: Path, submission: str | None = None) -> str:
    """Resolve once and write that resolution into ``run`` at draft time."""
    observations = {}
    walk_reports = []
    previous = read_tool_record(run / RECORD_NAME, _decode_record)
    if submission is not None:
        keys = coursework_run.submission_keys(submission)
        if len(keys) != 1:
            raise ValueError("write one submission observation at a time")
        if not (coursework_run.voice_records_directory(run, submission) / "supplied-voice.json").is_file():
            raise ValueError("supplied-voice.json is required before the identity gate")
        if previous is not None:
            observations = previous.get("observations", {})
        observations = coursework_run.observe_draft(run, submission, observations, reports=walk_reports)
    resolved = repo_root.canonical_voice_model()
    payload = {
        "path": str(resolved.path),
        "sha256": resolved.sha256,
        "exists": resolved.exists,
    }
    if submission is not None:
        payload["observations"] = observations
    (run / RECORD_NAME).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    if not resolved.exists:
        report = voice_model_scan.absent_model_banner(resolved.path)
    else:
        report = f"voice model identity: recorded {resolved.path}"
    return "\n".join((report, *walk_reports))


def _valid_record(payload: object) -> bool:
    if not isinstance(payload, dict) or frozenset(payload) not in {_RECORD_KEYS, _RECORD_KEYS | {"observations"}}:
        return False
    try:
        coursework_run.validate_observations(payload.get("observations", {}))
    except ValueError:
        return False
    path = payload.get("path")
    digest = payload.get("sha256")
    exists = payload.get("exists")
    if not isinstance(path, str) or not path or not isinstance(exists, bool):
        return False
    if exists:
        return isinstance(digest, str) and _SHA256.fullmatch(digest) is not None
    return digest is None


def _decode_record(text: str) -> dict:
    payload = object_record(text)
    if not _valid_record(payload):
        raise ValueError("invalid identity record")
    return payload


def _identity_completion_gate(run: Path, submission: str | None) -> CompletionGate:
    """Grade the draft-time identity record when a terminal submission is named."""
    if submission is None:
        return CompletionGate(
            finding=False,
            coverage=False,
            report=f"{EXPECTED_ROW}: not graded - --submission was not supplied",
        )

    record = run / RECORD_NAME
    try:
        payload = read_tool_record(record, _decode_record)
    except UnreadableRecord as failure:
        return CompletionGate(False, True, fault_report(failure, check=EXPECTED_ROW))
    if payload is None:
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record is missing")

    try:
        resolved = repo_root.canonical_voice_model()
    except (OSError, UnicodeError):
        return CompletionGate(
            finding=False,
            coverage=True,
            report=f"{EXPECTED_ROW}: not scanned - canonical model identity is unreadable",
        )
    declared_path = Path(payload["path"]).expanduser().resolve()
    wrong_path = declared_path != resolved.path.resolve()
    moved = payload["sha256"] != resolved.sha256 or payload["exists"] != resolved.exists
    states = []
    if wrong_path:
        states.append("finding - declared path is not canonical")
    if moved:
        states.append("not scanned - canonical digest moved")
    return CompletionGate(
        finding=wrong_path,
        coverage=moved,
        report=f"{EXPECTED_ROW}: " + ("; ".join(states) if states else "clean"),
    )


def completion_gate(run: Path, submission: str | None) -> CompletionGate:
    frozen = completion_checks.exemption(run, submission, "voice_model_identity", EXPECTED_ROW)
    if frozen is not None:
        return CompletionGate(False, False, frozen)
    result = _identity_completion_gate(run, submission)
    if submission is None:
        return result
    try:
        payload = read_tool_record(run / RECORD_NAME, _decode_record)
        observations = payload.get("observations") if payload is not None else None
    except UnreadableRecord as failure:
        return CompletionGate(False, True, fault_report(failure, check=EXPECTED_ROW) + "; draft order: not graded - identity record unreadable")
    try:
        order = coursework_run.grade_order(observations, submission, lambda key, path: project_context.order_waived(run, key, path), run=run)
    except UnreadableRecord as failure:
        return replace(result, coverage=True, report=result.report + "; " + fault_report(failure, check="draft order"))
    except RecordContentError as failure:
        return replace(result, finding=True, report=result.report + "; " + str(failure))
    return replace(result, finding=result.finding or order.finding, report=result.report + "; " + order.report)


def apply_completion_gate(
    grade: run_grader.Grade[TScan],
    run: Path,
    submission: str | None,
    *,
    coverage_limb: str | None = None,
) -> run_grader.Grade[TScan]:
    """Add the shared row to one already-computed completion grade."""
    identity = completion_gate(run, submission)
    limbs = grade.coverage_limbs
    if identity.coverage and coverage_limb is not None:
        limbs += (coverage_limb,)
    return replace(
        grade,
        findings_failed=grade.findings_failed or identity.finding,
        coverage_failed=grade.coverage_failed or identity.coverage,
        coverage_limbs=limbs,
        reports=grade.reports + (identity.report,),
    )


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] != "--write" or argv[2] != "--submission":
        print(
            "usage: python tools/voice_model_identity.py <run-directory> --write --submission <key>",
            file=sys.stderr,
        )
        return 2
    run = Path(argv[0]).expanduser().resolve()
    if not run.is_dir():
        print(f"voice model identity NOT WRITTEN -- no run directory at {run}", file=sys.stderr)
        return 2
    try:
        submission = argv[3]
        print(write_record(run, submission))
        order = coursework_run.grade_order(
            read_tool_record(run / RECORD_NAME, _decode_record)["observations"],
            submission, lambda key, path: project_context.order_waived(run, key, path),
        )
        print(order.report)
        if order.finding:
            return 1
    except RecordContentError as failure:
        print(str(failure), file=sys.stderr)
        return 1
    except UnreadableRecord as failure:
        print(fault_report(failure, check=EXPECTED_ROW), file=sys.stderr)
        return 2
    except coursework_run.DraftWalkUnreadable as failure:
        print(f"voice model identity NOT WRITTEN -- {failure}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError) as failure:
        print(f"voice model identity NOT WRITTEN -- {failure}", file=sys.stderr)
        return 1 if isinstance(failure, ValueError) else 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
