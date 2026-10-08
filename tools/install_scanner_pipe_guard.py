#!/usr/bin/env python3
"""Install the Codex PreToolUse scanner pipe guard. ADR 0299, #1457.

The live probe and selected mechanical-hook branch are recorded in
docs/agents/scanner-pipe-codex-probe.md. Hook trust remains Codex-managed.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from console_codec import require_python_floor, use_utf8
from install_grilling_guard import _read_exact, _write_atomic
from repo_root import main_repo_root

SOURCE_ROOT = Path(__file__).resolve().parent.parent
HOOK_FILENAME = 'scanner_pipe_hook.py'
INSTALL_FILES = (
    'tools/scanner_pipe_hook.py', 'tools/command_reader.py',
    'tools/shell_reader.py', 'tools/install_scanner_pipe_guard.py',
)


def install(*, home: Path, source_root: Path, owning_checkout: Path) -> None:
    """Refresh only our registration, pointing at the owning checkout."""
    for relative in INSTALL_FILES:
        source = _read_exact(source_root / relative).replace('\r\n', '\n')
        installed = _read_exact(owning_checkout / relative).replace('\r\n', '\n')
        if source != installed:
            raise ValueError('update the owning checkout before installing: ' + relative)
    path = home / '.codex' / 'hooks.json'
    document = json.loads(_read_exact(path)) if path.exists() else {'hooks': {}}
    if not isinstance(document, dict):
        raise ValueError('Codex hooks.json must contain an object')
    hooks = document.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Codex hooks.json must contain a hooks object')
    registrations = hooks.setdefault('PreToolUse', [])
    if not isinstance(registrations, list):
        raise ValueError('Codex PreToolUse must be a list')
    retained = []
    for registration in registrations:
        if not isinstance(registration, dict) or not isinstance(registration.get('hooks'), list):
            retained.append(registration)
            continue
        remaining = [handler for handler in registration['hooks']
                     if not (isinstance(handler, dict) and
                             HOOK_FILENAME in str(handler.get('command', '')))]
        if remaining:
            retained.append({**registration, 'hooks': remaining})
    script = (owning_checkout / 'tools' / HOOK_FILENAME).resolve()
    retained.append({'matcher': 'Bash|Monitor', 'hooks': [{
        'type': 'command',
        'command': f'"{Path(sys.executable).resolve()}" "{script}"',
        'timeout': 5,
        'statusMessage': 'Checking scanner pipeline status',
    }]})
    hooks['PreToolUse'] = retained
    _write_atomic(path, json.dumps(document, ensure_ascii=False, indent=2) + '\n')


def main() -> int:
    try:
        install(home=Path.home(), source_root=SOURCE_ROOT,
                owning_checkout=main_repo_root(SOURCE_ROOT / 'tools'))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print('Codex received the mechanical PreToolUse guard; trust it through /hooks.')
    return 0


if __name__ == '__main__':
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
