"""Shared run-record boundaries: handwritten content and tool-owned bookkeeping.

ADR 0395 checks handwritten C0 damage before parsing. ADR 0422 keeps missing
distinct from unreadable; its caller supplies the decoder and shape validator.
Neither boundary certifies content truth or infers ownership from a filename.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import json
import os
import re
import time
import uuid


DECLARED_LIMITS = (
    'run_record_reader record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.',
    'The locked update callback owns history-dependent reads and decisions; one replacement is atomic, append remains append-only, and compound sibling recovery is best effort under the same lock rather than a cross-file transaction.',
    'Handwritten damage covers raw C0 and strings/keys in successfully decoded declared JSON bodies, not printable escape loss or outbound DEL/C1. Copied-post body tabs are the sole exception. Diagnostics use declared filenames/field names or numeric locators without values. Known historical reads retain their prior newline view and existing validation; writers and original boundaries force refusal. Callers must withhold only damaged dependencies and continue independent records.',
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
_HANDWRITTEN_DAMAGE: ContextVar[dict[Path, "DamagedRecord"] | None] = ContextVar("handwritten_record_damage", default=None)
HANDWRITTEN_DAMAGE = "handwritten-damage"
KINDS = (HANDWRITTEN_DAMAGE,)


def checked_label(path: Path) -> str:
    """A declared filename is public vocabulary; an arbitrary filename is private."""
    return path.name if path.name in SAFE_FILENAMES else "file 1 of 1"


class RecordShapeError(ValueError):
    def __init__(self, rule: str):
        self.rule = rule if rule in SHAPE_RULES else "declared record shape"
        super().__init__(self.rule)


class RecordContentError(Exception):
    """Content damage retains the handwritten-record finding meaning, exit 1."""


class DamagedRecord(RecordContentError):
    """A fully read handwritten record has damaged content, not a shape fault."""
    def __init__(self, path: Path, diagnostics: tuple[str, ...], *, raw_damage: bool = False):
        self.path = _record_key(path)
        self.diagnostics = diagnostics
        self.raw_damage = raw_damage
        self._finding: bool | None = None
        self.checks: set[str] = set()
        if (damage := _HANDWRITTEN_DAMAGE.get()) is not None:
            if previous := damage.get(self.path):
                self.diagnostics = tuple(dict.fromkeys((*previous.diagnostics, *diagnostics)))
                self.raw_damage |= previous.raw_damage
                self._finding = True if previous._finding else None
                self.checks = previous.checks
            damage[self.path] = self
        super().__init__(f"{checked_label(path)}: not graded — damaged text\n" + "\n".join(diagnostics))

    @property
    def finding(self) -> bool:
        # An unhandled damaged read cannot silently become a historical waiver.
        return self._finding is not False


@contextmanager
def capture_handwritten_damage():
    """Track one command's damaged records; local callers still continue siblings."""
    damage: dict[Path, DamagedRecord] = {}
    token = _HANDWRITTEN_DAMAGE.set(damage)
    try:
        yield damage
    finally:
        _HANDWRITTEN_DAMAGE.reset(token)


def handwritten_record_damage(path: Path) -> DamagedRecord | None:
    """Actual-path dependency state, including retained records with digest names."""
    return (_HANDWRITTEN_DAMAGE.get() or {}).get(_record_key(path))


def damaged_record_result(error: DamagedRecord, *, check: str, artifact: str | None = None,
                          force: bool = False) -> tuple[bool, str]:
    """Withhold only this record's checks; writers and existing boundaries force refusal."""
    applies = force or _handwritten_check_applies(artifact)
    current = handwritten_record_damage(error.path) or error
    current._finding = applies if current._finding is None else current._finding or applies
    error._finding = current._finding
    if not applies:
        return False, f"{check}: not graded - check starts after approval"
    current.checks.add(check)
    return True, f"{check}: not graded — damaged text\n" + "\n".join(current.diagnostics)


def _handwritten_check_applies(artifact: str | None) -> bool:
    import completion_checks
    key = "run_record_reader:" + HANDWRITTEN_DAMAGE
    if artifact is not None:
        # A known global moment is not evidence of this keyed item's approval.
        if artifact not in completion_checks.ITEM_MOMENTS.get():
            return True
        return completion_checks.active_for_item(key, artifact)
    return completion_checks.active(key)


@dataclass(frozen=True)
class HandwrittenKind:
    """Named raw JSON spans and public field vocabulary, never business validation."""
    name: str
    json_bodies: Callable[[str], tuple[tuple[str, str], ...]] = lambda text: ()
    field_names: frozenset[str] = frozenset()
    legacy_newlines: bool = True
    decode_errors: str = "strict"

    def __post_init__(self):
        if self.decode_errors not in {"strict", "replace"}:
            raise ValueError("handwritten decoding must be strict or replace")


@dataclass(frozen=True)
class HandwrittenRead:
    """Only checked text is public; diagnostics remain available for local refusal."""
    path: Path
    _text: str = field(repr=False)
    diagnostics: tuple[str, ...] = ()
    _bodies: tuple[tuple[str, object], ...] = field(default=(), repr=False)
    _decode_error: ValueError | RecursionError | None = field(default=None, repr=False)
    _raw_damage: bool = False
    _legacy_newlines: bool = True

    @property
    def text(self) -> str:
        return self.require_text()

    def require_text(self, *, force: bool = False, artifact: str | None = None) -> str:
        applies = force or _handwritten_check_applies(artifact)
        if self.diagnostics and applies:
            raise DamagedRecord(self.path, self.diagnostics, raw_damage=self._raw_damage)
        if not applies and self._legacy_newlines:
            # Inactive enforcement retains the former Path.read_text view,
            # including bare-CR handling, so existing checks do not change.
            return self._text.replace("\r\n", "\n").replace("\r", "\n")
        return self._text

    @property
    def json(self) -> object:
        return self.require_json()

    def require_json(self, *, force: bool = False, artifact: str | None = None) -> object:
        self.require_text(force=force, artifact=artifact)
        if self._decode_error is not None:
            raise self._decode_error
        if len(self._bodies) != 1:
            raise ValueError("record kind has no single JSON body")
        return self._bodies[0][1]

    @property
    def json_bodies(self) -> tuple[tuple[str, object], ...]:
        return self.require_json_bodies()

    def require_json_bodies(self, *, force: bool = False, artifact: str | None = None) -> tuple[tuple[str, object], ...]:
        self.require_text(force=force, artifact=artifact)
        if self._decode_error is not None:
            raise self._decode_error
        return self._bodies

    @property
    def raw_damage(self) -> bool:
        """Identify the original raw C0 boundary without revealing raw payload."""
        return self._raw_damage


# Unlike tracker-body #723, tabs and bare CR are damage: Windows path
# escapes can produce them. Only LF and CR immediately before LF are safe.
# This is deliberately separate from ADR 0421's wider outbound DEL/C1 set.
HANDWRITTEN_CONTROL_CHARACTERS = frozenset(chr(code) for code in range(32) if code != 10)
# Faithful classmate post bodies may contain tabs; their agent-written metadata
# still refuses them. No other record kind has a copied-body tab exception.
COPIED_TEXT_TAB_KINDS = frozenset({"copied-post"})


def _handwritten_damage(text: str):
    lines = text.split("\n")
    for number, line in enumerate(lines, 1):
        for offset, character in enumerate(line):
            if character not in HANDWRITTEN_CONTROL_CHARACTERS:
                continue
            if character == "\r" and offset == len(line) - 1 and number < len(lines):
                continue
            yield number, character


@dataclass(frozen=True)
class _JSONPairs:
    pairs: tuple[tuple[str, object], ...]


def _join_field(parent: str, child: str) -> str:
    return parent + "." + child if parent else child


def _handwritten_json(text: str, kind: HandwrittenKind, prefix: str):
    parsed = json.loads(text, object_pairs_hook=lambda pairs: _JSONPairs(tuple(pairs)))
    diagnostics = []
    def damage(value, location):
        diagnostics.extend(f"{location}: U+{ord(character):04X}"
                           for _line, character in _handwritten_damage(value))
    def visit(value, location):
        if isinstance(value, _JSONPairs):
            result = {}
            for index, (key, child) in enumerate(value.pairs, 1):
                damage(key, _join_field(location, f"key[{index}]"))
                label = (key if key in kind.field_names and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key)
                         else f"field[{index}]")
                result[key] = visit(child, _join_field(location, label))
            return result
        if isinstance(value, list):
            return [visit(child, f"{location}[{index}]") for index, child in enumerate(value)]
        if isinstance(value, str):
            damage(value, location or "value")
        return value
    decoded = visit(parsed, prefix)
    return decoded, diagnostics


def _attachment_json_bodies(text: str) -> tuple[tuple[str, str], ...]:
    header, separator, body = text.strip().partition("\n")
    return (("body", body),) if separator and header.rstrip("\r") != "ATTACHMENTS: none" else ()


def _context_json_bodies(text: str) -> tuple[tuple[str, str], ...]:
    counts = {}
    bodies = []
    for line in text.split("\n"):
        name, separator, raw = line.partition(":")
        if separator and name in {"ORDER-OBSERVATION", "GO-AHEAD", "MEMORY-LINES"}:
            counts[name] = counts.get(name, 0) + 1
            bodies.append((f"{name}[{counts[name]}]", raw.rstrip("\r")))
    return tuple(bodies)


_HANDWRITTEN_KINDS = {
    "text": HandwrittenKind("text"),
    "raw-text": HandwrittenKind("raw-text", legacy_newlines=False),
    "json": HandwrittenKind("json", lambda text: (("", text),)),
    "copied-post": HandwrittenKind("copied-post"),
    "attachments": HandwrittenKind("attachments", _attachment_json_bodies, frozenset({
        "body", "file_id", "name", "size", "sha256", "local_sha256", "local_path", "location_source", "test",
    })),
    "project-context": HandwrittenKind("project-context", _context_json_bodies,
                                    frozenset({"ORDER-OBSERVATION", "GO-AHEAD", "MEMORY-LINES"}),
                                    legacy_newlines=False),
}


def check_handwritten_text(text: str, path: Path, kind: str | HandwrittenKind = "text") -> HandwrittenRead:
    """Check already-owned text without reopening a locked writer's record."""
    if isinstance(kind, str):
        kind = _HANDWRITTEN_KINDS[kind]
    label = checked_label(path)
    body_after = next((index for index, line in enumerate(text.split("\n"), 1)
                       if not line.removesuffix("\r")), len(text.split("\n")))
    diagnostics = [f"{label}: line {line}: U+{ord(character):04X}"
                   for line, character in _handwritten_damage(text)
                   if not (character == "\t" and kind.name in COPIED_TEXT_TAB_KINDS and line > body_after)]
    raw_damage = bool(diagnostics)
    bodies = []
    failure = None
    for index, (prefix, raw) in enumerate(kind.json_bodies(text), 1):
        # A selector may name a declared public field, never an input value.
        safe = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*)(?:\[[0-9]+\])?", prefix)
        if prefix and (safe is None or safe[1] not in kind.field_names):
            prefix = f"body[{index}]"
        try:
            decoded, damaged = _handwritten_json(raw, kind, prefix)
            bodies.append((prefix, decoded))
            diagnostics.extend(f"{label}: {item}" for item in damaged)
        except (ValueError, RecursionError) as error:
            failure = failure or error
    return HandwrittenRead(path, text, tuple(diagnostics), tuple(bodies), failure, raw_damage, kind.legacy_newlines)


def read_handwritten_record(path: Path, kind: str | HandwrittenKind = "text") -> HandwrittenRead:
    """Open and check together; callers retain their missing/unreadable meanings."""
    if isinstance(kind, str):
        kind = _HANDWRITTEN_KINDS[kind]
    with path.open("r", encoding="utf-8", errors=kind.decode_errors, newline="") as stream:
        text = stream.read()
    return check_handwritten_text(text, path, kind)


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
        created_temporary = False
        try:
            if append:
                with path.open("ab") as stream:
                    stream.write(update.payload)
                    stream.flush()
                    os.fsync(stream.fileno())
            else:
                with temporary.open("xb") as stream:
                    created_temporary = True
                    stream.write(update.payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                deadline = time.monotonic() + 1.0
                while True:
                    try:
                        os.replace(temporary, path)
                        created_temporary = False  # The candidate was consumed by the replace.
                        break
                    except PermissionError as failure:
                        # Retry transient Windows sharing failures without releasing
                        # canonical ownership or extending the bounded refusal indefinitely.
                        if getattr(failure, "winerror", None) not in {5, 32, 33} or time.monotonic() >= deadline:
                            raise
                        time.sleep(0.01)
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
            if created_temporary:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass  # A refused write keeps its original classified cause.
        return update.result
