"""Form-section artifact command at its file boundary."""

# phi-scan: synthetic

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


COMMAND = Path(__file__).with_name("form_sections.py")
NOTE = "Preamble\n## S\nsubject\nO:\nobject\n## A:\nassess\n## P:\nplan\nCoding worksheet\ntail\n"


class FormSectionsCommand(unittest.TestCase):
    def test_create_compare_diverge_and_explicit_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            copy = run / "entry-copies" / "note-1.md"
            copy.parent.mkdir()
            copy.write_text(NOTE, encoding="utf-8")
            artifact = run / "private" / "form-sections" / "note-1.json"

            def invoke(*extra: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run([sys.executable, str(COMMAND), str(copy), *extra],
                                      capture_output=True, text=True, encoding="utf-8", errors="replace")

            created = invoke()
            self.assertEqual(0, created.returncode, created.stderr)
            self.assertIn("created", created.stdout)
            self.assertIn("unread remainder 0", created.stdout)
            self.assertEqual({"S": "subject", "O": "object", "A": "assess", "P": "plan"},
                             json.loads(artifact.read_text(encoding="utf-8")))
            self.assertEqual(0, invoke().returncode)
            copy.write_text(NOTE.replace("assess", "new assess"), encoding="utf-8")
            divergent = invoke()
            self.assertEqual(0, divergent.returncode)
            self.assertIn("diverged", divergent.stdout)
            self.assertEqual("assess", json.loads(artifact.read_text(encoding="utf-8"))["A"])
            self.assertEqual(0, invoke("--replace").returncode)
            self.assertEqual("new assess", json.loads(artifact.read_text(encoding="utf-8"))["A"])

    def test_unknown_plan_closer_refuses_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            copy = run / "entry-copies" / "note-1.md"
            copy.parent.mkdir()
            copy.write_text(NOTE.replace("Coding worksheet", "Unknown closer"), encoding="utf-8")
            result = subprocess.run([sys.executable, str(COMMAND), str(copy)],
                                    capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(2, result.returncode)
            self.assertFalse((run / "private" / "form-sections" / "note-1.json").exists())


if __name__ == "__main__":
    unittest.main()
