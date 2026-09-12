"""Count unaccounted top-level entries across this repository's scratch roots.

The ratchet's complete boundary lives in ``DECLARED_LIMITS``.  Each row names a
mechanical path the census or the directory producer does not close.

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

INVALID_INVOCATION = "arguments do not match the command surface"
WORKTREE_REGISTRY_UNAVAILABLE = (
    "the registered checkout population or committing checkout is unavailable"
)
ACCOUNTED_SET_UNAVAILABLE = "the accounted top-level name set is unavailable"
OWNING_SCRATCH_ABSENT = "the owning checkout has no scratch root"
OWNING_SCRATCH_UNREADABLE = "the owning checkout scratch root cannot be read"
COMMITTING_SCRATCH_UNREADABLE = (
    "the committing checkout scratch root cannot be read"
)
EXIT_2_LIMBS = (
    INVALID_INVOCATION,
    WORKTREE_REGISTRY_UNAVAILABLE,
    ACCOUNTED_SET_UNAVAILABLE,
    OWNING_SCRATCH_ABSENT,
    OWNING_SCRATCH_UNREADABLE,
    COMMITTING_SCRATCH_UNREADABLE,
)

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

OWNING_SWAP_LIMIT = "the owning-checkout integer baseline has a one-entry swap hole"
OUTSIDE_CHECKOUT_LIMIT = (
    "material outside every checkout is outside this walk and any producer"
)
SEPARATE_CLONE_LIMIT = (
    "a separate clone has its own worktree registry and is invisible"
)
ABANDONED_WORKTREE_LIMIT = (
    "an abandoned worktree's loose entry is gated by no later commit and its "
    "removal can discard unrecoverable material without warning"
)
SHARED_TICKET_DIRECTORY_LIMIT = (
    "two drones on one ticket at the same time share one ticket directory"
)
SHARED_CHECKOUT_LIMIT = (
    "two drones sharing one checkout are one gating root to the census"
)
DELETED_COMMITTING_ROOT_LIMIT = (
    "a committing scratch root deleted rather than drained reports as one "
    "never created"
)

DECLARED_LIMITS = (
    OWNING_SWAP_LIMIT,
    OUTSIDE_CHECKOUT_LIMIT,
    SEPARATE_CLONE_LIMIT,
    ABANDONED_WORKTREE_LIMIT,
    SHARED_TICKET_DIRECTORY_LIMIT,
    SHARED_CHECKOUT_LIMIT,
    DELETED_COMMITTING_ROOT_LIMIT,
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


@dataclass(frozen=True)
class PeerPopulation:
    roots: tuple[Path, ...]
    counts: tuple[RootCount, ...]
    absent: tuple[Path, ...]
    empty: tuple[RootCount, ...]
    material: tuple[RootCount, ...]
    unreadable: tuple[Path, ...]
    stale: tuple[Path, ...]


def peer_population(
    roots: tuple[Path, ...],
    gating_roots: set[Path],
    counts: list[RootCount],
    absent: list[Path],
    unavailable: dict[Path, str],
    *,
    unaccounted_available: bool,
) -> PeerPopulation:
    peer_roots = tuple(root for root in roots if root not in gating_roots)
    peer_counts = tuple(item for item in counts if item.root not in gating_roots)
    peer_absent = tuple(root for root in absent if root not in gating_roots)
    peer_unreadable = tuple(
        root
        for root, state in unavailable.items()
        if root not in gating_roots and state == "unreadable"
    )
    peer_stale = tuple(
        root
        for root, state in unavailable.items()
        if root not in gating_roots and state == "stale registration"
    )
    peer_material = tuple(
        item
        for item in peer_counts
        if item.files > 0 or (unaccounted_available and item.unaccounted > 0)
    )
    material_roots = {item.root for item in peer_material}
    peer_empty = tuple(
        item for item in peer_counts if item.root not in material_roots
    )
    return PeerPopulation(
        roots=peer_roots,
        counts=peer_counts,
        absent=peer_absent,
        empty=peer_empty,
        material=peer_material,
        unreadable=peer_unreadable,
        stale=peer_stale,
    )


def print_peer_population(
    peers: PeerPopulation,
    *,
    show_all: bool,
    unaccounted_available: bool,
) -> None:
    print(
        f"REPORT ONLY: {len(peers.roots)} peer roots; "
        f"{len(peers.absent)} no root, {len(peers.empty)} empty, "
        f"{len(peers.material)} carrying material, "
        f"{len(peers.unreadable)} unreadable, {len(peers.stale)} stale"
    )
    counts_by_root = {item.root: item for item in peers.counts}
    material_roots = {item.root for item in peers.material}
    unreadable_roots = set(peers.unreadable)
    selected_roots = peers.roots if show_all else tuple(
        root
        for root in peers.roots
        if root in material_roots or root in unreadable_roots
    )
    for root in selected_roots:
        item = counts_by_root.get(root)
        if item is not None:
            noun = "file" if item.files == 1 else "files"
            if unaccounted_available:
                state = f"{item.files} {noun}, {item.unaccounted} unaccounted"
            else:
                state = f"{item.files} {noun}; unaccounted not scanned"
        elif root in unreadable_roots:
            state = "unreadable"
        elif root in peers.stale:
            state = "stale registration"
        else:
            state = "absent"
        print(f"REPORT ONLY: {root / 'scratch'}: {state}; never graded")


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


def enclosing_worktree(invocation: Path, roots: tuple[Path, ...]) -> Path:
    matches = [
        root
        for root in roots
        if invocation == root or invocation.is_relative_to(root)
    ]
    if not matches:
        raise CensusNotRun("current directory is outside every registered worktree")
    return max(matches, key=lambda root: len(root.parts))


def accounted_names(checkout: Path) -> frozenset[str]:
    finished = run_git(checkout, "grep", "-h", "-I", "-e", "scratch/", "--", ".")
    if finished.returncode not in (0, 1):
        raise CensusNotRun(finished.stderr.strip() or "git grep failed")
    return scratch_names(finished.stdout)


def scratch_names(text: str) -> frozenset[str]:
    names: set[str] = set()
    masked = list(text)

    def blank(start: int, end: int) -> None:
        masked[start:end] = " " * (end - start)

    for pattern in DELIMITED_SCRATCH_NAMES:
        for match in pattern.finditer(text):
            names.add(match.group(1))
            blank(*match.span())
    masked_text = "".join(masked)
    for match in EXPLICIT_DIRECTORY_NAME.finditer(masked_text):
        names.add(match.group(1))
        blank(*match.span())
    for match in PLAIN_SCRATCH_NAME.finditer("".join(masked)):
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

    invocation = Path.cwd().resolve()
    try:
        roots = worktree_roots(invocation)
        checkout = enclosing_worktree(invocation, roots)
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
    absent: list[Path] = []
    unavailable: dict[Path, str] = {}
    for root in roots:
        try:
            counted = count_root(root, accounted)
            if counted is not None:
                counts.append(counted)
            else:
                absent.append(root)
        except FileNotFoundError:
            unavailable[root] = (
                "unreadable" if root.is_dir() else "stale registration"
            )
        except OSError:
            unavailable[root] = "unreadable"

    unreadable_roots = tuple(
        root for root, state in unavailable.items() if state == "unreadable"
    )
    stale_roots = tuple(
        root for root, state in unavailable.items() if state == "stale registration"
    )
    coverage = (
        f"coverage: {len(roots)} worktrees enumerated; "
        f"{len(unreadable_roots)} unreadable"
        + (
            ": " + ", ".join(str(path) for path in unreadable_roots)
            if unreadable_roots
            else ""
        )
    )
    if stale_roots:
        noun = "registration" if len(stale_roots) == 1 else "registrations"
        coverage += (
            f"; {len(stale_roots)} stale {noun}: "
            + ", ".join(str(path) for path in stale_roots)
        )
    print(coverage)
    print(
        f"scratch roots: {len(counts)} checkouts own a scratch root; "
        f"{sum(item.files for item in counts)} files beneath"
    )
    owning = roots[0]
    if accounted_error is not None:
        gating_roots = {owning, checkout}
        peers = peer_population(
            roots,
            gating_roots,
            counts,
            absent,
            unavailable,
            unaccounted_available=False,
        )
        print_peer_population(
            peers,
            show_all=argv == ["--worktrees"],
            unaccounted_available=False,
        )
        for root in roots:
            if root not in gating_roots:
                continue
            state = unavailable.get(root)
            if state is None and root in absent:
                state = "absent"
            elif state is None:
                state = "not scanned"
            print(f"GATING: {root / 'scratch'}: {state}")
        print(f"NOT SCANNED: {accounted_error}", file=sys.stderr)
        print("NOT SCANNED: the accounted set could not be derived")
        if argv == ["--worktrees"] and stale_roots:
            print("REMEDY: run git worktree prune")
        return 2
    owning_count = next((item for item in counts if item.root == owning), None)
    owning_finding = (
        owning_count is not None and owning_count.unaccounted > OWNING_BASELINE
    )
    other_counts = [item for item in counts if item.root != owning]
    committing_count = next(
        (item for item in other_counts if item.root == checkout), None
    )
    committing_finding = (
        committing_count is not None and committing_count.unaccounted > 0
    )
    gating_unavailable = [root for root in absent if root == owning] + [
        root for root in unavailable if root in (owning, checkout)
    ]
    committing_absent = checkout != owning and checkout in absent
    finding = owning_finding or committing_finding
    not_scanned = bool(gating_unavailable)

    peers = peer_population(
        roots,
        {owning, checkout},
        counts,
        absent,
        unavailable,
        unaccounted_available=True,
    )
    print_peer_population(
        peers,
        show_all=argv == ["--worktrees"],
        unaccounted_available=True,
    )
    if argv == ["--worktrees"]:
        try:
            measured_roots = tuple(item.root for item in counts if item.root != owning)
            merged, clean, ahead = worktree_breakdown(owning, measured_roots)
            print(f"worktree state: {merged} merged; {clean} clean; {ahead} ahead")
        except CensusNotRun as error:
            print(f"worktree state: NOT SCANNED ({error})")

    if owning_count is not None:
        print(
            f"GATING: {owning_count.root / 'scratch'}: "
            f"{owning_count.unaccounted} unaccounted, "
            f"{max(0, owning_count.unaccounted - OWNING_BASELINE)} above baseline"
        )
    if committing_count is not None:
        print(
            f"GATING: {committing_count.root / 'scratch'}: "
            f"{committing_count.unaccounted} unaccounted, "
            f"{committing_count.unaccounted} above baseline"
        )
    if committing_absent:
        print(f"GATING: {checkout / 'scratch'}: absent; nothing to grade")
    for root in gating_unavailable:
        state = unavailable.get(root, "absent")
        print(f"GATING: {root / 'scratch'}: {state}; not scanned")
    if owning_finding and owning_count is not None:
        above = owning_count.unaccounted - OWNING_BASELINE
        noun = "entry" if above == 1 else "entries"
        print(
            f"FINDING: {above} top-level {noun} above "
            "the owning checkout's ratchet"
        )
    if committing_finding and committing_count is not None:
        above = committing_count.unaccounted
        noun = "entry" if above == 1 else "entries"
        print(
            f"FINDING: {above} top-level {noun} above "
            "the committing checkout's ratchet"
        )
    if finding:
        print("REMEDY: move it under scratch/sessions/ticket-<n>/")
        print(
            "        do not raise OWNING_BASELINE -- the ratchet's only value "
            "is that it cannot be moved to meet the disk"
        )
        if committing_finding:
            print("        do not delete a scratch root to clear this")
    elif not not_scanned:
        print("CLEAN: scratch top levels are within their ratchets")
    if not_scanned:
        if owning in absent:
            print(
                "REMEDY: run python tools/scratch_work.py ticket <n> to create "
                "the owning scratch root"
            )
        if unavailable.get(owning) == "unreadable":
            print("REMEDY: restore access to the owning scratch root")
        if checkout != owning and unavailable.get(checkout) == "unreadable":
            print("REMEDY: restore access to the committing scratch root")
        if any(unavailable.get(root) == "unreadable" for root in gating_unavailable):
            print("        do not delete a scratch root to clear this")
        print("NOT SCANNED: one or more required roots could not be read")
    if argv == ["--worktrees"] and stale_roots:
        print("REMEDY: run git worktree prune")

    if finding:
        return 1
    if not_scanned:
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
