"""Synthetic clinical/AAR record damage through public grading and writer seams."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
from datetime import timedelta
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import aar_scan
import anchor_scan
import completion_checks
import coding_freshness
import delegated_answers
import differential_scan
import filled_vitals_census
import medatrax_posting
import reader_remarks
import run_record_reader as records
import shift_summary
import specificity_scan
import test_encounter_openers as opener_tests
import test_medatrax_readback_command as portal_tests
import test_specificity_scan as specificity_tests
import test_delegated_answers as delegated_tests
import visit_times

CONTROLS = ('\t', '\a', '\0', '\f', '\v', '\r')
ANSWER = '## QUESTION: Synthetic question\nRULE: none found\nANSWER: Follow up.\nNOTE: note-1.md\nSECTIONS: P\n'
NOTE = ('Start time 0800\nEnd time 0830\nS:\nCough.\nO:\nNormal.\n'
        'A:\nDifferential:\n1. Cough - R05.9: most likely.\nP:\nFollow up.\n'
        '---\nFILLED·asserted   BP 118/76 filled.\n')


class HandwrittenClinical(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        (self.run / 'note-1.md').write_text(NOTE, encoding='utf-8')

    def test_text_populations_refuse_damage_including_before_the_first_question(self):
        for character in CONTROLS:
            for text in (character + 'x\n' + ANSWER,
                         ANSWER.replace('QUESTION:', 'QUESTION:' + character),
                         ANSWER.replace('none found', 'none found' + character + 'x'),
                         ANSWER.replace('Follow up.', 'Follow' + character + ' up.')):
                with self.subTest(character=ord(character), text=text):
                    (self.run / delegated_answers.RECORD).write_bytes(text.encode())
                    finding, report, unread = delegated_answers.completion_gate(self.run, 'synthetic')
                    self.assertTrue(finding, report)
                    self.assertIn('not graded — damaged text', report)
                    self.assertIn(f'U+{ord(character):04X}', report)
                    self.assertNotIn('holds no QUESTION', report)
                    summary = self.run / 'shift-summary.md'
                    summary.write_bytes(('GENERATION: ' + character + 'x\n').encode())
                    finding, incomplete, report = shift_summary.check(self.run, (), True)
                    self.assertTrue(finding, report)
                    self.assertFalse(incomplete)
                    self.assertIn('not graded — damaged text', report)

    def test_crlf_is_clean_and_known_old_key_does_not_waive_unknown_sibling(self):
        path = self.run / delegated_answers.RECORD
        path.write_bytes(ANSWER.replace('\n', '\r\n').encode())
        self.assertFalse(delegated_answers.completion_gate(self.run, 'synthetic')[0])
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        path.write_bytes(('\a\n' + ANSWER).encode())
        item = completion_checks.ITEM_MOMENTS.set({'old': old, 'exact': start})
        global_moment = completion_checks.MOMENTS.set({'approval': old})
        try:
            self.assertFalse(delegated_answers.completion_gate(self.run, 'old')[0])
            for key in ('exact', 'unknown'):
                self.assertTrue(delegated_answers.completion_gate(self.run, key)[0])
            # Historical damage is not a new finding, but an original malformed
            # answer remains a finding under its original contract.
            path.write_bytes(('\a\n' + ANSWER.replace('ANSWER: Follow up.\n', '')).encode())
            finding, report, unread = delegated_answers.completion_gate(self.run, 'old')
            self.assertTrue(finding)
            self.assertIn('ANSWER must appear once', report)
            self.assertNotIn('U+0007', report)
        finally:
            completion_checks.ITEM_MOMENTS.reset(item)
            completion_checks.MOMENTS.reset(global_moment)

    def test_answer_reader_damage_is_content_and_keeps_independent_rule_findings(self):
        source = self.run / delegated_answers.RECORD
        source.write_text(ANSWER, encoding='utf-8')
        path = delegated_tests.write_reader(self.run)
        intact = path.read_bytes()
        for character in CONTROLS:
            for raw in (intact + character.encode(),
                        json.dumps({'private' + character: 'value'}).encode(),
                        json.dumps({'private': [{'value': character}]}).encode()):
                with self.subTest(character=ord(character), raw=raw):
                    path.write_bytes(raw)
                    finding, report, unread = delegated_answers.completion_gate(self.run, 'synthetic')
                    self.assertTrue(finding, report)
                    self.assertEqual(0, unread, report)
                    self.assertIn(f'U+{ord(character):04X}', report)
                    self.assertNotIn('private', report)
        source.write_text(ANSWER.replace('RULE: none found', 'RULE: invented rule'), encoding='utf-8')
        for command in (differential_scan, filled_vitals_census):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                status = command.main([str(self.run), '--submission', 'synthetic'])
            self.assertEqual(1, status, output.getvalue())
            self.assertIn('U+000D', output.getvalue())
            self.assertIn('RULE is neither', output.getvalue())

    def test_answer_reader_cutoff_and_derived_writer_force_are_per_item(self):
        source = self.run / delegated_answers.RECORD
        source.write_text(ANSWER, encoding='utf-8')
        path = delegated_tests.write_reader(self.run)
        path.write_bytes(path.read_bytes() + b'\x07')
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        token = completion_checks.MOMENTS.set({'approval': old})
        item = completion_checks.ITEM_MOMENTS.set({'old': old, 'exact': start})
        try:
            self.assertFalse(delegated_answers.completion_gate(self.run, 'old')[0])
            for key in ('exact', 'unknown'):
                finding, report, unread = delegated_answers.completion_gate(self.run, key)
                self.assertTrue(finding, report)
                self.assertEqual(0, unread)
            finding, report, unread = delegated_answers.completion_gate(self.run, 'old', pre_approval=True)
            self.assertTrue(finding, report)
            source.write_bytes(source.read_bytes() + b'\x07')
            before = source.read_bytes()
            for operation in (lambda: delegated_answers.reader_brief(self.run),
                              lambda: delegated_answers.verify_shown_answers(self.run, 1, transcripts=((), False))):
                with self.assertRaises(records.DamagedRecord):
                    operation()
            self.assertEqual(before, source.read_bytes())
        finally:
            completion_checks.ITEM_MOMENTS.reset(item)
            completion_checks.MOMENTS.reset(token)

    def test_json_key_and_nested_string_damage_precedes_schema_in_each_reader(self):
        path = self.run / 'read.json'
        for character in CONTROLS:
            for payload in ({'private' + character: 'value'}, {'private': [{'nested': character}]}):
                with self.subTest(character=ord(character), payload=payload):
                    path.write_text(json.dumps(payload), encoding='utf-8')
                    second = specificity_scan.load_second_read(path)
                    self.assertTrue(second.damaged, second.why_not)
                    self.assertIn(f'U+{ord(character):04X}', second.why_not)
                    agreement = anchor_scan._grade_agreement([], 0, [path])
                    self.assertTrue(agreement.damage_reports)
                    self.assertIn(f'U+{ord(character):04X}', agreement.damage_reports[0])
                    with self.assertRaises(records.DamagedRecord):
                        anchor_scan._rendered_descriptors(path)
                    window = self.run / 'shift-values.json'
                    window.write_bytes(path.read_bytes())
                    with self.assertRaises(records.DamagedRecord):
                        visit_times.read_window(self.run)
                    before = path.read_bytes()
                    with self.assertRaises(records.DamagedRecord):
                        reader_remarks.replace_coding_record(path, {'pairs': []}, kind='agreement')
                    self.assertEqual(before, path.read_bytes())
                    self.assertNotIn('private', second.why_not)

    def test_shift_damage_withholds_window_but_keeps_independent_duration_finding(self):
        (self.run / 'note-1.md').write_text(NOTE.replace('0830', '0810'), encoding='utf-8')
        for character in CONTROLS:
            (self.run / 'shift-values.json').write_text(json.dumps({
                'start': '0800', 'duration': {'hours': 8, 'minutes': 0},
                'extra': {'nested': character}}), encoding='utf-8')
            result = visit_times.check(self.run, batch=True)
            report = visit_times.report(result)
            self.assertTrue(any('duration outside' in finding for finding in result.findings))
            self.assertIn('not graded — damaged text', report)
            self.assertNotIn('shift values absent or unreadable', report)

    def test_native_agreement_command_dates_the_entire_new_read_boundary(self):
        worksheets, notes = self.run / 'worksheets', self.run / 'notes'
        worksheets.mkdir()
        notes.mkdir()
        (worksheets / 'case-01.md').write_text('No code selected.\n', encoding='utf-8')
        (notes / 'case-01.md').write_text('No code selected.\n', encoding='utf-8')
        path = self.run / 'read.json'
        path.write_text(json.dumps({'pairs': [{'stem': 'case-01', 'codes': [], 'remarks': ['\a']}]}), encoding='utf-8')
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        for moment, expected in ((start - timedelta(microseconds=1), 0), (start, 1)):
            output = io.StringIO()
            with patch.object(completion_checks, 'approval_moment', return_value=moment), \
                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                status = anchor_scan.main([str(worksheets), '--notes', str(notes),
                    '--agreement-read', str(path), '--submission', 'synthetic'])
            self.assertEqual(expected, status, output.getvalue())
            if expected:
                self.assertIn('not graded — damaged text', output.getvalue())

    def test_native_specificity_command_keeps_artifact_finding_beside_reader_damage(self):
        fixture = specificity_tests.TheCommandGradesTheSeparatedRead('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        note = fixture.run / 'case-01.md'
        note.write_text(note.read_text(encoding='utf-8').replace('complete — the original reason', 'complete'), encoding='utf-8')
        fixture.read_path.write_text(json.dumps({'codes': [], 'nested': '\u0000'}), encoding='utf-8')
        status, output, errors = fixture._run('--second-read', str(fixture.read_path))
        self.assertEqual(1, status, output + errors)
        self.assertIn('not graded — damaged text', output + errors)
        self.assertIn('flag(s) fail', output + errors)

    def test_both_native_note_hosts_continue_after_damaged_delegation(self):
        (self.run / 'note-1.md').write_text(NOTE.replace(' - R05.9', ''), encoding='utf-8')
        (self.run / 'shift-values.json').write_text(json.dumps({
            'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
        (self.run / delegated_answers.RECORD).write_bytes(('\a\n' + ANSWER).encode())
        for command in (differential_scan, filled_vitals_census):
            if command is filled_vitals_census:
                (self.run / 'note-2.md').write_text(NOTE, encoding='utf-8')
            output = io.StringIO()
            arguments = [str(self.run), '--submission', 'synthetic']
            if command is differential_scan:
                arguments += ['--note', str(self.run / 'note-1.md')]
            with contextlib.ExitStack() as stack:
                for module in (command.aar_scan, command.medatrax_posting,
                               command.artifact_repairs, command.outbound_search):
                    stack.enter_context(patch.object(module, 'completion_gate', return_value=(False, 'synthetic: clean')))
                stack.enter_context(patch.object(command.approval_record, 'apply_completion_gate', side_effect=lambda grade, *args: grade))
                stack.enter_context(contextlib.redirect_stdout(output))
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                self.assertEqual(1, command.main(arguments), output.getvalue())
            self.assertIn('not graded — damaged text', output.getvalue())
            self.assertIn('U+0007', output.getvalue())
            if command is differential_scan:
                self.assertIn('numbered item without a code', output.getvalue())
            else:
                self.assertIn('sharing a body with another note', output.getvalue())

    def test_aar_public_command_refuses_review_damage_without_parsing_fake_fields(self):
        path = aar_scan.review_path(self.run, 'synthetic', 1)
        path.parent.mkdir()
        path.write_bytes(b'\x07\nSUBMISSION: synthetic\n')
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, aar_scan.main([str(self.run), '--submission', 'synthetic']))
        self.assertIn('not graded — damaged text', output.getvalue())
        self.assertNotIn('missing-header-field', output.getvalue())
        finding, report = aar_scan.completion_gate(self.run, 'synthetic')
        self.assertTrue(finding, report)
        self.assertIn('U+0007', report)

    def test_coding_retry_force_refuses_old_damage_and_retains_prior_bytes(self):
        path = self.run / 'read.json'
        path.write_text(json.dumps({'pairs': [], 'extra': '\u0000'}), encoding='utf-8')
        before = path.read_bytes()
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        token = completion_checks.MOMENTS.set({'approval': start - timedelta(days=1)})
        try:
            with self.assertRaises(records.DamagedRecord):
                reader_remarks.replace_coding_record(path, {'pairs': []}, kind='agreement')
        finally:
            completion_checks.MOMENTS.reset(token)
        self.assertEqual(before, path.read_bytes())

    def test_native_portal_writer_refuses_damaged_input_and_prior_reread_without_overwrite(self):
        fixture = portal_tests.ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.assertEqual(0, fixture.invoke('write'))
        target = fixture.run / 'reread.md'
        before = target.read_bytes()
        fixture.payload['verdict_detail'] = 'Private' + '\a' + 'marker'
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        token = completion_checks.MOMENTS.set({'approval': start - timedelta(days=1)})
        try:
            self.assertEqual(1, fixture.invoke('write'))
        finally:
            completion_checks.MOMENTS.reset(token)
        self.assertEqual(before, target.read_bytes())
        fixture.payload['verdict_detail'] = 'The same saved fields match.'
        target.write_bytes(before + b'\x07\n')
        self.assertEqual(1, fixture.invoke('check'))
        self.assertEqual(1, fixture.invoke('write'))
        self.assertEqual(before + b'\x07\n', target.read_bytes())
        target.write_bytes(b'{')
        self.assertEqual(2, fixture.invoke('check'))
        self.assertEqual(2, fixture.invoke('write'))
        self.assertEqual(b'{', target.read_bytes())

    def test_native_opener_input_refuses_nested_escaped_damage_before_publication(self):
        fixture = opener_tests.OpenerCommands('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for character in CONTROLS:
            result = fixture.record(readings=[{'note': 1, 'name': 'Example Person',
                'age': 'adult', 'sex': 'female', 'unparsed': {'nested': character}}])
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn(f'U+{ord(character):04X}', result.stdout + result.stderr)
            self.assertFalse((fixture.run / 'openers.json').exists())

    def test_native_collision_rulings_refuse_damage_before_identity_append(self):
        fixture = opener_tests.OpenerCommands('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.assertEqual(0, fixture.record().returncode)
        collisions = fixture.root / 'collisions.json'
        for character in CONTROLS:
            collisions.write_text(json.dumps({'unparsed': {'value': character}}), encoding='utf-8')
            result = fixture.identity('abcdef123456789', '--collisions', collisions)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertFalse(fixture.map.exists())

    def test_native_portal_input_checks_every_key_and_nested_value_before_schema(self):
        fixture = portal_tests.ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.assertEqual(0, fixture.invoke('write'))
        before = (fixture.run / 'reread.md').read_bytes()
        clean = dict(fixture.payload)
        for character in CONTROLS:
            for addition in ({'unparsed' + character: 'value'}, {'unparsed': {'nested': character}}):
                fixture.payload = {**clean, **addition}
                self.assertEqual(1, fixture.invoke('write'))
                self.assertEqual(before, (fixture.run / 'reread.md').read_bytes())

    def test_native_freshness_manifest_damage_is_before_network_and_receipt_changes(self):
        manifest = self.run / 'batch-codes.json'
        receipt = self.run / 'batch-freshness.json'
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        for observed in (None, start - timedelta(days=1), start):
            token = completion_checks.MOMENTS.set({'approval': observed})
            try:
                for character in CONTROLS:
                    for payload in ({'unknown' + character: 'value'}, {'unknown': [{'value': character}]}):
                        manifest.write_text(json.dumps(payload), encoding='utf-8')
                        receipt.write_bytes(b'prior receipt evidence')
                        output = io.StringIO()
                        with patch.object(coding_freshness, 'read_url', side_effect=AssertionError('network reached')) as network, \
                             contextlib.redirect_stdout(output):
                            status = coding_freshness.main([str(manifest), '--receipt', str(receipt)])
                        self.assertEqual(1, status, output.getvalue())
                        network.assert_not_called()
                        self.assertIn(f'U+{ord(character):04X}', output.getvalue())
                        self.assertNotIn('unknown', output.getvalue())
                        self.assertEqual(b'prior receipt evidence', receipt.read_bytes())
            finally:
                completion_checks.MOMENTS.reset(token)

    def test_freshness_malformed_shape_and_undecodable_inputs_keep_original_refusal(self):
        manifest = self.run / 'batch-codes.json'
        receipt = self.run / 'batch-freshness.json'
        for raw in (b'{', b'[]', b'{}', b'\xff'):
            manifest.write_bytes(raw)
            receipt.write_bytes(b'prior receipt evidence')
            with patch.object(coding_freshness, 'read_url', side_effect=AssertionError('network reached')) as network, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(2, coding_freshness.main([str(manifest), '--receipt', str(receipt)]))
            network.assert_not_called()
            self.assertFalse(receipt.exists())


if __name__ == '__main__':
    unittest.main()
