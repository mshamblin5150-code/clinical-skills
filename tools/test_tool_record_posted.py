"""Exercise damaged machine Markdown through each owning public grader command."""
# phi-scan: synthetic
import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
import re
from unittest import mock

import artifact_lock_test_support
import peer_critique_scan
import differential_scan
import filled_vitals_census
import test_checks_ledger as checks
import test_deck_scan as decks
import test_discussion_post_scan as posts
import test_discussion_reply_scan as replies
import test_peer_critique_scan as critiques
import test_assignment_docx_scan as word_papers
import project_context
import mechanics_test_support
import course_assignment_scan
import assignment_bar
import assignment_submission
import frozen_grade
import test_assignment_bar as bar_fixtures


def public_model_resolution():
    model = Path(__file__).parent / 'testdata' / 'voice-model-synthetic.md'
    return checks.checks.repo_root.VoiceModelResolution(
        model, hashlib.sha256(model.read_bytes()).hexdigest(), True,
    )


class PostedRecordCommands(unittest.TestCase):
    def check_faults(self, run, invoke):
        path = run / 'reread.md'
        original = path.read_bytes()
        for content, cause in ((original[:original.index(b'\n') + 1], 'wrong shape:'),
                               (b'[]', 'wrong shape:'), (None, 'could not be opened')):
            with self.subTest(content=content is None, cause=cause):
                path.unlink()
                if content is None:
                    path.mkdir()
                else:
                    path.write_bytes(content)
                frozen = run / 'frozen-grades.json'
                frozen.unlink(missing_ok=True)
                status, report, error = invoke()
                self.assertEqual(2, status, report + error)
                self.assertIn('reread.md: unreadable — ' + cause, report + error)
                self.assertIn('not graded', report)
                self.assertEqual(1, sum(line.startswith('unread remainder ') for line in report.splitlines()))
                self.assertIn('unread remainder 1', report)
                if content is None:
                    self.assertEqual([], list(path.iterdir()))
                    path.rmdir()
                else:
                    self.assertEqual(content, path.read_bytes())
                    path.unlink()
                path.write_bytes(original)

    def test_initial_post_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = posts.APostedInitialEntryHasItsOwnReading().posted_run(Path(directory))
            self.check_faults(run.root, run.grade)

    def test_reply_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = replies.Run(Path(directory))
            self.check_faults(run.root, lambda: replies.EveryPostedReplyHasALocatedReading().grade(run))

    def test_claim_heading_and_machine_faults_form_one_total_with_finding_precedence(self):
        for finding in (False, True):
            with self.subTest(finding=finding), tempfile.TemporaryDirectory() as directory:
                run = replies.Run(Path(directory))
                if finding:
                    response = run.root / 'response-maren.md'
                    response.write_text(replies.BODY.replace('12%', '17%', 1), encoding='utf-8')
                    run.write_heading_read()
                claims = run.root / 'claims.md'
                claims.write_text(claims.read_text(encoding='utf-8').replace(
                    '\nSTATUS: sourced', '\nUnknown claim-reader line.\nSTATUS: sourced', 1), encoding='utf-8')
                heading = run.root / 'heading-read.md'
                heading.write_text(heading.read_text(encoding='utf-8') + '\nUnknown heading-reader line.\n', encoding='utf-8')
                reading = run.root / 'reread.md'
                reading.write_bytes(b'[]')
                status, report, error = replies.EveryPostedReplyHasALocatedReading().grade(run)
                self.assertEqual(1 if finding else 2, status, report + error)
                self.assertEqual(['unread remainder 3'], [
                    line for line in report.splitlines() if line.startswith('unread remainder ')])
                self.assertIn('unread reader record: CLAIM:', report)
                self.assertIn('reread.md: unreadable', report)
                if finding:
                    self.assertIn('untraced-number', report)
                self.assertEqual(b'[]', reading.read_bytes())

    def test_peer_critique_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = critiques.build_run(root=Path(directory) / 'run')
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = peer_critique_scan.main([str(run)])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(run, invoke)

    def test_case_study_command(self):
        directory, path = checks.in_a_file(checks.whole_file())
        with directory:
            fixture = checks.ComposerAttachmentOutcome()
            fixture.prepare(path, 'inline')
            command = checks.checks
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with (
                    mock.patch.object(command.repo_root, 'canonical_voice_model', return_value=public_model_resolution()),
                    mock.patch.object(command.repo_root, 'output_root', return_value=path.parent / 'output'),
                    mock.patch.object(command.voice_read, 'apply_completion_gate', side_effect=lambda grade, *args, **kwargs: grade),
                    mock.patch.object(command.aar_scan, 'completion_gate', return_value=(False, 'the after-action review: clean')),
                    mock.patch.object(command.approval_record, 'completion_gate', return_value=(False, 'the approval record: clean')),
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err),
                ):
                    status = command.main([str(path), '--submission', 'case-study'])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(path.parent, invoke)

    def test_deck_command(self):
        with tempfile.TemporaryDirectory() as directory:
            run = decks.TheRenderedDeckRecordNamesTheTerminalPass().a_run(Path(directory))
            run.retain(1, 1)
            run.write_rendered()
            status, report, error = run.terminal()
            self.assertEqual(0, status, report + error)
            self.check_faults(run.root, lambda: run.terminal(bind=False))

    def test_both_clinical_submission_commands(self):
        from test_medatrax_readback_command import ReadbackCommand
        fixture = ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.run / 'note-3.md').write_text(
            'Start time 0800\nEnd time 0830\nDifferential:\n'
            '1. Cough - R05.9: most likely.\nFILLED·asserted BP 118/76 filled.\n', encoding='utf-8')
        (fixture.run / 'shift-values.json').write_text(
            '{"start":"0800","duration":{"hours":8,"minutes":0}}', encoding='utf-8')
        self.assertEqual(0, fixture.invoke('write'))
        for command in (differential_scan, filled_vitals_census):
            def invoke():
                out, err = io.StringIO(), io.StringIO()
                with (
                    mock.patch.object(command.aar_scan, 'completion_gate', return_value=(False, 'AAR: clean')),
                    mock.patch.object(command.artifact_repairs, 'completion_gate', return_value=(False, 'repairs: clean')),
                    mock.patch.object(command.delegated_answers, 'completion_gate', return_value=(False, 'answers: clean', 0)),
                    mock.patch.object(command.approval_record, 'completion_gate', return_value=(False, 'approval: clean')),
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err),
                ):
                    status = command.main([str(fixture.run), '--submission', 'shift'])
                return status, out.getvalue(), err.getvalue()
            self.check_faults(fixture.run, invoke)


class ContextDependentCommands(unittest.TestCase):
    def setUp(self):
        token = mechanics_test_support.begin()
        self.addCleanup(mechanics_test_support.end, token)

    @contextlib.contextmanager
    def damaged(self, path, content, heading, finding):
        original = path.read_bytes()
        saved_heading = heading.read_text(encoding='utf-8')
        if finding:
            heading.write_text(re.sub(r'(?m)^DRAFT: .*$', 'DRAFT: ' + '0' * 64,
                saved_heading), encoding='utf-8')
        path.unlink()
        if content is None:
            path.mkdir()
        else:
            path.write_bytes(content)
        try:
            yield
        finally:
            if content is None:
                path.rmdir()
            else:
                path.unlink()
            path.write_bytes(original)
            heading.write_text(saved_heading, encoding='utf-8')

    def command(self, module, arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = module.main(arguments)
        return status, out.getvalue(), err.getvalue()

    def dispatcher(self, run, arguments):
        with (mock.patch.object(course_assignment_scan.voice_model_identity.repo_root,
                                'canonical_voice_model', return_value=public_model_resolution()),
              mock.patch.object(decks.scan.aar_scan, 'completion_gate', return_value=(False, 'AAR: clean')),
              mock.patch.object(decks.scan.voice_read, 'apply_completion_gate', side_effect=lambda grade, *args, **kwargs: grade),
              mock.patch.object(assignment_submission.repo_root, 'output_root', return_value=run.root / 'canonical-output')):
            return self.command(course_assignment_scan, [*arguments, '--paper-language', 'en'])

    def exercise(self, root, heading, invoke):
        status, report, error = invoke()
        self.assertEqual(0, status, report + error)
        project_context.retain_heading_context(root)
        digest = project_context.recorded_digest(root)
        for path in (root / project_context.RECORD_NAME,
                     root / 'private' / 'heading-contexts' / (digest + '.md')):
            for content in (b'GO-AHEAD: {', b'ORDER-OBSERVATION: []\n', None):
                for finding in (False, True):
                    with self.subTest(record=path.name, directory=content is None, finding=finding), \
                            self.damaged(path, content, heading, finding):
                        status, report, error = invoke()
                        self.assertEqual(1 if finding else 2, status, report + error)
                        self.assertIn('heading-read context comparisons: not graded', report)
                        self.assertEqual(['unread remainder 1'], [line for line in report.splitlines()
                            if line.startswith('unread remainder ')])
                        self.assertNotRegex(report, r'heading-read-(?:context-digest|unopened-item):?\s+[1-9]')
                        if finding:
                            self.assertRegex(report, r'heading-read-draft-mismatch:?\s+1')
                        if content is None:
                            self.assertEqual([], list(path.iterdir()))
                        else:
                            self.assertEqual(content, path.read_bytes())

    def test_reply_context_faults_keep_independent_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            run = replies.Run(Path(directory), posted=False)
            (run.root / 'reread.md').unlink()
            self.exercise(run.root, run.root / 'heading-read.md',
                lambda: replies.EveryPostedReplyHasALocatedReading().grade(run))

    def test_initial_post_context_faults_keep_independent_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            run = posts.Run(Path(directory))
            self.exercise(run.root, run.root / 'heading-read.md',
                lambda: run.grade(bind_heading_read=False))

    def test_peer_context_faults_keep_independent_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = critiques.build_run(root=Path(directory) / 'run', posted=False)
            (root / 'reread.md').unlink()
            self.exercise(root, root / 'heading-read.md',
                lambda: self.command(peer_critique_scan, [str(root)]))

    def test_deck_context_faults_keep_independent_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            run = decks.TheRenderedDeckRecordNamesTheTerminalPass().a_run(Path(directory))
            run.grade()
            self.exercise(run.root, run.root / 'heading-read.md', lambda: run.grade(bind=False))

    def test_word_context_faults_keep_independent_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            case = word_papers.empty_population_input(Path(directory))
            root = Path(case.argv[0])
            claim = 'The example connects authority, coordination, and feedback.'
            (root / 'claims.md').write_text('DATE: 2026-09-13\n\n## CLAIM: ' + claim + '\n'
                'STATUS: sourced\nREFERENCE: Example Agency. (2025). *Systems coordination brief*. https://example.invalid/brief\n'
                'REFUTATION: stands - the source states this claim.\n'
                'SECOND-ROUTE: publisher HTML -> original source\n'
                'TESTED-HEADING: ' + word_papers.research_ledger.heading_digest(claim) + '\n', encoding='utf-8')
            self.exercise(root, root / 'heading-read.md',
                lambda: self.command(word_papers.scan, [*case.argv, '--paper-language', 'English']))

    def test_checks_context_faults_keep_independent_checks(self):
        directory, path = checks.in_a_file(checks.whole_file())
        with directory:
            checks.run([str(path)])
            arguments = [str(path), '--document', str(path.parent / 'draft.md')]
            self.exercise(path.parent, path, lambda: checks.run(arguments, bind=False))

    def test_dispatcher_machine_faults_keep_independent_artifact_checks(self):
        fixture = bar_fixtures.BarSignatures()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        run = decks.TheRenderedDeckRecordNamesTheTerminalPass().a_run(fixture.run)
        fixture.draft(decks.BAR)
        fixture.sign()
        status, report, error = run.terminal()
        self.assertEqual(0, status, report + error)
        frozen_grade.freeze(run.root, 'course-assignment',
            {**assignment_submission._read(run.root), 'submission': run.deck.stem})
        original_deck = run.deck.read_bytes()
        for name in (assignment_bar.RECORD, frozen_grade.RECORD):
            arguments = [str(run.root), '--artifact', str(run.deck)]
            if name == frozen_grade.RECORD:
                arguments += ['--submission', run.deck.stem]
            path = run.root / name
            original = path.read_bytes()
            for content in (b'{', b'[]', None):
                for finding in (False, True):
                    with self.subTest(record=name, directory=content is None, finding=finding):
                        if finding:
                            run.write_deck((decks.slide_xml('Plan', 'Unrecorded $19,500'),))
                        else:
                            run.deck.write_bytes(original_deck)
                            run.write_heading_read()
                        path.unlink()
                        if content is None:
                            path.mkdir()
                        else:
                            path.write_bytes(content)
                        try:
                            status, report, error = self.dispatcher(run, arguments)
                            self.assertEqual(1 if finding else 2, status, report + error)
                            self.assertIn('not graded', report)
                            self.assertEqual(['unread remainder 1'], [line for line in report.splitlines()
                                if line.startswith('unread remainder ')])
                            if finding:
                                self.assertIn('untraced-figure: 1', report)
                            if content is not None:
                                self.assertEqual(content, path.read_bytes())
                        finally:
                            path.rmdir() if content is None else path.unlink()
                            path.write_bytes(original)

    def test_dispatcher_keeps_valid_frozen_bypass_and_refuses_unreadable_bar_only(self):
        fixture = bar_fixtures.BarSignatures()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        run = decks.TheRenderedDeckRecordNamesTheTerminalPass().a_run(fixture.run)
        fixture.draft(decks.BAR)
        fixture.sign()
        status, report, error = run.terminal()
        self.assertEqual(0, status, report + error)
        frozen_grade.freeze(run.root, 'course-assignment',
            {**assignment_submission._read(run.root), 'submission': run.deck.stem})
        with mock.patch.object(course_assignment_scan, '_import_adapter') as adapter:
            status, report, error = self.command(course_assignment_scan,
                [str(run.root), '--artifact', str(run.deck), '--submission', run.deck.stem])
        self.assertEqual(0, status, report + error)
        adapter.assert_not_called()
        (run.root / assignment_bar.RECORD).write_bytes(b'{')
        status, report, error = self.command(course_assignment_scan, [str(run.root), '--bar-only'])
        self.assertEqual(2, status, report + error)
        self.assertIn('not graded', report)
        self.assertNotIn('assignment bar: clean', report)
        self.assertEqual(b'{', (run.root / assignment_bar.RECORD).read_bytes())


if __name__ == '__main__':
    unittest.main()
