"""Shared tool-written record read: missing is distinct from unreadable (ADR 0422).

The caller supplies the record's decoder and shape validator. This adapter does
not certify the content's truth or infer a schema from its filename.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import json
import os
import re
import time
import uuid


DECLARED_LIMITS = (
    'run_record_reader record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.',
)

T = TypeVar("T")


@dataclass(frozen=True)
class RecordUpdate:
    """Replacement bytes and caller result; None explicitly leaves evidence untouched."""
    payload: bytes | None
    result: object = None
    rollback: Callable[[], None] | None = None

# ADR 0421 outbound damage set; ADR 0423 applies it to reference sheets.
# CR is conditional: only CR immediately before LF is a line ending.
OUTBOUND_CONTROL_CHARACTERS = frozenset(
    chr(code) for code in (*range(32), *range(127, 160)) if code != 10
)


def outbound_text_damage(text: str, *, allow_tab: bool = False) -> tuple[tuple[int, str], ...]:
    """Name every damaged line/character pair without disclosing its text."""
    found: dict[tuple[int, str], None] = {}
    line = 1
    for offset, character in enumerate(text):
        if character == "\n":
            line += 1
        elif character in OUTBOUND_CONTROL_CHARACTERS:
            if character == "\r" and text[offset + 1:offset + 2] == "\n":
                continue
            if character == "\t" and allow_tab:
                continue
            found[(line, character)] = None
    return tuple(found)


SAFE_FILENAMES = frozenset({
    "posting-approvals.json", "submission-gates.json", "frozen-grades.json", "run-status.json",
    "bar-signatures.json", "voice-model-identity.json", "chain.json", "capture.json",
    "pass-1.json", "pass-2.json", "disagreements.json", "slide-terms.json", "openers.json",
    "outbound-searches.jsonl", "uptodate-pulls.jsonl", "reread.md", "project-context.md",
})
SHAPE_RULES = frozenset({"record object", "record fields", "record items", "record revision",
                         "record item fields", "unique submission keys", "record header fields"})
_FAULTS: ContextVar[dict[Path, "UnreadableRecord"] | None] = ContextVar("tool_record_faults", default=None)


def checked_label(path: Path) -> str:
    """A declared filename is public vocabulary; an arbitrary filename is private."""
    return path.name if path.name in SAFE_FILENAMES else "file 1 of 1"


class RecordShapeError(ValueError):
    def __init__(self, rule: str):
        self.rule = rule if rule in SHAPE_RULES else "declared record shape"
        super().__init__(self.rule)


class RecordContentError(Exception):
    """Content damage retains the handwritten-record finding meaning, exit 1."""


def _record_key(path: Path) -> Path:
    try:
        return Path(path).resolve()
    except (OSError, RuntimeError):
        return Path(path).absolute()


class UnreadableRecord(ValueError):
    """An existing record could not be decoded into its declared shape."""
    def __init__(self, path: Path, cause: str):
        self.path, self.cause = _record_key(path), cause
        self.dependent_checks: set[str] = set()
        super().__init__(f"{checked_label(Path(path))}: unreadable — {cause}")
        if (faults := _FAULTS.get()) is not None:
            if previous := faults.get(self.path):
                self.dependent_checks = previous.dependent_checks
            faults[self.path] = self


@contextmanager
def capture_errors():
    """One command counts each unreadable record once, even through several readers."""
    faults: dict[Path, UnreadableRecord] = {}
    token = _FAULTS.set(faults)
    try:
        yield faults
    finally:
        _FAULTS.reset(token)


def fault_report(error: UnreadableRecord, *, check: str) -> str:
    return f"{check}: not graded - tool-written record unreadable\n{error}"


def collecting_errors() -> bool:
    return _FAULTS.get() is not None


def mark_not_graded(error: UnreadableRecord, *, check: str) -> None:
    """Retain a named dependent check in this command's record-fault report."""
    if not collecting_errors():
        raise error
    error.dependent_checks.add(check)


def has_errors() -> bool:
    return bool(_FAULTS.get())


def unreadable_record(path: Path) -> bool:
    faults = _FAULTS.get()
    return faults is not None and _record_key(path) in faults


def unreadable_kind(filename: str) -> bool:
    """Dependent checks in a single-run command cannot use a damaged record kind."""
    return any(path.name == filename for path in (_FAULTS.get() or ()))


def positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def json_record(text: str):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise RecordShapeError("unique submission keys")
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=unique_object)


def object_record(text: str) -> dict:
    value = json_record(text)
    if not isinstance(value, dict):
        raise RecordShapeError("record object")
    return value


def valid_posting_item(item: object) -> bool:
    from run_status_stop_hook import RUN_KIND_BY_SKILL
    if not isinstance(item, dict):
        return False
    skill = item.get("skill")
    return bool(
        isinstance(skill, str) and skill in RUN_KIND_BY_SKILL and skill != "course-assignment"
        and isinstance(item.get("submission"), str) and item["submission"]
        and isinstance(item.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        and isinstance(item.get("sources"), list) and item["sources"]
        and all(isinstance(path, str) and path for path in item["sources"])
        and isinstance(item.get("grader_args"), list) and item["grader_args"]
        and all(isinstance(arg, str) for arg in item["grader_args"])
        and "--submission" not in item["grader_args"]
        and item.get("posting_route") in {"awaiting-posting", "agent", "clinician"}
        and item.get("pregrade_status") in {"clean", "incomplete"}
        and positive_integer(item.get("approval_revision"))
    )


def posting_record(text: str) -> dict:
    value = object_record(text)
    if type(value.get("version")) is not int or value["version"] != 1 or not positive_integer(value.get("approval_revision")):
        raise RecordShapeError("record revision")
    items = value.get("items")
    if not isinstance(items, list) or not all(valid_posting_item(item) for item in items):
        raise RecordShapeError("record item fields")
    keys = [(item["skill"], item["submission"]) for item in items]
    if len(keys) != len(set(keys)):
        raise RecordShapeError("unique submission keys")
    return value


def submission_record(text: str) -> dict:
    value = object_record(text)
    if not positive_integer(value.get("approval_revision")):
        raise RecordShapeError("record revision")
    if value.get("gate1_approved") is not True or not isinstance(value.get("artifact_path"), str) or not value["artifact_path"]:
        raise RecordShapeError("record fields")
    if (not isinstance(value.get("artifact"), str) or not value["artifact"]
            or not isinstance(value.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"])
            or type(value.get("attachment_count")) is not int or value["attachment_count"] < 1
            or not isinstance(value.get("uploaded_files"), list)
            or not all(isinstance(name, str) and name for name in value["uploaded_files"])):
        raise RecordShapeError("record fields")
    carriers = value.get("approved_carriers")
    if not isinstance(carriers, list) or not carriers:
        raise RecordShapeError("record items")
    names = []
    for row in carriers:
        if (not isinstance(row, dict) or not isinstance(row.get("filename"), str) or not row["filename"]
                or not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise RecordShapeError("record item fields")
        names.append(row["filename"])
    if len(names) != len(set(names)) or len(value["uploaded_files"]) != len(set(value["uploaded_files"])):
        raise RecordShapeError("unique submission keys")
    # Older legitimate records use the two Gate 2 booleans instead of upload_route.
    route = value.get("upload_route")
    if route is not None and route not in ("awaiting-upload", "agent", "clinician"):
        raise RecordShapeError("record fields")
    return value


def frozen_record(text: str) -> dict:
    value = object_record(text)
    items = value.get("items")
    if not isinstance(items, dict):
        raise RecordShapeError("record items")
    for key, item in items.items():
        if (not isinstance(key, str) or not key or not isinstance(item, dict)
                or not positive_integer(item.get("approval_revision"))
                or not isinstance(item.get("frozen_at"), str)
                or item.get("kind") not in {"graded clean", "frozen at adoption, never graded clean"}
                or not isinstance(item.get("sources"), dict)):
            raise RecordShapeError("record item fields")
    return value


def state_record(text: str) -> dict:
    value = object_record(text)
    if value.get("status") not in {"complete", "stopped"} or not isinstance(value.get("approval_revision"), str):
        raise RecordShapeError("record fields")
    revisions = json.loads(value["approval_revision"])
    if not isinstance(revisions, list):
        raise RecordShapeError("record revision")
    for row in revisions:
        if (not isinstance(row, list) or len(row) != 3 or not all(isinstance(v, str) and v for v in row[:2])
                or not positive_integer(row[2])):
            raise RecordShapeError("record item fields")
    keys = [tuple(row[:2]) for row in revisions]
    if len(keys) != len(set(keys)):
        raise RecordShapeError("unique submission keys")
    return value


def read_tool_record(path: Path, decode: Callable[[str], T]) -> T | None:
    """Return None only for an absent file; never recover partial evidence."""
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            text = stream.read()
    except FileNotFoundError as failure:
        try:
            path.lstat()
        except FileNotFoundError:
            return None
        except OSError:
            pass
        raise UnreadableRecord(path, "could not be opened") from failure
    except UnicodeDecodeError as failure:
        if path.suffix.casefold() == ".md":
            cause = f"does not decode at byte offset {failure.start}"
        else:
            prefix = failure.object[:failure.start].decode("utf-8", errors="ignore")
            cause = f"does not decode at line {prefix.count(chr(10)) + 1} column {len(prefix.rsplit(chr(10), 1)[-1]) + 1}"
        raise UnreadableRecord(path, cause) from failure
    except OSError as failure:
        raise UnreadableRecord(path, "could not be opened") from failure
    try:
        return decode(text)
    except UnreadableRecord:
        raise
    except json.JSONDecodeError as failure:
        raise UnreadableRecord(path, f"does not decode at line {failure.lineno} column {failure.colno}") from failure
    except RecordShapeError as failure:
        raise UnreadableRecord(path, f"wrong shape: {failure.rule}") from failure
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as failure:
        raise UnreadableRecord(path, "wrong shape: declared record shape") from failure


@contextmanager
def locked_record(path: Path):
    """Exclusive bookkeeping lock with a bounded retry and safe holder identity."""
    import artifact_lock
    deadline = time.monotonic() + 1.0
    while True:
        manager = artifact_lock.hold(path, "update tool-written run record")
        try:
            manager.__enter__()
            break
        except artifact_lock.ArtifactBusy:
            if time.monotonic() >= deadline:
                holder = "another task"
                try:
                    with artifact_lock.lock_path(path).open("rb") as stream:
                        stream.seek(1)  # Windows reserves byte zero for the actual lock.
                        raw = stream.read()
                    owner = json.loads(raw)
                    if type(owner.get("pid")) is int and owner["pid"] > 0:
                        holder = f"process {owner['pid']}"
                except (OSError, ValueError, AttributeError, RecursionError):
                    pass
                raise UnreadableRecord(path, f"held by another task: {holder}") from None
            time.sleep(0.01)
    try:
        yield
    finally:
        manager.__exit__(None, None, None)


def update_tool_record(
    path: Path, decode: Callable[[str], T], change: Callable[[T | None], RecordUpdate],
    *, append: bool = False,
) -> object:
    """Own the exclusive read/change/write transaction, or an explicit no-write result.

    The callback runs under the lock and must make history-dependent decisions there.
    Append-only kinds validate their whole prior record before appending under this lock.
    Other kinds replace one file atomically; no cross-file transaction is promised.
    """
    path = Path(path)
    with locked_record(path):
        previous = read_tool_record(path, decode)
        update = change(previous)
        if update.payload is None:
            return update.result
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
        try:
            if append:
                with path.open("ab") as stream:
                    stream.write(update.payload)
                    stream.flush()
                    os.fsync(stream.fileno())
            else:
                with temporary.open("xb") as stream:
                    stream.write(update.payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
        except BaseException as failure:
            if update.rollback is not None:
                try:
                    update.rollback()
                except BaseException:
                    pass  # Preserve the original persistence failure, never its private details.
            if isinstance(failure, OSError):
                raise UnreadableRecord(path, "could not be opened") from failure
            raise
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass  # A refused write keeps its original classified cause.
        return update.result
