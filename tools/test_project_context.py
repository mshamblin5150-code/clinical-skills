"""Behavior tests for the project-context gate. #1395.

Every project, path, service, and payload is synthetic.

phi-scan: synthetic
"""

from __future__ import annotations

import hashlib
import importlib
import json
import io
from contextlib import redirect_stdout
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import project_context as context
import repo_root
import run_grader
import approval_record
import assignment_submission
from test_discussion_reply_scan import Run


class ProjectContextFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name).resolve()
        self.run = self.root / "atlas-discussion"
        self.run.mkdir()
        self.memory = self.root / "memory-index.md"
        self.location = self.root / "atlas"
        self.location.mkdir()
        self.plan = self.location / "atlas-plan.md"
        self.memory.write_bytes(b"memory index\n")
        self.plan.write_bytes(b"atlas plan\n")
        self.registry = self.root / "project-registry.md"
        self.registry.write_text(
            "\n".join(
                (
                    f"MEMORY-INDEX: {self.memory}",
                    "",
                    "PROJECT: Atlas",
                    f"  LOCATION: {self.location}",
                    "  SERVICE: open-brain",
                    "",
                )
            ),
            encoding="utf-8",
        )
        self.service_payloads = {"open-brain": {"thought-17": "founder account"}}

    def record(self, *entries: str, header: tuple[str, ...] = ()) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "\n".join(
                (
                    "PROJECT-CONTEXT: Atlas",
                    *(("OWN-SUBMISSION: none - no earlier synthetic submission",)
                      if not any(line.startswith("OWN-SUBMISSION:") for line in header) else ()),
                    *header,
                    "CONFIRMED: 2001-01-01",
                    "",
                    *entries,
                    "",
                )
            ),
            encoding="utf-8",
        )

    def memory_entry(self, state: str = "read") -> str:
        return "\n".join(
            (
                f"## PLACE: {self.memory}",
                f"STATE: {state}",
                f"OPENED: {self.memory}",
            )
        )

    def plan_entry(self, *, terms: str = "founder motivation", opened: str | None = None) -> str:
        return "\n".join(
            (
                f"## PLACE: {self.location}",
                "STATE: searched",
                f"ROOT: {self.location}",
                f"TERMS: {terms}",
                "EXAMINED: 4",
                "UNREADABLE: 0",
                f"OPENED: {opened or self.plan}",
            )
        )

    def service_entry(self, *, opened: str = "thought-17") -> str:
        return "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: searched",
                "CORPUS-SIZE: 42",
                "QUERY: founder motivation | THRESHOLD: 0.75 | LIMIT: 5 | HITS: 1",
                f"OPENED: {opened}",
            )
        )

    def complete_record(self) -> None:
        self.record(self.memory_entry(), self.plan_entry(), self.service_entry())

    def write(self, payloads: dict[str, dict[str, str]] | None = None) -> context.GateResult:
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.write_record(
                self.run,
                service_payloads=self.service_payloads if payloads is None else payloads,
                submission="submission",
            )

    def complete(self, submission: str | None = "submission") -> context.CompletionGate:
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.completion_gate(self.run, submission)


class AProjectContextGateWritesTheRetrievalFingerprint(ProjectContextFixture):
    def test_a_complete_record_is_canonicalized_with_machine_written_hashes(self) -> None:
        self.complete_record()

        result = self.write()

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.waived, 0)
        written = self.run.joinpath(context.RECORD_NAME).read_text(encoding="utf-8")
        memory_digest = hashlib.sha256(b"memory index\n").hexdigest()
        self.assertIn(
            f"OPENED: {self.memory} | SHA256: {memory_digest}",
            written,
        )
        self.assertIn(
            "OPENED: thought-17 | SHA256: "
            + hashlib.sha256(b"founder account").hexdigest(),
            written,
        )
        digest = context.recorded_digest(self.run)
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertIn(f"CONTEXT-DIGEST: {digest}", written)

    def test_the_context_digest_binds_own_submission_and_sorted_place_item_hash_triples(self) -> None:
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        triples = sorted(
            (
                (str(self.memory), str(self.memory), hashlib.sha256(b"memory index\n").hexdigest()),
                (str(self.location), str(self.plan), hashlib.sha256(b"atlas plan\n").hexdigest()),
                ("open-brain", "thought-17", hashlib.sha256(b"founder account").hexdigest()),
            )
        )
        expected = hashlib.sha256(
            ("OWN-SUBMISSION\0none - no earlier synthetic submission\n" +
             "".join("\0".join(triple) + "\n" for triple in triples)).encode("utf-8")
        ).hexdigest()
        self.assertEqual(context.recorded_digest(self.run), expected)

    def test_a_none_declaration_needs_a_reason_and_writes_none(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none - critique concerns a classmate's case\nOWN-SUBMISSION: none - no earlier synthetic submission\n"
            "CONFIRMED: 2001-01-01\n",
            encoding="utf-8",
        )

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.recorded_digest(self.run), "67d55228f3d5d679eb597e38d220b591803ef13085d57f1176ec0b6302c5fc8f")

    def test_none_without_a_reason_is_a_finding(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none\nOWN-SUBMISSION: none - no earlier synthetic submission\nCONFIRMED: 2001-01-01\n", encoding="utf-8"
        )
        self.assertEqual(self.write(payloads={}).exit_code, 1)

    def test_an_unregistered_project_is_a_coverage_stop_that_asks_the_clinician(self) -> None:
        self.record()
        self.run.joinpath(context.RECORD_NAME).write_text(
            self.run.joinpath(context.RECORD_NAME)
            .read_text(encoding="utf-8")
            .replace("Atlas", "Unregistered", 1),
            encoding="utf-8",
        )

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 2)
        self.assertIn("ask the clinician", result.report)

    def test_a_missing_registry_is_a_coverage_stop(self) -> None:
        self.complete_record()
        with mock.patch.object(
            repo_root, "project_registry", return_value=self.root / "absent.md"
        ):
            result = context.write_record(self.run, service_payloads=self.service_payloads)
        self.assertEqual(result.exit_code, 2)


class EveryOwedPlaceHasOneSubstantiveEntry(ProjectContextFixture):
    def test_a_missing_owed_place_is_a_finding(self) -> None:
        self.record(self.memory_entry(), self.plan_entry())
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("open-brain", result.report)

    def test_a_duplicate_owed_place_is_a_finding(self) -> None:
        self.record(
            self.memory_entry(), self.plan_entry(), self.service_entry(), self.service_entry()
        )
        self.assertEqual(self.write().exit_code, 1)

    def test_a_searched_path_needs_terms_and_examined_count(self) -> None:
        self.record(
            self.memory_entry(),
            self.plan_entry().replace("TERMS: founder motivation\n", "").replace(
                "EXAMINED: 4\n", ""
            ),
            self.service_entry(),
        )
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("TERMS", result.report)
        self.assertIn("EXAMINED", result.report)

    def test_a_searched_path_records_opened_none_as_a_miss(self) -> None:
        self.record(self.memory_entry(), self.plan_entry(opened="none"), self.service_entry())
        result = self.write()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("OPENED: none", self.run.joinpath(context.RECORD_NAME).read_text())

    def test_a_read_location_cannot_open_an_unrelated_file(self) -> None:
        unrelated = self.root / "unrelated.md"
        unrelated.write_text("synthetic unrelated context\n", encoding="utf-8")
        self.record(
            self.memory_entry().replace(
                f"OPENED: {self.memory}", f"OPENED: {unrelated}"
            ),
            self.plan_entry(),
            self.service_entry(),
        )

        result = self.write()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("outside owed PLACE", result.report)

    def test_a_searched_location_root_must_be_the_owed_location(self) -> None:
        self.record(
            self.memory_entry(),
            self.plan_entry().replace(f"ROOT: {self.location}", f"ROOT: {self.root}"),
            self.service_entry(),
        )

        result = self.write()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("ROOT does not match", result.report)

    def test_a_service_needs_corpus_query_threshold_limit_and_hits(self) -> None:
        incomplete = self.service_entry().replace("CORPUS-SIZE: 42\n", "").replace(
            " | HITS: 1", ""
        )
        self.record(self.memory_entry(), self.plan_entry(), incomplete)
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("CORPUS-SIZE", result.report)
        self.assertIn("HITS", result.report)

    def test_a_service_opened_item_needs_payload_text_for_the_gate_to_hash(self) -> None:
        self.complete_record()
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("thought-17", result.report)

    def test_a_prior_digest_never_substitutes_for_returned_service_text(self) -> None:
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no returned text", result.report)

    def test_a_service_url_is_refused_in_the_registry(self) -> None:
        self.registry.write_text(
            self.registry.read_text(encoding="utf-8").replace(
                "SERVICE: open-brain", "SERVICE: https://credential.example/mcp"
            ),
            encoding="utf-8",
        )
        self.complete_record()
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("credential.example", result.report)

    def test_one_off_search_is_owed_and_its_terms_must_match(self) -> None:
        extra = self.root / "extra"
        extra.mkdir()
        note = extra / "note.md"
        note.write_text("synthetic context\n", encoding="utf-8")
        extra_entry = "\n".join(
            (
                f"## PLACE: {extra}",
                "STATE: searched",
                f"ROOT: {extra}",
                "TERMS: rural access",
                "EXAMINED: 1",
                "UNREADABLE: 0",
                f"OPENED: {note}",
            )
        )
        self.record(
            self.memory_entry(),
            self.plan_entry(),
            self.service_entry(),
            extra_entry,
            header=(f'PROJECT-SEARCH: {extra} - "rural access"',),
        )
        self.assertEqual(self.write().exit_code, 0)

        text = self.run.joinpath(context.RECORD_NAME).read_text(encoding="utf-8")
        self.run.joinpath(context.RECORD_NAME).write_text(
            text.replace("TERMS: rural access", "TERMS: another topic"), encoding="utf-8"
        )
        self.assertEqual(self.write().exit_code, 1)

    def test_unreadable_and_absent_places_need_confirmed_waivers(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        self.record(self.memory_entry(), self.plan_entry(), failed)
        self.assertEqual(self.write(payloads={}).exit_code, 1)

        self.record(
            self.memory_entry(),
            self.plan_entry(),
            failed,
            header=(
                "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23; "
                "proceed without, per the clinician",
            ),
        )
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.waived, 1)
        self.assertIn("waived places: 1", result.report)

    def test_a_waiver_needs_a_date_and_the_clinician_attestation(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        for waiver in (
            "PROJECT-WAIVE: open-brain - service unavailable; proceed without, per the clinician",
            "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23",
            "PROJECT-WAIVE: open-brain - service unavailable on 2026-99-99; proceed without, per the clinician",
            "PROJECT-WAIVE: open-brain - 2026-09-23; proceed without, per the clinician",
        ):
            with self.subTest(waiver=waiver):
                self.record(self.memory_entry(), self.plan_entry(), failed, header=(waiver,))
                self.assertEqual(self.write(payloads={}).exit_code, 1)


class CompletionRechecksFileItems(ProjectContextFixture):
    def setUp(self) -> None:
        super().setUp()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

    def test_an_unchanged_record_is_clean(self) -> None:
        result = self.complete()
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)

    def test_a_location_cannot_suppress_rehashing_with_service_metadata(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        marker = f"## PLACE: {self.location}\nSTATE: searched\n"
        record.write_text(
            text.replace(marker, marker + "CORPUS-SIZE: 1\n"), encoding="utf-8"
        )
        self.plan.write_text("changed plan\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_a_hashed_location_cannot_be_relabeled_unreadable_to_suppress_rehashing(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        marker = f"## PLACE: {self.location}\nSTATE: searched\n"
        text = text.replace(
            "CONFIRMED: 2001-01-01\n",
            "PROJECT-WAIVE: "
            f"{self.location} - file unavailable on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2001-01-01\n",
        ).replace(marker, f"## PLACE: {self.location}\nSTATE: unreadable\nDETAIL: moved\n")
        record.write_text(text, encoding="utf-8")
        self.plan.write_text("changed plan\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_a_waiver_for_a_readable_place_is_a_finding_and_not_counted(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8").replace(
            "CONFIRMED: 2001-01-01\n",
            "PROJECT-WAIVE: "
            f"{self.memory} - stale lead on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2001-01-01\n",
        )
        record.write_text(text, encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertIn("waived places: 0", result.report)

    def test_a_changed_file_is_exit_two_coverage(self) -> None:
        self.plan.write_text("changed plan\n", encoding="utf-8")
        result = self.complete()
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("file item moved", result.report)

    def test_a_missing_record_is_a_finding_only_at_completion(self) -> None:
        self.run.joinpath(context.RECORD_NAME).unlink()
        result = self.complete()
        self.assertTrue(result.finding)
        early = self.complete(None)
        self.assertFalse(early.finding)
        self.assertIn("not graded", early.report)

    def test_a_record_tamper_is_a_finding_and_wins_over_file_drift(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        record.write_text(
            record.read_text(encoding="utf-8").replace(
                "CONTEXT-DIGEST: ", "CONTEXT-DIGEST: " + "0" * 64 + " # "
            ),
            encoding="utf-8",
        )
        self.plan.write_text("changed plan\n", encoding="utf-8")
        result = self.complete()
        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_deleting_an_owed_entry_after_the_gate_is_a_finding(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        record.write_text(text.split(f"\n## PLACE: {self.location}", 1)[0] + "\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertIn("record shape is invalid", result.report)

    def test_service_items_are_not_retrieved_again_at_completion(self) -> None:
        result = self.complete()
        self.assertNotIn("service", result.report.casefold())

    def test_completion_reports_the_waived_place_count(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        self.record(
            self.memory_entry(),
            self.plan_entry(),
            failed,
            header=(
                "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23; "
                "proceed without, per the clinician",
            ),
        )
        self.assertEqual(self.write(payloads={}).exit_code, 0)

        result = self.complete()

        self.assertIn("waived places: 1", result.report)

    def test_shared_adapter_preserves_finding_precedence(self) -> None:
        self.run.joinpath(context.RECORD_NAME).unlink()
        base = run_grader.Grade(scan=object(), source=str(self.run))
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            result = context.apply_completion_gate(base, self.run, "submission")
        self.assertTrue(result.findings_failed)
        self.assertIn("record is missing", result.reports[-1])


class GoAheadRechecks(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

    def check(self, key="submission"):
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.go_ahead(self.run, key)

    def record_posting(self, *, required=True):
        # A pre-check durable record uses the historical public reader contract.
        (self.run / approval_record.RECORD).write_text(json.dumps({
            "items": [{"skill": "discussion-post", "submission": "submission",
                       "posting_route": "agent", "project_context_check": required}]
        }), encoding="utf-8")

    def test_an_added_memory_line_is_shown_without_moving_the_index(self):
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        original_digest = context.recorded_digest(self.run)
        self.memory.write_text("memory index\nnew pointer\n", encoding="utf-8")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            result = context.go_ahead(self.run, "submission")
        self.assertFalse(result.coverage, result.report)
        self.assertFalse(result.finding, result.report)
        self.assertIn("new pointer", result.report)
        self.assertEqual(original_digest, context.recorded_digest(self.run))

    def test_edited_and_removed_memory_lines_each_move(self):
        for text in ("edited pointer\n", ""):
            with self.subTest(text=text):
                self.memory.write_text(text, encoding="utf-8")
                result = self.check()
                self.assertTrue(result.coverage, result.report)
                self.assertIn(str(self.memory), result.report)

    def test_reordering_whitespace_and_blank_lines_do_not_move_but_duplicate_loss_does(self):
        self.memory.write_text("first\nsecond\nfirst\n", encoding="utf-8")
        self.assertEqual(self.write().exit_code, 0)
        self.memory.write_text("second  \n\nfirst\nfirst\n", encoding="utf-8")
        self.assertFalse(self.check().coverage)
        self.memory.write_text("second\nfirst\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)

    def test_a_moved_planning_file_is_named_and_reapproval_replaces_only_its_key(self):
        self.check("another")
        self.plan.write_text("changed plan\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)
        self.plan.write_bytes(b"atlas plan\n")
        self.assertFalse(self.check().coverage)
        text = (self.run / context.RECORD_NAME).read_text(encoding="utf-8")
        rows = [json.loads(line.split(": ", 1)[1]) for line in text.splitlines() if line.startswith("GO-AHEAD:")]
        self.assertEqual({row["submission"] for row in rows}, {"submission", "another"})
        self.assertEqual(len(rows), 2)

    def test_posted_clean_result_is_carried_forward_without_reading_current_files(self):
        self.assertFalse(self.check().coverage)
        self.record_posting()
        self.plan.unlink()
        self.memory.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("carried forward", result.report)

    def test_posted_move_is_reported_as_approved_over_and_passes(self):
        self.plan.write_text("changed plan\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)
        self.record_posting()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("clinician approved over moved places", result.report)
        self.assertIn(str(self.plan), result.report)

    def test_pre_check_posted_approval_is_named_counted_and_passes(self):
        self.record_posting(required=False)
        self.plan.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("approval predates the check", result.report)
        self.assertIn("pre-check approvals: 1", result.report)

    def test_new_posted_approval_cannot_use_the_pre_check_exemption(self):
        self.record_posting()
        self.assertTrue(self.complete().finding)

    def test_unposted_terminal_grade_keeps_whole_file_rechecking(self):
        self.check()
        self.memory.write_text("memory index\nnew pointer\n", encoding="utf-8")
        self.assertTrue(self.complete().coverage)

    def test_corrupt_saved_result_is_a_finding(self):
        self.check()
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace('"finding": false', '"finding": "false"'), encoding="utf-8")
        self.record_posting()
        self.assertTrue(self.complete().finding)

    def test_public_go_ahead_command_prints_every_added_line_and_exits_zero(self):
        self.memory.write_text("memory index\nnew pointer\nsecond pointer\n", encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), redirect_stdout(output):
            status = context.main([str(self.run), "--go-ahead", "submission"])
        self.assertEqual(status, 0, output.getvalue())
        self.assertIn("new pointer", output.getvalue())
        self.assertIn("second pointer", output.getvalue())

    def test_real_pre_post_grader_records_an_approved_move_as_incomplete(self):
        Run(self.run, posted=False)
        (self.run / "reread.md").unlink()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        claims = self.run / "heading-read.md"
        claims.write_text(claims.read_text(encoding="utf-8").replace("67d55228f3d5d679eb597e38d220b591803ef13085d57f1176ec0b6302c5fc8f", context.recorded_digest(self.run)), encoding="utf-8")
        self.plan.write_bytes(b"changed plan\n")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(
            approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)
        ), mock.patch.object(approval_record, "verify_shown_text", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)):
            approved = approval_record.approve(
                self.run, skill="discussion-reply", submission="submission",
                sources=(self.run / "response-maren.md",), grader_args=(str(self.run),),
                content_approved=True, clinician_reply="Approve over the changed plan.",
            )
        payload = json.loads((self.run / approval_record.RECORD).read_text(encoding="utf-8"))
        self.assertEqual(payload["items"][0]["pregrade_status"], "incomplete")
        self.assertIn(str(self.plan), approved.pregrade_report)
        approval_record.record_agent_posting(self.run, skill="discussion-reply", submission="submission")
        self.memory.unlink()
        self.assertFalse(self.complete().coverage)
        self.assertFalse(self.complete().finding)

    def test_approval_refuses_when_the_go_ahead_result_cannot_be_written(self):
        Run(self.run, posted=False)
        (self.run / "reread.md").unlink()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        claims = self.run / "heading-read.md"
        claims.write_text(claims.read_text(encoding="utf-8").replace("67d55228f3d5d679eb597e38d220b591803ef13085d57f1176ec0b6302c5fc8f", context.recorded_digest(self.run)), encoding="utf-8")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(Path, "replace", side_effect=OSError("synthetic write failure")), mock.patch.object(approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)), mock.patch.object(approval_record, "verify_shown_text", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)):
            with self.assertRaisesRegex(approval_record.ApprovalRecordError, "could not be written"):
                approval_record.approve(self.run, skill="discussion-reply", submission="submission", sources=(self.run / "response-maren.md",), grader_args=(str(self.run),), content_approved=True, clinician_reply="Approve the synthetic reply.")
        self.assertFalse((self.run / approval_record.RECORD).exists())

    def test_assignment_approval_and_upload_carry_forward_the_same_check(self):
        artifact = self.run / "submission.pptx"
        artifact.write_bytes(b"synthetic deck")
        self.plan.write_bytes(b"changed plan\n")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")):
            staged = assignment_submission.stage(self.run, artifact, artifact_approved=True)
        payload = json.loads((self.run / assignment_submission.RECORD).read_text(encoding="utf-8"))
        self.assertEqual(payload["pregrade_status"], "incomplete")
        assignment_submission.confirm(staged, uploaded_carriers=(artifact,), final_confirmation=True)
        self.plan.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("approved over", result.report)


class ScopedCompletionGraders(unittest.TestCase):
    def test_the_scoped_completion_graders_declare_the_same_row(self) -> None:
        self.assertEqual(
            set(context.COMPLETION_GRADERS),
            {
                "course-assignment",
                "discussion-post",
                "discussion-reply",
                "peer-critique",
                "practicum-case-study",
            },
        )
        for skill, module_name in context.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                self.assertIn(context.EXPECTED_ROW, module.EXPECTED_COMPLETION_CHECKS)

    def test_each_scoped_skill_runs_the_gate_before_drafting(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for skill in context.COMPLETION_GRADERS:
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("project_context.py", text)
                self.assertIn("--write", text)
                self.assertIn("--submission", text)

    def test_graders_and_claude_name_one_limits_object_without_copying_rows(self) -> None:
        root = Path(__file__).resolve().parent.parent
        readers = [
            root / "tools" / f"{module_name}.py"
            for module_name in context.COMPLETION_GRADERS.values()
        ]
        readers.append(root / "CLAUDE.md")
        readers.append(root / "skills" / "_shared" / "reference" / "sourcing.md")
        for path in readers:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("project_context.DECLARED_LIMITS", text)
                for key, reason in context.DECLARED_LIMITS:
                    if path.name != "sourcing.md":
                        self.assertNotIn(key, text)
                    self.assertNotIn(reason, text)

    def test_the_shared_draft_rule_points_at_an_existing_limits_row(self) -> None:
        root = Path(__file__).resolve().parent.parent
        text = (root / "skills" / "_shared" / "reference" / "sourcing.md").read_text(
            encoding="utf-8"
        )
        keys = dict(context.DECLARED_LIMITS)
        self.assertIn("agreement-is-a-reading", keys)
        self.assertIn("agreement-inherits-item-errors", keys)
        self.assertIn(
            "`project_context.DECLARED_LIMITS`, row `agreement-inherits-item-errors`", text
        )


if __name__ == "__main__":
    unittest.main()
