"""Public synthetic refusal controls for machine bookkeeping (ADR 0422)."""
# phi-scan: synthetic
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support
import artifact_repairs
import assignment_bar
import case_video
import discussion_artifact
import form_sections
import outbound_search
import reader_remarks
import run_grader
import run_record_reader as records
from test_assignment_bar import DECK_BAR
from test_form_sections import NOTE


class ToolRecordCommands(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'scratch' / 'runs' / 'synthetic'
        self.root.mkdir(parents=True)

    def damaged(self, path, invoke):
        path.parent.mkdir(parents=True, exist_ok=True)
        for content, cause in ((b'{', 'does not decode at line 1 column 2'),
                               (b'[]', 'wrong shape:'), (None, 'could not be opened')):
            with self.subTest(record=path.name, cause=cause):
                if content is None:
                    path.mkdir()
                else:
                    path.write_bytes(content)
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = invoke()
                report = out.getvalue() + err.getvalue()
                self.assertEqual(2, status, report)
                self.assertIn(': unreadable — ' + cause, report)
                self.assertIn('not graded', report)
                if content is None:
                    self.assertTrue(path.is_dir())
                    path.rmdir()
                else:
                    self.assertEqual(content, path.read_bytes())
                    path.unlink()

    def test_form_writer_and_explicit_replacement_preserve_damaged_record(self):
        source = self.root / 'entry-copies' / 'note-1.md'
        source.parent.mkdir()
        source.write_text(NOTE, encoding='utf-8')
        target = self.root / 'private' / 'form-sections' / 'note-1.json'
        for flags in ((), ('--replace',)):
            self.damaged(target, lambda: form_sections.main([str(source), *flags]))

    def test_bar_writer_preserves_damaged_signature_history_and_bar(self):
        bar = self.root / 'bar.md'
        bar.write_text(DECK_BAR, encoding='utf-8')
        original = bar.read_bytes()
        self.damaged(self.root / assignment_bar.RECORD,
                     lambda: assignment_bar.main([str(self.root), '--reply', 'Synthetic approval.']))
        self.assertEqual(original, bar.read_bytes())
        self.assertFalse((self.root / 'signed-bars').exists())

    def test_repair_report_uses_the_shared_refusal(self):
        self.damaged(artifact_repairs.ledger_path(self.root),
                     lambda: artifact_repairs.main(['report', str(self.root)]))

    def test_capture_command_refuses_before_heavy_environment_or_worker_launch(self):
        capture = self.root / 'case-video' / 'capture'
        fake_python = self.root / 'synthetic-python'
        fake_python.write_bytes(b'synthetic')
        self.damaged(capture / 'capture.json', lambda: case_video.main([
            'transcribe', str(self.root), '--python', str(fake_python),
            '--terms', str(capture / 'slide-terms.json'),
        ]))

    def test_outbound_writer_preserves_a_damaged_existing_log(self):
        path = self.root / outbound_search.SEARCHES
        with mock.patch.object(outbound_search, 'refusal', return_value=None):
            self.damaged(path, lambda: outbound_search.main([
                'check', 'synthetic clinical query', '--run', str(self.root), '--search-id', 'synthetic',
            ]))

    def test_receipt_rewriter_never_clears_a_failed_read(self):
        path = reader_remarks._receipt_path(self.root, 'discussion-post', 'post')
        path.parent.mkdir()
        for content in (b'{', b'[]'):
            path.write_bytes(content)
            with self.assertRaises(records.UnreadableRecord):
                reader_remarks.prepare(self.root, 'discussion-post', 'post', (), 'synthetic grade')
            self.assertEqual(content, path.read_bytes())

    def test_markdown_fault_keeps_independent_grade_and_one_coverage_total(self):
        path = self.root / 'reread.md'
        path.write_bytes(b'\xffPRIVATE-PLANTED')
        for finding in (False, True):
            def load(parsed):
                discussion_artifact.read_posted_reading_file(Path(parsed.source) / 'reread.md')
                return parsed.source
            command = run_grader.Grader(
                usage='synthetic <run>', options=(), load=load,
                grade=lambda source, parsed: run_grader.Grade(
                    source=source, scan=(), findings_failed=finding,
                    reports=('independent content check: ' + ('finding' if finding else 'clean'),),
                ),
                format_report=lambda scan, source, show=False: 'unread remainder 0',
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = run_grader.run(command, [str(self.root)])
            self.assertEqual(1 if finding else 2, status, output.getvalue())
            self.assertIn('independent content check:', output.getvalue())
            self.assertIn('reread.md: unreadable — does not decode at byte offset 0', output.getvalue())
            self.assertEqual(1, output.getvalue().count('unread remainder'))
            self.assertIn('unread remainder 1', output.getvalue())
            self.assertIn('not graded', '\n'.join(reader_remarks.coverage_lines(output.getvalue())))
            self.assertNotIn('PRIVATE-PLANTED', output.getvalue())


if __name__ == '__main__':
    unittest.main()
