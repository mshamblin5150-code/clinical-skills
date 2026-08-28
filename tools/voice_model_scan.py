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
In particular, it cannot establish that a quotation came from the named sample,
that a discriminating pair captures a real distinction, that the invoked domain
or property is accurate, or that the property actually carries an argument.
The clinician confirmation required by ``voice.md`` section 9 remains the only
verification of the model's truth.
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
REQUIRED_ITEMS = (
    "Sentence rhythm",
    "Where the weight falls",
    "Lexicon that is his",
    "The characteristic move",
    "How uncertainty is carried",
    "How humor is built, and where it sits",
    "What he never does",
    "The invoked source and what it spends",
)

NOT_REACHED = {
    "model-truth": "whether the modeled observations and pairs are true of the clinician",
    "quotation-provenance": "whether quoted text came from the source the model names",
    "invoked-source-fit": "whether the named domain and property are accurate or load-bearing",
}

INVALID_INVOCATION = "invalid invocation"
MODEL_ABSENT = "voice model absent"
NO_REGISTER_SHAPE = "no register shape read"
INCOMPLETE_REGISTER_SHAPE = "not every register could be read"
EXIT_2_LIMBS = (
    INVALID_INVOCATION,
    MODEL_ABSENT,
    NO_REGISTER_SHAPE,
    INCOMPLETE_REGISTER_SHAPE,
)

SECTION_FOUR = re.compile(
    r"^## 4\. Reading a sample into a model\s*$"
    r"(?P<body>.*?)"
    r"^### The two-sample rule\s*$",
    re.MULTILINE | re.DOTALL,
)
NUMBERED_ITEM = re.compile(r"^\d+\. \*\*(?P<name>.+?)\.\*\*", re.MULTILINE)
REGISTER_NAMES = {
    "1": "clinical argument",
    "2": "spoken patient education",
    "3": "reflective and argumentative prose",
}
REGISTER = re.compile(
    r"^## Register (?P<number>[123]) — "
    r"(?:clinical argument|spoken patient education|reflective and argumentative prose)\s*$\n"
    r"(?P<body>.*?)(?=^## Register [123]\b|^## Seen once\b|\Z)",
    re.MULTILINE | re.DOTALL,
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


def read_required_items(text: str) -> tuple[str, ...]:
    """Read the numbered observation vocabulary published by ``voice.md``."""
    section = SECTION_FOUR.search(text)
    if section is None:
        return ()
    return tuple(match.group("name") for match in NUMBERED_ITEM.finditer(section.group("body")))


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    detail: str


@dataclass(frozen=True)
class Scan:
    registers: int
    observations: int
    pairs: int
    invoked_observations: int
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class Source:
    path: Path
    text: str


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().rstrip(".")).casefold()


def survey(text: str, spec_text: str) -> Scan:
    """Read the model's three public register sections and their shape rows."""
    findings: list[Finding] = []
    published = read_required_items(spec_text)
    if published != REQUIRED_ITEMS:
        findings.append(
            Finding(
                "required-items",
                "voice.md section 4 and the grader's required item vocabulary differ",
            )
        )

    registers = list(REGISTER.finditer(text))
    seen_registers = {match.group("number") for match in registers}
    if registers:
        for number in ("1", "2", "3"):
            if number not in seen_registers:
                findings.append(Finding("missing-register", f"register {number} is absent"))

    observation_count = 0
    pair_count = 0
    invoked_count = 0
    invoked_name = _normalize(REQUIRED_ITEMS[-1])
    for register in registers:
        number = register.group("number")
        body = register.group("body")
        opening = register.group(0).splitlines()[0]
        expected_opening = f"## Register {number} — {REGISTER_NAMES[number]}"
        if opening != expected_opening:
            findings.append(Finding("register-name", f"register {number} does not carry its fixed heading"))
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
                if _normalize(title) == invoked_name:
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

    if registers and invoked_count == 0:
        findings.append(Finding("invoked-observation", "no invoked-source observation names what it spends"))

    return Scan(
        registers=len(registers),
        observations=observation_count,
        pairs=pair_count,
        invoked_observations=invoked_count,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = [
        "voice model: ACTIVE",
        f"source: {source}",
        f"registers: {scan.registers}",
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
    return Source(path, text)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source.text, VOICE_SPEC.read_text(encoding="utf-8"))
    no_registers = scan.registers == 0
    incomplete = 0 < scan.registers < 3
    limbs = tuple(
        limb
        for condition, limb in (
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
