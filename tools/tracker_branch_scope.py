"""Require dated main-branch provenance on published tracker text.

The ``in flight`` label is the mechanically visible boundary. An issue body or
comment published while that label is present starts with the exact scope form
documented in ``docs/agents/issue-tracker.md``. A citation to a path absent from
the checked-out default branch is a second trigger on every tracker publication
surface. The command opens no socket and never prints the record body.

Exit 0 means the record is scoped or outside this check, 1 means the published
record violates a branch-state or path-citation rule, and 2 means the event
could not be graded.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

from console_codec import use_utf8
from tracker_bodies import CODE_SPAN, FENCED_CODE
from tracker_merge_receipt import parse_merge_receipt


BRANCH_SCOPE = re.compile(
    r"\A>[ \t]+\*\*Branch state:\*\*[ \t]+"
    r"`[A-Za-z0-9._/-]+`[ \t]+at[ \t]+`[0-9a-fA-F]{40}`[ \t]+"
    r"is[ \t]+not[ \t]+on[ \t]+`main`[ \t]+as[ \t]+of[ \t]+"
    r"`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
CITED_RECORD_SCOPE = re.compile(
    r"\A>[ \t]+\*\*Cited record state:\*\*[ \t]+"
    r"`[^`\r\n]+`[ \t]+is[ \t]+not[ \t]+on[ \t]+`main`[ \t]+"
    r"as[ \t]+of[ \t]+`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
GITHUB_MAIN_PATH = re.compile(
    r"https://github\.com/[^\s/]+/[^\s/]+/(?:blob|tree|raw)/main/"
    r"(?P<path>[^\s)>'\"`?#]+)(?:[?#][^\s)>'\"`]*)?"
)
RAW_GITHUB_MAIN_PATH = re.compile(
    r"https://raw\.githubusercontent\.com/[^\s/]+/[^\s/]+/main/"
    r"(?P<path>[^\s)>'\"`?#]+)(?:[?#][^\s)>'\"`]*)?"
)
REPO_RELATIVE_MARKDOWN_PATH = re.compile(
    r"\[[^\]\r\n]*\]\("
    r"(?P<path>(?![A-Za-z][A-Za-z0-9+.-]*:|/|#)[^\s)]+/[^\s)]+)"
    r"(?:[ \t]+[\"'][^\r\n]*[\"'])?\)"
)
DECLARES_COMPLETION = re.compile(
    r"\A(?:\*\*)?(?:Ruled and built|Implemented locally|Built on|Landed on)\b",
    re.IGNORECASE,
)

NOT_REACHED = (
    (
        "publication precedes the check",
        "The workflow grades the GitHub event after the record is published; it is a "
        "backstop and cannot intercept the original write.",
    ),
    (
        "an advisory finding may go unread",
        "The workflow guarantees that the detector ran, while repository settings and "
        "human attention decide whether its red result changes anything.",
    ),
    (
        "code formatting can hide a citation",
        "Fenced code and inline code are deliberately stripped as mentions, so an author "
        "can place a real citation there beyond this detector.",
    ),
    (
        "Branch state is a record-level proxy",
        "The canonical qualifier dates the record's branch and can satisfy a citation "
        "whose actual path belongs to a different unmerged branch.",
    ),
    (
        "a bare record number has no path",
        "Text such as ADR 0042 carries no resolvable repository path and remains a "
        "convention-only citation outside this mechanical check.",
    ),
    (
        "citation coordinates need file contents",
        "A live path paired with a nonexistent ruling or stale line number requires file "
        "contents, while this detector reads only tree membership.",
    ),
    (
        "an undated assertion about a resolved path",
        "A citation that already resolves does not trigger, even when nearby prose falsely "
        "claims that its record is still absent from main.",
    ),
    (
        "the qualifier forms cannot compose",
        "Both accepted qualifiers are record-level and anchored at the first line, so one "
        "record cannot independently date two different branch relationships.",
    ),
)


class Result(NamedTuple):
    status: int
    report: str


def _citation_prose(body: str) -> str:
    return CODE_SPAN.sub(" ", FENCED_CODE.sub(" ", body))


def _cited_main_paths(body: str) -> tuple[str, ...]:
    prose = _citation_prose(body)
    paths = []
    for pattern in (GITHUB_MAIN_PATH, RAW_GITHUB_MAIN_PATH):
        paths.extend(match.group("path").rstrip(".,;:!") for match in pattern.finditer(prose))
    return tuple(paths)


def _repo_relative_markdown_paths(body: str) -> tuple[str, ...]:
    prose = _citation_prose(body)
    return tuple(match.group("path") for match in REPO_RELATIVE_MARKDOWN_PATH.finditer(prose))


def _default_branch_paths() -> frozenset[str]:
    completed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        check=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parent.parent,
        encoding="utf-8",
    )
    return frozenset(completed.stdout.splitlines())


def _unresolved_main_paths(
    cited: tuple[str, ...], tracked: frozenset[str]
) -> tuple[str, ...]:
    return tuple(path for path in cited if path not in tracked)


def cites_an_unresolved_path(body: str) -> bool:
    cited = _cited_main_paths(body)
    if not cited:
        return False
    tracked = _default_branch_paths()
    return any(path not in tracked for path in cited)


def _has_near_miss(path: str, tracked: frozenset[str]) -> bool:
    candidate = Path(path)
    stem_head, separator, _ = candidate.name.partition("-")
    if not separator:
        return False
    prefix = f"{candidate.parent.as_posix()}/{stem_head}-"
    return any(entry.startswith(prefix) for entry in tracked)


def grade(document: Any, event_name: str) -> Result:
    if not isinstance(document, dict):
        raise ValueError("GitHub event JSON must be an object")
    if event_name in ("issues", "issue_comment"):
        issue = document.get("issue")
        if not isinstance(issue, dict):
            raise ValueError("GitHub event has no issue object")
        pull_request_discussion = "pull_request" in issue
        if event_name == "issues":
            record = issue
        else:
            record = document.get("comment")
            if not isinstance(record, dict):
                raise ValueError("GitHub issue_comment event has no comment object")
    elif event_name in (
        "pull_request_target",
        "pull_request_review",
        "pull_request_review_comment",
    ):
        issue = document.get("pull_request")
        if not isinstance(issue, dict):
            raise ValueError("GitHub pull request event has no pull_request object")
        pull_request_discussion = False
        key = {
            "pull_request_target": "pull_request",
            "pull_request_review": "review",
            "pull_request_review_comment": "comment",
        }[event_name]
        record = document.get(key)
        if not isinstance(record, dict):
            raise ValueError(f"GitHub {event_name} event has no {key} object")
    else:
        return Result(0, "tracker-branch-scope: event is outside issue text")
    body = record.get("body")
    url = record.get("html_url") or issue.get("html_url") or "unknown record"
    if not isinstance(body, str):
        body = ""

    cited = _cited_main_paths(body)
    tracked = _default_branch_paths() if cited else frozenset()
    unresolved_paths = _unresolved_main_paths(cited, tracked)
    unresolved_path = bool(unresolved_paths)
    relative_paths = _repo_relative_markdown_paths(body)

    if relative_paths:
        return Result(
            1,
            f"tracker-branch-scope: {url}: repo-relative Markdown link does not "
            "resolve from tracker text; use an absolute blob/main URL",
        )
    if any(_has_near_miss(path, tracked) for path in unresolved_paths):
        return Result(
            1,
            f"tracker-branch-scope: {url}: unresolved path has a same-directory "
            "near miss; fix the slug rather than adding a qualifier",
        )

    if pull_request_discussion and not unresolved_path:
        return Result(0, "tracker-branch-scope: pull request discussion is outside scope")

    labels = issue.get("labels", [])
    if not isinstance(labels, list) or any(not isinstance(row, dict) for row in labels):
        raise ValueError("GitHub issue labels must be objects")
    in_flight = (
        event_name in ("issues", "issue_comment")
        and not pull_request_discussion
        and "in flight" in {row.get("name") for row in labels}
    )
    self_declares_completion = (
        event_name == "issue_comment"
        and not pull_request_discussion
        and DECLARES_COMPLETION.match(body) is not None
    )
    if not in_flight and not self_declares_completion and not unresolved_path:
        return Result(0, "tracker-branch-scope: record has no branch-state trigger")
    receipt = parse_merge_receipt(body)
    receipt_matches_issue = (
        receipt is not None and receipt.ticket == issue.get("number")
    )
    if BRANCH_SCOPE.match(body) or CITED_RECORD_SCOPE.match(body) or receipt_matches_issue:
        return Result(0, f"tracker-branch-scope: {url}: explicit branch state present")

    if unresolved_path:
        reason = "text cites an unresolved path on the default branch"
    elif self_declares_completion:
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


def _read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def grade_text(body: str) -> Result:
    return grade(
        {
            "issue": {"number": 0, "labels": []},
            "comment": {"body": body, "html_url": "draft text"},
        },
        "issue_comment",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grade branch scope on a GitHub event.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--github-event", metavar="PATH")
    source.add_argument("--text", metavar="PATH")
    parser.add_argument("--event-name")
    args = parser.parse_args(argv)

    try:
        if args.github_event is not None:
            if not args.event_name:
                raise ValueError("--event-name is required with --github-event")
            result = grade(_read(args.github_event), args.event_name)
        else:
            result = grade_text(_read_text(args.text))
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
        ValueError,
    ) as exc:
        print(f"tracker-branch-scope: could not grade input: {exc}", file=sys.stderr)
        return 2
    print(result.report)
    return result.status


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
