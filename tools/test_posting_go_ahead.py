"""Posting approval kinds and the dated historical boundary. #1502."""
import artifact_lock_test_support
import json
import tempfile
import unittest
import artifact_lock_test_support
from pathlib import Path
from unittest import mock
import approval_record as approvals
from project_context_test_support import write_none_context

class PostingGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name); write_none_context(self.run)
        self.source = self.run / 'draft.md'; self.source.write_text('Synthetic text.', encoding='utf-8')
        for name, value in (('_preflight_grader', None), ('_pre_post_grade', (0, 'clean')),
                            ('verify_shown_text', approvals.ReplyVerification('verified', 'synthetic', 2100000000.0))):
            patch = mock.patch.object(approvals, name, return_value=value); patch.start(); self.addCleanup(patch.stop)
        patch = mock.patch.object(approvals.reader_remarks, 'verify', return_value=[])
        patch.start(); self.addCleanup(patch.stop)
        self.tick = 2100000000.0
        patch = mock.patch.object(approvals, 'verify_clinician_reply', side_effect=self.reply)
        patch.start(); self.addCleanup(patch.stop)
        patch = mock.patch.object(approvals, '_recheck_replies', side_effect=lambda *a: approvals.ReplyVerification('verified', 'synthetic', self.tick))
        patch.start(); self.addCleanup(patch.stop)

    def reply(self, *args, **kwargs):
        self.tick += 1
        return approvals.ReplyVerification('verified', 'synthetic', self.tick)

    def approve(self, kind='content', skill='discussion-post'):
        return approvals.approve(self.run, skill=skill, submission='draft', sources=(self.source,),
                                 grader_args=(str(self.run),), content_approved=True,
                                 clinician_reply='Synthetic approval.', approval_kind=kind)

    def finish(self, skill='discussion-post', clinician=False):
        recorder = approvals.record_clinician_posting if clinician else approvals.record_agent_posting
        recorder(self.run, skill=skill, submission='draft')
        (self.run / 'reread.md').write_text('## REREAD: draft\nPOST-URL: https://example.test/post\n'
          'POSTED: 2026-10-11\nREAD: 2026-10-11\nSUBMISSION-SHA256: ' + approvals.source_sha256((self.source,)) +
          '\nVERDICT: matches - synthetic text matches\n', encoding='utf-8')
        return approvals.completion_gate(self.run, skill, 'draft')

    def test_all_four_agent_posting_skills_owe_a_later_posting_approval(self):
        for skill in approvals.POSTING_GO_AHEAD_SKILLS:
            with self.subTest(skill=skill):
                (self.run / approvals.RECORD).unlink(missing_ok=True)
                self.approve(skill=skill)
                failed, report = self.finish(skill)
                self.assertTrue(failed); self.assertIn('Posting go-ahead', report)
                self.approve('posting', skill)
                self.assertFalse(self.finish(skill)[0])
                rows = json.loads((self.run / approvals.RECORD).read_text(encoding='utf-8'))['items'][-1]['approvals']
                self.assertEqual(['content', 'posting'], [row['approval_kind'] for row in rows])

    def test_two_content_approvals_are_not_a_posting_approval(self):
        self.approve(); self.approve()
        self.assertTrue(self.finish()[0])

    def test_clinician_route_owes_no_posting_approval(self):
        self.approve()
        self.assertFalse(self.finish(clinician=True)[0])

    def test_historical_content_approval_is_graded_as_before(self):
        self.approve()
        path = self.run / approvals.RECORD
        payload = json.loads(path.read_text(encoding='utf-8'))
        row = payload['items'][0]['approvals'][0]
        row['recorded_at'] = approvals.POSTING_GO_AHEAD_CUTOFF - 1
        path.write_text(json.dumps(payload), encoding='utf-8')
        self.assertFalse(self.finish()[0])
        row.pop('approval_kind'); row.pop('recorded_at')
        row['reply_matched_at'] = approvals.POSTING_GO_AHEAD_CUTOFF - 1
        path.write_text(json.dumps(payload), encoding='utf-8')
        self.assertFalse(self.finish()[0])

    def test_cutoff_itself_is_not_historical(self):
        self.approve()
        path = self.run / approvals.RECORD
        payload = json.loads(path.read_text(encoding='utf-8'))
        payload['items'][0]['approvals'][0]['recorded_at'] = approvals.POSTING_GO_AHEAD_CUTOFF
        path.write_text(json.dumps(payload), encoding='utf-8')
        self.assertTrue(self.finish()[0])

    def test_changed_bytes_need_a_new_content_and_posting_approval(self):
        self.approve(); self.approve('posting')
        self.source.write_text('Changed text.', encoding='utf-8')
        with self.assertRaisesRegex(approvals.ApprovalRecordError, 'same fingerprint'):
            self.approve('posting')
        self.approve()
        self.assertTrue(self.finish()[0])
        self.approve('posting')
        self.assertFalse(self.finish()[0])

    def test_posting_cannot_be_first_or_an_unknown_kind(self):
        with self.assertRaises(approvals.ApprovalRecordError): self.approve('posting')
        with self.assertRaises(approvals.ApprovalRecordError): self.approve('other')

if __name__ == '__main__': unittest.main()
