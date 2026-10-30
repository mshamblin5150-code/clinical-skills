"""Fence Claude subagent writes to the staging folder in their brief. ADR 0439."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from console_codec import require_python_floor, use_utf8
from hook_payload import read_payload
import command_reader
import heredoc_write_hook
import repo_root
import shell_reader
import subagent_staging_hook


DECLARED_LIMITS = (
    "The harness measurement is historical: Claude Code 2.1.306 on 2026-10-23 supplied "
    "agent_id on Write, Edit and Bash calls, with the parent transcript_path and a "
    "first-row user brief at <parent stem>/subagents/agent-<agent_id>.jsonl.",
    "Live remeasurement on 2026-10-30, Claude Code 2.1.312, in a throwaway session with an "
    "explicit --settings file registering this hook and a field-name probe: the same fields "
    "and brief position held on Write, Edit and Bash, a write outside the staging folder "
    "was refused and created no file through Write and through a literal redirection, a "
    "write inside it and a null-device redirection were allowed, and a variable-built "
    "target was refused. The Agent launch and the main session's write carried no agent_id, "
    "and that write passed. A later harness version is not established by this measurement.",
    "A first row that is not a user text brief reads as unreadable. A census on 2026-10-30 of "
    "one machine's flat subagent transcripts found that shape rare and not absent; nested "
    "transcripts sit below the path this reads, so they read as unreadable too.",
    "Codex subagents and Workflow subagents were not measured. A call without agent_id "
    "passes untouched; an unreadable brief follows the selective refusal policy.",
    "Programs that write files themselves, including scripts, cp and mv, are outside "
    "the command-text reading except for the heredoc reader's modeled Python writes.",
    "Literal brief and shell path recognition is a floor; computed or unrecognized "
    "brief paths may evade the fence. Future transcript layouts follow the unreadable-brief policy. "
    "The bare scratch/sessions/ namespace and a template token (one carrying <, >, {, }, $, %, * "
    "or ?) name no folder and bind nothing, so a brief naming only those is unfenced. A concrete "
    "token binds even when it is only a mention and even when no such folder exists.",
    "Only Write, Edit, NotebookEdit and command_reader's modeled Bash tools are read. "
    "Other shells are outside the command-text reading. Unreadable payloads refuse only "
    "when raw text names agent_id and a scratch, output or temporary location; escaped "
    "or split raw triggers may evade that check, and failed stream reads warn.",
    "Shell file-write recognition covers >, >>, &>, &>> and >& targets, tee arguments and "
    "the heredoc reader's literal Python writes. A descriptor duplication and the null and "
    "standard-stream devices are not file writes. Other redirection forms and runtime shell "
    "or program behavior remain outside that reading.",
    "No refusal tally is kept; a subagent that omits a refusal from its result leaves "
    "no cross-run trace.",
)
FILE_TOOLS = {'Write': 'file_path', 'Edit': 'file_path', 'NotebookEdit': 'notebook_path'}
NULL_DEVICES = frozenset({'/dev/null', '/dev/stdout', '/dev/stderr', '/dev/tty'})
TEMPLATE_CHARACTERS = frozenset('<>{}$%*?')
NAMESPACE_CHILD = re.compile(r'(?<![\w.-])scratch/sessions/[^/]', re.I)


class UnreadableBrief(ValueError):
    """A fixed, content-free reason the brief cannot be read."""


def _brief(payload: dict) -> str:
    agent = payload.get('agent_id')
    transcript = payload.get('transcript_path')
    if not isinstance(agent, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', agent):
        raise UnreadableBrief('subagent identity is unreadable')
    if not isinstance(transcript, str) or not Path(transcript).is_absolute():
        raise UnreadableBrief('parent transcript location is unreadable')
    parent = Path(transcript)
    path = parent.with_suffix('') / 'subagents' / f'agent-{agent}.jsonl'
    try:
        with path.open(encoding='utf-8') as stream:
            row = json.loads(stream.readline())
    except (OSError, UnicodeError):
        raise UnreadableBrief('subagent transcript cannot be read') from None
    except (ValueError, RecursionError):
        raise UnreadableBrief('first transcript row is damaged') from None
    if not isinstance(row, dict) or row.get('type') != 'user':
        raise UnreadableBrief('first transcript row is not a user brief')
    message = row.get('message')
    text = message.get('content') if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise UnreadableBrief('first transcript row is not text')
    return text


def _deny(reason: str) -> dict:
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
        'permissionDecisionReason': 'Subagent write refused: ' + reason
        + '. Report this refusal in your result.',
    }}


def _named_folders(brief: str, cwd: str | None) -> list[Path]:
    """Resolve the brief's staging folders; the bare namespace or a template names none."""
    return subagent_staging_hook.resolve_staging(
        [token for token in subagent_staging_hook.staging_tokens(brief)
         if NAMESPACE_CHILD.search(token) and not TEMPLATE_CHARACTERS.intersection(token)], cwd)


def _device(target: object) -> bool:
    return target in NULL_DEVICES or (
        sys.platform == 'win32' and isinstance(target, str) and target.lower() == 'nul')


def _target(value: str, cwd: str | None) -> Path | None:
    try:
        path = Path(shell_reader.candidate_paths(value)[-1])
        if not path.is_absolute():
            if not isinstance(cwd, str) or not Path(cwd).is_absolute():
                return None
            path = Path(cwd) / path
        return path.resolve()
    except (OSError, ValueError, RuntimeError):
        return None


def _unreadable(reason: str, target: str | None, cwd: str | None) -> dict:
    sensitive = False
    if target:
        path = _target(target, cwd)
        checkout = repo_root.enclosing_checkout(path) if path is not None else None
        sensitive = subagent_staging_hook.names_temp(target) or (
            checkout is not None and any(path.is_relative_to(checkout / name)
                                         for name in ('scratch', 'output')))
    note = 'Subagent write guard: ' + reason + '; brief was not checked.'
    specific = {'hookEventName': 'PreToolUse', 'additionalContext': note}
    if sensitive:
        specific.update(_deny(reason)['hookSpecificOutput'])
    return {'hookSpecificOutput': specific, 'systemMessage': note}


def handle(payload: dict) -> dict:
    tool = payload.get('tool_name')
    if not isinstance(tool, str) or not payload.get('agent_id') or (
        tool not in FILE_TOOLS and command_reader.COMMAND_TOOLS.get(tool) != command_reader.MODELED_SHELL
    ):
        return {}
    inputs = payload.get('tool_input')
    cwd = payload.get('cwd')
    writes = []
    unread = False
    if tool in FILE_TOOLS:
        target = inputs.get(FILE_TOOLS[tool]) if isinstance(inputs, dict) else None
        writes = [(target, cwd)]
    else:
        command = inputs.get('command') if isinstance(inputs, dict) else None
        if not isinstance(command, str):
            return {}
        folder = Path(cwd) if isinstance(cwd, str) and Path(cwd).is_absolute() else None
        targets, unread = heredoc_write_hook.write_targets(command, folder, include_plain=True)
        writes = [(target, str(base) if base is not None else None)
                  for target, base in targets if not _device(target)]
        if not writes and not unread:
            return {}
    writes = [(target if isinstance(target, str) else None, base) for target, base in writes]
    try:
        brief = _brief(payload)
    except UnreadableBrief as failure:
        responses = [_unreadable(str(failure), target, base) for target, base in writes]
        return next((response for response in responses if
                     response['hookSpecificOutput'].get('permissionDecision') == 'deny'),
                    _unreadable(str(failure), None, cwd))
    try:
        paths = _named_folders(brief, payload.get('cwd'))
    except (OSError, ValueError, RuntimeError):
        responses = [_unreadable('brief staging folder cannot be resolved', target, base)
                     for target, base in writes]
        return next((response for response in responses if
                     response['hookSpecificOutput'].get('permissionDecision') == 'deny'),
                    _unreadable('brief staging folder cannot be resolved', None, cwd))
    if not paths:
        return {}
    if unread:
        return _deny('shell write target cannot be resolved; spell the staging folder literally')
    for target, base in writes:
        if not target or (tool not in FILE_TOOLS and
                          (target.startswith('~') or any(char in target for char in '$`*?'))):
            return _deny('write target cannot be resolved; spell the staging folder literally')
        path = _target(target, base)
        if path is None:
            return _deny('relative write target requires absolute cwd; spell the staging folder literally')
        if not any(path.is_relative_to(stage) for stage in paths):
            return _deny('write outside the brief staging folder; use that folder')
    return {}


def main() -> int:
    payload, response = read_payload('subagent_write_hook', lambda raw:
        re.search(r'\bagent_id\b', raw) is not None and (
            re.search(r'\b(?:scratch|output)/', subagent_staging_hook.normalized(raw)) is not None
            or subagent_staging_hook.names_temp(raw)),
        validate=lambda value: isinstance(value.get('tool_name'), str)
        and isinstance(value.get('tool_input'), dict))
    if payload is not None:
        response = handle(payload)
    specific = response.get('hookSpecificOutput', {})
    if payload is None and specific.get('permissionDecision') == 'deny':
        remedy = ' Report this refusal in your result.'
        specific['permissionDecisionReason'] += remedy
        specific['additionalContext'] += remedy
        response['systemMessage'] += remedy
    print(json.dumps(response))
    return 0


if __name__ == '__main__':
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
