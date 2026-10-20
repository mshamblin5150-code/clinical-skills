"""Synthetic recorded imagery and canonical observation controls."""
# phi-scan: synthetic
import artifact_lock_test_support
import hashlib
import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from dataclasses import dataclass

import repo_root
import voice_model_observation as models
import recorded_image_match as match
import completion_checks
import run_grader
import voice_read
import imagery_proposals
import approval_record
import run_record_reader
import test_voice_read as voice_fixture


MODEL = '''## Imagery
### The domains
> Synthetic machinery
### How an image works for the writer
> The synthetic wheel carries the load.

### Scale and consequence
> A synthetic bridge holds the weight.
> The whole span bears it.
'''


class RecordedImagery(unittest.TestCase):
    def test_independent_quote_starts_expose_zero_and_partial_extraction(self):
        source = MODEL + '\n"An unfinished synthetic image\n'
        result = models.read_images(source)
        self.assertEqual((result.candidates, result.unread), (3, 1))
        with mock.patch.object(models, "_QUOTED") as extractor:
            extractor.finditer.return_value = ()
            result = models.read_images(MODEL)
        self.assertEqual((result.candidates, result.unread), (2, 2))
        original = models._QUOTED
        with mock.patch.object(models, "_QUOTED") as extractor:
            extractor.finditer.side_effect = lambda body: tuple(original.finditer(body))[:0] if "bridge" in body else original.finditer(body)
            result = models.read_images(MODEL)
        self.assertEqual((result.candidates, result.unread), (2, 1))

    def test_empty_and_separate_blockquotes_are_observed(self):
        result = models.read_images(MODEL + '\n>\n\n> A separate complete synthetic image.\n')
        self.assertEqual((result.candidates, result.unread), (4, 1))
        self.assertEqual(models.read_images(MODEL.replace('\n', '\r\n')).images, models.read_images(MODEL).images)
        quoted = MODEL.replace("> The synthetic wheel carries the load.", '> "The synthetic wheel carries the load."')
        self.assertEqual(models.read_images(quoted).images, models.read_images(MODEL).images)
    def test_population_is_derived_without_a_match_record(self):
        result = models.read_images(MODEL)
        self.assertEqual(result.candidates, 2)
        self.assertEqual(result.unread, 0)
        self.assertFalse(result.missing)
        self.assertEqual(result.images, ("The synthetic wheel carries the load.", "A synthetic bridge holds the weight.\nThe whole span bears it."))
        self.assertNotIn("Synthetic machinery", result.images)
        extra = MODEL + '\n"A third complete synthetic image."\n'
        self.assertEqual(models.read_images(extra).candidates, 3)
        self.assertEqual(len(models.read_images(extra).images), 3)

    def test_missing_parts_and_duplicate_sections_cannot_certify_inventory(self):
        for source in ("", MODEL.replace("### Scale and consequence", "### Unrecognized subsection"), MODEL + MODEL):
            with self.subTest(source_length=len(source)):
                self.assertTrue(models.read_images(source).missing)

    def test_observation_hashes_the_same_bytes_it_decodes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-model.md"
            raw = MODEL.replace("\n", "\r\n").encode("utf-8")
            path.write_bytes(raw)
            result = models.observe(repo_root.VoiceModelResolution(path, "stale-resolution-digest", True))
            self.assertEqual(result.sha256, hashlib.sha256(raw).hexdigest())
            self.assertEqual(result.text, raw.decode("utf-8"))
            self.assertEqual(result.unread, 0)
            path.write_bytes(b"\xff")
            unread = models.observe(repo_root.VoiceModelResolution(path, None, True))
            self.assertEqual(unread.unread, 1)
            self.assertIsNone(unread.text)
            self.assertEqual(models.observe(repo_root.VoiceModelResolution(path, None, False)).unread, 1)


class MatchRecord(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.run = Path(self.directory.name)
        self.model = self.run / "synthetic-model.md"
        self.model.write_text(MODEL, encoding="utf-8")
        self.resolution = repo_root.VoiceModelResolution(self.model, hashlib.sha256(self.model.read_bytes()).hexdigest(), True)
        self.patch = mock.patch.object(repo_root, "canonical_voice_model", return_value=self.resolution)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.freeze = mock.patch("frozen_grade.all_reports", return_value=None)
        self.freeze.start()
        self.addCleanup(self.freeze.stop)

    def write(self, image=None, reason="No recorded image fits the synthetic point."):
        (self.run / match.RECORD_NAME).write_text(json.dumps({"matches": {"draft.md": {"central_point": "A bounded synthetic point.", "image": image, "reason": reason}}}), encoding="utf-8")

    def command(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = match.main([str(self.run), "--artifact", "draft.md"])
        return status, output.getvalue()

    def test_native_before_drafting_missing_clean_and_named_image_twins(self):
        self.assertEqual(self.command()[0], 1)
        self.write()
        self.assertEqual(self.command()[0], 0)
        self.write("The synthetic wheel carries the load.")
        self.assertEqual(self.command()[0], 0)
        self.write("An image not in the model.")
        self.assertEqual(self.command()[0], 1)

    def test_terminal_model_and_artifact_membership_are_separate(self):
        image = "The synthetic wheel carries the load."
        self.write(image)
        self.assertFalse(match.completion_gate(self.run, {"draft.md": image}).finding)
        absent = match.completion_gate(self.run, {"draft.md": "No image here."})
        self.assertTrue(absent.finding)
        self.assertIn("finished artifact", absent.report)
        # A clinician removal is carried into the handwritten match, not grandfathered.
        self.write(None, "The clinician removed the matched image.")
        self.assertFalse(match.completion_gate(self.run, {"draft.md": "No image here."}).finding)

    def test_force_and_per_item_boundary_preserve_the_old_record(self):
        self.write()
        path = self.run / match.RECORD_NAME
        raw = path.read_bytes() + b"\x07"
        path.write_bytes(raw)
        boundary = datetime(2026, 10, 20, 17, 22, 53, tzinfo=timezone.utc)
        for moment, expected in ((boundary - timedelta(microseconds=1), False), (boundary, True), (None, True)):
            token = completion_checks.ITEM_MOMENTS.set({"draft.md": moment})
            try:
                result = match.completion_gate(self.run, {"draft.md": "Synthetic draft."})
                self.assertEqual(result.finding, expected)
                self.assertEqual((result.model_unread, result.record_unread), (0, 0))
                self.assertEqual(self.command()[0], 1)
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)
        self.assertEqual(path.read_bytes(), raw)

    def test_model_failure_is_one_member_and_independent_missing_record_stays_finding(self):
        self.model.write_bytes(b"\xff")
        result = match.completion_gate(self.run, {"draft.md": "Synthetic draft."})
        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)
        self.assertEqual(result.model_unread, 1)
        self.write()
        self.assertEqual(self.command()[0], 2)

    def test_absence_has_the_existing_named_door_but_unreadability_does_not(self):
        self.write()
        missing = repo_root.VoiceModelResolution(self.model, None, False)
        with mock.patch.object(repo_root, "canonical_voice_model", return_value=missing):
            status, report = self.command()
        self.assertEqual(status, 2)
        self.assertIn("NOT RUN -- no model", report)
        self.model.write_bytes(b"\xff")
        status, report = self.command()
        self.assertEqual(status, 2)
        self.assertNotIn("NOT RUN -- no model", report)

    def test_unknown_member_cannot_inherit_an_old_global_or_sibling(self):
        boundary = datetime(2026, 10, 20, 17, 22, 53, tzinfo=timezone.utc)
        old = boundary - timedelta(microseconds=1)
        for items in ({}, {"other.md": old}):
            global_token = completion_checks.MOMENTS.set({"approval": old})
            item_token = completion_checks.ITEM_MOMENTS.set(items)
            try:
                self.assertTrue(match.completion_gate(self.run, {"draft.md": "Synthetic draft."}).finding)
            finally:
                completion_checks.ITEM_MOMENTS.reset(item_token)
                completion_checks.MOMENTS.reset(global_token)


@dataclass(frozen=True)
class GateScan:
    image_answer_unread: int = 0
    model_unread: int = 0
    image_match_unread: int = 0


class ComposedVoice(unittest.TestCase):
    def setUp(self):
        self.fixture = voice_fixture.CompletionGate(methodName="runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.run = self.fixture.run
        source = voice_fixture.MODEL
        self.fixture.model.write_text(source, encoding="utf-8")
        digest = hashlib.sha256(self.fixture.model.read_bytes()).hexdigest()
        self.resolved = repo_root.VoiceModelResolution(self.fixture.model, digest, True)
        identity = self.run / "voice-model-identity.json"
        value = json.loads(identity.read_text(encoding="utf-8"))
        value["sha256"] = digest
        identity.write_text(json.dumps(value), encoding="utf-8")
        reader = self.fixture.payload(voice_read.READER_RECORD_NAME)
        reader["model_sha256"] = digest
        reader["unused_recorded_image"] = {"central_point": "Synthetic point.", "image": None, "reason": "No unused recorded image fits."}
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        (self.run / match.RECORD_NAME).write_text(json.dumps({"matches": {"submission": {"central_point": "Synthetic point.", "image": None, "reason": "No recorded image fits."}}}), encoding="utf-8")
        self.resolver = mock.patch.object(repo_root, "canonical_voice_model", return_value=self.resolved)
        self.resolver.start()
        self.addCleanup(self.resolver.stop)
        self.frozen = mock.patch("frozen_grade.all_reports", return_value=None)
        self.frozen.start()
        self.addCleanup(self.frozen.stop)

    def grade(self, finding=False):
        surface = voice_read.DraftSurface(voice_fixture.digest(self.fixture.draft), self.fixture.draft, self.fixture.draft)
        return match.apply_coursework_gates(run_grader.Grade(GateScan(), "synthetic", findings_failed=finding), self.run,
            "submission", surface, {"submission": self.fixture.draft})

    def test_fully_frozen_composition_never_resolves_or_reads_a_model(self):
        with mock.patch("frozen_grade.all_reports", return_value="frozen retained grade"), mock.patch.object(match, "observe", side_effect=AssertionError("new model read")), mock.patch.object(match, "read_match", side_effect=AssertionError("new record read")), mock.patch.object(repo_root, "canonical_voice_model", side_effect=AssertionError("new model resolution")):
            grade = self.grade()
        self.assertEqual(grade.scan.model_unread, 0)
        self.assertFalse(grade.coverage_failed)
        self.assertTrue(all(not report or report == "frozen retained grade" for report in grade.reports))

    def test_mixed_frozen_and_current_match_members_only_owe_current_record(self):
        def frozen(_run, key):
            return "frozen retained grade" if key == "frozen.md" else None
        with mock.patch("frozen_grade.all_reports", side_effect=frozen):
            result = match.completion_gate(self.run, {"frozen.md": "Old synthetic paper.", "submission": self.fixture.draft})
        self.assertFalse(result.finding)
        self.assertIn("read 1 of 1", result.report)

    def test_native_voice_question_and_original_populations_remain_independent(self):
        self.assertFalse(self.grade().findings_failed)
        self.assertFalse(self.grade().coverage_failed)
        reader = self.fixture.payload(voice_read.READER_RECORD_NAME)
        reader["unused_recorded_image"]["image"] = "The synthetic wheel carries the load."
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assertTrue(self.grade().findings_failed)
        # Missing the plant still fails even if the new question says no image fits.
        reader["unused_recorded_image"]["image"] = None
        reader["suspected_plant_quote"] = "A wrong synthetic sentence."
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assertTrue(self.grade().findings_failed)

    def test_unreadable_model_is_one_member_and_does_not_hide_prior_findings(self):
        self.fixture.model.write_bytes(b"\xff")
        grade = self.grade(finding=True)
        self.assertTrue(grade.findings_failed)
        self.assertTrue(grade.coverage_failed)
        self.assertEqual(grade.scan.model_unread, 1)
        self.assertEqual(grade.scan.image_answer_unread, 0)

    def test_match_record_and_model_fault_populations_remain_separate(self):
        path = self.run / match.RECORD_NAME
        path.unlink()
        path.mkdir()
        grade = self.grade()
        self.assertEqual((grade.scan.model_unread, grade.scan.image_match_unread, grade.scan.image_answer_unread), (0, 1, 0))
        self.assertTrue(grade.coverage_failed)
        self.fixture.model.write_bytes(b"\xff")
        grade = self.grade(finding=True)
        self.assertTrue(grade.findings_failed)
        self.assertEqual((grade.scan.model_unread, grade.scan.image_match_unread, grade.scan.image_answer_unread), (1, 1, 0))
        self.assertIn("unread canonical voice models: 1", "\n".join(grade.reports))
        self.assertIn("unread recorded-image match records: 1", "\n".join(grade.reports))

    def test_machine_identity_fault_does_not_hide_the_independent_reader_question(self):
        reader = self.fixture.payload(voice_read.READER_RECORD_NAME)
        reader["unused_recorded_image"]["image"] = "The synthetic wheel carries the load."
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        identity = self.run / "voice-model-identity.json"
        identity.write_bytes(b"{")
        with run_record_reader.capture_errors() as faults:
            grade = self.grade()
        self.assertTrue(grade.findings_failed)
        self.assertTrue(grade.coverage_failed)
        self.assertIn("reader identified a fitting recorded image", "\n".join(grade.reports))
        self.assertEqual(len(faults), 1)
        self.assertEqual(identity.read_bytes(), b"{")

    def test_same_point_approval_skips_only_the_new_question(self):
        reader = self.fixture.payload(voice_read.READER_RECORD_NAME)
        del reader["unused_recorded_image"]
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        surface = voice_read.DraftSurface(voice_fixture.digest(self.fixture.draft), self.fixture.draft, self.fixture.draft)
        same = voice_read.completion_gate(self.run, "submission", surface,
            approved_points=frozenset({("submission", "Synthetic point.")}))
        self.assertFalse(same.finding)
        self.assertFalse(same.coverage)
        other = voice_read.completion_gate(self.run, "submission", surface,
            approved_points=frozenset({("submission", "An unrelated point.")}))
        self.assertTrue(other.coverage)
        reader["suspected_plant_quote"] = "A wrong synthetic sentence."
        self.fixture.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assertTrue(voice_read.completion_gate(self.run, "submission", surface,
            approved_points=frozenset({("submission", "Synthetic point.")})).finding)

    def test_only_actual_verified_current_proposal_returns_same_point_metadata(self):
        image = "A synthetic comparison carries the point."
        proposal = {"key": "synthetic-image", "artifact": "submission", "image": image,
            "domain": "Synthetic machinery", "behavior": "carries a bounded load",
            "status": "proposed-and-approved", "central_point": "Synthetic point.",
            "ruling": {"clinician_reply": "Yes, keep this synthetic image.", "reply_at": 200, "shown_draft_at": 100}}
        path = self.run / imagery_proposals.RECORD_NAME
        rows = [{"type": "user", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": proposal["ruling"]["clinician_reply"]}}]
        def grade():
            path.write_text(json.dumps({"proposals": [proposal]}), encoding="utf-8")
            with mock.patch.object(approval_record, "_main_transcripts", return_value=([rows], False)):
                return imagery_proposals.completion_gate(self.run, {"submission": image})
        self.assertEqual(grade().approved_points, frozenset({("submission", "Synthetic point.")}))
        proposal["changed_image"] = image + " Revised."
        self.assertEqual(grade().approved_points, frozenset())
        del proposal["changed_image"]
        proposal["ruling"]["clinician_reply"] = "A message that was never said."
        self.assertEqual(grade().approved_points, frozenset())
        proposal["ruling"]["clinician_reply"] = rows[0]["message"]["content"]
        del proposal["central_point"]
        legacy = grade()
        self.assertFalse(legacy.finding)
        self.assertEqual(legacy.approved_points, frozenset())
