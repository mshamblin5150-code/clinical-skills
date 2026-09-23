"""Durable authorization state for course-assignment upload carriers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import file_digest
import repo_root
from discussion_artifact import read_posted_readings


class GateError(ValueError):
    pass


RECORD = "submission-gates.json"


@dataclass(frozen=True)
class Carrier:
    path: Path
    name: str
    sha256: str


@dataclass(frozen=True)
class StagedUpload:
    run: Path
    artifact: Path
    sha256: str
    carriers: tuple[Carrier, ...]


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


def _carrier(path: Path) -> Carrier:
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise GateError(f"approved carrier does not exist: {resolved.name}")
    return Carrier(resolved, resolved.name, file_digest.sha256(resolved))


def _carrier_payload(carriers: tuple[Carrier, ...]) -> list[dict[str, str]]:
    return [{"filename": item.name, "sha256": item.sha256} for item in carriers]


def stage(
    run: Path,
    artifact: Path,
    *,
    artifact_approved: bool,
    approved_carriers: tuple[Path, ...] | None = None,
) -> StagedUpload:
    """Persist Gate 1 for the exact filenames approved for LMS upload."""

    root = Path(run).resolve()
    path = Path(artifact).resolve()
    if not artifact_approved:
        raise GateError("artifact approval is required before staging")
    if not root.is_dir():
        raise GateError("Gate 1 needs an existing run directory")
    if not path.is_file() or path.suffix.casefold() not in {".docx", ".pptx"}:
        raise GateError("Gate 1 needs an existing DOCX or PowerPoint artifact")
    carrier_inputs = (path,) if approved_carriers is None else approved_carriers
    carriers = tuple(_carrier(item) for item in carrier_inputs)
    names = tuple(item.name for item in carriers)
    if not carriers:
        raise GateError("Gate 1 needs at least one approved carrier")
    if len({name.casefold() for name in names}) != len(names):
        raise GateError("approved carrier filenames must be unique")
    if not any(item.path == path for item in carriers):
        raise GateError("the canonical artifact must be in the approved carrier set")
    digest = file_digest.sha256(path)
    _write(
        root / RECORD,
        {
            "artifact": path.name,
            "sha256": digest,
            "attachment_count": len(carriers),
            "approved_carriers": _carrier_payload(carriers),
            "uploaded_files": [],
            "gate1_approved": True,
            "gate2_confirmed": False,
        },
    )
    return StagedUpload(root, path, digest, carriers)


def approval_surface(staged: StagedUpload) -> str:
    """Return the exact filename-and-count surface shown for Gate 1 approval."""

    lines = [f"ATTACHMENT-COUNT: {len(staged.carriers)}"]
    lines.extend(f"FILENAME: {item.name}" for item in staged.carriers)
    return "\n".join(lines)


def upload_is_allowed(staged: StagedUpload, candidate: Path) -> bool:
    """Whether one candidate's name and bytes belong to the approved carrier set."""

    path = Path(candidate).resolve()
    if not path.is_file():
        return False
    match = next((item for item in staged.carriers if item.name == path.name), None)
    return bool(match is not None and file_digest.sha256(path) == match.sha256)


def confirm(
    staged: StagedUpload,
    *,
    uploaded_carriers: tuple[Path, ...],
    final_confirmation: bool,
) -> None:
    """Persist Gate 2 only for the exact unchanged approved upload population."""

    if not final_confirmation:
        raise GateError("final confirmation is required for Gate 2")
    uploaded = tuple(Path(item).resolve() for item in uploaded_carriers)
    approved_names = tuple(item.name for item in staged.carriers)
    uploaded_names = tuple(item.name for item in uploaded)
    if uploaded_names != approved_names or not all(
        upload_is_allowed(staged, item) for item in uploaded
    ):
        raise GateError("the staged upload population differs from the approved carrier set")
    if not staged.artifact.is_file() or file_digest.sha256(staged.artifact) != staged.sha256:
        raise GateError("the canonical artifact changed after Gate 1")
    payload = _read(staged.run)
    if (
        payload.get("artifact") != staged.artifact.name
        or payload.get("sha256") != staged.sha256
        or payload.get("approved_carriers") != _carrier_payload(staged.carriers)
        or payload.get("attachment_count") != len(staged.carriers)
    ):
        raise GateError("the durable Gate 1 record names another artifact or carrier set")
    payload["uploaded_files"] = list(uploaded_names)
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
            and payload.get("attachment_count") == len(staged.carriers)
            and payload.get("approved_carriers") == _carrier_payload(staged.carriers)
            and payload.get("uploaded_files") == [item.name for item in staged.carriers]
            and staged.artifact.is_file()
            and file_digest.sha256(staged.artifact) == staged.sha256
            and all(upload_is_allowed(staged, item.path) for item in staged.carriers)
        )
    except (GateError, OSError):
        return False


def completion_gate(
    run: Path, artifact: Path, submission: str | None = None
) -> tuple[bool, str]:
    """Grade approvals and the terminal canonical and posted artifact joins."""

    root = Path(run).resolve()
    path = Path(artifact).resolve()
    canonical = repo_root.output_root() / "course-assignments" / path.name
    canonical_failure: str | None = None
    try:
        payload = _read(root)
        approved = payload.get("approved_carriers")
        filenames = (
            tuple(item.get("filename", "") for item in approved)
            if isinstance(approved, list)
            and all(isinstance(item, dict) for item in approved)
            else ()
        )
        clean = bool(
            payload.get("gate1_approved") is True
            and payload.get("gate2_confirmed") is True
            and payload.get("artifact") == path.name
            and path.is_file()
            and payload.get("sha256") == file_digest.sha256(path)
            and payload.get("attachment_count") == len(filenames)
            and payload.get("uploaded_files") == list(filenames)
            and path.name in filenames
        )
        if clean and submission is not None:
            if not canonical.is_file():
                canonical_failure = f"canonical artifact is missing: {canonical}"
                clean = False
            elif file_digest.sha256(canonical) != file_digest.sha256(path):
                canonical_failure = (
                    f"canonical artifact fingerprint differs: {canonical}"
                )
                clean = False
        if clean and submission is not None:
            readings = read_posted_readings(
                (root / "reread.md").read_text(encoding="utf-8")
            )
            reading = next(
                (item for item in readings if item.artifact == submission), None
            )
            clean = bool(
                reading is not None
                and reading.attachment_count.isascii()
                and reading.attachment_count.isdecimal()
                and int(reading.attachment_count) == len(filenames)
                and reading.submitted_files == filenames
                and reading.submission_sha256_is_valid
                and reading.submission_sha256 == file_digest.sha256(path)
                and reading.verdict == "matches"
                and reading.verdict_has_substance
            )
    except (GateError, OSError, UnicodeError, ValueError):
        clean = False
    if clean and submission is not None:
        report = f"submission gates: clean - canonical artifact: {canonical}"
    elif canonical_failure is not None:
        report = f"submission gates: not clean - {canonical_failure}"
    else:
        report = "submission gates: clean" if clean else "submission gates: not clean"
    return not clean, report
