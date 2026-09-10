"""Public-boundary tests for the pure threshold-sheet grammar module."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parent


class GrammarModuleBoundary(unittest.TestCase):
    def test_importing_grammar_does_not_load_the_gate_module(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import threshold_grammar; "
                "assert 'threshold_sheet' not in sys.modules",
            ],
            cwd=TOOLS_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
