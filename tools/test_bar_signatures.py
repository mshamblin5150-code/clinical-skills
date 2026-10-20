"""Synthetic public signing and changed-bar controls for ADR 0397."""
# phi-scan: synthetic
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

import approval_record
import bar_signatures


class SharedBarSigning(unittest.TestCase):
    def test_each_new_skill_signs_and_refuses_changed_bytes(self):
        for skill in ("discussion-post", "discussion-reply", "peer-critique", "practicum-case-study"):
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                text = "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n"
                if skill == "discussion-post":
                    text += "TOPIC: Synthetic\nSYLLABUS: Synthetic\nWORD-FLOOR: 100\nWORD-CEILING: none\nREFERENCE-MINIMUM: 1\n"
                if skill == "practicum-case-study":
                    text += "SUBMISSION-TYPE: docx-upload\nRequired: explain the supplied synthetic case.\n"
                (run / "bar.md").write_text(text, encoding="utf-8")
                os.utime(run / "bar.md", (100, 100))
                messages = [{"type": "user", "timestamp": "2100-01-01T00:00:00Z", "message": {"content": "2"}}]
                with mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], False)), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(0, bar_signatures.main([str(run), "--skill", skill, "--reply", "2"]))
                self.assertFalse(bar_signatures.completion_gate(run, skill=skill)[0])
                retained = json.loads((run / "bar-signatures.json").read_text())["signatures"][-1]
                self.assertEqual("2", retained["clinician_reply"])
                (run / "bar.md").write_text((run / "bar.md").read_text() + "Changed requirement.\n")
                self.assertTrue(bar_signatures.completion_gate(run, skill=skill)[0])


if __name__ == "__main__":
    unittest.main()
