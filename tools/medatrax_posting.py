"""Verify that a Medatrax posted reading covers the current note bytes.

The complete boundary of this helper's clean result is declared in
``medatrax_posting.DECLARED_LIMITS``.
"""

from __future__ import annotations

from discussion_artifact import check_posted_reading

import json
import re
from hashlib import sha256
from pathlib import Path

from discussion_artifact import PostedReading, read_posted_readings
from run_grader import EvidenceDisposition


NOTE_NUMBER = re.compile(r"note-(?P<number>\d+)\.md", re.IGNORECASE)
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
        "A clean record binds a complete READ count to the note population, ordered VISIT lines carrying each required locator, reference, patient number, date, and verdict token, and one TIME-LOG line stating not requested or a date, hours and minutes, and entered or matched. The Time Log line does not establish instruction, a portal action, or agreement with the stated shift values.",
        EvidenceDisposition.BEHAVIOR,
    ),
)


def note_paths(run: Path, *, batch: bool) -> tuple[Path, ...]:
    """Return the exact source population fingerprinted by the clinical record."""

    candidates = tuple(
        path
        for path in run.glob("*.md")
        if path.is_file() and path.name.casefold() not in {"readme.md", "reread.md", "shift-summary.md"}
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


def completion_gate(
    run: Path, submission: str | None, *, batch: bool
) -> tuple[bool, str]:
    """Return the terminal fingerprint verdict for one clinical submission."""

    if submission is None:
        return False, "the Medatrax posted reading: NOT GRADED - --submission was not supplied"
    record = posted_reading(run, submission)
    paths = note_paths(run, batch=batch)
    if not paths:
        unit = "numbered note files" if batch else "one standalone note file"
        return True, f"the Medatrax posted reading: finding - could not identify {unit}"
    try:
        current = source_sha256(paths)
    except OSError:
        return True, "the Medatrax posted reading: finding - could not read the note bytes"
    outcomes = check_posted_reading(
        record, current, expected_visits=len(paths), matches_only=True,
        expected_patients=tuple(NOTE_NUMBER.fullmatch(path.name)["number"] for path in paths) if batch else None,
    )
    if outcomes:
        return True, f"the Medatrax posted reading: finding - {outcomes[0].message}"
    return False, "the Medatrax posted reading: clean"
