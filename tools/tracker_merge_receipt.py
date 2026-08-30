"""Plan immutable ticket receipts for a pull request merged into ``main``.

Tracker prose written from a branch is true in one tree and read from another.
This command does not guess which prose is an assertion. It reads the explicit
ticket bindings the maintainer already puts on their own lines in a pull request
and emits one JSON object per ticket for the workflow to publish::

    Closes #290
    Part of #298
    Implements #300's lead 2

Usage::

    gh pr view 401 --json number,url,title,body,baseRefName,mergedAt,mergeCommit,commits |
        python tools/tracker_merge_receipt.py -

Exit 0 means the plan contains a binding or a reasoned no-ticket declaration.
Exit 1 means the plan is empty or a reference-shaped line was declined. Exit 2
means the input could not establish a completed merge into ``main``. Use
``--check-plan`` before merge to grade bindings without requiring merge data.
The command opens no socket and mutates nothing; its JSON-lines output is the
bounded plan consumed by ``.github/workflows/tracker.yml``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

from console_codec import use_utf8


class ReferenceAlternative(NamedTuple):
    name: str
    pattern: str
    example: str


# Historical measurement on 2026-08-27 at cea7963 (ADR 0051): across 47 open
# ticket bodies and 35 pull-request bodies, decision + number appeared 51
# times, option + number 12 times, and lead + number 0 times.
UNIT_NOUNS = ("decision", "decisions", "option", "options", "lead", "leads")
TERMINAL_PUNCTUATION = ".;:!?"
LINE_DECORATION = (
    r"[ \t]*(?:>[ \t]*)?(?:(?:[-+*]|[0-9]+[.)])[ \t]+)?"
)
EMPHASIS_DECORATION = r"(?:\*{1,3}|_{1,3})"


def _owned_line(
    body: str,
    trailer: str,
    emphasis_group: str,
    terminal_punctuation: str = "",
) -> str:
    prefix = (
        rf"(?im)^{LINE_DECORATION}"
        rf"(?P<{emphasis_group}>{EMPHASIS_DECORATION})?"
        rf"(?:{body}){trailer}"
    )
    if not terminal_punctuation:
        ending = rf"(?({emphasis_group})(?P={emphasis_group}))"
    else:
        punctuation = f"[{re.escape(terminal_punctuation)}]"
        ending = (
            rf"(?({emphasis_group})"
            rf"(?:{punctuation}?(?P={emphasis_group})|"
            rf"(?P={emphasis_group}){punctuation})"
            rf"|{punctuation}?)"
        )
    return prefix + ending + r"[ \t\r]*$"


REFERENCE_ALTERNATIVES = (
    ReferenceAlternative("closes", r"Closes[ \t]+#(?P<closes>[0-9]+)", "Closes #530"),
    ReferenceAlternative("part", r"Part[ \t]+of[ \t]+#(?P<part>[0-9]+)", "Part of #530"),
    ReferenceAlternative(
        "implements",
        r"Implements[ \t]+#(?P<implements>[0-9]+)['’]s[ \t]+"
        rf"(?P<unit>{'|'.join(UNIT_NOUNS)})[ \t]+"
        r"(?P<unit_numbers>[0-9]+(?:[ \t]*(?:-|,)[ \t]*[0-9]+)*)",
        "Implements #530's decision 1",
    ),
)
REFERENCE = re.compile(
    _owned_line(
        "|".join(alternative.pattern for alternative in REFERENCE_ALTERNATIVES),
        r"(?P<extra_references>(?:[ \t]*,[ \t]*#[0-9]+)*)"
        r"[ \t]*",
        "reference_emphasis",
        TERMINAL_PUNCTUATION,
    )
)
NO_BINDING = re.compile(
    _owned_line(
        r"Binds[ \t]+no[ \t]+ticket:[ \t]*(?P<reason>\S(?:.*?\S)?)",
        "",
        "declaration_emphasis",
    )
)
REFERENCE_SHAPE = re.compile(
    r"(?i)(?:"
    r"Closes[ \t]+#[0-9]+(?:[ \t]*,[ \t]*#[0-9]+)*|"
    r"Part[ \t]+of[ \t]+#[0-9]+(?:[ \t]*,[ \t]*#[0-9]+)*|"
    r"Implements[ \t]+#[0-9]+['’]s(?:[ \t]+[A-Za-z]+)?"
    r"(?:[ \t]+[0-9]+(?:[ \t]*(?:-|,)[ \t]*[0-9]+)*)?|"
    r"Binds[ \t]+no[ \t]+ticket(?::[ \t]*[^\r\n]+)?"
    r")"
)
FULL_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
ISO_DAY = re.compile(r"^(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})T")
RECEIPT = re.compile(
    r"\AMerged into `main` by \[PR #(?P<number>[1-9][0-9]*)\]"
    r"\((?P<url>https://github\.com/[^/\s)]+/[^/\s)]+/pull/(?P=number))\) "
    r"at `(?P<sha>[0-9a-fA-F]{40})` on "
    r"(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})\. "
    r"Merge claim: `(?P<claim>[^`]+)`\. This immutable merge receipt "
    r"establishes that pull request's state; it does not make later names "
    r"or claims current\.\Z"
)


class Receipt(NamedTuple):
    ticket: int
    body: str


class Binding(NamedTuple):
    ticket: int
    claim: str


class ArtifactText(NamedTuple):
    name: str
    message: str
    text: str


class PlanLine(NamedTuple):
    source: str
    number: int
    text: str
    message: str


class BindingLine(NamedTuple):
    source: str
    number: int
    binding: Binding
    message: str


class MessageConflict(NamedTuple):
    message: str
    binding: BindingLine
    declaration: PlanLine


class PlanAssessment(NamedTuple):
    bindings: list[BindingLine]
    declarations: list[PlanLine]
    declined: list[PlanLine]

    @property
    def conflicts(self) -> list[MessageConflict]:
        conflicts = {}
        for binding in self.bindings:
            for declaration in self.declarations:
                if binding.message != declaration.message:
                    continue
                coordinates = (
                    binding.message,
                    binding.source,
                    binding.number,
                    declaration.source,
                    declaration.number,
                )
                conflicts.setdefault(
                    coordinates,
                    MessageConflict(binding.message, binding, declaration),
                )
        return list(conflicts.values())

    @property
    def status(self) -> int:
        if self.declined or self.conflicts:
            return 1
        if self.bindings or self.declarations:
            return 0
        return 1


def _text(record: dict[str, Any], field: str, source: str) -> str:
    value = record.get(field, "")
    if value is not None and not isinstance(value, str):
        raise ValueError(f"GitHub JSON field {source!r} must be text")
    return value or ""


def _artifact_sources(document: dict[str, Any]) -> list[ArtifactText]:
    sources = [ArtifactText("body", "body", _text(document, "body", "body"))]
    commits = document.get("commits", [])
    if commits is None:
        commits = []
    if not isinstance(commits, list):
        raise ValueError("GitHub JSON field 'commits' must be a list")
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            raise ValueError(f"GitHub JSON commits[{index}] must be an object")
        sources.append(
            ArtifactText(
                f"commits[{index}].messageHeadline",
                f"commits[{index}]",
                _text(commit, "messageHeadline", f"commits[{index}].messageHeadline"),
            )
        )
        sources.append(
            ArtifactText(
                f"commits[{index}].messageBody",
                f"commits[{index}]",
                _text(commit, "messageBody", f"commits[{index}].messageBody"),
            )
        )
    return sources


def _match_bindings(match: re.Match[str]) -> list[Binding]:
    extras = [
        int(value[1:])
        for value in re.findall(r"#[0-9]+", match.group("extra_references"))
    ]
    if match.group("closes"):
        tickets = [int(match.group("closes")), *extras]
        return [Binding(ticket, f"Closes #{ticket}") for ticket in tickets]
    if match.group("part"):
        tickets = [int(match.group("part")), *extras]
        return [Binding(ticket, f"Part of #{ticket}") for ticket in tickets]

    tickets = [int(match.group("implements")), *extras]
    noun = match.group("unit")
    numbers = re.sub(r"[ \t]+", " ", match.group("unit_numbers"))
    return [
        Binding(ticket, f"Implements #{ticket}'s {noun} {numbers}")
        for ticket in tickets
    ]


def _bindings(document: dict[str, Any]) -> list[Binding]:
    return sorted({line.binding for line in _binding_lines(document)})


def _binding_lines(document: dict[str, Any]) -> list[BindingLine]:
    found = []
    for source in _artifact_sources(document):
        for number, line in enumerate(source.text.splitlines(), start=1):
            if match := REFERENCE.fullmatch(line):
                found.extend(
                    BindingLine(source.name, number, binding, source.message)
                    for binding in _match_bindings(match)
                )
    return found


def assess_plan(document: Any) -> PlanAssessment:
    if not isinstance(document, dict):
        raise ValueError("GitHub JSON must be an object")

    bindings = _binding_lines(document)
    declarations = []
    declined = []
    for source in _artifact_sources(document):
        for number, line in enumerate(source.text.splitlines(), start=1):
            if declaration := NO_BINDING.fullmatch(line):
                declarations.append(
                    PlanLine(
                        source.name,
                        number,
                        declaration.group("reason"),
                        source.message,
                    )
                )
                continue
            if REFERENCE.fullmatch(line):
                continue
            if near_match := REFERENCE_SHAPE.search(line):
                declined.append(
                    PlanLine(
                        source.name,
                        number,
                        near_match.group(0).strip(),
                        source.message,
                    )
                )
    return PlanAssessment(bindings, declarations, declined)


def report_assessment(assessment: PlanAssessment) -> None:
    declaration_case = (
        "pull request also contains bindings"
        if assessment.bindings
        else "pull request contains no bindings"
    )
    for declaration in assessment.declarations:
        print(
            f"tracker-merge-receipt: {declaration.source} line "
            f"{declaration.number}: Binds no ticket ({declaration_case}): "
            f"{declaration.text}",
            file=sys.stderr,
        )
    if not assessment.bindings and not assessment.declarations:
        print("tracker-merge-receipt: finding: receipt plan is empty", file=sys.stderr)
    for conflict in assessment.conflicts:
        print(
            f"tracker-merge-receipt: finding: authored message {conflict.message} "
            f"has a binding at {conflict.binding.source} line "
            f"{conflict.binding.number} and a no-ticket declaration at "
            f"{conflict.declaration.source} line {conflict.declaration.number}",
            file=sys.stderr,
        )
    for line in assessment.declined:
        print(
            f"tracker-merge-receipt: finding: declined {line.source} line "
            f"{line.number}: {line.text}",
            file=sys.stderr,
        )


def render_receipt(number: int, url: str, sha: str, day: str, binding: Binding) -> str:
    return (
        f"Merged into `main` by [PR #{number}]({url}) at `{sha}` on {day}. "
        f"Merge claim: `{binding.claim}`. This immutable merge receipt "
        "establishes that pull request's state; it does not make later names "
        "or claims current."
    )


def parse_merge_receipt(body: str) -> Binding | None:
    """Return the binding from an exact canonical receipt, or ``None``."""
    match = RECEIPT.fullmatch(body)
    if match is None:
        return None
    claim_match = REFERENCE.fullmatch(match.group("claim"))
    if claim_match is None:
        return None
    bindings = _match_bindings(claim_match)
    if len(bindings) != 1:
        return None
    binding = bindings[0]
    canonical = render_receipt(
        int(match.group("number")),
        match.group("url"),
        match.group("sha"),
        match.group("day"),
        binding,
    )
    return binding if body == canonical else None


def plan_receipts(document: Any) -> list[Receipt]:
    if not isinstance(document, dict):
        raise ValueError("GitHub JSON must be an object")
    if document.get("baseRefName") != "main":
        raise ValueError("pull request base branch is not 'main'")

    merged_at = document.get("mergedAt")
    if not isinstance(merged_at, str) or not (day_match := ISO_DAY.match(merged_at)):
        raise ValueError("pull request is not merged with a dated merge event")

    merge_commit = document.get("mergeCommit")
    if not isinstance(merge_commit, dict):
        raise ValueError("pull request has no full merge commit")
    sha = merge_commit.get("oid")
    if not isinstance(sha, str) or not FULL_SHA.fullmatch(sha):
        raise ValueError("pull request has no full merge commit")

    number = document.get("number")
    url = document.get("url")
    if not isinstance(number, int) or number < 1:
        raise ValueError("pull request number must be a positive integer")
    if (
        not isinstance(url, str)
        or re.fullmatch(
            rf"https://github\.com/[^/\s)]+/[^/\s)]+/pull/{number}", url
        )
        is None
    ):
        raise ValueError("pull request URL must be a GitHub HTTPS URL")

    day = day_match.group("day")
    rows = []
    for binding in _bindings(document):
        body = render_receipt(number, url, sha, day, binding)
        rows.append(Receipt(binding.ticket, body))
    return rows


def _read(path: str) -> Any:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan ticket receipts for a pull request merged into main."
    )
    parser.add_argument(
        "--check-plan",
        action="store_true",
        help="grade bindings before merge without requiring merge metadata",
    )
    parser.add_argument("path", help="gh pr view JSON, or - for stdin")
    args = parser.parse_args(argv)

    try:
        document = _read(args.path)
        assessment = assess_plan(document)
        rows = [] if args.check_plan else plan_receipts(document)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"tracker-merge-receipt: could not grade input: {exc}", file=sys.stderr)
        return 2

    for row in rows:
        print(json.dumps(row._asdict(), ensure_ascii=False))
    report_assessment(assessment)
    return assessment.status


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
