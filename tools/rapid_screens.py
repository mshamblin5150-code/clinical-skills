"""Profile-selected rapid-screen row shared by both clinical completion graders."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import completion_checks
import medatrax_posting
import note_grammar
from run_record_reader import UnreadableRecord, mark_not_graded


CHECK = "rapid_screens:pending"
EXPECTED_ROW = "pending"
DECLARATION = "Rapid screens: negative unless stated"
DECLARED_LIMITS = (
    "The caller supplies --profile; omission is reported not graded without opening account files. The opt-in is one complete line Rapid screens: negative unless stated, ignoring case and double-asterisk bold markers; other declarations are not inferred.",
    "Candidates name strep/streptococcus/streptococcal, influenza/flu, COVID-19/COVID or RSV with rapid, screen, antigen or POCT in one physical clause. Other test names and wordings remain outside this vocabulary check.",
    "Clauses end at commas, semicolons or sentence-ending punctuation, or at and/but before another named test assertion. Influenza A and B remains one name. The shared note_grammar reader locates the four SOAP sections and their closer; missing or ambiguous sections leave one note unread. Markup is preserved. Actual test performance and results remain readings.",
    "Pending, awaiting a result/results, unresulted and no result are recognized. Clauses declaring not performed, not done, not run, declined or refused, or naming culture, PCR or send-out, are outside the refusal.",
    "Only numbered batch notes, an explicit standalone --note, or the existing approved standalone source population are read; no resolved population is incomplete coverage.",
)
TEST = re.compile(r"\b(?:strep(?:tococc(?:us|al))?|influenza|flu|covid(?:-19)?|rsv)\b", re.I)
SCREEN = re.compile(r"\b(?:rapid|screens?|antigen|poct)\b", re.I)
PENDING = re.compile(r"\b(?:pending|awaiting\s+(?:(?:a|the)\s+)?results?|unresulted|no\s+results?)\b", re.I)
EXCLUDED = re.compile(r"\b(?:not\s+(?:performed|done|run)|declined|refused|culture|pcr|send[- ]out)\b", re.I)
ASSERTION_BREAK = re.compile(
    r"\s+(?:and|but)\s+(?=(?:rapid\b|screens?\b|antigen\b|poct\b|"
    + TEST.pattern + r"|(?:\w+\s+)?culture\b|pcr\b|send[- ]out\b))", re.I)


@dataclass(frozen=True)
class Result:
    state: str
    notes: int = 0
    candidates: int = 0
    findings: tuple[tuple[int, int], ...] = ()
    unread: int = 0

    @property
    def incomplete(self) -> bool:
        return self.state in {"unread", "dependency"} or bool(self.unread)


def read_note(text: str) -> tuple[int, tuple[int, ...]]:
    parsed = note_grammar.parse(text)
    offset = len(parsed.buckets['preamble'].splitlines())
    body = ''.join(parsed.buckets[label] for label in 'SOAP')
    candidates, pending = 0, []
    for number, line in enumerate(body.splitlines(), offset + 1):
        for clause in re.split(r"[,;]|(?<=[.!?])\s+", ASSERTION_BREAK.sub(";", line)):
            if TEST.search(clause) and SCREEN.search(clause):
                candidates += 1
                if PENDING.search(clause) and not EXCLUDED.search(clause):
                    pending.append(number)
    return candidates, tuple(pending)


def check(run: Path, *, batch: bool, note: Path | None = None,
          profile: Path | None = None) -> Result:
    if not completion_checks.active(CHECK):
        return Result("historical")
    if profile is None:
        return Result("unsupplied")
    try:
        profile_text = profile.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return Result("unread", unread=1)
    if not any(line.replace("**", "").strip().casefold() == DECLARATION.casefold()
               for line in profile_text.splitlines()):
        return Result("undeclared")
    try:
        paths = (note,) if note is not None else medatrax_posting.note_paths(run, batch=batch)
    except UnreadableRecord as failure:
        mark_not_graded(failure, check="rapid-screen note population")
        return Result("dependency")
    notes = candidates = unread = 0
    findings = []
    for number, source in enumerate(paths, 1):
        try:
            text = source.read_text(encoding="utf-8")
            count, pending = read_note(text)
        except (OSError, UnicodeError, ValueError):
            unread += 1
            continue
        notes += 1
        candidates += count
        findings.extend((number, line) for line in pending)
    return Result("active" if paths else "unread", notes, candidates, tuple(findings), unread)


def report(result: Result, *, show: bool = False) -> str:
    if result.state == "historical":
        return "rapid screens: not graded - check starts after approval"
    if result.state == "unsupplied":
        return "rapid screens: not graded - no --profile supplied"
    if result.state == "undeclared":
        return "rapid screens: not graded - profile has no rapid-screen declaration"
    if result.state == "unread":
        return "rapid screens: not checked - profile or note population unread"
    if result.state == "dependency":
        return "rapid screens: not graded - approved note population unread"
    lines = [f"rapid screens: notes read {result.notes}; candidates {result.candidates}; pending findings {len(result.findings)}"]
    if result.unread:
        lines.append(f"rapid screens: incomplete coverage - unread notes {result.unread}")
    if show:
        lines.extend(f"rapid screen: note {note}, line {line}: pending result" for note, line in result.findings)
    return "\n".join(lines)
