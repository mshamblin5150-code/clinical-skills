"""The recurring tracker scan runs at the public tracker event seam. Issue #260.

The workflow intentionally scans one changed record. Replaying the whole
historical surface would reproduce #264's already-triaged findings on every
comment and turn the check into a warning nobody reads.
"""

import re
import unittest
from pathlib import Path

import phi_scan
import test_module_sections
import tracker_branch_scope
import tracker_bodies
import tracker_freshness
import tracker_merge_receipt
import tracker_publish_hook


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tracker.yml"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
ISSUE_TRACKER = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"


def workflow_text():
    return WORKFLOW.read_text(encoding="utf-8")


class EveryTrackerGateHasASection(unittest.TestCase):
    """Derive a floor from three sources and require a ``CLAUDE.md`` section.

    A tracker gate reachable by none of the module-prefix, documented-command,
    or configured-invocation sources is outside this walk.
    """

    @staticmethod
    def module_prefix_contribution():
        return {path.stem for path in (REPO_ROOT / "tools").glob("tracker_*.py")}

    @staticmethod
    def documented_command_contribution():
        text = ISSUE_TRACKER.read_text(encoding="utf-8")
        return set(re.findall(r"tools/([a-z0-9_]+)\.py", text))

    @staticmethod
    def configured_invocation_contribution():
        text = workflow_text() + "\n" + SETTINGS.read_text(encoding="utf-8")
        return set(re.findall(r"tools/([a-z0-9_]+)\.py", text))

    @staticmethod
    def sectioned_modules(text=None):
        """Modules with a declared section, plus any whose title names them.

        #743: this normalized a section's **title** into a module name, which is
        right for the eighteen sections titled after their module and wrong for
        the house's dominant style. `map_scan` owns *Implementation map
        disagreement scan* and normalizes to nothing, so it passed here only
        because no source reached it -- a false alarm waiting for the day
        `tools/map_scan.py` is named in `docs/agents/issue-tracker.md` or in
        `tracker.yml`. The declared map in `test_module_sections` is the
        authority; the title fallback stays so a gate that is not a command
        module is still reachable.
        """

        source = CLAUDE_MD.read_text(encoding="utf-8") if text is None else text
        sections = re.split(r"(?m)^### ", source)[1:]
        titles = {
            section.partition("\n")[0].strip().lower().replace(" ", "_")
            for section in sections
        }
        if text is not None:
            return titles
        return titles | set(test_module_sections.DECLARED_SECTIONS)

    @staticmethod
    def missing_gates(contributions, sectioned):
        return set().union(*contributions.values()) - sectioned

    def source_contributions(self):
        return {
            "module prefix": self.module_prefix_contribution(),
            "documented command": self.documented_command_contribution(),
            "configured invocation": self.configured_invocation_contribution(),
        }

    def test_every_derived_gate_has_a_section(self):
        contributions = self.source_contributions()
        missing = self.missing_gates(contributions, self.sectioned_modules())
        report = "; ".join(
            f"{source}: {', '.join(sorted(modules)) or '(none)'}"
            for source, modules in contributions.items()
        )

        self.assertFalse(
            missing,
            f"derived tracker gates without CLAUDE.md sections: "
            f"{', '.join(sorted(missing))}; source contributions: {report}",
        )

    def test_each_declared_source_contributes_to_the_extraction(self):
        for source, modules in self.source_contributions().items():
            with self.subTest(source=source):
                self.assertTrue(modules, f"{source} contributed no tracker gate")

    def test_a_derived_gate_without_a_section_is_a_finding(self):
        contributions = {
            "module prefix": {"synthetic_tracker_gate"},
            "documented command": set(),
            "configured invocation": set(),
        }
        prose_with_only_a_cross_section_mention = (
            "### Existing scan\n\n"
            "This section mentions `tools/synthetic_tracker_gate.py` but does "
            "not give that gate its own section.\n"
        )

        self.assertEqual(
            self.missing_gates(
                contributions,
                self.sectioned_modules(prose_with_only_a_cross_section_mention),
            ),
            {"synthetic_tracker_gate"},
        )

    def test_a_section_does_not_require_a_limits_object(self):
        self.assertIn("tracker_freshness", self.sectioned_modules())
        self.assertFalse(hasattr(tracker_freshness, "NOT_REACHED"))


class TheTriggerCountIsBoundToTheModule(unittest.TestCase):
    """ADR 0083's prose said four triggers while its own table listed five.

    Nothing failed, because no check bound the sentence to the module. The count
    is derived here by driving every shape rather than by reading the file, so a
    sixth trigger has to move the record with it.
    """

    BLOB = "https://github.com/mshamblin5150-code/clinical-skills/blob/main/"
    RESOLVED = "docs/adr/0001-fixture-asserts-on-named-findings.md"

    @classmethod
    def grade_body(cls, body, labels=()):
        document = {
            "issue": {
                "number": 1,
                "labels": [{"name": name} for name in labels],
                "html_url": "https://example.invalid/1",
            },
            "comment": {"body": body, "html_url": "https://example.invalid/1#c"},
        }
        return tracker_branch_scope.grade(document, "issue_comment")

    def trigger_cases(self):
        near_miss = self.RESOLVED[:-3] + "-typo.md"
        return {
            "repo-relative Markdown link": (f"See [x](../{self.RESOLVED}).", ()),
            "unresolved path with a near miss": (f"See [x]({self.BLOB}{near_miss}).", ()),
            "unresolved path without a near miss": (
                f"See [x]({self.BLOB}tools/nothing_like_this_exists.py).",
                (),
            ),
            "self-declares completion": ("Implemented locally and verified.", ()),
            "in flight label": ("Nothing here trips a path rule.", ("in flight",)),
        }

    def test_every_declared_trigger_refuses_on_its_own(self):
        for name, (body, labels) in self.trigger_cases().items():
            with self.subTest(trigger=name):
                self.assertEqual(self.grade_body(body, labels).status, 1)

    def test_each_trigger_refuses_for_its_own_stated_reason(self):
        reports = {
            name: self.grade_body(body, labels).report
            for name, (body, labels) in self.trigger_cases().items()
        }

        self.assertEqual(len(set(reports.values())), len(reports))

    def test_the_instrument_is_live(self):
        """A resolved citation with no trigger must pass, or the cases prove nothing."""

        clean = self.grade_body(f"See [x]({self.BLOB}{self.RESOLVED}).")

        self.assertEqual(clean.status, 0)
        self.assertIn("no branch-state trigger", clean.report)

    def test_the_ratified_posture_table_lists_exactly_these_triggers(self):
        adr = next((REPO_ROOT / "docs" / "adr").glob("0083-*.md"))
        text = adr.read_text(encoding="utf-8")
        rows = re.findall(r"(?m)^\| (.+?) \| (?:no|yes) \| ", text)

        self.assertEqual(len(rows), len(self.trigger_cases()))
        # Keyed on the two claims, never on the bare phrase: the correction note
        # quotes `four triggers` in order to say it was wrong, and a substring
        # test failed on that quotation. `spelling_scan`'s mention-versus-use
        # rule and #153's `describing the rule broke the tool that checks the
        # rule`, arriving on this record while it was being repaired.
        self.assertNotIn("The module has four triggers", text)
        self.assertNotIn("The four triggers split", text)


class DeclaredLimitsAreBound(unittest.TestCase):
    CASES = (
        ("Tracker bodies", "tracker_bodies", tracker_bodies, True),
        ("Tracker branch scope", "tracker_branch_scope", tracker_branch_scope, False),
        ("Tracker merge receipt", "tracker_merge_receipt", tracker_merge_receipt, True),
        ("Tracker publish hook", "tracker_publish_hook", tracker_publish_hook, True),
    )

    @staticmethod
    def section(heading):
        text = CLAUDE_MD.read_text(encoding="utf-8")
        marker = f"### {heading}\n"
        _before, found, after = text.partition(marker)
        if not found:
            return ""
        return after.partition("\n### ")[0]

    def test_each_section_points_at_one_object_and_copies_no_row(self):
        for heading, module_name, module, module_points_at_object in self.CASES:
            with self.subTest(heading=heading):
                section = self.section(heading)
                module_doc = module.__doc__ or ""
                self.assertTrue(section, f"missing CLAUDE.md section {heading!r}")
                self.assertIn(f"{module_name}.NOT_REACHED", section)
                if module_points_at_object:
                    self.assertIn("NOT_REACHED", module_doc)
                for key, reason in module.NOT_REACHED:
                    self.assertNotIn(key, section)
                    self.assertNotIn(reason, section)
                    if module_points_at_object:
                        self.assertNotIn(key, module_doc)
                        self.assertNotIn(reason, module_doc)
                    self.assertGreater(len(reason.split()), 8)


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

    def test_changed_bodies_run_the_body_shape_scan_and_report_coverage(self):
        text = workflow_text()
        step = text.partition("Changed tracker body integrity")[2].partition(
            "\n      - name:"
        )[0]

        self.assertIn("tracker_bodies.py --github-event", step)
        self.assertIn("GITHUB_EVENT_PATH", step)
        self.assertIn("GITHUB_EVENT_NAME", step)
        self.assertIn("GITHUB_STEP_SUMMARY", step)
        self.assertIn("### Tracker body integrity", step)
        self.assertIn("github.event.changes.body", step)
        for action in ("opened", "created", "submitted", "edited"):
            self.assertIn(f"github.event.action == '{action}'", step)
        self.assertNotIn("github.event.action != 'edited'", step)
        self.assertNotIn("github.event.action == 'labeled'", step)
        self.assertNotIn("gh api", step)

    def test_the_body_shape_workflow_uses_the_public_event_mode(self):
        self.assertTrue(hasattr(tracker_bodies, "load_github_event"))

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
