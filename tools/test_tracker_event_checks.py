"""One dispatcher owns the checks applied to a changed tracker record."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import tracker_event_checks as checks


def event(action: str, *, number: int = 1, body_changed: bool = False):
    document = {
        "action": action,
        "issue": {"number": number, "labels": []},
        "comment": {"body": "text"},
    }
    if body_changed:
        document["changes"] = {"body": {"from": "old text"}}
    return document


class TheEventDispatcherOwnsTheChangedRecordCheckSet(unittest.TestCase):
    def assert_selected(self, document, event_name, expected):
        self.assertEqual(
            [check.module for check in checks.select_checks(document, event_name)],
            expected,
        )

    def test_phi_is_advisory_while_a_refusing_check_controls_status(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            module = Path(command[1]).stem
            status = {"tracker_scan": 1, "tracker_branch_scope": 2}.get(module, 0)
            return subprocess.CompletedProcess(command, status, f"{module} report\n", "")

        with tempfile.TemporaryDirectory() as raw:
            event_path = Path(raw) / "event.json"
            summary = Path(raw) / "summary.md"
            event_path.write_text("{}", encoding="utf-8")

            status = checks.run_selected(
                event_path,
                "issue_comment",
                (checks.PHI, checks.BRANCH),
                runner=runner,
                summary_path=summary,
            )

            report = summary.read_text(encoding="utf-8")

        self.assertEqual(status, 2)
        self.assertEqual(len(calls), 2)
        self.assertIn("### Tracker PHI shape layer", report)
        self.assertIn("### Tracker branch scope", report)
        self.assertIn("--allow-no-corpus", calls[0][0])

    def test_each_summary_names_its_exit_posture_and_carries_stderr(self):
        def runner(command, **kwargs):
            module = Path(command[1]).stem
            status = {"tracker_scan": 1, "tracker_branch_scope": 2}[module]
            return subprocess.CompletedProcess(
                command,
                status,
                f"{module} stdout\n",
                f"{module} stderr\n",
            )

        with tempfile.TemporaryDirectory() as raw:
            event_path = Path(raw) / "event.json"
            summary = Path(raw) / "summary.md"
            event_path.write_text("{}", encoding="utf-8")

            checks.run_selected(
                event_path,
                "issue_comment",
                (checks.PHI, checks.BRANCH),
                runner=runner,
                summary_path=summary,
            )

            report = summary.read_text(encoding="utf-8")

        self.assertIn("### Tracker PHI shape layer: FINDING", report)
        self.assertIn("tracker_scan stderr", report)
        self.assertIn("### Tracker branch scope: DID NOT SCAN", report)
        self.assertIn("tracker_branch_scope stderr", report)

    def test_a_clean_phi_shape_heading_preserves_the_unchecked_names_warning(self):
        warning = "PATIENT NAMES ARE NOT CHECKED -- corpus layer unavailable\n"

        def runner(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, "shape findings: 0\n", warning)

        with tempfile.TemporaryDirectory() as raw:
            event_path = Path(raw) / "event.json"
            summary = Path(raw) / "summary.md"
            event_path.write_text("{}", encoding="utf-8")

            checks.run_selected(
                event_path,
                "issue_comment",
                (checks.PHI,),
                runner=runner,
                summary_path=summary,
            )

            report = summary.read_text(encoding="utf-8")

        self.assertIn("### Tracker PHI shape layer: CLEAN", report)
        self.assertIn("PATIENT NAMES ARE NOT CHECKED", report)
        self.assertNotIn("Tracker PHI scan coverage: CLEAN", report)

    def test_an_issue_comment_created_runs_the_shared_record_checks(self):
        self.assert_selected(
            event("created"),
            "issue_comment",
            [
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
            ],
        )

    def test_issue_open_and_body_edit_keep_the_filed_from_check(self):
        expected = [
            "tracker_scan",
            "tracker_branch_scope",
            "tracker_bodies",
            "tracker_coordinates",
            "tracker_measurements",
            "tracker_filed_from",
        ]
        self.assert_selected(event("opened"), "issues", expected)
        self.assert_selected(event("edited", body_changed=True), "issues", expected)

    def test_the_implementation_map_body_edit_adds_its_producer_stamp_check(self):
        self.assert_selected(
            event("edited", number=596, body_changed=True),
            "issues",
            [
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
                "tracker_filed_from",
                "map_scan",
            ],
        )


if __name__ == "__main__":
    unittest.main()
