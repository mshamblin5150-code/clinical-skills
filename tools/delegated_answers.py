"""Grade a run's record of delegated answers against the written rules they cite.

When the clinician delegates a run's open questions, ADR 0309 ruling 1 limits a
delegated answer to the question kinds the skills name as his and settles every
other question by the written rule the run quotes; ruling 2 records each such
question, with that rule or ``none found``. A delegated answer is the orchestrator's answer to a
question the clinician delegated; it is never a ruling, which is an ADR's.

The record is ``<run>/delegated-answers.md``, one record per question::

    ## QUESTION: <the question as it arose>
    RULE: <repository path>: "<the governing sentence, verbatim>"
    ANSWER: <what the run did>
    NOTE: <exact note basename, or shift>
    SECTIONS: <section names separated by |; shift uses note.md#section>

``RULE: none found`` declares that no written rule governs the question; such an
answer is named to the clinician at the go-ahead. A quoted rule must be at least
``MIN_QUOTE_WORDS`` words and appear, whitespace-normalized, in the cited file of
the checkout running this grade, so a run cannot cite a rule that is not written.

``completion_gate`` grades at an explicit ``--submission`` and before an approval
ask; both clinical hosts add its unread answers to their one shared remainder.
The independent reader receives ``reader_brief``'s answer lines and current
section text; its separate ``answer-reader/read.json`` binds the answer file and
every section fingerprint. Reports print counts only: a question names a patient's
encounter and stays in the run directory. The complete boundary of a clean
result is ``delegated_answers.DECLARED_LIMITS``.
"""

from __future__ import annotations

import completion_checks
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from pathlib import Path

import run_grader
from run_record_reader import (read_handwritten_record, check_handwritten_text,
                               HandwrittenKind, DamagedRecord, damaged_record_result)


# The checkout running the grade: its skills are the rules this run was bound by.
CHECKOUT = Path(__file__).resolve().parent.parent


EXPECTED_ROW = "the delegated answers"
RECORD = "delegated-answers.md"
RECORD_KIND = HandwrittenKind("delegated-answers", decode_errors="replace")
NONE_FOUND = "none found"
# Where a governing rule may be written. A rule anywhere else is not one a run
# was bound by.
RULE_ROOTS = ("skills/", "reference/", "docs/adr/", "AGENTS.md")
# A governing sentence, not a word: a one-word fragment appears in any file.
MIN_QUOTE_WORDS = 6

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
    (
        "the answer reader's judgment",
        "A current separate-context verdict is recorded evidence, not proof that the reader's agrees or disagrees judgment is correct or that its declared route is truthful.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "note-section recognition",
        "Pointers resolve unique Markdown or standalone colon headings, with Subjective/Objective/Assessment/Plan aliases and standalone labels nested inside their SOAP section; other heading forms cannot be located by this reader.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "the clinician reading the answer quotes",
        "The shared main-session transcript reader compares whitespace-folded complete ANSWER lines in the answer file's change-to-reply window; it proves the lines were shown, not clinician attention or text shown outside chat.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
)

HEADING = re.compile(r"(?m)^## QUESTION:[ \t]*(\S.*)?$")
FIELD = re.compile(r"(?m)^(RULE|ANSWER|NOTE|SECTIONS):[ \t]*(.*)$")
QUOTED_RULE = re.compile(r'^(\S+?):\s*"(.+)"\s*$', re.DOTALL)
NOTE_SECTIONS = "delegated_answers:note-sections"
ANSWER_READER = "delegated_answers:answer-reader"
READER_RECORD = "answer-reader/read.json"
EXPECTED_CHECKS = ("note-sections", "answer-reader", "shown-answers")


@dataclass(frozen=True)
class Answer:
    ordinal: int
    line: str
    sections: tuple[tuple[str, str], ...]


def _fields(record: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for match in FIELD.finditer(record):
        result.setdefault(match.group(1), []).append(match.group(2).strip())
    return result


def _section_name(value: str) -> str:
    value = value.strip("#*_ :\t").casefold()
    return {"subjective": "s", "objective": "o", "assessment": "a", "plan": "p"}.get(value, value)


def section_texts(text: str) -> dict[str, str]:
    """Read unique Markdown or standalone colon headings, retaining section bytes."""
    lines = text.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []
    end = len(lines)
    fence = None
    for index, line in enumerate(lines):
        plain = line.strip()
        if plain.startswith(("```", "~~~")):
            fence = None if fence == plain[0] else plain[0]
            continue
        if fence:
            continue
        if re.match(r"^(?:#{1,6}\s*)?(?:Coding worksheet|Medatrax entry|Tier block|Drift matrix|Drift verdicts)\b", plain, re.I):
            end = index
            break
        markdown = re.fullmatch(r"(#{1,6})\s+(.+)", plain)
        label = plain.strip("*_")
        if markdown:
            headings.append((index, len(markdown[1]), _section_name(markdown[2])))
        elif re.fullmatch(r"[A-Za-z][A-Za-z /&-]*:", label):
            name = _section_name(label)
            level = 1 if name in {"s", "o", "a", "p"} else next(
                (depth + 1 for _, depth, parent in reversed(headings) if parent in {"s", "o", "a", "p"}), 1)
            headings.append((index, level, name))
    result = {}
    for position, (start, level, name) in enumerate(headings):
        if sum(other == name for _, _, other in headings) != 1:
            continue
        stop = next((at for at, depth, _ in headings[position + 1:] if depth <= level), end)
        result[name] = "".join(lines[start:stop])
    return result


def answer_sections(run: Path, text: str) -> tuple[tuple[Answer, ...], tuple[str, ...]]:
    """Resolve pointers only through the shared run-artifact population."""
    notes = {artifact.path.name: artifact.text for artifact in run_grader.read_run_artifacts(run)}
    answers = []
    problems = []
    for ordinal, record in enumerate(records(text), 1):
        fields = _fields(record)
        if any(len(fields.get(name, ())) != 1 or not fields[name][0] for name in ("NOTE", "SECTIONS", "ANSWER")):
            problems.append(f"record {ordinal}: note/section pointers must appear once with values")
            continue
        note = fields["NOTE"][0]
        pointers = fields["SECTIONS"][0].split(" | ")
        selected = []
        for pointer in pointers:
            if note == "shift":
                filename, separator, section = pointer.partition("#")
            else:
                filename, separator, section = note, "#", pointer
            sections = section_texts(notes[filename]) if filename in notes else {}
            value = sections.get(_section_name(section)) if separator else None
            if value is None:
                problems.append(f"record {ordinal}: note/section pointer does not resolve")
            else:
                selected.append((filename + "#" + _section_name(section), value))
        if selected and len(selected) == len(pointers):
            line = next(match.group(0).rstrip("\r") for match in FIELD.finditer(record) if match.group(1) == "ANSWER")
            answers.append(Answer(ordinal, line, tuple(selected)))
    return tuple(answers), tuple(problems)


def _section_digests(answer: Answer) -> dict[str, str]:
    return {pointer: sha256(text.encode("utf-8")).hexdigest() for pointer, text in answer.sections}


def reader_brief(run: Path) -> dict:
    """Give the separate reader answer lines and their current sections, never rules."""
    raw = (run / RECORD).read_bytes()
    text = check_handwritten_text(raw.decode("utf-8"), run / RECORD, "raw-text").require_text(force=True)
    answers, problems = answer_sections(run, text)
    if problems:
        raise ValueError("delegated answer note/section pointers do not resolve")
    return {
        "answers_sha256": sha256(raw).hexdigest(),
        "answers": [{"answer": answer.ordinal, "line": answer.line,
                     "sections": [{"pointer": pointer, "text": text,
                                   "sha256": sha256(text.encode("utf-8")).hexdigest()}
                                  for pointer, text in answer.sections]}
                    for answer in answers],
    }


def _unique_fields(pairs: list[tuple[str, object]]) -> dict:
    fields = {}
    for name, value in pairs:
        if name in fields:
            raise ValueError("duplicate answer-reader field")
        fields[name] = value
    return fields


def reader_verdicts(
    run: Path, answers: tuple[Answer, ...], *, artifact: str | None = None, force: bool = False
) -> tuple[int, int, int]:
    """Count current agreements/disagreements and every unread answer once."""
    try:
        text = read_handwritten_record(run / READER_RECORD, "json").require_text(artifact=artifact, force=force)
        payload = json.loads(text, object_pairs_hook=_unique_fields)
        if (not isinstance(payload, dict) or set(payload) != {"route", "answers_sha256", "answers"}
                or payload["answers_sha256"] != sha256((run / RECORD).read_bytes()).hexdigest()
                or payload["route"] not in {"separate context", "not run - no second context"}
                or not isinstance(payload["answers"], list)):
            raise ValueError("invalid answer-reader container")
        if payload["route"] == "not run - no second context":
            return 0, 0, len(answers)
        rows = {}
        for row in payload["answers"]:
            if (not isinstance(row, dict) or set(row) != {"answer", "sections", "verdict", "disagreement"}
                    or type(row["answer"]) is not int or row["answer"] in rows
                    or row["answer"] not in {answer.ordinal for answer in answers}
                    or row["verdict"] not in {"agrees", "disagrees"}
                    or not isinstance(row["sections"], dict)
                    or not isinstance(row["disagreement"], str)
                    or (row["verdict"] == "disagrees" and not row["disagreement"].strip())):
                raise ValueError("invalid answer-reader verdict")
            rows[row["answer"]] = row
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RecursionError):
        return 0, 0, len(answers)
    agreed = disagreed = unread = 0
    for answer in answers:
        row = rows.get(answer.ordinal)
        if row is None or row["sections"] != _section_digests(answer):
            unread += 1
        elif row["verdict"] == "disagrees":
            disagreed += 1
        else:
            agreed += 1
    return agreed, disagreed, unread


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
    if len(quote.split()) < MIN_QUOTE_WORDS:
        return f"RULE quotes fewer than {MIN_QUOTE_WORDS} words, not a governing sentence"
    if not path.startswith(RULE_ROOTS) or ".." in Path(path).parts:
        return "RULE cites a file outside skills/, reference/, docs/adr/ or AGENTS.md"
    source = root / path
    if not source.is_file():
        return "RULE cites a file that does not exist"
    written = source.read_text(encoding="utf-8", errors="replace")
    if _normalized(quote) not in _normalized(written):
        return "RULE quotes a sentence the cited file does not contain"
    return None


def grade_text(text: str, root: Path) -> tuple[int, int, int, list[str]]:
    """Records, rule-settled records, none-found records, and findings."""
    found = records(text)
    settled = none = 0
    findings: list[str] = []
    for ordinal, record in enumerate(found, 1):
        heading = HEADING.match(record)
        fields = _fields(record)
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
    run: Path, submission: str | None, root: Path | None = None, *, pre_approval: bool = False
) -> tuple[bool, str, int]:
    """Grade the run's delegated-answer record at an explicit terminal submission."""
    frozen = completion_checks.exemption(run, submission, "delegated_answers", "delegated answers") if not pre_approval else None
    if frozen is not None:
        return False, frozen, 0
    if submission is None:
        return False, f"{EXPECTED_ROW}: {run_grader.NOT_GRADED} - --submission was not supplied", 0
    path = run / RECORD
    if not path.is_file():
        return False, f"{EXPECTED_ROW}: none recorded - {RECORD} is absent", 0
    try:
        text = read_handwritten_record(path, RECORD_KIND).require_text(artifact=submission, force=pre_approval)
    except DamagedRecord as failure:
        finding, report = damaged_record_result(failure, check=EXPECTED_ROW, artifact=submission, force=pre_approval)
        return finding, report, 0
    total, settled, none, findings = grade_text(
        text,
        root or CHECKOUT,
    )
    answers = ()
    if completion_checks.active(NOTE_SECTIONS):
        answers, pointers = answer_sections(run, text)
        findings.extend(pointers)
    agreed = disagreed = unread = 0
    if completion_checks.active(ANSWER_READER):
        try:
            agreed, disagreed, unread = reader_verdicts(run, answers, artifact=submission, force=pre_approval)
        except DamagedRecord as failure:
            _, report = damaged_record_result(failure, check="the delegated answer reader", artifact=submission, force=pre_approval)
            findings.append(report)
    counts = (
        f"{total} recorded, {settled} settled by a quoted written rule,"
        f" {none} with no governing rule to name at the go-ahead"
    )
    if not total:
        return True, f"{EXPECTED_ROW}: finding - {RECORD} holds no QUESTION record", 0
    if findings:
        return True, f"{EXPECTED_ROW}: finding - {counts}; " + "; ".join(findings), unread
    if completion_checks.active(ANSWER_READER):
        counts += f"; answer reader agrees {agreed}, disagrees {disagreed}, unread answers {unread}"
    if disagreed:
        return True, f"{EXPECTED_ROW}: finding - {counts}", unread
    return False, f"{EXPECTED_ROW}: " + ("incomplete - " if unread else "clean - ") + counts, unread


def pre_approval(run: Path, submission: str, status: int, report: str) -> tuple[int, str]:
    """Apply the same answer gate before the ask, preserving one combined remainder."""
    if not completion_checks.active(ANSWER_READER) or not (run / RECORD).exists():
        return status, report
    finding, answer_report, unread = completion_gate(run, submission, pre_approval=True)
    lines = [line for line in report.splitlines() if not line.startswith(EXPECTED_ROW + ":")]
    remainders = [index for index, line in enumerate(lines) if re.match(r"^unread remainder \d+", line)]
    if len(remainders) > 1:
        raise ValueError("the paired grade has more than one unread remainder")
    if remainders:
        index = remainders[0]
        lines[index] = re.sub(r"(?<=unread remainder )\d+", lambda match: str(int(match[0]) + unread), lines[index], count=1)
    elif unread:
        lines.append(run_grader.format_unread_remainder(unread))
    lines.append(answer_report)
    return (1 if finding or status == 1 else 2 if unread or status == 2 else status), "\n".join(lines)


def verify_shown_answers(run: Path, reply_at: float | None, *, transcripts=None):
    """Verify physical ANSWER lines using the record's own last-change window."""
    from approval_record import ReplyVerification, assistant_text
    path = run / RECORD
    if not completion_checks.active("delegated_answers:shown-answers") or not path.exists():
        return ReplyVerification("exempt", "no current delegated answer quotes owed")
    if reply_at is None:
        return ReplyVerification("unreadable", "delegated answer transcript not verified")
    try:
        text = read_handwritten_record(path, "raw-text").require_text(force=True)
        required = tuple(_normalized(match.group(0)) for match in FIELD.finditer(text) if match.group(1) == "ANSWER")
        boundary = path.stat().st_mtime
    except (OSError, UnicodeError):
        return ReplyVerification("unreadable", "delegated answer record not verified")
    shown, unread = assistant_text(run, after=boundary, before=reply_at, transcripts=transcripts)
    if unread:
        return ReplyVerification("unreadable", "delegated answer transcript not verified")
    visible = {_normalized(line) for message in shown for line in message.splitlines()}
    missing = sum(line not in visible for line in required)
    if missing:
        return ReplyVerification("not found", f"delegated answer lines were not shown: {missing} missing")
    return ReplyVerification("verified", "every recorded delegated answer line was shown")
