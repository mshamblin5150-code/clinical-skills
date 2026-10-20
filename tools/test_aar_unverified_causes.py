"""ADR0396 cause provenance and not-shown candidates through the public AAR CLI."""
# phi-scan: synthetic
import artifact_lock_test_support
from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest import mock

import aar_scan
import test_aar_reversal_candidates as fixtures

WARNING = "**Cause unverified:** the review's reader could not see the tool output this cause rests on; reread the run's transcript before building on it."


class CauseRecords(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ReversalCandidates()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        patch = mock.patch.object(aar_scan, "UNVERIFIED_CAUSE_CUTOFF",
                                  datetime(2020, 1, 1, tzinfo=timezone.utc), create=True)
        patch.start()
        self.addCleanup(patch.stop)

    def correction(self, classifier="shown - user-1", final="shown - user-1", reason=None):
        self.fixture.extract()
        self.fixture.correction()
        lines = self.fixture.record.read_text(encoding="utf-8").splitlines()
        self.fixture.record.write_text("\n".join(line for line in lines
                                      if not line.startswith(("CLASSIFIER-CAUSE:", "CAUSE:"))) + "\n", encoding="utf-8")
        if classifier is not None:
            self.fixture.append(f"CLASSIFIER-CAUSE: {classifier}\n")
        if final is not None:
            self.fixture.append(f"CAUSE: {final}\n")
        if reason is not None:
            self.fixture.append(f"CAUSE-OVERRULE: {reason}\n")

    def grade(self):
        return self.fixture.command("--show")

    def ticket(self, classifier="unverified - user-1", reason=None):
        self.correction(classifier=classifier, final="unverified - user-1", reason=reason)
        self.landing = "https://github.com/synthetic/repository/issues/71"
        source = self.fixture.record.read_text(encoding="utf-8")
        self.fixture.record.write_text(source.replace("DISPOSITION: memory-write", "DISPOSITION: tracker-ticket")
                                       .replace("LANDING: recorded correction", "LANDING: " + self.landing), encoding="utf-8")
        self.folder = self.fixture.run / "aar" / "publications"
        self.folder.mkdir()
        self.body = self.folder / "cause.md"
        self.body_text = "**Filed from:** the after-action review of a discussion-post run (synthetic), 2026-10-20.\n\n" + WARNING + "\n\nThe workflow needs review.\n"
        self.body.write_text(self.body_text, encoding="utf-8")
        self.initial_transcript = self.fixture.transcript.read_text(encoding="utf-8")
        self.extracted = datetime.fromisoformat(self.fixture.fields["EXTRACTED-AT"].replace("Z", "+00:00"))

    def evidence(self, command="gh issue create --title 'synthetic' --body-file cause.md --label grilling",
                 harness="claude", cwd=True, success=True, output=None, offset=2):
        self.fixture.transcript.write_text(self.initial_transcript, encoding="utf-8")
        for index, (source, result) in enumerate((("gh issue list --state all --search synthetic", "[]"),
                                                  (command, self.landing if output is None else output))):
            timestamp = (self.extracted + timedelta(seconds=1 if index == 0 else offset)).isoformat()
            folder = str(self.folder) if cwd else None
            if harness == "codex":
                rows = [{"type": "event_msg", "timestamp": timestamp, "payload": {
                    "type": "item_completed", "item": {"type": "CommandExecution", "status": "completed",
                    "exit_code": 0 if success or index == 0 else 1, "command": source, "cwd": folder, "stdout": result}}}]
            else:
                rows = [{"type": "assistant", "timestamp": timestamp, "cwd": folder, "message": {"content": [
                    {"type": "tool_use", "name": "Bash", "id": f"call-{index}", "input": {"command": source}}]}},
                    {"type": "user", "timestamp": timestamp, "message": {"content": [
                    {"type": "tool_result", "tool_use_id": f"call-{index}", "is_error": not success if index else False, "content": result}]}}]
            with self.fixture.transcript.open("a", encoding="utf-8") as stream:
                stream.write("".join(json.dumps(row) + "\n" for row in rows))

    def test_warning_body_create_labels_and_both_harness_routes(self):
        self.ticket()
        for harness in ("claude", "codex"):
            for labels in ("--label grilling", "--label=bug,grilling", "-l bug -l grilling"):
                with self.subTest(harness=harness, labels=labels):
                    self.evidence("gh issue create --title 'synthetic' --body-file cause.md " + labels, harness)
                    with mock.patch.object(aar_scan.subprocess, "run", side_effect=AssertionError("never replay commands")):
                        status, report = self.grade()
                    self.assertEqual(status, 0, report)
                    self.assertEqual(report.count("round 1 unverified causes: 1"), 1)
                    call = aar_scan._successful_gh_commands((self.fixture.transcript,))[-1]
                    self.assertEqual(call.cwd, str(self.folder))
                    self.assertEqual(call.output.strip(), self.landing)
                    self.assertEqual(call.timestamp, self.extracted + timedelta(seconds=2))
            for labels in ("", "--label ready-for-agent", "--label grilling,ready-for-agent"):
                with self.subTest(harness=harness, labels=labels):
                    self.evidence("gh issue create --title 'synthetic' --body-file cause.md " + labels, harness)
                    status, report = self.grade()
                    self.assertEqual(status, 1, report)
                    self.assertIn("unverified-publication", report)

    def test_comment_requires_warning_but_no_new_issue_labels(self):
        self.ticket()
        self.landing += "#issuecomment-91"
        self.fixture.record.write_text(self.fixture.record.read_text(encoding="utf-8").replace(
            "LANDING: https://github.com/synthetic/repository/issues/71", "LANDING: " + self.landing), encoding="utf-8")
        self.evidence("gh issue comment 71 --body-file cause.md")
        self.assertEqual(self.grade()[0], 0)
        for body in (self.body_text.replace(WARNING, "Cause unverified: incomplete"),
                     self.body_text.replace("\n\n" + WARNING, "\n\nAn intervening paragraph.\n" + WARNING),
                     self.body_text.replace("**Filed from:**", "Origin:")):
            with self.subTest(body=body):
                self.body.write_text(body, encoding="utf-8")
                status, report = self.grade()
                self.assertEqual(status, 1, report)
                self.assertIn("unverified-publication", report)
        self.body.write_text(self.body_text, encoding="utf-8")
        self.assertEqual(self.grade()[0], 0)

    def test_body_file_relative_to_recorded_cwd_or_literal_cd_not_current_process(self):
        self.ticket()
        self.evidence(cwd=False)
        self.assertEqual(self.grade()[0], 1)
        self.evidence(f'cd "{self.folder.as_posix()}" && gh issue create --body-file cause.md --label grilling', cwd=False)
        self.assertEqual(self.grade()[0], 0)
        self.evidence(cwd=True)
        self.assertEqual(self.grade()[0], 0)
        self.body.unlink()
        self.assertEqual(self.grade()[0], 1)

    def test_failed_earlier_different_or_unknown_publication_never_proves_warning(self):
        self.ticket()
        for options in ({"success": False}, {"offset": -1}, {"output": self.landing + "#issuecomment-999"},
                        {"command": "gh issue create --title 'synthetic' --body inline --label grilling"},
                        {"command": "gh issue create --title synthetic --body-file cause.md --label grilling"},
                        {"command": "gh issue view 71"}):
            with self.subTest(options=options):
                self.evidence(**options)
                self.assertEqual(self.grade()[0], 1)
        self.evidence()
        self.assertEqual(self.grade()[0], 0)

    def test_skill_file_uses_the_same_unverified_ticket_route(self):
        self.ticket()
        source = self.fixture.record.read_text(encoding="utf-8")
        self.fixture.record.write_text(source.replace("DISPOSITION: tracker-ticket", "DISPOSITION: skill-file"), encoding="utf-8")
        self.evidence()
        self.assertEqual(self.grade()[0], 0)
        self.body.write_text(self.body_text.replace(WARNING, ""), encoding="utf-8")
        self.assertIn("unverified-publication", self.grade()[1])

    def test_codex_shared_output_cannot_bind_a_sibling_body_to_the_landing(self):
        self.ticket()
        (self.folder / "bad.md").write_text(self.body_text.replace(WARNING, ""), encoding="utf-8")
        good = "gh issue create --body-file cause.md --label grilling"
        bad = "gh issue create --body-file bad.md --label grilling"
        for commands in ([good, bad], [good, "echo " + self.landing]):
            with self.subTest(commands=commands):
                self.evidence(commands, "codex")
                with mock.patch.object(aar_scan.subprocess, "run", side_effect=AssertionError("never replay")):
                    status, report = self.grade()
                self.assertEqual(status, 1, report)
                self.assertIn("unverified-publication", report)
                # The historical landing/search evidence keeps its original recognition.
                self.assertNotIn("missing-gh-call", report)
                self.assertNotIn("missing-landing-search", report)
        self.evidence([good], "codex")
        self.assertEqual(self.grade()[0], 0)

    def test_compound_result_is_not_a_single_publication_but_literal_cd_is(self):
        self.ticket()
        good = "gh issue create --body-file cause.md --label grilling"
        for command in (good + " && echo " + self.landing,
                        "echo ready; " + good,
                        good + " ; gh issue create --body-file absent.md --label grilling"):
            with self.subTest(command=command):
                self.evidence(command)
                status, report = self.grade()
                self.assertEqual(status, 1, report)
                self.assertIn("unverified-publication", report)
        self.evidence(f'cd "{self.folder.as_posix()}" && ' + good, cwd=False)
        self.assertEqual(self.grade()[0], 0)

    def test_unknown_extraction_moment_is_active_and_not_an_historical_exemption(self):
        self.correction(classifier=None, final=None)
        path = aar_scan.extract_path(self.fixture.run, "synthetic")
        # Format 1 legitimately predates the timestamp field; preserve its genuine entries.
        header = [line for line in path.read_text(encoding="utf-8").split("\n\n", 1)[0].splitlines()
                  if not line.startswith(("FORMAT:", "EXTRACTED-AT:"))]
        path.write_text("\n".join(header) + "\n\n" + "\n".join(
            "## ENTRY: " + entry.identifier for entry in self.fixture.entries) + "\n", encoding="utf-8")
        aar_scan.memory_measurement_path(self.fixture.run, "synthetic").unlink()
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("cause-line", report)
        self.assertNotIn("unverified causes: 0 (not graded", report)
        self.fixture.append("CLASSIFIER-CAUSE: shown - user-1\nCAUSE: shown - user-1\n")
        status, report = self.grade()
        self.assertEqual(status, 0, report)

    def test_rebuilt_report_has_one_cause_count_and_one_remainder(self):
        self.ticket()
        self.evidence()
        status, report = self.fixture.command("--memory-index", str(self.fixture.memory),
                                              "--extract", "--rebuild-round", "1")
        self.assertEqual(status, 0, report)
        self.assertEqual(report.count("round 1 unverified causes: 1"), 1)
        self.assertEqual(report.count("unread remainder "), 1)

    def test_damaged_extract_withholds_cause_checks_but_preserves_independent_review_finding(self):
        self.correction()
        self.fixture.append("\n## SUSTAIN: absent\nSUMMARY: Keep the established workflow.\n")
        path = aar_scan.extract_path(self.fixture.run, "synthetic")
        original = path.read_bytes()
        path.write_bytes(b"\xff")
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("contradictory-sustain-verdict", report)
        self.assertIn("unread remainder 1", report)
        self.assertIn("extract-dependent checks: not graded", report)
        self.assertNotIn("cause-line", report)
        path.write_bytes(original)
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("unknown-sustain-event", report)

    def test_shown_to_unverified_needs_a_reason_and_keeps_both_pointers(self):
        self.ticket(classifier="shown - user-1")
        self.evidence()
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("cause-overrule", report)
        self.fixture.append("CAUSE-OVERRULE: the claimed output is absent from the extract\n")
        self.assertEqual(self.grade()[0], 0)
        review = aar_scan.read_review(self.fixture.record)
        self.assertEqual(review.corrections[0].fields["CLASSIFIER-CAUSE"], "shown - user-1")
        self.assertEqual(review.corrections[0].fields["CAUSE"], "unverified - user-1")

    def test_before_and_exact_extraction_boundary_preserve_old_rounds(self):
        self.correction(classifier=None, final=None)
        (self.fixture.memory.parent / "correction.md").write_text(
            "# Corrected workflow\n", encoding="utf-8")
        self.fixture.memory.write_text("# Index\n- [Correction](correction.md) — synthetic workflow\n", encoding="utf-8")
        cutoff = datetime(2026, 10, 20, 16, 13, 19, tzinfo=timezone.utc)
        for check in ("cause-line", "cause-overrule", "unverified-disposition", "unverified-publication"):
            self.assertEqual(aar_scan.completion_checks.registry()["aar_scan:" + check], (cutoff, "extraction"))
        path = aar_scan.extract_path(self.fixture.run, "synthetic")
        original = path.read_text(encoding="utf-8")
        moment = self.fixture.fields["EXTRACTED-AT"]
        path.write_text(original.replace(moment, (cutoff - timedelta(microseconds=1)).isoformat()), encoding="utf-8")
        aar_scan.measure_memory(self.fixture.run, "synthetic", 1)
        with mock.patch.object(aar_scan, "UNVERIFIED_CAUSE_CUTOFF", cutoff):
            status, report = self.grade()
            self.assertEqual(status, 0, report)
        path.write_text(original.replace(moment, cutoff.isoformat()), encoding="utf-8")
        aar_scan.measure_memory(self.fixture.run, "synthetic", 1)
        with mock.patch.object(aar_scan, "UNVERIFIED_CAUSE_CUTOFF", cutoff):
            status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("cause-line", report)

    def test_missing_cause_refuses_and_shown_real_entry_passes(self):
        self.correction(classifier=None, final=None)
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("cause-line", report)
        self.fixture.append("CLASSIFIER-CAUSE: shown - user-1\nCAUSE: shown - user-1\n")
        status, report = self.grade()
        self.assertEqual(status, 0, report)
        self.assertIn("round 1 unverified causes: 0", report)

    def test_cause_pointer_is_same_round_real_entry_not_candidates(self):
        self.correction()
        original = self.fixture.record.read_text(encoding="utf-8")
        candidate = next(entry.identifier for entry in self.fixture.entries
                         if entry.kind == "reversal-candidates")
        for value in ("shown", "shown - absent", f"shown - {candidate}", "invented - user-1"):
            with self.subTest(value=value):
                self.fixture.record.write_text(original.replace("CAUSE: shown - user-1", "CAUSE: " + value), encoding="utf-8")
                status, report = self.grade()
                self.assertEqual(status, 1, report)
                self.assertIn("cause-line", report)
        self.fixture.record.write_text(original, encoding="utf-8")
        self.assertEqual(self.grade()[0], 0)

    def test_unverified_cannot_land_as_memory_or_check(self):
        self.correction(classifier="unverified - user-1", final="unverified - user-1")
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("unverified-disposition", report)
        self.assertIn("round 1 unverified causes: 1", report)
        source = self.fixture.record.read_text(encoding="utf-8")
        self.fixture.record.write_text(source.replace("DISPOSITION: memory-write", "DISPOSITION: check"), encoding="utf-8")
        self.assertIn("unverified-disposition", self.grade()[1])
        self.fixture.record.write_text(source.replace("unverified - user-1", "shown - user-1"), encoding="utf-8")
        self.assertEqual(self.grade()[0], 0)

    def test_classifier_unverified_cannot_be_promoted_to_shown(self):
        self.correction(classifier="unverified - user-1", final="shown - user-1")
        status, report = self.grade()
        self.assertEqual(status, 1, report)
        self.assertIn("cause-overrule", report)
        source = self.fixture.record.read_text(encoding="utf-8")
        self.fixture.record.write_text(source.replace("CLASSIFIER-CAUSE: unverified", "CLASSIFIER-CAUSE: shown"), encoding="utf-8")
        self.assertEqual(self.grade()[0], 0)

    def test_not_shown_is_a_reasoned_candidate_answer_counted_separately(self):
        self.fixture.extract("An observed reversal has no retained entry.\nA second candidate was not a correction.\n")
        self.fixture.append("\n## CANDIDATE: 1\nANSWER: not shown - no retained entry carries the reversal\n"
                            "\n## CANDIDATE: 2\nANSWER: not a correction - no later contradiction stood\n")
        status, report = self.grade()
        self.assertEqual(status, 0, report)
        self.assertIn("not a correction 1; not shown 1", report)
        self.assertEqual(report.count("unread remainder "), 1)
        source = self.fixture.record.read_text(encoding="utf-8")
        self.fixture.record.write_text(source.replace("not shown - no retained entry carries the reversal", "not shown - no"), encoding="utf-8")
        self.assertEqual(self.grade()[0], 1)


if __name__ == "__main__":
    unittest.main()
