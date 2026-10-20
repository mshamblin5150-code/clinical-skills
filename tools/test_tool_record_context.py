"""Synthetic public controls for ADR0422's context and voice identity readers."""
# phi-scan: synthetic
import contextlib
import io
import tempfile
from pathlib import Path
import unittest
import artifact_lock_test_support

import project_context
import voice_model_identity
from run_record_reader import UnreadableRecord, capture_errors


class ToolRecords(unittest.TestCase):
    def test_context_faults_are_coverage_and_writers_preserve_the_original(self):
        for content in (b'GO-AHEAD: {', b'ORDER-OBSERVATION: []\n', b'\xff',
                        b'ORDER-OBSERVATION: {"submission":{"paths":[]},"submission":{"paths":[]}}\n'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                path = run / project_context.RECORD_NAME
                path.write_bytes(content)
                with capture_errors() as faults:
                    result = project_context.completion_gate(run, 'submission')
                    self.assertFalse(result.finding, result.report)
                    self.assertTrue(result.coverage, result.report)
                    self.assertIn('not graded', result.report)
                self.assertEqual(1, len(faults))
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    status = project_context.main([str(run), '--write', '--submission', 'submission'])
                self.assertEqual(2, status, output.getvalue())
                self.assertIn('project-context.md: unreadable', output.getvalue())
                self.assertEqual(content, path.read_bytes())
                for reader in (project_context.recorded_opened_items, project_context.recorded_digest,
                               project_context.order_observations, project_context.retain_heading_context):
                    with self.assertRaises(UnreadableRecord):
                        reader(run)

    def test_voice_faults_are_coverage_and_writers_preserve_the_original(self):
        for content in (b'{', b'[]', b'{"observations": []}', b'\xff',
                        b'{"path":"model.md","exists":false,"sha256":null,"observations":{"submission":{"paths":[]},"submission":{"paths":[]}}}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                path = run / voice_model_identity.RECORD_NAME
                path.write_bytes(content)
                with capture_errors() as faults:
                    result = voice_model_identity.completion_gate(run, 'submission')
                    self.assertFalse(result.finding, result.report)
                    self.assertTrue(result.coverage, result.report)
                    self.assertIn('draft order: not graded', result.report)
                self.assertEqual(1, len(faults))
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    status = voice_model_identity.main([str(run), '--write', '--submission', 'submission'])
                self.assertEqual(2, status, output.getvalue())
                self.assertIn('voice-model-identity.json: unreadable', output.getvalue())
                self.assertEqual(content, path.read_bytes())

    def test_unopenable_paths_are_not_missing_and_no_writer_replaces_them(self):
        for module in (project_context, voice_model_identity):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                path = run / module.RECORD_NAME
                path.mkdir()
                result = module.completion_gate(run, 'submission')
                self.assertFalse(result.finding, result.report)
                self.assertTrue(result.coverage, result.report)
                self.assertIn('could not be opened', result.report)
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    status = module.main([str(run), '--write', '--submission', 'submission'])
                self.assertEqual(2, status)
                self.assertTrue(path.is_dir())
                self.assertEqual([], list(path.iterdir()))

    def test_context_control_damage_precedes_broken_tool_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            path = run / project_context.RECORD_NAME
            content = b'GO-AHEAD: {\x07\n'
            path.write_bytes(content)
            result = project_context.completion_gate(run, 'submission')
            self.assertTrue(result.finding, result.report)
            self.assertFalse(result.coverage, result.report)
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                status = project_context.main([str(run), '--write', '--submission', 'submission'])
            self.assertEqual(1, status, output.getvalue())
            self.assertIn('U+0007', output.getvalue())
            self.assertEqual(content, path.read_bytes())
