"""ADR 0395 handwritten read boundary; synthetic inputs only."""
# phi-scan: synthetic
import artifact_lock_test_support
from pathlib import Path
import tempfile
import unittest

import run_record_reader as records


class HandwrittenRecords(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'project-context.md'

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
