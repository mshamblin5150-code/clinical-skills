"""One dated completion-check registry, with a declared source derivation floor.

The walk follows literal local imports from the seven terminal graders and the
assignment adapters. It recognizes literal Finding kinds, literal keys/values
in KINDS, ROWS, EXPECTED_CHECKS and EXPECTED_ROW, and completion_gate functions.
Computed kinds, dynamic imports and checks assembled under other names remain
outside this derivation. For this checkout, the same named exported collections
are also read from imported modules, including forwarded rows and tuple spreads.
Dataclass Scan fields read by grade/_grade are registered as aggregate checks;
computed properties and other result shapes remain outside this field walk.
The suite binds this floor and tests a new literal kind.
Unreadable tool-written approval bookkeeping establishes no historical exemption;
captured commands retain its record fault and grade independent current checks.
"""
from __future__ import annotations

import ast
import importlib
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import replace, fields
from datetime import date, datetime, timezone
from functools import lru_cache
from functools import wraps
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLE = ROOT.parent / "reference" / "completion-check-starts.tsv"
SEEDS = ("discussion_post_scan", "discussion_reply_scan", "peer_critique_scan",
         "checks_ledger", "differential_scan", "filled_vitals_census",
         "course_assignment_scan", "deck_scan", "assignment_docx_scan")
DECLARED_LIMITS = (__doc__,)
MOMENTS = ContextVar("completion_check_moments", default={})
ITEM_MOMENTS = ContextVar("completion_item_moments", default={})
SKIPPED = ContextVar("completion_checks_not_graded", default=None)


def derive(directory: Path = ROOT) -> dict[str, str]:
    """Return check identifiers and defining literals under the declared floor."""
    pending, seen, result = list(SEEDS), set(), {}
    while pending:
        module = pending.pop()
        path = directory / (module + ".py")
        if module in seen or not path.is_file():
            continue
        seen.add(module)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        literals = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name) and isinstance(node.value.value, str):
                        literals[target.id] = node.value.value
        def strings(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return (node.value,)
            if isinstance(node, ast.Name):
                return (literals[node.id],) if node.id in literals else ()
            if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
                return tuple(s for child in node.elts for s in strings(child))
            if isinstance(node, ast.Dict):
                return tuple(s for child in node.keys if child is not None for s in strings(child))
            return ()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                pending.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                pending.append(node.module)
            elif isinstance(node, ast.Call) and node.args:
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                if name == "Finding":
                    for kind in strings(node.args[0]):
                        result[module + ":" + kind] = kind
            elif isinstance(node, ast.Assign):
                if any(isinstance(t, ast.Name) and t.id in {
                    "KINDS", "ROWS", "ROW_TICKET", "EXPECTED_CHECKS", "EXPECTED_ROW",
                    "POSTED_READING_MESSAGES"} for t in node.targets):
                    for kind in strings(node.value):
                        result[module + ":" + kind] = kind
            elif isinstance(node, ast.FunctionDef) and node.name == "completion_gate":
                result[module + ":completion_gate"] = "def completion_gate"
    if directory.resolve() == ROOT.resolve():
        for module in seen:
            imported = importlib.import_module(module)
            for name in ("KINDS", "ROWS", "ROW_TICKET", "EXPECTED_CHECKS", "EXPECTED_ROW", "POSTED_READING_MESSAGES"):
                value = getattr(imported, name, ())
                entries = (value,) if isinstance(value, str) else value if isinstance(value, (dict, tuple, list)) else ()
                for kind in entries:
                    if isinstance(kind, str):
                        result[module + ":" + kind] = kind
            scan_class = getattr(imported, "Scan", None)
            if scan_class is not None and hasattr(scan_class, "__dataclass_fields__"):
                tree = ast.parse((directory / (module + ".py")).read_text(encoding="utf-8"))
                for function in tree.body:
                    if isinstance(function, ast.FunctionDef) and function.name in {"grade", "_grade"}:
                        for node in ast.walk(function):
                            if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                                    and node.value.id in {"scan", "scanned"} and node.attr in scan_class.__dataclass_fields__):
                                result[module + ":scan:" + node.attr] = node.attr
    # These checks raise a boolean result rather than a literal Finding kind.
    result.update({"coursework_run:draft-order": "def grade_order",
                   "project_context:classmate": "CLASSMATE_CUTOFF",
                   "research_ledger:qualifiers": "QUALIFIER_CUTOFF",
                   "research_ledger:stated-expiry": "STATED-EXPIRY",
                   "approval_record:posting-go-ahead": "POSTING_GO_AHEAD_CUTOFF"})
    result["reader_remarks:unread-reader-record"] = "unread = sum"
    for name in ("REVIEW_CLASSIFIER_ENTRY", "POSTED_READING_FINGERPRINT", "UNREAD_REMAINDER",
                 "LANDING_OUTPUT", "MEMORY_MEASUREMENT", "SYSTEM_SUBTYPE"):
        result["aar_scan:" + name.lower().replace("_", "-")] = name + "_CUTOFF"
    return result


@lru_cache(maxsize=1)
def registry() -> dict[str, tuple[datetime, str]]:
    result = {}
    for line in TABLE.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        key, start, moment = line.split("\t")
        if key in result or moment not in {"approval", "extraction", "confirmation", "ledger"}:
            raise ValueError("invalid completion-check start row: " + key)
        parsed = datetime.fromisoformat(start.replace("Z", "+00:00"))
        timestamp = parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
        result[key] = (timestamp, moment)
    return result


def instant(value) -> datetime | None:
    try:
        if isinstance(value, datetime):
            return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time(), timezone.utc)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return datetime.fromtimestamp(value, timezone.utc)
        if isinstance(value, str):
            return instant(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except (ValueError, OverflowError, OSError):
        pass
    return None


def active(key: str, moment=None) -> bool:
    start, compared_with = registry()[key]
    observed = instant(moment) if moment is not None else MOMENTS.get().get(compared_with)
    # Missing historical evidence grants no exemption.
    applies = observed is None or observed >= start
    if not applies and SKIPPED.get() is not None:
        SKIPPED.get().add(key)
    return applies


def active_for_item(key: str, artifact: str) -> bool:
    """Use an item's own moment; an unknown item never inherits a sibling's date."""
    items = ITEM_MOMENTS.get()
    if not items:
        return active(key)
    observed = items.get(artifact)
    return True if observed is None else active(key, observed)


def approval_moment(run: Path, submission: str):
    import frozen_grade
    from run_record_reader import UnreadableRecord, collecting_errors
    try:
        approval = frozen_grade.approved(run, submission)
    except UnreadableRecord:
        if not collecting_errors():
            raise
        return None  # No historical exemption is established; record coverage retains the fault.
    if approval is None:
        return None
    item = approval[1]
    history = item.get("approvals", ())
    contents = [row for row in history if isinstance(row, dict) and row.get("approval_kind") == "content"]
    content = contents[-1] if contents else item
    return content.get("recorded_at", content.get("reply_matched_at"))


@contextmanager
def grading(run: Path, submission: str | None):
    import frozen_grade
    items = {}
    moments = []
    for key in (submission or "").split(","):
        key = key.strip()
        if not key:
            continue
        observed = instant(approval_moment(run, key))
        moments.append(observed)
        items[key] = observed
        from run_record_reader import UnreadableRecord, collecting_errors
        try:
            approval = frozen_grade.approved(run, key)
        except UnreadableRecord:
            if not collecting_errors():
                raise
            approval = None
        if approval is not None:
            for path in (*approval[1].get("sources", ()), *approval[1].get("note_sources", ())):
                items[Path(path).name] = observed
    known = [value for value in moments if value is not None]
    # Multi-item callers select each item themselves; no unknown date is waived.
    value = max(known) if known and len(known) == len(moments) else None
    token = MOMENTS.set({"approval": value})
    item_token = ITEM_MOMENTS.set(items)
    skipped = SKIPPED.set(set())
    try:
        yield
    finally:
        MOMENTS.reset(token)
        ITEM_MOMENTS.reset(item_token)
        SKIPPED.reset(skipped)


def filter_findings(module: str, findings, *, moment=None, ledger_date=None):
    selected = []
    for finding in findings:
        key = module + ":" + finding.kind
        observed = moment
        if registry()[key][1] == "ledger":
            observed = ledger_date
        applies = None
        if observed is None and registry()[key][1] == "approval":
            artifact = getattr(finding, "artifact", getattr(finding, "response", ""))
            if artifact:
                applies = active_for_item(key, artifact)
        if applies is None:
            applies = active(key, observed)
        if applies:
            selected.append(finding)
    return tuple(selected)


def filter_scan(module: str, scan):
    original = scan.findings
    findings = filter_findings(module, original, ledger_date=getattr(scan, "as_of", None))
    values = {"findings": findings} if len(findings) != len(original) else {}
    names = {f.name for f in fields(scan)}
    if values and "counts" in names:
        values["counts"] = tuple((kind, sum(f.kind == kind for f in findings)) for kind, _ in scan.counts)
    if values and "failing_checks" in names:
        values["failing_checks"] = len(findings)
    if values and "failing_records" in names:
        values["failing_records"] = len({getattr(f, "claim", "") for f in findings})
    for name in names:
        key = module + ":scan:" + name
        if key not in registry() or active(key):
            continue
        value = getattr(scan, name)
        if name.endswith("_graded"):
            values[name] = True
        elif isinstance(value, (int, bool)):
            values[name] = 0
        elif isinstance(value, tuple):
            values[name] = ()
    if not values:
        return scan
    return replace(scan, **values)


def report() -> str:
    return "\n".join(key + ": not graded - check starts after its comparison moment" for key in sorted(SKIPPED.get() or ()))


def dated_scan(function):
    """Filter a scanner's rows before its caller computes terminal status."""
    @wraps(function)
    def scan(*args, **kwargs):
        result = function(*args, **kwargs)
        if MOMENTS.get() and hasattr(result, "findings"):
            module = Path(function.__code__.co_filename).stem
            return filter_scan(module, result)
        return result
    return scan


def dated_posted_reading(function):
    @wraps(function)
    def check(run, submission, *args, **kwargs):
        if MOMENTS.get():
            return function(run, submission, *args, **kwargs)
        with grading(run, submission):
            return function(run, submission, *args, **kwargs)
    return check


def exemption(run: Path, submission: str | None, module: str, label: str) -> str | None:
    """Frozen evidence precedes the start-date comparison at every shared gate."""
    import frozen_grade
    frozen = frozen_grade.all_reports(run, submission)
    if frozen is not None:
        return frozen
    if not active(module + ":completion_gate"):
        return label + ": not graded - approval predates the check"
    return None
