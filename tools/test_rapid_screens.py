"""ADR 0404 paired public grader controls, using synthetic profiles and notes."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
from datetime import timedelta
import json
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import completion_checks
import rapid_screens
import reader_remarks
import differential_scan
import filled_vitals_census
import visit_times
from prose_bind import bind, NAMING

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
NOTE = ('Start time 0800\nEnd time 0830\nS:\nCough.\nO:\n{screen}\n'
        'A:\nDifferential:\n1. Cough - R05.9: most likely.\nP:\nFollow up.\n'
        '---\nFILLED·asserted   BP 118/76 filled.\n')


class PublicRapidScreens(unittest.TestCase):
    def invoke(self, run, module, text, *, declared=True, profile=True, times=True):
        note = run / 'note-1.md'
        note.write_text(NOTE.format(screen=text), encoding='utf-8')
        source = run / 'profile.txt'
        source.write_text(rapid_screens.DECLARATION if declared else 'Other account settings.', encoding='utf-8')
        (run / 'shift-values.json').write_text(json.dumps({
            'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
        if not times:
            (run / 'shift-values.json').unlink()
        args = [str(run), *(['--note', str(note)] if module == 'differential_scan' else [])]
        if profile:
            args += ['--profile', str(source)]
        return subprocess.run([sys.executable, str(TOOLS / (module + '.py')), *args],
                              capture_output=True, encoding='utf-8', errors='replace')

    def test_both_paired_public_commands_refuse_pending_and_keep_ruled_exceptions(self):
        cases = (
            ('Rapid strep pending.', 1),
            ('Influenza screen awaiting a result.', 1),
            ('COVID-19 rapid antigen: unresulted.', 1),
            ('RSV screen: no result.', 1),
            ('Rapid strep not performed.', 0),
            ('Rapid flu declined.', 0),
            ('Send-out strep culture pending.', 0),
            ('COVID-19 PCR pending.', 0),
            ('Rapid strep declined; rapid flu pending.', 1),
            ('Rapid flu negative; PCR pending.', 0),
            ('Rapid strep not performed, RSV screen awaiting results.', 1),
            ('Rapid strep pending and throat culture pending.', 1),
            ('Rapid flu not performed but RSV screen pending.', 1),
            ('Rapid flu negative and PCR pending.', 0),
        )
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for module in ('differential_scan', 'filled_vitals_census'):
                for text, expected in cases:
                    with self.subTest(module=module, text=text):
                        result = self.invoke(run, module, text)
                        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
                        self.assertIn('rapid screens: notes read 1;', result.stdout)
                        self.assertEqual(1, sum(line.startswith('unread remainder ') for line in result.stdout.splitlines()))
                        self.assertNotIn(text, result.stdout + result.stderr)

    def test_no_declaration_and_no_profile_are_distinct_shown_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for module in ('differential_scan', 'filled_vitals_census'):
                declared = self.invoke(run, module, 'Rapid strep pending.', declared=False)
                omitted = self.invoke(run, module, 'Rapid strep pending.', profile=False)
                for result, reason in ((declared, 'profile has no rapid-screen declaration'),
                                       (omitted, 'no --profile supplied')):
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    line = 'rapid screens: not graded - ' + reason
                    self.assertIn(line, result.stdout)
                    self.assertIn(line, reader_remarks.coverage_lines(result.stdout))

    def test_pending_finding_outranks_other_incomplete_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for module in ('differential_scan', 'filled_vitals_census'):
                clean = self.invoke(run, module, 'Rapid strep negative.', times=False)
                failed = self.invoke(run, module, 'Rapid strep pending.', times=False)
                self.assertEqual(2, clean.returncode, clean.stdout + clean.stderr)
                self.assertEqual(1, failed.returncode, failed.stdout + failed.stderr)

    def test_both_public_commands_report_unread_profile_as_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for module in ('differential_scan', 'filled_vitals_census'):
                self.invoke(run, module, 'Rapid strep negative.')
                result = subprocess.run([
                    sys.executable, str(TOOLS / (module + '.py')), str(run),
                    '--profile', str(run / 'missing-profile.txt'),
                    *(['--note', str(run / 'note-1.md')] if module == 'differential_scan' else [])],
                    capture_output=True, encoding='utf-8', errors='replace')
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertIn('rapid screens: not checked - profile or note population unread', result.stdout)
                self.assertEqual(1, sum(line == 'unread remainder 1' for line in result.stdout.splitlines()))

    def test_no_implicit_profile_read_and_exact_approval_boundary(self):
        with patch.object(Path, 'read_text', side_effect=AssertionError('unexpected file read')):
            self.assertEqual('unsupplied', rapid_screens.check(Path('absent'), batch=True).state)
        start, _moment = completion_checks.registry()[rapid_screens.CHECK]
        for observed, state in ((start - timedelta(microseconds=1), 'historical'), (start, 'unsupplied')):
            with self.subTest(observed=observed):
                token = completion_checks.MOMENTS.set({'approval': observed})
                try:
                    self.assertEqual(state, rapid_screens.check(Path('absent'), batch=True).state)
                finally:
                    completion_checks.MOMENTS.reset(token)

    def test_unread_profile_or_body_keeps_counts_and_other_findings_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            profile = run / 'profile.txt'
            profile.write_text(rapid_screens.DECLARATION, encoding='utf-8')
            (run / 'note-1.md').write_text(NOTE.format(screen='Rapid strep pending.'), encoding='utf-8')
            (run / 'note-2.md').write_text('S:\nRapid flu pending.\n', encoding='utf-8')
            result = rapid_screens.check(run, batch=True, profile=profile)
            self.assertEqual((1, 1, 1), (result.notes, len(result.findings), result.unread))
            self.assertTrue(result.incomplete)
            self.assertEqual(1, rapid_screens.check(run, batch=True, profile=run).unread)

    def test_both_native_commands_use_the_exact_approval_boundary(self):
        start, _moment = completion_checks.registry()[rapid_screens.CHECK]
        original_grading = completion_checks.grading
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            note = run / 'note-1.md'
            note.write_text(NOTE.format(screen='Rapid strep pending.'), encoding='utf-8')
            profile = run / 'profile.txt'
            profile.write_text(rapid_screens.DECLARATION, encoding='utf-8')
            (run / 'shift-values.json').write_text(json.dumps({
                'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
            for module in (differential_scan, filled_vitals_census):
                for observed, expected in ((start - timedelta(microseconds=1), 0), (start, 1)):
                    @contextlib.contextmanager
                    def dated_grading(path, submission):
                        # Isolate only the retained approval moment at the normal
                        # command grading boundary; all artifact rows run unchanged.
                        with original_grading(path, submission):
                            token = completion_checks.MOMENTS.set({'approval': observed})
                            try:
                                yield
                            finally:
                                completion_checks.MOMENTS.reset(token)
                    args = [str(run), '--profile', str(profile)]
                    if module is differential_scan:
                        args += ['--note', str(note)]
                    output = io.StringIO()
                    with self.subTest(module=module.__name__, observed=observed), \
                         patch.object(completion_checks, 'grading', dated_grading), \
                         contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(expected, module.main(args), output.getvalue())
                    self.assertIn('pending findings 1' if expected else
                                  'rapid screens: not graded - check starts after approval', output.getvalue())

    def test_approved_standalone_population_and_numbered_batch_exclude_run_records(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            profile = run / 'profile.txt'
            profile.write_text(rapid_screens.DECLARATION, encoding='utf-8')
            note = run / 'note-1.md'
            note.write_text(NOTE.format(screen='Rapid strep negative.'), encoding='utf-8')
            for name in ('shift-summary.md', 'delegated-answers.md', 'reread.md'):
                (run / name).write_text(NOTE.format(screen='Rapid strep pending.'), encoding='utf-8')
            self.assertEqual((), rapid_screens.check(run, batch=True, profile=profile).findings)
            # Preserve the existing strict approval envelope and source selection.
            payload = {'version': 1, 'approval_revision': 1, 'items': [{
                'skill': 'clinical-note', 'submission': 'synthetic', 'sources': [str(note)],
                'sha256': 'a' * 64, 'approval_revision': 1, 'grader_args': [str(run)],
                'posting_route': 'awaiting-posting', 'pregrade_status': 'clean'}]}
            (run / 'posting-approvals.json').write_text(json.dumps(payload), encoding='utf-8')
            (run / 'other.md').write_text('Rapid flu pending.', encoding='utf-8')
            result = rapid_screens.check(run, batch=False, profile=profile)
            self.assertEqual(1, result.notes)
            self.assertFalse(result.findings)

    def test_preserved_rapid_test_forms_are_reached_without_mutating_records(self):
        for phrase in ('rapid influenza A and B test', 'rapid group A streptococcus test'):
            members = [path for path in (ROOT / 'fixtures' / 'slot-form-run').glob('*.md')
                       if phrase.casefold() in path.read_text(encoding='utf-8').casefold()]
            self.assertTrue(members, phrase)
            self.assertTrue(all(rapid_screens.read_note(path.read_text(encoding='utf-8'))[0]
                                for path in members), phrase)

    def test_new_population_dependency_does_not_abort_independent_host_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            profile = run / 'profile.txt'
            profile.write_text(rapid_screens.DECLARATION, encoding='utf-8')
            (run / 'note-1.md').write_text(NOTE.format(screen='Rapid strep negative.').replace(
                '1. Cough - R05.9: most likely.', '1. Cough: most likely.'), encoding='utf-8')
            damaged = run / 'posting-approvals.json'
            damaged.write_bytes(b'{')
            before = damaged.read_bytes()
            resolve = rapid_screens.medatrax_posting.note_paths
            calls = 0
            def population(*args, **kwargs):
                nonlocal calls
                calls += 1
                # Isolate pre-existing repair and visit-time paths: only the
                # new rapid-screen row reads this damaged population in this control.
                return resolve(*args, **kwargs) if calls == 1 else ()
            output = io.StringIO()
            with patch.object(rapid_screens.medatrax_posting, 'note_paths', side_effect=population), \
                 patch.object(visit_times, 'check', return_value=visit_times.Result(graded=False)), \
                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                status = differential_scan.main([str(run), '--profile', str(profile)])
            self.assertEqual(1, status, output.getvalue())
            self.assertIn('rapid screens: not graded - approved note population unread', output.getvalue())
            self.assertEqual(1, sum(line == 'unread remainder 1' for line in output.getvalue().splitlines()))
            self.assertEqual(before, damaged.read_bytes())


    def test_handwritten_damage_and_rapid_findings_keep_each_items_approval_boundary(self):
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        original_grading = completion_checks.grading
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            note = run / 'note-1.md'
            note.write_text(NOTE.format(screen='Rapid strep pending.'), encoding='utf-8')
            profile = run / 'profile.txt'
            profile.write_text(rapid_screens.DECLARATION, encoding='utf-8')
            (run / 'shift-values.json').write_text(json.dumps({
                'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
            answers = run / 'delegated-answers.md'
            answers.write_bytes(b'\x07\n## QUESTION: Synthetic question\nRULE: none found\n'
                                b'ANSWER: Follow up.\nNOTE: note-1.md\nSECTIONS: P\n')
            before = answers.read_bytes()
            for module in (differential_scan, filled_vitals_census):
                for label, moment in (('old', old), ('exact', start), ('unknown', None)):
                    @contextlib.contextmanager
                    def dated_grading(path, submission):
                        with original_grading(path, submission):
                            global_token = completion_checks.MOMENTS.set({'approval': old})
                            items_token = completion_checks.ITEM_MOMENTS.set({
                                'old-sibling': old,
                                **({'synthetic': moment} if moment is not None else {}),
                            })
                            try:
                                yield
                            finally:
                                completion_checks.ITEM_MOMENTS.reset(items_token)
                                completion_checks.MOMENTS.reset(global_token)
                    args = [str(run), '--submission', 'synthetic', '--profile', str(profile)]
                    if module is differential_scan:
                        args += ['--note', str(note)]
                    output = io.StringIO()
                    with self.subTest(module=module.__name__, moment=label), contextlib.ExitStack() as stack:
                        stack.enter_context(patch.object(completion_checks, 'grading', dated_grading))
                        for sibling in (module.aar_scan, module.medatrax_posting,
                                        module.artifact_repairs, module.outbound_search):
                            stack.enter_context(patch.object(sibling, 'completion_gate', return_value=(False, 'synthetic: clean')))
                        stack.enter_context(patch.object(module.approval_record, 'apply_completion_gate', side_effect=lambda grade, *args: grade))
                        stack.enter_context(contextlib.redirect_stdout(output))
                        stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                        self.assertEqual(1, module.main(args), output.getvalue())
                    report = output.getvalue()
                    self.assertIn('pending findings 1', report)
                    self.assertEqual(label != 'old', 'U+0007' in report)
                    self.assertEqual(1, sum(line.startswith('unread remainder ') for line in report.splitlines()))
                    self.assertEqual(before, answers.read_bytes())


class SkillAgreement(unittest.TestCase):
    def test_skill_names_the_reading_boundary_without_copying_its_limits(self):
        clinical = (ROOT / 'skills/clinical-note/SKILL.md').read_text(encoding='utf-8')
        self.assertEqual((), bind(rapid_screens.DECLARED_LIMITS, clinical, mode=NAMING))

    def test_split_stop_and_both_required_paired_invocations_keep_the_contract(self):
        batch = (ROOT / 'skills/batch-shift/SKILL.md').read_text(encoding='utf-8')
        step4 = batch.split('### 4.', 1)[1].split('### 5.', 1)[0]
        self.assertIn('Earlier care mentioned, no identity-map row:', step4)
        self.assertIn('read every identity-map row for that name', step4)
        self.assertIn('within three\nyears', step4)
        self.assertIn('whole verbatim reply', step4)
        self.assertIn('delegate never answers', step4)
        self.assertIn('parsed value per encounter', step4)
        self.assertIn("shared opener command's `answer` route", step4)
        # batch-shift step 4 settles the earlier-care question once.
        self.assertIn('only for an encounter step 4 did not settle', batch)
        clinical = (ROOT / 'skills/clinical-note/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Where an answer to this block can be parsed more than one way', clinical)
        self.assertIn('Rapid screens: negative unless stated', clinical)
        for text, tool in ((batch, 'filled_vitals_census.py'), (clinical, 'differential_scan.py')):
            terminal = next(line for line in text.splitlines() if tool in line and '--submission' in line)
            self.assertIn('--profile <owning checkout>/scratch/medatrax-profile.md', terminal)


if __name__ == '__main__':
    unittest.main()
