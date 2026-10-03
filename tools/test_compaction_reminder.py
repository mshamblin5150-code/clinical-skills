"""Public command and canonical-rule contracts for #1206."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import install_compaction_reminder as installer


ROOT = Path(__file__).resolve().parent.parent


class HookCommand(unittest.TestCase):
    def run_hook(self, payload: bytes) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / "compaction_reminder.py")],
            input=payload, capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        )

    def payload(self, source: str, **extra: object) -> bytes:
        return json.dumps({"hook_event_name": "SessionStart", "source": source, **extra},
                          ensure_ascii=False).encode("utf-8")

    def test_compact_delivers_context_even_in_a_subagent_session(self) -> None:
        # UTF-8 includes 0x9D, undefined in cp1252: locale decoding would fail.
        result = self.run_hook(self.payload("compact", agent_id="reader", cwd="ĝ"))
        self.assertEqual(0, result.returncode, result.stderr)
        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]
        self.assertEqual("SessionStart", context["hookEventName"])
        self.assertIn("summary holds no command result that may be stated", context["additionalContext"])
        self.assertNotIn("decision", output)

    def test_other_sources_emit_no_reminder(self) -> None:
        for source in ("startup", "resume", "clear", "unknown"):
            with self.subTest(source=source):
                result = self.run_hook(self.payload(source))
                self.assertEqual((0, b"", b""), (result.returncode, result.stdout, result.stderr))

    def test_malformed_payloads_do_not_crash_the_session(self) -> None:
        for payload in (b"", b"{", b"[]", b"null", b"1", b'"compact"', b"\xff", b"{}"):
            with self.subTest(payload=payload):
                result = self.run_hook(payload)
                self.assertEqual((0, b"", b""), (result.returncode, result.stdout, result.stderr))

    def test_another_event_with_compact_source_is_silent(self) -> None:
        result = self.run_hook(b'{"hook_event_name":"Stop","source":"compact"}')
        self.assertEqual((0, b""), (result.returncode, result.stdout))

    def test_claude_registration_is_session_start_without_agent_filter(self) -> None:
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        registrations = [row for row in settings["hooks"]["SessionStart"]
                         if any("compaction_reminder.py" in hook["command"] for hook in row["hooks"])]
        self.assertEqual(1, len(registrations))
        self.assertNotIn("if", registrations[0])
        self.assertNotIn("matcher", registrations[0])

    def test_reminder_points_to_the_matching_canonical_rule(self) -> None:
        context = json.loads(self.run_hook(self.payload("compact")).stdout)["hookSpecificOutput"]["additionalContext"]
        rule = installer.rule_text(ROOT)
        self.assertIn("AGENTS.md standing rule 7", context)
        for phrase in ("After a compaction", "every", "maintainer work", "read-only command",
                       "read back", "predates a", "has not been re-checked", "last resort",
                       "summary holds no command result that may be stated", "exit status",
                       "pipe", "`;` chain", "ADR 0281"):
            self.assertIn(phrase, rule)
        self.assertIn("re-observe", context)
        self.assertIn("last-resort label", context)


class WrittenFallback(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.source = self.root / "worktree"
        self.owning = self.root / "owning"
        for root in (self.source, self.owning):
            root.mkdir()
            (root / "AGENTS.md").write_bytes((ROOT / "AGENTS.md").read_bytes())
        self.agents = self.home / ".codex" / "AGENTS.md"
        self.agents.parent.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self) -> None:
        installer.install(home=self.home, source_root=self.source, owning_checkout=self.owning)

    def test_install_preserves_every_other_byte_and_is_idempotent(self) -> None:
        before, after = "before\r\n≥\r\n", "\r\nafter\r\n"
        self.agents.write_bytes((before + installer.BLOCK_START + "\nold\n" + installer.BLOCK_END + after).encode("utf-8"))
        hooks = self.home / ".codex" / "hooks.json"
        hooks.write_bytes(b'{"existing":"untouched"}')
        self.install()
        once = self.agents.read_bytes()
        self.install()
        self.assertEqual(once, self.agents.read_bytes())
        text = once.decode("utf-8")
        self.assertTrue(text.startswith(before))
        self.assertTrue(text.endswith(after))
        expected = installer.rule_text(self.owning).replace("(docs/adr/", f"({self.owning.resolve().as_posix()}/docs/adr/")
        self.assertIn(expected, text)
        self.assertEqual(b'{"existing":"untouched"}', hooks.read_bytes())

    def test_empty_home_gets_the_canonical_rule_and_no_hook(self) -> None:
        self.install()
        self.assertIn(installer.rule_text(self.owning).splitlines()[0], self.agents.read_text(encoding="utf-8"))
        self.assertFalse((self.home / ".codex" / "hooks.json").exists())

    def test_changed_source_is_refreshed_instead_of_copied_from_installer(self) -> None:
        self.install()
        for root in (self.source, self.owning):
            path = root / "AGENTS.md"
            path.write_text(path.read_text(encoding="utf-8") + "   Fresh canonical instruction.\n", encoding="utf-8")
        self.install()
        self.assertIn("Fresh canonical instruction.", self.agents.read_text(encoding="utf-8"))
        self.assertEqual(1, self.agents.read_text(encoding="utf-8").count(installer.BLOCK_START))

    def test_unmerged_rule_refuses_before_writing(self) -> None:
        path = self.owning / "AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + "   Stale owning rule.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "owning checkout"):
            self.install()
        self.assertFalse(self.agents.exists())

    def test_missing_rule_or_broken_markers_refuse_without_changing_file(self) -> None:
        for text in (installer.BLOCK_START, installer.BLOCK_END,
                     installer.BLOCK_END + installer.BLOCK_START,
                     (installer.BLOCK_START + installer.BLOCK_END) * 2):
            with self.subTest(text=text):
                self.agents.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.install()
                self.assertEqual(text, self.agents.read_text(encoding="utf-8"))
        (self.owning / "AGENTS.md").write_text("no rule\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "standing rule 7"):
            self.install()

    def test_next_standing_rule_is_not_installed(self) -> None:
        for root in (self.source, self.owning):
            path = root / "AGENTS.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n8. Another rule.\n", encoding="utf-8")
        self.install()
        self.assertNotIn("Another rule", self.agents.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
