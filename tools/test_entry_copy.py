"""Public command contract for the note entered in Medatrax."""

# phi-scan: synthetic

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import entry_copy
import medatrax_posting


COMMAND = Path(__file__).with_name("entry_copy.py")
ROOT = Path(__file__).resolve().parents[1]
LABELS = (
    "Non-pharmacologic:\n"
    "Pharmacologic:\n"
    "Health Promotion/Patient Education:\n"
    "Referral/Follow-up:\n"
)
SOAP_REFUSAL = (
    "2. Pain in left elbow - M25.522: 5/10 pain after a fall, elbow radiographs "
    "ordered today to rule out a radial head fracture, no result. NOT CODED: "
    "S52.125A Nondisplaced fracture of head of left radius, initial encounter "
    "for closed fracture, nothing established it. Less likely."
)
SOAP_EXPECTED = (
    "2. Pain in left elbow - M25.522: 5/10 pain after a fall, elbow radiographs "
    "ordered today to rule out a radial head fracture, no result. Less likely."
)


class EntryCopyCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.run = Path(self.temporary.name)
        self.note = self.run / "encounter.md"
        self.copy = self.run / "entry-copies" / "encounter.md"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, content: str) -> subprocess.CompletedProcess[str]:
        self.note.write_text(content, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(COMMAND), str(self.note)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_soap_worked_example_removes_clause_and_keeps_sentence(self) -> None:
        self.assertIn(SOAP_REFUSAL, (ROOT / "skills/clinical-note/SOAP.md").read_text(encoding="utf-8"))
        result = self.invoke("A:\n" + SOAP_REFUSAL + "\nP:\n" + LABELS)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(SOAP_EXPECTED, self.copy.read_text(encoding="utf-8"))
        self.assertNotIn("NOT CODED", self.copy.read_text(encoding="utf-8"))
        self.assertEqual((self.note,), medatrax_posting.note_paths(self.run, batch=False))

    def test_hp_mdm_and_final_diagnosis_remove_all_clauses(self) -> None:
        hp = (ROOT / "skills/clinical-note/HP.md").read_text(encoding="utf-8")
        self.assertIn("NOT CODED: J13 Pneumonia due to Streptococcus pneumoniae, nothing tested for the organism.", hp)
        note = (
            "Medical Decision Making:\n"
            "The film has no result. NOT CODED: J13 Pneumonia due to Streptococcus "
            "pneumoniae, nothing tested for the organism. Treatment proceeds.\n"
            "Final diagnosis: Pneumonia - J18.9; NOT CODED: J13 Pneumonia due to "
            "Streptococcus pneumoniae, organism unconfirmed.\n"
            "Plan\n" + LABELS + "\nDiscussion\nFinished.\n"
        )
        result = self.invoke(note)
        self.assertEqual(0, result.returncode, result.stderr)
        output = self.copy.read_text(encoding="utf-8")
        self.assertIn("The film has no result. Treatment proceeds.", output)
        self.assertIn("Final diagnosis: Pneumonia - J18.9;", output)
        self.assertNotIn("NOT CODED", output)

    def test_skill_worked_examples_keep_surrounding_prose(self) -> None:
        skill = (ROOT / "skills/clinical-note/SKILL.md").read_text(encoding="utf-8")
        chest = next(line for line in skill.splitlines() if line.startswith("3. Chest pain, unspecified - R07.9:"))
        conclusion = (
            "Final diagnosis: Community-acquired pneumonia, pneumococcal organism suspected - J18.9\n"
            "Pneumonia, unspecified organism. Nothing tested for the organism, so NOT CODED: "
            "J13 Pneumonia due to Streptococcus pneumoniae; an organism-specific result would earn it."
        )
        self.assertIn(conclusion, skill)
        result = self.invoke(chest + "\n" + conclusion + "\nP:\n" + LABELS)
        self.assertEqual(0, result.returncode, result.stderr)
        output = self.copy.read_text(encoding="utf-8")
        self.assertIn("CT angiography pending. Less likely.", output)
        self.assertIn("so an organism-specific result would earn it.", output)
        self.assertNotIn("NOT CODED", output)

    def test_period_inside_refusal_does_not_leave_descriptor_or_reason(self) -> None:
        result = self.invoke(
            "A:\nFinding. NOT CODED: A04.72 Enterocolitis due to Clostridium difficile, "
            "no C. difficile assay was done by Dr. Smith. Less likely.\n"
            "P:\n" + LABELS
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Finding. Less likely.", self.copy.read_text(encoding="utf-8"))
        self.assertNotIn("difficile assay", self.copy.read_text(encoding="utf-8"))

    def test_terminal_single_letter_does_not_remove_following_sentence(self) -> None:
        result = self.invoke(
            "A:\nFinding. NOT CODED: J02.0 Streptococcal pharyngitis, "
            "no throat culture for group A. Less likely.\nP:\n" + LABELS
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Finding. Less likely.", self.copy.read_text(encoding="utf-8"))

    def test_surviving_mark_refuses_and_removes_stale_copy(self) -> None:
        self.copy.parent.mkdir()
        self.copy.write_text("stale", encoding="utf-8")
        result = self.invoke("P:\n" + LABELS + "\nNOT CODED was typed bare.\n")
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.copy.exists())

    def test_planted_unbounded_clause_refuses(self) -> None:
        result = self.invoke("A:\nNOT CODED: J13 Pneumonia due to Streptococcus pneumoniae, reason unfinished\nP:\n" + LABELS + "Return in a week.\n")
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.copy.exists())

    def test_missing_or_extra_plan_label_refuses(self) -> None:
        for labels in (
            LABELS.replace("Referral/Follow-up:\n", ""),
            LABELS + "Diagnostics:\n",
            LABELS + "Screening offered and reviewed:\n",
            LABELS + "Intervention:\n",
        ):
            with self.subTest(labels=labels):
                result = self.invoke("P:\n" + labels + "\nCoding worksheet\n")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(self.copy.exists())

    def test_sentence_and_sig_fields_pass(self) -> None:
        result = self.invoke(
            "P:\n" + LABELS + "If the urine culture grows a pathogen: call.\n"
            "Sig: daily\nDispense: 10\nRefills: 0\nCoding worksheet\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)


class CommittedNotePlans(unittest.TestCase):
    def test_preserved_fixture_notes_are_named_refusals(self) -> None:
        fixtures = Path(__file__).resolve().parents[1] / "fixtures"
        expected = set(
            """blind-run/duration-span-case-01.md
blind-run/duration-span-case-02.md
blind-run/duration-span-case-03.md
blind-run/obesity-bmi-case-01.md
blind-run/obesity-bmi-case-02.md
blind-run/obesity-bmi-case-03.md
blind-run/obesity-bmi-case-04.md
slot-form-run/day-a-case-06.md
slot-form-run/day-b-case-02.md
slot-form-run/day-b-case-07.md
slot-form-run/day-b-case-11.md
slot-form-run/hedged-dx-case-03.md
slot-form-run/peds-bp-case-05.md
filled-anchor/notes/case-01.md
filled-anchor/notes/case-02.md
filled-anchor/notes/case-03.md
filled-anchor/notes/case-04.md
filled-anchor/notes/case-05.md
filled-anchor/notes/case-06.md
filled-anchor/notes/case-07.md
filled-anchor/notes/case-08.md
filled-anchor/notes/case-09.md
filled-anchor/notes/case-10.md
filled-anchor/notes/case-11.md
filled-anchor/notes/case-12.md
descriptor-agreement-positive-control/notes/case-01.md
descriptor-agreement-note-path-control/notes/case-01.md
descriptor-agreement-negative-control/notes/case-01.md""".splitlines()
        )
        notes = {
            path.relative_to(fixtures).as_posix(): path
            for path in fixtures.rglob("*.md")
            if any(
                entry_copy._plain(line) in {"P:", "Plan", "Plan:"}
                for line in path.read_text(encoding="utf-8").splitlines()
            )
        }
        self.assertEqual(expected, set(notes))
        for name, path in notes.items():
            with self.subTest(note=name):
                with self.assertRaisesRegex(ValueError, "Plan labels invalid"):
                    entry_copy.derive(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
