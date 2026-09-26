"""Contract tests for the coursework voice-read completion gates. #1400."""

from __future__ import annotations

import hashlib
import importlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import peer_critique_scan
import repo_root
import test_peer_critique_scan
import voice_read
import voice_model_identity


MODEL = """# Voice model — Synthetic

## Register 1 — clinical argument

### Discriminating pairs

**1a.** A sentence.
- *Generic*: "This is a generic sentence."
- *His*: "This is the sentence I would write."

**1b.** Another sentence.
- *Generic*: "Another generic construction."
- *His*: "Another sentence I would write."

## Profanity — the list graded copy never carries

Match as whole words, compounds and infixes included:

- `fuck` and every form and infix of it (`fucking`, `motherfucker`)

## Seen in the samples, never reproduce

| Defect | Instances |
| --- | --- |
| Dropped word | "he would fine" |

## Seen in the corpus, never reproduce — how he types when nobody is reading

- opens in lowercase
"""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CompletionGate(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.model = self.root / "voice-model.md"
        self.model.write_text(MODEL, encoding="utf-8")
        self.draft = "This is the original sentence. Another sentence remains."
        self.planted = "This is a generic sentence. Another sentence remains."
        self.records = self.run / voice_read.RECORDS_DIRECTORY / "submission"
        self.records.mkdir(parents=True)
        self.capture_path = self.records / voice_read.SUPPLIED_VOICE_RECORD_NAME
        self.capture_path.write_text(
            json.dumps({"status": "none"}) + "\n", encoding="utf-8"
        )
        (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(
            self.planted.encode("utf-8")
        )
        (self.run / "voice-model-identity.json").write_text(
            json.dumps(
                {"path": str(self.model), "sha256": digest(MODEL), "exists": True}
            )
            + "\n",
            encoding="utf-8",
        )
        (self.records / voice_read.PLANTER_RECORD_NAME).write_text(
            json.dumps(
                {
                    "status": "complete",
                    "draft_sha256": digest(self.draft),
                    "planted_sha256": digest(self.planted),
                    "pair_id": "1a",
                    "original_sentence": "This is the original sentence.",
                    "planted_sentence": "This is a generic sentence.",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.records / voice_read.READER_RECORD_NAME).write_text(
            json.dumps(
                {
                    "status": "complete",
                    "draft_sha256": digest(self.draft),
                    "planted_sha256": digest(self.planted),
                    "model_sha256": digest(MODEL),
                    "supplied_voice_sha256": hashlib.sha256(
                        self.capture_path.read_bytes()
                    ).hexdigest(),
                    "suspected_plant_quote": "This is a generic sentence.",
                    "answers": [
                        {
                            "pair_id": "1a",
                            "quote": "This is a generic sentence.",
                            "resemblance": "generic",
                        },
                        {
                            "pair_id": "1b",
                            "quote": None,
                            "resemblance": "no counterpart",
                        },
                    ],
                    "supplied_voice_answers": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(MODEL), exists=True
        )

    def grade(self) -> voice_read.CompletionGate:
        surface = voice_read.DraftSurface(
            sha256=digest(self.draft),
            text=self.draft,
            plantable_text=self.draft,
        )
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            return voice_read.completion_gate(self.run, "submission", surface)

    def payload(self, name: str) -> dict[str, object]:
        return json.loads((self.records / name).read_text(encoding="utf-8"))

    def write_payload(self, name: str, payload: dict[str, object]) -> None:
        (self.records / name).write_text(
            json.dumps(payload) + "\n", encoding="utf-8"
        )

    def record_supplied_item(
        self,
        *,
        source_quote: str,
        verdict: str,
        draft_quote: str | None,
        kind: str = "image",
    ) -> None:
        self.capture_path.write_text(
            json.dumps(
                {
                    "status": "complete",
                    "items": [
                        {
                            "id": "input-1",
                            "kind": kind,
                            "quote": source_quote,
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        if draft_quote is not None:
            self.draft += f" {draft_quote}"
            self.planted += f" {draft_quote}"
            (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(
                self.planted.encode("utf-8")
            )
            planter = self.payload(voice_read.PLANTER_RECORD_NAME)
            planter["draft_sha256"] = digest(self.draft)
            planter["planted_sha256"] = digest(self.planted)
            self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["draft_sha256"] = digest(self.draft)
        reader["planted_sha256"] = digest(self.planted)
        reader["supplied_voice_sha256"] = hashlib.sha256(
            self.capture_path.read_bytes()
        ).hexdigest()
        reader["supplied_voice_answers"] = [
            {"item_id": "input-1", "verdict": verdict, "quote": draft_quote}
        ]
        self.write_payload(voice_read.READER_RECORD_NAME, reader)

    def test_a_correct_record_grades_both_rows_clean(self) -> None:
        result = self.grade()
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)
        self.assertEqual(
            result.reports,
            (
                f"{voice_read.EXPECTED_ROW}: clean; supplied items 0; unanswered 0; pair candidates 2; unread remainder 0",
                f"{voice_read.PROFANITY_EXPECTED_ROW}: clean; profanity rows 1; unread remainder 0",
            ),
        )

    def test_a_supplied_image_kept_whole_grades_clean(self) -> None:
        self.record_supplied_item(
            source_quote="They bounce until they bounce off the cliff.",
            verdict="kept whole",
            draft_quote="They bounce until they bounce off the cliff.",
        )

        result = self.grade()

        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)
        self.assertIn("supplied items 1", result.reports[0])

    def test_a_supplied_image_shrunk_to_a_flat_payoff_is_a_finding(self) -> None:
        self.record_supplied_item(
            source_quote="They bounce until they bounce off the cliff.",
            verdict="shrunk",
            draft_quote="Children are resilient.",
        )

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertIn("supplied item(s) shrunk or dropped", result.reports[0])

    def test_graded_copy_profanity_removal_is_not_shrinkage(self) -> None:
        self.record_supplied_item(
            source_quote="We do not fucking trade the consequence for comfort.",
            verdict="kept whole",
            draft_quote="We do not trade the consequence for comfort.",
            kind="reasoning-ground",
        )

        result = self.grade()

        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)

    def test_a_dropped_supplied_reasoning_ground_is_a_finding(self) -> None:
        self.record_supplied_item(
            source_quote="A principle without a cost is only decoration.",
            verdict="dropped",
            draft_quote=None,
            kind="reasoning-ground",
        )

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertIn("supplied item(s) shrunk or dropped", result.reports[0])

    def test_a_missing_supplied_voice_capture_is_a_finding(self) -> None:
        self.capture_path.unlink()

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertIn("supplied voice capture is missing", result.reports[0])

    def test_a_captured_item_without_a_verdict_is_incomplete_not_clean(self) -> None:
        self.capture_path.write_text(
            json.dumps(
                {
                    "status": "complete",
                    "items": [
                        {
                            "id": "input-1",
                            "kind": "image",
                            "quote": "They bounce until they bounce off the cliff.",
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["supplied_voice_sha256"] = hashlib.sha256(
            self.capture_path.read_bytes()
        ).hexdigest()
        self.write_payload(voice_read.READER_RECORD_NAME, reader)

        result = self.grade()

        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("verdict population is incomplete", result.reports[0])

    def test_a_shrunk_item_wins_when_another_item_has_no_verdict(self) -> None:
        self.capture_path.write_text(
            json.dumps(
                {
                    "status": "complete",
                    "items": [
                        {
                            "id": "input-1",
                            "kind": "image",
                            "quote": "They bounce until they bounce off the cliff.",
                        },
                        {
                            "id": "input-2",
                            "kind": "reasoning-ground",
                            "quote": "A principle without a cost is only decoration.",
                        },
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.draft += " Children are resilient."
        self.planted += " Children are resilient."
        (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(
            self.planted.encode("utf-8")
        )
        planter = self.payload(voice_read.PLANTER_RECORD_NAME)
        planter["draft_sha256"] = digest(self.draft)
        planter["planted_sha256"] = digest(self.planted)
        self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["draft_sha256"] = digest(self.draft)
        reader["planted_sha256"] = digest(self.planted)
        reader["supplied_voice_sha256"] = hashlib.sha256(
            self.capture_path.read_bytes()
        ).hexdigest()
        reader["supplied_voice_answers"] = [
            {
                "item_id": "input-1",
                "verdict": "shrunk",
                "quote": "Children are resilient.",
            }
        ]
        self.write_payload(voice_read.READER_RECORD_NAME, reader)

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("unanswered 1", result.reports[0])

    def test_an_unanswered_pair_population_is_a_finding(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"] = reader["answers"][:-1]  # type: ignore[index]
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("pair population is not fully answered", result.reports[0])

    def test_a_quote_absent_from_the_planted_copy_is_a_finding(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"][1] = {  # type: ignore[index]
            "pair_id": "1b",
            "quote": "A sentence that is not in the copy.",
            "resemblance": "his",
        }
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("quote is not present", result.reports[0])

    def test_a_quote_fragment_is_not_accepted_as_a_verbatim_sentence(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"][1] = {  # type: ignore[index]
            "pair_id": "1b",
            "quote": "sentence remains.",
            "resemblance": "his",
        }
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("not a verbatim sentence", result.reports[0])

    def test_a_model_digest_unequal_to_the_identity_record_is_a_finding(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["model_sha256"] = "b" * 64
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("model digest does not match", result.reports[0])

    def test_a_second_change_in_the_planted_copy_is_a_finding(self) -> None:
        planted = self.planted.replace("remains", "changed")
        (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(planted.encode("utf-8"))
        for name in (voice_read.PLANTER_RECORD_NAME, voice_read.READER_RECORD_NAME):
            payload = self.payload(name)
            payload["planted_sha256"] = digest(planted)
            self.write_payload(name, payload)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("differs in other than the named sentence", result.reports[0])

    def test_a_planter_record_that_does_not_name_the_changed_sentence_is_a_finding(self) -> None:
        planter = self.payload(voice_read.PLANTER_RECORD_NAME)
        planter["original_sentence"] = "A sentence that never existed."
        self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("does not name one plantable", result.reports[0])

    def test_a_missed_planted_sentence_voids_the_read(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["suspected_plant_quote"] = "Another sentence remains."
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("planted sentence was not flagged", result.reports[0])

    def test_a_real_sentence_placed_on_a_generic_half_is_a_finding(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"][1] = {  # type: ignore[index]
            "pair_id": "1b",
            "quote": "Another sentence remains.",
            "resemblance": "generic",
        }
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("real draft sentence", result.reports[0])

    def test_a_draft_digest_that_moved_since_the_read_is_a_finding(self) -> None:
        planter = self.payload(voice_read.PLANTER_RECORD_NAME)
        planter["draft_sha256"] = "c" * 64
        self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("draft digest moved", result.reports[0])

    def test_a_recorded_no_subagent_run_is_incomplete_coverage_not_clean(self) -> None:
        payload = {"status": "not run", "reason": "no subagent tool"}
        self.write_payload(voice_read.PLANTER_RECORD_NAME, payload)
        self.write_payload(voice_read.READER_RECORD_NAME, payload)
        result = self.grade()
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("recorded as not run", result.reports[0])

    def test_the_model_owned_profanity_row_fires_on_an_infix_control(self) -> None:
        self.draft = "This is the original sentence. The control is absofuckinglutely live."
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("model-owned term", result.reports[1])

    def test_an_unread_discriminating_pair_candidate_is_incomplete_coverage(self) -> None:
        malformed = MODEL.replace(
            '- *His*: "Another sentence I would write."',
            '- *Personal*: "Another sentence I would write."',
        )
        self.model.write_text(malformed, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(malformed), exists=True
        )
        identity = json.loads(
            (self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8")
        )
        identity["sha256"] = digest(malformed)
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(identity) + "\n", encoding="utf-8"
        )
        result = self.grade()
        self.assertTrue(result.coverage)
        self.assertIn("pair candidates 2; unread remainder 1", result.reports[0])

    def test_a_malformed_pair_heading_remains_in_the_unread_denominator(self) -> None:
        malformed = MODEL.replace("**1b.** Another sentence.", "**1b** Another sentence.")
        population = voice_read.read_pairs(malformed)
        self.assertEqual(2, population.candidates)
        self.assertEqual(1, population.unread)

    def test_duplicate_pair_halves_are_unread_not_collapsed(self) -> None:
        malformed = MODEL.replace(
            '- *His*: "Another sentence I would write."',
            '- *Generic*: "Another sentence I would write."',
        )
        population = voice_read.read_pairs(malformed)
        self.assertEqual(2, population.candidates)
        self.assertEqual(1, population.unread)

    def test_pair_population_joins_every_discriminating_pair_section(self) -> None:
        second = MODEL.replace("1a", "2a").replace("1b", "2b")
        combined = MODEL + "\n" + second
        population = voice_read.read_pairs(combined)
        self.assertEqual(4, population.candidates)
        self.assertEqual(4, len(population.items))
        self.assertEqual(0, population.unread)

    def test_clean_multiple_submissions_report_the_pair_denominator(self) -> None:
        shutil.copytree(self.records, self.run / voice_read.RECORDS_DIRECTORY / "second")
        surface = voice_read.DraftSurface(
            sha256=digest(self.draft), text=self.draft, plantable_text=self.draft
        )
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            result = voice_read.completion_gate(
                self.run,
                "submission,second",
                {"submission": surface, "second": surface},
            )
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)
        self.assertIn("2 submissions; pair candidates 2; unread remainder 0", result.reports[0])

    def test_an_unread_profanity_list_row_is_incomplete_coverage(self) -> None:
        malformed = MODEL.replace(
            "- `fuck` and every form and infix of it (`fucking`, `motherfucker`)",
            "- every form and infix of the forbidden term",
        )
        self.model.write_text(malformed, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(malformed), exists=True
        )
        identity = json.loads(
            (self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8")
        )
        identity["sha256"] = digest(malformed)
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(identity) + "\n", encoding="utf-8"
        )
        result = self.grade()
        self.assertTrue(result.coverage)
        self.assertIn("profanity rows 1; unread remainder 1", result.reports[1])

    def test_sentence_boundaries_reject_abbreviation_fragments(self) -> None:
        text = "Dr. Smith arrived. Another sentence follows."
        self.assertTrue(voice_read._verbatim_sentence(text, "Dr. Smith arrived."))
        self.assertFalse(voice_read._verbatim_sentence(text, "Smith arrived."))

    def test_sentence_boundaries_accept_a_complete_quoted_sentence(self) -> None:
        text = '“This works.” Another sentence follows.'
        self.assertTrue(voice_read._verbatim_sentence(text, '“This works.”'))
        self.assertTrue(
            voice_read._verbatim_sentence(text, "Another sentence follows.")
        )

    def test_missing_model_sections_preserve_the_population_invariant(self) -> None:
        pairs = voice_read.read_pairs("# No pair section\n")
        profanity = voice_read.read_profanity_terms("# No profanity section\n")
        self.assertEqual((0, 0, True), (pairs.candidates, pairs.unread, pairs.missing))
        self.assertEqual(
            (0, 0, True),
            (profanity.candidates, profanity.unread, profanity.missing),
        )

    def test_missing_capture_is_a_finding_when_no_pair_population_is_read(self) -> None:
        model_without_pairs = MODEL.replace("### Discriminating pairs", "### Other")
        self.model.write_text(model_without_pairs, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(model_without_pairs), exists=True
        )
        identity = json.loads(
            (self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8")
        )
        identity["sha256"] = digest(model_without_pairs)
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(identity) + "\n", encoding="utf-8"
        )
        self.capture_path.unlink()

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertIn("supplied voice capture is missing", result.reports[0])

    def test_shrunk_supplied_item_is_a_finding_without_model_pairs(self) -> None:
        self.record_supplied_item(
            source_quote="They bounce until they bounce off the cliff.",
            verdict="shrunk",
            draft_quote="Children are resilient.",
        )
        model_without_pairs = MODEL.replace("### Discriminating pairs", "### Other")
        self.model.write_text(model_without_pairs, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(model_without_pairs), exists=True
        )
        identity = json.loads(
            (self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8")
        )
        identity["sha256"] = digest(model_without_pairs)
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(identity) + "\n", encoding="utf-8"
        )

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("supplied item(s) shrunk or dropped", result.reports[0])

    def test_kept_supplied_item_is_answered_without_model_pairs(self) -> None:
        self.record_supplied_item(
            source_quote="They bounce until they bounce off the cliff.",
            verdict="kept whole",
            draft_quote="They bounce until they bounce off the cliff.",
        )
        model_without_pairs = MODEL.replace("### Discriminating pairs", "### Other")
        self.model.write_text(model_without_pairs, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(model_without_pairs), exists=True
        )
        identity = json.loads(
            (self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8")
        )
        identity["sha256"] = digest(model_without_pairs)
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(identity) + "\n", encoding="utf-8"
        )

        result = self.grade()

        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("supplied items 1; unanswered 0", result.reports[0])

    def test_unreadable_model_does_not_bypass_a_missing_capture(self) -> None:
        self.capture_path.unlink()
        self.resolved = repo_root.VoiceModelResolution(
            path=self.root / "missing-model.md", sha256="a" * 64, exists=True
        )

        result = self.grade()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("supplied voice capture is missing", result.reports[0])
        self.assertIn("canonical voice model is unreadable", result.reports[0])


class PublicCompletionCommand(unittest.TestCase):
    """Every #1400 refusal is observable through a real completion command."""

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.run = test_peer_critique_scan.build_run(
            root=self.root / "run",
            extra="\n\nA unique closing sentence. A real generic control sentence.",
        )
        self.model = self.root / "voice-model.md"
        self.model.write_text(MODEL, encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(
            path=self.model, sha256=digest(MODEL), exists=True
        )
        self.draft_path = self.run / "critique.md"
        self.draft = self.draft_path.read_text(encoding="utf-8")
        self.original = "A unique closing sentence."
        self.replacement = "This is a generic sentence."
        self.planted = self.draft.replace(self.original, self.replacement, 1)
        self.records = self.run / voice_read.RECORDS_DIRECTORY / "critique"
        self.records.mkdir(parents=True)
        self.capture_path = self.records / voice_read.SUPPLIED_VOICE_RECORD_NAME
        self.capture_path.write_text(
            json.dumps({"status": "none"}) + "\n", encoding="utf-8"
        )
        (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(
            self.planted.encode("utf-8")
        )
        (self.records / voice_read.PLANTER_RECORD_NAME).write_text(
            json.dumps(
                {
                    "status": "complete",
                    "draft_sha256": hashlib.sha256(self.draft_path.read_bytes()).hexdigest(),
                    "planted_sha256": digest(self.planted),
                    "pair_id": "1a",
                    "original_sentence": self.original,
                    "planted_sentence": self.replacement,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.records / voice_read.READER_RECORD_NAME).write_text(
            json.dumps(
                {
                    "status": "complete",
                    "draft_sha256": hashlib.sha256(self.draft_path.read_bytes()).hexdigest(),
                    "planted_sha256": digest(self.planted),
                    "model_sha256": digest(MODEL),
                    "supplied_voice_sha256": hashlib.sha256(
                        self.capture_path.read_bytes()
                    ).hexdigest(),
                    "suspected_plant_quote": self.replacement,
                    "answers": [
                        {
                            "pair_id": "1a",
                            "quote": self.replacement,
                            "resemblance": "generic",
                        },
                        {
                            "pair_id": "1b",
                            "quote": None,
                            "resemblance": "no counterpart",
                        },
                    ],
                    "supplied_voice_answers": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.run / voice_model_identity.RECORD_NAME).write_text(
            json.dumps(
                {"path": str(self.model), "sha256": digest(MODEL), "exists": True}
            )
            + "\n",
            encoding="utf-8",
        )

    def payload(self, name: str) -> dict[str, object]:
        return json.loads((self.records / name).read_text(encoding="utf-8"))

    def write_payload(self, name: str, payload: dict[str, object]) -> None:
        (self.records / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def command(self) -> tuple[int, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.object(
                repo_root, "canonical_voice_model", return_value=self.resolved
            ),
            mock.patch.object(
                peer_critique_scan.aar_scan,
                "completion_gate",
                return_value=(False, "the after-action review: clean"),
            ),
            mock.patch.object(
                peer_critique_scan.project_context,
                "apply_completion_gate",
                side_effect=lambda grade, *_args, **_kwargs: grade,
            ),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = peer_critique_scan.main(
                [str(self.run), "--submission", "critique"]
            )
        return status, stdout.getvalue() + stderr.getvalue()

    def assert_public_finding(self, phrase: str) -> None:
        status, output = self.command()
        self.assertEqual(1, status, output)
        self.assertIn(phrase, output)

    def test_a_correct_record_is_clean_through_the_public_command(self) -> None:
        status, output = self.command()
        self.assertEqual(0, status, output)
        self.assertIn(f"{voice_read.EXPECTED_ROW}: clean", output)

    def test_a_missing_capture_is_a_finding_through_the_public_command(self) -> None:
        self.capture_path.unlink()

        self.assert_public_finding("supplied voice capture is missing")

    def test_incomplete_pair_population_is_public(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"] = reader["answers"][:-1]  # type: ignore[index]
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assert_public_finding("pair population is not fully answered")

    def test_absent_quote_is_public(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"][1] = {  # type: ignore[index]
            "pair_id": "1b",
            "quote": "Not in the planted copy.",
            "resemblance": "his",
        }
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assert_public_finding("quote is not present")

    def test_wrong_model_digest_is_public(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["model_sha256"] = "b" * 64
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assert_public_finding("model digest does not match")

    def test_extra_planted_copy_change_is_public(self) -> None:
        planted = self.planted.replace("word word", "term word", 1)
        (self.records / voice_read.PLANTED_COPY_NAME).write_bytes(planted.encode("utf-8"))
        for name in (voice_read.PLANTER_RECORD_NAME, voice_read.READER_RECORD_NAME):
            payload = self.payload(name)
            payload["planted_sha256"] = digest(planted)
            self.write_payload(name, payload)
        self.assert_public_finding("differs in other than the named sentence")

    def test_unnamed_changed_sentence_is_public(self) -> None:
        planter = self.payload(voice_read.PLANTER_RECORD_NAME)
        planter["original_sentence"] = "Not in the draft."
        self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        self.assert_public_finding("does not name one plantable")

    def test_missed_plant_is_public(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["suspected_plant_quote"] = "No plant identified."
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assert_public_finding("planted sentence was not flagged")

    def test_real_generic_sentence_is_public(self) -> None:
        reader = self.payload(voice_read.READER_RECORD_NAME)
        reader["answers"][1] = {  # type: ignore[index]
            "pair_id": "1b",
            "quote": "A real generic control sentence.",
            "resemblance": "generic",
        }
        self.write_payload(voice_read.READER_RECORD_NAME, reader)
        self.assert_public_finding("real draft sentence")

    def test_moved_draft_digest_is_public(self) -> None:
        planter = self.payload(voice_read.PLANTER_RECORD_NAME)
        planter["draft_sha256"] = "c" * 64
        self.write_payload(voice_read.PLANTER_RECORD_NAME, planter)
        self.assert_public_finding("draft digest moved")


class ScopedCompletionGraders(unittest.TestCase):
    def test_all_five_completion_graders_declare_both_rows(self) -> None:
        self.assertEqual(voice_model_identity.SCOPED_SKILLS, voice_read.SCOPED_SKILLS)
        for skill, module_name in voice_read.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                self.assertIn(voice_read.EXPECTED_ROW, module.EXPECTED_COMPLETION_CHECKS)
                self.assertIn(
                    voice_read.PROFANITY_EXPECTED_ROW,
                    module.EXPECTED_COMPLETION_CHECKS,
                )

    def test_each_skill_names_the_shared_protocol_and_limits_object(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for skill in voice_read.SCOPED_SKILLS:
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("voice-read.md", text)
                self.assertIn("voice_read.DECLARED_LIMITS", text)
                self.assertIn("supplied-voice.json", text)

    def test_graders_and_claude_point_to_one_limits_object_without_copying_rows(self) -> None:
        root = Path(__file__).resolve().parent.parent
        readers = [
            root / "tools" / f"{module_name}.py"
            for module_name in voice_read.COMPLETION_GRADERS.values()
        ]
        readers.append(root / "CLAUDE.md")
        for path in readers:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("voice_read.DECLARED_LIMITS", text)
                for row in voice_read.DECLARED_LIMITS:
                    self.assertNotIn(row.key, text)
                    self.assertNotIn(row.limit, text)

    def test_every_declared_limit_carries_an_evidence_disposition(self) -> None:
        for row in voice_read.DECLARED_LIMITS:
            self.assertIsInstance(row.evidence, voice_read.run_grader.EvidenceDisposition)


if __name__ == "__main__":
    unittest.main()
