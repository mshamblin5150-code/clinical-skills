#!/usr/bin/env python3
"""Grade the attachment appendix of a coursework sitting's snapshot.

The complete ceiling belongs to ``DECLARED_LIMITS``. Completion checks the
retained sitting record, never the live course page.
"""

from __future__ import annotations

import completion_checks
import json
import re
import sys
from dataclasses import replace
from pathlib import Path
from typing import TypeVar

import coursework_run
import file_digest
import run_grader
from console_codec import require_python_floor, use_utf8
from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result


EXPECTED_ROW = "the LMS attachment identity"
DECLARED_LIMITS = (
    ("unrecorded-linked-file", "A linked file the run never recorded is unseen."),
    ("page-before-disk-unobservable", "The page-before-disk order is not observable."),
    ("handwritten attachment damage", "The shared reader checks the appendix's raw C0 and decoded JSON before local paths; a damaged appendix withholds its file checks while other keyed appendices continue."),
)
_FIELDS = frozenset({
    "file_id", "name", "size", "sha256", "local_sha256", "local_path",
    "location_source", "test",
})
_SHA256 = re.compile(r"[0-9a-f]{64}")
TScan = TypeVar("TScan")


def _records(path: Path, artifact: str | None = None) -> list[dict]:
    text = read_handwritten_record(path, "attachments").require_text(artifact=artifact).strip()
    if text == "ATTACHMENTS: none":
        return []
    header, separator, body = text.partition("\n")
    if header.rstrip("\r") != "ATTACHMENTS: files" or not separator:
        raise ValueError("attachment declaration is invalid")
    rows = json.loads(body)
    if not isinstance(rows, list) or not rows:
        raise ValueError("files declaration needs a nonempty record list")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or frozenset(row) != _FIELDS:
            raise ValueError("attachment record shape is invalid")
        for field in ("file_id", "name", "local_path"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"attachment {field} is missing")
        if row["file_id"] in seen:
            raise ValueError("attachment file id is duplicated")
        seen.add(row["file_id"])
        if type(row["size"]) is not int or row["size"] < 0:
            raise ValueError("attachment size is invalid")
        if not Path(row["local_path"]).is_absolute():
            raise ValueError("attachment local path must be absolute")
        if row["location_source"] not in ("found", "clinician-supplied"):
            raise ValueError("attachment location source is invalid")
        digest = row["local_sha256"]
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise ValueError("attachment local fingerprint is invalid")
        if row["test"] == "sha256":
            if row["sha256"] != digest:
                raise ValueError("local fingerprint does not match the page fingerprint")
        elif row["test"] == "size":
            if row["sha256"] is not None:
                raise ValueError("size fallback requires an unavailable page fingerprint")
        else:
            raise ValueError("attachment identity test is invalid")
    return rows


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    """Re-fingerprint each selected sitting appendix without a page request."""
    frozen = completion_checks.exemption(run, submission, "lms_attachments", "LMS attachments")
    if frozen is not None:
        return False, frozen
    if submission is None:
        return False, f"{EXPECTED_ROW}: not graded - --submission was not supplied"
    findings = []
    count = 0
    try:
        keys = coursework_run.submission_keys(submission)
    except ValueError as failure:
        return True, f"{EXPECTED_ROW}: finding - {failure}"
    for key in keys:
        record = run / "lms-attachments" / f"{key}.md"
        try:
            rows = _records(record, key)
        except DamagedRecord as failure:
            _failed, report = damaged_record_result(failure, check=EXPECTED_ROW, artifact=key)
            findings.append(report)
            continue
        except (OSError, UnicodeError, ValueError) as failure:
            detail = "record is missing" if isinstance(failure, FileNotFoundError) else "record is unreadable or invalid"
            findings.append(f"{key}: {detail}")
            continue
        for row in rows:
            count += 1
            local = Path(row["local_path"])
            try:
                matches = (
                    local.stat().st_size == row["size"]
                    and file_digest.sha256(local) == row["local_sha256"]
                )
            except OSError:
                matches = False
            if not matches:
                findings.append(f"{key}: file {row['file_id']} local copy is missing or changed")
    detail = "finding - " + "; ".join(findings) if findings else "clean"
    return bool(findings), f"{EXPECTED_ROW}: {detail}; recorded files checked: {count}"


def apply_completion_gate(
    grade: run_grader.Grade[TScan], run: Path, submission: str | None,
) -> run_grader.Grade[TScan]:
    failed, report = completion_gate(run, submission)
    return replace(
        grade, findings_failed=grade.findings_failed or failed,
        reports=grade.reports + (report,),
    )


def main(argv: list[str]) -> int:
    if not argv or len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--submission"):
        print("usage: lms_attachments.py <run directory> [--submission <key[,key]>]", file=sys.stderr)
        return 2
    run = Path(argv[0])
    if not run.is_dir():
        print("attachments not scanned: no run directory", file=sys.stderr)
        return 2
    failed, report = completion_gate(run, argv[2] if len(argv) == 3 else None)
    print(report)
    return int(failed)


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
