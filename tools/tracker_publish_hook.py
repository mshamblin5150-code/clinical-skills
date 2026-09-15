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

**One row advises on a retired citation**: a paragraph stating the
correct-in-place rule beside ``#436``, which rules nothing about corrections.
ADR 0191 ruled it reported rather than refused, because a record discussing the
defect quotes the pairing on purpose and tracker prose carries no
mention-versus-use exemption. It grades one literal pairing, grown on recorded
instances, and how narrow that is belongs to ``NOT_REACHED`` with every other
ceiling.

One anchor-free loose classifier also finds literal publications the precise
single-call reader did not reproduce, including quoted argv lists. A modeled
command carrying such a publication is refused unread before any partial grade;
the same classifier bounds the unmodeled-shell refusal and the implementation-
map post-hook's observation. Runtime assembly remains in ``NOT_REACHED``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import date as CalendarDate
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple

import phi_scan
from github_graphql import DeclaredAbsence, GraphQLResponseError, read_response
import tracker_bodies
import tracker_coordinates
import tracker_measurements
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
MODELED_SHELL = "bash"
COMMAND_TOOLS = {
    "Bash": MODELED_SHELL,
    "Monitor": MODELED_SHELL,
    "PowerShell": None,
}
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
        "the retired-citation row reaches one literal pairing",
        "It reports the correct-in-place rule stated beside #436 and nothing "
        "else. A paraphrase of the rule, the same rule attributed to another "
        "wrong record, and a citation whose claim about any other record is "
        "false are all outside it. Nothing here can establish that a cited "
        "record says what a sentence claims it says.",
    ),
    (
        "a shell command assembled at run time is invisible",
        "A command such as `G=gh; $G issue comment ...` carries no literal gh "
        "publication for the static classifier to recognize.",
    ),
    (
        "a program-formatted command is invisible",
        "A command assembled by string formatting inside a program is outside "
        "the literal command text this classifier reads.",
    ),
    (
        "an argv list assembled in pieces is invisible",
        "The argv-list form reaches one literal list only; a list assembled "
        "from variables or concatenated pieces is outside it.",
    ),
    (
        "an alias or function standing in for gh is invisible",
        "An alias or function invoked under another name carries no gh word "
        "for the static classifier to recognize.",
    ),
    (
        "a newly added API endpoint is refused until classified",
        "The non-publication list is a floor. An endpoint GitHub adds later is "
        "refused as an unclassified API call until the route table or the "
        "non-publication list names it.",
    ),
    (
        "a wrong non-publication entry silently passes",
        "A text-bearing endpoint placed on the non-publication list is left "
        "alone, so the classifier cannot establish that every listed endpoint "
        "publishes no tracker text.",
    ),
    (
        "a GraphQL document assembled at run time is unreadable",
        "The reader can judge a literal document, a same-command plain "
        "assignment, or a resolved field file. A document assembled by a "
        "substitution or an earlier command is refused rather than inferred.",
    ),
)


@dataclass(frozen=True)
class Publication:
    field: str
    text: str
    origin: str = "inline"
    path: Path | None = None
    resolved_against: str | None = None
    reconstructed_path: str | None = None
    record: TrackerRecord | None = None

    def __post_init__(self) -> None:
        if self.origin not in ("inline", "inline heredoc", "body-file"):
            raise ValueError("origin is not a recognized publication origin")
        if self.origin == "body-file":
            if not isinstance(self.path, Path) or not self.path.is_absolute():
                raise ValueError("path must be a resolved Path for body-file origin")
            if self.path != self.path.resolve():
                raise ValueError("path must be a resolved Path for body-file origin")
        elif self.path is not None:
            raise ValueError("path must be None unless origin is body-file")


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
    return replace(publication, record=record)


class Unreadable(NamedTuple):
    field: str
    kind: str
    source: str
    resolved_against: str | None = None
    reconstructed_path: str | None = None


class UnclassifiedApiCall(NamedTuple):
    kind: str
    endpoint: str


class ApiInput(NamedTuple):
    request: dict[str, object]
    origin: str
    path: Path | None = None
    resolved_against: str | None = None
    reconstructed_path: str | None = None


class Extraction(NamedTuple):
    route: tuple[str, ...] | None
    number: int | None
    publications: tuple[Publication, ...]
    unreadable: tuple[Unreadable, ...]
    grade_route: tuple[str, ...] | None = None
    unclassified_api_calls: tuple[UnclassifiedApiCall, ...] = ()


class Finding(NamedTuple):
    rule: str
    count: int
    field: str
    posture: str


class Analysis(NamedTuple):
    findings: tuple[Finding, ...]
    report: str


class CommandGrade(NamedTuple):
    scanned: bool
    denied: bool
    report: str


class LooseCommand(NamedTuple):
    executable: str
    route: tuple[str, ...]
    arguments: str
    argv_list: bool


_USE_ANALYSIS_ROUTE = object()


INLINE_FLAGS = {
    "--title": "title",
    "-t": "title",
    "--body": "body",
    "-b": "body",
}
FILE_FLAGS = {"--body-file": "body", "-F": "body"}
API_VALUE_OPTIONS = (
    ("raw-field", ("--raw-field", "-f")),
    ("field", ("--field", "-F")),
    ("cache", ("--cache",)),
    ("header", ("--header", "-H")),
    ("hostname", ("--hostname",)),
    ("input", ("--input",)),
    ("jq", ("--jq", "-q")),
    ("method", ("--method", "-X")),
    ("preview", ("--preview", "-p")),
    ("template", ("--template", "-t")),
)
PUBLISH_ASSIGNMENT_WORD = re.compile(
    r"\A(?P<name>[A-Za-z_][A-Za-z0-9_]*)="
    r"(?:'(?P<single>[^']*)'|\"(?P<double>[^\"]*)\"|"
    r"(?P<bare>[^'\"\s;&|]*))\Z",
    re.DOTALL,
)
API_NON_PUBLICATION_ENDPOINTS = (
    re.compile(r"/?markdown(?:\?.*)?\Z"),
    re.compile(r"/?repos/[^/?]+/[^/?]+/git/refs(?:/.+)?(?:\?.*)?\Z"),
)
API_NON_PUBLICATION_RECORD_ENDPOINTS = (
    re.compile(
        r"/?repos/[^/?]+/[^/?]+/issues/(?P<identifier>[^/?]+)/"
        r"(?:dependencies/(?:blocked_by|blocking)(?:/[^/?]+)?|"
        r"sub_issues(?:/priority)?|sub_issue|parent|labels(?:/[^/?]+)?|"
        r"assignees|reactions(?:/[^/?]+)?|lock)(?:\?.*)?\Z"
    ),
    re.compile(
        r"/?repos/[^/?]+/[^/?]+/pulls/(?P<identifier>[^/?]+)/"
        r"requested_reviewers(?:\?.*)?\Z"
    ),
    re.compile(
        r"/?repos/[^/?]+/[^/?]+/issues/comments/"
        r"(?P<identifier>[^/?]+)/reactions(?:/[^/?]+)?(?:\?.*)?\Z"
    ),
    re.compile(
        r"/?repos/[^/?]+/[^/?]+/pulls/comments/"
        r"(?P<identifier>[^/?]+)/reactions(?:/[^/?]+)?(?:\?.*)?\Z"
    ),
)
API_ROUTE_PATTERNS = (
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/issues/"
            r"(?P<identifier>[^/?]+)/comments(?:\?.*)?\Z"
        ),
        ("issue", "comment"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/pulls/"
            r"(?P<identifier>[^/?]+)/reviews(?:\?.*)?\Z"
        ),
        ("pr", "review"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/pulls/"
            r"(?P<identifier>[^/?]+)/comments(?:\?.*)?\Z"
        ),
        ("pr", "comment"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/pulls/"
            r"(?P<identifier>[^/?]+)(?:\?.*)?\Z"
        ),
        ("pr", "edit"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/issues/"
            r"(?P<identifier>[^/?]+)(?:\?.*)?\Z"
        ),
        ("issue", "edit"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/issues/comments/"
            r"(?P<identifier>[^/?]+)(?:\?.*)?\Z"
        ),
        ("issue", "comment"),
    ),
    (
        re.compile(
            r"/?repos/[^/?]+/[^/?]+/pulls/comments/"
            r"(?P<identifier>[^/?]+)(?:\?.*)?\Z"
        ),
        ("pr", "comment"),
    ),
)
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
RETIRED_CITATION = "citation:retired-correction-rule"
#: The correct-in-place rule as the tracker states it, matched without regard to
#: case. Records carrying one of these wordings attribute it to #436, which rules
#: nothing about corrections. Grown on evidence written in this repository, the
#: way ``spelling_scan``'s table grows, rather than by a rule over citations. How
#: many records that was on 2026-09-12 is ADR 0191's to state: it is a count over
#: a live tracker that nothing here re-derives, and the repair that record orders
#: drives it to zero.
CORRECT_IN_PLACE_PHRASES = (
    "below the advice",
    "acts on the advice",
    "acting on the advice",
)
RETIRED_CORRECTION_TICKET = re.compile(r"(?:#|issues/)436\b")
RETIRED_CITATION_REMEDY = (
    "#436 is a 160-char extraction ticket and rules nothing about corrections; "
    "cite ADR 0191, which rules this for the tracker. When repairing a record "
    "written before it, ADR 0016 goes in the sentence and ADR 0191 on the "
    "dated line, because that record's sentence says what a past session "
    "relied on"
)
PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
REDACTION_WALK_KINDS = (
    "phi:corpus-name",
    "phi:corpus-date",
    *(f"phi:{kind}" for kind in phi_scan.SHAPE_RULES),
    *(f"body:{kind}" for kind in tracker_bodies.KINDS),
    tracker_coordinates.UNANCHORED,
    "verdict:missing-discriminator",
    RETIRED_CITATION,
    *tracker_branch_scope.BRANCH_RULES,
)


def retired_citation_paragraphs(text: str) -> int:
    """Count paragraphs stating the correct-in-place rule beside the retired #436.

    The unit is the paragraph rather than a character window, and that is
    measured rather than chosen: over the population ADR 0191 states, a window is
    flat from the widest observed separation upward and the paragraph rule
    reproduces the identical members with no value to defend. It counts a
    deliberate quotation too -- tracker prose carries no mention-versus-use
    exemption, and the two this repository does have are a Python pragma and an
    own-line marker, neither of which a tracker record can use -- which is why
    the row advises and never denies.
    """
    return sum(
        1
        for paragraph in PARAGRAPH_BREAK.split(text.replace("\r\n", "\n").casefold())
        if any(phrase in paragraph for phrase in CORRECT_IN_PLACE_PHRASES)
        and RETIRED_CORRECTION_TICKET.search(paragraph)
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
LOOSE_PUBLICATION_FLAG = re.compile(
    r"(?<!\S)(?:(?:--body(?:-file)?|--title|--comment|--input|"
    r"--raw-field|--field)(?:\s|=|\Z)|-[btFcf](?:\S*|\s|\Z))"
)
LOOSE_ARGV_PUBLICATION_FLAG = re.compile(
    r"['\"](?:(?:--body(?:-file)?|--title|--comment|--input|"
    r"--raw-field|--field)(?:['\"]|=)|-[btFcf](?:['\"]|\S))",
    re.IGNORECASE,
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


def _aar_run_directory(path: Path | None) -> Path | None:
    """The run root for an AAR-owned body file, otherwise ``None``."""
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
    run = _aar_run_directory(publication.path)
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
    aar_publications = tuple(
        publication
        for publication in publications
        if _aar_run_directory(publication.path) is not None
    )
    findings = tuple(
        Finding("aar-quotation", 1, publication.field, "deny")
        for publication in aar_publications
        if _quotes_run_material(publication)
    )
    if aar_publications:
        report = (
            f"AAR quotation gate: {len(findings)} copied private-run span(s) "
            f"across {len(aar_publications)} AAR publication(s)"
        )
    else:
        report = (
            "AAR quotation gate: not applicable -- no publication under "
            "aar/publications/"
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


def loose_command_calls(
    command: str,
    executable: str,
    routes: tuple[tuple[str, ...], ...],
) -> tuple[LooseCommand, ...]:
    """Find literal command and argv-list routes without requiring an anchor."""
    found: list[tuple[int, LooseCommand]] = []
    for route in routes:
        words = r"\s+".join(re.escape(word) for word in route)
        text = re.compile(
            rf"\b{re.escape(executable)}\b\s+{words}\b"
            r"(?P<arguments>[^;&|}\r\n]*)",
            re.IGNORECASE,
        )
        argv_words = r"\s*,\s*".join(
            rf"['\"]{re.escape(word)}['\"]" for word in route
        )
        argv = re.compile(
            rf"['\"]{re.escape(executable)}['\"]\s*,\s*{argv_words}"
            r"(?P<arguments>[^\]\r\n]*)",
            re.IGNORECASE,
        )
        for match in text.finditer(command):
            found.append(
                (
                    match.start(),
                    LooseCommand(
                        executable,
                        route,
                        match.group("arguments"),
                        False,
                    ),
                )
            )
        for match in argv.finditer(command):
            found.append(
                (
                    match.start(),
                    LooseCommand(
                        executable,
                        route,
                        match.group("arguments"),
                        True,
                    ),
                )
            )
    return tuple(row for _position, row in sorted(found, key=lambda item: item[0]))


def _loose_api_is_publication(call: LooseCommand) -> bool:
    return _loose_has_publication_flag(call)


def _loose_has_publication_flag(call: LooseCommand) -> bool:
    flag = (
        LOOSE_ARGV_PUBLICATION_FLAG
        if call.argv_list
        else LOOSE_PUBLICATION_FLAG
    )
    return flag.search(call.arguments) is not None


def loose_publish_calls(command: str) -> tuple[LooseCommand, ...]:
    """Classify literal publications without claiming their bytes are reproducible."""
    publications: list[LooseCommand] = []
    for call in loose_command_calls(command, "gh", PUBLISH_ROUTES):
        if call.route == ("issue", "create"):
            publications.append(call)
            continue
        if call.route == ("api",):
            if _loose_api_is_publication(call):
                publications.append(call)
            continue
        if _loose_has_publication_flag(call):
            publications.append(call)
    return tuple(publications)


def _loose_publish_route(command: str) -> tuple[str, ...] | None:
    """Return the first likely publication in any literal command position."""
    calls = loose_publish_calls(command)
    return calls[0].route if calls else None


def _unreproduced_publish_route(command: str) -> tuple[str, ...] | None:
    """Return a loose publication the precise single-call reader did not reach."""
    calls = list(loose_publish_calls(command))
    publish = _publish_tokens(command)
    if publish is not None:
        tokens, start = publish
        precise_calls = loose_publish_calls(" ".join(tokens[start:]))
        if precise_calls:
            precise = precise_calls[0].route
            for index, call in enumerate(calls):
                if call.route == precise:
                    del calls[index]
                    break
    return calls[0].route if calls else None


def _api_value_option(
    arguments: list[str], index: int
) -> tuple[str, str | None, int] | None:
    token = arguments[index]
    for name, flags in API_VALUE_OPTIONS:
        for flag in flags:
            if token == flag:
                value = arguments[index + 1] if index + 1 < len(arguments) else None
                return name, value, 2 if value is not None else 1
            if flag.startswith("--") and token.startswith(flag + "="):
                return name, token[len(flag) + 1 :], 1
            if flag.startswith("-") and not flag.startswith("--"):
                if token.startswith(flag) and len(token) > len(flag):
                    return name, token[len(flag) :].removeprefix("="), 1
    return None


def _api_method(arguments: list[str]) -> str:
    explicit_method: str | None = None
    has_parameters = False
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is None:
            index += 1
            continue
        name, value, width = option
        if name == "method" and value is not None:
            explicit_method = value.upper()
        elif name in ("raw-field", "field", "input"):
            has_parameters = True
        index += width
    if explicit_method is not None:
        return explicit_method
    return "POST" if has_parameters else "GET"


def _api_explicit_method(arguments: list[str]) -> str | None:
    method: str | None = None
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is None:
            index += 1
            continue
        name, value, width = option
        if name == "method" and value is not None:
            method = value.upper()
        index += width
    return method


def _api_endpoint(arguments: list[str]) -> str:
    index = 0
    while index < len(arguments):
        token = arguments[index]
        option = _api_value_option(arguments, index)
        if option is not None:
            index += option[2]
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token
    return ""


def _api_endpoint_source(
    arguments: list[str], sources: tuple[str, ...] | None
) -> str:
    if sources is None:
        return ""
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is not None:
            index += option[2]
            continue
        if not arguments[index].startswith("-"):
            return sources[index]
        index += 1
    return ""


def _api_option_source_word(
    sources: tuple[str, ...] | None,
    index: int,
    width: int,
) -> str:
    if sources is None:
        return ""
    if width == 2:
        return sources[index + 1]
    return sources[index]


class _SourceCharacter(NamedTuple):
    value: str
    quote: str | None
    escaped: bool
    index: int


def _source_characters(source: str) -> tuple[_SourceCharacter, ...]:
    """Return shell characters with quote and escape provenance."""
    characters: list[_SourceCharacter] = []
    quote: str | None = None
    index = 0
    while index < len(source):
        character = source[index]
        if character == "\\" and quote != "'" and index + 1 < len(source):
            following = source[index + 1]
            if quote != '"' or following in '$`"\\\r\n':
                if following not in "\r\n":
                    characters.append(
                        _SourceCharacter(following, quote, True, index + 1)
                    )
                index += 2
                continue
        if character in ("'", '"'):
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            index += 1
            continue
        characters.append(_SourceCharacter(character, quote, False, index))
        index += 1
    return tuple(characters)


def _source_fanout_kind(
    characters: tuple[_SourceCharacter, ...],
    assignment_tilde: bool,
) -> str | None:
    brace_candidates: list[bool] = []
    bracket_start: int | None = None
    assignment_name_valid = False
    assignment_separator: int | None = None
    if assignment_tilde:
        for position, character in enumerate(characters):
            if (
                character.value == "="
                and character.quote is None
                and not character.escaped
            ):
                name = characters[:position]
                assignment_name_valid = bool(name) and all(
                    item.quote is None and not item.escaped for item in name
                ) and re.fullmatch(
                    r"[A-Za-z_][A-Za-z0-9_]*",
                    "".join(item.value for item in name),
                ) is not None
                assignment_separator = position
                break
    for position, character in enumerate(characters):
        if character.quote is not None or character.escaped:
            continue
        value = character.value
        if value == "~" and (
            position == 0
            or (
                assignment_name_valid
                and assignment_separator is not None
                and (
                    position == assignment_separator + 1
                    or (
                        position > assignment_separator + 1
                        and characters[position - 1].quote is None
                        and not characters[position - 1].escaped
                        and characters[position - 1].value == ":"
                    )
                )
            )
        ):
            return "tilde-expansion"
        if (
            value in ("<", ">")
            and position + 1 < len(characters)
            and characters[position + 1].value == "("
            and characters[position + 1].quote is None
            and not characters[position + 1].escaped
        ):
            return "process-substitution"
        if value == "{" and (
            position == 0
            or characters[position - 1].value != "$"
            or characters[position - 1].quote is not None
            or characters[position - 1].escaped
        ):
            brace_candidates.append(False)
        elif brace_candidates and (
            value == ","
            or (
                value == "."
                and position + 1 < len(characters)
                and characters[position + 1].value == "."
                and characters[position + 1].quote is None
                and not characters[position + 1].escaped
            )
        ):
            brace_candidates[-1] = True
        elif value == "}" and brace_candidates:
            if brace_candidates.pop():
                return "brace-expansion"
        if value in ("*", "?"):
            return "pathname-expansion"
        if value == "[":
            bracket_start = position
        elif value == "]" and bracket_start is not None:
            candidate = characters[bracket_start : position + 1]
            if len(candidate) > 2:
                candidate_text = "".join(item.value for item in candidate)
                if (
                    "$" not in candidate_text
                    and "`" not in candidate_text
                ):
                    return "pathname-expansion"
            bracket_start = None
    return None


def _analyze_source_word(
    source: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
    assignment_tilde: bool = False,
) -> tuple[str | None, str | None, set[str], bool, bool]:
    characters = _source_characters(source)
    fanout_kind = _source_fanout_kind(characters, assignment_tilde)
    if fanout_kind is not None:
        return None, fanout_kind, set(), True, False
    parts: list[str] = []
    unquoted_names: set[str] = set()
    failure_kind: str | None = None
    field_has_text = False
    injected_option = False
    position = 0
    variable = re.compile(
        r"\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
        r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))"
    )
    while position < len(characters):
        item = characters[position]
        character = item.value
        quote = item.quote
        index = item.index
        if item.escaped:
            if not field_has_text and character == "-":
                injected_option = True
            parts.append(character)
            field_has_text = True
            position += 1
            continue
        if quote != "'" and source.startswith("$(", index):
            return None, "command-substitution", unquoted_names, True, False
        if quote != "'" and character == "`":
            return None, "command-substitution", unquoted_names, True, False
        if quote != "'" and character == "$":
            match = variable.match(source, index)
            if match is None:
                return None, "external-variable", unquoted_names, True, False
            name = match.group("braced") or match.group("plain")
            if quote is None:
                unquoted_names.add(name)
            if name in assignments:
                assigned = assignments[name]
                parts.append(assigned)
                if quote is None:
                    for assigned_character in assigned:
                        if assigned_character.isspace():
                            field_has_text = False
                        else:
                            if not field_has_text and assigned_character == "-":
                                injected_option = True
                            field_has_text = True
                elif assigned:
                    if not field_has_text and assigned.startswith("-"):
                        injected_option = True
                    field_has_text = True
            elif name in substitutions:
                failure_kind = failure_kind or "command-substitution"
            else:
                failure_kind = failure_kind or "external-variable"
            position += 1
            while (
                position < len(characters)
                and characters[position].index < match.end()
            ):
                position += 1
            continue
        if not field_has_text and character == "-":
            injected_option = True
        parts.append(character)
        field_has_text = True
        position += 1
    return (
        "".join(parts),
        failure_kind,
        unquoted_names,
        False,
        injected_option,
    )


def _expand_source_word(
    source: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
    assignment_tilde: bool = False,
) -> tuple[str | None, str | None]:
    expanded, kind, _names, _dynamic, _injected = _analyze_source_word(
        source, assignments, substitutions, assignment_tilde
    )
    return (None if kind is not None else expanded), kind


def _api_expanded_arguments(
    arguments: list[str],
    sources: tuple[str, ...],
    command: str,
) -> list[str] | UnclassifiedApiCall:
    """Reconstruct each API argv word once before classifying its contents."""
    assignments, substitutions, _uncertain = _publish_assignments(command)
    option_value_indices: set[int] = set()
    separate_value_indices: set[int] = set()
    endpoint_index: int | None = None
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is None:
            if endpoint_index is None and not arguments[index].startswith("-"):
                endpoint_index = index
            index += 1
            continue
        name, value, width = option
        value_index = index + 1 if width == 2 and value is not None else index
        option_value_indices.add(value_index)
        if width == 2 and value is not None:
            separate_value_indices.add(value_index)
        index += width
    expanded_arguments: list[str] = []
    failed_indices: set[int] = set()
    for index, (argument, source) in enumerate(
        zip(arguments, sources, strict=True)
    ):
        expanded, kind, _names, _dynamic, _injected = _analyze_source_word(
            source,
            assignments,
            substitutions,
            index in separate_value_indices,
        )
        if kind is not None:
            failed_indices.add(index)
        expanded_arguments.append(
            argument
            if kind is not None and index == endpoint_index
            else (expanded if kind is None or expanded else argument)
        )

    endpoint = _api_endpoint(expanded_arguments)
    named_nonpublication = any(
        pattern.fullmatch(endpoint)
        for pattern in (
            *API_NON_PUBLICATION_ENDPOINTS,
            *API_NON_PUBLICATION_RECORD_ENDPOINTS,
        )
    )
    read_bypass = (
        _api_explicit_method(expanded_arguments) == "GET"
        or named_nonpublication
    )
    specialized_failures: set[int] = set()
    index = 0
    while index < len(expanded_arguments):
        option = _api_value_option(expanded_arguments, index)
        if option is None:
            index += 1
            continue
        name, value, width = option
        value_index = index + 1 if width == 2 and value is not None else index
        key = "" if value is None else value.partition("=")[0]
        if name == "input" or (
            name in ("raw-field", "field")
            and (
                key in ("body", "title")
                or (
                    endpoint == "graphql"
                    and key in ("query", "operationName")
                )
            )
        ):
            specialized_failures.add(value_index)
        index += width

    for index in failed_indices:
        argument = arguments[index]
        if index == endpoint_index:
            stable_endpoint = (
                not argument.startswith(("$", "`"))
            )
        else:
            stable_endpoint = False
        if (
            stable_endpoint
            or index in specialized_failures
            or (read_bypass and index in option_value_indices)
            or (
                named_nonpublication
                and endpoint_index is not None
                and index > endpoint_index
            )
        ):
            continue
        remedy = (
            "unclassified-api-identifier"
            if _api_dynamic_identifier_source(argument)
            else "unclassified-api-arguments"
        )
        return UnclassifiedApiCall(remedy, argument)
    return expanded_arguments


def _api_graphql_field(
    arguments: list[str],
    command: str,
    target: str,
    sources: tuple[str, ...] | None = None,
) -> str | Unreadable | None:
    found: str | Unreadable | None = None
    assignments, substitutions, _uncertain = _publish_assignments(command)
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is not None:
            name, option_value, width = option
            value = "" if option_value is None else option_value
            key, separator, value = value.partition("=")
            if name in ("raw-field", "field") and separator and key == target:
                source_word = ""
                if option_value is not None:
                    source_word = _api_option_source_word(
                        sources, index, width
                    )
                source_kind: str | None = None
                if source_word:
                    _expanded, source_kind = _expand_source_word(
                        source_word, assignments, substitutions, width == 2
                    )
                if value.startswith("@") and name == "field":
                    read = _read_file_field(
                        "body",
                        value[1:],
                        command,
                        assignments,
                        substitutions,
                        False,
                    )
                    found = read if isinstance(read, Unreadable) else read.text
                elif source_kind is not None:
                    found = Unreadable("body", source_kind, value)
                elif source_word:
                    found = value
                else:
                    expanded, kind = shell_reader.expand(
                        value,
                        assignments,
                        substitutions,
                    )
                    found = (
                        Unreadable("body", kind, value)
                        if kind is not None
                        else expanded
                    )
            index += width
            continue
        index += 1
    return found


def _graphql_operation(
    document: str, operation_name: str | None = None
) -> str | None:
    operations: list[tuple[str | None, str]] = []
    braces = 0
    parentheses = 0
    brackets = 0
    definition: str | None = None
    awaiting_name = False
    index = 0
    while index < len(document):
        if document.startswith('"""', index):
            end = document.find('"""', index + 3)
            index = len(document) if end < 0 else end + 3
            continue
        character = document[index]
        if character == '"':
            index += 1
            while index < len(document):
                if document[index] == "\\":
                    index += 2
                elif document[index] == '"':
                    index += 1
                    break
                else:
                    index += 1
            continue
        if character == "#":
            end = re.search(r"[\r\n]", document[index:])
            index = len(document) if end is None else index + end.start() + 1
            continue
        if character == "{":
            if braces == parentheses == brackets == 0:
                if definition is None:
                    operations.append((None, "query"))
                elif awaiting_name and definition != "fragment":
                    operations.append((None, definition))
                    awaiting_name = False
                braces = 1
            else:
                braces += 1
            index += 1
            continue
        if character == "}":
            braces = max(0, braces - 1)
            if braces == parentheses == brackets == 0:
                definition = None
                awaiting_name = False
            index += 1
            continue
        if character == "(":
            if braces == parentheses == brackets == 0 and awaiting_name:
                operations.append((None, definition or "query"))
                awaiting_name = False
            parentheses += 1
        elif character == ")":
            parentheses = max(0, parentheses - 1)
        elif character == "[":
            brackets += 1
        elif character == "]":
            brackets = max(0, brackets - 1)
        elif character == "@" and braces == parentheses == brackets == 0:
            if awaiting_name:
                operations.append((None, definition or "query"))
                awaiting_name = False
        elif braces == parentheses == brackets == 0:
            name = re.match(r"[_A-Za-z][_0-9A-Za-z]*", document[index:])
            if name is not None:
                token = name.group(0)
                if awaiting_name and definition != "fragment":
                    operations.append((token, definition or "query"))
                    awaiting_name = False
                elif definition is None and token in (
                    "query",
                    "mutation",
                    "subscription",
                    "fragment",
                ):
                    definition = token
                    awaiting_name = token != "fragment"
                index += len(token)
                continue
        index += 1
    if operation_name is not None:
        selected = [operation for name, operation in operations if name == operation_name]
        return selected[0] if len(selected) == 1 else None
    operation_kinds = {operation for _name, operation in operations}
    if "mutation" in operation_kinds:
        return "mutation"
    return "query" if operation_kinds == {"query"} else None


def _api_identifier(
    identifier: str, command: str, reconstruct: bool = True
) -> str | None:
    assignments, substitutions, _uncertain = _publish_assignments(command)
    if reconstruct:
        expanded, kind = shell_reader.expand(
            identifier, assignments, substitutions
        )
    else:
        expanded, kind = identifier, None
    if (
        kind is not None
        or expanded is None
        or expanded == ""
        or re.search(r"[/\?$`]", expanded)
    ):
        return None
    return expanded


def _endpoint_failure_is_query_only(source: str) -> bool:
    query = source.find("?")
    if query < 0:
        return False
    dynamic_positions = [match.start() for match in re.finditer(r"[$`]", source)]
    return bool(dynamic_positions) and all(
        position > query for position in dynamic_positions
    )


def _expand_publish_assignment(
    value: str,
    assignments: dict[str, str],
    substitutions: frozenset[str],
) -> tuple[str | None, str | None]:
    """Expand shell-active named variables once without rescanning replacements."""
    parts: list[str] = []
    index = 0
    variable = re.compile(
        r"\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
        r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))"
    )
    while index < len(value):
        if value[index] != "$":
            parts.append(value[index])
            index += 1
            continue
        match = variable.match(value, index)
        if match is None:
            return None, "external-variable"
        name = match.group("braced") or match.group("plain")
        if name in assignments:
            parts.append(assignments[name])
        elif name in substitutions:
            return None, "command-substitution"
        else:
            return None, "external-variable"
        index = match.end()
    return "".join(parts), None


def _publish_assignments(
    command: str,
) -> tuple[dict[str, str], frozenset[str], bool]:
    """Read persistent assignments completed before the modeled publication."""
    assignments: dict[str, str] = {}
    substitutions: set[str] = set()
    uncertain_shell_state = False
    pieces = shell_reader.shell_pieces(command)
    conditional = False
    for position, piece in enumerate(pieces):
        if piece in shell_reader.SEPARATORS:
            if piece in ("&&", "||", "|", "&"):
                assignments.clear()
                substitutions.clear()
                conditional = True
                uncertain_shell_state = True
            elif piece in (";", "\n"):
                conditional = False
            continue
        for tokens, index in shell_reader.executable_calls(piece, "gh"):
            tail = tokens[index + 1 :]
            if not tail:
                continue
            route = ("api",) if tail[0] == "api" else tuple(tail[:2])
            if route in PUBLISH_ROUTES:
                return (
                    assignments,
                    frozenset(substitutions),
                    uncertain_shell_state,
                )
        words = shell_reader.source_words(piece)
        if not words or conditional:
            continue
        assignment_words = words
        if not assignment_words or any(
            re.match(r"[A-Za-z_][A-Za-z0-9_]*=", word) is None
            for word in assignment_words
        ):
            assignments.clear()
            substitutions.clear()
            uncertain_shell_state = True
            continue
        next_piece = pieces[position + 1] if position + 1 < len(pieces) else None
        if next_piece in ("|", "&"):
            continue
        for word in assignment_words:
            match = PUBLISH_ASSIGNMENT_WORD.fullmatch(word)
            name = word.partition("=")[0]
            if match is None:
                assignments.pop(name, None)
                if "$(" in word or "`" in word:
                    substitutions.add(name)
                else:
                    substitutions.discard(name)
                continue
            single = match.group("single")
            if single is not None:
                assignments[name] = single
                substitutions.discard(name)
                continue
            double = match.group("double")
            value = double
            if value is None:
                value = match.group("bare") or ""
            if "$(" in value or "`" in value:
                assignments.pop(name, None)
                substitutions.add(name)
                continue
            if (
                double is None and "\\" in value
            ) or (
                double is not None
                and re.search(r'\\(?:[$`"\\]|\r?\n)', value) is not None
            ):
                assignments.pop(name, None)
                substitutions.discard(name)
                continue
            expanded, kind = _expand_publish_assignment(
                value, assignments, frozenset(substitutions)
            )
            if (
                kind is not None
                or expanded is None
                or "`" in expanded
            ):
                assignments.pop(name, None)
                if kind == "command-substitution":
                    substitutions.add(name)
                else:
                    substitutions.discard(name)
                continue
            assignments[name] = expanded
            substitutions.discard(name)
    return assignments, frozenset(substitutions), uncertain_shell_state


def _api_identifier_source(argument: str, name: str) -> bool:
    patterns = [pattern for pattern, _route in API_ROUTE_PATTERNS]
    patterns.extend(API_NON_PUBLICATION_RECORD_ENDPOINTS)
    for pattern in patterns:
        match = pattern.fullmatch(argument)
        if match is not None and match.group("identifier") in (
            f"${name}",
            "${" + name + "}",
        ):
            return True
    return False


def _api_dynamic_identifier_source(argument: str) -> bool:
    patterns = [pattern for pattern, _route in API_ROUTE_PATTERNS]
    patterns.extend(API_NON_PUBLICATION_RECORD_ENDPOINTS)
    return any(
        match is not None and re.search(r"[$`]", match.group("identifier"))
        for pattern in patterns
        if (match := pattern.fullmatch(argument)) is not None
    )


def _api_dynamic_arguments(
    arguments: list[str],
    sources: tuple[str, ...],
    command: str,
    read_bypass: bool = False,
    nonpublication_bypass: bool = False,
) -> UnclassifiedApiCall | None:
    assignments, substitutions, uncertain_shell_state = _publish_assignments(command)
    separate_value_indices: set[int] = set()
    endpoint_index: int | None = None
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is None:
            if endpoint_index is None and not arguments[index].startswith("-"):
                endpoint_index = index
            index += 1
            continue
        _name, value, width = option
        if width == 2 and value is not None:
            separate_value_indices.add(index + 1)
        index += width
    for index, (argument, source) in enumerate(
        zip(arguments, sources, strict=True)
    ):
        if (
            nonpublication_bypass
            and endpoint_index is not None
            and index > endpoint_index
        ):
            continue
        (
            expanded_source,
            source_kind,
            names,
            dynamic,
            injected_option,
        ) = _analyze_source_word(
            source,
            assignments,
            substitutions,
            index in separate_value_indices,
        )
        if dynamic:
            kind = (
                "unclassified-api-identifier"
                if _api_dynamic_identifier_source(argument)
                else "unclassified-api-arguments"
            )
            return UnclassifiedApiCall(kind, argument)
        if names and source_kind is not None:
            kind = (
                "unclassified-api-identifier"
                if _api_dynamic_identifier_source(argument)
                else "unclassified-api-arguments"
            )
            return UnclassifiedApiCall(kind, argument)
        if names and injected_option:
            return UnclassifiedApiCall("unclassified-api-arguments", argument)
        for name in names:
            if name not in assignments:
                kind = (
                    "unclassified-api-identifier"
                    if _api_identifier_source(argument, name)
                    else "unclassified-api-arguments"
                )
                return UnclassifiedApiCall(kind, argument)
            value = assignments[name]
            split_capable = re.search(r"[\s*?\[]", value) is not None
            if not value and _api_identifier_source(argument, name):
                return UnclassifiedApiCall(
                    "unclassified-api-identifier", argument
                )
            if uncertain_shell_state or "IFS" in assignments or not value:
                return UnclassifiedApiCall("unclassified-api-arguments", argument)
            if split_capable and (
                not read_bypass
                or re.search(r"[*?\[]", value) is not None
            ):
                return UnclassifiedApiCall("unclassified-api-arguments", argument)
    return None


def _api_route_match(
    endpoint: str, command: str, reconstruct_identifier: bool = True
) -> tuple[tuple[str, ...], str] | UnclassifiedApiCall | None:
    for pattern, route in API_ROUTE_PATTERNS:
        match = pattern.fullmatch(endpoint)
        if match is None:
            continue
        identifier = match.group("identifier")
        expanded = _api_identifier(identifier, command, reconstruct_identifier)
        if expanded is None:
            return UnclassifiedApiCall("unclassified-api-identifier", endpoint)
        return route, expanded
    return None


def _api_grade_route(
    arguments: list[str],
    command: str = "",
    sources: tuple[str, ...] | None = None,
) -> tuple[str, ...] | Unreadable | UnclassifiedApiCall | None:
    if _api_method(arguments) == "GET":
        return None
    endpoint = _api_endpoint(arguments)
    endpoint_source = _api_endpoint_source(arguments, sources)
    endpoint_expanded = False
    if endpoint_source:
        assignments, substitutions, _uncertain = _publish_assignments(command)
        expanded_endpoint, endpoint_kind = _expand_source_word(
            endpoint_source, assignments, substitutions
        )
        if endpoint_kind is None and expanded_endpoint is not None:
            endpoint = expanded_endpoint
            endpoint_expanded = True
        elif not _endpoint_failure_is_query_only(endpoint_source):
            kind = (
                "unclassified-api-identifier"
                if _api_dynamic_identifier_source(endpoint)
                else "unclassified-api-endpoint"
            )
            return UnclassifiedApiCall(kind, endpoint)
    if any(pattern.fullmatch(endpoint) for pattern in API_NON_PUBLICATION_ENDPOINTS):
        return None
    for pattern in API_NON_PUBLICATION_RECORD_ENDPOINTS:
        match = pattern.fullmatch(endpoint)
        if match is None:
            continue
        if _api_identifier(
            match.group("identifier"), command, not endpoint_expanded
        ) is None:
            return UnclassifiedApiCall("unclassified-api-identifier", endpoint)
        return None
    if endpoint == "graphql":
        api_input = _api_input(arguments, command, sources)
        if isinstance(api_input, Unreadable):
            return api_input
        if api_input is not None:
            request_document = api_input.request.get("query")
            request_operation = api_input.request.get("operationName")
            document = request_document if isinstance(request_document, str) else None
            operation_name = (
                request_operation if isinstance(request_operation, str) else None
            )
        else:
            document = _api_graphql_field(
                arguments, command, "query", sources
            )
            operation_name = _api_graphql_field(
                arguments, command, "operationName", sources
            )
        if isinstance(document, Unreadable):
            return document
        if isinstance(operation_name, Unreadable):
            return operation_name
        if document is not None:
            operation = _graphql_operation(document, operation_name)
            if operation == "query":
                return None
            if operation == "mutation":
                return UnclassifiedApiCall("unclassified-api-mutation", "graphql")
    route_match = _api_route_match(endpoint, command, not endpoint_expanded)
    if isinstance(route_match, UnclassifiedApiCall):
        return route_match
    if route_match is not None:
        return route_match[0]
    if re.fullmatch(
        r"/?repos/[^/?]+/[^/?]+/pulls(?:\?.*)?\Z", endpoint
    ):
        return ("pr", "create")
    if re.fullmatch(
        r"/?repos/[^/?]+/[^/?]+/issues(?:\?.*)?\Z", endpoint
    ):
        return ("issue", "create")
    return UnclassifiedApiCall("unclassified-api-endpoint", endpoint)


def _record_number(
    route: tuple[str, ...],
    arguments: list[str],
    command: str = "",
    sources: tuple[str, ...] | None = None,
) -> int | None:
    if route == ("api",):
        endpoint = _api_endpoint(arguments)
        reconstruct_identifier = True
        endpoint_source = _api_endpoint_source(arguments, sources)
        if endpoint_source:
            assignments, substitutions, _uncertain = _publish_assignments(command)
            expanded_endpoint, endpoint_kind = _expand_source_word(
                endpoint_source, assignments, substitutions
            )
            if endpoint_kind is None and expanded_endpoint is not None:
                endpoint = expanded_endpoint
                reconstruct_identifier = False
            elif not _endpoint_failure_is_query_only(endpoint_source):
                return None
        route_match = _api_route_match(
            endpoint, command, reconstruct_identifier
        )
        if route_match is None or isinstance(route_match, UnclassifiedApiCall):
            return None
        identifier = route_match[1]
        return (
            int(identifier)
            if identifier is not None and identifier.isdecimal()
            else None
        )
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
    expand_source: bool = True,
) -> Publication | Unreadable:
    expanded, kind = (
        shell_reader.expand(source, assignments, substitutions)
        if expand_source
        else (source, None)
    )
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
    path = shell_reader.candidate_file(source)
    if path is None:
        return Unreadable(
            field,
            "missing-file",
            source,
            None if folder is None else str(folder),
            source,
        )
    return Publication(
        field,
        path.read_text(encoding="utf-8"),
        "body-file",
        path,
        None if folder is None else str(folder),
        source,
    )


def _read_api_input(
    source: str, command: str, expand_source: bool = True
) -> ApiInput | Unreadable:
    assignments, substitutions, _uncertain = _publish_assignments(command)
    if source == "-":
        heredoc = HEREDOC.search(command)
        if heredoc is None:
            return Unreadable("body", "pipe", source)
        request_text = heredoc.group("body")
        origin = "inline heredoc"
        path = None
        resolved_against = None
        reconstructed_path = None
    else:
        read = _read_file_field(
            "body",
            source,
            command,
            assignments,
            substitutions,
            expand_source,
        )
        if isinstance(read, Unreadable):
            return read
        request_text = read.text
        origin = read.origin
        path = read.path
        resolved_against = read.resolved_against
        reconstructed_path = read.reconstructed_path
    try:
        request = json.loads(request_text)
        if not isinstance(request, dict):
            raise ValueError("API input is not an object")
    except (json.JSONDecodeError, ValueError):
        return Unreadable(
            "body",
            "invalid-input",
            origin,
            resolved_against,
            reconstructed_path,
        )
    return ApiInput(
        request,
        origin,
        path,
        resolved_against,
        reconstructed_path,
    )


def _api_input(
    arguments: list[str],
    command: str,
    sources: tuple[str, ...] | None = None,
) -> ApiInput | Unreadable | None:
    source: str | None = None
    source_argument = ""
    found = False
    index = 0
    while index < len(arguments):
        option = _api_value_option(arguments, index)
        if option is None:
            index += 1
            continue
        name, value, width = option
        if name == "input":
            found = True
            source = value
            if value is not None:
                source_argument = _api_option_source_word(
                    sources, index, width
                )
        index += width
    if not found:
        return None
    if source is None:
        return Unreadable("body", "missing-value", "--input")
    if source_argument:
        assignments, substitutions, _uncertain = _publish_assignments(command)
        expanded, kind = _expand_source_word(
            source_argument, assignments, substitutions
        )
        if kind is not None or expanded is None:
            return Unreadable("body", kind or "external-variable", source)
    return _read_api_input(source, command, not bool(source_argument))


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
    if route == ("api",):
        expanded_arguments = _api_expanded_arguments(
            arguments, argument_sources, command
        )
        if isinstance(expanded_arguments, UnclassifiedApiCall):
            return Extraction(
                route, None, (), (), None, (expanded_arguments,)
            )
        endpoint = _api_endpoint(expanded_arguments)
        listed_nonpublication = any(
            pattern.fullmatch(endpoint)
            for pattern in (
                *API_NON_PUBLICATION_ENDPOINTS,
                *API_NON_PUBLICATION_RECORD_ENDPOINTS,
            )
        )
        dynamic_arguments = _api_dynamic_arguments(
            arguments,
            argument_sources,
            command,
            _api_explicit_method(expanded_arguments) == "GET"
            or listed_nonpublication,
            listed_nonpublication,
        )
        if dynamic_arguments is not None:
            return Extraction(
                route, None, (), (), None, (dynamic_arguments,)
            )
        arguments = expanded_arguments
    number = _record_number(
        route,
        arguments,
        command,
        argument_sources,
    )
    api_grade = (
        _api_grade_route(arguments, command, argument_sources)
        if route == ("api",)
        else route
    )
    if isinstance(api_grade, UnclassifiedApiCall):
        return Extraction(route, number, (), (), None, (api_grade,))
    if isinstance(api_grade, Unreadable):
        return Extraction(route, number, (), (api_grade,), None)
    grade_route = api_grade
    if route == ("api",) and grade_route is None:
        return Extraction(route, number, (), (), None)
    publications: list[Publication] = []
    assignments, substitutions, _uncertain = _publish_assignments(command)
    index = 0
    while index < len(arguments):
        token = arguments[index]
        source_token = argument_sources[index]
        api_option = _api_value_option(arguments, index) if route == ("api",) else None
        if (
            api_option is not None
            and api_option[0] in ("raw-field", "field", "input")
            and api_option[1] is None
        ):
            unreadable = Unreadable("body", "missing-value", token)
            return Extraction(
                route, number, tuple(publications), (unreadable,), grade_route
            )
        body_flag = (
            token in INLINE_FLAGS
            or token in FILE_FLAGS
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
        if api_option is not None and api_option[0] in ("raw-field", "field"):
            option_name, option_value, width = api_option
            if option_value is None:
                unreadable = Unreadable("body", "missing-value", token)
                return Extraction(
                    route, number, tuple(publications), (unreadable,), grade_route
                )
            key, separator, value = option_value.partition("=")
            if separator and key in ("body", "title"):
                source_argument = _api_option_source_word(
                    argument_sources,
                    index,
                    width,
                )
                _expanded, source_kind, _names, _dynamic, _injected = (
                    _analyze_source_word(
                        source_argument,
                        assignments,
                        substitutions,
                        width == 2,
                    )
                )
                if source_kind is not None:
                    unreadable = Unreadable(key, source_kind, source_argument)
                    return Extraction(
                        route,
                        number,
                        tuple(publications),
                        (unreadable,),
                        grade_route,
                    )
                if value.startswith("@") and option_name == "field":
                    read = _read_file_field(
                        key,
                        value[1:],
                        command,
                        assignments,
                        substitutions,
                        False,
                    )
                    if isinstance(read, Unreadable):
                        return Extraction(route, number, tuple(publications), (read,))
                    publications.append(read)
                else:
                    publications.append(Publication(key, value))
            index += width
            continue
        if api_option is not None and api_option[0] == "input":
            source = api_option[1]
            if source is None:
                raise ValueError("missing API input was not refused")
            source_argument = _api_option_source_word(
                argument_sources,
                index,
                api_option[2],
            )
            _expanded, source_kind, _names, _dynamic, _injected = (
                _analyze_source_word(
                    source_argument,
                    assignments,
                    substitutions,
                    api_option[2] == 2,
                )
            )
            if source_kind is not None:
                unreadable = Unreadable("body", source_kind, source_argument)
                return Extraction(
                    route,
                    number,
                    tuple(publications),
                    (unreadable,),
                    grade_route,
                )
            api_input = _read_api_input(source, command, False)
            if isinstance(api_input, Unreadable):
                return Extraction(
                    route,
                    number,
                    tuple(publications),
                    (api_input,),
                    grade_route,
                )
            for field in ("title", "body"):
                value = api_input.request.get(field)
                if isinstance(value, str):
                    publications.append(
                        Publication(
                            field,
                            value,
                            api_input.origin,
                            api_input.path,
                            api_input.resolved_against,
                            api_input.reconstructed_path,
                        )
                    )
            index += api_option[2]
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
    findings.extend(
        Finding(row.rule, 1, publication.field, "deny")
        for row in tracker_measurements.grade_current(
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
    retired_citations = retired_citation_paragraphs(publication.text)
    if retired_citations:
        findings.append(Finding(
            RETIRED_CITATION, retired_citations, publication.field, "advise"
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
        if row.rule == RETIRED_CITATION:
            line += f"; remedy: {RETIRED_CITATION_REMEDY}"
        if row.rule == tracker_measurements.INSIDE_QUOTE:
            line += "; remedy: add one blank line above the Measured at declaration"
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
    measurement_findings = tracker_measurements.grade_current(body, label)
    if measurement_findings:
        rules = ", ".join(row.rule for row in measurement_findings)
        raise ValueError(f"tracker body refused for {label}: {rules}")
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
    declared_absences = tuple(
        DeclaredAbsence("NOT_FOUND", ("repository", f"record_{number}"))
        for number in sorted(numbers)
    )
    try:
        data = read_response(subprocess.run(
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
        ).stdout, declared_absences).data
    except GraphQLResponseError as error:
        raise ValueError(str(error)) from error
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
        "first, otherwise create it, then save the exact publication command "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "unrooted-path": (
        'put `cd "<folder>" && ` in front of the command, or write the whole '
        "path in quotes"
    ),
    "external-variable": (
        "resolve the variable in the publication command, save that command, "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "pipe": (
        "save the piped text to a body file, update and save the publication "
        "command, and run `python tools/tracker_publish_hook.py --command-file "
        "<path>` before retrying"
    ),
    "command-substitution": (
        "run the substitution separately, save the resolved publication command, "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "expansion-exposed-inline": (
        "single-quote every segment of the body value, escaping an apostrophe "
        "between segments, or write the body to a file and pass its absolute "
        "path to --body-file; the value must be requoted before its content can "
        "be graded"
    ),
    "invalid-input": (
        "repair the JSON input, save the exact publication command, and run "
        "`python tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
    "invalid-command": (
        "repair and save the exact publication command, and run `python "
        "tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
    "missing-value": (
        "supply the flag value, save the exact publication command, and run "
        "`python tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
}
UNCLASSIFIED_API_REMEDIES = {
    "unclassified-api-mutation": (
        "a GraphQL mutation is an unclassified API call; publish through `gh issue` "
        "or `gh pr`, or use a named REST `/issues` or `/pulls` endpoint"
    ),
    "unclassified-api-endpoint": (
        "this unclassified API call names neither the route table nor the "
        "non-publication list; add the endpoint to the correct classification "
        "before retrying"
    ),
    "unclassified-api-identifier": (
        "the record identifier cannot be reconstructed; type the literal "
        "identifier in the endpoint before retrying"
    ),
    "unclassified-api-arguments": (
        "an unquoted runtime expansion can change the API argument list; "
        "type the endpoint and options explicitly before retrying"
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


def _unreadable_report(extracted: Extraction) -> str:
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
    return "\n".join(lines)


def _unclassified_api_report(extracted: Extraction) -> str:
    return "\n".join(
        "tracker pre-publish: NOT SCANNED -- unclassified API call "
        f"({row.kind}); {UNCLASSIFIED_API_REMEDIES[row.kind]}"
        for row in extracted.unclassified_api_calls
    )


def grade_command(command: str) -> CommandGrade | None:
    """Grade one Bash publication command without writing the hook marker."""
    if _unreproduced_publish_route(command) is not None:
        return CommandGrade(
            False,
            True,
            "tracker pre-publish: NOT SCANNED -- unreproduced publication; "
            "publish one top-level `gh` command per Bash call, and if a script "
            "merely mentions a publication, run that script from a file",
        )
    extracted = extract(command)
    if extracted.route is None:
        return None
    if extracted.unclassified_api_calls:
        return CommandGrade(False, True, _unclassified_api_report(extracted))
    if extracted.unreadable:
        return CommandGrade(False, True, _unreadable_report(extracted))

    quotation = aar_quotation_analysis(extracted.publications)
    if not extracted.publications:
        if (extracted.grade_route or extracted.route) == ("issue", "create"):
            analysis = _missing_issue_create_analysis()
            return CommandGrade(True, True, analysis.report)
        return CommandGrade(
            False,
            False,
            "tracker pre-publish: NOT SCANNED -- no publication fields "
            "recognized in the command",
        )

    index, missing = current_index()
    remote_fresh = refresh_default_branch()
    # ``tracker_scan`` splits title and body so a finding identifies the field
    # to edit. A readback identifies records, not fields, so that reason does
    # not transfer and both fields deliberately form one set.
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

    route = extracted.grade_route or extracted.route
    bound_publications = [
        with_tracker_record(publication, route=route, context=issue)
        for publication in extracted.publications
    ]
    analyses = [
        analyze(
            publication,
            index=index,
            issue=issue,
            remote_fresh=remote_fresh,
            route=route,
        )
        for publication in bound_publications
    ]
    if route == ("issue", "create") and not any(
        row.field == "body" for row in bound_publications
    ):
        analyses.append(_missing_issue_create_analysis())
    analyses.append(quotation)

    lines = [
        f"tracker pre-publish: {publication.field} read from {publication.origin}"
        for publication in extracted.publications
    ]
    if missing:
        lines.append(
            "PHI corpus layer incomplete: " + ", ".join(missing) + " not available"
        )
    lines.extend(readback_lines)
    lines.extend(analysis.report for analysis in analyses)
    denied = any(
        finding.posture == "deny"
        for analysis in analyses
        for finding in analysis.findings
    )
    return CommandGrade(True, denied, "\n".join(lines))


def handle(payload: dict) -> dict:
    """Return one Claude Code hook response without echoing tracker text."""
    try:
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("tool_input is not an object")
        command = tool_input.get("command")
        if command is None:
            return {}
        if not isinstance(command, str):
            raise ValueError("tool_input.command is not text")
        tool_name = payload.get("tool_name")
        if not isinstance(tool_name, str):
            raise ValueError("tool_name is not text")
        if COMMAND_TOOLS.get(tool_name) != MODELED_SHELL:
            route = _loose_publish_route(command)
            if route is None:
                return {}
            return _hook_response(
                "deny",
                "tracker pre-publish: NOT SCANNED -- "
                f"{tool_name} carries an unmodeled shell; save the tracker text "
                "to a file and publish it through Bash so the text can be graded",
                UNSCANNED_REFUSAL,
            )
        grade = grade_command(command)
        if grade is None:
            return {}
        if not grade.scanned and not grade.denied:
            return {}
        write_marker()
        return _hook_response(
            "deny" if grade.denied else None,
            grade.report,
            UNSCANNED_REFUSAL if not grade.scanned else BRANCH_SCOPE_REFUSAL,
        )
    except Exception as exc:
        return _hook_response(
            "deny",
            "tracker pre-publish HOOK FAILURE: "
            f"analysis failed ({type(exc).__name__})",
        )


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) == 2 and arguments[0] == "--command-file":
        try:
            command = Path(arguments[1]).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(
                "tracker pre-publish: NOT SCANNED -- unreadable command file "
                f"({type(exc).__name__})",
                file=sys.stderr,
            )
            return 2
        try:
            grade = grade_command(command)
        except Exception as exc:
            print(
                "tracker pre-publish: NOT SCANNED -- "
                f"analysis failed ({type(exc).__name__})",
                file=sys.stderr,
            )
            return 2
        if grade is None:
            print(
                "tracker pre-publish: NOT SCANNED -- no publication route "
                "recognized in the command file"
            )
            return 2
        print(grade.report)
        if not grade.scanned:
            return 2
        return 1 if grade.denied else 0
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
