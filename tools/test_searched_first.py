"""First-stop search records through the ledger command. #1503."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import research_ledger as ledger
from test_research_ledger import CLEAN, ledger_text, replace_field, write_bar


class SearchedFirstCommand(unittest.TestCase):
    def command(self, field):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_bar(root)
            path = root / "claims.md"
            path.write_text(ledger_text(replace_field(CLEAN, "SEARCHED-FIRST", field)), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                status = ledger.main([str(path), "--show"])
            return status, output.getvalue()

    def test_missing_search_line_is_refused(self):
        status, report = self.command(None)
        self.assertEqual(status, 1, report)
        self.assertIn("SEARCHED-FIRST", report)

    def test_missing_store_search_is_refused(self):
        status, report = self.command('guidelines "pregnancy" -> 0')
        self.assertEqual(status, 1, report)

    def test_missing_guideline_search_is_refused(self):
        status, report = self.command('store "pregnancy" -> 0')
        self.assertEqual(status, 1, report)

    def test_both_searches_with_zero_hits_pass(self):
        status, report = self.command('store "pregnancy" -> 0; guidelines "pregnancy" -> 0')
        self.assertEqual(status, 0, report)
