"""Verify that a Medatrax posted reading covers the current note bytes.

The complete boundary of this helper's clean result is declared in
``medatrax_posting.DECLARED_LIMITS``.
"""

from __future__ import annotations

import completion_checks
from discussion_artifact import check_posted_reading, PostedReadingOutcome

import json
import argparse
import os
import re
import sys
import tempfile
from hashlib import sha256
from pathlib import Path

from discussion_artifact import PostedReading, read_posted_readings
from run_grader import EvidenceDisposition, RUN_RECORD_STEMS, is_run_record
from console_codec import require_python_floor, use_utf8
from run_record_reader import read_tool_record


NOTE_NUMBER = re.compile(r"note-(?P<number>\d+)\.md", re.IGNORECASE)
DECLARED_LIMITS = (
    (
        "batch note filename grammar",
        "Only top-level note-N.md files, with decimal N, enter a batch fingerprint.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "standalone note population",
        "A standalone fingerprint requires exactly one top-level Markdown file after the shared "
        "run-record list is excluded: " + ", ".join(f"{stem}.md" for stem in RUN_RECORD_STEMS) + ".",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "portal readback grammar",
        "A clean record binds a complete READ count to the note population, ordered VISIT lines carrying each required locator, reference, patient number, date, and verdict token, and one TIME-LOG line stating not requested or a date, hours and minutes, and entered or matched. The Time Log line does not establish instruction, a portal action, or agreement with the stated shift values.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "agent supplied portal readings",
        "The writer formats supplied readings; it cannot establish that they are what the portal displayed.",
        EvidenceDisposition.DECLARED_READING,
    ),
)


def note_paths(run: Path, *, batch: bool) -> tuple[Path, ...]:
    """Return the exact source population fingerprinted by the clinical record."""

    candidates = tuple(
        path
        for path in run.glob("*.md")
        if path.is_file() and not is_run_record(path)
    )
    if batch:
        numbered = tuple(
            (int(match.group("number")), path)
            for path in candidates
            if (match := NOTE_NUMBER.fullmatch(path.name)) is not None
        )
        return tuple(path for _number, path in sorted(numbered))
    approved = _approved_standalone_note(run)
    if approved is not None:
        return (approved,)
    return candidates if len(candidates) == 1 else ()


def _approved_standalone_note(run: Path) -> Path | None:
    """Resolve the output note named by one clinical-note approval record."""

    try:
        payload = json.loads((run / "posting-approvals.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    matches = tuple(
        item
        for item in items
        if isinstance(item, dict) and item.get("skill") == "clinical-note"
    )
    if len(matches) != 1:
        return None
    sources = matches[0].get("sources")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], str):
        return None
    note = Path(sources[0])
    return note if note.is_file() else None


def source_sha256(paths: tuple[Path, ...]) -> str:
    digest = sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def posted_reading(run: Path, submission: str) -> PostedReading | None:
    try:
        records = read_posted_readings((run / "reread.md").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None
    matches = tuple(record for record in records if record.artifact == submission)
    return matches[0] if len(matches) == 1 else None


def portal_record_problem(
    record: PostedReading, *, expected_visits: int
) -> str | None:
    """Return why a clinical posted reading cannot establish a complete readback."""

    outcomes = check_posted_reading(
        record, record.submission_sha256,
        expected_visits=expected_visits, matches_only=True,
    )
    return outcomes[0].message if outcomes else None


@completion_checks.dated_posted_reading
def posted_reading_check(
    run: Path, submission: str, *, batch: bool
) -> tuple[PostedReadingOutcome, ...]:
    """Apply the terminal portal grammar to the current note population."""
    import frozen_grade
    if frozen_grade.report(run, submission) is not None:
        return ()
    paths = note_paths(run, batch=batch)
    if not paths:
        unit = "numbered note files" if batch else "one standalone note file"
        raise ValueError(f"could not identify {unit}")
    return check_posted_reading(
        posted_reading(run, submission), source_sha256(paths),
        expected_visits=len(paths), matches_only=True,
        expected_patients=tuple(NOTE_NUMBER.fullmatch(path.name)["number"] for path in paths) if batch else None,
    )


def completion_gate(
    run: Path, submission: str | None, *, batch: bool
) -> tuple[bool, str]:
    """Return the terminal fingerprint verdict for one clinical submission."""
    frozen = completion_checks.exemption(run, submission, "medatrax_posting", "the Medatrax posted reading")
    if frozen is not None:
        return False, frozen

    if submission is None:
        return False, "the Medatrax posted reading: NOT GRADED - --submission was not supplied"
    try:
        outcomes = posted_reading_check(run, submission, batch=batch)
    except ValueError as failure:
        return True, f"the Medatrax posted reading: finding - {failure}"
    except OSError:
        return True, "the Medatrax posted reading: finding - could not read the note bytes"
    if outcomes:
        return True, f"the Medatrax posted reading: finding - {outcomes[0].message}"
    return False, "the Medatrax posted reading: clean"


def _one_line(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("readback values must be nonempty single lines without controls")
    return value


def _record_text(payload: dict, submission: str, paths: tuple[Path, ...]) -> str:
    """Produce only the known portal fields, then let the shared checker grade."""
    if not isinstance(payload, dict) or set(payload) != {"post_url", "posted", "verdict_detail", "time_log", "visits"}:
        raise ValueError("readback input needs the documented fields only")
    time_log = payload["time_log"]
    if time_log is None:
        duration = "not requested"
    else:
        if not isinstance(time_log, dict) or set(time_log) != {"date", "hours", "minutes", "outcome"}:
            raise ValueError("Time Log needs date, hours, minutes, and outcome")
        hours, minutes = time_log["hours"], time_log["minutes"]
        if type(hours) is not int or type(minutes) is not int or hours < 0 or not 0 <= minutes < 60 or time_log["outcome"] not in {"entered", "matched"}:
            raise ValueError("invalid Time Log duration or outcome")
        duration = f"date={_one_line(time_log['date'])} | duration={hours} hours {minutes} minutes | {time_log['outcome']}"
    visits = payload["visits"]
    if not isinstance(visits, list) or len(visits) != len(paths):
        raise ValueError("visit population differs from the notes")
    lines = [f"## REREAD: {_one_line(submission)}", f"POST-URL: {_one_line(payload['post_url'])}",
             f"POSTED: {_one_line(payload['posted'])}", f"READ: {len(visits)} of {len(paths)} read",
             f"VERDICT: matches - {_one_line(payload['verdict_detail'])}",
             f"SUBMISSION-SHA256: {source_sha256(paths)}", f"TIME-LOG: {duration}"]
    required = {"patient", "reference_status", "reference", "patient_detail", "note_view", "finished", "verdict"}
    for order, visit in enumerate(visits, 1):
        if not isinstance(visit, dict) or not required <= set(visit) or set(visit) - required not in ({"created"}, {"visit_date"}, {"created", "corrections"}, {"visit_date", "corrections"}):
            raise ValueError("visit needs the documented locators and exactly one date kind")
        if type(visit["patient"]) is not int or visit["patient"] < 1 or visit["reference_status"] not in {"matched", "new"} or visit["verdict"] != "matches":
            raise ValueError("invalid visit patient, reference status, or verdict")
        date_kind = "created" if "created" in visit else "visit_date"
        line = (f"VISIT: {order} | patient {visit['patient']} | reference {visit['reference_status']} {_one_line(visit['reference'])}"
                f" | patient-detail={_one_line(visit['patient_detail'])} | note-view={_one_line(visit['note_view'])}"
                f" | {date_kind.replace('_', '-')}={_one_line(visit[date_kind])} | finished={_one_line(visit['finished'])} | matches")
        corrections = visit.get("corrections", [])
        if not isinstance(corrections, list):
            raise ValueError("corrections must be a list")
        for correction in corrections:
            line += f" | correction={_one_line(correction)}; reread matches"
        lines.append(line)
    return "\n".join(lines) + "\n"


def _checked_record(text: str, submission: str, paths: tuple[Path, ...], *, batch: bool) -> None:
    records = read_posted_readings(text)
    matches = [record for record in records if record.artifact == submission]
    record = matches[0] if len(matches) == 1 else None
    problems = check_posted_reading(record, source_sha256(paths), expected_visits=len(paths), matches_only=True,
        expected_patients=tuple(NOTE_NUMBER.fullmatch(path.name)["number"] for path in paths) if batch else None)
    if problems:
        raise ValueError(problems[0].message)


def main(argv: list[str]) -> int:
    """Write a validated reread.md or check a hand-written one before AAR."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("write", "check"))
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--submission", required=True)
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--notes", type=Path, nargs="+")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        paths = tuple(args.notes) if args.notes else note_paths(args.run, batch=args.batch)
        if not paths:
            raise ValueError("could not identify the note population")
        if args.batch and any(NOTE_NUMBER.fullmatch(path.name) is None for path in paths):
            raise ValueError("batch notes must have numbered filenames")
        target = args.run / "reread.md"
        # Parse every existing block before a write so damage is never overwritten.
        existing = read_tool_record(target, lambda text: (read_posted_readings(text), text))
        if args.action == "check":
            if existing is None:
                raise ValueError("posted reading is missing")
            _checked_record(existing[1], args.submission, paths, batch=args.batch)
        else:
            if args.input is None:
                raise ValueError("write needs --input readback.json")
            if existing is not None:
                for record in existing[0]:
                    problem = portal_record_problem(record, expected_visits=len(record.visits))
                    if problem:
                        raise ValueError("existing posted reading is malformed")
            payload = read_tool_record(args.input, json.loads)
            text = _record_text(payload, args.submission, paths)
            _checked_record(text, args.submission, paths, batch=args.batch)
            if existing is not None:
                current = existing[1]
                blocks = tuple(re.finditer(r"(?ms)^## REREAD:([^\n]+)\n.*?(?=^## REREAD:|\Z)", current))
                selected = [block for block in blocks if block[1].strip() == args.submission]
                if selected:
                    if not args.replace:
                        raise ValueError("record already exists; use --replace for an explicit revision")
                    block = selected[0]
                    text = current[:block.start()] + text + current[block.end():]
                else:
                    text = current.rstrip() + "\n\n" + text
            _checked_record(text, args.submission, paths, batch=args.batch)
            with tempfile.NamedTemporaryFile(dir=args.run, suffix=".building", delete=False) as stream:
                temporary = Path(stream.name)
            try:
                temporary.write_text(text, encoding="utf-8")
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        print("Medatrax posted reading: clean")
        return 0
    except (OSError, UnicodeError, ValueError, TypeError):
        print("Medatrax posted reading: refused - private input or record unreadable or invalid", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
