"""Behavior tests for the project-context gate. #1395.

Every project, path, service, and payload is synthetic.

phi-scan: synthetic
"""

from __future__ import annotations

import hashlib
import importlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import project_context as context
import repo_root
import run_grader


class ProjectContextFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name).resolve()
        self.run = self.root / "run"
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
                    *header,
                    "CONFIRMED: 2026-09-23",
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

    def test_the_context_digest_is_over_sorted_place_item_hash_triples(self) -> None:
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
            "".join("\0".join(triple) + "\n" for triple in triples).encode("utf-8")
        ).hexdigest()
        self.assertEqual(context.recorded_digest(self.run), expected)

    def test_a_none_declaration_needs_a_reason_and_writes_none(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none - critique concerns a classmate's case\n"
            "CONFIRMED: 2026-09-23\n",
            encoding="utf-8",
        )

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.recorded_digest(self.run), "none")

    def test_none_without_a_reason_is_a_finding(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none\nCONFIRMED: 2026-09-23\n", encoding="utf-8"
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
            "CONFIRMED: 2026-09-23\n",
            "PROJECT-WAIVE: "
            f"{self.location} - file unavailable on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2026-09-23\n",
        ).replace(marker, f"## PLACE: {self.location}\nSTATE: unreadable\nDETAIL: moved\n")
        record.write_text(text, encoding="utf-8")
        self.plan.write_text("changed plan\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_a_waiver_for_a_readable_place_is_a_finding_and_not_counted(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8").replace(
            "CONFIRMED: 2026-09-23\n",
            "PROJECT-WAIVE: "
            f"{self.memory} - stale lead on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2026-09-23\n",
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
        for path in readers:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("project_context.DECLARED_LIMITS", text)
                for key, reason in context.DECLARED_LIMITS:
                    self.assertNotIn(key, text)
                    self.assertNotIn(reason, text)


if __name__ == "__main__":
    unittest.main()
