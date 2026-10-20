"""ADR 0377 skill agreement and the existing link-source grading ceiling."""
# phi-scan: synthetic
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from prose_bind import section

ROOT = Path(__file__).resolve().parent.parent


class CausalLinkAgreement(unittest.TestCase):
    def test_note_prose_and_coding_have_their_distinct_sources(self):
        note = (ROOT / 'skills/clinical-note/SKILL.md').read_text(encoding='utf-8')
        relationship = section(note, '#### A relationship is stated only when the clinician stated it')
        for phrase in ('caused, complicated, or is unrelated', 'shorthand or recorded answer',
                       'side by side', "code's official descriptor", 'paronychia', 'osteomyelitis',
                       '`E11.69`', 'no link sentence'):
            self.assertIn(phrase, relationship)
        coding = (ROOT / 'skills/icd10-cpt/SKILL.md').read_text(encoding='utf-8')
        linked = coding.split('#### Linked conditions take the `with` combination code\n', 1)[1].split('\n#### ', 1)[0]
        for phrase in ('index `with` path', '`clinician:`', 'own words',
                       'neither source is not proposed', 'do not grade these link-source forms'):
            self.assertIn(phrase, linked)
        blind = section(coding, '#### Descriptor agreement is a separate blind read')
        for phrase in ('remove the sentence', 'before recoding', 'standing rule 6',
                       'Before the blind brief', 'every `clinician:`', 'shorthand or recorded answer'):
            self.assertIn(phrase, blind)

    def test_case_study_presumed_code_exemption_preserves_the_causal_claim_rule(self):
        text = (ROOT / 'skills/practicum-case-study/SKILL.md').read_text(encoding='utf-8')
        start = text.index('**A causal link drawn between two')
        rule = text[start:text.index('\n## ', start)]
        for phrase in ('step 3 claim record', '`### DEPARTURE:`',
                       'index presumes through `with`', 'needs neither', 'recorded index path',
                       'with no index path still needs both'):
            self.assertIn(phrase, rule)

    def test_existing_public_graders_do_not_discriminate_link_source_forms(self):
        # A valid index form, a clinician form, and neither all take the same
        # existing grade. A clean grade therefore cannot verify this new rule.
        reasons = ('index: Diabetes > type 2 > with > osteomyelitis',
                   'clinician: the osteomyelitis is a complication of diabetes',
                   'a stock reason naming no source')
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            worksheet = run / 'codes.md'
            for reason in reasons:
                worksheet.write_text(
                    'ICD-10  E11.69  Type 2 diabetes mellitus with other specified complication\n'
                    '  SOURCE: filled\n'
                    '  ANCHOR: "Documented conditions"\n'
                    f'  SPECIFICITY: complete - {reason}\n\n'
                    '--- CODED, ANCHOR WAS FILLED - CONFIRM BEFORE SUBMITTING ---\n'
                    'E11.69 - Documented conditions\n', encoding='utf-8')
                for tool in ('specificity_scan.py', 'anchor_scan.py'):
                    result = subprocess.run([sys.executable, str(ROOT / 'tools' / tool), str(run)],
                                            capture_output=True, encoding='utf-8', errors='replace')
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
