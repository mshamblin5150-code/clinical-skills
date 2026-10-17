#!/usr/bin/env python3
"""Survey or rebuild the Claude Code memory index and its subject lists.

    python tools/memory_index.py <MEMORY.md> [--write [--install-rule]] [--show]

ADR 0391. ``MEMORY.md`` keeps flat lines for memories that apply in every session
and one line per subject; each subject line points to ``subjects/<subject>.md``. Every
memory file declares its placement in its own header as ``subjects: <subject>, ...``
or ``subjects: none``. The filing rule and the fixed subject table live in
``docs/agents/memory.md``.

Without ``--write`` the command reads and reports. ``--write`` rebuilds every
subject list and the flat part of ``MEMORY.md`` from the memory files' own headers
and descriptions, and refreshes the installed rule block when it is present;
``--install-rule`` also inserts that block. A memory with no ``subjects`` header keeps
its existing flat line, so a rebuild before any header exists leaves the index's
lines unchanged.

The population is every top-level ``*.md`` beside the index other than the index
itself, derived from the directory rather than from the index's links. Exit 0
means every memory file is placed in an index, 1 means at least one is unplaced,
and 2 means the index, its directory, or the tracked rule could not be read. Counts
print by default; ``--show`` names unplaced memory files.

The complete boundary is ``DECLARED_LIMITS``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Mapping

from console_codec import require_python_floor, use_utf8


RULE_SOURCE = Path(__file__).resolve().parent.parent / "docs" / "agents" / "memory.md"
BLOCK_START = (
    "<!-- memory-index rule: installed from docs/agents/memory.md by "
    "tools/memory_index.py; edit there -->"
)
BLOCK_END = "<!-- end memory-index rule -->"
SUBJECTS_DIR = "subjects"
SEPARATOR = " — "
# ECMAScript WhiteSpace and LineTerminator characters used by String.trim().
JS_TRIM_WHITESPACE = (
    "\t\n\v\f\r         "
    "         　﻿"
)

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
)

_LINK = re.compile(r"^- \[(?P<title>.+?)\]\((?P<target>[^)]+)\)(?P<rest>.*)$")


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
    header: str  # "absent", "read", or "unreadable"


@dataclass(frozen=True)
class Plan:
    index_text: str
    lists: Mapping[str, str]
    memories: int
    flat: int
    filed: int
    unplaced: tuple[tuple[str, str], ...]
    dropped: int


@dataclass(frozen=True)
class Survey:
    memories: int
    unplaced: tuple[tuple[str, str], ...]
    lines: int
    characters: int
    subject_lists: Mapping[str, int]
    block: str  # "absent", "current", or "stale"
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
        if cells[0] in {"Subject", ""} or set(cells[0]) <= {"-", " "}:
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


def read_memory(path: Path) -> Memory:
    """Read one memory file's header; a malformed header is reported, never guessed."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return Memory(path, None, None, None, None, "absent")
    end = text.find("\n---\n", 3)
    if end < 0 and text.endswith("\n---"):
        end = len(text) - 4
    if end < 0:
        return Memory(path, None, None, None, None, "unreadable")
    top: dict[str, str] = {}
    metadata: dict[str, str] = {}
    section = None
    try:
        for line in text[4:end].split("\n"):
            if not line.strip():
                continue
            if line.startswith((" ", "\t")):
                if section != "metadata":
                    continue
                key, colon, value = line.strip().partition(":")
                if not colon:
                    raise ValueError(line)
                metadata[key.strip()] = _scalar(value)
                continue
            key, colon, value = line.partition(":")
            if not colon:
                raise ValueError(line)
            section = key.strip()
            top[section] = _scalar(value)
    except ValueError:
        return Memory(path, None, None, None, None, "unreadable")
    raw = metadata.get("subjects")
    subjects: tuple[str, ...] | None
    if raw is None:
        subjects = None
    elif raw.strip().casefold() == "none":
        subjects = ()
    else:
        subjects = tuple(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))
    description = top.get("description") or None
    return Memory(path, top.get("name") or None, top.get("title") or None, description, subjects, "read")


def memory_files(index: Path) -> tuple[Path, ...]:
    """Every top-level Markdown file beside the index except the index itself."""
    return tuple(sorted(
        path for path in index.parent.glob("*.md")
        if path.is_file() and path.name != index.name
    ))


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")


def _list_paths(index: Path) -> tuple[Path, ...]:
    root = index.parent / SUBJECTS_DIR
    return tuple(sorted(root.glob("*.md"))) if root.is_dir() else ()


def index_lines(index: Path) -> list[str]:
    """Nonblank lines of MEMORY.md and of every subject list, read as one index."""
    lines = []
    for path in (index, *_list_paths(index)):
        lines.extend(line.rstrip() for line in _lines(path) if line.strip())
    return lines


def _links(lines: list[str], prefix: str = "") -> dict[str, str]:
    """Map a linked memory file name to the title its line carries."""
    titles: dict[str, str] = {}
    for line in lines:
        match = _LINK.match(line.strip())
        if match:
            target = match.group("target")
            if prefix and target.startswith(prefix):
                target = target[len(prefix):]
            if "/" not in target:
                titles.setdefault(target, match.group("title"))
    return titles


def _line(title: str, target: str, description: str) -> str:
    return f"- [{title}]({target}){SEPARATOR}{description}"


def plan(index: Path, rule: Rule, *, install: bool = False) -> Plan:
    """Compute the rebuilt index and subject lists without writing them."""
    current = _lines(index)
    newline = "\r\n" if b"\r\n" in index.read_bytes() else "\n"
    list_titles: dict[str, str] = {}
    for path in _list_paths(index):
        list_titles.update({k: v for k, v in _links(_lines(path), "../").items() if k not in list_titles})
    index_titles = _links(current)
    memories = {path.name: read_memory(path) for path in memory_files(index)}

    unplaced: list[tuple[str, str]] = []
    generated_flat: dict[str, str] = {}
    keep_flat: set[str] = set()
    members: dict[str, list[tuple[str, str]]] = {subject.key: [] for subject in rule.subjects}
    for name, memory in memories.items():
        title = index_titles.get(name) or list_titles.get(name) or memory.title or memory.name or Path(name).stem
        if memory.header == "unreadable":
            unplaced.append((name, "the header cannot be read"))
            keep_flat.add(name)
            continue
        if memory.subjects is None and name in index_titles:
            keep_flat.add(name)
            continue
        unknown = [key for key in (memory.subjects or ()) if key not in rule.keys]
        if unknown:
            unplaced.append((name, "subject not on the fixed list: " + ", ".join(unknown)))
            keep_flat.add(name)
            continue
        if not memory.description:
            unplaced.append((name, "no description to build a line from"))
            keep_flat.add(name)
            continue
        if not memory.subjects:
            generated_flat[name] = _line(title, name, memory.description)
        else:
            for key in memory.subjects:
                members[key].append((title, _line(title, "../" + name, memory.description)))

    body: list[str] = []
    dropped = 0
    in_block = False
    had_block = False
    for line in current:
        stripped = line.strip()
        if stripped == BLOCK_START:
            in_block, had_block = True, True
            continue
        if in_block:
            if stripped == BLOCK_END:
                in_block = False
            continue
        match = _LINK.match(stripped)
        if not match:
            if stripped:
                body.append(line.rstrip())
            continue
        target = match.group("target")
        if target.startswith(SUBJECTS_DIR + "/"):
            key = target[len(SUBJECTS_DIR) + 1:].removesuffix(".md")
            if key not in rule.keys:
                body.append(line.rstrip())
            continue
        if "/" in target or target not in memories:
            dropped += 1
            continue
        if target in keep_flat:
            body.append(line.rstrip())
        elif target in generated_flat:
            body.append(generated_flat.pop(target))
        # otherwise the memory is filed under a subject and leaves MEMORY.md
    body.extend(generated_flat[name] for name in sorted(generated_flat))

    subject_lines = [
        _line(subject.name, f"{SUBJECTS_DIR}/{subject.key}.md", "open when " + subject.when)
        for subject in rule.subjects if members[subject.key]
    ]
    head = [rule.block] if (had_block or install) else []
    index_text = newline.join([*head, *subject_lines, *body]) + newline
    lists = {}
    for subject in rule.subjects:
        entries = members[subject.key]
        if not entries:
            continue
        rows = [line for _title, line in sorted(entries, key=lambda item: (item[0].casefold(), item[1]))]
        lists[subject.key] = newline.join(
            [f"# {subject.name}", "", f"Open when {subject.when}.", "", *rows]
        ) + newline
    flat = sum(1 for line in body if _LINK.match(line.strip()))
    filed = sum(1 for memory in memories.values() if memory.subjects and memory.path.name not in keep_flat)
    return Plan(index_text, lists, len(memories), flat, filed, tuple(unplaced), dropped)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    temporary.replace(path)


def write(index: Path, rule: Rule, *, install: bool = False) -> Plan:
    """Rebuild the index and subject lists, removing a table subject's list once it is empty."""
    result = plan(index, rule, install=install)
    for key, text in result.lists.items():
        _write_atomic(index.parent / SUBJECTS_DIR / f"{key}.md", text)
    for subject in rule.subjects:
        stale = index.parent / SUBJECTS_DIR / f"{subject.key}.md"
        if subject.key not in result.lists and stale.is_file():
            stale.unlink()
    _write_atomic(index, result.index_text)
    return result


def measure(index: Path) -> tuple[int, int]:
    """Lines and characters as Claude Code counts the loaded index (ADR 0333).

    Claude Code measures the trimmed JavaScript string in UTF-16 code units rather
    than UTF-8 bytes; interior CRLF characters are preserved.
    """
    text = index.read_bytes().decode("utf-8").strip(JS_TRIM_WHITESPACE)
    lines = len(text.split("\n")) if text else 0
    return lines, len(text.encode("utf-16-le")) // 2


def survey(index: Path, rule: Rule | None = None) -> Survey:
    """Report the current index: placement of every memory file and each list's size."""
    rule = rule or read_rule()
    result = plan(index, rule)
    linked = set(_links(_lines(index)))
    for path in _list_paths(index):
        linked |= set(_links(_lines(path), "../"))
    reasons = dict(result.unplaced)
    for path in memory_files(index):
        if path.name not in linked and path.name not in reasons:
            reasons[path.name] = "no line in any index; rebuild to place it"
    lists = {path.stem: sum(1 for line in _lines(path) if line.strip()) for path in _list_paths(index)}
    current = index.read_text(encoding="utf-8")
    if BLOCK_START not in current:
        block = "absent"
    else:
        block = "current" if rule.block.replace("\n", "\r\n" if "\r\n" in current else "\n") in current else "stale"
    stale_files = int(result.index_text.replace("\r\n", "\n") != current.replace("\r\n", "\n"))
    for key, text in result.lists.items():
        path = index.parent / SUBJECTS_DIR / f"{key}.md"
        existing = path.read_text(encoding="utf-8") if path.is_file() else None
        stale_files += int(existing is None or existing.replace("\r\n", "\n") != text.replace("\r\n", "\n"))
    lines, characters = measure(index)
    return Survey(
        result.memories, tuple(sorted(reasons.items())), lines, characters, lists, block, stale_files
    )


def report_lines(index: Path, view: Survey, *, show: bool, wrote: Plan | None) -> list[str]:
    placed = view.memories - len(view.unplaced)
    report = [
        f"memory files: {view.memories}; placed {placed}; unplaced {len(view.unplaced)}",
        f"MEMORY.md: {view.lines} lines; {view.characters} characters",
        "subject lists (reported only): "
        + ("; ".join(f"{key} {count} lines" for key, count in sorted(view.subject_lists.items())) or "none"),
        f"rule block: {view.block}",
    ]
    if wrote is not None:
        report.append(f"rebuilt: {wrote.flat} flat lines; {wrote.filed} memories under subjects; "
                      f"{wrote.dropped} dangling lines dropped")
    else:
        report.append(f"files a rebuild would change: {view.stale_files}")
    if show:
        report.extend(f"  unplaced: {name}: {reason}" for name, reason in view.unplaced)
    return report


def main(argv: list[str]) -> int:
    args = [arg for arg in argv if not arg.startswith("--")]
    flags = {arg for arg in argv if arg.startswith("--")}
    unknown = flags - {"--write", "--install-rule", "--show"}
    if len(args) != 1 or unknown or ("--install-rule" in flags and "--write" not in flags):
        print("usage: memory_index.py <MEMORY.md> [--write [--install-rule]] [--show]", file=sys.stderr)
        return 2
    index = Path(args[0]).expanduser()
    try:
        rule = read_rule()
        if not index.is_file():
            raise OSError(f"{index} is not a file")
        wrote = write(index, rule, install="--install-rule" in flags) if "--write" in flags else None
        view = survey(index, rule)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"memory index NOT READ: {exc}", file=sys.stderr)
        return 2
    print("\n".join(report_lines(index, view, show="--show" in flags, wrote=wrote)))
    return 1 if view.unplaced else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
