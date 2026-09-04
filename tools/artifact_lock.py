"""Nonblocking process locks for shared, out-of-repo build artifacts.

The lock root may be overridden for a bounded run, but it always remains outside
every checkout. Scoped identities bound ordinary acquisition work to one artifact;
the legacy layout remains a compatibility bridge until #877's derived tripwire
fires. What neither mechanism guards is declared in ``NOT_GUARDED``.
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
        "the compatibility window is bounded by one worktree registry",
        "The retirement tripwire cannot see separate clones. On non-Windows hosts the "
        "bridge retains its flat legacy-reader lookup, and an abandoned registered "
        "worktree keeps the bridge in place rather than risking overlap.",
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


def _legacy_record_path(scoped_record_path: Path) -> Path:
    return (
        scoped_record_path.parent.parent
        / f"{scoped_record_path.parent.name}.lock"
    )


def _legacy_reader_paths(scoped_record_path: Path) -> Iterator[Path]:
    """Find old reader records without scanning every flat lock on Windows."""
    root = scoped_record_path.parent.parent
    pattern = f"{scoped_record_path.parent.name}.reader.*"
    if os.name != "nt":
        yield from root.glob(pattern)
        return

    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    find_first = kernel32.FindFirstFileW
    find_first.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(wintypes.WIN32_FIND_DATAW))
    find_first.restype = wintypes.HANDLE
    find_next = kernel32.FindNextFileW
    find_next.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.WIN32_FIND_DATAW))
    find_next.restype = wintypes.BOOL
    find_close = kernel32.FindClose
    find_close.argtypes = (wintypes.HANDLE,)
    find_close.restype = wintypes.BOOL

    data = wintypes.WIN32_FIND_DATAW()
    handle = find_first(str(root / pattern), ctypes.byref(data))
    invalid = wintypes.HANDLE(-1).value
    if handle == invalid:
        error = ctypes.get_last_error()
        if error in {2, 18}:  # file not found; no more files
            return
        raise OSError(error, os.strerror(error), str(root / pattern))
    try:
        while True:
            yield root / data.cFileName
            if find_next(handle, ctypes.byref(data)):
                continue
            error = ctypes.get_last_error()
            if error == 18:  # no more files
                break
            raise OSError(error, os.strerror(error), str(root / pattern))
    finally:
        find_close(handle)


@contextmanager
def _handoff(scoped_record_path: Path, artifact: Path) -> Iterator[None]:
    """Serialize the short ownership handoff, never the artifact operation."""
    handoff_path = _legacy_record_path(scoped_record_path).with_suffix(".gate")
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
    reader_paths = (
        scoped_record_path.parent / f"reader.{suffix}",
        scoped_record_path.parent.parent
        / f"{scoped_record_path.parent.name}.reader.{suffix}",
    )
    readers: list[tuple[BinaryIO, Path]] = []
    try:
        with _handoff(scoped_record_path, artifact):
            writers = []
            try:
                for writer_path in (
                    _legacy_record_path(scoped_record_path),
                    scoped_record_path,
                ):
                    writer = writer_path.open("a+b")
                    writers.append(writer)
                    _prepare(writer)
                    try:
                        _try_lock(writer)
                    except (BlockingIOError, PermissionError) as failure:
                        raise _busy(artifact, _owner(writer), reader=True) from failure
                    else:
                        _unlock(writer)

                for reader_path in reader_paths:
                    reader = reader_path.open("a+b")
                    readers.append((reader, reader_path))
                    _prepare(reader)
                    _try_lock(reader)
                    _record(reader, action)
            finally:
                for writer in writers:
                    writer.close()
    except Exception:
        for reader, reader_path in readers:
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
            for reader, reader_path in readers:
                _unlock(reader)
                reader.close()
                reader_path.unlink(missing_ok=True)


@contextmanager
def _hold_write(
    artifact: Path, scoped_record_path: Path, action: str
) -> Iterator[Path]:
    writer = scoped_record_path.open("a+b")
    legacy_writer = _legacy_record_path(scoped_record_path).open("a+b")
    _prepare(writer)
    _prepare(legacy_writer)
    try:
        with _handoff(scoped_record_path, artifact):
            locked = []
            for stream in (legacy_writer, writer):
                try:
                    _try_lock(stream)
                    locked.append(stream)
                except (BlockingIOError, PermissionError) as failure:
                    for acquired in reversed(locked):
                        _unlock(acquired)
                    raise _busy(artifact, _owner(stream), reader=False) from failure

            scoped_readers = scoped_record_path.parent.glob("reader.*")
            legacy_readers = _legacy_reader_paths(scoped_record_path)
            for reader_path in (*scoped_readers, *legacy_readers):
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
            _record(legacy_writer, action)

        try:
            yield scoped_record_path
        finally:
            for stream in (writer, legacy_writer):
                stream.seek(1)
                stream.truncate()
                stream.flush()
                _unlock(stream)
    finally:
        writer.close()
        legacy_writer.close()


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
