"""Sign each coursework bar through one retained-byte and verified-reply mechanism."""

from __future__ import annotations

import re
import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from datetime import date
from datetime import datetime, timezone

import run_grader
import completion_checks
import file_digest
from console_codec import use_utf8, require_python_floor


RECORD = "bar-signatures.json"
EXPECTED_ROW = "the bar signature"
REMEDY = "show the changed lines, take a new reply, run the signing command"
SKILLS = ("course-assignment", "discussion-post", "discussion-reply", "peer-critique", "practicum-case-study")
DECLARED_LIMITS = (
    "Whole-message verification proves the clinician wrote the reply, not that it concerned the shown bar.",
    "Changed-line display and completeness of a transcribed case-study bar remain reader-owned.",
    "Writes retain atomic replacement without a shared artifact lock; the locked-writer migration belongs to #1905.",
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
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload["signatures"]
        if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
            raise ValueError("signatures must be a nonempty object population")
        return rows
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as failure:
        raise run_grader.SourceError(f"bar signature history unreadable; {REMEDY}") from failure


def _replace(path: Path, content: bytes) -> None:
    partial = path.with_name(path.name + f".{os.getpid()}.building")
    try:
        partial.write_bytes(content)
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def sign(run: Path, clinician_reply: str, *, skill: str) -> dict:
    """Sign validated bar bytes using ADR 0310's whole-message predicate.

    Reply verification inherits approval_record's limit: matching words does
    not establish that the message was about this bar.
    """
    from approval_record import verify_clinician_reply

    run = Path(run).resolve()
    bar = run / "bar.md"
    original = bar.read_bytes()
    text = original.decode("utf-8")
    if len(re.findall(r"(?m)^SIGNED\s*:", text)) > 1:
        raise run_grader.SourceError("bar.md has a duplicate SIGNED field")
    signed = f"SIGNED: {date.today().isoformat()}\n"
    text = re.sub(r"(?m)^SIGNED\s*:[^\r\n]*(?:\r?\n|$)", "", text)
    content = (signed + text).encode("utf-8")
    validate(content.decode("utf-8"), skill)
    history = _signatures(run)
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
    copies.mkdir(exist_ok=True)
    copy = copies / f"bar-{len(history) + 1}.md"
    with copy.open("xb") as output:
        output.write(content)
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
    try:
        _replace(bar, content)
        _replace(run / RECORD, (json.dumps({"signatures": [*history, entry]}, indent=2) + "\n").encode("utf-8"))
    except BaseException:
        copy.unlink(missing_ok=True)
        if bar.read_bytes() == content:
            _replace(bar, original)
        raise
    return entry


def completion_gate(run: Path, *, skill: str | None = None) -> tuple[bool, str]:
    """Refuse changed or unrecorded current bars at every public gate."""
    try:
        run = Path(run)
        text = (run / "bar.md").read_text(encoding="utf-8")
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
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        return True, EXPECTED_ROW + ": not clean - " + str(failure)


def latest_digest(run: Path) -> str | None:
    """Return the verified latest bar identity, or None for a legacy exemption."""
    failed, report = completion_gate(run)
    if failed:
        raise run_grader.SourceError(report)
    history = _signatures(Path(run))
    return history[-1]["sha256"] if history else None


def apply_completion_gate(grade, run: Path, skill: str, submission: str | None):
    """Enable the same signature comparison at each coursework completion seam."""
    from dataclasses import replace
    if submission is None:
        return grade
    failed, report = completion_gate(run, skill=skill)
    return replace(grade, coverage_failed=grade.coverage_failed or failed,
                   reports=(*grade.reports, report))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sign a coursework bar after clinician confirmation.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--reply", required=True, help="whole confirming clinician message")
    args = parser.parse_args(argv)
    try:
        entry = sign(args.run, args.reply, skill=args.skill)
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        print(f"bar not signed: {failure}", file=sys.stderr)
        return 2
    print("bar signed: " + entry["reply_verification"])
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
