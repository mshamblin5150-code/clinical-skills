"""Every committed Git hook is executable, so a Linux or macOS clone runs it.

``core.hooksPath`` points Git at ``tools/hooks``. Git on Linux and macOS skips a
hook file that lacks the executable bit, and says nothing; Windows ignores the
bit. ``tools/hooks/pre-commit`` was committed as mode 100644, so in every Linux
cloud session the PHI scan, the scratch census and the other commit-time graders
never ran while the commits went through. This pins the mode Git records for
each hook, which is what a fresh clone checks out.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = "tools/hooks"
EXECUTABLE = "100755"


def tracked_hook_modes() -> dict[str, str]:
    """The index mode of each tracked file under ``tools/hooks``.

    This walks tracked files only: an untracked hook is not in the index, so a
    new hook is graded from the commit that adds it.
    """
    result = subprocess.run(
        ["git", "ls-files", "-s", "-z", "--", HOOKS],
        cwd=ROOT, capture_output=True, check=True,
    )
    modes: dict[str, str] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        meta, _, path = record.partition(b"\t")
        modes[path.decode("utf-8", "surrogateescape")] = meta.split(b" ")[0].decode("ascii")
    return modes


class EveryHookIsExecutable(unittest.TestCase):
    def test_the_population_is_not_empty(self) -> None:
        modes = tracked_hook_modes()
        self.assertIn(f"{HOOKS}/pre-commit", modes, "the hook walk read no pre-commit hook")

    def test_every_hook_is_recorded_executable(self) -> None:
        wrong = {path: mode for path, mode in tracked_hook_modes().items() if mode != EXECUTABLE}
        self.assertEqual({}, wrong, "a hook Git would skip on Linux and macOS: "
                         "run git update-index --chmod=+x on it")


if __name__ == "__main__":
    unittest.main()
