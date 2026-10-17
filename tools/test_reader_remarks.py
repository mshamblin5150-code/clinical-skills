"""ADR 0330 through both public approval seams; all prose is synthetic.

phi-scan: synthetic
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import aar_scan
import approval_record as approvals
import assignment_submission as assignments
import checks_ledger
import deck_scan
import heading_read
import reader_remarks as remarks
import research_ledger
import voice_read
from project_context_test_support import write_none_context
from prose_bind import NAMING, bind


class ReaderRecordContracts(unittest.TestCase):
    def test_the_shared_contract_names_the_gate_ceiling_without_copying_it(self):
        text = (Path(__file__).resolve().parents[1] / "skills/_shared/reference/sourcing.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(remarks.DECLARED_LIMITS, text, mode=NAMING))

    def test_heading_remarks_leave_the_verdict_and_unknown_prose_is_unread(self):
        from test_heading_read import record, scan
        result = scan(record() + 'REMARK: Clarify the secondary citation.\nextra prose\n')
        self.assertFalse(result.findings)
        self.assertEqual(1, result.unread)
        self.assertEqual('Clarify the secondary citation.', result.remarks[0].text)
        self.assertIn('draft.md', result.unread_records)
        sibling = record().replace('draft.md', 'other.md') + 'extra prose\nREMARK: Other artifact.\n'
        result = scan(record() + sibling)
        self.assertEqual(0, result.unread)
        self.assertEqual((), result.remarks)

    def test_claim_and_check_keep_repeated_remarks_and_prefield_prose(self):
        for module, header, attribute in ((research_ledger, 'CLAIM', 'claim'), (checks_ledger, 'CHECK', 'check')):
            with self.subTest(module=module.__name__):
                verdict = 'STATUS: sourced' if header == 'CLAIM' else 'VERDICT: clean'
                record = module.read_records(f'## {header}: Synthetic\nunrecognized prose\nREMARK: First.\nREMARK: Second.\n{verdict}\n')[0]
                self.assertEqual(('First.', 'Second.'), record.remarks)
                self.assertEqual(1, record.unread)

    def test_discussion_visual_unknown_fields_and_empty_remarks_are_unread(self):
        import discussion_post_scan
        text = "## RENDERED: draft.md\nPAGES: 1 of 1 imaged\nSOURCE: word-pdf\nUNSEEN: none\nREAD: 2026-10-11\nVERDICT: clean - compared pixels\nEXTRA: Unknown field\nREMARK: \nREMARK: Keep this real remark.\n"
        records = discussion_post_scan._rendered_readings(text)
        self.assertEqual(1, len(records))
        self.assertEqual(2, records[0].unread)
        self.assertEqual(("Keep this real remark.",), records[0].remarks)
        self.assertEqual((), records[0].errors)

    def test_visual_remarks_and_unknown_lines_are_retained(self):
        record = deck_scan._rendered_records('## RENDERED: deck.pptx\nREMARK: Citation needs work.\nunknown prose\nVERDICT: clean - pixels compared\n')[0]
        self.assertEqual(('Citation needs work.',), record.remarks)
        self.assertEqual(1, record.unread)

    def test_practicum_loader_excludes_another_artifacts_heading_record(self):
        import run_grader
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "draft.md"
            document.write_text("Synthetic draft.", encoding="utf-8")
            checks = root / "checks.md"
            checks.write_text("## HEADING-READ: other.md\nUnknown prose.\nREMARK: Sibling only.\nVERDICT: clean\n## CHECK: Synthetic check\nVERDICT: clean\n", encoding="utf-8")
            parsed = run_grader.parse(checks_ledger.GRADER, [str(checks), "--document", str(document)])
            bound = checks_ledger._load(parsed)
            self.assertEqual(1, len(bound.records))
            self.assertEqual((), bound.records[0].remarks)
            self.assertEqual(0, bound.records[0].unread)

    def test_voice_reader_accepts_and_returns_remarks(self):
        self.assertIn('remarks', voice_read._READER_KEYS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'voice-reads' / 'draft' / 'voice-read.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'remarks': ['Check the transition.']}), encoding='utf-8')
            self.assertEqual('Check the transition.', remarks.voice_remarks(root, ('draft.md',))[0].text)


class ApprovalSurfaces(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run = self.root / 'run'
        self.run.mkdir()
        write_none_context(self.run)
        self.source = self.root / 'draft.md'
        self.source.write_text('Synthetic approved content.\n', encoding='utf-8')
        os.utime(self.source, (1, 1))
        self.transcript = self.root / 'session.jsonl'
        patch = mock.patch.object(aar_scan, 'discover_transcripts', return_value=aar_scan.TranscriptDiscovery((self.transcript,), 1, 0, 0, 1))
        patch.start()
        self.addCleanup(patch.stop)
        self.grade = 'paired grade: clean\nunread remainder 1\nposted reading: NOT GRADED\n' + remarks.report((remarks.Remark('HEADING-READ: draft.md', 'Clarify the secondary citation.'),))
        self.outcomes = (remarks.Outcome('fixed', 'The draft identifies the original body with the secondary citation.'),)

    def show(self, text, reply='go', *, before=None, codex=False):
        at = before if before is not None else time.time() + 10
        def row(role, value, stamp):
            timestamp = datetime.fromtimestamp(stamp, timezone.utc).isoformat()
            if codex:
                return {'type': 'response_item', 'timestamp': timestamp, 'payload': {'type': 'message', 'role': role, 'content': [{'type': 'output_text' if role == 'assistant' else 'input_text', 'text': value}]}}
            return {'type': role, 'timestamp': timestamp, 'message': {'content': value}}
        self.transcript.write_text('\n'.join(json.dumps(r) for r in (row('assistant', text, at), row('user', reply, at + 1))) + '\n', encoding='utf-8')

    def prepare(self, course=False):
        if course:
            from test_assignment_bar import DOCX_BAR
            (self.run / 'bar.md').write_text(DOCX_BAR, encoding='utf-8')
            self.source = self.root / 'draft.docx'
            self.source.write_bytes(b'synthetic artifact')
            os.utime(self.source, (1, 1))
            return assignments.prepare(self.run, self.source)
        return approvals.prepare(self.run, skill='discussion-post', submission='draft', sources=(self.source,), grader_args=(str(self.run),))

    def approve(self, course=False, reply='go'):
        if course:
            return assignments.stage(self.run, self.source, artifact_approved=True, clinician_reply=reply, remark_outcomes=self.outcomes)
        return approvals.approve(self.run, skill='discussion-post', submission='draft', sources=(self.source,), grader_args=(str(self.run),), content_approved=True, clinician_reply=reply, remark_outcomes=self.outcomes)

    def graders(self):
        patches = (mock.patch.object(approvals, '_pre_post_grade', return_value=(2, self.grade)), mock.patch.object(assignments, '_pre_upload_grade', return_value=(True, self.grade)))
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_unchanged_posting_reply_carries_the_content_leave_without_renaming_it(self):
        self.graders()
        self.outcomes = (remarks.Outcome('leave', 'Keep this synthetic wording.'),)
        prepared = self.prepare()
        self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes), 'go, leave 1')
        self.approve(reply='go, leave 1')
        row = {'type': 'user', 'timestamp': datetime.fromtimestamp(time.time() + 30, timezone.utc).isoformat(),
               'message': {'content': 'Post the loaded box.'}}
        with self.transcript.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row) + '\n')
        approvals.approve(self.run, skill='discussion-post', submission='draft', sources=(self.source,),
                          grader_args=(str(self.run),), content_approved=True,
                          clinician_reply='Post the loaded box.', approval_kind='posting')
        item = json.loads((self.run / approvals.RECORD).read_text(encoding='utf-8'))['items'][0]
        self.assertEqual("left on clinician's word", item['reader_remarks'][0]['outcome'])
        self.assertEqual('exempt', item['shown_text_verification'])
        self.assertEqual(['content', 'posting'], [row['approval_kind'] for row in item['approvals']])

    def test_posting_preserves_stored_order_when_a_fixed_remark_disappears(self):
        first = remarks.Remark('HEADING-READ: draft.md', 'First observation.')
        second = remarks.Remark('HEADING-READ: draft.md', 'Second observation.')
        self.grade = 'paired grade: clean\nunread remainder 1\n' + remarks.report((first, second))
        self.graders()
        self.outcomes = (remarks.Outcome('fixed', 'First repaired.'), remarks.Outcome('leave', 'Keep second.'))
        prepared = self.prepare()
        self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes), 'go, leave 2')
        self.approve(reply='go, leave 2')
        row = {'type': 'user', 'timestamp': datetime.fromtimestamp(time.time() + 30, timezone.utc).isoformat(),
               'message': {'content': 'Post the loaded box.'}}
        with self.transcript.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row) + '\n')
        with mock.patch.object(approvals, '_pre_post_grade', return_value=(2, 'paired grade: clean\nunread remainder 1\n' + remarks.report((second,)))):
            approvals.approve(self.run, skill='discussion-post', submission='draft', sources=(self.source,),
                              grader_args=(str(self.run),), content_approved=True,
                              clinician_reply='Post the loaded box.', approval_kind='posting')
        item = json.loads((self.run / approvals.RECORD).read_text(encoding='utf-8'))['items'][0]
        self.assertEqual(['First observation.', 'Second observation.'], [r['text'] for r in item['reader_remarks']])
        with mock.patch.object(approvals, '_pre_post_grade', return_value=(2, self.grade + '\n' + remarks.report((remarks.Remark('new', 'New observation.'),)))):
            row['timestamp'] = datetime.fromtimestamp(time.time() + 60, timezone.utc).isoformat()
            with self.transcript.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(row) + '\n')
            with self.assertRaisesRegex(approvals.ApprovalRecordError, 'reader remarks changed'):
                approvals.approve(self.run, skill='discussion-post', submission='draft', sources=(self.source,),
                                  grader_args=(str(self.run),), content_approved=True,
                                  clinician_reply='Post the loaded box.', approval_kind='posting')

    def test_both_seams_refuse_each_missing_approval_part(self):
        self.graders()
        for course in (False, True):
            for missing in ('remark', 'coverage', 'count'):
                with self.subTest(course=course, missing=missing):
                    prepared = self.prepare(course)
                    surface = remarks.surface(prepared, self.outcomes)
                    if missing == 'remark':
                        surface = '\n'.join(surface.splitlines()[1:])
                    elif missing == 'coverage':
                        surface = surface.replace('unread remainder 1', '')
                    else:
                        surface = surface.replace('unread remainder 1', 'unread remainder 10')
                    self.show('Synthetic approved content.\n' + surface)
                    with self.assertRaisesRegex((approvals.ApprovalRecordError, assignments.GateError), 'not shown'):
                        self.approve(course)

    def test_both_seams_refuse_bare_approval_with_leave_and_accept_named_leave(self):
        self.graders()
        self.outcomes = (remarks.Outcome('leave', 'Keep the wording for this synthetic exercise.'),)
        for course in (False, True):
            with self.subTest(course=course):
                prepared = self.prepare(course)
                self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes))
                with self.assertRaisesRegex((approvals.ApprovalRecordError, assignments.GateError), 'unanswered.*1'):
                    self.approve(course)
                self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes), 'send it, leave 1')
                self.approve(course, 'send it, leave 1')
                payload = json.loads((self.run / (assignments.RECORD if course else approvals.RECORD)).read_text())
                item = payload if course else payload['items'][0]
                self.assertEqual("left on clinician's word", item['reader_remarks'][0]['outcome'])

    def test_fixed_remarks_are_accepted_with_actual_words_in_both_transcript_formats(self):
        self.graders()
        for codex, reply in ((False, 'fire'), (True, 'send it')):
            prepared = self.prepare()
            self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes), reply, codex=codex)
            self.approve(reply=reply)
            item = json.loads((self.run / approvals.RECORD).read_text())['items'][0]
            self.assertEqual('fixed', item['reader_remarks'][0]['outcome'])

    def test_grade_must_be_prepared_before_ask_and_after_latest_change(self):
        self.graders()
        prepared = self.prepare()
        self.show('Synthetic approved content.\n' + remarks.surface(prepared, self.outcomes), before=2)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, 'before the approval reply'):
            self.approve()
        self.source.write_text('Changed source.\n', encoding='utf-8')
        self.show('Changed source.\n' + remarks.surface(prepared, self.outcomes))
        with self.assertRaisesRegex(approvals.ApprovalRecordError, 'source changed'):
            self.approve()

    def test_real_reply_grader_carries_a_remark_and_unread_record_to_the_ask(self):
        from test_discussion_reply_scan import Run
        Run(self.run, posted=False)
        (self.run / "reread.md").unlink(missing_ok=True)
        self.source = self.run / "response-maren.md"
        heading = self.run / "heading-read.md"
        heading.write_text(heading.read_text(encoding="utf-8") + "REMARK: Check the secondary citation.\nUnrecognized reader prose.\n", encoding="utf-8")
        args = dict(skill="discussion-reply", submission=self.source.name,
                    sources=(self.source,), grader_args=(str(self.run),))
        prepared = approvals.prepare(self.run, **args)
        self.assertIn("unread remainder 1", prepared.report)
        self.assertIn("unread reader record: HEADING-READ: response-maren.md", prepared.report)
        self.assertEqual("Check the secondary citation.", prepared.remarks[0].text)
        outcomes = (remarks.Outcome("fixed", "The reference identifies the secondary route."),)
        self.show(self.source.read_text(encoding="utf-8") + "\n" + remarks.surface(prepared, outcomes), "fire")
        approved = approvals.approve(self.run, **args, content_approved=True,
                                     clinician_reply="fire", remark_outcomes=outcomes)
        self.assertIn("unread remainder 1", approved.pregrade_report)

    def test_a_replaced_reader_record_does_not_erase_a_previously_prepared_remark(self):
        self.graders()
        first = self.prepare()
        current_report = "paired grade: clean"
        with mock.patch.object(approvals, "_pre_post_grade", return_value=(0, current_report)):
            prepared = self.prepare()
            self.assertEqual(first.remarks, prepared.remarks)
            self.show("Synthetic approved content.\n" + remarks.surface(prepared, self.outcomes))
            self.approve()

    def test_the_surface_names_the_reply_forms_only_when_a_remark_is_proposed_to_be_left(self):
        prepared = remarks.Prepared('', (remarks.Remark('a', 'One.'), remarks.Remark('b', 'Two.'), remarks.Remark('c', 'Three.')), ('unread remainder 1',))
        fixed = remarks.Outcome('fixed', 'Repaired.')
        leave = remarks.Outcome('leave', 'Keep it.')
        self.assertNotIn('Proposed to leave', remarks.surface(prepared, (fixed, fixed, fixed)))
        lines = remarks.surface(prepared, (leave, fixed, leave)).splitlines()
        request = 'Proposed to leave: 1, 3. To leave them, reply "leave all of them" or "leave 1, 3".'
        self.assertEqual(request, lines[3])
        self.assertEqual('unread remainder 1', lines[4])
        for reply in ('leave all of them', 'leave 1, 3'):
            with self.subTest(reply=reply):
                self.assertTrue({1, 3} <= remarks._left_numbers(reply, 3))
        self.assertNotIn('Proposed to leave', remarks.surface(prepared, (leave, fixed, leave), request_leaves=False))

    def test_a_content_ask_without_the_reply_forms_is_refused(self):
        self.graders()
        self.outcomes = (remarks.Outcome('leave', 'Keep the wording for this synthetic exercise.'),)
        for course in (False, True):
            with self.subTest(course=course):
                prepared = self.prepare(course)
                shown = remarks.surface(prepared, self.outcomes, request_leaves=False)
                self.show('Synthetic approved content.\n' + shown, 'send it, leave 1')
                with self.assertRaisesRegex((approvals.ApprovalRecordError, assignments.GateError), 'not shown.*Proposed to leave'):
                    self.approve(course, 'send it, leave 1')

    def test_all_leaves_and_negated_leaves(self):
        self.assertEqual({1, 2}, remarks._left_numbers('go, leave all of them', 2))
        self.assertEqual({1, 2}, remarks._left_numbers('leave 1 and 2, fire', 2))
        self.assertEqual(set(), remarks._left_numbers('do not leave 1', 2))


if __name__ == '__main__':
    unittest.main()
