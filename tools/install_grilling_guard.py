#!/usr/bin/env python3
"""Install the tracked one-question format and Codex Stop hook. #1392."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile

from console_codec import require_python_floor, use_utf8
import grilling_stop_hook
from repo_root import main_repo_root


SOURCE_ROOT = Path(__file__).resolve().parent.parent
BLOCK_START = grilling_stop_hook.BLOCK_START
BLOCK_END = grilling_stop_hook.BLOCK_END
HOOK_FILENAME = "grilling_stop_hook.py"
INSTALL_FILES = (
    Path("docs/agents/grilling.md"),
    Path("tools/grilling_stop_hook.py"),
)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    temporary.replace(path)


def _read_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def _install_block(existing: str, format_text: str) -> str:
    block = grilling_stop_hook.marked_block(format_text).rstrip("\n")
    pattern = re.compile(
        re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END), re.DOTALL
    )
    starts = existing.count(BLOCK_START)
    ends = existing.count(BLOCK_END)
    if starts != ends or starts > 1:
        raise ValueError("the Codex AGENTS file has malformed grilling block markers")
    if starts == 1:
        match = pattern.search(existing)
        if match is None:
            raise ValueError("the Codex AGENTS file has unreadable grilling block markers")
        return existing[: match.start()] + block + existing[match.end() :]
    if not existing:
        return block + "\n"
    newline = "\r\n" if "\r\n" in existing else "\n"
    if existing.endswith(newline * 2):
        separator = ""
    elif existing.endswith(newline):
        separator = newline
    else:
        separator = newline * 2
    return existing + separator + block + "\n"


def _hook_command(script: Path) -> str:
    return f'"{Path(sys.executable).resolve()}" "{script.resolve()}"'


def _install_hook(document: object, script: Path) -> dict[str, object]:
    if not isinstance(document, dict):
        raise ValueError("~/.codex/hooks.json must contain a JSON object")
    hooks = document.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("~/.codex/hooks.json has no hooks object")
    stop = hooks.setdefault("Stop", [])
    if not isinstance(stop, list):
        raise ValueError("~/.codex/hooks.json has no Stop list")

    retained = []
    for registration in stop:
        if not isinstance(registration, dict):
            retained.append(registration)
            continue
        handlers = registration.get("hooks")
        if not isinstance(handlers, list):
            retained.append(registration)
            continue
        remaining = [
            handler
            for handler in handlers
            if not (
                isinstance(handler, dict)
                and HOOK_FILENAME in str(handler.get("command", ""))
            )
        ]
        if remaining:
            retained.append({**registration, "hooks": remaining})
    retained.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_command(script),
                    "timeout": 5,
                    "statusMessage": "Checking one-question grilling format",
                }
            ]
        }
    )
    hooks["Stop"] = retained
    return document


def _memory_pointer(tracked_format: Path) -> str:
    return (
        "---\n"
        "name: grill-one-question-at-a-time\n"
        'description: "Use the tracked one-question grilling format."\n'
        "metadata:\n"
        "  node_type: memory\n"
        "  type: feedback\n"
        "---\n\n"
        "The binding format is the tracked file at "
        f"`{tracked_format}`. Read it before asking a grilling question; this memory "
        "keeps no second copy of the rules.\n"
    )


def _require_matching_owning_checkout(
    source_root: Path, owning_checkout: Path
) -> None:
    mismatches = []
    for relative in INSTALL_FILES:
        source = source_root / relative
        installed = owning_checkout / relative
        try:
            matches = source.read_bytes() == installed.read_bytes()
        except OSError:
            matches = False
        if not matches:
            mismatches.append(relative.as_posix())
    if mismatches:
        raise ValueError(
            "the owning checkout does not contain this installer's tracked bytes: "
            + ", ".join(mismatches)
            + "; update the owning checkout before installing"
        )


def install(*, home: Path, source_root: Path, owning_checkout: Path) -> None:
    _require_matching_owning_checkout(source_root, owning_checkout)
    format_source = owning_checkout / "docs" / "agents" / "grilling.md"
    format_text = _read_exact(format_source)

    agents_path = home / ".codex" / "AGENTS.md"
    existing_agents = (
        _read_exact(agents_path) if agents_path.exists() else ""
    )
    _write_atomic(agents_path, _install_block(existing_agents, format_text))

    hooks_path = home / ".codex" / "hooks.json"
    hooks_document: object = {"hooks": {}}
    if hooks_path.exists():
        hooks_document = json.loads(hooks_path.read_text(encoding="utf-8"))
    installed_hooks = _install_hook(
        hooks_document, owning_checkout / "tools" / HOOK_FILENAME
    )
    _write_atomic(
        hooks_path,
        json.dumps(installed_hooks, ensure_ascii=False, indent=2) + "\n",
    )

    tracked_format = owning_checkout / "docs" / "agents" / "grilling.md"
    memory_root = home / ".claude" / "projects"
    if memory_root.exists():
        for memory in memory_root.glob(
            "*/memory/grill-one-question-at-a-time.md"
        ):
            _write_atomic(memory, _memory_pointer(tracked_format))


def main() -> int:
    install(
        home=Path.home(),
        source_root=SOURCE_ROOT,
        owning_checkout=main_repo_root(SOURCE_ROOT / "tools"),
    )
    print("Installed the one-question grilling format and Codex Stop hook.")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
