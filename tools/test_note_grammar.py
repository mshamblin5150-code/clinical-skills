"""Note-section boundaries over synthetic and committed note text."""

# phi-scan: synthetic

from __future__ import annotations

import unittest
from pathlib import Path

import entry_copy
import note_grammar


ROOT = Path(__file__).resolve().parents[1]


class NoteGrammar(unittest.TestCase):
    def test_all_committed_notes_partition_and_agree_on_plan_boundary(self) -> None:
        fixtures = ROOT / "fixtures"
        notes = [
            path for path in fixtures.rglob("*.md")
            if any(entry_copy._plain(line) in {"P:", "Plan", "Plan:"}
                   for line in path.read_text(encoding="utf-8").splitlines())
        ]
        self.assertEqual(28, len(notes))
        for path in notes:
            with self.subTest(note=str(path.relative_to(fixtures))):
                source = path.read_text(encoding="utf-8")
                result = note_grammar.parse(source)
                self.assertEqual(source, "".join(result.buckets.values()))
                self.assertTrue(all(result.sections.values()))
                self.assertTrue(result.buckets["tail"])
                # A planted label is visible at every Plan line and invisible
                # immediately after the grammar's closing line.
                prefix = "".join(result.buckets[name] for name in ("preamble", "S", "O", "A"))
                plan_lines = result.buckets["P"].splitlines(keepends=True)
                tail_lines = result.buckets["tail"].splitlines(keepends=True)
                probe = "UnexpectedProbe: value\n"
                for index in range(1, len(plan_lines) + 1):
                    planted = prefix + "".join(plan_lines[:index]) + probe + "".join(plan_lines[index:]) + result.buckets["tail"]
                    self.assertIn("UnexpectedProbe", entry_copy._plan_labels(planted)[1])
                planted_after = prefix + result.buckets["P"] + tail_lines[0] + probe + "".join(tail_lines[1:])
                self.assertNotIn("UnexpectedProbe", entry_copy._plan_labels(planted_after)[1])

    def test_missing_heading_and_unknown_terminator_refuse(self) -> None:
        note = "Intro\nS:\nSubject\nO:\nObject\nA:\nAssess\nP:\nPlan\n---\nTail\n"
        self.assertEqual("Subject\n", note_grammar.parse(note).sections["S"])
        with self.assertRaises(ValueError):
            note_grammar.parse(note.replace("O:\n", "Unknown:\n"))
        with self.assertRaises(ValueError):
            note_grammar.parse(note.replace("---\n", "Unknown closer\n"))
        with self.assertRaises(ValueError):
            note_grammar.parse(note.replace("---\n", "## Unknown closer\n## Tier block\n"))
        with self.assertRaises(ValueError):
            note_grammar.parse("S:\nsubject\n```\nO:\nfenced\n```\nA:\nassess\nP:\nplan\n---\ntail\n")
        with self.assertRaises(ValueError):
            note_grammar.parse("S:\ns\nO:\no\nA:\na\nP:\nplan\n~~~\n---\n~~~\ntail\n")


if __name__ == "__main__":
    unittest.main()
