"""Required instructions do not disclose the fixtures they grade -- issue #147.

A generating pass has to read these files, so naming a concrete fixture in one
of them gives the pass information that the runner meant to withhold.  The
general fixture policy remains linkable; set, case, run, row and score evidence
belongs in the withheld fixture files instead.

This guard deliberately checks identity, not semantic resemblance.  It can
prove that a required file names a committed set.  It cannot prove that a
synthetic example merely resembles an encounter, so review still owns that
question.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "fixtures"

# Every skill entry point is mandatory when that skill runs.  clinical-note's
# entry point additionally requires its glossary and the selected template.
REQUIRED_INSTRUCTIONS = sorted(SKILLS.glob("*/SKILL.md")) + [
    SKILLS / "clinical-note" / "GLOSSARY.md",
    SKILLS / "clinical-note" / "HP.md",
    SKILLS / "clinical-note" / "SOAP.md",
]


def concrete_fixture_names() -> list[str]:
    return sorted(path.name for path in FIXTURES.iterdir() if path.is_dir())


def findings(path: Path) -> list[str]:
    names = concrete_fixture_names()
    name_pattern = re.compile(
        r"(?<![A-Za-z0-9_-])(?:" + "|".join(map(re.escape, names)) + r")(?![A-Za-z0-9_-])"
    )
    fixture_path = re.compile(r"fixtures/(?!README(?:\.md)?(?:[#)\s\]]|$))")
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        normalized = line.replace("\\", "/")
        if fixture_path.search(normalized) or name_pattern.search(normalized):
            found.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    return found


class RequiredInstructionsStayBlind(unittest.TestCase):
    def test_the_required_instruction_population_is_real(self):
        self.assertGreater(len(REQUIRED_INSTRUCTIONS), 5)
        self.assertTrue(all(path.is_file() for path in REQUIRED_INSTRUCTIONS))
        self.assertIn(SKILLS / "clinical-note" / "GLOSSARY.md", REQUIRED_INSTRUCTIONS)

    def test_no_required_instruction_names_a_concrete_fixture(self):
        leaked = [item for path in REQUIRED_INSTRUCTIONS for item in findings(path)]
        self.assertEqual(
            leaked,
            [],
            "required instructions disclose concrete fixtures:\n" + "\n".join(leaked),
        )

    def test_the_guard_detects_a_planted_fixture_identity(self):
        name = concrete_fixture_names()[0]
        pattern = re.compile(
            r"(?<![A-Za-z0-9_-])" + re.escape(name) + r"(?![A-Za-z0-9_-])"
        )
        self.assertIsNotNone(pattern.search(f"a run over {name} disclosed its score"))

    def test_the_general_policy_link_is_not_a_concrete_fixture_path(self):
        fixture_path = re.compile(r"fixtures/(?!README(?:\.md)?(?:[#)\s\]]|$))")
        self.assertIsNone(fixture_path.search("[fixtures/README](../../fixtures/README.md)"))
        self.assertIsNotNone(fixture_path.search("../../fixtures/example-set/README.md"))


if __name__ == "__main__":
    unittest.main()
