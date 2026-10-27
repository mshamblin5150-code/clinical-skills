"""Pin each member's public missing/stale/clean contract with synthetic runs."""



import mechanics_test_support

setUpModule, tearDownModule = mechanics_test_support.module_hooks()

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import approval_record
import assignment_submission
from project_context_test_support import write_none_context
import file_digest
import medatrax_posting
import test_checks_ledger as checks
import test_deck_scan as deck
import test_discussion_post_scan as post
import test_discussion_reply_scan as reply
import test_medatrax_posting as portal
import test_peer_critique_scan as critique
import test_assignment_submission as assignment


class PostedReadingMembers(unittest.TestCase):
    def assert_grader_controls(self, record, grade, missing_kind, fingerprint_kind):
        clean = record.read_text(encoding='utf-8')
        for text, status, kind in (
            (clean, 0, None),
            # Keep a valid envelope but omit this member, without fixture helpers
            # recreating an absent file or treating empty bytes as a missing record.
            (re.sub(r'(?m)^## REREAD:.*$', '## REREAD: unrelated-synthetic-item', clean), 1, missing_kind),
            (re.sub(r'(?m)^SUBMISSION-SHA256:.*$', 'SUBMISSION-SHA256: ' + 'f' * 64, clean), 1, fingerprint_kind),
        ):
            with self.subTest(status=status, kind=kind):
                record.write_text(text, encoding='utf-8')
                result, report, errors = grade()
                self.assertEqual(status, result, report + errors)
                if kind:
                    self.assertRegex(report, rf'(?m)^\s*(?:#\d+ - )?{kind}(?::|\s)\s*1\b')

    def test_post_kinds_and_exit_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = post.APostedInitialEntryHasItsOwnReading().posted_run(Path(temporary))
            self.assert_grader_controls(run.root / 'reread.md', run.grade,
                                       'missing-posted-reading', 'submission-fingerprint')

    def test_reply_kinds_and_exit_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = reply.Run(Path(temporary))
            self.assert_grader_controls(run.root / 'reread.md',
                                       lambda: reply.EveryPostedReplyHasALocatedReading().grade(run),
                                       'missing-posted-reading', 'submission-fingerprint')

    def test_critique_kinds_and_exit_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = critique.build_run(root=Path(temporary) / 'run')
            def grade():
                scan = critique.graded(run)
                return (int(bool(scan.findings)), critique.scan.format_report(scan, str(run)), '')
            self.assert_grader_controls(run / 'reread.md', grade,
                                       'missing-posted-reading', 'submission-fingerprint')

    def test_deck_kinds_and_gate_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = deck.TheRenderedDeckRecordNamesTheTerminalPass().a_run(Path(temporary))
            run.retain(1, 1)
            run.write_rendered()
            run.write_reread()
            self.assert_grader_controls(run.root / 'reread.md', run.terminal,
                                       'submission-fingerprint', 'submission-fingerprint')

    def test_checks_ledger_kinds_and_gate_results(self):
        directory, path = checks.in_a_file(checks.whole_file())
        with directory, mock.patch.object(checks.checks.aar_scan, 'completion_gate', return_value=(False, 'the after-action review: clean')), mock.patch.object(checks.checks.approval_record, 'completion_gate', return_value=(False, 'the approval record: clean')):
            def grade():
                return checks.run([str(path), '--submission', 'case-study'])
            self.assertEqual(0, grade()[0])
            self.assert_grader_controls(path.parent / 'reread.md', grade,
                                       'submission-fingerprint', 'submission-fingerprint')

    def assert_gate_controls(self, record, grade):
        clean = record.read_text(encoding='utf-8')
        for text, failed, detail in (
            (clean, False, 'clean'),
            (re.sub(r'(?m)^## REREAD:.*$', '## REREAD: unrelated-synthetic-item', clean), True,
             'no REREAD record for the submission'),
            (re.sub(r'(?m)^SUBMISSION-SHA256:.*$', 'SUBMISSION-SHA256: ' + 'f' * 64, clean), True,
             'SUBMISSION-SHA256 is missing, malformed, or stale'),
        ):
            with self.subTest(failed=failed, detail=detail):
                record.write_text(text, encoding='utf-8')
                result, report = grade()
                self.assertEqual(failed, result, report)
                self.assertIn(detail, report)

    def test_medatrax_gate_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            note = run / 'note-1.md'
            note.write_bytes(b'synthetic note')
            record = run / 'reread.md'
            record.write_text(portal.reading(file_digest.sha256(note)), encoding='utf-8')
            self.assert_gate_controls(record, lambda: medatrax_posting.completion_gate(run, portal.SUBMISSION, batch=True))

    def test_approval_gate_results(self):
        # Posted-reading mutation controls isolate transcript prerequisites.
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(approval_record, '_preflight_grader', return_value=None), mock.patch.object(
            approval_record, 'verify_clinician_reply',
            return_value=approval_record.ReplyVerification('verified', 'synthetic whole reply matched', 4102444800),
        ), mock.patch.object(approval_record.canvas_load_route, 'require_shown'):
            run = Path(temporary)
            note = run / 'post.md'
            note.write_bytes(b'approved post')
            write_none_context(run)
            with mock.patch.object(approval_record.reader_remarks, "verify", return_value=[]):
                approval_record.approve(run, skill='discussion-post', submission='post', sources=(note,), grader_args=(str(run),), content_approved=True, clinician_reply='Approve the synthetic post.')
                approval_record.approve(run, skill='discussion-post', submission='post', sources=(note,), grader_args=(str(run),), content_approved=True, clinician_reply='Post the synthetic loaded box.', approval_kind='posting')
            approval_record.record_agent_posting(run, skill='discussion-post', submission='post')
            record = run / 'reread.md'
            record.write_text('## REREAD: post\nPOST-URL: https://example.org/post\n'
                              'POSTED: 2100-01-01\nREAD: 2100-01-01\n'
                              'VERDICT: matches - the posted text equals the approved artifact\n'
                              'SUBMISSION-SHA256: ' + file_digest.sha256(note) + '\n', encoding='utf-8')
            self.assert_gate_controls(record, lambda: approval_record.completion_gate(run, 'discussion-post', 'post'))

    def test_assignment_gate_results(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(assignment_submission, '_pre_upload_grade', return_value=(True, 'pre-upload grade: clean')):
            run = Path(temporary)
            document = run / 'assignment.pptx'
            document.write_bytes(b'reviewed deck')
            helper = assignment.TwoGateUpload()
            helper._completed_submission(run, document)
            with helper._canonical_copy(run / 'canonical', document):
                self.assert_gate_controls(run / 'reread.md', lambda: assignment_submission.completion_gate(run, document, submission='assignment'))
