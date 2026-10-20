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
import encounter_openers
import form_sections
import frozen_grade
import outbound_search
import uptodate_block
import medatrax_posting
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

    def damaged(self, path, invoke, *, wrong=b'[]', wrong_cause='wrong shape: record object', truncated_cause='does not decode at line 1 column 2'):
        path.parent.mkdir(parents=True, exist_ok=True)
        for content, cause in ((b'{', truncated_cause),
                               (wrong, wrong_cause), (None, 'could not be opened')):
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

    def test_every_repair_rewriter_preserves_unreadable_chain(self):
        note = self.root / 'synthetic.md'
        note.write_text('A:\nSynthetic assessment.\nP:\nSynthetic plan.\n', encoding='utf-8')
        scope = self.root / 'scope.json'
        scope.write_text('{"fields":[],"sections":["A"]}', encoding='utf-8')
        for arguments in (
            ['place', str(self.root), str(note), '--kind', 'note'],
            ['begin', str(self.root), str(note), '--scope', str(scope)],
            ['compare', str(self.root), '--after', str(note)],
            ['re-scope', str(self.root), str(note), '--repair', 'synthetic', '--scope', str(scope), '--clinician-reply', 'Synthetic approval.'],
        ):
            self.damaged(artifact_repairs.ledger_path(self.root), lambda: artifact_repairs.main(arguments))

    def test_adoption_command_preserves_unreadable_freeze_record(self):
        self.damaged(self.root / frozen_grade.RECORD, lambda: frozen_grade.main([str(self.root)]))

    def test_adoption_never_defaults_a_damaged_posted_reading_to_empty(self):
        from test_frozen_grade import FrozenGrade
        fixture = FrozenGrade('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.run / 'reread.md').write_text(fixture.reading('2026-10-01T12:00:00Z'), encoding='utf-8')
        self.damaged(fixture.run / 'reread.md', lambda: frozen_grade.main([str(fixture.run)]),
                     truncated_cause='wrong shape: declared record shape',
                     wrong_cause='wrong shape: declared record shape')

    def test_planted_voice_identity_caller_preserves_unreadable_identity(self):
        from test_voice_read import PublicCompletionCommand
        fixture = PublicCompletionCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        def invoke():
            status, report = fixture.command()
            print(report)
            return status
        self.damaged(fixture.run / 'voice-model-identity.json', invoke)

    def test_capture_command_refuses_before_heavy_environment_or_worker_launch(self):
        capture = self.root / 'case-video' / 'capture'
        fake_python = self.root / 'synthetic-python'
        fake_python.write_bytes(b'synthetic')
        self.damaged(capture / 'capture.json', lambda: case_video.main([
            'transcribe', str(self.root), '--python', str(fake_python),
            '--terms', str(capture / 'slide-terms.json'),
        ]))

    def test_every_capture_record_kind_refuses_through_the_check_command(self):
        from test_case_video import CaptureGate
        fixture = CaptureGate('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        arguments = ['check', str(fixture.run), '--submission', fixture.key, '--draft', str(fixture.draft_path)]
        for name in ('capture.json', 'pass-1.json', 'pass-2.json', 'disagreements.json', 'slide-terms.json'):
            path = fixture.root / name
            original = path.read_bytes()
            wrong = b'{}' if name in {'pass-1.json', 'pass-2.json', 'disagreements.json'} else b'[]'
            rule = 'record items' if wrong == b'{}' else 'record object'
            self.damaged(path, lambda: case_video.main(arguments), wrong=wrong, wrong_cause='wrong shape: ' + rule)
            path.write_bytes(original)

    def test_transcription_vocabulary_input_keeps_agent_authored_ownership(self):
        import json
        import sys
        from types import SimpleNamespace
        from test_case_video import CaptureGate
        fixture = CaptureGate('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        record = case_video.valid_capture(fixture.root)
        record['state'] = 'prepared'
        source = fixture.run / 'slide-terms.json'
        source.write_bytes(b'{')
        args = SimpleNamespace(terms=str(source))
        worker = SimpleNamespace(WhisperModel=mock.Mock())
        with (mock.patch.dict(sys.modules, {'faster_whisper': worker}),
              mock.patch.object(case_video, 'valid_capture', return_value=record),
              records.capture_errors() as faults):
            with self.assertRaises(json.JSONDecodeError) as caught:
                case_video.transcribe(args, fixture.root)
            self.assertNotIsInstance(caught.exception, records.UnreadableRecord)
            self.assertEqual({}, faults)
        worker.WhisperModel.assert_not_called()
        self.assertEqual(b'{', source.read_bytes())

    def test_medatrax_writer_check_and_replace_preserve_unreadable_markdown(self):
        from test_medatrax_readback_command import ReadbackCommand
        fixture = ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        import json
        fixture.input.write_text(json.dumps(fixture.payload), encoding='utf-8')
        common = ['--run', str(fixture.run), '--submission', 'shift', '--batch']
        for arguments in (['check', *common], ['write', *common, '--input', str(fixture.input)],
                          ['write', *common, '--input', str(fixture.input), '--replace']):
            self.damaged(fixture.run / 'reread.md', lambda: medatrax_posting.main(arguments),
                         truncated_cause='wrong shape: declared record shape',
                         wrong_cause='wrong shape: declared record shape')

    def test_standalone_medatrax_check_never_falls_back_after_damaged_approval(self):
        (self.root / 'synthetic.md').write_text('Synthetic note.', encoding='utf-8')
        self.damaged(self.root / 'posting-approvals.json', lambda: medatrax_posting.main([
            'check', '--run', str(self.root), '--submission', 'synthetic',
        ]))

    def test_outbound_writer_preserves_a_damaged_existing_log(self):
        path = self.root / outbound_search.SEARCHES
        with mock.patch.object(outbound_search, 'refusal', return_value=None):
            self.damaged(path, lambda: outbound_search.main([
                'check', 'synthetic clinical query', '--run', str(self.root), '--search-id', 'synthetic',
            ]))

    def test_pull_writer_and_disclosure_refuse_each_damaged_log(self):
        import json
        searches = self.root / outbound_search.SEARCHES
        searches.write_text(json.dumps({'search_id': 'synthetic', 'query': 'synthetic', 'passed': True}) + '\n', encoding='utf-8')
        self.damaged(self.root / outbound_search.PULLS, lambda: outbound_search.main([
            'pull', '--run', str(self.root), '--search-id', 'synthetic', '--dump-id', 'synthetic',
        ]))
        note = self.root / 'synthetic.md'
        note.write_text('Synthetic note.', encoding='utf-8')
        for name in (outbound_search.PULLS, outbound_search.SEARCHES):
            self.damaged(self.root / name, lambda: uptodate_block.main([
                '--run', str(self.root), '--notes', str(note),
            ]))

    def test_receipt_rewriter_never_clears_a_failed_read(self):
        path = reader_remarks._receipt_path(self.root, 'discussion-post', 'post')
        path.parent.mkdir()
        for content in (b'{', b'[]'):
            path.write_bytes(content)
            with self.assertRaises(records.UnreadableRecord):
                reader_remarks.prepare(self.root, 'discussion-post', 'post', (), 'synthetic grade')
            self.assertEqual(content, path.read_bytes())

    def test_opener_record_answer_and_identity_writers_preserve_damage(self):
        source = self.root / 'synthetic.txt'
        source.write_text('Note 1\nadult female\n', encoding='utf-8')
        readings = self.root / 'readings.json'
        readings.write_text('[{"note":1,"name":null,"age":"adult","sex":"female"}]', encoding='utf-8')
        target = self.root / 'openers.json'
        commands = (
            ['record', '--run', str(self.root), '--source', str(source), '--readings', str(readings), '--service-date', '2026-01-01'],
            ['answer', '--run', str(self.root), '--note', '1', '--reply', 'No name available.'],
            ['identity', '--run', str(self.root), '--note', '1', '--reference', 'abcdef123456789', '--map', str(self.root / 'map.md')],
        )
        for arguments in commands:
            self.damaged(target, lambda: encounter_openers.main(arguments))
        self.assertFalse((self.root / 'map.md').exists())

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
