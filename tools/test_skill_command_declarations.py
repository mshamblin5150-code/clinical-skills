#!/usr/bin/env python3
"""Hold the rule that every command a skill invokes is named in AGENTS.md."""

from __future__ import annotations

import unittest
from pathlib import Path

import python_floor


REPO_ROOT = Path(__file__).resolve().parent.parent


class EverySkillCommandIsDeclared(unittest.TestCase):
    def test_an_unnamed_skill_command_is_refused_with_both_remedies(self):
        roots = python_floor.invoked_roots(
            (("skills/sample/SKILL.md", "Run `python tools/unnamed.py`."),)
        )

        findings = python_floor.undeclared_skill_commands(roots, "# Agents\n")

        self.assertEqual(("unnamed",), findings)
        self.assertIn("name the command in AGENTS.md", python_floor.UNDECLARED_REMEDY)
        self.assertIn(
            "stop handing consumers a command they must not run",
            python_floor.UNDECLARED_REMEDY,
        )

    def test_every_skill_command_in_the_repository_is_named(self):
        report = python_floor.scan_repository(REPO_ROOT)

        self.assertEqual((), report.undeclared_roots, python_floor.UNDECLARED_REMEDY)


if __name__ == "__main__":
    unittest.main()
