"""Print the private go-ahead UpToDate disclosure word for word (ADR 0408).

Exit 0 prints the complete block. Exit 2 refuses without a partial block.
The output is private clinical working material. The complete boundary belongs
to uptodate_block.DECLARED_LIMITS.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8
import medatrax_posting
import outbound_search

DECLARED_LIMITS = (
    "Only bracketed UpToDate-over-threshold and failed-pull tails in the supplied notes are recognized as conflicts.",
    "Recorded decisions, instruments, and differences are not independently verified against the browser or clinical sources.",
    "A live action with no committed search or outcome record remains invisible.",
)

HEADINGS = ("UPTODATE CONFLICTS", "UPTODATE FAILED PULLS", "UPTODATE MISMATCHED SEARCHES")
CONFLICT = re.compile(r"\[uptodate over thresholds/([a-z0-9-]+)(?:\.md)? ([^:\]\n]+): ([^\]\n]+), updated ([A-Za-z]+ \d{4}), ([a-z0-9][a-z0-9._-]*)\]")
FALLBACK = re.compile(r"\[(thresholds/[^\]\n]+); uptodate pull failed\]")


def source_paths(run: Path, notes: tuple[Path, ...]) -> tuple[Path, ...]:
    return notes + tuple(run / name for name in (outbound_search.SEARCHES, outbound_search.PULLS) if (run / name).exists())


def render(run: Path, notes: tuple[Path, ...]) -> str:
    """Derive a whole disclosure, refusing unbound conflict details."""
    if not notes:
        raise ValueError("UpToDate disclosure needs a note population")
    failed, report = outbound_search.completion_gate(run, "go-ahead")
    if failed or "unreadable" in report:
        raise ValueError("UpToDate outcome population is incomplete or unreadable")
    pulls = outbound_search.records(run / outbound_search.PULLS)
    conflicts = []
    bound = set()
    for note in notes:
        text = note.read_text(encoding="utf-8")
        matches = tuple(CONFLICT.finditer(text))
        if text.count("[uptodate over thresholds/") != len(matches):
            raise ValueError("UpToDate conflict tail is unreadable")
        for match in matches:
            sheet, row, topic, updated, dump = match.groups()
            joined = [pull for pull in pulls if pull.get("sheet") == sheet and pull.get("row") == row and pull.get("dump_id") == dump and not pull.get("sheet_kept")]
            if len(joined) != 1 or not joined[0].get("difference"):
                raise ValueError("UpToDate conflict lacks a matching live pull and difference")
            pull = joined[0]
            bound.add((sheet, row, dump))
            conflicts.append(f"{note.name} | thresholds/{sheet} {row} | {topic}, updated {updated}, {dump} | {pull['difference']}")
        fallbacks = tuple(FALLBACK.finditer(text))
        if len(re.findall(r";\s*uptodate pull failed", text, re.I)) != len(fallbacks):
            raise ValueError("UpToDate failed-pull tail is unreadable")
        for match in fallbacks:
            if not any(pull.get("outcome") == "failed" for pull in pulls):
                raise ValueError("failed conflict tail has no failed-pull record")
            conflicts.append(f"{note.name} | {match[1]} | sheet kept; uptodate pull failed")
    for pull in pulls:
        if pull.get("sheet"):
            if not all(isinstance(pull.get(key), str) and pull[key].strip() for key in ("sheet", "row", "dump_id", "difference")):
                raise ValueError("UpToDate conflict record is incomplete")
            if pull.get("sheet_kept"):
                conflicts.append(f"thresholds/{pull['sheet']} {pull['row']} | {pull['dump_id']} | sheet kept | {pull['difference']}")
            elif (pull["sheet"], pull["row"], pull["dump_id"]) not in bound:
                raise ValueError("UpToDate conflict live pull is absent from note tails")
    failures = [f"{pull['search_id']} | {pull['decision']} | {pull['instrument']}" for pull in pulls if pull.get("outcome") == "failed"]
    mismatches = [f"{pull['search_id']} | {pull['query_readback']} | sent-query identifier check: {'passed' if pull['sent_query_passed'] else 'refused'}"
                  for pull in pulls if pull.get("outcome") == "mismatched"]
    lines = []
    for heading, entries in zip(HEADINGS, (conflicts, failures, mismatches)):
        lines.append(f"{heading}: {len(entries) if entries else 'none'}")
        lines.extend(f"- {entry}" for entry in entries)
    return "\n".join(lines) + "\n"


def shown_matches(message: str, expected: str) -> bool:
    """Compare complete disclosure lines, allowing only surrounding chat text."""
    lines = message.splitlines()
    expected_lines = expected.rstrip("\n").splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(HEADINGS[0] + ":")]
    if len(starts) != 1:
        return False
    end = starts[0] + len(expected_lines)
    return (lines[starts[0]:end] == expected_lines
            and (end == len(lines) or not lines[end].startswith("- "))
            and sum(line.startswith(heading + ":") for line in lines for heading in HEADINGS) == len(HEADINGS))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--notes", type=Path, nargs="+")
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args(argv)
    try:
        notes = tuple(args.notes) if args.notes else medatrax_posting.note_paths(args.run, batch=args.batch)
        print(render(args.run, notes), end="")
        return 0
    except (OSError, UnicodeError, ValueError, TypeError):
        print("UpToDate disclosure: refused - private notes or outcome records incomplete or unreadable", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
