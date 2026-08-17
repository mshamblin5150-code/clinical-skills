"""Which checkout holds the corpus, which is not the one this file is in.

``Path(__file__).resolve().parent.parent`` is the **worktree** root. That is the
right answer for almost everything in ``tools/`` -- a test reading a committed
fixture, a tool writing into the tree it was run from -- and it is the wrong
answer for exactly one thing: ``scratch/``.

``scratch/`` is gitignored, so ``git worktree`` does not bring it. It exists in
the main clone and nowhere else. A tool that resolves it from its own location
therefore looks for the corpus inside a worktree that has never had one, finds
nothing, and -- if it is ``phi_scan`` -- switches off the layer that catches
patient names while continuing to exit 0. That is issue #93, and it was the
steady state for most commits made to this repo, because agents work in
worktrees.

**One place, because the ticket asked for one place.** #93's body says *if the
resolution changes, it should change in one place*, and when it was filed there
was none. ``main_repo_root`` already existed in ``guidelines_index.py``, written
for a different symptom of the same trap -- defaulting a 65 MB index relative to
a worktree puts it *inside* the repo while reading as outside one. It moved here
rather than being copied.

**What must not adopt this.** The count of modules repeating
``Path(__file__).resolve().parent.parent`` is not a to-do list, and #93's own
comment thread invites reading it as one. Most of them want the worktree: a test
reading ``fixtures/``, ``scan_all`` walking the files being committed, ``_git``
choosing a working directory. Making those adopt this would send a worktree's
scan into the wrong tree, which is worse than the bug being fixed. **Only a
caller reaching for ``scratch/`` wants the main checkout** -- that is the test,
and it is stated as a test rather than as a list on purpose.

An earlier draft of that sentence ended by counting the qualifying call sites.
It was correct when written, nothing recomputed it, and it sat four lines above
the warning that such a number goes stale -- #143's shape inside the paragraph
about #143, which is the same thing that happened to the module count in
``CLAUDE.md`` on this branch. Caught in review both times; the fix both times was
to state no number.

No subprocess, deliberately. ``git rev-parse --git-common-dir`` answers the same
question and #93 verified it, but it needs git on PATH and a process launch on a
path that runs inside a pre-commit hook. The ``.git`` pointer file is the same
fact, readable.
"""

from __future__ import annotations

from pathlib import Path


def main_repo_root(start: Path | None = None) -> Path:
    """The main checkout, which is not this worktree.

    ``start`` is a ``tools/`` directory; the root is its parent. It exists so the
    suite can stand in a checkout it built, since the thing under test is which
    tree you are in.

    A worktree's ``.git`` is a file naming ``<main>/.git/worktrees/<name>``, so
    the main checkout is three levels up from what it points at. **Only that
    exact shape is followed** -- a submodule's ``.git`` is also a pointer file
    and does not name a worktree, and walking one of those up three levels lands
    somewhere unrelated. Anything else, including no ``.git`` at all, is its own
    root: an exported tree has no parent checkout to find, and inventing one
    would point a scan at a tree nobody asked about.
    """
    root = (start or Path(__file__).resolve().parent).resolve().parent
    marker = root / ".git"
    if marker.is_file():
        pointer = marker.read_text(encoding="utf-8").split(":", 1)[-1].strip()
        gitdir = Path(pointer)
        if not gitdir.is_absolute():
            gitdir = (root / gitdir).resolve()
        # <main>/.git/worktrees/<name> -> <main>
        if gitdir.parent.parent.name == ".git":
            return gitdir.parent.parent.parent
    return root


def scratch_root(start: Path | None = None) -> Path:
    """The corpus directory, resolved to the checkout that actually holds one.

    **Returns the path whether or not it exists, and that is the point.** #93 is
    a ticket about a layer going quiet: a resolver that returned ``None`` for an
    absent corpus would hand its caller the same silence in a different shape.
    Absence is a finding, and the caller is the one that has to report it.
    """
    return main_repo_root(start) / "scratch"
