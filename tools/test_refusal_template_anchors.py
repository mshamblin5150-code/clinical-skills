"""Keep the refusal teaching examples aligned with their verbatim anchor rule."""

from pathlib import Path
import re
import unittest


class RefusalTemplateAnchors(unittest.TestCase):
    def test_every_step_four_refusal_has_its_code_descriptor_anchor(self):
        skill = (Path(__file__).resolve().parents[1] / "skills" / "icd10-cpt" / "SKILL.md").read_text(encoding="utf-8")
        section = skill.split("### 4. Report what documentation is missing", 1)[1].split("### 5.", 1)[0]
        refusals = []
        for block in re.findall(r"```[^\n]*\n(.*?)```", section, re.DOTALL):
            lines = block.splitlines()
            for index, line in enumerate(lines):
                if line.startswith("  NOT CODED: "):
                    value = line.removeprefix("  NOT CODED: ")
                    expected = ("<the code-and-descriptor half of the note's welded NOT CODED: clause>"
                                if value == "<code and official descriptor>" else value)
                    self.assertLess(index + 1, len(lines))
                    self.assertEqual(f'  ANCHOR: "{expected}"', lines[index + 1])
                    refusals.append(value)
        self.assertIn("<code and official descriptor>", refusals)
        self.assertIn("U07.1  COVID-19", refusals)
        self.assertIn("M86.9  Osteomyelitis, unspecified", refusals)


if __name__ == "__main__":
    unittest.main()
