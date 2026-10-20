"""ADR 0419 legal forms through the four public graders. Synthetic only."""
from contextlib import redirect_stderr, redirect_stdout
from datetime import timedelta
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import unittest
import mechanics_test_support

setUpModule, tearDownModule = mechanics_test_support.module_hooks()

import completion_checks
import discussion_artifact as artifact
import discussion_reply_scan
import peer_critique_scan
import reference_scan
import assignment_docx
import assignment_docx_scan
import run_grader
from test_assignment_docx_scan import empty_population_input
from test_discussion_post_scan import Run as PostRun, BODY as POST_BODY
from test_discussion_reply_scan import Run as ReplyRun, BODY as REPLY_BODY
from test_peer_critique_scan import build_run, REFERENCES


ENTRY = "Patient rights, 42 C.F.R. § 482.13 (2024)."
FORMS = (
    ("Patient rights (2024)", False),
    ("(Patient rights, 2024)", False),
    ("42 C.F.R. § 482.13 (2024)", True),
    ("(42 C.F.R. § 482.13, 2024)", True),
    ("42 C.F.R. § 482.13", True),
)
KIND = artifact.LEGAL_CITATION_SECTION_FORM


def command(main, arguments):
    output, errors = io.StringIO(), io.StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        status = main(arguments)
    return status, output.getvalue() + errors.getvalue()


class LegalCitationFormGraders(unittest.TestCase):
    def test_post_resolves_each_form_and_refuses_only_section_forms(self):
        self.assertIn("(Patient rights, 2024)", POST_BODY)
        for form, refused in FORMS:
            with self.subTest(form=form), tempfile.TemporaryDirectory() as temp:
                run = PostRun(Path(temp))
                run.draft.write_text(POST_BODY.replace("(Patient rights, 2024)", form) + f"\n{ENTRY}\n", encoding="utf-8")
                status, report, errors = run.grade("--show")
                self.assertEqual(int(refused), status, report + errors)
                self.assertIn(f"{KIND}: {int(refused)}", report)
                self.assertIn("untraced-citation: 0", report)
                self.assertIn("untraced-number: 0", report)

    def test_reply_resolves_each_form_and_reports_the_actual_form_defect(self):
        for form, refused in FORMS:
            with self.subTest(form=form), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                ReplyRun(root)
                text = REPLY_BODY.replace("(Quill, 2024)", form).replace(
                    "Quill, R. (2024). Measuring usable access in community care. Journal of Care, 4(2), 10-18.", ENTRY)
                (root / "response-maren.md").write_text(text, encoding="utf-8")
                status, report = command(discussion_reply_scan.main, [temp, "--show"])
                self.assertIn(f"{KIND}: {int(refused)}", report)
                self.assertIn("unresolved-citation: 0", report)
                if refused:
                    self.assertEqual(1, status, report)
                    self.assertIn("write the legal source's name and the entry's year", report)

    def test_critique_resolves_each_form_and_reports_the_actual_form_defect(self):
        for form, refused in FORMS:
            with self.subTest(form=form), tempfile.TemporaryDirectory() as temp:
                root = build_run(root=Path(temp) / "run", posted=False,
                                 extra=f"\nThe rule applies {form}.\n",
                                 references=REFERENCES + f"\n{ENTRY}\n")
                status, report = command(peer_critique_scan.main, [str(root), "--show"])
                self.assertIn(f"{KIND}: {int(refused)}", report)
                self.assertIn("unresolved-citation: 0", report)
                if refused:
                    self.assertEqual(1, status, report)

    def test_draft_five_row_table_has_no_false_missing_source_or_unused_entry(self):
        for form, refused in (*FORMS, ("elsewhere", False)):
            with self.subTest(form=form), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "draft.md"
                path.write_text(f"The rule applies {form}.\n\n## References\n\n{ENTRY}\n", encoding="utf-8")
                status, report = command(reference_scan.main, [str(path), "--as-of", "2026-10-19", "--paper-language", "en", "--show"])
                self.assertEqual(int(refused or form == "elsewhere"), status, report)
                document = reference_scan.read_document(path.read_text(encoding="utf-8"))
                found = {finding.kind for finding in reference_scan.findings(document, None, "en")}
                self.assertEqual(refused, KIND in found)
                self.assertEqual(form == "elsewhere", reference_scan.UNCITED_ENTRY in found)
                self.assertNotIn(reference_scan.UNLISTED_CITATION, found)

    def test_start_rows_exempt_earlier_approvals_without_a_frozen_grade(self):
        modules = ("discussion_post_scan", "discussion_reply_scan", "peer_critique_scan", "reference_scan")
        for module in modules:
            with self.subTest(module=module):
                start, moment = completion_checks.registry()[module + ":" + KIND]
                self.assertEqual("approval", moment)
                finding = reference_scan.Finding(KIND, "body", "synthetic section")
                self.assertEqual((), completion_checks.filter_findings(
                    module, (finding,), moment=start - timedelta(seconds=1)))
                self.assertEqual((finding,), completion_checks.filter_findings(
                    module, (finding,), moment=start))
                self.assertEqual((finding,), completion_checks.filter_findings(module, (finding,)))

    def test_word_reference_grading_obeys_the_draft_row_start_without_a_freeze(self):
        start, _ = completion_checks.registry()["reference_scan:" + KIND]
        with tempfile.TemporaryDirectory() as temp:
            case = empty_population_input(Path(temp))
            artifact_path = Path(case.argv[2])
            spec = replace(
                assignment_docx.fixture_spec(),
                sections=(assignment_docx.Section("Purpose", ("The rule applies (42 C.F.R. § 482.13, 2024).",)),),
                references=(ENTRY,),
            )
            assignment_docx.build(spec, artifact_path, force=True)
            source = assignment_docx_scan.load(run_grader.Parsed(
                source=case.argv[0], values={"--docx": str(artifact_path)}))
            for approval, expected in ((start - timedelta(seconds=1), False), (start, True)):
                token = completion_checks.MOMENTS.set({"approval": approval})
                try:
                    scan = assignment_docx_scan.survey(source)
                finally:
                    completion_checks.MOMENTS.reset(token)
                self.assertEqual(expected, any(
                    finding.kind == assignment_docx_scan.REFERENCE_DEFECT
                    and "write the legal source's name and the entry's year" in finding.detail
                    for finding in scan.findings))


if __name__ == "__main__":
    unittest.main()
