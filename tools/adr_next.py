"""Claim the next ADR number across every worktree by writing its file."""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8


ADR_PREFIX = re.compile(r"^(?P<number>\d{4})")
REPO_ROOT = Path(__file__).resolve().parent.parent

# ``repo_root.ensure_outside_checkout`` protects generated artifacts that must not
# be committed. An ADR is a tracked source record, and claiming its number means
# writing it inside the checkout from which this command was invoked. #452.
WHY_NO_WRITE_GUARD = (
    "docs/adr is tracked, and the claim is the file written inside this checkout"
)

# Kept as data so documentation can point here without copying a list that can drift.
DECLARED_LIMITS = (
    "a separate clone has a different worktree registry and is invisible",
    "a worktree that has not written its ADR yet is invisible",
    "an abandoned worktree keeps its number claimed and may leave a harmless gap",
)


class WorktreeListFailed(Exception):
    pass


@dataclass(frozen=True)
class AdrClaim:
    number: int
    filename: str


@dataclass(frozen=True)
class WorktreeClaims:
    root: Path
    claims: tuple[AdrClaim, ...]


@dataclass(frozen=True)
class WorktreeScan:
    roots: tuple[Path, ...]
    unreadable: tuple[Path, ...]
    numbers: tuple[int, ...]
    claims: tuple[WorktreeClaims, ...] = ()


def adr_claims(adr_dir: Path) -> list[AdrClaim]:
    """Return every four-digit ADR number and filename in an on-disk directory."""

    claims = []
    for path in adr_dir.iterdir():
        match = ADR_PREFIX.match(path.name)
        if path.is_file() and match:
            claims.append(AdrClaim(int(match.group("number")), path.name))
    return claims


def adr_numbers(adr_dir: Path) -> list[int]:
    return [claim.number for claim in adr_claims(adr_dir)]


def adr_numbers_are_unique(adr_dir: Path) -> bool:
    numbers = adr_numbers(adr_dir)
    return len(numbers) == len(set(numbers))


def run_git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def checkout_root(cwd: Path) -> Path:
    finished = run_git(cwd, "rev-parse", "--show-toplevel")
    if finished.returncode != 0:
        raise WorktreeListFailed(finished.stderr.strip() or "not inside a Git checkout")
    return Path(finished.stdout.strip()).resolve()


def worktree_roots(checkout: Path) -> tuple[Path, ...]:
    finished = run_git(checkout, "worktree", "list", "--porcelain")
    if finished.returncode != 0:
        raise WorktreeListFailed(finished.stderr.strip() or "git worktree list failed")
    roots = tuple(
        Path(line.removeprefix("worktree ")).resolve()
        for line in finished.stdout.splitlines()
        if line.startswith("worktree ")
    )
    if not roots:
        raise WorktreeListFailed("git worktree list returned no worktrees")
    return roots


def scan_worktrees(checkout: Path) -> WorktreeScan:
    roots = worktree_roots(checkout)
    unreadable = []
    numbers = []
    claims = []
    for root in roots:
        try:
            claimed = tuple(adr_claims(root / "docs" / "adr"))
            numbers.extend(claim.number for claim in claimed)
            claims.append(WorktreeClaims(root, claimed))
        except OSError:
            unreadable.append(root)
    return WorktreeScan(roots, tuple(unreadable), tuple(numbers), tuple(claims))


def report_coverage(scan: WorktreeScan) -> None:
    message = "coverage: {total} worktrees enumerated; {missing} unreadable".format(
        total=len(scan.roots), missing=len(scan.unreadable)
    )
    if scan.unreadable:
        message += ": " + ", ".join(str(path) for path in scan.unreadable)
    print(message, file=sys.stderr)


def slugify(title: str) -> str:
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.casefold()).strip("-")


def display_title(title: str) -> str:
    stripped = title.strip()
    return stripped[:1].upper() + stripped[1:]


def write_claim(checkout: Path, number: int, title: str) -> Path:
    slug = slugify(title)
    if not slug:
        raise ValueError("title must contain a letter or number")
    destination = checkout / "docs" / "adr" / f"{number:04d}-{slug}.md"
    body = "# {title}\n".format(title=display_title(title))
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(body)
    return destination


def staged_adr_claims(checkout: Path) -> tuple[AdrClaim, ...]:
    finished = run_git(
        checkout,
        "diff",
        "--cached",
        "--name-only",
        "-M",
        "--diff-filter=ACMR",
    )
    if finished.returncode != 0:
        raise OSError(finished.stderr.strip() or "could not read staged paths")
    claims = []
    for raw_path in finished.stdout.splitlines():
        normalized = raw_path.replace("\\", "/")
        if not normalized.startswith("docs/adr/"):
            continue
        filename = Path(normalized).name
        match = ADR_PREFIX.match(filename)
        if match:
            claims.append(AdrClaim(int(match.group("number")), filename))
    return tuple(claims)


def warn_about_staged_collisions(checkout: Path, scan: WorktreeScan) -> None:
    staged = set(staged_adr_claims(checkout))
    for worktree in scan.claims:
        if worktree.root == checkout:
            continue
        for claim in sorted(staged, key=lambda item: (item.number, item.filename)):
            conflicting = sorted(
                other.filename
                for other in worktree.claims
                if other.number == claim.number and other.filename != claim.filename
            )
            if not conflicting:
                continue
            print(
                "warning: staged ADR {number:04d} ({filename}) conflicts with {other} "
                "in {root}".format(
                    number=claim.number,
                    filename=claim.filename,
                    other=", ".join(conflicting),
                    root=worktree.root,
                ),
                file=sys.stderr,
            )


USAGE = 'usage: adr_next.py "title"'


def main(argv: list[str]) -> int:
    cwd = Path.cwd()
    try:
        checkout = checkout_root(cwd)
        scan = scan_worktrees(checkout)
    except (OSError, WorktreeListFailed) as error:
        print("coverage: 0 worktrees enumerated; 0 unreadable", file=sys.stderr)
        print(f"could not enumerate worktrees: {error}", file=sys.stderr)
        return 2

    report_coverage(scan)
    if argv == ["--check-staged"]:
        try:
            warn_about_staged_collisions(checkout, scan)
        except OSError as error:
            print(f"could not check staged ADRs: {error}", file=sys.stderr)
            return 2
        # This mode is advisory for the hook, which deliberately suppresses its
        # status. The writer's contract remains exact: no file written means 2.
        return 2
    if len(argv) != 1 or not argv[0].strip():
        print(USAGE, file=sys.stderr)
        return 2

    adr_dir = checkout / "docs" / "adr"
    if checkout in scan.unreadable or not adr_dir.is_dir():
        print(f"docs/adr is absent or unreadable: {adr_dir}", file=sys.stderr)
        return 2

    next_number = max(scan.numbers, default=0) + 1
    try:
        destination = write_claim(checkout, next_number, argv[0])
    except (FileExistsError, OSError, ValueError) as error:
        print(f"could not write ADR: {error}", file=sys.stderr)
        return 2
    print(destination.relative_to(checkout).as_posix())
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
