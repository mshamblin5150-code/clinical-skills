"""Inspect tracker text immediately before a ``gh`` publication.

The command is a Claude Code ``PreToolUse`` hook: it reads one hook payload as
JSON from stdin and writes one hook response as JSON to stdout. It never prints
the text it scans. Counts, rule names, and the field to edit are the complete
reporting surface.

**A publication whose text cannot be read is refused rather than allowed**, on
every kind in ``UNREADABLE_REMEDIES``, and only on a route in
``PUBLISH_ROUTES`` -- an unrecognized command is never touched. #745: the gate
returned *allow* whenever it could not parse its own input, so the one limb
that refuses evaporated exactly when the hook was least able to vouch for the
text. Each kind's remedy names the by-hand command that grades the file.

**What it reads is the command as typed, not the shell's expansion of it**, so
resolution is reconstructed rather than observed: assignments made in the same
command are substituted, including where a variable names only the leading part
of a path, and a Git Bash ``/c/...`` path is also tried in its Windows
spelling. What is left -- a variable from the environment, a command
substitution, a pipe -- is unreadable by construction and is refused above.

What a clean run does not establish is owned by ``NOT_REACHED`` below rather
than copied into this docstring or ``CLAUDE.md``.
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
import tracker_bodies
import tracker_branch_scope
import tracker_readback
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

# Measured before being written, per ADR 0109 ruling 13. Across 371 real issue
# bodies and the text in 11 real run directories on 2026-09-02, an 80-character
# normalized span appeared in seven bodies; shorter floors rapidly admitted
# ordinary overlap. The gate fires only for a body file under
# ``<run>/aar/publications/`` and therefore changes no ordinary publication.
AAR_QUOTE_SPAN_CHARS = 80
AAR_PUBLICATION_PARTS = ("aar", "publications")

NOT_REACHED = (
    (
        "the GitHub web UI bypasses the hook",
        "Tracker text published through the GitHub web UI never crosses this "
        "Claude Code pre-publication boundary.",
    ),
    (
        "disabled or overridden hooks bypass the check",
        "A session started with hooks disabled or with overriding settings can "
        "publish without this hook running.",
    ),
    (
        "retained pre-edit revisions remain readable",
        "GitHub retains earlier revisions of edited tracker records, and this "
        "hook cannot read or remove those preserved versions.",
    ),
    (
        "workspace trust can silently suppress registration",
        "An unaccepted workspace trust prompt can silently prevent the project "
        "hook from registering in a new worktree.",
    ),
    (
        "a file rewritten after the scan is graded on its earlier text",
        "The body is read when the hook runs. A command that rewrites that "
        "file between the scan and the publication publishes text this hook "
        "never saw.",
    ),
    (
        "expansion is reconstructed and reaches only the same command",
        "A variable assigned in an earlier command, an exported one, and "
        "anything a subshell computes are not resolvable here. Each is refused "
        "rather than guessed at, so the floor does not become a silent pass.",
    ),
    (
        "the refusing hook covers one of two publishers",
        "This Claude Code hook prevents a damaged publication from this "
        "publisher only. The GitHub workflow reaches both known publishers "
        "after publication and reports rather than prevents.",
    ),
    (
        "a failed tracker readback leaves the publication context-blind",
        "When the batched tracker fetch fails, the hook says that current "
        "record state and labels were not read and continues without claiming "
        "that the cited records are current.",
    ),
    (
        "an AAR paraphrase passes the quotation gate",
        "The AAR gate refuses copied spans and cannot recognize a paraphrase of private working material.",
    ),
)


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
}
FILE_FLAGS = {"--body-file": "body", "-F": "body"}
API_VALUE_FLAGS = {"-f", "--raw-field", "-F", "--field"}
TARGET_VALUE_FLAGS = {
    "--add-assignee",
    "--add-label",
    "--add-project",
    "--add-reviewer",
    "--base",
    "--milestone",
    "--reason",
    "--remove-assignee",
    "--remove-label",
    "--remove-project",
    "--remove-reviewer",
    "--repo",
    "-R",
}
API_RECORD_NUMBER = re.compile(r"/(?:issues|pulls?)/(?P<number>[0-9]+)(?:/|\Z)")
RAW_PUBLISH_ROUTE = re.compile(
    r"(?:\A|[;&|]\s*)gh\s+(?:(api)\b|([A-Za-z]+)\s+([A-Za-z]+)\b)"
)
PLAIN_ASSIGNMENT = re.compile(
    r"(?:\A|[;&|\n]\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)="
    r"(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<bare>[^\s;&|]+))"
)
VARIABLE = re.compile(
    r"\A\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
    r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))(?P<rest>/.*)?\Z",
    re.DOTALL,
)
MSYS_PATH = re.compile(r"\A/(?P<drive>[A-Za-z])/(?P<rest>.*)\Z", re.DOTALL)
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


def _expand(
    value: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> tuple[str | None, str | None]:
    """Return the shell-expanded value, or the kind that makes it unreadable.

    The hook runs before the shell does, so there is no expanded argument to
    read -- ``tool_input.command`` is the text as typed. Expansion is therefore
    reconstructed from assignments made in the same command, which is the only
    source available at this point. A variable naming a path *prefix* expands
    here as the shell would expand it; #745 is what happened while only a value
    that was entirely one variable did.
    """
    variable = VARIABLE.match(value)
    if variable is None:
        return value, None
    name = variable.group("braced") or variable.group("plain")
    rest = variable.group("rest") or ""
    if name in assignments:
        return assignments[name] + rest, None
    return None, (
        "command-substitution" if name in substitutions else "external-variable"
    )


def _candidate_paths(source: str) -> tuple[str, ...]:
    """Return the spellings of one path this platform may have to try.

    A Git Bash command line writes ``/c/Users/...`` where Windows resolves
    ``C:/Users/...``. MSYS rewrites it when it launches a native executable, so
    the shell's own argument is fine and the hook's copy -- taken before that
    rewrite -- is not. Reading it here is not a guess about the caller: either
    spelling names one file, and only one of them opens.
    """
    match = MSYS_PATH.match(source)
    if match is None or sys.platform != "win32":
        return (source,)
    drive = match.group("drive").upper()
    return (source, f"{drive}:/{match.group('rest')}")


def _read_candidate(source: str) -> str | None:
    for candidate in _candidate_paths(source):
        try:
            return Path(candidate).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
    return None


def _candidate_file(source: str) -> Path | None:
    for candidate in _candidate_paths(source):
        path = Path(candidate)
        if path.is_file():
            return path.resolve()
    return None


def _aar_run_directory(source: str) -> Path | None:
    """The run root for an AAR-owned body file, otherwise ``None``."""
    path = _candidate_file(source)
    if path is None or path.parent.name != AAR_PUBLICATION_PARTS[1]:
        return None
    aar = path.parent.parent
    if aar.name != AAR_PUBLICATION_PARTS[0]:
        return None
    return aar.parent


def _normalized_span_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _quotes_run_material(publication: Publication) -> bool:
    """Whether one AAR body repeats a measured-length span from its run.

    ``aar/`` is excluded because its extract necessarily contains the complete
    reduced conversation. The gate's subject is the working material the review
    was about, not the review record describing conduct.
    """
    run = _aar_run_directory(publication.source)
    body = _normalized_span_text(publication.text)
    if run is None or len(body) < AAR_QUOTE_SPAN_CHARS:
        return False
    spans = {
        body[index : index + AAR_QUOTE_SPAN_CHARS]
        for index in range(len(body) - AAR_QUOTE_SPAN_CHARS + 1)
    }
    for path in run.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".md", ".txt", ".json"}:
            continue
        try:
            path.resolve().relative_to((run / "aar").resolve())
        except ValueError:
            pass
        else:
            continue
        try:
            source = _normalized_span_text(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if any(
            source[index : index + AAR_QUOTE_SPAN_CHARS] in spans
            for index in range(len(source) - AAR_QUOTE_SPAN_CHARS + 1)
        ):
            return True
    return False


def aar_quotation_analysis(publications: tuple[Publication, ...]) -> Analysis:
    findings = tuple(
        Finding("aar-quotation", 1, publication.field, "deny")
        for publication in publications
        if _quotes_run_material(publication)
    )
    report = (
        "AAR quotation gate: copied private-run spans " + str(len(findings))
        if findings
        else "AAR quotation gate: 0 copied private-run spans"
    )
    return Analysis(findings, report)


def _resolve_plain_value(
    field: str,
    value: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> Publication | Unreadable:
    expanded, kind = _expand(value, assignments, substitutions)
    if kind is not None:
        return Unreadable(field, kind, value)
    return Publication(field, expanded)


def _raw_publish_route(command: str) -> tuple[str, ...] | None:
    match = RAW_PUBLISH_ROUTE.search(command)
    if match is None:
        return None
    if match.group(1) == "api":
        return ("api",)
    route = (match.group(2), match.group(3))
    return route if route in PUBLISH_ROUTES else None


def _api_grade_route(arguments: list[str]) -> tuple[str, ...]:
    endpoint = next(
        (
            token
            for token in arguments
            if re.search(r"/(?:issues|pulls)(?:/|\?|\Z)", token)
        ),
        "",
    )
    if re.search(r"/issues/[0-9]+/comments(?:\Z|\?)", endpoint):
        return ("issue", "comment")
    if re.search(r"/pulls/[0-9]+/reviews(?:\Z|\?)", endpoint):
        return ("pr", "review")
    if re.search(r"/pulls/[0-9]+/comments(?:\Z|\?)", endpoint):
        return ("pr", "comment")
    if re.search(r"/pulls/[0-9]+(?:\Z|\?)", endpoint):
        return ("pr", "edit")
    if re.search(r"/issues/[0-9]+(?:\Z|\?)", endpoint):
        return ("issue", "edit")
    if re.search(r"/issues/comments/[0-9]+(?:\Z|\?)", endpoint):
        return ("issue", "comment")
    if re.search(r"/pulls/comments/[0-9]+(?:\Z|\?)", endpoint):
        return ("pr", "comment")
    if re.search(r"/pulls(?:\Z|\?)", endpoint):
        return ("pr", "create")
    if re.search(r"/issues(?:\Z|\?)", endpoint):
        return ("issue", "create")
    return ("issue", "edit")


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
    index = 0
    value_flags = set(INLINE_FLAGS) | set(FILE_FLAGS) | TARGET_VALUE_FLAGS
    if route == ("issue", "close"):
        value_flags |= {"--comment", "-c"}
    while index < len(arguments):
        token = arguments[index]
        if token in value_flags:
            index += 2
            continue
        if any(
            token.startswith(flag + "=")
            for flag in set(INLINE_FLAGS) | set(FILE_FLAGS)
        ):
            index += 1
            continue
        if token.isdecimal():
            return int(token)
        match = API_RECORD_NUMBER.search(token)
        if match is not None:
            return int(match.group("number"))
        index += 1
    return None


def _read_file_field(
    field: str,
    source: str,
    command: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> Publication | Unreadable:
    expanded, kind = _expand(source, assignments, substitutions)
    if kind is not None:
        return Unreadable(field, kind, source)
    source = expanded
    if source == "-":
        heredoc = HEREDOC.search(command)
        if heredoc is None:
            return Unreadable(field, "pipe", source)
        return Publication(field, heredoc.group("body"), "inline heredoc")
    text = _read_candidate(source)
    if text is None:
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
            or (
                route == ("issue", "close")
                and token in ("--comment", "-c")
            )
        )
        if body_flag and index + 1 >= len(arguments):
            unreadable = Unreadable("body", "missing-value", token)
            return Extraction(route, number, tuple(publications), (unreadable,), grade_route)
        if (
            route == ("issue", "close")
            and token in ("--comment", "-c")
            and index + 1 < len(arguments)
        ):
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
                    request_text = _read_candidate(source)
                    if request_text is None:
                        raise OSError(source)
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
        if route == ("issue", "close"):
            close_equals = next(
                (
                    token[len(flag) + 1 :]
                    for flag in ("--comment", "-c")
                    if token.startswith(flag + "=")
                ),
                None,
            )
            if close_equals is not None:
                read = _resolve_plain_value(
                    "body", close_equals, assignments, substitutions
                )
                if isinstance(read, Unreadable):
                    return Extraction(
                        route, number, tuple(publications), (read,), grade_route
                    )
                publications.append(read)
                index += 1
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
    if tracker_bodies.has_c0_control_character(publication.text):
        findings.append(Finding(
            "body:c0-control-character", 1, publication.field, "deny"
        ))

    if publication.field == "title":
        branch = tracker_branch_scope.grade(
            {
                "pull_request": {
                    "body": publication.text,
                    "html_url": "draft title",
                }
            },
            "pull_request_target",
            remote_fresh=remote_fresh,
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
            branch = tracker_branch_scope.grade(
                {"issue": container}, "issues", remote_fresh=remote_fresh
            )
        elif route in (("pr", "create"), ("pr", "edit")):
            container["body"] = publication.text
            branch = tracker_branch_scope.grade(
                {"pull_request": container},
                "pull_request_target",
                remote_fresh=remote_fresh,
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
                remote_fresh=remote_fresh,
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
                remote_fresh=remote_fresh,
            )
        context = (
            "context-blind: record number and labels were not read; the in-flight "
            "trigger was not evaluated"
            if issue is None
            else f"record context: issue #{container['number']} labels read"
        )

    positive_unverified = (
        branch.status == 0 and "ancestry could not be verified" in branch.report
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
    if positive_unverified:
        lines.append(
            "positive Branch state accepted without ancestry verification"
        )
    lines.extend(
        f"{row.posture}: {row.rule}: {row.count} finding(s) in {row.field}"
        for row in findings
    )
    if not findings:
        lines.append(f"scanned {publication.field}: 0 findings")
    return Analysis(tuple(findings), "\n".join(lines))


def authorize_issue_body(body: str, label: str) -> None:
    """Apply the shared lost-body and raw-control refusal for direct writers.

    Most tracker writes arrive as a shell command and enter through ``handle``.
    An in-process writer already holds the exact body, so making it reconstruct
    shell quoting would add a second, weaker extraction path. This entry point
    feeds those bytes to the same ``tracker_bodies`` predicate instead.
    """
    findings = tracker_bodies.grade(
        [tracker_bodies.Record("direct publication", label, tracker_bodies.ISSUE, body)]
    )
    if findings:
        kinds = ", ".join(row.kind for row in findings)
        raise ValueError(f"tracker body refused for {label}: {kinds}")


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


REPOSITORY_OWNER = "mshamblin5150-code"
REPOSITORY_NAME = "clinical-skills"


def _readback_query(numbers: frozenset[int]) -> str:
    selections = "\n".join(
        f"""record_{number}: issueOrPullRequest(number: {number}) {{
      ... on Issue {{ number state labels(first: 100) {{ nodes {{ name }} }} updatedAt body url }}
      ... on PullRequest {{ number state labels(first: 100) {{ nodes {{ name }} }} updatedAt body url }}
    }}"""
        for number in sorted(numbers)
    )
    return f"""query($owner: String!, $name: String!) {{
  repository(owner: $owner, name: $name) {{
    {selections}
  }}
}}"""


def fetch_readback(
    numbers: frozenset[int],
) -> dict[int, dict | None]:
    """Fetch all current record fingerprints in one GraphQL request.

    ``gh api graphql`` can return status 1 while stdout still contains every
    resolved alias and ``null`` for an unresolved one.  The payload, not the
    process status, therefore decides whether the read succeeded.
    """
    completed = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-F",
            f"owner={REPOSITORY_OWNER}",
            "-F",
            f"name={REPOSITORY_NAME}",
            "-f",
            "query=" + _readback_query(numbers),
        ],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    document = json.loads(completed.stdout)
    if not isinstance(document, dict):
        raise ValueError("tracker readback payload was not an object")
    data = document.get("data")
    repository = data.get("repository") if isinstance(data, dict) else None
    if not isinstance(repository, dict):
        raise ValueError("tracker readback payload had no repository data")
    records: dict[int, dict | None] = {}
    for number in numbers:
        alias = f"record_{number}"
        if alias not in repository:
            raise ValueError("tracker readback omitted requested record")
        record = repository[alias]
        if record is not None and not isinstance(record, dict):
            raise ValueError("tracker readback record had the wrong type")
        records[number] = record
    return records


def _issue_context(record: dict | None) -> dict | None:
    if record is None:
        return None
    url = record.get("url")
    if not isinstance(url, str):
        raise ValueError("tracker readback record URL had the wrong type")
    return {
        "number": record.get("number"),
        "labels": list(tracker_readback.label_names(record)),
        "url": url,
    }


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


BRANCH_SCOPE_REFUSAL = (
    "tracker branch-scope text must be corrected before publication"
)
UNSCANNED_REFUSAL = (
    "tracker text could not be read, so this publication was not scanned"
)


def _hook_response(
    decision: str | None,
    report: str,
    reason: str = BRANCH_SCOPE_REFUSAL,
) -> dict:
    specific = {
        "hookEventName": "PreToolUse",
        "additionalContext": report,
    }
    if decision is not None:
        specific["permissionDecision"] = decision
    if decision == "deny":
        specific["permissionDecisionReason"] = reason
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
                f"tracker pre-publish: NOT SCANNED -- unreadable {row.field} "
                f"({row.kind}); {UNREADABLE_REMEDIES[row.kind]}"
                for row in extracted.unreadable
            ]
            return _hook_response("deny", "\n".join(lines), UNSCANNED_REFUSAL)
        if not extracted.publications:
            return {}

        index, missing = current_index()
        remote_fresh = refresh_default_branch()
        # ``tracker_scan`` splits title and body so a finding identifies the
        # field to edit. A readback identifies records, not fields, so that
        # reason does not transfer and both fields deliberately form one set.
        publication_text = "\n".join(row.text for row in extracted.publications)
        citations = tracker_readback.citation_numbers(
            publication_text,
            publication_number=extracted.number,
        )
        issue = None
        readback_lines: tuple[str, ...]
        if citations:
            try:
                records = fetch_readback(citations)
                readback_lines = tracker_readback.fingerprint_lines(records)
                if extracted.number is not None:
                    issue = _issue_context(records.get(extracted.number))
            except (
                OSError,
                UnicodeError,
                subprocess.SubprocessError,
                json.JSONDecodeError,
                ValueError,
            ):
                readback_lines = (
                    "tracker readback: FETCH FAILED; context-blind -- current "
                    "record state and labels were not read",
                )
        else:
            readback_lines = (tracker_readback.empty_citation_line(),)

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
        analyses.append(aar_quotation_analysis(extracted.publications))
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
        lines.extend(readback_lines)
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
