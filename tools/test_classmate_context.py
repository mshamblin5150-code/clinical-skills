"""Classmate declarations at the public command seam. #1506.

All sources are synthetic; the committed template is the positive control.
phi-scan: synthetic
"""
import contextlib
import io
from pathlib import Path
from unittest import mock

import project_context as context
import repo_root
import discussion_reply_scan
from test_project_context import ProjectContextFixture
from test_discussion_reply_scan import Run


class ClassmateContextCommand(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.registry.write_text(f"MEMORY-INDEX: {self.memory}\nPROJECT: Atlas\n", encoding="utf-8")
        self.post = self.run / "maren.md"
        self.board = self.run / "board.md"
        self.attachment = self.run / "attachment.txt"
        self.other_post = self.run / "quill.md"
        for source in (self.post, self.board, self.attachment, self.other_post):
            source.write_text("Synthetic classmate words.\n", encoding="utf-8")
        template = Path(__file__).resolve().parents[1] / "fixtures/classmate-context/project-context.md.in"
        self.path = self.run / context.RECORD_NAME
        self.path.write_text(template.read_text(encoding="utf-8").format(
            post=self.post, board=self.board, attachment=self.attachment,
            other_post=self.other_post, run=self.run, memory=self.memory), encoding="utf-8")

    def command(self, *arguments):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = context.main([str(self.run), *(arguments or (
                "--write", "--submission", "response-maren.md"))])
        return status, output.getvalue()

    def change(self, old, new=""):
        self.path.write_text(self.path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_missing_post_is_refused(self):
        self.change(f"CLASSMATE-POST: response-maren.md -> {self.post}\n")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CLASSMATE-POST", report)

    def test_positive_control_writes_and_rechecks_both_keys(self):
        for key in ("response-maren.md", "response-quill.md"):
            status, report = self.command("--write", "--submission", key)
            self.assertEqual(status, 0, report)
            self.assertIn("classmate declarations: clean", report)
            status, report = self.command("--go-ahead", key)
            self.assertEqual(status, 0, report)
        written = self.path.read_text(encoding="utf-8")
        self.assertIn(f"CLASSMATE-POST: response-maren.md -> {self.post}", written)
        self.assertIn(f"OPENED: {self.attachment} | SHA256:", written)

    def test_missing_board_is_refused(self):
        self.change(f"CLASSMATE-BOARD: response-maren.md -> {self.board}\n")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CLASSMATE-BOARD", report)

    def test_missing_attachment_is_refused(self):
        self.change(f"CLASSMATE-ATTACHMENT: response-maren.md -> {self.attachment}\n")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CLASSMATE-ATTACHMENT", report)

    def test_duplicate_post_or_board_is_refused(self):
        original = self.path.read_text(encoding="utf-8")
        for name, path in (("POST", self.post), ("BOARD", self.board)):
            with self.subTest(name=name):
                self.path.write_text(original.replace(f"CLASSMATE-{name}: response-maren.md -> {path}",
                    f"CLASSMATE-{name}: response-maren.md -> {path}\n" * 2), encoding="utf-8")
                status, report = self.command()
                self.assertEqual(status, 1, report)
                self.assertIn("duplicated", report)

    def test_attachment_none_without_reason_is_refused(self):
        self.change(f"CLASSMATE-ATTACHMENT: response-maren.md -> {self.attachment}",
                    "CLASSMATE-ATTACHMENT: response-maren.md -> none")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("none needs a reason", report)

    def test_attachment_none_beside_path_is_refused(self):
        self.change("CONFIRMED:", "CLASSMATE-ATTACHMENT: response-maren.md -> none - no files\nCONFIRMED:")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("beside", report)

    def test_a_declared_path_not_opened_is_refused(self):
        self.change(f"OPENED: {self.post}\n")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("not OPENED", report)

    def test_a_searched_place_does_not_satisfy_the_read_requirement(self):
        self.change(f"## PLACE: {self.run}\nSTATE: read", f"## PLACE: {self.run}\nSTATE: searched")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("not OPENED", report)

    def test_other_key_cannot_stand_in_for_the_gated_key(self):
        self.change("CLASSMATE-POST: response-maren.md", "CLASSMATE-POST: response-quill.md")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("response-maren.md is missing", report)

    def test_confirmed_before_cutoff_reports_ungraded_count(self):
        self.change("CONFIRMED: 2026-10-11", "CONFIRMED: 2026-10-10")
        self.change(f"CLASSMATE-POST: response-maren.md -> {self.post}\n")
        for arguments in ((), ("--go-ahead", "response-maren.md")):
            status, report = self.command(*arguments)
            self.assertEqual(status, 0, report)
            self.assertIn("classmate declarations: not graded; pre-cutoff records: 1", report)

    def test_peer_critique_owes_its_own_classmate_lines(self):
        self.change("response-maren.md", "critique.md")
        status, report = self.command("--write", "--submission", "critique.md")
        self.assertEqual(status, 0, report)
        self.change(f"CLASSMATE-BOARD: critique.md -> {self.board}\n")
        status, report = self.command("--go-ahead", "critique.md")
        self.assertEqual(status, 1, report)
        self.assertIn("CLASSMATE-BOARD", report)

    def test_changed_classmate_declaration_breaks_the_digest(self):
        self.assertEqual(self.command()[0], 0)
        self.change(f"CLASSMATE-POST: response-quill.md -> {self.other_post}",
                    f"CLASSMATE-POST: response-quill.md -> {self.post}")
        status, report = self.command("--go-ahead", "response-maren.md")
        self.assertEqual(status, 1, report)
        self.assertIn("fingerprint", report)

    def test_multiple_attachment_paths_pass(self):
        self.change("CONFIRMED:", f"CLASSMATE-ATTACHMENT: response-maren.md -> {self.board}\nCONFIRMED:")
        status, report = self.command()
        self.assertEqual(status, 0, report)

    def test_heading_read_refuses_the_other_replys_opened_classmate_file(self):
        self.assertEqual(self.command()[0], 0)
        retained = self.path.read_text(encoding="utf-8")
        Run(self.run, posted=False)
        self.path.write_text(retained, encoding="utf-8")
        claims = self.run / "claims.md"
        claims.write_text("DATE: 2026-10-11\n", encoding="utf-8")
        heading = self.run / "heading-read.md"
        original = heading.read_text(encoding="utf-8")
        original = original.replace("0 factual, 0 clinician's own", "0 factual, 0 clinician's own, 1 item")
        original = "\n".join(line for line in original.splitlines() if not line.startswith("PAIR:"))
        original = original.replace("CONTEXT-DIGEST:", f"ITEM: paragraph 1 -> {{item}}\nCONTEXT-DIGEST:")
        original = original.replace("e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf", context.recorded_digest(self.run))
        for item, refused in ((self.post, False), (self.board, False), (self.other_post, True)):
            with self.subTest(item=item):
                heading.write_text(original.replace("{item}", str(item)), encoding="utf-8")
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    discussion_reply_scan.main([str(self.run)])
                self.assertIn(f"heading-read-unopened-item: {int(refused)}\n", output.getvalue())
