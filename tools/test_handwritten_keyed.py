"""Synthetic keyed handwritten-reader routes; no private run content."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
import io
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from datetime import timedelta

import artifact_repairs
import case_video
import completion_checks
import coursework_mechanics
import imagery_proposals
import lms_attachments
import run_grader
import voice_read
import approval_record
import repo_root
import test_voice_read as voice_fixtures
import test_case_video as video_fixtures


def invoke(command):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        status = command()
    return status, output.getvalue()


class KeyedRecordDamage(unittest.TestCase):
    def test_named_voice_artifact_keeps_its_own_historical_remark_window(self):
        case = voice_fixtures.CompletionGate()
        case.setUp()
        self.addCleanup(case.doCleanups)
        reader = case.records / voice_read.READER_RECORD_NAME
        payload = json.loads(reader.read_bytes())
        payload["remarks"] = ["synthetic\a"]
        reader.write_text(json.dumps(payload), encoding="utf-8")
        surface = voice_read.DraftSurface(voice_fixtures.digest(case.draft), case.draft, case.draft)
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        for moment, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1)):
            token = completion_checks.ITEM_MOMENTS.set({"submission.md": moment})
            try:
                with mock.patch.object(repo_root, "canonical_voice_model", return_value=case.resolved):
                    status, report = invoke(lambda: run_grader.collect_record_errors(
                        lambda: int(voice_read.completion_gate(case.run, "submission.md", surface).finding)))
                self.assertEqual(expected, status, report)
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)

    def test_imagery_shared_record_does_not_inherit_old_first_sibling_waiver(self):
        model = self.run / "model.md"
        model.write_text('# Voice model\n## Imagery\n### The domains\n> "Domain evidence."\n', encoding="utf-8")
        payload = {"proposals": [{"key": "image-1", "artifact": "old", "image": "Synthetic image.",
                   "domain": "Domain evidence.", "behavior": "synthetic\a", "status": "proposed-and-removed",
                   "ruling": {"clinician_reply": "Yes, remove it.", "reply_at": 200, "shown_draft_at": 100}}]}
        path = self.run / imagery_proposals.RECORD_NAME
        path.write_text(json.dumps(payload), encoding="utf-8")
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        resolved = repo_root.VoiceModelResolution(path=model, sha256="a" * 64, exists=True)
        for moment, expected in ((cutoff - timedelta(microseconds=1), False), (cutoff, True), (None, True)):
            token = completion_checks.ITEM_MOMENTS.set({"old": moment, "new": cutoff})
            try:
                with mock.patch.object(repo_root, "canonical_voice_model", return_value=resolved), mock.patch.object(
                    approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "", 200)
                ), mock.patch.object(approval_record, "_main_transcripts", return_value=([], False)):
                    self.assertEqual(expected, imagery_proposals.completion_gate(self.run, {"old": "Ordinary prose."}).finding)
                    mixed = imagery_proposals.completion_gate(self.run, {"old": "Ordinary prose.", "new": "Ordinary prose."})
                    self.assertTrue(mixed.finding, mixed.report)
                    self.assertIn("not graded — damaged text", mixed.report)
                    marked = imagery_proposals.completion_gate(self.run, {"old": "[[PROPOSED IMAGE independent]]", "new": "Ordinary prose."})
                    self.assertIn("independent working marker remains", marked.report)
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)

    def test_voice_and_mechanics_before_exact_and_unknown_use_item_moments(self):
        case = voice_fixtures.CompletionGate()
        case.setUp()
        self.addCleanup(case.doCleanups)
        reader = case.records / voice_read.READER_RECORD_NAME
        payload = json.loads(reader.read_bytes())
        payload["remarks"] = ["synthetic\a"]
        reader.write_text(json.dumps(payload), encoding="utf-8")
        record = self.run / coursework_mechanics.RECORD_NAME
        record.write_text(json.dumps({"artifacts": [], "notes": "synthetic\a"}), encoding="utf-8")
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        for moment, expected in ((cutoff - timedelta(microseconds=1), False), (cutoff, True), (None, True)):
            token = completion_checks.ITEM_MOMENTS.set({"submission": moment, "subject": moment, "sibling": cutoff})
            try:
                self.assertEqual(expected, case.grade().finding)
                grade = coursework_mechanics.apply_grade(run_grader.Grade(None, str(self.run)), self.run,
                    (("subject", "Ordinary prose remains."),), run_grader.Parsed(str(self.run)), language="en")
                self.assertEqual(expected, grade.findings_failed, grade.reports)
                # spelling-scan: mentions 1
                grade = coursework_mechanics.apply_grade(run_grader.Grade(None, str(self.run)), self.run,
                    (("subject", "The colour remains."),), run_grader.Parsed(str(self.run)), language="en")
                self.assertTrue(grade.findings_failed)
                self.assertIn("british-body-form: 1", "\n".join(grade.reports))
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)

    def test_attachment_mixed_moments_and_independent_sibling_continue(self):
        directory = self.run / "lms-attachments"
        directory.mkdir()
        local = self.run / "source.txt"
        local.write_bytes(b"synthetic")
        digest = hashlib.sha256(b"synthetic").hexdigest()
        row = {"file_id": "1", "name": "synthetic\a", "size": 9, "sha256": digest,
               "local_sha256": digest, "local_path": str(local), "location_source": "found", "test": "sha256"}
        (directory / "old.md").write_text("ATTACHMENTS: files\n" + json.dumps([row]), encoding="utf-8")
        (directory / "new.md").write_bytes(b"ATTACHMENTS: none\r\n")
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        for moment, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1), (None, 1)):
            token = completion_checks.ITEM_MOMENTS.set({"old": moment, "new": cutoff})
            try:
                self.assertEqual(expected, invoke(lambda: lms_attachments.main([str(self.run), "--submission", "old,new"]))[0])
                (directory / "new.md").write_text("invalid independent appendix", encoding="utf-8")
                status, report = invoke(lambda: lms_attachments.main([str(self.run), "--submission", "old,new"]))
                self.assertEqual(1, status, report)
                self.assertIn("new: record is unreadable or invalid", report)
                (directory / "new.md").write_bytes(b"ATTACHMENTS: none\r\n")
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)

    def test_video_machine_fault_is_two_but_independent_review_finding_wins(self):
        case = video_fixtures.CaptureGate()
        case.setUp()
        self.addCleanup(case.doCleanups)
        (case.root / "capture.json").write_bytes(b"{")
        sibling = case.run / "case-video/sibling.json"
        sibling.write_text('{"kind":"none","reason":"clean"}', encoding="utf-8")
        command = ["check", str(case.run), "--submission", case.key + ",sibling"]
        original = case_video.check_review
        with mock.patch.object(case_video, "check_review", wraps=case_video.check_review) as checked:
            # The native multi-key check has no per-key --draft carrier; use a
            # typed current identity only for this existing source-read fixture.
            checked.side_effect = lambda run, key, draft: original(run, key, case.draft if key == case.key else draft)
            case.review_path.write_text(json.dumps(case.review), encoding="utf-8")
            status, report = invoke(lambda: case_video.main(command))
            self.assertEqual(2, status, report)
            sibling.write_text('{"kind":"none","reason":""}', encoding="utf-8")
            status, report = invoke(lambda: case_video.main(command))
            self.assertEqual(1, status, report)
            self.assertIn("incomplete capture review", report)
            self.assertIn("unread tool-written records 1", report)

    def test_vocabulary_writer_refuses_before_worker_log_or_capture_changes(self):
        capture = self.run / "case-video/capture"
        capture.mkdir(parents=True)
        manifest = capture / "capture.json"
        manifest.write_bytes(b"retained machine evidence")
        terms = self.run / "terms.json"
        terms.write_text(json.dumps({"terms": "PRIVATE\tVALUE"}), encoding="utf-8")
        interpreter = self.run / "synthetic-python.exe"
        interpreter.write_bytes(b"unused interpreter fixture")
        token = completion_checks.MOMENTS.set({"approval": "2000-01-01"})
        try:
            status, report = invoke(lambda: case_video.main(["transcribe", str(self.run), "--terms", str(terms), "--python", str(interpreter)]))
        finally:
            completion_checks.MOMENTS.reset(token)
        self.assertEqual(1, status, report)
        self.assertIn("U+0009", report)
        self.assertEqual(b"retained machine evidence", manifest.read_bytes())
        self.assertFalse((capture / "transcribe.log").exists())

    def test_voice_capture_planter_and_reader_damage_keeps_independent_profanity(self):
        case = voice_fixtures.CompletionGate()
        case.setUp()
        self.addCleanup(case.doCleanups)
        self.assertFalse(case.grade().finding)
        for name in (voice_read.SUPPLIED_VOICE_RECORD_NAME, voice_read.PLANTER_RECORD_NAME, voice_read.READER_RECORD_NAME):
            with self.subTest(record=name):
                path = case.records / name
                before = path.read_bytes()
                payload = json.loads(before)
                payload["PRIVATE-KEY"] = "PRIVATE-VALUE\a"
                path.write_text(json.dumps(payload), encoding="utf-8")
                draft = case.draft
                case.draft += " A fucking example remains."
                result = case.grade()
                self.assertTrue(result.finding, result.reports)
                self.assertIn("not graded — damaged text", result.reports[0])
                self.assertIn("model-owned term(s) found", result.reports[1])
                self.assertNotIn("PRIVATE", "\n".join(result.reports))
                case.draft = draft
                path.write_bytes(before)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name) / "scratch" / "runs" / "synthetic"
        self.run.mkdir(parents=True)

    def routes(self, raw):
        run = self.run
        (run / "lms-attachments").mkdir(exist_ok=True)
        (run / "lms-attachments/subject.md").write_text("ATTACHMENTS: files\n" + raw, encoding="utf-8")
        yield "attachments", invoke(lambda: lms_attachments.main([str(run), "--submission", "subject"]))
        reader, planted, draft = run / "reader.json", run / "planted.txt", run / "draft.txt"
        reader.write_text(raw, encoding="utf-8")
        planted.write_text("Synthetic sentence.", encoding="utf-8")
        draft.write_text("Synthetic sentence.", encoding="utf-8")
        yield "voice", invoke(lambda: voice_read.main(["--check-quotes", str(reader), "--planted", str(planted), "--draft", str(draft)]))
        (run / "case-video").mkdir(exist_ok=True)
        (run / "case-video/subject.json").write_text(raw, encoding="utf-8")
        yield "video", invoke(lambda: case_video.main(["check", str(run), "--submission", "subject"]))
        (run / imagery_proposals.RECORD_NAME).write_text(raw, encoding="utf-8")
        result = imagery_proposals.completion_gate(run, {"subject": "[[PROPOSED IMAGE independent]]"})
        yield "imagery", (int(result.finding), result.report)
        (run / coursework_mechanics.RECORD_NAME).write_text(raw, encoding="utf-8")
        # spelling-scan: mentions 1
        grade = coursework_mechanics.apply_grade(run_grader.Grade(None, str(run)), run,
            (("subject", "The colour remains."),), run_grader.Parsed(str(run)), language="en")
        yield "mechanics", (int(grade.findings_failed), "\n".join(grade.reports))
        scope = run / "scope.json"
        scope.write_text(raw, encoding="utf-8")
        before = scope.read_bytes()
        yield "repair", invoke(lambda: artifact_repairs.main(["begin", str(run), str(draft), "--scope", str(scope)]))
        yield "re-scope", invoke(lambda: artifact_repairs.main(["re-scope", str(run), str(draft), "--repair", "synthetic", "--scope", str(scope), "--clinician-reply", "Synthetic confirmation."]))
        self.assertEqual(before, scope.read_bytes())
        self.assertFalse((run / "private/repairs/chain.json").exists())

    def test_each_public_reader_refuses_raw_and_escaped_damage_without_echo(self):
        for character in ("\t", "\a", "\0", "\f", "\v", "\r"):
            # Keys, vocabulary, free text and heading values all pass through
            # the decoded walk; raw forms must refuse before JSON parsing.
            for field in ("PRIVATE-KEY" + character, "status", "free", "heading"):
                raw = json.dumps({field: "PRIVATE-VALUE" + character})
                for route, (status, report) in self.routes(raw):
                    with self.subTest(character=ord(character), field=field, route=route):
                        self.assertEqual(1, status, report)
                        self.assertIn("not graded — damaged text", report)
                        self.assertIn(f"U+{ord(character):04X}", report)
                        self.assertNotIn("PRIVATE-KEY", report)
                        self.assertNotIn("PRIVATE-VALUE", report)
                raw = raw.replace(json.dumps(character)[1:-1], character)
                for route, (status, report) in self.routes(raw):
                    with self.subTest(raw=True, character=ord(character), route=route):
                        self.assertEqual(1, status, report)
                        self.assertIn(f"U+{ord(character):04X}", report)

    def test_keyed_video_exact_boundary_unknown_and_independent_sibling(self):
        directory = self.run / "case-video"
        directory.mkdir()
        (directory / "old.json").write_text(json.dumps({"kind": "none", "reason": "synthetic\a"}), encoding="utf-8")
        (directory / "new.json").write_bytes(b'{"kind":"none","reason":"clean"}\r\n')
        (directory / "unknown.json").write_text(json.dumps({"kind": "none", "reason": "synthetic\a"}), encoding="utf-8")
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        for moment, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1)):
            token = completion_checks.ITEM_MOMENTS.set({"old": moment, "new": cutoff})
            try:
                self.assertEqual(expected, invoke(lambda: case_video.main(["check", str(self.run), "--submission", "old,new"]))[0])
                self.assertEqual(1, invoke(lambda: case_video.main(["check", str(self.run), "--submission", "unknown,new"]))[0])
                (directory / "new.json").write_text('{"kind":"none","reason":""}', encoding="utf-8")
                status, report = invoke(lambda: case_video.main(["check", str(self.run), "--submission", "old,new"]))
                self.assertEqual(1, status, report)
                self.assertIn("incomplete capture review", report)
                (directory / "new.json").write_bytes(b'{"kind":"none","reason":"clean"}\r\n')
            finally:
                completion_checks.ITEM_MOMENTS.reset(token)

    def test_attachment_escaped_nul_is_a_finding_before_path_construction(self):
        path = self.run / "lms-attachments/subject.md"
        path.parent.mkdir()
        path.write_text("ATTACHMENTS: files\n" + json.dumps([{"local_path": "PRIVATE\0PATH"}]), encoding="utf-8")
        status, report = invoke(lambda: lms_attachments.main([str(self.run), "--submission", "subject"]))
        self.assertEqual(1, status, report)
        self.assertIn("local_path: U+0000", report)
        self.assertNotIn("PRIVATE", report)


if __name__ == "__main__":
    unittest.main()
