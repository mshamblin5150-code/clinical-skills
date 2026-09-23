#!/usr/bin/env python3
"""Write and grade the confirmed project-context retrieval record. #1395.

``DECLARED_LIMITS`` is the complete ceiling of a clean project-context row.
Scoped graders and ``CLAUDE.md`` name this object and copy no row.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, replace
from datetime import date
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, TypeVar

import aar_scan
import repo_root
import run_grader
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
DECLARED_LIMITS = (
    (
        "retrieval-before-draft-unobservable",
        "The record cannot prove that retrieval finished before the first draft prose was written.",
    ),
    (
        "agreement-is-a-reading",
        "A clean shape cannot establish that an agrees verdict is substantively true.",
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
    {"PROJECT-CONTEXT", "PROJECT-SEARCH", "PROJECT-WAIVE", "CONFIRMED", "CONTEXT-DIGEST"}
)
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
    }
)
_REPEATABLE_HEADER = frozenset({"PROJECT-SEARCH", "PROJECT-WAIVE"})
_REPEATABLE_ENTRY = frozenset({"QUERY", "OPENED"})
TScan = TypeVar("TScan")


@dataclass(frozen=True)
class Project:
    name: str
    locations: tuple[str, ...]
    services: tuple[str, ...]


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

    def close_project() -> None:
        nonlocal current_name, current_locations, current_services
        if current_name is None:
            return
        if current_name in projects:
            raise RegistryFinding("duplicate PROJECT entry")
        projects[current_name] = Project(
            current_name, tuple(current_locations), tuple(current_services)
        )
        current_name, current_locations, current_services = None, [], []

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
    try:
        date.fromisoformat(value)
    except ValueError:
        return "CONFIRMED needs an ISO date"
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
    project = registry.projects.get(project_name)
    if project is None:
        raise RegistryCoverage(
            "declared project is not registered; ask the clinician to register it or confirm none"
        )
    ordered: dict[str, OwedPlace] = {
        registry.memory_index: OwedPlace(registry.memory_index, "location"),
        **{path: OwedPlace(path, "location") for path in project.locations},
        **{service: OwedPlace(service, "service") for service in project.services},
    }
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


def _hash_file(
    entry: Entry, owed: OwedPlace, opened: Opened
) -> tuple[str | None, str | None]:
    item = Path(opened.item).expanduser()
    if not item.is_absolute():
        root = entry.value("ROOT") or entry.place
        item = Path(root).expanduser() / item
    item = item.resolve()
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


def _context_digest(triples: list[tuple[str, str, str]]) -> str:
    payload = "".join("\0".join(triple) + "\n" for triple in sorted(triples))
    return sha256(payload.encode("utf-8")).hexdigest()


def _render(
    record: Record,
    entries: tuple[Entry, ...],
    hashed: Mapping[str, tuple[Opened, ...]],
    digest: str,
) -> str:
    lines = [f"PROJECT-CONTEXT: {record.value('PROJECT-CONTEXT')}"]
    lines.extend(f"PROJECT-SEARCH: {value}" for value in record.values("PROJECT-SEARCH"))
    lines.extend(f"PROJECT-WAIVE: {value}" for value in record.values("PROJECT-WAIVE"))
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


def write_record(
    run: Path,
    *,
    service_payloads: Mapping[str, Mapping[str, str | bytes]] | None = None,
) -> GateResult:
    """Validate retrieval, write hashes and the context digest, and report the gate."""
    record_path = run / RECORD_NAME
    if not record_path.is_file():
        return GateResult(1, "project context: finding - record is missing")
    try:
        record = read_record(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return GateResult(1, "project context: finding - record shape is invalid")
    errors = _duplicates(record)
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
    if project_name == "none":
        if searches or waivers or record.entries:
            return GateResult(1, "project context: finding - a none run cannot owe places")
        record_path.write_text(_render(record, (), {}, "none"), encoding="utf-8")
        return GateResult(0, "project context: clean; waived places: 0", digest="none")

    registry_path = repo_root.project_registry()
    if not registry_path.is_file():
        return GateResult(2, "project context NOT SCANNED - project registry is unavailable")
    try:
        registry = read_registry(registry_path.read_text(encoding="utf-8"))
        owed = _owed_places(registry, project_name, searches)
    except RegistryCoverage as failure:
        return GateResult(2, f"project context NOT SCANNED - {failure}")
    except (OSError, UnicodeError):
        return GateResult(2, "project context NOT SCANNED - project registry is unreadable")
    except RegistryFinding as failure:
        return GateResult(1, f"project context: finding - {failure}")

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
    for item, entry in zip(owed, entries):
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
            opened_rows.append(Opened(opened.item, digest))
            triples.append((item.place, opened.item, digest))
        hashed[item.place] = tuple(opened_rows)
    if errors:
        return GateResult(1, "project context: finding - " + "; ".join(errors))
    digest = _context_digest(triples)
    record_path.write_text(_render(record, tuple(entries), hashed, digest), encoding="utf-8")
    return GateResult(
        0,
        f"project context: clean; owed places: {len(owed)}; waived places: {waived}",
        waived=waived,
        digest=digest,
    )


def recorded_digest(run: Path) -> str:
    """Return the machine-written digest for the shared heading-read binding."""
    try:
        return read_record((run / RECORD_NAME).read_text(encoding="utf-8")).value(
            "CONTEXT-DIGEST"
        )
    except (OSError, UnicodeError, ValueError):
        return ""


def completion_gate(run: Path, submission: str | None) -> CompletionGate:
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
        return CompletionGate(True, False, f"{EXPECTED_ROW}: finding - record shape is invalid")
    if declaration == "none":
        clean = digest == "none" and not record.entries
        return CompletionGate(
            not clean,
            False,
            f"{EXPECTED_ROW}: {'clean' if clean else 'finding - record fingerprint is invalid'}",
        )
    assert declaration is not None
    registry_path = repo_root.project_registry()
    if not registry_path.is_file():
        return CompletionGate(
            False,
            True,
            f"{EXPECTED_ROW}: not scanned - project registry is unavailable",
        )
    try:
        registry = read_registry(registry_path.read_text(encoding="utf-8"))
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
            if item.kind == "service":
                continue
            current, file_error = _hash_file(entry, item, opened)
            if file_error and "outside owed PLACE" in file_error:
                shape_errors.append(file_error)
            if file_error or current != opened.digest:
                moved = True
    if not malformed and _context_digest(triples) != digest:
        malformed = True
    states: list[str] = []
    if shape_errors:
        states.append("finding - record shape is invalid")
    if malformed:
        states.append("finding - record fingerprint is invalid")
    if moved:
        states.append("not scanned - file item moved")
    return CompletionGate(
        bool(shape_errors) or malformed,
        moved,
        f"{EXPECTED_ROW}: "
        + ("; ".join(states) if states else "clean")
        + f"; owed places: {len(owed)}; waived places: {len(waivers & failed_places)}",
    )


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
    if len(argv) < 2 or argv[1] != "--write":
        print(
            "usage: python tools/project_context.py <run-directory> --write "
            "[--service-payloads -]",
            file=sys.stderr,
        )
        return 2
    run = Path(argv[0]).expanduser().resolve()
    if not run.is_dir():
        print(f"project context NOT WRITTEN - no run directory at {run}", file=sys.stderr)
        return 2
    try:
        payloads = _service_payloads(argv[2:])
        result = write_record(run, service_payloads=payloads)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        print("project context NOT WRITTEN - service input is unreadable", file=sys.stderr)
        return 2
    stream = sys.stdout if result.exit_code == 0 else sys.stderr
    print(result.report, file=stream)
    return result.exit_code


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
