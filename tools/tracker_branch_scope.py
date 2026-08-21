"""Require dated provenance on issue text published during branch work.

The ``in flight`` label is the mechanically visible boundary. An issue body or
comment published while that label is present starts with the exact scope form
documented in ``docs/agents/issue-tracker.md``. The command reads one GitHub
event, opens no socket, and never prints the record body.

Exit 0 means the record is scoped or outside this check, 1 means an in-flight
record lacks the scope, and 2 means the event could not be graded.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

from console_codec import use_utf8
from tracker_merge_receipt import parse_merge_receipt


BRANCH_SCOPE = re.compile(
    r"\A>[ \t]+\*\*Branch state:\*\*[ \t]+"
    r"`[A-Za-z0-9._/-]+`[ \t]+at[ \t]+`[0-9a-fA-F]{40}`[ \t]+"
    r"is[ \t]+not[ \t]+on[ \t]+`main`[ \t]+as[ \t]+of[ \t]+"
    r"`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
DECLARES_COMPLETION = re.compile(
    r"\A(?:\*\*)?(?:Ruled and built|Implemented locally|Built on|Landed on)\b",
    re.IGNORECASE,
)


class Result(NamedTuple):
    status: int
    report: str


def grade(document: Any, event_name: str) -> Result:
    if not isinstance(document, dict):
        raise ValueError("GitHub event JSON must be an object")
    if event_name not in ("issues", "issue_comment"):
        return Result(0, "tracker-branch-scope: event is outside issue text")

    issue = document.get("issue")
    if not isinstance(issue, dict):
        raise ValueError("GitHub event has no issue object")
    if "pull_request" in issue:
        return Result(0, "tracker-branch-scope: pull request discussion is outside scope")

    if event_name == "issues":
        record = issue
    else:
        record = document.get("comment")
        if not isinstance(record, dict):
            raise ValueError("GitHub issue_comment event has no comment object")
    body = record.get("body")
    url = record.get("html_url") or issue.get("html_url") or "unknown record"
    if not isinstance(body, str):
        body = ""

    labels = issue.get("labels", [])
    if not isinstance(labels, list) or any(not isinstance(row, dict) for row in labels):
        raise ValueError("GitHub issue labels must be objects")
    in_flight = "in flight" in {row.get("name") for row in labels}
    self_declares_completion = (
        event_name == "issue_comment" and DECLARES_COMPLETION.match(body) is not None
    )
    if not in_flight and not self_declares_completion:
        return Result(0, "tracker-branch-scope: record has no branch-state trigger")
    receipt = parse_merge_receipt(body)
    receipt_matches_issue = (
        receipt is not None and receipt.ticket == issue.get("number")
    )
    if BRANCH_SCOPE.match(body) or receipt_matches_issue:
        return Result(0, f"tracker-branch-scope: {url}: explicit branch state present")

    if self_declares_completion:
        reason = "text self-declares completion"
    else:
        reason = "the issue is labeled 'in flight'"
    if body:
        return Result(
            1,
            f"tracker-branch-scope: {url}: missing Branch state at the start of "
            f"text because {reason}",
        )
    return Result(1, f"tracker-branch-scope: {url}: missing body while {reason}")


def _read(path: str) -> Any:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grade branch scope on a GitHub event.")
    parser.add_argument("--github-event", required=True, metavar="PATH")
    parser.add_argument("--event-name", required=True)
    args = parser.parse_args(argv)

    try:
        result = grade(_read(args.github_event), args.event_name)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"tracker-branch-scope: could not grade input: {exc}", file=sys.stderr)
        return 2
    print(result.report)
    return result.status


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
