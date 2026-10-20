"""Apply saved refuter returns: ledger, then one or more group files.

The coverage boundary lives in refutation_apply.DECLARED_LIMITS.
Default reports contain positions and fixed reasons; --show is private.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import research_ledger
import run_grader
import run_record_reader as records
from console_codec import require_python_floor, use_utf8

DECLARED_LIMITS = (
    "The ledger's mixed handwritten content keeps its existing parser; its tool rewrite holds the ledger lock through source/snapshot allocation and atomic replacement. Immutable saved returns and snapshots are separate evidence, not a cross-file transaction.",
    "Recognized blocks are copied without checking verdict completeness or source support.",
    "A saved return does not establish who wrote it or whether its stated route was taken.",
)
FIELDS = ("REFUTATION", "TESTED-HEADING", "SECOND-ROUTE", "INSTRUMENTS")


@dataclass(frozen=True)
class Block:
    record: research_ledger.Record
    lines: tuple[str, ...]
    unread: int


def read_blocks(text: str) -> tuple[list[Block], int]:
    """Use the ledger reader for values; admit only the return grammar."""
    blocks = []
    current: list[str] = []
    outside = 0

    def close() -> None:
        if not current:
            return
        unread = 0
        continuation = False
        for line in current[1:]:
            if not line.strip():
                continue
            named = research_ledger.FIELD.match(line)
            if named:
                continuation = named.group(1).upper() in (*FIELDS, "REMARK")
                unread += int(not continuation)
            elif line[:1].isspace() and continuation:
                pass
            else:
                unread += 1
                continuation = False
        blocks.append(Block(research_ledger.read_records("\n".join(current))[0], tuple(current), unread))

    for line in text.splitlines():
        if research_ledger.CLAIM.match(line):
            close()
            current = [line]
        elif current:
            current.append(line)
        elif line.strip():
            outside += 1
    close()
    return blocks, outside


def refutation_values(record: research_ledger.Record) -> tuple[str, ...]:
    return tuple(record.value(name) for name in FIELDS)


def report_counts(file_number: int, total: int, counts: dict[str, int]) -> None:
    print(f"file {file_number} of {total}: " + ", ".join(f"{name} {count}" for name, count in counts.items()))


def merge_record(text: str, block: Block) -> str:
    """Replace all old refutation fields while preserving other lines and remarks."""
    kept = []
    skipping = False
    for line in text.splitlines():
        named = research_ledger.FIELD.match(line)
        if named:
            skipping = named.group(1).upper() in FIELDS
        elif research_ledger.CLAIM.match(line):
            skipping = False
        if not skipping:
            kept.append(line)
    existing = research_ledger.read_records(text)[0]
    copying = False
    for line in block.lines[1:]:
        named = research_ledger.FIELD.match(line)
        if named:
            name = named.group(1).upper()
            copying = name in FIELDS or (name == "REMARK" and named.group(2).strip() not in existing.remarks)
        if copying:
            kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def _snapshot_ledger(path: Path, original: bytes) -> None:
    """Retain one immutable prior version while the ledger transaction owns allocation."""
    number = 1
    while True:
        snapshot = path.with_name(f"{path.stem}-snapshot-{number}{path.suffix}")
        try:
            with snapshot.open("xb") as stream:
                stream.write(original)
            break
        except FileExistsError:
            number += 1


def apply(ledger: Path, returns: list[Path], show: bool = False) -> int:
    result = (0, 0)
    def change(text):
        nonlocal result
        update = _apply(ledger, returns, show, text)
        result = update.result
        return update
    try:
        status, unread = records.update_tool_record(ledger, lambda text: text, change)
    except records.UnreadableRecord as failure:
        print(records.fault_report(failure, check="the saved refuter application"))
        status, unread = (1 if result[0] == 1 else 2), result[1] + 1
    print(run_grader.format_unread_remainder(unread))
    return status


def _apply(ledger: Path, returns: list[Path], show: bool, text: str | None) -> records.RecordUpdate:
    unread = 0
    failed = False
    changed = False
    if text is None:
        print("ledger could not be read")
        return records.RecordUpdate(None, (2, 1))
    original = text.encode("utf-8")
    if not research_ledger.read_records(text):
        print("ledger contains no record")
        return records.RecordUpdate(None, (2, 1))
    newline = "\r\n" if "\r\n" in text else "\n"
    parts = [""]
    for line in text.replace("\r\n", "\n").splitlines(keepends=True):
        if research_ledger.CLAIM.match(line.rstrip("\n")):
            parts.append("")
        parts[-1] += line
    for file_number, path in enumerate(returns, 1):
        counts = dict.fromkeys(("read", "applied", "replaced", "already applied", "refused", "unmatched"), 0)
        try:
            raw = path.read_bytes()
            blocks, outside = read_blocks(raw.decode("utf-8"))
            unread += outside
        except (OSError, UnicodeError):
            print(f"file {file_number} of {len(returns)}: input could not be read")
            report_counts(file_number, len(returns), counts)
            unread += 1
            continue
        kept_conflict = False
        try:
            directory = ledger.parent / "refutations"
            directory.mkdir(exist_ok=True)
            kept = directory / path.name
            try:
                with kept.open("xb") as stream:
                    stream.write(raw)
            except FileExistsError:
                kept_conflict = kept.read_bytes() != raw
        except OSError:
            print(f"file {file_number} of {len(returns)}: return could not be kept")
            counts["read"] = len(blocks)
            report_counts(file_number, len(returns), counts)
            unread += 1
            continue
        if kept_conflict:
            failed = True
        if not blocks:
            print(f"file {file_number} of {len(returns)}: no blocks")
            unread += 1
        for block_number, block in enumerate(blocks, 1):
            counts["read"] += 1
            unread += block.unread
            matches = [(index, record) for index, part in enumerate(parts)
                       for record in research_ledger.read_records(part) if record.claim == block.record.claim]
            outcome, reason = "refused", "kept return has different bytes"
            if kept_conflict:
                pass
            elif block.unread:
                reason = "unrecognized lines"
            elif not matches:
                outcome, reason = "unmatched", "heading names no record"
                failed = True
            elif len(matches) > 1:
                reason = "heading names multiple records"
                failed = True
            elif block.record.value("TESTED-HEADING") and block.record.value("TESTED-HEADING") != research_ledger.heading_digest(block.record.claim):
                reason = "fingerprint no longer matches the heading"
                failed = True
            else:
                index, record = matches[0]
                has_existing = any(name in record.fields for name in FIELDS)
                live = record.value("TESTED-HEADING") == research_ledger.heading_digest(record.claim)
                identical = refutation_values(record) == refutation_values(block.record)
                if has_existing and live and not identical:
                    reason = "live refutation differs"
                    failed = True
                else:
                    outcome = "already applied" if has_existing and live else "replaced" if has_existing else "applied"
                    # New remarks still survive an otherwise identical return.
                    if outcome != "already applied" or any(remark not in record.remarks for remark in block.record.remarks):
                        parts[index] = merge_record(parts[index], block)
                        changed = True
            counts[outcome] += 1
            if outcome in {"refused", "unmatched"}:
                print(f"file {file_number} of {len(returns)}, block {block_number}: {outcome}, {reason}")
            if show:
                print(block.record.claim)
        report_counts(file_number, len(returns), counts)
    updated = "".join(parts).replace("\n", newline).encode("utf-8")
    payload = None
    if changed and updated != original:
        try:
            _snapshot_ledger(ledger, original)
            payload = updated
        except OSError:
            print("ledger could not be written")
            unread += 1
    return records.RecordUpdate(payload, (1 if failed else 2 if unread else 0, unread))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("returns", type=Path, nargs="+")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)
    return apply(args.ledger, args.returns, args.show)


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
