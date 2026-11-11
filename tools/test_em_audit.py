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
from prose_bind import bind, NAMING, ProseBind
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
        name_the_committed_sheet(self.run)
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, QUESTION, [], REPLY)
        em_audit.reset_sheet_cache()
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
                         "Clinician signature:"):
            self.assertIn(expected, text)
        self.assertNotIn("The visible Coding worksheet", text)
        self.assertNotIn("Entry ids: not checked", text)

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
        # Tenth review: an unmappable refused line now withholds the item comparison, so this uses a
        # refused line that maps to an element (an empty EM-RULE value).
        self.private(PRIVATE.format(elements=ELEMENTS + "  EM-RULE:\n"))
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

    def test_f10_the_terminal_grader_imports_the_gate_lazily_and_names_the_run_once(self):
        # Seventh review: the module-level import loaded the approval and manifest stack on every
        # specificity_scan import; the load-order cycle it once guarded is handled inside em_audit.
        source = Path(em_audit.__file__).with_name("specificity_scan.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        top = {alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names}
        # Eleventh review: the import sits in em_audit_gate, after the checks that need no em_audit.
        gate = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "em_audit_gate")
        nested = [node for node in ast.walk(tree) if isinstance(node, ast.Import)
                  and any(alias.name == "em_audit" for alias in node.names)]
        self.assertEqual(nested, [node for node in ast.walk(gate) if node in nested])
        self.assertNotIn("em_audit", top)
        self.assertEqual(1, len(nested))
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

    def test_u4_the_named_sheet_is_read_by_its_parser_and_bound_to_the_receipt_digest(self):
        import cpt_mdm_sheet
        status, output = self.in_process("--write")
        self.assertEqual(0, status, output)
        self.assertNotIn("Entry ids: not checked", self.sheet.read_text(encoding="utf-8"))
        em_audit.reset_sheet_cache()
        with mock.patch.object(em_audit.cpt_mdm_sheet, "read_entries", wraps=cpt_mdm_sheet.read_entries) as parser:
            self.in_process()
        self.assertEqual(1, parser.call_count)
        em_audit.reset_sheet_cache()
        with mock.patch.object(em_audit.cpt_mdm_sheet, "read_entries", side_effect=ValueError("no entries")):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("CPT MDM sheet", output)

    def test_u5_an_element_line_edited_after_the_manifest_refuses_the_check_off(self):
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace(
            "rest and education", "rest and education, edited after the manifest")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((True, 0), (finding, unread), report)  # eleventh review: a finding, not unread

    def test_u5_a_manifest_without_the_element_fingerprint_is_unread(self):
        path = self.run / review_manifest.MANIFEST
        value = json.loads(path.read_text(encoding="utf-8"))
        del value["encounters"][0]["private_worksheet_sha256"]
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



def name_the_committed_sheet(run: Path, filename: str = "cpt-em-mdm-2026.md") -> None:
    """Point the synthetic receipt at a sheet under reference/, with the receipt's own fingerprint rule."""
    import coding_freshness
    path = ROOT / "reference" / filename
    receipt = run / review_manifest.RECEIPT
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["sources"]["cpt"]["mdm_sheet_filename"] = filename
    if path.is_file():
        value["sources"]["cpt"]["mdm_sheet_sha256"] = coding_freshness.committed_sheet_sha256(path)
    receipt.write_text(json.dumps(value), encoding="utf-8")


class FifthReviewFindings(RunFixture):
    """The fifth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_v1_a_unicode_line_separator_above_an_entry_keeps_its_fields(self):
        self.write_private("Synthetic preface" + chr(0x2028) + "continued\n" + PRIVATE.format(elements=ELEMENTS))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 0", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn('  - Anchor: "Cough."', text)
        self.assertIn("  - Specificity: complete - the synthetic encounter documents no further axis", text)

    def test_v2_a_missing_sheet_the_receipt_names_is_incomplete_coverage(self):
        name_the_committed_sheet(self.run, "absent-mdm-sheet.md")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("- Entry ids: not checked", self.sheet.read_text(encoding="utf-8"))
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)

    def two_sheets(self):
        return [em_audit.Sheet(1, "note-1", "# One\n"), em_audit.Sheet(2, "note-2", "# Two\n")]

    def test_v3_a_refused_check_off_names_the_note_and_counts_those_written(self):
        (self.run / em_audit.OUTPUT_DIRECTORY / "note-2.md").mkdir(parents=True)
        with mock.patch.object(em_audit, "render", return_value=(em_audit.Tally(), 2, self.two_sheets())):
            status, output = self.in_process("--write")
        self.assertEqual(2, status, output)
        self.assertIn("check-offs written 1", output)
        self.assertIn("check-offs refused at note 2", output)
        self.assertTrue(self.sheet.is_file())

    def test_v4_the_sheet_fingerprint_is_the_receipts_own_rule(self):
        import coding_freshness
        name_the_committed_sheet(self.run)
        # Eighth review: the receipt's rule is applied to the sheet's committed history, not HEAD alone.
        with mock.patch.object(coding_freshness, "sheet_sha256", wraps=coding_freshness.sheet_sha256) as rule:
            status, output = self.in_process("--write")
        self.assertEqual(0, status, output)
        self.assertGreater(rule.call_count, 0)
        self.assertNotIn("Entry ids: not checked", self.sheet.read_text(encoding="utf-8"))
        em_audit.reset_sheet_cache()
        with mock.patch.object(coding_freshness, "sheet_sha256", return_value="0" * 64):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("unread remainder 1", output)
        em_audit.reset_sheet_cache()
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("CPT MDM sheet", output)

    def test_v6_a_refused_check_off_says_the_word_copies_were_not_attempted(self):
        (self.run / em_audit.OUTPUT_DIRECTORY / "note-2.md").mkdir(parents=True)
        with mock.patch.object(em_audit, "render", return_value=(em_audit.Tally(), 2, self.two_sheets())):
            status, output = self.in_process("--write", "--docx", "--output-dir", self.root / "export")
        self.assertEqual(2, status, output)
        self.assertIn("Word copies not attempted", output)
        self.assertFalse((self.root / "export").exists())

    def bill_ecg(self, code: str, ecg: str) -> None:
        inputs = self.run / "inputs.json"
        rows = json.loads(inputs.read_text(encoding="utf-8"))
        rows[0]["codes"]["cpt"] = [code]
        inputs.write_text(json.dumps(rows), encoding="utf-8")
        entry = f"CPT {code} Electrocardiogram\n"
        (self.run / "visible-worksheet-1.md").write_text(VISIBLE.replace("CPT 99283", entry + "CPT 99283"),
                                                          encoding="utf-8")
        elements = ELEMENTS.replace("EM-ECG: not applicable", "EM-ECG: " + ecg)
        self.write_private(PRIVATE.format(elements=elements).replace("CPT 99283", entry + "CPT 99283"))
        self.record(elements)
        passing_receipt(self.run)
        name_the_committed_sheet(self.run)

    def test_v7_an_ecg_limb_contradicting_the_billed_code_is_a_finding(self):
        for code, ecg, finding in (
                ("93005", "ADR 0443: 93005 billed while the findings are pending; one test ordered", False),
                ("93000", "ADR 0443: 93000, his own read; counts nothing toward data", False),
                ("93005", "not applicable", True),
                ("93005", "ADR 0443: 93000, his own read; counts nothing toward data", True),
                ("93000", "ADR 0443: 93005 billed while the findings are pending; one test ordered", True)):
            with self.subTest(code=code, ecg=ecg):
                self.bill_ecg(code, ecg)
                result = self.invoke("--write")
                self.assertEqual(1 if finding else 0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(finding, "- FINDING: the worksheet bills" in self.sheet.read_text(encoding="utf-8"))

    def test_v8_the_answer_guard_has_no_empty_branch(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "block_findings")
        self.assertEqual([], [node for node in ast.walk(function) if isinstance(node, ast.Pass)])



class SixthReviewFindings(RunFixture):
    """The sixth code-review findings of 2026-11-11, each reproduced red before its fix."""

    UNDOCUMENTED = ("## Undocumented, would support a more specific code\n\n"
                    "CPT 99284 would be supported with documented time\n"
                    "History documented only in part.\n\n")

    def section(self, text: str, title: str) -> str:
        return text.split("## " + title, 1)[1].split("\n## ", 1)[0]

    def test_x1_an_entry_inside_a_step_four_block_never_ends_its_quotation(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "## Coded, anchor was filled", self.UNDOCUMENTED + "## Coded, anchor was filled"))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.sheet.read_text(encoding="utf-8")
        documentation = self.section(text, "Documentation that would support a more specific code")
        self.assertIn("> CPT 99284 would be supported with documented time", documentation)
        self.assertIn("> History documented only in part.", documentation)
        self.assertNotIn("E/M line: CPT 99284", self.section(text, "E/M level, element by element"))

    def test_x1_an_em_line_after_the_blocks_still_ends_the_last_one(self):
        # The manifest selects an E/M identity after the icd10-cpt step 4 blocks only from an E/M: label line.
        for tail in ("\nE/M: 99283 low complexity\n" + ELEMENTS,
                     "\nE/M: 99283 low complexity\n  NOTE: support restated\n" + ELEMENTS):
            with self.subTest(tail=tail.splitlines()[2]):
                self.write_private(PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n", "") + tail)
                self.assertEqual(0, self.invoke("--write").returncode)
                refused = self.section(self.sheet.read_text(encoding="utf-8"),
                                       "Codes refused, with what would establish them")
                self.assertIn("NOT CODED: J18.9", refused)
                self.assertNotIn("EM-", refused)
                self.assertNotIn("99283", refused)

    def test_x1_the_check_off_quotes_the_grader_lines_less_the_em_section(self):
        # Eleventh review: the graders keep main's readers; only the check-off leaves the E/M section out.
        import anchor_scan
        import refusal_scan
        import worksheet_grammar
        section = {"E/M: 99283 low complexity", *ELEMENTS.splitlines()}
        for text in (PRIVATE.format(elements=ELEMENTS) + "\nE/M: 99283 low complexity\n" + ELEMENTS,
                     SeventhReviewFindings.SYNTHETIC):
            with self.subTest(text=text[:20]):
                for heading, kind, lines in (
                        (worksheet_grammar.REFUSAL_HEADING, "refusal", refusal_scan._block_lines(text.splitlines())[0]),
                        (worksheet_grammar.BLOCK_HEADING, "filled", anchor_scan._block_lines(text)[0])):
                    self.assertEqual("\n".join(line for line in lines if line not in section).strip("\n"),
                                     worksheet_grammar.block_text(text, heading, kind))

    def test_x3_a_refused_element_line_without_a_colon_is_left_out_of_the_comparison(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace(
            "EM-PROBLEM: definition-stable-chronic", "EM-PROBLEM definition-stable-chronic")))
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0", result.stdout)
        self.assertIn("unread remainder 1", result.stdout)

    def at_approval(self, moment: float, *args):
        import completion_checks
        with mock.patch.object(completion_checks, "approval_moment", return_value=moment):
            return self.in_process(*args)

    def test_x5_a_missing_block_is_a_finding_only_after_the_check_started(self):
        self.write_private(PRIVATE.format(elements=""))
        before, after = 1_700_000_000.0, 4_102_444_800.0
        status, output = self.at_approval(before, "--submission", "shift-synthetic")
        self.assertEqual(0, status, output)
        self.assertIn("not graded, approval predates the check: element blocks 1, re-derivations 0", output)
        status, output = self.at_approval(after, "--submission", "shift-synthetic")
        self.assertEqual(1, status, output)
        self.assertIn("element blocks: present 0, absent 1", output)
        status, output = self.in_process()
        self.assertEqual(1, status, output)
        import completion_checks
        for moment, expected in ((before, (False, "not graded")), (after, (True, "finding"))):
            with mock.patch.object(completion_checks, "approval_moment", return_value=moment), \
                    completion_checks.grading(self.run, "shift-synthetic"):
                finding, report, _ = em_audit.completion_gate(self.run, "shift-synthetic")
            self.assertEqual(expected[0], finding, report)
            self.assertIn(expected[1], report)

    def test_x6_a_re_derivation_with_no_readable_element_line_is_absent(self):
        # Eighth review: only a record with no element candidate is absent; refused candidates are unread.
        self.record("Prose only, no element line.\n")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 1", result.stdout)
        self.record("  EM-OPINION: an unrecognized line\n")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 0", result.stdout)
        self.record(ELEMENTS.replace("  EM-LEVEL: 99283\n", "  EM-LEVEL: not a code\n"))
        result = self.invoke()
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 0", result.stdout)

    def specificity(self):
        return subprocess.run([sys.executable, str(Path(__file__).with_name("specificity_scan.py")), str(self.run),
                               "--submission", "shift-synthetic"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_x7_the_check_off_unread_share_is_labeled_and_counted_once(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS + "  EM-OPINION: an unrecognized line\n"))
        self.assertEqual(2, self.invoke("--write").returncode)
        result = self.specificity()
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("unread E/M audit check-off members 1 (the E/M audit check-offs)", result.stdout + result.stderr)
        self.write_private(PRIVATE.format(elements=ELEMENTS))
        self.assertEqual(0, self.invoke("--write").returncode)
        self.sheet.write_bytes(b"\xff not utf-8")
        result = self.specificity()
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("unread tool-written records 1", result.stdout)



def main_refusal_block_lines(lines: list[str]) -> tuple[list[str], bool]:
    """refusal_scan._block_lines exactly as origin/main held it (1c5c34b1)."""
    import worksheet_grammar
    start = next((i for i, line in enumerate(lines) if worksheet_grammar.REFUSAL_HEADING.search(line)), None)
    if start is None:
        return [], False
    any_heading = re.compile(r"^[ \t]*(?:#{1,6}[ \t]+|---[ \t]+\S.*---[ \t]*$)")
    block: list[str] = []
    for line in lines[start + 1:]:
        if any_heading.match(line):
            break
        block.append(line)
    return block, True


def main_anchor_block_lines(text: str) -> tuple[list[str], bool]:
    """anchor_scan._block_lines exactly as origin/main held it (1c5c34b1)."""
    import worksheet_grammar
    other = re.compile(r"^[ \t]*(?:-{3,}|#{1,6}[ \t])")
    collected: list[str] = []
    found = inside = False
    for line in text.splitlines():
        if worksheet_grammar.BLOCK_HEADING.match(line):
            found = inside = True
            continue
        if inside:
            if other.match(line):
                inside = False
                continue
            collected.append(line)
    return collected, found


class SeventhReviewFindings(RunFixture):
    """The seventh code-review findings of 2026-11-11, each reproduced red before its fix."""

    SYNTHETIC = (
        "---CODED, ANCHOR WAS FILLED---\nZ68.41\n---\nafter a bare rule\n"
        "---NOT CODED, NOTHING ESTABLISHED IT---\nNOT CODED: J18.9  Pneumonia, unspecified organism\n---\n"
        "----\nneeds: imaging" + chr(0x2028) + "establishing pneumonia\nproposed instead:\fR05.9  Cough\n"
        "--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---\nnone\n")

    def test_y0_the_graders_read_exactly_the_lines_main_read_on_every_worksheet_without_a_block(self):
        import anchor_scan
        import refusal_scan
        import worksheet_grammar
        texts = {path: path.read_text(encoding="utf-8") for path in sorted((ROOT / "fixtures").rglob("*.md"))}
        texts["synthetic"] = self.SYNTHETIC
        compared = 0
        for name, text in texts.items():
            if worksheet_grammar.worksheet_em_block(text).blocks:
                continue
            with self.subTest(worksheet=str(name)):
                compared += 1
                self.assertEqual(main_refusal_block_lines(text.splitlines()), refusal_scan._block_lines(text.splitlines()))
                self.assertEqual(main_anchor_block_lines(text), anchor_scan._block_lines(text))
        self.assertGreater(compared, 20)
        self.assertEqual(["NOT CODED: J18.9  Pneumonia, unspecified organism", "---", "----", "needs: imaging",
                          "establishing pneumonia", "proposed instead:", "R05.9  Cough"],
                         refusal_scan._block_lines(self.SYNTHETIC.splitlines())[0])

    def section(self, text: str, title: str) -> str:
        return text.split("## " + title, 1)[1].split("\n## ", 1)[0]

    def test_y1_the_check_off_quotes_a_refusal_block_as_its_grader_reads_it(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "  needs: imaging establishing pneumonia\n", "---\n  needs: imaging establishing pneumonia\n"))
        self.assertEqual(0, self.invoke("--write").returncode)
        refused = self.section(self.sheet.read_text(encoding="utf-8"), "Codes refused, with what would establish them")
        self.assertIn(">   needs: imaging establishing pneumonia", refused)

    def test_y2_a_not_for_entry_em_line_is_never_an_anchor(self):
        import worksheet_grammar
        lines = ["---NOT CODED, NOTHING ESTABLISHED IT---", "refused",
                 "CPT 99285 Emergency visit, high MDM NOT FOR ENTRY", "  EM-LEVEL: 99285", "  EM-MDM: high",
                 "CPT 93000 Electrocardiogram", "  EM-LEVEL: 99285", "kept"]
        self.assertEqual((lines[1:], True), worksheet_grammar.step_four_block(
            lines, worksheet_grammar.REFUSAL_HEADING, worksheet_grammar.ANY_HEADING))
        text = PRIVATE.format(elements=ELEMENTS) + "\nCPT 99285 Emergency visit, high MDM NOT FOR ENTRY\n" + ELEMENTS
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual((1, len(ELEMENTS.splitlines())), (elements.blocks, elements.outside))

    def test_y2_em_lines_under_a_not_for_entry_em_line_are_unread(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS)
                           + "\nCPT 99285 Emergency visit, high MDM NOT FOR ENTRY\n  EM-LEVEL: 99285\n")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("findings 0", result.stdout)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertNotIn("E/M line: CPT 99285", self.sheet.read_text(encoding="utf-8"))

    def test_y3_a_direct_consultation_without_a_note_path_is_not_graded(self):
        (self.run / review_manifest.MANIFEST).unlink()
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        (self.run / "openers.json").unlink()
        finding, report, unread = em_audit.completion_gate(self.run, "consultation-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("not graded", report)

    def test_y5_the_re_derivation_reader_carries_no_dead_branch(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "rederivation_lines")
        self.assertEqual([], [ast.unparse(node) for node in ast.walk(function) if isinstance(node, ast.IfExp)])



class EighthReviewFindings(ProseBind, RunFixture):
    """The eighth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_z1_a_finding_is_repaired_before_approval_and_only_differences_are_shown(self):
        skill = SKILL.read_text(encoding="utf-8")
        coding = (ROOT / "skills" / "icd10-cpt" / "SKILL.md").read_text(encoding="utf-8")
        self.assertProseNotIn("`FINDING` lines the clinician has seen", skill)
        self.assertProseNotIn("differences and findings shown to the clinician", coding)
        for text in (skill, coding):
            self.assertProseIn("rebuild the manifest", text)
        self.record(ELEMENTS.replace("definition-stable-chronic | not counted", "definition-stable-chronic | counted"))
        self.assertEqual(1, self.invoke("--write").returncode)
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("differing 1", report)
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace("risk low; mdm low", "risk low; mdm moderate")))
        self.invoke("--write")
        finding, report, _ = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)

    def git_repository(self) -> Path:
        repository = self.root / "repository"
        (repository / "reference").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        return repository

    def commit(self, repository: Path, content: bytes) -> None:
        (repository / "reference" / "history-mdm.md").write_bytes(content)
        subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repository), "-c", "user.name=synthetic", "-c", "user.email=synthetic@example.test",
                        "commit", "-q", "-m", "synthetic"], check=True)

    def test_z5_the_sheet_version_the_receipt_bound_is_read_after_a_later_commit(self):
        import coding_freshness
        import hashlib
        real = (ROOT / "reference" / "cpt-em-mdm-2026.md").read_bytes()
        repository = self.git_repository()
        self.commit(repository, real)
        self.commit(repository, real + b"\nA later revision of the sheet.\n")
        receipt = self.run / review_manifest.RECEIPT
        value = json.loads(receipt.read_text(encoding="utf-8"))
        value["sources"]["cpt"]["mdm_sheet_filename"] = "history-mdm.md"
        value["sources"]["cpt"]["mdm_sheet_sha256"] = hashlib.sha256(real).hexdigest()
        receipt.write_text(json.dumps(value), encoding="utf-8")
        with mock.patch.object(coding_freshness, "ROOT", repository), mock.patch.object(em_audit, "REPOSITORY", repository):
            status, output = self.in_process("--write")
            self.assertEqual(0, status, output)
            self.assertNotIn("Entry ids: not checked", self.sheet.read_text(encoding="utf-8"))
            value["sources"]["cpt"]["mdm_sheet_sha256"] = "0" * 64
            receipt.write_text(json.dumps(value), encoding="utf-8")
            status, output = self.in_process()
            self.assertEqual(2, status, output)
            self.assertIn("unread remainder 1", output)

    def test_z6_a_re_derivation_whose_element_lines_are_all_refused_is_unread_not_absent(self):
        self.record("".join("- " + line.strip() + "\n" for line in ELEMENTS.splitlines()))
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 0", result.stdout)
        self.record("Prose only, no element line.\n")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("absent 1", result.stdout)

    def test_z7_check_offs_are_written_under_the_run_record_lock(self):
        with mock.patch.object(em_audit, "update_tool_record", wraps=em_audit.update_tool_record) as writer:
            status, output = self.in_process("--write")
        self.assertEqual(0, status, output)
        self.assertEqual(1, writer.call_count)
        self.sheet.write_bytes(b"\xff damaged check-off")
        status, output = self.in_process("--write")
        self.assertEqual(2, status, output)
        self.assertIn("check-offs refused at note 1", output)

    def test_z8_one_em_family_constant_and_no_lock_stack_in_the_grammar(self):
        import coding_freshness
        import cpt_identity
        import worksheet_grammar
        self.assertIs(cpt_identity.EM_CODES, review_manifest.EM_CODES)
        self.assertIs(cpt_identity.EM_CODES, worksheet_grammar.EM_CODES)
        self.assertEqual(cpt_identity.EM_CODES, coding_freshness.ED_EM | coding_freshness.OFFICE_EM)
        self.assertFalse(hasattr(worksheet_grammar, "em_family"))
        tree = ast.parse(Path(worksheet_grammar.__file__).read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual({"__future__", "re", "dataclasses", "cpt_identity"}, imported)

    def test_z9_and_z10_the_element_block_walk_does_not_copy_and_the_stops_share_one_class(self):
        import worksheet_grammar
        tree = ast.parse(Path(worksheet_grammar.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "element_body_end")
        self.assertEqual([], [ast.unparse(node) for node in ast.walk(function) if isinstance(node, ast.Slice)])
        self.assertIs(em_audit.CheckOffsStopped.__init__, em_audit.WordExportStopped.__init__)
        self.assertTrue(issubclass(em_audit.CheckOffsStopped, em_audit.WritesStopped))
        self.assertTrue(issubclass(em_audit.WordExportStopped, em_audit.WritesStopped))



class NinthReviewFindings(RunFixture):
    """The ninth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_n1_a_margin_field_under_an_entry_is_owned_as_paired_entry_owns_it(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            '  ANCHOR: "Cough."\n  SPECIFICITY: complete - the synthetic encounter documents no further axis\n'
            '  CONFIDENCE: verified against ICD-10-CM FY2026\n',
            '  SPECIFICITY: complete - the synthetic encounter documents no further axis\n'
            '  CONFIDENCE: verified against ICD-10-CM FY2026\nANCHOR: "Cough."\n'))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("codes without an anchor 0", result.stdout)
        self.assertIn("unread remainder 0", result.stdout)
        self.assertIn('  - Anchor: "Cough."', self.sheet.read_text(encoding="utf-8"))

    def test_n3_a_check_off_is_stale_only_when_the_fresh_render_read_everything(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        (self.run / preapproval_answers.RECORD).write_text("not json", encoding="utf-8")
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("check-offs missing or stale 0", report)
        self.assertIn("not compared", report)

    def test_n4_an_edit_anywhere_in_the_private_worksheet_after_the_manifest_refuses(self):
        path = self.run / "worksheets/note-1.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "needs: imaging establishing pneumonia", "needs: imaging, edited after the manifest"), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        manifest = json.loads((self.run / review_manifest.MANIFEST).read_text(encoding="utf-8"))
        self.assertIn("private_worksheet_sha256", manifest["encounters"][0])
        self.assertNotIn("element_block_sha256", manifest["encounters"][0])

    def test_n5_a_manifest_without_the_fingerprint_is_not_graded_before_the_check_started(self):
        import completion_checks
        path = self.run / review_manifest.MANIFEST
        value = json.loads(path.read_text(encoding="utf-8"))
        del value["encounters"][0]["private_worksheet_sha256"]
        path.write_text(json.dumps(value), encoding="utf-8")
        with mock.patch.object(completion_checks, "approval_moment", return_value=1_700_000_000.0):
            status, output = self.in_process("--submission", "shift-synthetic")
        self.assertEqual(0, status, output)
        self.assertIn("unread remainder 0", output)
        status, output = self.in_process()
        self.assertEqual(2, status, output)

    def test_n6_an_indented_em_anchor_carries_no_block(self):
        import worksheet_grammar
        text = (PRIVATE.format(elements=ELEMENTS) + "\nSupport restated:\n  E/M: 99283 restated\n"
                + "".join("    " + line.strip() + "\n" for line in ELEMENTS.splitlines()))
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual((1, len(ELEMENTS.splitlines())), (elements.blocks, elements.outside))

    def test_n8_a_word_destination_that_cannot_be_resolved_is_a_word_refusal(self):
        with mock.patch.object(repo_root, "output_root", side_effect=ValueError("no owning checkout")):
            status, output = self.in_process("--write", "--docx")
        self.assertEqual(2, status, output)
        self.assertIn("check-offs written 1", output)
        self.assertIn("Word copy refused", output)



class TenthReviewFindings(RunFixture):
    """The tenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_q2_a_suffixed_element_name_keeps_its_entry_out_of_the_comparison(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace(
            "EM-PROBLEM: definition-stable-chronic", "EM-PROBLEMS: definition-stable-chronic")))
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0", result.stdout)
        self.assertIn("unread remainder 1", result.stdout)

    def test_q2_an_unmappable_refused_line_leaves_the_counted_elements_uncompared(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS + "  EM-OPINION: an unrecognized line\n"))
        self.record(ELEMENTS.replace('| not counted | "Hypertension."', '| counted | "Hypertension."'))
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0", result.stdout)

    def test_q3_a_check_off_never_written_is_missing_even_when_the_render_is_partial(self):
        (self.run / preapproval_answers.RECORD).write_text("not json", encoding="utf-8")
        finding, report, _ = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)
        self.assertIn("check-offs missing or stale 1", report)

    def test_q5_one_selected_line_read_per_splitting_rule_and_one_sheet_resolution_per_process(self):
        import coding_freshness
        import worksheet_grammar
        name_the_committed_sheet(self.run)
        em_audit.reset_sheet_cache()
        with mock.patch.object(worksheet_grammar, "selected_em_lines", wraps=worksheet_grammar.selected_em_lines) as inner, \
                mock.patch.object(em_audit, "selected_em_lines", wraps=em_audit.selected_em_lines) as outer, \
                mock.patch.object(coding_freshness, "bound_sheet_version",
                                  wraps=coding_freshness.bound_sheet_version) as sheet:
            em_audit.render(self.run, [])
            em_audit.render(self.run, [])
        self.assertLessEqual(inner.call_count + outer.call_count, 4)
        self.assertEqual(1, sheet.call_count)

    def test_q6_one_body_rule_and_no_em_codes_parameter(self):
        import inspect
        import worksheet_grammar
        tree = ast.parse(Path(worksheet_grammar.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "worksheet_em_block")
        calls = {node.func.id for node in ast.walk(function) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertIn("element_body_end", calls)
        self.assertEqual([], [node for node in ast.walk(function) if isinstance(node, (ast.For, ast.While))
                              and any(isinstance(inner, ast.Compare) and "lines" in ast.unparse(inner)
                                      and '" \\t"' in ast.unparse(inner) for inner in ast.walk(node))])
        self.assertNotIn("em_codes", inspect.signature(worksheet_grammar.worksheet_em_block).parameters)
        self.assertNotIn("em_codes", inspect.signature(worksheet_grammar.selected_em_lines).parameters)
        source = ast.unparse(next(node for node in ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8")).body
                                  if isinstance(node, ast.FunctionDef) and node.name == "entry_details"))
        self.assertIn("indented_line", source)
        self.assertNotIn('" \\t"', source)


class EleventhReviewFindings(ProseBind, RunFixture):
    """The eleventh code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit.completion_gate(self.run, "shift-synthetic")

    def edit_json(self, name: str, change) -> None:
        path = self.run / name
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_e1_a_private_worksheet_changed_after_the_manifest_is_a_finding(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        path = self.run / "worksheets/note-1.md"
        path.write_text(path.read_text(encoding="utf-8").replace("needs: imaging", "needs: imaging, edited"),
                        encoding="utf-8")
        finding, report, unread = self.gate()
        self.assertEqual((True, 0), (finding, unread), report)
        self.assertIn("finding", report)

    def test_e1_a_stale_manifest_is_a_finding(self):
        self.edit_json(review_manifest.MANIFEST,
                       lambda value: value["encounters"][0].update(normalized_sha256="0" * 64))
        finding, report, unread = self.gate()
        self.assertEqual((True, 0), (finding, unread), report)

    def test_e1_a_stale_receipt_is_a_finding_and_a_missing_one_stays_unread(self):
        self.edit_json(review_manifest.RECEIPT,
                       lambda value: value["encounters"][0].update(normalized_sha256="1" * 64))
        finding, report, unread = self.gate()
        self.assertEqual((True, 0), (finding, unread), report)
        (self.run / review_manifest.RECEIPT).unlink()
        finding, report, unread = self.gate()
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("incomplete", report)

    def test_e1_a_sheet_version_the_parser_refuses_is_a_finding(self):
        import coding_freshness
        em_audit.reset_sheet_cache()
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            finding, report, unread = self.gate()
        self.assertEqual((True, 0), (finding, unread), report)

    def test_e2_a_fault_a_capturing_command_counts_never_reads_clean(self):
        from run_record_reader import capture_errors
        self.assertEqual(0, self.invoke("--write").returncode)
        (self.run / preapproval_answers.RECORD).write_text("not json", encoding="utf-8")
        with capture_errors():
            finding, report, unread = self.gate()
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertNotIn(": clean", report)
        self.assertIn(": incomplete", report)

    def test_e3_a_padded_manifest_cpt_code_still_names_its_ecg_rule(self):
        inputs = self.run / "inputs.json"
        value = json.loads(inputs.read_text(encoding="utf-8"))
        value[0]["codes"]["cpt"] = ["93005"]
        inputs.write_text(json.dumps(value), encoding="utf-8")
        visible = self.run / "visible-worksheet-1.md"
        visible.write_text(VISIBLE.replace("CPT 99283", "CPT 93005 Electrocardiogram, tracing only\nCPT 99283"),
                           encoding="utf-8")
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "CPT 99283", 'CPT 93005 Electrocardiogram, tracing only\n  ANCHOR: "ECG."\nCPT 99283'))
        self.edit_json(review_manifest.MANIFEST, lambda value: value["encounters"][0]["codes"].update(cpt=[" 93005 "]))
        passing_receipt(self.run)
        name_the_committed_sheet(self.run)
        tally, _, sheets = em_audit.render(self.run, [])
        self.assertIn("- ECG code: " + em_audit.ECG_RULES["93005"], sheets[0].text)
        self.assertIn("EM-ECG line says not applicable", sheets[0].text)

    def test_e4_a_manifest_without_the_fingerprint_is_unread_and_never_sent_to_a_rebuild(self):
        self.edit_json(review_manifest.MANIFEST, lambda value: value["encounters"][0].pop("private_worksheet_sha256"))
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("not bound to the manifest", text)
        for advice in (text, result.stdout):
            self.assertNotIn("rebuild", advice.lower())
        skill = SKILL.read_text(encoding="utf-8")
        self.assertProseIn("predates the private worksheet fingerprint", skill)
        self.assertProseIn("Keep the manifest as it stands", skill)
        import completion_checks
        with mock.patch.object(completion_checks, "approval_moment", return_value=1_700_000_000.0):
            status, output = self.in_process("--submission", "shift-synthetic")
        self.assertEqual(0, status, output)

    def test_e5_the_gate_reads_no_exemption_before_its_presence_checks(self):
        import completion_checks
        bare = self.root / "consultation"
        bare.mkdir()
        with mock.patch.object(completion_checks, "exemption", side_effect=AssertionError("read")) as exemption:
            self.assertIn("not graded", em_audit.completion_gate(self.run, None)[1])
            self.assertIn("not graded", em_audit.completion_gate(bare, "consultation-synthetic")[1])
        self.assertEqual(0, exemption.call_count)

    def test_e5_specificity_scan_answers_both_not_graded_cases_without_loading_em_audit(self):
        import specificity_scan
        bare = self.root / "consultation"
        bare.mkdir()
        for run, submission in ((self.run, None), (bare, "consultation-synthetic")):
            with self.subTest(submission=submission):
                self.assertEqual(em_audit.completion_gate(run, submission),
                                 specificity_scan.em_audit_gate(run, submission))
        self.assertEqual(em_audit.EXPECTED_ROW, specificity_scan.EM_AUDIT_ROW)
        self.assertEqual(em_audit.RUN_RECORDS, specificity_scan.EM_AUDIT_RUN_RECORDS)
        probe = ("import sys, specificity_scan\n"
                 f"specificity_scan.em_audit_gate(__import__('pathlib').Path({str(bare)!r}), 'c')\n"
                 f"specificity_scan.em_audit_gate(__import__('pathlib').Path({str(self.run)!r}), None)\n"
                 "print('em_audit' in sys.modules)\n")
        result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", cwd=str(Path(__file__).parent))
        self.assertEqual("False", result.stdout.strip(), result.stderr)

    def test_e9_the_one_line_element_block_wrapper_is_gone(self):
        import worksheet_grammar
        self.assertFalse(hasattr(worksheet_grammar, "opens_element_block"))
        self.assertFalse(hasattr(em_audit, "opens_element_block"))

    def test_e6_the_graders_read_main_lines_and_grade_the_valid_placement_unchanged(self):
        import anchor_scan
        import refusal_scan
        import worksheet_grammar
        tail = "\nE/M: 99283 low complexity\n" + ELEMENTS
        quoting = tail.replace("  EM-DATA:", '  EM-PROBLEM: none | not counted | "Suspected pneumonia, NOT CODED: '
                               'J18.9 Pneumonia, unspecified organism." | not established\n  EM-DATA:')
        base = PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n", "CPT 99283 Emergency visit\n  ANCHOR: \"Cough.\"\n")
        filled = "## Coded, anchor was filled: confirm before submitting\n\nNone.\n"
        refused = base.split("## Not coded", 1)[1]
        undocumented = "## Undocumented, would support a more specific code\n\nduration of the cough\n  affects: R05.9\n\n"
        head = base.split("## Coded", 1)[0]
        blocks = {"filled": filled, "refusal": "## Not coded" + refused, "undocumented": undocumented}
        graded = 0
        for last in blocks:
            body = head + "".join(blocks[name] for name in blocks if name != last) + blocks[last]
            for extra in (tail, quoting):
                with self.subTest(last=last, quoting=extra is quoting):
                    text = body + extra
                    self.assertEqual(main_refusal_block_lines(text.splitlines()), refusal_scan._block_lines(text.splitlines()))
                    self.assertEqual(main_anchor_block_lines(text), anchor_scan._block_lines(text))
                    self.assertNotIn("EM-", worksheet_grammar.block_text(text, worksheet_grammar.REFUSAL_HEADING, "refusal"))
                    reports = []
                    # The control keeps the E/M label line and drops only its element lines.
                    for content in (body + "\nE/M: 99283 low complexity\n", text):
                        folder = Path(tempfile.mkdtemp(dir=self.root))
                        (folder / "note-1.md").write_text(content, encoding="utf-8")
                        for grader in ("refusal_scan.py", "anchor_scan.py"):
                            outcome = subprocess.run([sys.executable, str(Path(__file__).with_name(grader)), str(folder)],
                                                     capture_output=True, text=True, encoding="utf-8",
                                                     errors="replace")
                            reports.append((outcome.returncode, outcome.stdout.replace(folder.name, "")))
                    self.assertEqual(reports[:2], reports[2:])
                    graded += 1
        self.assertEqual(6, graded)
        self.assertIs(worksheet_grammar.OTHER_HEADING, anchor_scan.OTHER_HEADING)

    def test_e7_one_parse_of_the_private_worksheet_per_check_off(self):
        import worksheet_grammar
        private = (self.run / "worksheets/note-1.md").read_text(encoding="utf-8")
        counted = {name: mock.Mock(wraps=getattr(worksheet_grammar, name))
                   for name in ("entry_region", "read_entries", "physical_lines")}
        validated = review_manifest.validated_population(self.run)  # the validation's own reads are not counted
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(review_manifest, "validated_population", return_value=validated))
            for name, wrapper in counted.items():
                stack.enter_context(mock.patch.object(worksheet_grammar, name, wrapper))
                if hasattr(em_audit, name):
                    stack.enter_context(mock.patch.object(em_audit, name, wrapper))
            em_audit.render(self.run, [])
        self.assertEqual(1, counted["entry_region"].call_count)
        self.assertEqual(1, counted["read_entries"].call_count)
        self.assertEqual(1, sum(call.args[0] == private for call in counted["physical_lines"].call_args_list))

    def test_e8_the_bound_sheet_version_is_found_in_two_processes(self):
        import coding_freshness
        path = ROOT / "reference" / "cpt-em-mdm-2026.md"
        digest = coding_freshness.committed_sheet_sha256(path)
        self.assertEqual(digest, coding_freshness.sheet_sha256(coding_freshness.bound_sheet_version(path, digest)))
        relative = "reference/cpt-em-mdm-2026.md"
        history = subprocess.run(["git", "log", "--format=%H", "--", relative], cwd=ROOT,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
        oldest = subprocess.run(["git", "show", f"{history[-1]}:{relative}"], cwd=ROOT, capture_output=True).stdout
        self.assertEqual(oldest, coding_freshness.bound_sheet_version(path, coding_freshness.sheet_sha256(oldest)))
        # A fingerprint no version carries walks the whole history, the case a process per version made long.
        with mock.patch.object(coding_freshness.subprocess, "run", wraps=subprocess.run) as run:
            self.assertIsNone(coding_freshness.bound_sheet_version(path, "0" * 64))
        self.assertLessEqual(run.call_count, 2)

    def test_e10_the_re_derivation_done_condition_and_step_1_exit_2(self):
        rederivation = (SKILL.parent / "rederivation.md").read_text(encoding="utf-8")
        self.assertProseNotIn("reports `absent 0` among the re-derivations and `unread remainder 0`", rederivation)
        self.assertProseIn("no re-derivation line unread", rederivation)
        self.assertProseIn("their own repair", rederivation)
        skill = SKILL.read_text(encoding="utf-8")
        step = skill.split("## 1.", 1)[1].split("## 2.", 1)[0]
        self.assertProseIn("unread remainder", step)


if __name__ == "__main__":
    unittest.main()
