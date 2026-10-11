"""The reply and critique research bars are shown before research. #1495.

phi-scan: synthetic
"""

import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import research_ledger
from test_research_ledger import CLEAN, ledger_text


ROOT = Path(__file__).resolve().parents[1]


class SignedReplyAndCritiqueBars(unittest.TestCase):
    def test_both_skills_show_the_bar_at_the_existing_stop_before_research(self):
        for skill, stop in (("discussion-reply", "ranking stop"),
                            ("peer-critique", "spec-signing stop")):
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                start = text.index(f"At this {stop}")
                block = text[start:text.index("```", text.index("```text", start) + 7) + 3]
                self.assertIn("before researching any claim", block)
                self.assertIn("SIGNED: <leave blank until the clinician answers>", block)
                self.assertIn("SOURCE-CLASSES:", block)
                self.assertIn("RECENCY-WINDOW-YEARS:", block)
                self.assertIn("Show these lines beside", text[start:])
                self.assertIn("only then", text[start:])
                listing = re.search(r"```text\nscratch/runs/.*?```", text, re.S).group()
                self.assertIn("    bar.md\n", listing)

    def test_a_reply_reuses_the_signed_initial_post_bar_without_changing_it(self):
        skill = (ROOT / "skills/discussion-reply/SKILL.md").read_text(encoding="utf-8")
        initial = (ROOT / "skills/discussion-post/SKILL.md").read_text(encoding="utf-8")
        fields = "\n".join(re.findall(
            r"(?m)^(?:SOURCE-CLASSES|RECENCY-WINDOW-YEARS):.*$", initial))
        self.assertIn("write no second bar", skill)
        self.assertIn("including when reusing the signed bar", skill)
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            bar = run / "bar.md"
            bar.write_text("SIGNED: 2026-08-19\n" + fields + "\n", encoding="utf-8")
            before = bar.read_bytes()
            claims = run / "claims.md"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                status = research_ledger.main([str(claims)])
            self.assertEqual(0, status)
            self.assertEqual(before, bar.read_bytes())


if __name__ == "__main__":
    unittest.main()
