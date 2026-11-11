"""Synthetic public-command checks for the E/M audit check-off renderer."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support

import ast
import contextlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import approval_record
from run_record_reader import OutboundTextError
import em_audit
import preapproval_answers
import repo_root
import review_manifest
from prose_bind import bind, NAMING
from test_review_manifest import passing_receipt, synthetic_run

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "em-audit-checkoff.md"
SKILL = ROOT / "skills" / "em-audit" / "SKILL.md"
CONSTANTS = dict(course="Synthetic course", preceptor="Synthetic preceptor", site="Synthetic site")
ELEMENTS = """  EM-PROBLEM: definition-acute-uncomplicated | counted | "Cough." | evaluated this visit
  EM-PROBLEM: definition-stable-chronic | not counted | "Hypertension." | history only, no evaluation documented
  EM-DATA: none | not counted | none | no test documented
  EM-RISK: table-low | counted | "Education: Rest." | rest and education
  EM-RULE: ADR 0308 ruling 1
  EM-ANSWER: note-1.q1
  EM-ECG: not applicable
  EM-MDM: problems low; data straightforward; risk low; mdm low
  EM-LEVEL: 99283
"""
PRIVATE = """ICD-10-CM R05.9 Cough
  ANCHOR: "Cough."
  SPECIFICITY: complete - the synthetic encounter documents no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
CPT 99283 Emergency visit
{elements}
## Coded, anchor was filled: confirm before submitting

None.

## Not coded, nothing established it

Synthetic refusal line
  NOT CODED: J18.9  Pneumonia, unspecified organism
  needs: imaging establishing pneumonia
  proposed instead: R05.9  Cough
"""
VISIBLE = """ICD-10-CM R05.9 Cough
CPT 99283 Emergency visit
E/M: 99283, low complexity, synthetic support [SOURCE: filled - data: chest radiograph]
"""
NOTE_EM = "E/M: Low complexity, synthetic support; 99283, emergency department service.\n\n"
QUESTION = "Synthetic question that changed no level: did you read the radiograph yourself?"
REPLY = "Synthetic reply: no, radiology read it."
VERIFIED = approval_record.ReplyVerification("verified", "synthetic reply", 4102444800.0)


def headings(text: str) -> list[str]:
    return re.findall(r"(?m)^## (.+?)[ \t]*$", text)


class RunFixture(unittest.TestCase):
    """A built synthetic run with a passing receipt and one recorded answer; no tests of its own."""

    elements = ELEMENTS

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.run = synthetic_run(self.root)
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=self.elements), encoding="utf-8")
        (self.run / "visible-worksheet-1.md").write_text(VISIBLE, encoding="utf-8")
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace(
            "## Medatrax entry fields", NOTE_EM + "## Medatrax entry fields"), encoding="utf-8")
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        passing_receipt(self.run)
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, QUESTION, [], REPLY)
        self.sheet = self.run / em_audit.OUTPUT_DIRECTORY / "note-1.md"
        self.rederivation = self.run / em_audit.OUTPUT_DIRECTORY / em_audit.REDERIVATION_DIRECTORY / "note-1.md"
        self.record(ELEMENTS)

    def write_private(self, text: str, encoding: str = "utf-8") -> None:
        """Write the private worksheet and rebuild the manifest, which binds its element lines."""
        (self.run / "worksheets/note-1.md").write_text(text, encoding=encoding)
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)

    def invoke(self, *args):
        command = [sys.executable, str(Path(__file__).with_name("em_audit.py")), str(self.run), *map(str, args)]
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def in_process(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = em_audit.main([str(self.run), *map(str, args)])
        return status, output.getvalue()

    def record(self, text: str) -> None:
        folder = self.run / em_audit.OUTPUT_DIRECTORY / em_audit.REDERIVATION_DIRECTORY
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "note-1.md").write_text(text, encoding="utf-8")

    def sources(self):
        return {path: path.read_bytes() for path in (self.run / "note-1.md", self.run / "visible-worksheet-1.md",
                                                     self.run / "worksheets/note-1.md")}


class CheckOffCommand(RunFixture):
    def test_default_prints_counts_only_and_writes_nothing(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for line in ("em-audit: notes in run 1; selected 1",
                     "codes rendered: icd10 1, cpt 0, hcpcs 0, em 1",
                     "codes without an anchor 0",
                     "worksheet blocks: filled-anchor 1, refusal 1, undocumented 0",
                     "element blocks: present 1, absent 0; findings 0",
                     "E/M filled marks 1",
                     "pre-approval answers shown 1",
                     "re-derivations: agree 1; differ 0; damaged 0; absent 0",
                     "element differences 0",
                     "nothing written (pass --write or --docx)",
                     "unread remainder 0"):
            self.assertIn(line, result.stdout)
        for private in ("Cough", "radiograph", "J18.9", "Example Person", "Synthetic reply"):
            self.assertNotIn(private, result.stdout)
        self.assertFalse(self.sheet.exists())
        self.assertEqual([], list(self.root.rglob("*.docx")))
        self.assertFalse((repo_root.output_root() / em_audit.WORD_DIRECTORY / self.run.name).exists())

    def test_written_check_off_renders_every_recorded_decision_in_template_order(self):
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("check-offs written 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        for expected in ("- [ ] ICD-10-CM R05.9 Cough", "  - Anchor: \"Cough.\"",
                         "  - Source: recorded (no SOURCE line)",
                         ">   NOT CODED: J18.9  Pneumonia, unspecified organism",
                         "- [ ] E/M code: 99283", "- Filled marks: [SOURCE: filled - data: chest radiograph]",
                         "- [ ] Problem: definition-acute-uncomplicated, counted; note text \"Cough.\"; reason: evaluated this visit",
                         "- [ ] Problem: definition-stable-chronic, not counted;",
                         "- [ ] Data: none, not counted; note text none; reason: no test documented",
                         "- MDM: problems low; data straightforward; risk low; two of three low",
                         "- Level: 99283", "- Answer relied on: note-1.q1", "- Rule applied: ADR 0308 ruling 1",
                         "- Question note-1.q1; levels named: none named; reply check: verified as a whole clinician message",
                         "> " + QUESTION, "> " + REPLY,
                         "- Setting: emergency department", "the re-derivation agrees with the worksheet.",
                         "Clinician signature:", "- Entry ids: not checked"):
            self.assertIn(expected, text)
        self.assertNotIn("The visible Coding worksheet", text)

    def test_template_carries_the_renderer_sections(self):
        self.assertEqual(list(em_audit.SECTIONS), headings(TEMPLATE.read_text(encoding="utf-8")))

    def test_a_matching_re_derivation_agrees_and_each_differing_element_is_listed(self):
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0", result.stdout)
        before = self.sources()
        self.record(ELEMENTS.replace("definition-stable-chronic | not counted", "definition-stable-chronic | counted")
                    .replace("problems low; data straightforward; risk low; mdm low",
                             "problems moderate; data straightforward; risk low; mdm low"))
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 0; differ 1", result.stdout)
        self.assertIn("element differences 3", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        for expected in ("- DIFFERS: Problem definition-stable-chronic not counted: in the worksheet block only",
                         "- DIFFERS: Problem definition-stable-chronic counted: in the re-derivation only",
                         "- DIFFERS: MDM problems: worksheet low, re-derivation moderate"):
            self.assertIn(expected, text)
        self.assertEqual(before, self.sources())

    def test_an_incomplete_re_derivation_is_unread_rather_than_agreeing(self):
        self.record(ELEMENTS.replace("  EM-LEVEL: 99283\n", ""))
        result = self.invoke()
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("agree 0; differ 0", result.stdout)

    def test_a_block_that_contradicts_itself_is_a_finding(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace(
            "risk low; mdm low", "risk low; mdm moderate")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("findings 1", result.stdout)
        self.assertIn("- FINDING: the MDM line states moderate, but two of its three elements meet low",
                      self.sheet.read_text(encoding="utf-8"))

    def test_entry_ids_are_checked_against_the_named_sheet(self):
        with mock.patch.object(em_audit, "sheet_ids", return_value={"definition-acute-uncomplicated", "table-low"}):
            status, output = self.in_process()
        self.assertEqual(1, status, output)
        self.assertIn("findings 1", output)

    def test_the_answers_record_absent_or_malformed_is_said_on_the_check_off(self):
        record = self.run / preapproval_answers.RECORD
        record.unlink()
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("No pre-approval answers record exists for this run.", text)
        self.assertIn("names a pre-approval answer, but the run has no readable answers record", text)
        record.write_text("{\"schema\": 1}", encoding="utf-8")
        result = self.invoke("--write")
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("could not be read", self.sheet.read_text(encoding="utf-8"))

    def test_an_answer_id_the_record_lacks_is_a_finding(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace(
            "note-1.q1", "note-1.q2")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("answer note-1.q2 is not a pre-approval answer of this note", self.sheet.read_text(encoding="utf-8"))

    def test_stale_records_refuse_and_write_nothing(self):
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace("Cough.", "Cough and fever."), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        self.assertFalse(self.sheet.exists())

    def test_note_selection_and_unknown_note(self):
        self.assertIn("selected 1", self.invoke("--note", 1).stdout)
        self.assertEqual(2, self.invoke("--note", 2).returncode)

    def test_word_export_is_on_demand_and_keeps_the_overwrite_refusal(self):
        folder = self.root / "export"
        result = self.invoke("--docx", "--output-dir", folder)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Word copies written 1", result.stdout)
        self.assertTrue((folder / "note-1.docx").is_file())
        self.assertFalse(self.sheet.exists())
        (folder / "note-1.docx").write_bytes(b"not a document this renderer wrote")
        refused = self.invoke("--docx", "--output-dir", folder)
        self.assertEqual(2, refused.returncode, refused.stdout + refused.stderr)
        self.assertIn("Word copy refused", refused.stdout)
        forced = self.invoke("--docx", "--output-dir", folder, "--force")
        self.assertEqual(0, forced.returncode, forced.stdout + forced.stderr)

    def test_completion_requires_a_re_derivation_and_a_current_check_off(self):
        self.rederivation.unlink()
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)
        self.assertIn("re-derivations absent 1", report)
        self.assertIn("check-offs missing or stale 1", report)
        self.record(ELEMENTS)
        self.assertEqual(0, self.invoke("--write").returncode)
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("the E/M audit check-offs: clean", report)
        not_graded = em_audit.completion_gate(self.run, None)
        self.assertFalse(not_graded[0])
        self.assertIn("not graded", not_graded[1])

    def test_declared_limits_are_named_by_the_skill_and_not_copied(self):
        self.assertEqual((), bind(em_audit.DECLARED_LIMITS, SKILL.read_text(encoding="utf-8"), mode=NAMING))


class PreservedWorksheetWithoutTheBlock(CheckOffCommand):
    """A worksheet written before the element block stays valid and renders its prose."""

    elements = ""

    def test_default_prints_counts_only_and_writes_nothing(self):
        result = self.invoke()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 0, absent 1; findings 0", result.stdout)

    def test_written_check_off_renders_every_recorded_decision_in_template_order(self):
        self.assertEqual(1, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        for expected in ("The private worksheet has no element block", "The visible Coding worksheet, as approved:",
                         "> E/M: 99283, low complexity, synthetic support", "> " + NOTE_EM.strip()):
            self.assertIn(expected, text)

    def test_a_matching_re_derivation_agrees_and_each_differing_element_is_listed(self):
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("level only, because the worksheet has no element block", self.sheet.read_text(encoding="utf-8"))

    def test_an_incomplete_re_derivation_is_unread_rather_than_agreeing(self):
        self.record(ELEMENTS.replace("  EM-LEVEL: 99283" + chr(10), ""))
        result = self.invoke()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)

    def test_word_export_is_on_demand_and_keeps_the_overwrite_refusal(self):
        result = self.invoke("--docx", "--output-dir", self.root / "export")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue((self.root / "export" / "note-1.docx").is_file())

    def test_a_block_that_contradicts_itself_is_a_finding(self):
        pass

    def test_entry_ids_are_checked_against_the_named_sheet(self):
        pass

    def test_an_answer_id_the_record_lacks_is_a_finding(self):
        pass

    def test_the_answers_record_absent_or_malformed_is_said_on_the_check_off(self):
        (self.run / preapproval_answers.RECORD).unlink()
        self.assertEqual(1, self.invoke("--write").returncode)
        self.assertIn("No pre-approval answers record exists for this run.", self.sheet.read_text(encoding="utf-8"))

    def test_completion_requires_a_re_derivation_and_a_current_check_off(self):
        self.record(ELEMENTS)
        self.assertEqual(1, self.invoke("--write").returncode)
        finding, report, _ = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertTrue(finding)
        self.assertIn("element blocks absent 1", report)


class ReviewFindings(RunFixture):
    """The code-review findings of 2026-11-11, each reproduced red before its fix."""

    def private(self, text: str) -> None:
        self.write_private(text, encoding="utf-8")

    def test_f1_every_em_spelling_the_code_reader_accepts_anchors_the_block(self):
        for spelling in ("cpt 99283 Emergency visit", "**E/M**: 99283 Emergency visit", "e/m: 99283 Emergency visit"):
            with self.subTest(spelling=spelling):
                self.private(PRIVATE.format(elements=ELEMENTS).replace("CPT 99283 Emergency visit", spelling))
                result = self.invoke()
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("element blocks: present 1, absent 0; findings 0", result.stdout)
                self.assertIn("unread remainder 0", result.stdout)

    def test_f2_a_step_four_heading_without_spaces_ends_the_copied_block(self):
        self.private(PRIVATE.format(elements=ELEMENTS)
                     .replace("## Coded, anchor was filled: confirm before submitting", "---CODED, ANCHOR WAS FILLED---")
                     .replace("## Not coded, nothing established it", "---NOT CODED, NOTHING ESTABLISHED IT---"))
        self.assertEqual(0, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        filled = text.split("## Codes resting on a filled anchor", 1)[1].split("## Codes refused", 1)[0]
        refused = text.split("## Codes refused", 1)[1].split("## Documentation", 1)[0]
        self.assertNotIn("NOT CODED", filled)
        self.assertIn("NOT CODED: J18.9", refused)

    def test_f3_a_multi_line_question_or_reply_stays_one_quoted_value(self):
        question = "First line of the question\n## injected question heading\n- injected bullet"
        reply = "First line of the reply\n\n> injected quote\n## injected reply heading"
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, question, ["99283"], reply)
        self.assertEqual(0, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        injected = [line for line in text.splitlines() if "injected" in line]
        self.assertEqual(4, len(injected))
        self.assertTrue(all(line.startswith("> ") for line in injected), injected)
        import docx_write
        self.assertEqual({"block-quotation"},
                         {block.kind for block in docx_write.blocks(text) if "injected" in block.text})

    def test_f4_the_block_under_either_anchor_is_read_and_two_blocks_are_a_finding(self):
        self.private(PRIVATE.format(elements="") + "\nE/M: 99283 low complexity\n" + ELEMENTS)
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 1, absent 0; findings 0", result.stdout)
        self.private(PRIVATE.format(elements=ELEMENTS) + "\nE/M: 99283 low complexity\n" + ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("- FINDING: the private worksheet carries 2 element blocks",
                      self.sheet.read_text(encoding="utf-8"))

    def test_f5_a_partly_unread_block_is_still_compared_element_by_element(self):
        self.private(PRIVATE.format(elements=ELEMENTS + "  EM-OPINION: an unrecognized line\n"))
        self.record(ELEMENTS.replace("| not counted | \"Hypertension.\"", "| counted | \"Hypertension.\""))
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertNotIn("the worksheet has no element block", text)
        self.assertIn("- DIFFERS: Problem definition-stable-chronic counted: in the re-derivation only", text)

    def test_f6_a_level_resting_on_an_unverified_answer_is_incomplete(self):
        (self.run / preapproval_answers.RECORD).unlink()
        self.assertEqual("unreadable", preapproval_answers.record(self.run, 1, QUESTION, [], REPLY)[1])
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("recorded unverified", self.sheet.read_text(encoding="utf-8"))

    def test_f8_the_rendered_text_is_the_text_that_was_validated(self):
        private = (self.run / "worksheets/note-1.md").resolve()
        reads = []
        original = review_manifest.read_text

        def counting(path):
            reads.append(Path(path).resolve())
            return original(path)

        with mock.patch.object(review_manifest, "read_text", side_effect=counting), \
                mock.patch.object(em_audit, "read_tool_record", wraps=em_audit.read_tool_record) as tool_reads:
            em_audit.render(self.run, [])
        self.assertEqual(1, reads.count(private))
        self.assertEqual(0, tool_reads.call_count)

    def test_f9_the_for_entry_region_is_read_by_the_validators_own_readers(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        called = {node.func.id for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertNotIn("system_key", defined)
        self.assertNotIn("entry_is_for_entry", called)
        self.assertTrue({"read_entries", "paired_entry"} <= called, called)

    def test_f10_the_terminal_grader_imports_the_gate_at_module_level_and_names_the_run_once(self):
        source = Path(em_audit.__file__).with_name("specificity_scan.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        top = {alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names}
        nested = [node for node in ast.walk(tree) if isinstance(node, ast.Import) and node not in tree.body
                  and any(alias.name == "em_audit" for alias in node.names)]
        self.assertIn("em_audit", top)
        self.assertEqual([], nested)
        self.assertEqual(1, source.count("source.directory.parent if source.directory.name == \"worksheets\""))


class SecondReviewFindings(RunFixture):
    """The second code-review findings of 2026-11-11, each reproduced red before its fix."""

    def with_answer_entries(self, *entries: dict) -> None:
        path = self.run / preapproval_answers.RECORD
        value = json.loads(path.read_text(encoding="utf-8"))
        value["answers"].extend(entries)
        path.write_text(json.dumps(value), encoding="utf-8")

    def fake_checkout(self) -> Path:
        checkout = self.root / "main-checkout"
        (checkout / ".git").mkdir(parents=True)
        return checkout

    def test_r1_a_note_without_a_re_derivation_or_an_element_block_is_not_complete(self):
        self.rederivation.unlink()
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 1", result.stdout)
        self.record(ELEMENTS)
        self.write_private(PRIVATE.format(elements=""), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 0, absent 1", result.stdout)

    def test_r2_an_answer_id_from_another_note_is_a_finding(self):
        self.with_answer_entries({"id": "note-2.q1", "note": 2, "question": QUESTION, "levels": [],
                                  "clinician_reply": REPLY, "verification": "verified",
                                  "reply_matched_at": 4102444800.0, "recorded_at": 4102444800.0})
        moved = ELEMENTS.replace("note-1.q1", "note-2.q1")
        self.write_private(PRIVATE.format(elements=moved), encoding="utf-8")
        self.record(moved)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("- FINDING: answer note-2.q1 is not a pre-approval answer of this note",
                      self.sheet.read_text(encoding="utf-8"))

    def test_r3_every_unreadable_answer_of_the_note_is_incomplete_coverage(self):
        self.assertEqual("unreadable", preapproval_answers.record(self.run, 1, "An uncited second question?", [], REPLY)[1])
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)

    def test_r4_a_word_copy_inside_the_main_checkout_goes_only_under_output(self):
        checkout = self.fake_checkout()
        self.record(ELEMENTS)
        with mock.patch.object(repo_root, "main_repo_root", return_value=checkout):
            status, output = self.in_process("--docx", "--output-dir", checkout / "reference" / "audit")
            self.assertEqual(2, status, output)
            self.assertIn("Word copy refused", output)
            self.assertEqual([], list(checkout.rglob("*.docx")))
            status, output = self.in_process("--docx", "--output-dir", checkout / "output" / "audit")
            self.assertEqual(0, status, output)
            self.assertTrue((checkout / "output" / "audit" / "note-1.docx").is_file())

    def test_r5_an_unknown_note_and_a_word_render_failure_each_say_what_happened(self):
        unknown = self.invoke("--note", 2)
        self.assertEqual(2, unknown.returncode)
        self.assertIn("is not an encounter of this run", unknown.stdout)
        self.assertNotIn("stale", unknown.stdout)
        self.record(ELEMENTS)
        with mock.patch("docx_write.write_docx", side_effect=OutboundTextError("line 3: U+0085")):
            status, output = self.in_process("--write", "--docx", "--output-dir", self.root / "export")
        self.assertEqual(2, status, output)
        self.assertIn("check-offs written 1", output)
        self.assertIn("Word copy refused", output)
        self.assertNotIn("stale", output)
        self.assertTrue(self.sheet.exists())

    def test_r8_manifest_for_reads_either_mode_when_asked(self):
        self.assertTrue(review_manifest.manifest_for(self.run, batch=None)["batch"])

    def test_r9_and_r10_em_audit_imports_its_readers_eagerly_and_quotes_with_one_helper(self):
        import specificity_scan
        import worksheet_grammar
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        nested = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                  and node not in tree.body and not any(
                      isinstance(parent, ast.If) and node in ast.walk(parent) for parent in tree.body)]
        self.assertEqual([], [ast.unparse(node) for node in nested if "docx_write" not in ast.unparse(node)
                              and "completion_checks" not in ast.unparse(node)])
        self.assertIs(worksheet_grammar.read_entries, specificity_scan.read_entries)
        defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("quoted_value", defined)



class ThirdReviewFindings(RunFixture):
    """The third code-review findings of 2026-11-11, each reproduced red before its fix."""

    def private(self, elements: str, tail: str = "") -> None:
        self.write_private(PRIVATE.format(elements=elements) + tail, encoding="utf-8")

    def test_t1_the_counterpart_of_an_unread_worksheet_line_is_not_a_difference(self):
        self.private(ELEMENTS.replace("history only, no evaluation documented",
                                      "history only | no evaluation documented"))
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0", result.stdout)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertNotIn("DIFFERS", self.sheet.read_text(encoding="utf-8"))
        self.record(ELEMENTS.replace("definition-acute-uncomplicated | counted",
                                     "definition-acute-uncomplicated | not counted"))
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("element differences 2", result.stdout)
        self.assertNotIn("definition-stable-chronic", "".join(
            line for line in self.sheet.read_text(encoding="utf-8").splitlines() if "DIFFERS" in line))

    def test_t2_an_em_line_after_the_step_four_blocks_is_not_quoted_inside_them(self):
        self.private("", "\nE/M: 99283 low complexity\n" + ELEMENTS)
        self.assertEqual(0, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        refused = text.split("## Codes refused", 1)[1].split("## Documentation", 1)[0]
        self.assertIn("NOT CODED: J18.9", refused)
        self.assertNotIn("EM-", refused)
        self.assertNotIn("E/M: 99283", refused)

    def test_t3_every_recorded_anchor_is_rendered(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            '  ANCHOR: "Cough."\n', '  ANCHOR: "Cough."\n  ANCHOR: "Coughing for two days."\n'), encoding="utf-8")
        self.assertEqual(0, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn('  - Anchor: "Cough."', text)
        self.assertIn('  - Anchor: "Coughing for two days."', text)

    def test_t4_the_word_copy_reproduces_asterisks_and_backticks_literally(self):
        marked = ELEMENTS.replace('"Education: Rest." | rest and education',
                                  '"Education: *recheck* rest." | rest ** education')
        self.private(marked)
        self.record(marked)
        question = "Synthetic question with `code` and *recheck* in it?"
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, question, [], "Reply with **bold** markers.")
        folder = self.root / "export"
        result = self.invoke("--docx", "--output-dir", folder)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        import docx_read
        text = "\n".join(docx_read.read_docx(folder / "note-1.docx"))
        for literal in ("*recheck* rest.", "rest ** education", "`code` and *recheck*", "**bold** markers."):
            self.assertIn(literal, text)

    def test_t5_an_unreadable_check_off_is_unread_rather_than_stale(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        self.sheet.write_bytes(b"\xff\xfe not utf-8")
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("check-offs missing or stale 0", report)
        self.assertIn("unreadable 1", report)

    def test_t8_an_unreadable_answer_of_another_note_is_not_claimed_as_counted_here(self):
        SecondReviewFindings.with_answer_entries(self, {"id": "note-2.q1", "note": 2, "question": QUESTION, "levels": [],
                                  "clinician_reply": REPLY, "verification": "unreadable",
                                  "reply_matched_at": None, "recorded_at": 4102444800.0})
        moved = ELEMENTS.replace("note-1.q1", "note-2.q1")
        self.private(moved)
        self.record(moved)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("- FINDING: answer note-2.q1 is not a pre-approval answer of this note", text)
        self.assertNotIn("counted with the answers below", text)

    def test_t9_word_options_without_docx_are_refused(self):
        for options in (("--force",), ("--output-dir", self.root / "export")):
            with self.subTest(options=options):
                result = self.invoke("--write", *options)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertIn("--docx", result.stderr)
                self.assertFalse(self.sheet.exists())

    def test_t10_the_tally_carries_no_dead_counters(self):
        tally = em_audit.Tally()
        self.assertFalse(hasattr(tally, "written") or hasattr(tally, "word"))



class FourthReviewFindings(RunFixture):
    """The fourth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def rebuilt(self, text: str) -> None:
        self.write_private(text)

    def section(self, text: str, title: str) -> str:
        return text.split("## " + title, 1)[1].split("\n## ", 1)[0]

    def test_u1_wrapped_field_values_are_read_whole(self):
        self.rebuilt(PRIVATE.format(elements=ELEMENTS)
                     .replace('  ANCHOR: "Cough."', '  ANCHOR: "Cough\n           for two days."')
                     .replace("  SPECIFICITY: complete - the synthetic encounter documents no further axis",
                              "  SPECIFICITY: complete - the synthetic encounter documents\n"
                              "               no further axis"))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn('  - Anchor: "Cough for two days."', text)
        self.assertIn("  - Specificity: complete - the synthetic encounter documents no further axis", text)

    def test_u1_a_detail_line_the_reader_cannot_place_is_unread(self):
        for stray in ("  EM-LEVEL: 99283\n  stray prose after the element block\n",
                      "  EM-LEVEL: 99283\n\n  NOTE: an orphaned detail line\n"):
            with self.subTest(stray=stray):
                self.rebuilt(PRIVATE.format(elements=ELEMENTS.replace("  EM-LEVEL: 99283\n", stray)))
                result = self.invoke()
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertIn("unread remainder 1", result.stdout)

    def test_u2_an_unreadable_answers_record_is_incomplete_not_a_finding(self):
        (self.run / preapproval_answers.RECORD).write_text("not json", encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("findings 0", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertNotIn("FINDING", text)
        self.assertIn("- Answer ids: not checked; the pre-approval answers record could not be read", text)

    def test_u3_the_em_entry_fields_reach_the_em_section(self):
        self.rebuilt(PRIVATE.format(elements='  ANCHOR: "Low complexity, synthetic support"\n'
                                    "  CONFIDENCE: verified against the synthetic sheet\n" + ELEMENTS))
        self.assertEqual(0, self.invoke("--write").returncode)
        em = self.section(self.sheet.read_text(encoding="utf-8"), "E/M level, element by element")
        for expected in ("- E/M line: CPT 99283 Emergency visit", '  - Anchor: "Low complexity, synthetic support"',
                         "  - Confidence: verified against the synthetic sheet"):
            self.assertIn(expected, em)

    def receipt_names(self, sheet: bytes) -> Path:
        import hashlib
        folder = self.root / "repository"
        (folder / "reference").mkdir(parents=True, exist_ok=True)
        (folder / "reference" / "synthetic-mdm.md").write_bytes(sheet)
        receipt = self.run / review_manifest.RECEIPT
        value = json.loads(receipt.read_text(encoding="utf-8"))
        value["sources"]["cpt"]["mdm_sheet_sha256"] = hashlib.sha256(sheet.replace(b"\r\n", b"\n")).hexdigest()
        receipt.write_text(json.dumps(value), encoding="utf-8")
        return folder

    def test_u4_the_named_sheet_is_read_by_its_parser_and_bound_to_the_receipt_digest(self):
        real = (ROOT / "reference" / "cpt-em-mdm-2026.md").read_bytes()
        folder = self.receipt_names(real)
        with mock.patch.object(em_audit, "REPOSITORY", folder):
            status, output = self.in_process("--write")
            self.assertEqual(0, status, output)
            self.assertNotIn("Entry ids: not checked", self.sheet.read_text(encoding="utf-8"))
            (folder / "reference" / "synthetic-mdm.md").write_bytes(real + b"\nEdited after the receipt.\n")
            status, output = self.in_process()
            self.assertEqual(2, status, output)
            self.assertIn("CPT MDM sheet", output)
        folder = self.receipt_names(b"## Entry: table-low\n## Entry: definition-stable-chronic\n")
        with mock.patch.object(em_audit, "REPOSITORY", folder):
            status, output = self.in_process()
        self.assertEqual(2, status, output)

    def test_u5_an_element_line_edited_after_the_manifest_refuses_the_check_off(self):
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace(
            "rest and education", "rest and education, edited after the manifest")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)

    def test_u5_a_manifest_without_the_element_fingerprint_is_unread(self):
        path = self.run / review_manifest.MANIFEST
        value = json.loads(path.read_text(encoding="utf-8"))
        del value["encounters"][0]["element_block_sha256"]
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("not bound to the manifest", self.sheet.read_text(encoding="utf-8"))

    def test_u7_a_coded_run_without_a_manifest_is_incomplete_at_submission(self):
        (self.run / review_manifest.MANIFEST).unlink()
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("incomplete", report)
        self.assertIn("not graded", em_audit.completion_gate(self.run, None)[1])
        (self.run / "worksheets/note-1.md").write_text("ICD-10-CM R05.9 Cough\n  ANCHOR: \"Cough.\"\n",
                                                       encoding="utf-8")
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("not graded", report)

    def test_u8_the_command_and_the_gate_share_one_finding_predicate(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name in ("status_of", "completion_gate"):
            calls = {node.func.id for node in ast.walk(functions[name])
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
            self.assertIn("has_finding", calls, name)
        cases = {"block_findings": 1, "differ": 1, "damaged": 1, "blocks_absent": 1, "absent": 1, "unread": 0}
        for attribute in cases:
            with self.subTest(attribute=attribute):
                tally = em_audit.Tally()
                setattr(tally, attribute, 1)
                command = em_audit.status_of(tally) == 1
                gate = em_audit.has_finding(tally, differences=False, stale=0)
                self.assertEqual(attribute not in ("unread", "differ"), gate)
                self.assertEqual(attribute != "unread", command)
        self.assertTrue(em_audit.has_finding(em_audit.Tally(), differences=False, stale=1))
        self.rederivation.unlink()
        status, _ = self.in_process()
        finding, _, _ = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((1, True), (status, finding))

    def test_u9_a_word_refusal_names_the_note_and_counts_the_copies_already_written(self):
        folder = self.root / "export"
        sheets = [em_audit.Sheet(1, "note-1", "# One\n"), em_audit.Sheet(2, "note-2", "# Two\n")]
        folder.mkdir()
        (folder / "note-2.docx").write_bytes(b"not a document this renderer wrote")
        with self.assertRaises(em_audit.WordExportStopped) as stopped:
            em_audit.export_word(self.run, sheets, folder, False)
        self.assertEqual((1, 2), (stopped.exception.written, stopped.exception.order))
        self.assertTrue((folder / "note-1.docx").is_file())
        tally = em_audit.Tally()
        with mock.patch.object(em_audit, "render", return_value=(tally, 2, sheets)):
            (folder / "note-1.docx").unlink()
            status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(2, status, output)
        self.assertIn("Word copies written 1", output)
        self.assertIn("Word copy refused at note 2", output)


if __name__ == "__main__":
    unittest.main()
