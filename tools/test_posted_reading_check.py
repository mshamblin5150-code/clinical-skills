"""Standalone checks for the shared posted-reading boundary (synthetic records)."""

import unittest
import ast
import tempfile
from dataclasses import replace
from pathlib import Path

import discussion_artifact as artifact


class PostedReadingCheck(unittest.TestCase):
    def test_core_has_clean_missing_and_stale_controls(self):
        reading = artifact.read_posted_readings(
            '## REREAD: example\nSUBMISSION-SHA256: ' + 'a' * 64 + '\n'
        )[0]
        self.assertEqual((), artifact.check_posted_reading(reading, 'a' * 64))
        self.assertEqual(
            ['missing-record'],
            [item.code for item in artifact.check_posted_reading(None, 'a' * 64)],
        )
        for digest in ('', 'bad', 'b' * 64):
            with self.subTest(digest=digest):
                self.assertEqual(
                    ['fingerprint'],
                    [item.code for item in artifact.check_posted_reading(
                        replace(reading, submission_sha256=digest), 'a' * 64
                    )],
                )

    def test_every_optional_outcome_has_a_defect_and_clean_control(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            docx = run / 'example.docx'
            docx.write_bytes(b'local Word bytes')
            (run / 'posted').mkdir()
            copy = run / 'posted' / docx.name
            copy.write_bytes(docx.read_bytes())
            reading = artifact.read_posted_readings(
                '## REREAD: example\nPOST-URL: https://example.org/?entry_id=9\n'
                'POSTED: today\nREAD: 1 of 1 read\n'
                'SUBMISSION-SHA256: ' + 'a' * 64 + '\n'
                'VERDICT: matches - copied text matches\n'
                'TIME-LOG: not requested\n'
                'LEGACY-DISPLAY: expected - observed display\n'
                'COMPOSER-OUTCOME: attachment\nHTML-BYTES: 42\n'
                'ATTACHMENT-COUNT: 1\nSUBMITTED-FILE: example.docx\n'
                'REFUSAL: 2026-10-03 - observed refusal\nATTACHMENT: posted/example.docx\n'
                'VISIT: 1 | patient 1 | reference matched P-1 | patient-detail=/1 | '
                'note-view=/view?resultid=1 | visit-date=today | finished=today | matches\n'
            )[0]
            options = dict(posted_fields=True, verdict=True, matches_only=True,
                           entry_link=True, composer=True, html_bytes=42,
                           run=run, docx=docx, expected_visits=1, legacy_display=True,
                           expected_submitted_files=('example.docx',),
                           saved_post_url=reading.post_url, saved_posted='today')
            self.assertEqual((), artifact.check_posted_reading(reading, 'a' * 64, **options))
            cases = {
                'posted-fields': dict(posted=''),
                'unknown-verdict': dict(verdict='maybe'),
                'bare-verdict': dict(verdict_detail=''),
                'completion-verdict': dict(verdict='diverges'),
                'unlocated': dict(post_url='https://example.org/'),
                'composer-outcome': dict(composer_outcome='maybe'),
                'html-bytes': dict(html_bytes='41'),
                'refusal': dict(refusal='undated refusal'),
                'attachment-field': dict(attachment=''),
                'attachment-copy': dict(attachment='../example.docx'),
                'portal-fields': dict(missing_fields=('POST-URL',)),
                'read-count': dict(read='1 of 2 read'),
                'visit-count': dict(visits=()),
                'time-log': dict(time_log=''),
                'visit-fields': dict(visits=('2 | missing locators',)),
                'legacy-display': dict(legacy_display='maybe'),
                'attachment-count': dict(attachment_count='2'),
                'submitted-files': dict(submitted_files=('other.docx',)),
                'post-link': dict(post_url='https://example.org/?entry_id=8'),
            }
            observed = {'missing-record', 'fingerprint'}
            for code, changes in cases.items():
                with self.subTest(code=code):
                    results = artifact.check_posted_reading(replace(reading, **changes), 'a' * 64, **options)
                    self.assertIn(code, [item.code for item in results])
                    observed.update(item.code for item in results)
                    self.assertTrue(all(item.message for item in results))
            metadata_options = dict(options, saved_posted='')
            results = artifact.check_posted_reading(reading, 'a' * 64, **metadata_options)
            self.assertEqual(['post-metadata'], [item.code for item in results])
            observed.update(item.code for item in results)
            self.assertEqual((), artifact.check_posted_reading(reading, 'a' * 64, **options))
            for option in ('roster_ids', 'duplicate_ids'):
                results = artifact.check_posted_reading(reading, 'a' * 64, **options, **{option: {'9'}})
                self.assertEqual(['borrowed'], [item.code for item in results])
                observed.add('borrowed')
            copy.write_bytes(b'changed posted copy')
            self.assertEqual(['attachment-digest'], [item.code for item in artifact.check_posted_reading(reading, 'a' * 64, **options)])
            observed.add('attachment-digest')
            self.assertEqual(set(artifact.POSTED_READING_MESSAGES), observed)

    def test_members_never_compare_the_posted_fingerprint_themselves(self):
        members = ('discussion_post_scan', 'discussion_reply_scan', 'peer_critique_scan',
                   'checks_ledger', 'deck_scan', 'medatrax_posting',
                   'assignment_submission', 'approval_record')
        for member in members:
            with self.subTest(member=member):
                tree = ast.parse((Path(__file__).parent / (member + '.py')).read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        self.assertFalse(any(isinstance(child, ast.Attribute) and child.attr == 'submission_sha256'
                                             for child in ast.walk(node)))
