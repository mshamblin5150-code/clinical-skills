"""Read command structure without invoking or expanding a shell."""

from __future__ import annotations

import re
import shlex
import sys
from collections.abc import Callable, Iterator
from pathlib import Path


SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}
HEREDOC = re.compile(
    r"<<-?\s*['\"]?(?P<tag>[A-Za-z_][A-Za-z0-9_]*)['\"]?[ \t]*\r?\n"
    r"(?P<body>.*?)\r?\n(?P=tag)(?:\r?\n|\Z)", re.DOTALL,
)
PLAIN_ASSIGNMENT = re.compile(
    r"(?:\A|[;&|\n]\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)="
    r"(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<bare>[^\s;&|]+))"
)
VARIABLE = re.compile(
    r"\A\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
    r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))(?P<rest>/.*)?\Z", re.DOTALL,
)
MSYS_PATH = re.compile(r"\A/(?P<drive>[A-Za-z])/(?P<rest>.*)\Z", re.DOTALL)
LITERAL_CD = re.compile(r"\Acd\s+(?P<target>\"[^\"]*\"|'[^']*'|[^\s;&|]+)\s*\Z")


def shell_pieces(command: str) -> list[str]:
    """Split commands at unquoted separators without expanding them."""
    command = HEREDOC.sub(
        lambda match: match.group(0)[:match.start("body") - match.start()]
        + match.group(0)[match.end("body") - match.start():], command,
    )
    pieces: list[str] = []
    current: list[str] = []
    index = 0
    quote: str | None = None
    substitution_depth = 0
    while index < len(command):
        character = command[index]
        if quote is not None:
            current.append(character)
            if quote == '"' and character == "\\" and index + 1 < len(command):
                current.append(command[index + 1]); index += 2; continue
            if character == quote:
                quote = None
            index += 1; continue
        if character in "\"'":
            quote = character; current.append(character); index += 1; continue
        if command.startswith("$(", index):
            substitution_depth += 1; current.append("$("); index += 2; continue
        if substitution_depth:
            current.append(character)
            if character == "(": substitution_depth += 1
            elif character == ")": substitution_depth -= 1
            index += 1; continue
        if character == "#" and (index == 0 or command[index - 1].isspace() or command[index - 1] in ";|&"):
            while index < len(command) and command[index] not in "\r\n": index += 1
            continue
        if character == "&" and ((index > 0 and command[index - 1] == ">") or (index + 1 < len(command) and command[index + 1] == ">")):
            index += 1; continue
        separator = "&&" if command.startswith("&&", index) else "||" if command.startswith("||", index) else character
        if separator in {"&&", "||"} or character in ";|&\n":
            pieces.extend(("".join(current), separator)); current = []; index += len(separator); continue
        current.append(character); index += 1
    pieces.append("".join(current))
    return pieces


def is_command_prefix(tokens: list[str]) -> bool:
    assignment = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*=")
    if all(assignment.match(token) is not None for token in tokens):
        return True
    if tokens[:1] in (["command"], ["env"]):
        return all(token.startswith("-") or assignment.match(token) is not None for token in tokens[1:])
    return False


def executable_calls(command: str, executable: str) -> Iterator[tuple[list[str], int]]:
    """Yield quote-aware, command-position invocations of one executable."""
    for fragment in shell_pieces(command):
        if fragment in SEPARATORS:
            continue
        try:
            tokens = shlex.split(fragment, posix=True)
        except ValueError:
            continue
        for index, token in enumerate(tokens):
            if token == executable and is_command_prefix(tokens[:index]):
                yield tokens, index


def has_executable(command: str, executable: str) -> bool:
    return next(executable_calls(command, executable), None) is not None


def _assignment_value(match: re.Match[str]) -> str:
    return next(part for part in (match.group("double"), match.group("single"), match.group("bare")) if part is not None)


def plain_assignments(command: str) -> dict[str, str]:
    return {match.group("name"): value for match in PLAIN_ASSIGNMENT.finditer(command)
            if "$(" not in (value := _assignment_value(match)) and "`" not in value}


def substitution_assignments(command: str) -> frozenset[str]:
    return frozenset(match.group("name") for match in PLAIN_ASSIGNMENT.finditer(command)
                     if "$(" in _assignment_value(match) or "`" in _assignment_value(match))


def expand(value: str, assignments: dict[str, str], substitutions: frozenset[str]) -> tuple[str | None, str | None]:
    variable = VARIABLE.match(value)
    if variable is None:
        return value, None
    name = variable.group("braced") or variable.group("plain")
    rest = variable.group("rest") or ""
    if name in assignments:
        return assignments[name] + rest, None
    return None, "command-substitution" if name in substitutions else "external-variable"


def candidate_paths(source: str) -> tuple[str, ...]:
    match = MSYS_PATH.match(source)
    if match is None or sys.platform != "win32":
        return (source,)
    return source, f"{match.group('drive').upper()}:/{match.group('rest')}"


def is_absolute_path(source: str) -> bool:
    return Path(source).is_absolute() or MSYS_PATH.match(source) is not None


def read_candidate(source: str) -> str | None:
    for candidate in candidate_paths(source):
        try:
            return Path(candidate).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
    return None


def candidate_file(source: str) -> Path | None:
    for candidate in candidate_paths(source):
        path = Path(candidate)
        if path.is_file():
            return path.resolve()
    return None


def literal_command_folder(
    command: str, target: Callable[[str], bool]
) -> Path | None:
    """Return the last literal absolute ``cd`` before the target command."""
    pieces = shell_pieces(command)
    target_index = next((i for i, piece in enumerate(pieces)
                         if piece not in SEPARATORS and target(piece)), None)
    if target_index is None:
        return None
    compound = {"(", ")", "{", "}", "if", "then", "elif", "else", "fi",
                "for", "while", "until", "case", "esac", "do", "done", "function"}
    for piece in pieces[:target_index]:
        if piece in SEPARATORS:
            continue
        if any(delimiter in piece for delimiter in "(){}"):
            return None
        try:
            tokens = shlex.split(piece, posix=True)
        except ValueError:
            return None
        if compound.intersection(tokens):
            return None
    folder: Path | None = None
    previous = ""
    conditional_cd = False
    for index, piece in enumerate(pieces[:target_index]):
        if piece in SEPARATORS:
            previous = piece
            if conditional_cd and piece != "&&":
                folder = None; conditional_cd = False
            continue
        fragment = piece.strip()
        if not re.match(r"\Acd(?:\s|\Z)", fragment):
            try:
                tokens = shlex.split(fragment, posix=True)
            except ValueError:
                tokens = []
            if "cd" in tokens:
                folder = None; conditional_cd = previous in {"&&", "||"}
            continue
        next_separator = pieces[index + 1] if index + 1 < target_index and pieces[index + 1] in SEPARATORS else ""
        if previous == "|" or next_separator in {"|", "&"}:
            continue
        if previous == "||":
            folder = None; conditional_cd = True; continue
        match = LITERAL_CD.fullmatch(fragment)
        if match is None:
            folder = None; conditional_cd = previous in {"&&", "||"}; continue
        value = match.group("target")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        folder = Path(candidate_paths(value)[-1]) if is_absolute_path(value) else None
        conditional_cd = previous in {"&&", "||"}
    return folder
