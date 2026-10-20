"""ADR 0395 handwritten read boundary; synthetic inputs only."""
# phi-scan: synthetic
import artifact_lock_test_support
from datetime import datetime, timedelta, timezone
import json
import sys
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_record_reader as records
import completion_checks


class HandwrittenRecords(unittest.TestCase):
    def test_only_declared_public_schema_filenames_are_named(self):
        for name, label in (('claims.md', 'claims.md'), ('Sensitive-Private-Name.md', 'file 1 of 1')):
            path = self.path.with_name(name)
            path.write_bytes(b'FIELD: private\x07value\n')
            with self.assertRaises(records.DamagedRecord) as caught:
                records.read_handwritten_record(path).text
            self.assertIn(label + ': line 1: U+0007', str(caught.exception))
            self.assertNotIn('Sensitive-Private-Name', str(caught.exception))
            self.assertNotIn('private', str(caught.exception))
    def test_copied_post_leading_padding_does_not_turn_metadata_into_body(self):
        for padding in ('\n', '\n\n', '  \r\n'):
            for header in ('AUTHOR:\tSynthetic Author', 'AUTHOR\t: Synthetic Author'):
                source = padding + header + '\nREPLIES: 2\nPOST-URL: https://example.org\n\nCopied\tbody\n'
                self.path.write_bytes(source.encode('utf-8'))
                with self.assertRaises(records.DamagedRecord):
                    records.read_handwritten_record(self.path, 'copied-post').text
                clean = source.replace(header, 'AUTHOR: Synthetic Author')
                self.path.write_bytes(clean.encode('utf-8'))
                self.assertIn('Copied\tbody', records.read_handwritten_record(self.path, 'copied-post').text)
        split_metadata = '\nAUTHOR: Synthetic Author\n\nPOST-URL:\thttps://example.org\n\nCopied\tbody\n'
        self.path.write_bytes(split_metadata.encode('utf-8'))
        with self.assertRaises(records.DamagedRecord):
            records.read_handwritten_record(self.path, 'copied-post').text
    def test_context_json_spans_follow_the_owners_case_and_space_grammar(self):
        for name, body in (('go-ahead', '{"submission":"bad\\u0000key"}'),
                           ('Order-Observation', '{"draft":"bad\\u0007text"}'),
                           ('memory-lines', '["bad\\u000ctext"]')):
            for padding in (' ', '  '):
                with self.subTest(name=name, padding=len(padding)):
                    source = f'{padding}{name}: {body}  \r\n'
                    result = records.check_handwritten_text(source, self.path, 'project-context')
                    with self.assertRaises(records.DamagedRecord):
                        result.require_text(force=True)
                    self.assertEqual(1, len(result.diagnostics))

    def test_existing_replacement_decoding_keeps_c0_validation(self):
        kind = records.HandwrittenKind('legacy-replacement', decode_errors='replace')
        self.path.write_bytes(b'FIELD: \xff\n')
        self.assertEqual('FIELD: \ufffd\n', records.read_handwritten_record(self.path, kind).text)
        with self.assertRaises(UnicodeDecodeError):
            records.read_handwritten_record(self.path)
        self.path.write_bytes(b'FIELD: \xff\x07\n')
        with self.assertRaises(records.DamagedRecord) as caught:
            records.read_handwritten_record(self.path, kind).require_text(force=True)
        self.assertIn('U+0007', str(caught.exception))
        with self.assertRaises(ValueError):
            records.HandwrittenKind('invalid', decode_errors='ignore')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name).resolve() / 'project-context.md'

    def test_every_damaged_line_is_named_before_text_can_be_consumed(self):
        self.path.write_bytes(b'FIELD: tab\tbell\x07\nHEADING\x00\x0c\x0b\nvalue\rrest\n')
        result = records.read_handwritten_record(self.path, 'text')
        self.assertEqual((
            'project-context.md: line 1: U+0009',
            'project-context.md: line 1: U+0007',
            'project-context.md: line 2: U+0000',
            'project-context.md: line 2: U+000C',
            'project-context.md: line 2: U+000B',
            'project-context.md: line 3: U+000D',
        ), result.diagnostics)
        with self.assertRaises(records.RecordContentError) as caught:
            _ = result.text
        self.assertNotIsInstance(caught.exception, ValueError)
        self.assertIn('not graded — damaged text', str(caught.exception))
        self.assertNotIn('value', str(caught.exception))

    def test_decoded_json_keys_and_strings_are_checked_before_consumption(self):
        kind = records.HandwrittenKind(
            'image-record', lambda text: (('', text),), frozenset({'images', 'path'}))
        self.path.write_bytes(br'{"images":[{"path":"C:\temp","private\u0000key":"secret\u0007"}]}')
        result = records.read_handwritten_record(self.path, kind)
        self.assertEqual((
            'project-context.md: images[0].path: U+0009',
            'project-context.md: images[0].key[2]: U+0000',
            'project-context.md: images[0].field[2]: U+0007',
        ), result.diagnostics)
        for access in (lambda: result.text, lambda: result.json, lambda: result.json_bodies):
            with self.assertRaises(records.DamagedRecord) as caught:
                access()
            self.assertNotIn('secret', str(caught.exception))
            self.assertNotIn('private', str(caught.exception))

    def test_only_copied_post_body_allows_tab_and_crlf_stays_intact(self):
        clean = 'AUTHOR: Synthetic Author\r\nPOST-URL: https://example.org\r\n\r\nCopied\tbody\x7f\x85\r\n'
        self.path.write_bytes(clean.encode('utf-8'))
        self.assertEqual(clean.replace('\r\n', '\n'), records.read_handwritten_record(self.path, 'copied-post').text)
        raw = clean.replace('\t', ' ')
        self.assertEqual(raw, records.check_handwritten_text(raw, self.path, 'raw-text').text)
        import research_ledger
        self.path.write_bytes(b'DATE: 2026-10-20\r\n\r\n')
        self.assertEqual('2026-10-20', research_ledger.ledger_date(
            records.read_handwritten_record(self.path).text).isoformat())
        for value, kind in ((clean.replace('AUTHOR:', 'AUTHOR:\t'), 'copied-post'),
                            (clean, 'text'), (clean.replace('Copied', '\x07Copied'), 'copied-post')):
            with self.subTest(kind=kind, value=repr(value)):
                self.path.write_bytes(value.encode('utf-8'))
                self.assertTrue(records.read_handwritten_record(self.path, kind).diagnostics)

    def test_json_bodies_in_mixed_records_are_checked_before_business_parsing(self):
        for kind, source, locations in (
            ('attachments', 'ATTACHMENTS: files\r\n[{"local_path":"C:\\temp"}]\r\n', ('body[0].local_path',)),
            ('project-context', 'PROJECT: none\nORDER-OBSERVATION: {"draft":"C:\\temp"}\n'
             'MEMORY-LINES: ["\\u0000"]\n', ('ORDER-OBSERVATION[1].field[1]', 'MEMORY-LINES[1][0]')),
        ):
            with self.subTest(kind=kind):
                self.path.write_bytes(source.encode('utf-8'))
                result = records.read_handwritten_record(self.path, kind)
                self.assertEqual(len(locations), len(result.diagnostics))
                for expected, diagnostic in zip(locations, result.diagnostics):
                    self.assertIn(expected + ': U+', diagnostic)
                with self.assertRaises(records.DamagedRecord):
                    result.require_text()

    def test_one_approval_boundary_withholds_damage_without_waiving_a_rewriter(self):
        boundary = datetime(2026, 10, 20, 10, 59, 37, tzinfo=timezone.utc)
        self.path.write_bytes(b'FIELD: damaged\x07\n')
        for approved, expected in ((boundary - timedelta(microseconds=1), False), (boundary, True)):
            token = completion_checks.MOMENTS.set({'approval': approved})
            self.addCleanup(completion_checks.MOMENTS.reset, token)
            with records.capture_handwritten_damage() as damage:
                with self.assertRaises(records.DamagedRecord) as caught:
                    records.read_handwritten_record(self.path).require_text(force=True)
                finding, report = records.damaged_record_result(caught.exception, check='synthetic record checks')
                self.assertEqual(expected, finding)
                self.assertEqual(expected, damage[self.path].finding)
                self.assertIn('not graded', report)
                if not expected:
                    self.assertNotIn('U+0007', report)
                    finding, report = records.damaged_record_result(
                        caught.exception, check='record rewrite', force=True)
                    self.assertTrue(finding)
                    self.assertIn('U+0007', report)

    def test_boundary_fixture_uses_canonical_identity_for_native_equivalent_temp_paths(self):
        canonical = self.path.parent / 'synthetic-long-directory-for-fixture'
        canonical.mkdir()
        alias = self.path.parent / 'alias'
        alias.mkdir()
        supplied = alias / '..' / canonical.name
        route = 'existing-directory/alias/..'
        if sys.platform == 'win32':
            import ctypes
            function = ctypes.windll.kernel32.GetShortPathNameW
            function.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
            function.restype = ctypes.c_uint32
            size = function(str(canonical), None, 0)
            if size:
                buffer = ctypes.create_unicode_buffer(size)
                if function(str(canonical), buffer, size):
                    short = Path(buffer.value)
                    if short != canonical and short.resolve() == canonical.resolve():
                        supplied, route = short, 'GetShortPathNameW'
        with self.subTest(route=route):
            self.assertNotEqual(supplied, supplied.resolve())
            self.assertTrue(supplied.samefile(canonical))
            class Factory:
                name = str(supplied)
                def cleanup(self):
                    pass  # The outer fixture owns every synthetic path.
            method = 'test_one_approval_boundary_withholds_damage_without_waiving_a_rewriter'
            case = type(self)(method)
            result = unittest.TestResult()
            with mock.patch.object(tempfile, 'TemporaryDirectory', return_value=Factory()):
                case.run(result)
            self.assertEqual(1, result.testsRun)
            self.assertEqual([], result.failures)
            self.assertEqual([], result.errors)

    def test_historical_access_preserves_an_existing_claim_finding(self):
        import research_ledger as ledger
        source = '## CLAIM: Synthetic condition claim.\nSTATUS: invented\nNOTE: unrelated\x07\n'
        self.path.write_bytes(source.encode('utf-8'))
        token = completion_checks.MOMENTS.set({
            'approval': datetime(2026, 10, 20, 10, 59, 36, 999999, tzinfo=timezone.utc)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        checked = records.read_handwritten_record(self.path)
        self.assertEqual(source, checked.text)
        scan = ledger.survey(ledger.read_records(checked.text), datetime(2026, 10, 20).date())
        self.assertGreater(dict(scan.counts)[ledger.UNKNOWN_STATUS], 0)
        self.assertGreater(scan.failing_records, 0)
        with self.assertRaises(records.DamagedRecord):
            checked.require_text(force=True)

    def test_each_item_uses_its_own_approval_and_unknown_items_are_current(self):
        boundary = datetime(2026, 10, 20, 10, 59, 37, tzinfo=timezone.utc)
        self.path.write_bytes(b'FIELD: damaged\x07\n')
        token = completion_checks.MOMENTS.set({'approval': boundary - timedelta(microseconds=1)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        token = completion_checks.ITEM_MOMENTS.set({
            'older': boundary - timedelta(microseconds=1),
            'current': boundary,
        })
        self.addCleanup(completion_checks.ITEM_MOMENTS.reset, token)
        checked = records.read_handwritten_record(self.path)
        self.assertIn('\x07', checked.require_text(artifact='older'))
        for key in ('current', 'unknown'):
            with self.subTest(key=key), self.assertRaises(records.DamagedRecord):
                checked.require_text(artifact=key)

    def test_unknown_key_cannot_inherit_an_older_global_moment_when_item_map_is_empty(self):
        self.path.write_bytes(b'FIELD: damaged\x07\n')
        token = completion_checks.MOMENTS.set({
            'approval': datetime(2026, 10, 20, 10, 59, 36, tzinfo=timezone.utc)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        token = completion_checks.ITEM_MOMENTS.set({})
        self.addCleanup(completion_checks.ITEM_MOMENTS.reset, token)
        checked = records.read_handwritten_record(self.path)
        self.assertIn('\x07', checked.text)  # A nonkeyed historical reader retains its old view.
        with self.assertRaises(records.DamagedRecord):
            checked.require_text(artifact='unknown')

    def test_historical_crlf_keeps_the_previous_text_reader_and_claim_outcome(self):
        import research_ledger as ledger
        self.path.write_bytes(b'## CLAIM: Synthetic condition claim.\r\nSTATUS: invented\r\nNOTE: unrelated\x07\r\n')
        token = completion_checks.MOMENTS.set({
            'approval': datetime(2026, 10, 20, 10, 59, 36, tzinfo=timezone.utc)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        checked = records.read_handwritten_record(self.path)
        self.assertEqual('## CLAIM: Synthetic condition claim.\nSTATUS: invented\nNOTE: unrelated\x07\n', checked.text)
        scan = ledger.survey(ledger.read_records(checked.text), datetime(2026, 10, 20).date())
        self.assertGreater(dict(scan.counts)[ledger.UNKNOWN_STATUS], 0)
        self.assertGreater(scan.failing_records, 0)

    def test_existing_context_raw_damage_refuses_before_the_new_approval_boundary(self):
        import project_context
        import project_context_test_support as context_fixtures
        context_fixtures.write_none_context(self.path.parent)
        original = self.path.read_bytes() + b'\x0c'
        self.path.write_bytes(original)
        token = completion_checks.MOMENTS.set({
            'approval': datetime(2026, 10, 20, 10, 59, 36, tzinfo=timezone.utc)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        result = project_context.write_record(self.path.parent)
        self.assertEqual(1, result.exit_code)
        self.assertIn('U+000C', result.report)
        self.assertEqual(original, self.path.read_bytes())

    def test_raw_and_decoded_damage_are_both_reported_without_private_key_or_value_echo(self):
        kind = records.HandwrittenKind('mixed', lambda text: (('private-prefix', text.split('\n')[1]),))
        self.path.write_bytes(b'TITLE: \x07\n{"private-key":"\\u0000private-value"}\n')
        result = records.read_handwritten_record(self.path, kind)
        self.assertTrue(result.raw_damage)
        self.assertEqual(('project-context.md: line 1: U+0007',
                          'project-context.md: body[1].field[1]: U+0000'), result.diagnostics)
        with self.assertRaises(records.DamagedRecord) as caught:
            result.require_text()
        self.assertNotIn('private-', str(caught.exception))

    def test_all_json_occurrences_are_checked_without_changing_duplicate_key_semantics(self):
        self.path.write_bytes(br'{"field":"\u0000","field":"safe"}')
        checked = records.read_handwritten_record(self.path, 'json')
        self.assertEqual(('project-context.md: field[1]: U+0000',), checked.diagnostics)
        with self.assertRaises(records.DamagedRecord):
            _ = checked.json
        token = completion_checks.MOMENTS.set({
            'approval': datetime(2026, 10, 20, 10, 59, 36, tzinfo=timezone.utc)})
        self.addCleanup(completion_checks.MOMENTS.reset, token)
        self.assertEqual({'field': 'safe'}, checked.json)

    def test_locked_mixed_decode_keeps_content_damage_distinct_and_writes_nothing(self):
        self.path.write_bytes(br'{"payload":"\u0000"}')
        before = self.path.read_bytes()
        def decode(text):
            return records.check_handwritten_text(text, self.path, 'json').require_json(force=True)
        with self.assertRaises(records.DamagedRecord) as caught:
            records.update_tool_record(self.path, decode, lambda previous: records.RecordUpdate(b'{}'))
        self.assertNotIsInstance(caught.exception, records.UnreadableRecord)
        self.assertEqual(before, self.path.read_bytes())
        self.path.write_bytes(b'{')
        with self.assertRaises(records.UnreadableRecord):
            records.read_tool_record(self.path, records.object_record)

    def test_open_and_json_errors_retain_the_callers_existing_error_types(self):
        with self.assertRaises(FileNotFoundError):
            records.read_handwritten_record(self.path)
        self.path.write_bytes(b'\xff')
        with self.assertRaises(UnicodeDecodeError):
            records.read_handwritten_record(self.path)
        self.path.write_bytes(b'{')
        with self.assertRaises(json.JSONDecodeError):
            _ = records.read_handwritten_record(self.path, 'json').json
        with self.assertRaises(OSError):
            records.read_handwritten_record(self.path.parent)
