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
from pathlib import Path, PurePosixPath
from typing import Any, NamedTuple
from urllib.parse import unquote

from console_codec import use_utf8
import git_paths
import git_ancestry
from tracker_records import TrackerRecord, from_actions_event
from tracker_bodies import prose_outside_code
from tracker_merge_receipt import parse_merge_receipt


BRANCH_SCOPE_BODY = (
    r"\*\*Branch state:\*\*[ \t]+"
    r"`[A-Za-z0-9._/-]+`[ \t]+at[ \t]+`[0-9a-fA-F]{40}`[ \t]+"
    r"is[ \t]+not[ \t]+on[ \t]+`main`[ \t]+as[ \t]+of[ \t]+"
    r"`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
BRANCH_SCOPE = re.compile(r"\A>[ \t]+" + BRANCH_SCOPE_BODY)
BRANCH_SCOPE_WITHOUT_BLOCKQUOTE = re.compile(r"\A" + BRANCH_SCOPE_BODY)
MAIN_SCOPE_BODY = (
    r"\*\*Branch state:\*\*[ \t]+this[ \t]+text[ \t]+rests[ \t]+on[ \t]+"
    r"`main`[ \t]+at[ \t]+`(?P<commit>[0-9a-fA-F]{40})`[ \t]+as[ \t]+of[ \t]+"
    r"`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
MAIN_SCOPE = re.compile(r"\A>[ \t]+" + MAIN_SCOPE_BODY)
MAIN_SCOPE_WITHOUT_BLOCKQUOTE = re.compile(r"\A" + MAIN_SCOPE_BODY)
CITED_RECORD_SCOPE = re.compile(
    r"\A>[ \t]+\*\*Cited record state:\*\*[ \t]+"
    r"`(?P<path>[^`\r\n]+)`[ \t]+is[ \t]+not[ \t]+on[ \t]+`main`[ \t]+"
    r"as[ \t]+of[ \t]+`[0-9]{4}-[0-9]{2}-[0-9]{2}`\.[ \t]*\r?\n"
)
GITHUB_MAIN_PATH = re.compile(
    r"https://github\.com/[^\s/]+/[^\s/]+/(?P<kind>blob|tree|raw)/main/"
    r"(?P<path>[^\s)>'\"`?#]+)(?:[?#][^\s)>'\"`]*)?"
)
RAW_GITHUB_MAIN_PATH = re.compile(
    r"https://raw\.githubusercontent\.com/[^\s/]+/[^\s/]+/main/"
    r"(?P<path>[^\s)>'\"`?#]+)(?:[?#][^\s)>'\"`]*)?"
)
REPO_RELATIVE_MARKDOWN_PATH = re.compile(
    r"\[[^\]\r\n]*\]\("
    r"(?P<path>(?![A-Za-z][A-Za-z0-9+.-]*:|/|#)[^\s)]+)"
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
        "All three accepted qualifiers are record-level and anchored at the first line, so one "
        "record cannot independently date two different branch relationships.",
    ),
    (
        "the default-branch tree read can fail",
        "A failed Git tree read leaves citation resolution not graded; the report names "
        "the missing measurement while unrelated branch-scope rules still run.",
    ),
    (
        "citation extraction truncates punctuation-bearing paths",
        "The citation extractor stops at parentheses, quotes, apostrophes, and backticks, "
        "so a correct citation to a tracked path containing one is reported unresolved.",
    ),
    (
        "a raw literal-percent form can resolve the wrong URL",
        "A raw citation form matching a tracked path containing a literal percent can pass "
        "even when URL decoding points to a different repository path.",
    ),
)

BRANCH_RULES = (
    "branch:repo-relative-link",
    "branch:near-miss",
    "branch:unresolved-path",
    "branch:self-declares-completion",
    "branch:in-flight",
    "branch:blockquote-missing",
    "branch:ancestry-refused",
)


class Verdict(NamedTuple):
    rule: str | None
    ancestry_verified: bool | None
    default_branch_tree_read: bool


class Result(NamedTuple):
    status: int
    report: str
    verdict: Verdict = Verdict(None, None, False)


class CitedPath(NamedTuple):
    kind: str
    path: str


def _citation_prose(body: str) -> str:
    return prose_outside_code(body)


def _cited_main_paths(body: str) -> tuple[CitedPath, ...]:
    prose = _citation_prose(body)
    paths = [
        CitedPath(match.group("kind"), match.group("path").rstrip(".,;:!"))
        for match in GITHUB_MAIN_PATH.finditer(prose)
    ]
    paths.extend(
        CitedPath("raw", match.group("path").rstrip(".,;:!"))
        for match in RAW_GITHUB_MAIN_PATH.finditer(prose)
    )
    return tuple(paths)


def _repo_relative_markdown_paths(body: str) -> tuple[str, ...]:
    prose = _citation_prose(body)
    return tuple(match.group("path") for match in REPO_RELATIVE_MARKDOWN_PATH.finditer(prose))


REPO_ROOT = Path(__file__).resolve().parent.parent


def _default_branch_paths(repo: Path = REPO_ROOT) -> frozenset[str] | None:
    try:
        return frozenset(git_paths.read_path_records(
            repo, "ls-tree", "-r", "-z", "--name-only", "origin/main"
        ))
    except git_paths.GitPathError:
        return None


def _main_ancestry(commit: str) -> bool | None:
    def run_git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], check=False, capture_output=True,
            cwd=Path(__file__).resolve().parent.parent,
            encoding="utf-8", errors="replace",
        )
    return git_ancestry.is_ancestor(commit, "origin/main", run_git=run_git)


def _unresolved_main_paths(
    cited: tuple[CitedPath, ...], tracked: frozenset[str]
) -> tuple[str, ...]:
    directories = {
        parent.as_posix()
        for entry in tracked
        for parent in PurePosixPath(entry).parents
        if parent.as_posix() != "."
    }
    return tuple(
        citation.path
        for citation in cited
        if not any(form in tracked for form in _citation_forms(citation.path))
        and not (
            citation.kind == "tree"
            and any(form in directories for form in _citation_forms(citation.path))
        )
    )


def _citation_forms(path: str) -> tuple[str, ...]:
    decoded = unquote(path, encoding="utf-8", errors="surrogateescape")
    return (path,) if decoded == path else (path, decoded)


def cites_an_unresolved_path(body: str) -> bool:
    cited = _cited_main_paths(body)
    if not cited:
        return False
    tracked = _default_branch_paths()
    if tracked is None:
        return False
    return bool(_unresolved_main_paths(cited, tracked))


def _has_near_miss(path: str, tracked: frozenset[str]) -> bool:
    for form in _citation_forms(path):
        candidate = Path(form)
        stem_head, separator, _ = candidate.name.partition("-")
        if not separator:
            continue
        prefix = f"{candidate.parent.as_posix()}/{stem_head}-"
        if any(entry.startswith(prefix) for entry in tracked):
            return True
    return False


def grade(document: Any, event_name: str, *, remote_fresh: bool = True) -> Result:
    record = from_actions_event(document, event_name, require_container=True)
    if record is None:
        return Result(0, "tracker-branch-scope: event is outside issue text")
    return grade_record(record, remote_fresh=remote_fresh)


def grade_record(record: TrackerRecord, *, remote_fresh: bool = True) -> Result:
    body = record.body
    url = record.url
    pull_request_discussion = record.container == "pull_request" and record.surface != "body"

    cited = _cited_main_paths(body)
    tracked_read = _default_branch_paths() if cited else None
    tree_not_graded = bool(cited) and tracked_read is None
    tree_read = tracked_read is not None
    tracked = frozenset() if tracked_read is None else tracked_read
    unresolved_paths = _unresolved_main_paths(cited, tracked)
    if tree_not_graded:
        unresolved_paths = ()
    unresolved_path = bool(unresolved_paths)
    relative_paths = _repo_relative_markdown_paths(body)

    ancestry_verified: bool | None = None

    def graded(status: int, report: str, rule: str | None = None) -> Result:
        if tree_not_graded:
            report += (
                "; citation path resolution NOT GRADED -- the default-branch "
                "tree was not read"
            )
        return Result(status, report, Verdict(rule, ancestry_verified, tree_read))

    if relative_paths:
        return graded(
            1,
            f"tracker-branch-scope: {url}: repo-relative Markdown link does not "
            "resolve from tracker text; use an absolute blob/main URL",
            "branch:repo-relative-link",
        )
    if any(_has_near_miss(path, tracked) for path in unresolved_paths):
        return graded(
            1,
            f"tracker-branch-scope: {url}: unresolved path has a same-directory "
            "near miss; fix the slug rather than adding a qualifier",
            "branch:near-miss",
        )

    if pull_request_discussion and not unresolved_path:
        return graded(0, "tracker-branch-scope: pull request discussion is outside scope")

    in_flight = (
        record.container == "issue"
        and record.surface != "title"
        and "in flight" in record.labels
    )
    self_declares_completion = (
        record.surface == "comment"
        and not pull_request_discussion
        and DECLARES_COMPLETION.match(body) is not None
    )
    if not in_flight and not self_declares_completion and not unresolved_path:
        return graded(0, "tracker-branch-scope: record has no branch-state trigger")
    receipt = parse_merge_receipt(body)
    receipt_matches_issue = (
        receipt is not None and receipt.ticket == record.number
    )
    branch_scope = BRANCH_SCOPE.match(body)
    main_scope = MAIN_SCOPE.match(body)
    cited_record_scope = CITED_RECORD_SCOPE.match(body)
    cited_record_scope_matches = (
        cited_record_scope is not None
        and (
            not unresolved_path
            or cited_record_scope.group("path") in unresolved_paths
        )
    )
    if main_scope is not None:
        ancestry = _main_ancestry(main_scope.group("commit"))
        ancestry_verified = ancestry is not None
        if ancestry is not True and not remote_fresh:
            ancestry_verified = False
            return graded(
                0,
                f"tracker-branch-scope: {url}: explicit main branch state present; "
                "ancestry could not be verified",
            )
        if ancestry is False:
            return graded(
                1,
                f"tracker-branch-scope: {url}: claimed main commit is not an "
                "ancestor of origin/main",
                "branch:ancestry-refused",
            )
        if ancestry is None:
            return graded(
                1,
                f"tracker-branch-scope: {url}: positive Branch state refused; "
                "ancestry could not be verified",
                "branch:ancestry-refused",
            )
    explicit_scope = (
        branch_scope is not None
        or main_scope is not None
        or cited_record_scope_matches
    )
    if explicit_scope or (not unresolved_path and receipt_matches_issue):
        return graded(0, f"tracker-branch-scope: {url}: explicit branch state present")

    if (
        BRANCH_SCOPE_WITHOUT_BLOCKQUOTE.match(body) is not None
        or MAIN_SCOPE_WITHOUT_BLOCKQUOTE.match(body) is not None
    ):
        return graded(
            1,
            f"tracker-branch-scope: {url}: Branch state blockquote marker is missing",
            "branch:blockquote-missing",
        )

    if unresolved_path:
        reason = "text cites an unresolved path on the default branch"
        rule = "branch:unresolved-path"
    elif self_declares_completion:
        reason = "text self-declares completion"
        rule = "branch:self-declares-completion"
    else:
        reason = "the issue is labeled 'in flight'"
        rule = "branch:in-flight"
    if body:
        return graded(
            1,
            f"tracker-branch-scope: {url}: missing Branch state at the start of "
            f"text because {reason}", rule,
        )
    return graded(1, f"tracker-branch-scope: {url}: missing body while {reason}", rule)


def _read(path: str) -> Any:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def _read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def grade_text(body: str) -> Result:
    return grade_record(TrackerRecord(body, "draft text", 0, (), "issue", "comment"))


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
