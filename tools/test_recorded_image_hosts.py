"""Synthetic public-host integration for the shared recorded-image composition."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
from dataclasses import replace
from datetime import timedelta
import hashlib
import importlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import approval_record
import aar_scan
import assignment_submission
import bar_signatures
import case_video
import completion_checks
import coursework_mechanics
import frozen_grade
import lms_attachments
import project_context
import recorded_image_match as images
import repo_root
import voice_model_identity
import voice_read
import test_assignment_docx_scan as docx_fixture
import test_checks_ledger as checks_fixture
import test_deck_scan as deck_fixture
import test_discussion_post_scan as post_fixture
import test_discussion_reply_scan as reply_fixture
import test_peer_critique_scan as peer_fixture
import test_recorded_image_match as image_fixture
import tool_record_test_support as record_fixture

HOSTS = ("deck_scan", "assignment_docx_scan", "discussion_post_scan",
         "discussion_reply_scan", "peer_critique_scan", "checks_ledger")


class RecordedImageHosts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.model = self.root / "synthetic-model.md"
        self.model.write_text(image_fixture.MODEL, encoding="utf-8")
        self.resolution = repo_root.VoiceModelResolution(
            self.model, hashlib.sha256(self.model.read_bytes()).hexdigest(), True)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(repo_root, "canonical_voice_model", return_value=self.resolution))
        self.stack.enter_context(mock.patch.object(frozen_grade, "all_reports", return_value=None))
        self.stack.enter_context(mock.patch.object(frozen_grade, "command_result", return_value=None))
        # These are separate terminal gates, not the model/match/proposal subject.
        for owner in (voice_model_identity, project_context, lms_attachments,
                      approval_record, bar_signatures, case_video):
            self.stack.enter_context(mock.patch.object(owner, "apply_completion_gate", side_effect=lambda grade, *a, **k: grade))
        self.stack.enter_context(mock.patch.object(coursework_mechanics, "apply_grade", side_effect=lambda grade, *a, **k: grade))
        self.stack.enter_context(mock.patch.object(aar_scan, "completion_gate", return_value=(False, "synthetic AAR: clean")))
        self.stack.enter_context(mock.patch.object(aar_scan, "completion_finding", return_value=None))
        self.stack.enter_context(mock.patch.object(assignment_submission, "completion_gate", return_value=(False, "synthetic submission: clean")))
        # Pair/capture schema and plant behavior are covered by the owning core
        # tests; retain the real apply adapter and composition/report paths here.
        self.stack.enter_context(mock.patch.object(voice_read, "completion_gate", return_value=
            voice_read.CompletionGate(False, False, ("synthetic voice: clean", "synthetic profanity: clean"))))

    def fixture(self, name):
        root = self.root / name
        root.mkdir()
        module = importlib.import_module(name)
        if name == "deck_scan":
            fixture = deck_fixture.Run(root)
            fixture.write_deck((deck_fixture.slide_xml("Plan", "Plain synthetic text"),))
            (root / "reread.md").write_text(
                "## REREAD: synthetic.pptx\nPOST-URL: https://example.test/submission\n"
                "POSTED: 2026-09-13\nREAD: 2026-09-13\nSUBMISSION-SHA256: "
                + hashlib.sha256(fixture.deck.read_bytes()).hexdigest()
                + "\nVERDICT: matches - the submitted deck was read back\n", encoding="utf-8")
            return root, "synthetic.pptx", lambda: fixture.grade("--submission", "synthetic.pptx", "--paper-language", "en")
        if name == "discussion_post_scan":
            fixture = post_fixture.Run(root)
            return root, fixture.draft.name, lambda: fixture.grade("--submission", fixture.draft.name, "--paper-language", "en")
        if name == "discussion_reply_scan":
            reply_fixture.Run(root)
            return root, "response-maren.md", lambda: self.invoke(module, [str(root), "--submission", "response-maren.md", "--paper-language", "en"])
        if name == "peer_critique_scan":
            run = peer_fixture.build_run(root=root)
            return run, "critique.md", lambda: self.invoke(module, [str(run), "--submission", "critique.md", "--paper-language", "en"])
        if name == "checks_ledger":
            path = root / "checks.md"
            path.write_text(checks_fixture.whole_file(), encoding="utf-8")
            # Finish fixture-only identity/render writes before any command or
            # frozen resolver tripwire. The owning command gets an explicit file.
            checks_fixture.run([str(path), "--submission", "synthetic"])
            (root / images.RECORD_NAME).unlink()
            return root, "synthetic", lambda: self.invoke(module,
                [str(path), "--submission", "synthetic", "--document", str(root / "output/synthetic.md")])
        fixture = docx_fixture.empty_population_input(root)
        run, artifact = Path(fixture.argv[0]), Path(fixture.argv[2])
        spec = docx_fixture.assignment_docx.fixture_spec()
        docx_fixture.assignment_docx.build(replace(spec, title_page=replace(spec.title_page, title="Synthetic document")), artifact, force=True)
        digest = docx_fixture.file_digest.sha256(artifact)
        heading = run / "heading-read.md"
        heading.write_text(heading.read_text(encoding="utf-8").replace(
            next(line for line in heading.read_text(encoding="utf-8").splitlines() if line.startswith("DRAFT:")), "DRAFT: " + digest), encoding="utf-8")
        docx_fixture.file_digest.write_recorded_sha256(run / "render/pass-1" / module.FINGERPRINT_FILE, digest)
        claim = "The example connects authority."
        (run / "claims.md").write_text(
            "DATE: 2026-09-13\n\n## CLAIM: " + claim + "\nSTATUS: sourced\nREFERENCE: "
            + spec.references[0] + "\nREFUTATION: stands - the source states the connection.\nTESTED-HEADING: "
            + docx_fixture.research_ledger.heading_digest(claim)
            + "\nSECOND-ROUTE: source page -> independent reading\n", encoding="utf-8")
        return run, artifact.name, lambda: self.invoke(module, [*fixture.argv, "--submission", artifact.name, "--paper-language", "en"])

    def invoke(self, module, arguments):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.ExitStack() as stack:
            if module.__name__ == "checks_ledger":
                stack.enter_context(mock.patch.object(repo_root, "output_root", return_value=Path(arguments[0]).parent / "output"))
            stack.enter_context(contextlib.redirect_stdout(output))
            stack.enter_context(contextlib.redirect_stderr(error))
            status = module.main(arguments)
        return status, output.getvalue(), error.getvalue()

    def write_match(self, run, key):
        path = run / images.RECORD_NAME
        path.write_text(json.dumps({"matches": {key: {"central_point": "Synthetic point.",
            "image": None, "reason": "No recorded image fits this point."}}}), encoding="utf-8")
        return path

    def test_missing_clean_and_unread_model_reach_every_native_host(self):
        for name in HOSTS:
            with self.subTest(host=name):
                self.model.write_text(image_fixture.MODEL, encoding="utf-8")
                run, key, command = self.fixture(name)
                status, output, error = command()
                report = output + error
                self.assertEqual(1, status, report)
                self.assertIn("match record is missing", report)
                self.write_match(run, key)
                status, output, error = command()
                report = output + error
                self.assertEqual(0, status, report)
                self.assertIn("recorded image match: read 1 of 1", report)
                self.model.write_bytes(b"\xff")
                status, output, error = command()
                report = output + error
                self.assertEqual(2, status, report)
                self.assertIn("model imagery unreadable", report)
                self.assertEqual(1, sum(line.startswith("unread remainder ") for line in report.splitlines()), report)
                self.assertIn("unread remainder 1", report)
                (run / images.RECORD_NAME).unlink()
                status, output, error = command()
                report = output + error
                self.assertEqual(1, status, report)
                self.assertIn("match record is missing", report)
                self.assertIn("unread remainder 1", report)
                self.model.write_text(image_fixture.MODEL, encoding="utf-8")

    def test_frozen_native_hosts_do_not_resolve_or_observe_a_new_model(self):
        for name in HOSTS:
            with self.subTest(host=name):
                _run, _key, command = self.fixture(name)
                with mock.patch.object(frozen_grade, "all_reports", return_value="synthetic retained grade"), \
                     mock.patch.object(frozen_grade, "report", return_value="synthetic retained grade"), \
                     mock.patch.object(repo_root, "canonical_voice_model", side_effect=AssertionError("frozen model resolution")), \
                     mock.patch.object(images, "observe", side_effect=AssertionError("frozen model observation")), \
                     mock.patch.object(images, "read_match", side_effect=AssertionError("frozen match record read")):
                    status, output, error = command()
                self.assertEqual(0, status, output + error)
                self.assertIn("synthetic retained grade", output + error)
                self.assertNotIn("model imagery unreadable", output + error)

    def test_native_local_match_damage_and_strict_context_fault_keep_distinct_statuses(self):
        run, key, command = self.fixture("discussion_post_scan")
        path = self.write_match(run, key)
        original = path.read_bytes()
        context = run / "project-context.md"
        context.write_text("CONTEXT-DIGEST: broken\n", encoding="utf-8")
        status, output, error = command()
        report = output + error
        self.assertEqual(2, status, report)
        self.assertIn("unread tool-written records 1", report)
        self.assertIn("unread remainder 1", report)
        self.assertNotIn("model imagery unreadable", report)
        payload = json.loads(original)
        payload["matches"][key]["reason"] = "Synthetic\x07reason"
        path.write_text(json.dumps(payload), encoding="utf-8")
        damaged = path.read_bytes()
        status, output, error = command()
        report = output + error
        self.assertEqual(1, status, report)
        self.assertIn("U+0007", report)
        self.assertIn("unread tool-written records 1", report)
        self.assertEqual(1, sum(line.startswith("unread remainder ") for line in report.splitlines()), report)
        self.assertIn("unread remainder 1", report)
        self.assertNotIn("matched image is absent", report)
        self.assertEqual(damaged, path.read_bytes())

    def test_unopenable_match_record_and_model_are_distinct_single_members_in_all_hosts(self):
        for name in HOSTS:
            with self.subTest(host=name):
                self.model.write_text(image_fixture.MODEL, encoding="utf-8")
                run, _key, command = self.fixture(name)
                path = run / images.RECORD_NAME
                path.mkdir()
                for damaged_model, expected in ((False, 1), (True, 2)):
                    if damaged_model:
                        self.model.write_bytes(b"\xff")
                    status, output, error = command()
                    report = output + error
                    self.assertEqual(2, status, report)
                    self.assertIn("unread recorded-image match records: 1", report)
                    self.assertIn(f"unread remainder {expected}", report)
                    self.assertEqual(1, sum(line.startswith("unread remainder ") for line in report.splitlines()), report)
                    if damaged_model:
                        self.assertIn("unread canonical voice models: 1", report)
                    self.assertTrue(path.is_dir())

    def test_native_multi_reply_selection_keeps_old_exact_unknown_and_shared_record_count(self):
        root = self.root / "mixed"
        root.mkdir()
        fixture = reply_fixture.Run(root)
        rory = root / "response-rory.md"
        rory.write_text(reply_fixture.BODY.replace("Maren,", "Rory,").replace("12%", "measurable")
                        .replace("Quill", "Novel"), encoding="utf-8")
        (root / "posts/rory.md").write_text("AUTHOR: Rory Example\nREPLIES: 0\n\nA synthetic post.\n", encoding="utf-8")
        claims = (root / "claims.md").read_text(encoding="utf-8")
        (root / "claims.md").write_text(claims + "\n" + claims.split("\n\n", 1)[1].replace("[REPLY: maren]", "[REPLY: rory]")
                                      .replace("Quill", "Novel"), encoding="utf-8")
        fixture.write_heading_read()
        reading = reply_fixture.REREAD.format(submission_sha256=hashlib.sha256(rory.read_bytes()).hexdigest()).replace("response-maren.md", rory.name).replace("entry_id=31", "entry_id=32")
        with (root / "reread.md").open("a", encoding="utf-8") as stream:
            stream.write("\n" + reading)
        approval = json.loads((root / "posting-approvals.json").read_text(encoding="utf-8"))
        extra = record_fixture.posting_record(rory, {"skill": "discussion-reply", "submission": rory.name, "posting_route": "agent"})
        approval["items"].extend(extra["items"])
        (root / "posting-approvals.json").write_text(json.dumps(approval), encoding="utf-8")
        start, _ = completion_checks.registry()[images.CHECK]
        old = start - timedelta(microseconds=1)
        original = completion_checks.grading
        selected = "response-maren.md,response-rory.md"
        module = importlib.import_module("discussion_reply_scan")
        for moment, present, expected in ((start, True, 0), (start, False, 1), (None, False, 1)):
            with self.subTest(moment=moment, present=present):
                path = self.write_match(root, rory.name)
                if not present:
                    path.unlink()
                @contextlib.contextmanager
                def dated(run, submission):
                    with original(run, submission):
                        global_token = completion_checks.MOMENTS.set({"approval": old})
                        item_token = completion_checks.ITEM_MOMENTS.set({"response-maren.md": old,
                            **({rory.name: moment} if moment is not None else {})})
                        try:
                            yield
                        finally:
                            completion_checks.ITEM_MOMENTS.reset(item_token)
                            completion_checks.MOMENTS.reset(global_token)
                with mock.patch.object(completion_checks, "grading", dated):
                    status, output, error = self.invoke(module, [str(root), "--submission", selected, "--paper-language", "en"])
                report = output + error
                self.assertEqual(expected, status, report)
                self.assertIn("read 1 of 1" if present else "match record is missing", report)
                self.assertIn("unread remainder 0", report)
        path = root / images.RECORD_NAME
        path.mkdir()
        status, output, error = self.invoke(module, [str(root), "--submission", selected, "--paper-language", "en"])
        self.assertEqual(2, status, output + error)
        self.assertIn("unread recorded-image match records: 1", output + error)
        self.assertIn("unread remainder 1", output + error)

    def test_native_verified_stop_point_reaches_voice_and_unread_transcript_stays_separate(self):
        run, key, command = self.fixture("discussion_post_scan")
        self.write_match(run, key)
        draft = run / key
        image = "A synthetic approved image carries this point."
        draft.write_text(draft.read_text(encoding="utf-8").replace("## References", image + "\n\n## References"), encoding="utf-8")
        (run / "imagery-proposals.json").write_text(json.dumps({"proposals": [{
            "key": "synthetic-proposal", "artifact": key, "image": image,
            "domain": "Synthetic machinery", "behavior": "Carries the bounded point.",
            "status": "proposed-and-approved", "central_point": "Synthetic point.",
            "ruling": {"clinician_reply": "Yes, keep it.", "shown_draft_at": "1970-01-01T00:01:40Z",
                       "reply_at": "1970-01-01T00:03:20Z"}}]}), encoding="utf-8")
        messages = [{"type": "user", "timestamp": "1970-01-01T00:03:20Z",
                     "message": {"content": "Yes, keep it."}}]
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], False)):
            status, output, error = command()
        self.assertEqual(0, status, output + error)
        self.assertEqual(frozenset({(key, "Synthetic point.")}), voice_read.completion_gate.call_args.kwargs["approved_points"])
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([], True)):
            status, output, error = command()
        report = output + error
        self.assertEqual(2, status, report)
        self.assertEqual(frozenset(), voice_read.completion_gate.call_args.kwargs["approved_points"])
        self.assertIn("unread image-answer transcript observations: 1", report)
        self.assertNotIn("unread canonical voice models:", report)
        self.assertNotIn("unread recorded-image match records:", report)
        self.assertIn("unread remainder 1", report)


if __name__ == "__main__":
    unittest.main()
