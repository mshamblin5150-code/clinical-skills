"""ADR 0393's overlapping reader populations through public commands.

phi-scan: synthetic
"""
import mechanics_test_support

setUpModule, tearDownModule = mechanics_test_support.module_hooks()

import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import tempfile
import unittest

import discussion_reply_scan as replies
from test_discussion_reply_scan import Run


class OneUnreadReport(unittest.TestCase):
    def test_claim_and_heading_members_form_a_disjoint_total(self):
        for heading_damage, expected in (("", 1), ("\nUnknown heading-reader line.\n", 2)):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                Run(root)
                claims = root / "claims.md"
                claims.write_text(claims.read_text(encoding="utf-8").replace(
                    "\nSTATUS: sourced", "\nUnknown claim-reader line.\nSTATUS: sourced", 1), encoding="utf-8")
                heading = root / "heading-read.md"
                heading.write_text(heading.read_text(encoding="utf-8") + heading_damage, encoding="utf-8")
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    code = replies.main([str(root)])
                self.assertEqual(2, code, output.getvalue())
                self.assertEqual([f"unread remainder {expected}"],
                                 [line for line in output.getvalue().splitlines() if line.startswith("unread remainder ")])
                self.assertIn("unread reader record: CLAIM:", output.getvalue())

    def test_bare_and_bound_heading_damage_each_count_once(self):
        for damage in ("\n## HEADING-READ\n", "\nUnrecognized reader prose.\n"):
            with self.subTest(damage=damage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                Run(root)
                heading = root / "heading-read.md"
                heading.write_text(heading.read_text(encoding="utf-8") + damage, encoding="utf-8")
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    code = replies.main([str(root)])
                text = output.getvalue()
                self.assertEqual(2, code, text)
                self.assertEqual(["unread remainder 1"],
                                 [line for line in text.splitlines() if line.startswith("unread remainder ")])
                self.assertTrue(any("unread" in line and not line.startswith("unread remainder ")
                                    for line in text.splitlines()), text)

    def test_clean_report_has_one_zero_and_no_unread_population_details(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Run(root)
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                code = replies.main([str(root)])
            text = output.getvalue()
            self.assertEqual(0, code, text)
            self.assertEqual(["unread remainder 0"],
                             [line for line in text.splitlines() if line.startswith("unread remainder ")])
            self.assertNotIn("unread reader record:", text)
