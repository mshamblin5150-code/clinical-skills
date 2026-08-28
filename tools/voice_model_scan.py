#!/usr/bin/env python3
"""Grade the mechanical shape of one private voice model.

    python tools/voice_model_scan.py [<voice-model.md>] [--show]

With no path, the command reads the account-owned model through
``repo_root.scratch_root()``. The default report contains counts only. ``--show``
prints finding detail from private working material and must not be pasted.

Exit 0 means the reached shape rows are clean, 1 means at least one shape
finding, and 2 means no model was scanned. A finding wins over incomplete
coverage, so a malformed tail cannot hide a defect already established in a
register the command could read.

The command grades shape, never whether the model sounds like its clinician.
``NOT_REACHED`` is the single inventory of those declared limits. The clinician
confirmation required by ``voice.md`` section 9 remains the verification of the
model's truth.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import repo_root
import run_grader


VOICE_SPEC = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "practicum-case-study"
    / "reference"
    / "voice.md"
)
NOT_REACHED = {
    "model-truth": "whether the modeled observations and pairs are true of the clinician",
    "quotation-provenance": "whether quoted text came from the source the model names",
    "invoked-source-fit": "whether the named domain and property are accurate or load-bearing",
    "register-candidate": "a malformed register heading that does not begin with a level-two Register label",
}

INVALID_INVOCATION = "invalid invocation"
MODEL_ABSENT = "voice model absent"
SPEC_UNAVAILABLE = "voice model specification unavailable"
REQUIRED_ITEMS_UNREADABLE = "required item vocabulary unreadable"
NO_REGISTER_SHAPE = "no register shape read"
INCOMPLETE_REGISTER_SHAPE = "not every register could be read"
EXIT_2_LIMBS = (
    INVALID_INVOCATION,
    MODEL_ABSENT,
    SPEC_UNAVAILABLE,
    REQUIRED_ITEMS_UNREADABLE,
    NO_REGISTER_SHAPE,
    INCOMPLETE_REGISTER_SHAPE,
)

SECTION_FOUR = re.compile(
    r"^## 4\. Reading a sample into a model\s*$"
    r"(?P<body>.*?)"
    r"^### The two-sample rule\s*$",
    re.MULTILINE | re.DOTALL,
)
NUMBERED_ITEM = re.compile(
    r"^\d+\. \*\*(?P<name>.+?)\.\*\*"
    r"(?: <!-- voice-model-scan: (?P<role>[a-z-]+) -->)?",
    re.MULTILINE,
)
REGISTER_NAMES = {
    "1": "clinical argument",
    "2": "spoken patient education",
    "3": "reflective and argumentative prose",
}
REGISTER_CANDIDATE = re.compile(
    r"^##[ \t]+Register\b(?P<rest>[^\n]*)$",
    re.MULTILINE | re.IGNORECASE,
)
REGISTER_SHAPE = re.compile(
    r"^[ \t]+(?P<number>[123])[ \t]+—[ \t]+(?P<name>[^\n]+?)[ \t]*$",
)
OBSERVATIONS = re.compile(
    r"^### Observations\s*$\n(?P<body>.*?)(?=^### Discriminating pairs\s*$|^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
PAIRS = re.compile(
    r"^### Discriminating pairs\s*$\n(?P<body>.*?)(?=^### Coverage\s*$|^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
OBSERVATION = re.compile(
    r"^(?P<number>\d+)\. \*\*(?P<title>.+?)\*\*[^\n]*\n"
    r"(?P<body>.*?)(?=^\d+\. \*\*|\Z)",
    re.MULTILINE | re.DOTALL,
)
PAIR = re.compile(
    r"^\*\*(?P<name>[^*\n]+)\.\*\*[^\n]*\n(?P<body>.*?)(?=^\*\*[^*\n]+\.\*\*|\Z)",
    re.MULTILINE | re.DOTALL,
)
GENERIC = re.compile(r"^\s*- \*Generic(?:\s*\([^)]*\))?\*:\s*\S", re.MULTILINE | re.IGNORECASE)
HIS = re.compile(r'^\s*- \*His(?:\s*\([^)]*\))?\*:\s*["“]\S', re.MULTILINE | re.IGNORECASE)
QUOTE = re.compile(r"^\s*>\s*\S", re.MULTILINE)
DOMAIN = re.compile(r"^\s*Domain:\s*(?P<value>\S.*?)\s*$", re.MULTILINE | re.IGNORECASE)
PROPERTY = re.compile(r"^\s*Property:\s*(?P<value>\S.*?)\s*$", re.MULTILINE | re.IGNORECASE)


def read_required_item_records(text: str) -> tuple[tuple[str, str | None], ...]:
    """Read ``(name, machine role)`` rows from section 4 once."""
    section = SECTION_FOUR.search(text)
    if section is None:
        return ()
    return tuple(
        (match.group("name"), match.group("role"))
        for match in NUMBERED_ITEM.finditer(section.group("body"))
    )


def read_required_items(text: str) -> tuple[str, ...]:
    """Read the numbered observation vocabulary published by ``voice.md``."""
    return tuple(name for name, _role in read_required_item_records(text))


def read_required_roles(text: str) -> dict[str, str]:
    """Read machine roles attached to section 4's numbered item vocabulary."""
    return {
        role: name
        for name, role in read_required_item_records(text)
        if role is not None
    }


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    detail: str


@dataclass(frozen=True)
class Scan:
    register_headings: int
    registers: int
    unread_registers: int
    observations: int
    pairs: int
    invoked_observations: int
    required_items_read: bool
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class Source:
    path: Path
    text: str
    spec_text: str


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().rstrip(".")).casefold()


def survey(text: str, spec_text: str) -> Scan:
    """Read the model's three public register sections and their shape rows."""
    findings: list[Finding] = []
    required_records = read_required_item_records(spec_text)
    required_items = tuple(name for name, _role in required_records)
    required_roles = {role: name for name, role in required_records if role is not None}
    invoked_item = required_roles.get("invoked-source")
    required_items_read = bool(required_items and invoked_item)

    headings = list(REGISTER_CANDIDATE.finditer(text))
    registers: list[tuple[str, str]] = []
    unread_registers = 0
    seen_registers: set[str] = set()
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        seen_once = text.find("\n## Seen once", heading.end(), end)
        if seen_once >= 0:
            end = seen_once
        body = text[heading.end():end]
        shape = REGISTER_SHAPE.fullmatch(heading.group("rest"))
        if shape is None:
            unread_registers += 1
            findings.append(Finding("unread-register", f"unrecognized register heading at physical position {index + 1}"))
            continue
        number = shape.group("number")
        name = shape.group("name")
        if REGISTER_NAMES.get(number) != name or number in seen_registers:
            unread_registers += 1
            detail = "duplicate" if number in seen_registers else "unrecognized"
            findings.append(Finding("unread-register", f"{detail} register heading at physical position {index + 1}"))
            continue
        seen_registers.add(number)
        registers.append((number, body))

    if headings:
        for number in ("1", "2", "3"):
            if number not in seen_registers:
                findings.append(Finding("missing-register", f"register {number} is absent"))

    observation_count = 0
    pair_count = 0
    invoked_count = 0
    invoked_name = _normalize(invoked_item or "")
    for number, body in registers:
        observations_match = OBSERVATIONS.search(body)
        if observations_match is None:
            findings.append(Finding("missing-observations", f"register {number} has no Observations section"))
        else:
            observations = list(OBSERVATION.finditer(observations_match.group("body")))
            observation_count += len(observations)
            if not observations:
                findings.append(Finding("missing-observations", f"register {number} carries no observations"))
            for observation in observations:
                title = observation.group("title")
                observation_body = observation.group("body")
                if QUOTE.search(observation_body) is None:
                    findings.append(
                        Finding(
                            "observation-without-quote",
                            f"register {number} observation {observation.group('number')} carries no quote",
                        )
                    )
                if invoked_name and _normalize(title) == invoked_name:
                    invoked_count += 1
                    if DOMAIN.search(observation_body) is None:
                        findings.append(Finding("invoked-domain", f"register {number} invoked-source observation has no domain"))
                    if PROPERTY.search(observation_body) is None:
                        findings.append(Finding("invoked-property", f"register {number} invoked-source observation has no property"))

        pairs_match = PAIRS.search(body)
        if pairs_match is None:
            findings.append(Finding("missing-pairs", f"register {number} has no Discriminating pairs section"))
            continue
        pairs = list(PAIR.finditer(pairs_match.group("body")))
        pair_count += len(pairs)
        if len(pairs) < 2:
            findings.append(Finding("pair-floor", f"register {number} carries fewer than two discriminating pairs"))
        for pair in pairs:
            if GENERIC.search(pair.group("body")) is None:
                findings.append(Finding("pair-generic", f"register {number} pair {pair.group('name')} has no Generic half"))
            if HIS.search(pair.group("body")) is None:
                findings.append(Finding("pair-his", f"register {number} pair {pair.group('name')} has no His half"))

    if registers and required_items_read and invoked_count == 0:
        findings.append(Finding("invoked-observation", "no invoked-source observation names what it spends"))

    return Scan(
        register_headings=len(headings),
        registers=len(registers),
        unread_registers=unread_registers,
        observations=observation_count,
        pairs=pair_count,
        invoked_observations=invoked_count,
        required_items_read=required_items_read,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = [
        "voice model: ACTIVE",
        f"source: {source}",
        f"register headings: {scan.register_headings}",
        f"registers: {scan.registers}",
        f"unread register headings: {scan.unread_registers}",
        f"observations: {scan.observations}",
        f"discriminating pairs: {scan.pairs}",
        f"invoked-source observations: {scan.invoked_observations}",
        f"findings: {len(scan.findings)}",
    ]
    if show:
        lines.extend(f"- {finding.kind}: {finding.detail}" for finding in scan.findings)
        lines.append("--show output is private working material; do not paste it.")
    return "\n".join(lines)


def _load(parsed: run_grader.Parsed) -> Source:
    path = Path(parsed.source)
    if not path.is_file():
        raise run_grader.SourceError(
            f"voice model: NOT RUN -- no model at {path}; voice unmodeled",
            exit_2_limb=MODEL_ABSENT,
        )
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as failure:
        raise run_grader.SourceError(
            f"voice model: NOT RUN -- could not read {path}: {failure}; voice unmodeled",
            exit_2_limb=MODEL_ABSENT,
        ) from failure
    try:
        spec_text = VOICE_SPEC.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as failure:
        raise run_grader.SourceError(
            f"voice model: NOT RUN -- could not read the tracked voice specification: {failure}",
            exit_2_limb=SPEC_UNAVAILABLE,
        ) from failure
    return Source(path, text, spec_text)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source.text, source.spec_text)
    no_registers = scan.register_headings == 0
    incomplete = scan.register_headings > 0 and (
        scan.registers != len(REGISTER_NAMES) or scan.unread_registers > 0
    )
    required_items_unreadable = not scan.required_items_read
    limbs = tuple(
        limb
        for condition, limb in (
            (required_items_unreadable, REQUIRED_ITEMS_UNREADABLE),
            (no_registers, NO_REGISTER_SHAPE),
            (incomplete, INCOMPLETE_REGISTER_SHAPE),
        )
        if condition
    )
    diagnostics = ()
    if limbs:
        diagnostics = ("voice model shape was not completely scanned",)
    return run_grader.Grade(
        scan=scan,
        source=source.path.name,
        findings_failed=bool(scan.findings),
        coverage_failed=bool(limbs),
        coverage_limbs=limbs,
        diagnostics=diagnostics,
    )


GRADER = run_grader.Grader(
    usage="usage: voice_model_scan.py [<voice-model.md>] [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
    allow_extra_positionals=False,
    exit_2_limbs=EXIT_2_LIMBS,
    invalid_invocation_limb=INVALID_INVOCATION,
)


def main(argv: list[str]) -> int:
    """Run the grader; an omitted path resolves the durable account model."""
    arguments = list(argv)
    if not any(not argument.startswith("-") for argument in arguments):
        arguments.insert(0, str(repo_root.scratch_root() / "voice-model.md"))
    return run_grader.run(GRADER, arguments)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
