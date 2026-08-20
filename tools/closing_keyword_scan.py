"""Report GitHub closing keywords that can settle a ticket by accident.

GitHub scans commit messages, pull request titles and bodies, and merge commit
messages. Quoting a phrase does not make it inert. This command therefore
grades artifact text, not prose intent, and reports every binding except the
repo's one deliberate whole-ticket form on a line by itself::

    Closes #123

Usage::

    python tools/closing_keyword_scan.py COMMIT_EDITMSG
    gh pr view 123 --json title,body,commits |
        python tools/closing_keyword_scan.py --github-json -

Exit 0 is clean, 1 means a hazardous binding was found, and 2 means the input
could not be graded. The hook and CI callers are advisory by repository ruling;
the non-zero status makes the command usable without changing that posture.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

from console_codec import use_utf8


# A Markdown list or a few words of prose can sit between the closing verb and
# the reference. Stop at a sentence boundary, not at a source line: a false
# negative settles a ticket; a false positive asks a person to reword one
# sentence. GitHub itself is the final parser, so this is deliberately the
# conservative preflight grammar recorded by issue #183's live instances.
BINDING = re.compile(
    r"\b(?P<keyword>close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
    r"(?P<between>[^.!?]*?)"
    r"#(?P<ticket>[0-9]+)\b",
    re.IGNORECASE,
)

DELIBERATE = re.compile(r"(?m)^[ \t]*Closes[ \t]+#[0-9]+[ \t\r]*$")
FENCE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})")


class Finding(NamedTuple):
    source: str
    line: int
    ticket: int
    keyword: str


def _fenced_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    opened_at = None
    marker = ""
    offset = 0
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if opened_at is None and match:
            opened_at = offset
            marker = match.group("fence")
        elif opened_at is not None and match:
            candidate = match.group("fence")
            if candidate[0] == marker[0] and len(candidate) >= len(marker):
                spans.append((opened_at, offset + len(line)))
                opened_at, marker = None, ""
        offset += len(line)
    if opened_at is not None:
        spans.append((opened_at, len(text)))
    return spans


def _deliberate_spans(text: str) -> list[tuple[int, int]]:
    fenced = _fenced_spans(text)
    return [
        match.span()
        for match in DELIBERATE.finditer(text)
        if not any(start <= match.start() < end for start, end in fenced)
    ]


def scan_text(text: str, source: str) -> list[Finding]:
    allowed = _deliberate_spans(text)
    findings = []
    for match in BINDING.finditer(text):
        if any(start <= match.start() and match.end() <= end for start, end in allowed):
            continue
        findings.append(
            Finding(
                source=source,
                line=text.count("\n", 0, match.start()) + 1,
                ticket=int(match.group("ticket")),
                keyword=match.group("keyword"),
            )
        )
    return findings


def scan_github_document(document: Any) -> list[Finding]:
    if not isinstance(document, dict):
        raise ValueError("GitHub JSON must be an object")

    def text_field(record: dict[str, Any], field: str, source: str) -> str:
        value = record.get(field, "")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"GitHub JSON field {source!r} must be text")
        return value or ""

    findings = []
    for field in ("title", "body"):
        findings.extend(scan_text(text_field(document, field, field), field))

    commits = document.get("commits", [])
    if commits is None:
        commits = []
    if not isinstance(commits, list):
        raise ValueError("GitHub JSON field 'commits' must be a list")
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            raise ValueError(f"GitHub JSON commits[{index}] must be an object")
        headline = text_field(
            commit, "messageHeadline", f"commits[{index}].messageHeadline"
        )
        body = text_field(commit, "messageBody", f"commits[{index}].messageBody")
        message = headline + ("\n\n" + body if body else "")
        findings.extend(scan_text(message, f"commits[{index}]"))
    return findings


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _render(findings: list[Finding], quiet: bool) -> None:
    for finding in findings:
        print(
            f"closing-keyword-scan: {finding.source}:{finding.line}: "
            f"{finding.keyword!r} binds #{finding.ticket}; reword it, or use "
            f"'Closes #{finding.ticket}' alone on a line only when the whole "
            "ticket is done."
        )
    if not findings and not quiet:
        print("closing-keyword-scan: no hazardous GitHub closing keyword found.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report GitHub closing keywords that can settle a ticket by accident."
    )
    parser.add_argument("paths", nargs="*", help="UTF-8 text files, or - for stdin")
    parser.add_argument(
        "--github-json",
        metavar="PATH",
        help="scan gh pr view --json title,body,commits output; use - for stdin",
    )
    parser.add_argument("--quiet", action="store_true", help="print nothing when clean")
    args = parser.parse_args(argv)

    if args.github_json and args.paths:
        parser.error("paths cannot be combined with --github-json")
    if not args.github_json and not args.paths:
        parser.error("supply a text path, -, or --github-json PATH")

    try:
        if args.github_json:
            document = json.loads(_read(args.github_json))
            findings = scan_github_document(document)
        else:
            findings = []
            for path in args.paths:
                findings.extend(scan_text(_read(path), path))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"closing-keyword-scan: could not grade input: {exc}", file=sys.stderr)
        return 2

    _render(findings, args.quiet)
    return 1 if findings else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
