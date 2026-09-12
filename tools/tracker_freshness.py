"""Fetch the tracker sweep's base before findings are trusted.

Ticket #320 records findings that were correct about a stale checkout and false
about the current repository. This command makes the remote read part of the
check instead of trusting a possibly stale remote-tracking reference.

Exit status distinguishes not having checked from having checked and found
nothing wrong, which is the convention every graded command in ``tools/``
states. Ticket #744 ruled the earlier collapse of the two non-zero limbs a
defect:

* ``0`` -- ``FRESH``. The fetch ran and ``HEAD`` contains the fetched commit.
* ``1`` -- ``STALE``. The gate ran and found the thing it exists to find. This
  is a finding about the base, not a failure to look.
* ``2`` -- ``DID NOT CHECK``. No verdict about the base was reached, because a
  git command the gate depends on did not complete.

**Every route to 2 is a route that checked nothing, and that is the whole
point of the split.** A failed fetch is the documented one; a ``git`` binary
that cannot be executed, a ``rev-parse`` that fails after a successful fetch,
and a ``merge-base --is-ancestor`` that neither confirms nor denies ancestry
all reach it too. Before #744 those three escaped as an uncaught traceback and
the process exited **1** -- which under the house convention reads as *ran and
found something*, and which after this change would be indistinguishable from
``STALE``. That is ticket #150's traceback-becomes-a-verdict shape, and
repairing only the ``STALE`` limb would have made it worse rather than better.
"""

from __future__ import annotations

import subprocess
import sys

from console_codec import require_python_floor, use_utf8
import git_ancestry


REMOTE = "origin"
BRANCH = "main"
REMOTE_REF = f"refs/remotes/{REMOTE}/{BRANCH}"

FRESH = 0
STALE = 1
DID_NOT_CHECK = 2

COMMIT_BASE_SCOPE = "tracker records"
NOT_REACHED = (
    (
        COMMIT_BASE_SCOPE,
        "The gate reads the commit base and no tracker record.",
    ),
    (
        "record verdict currency",
        "A verdict about a tracker record is current only as of when it was read.",
    ),
    (
        "aggregate verdicts",
        "A verdict naming no record number is reached by no mechanism, permanently.",
    ),
)

class DidNotCheck(RuntimeError):
    """A git command the gate depends on did not complete."""


def scope_clause() -> str:
    """Render the command-line qualifier from the declaration it exposes."""

    scope = next(reason for subject, reason in NOT_REACHED if subject == COMMIT_BASE_SCOPE)
    return f"Scope: {scope}"


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run one git command, converting every failure-to-run into DidNotCheck."""

    try:
        return subprocess.run(
            ["git", *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError as failure:
        raise DidNotCheck(f"`git {' '.join(args)}` could not run: {failure}") from failure


def git(*args: str) -> str:
    completed = run_git(*args)
    if completed.returncode != 0:
        raise DidNotCheck(f"`git {' '.join(args)}` failed")
    return completed.stdout.strip()


def main() -> int:
    try:
        git("fetch", "--no-tags", REMOTE, f"refs/heads/{BRANCH}:{REMOTE_REF}")
        head = git("rev-parse", "HEAD")
        upstream = git("rev-parse", REMOTE_REF)
        contains_main = git_ancestry.is_ancestor(
            REMOTE_REF, "HEAD", run_git=run_git
        )
        if contains_main is None:
            raise DidNotCheck(
                "`git merge-base --is-ancestor` neither confirmed nor denied ancestry"
            )
    except DidNotCheck as failure:
        print(
            f"tracker-freshness: DID NOT CHECK -- {failure}. No cached remote "
            "reference was trusted and no verdict about the base was reached. "
            f"{scope_clause()}",
            file=sys.stderr,
        )
        return DID_NOT_CHECK
    if contains_main is False:
        print(
            f"tracker-freshness: STALE HEAD={head} {REMOTE}/{BRANCH}={upstream}. "
            f"Run `git rebase {REMOTE}/{BRANCH}` or merge it, resolve any "
            "conflicts, rerun the relevant checks, then run this command again. "
            f"{scope_clause()}",
            file=sys.stderr,
        )
        return STALE
    print(
        f"tracker-freshness: FRESH HEAD={head} {REMOTE}/{BRANCH}={upstream}. "
        f"{scope_clause()}"
    )
    return FRESH


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
