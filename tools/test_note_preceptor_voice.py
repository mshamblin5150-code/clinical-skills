"""Keep issue #1445's retired preceptor-deferral instructions out of the skill."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "clinical-note"


class NotePreceptorVoiceTests(unittest.TestCase):
    def test_no_skill_passage_teaches_preceptor_deferral(self) -> None:
        retired = re.compile(
            r"\b(?:for\s+the\s+)?preceptor\s+(?:to\s+rule|rules\s+on\s+it)\b",
            re.IGNORECASE,
        )
        for path in SKILL_DIR.rglob("*.md"):
            with self.subTest(path=path.relative_to(SKILL_DIR)):
                self.assertIsNone(retired.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
