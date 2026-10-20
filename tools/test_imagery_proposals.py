"""Contract tests for coursework imagery proposals. #1431."""

from __future__ import annotations

import importlib
import io
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace

import imagery_proposals as proposals
import peer_critique_scan
import repo_root
import approval_record
import completion_checks
from datetime import timedelta
import mechanics_test_support

setUpModule, tearDownModule = mechanics_test_support.module_hooks()
from prose_bind import NAMING, bind
from test_peer_critique_scan import build_run


class CompletionGate(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.model = self.root / "voice-model.md"
        self.domain_evidence = (
            "Orbital mechanics gives me a way to show motion held by a constraint."
        )
        self.model.write_text(
            "# Voice model\n\n"
            "## Imagery\n\n"
            "### The domains\n\n"
            f"> \"{self.domain_evidence}\"\n\n"
            "### How an image works for the writer\n\n"
            "> \"The image carries the mechanism.\"\n\n"
            "### Scale and consequence\n\n"
            "> \"The orbit stays whole.\"\n",
            encoding="utf-8",
        )
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model,
            sha256="a" * 64,
            exists=True,
        )

    def write(self, *, status: str, domain: str | None = None) -> None:
        payload = {
            "proposals": [
                {
                    "key": "image-1",
                    "artifact": "submission",
                    "image": "The care plan needs an orbit, not a straight line.",
                    "domain": domain or self.domain_evidence,
                    "behavior": "keeps the competing force active",
                    "status": status,
                    "ruling": {"clinician_reply": "Yes, keep it.", "reply_at": 200, "shown_draft_at": 100},
                }
            ]
        }
        (self.run / proposals.RECORD_NAME).write_text(
            json.dumps(payload) + "\n", encoding="utf-8"
        )

    def grade(self, text: str) -> proposals.CompletionGate:
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ), mock.patch.object(approval_record, "_main_transcripts", return_value=([[{"type": "user", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": "Yes, keep it."}}]], False)):
            return proposals.completion_gate(
                self.run,
                {"submission": text},
            )

    def real_grade(self, text, *, terminal=True, rows=None, unread=False):
        messages = rows if rows is not None else [{"type": "user", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": "Yes, keep it."}}]
        with mock.patch.object(repo_root, "canonical_voice_model", return_value=self.resolved), mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], unread)):
            return proposals.completion_gate(self.run, {"submission": text}, terminal=terminal)

    def change_record(self, **changes):
        path = self.run / proposals.RECORD_NAME
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["proposals"][0].update(changes)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_whole_reply_and_time_bind_the_shown_draft_not_the_later_edit(self):
        self.write(status="proposed-and-approved")
        text = "The care plan needs an orbit, not a straight line."
        self.assertFalse(self.real_grade(text, terminal=False).finding)
        for row in (
            {"type": "assistant", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": "Yes, keep it."}},
            {"type": "user", "timestamp": "1970-01-01T00:01:00Z", "message": {"content": "Yes, keep it."}},
            {"type": "user", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": "Yes, keep it. With conditions."}},
            {"type": "user", "timestamp": "1970-01-01T00:03:21Z", "message": {"content": "Yes, keep it."}},
        ):
            with self.subTest(row=row):
                self.assertTrue(self.real_grade(text, terminal=False, rows=[row]).finding)
        self.change_record(ruling={"clinician_reply": "Yes, keep it.", "reply_at": 200, "shown_draft_at": 250})
        self.assertTrue(self.real_grade(text, terminal=False).finding)

    def test_unread_transcript_is_counted_once_and_an_independent_marker_still_fails(self):
        self.write(status="proposed-and-approved")
        text = "The care plan needs an orbit, not a straight line."
        result = self.real_grade(text, terminal=False, rows=[], unread=True)
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertEqual(1, result.unread)
        self.assertIn("not verified", result.report)
        result = self.real_grade("[[PROPOSED IMAGE image-1]] " + text, terminal=False, rows=[], unread=True)
        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_later_changes_are_counted_before_submission_and_require_reconfirmation(self):
        self.write(status="proposed-and-approved")
        self.change_record(changed_image="The revised orbit holds the forces together.")
        text = "The revised orbit holds the forces together."
        result = self.real_grade(text, terminal=False)
        self.assertFalse(result.finding, result.report)
        self.assertIn("changed since approval 1", result.report)
        self.assertTrue(self.real_grade(text).finding)
        path = self.run / proposals.RECORD_NAME
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["proposals"][0]["image"] = payload["proposals"][0].pop("changed_image")
        payload["proposals"][0]["ruling"] = {"clinician_reply": "Yes, keep the revision.", "reply_at": 400, "shown_draft_at": 300}
        path.write_text(json.dumps(payload), encoding="utf-8")
        revised_reply = [{"type": "user", "timestamp": "1970-01-01T00:06:40Z", "message": {"content": "Yes, keep the revision."}}]
        self.assertFalse(self.real_grade(text, rows=revised_reply).finding)
        self.change_record(changed_image="")
        self.assertFalse(self.real_grade("Ordinary prose after removal.", terminal=False, rows=revised_reply).finding)
        self.assertTrue(self.real_grade("Ordinary prose after removal.", rows=revised_reply).finding)

    def test_pregrade_start_has_exact_historical_controls(self):
        cutoff = completion_checks.registry()["imagery_proposals:image-stop"][0]
        self.write(status="proposed")
        for moment, finding in ((cutoff - timedelta(microseconds=1), False), (cutoff, True)):
            token = completion_checks.MOMENTS.set({"approval": moment})
            try:
                result = self.real_grade("[[PROPOSED IMAGE image-1]] pending", terminal=False)
                self.assertEqual(finding, result.finding)
            finally:
                completion_checks.MOMENTS.reset(token)

    def test_a_run_without_proposals_reports_zero_counts(self) -> None:
        result = self.grade("Ordinary draft text.")
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)
        self.assertIn("proposed 0; approved 0; unresolved 0", result.report)

    def test_an_unresolved_proposal_fails_completion(self) -> None:
        self.write(status="proposed")
        result = self.grade("[[PROPOSED IMAGE image-1]] The care plan needs an orbit.")
        self.assertTrue(result.finding)
        self.assertIn("proposed 1; approved 0; unresolved 1", result.report)

    def test_a_pregrade_refuses_the_unanswered_proposal_before_submission(self) -> None:
        self.write(status="proposed")
        with mock.patch.object(repo_root, "canonical_voice_model", return_value=self.resolved):
            result = proposals.completion_gate(self.run, {"submission": "[[PROPOSED IMAGE image-1]] The care plan needs an orbit."}, terminal=False)
        self.assertTrue(result.finding)
        self.assertIn("unresolved", result.report)

    def test_a_proposal_from_an_unrecorded_domain_is_refused(self) -> None:
        self.write(status="proposed-and-approved", domain="shipbuilding")
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

    def test_domain_must_be_the_complete_quoted_model_sentence(self) -> None:
        self.write(status="proposed-and-approved", domain="Orbital mechanics")
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

    def test_unquoted_domain_prose_is_not_model_evidence(self) -> None:
        self.write(status="proposed-and-approved")
        self.model.write_text(
            "## Imagery\n\n### The domains\n\n"
            f"{self.domain_evidence}\n",
            encoding="utf-8",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

    def test_an_inline_quote_inside_prose_is_not_a_domain_entry(self) -> None:
        self.write(status="proposed-and-approved")
        self.model.write_text(
            "## Imagery\n\n### The domains\n\n"
            f"The model mentions \"{self.domain_evidence}\" inside prose.\n",
            encoding="utf-8",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

    def test_an_exact_domain_table_cell_is_recorded_evidence(self) -> None:
        self.write(status="proposed-and-approved", domain="orbital mechanics")
        self.model.write_text(
            "## Imagery\n\n### The domains\n\n"
            "| Domain | Attestation |\n| --- | --- |\n"
            "| `orbital mechanics` | recorded twice |\n",
            encoding="utf-8",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertFalse(result.finding)

    def test_an_unrelated_later_table_does_not_inherit_the_domain_column(self) -> None:
        self.write(status="proposed-and-approved", domain="not a domain")
        self.model.write_text(
            "## Imagery\n\n### The domains\n\n"
            "| Domain | Attestation |\n| --- | --- |\n"
            "| `orbital mechanics` | recorded twice |\n\n"
            "| Label | Detail |\n| --- | --- |\n"
            "| not a domain | unrelated evidence |\n",
            encoding="utf-8",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

    def test_a_multiline_blockquote_is_one_complete_domain_entry(self) -> None:
        self.write(status="proposed-and-approved", domain="first fragment")
        self.model.write_text(
            "## Imagery\n\n### The domains\n\n"
            "> first fragment\n"
            "> second fragment\n",
            encoding="utf-8",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("domain is not supported", result.report)

        self.write(
            status="proposed-and-approved",
            domain="first fragment second fragment",
        )
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertFalse(result.finding)

    def test_an_approved_proposal_submits_and_is_a_harvest_exclusion(self) -> None:
        self.write(status="proposed-and-approved")
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)
        self.assertIn("proposed 1; approved 1; unresolved 0", result.report)
        self.assertEqual(
            proposals.harvest_exclusions(self.run),
            ("The care plan needs an orbit, not a straight line.",),
        )

    def test_approved_image_matching_preserves_capitalization(self) -> None:
        self.write(status="proposed-and-approved")
        result = self.grade("the care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("approved image is absent", result.report)

    def test_an_approved_image_with_its_working_marker_still_present_fails(self) -> None:
        self.write(status="proposed-and-approved")
        result = self.grade(
            "[[PROPOSED IMAGE image-1]]\n"
            "The care plan needs an orbit, not a straight line."
        )
        self.assertTrue(result.finding)
        self.assertIn("working marker remains", result.report)

    def test_an_inline_working_marker_also_fails(self) -> None:
        result = self.grade("prefix [[PROPOSED IMAGE ghost]] suffix")
        self.assertTrue(result.finding)
        self.assertIn("working marker remains", result.report)

    def test_a_removed_proposal_must_not_survive_in_the_submission(self) -> None:
        self.write(status="proposed-and-removed")
        result = self.grade("The care plan needs an orbit, not a straight line.")
        self.assertTrue(result.finding)
        self.assertIn("removed image remains", result.report)

    def test_a_partial_reply_grade_still_refuses_an_unknown_artifact_key(self) -> None:
        self.write(status="proposed")
        payload = json.loads(
            (self.run / proposals.RECORD_NAME).read_text(encoding="utf-8")
        )
        payload["proposals"][0]["artifact"] = "misspelled-reply"
        (self.run / proposals.RECORD_NAME).write_text(
            json.dumps(payload) + "\n", encoding="utf-8"
        )
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            result = proposals.completion_gate(
                self.run,
                {"response-maren": "Ordinary draft."},
                partial=True,
                known_artifacts={"response-maren", "response-jon"},
            )
        self.assertTrue(result.finding)
        self.assertIn("not a known artifact", result.report)


class ScopedCompletionGraders(unittest.TestCase):
    def test_every_coursework_completion_grader_declares_the_shared_row(self) -> None:
        modules = (
            "checks_ledger",
            "discussion_post_scan",
            "discussion_reply_scan",
            "peer_critique_scan",
            "course_assignment_scan",
            "deck_scan",
            "assignment_docx_scan",
        )
        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIn(
                    proposals.EXPECTED_ROW,
                    module.EXPECTED_COMPLETION_CHECKS,
                )

    def test_each_scoped_skill_carries_the_proposal_rule_and_go_ahead_table(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for skill in (
            "practicum-case-study",
            "course-assignment",
            "discussion-post",
            "discussion-reply",
            "peer-critique",
        ):
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("imagery-proposals.md", text)
                self.assertIn("| Proposed image | Recorded domain |", text)
                self.assertIn("separately", text)

    def test_voice_harvest_excludes_approved_co_written_images(self) -> None:
        root = Path(__file__).resolve().parent.parent
        voice = (
            root / "skills" / "_shared" / "reference" / "voice.md"
        ).read_text(encoding="utf-8")
        self.assertIn("imagery_proposals.harvest_exclusions", voice)
        self.assertIn("proposed-and-approved", voice)

    def test_shared_sheet_points_to_the_limits_object_without_copying_it(self) -> None:
        root = Path(__file__).resolve().parent.parent
        shared = (
            root / "skills" / "_shared" / "reference" / "imagery-proposals.md"
        ).read_text(encoding="utf-8")
        self.assertEqual((), bind(proposals.DECLARED_LIMITS, shared, mode=NAMING))


class CompletionGraderIntegration(unittest.TestCase):
    def test_public_pregrade_counts_an_unread_answer_once_and_keeps_finding_precedence(self):
        fixture = CompletionGate()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        image = "The care plan needs an orbit, not a straight line."
        fixture.write(status="proposed-and-approved")
        payload = json.loads((fixture.run / proposals.RECORD_NAME).read_text(encoding="utf-8"))
        for marked, expected in ((False, 2), (True, 1)):
            run = build_run(root=fixture.root / ("marked" if marked else "clean"), extra="\n" + ("[[PROPOSED IMAGE image-1]]\n" if marked else "") + image)
            payload["proposals"][0]["artifact"] = "critique"
            second = dict(payload["proposals"][0], key="image-2")
            (run / proposals.RECORD_NAME).write_text(json.dumps({"proposals": [payload["proposals"][0], second]}), encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(repo_root, "canonical_voice_model", return_value=fixture.resolved), mock.patch.object(approval_record, "_main_transcripts", return_value=([], True)), redirect_stdout(output), redirect_stderr(output):
                status = peer_critique_scan.main([str(run)])
            self.assertEqual(expected, status, output.getvalue())
            self.assertEqual(["unread remainder 1"], [line for line in output.getvalue().splitlines() if line.startswith("unread remainder ")])
            self.assertIn("the image answer: not verified", output.getvalue())

    def test_all_six_public_pregrades_refuse_a_surviving_marker(self):
        from test_discussion_post_scan import Run as PostRun
        from test_discussion_reply_scan import Run as ReplyRun
        import discussion_reply_scan
        from test_deck_scan import Run as DeckRun, slide_xml
        import assignment_docx
        import assignment_docx_scan
        from test_assignment_docx_scan import empty_population_input
        import test_checks_ledger as checks_tests

        marker = "[[PROPOSED IMAGE ghost]]"
        def captured(command, arguments):
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                status = command(arguments)
            return status, output.getvalue(), ""

        for host in ("post", "reply", "critique", "deck", "docx", "checks"):
            with self.subTest(host=host), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "clean"
                root.mkdir()
                def run(marked):
                    extra = marker if marked else ""
                    if host == "post":
                        fixture = PostRun(root)
                        fixture.draft.write_text(fixture.draft.read_text(encoding="utf-8") + "\n" + extra, encoding="utf-8")
                        return fixture.grade()
                    if host == "reply":
                        fixture = ReplyRun(root)
                        draft = root / "response-maren.md"
                        if marked:
                            draft.write_text(draft.read_text(encoding="utf-8") + "\n" + extra, encoding="utf-8")
                        fixture.write_heading_read()
                        return captured(discussion_reply_scan.main, [str(root)])
                    if host == "critique":
                        path = build_run(root=root / ("marked" if marked else "clean"), extra="\n" + extra)
                        return captured(peer_critique_scan.main, [str(path)])
                    if host == "deck":
                        fixture = DeckRun(root)
                        fixture.write_deck((slide_xml("Synthetic", "Safe words. " + extra),))
                        return fixture.grade()
                    if host == "docx":
                        case = empty_population_input(root)
                        artifact = Path(case.argv[2])
                        entry = assignment_docx.fixture_spec().references[0]
                        spec = replace(assignment_docx.fixture_spec(), sections=(assignment_docx.Section("Purpose", ("Safe words (Example Agency, 2025). " + extra,)),), references=(entry,))
                        assignment_docx.build(spec, artifact, force=True)
                        run_root = Path(case.argv[0])
                        (run_root / "claims.md").write_text("DATE: 2026-09-13\n\n## CLAIM: Safe words.\nSTATUS: sourced\nREFERENCE: " + entry + "\nREFUTATION: stands - this synthetic source supports the statement\nTESTED-HEADING: " + hashlib.sha256(b"Safe words.").hexdigest() + "\nSECOND-ROUTE: journal page -> independent reader\n", encoding="utf-8")
                        import file_digest
                        file_digest.write_recorded_sha256(run_root / "render" / "pass-1" / assignment_docx_scan.FINGERPRINT_FILE, file_digest.sha256(artifact))
                        heading = run_root / "heading-read.md"
                        import re
                        heading.write_text(re.sub(r"(?m)^DRAFT:.*$", "DRAFT: " + hashlib.sha256(artifact.read_bytes()).hexdigest(), heading.read_text(encoding="utf-8")), encoding="utf-8")
                        return captured(assignment_docx_scan.main, [*case.argv, "--paper-language", "English"])
                    document = root / "draft.md"
                    document.write_bytes((checks_tests.DRAFT_TEXT + ("\n" + extra if marked else "")).encode("utf-8"))
                    checks = root / "checks.md"
                    checks.write_text(checks_tests.whole_file().replace(checks_tests.DRAFT_SHA, hashlib.sha256(document.read_bytes()).hexdigest()), encoding="utf-8")
                    with mock.patch.object(checks_tests, "DRAFT_SHA", hashlib.sha256(document.read_bytes()).hexdigest()):
                        return checks_tests.run([str(checks), "--document", str(document)])
                clean = run(False)
                root = Path(directory) / "marked"
                root.mkdir()
                planted = run(True)
                self.assertEqual(0, clean[0], clean[1] + clean[2])
                self.assertNotIn("working marker remains", clean[1] + clean[2])
                self.assertEqual(1, planted[0], planted[1] + planted[2])
                self.assertIn("ghost working marker remains", planted[1] + planted[2])

    def test_a_synthetic_unresolved_proposal_fails_a_terminal_grader(self) -> None:
        run = build_run(
            extra=(
                "\n[[PROPOSED IMAGE image-1]]\n"
                "The care plan needs an orbit, not a straight line.\n"
            )
        )
        model = run.parent / "voice-model.md"
        evidence = "Orbital mechanics gives me a way to show motion held by a constraint."
        model.write_text(
            "## Imagery\n\n### The domains\n\n" f"> \"{evidence}\"\n",
            encoding="utf-8",
        )
        (run / proposals.RECORD_NAME).write_text(
            json.dumps(
                {
                    "proposals": [
                        {
                            "key": "image-1",
                            "artifact": "critique",
                            "image": "The care plan needs an orbit, not a straight line.",
                            "domain": evidence,
                            "behavior": "keeps the competing force active",
                            "status": "proposed",
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        resolved = repo_root.VoiceModelResolution(
            path=model, sha256="a" * 64, exists=True
        )
        parsed = peer_critique_scan.run_grader.parse(
            peer_critique_scan.GRADER,
            [str(run), "--submission", "critique"],
        )
        source = peer_critique_scan.load(parsed)
        with (
            mock.patch.object(
                peer_critique_scan.aar_scan,
                "completion_gate",
                return_value=(False, "the after-action review: clean"),
            ),
            mock.patch.object(
                peer_critique_scan.voice_model_identity,
                "apply_completion_gate",
                side_effect=lambda grade, *_args, **_kwargs: grade,
            ),
            mock.patch.object(
                peer_critique_scan.voice_read,
                "apply_completion_gate",
                side_effect=lambda grade, *_args, **_kwargs: grade,
            ),
            mock.patch.object(
                peer_critique_scan.project_context,
                "apply_completion_gate",
                side_effect=lambda grade, *_args, **_kwargs: grade,
            ),
            mock.patch.object(
                repo_root, "canonical_voice_model", return_value=resolved
            ),
        ):
            grade = peer_critique_scan.grade(source, parsed)

        self.assertTrue(grade.findings_failed)
        self.assertTrue(any("unresolved 1" in report for report in grade.reports))


if __name__ == "__main__":
    unittest.main()
