"""Run records stay outside the note population. Issue #1805."""

import contextlib
import importlib
import io
from pathlib import Path
import re
import tempfile
import unittest

import medatrax_posting
import run_grader


class RunRecords(unittest.TestCase):
    def unclassified_names(self, text):
        names = set(re.findall(r"`([^`/\\\r\n:]+\.md)`", text))
        classified = {f"{stem}.md".casefold() for stem in run_grader.RUN_RECORD_STEMS}
        classified.update(name.casefold() for name in run_grader.NON_RUN_MARKDOWN_NAMES)
        return {name for name in names if name.casefold() not in classified
                and re.fullmatch(r"note-(?:N|[0-9]+)\.md", name) is None}

    def test_every_bare_backticked_markdown_name_in_the_note_skills_is_classified(self):
        root = Path(__file__).resolve().parents[1]
        paths = [root / "skills/batch-shift/SKILL.md", root / "skills/icd10-cpt/SKILL.md",
                 *sorted((root / "skills/clinical-note").rglob("*.md"))]
        for path in paths:
            with self.subTest(path=path.relative_to(root)):
                self.assertEqual(set(), self.unclassified_names(path.read_text(encoding="utf-8")))

    def test_inventory_catches_a_new_run_record_but_does_not_read_unquoted_names(self):
        self.assertEqual({"new-record.md"}, self.unclassified_names("Write `new-record.md`."))
        self.assertEqual({"review.v2.md"}, self.unclassified_names("Write `review.v2.md`."))
        self.assertEqual({"review copy.md"}, self.unclassified_names("Write `review copy.md`."))
        self.assertEqual(set(), self.unclassified_names("Write new-record.md."))

    def test_record_names_leave_arbitrarily_named_notes_in_the_shared_reader(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ("case-01.md", "unexpected.md", "README.md", "shift-summary.md",
                         "delegated-answers.md", "reread.md"):
                (root / name).write_text(name, encoding="utf-8")
            self.assertEqual(["case-01.md", "unexpected.md"],
                             [item.path.name for item in run_grader.read_run_artifacts(root)])

    def test_each_public_run_command_reports_its_set_aside_records(self):
        for module_name in ("anchor_scan", "block_scan", "differential_scan",
                            "refusal_scan", "specificity_scan", "filled_vitals_census"):
            with self.subTest(module=module_name), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                (root / "case-01.md").write_text("S: A synthetic note.\n", encoding="utf-8")
                module = importlib.import_module(module_name)
                def report():
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                        module.main([str(root)])
                    return output.getvalue()
                before = report()
                for name in ("README.md", "shift-summary.md", "delegated-answers.md", "reread.md"):
                    (root / name).write_text("Run record.\n", encoding="utf-8")
                after = report()
                for name in ("README.md", "shift-summary.md", "delegated-answers.md", "reread.md"):
                    self.assertIn(name, after)
                self.assertIn("set aside as run records:", after)
                counts = r"(?:notes read|worksheets read|^worksheets)\s+\d+"
                self.assertTrue(re.findall(counts, before, re.MULTILINE), before)
                self.assertEqual(re.findall(counts, before, re.MULTILINE),
                                 re.findall(counts, after, re.MULTILINE))

    def test_standalone_posting_keeps_one_note_beside_all_records(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ("case-01.md", "README.md", "shift-summary.md",
                         "delegated-answers.md", "reread.md"):
                (root / name).write_text("Synthetic.\n", encoding="utf-8")
            self.assertEqual((root / "case-01.md",), medatrax_posting.note_paths(root, batch=False))


if __name__ == "__main__":
    unittest.main()
