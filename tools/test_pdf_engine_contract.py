"""The consumer PDF-engine contract is derived from the skills that use it.

The derivation sees a role only when a skill writes its ``<role>.py`` command
name, and it sees a direct engine import only inside a fenced Python block. A
skill that reaches the engine through any other spelling escapes this walk.
Issue #1009.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401
import pdf_engine
from prose_bind import NAMING, bind


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
AGENTS = ROOT / "AGENTS.md"
CHECK_COMMAND = "python tools/pdf_engine.py"
CONTRACT_OPENING = "**PDF engine prerequisites.**"


def engine_dependent_skills(sources: dict[str, str]) -> set[str]:
    """Return skill names visible through the ticket's bounded derivation."""
    role_commands = tuple(f"{role}.py" for role in pdf_engine.ROLES)
    fenced_python = re.compile(r"```python\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    direct_import = re.compile(r"(?m)^\s*(?:import|from)\s+(?:fitz|pymupdf)\b")
    return {
        name
        for name, source in sources.items()
        if any(command in source for command in role_commands)
        or any(direct_import.search(block) for block in fenced_python.findall(source))
    }


def contract_paragraph(source: str) -> str:
    start = source.index(CONTRACT_OPENING)
    end = source.find("\n\n", start)
    return source[start:] if end < 0 else source[start:end]


def declared_engine_skills(source: str, skill_names: set[str]) -> set[str]:
    paragraph = contract_paragraph(source)
    named_list = paragraph.split(" skills need", 1)[0]
    return {name for name in skill_names if f"`{name}`" in named_list}


class TheIndexNamesEveryEngineDependentSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = {
            path.parent.name: path.read_text(encoding="utf-8")
            for path in sorted(SKILLS.glob("*/SKILL.md"))
        }
        cls.agents = AGENTS.read_text(encoding="utf-8")

    def test_the_derivation_detects_both_live_inputs(self):
        fixture = {
            "role": "Run `python tools/render_scan.py run`.\n",
            "direct": "```python\nimport fitz\n```\n",
            "clean": "Run `python tools/other.py`.\n",
        }
        self.assertEqual({"role", "direct"}, engine_dependent_skills(fixture))

        expanded = dict(self.sources)
        expanded["fixture-skill"] = "Run `python tools/render_scan.py run`.\n"
        self.assertNotEqual(
            engine_dependent_skills(expanded),
            declared_engine_skills(self.agents, set(expanded)),
        )

    def test_the_derived_and_declared_sets_match_in_both_directions(self):
        derived = engine_dependent_skills(self.sources)
        declared = declared_engine_skills(self.agents, set(self.sources))
        self.assertEqual(
            derived,
            declared,
            f"derived only {sorted(derived - declared)}; declared only {sorted(declared - derived)}",
        )

    def test_removing_a_derived_skill_name_from_the_paragraph_is_detected(self):
        derived = engine_dependent_skills(self.sources)
        removed = next(iter(sorted(derived)))
        paragraph = contract_paragraph(self.agents)
        altered_paragraph = paragraph.replace(f"`{removed}`", removed, 1)
        altered = self.agents.replace(paragraph, altered_paragraph, 1)
        self.assertNotEqual(
            derived,
            declared_engine_skills(altered, set(self.sources)),
        )

    def test_setup_and_each_derived_skill_run_the_check(self):
        setup = self.sources["setup-clinical-skills"]
        step_zero = setup[setup.index("### 0.") : setup.index("### 1.")]
        self.assertIn(CHECK_COMMAND, step_zero)
        for name in engine_dependent_skills(self.sources):
            with self.subTest(skill=name):
                self.assertIn(CHECK_COMMAND, self.sources[name])

    def test_setup_never_routes_an_indeterminate_recheck_to_fallback(self):
        setup = self.sources["setup-clinical-skills"]
        step_zero = setup[setup.index("### 0.") : setup.index("### 1.")]
        self.assertNotIn("second check does not exit 0", step_zero)
        self.assertIn("second check exits 1", step_zero)

    def test_the_index_points_to_the_check_without_copying_its_remedy(self):
        paragraph = contract_paragraph(self.agents)
        self.assertIn(CHECK_COMMAND, paragraph)
        self.assertEqual((), bind((pdf_engine.REMEDY,), self.agents, mode=NAMING))

    def test_discussion_post_completion_distinguishes_absence_from_findings(self):
        completion = self.sources["discussion-post"].split("## Completion", 1)[1]
        self.assertIn("not mechanically verified", completion)
        self.assertIn("engine check reported the engine missing", completion)
        self.assertIn("A finding still stops the run", completion)


if __name__ == "__main__":
    unittest.main()
