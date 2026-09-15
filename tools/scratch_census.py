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
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from git_paths import GitPathError, read_path_records


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
HARNESS_REMOVAL_LIMIT = (
    "a harness can remove a worktree without running the pre-removal report"
)
RUNNING_SESSION_LIMIT = (
    "a worktree the pre-removal report does not hold back may still belong "
    "to a running session"
)
UNLOCKED_UNMOUNTED_WORKTREE_LIMIT = (
    "an unlocked worktree on an unmounted volume reports as a stale "
    "registration, and pruning it unregisters a live checkout whose scratch "
    "material then leaves the walk permanently"
)

DECLARED_LIMITS = (
    OWNING_SWAP_LIMIT,
    OUTSIDE_CHECKOUT_LIMIT,
    SEPARATE_CLONE_LIMIT,
    ABANDONED_WORKTREE_LIMIT,
    SHARED_TICKET_DIRECTORY_LIMIT,
    SHARED_CHECKOUT_LIMIT,
    DELETED_COMMITTING_ROOT_LIMIT,
    HARNESS_REMOVAL_LIMIT,
    RUNNING_SESSION_LIMIT,
    UNLOCKED_UNMOUNTED_WORKTREE_LIMIT,
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
class WorktreeRegistration:
    root: Path
    locked_reason_present: bool | None = None

    @property
    def locked(self) -> bool:
        return self.locked_reason_present is not None


@dataclass(frozen=True)
class PreRemovalRead:
    root: Path
    scratch_files: int
    output_files: int
    untracked_files: int
    tracked_changes: int
    commits_not_on_main: int
    locked: bool

    @property
    def held_back(self) -> bool:
        return any(
            (
                self.scratch_files,
                self.output_files,
                self.untracked_files,
                self.tracked_changes,
                self.commits_not_on_main,
                self.locked,
            )
        )


@dataclass(frozen=True)
class PeerPopulation:
    roots: tuple[Path, ...]
    counts: tuple[RootCount, ...]
    absent: tuple[Path, ...]
    empty: tuple[RootCount, ...]
    material: tuple[RootCount, ...]
    unreadable: tuple[Path, ...]
    stale: tuple[Path, ...]
    locked: tuple[WorktreeRegistration, ...]


def peer_population(
    registrations: tuple[WorktreeRegistration, ...],
    gating_roots: set[Path],
    counts: list[RootCount],
    absent: list[Path],
    unavailable: dict[Path, str],
    *,
    unaccounted_available: bool,
) -> PeerPopulation:
    roots = tuple(item.root for item in registrations)
    registrations_by_root = {item.root: item for item in registrations}
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
    peer_locked = tuple(
        registrations_by_root[root]
        for root, state in unavailable.items()
        if root not in gating_roots and state == "locked registration"
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
        locked=peer_locked,
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
        f"{len(peers.unreadable)} unreadable, {len(peers.stale)} stale, "
        f"{len(peers.locked)} locked"
    )
    counts_by_root = {item.root: item for item in peers.counts}
    material_roots = {item.root for item in peers.material}
    unreadable_roots = set(peers.unreadable)
    locked_by_root = {
        registration.root: registration for registration in peers.locked
    }
    locked_roots = set(locked_by_root)
    selected_roots = peers.roots if show_all else tuple(
        root
        for root in peers.roots
        if root in material_roots or root in unreadable_roots or root in locked_roots
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
        elif root in locked_roots:
            reason = (
                "reason recorded"
                if locked_by_root[root].locked_reason_present
                else "no reason recorded"
            )
            state = f"locked registration; {reason}"
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


def worktree_registrations(checkout: Path) -> tuple[WorktreeRegistration, ...]:
    try:
        records = read_path_records(
            checkout, "worktree", "list", "--porcelain", "-z"
        )
    except GitPathError as error:
        raise CensusNotRun(str(error)) from None
    registrations: list[WorktreeRegistration] = []
    current_root: Path | None = None
    locked_reason_present: bool | None = None
    for record in records:
        if record.startswith("worktree "):
            if current_root is not None:
                registrations.append(
                    WorktreeRegistration(current_root, locked_reason_present)
                )
            current_root = Path(record.removeprefix("worktree ")).resolve()
            locked_reason_present = None
        elif current_root is not None and (
            record == "locked" or record.startswith("locked ")
        ):
            locked_reason_present = record.startswith("locked ")
    if current_root is not None:
        registrations.append(
            WorktreeRegistration(current_root, locked_reason_present)
        )
    if not registrations:
        raise CensusNotRun("git worktree list returned no worktrees")
    return tuple(registrations)


def worktree_roots(checkout: Path) -> tuple[Path, ...]:
    return tuple(
        registration.root for registration in worktree_registrations(checkout)
    )


def print_prune_remedy() -> None:
    print("REMEDY: run git worktree prune")
    print(
        "        prune only after confirming each stale directory was deleted "
        "rather than on an unmounted volume; pruning cannot be undone"
    )
    print(
        "        use git worktree lock <path> for a worktree on removable or "
        "network storage"
    )


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
    root_mode = root.stat().st_mode
    if not stat.S_ISDIR(root_mode):
        raise OSError(f"not a directory: {root}")
    scratch = root / "scratch"
    try:
        scratch_mode = scratch.stat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISDIR(scratch_mode):
        raise OSError(f"not a directory: {scratch}")
    entries = tuple(scratch.iterdir())
    return RootCount(
        root=root,
        unaccounted=sum(entry.name not in accounted for entry in entries),
        files=count_files(scratch),
    )


def optional_tree_file_count(path: Path) -> int:
    try:
        path_mode = path.stat().st_mode
    except FileNotFoundError:
        return 0
    if not stat.S_ISDIR(path_mode):
        raise OSError(f"not a directory: {path}")
    return count_files(path)


def pre_removal_read(root: Path, *, locked: bool) -> PreRemovalRead:
    status = run_git(
        root,
        "status",
        "--porcelain=v2",
        "-z",
        "--untracked-files=all",
    )
    if status.returncode != 0:
        raise CensusNotRun(status.stderr.strip() or "could not read worktree state")
    records = status.stdout.split("\0")
    untracked = sum(record.startswith("? ") for record in records)
    tracked = sum(
        record.startswith(("1 ", "2 ", "u ")) for record in records
    )
    history = run_git(root, "rev-list", "--count", "origin/main..HEAD")
    if history.returncode != 0:
        raise CensusNotRun(
            history.stderr.strip() or "could not compare the worktree with origin/main"
        )
    try:
        commits_not_on_main = int(history.stdout.strip())
    except ValueError:
        raise CensusNotRun("git rev-list returned a non-integer count") from None
    return PreRemovalRead(
        root=root,
        scratch_files=optional_tree_file_count(root / "scratch"),
        output_files=optional_tree_file_count(root / "output"),
        untracked_files=untracked,
        tracked_changes=tracked,
        commits_not_on_main=commits_not_on_main,
        locked=locked,
    )


def print_pre_removal_report(
    worktrees: tuple[WorktreeRegistration, ...]
) -> None:
    def counted(value: int, noun: str) -> str:
        return f"{value} {noun if value == 1 else noun + 's'}"

    reads: list[PreRemovalRead] = []
    unread: list[Path] = []
    for registration in worktrees:
        root = registration.root
        try:
            reads.append(pre_removal_read(root, locked=registration.locked))
        except (CensusNotRun, OSError):
            unread.append(root)
    print(f"pre-removal: {len(reads)} worktrees read; {len(unread)} not read")
    by_root = {item.root: item for item in reads}
    for registration in worktrees:
        root = registration.root
        item = by_root.get(root)
        if item is None:
            print(f"PRE-REMOVAL: {root}: not read; HELD BACK")
            continue
        lock_state = "locked" if item.locked else "unlocked"
        print(
            f"PRE-REMOVAL: {root}: scratch {counted(item.scratch_files, 'file')}; "
            f"output {counted(item.output_files, 'file')}; "
            f"{counted(item.untracked_files, 'untracked file')}; "
            f"{counted(item.tracked_changes, 'tracked change')}; "
            f"{counted(item.commits_not_on_main, 'commit')} not on origin/main; "
            f"{lock_state}"
            + ("; HELD BACK" if item.held_back else "")
        )


def main(argv: list[str]) -> int:
    if argv not in ([], ["--worktrees"]):
        print("usage: scratch_census.py [--worktrees]", file=sys.stderr)
        return 2

    invocation = Path.cwd().resolve()
    try:
        registrations = worktree_registrations(invocation)
        roots = tuple(registration.root for registration in registrations)
        checkout = enclosing_worktree(invocation, roots)
    except CensusNotRun as error:
        print("coverage: 0 worktrees enumerated; 0 unreadable")
        print(f"NOT SCANNED: {error}", file=sys.stderr)
        return 2
    registrations_by_root = {
        registration.root: registration for registration in registrations
    }

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
            try:
                root.stat()
            except FileNotFoundError:
                unavailable[root] = (
                    "locked registration"
                    if registrations_by_root[root].locked
                    else "stale registration"
                )
            except OSError:
                unavailable[root] = "unreadable"
            else:
                unavailable[root] = "unreadable"
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
    if argv == ["--worktrees"]:
        measured_worktrees = tuple(
            item
            for item in registrations
            if item.root != owning
            and unavailable.get(item.root)
            not in ("stale registration", "locked registration")
        )
        print_pre_removal_report(measured_worktrees)
    if accounted_error is not None:
        gating_roots = {owning, checkout}
        peers = peer_population(
            registrations,
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
            print_prune_remedy()
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
        registrations,
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
        print_prune_remedy()

    if finding:
        return 1
    if not_scanned:
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
