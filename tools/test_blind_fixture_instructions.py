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

Decision records under docs/adr/ are history no generating pass loads;
docs/agents/ documents are read only for tracker work. Both are outside this check.
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
THRESHOLDS = REFERENCE / "thresholds"

# Guard every skill and reference Markdown file so a newly linked sheet cannot
# open a gap. Root documents are named because each was ruled on individually:
# README.md and CONTEXT.md join because authors edit them constantly, not because
# a generating pass reads them; CLAUDE.md remains outside because fixture writers
# start without it (ADR 0403). The per-run recall proof tests that host behavior.
REQUIRED_INSTRUCTIONS = sorted(
    {
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        ROOT / "CONTEXT.md",
        ROOT / ".claude/agents/fixture-writer.md",
        *SKILLS.rglob("*.md"),
        *REFERENCE.rglob("*.md"),
    }
)

CONCRETE_FIXTURE_PATH = re.compile(
    r"fixtures/(?!README(?:\.md)?(?:[#)\s\]]|$))(?=[^\s`\]).,;:!?])"
)
NUMBERED_CASE_OR_RUN = re.compile(r"(?i)\b(?:case|run)\s*-?\d+\b")
# These strings are ordinary clinical notation as well as assertion identifiers.
# Ignoring them avoids treating vitamin B12, heart sounds S1/S2, oxygen O2, and
# fibrosis stages F3/F4 as leaks. C1 and S4 are exempt only in their clinical or
# guideline-section contexts so a standalone fixture row still refuses.
CLINICAL_ROW_HOMONYMS = {"B12", "F3", "F4", "O2", "S1", "S2"}
CLINICAL_ROW_CONTEXTS = (
    re.compile(r"\bC1(?=\s+esterase\b)"),
    re.compile(r"\bS4(?=\.\d)"),
)


def concrete_fixture_names() -> list[str]:
    return sorted(path.name for path in FIXTURES.iterdir() if path.is_dir())


def concrete_assertion_rows() -> list[str]:
    rows = set()
    for path in FIXTURES.glob("*/assertions.md"):
        rows.update(ROW_ID.findall(path.read_text(encoding="utf-8")))
    return sorted(rows - CLINICAL_ROW_HOMONYMS)


def without_clinical_row_contexts(line: str) -> str:
    for pattern in CLINICAL_ROW_CONTEXTS:
        line = pattern.sub("", line)
    return line


def row_checked_line(path: Path, line: str) -> str:
    """Return the surface on which fixture assertion identifiers are meaningful.

    Threshold sheets carry clinical stage and category identifiers such as A1,
    C1, D2, F2, and G1 as source vocabulary. Those strings collide with fixture
    row identifiers by construction, so the row-identity limb cannot distinguish
    them there. The other identity limbs still scan every threshold-sheet line.
    """
    if path.parent == THRESHOLDS:
        return ""
    return without_clinical_row_contexts(line)


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
        row_checked = row_checked_line(path, normalized)
        if (
            CONCRETE_FIXTURE_PATH.search(normalized)
            or name_pattern.search(normalized)
            or NUMBERED_CASE_OR_RUN.search(normalized)
            or row_pattern.search(row_checked)
        ):
            found.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    return found


class RequiredInstructionsStayBlind(unittest.TestCase):
    def test_the_required_instruction_population_is_real(self):
        self.assertGreater(len(REQUIRED_INSTRUCTIONS), 5)
        self.assertTrue(all(path.is_file() for path in REQUIRED_INSTRUCTIONS))
        self.assertIn(ROOT / "AGENTS.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(ROOT / "README.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(ROOT / "CONTEXT.md", REQUIRED_INSTRUCTIONS)
        self.assertNotIn(ROOT / "CLAUDE.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(ROOT / ".claude/agents/fixture-writer.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(REFERENCE / "medatrax-fields.md", REQUIRED_INSTRUCTIONS)
        self.assertIn(REFERENCE / "uptodate" / "README.md", REQUIRED_INSTRUCTIONS)
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

    def test_clinical_row_contexts_do_not_exempt_standalone_fixture_rows(self):
        self.assertEqual(without_clinical_row_contexts("C1 esterase and S4.2.2"), " esterase and .2.2")
        self.assertEqual(without_clinical_row_contexts("C1 carried S4"), "C1 carried S4")

    def test_threshold_clinical_codes_do_not_widen_the_skill_instruction_exemption(self):
        threshold = THRESHOLDS / "example.md"
        skill = SKILLS / "example" / "SKILL.md"
        self.assertEqual(row_checked_line(threshold, "A1 C1 G1"), "")
        self.assertEqual(row_checked_line(skill, "B18 carried the answer"), "B18 carried the answer")

    def test_the_general_policy_link_is_not_a_concrete_fixture_path(self):
        self.assertIsNone(
            CONCRETE_FIXTURE_PATH.search("[fixtures/README](../../fixtures/README.md)")
        )
        self.assertIsNotNone(
            CONCRETE_FIXTURE_PATH.search("../../fixtures/example-set/README.md")
        )

    def test_a_bare_fixture_directory_discloses_no_identity(self):
        for suffix in ("", " ", "\t", "\n", "`", "]", ")", ".", ",", ";", ":", "!", "?"):
            with self.subTest(suffix=suffix):
                self.assertIsNone(CONCRETE_FIXTURE_PATH.search("fixtures/" + suffix))
        self.assertIsNone(
            CONCRETE_FIXTURE_PATH.search("fixtures/                 de-identified regression material and run records")
        )

    def test_fixture_path_segments_still_disclose_an_identity(self):
        for path in (
            "fixtures/day-a/shorthand/case-01.md",
            "fixtures/*/assertions.md",
            "fixtures/<set>/",
            "fixtures/README-other/",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(CONCRETE_FIXTURE_PATH.search(path))


if __name__ == "__main__":
    unittest.main()
