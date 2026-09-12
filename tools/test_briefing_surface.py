"""Bind every skill briefing surface to standing rule 6 and a declared kind."""

from __future__ import annotations

import unittest
from pathlib import Path

import briefing_surface
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent


class BriefingSurfaceCoverage(unittest.TestCase):
    def test_declared_limits_are_not_copied_into_the_module_prose(self):
        self.assertEqual((), bind(briefing_surface.DECLARED_LIMITS, briefing_surface.__doc__ or "", mode=NAMING))

    def test_standing_rule_six_carries_every_shared_briefing_floor(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual((), briefing_surface.standing_rule_findings(agents))

    def test_the_adversarial_floor_cannot_disappear_from_the_shared_home(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        mutant = agents.replace("refute rather than confirm", "review the record")

        self.assertIn("missing adversarial refutation floor", briefing_surface.standing_rule_findings(mutant))

    def test_a_spawn_shaped_line_outside_a_declared_surface_is_a_finding(self):
        text = "## Research\n\nFan out one research context per claim.\n"

        self.assertEqual(
            ("sample/SKILL.md:3: detector line is outside a declared briefing surface",),
            briefing_surface.surface_findings(Path("sample/SKILL.md"), text),
        )

    def test_a_declared_surface_cannot_copy_the_shared_one_writer_rule(self):
        text = (
            "This Fan-out brief applies [standing rule 6](../../AGENTS.md). "
            "The orchestrator alone writes the records.\n"
        )

        self.assertEqual(
            ("sample/SKILL.md:1: briefing surface copies standing rule 6",),
            briefing_surface.surface_findings(Path("sample/SKILL.md"), text),
        )

    def test_every_detected_surface_in_the_skill_population_is_declared(self):
        paths = briefing_surface.briefed_skill_paths(REPO_ROOT / "skills")

        self.assertTrue(paths)
        self.assertEqual(
            (),
            tuple(
                finding
                for path in paths
                for finding in briefing_surface.surface_findings(
                    path.relative_to(REPO_ROOT), path.read_text(encoding="utf-8")
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
