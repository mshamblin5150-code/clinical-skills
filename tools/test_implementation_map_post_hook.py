"""Public-contract tests for the implementation-map PostToolUse reminder."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import implementation_map_post_hook as hook
import artifact_lock_test_support  # noqa: F401


class CommandContext(unittest.TestCase):
    def payload(self, command: str, response: object = "") -> dict:
        return {"tool_input": {"command": command}, "tool_response": response}

    def test_ready_flip_names_the_existing_ticket_and_command(self):
        response = hook.handle(
            self.payload("gh issue edit 920 --add-label ready-for-agent")
        )

        context = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("#920", context)
        self.assertIn("apply-delta --ticket 920", context)
        self.assertNotIn("permissionDecision", response["hookSpecificOutput"])

    def test_ready_create_reads_the_ticket_number_from_tool_output(self):
        response = hook.handle(
            self.payload(
                "gh issue create --label bug,ready-for-agent --title Work",
                {"stdout": "https://github.com/example/project/issues/1042"},
            )
        )

        self.assertIn(
            "apply-delta --ticket 1042",
            response["hookSpecificOutput"]["additionalContext"],
        )

    def test_nonmatching_command_is_silent(self):
        self.assertEqual(hook.handle(self.payload("gh issue edit 920 --add-label bug")), {})

    def test_ready_flip_in_another_repository_is_silent(self):
        with mock.patch.object(
            hook, "_git_line",
            return_value="git@github.com:example/clinical-skills.git",
        ):
            self.assertEqual(
                hook.handle(
                    self.payload(
                        "gh issue edit 920 --repo other/project "
                        "--add-label ready-for-agent"
                    )
                ),
                {},
            )
            self.assertEqual(
                hook.handle(
                    self.payload(
                        "gh issue edit 920 -Rother/project "
                        "--add-label ready-for-agent"
                    )
                ),
                {},
            )
            self.assertEqual(
                hook.handle(
                    self.payload(
                        "gh issue edit 920 --repo example.invalid/example/clinical-skills "
                        "--add-label ready-for-agent"
                    )
                ),
                {},
            )


class AdrMergeContext(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Hook Tests"], cwd=self.root, check=True)
        (self.root / "docs" / "adr").mkdir(parents=True)
        (self.root / "seed.txt").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        subprocess.run(["git", "branch", "origin/main"], cwd=self.root, check=True)
        subprocess.run(["git", "switch", "-qc", "feature"], cwd=self.root, check=True)
        (self.root / "docs" / "adr" / "0168-decision.md").write_text("# Decision\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "decision"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_pr_merge_names_each_branch_adr_and_never_refuses(self):
        with mock.patch.object(hook, "REPO_ROOT", self.root), mock.patch.object(
            hook, "_pr_lands_session_branch", return_value=True
        ):
            response = hook.handle({"tool_input": {"command": "gh pr merge --merge"}})

        specific = response["hookSpecificOutput"]
        self.assertIn("ADR 0168", specific["additionalContext"])
        self.assertNotIn("permissionDecision", specific)

    def test_push_to_main_names_the_branch_adr(self):
        old = subprocess.run(
            ["git", "rev-parse", "origin/main"], cwd=self.root, check=True,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout.strip()
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout.strip()
        subprocess.run(["git", "branch", "-f", "origin/main", "HEAD"], cwd=self.root, check=True)
        with mock.patch.object(hook, "REPO_ROOT", self.root):
            response = hook.handle(
                {
                    "tool_input": {"command": "git push origin HEAD:main"},
                    "tool_response": {"stdout": f"{old[:7]}..{head[:7]} HEAD -> main"},
                }
            )

        self.assertIn("ADR 0168", response["hookSpecificOutput"]["additionalContext"])

    def test_fully_qualified_push_to_main_is_classified(self):
        with mock.patch.object(hook, "_default_branch_name", return_value="main"):
            self.assertTrue(
                hook._lands_default_branch("git push origin HEAD:refs/heads/main")
            )

    def test_other_pr_or_nondefault_base_is_silent(self):
        with mock.patch.object(hook, "_pr_lands_session_branch", return_value=False):
            self.assertEqual(
                hook.handle({"tool_input": {"command": "gh pr merge 123 --merge"}}),
                {},
            )

    def test_pr_merge_must_match_session_branch_and_default_base(self):
        configured_base = ""

        def git_line(arguments: tuple[str, ...]) -> str:
            if arguments[0] == "branch":
                return "feature"
            if arguments[0] == "config":
                return configured_base
            return "origin/main"

        with mock.patch.object(hook, "_git_line", side_effect=git_line):
            self.assertFalse(hook._pr_lands_session_branch("gh pr merge 123 --merge"))
            self.assertTrue(hook._pr_lands_session_branch("gh pr merge feature --merge"))
            self.assertTrue(hook._pr_lands_session_branch("gh pr merge --merge"))
            configured_base = "release"
            self.assertFalse(hook._pr_lands_session_branch("gh pr merge --merge"))

    def test_ordinary_upstream_push_on_main_is_classified(self):
        def git_line(arguments: tuple[str, ...]) -> str:
            return "origin/main" if arguments[0] == "symbolic-ref" else "main"

        with mock.patch.object(hook, "_git_line", side_effect=git_line):
            self.assertTrue(hook._lands_default_branch("git push"))
            self.assertTrue(hook._lands_default_branch("git push origin HEAD"))

    def test_push_to_main_must_source_the_session_branch(self):
        def git_line(arguments: tuple[str, ...]) -> str:
            return "origin/main" if arguments[0] == "symbolic-ref" else "feature"

        with mock.patch.object(hook, "_git_line", side_effect=git_line):
            self.assertTrue(hook._lands_default_branch("git push origin HEAD:main"))
            self.assertTrue(hook._lands_default_branch("git push origin feature:main"))
            self.assertFalse(hook._lands_default_branch("git push origin other:main"))
            self.assertFalse(hook._lands_default_branch("git push origin :main"))
            self.assertFalse(hook._lands_default_branch("git push --delete origin main"))

    def test_pr_merge_in_another_repository_is_silent(self):
        with mock.patch.object(
            hook, "_git_line",
            return_value="git@github.com:example/clinical-skills.git",
        ):
            self.assertEqual(
                hook.handle(
                    {"tool_input": {"command": "gh pr merge --repo other/project --merge"}}
                ),
                {},
            )

    def test_pr_merge_with_separated_same_repo_short_flag_is_classified(self):
        def git_line(arguments: tuple[str, ...]) -> str:
            if arguments[0] == "branch":
                return "feature"
            if arguments[0] == "config":
                return ""
            if arguments[0] == "symbolic-ref":
                return "origin/main"
            return "git@github.com:example/clinical-skills.git"

        with mock.patch.object(hook, "_git_line", side_effect=git_line):
            self.assertTrue(
                hook._lands_default_branch(
                    "gh pr merge -R example/clinical-skills --merge"
                )
            )


class ProjectRegistration(unittest.TestCase):
    def test_post_use_hook_is_registered(self):
        settings = json.loads(
            Path(__file__).resolve().parents[1].joinpath(".claude/settings.json").read_text(encoding="utf-8")
        )
        registrations = settings["hooks"]["PostToolUse"]
        self.assertEqual(registrations[0]["matcher"], "Bash")
        self.assertIn("implementation_map_post_hook.py", registrations[0]["hooks"][0]["command"])

    def test_declared_limits_are_owned_here(self):
        self.assertEqual(len(hook.DECLARED_LIMITS), 5)
        self.assertTrue(any("number or URL" in row for row in hook.DECLARED_LIMITS))


if __name__ == "__main__":
    unittest.main()
