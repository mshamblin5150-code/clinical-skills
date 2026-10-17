"""Tests for the two-level memory index (ADR 0391)."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import memory_index


RULE = memory_index.read_rule()


def memory(root: Path, name: str, description: str | None = "does a thing", subjects: str | None = None,
           *, frontmatter: bool = True) -> Path:
    path = root / f"{name}.md"
    if not frontmatter:
        path.write_text(f"# {name}\n\nbody\n", encoding="utf-8")
        return path
    lines = ["---", f"name: {name}"]
    if description is not None:
        lines.append(f'description: "{description}"')
    lines += ["metadata:", "  type: feedback"]
    if subjects is not None:
        lines.append(f"  subjects: {subjects}")
    path.write_text("\n".join([*lines, "---", "", "body", ""]), encoding="utf-8")
    return path


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            status = memory_index.main(argv)
        except SystemExit as exit_:
            status = exit_.code
    return status, out.getvalue(), err.getvalue()


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.index = self.root / "MEMORY.md"

    def tearDown(self) -> None:
        self.tmp.cleanup()


class TheTrackedRuleParses(unittest.TestCase):
    def test_the_seven_ruled_subjects_are_the_table(self):
        self.assertEqual(
            [subject.key for subject in RULE.subjects],
            ["clinical", "coursework", "canvas", "research", "tracker", "adr-grilling", "side-projects"],
        )

    def test_the_installed_block_names_every_subject_from_the_table(self):
        self.assertTrue(RULE.block.startswith(memory_index.BLOCK_START))
        self.assertTrue(RULE.block.endswith(memory_index.BLOCK_END))
        self.assertNotIn("{SUBJECTS}", RULE.block)
        for subject in RULE.subjects:
            self.assertIn(subject.key, RULE.block)


class ARebuildBeforeAnyHeaderChangesNothing(Fixture):
    def test_existing_flat_lines_survive_byte_for_byte(self):
        memory(self.root, "a")
        memory(self.root, "b", frontmatter=False)
        text = "- [A title](a.md) — hand hook\n- [B title](b.md) — other hook\n"
        self.index.write_text(text, encoding="utf-8")
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        self.assertEqual(self.index.read_text(encoding="utf-8"), text)
        self.assertFalse((self.root / "subjects").exists())
        self.assertIn("rule block: absent", out)

    def test_crlf_index_keeps_its_newlines(self):
        memory(self.root, "a")
        self.index.write_bytes(b"- [A](a.md) \xe2\x80\x94 hook\r\n")
        run([str(self.index), "--write"])
        self.assertEqual(self.index.read_bytes(), b"- [A](a.md) \xe2\x80\x94 hook\r\n")


class FilingMovesALineToItsSubjectLists(Fixture):
    def test_a_memory_with_two_subjects_is_listed_in_both_and_leaves_the_flat_part(self):
        memory(self.root, "pause", "pause in the box", "canvas, coursework")
        memory(self.root, "stash", "never stash", "none")
        self.index.write_text("- [Pause](pause.md) — old\n- [Stash](stash.md) — old\n", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        index = self.index.read_text(encoding="utf-8").splitlines()
        self.assertIn("- [Stash](stash.md) — never stash", index)
        self.assertFalse(any("pause.md" in line for line in index))
        canvas = (self.root / "subjects" / "canvas.md").read_text(encoding="utf-8")
        coursework = (self.root / "subjects" / "coursework.md").read_text(encoding="utf-8")
        for text in (canvas, coursework):
            self.assertIn("- [Pause](../pause.md) — pause in the box", text)
        self.assertEqual(sum(line.startswith("- [") and "subjects/" in line for line in index), 2)

    def test_a_subject_line_carries_no_member_count(self):
        memory(self.root, "one", "first", "canvas")
        self.index.write_text("", encoding="utf-8")
        run([str(self.index), "--write"])
        before = self.index.read_text(encoding="utf-8")
        memory(self.root, "two", "second", "canvas")
        run([str(self.index), "--write"])
        self.assertEqual(self.index.read_text(encoding="utf-8"), before)
        self.assertIn("../two.md", (self.root / "subjects" / "canvas.md").read_text(encoding="utf-8"))

    def test_an_empty_subject_list_is_removed(self):
        path = memory(self.root, "one", "first", "canvas")
        self.index.write_text("", encoding="utf-8")
        run([str(self.index), "--write"])
        path.unlink()
        run([str(self.index), "--write"])
        self.assertFalse((self.root / "subjects" / "canvas.md").exists())
        self.assertNotIn("subjects/canvas.md", self.index.read_text(encoding="utf-8"))

    def test_a_retired_memory_drops_out_of_every_index(self):
        path = memory(self.root, "old", "superseded", "none")
        self.index.write_text("- [Old](old.md) — superseded\n", encoding="utf-8")
        (self.root / "retired").mkdir()
        path.replace(self.root / "retired" / path.name)
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        self.assertEqual(self.index.read_text(encoding="utf-8"), "\n")
        self.assertIn("1 dangling lines dropped", out)

    def test_a_new_undeclared_memory_gets_a_flat_line(self):
        memory(self.root, "fresh", "a new rule")
        self.index.write_text("", encoding="utf-8")
        status, _, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0)
        self.assertIn("- [fresh](fresh.md) — a new rule", self.index.read_text(encoding="utf-8"))


class AnUnplacedMemoryIsAFinding(Fixture):
    def test_a_subject_off_the_fixed_list_is_unplaced_and_keeps_its_visible_line(self):
        memory(self.root, "odd", "x", "lms")
        self.index.write_text("- [Odd](odd.md) — kept\n", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write", "--show"])
        self.assertEqual(status, 1)
        self.assertIn("unplaced 1", out)
        self.assertIn("subject not on the fixed list: lms", out)
        self.assertIn("- [Odd](odd.md) — kept", self.index.read_text(encoding="utf-8"))

    def test_no_description_and_no_line_is_unplaced(self):
        memory(self.root, "bare", frontmatter=False)
        self.index.write_text("", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 1, out)

    def test_an_unreadable_header_with_a_line_is_counted_but_placed(self):
        # ADR 0391 ruling 9 fails only a memory that reaches no index.
        (self.root / "broken.md").write_text("---\nname broken\n---\n", encoding="utf-8")
        self.index.write_text("- [Broken](broken.md) — x\n", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write", "--show"])
        self.assertEqual(status, 0, out)
        self.assertIn("unread headers: 1", out)
        self.assertIn("unread header: broken.md", out)
        self.assertIn("- [Broken](broken.md) — x", self.index.read_text(encoding="utf-8"))

    def test_an_unreadable_header_keeps_its_subject_list_lines(self):
        path = memory(self.root, "listed", "x", "canvas")
        self.index.write_text("", encoding="utf-8")
        run([str(self.index), "--write"])
        path.write_text("---\nname listed\n---\n", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        self.assertIn("../listed.md", (self.root / "subjects" / "canvas.md").read_text(encoding="utf-8"))

    def test_an_unreadable_header_in_no_index_is_unplaced(self):
        (self.root / "broken.md").write_text("---\nname broken\n---\n", encoding="utf-8")
        self.index.write_text("", encoding="utf-8")
        status, out, _ = run([str(self.index), "--write", "--show"])
        self.assertEqual(status, 1, out)
        self.assertIn("the header cannot be read and the memory is in no index", out)

    def test_top_level_and_metadata_subjects_are_both_read_and_must_agree(self):
        (self.root / "top.md").write_text('---\nname: top\ndescription: "x"\nsubjects: canvas\n---\n',
                                          encoding="utf-8")
        self.index.write_text("- [Top](top.md) — x\n", encoding="utf-8")
        status, _, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0)
        self.assertIn("../top.md", (self.root / "subjects" / "canvas.md").read_text(encoding="utf-8"))
        (self.root / "top.md").write_text(
            '---\nname: top\ndescription: "x"\nsubjects: canvas\nmetadata:\n  subjects: none\n---\n',
            encoding="utf-8",
        )
        _, out, _ = run([str(self.index)])
        self.assertIn("unread headers: 1", out)

    def test_a_declared_memory_not_yet_rebuilt_is_unplaced_until_the_rebuild(self):
        memory(self.root, "new", "x", "canvas")
        self.index.write_text("", encoding="utf-8")
        status, out, _ = run([str(self.index)])
        self.assertEqual(status, 1, out)
        self.assertIn("files a rebuild would change: 2", out)
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)

    def test_counts_print_by_default_and_names_only_under_show(self):
        memory(self.root, "secretname", "x", "lms")
        self.index.write_text("", encoding="utf-8")
        _, out, _ = run([str(self.index)])
        self.assertNotIn("secretname", out)


class TheRuleBlock(Fixture):
    def test_install_places_the_block_at_the_top_and_write_refreshes_it(self):
        memory(self.root, "a", "x", "none")
        self.index.write_text("- [A](a.md) — x\n", encoding="utf-8")
        run([str(self.index), "--write", "--install-rule"])
        text = self.index.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(memory_index.BLOCK_START))
        stale = text.replace("Filing rule", "Old rule")
        self.index.write_text(stale, encoding="utf-8")
        _, out, _ = run([str(self.index)])
        self.assertIn("rule block: stale", out)
        run([str(self.index), "--write"])
        self.assertEqual(self.index.read_text(encoding="utf-8"), text)

    def test_install_needs_write(self):
        self.index.write_text("", encoding="utf-8")
        status, _, err = run([str(self.index), "--install-rule"])
        self.assertEqual(status, 2)
        self.assertIn("usage", err)


class TheRebuildConverges(Fixture):
    def files(self) -> dict[str, bytes]:
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in sorted(self.root.rglob("*")) if path.is_file()}

    def seed(self) -> None:
        memory(self.root, "pause", "pause in the box", "canvas, coursework")
        memory(self.root, "stash", "never stash", "none")
        memory(self.root, "old")
        self.index.write_text("- [Old](old.md) — kept\n- [Pause](pause.md) — old\n", encoding="utf-8")

    def test_running_twice_changes_nothing_the_second_time(self):
        self.seed()
        run([str(self.index), "--write", "--install-rule"])
        first = self.files()
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        self.assertEqual(self.files(), first)
        self.assertIn("files a rebuild would change: 0", run([str(self.index)])[1])

    def test_a_crash_after_the_lists_and_before_the_index_converges_on_rerun(self):
        self.seed()
        rule = memory_index.read_rule()
        result = memory_index.plan(self.index, rule)
        for key, text in result.lists.items():  # the crash: lists written, index not
            memory_index._write_atomic(self.root / "subjects" / f"{key}.md", text)
        run([str(self.index), "--write"])
        crashed = self.files()
        clean = Path(tempfile.mkdtemp(dir=self.root.parent))
        try:
            self.root, self.index = clean, clean / "MEMORY.md"
            self.seed()
            run([str(self.index), "--write"])
            self.assertEqual(self.files(), crashed)
        finally:
            import shutil
            shutil.rmtree(clean)

    def test_a_failed_write_leaves_no_temporary_file(self):
        target = self.root / "out.md"
        with mock.patch.object(Path, "replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                memory_index._write_atomic(target, "text")
        self.assertEqual(sorted(self.root.iterdir()), [])


class TheSubjectTable(unittest.TestCase):
    def test_an_aligned_separator_row_is_read_as_a_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "memory.md"
            source.write_text(
                "## Subjects\n\n| Subject | Name | Open when |\n| :--- | :---: | ---: |\n"
                "| canvas | Canvas | posting |\n\n## Installed block\n\n```text\nSubjects: {SUBJECTS}.\n```\n",
                encoding="utf-8",
            )
            self.assertEqual([s.key for s in memory_index.read_rule(source).subjects], ["canvas"])


class NotRead(Fixture):
    def test_a_missing_index_is_exit_two(self):
        status, _, err = run([str(self.index)])
        self.assertEqual(status, 2)
        self.assertIn("NOT READ", err)

    def test_an_unterminated_rule_block_refuses_and_writes_nothing(self):
        memory(self.root, "a")
        text = memory_index.BLOCK_START + "\nrule text\n- [A](a.md) — kept\n"
        self.index.write_text(text, encoding="utf-8")
        status, _, err = run([str(self.index), "--write"])
        self.assertEqual(status, 2)
        self.assertIn("malformed rule block markers", err)
        self.assertEqual(self.index.read_text(encoding="utf-8"), text)


class LinesThatAreNotMemoriesAreKept(Fixture):
    def test_external_links_anchors_blank_lines_and_trailing_spaces_survive(self):
        memory(self.root, "a")
        text = ("# Index\n\n- [A](a.md) — hook  \n- [Site](https://example.org/x) — external\n"
                "- [Part](a.md#section) — anchor\n")
        self.index.write_text(text, encoding="utf-8")
        status, out, _ = run([str(self.index), "--write"])
        self.assertEqual(status, 0, out)
        self.assertEqual(self.index.read_text(encoding="utf-8"), text)
        self.assertIn("0 dangling lines dropped", out)

    def test_the_trim_constant_holds_no_invisible_source_character(self):
        source = Path(memory_index.__file__).read_text(encoding="utf-8")
        self.assertEqual(len(source.splitlines()), source.count("\n"))


class TheSurveyCountsEveryFileARebuildWouldTouch(Fixture):
    def test_an_emptied_subject_list_counts_as_a_change(self):
        path = memory(self.root, "one", "first", "canvas")
        self.index.write_text("", encoding="utf-8")
        run([str(self.index), "--write"])
        path.write_text(path.read_text(encoding="utf-8").replace("subjects: canvas", "subjects: none"),
                        encoding="utf-8")
        _, out, _ = run([str(self.index)])
        self.assertIn("files a rebuild would change: 2", out)


class TheIndexIsReadAsOne(Fixture):
    def test_index_lines_include_every_subject_list(self):
        memory(self.root, "a", "x", "canvas")
        self.index.write_text("", encoding="utf-8")
        run([str(self.index), "--write"])
        lines = memory_index.index_lines(self.index)
        self.assertIn("- [a](../a.md) — x", lines)
        self.assertTrue(any(line.startswith("- [Canvas and LMS posting](subjects/canvas.md)") for line in lines))

    def test_measure_counts_utf16_code_units_after_a_javascript_trim(self):
        self.index.write_bytes("﻿ a\n\U0001f600\n\n".encode("utf-8"))
        self.assertEqual(memory_index.measure(self.index), (2, 4))


if __name__ == "__main__":
    unittest.main()
