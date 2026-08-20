"""Plan immutable ticket receipts for a pull request merged into ``main``.

Tracker prose written from a branch is true in one tree and read from another.
This command does not guess which prose is an assertion. It reads the explicit
ticket bindings the maintainer already puts on their own lines in a pull request
and emits one JSON object per ticket for the workflow to publish::

    Closes #290
    Part of #298
    Implements #300's lead 2

Usage::

    gh pr view 401 --json number,url,title,body,baseRefName,mergedAt,mergeCommit,commits |
        python tools/tracker_merge_receipt.py -

Exit 0 means the merged pull request was graded, including a valid empty plan.
Exit 2 means the input could not establish a completed merge into ``main``.
The command opens no socket and mutates nothing; its JSON-lines output is the
bounded plan consumed by ``.github/workflows/tracker.yml``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

from console_codec import use_utf8


REFERENCE = re.compile(
    r"(?im)^[ \t]*(?:"
    r"Closes[ \t]+#(?P<closes>[0-9]+)|"
    r"Part[ \t]+of[ \t]+#(?P<part>[0-9]+)|"
    r"Implements[ \t]+#(?P<implements>[0-9]+)'s[ \t]+lead[ \t]+"
    r"(?P<lead>[0-9]+)"
    r")[ \t\r]*$"
)
FULL_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
ISO_DAY = re.compile(r"^(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})T")


class Receipt(NamedTuple):
    ticket: int
    body: str


class Binding(NamedTuple):
    ticket: int
    claim: str


def _text(record: dict[str, Any], field: str, source: str) -> str:
    value = record.get(field, "")
    if value is not None and not isinstance(value, str):
        raise ValueError(f"GitHub JSON field {source!r} must be text")
    return value or ""


def _artifact_texts(document: dict[str, Any]) -> list[str]:
    texts = [_text(document, "body", "body")]
    commits = document.get("commits", [])
    if commits is None:
        commits = []
    if not isinstance(commits, list):
        raise ValueError("GitHub JSON field 'commits' must be a list")
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            raise ValueError(f"GitHub JSON commits[{index}] must be an object")
        texts.append(
            _text(commit, "messageHeadline", f"commits[{index}].messageHeadline")
        )
        texts.append(_text(commit, "messageBody", f"commits[{index}].messageBody"))
    return texts


def _bindings(document: dict[str, Any]) -> list[Binding]:
    found = set()
    for text in _artifact_texts(document):
        for match in REFERENCE.finditer(text):
            if match.group("closes"):
                ticket = int(match.group("closes"))
                claim = f"Closes #{ticket}"
            elif match.group("part"):
                ticket = int(match.group("part"))
                claim = f"Part of #{ticket}"
            else:
                ticket = int(match.group("implements"))
                claim = f"Implements #{ticket}'s lead {int(match.group('lead'))}"
            found.add(Binding(ticket, claim))
    return sorted(found)


def plan_receipts(document: Any) -> list[Receipt]:
    if not isinstance(document, dict):
        raise ValueError("GitHub JSON must be an object")
    if document.get("baseRefName") != "main":
        raise ValueError("pull request base branch is not 'main'")

    merged_at = document.get("mergedAt")
    if not isinstance(merged_at, str) or not (day_match := ISO_DAY.match(merged_at)):
        raise ValueError("pull request is not merged with a dated merge event")

    merge_commit = document.get("mergeCommit")
    if not isinstance(merge_commit, dict):
        raise ValueError("pull request has no full merge commit")
    sha = merge_commit.get("oid")
    if not isinstance(sha, str) or not FULL_SHA.fullmatch(sha):
        raise ValueError("pull request has no full merge commit")

    number = document.get("number")
    url = document.get("url")
    if not isinstance(number, int) or number < 1:
        raise ValueError("pull request number must be a positive integer")
    if not isinstance(url, str) or not url.startswith("https://github.com/"):
        raise ValueError("pull request URL must be a GitHub HTTPS URL")

    day = day_match.group("day")
    rows = []
    for binding in _bindings(document):
        body = (
            f"Merged into `main` by [PR #{number}]({url}) at `{sha}` on {day}. "
            f"Merge claim: `{binding.claim}`. This immutable merge receipt "
            "establishes that pull request's state; it does not make later names "
            "or claims current."
        )
        rows.append(Receipt(binding.ticket, body))
    return rows


def _read(path: str) -> Any:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan ticket receipts for a pull request merged into main."
    )
    parser.add_argument("path", help="gh pr view JSON, or - for stdin")
    args = parser.parse_args(argv)

    try:
        rows = plan_receipts(_read(args.path))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"tracker-merge-receipt: could not grade input: {exc}", file=sys.stderr)
        return 2

    for row in rows:
        print(json.dumps(row._asdict(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
