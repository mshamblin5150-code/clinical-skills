"""Native context, identity and form-section writer transactions. Synthetic only."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import project_context as context
import voice_model_identity as identity
import form_sections
import repo_root
import run_record_reader as records
import coursework_run
import test_form_sections as form_tests
import project_context_test_support as context_tests


class ContextWriters(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name).resolve()
        resolved = repo_root.VoiceModelResolution(self.run / 'model.md', 'a' * 64, True)
        patch = mock.patch.object(repo_root, 'canonical_voice_model', return_value=resolved)
        patch.start()
        self.addCleanup(patch.stop)
        context_tests.write_none_context(self.run)
        self.assertEqual(0, context.write_record(self.run).exit_code)
        identity.write_record(self.run)
        supplied = coursework_run.voice_records_directory(self.run, 'response-first.md')
        supplied.mkdir(parents=True, exist_ok=True)
        (supplied / 'supplied-voice.json').write_text('{}', encoding='utf-8')
        self.copy = self.run / 'entry-copies/note-1.md'
        self.copy.parent.mkdir()
        self.copy.write_text(form_tests.NOTE, encoding='utf-8')
        with redirect_stdout(io.StringIO()):
            self.invoke_form()

    def invoke_form(self):
        return form_sections.main([str(self.copy), '--replace'])

    def test_machine_directory_failures_are_safe_and_preserve_evidence(self):
        canonical = self.run / context.RECORD_NAME
        digest = 'b' * 64
        canonical.write_text(canonical.read_text(encoding='utf-8').replace(
            'CONTEXT-DIGEST: ' + context.recorded_digest(self.run), 'CONTEXT-DIGEST: ' + digest), encoding='utf-8')
        retained = self.run / 'private/heading-contexts' / (digest + '.md')
        form = self.run / 'private/form-sections/note-1.json'
        original_mkdir = Path.mkdir
        for target, invoke in (
            (retained, lambda: context.retain_heading_context(self.run)),
            (retained, lambda: context.main([str(self.run), '--write', '--submission', 'response-first.md'])),
            (form, self.invoke_form),
        ):
            with self.subTest(target=target.name, invoke=invoke):
                before = canonical.read_bytes(), form.read_bytes()
                def denied(path, *args, **kwargs):
                    if path == target.parent:
                        raise OSError('PRIVATE-DIRECTORY-FAILURE')
                    return original_mkdir(path, *args, **kwargs)
                with mock.patch.object(Path, 'mkdir', denied), redirect_stdout(io.StringIO()) as out, redirect_stderr(out):
                    try:
                        status = invoke()
                    except records.UnreadableRecord as failure:
                        self.assertEqual(target, failure.path)
                        self.assertIn('could not be opened', str(failure))
                        self.assertNotIn('PRIVATE-DIRECTORY-FAILURE', str(failure))
                    else:
                        self.assertEqual(2, status, out.getvalue())
                        self.assertIn('unreadable — could not be opened', out.getvalue())
                    self.assertNotIn('PRIVATE-DIRECTORY-FAILURE', out.getvalue())
                self.assertEqual(before, (canonical.read_bytes(), form.read_bytes()))
                self.assertFalse(retained.exists())

    def writers(self):
        return (
            (self.run / context.RECORD_NAME, lambda: context.main([str(self.run), '--write', '--submission', 'response-first.md'])),
            (self.run / identity.RECORD_NAME, lambda: identity.main([str(self.run), '--write', '--submission', 'response-first.md'])),
            (self.run / 'private/form-sections/note-1.json', self.invoke_form),
            (self.run / context.RECORD_NAME, lambda: context.go_ahead(self.run, 'first')),
        )

    def test_each_native_writer_refuses_a_held_lock_and_preserves_old_bytes(self):
        for path, invoke in self.writers():
            with self.subTest(kind=path.name):
                before = path.read_bytes()
                with artifact_lock.hold(path, 'synthetic holder'), redirect_stdout(io.StringIO()) as out, redirect_stderr(out):
                    try:
                        result = invoke()
                    except records.UnreadableRecord as failure:
                        self.assertIn('held by another task', str(failure))
                    else:
                        self.assertEqual(2, result)
                        self.assertIn('unreadable — held by another task:', out.getvalue())
                self.assertEqual(before, path.read_bytes())

    def test_each_native_writer_preserves_old_bytes_before_failed_replace(self):
        for path, invoke in self.writers():
            with self.subTest(kind=path.name):
                before = path.read_bytes()
                with mock.patch.object(records.os, 'replace', side_effect=OSError('synthetic interruption')), redirect_stdout(io.StringIO()) as out, redirect_stderr(out):
                    try:
                        result = invoke()
                    except records.UnreadableRecord as failure:
                        self.assertIn('could not be opened', str(failure))
                    else:
                        self.assertEqual(2, result)
                        self.assertIn('unreadable — could not be opened', out.getvalue())
                self.assertEqual(before, path.read_bytes())

    def test_concurrent_identity_and_context_submission_observations_survive(self):
        keys = ('response-first.md', 'response-second.md')
        for key in keys:
            directory = coursework_run.voice_records_directory(self.run, key)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'supplied-voice.json').write_text('{}', encoding='utf-8')
        for writer, read in (
            (lambda key: identity.write_record(self.run, key),
             lambda: json.loads((self.run / identity.RECORD_NAME).read_text())['observations']),
            (lambda key: context.write_record(self.run, submission=key),
             lambda: context.order_observations(self.run)),
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(writer, keys))
            self.assertEqual(set(keys), set(read()))

    def test_concurrent_go_ahead_keys_survive(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda key: context.go_ahead(self.run, key), ('first', 'second')))
        self.assertEqual({'first', 'second'}, set(context._go_ahead_records(self.run)))

    def test_unreadable_first_draft_walk_writes_no_new_retained_context(self):
        directory = self.run / 'private/heading-contexts'
        for path in directory.glob('*.md'):
            path.unlink()
        before = (self.run / context.RECORD_NAME).read_bytes()
        with mock.patch.object(coursework_run, 'observe_draft', side_effect=coursework_run.DraftWalkUnreadable('synthetic unread walk')):
            result = context.write_record(self.run, submission='response-first.md')
        self.assertEqual(2, result.exit_code)
        self.assertEqual((self.run / context.RECORD_NAME).read_bytes(), before)
        self.assertFalse(list(directory.glob('*.md')))

    def test_retained_context_api_refuses_held_or_interrupted_first_publication(self):
        canonical = self.run / context.RECORD_NAME
        digest = 'b' * 64
        canonical.write_text(canonical.read_text(encoding='utf-8').replace(
            'CONTEXT-DIGEST: ' + context.recorded_digest(self.run), 'CONTEXT-DIGEST: ' + digest), encoding='utf-8')
        target = self.run / 'private/heading-contexts' / (digest + '.md')
        before = canonical.read_bytes()
        self.assertFalse(target.exists())
        with artifact_lock.hold(target, 'synthetic retained holder'):
            with self.assertRaisesRegex(records.UnreadableRecord, 'held by another task:'):
                context.retain_heading_context(self.run)
        self.assertFalse(target.exists())
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
                context.retain_heading_context(self.run)
        self.assertFalse(target.exists())
        self.assertEqual(canonical.read_bytes(), before)
