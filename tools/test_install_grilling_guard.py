"""Public-contract tests for the one-command grilling guard installer. #1392."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import install_grilling_guard as installer


class InstallerContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.source = self.root / "worktree"
        self.owning = self.root / "owning checkout"
        (self.source / "docs" / "agents").mkdir(parents=True)
        (self.source / "docs" / "agents" / "grilling.md").write_text(
            "tracked format\n", encoding="utf-8"
        )
        (self.source / "tools").mkdir(parents=True)
        (self.source / "tools" / "grilling_stop_hook.py").write_text(
            "tracked hook\n", encoding="utf-8"
        )
        (self.owning / "tools").mkdir(parents=True)
        (self.owning / "docs" / "agents").mkdir(parents=True)
        for relative in (
            Path("docs/agents/grilling.md"),
            Path("tools/grilling_stop_hook.py"),
        ):
            (self.owning / relative).write_bytes((self.source / relative).read_bytes())
        (self.home / ".codex").mkdir(parents=True)
        (self.home / ".claude" / "projects" / "project" / "memory").mkdir(
            parents=True
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self) -> None:
        installer.install(
            home=self.home,
            source_root=self.source,
            owning_checkout=self.owning,
        )

    @staticmethod
    def hook_commands(document: dict[str, object]) -> list[str]:
        return [
            hook["command"]
            for registration in document["hooks"]["Stop"]
            for hook in registration["hooks"]
        ]

    def test_one_install_preserves_agents_text_and_the_david_hook(self) -> None:
        agents = self.home / ".codex" / "AGENTS.md"
        agents.write_text("before\n\nafter\n", encoding="utf-8")
        hooks = self.home / ".codex" / "hooks.json"
        david = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "node C:/david.mjs hook",
                            }
                        ]
                    }
                ]
            }
        }
        hooks.write_text(json.dumps(david), encoding="utf-8")

        self.install()

        installed_agents = agents.read_text(encoding="utf-8")
        self.assertTrue(installed_agents.startswith("before\n\nafter\n"))
        self.assertIn("tracked format", installed_agents)
        installed_hooks = json.loads(hooks.read_text(encoding="utf-8"))
        commands = self.hook_commands(installed_hooks)
        self.assertIn("node C:/david.mjs hook", commands)
        expected_script = (self.owning / "tools" / "grilling_stop_hook.py").resolve()
        self.assertTrue(any(str(expected_script) in command for command in commands))

    def test_reinstall_replaces_its_block_and_registration_without_duplicates(self) -> None:
        self.install()
        self.install()

        agents = (self.home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(agents.count(installer.BLOCK_START), 1)
        hooks = json.loads(
            (self.home / ".codex" / "hooks.json").read_text(encoding="utf-8")
        )
        commands = self.hook_commands(hooks)
        self.assertEqual(
            sum("grilling_stop_hook.py" in command for command in commands), 1
        )

    def test_the_claude_memory_becomes_a_pointer_not_a_second_copy(self) -> None:
        memory = (
            self.home
            / ".claude"
            / "projects"
            / "project"
            / "memory"
            / "grill-one-question-at-a-time.md"
        )
        memory.write_text("old duplicated rules\n", encoding="utf-8")

        self.install()

        pointer = memory.read_text(encoding="utf-8")
        self.assertIn(
            str(self.owning / "docs" / "agents" / "grilling.md"), pointer
        )
        self.assertNotIn("old duplicated rules", pointer)
        self.assertNotIn("tracked format", pointer)

    def test_a_rerun_keeps_the_memory_s_subject_placement(self) -> None:
        # ADR 0391: the pointer must not move a filed memory back to a flat line.
        import memory_index

        memory = (
            self.home / ".claude" / "projects" / "project" / "memory"
            / "grill-one-question-at-a-time.md"
        )
        memory.write_text(
            "---\nname: grill-one-question-at-a-time\n"
            'description: "Use the tracked one-question grilling format."\n'
            "metadata:\n  node_type: memory\n  type: feedback\n  subjects: adr-grilling\n---\n\nold\n",
            encoding="utf-8",
        )

        self.install()

        self.assertEqual(memory_index.read_memory(memory).subjects, ("adr-grilling",))
        self.assertIn(str(self.owning / "docs" / "agents" / "grilling.md"), memory.read_text(encoding="utf-8"))

    def test_a_memory_with_no_placement_stays_unplaced_by_the_installer(self) -> None:
        import memory_index

        memory = (
            self.home / ".claude" / "projects" / "project" / "memory"
            / "grill-one-question-at-a-time.md"
        )
        memory.write_text("old duplicated rules\n", encoding="utf-8")

        self.install()

        self.assertIsNone(memory_index.read_memory(memory).subjects)

    def test_agents_bytes_outside_the_marked_block_are_unchanged(self) -> None:
        agents = self.home / ".codex" / "AGENTS.md"
        before = b"first\r\nsecond\r\n\r\n"
        agents.write_bytes(before)

        self.install()

        self.assertTrue(agents.read_bytes().startswith(before))

        installed = agents.read_bytes()
        prefix, marked = installed.split(installer.BLOCK_START.encode("utf-8"), 1)
        agents.write_bytes(
            prefix
            + installer.BLOCK_START.encode("utf-8")
            + marked.replace(b"tracked format", b"stale format", 1)
            + b"tail\r\n\r\n"
        )
        expected_suffix = b"tail\r\n\r\n"

        self.install()

        refreshed = agents.read_bytes()
        self.assertTrue(refreshed.startswith(before))
        self.assertTrue(refreshed.endswith(expected_suffix))

    def test_a_missing_or_different_owning_copy_refuses_before_user_writes(self) -> None:
        (self.owning / "tools" / "grilling_stop_hook.py").write_text(
            "older hook\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "owning checkout"):
            self.install()

        self.assertFalse((self.home / ".codex" / "AGENTS.md").exists())
        self.assertFalse((self.home / ".codex" / "hooks.json").exists())

    def test_checkout_line_endings_do_not_make_identical_tracked_text_different(self) -> None:
        for relative in (
            Path("docs/agents/grilling.md"),
            Path("tools/grilling_stop_hook.py"),
        ):
            text = (self.source / relative).read_text(encoding="utf-8")
            (self.source / relative).write_bytes(
                text.replace("\n", "\r\n").encode("utf-8")
            )
            (self.owning / relative).write_bytes(text.encode("utf-8"))

        self.install()

        self.assertTrue((self.home / ".codex" / "AGENTS.md").exists())

    def test_a_standalone_carriage_return_is_content_and_still_refuses(self) -> None:
        relative = Path("docs/agents/grilling.md")
        (self.source / relative).write_bytes(b"first\rsecond\n")
        (self.owning / relative).write_bytes(b"first\nsecond\n")

        with self.assertRaisesRegex(ValueError, "owning checkout"):
            self.install()


    def test_a_rerun_keeps_every_stop_hook_at_its_trust_key_position(self) -> None:
        # Codex keys hook trust by position (hooks.json:stop:<group>:<handler>),
        # so moving our registration to the end shifts every hook after it.
        hooks = self.home / ".codex" / "hooks.json"
        david = {"hooks": [{"type": "command", "command": "node C:/david.mjs hook"}]}
        old = {"hooks": [{"type": "command", "command": "python old/grilling_stop_hook.py"}]}
        later = {"hooks": [{"type": "command", "command": "python run_status_stop_hook.py"}]}
        hooks.write_text(
            json.dumps({"hooks": {"Stop": [david, old, later]}}), encoding="utf-8"
        )

        self.install()

        stop = json.loads(hooks.read_text(encoding="utf-8"))["hooks"]["Stop"]
        self.assertEqual(stop[0], david)
        self.assertIn(
            str((self.owning / "tools" / "grilling_stop_hook.py").resolve()),
            stop[1]["hooks"][0]["command"],
        )
        self.assertEqual(stop[2], later)
        self.assertEqual(len(stop), 3)


class InPlaceRegistration(unittest.TestCase):
    """The shared seam every Codex hook installer registers through."""

    @staticmethod
    def handler(command: str) -> dict[str, object]:
        return {"type": "command", "command": command}

    def ours(self) -> dict[str, object]:
        return {"hooks": [self.handler("python new/guard.py")]}

    def test_an_absent_registration_is_appended(self) -> None:
        other = {"hooks": [self.handler("other")]}
        self.assertEqual(
            installer.register_in_place([other], "guard.py", self.ours()),
            [other, self.ours()],
        )

    def test_a_sole_registration_is_replaced_where_it_stands(self) -> None:
        first = {"hooks": [self.handler("first")]}
        last = {"hooks": [self.handler("last")]}
        stale = {"matcher": "Bash", "hooks": [self.handler("python old/guard.py")]}
        self.assertEqual(
            installer.register_in_place([first, stale, last], "guard.py", self.ours()),
            [first, self.ours(), last],
        )

    def test_a_later_duplicate_is_removed_and_earlier_positions_hold(self) -> None:
        first = {"hooks": [self.handler("first")]}
        stale = {"hooks": [self.handler("python old/guard.py")]}
        self.assertEqual(
            installer.register_in_place(
                [first, stale, dict(stale)], "guard.py", self.ours()
            ),
            [first, self.ours()],
        )

    def test_a_shared_registration_keeps_its_other_handlers(self) -> None:
        shared = {
            "matcher": "Bash",
            "hooks": [self.handler("other"), self.handler("python old/guard.py")],
        }
        self.assertEqual(
            installer.register_in_place([shared], "guard.py", self.ours()),
            [{"matcher": "Bash", "hooks": [self.handler("other")]}, self.ours()],
        )

    def test_registrations_that_name_no_handler_of_ours_are_untouched(self) -> None:
        empty = {"hooks": []}
        opaque = "not a registration"
        self.assertEqual(
            installer.register_in_place([empty, opaque], "guard.py", self.ours()),
            [empty, opaque, self.ours()],
        )


class CommandLine(unittest.TestCase):
    """An argument never performs the install it was meant to ask about."""

    def test_an_argument_never_installs(self) -> None:
        for argument, status in (("--help", 0), ("--dry-run", 2)):
            with self.subTest(argument=argument):
                with mock.patch.object(installer, "install") as install:
                    with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                        with self.assertRaises(SystemExit) as stopped:
                            installer.main([argument])
                self.assertEqual(stopped.exception.code, status)
                install.assert_not_called()

if __name__ == "__main__":
    unittest.main()
