"""Which runs the E/M audit check-off row grades, readable without loading the coding records.

``em_audit.completion_gate`` and ``specificity_scan`` both read this module first, so a run the row
does not grade never loads the approval and manifest stack ``em_audit`` imports. It holds the row
name, the two records whose absence marks a direct consultation, and the not-graded answers for a
missing ``--submission`` and for that consultation. It imports only the standard library.
"""
from __future__ import annotations

from pathlib import Path

# em_audit.EXPECTED_ROW, the name completion_checks derives the row's start-date key from.
ROW = "the E/M audit check-offs"
# review_manifest.MANIFEST, named here so this module stays light; test_em_audit binds the two.
MANIFEST = "batch-codes.json"
# The encounter opener record review_manifest.build reads first: a run carrying it is on the
# clinical-note or batch-shift path, where ADR 0445 ruling 6 requires the manifest and check-offs.
NOTE_PATH_MARKER = "openers.json"


def not_graded(run: Path, submission: str | None) -> str | None:
    """The row's not-graded report for a run it never grades, or None for a run it grades.

    Without ``--submission`` nothing is graded; a run with neither a coding manifest nor an
    encounter opener record is a direct consultation rather than the note path. Neither answer
    reads a record, so it precedes the frozen-grade exemption and every manifest read.
    """
    if submission is None:
        return f"{ROW}: not graded - --submission was not supplied"
    if not any((run.resolve() / name).exists() for name in (MANIFEST, NOTE_PATH_MARKER)):
        return (f"{ROW}: not graded - the run has no coding manifest and no encounter opener "
                "record, so it is a direct consultation rather than the note path")
    return None
