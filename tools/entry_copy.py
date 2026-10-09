#!/usr/bin/env python3
"""Derive the Medatrax Entry copy from a finished clinical note."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from note_grammar import parse


REFUSAL = re.compile(r"NOT CODED:\s*[A-Z][0-9][0-9A-Z]*(?:\.[0-9A-Z]+)?\b")
MARK = re.compile(r"NOT CODED", re.IGNORECASE)
PLAN_LABELS = frozenset(
    {
        "Non-pharmacologic",
        "Pharmacologic",
        "Health Promotion/Patient Education",
        "Referral/Follow-up",
    }
)
PLAN_EXCEPTIONS = frozenset({"Sig", "Dispense", "Refills"})
PLAN_ENDS = frozenset({"Coding worksheet"})
ABBREVIATIONS = frozenset({"dr", "mr", "mrs", "ms", "st", "vs", "etc"})
PORTAL_VERDICTS = {"∴": ";"}  # Measured in the saved Medatrax note form.
CLINICIAN_INSTRUCTIONS = (
    ("before entry", re.compile(r"\bbefore\s+(?:portal\s+)?entry\b", re.IGNORECASE)),
    ("before submitting", re.compile(r"\bbefore\s+(?:submitting|submission)\b", re.IGNORECASE)),
    ("before posting", re.compile(r"\bbefore\s+posting\b", re.IGNORECASE)),
)


class RefusalGrammarError(ValueError):
    """A refused-code clause would leave sentence residue in an Entry copy."""


def _plain(line: str) -> str:
    return line.strip().strip("#*_ ").strip()


def _plan_labels(note: str) -> tuple[set[str], list[str]]:
    in_plan = False
    found: set[str] = set()
    invalid: list[str] = []
    for line in note.splitlines():
        plain = _plain(line)
        if not in_plan:
            if plain in {"P:", "Plan", "Plan:"}:
                in_plan = True
            continue
        if plain in PLAN_ENDS or plain in {end + ":" for end in PLAN_ENDS}:
            break
        if line.lstrip().startswith(("---", "## ")):
            break
        if ":" not in plain:
            continue
        lead = plain.split(":", 1)[0].strip("*_ ")
        if len(lead.split()) > 4:
            continue
        if lead in PLAN_LABELS:
            if lead in found:
                invalid.append(lead + " (repeated)")
            found.add(lead)
        elif lead not in PLAN_EXCEPTIONS:
            invalid.append(lead)
    if not in_plan:
        invalid.append("Plan missing")
    invalid.extend(sorted(PLAN_LABELS - found))
    return found, invalid


def _sentence_period(note: str, position: int) -> bool:
    if note[position] != "." or (
        position + 1 < len(note) and not note[position + 1].isspace()
    ):
        return False
    preceding = re.search(r"([A-Za-z]+)$", note[:position])
    next_word = note[position + 1 :].lstrip()[:1]
    return not (preceding and (
        preceding.group(1).lower() in ABBREVIATIONS
        or (
            len(preceding.group(1)) == 1
            and (
                next_word.islower()
                or (preceding.start(1) > 0 and note[preceding.start(1) - 1] == ".")
            )
        )
    ))


def _clause_end(note: str, start: int) -> int | None:
    for position in range(start, len(note)):
        char = note[position]
        if char == ";":
            return position + 1
        if char == "." and _sentence_period(note, position):
            return position + 1
        if char == "\n":
            return None
    return None


def _without_refusals(note: str) -> str:
    previous_end = None
    for match in REFUSAL.finditer(note):
        line_start = note.rfind("\n", 0, match.start()) + 1
        line_prefix = note[line_start:match.start()]
        prefix = line_prefix.rstrip(" \t\r")
        at_line_start = re.fullmatch(
            r"[ \t]*(?:>[ \t]*)*(?:(?:[-+*]|[0-9]+[.)])[ \t]+)?", line_prefix
        )
        after_period = bool(prefix) and _sentence_period(note, line_start + len(prefix) - 1)
        after_clause = (
            previous_end is not None
            and note[previous_end - 1] == ";"
            and not note[previous_end:match.start()].strip()
        )
        if not (at_line_start or after_period or after_clause):
            raise RefusalGrammarError("NOT CODED clause must open its own sentence")
        previous_end = _clause_end(note, match.end())
        if (
            previous_end is not None
            and note[previous_end - 1] == ";"
            and not REFUSAL.match(note[previous_end:].lstrip())
        ):
            raise RefusalGrammarError("NOT CODED clause semicolon must join another welded clause")
    while match := REFUSAL.search(note):
        end = _clause_end(note, match.end())
        if end is None:
            break
        start = match.start()
        while start > 0 and note[start - 1] in " \t":
            start -= 1
        note = note[:start] + note[end:]
    return note


def _portal_characters(copy: str) -> str:
    """Apply measured portal characters only to text pasted in the four boxes."""
    try:
        parsed = parse(copy)
    except ValueError:
        # Legacy partial worked examples have no four-section form to paste.
        # A full run still reaches form_sections, which refuses this shape.
        if any(not char.isascii() for char in copy):
            raise
        return copy
    result = [parsed.buckets["preamble"]]
    for label in "SOAP":
        heading, body = parsed.buckets[label].split("\n", 1)
        for vocabulary, pattern in CLINICIAN_INSTRUCTIONS:
            if pattern.search(body):
                raise ValueError(
                    f"clinician-directed instruction '{vocabulary}' in section {label}"
                )
        for char in body:
            if not char.isascii() and char not in PORTAL_VERDICTS:
                raise ValueError(f"unmeasured portal character U+{ord(char):04X}")
        result.append(heading + "\n" + "".join(PORTAL_VERDICTS.get(char, char) for char in body))
    result.append(parsed.buckets["tail"])
    return "".join(result)


def derive(note: str) -> str:
    _found, invalid = _plan_labels(note)
    if invalid:
        raise ValueError("Plan labels invalid: " + ", ".join(invalid))
    copy = _without_refusals(note)
    try:
        parsed = parse(copy)
    except ValueError:
        if MARK.search(copy):
            raise ValueError("NOT CODED mark survived Entry copy derivation") from None
    else:
        for label in "SOAP":
            if MARK.search(parsed.buckets[label]):
                raise ValueError(f"NOT CODED mark survived Entry copy derivation in section {label}")
    return _portal_characters(copy)


def check(note: str) -> None:
    """Refuse an Entry copy that cannot be derived and split, without writing it."""
    try:
        copy = derive(note)
    except ValueError as error:
        if str(error).startswith("Plan labels invalid:"):
            # An unrecognized label can contain patient text; keep it out of diagnostics.
            raise ValueError("Plan labels invalid") from None
        raise
    parse(copy)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check derivation and four-section split without writing")
    parser.add_argument("note", type=Path, nargs="+", help="finished note from a new or existing run")
    args = parser.parse_args(argv)
    status = 0
    for source in args.note:
        destination = source.parent / "entry-copies" / source.name
        try:
            if source.parent.name == "entry-copies":
                raise ValueError("input must be the finished note, not an Entry copy")
            note = source.read_text(encoding="utf-8")
            if args.check:
                check(note)
            else:
                copy = derive(note)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(copy, encoding="utf-8", newline="")
        except (OSError, UnicodeError, ValueError) as error:
            if not args.check or isinstance(error, RefusalGrammarError):
                destination.unlink(missing_ok=True)
            location = f"{source}: " if args.check or len(args.note) > 1 else ""
            print(f"Entry copy refused: {location}{error}", file=sys.stderr)
            status = 1
            continue
        if not args.check:
            print(destination)
    return status


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
