"""Fetch the tracker sweep's base before findings are trusted.

Ticket #320 records findings that were correct about a stale checkout and false
about the current repository. This command makes the remote read part of the
check instead of trusting a possibly stale remote-tracking reference.
"""

from __future__ import annotations

import subprocess
import sys

from console_codec import use_utf8


REMOTE = "origin"
BRANCH = "main"
REMOTE_REF = f"refs/remotes/{REMOTE}/{BRANCH}"


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def main() -> int:
    try:
        git(
            "fetch",
            "--no-tags",
            REMOTE,
            f"refs/heads/{BRANCH}:{REMOTE_REF}",
        )
    except subprocess.CalledProcessError:
        print(
            f"tracker-freshness: DID NOT CHECK -- `git fetch {REMOTE} "
            f"{BRANCH}` failed. No cached remote reference was trusted.",
            file=sys.stderr,
        )
        return 2
    head = git("rev-parse", "HEAD")
    upstream = git("rev-parse", REMOTE_REF)
    contains_main = subprocess.run(
        ["git", "merge-base", "--is-ancestor", REMOTE_REF, "HEAD"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if contains_main.returncode != 0:
        print(
            f"tracker-freshness: STALE HEAD={head} {REMOTE}/{BRANCH}={upstream}. "
            f"Run `git rebase {REMOTE}/{BRANCH}` or merge it, resolve any "
            "conflicts, rerun the relevant checks, then run this command again.",
            file=sys.stderr,
        )
        return 2
    print(f"tracker-freshness: FRESH HEAD={head} {REMOTE}/{BRANCH}={upstream}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
