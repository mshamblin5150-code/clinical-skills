#!/usr/bin/env python3
"""Install the approved-run Stop hook in Codex user configuration. #1398."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from console_codec import require_python_floor, use_utf8
from install_grilling_guard import register_in_place
from repo_root import main_repo_root


SOURCE_ROOT = Path(__file__).resolve().parent.parent
HOOK_FILENAME = "run_status_stop_hook.py"
HOOK_RELATIVE = Path("tools") / HOOK_FILENAME


def _read_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    temporary.replace(path)


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
    hooks["Stop"] = register_in_place(
        stop,
        HOOK_FILENAME,
        {
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_command(script),
                    "timeout": 30,
                    "statusMessage": "Checking approved run status",
                }
            ]
        },
    )
    return document


def install(*, home: Path, source_root: Path, owning_checkout: Path) -> None:
    source = source_root / HOOK_RELATIVE
    installed = owning_checkout / HOOK_RELATIVE
    try:
        matches = _read_exact(source).replace("\r\n", "\n") == _read_exact(
            installed
        ).replace("\r\n", "\n")
    except (OSError, UnicodeError):
        matches = False
    if not matches:
        raise ValueError(
            "the owning checkout does not contain this installer's tracked content; "
            "update the owning checkout before installing"
        )
    hooks_path = home / ".codex" / "hooks.json"
    document: object = {"hooks": {}}
    if hooks_path.exists():
        document = json.loads(hooks_path.read_text(encoding="utf-8"))
    _write_atomic(
        hooks_path,
        json.dumps(_install_hook(document, installed), ensure_ascii=False, indent=2)
        + "\n",
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    install(
        home=Path.home(),
        source_root=SOURCE_ROOT,
        owning_checkout=main_repo_root(SOURCE_ROOT / "tools"),
    )
    print("Installed the approved-run Codex Stop hook.")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
