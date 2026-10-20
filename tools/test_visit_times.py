"""ADR 0410 public-command controls; all notes below are synthetic."""
# phi-scan: synthetic
import contextlib
from datetime import timedelta
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import artifact_lock_test_support
import differential_scan
import filled_vitals_census
import visit_times


class PublicCommands(unittest.TestCase):
    def test_all_three_commands_enforce_each_ruled_case(self):
        cases = (
            ((('0800', '0830'), ('0835', '0855')), '0800', 0),
            ((('0800', '0930'),), '0800', 1),
            ((('0800', '0845'),), '0800', 1),
            ((('0800', '0822'),), '0800', 1),
            ((('0800', '0830'), ('0825', '0855')), '0800', 1),
            ((('0800', '0830'), ('0830', '0855')), '0800', 1),
            ((('0755', '0825'),), '0800', 1),
            ((('2350', '0010'), ('0015', '0045')), '2300', 0),
            ((('0800', '0830'),), None, 2),
            ((('0800', '0830'), ('0830', '0900')), None, 1),
            ((('unreadable', '0830'),), '0800', 2),
        )
        for pairs, shift, expected in cases:
            with self.subTest(pairs=pairs, shift=shift), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                for number, (start, end) in enumerate(pairs, 1):
                    (run / f'note-{number}.md').write_text(
                        f'Start time: {start}, estimated\nEnd time: {end}, estimated\n'
                        'Differential:\n1. Cough - R05.9: most likely.\n'
                        'FILLED·asserted   BP 118/76 filled.\n', encoding='utf-8')
                if shift:
                    (run / 'shift-values.json').write_text(json.dumps(
                        {'start': shift, 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
                # A standalone --note invocation reads exactly one encounter.
                # Exercise multi-note ordering through its approved population seam.
                with patch.object(differential_scan.medatrax_posting, 'note_paths',
                                  return_value=tuple(sorted(run.glob('note-*.md')))):
                    for command in (visit_times.main, filled_vitals_census.main, differential_scan.main):
                        output = io.StringIO()
                        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                            status = command([str(run)])
                        self.assertEqual(expected, status, output.getvalue())
                        self.assertEqual(1, sum(line.startswith('unread remainder ') for line in output.getvalue().splitlines()))

    def test_executable_command_and_private_output(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'note-1.md').write_text('Start time 0800\nEnd time 0900\n', encoding='utf-8')
            result = subprocess.run([sys.executable, visit_times.__file__, str(run)], capture_output=True,
                                    encoding='utf-8', errors='replace')
            self.assertEqual(1, result.returncode)
            self.assertNotIn('0800', result.stdout)
            self.assertNotIn('0900', result.stdout)

    def test_real_executables_pass_a_single_note_and_refuse_its_changed_times(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            note = run / 'note-1.md'
            clean = ('Start time 0800\nEnd time 0830\n'
                     'Differential:\n1. Cough - R05.9: most likely.\n'
                     'FILLED·asserted   BP 118/76 filled.\n')
            (run / 'shift-values.json').write_text(json.dumps(
                {'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
            for expected, text in ((0, clean), (1, clean.replace('0830', '0900'))):
                note.write_text(text, encoding='utf-8')
                for module in (visit_times, filled_vitals_census, differential_scan):
                    result = subprocess.run([sys.executable, module.__file__, str(run)],
                                            capture_output=True, encoding='utf-8', errors='replace')
                    self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
                    self.assertEqual(1, sum(line.startswith('unread remainder ') for line in result.stdout.splitlines()))

    def test_absent_null_or_damaged_shift_record_keeps_note_tests_active(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'note-1.md').write_text('Start time 0800\nEnd time 0830\n', encoding='utf-8')
            for text in ('{', 'null', '{"start":null,"duration":null}',
                         '{"start":"0800","duration":null}',
                         '{"start":"0800","duration":{"hours":8,"minutes":true}}'):
                (run / 'shift-values.json').write_text(text, encoding='utf-8')
                result = visit_times.check(run, batch=True)
                self.assertEqual(1, result.pairs)
                self.assertTrue(result.incomplete)
                self.assertIn('not checked', visit_times.report(result))

    def test_reader_forms_and_tier_restatement(self):
        for text in ('| Start time | 10:25, estimated |\n| End time | 10:55, estimated |',
                     'Start time:   09:20, estimated\nEnd time: 09:50, estimated',
                     'Start time   1105, estimated\nEnd time 1135, estimated'):
            pair, unread = visit_times.read_pair(text + '\nStart 15:05, End 15:40, both estimated')
            self.assertIsNotNone(pair)
            self.assertEqual(0, unread)

    def test_each_documented_field_form_has_a_readable_committed_member(self):
        # Derive the source population independently of FIELD; no preserved
        # record is normalized or copied into a new fixture.
        root = Path(__file__).resolve().parent.parent
        texts = [path.read_text(encoding='utf-8') for path in (root / 'fixtures').rglob('*.md')]
        for shape in (r'^\| Start time \|.*$', r'^Start time:[ \t]+.*$', r'^Start time[ \t]+\d{4}.*$'):
            lines = [match.group() for text in texts for match in re.finditer(shape, text, re.M)]
            self.assertTrue(lines, 'committed form has no independently located member')
            self.assertTrue(any(visit_times.read_pair(line + '\nEnd time 2355')[0] is not None
                                for line in lines), 'reader reached no committed member of the form')

    def test_standalone_ambiguity_does_not_fall_back_to_records(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ('note.md', 'other.md'):
                (run / name).write_text('Start time 0800\nEnd time 0830\n', encoding='utf-8')
            result = visit_times.check(run, batch=False)
            self.assertFalse(result.population_checked)
            self.assertEqual(0, result.notes)
            self.assertEqual(1, visit_times.check(run, batch=False, note=run / 'note.md').pairs)

    def test_historical_approval_omits_the_new_row(self):
        token = visit_times.completion_checks.MOMENTS.set({'approval': visit_times.completion_checks.instant('2026-10-19')})
        try:
            result = visit_times.check(Path('absent'), batch=True)
            self.assertFalse(result.graded)
            self.assertFalse(result.incomplete)
        finally:
            visit_times.completion_checks.MOMENTS.reset(token)

    def test_the_exact_build_boundary_preserves_earlier_approvals(self):
        start, _ = visit_times.completion_checks.registry()['visit_times:visit-times']
        for observed, graded in ((start - timedelta(microseconds=1), False), (start, True)):
            token = visit_times.completion_checks.MOMENTS.set({'approval': observed})
            try:
                self.assertEqual(graded, visit_times.check(Path('absent'), batch=True).graded)
            finally:
                visit_times.completion_checks.MOMENTS.reset(token)
