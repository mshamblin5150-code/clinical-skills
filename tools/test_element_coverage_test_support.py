"""Synthetic DOCX fixture lifecycle checks, not independent reader evidence."""

from pathlib import Path
import json
import re
import shutil
import tempfile
import unittest
import zipfile

import assignment_docx
import element_coverage
import element_coverage_test_support as fixtures
import file_digest


class ExplicitDocxFixtureFinalization(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        self.artifact = self.run / "assignment.docx"
        # Coverage binds raw artifact bytes; no guarded document producer or
        # actual document/reader execution is needed for this fixture seam.
        self.artifact.write_bytes(b"abc")
        (self.run / "bar.md").write_text("SIGNED: 2099-01-01\nSynthetic fixture bar.\n", encoding="utf-8")
        self.heading = self.run / "heading-read.md"
        self.heading.write_text(
            "## HEADING-READ: assignment.docx\nDRAFT: " + "0" * 64 + "\n"
            "ROUTE: synthetic separate reader\nCONTEXT-DIGEST: preserve-this-context\n"
            "REMARK: Preserve this unrelated reader observation.\nVERDICT: clean\n",
            encoding="utf-8",
        )
        retained = self.run / "render" / "pass-1"
        retained.mkdir(parents=True)
        self.fingerprint = retained / assignment_docx.FINGERPRINT_FILE
        file_digest.write_recorded_sha256(self.fingerprint, "0" * 64)

    def refresh_only_the_old_reader_fingerprints(self):
        digest = file_digest.sha256(self.artifact)
        self.heading.write_text(re.sub(
            r"(?m)^DRAFT: .*", "DRAFT: " + digest,
            self.heading.read_text(encoding="utf-8"),
        ), encoding="utf-8")
        file_digest.write_recorded_sha256(self.fingerprint, digest)

    def test_heading_and_render_only_refresh_leaves_real_coverage_stale(self):
        fixtures.write_synthetic_element_coverage(self.run, self.artifact)
        self.artifact.write_bytes(b"abcd")
        self.refresh_only_the_old_reader_fingerprints()

        result = element_coverage.survey(self.run, self.artifact)

        self.assertTrue(result.failed)
        self.assertIn("artifact digest or name changed", result.report)
        self.assertEqual(file_digest.sha256(self.artifact), file_digest.recorded_sha256(self.fingerprint))

    def test_explicit_finalization_rebinds_coverage_and_preserves_reader_context(self):
        fixtures.write_synthetic_element_coverage(self.run, self.artifact)
        self.artifact.write_bytes(b"abcd")
        context_before = re.sub(r"(?m)^DRAFT: .*\n", "", self.heading.read_text(encoding="utf-8"))

        fixtures.finalize_current_docx_fixture(self.run, self.artifact)

        result = element_coverage.survey(self.run, self.artifact)
        self.assertFalse(result.failed, result.report)
        digest = "88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589"
        self.assertEqual(digest, file_digest.recorded_sha256(self.fingerprint))
        heading = self.heading.read_text(encoding="utf-8")
        self.assertIn("DRAFT: " + digest, heading)
        self.assertEqual(context_before, re.sub(r"(?m)^DRAFT: .*\n", "", heading))

    def test_a_later_artifact_rewrite_stays_stale_until_explicit_finalization(self):
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        before = self.heading.read_bytes(), self.fingerprint.read_bytes()
        self.artifact.write_bytes(b"abcd")

        result = element_coverage.survey(self.run, self.artifact)

        self.assertTrue(result.failed)
        self.assertIn("artifact digest or name changed", result.report)
        self.assertEqual(before, (self.heading.read_bytes(), self.fingerprint.read_bytes()))
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)

    def test_a_renamed_artifact_needs_rebinding_after_its_reader_is_retargeted(self):
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        renamed = self.artifact.with_name("renamed.docx")
        self.artifact.rename(renamed)
        # The producer explicitly supplies the renamed reader identity. The
        # finalizer updates hashes only; it does not rename reader subjects.
        self.heading.write_text(self.heading.read_text(encoding="utf-8").replace(
            "HEADING-READ: assignment.docx", "HEADING-READ: renamed.docx",
        ), encoding="utf-8")

        result = element_coverage.survey(self.run, renamed)

        self.assertTrue(result.failed)
        self.assertIn("artifact digest or name changed", result.report)
        fixtures.finalize_current_docx_fixture(self.run, renamed)
        self.assertFalse(element_coverage.survey(self.run, renamed).failed)
        record = json.loads((self.run / "element-coverage.json").read_text(encoding="utf-8"))
        self.assertEqual("renamed.docx", record["artifact"])

    def test_a_later_bar_input_change_requires_explicit_finalization(self):
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        bar = self.run / "bar.md"
        bar.write_text(bar.read_text(encoding="utf-8") + "Changed synthetic input.\n", encoding="utf-8")

        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)

    def test_a_deleted_coverage_record_is_not_automatically_recreated(self):
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        record = self.run / "element-coverage.json"
        record.unlink()

        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)
        self.assertFalse(record.exists())

        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)

    def test_a_direct_package_copy_requires_explicit_finalization(self):
        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        replacement = self.run / "replacement.docx"
        # Direct public-package bytes avoid invoking a guarded DOCX producer.
        with zipfile.ZipFile(replacement, "w") as archive:
            archive.writestr("word/document.xml", "<synthetic>Rebuilt package.</synthetic>")
        shutil.copyfile(replacement, self.artifact)

        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

        fixtures.finalize_current_docx_fixture(self.run, self.artifact)
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)


if __name__ == "__main__":
    unittest.main()
