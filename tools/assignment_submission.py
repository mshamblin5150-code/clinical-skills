"""Durable authorization state for the course-assignment DOCX upload gates."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import file_digest


class GateError(ValueError):
    pass


RECORD = "submission-gates.json"


@dataclass(frozen=True)
class StagedUpload:
    run: Path
    artifact: Path
    sha256: str


def _write(record: Path, payload: dict[str, object]) -> None:
    partial = record.with_name(f"{record.name}.{os.getpid()}.building")
    partial.unlink(missing_ok=True)
    try:
        partial.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(partial, record)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def _read(run: Path) -> dict[str, object]:
    try:
        value = json.loads((run / RECORD).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as failure:
        raise GateError(f"could not read durable submission gates: {failure}") from failure
    if not isinstance(value, dict):
        raise GateError("durable submission gates must be one object")
    return value


def stage(run: Path, artifact: Path, *, artifact_approved: bool) -> StagedUpload:
    """Persist Gate 1 for the exact DOCX selected for Canvas staging."""

    root = Path(run).resolve()
    path = Path(artifact).resolve()
    if not artifact_approved:
        raise GateError("artifact approval is required before staging")
    if not root.is_dir():
        raise GateError("Gate 1 needs an existing run directory")
    if not path.is_file() or path.suffix.casefold() != ".docx":
        raise GateError("Gate 1 may stage only an existing DOCX")
    digest = file_digest.sha256(path)
    _write(
        root / RECORD,
        {
            "artifact": path.name,
            "sha256": digest,
            "gate1_approved": True,
            "gate2_confirmed": False,
        },
    )
    return StagedUpload(root, path, digest)


def confirm(staged: StagedUpload, *, final_confirmation: bool) -> None:
    """Persist Gate 2 only for the unchanged artifact bound by Gate 1."""

    if not final_confirmation:
        raise GateError("final confirmation is required for Gate 2")
    if not staged.artifact.is_file() or file_digest.sha256(staged.artifact) != staged.sha256:
        raise GateError("the staged DOCX changed after Gate 1")
    payload = _read(staged.run)
    if payload.get("artifact") != staged.artifact.name or payload.get("sha256") != staged.sha256:
        raise GateError("the durable Gate 1 record names another artifact")
    payload["gate2_confirmed"] = True
    _write(staged.run / RECORD, payload)


def submit_is_authorized(staged: StagedUpload) -> bool:
    """Whether durable Gate 2 permits the Submit Assignment click right now."""

    try:
        payload = _read(staged.run)
        return bool(
            payload.get("gate1_approved") is True
            and payload.get("gate2_confirmed") is True
            and payload.get("artifact") == staged.artifact.name
            and payload.get("sha256") == staged.sha256
            and staged.artifact.is_file()
            and file_digest.sha256(staged.artifact) == staged.sha256
        )
    except (GateError, OSError):
        return False


def completion_gate(run: Path, artifact: Path) -> tuple[bool, str]:
    """Grade both durable approvals against the canonical DOCX bytes."""

    path = Path(artifact).resolve()
    try:
        payload = _read(Path(run).resolve())
        clean = bool(
            payload.get("gate1_approved") is True
            and payload.get("gate2_confirmed") is True
            and payload.get("artifact") == path.name
            and path.is_file()
            and payload.get("sha256") == file_digest.sha256(path)
        )
    except (GateError, OSError):
        clean = False
    return not clean, "submission gates: clean" if clean else "submission gates: not clean"
