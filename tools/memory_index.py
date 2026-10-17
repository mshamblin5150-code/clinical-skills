#!/usr/bin/env python3
"""Survey or rebuild the Claude Code memory index and its subject lists.

    python tools/memory_index.py <MEMORY.md> [--write [--install-rule]] [--show]

ADR 0391. ``MEMORY.md`` keeps flat lines for memories that apply in every session
and one line per subject; each subject line points to ``subjects/<subject>.md``. Each
memory file declares its placement in its own header. The filing rule and the fixed
subject table live in ``docs/agents/memory.md``; this docstring does not restate them.

Without ``--write`` the command reads and reports. ``--write`` rebuilds every
subject list and the flat part of ``MEMORY.md`` from the memory files' own headers
and descriptions, and refreshes the installed rule block when it is present;
``--install-rule`` also inserts that block. A memory with no ``subjects`` header
keeps its existing flat line verbatim, and every line that does not link a memory
file is kept as written.

The population is every top-level ``*.md`` beside the index other than the index
itself, derived from the directory rather than from the index's links. A memory is
unplaced when it reaches no index, when its header names a subject off the fixed
list, or when it needs a generated line and has no description. A header that
cannot be read is counted on its own line and is unplaced only when its memory
reaches no index. Exit 0 means no memory is unplaced, 1 means at least one is,
and 2 means the index, its directory, its rule block markers, or the tracked rule
could not be read. Counts print by default; ``--show`` names the files behind them.

The complete boundary is ``DECLARED_LIMITS``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Literal, Mapping

from console_codec import require_python_floor, use_utf8


RULE_SOURCE = Path(__file__).resolve().parent.parent / "docs" / "agents" / "memory.md"
BLOCK_START = (
    "<!-- memory-index rule: installed from docs/agents/memory.md by "
    "tools/memory_index.py; edit there -->"
)
BLOCK_END = "<!-- end memory-index rule -->"
SUBJECTS_DIR = "subjects"
SEPARATOR = " — "
# ECMAScript WhiteSpace and LineTerminator characters used by String.trim(), built
# from code points so the source holds no invisible character.
JS_TRIM_WHITESPACE = "".join(map(chr, (
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680, 0x2000, 0x2001, 0x2002, 0x2003,
    0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200A, 0x2028, 0x2029, 0x202F,
    0x205F, 0x3000, 0xFEFF,
)))

DECLARED_LIMITS = (
    (
        "whether a session opens a list",
        "A placed memory is reachable from MEMORY.md; whether a session opens the subject list "
        "its task needed is outside this command and is answered after a miss by ADR 0391 ruling 6.",
    ),
    (
        "description quality",
        "Lines repeat each file's own description; a poor description is a poor line wherever it lands.",
    ),
    (
        "header grammar",
        "Only a leading '---' frontmatter block with top-level 'key: value' lines and an indented "
        "'metadata:' map is read; other YAML forms are an unreadable header.",
    ),
    (
        "rule source",
        "The rule and subject table are read from the checkout running the command, not from the "
        "owning checkout.",
    ),
    (
        "other files in subjects/",
        "Files in subjects/ that no table subject names are read as index lines and never rewritten.",
    ),
    (
        "an index in a shared folder",
        "The population is every top-level Markdown file beside the index, so an index kept in a "
        "folder with other documents reads them as memories.",
    ),
    (
        "a refresh rebuilds the whole index",
        "The rule block is refreshed only by --write, which also rebuilds every list and flat line.",
    ),
)

HeaderState = Literal["absent", "read", "unreadable"]
BlockState = Literal["absent", "current", "stale"]

_LINK = re.compile(r"^- \[(?P<title>.+?)\]\((?P<target>[^)]+)\)(?P<rest>.*)$")
_MEMORY_TARGET = re.compile(r"[^/#?\s]+\.md")


@dataclass(frozen=True)
class Subject:
    key: str
    name: str
    when: str


@dataclass(frozen=True)
class Rule:
    subjects: tuple[Subject, ...]
    block: str

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(subject.key for subject in self.subjects)


@dataclass(frozen=True)
class Memory:
    path: Path
    name: str | None
    title: str | None
    description: str | None
    subjects: tuple[str, ...] | None
    header: HeaderState


@dataclass(frozen=True)
class Snapshot:
    """Every file one survey or rebuild reads, read once."""

    index_text: str
    list_texts: Mapping[str, str]  # every subjects/*.md stem -> its text
    memories: Mapping[str, Memory]  # memory file name -> its header

    @property
    def newline(self) -> str:
        return "\r\n" if "\r\n" in self.index_text else "\n"

    @property
    def unread_headers(self) -> tuple[str, ...]:
        return tuple(name for name, memory in self.memories.items() if memory.header == "unreadable")


@dataclass(frozen=True)
class Links:
    """The memory-file links the current index and subject lists carry."""

    index: frozenset[str]  # memory files MEMORY.md links
    lists: Mapping[str, Mapping[str, str]]  # subject key -> memory file name -> line
    titles: Mapping[str, str]  # memory file name -> the title its first line carries

    @property
    def linked(self) -> frozenset[str]:
        return self.index | frozenset(name for lines in self.lists.values() for name in lines)


@dataclass(frozen=True)
class Plan:
    snapshot: Snapshot
    links: Links
    index_text: str
    lists: Mapping[str, str]
    removed_lists: tuple[str, ...]
    flat: int
    filed: int
    unplaced: tuple[tuple[str, str], ...]  # header problems; reaching no index is the survey's
    dropped: int


@dataclass(frozen=True)
class Survey:
    memories: int
    unplaced: tuple[tuple[str, str], ...]
    unread_headers: tuple[str, ...]
    lines: int
    characters: int
    subject_lists: Mapping[str, int]
    block: BlockState
    stale_files: int


def read_rule(source: Path = RULE_SOURCE) -> Rule:
    """Read the subject table and installed-block text from the tracked rule file."""
    text = source.read_text(encoding="utf-8")
    table = re.search(r"^## Subjects\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if table is None:
        raise ValueError(f"{source.name}: no Subjects section")
    subjects = []
    for row in table.group(1).splitlines():
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) != 3 or not row.strip().startswith("|"):
            continue
        if cells[0] in {"Subject", ""} or set(cells[0]) <= {"-", ":", " "}:
            continue
        if not re.fullmatch(r"[a-z][a-z0-9-]*", cells[0]):
            raise ValueError(f"{source.name}: invalid subject identifier {cells[0]!r}")
        subjects.append(Subject(cells[0], cells[1], cells[2]))
    keys = [subject.key for subject in subjects]
    if not subjects or len(set(keys)) != len(keys):
        raise ValueError(f"{source.name}: the subject table is empty or repeats a subject")
    block = re.search(r"^## Installed block\n.*?^```text\n(.*?)^```", text, re.M | re.S)
    if block is None:
        raise ValueError(f"{source.name}: no installed block text")
    body = block.group(1).rstrip("\n")
    if "{SUBJECTS}" not in body:
        raise ValueError(f"{source.name}: the installed block does not name the subjects")
    body = body.replace("{SUBJECTS}", ", ".join(keys))
    return Rule(tuple(subjects), "\n".join((BLOCK_START, body, BLOCK_END)))


def _scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"'):
        return str(json.loads(value))
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1].replace("''", "'")
    return value


def _subjects(raw: str | None) -> tuple[str, ...] | None:
    if raw is None:
        return None
    if raw.strip().casefold() == "none":
        return ()
    return tuple(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))


def read_memory(path: Path) -> Memory:
    """Read one memory file's header; a malformed header is reported, never guessed."""
    unreadable = Memory(path, None, None, None, None, "unreadable")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return Memory(path, None, None, None, None, "absent")
    end = text.find("\n---\n", 3)
    if end < 0 and text.endswith("\n---"):
        end = len(text) - 4
    if end < 0:
        return unreadable
    top: dict[str, str] = {}
    metadata: dict[str, str] = {}
    section = None
    try:
        for line in text[4:end].split("\n"):
            if not line.strip():
                continue
            nested = line.startswith((" ", "\t"))
            if nested and section != "metadata":
                continue
            key, colon, value = line.strip().partition(":")
            if not colon:
                raise ValueError(line)
            if nested:
                metadata[key.strip()] = _scalar(value)
            else:
                section = key.strip()
                top[section] = _scalar(value)
    except ValueError:
        return unreadable
    declared = [_subjects(place.get("subjects")) for place in (top, metadata) if "subjects" in place]
    if len(declared) == 2 and declared[0] != declared[1]:
        return unreadable
    subjects = declared[0] if declared else None
    return Memory(
        path, top.get("name") or None, top.get("title") or None,
        top.get("description") or None, subjects, "read",
    )


def memory_files(index: Path) -> tuple[Path, ...]:
    """Every top-level Markdown file beside the index except the index itself."""
    return tuple(sorted(
        path for path in index.parent.glob("*.md")
        if path.is_file() and path.name != index.name
    ))


def _split(text: str) -> list[str]:
    lines = text.replace("\r\n", "\n").split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def _list_paths(index: Path) -> tuple[Path, ...]:
    root = index.parent / SUBJECTS_DIR
    return tuple(sorted(root.glob("*.md"))) if root.is_dir() else ()


def read_snapshot(index: Path) -> Snapshot:
    return Snapshot(
        index.read_bytes().decode("utf-8"),
        {path.stem: path.read_bytes().decode("utf-8") for path in _list_paths(index)},
        {path.name: read_memory(path) for path in memory_files(index)},
    )


def index_lines(index: Path) -> list[str]:
    """Nonblank lines of MEMORY.md and of every subject list, read as one index."""
    lines = []
    for path in (index, *_list_paths(index)):
        lines.extend(line.rstrip() for line in _split(path.read_bytes().decode("utf-8")) if line.strip())
    return lines


def _memory_target(target: str, prefix: str = "") -> str | None:
    """The memory file a link names, or None for any other destination."""
    if prefix:
        if not target.startswith(prefix):
            return None
        target = target[len(prefix):]
    return target if _MEMORY_TARGET.fullmatch(target) else None


def read_links(snapshot: Snapshot, rule: Rule) -> Links:
    index: set[str] = set()
    titles: dict[str, str] = {}
    for line in _split(snapshot.index_text):
        match = _LINK.match(line.strip())
        name = match and _memory_target(match.group("target"))
        if name:
            index.add(name)
            titles.setdefault(name, match.group("title"))
    lists: dict[str, dict[str, str]] = {}
    for key, text in snapshot.list_texts.items():
        if key not in rule.keys:
            continue
        members: dict[str, str] = {}
        for line in _split(text):
            match = _LINK.match(line.strip())
            name = match and _memory_target(match.group("target"), "../")
            if name:
                members.setdefault(name, line.rstrip())
                titles.setdefault(name, match.group("title"))
        lists[key] = members
    return Links(frozenset(index), lists, titles)


def _block_bounds(lines: list[str]) -> tuple[int, int] | None:
    starts = [i for i, line in enumerate(lines) if line.strip() == BLOCK_START]
    ends = [i for i, line in enumerate(lines) if line.strip() == BLOCK_END]
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise ValueError("the memory index has malformed rule block markers")
    return starts[0], ends[0]


def _line(title: str, target: str, description: str) -> str:
    return f"- [{title}]({target}){SEPARATOR}{description}"


def plan(index: Path, rule: Rule, *, install: bool = False) -> Plan:
    """Compute the rebuilt index and subject lists without writing them."""
    snapshot = read_snapshot(index)
    current = _split(snapshot.index_text)
    bounds = _block_bounds(current)
    newline = snapshot.newline
    links = read_links(snapshot, rule)

    unplaced: list[tuple[str, str]] = []
    generated_flat: dict[str, str] = {}
    keep_flat: set[str] = set()  # memories whose existing lines are kept verbatim
    members: dict[str, list[tuple[str, str]]] = {subject.key: [] for subject in rule.subjects}
    for name, memory in snapshot.memories.items():
        title = links.titles.get(name) or memory.title or memory.name or Path(name).stem
        unknown = [key for key in (memory.subjects or ()) if key not in rule.keys]
        if memory.header == "unreadable":
            for key, lines in links.lists.items():
                if name in lines:
                    members[key].append((title, lines[name]))
        elif memory.subjects is None and name in links.index:
            pass
        elif unknown:
            unplaced.append((name, "subject not on the fixed list: " + ", ".join(unknown)))
        elif not memory.description:
            unplaced.append((name, "no description to build a line from"))
        elif not memory.subjects:
            generated_flat[name] = _line(title, name, memory.description)
            continue
        else:
            for key in memory.subjects:
                members[key].append((title, _line(title, "../" + name, memory.description)))
            continue
        keep_flat.add(name)

    body: list[str] = []
    flat = dropped = 0
    subject_targets = {f"{SUBJECTS_DIR}/{key}.md" for key in rule.keys}
    for position, line in enumerate(current):
        if bounds and bounds[0] <= position <= bounds[1]:
            continue
        match = _LINK.match(line.strip())
        target = match.group("target") if match else ""
        name = _memory_target(target) if match else None
        if target in subject_targets:
            continue  # subject lines are regenerated below
        if name is None:
            body.append(line)
        elif name not in snapshot.memories:
            dropped += 1
        elif name in keep_flat:
            body.append(line)
            flat += 1
        elif name in generated_flat:
            body.append(generated_flat.pop(name))
            flat += 1
        # otherwise the memory is filed under a subject and leaves MEMORY.md
    body.extend(generated_flat[name] for name in sorted(generated_flat))
    flat += len(generated_flat)

    subject_lines = [
        _line(subject.name, f"{SUBJECTS_DIR}/{subject.key}.md", "open when " + subject.when)
        for subject in rule.subjects if members[subject.key]
    ]
    head = [rule.block.replace("\n", newline)] if (bounds or install) else []
    index_text = newline.join([*head, *subject_lines, *body]) + newline
    lists = {}
    for subject in rule.subjects:
        entries = members[subject.key]
        if entries:
            rows = [line for _title, line in sorted(entries, key=lambda item: (item[0].casefold(), item[1]))]
            lists[subject.key] = newline.join(
                [f"# {subject.name}", "", f"Open when {subject.when}.", "", *rows]
            ) + newline
    removed = tuple(key for key in links.lists if key not in lists)
    filed = sum(1 for name, memory in snapshot.memories.items() if memory.subjects and name not in keep_flat)
    return Plan(snapshot, links, index_text, lists, removed, flat, filed, tuple(unplaced), dropped)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    try:
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def write(index: Path, rule: Rule, *, install: bool = False) -> Plan:
    """Rebuild the index and subject lists, removing a table subject's list once it is empty.

    Every output is derived from the memory files' headers, so a run interrupted after
    some lists were written converges on the next run.
    """
    result = plan(index, rule, install=install)
    for key, text in result.lists.items():
        _write_atomic(index.parent / SUBJECTS_DIR / f"{key}.md", text)
    for key in result.removed_lists:
        (index.parent / SUBJECTS_DIR / f"{key}.md").unlink()
    _write_atomic(index, result.index_text)
    return result


def _measure_text(text: str) -> tuple[int, int]:
    text = text.strip(JS_TRIM_WHITESPACE)
    lines = len(text.split("\n")) if text else 0
    return lines, len(text.encode("utf-16-le")) // 2


def measure(index: Path) -> tuple[int, int]:
    """Lines and characters as Claude Code counts the loaded index (ADR 0333).

    Claude Code measures the trimmed JavaScript string in UTF-16 code units rather
    than UTF-8 bytes; interior CRLF characters are preserved.
    """
    return _measure_text(index.read_bytes().decode("utf-8"))


def subject_list_summary(subject_lists: Mapping[str, int]) -> str:
    """The one wording of the ungraded subject-list sizes (ADR 0391 ruling 9)."""
    sizes = "; ".join(f"{key} {count} lines" for key, count in sorted(subject_lists.items()))
    return "subject lists (reported only): " + (sizes or "none")


def survey(index: Path, rule: Rule | None = None) -> Survey:
    """Report the index as it stands on disk: placement, list sizes, and pending changes."""
    rule = rule or read_rule()
    result = plan(index, rule)
    snapshot = result.snapshot
    reasons = dict(result.unplaced)
    unread = snapshot.unread_headers
    for name in snapshot.memories:
        if name not in result.links.linked and name not in reasons:
            reasons[name] = (
                "the header cannot be read and the memory is in no index" if name in unread
                else "no line in any index; rebuild to place it"
            )
    current = snapshot.index_text
    block: BlockState
    if BLOCK_START not in current:
        block = "absent"
    else:
        block = "current" if rule.block.replace("\n", snapshot.newline) in current else "stale"
    stale_files = int(current != result.index_text) + len(result.removed_lists) + sum(
        snapshot.list_texts.get(key) != text for key, text in result.lists.items()
    )
    lines, characters = _measure_text(current)
    return Survey(
        len(snapshot.memories), tuple(sorted(reasons.items())), unread, lines, characters,
        {key: sum(1 for line in _split(text) if line.strip()) for key, text in snapshot.list_texts.items()},
        block, stale_files,
    )


def report_lines(view: Survey, *, show: bool, wrote: Plan | None) -> list[str]:
    placed = view.memories - len(view.unplaced)
    report = [
        f"memory files: {view.memories}; placed {placed}; unplaced {len(view.unplaced)}",
        f"unread headers: {len(view.unread_headers)}",
        f"MEMORY.md: {view.lines} lines; {view.characters} characters",
        subject_list_summary(view.subject_lists),
        f"rule block: {view.block}",
    ]
    if wrote is not None:
        report.append(f"rebuilt: {wrote.flat} flat lines; {wrote.filed} memories under subjects; "
                      f"{wrote.dropped} dangling lines dropped")
    else:
        report.append(f"files a rebuild would change: {view.stale_files}")
    if show:
        report.extend(f"  unplaced: {name}: {reason}" for name, reason in view.unplaced)
        report.extend(f"  unread header: {name}" for name in view.unread_headers)
    return report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Survey or rebuild the memory index (ADR 0391).")
    parser.add_argument("index", type=Path, help="the MEMORY.md file")
    parser.add_argument("--write", action="store_true", help="rebuild the subject lists and flat lines")
    parser.add_argument("--install-rule", action="store_true", help="also insert the rule block (needs --write)")
    parser.add_argument("--show", action="store_true", help="name the files behind each count")
    args = parser.parse_args(argv)
    if args.install_rule and not args.write:
        parser.error("--install-rule requires --write")
    index = args.index.expanduser()
    try:
        rule = read_rule()
        if not index.is_file():
            raise OSError(f"{index} is not a file")
        wrote = write(index, rule, install=args.install_rule) if args.write else None
        # Deliberately re-read after a write: the report describes the files on disk.
        view = survey(index, rule)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"memory index NOT READ: {exc}", file=sys.stderr)
        return 2
    print("\n".join(report_lines(view, show=args.show, wrote=wrote)))
    return 1 if view.unplaced else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
