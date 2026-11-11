"""Synthetic public-command checks for the E/M audit check-off renderer."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support

import contextlib
import io
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import approval_record
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


class CheckOffCommand(unittest.TestCase):
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
                     "re-derivations: agree 0; differ 0; damaged 0; absent 1",
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
                         "- Question note-1.q1: " + QUESTION, "  - Levels named: none named",
                         "  - Reply: \"" + REPLY + "\"", "verified as a whole clinician message",
                         "- Setting: emergency department", "No re-derivation record is placed for this note.",
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
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace(
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
        (self.run / "worksheets/note-1.md").write_text(PRIVATE.format(elements=ELEMENTS.replace(
            "note-1.q1", "note-1.q2")), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("answer note-1.q2 is not in the pre-approval answers record", self.sheet.read_text(encoding="utf-8"))

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
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("element blocks: present 0, absent 1; findings 0", result.stdout)

    def test_written_check_off_renders_every_recorded_decision_in_template_order(self):
        self.assertEqual(0, self.invoke("--write").returncode)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        for expected in ("The private worksheet has no element block", "The visible Coding worksheet, as approved:",
                         "> E/M: 99283, low complexity, synthetic support", "> " + NOTE_EM.strip()):
            self.assertIn(expected, text)

    def test_a_matching_re_derivation_agrees_and_each_differing_element_is_listed(self):
        self.record(ELEMENTS)
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("level only, because the worksheet has no element block", self.sheet.read_text(encoding="utf-8"))

    def test_a_block_that_contradicts_itself_is_a_finding(self):
        pass

    def test_entry_ids_are_checked_against_the_named_sheet(self):
        pass

    def test_an_answer_id_the_record_lacks_is_a_finding(self):
        pass

    def test_the_answers_record_absent_or_malformed_is_said_on_the_check_off(self):
        (self.run / preapproval_answers.RECORD).unlink()
        self.assertEqual(0, self.invoke("--write").returncode)
        self.assertIn("No pre-approval answers record exists for this run.", self.sheet.read_text(encoding="utf-8"))

    def test_completion_requires_a_re_derivation_and_a_current_check_off(self):
        self.record(ELEMENTS)
        self.assertEqual(0, self.invoke("--write").returncode)
        finding, report, _ = em_audit.completion_gate(self.run, "shift-synthetic")
        self.assertTrue(finding)
        self.assertIn("element blocks absent 1", report)


if __name__ == "__main__":
    unittest.main()
