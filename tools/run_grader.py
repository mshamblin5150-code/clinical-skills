#!/usr/bin/env python3
"""Shared runner, run-directory reader, and family declarations for run graders.

The population walk is deliberately a floor on one source shape: a module with
an executable ``__main__`` guard plus top-level ``survey`` and ``format_report``
functions. A grader that assembles those parts under different names is outside
what this instrument can see; membership here is never proof that none exists.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Generic, Mapping, TypeVar

from console_codec import use_utf8


TSource = TypeVar("TSource")
TScan = TypeVar("TScan")
NOT_GRADED = "not graded"
UNREADABLE_RUN_ARTIFACT = "a run artifact could not be opened"


class EvidenceDisposition(Enum):
    """How a grader-family declared limit is supported."""

    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"

WALK_CEILING = (
    "top-level survey(), top-level format_report(), and an if __name__ == '__main__' guard; "
    "grader shapes assembled differently are invisible"
)

MEMBERS: set[str] = {
    "anchor_scan",
    "aar_scan",
    "block_scan",
    "case_study_scan",
    "checks_ledger",
    "differential_scan",
    "discussion_post_scan",
    "discussion_reply_scan",
    "deck_scan",
    "reference_scan",
    "refusal_scan",
    "render_scan",
    "research_ledger",
    "specificity_scan",
    "filled_vitals_census",
    "voice_model_scan",
}

REFUSED: Mapping[str, str] = MappingProxyType(
    {
        "corpus_census": "a census over the corpus, not a grader over a run",
        "threshold_sheet": (
            "the shared runner has no quiet path and grades one source to one status, "
            "while threshold_sheet must suppress reports under --quiet and --all must "
            "return the worst status across multiple sheets"
        ),
        "tracker_bodies": "format_report takes no show flag and its report is safe to paste",
    }
)

DEFERRED: Mapping[str, str] = MappingProxyType({})

# Named beside the walk because the population review considered them, but their
# present source shape is below the predicate's stated floor.
OUTSIDE_WALK: Mapping[str, str] = MappingProxyType(
    {
        "tracker_scan": "main assembles values outside a Scan and keeps unscanned out of format_report",
        "voice_corpus": "format_report returns a list and takes no source",
    }
)

RUN_DIRECTORY_READERS = frozenset(
    {
        "anchor_scan",
        "block_scan",
        "differential_scan",
        "filled_vitals_census",
        "refusal_scan",
        "specificity_scan",
    }
)
RUN_DIRECTORY_BYTE_REASON = (
    "the shared run-directory reader preserves the other artifacts in the set"
)

UNDECODABLE_BYTE_POSTURES: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "grade": MappingProxyType(
            {
                **{
                    name: RUN_DIRECTORY_BYTE_REASON
                    for name in sorted(RUN_DIRECTORY_READERS)
                },
                "case_study_scan": "the draft and optional skill reads use replacement so their readable text remains gradeable",
                "checks_ledger": "the ledger read uses replacement and grades the rows it can recover",
                "reference_scan": "the draft read uses replacement and grades the references it can recover",
                "research_ledger": "the run artifacts use replacement and grade the records they can recover",
            }
        ),
        "refuse": MappingProxyType(
            {
                "deck_scan": "the signed bar and claim ledger are required primary sources for the deck grade",
                "discussion_post_scan": "the signed run artifacts are required primary sources for the post grade",
                "discussion_reply_scan": "the roster and signed run artifacts are required primary sources for the reply grade",
                "voice_model_scan": "the model and tracked specification must both be readable before the comparison can run",
            }
        ),
        "finding": MappingProxyType(
            {
                "aar_scan": "the graded path converts unreadable strict baseline and orphan-pointer evidence into findings; replacement would corrupt landing evidence",
            }
        ),
        "crash": MappingProxyType({}),
        "no text read": MappingProxyType(
            {
                "render_scan": "the retained export is opened by PyMuPDF and the module performs no built-in text read",
            }
        ),
    }
)

TEXT_READ_WALK_CEILING = (
    "AST floor over direct .read_text calls with an absent errors argument or the literal "
    "errors='replace'; a strict read counts as a refusal only when both OSError and "
    "UnicodeError are converted to SourceError; other conversions remain in the crashing "
    "count, and built-in open calls, indirect readers, and computed error modes are invisible"
)


@dataclass(frozen=True)
class TextReadWalk:
    """Recognized direct text reads and the unread remainder under the walk's ceiling."""

    total: int
    replacing: int
    refusing: int
    crashing: int

    @property
    def recognized(self) -> int:
        return self.replacing + self.refusing + self.crashing

    @property
    def unread(self) -> int:
        return self.total - self.recognized


def _exception_names(node: ast.expr | None) -> set[str]:
    if node is None:
        return {"BaseException"}
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, ast.Attribute):
        return {node.attr}
    if isinstance(node, ast.Tuple):
        return set().union(*(_exception_names(item) for item in node.elts))
    return set()


def _raises_source_error(handler: ast.ExceptHandler) -> bool:
    return any(
        isinstance(node, ast.Raise)
        and isinstance(node.exc, ast.Call)
        and (
            isinstance(node.exc.func, ast.Name)
            and node.exc.func.id == "SourceError"
            or isinstance(node.exc.func, ast.Attribute)
            and node.exc.func.attr == "SourceError"
        )
        for node in ast.walk(handler)
    )


def _converts_read_failure(handler: ast.ExceptHandler) -> bool:
    caught = _exception_names(handler.type)
    covers_read_failures = bool(
        caught & {"Exception", "BaseException"}
        or {"OSError", "UnicodeError"} <= caught
    )
    return covers_read_failures and _raises_source_error(handler)


def walk_text_reads(source: str) -> TextReadWalk:
    """Count direct ``read_text`` calls without presenting partial coverage as whole."""

    tree = ast.parse(source)
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    def enclosed_by_refusal(node: ast.AST) -> bool:
        child = node
        parent = parents.get(child)
        while parent is not None:
            if isinstance(parent, ast.Try) and child in parent.body:
                if any(_converts_read_failure(handler) for handler in parent.handlers):
                    return True
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            child, parent = parent, parents.get(parent)
        return False

    def enclosing_function(node: ast.AST) -> str | None:
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return parent.name
            parent = parents.get(parent)
        return None

    def helper_called_under_refusal(name: str | None) -> bool:
        if name is None:
            return False
        return any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
            and enclosed_by_refusal(node)
            for node in ast.walk(tree)
        )

    total = replacing = refusing = crashing = 0
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "read_text"
        ):
            continue
        total += 1
        if any(keyword.arg is None for keyword in node.keywords):
            continue
        errors = next((keyword.value for keyword in node.keywords if keyword.arg == "errors"), None)
        if errors is None:
            if enclosed_by_refusal(node) or helper_called_under_refusal(enclosing_function(node)):
                refusing += 1
            else:
                crashing += 1
        elif isinstance(errors, ast.Constant) and errors.value == "replace":
            replacing += 1
    return TextReadWalk(
        total=total,
        replacing=replacing,
        refusing=refusing,
        crashing=crashing,
    )


@dataclass(frozen=True)
class Finding:
    """The one field every grader finding shares."""

    kind: str


@dataclass(frozen=True)
class Option:
    """One declared command-line option."""

    name: str
    takes_value: bool = False
    missing_value: str | None = None
    repeatable: bool = True


@dataclass(frozen=True)
class Parsed:
    """The shared reading of one grader invocation."""

    source: str
    flags: frozenset[str] = frozenset()
    values: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    @property
    def show(self) -> bool:
        return "--show" in self.flags

    def enabled(self, name: str) -> bool:
        return name in self.flags

    def value(self, name: str) -> str | None:
        return self.values.get(name)


@dataclass(frozen=True)
class Grade(Generic[TScan]):
    """A completed grade whose report and status have not yet been emitted."""

    scan: TScan
    source: str
    findings_failed: bool = False
    coverage_failed: bool = False
    coverage_limbs: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()
    reports: tuple[str, ...] = ()


@dataclass(frozen=True)
class EarlyExit:
    """A declared non-grader mode, such as a separated-reader brief."""

    status: int
    stdout: tuple[str, ...] = ()
    stderr: tuple[str, ...] = ()
    exit_2_limb: str | None = None


class SourceError(Exception):
    """A primary source was unavailable, so nothing could be graded."""

    def __init__(self, message: str, *, exit_2_limb: str | None = None):
        super().__init__(message)
        self.exit_2_limb = exit_2_limb


def read_run_directory(directory: Path) -> list[str]:
    """Read a run directory's Markdown artifacts in name order, excluding README."""

    try:
        return [
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(directory.glob("*.md"))
            if path.is_file() and path.stem.lower() != "readme"
        ]
    except OSError as failure:
        raise SourceError(
            f"could not read a run artifact in {directory.name}",
            exit_2_limb=UNREADABLE_RUN_ARTIFACT,
        ) from failure


class ParseError(SourceError):
    """An invocation the declared command-line interface refuses."""


@dataclass(frozen=True)
class Grader(Generic[TSource, TScan]):
    """The per-module parts called by the shared runner."""

    usage: str
    load: Callable[[Parsed], TSource]
    grade: Callable[[TSource, Parsed], Grade[TScan] | EarlyExit]
    format_report: Callable[..., str]
    options: tuple[Option, ...] = ()
    parse_error: Callable[[str], str] = lambda message: message
    validate: Callable[[Parsed], str | None] | None = None
    source_error_to_stdout: bool = False
    allow_extra_positionals: bool = True
    exit_2_limbs: tuple[str, ...] = ()
    invalid_invocation_limb: str | None = None

    def __post_init__(self) -> None:
        if not self.exit_2_limbs:
            if self.invalid_invocation_limb is not None:
                raise ValueError("invalid_invocation_limb needs an exit-2 vocabulary")
            return
        if any(not limb.strip() for limb in self.exit_2_limbs):
            raise ValueError("exit-2 limbs must be nonempty")
        if len(set(self.exit_2_limbs)) != len(self.exit_2_limbs):
            raise ValueError("exit-2 limbs must be distinct")
        if self.invalid_invocation_limb not in self.exit_2_limbs:
            raise ValueError("the exit-2 vocabulary must name invalid invocation")


def _require_declared_exit_2_limb(command: Grader[Any, Any], limb: str | None) -> None:
    """Refuse an unclassified exit 2 where a grader declares exact coverage."""
    if not command.exit_2_limbs:
        return
    if limb is None:
        raise ValueError("an exit-2 path names no exit-2 limb")
    if limb not in command.exit_2_limbs:
        raise ValueError(f"undeclared exit-2 limb: {limb}")


def parse(command: Grader[Any, Any], argv: list[str]) -> Parsed:
    declared = {option.name: option for option in command.options}
    positionals: list[str] = []
    flags: set[str] = set()
    values: dict[str, str] = {}
    index = 0
    while index < len(argv):
        argument = argv[index]
        name, separator, attached = argument.partition("=")
        if argument.startswith("-"):
            option = declared.get(name)
            if option is None:
                raise ParseError(command.parse_error(f"unrecognized option {name}"))
            if not option.repeatable and (name in flags or name in values):
                raise ParseError(command.parse_error(f"{name} was given twice"))
            if option.takes_value:
                if separator:
                    value = attached
                else:
                    index += 1
                    if index >= len(argv) or argv[index].startswith("-"):
                        complaint = option.missing_value or f"{name} needs a value"
                        raise ParseError(command.parse_error(complaint))
                    value = argv[index]
                if not value:
                    complaint = option.missing_value or f"{name} needs a value"
                    raise ParseError(command.parse_error(complaint))
                values[name] = value
            else:
                if separator:
                    raise ParseError(command.parse_error(f"{name} does not take a value"))
                flags.add(name)
        else:
            positionals.append(argument)
        index += 1

    if not positionals:
        raise ParseError(command.usage)
    if len(positionals) != 1 and not command.allow_extra_positionals:
        raise ParseError(command.parse_error("one source at a time"))
    parsed = Parsed(
        source=positionals[0],
        flags=frozenset(flags),
        values=MappingProxyType(values),
    )
    if command.validate is not None:
        complaint = command.validate(parsed)
        if complaint:
            raise ParseError(command.parse_error(complaint))
    return parsed


def run(command: Grader[TSource, TScan], argv: list[str]) -> int:
    """Run one grader with source failures before output and status at the tail."""

    use_utf8()
    try:
        parsed = parse(command, argv)
    except ParseError as failure:
        _require_declared_exit_2_limb(command, command.invalid_invocation_limb)
        print(str(failure), file=sys.stderr)
        return 2
    try:
        source = command.load(parsed)
    except SourceError as failure:
        _require_declared_exit_2_limb(command, failure.exit_2_limb)
        print(str(failure), file=sys.stdout if command.source_error_to_stdout else sys.stderr)
        return 2

    result = command.grade(source, parsed)
    if isinstance(result, EarlyExit):
        if result.status == 2:
            _require_declared_exit_2_limb(command, result.exit_2_limb)
        for chunk in result.stdout:
            print(chunk, end="" if chunk.endswith("\n") else "\n")
        for line in result.stderr:
            print(line, file=sys.stderr)
        return result.status

    if result.coverage_failed:
        if command.exit_2_limbs and not result.coverage_limbs:
            raise ValueError("coverage failure names no exit-2 limb")
        for limb in result.coverage_limbs:
            _require_declared_exit_2_limb(command, limb)
    elif result.coverage_limbs:
        raise ValueError("coverage limbs require coverage_failed")
    print(command.format_report(result.scan, result.source, show=parsed.show))
    for report in result.reports:
        print(report)
    for diagnostic in result.diagnostics:
        print(diagnostic, file=sys.stderr)
    if result.findings_failed:
        return 1
    if result.coverage_failed:
        return 2
    return 0


def _has_main_guard(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        comparison = node.test
        if not isinstance(comparison, ast.Compare) or len(comparison.ops) != 1:
            continue
        if not isinstance(comparison.left, ast.Name) or comparison.left.id != "__name__":
            continue
        if any(isinstance(value, ast.Constant) and value.value == "__main__" for value in comparison.comparators):
            return True
    return False


def walk_grader_modules(directory: Path | None = None) -> set[str]:
    """Derive the visible grader population from source rather than a typed list."""

    root = directory or Path(__file__).parent
    population: set[str] = set()
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if {"survey", "format_report"} <= functions and _has_main_guard(tree):
            population.add(path.stem)
    return population
