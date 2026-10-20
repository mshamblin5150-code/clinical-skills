"""Sign each coursework bar through one retained-byte and verified-reply mechanism."""

from __future__ import annotations

import re
import argparse
import importlib
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import date
from datetime import datetime, timezone

import run_grader
import completion_checks
import file_digest
from console_codec import use_utf8, require_python_floor
from run_record_reader import (read_tool_record, object_record, RecordShapeError,
                               UnreadableRecord, collecting_errors, fault_report, mark_not_graded,
                               update_tool_record, RecordUpdate, read_handwritten_record,
                               check_handwritten_text, DamagedRecord, damaged_record_result)


RECORD = "bar-signatures.json"
EXPECTED_ROW = "the bar signature"
REMEDY = "show the changed lines, take a new reply, run the signing command"
SKILLS = ("course-assignment", "discussion-post", "discussion-reply", "peer-critique", "practicum-case-study")
DECLARED_LIMITS = (
    "Whole-message verification proves the clinician wrote the reply, not that it concerned the shown bar.",
    "Changed-line display and completeness of a transcribed case-study bar remain reader-owned.",
    "Signing holds the canonical history lock across revision allocation, retained-copy creation and atomic history replacement; sibling bar/copy rollback is best effort, not a cross-file atomic transaction.",
    "Unreadable retained signature bookkeeping grants no historical waiver; dependent checks are not graded while independent artifact checks continue.",
)

def signed_date(text: str) -> str:
    values = re.findall(r"(?mi)^SIGNED:[ \t]*([^\r\n]*)", text)
    if len(values) != 1:
        raise run_grader.SourceError("bar.md needs exactly one SIGNED field")
    try:
        date.fromisoformat(values[0].strip())
    except ValueError as failure:
        raise run_grader.SourceError("bar.md SIGNED must be an ISO date") from failure
    return values[0].strip()

def validate(text: str, skill: str) -> None:
    if skill not in SKILLS:
        raise run_grader.SourceError("unknown bar signing skill")
    signed_date(text)
    if skill == "course-assignment":
        import assignment_bar
        envelope = assignment_bar.parse(text)
        importlib.import_module(assignment_bar.adapter_name(envelope)).validate_bar(envelope)
    else:
        import research_ledger
        research_ledger.read_bar(text)
        if skill == "discussion-post":
            import discussion_post_scan
            discussion_post_scan._read_bar(text)
        elif skill == "practicum-case-study":
            values = re.findall(r"(?mi)^SUBMISSION-TYPE:[ \t]*([^\r\n]*)", text)
            if len(values) != 1 or values[0].strip() not in {"canvas-composer", "file-upload"}:
                raise run_grader.SourceError("bar.md needs SUBMISSION-TYPE: canvas-composer or file-upload")


def _signatures(run: Path) -> list[dict]:
    """Read retained signing history; a damaged record is never a legacy bar."""
    path = run / RECORD
    payload = read_tool_record(path, _decode_signatures)
    return payload["signatures"] if payload is not None else []


def _decode_signatures(text: str) -> dict:
    """The single retained-history schema, shared with the assignment wrapper."""
    payload = object_record(text)
    rows = payload.get("signatures")
    if not isinstance(rows, list) or not rows:
        raise RecordShapeError("record items")
    for position, row in enumerate(rows, 1):
        if (not isinstance(row, dict) or row.get("copy") != f"signed-bars/bar-{position}.md"
                or not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                or not isinstance(row.get("clinician_reply"), str) or not row["clinician_reply"].strip()
                or row.get("reply_verification") not in {"verified", "not verified"}):
            raise RecordShapeError("record item fields")
    return payload


def _replace(path: Path, content: bytes) -> None:
    partial = path.with_name(path.name + "." + uuid.uuid4().hex + ".building")
    created = False
    try:
        with partial.open("xb") as stream:
            created = True
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(partial, path)
        created = False  # Publication consumed our candidate; its old name is no longer ours.
    finally:
        if created:
            partial.unlink(missing_ok=True)


def sign(run: Path, clinician_reply: str, *, skill: str) -> dict:
    """Sign validated bar bytes using ADR 0310's whole-message predicate.

    Reply verification inherits approval_record's limit: matching words does
    not establish that the message was about this bar.
    """
    run = Path(run).resolve()
    return update_tool_record(run / RECORD, _decode_signatures,
                              lambda previous: _sign(run, clinician_reply, previous, skill=skill))


def _sign(run: Path, clinician_reply: str, previous_record: dict | None, *, skill: str) -> RecordUpdate:
    from approval_record import verify_clinician_reply

    bar = run / "bar.md"
    original = bar.read_bytes()
    text = check_handwritten_text(original.decode("utf-8"), bar, "raw-text").require_text(force=True)
    if len(re.findall(r"(?m)^SIGNED\s*:", text)) > 1:
        raise run_grader.SourceError("bar.md has a duplicate SIGNED field")
    signed = f"SIGNED: {date.today().isoformat()}\n"
    text = re.sub(r"(?m)^SIGNED\s*:[^\r\n]*(?:\r?\n|$)", "", text)
    content = (signed + text).encode("utf-8")
    validate(content.decode("utf-8"), skill)
    history = previous_record["signatures"] if previous_record is not None else []
    previous = history[-1] if history else {}
    after = previous.get("reply_matched_at") or previous.get("recorded_at")
    boundary = completion_checks.instant(after)
    if history and boundary is None:
        raise run_grader.SourceError(f"previous signature time unreadable; {REMEDY}")
    verification = verify_clinician_reply(run, clinician_reply, (bar,),
        after=boundary.timestamp() if boundary else None,
        # A re-signing may implement the clinician's preceding own-work request.
        # Its whole reply must follow the previous signature, not the requested edit.
        source_modified_at=boundary.timestamp() if boundary else None)
    if verification.state == "not found":
        raise run_grader.SourceError("the clinician bar reply was not found: " + verification.reason)
    if bar.read_bytes() != original:
        raise run_grader.SourceError(f"bar changed during signing; {REMEDY}")
    copies = run / "signed-bars"
    copy = copies / f"bar-{len(history) + 1}.md"
    created_copy = False
    def rollback():
        copy.unlink(missing_ok=True)
        if bar.read_bytes() == content:
            _replace(bar, original)
    try:
        copies.mkdir(exist_ok=True)
        with copy.open("xb") as output:
            created_copy = True
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        entry = {
            "skill": skill,
            "copy": copy.relative_to(run).as_posix(),
            "sha256": file_digest.sha256(copy),
            "clinician_reply": clinician_reply,
            "reply_verification": "verified" if verification.state == "verified" else "not verified",
            "reply_reason": verification.reason,
            "reply_matched_at": verification.matched_at,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        _replace(bar, content)
    except BaseException as failure:
        if created_copy:
            try:
                rollback()
            except BaseException:
                pass
        if isinstance(failure, OSError):
            raise UnreadableRecord(run / RECORD, "could not be opened") from failure
        raise
    return RecordUpdate((json.dumps({"signatures": [*history, entry]}, indent=2) + "\n").encode("utf-8"),
                        entry, rollback=rollback)


def _completion_gate(
    run: Path, *, skill: str | None = None, artifact: str | None = None
) -> tuple[bool, str]:
    """Refuse changed or unrecorded current bars at every public gate."""
    try:
        run = Path(run)
        text = read_handwritten_record(run / "bar.md").require_text(artifact=artifact)
        signed = signed_date(text)
        if skill == "course-assignment":
            validate(text, skill)
        history = _signatures(run)
        if not history:
            check = "assignment_bar:completion_gate" if skill == "course-assignment" else "bar_signatures:completion_gate"
            moment = signed if skill == "course-assignment" else completion_checks.MOMENTS.get().get("approval") or signed
            if not completion_checks.active(check, moment):
                return False, EXPECTED_ROW + ": not graded - bar signed before the command existed"
            raise run_grader.SourceError(f"bar has no recorded signature; {REMEDY}")
        latest = history[-1]
        if skill is not None:
            validate(text, skill)
        copy_name = latest.get("copy")
        if not isinstance(copy_name, str):
            raise run_grader.SourceError(f"signed bar copy identity unreadable; {REMEDY}")
        copy = Path(copy_name)
        if copy.is_absolute() or copy.parts != ("signed-bars", f"bar-{len(history)}.md"):
            raise run_grader.SourceError(f"signed bar copy identity unreadable; {REMEDY}")
        if file_digest.sha256(run / "bar.md") != latest.get("sha256") or file_digest.sha256(run / copy) != latest.get("sha256"):
            raise run_grader.SourceError(f"bar.md does not match its latest signature; {REMEDY}")
        reply = latest.get("clinician_reply")
        if latest.get("reply_verification") not in ("verified", "not verified") or not isinstance(reply, str) or not reply.strip():
            raise run_grader.SourceError(f"bar signature reply unreadable; {REMEDY}")
        suffix = " - clinician reply not verified" if latest["reply_verification"] == "not verified" else ""
        return False, EXPECTED_ROW + ": clean" + suffix
    except UnreadableRecord as failure:
        if not collecting_errors():
            raise
        return False, fault_report(failure, check=EXPECTED_ROW)
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        return True, EXPECTED_ROW + ": not clean - " + str(failure)


def completion_gate(
    run: Path, *, skill: str | None = None, artifact: str | None = None
) -> tuple[bool, str]:
    """Report content damage locally while observing independent bookkeeping."""
    try:
        return _completion_gate(run, skill=skill, artifact=artifact)
    except DamagedRecord as failure:
        finding, report = damaged_record_result(failure, check=EXPECTED_ROW, artifact=artifact)
        try:
            _signatures(Path(run))
        except UnreadableRecord as record_failure:
            report += "\n" + fault_report(record_failure, check=EXPECTED_ROW)
        return finding, report


def latest_digest(run: Path, *, artifact: str | None = None) -> str | None:
    """Return the verified latest bar identity, or None for a legacy exemption."""
    failed, report = _completion_gate(run, artifact=artifact)
    if failed:
        raise run_grader.SourceError(report)
    try:
        history = _signatures(Path(run))
    except UnreadableRecord as failure:
        mark_not_graded(failure, check="bar-walk signature")
        return None
    return history[-1]["sha256"] if history else None


def apply_completion_gate(grade, run: Path, skill: str, submission: str | None):
    """Enable the same signature comparison at each coursework completion seam."""
    from dataclasses import replace
    if submission is None:
        return grade
    failed, report = completion_gate(run, skill=skill, artifact=submission)
    return replace(grade, findings_failed=grade.findings_failed or failed,
                   reports=(*grade.reports, report))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sign a coursework bar after clinician confirmation.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--reply", required=True, help="whole confirming clinician message")
    args = parser.parse_args(argv)
    try:
        entry = sign(args.run, args.reply, skill=args.skill)
    except DamagedRecord as failure:
        print(damaged_record_result(failure, check=EXPECTED_ROW, force=True)[1])
        return 1
    except UnreadableRecord as failure:
        print(fault_report(failure, check=EXPECTED_ROW))
        print(run_grader.format_unread_remainder(1))
        return 2
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        print(f"bar not signed: {failure}", file=sys.stderr)
        return 2
    print("bar signed: " + entry["reply_verification"])
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
