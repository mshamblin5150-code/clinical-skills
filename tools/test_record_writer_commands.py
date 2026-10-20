"""Native primary writer lock/refusal controls, with synthetic records only."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import assignment_bar
import case_video
import encounter_openers
import refutation_apply
import run_record_reader as records
import test_assignment_bar as bars
import test_case_video as videos
import test_encounter_openers as openers
import test_run_status_stop_hook as stops
import test_refutation_apply as refuters


def invoke(command):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        status = command()
    return status, output.getvalue()


class NativeWriterTransactions(unittest.TestCase):
    def check_refusals(self, path, command):
        before = path.read_bytes()
        with artifact_lock.hold(path, 'synthetic command holder'):
            status, report = invoke(command)
        self.assertEqual(status, 2, report)
        self.assertIn('unreadable — held by another task:', report)
        self.assertEqual(path.read_bytes(), before)
        real_replace = records.os.replace
        def interrupted(source, destination):
            if Path(destination) == path:
                raise OSError('PRIVATE-PLANTED')
            return real_replace(source, destination)
        with mock.patch.object(records.os, 'replace', side_effect=interrupted):
            status, report = invoke(command)
        self.assertEqual(status, 2, report)
        self.assertIn('unreadable — could not be opened', report)
        self.assertNotIn('PRIVATE-PLANTED', report)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(path.parent.glob(path.name + '.*.partial')))

    def test_signer_command_retains_history_bar_and_copies_after_both_refusals(self):
        fixture = bars.BarSignatures()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.draft(bars.DOCX_BAR)
        fixture.sign()
        before_bar = fixture.bar.read_bytes()
        before_copies = {p.name: p.read_bytes() for p in (fixture.run / 'signed-bars').iterdir()}
        reply = 'I confirm the second synthetic bar.'
        fixture.messages.append({'type': 'user', 'timestamp': '2100-10-09T12:01:00Z',
                                 'message': {'content': reply}})
        self.check_refusals(fixture.run / assignment_bar.RECORD,
                            lambda: assignment_bar.main([str(fixture.run), '--reply', reply]))
        self.assertEqual(fixture.bar.read_bytes(), before_bar)
        self.assertEqual({p.name: p.read_bytes() for p in (fixture.run / 'signed-bars').iterdir()}, before_copies)

    def test_saved_refuter_command_locks_source_and_snapshot_allocation(self):
        fixture = refuters.ApplyReturns()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.input.write_text(refuters.returned(), encoding='utf-8')
        self.check_refusals(fixture.path, lambda: refutation_apply.main([str(fixture.path), str(fixture.input)]))

    def test_independent_refuter_finding_wins_over_persistence_coverage(self):
        fixture = refuters.ApplyReturns()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.input.write_text(refuters.returned() + refuters.returned('different synthetic claim'), encoding='utf-8')
        before = fixture.path.read_bytes()
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            status, report = invoke(lambda: refutation_apply.main([str(fixture.path), str(fixture.input)]))
        self.assertEqual(status, 1, report)
        self.assertIn('unmatched 1', report)
        self.assertIn('not graded', report)
        self.assertIn('unread remainder 1', report)
        self.assertEqual(fixture.path.read_bytes(), before)

    def test_opener_record_and_answer_commands_share_the_transaction(self):
        fixture = openers.OpenerCommands()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.assertEqual(0, fixture.record('Note 1\nadult female\n',
                                          [{'note': 1, 'name': None, 'age': 'adult', 'sex': 'female'}]).returncode)
        record = fixture.run / 'openers.json'
        commands = (
            ['record', '--run', str(fixture.run), '--source', str(fixture.source),
             '--readings', str(fixture.readings), '--service-date', '2026-01-01'],
            ['answer', '--run', str(fixture.run), '--note', '1', '--name', 'Example Person',
             '--reply', 'The synthetic encounter name is Example Person.'],
        )
        for command in commands:
            with self.subTest(command=command[0]):
                self.check_refusals(record, lambda: encounter_openers.main(command))

    def test_capture_worker_commands_preserve_each_existing_machine_kind(self):
        fixture = videos.CaptureGate()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for name in ('capture.json', 'slide-terms.json', 'pass-1.json', 'pass-2.json', 'disagreements.json'):
            path = fixture.root / name
            value = json.loads(path.read_bytes())
            # Replace only the heavy capture stage; the native worker dispatch and
            # committed machine-record writer execute for every retained kind.
            with self.subTest(kind=name), artifact_lock.hold(fixture.root, 'synthetic parent capture'), mock.patch.object(
                case_video, 'prepare', side_effect=lambda args, root: case_video.write_json(path, value)
            ):
                self.check_refusals(path, lambda: case_video.main(
                    ['prepare', str(fixture.run), '--source', 'synthetic-source', '--worker']))

    def test_stop_command_preserves_prior_state_and_reports_held_or_failed_write(self):
        fixture = stops.RunStatusContract()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        path = fixture.run / 'run-status.json'
        path.write_text(json.dumps({'status': 'stopped', 'approval_revision': '[]'}), encoding='utf-8')
        before = path.read_bytes()
        message = f'Run status: {fixture.run.name} — stopped - synthetic stop'
        with artifact_lock.hold(path, 'synthetic state holder'):
            response = fixture.grade(message)
        self.assertEqual(response['decision'], 'block')
        self.assertIn('unreadable — held by another task:', response['reason'])
        self.assertEqual(path.read_bytes(), before)
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            response = fixture.grade(message)
        self.assertEqual(response['decision'], 'block')
        self.assertIn('run-status.json: unreadable — could not be opened', response['reason'])
        self.assertNotIn('PRIVATE-PLANTED', str(response))
        self.assertEqual(path.read_bytes(), before)

    def test_capture_parent_locks_before_preflight_and_holds_through_worker(self):
        fixture = videos.CaptureGate()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        python = fixture.run / 'synthetic-worker-python'
        python.write_bytes(b'synthetic executable placeholder')
        command = ['transcribe', str(fixture.run), '--terms', str(fixture.root / 'slide-terms.json'),
                   '--python', str(python)]
        with artifact_lock.hold(fixture.root, 'synthetic parent holder'), mock.patch.object(case_video, 'valid_capture') as preflight:
            status, report = invoke(lambda: case_video.main(command))
        self.assertEqual(status, 2, report)
        self.assertIn('unreadable — held by another task:', report)
        preflight.assert_not_called()
        original = case_video.valid_capture
        first = True
        def preflight(root, **kwargs):
            nonlocal first
            if first:
                with self.assertRaises(artifact_lock.ArtifactBusy):
                    with artifact_lock.hold(root, 'competing preflight'):
                        self.fail('preflight preceded root lock')
                first = False
            return original(root, **kwargs)
        def worker(*args, **kwargs):
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(fixture.root, 'competing worker'):
                    self.fail('worker ran after root unlock')
            return mock.Mock(returncode=0)
        with mock.patch.object(case_video, 'valid_capture', side_effect=preflight), mock.patch.object(
            case_video.subprocess, 'run', side_effect=worker
        ):
            status, report = invoke(lambda: case_video.main(command))
        self.assertEqual(status, 0, report)
