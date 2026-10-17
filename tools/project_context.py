#!/usr/bin/env python3
"""Write and grade the confirmed project-context retrieval record. #1395.

``DECLARED_LIMITS`` is the complete ceiling of a clean project-context row.
Scoped graders and ``CLAUDE.md`` name this object and copy no row.
"""

from __future__ import annotations

import completion_checks
import json
from collections import Counter
import re
import sys
from dataclasses import dataclass, field, replace
from datetime import date
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, TypeVar

import coursework_run
import memory_index
import aar_scan
import repo_root
import run_grader
import uptodate_store
from console_codec import require_python_floor, use_utf8


RECORD_NAME = "project-context.md"
EXPECTED_ROW = "the confirmed project context"
SCOPED_SKILLS = frozenset(
    {
        "course-assignment",
        "discussion-post",
        "discussion-reply",
        "peer-critique",
        "practicum-case-study",
    }
)
COMPLETION_GRADERS = MappingProxyType(
    {skill: aar_scan.COMPLETION_GRADERS[skill] for skill in SCOPED_SKILLS}
)
CLASSMATE_CUTOFF = completion_checks.registry()["project_context:classmate"][0].date()
CLASSMATE_SKILLS = MappingProxyType({
    "discussion-reply": re.compile(r"response-.+\.md"),
    "peer-critique": re.compile(r"critique\.md"),
})
CLASSMATE_FIELDS = ("CLASSMATE-POST", "CLASSMATE-BOARD", "CLASSMATE-ATTACHMENT")
DECLARED_LIMITS = (
    ("unregistered-assets-unseen", "An asset the clinician never registers or names at confirmation is owed by nothing."),
    ("printable-write-damage-unseen", "The write preflight cannot detect damage that leaves only printable characters, such as a lost backslash."),
    ("later-control-damage-unchecked", "Go-ahead and completion re-reads do not check control characters introduced after the last --write."),
    ("other-record-damage-unchecked", "The write preflight checks only project-context.md and the account registry, not other hand-written run records."),
    ("heredoc-route-ungraded", "The write preflight checks file contents, not whether a heredoc was used to write them."),
    ("classmate-identity-unverified", "The gate checks that declared classmate files were opened, never that they belong to the selected classmate."),
    ("course-history-completeness-unverified", "The gate cannot tell whether the declared course history is complete, because course codes in names are unreliable."),
    ("date-only-confirmation-granularity", "A date-only confirmation compares as midnight UTC; the gate cannot place it before or after an intraday start on that date."),
    ("approval-notice-unverified", "Approval verifies the shown draft, not whether the clinician saw the moved-item notice."),
    ("added-memory-lines-ungraded", "Added memory-index lines are shown for the clinician's reading; their bearing on the draft is not graded."),
    ("pre-check-approvals", "Posted approvals predating the go-ahead check are named and counted, and pass without a recorded check."),
    (
        "retrieval-before-draft-unobservable",
        "The historical first observation cannot see a draft deleted or moved before the gate, "
        "prose at other locations, or conversation prose saved only after the gates. "
        "Order waivers depend on this confirmed header across both records.",
    ),
    (
        "agreement-is-a-reading",
        "A clean shape cannot establish that an agrees verdict is substantively true.",
    ),
    (
        "agreement-inherits-item-errors",
        "An agrees verdict measures the draft against the opened items only, so an error "
        "an item carries about itself is agreed with.",
    ),
    (
        "semantic-search-ranked-tail-unseen",
        "A semantic search cannot show which items ranked below its returned cutoff.",
    ),
    (
        "service-items-not-rehashed",
        "Captured service items cannot be retrieved and hashed again at completion.",
    ),
    (
        "heading-reader-is-the-use-ceiling",
        "A narrower draft is caught only as far as the shared heading reader catches it.",
    ),
)

_URL = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ENTRY_HEADER = re.compile(r"^##[ \t]+PLACE:[ \t]*(.+?)[ \t]*$", re.IGNORECASE)
_ANY_HEADER = re.compile(r"^#{1,6}[ \t]+")
_FIELD = re.compile(r"^([A-Z][A-Z-]*):[ \t]*(.*)$", re.IGNORECASE)
_SEARCH = re.compile(r'^(.+?)[ \t]+-[ \t]+"(.*)"$')
_WAIVER = re.compile(
    r"^(?P<failure>.+?)[ \t]+(?P<when>[0-9]{4}-[0-9]{2}-[0-9]{2})"
    r"; proceed without, per the clinician$"
)
_QUERY = re.compile(
    r"^(?P<terms>.+?)[ \t]+\|[ \t]+THRESHOLD:[ \t]*(?P<threshold>[^|]+?)"
    r"[ \t]+\|[ \t]+LIMIT:[ \t]*(?P<limit>[0-9]+)"
    r"[ \t]+\|[ \t]+HITS:[ \t]*(?P<hits>[0-9]+)$",
    re.IGNORECASE,
)
_OPENED = re.compile(
    r"^(?P<item>.+?)[ \t]+\|[ \t]+SHA256:[ \t]*(?P<digest>[0-9a-f]{64})$",
    re.IGNORECASE,
)
_HEADER_FIELDS = frozenset(
    {"PROJECT-CONTEXT", "OWN-SUBMISSION", "CASE-MATERIAL", "CASE-RESEARCH", "PROJECT-SEARCH", "PROJECT-WAIVE", "CONFIRMED", "CONTEXT-DIGEST", "ORDER-WAIVE", "ORDER-OBSERVATION", "GO-AHEAD"}
) | frozenset(CLASSMATE_FIELDS) | {"ASSET", "COURSE-HISTORY"}
_ENTRY_FIELDS = frozenset(
    {
        "STATE",
        "ROOT",
        "TERMS",
        "EXAMINED",
        "UNREADABLE",
        "CORPUS-SIZE",
        "QUERY",
        "OPENED",
        "DETAIL",
        "MEMORY-LINES",
    }
)
_REPEATABLE_HEADER = frozenset({"PROJECT-SEARCH", "PROJECT-WAIVE", "ORDER-WAIVE", "ORDER-OBSERVATION", "GO-AHEAD", "ASSET", "COURSE-HISTORY", *CLASSMATE_FIELDS})
_REPEATABLE_ENTRY = frozenset({"QUERY", "OPENED"})
TScan = TypeVar("TScan")


@dataclass(frozen=True)
class Project:
    name: str
    locations: tuple[str, ...]
    services: tuple[str, ...]
    assets: tuple[str, ...] = ()


@dataclass(frozen=True)
class Registry:
    memory_index: str
    projects: Mapping[str, Project]


@dataclass(frozen=True)
class Opened:
    item: str
    digest: str | None = None


@dataclass(frozen=True)
class Entry:
    place: str
    fields: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def values(self, name: str) -> tuple[str, ...]:
        return self.fields.get(name, ())

    def value(self, name: str) -> str:
        values = self.values(name)
        return values[0] if values else ""


@dataclass(frozen=True)
class Record:
    fields: Mapping[str, tuple[str, ...]]
    entries: tuple[Entry, ...]

    def values(self, name: str) -> tuple[str, ...]:
        return self.fields.get(name, ())

    def value(self, name: str) -> str:
        values = self.values(name)
        return values[0] if values else ""


@dataclass(frozen=True)
class OwedPlace:
    place: str
    kind: str
    directed_terms: str | None = None


@dataclass(frozen=True)
class GateResult:
    exit_code: int
    report: str
    waived: int = 0
    digest: str | None = None


@dataclass(frozen=True)
class CompletionGate:
    finding: bool
    coverage: bool
    report: str
    moved_places: tuple[str, ...] = ()
    added_lines: tuple[str, ...] = ()


class RegistryCoverage(ValueError):
    """The registry could not establish the owed population."""


class RegistryFinding(ValueError):
    """The registry was readable but violated its public shape."""


def _append(target: dict[str, list[str]], name: str, value: str) -> None:
    target.setdefault(name, []).append(value.strip())


def read_registry(text: str) -> Registry:
    """Parse the account registry without inferring any path or service."""
    memory: list[str] = []
    projects: dict[str, Project] = {}
    current_name: str | None = None
    current_locations: list[str] = []
    current_services: list[str] = []
    current_assets: list[str] = []

    def close_project() -> None:
        nonlocal current_name, current_locations, current_services, current_assets
        if current_name is None:
            return
        if current_name in projects:
            raise RegistryFinding("duplicate PROJECT entry")
        projects[current_name] = Project(
            current_name, tuple(current_locations), tuple(current_services), tuple(current_assets)
        )
        current_name, current_locations, current_services = None, [], []
        current_assets = []

    for raw in text.splitlines():
        if not raw.strip():
            continue
        stripped = raw.strip()
        if stripped.startswith("MEMORY-INDEX:"):
            close_project()
            memory.append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("PROJECT:"):
            close_project()
            current_name = stripped.split(":", 1)[1].strip()
            if not current_name:
                raise RegistryFinding("PROJECT needs a name")
        elif stripped.startswith("LOCATION:") and current_name is not None:
            current_locations.append(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("SERVICE:") and current_name is not None:
            service = stripped.split(":", 1)[1].strip()
            if _URL.match(service):
                raise RegistryFinding("a SERVICE must be an MCP server name, never a URL")
            current_services.append(service)
        elif stripped.startswith("ASSET:") and current_name is not None:
            asset = stripped.split(":", 1)[1].strip()
            if not asset:
                raise RegistryFinding("ASSET needs a description")
            if asset in current_assets:
                raise RegistryFinding("duplicate ASSET entry")
            current_assets.append(asset)
        else:
            raise RegistryFinding("unrecognized project registry line")
    close_project()
    if len(memory) != 1 or not memory[0]:
        raise RegistryFinding("the registry needs exactly one MEMORY-INDEX")
    if not Path(memory[0]).expanduser().is_absolute():
        raise RegistryFinding("MEMORY-INDEX must state an absolute path")
    for project in projects.values():
        if len(set(project.locations)) != len(project.locations):
            raise RegistryFinding("duplicate LOCATION entry")
        if len(set(project.services)) != len(project.services):
            raise RegistryFinding("duplicate SERVICE entry")
        if any(not Path(path).expanduser().is_absolute() for path in project.locations):
            raise RegistryFinding("LOCATION must state an absolute path")
        if any(not service for service in project.services):
            raise RegistryFinding("SERVICE needs an MCP server name")
    return Registry(memory[0], MappingProxyType(projects))


def read_record(text: str) -> Record:
    """Parse one purpose-named project-context record."""
    header: dict[str, list[str]] = {}
    entries: list[Entry] = []
    place: str | None = None
    fields: dict[str, list[str]] = {}

    def close_entry() -> None:
        nonlocal place, fields
        if place is not None:
            entries.append(
                Entry(place=place, fields=MappingProxyType({k: tuple(v) for k, v in fields.items()}))
            )
        place, fields = None, {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = _ENTRY_HEADER.match(line)
        if match:
            close_entry()
            place = match.group(1).strip()
            continue
        if _ANY_HEADER.match(line):
            raise ValueError("unrecognized heading in project context record")
        named = _FIELD.match(line)
        if not named:
            raise ValueError("unrecognized line in project context record")
        name, value = named.group(1).upper(), named.group(2).strip()
        if place is None:
            if name not in _HEADER_FIELDS:
                raise ValueError(f"unrecognized header field {name}")
            _append(header, name, value)
        else:
            if name not in _ENTRY_FIELDS:
                raise ValueError(f"unrecognized place field {name}")
            _append(fields, name, value)
    close_entry()
    return Record(
        fields=MappingProxyType({key: tuple(values) for key, values in header.items()}),
        entries=tuple(entries),
    )


def _duplicates(record: Record) -> list[str]:
    errors = [
        f"{name} appears more than once"
        for name, values in record.fields.items()
        if name not in _REPEATABLE_HEADER and len(values) != 1
    ]
    for entry in record.entries:
        errors.extend(
            f"{entry.place}: {name} appears more than once"
            for name, values in entry.fields.items()
            if name not in _REPEATABLE_ENTRY and len(values) != 1
        )
    return errors


def _confirmation_error(value: str) -> str | None:
    if completion_checks.instant(value) is None:
        return "CONFIRMED needs an ISO date or timestamp"
    return None


def _declaration(record: Record) -> tuple[str | None, str | None]:
    values = record.values("PROJECT-CONTEXT")
    if len(values) != 1 or not values[0]:
        return None, "PROJECT-CONTEXT is missing or duplicated"
    declaration = values[0]
    if declaration.casefold().startswith("none"):
        prefix, separator, reason = declaration.partition(" - ")
        if prefix.casefold() != "none" or not separator or not reason.strip():
            return None, "PROJECT-CONTEXT none needs a reason"
        return "none", None
    return declaration, None


def _file_declaration_error(record: Record, name: str, value: str | None = None) -> str | None:
    values = record.values(name)
    if len(values) != 1 or not values[0]:
        return f"{name} is missing or duplicated"
    value = values[0] if value is None else value
    if value.casefold().startswith("none"):
        prefix, separator, reason = value.partition(" - ")
        if prefix.casefold() != "none" or not separator or not reason.strip():
            return f"{name} none needs a reason"
        return None
    return _opened_file_error(record, name, value)


def _opened_file_error(record: Record, name: str, value: str) -> str | None:
    path = Path(value).expanduser()
    if not path.is_absolute():
        return f"{name} needs an absolute file path"
    for entry in record.entries:
        if entry.value("STATE").casefold() != "read":
            continue
        for opened_value in entry.values("OPENED"):
            opened = _opened(opened_value)
            if opened.item.casefold() == "none":
                continue
            item = Path(opened.item).expanduser()
            if not item.is_absolute():
                item = Path(entry.value("ROOT") or entry.place).expanduser() / item
            if item.resolve() == path.resolve():
                return None
    return f"{name} path is not OPENED in a read PLACE"


def _course_history_gate(record: Record) -> tuple[list[str], str]:
    """Grade declared reads, leaving the course's complete population to its reader."""
    confirmed = completion_checks.instant(record.value("CONFIRMED"))
    if confirmed is None:
        return [], ""  # The confirmation shape check owns this refusal.
    if not completion_checks.active("project_context:course-history", confirmed):
        return [], "course history: not graded; pre-cutoff records: 1"
    values = record.values("COURSE-HISTORY")
    errors = []
    if not values:
        errors.append("COURSE-HISTORY is missing")
    none = tuple(value for value in values if value.casefold().startswith("none"))
    if none:
        if len(values) != 1:
            errors.append("COURSE-HISTORY cannot put none beside another declaration")
        if any(not re.fullmatch(r"(?i)none - \S.*", value) for value in none):
            errors.append("COURSE-HISTORY none needs a reason")
    paths = [Path(value).expanduser().resolve() for value in values if value not in none]
    if len(set(paths)) != len(paths):
        errors.append("duplicate COURSE-HISTORY path")
    for value in values:
        if value not in none:
            if error := _opened_file_error(record, "COURSE-HISTORY", value):
                errors.append(error)
    return errors, "course history: " + ("finding - " + "; ".join(errors) if errors else "clean")


def _has_declared_retrieval(record: Record) -> bool:
    return any(record.values(name) for name in CLASSMATE_FIELDS) or any(
        not value.casefold().startswith("none") for value in record.values("COURSE-HISTORY")
    )


def _classmate_lines(record: Record, name: str) -> tuple[tuple[str, str], ...]:
    rows = []
    for value in record.values(name):
        key, separator, target = value.partition(" -> ")
        if not separator or not target.strip() or len(coursework_run.submission_keys(key)) != 1:
            raise ValueError(f"{name} needs a submission key -> file path or attachment none")
        rows.append((key, target.strip()))
    return tuple(rows)


def _classmate_gate(record: Record, submission: str | None) -> tuple[list[str], str]:
    if submission is None or not any(pattern.fullmatch(submission) for pattern in CLASSMATE_SKILLS.values()):
        return [], ""
    confirmed = completion_checks.instant(record.value("CONFIRMED"))
    if confirmed is None:
        return [], ""  # The confirmation shape check owns this refusal.
    if confirmed.date() < CLASSMATE_CUTOFF:
        return [], "classmate declarations: not graded; pre-cutoff records: 1"
    errors = []
    for name in CLASSMATE_FIELDS:
        try:
            targets = tuple(target for key, target in _classmate_lines(record, name) if key == submission)
        except ValueError as failure:
            errors.append(str(failure))
            continue
        if not targets or (name != "CLASSMATE-ATTACHMENT" and len(targets) != 1):
            errors.append(f"{name} for {submission} is missing or duplicated")
            continue
        none = tuple(target for target in targets if target.casefold().startswith("none"))
        if none:
            if name != "CLASSMATE-ATTACHMENT":
                errors.append(f"{name} for {submission} needs an absolute file path")
            elif len(targets) != 1:
                errors.append(f"{name} for {submission} cannot put none beside another attachment")
            elif not re.fullmatch(r"(?i)none - \S.*", none[0]):
                errors.append(f"{name} for {submission} none needs a reason")
        for target in targets:
            if target not in none:
                if error := _opened_file_error(record, name, target):
                    errors.append(error)
    return errors, "classmate declarations: " + ("finding - " + "; ".join(errors) if errors else "clean")


def other_classmate_items(run: Path, submission: str) -> tuple[str, ...]:
    """Opened identifiers declared only under another submission's classmate lines."""
    try:
        record = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
        declarations = tuple(row for name in CLASSMATE_FIELDS for row in _classmate_lines(record, name))
    except (OSError, UnicodeError, ValueError):
        return ()
    own, other = set(), set()
    for key, target in declarations:
        if target.casefold().startswith("none"):
            continue
        path = Path(target).expanduser().resolve()
        (own if key == submission else other).add(path)
    excluded = other - own
    return tuple(opened.item for entry in record.entries
                 for value in entry.values("OPENED") for opened in (_opened(value),)
                 if opened.item.casefold() != "none"
                 and _file_path(entry, opened) in excluded)


def _case_research_error(record: Record, *, recheck_files: bool) -> str | None:
    values = record.values("CASE-RESEARCH")
    if len(values) != 1 or not values[0]:
        return "CASE-RESEARCH is missing or duplicated"
    dump_id = values[0]
    if dump_id.casefold().startswith("none"):
        return _file_declaration_error(record, "CASE-RESEARCH")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", dump_id):
        return "CASE-RESEARCH needs a dump id"
    store = uptodate_store.default_store().resolve()
    source = store / "dumps" / dump_id / uptodate_store.SOURCE_NAME
    if recheck_files:
        try:
            manifest = uptodate_store.manifest_for_dump(dump_id, store)
            if manifest is None:
                return "CASE-RESEARCH dump has no manifest"
        except (OSError, UnicodeError, ValueError):
            return "CASE-RESEARCH manifest or filed copy is unreadable or has a fingerprint mismatch"
    return _file_declaration_error(record, "CASE-RESEARCH", str(source))


def _context_declaration_errors(record: Record, *, recheck_files: bool = True) -> list[str]:
    errors = [error for name in ("OWN-SUBMISSION", "CASE-MATERIAL")
              if (error := _file_declaration_error(record, name))]
    if error := _case_research_error(record, recheck_files=recheck_files):
        errors.append(error)
    assets = record.values("ASSET")
    if any(not asset for asset in assets):
        errors.append("ASSET needs a description")
    if len(set(assets)) != len(assets):
        errors.append("duplicate ASSET entry in confirmed header")
    if _declaration(record)[0] == "none" and assets:
        errors.append("a none run cannot carry ASSET lines")
    return errors


def _asset_errors(record: Record, registry: Registry, project_name: str) -> list[str]:
    """Require the clinician's header to carry precisely the registered assets."""
    expected = () if project_name == "none" else registry.projects[project_name].assets
    declared = record.values("ASSET")
    return ([f"missing ASSET from confirmed header: {asset}" for asset in expected if asset not in declared] +
            [f"unregistered ASSET in confirmed header: {asset}" for asset in declared if asset not in expected])


def _searches(record: Record) -> tuple[dict[str, str], list[str]]:
    searches: dict[str, str] = {}
    errors: list[str] = []
    for value in record.values("PROJECT-SEARCH"):
        parsed = _SEARCH.fullmatch(value)
        if parsed is None or not parsed.group(1).strip() or not parsed.group(2).strip():
            errors.append("PROJECT-SEARCH needs a place and quoted terms")
            continue
        target, terms = parsed.group(1).strip(), parsed.group(2).strip()
        if target in searches:
            errors.append(f"duplicate PROJECT-SEARCH for {target}")
        searches[target] = terms
    return searches, errors


def _waivers(record: Record) -> tuple[set[str], list[str]]:
    waivers: set[str] = set()
    errors: list[str] = []
    for value in record.values("PROJECT-WAIVE"):
        target, separator, reason = value.partition(" - ")
        if not separator or not target.strip() or not reason.strip():
            errors.append("PROJECT-WAIVE needs a place and substantive reason")
            continue
        waiver = _WAIVER.fullmatch(reason)
        valid_date = False
        if waiver is not None:
            try:
                date.fromisoformat(waiver.group("when"))
                valid_date = bool(re.search(r"[A-Za-z]", waiver.group("failure")))
            except ValueError:
                pass
        if not valid_date:
            errors.append(
                "PROJECT-WAIVE needs what failed, an ISO date, and "
                "'; proceed without, per the clinician'"
            )
        target = target.strip()
        if target in waivers:
            errors.append(f"duplicate PROJECT-WAIVE for {target}")
        waivers.add(target)
    return waivers, errors


def _owed_places(
    registry: Registry, project_name: str, searches: Mapping[str, str]
) -> tuple[OwedPlace, ...]:
    ordered: dict[str, OwedPlace] = {}
    if project_name != "none":
        project = registry.projects.get(project_name)
        if project is None:
            raise RegistryCoverage(
                "declared project is not registered; ask the clinician to register it or confirm none"
            )
        ordered.update({
            registry.memory_index: OwedPlace(registry.memory_index, "location"),
            **{path: OwedPlace(path, "location") for path in project.locations},
            **{service: OwedPlace(service, "service") for service in project.services},
        })
    for target, terms in searches.items():
        if _URL.match(target):
            raise RegistryFinding("a service route must be named, never written as a URL")
        kind = "location" if Path(target).expanduser().is_absolute() else "service"
        previous = ordered.get(target)
        ordered[target] = OwedPlace(target, previous.kind if previous else kind, terms)
    return tuple(ordered.values())


def _integer(entry: Entry, name: str, errors: list[str]) -> int | None:
    value = entry.value(name)
    try:
        number = int(value)
    except ValueError:
        errors.append(f"{entry.place}: {name} needs a nonnegative integer")
        return None
    if number < 0:
        errors.append(f"{entry.place}: {name} needs a nonnegative integer")
        return None
    return number


def recorded_opened_items(run: Path) -> tuple[str, ...]:
    """Identifiers of opened items, using the same parser as the context gate."""
    try:
        record = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
    except OSError:
        return ()
    return tuple(
        _opened(value).item
        for entry in record.entries
        if entry.value("STATE").casefold() in ("read", "searched")
        for value in entry.values("OPENED")
        if value.casefold() != "none"
    )


def _opened(value: str) -> Opened:
    match = _OPENED.fullmatch(value)
    return (
        Opened(match.group("item").strip(), match.group("digest").casefold())
        if match
        else Opened(value.strip())
    )


def _entry_errors(entry: Entry, owed: OwedPlace) -> list[str]:
    errors: list[str] = []
    state = entry.value("STATE").casefold()
    if state not in {"read", "searched", "unreadable", "absent"}:
        return [f"{entry.place}: STATE must be read, searched, unreadable, or absent"]
    if state in {"unreadable", "absent"}:
        if not entry.value("DETAIL"):
            errors.append(f"{entry.place}: {state} needs DETAIL")
        if entry.values("OPENED"):
            errors.append(f"{entry.place}: {state} cannot retain OPENED items")
        return errors
    opened = entry.values("OPENED")
    if not opened:
        errors.append(f"{entry.place}: OPENED is missing")
    if any(not value for value in opened):
        errors.append(f"{entry.place}: OPENED has an empty item")
    if owed.kind == "location":
        if entry.value("CORPUS-SIZE") or entry.values("QUERY"):
            errors.append(f"{entry.place}: service-only fields are not allowed")
        if state == "searched":
            for name in ("ROOT", "TERMS", "EXAMINED", "UNREADABLE"):
                if not entry.value(name):
                    errors.append(f"{entry.place}: {name} is missing")
            root = entry.value("ROOT")
            if root and not Path(root).expanduser().is_absolute():
                errors.append(f"{entry.place}: ROOT must be absolute")
            elif root and Path(root).expanduser().resolve() != Path(owed.place).expanduser().resolve():
                errors.append(f"{entry.place}: ROOT does not match the owed PLACE")
            _integer(entry, "EXAMINED", errors)
            _integer(entry, "UNREADABLE", errors)
            if owed.directed_terms is not None and entry.value("TERMS") != owed.directed_terms:
                errors.append(f"{entry.place}: TERMS do not match PROJECT-SEARCH")
    else:
        if any(entry.value(name) for name in ("ROOT", "TERMS", "EXAMINED", "UNREADABLE")):
            errors.append(f"{entry.place}: location-only fields are not allowed")
        if state != "searched":
            errors.append(f"{entry.place}: a readable service STATE must be searched")
        if not entry.value("CORPUS-SIZE"):
            errors.append(f"{entry.place}: CORPUS-SIZE is missing")
        else:
            _integer(entry, "CORPUS-SIZE", errors)
        queries = entry.values("QUERY")
        if not queries:
            errors.append(f"{entry.place}: QUERY is missing")
        parsed_terms: list[str] = []
        for query in queries:
            parsed = _QUERY.fullmatch(query)
            if parsed is None:
                errors.append(
                    f"{entry.place}: QUERY needs THRESHOLD, LIMIT, and HITS"
                )
            else:
                parsed_terms.append(parsed.group("terms").strip())
        if owed.directed_terms is not None and owed.directed_terms not in parsed_terms:
            errors.append(f"{entry.place}: QUERY does not match PROJECT-SEARCH")
    return errors


def _file_path(entry: Entry, opened: Opened) -> Path:
    item = Path(opened.item).expanduser()
    if not item.is_absolute():
        root = entry.value("ROOT") or entry.place
        item = Path(root).expanduser() / item
    return item.resolve()


def _hash_file(
    entry: Entry, owed: OwedPlace, opened: Opened
) -> tuple[str | None, str | None]:
    item = _file_path(entry, opened)
    owed_path = Path(owed.place).expanduser().resolve()
    within_owed = item.is_relative_to(owed_path) if owed_path.is_dir() else item == owed_path
    if not within_owed:
        return None, f"{entry.place}: OPENED item is outside owed PLACE"
    try:
        return sha256(item.read_bytes()).hexdigest(), None
    except (OSError, UnicodeError):
        return None, f"{entry.place}: an OPENED file could not be read"


def _hash_service(
    entry: Entry,
    opened: Opened,
    payloads: Mapping[str, Mapping[str, str | bytes]],
) -> tuple[str | None, str | None]:
    value = payloads.get(entry.place, {}).get(opened.item)
    if value is None:
        return None, f"{entry.place}: no returned text was supplied for {opened.item}"
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return sha256(payload).hexdigest(), None


def _context_digest(triples: list[tuple[str, str, str]], record: Record) -> str:
    payload = "".join(name + "\0" + record.value(name) + "\n"
                      for name in ("OWN-SUBMISSION", "CASE-MATERIAL", "CASE-RESEARCH"))
    payload += "".join(name + "\0" + value + "\n"
                       for name in (*CLASSMATE_FIELDS, "ASSET", "COURSE-HISTORY") for value in record.values(name))
    payload += "".join("\0".join(triple) + "\n" for triple in sorted(triples))
    return sha256(payload.encode("utf-8")).hexdigest()


def _render(
    record: Record,
    entries: tuple[Entry, ...],
    hashed: Mapping[str, tuple[Opened, ...]],
    digest: str,
) -> str:
    lines = [f"PROJECT-CONTEXT: {record.value('PROJECT-CONTEXT')}"]
    lines.extend(f"{name}: {record.value(name)}"
                 for name in ("OWN-SUBMISSION", "CASE-MATERIAL", "CASE-RESEARCH"))
    lines.extend(f"{name}: {value}" for name in CLASSMATE_FIELDS for value in record.values(name))
    lines.extend(f"COURSE-HISTORY: {value}" for value in record.values("COURSE-HISTORY"))
    lines.extend(f"ASSET: {value}" for value in record.values("ASSET"))
    lines.extend(f"PROJECT-SEARCH: {value}" for value in record.values("PROJECT-SEARCH"))
    lines.extend(f"PROJECT-WAIVE: {value}" for value in record.values("PROJECT-WAIVE"))
    lines.extend(f"ORDER-WAIVE: {value}" for value in record.values("ORDER-WAIVE"))
    lines.extend(f"ORDER-OBSERVATION: {value}" for value in record.values("ORDER-OBSERVATION"))
    lines.extend(f"GO-AHEAD: {value}" for value in record.values("GO-AHEAD"))
    lines.append(f"CONFIRMED: {record.value('CONFIRMED')}")
    lines.append(f"CONTEXT-DIGEST: {digest}")
    field_order = (
        "STATE",
        "ROOT",
        "TERMS",
        "EXAMINED",
        "UNREADABLE",
        "CORPUS-SIZE",
        "QUERY",
        "DETAIL",
        "MEMORY-LINES",
    )
    for entry in entries:
        lines.extend(("", f"## PLACE: {entry.place}"))
        for name in field_order:
            lines.extend(f"{name}: {value}" for value in entry.values(name))
        for opened in hashed.get(entry.place, ()):
            if opened.item == "none":
                lines.append("OPENED: none")
            else:
                lines.append(f"OPENED: {opened.item} | SHA256: {opened.digest}")
    return "\n".join(lines) + "\n"


def _write_context_record(
    run: Path,
    *,
    service_payloads: Mapping[str, Mapping[str, str | bytes]] | None = None,
    submission: str | None = None,
) -> GateResult:
    """Validate retrieval, write hashes and the context digest, and report the gate."""
    retain_heading_context(run)
    record_path = run / RECORD_NAME
    if not record_path.is_file():
        return GateResult(1, "project context: finding - record is missing")
    try:
        record = read_record(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return GateResult(1, "project context: finding - record shape is invalid")
    errors = _duplicates(record)
    errors.extend(_context_declaration_errors(record))
    classmate_errors, classmate_report = _classmate_gate(record, submission)
    errors.extend(classmate_errors)
    history_errors, history_report = _course_history_gate(record)
    errors.extend(history_errors)
    retrieval_report = "; ".join(filter(None, (classmate_report, history_report)))
    project_name, declaration_error = _declaration(record)
    if declaration_error:
        errors.append(declaration_error)
    confirmed = record.values("CONFIRMED")
    if len(confirmed) != 1:
        errors.append("CONFIRMED is missing or duplicated")
    elif error := _confirmation_error(confirmed[0]):
        errors.append(error)
    searches, search_errors = _searches(record)
    waivers, waiver_errors = _waivers(record)
    errors.extend(search_errors)
    errors.extend(waiver_errors)
    if errors:
        return GateResult(1, "project context: finding - " + "; ".join(errors))
    assert project_name is not None
    if project_name == "none" and not _has_declared_retrieval(record):
        if searches or waivers or record.entries:
            return GateResult(1, "project context: finding - a none run cannot owe places")
        digest = _context_digest([], record)
        record_path.write_text(_render(record, (), {}, digest), encoding="utf-8")
        return GateResult(0, "; ".join(filter(None, ("project context: clean; waived places: 0", retrieval_report))), digest=digest)

    registry_path = repo_root.project_registry()
    if project_name != "none" and not registry_path.is_file():
        return GateResult(2, "project context NOT SCANNED - project registry is unavailable")
    try:
        registry = Registry("", MappingProxyType({})) if project_name == "none" else read_registry(registry_path.read_text(encoding="utf-8"))
        owed = _owed_places(registry, project_name, searches)
    except RegistryCoverage as failure:
        return GateResult(2, f"project context NOT SCANNED - {failure}")
    except (OSError, UnicodeError):
        return GateResult(2, "project context NOT SCANNED - project registry is unreadable")
    except RegistryFinding as failure:
        return GateResult(1, f"project context: finding - {failure}")

    if errors := _asset_errors(record, registry, project_name):
        return GateResult(1, "project context: finding - " + "; ".join(errors))

    by_place: dict[str, list[Entry]] = {}
    for entry in record.entries:
        by_place.setdefault(entry.place, []).append(entry)
    owed_names = {item.place for item in owed}
    errors = [f"unexpected PLACE {name}" for name in by_place if name not in owed_names]
    entries: list[Entry] = []
    for item in owed:
        matches = by_place.get(item.place, [])
        if len(matches) != 1:
            errors.append(
                f"{item.place}: expected one owed PLACE entry, found {len(matches)}"
            )
            continue
        entry = matches[0]
        entries.append(entry)
        errors.extend(_entry_errors(entry, item))
    if waivers - owed_names:
        errors.append("PROJECT-WAIVE names a place that is not owed")
    failed_places = {
        item.place
        for item, entry in zip(owed, entries)
        if entry.value("STATE").casefold() in {"unreadable", "absent"}
    }
    if waivers - failed_places:
        errors.append("PROJECT-WAIVE must name an unreadable or absent place")
    if errors:
        return GateResult(1, "project context: finding - " + "; ".join(errors))

    payloads = service_payloads or {}
    triples: list[tuple[str, str, str]] = []
    hashed: dict[str, tuple[Opened, ...]] = {}
    waived = 0
    for entry_index, (item, entry) in enumerate(zip(owed, entries)):
        state = entry.value("STATE").casefold()
        if state in {"unreadable", "absent"}:
            if item.place not in waivers:
                errors.append(f"{item.place}: {state} is not waived")
            else:
                waived += 1
            hashed[item.place] = ()
            continue
        opened_rows: list[Opened] = []
        for value in entry.values("OPENED"):
            opened = _opened(value)
            if opened.item.casefold() == "none":
                opened_rows.append(Opened("none"))
                continue
            digest, error = (
                _hash_file(entry, item, opened)
                if item.kind == "location"
                else _hash_service(entry, opened, payloads)
            )
            if error:
                errors.append(error)
                continue
            assert digest is not None
            if item.place == registry.memory_index:
                try:
                    hashes = [sha256(line.encode("utf-8")).hexdigest()
                              for line in _memory_lines(entry, opened)]
                except (OSError, UnicodeError):
                    errors.append(f"{item.place}: memory index could not be read")
                    continue
                fields = dict(entry.fields)
                fields["MEMORY-LINES"] = (json.dumps(hashes),)
                entry = replace(entry, fields=fields)
                entries[entry_index] = entry
            opened_rows.append(Opened(opened.item, digest))
            triples.append((item.place, opened.item, digest))
        hashed[item.place] = tuple(opened_rows)
    if errors:
        return GateResult(1, "project context: finding - " + "; ".join(errors))
    digest = _context_digest(triples, record)
    record_path.write_text(_render(record, tuple(entries), hashed, digest), encoding="utf-8")
    return GateResult(
        0,
        "; ".join(filter(None, (f"project context: clean; owed places: {len(owed)}; waived places: {waived}", retrieval_report))),
        waived=waived,
        digest=digest,
    )


def order_observations(run: Path) -> dict:
    """Read only the project record's machine observations."""
    record = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
    observations = {}
    for value in record.values("ORDER-OBSERVATION"):
        row = json.loads(value)
        coursework_run.validate_observations(row)
        if observations.keys() & row.keys():
            raise ValueError("duplicate draft observation")
        observations.update(row)
    return observations


def order_waived(run: Path, submission: str, draft_path: str) -> bool:
    """Answer the cross-record waiver question without exposing record parsing."""
    try:
        record = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
        if _duplicates(record) or len(record.values("CONFIRMED")) != 1 or _confirmation_error(record.value("CONFIRMED")):
            return False
        coursework_run.submission_keys(submission)
        for value in record.values("ORDER-WAIVE"):
            match = re.fullmatch(r"(.+?) - (.+?); proceed, per the clinician", value)
            if match and match[2].strip() and Path(match[1]).is_absolute() and Path(match[1]).resolve() == Path(draft_path).resolve():
                return True
    except (OSError, UnicodeError, ValueError):
        pass
    return False


def _damaged_lines(path: Path) -> list[str]:
    # Unlike tracker-body #723, tabs and bare CR are damage: Windows path
    # escapes can produce them. Only LF and CR immediately before LF are safe.
    with path.open(encoding="utf-8", newline="") as source:
        text = source.read()
    findings = []
    lines = text.split("\n")
    for number, line in enumerate(lines, 1):
        for offset, character in enumerate(line):
            if ord(character) >= 32:
                continue
            if character == "\r" and offset == len(line) - 1 and number < len(lines):
                continue
            findings.append(f"{path}: line {number}: U+{ord(character):04X} ({ascii(character)})")
    return findings


def _write_damage(run: Path) -> GateResult | None:
    path = run / RECORD_NAME
    if not path.is_file():
        return None
    findings = _damaged_lines(path)
    if not findings:
        record = read_record(path.read_text(encoding="utf-8"))
        project, _ = _declaration(record)
        if project is not None and project != "none":
            registry = repo_root.project_registry()
            if registry.is_file():
                findings = _damaged_lines(registry)
    if not findings:
        return None
    return GateResult(1, "project context: finding - damaged text\n" + "\n".join(findings) +
        "\nRewrite using AGENTS.md standing rule 6: the Write tool in a private staging "
        "folder, then one copy, rename, and read-back; never a shell heredoc. Use spaces for tabs.")


def write_record(run: Path, *, service_payloads=None, submission: str | None = None) -> GateResult:
    """Refresh retrieval and retain each sitting's first draft observation."""
    damage = _write_damage(run)
    if damage is not None:
        return damage
    if submission is not None:
        keys = coursework_run.submission_keys(submission)
        if len(keys) != 1:
            raise ValueError("write one submission observation at a time")
        observations = coursework_run.observe_draft(run, keys[0], order_observations(run))
        path = run / RECORD_NAME
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if not line.startswith("ORDER-OBSERVATION:")]
        lines.insert(0, "ORDER-OBSERVATION: " + json.dumps(observations))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = _write_context_record(run, service_payloads=service_payloads, submission=submission)
    if result.exit_code == 0:
        retain_heading_context(run)
    if submission is None:
        return result
    order = coursework_run.grade_order(order_observations(run), submission, lambda key, path: order_waived(run, key, path))
    return replace(result, exit_code=1 if order.finding else result.exit_code, report=result.report + "; " + order.report)


def completion_gate(run: Path, submission: str | None) -> CompletionGate:
    frozen = completion_checks.exemption(run, submission, "project_context", EXPECTED_ROW)
    if frozen is not None:
        return CompletionGate(False, False, frozen)
    if submission is None:
        return _context_completion_gate(run, submission)
    import approval_record
    try:
        rows = []
        for key in coursework_run.submission_keys(submission):
            state = approval_record.project_context_posting(run, key)
            if not state.posted:
                rows.append(_context_completion_gate(run, key))
                continue
            records = _go_ahead_records(run)
            row = records.get(key)
            if row is None:
                if state.check_required:
                    rows.append(CompletionGate(True, False, f"{EXPECTED_ROW}: finding - {key} go-ahead result is missing"))
                else:
                    rows.append(CompletionGate(False, False, f"{EXPECTED_ROW}: {key} not checked at the go-ahead because approval predates the check; pre-check approvals: 1"))
                continue
            if row.get("approval_revision") != state.approval_revision:
                rows.append(CompletionGate(True, False, f"{EXPECTED_ROW}: finding - go-ahead approval revision differs for {key}"))
                continue
            rows.append(CompletionGate(
                row["finding"],
                row["coverage"] and not row["moved_places"],
                row["report"] + ("; clinician approved over moved places" if row["moved_places"] else "; carried forward from go-ahead"),
            ))
        result = CompletionGate(any(row.finding for row in rows), any(row.coverage for row in rows), "; ".join(row.report for row in rows))
    except (OSError, UnicodeError, ValueError):
        result = CompletionGate(True, False, f"{EXPECTED_ROW}: finding - go-ahead or posting record is unreadable")
    if submission is None:
        return result
    try:
        observations = order_observations(run)
    except (OSError, UnicodeError, ValueError):
        observations = None
    order = coursework_run.grade_order(observations, submission, lambda key, path: order_waived(run, key, path), run=run)
    return replace(result, finding=result.finding or order.finding, report=result.report + "; " + order.report)


def recorded_digest(run: Path) -> str:
    """Return the machine-written digest for the shared heading-read binding."""
    try:
        return read_record((run / RECORD_NAME).read_text(encoding="utf-8")).value(
            "CONTEXT-DIGEST"
        )
    except (OSError, UnicodeError, ValueError):
        return ""


def retain_heading_context(run: Path) -> None:
    """Keep each context the heading reader can name, before a later refresh."""
    try:
        text = (run / RECORD_NAME).read_text(encoding="utf-8")
        digest = read_record(text).value("CONTEXT-DIGEST")
    except (OSError, UnicodeError, ValueError):
        return
    if _SHA256.fullmatch(digest):
        directory = run / "private" / "heading-contexts"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (digest + ".md")
        if not path.exists():
            path.write_text(text, encoding="utf-8")


def heading_context_matches(run: Path, digest: str, artifact: str) -> bool:
    """Compare the read's items; memory additions leave old line hashes intact."""
    import frozen_grade
    approval = frozen_grade.approved(run, artifact) or frozen_grade.approved(run, Path(artifact).stem)
    if approval is not None:
        _skill, item = approval
        if item.get("posting_route", item.get("upload_route")) in {"agent", "clinician"}:
            return True
    if digest == "none":
        return recorded_digest(run) == "none"
    if not _SHA256.fullmatch(digest):
        return False
    try:
        path = run / "private" / "heading-contexts" / (digest + ".md")
        # An unchanged legacy record can supply its own retained population.
        if not path.is_file() and digest == recorded_digest(run):
            retain_heading_context(run)
        previous = read_record(path.read_text(encoding="utf-8"))
        current = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
        names = ("OWN-SUBMISSION", "CASE-MATERIAL", "CASE-RESEARCH", *CLASSMATE_FIELDS, "ASSET", "COURSE-HISTORY")
        if _declaration(previous)[0] != _declaration(current)[0]:
            return False
        if any(previous.values(name) != current.values(name) for name in names):
            return False
        def population(record):
            return {(entry.place, opened.item): (entry, opened)
                    for entry in record.entries for value in entry.values("OPENED")
                    for opened in (_opened(value),) if opened.item != "none"}
        before, after = population(previous), population(current)
        if before.keys() != after.keys() or {e.place for e in previous.entries} != {e.place for e in current.entries}:
            return False
        for key, (entry, opened) in before.items():
            new_entry, new_opened = after[key]
            stored_lines = entry.value("MEMORY-LINES")
            if stored_lines:
                stored = json.loads(stored_lines)
                hashes = [sha256(line.encode("utf-8")).hexdigest() for line in _memory_lines(entry, opened)]
                if Counter(stored) - Counter(hashes):
                    return False
            elif opened.digest != new_opened.digest:
                return False
            elif entry.value("ROOT") or Path(entry.place).exists():
                if sha256(_file_path(entry, opened).read_bytes()).hexdigest() != opened.digest:
                    return False
        return True
    except (OSError, UnicodeError, ValueError, TypeError):
        return False


def _context_completion_gate(run: Path, submission: str | None, *, recheck_files: bool = True, compare_memory_lines: bool = False) -> CompletionGate:
    """Grade record shape, fingerprint integrity, and current file identities."""
    if submission is None:
        return CompletionGate(
            False,
            False,
            f"{EXPECTED_ROW}: not graded - --submission was not supplied",
        )
    path = run / RECORD_NAME
    if not path.is_file():
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record is missing")
    try:
        record = read_record(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record shape is invalid")
    digest = record.value("CONTEXT-DIGEST")
    declaration, error = _declaration(record)
    shape_errors = _duplicates(record)
    shape_errors.extend(_context_declaration_errors(record, recheck_files=recheck_files))
    classmate_errors, classmate_report = _classmate_gate(record, submission)
    shape_errors.extend(classmate_errors)
    history_errors, history_report = _course_history_gate(record)
    shape_errors.extend(history_errors)
    retrieval_report = "; ".join(filter(None, (classmate_report, history_report)))
    confirmed = record.values("CONFIRMED")
    if error:
        shape_errors.append(error)
    if len(confirmed) != 1:
        shape_errors.append("CONFIRMED is missing or duplicated")
    elif confirmation_error := _confirmation_error(confirmed[0]):
        shape_errors.append(confirmation_error)
    searches, search_errors = _searches(record)
    waivers, waiver_errors = _waivers(record)
    shape_errors.extend(search_errors)
    shape_errors.extend(waiver_errors)
    if shape_errors:
        return CompletionGate(True, False, "; ".join(filter(None, (f"{EXPECTED_ROW}: finding - record shape is invalid", retrieval_report))))
    if declaration == "none" and not _has_declared_retrieval(record):
        clean = digest == _context_digest([], record) and not record.entries
        return CompletionGate(
            not clean,
            False,
            "; ".join(filter(None, (f"{EXPECTED_ROW}: {'clean' if clean else 'finding - record fingerprint is invalid'}", retrieval_report))),
        )
    assert declaration is not None
    registry_path = repo_root.project_registry()
    if declaration != "none" and not registry_path.is_file():
        return CompletionGate(
            False,
            True,
            f"{EXPECTED_ROW}: not scanned - project registry is unavailable",
        )
    try:
        registry = Registry("", MappingProxyType({})) if declaration == "none" else read_registry(registry_path.read_text(encoding="utf-8"))
        owed = _owed_places(registry, declaration, searches)
    except RegistryCoverage:
        return CompletionGate(
            False,
            True,
            f"{EXPECTED_ROW}: not scanned - declared project is not registered",
        )
    except (OSError, UnicodeError):
        return CompletionGate(
            False,
            True,
            f"{EXPECTED_ROW}: not scanned - project registry is unreadable",
        )
    except RegistryFinding:
        return CompletionGate(
            True,
            False,
            f"{EXPECTED_ROW}: finding - project registry shape is invalid",
        )
    shape_errors.extend(_asset_errors(record, registry, declaration))
    by_place: dict[str, list[Entry]] = {}
    for entry in record.entries:
        by_place.setdefault(entry.place, []).append(entry)
    owed_names = {item.place for item in owed}
    shape_errors.extend(
        f"unexpected PLACE {name}" for name in by_place if name not in owed_names
    )
    owed_entries: list[tuple[OwedPlace, Entry]] = []
    failed_places: set[str] = set()
    for item in owed:
        matches = by_place.get(item.place, [])
        if len(matches) != 1:
            shape_errors.append(
                f"{item.place}: expected one owed PLACE entry, found {len(matches)}"
            )
            continue
        entry = matches[0]
        owed_entries.append((item, entry))
        shape_errors.extend(_entry_errors(entry, item))
        if (
            entry.value("STATE").casefold() in {"unreadable", "absent"}
            and item.place not in waivers
        ):
            shape_errors.append(f"{item.place}: failed place is not waived")
        if entry.value("STATE").casefold() in {"unreadable", "absent"}:
            failed_places.add(item.place)
    if waivers - owed_names:
        shape_errors.append("PROJECT-WAIVE names a place that is not owed")
    if waivers - failed_places:
        shape_errors.append("PROJECT-WAIVE must name an unreadable or absent place")
    triples: list[tuple[str, str, str]] = []
    moved = False
    moved_places: list[str] = []
    added_lines: list[str] = []
    malformed = not bool(_SHA256.fullmatch(digest))
    for item, entry in owed_entries:
        for value in entry.values("OPENED"):
            opened = _opened(value)
            if opened.item.casefold() == "none":
                continue
            if opened.digest is None:
                malformed = True
                continue
            triples.append((entry.place, opened.item, opened.digest))
            if item.kind == "service" or not recheck_files:
                continue
            current, file_error = _hash_file(entry, item, opened)
            if file_error and "outside owed PLACE" in file_error:
                shape_errors.append(file_error)
            changed = current != opened.digest
            if (not compare_memory_lines and not changed and not file_error
                    and item.place == registry.memory_index and entry.values("MEMORY-LINES")):
                # ADR 0391 ruling 8: an edit inside a subject list leaves MEMORY.md's
                # bytes alone, so the whole-file recheck also compares the line population.
                try:
                    stored = json.loads(entry.value("MEMORY-LINES"))
                    current_lines = [sha256(line.encode("utf-8")).hexdigest() for line in _memory_lines(entry, opened)]
                    changed = bool(Counter(stored) - Counter(current_lines))
                except (OSError, UnicodeError, ValueError, TypeError):
                    shape_errors.append("memory line fingerprints are unreadable")
            if compare_memory_lines and not file_error and item.place == registry.memory_index and entry.values("MEMORY-LINES"):
                try:
                    stored = json.loads(entry.value("MEMORY-LINES"))
                    if not isinstance(stored, list) or any(not isinstance(value, str) or not _SHA256.fullmatch(value) for value in stored):
                        raise ValueError("invalid memory line fingerprints")
                    lines = _memory_lines(entry, opened)
                    hashes = [sha256(line.encode("utf-8")).hexdigest() for line in lines]
                    changed = bool(Counter(stored) - Counter(hashes))
                    additions = Counter(hashes) - Counter(stored)
                    for line, fingerprint in zip(lines, hashes):
                        if additions[fingerprint]:
                            added_lines.append(line)
                            additions[fingerprint] -= 1
                except (OSError, UnicodeError, ValueError):
                    shape_errors.append("memory line fingerprints are unreadable")
            if file_error or changed:
                moved = True
                moved_places.append(f"{entry.place}: {opened.item}")
    if not malformed and _context_digest(triples, record) != digest:
        malformed = True
    states: list[str] = []
    if shape_errors:
        states.append("finding - record shape is invalid")
    if malformed:
        states.append("finding - record fingerprint is invalid")
    if moved:
        states.append("not scanned - file item moved: " + ", ".join(moved_places))
    if added_lines:
        states.append("added memory-index lines (not graded):\n" + "\n".join(added_lines))
    return CompletionGate(
        bool(shape_errors) or malformed,
        moved,
        f"{EXPECTED_ROW}: "
        + ("; ".join(states) if states else "clean")
        + f"; owed places: {len(owed)}; waived places: {len(waivers & failed_places)}"
        + (f"; {retrieval_report}" if retrieval_report else ""),
        tuple(moved_places),
        tuple(added_lines),
    )


def _memory_lines(entry: Entry, opened: Opened) -> list[str]:
    """The memory index and every subject list, read as one index (ADR 0391 ruling 8)."""
    return memory_index.index_lines(_file_path(entry, opened))


def _go_ahead_records(run: Path) -> dict[str, dict]:
    record = read_record((run / RECORD_NAME).read_text(encoding="utf-8"))
    rows = {}
    for value in record.values("GO-AHEAD"):
        row = json.loads(value)
        if not isinstance(row, dict):
            raise ValueError("invalid go-ahead result")
        key = row.get("submission")
        if not isinstance(key, str) or len(coursework_run.submission_keys(key)) != 1 or key in rows:
            raise ValueError("duplicate or invalid go-ahead key")
        if (not isinstance(row.get("report"), str)
                or not isinstance(row.get("digest"), str)
                or any(type(row.get(name)) is not bool for name in ("finding", "coverage"))
                or any(not isinstance(row.get(name), list) or any(not isinstance(value, str) for value in row[name]) for name in ("moved_places", "added_lines"))):
            raise ValueError("invalid go-ahead result fields")
        revision = row.get("approval_revision")
        if revision is not None and (type(revision) is not int or revision < 1):
            raise ValueError("invalid go-ahead approval revision")
        rows[key] = row
    return rows


def inspect_go_ahead(run: Path, submission: str) -> CompletionGate:
    """Show the live notice before approval without replacing approval evidence."""
    if len(coursework_run.submission_keys(submission)) != 1:
        raise ValueError("check one go-ahead at a time")
    return _context_completion_gate(run, submission, compare_memory_lines=True)


def go_ahead(run: Path, submission: str, *, approval_revision: int | None = None) -> CompletionGate:
    """Recheck opened files and replace this key's machine-written go-ahead result."""
    keys = coursework_run.submission_keys(submission)
    if len(keys) != 1:
        raise ValueError("check one go-ahead at a time")
    import approval_record
    state = approval_record.project_context_posting(run, submission)
    if state.posted and (approval_revision is None or approval_revision <= (state.approval_revision or 0)):
        raise ValueError("a posted go-ahead result requires a new approval revision")
    result = inspect_go_ahead(run, submission)
    rows = _go_ahead_records(run)
    rows[submission] = dict(submission=submission, digest=recorded_digest(run),
                            finding=result.finding, coverage=result.coverage,
                            report=result.report, moved_places=list(result.moved_places),
                            added_lines=list(result.added_lines), approval_revision=approval_revision)
    path = run / RECORD_NAME
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("GO-AHEAD:")]
    position = next((index for index, line in enumerate(lines) if line.startswith("## PLACE:")), len(lines))
    lines[position:position] = ["GO-AHEAD: " + json.dumps(row) for row in rows.values()]
    partial = path.with_name(path.name + ".building")
    try:
        partial.write_text("\n".join(lines) + "\n", encoding="utf-8")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
    return result


def apply_completion_gate(
    grade: run_grader.Grade[TScan],
    run: Path,
    submission: str | None,
    *,
    coverage_limb: str | None = None,
) -> run_grader.Grade[TScan]:
    """Add the shared completion row to an already computed grade."""
    project = completion_gate(run, submission)
    limbs = grade.coverage_limbs
    if project.coverage and coverage_limb is not None:
        limbs += (coverage_limb,)
    return replace(
        grade,
        findings_failed=grade.findings_failed or project.finding,
        coverage_failed=grade.coverage_failed or project.coverage,
        coverage_limbs=limbs,
        reports=grade.reports + (project.report,),
    )


def _service_payloads(arguments: list[str]) -> Mapping[str, Mapping[str, str]]:
    if not arguments:
        return {}
    if arguments != ["--service-payloads", "-"]:
        raise ValueError("only --service-payloads - is supported")
    payload = json.loads(sys.stdin.read())
    if not isinstance(payload, dict) or any(
        not isinstance(place, str)
        or not isinstance(items, dict)
        or any(not isinstance(item, str) or not isinstance(text, str) for item, text in items.items())
        for place, items in payload.items()
    ):
        raise ValueError("service payloads need a place -> item -> text object")
    return payload


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--go-ahead":
        try:
            result = inspect_go_ahead(Path(argv[0]).expanduser().resolve(), argv[2])
        except (OSError, UnicodeError, ValueError):
            print("project context NOT WRITTEN - go-ahead result is unreadable", file=sys.stderr)
            return 2
        print(result.report)
        return 1 if result.finding else 2 if result.coverage else 0
    if len(argv) < 2 or argv[1] != "--write":
        print(
            "usage: python tools/project_context.py <run-directory> --write "
            "--submission <key> [--service-payloads -]",
            file=sys.stderr,
        )
        return 2
    run = Path(argv[0]).expanduser().resolve()
    if not run.is_dir():
        print(f"project context NOT WRITTEN - no run directory at {run}", file=sys.stderr)
        return 2
    try:
        arguments = argv[2:]
        if len(arguments) < 2 or arguments[0] != "--submission":
            raise ValueError("--submission is required")
        submission = arguments[1]
        payloads = _service_payloads(arguments[2:])
        result = write_record(run, service_payloads=payloads, submission=submission)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        print("project context NOT WRITTEN - submission or record input is unreadable", file=sys.stderr)
        return 2
    stream = sys.stdout if result.exit_code == 0 else sys.stderr
    print(result.report, file=stream)
    return result.exit_code


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
