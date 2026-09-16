"""Verify that a Medatrax posted reading covers the current note bytes.

The complete boundary of this helper's clean result is declared in
``medatrax_posting.DECLARED_LIMITS``.
"""

from __future__ import annotations

import re
from hashlib import sha256
from pathlib import Path

from discussion_artifact import PostedReading, read_posted_readings
from run_grader import EvidenceDisposition


NOTE_NUMBER = re.compile(r"note-(?P<number>\d+)\.md", re.IGNORECASE)
READ_COUNT = re.compile(r"(?P<count>\d+)\s+of\s+(?P<total>\d+)\s+read", re.IGNORECASE)
VISIT_NUMBER = re.compile(r"(?P<number>\d+)\s*\|")
DECLARED_LIMITS = (
    (
        "batch note filename grammar",
        "Only top-level note-N.md files, with decimal N, enter a batch fingerprint.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "standalone note population",
        "A standalone fingerprint requires exactly one top-level Markdown file after README.md and reread.md are excluded.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "portal readback grammar",
        "A clean record binds a complete READ count to the note population and ordered VISIT lines carrying each required locator, reference, patient number, date, and verdict token.",
        EvidenceDisposition.BEHAVIOR,
    ),
)


def note_paths(run: Path, *, batch: bool) -> tuple[Path, ...]:
    """Return the exact source population fingerprinted by the clinical record."""

    candidates = tuple(
        path
        for path in run.glob("*.md")
        if path.is_file() and path.name.casefold() not in {"readme.md", "reread.md"}
    )
    if batch:
        numbered = tuple(
            (int(match.group("number")), path)
            for path in candidates
            if (match := NOTE_NUMBER.fullmatch(path.name)) is not None
        )
        return tuple(path for _number, path in sorted(numbered))
    return candidates if len(candidates) == 1 else ()


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

    if record.missing_fields:
        return f"{record.missing_fields[0]} is missing"
    read = READ_COUNT.fullmatch(record.read)
    if read is None or read.group("count") != read.group("total"):
        return "READ must state N of N read"
    expected = int(read.group("total"))
    if expected != expected_visits:
        return f"READ names {expected} visit(s) but the fingerprint covers {expected_visits} note(s)"
    if len(record.visits) != expected:
        return f"READ names {expected} visit(s) but {len(record.visits)} VISIT line(s) were found"
    if record.verdict != "matches" or not record.verdict_has_substance:
        return "VERDICT must be matches with readback detail"
    for number, visit in enumerate(record.visits, start=1):
        visit_number = VISIT_NUMBER.match(visit)
        required = (
            visit_number is not None and int(visit_number.group("number")) == number,
            re.search(r"(?:^|\|)\s*patient\s+\S+", visit, re.IGNORECASE) is not None,
            re.search(r"(?:^|\|)\s*reference\s+(?:matched|new)\s+\S+", visit, re.IGNORECASE) is not None,
            re.search(r"(?:^|\|)\s*patient-detail=\S+", visit, re.IGNORECASE) is not None,
            re.search(r"(?:^|\|)\s*note-view=\S*resultid=\S+", visit, re.IGNORECASE) is not None,
            re.search(r"(?:^|\|)\s*(?:created|visit-date)=\S+", visit, re.IGNORECASE) is not None,
            re.search(r"(?:^|\|)\s*matches(?:\s|$)", visit, re.IGNORECASE) is not None,
        )
        if not all(required):
            return f"VISIT {number} is missing a required copied locator, date, reference, patient number, or verdict"
    return None


def completion_gate(
    run: Path, submission: str | None, *, batch: bool
) -> tuple[bool, str]:
    """Return the terminal fingerprint verdict for one clinical submission."""

    if submission is None:
        return False, "the Medatrax posted reading: NOT GRADED - --submission was not supplied"
    record = posted_reading(run, submission)
    if record is None:
        return True, f"the Medatrax posted reading: finding - no readable REREAD record for {submission}"
    if not record.submission_sha256:
        return True, "the Medatrax posted reading: finding - SUBMISSION-SHA256 is missing"
    if not record.submission_sha256_is_valid:
        return True, "the Medatrax posted reading: finding - SUBMISSION-SHA256 is malformed"
    paths = note_paths(run, batch=batch)
    if not paths:
        unit = "numbered note files" if batch else "one standalone note file"
        return True, f"the Medatrax posted reading: finding - could not identify {unit}"
    record_problem = portal_record_problem(record, expected_visits=len(paths))
    if record_problem is not None:
        return True, f"the Medatrax posted reading: finding - {record_problem}"
    try:
        current = source_sha256(paths)
    except OSError:
        return True, "the Medatrax posted reading: finding - could not read the note bytes"
    if current != record.submission_sha256:
        return True, "the Medatrax posted reading: finding - SUBMISSION-SHA256 does not match the current note bytes"
    return False, "the Medatrax posted reading: clean"
