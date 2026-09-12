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

from console_codec import require_python_floor, use_utf8


TSource = TypeVar("TSource")
TScan = TypeVar("TScan")
NOT_GRADED = "not graded"
UNREADABLE_RUN_ARTIFACT = "a run artifact could not be opened"


class EvidenceDisposition(Enum):
    """How a grader-family declared limit is supported."""

    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"

DECLARED_LIMITS = (
    (
        "grader-family discovery",
        "top-level survey(), top-level format_report(), and an if __name__ == '__main__' guard; "
        "grader shapes assembled differently are invisible",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "direct text-read classification",
        "AST floor over direct .read_text calls with an absent errors argument or the literal "
        "errors='replace'; a strict read counts as a refusal only when both OSError and "
        "UnicodeError are converted to SourceError; other conversions remain in the crashing "
        "count, and built-in open calls, indirect readers, and computed error modes are invisible",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "run artifacts read through read_run_directory",
        "Members that call read_run_directory open only top-level files matching "
        "*.md (case-insensitively on Windows) whose stem is not README; artifacts "
        "in subdirectories and files with other extensions are not read.",
        EvidenceDisposition.BEHAVIOR,
    ),
)
WALK_CEILING = DECLARED_LIMITS[0][1]
TEXT_READ_WALK_CEILING = DECLARED_LIMITS[1][1]

MEMBERS: set[str] = {
    "anchor_scan",
    "aar_scan",
    "block_scan",
    "case_study_scan",
    "checks_ledger",
    "differential_scan",
    "discussion_post_scan",
    "discussion_reply_scan",
    "peer_critique_scan",
    "deck_scan",
    "reference_scan",
    "refusal_scan",
    "render_scan",
    "research_ledger",
    "specificity_scan",
    "filled_vitals_census",
    "voice_model_scan",
}


class EmptyPopulationPosture(Enum):
    """The closed family vocabulary for an empty load-bearing population."""

    NOT_SCANNED = "not-scanned"
    FINDING = "finding"
    ESTABLISHED = "established"


@dataclass(frozen=True)
class EmptyPopulationDeclaration:
    """One member's ruling for its load-bearing population when that set is empty."""

    population: str
    posture: EmptyPopulationPosture
    finding: str | None
    reason: str


EMPTY_POPULATION_POSTURES: Mapping[str, EmptyPopulationDeclaration] = MappingProxyType(
    {
        "aar_scan": EmptyPopulationDeclaration(
            "the submission's review record",
            EmptyPopulationPosture.FINDING,
            "missing-review",
            "a requested submission owes one completed review record",
        ),
        "anchor_scan": EmptyPopulationDeclaration(
            "marked, listed, and pediatric bands",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the matchers establish membership in those bands",
        ),
        "block_scan": EmptyPopulationDeclaration(
            "notes carrying a tier block",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the tier-block matcher establishes that a note belongs",
        ),
        "case_study_scan": EmptyPopulationDeclaration(
            "recognized sections",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the section matcher establishes a recognized case-study section",
        ),
        "checks_ledger": EmptyPopulationDeclaration(
            "check records",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the record parser establishes a check record",
        ),
        "deck_scan": EmptyPopulationDeclaration(
            "text runs read from slide faces",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the slide-face readers establish a readable text run",
        ),
        "differential_scan": EmptyPopulationDeclaration(
            "differential and conclusion entries, labeled blocks, and FILLED-proposed items",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the note matchers establish membership in the named union",
        ),
        "discussion_post_scan": EmptyPopulationDeclaration(
            "the draft's body text with headings removed",
            EmptyPopulationPosture.FINDING,
            "empty-body",
            "an initial post owes substantive body text independently of its signed floors",
        ),
        "discussion_reply_scan": EmptyPopulationDeclaration(
            "the replies' text",
            EmptyPopulationPosture.FINDING,
            "word-floor",
            "a requested reply owes text and its existing word-floor row settles the absence",
        ),
        "filled_vitals_census": EmptyPopulationDeclaration(
            "filled heights and filled pressures",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the filled-vitals matchers establish either population",
        ),
        "peer_critique_scan": EmptyPopulationDeclaration(
            "the critique's text",
            EmptyPopulationPosture.FINDING,
            "word-floor",
            "a requested critique owes text and its existing word-floor row settles the absence",
        ),
        "reference_scan": EmptyPopulationDeclaration(
            "reference entries",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the reference-list parser establishes an entry",
        ),
        "refusal_scan": EmptyPopulationDeclaration(
            "NOT CODED lines in the refusal block, well-formed and malformed",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the refusal-block matcher establishes a line in this population",
        ),
        "render_scan": EmptyPopulationDeclaration(
            "the final pass's exported pages",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the retained-pass reader establishes an exported page",
        ),
        "research_ledger": EmptyPopulationDeclaration(
            "claim records",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the claim-record parser establishes a record",
        ),
        "specificity_scan": EmptyPopulationDeclaration(
            "for-entry SPECIFICITY flags",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the specificity matcher establishes a for-entry flag",
        ),
        "voice_model_scan": EmptyPopulationDeclaration(
            "register headings",
            EmptyPopulationPosture.NOT_SCANNED,
            None,
            "only the register-heading matcher establishes a register",
        ),
    }
)

REFUSED: Mapping[str, str] = MappingProxyType(
    {
        "threshold_sheet": (
            "the shared runner has no quiet path and grades one source to one status, "
            "while threshold_sheet must suppress reports under --quiet and --all must "
            "return the worst status across multiple sheets"
        ),
        "tracker_bodies": (
            "the shared runner passes show to format_report, which takes no show flag because "
            "its report is safe to paste, and Parsed carries one positional source while the "
            "harvest mode grades several files as one population"
        ),
        "tracker_coordinates": (
            "the shared runner accepts one positional run source, while this command grades "
            "changed tracker events or a forward-only ADR population selected from per-file "
            "git history"
        ),
    }
)

DEFERRED: Mapping[str, str] = MappingProxyType({})

GRADER_LOOKALIKES: Mapping[str, str] = MappingProxyType(
    {
        "corpus_census": "a census over the corpus, not a grader over a run",
    }
)

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
                "peer_critique_scan": "the roster, claim ledger and critique are required primary sources for the critique grade",
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
    require_python_floor()
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
