"""Synthetic host boundary controls for ADR 0395.

phi-scan: synthetic
"""
import artifact_lock_test_support
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest
import re

import project_context
import run_grader
import run_record_reader as records
import test_deck_scan as deck_fixture
import test_assignment_docx_scan as docx_fixture
import test_project_context as context_fixture
import test_discussion_reply_scan as reply_fixture
import discussion_reply_scan
import assignment_docx_scan
import repo_root
import assignment_bar
import bar_signatures
import test_bar_signatures as signature_fixture
import test_checks_ledger as checks_fixture
import checks_ledger
import approval_record
import assignment_submission
import frozen_grade
import course_assignment_scan
import anchor_scan
import completion_checks
from datetime import timedelta
from unittest import mock


class HandwrittenHosts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)

    def test_canonical_signer_forces_content_refusal_for_every_skill_before_mutation(self):
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        for skill in bar_signatures.SKILLS:
            with self.subTest(skill=skill):
                root = self.run / skill
                root.mkdir()
                text = deck_fixture.BAR if skill == 'course-assignment' else (
                    'SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n')
                if skill == 'discussion-post':
                    text += 'TOPIC: Synthetic\nSYLLABUS: Synthetic\nWORD-FLOOR: 100\nWORD-CEILING: none\nREFERENCE-MINIMUM: 1\n'
                if skill == 'practicum-case-study':
                    text += 'SUBMISSION-TYPE: file-upload\nRequired: synthetic assessment.\n'
                signature_fixture.SharedBarSigning().sign(root, skill, text)
                bar = root / 'bar.md'
                # The locked same-byte consumer must not normalize retained CRLF.
                if skill != 'course-assignment':
                    self.assertIn(b'\r\n', bar.read_bytes())
                bar.write_bytes(bar.read_bytes() + b'DETAIL: damaged\x07text\n')
                paths = (bar, root / bar_signatures.RECORD, root / 'signed-bars/bar-1.md')
                before = tuple(path.read_bytes() for path in paths)
                token = completion_checks.MOMENTS.set({'approval': start - timedelta(microseconds=1)})
                try:
                    output = io.StringIO()
                    with redirect_stdout(output):
                        status = bar_signatures.main([str(root), '--skill', skill, '--reply', 'yes'])
                    self.assertEqual(1, status, output.getvalue())
                    self.assertIn('U+0007', output.getvalue())
                    self.assertEqual(before, tuple(path.read_bytes() for path in paths))
                    self.assertFalse((root / 'signed-bars/bar-2.md').exists())
                finally:
                    completion_checks.MOMENTS.reset(token)

    def test_damaged_bar_and_history_keep_distinct_record_populations(self):
        signature_fixture.SharedBarSigning().sign(self.run, 'peer-critique',
            'SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n')
        bar = self.run / 'bar.md'
        bar.write_bytes(bar.read_bytes() + b'DETAIL: bad\x07text\n')
        history = self.run / bar_signatures.RECORD
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        token = completion_checks.MOMENTS.set({'approval': old})
        item = completion_checks.ITEM_MOMENTS.set({'old': old, 'exact': start})
        try:
            for key in ('old', 'exact', 'unknown'):
                finding, report = bar_signatures.completion_gate(self.run, skill='peer-critique', artifact=key)
                self.assertTrue(finding, report)
                self.assertEqual(key != 'old', 'U+0007' in report)
                if key == 'old':
                    self.assertIn('does not match its latest signature', report)
        finally:
            completion_checks.ITEM_MOMENTS.reset(item)
            completion_checks.MOMENTS.reset(token)
        for damaged_history in (False, True):
            with self.subTest(damaged_history=damaged_history):
                if damaged_history:
                    history.write_bytes(b'{')
                def grade():
                    finding, report = bar_signatures.completion_gate(self.run, skill='peer-critique')
                    print(report)
                    return 1 if finding else 0
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(1, run_grader.collect_record_errors(grade))
                self.assertIn('U+0007', output.getvalue())
                self.assertEqual(damaged_history, 'unread tool-written records 1' in output.getvalue())

    def test_native_walk_bar_damage_withholds_only_signature_join(self):
        first = signature_fixture.SharedBarSigning().sign(self.run, 'practicum-case-study',
            'SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\nSUBMISSION-TYPE: file-upload\n')
        walks = checks_fixture.PreReviewWalksThroughCommand().records()
        walks['routing-walk.json'] = {'entries': [], 'none': 'No synthetic routing subjects'}
        walks['bar-walk.json']['bar_sha256'] = first['sha256']
        for name, value in walks.items():
            (self.run / name).write_text(json.dumps(value), encoding='utf-8')
        checks = self.run / 'checks.md'
        checks.write_text('FIRST-DRAFT: 2099-01-01T00:00:00Z\n', encoding='utf-8')
        bar = self.run / 'bar.md'
        bar.write_bytes(bar.read_bytes() + b'DETAIL: bad\x07text\n')
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        token = completion_checks.MOMENTS.set({'approval': old})
        item = completion_checks.ITEM_MOMENTS.set({'old': old})
        try:
            with records.capture_handwritten_damage():
                findings = checks_ledger.pre_review_walks(self.run, checks.read_text(encoding='utf-8'), artifact='unknown')
                self.assertFalse(findings)
                self.assertIsNotNone(records.handwritten_record_damage(bar))
        finally:
            completion_checks.ITEM_MOMENTS.reset(item)
            completion_checks.MOMENTS.reset(token)
        for independent_fault in (False, True):
            with self.subTest(independent_fault=independent_fault):
                if independent_fault:
                    walks['bar-walk.json']['entries'][0]['outcome'] = 'invented'
                    (self.run / 'bar-walk.json').write_text(json.dumps(walks['bar-walk.json']), encoding='utf-8')
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(1, checks_ledger.main([str(checks), '--walks-only', '--show']))
                self.assertIn('U+0007', output.getvalue())
                self.assertEqual(independent_fault, 'missing or malformed pre-review walk' in output.getvalue())

    def test_native_damaged_bars_do_not_hide_sibling_damage_or_docx_package_checks(self):
        import zipfile
        from xml.etree import ElementTree
        for kind in ('deck', 'docx'):
            with self.subTest(kind=kind):
                root = self.run / kind
                root.mkdir()
                if kind == 'deck':
                    fixture = deck_fixture.Run(root)
                    fixture.write_deck((deck_fixture.slide_xml('Plan', 'Plain synthetic text', points=99),))
                    artifact = fixture.deck
                    direct = lambda: fixture.grade('--show', '--paper-language', 'en')[:2]
                    run = root
                else:
                    fixture = docx_fixture.empty_population_input(root)
                    run = Path(fixture.argv[0])
                    artifact = Path(fixture.argv[2])
                    with zipfile.ZipFile(artifact) as archive:
                        parts = {name: archive.read(name) for name in archive.namelist()}
                    core = ElementTree.fromstring(parts['docProps/core.xml'])
                    core.find(assignment_docx_scan.DC + 'title').text = ''
                    parts['docProps/core.xml'] = ElementTree.tostring(core)
                    with zipfile.ZipFile(artifact, 'w') as archive:
                        for name, value in parts.items():
                            archive.writestr(name, value)
                    def direct():
                        output = io.StringIO()
                        with redirect_stdout(output):
                            status = assignment_docx_scan.main([*fixture.argv, '--show', '--paper-language', 'en'])
                        return status, output.getvalue()
                bar = run / 'bar.md'
                claims = run / 'claims.md'
                bar.write_bytes(bar.read_bytes() + b'\nDETAIL: bad\x07text\n')
                claims.write_bytes(claims.read_bytes() + b'\nDETAIL: bad\x0btext\n')
                for operation in (direct, lambda: self._assignment_dispatch(run, artifact)):
                    status, report = operation()
                    self.assertEqual(1, status, report)
                    self.assertIn('U+0007', report)
                    self.assertIn('U+000B', report)
                    self.assertNotIn('run not scanned', report)
                    self.assertIn('not graded — damaged text', report)
                    if kind == 'deck':
                        self.assertIn('font-points: not graded — damaged text', report)
                    else:
                        self.assertIn('package-structure: 1', report)

    def _assignment_dispatch(self, run, artifact):
        output = io.StringIO()
        with redirect_stdout(output):
            status = course_assignment_scan.main([str(run), '--artifact', str(artifact), '--show', '--paper-language', 'en'])
        return status, output.getvalue()

    def test_both_prepare_entrypoints_refuse_context_formfeed_before_receipts(self):
        context = self.run / 'project-context.md'
        before = b'PROJECT-CONTEXT: none - synthetic\nDETAIL: bad\x0ctext\n'
        context.write_bytes(before)
        artifact = self.run / 'synthetic.docx'
        artifact.write_bytes(b'synthetic source')
        with mock.patch.object(approval_record, '_pre_post_grade', return_value=(0, 'clean')), \
             mock.patch.object(assignment_submission, '_require_signed_bar'), \
             mock.patch.object(assignment_submission, '_pre_upload_grade', return_value=(True, 'clean')), \
             mock.patch('reader_remarks.prepare') as retain:
            operations = (
                lambda: approval_record.prepare(self.run, skill='discussion-post', submission='synthetic',
                    sources=(artifact,), grader_args=(str(self.run),)),
                lambda: assignment_submission.prepare(self.run, artifact),
            )
            for operation in operations:
                with self.assertRaises(records.DamagedRecord) as caught:
                    operation()
                self.assertIn('U+000C', str(caught.exception))
                self.assertEqual(before, context.read_bytes())
            retain.assert_not_called()
        self.assertFalse((self.run / approval_record.RECORD).exists())
        self.assertFalse((self.run / assignment_submission.RECORD).exists())

    def test_native_docx_damage_withholds_only_dependent_rows(self):
        for filename, row in (('claims.md', 'claim-ledger'),
                              ('heading-read.md', 'missing-heading-read'),
                              ('rendered.md', 'rendered-record')):
            with self.subTest(filename=filename):
                root = self.run / filename.replace('.', '-')
                root.mkdir()
                fixture = docx_fixture.empty_population_input(root)
                run = Path(fixture.argv[0])
                bar = run / 'bar.md'
                bar.write_text(bar.read_text(encoding='utf-8').replace(
                    'WORD-MIN: 1\nWORD-MAX: 200', 'WORD-MIN: 1000\nWORD-MAX: 2000'), encoding='utf-8')
                path = run / filename
                before = path.read_bytes() + b'\nDETAIL: damaged\x07text\n'
                path.write_bytes(before)
                output = io.StringIO()
                with redirect_stdout(output):
                    status = assignment_docx_scan.main([*fixture.argv, '--paper-language', 'en'])
                report = output.getvalue()
                self.assertEqual(1, status, report)
                self.assertIn('word-range: 1', report)
                self.assertIn(row + ': not graded — damaged text', report)
                self.assertIn('unread remainder 0', report)
                self.assertEqual(before, path.read_bytes())

    def test_scoped_agreement_damage_does_not_waive_another_missing_pair(self):
        directory = self.run / 'agreement-self'
        directory.mkdir()
        damaged = directory / 'alpha.json'
        damaged.write_bytes(b'{"pairs": [], "detail":"bad\\u0007text"}')
        clean = directory / 'beta.json'
        clean.write_bytes(b'{"pairs":[{"stem":"beta","codes":[]}]}')
        pairs = [anchor_scan.AgreementPair(stem, '', '', (), 0)
                 for stem in ('alpha', 'beta', 'gamma')]
        result = anchor_scan._grade_agreement(pairs, 0, [damaged, clean])
        self.assertEqual(1, result.unread)
        self.assertIn('U+0007', '\n'.join(result.damage_reports))
        generic = self.run / 'read.json'
        generic.write_bytes(damaged.read_bytes())
        result = anchor_scan._grade_agreement(pairs, 0, [generic, clean])
        self.assertEqual(0, result.unread)

    def test_native_adoption_damage_refuses_without_publishing_a_freeze(self):
        reply_fixture.Run(self.run)
        reading = self.run / 'reread.md'
        reading.write_bytes(b'[]\x07')
        output = io.StringIO()
        with redirect_stdout(output):
            status = frozen_grade.main([str(self.run)])
        self.assertEqual(1, status, output.getvalue())
        self.assertIn('U+0007', output.getvalue())
        self.assertFalse((self.run / frozen_grade.RECORD).exists())

    def test_native_first_adoption_forces_damage_refusal_even_for_known_old_approval(self):
        reply_fixture.Run(self.run)
        reading = self.run / 'reread.md'
        reading.write_bytes(reading.read_bytes().replace(b'READ:', b'READ: bad\x07', 1))
        start, _ = completion_checks.registry()['run_record_reader:handwritten-damage']
        old = start - timedelta(microseconds=1)
        moment_token = completion_checks.MOMENTS.set({'approval': old})
        item_token = completion_checks.ITEM_MOMENTS.set({'response-maren.md': old})
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                status = frozen_grade.main([str(self.run)])
        finally:
            completion_checks.ITEM_MOMENTS.reset(item_token)
            completion_checks.MOMENTS.reset(moment_token)
        self.assertEqual(1, status, output.getvalue())
        self.assertIn('U+0007', output.getvalue())
        self.assertFalse((self.run / frozen_grade.RECORD).exists())

    def test_native_retained_freeze_bypasses_new_content_reads(self):
        reply_fixture.Run(self.run)
        key = 'response-maren.md'
        skill, item = frozen_grade.approved(self.run, key)
        frozen_grade.freeze(self.run, skill, item)
        before = (self.run / frozen_grade.RECORD).read_bytes()
        (self.run / 'reread.md').write_bytes(b'[]\x07')
        output = io.StringIO()
        with redirect_stdout(output):
            status = discussion_reply_scan.main([str(self.run), '--submission', key])
        self.assertEqual(0, status, output.getvalue())
        self.assertIn('frozen', output.getvalue())
        self.assertNotIn('U+0007', output.getvalue())
        self.assertEqual(before, (self.run / frozen_grade.RECORD).read_bytes())

    def test_native_reply_leading_blank_copy_keeps_metadata_tabs_refused(self):
        reply = reply_fixture.Run(self.run)
        path = self.run / 'posts' / 'maren-quill.md'
        original = path.read_text(encoding='utf-8')
        def grade(reply):
            output = io.StringIO()
            with redirect_stdout(output):
                status = discussion_reply_scan.main([str(reply.root), '--paper-language', 'en'])
            return status, output.getvalue(), ''
        path.write_text('\n' + original.replace('A synthetic', 'A\tsynthetic'), encoding='utf-8')
        status, report, error = grade(reply)
        self.assertEqual(0, status, report + error)
        path.write_text('\n' + original.replace('AUTHOR:', 'AUTHOR:\t'), encoding='utf-8')
        status, report, error = grade(reply)
        self.assertEqual(1, status, report + error)
        self.assertIn('U+0009', report)

    def test_native_signer_refuses_damaged_bar_before_any_publication(self):
        path = self.run / 'bar.md'
        before = (deck_fixture.BAR + '\nDETAIL: damaged\x0ctext\n').encode('utf-8')
        path.write_bytes(before)
        output = io.StringIO()
        with redirect_stdout(output):
            status = assignment_bar.main([str(self.run), '--reply', 'yes'])
        self.assertEqual(1, status)
        self.assertIn('U+000C', output.getvalue())
        self.assertEqual(before, path.read_bytes())
        self.assertFalse((self.run / assignment_bar.RECORD).exists())
        self.assertFalse((self.run / 'signed-bars').exists())

    def test_native_reply_registry_damage_does_not_hide_independent_draft_number(self):
        fixture = context_fixture.ProjectContextFixture()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        reply = reply_fixture.Run(fixture.run, posted=False)
        fixture.complete_record()
        self.assertEqual(0, fixture.write().exit_code)
        response = fixture.run / 'response-maren.md'
        response.write_text(response.read_text(encoding='utf-8').replace('12%', '17%'), encoding='utf-8')
        reply.write_heading_read()
        heading = fixture.run / 'heading-read.md'
        digest = project_context.recorded_digest(fixture.run)
        heading.write_text(heading.read_text(encoding='utf-8').replace(
            'e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf', digest), encoding='utf-8')
        fixture.registry.write_bytes(fixture.registry.read_bytes() + b'DETAIL: damaged\x07text\n')
        output = io.StringIO()
        with mock.patch.object(repo_root, 'project_registry', return_value=fixture.registry), redirect_stdout(output):
            status = discussion_reply_scan.main([str(fixture.run), '--submission', response.name, '--show'])
        self.assertEqual(1, status, output.getvalue())
        self.assertIn('untraced-number: 1', output.getvalue())
        self.assertIn('U+0007', output.getvalue())

    def test_native_deck_record_damage_preserves_independent_font_finding(self):
        for filename in ('claims.md', 'heading-read.md', 'rendered.md', 'adversarial.md', 'intent.md'):
            with self.subTest(filename=filename):
                root = self.run / filename.replace('.', '-')
                root.mkdir()
                fixture = deck_fixture.Run(root)
                fixture.write_deck((deck_fixture.slide_xml('Plan', 'Plain synthetic text', points=99),))
                _, clean, _ = fixture.grade('--show')
                path = root / filename
                before = path.read_bytes() + b'\nDETAIL: damaged\x07text\n'
                path.write_bytes(before)
                status, report, _ = fixture.grade('--show')
                self.assertEqual(1, status, report)
                self.assertIn('font-points: 1', report)
                self.assertIn('U+0007', report)
                self.assertNotIn('claims.md has no CLAIM', report)
                self.assertNotIn('rendered.md has no RENDERED', report)
                totals = lambda text: re.findall(r'(?m)^unread remainder (\d+)', text)
                self.assertEqual(totals(clean), totals(report))
                self.assertEqual(before, path.read_bytes())

    def test_context_decoded_damage_precedes_machine_shape_and_preserves_bytes(self):
        path = self.run / 'project-context.md'
        path.write_bytes(b'PROJECT-CONTEXT: none\nGO-AHEAD: {"submission":"bad\\u0000key"}\n')
        before = path.read_bytes()
        result = project_context.write_record(self.run)
        self.assertEqual(1, result.exit_code)
        self.assertIn('U+0000', result.report)
        self.assertNotIn('bad', result.report)
        self.assertEqual(before, path.read_bytes())

    def test_retained_context_damage_uses_actual_path_dependency(self):
        path = self.run / 'private' / 'heading-contexts' / ('a' * 64 + '.md')
        path.parent.mkdir(parents=True)
        path.write_bytes(b'DETAIL: bad\x07text\n')
        with records.capture_handwritten_damage():
            with self.assertRaises(records.DamagedRecord):
                project_context._read_context(path)
            self.assertIsNotNone(records.handwritten_record_damage(path))
            self.assertIsNone(records.handwritten_record_damage(self.run / 'project-context.md'))

    def test_retained_context_indented_mixedcase_json_damage_precedes_shape(self):
        path = self.run / 'private' / 'heading-contexts' / ('b' * 64 + '.md')
        path.parent.mkdir(parents=True)
        path.write_bytes(b'  Go-Ahead: {"submission":"bad\\u0000key"}\r\n')
        with records.capture_handwritten_damage():
            with self.assertRaises(records.DamagedRecord) as caught:
                project_context._read_context(path)
            self.assertIn('U+0000', str(caught.exception))
            self.assertIsNotNone(records.handwritten_record_damage(path))

    def test_local_damage_keeps_independent_host_result_and_tool_fault_population(self):
        path = self.run / 'hand.md'
        path.write_bytes(b'FIELD: bad\x07text\n')
        for original, tool in ((0, False), (1, False), (0, True)):
            with self.subTest(original=original, tool=tool):
                def grade():
                    try:
                        records.read_handwritten_record(path).text
                    except records.DamagedRecord as failure:
                        print(records.damaged_record_result(failure, check='handwritten check')[1])
                    print('independent checks reached')
                    if tool:
                        try:
                            raise records.UnreadableRecord(self.run / 'run-status.json', 'could not be opened')
                        except records.UnreadableRecord:
                            pass
                    return original
                output = io.StringIO()
                with redirect_stdout(output):
                    status = run_grader.collect_record_errors(grade)
                self.assertEqual(1, status)
                report = output.getvalue()
                self.assertIn('independent checks reached', report)
                self.assertEqual(1, report.count('U+0007'))
                self.assertEqual(tool, 'unread tool-written records 1' in report)
