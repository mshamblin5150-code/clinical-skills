"""Contract tests for coursework imagery proposals. #1431."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import imagery_proposals as proposals
import peer_critique_scan
import repo_root
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
                }
            ]
        }
        (self.run / proposals.RECORD_NAME).write_text(
            json.dumps(payload) + "\n", encoding="utf-8"
        )

    def grade(self, text: str) -> proposals.CompletionGate:
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            return proposals.completion_gate(
                self.run,
                {"submission": text},
            )

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
        self.assertIn("unresolved 1", grade.reports[-1])


if __name__ == "__main__":
    unittest.main()
