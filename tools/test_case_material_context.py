"""Synthetic faculty-source identity and distinct capture context controls."""
# phi-scan: synthetic
import artifact_lock_test_support
from contextlib import redirect_stdout, redirect_stderr
from hashlib import sha256
import io
import json
import unittest
from unittest import mock

import project_context as context
import test_project_context as fixtures


class CaseMaterialContext(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ProjectContextFixture()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.path = self.fixture.run / context.RECORD_NAME
        self.capture = self.fixture.location / "synthetic-capture.md"
        self.capture.write_bytes(b"Synthetic working capture.\r\n")
        self.url = "https://course.example/cases/video?case=7"

    def record(self, material=None, capture=None):
        header = ["CASE-MATERIAL: " + (material or self.url)]
        if capture is not None:
            header.append("CASE-CAPTURE: " + capture)
        entry = self.fixture.plan_entry().replace("STATE: searched", "STATE: read")
        if capture is not None:
            entry += "\nOPENED: " + str(self.capture)
        self.fixture.record(self.fixture.memory_entry(), entry, self.fixture.service_entry(), header=tuple(header))

    def command(self, *options):
        output, error = io.StringIO(), io.StringIO()
        with mock.patch.object(context.repo_root, "project_registry", return_value=self.fixture.registry), \
             mock.patch("sys.stdin", io.StringIO(json.dumps(self.fixture.service_payloads))), \
             redirect_stdout(output), redirect_stderr(error):
            status = context.main([str(self.fixture.run), *(options or
                ("--write", "--submission", "submission", "--service-payloads", "-"))])
        return status, output.getvalue() + error.getvalue()

    def test_faculty_video_url_has_identity_but_no_download_or_file_fingerprint(self):
        self.record()
        original = context._hash_file
        def only_declared_files(entry, owed, opened):
            self.assertNotIn("https://", opened.item)
            return original(entry, owed, opened)
        with mock.patch.object(context, "_hash_file", side_effect=only_declared_files):
            status, report = self.command()
        self.assertEqual(status, 0, report)
        self.assertIn("CASE-MATERIAL: " + self.url, self.path.read_text(encoding="utf-8"))
        self.assertNotIn("CASE-CAPTURE:", self.path.read_text(encoding="utf-8"))

    def test_machine_and_typed_capture_are_separate_opened_fingerprinted_working_items(self):
        for route in ("machine", "typed"):
            with self.subTest(route=route):
                self.record(capture=route + " | " + str(self.capture))
                status, report = self.command()
                self.assertEqual(status, 0, report)
                text = self.path.read_text(encoding="utf-8")
                self.assertIn("CASE-MATERIAL: " + self.url, text)
                self.assertIn("CASE-CAPTURE: " + route + " | " + str(self.capture), text)
                self.assertIn("OPENED: " + str(self.capture) + " | SHA256: " + sha256(self.capture.read_bytes()).hexdigest(), text)
                self.assertIn(str(self.capture), context.recorded_opened_items(self.fixture.run))

    def test_unopened_or_malformed_capture_refuses_and_retains_declarations(self):
        for value in ("invented | " + str(self.capture), "machine | relative.md", str(self.capture),
                      "typed | " + str(self.fixture.location / "unopened.md")):
            with self.subTest(value=value):
                self.record(capture=value)
                before = context.read_record(self.path.read_text(encoding="utf-8"))
                status, report = self.command()
                self.assertEqual(status, 1, report)
                self.assertIn("CASE-CAPTURE", report)
                after = context.read_record(self.path.read_text(encoding="utf-8"))
                self.assertEqual({key: value for key, value in after.fields.items() if key != "ORDER-OBSERVATION"}, before.fields)
                self.assertEqual(after.entries, before.entries)
                self.assertEqual(len(after.values("ORDER-OBSERVATION")), 1)
        self.record(capture="typed | " + str(self.capture))
        self.assertEqual(self.command()[0], 0)

    def test_invalid_video_addresses_refuse_and_faculty_file_compatibility_remains(self):
        for url in ("https://", "ftp://course.example/case", "https://course.example/has space"):
            with self.subTest(url=url):
                self.record(material=url)
                self.assertEqual(self.command()[0], 1)
        self.record(material=str(self.fixture.plan))
        self.assertEqual(self.command()[0], 0)

    def test_capture_route_source_address_and_bytes_bind_digest_and_retained_heading(self):
        self.record(capture="machine | " + str(self.capture))
        self.assertEqual(self.command()[0], 0)
        before = context.recorded_digest(self.fixture.run)
        context.retain_heading_context(self.fixture.run)
        self.assertTrue(context.heading_context_matches(self.fixture.run, before, "draft.md"))
        original = self.path.read_text(encoding="utf-8")
        second = self.fixture.location / "second-capture.md"
        second.write_bytes(self.capture.read_bytes())
        for old, new in (("machine | ", "typed | "), (self.url, self.url + "&revision=2"),
                         (str(self.capture), str(second))):
            self.path.write_text(original.replace(old, new), encoding="utf-8")
            self.assertFalse(context.heading_context_matches(self.fixture.run, before, "draft.md"))
            self.assertEqual(self.command()[0], 0)
            self.assertNotEqual(context.recorded_digest(self.fixture.run), before)
            self.path.write_text(original, encoding="utf-8")
        self.capture.write_bytes(b"Changed synthetic capture.\n")
        self.assertFalse(context.heading_context_matches(self.fixture.run, before, "draft.md"))
        status, report = self.command("--go-ahead", "draft.md")
        self.assertEqual(status, 2, report)
        self.assertIn("moved", report)

    def test_capture_duplicate_and_raw_damage_are_refused_before_publication(self):
        self.record(capture="typed | " + str(self.capture))
        text = self.path.read_text(encoding="utf-8")
        self.path.write_text(text.replace("CONFIRMED:", "CASE-CAPTURE: machine | " + str(self.capture) + "\nCONFIRMED:"), encoding="utf-8")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-CAPTURE", report)
        self.record(capture="typed | " + str(self.capture))
        self.path.write_bytes(self.path.read_bytes().replace(b"typed |", b"typed\x07 |"))
        before = self.path.read_bytes()
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("U+0007", report)
        self.assertEqual(before, self.path.read_bytes())

    def test_case_headers_neither_supply_retrieval_credit_nor_change_absent_capture_digests(self):
        self.record(capture="typed | " + str(self.capture))
        record = context.read_record(self.path.read_text(encoding="utf-8"))
        self.assertFalse(context._has_declared_retrieval(record))
        self.record(material=str(self.fixture.plan))
        self.assertEqual(self.command()[0], 0)
        written = self.path.read_text(encoding="utf-8")
        self.assertNotIn("CASE-CAPTURE", written)
        # A video URL alone grants no PLACE population, unlike declared retrievals.
        self.path.write_text("PROJECT-CONTEXT: none - no registered project\n"
            "OWN-SUBMISSION: none - no own paper\nCASE-MATERIAL: " + self.url +
            "\nCASE-RESEARCH: none - no dump\nCONFIRMED: 2001-01-01\n", encoding="utf-8")
        self.assertEqual(self.command()[0], 0)


if __name__ == "__main__":
    unittest.main()
