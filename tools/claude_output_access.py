#!/usr/bin/env python3
"""Read Claude Code's user settings for the owning output grant. #1500.

This checks the saved entry, not whether a browser honors it. It never writes
settings or grants access, and it does not inspect Codex permissions.
"""

from __future__ import annotations

import json
from pathlib import Path

from console_codec import require_python_floor, use_utf8
import repo_root


def main() -> int:
    """Exit 0 for the grant, 1 for a missing entry, 2 for unreadable settings."""
    settings = Path.home() / ".claude" / "settings.json"
    try:
        output = repo_root.output_root().resolve()
        payload = json.loads(settings.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("settings must be a JSON object")
        permissions = payload.get("permissions", {})
        if not isinstance(permissions, dict):
            raise ValueError("permissions must be a JSON object")
        directories = permissions.get("additionalDirectories", [])
        if not isinstance(directories, list) or any(
            not isinstance(item, str) for item in directories
        ):
            raise ValueError("additionalDirectories must be an array of paths")
        granted = any(Path(item).expanduser().resolve() == output for item in directories)
    except (OSError, ValueError, RuntimeError) as failure:
        print(f"Claude output access check failed: {settings}: {failure}")
        return 2
    if granted:
        print(f"Claude output access entry present: {output}")
        return 0
    print(f"Add this entry by hand to {settings}, preserving existing settings:")
    print(json.dumps({"permissions": {"additionalDirectories": [str(output)]}}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
