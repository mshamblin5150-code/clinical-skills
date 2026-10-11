"""Own-submission contracts through the project-context command. #1493.

phi-scan: synthetic
"""
import contextlib
import io
from unittest import mock

import project_context as context
import repo_root
from test_project_context import ProjectContextFixture


class OwnSubmissionCommand(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.registry.write_text(f"MEMORY-INDEX: {self.memory}\nPROJECT: Atlas\n", encoding="utf-8")

    def command(self):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output), \
                mock.patch("sys.stdin", io.StringIO("{}")):
            status = context.main([str(self.run), "--write", "--submission", "submission",
                                   "--service-payloads", "-"])
        return status, output.getvalue()

    def test_missing_own_submission_is_refused(self):
        self.record(self.memory_entry())
        path = self.run / context.RECORD_NAME
        path.write_text("\n".join(line for line in path.read_text().splitlines()
                                 if not line.startswith("OWN-SUBMISSION:")), encoding="utf-8")
        self.registry.write_text(f"MEMORY-INDEX: {self.memory}\nPROJECT: Atlas\n", encoding="utf-8")
        with mock.patch("sys.stdin", io.StringIO("{}")):
            status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("OWN-SUBMISSION", report)

    def declared_record(self, declaration):
        self.record(self.memory_entry(), header=(f"OWN-SUBMISSION: {declaration}",))

    def test_none_without_a_reason_is_refused(self):
        self.declared_record("none")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("needs a reason", report)

    def test_an_unopened_path_is_refused(self):
        self.declared_record(str(self.plan))
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("not OPENED", report)

    def test_a_declared_read_file_is_retained_and_passes_completion(self):
        self.declared_record(str(self.memory))
        status, report = self.command()
        self.assertEqual(status, 0, report)
        self.assertIn(f"OWN-SUBMISSION: {self.memory}", (self.run / context.RECORD_NAME).read_text())
        self.assertFalse(self.complete().finding)

    def test_duplicate_declarations_are_refused(self):
        self.record(self.memory_entry(), header=(
            f"OWN-SUBMISSION: {self.memory}", "OWN-SUBMISSION: none - no earlier submission",
        ))
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("OWN-SUBMISSION", report)

    def test_changing_the_declaration_invalidates_the_context_digest(self):
        self.declared_record(str(self.memory))
        self.assertEqual(self.command()[0], 0)
        path = self.run / context.RECORD_NAME
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(f"OWN-SUBMISSION: {self.memory}",
                                     "OWN-SUBMISSION: none - no earlier submission"), encoding="utf-8")
        result = self.complete()
        self.assertTrue(result.finding)
        self.assertIn("fingerprint", result.report)

    def test_none_has_a_bound_reason_even_without_a_project(self):
        path = self.run / context.RECORD_NAME
        path.write_text("PROJECT-CONTEXT: none - no project\n"
                        "OWN-SUBMISSION: none - no earlier submission\n"
                        "CONFIRMED: 2026-10-11\n", encoding="utf-8")
        self.assertEqual(self.command()[0], 0)
        self.assertFalse(self.complete().finding)
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("no earlier submission", "another reason"), encoding="utf-8")
        self.assertTrue(self.complete().finding)
