"""Grade a run's record of delegated answers against the written rules they cite.

When the clinician delegates a run's open questions, ADR 0309 ruling 1 limits a
delegated answer to the question kinds the skills name as his, and ruling 2
requires every other question to be settled by the written rule the run quotes or
recorded as having none. A delegated answer is the orchestrator's answer to a
question the clinician delegated; it is never a ruling, which is an ADR's.

The record is ``<run>/delegated-answers.md``, one record per question::

    ## QUESTION: <the question as it arose>
    RULE: <repository path>: "<the governing sentence, verbatim>"
    ANSWER: <what the run did>

``RULE: none found`` declares that no written rule governs the question; such an
answer is named to the clinician at the go-ahead. A quoted rule must appear,
whitespace-normalized, in the cited tracked file of the checkout running this
grade, so a run cannot cite a rule that is not written.

``completion_gate`` grades only at an explicit ``--submission``, beside the
after-action review row, and prints counts only: a question names a patient's
encounter and stays in the run directory. The complete boundary of a clean
result is ``delegated_answers.DECLARED_LIMITS``.
"""

from __future__ import annotations

import re
from pathlib import Path

import run_grader


# The checkout running the grade: its skills are the rules this run was bound by.
CHECKOUT = Path(__file__).resolve().parent.parent


EXPECTED_ROW = "the delegated answers"
RECORD = "delegated-answers.md"
NONE_FOUND = "none found"
# Where a governing rule may be written. A rule anywhere else is not one a run
# was bound by.
RULE_ROOTS = ("skills/", "reference/", "docs/adr/", "AGENTS.md")

DECLARED_LIMITS = (
    (
        "an unrecorded delegation",
        "A run that received a delegation and wrote no record reads as having none; the record's absence is reported, never graded.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "a rule the run did not find",
        "RULE: none found is accepted as written, so a governing rule the run missed is caught only where a mechanical row, such as the BMI row, grades the content it governs.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether the answer follows the quoted rule",
        "The grader proves a quoted rule is written, not that the answer obeys it; that comparison is the clinician's at the go-ahead.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
)

HEADING = re.compile(r"(?m)^## QUESTION:[ \t]*(\S.*)?$")
FIELD = re.compile(r"(?m)^(RULE|ANSWER):[ \t]*(.*)$")
QUOTED_RULE = re.compile(r'^(\S+?):\s*"(.+)"\s*$', re.DOTALL)


def _normalized(text: str) -> str:
    return " ".join(text.split())


def records(text: str) -> list[str]:
    """Each record's text, heading included, in file order."""
    starts = [match.start() for match in HEADING.finditer(text)]
    return [text[start:end] for start, end in zip(starts, starts[1:] + [len(text)])]


def rule_finding(rule: str, root: Path) -> str | None:
    """Why one RULE value fails, or ``None`` where it is ``none found`` or written."""
    if rule.casefold() == NONE_FOUND:
        return None
    match = QUOTED_RULE.match(rule)
    if match is None:
        return 'RULE is neither "none found" nor a path and a quoted sentence'
    path, quote = match.group(1), match.group(2)
    if not path.startswith(RULE_ROOTS) or ".." in Path(path).parts:
        return "RULE cites a file outside skills/, reference/, docs/adr/ or AGENTS.md"
    source = root / path
    if not source.is_file():
        return "RULE cites a file that does not exist"
    if _normalized(quote) not in _normalized(source.read_text(encoding="utf-8")):
        return "RULE quotes a sentence the cited file does not contain"
    return None


def grade_text(text: str, root: Path) -> tuple[int, int, int, list[str]]:
    """Records, rule-settled records, none-found records, and findings."""
    found = records(text)
    settled = none = 0
    findings: list[str] = []
    for ordinal, record in enumerate(found, 1):
        heading = HEADING.match(record)
        fields: dict[str, list[str]] = {}
        for match in FIELD.finditer(record):
            fields.setdefault(match.group(1), []).append(match.group(2).strip())
        problems: list[str] = []
        if heading is None or heading.group(1) is None:
            problems.append("QUESTION is empty")
        for name in ("RULE", "ANSWER"):
            values = fields.get(name, [])
            if len(values) != 1 or not values[0]:
                problems.append(f"{name} must appear once with a value")
        rule = fields.get("RULE", [""])[0]
        if len(fields.get("RULE", [])) == 1 and rule:
            why = rule_finding(rule, root)
            if why:
                problems.append(why)
            elif rule.casefold() == NONE_FOUND:
                none += 1
            else:
                settled += 1
        findings.extend(f"record {ordinal}: {problem}" for problem in problems)
    return len(found), settled, none, findings


def completion_gate(
    run: Path, submission: str | None, root: Path | None = None
) -> tuple[bool, str]:
    """Grade the run's delegated-answer record at an explicit terminal submission."""
    if submission is None:
        return False, f"{EXPECTED_ROW}: {run_grader.NOT_GRADED} - --submission was not supplied"
    path = run / RECORD
    if not path.is_file():
        return False, f"{EXPECTED_ROW}: none recorded - {RECORD} is absent"
    total, settled, none, findings = grade_text(
        path.read_text(encoding="utf-8", errors="replace"),
        root or CHECKOUT,
    )
    counts = (
        f"{total} recorded, {settled} settled by a quoted written rule,"
        f" {none} with no governing rule to name at the go-ahead"
    )
    if not total:
        return True, f"{EXPECTED_ROW}: finding - {RECORD} holds no QUESTION record"
    if findings:
        return True, f"{EXPECTED_ROW}: finding - {counts}; " + "; ".join(findings)
    return False, f"{EXPECTED_ROW}: clean - {counts}"
