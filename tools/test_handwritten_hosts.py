"""Synthetic host boundary controls for ADR 0395.

phi-scan: synthetic
"""
import artifact_lock_test_support
from contextlib import redirect_stdout
import io
import tempfile
from pathlib import Path
import unittest

import project_context
import run_grader
import run_record_reader as records


class HandwrittenHosts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)

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

