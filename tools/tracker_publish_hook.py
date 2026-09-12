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

**What it reads is the command as typed, not the shell's expansion of it.** An
inline body or title is readable only when every segment is single-quoted or an
outside-quote escaped character, so the hook can reproduce exactly what the
shell will deliver. Body-file resolution is reconstructed rather than observed:
same-command assignments are substituted, including where a variable names only
the leading part of a path, and a Git Bash ``/c/...`` path is also tried in its
Windows spelling. What is left unreadable is refused above.

Every readable body is graded through ``tracker_bodies.grade``. On the command
route, each returned row refuses as ``body:<kind>`` and carries the remedy from
``BODY_REMEDIES``. The direct writer keeps its existing exception interface. A
title stays outside that body grader and keeps only the C0-control and
flanked-carriage-return predicates. What a clean run does not establish is
owned by ``NOT_REACHED`` below rather than copied into this docstring or
``CLAUDE.md``.
"""

from __future__ import annotations

from collections import Counter
from datetime import date as CalendarDate
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple

import phi_scan
import tracker_bodies
import tracker_coordinates
import tracker_branch_scope
import tracker_filed_from
import tracker_readback
import shell_reader
from console_codec import require_python_floor, use_utf8
from tracker_records import TrackerRecord, from_command, from_graphql
from tracker_bodies import ordinary_paragraph_prose


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
        "assignment expansion is reconstructed and reaches only the same command",
        "A variable assigned in an earlier command or exported by the environment "
        "is not resolvable here. A substitution behind a same-command variable is "
        "refused rather than guessed at; directly supplied inline values instead "
        "cross the quoting-fidelity refusal before their text is graded.",
    ),
    (
        "no route rule covers the cause side of escape collapse",
        "A residual reproducible inline body is not thereby text-graded for a "
        "partial literal-newline collapse. The body grader declares its own text "
        "boundary; no additional command-form rule refuses that cause.",
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
        "the fetched origin can be a non-canonical repository",
        "Branch-scope grading fetches and reads the remote named origin even "
        "when that remote is not mshamblin5150-code/clinical-skills.",
    ),
    (
        "an AAR paraphrase passes the quotation gate",
        "The AAR gate refuses copied spans and cannot recognize a paraphrase of private working material.",
    ),
    (
        "the command-folder reader reaches literal absolute cd targets only",
        "A variable, substitution, parent, previous-folder, home, or relative cd target is refused rather than guessed at.",
    ),
    (
        "a stock discriminator clause can satisfy the verdict form check",
        "The check establishes that the comment carries the declared form and "
        "cannot establish that its counterfactual is true.",
    ),
    (
        "manual text mode has no issue publication route",
        "The --text command grades body shape without a create or edit route, so it reports the Filed-from rule not graded rather than clean.",
    ),
)


class Publication(NamedTuple):
    field: str
    text: str
    source: str = "inline"
    resolved_against: str | None = None
    reconstructed_path: str | None = None
    record: TrackerRecord | None = None


def with_tracker_record(
    publication: Publication,
    *,
    route: tuple[str, ...],
    context: TrackerRecord | dict | None,
) -> Publication:
    """Bind command text to its semantic record before policy grading."""
    if publication.record is not None:
        return publication
    if isinstance(context, TrackerRecord):
        url = context.url
        number = context.number
        labels = context.labels
    elif isinstance(context, dict):
        url = context.get("url", "draft record")
        number = context.get("number")
        labels = tuple(
            row.get("name") if isinstance(row, dict) else row
            for row in context.get("labels", [])
            if isinstance(row, (dict, str))
        )
    else:
        url = "draft record"
        number = None
        labels = ()
    record = from_command(
        publication.text,
        url=url,
        number=number,
        labels=labels,
        route=route,
        field=publication.field,
    )
    return publication._replace(record=record)


class Unreadable(NamedTuple):
    field: str
    kind: str
    source: str
    resolved_against: str | None = None
    reconstructed_path: str | None = None


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


_USE_ANALYSIS_ROUTE = object()


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
COMMENT_ROUTES = (
    ("issue", "comment"),
    ("issue", "close"),
    ("pr", "comment"),
    ("pr", "review"),
)
DISCRIMINATOR_CLAUSE = re.compile(
    r"\bunder the claim['’]s negation\b",
    re.IGNORECASE,
)
REDACTION_WALK_KINDS = (
    "phi:corpus-name",
    "phi:corpus-date",
    *(f"phi:{kind}" for kind in phi_scan.SHAPE_RULES),
    *(f"body:{kind}" for kind in tracker_bodies.KINDS),
    tracker_coordinates.UNANCHORED,
    "verdict:missing-discriminator",
    *tracker_branch_scope.BRANCH_RULES,
)

LOST_BODY_REMEDY = (
    "the body did not land; write it to a file and pass that file's "
    "absolute path to --body-file"
)
BODY_REMEDIES = {
    tracker_bodies.LOST_AT_DASH: LOST_BODY_REMEDY,
    tracker_bodies.EMPTY_BODY: LOST_BODY_REMEDY,
    tracker_bodies.LITERAL_AT_PATH: LOST_BODY_REMEDY,
    tracker_bodies.DOUBLE_ENCODED: (
        "rewrite text damaged through a cp1252 path as UTF-8; for a genuine "
        "mention only, put the deliberately named sequence in backticks, "
        "because backticks also hide damage"
    ),
    tracker_bodies.C0_CONTROL_CHARACTER: (
        "remove the raw C0 control character and restore the intended text"
    ),
    tracker_bodies.CARRIAGE_RETURN_FLANKED: (
        "replace the flanked carriage return with the intended text or line break"
    ),
    tracker_bodies.LITERAL_NEWLINE_ESCAPE: (
        "replace the literal newline escape with the intended real line break"
    ),
    tracker_bodies.DOUBLED_PATH_SEPARATOR: (
        "restore the intended single path separator"
    ),
}
COORDINATE_REMEDY = (
    "place an anchor beside the coordinate: a backticked identifier or span, "
    "a prose quotation, or an immediately following fenced or quoted block"
)


def body_remedy(kind: str, route: tuple[str, ...]) -> str:
    """The repair for one body row on the publication route that produced it."""
    if kind == tracker_bodies.EMPTY_BODY and route == ("pr", "review"):
        return (
            "omit the --body flag if this is an approval; otherwise supply "
            "the intended review text"
        )
    return BODY_REMEDIES[kind]


def redaction_walk_report(triggered: set[str]) -> str:
    """Report the declared denominator and any kind the fixtures did not trigger."""
    unread = tuple(kind for kind in REDACTION_WALK_KINDS if kind not in triggered)
    remainder = ", ".join(unread) if unread else "none"
    return (
        f"tracker redaction walk: {len(REDACTION_WALK_KINDS) - len(unread)}/"
        f"{len(REDACTION_WALK_KINDS)} kinds triggered; unread: {remainder}"
    )
API_RECORD_NUMBER = re.compile(r"/(?:issues|pulls?)/(?P<number>[0-9]+)(?:/|\Z)")
RAW_PUBLISH_ROUTE = re.compile(
    r"(?:\A|[;&|]\s*)gh\s+(?:(api)\b|([A-Za-z]+)\s+([A-Za-z]+)\b)"
)
HEREDOC = re.compile(
    r"<<-?\s*['\"]?(?P<tag>[A-Za-z_][A-Za-z0-9_]*)['\"]?[ \t]*\r?\n"
    r"(?P<body>.*?)\r?\n(?P=tag)(?:\r?\n|\Z)",
    re.DOTALL,
)


def _fragment_has_publish(fragment: str) -> bool:
    return _publish_tokens(fragment) is not None


def command_tokens(command: str, executable: str) -> tuple[tuple[list[str], int], ...]:
    """Shared shell-token boundary for hooks that classify completed commands."""
    return tuple(shell_reader.executable_calls(command, executable))


def gh_command_tokens(
    command: str, routes: tuple[tuple[str, ...], ...]
) -> tuple[list[str], int] | None:
    """Return the first parsed ``gh`` invocation matching a declared route."""
    for tokens, index in command_tokens(command, "gh"):
        if index + 1 >= len(tokens):
            continue
        tail = tokens[index + 1 :]
        route = ("api",) if tail[0] == "api" else tuple(tail[:2])
        if route in routes:
            return tokens, index
    return None


def _publish_tokens(command: str) -> tuple[list[str], int] | None:
    return gh_command_tokens(command, PUBLISH_ROUTES)


def _publish_source_tokens(
    command: str,
) -> tuple[list[str], tuple[str, ...], int] | None:
    for tokens, sources, index in shell_reader.executable_source_calls(command, "gh"):
        if index + 1 >= len(tokens):
            continue
        tail = tokens[index + 1 :]
        route = ("api",) if tail[0] == "api" else tuple(tail[:2])
        if route in PUBLISH_ROUTES:
            return tokens, sources, index
    return None


def _resolve_file_source(source: str, command: str) -> tuple[str, Path | None] | None:
    if shell_reader.is_absolute_path(source):
        return source, None
    if re.match(r"\A[A-Za-z]:[^\\/]", source):
        return None
    folder = shell_reader.literal_command_folder(command, _fragment_has_publish)
    if folder is None:
        return None
    return str(folder / source), folder


def _aar_run_directory(source: str) -> Path | None:
    """The run root for an AAR-owned body file, otherwise ``None``."""
    path = shell_reader.candidate_file(source)
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


def _reproduce_inline_value(source: str) -> str | None:
    """Reproduce a value made only of literal shell segments."""
    reproduced: list[str] = []
    index = 0
    while index < len(source):
        if source[index] == "'":
            closing = source.find("'", index + 1)
            if closing < 0:
                return None
            reproduced.append(source[index + 1 : closing])
            index = closing + 1
            continue
        if source[index] == "\\" and index + 1 < len(source):
            if source[index + 1] != "\n":
                reproduced.append(source[index + 1])
            index += 2
            continue
        return None
    return "".join(reproduced)


def _before_shell_redirection(source: str) -> str:
    quote: str | None = None
    index = 0
    while index < len(source):
        character = source[index]
        if quote == "'":
            if character == "'":
                quote = None
            index += 1
            continue
        if quote == '"':
            if character == "\\" and index + 1 < len(source):
                index += 2
                continue
            if character == '"':
                quote = None
            index += 1
            continue
        if character == "\\" and index + 1 < len(source):
            index += 2
            continue
        if character in "\"'":
            quote = character
            index += 1
            continue
        if character in "<>":
            return source[:index]
        index += 1
    return source


def _read_inline_value(
    field: str, source: str, prefix: str = ""
) -> Publication | Unreadable:
    reproduced = _reproduce_inline_value(_before_shell_redirection(source))
    if reproduced is None:
        return Unreadable(field, "expansion-exposed-inline", source)
    if prefix:
        if not reproduced.startswith(prefix):
            return Unreadable(field, "invalid-command", source)
        reproduced = reproduced[len(prefix) :]
    return Publication(field, reproduced)


def _source_without_literal_prefix(source: str, prefix: str) -> str:
    return source[len(prefix) :] if source.startswith(prefix) else source


def _raw_publish_route(command: str) -> tuple[str, ...] | None:
    match = RAW_PUBLISH_ROUTE.search(command)
    if match is None:
        return None
    if match.group(1) == "api":
        return ("api",)
    route = (match.group(2), match.group(3))
    return route if route in PUBLISH_ROUTES else None


def _api_method(arguments: list[str]) -> str:
    explicit_method: str | None = None
    has_parameters = False
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token in ("--method", "-X") and index + 1 < len(arguments):
            explicit_method = arguments[index + 1].upper()
            index += 2
            continue
        if token.startswith("--method="):
            explicit_method = token.partition("=")[2].upper()
        elif token.startswith("-X") and len(token) > 2:
            explicit_method = token[2:].upper()
        elif (
            token in API_VALUE_FLAGS
            or token == "--input"
            or token.startswith("--raw-field=")
            or token.startswith("--field=")
            or token.startswith("--input=")
            or (token.startswith(("-f", "-F")) and len(token) > 2)
        ):
            has_parameters = True
        index += 1
    if explicit_method is not None:
        return explicit_method
    return "POST" if has_parameters else "GET"


def _api_grade_route(arguments: list[str]) -> tuple[str, ...] | None:
    if _api_method(arguments) == "GET":
        return None
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
    expanded, kind = shell_reader.expand(source, assignments, substitutions)
    if kind is not None:
        return Unreadable(field, kind, source)
    source = expanded
    if source == "-":
        heredoc = HEREDOC.search(command)
        if heredoc is None:
            return Unreadable(field, "pipe", source)
        return Publication(field, heredoc.group("body"), "inline heredoc")
    resolved = _resolve_file_source(source, command)
    if resolved is None:
        return Unreadable(field, "unrooted-path", source, None, source)
    source, folder = resolved
    text = shell_reader.read_candidate(source)
    if text is None:
        return Unreadable(
            field,
            "missing-file",
            source,
            None if folder is None else str(folder),
            source,
        )
    return Publication(
        field,
        text,
        source,
        None if folder is None else str(folder),
        source,
    )


def extract(command: str) -> Extraction:
    """Read inline tracker fields from one ``gh`` invocation."""
    publish = _publish_tokens(command)
    if publish is None:
        route = _raw_publish_route(command)
        if route is None:
            return Extraction(None, None, (), ())
        unreadable = Unreadable("body", "invalid-command", "inline")
        return Extraction(route, None, (), (unreadable,), route)
    tokens, start = publish
    tail = tokens[start + 1 :]
    if not tail:
        return Extraction(None, None, (), ())
    route = ("api",) if tail[0] == "api" else tuple(tail[:2])
    if route not in PUBLISH_ROUTES:
        return Extraction(None, None, (), ())
    source_publish = _publish_source_tokens(command)
    if source_publish is None:
        unreadable = Unreadable("body", "invalid-command", "inline")
        return Extraction(route, None, (), (unreadable,), route)
    source_tokens, sources, source_start = source_publish
    source_tail = source_tokens[source_start + 1 :]
    source_route = (
        ("api",) if source_tail[0] == "api" else tuple(source_tail[:2])
    )
    if source_route != route:
        unreadable = Unreadable("body", "invalid-command", "inline")
        return Extraction(route, None, (), (unreadable,), route)
    route_width = len(route)
    arguments = source_tail[route_width:]
    argument_sources = sources[source_start + 1 + route_width :]
    number = _record_number(route, arguments)
    grade_route = _api_grade_route(arguments) if route == ("api",) else route
    if route == ("api",) and grade_route is None:
        return Extraction(route, number, (), (), None)
    publications: list[Publication] = []
    assignments = shell_reader.plain_assignments(command)
    substitutions = shell_reader.substitution_assignments(command)
    index = 0
    while index < len(arguments):
        token = arguments[index]
        source_token = argument_sources[index]
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
            read = _read_inline_value("body", argument_sources[index + 1])
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
                    source_argument = argument_sources[index + 1]
                    literal_prefix = key + "="
                    source_has_literal_prefix = source_argument.startswith(
                        literal_prefix
                    )
                    source_value = _source_without_literal_prefix(
                        source_argument, literal_prefix
                    )
                    read = _read_inline_value(
                        key,
                        source_value,
                        "" if source_has_literal_prefix else literal_prefix,
                    )
                    if isinstance(read, Unreadable):
                        return Extraction(route, number, tuple(publications), (read,), grade_route)
                    publications.append(read)
            index += 2
            continue
        if route == ("api",) and token == "--input" and index + 1 < len(arguments):
            source = arguments[index + 1]
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
                    resolved_against = None
                    reconstructed_path = None
                else:
                    read = _read_file_field(
                        "body", source, command, assignments, substitutions
                    )
                    if isinstance(read, Unreadable):
                        return Extraction(
                            route, number, tuple(publications), (read,), grade_route
                        )
                    request_text = read.text
                    source = read.source
                    resolved_against = read.resolved_against
                    reconstructed_path = read.reconstructed_path
                request = json.loads(request_text)
                if not isinstance(request, dict):
                    raise ValueError("API input is not an object")
            except (json.JSONDecodeError, ValueError):
                unreadable = Unreadable(
                    "body",
                    "invalid-input",
                    source,
                    resolved_against,
                    reconstructed_path,
                )
                return Extraction(route, number, tuple(publications), (unreadable,))
            for field in ("title", "body"):
                value = request.get(field)
                if isinstance(value, str):
                    publications.append(Publication(field, value, source))
            index += 2
            continue
        if token in INLINE_FLAGS and index + 1 < len(arguments):
            read = _read_inline_value(
                INLINE_FLAGS[token], argument_sources[index + 1]
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
                source_prefix = next(
                    flag + "="
                    for flag in ("--comment", "-c")
                    if token.startswith(flag + "=")
                )
                source_value = _source_without_literal_prefix(
                    source_token, source_prefix
                )
                read = _read_inline_value(
                    "body",
                    source_value,
                    "" if source_token.startswith(source_prefix) else source_prefix,
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
                read = _read_inline_value(
                    field,
                    _source_without_literal_prefix(source_token, prefix),
                    "" if source_token.startswith(prefix) else prefix,
                )
                if isinstance(read, Unreadable):
                    return Extraction(route, number, tuple(publications), (read,), grade_route)
                publications.append(read)
                break
        index += 1
    return Extraction(route, number, tuple(publications), (), grade_route)


def analyze(
    publication: Publication,
    *,
    index: phi_scan.CorpusIndex,
    issue: TrackerRecord | dict | None,
    remote_fresh: bool,
    route: tuple[str, ...] = ("issue", "comment"),
    filed_from_route: tuple[str, ...] | None | object = _USE_ANALYSIS_ROUTE,
) -> Analysis:
    """Grade one title or body without returning its text or matched values."""
    publication = with_tracker_record(publication, route=route, context=issue)
    record = publication.record
    if record is None:  # NamedTuple narrowing for type checkers.
        raise ValueError("publication has no tracker record")
    phi_counts = Counter(
        finding.rule
        for finding in phi_scan.scan_text(publication.text, publication.field, index)
    )
    findings = [
        Finding(f"phi:{rule}", count, publication.field, "advise")
        for rule, count in sorted(phi_counts.items())
    ]
    if publication.field == "body":
        body_findings = tracker_bodies.grade(
            [
                tracker_bodies.Record(
                    "pre-publication",
                    "body being published",
                    tracker_bodies.ISSUE,
                    publication.text,
                )
            ]
        )
        findings.extend(
            Finding(f"body:{row.kind}", 1, publication.field, "deny")
            for row in body_findings
        )
    else:
        if tracker_bodies.has_c0_control_character(publication.text):
            findings.append(Finding(
                "body:c0-control-character", 1, publication.field, "deny"
            ))
        if tracker_bodies.has_carriage_return_flanked(publication.text):
            findings.append(Finding(
                "body:carriage-return-flanked", 1, publication.field, "deny"
            ))
    findings.extend(
        Finding(row.rule, 1, publication.field, "deny")
        for row in tracker_coordinates.grade(
            publication.text, f"{publication.field} being published"
        )
    )
    comment_prose = (
        ordinary_paragraph_prose(publication.text)
        if publication.field == "body" and route in COMMENT_ROUTES
        else ""
    )
    if (
        publication.field == "body"
        and route in COMMENT_ROUTES
        and any(
            line.startswith("**Verdict:**")
            for line in comment_prose.splitlines()
        )
        and not DISCRIMINATOR_CLAUSE.search(comment_prose)
    ):
        findings.append(Finding(
            "verdict:missing-discriminator", 1, publication.field, "advise"
        ))

    branch = tracker_branch_scope.grade_record(record, remote_fresh=remote_fresh)
    if publication.field == "title":
        context = (
            "title path triggers evaluated; record-label and completion triggers "
            "apply to bodies"
        )
    else:
        context = (
            "context-blind: record number and labels were not read; the in-flight "
            "trigger was not evaluated"
            if issue is None
            else f"record context: issue #{record.number} labels read"
        )

    positive_unverified = branch.status == 0 and branch.verdict.ancestry_verified is False

    if isinstance(issue, TrackerRecord):
        current_body = issue.body
    elif isinstance(issue, dict) and isinstance(issue.get("body"), str):
        current_body = issue["body"]
    else:
        current_body = None
    policy_route = route if filed_from_route is _USE_ANALYSIS_ROUTE else filed_from_route
    filed_from = tracker_filed_from.grade_publication(
        publication.text,
        policy_route if publication.field == "body" else None,
        current_body=current_body,
    )
    if filed_from.rule is not None:
        findings.append(Finding(
            filed_from.rule, 1, publication.field, filed_from.posture
        ))

    if branch.status == 1:
        rule = branch.verdict.rule
        if rule not in tracker_branch_scope.BRANCH_RULES:
            raise ValueError("branch grader returned an undeclared rule")
        remote_rule = rule in ("branch:unresolved-path", "branch:near-miss")
        posture = (
            "advise"
            if rule == "branch:near-miss" or (remote_rule and not remote_fresh)
            else "deny"
        )
        findings.append(Finding(rule, 1, publication.field, posture))

    lines = [context]
    if not branch.verdict.default_branch_tree_read:
        lines.append(branch.report)
    if not remote_fresh:
        lines.append(
            "origin/main fetch failed: unresolved-path and near-miss rules are advisory"
        )
    if positive_unverified:
        lines.append(
            "positive Branch state accepted without ancestry verification"
        )
    if publication.field == "body":
        lines.append(filed_from.report)
    for row in findings:
        line = (
            f"{row.posture}: {row.rule}: {row.count} finding(s) in {row.field}"
        )
        body_kind = row.rule.removeprefix("body:")
        if body_kind in BODY_REMEDIES:
            line += f"; remedy: {body_remedy(body_kind, route)}"
        if row.rule == tracker_coordinates.UNANCHORED:
            line += f"; remedy: {COORDINATE_REMEDY}"
        lines.append(line)
    if not findings:
        lines.append(f"scanned {publication.field}: 0 findings")
    return Analysis(tuple(findings), "\n".join(lines))


def authorize_issue_body(
    body: str,
    label: str,
    *,
    issue_number: int | None = None,
) -> None:
    """Apply the complete shared body-grade refusal for direct writers.

    Most tracker writes arrive as a shell command and enter through ``handle``.
    An in-process writer already holds the exact body, so making it reconstruct
    shell quoting would add a second, weaker extraction path. This entry point
    feeds that body string to the same ``tracker_bodies.grade`` call instead;
    every row in ``tracker_bodies.KINDS`` therefore refuses on both routes.
    """
    findings = tracker_bodies.grade(
        [tracker_bodies.Record("direct publication", label, tracker_bodies.ISSUE, body)]
    )
    if findings:
        kinds = ", ".join(row.kind for row in findings)
        raise ValueError(f"tracker body refused for {label}: {kinds}")
    coordinate_findings = tracker_coordinates.grade(body, label)
    if coordinate_findings:
        raise ValueError(
            f"tracker body refused for {label}: {tracker_coordinates.UNANCHORED}; "
            f"remedy: {COORDINATE_REMEDY}"
        )
    if issue_number is not None:
        # Lazy import avoids the module-level cycle: implementation_map uses
        # this direct-writer gate when it publishes the same body.
        from implementation_map import MAP_ISSUE, producer_stamp_problem

        if issue_number == MAP_ISSUE:
            problem = producer_stamp_problem(body)
            if problem is not None:
                raise ValueError(
                    f"tracker body refused for {label}: producer stamp: {problem}"
                )


def current_index() -> tuple[phi_scan.CorpusIndex, tuple[str, ...]]:
    names, dates = phi_scan.corpus_identifiers()
    return phi_scan.build_index(names, dates), tuple(phi_scan.missing_corpus_sources())


def refresh_default_branch(repo: Path | None = None) -> bool:
    """Refresh ``origin/main`` without relying on the clone's fetch mapping.

    The destination is explicit because ``_main_ancestry`` reads that ref. The
    leading ``+`` also follows a rewritten remote branch: without it, a stuck
    ref could verify a rewritten-away commit as on ``main``. The freshness gate
    omits ``+`` safely because its failed fetch reaches no ancestry verdict.
    """
    completed = subprocess.run(
        [
            "git",
            "fetch",
            "--no-tags",
            "origin",
            "+refs/heads/main:refs/remotes/origin/main",
        ],
        cwd=repo or Path(__file__).resolve().parent.parent,
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


def _issue_context(record: dict | None) -> TrackerRecord | None:
    return from_graphql(record)


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


def _missing_issue_create_analysis() -> Analysis:
    grade = tracker_filed_from.grade_publication("", ("issue", "create"))
    if grade.rule is None:
        raise ValueError("missing issue body returned no Filed-from finding")
    return Analysis(
        (Finding(grade.rule, 1, "body", grade.posture),),
        grade.report,
    )


UNREADABLE_REMEDIES = {
    "missing-file": (
        "no file was at this path when the hook ran, which is before any part "
        "of this command runs, and a refused command runs none of its stages; "
        "if this command writes the file, write it in a separate command "
        "first, otherwise create it, then run `python "
        "tools/tracker_publish_hook.py --text <path>` before retrying"
    ),
    "unrooted-path": (
        'put `cd "<folder>" && ` in front of the command, or write the whole '
        "path in quotes"
    ),
    "external-variable": (
        "resolve the variable and run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "pipe": (
        "save the piped text to a file and run `python tools/tracker_publish_hook.py "
        "--text <path>` before retrying"
    ),
    "command-substitution": (
        "run the substitution separately and then run `python "
        "tools/tracker_publish_hook.py --text <path>` before retrying"
    ),
    "expansion-exposed-inline": (
        "single-quote every segment of the body value, escaping an apostrophe "
        "between segments, or write the body to a file and pass its absolute "
        "path to --body-file; the value must be requoted before its content can "
        "be graded"
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


def unreadable_remedy(row: Unreadable) -> str:
    if row.kind == "expansion-exposed-inline" and row.field == "title":
        return (
            "single-quote every segment of the title value, escaping an "
            "apostrophe between segments; the value must be requoted before "
            "its content can be graded"
        )
    return UNREADABLE_REMEDIES[row.kind]


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
            lines = []
            for row in extracted.unreadable:
                reconstructed = row.reconstructed_path or row.source
                if row.resolved_against is not None:
                    resolved_against = row.resolved_against
                elif shell_reader.is_absolute_path(reconstructed):
                    resolved_against = "none (path was absolute)"
                else:
                    resolved_against = "none readable"
                lines.extend(
                    (
                        f"tracker pre-publish: NOT SCANNED -- unreadable {row.field} "
                        f"({row.kind}); {unreadable_remedy(row)}",
                        "tracker pre-publish: resolved against: "
                        + resolved_against
                        + f"; reconstructed path: {reconstructed}",
                    )
                )
            return _hook_response("deny", "\n".join(lines), UNSCANNED_REFUSAL)
        if (
            not extracted.publications
            and (extracted.grade_route or extracted.route) == ("issue", "create")
        ):
            return _hook_response("deny", _missing_issue_create_analysis().report)
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

        bound_publications = [
            with_tracker_record(
                publication,
                route=extracted.grade_route or extracted.route,
                context=issue,
            )
            for publication in extracted.publications
        ]
        analyses = [
            analyze(
                publication,
                index=index,
                issue=issue,
                remote_fresh=remote_fresh,
                route=extracted.grade_route or extracted.route,
            )
            for publication in bound_publications
        ]
        if (
            (extracted.grade_route or extracted.route) == ("issue", "create")
            and not any(row.field == "body" for row in bound_publications)
        ):
            analyses.append(_missing_issue_create_analysis())
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
            "deny",
            "tracker pre-publish HOOK FAILURE: "
            f"analysis failed ({type(exc).__name__})",
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
                filed_from_route=None,
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
    require_python_floor()
    raise SystemExit(main())
