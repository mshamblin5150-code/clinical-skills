"""Count unaccounted top-level entries across this repository's scratch roots.

The ratchet deliberately has three limits which are properties of the mechanism:

* its integer baseline has a one-entry swap hole in the owning checkout;
* material written outside every checkout is outside the walk and any producer;
* a separate clone has its own worktree registry and is invisible here.

The command never reads scratch-file contents and never prints an unaccounted
entry's name. Deletion is outside its authority; a failing worktree is drained
to the owning checkout without classifying or deleting what moves.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8


# This is the only current statement of the grandfathered owning-checkout count.
# Re-recording it requires a live count-only run and a visible diff. A list of the
# entries would publish patient-derived filenames and is therefore unavailable.
OWNING_BASELINE = 28

STANDING_ARTIFACTS = frozenset(
    {
        "runs",
        "day-file-text",
        "writing-samples",
        "name-index.json",
        "harvest-reviewed.json",
        "medatrax-profile.md",
        "identity-map.md",
        "voice-model.md",
        "shorthand.md",
    }
)

DECLARED_LIMITS = (
    "the owning-checkout integer baseline has a one-entry swap hole",
    "material outside every checkout is outside this walk and any producer",
    "a separate clone has its own worktree registry and is invisible",
)

DELIMITED_SCRATCH_NAMES = (
    re.compile(r"`scratch/([^/`\r\n]+)"),
    re.compile(r'"scratch/([^/"\r\n]+)'),
    re.compile(r"'scratch/([^/'\r\n]+)"),
    re.compile(r"<scratch/([^/><\r\n]+)"),
)
EXPLICIT_DIRECTORY_NAME = re.compile(r"(?<![\w.-])scratch/([^/\r\n]+?)/")
PLAIN_SCRATCH_NAME = re.compile(r"(?<![\w.-])scratch/([^\s/]+)")


class CensusNotRun(Exception):
    pass


@dataclass(frozen=True)
class RootCount:
    root: Path
    unaccounted: int
    files: int


def run_git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        raise CensusNotRun(str(error)) from None


def worktree_roots(checkout: Path) -> tuple[Path, ...]:
    finished = run_git(checkout, "worktree", "list", "--porcelain")
    if finished.returncode != 0:
        raise CensusNotRun(finished.stderr.strip() or "git worktree list failed")
    roots = tuple(
        Path(line.removeprefix("worktree ")).resolve()
        for line in finished.stdout.splitlines()
        if line.startswith("worktree ")
    )
    if not roots:
        raise CensusNotRun("git worktree list returned no worktrees")
    return roots


def accounted_names(checkout: Path) -> frozenset[str]:
    finished = run_git(checkout, "grep", "-h", "-I", "-e", "scratch/", "--", ".")
    if finished.returncode not in (0, 1):
        raise CensusNotRun(finished.stderr.strip() or "git grep failed")
    return scratch_names(finished.stdout)


def scratch_names(text: str) -> frozenset[str]:
    names: set[str] = set()
    complete_spans: list[tuple[int, int]] = []
    for pattern in (*DELIMITED_SCRATCH_NAMES, EXPLICIT_DIRECTORY_NAME):
        for match in pattern.finditer(text):
            names.add(match.group(1))
            complete_spans.append(match.span())
    for match in PLAIN_SCRATCH_NAME.finditer(text):
        if any(start <= match.start() < end for start, end in complete_spans):
            continue
        names.add(match.group(1))
    return frozenset(names)


def count_files(root: Path) -> int:
    total = 0

    def failed(error: OSError) -> None:
        raise error

    for _, _, filenames in os.walk(root, followlinks=False, onerror=failed):
        total += len(filenames)
    return total


def count_root(root: Path, accounted: frozenset[str]) -> RootCount | None:
    if not root.is_dir():
        raise FileNotFoundError(root)
    scratch = root / "scratch"
    if not scratch.exists():
        return None
    entries = tuple(scratch.iterdir())
    return RootCount(
        root=root,
        unaccounted=sum(entry.name not in accounted for entry in entries),
        files=count_files(scratch),
    )


def worktree_breakdown(
    owning: Path, worktrees: tuple[Path, ...]
) -> tuple[int, int, int]:
    if not worktrees:
        return 0, 0, 0
    owning_result = run_git(owning, "rev-parse", "HEAD")
    if owning_result.returncode != 0:
        raise CensusNotRun(
            owning_result.stderr.strip() or "could not measure the owning checkout"
        )
    owning_oid = owning_result.stdout.strip()
    statuses: list[tuple[str, bool]] = []
    for root in worktrees:
        finished = run_git(root, "status", "--porcelain=v2", "--branch")
        if finished.returncode != 0:
            raise CensusNotRun(
                finished.stderr.strip() or "could not measure worktree state"
            )
        lines = finished.stdout.splitlines()
        oid = next(
            (line.removeprefix("# branch.oid ") for line in lines if line.startswith("# branch.oid ")),
            "",
        )
        clean = not any(not line.startswith("# ") for line in lines)
        statuses.append((oid, clean))

    history_result = run_git(owning, "rev-list", owning_oid)
    if history_result.returncode != 0:
        raise CensusNotRun(
            history_result.stderr.strip() or "could not measure merged worktrees"
        )
    merged_oids = set(history_result.stdout.splitlines())
    merged = sum(oid in merged_oids for oid, _ in statuses)
    clean = sum(item[1] for item in statuses)
    ahead = len(statuses) - merged
    return merged, clean, ahead


def main(argv: list[str]) -> int:
    if argv not in ([], ["--worktrees"]):
        print("usage: scratch_census.py [--worktrees]", file=sys.stderr)
        return 2

    checkout = Path.cwd().resolve()
    try:
        roots = worktree_roots(checkout)
    except CensusNotRun as error:
        print("coverage: 0 worktrees enumerated; 0 unreadable")
        print(f"NOT SCANNED: {error}", file=sys.stderr)
        return 2

    accounted_error: CensusNotRun | None = None
    try:
        accounted = accounted_names(checkout)
    except CensusNotRun as error:
        accounted = frozenset()
        accounted_error = error

    counts: list[RootCount] = []
    unreadable: list[Path] = []
    for root in roots:
        try:
            counted = count_root(root, accounted)
            if counted is not None:
                counts.append(counted)
        except OSError:
            unreadable.append(root)

    print(
        f"coverage: {len(roots)} worktrees enumerated; "
        f"{len(unreadable)} unreadable"
        + (": " + ", ".join(str(path) for path in unreadable) if unreadable else "")
    )
    print(
        f"scratch roots: {len(counts)} checkouts own a scratch root; "
        f"{sum(item.files for item in counts)} files beneath"
    )
    if accounted_error is not None:
        print(f"NOT SCANNED: {accounted_error}", file=sys.stderr)
        if unreadable:
            print("NOT SCANNED: one or more required roots could not be read")
        return 2
    owning = roots[0]
    state_not_scanned = False
    if argv == ["--worktrees"]:
        try:
            measured_roots = tuple(item.root for item in counts if item.root != owning)
            merged, clean, ahead = worktree_breakdown(owning, measured_roots)
            print(f"worktree state: {merged} merged; {clean} clean; {ahead} ahead")
        except CensusNotRun as error:
            print(f"worktree state: NOT SCANNED ({error})")
            state_not_scanned = True

    owning_count = next((item for item in counts if item.root == owning), None)
    owning_finding = (
        owning_count is not None and owning_count.unaccounted > OWNING_BASELINE
    )
    other_counts = [item for item in counts if item.root != owning]
    other_finding = any(item.unaccounted > 0 for item in other_counts)
    finding = owning_finding or other_finding
    not_scanned = owning_count is None or bool(unreadable) or state_not_scanned

    print(
        "top levels: {owning} owning-checkout unaccounted; "
        "{other} other-checkout unaccounted across {roots} roots".format(
            owning=owning_count.unaccounted if owning_count else 0,
            other=sum(item.unaccounted for item in other_counts),
            roots=len(other_counts),
        )
    )

    if finding:
        print("FINDING: one or more scratch top-level ratchets were exceeded")
    elif not not_scanned:
        print("CLEAN: scratch top levels are within their ratchets")
    if not_scanned:
        print("NOT SCANNED: one or more required roots could not be read")

    if finding:
        return 1
    if not_scanned:
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
