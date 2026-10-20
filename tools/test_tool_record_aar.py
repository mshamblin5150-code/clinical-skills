"""Public AAR command controls for damaged tool-written bookkeeping (ADR 0422)."""
# phi-scan: synthetic
from pathlib import Path
import json
import unittest
from unittest import mock

import aar_scan
import test_aar_scan as legacy


class ToolWrittenAarRecords(unittest.TestCase):
    def setUp(self):
        self.fixture = legacy.SubmissionRecord("runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        self.fixture.write_clean()
        self.arguments = [str(self.fixture.run), "--submission", self.fixture.submission]

    def paths(self):
        return (
            aar_scan.extract_path(self.fixture.run, self.fixture.submission),
            aar_scan.baseline_path(self.fixture.run, self.fixture.submission),
            aar_scan.memory_measurement_path(self.fixture.run, self.fixture.submission),
        )

    def assert_unreadable(self):
        status, stdout, stderr = legacy.invoke_main(self.arguments)
        self.assertEqual((status, stderr), (2, ""), stdout)
        self.assertIn("not graded - tool-written record unreadable", stdout)
        self.assertNotIn("PRIVATE-PLANTED", stdout)
        self.assertIn("unread remainder 1", stdout)

    def test_truncated_wrong_shape_and_invalid_bytes_are_not_empty_records(self):
        for path in self.paths():
            original = path.read_bytes()
            for damage in (b'{"PRIVATE-PLANTED":', b'[]', b'\xffPRIVATE-PLANTED'):
                with self.subTest(record=path.suffix, damage=damage[:1]):
                    path.write_bytes(damage)
                    self.assert_unreadable()
            path.write_bytes(original)
        status, stdout, stderr = legacy.invoke_main(self.arguments)
        self.assertEqual((status, stderr), (0, ""), stdout)

    def test_unopenable_existing_records_have_the_same_public_failure(self):
        original_open = Path.open
        for path in self.paths():
            def denied(candidate, *args, **kwargs):
                if candidate == path:
                    raise PermissionError("PRIVATE-PLANTED")
                return original_open(candidate, *args, **kwargs)
            with self.subTest(record=path.suffix), mock.patch.object(Path, "open", denied):
                self.assert_unreadable()

    def test_wrong_typed_fields_and_duplicate_json_keys_are_unreadable(self):
        extract, baseline, measurement = self.paths()
        originals = {path: path.read_bytes() for path in self.paths()}
        measured = json.loads(originals[measurement])
        measured["limits"]["lines"] = "200"
        damaged = {
            extract: originals[extract].replace(b"UNREAD-REMAINDER: 0", b"UNREAD-REMAINDER: unknown"),
            baseline: b'{"PRIVATE-PLANTED": []}',
            measurement: json.dumps(measured).encode(),
        }
        for path, content in damaged.items():
            with self.subTest(record=path.suffix):
                path.write_bytes(content)
                self.assert_unreadable()
                path.write_bytes(originals[path])
        baseline.write_bytes(b'{"PRIVATE-PLANTED": null, "PRIVATE-PLANTED": null}')
        self.assert_unreadable()

    def test_missing_original_machine_headers_are_unreadable(self):
        path = self.paths()[0]
        original = path.read_bytes()
        for header in (b"TRANSCRIPTS:", b"WATERMARK:"):
            with self.subTest(header=header):
                path.write_bytes(b"\n".join(line for line in original.split(b"\n") if not line.startswith(header)))
                self.assert_unreadable()
        path.write_bytes(original)

    def test_damaged_posted_reading_is_ungraded_and_independent_findings_survive(self):
        from datetime import datetime, timezone
        path = self.fixture.run / 'reread.md'
        path.write_bytes(b'\xffPRIVATE-PLANTED')
        with mock.patch.object(aar_scan, 'POSTED_READING_FINGERPRINT_CUTOFF', datetime.min.replace(tzinfo=timezone.utc)):
            self.assert_unreadable()
            review = aar_scan.review_path(self.fixture.run, self.fixture.submission)
            review.write_text(review.read_text(encoding='utf-8').replace('UNREAD: 0', 'UNREAD: 1'), encoding='utf-8')
            status, stdout, stderr = legacy.invoke_main(self.arguments)
        self.assertEqual((status, stderr), (1, ''), stdout)
        self.assertIn('not graded', stdout)

    def test_independent_review_finding_wins_over_unreadable_bookkeeping(self):
        review = aar_scan.review_path(self.fixture.run, self.fixture.submission)
        review.write_text(review.read_text(encoding="utf-8").replace(
            f"SUBMISSION: {self.fixture.submission}", "SUBMISSION: different-key"), encoding="utf-8")
        for path in self.paths():
            original = path.read_bytes()
            path.write_bytes(b'[]')
            status, stdout, stderr = legacy.invoke_main(self.arguments)
            self.assertEqual((status, stderr), (1, ""), stdout)
            self.assertIn("not graded - tool-written record unreadable", stdout)
            path.write_bytes(original)

    def test_rebuild_and_measurement_refuse_damaged_extract_without_overwriting(self):
        path = self.paths()[0]
        original = path.read_bytes()
        path.write_bytes(b'\xffPRIVATE-PLANTED')
        for extra in (("--measure-memory",), ("--extract", "--rebuild-round", "1",
                     "--memory-index", str(self.fixture.memory))):
            status, stdout, stderr = legacy.invoke_main([*self.arguments, *extra])
            self.assertEqual(status, 2, stdout + stderr)
            self.assertNotIn("PRIVATE-PLANTED", stdout + stderr)
            self.assertEqual(path.read_bytes(), b'\xffPRIVATE-PLANTED')
        path.write_bytes(original)

    def test_unread_review_candidates_remain_a_finding_when_extract_is_damaged(self):
        review = aar_scan.review_path(self.fixture.run, self.fixture.submission)
        review.write_text(review.read_text(encoding="utf-8").replace("UNREAD: 0", "UNREAD: 1"), encoding="utf-8")
        self.paths()[0].write_bytes(b'[]')
        status, stdout, stderr = legacy.invoke_main([*self.arguments, "--show"])
        self.assertEqual((status, stderr), (1, ""), stdout)
        self.assertIn("unread-candidates", stdout)
        self.assertIn("not graded - tool-written record unreadable", stdout)


if __name__ == "__main__":
    unittest.main()
