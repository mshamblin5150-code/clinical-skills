"""Exercise damaged machine Markdown through each owning public grader command."""
# phi-scan: synthetic
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support
import peer_critique_scan
import differential_scan
import filled_vitals_census
import test_checks_ledger as checks
import test_deck_scan as decks
import test_discussion_post_scan as posts
import test_discussion_reply_scan as replies
import test_peer_critique_scan as critiques


class PostedRecordCommands(unittest.TestCase):
    def check_faults(self, run, invoke):
        path = run / 'reread.md'
        original = path.read_bytes()
        for content, cause in ((original[:original.index(b'\n') + 1], 'wrong shape:'),
                               (b'[]', 'wrong shape:'), (None, 'could not be opened')):
            with self.subTest(content=content is None, cause=cause):
                path.unlink()
                if content is None:
                    path.mkdir()
                else:
                    path.write_bytes(content)
                frozen = run / 'frozen-grades.json'
                frozen.unlink(missing_ok=True)
                status, report, error = invoke()
                self.assertEqual(2, status, report + error)
                self.assertIn('reread.md: unreadable — ' + cause, report + error)
                self.assertIn('not graded', report)
                self.assertEqual(1, sum(line.startswith('unread remainder ') for line in report.splitlines()))
                self.assertIn('unread remainder 1', report)
                if content is None:
                    self.assertEqual([], list(path.iterdir()))
                    path.rmdir()
                else:
                    self.assertEqual(content, path.read_bytes())
                    path.unlink()
                path.write_bytes(original)

    def test_initial_post_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = posts.APostedInitialEntryHasItsOwnReading().posted_run(Path(directory))
            self.check_faults(run.root, run.grade)

    def test_reply_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = replies.Run(Path(directory))
            self.check_faults(run.root, lambda: replies.EveryPostedReplyHasALocatedReading().grade(run))

    def test_claim_heading_and_machine_faults_form_one_total_with_finding_precedence(self):
        for finding in (False, True):
            with self.subTest(finding=finding), tempfile.TemporaryDirectory() as directory:
                run = replies.Run(Path(directory))
                if finding:
                    response = run.root / 'response-maren.md'
                    response.write_text(replies.BODY.replace('12%', '17%', 1), encoding='utf-8')
                    run.write_heading_read()
                claims = run.root / 'claims.md'
                claims.write_text(claims.read_text(encoding='utf-8').replace(
                    '\nSTATUS: sourced', '\nUnknown claim-reader line.\nSTATUS: sourced', 1), encoding='utf-8')
                heading = run.root / 'heading-read.md'
                heading.write_text(heading.read_text(encoding='utf-8') + '\nUnknown heading-reader line.\n', encoding='utf-8')
                reading = run.root / 'reread.md'
                reading.write_bytes(b'[]')
                status, report, error = replies.EveryPostedReplyHasALocatedReading().grade(run)
                self.assertEqual(1 if finding else 2, status, report + error)
                self.assertEqual(['unread remainder 3'], [
                    line for line in report.splitlines() if line.startswith('unread remainder ')])
                self.assertIn('unread reader record: CLAIM:', report)
                self.assertIn('reread.md: unreadable', report)
                if finding:
                    self.assertIn('untraced-number', report)
                self.assertEqual(b'[]', reading.read_bytes())

    def test_peer_critique_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = critiques.build_run(root=Path(directory) / 'run')
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = peer_critique_scan.main([str(run)])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(run, invoke)

    def test_case_study_command(self):
        directory, path = checks.in_a_file(checks.whole_file())
        with directory:
            fixture = checks.ComposerAttachmentOutcome()
            fixture.prepare(path, 'inline')
            command = checks.checks
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with (
                    mock.patch.object(command.repo_root, 'output_root', return_value=path.parent / 'output'),
                    mock.patch.object(command.voice_read, 'apply_completion_gate', side_effect=lambda grade, *args, **kwargs: grade),
                    mock.patch.object(command.aar_scan, 'completion_gate', return_value=(False, 'the after-action review: clean')),
                    mock.patch.object(command.approval_record, 'completion_gate', return_value=(False, 'the approval record: clean')),
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err),
                ):
                    status = command.main([str(path), '--submission', 'case-study'])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(path.parent, invoke)

    def test_deck_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = decks.TheRenderedDeckRecordNamesTheTerminalPass().a_run(Path(directory))
            run.retain(1, 1)
            run.write_rendered()
            status, report, error = run.terminal()
            self.assertEqual(0, status, report + error)
            self.check_faults(run.root, lambda: run.terminal(bind=False))

    def test_both_clinical_submission_commands(self):
        from test_medatrax_readback_command import ReadbackCommand
        fixture = ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.run / 'note-3.md').write_text(
            'Start time 0800\nEnd time 0830\nDifferential:\n'
            '1. Cough - R05.9: most likely.\nFILLED·asserted BP 118/76 filled.\n', encoding='utf-8')
        (fixture.run / 'shift-values.json').write_text(
            '{"start":"0800","duration":{"hours":8,"minutes":0}}', encoding='utf-8')
        self.assertEqual(0, fixture.invoke('write'))
        for command in (differential_scan, filled_vitals_census):
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with (
                    mock.patch.object(command.aar_scan, 'completion_gate', return_value=(False, 'AAR: clean')),
                    mock.patch.object(command.artifact_repairs, 'completion_gate', return_value=(False, 'repairs: clean')),
                    mock.patch.object(command.delegated_answers, 'completion_gate', return_value=(False, 'answers: clean')),
                    mock.patch.object(command.approval_record, 'completion_gate', return_value=(False, 'approval: clean')),
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err),
                ):
                    status = command.main([str(fixture.run), '--submission', 'shift'])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(fixture.run, invoke)


if __name__ == '__main__':
    unittest.main()
