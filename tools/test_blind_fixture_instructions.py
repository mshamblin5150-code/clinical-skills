"""Required instructions do not disclose the fixtures they grade -- issue #147.

A generating pass has to read these files, so naming a concrete fixture in one
of them gives the pass information that the runner meant to withhold.  The
general fixture policy remains linkable; set, case, run, row and score evidence
belongs in the withheld fixture files instead.

This guard deliberately checks identity, not semantic resemblance.  It can
prove that a required file names a committed set, path, or numbered case/run.
It cannot prove that an unattributed row, score or count came from a fixture, or
that a synthetic example merely resembles an encounter, so review still owns
those questions.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from assertion_record import ROW_ID


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FIXTURES = ROOT / "fixtures"
REFERENCE = ROOT / "reference"

# Every Markdown file shipped inside a skill can become part of that skill's
# required instructions.  The repo-wide agent rules and clinical-note's
# required or conditionally required reference sheets sit outside that tree.
# Guard the safe superset so a newly linked supporting file cannot open a gap.
REQUIRED_INSTRUCTIONS = sorted(
    {
        ROOT / "AGENTS.md",
        REFERENCE / "guidelines-uspstf.md",
        REFERENCE / "medatrax-fields.md",
        *SKILLS.rglob("*.md"),
        *(REFERENCE / "thresholds").glob("*.md"),
    }
)

CONCRETE_FIXTURE_PATH = re.compile(
    r"fixtures/(?!README(?:\.md)?(?:[#)\s\]]|$))"
)
NUMBERED_CASE_OR_RUN = re.compile(r"(?i)\b(?:case|run)\s*-?\d+\b")
# These strings are ordinary clinical notation as well as assertion identifiers.
# Ignoring them avoids treating vitamin B12, heart sounds S1/S2, oxygen O2, and
# fibrosis stages F3/F4 as leaks.
CLINICAL_ROW_HOMONYMS = {"B12", "F3", "F4", "O2", "S1", "S2"}


def concrete_fixture_names() -> list[str]:
    return sorted(path.name for path in FIXTURES.iterdir() if path.is_dir())


def concrete_assertion_rows() -> list[str]:
    rows = set()
    for path in FIXTURES.glob("*/assertions.md"):
        rows.update(ROW_ID.findall(path.read_text(encoding="utf-8")))
    return sorted(rows - CLINICAL_ROW_HOMONYMS)


def findings(path: Path) -> list[str]:
    names = concrete_fixture_names()
    name_pattern = re.compile(
        r"(?<![A-Za-z0-9_-])(?:" + "|".join(map(re.escape, names)) + r")(?![A-Za-z0-9_-])"
    )
    row_pattern = re.compile(
        r"(?<![A-Za-z0-9])(?:"
        + "|".join(map(re.escape, concrete_assertion_rows()))
        + r")(?![A-Za-z0-9])"
    )
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        normalized = line.replace("\\", "/")
        if (
            CONCRETE_FIXTURE_PATH.search(normalized)
            or name_pattern.search(normalized)
            or NUMBERED_CASE_OR_RUN.search(normalized)
            or row_pattern.search(normalized)
        ):
            found.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    return found


class RequiredInstructionsStayBlind(unittest.TestCase):
    def test_the_required_instruction_population_is_real(self):
        self.assertGreater(len(REQUIRED_INSTRUCTIONS), 5)
        self.assertTrue(all(path.is_file() for path in REQUIRED_INSTRUCTIONS))
        self.assertIn(ROOT / "AGENTS.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(REFERENCE / "medatrax-fields.md", REQUIRED_INSTRUCTIONS)
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

    def test_the_guard_detects_a_numbered_case_or_run_without_a_set_name(self):
        self.assertIsNotNone(NUMBERED_CASE_OR_RUN.search("case 7 carried the answer"))
        self.assertIsNotNone(NUMBERED_CASE_OR_RUN.search("run 2 scored it"))

    def test_the_guard_detects_a_committed_assertion_row(self):
        self.assertIn("B18", concrete_assertion_rows())
        path = ROOT / "tools" / "test_blind_fixture_instructions.py"
        row_pattern = re.compile(
            r"(?<![A-Za-z0-9])(?:"
            + "|".join(map(re.escape, concrete_assertion_rows()))
            + r")(?![A-Za-z0-9])"
        )
        self.assertIsNotNone(row_pattern.search("B18 carried the answer"))
        self.assertIsNone(row_pattern.search("vitamin B12 level"))

    def test_the_general_policy_link_is_not_a_concrete_fixture_path(self):
        self.assertIsNone(
            CONCRETE_FIXTURE_PATH.search("[fixtures/README](../../fixtures/README.md)")
        )
        self.assertIsNotNone(
            CONCRETE_FIXTURE_PATH.search("../../fixtures/example-set/README.md")
        )


if __name__ == "__main__":
    unittest.main()
