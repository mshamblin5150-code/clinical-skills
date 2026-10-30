"""Refuse literal Bash heredoc writes into a checkout's private roots."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import shlex
import sys
from typing import NamedTuple

import command_reader
import repo_root
import shell_reader
from hook_payload import read_payload
from console_codec import require_python_floor, use_utf8


DECLARED_LIMITS = (
    ('Unreadable harness payload', 'Unreadable payloads refuse only on raw << together with scratch or output; otherwise allow with both notes. Escaped or split literals can evade the raw search.'),
    ("Python bodies are a floor", "Only literal open calls and pathlib file writes are read; "
     "computed paths, aliases, and arbitrary Python execution are outside the read."),
    ("Unresolvable targets are unread", "Variables, substitutions, unknown command folders, "
     "and malformed shell or Python text do not establish where a write lands."),
    ("PowerShell here-strings are unread", "Only command_reader's modeled Bash tools are read."),
    ("Shell reading is a floor", "Single-line heredoc headers and literal >, >>, &>, &>>, >& and tee "
     "file writes are read; continued headers, generated shell commands, and runtime shell state "
     "are unread."),
)
OUTPUT_REDIRECTIONS = frozenset({'>', '>>', '&>', '&>>', '>&'})
DESCRIPTOR_WORD = re.compile(r'\d+-?|-')


def _private_target(source: str, cwd: Path | None) -> bool | None:
    if source.startswith("~") or any(character in source for character in "$`*?"):
        return None
    target = Path(shell_reader.candidate_paths(source)[-1])
    if not target.is_absolute():
        if cwd is None:
            return None
        target = cwd / target
    target = target.resolve()
    checkout = repo_root.enclosing_checkout(target)
    return checkout is not None and any(
        target.is_relative_to(checkout / name) for name in ("scratch", "output")
    )


class _ShellToken(NamedTuple):
    value: str
    operator: bool
    start: int
    end: int


def _write_tokens(source: str) -> list[_ShellToken]:
    """Keep quoted/escaped operator text distinct from executable shell operators."""
    result = []
    start = None
    quote = None
    depth = 0
    index = 0

    def word(end):
        if start is not None:
            raw = source[start:end]
            cooked = shlex.split(raw, posix=True)
            result.append(_ShellToken(cooked[0] if len(cooked) == 1 else raw, False, start, end))

    while index < len(source):
        char = source[index]
        if quote is not None:
            if char == '\\' and quote != "'":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char == '\\':
            if start is None:
                start = index
            if index + 1 == len(source):
                raise ValueError('unfinished escape')
            index += 2
            continue
        if char in "\"'`":
            if start is None:
                start = index
            quote = char
            index += 1
            continue
        if source.startswith('$(', index):
            if start is None:
                start = index
            depth += 1
            index += 2
            continue
        if depth:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            index += 1
            continue
        if char == '#' and start is None:
            break
        if char.isspace():
            word(index)
            start = None
            index += 1
            continue
        if char in '<>|;&()':
            word(index)
            start = None
            end = index + 1
            while end < len(source) and source[end] in '<>|;&()':
                end += 1
            if source[index:end] == '<<' and source[end:end + 1] == '-':
                end += 1
            result.append(_ShellToken(source[index:end], True, index, end))
            index = end
            continue
        if start is None:
            start = index
        index += 1
    if quote is not None or depth:
        raise ValueError('unfinished shell word')
    word(index)
    return result


def _headers(command: str, *, include_plain: bool = False):
    """Read headers separately so patient text never becomes shell tokens."""
    lines = command.splitlines()
    index = 0
    while index < len(lines):
        header = lines[index]
        index += 1
        if "<<" not in header and not include_plain:
            continue
        tokens = None
        while True:
            try:
                tokens = _write_tokens(header)
                break
            except ValueError:
                if include_plain and index < len(lines):
                    header += '\n' + lines[index]
                    index += 1
                    continue
                break
        header_end = index
        if tokens is None:
            # A multiline quoted argument (including a commit-message
            # substitution) is data, not a heredoc header.
            try:
                words = shlex.split(command)
            except ValueError:
                words = []
            if not any("\n" in word and "<<" in word for word in words):
                yield header, None, [], "\n".join(lines[:header_end])
            continue
        delimiters = [
            (tokens[position + 1].value, token.value == "<<-")
            for position, token in enumerate(tokens[:-1])
            if token.operator and token.value in {"<<", "<<-"}
        ]
        bodies = []
        for delimiter, strip_tabs in delimiters:
            start = index
            while index < len(lines) and (
                lines[index].lstrip("\t") if strip_tabs else lines[index]
            ) != delimiter:
                index += 1
            bodies.append("\n".join(lines[start:index]))
            index += 1
        if delimiters:
            yield header, tokens, bodies, "\n".join(lines[:header_end])
        elif include_plain:
            yield header, tokens, [], "\n".join(lines[:header_end])


def _python_targets(body: str, *, reads_untouched: bool = False) -> tuple[list[str], bool]:
    """Read literal paths, including a simple assignment to a Path object."""
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return [], True
    paths: dict[str, str] = {}

    def literal(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return paths.get(node.id)
        if isinstance(node, ast.Call) and node.args and (
            isinstance(node.func, ast.Name) and node.func.id == "Path"
            or isinstance(node.func, ast.Attribute) and node.func.attr == "Path"
        ):
            return literal(node.args[0])
        return None

    targets = []
    unread = False
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            path = literal(statement.value)
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    paths.pop(target.id, None)
                    if path is not None:
                        paths[target.id] = path
        for node in ast.walk(statement):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                path_node = node.args[0] if node.args else next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "file"), None
                )
                mode_node = node.args[1] if len(node.args) > 1 else next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "mode"), None
                )
                mode = literal(mode_node) if mode_node is not None else "r"
                if reads_untouched and mode is not None and not any(flag in mode for flag in 'wax+'):
                    continue
                path = literal(path_node)
                if path is None or mode is None:
                    unread = True
                if path is not None and mode is not None and any(flag in mode for flag in "wax+"):
                    targets.append(path)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                "write_text", "write_bytes", "open", "touch"
            }:
                if reads_untouched and node.func.attr == 'open':
                    mode = literal(node.args[0]) if node.args else next(
                        (literal(keyword.value) for keyword in node.keywords if keyword.arg == 'mode'), 'r')
                    if mode is not None and not any(flag in mode for flag in 'wax+'):
                        continue
                path = literal(node.func.value)
                if path is None:
                    unread = True
                if path is not None:
                    if node.func.attr == "open":
                        mode = literal(node.args[0]) if node.args else next(
                            (literal(keyword.value) for keyword in node.keywords if keyword.arg == "mode"), "r"
                        )
                        if mode is None:
                            unread = True
                        if mode is None or not any(flag in mode for flag in "wax+"):
                            continue
                    targets.append(path)
    return targets, unread


def _unread(reason: str) -> dict:
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "Heredoc write guard: unread — " + reason +
        "; the reading boundary is heredoc_write_hook.DECLARED_LIMITS.",
    }}


def write_targets(command: str, cwd: Path | None, *, include_plain: bool = False
                  ) -> tuple[list[tuple[str, Path | None]], bool]:
    """Read literal file writes without expanding shell text or executing Python.

    The subagent fence includes ordinary redirections; the heredoc guard keeps
    its existing header-only population. Unresolved Python targets and parsing
    failures set the unread flag; callers own the resulting policy.
    """
    writes = []
    unread = False
    for header, tokens, bodies, prefix in _headers(command, include_plain=include_plain):
        if tokens is None:
            unread = True
            continue
        fragments = (shell_reader.shell_pieces(header, keep_redirect_ampersand=True)
                     if include_plain else [header])
        preceding = prefix[:-len(header)] if header else prefix
        for fragment in fragments:
            preceding += fragment
            if fragment in shell_reader.SEPARATORS:
                continue
            if include_plain:
                try:
                    fragment_tokens = _write_tokens(fragment)
                except ValueError:
                    unread = True
                    continue
                sentinel = '__subagent_write_target__'
                folder = shell_reader.literal_command_folder(
                    preceding + '\n' + sentinel, lambda piece: piece.strip() == sentinel)
                if folder is None and not shell_reader.has_executable(preceding, 'cd'):
                    folder = cwd
            else:
                fragment_tokens = tokens
                folder = shell_reader.literal_command_folder(prefix, lambda piece: '<<' in piece)
                if folder is None and not shell_reader.has_executable(prefix, 'cd'):
                    folder = cwd
            targets = [following.value
                       for token, following in zip(fragment_tokens, fragment_tokens[1:])
                       if token.operator and token.value in OUTPUT_REDIRECTIONS
                       and not (token.value == '>&' and DESCRIPTOR_WORD.fullmatch(following.value))]
            if fragment_tokens and fragment_tokens[-1].operator and fragment_tokens[-1].value in OUTPUT_REDIRECTIONS:
                unread = True
            for piece in shell_reader.shell_pieces(fragment):
                arguments = _write_tokens(piece)
                executable_index = next((index for index, token in enumerate(arguments)
                    if not token.operator and token.value == 'tee'
                    and shell_reader.is_command_prefix([item.value for item in arguments[:index]])), None)
                if executable_index is None:
                    continue
                index = executable_index + 1
                while index < len(arguments):
                    token = arguments[index]
                    following = arguments[index + 1] if index + 1 < len(arguments) else None
                    if token.operator:
                        if '<' in token.value or '>' in token.value:
                            index += 2
                            continue
                        break
                    if token.value.isdecimal() and following is not None and following.operator and (
                        '<' in following.value or '>' in following.value) and token.end == following.start:
                        index += 1
                        continue
                    if not token.value.startswith('-'):
                        targets.append(token.value)
                    index += 1
            if any(shell_reader.has_executable(fragment, executable) for executable in ('python', 'python3')):
                for body in bodies:
                    python_targets, python_unread = _python_targets(body, reads_untouched=include_plain)
                    targets.extend(python_targets)
                    unread = unread or python_unread
            writes.extend((target, folder) for target in targets)
    return writes, unread


def handle(payload: dict) -> dict:
    """Return a Claude PreToolUse response without echoing command or note text."""
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return {}
    if command_reader.COMMAND_TOOLS.get(tool) != command_reader.MODELED_SHELL:
        return _unread("PowerShell here-string") if "@'" in command or '@"' in command else {}
    cwd = Path(payload.get("cwd") or Path.cwd())
    writes, unread = write_targets(command, cwd)
    resolutions = [_private_target(target, folder) for target, folder in writes]
    unread = unread or None in resolutions
    if True in resolutions:
        return {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Heredoc write refused: use the Write tool and "
                "the standing rule 6 staging, copy, rename, and destination-readback route.",
        }}
    return _unread("unresolvable file target") if unread else {}


def main() -> int:
    payload, response = read_payload('heredoc_write_hook', lambda raw: "<<" in raw and ("scratch" in raw or "output" in raw))
    if payload is not None:
        response = handle(payload)
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
