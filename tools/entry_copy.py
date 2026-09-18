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


def _clause_end(note: str, start: int) -> int | None:
    for position in range(start, len(note)):
        char = note[position]
        if char == ";":
            return position + 1
        if char == "." and (
            position + 1 == len(note) or note[position + 1].isspace()
        ):
            preceding = re.search(r"([A-Za-z]+)$", note[:position])
            next_word = note[position + 1 :].lstrip()[:1]
            if preceding and (
                preceding.group(1).lower() in ABBREVIATIONS
                or (
                    len(preceding.group(1)) == 1
                    and (
                        next_word.islower()
                        or (
                            preceding.start(1) > 0
                            and note[preceding.start(1) - 1] == "."
                        )
                    )
                )
            ):
                continue
            return position + 1
        if char == "\n":
            return None
    return None


def _without_refusals(note: str) -> str:
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
    if MARK.search(copy):
        raise ValueError("NOT CODED mark survived Entry copy derivation")
    return _portal_characters(copy)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", type=Path, help="finished note from a new or existing run")
    args = parser.parse_args(argv)
    source = args.note
    destination = source.parent / "entry-copies" / source.name
    try:
        if source.parent.name == "entry-copies":
            raise ValueError("input must be the finished note, not an Entry copy")
        copy = derive(source.read_text(encoding="utf-8"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(copy, encoding="utf-8", newline="")
    except (OSError, UnicodeError, ValueError) as error:
        destination.unlink(missing_ok=True)
        print(f"Entry copy refused: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
