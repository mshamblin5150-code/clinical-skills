"""Public-command controls for ADR 0368 and ADR 0392, #1581."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


TOOLS = Path(__file__).resolve().parent
SLASH = chr(92)
PROBE = "printf '%s" + SLASH + "n' 'backslash-probe: a" + SLASH * 2 + "b'"


class BackslashPairCommand(unittest.TestCase):
    def command(self, raw):
        result = subprocess.run(
            [sys.executable, str(TOOLS / "backslash_pair_hook.py")],
            input=raw, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def payload(self, command, tool="Bash"):
        return json.dumps({"tool_name": tool, "tool_input": {"command": command}})

    def test_refuses_pairs_in_every_command_context(self):
        for command in (
            "cat <<'EOF'\n" + SLASH * 2 + "n\nEOF",
            "printf '%s' '" + SLASH * 2 + "b'",
            "python -c 'print(\"" + SLASH * 2 + "n\")'",
            'echo "a' + SLASH * 2 + 'b"',
            PROBE + " ",
        ):
            for tool in ("Bash", "Monitor"):
                with self.subTest(command=command, tool=tool):
                    response = self.command(self.payload(command, tool))
                    specific = response["hookSpecificOutput"]
                    self.assertEqual(specific["permissionDecision"], "deny")
                    self.assertIn("Write tool", specific["permissionDecisionReason"])
                    self.assertIn(PROBE, specific["permissionDecisionReason"])

    def test_allows_single_backslash_and_only_the_exact_probe(self):
        for command in ("echo a" + SLASH + "b", PROBE, "echo plain"):
            with self.subTest(command=command):
                self.assertEqual(self.command(self.payload(command)), {})

    def test_unreadable_fields_use_original_raw_text_and_both_note_channels(self):
        for tool_input in (None, [], {}, {"command": None}, {"command": 42}):
            for trigger in (False, True):
                raw = json.dumps({"tool_input": tool_input,
                                  "other": SLASH * 2 if trigger else "plain"})
                with self.subTest(tool_input=tool_input, trigger=trigger):
                    response = self.command(raw)
                    specific = response["hookSpecificOutput"]
                    self.assertEqual(specific.get("permissionDecision"), "deny" if trigger else None)
                    self.assertIn("backslash check: unread", response["systemMessage"])
                    self.assertEqual(specific["additionalContext"], response["systemMessage"])

        # Decoded escapes would form a pair; the ruled raw literal is absent.
        raw = '{"other":"' + (SLASH + 'u005c') * 2 + '"}'
        response = self.command(raw)
        self.assertNotIn("permissionDecision", response["hookSpecificOutput"])

    def test_readable_command_does_not_search_other_fields(self):
        raw = json.dumps({"tool_input": {"command": "echo plain"}, "other": SLASH * 4})
        self.assertEqual(self.command(raw), {})

    def test_repo_settings_register_for_bash_and_monitor(self):
        settings = json.loads((TOOLS.parent / ".claude/settings.json").read_text(encoding="utf-8"))
        entries = [entry for entry in settings["hooks"]["PreToolUse"]
                   if any("backslash_pair_hook.py" in hook["command"] for hook in entry["hooks"])]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["matcher"], "Bash|Monitor")


if __name__ == "__main__":
    from console_codec import require_python_floor, use_utf8

    use_utf8()
    require_python_floor()
    unittest.main()
