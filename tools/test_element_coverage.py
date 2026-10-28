"""Public synthetic record checks; no private corpus or durable approval writes."""

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import element_coverage
from prose_bind import NAMING, bind


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_reader_contract_names_its_limits_without_copying_them(self):
        sheet = (Path(__file__).resolve().parents[1] / "skills/course-assignment/references/element-coverage.md").read_text(encoding="utf-8")
        self.assertIn("element_coverage.DECLARED_LIMITS", sheet)
        self.assertEqual((), bind(element_coverage.DECLARED_LIMITS, sheet, mode=NAMING))


class ElementCoverage(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        self.artifact = self.run / "assignment.docx"
        self.artifact.write_bytes(b"Synthetic built artifact containing an answer.")

    def records(self):
        (self.run / "assignment-2026-10-28.md").write_text("Synthetic prompt: explain the comparison. Points: 10.\n", encoding="utf-8")
        (self.run / "elements.md").write_text("- E1: Explain the synthetic comparison.\n", encoding="utf-8")
        if not (self.run / "bar.md").exists():
            (self.run / "bar.md").write_text("SIGNED: 2026-10-28\nOMISSION: Leave out the optional comparison.\n", encoding="utf-8")
        self.rubric = {"assignment_points": "10", "criteria": [
            {"id": "R1", "criterion": "Comparison", "descriptor": "Explain the comparison.", "points": "10"}
        ], "points_exception": ""}
        self.record = {"artifact": self.artifact.name, "artifact_sha256": sha256(self.artifact.read_bytes()).hexdigest(),
            "elements": [{"id": "C1", "requirement": "Explain the comparison.", "origin": "rubric", "rubric_id": "R1",
                          "status": "answered", "location": "body paragraph 1", "bar_quote": "", "remark": ""}],
            "reconciliation": [{"draft_id": "E1", "element_ids": ["C1"]}]}
        self.save()

    def save(self):
        (self.run / "rubric.json").write_text(json.dumps(self.rubric), encoding="utf-8")
        self.record["inputs_sha256"] = {name: sha256((self.run / name).read_bytes()).hexdigest()
            for name in ("rubric.json", "elements.md", "bar.md", "assignment-2026-10-28.md")}
        (self.run / "element-coverage.json").write_text(json.dumps(self.record), encoding="utf-8")

    def test_a_missing_independent_read_refuses_the_artifact(self):
        result = element_coverage.survey(self.run, self.artifact)
        self.assertTrue(result.failed)
        self.assertIn("missing", result.report)

    def test_a_complete_read_accepts_both_built_artifact_branches(self):
        for suffix in (".docx", ".pptx"):
            with self.subTest(suffix=suffix):
                self.artifact = self.artifact.with_suffix(suffix)
                self.artifact.write_bytes(b"Synthetic built artifact containing an answer.")
                self.records()
                result = element_coverage.survey(self.run, self.artifact)
                self.assertFalse(result.failed, result.report)
                self.assertIn("listed 1; answered 1; omitted 0", result.report)

    def test_a_planted_missing_element_refuses_instead_of_becoming_a_remark(self):
        self.records()
        self.record["elements"][0].update(status="missing", location="")
        self.save()
        result = element_coverage.survey(self.run, self.artifact)
        self.assertTrue(result.failed)
        self.assertIn("unanswered", result.report)

    def test_any_later_artifact_repair_invalidates_the_read(self):
        self.records()
        self.artifact.write_bytes(b"Repaired layout, requiring a fresh coverage read.")
        result = element_coverage.survey(self.run, self.artifact)
        self.assertTrue(result.failed)
        self.assertIn("digest", result.report)

    def sign_bar(self):
        copy = self.run / "signed-bars" / "bar-1.md"
        copy.parent.mkdir(exist_ok=True)
        copy.write_bytes((self.run / "bar.md").read_bytes())
        history = {"signatures": [{"copy": "signed-bars/bar-1.md", "sha256": sha256(copy.read_bytes()).hexdigest(),
                   "clinician_reply": "Keep the stated omission.", "reply_verification": "verified"}]}
        (self.run / "bar-signatures.json").write_text(json.dumps(history), encoding="utf-8")

    def test_a_deliberate_omission_needs_the_exact_current_signed_bar_line(self):
        self.records()
        self.record["elements"][0].update(status="omitted", location="", bar_quote="OMISSION: Leave out the optional comparison.")
        self.save()
        self.sign_bar()
        result = element_coverage.survey(self.run, self.artifact)
        self.assertFalse(result.failed, result.report)
        self.assertIn("omitted 1", result.report)
        self.assertIn("Explain the comparison.", result.report)
        self.record["elements"][0]["bar_quote"] = "OMISSION: A permission the bar never gave."
        self.save()
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)
        self.record["elements"][0]["bar_quote"] = "OMISSION: Leave out the optional comparison."
        self.save()
        (self.run / "bar-signatures.json").unlink()
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_a_dropped_rubric_row_fails_the_independent_point_sum(self):
        self.records()
        self.rubric["assignment_points"] = "20"
        self.save()
        result = element_coverage.survey(self.run, self.artifact)
        self.assertTrue(result.failed)
        self.assertIn("points", result.report)
        self.rubric["points_exception"] = "The faculty includes an unscored criterion outside these ten points."
        self.save()
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)

    def test_every_rubric_and_drafting_identifier_must_be_reconciled(self):
        self.records()
        self.record["reconciliation"] = []
        self.save()
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)
        self.records()
        self.record["elements"][0]["rubric_id"] = "unknown"
        self.save()
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_thin_coverage_is_a_numbered_reader_remark_and_not_a_refusal(self):
        import reader_remarks
        self.records()
        self.record["elements"][0].update(status="thin", remark="The comparison needs a concrete example.")
        self.save()
        result = element_coverage.survey(self.run, self.artifact)
        self.assertFalse(result.failed, result.report)
        self.assertEqual("The comparison needs a concrete example.", reader_remarks.read_report(result.report)[0].text)
        self.assertIn("listed 1", reader_remarks.coverage_lines(result.report)[0])

    def test_malformed_rows_cannot_claim_clean_coverage(self):
        for field, value in (("status", "invented"), ("requirement", ""), ("id", []), ("location", None)):
            with self.subTest(field=field):
                self.records()
                self.record["elements"][0][field] = value
                self.save()
                self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)
        for points in ("NaN", "Infinity", "-10", True):
            with self.subTest(points=points):
                self.records()
                self.rubric["criteria"][0]["points"] = points
                self.rubric["points_exception"] = "An exception cannot make malformed arithmetic valid."
                self.save()
                self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_no_rubric_is_explicit_and_does_not_erase_prompt_elements(self):
        self.records()
        self.rubric.update(criteria=[], no_rubric="The assignment has no rubric.")
        self.record["elements"][0].update(origin="prompt", rubric_id="")
        self.save()
        self.assertFalse(element_coverage.survey(self.run, self.artifact).failed)
        del self.rubric["no_rubric"]
        self.save()
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_preapproval_enforces_the_read_and_legacy_approval_reports_not_graded(self):
        from datetime import datetime, timezone
        import completion_checks
        self.assertTrue(element_coverage.completion_gate(self.run, self.artifact).failed)
        token = completion_checks.MOMENTS.set({"approval": datetime(2020, 1, 1, tzinfo=timezone.utc)})
        try:
            result = element_coverage.completion_gate(self.run, self.artifact, "assignment")
            self.assertFalse(result.failed)
            self.assertIn("not graded", result.report)
        finally:
            completion_checks.MOMENTS.reset(token)

    def test_changed_source_capture_or_drafting_list_invalidates_the_read(self):
        for name in ("rubric.json", "elements.md", "assignment-2026-10-28.md"):
            with self.subTest(name=name):
                self.records()
                with (self.run / name).open("a", encoding="utf-8") as stream:
                    stream.write("\nChanged source after the read.\n")
                self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_duplicate_json_fields_and_identifiers_are_refused(self):
        self.records()
        path = self.run / "element-coverage.json"
        path.write_text('{"artifact":"wrong.docx",' + path.read_text()[1:], encoding="utf-8")
        self.assertTrue(element_coverage.survey(self.run, self.artifact).failed)

    def test_the_grade_is_blocked_without_the_read_even_before_a_submission_key(self):
        import run_grader
        grade = run_grader.Grade(scan=None, source=str(self.run))
        result = element_coverage.apply_completion_gate(grade, self.run, self.artifact)
        self.assertTrue(result.findings_failed)
        self.records()
        self.assertFalse(element_coverage.apply_completion_gate(grade, self.run, self.artifact).findings_failed)

    def test_both_real_branch_graders_carry_the_current_coverage_report(self):
        from contextlib import ExitStack
        from unittest import mock
        import zipfile
        import assignment_docx
        import assignment_docx_scan
        import deck_scan
        import run_grader
        from test_assignment_bar import DOCX_BAR
        from test_deck_scan import Run, slide_xml
        for adapter, suffix in ((assignment_docx_scan, ".docx"), (deck_scan, ".pptx")):
            with self.subTest(branch=suffix), ExitStack() as stack:
                if suffix == ".docx":
                    self.artifact = self.run / "assignment.docx"
                    with zipfile.ZipFile(self.artifact, "w") as archive:
                        for name, value in assignment_docx.parts(assignment_docx.fixture_spec()).items():
                            archive.writestr(name, value)
                    (self.run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
                    (self.run / "claims.md").write_text("DATE: 2026-10-28\n", encoding="utf-8")
                    option = "--docx"
                else:
                    fixture = Run(self.run)
                    fixture.write_deck((slide_xml("Synthetic title"),))
                    self.artifact = fixture.deck
                    option = "--pptx"
                parsed = run_grader.parse(adapter.GRADER, [str(self.run), option, str(self.artifact), "--paper-language", "en"])
                source = adapter.load(parsed)
                for module, function in ((adapter.voice_model_identity, "apply_completion_gate"),
                        (adapter.recorded_image_match, "apply_coursework_gates"),
                        (adapter.project_context, "apply_completion_gate"),
                        (adapter.lms_attachments, "apply_completion_gate")):
                    stack.enter_context(mock.patch.object(module, function, side_effect=lambda grade, *a, **kw: grade))
                stack.enter_context(mock.patch.object(adapter.aar_scan, "completion_gate", return_value=(False, "synthetic AAR boundary")))
                if suffix == ".docx":
                    stack.enter_context(mock.patch.object(adapter.coursework_mechanics, "apply_grade", side_effect=lambda grade, *a, **kw: grade))
                self.records()
                result = adapter.grade(source, parsed)
                self.assertTrue(any(element_coverage.EXPECTED_ROW + ": clean" in report for report in result.reports))
                (self.run / "element-coverage.json").unlink()
                result = adapter.grade(source, parsed)
                self.assertTrue(result.findings_failed)
                self.assertTrue(any(element_coverage.EXPECTED_ROW + ": finding" in report for report in result.reports))


if __name__ == "__main__":
    unittest.main()
