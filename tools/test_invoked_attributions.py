"""The research look-ahead reaches the shared attribution rule. #1497."""

import tempfile
import unittest
from pathlib import Path

import repo_root


ROOT = Path(__file__).resolve().parent.parent


class AttributionLibrary(unittest.TestCase):
    def test_worktree_uses_the_owning_library_even_when_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory).resolve() / "main"
            gitdir = main / ".git" / "worktrees" / "linked"
            gitdir.mkdir(parents=True)
            tree = main / "linked"
            (tree / "tools").mkdir(parents=True)
            (tree / ".git").write_text(f"gitdir: {gitdir.as_posix()}\n", encoding="utf-8")

            library = repo_root.attribution_library(tree / "tools")

            self.assertEqual(library, main / "scratch" / "attributions.md")
            self.assertFalse(library.exists())
            (main / "scratch").mkdir()
            library.write_text("pointer only\n", encoding="utf-8")
            self.assertEqual(repo_root.attribution_library(tree / "tools"), library)

    def test_all_research_steps_reach_the_section_and_its_resolved_path(self):
        section = "#invoked-attributions"
        research_steps = {
            "course-assignment": "## 2. Research before production",
            "discussion-post": "## 3. Outline blind, research the questions, then draft from records",
            "discussion-reply": "## 2. Build and verify the claim ledger",
            "peer-critique": "## 3. Build and verify the claim ledger",
            "practicum-case-study": "### 3. Research what the evidence does not cover",
        }
        for skill, heading in research_steps.items():
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                step = text.split(heading, 1)[1].split("\n##", 1)[0]
                self.assertIn(f"../_shared/reference/sourcing.md{section}", step)
                self.assertIn("canonical voice model's stated principles and invoked sources", step)

        sourcing = (ROOT / "skills/_shared/reference/sourcing.md").read_text(encoding="utf-8")
        attribution_section = sourcing.split("## Invoked attributions\n", 1)[1].split("\n## ", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            library = repo_root.attribution_library(root / "tools")
            self.assertIn(f"`{library.relative_to(root).as_posix()}`", attribution_section)


if __name__ == "__main__":
    unittest.main()
