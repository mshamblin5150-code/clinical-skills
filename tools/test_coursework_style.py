"""Tests for the shared coursework narrative-body row."""

from __future__ import annotations

import unittest
from pathlib import Path
from xml.etree import ElementTree

import coursework_style
from prose_bind import NAMING, bind


ROOT = Path(__file__).resolve().parent.parent


class SharedRendererGrammar(unittest.TestCase):
    def test_bullets_numbered_lists_and_tables_are_the_prohibited_population(self):
        text = (
            "Narrative paragraph.\n\n"
            "- bullet\n"
            "1. numbered\n\n"
            "| A | B |\n| --- | --- |\n| x | y |\n"
        )
        self.assertEqual(
            ("bullet", "numbered", "table"),
            tuple(block.kind for block in coursework_style.narrative_blocks(text)),
        )

    def test_quoted_material_and_correct_prose_are_outside_the_row(self):
        text = "Narrative paragraph.\n\n> - Quoted list wording.\n"
        self.assertEqual((), coursework_style.narrative_blocks(text))

    def test_a_native_word_list_retains_the_quote_exemption(self):
        document = ElementTree.fromstring(
            f'<w:document xmlns:w="{coursework_style.W[1:-1]}"><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Body</w:t></w:r></w:p>'
            '<w:p><w:pPr><w:pStyle w:val="BlockQuotation"/><w:numPr/></w:pPr>'
            '<w:r><w:t>Quoted list wording.</w:t></w:r></w:p>'
            '</w:body></w:document>'
        )
        self.assertEqual((), coursework_style.docx_narrative_blocks(document))

    def test_the_shared_style_and_each_affected_skill_name_the_row(self):
        paths = (
            ROOT / "skills" / "_shared" / "reference" / "style.md",
            ROOT / "skills" / "discussion-post" / "SKILL.md",
            ROOT / "skills" / "discussion-reply" / "SKILL.md",
            ROOT / "skills" / "peer-critique" / "SKILL.md",
            ROOT / "skills" / "course-assignment" / "references" / "docx.md",
        )
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIn("`narrative-body`", path.read_text(encoding="utf-8"))

    def test_the_word_projection_ceiling_is_bound_to_the_shared_style(self):
        style = (ROOT / "skills" / "_shared" / "reference" / "style.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            (), bind(coursework_style.DECLARED_LIMITS, style, mode=NAMING)
        )


if __name__ == "__main__":
    unittest.main()
