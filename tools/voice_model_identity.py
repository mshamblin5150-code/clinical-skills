#!/usr/bin/env python3
"""Write and grade the canonical voice-model identity for coursework runs.

``DECLARED_LIMITS`` is the complete ceiling of what a clean identity row can
establish. Scoped graders and ``CLAUDE.md`` point here and copy no row.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import TypeVar

import aar_scan
import repo_root
import run_grader
import voice_model_scan
from console_codec import require_python_floor, use_utf8


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


def write_record(run: Path) -> str:
    """Resolve once and write that resolution into ``run`` at draft time."""
    resolved = repo_root.canonical_voice_model()
    payload = {
        "path": str(resolved.path),
        "sha256": resolved.sha256,
        "exists": resolved.exists,
    }
    (run / RECORD_NAME).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    if not resolved.exists:
        return voice_model_scan.absent_model_banner(resolved.path)
    return f"voice model identity: recorded {resolved.path}"


def _valid_record(payload: object) -> bool:
    if not isinstance(payload, dict) or frozenset(payload) != _RECORD_KEYS:
        return False
    path = payload.get("path")
    digest = payload.get("sha256")
    exists = payload.get("exists")
    if not isinstance(path, str) or not path or not isinstance(exists, bool):
        return False
    if exists:
        return isinstance(digest, str) and _SHA256.fullmatch(digest) is not None
    return digest is None


def completion_gate(run: Path, submission: str | None) -> CompletionGate:
    """Grade the draft-time identity record when a terminal submission is named."""
    if submission is None:
        return CompletionGate(
            finding=False,
            coverage=False,
            report=f"{EXPECTED_ROW}: not graded - --submission was not supplied",
        )

    record = run / RECORD_NAME
    if not record.is_file():
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record is missing")
    try:
        payload = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record shape is invalid")
    if not _valid_record(payload):
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record shape is invalid")

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
    if len(argv) != 2 or argv[1] != "--write":
        print(
            "usage: python tools/voice_model_identity.py <run-directory> --write",
            file=sys.stderr,
        )
        return 2
    run = Path(argv[0]).expanduser().resolve()
    if not run.is_dir():
        print(f"voice model identity NOT WRITTEN -- no run directory at {run}", file=sys.stderr)
        return 2
    try:
        print(write_record(run))
    except (OSError, UnicodeError) as failure:
        print(f"voice model identity NOT WRITTEN -- {failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
