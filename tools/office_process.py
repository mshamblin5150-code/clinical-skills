"""Run one bounded Office automation process and stop only its owned PID."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable


class OwnedProcessError(Exception):
    pass


def _ownership(ownership_file: Path) -> tuple[str, str] | None:
    try:
        pid, stage = ownership_file.read_text(encoding="ascii").strip().split("|", 1)
    except (OSError, ValueError):
        return None
    if not pid.isdigit():
        return None
    return pid, stage or "after process creation"


def _stop_owned_process(
    ownership_file: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess],
) -> None:
    ownership = _ownership(ownership_file)
    if ownership is None:
        return
    pid, _stage = ownership
    runner(
        ["taskkill.exe", "/PID", pid, "/T", "/F"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_owned_process(
    command: list[str],
    ownership_file: Path,
    *,
    timeout_seconds: int,
    application: str,
    action: str,
    runner: Callable[..., subprocess.CompletedProcess],
    encoding: str = "utf-8",
) -> subprocess.CompletedProcess:
    """Run a parameterized bound and kill only the PID the child recorded."""
    try:
        completed = runner(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding=encoding,
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as failure:
        ownership = _ownership(ownership_file)
        stage = (
            ownership[1]
            if ownership is not None
            else "before process ownership was recorded"
        )
        _stop_owned_process(ownership_file, runner=runner)
        raise OwnedProcessError(
            f"{application} {action} timed out at stage {stage}"
        ) from failure
    if completed.returncode != 0:
        _stop_owned_process(ownership_file, runner=runner)
        raise OwnedProcessError(
            completed.stderr.strip() or f"{application} {action} failed"
        )
    return completed
