"""Grade the append-only Filed-from line on issue bodies.

The fixed-position parser is shared by the pre-publication hook, the GitHub
event backstop, and the bounded open-ticket sweep.  It never judges whether the
line is true.  The complete boundary belongs to ``NOT_REACHED`` below.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import NamedTuple

from console_codec import require_python_floor, use_utf8
import tracker_branch_scope


FILED_FROM_CUTOFF = datetime(
    2026, 9, 11, 2, 19, 36, tzinfo=timezone.utc
)

NOT_REACHED = (
    (
        "the Filed-from line can be false",
        "The grader checks only the fixed label, position, and preservation; the filing session owns the truth of its text.",
    ),
    (
        "an older origin sentence is not recognized or converted",
        "Free wording cannot be classified mechanically, so a pre-cutoff respec remains responsible for moving or reconstructing it.",
    ),
    (
        "a GitHub event reports only after publication",
        "The workflow backstop can identify a damaged issue body but cannot prevent the revision from reaching GitHub.",
    ),
    (
        "pre-cutoff tickets without a Filed-from line remain outside the sweep",
        "The cutoff deliberately leaves older bodies unchanged until a later respec applies the written migration rule.",
    ),
    (
        "closed tickets remain outside the open-ticket sweep",
        "The bounded sweep reads open issues only and establishes nothing about closed carriers or their retained edit history.",
    ),
    (
        "Filed-from correction form and placement are not graded",
        "The fixed-line comparison preserves the original line but does not recognize, date, or position a later correction to it.",
    ),
)

FILED_FROM = re.compile(r"\*\*Filed from:\*\*[ \t]+\S[^\r\n]*")
SCOPE_PATTERNS = (
    tracker_branch_scope.BRANCH_SCOPE,
    tracker_branch_scope.MAIN_SCOPE,
    tracker_branch_scope.CITED_RECORD_SCOPE,
)


class Grade(NamedTuple):
    rule: str | None
    posture: str
    report: str


class Finding(NamedTuple):
    rule: str
    url: str


class Scan(NamedTuple):
    findings: tuple[Finding, ...]
    report: str
    complete: bool
    records: int
    eligible: int
    unread: int


class OpenedBodyGrade(NamedTuple):
    eligible: bool
    missing: bool
    map_body: bool


def has_map_producer_stamp(body: str) -> bool:
    """Return whether the implementation map's existing predicate accepts the body."""
    # Lazy import avoids implementation_map's existing import of the publish
    # hook, which imports this module.
    from implementation_map import MapError, producer_stamp_problem

    try:
        return producer_stamp_problem(body) is None
    except MapError as error:
        raise ValueError("implementation map producer could not be graded") from error


def fixed_position_line(body: str) -> str | None:
    """Return the Filed-from line only when it occupies its ruled position."""
    offset = 0
    for pattern in SCOPE_PATTERNS:
        match = pattern.match(body)
        if match is not None:
            offset = match.end()
            break
    match = FILED_FROM.match(body, offset)
    return None if match is None else match.group(0)


def grade_publication(
    body: str,
    route: tuple[str, ...] | None,
    *,
    current_body: str | None = None,
) -> Grade:
    """Grade one proposed publication at the issue-body command seam."""
    if route is None:
        return Grade(None, "not-graded", "filed-from: NOT GRADED; no route")
    if route[:1] != ("issue",) or route not in (
        ("issue", "create"),
        ("issue", "edit"),
    ):
        return Grade(None, "not-graded", "filed-from: NOT GRADED; not an issue body write")
    if has_map_producer_stamp(body):
        return Grade(None, "not-graded", "filed-from: NOT GRADED; implementation map producer stamp")
    if route == ("issue", "create") and fixed_position_line(body) is None:
        return Grade(
            "filed-from:create",
            "deny",
            "deny: filed-from:create: issue body lacks a Filed-from line at the fixed position",
        )
    if route == ("issue", "edit"):
        if current_body is None:
            return Grade(
                None,
                "not-graded",
                "filed-from: NOT GRADED; current issue body was not read",
            )
        current_line = fixed_position_line(current_body)
        if current_line is not None and fixed_position_line(body) != current_line:
            return Grade(
                "filed-from:edit",
                "deny",
                "deny: filed-from:edit: existing Filed-from line was removed, altered, or moved",
            )
    return Grade(
        None,
        "clean",
        "filed-from: 0 fixed-line findings; correction form and placement NOT GRADED",
    )


def _utc_timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} was not text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} was not an ISO timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{label} had no UTC offset")
    return parsed.astimezone(timezone.utc)


def _format_scan(
    findings: tuple[Finding, ...],
    subject: str,
    *,
    complete: bool = True,
    records: int = 1,
    eligible: int = 1,
    unread: int = 0,
    cap_reached: bool = False,
) -> Scan:
    lines = [
        f"Filed-from line over {subject}",
        f"records read {records}",
        f"eligible records {eligible}",
        f"unread records {unread}",
        f"findings {len(findings)}",
    ]
    if complete:
        lines.append("read complete")
    else:
        reasons = []
        if cap_reached:
            reasons.append("read reached its cap")
        if unread:
            reasons.append(f"{unread} record(s) unread")
        lines.append("NOT COMPLETE: " + "; ".join(reasons))
    lines.extend(f"{finding.rule} {finding.url}" for finding in findings)
    return Scan(findings, "\n".join(lines), complete, records, eligible, unread)


def grade_opened_body(created_at: object, body: str) -> OpenedBodyGrade:
    """Classify one issue body independently of an event or harvest."""
    if _utc_timestamp(created_at, "issue creation timestamp") < FILED_FROM_CUTOFF:
        return OpenedBodyGrade(False, False, False)
    if has_map_producer_stamp(body):
        return OpenedBodyGrade(False, False, True)
    return OpenedBodyGrade(True, fixed_position_line(body) is None, False)


def grade_event(document: object, event_name: str) -> Scan:
    """Grade one GitHub issue event without returning either body."""
    if not isinstance(document, dict):
        raise ValueError("GitHub event was not an object")
    if event_name != "issues":
        return _format_scan((), f"{event_name} event (not graded)", eligible=0)
    issue = document.get("issue")
    if not isinstance(issue, dict):
        raise ValueError("GitHub issues event had no issue object")
    body = issue.get("body")
    url = issue.get("html_url")
    if not isinstance(body, str) or not isinstance(url, str):
        raise ValueError("GitHub issue body or URL was not text")
    action = document.get("action")
    findings: tuple[Finding, ...] = ()
    eligible = 0
    if action == "opened":
        opened = grade_opened_body(issue.get("created_at"), body)
        if opened.map_body:
            return _format_scan(
                (), "issues event (implementation map not graded)", eligible=0
            )
        eligible = int(opened.eligible)
        if opened.missing:
            findings = (Finding("filed-from:opened", url),)
    elif action == "edited":
        changes = document.get("changes")
        body_change = changes.get("body") if isinstance(changes, dict) else None
        if body_change is None:
            return _format_scan(
                (), "issues edited event (body not graded)", eligible=0
            )
        if not isinstance(body_change, dict):
            raise ValueError("GitHub issue body change was not an object")
        previous = body_change.get("from")
        if not isinstance(previous, str):
            raise ValueError("GitHub issue previous body was not text")
        previous_line = fixed_position_line(previous)
        eligible = int(previous_line is not None)
        if previous_line is not None and fixed_position_line(body) != previous_line:
            findings = (Finding("filed-from:edited", url),)
    return _format_scan(findings, "issues event", eligible=eligible)


def grade_open_issues(rows: object, *, cap: int) -> Scan:
    """List post-cutoff open issues lacking the fixed-position line."""
    if not isinstance(rows, list):
        raise ValueError("open-ticket harvest was not a JSON array")
    if cap < 1:
        raise ValueError("open-ticket harvest cap must be positive")
    cap_complete = len(rows) < cap
    findings: list[Finding] = []
    eligible = 0
    unread = 0
    for row in rows:
        if not isinstance(row, dict):
            unread += 1
            continue
        if "pull_request" in row:
            continue
        state = row.get("state")
        if not isinstance(state, str):
            unread += 1
            continue
        if state != "OPEN":
            continue
        body = row.get("body")
        url = row.get("url")
        if not isinstance(body, str) or not isinstance(url, str):
            unread += 1
            continue
        try:
            opened = grade_opened_body(row.get("createdAt"), body)
        except ValueError:
            unread += 1
            continue
        eligible += int(opened.eligible)
        if opened.missing:
            findings.append(Finding("filed-from:sweep", url))
    complete = cap_complete and unread == 0
    return _format_scan(
        tuple(findings),
        "open issues",
        complete=complete,
        records=len(rows),
        eligible=eligible,
        unread=unread,
        cap_reached=not cap_complete,
    )


USAGE = (
    "usage: tracker_filed_from.py --github-event <event.json> --event-name "
    "<name> | --harvest <open-issues.json|-> --cap <count>"
)


def main(argv: list[str] | None = None, *, stdin=None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    event_mode = "--github-event" in arguments or "--event-name" in arguments
    harvest_mode = "--harvest" in arguments or "--cap" in arguments
    if event_mode == harvest_mode or len(arguments) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        if event_mode:
            if (
                arguments.count("--github-event") != 1
                or arguments.count("--event-name") != 1
            ):
                raise ValueError("event flags must appear once together")
            path = Path(arguments[arguments.index("--github-event") + 1])
            event_name = arguments[arguments.index("--event-name") + 1]
            document = json.loads(path.read_text(encoding="utf-8"))
            scan = grade_event(document, event_name)
        else:
            if (
                arguments.count("--harvest") != 1
                or arguments.count("--cap") != 1
            ):
                raise ValueError("harvest flags must appear once together")
            source = arguments[arguments.index("--harvest") + 1]
            cap = int(arguments[arguments.index("--cap") + 1])
            if source == "-":
                document = json.load(sys.stdin if stdin is None else stdin)
            else:
                document = json.loads(Path(source).read_text(encoding="utf-8"))
            scan = grade_open_issues(document, cap=cap)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"Filed-from line NOT GRADED: {type(error).__name__}", file=sys.stderr)
        return 2
    print(scan.report)
    if not scan.complete:
        return 2
    return 1 if scan.findings else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
