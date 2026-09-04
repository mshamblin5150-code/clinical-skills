"""Nonblocking process locks for shared, out-of-repo build artifacts.

The lock root may be overridden for a bounded run, but it always remains outside
every checkout. Scoped identities bound ordinary acquisition work to one artifact;
what the mechanism does not guard is declared in ``NOT_GUARDED``.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterator

from repo_root import ensure_outside_checkout


LOCK_ROOT_ENVIRONMENT_VARIABLE = "CLINICAL_SKILLS_LOCK_ROOT"

NOT_GUARDED = (
    (
        "lock identity directories are permanent debris",
        "The directory and its lock record remain after release because deleting a "
        "lock another process may be opening can split ownership across two inodes.",
    ),
    (
        "different lock roots do not coordinate",
        "Two processes configured with different overrides cannot observe one another; "
        "the value is kept outside checkouts, but disagreement is undetectable at run time.",
    ),
)


class ArtifactBusy(ValueError):
    """Another task currently owns a shared artifact."""


def lock_root() -> Path:
    """Return the shared lock root, constrained outside every checkout."""
    override = os.environ.get(LOCK_ROOT_ENVIRONMENT_VARIABLE)
    if override:
        return ensure_outside_checkout(override)
    return Path(tempfile.gettempdir()) / "clinical-skills-artifact-locks"


def lock_path(artifact: Path | str) -> Path:
    """Map an artifact identity to its scoped record outside every checkout."""
    identity = os.path.normcase(str(Path(artifact).resolve())).encode("utf-8")
    digest = hashlib.sha256(identity).hexdigest()
    return lock_root() / digest / "lock"


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


def _prepare(stream: BinaryIO) -> None:
    stream.seek(0, os.SEEK_END)
    if stream.tell() == 0:
        stream.write(b"\0")
        stream.flush()


def _busy(artifact: Path, owner: str, *, reader: bool) -> ArtifactBusy:
    detail = f" ({owner})" if owner else ""
    activity = "rebuilding" if reader else "rebuilding or reading"
    return ArtifactBusy(
        f"another task is {activity} {artifact}{detail}; retry after that task finishes"
    )


def _record(stream: BinaryIO, action: str) -> None:
    record = {
        "action": action,
        "pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    stream.seek(1)
    stream.truncate()
    stream.write(json.dumps(record, sort_keys=True).encode("utf-8"))
    stream.flush()


@contextmanager
def _handoff(scoped_record_path: Path, artifact: Path) -> Iterator[None]:
    """Serialize the short ownership handoff, never the artifact operation."""
    handoff_path = scoped_record_path.parent / "handoff"
    with handoff_path.open("a+b") as stream:
        _prepare(stream)
        deadline = time.monotonic() + 1.0
        while True:
            try:
                _try_lock(stream)
                break
            except (BlockingIOError, PermissionError):
                if time.monotonic() >= deadline:
                    raise ArtifactBusy(
                        f"another task is choosing an owner for {artifact}; "
                        "retry immediately"
                    ) from None
                time.sleep(0.001)
        try:
            yield
        finally:
            _unlock(stream)


@contextmanager
def _hold_read(
    artifact: Path, scoped_record_path: Path, action: str
) -> Iterator[Path]:
    suffix = f"{os.getpid()}.{uuid.uuid4().hex}"
    reader_path = scoped_record_path.parent / f"reader.{suffix}"
    reader: BinaryIO | None = None
    try:
        with _handoff(scoped_record_path, artifact):
            with scoped_record_path.open("a+b") as writer:
                _prepare(writer)
                try:
                    _try_lock(writer)
                except (BlockingIOError, PermissionError) as failure:
                    raise _busy(artifact, _owner(writer), reader=True) from failure
                else:
                    _unlock(writer)

            reader = reader_path.open("a+b")
            _prepare(reader)
            _try_lock(reader)
            _record(reader, action)
    except Exception:
        if reader is not None:
            try:
                _unlock(reader)
            except OSError:
                pass
            reader.close()
            reader_path.unlink(missing_ok=True)
        raise

    try:
        yield scoped_record_path
    finally:
        with _handoff(scoped_record_path, artifact):
            assert reader is not None
            _unlock(reader)
            reader.close()
            reader_path.unlink(missing_ok=True)


@contextmanager
def _hold_write(
    artifact: Path, scoped_record_path: Path, action: str
) -> Iterator[Path]:
    writer = scoped_record_path.open("a+b")
    _prepare(writer)
    try:
        with _handoff(scoped_record_path, artifact):
            try:
                _try_lock(writer)
            except (BlockingIOError, PermissionError) as failure:
                raise _busy(artifact, _owner(writer), reader=False) from failure

            scoped_readers = scoped_record_path.parent.glob("reader.*")
            for reader_path in scoped_readers:
                with reader_path.open("a+b") as reader:
                    _prepare(reader)
                    try:
                        _try_lock(reader)
                    except (BlockingIOError, PermissionError) as failure:
                        owner = _owner(reader)
                        _unlock(writer)
                        raise _busy(artifact, owner, reader=False) from failure
                    else:
                        _unlock(reader)
                reader_path.unlink(missing_ok=True)

            _record(writer, action)

        try:
            yield scoped_record_path
        finally:
            writer.seek(1)
            writer.truncate()
            writer.flush()
            _unlock(writer)
    finally:
        writer.close()


@contextmanager
def hold(
    artifact: Path | str, action: str, *, mode: str = "write"
) -> Iterator[Path]:
    """Read or write ``artifact`` without overlapping one of its writers."""
    if mode not in {"read", "write"}:
        raise ValueError(f"unknown artifact lock mode: {mode}")
    artifact = Path(artifact).resolve()
    scoped_record_path = lock_path(artifact)
    scoped_record_path.parent.mkdir(parents=True, exist_ok=True)
    holder = (
        _hold_read(artifact, scoped_record_path, action)
        if mode == "read"
        else _hold_write(artifact, scoped_record_path, action)
    )
    with holder:
        yield scoped_record_path
