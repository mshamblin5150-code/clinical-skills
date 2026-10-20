"""Case video public command and confirmation gate. Synthetic data only."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import case_video
import artifact_lock_test_support
import artifact_lock
from prose_bind import NAMING, bind


class Alignment(unittest.TestCase):
    def test_segmentation_does_not_manufacture_disagreement(self):
        first = [{"start": 0, "end": 3, "text": "Give five mg today."}]
        second = [{"start": 0, "end": 1, "text": "Give five"},
                  {"start": 1, "end": 3, "text": "mg today."}]
        self.assertEqual([], case_video.disagreements(first, second))

    def test_second_pass_only_number_is_not_lost(self):
        first = [{"start": 0, "end": 3, "text": "Give mg today."}]
        second = [{"start": 0, "end": 3, "text": "Give fifty mg today."}]
        self.assertEqual([{"id": "D1", "start": 0, "end": 3,
                           "first": "", "second": "fifty"}], case_video.disagreements(first, second))

    def test_number_and_punctuation_changes_remain_visible(self):
        first = [{"start": 0, "end": 3, "text": "Dose 1.5 mg."}]
        second = [{"start": 0, "end": 3, "text": "Dose 15 mg."}]
        self.assertEqual("1.5", case_video.disagreements(first, second)[0]["first"])


class CaptureGate(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name) / "scratch" / "runs" / "fixture"
        self.root = self.run / "case-video" / "capture"
        (self.root / "frames").mkdir(parents=True)
        self.key = "critique.md"
        self.review_path = self.root.parent / f"{self.key}.json"
        self.draft = b"# Critique\r\nSynthetic teaching case.\r\n"
        self.draft_path = self.run / self.key
        self.draft_path.write_bytes(self.draft)
        first = [{"start": 0, "end": 3, "text": "Give five mg today."}]
        second = [{"start": 0, "end": 3, "text": "Give fifty mg today."}]
        files = {
            "video.mp4": b"synthetic video bytes",
            "frames/frame-000001.png": b"synthetic image bytes",
            "transcript.md": b"Machine transcription",
            "slide-terms.json": json.dumps({"frames_read": ["frames/frame-000001.png"],
                                             "terms": "mg", "model_reason": "Synthetic fixture sizes"}).encode(),
            "pass-1.json": json.dumps(first).encode(),
            "pass-2.json": json.dumps(second).encode(),
            "disagreements.json": json.dumps(case_video.disagreements(first, second)).encode(),
        }
        for name, data in files.items():
            (self.root / name).write_bytes(data)
        self.manifest = {
            "state": "transcribed", "route": "winx", "video": "video.mp4",
            "frames": [{"file": "frames/frame-000001.png", "seconds": 0}],
            "models": ["medium.en", "small.en"],
            "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        }
        self.review = {
            "kind": "machine", "capture": "case-video/capture",
            "draft_sha256": hashlib.sha256(self.draft).hexdigest(),
            "frames_read": ["frames/frame-000001.png"],
            "narration_review": "Compared all narration with the slide images.",
            "narration_only": [{"id": "N1", "kind": "dose", "quote": "five mg", "seconds": 1}],
            "answers": {"D1": "Clinician confirms five.", "N1": "Clinician confirms five mg."},
            "uses": [{"id": "N1", "location": "Intake, first sentence"}],
        }
        self.save()

    def save(self):
        case_video.write_json(self.root / "capture.json", self.manifest)
        self.review["manifest_sha256"] = case_video.digest(self.root / "capture.json")
        case_video.write_json(self.review_path, self.review)

    def gate(self):
        return case_video.completion_gate(self.run, self.key, {self.key: self.draft})

    def test_complete_review_passes_with_exact_crlf_draft_bytes(self):
        failed, report = self.gate()
        self.assertFalse(failed, report)
        self.assertIn("frames read 1; confirmations 2", report)

    def test_each_unanswered_entry_blocks_even_when_not_used(self):
        self.review["uses"] = []
        for entry in ("D1", "N1"):
            with self.subTest(entry=entry):
                saved = self.review["answers"].pop(entry)
                self.save()
                self.assertTrue(self.gate()[0])
                self.review["answers"][entry] = saved

    def test_missing_or_changed_retained_file_blocks(self):
        for name in self.manifest["files"]:
            with self.subTest(file=name):
                file = self.root / name
                original = file.read_bytes()
                file.write_bytes(b"changed")
                if name in {"pass-1.json", "pass-2.json", "disagreements.json", "slide-terms.json"}:
                    from run_record_reader import UnreadableRecord
                    with self.assertRaises(UnreadableRecord):
                        self.gate()
                else:
                    self.assertTrue(self.gate()[0])
                file.write_bytes(original)

    def test_empty_transcription_passes_are_readable_retained_records(self):
        for name in ("pass-1.json", "pass-2.json"):
            path = self.root / name
            case_video.write_json(path, [])
            self.assertEqual([], case_video.read_capture_json(path))
        self.assertEqual([], case_video.disagreements([], []))

    def test_omitted_disagreement_cannot_be_hidden_by_refingerprinting(self):
        case_video.write_json(self.root / "disagreements.json", [])
        self.manifest["files"]["disagreements.json"] = case_video.digest(self.root / "disagreements.json")
        self.review["answers"].pop("D1")
        self.save()
        self.assertTrue(self.gate()[0])

    def test_unread_frame_and_duplicate_read_are_findings(self):
        for frames in ([], ["frames/frame-000001.png"] * 2):
            self.review["frames_read"] = frames
            self.save()
            self.assertTrue(self.gate()[0])

    def test_draft_edit_or_manifest_edit_invalidates_review(self):
        self.draft += b"Edited."
        self.assertTrue(self.gate()[0])
        self.draft = self.draft_path.read_bytes()
        self.manifest["route"] = "local"
        case_video.write_json(self.root / "capture.json", self.manifest)
        self.assertTrue(self.gate()[0])

    def test_same_size_models_refuse_even_with_different_large_versions(self):
        self.manifest["models"] = ["large-v2", "large-v3"]
        self.save()
        self.assertTrue(self.gate()[0])

    def test_missing_or_invalid_route_never_reads_as_nonvideo(self):
        self.review_path.unlink()
        self.assertTrue(self.gate()[0])
        for invalid in ({}, [], {"kind": "none", "reason": ""}, {"kind": "captions"}):
            case_video.write_json(self.review_path, invalid)
            self.assertTrue(self.gate()[0])

    def test_explicit_nonvideo_needs_no_media_dependency(self):
        case_video.write_json(self.review_path, {"kind": "none", "reason": "Document-only faculty case"})
        self.assertFalse(self.gate()[0])

    def test_typed_route_needs_clinician_choice_and_unchanged_file(self):
        typed = self.run / "typed-case.md"
        typed.write_bytes(b"Synthetic typed case")
        self.review = {
            "kind": "typed", "failure": "Decoder unavailable", "clinician_reply": "I will type it.",
            "file": "typed-case.md", "sha256": case_video.digest(typed),
            "draft_sha256": hashlib.sha256(self.draft).hexdigest(),
        }
        self.save()
        self.assertFalse(self.gate()[0])
        self.review["clinician_reply"] = ""
        self.save()
        self.assertTrue(self.gate()[0])
        self.review["clinician_reply"] = "I will type it."
        self.save()
        typed.write_bytes(b"Changed")
        self.assertTrue(self.gate()[0])

    def test_paths_cannot_escape_the_run(self):
        self.review["capture"] = "../../outside"
        self.save()
        self.assertTrue(self.gate()[0])

    def test_public_check_has_counts_but_no_transcript_text(self):
        result = subprocess.run(
            [sys.executable, str(Path(case_video.__file__)), "check", str(self.run),
             "--submission", self.key, "--draft", str(self.draft_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertNotIn("five", result.stdout + result.stderr)

    def test_prepare_refuses_missing_separate_environment_without_leaking_source(self):
        result = subprocess.run(
            [sys.executable, str(Path(case_video.__file__)), "prepare", str(self.run),
             "--source", "private-case-filename.mp4"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(2, result.returncode)
        self.assertNotIn("private-case-filename", result.stderr)

    def test_busy_capture_does_not_start_a_worker_or_clobber_its_log(self):
        log = self.root / "transcribe.log"
        log.write_bytes(b"Existing private log")
        separate = self.run / "separate-python.exe"
        separate.write_bytes(b"Not an executable; a locked operation must never launch it")
        with artifact_lock.hold(self.root, "synthetic competing capture"):
            result = subprocess.run(
                [sys.executable, str(Path(case_video.__file__)), "transcribe", str(self.run),
                 "--python", str(separate), "--terms", str(self.root / "slide-terms.json")],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
        self.assertEqual(2, result.returncode)
        self.assertEqual(b"Existing private log", log.read_bytes())

    def test_unselected_sitting_cannot_supply_a_review(self):
        self.assertTrue(case_video.completion_gate(self.run, "other", {"other": self.draft})[0])

    def test_non_submission_run_reports_not_graded(self):
        failed, report = case_video.completion_gate(self.run, None)
        self.assertFalse(failed)
        self.assertIn("not graded", report)


class Wiring(unittest.TestCase):
    def test_consumers_name_the_limits_without_copying_their_rows(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("AGENTS.md", "CLAUDE.md", "skills/_shared/reference/case-video.md"):
            self.assertFalse(bind(case_video.DECLARED_LIMITS, (root / name).read_text(encoding="utf-8"), mode=NAMING))

    def test_only_the_two_video_case_graders_owe_the_gate(self):
        import checks_ledger
        import peer_critique_scan
        import discussion_post_scan
        for grader in (checks_ledger, peer_critique_scan):
            self.assertIn(case_video.EXPECTED_ROW, grader.EXPECTED_COMPLETION_CHECKS)
        self.assertNotIn(case_video.EXPECTED_ROW, discussion_post_scan.EXPECTED_COMPLETION_CHECKS)


if __name__ == "__main__":
    unittest.main()
