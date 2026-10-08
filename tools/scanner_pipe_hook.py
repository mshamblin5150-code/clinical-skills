#!/usr/bin/env python3
"""Refuse a scanner status read through a Bash pipe. ADR 0299, #1457."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shlex
import sys

import command_reader
from console_codec import require_python_floor, use_utf8


DECLARED_LIMITS = (
    ('PowerShell is not read or refused',
     'ADR 0299 measured PowerShell 7.6.6 on 2026-10-08: cmdlet filters '
     'preserved $LASTEXITCODE and conditional status; findstr lost them. '
     'A recorded PowerShell instance reopens this boundary.'),
    ('Recognized invocations',
     'Literal python or python3, optionally command/env and plain assignments, '
     'followed directly by tools/name.py or ./tools/name.py, including quoted '
     'spellings. The file must exist beneath the hook payload cwd. Interpreter '
     'flags, py, absolute paths, aliases, variables, eval and generated commands '
     'are outside this population.'),
    ('Static Bash reading',
     'Uses command_reader.shell_reader separators and source words; recognizes '
     'do/then/else/if/while/until/! command prefixes. Malformed quoting, '
     'subshells, functions, substitutions, nested shells, background pipelines '
     'and dynamic cd targets are not parsed. Literal cd does not change the '
     'checkout used for file existence. Heredoc bodies are excluded by the reader.'),
    ('Status expansion reading',
     'Reads unescaped $? and literal ${PIPESTATUS[N]} outside single quotes. '
     'Computed indexes, array-wide expansions and indirect status reads are '
     'outside this reading. A later status expansion in the same straight-line '
     'command list is treated as a read; runtime branch reachability is not modeled.'),
)

RULE = (
    'Never report or branch on a tools/*.py scanner status through a Bash pipe. '
    'Use python tools/<name>.py > <file> 2>&1; echo "exit=$?", then grep the file. '
    'A pipe is allowed only when the very next command reads ${PIPESTATUS[N]} '
    'with N the scanner stage; an intervening command, wrong index, command-ending '
    'pipe, or set -o pipefail does not satisfy this rule.'
)


def _expansions(fragment: str) -> tuple[str, ...]:
    """Keep expansions that Bash actually evaluates, excluding quoted literals."""
    found = []
    quote = None
    index = 0
    while index < len(fragment):
        char = fragment[index]
        if quote == "'":
            if char == "'":
                quote = None
            index += 1
            continue
        if char == '\\':
            index += 2
            continue
        if char == '"':
            quote = None if quote == '"' else '"'
        elif char == "'" and quote is None:
            quote = "'"
        elif char == '$':
            match = re.match(r'\$\?|\$\{PIPESTATUS\[[0-9]+\]\}', fragment[index:])
            if match:
                found.append(match.group())
                index += len(match.group())
                continue
        index += 1
    return tuple(found)


def _scanner(fragment: str, cwd: Path) -> str | None:
    try:
        tokens = shlex.split(fragment)
    except ValueError:
        return None
    while tokens and tokens[0] in {'do', 'then', 'else', 'if', 'while', 'until', '!'}:
        tokens.pop(0)
    for executable in ('python', 'python3'):
        for arguments, index in command_reader.shell_reader.executable_calls(
            shlex.join(tokens), executable
        ):
            if index + 1 >= len(arguments):
                continue
            path = arguments[index + 1]
            if re.fullmatch(r'(?:\./)?tools/[^/]+\.py', path) and (cwd / path).is_file():
                return path
    return None


def handle(payload: dict) -> dict:
    """Return the PreToolUse decision without executing the supplied command."""
    if command_reader.COMMAND_TOOLS.get(payload.get('tool_name')) != command_reader.MODELED_SHELL:
        return {}
    tool_input = payload.get('tool_input', {})
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return {}
    cwd = Path(payload.get('cwd') or Path.cwd())
    pieces = command_reader.shell_reader.shell_pieces(command)
    index = 0
    while index < len(pieces):
        end = index
        stages = [pieces[index]]
        while end + 2 < len(pieces) and pieces[end + 1] == '|':
            end += 2
            stages.append(pieces[end])
        separator = pieces[end + 1] if end + 1 < len(pieces) else ''
        following = pieces[end + 2] if end + 2 < len(pieces) else ''
        for stage, fragment in enumerate(stages[:-1]):
            script = _scanner(fragment, cwd)
            if script is None:
                continue
            expansions = _expansions(following)
            own = '${PIPESTATUS[' + str(stage) + ']}'
            immediate = separator in {';', '\n'} and own in expansions and '$?' not in expansions
            if immediate:
                continue
            conditional = bool(re.match(r'\s*(?:if|while|until)\b', stages[0]))
            later = any(_expansions(piece) for piece in pieces[end + 2:])
            terminal = not separator or (separator in {';', '\n'} and
                       (not following.strip() or following.strip() in {'done', 'fi', '}', ')'}))
            if conditional or separator in {'&&', '||'} or terminal or later:
                return {'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason':
                        f'Scanner pipe refused: python {script} > <file> 2>&1; '
                        'echo "exit=$?", then grep the file. Alternatively read '
                        f'{own} in the very next command. See scanner_pipe_hook.DECLARED_LIMITS.',
                }}
        index = end + 2
    return {}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        response = handle(payload) if isinstance(payload, dict) else {}
    except (ValueError, OSError, TypeError):
        response = {}
    print(json.dumps(response))
    return 0


if __name__ == '__main__':
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
