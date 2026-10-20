"""Shared estimated visit-time check (ADR 0410).

The complete reading boundary is ``DECLARED_LIMITS``. Default output is counts
only; --show is private. Call check_pairs for field blocks not yet saved as notes.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import completion_checks
from console_codec import require_python_floor, use_utf8
import medatrax_posting
import run_grader
from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result

EXPECTED_ROW = "visit-times"
DECLARED_LIMITS = (
    "Visit complexity and even distribution across the shift remain reader judgments.",
    "Portal values are not compared with note values.",
    "Unlabeled times and tier-block restatements are neither graded nor counted unread.",
    "The candidate reader recognizes physical lines carrying Start time or End time; other labels are outside coverage.",
    "Shift evidence uses the shared handwritten reader before clock and duration parsing; damaged content withholds only the shift-window comparison while note-duration and spacing checks continue.",
)
CANDIDATE = re.compile(r"\b(start|end)[ \t]+time\b", re.I)
FIELD = re.compile(
    r"^[ \t]*(?:\|[ \t]*)?(?:\*\*)?(Start|End)[ \t]+time(?:\*\*)?"
    r"[ \t]*(?:[:|][ \t]*)?(\d{2}:?\d{2})(?=$|[ \t,|])"
    r"(?:[ \t]*,?[ \t]*(?:estimated|\(estimated\)))?[ \t]*\|?[ \t]*$", re.I
)


@dataclass(frozen=True)
class Result:
    notes: int = 0
    pairs: int = 0
    findings: tuple[str, ...] = ()
    unread: int = 0
    window_checked: bool = False
    population_checked: bool = True
    graded: bool = True
    damage_report: str = ""

    @property
    def incomplete(self) -> bool:
        return self.graded and bool(self.unread or self.pairs < self.notes or not self.window_checked or not self.population_checked)


def clock(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:?\d{2}", value):
        raise ValueError("unreadable clock")
    digits = value.replace(":", "")
    hours, minutes = int(digits[:2]), int(digits[2:])
    if hours > 23 or minutes > 59:
        raise ValueError("invalid clock")
    return hours * 60 + minutes


def read_pair(text: str) -> tuple[tuple[int, int] | None, int]:
    fields: dict[str, list[int]] = {"start": [], "end": []}
    unread = 0
    for line in text.splitlines():
        if not CANDIDATE.search(line):
            continue
        match = FIELD.fullmatch(line)
        if match is None:
            unread += 1
            continue
        try:
            fields[match[1].lower()].append(clock(match[2]))
        except ValueError:
            unread += 1
    if any(len(values) != 1 for values in fields.values()):
        unread += sum(len(values) for values in fields.values() if len(values) > 1)
        return None, unread
    return (fields["start"][0], fields["end"][0]), unread


def read_window(run: Path) -> tuple[int, int] | None:
    def decode(text: str) -> tuple[int, int]:
        value = json.loads(text)
        start = clock(value["start"])
        duration = value["duration"]
        hours, minutes = duration["hours"], duration["minutes"]
        if (type(hours) is not int or type(minutes) is not int
                or hours < 0 or not 0 <= minutes < 60 or hours * 60 + minutes <= 0):
            raise ValueError("invalid shift duration")
        return start, hours * 60 + minutes
    try:
        return decode(read_handwritten_record(run / "shift-values.json", "json").text)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return None


def check_pairs(pairs: tuple[tuple[int, int] | None, ...],
                window: tuple[int, int] | None = None) -> tuple[str, ...]:
    """Check minute-of-day pairs in encounter order, preserving unread gaps.

    A window is (start minute, duration minutes). A missing pair interrupts the
    adjacent spacing test rather than inventing an encounter's times.
    """
    findings = []
    previous_end = None
    day = 0
    previous_start = None
    for number, pair in enumerate(pairs, 1):
        if pair is None:
            previous_end = None
            continue
        start, end = pair
        duration = (end - start) % 1440
        if duration < 15 or duration > 40:
            findings.append(f"note {number}: duration outside 15 to 40 minutes")
        if duration % 5:
            findings.append(f"note {number}: duration is not a 5-minute step")
        if window is not None:
            offset = (start - window[0]) % 1440
            if offset > window[1] or offset + duration > window[1]:
                findings.append(f"note {number}: outside shift window")
        else:
            # Only a substantial backwards clock jump is a midnight crossing;
            # ordinary backwards starts remain overlap/order findings.
            if previous_start is not None and previous_start - start > 720:
                day += 1440
            offset = start + day
            previous_start = start
        if previous_end is not None and offset - previous_end < 5:
            findings.append(f"note {number}: spacing less than 5 minutes")
        previous_end = offset + duration
    return tuple(findings)


def check(run: Path, *, batch: bool, note: Path | None = None) -> Result:
    if not completion_checks.active("visit_times:visit-times"):
        return Result(graded=False)
    paths = (note,) if note is not None else medatrax_posting.note_paths(run, batch=batch)
    pairs = []
    unread = 0
    for path in paths:
        try:
            pair, residue = read_pair(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            pair, residue = None, 1
        pairs.append(pair)
        unread += residue
    damage_report = ""
    damage_findings = ()
    try:
        window = read_window(run)
    except DamagedRecord as failure:
        finding, damage_report = damaged_record_result(failure, check="visit-time shift window")
        damage_findings = (damage_report,) if finding else ()
        window = None
    return Result(len(paths), sum(pair is not None for pair in pairs),
                  (*check_pairs(tuple(pairs), window), *damage_findings), unread,
                  window is not None, bool(paths), damage_report=damage_report)


def report(result: Result, *, show: bool = False) -> str:
    if not result.graded:
        return "visit times: not graded - check starts after approval"
    lines = [f"visit times: {result.pairs} of {result.notes} notes read; findings {len(result.findings)}"]
    if result.pairs < result.notes:
        lines.append("visit times: incomplete coverage - a note has no unique readable Start time / End time pair")
    if not result.population_checked:
        lines.append("visit times: not checked - no posted note resolved; supply --note for a standalone note")
    if not result.window_checked and not result.damage_report:
        lines.append("visit times: not checked - shift values absent or unreadable; record start and duration in shift-values.json")
    if result.damage_report:
        lines.append(result.damage_report)
    if show:
        lines.extend(result.findings)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--note", type=Path)
    parser.add_argument("--standalone", action="store_true")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)
    result = check(args.run, batch=not args.standalone, note=args.note)
    print(report(result, show=args.show))
    print(run_grader.format_unread_remainder(result.unread))
    return 1 if result.findings else 2 if result.incomplete else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
