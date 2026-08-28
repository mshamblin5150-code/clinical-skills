"""The recurring tracker scan runs at the public tracker event seam. Issue #260.

The workflow intentionally scans one changed record. Replaying the whole
historical surface would reproduce #264's already-triaged findings on every
comment and turn the check into a warning nobody reads.
"""

import re
import unittest
from pathlib import Path

import phi_scan
import tracker_merge_receipt


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tracker.yml"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
ISSUE_TRACKER = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"


def workflow_text():
    return WORKFLOW.read_text(encoding="utf-8")


class EveryChangedTrackerRecordTriggersTheShapeScan(unittest.TestCase):
    def test_the_workflow_exists_without_tabs(self):
        self.assertTrue(WORKFLOW.is_file())
        self.assertNotIn("\t", workflow_text())

    def test_issue_pull_request_comment_and_review_surfaces_are_named(self):
        text = workflow_text()
        for event in (
            "issues",
            "issue_comment",
            "pull_request_target",
            "pull_request_review",
            "pull_request_review_comment",
        ):
            with self.subTest(event=event):
                self.assertRegex(text, rf"(?m)^  {re.escape(event)}:")

    def test_create_and_edit_do_not_depend_on_a_later_push(self):
        text = workflow_text()
        expected = {
            "issues": ("opened", "edited", "labeled"),
            "issue_comment": ("created", "edited"),
            "pull_request_target": ("opened", "edited"),
            "pull_request_review": ("submitted", "edited"),
            "pull_request_review_comment": ("created", "edited"),
        }
        for event, actions in expected.items():
            with self.subTest(event=event):
                match = re.search(
                    rf"(?m)^  {re.escape(event)}:\r?\n    types: \[([^]]+)\]$",
                    text,
                )
                self.assertIsNotNone(match, f"no trigger block for {event}")
                block = match.group(1)
                for action in actions:
                    self.assertIn(action, block)

    def test_the_changed_event_is_the_only_harvest(self):
        text = workflow_text()
        self.assertIn("tracker_scan.py --github-event", text)
        self.assertIn("GITHUB_EVENT_PATH", text)
        self.assertNotIn("gh api", text)

    def test_a_bodyless_review_does_not_report_did_not_scan(self):
        self.assertRegex(
            workflow_text(),
            r"github\.event\.review\.body\s*!=\s*null",
        )

    def test_an_edit_that_changes_no_text_does_not_start_a_text_scan(self):
        text = workflow_text()
        self.assertIn("github.event.changes.title", text)
        self.assertIn("github.event.changes.body", text)

    def test_the_ci_run_names_and_accepts_its_dead_corpus_layer(self):
        text = workflow_text()
        self.assertRegex(text, r"(?m)^\s*name:\s*tracker PHI shape layer only\s*$")
        command = next(
            line for line in text.splitlines() if "tracker_scan.py --github-event" in line
        )
        self.assertIn(phi_scan.ALLOW_NO_CORPUS_FLAG, command)

    def test_pull_request_code_is_never_executed_by_the_privileged_event(self):
        text = workflow_text()
        self.assertIn("github.event.repository.default_branch", text)
        self.assertNotRegex(text, r"github\.event\.pull_request\.head")


class TheRulingIsWrittenBesideTheMaintainerWorkflow(unittest.TestCase):
    def test_claude_md_names_the_event_trigger_and_incremental_boundary(self):
        section = CLAUDE_MD.read_text(encoding="utf-8").partition(
            "### Tracker scan"
        )[2].partition("\n### ")[0]
        self.assertIn("tracker event", section.lower())
        self.assertIn("changed record", section.lower())
        self.assertIn("shape layer", section.lower())
        self.assertIn("corpus layer", section.lower())


class TheFileIsValidYaml(unittest.TestCase):
    def test_it_parses_when_the_optional_parser_is_available(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML absent; the text tests are the floor")
        self.assertIsInstance(yaml.safe_load(workflow_text()), dict)


class ACompletedMergePublishesAnImmutableTicketReceipt(unittest.TestCase):
    def test_the_workflow_listens_for_a_closed_pull_request(self):
        text = workflow_text()
        self.assertRegex(
            text,
            r"(?m)^  pull_request_target:\r?\n    types: \[[^]]*closed[^]]*\]$",
        )
        self.assertIn("github.event.pull_request.merged == true", text)

    def test_trusted_main_builds_and_publishes_the_receipt_plan(self):
        text = workflow_text()
        self.assertIn("tracker_merge_receipt.py", text)
        self.assertIn("gh pr view", text)
        self.assertIn("gh issue comment", text)
        self.assertIn("issues: write", text)
        self.assertIn("github.event.repository.default_branch", text)

    def test_tracker_citations_are_scoped_at_the_publication_event(self):
        text = workflow_text()
        self.assertIn("--github-event", text)
        self.assertIn("--event-name", text)
        self.assertIn("Dated main-branch scope for tracker citations", text)

    def test_the_maintainer_rule_names_both_sides_of_the_state_change(self):
        text = ISSUE_TRACKER.read_text(encoding="utf-8")
        self.assertIn("Branch state:", text)
        self.assertIn("not on `main` as of", text)
        self.assertIn("Part of #", text)
        self.assertIn("merge receipt", text.lower())
        self.assertIn("do not rewrite", text.lower())

    def test_receipts_are_published_before_the_planners_status_is_enforced(self):
        step = workflow_text().partition(
            "Publish one immutable receipt per explicitly referenced ticket"
        )[2].partition("\n      #")[0]
        status = step.index("$status = $LASTEXITCODE")
        publication = step.index("gh issue comment", status)
        enforcement = step.index("exit $status", publication)

        self.assertLess(status, publication)
        self.assertLess(publication, enforcement)


class PullRequestsGradeTheReceiptPlanBeforeMerge(unittest.TestCase):
    def test_the_advisory_step_uses_the_open_pr_entry_point(self):
        checks = (REPO_ROOT / ".github" / "workflows" / "checks.yml").read_text(
            encoding="utf-8"
        )
        step = checks.partition("Receipt plan scan, advisory")[2].partition("\n      - name:")[0]

        self.assertIn("continue-on-error: true", step)
        self.assertGreaterEqual(checks.count("pull-request.json"), 2)
        self.assertIn("tracker_merge_receipt.py --check-plan", step)
        self.assertIn("if: github.event_name == 'pull_request'", step)

    def test_documented_nouns_and_own_line_rule_come_from_module_constants(self):
        texts = [
            ISSUE_TRACKER.read_text(encoding="utf-8"),
            CLAUDE_MD.read_text(encoding="utf-8"),
        ]
        for noun in tracker_merge_receipt.UNIT_NOUNS:
            for text in texts:
                with self.subTest(noun=noun):
                    self.assertIn(noun, text)
        for alternative in tracker_merge_receipt.REFERENCE_ALTERNATIVES:
            documented_form = alternative.example.partition("#")[0].strip()
            for text in texts:
                with self.subTest(form=alternative.name):
                    self.assertIn(documented_form, text)
        for text in texts:
            self.assertIn("owns its line", text)


if __name__ == "__main__":
    unittest.main()
