"""Select full validation unless a PR edit is confirmed to change only text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8


def requires_code(event_name: str, event: object) -> bool:
    """Unknown events/shapes retain full validation; this grants no passing check."""
    if event_name != "pull_request" or not isinstance(event, dict):
        return True
    if event.get("action") != "edited":
        return True
    changes = event.get("changes")
    if not isinstance(changes, dict) or not changes or not set(changes) <= {"title", "body"}:
        return True
    for field, change in changes.items():
        if not isinstance(change, dict) or set(change) != {"from"}:
            return True
        if not isinstance(change["from"], str) and not (field == "body" and change["from"] is None):
            return True
    pr = event.get("pull_request")
    if not isinstance(pr, dict) or not isinstance(pr.get("title"), str):
        return True
    if "body" not in pr or not (pr["body"] is None or isinstance(pr["body"], str)):
        return True
    for section in ("head", "base"):
        identity = pr.get(section)
        if not isinstance(identity, dict) or not isinstance(identity.get("ref"), str) or not identity["ref"]:
            return True
        sha = identity.get("sha")
        if not isinstance(sha, str) or re.fullmatch(r"[0-9a-fA-F]{40}", sha) is None:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--github-event", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        event = json.loads(args.github_event.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print("CI event unreadable; full code validation selected", file=sys.stderr)
        event = None
    print("true" if requires_code(args.event_name, event) else "false")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
