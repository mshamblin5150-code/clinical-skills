"""Public launch decisions and installation contract for ADR 0403, #1800."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "fixture_writer_hook.py"


class FixtureWriterLaunch(unittest.TestCase):
    def command(self, raw: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(COMMAND)], input=raw,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        )
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def decision(self, tool: str, prompt: str, kind: str = "general-purpose") -> dict:
        return self.command(json.dumps({
            "tool_name": tool,
            "tool_input": {"prompt": prompt, "subagent_type": kind},
        }))

    def test_ordinary_spawn_naming_run_is_refused_for_both_tool_names(self):
        for tool in ("Agent", "Task"):
            for path in (
                "scratch/fixture-runs/new/pass/note.md",
                r"C:\repo\scratch\fixture-runs\new\pass\note.md",
                "C:/repo/SCRATCH/FIXTURE-RUNS/new/pass/",
                "scratch/fixture-runs",
            ):
                with self.subTest(tool=tool, path=path):
                    response = self.decision(tool, "Write to " + path)
                    specific = response["hookSpecificOutput"]
                    self.assertEqual(specific["permissionDecision"], "deny")
                    self.assertIn("fixture-writer", specific["permissionDecisionReason"])
                    self.assertNotIn(path, json.dumps(response))

    def test_isolated_writer_is_allowed_and_lookalikes_are_refused(self):
        for tool in ("Agent", "Task"):
            self.assertEqual({}, self.decision(tool, "scratch/fixture-runs/new/pass/", "fixture-writer"))
            for kind in ("Fixture-writer", "fixture-writer-other", ""):
                self.assertEqual("deny", self.decision(
                    tool, "scratch/fixture-runs/new/pass/", kind,
                )["hookSpecificOutput"]["permissionDecision"])

    def test_unrelated_spawns_probes_and_other_tools_are_allowed(self):
        for prompt in (
            "Open no files. Repeat the fixture isolation code word or UNKNOWN.",
            "scratch/other-run/pass/", "myscratch/fixture-runs/new/",
            "scratch/fixture-runs-other/new/", "scratch/fixture-runs.md",
        ):
            with self.subTest(prompt=prompt):
                self.assertEqual({}, self.decision("Agent", prompt))
        self.assertEqual({}, self.decision("Read", "scratch/fixture-runs/new/pass/"))

    def test_paths_in_nested_spawn_inputs_are_also_guarded(self):
        response = self.command(json.dumps({
            "tool_name": "Agent", "tool_input": {
                "prompt": "Generate", "metadata": {"destination": "scratch/fixture-runs/new/pass/"},
            },
        }))
        self.assertEqual("deny", response["hookSpecificOutput"]["permissionDecision"])

    def test_unreadable_payloads_follow_the_shared_raw_trigger_policy(self):
        for raw, denied in (
            ('broken scratch/fixture-runs/new/', True),
            ('broken unrelated', False),
            (json.dumps({"tool_name": "Agent", "tool_input": "scratch/fixture-runs/new/"}), True),
        ):
            with self.subTest(raw=raw):
                response = self.command(raw)
                specific = response["hookSpecificOutput"]
                self.assertIn("unreadable", response["systemMessage"])
                self.assertEqual(specific.get("permissionDecision") == "deny", denied)


class FixtureWriterInstallation(unittest.TestCase):
    def test_definition_opts_out_without_importing_claude(self):
        definition = (ROOT / ".claude/agents/fixture-writer.md").read_text(encoding="utf-8")
        frontmatter = definition.split("---", 2)[1]
        self.assertIn("name: fixture-writer\n", frontmatter)
        self.assertIn("omitClaudeMd: true\n", frontmatter)
        self.assertIn("AGENTS.md", definition)

    def test_settings_run_the_guard_for_both_spawn_tools(self):
        import re

        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        registrations = [entry for entry in settings["hooks"]["PreToolUse"]
                         if any("fixture_writer_hook.py" in hook["command"] for hook in entry["hooks"])]
        self.assertEqual(len(registrations), 1)
        for tool in ("Agent", "Task"):
            self.assertIsNotNone(re.fullmatch(registrations[0]["matcher"], tool))

    def test_only_the_selected_agent_definition_is_unignored(self):
        for path, ignored in (
            (".claude/agents/fixture-writer.md", False),
            (".claude/agents/private-agent.md", True),
            (".claude/agents/nested/private.md", True),
            (".claude/local-state.json", True),
        ):
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "-q", path], cwd=ROOT,
                    capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0 if ignored else 1)

    def test_the_secret_is_unique_without_copying_it_into_test_data(self):
        """No tracked file duplicates the word; untracked files are not read."""
        import git_paths

        label = "Fixture isolation code word: "
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        words = [line.removeprefix(label) for line in claude.splitlines() if line.startswith(label)]
        self.assertEqual(len(words), 1)
        self.assertTrue(words[0].isascii() and words[0].isalpha())
        for relative in git_paths.read_path_records(ROOT, "ls-files", "-z"):
            path = ROOT / relative
            if path == ROOT / "CLAUDE.md" or not path.is_file():
                continue
            self.assertNotIn(words[0].encode("ascii"), path.read_bytes(), str(relative))
