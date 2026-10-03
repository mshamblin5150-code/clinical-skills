"""Read tracker publication commands above the generic shell reader.

The public boundary is extract and Extraction, plus gh_command_tokens,
loose_command_calls and LooseCommand for token-level observers. Route tables
and COMMAND_TOOLS declare the publication and shell populations it can read.
The complete reading boundary belongs to NOT_REACHED; policy belongs to the
consuming hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import NamedTuple

import shell_reader
from tracker_records import TrackerRecord


NOT_REACHED = (
    (
        "a file rewritten after the scan is graded on its earlier text",
        "The reader reads body-file bytes when extraction runs and does not "
        "observe a rewrite before publication.",
    ),
    (
        "which file an author meant is not established",
        "The reader reads the file the shell will open. On the modeled path, "
        "the shell and this reader alike remove an unquoted backslash, so a "
        "path spelled with one publishes whatever file that spelling opens, "
        "which need not be the file the author intended.",
    ),
    (
        "assignment expansion is reconstructed and reaches only the same "
        "command",
        "A variable assigned in an earlier command or exported by the "
        "environment is not resolvable here. A substitution behind a "
        "same-command variable is reported unreadable; directly supplied "
        "inline values instead receive an unreadable quoting-fidelity "
        "result.",
    ),
    (
        "the command-folder reader reaches literal absolute cd targets only",
        "A variable, substitution, parent, previous-folder, home, or "
        "relative cd target is reported unreadable rather than guessed at.",
    ),
    (
        "a shell command assembled at run time is invisible",
        "A command such as `G=gh; $G issue comment ...` carries no literal "
        "gh publication for the static classifier to recognize.",
    ),
    (
        "a program-formatted command is invisible",
        "A command assembled by string formatting inside a program is "
        "outside the literal command text this classifier reads.",
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
        "The non-publication list is a floor. An endpoint GitHub adds later "
        "is reported as an unclassified API call until the route table or "
        "the non-publication list names it.",
    ),
    (
        "a wrong non-publication entry silently passes",
        "A text-bearing endpoint placed on the non-publication list is left "
        "alone, so the classifier cannot establish that every listed "
        "endpoint publishes no tracker text.",
    ),
    (
        "a GraphQL document assembled at run time is unreadable",
        "The reader can judge a literal document, a same-command plain "
        "assignment, or a resolved field file. A document assembled by a "
        "substitution or an earlier command is reported unreadable rather "
        "than inferred.",
    ),
)


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


class LooseCommand(NamedTuple):
    executable: str
    route: tuple[str, ...]
    arguments: str
    argv_list: bool


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


def gh_command_tokens(
    command: str, routes: tuple[tuple[str, ...], ...]
) -> tuple[list[str], int] | None:
    """Return the first parsed ``gh`` invocation matching a declared route."""
    for tokens, index in shell_reader.executable_calls(command, "gh"):
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
