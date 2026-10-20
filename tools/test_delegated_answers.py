"""Tests for ``delegated_answers``: a delegated answer cites a written rule or says none.

Records are written in this file against a temporary checkout, so a quoted rule
is checked against text the test controls (ADR 0309 rulings 1 and 2).
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timedelta, timezone
import io
import hashlib
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401 -- the graders below reach artifact_lock
import delegated_answers as d
import differential_scan
import filled_vitals_census
import run_status_stop_hook
import test_clinical_coverage_approval as clinical_tests
from prose_bind import NAMING, bind


RULE_TEXT = (
    "**Not withheld.** A BMI of 26.5 from a filled height and weight produces\n"
    "`E66.3` and `Z68.26`, and the note carries both.\n"
)
SETTLED = (
    "## QUESTION: Code weight where no weight assessment was documented?\n"
    'RULE: skills/clinical-note/SKILL.md: "A BMI of 26.5 from a filled height and weight produces `E66.3` and `Z68.26`, and the note carries both."\n'
    "ANSWER: the codes stay, as the rule says.\n"
)
NONE = (
    "## QUESTION: Which of two equivalent follow-up intervals?\n"
    "RULE: none found\n"
    "ANSWER: two weeks, named at the go-ahead.\n"
)


class Checkout:
    def __enter__(self) -> tuple[Path, Path]:
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        skill = root / "skills" / "clinical-note"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(RULE_TEXT, encoding="utf-8")
        run = root / "run"
        run.mkdir()
        return root, run

    def __exit__(self, *exc: object) -> None:
        self.directory.cleanup()


def gate(record: str | None, submission: str | None = "a-test-submission") -> tuple[bool, str]:
    with Checkout() as (root, run):
        if record is not None:
            (run / d.RECORD).write_text(record, encoding="utf-8")
        token = d.completion_checks.MOMENTS.set({"approval": datetime(2026, 10, 19, tzinfo=timezone.utc)})
        try:
            return d.completion_gate(run, submission, root=root)[:2]
        finally:
            d.completion_checks.MOMENTS.reset(token)


def write_reader(run: Path, *, verdict="agrees", route="separate context") -> Path:
    brief = d.reader_brief(run)
    path = run / d.READER_RECORD
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"route": route, "answers_sha256": brief["answers_sha256"],
        "answers": [{"answer": answer["answer"], "verdict": verdict,
                     "disagreement": "Retain the recommendation." if verdict == "disagrees" else "",
                     "sections": {section["pointer"]: section["sha256"] for section in answer["sections"]}}
                    for answer in brief["answers"]] if route == "separate context" else []}), encoding="utf-8")
    return path


class TheBoundaryIsDeclaredOnce(unittest.TestCase):
    def test_the_docstring_points_at_the_object_without_copying_rows(self):
        doc = d.__doc__ or ""
        self.assertEqual(1, doc.count("delegated_answers.DECLARED_LIMITS"))
        self.assertEqual((), bind(d.DECLARED_LIMITS, doc, mode=NAMING))


class TheGate(unittest.TestCase):
    def test_it_waits_for_the_terminal_submission(self):
        failed, report = gate(SETTLED, submission=None)
        self.assertFalse(failed)
        self.assertIn("not graded", report.casefold())

    def test_an_absent_record_is_reported_and_never_graded(self):
        failed, report = gate(None)
        self.assertFalse(failed)
        self.assertIn("none recorded", report)

    def test_a_quoted_rule_and_a_none_found_answer_are_clean_and_counted(self):
        failed, report = gate(SETTLED + "\n" + NONE)
        self.assertFalse(failed, report)
        self.assertIn("2 recorded, 1 settled by a quoted written rule, 1 with no governing rule", report)

    def test_a_rule_the_cited_file_does_not_contain_is_a_finding(self):
        failed, report = gate(SETTLED.replace("carries both", "carries neither"))
        self.assertTrue(failed)
        self.assertIn("does not contain", report)

    def test_a_fragment_the_file_contains_is_not_a_governing_sentence(self):
        fragment = SETTLED.replace(
            '"A BMI of 26.5 from a filled height and weight produces `E66.3` and `Z68.26`, and the note carries both."',
            '"withheld"',
        )
        failed, report = gate(fragment)
        self.assertTrue(failed)
        self.assertIn("not a governing sentence", report)

    def test_a_rule_outside_the_written_rules_is_a_finding(self):
        failed, report = gate(SETTLED.replace("skills/clinical-note/SKILL.md", "scratch/notes.md"))
        self.assertTrue(failed)
        self.assertIn("outside", report)

    def test_a_missing_answer_or_a_bare_rule_is_a_finding(self):
        for record, why in (
            (NONE.replace("ANSWER: two weeks, named at the go-ahead.\n", ""), "ANSWER"),
            (NONE.replace("RULE: none found", "RULE: the skill says so"), "neither"),
        ):
            with self.subTest(why=why):
                failed, report = gate(record)
                self.assertTrue(failed)
                self.assertIn(why, report)

    def test_a_record_with_no_question_is_a_finding(self):
        failed, report = gate("delegated answers follow\n")
        self.assertTrue(failed)
        self.assertIn("no QUESTION record", report)

    def test_the_report_never_carries_the_question_or_the_answer(self):
        _, report = gate(SETTLED.replace("carries both", "carries neither") + NONE)
        self.assertNotIn("weight assessment", report)
        self.assertNotIn("two weeks", report)


class BothNoteGradersRunIt(unittest.TestCase):
    """Driven through each command, so a dropped call fails rather than a dropped string."""

    def test_each_completion_grader_reports_the_row_at_a_submission(self):
        for module in (filled_vitals_census, differential_scan):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                (run / "note-1.md").write_text(
                    "# Note 1, 45-year-old male\n\nVS: Ht 70 in, Wt 160 lb\n", encoding="utf-8"
                )
                (run / d.RECORD).write_text("RULE: none found\n", encoding="utf-8")
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    status = module.main([str(run), "--submission", "a-test-submission"])
                output = stdout.getvalue() + stderr.getvalue()
                self.assertEqual(1, status)
                self.assertIn(f"{d.EXPECTED_ROW}: finding - {d.RECORD} holds no QUESTION record", output)


class AnswerReader(unittest.TestCase):
    def test_committed_note_sections_are_resolved_without_rewriting_the_fixture(self):
        population = tuple(sorted((Path(__file__).resolve().parents[1] / "fixtures/filled-anchor/notes").glob("case-*.md")))
        self.assertEqual(12, len(population))
        for source in population:
            with self.subTest(note=source.name), Checkout() as (_root, run):
                note = run / source.name
                note.write_bytes(source.read_bytes())
                text = source.read_text(encoding="utf-8")
                # These source boundaries are selected independently of the extractor.
                assessment = text.index("## A:")
                plan = text.index("## P:")
                posting = text.index("## Medatrax entry")
                record = NONE + f"NOTE: {source.name}\nSECTIONS: A | P\n"
                answers, problems = d.answer_sections(run, record)
                self.assertEqual((), problems)
                self.assertEqual(1, len(answers))
                self.assertEqual(((source.name + "#a", text[assessment:plan]),
                                  (source.name + "#p", text[plan:posting])), answers[0].sections)
                # Removing the pointed-to heading must make this same member unreadable.
                note.write_text(text.replace("## P:", "## Changed section:", 1), encoding="utf-8")
                changed, problems = d.answer_sections(run, record)
                self.assertEqual((), changed)
                self.assertEqual(1, len(problems))

    def test_new_pointer_and_reader_checks_start_at_the_exact_approval_boundary(self):
        with Checkout() as (root, run):
            (run / d.RECORD).write_text(NONE, encoding="utf-8")
            cutoff = d.completion_checks.registry()[d.NOTE_SECTIONS][0]
            for moment, finding in ((cutoff - timedelta(microseconds=1), False), (cutoff, True)):
                token = d.completion_checks.MOMENTS.set({"approval": moment})
                try:
                    result = d.completion_gate(run, "synthetic-submission", root=root)
                    self.assertEqual(finding, result[0], result[1])
                finally:
                    d.completion_checks.MOMENTS.reset(token)
            (run / "note-1.md").write_text("P:\nRetain the recommendation.\n", encoding="utf-8")
            (run / d.RECORD).write_text(NONE + "NOTE: note-1.md\nSECTIONS: P\n", encoding="utf-8")
            for moment, unread, shown in ((cutoff - timedelta(microseconds=1), 0, "exempt"),
                                          (cutoff, 1, "not found")):
                token = d.completion_checks.MOMENTS.set({"approval": moment})
                try:
                    result = d.completion_gate(run, "synthetic-submission", root=root)
                    self.assertEqual((False, unread), (result[0], result[2]), result[1])
                    self.assertEqual(shown, d.verify_shown_answers(run, time.time(), transcripts=((), False)).state)
                finally:
                    d.completion_checks.MOMENTS.reset(token)

    def test_current_disagreement_is_a_finding_and_stale_or_missing_verdicts_are_unread(self):
        with Checkout() as (root, run):
            note = run / "note-1.md"
            note.write_text("## Plan\nRetain the recommendation.\n", encoding="utf-8")
            source = run / d.RECORD
            source.write_text(NONE + "NOTE: note-1.md\nSECTIONS: Plan\n", encoding="utf-8")
            reader = write_reader(run)
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertEqual((False, 0), (result[0], result[2]), result[1])
            intact = reader.read_text(encoding="utf-8")
            reader.write_text(intact.replace('"route":', '"route": "not run - no second context", "route":', 1), encoding="utf-8")
            duplicate = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertEqual((False, 1), (duplicate[0], duplicate[2]), duplicate[1])
            reader.write_text(intact, encoding="utf-8")
            payload = json.loads(reader.read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256(b"## Plan\nRetain the recommendation.\n").hexdigest(),
                             payload["answers"][0]["sections"]["note-1.md#p"])
            write_reader(run, verdict="disagrees")
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertTrue(result[0], result[1])
            self.assertEqual(0, result[2])
            note.write_text("## Plan\nChanged recommendation.\n", encoding="utf-8")
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertEqual((False, 1), (result[0], result[2]), result[1])
            write_reader(run)
            source.write_bytes(source.read_bytes() + b"\n")
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertEqual((False, 1), (result[0], result[2]), result[1])
            for damage in (b"{", b"[]", b"\xff"):
                reader.write_bytes(damage)
                result = d.completion_gate(run, "synthetic-submission", root=root)
                self.assertEqual((False, 1), (result[0], result[2]), result[1])
            write_reader(run, route="not run - no second context")
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertEqual((False, 1), (result[0], result[2]), result[1])

    def test_shift_pointers_and_blind_brief_retain_each_named_section_only(self):
        with Checkout() as (_root, run):
            for number in (1, 2):
                (run / f"note-{number}.md").write_text("## Subjective\nUnselected history.\n## Plan\nRetain the recommendation.\n", encoding="utf-8")
            (run / d.RECORD).write_text(NONE + "NOTE: shift\nSECTIONS: note-1.md#Plan | note-2.md#Plan\n", encoding="utf-8")
            brief = d.reader_brief(run)
            self.assertEqual(["note-1.md#p", "note-2.md#p"], [section["pointer"] for section in brief["answers"][0]["sections"]])
            serialized = json.dumps(brief)
            self.assertNotIn("Unselected history", serialized)
            self.assertNotIn("Which of two", serialized)
            self.assertNotIn("RULE:", serialized)
            self.assertEqual("ANSWER: two weeks, named at the go-ahead.", brief["answers"][0]["line"])

    def test_a_missing_independent_read_is_one_unread_answer(self):
        with Checkout() as (root, run):
            (run / "note-1.md").write_text("## Plan\nRetain the recommendation.\n", encoding="utf-8")
            (run / d.RECORD).write_text(NONE + "NOTE: note-1.md\nSECTIONS: Plan\n", encoding="utf-8")
            result = d.completion_gate(run, "synthetic-submission", root=root)
            self.assertFalse(result[0], result[1])
            self.assertEqual(1, result[2])
            self.assertIn("unread answers 1", result[1])

    def test_every_answer_names_a_real_note_and_section(self):
        with Checkout() as (root, run):
            (run / "note-1.md").write_text(
                "S:\nSynthetic history.\nO:\nSynthetic examination.\n"
                "A:\nSynthetic assessment.\nP:\nRetain the recommendation.\nCoding worksheet\n",
                encoding="utf-8",
            )
            for pointers in ("", "NOTE: delegated-answers.md\nSECTIONS: P\n",
                             "NOTE: note-1.md\nSECTIONS: missing\n"):
                with self.subTest(pointers=pointers):
                    (run / d.RECORD).write_text(NONE + pointers, encoding="utf-8")
                    result = d.completion_gate(run, "synthetic-submission", root=root)
                    self.assertTrue(result[0], result[1])
                    self.assertIn("note/section", result[1])


class ClinicalAnswerApproval(unittest.TestCase):
    def assert_delegation_survives_record_and_stop_read(self, fixture):
        expected = {name: fixture.item()[name] for name in
                    ("delegated_answers_verification", "delegated_answers_reason")}
        self.assertTrue(expected["delegated_answers_reason"])
        clinical_tests.approvals.record_agent_posting(
            fixture.run, skill=fixture.skill, submission="synthetic-note")
        items = run_status_stop_hook.approvals(fixture.run)
        self.assertEqual(1, len(items))
        self.assertEqual(expected, {name: items[0][1][name] for name in expected})
        self.assertEqual("agent", clinical_tests.approvals.posting_route(
            fixture.run, skill=fixture.skill, submission="synthetic-note"))

    def test_terminal_hosts_keep_the_answer_unread_member_despite_independent_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "note-1.md").write_text(
                "Start time 0800\nEnd time 0830\nS:\nSynthetic history.\nO:\nSynthetic examination.\n"
                "A:\nDifferential:\n1. Cough - R05.9: most likely.\nP:\nRetain the recommendation.\nCoding worksheet\n"
                "FILLED·asserted   BP 118/76 filled.\n", encoding="utf-8")
            (run / "shift-values.json").write_text(json.dumps({"start": "0800", "duration": {"hours": 8, "minutes": 0}}), encoding="utf-8")
            (run / d.RECORD).write_text(NONE + "NOTE: note-1.md\nSECTIONS: P\n", encoding="utf-8")
            write_reader(run, route="not run - no second context")
            for module in (differential_scan, filled_vitals_census):
                with self.subTest(module=module.__name__):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        status = module.main([str(run), "--submission", "synthetic-submission"])
                    self.assertEqual(1, status)  # The independent missing AAR remains a finding.
                    self.assertEqual(["unread remainder 1"], [line for line in stdout.getvalue().splitlines() if line.startswith("unread remainder ")])

    def test_real_paired_pregrades_combine_answer_and_visit_unread_members_once(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            note = run / "note-1.md"
            note.write_text("Start time 0800\nEnd time 0830\nS:\nSynthetic history.\nO:\nSynthetic examination.\n"
                            "A:\nDifferential:\n1. Cough - R05.9: most likely.\nP:\nRetain the recommendation.\nCoding worksheet\n"
                            "FILLED·asserted   BP 118/76 filled.\n", encoding="utf-8")
            (run / d.RECORD).write_text(NONE + "NOTE: note-1.md\nSECTIONS: P\n", encoding="utf-8")
            shift = run / "shift-values.json"
            shift.write_text(json.dumps({"start": "0800", "duration": {"hours": 8, "minutes": 0}}), encoding="utf-8")
            for skill in ("clinical-note", "batch-shift"):
                arguments = dict(skill=skill, submission="synthetic-submission", sources=(note,), grader_args=(str(run),))
                write_reader(run)
                prepared = clinical_tests.approvals.prepare(run, **arguments)
                self.assertEqual(["unread remainder 0"], [line for line in prepared.coverage if line.startswith("unread remainder ")])
                write_reader(run, route="not run - no second context")
                prepared = clinical_tests.approvals.prepare(run, **arguments)
                self.assertEqual(["unread remainder 1"], [line for line in prepared.coverage if line.startswith("unread remainder ")])
                original = note.read_text(encoding="utf-8")
                note.write_text(original.replace("End time 0830", "End time unreadable"), encoding="utf-8")
                prepared = clinical_tests.approvals.prepare(run, **arguments)
                self.assertEqual(["unread remainder 2"], [line for line in prepared.coverage if line.startswith("unread remainder ")])
                note.write_text(original, encoding="utf-8")
                write_reader(run, verdict="disagrees")
                with self.assertRaisesRegex(clinical_tests.approvals.ApprovalRecordError, "answer reader agrees 0, disagrees 1"):
                    clinical_tests.approvals.prepare(run, **arguments)

    def test_both_skills_require_the_exact_answer_line_in_each_transcript_shape(self):
        fixture = clinical_tests.ClinicalCoverageApproval("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        record = fixture.run / d.RECORD
        record.write_text(NONE + "NOTE: note-1.md\nSECTIONS: P\n", encoding="utf-8")
        write_reader(fixture.run)
        for skill in ("clinical-note", "batch-shift"):
            for codex in (False, True):
                with self.subTest(skill=skill, codex=codex):
                    fixture.skill = skill
                    (fixture.run / clinical_tests.approvals.RECORD).unlink(missing_ok=True)
                    prepared = fixture.prepare()
                    fixture.show("\n".join(prepared.coverage), codex=codex)
                    with self.assertRaisesRegex(clinical_tests.approvals.ApprovalRecordError, "delegated answer lines were not shown"):
                        fixture.approve()
                    exact = "\n".join(prepared.coverage) + "\nANSWER: two weeks, named at the go-ahead."
                    fixture.show(exact + " Extra interpretation.", codex=codex)
                    with self.assertRaisesRegex(clinical_tests.approvals.ApprovalRecordError, "delegated answer lines were not shown"):
                        fixture.approve()
                    stamp = time.time() + 10
                    os.utime(record, (stamp + 1, stamp + 1))
                    fixture.show(exact, codex=codex, shown_at=stamp, reply_at=stamp + 2)
                    with self.assertRaisesRegex(clinical_tests.approvals.ApprovalRecordError, "delegated answer lines were not shown"):
                        fixture.approve()
                    os.utime(record, (1, 1))
                    fixture.show(exact, codex=codex)
                    fixture.discovery.reset_mock()
                    fixture.approve()
                    fixture.discovery.assert_called_once()
                    self.assertEqual("verified", fixture.item()["delegated_answers_verification"])
                    self.assert_delegation_survives_record_and_stop_read(fixture)

    def test_unreadable_transcript_records_incomplete_instead_of_a_fabricated_quote(self):
        fixture = clinical_tests.ClinicalCoverageApproval("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        (fixture.run / d.RECORD).write_text(NONE + "NOTE: note-1.md\nSECTIONS: P\n", encoding="utf-8")
        write_reader(fixture.run)
        prepared = fixture.prepare()
        fixture.show("\n".join(prepared.coverage) + "\nANSWER: two weeks, named at the go-ahead.")
        fixture.transcript.unlink()
        fixture.approve()
        self.assertEqual("incomplete", fixture.item()["pregrade_status"])
        self.assertEqual("unreadable", fixture.item()["delegated_answers_verification"])
        self.assert_delegation_survives_record_and_stop_read(fixture)


if __name__ == "__main__":
    unittest.main()
