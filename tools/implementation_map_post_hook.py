"""Add non-blocking context after acts that incur implementation-map work.

Command tokenization is owned by ``tracker_publish_hook.gh_command_tokens``;
this hook classifies only the ruled label and merge routes. It reads no tracker
record, never refuses the completed command, and emits no response for any
other command. The complete boundary is ``DECLARED_LIMITS``.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

from console_codec import use_utf8
import git_paths
import tracker_publish_hook


REPO_ROOT = Path(__file__).resolve().parent.parent
READY_LABEL = "ready-for-agent"
ROUTES = (("issue", "edit"), ("issue", "create"), ("pr", "merge"))

DECLARED_LIMITS = (
    "A ready flip made in the GitHub web UI bypasses this repository hook.",
    "A session that runs no repository hook, including Codex, receives no context.",
    "A merge made outside the session receives no context.",
    "A session may read the additional context and still decline to act on it.",
    "A PR selected by number or URL cannot be tied to the session branch without "
    "a tracker read, so only an omitted selector or the current branch name is classified.",
)


def _specific(context: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }


def _arguments(command: str, route: tuple[str, ...]) -> list[str] | None:
    parsed = tracker_publish_hook.gh_command_tokens(command, ROUTES)
    if parsed is None:
        return None
    tokens, index = parsed
    tail = tokens[index + 1 :]
    if tuple(tail[:2]) != route:
        return None
    return tail[2:]


def _flag_values(arguments: list[str], flags: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    for index, token in enumerate(arguments):
        if token in flags and index + 1 < len(arguments):
            values.extend(arguments[index + 1].split(","))
        for flag in flags:
            if token.startswith(flag + "="):
                values.extend(token[len(flag) + 1 :].split(","))
            if len(flag) == 2 and token.startswith(flag) and len(token) > 2:
                values.extend(token[len(flag) :].split(","))
    return tuple(value.strip() for value in values if value.strip())


def _repo_identity(
    value: str, *, default_host: str | None = None
) -> tuple[str | None, str] | None:
    cleaned = re.sub(r"\.git$", "", value.strip().rstrip("/"), flags=re.IGNORECASE)
    ssh = re.fullmatch(r"[^@]+@([^:]+):(.+)", cleaned)
    if ssh is not None:
        host, path = ssh.groups()
        parts = [part for part in path.split("/") if part]
    elif "://" in cleaned:
        match = re.fullmatch(r"[^:]+://([^/]+)/(.+)", cleaned)
        if match is None:
            return None
        host, path = match.groups()
        parts = [part for part in path.split("/") if part]
    else:
        parts = [part for part in cleaned.split("/") if part]
        host = parts.pop(0) if len(parts) >= 3 else default_host
    if len(parts) < 2:
        return None
    return host.lower() if host else None, "/".join(parts[-2:]).lower()


def _targets_this_repo(arguments: list[str]) -> bool:
    selected = _flag_values(arguments, ("--repo", "-R"))
    if not selected:
        return True
    current = _repo_identity(_git_line(("remote", "get-url", "origin")))
    if current is None:
        return False
    return all(
        _repo_identity(value, default_host=current[0]) == current for value in selected
    )


def _created_issue_number(response: object) -> int | None:
    text = json.dumps(response, ensure_ascii=False) if not isinstance(response, str) else response
    patterns = (
        r"/issues/(\d+)(?:\D|$)",
        r"(?:issue|Issue)\s+#?(\d+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _ready_flip(command: str, response: object) -> int | None:
    edit = _arguments(command, ("issue", "edit"))
    if (
        edit is not None
        and _targets_this_repo(edit)
        and READY_LABEL in _flag_values(edit, ("--add-label",))
    ):
        number = next((int(token) for token in edit if token.isdigit()), None)
        return number
    create = _arguments(command, ("issue", "create"))
    if (
        create is not None
        and _targets_this_repo(create)
        and READY_LABEL in _flag_values(create, ("--label", "-l"))
    ):
        return _created_issue_number(response)
    return None


def branch_adrs(
    repo_root: Path | None = None, *, base: str = "origin/main"
) -> tuple[str, ...]:
    repo_root = repo_root or REPO_ROOT
    try:
        records = git_paths.read_path_records(
            repo_root,
            "diff", "-z", "--name-only", "--diff-filter=AM",
            f"{base}...HEAD", "--", "docs/adr/",
        )
    except git_paths.GitPathError:
        return ()
    return tuple(
        sorted(
            Path(record).as_posix()
            for record in records
            if re.fullmatch(r"docs[\\/]adr[\\/]\d{4}[^\\/]*\.md", record)
        )
    )


def _git_line(arguments: tuple[str, ...]) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _default_branch_name() -> str:
    symbolic = _git_line(("symbolic-ref", "--short", "refs/remotes/origin/HEAD"))
    return symbolic.removeprefix("origin/") or "main"


def _pr_lands_session_branch(command: str) -> bool:
    arguments = _arguments(command, ("pr", "merge"))
    if arguments is None or not _targets_this_repo(arguments):
        return False
    value_flags = {
        "--body", "--body-file", "--match-head-commit", "--repo", "-R", "--subject",
    }
    selector = None
    skip_value = False
    for token in arguments:
        if skip_value:
            skip_value = False
            continue
        if token in value_flags:
            skip_value = True
            continue
        if token.startswith("-"):
            continue
        selector = token
        break
    current = _git_line(("branch", "--show-current"))
    if not current:
        return False
    # With no selector gh merges the current branch's PR. A branch-name
    # selector is also locally provable; numbers and URLs are not, so the
    # non-blocking hook stays silent rather than reading a PR record.
    if selector is not None and selector != current:
        return False
    configured_base = _git_line(
        ("config", "--get", f"branch.{current}.gh-merge-base")
    )
    return not configured_base or configured_base == _default_branch_name()


def _push_target(token: str) -> str:
    target = token.rsplit(":", 1)[-1]
    return target.removeprefix("refs/heads/")


def _push_source(token: str) -> str:
    source = token.rsplit(":", 1)[0] if ":" in token else token
    return source.removeprefix("+").removeprefix("refs/heads/")


def _lands_default_branch(command: str) -> bool:
    if _arguments(command, ("pr", "merge")) is not None:
        return _pr_lands_session_branch(command)
    for tokens, index in tracker_publish_hook.command_tokens(command, "git"):
        tail = tokens[index + 1 :]
        if not tail or tail[0] != "push":
            continue
        default = _default_branch_name()
        arguments = tail[1:]
        current = _git_line(("branch", "--show-current"))
        if "--delete" in arguments or "-d" in arguments:
            return False
        if any(
            _push_target(token) == default
            and _push_source(token) in ("HEAD", current)
            for token in arguments
        ):
            return True
        return current == default and arguments in (
            [], ["origin"], ["HEAD"], ["origin", "HEAD"]
        )
    return False


def _response_text(response: object) -> str:
    return response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)


def _pre_push_base(command: str, response: object) -> str:
    is_push = any(
        tokens[index + 1 : index + 2] == ["push"]
        for tokens, index in tracker_publish_hook.command_tokens(command, "git")
    )
    if not is_push:
        return "origin/main"
    match = re.search(
        r"\b([0-9a-f]{7,40})\.\.[0-9a-f]{7,40}\b",
        _response_text(response),
    )
    if match is not None:
        return match.group(1)
    previous = _git_line(("rev-parse", "--verify", "origin/main@{1}"))
    return previous or "origin/main"


def handle(payload: dict) -> dict:
    """Return additional context only; malformed and nonmatching inputs are silent."""
    try:
        command = payload["tool_input"]["command"]
        if not isinstance(command, str):
            return {}
        ticket = _ready_flip(command, payload.get("tool_response", ""))
        if ticket is not None:
            return _specific(
                f"Ticket #{ticket} was made {READY_LABEL}. If it is not already in "
                "a packet, place it now with `python tools/implementation_map.py "
                f"apply-delta --ticket {ticket} --outcome \"<one sentence>\"`."
            )
        if _lands_default_branch(command):
            adrs = branch_adrs(
                base=_pre_push_base(command, payload.get("tool_response", ""))
            )
            if adrs:
                names = ", ".join(f"ADR {Path(path).name[:4]}" for path in adrs)
                return _specific(
                    f"This merge lands {names}. Record each ADR's implementation-map "
                    "review now with apply-delta."
                )
    except (KeyError, TypeError, ValueError):
        return {}
    return {}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    json.dump(handle(payload), sys.stdout)
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
