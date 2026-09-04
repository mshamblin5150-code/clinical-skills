"""Which checkout holds the corpus, and which paths are inside a checkout at all.

Two questions about the same subject, and both used to be answered in several
places at once. ``main_repo_root``, ``scratch_root`` and ``output_root`` answer
*which tree owns shared state*. ``enclosing_checkout``,
``ensure_outside_checkout`` and ``ensure_main_checkout`` answer *would writing
here land in an allowed checkout*. They share the fact that a
worktree's ``.git`` is a file rather than a directory, which is the detail every
copy of either had to get right independently.

**This module is infrastructure rather than a tool another tool happens to
need**, which is the line ``CLAUDE.md`` draws around ``console_codec.py`` and the
test #253 states for when a helper may be shared: depending on it is the point,
not that two callers currently agree. A policy about where an artifact may land
passes that test -- #176's four writers were not converging by accident, they
were each encoding one rule about one repository. ``keyword_of`` fails it, and
stays copied.


``Path(__file__).resolve().parent.parent`` is the **worktree** root. That is the
right answer for almost everything in ``tools/`` -- a test reading a committed
fixture, a tool writing into the tree it was run from -- and it is the wrong
answer for the gitignored, account-owned ``scratch/`` and ``output/`` trees.

The tracker gates deliberately use that module root for the default-tree read,
the main-ancestry check, the default-branch fetch, and the GraphQL readback.
Refs live in the common Git directory, and the network call's working directory
is inert; an exported tree has no owning checkout to discover. These are
declared module-root uses, not account-owned-state lookups waiting to migrate.

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
for a different symptom of the same trap -- defaulting the index relative to
a worktree puts it *inside* the repo while reading as outside one. It moved here
rather than being copied.

**What must not adopt this.** The count of modules repeating
``Path(__file__).resolve().parent.parent`` is not a to-do list, and #93's own
comment thread invites reading it as one. Most of them want the worktree: a test
reading ``fixtures/``, ``scan_all`` walking the files being committed, ``_git``
choosing a working directory. Making those adopt this would send a worktree's
scan into the wrong tree, which is worse than the bug being fixed. **Only a
caller reaching for gitignored, account-owned state wants the main checkout** --
that is the test, stated as a property rather than as a list. Working material
lives under ``scratch/`` and finished submissions under ``output/``; neither
belongs to a disposable worktree.

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

from collections.abc import Iterable
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


def output_root(start: Path | None = None) -> Path:
    """The finished-submission directory in the checkout that survives worktrees.

    Like :func:`scratch_root`, this returns the path whether or not it exists.
    The producer decides when to create it; resolution must not silently choose
    a disposable worktree because that is where the command was launched.
    """
    return main_repo_root(start) / "output"


class InsideCheckout(ValueError):
    """A build artifact was aimed at a path inside a git checkout.

    **One exception type, because a caller could not handle *refused* uniformly**
    -- #176. The three writers raised ``SystemExit``, a module-local
    ``InsideRepo`` and nothing at all, so a fourth author choosing between them
    had three answers to pick from and wrote a fourth.

    A ``ValueError`` rather than a ``SystemExit``: this is a library refusal, and
    a command line that wants to exit converts it at its own boundary. The
    reverse cannot be done -- a helper raising ``SystemExit`` takes the decision
    to terminate away from every caller that is not a ``main``.

    ``target`` and ``checkout`` are carried rather than only formatted, because
    **the callers' reasons genuinely differ and the detection does not**: one is
    protecting an artifact from being materialized into every worktree, one
    is protecting a society's copyrighted expression (#87), and one is protecting
    a list of patient names. The rule is shared; the sentence is the caller's.
    """

    def __init__(self, target: Path, checkout: Path, detail: str = "") -> None:
        self.target = target
        self.checkout = checkout
        self.detail = detail
        message = (
            f"refusing to write inside a git checkout: {target}\n"
            f"  {checkout} is a repository."
        )
        super().__init__(f"{message}\n{detail}" if detail else message)


class ForeignCheckout(ValueError):
    """A finished submission was aimed at a checkout other than the main one.

    This is deliberately a sibling of :class:`InsideCheckout`. The outside-
    every-checkout policy and main-checkout-only policy point in opposite
    directions, so one call cannot raise both and their callers do not share a
    remedy.
    """

    def __init__(self, target: Path, expected: Path) -> None:
        self.target = target
        self.expected = expected
        super().__init__(
            f"refusing to write a finished submission into a foreign checkout: {target}\n"
            f"  use {expected / 'output'} instead."
        )


def enclosing_checkout(
    path: Path | str, permitted: Iterable[Path | str] = ()
) -> Path | None:
    """The git checkout this path would land in, or ``None``.

    **Walks up for a ``.git`` entry, which is the stronger of the two rules #176
    found.** Comparing against a list of known roots -- the worktree plus the
    clone that owns it -- misses a *sibling* worktree, and under
    ``.claude/worktrees/`` a sibling is the ordinary case here rather than an
    exotic one. It also misses any other repository the maintainer keeps nearby.
    The walk catches all three for the same cost.

    **A worktree's ``.git`` is a file, not a directory**, so this tests for
    existence and never for directory-ness. That is the detail each of the three
    copies had to get right independently.

    **The target itself is walked, not only its parents.** A directory target may
    *be* a checkout -- ``--out C:/codeing/clinical_skills`` -- and a rule that
    started at the parent would bless it.

    ``permitted`` is the parameter a shared rule needs and a single rule cannot
    have. ``name_index`` writes a list of patient names *inside* the repo on
    purpose, under ``scratch/``: it is gitignored, and ``phi_scan``'s path layer
    refuses a commit from there even under ``git add -f``. Each entry is a
    **resolved directory** and never a path component -- keyed on the name it
    would bless somebody else's ``~/scratch/`` on a coincidence, which is the
    narrowing that module found on its own first version. Containment is path
    ancestry rather than a string prefix, so ``scratch-old`` is not ``scratch``.

    **It answers *where*, and deliberately not *whose*.** Which directory a given
    worktree should write into is #276, and nothing here constrains it: the
    defaults live with the tools that own them, and a per-worktree output root is
    a change to a default rather than to this rule.
    """
    target = Path(path).expanduser().resolve()
    for allowed in permitted:
        if target.is_relative_to(Path(allowed).expanduser().resolve()):
            return None
    for candidate in (target, *target.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def ensure_outside_checkout(
    path: Path | str,
    permitted: Iterable[Path | str] = (),
    detail: str = "",
) -> Path:
    """The resolved target, or ``InsideCheckout`` naming what it landed in.

    ``detail`` is the caller's own sentence -- why *this* artifact must stay out
    -- appended to the two facts every refusal states.
    """
    target = Path(path).expanduser().resolve()
    checkout = enclosing_checkout(target, permitted)
    if checkout is not None:
        raise InsideCheckout(target, checkout, detail)
    return target


def ensure_main_checkout(path: Path | str, start: Path | None = None) -> Path:
    """The resolved target, or ``ForeignCheckout`` for a disposable checkout.

    A target under the main checkout is allowed. A target outside every checkout
    is also allowed so tests and deliberate exports can render in temporary
    directories. Only a target inside another checkout is refused.
    """
    target = Path(path).expanduser().resolve()
    expected = main_repo_root(start).resolve()
    checkout = enclosing_checkout(target)
    if checkout is not None and checkout.resolve() != expected:
        raise ForeignCheckout(target, expected)
    return target
