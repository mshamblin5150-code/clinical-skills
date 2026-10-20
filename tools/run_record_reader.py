"""Shared tool-written record read: missing is distinct from unreadable (ADR 0422).

The caller supplies the record's decoder and shape validator. This adapter does
not certify the content's truth or infer a schema from its filename.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar
from contextlib import contextmanager
from contextvars import ContextVar
import json
import re
import time

T = TypeVar("T")

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


class UnreadableRecord(ValueError):
    """An existing record could not be decoded into its declared shape."""
    def __init__(self, path: Path, cause: str):
        self.path, self.cause = Path(path).resolve(), cause
        super().__init__(f"{checked_label(Path(path))}: unreadable — {cause}")
        if (faults := _FAULTS.get()) is not None:
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


def positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def object_record(text: str) -> dict:
    value = json.loads(text)
    if not isinstance(value, dict):
        raise RecordShapeError("record object")
    return value


POSTING_SKILLS = frozenset({"discussion-post", "discussion-reply", "peer-critique",
                           "practicum-case-study", "clinical-note", "batch-shift"})


def valid_posting_item(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    return bool(
        item.get("skill") in POSTING_SKILLS
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
    if value.get("version") != 1 or not positive_integer(value.get("approval_revision")):
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
    return value


def frozen_record(text: str) -> dict:
    value = object_record(text)
    items = value.get("items", {})
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
    return value


def read_tool_record(path: Path, decode: Callable[[str], T]) -> T | None:
    """Return None only for an absent file; never recover partial evidence."""
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            text = stream.read()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as failure:
        raise UnreadableRecord(path, f"does not decode at byte offset {failure.start}") from failure
    except OSError as failure:
        raise UnreadableRecord(path, "could not be opened") from failure
    try:
        return decode(text)
    except json.JSONDecodeError as failure:
        raise UnreadableRecord(path, f"does not decode at line {failure.lineno} column {failure.colno}") from failure
    except RecordShapeError as failure:
        raise UnreadableRecord(path, f"wrong shape: {failure.rule}") from failure
    except (ValueError, TypeError, KeyError, AttributeError) as failure:
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
                except (OSError, ValueError, AttributeError):
                    pass
                raise UnreadableRecord(path, f"held by another task: {holder}") from None
            time.sleep(0.01)
    try:
        yield
    finally:
        manager.__exit__(None, None, None)
