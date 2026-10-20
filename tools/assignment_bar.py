"""Read the common signed envelope for a course-assignment artifact."""

from __future__ import annotations

from run_record_reader import read_tool_record, object_record, RecordShapeError, UnreadableRecord, fault_report, collecting_errors

import re
import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from datetime import datetime, timezone

import run_grader
import completion_checks
import file_digest
from console_codec import use_utf8, require_python_floor


DECLARED_LIMITS = (
    'assignment_bar record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.',
)


FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
COMMON_FIELDS = (
    "ASSIGNMENT",
    "SIGNED",
    "ARTIFACT",
    "SOURCE-CLASSES",
    "RECENCY-WINDOW-YEARS",
)
ADAPTERS = {
    "deck": "deck_scan",
    "docx": "assignment_docx_scan",
}
RECORD = "bar-signatures.json"
EXPECTED_ROW = "the assignment bar signature"
REMEDY = "show the changed lines, take a new reply, run the signing command"


@dataclass(frozen=True)
class Envelope:
    artifact: str
    fields: dict[str, str]
    counts: dict[str, int]


def parse(text: str) -> Envelope:
    """Return one validated common envelope without reading branch fields."""

    matches = tuple(FIELD.finditer(text))
    fields = {match.group("name"): match.group("value").strip() for match in matches}
    counts = {
        name: sum(match.group("name") == name for match in matches)
        for name in {match.group("name") for match in matches}
    }
    for name in COMMON_FIELDS:
        count = counts.get(name, 0)
        if count > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
        if count == 0:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    try:
        date.fromisoformat(fields["SIGNED"])
    except ValueError as failure:
        raise run_grader.SourceError("bar.md SIGNED must be an ISO date") from failure
    artifact = fields["ARTIFACT"].casefold()
    if artifact not in ADAPTERS:
        raise run_grader.SourceError("bar.md ARTIFACT must be deck or docx")
    return Envelope(artifact, fields, counts)


def adapter_name(envelope: Envelope) -> str:
    """Return the deep artifact adapter selected by a signed envelope."""

    return ADAPTERS[envelope.artifact]


def _signatures(run: Path) -> list[dict]:
    """Read retained signing history; a damaged record is never a legacy bar."""
    path = run / RECORD
    payload = read_tool_record(path, _decode_signatures)
    return payload["signatures"] if payload is not None else []


def _decode_signatures(text: str) -> dict:
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
    partial = path.with_name(path.name + f".{os.getpid()}.building")
    try:
        partial.write_bytes(content)
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def sign(run: Path, clinician_reply: str) -> dict:
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
    envelope = parse(content.decode("utf-8"))
    importlib.import_module(adapter_name(envelope)).validate_bar(envelope)
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


def completion_gate(run: Path) -> tuple[bool, str]:
    """Refuse changed or unrecorded current bars at every public gate."""
    try:
        run = Path(run)
        envelope = parse((run / "bar.md").read_text(encoding="utf-8"))
        history = _signatures(run)
        if not history:
            if not completion_checks.active("assignment_bar:completion_gate", envelope.fields["SIGNED"]):
                return False, EXPECTED_ROW + ": not graded - bar signed before the command existed"
            raise run_grader.SourceError(f"bar has no recorded signature; {REMEDY}")
        latest = history[-1]
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sign a course-assignment bar after clinician confirmation.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--reply", required=True, help="whole confirming clinician message")
    args = parser.parse_args(argv)
    try:
        entry = sign(args.run, args.reply)
    except UnreadableRecord as failure:
        print(fault_report(failure, check=EXPECTED_ROW))
        print(run_grader.format_unread_remainder(1))
        return 2
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        print(f"bar not signed: {failure}", file=sys.stderr)
        return 2
    print("assignment bar signed: " + entry["reply_verification"])
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
