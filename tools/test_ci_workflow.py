"""The CI workflow says what CLAUDE.md says it says. Issue #86.

**Two tiers, and the split is a dependency decision rather than a taste one.**
`tools/` is stdlib only and #86's whole cost argument for CI depends on that
staying true, so nothing here may require PyYAML.

- **The floor reads the workflow as text and runs everywhere.** It pins the
  four things that appear in both this file and the prose a reader opens --
  the runner, the Python version, the test command, and the fact that the PHI
  step reports its own coverage -- so one cannot go stale alone. That is #143,
  aimed at a file that is not prose.
- **`TheFileIsValidYaml` parses, when PyYAML happens to be importable**, and
  skips when it is not. It is the one guard that matters *before* the push: a
  syntax error means GitHub declines to run the workflow, so the PR page shows
  **no failing check at all** rather than a red one -- the silent-absence
  failure this whole ticket is about, arriving through the mechanism built to
  fix it. No test inside the job could ever report that, because the job would
  not exist.

**What neither tier reaches.** On a machine with no PyYAML the tab test is all
that stands between a malformed workflow and a silent merge, and neither tier
can tell you the job passed -- only that it would run the right command if it
ran. The first push is still the only end-to-end check.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "checks.yml"
TRACKER_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tracker.yml"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

#: The one command CLAUDE.md tells a maintainer to run. If CI runs a different
#: one, a green check answers a question nobody asked.
SUITE_COMMAND = "python -m unittest discover -s tools -t tools"
THRESHOLD_COMMAND = "python tools/threshold_sheet.py --all"
THRESHOLD_STEP_NAME = "Threshold sheet gates, external evidence may not run"
MAP_COMMAND = "python tools/map_scan.py $harvest --advisory"
MAP_STEP_NAME = "Implementation map disagreement, advisory after merge"

RUNNER = "windows-latest"
PYTHON_VERSION = "3.14"


def workflow_text():
    return WORKFLOW.read_text(encoding="utf-8")


def tracker_workflow_text():
    return TRACKER_WORKFLOW.read_text(encoding="utf-8")


TRACKER_EVENTS = {
    "issues",
    "issue_comment",
    "pull_request_target",
    "pull_request_review",
    "pull_request_review_comment",
}


def tracker_branch_scope_step(text):
    lines = text.splitlines()
    command = next(i for i, line in enumerate(lines) if "tracker_branch_scope.py" in line)
    start = max(i for i, line in enumerate(lines[: command + 1]) if re.match(r"^\s*- name:", line))
    end = next(
        (
            i
            for i, line in enumerate(lines[command + 1 :], command + 1)
            if re.match(r"^(?:      - |  [A-Za-z0-9_-]+:)", line)
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


class TheWorkflowExists(unittest.TestCase):
    def test_the_file_is_where_github_looks_for_it(self):
        self.assertTrue(WORKFLOW.is_file(), f"no workflow at {WORKFLOW}")

    def test_it_contains_no_tab_characters(self):
        """YAML forbids tabs for indentation, and a tab is the commonest way to
        write a file GitHub then silently refuses to run. This is not a parser
        and does not pretend to be one -- see the module docstring."""
        text = workflow_text()
        offenders = [n for n, line in enumerate(text.splitlines(), 1) if "\t" in line]
        self.assertEqual(offenders, [], f"tab characters on lines {offenders}")


class TrackerBranchScopeCoversEveryPublicationEvent(unittest.TestCase):
    def test_the_text_floor_pins_all_five_events(self):
        step = tracker_branch_scope_step(tracker_workflow_text())

        for event in TRACKER_EVENTS:
            with self.subTest(event=event):
                self.assertIn(f"github.event_name == '{event}'", step)

    def test_the_text_floor_pins_the_step_summary(self):
        step = tracker_branch_scope_step(tracker_workflow_text())

        self.assertIn("GITHUB_STEP_SUMMARY", step)
        self.assertNotIn("merge-receipts", step)


class TheJobRunsWhatTheDocsRun(unittest.TestCase):
    """#143's shape, applied to a file that is not prose.

    A workflow quietly running a narrower command than the one documented is
    worse than no workflow: the checkmark is real, and it answers for less than
    a reader thinks.
    """

    def test_the_suite_command_is_the_documented_one(self):
        self.assertIn(SUITE_COMMAND, workflow_text())

    def test_claude_md_documents_that_same_command(self):
        self.assertIn(SUITE_COMMAND, CLAUDE_MD.read_text(encoding="utf-8"))

    def test_nothing_is_installed(self):
        """#86's cost argument in one assertion. Three tools here need PyMuPDF,
        none of them at module scope, so a suite-only job resolves nothing --
        no package manager and no lockfile, exactly as CLAUDE.md claims. A
        ``pip install`` line here would falsify that sentence silently."""
        self.assertNotIn("pip install", workflow_text())


class TheJobMatchesWhatIsWrittenDown(unittest.TestCase):
    def test_the_runner_is_the_one_claude_md_names(self):
        self.assertIn(RUNNER, workflow_text())
        self.assertIn(RUNNER, CLAUDE_MD.read_text(encoding="utf-8"))

    def test_the_python_version_is_the_one_claude_md_names(self):
        self.assertRegex(workflow_text(), rf"python-version:\s*['\"]?{re.escape(PYTHON_VERSION)}")
        self.assertIn(PYTHON_VERSION, CLAUDE_MD.read_text(encoding="utf-8"))

    def test_the_python_version_is_quoted(self):
        """``3.10`` unquoted is the float 3.1, which is a real and famous way to
        run a Python nobody asked for. Quoting is cheap and 3.14 will not be the
        last version written here."""
        self.assertRegex(workflow_text(), r"python-version:\s*['\"]")


class BothMergeRoutesAreCovered(unittest.TestCase):
    """#86's subject. `main` is reached two ways here and a guard on one is not
    a guard.

    ``03f5adf`` merged #142 with ``git merge --no-ff`` locally and then
    ``git push origin main``, so the GitHub merge button was never in the path.
    A ``pull_request`` trigger alone would have watched a route that merge did
    not take.
    """

    def test_it_runs_on_a_push_to_main(self):
        text = workflow_text()
        self.assertRegex(text, r"(?s)push:.*branches:.*main")

    def test_it_runs_on_a_pull_request(self):
        self.assertRegex(workflow_text(), r"(?m)^\s*pull_request:")

    def test_it_can_be_run_by_hand(self):
        """A merge that has already landed is the one moment somebody wants to
        re-run the check against a tree neither parent had."""
        self.assertRegex(workflow_text(), r"(?m)^\s*workflow_dispatch:")


class ImplementationMapGateRunsWhereReconciliationIsOwed(unittest.TestCase):
    def map_step(self):
        text = workflow_text()
        return text.partition(f"- name: {MAP_STEP_NAME}")[2].partition(
            "\n      - name:"
        )[0]

    def test_the_step_is_pinned_to_push_and_manual_runs(self):
        step = self.map_step()
        self.assertTrue(step, "implementation-map step is absent")
        self.assertIn(
            "if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'",
            step,
        )
        self.assertNotIn("pull_request", step.partition("run:")[0])

    def test_it_harvests_the_whole_issue_surface_into_runner_temp(self):
        step = self.map_step()
        self.assertIn("RUNNER_TEMP", step)
        self.assertIn("issues?state=all&per_page=100", step)
        self.assertIn("gh api --paginate", step)

    def test_the_tool_owns_the_advisory_conversion(self):
        step = self.map_step()
        self.assertIn(MAP_COMMAND, step)
        self.assertNotIn("continue-on-error", step)

    def test_the_report_reaches_the_step_summary(self):
        self.assertIn("GITHUB_STEP_SUMMARY", self.map_step())

    def test_the_job_can_read_issues(self):
        self.assertRegex(workflow_text(), r"(?m)^\s*issues:\s*read\s*$")

    def test_claude_documents_the_same_command(self):
        self.assertIn(MAP_COMMAND, CLAUDE_MD.read_text(encoding="utf-8"))


class ClosingKeywordSurfacesAreCovered(unittest.TestCase):
    """#183: PR text and the landed merge message are different artifacts."""

    def test_pull_request_metadata_and_commits_are_scanned(self):
        text = workflow_text()
        self.assertIn("gh pr view", text)
        self.assertIn("--json title,body,commits", text)
        self.assertIn("pull-request.json", text)
        self.assertIn("closing_keyword_scan.py --github-json $pr", text)
        self.assertRegex(text, r"(?m)^\s*pull-requests:\s*read\s*$")

    def test_an_edited_pull_request_is_rescanned(self):
        self.assertRegex(
            workflow_text(),
            r"(?s)pull_request:.*?types:[^\n]*\bedited\b",
        )

    def test_every_commit_message_in_a_push_is_scanned(self):
        text = workflow_text()
        self.assertIn("git log --format=%B", text)
        self.assertIn("$env:BEFORE_SHA..$env:GITHUB_SHA", text)
        self.assertRegex(text, r"(?m)^\s*fetch-depth:\s*0\s*$")
        self.assertRegex(text, r"closing_keyword_scan\.py\s+-")

    def test_pull_request_findings_fail_the_check(self):
        text = workflow_text()
        self.assertRegex(
            text,
            r"(?s)- name: Closing keyword scan, pull request.*?"
            r"if: github\.event_name == 'pull_request'.*?"
            r"python tools/closing_keyword_scan\.py --github-json \$pr",
        )
        pull_request_step = text.partition(
            "- name: Closing keyword scan, pull request"
        )[2].partition("\n      - name:")[0]
        self.assertNotIn("continue-on-error", pull_request_step)

    def test_post_merge_push_findings_stay_advisory(self):
        self.assertRegex(
            workflow_text(),
            r"(?s)- name: Closing keyword scan, advisory push or manual run.*?"
            r"if: github\.event_name != 'pull_request'.*?"
            r"continue-on-error:\s*true.*?closing_keyword_scan\.py\s+-",
        )

    def test_claude_md_documents_the_same_surfaces(self):
        section = CLAUDE_MD.read_text(encoding="utf-8").partition(
            "### Closing keyword scan"
        )[2].partition("\n### ")[0]
        self.assertTrue(section.strip(), "no Closing keyword scan section in CLAUDE.md")
        for surface in ("commit-msg", "title", "body", "merge message"):
            with self.subTest(surface=surface):
                self.assertIn(surface, section)


class ThePhiStepCannotReadAsCoverage(unittest.TestCase):
    """#86 decision 2, and the trap the ticket names as its sharpest risk:

        *A green check on a PHI scan that cannot see the corpus is worse than
        no check, because it reads as coverage.*

    ``scratch/`` is gitignored PHI and must never reach a runner, so in CI the
    corpus layer is dead on every run that will ever happen here. The answer
    ruled on was not to drop the scan but to make the job state its own
    coverage -- and to derive that statement from the scanner rather than type
    it into YAML, where nothing would re-derive it.
    """

    def test_the_job_prints_the_layer_report(self):
        self.assertIn("phi_scan.py --layers", workflow_text())

    def test_the_layer_report_reaches_the_step_summary(self):
        """The log is a place nobody opens; the summary is the page attached to
        the checkmark itself."""
        text = workflow_text()
        self.assertIn("GITHUB_STEP_SUMMARY", text)

    def test_the_scan_itself_still_runs(self):
        """The shape layer is not worthless -- working #64 it caught a real date
        of birth copied out of a note into a staged file, in a worktree where
        the corpus layer was already dead."""
        self.assertRegex(workflow_text(), r"phi_scan\.py --all")

    def test_the_scan_step_carries_the_no_corpus_flag(self):
        """Since #93 an absent corpus is exit 2, and in CI it is absent on every
        run that will ever happen -- so without this flag the step is red
        forever, and a check that can never be green checks nothing.

        Pinned here because the failure is invisible until a push: dropping the
        flag breaks nothing locally, where the corpus is present, and the first
        thing that notices is a red `main`. That is ADR 0002's own *the first
        push is still the only end-to-end check*, so the flag needs a test on
        the side where it can be seen.
        """
        import phi_scan
        step = [
            line for line in workflow_text().splitlines()
            if "phi_scan.py --all" in line and "--layers" not in line
        ]
        self.assertEqual(len(step), 1, "expected exactly one scanning phi step")
        self.assertIn(phi_scan.ALLOW_NO_CORPUS_FLAG, step[0])

    def test_the_yaml_does_not_second_guess_the_exit_status(self):
        """#93 ruled the exemption belongs in the scanner's vocabulary, not in
        control flow here. Branching on the scanner's exit code in this file
        would be a judgment about `phi_scan` that `phi_scan` does not make and
        nothing re-derives -- the same objection the layer-report step exists to
        answer, one step over.

        **Comment lines are stripped, and that is not tidiness.** The first
        version was a substring search over the whole file, and it failed on the
        comment above the step -- prose that names the construct in order to
        reject it. That is `spelling_scan.py`'s mention-versus-use distinction
        and the pragma's own-line rule arriving uninvited a third time: a file
        explaining a rule should not have to break it to say what it does.
        """
        lines = workflow_text().splitlines()
        scan_line = next(
            index
            for index, line in enumerate(lines)
            if "phi_scan.py --all" in line and "--layers" not in line
        )
        step_start = max(
            index
            for index, line in enumerate(lines[: scan_line + 1])
            if re.match(r"^\s*- name:", line)
        )
        step_end = next(
            (
                index
                for index, line in enumerate(lines[scan_line + 1 :], scan_line + 1)
                if re.match(r"^\s*- name:", line)
            ),
            len(lines),
        )
        live_step = [
            line
            for line in lines[step_start:step_end]
            if line.strip() and not line.strip().startswith("#")
        ]
        self.assertNotIn("LASTEXITCODE", "\n".join(live_step))

    def test_the_job_name_carries_the_caveat(self):
        """The **job** name is the string on the PR check list. It is the only
        part of this a reader who never opens the run will ever see, so the
        caveat has to survive there and not only in the step.

        Asserted as its own line rather than by a pattern over the file: the
        first version matched ``name:.*shape layer`` anywhere, which the step
        name below satisfies on its own -- so deleting the job name left the
        test green on the one string the whole trap ruling rests on."""
        self.assertRegex(workflow_text(), r"(?m)^\s*name:\s*suite \+ PHI shape layer\s*$")

    def test_the_step_name_says_the_corpus_layer_could_not_run(self):
        """The step name is what sits beside the scan in the log, so it carries
        the reason the job name has no room for."""
        self.assertRegex(
            workflow_text(),
            r"(?m)^\s*- name:\s*PHI shape layer only, corpus layer cannot run in CI\s*$",
        )


class ThresholdSheetsAreGradedAtTheMerge(unittest.TestCase):
    """#190: a commit-refusing sheet gate must also run on the merge tree."""

    def threshold_step(self):
        lines = workflow_text().splitlines()
        step_start = next(
            index
            for index, line in enumerate(lines)
            if line.strip() == f"- name: {THRESHOLD_STEP_NAME}"
        )
        step_end = next(
            (
                index
                for index, line in enumerate(lines[step_start + 1 :], step_start + 1)
                if re.match(r"^\s*- name:", line)
            ),
            len(lines),
        )
        return "\n".join(
            line
            for line in lines[step_start:step_end]
            if line.strip() and not line.strip().startswith("#")
        )

    def test_the_job_runs_the_threshold_sheet_cli(self):
        self.assertEqual(self.threshold_step().count(THRESHOLD_COMMAND), 1)

    def test_claude_md_documents_that_same_command(self):
        section = CLAUDE_MD.read_text(encoding="utf-8").partition(
            "### Continuous integration"
        )[2].partition("\n### ")[0]
        self.assertTrue(section.strip(), "no Continuous integration section in CLAUDE.md")
        self.assertIn(THRESHOLD_COMMAND, section)

    def test_the_gate_report_reaches_the_step_summary(self):
        step = self.threshold_step()
        self.assertIn("### Threshold sheet gate coverage", step)
        self.assertRegex(step, r"Out-File .*GITHUB_STEP_SUMMARY")


class TheFileIsValidYaml(unittest.TestCase):
    """The one guard that has to run *before* the push, and the only one that
    cannot usefully run inside the job.

    A syntax error means GitHub declines to run the workflow, so the PR page
    shows **no failing check at all** rather than a red one. A test inside the
    job could never report that -- the job would not exist. So this is the half
    of the guard that belongs on the machine the commit is made from.

    **PyYAML is optional and stays optional.** `tools/` is stdlib only and #86's
    cost argument depends on that, so the import is inside the test and its
    absence skips rather than fails. That means this validates on the
    maintainer's machine, where the commit happens, and skips on the runner,
    where it would be circular anyway. The tests above are the floor that runs
    everywhere.
    """

    def load(self):
        try:
            import yaml
        except ImportError:  # pragma: no cover - depends on the machine
            self.skipTest("PyYAML absent; the text tests above are the floor")
        return yaml.safe_load(workflow_text())

    def test_it_parses(self):
        self.assertIsInstance(self.load(), dict)

    def triggers(self, doc):
        """YAML 1.1 reads a bare ``on`` as the boolean true, so the trigger block
        arrives under the key ``True``. Every GitHub workflow in the world has
        this; it is worth naming rather than rediscovering."""
        return doc.get("on", doc.get(True))

    def test_the_triggers_survive_a_parse(self):
        self.assertEqual(
            sorted(self.triggers(self.load())),
            ["pull_request", "push", "workflow_dispatch"],
        )

    def test_the_job_is_shaped_the_way_the_text_tests_assume(self):
        job = self.load()["jobs"]["suite"]
        self.assertEqual(job["runs-on"], RUNNER)
        commands = " ".join(step.get("run", "") for step in job["steps"])
        self.assertIn(SUITE_COMMAND, commands)

    def test_the_python_version_survives_as_a_string(self):
        """Unquoted it would arrive as a float, which is how `3.10` becomes 3.1
        in somebody else's repository."""
        steps = self.load()["jobs"]["suite"]["steps"]
        versions = [
            step["with"]["python-version"] for step in steps if "python-version" in step.get("with", {})
        ]
        self.assertEqual(versions, [PYTHON_VERSION])

    def test_the_tracker_if_survives_with_all_five_events(self):
        try:
            import yaml
        except ImportError:  # pragma: no cover - depends on the machine
            self.skipTest("PyYAML absent; the text tests above are the floor")
        document = yaml.safe_load(tracker_workflow_text())
        step = next(
            row
            for row in document["jobs"]["changed-record"]["steps"]
            if "tracker_branch_scope.py" in row.get("run", "")
        )

        for event in TRACKER_EVENTS:
            with self.subTest(event=event):
                self.assertIn(f"github.event_name == '{event}'", step["if"])
        self.assertIn("GITHUB_STEP_SUMMARY", step["run"])


class TheWorkflowIsAdvisory(unittest.TestCase):
    """#86 decision 4. A red run reports and blocks nothing.

    **Nothing in this file can enforce that, and that is the point of the
    test.** Blocking lives in branch protection, which is a repository setting
    outside the tree -- so this asserts only that the workflow does not quietly
    describe itself as required, and CLAUDE.md carries the ruling.
    """

    def test_claude_md_records_the_advisory_ruling(self):
        """Anchored on the CI section rather than on the word.

        The first version asserted only ``"advisory" in CLAUDE.md.lower()``,
        and that word is already in this file three times over -- the mirror
        scanner, the spelling scanner and the hook. It passed with the whole
        *Continuous integration* section deleted, which is #86's own recorded
        defect: *a test asserted that "one" and "finding" appear in the row,
        satisfied by the word "none"*."""
        text = CLAUDE_MD.read_text(encoding="utf-8")
        section = text.partition("### Continuous integration")[2].partition("\n### ")[0]
        self.assertTrue(section.strip(), "no Continuous integration section in CLAUDE.md")
        self.assertIn("Advisory", section)
        self.assertIn("required status check", section)

    def test_the_adr_exists(self):
        adrs = list((REPO_ROOT / "docs" / "adr").glob("*.md"))
        matching = [p for p in adrs if "ci" in p.stem.split("-")]
        self.assertTrue(matching, f"no CI ADR among {[p.name for p in adrs]}")


if __name__ == "__main__":
    unittest.main()
