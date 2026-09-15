"""Dispatch every check that applies to one changed GitHub tracker record.

The command is the shared policy seam for ``tracker.yml`` and for merge-receipt
publication.  It writes one GitHub step-summary section per selected check.
The PHI shape layer is advisory; every other selected check refuses on a
nonzero exit.

Usage::

    python tools/tracker_event_checks.py --github-event event.json \
        --event-name issue_comment
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from console_codec import require_python_floor, use_utf8


TOOLS = Path(__file__).resolve().parent
EVENT_ACTIONS = {
    "issues": frozenset(("opened", "edited", "labeled")),
    "issue_comment": frozenset(("created", "edited")),
    "pull_request_target": frozenset(("opened", "edited", "closed")),
    "pull_request_review": frozenset(("submitted", "edited")),
    "pull_request_review_comment": frozenset(("created", "edited")),
}
EVENT_NAMES = tuple(EVENT_ACTIONS)

NOT_REACHED = (
    (
        "a future workflow-token writer is not discovered",
        "The command grades an event deliberately supplied to it and does not enumerate "
        "workflow-token writes or prove that every writer calls it.",
    ),
    (
        "the PHI corpus layer is unavailable on a runner",
        "The event command runs the PHI shape layer with the corpus absence declared; "
        "patient-name evidence remains outside a GitHub runner.",
    ),
    (
        "a clean event grade is not a correct tracker claim",
        "The selected checks grade their declared mechanical properties and do not "
        "establish that a record's prose is true or complete.",
    ),
)


@dataclass(frozen=True)
class Check:
    module: str
    heading: str
    refusing: bool = True
    extra_args: tuple[str, ...] = ()


ALL_CHECKS = (
    Check(
        "tracker_scan",
        "Tracker PHI shape layer",
        refusing=False,
        extra_args=("--allow-no-corpus",),
    ),
    Check("tracker_branch_scope", "Tracker branch scope"),
    Check("tracker_bodies", "Tracker body integrity"),
    Check("tracker_coordinates", "Tracker coordinate accompaniment"),
    Check("tracker_measurements", "Publication measurement base"),
    Check("tracker_filed_from", "Tracker Filed-from line"),
    Check("map_scan", "Implementation map producer stamp"),
)
PHI, BRANCH, BODY, COORDINATES, MEASUREMENTS, FILED_FROM, MAP = ALL_CHECKS


def _body_changed(document: dict[str, Any]) -> bool:
    changes = document.get("changes")
    return isinstance(changes, dict) and changes.get("body") is not None


def _title_changed(document: dict[str, Any]) -> bool:
    changes = document.get("changes")
    return isinstance(changes, dict) and changes.get("title") is not None


def _has_changed_record(document: dict[str, Any], event_name: str) -> bool:
    action = document.get("action")
    if action not in EVENT_ACTIONS.get(event_name, ()) or action == "closed":
        return False
    if event_name == "pull_request_review":
        review = document.get("review")
        if not isinstance(review, dict) or review.get("body") in (None, ""):
            return False
    if action == "edited" and not (_title_changed(document) or _body_changed(document)):
        return False
    return True


def select_checks(document: Any, event_name: str) -> tuple[Check, ...]:
    """Return the checks selected by the pre-#1146 ``changed-record`` job."""
    if not isinstance(document, dict):
        raise ValueError("GitHub event JSON must be an object")
    if not _has_changed_record(document, event_name):
        return ()

    selected = [PHI, BRANCH]
    action = document.get("action")
    changed_body = _body_changed(document)
    body_event = action in ("opened", "created", "submitted") or (
        action == "edited" and changed_body
    )
    if body_event:
        selected.extend((BODY, COORDINATES, MEASUREMENTS))
    if event_name == "issues" and (
        action == "opened" or (action == "edited" and changed_body)
    ):
        selected.append(FILED_FROM)
    issue = document.get("issue")
    if (
        event_name == "issues"
        and action == "edited"
        and changed_body
        and isinstance(issue, dict)
        and issue.get("number") == 596
    ):
        selected.append(MAP)
    return tuple(selected)


def _status_label(returncode: int) -> str:
    return {0: "CLEAN", 1: "FINDING", 2: "DID NOT SCAN"}.get(
        returncode, f"EXIT {returncode}"
    )


def _summary_section(heading: str, returncode: int, report: str) -> str:
    return (
        f"### {heading}: {_status_label(returncode)}\n\n"
        f"```\n{report.rstrip()}\n```\n"
    )


def _append_summary(path: Path | None, section: str) -> None:
    if path is None:
        return
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(section)


def run_selected(
    event_path: Path,
    event_name: str,
    selected: Sequence[Check],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    summary_path: Path | None = None,
) -> int:
    """Run every selected check and return the aggregate refusing status."""
    status = 0
    for check in selected:
        command = [
            sys.executable,
            str(TOOLS / f"{check.module}.py"),
            "--github-event",
            str(event_path),
            "--event-name",
            event_name,
            *check.extra_args,
        ]
        completed = runner(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        report = "\n".join(
            part.rstrip() for part in (completed.stdout, completed.stderr) if part.rstrip()
        )
        section = _summary_section(check.heading, completed.returncode, report)
        print(section, end="")
        _append_summary(summary_path, section)
        if check.refusing and completed.returncode != 0 and status == 0:
            status = completed.returncode
    return status


def grade_event_path(
    event_path: Path,
    event_name: str,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    summary_path: Path | None = None,
) -> int:
    document = json.loads(event_path.read_text(encoding="utf-8-sig"))
    return run_selected(
        event_path,
        event_name,
        select_checks(document, event_name),
        runner=runner,
        summary_path=summary_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the checks selected for one GitHub tracker event."
    )
    parser.add_argument("--github-event", type=Path, required=True)
    parser.add_argument("--event-name", choices=EVENT_NAMES, required=True)
    args = parser.parse_args(argv)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    try:
        return grade_event_path(
            args.github_event,
            args.event_name,
            summary_path=Path(summary) if summary else None,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"tracker-event-checks: could not grade input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
