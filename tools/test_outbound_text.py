"""ADR 0421 public-builder and pre-upload damage controls; synthetic only."""
# phi-scan: synthetic
import contextlib
from dataclasses import asdict, replace
from datetime import timedelta
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support
import mechanics_test_support

setUpModule, tearDownModule = mechanics_test_support.module_hooks()

import assignment_docx
import completion_checks
import docx_write
import entry_copy
import post_html
import post_text
import run_record_reader as shared
from test_deck_scan import Run as DeckRun, slide_xml, notes_xml, relationships_xml
from test_discussion_post_scan import Run as PostRun

ROOT = Path(__file__).resolve().parent
DAMAGE = ('\t', '\x07', '\x00', '\x0c', '\x0b', '\r', '\x1b', '\x7f', '\x85')
NOTE = ('S:\nSafe words.\nO:\nNormal.\nA:\nSymptom.\nP:\n'
        'Non-pharmacologic:\nPharmacologic:\n'
        'Health Promotion/Patient Education:\nReferral/Follow-up:\n')


class Builders(unittest.TestCase):
    def test_each_public_builder_refuses_each_character_before_transforming(self):
        for char in DAMAGE:
            text = f'SYNTHETIC-PRIVATE{char}words'
            spec = assignment_docx.fixture_spec()
            spec = replace(spec, title_page=replace(spec.title_page, author=text))
            for builder, value in ((entry_copy.derive, NOTE.replace('Safe words.', text)),
                                   (post_text.render, text), (post_html.render, text),
                                   (docx_write.parts, text), (assignment_docx.parts, spec)):
                with self.subTest(builder=builder.__module__, code=ord(char)):
                    with self.assertRaises(shared.OutboundTextError) as refusal:
                        builder(value)
                    self.assertIn(f'U+{ord(char):04X}', str(refusal.exception))
                    self.assertIn('line ', str(refusal.exception))
                    self.assertNotIn('SYNTHETIC-PRIVATE', str(refusal.exception))

    def test_each_command_preserves_bare_cr_until_the_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for char in DAMAGE:
                text = f'SYNTHETIC-PRIVATE{char}words'
                source = run / 'source.md'
                source.write_bytes(NOTE.replace('Safe words.', text).encode('utf-8'))
                mapping = asdict(assignment_docx.fixture_spec())
                mapping['title_page']['author'] = text
                json_source = run / 'assignment.json'
                json_source.write_text(json.dumps(mapping), encoding='utf-8')
                commands = (
                    ('entry_copy.py', (str(source),), run / 'entry-copies/source.md'),
                    ('post_text.py', (str(source), str(run / 'post.txt')), run / 'post.txt'),
                    ('post_html.py', (str(source), str(run / 'post.html')), run / 'post.html'),
                    ('docx_write.py', (str(source), str(run / 'post.docx')), run / 'post.docx'),
                    ('assignment_docx.py', (str(json_source), str(run / 'rich.docx')), run / 'rich.docx'),
                )
                for tool, args, target in commands:
                    with self.subTest(tool=tool, code=ord(char)):
                        result = subprocess.run([sys.executable, str(ROOT / tool), *args],
                                                capture_output=True, encoding='utf-8', errors='replace')
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn(f'U+{ord(char):04X}', result.stderr)
                        self.assertNotIn('SYNTHETIC-PRIVATE', result.stderr)
                        self.assertFalse(target.exists())

    def test_windows_line_endings_are_a_clean_control(self):
        shared.require_outbound_text('a\r\nb\r\n')
        self.assertEqual(post_html.render('a\nb\n'), post_html.render('a\r\nb\r\n'))
        self.assertEqual(post_text.render('a\nb\n'), post_text.render('a\r\nb\r\n'))
        self.assertEqual(docx_write.parts('a\nb\n'), docx_write.parts('a\r\nb\r\n'))
        self.assertTrue(entry_copy.derive(NOTE.replace('\n', '\r\n')))

    def test_named_prior_damage_symptoms_refuse_before_the_old_parser(self):
        for builder in (entry_copy.derive, entry_copy.check):
            with self.assertRaisesRegex(shared.OutboundTextError, 'line 2: U\\+000B'):
                builder(NOTE.replace('Safe words.', 'Subjective words.\x0bO:\x0bmore.'))
        with self.assertRaisesRegex(shared.OutboundTextError, 'U\\+000C'):
            post_html.render('https://example.invalid/a\x0cb')
        for builder in (post_html.render, docx_write.parts):
            with self.assertRaisesRegex(shared.OutboundTextError, 'U\\+000B'):
                builder('a\x0bb')

    def test_assignment_checks_title_credentials_figure_and_docprops_text(self):
        clean = assignment_docx.fixture_spec()
        for spec in (replace(clean, title_page=replace(clean.title_page, title='a\tb')),
                     replace(clean, title_page=replace(clean.title_page, credentials='a\tb')),
                     replace(clean, figure_alt_text='a\tb'), replace(clean, figure_note='a\tb')):
            with self.assertRaisesRegex(shared.OutboundTextError, 'U\\+0009'):
                assignment_docx.parts(spec)


class GraderBoundaries(unittest.TestCase):
    def test_raw_slide_and_speaker_note_edges_are_checked_before_strip(self):
        for char in ('\t', '\x7f', '\x85', '&#13;', 'words&#13;'):
            for notes in (False, True):
                with self.subTest(char=char, notes=notes), tempfile.TemporaryDirectory() as directory:
                    run = DeckRun(Path(directory))
                    run.write_deck((slide_xml('Synthetic', 'Safe words'),))
                    _status, report, error = run.grade('--paper-language', 'en')
                    self.assertIn('outbound-text: 0', report, error)
                    run.write_deck((slide_xml('Synthetic', 'Safe words' if notes else char + 'words'),),
                                   notes=(notes_xml(char + 'words'),) if notes else (),
                                   parts={'ppt/slides/_rels/slide1.xml.rels': relationships_xml(
                                       ('rIdNotes', 'notesSlide', '../notesSlides/notesSlide1.xml'))} if notes else {})
                    status, report, error = run.grade('--paper-language', 'en')
                    self.assertEqual(1, status, report + error)
                    self.assertIn('outbound-text: 1', report)
                    self.assertIn('outbound text: slide 1: line ', report)

    def test_note_part_number_does_not_invent_its_owning_slide(self):
        with tempfile.TemporaryDirectory() as directory:
            run = DeckRun(Path(directory))
            run.write_deck((slide_xml('First', 'Safe'), slide_xml('Second', 'Safe')),
                           parts={'ppt/notesSlides/notesSlide7.xml': notes_xml('\twords'),
                                  'ppt/slides/_rels/slide2.xml.rels': relationships_xml(
                                      ('rIdNotes', 'notesSlide', '../notesSlides/notesSlide7.xml'))})
            status, report, error = run.grade('--paper-language', 'en')
            self.assertEqual(1, status, report + error)
            self.assertIn('outbound text: slide 2: line 1: U+0009', report)
            self.assertNotIn('outbound text: slide 7:', report)
            run.write_deck((slide_xml('First', 'Safe'),), notes=(notes_xml('\twords'),))
            status, report, error = run.grade('--paper-language', 'en')
            self.assertEqual(1, status, report + error)
            self.assertIn('outbound text: unassociated speaker note: line 1: U+0009', report)

    def test_initial_post_reports_damage_as_a_finding_even_without_a_carrier(self):
        with tempfile.TemporaryDirectory() as directory:
            run = PostRun(Path(directory))
            self.assertEqual(0, run.grade('--paper-language', 'en')[0])
            run.draft.write_bytes(run.draft.read_bytes() + b'\nSYNTHETIC-PRIVATE\rwords\n')
            status, report, error = run.grade('--paper-language', 'en')
            self.assertEqual(1, status, report + error)
            self.assertIn('outbound-text: 1', report)
            self.assertNotIn('SYNTHETIC-PRIVATE', report + error)

    def test_handwritten_damage_keeps_outbound_findings_and_withholds_only_its_joins(self):
        for kind in ('deck', 'post'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run = DeckRun(root) if kind == 'deck' else PostRun(root)
                if kind == 'deck':
                    run.write_deck((slide_xml('Synthetic', '\x7fwords'),))
                else:
                    run.draft.write_bytes(run.draft.read_bytes() + b'\n\x7fwords\n')
                records = (root / 'bar.md', root / 'claims.md')
                for path, damage in zip(records, (b'\x07', b'\x0b')):
                    path.write_bytes(path.read_bytes() + b'\nDETAIL: damaged' + damage + b'text\n')
                before = tuple(path.read_bytes() for path in records)
                # The post must not rebuild its damaged outbound source, but
                # must still preserve all handwritten dependency withholding.
                with mock.patch('discussion_post_scan._editor_readback_result',
                                side_effect=AssertionError('damaged source rebuilt')):
                    status, report, error = run.grade('--paper-language', 'en', '--show')
                self.assertEqual(1, status, report + error)
                self.assertIn('outbound-text: 1', report)
                self.assertIn('U+007F', report)
                self.assertIn('U+0007', report)
                self.assertIn('U+000B', report)
                self.assertIn('not graded — damaged text', report)
                self.assertNotIn('run not scanned', report + error)
                self.assertEqual(before, tuple(path.read_bytes() for path in records))

    def test_completion_policy_changes_at_its_recorded_approval_boundary(self):
        for key in ('checks_ledger:outbound-text', 'discussion_post_scan:outbound-text',
                    'peer_critique_scan:outbound-text'):
            start, _ = completion_checks.registry()[key]
            guarded = shared.outbound_completion(lambda: completion_checks.active(key))(post_html.render)
            for moment, refused in ((start - timedelta(microseconds=1), False), (start, True)):
                token = completion_checks.MOMENTS.set({'approval': moment})
                try:
                    if refused:
                        with self.assertRaises(shared.OutboundTextError):
                            guarded('a\x0bb')
                    else:
                        self.assertEqual(post_html.render('ab'), guarded('a\x0bb'))
                    with self.assertRaises(shared.OutboundTextError):
                        post_html.render('a\x0bb')
                finally:
                    completion_checks.MOMENTS.reset(token)
