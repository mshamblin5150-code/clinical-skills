"""Nonblocking process locks for shared, out-of-repo build artifacts."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterator


class ArtifactBusy(RuntimeError):
    """Another task currently owns a shared artifact."""


def lock_path(artifact: Path | str) -> Path:
    """Return the persistent sibling whose first byte carries the OS lock."""
    return Path(str(Path(artifact).resolve()) + ".lock")


def _try_lock(stream: BinaryIO) -> None:
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(stream: BinaryIO) -> None:
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _owner(stream: BinaryIO) -> str:
    try:
        stream.seek(1)
        raw = stream.read().decode("utf-8").strip()
        data = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""
    if not isinstance(data, dict):
        return ""
    details = []
    if data.get("action"):
        details.append(str(data["action"]))
    if data.get("pid"):
        details.append(f"process {data['pid']}")
    if data.get("started_at"):
        details.append(f"started {data['started_at']}")
    return ", ".join(details)


@contextmanager
def hold(artifact: Path | str, action: str) -> Iterator[Path]:
    """Own ``artifact`` until the context exits, or fail without waiting."""
    artifact = Path(artifact).resolve()
    path = lock_path(artifact)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        try:
            _try_lock(stream)
        except (BlockingIOError, PermissionError) as failure:
            owner = _owner(stream)
            detail = f" ({owner})" if owner else ""
            raise ArtifactBusy(
                f"another task is rebuilding {artifact}{detail}; "
                "retry after that task finishes"
            ) from failure

        record = {
            "action": action,
            "pid": os.getpid(),
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        try:
            stream.seek(1)
            stream.truncate()
            stream.write(json.dumps(record, sort_keys=True).encode("utf-8"))
            stream.flush()
            yield path
        finally:
            stream.seek(1)
            stream.truncate()
            stream.flush()
            _unlock(stream)
