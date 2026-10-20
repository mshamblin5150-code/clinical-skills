"""Exercise the saved-return writer with synthetic private markers."""
from __future__ import annotations

import artifact_lock_test_support
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import refutation_apply as apply
import research_ledger as ledger
from prose_bind import NAMING, bind

MARKER = "PRIVATE_MARKER"


def returned(heading=MARKER, verdict="stands - checked the passage"):
    return (f"## CLAIM: {heading}\nREFUTATION: {verdict}\n"
            f"TESTED-HEADING: {ledger.heading_digest(heading)}\n"
            "SECOND-ROUTE: HTML -> rendered PDF\n")


class ApplyReturns(unittest.TestCase):
    def test_limits_are_named_without_copying_the_rows(self):
        surface = Path(__file__).resolve().parent.parent / "CLAUDE.md"
        self.assertEqual((), bind(apply.DECLARED_LIMITS, surface.read_text(encoding="utf-8"), mode=NAMING))

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / "claims.md"
        self.path.write_text(f"DATE: 2026-10-12\n\n## CLAIM: {MARKER}\nSTATUS: sourced\n", encoding="utf-8")
        self.input = self.root / f"{MARKER}.md"

    def run_return(self, text, show=False):
        self.input.write_text(text, encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = apply.main([str(self.path), str(self.input)] + (["--show"] if show else []))
        if not show:
            self.assertNotIn(MARKER, output.getvalue())
        return code, output.getvalue()

    def test_apply_retry_snapshot_and_one_step_write(self):
        original = self.path.read_bytes()
        text = returned() + f"REMARK: {MARKER} outside the question\n"
        with mock.patch.object(apply.records.os, "replace", wraps=apply.records.os.replace) as replace:
            self.assertEqual(0, self.run_return(text)[0])
            replace.assert_called_once()
        self.assertEqual(original, (self.root / "claims-snapshot-1.md").read_bytes())
        self.assertEqual(self.input.read_bytes(), (self.root / "refutations" / self.input.name).read_bytes())
        updated = self.path.read_bytes()
        self.assertIn("already applied 1", self.run_return(text)[1])
        self.assertEqual(updated, self.path.read_bytes())
        self.assertFalse((self.root / "claims-snapshot-2.md").exists())

    def test_replaces_expired_fields_and_keeps_remarks(self):
        self.path.write_text(returned().replace(ledger.heading_digest(MARKER), "0" * 64)
                             + "INSTRUMENTS: old tool -> other tool\nREMARK: old remark\n", encoding="utf-8")
        code, output = self.run_return(returned() + "REMARK: new remark\n")
        self.assertEqual(0, code)
        self.assertIn("replaced 1", output)
        record = ledger.read_records(self.path.read_text(encoding="utf-8"))[0]
        self.assertNotIn("INSTRUMENTS", record.fields)
        self.assertEqual(("old remark", "new remark"), record.remarks)

    def test_live_conflict_and_kept_file_conflict(self):
        self.path.write_text(returned(verdict="refuted - wrong passage"), encoding="utf-8")
        self.assertEqual(1, self.run_return(returned())[0])
        self.assertEqual(1, self.run_return(returned(verdict="paywalled - body unavailable"))[0])
        self.assertFalse((self.root / "claims-snapshot-1.md").exists())

    def test_stale_unmatched_ambiguous_and_malformed(self):
        original = self.path.read_bytes()
        self.assertEqual(1, self.run_return(returned().replace(ledger.heading_digest(MARKER), "0" * 64))[0])
        self.input = self.root / "unmatched.md"
        self.assertEqual(1, self.run_return(returned(MARKER + " other"))[0])
        self.input = self.root / "ambiguous.md"
        self.path.write_bytes(original + original)
        self.assertEqual(1, self.run_return(returned())[0])
        self.input = self.root / "malformed.md"
        code, output = self.run_return(returned() + f"stray {MARKER}\n")
        self.assertEqual(2, code)
        self.assertIn("unread remainder 1", output)

    def test_partial_write_and_status_precedence(self):
        code, output = self.run_return(returned() + returned(MARKER + " unmatched") + f"stray {MARKER}\n")
        self.assertEqual(2, code)  # malformed whole second block, not unmatched
        self.assertIn("applied 1", output)
        self.input = self.root / "mixed.md"
        code, output = self.run_return(returned(MARKER + " unmatched") + returned() + f"stray {MARKER}\n")
        self.assertEqual(1, code)
        self.assertIn("unread remainder 1", output)

    def test_unreadable_no_record_no_block_and_show(self):
        self.assertEqual(2, self.run_return(f"stray {MARKER}\n")[0])
        self.input = self.root / "show.md"
        self.assertIn(MARKER, self.run_return(returned(), show=True)[1])
        self.path.write_text("DATE: 2026-10-12\n", encoding="utf-8")
        self.assertEqual(2, self.run_return(returned())[0])
        self.path.unlink()
        self.assertEqual(2, self.run_return(returned())[0])

    def test_wrapped_fields_and_incomplete_return_are_copied(self):
        text = f"## CLAIM: {MARKER}\nREFUTATION: unreadable - two attempts\n    failed on the body\nINSTRUMENTS: HTML -> PDF\n"
        self.assertEqual(0, self.run_return(text)[0])
        self.assertIn("    failed on the body", self.path.read_text(encoding="utf-8"))

    def test_indented_unknown_field_refuses_whole_block(self):
        original = self.path.read_bytes()
        self.assertEqual(2, self.run_return(returned() + "    STATUS: sourced\n")[0])
        self.assertEqual(original, self.path.read_bytes())

    def test_ledger_heading_boundaries_use_the_imported_reader(self):
        self.path.write_text(f"  # claim : {MARKER}\nSTATUS: sourced\n"
                             + returned(MARKER + " other"), encoding="utf-8")
        self.assertEqual(0, self.run_return(returned())[0])
        records = ledger.read_records(self.path.read_text(encoding="utf-8"))
        self.assertEqual(2, len(records))
        self.assertEqual(ledger.heading_digest(MARKER), records[0].value("TESTED-HEADING"))
        self.assertEqual(ledger.heading_digest(MARKER + " other"), records[1].value("TESTED-HEADING"))

    def test_missing_input_and_non_utf8_are_bounded(self):
        for raw in (None, b"\xff"):
            with self.subTest(raw=raw):
                if raw is None:
                    self.input.unlink(missing_ok=True)
                else:
                    self.input.write_bytes(raw)
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(2, apply.main([str(self.path), str(self.input)]))
                self.assertNotIn(MARKER, output.getvalue())
                self.assertIn("unread remainder 1", output.getvalue())
                self.assertIn("read 0, applied 0", output.getvalue())

    def test_identical_retry_preserves_mixed_line_endings(self):
        text = returned()
        original = text.replace("\n", "\r\n", 1).encode("utf-8")
        self.path.write_bytes(original)
        self.assertEqual(0, self.run_return(text)[0])
        self.assertEqual(original, self.path.read_bytes())
        self.assertFalse((self.root / "claims-snapshot-1.md").exists())

    def test_snapshot_sequence_and_atomic_failure_preserve_ledger(self):
        snapshot = self.root / "claims-snapshot-1.md"
        snapshot.write_bytes(b"previous snapshot")
        original = self.path.read_bytes()
        with mock.patch.object(apply.records.os, "replace", side_effect=OSError):
            self.assertEqual(2, self.run_return(returned())[0])
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(b"previous snapshot", snapshot.read_bytes())
        self.assertEqual(original, (self.root / "claims-snapshot-2.md").read_bytes())
        self.assertEqual([], list(self.root.glob(".refutation-*")))

    def test_multiple_groups_counts_and_new_remarks_on_retry(self):
        self.assertEqual(0, self.run_return(returned())[0])
        self.input = self.root / "second.md"
        code, output = self.run_return(returned() + "REMARK: new remark\n")
        self.assertEqual(0, code)
        self.assertIn("already applied 1", output)
        self.assertIn("new remark", self.path.read_text(encoding="utf-8"))
        self.assertEqual(0, self.run_return(returned() + "REMARK: new remark\n")[0])
        output = io.StringIO()
        first = self.root / f"{MARKER}.md"
        with redirect_stdout(output):
            self.assertEqual(0, apply.main([str(self.path), str(first), str(self.input)]))
        self.assertIn("file 1 of 2", output.getvalue())
        self.assertIn("file 2 of 2", output.getvalue())
        self.assertNotIn(MARKER, output.getvalue())


if __name__ == "__main__":
    unittest.main()
