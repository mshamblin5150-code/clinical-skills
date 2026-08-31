"""Inspect tracker text immediately before a ``gh`` publication.

The command is a Claude Code ``PreToolUse`` hook: it reads one hook payload as
JSON from stdin and writes one hook response as JSON to stdout. It never prints
the text it scans. Counts, rule names, and the field to edit are the complete
reporting surface.
"""

from __future__ import annotations

from collections import Counter
from datetime import date as CalendarDate
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import NamedTuple

import phi_scan
import tracker_branch_scope
from console_codec import use_utf8


PUBLISH_ROUTES = (
    ("issue", "create"),
    ("issue", "comment"),
    ("issue", "edit"),
    ("issue", "close"),
    ("pr", "create"),
    ("pr", "comment"),
    ("pr", "edit"),
    ("pr", "review"),
    ("api",),
)
PUBLISH_MARKER = phi_scan.TRACKER_PUBLISH_MARKER


class Publication(NamedTuple):
    field: str
    text: str
    source: str = "inline"


class Unreadable(NamedTuple):
    field: str
    kind: str
    source: str


class Extraction(NamedTuple):
    route: tuple[str, ...] | None
    number: int | None
    publications: tuple[Publication, ...]
    unreadable: tuple[Unreadable, ...]
    grade_route: tuple[str, ...] | None = None


class Finding(NamedTuple):
    rule: str
    count: int
    field: str
    posture: str


class Analysis(NamedTuple):
    findings: tuple[Finding, ...]
    report: str


INLINE_FLAGS = {
    "--title": "title",
    "-t": "title",
    "--body": "body",
    "-b": "body",
    "--comment": "body",
}
FILE_FLAGS = {"--body-file": "body", "-F": "body"}
API_VALUE_FLAGS = {"-f", "--raw-field", "-F", "--field"}
API_RECORD_NUMBER = re.compile(r"/(?:issues|pulls)/(?P<number>[0-9]+)(?:/|\Z)")
RAW_PUBLISH_ROUTE = re.compile(
    r"(?:\A|[;&|]\s*)gh\s+(?:(api)\b|(issue|pr)\s+"
    r"(create|comment|edit|close|review)\b)"
)
PLAIN_ASSIGNMENT = re.compile(
    r"(?:\A|[;&|\n]\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)="
    r"(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<bare>[^\s;&|]+))"
)
VARIABLE = re.compile(
    r"\A\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
    r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))\Z"
)
HEREDOC = re.compile(
    r"<<-?\s*['\"]?(?P<tag>[A-Za-z_][A-Za-z0-9_]*)['\"]?[ \t]*\r?\n"
    r"(?P<body>.*?)\r?\n(?P=tag)(?:\r?\n|\Z)",
    re.DOTALL,
)


def _assignment_value(match: re.Match[str]) -> str:
    return next(
        part
        for part in (match.group("double"), match.group("single"), match.group("bare"))
        if part is not None
    )


def _plain_assignments(command: str) -> dict[str, str]:
    return {
        match.group("name"): value
        for match in PLAIN_ASSIGNMENT.finditer(command)
        if "$(" not in (value := _assignment_value(match)) and "`" not in value
    }


def _substitution_assignments(command: str) -> frozenset[str]:
    return frozenset(
        match.group("name")
        for match in PLAIN_ASSIGNMENT.finditer(command)
        if "$(" in _assignment_value(match) or "`" in _assignment_value(match)
    )


def _written_before_publish(command: str, source: str) -> bool:
    publish_at = command.find("gh ")
    if publish_at < 0:
        return False
    prefix = command[:publish_at]
    return re.search(r">\s*['\"]?" + re.escape(source) + r"['\"]?", prefix) is not None


def _resolve_plain_value(
    field: str,
    value: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> Publication | Unreadable:
    variable = VARIABLE.match(value)
    if variable is None:
        return Publication(field, value)
    name = variable.group("braced") or variable.group("plain")
    if name in assignments:
        return Publication(field, assignments[name])
    kind = "command-substitution" if name in substitutions else "external-variable"
    return Unreadable(field, kind, value)


def _raw_publish_route(command: str) -> tuple[str, ...] | None:
    match = RAW_PUBLISH_ROUTE.search(command)
    if match is None:
        return None
    if match.group(1) == "api":
        return ("api",)
    return (match.group(2), match.group(3))


def _api_grade_route(arguments: list[str]) -> tuple[str, ...]:
    endpoint = next(
        (
            token
            for token in arguments
            if re.search(r"/(?:issues|pulls)/[0-9]+(?:/|\Z)", token)
        ),
        "",
    )
    if re.search(r"/issues/[0-9]+/comments(?:\Z|\?)", endpoint):
        return ("issue", "comment")
    if re.search(r"/pulls/[0-9]+/reviews(?:\Z|\?)", endpoint):
        return ("pr", "review")
    if re.search(r"/pulls/[0-9]+(?:\Z|\?)", endpoint):
        return ("pr", "edit")
    if re.search(r"/issues/[0-9]+(?:\Z|\?)", endpoint):
        return ("issue", "edit")
    return ("issue", "comment")


def _record_number(route: tuple[str, ...], arguments: list[str]) -> int | None:
    if route == ("api",):
        match = next(
            (
                found
                for token in arguments
                if (found := API_RECORD_NUMBER.search(token)) is not None
            ),
            None,
        )
        return None if match is None else int(match.group("number"))
    if route in (("issue", "create"), ("pr", "create")) or not arguments:
        return None
    target = arguments[0]
    if target.isdecimal():
        return int(target)
    match = API_RECORD_NUMBER.search(target)
    return None if match is None else int(match.group("number"))


def _read_file_field(
    field: str,
    source: str,
    command: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> Publication | Unreadable:
    variable = VARIABLE.match(source)
    if variable is not None:
        name = variable.group("braced") or variable.group("plain")
        if name not in assignments:
            kind = "command-substitution" if name in substitutions else "external-variable"
            return Unreadable(field, kind, source)
        source = assignments[name]
    if source == "-":
        heredoc = HEREDOC.search(command)
        if heredoc is None:
            return Unreadable(field, "pipe", source)
        return Publication(field, heredoc.group("body"), "inline heredoc")
    try:
        text = Path(source).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        kind = (
            "written-before-publish"
            if _written_before_publish(command, source)
            else "missing-file"
        )
        return Unreadable(field, kind, source)
    return Publication(field, text, source)


def extract(command: str) -> Extraction:
    """Read inline tracker fields from one ``gh`` invocation."""
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        route = _raw_publish_route(command)
        if route is None:
            return Extraction(None, None, (), ())
        unreadable = Unreadable("body", "invalid-command", "inline")
        return Extraction(route, None, (), (unreadable,), route)
    try:
        start = tokens.index("gh")
    except ValueError:
        return Extraction(None, None, (), ())
    tail = tokens[start + 1 :]
    if not tail:
        return Extraction(None, None, (), ())
    route = ("api",) if tail[0] == "api" else tuple(tail[:2])
    if route not in PUBLISH_ROUTES:
        return Extraction(None, None, (), ())
    route_width = len(route)
    arguments = tail[route_width:]
    number = _record_number(route, arguments)
    grade_route = _api_grade_route(arguments) if route == ("api",) else route
    publications: list[Publication] = []
    assignments = _plain_assignments(command)
    substitutions = _substitution_assignments(command)
    index = 0
    while index < len(arguments):
        token = arguments[index]
        body_flag = (
            token in INLINE_FLAGS
            or token in FILE_FLAGS
            or (route == ("api",) and token in API_VALUE_FLAGS)
            or (route == ("api",) and token == "--input")
            or (route == ("issue", "close") and token == "-c")
        )
        if body_flag and index + 1 >= len(arguments):
            unreadable = Unreadable("body", "missing-value", token)
            return Extraction(route, number, tuple(publications), (unreadable,), grade_route)
        if route == ("issue", "close") and token == "-c" and index + 1 < len(arguments):
            read = _resolve_plain_value(
                "body", arguments[index + 1], assignments, substitutions
            )
            if isinstance(read, Unreadable):
                return Extraction(route, number, tuple(publications), (read,), grade_route)
            publications.append(read)
            index += 2
            continue
        if route == ("api",) and token in API_VALUE_FLAGS and index + 1 < len(arguments):
            key, separator, value = arguments[index + 1].partition("=")
            if separator and key in ("body", "title"):
                if value.startswith("@") and token in ("-F", "--field"):
                    read = _read_file_field(
                        key, value[1:], command, assignments, substitutions
                    )
                    if isinstance(read, Unreadable):
                        return Extraction(route, number, tuple(publications), (read,))
                    publications.append(read)
                else:
                    read = _resolve_plain_value(key, value, assignments, substitutions)
                    if isinstance(read, Unreadable):
                        return Extraction(route, number, tuple(publications), (read,), grade_route)
                    publications.append(read)
            index += 2
            continue
        if route == ("api",) and token == "--input" and index + 1 < len(arguments):
            source = arguments[index + 1]
            variable = VARIABLE.match(source)
            if variable is not None:
                name = variable.group("braced") or variable.group("plain")
                if name not in assignments:
                    kind = "command-substitution" if name in substitutions else "external-variable"
                    unreadable = Unreadable("body", kind, source)
                    return Extraction(route, number, tuple(publications), (unreadable,), grade_route)
                source = assignments[name]
            try:
                if source == "-":
                    heredoc = HEREDOC.search(command)
                    if heredoc is None:
                        unreadable = Unreadable("body", "pipe", source)
                        return Extraction(
                            route, number, tuple(publications), (unreadable,)
                        )
                    request_text = heredoc.group("body")
                    source = "inline heredoc"
                else:
                    request_text = Path(source).read_text(encoding="utf-8")
                request = json.loads(request_text)
                if not isinstance(request, dict):
                    raise ValueError("API input is not an object")
            except (OSError, UnicodeError):
                unreadable = Unreadable("body", "missing-file", source)
                return Extraction(route, number, tuple(publications), (unreadable,))
            except (json.JSONDecodeError, ValueError):
                unreadable = Unreadable("body", "invalid-input", source)
                return Extraction(route, number, tuple(publications), (unreadable,))
            for field in ("title", "body"):
                value = request.get(field)
                if isinstance(value, str):
                    publications.append(Publication(field, value, source))
            index += 2
            continue
        if token in INLINE_FLAGS and index + 1 < len(arguments):
            read = _resolve_plain_value(
                INLINE_FLAGS[token], arguments[index + 1], assignments, substitutions
            )
            if isinstance(read, Unreadable):
                return Extraction(route, number, tuple(publications), (read,), grade_route)
            publications.append(read)
            index += 2
            continue
        if token in FILE_FLAGS and index + 1 < len(arguments):
            field = FILE_FLAGS[token]
            read = _read_file_field(
                field, arguments[index + 1], command, assignments, substitutions
            )
            if isinstance(read, Unreadable):
                return Extraction(route, number, tuple(publications), (read,))
            publications.append(read)
            index += 2
            continue
        if route != ("api",):
            for flag, field in FILE_FLAGS.items():
                prefix = flag + "="
                if token.startswith(prefix):
                    read = _read_file_field(
                        field,
                        token[len(prefix) :],
                        command,
                        assignments,
                        substitutions,
                    )
                    if isinstance(read, Unreadable):
                        return Extraction(route, number, tuple(publications), (read,))
                    publications.append(read)
                    break
        for flag, field in INLINE_FLAGS.items():
            prefix = flag + "="
            if token.startswith(prefix):
                read = _resolve_plain_value(
                    field, token[len(prefix) :], assignments, substitutions
                )
                if isinstance(read, Unreadable):
                    return Extraction(route, number, tuple(publications), (read,), grade_route)
                publications.append(read)
                break
        index += 1
    return Extraction(route, number, tuple(publications), (), grade_route)


def _branch_rule(report: str) -> str:
    if "repo-relative Markdown link" in report:
        return "branch:repo-relative-link"
    if "same-directory" in report:
        return "branch:near-miss"
    if "unresolved path" in report or "cites an unresolved path" in report:
        return "branch:unresolved-path"
    if "self-declares completion" in report:
        return "branch:self-declares-completion"
    if "labeled 'in flight'" in report:
        return "branch:in-flight"
    return "branch:scope"


def analyze(
    publication: Publication,
    *,
    index: phi_scan.CorpusIndex,
    issue: dict | None,
    remote_fresh: bool,
    route: tuple[str, ...] = ("issue", "comment"),
) -> Analysis:
    """Grade one title or body without returning its text or matched values."""
    phi_counts = Counter(
        finding.rule
        for finding in phi_scan.scan_text(publication.text, publication.field, index)
    )
    findings = [
        Finding(f"phi:{rule}", count, publication.field, "advise")
        for rule, count in sorted(phi_counts.items())
    ]

    if publication.field == "title":
        branch = tracker_branch_scope.grade(
            {
                "pull_request": {
                    "body": publication.text,
                    "html_url": "draft title",
                }
            },
            "pull_request_target",
        )
        context = (
            "title path triggers evaluated; record-label and completion triggers "
            "apply to bodies"
        )
    else:
        labels = [] if issue is None else issue.get("labels", [])
        label_rows = [
            row if isinstance(row, dict) else {"name": row}
            for row in labels
        ]
        container = {
            "number": 0 if issue is None else issue.get("number"),
            "labels": label_rows,
            "html_url": "draft record" if issue is None else issue.get("url", "draft record"),
        }
        if route in (("issue", "create"), ("issue", "edit")):
            container["body"] = publication.text
            branch = tracker_branch_scope.grade({"issue": container}, "issues")
        elif route in (("pr", "create"), ("pr", "edit")):
            container["body"] = publication.text
            branch = tracker_branch_scope.grade(
                {"pull_request": container}, "pull_request_target"
            )
        elif route == ("pr", "review"):
            branch = tracker_branch_scope.grade(
                {
                    "pull_request": container,
                    "review": {
                        "body": publication.text,
                        "html_url": container["html_url"],
                    },
                },
                "pull_request_review",
            )
        else:
            if route == ("pr", "comment") or "/pull/" in container["html_url"]:
                container["pull_request"] = {}
            branch = tracker_branch_scope.grade(
                {
                    "issue": container,
                    "comment": {
                        "body": publication.text,
                        "html_url": container["html_url"],
                    },
                },
                "issue_comment",
            )
        context = (
            "context-blind: record number and labels were not read; the in-flight "
            "trigger was not evaluated"
            if issue is None
            else f"record context: issue #{container['number']} labels read"
        )

    if branch.status == 1:
        rule = _branch_rule(branch.report)
        remote_rule = rule in ("branch:unresolved-path", "branch:near-miss")
        posture = (
            "advise"
            if rule == "branch:near-miss" or (remote_rule and not remote_fresh)
            else "deny"
        )
        findings.append(Finding(rule, 1, publication.field, posture))

    lines = [context]
    if not remote_fresh:
        lines.append(
            "origin/main fetch failed: unresolved-path and near-miss rules are advisory"
        )
    lines.extend(
        f"{row.posture}: {row.rule}: {row.count} finding(s) in {row.field}"
        for row in findings
    )
    if not findings:
        lines.append(f"scanned {publication.field}: 0 findings")
    return Analysis(tuple(findings), "\n".join(lines))


def current_index() -> tuple[phi_scan.CorpusIndex, tuple[str, ...]]:
    names, dates = phi_scan.corpus_identifiers()
    return phi_scan.build_index(names, dates), tuple(phi_scan.missing_corpus_sources())


def refresh_default_branch() -> bool:
    completed = subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode == 0


def fetch_issue(number: int) -> dict:
    completed = subprocess.run(
        ["gh", "issue", "view", str(number), "--json", "number,labels,url"],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    document = json.loads(completed.stdout)
    if not isinstance(document, dict):
        raise ValueError("issue context was not an object")
    return document


def write_marker() -> None:
    PUBLISH_MARKER.parent.mkdir(parents=True, exist_ok=True)
    PUBLISH_MARKER.write_text(
        json.dumps(
            {"version": 1, "ran_on": CalendarDate.today().isoformat()},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _hook_response(decision: str | None, report: str) -> dict:
    specific = {
        "hookEventName": "PreToolUse",
        "additionalContext": report,
    }
    if decision is not None:
        specific["permissionDecision"] = decision
    if decision == "deny":
        specific["permissionDecisionReason"] = (
            "tracker branch-scope text must be corrected before publication"
        )
    return {"hookSpecificOutput": specific}


UNREADABLE_REMEDIES = {
    "missing-file": (
        "create the file first, then run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "external-variable": (
        "resolve the variable and run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "pipe": (
        "save the piped text to a file and run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "written-before-publish": (
        "write the file in a separate command, then retry the gh publication"
    ),
    "command-substitution": (
        "run the substitution separately and then run `python "
        "tools/tracker_publish_hook.py --text <path>` before retrying"
    ),
    "invalid-input": (
        "repair the JSON input and run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "invalid-command": (
        "repair the command quoting, save the tracker text to a file, and run "
        "`python tools/tracker_publish_hook.py --text <path>` before retrying"
    ),
    "missing-value": (
        "supply the flag value, or save the tracker text to a file and run "
        "`python tools/tracker_publish_hook.py --text <path>` before retrying"
    ),
}


def _source_label(source: str) -> str:
    return source if source in ("inline", "inline heredoc") else "body-file"


def handle(payload: dict) -> dict:
    """Return one Claude Code hook response without echoing tracker text."""
    try:
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("tool_input is not an object")
        command = tool_input.get("command")
        if not isinstance(command, str):
            raise ValueError("tool_input.command is not text")
        extracted = extract(command)
        if extracted.route is None:
            return {}
        if extracted.unreadable:
            lines = [
                f"tracker pre-publish: Unreadable {row.field} "
                f"({row.kind}); {UNREADABLE_REMEDIES[row.kind]}"
                for row in extracted.unreadable
            ]
            return _hook_response(None, "\n".join(lines))
        if not extracted.publications:
            return {}

        index, missing = current_index()
        remote_fresh = refresh_default_branch()
        issue = None
        if extracted.number is not None:
            try:
                issue = fetch_issue(extracted.number)
            except (
                OSError,
                UnicodeError,
                subprocess.SubprocessError,
                json.JSONDecodeError,
                ValueError,
            ):
                issue = None

        analyses = [
            analyze(
                publication,
                index=index,
                issue=issue,
                remote_fresh=remote_fresh,
                route=extracted.grade_route or extracted.route,
            )
            for publication in extracted.publications
        ]
        write_marker()
        lines = [
            f"tracker pre-publish: {publication.field} read from "
            f"{_source_label(publication.source)}"
            for publication in extracted.publications
        ]
        if missing:
            lines.append(
                "PHI corpus layer incomplete: "
                + ", ".join(missing)
                + " not available"
            )
        lines.extend(analysis.report for analysis in analyses)
        denied = any(
            finding.posture == "deny"
            for analysis in analyses
            for finding in analysis.findings
        )
        return _hook_response("deny" if denied else None, "\n".join(lines))
    except Exception as exc:
        return _hook_response(
            None,
            "tracker pre-publish HOOK FAILURE: "
            f"Unreadable body ({type(exc).__name__})",
        )


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) == 2 and arguments[0] == "--text":
        try:
            text = Path(arguments[1]).read_text(encoding="utf-8")
            index, missing = current_index()
            analysis = analyze(
                Publication("body", text, "body-file"),
                index=index,
                issue=None,
                remote_fresh=refresh_default_branch(),
            )
        except (OSError, UnicodeError, subprocess.SubprocessError, ValueError) as exc:
            print(
                "tracker pre-publish: Unreadable body: " + type(exc).__name__,
                file=sys.stderr,
            )
            return 2
        print("tracker pre-publish: body read from body-file")
        if missing:
            print("PHI corpus layer incomplete: " + ", ".join(missing) + " not available")
        print(analysis.report)
        return 1 if any(row.posture == "deny" for row in analysis.findings) else 0
    if arguments:
        print("tracker pre-publish: unsupported arguments", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
    except (UnicodeError, json.JSONDecodeError) as exc:
        response = _hook_response(
            None,
            "tracker pre-publish HOOK FAILURE: "
            f"Unreadable body ({type(exc).__name__})",
        )
    else:
        response = handle(payload)
    print(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
