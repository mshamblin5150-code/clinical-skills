"""ADR 0380/0433 literal-name controls through the public scanner; synthetic."""
# phi-scan: synthetic
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import artifact_lock_test_support
import reader_remarks

TOOLS = Path(__file__).resolve().parent
NOTE = ('Start time: 0800, estimated\nEnd time: 0830, estimated\n'
        'S:\nCough.\nO:\n{objective}\nA:\nDifferential:\n'
        '1. Cough - R05.9: most likely.\nP:\nFollow up.\n---\n'
        'FILLED·proposed 1. {proposal}\n')


class ObjectivePairs(unittest.TestCase):
    def grade(self, root, objective, proposal, *, show=False, end='0830', window=True):
        note = root / 'note-1.md'
        note.write_text(NOTE.format(objective=objective, proposal=proposal).replace(
            'End time: 0830', f'End time: {end}'), encoding='utf-8')
        shift = root / 'shift-values.json'
        if window:
            shift.write_text(json.dumps({'start': '0800', 'duration': {'hours': 8, 'minutes': 0}}), encoding='utf-8')
        elif shift.exists():
            shift.unlink()
        return subprocess.run([sys.executable, str(TOOLS / 'differential_scan.py'), str(root),
                               '--note', str(note), *(['--show'] if show else [])],
                              capture_output=True, encoding='utf-8', errors='replace')

    def test_test_drug_and_referral_names_count_without_affecting_any_exit(self):
        forms = (('Recommend CBC', 'CBC ordered.'),
                 ('Start amoxicillin 500 mg PO daily', 'Amoxicillin given.'),
                 ('Refer to dermatology', 'Dermatology referral ordered.'))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for proposal, objective in forms:
                for end, window, expected in (('0830', True, 0), ('0930', True, 1), ('0830', False, 2)):
                    with self.subTest(proposal=proposal, exit=expected):
                        absent = self.grade(root, 'Normal appearance.', proposal, end=end, window=window)
                        matched = self.grade(root, objective, proposal, end=end, window=window)
                        self.assertEqual(expected, absent.returncode, absent.stdout + absent.stderr)
                        self.assertEqual(absent.returncode, matched.returncode, matched.stdout + matched.stderr)
                        self.assertIn('Objective candidates, never graded: 0', absent.stdout)
                        self.assertIn('Objective candidates, never graded: 1', matched.stdout)

    def test_own_name_counts_but_a_drug_page_title_or_subjective_name_does_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for proposal, expected in (('Recommend CBC [uptodate drug: amoxicillin]', 1),
                                       ('Recommend amoxicillin [uptodate drug: CBC]', 0),
                                       ('Recommend CBCD', 0)):
                result = self.grade(root, 'CBC ordered.', proposal)
                self.assertIn(f'Objective candidates, never graded: {expected}', result.stdout)
            result = self.grade(root, 'Normal appearance.', 'Recommend Cough')
            self.assertIn('Objective candidates, never graded: 0', result.stdout)

    def test_private_pairs_are_attributed_once_and_named_run_records_stay_out(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ('shift-summary.md', 'delegated-answers.md', 'reread.md'):
                (root / filename).write_text(NOTE.format(objective='CBC ordered.', proposal='Recommend CBC'), encoding='utf-8')
            public = self.grade(root, 'PRIVATE-SYNTHETIC CBC ordered.\nCBC resulted.', 'Recommend CBC')
            private = self.grade(root, 'PRIVATE-SYNTHETIC CBC ordered.\nCBC resulted.', 'Recommend CBC', show=True)
            self.assertEqual(0, public.returncode, public.stdout + public.stderr)
            self.assertEqual(public.returncode, private.returncode)
            self.assertIn('Objective candidates, never graded: 1', public.stdout)
            self.assertIn('  Objective candidates, never graded: 1', reader_remarks.coverage_lines(public.stdout))
            self.assertNotIn('PRIVATE-SYNTHETIC', public.stdout + public.stderr)
            self.assertIn('note-1.md', private.stdout)
            self.assertIn('-> Objective line ', private.stdout)
            self.assertIn('PRIVATE-SYNTHETIC', private.stdout)


class SkillAgreement(unittest.TestCase):
    def test_handoffs_keep_their_distinct_roles_and_rules(self):
        repo = TOOLS.parent
        batch = (repo / 'skills/batch-shift/SKILL.md').read_text(encoding='utf-8')
        clinical = (repo / 'skills/clinical-note/SKILL.md').read_text(encoding='utf-8')
        agents = (repo / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('check writes nothing', batch)
        self.assertIn('once per final numbered note as a non-authoring **Grader handoff**', batch)
        self.assertIn('is not a terminal grader', agents)
        self.assertIn('the memory index together with the subject list', agents)
        self.assertIn('A blanket delegation never supplies', clinical)
        self.assertIn('approval confirms each listed pair', clinical)
