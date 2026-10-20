"""Launch payload decisions for ADR 0375 and #1593."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid

from repo_root import scratch_path


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools/subagent_staging_hook.py"


class SubagentStagingLaunch(unittest.TestCase):
    def setUp(self):
        parent = scratch_path(ROOT / "scratch", "sessions")
        parent.mkdir(parents=True, exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(prefix="launch-test-", dir=parent)
        self.addCleanup(self.workspace.cleanup)
        self.folder = Path(self.workspace.name)
        self.stage = self.folder / "pass"
        self.stage.mkdir()

    def command(self, prompt, cwd=None, tool="Agent"):
        payload = {"tool_name": tool, "tool_input": {"prompt": prompt},
                   "cwd": str(cwd or ROOT)}
        result = subprocess.run(
            [sys.executable, str(COMMAND)], input=json.dumps(payload),
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def test_run_without_staging_route_is_refused_without_echoing_patient_text(self):
        for tool in ("Agent", "Task"):
            response = self.command("Read scratch/runs/example/note.md PRIVATE-TEXT", tool=tool)
            specific = response["hookSpecificOutput"]
            self.assertEqual(specific["permissionDecision"], "deny")
            self.assertIn("scratch/sessions/<key>/<pass-label>/", specific["permissionDecisionReason"])
            self.assertNotIn("PRIVATE-TEXT", json.dumps(response))

    def test_readonly_and_fixture_briefs_owe_no_route(self):
        for prompt in ("Read tools/example.py", "Read scratch/fixture-runs/example/",
                       "Read myoutput/example/ and scratch/runs-other/example/"):
            self.assertEqual({}, self.command(prompt))

    def test_temp_locations_are_refused_even_without_a_run(self):
        for location in ("/tmp/work/", "/var/tmp/work/", "/private/tmp/work/",
                         r"C:\Users\example\AppData\Local\Temp\work",
                         "C:/Windows/Temp/work", "%TEMP%/work", "$env:TEMP/work",
                         "$TMP/work", "${TMP}/work", "session scratchpad",
                         "system temporary directory", tempfile.gettempdir()):
            with self.subTest(location=location):
                response = self.command("Stage in " + location + " PRIVATE-TEXT")
                self.assertEqual("deny", response["hookSpecificOutput"]["permissionDecision"])
                self.assertNotIn("PRIVATE-TEXT", json.dumps(response))

    def test_existing_nonempty_folder_accepts_relative_absolute_and_backslash_routes(self):
        (self.stage / "existing.txt").write_text("fixture", encoding="utf-8")
        for path in (str(self.stage), self.stage.as_posix(),
                     self.stage.relative_to(ROOT).as_posix(),
                     "./" + self.stage.relative_to(ROOT).as_posix()):
            with self.subTest(path=path):
                self.assertEqual({}, self.command('Read output/example/; stage in `' + path + '`'))
        spaced = self.folder / "pass with spaces"
        spaced.mkdir()
        self.assertEqual({}, self.command('Read output/example/; stage in "' + str(spaced) + '"'))

    def test_reused_brief_fails_after_cleanup_removed_its_folder(self):
        prompt = 'Read scratch/runs/example/; stage in `' + str(self.stage) + '`'
        self.assertEqual({}, self.command(prompt))
        self.stage.rmdir()
        self.assertEqual("deny", self.command(prompt)["hookSpecificOutput"]["permissionDecision"])

    def test_file_traversal_root_and_missing_folder_do_not_satisfy_route(self):
        file = self.folder / "file"
        file.write_text("fixture", encoding="utf-8")
        for path in (file, self.folder / "missing", scratch_path(ROOT / "scratch", "sessions"),
                     self.folder / "../../.." / "tools"):
            with self.subTest(path=path):
                response = self.command('Read output/example/; stage in `' + str(path) + '`')
                self.assertEqual("deny", response["hookSpecificOutput"]["permissionDecision"])

    def test_relative_paths_use_payload_cwd_instead_of_hook_process_cwd(self):
        relative = self.stage.relative_to(ROOT)
        self.assertEqual({}, self.command(f"Read output/example/; `{relative}`", cwd=ROOT))
        response = self.command(f"Read output/example/; `{relative}`", cwd=self.folder)
        self.assertEqual("deny", response["hookSpecificOutput"]["permissionDecision"])

    def test_any_named_missing_route_is_refused_even_alongside_a_valid_route(self):
        prompt = f"Read output/example/; `{self.stage}` and `{self.folder / 'missing'}`"
        self.assertEqual("deny", self.command(prompt)["hookSpecificOutput"]["permissionDecision"])

    def test_existing_folder_outside_registered_checkouts_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="launch-unregistered-", dir=ROOT.parent) as directory:
            path = scratch_path(Path(directory) / "scratch", "sessions") / "pass"
            path.mkdir(parents=True)
            self.assertEqual("deny", self.command(f"Read output/example/; `{path}`")
                             ["hookSpecificOutput"]["permissionDecision"])

    def test_staging_symlink_cannot_escape_the_sessions_root(self):
        target = self.folder / "../../.." / "tools"
        link = self.folder / "link"
        try:
            link.symlink_to(target.resolve(), target_is_directory=True)
        except OSError:
            self.skipTest("directory symlinks unavailable")
        self.assertEqual("deny", self.command(f"Read output/example/; `{link}`")
                         ["hookSpecificOutput"]["permissionDecision"])

    def test_registered_peer_checkout_is_accepted(self):
        peer = self.folder / ("checkout-" + uuid.uuid4().hex)
        subprocess.run(["git", "worktree", "add", "--detach", "--no-checkout", str(peer), "HEAD"],
                       cwd=ROOT, capture_output=True, check=True)
        try:
            stage = scratch_path(peer / "scratch", "sessions") / "probe/pass"
            stage.mkdir(parents=True)
            self.assertEqual({}, self.command(f"Read output/example/; `{stage}`"))
            self.assertEqual({}, self.command("Read output/example/; scratch/sessions/probe/pass/", cwd=peer))
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(peer)], cwd=ROOT,
                           capture_output=True, check=True)


class SubagentStagingInstallation(unittest.TestCase):
    def test_hook_is_registered_for_both_launch_tools(self):
        import re

        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        entries = [entry for entry in settings["hooks"]["PreToolUse"]
                   if any("subagent_staging_hook.py" in hook["command"] for hook in entry["hooks"])]
        self.assertEqual(len(entries), 1)
        for tool in ("Agent", "Task"):
            self.assertIsNotNone(re.fullmatch(entries[0]["matcher"], tool))

    def test_missing_cwd_and_prompt_follow_public_policy(self):
        for inputs, cwd in (({"prompt": "Read output/example/; scratch/sessions/existing/pass/"}, None),
                            ({"prompt": "Read output/example/; scratch/sessions/existing/pass/"}, "relative"),
                            ({"prompt": 17, "description": "output/example/"}, str(ROOT))):
            payload = {"tool_name": "Agent", "tool_input": inputs}
            if cwd is not None:
                payload["cwd"] = cwd
            result = subprocess.run([sys.executable, str(COMMAND)], input=json.dumps(payload),
                                    capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual("deny", json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"])


if __name__ == "__main__":
    unittest.main()
