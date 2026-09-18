"""Count claim records in the ledgers that run certifiers actually read.

    python tools/claim_ledger_census.py

The population is ``scratch/runs/*/claims.md`` in every registered checkout.
Other ``claims*.md`` files are counted, never opened or graded. A separate
clone has another worktree registry, and material outside registered checkouts
is outside this walk. The report contains only fixed labels and integers: no
claim, filename, or path can enter its output.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from research_ledger import (
    DATE_HEADER,
    SOURCED,
    STATUSES,
    has_substantive_refutation,
    read_records,
)
import scratch_census


USAGE = "usage: claim_ledger_census.py"
LEDGERLESS_RUN_LIMIT = (
    "A nonzero count of runs with claims*.md but no claims.md needs a reader; "
    "no certifier loads those files."
)
DECLARED_LIMITS = (LEDGERLESS_RUN_LIMIT,)


@dataclass(frozen=True)
class RootRead:
    ledgers: int = 0
    dated_ledgers: int = 0
    statuses: tuple[int, ...] = (0, 0, 0, 0)
    sourced_without_refutation: int = 0
    snapshots: int = 0
    ledgerless_runs: int = 0


@dataclass(frozen=True)
class Census:
    checkouts: int
    roots_read: int
    roots_unreadable: int
    ledgers: int
    dated_ledgers: int
    statuses: tuple[int, ...]
    sourced_without_refutation: int
    snapshots: int
    ledgerless_runs: int


def read_root(root: Path) -> RootRead | None:
    """Read only exact-name ledgers under one registered scratch root."""
    if not root.exists():
        return None
    if not root.is_dir():
        raise OSError("scratch root is not a directory")
    # Probe the root even when it has no runs directory. An unreadable root is
    # still an incomplete registered population.
    next(root.iterdir(), None)
    runs = root / "runs"
    if not runs.exists():
        return RootRead()
    if not runs.is_dir():
        raise OSError("runs is not a directory")

    ledgers = dated = without_refutation = snapshots = ledgerless = 0
    statuses = [0] * (len(STATUSES) + 1)
    for run in runs.iterdir():
        if not run.is_dir():
            continue
        claim_files = tuple(
            path for path in run.iterdir()
            if path.is_file() and path.name.startswith("claims") and path.name.endswith(".md")
        )
        ledger = run / "claims.md"
        if ledger not in claim_files:
            ledgerless += int(bool(claim_files))
            continue
        snapshots += len(claim_files) - 1
        contents = ledger.read_text(encoding="utf-8", errors="replace")
        ledgers += 1
        dated += int(DATE_HEADER.search(contents) is not None)
        for record in read_records(contents):
            status = record.status
            index = STATUSES.index(status) if status in STATUSES else len(STATUSES)
            statuses[index] += 1
            without_refutation += int(
                status == SOURCED and not has_substantive_refutation(record)
            )
    return RootRead(
        ledgers, dated, tuple(statuses), without_refutation, snapshots, ledgerless
    )


def scan_corpus(checkout: Path) -> Census:
    """Aggregate completed roots without retaining private paths or text."""
    worktrees = scratch_census.worktree_roots(checkout)
    roots_read = roots_unreadable = ledgers = dated = without_refutation = 0
    snapshots = ledgerless = 0
    statuses = [0] * (len(STATUSES) + 1)
    for worktree in worktrees:
        try:
            found = read_root(worktree / "scratch")
        except OSError:
            roots_unreadable += 1
            continue
        if found is None:
            continue
        roots_read += 1
        ledgers += found.ledgers
        dated += found.dated_ledgers
        without_refutation += found.sourced_without_refutation
        snapshots += found.snapshots
        ledgerless += found.ledgerless_runs
        statuses = [left + right for left, right in zip(statuses, found.statuses)]
    return Census(
        len(worktrees), roots_read, roots_unreadable, ledgers, dated,
        tuple(statuses), without_refutation, snapshots, ledgerless,
    )


def format_report(census: Census) -> str:
    lines = [
        f"checkouts enumerated              {census.checkouts}",
        f"scratch roots read                 {census.roots_read}",
        f"scratch roots unreadable           {census.roots_unreadable}",
        f"ledgers read                       {census.ledgers}",
        f"ledgers with DATE header           {census.dated_ledgers}",
        "claim records by STATUS",
    ]
    for status, count in zip((*STATUSES, "unrecognized"), census.statuses):
        lines.append(f"  {status:<33} {count}")
    lines.extend(
        (
            f"sourced without substantive refutation {census.sourced_without_refutation}",
            f"snapshots beside a ledger          {census.snapshots}",
            f"runs with claim files and no ledger {census.ledgerless_runs}",
        )
    )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        result = scan_corpus(Path.cwd().resolve())
    except scratch_census.CensusNotRun:
        print("NOT SCANNED: registered checkout population unavailable", file=sys.stderr)
        return 2
    print(format_report(result))
    if result.roots_unreadable:
        print("NOT SCANNED: registered scratch root unreadable", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
