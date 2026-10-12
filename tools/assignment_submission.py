"""Durable authorization state for course-assignment upload carriers.

The posted-fingerprint coverage boundary belongs to
``assignment_submission.DECLARED_LIMITS``; this docstring copies no row.
"""

from __future__ import annotations

import completion_checks
import assignment_bar
from discussion_artifact import check_posted_reading, PostedReadingOutcome

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import reader_remarks
import file_digest
import repo_root
import project_context
from discussion_artifact import read_posted_readings
from run_grader import EvidenceDisposition


DECLARED_LIMITS = (
    (
        "page-fingerprint-origin",
        "A page POSTED-FILE fingerprint copied from the approved record passes; the grader cannot prove that the page computed it.",
        EvidenceDisposition.BEHAVIOR,
    ),
)


class GateError(ValueError):
    pass


def _require_signed_bar(run: Path) -> None:
    failed, report = assignment_bar.completion_gate(run)
    if failed:
        raise GateError(report)


RECORD = "submission-gates.json"
COURSE_ASSIGNMENT_SCAN = Path(__file__).resolve().parent / "course_assignment_scan.py"


class UploadRoute(str, Enum):
    AWAITING = "awaiting-upload"
    AGENT = "agent"
    CLINICIAN = "clinician"


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


def _pre_upload_grade(run: Path, artifact: Path) -> tuple[bool, str]:
    """Run the artifact-aware grade before durable approval is recorded."""

    completed = subprocess.run(
        [
            sys.executable,
            str(COURSE_ASSIGNMENT_SCAN),
            str(run),
            "--artifact",
            str(artifact),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    report = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    return completed.returncode == 0, report or f"grader exited {completed.returncode}"


def _next_approval_revision(run: Path) -> int:
    try:
        previous = _read(run).get("approval_revision", 0)
    except GateError:
        previous = 0
    return previous + 1 if isinstance(previous, int) and previous >= 0 else 1


def _upload_route(payload: dict[str, object]) -> UploadRoute | None:
    """Read the current route, including the pre-route Gate 2 record shape."""

    try:
        return UploadRoute(payload.get("upload_route"))
    except (TypeError, ValueError):
        return (
            UploadRoute.AGENT
            if payload.get("gate2_confirmed") is True
            else None
        )


def prepare(run: Path, artifact: Path) -> reader_remarks.Prepared:
    """Grade Gate 1 before asking for the artifact go-ahead."""
    root, path = Path(run).resolve(), Path(artifact).resolve()
    _require_signed_bar(root)
    clean, report = _pre_upload_grade(root, path)
    if not clean:
        raise GateError("the run-directory pre-upload grade is not clean: " + report)
    context = project_context.go_ahead(root, path.stem, approval_revision=_next_approval_revision(root))
    if context.finding:
        raise GateError("project-context go-ahead has a finding: " + context.report)
    report = reader_remarks.approval_report(report, context.report, root, (path.name,))
    return reader_remarks.prepare(root, "course-assignment", path.stem, (path,), report)


def stage(
    run: Path,
    artifact: Path,
    *,
    artifact_approved: bool,
    clinician_reply: str,
    remark_outcomes: tuple[reader_remarks.Outcome, ...] = (),
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
    grade_clean, grade_report = _pre_upload_grade(root, path)
    if not grade_clean:
        raise GateError(f"the run-directory pre-upload grade is not clean: {grade_report}")
    _require_signed_bar(root)
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
    revision = _next_approval_revision(root)
    try:
        context = project_context.go_ahead(root, path.stem, approval_revision=revision)
    except (OSError, UnicodeError, ValueError) as failure:
        raise GateError("project-context go-ahead result could not be written") from failure
    if context.finding:
        raise GateError("project-context go-ahead has a finding: " + context.report)
    from approval_record import verify_clinician_reply
    verification = verify_clinician_reply(root, clinician_reply, (path,))
    if verification.state != "verified":
        raise GateError("Gate 1 needs a verified whole clinician reply: " + verification.reason)
    grade_report = reader_remarks.approval_report(grade_report, context.report, root, (path.name,))
    try:
        remarks = reader_remarks.verify(root, "course-assignment", path.stem, (path,), grade_report,
            clinician_reply, verification.matched_at, remark_outcomes)
    except reader_remarks.RemarkError as failure:
        raise GateError(str(failure)) from failure
    _write(
        root / RECORD,
        {
            "artifact": path.name,
            "artifact_path": str(path),
            "sha256": digest,
            "attachment_count": len(carriers),
            "approved_carriers": _carrier_payload(carriers),
            "uploaded_files": [],
            "gate1_approved": True,
            "clinician_reply": clinician_reply,
            "reply_matched_at": verification.matched_at,
            "reader_remarks": remarks,
            "coverage_lines": list(reader_remarks.coverage_lines(grade_report)),
            "pregrade_report": grade_report,
            "upload_route": UploadRoute.AWAITING.value,
            "approval_revision": revision,
            "project_context_check": True,
            "pregrade_status": "incomplete" if context.coverage else "clean",
            "project_context_report": context.report,
        },
    )
    return StagedUpload(root, path, digest, carriers)


def approval_surface(staged: StagedUpload) -> str:
    """Return the exact filename-and-count surface shown for Gate 1 approval."""

    lines = [f"ATTACHMENT-COUNT: {len(staged.carriers)}"]
    lines.extend(f"FILENAME: {item.name}" for item in staged.carriers)
    return "\n".join(lines)


def project_context_posting(run: Path, submission: str):
    """Expose the assignment approval's keyed upload state to the shared reader."""
    from approval_record import ProjectContextPosting
    if not (run / RECORD).exists():
        return ProjectContextPosting(False)
    payload = _read(run)
    artifact = payload.get("artifact")
    if not isinstance(artifact, str) or Path(artifact).stem != submission:
        return ProjectContextPosting(False)
    revision = payload.get("approval_revision")
    if revision is not None and (type(revision) is not int or revision < 1):
        raise GateError("invalid assignment approval revision")
    return ProjectContextPosting(_upload_route(payload) in {UploadRoute.AGENT, UploadRoute.CLINICIAN}, payload.get("project_context_check") is True, revision)


def upload_is_allowed(staged: StagedUpload, candidate: Path) -> bool:
    """Whether one candidate's path, name and bytes are an approved carrier."""

    path = Path(candidate).resolve()
    if assignment_bar.completion_gate(staged.run)[0]:
        return False
    if not path.is_file():
        return False
    match = next((item for item in staged.carriers if item.name == path.name), None)
    return bool(
        match is not None
        and path == match.path.resolve()
        and file_digest.sha256(path) == match.sha256
    )


def confirm(
    staged: StagedUpload,
    *,
    uploaded_carriers: tuple[Path, ...],
    final_confirmation: bool,
) -> None:
    """Persist Gate 2 only for the exact unchanged approved upload population."""

    if not final_confirmation:
        raise GateError("final confirmation is required for Gate 2")
    _require_signed_bar(staged.run)
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
    payload["upload_route"] = UploadRoute.AGENT.value
    payload.pop("gate2_confirmed", None)
    payload.pop("clinician_upload_recorded", None)
    _write(staged.run / RECORD, payload)


def record_clinician_upload(
    run: Path,
    artifact: Path,
    *,
    uploaded_carriers: tuple[Path, ...],
) -> None:
    """Record the clinician's upload against an existing exact Gate 1 approval."""

    root = Path(run).resolve()
    path = Path(artifact).resolve()
    try:
        payload = _read(root)
    except GateError as failure:
        raise GateError("a clinician posting needs recorded approval") from failure
    if payload.get("gate1_approved") is not True:
        raise GateError("a clinician posting needs recorded approval")
    _require_signed_bar(root)
    approved = payload.get("approved_carriers")
    if not isinstance(approved, list) or not all(
        isinstance(item, dict) for item in approved
    ):
        raise GateError("a clinician posting needs a readable recorded approval")
    approved_names = tuple(str(item.get("filename", "")) for item in approved)
    uploaded = tuple(Path(item).resolve() for item in uploaded_carriers)
    uploaded_names = tuple(item.name for item in uploaded)
    approved_digests = {
        str(item.get("filename", "")): str(item.get("sha256", ""))
        for item in approved
    }
    if (
        payload.get("artifact") != path.name
        or payload.get("sha256") != file_digest.sha256(path)
        or path.name not in approved_names
        or uploaded_names != approved_names
        or any(
            not candidate.is_file()
            or file_digest.sha256(candidate) != approved_digests.get(candidate.name)
            for candidate in uploaded
        )
    ):
        raise GateError(
            "the clinician-uploaded population differs from the recorded approval"
        )
    payload["uploaded_files"] = list(uploaded_names)
    payload["upload_route"] = UploadRoute.CLINICIAN.value
    payload.pop("gate2_confirmed", None)
    payload.pop("clinician_upload_recorded", None)
    _write(root / RECORD, payload)


def submit_is_authorized(staged: StagedUpload) -> bool:
    """Whether durable Gate 2 permits the Submit Assignment click right now."""

    try:
        _require_signed_bar(staged.run)
        payload = _read(staged.run)
        return bool(
            payload.get("gate1_approved") is True
            and _upload_route(payload) is UploadRoute.AGENT
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


@completion_checks.dated_posted_reading
def posted_reading_check(
    run: Path, submission: str, artifact: Path
) -> tuple[PostedReadingOutcome, ...]:
    """Check the posted artifact and the complete approved carrier population."""
    import frozen_grade
    if frozen_grade.report(run, submission) is not None:
        return ()
    payload = _read(run)
    approved = payload.get("approved_carriers")
    if not isinstance(approved, list) or not all(isinstance(item, dict) for item in approved):
        raise GateError("approved carrier population cannot be read")
    filenames = tuple(item.get("filename", "") for item in approved)
    posted_files = tuple((item.get("filename", ""), item.get("sha256", "")) for item in approved)
    reread = run / "reread.md"
    readings = read_posted_readings(reread.read_text(encoding="utf-8")) if reread.is_file() else ()
    reading = next((item for item in readings if item.artifact == submission), None)
    return check_posted_reading(
        reading, file_digest.sha256(artifact), matches_only=True,
        expected_submitted_files=filenames,
        expected_posted_files=posted_files, run=run,
    )


def completion_gate(
    run: Path, artifact: Path, submission: str | None = None
) -> tuple[bool, str]:
    """Grade approvals and the terminal canonical and posted artifact joins."""
    frozen = completion_checks.exemption(run, submission, "assignment_submission", "assignment submission")
    if frozen is not None:
        return False, frozen

    failed, report = assignment_bar.completion_gate(run)
    if failed:
        return True, report

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
            and _upload_route(payload)
            in (UploadRoute.AGENT, UploadRoute.CLINICIAN)
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
            outcomes = posted_reading_check(root, submission, path)
            if outcomes:
                canonical_failure = outcomes[0].message
            clean = not outcomes
    except (GateError, OSError, UnicodeError, ValueError):
        clean = False
    if clean and submission is not None:
        report = f"submission gates: clean - canonical artifact: {canonical}"
    elif canonical_failure is not None:
        report = f"submission gates: not clean - {canonical_failure}"
    else:
        report = "submission gates: clean" if clean else "submission gates: not clean"
    return not clean, report
