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
from code_set_database_test_support import PROCEDURE_CODES_DATABASE_SHA256, assert_code_set_database_digest

ROOT = Path(__file__).resolve().parent.parent
# The check-off reads each E/M level's MDM level from the committed CPT 2026 descriptors.
assert_code_set_database_digest(
    ROOT / "reference" / "procedure-codes-2026.sqlite",
    PROCEDURE_CODES_DATABASE_SHA256,
    "procedure-code Code-set database",
)
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


def em_audit_gate(run: Path, submission: str | None):
    """The production E/M audit gate, specificity_scan's: it scopes the run, then grades it in em_audit."""
    import specificity_scan
    return specificity_scan.em_audit_gate(run, submission)


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

    def fake_checkout(self) -> Path:
        checkout = self.root / "main-checkout"
        (checkout / ".git").mkdir(parents=True, exist_ok=True)
        return checkout

    def word_destination(self) -> Path:
        """A folder under a stand-in main checkout's output/, the only place a Word copy may go."""
        checkout = self.fake_checkout()
        patcher = mock.patch.object(repo_root, "main_repo_root", return_value=checkout)
        patcher.start()
        self.addCleanup(patcher.stop)
        return checkout / "output" / "export"

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
        self.assertFalse(em_audit.word_folder(self.run, None).exists())

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
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)  # eighteenth review: a finding
        self.assertIn("changed or went missing after the manifest", result.stdout)
        self.assertFalse(self.sheet.exists())

    def test_note_selection_and_unknown_note(self):
        self.assertIn("selected 1", self.invoke("--note", 1).stdout)
        self.assertEqual(2, self.invoke("--note", 2).returncode)

    def test_word_export_is_on_demand_and_keeps_the_overwrite_refusal(self):
        folder = self.word_destination()
        status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(0, status, output)
        self.assertIn("Word copies written 1", output)
        self.assertTrue((folder / "note-1.docx").is_file())
        self.assertFalse(self.sheet.exists())
        (folder / "note-1.docx").write_bytes(b"not a document this renderer wrote")
        status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(2, status, output)
        self.assertIn("Word copy refused", output)
        status, output = self.in_process("--docx", "--output-dir", folder, "--force")
        self.assertEqual(0, status, output)

    def test_completion_requires_a_re_derivation_and_a_current_check_off(self):
        self.rederivation.unlink()
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)
        self.assertIn("re-derivations absent 1", report)
        self.assertIn("check-offs missing or stale 1", report)
        self.record(ELEMENTS)
        self.assertEqual(0, self.invoke("--write").returncode)
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("the E/M audit check-offs: clean", report)
        not_graded = em_audit_gate(self.run, None)
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
        folder = self.word_destination()
        status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(1, status, output)
        self.assertTrue((folder / "note-1.docx").is_file())

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
        finding, report, _ = em_audit_gate(self.run, "shift-synthetic")
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
        # Fifteenth review: ownership is entry_walk's, whose field rule is detail_belongs_to_entry's (test_h9).
        # Twenty-sixth review: the region and its entries are validation's own read (read_private).
        attributes = {node.func.attr for node in ast.walk(tree)
                      if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertIn("entry_walk", called, called)
        self.assertIn("read_private", attributes)

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
        folder = self.word_destination()
        with mock.patch("docx_write.write_docx", side_effect=OutboundTextError("line 3: U+0085")):
            status, output = self.in_process("--write", "--docx", "--output-dir", folder)
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
        folder = self.word_destination()
        status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(0, status, output)
        import docx_read
        text = "\n".join(docx_read.read_docx(folder / "note-1.docx"))
        for literal in ("*recheck* rest.", "rest ** education", "`code` and *recheck*", "**bold** markers."):
            self.assertIn(literal, text)

    def test_t5_an_unreadable_check_off_is_unread_rather_than_stale(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        self.sheet.write_bytes(b"\xff\xfe not utf-8")
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
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
        with mock.patch.object(em_audit.cpt_mdm_sheet, "read_entries", wraps=cpt_mdm_sheet.read_entries) as parser:
            self.in_process()
        self.assertEqual(1, parser.call_count)
        with mock.patch.object(em_audit.cpt_mdm_sheet, "read_entries", side_effect=ValueError("no entries")):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("CPT MDM sheet", output)

    def test_u5_an_element_line_edited_after_the_manifest_refuses_the_check_off(self):
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace(
            "rest and education", "rest and education, edited after the manifest")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)  # eighteenth review: a finding
        self.assertIn("changed after the manifest", result.stdout)
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((True, 0), (finding, unread), report)  # eleventh review: a finding, not unread

    def test_u5_a_run_without_its_private_fingerprint_record_is_unread(self):
        # Thirteenth review: the fingerprint lives beside the manifest, never in it.
        (self.run / review_manifest.PRIVATE_FINGERPRINTS).unlink()
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("no fingerprint is recorded", self.sheet.read_text(encoding="utf-8"))

    def test_u7_a_coded_run_without_a_manifest_is_incomplete_at_submission(self):
        (self.run / review_manifest.MANIFEST).unlink()
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("incomplete", report)
        self.assertIn("not graded", em_audit_gate(self.run, None)[1])
        # Twenty-fourth review: scope is em_audit_scope's alone, so a note-path run without a manifest
        # is incomplete whatever its worksheets select.
        (self.run / "worksheets/note-1.md").write_text("ICD-10-CM R05.9 Cough\n  ANCHOR: \"Cough.\"\n",
                                                       encoding="utf-8")
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("incomplete", report)

    def test_u8_the_command_and_the_gate_share_one_finding_predicate(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name in ("status_of", "completion_gate"):  # twenty-second review: the grading body
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
        finding, _, _ = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((1, True), (status, finding))

    def test_u9_a_word_refusal_names_the_note_and_counts_the_copies_already_written(self):
        folder = self.word_destination()
        sheets = [em_audit.Sheet(1, "note-1", "# One\n"), em_audit.Sheet(2, "note-2", "# Two\n")]
        folder.mkdir(parents=True)
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
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
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
        with mock.patch.object(coding_freshness, "sheet_sha256", return_value="0" * 64):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("unread remainder 1", output)
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("CPT MDM sheet", output)

    def test_v6_a_refused_check_off_says_the_word_copies_were_not_attempted(self):
        (self.run / em_audit.OUTPUT_DIRECTORY / "note-2.md").mkdir(parents=True)
        folder = self.word_destination()
        with mock.patch.object(em_audit, "render", return_value=(em_audit.Tally(), 2, self.two_sheets())):
            status, output = self.in_process("--write", "--docx", "--output-dir", folder)
        self.assertEqual(2, status, output)
        self.assertIn("Word copies not attempted", output)
        self.assertFalse(folder.exists())

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
                                     em_audit.block_quote(em_audit.parse_private(text), heading, kind))

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
                finding, report, _ = em_audit_gate(self.run, "shift-synthetic")
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
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        (self.run / "openers.json").unlink()
        finding, report, unread = em_audit_gate(self.run, "consultation-synthetic")
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
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("differing 1", report)
        self.write_private(PRIVATE.format(elements=ELEMENTS.replace("risk low; mdm low", "risk low; mdm moderate")))
        self.invoke("--write")
        finding, report, _ = em_audit_gate(self.run, "shift-synthetic")
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
        # Thirteenth review: review_manifest reads the E/M identity through worksheet_grammar.em_identity.
        self.assertFalse(hasattr(review_manifest, "EM_CODES"))
        self.assertIs(cpt_identity.EM_CODES, worksheet_grammar.EM_CODES)
        self.assertEqual(cpt_identity.EM_CODES, coding_freshness.ED_EM | coding_freshness.OFFICE_EM)
        self.assertFalse(hasattr(worksheet_grammar, "em_family"))
        tree = ast.parse(Path(worksheet_grammar.__file__).read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        # Twenty-seventh review: bisect numbers lines by their starts, standard library only.
        self.assertEqual({"__future__", "bisect", "re", "dataclasses", "cpt_identity"}, imported)

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
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("check-offs missing or stale 0", report)
        self.assertIn("not compared", report)

    def test_n4_an_edit_anywhere_in_the_private_worksheet_after_the_manifest_refuses(self):
        path = self.run / "worksheets/note-1.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "needs: imaging establishing pneumonia", "needs: imaging, edited after the manifest"), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)  # eighteenth review: a finding
        self.assertIn("changed after the manifest", result.stdout)
        manifest = json.loads((self.run / review_manifest.MANIFEST).read_text(encoding="utf-8"))
        self.assertNotIn("private_worksheet_sha256", manifest["encounters"][0])  # thirteenth review
        self.assertNotIn("element_block_sha256", manifest["encounters"][0])
        self.assertIn(str(self.run / "worksheets/note-1.md"), review_manifest.private_fingerprints(self.run))

    def test_n5_a_missing_fingerprint_is_not_graded_before_the_check_started(self):
        import completion_checks
        (self.run / review_manifest.PRIVATE_FINGERPRINTS).unlink()
        with mock.patch.object(completion_checks, "approval_moment", return_value=1_700_000_000.0):
            status, output = self.in_process("--submission", "shift-synthetic")
        self.assertEqual(0, status, output)
        self.assertIn("unread remainder 0", output)
        status, output = self.in_process()
        self.assertEqual(2, status, output)

    def test_n6_an_indented_em_label_anchors_a_block_as_the_manifest_reader_selects_it(self):
        # Twelfth review: the anchor rule is review_manifest.selected_codes's, which reads an indented
        # E/M: label, so a restated block under one is a second block rather than outside lines.
        import worksheet_grammar
        text = (PRIVATE.format(elements=ELEMENTS) + "\nSupport restated:\n  E/M: 99283 restated\n"
                + "".join("    " + line.strip() + "\n" for line in ELEMENTS.splitlines()))
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual((2, 0), (elements.blocks, elements.outside))

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
        finding, report, _ = em_audit_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)
        self.assertIn("check-offs missing or stale 1", report)

    def test_q5_one_selected_line_read_per_splitting_rule_and_one_sheet_resolution_per_process(self):
        import coding_freshness
        import worksheet_grammar
        name_the_committed_sheet(self.run)
        # Twenty-fourth review: em_audit no longer reads selected lines itself (selects_em_level is gone).
        with mock.patch.object(worksheet_grammar, "selected_em_lines", wraps=worksheet_grammar.selected_em_lines) as inner, \
                mock.patch.object(coding_freshness, "bound_sheet_version",
                                  wraps=coding_freshness.bound_sheet_version) as sheet:
            em_audit.render(self.run, [])
            em_audit.render(self.run, [])
        self.assertLessEqual(inner.call_count, 4)
        self.assertEqual(2, sheet.call_count)  # fourteenth review: once per render, no process cache

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
                                  if isinstance(node, ast.FunctionDef) and node.name == "entry_walk"))
        # Sixteenth review: the walk reads worksheet_grammar.body_end, the one body rule.
        self.assertIn("body_end(", source)
        self.assertIn("indented_line", inspect.getsource(worksheet_grammar.body_end))
        self.assertNotIn('" \\t"', source)


class EleventhReviewFindings(ProseBind, RunFixture):
    """The eleventh code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

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

    def test_e1_a_sheet_version_the_parser_refuses_is_a_tool_defect(self):
        # Nineteenth review: a committed sheet the current reader refuses is incomplete, not a finding.
        import coding_freshness
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            finding, report, unread = self.gate()
        self.assertEqual((False, 1), (finding, unread), report)

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

    def test_e4_a_missing_fingerprint_is_unread_and_its_repair_keeps_the_approved_manifest(self):
        # Thirteenth review: with the fingerprint beside the manifest, building again records it and
        # leaves an unchanged manifest byte-identical, so the repair never orphans an approval.
        manifest = self.run / review_manifest.MANIFEST
        before = manifest.read_bytes()
        (self.run / review_manifest.PRIVATE_FINGERPRINTS).unlink()
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("Build the manifest again to record it", text)
        skill = SKILL.read_text(encoding="utf-8")
        self.assertProseIn("no private worksheet fingerprint is recorded", skill)
        self.assertProseIn("leaves an unchanged manifest byte-identical", skill)
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        self.assertEqual(before, manifest.read_bytes())
        (self.run / review_manifest.PRIVATE_FINGERPRINTS).unlink()
        import completion_checks
        with mock.patch.object(completion_checks, "approval_moment", return_value=1_700_000_000.0):
            status, output = self.in_process("--submission", "shift-synthetic")
        self.assertEqual(0, status, output)

    def test_e5_the_gate_reads_no_exemption_before_its_presence_checks(self):
        import completion_checks
        bare = self.root / "consultation"
        bare.mkdir()
        with mock.patch.object(completion_checks, "exemption", side_effect=AssertionError("read")) as exemption:
            self.assertIn("not graded", em_audit_gate(self.run, None)[1])
            self.assertIn("not graded", em_audit_gate(bare, "consultation-synthetic")[1])
        self.assertEqual(0, exemption.call_count)

    def test_e5_specificity_scan_answers_both_not_graded_cases_without_loading_em_audit(self):
        import specificity_scan
        bare = self.root / "consultation"
        bare.mkdir()
        for run, submission in ((self.run, None), (bare, "consultation-synthetic")):
            with self.subTest(submission=submission):
                finding, report, unread = specificity_scan.em_audit_gate(run, submission)
                self.assertEqual((False, 0), (finding, unread), report)
                self.assertIn("not graded", report)
        import em_audit_scope
        self.assertIs(em_audit_scope.ROW, em_audit.EXPECTED_ROW)
        self.assertEqual(review_manifest.MANIFEST, em_audit_scope.MANIFEST)
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
                    self.assertNotIn("EM-", em_audit.block_quote(em_audit.parse_private(text),
                                                                 worksheet_grammar.REFUSAL_HEADING, "refusal"))
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
        # Twenty-sixth review: the check-off reuses validation's parse, so beyond it nothing is parsed;
        # test_y7 counts the one parse per render, validation included.
        self.assertEqual(0, counted["entry_region"].call_count)
        self.assertEqual(0, counted["read_entries"].call_count)
        self.assertEqual(0, sum(call.args[0] == private for call in counted["physical_lines"].call_args_list))

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
        # A fingerprint no version carries walks the whole history, the case a process per version made
        # long: HEAD's version, then one log and one batch (twelfth review: HEAD first).
        # Every process starts through Popen, subprocess.run's included.
        with mock.patch.object(coding_freshness.subprocess, "Popen", wraps=subprocess.Popen) as popen:
            self.assertIsNone(coding_freshness.bound_sheet_version(path, "0" * 64))
        self.assertLessEqual(popen.call_count, 3)

    def test_e10_the_re_derivation_done_condition_and_step_1_exit_2(self):
        rederivation = (SKILL.parent / "rederivation.md").read_text(encoding="utf-8")
        self.assertProseNotIn("reports `absent 0` among the re-derivations and `unread remainder 0`", rederivation)
        self.assertProseIn("no re-derivation line unread", rederivation)
        self.assertProseIn("their own repair", rederivation)
        skill = SKILL.read_text(encoding="utf-8")
        step = skill.split("## 1.", 1)[1].split("## 2.", 1)[0]
        self.assertProseIn("unread remainder", step)


class FakeBatch:
    """A ``git cat-file --batch`` stand-in answering each request as it is written."""

    def __init__(self, answers: dict[str, bytes], requests: list[str]) -> None:
        self.answers, self.requests, self.buffer = answers, requests, b""
        self.stdin, self.stdout = self, self

    def write(self, data: bytes) -> None:
        for request in data.decode("utf-8").splitlines():
            self.requests.append(request)
            self.buffer += self.answers[request.split(":", 1)[0]]

    def flush(self) -> None:
        pass

    def readline(self) -> bytes:
        line, _, self.buffer = self.buffer.partition(b"\n")
        return line + b"\n"

    def read(self, size: int) -> bytes:
        data, self.buffer = self.buffer[:size], self.buffer[size:]
        return data

    def close(self) -> None:
        pass

    def wait(self) -> int:
        return 0


def fake_git(head: bytes, versions: list[tuple[str, bytes]]):
    """``subprocess.run`` and ``subprocess.Popen`` stand-ins over ``versions``, and the batch requests made."""
    commits = [f"{index:040x}" for index in range(1, len(versions) + 1)]
    answers = {commit: (f"{commit} missing\n".encode() if kind == "missing"
                        else f"{commit} {kind} {len(body)}\n".encode() + body + b"\n")
               for commit, (kind, body) in zip(commits, versions)}
    requests: list[str] = []

    def run(command, **_):
        if command[1] == "show":
            return subprocess.CompletedProcess(command, 0, head, b"")
        return subprocess.CompletedProcess(command, 0, "\0".join(commits).encode() + b"\0", b"")

    def popen(command, **_):
        return FakeBatch(answers, requests)
    return run, popen, requests


class TwelfthReviewFindings(ProseBind, RunFixture):
    """The twelfth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def edit_json(self, name: str, change) -> None:
        path = self.run / name
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_g1_a_selected_code_edit_after_the_manifest_is_stale_and_a_finding(self):
        private = self.run / "worksheets/note-1.md"
        cases = {
            "visible": (self.run / "visible-worksheet-1.md", "ICD-10-CM R05.9 Cough", "ICD-10-CM R05.1 Acute cough"),
            "private": (private, "ICD-10-CM R05.9 Cough", "ICD-10-CM R05.9 Cough\nICD-10-CM J18.9 Pneumonia"),
            "second E/M identity": (private, "CPT 99283 Emergency visit", "CPT 99283 Emergency visit\nE/M: 99284 high"),
        }
        for name, (path, old, new) in cases.items():
            with self.subTest(case=name):
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                try:
                    with self.assertRaises(review_manifest.StaleRecord):
                        review_manifest.validated_population(self.run, review_manifest.private_fingerprints(self.run))
                    finding, report, unread = self.gate()
                    self.assertEqual((True, 0), (finding, unread), report)
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_g1_an_embedded_worksheet_edited_after_the_manifest_is_stale(self):
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace(
            "## Medatrax entry fields", "## Coding worksheet\n" + VISIBLE + "\n## Medatrax entry fields"), encoding="utf-8")
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        passing_receipt(self.run)
        name_the_committed_sheet(self.run)
        review_manifest.validated_population(self.run)
        note.write_text(note.read_text(encoding="utf-8").replace("CPT 99283 Emergency visit\nE/M",
                                                                 "CPT 99284 Emergency visit\nE/M"), encoding="utf-8")
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(self.run)

    def test_g1_a_manifest_that_never_matched_its_worksheets_stays_incomplete(self):
        self.edit_json(review_manifest.MANIFEST, lambda value: value["encounters"][0]["codes"]["icd10"].append("J18.9"))
        with self.assertRaises(ValueError) as raised:
            review_manifest.validated_population(self.run)
        self.assertNotIsInstance(raised.exception, review_manifest.StaleRecord)
        finding, report, unread = self.gate()
        self.assertEqual((False, 1), (finding, unread), report)

    def test_g2_an_indented_em_label_is_selected_as_the_manifest_reader_selects_it(self):
        import worksheet_grammar
        lines = ["ICD-10-CM R05.9 Cough", "", "  E/M: 99283 low complexity", *ELEMENTS.splitlines()]
        text = "\n".join(lines) + "\n"
        self.assertEqual("99283", review_manifest.selected_codes(text, private=True)["em"])
        self.assertIn(2, worksheet_grammar.selected_em_lines(lines))
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual((1, 0, 0), (elements.blocks, elements.outside, elements.block.unread))
        # An indented label inside the selected entry's own body is the same block, not a second one.
        nested = PRIVATE.format(elements="  E/M: 99283 restated\n" + ELEMENTS)
        self.assertEqual(1, worksheet_grammar.worksheet_em_block(nested).blocks)
        refused = "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n  E/M: 99283 restated\n" + ELEMENTS + "more\n"
        self.assertEqual("refused\nmore", em_audit.block_quote(em_audit.parse_private(refused),
                                                                worksheet_grammar.REFUSAL_HEADING, "refusal"))

    def test_g2_a_check_off_reads_a_block_under_an_indented_label(self):
        self.write_private(PRIVATE.format(elements="").replace(
            "CPT 99283 Emergency visit\n", "\n  E/M: 99283 low complexity\n" + ELEMENTS))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 1, absent 0; findings 0", result.stdout)
        self.assertIn("- E/M line: E/M: 99283 low complexity", self.sheet.read_text(encoding="utf-8"))

    def test_g3_an_unchanged_rebuild_writes_neither_record(self):
        # Thirteenth review: the manifest never carries the private fingerprint, so no old format exists.
        path = self.run / review_manifest.MANIFEST
        record = self.run / review_manifest.PRIVATE_FINGERPRINTS
        before = [(target.read_bytes(), target.stat().st_mtime_ns) for target in (path, record)]
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        self.assertEqual(before, [(target.read_bytes(), target.stat().st_mtime_ns) for target in (path, record)])
        self.assertNotIn("private_worksheet_sha256", path.read_text(encoding="utf-8"))

    def fake_git(self, head: bytes, versions: list[tuple[str, bytes]]):
        """A git stand-in (run, Popen, requests): HEAD's bytes, a log, and a batch answering ``versions``."""
        return fake_git(head, versions)

    def test_g4_and_g8_the_batch_reader_skips_every_object_by_its_size(self):
        import coding_freshness
        path = ROOT / "reference" / "cpt-em-mdm-2026.md"
        wanted = b"the version the receipt bound\n"
        decoy = b"0" * 40 + b" blob 5\nlies!\n"  # a tree body that reads like a header
        stream = [("missing", b""), ("tree", decoy), ("blob", b"another version\n"), ("blob", wanted)]
        run, popen, _ = self.fake_git(b"head\n", stream)
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run) as runs, \
                mock.patch.object(coding_freshness.subprocess, "Popen", side_effect=popen) as batches:
            self.assertEqual(wanted, coding_freshness.bound_sheet_version(path, coding_freshness.sheet_sha256(wanted)))
        self.assertEqual(3, runs.call_count + batches.call_count)
        run, popen, _ = self.fake_git(wanted, stream)
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run) as runs, \
                mock.patch.object(coding_freshness.subprocess, "Popen", side_effect=popen) as batches:
            self.assertEqual(wanted, coding_freshness.bound_sheet_version(path, coding_freshness.sheet_sha256(wanted)))
        self.assertEqual((1, 0), (runs.call_count, batches.call_count))  # HEAD matched: no history walk

    def test_g5_a_bound_sheet_version_that_does_not_parse_names_the_parse_failure(self):
        import coding_freshness
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("does not parse", output)
        self.assertNotIn("coding_freshness again", output)
        self.assertNotIn("is not the one the receipt fingerprinted", output)

    def test_g6_both_graders_read_through_the_one_block_reader_with_the_skip_off(self):
        import anchor_scan
        import refusal_scan
        for module in (anchor_scan, refusal_scan):
            with self.subTest(module=module.__name__):
                tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
                function = next(node for node in tree.body
                                if isinstance(node, ast.FunctionDef) and node.name == "_block_lines")
                calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)
                         and getattr(node.func, "id", "") == "step_four_block"]
                self.assertEqual(1, len(calls))
                # Fifteenth review: step_four_block is the plain reader; nothing turns a skip off.
                self.assertNotIn("em_section", [keyword.arg for keyword in calls[0].keywords])

    def test_g7_one_light_module_holds_the_row_the_run_records_and_the_not_graded_guards(self):
        import em_audit_scope
        import specificity_scan
        for name in ("EM_AUDIT_ROW", "EM_AUDIT_RUN_RECORDS"):
            self.assertFalse(hasattr(specificity_scan, name), name)
        self.assertIs(em_audit_scope.ROW, em_audit.EXPECTED_ROW)
        for module in (specificity_scan, em_audit):
            source = Path(module.__file__).read_text(encoding="utf-8")
            for duplicate in ('"openers.json"', '"batch-codes.json"', "--submission was not supplied",
                              "so it is a direct consultation"):
                self.assertNotIn(duplicate, source, module.__name__)
        probe = "import sys, em_audit_scope\nprint(sorted({'review_manifest', 'approval_record', 'em_audit'} & set(sys.modules)))\n"
        result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, encoding="utf-8",
                                errors="replace", cwd=str(Path(__file__).parent))
        self.assertEqual("[]", result.stdout.strip(), result.stderr)

    def test_g9_both_skills_route_an_unread_exit_2(self):
        coding = (ROOT / "skills" / "icd10-cpt" / "SKILL.md").read_text(encoding="utf-8")
        paragraph = coding.split("every coded note also needs its E/M audit check-off", 1)[1].split("\n\n", 1)[0]
        skill = SKILL.read_text(encoding="utf-8")
        step_three = skill.split("## 3.", 1)[1].split("## 4.", 1)[0]
        for text in (paragraph, step_three):
            self.assertProseIn("On exit 2", text)
            self.assertProseIn("unread", text)
            self.assertProseIn("tell the clinician", text)


def entry_details_before_the_thirteenth_review(lines, index):
    """em_audit.entry_details as it stood at 5b8ba90b, re-joining the body per field line."""
    import worksheet_grammar as grammar
    first_line = re.compile(r"[^\n]*")
    tail, fields = [], {}
    unplaced, state, end = 0, "header", index + 1
    for position in range(index + 1, len(lines)):
        line = lines[position]
        field = grammar.FIELD.match(line)
        if not line.strip() or grammar.ENTRY.match(line):
            break
        if field:
            span = "\n".join(lines[index:position + 1])
            owner = first_line.match(span)
            if not grammar.detail_belongs_to_entry(span, owner, grammar.FIELD.match(span, len(span) - len(line))):
                break
        elif not grammar.indented_line(line):
            break
        end += 1
        if grammar.EM_CANDIDATE.match(line) or grammar.EM_CODE_LABEL.match(line):
            state = "element"
        elif field:
            state = field.group("field").upper()
            fields.setdefault(state, []).append(line[field.end():].strip())
        elif state == "header":
            tail.append(line.strip())
        elif state == "element":
            unplaced += 1
        else:
            fields[state][-1] = (fields[state][-1] + " " + line.strip()).strip()
    return tail, fields, unplaced, end


class ThirteenthReviewFindings(ProseBind, RunFixture):
    """The thirteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_h1_an_indented_for_entry_em_entry_is_selected_by_the_one_rule(self):
        import worksheet_grammar
        lines = ["ICD-10-CM R05.9 Cough", "", "  CPT 99283 Emergency visit", *ELEMENTS.splitlines()]
        text = "\n".join(lines) + "\n"
        self.assertEqual("99283", review_manifest.selected_codes(text, private=True)["em"])
        self.assertIn(2, worksheet_grammar.selected_em_lines(lines))
        self.assertEqual(1, worksheet_grammar.worksheet_em_block(text).blocks)
        region = worksheet_grammar.entry_region(text)
        self.assertEqual(((2, "99283"),), worksheet_grammar.selected_em(text, region,
                                                                       worksheet_grammar.read_entries(region)))
        # One rule: nothing outside worksheet_grammar's own rule reads the E/M code families.
        # em_audit still reads an E/M label as a line of an element block's body, never to select one.
        tree = ast.parse(Path(review_manifest.__file__).read_text(encoding="utf-8"))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        names |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        names |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names}
        for name in ("EM_CODES", "EM_CODE_LABEL"):
            self.assertNotIn(name, names, "review_manifest")
        # Eighteenth review: em_audit names the E/M families only to look their CPT 2026 descriptors up.
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        levels = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "mdm_levels")
        inside = {id(node) for node in ast.walk(levels)}
        self.assertEqual([], [node.lineno for node in ast.walk(tree) if isinstance(node, ast.Name)
                              and node.id == "EM_CODES" and id(node) not in inside])

    def test_h3_a_provenance_edit_and_rebuild_keeps_the_approved_manifest_bytes(self):
        manifest = self.run / review_manifest.MANIFEST
        fingerprints = self.run / review_manifest.PRIVATE_FINGERPRINTS
        before, recorded = manifest.read_bytes(), fingerprints.read_bytes()
        self.assertNotIn(b"private_worksheet_sha256", before)
        binding = review_manifest.approval_binding(self.run, batch=True)
        path = self.run / "worksheets/note-1.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "documents no further axis", "documents no further axis, restated"), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)  # eighteenth review: a finding
        self.assertIn("changed after the manifest", result.stdout)
        self.assertEqual((True, 0), self.gate()[::2])
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        self.assertEqual(before, manifest.read_bytes())
        self.assertNotEqual(recorded, fingerprints.read_bytes())
        self.assertEqual(binding, review_manifest.approval_binding(self.run, batch=True))
        self.assertEqual(0, self.invoke("--write").returncode)

    def test_h3_a_missing_fingerprint_record_is_unread_and_a_rebuild_records_it(self):
        manifest = self.run / review_manifest.MANIFEST
        before = manifest.read_bytes()
        (self.run / review_manifest.PRIVATE_FINGERPRINTS).unlink()
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        self.assertEqual(before, manifest.read_bytes())
        self.assertEqual(0, self.invoke("--write").returncode)

    def test_h4_the_history_walk_follows_every_branch(self):
        import coding_freshness
        commands = []

        def run(command, **_):
            commands.append(command)
            if command[1] == "show":
                return subprocess.CompletedProcess(command, 0, b"head\n", b"")
            if command[1] == "log":
                return subprocess.CompletedProcess(command, 0, b"", b"")
            return subprocess.CompletedProcess(command, 0, b"", b"")
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run):
            coding_freshness.bound_sheet_version(ROOT / "reference" / "cpt-em-mdm-2026.md", "0" * 64)
        self.assertIn("--full-history", next(command for command in commands if command[1] == "log"))

    def test_h5_the_note_paragraph_fallback_reads_the_label_as_the_manifest_does(self):
        for label in ("E/M:", "  E/M:", "**E/M:**", "**E/M**:"):
            with self.subTest(label=label):
                self.assertIsNotNone(em_audit.EM_PARAGRAPH.search("Plan.\n\n" + label + " low complexity; 99283.\n"))
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace("E/M: Low complexity", "**E/M:** Low complexity"),
                        encoding="utf-8")
        self.write_private(PRIVATE.format(elements=""))
        passing_receipt(self.run)
        name_the_committed_sheet(self.run)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("> **E/M:** Low complexity", self.sheet.read_text(encoding="utf-8"))

    def test_h6_specificity_scan_imports_no_unused_reader(self):
        import specificity_scan
        tree = ast.parse(Path(specificity_scan.__file__).read_text(encoding="utf-8"))
        imported = {alias.name for node in tree.body if isinstance(node, ast.ImportFrom) for alias in node.names}
        self.assertNotIn("entry_is_for_entry", imported)

    def test_h7_a_quotation_takes_its_lines_and_anchors_as_one_value(self):
        # Fifteenth review: the quotation reads one PrivateWorksheet, which holds both splittings and
        # the anchor positions together; worksheet_em_block still takes one Anchored value.
        import inspect
        import worksheet_grammar
        for function in (worksheet_grammar.step_four_block, worksheet_grammar.worksheet_em_block):
            self.assertNotIn("selected", inspect.signature(function).parameters, function.__name__)
        self.assertEqual(["private", "heading", "kind"], list(inspect.signature(em_audit.block_quote).parameters))
        text = PRIVATE.format(elements=ELEMENTS)
        other = worksheet_grammar.anchored((text + "\nextra line\n").split("\n"))
        with self.assertRaises(ValueError):
            worksheet_grammar.worksheet_em_block(text, other)

    def test_h8_the_predates_branches_are_reached_from_the_command_and_never_inside_the_gate(self):
        import completion_checks
        self.write_private(PRIVATE.format(elements=""))
        with mock.patch.object(completion_checks, "approval_moment", return_value=1_700_000_000.0):
            status, output = self.in_process("--submission", "shift-synthetic")
            with mock.patch.object(em_audit, "render", side_effect=AssertionError("rendered")), \
                    completion_checks.grading(self.run, "shift-synthetic"):
                finding, report, _ = self.gate()
        self.assertEqual(0, status, output)
        self.assertIn("not graded, approval predates the check", output)
        self.assertEqual(False, finding, report)
        self.assertIn("approval predates the check", report)

    def test_h9_entry_details_owns_a_field_from_the_lines_it_consumed(self):
        import worksheet_grammar as grammar
        texts = {str(path): path.read_text(encoding="utf-8") for path in sorted((ROOT / "fixtures").rglob("*.md"))}
        texts["separator"] = ("CPT 99283 Emergency visit\n  wrapped" + chr(0x2028) + "\n  ANCHOR: \"x\"\n"
                              "ICD-10-CM R05.9 Cough\n  more\nANCHOR: \"margin field\"\nSOURCE: second margin field\n")
        compared = 0
        for name, text in texts.items():
            lines = grammar.physical_lines(text)
            for index, line in enumerate(lines):
                if grammar.ENTRY.match(line) or grammar.EM_CODE_LABEL.match(line):
                    compared += 1
                    tail, fields, unplaced, end = em_audit.entry_walk(lines, index)
                    self.assertEqual(entry_details_before_the_thirteenth_review(lines, index),
                                     (tail, fields, len(unplaced), end), f"{name}:{index}")
        self.assertGreater(compared, 200)
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "entry_walk")
        source = ast.unparse(function)
        self.assertNotIn("detail_belongs_to_entry(", source)
        self.assertNotIn(".join(", source)


# Markers salted into every source field that could carry patient identity (ADR 0445 ruling 4).
SALT = {
    "opener name": "Zorblat Quenmar",
    "status pointer": "chart-row-zq55501",
    "status reply": "status-reply-zq55502",
    "status evidence file": "evidence-zq55503",
    "note header": "header-zq55504",
    "opener source line": "source-zq55505",
}


class FourteenthReviewFindings(ProseBind, RunFixture):
    """The fourteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def office_run(self) -> Path:
        """A synthetic office run whose identity fields all carry a SALT marker."""
        import encounter_openers
        import encounter_status
        root = self.root / "salted"
        root.mkdir()
        run = root / "run"
        source = root / "source.txt"
        source.write_text(f"Note 1 {SALT['opener name']}\n40 female {SALT['opener source line']}\n", encoding="utf-8")
        readings = root / "readings.json"
        readings.write_text(json.dumps([dict(note=1, name=SALT["opener name"], age="40", sex="female")]),
                            encoding="utf-8")
        encounter_openers.create(run, source, readings, "2026-10-01", "split", None)
        (run / "note-1.md").write_text(
            f"# Encounter {SALT['note header']}\n\n## Subjective\nCough.\n\n## Objective\nAlert.\n\n"
            "## Assessment\nCough.\n\n## Plan\nEducation: Rest.\n\n"
            "E/M: Low complexity, synthetic support; 99213, office service.\n\n"
            "## Medatrax entry fields\n| Field | Value |\n| --- | --- |\n| Gender | Female |\n\n"
            "## Tier block\nPrivate working text.\n", encoding="utf-8")
        (run / "visible-worksheet-1.md").write_text(VISIBLE.replace("99283", "99213").replace(
            "CPT 99213 Emergency visit", "CPT 99213 Office visit"), encoding="utf-8")
        (run / "worksheets").mkdir()
        (run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace("99283", "99213")).replace(
            "CPT 99283 Emergency visit", "CPT 99213 Office visit"), encoding="utf-8")
        evidence = root / (SALT["status evidence file"] + ".txt")
        evidence.write_text(f"Was this patient seen before? {SALT['status reply']}\n", encoding="utf-8")
        encounter_status.record_status(run, 1, "established", "clinician-answer", evidence,
                                       SALT["status pointer"], SALT["status reply"])
        codes = dict(icd10=["R05.9"], em="99213", cpt=[], hcpcs=[])
        (run / "inputs.json").write_text(json.dumps([dict(note="note-1.md", worksheet="visible-worksheet-1.md",
                                                          setting="office", codes=codes)]), encoding="utf-8")
        review_manifest.build(run, run / "inputs.json", batch=True, constants=CONSTANTS)
        passing_receipt(run)
        name_the_committed_sheet(run)
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(run, 1, QUESTION, [], REPLY)
        return run

    def test_i1_no_identity_field_reaches_the_check_off_or_its_word_copy(self):
        run = self.office_run()
        manifest = json.loads((run / review_manifest.MANIFEST).read_text(encoding="utf-8"))
        status = manifest["encounters"][0]["patient_status"]
        self.assertEqual((SALT["status pointer"], SALT["status reply"]), (status["pointer"], status["clinician_reply"]))
        folder = self.word_destination()
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            em_audit.main([str(run), "--write", "--docx", "--output-dir", str(folder)])
        stdout = captured.getvalue()
        self.assertIn("check-offs written 1", stdout, stdout)
        import docx_read
        markdown = (run / em_audit.OUTPUT_DIRECTORY / "note-1.md").read_text(encoding="utf-8")
        word = "\n".join(docx_read.read_docx(folder / "note-1.docx"))
        for field, marker in SALT.items():
            for name, text in (("Markdown", markdown), ("Word", word), ("stdout", stdout)):
                self.assertNotIn(marker.casefold(), text.casefold(), f"{field} reached the {name} copy")
        # The status is shown by value, evidence kind and fingerprint; the answers record keeps its replies.
        self.assertIn(f"- Patient status: established; evidence: clinician answer; fingerprint {status['evidence_sha256']}",
                      markdown)
        self.assertIn("> " + REPLY, markdown)

    def test_i2_a_freshness_run_on_another_day_leaves_the_check_off_current(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        path = self.run / review_manifest.RECEIPT
        value = json.loads(path.read_text(encoding="utf-8"))
        value["checked_as_of"] = "2026-11-02"
        path.write_text(json.dumps(value), encoding="utf-8")
        finding, report, unread = self.gate()
        self.assertEqual((False, 0), (finding, unread), report)
        self.assertIn("check-offs missing or stale 0", report)
        self.assertNotIn("2026-10-21", self.sheet.read_text(encoding="utf-8"))

    def block(self, lines: str):
        import worksheet_grammar
        return worksheet_grammar.em_block(lines)

    def test_i3_a_billed_ecg_code_must_be_named_by_the_ecg_line(self):
        base = ELEMENTS.replace("  EM-ECG: not applicable\n", "")
        cases = {
            ("93005",): {"  EM-ECG: the ADR 0443 limb for a pending reading\n": True,
                         "  EM-ECG: not applicable\n": True, "  EM-ECG: 93005 counts one test ordered\n": False},
            ("93000", "93005"): {"  EM-ECG: 93005 counts one test ordered\n": True,
                                 "  EM-ECG: 93000 read here; 93005 pending, one test ordered\n": False},
        }
        for billed, lines in cases.items():
            for line, expected in lines.items():
                with self.subTest(billed=billed, line=line):
                    found = em_audit.ecg_findings(self.block(base + line), frozenset(billed))
                    self.assertEqual(expected, bool(found), found)

    def test_i4_a_counted_item_needs_an_entry_id_and_note_text(self):
        all_none = ("  EM-PROBLEM: none | counted | none | high problems\n"
                    "  EM-DATA: none | counted | none | extensive data\n"
                    "  EM-RISK: none | counted | none | high risk\n"
                    "  EM-ANSWER: none\n  EM-ECG: not applicable\n"
                    "  EM-MDM: problems high; data high; risk high; mdm high\n  EM-LEVEL: 99215\n")
        found = em_audit.block_findings(self.block(all_none), "99215", None, None)
        self.assertEqual(3, sum("none | not counted | none" in finding for finding in found), found)
        quoteless = ELEMENTS.replace('counted | "Cough." |', 'counted | none |')
        found = em_audit.block_findings(self.block(quoteless), "99283", None, None)
        self.assertTrue(any("quotes no note text" in finding for finding in found), found)
        self.assertEqual([], em_audit.block_findings(self.block(ELEMENTS), "99283", None, {"note-1.q1"}))

    def test_i5_a_field_after_an_element_block_is_the_entry_s_own(self):
        # Twenty-seventh review: either order pairs, so a field written after the block is the
        # entry's provenance, rendered and never unread; prose after the block stays unread.
        late = '  ANCHOR: "Late field after the block."\n'
        self.write_private(PRIVATE.format(elements=ELEMENTS + late))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 0", result.stdout)
        self.assertIn("Late field after the block", self.sheet.read_text(encoding="utf-8"))
        import worksheet_grammar
        lines = worksheet_grammar.physical_lines('ICD-10-CM R05.9 Cough\n  EM-LEVEL: 99283\n' + late)
        tail, fields, unplaced, _ = em_audit.entry_walk(lines, 0)
        self.assertEqual(({"ANCHOR": ['"Late field after the block."']}, 0), (fields, len(unplaced)))
        lines = worksheet_grammar.physical_lines('ICD-10-CM R05.9 Cough\n  EM-LEVEL: 99283\n  stray prose\n')
        self.assertEqual(1, len(em_audit.entry_walk(lines, 0)[2]))

    def test_i6_no_process_lifetime_cache_of_the_sheet(self):
        import coding_freshness
        self.assertFalse(hasattr(em_audit, "_SHEET_IDS"))
        self.assertFalse(hasattr(em_audit, "reset_sheet_cache"))
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        self.assertEqual([], [ast.unparse(node) for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign))
                              and isinstance(getattr(node, "value", None), ast.Dict) and not node.value.keys])
        with mock.patch.object(coding_freshness, "bound_sheet_version",
                               wraps=coding_freshness.bound_sheet_version) as sheet:
            em_audit.render(self.run, [])
            em_audit.render(self.run, [])
        self.assertEqual(2, sheet.call_count)  # once per render, never remembered across calls

    def test_i7_the_docs_follow_the_one_selection_rule(self):
        import worksheet_grammar
        elements = (ROOT / "skills" / "_shared" / "reference" / "em-elements.md").read_text(encoding="utf-8")
        self.assertProseNotIn("for entry at the margin", elements)
        self.assertProseNotIn("margin for-entry", worksheet_grammar.worksheet_em_block.__doc__)

    def test_i8_two_runs_with_one_name_get_their_own_word_folders(self):
        first, second = self.root / "a" / "run", self.root / "b" / "run"
        for run in (first, second):
            run.mkdir(parents=True)
        one, two = em_audit.word_folder(first, None), em_audit.word_folder(second, None)
        self.assertNotEqual(one, two)
        self.assertTrue(one.name.startswith("run-"), one)
        self.assertEqual(one, em_audit.word_folder(first, None))


class FifteenthReviewFindings(ProseBind, RunFixture):
    """The fifteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_k1_a_field_after_a_blank_is_unread_never_dropped(self):
        # Twenty-first review: only a detail-shaped line is a candidate; indented prose no entry owns
        # is not one, so it no longer turns a worksheet with wrapped step prose unread.
        for stray, unread in (("  NOTE: a field no entry owns, after a blank\n", 1),
                              ("  a line of prose no entry owns, after a blank\n", 0)):
            with self.subTest(stray=stray):
                self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
                    "  CONFIDENCE: verified against ICD-10-CM FY2026\n",
                    "  CONFIDENCE: verified against ICD-10-CM FY2026\n\n" + stray))
                result = self.invoke("--write")
                self.assertEqual(2 if unread else 0, result.returncode, result.stdout + result.stderr)
                self.assertIn(f"unread remainder {unread}", result.stdout)
                placed = "1 detail line(s) could not be placed" in self.sheet.read_text(encoding="utf-8")
                self.assertEqual(bool(unread), placed)

    def test_k2_an_ecg_code_is_named_as_a_whole_token_and_not_as_not_billed(self):
        import worksheet_grammar
        base = ELEMENTS.replace("  EM-ECG: not applicable\n", "")
        cases = {"  EM-ECG: 930001 reading of the tracing\n": True,
                 "  EM-ECG: 93000 not billed; 93005 pending\n": True,
                 "  EM-ECG: 93000 read and reported here\n": False}
        for line, expected in cases.items():
            with self.subTest(line=line):
                found = em_audit.ecg_findings(worksheet_grammar.em_block(base + line), frozenset({"93000"}))
                self.assertEqual(expected, bool(found), found)
        found = em_audit.ecg_findings(worksheet_grammar.em_block(base + "  EM-ECG: 93000 not billed\n"),
                                      frozenset({"93000"}))
        self.assertEqual(["the worksheet bills 93000, but its EM-ECG line says 93000 is not billed"], found)

    def test_k3_a_flawed_re_derivation_is_a_finding_even_when_it_agrees(self):
        flawed = ELEMENTS.replace("risk low; mdm low", "risk low; mdm moderate")
        self.write_private(PRIVATE.format(elements=flawed))
        self.record(flawed)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; differ 0; damaged 0; absent 0; findings 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("- FINDING (re-derivation): the MDM line states moderate", text)
        self.assertIn("the re-derivation agrees with the worksheet", text)
        self.write_private(PRIVATE.format(elements=ELEMENTS))
        self.assertEqual(1, self.invoke("--write").returncode)
        finding, report, _ = self.gate()
        self.assertTrue(finding, report)
        self.assertIn("findings 1", report)
        rederivation = (SKILL.parent / "rederivation.md").read_text(encoding="utf-8")
        self.assertProseIn("no re-derivation finding", rederivation)

    def test_k4_provenance_under_an_em_label_in_a_step_four_block_renders_once(self):
        tail = "E/M: 99283 low complexity\n  NOTE: support restated once\n" + ELEMENTS
        self.write_private(PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n", "") + tail)
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("support restated once"), text)
        self.assertIn("  - Note: support restated once", text)

    def test_k5_step_four_block_is_the_plain_reader(self):
        import inspect
        import worksheet_grammar
        self.assertEqual(["lines", "heading", "end", "every"],
                         list(inspect.signature(worksheet_grammar.step_four_block).parameters))
        self.assertFalse(hasattr(worksheet_grammar, "resplit"))
        self.assertFalse(hasattr(worksheet_grammar, "block_text"))
        source = inspect.getsource(worksheet_grammar.step_four_lines)
        for name in ("selected", "element_body_end", "Anchored", "EM_CANDIDATE"):
            self.assertNotIn(name, source)

    def test_k7_the_batch_stops_at_the_first_matching_version(self):
        import coding_freshness
        wanted = b"the version the receipt bound\n"
        run, popen, requests = fake_git(b"head\n", [("blob", b"newer version\n"), ("blob", wanted),
                                                    ("blob", b"older version, never read\n")])
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run) as runs, \
                mock.patch.object(coding_freshness.subprocess, "Popen", side_effect=popen) as batches:
            self.assertEqual(wanted, coding_freshness.bound_sheet_version(
                ROOT / "reference" / "cpt-em-mdm-2026.md", coding_freshness.sheet_sha256(wanted)))
        self.assertEqual(2, len(requests))
        self.assertLessEqual(runs.call_count + batches.call_count, 3)


class SixteenthReviewFindings(ProseBind, RunFixture):
    """The sixteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_l1_a_blind_level_that_differs_is_shown_never_failed(self):
        consistent = ELEMENTS.replace("problems low; data straightforward; risk low; mdm low",
                                      "problems moderate; data straightforward; risk moderate; mdm moderate"
                                      ).replace("EM-LEVEL: 99283", "EM-LEVEL: 99284")
        self.record(consistent)
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 0; differ 1; damaged 0; absent 0; findings 0", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("- DIFFERS: Level: selected 99283, re-derived 99284", text)
        self.assertNotIn("FINDING (re-derivation)", text)
        self.assertEqual((False, 0), self.gate()[::2])
        # A re-derivation contradicting itself is a re-derivation finding, whatever the worksheet says.
        self.record(consistent.replace("EM-LEVEL: 99284", "EM-LEVEL: 99285"))
        self.assertEqual(1, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("- FINDING (re-derivation): the level 99285 is high MDM", text)
        self.assertTrue(self.gate()[0])
        rederivation = (SKILL.parent / "rederivation.md").read_text(encoding="utf-8")
        self.assertProseIn("never toward the worksheet", rederivation)

    def test_l1_only_the_worksheet_block_is_compared_with_the_worksheet_decisions(self):
        import worksheet_grammar
        block = worksheet_grammar.em_block(ELEMENTS.replace("EM-ECG: not applicable", "EM-ECG: not applicable")
                                           .replace("EM-ANSWER: note-1.q1", "EM-ANSWER: note-9.q1"))
        self.assertEqual([], em_audit.rederivation_findings(block, None))
        found = em_audit.block_findings(block, "99284", None, set(), billed=frozenset({"93005"}))
        self.assertEqual(3, len(found), found)  # level vs selected, answer id and ECG; the block is consistent
        inconsistent = worksheet_grammar.em_block(ELEMENTS.replace("EM-LEVEL: 99283", "EM-LEVEL: 99285"))
        self.assertEqual(["the level 99285 is high MDM, but the block's elements meet low"],
                         em_audit.rederivation_findings(inconsistent, None, em_audit.mdm_levels("2026-10-01")))

    def test_l2_one_body_rule_for_an_em_line_with_a_margin_field(self):
        import worksheet_grammar
        text = PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n",
                                                   'CPT 99283 Emergency visit\nANCHOR: "Cough."\n' + ELEMENTS)
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual((1, 0), (elements.blocks, elements.outside))
        self.write_private(text)
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 1, absent 0; findings 0", result.stdout)

    def test_l3_a_not_for_entry_code_in_the_region_is_rendered_once(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "CPT 99283 Emergency visit\n",
            "ICD-10-CM J18.9 Pneumonia, unspecified organism NOT FOR ENTRY\n"
            '  ANCHOR: "Possible pneumonia, not established."\nCPT 99283 Emergency visit\n'))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("codes rendered: icd10 1,", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertIn("- Not for entry: ICD-10-CM J18.9", text)
        self.assertEqual(1, text.count("Possible pneumonia, not established."))

    def test_l4_a_block_holding_only_the_em_line_says_so(self):
        self.write_private(PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n", "").replace(
            "## Coded, anchor was filled: confirm before submitting\n\nNone.\n",
            "## Coded, anchor was filled: confirm before submitting\n\nE/M: 99283 low complexity\n" + ELEMENTS))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("filled-anchor 1", result.stdout)
        filled = self.sheet.read_text(encoding="utf-8").split("## Codes resting on a filled anchor", 1)[1].split("\n## ", 1)[0]
        self.assertIn(em_audit.EM_ONLY_BLOCK, filled)
        self.assertNotIn("None recorded", filled)

    def test_l5_each_body_is_walked_once_per_check_off(self):
        with mock.patch.object(em_audit, "entry_walk", wraps=em_audit.entry_walk) as walk:
            em_audit.render(self.run, [])
        indexes = [call.args[1] for call in walk.call_args_list]
        self.assertEqual(len(indexes), len(set(indexes)), indexes)

    def test_l6_and_l7_no_entry_details_wrapper_and_a_word_refusal_counts_zero(self):
        self.assertFalse(hasattr(em_audit, "entry_details"))
        with mock.patch.object(repo_root, "output_root", side_effect=ValueError("no owning checkout")):
            status, output = self.in_process("--docx")
        self.assertEqual(2, status, output)
        self.assertIn("Word copies written 0", output)
        self.assertNotIn("nothing written", output)


class SeventeenthReviewFindings(ProseBind, RunFixture):
    """The seventeenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_m_a_the_mdm_levels_come_from_the_verified_cpt_2026_descriptors(self):
        import cpt_identity
        self.assertFalse(hasattr(cpt_identity, "MDM_LEVEL_OF"))
        levels = em_audit.mdm_levels("2026-10-01")
        self.assertTrue(levels.readable)
        expected = {"99202": "straightforward", "99212": "straightforward", "99282": "straightforward",
                    "99203": "low", "99213": "low", "99283": "low",
                    "99204": "moderate", "99214": "moderate", "99284": "moderate",
                    "99205": "high", "99215": "high", "99285": "high"}
        self.assertEqual(expected, {code: levels.levels[code] for code in expected})
        self.assertLessEqual({"99211", "99281"}, set(levels.unleveled))

    def test_m_a_an_unverified_descriptor_set_leaves_the_level_check_unread(self):
        import procedure_codes_lookup
        with mock.patch.object(procedure_codes_lookup, "cpt_descriptors_verified", return_value=False):
            self.assertFalse(em_audit.mdm_levels("2026-10-01").readable)
            result_status, output = self.in_process()
        self.assertEqual(2, result_status, output)
        self.assertIn("unread remainder 1", output)

    def test_m_a_a_missing_descriptor_is_unread_never_guessed(self):
        import procedure_codes_lookup
        real = procedure_codes_lookup.valid_on

        # Twenty-fifth review: a code with no entry at all is a finding, so the unread descriptor
        # here is an E/M code whose descriptor is not valid on the service date.
        def valid_on(entry, on):
            return False if entry.code == "99283" else real(entry, on)
        with mock.patch.object(procedure_codes_lookup, "valid_on", side_effect=valid_on):
            status, output = self.in_process("--write")
        self.assertEqual(2, status, output)
        self.assertIn("unread remainder 2", output)  # the worksheet block and the re-derivation
        self.assertIn("MDM level of 99283 not checked", self.sheet.read_text(encoding="utf-8"))

    def test_m_b1_a_declared_time_basis_lifts_the_level_against_mdm_check(self):
        import worksheet_grammar
        timed = ELEMENTS.replace("EM-RULE: ADR 0308 ruling 1", "EM-RULE: " + em_audit.TIME_BASIS).replace(
            "EM-LEVEL: 99283", "EM-LEVEL: 99214")
        levels = em_audit.mdm_levels("2026-10-01")
        block = worksheet_grammar.em_block(timed)
        self.assertEqual([], em_audit.rederivation_findings(block, None, levels))
        self.assertEqual(["the block level 99214 differs from the selected code 99213"],
                         em_audit.block_findings(block, "99213", None, {"note-1.q1"}, levels=levels))
        undeclared = worksheet_grammar.em_block(timed.replace(em_audit.TIME_BASIS, "ADR 0308 ruling 1"))
        self.assertEqual(["the level 99214 is moderate MDM, but the block's elements meet low"],
                         em_audit.rederivation_findings(undeclared, None, levels))
        elements = (ROOT / "skills" / "_shared" / "reference" / "em-elements.md").read_text(encoding="utf-8")
        self.assertProseIn(em_audit.TIME_BASIS, elements)

    def test_m_b2_every_refusal_block_is_quoted(self):
        second = ("\n## Not coded, nothing established it\n\nA second refusal record\n"
                  "  NOT CODED: J20.9  Acute bronchitis, unspecified\n  needs: a documented course\n"
                  "  proposed instead: R05.9  Cough\n")
        self.write_private(PRIVATE.format(elements=ELEMENTS) + second)
        self.assertEqual(0, self.invoke("--write").returncode)
        refused = self.sheet.read_text(encoding="utf-8").split("## Codes refused", 1)[1].split("\n## ", 1)[0]
        self.assertIn("J18.9", refused)
        self.assertIn("J20.9", refused)

    def test_m_b3_an_em_label_inside_a_code_entry_has_one_owner(self):
        self.write_private(PRIVATE.format(elements="").replace(
            "CPT 99283 Emergency visit\n", "").replace(
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n",
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n  E/M: 99283 low complexity\n"
            "  NOTE: support written under the label\n" + ELEMENTS))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 0", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("support written under the label"), text)

    def test_m_b4_a_selected_note_is_not_refused_for_another_notes_worksheet(self):
        validated = review_manifest.validated_population(self.run)
        fingerprints = review_manifest.private_fingerprints(self.run)
        first = validated.encounters[0]
        other_path = str(self.run / "worksheets" / "note-2.md")
        other = review_manifest.ValidatedEncounter(dict(first.item, order=2, id="note-2",
                                                        private_worksheet_path=other_path),
                                                   first.note, first.worksheet, first.private)
        wider = review_manifest.ValidatedRun(validated.manifest, validated.receipt, (first, other))
        moved = dict(fingerprints, **{other_path: "0" * 64})
        with mock.patch.object(review_manifest, "validated_population", return_value=wider), \
                mock.patch.object(review_manifest, "private_fingerprints", return_value=moved):
            self.assertEqual([], em_audit.render(self.run, [1])[0].moved)
            # Twenty-fifth review: the moved note is refused by itself; the render goes on.
            self.assertEqual([2], em_audit.render(self.run, [])[0].moved)

    def test_m_b5_a_damaged_worksheet_without_a_manifest_is_incomplete_records(self):
        # Twenty-fourth review: without a manifest no worksheet is read; the run is incomplete.
        (self.run / review_manifest.MANIFEST).unlink()
        (self.run / "worksheets/note-1.md").write_text("ICD-10-CM R05.9 Cough" + chr(1) + "\n", encoding="utf-8")
        finding, report, unread = self.gate()
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("the coding records are missing or cannot be read", report)

    def test_m_b6_the_header_rule_is_said_where_it_lives_and_no_fixture_moves(self):
        import worksheet_grammar
        self.assertIn("EM- lines exist only in", worksheet_grammar.entry_is_for_entry.__doc__)
        moved = []
        for path in sorted((ROOT / "fixtures").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            entries = list(worksheet_grammar.ENTRY.finditer(text))
            for index in range(len(entries)):
                start = entries[index].start()
                end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
                field = worksheet_grammar.FIELD.search(text, start, end)
                header = text[start:field.start() if field else end]
                if (worksheet_grammar.NOT_FOR_ENTRY.search(header) is None) != worksheet_grammar.entry_is_for_entry(
                        text, entries, index):
                    moved.append(f"{path}:{index}")
        self.assertEqual([], moved)

    def test_m_b7_one_payload_helper_in_the_answers_record(self):
        tree = ast.parse(Path(preapproval_answers.__file__).read_text(encoding="utf-8"))
        record = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "record")
        dumps = [node for node in ast.walk(record) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == "dumps"]
        self.assertEqual(1, len(dumps), [ast.unparse(node) for node in dumps])


class EighteenthReviewFindings(ProseBind, RunFixture):
    """The eighteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_n1_a_label_selects_only_an_em_identity_outside_a_rejected_entry(self):
        import worksheet_grammar
        entries = 'ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\n'
        # (a) a label naming a code outside the E/M families is not the E/M identity.
        with self.assertRaises(ValueError):
            review_manifest.selected_codes(entries + "E/M: 93000 tracing reviewed\n", private=True)
        # (b) a label inside a NOT FOR ENTRY entry is a rejected level, never the final one.
        rejected = (entries + "CPT 99283 Emergency visit\nCPT 99285 Emergency visit, high MDM NOT FOR ENTRY\n"
                    "  E/M: 99285 rejected level\n" + ELEMENTS.replace("99283", "99285"))
        self.assertEqual("99283", review_manifest.selected_codes(rejected, private=True)["em"])
        lines = worksheet_grammar.physical_lines(rejected)
        self.assertNotIn(lines.index("  E/M: 99285 rejected level"), worksheet_grammar.selected_em_lines(lines))
        elements = worksheet_grammar.worksheet_em_block(rejected)
        self.assertEqual((0, len(ELEMENTS.splitlines())), (elements.blocks, elements.outside))
        # No committed fixture's selected E/M identity moves.
        moved = []
        for path in sorted((ROOT / "fixtures").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            region = worksheet_grammar.entry_region(text)
            labels = {match.group("code") for match in worksheet_grammar.EM_CODE_LABEL.finditer(text)}
            entries_ = {entry.code.upper() for entry in worksheet_grammar.read_entries(region)
                        if entry.for_entry and worksheet_grammar.em_identity(entry.system, entry.code)}
            new = {code for _, code in worksheet_grammar.selected_em(text, region, worksheet_grammar.read_entries(region))}
            if labels | entries_ != new:
                moved.append(str(path))
        self.assertEqual([], moved)

    def test_n2_an_indented_heading_ends_an_element_body(self):
        import worksheet_grammar
        text = ('ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\nCPT 99283 Emergency visit\n' + ELEMENTS
                + "  ## Not coded, nothing established it\n  EM-RULE: a stray line under the refusal heading\n"
                "  NOT CODED: J18.9  Pneumonia, unspecified organism\n")
        elements = worksheet_grammar.worksheet_em_block(text)
        self.assertEqual(("ADR 0308 ruling 1",), elements.block.rules)
        self.assertEqual(1, elements.outside)
        private = em_audit.parse_private(text)
        quote = em_audit.block_quote(private, worksheet_grammar.REFUSAL_HEADING, "refusal")
        self.assertIn("a stray line under the refusal heading", quote)
        self.assertEqual(1, quote.count("NOT CODED: J18.9"))

    def test_n3_a_changed_status_evidence_is_stale(self):
        run = FourteenthReviewFindings.office_run(self)
        status = json.loads((run / review_manifest.MANIFEST).read_text(encoding="utf-8"))["encounters"][0]["patient_status"]
        evidence = Path(status["evidence_path"])
        evidence.write_text(evidence.read_text(encoding="utf-8") + "edited after the manifest\n", encoding="utf-8")
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(run)

    def test_n3_a_moved_run_is_stale_and_a_mismatched_pair_never_valid(self):
        import shutil
        copy = self.root / "moved" / "run"
        shutil.copytree(self.run, copy)
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(copy)
        path = self.run / review_manifest.MANIFEST
        value = json.loads(path.read_text(encoding="utf-8"))
        other = self.run / "worksheets" / "other-name.md"
        shutil.copy(self.run / "worksheets/note-1.md", other)
        value["encounters"][0]["private_worksheet_path"] = str(other)
        path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaises(ValueError) as raised:
            review_manifest.validated_population(self.run)
        self.assertNotIsInstance(raised.exception, review_manifest.StaleRecord)

    def test_n4_the_command_reports_a_changed_record_as_a_finding(self):
        self.edit_manifest = json.loads((self.run / review_manifest.MANIFEST).read_text(encoding="utf-8"))
        self.edit_manifest["encounters"][0]["normalized_sha256"] = "0" * 64
        (self.run / review_manifest.MANIFEST).write_text(json.dumps(self.edit_manifest), encoding="utf-8")
        status, output = self.in_process()
        self.assertEqual(1, status, output)
        self.assertIn("finding", output)
        self.assertIn("changed or went missing after the manifest", output)
        self.assertTrue(self.gate()[0])
        step = SKILL.read_text(encoding="utf-8").split("## 1.", 1)[1].split("## 2.", 1)[0]
        self.assertProseIn("Exit 1 naming a record that changed or went missing after the manifest", step)

    def test_n6_the_mdm_levels_read_only_the_em_codes(self):
        import procedure_codes_lookup
        with mock.patch.object(procedure_codes_lookup, "find", side_effect=AssertionError("table scan")):
            levels = em_audit.mdm_levels("2026-10-01")
        self.assertEqual("low", levels.levels["99283"])
        self.assertIn("99281", levels.unleveled)

    def test_n7_the_word_destination_rule_is_the_shared_guard(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "word_folder")
        source = ast.unparse(function)
        self.assertNotIn("enclosing_checkout", source)
        self.assertNotIn("is_relative_to", source)
        self.assertIn("ensure_main_checkout", source)
        checkout = self.root / "main-checkout"
        (checkout / ".git").mkdir(parents=True)
        with mock.patch.object(repo_root, "main_repo_root", return_value=checkout):
            with self.assertRaises(repo_root.OutsideOutput):
                repo_root.ensure_main_checkout(checkout / "reference" / "audit", under_output=True)
            self.assertEqual((checkout / "output" / "audit").resolve(),
                             repo_root.ensure_main_checkout(checkout / "output" / "audit", under_output=True))
            self.assertEqual((checkout / "reference").resolve(), repo_root.ensure_main_checkout(checkout / "reference"))


class NineteenthReviewFindings(ProseBind, RunFixture):
    """The nineteenth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def gate(self):
        return em_audit_gate(self.run, "shift-synthetic")

    def test_o1_an_unselected_label_and_its_lines_are_counted_unread(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "CPT 99283 Emergency visit\n",
            "E/M: 99241 office consultation, not an E/M identity\n  NOTE: support under the unselected label\n"
            "CPT 99283 Emergency visit\n"))
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 2", result.stdout)
        self.assertNotIn("support under the unselected label", self.sheet.read_text(encoding="utf-8"))

    def test_o2_a_label_under_a_rejected_visible_entry_follows_the_private_rule(self):
        visible = ("ICD-10-CM: R05.9 Cough\nCPT: 99285 Emergency visit, high MDM NOT FOR ENTRY\n"
                   "  E/M: 99285 rejected level\nCPT: 99283 Emergency visit\n")
        private = ('ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\nCPT 99285 Emergency visit, high MDM NOT FOR ENTRY\n'
                   "  E/M: 99285 rejected level\nCPT 99283 Emergency visit\n")
        self.assertEqual("99283", review_manifest.selected_codes(private, private=True)["em"])
        self.assertEqual("99283", review_manifest.selected_codes(visible, private=False)["em"])

    def test_o3_an_answer_recorded_after_the_render_stales_the_check_off_until_rendered_again(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        self.assertEqual((False, 0), self.gate()[::2])
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, "A synthetic second question before approval?", [],
                                       "Synthetic second reply.")
        finding, report, _ = self.gate()
        self.assertTrue(finding, report)
        self.assertIn("check-offs missing or stale 1", report)
        self.assertIn("render the check-offs again with --write", report)
        self.assertEqual(0, self.invoke("--write").returncode)
        self.assertEqual((False, 0), self.gate()[::2])
        for path in (SKILL, ROOT / "skills" / "icd10-cpt" / "SKILL.md"):
            self.assertProseIn("after the last pre-approval answer is recorded", path.read_text(encoding="utf-8"))

    def test_o4_the_module_exit_contract_matches_the_command(self):
        doc = em_audit.__doc__
        exit_two = doc.split("; 2 when", 1)[1]
        self.assertNotIn("private worksheet changed", exit_two)
        self.assertIn("a record that changed or went missing after the manifest",
                      " ".join(doc.split("; 2 when", 1)[0].split()))

    def test_o5_a_sheet_version_the_reader_refuses_is_an_incomplete_tool_defect(self):
        import coding_freshness
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=b"no entries here"):
            finding, report, unread = self.gate()
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("tool defect", report)

    def test_o6_the_scope_check_runs_once_on_the_terminal_path(self):
        import em_audit_scope
        import specificity_scan
        with mock.patch.object(em_audit_scope, "not_graded", wraps=em_audit_scope.not_graded) as scope:
            specificity_scan.em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual(1, scope.call_count)
        with mock.patch.object(em_audit_scope, "not_graded", wraps=em_audit_scope.not_graded) as scope:
            em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual(0, scope.call_count)  # twenty-second review: the scope is the production gate's


def committed_tree(root: Path, steps: list[tuple[str, str | None, bytes | None]]) -> None:
    """A throwaway repository: each step writes ``(path, None, bytes)`` or renames ``(old, new, None)``, then commits."""
    def run(*args):
        subprocess.run(["git", "-c", "user.email=synthetic@example.invalid", "-c", "user.name=synthetic",
                        "-c", "commit.gpgsign=false", *args], cwd=root, check=True, capture_output=True)
    run("init", "-q")
    for index, (first, second, body) in enumerate(steps):
        if second is None:
            (root / first).parent.mkdir(parents=True, exist_ok=True)
            (root / first).write_bytes(body)
            run("add", "-A")
        else:
            run("mv", first, second)
        run("commit", "-qm", f"step {index}")


class TwentiethReviewFindings(ProseBind, RunFixture):
    """The twentieth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def assert_changed_after_the_manifest(self, run: Path) -> None:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            status = em_audit.main([str(run)])
        self.assertEqual(1, status, captured.getvalue())
        self.assertIn("changed or went missing after the manifest", captured.getvalue())
        finding, report, unread = em_audit_gate(run, "shift-synthetic")
        self.assertEqual((True, 0), (finding, unread), report)
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(run)

    def test_p1_a_word_copy_goes_only_under_the_main_checkout_output(self):
        checkout = self.fake_checkout()
        outside = self.root / "elsewhere"
        with mock.patch.object(repo_root, "main_repo_root", return_value=checkout):
            with self.assertRaises(repo_root.OutsideOutput):
                repo_root.ensure_main_checkout(outside / "audit", under_output=True)
            # The default rule is unchanged: an explicit export outside every checkout stays allowed.
            self.assertEqual((outside / "audit").resolve(), repo_root.ensure_main_checkout(outside / "audit"))
            with self.assertRaises(em_audit.WordTargetRefused):
                em_audit.word_folder(self.run, outside)
            status, output = self.in_process("--docx", "--output-dir", outside)
            self.assertEqual(2, status, output)
            self.assertIn("Word copy refused - " + em_audit.WORD_REFUSALS["target"], output)
            self.assertFalse(outside.exists())
            status, output = self.in_process("--docx", "--output-dir", checkout / "output" / "audit")
            self.assertEqual(0, status, output)
            self.assertTrue((checkout / "output" / "audit" / "note-1.docx").is_file())
        for text in (em_audit.WORD_REFUSALS["target"], em_audit.word_folder.__doc__, SKILL.read_text(encoding="utf-8")):
            self.assertProseNotIn("outside every checkout", text)

    def test_p2_an_opener_record_that_changed_or_went_missing_is_a_finding(self):
        source = self.root / "source.txt"
        encounter = self.run / "encounters" / "encounter-1.txt"
        unassigned = self.run / "encounters" / "unassigned.txt"
        record = self.run / "openers.json"
        for path, edited in ((source, b"Note 1 Example Person\n41 female\n"), (encounter, b"edited\n"),
                             (unassigned, b"edited\n"), (record, None)):
            original = path.read_bytes()
            changes = [("missing", path.unlink)]
            if edited is not None:
                changes.append(("edited", lambda path=path, edited=edited: path.write_bytes(edited)))
            for name, change in changes:
                with self.subTest(path=path.name, change=name):
                    change()
                    try:
                        self.assert_changed_after_the_manifest(self.run)
                    finally:
                        path.write_bytes(original)

    def test_p2_a_note_or_worksheet_the_manifest_recorded_and_now_missing_is_a_finding(self):
        for path in (self.run / "note-1.md", self.run / "visible-worksheet-1.md", self.run / "worksheets" / "note-1.md"):
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.unlink()
                try:
                    self.assert_changed_after_the_manifest(self.run)
                finally:
                    path.write_bytes(original)

    def test_p2_patient_status_evidence_or_record_gone_after_the_manifest_is_a_finding(self):
        run = FourteenthReviewFindings.office_run(self)
        status = json.loads((run / "encounter-status.json").read_text(encoding="utf-8"))["encounters"]["1"]
        for path in (Path(status["evidence_path"]), run / "encounter-status.json"):
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.unlink()
                try:
                    self.assert_changed_after_the_manifest(run)
                finally:
                    path.write_bytes(original)

    def test_p2_a_missing_freshness_receipt_stays_incomplete(self):
        (self.run / review_manifest.RECEIPT).unlink()
        status, output = self.in_process()
        self.assertEqual(2, status, output)
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)

    def test_p3_the_command_and_the_gate_read_one_start_row(self):
        import completion_checks
        keys = []
        real = completion_checks.active

        def spy(key, moment=None):
            keys.append(key)
            return real(key, moment)
        with mock.patch.object(completion_checks, "active", side_effect=spy):
            em_audit.render(self.run, [])
            command = {key for key in keys if key.startswith("em_audit:")}
            keys.clear()
            em_audit.completion_gate(self.run, "shift-synthetic")
            gate = {key for key in keys if key.startswith("em_audit:")}
        self.assertEqual({"em_audit:completion_gate"}, command)
        self.assertEqual(command, gate)

    def test_p4_a_sheet_version_committed_under_its_former_name_is_found(self):
        import coding_freshness
        repository = self.root / "repository"
        repository.mkdir()
        first, second, third = b"first version\n", b"second version\n", b"third version\n"
        committed_tree(repository, [("reference/old-sheet.md", None, first), ("reference/old-sheet.md", None, second),
                                    ("reference/old-sheet.md", "reference/new-sheet.md", None),
                                    ("reference/new-sheet.md", None, third)])
        sheet = repository / "reference" / "new-sheet.md"
        with mock.patch.object(coding_freshness, "ROOT", repository):
            for version in (third, second, first):
                with self.subTest(version=version):
                    self.assertEqual(version, coding_freshness.bound_sheet_version(
                        sheet, coding_freshness.sheet_sha256(version)))
            self.assertIsNone(coding_freshness.bound_sheet_version(sheet, "0" * 64))

    def test_p4_the_history_walk_follows_renames_on_the_full_history(self):
        import coding_freshness
        commands = []

        def run(command, **_):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, b"head\n" if command[1] == "show" else b"", b"")
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run):
            coding_freshness.bound_sheet_version(ROOT / "reference" / "cpt-em-mdm-2026.md", "0" * 64)
        log = next(command for command in commands if command[1] == "log")
        for option in ("--full-history", "--follow", "--name-only"):
            self.assertIn(option, log)

    def test_p5_a_line_split_is_refused_in_the_visible_mode(self):
        import worksheet_grammar
        visible = VISIBLE
        reading = worksheet_grammar.entry_reading(visible, private=False)
        entries = worksheet_grammar.read_entries(reading)
        with self.assertRaises(ValueError):
            worksheet_grammar.selected_em(visible, reading, entries, worksheet_grammar.physical_lines(reading),
                                          private=False)
        self.assertEqual("99283", review_manifest.selected_codes(visible, private=False)["em"])

    def test_p7_docx_write_passes_its_destination_rule_through(self):
        import docx_write
        calls = []

        def guard(destination, *args, **options):
            calls.append(options)
            raise repo_root.ForeignCheckout(Path(destination), self.root)
        with mock.patch.object(docx_write, "ensure_main_checkout", side_effect=guard):
            for under_output in (False, True):
                with self.assertRaises(repo_root.ForeignCheckout):
                    docx_write.write_docx("# One\n", self.root / "out.docx", under_output=under_output)
        self.assertEqual([{"under_output": False}, {"under_output": True}], calls)


def committed_worksheets() -> dict[str, str]:
    """Every committed fixture file carrying a code entry, by path: the real worksheet population."""
    found = {}
    for path in sorted((ROOT / "fixtures").rglob("*.md")):
        if path.name in ("README.md", "assertions.md"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if em_audit.parse_private(text).entries:
            found[path.relative_to(ROOT).as_posix()] = text
    return found


class TwentyFirstReviewFindings(ProseBind, RunFixture):
    """The twenty-first code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_q1_wrapped_prose_before_the_entries_is_not_an_unplaced_detail_line(self):
        worksheets = committed_worksheets()
        for name in ("fixtures/filled-anchor/run-2/case-03.md", "fixtures/filled-anchor/run-2/case-05.md",
                     "fixtures/filled-anchor/run-2/case-06.md", "fixtures/worksheet-grammar-positive-control/case-01.md"):
            self.assertIn(name, worksheets)
        unread = {name: em_audit.for_entry_codes(em_audit.parse_private(text))[1]
                  for name, text in worksheets.items()}
        self.assertEqual({}, {name: count for name, count in unread.items() if count})

    def test_q1_only_a_field_nothing_owns_is_counted_and_its_wrap_is_its_own(self):
        prose = "## Encounter summary\n\n1. A synthetic list item whose sentence\n   wraps onto an indented line.\n\n"
        orphan = "\n  NOTE: an orphaned field\n    whose value wraps onto a second line\n"
        for prefix, expected in ((prose, 0), (prose + orphan, 1)):
            with self.subTest(expected=expected):
                private = em_audit.parse_private(prefix + PRIVATE.format(elements=ELEMENTS))
                self.assertEqual(expected, em_audit.for_entry_codes(private)[1])

    def test_q2_a_failed_fingerprint_write_leaves_no_false_edit_finding_and_a_rebuild_repairs_it(self):
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace("Cough.", "Cough and fever."), encoding="utf-8")
        private = self.run / "worksheets/note-1.md"
        private.write_text(private.read_text(encoding="utf-8").replace(
            "needs: imaging establishing pneumonia", "needs: imaging, edited with the note"), encoding="utf-8")
        manifest = (self.run / review_manifest.MANIFEST).read_bytes()
        real = review_manifest.update_tool_record

        def failing(target, *args, **options):
            if Path(target).name == Path(review_manifest.PRIVATE_FINGERPRINTS).name:
                raise OSError("synthetic write failure")
            return real(target, *args, **options)
        with mock.patch.object(review_manifest, "update_tool_record", side_effect=failing):
            with self.assertRaises(OSError):
                review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        self.assertEqual(manifest, (self.run / review_manifest.MANIFEST).read_bytes())
        status, output = self.in_process()
        self.assertEqual(1, status, output)
        self.assertNotIn("private worksheet changed", output)
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        passing_receipt(self.run)
        name_the_committed_sheet(self.run)
        status, output = self.in_process()
        self.assertEqual(0, status, output)

    def test_q3_a_relative_output_folder_is_read_from_the_main_checkout(self):
        import os
        checkout = self.fake_checkout()
        worktree = self.root / "worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        previous = os.getcwd()
        os.chdir(worktree)
        try:
            with mock.patch.object(repo_root, "main_repo_root", return_value=checkout):
                self.assertEqual((checkout / "output" / "em-audit" / "x").resolve(),
                                 em_audit.word_folder(self.run, Path("output/em-audit/x")))
                status, output = self.in_process("--docx", "--output-dir", "output/em-audit/x")
                self.assertEqual(0, status, output)
                absolute = checkout / "output" / "absolute"
                self.assertEqual(absolute.resolve(), em_audit.word_folder(self.run, absolute))
        finally:
            os.chdir(previous)
        self.assertTrue((checkout / "output" / "em-audit" / "x" / "note-1.docx").is_file())
        self.assertFalse((worktree / "output").exists())

    def test_q5_review_manifest_reads_the_worksheet_grammar_at_module_level(self):
        source = Path(review_manifest.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for function in (node for node in tree.body if isinstance(node, ast.FunctionDef)
                         and node.name in ("code_key", "selected_codes")):
            self.assertEqual([], [node for node in ast.walk(function) if isinstance(node, (ast.Import, ast.ImportFrom))],
                             function.name)
        self.assertTrue(any(isinstance(node, ast.ImportFrom) and node.module == "worksheet_grammar" for node in tree.body))
        self.assertNotIn("\n\n\n\ndef code_key", source)


class TwentySecondReviewFindings(ProseBind, RunFixture):
    """The twenty-second code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_s1_an_indented_hash_line_in_a_body_is_body_text_for_both_rules(self):
        import specificity_scan
        import worksheet_grammar
        text = ("ICD-10-CM E11.9 Type 2 diabetes mellitus without complications\n"
                "  # 2 visits this year\n"
                "  SPECIFICITY: complete - the synthetic encounter documents no further axis\n")
        flags, orphans = specificity_scan.read_flags_with_orphans(text)
        self.assertEqual((["E11.9"], 0), ([flag.code for flag in flags], orphans))
        self.assertEqual(3, worksheet_grammar.body_end(text.split("\n"), 0))
        codes, unread = em_audit.for_entry_codes(em_audit.parse_private(text))
        self.assertEqual(0, unread)
        self.assertIn("SPECIFICITY", codes[0][4])

    def test_s1_a_step_four_heading_ends_a_body_for_both_rules(self):
        import worksheet_grammar
        text = ("ICD-10-CM E11.9 Type 2 diabetes mellitus without complications\n"
                "  ## Not coded, nothing established it\n"
                "  SPECIFICITY: complete - the synthetic encounter documents no further axis\n")
        entry = next(worksheet_grammar.ENTRY.finditer(text))
        detail = next(worksheet_grammar.FIELD.finditer(text))
        self.assertFalse(worksheet_grammar.detail_belongs_to_entry(text, entry, detail))
        self.assertEqual(1, worksheet_grammar.body_end(text.split("\n"), 0))

    def test_s1_the_two_rules_agree_on_every_committed_fixture(self):
        import worksheet_grammar as grammar
        disagree, details = [], 0
        for name, text in committed_worksheets().items():
            entries = list(grammar.ENTRY.finditer(text))
            lines = text.split("\n")
            for detail in grammar.FIELD.finditer(text):
                owner = next((entry for entry in reversed(entries) if entry.start() < detail.start()), None)
                if owner is None:
                    continue
                details += 1
                first, line = text.count("\n", 0, owner.start()), text.count("\n", 0, detail.start())
                if (first < line < grammar.body_end(lines, first)) != grammar.detail_belongs_to_entry(text, owner, detail):
                    disagree.append((name, line + 1))
        self.assertGreater(details, 0)
        self.assertEqual([], disagree)

    def test_s2_a_negation_on_either_side_of_the_billed_code_is_not_naming_it(self):
        import worksheet_grammar
        base = ELEMENTS.replace("  EM-ECG: not applicable\n", "")
        cases = {"  EM-ECG: not billed: 93005\n": True,
                 "  EM-ECG: 93005 not billed\n": True,
                 "  EM-ECG: 93005 is not billed; reading documented\n": True,
                 "  EM-ECG: 93000 not billed; 93005 tracing only, billed here\n": False,
                 "  EM-ECG: 93005 tracing only. Interpretation 93000 not billed\n": False}
        for line, expected in cases.items():
            with self.subTest(line=line):
                found = em_audit.ecg_findings(worksheet_grammar.em_block(base + line), frozenset({"93005"}))
                self.assertEqual(expected, bool(found), found)
                if expected:
                    self.assertEqual(["the worksheet bills 93005, but its EM-ECG line says 93005 is not billed"], found)

    def private_code_edit(self) -> None:
        """Add a fever code to the worksheets and inputs, as a coding correction before a rebuild."""
        private = self.run / "worksheets/note-1.md"
        private.write_text(private.read_text(encoding="utf-8").replace(
            "CPT 99283 Emergency visit\n", 'ICD-10-CM R50.9 Fever, unspecified\n  ANCHOR: "Cough."\n'
            "CPT 99283 Emergency visit\n", 1), encoding="utf-8")
        visible = self.run / "visible-worksheet-1.md"
        visible.write_text(visible.read_text(encoding="utf-8").replace(
            "CPT 99283", "ICD-10-CM R50.9 Fever, unspecified\nCPT 99283", 1), encoding="utf-8")
        inputs = self.run / "inputs.json"
        rows = json.loads(inputs.read_text(encoding="utf-8"))
        rows[0]["codes"]["icd10"].append("R50.9")
        inputs.write_text(json.dumps(rows), encoding="utf-8")

    def failed_manifest_write(self) -> None:
        real = review_manifest.update_tool_record

        def failing(target, *args, **options):
            if Path(target).name == Path(review_manifest.MANIFEST).name:
                raise OSError("synthetic manifest write failure")
            return real(target, *args, **options)
        with mock.patch.object(review_manifest, "update_tool_record", side_effect=failing):
            with self.assertRaises(OSError):
                review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)

    def test_s3_a_manifest_write_that_fails_after_a_code_edit_leaves_a_stale_manifest(self):
        self.private_code_edit()
        self.failed_manifest_write()
        fingerprints = review_manifest.private_fingerprints(self.run)
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(self.run, fingerprints)
        # The visible worksheet restored to the manifest's codes: only the private worksheet
        # disagrees, and it matches the fingerprint the failed build recorded, so nothing the run
        # records changed after the manifest. Twenty-seventh review: the manifest never matched
        # this worksheet, so it is refused and rebuilt, incomplete rather than a finding.
        visible = self.run / "visible-worksheet-1.md"
        visible.write_text(VISIBLE, encoding="utf-8")
        with self.assertRaises(ValueError) as refused:
            review_manifest.validated_population(self.run, fingerprints)
        self.assertNotIsInstance(refused.exception, review_manifest.StaleRecord)
        finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)

    def test_s4_a_wrapped_filled_mark_is_read_and_an_unclosed_one_is_unread(self):
        self.assertEqual((["[SOURCE: filled - data: chest radiograph]"], 0), em_audit.filled_marks(
            "E/M: 99283 support [SOURCE: filled -\n  data: chest\n  radiograph]\n"))
        self.assertEqual(([], 1), em_audit.filled_marks("E/M: 99283 support [SOURCE: filled - data: chest\n\nnext\n"))
        self.assertEqual(([], 0), em_audit.filled_marks("ICD-10-CM E66.9 [SOURCE: filled - BMI 31]\n"))
        for visible, unread in ((VISIBLE.replace("[SOURCE: filled - data: chest radiograph]",
                                                 "[SOURCE: filled - data:\n  chest radiograph]"), 0),
                                (VISIBLE.replace("[SOURCE: filled - data: chest radiograph]",
                                                 "[SOURCE: filled - data: chest radiograph"), 1)):
            with self.subTest(unread=unread):
                (self.run / "visible-worksheet-1.md").write_text(visible, encoding="utf-8")
                review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
                passing_receipt(self.run)
                name_the_committed_sheet(self.run)
                status, output = self.in_process("--write")
                self.assertIn(f"unread remainder {unread}", output)
                text = self.sheet.read_text(encoding="utf-8")
                if unread:
                    self.assertIn("- Filled marks: none; 1 could not be read", text)
                else:
                    self.assertIn("- Filled marks: [SOURCE: filled - data: chest radiograph]", text)

    def test_s5_a_note_left_unread_does_not_stop_its_neighbor_being_compared(self):
        folder = self.run / em_audit.OUTPUT_DIRECTORY
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "note-1.md").write_text("# One, unread\n", encoding="utf-8")
        (folder / "note-2.md").write_text("# Two, as rendered before an answer\n", encoding="utf-8")
        sheets = [em_audit.Sheet(1, "note-1", "# One\n", 1), em_audit.Sheet(2, "note-2", "# Two\n", 0)]
        tally = em_audit.Tally()
        tally.unread = 1
        with mock.patch.object(em_audit, "render", return_value=(tally, 2, sheets)):
            finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertTrue(finding, report)
        self.assertIn("check-offs missing or stale 1", report)
        self.assertIn("render the check-offs again with --write", report)
        self.assertIn("not compared 1", report)
        tally.run_wide.append("no committed CPT MDM sheet version matches the receipt")
        with mock.patch.object(em_audit, "render", return_value=(tally, 2, sheets)):
            finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertFalse(finding, report)
        self.assertIn("check-offs missing or stale 0", report)
        self.assertIn("no committed CPT MDM sheet version matches the receipt", report)

    def test_s5_the_render_attributes_unread_to_its_note_and_names_run_wide_reasons(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace(
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n",
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n\n  NOTE: a field no entry owns\n"))
        tally, _, sheets = em_audit.render(self.run, [])
        self.assertEqual(([1], []), ([sheet_.unread for sheet_ in sheets], tally.run_wide))
        import coding_freshness
        with mock.patch.object(coding_freshness, "bound_sheet_version", return_value=None):
            tally, _, sheets = em_audit.render(self.run, [])
        self.assertEqual(1, len(tally.run_wide))

    def test_s6_the_production_gate_is_the_one_the_tests_drive(self):
        import specificity_scan
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("scoped_gate", functions)
        self.assertNotIn("not_graded", Path(em_audit.__file__).read_text(encoding="utf-8"))
        gate = next(node for node in ast.parse(Path(specificity_scan.__file__).read_text(encoding="utf-8")).body
                    if isinstance(node, ast.FunctionDef) and node.name == "em_audit_gate")
        calls = {node.func.attr for node in ast.walk(gate)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertIn("completion_gate", calls)

    def test_s7_the_history_walk_reads_through_the_shared_byte_safe_reader(self):
        import coding_freshness
        import git_paths
        with mock.patch.object(git_paths, "read_path_records", wraps=git_paths.read_path_records) as reader:
            coding_freshness.bound_sheet_version(ROOT / "reference" / "cpt-em-mdm-2026.md", "0" * 64)
        self.assertEqual(1, reader.call_count)
        self.assertNotIn('split("\\0")', Path(coding_freshness.__file__).read_text(encoding="utf-8"))


class TwentyThirdReviewFindings(ProseBind, RunFixture):
    """The twenty-third code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_t1_a_negation_qualifies_only_the_code_it_is_attached_to(self):
        import worksheet_grammar
        base = ELEMENTS.replace("  EM-ECG: not applicable\n", "")
        both, one = frozenset({"93000", "93005"}), frozenset({"93005"})
        cases = {"  EM-ECG: 93005 billed, 93000 not billed\n": (both, ["93000"]),
                 "  EM-ECG: 93005 billed while the read is pending (93000 not billed)\n": (both, ["93000"]),
                 "  EM-ECG: not billed: 93005\n": (one, ["93005"]),
                 "  EM-ECG: 93005 tracing only, not billed\n": (one, ["93005"]),
                 "  EM-ECG: 93005 is not billed; 93000 reading documented\n": (both, ["93005"]),
                 "  EM-ECG: 93000 read and reported; 93005 traced here\n": (both, [])}
        for line, (billed, expected) in cases.items():
            with self.subTest(line=line):
                found = em_audit.ecg_findings(worksheet_grammar.em_block(base + line), billed)
                self.assertEqual([f"the worksheet bills {code}, but its EM-ECG line says {code} is not billed"
                                  for code in expected], found)

    def element_field(self) -> str:
        return ('ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\nCPT 99283 Emergency visit\n' + ELEMENTS
                + "  SPECIFICITY: complete - written after the element block\n")

    def test_t2_a_field_after_the_element_block_belongs_to_its_entry(self):
        # Twenty-seventh review: the contract puts an entry's fields before its block, and a field
        # written after it in the same body still pairs with the entry in both readers.
        import specificity_scan
        import worksheet_grammar
        text = self.element_field()
        entries = list(worksheet_grammar.ENTRY.finditer(text))
        detail = list(worksheet_grammar.FIELD.finditer(text))[-1]
        self.assertEqual("99283", worksheet_grammar.paired_entry(text, entries, detail).group("code"))
        flags, orphans = specificity_scan.read_flags_with_orphans(text)
        self.assertEqual((["99283"], 0), ([flag.code for flag in flags if flag.code], orphans))
        private = em_audit.parse_private(text)
        self.assertEqual(0, sum(len(section.unplaced) for section in private.sections))

    def test_t2_the_pairings_of_every_committed_fixture_are_unchanged(self):
        import worksheet_grammar
        worksheets = committed_worksheets()
        self.assertFalse(any(worksheet_grammar.EM_CANDIDATE.match(line)
                             for text in worksheets.values() for line in text.split("\n")))
        paired = sum(worksheet_grammar.paired_entry(text, list(worksheet_grammar.ENTRY.finditer(text)), detail)
                     is not None for text in worksheets.values()
                     for detail in worksheet_grammar.FIELD.finditer(text))
        self.assertEqual(925, paired)  # measured before the twenty-third review's change

    def test_t3_only_a_step_four_heading_ends_the_element_block(self):
        import worksheet_grammar
        lines = ELEMENTS.splitlines(keepends=True)
        reasoning = PRIVATE.format(elements="".join(lines[:4]) + "  ### Reasoning\n" + "".join(lines[4:]))
        elements = worksheet_grammar.worksheet_em_block(reasoning)
        self.assertEqual((1, 0, "99283"), (elements.blocks, elements.outside, elements.block.level))
        self.write_private(reasoning)
        status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("unread remainder 1", output)
        doc = (ROOT / "skills" / "_shared" / "reference" / "em-elements.md").read_text(encoding="utf-8")
        self.assertProseNotIn("A heading, indented or not, ends the block", doc)
        self.assertProseIn("An icd10-cpt step 4 block heading, at the margin or indented, ends the block", doc)

    def test_t4_build_names_the_grammar_defect_it_refuses(self):
        for name, private in (("visible-worksheet-1.md", False), ("worksheets/note-1.md", True)):
            with self.subTest(private=private):
                path = self.run / name
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace("CPT 99283 Emergency visit",
                                                 "CPT 99283 Emergency visit\nCPT 99284 Emergency visit"),
                                encoding="utf-8")
                try:
                    with self.assertRaises(ValueError) as refused:
                        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
                    self.assertIn("worksheet needs exactly one final E/M identity", str(refused.exception))
                    self.assertNotIn("disagree with manifest", str(refused.exception))
                finally:
                    path.write_text(original, encoding="utf-8")


def merged_sheet_repository(root: Path) -> bytes:
    """A throwaway repository: a sheet changed on two branches, merged with a resolution of its own,
    then renamed and changed again; returns the merge's version of the sheet."""
    def git(*args, check=True):
        subprocess.run(["git", "-c", "user.email=synthetic@example.invalid", "-c", "user.name=synthetic",
                        "-c", "commit.gpgsign=false", *args], cwd=root, check=check, capture_output=True)
    body = "".join(f"synthetic sheet line {number}\n" for number in range(20))
    sheet = root / "reference" / "old-sheet.md"
    sheet.parent.mkdir(parents=True)
    git("init", "-q", "-b", "main")
    sheet.write_text(body + "base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "base")
    git("checkout", "-qb", "side")
    sheet.write_text(body + "side\n", encoding="utf-8")
    git("commit", "-qam", "side")
    git("checkout", "-q", "main")
    sheet.write_text(body + "main\n", encoding="utf-8")
    git("commit", "-qam", "main")
    git("merge", "-q", "side", check=False)
    merged = (body + "resolved in the merge\n").encode("utf-8")
    sheet.write_bytes(merged)
    git("add", "-A")
    git("commit", "-qm", "merge")
    git("mv", "reference/old-sheet.md", "reference/new-sheet.md")
    (root / "reference" / "new-sheet.md").write_text(body + "renamed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "rename")
    (root / "reference" / "new-sheet.md").write_text(body + "latest\n", encoding="utf-8")
    git("commit", "-qam", "latest")
    return merged


class TwentyFourthReviewFindings(ProseBind, RunFixture):
    """The twenty-fourth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_w1_a_label_under_a_rejected_diagnosis_stays_the_final_level(self):
        private = ('ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\nICD-10-CM I10 Essential hypertension NOT FOR ENTRY\n'
                   "  E/M: 99283 emergency department visit, low MDM\n")
        visible = ("ICD-10-CM: R05.9 Cough\nICD-10-CM: I10 Essential hypertension NOT FOR ENTRY\n"
                   "  E/M: 99283 emergency department visit, low MDM\n")
        self.assertEqual("99283", review_manifest.selected_codes(private, private=True)["em"])
        self.assertEqual("99283", review_manifest.selected_codes(visible, private=False)["em"])
        rejected = ('ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\nCPT 99285 Emergency visit, high MDM NOT FOR ENTRY\n'
                    "  E/M: 99285 rejected level\nCPT 99283 Emergency visit\n")
        self.assertEqual("99283", review_manifest.selected_codes(rejected, private=True)["em"])

    def test_w2_a_sheet_version_resolved_in_a_merge_before_a_rename_is_found(self):
        import coding_freshness
        repository = self.root / "repository"
        repository.mkdir()
        merged = merged_sheet_repository(repository)
        with mock.patch.object(coding_freshness, "ROOT", repository):
            self.assertEqual(merged, coding_freshness.bound_sheet_version(
                repository / "reference" / "new-sheet.md", coding_freshness.sheet_sha256(merged)))

    def test_w2_a_commit_listed_without_a_path_is_asked_at_both_neighboring_paths(self):
        import coding_freshness
        records = ("c3", "\nreference/new.md", "c2", "c1", "\nreference/old.md")
        self.assertEqual([("c3", ("reference/new.md",)), ("c2", ("reference/new.md", "reference/old.md")),
                          ("c1", ("reference/old.md",))],
                         coding_freshness.history_paths(records, "reference/new.md"))

    def test_w3_a_tool_defect_is_named_as_one_and_not_sent_to_record_repair(self):
        with mock.patch.object(em_audit, "parse_private", side_effect=KeyError("synthetic")):
            status, output = self.in_process()
            finding, report, unread = em_audit_gate(self.run, "shift-synthetic")
        self.assertEqual(2, status, output)
        self.assertIn("tool defect (KeyError)", output)
        self.assertNotIn("missing, invalid, or stale", output)
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("tool defect (KeyError)", report)
        self.assertIn("maintainer", report)
        self.assertNotIn("missing or cannot be read", report)
        (self.run / review_manifest.RECEIPT).unlink()
        status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("missing, invalid or unreadable coding records", output)

    def test_w4_the_region_is_sliced_once_and_the_marks_read_in_place(self):
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        comprehensions = [node for node in ast.walk(functions["parse_private"])
                          if isinstance(node, (ast.DictComp, ast.ListComp, ast.SetComp))]
        self.assertEqual([], [ast.unparse(node) for comprehension in comprehensions
                              for node in ast.walk(comprehension) if isinstance(node, ast.Slice)])
        self.assertEqual([], [ast.unparse(node) for node in ast.walk(functions["filled_marks"])
                              if isinstance(node, ast.Slice) and node.upper is None])
        self.assertEqual((["[SOURCE: filled - data: chest radiograph]"], 1), em_audit.filled_marks(
            "[SOURCE: filled -\n  data: chest radiograph] then [SOURCE: filled - risk: never closed\n\n]"))

    def test_w5_a_direct_gate_call_without_a_manifest_is_incomplete(self):
        (self.run / review_manifest.MANIFEST).unlink()
        finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual((False, 1), (finding, unread), report)
        self.assertIn("the coding records are missing or cannot be read", report)
        source = ast.unparse(next(node for node in ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8")).body
                                  if isinstance(node, ast.FunctionDef) and node.name == "completion_gate"))
        self.assertNotIn("MANIFEST", source)
        self.assertFalse(hasattr(em_audit, "selects_em_level"))

    def test_w6_a_target_outside_output_is_refused_as_outside_output(self):
        checkout = self.fake_checkout()
        with mock.patch.object(repo_root, "main_repo_root", return_value=checkout):
            for target in (checkout / "scratch" / "audit", self.root / "elsewhere" / "audit"):
                with self.subTest(target=target):
                    with self.assertRaises(repo_root.OutsideOutput) as refused:
                        repo_root.ensure_main_checkout(target, under_output=True)
                    self.assertNotIsInstance(refused.exception, repo_root.ForeignCheckout)
                    self.assertNotIn("foreign checkout", str(refused.exception))
                    self.assertIn("output", str(refused.exception))
                    with self.assertRaises(em_audit.WordTargetRefused):
                        em_audit.word_folder(self.run, target)

    def test_w7_an_encounter_file_turned_into_a_folder_is_a_change_after_the_manifest(self):
        encounter = self.run / "encounters" / "encounter-1.txt"
        encounter.unlink()
        encounter.mkdir()
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(self.run)

    def test_w8_one_fingerprint_rule(self):
        import coding_freshness
        import encounter_openers
        self.assertIs(encounter_openers.digest, coding_freshness.sheet_sha256)


class TwentyFifthReviewFindings(ProseBind, RunFixture):
    """The twenty-fifth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_x1_both_invocations_read_the_approval_of_the_run_the_gate_grades(self):
        import completion_checks
        import specificity_scan
        self.write_private(PRIVATE.format(elements=""))
        run = self.run.resolve()

        def moment(source, key):
            # The approval is the run's: a worksheets/ folder carries none of its own.
            return 1_700_000_000.0 if Path(source).resolve() == run else None
        for source in (run / "worksheets", run):
            with self.subTest(source=source.name):
                captured = io.StringIO()
                with mock.patch.object(completion_checks, "approval_moment", side_effect=moment), \
                        contextlib.redirect_stdout(captured):
                    specificity_scan.main([str(source), "--submission", "shift-synthetic"])
                rows = [line for line in captured.getvalue().splitlines() if line.startswith(em_audit.EXPECTED_ROW)]
                self.assertEqual([f"{em_audit.EXPECTED_ROW}: not graded - approval predates the check"], rows)

    def test_x2_a_level_that_is_no_e_m_code_is_a_finding_and_an_unread_descriptor_stays_unread(self):
        import worksheet_grammar
        levels = em_audit.MdmLevels(True, {"99283": "low"}, frozenset(), frozenset({"99210"}))
        for level, finding in (("93000", "EM-LEVEL 93000 is not an E/M code"),
                               ("99210", "EM-LEVEL 99210 is not a CPT 2026 E/M code")):
            with self.subTest(level=level):
                block = worksheet_grammar.em_block(ELEMENTS.replace("EM-LEVEL: 99283", f"EM-LEVEL: {level}"))
                self.assertIn(finding, em_audit.rederivation_findings(block, None, levels))
                self.assertFalse(em_audit.level_unread(block, levels))
                self.assertIn(finding, em_audit.block_findings(block, "99283", None, None, levels=levels))
        block = worksheet_grammar.em_block(ELEMENTS.replace("EM-LEVEL: 99283", "EM-LEVEL: 99284"))
        self.assertTrue(em_audit.level_unread(block, levels))
        self.assertFalse([line for line in em_audit.rederivation_findings(block, None, levels) if "EM-LEVEL" in line])

    def test_x3_a_file_replaced_by_a_folder_is_a_change_whatever_error_the_read_raises(self):
        import pathlib
        encounter = self.run / "encounters" / "encounter-1.txt"
        real = pathlib.Path.read_bytes

        def windows_like(self_path):
            if self_path.is_dir():
                raise PermissionError(13, "Permission denied", str(self_path))
            return real(self_path)
        encounter.unlink()
        encounter.mkdir()
        with mock.patch.object(pathlib.Path, "read_bytes", windows_like):
            with self.assertRaises(review_manifest.StaleRecord):
                review_manifest.validated_population(self.run)
        encounter.rmdir()
        encounter.write_text("Note 1 Example Person\n40 female\n", encoding="utf-8")

        def denied(self_path):
            if self_path.name == "encounter-1.txt":
                raise PermissionError(13, "Permission denied", str(self_path))
            return real(self_path)
        with mock.patch.object(pathlib.Path, "read_bytes", denied):
            with self.assertRaises(PermissionError):
                review_manifest.validated_population(self.run)

    def test_x4_status_evidence_and_a_recorded_file_replaced_by_folders_are_stale(self):
        import encounter_openers
        import encounter_status
        # Twenty-seventh review: both read through the one read-or-classify helper.
        self.assertIs(encounter_openers.read_or_changed, encounter_status.read_or_changed)
        self.assertIs(encounter_openers.read_or_changed, review_manifest.read_or_changed)
        note = self.run / "note-1.md"
        original = note.read_bytes()
        note.unlink()
        note.mkdir()
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(self.run)
        note.rmdir()
        note.write_bytes(original)
        run = FourteenthReviewFindings.office_run(self)
        status = json.loads((run / "encounter-status.json").read_text(encoding="utf-8"))["encounters"]["1"]
        evidence = Path(status["evidence_path"])
        evidence.unlink()
        evidence.mkdir()
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(run)

    def test_x5_a_refused_copy_of_the_level_or_mdm_line_leaves_it_unknown(self):
        import worksheet_grammar
        for line in ("  EM-LEVEL: 9928\n", "  EM-MDM: problems low; data low\n"):
            with self.subTest(line=line):
                block = worksheet_grammar.em_block(ELEMENTS.replace("  EM-LEVEL: 99283\n", "  EM-LEVEL: 99283\n" + line)
                                                   .replace("EM-MDM: problems low; data straightforward; risk low; mdm low",
                                                            "EM-MDM: problems low; data straightforward; risk low; mdm high"))
                self.assertEqual(1, block.unread)
                kind = "LEVEL" if "LEVEL" in line else "MDM"
                self.assertIsNone(block.level if kind == "LEVEL" else block.mdm)
                found = em_audit.block_findings(block, "99284", None, None)
                self.assertFalse([f for f in found if ("level" in f and kind == "LEVEL") or ("MDM line" in f and kind == "MDM")],
                                 found)

    def two_note_run(self):
        validated = review_manifest.validated_population(self.run)
        fingerprints = review_manifest.private_fingerprints(self.run)
        first = validated.encounters[0]
        other_path = str(self.run / "worksheets" / "note-2.md")
        other = review_manifest.ValidatedEncounter(dict(first.item, order=2, id="note-2",
                                                        private_worksheet_path=other_path,
                                                        note_path=str(self.run / "note-2.md")),
                                                   first.note, first.worksheet, first.private)
        wider = review_manifest.ValidatedRun(validated.manifest, validated.receipt, (first, other))
        moved = dict(fingerprints, **{other_path: "0" * 64})
        return (mock.patch.object(review_manifest, "validated_population", return_value=wider),
                mock.patch.object(review_manifest, "private_fingerprints", return_value=moved))

    def test_x6_one_moved_worksheet_refuses_only_its_own_check_off(self):
        population, fingerprints = self.two_note_run()
        with population, fingerprints:
            tally, total, sheets = em_audit.render(self.run, [])
            status, output = self.in_process("--write")
            finding, report, unread = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertEqual(([2], [1], 2), (tally.moved, [sheet_.order for sheet_ in sheets], total))
        self.assertEqual(1, status, output)
        self.assertIn("check-offs written 1", output)
        self.assertIn("the private worksheet of note 2 changed after the manifest", output)
        self.assertTrue(self.sheet.exists())
        self.assertFalse((self.run / em_audit.OUTPUT_DIRECTORY / "note-2.md").exists())
        self.assertTrue(finding, report)
        self.assertIn("private worksheets changed after their fingerprint 1 (note 2)", report)

    def test_x7_a_merge_listed_once_per_parent_is_asked_once(self):
        import coding_freshness
        merge, older = "a" * 40, "b" * 40
        relative, former = "reference/cpt-em-mdm-2026.md", "reference/former-sheet.md"
        requests: list[str] = []
        answers = {commit: f"{commit} missing\n".encode() for commit in (merge, older)}

        def run(command, **_):
            if command[1] == "show":
                return subprocess.CompletedProcess(command, 0, b"head\n", b"")
            # The merge listed with its path for one parent and without one for the other.
            return subprocess.CompletedProcess(command, 0, f"{merge}\0\n{relative}\0{merge}\0"
                                                f"{older}\0\n{former}\0".encode(), b"")
        with mock.patch.object(coding_freshness.subprocess, "run", side_effect=run), \
                mock.patch.object(coding_freshness.subprocess, "Popen", side_effect=lambda *a, **k: FakeBatch(answers, requests)):
            self.assertIsNone(coding_freshness.bound_sheet_version(ROOT / relative, "0" * 64))
        self.assertEqual([f"{merge}:{relative}", f"{merge}:{former}", f"{older}:{former}"], requests)

    def test_x8_one_digest_names_the_word_folder(self):
        source = ast.unparse(next(node for node in ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8")).body
                                  if isinstance(node, ast.FunctionDef) and node.name == "word_folder"))
        self.assertNotIn("hashlib", source)
        self.assertIn("digest(", source)

    def test_x9_answer_levels_are_stored_as_the_set_they_are_compared_as(self):
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            identifier, _ = preapproval_answers.record(self.run, 1, "A synthetic question naming levels?",
                                                       ["99284", "99283", "99284"], REPLY)
        entry = next(entry for entry in preapproval_answers.read(self.run)["answers"] if entry["id"] == identifier)
        self.assertEqual(["99283", "99284"], entry["levels"])


class TwentySixthReviewFindings(ProseBind, RunFixture):
    """The twenty-sixth code-review findings of 2026-11-11, each reproduced red before its fix."""

    def test_y1_the_colon_form_applies_only_where_it_opens_the_clause(self):
        both, one = frozenset({"93000", "93005"}), frozenset({"93005"})
        cases = {"93005 not billed: 93000 is billed for the read": {"93005"},
                 "not billed: 93005": {"93005"},
                 "93005 tracing only, not billed": {"93005"},
                 "93005 billed, 93000 not billed": {"93000"},
                 "93005 billed while the read is pending (93000 not billed)": {"93000"},
                 "93005 is not billed; 93000 reading documented": {"93005"},
                 "93000 read and reported; 93005 traced here": set()}
        for line, expected in cases.items():
            with self.subTest(line=line):
                self.assertEqual(expected, em_audit.negated_codes(line) & both)
        self.assertEqual({"93005"}, em_audit.negated_codes("Tracing not billed: 93005") & one)

    def test_y2_a_tab_in_a_reply_renders_as_a_space_in_word(self):
        reply = "Synthetic reply:\tno, radiology read it."
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            preapproval_answers.record(self.run, 1, "A synthetic question with a tabbed reply?", [], reply)
        folder = self.word_destination()
        status, output = self.in_process("--write", "--docx", "--output-dir", folder)
        self.assertIn("Word copies written 1", output)
        self.assertIn("> " + reply, self.sheet.read_text(encoding="utf-8"))
        import docx_read
        self.assertIn("Synthetic reply: no, radiology read it.", "\n".join(docx_read.read_docx(folder / "note-1.docx")))
        self.assertProseIn("tab", " ".join(row for row in em_audit.DECLARED_LIMITS if "Word" in row))

    def test_y2_another_control_character_is_refused_when_the_answer_is_recorded(self):
        record = self.run / preapproval_answers.RECORD
        before = record.read_bytes()
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=VERIFIED):
            with self.assertRaises(ValueError) as refused:
                preapproval_answers.record(self.run, 1, "A synthetic question\x07 with a bell?", [], REPLY)
        self.assertIn("U+0007", str(refused.exception))
        self.assertIn("line 1", str(refused.exception))
        self.assertEqual(before, record.read_bytes())

    def test_y2_a_word_refusal_names_its_note_and_line(self):
        folder = self.word_destination()
        with mock.patch("docx_write.write_docx", side_effect=OutboundTextError("line 3: U+0085")):
            status, output = self.in_process("--docx", "--output-dir", folder)
        self.assertEqual(2, status, output)
        self.assertIn("Word copy refused at note 1", output)
        self.assertIn("line 3: U+0085", output)

    def test_y3_an_empty_anchor_is_not_an_anchor(self):
        self.write_private(PRIVATE.format(elements=ELEMENTS).replace('  ANCHOR: "Cough."', "  ANCHOR:"))
        status, output = self.in_process("--write")
        self.assertIn("codes without an anchor 1", output)
        self.assertIn("  - Anchor: not recorded", self.sheet.read_text(encoding="utf-8"))

    def test_y4_a_refused_record_is_not_called_stale(self):
        (self.run / review_manifest.RECEIPT).unlink()
        status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertIn("em-audit: refused - missing, invalid or unreadable coding records", output)
        self.assertNotIn("stale", output)

    def test_y5_the_gate_regrades_inside_a_with_block(self):
        import specificity_scan
        gate = next(node for node in ast.parse(Path(specificity_scan.__file__).read_text(encoding="utf-8")).body
                    if isinstance(node, ast.FunctionDef) and node.name == "em_audit_gate")
        self.assertTrue(any(isinstance(node, ast.With) for node in ast.walk(gate)))
        self.assertNotIn("__enter__", ast.unparse(gate))
        self.assertNotIn("UnreadableRecord", ast.unparse(gate))

    def test_y6_history_paths_reads_in_one_pass_each_way(self):
        import coding_freshness
        function = next(node for node in ast.parse(Path(coding_freshness.__file__).read_text(encoding="utf-8")).body
                        if isinstance(node, ast.FunctionDef) and node.name == "history_paths")
        self.assertEqual([], [ast.unparse(node) for node in ast.walk(function) if isinstance(node, ast.Slice)])
        records = ("c5", "c4", "\nreference/new.md", "c3", "c2", "\nreference/old.md", "c1")
        self.assertEqual([("c5", ("reference/new.md",)), ("c4", ("reference/new.md",)),
                          ("c3", ("reference/new.md", "reference/old.md")), ("c2", ("reference/old.md",)),
                          ("c1", ("reference/old.md",))],
                         coding_freshness.history_paths(records, "reference/new.md"))

    def test_y7_one_parse_of_each_private_worksheet_per_render_validation_included(self):
        import worksheet_grammar
        private = (self.run / "worksheets/note-1.md").read_text(encoding="utf-8")
        region = worksheet_grammar.entry_region(private)
        counted = {name: mock.Mock(wraps=getattr(worksheet_grammar, name))
                   for name in ("entry_region", "read_entries", "physical_lines")}
        with contextlib.ExitStack() as stack:
            for name, wrapper in counted.items():
                for module in (worksheet_grammar, review_manifest, em_audit):
                    if hasattr(module, name):
                        stack.enter_context(mock.patch.object(module, name, wrapper))
            em_audit.render(self.run, [])
        self.assertEqual(1, sum(call.args[0] == private for call in counted["entry_region"].call_args_list))
        self.assertEqual(1, sum(call.args[0] == region for call in counted["read_entries"].call_args_list))
        self.assertEqual(1, sum(call.args[0] == private for call in counted["physical_lines"].call_args_list))


class TwentySeventhReviewFindings(ProseBind, RunFixture):
    """The twenty-seventh code-review findings of 2026-11-11, each reproduced red before its fix."""

    FIELDS = ('  ANCHOR: "Cough."\n  SPECIFICITY: complete - the synthetic encounter documents no further axis\n'
              "  CONFIDENCE: verified against CPT 2026\n")

    def ordered(self, fields_first: bool) -> str:
        body = self.FIELDS + ELEMENTS if fields_first else ELEMENTS + self.FIELDS
        return PRIVATE.format(elements="").replace("CPT 99283 Emergency visit\n", "CPT 99283 Emergency visit\n" + body)

    def test_z2_the_entry_fields_pair_before_or_after_its_block(self):
        import specificity_scan
        for fields_first in (True, False):
            with self.subTest(fields_first=fields_first):
                self.write_private(self.ordered(fields_first))
                status, output = self.in_process()
                self.assertIn("unread remainder 0", output)
                self.assertEqual(0, status, output)
                self.assertEqual(0, specificity_scan.main([str(self.run / "worksheets")]))

    def test_z2_a_label_inside_the_e_m_entry_keeps_the_fields_after_the_block_the_entry_s(self):
        text = PRIVATE.format(elements="").replace(
            "CPT 99283 Emergency visit\n",
            "CPT 99283 Emergency visit\n  E/M: 99283 low complexity\n" + ELEMENTS + self.FIELDS)
        self.write_private(text)
        status, output = self.in_process()
        self.assertIn("unread remainder 0", output)
        self.assertEqual(0, status, output)

    def test_z2_a_field_after_the_block_across_a_blank_line_belongs_to_nothing(self):
        import specificity_scan
        text = self.ordered(False).replace(ELEMENTS + "  ANCHOR:", ELEMENTS + "\n  ANCHOR:")
        self.write_private(text)
        status, output = self.in_process()
        self.assertEqual(2, status, output)
        self.assertNotIn("unread remainder 0", output)
        self.assertEqual(1, specificity_scan.read_flags_with_orphans(text)[1])

    def test_z2_the_reference_puts_the_fields_before_the_block(self):
        doc = (ROOT / "skills" / "_shared" / "reference" / "em-elements.md").read_text(encoding="utf-8")
        self.assertProseIn("after the entry's own fields", doc)
        self.assertProseNotIn("A field line written after the block under the same E/M line is unread", doc)
        example = doc.split("Synthetic example", 1)[1].split("```text", 1)[1].split("```", 1)[0]
        lines = example.strip("\n").split("\n")
        self.assertEqual(["ANCHOR", "SPECIFICITY", "CONFIDENCE"],
                         [line.split(":", 1)[0].strip() for line in lines[1:4]])
        step = (ROOT / "skills" / "icd10-cpt" / "SKILL.md").read_text(encoding="utf-8")
        self.assertProseIn("after the line's own ANCHOR, SOURCE, SPECIFICITY and CONFIDENCE fields", step)

    def test_z1_an_e_m_label_ends_the_header_above_it_and_its_own_marker_rejects_it(self):
        entries = 'ICD-10-CM R05.9 Cough\n  ANCHOR: "Cough."\n'
        label = "E/M: 99284 emergency department visit, moderate MDM NOT FOR ENTRY\n"
        cases = {"after the E/M entry": entries + "CPT 99283 Emergency visit\n" + label,
                 "after a diagnosis": "CPT 99283 Emergency visit\n" + entries.replace('  ANCHOR: "Cough."\n', "") + label}
        for name, private in cases.items():
            with self.subTest(case=name):
                codes = review_manifest.selected_codes(private, private=True)
                self.assertEqual(("99283", ["R05.9"]), (codes["em"], codes["icd10"]))

    def test_z4_a_disagreement_is_stale_only_when_the_worksheet_moved_from_its_fingerprint(self):
        private = self.run / "worksheets/note-1.md"
        recorded = review_manifest.private_fingerprints(self.run)
        edited = private.read_text(encoding="utf-8").replace("CPT 99283 Emergency visit", "CPT 99284 Emergency visit")
        private.write_text(edited, encoding="utf-8")
        with self.assertRaises(review_manifest.StaleRecord):
            review_manifest.validated_population(self.run, recorded)
        matching = dict(recorded, **{str(private.resolve()): review_manifest.private_worksheet_sha256(edited)})
        with self.assertRaises(ValueError) as refused:
            review_manifest.validated_population(self.run, matching)
        self.assertNotIsInstance(refused.exception, review_manifest.StaleRecord)

    def test_z5_cleanups(self):
        import encounter_openers
        import encounter_status
        import worksheet_grammar
        tree = ast.parse(Path(em_audit.__file__).read_text(encoding="utf-8"))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("re.compile", ast.unparse(functions["ecg_findings"]))
        self.assertIn("ECG_TOKEN", ast.unparse(functions["ecg_findings"]))
        for module, name in ((encounter_openers, "bound_bytes"), (encounter_status, "status_for"),
                             (review_manifest, "recorded_text")):
            source = ast.unparse(next(node for node in ast.parse(Path(module.__file__).read_text(encoding="utf-8")).body
                                      if isinstance(node, ast.FunctionDef) and node.name == name))
            self.assertIn("read_or_changed", source, name)
            self.assertNotIn("no_longer_a_file", source, name)
        counted = '.count("' + chr(92) + 'n"'
        for module, names in ((worksheet_grammar, ("selected_em",)), (em_audit, ("parse_private", "for_entry_codes"))):
            module_tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            for name in names:
                source = ast.unparse(next(node for node in module_tree.body
                                          if isinstance(node, ast.FunctionDef) and node.name == name))
                self.assertNotIn("count('" + chr(92) + "n', 0", source, name)
        self.assertTrue(counted)
        validated = review_manifest.validated_population(self.run)  # validation's own reads are not counted
        with mock.patch.object(review_manifest, "validated_population", return_value=validated), \
                mock.patch.object(review_manifest, "clean_codes", wraps=review_manifest.clean_codes) as clean, \
                mock.patch.object(em_audit, "level_code_findings", wraps=em_audit.level_code_findings) as levels:
            em_audit.render(self.run, [])
        self.assertEqual(1, clean.call_count)
        self.assertEqual(2, levels.call_count)  # the worksheet block once, the re-derivation once


if __name__ == "__main__":
    unittest.main()
