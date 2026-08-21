#!/usr/bin/env python3
"""Shared command tail for graders over run artifacts.

The population walk is deliberately a floor on one source shape: a module with
an executable ``__main__`` guard plus top-level ``survey`` and ``format_report``
functions. A grader that assembles those parts under different names is outside
what this instrument can see; membership here is never proof that none exists.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Generic, Mapping, TypeVar

from console_codec import use_utf8


TSource = TypeVar("TSource")
TScan = TypeVar("TScan")

WALK_CEILING = (
    "top-level survey(), top-level format_report(), and an if __name__ == '__main__' guard; "
    "grader shapes assembled differently are invisible"
)

MEMBERS: set[str] = {
    "anchor_scan",
    "block_scan",
    "case_study_scan",
    "checks_ledger",
    "differential_scan",
    "reference_scan",
    "refusal_scan",
    "research_ledger",
    "specificity_scan",
}

NOT_MEMBERS: Mapping[str, str] = MappingProxyType(
    {
        "corpus_census": "a census over the corpus, not a grader over a run",
        "filled_vitals_census": "migration requires the Finding rewrite reserved for its own ticket",
        "tracker_bodies": "format_report takes no show flag and its report is safe to paste",
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
    repeatable: bool = False


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
    diagnostics: tuple[str, ...] = ()
    reports: tuple[str, ...] = ()


@dataclass(frozen=True)
class EarlyExit:
    """A declared non-grader mode, such as a separated-reader brief."""

    status: int
    stdout: tuple[str, ...] = ()
    stderr: tuple[str, ...] = ()


class SourceError(Exception):
    """A tier-1 failure: no run artifact was available to grade."""


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
    if len(positionals) != 1:
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
        print(str(failure), file=sys.stderr)
        return 2
    try:
        source = command.load(parsed)
    except SourceError as failure:
        print(str(failure), file=sys.stdout if command.source_error_to_stdout else sys.stderr)
        return 2

    result = command.grade(source, parsed)
    if isinstance(result, EarlyExit):
        for chunk in result.stdout:
            print(chunk, end="" if chunk.endswith("\n") else "\n")
        for line in result.stderr:
            print(line, file=sys.stderr)
        return result.status

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
