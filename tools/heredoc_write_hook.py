"""Refuse literal Bash heredoc writes into a checkout's private roots."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import shlex
import sys

import command_reader
import repo_root
import shell_reader
from console_codec import require_python_floor, use_utf8


DECLARED_LIMITS = (
    ("Python bodies are a floor", "Only literal open calls and pathlib file writes are read; "
     "computed paths, aliases, and arbitrary Python execution are outside the read."),
    ("Unresolvable targets are unread", "Variables, substitutions, unknown command folders, "
     "and malformed shell or Python text do not establish where a write lands."),
    ("PowerShell here-strings are unread", "Only command_reader's modeled Bash tools are read."),
    ("Shell reading is a floor", "Single-line heredoc headers and literal file redirections "
     "are read; continued headers, generated shell commands, and runtime shell state are unread."),
)


def _private_target(source: str, cwd: Path | None) -> bool | None:
    if any(character in source for character in "$`~*?"):
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


def _headers(command: str):
    """Read headers separately so patient text never becomes shell tokens."""
    lines = command.splitlines()
    index = 0
    while index < len(lines):
        header_index = index
        header = lines[index]
        index += 1
        if "<<" not in header:
            continue
        lexer = shlex.shlex(header, posix=True, punctuation_chars="<>|;&()")
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            # A multiline quoted argument (including a commit-message
            # substitution) is data, not a heredoc header.
            try:
                words = shlex.split(command)
            except ValueError:
                words = []
            if not any("\n" in word and "<<" in word for word in words):
                yield header, None, [], "\n".join(lines[:header_index + 1])
            continue
        delimiters = [
            (tokens[position + 1], token == "<<-")
            for position, token in enumerate(tokens[:-1]) if token in {"<<", "<<-"}
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
            yield header, tokens, bodies, "\n".join(lines[:header_index + 1])


def _python_targets(body: str) -> tuple[list[str], bool]:
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
                path = literal(path_node)
                if path is None or mode is None:
                    unread = True
                if path is not None and mode is not None and any(flag in mode for flag in "wax+"):
                    targets.append(path)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                "write_text", "write_bytes", "open", "touch"
            }:
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
    unread = False
    for header, tokens, bodies, prefix in _headers(command):
        if tokens is None:
            unread = True
            continue
        folder = shell_reader.literal_command_folder(
            prefix, lambda piece: "<<" in piece
        )
        if folder is None and not shell_reader.has_executable(prefix, "cd"):
            folder = cwd
        targets = [tokens[index + 1] for index, token in enumerate(tokens[:-1])
                   if token in {">", ">>"}]
        for arguments, executable_index in command_reader.shell_reader.executable_calls(header, "tee"):
            for argument in arguments[executable_index + 1:]:
                if argument.startswith("-") or argument in {"<<", "<<-", "|"}:
                    continue
                targets.append(argument)
        if any(command_reader.shell_reader.has_executable(header, executable)
               for executable in ("python", "python3")):
            for body in bodies:
                python_targets, python_unread = _python_targets(body)
                targets.extend(python_targets)
                unread = unread or python_unread
        resolutions = [_private_target(target, folder) for target in targets]
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
    try:
        payload = json.load(sys.stdin)
        response = handle(payload) if isinstance(payload, dict) else {}
    except (ValueError, OSError, TypeError):
        response = {}
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
