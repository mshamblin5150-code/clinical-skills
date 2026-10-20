"""Plant unreadable payloads at each existing guard's public command. ADR 0392."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


TOOLS = Path(__file__).resolve().parent
COMMAND_GUARDS = {
    "subagent_staging_hook": ("scratch/runs/a/", "output/b/", "scratch/other/", "plain"),
    "fixture_writer_hook": ("scratch/fixture-runs/a/", "scratch/fixture-runs/b/", "scratch/other/", "plain"),
    "backslash_pair_hook": (chr(92) * 4, "a" + chr(92) * 4 + "b", chr(92), "plain"),
    "heredoc_write_hook": ("<< scratch", "<< output", "<< public", "scratch"),
    "scanner_pipe_hook": ("| specificity_scan.py", "| differential_scan.py", "| missing-file.py", "specificity_scan.py"),
    "tracker_publish_hook": ("gh issue create", "echo gh", "git status", "GH"),
    "browser_tab_hook": ("read_page", "browser_batch", "tabId", "mcp__claude-in-chrome__tabs_context_mcp"),
}
STOP_GUARDS = ("grilling_stop_hook", "run_status_stop_hook")


class UnreadableHookPayloads(unittest.TestCase):
    def command(self, name, raw="", failed_read=None):
        args = [sys.executable, str(TOOLS / (name + ".py"))]
        if failed_read:
            # Fault the actual command's input stream, before its __main__ runs.
            launcher = (
                "import io, runpy, sys; "
                "sys.path.insert(0, sys.argv[1]); "
                "path = sys.argv[2]; sys.argv = [path]; "
            )
            if failed_read == "closed":
                launcher += "sys.stdin = io.StringIO(); sys.stdin.close(); "
            else:
                launcher += (
                    "stream = type('Broken', (), {'read': lambda self: "
                    "(_ for _ in ()).throw(OSError('PRIVATE-READ-ERROR'))}); "
                    "sys.stdin = stream(); "
                )
            launcher += "runpy.run_path(path, run_name='__main__')"
            args = [sys.executable, "-c", launcher, str(TOOLS), str(TOOLS / (name + ".py"))]
        result = subprocess.run(args, input=raw, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def assert_command_outcome(self, response, denied):
        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "PreToolUse")
        self.assertEqual(specific.get("permissionDecision"), "deny" if denied else None)
        self.assertIn("unreadable hook payload", specific["additionalContext"])
        self.assertIn("did not grade the call", specific["additionalContext"])
        self.assertEqual(response["systemMessage"], specific["additionalContext"])
        if denied:
            self.assertEqual(specific["permissionDecisionReason"], response["systemMessage"])

    def test_malformed_and_nonobject_payloads_use_each_guards_raw_trigger(self):
        for name, samples in COMMAND_GUARDS.items():
            for index, sample in enumerate(samples):
                for raw in (sample + " PRIVATE-PAYLOAD", json.dumps([sample, "PRIVATE-PAYLOAD"])):
                    with self.subTest(name=name, raw=raw):
                        response = self.command(name, raw)
                        self.assert_command_outcome(response, index < 2)
                        self.assertNotIn("PRIVATE-PAYLOAD", json.dumps(response))

    def test_failed_reads_allow_command_guards_with_both_notes(self):
        for name in COMMAND_GUARDS:
            for failure in ("oserror", "closed"):
                with self.subTest(name=name, failure=failure):
                    response = self.command(name, failed_read=failure)
                    self.assert_command_outcome(response, False)
                    self.assertNotIn("PRIVATE-READ-ERROR", json.dumps(response))

    def test_empty_and_nonobject_scalars_are_unreadable(self):
        for name in COMMAND_GUARDS:
            for raw in ("", "null", "42", "true"):
                with self.subTest(name=name, raw=raw):
                    self.assert_command_outcome(self.command(name, raw), name == "browser_tab_hook")

    def test_stops_always_allow_unreadable_payloads_with_warning(self):
        for name in STOP_GUARDS:
            for raw, failed_read in (("<< scratch | gh", None), ('["tabId", "gh"]', None),
                                     ("null", None), ("", "oserror"), ("", "closed")):
                with self.subTest(name=name, raw=raw, failed_read=failed_read):
                    response = self.command(name, raw, failed_read)
                    self.assertTrue(response["continue"])
                    self.assertIn("did not grade the turn", response["systemMessage"])
                    self.assertNotIn("decision", response)
                    self.assertNotIn("hookSpecificOutput", response)

    def test_browser_creation_and_listing_exemptions_for_both_families(self):
        for tool in ("mcp__claude-in-chrome__tabs_create_mcp",
                     "mcp__claude-in-chrome__tabs_context_mcp",
                     "mcp__Claude_Browser__tabs_context",
                     "mcp__Claude_Browser__tabs_create"):
            for raw in (tool + " {", json.dumps([tool])):
                with self.subTest(tool=tool, raw=raw):
                    self.assert_command_outcome(self.command("browser_tab_hook", raw), False)

    def test_unreadable_browser_batch_with_one_tab_id_passes_raw_search(self):
        batch = {"tool_name": "mcp__claude-in-chrome__browser_batch", "tool_input": {
            "actions": [{"name": "read_page", "input": {"tabId": 7}},
                        {"name": "read_page", "input": {}}]}}
        self.assert_command_outcome(self.command("browser_tab_hook", json.dumps(batch)[:-1]), False)
        # When readable the same batch still receives the ordinary per-action refusal.
        response = self.command("browser_tab_hook", json.dumps(batch))
        self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_escaped_trigger_is_a_declared_raw_search_limit(self):
        self.assert_command_outcome(self.command("tracker_publish_hook", '["g\\u0068"]'), False)

    def test_decoder_nesting_limit_uses_the_same_unreadable_policy(self):
        for name, samples in COMMAND_GUARDS.items():
            for index in (0, 2):
                with self.subTest(name=name, trigger=index == 0):
                    raw = "[" * 1100 + json.dumps(samples[index])
                    self.assert_command_outcome(self.command(name, raw), index == 0)
        for name in STOP_GUARDS:
            with self.subTest(name=name):
                response = self.command(name, "[" * 1100 + '"gh"')
                self.assertTrue(response["continue"])
                self.assertIn("did not grade the turn", response["systemMessage"])


if __name__ == "__main__":
    from console_codec import require_python_floor, use_utf8

    use_utf8()
    require_python_floor()
    unittest.main()
