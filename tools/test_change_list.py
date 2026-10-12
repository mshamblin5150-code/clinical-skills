"""Sentence change-list and retained-revision contracts for ADR 0348. #1560."""

# phi-scan: synthetic

from __future__ import annotations

import io
import runpy
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import change_list
import case_study_scan
import coursework_run
import discussion_post_scan
import discussion_reply_scan
import peer_critique_scan
import prose_bind
import run_grader


class SentenceChanges(unittest.TestCase):
    def test_a_dropped_closing_sentence_is_named(self) -> None:
        self.assertEqual(
            change_list.changes(
                change_list.sentences("The opening remains. The closing matters."),
                change_list.sentences("The opening remains."),
            ),
            ("Removed: The closing matters.",),
        )

    def test_an_added_sentence_is_named(self) -> None:
        self.assertEqual(
            change_list.changes(("The opening remains.",), ("The opening remains.", "A sentence joins.")),
            ("Added: A sentence joins.",),
        )

    def test_a_reworded_sentence_has_both_versions(self) -> None:
        self.assertEqual(
            change_list.changes(("The old wording remains.",), ("The new wording remains.",)),
            ("Reworded:", "  Before: The old wording remains.", "  After: The new wording remains."),
        )

    def test_a_moved_sentence_is_removed_and_added(self) -> None:
        result = change_list.changes(
            ("Moved sentence.", "First anchor.", "Second anchor."),
            ("First anchor.", "Second anchor.", "Moved sentence."),
        )
        self.assertEqual(result, ("Removed: Moved sentence.", "Added: Moved sentence."))

    def test_whitespace_changes_and_identical_versions_have_no_changes(self) -> None:
        before = change_list.sentences("A sentence spans\n  two lines.\n\nAnother sentence.")
        after = change_list.sentences("A sentence spans two lines.\n\nAnother sentence.")
        self.assertEqual(before, after)
        self.assertEqual(change_list.changes(before, after), ("No sentence changed.",))
        self.assertEqual(change_list.changes((), ()), ("No sentence changed.",))

    def test_markdown_blocks_split_sentences_and_keep_reference_entries_whole(self) -> None:
        reference = "Writer, A. (2026). A title. Publisher. https://example.org/source"
        result = change_list.sentences(
            "# Discussion\n\nOpening sentence. Another sentence!\n\n"
            "- A list item?\n\n## References\n\n" + reference + "\n"
        )
        self.assertIn("Opening sentence.", result)
        self.assertIn("Another sentence!", result)
        self.assertIn("A list item?", result)
        self.assertIn(reference, result)
        self.assertNotIn("Writer, A.", result)

    def test_markdown_is_read_through_the_shared_blocks_parser(self) -> None:
        with mock.patch.object(change_list, "blocks", wraps=change_list.blocks) as reader:
            change_list.sentences("A paragraph. Another sentence.")
        reader.assert_called_once_with("A paragraph. Another sentence.")

    def test_positional_pairing_boundary_is_declared(self) -> None:
        text = str(change_list.DECLARED_LIMITS).lower()
        self.assertIn("positional", text)
        self.assertIn("heuristic", text)

    def test_shared_procedure_names_limits_without_copying_them(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills" / "_shared" / "reference" / "revisions.md").read_text(encoding="utf-8")
        self.assertEqual((), prose_bind.bind(change_list.DECLARED_LIMITS, text, mode=prose_bind.NAMING))


class CommandContract(unittest.TestCase):
    def invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = change_list.main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_command_prints_the_list_and_checks_its_runtime_floor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before, after = root / "before.md", root / "after.md"
            before.write_text("Opening. Closing.", encoding="utf-8")
            after.write_text("Opening.", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch("console_codec.use_utf8") as codec, mock.patch(
                "console_codec.require_python_floor"
            ) as floor, mock.patch("sys.argv", ["change_list.py", str(before), str(after)]):
                with redirect_stdout(stdout), redirect_stderr(stderr), self.assertRaises(SystemExit) as stopped:
                    runpy.run_path(change_list.__file__, run_name="__main__")
            self.assertEqual((stopped.exception.code, stdout.getvalue(), stderr.getvalue()), (0, "Removed: Closing.\n", ""))
            codec.assert_called_once()
            floor.assert_called_once()

    def test_either_missing_or_invalid_utf8_file_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.md"
            valid.write_text("Synthetic sentence.", encoding="utf-8")
            invalid = root / "invalid.md"
            invalid.write_bytes(b"\xff")
            for unreadable in (root / "missing.md", invalid):
                for arguments in ([str(unreadable), str(valid)], [str(valid), str(unreadable)]):
                    with self.subTest(arguments=arguments):
                        status, stdout, stderr = self.invoke(arguments)
                        self.assertEqual(status, 2)
                        self.assertEqual(stdout, "")
                        self.assertTrue(stderr.strip())


class SharedRevisionProcedure(unittest.TestCase):
    def test_the_four_skills_point_to_one_revision_sheet(self) -> None:
        root = Path(__file__).resolve().parents[1]
        sheet = root / "skills" / "_shared" / "reference" / "revisions.md"
        self.assertTrue(sheet.is_file())
        for skill in ("discussion-reply", "discussion-post", "peer-critique", "practicum-case-study"):
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("../_shared/reference/revisions.md", text)

    def test_retained_copies_do_not_enter_any_of_the_four_actual_loaders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            (run / "posts").mkdir()
            (run / "posts" / "classmate.md").write_text("AUTHOR: Synthetic Classmate\n", encoding="utf-8")
            (run / "board-2026-10-12.md").write_text("Synthetic board.\n", encoding="utf-8")
            (run / "claims.md").write_text("Synthetic ledger.\n", encoding="utf-8")
            (run / "bar.md").write_text(
                "TOPIC: Synthetic\nSYLLABUS: Synthetic\nSIGNED: 2026-10-12\n"
                "WORD-FLOOR: 1\nWORD-CEILING: none\nREFERENCE-MINIMUM: 0\n", encoding="utf-8"
            )
            drafts = {"reply": "response-synthetic.md", "post": "draft.md", "critique": "critique.md", "case": "case.md"}
            for name in drafts.values():
                (run / name).write_text("Synthetic current sentence.\n", encoding="utf-8")
            parsed = run_grader.Parsed(str(run))
            post_parsed = run_grader.Parsed(str(run), values={"--draft": str(run / drafts["post"])})
            case_parsed = run_grader.Parsed(str(run / drafts["case"]))
            loaders = (
                (discussion_reply_scan.load, parsed),
                (discussion_post_scan.load, post_parsed),
                (peer_critique_scan.load, parsed),
                (case_study_scan._load, case_parsed),
            )
            before = tuple(loader(arguments) for loader, arguments in loaders)
            for key in drafts.values():
                stem = coursework_run.voice_records_directory(run, key).name
                retained = run / "revisions" / stem
                retained.mkdir(parents=True)
                # Invalid bytes make accidental opening observable in strict readers.
                (retained / key).write_bytes(b"STALE REVISION MUST NOT ENTER THE GRADE.\xff")
            after = tuple(loader(arguments) for loader, arguments in loaders)
            self.assertEqual(before, after)
            self.assertEqual(tuple(reply.path.name for reply in after[0].replies), (drafts["reply"],))


if __name__ == "__main__":
    unittest.main()
