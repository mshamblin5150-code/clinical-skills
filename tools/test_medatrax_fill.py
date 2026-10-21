"""Synthetic public-command checks for the approved encounter fill builder."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support
import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

import approval_record
import encounter_openers
import medatrax_fill
import review_manifest
from test_review_manifest import synthetic_run, passing_receipt


VALUES = {
    "Visit Date": "2026-10-01", "Course": "Synthetic course", "Site": "Synthetic site",
    "Preceptor": "Example,Teacher", "Interaction Level": "Level 2",
    "Race/Ethnicity": "Other", "Gender": "Female", "Age": "40", "Age unit": "Years",
    "Marital status at first contact": "Single", "Primary Payment Method": "none",
    "Case Type": "Respiratory", "Patient Time": "Adult (18 – 60) Hours",
    "Start time": "0800", "End time": "0830", "Blood pressure systolic": "120",
    "Blood pressure diastolic": "80", "Respiratory Rate": "16", "Height": "65", "BMI": "24",
}


class FillCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run = synthetic_run(self.root)
        self.profile = self.root / "profile.md"
        self.profile.write_text("# Profile\n## Course\n- `Synthetic course`\n## Picklists\n### Site\n- `Synthetic site`\n### Preceptor\n- `Example,Teacher`\n## Interaction Level\nLevel 5\n", encoding="utf-8")
        (self.run / "shift-values.json").write_text(json.dumps(dict(start="0800", duration=dict(hours=8, minutes=0))), encoding="utf-8")
        self.values = dict(VALUES)
        self.approve()

    def approve(self, *, batch=True):
        note = self.run / "note-1.md"
        clinical = note.read_text(encoding="utf-8").split("## Medatrax")[0]
        note.write_text(clinical + "## Medatrax entry fields\n| Field | Value |\n| --- | --- |\n" + "".join(f"| {key} | {value} |\n" for key, value in self.values.items()), encoding="utf-8")
        review_manifest.build(self.run, self.run / "inputs.json", batch=batch,
                              constants=dict(course="Synthetic course", site="Synthetic site", preceptor="Example,Teacher"))
        passing_receipt(self.run, batch=batch)
        binding = review_manifest.approval_binding(self.run, batch=batch)
        # Synthetic retained approval, not a claim that a clinician approved this fixture.
        item = dict(skill="batch-shift" if batch else "clinical-note", submission="synthetic",
                    sha256=approval_record.source_sha256(binding.sources), sources=list(map(str, binding.sources)),
                    note_sources=list(map(str, binding.notes)), clinical_manifest_binding=True,
                    grader_args=[str(self.run)], pregrade_status="clean", posting_route="awaiting-posting",
                    approval_revision=1, clinician_reply="Synthetic approval", approval_kind="content")
        (self.run / approval_record.RECORD).write_text(json.dumps(dict(version=1, approval_revision=1, items=[item])), encoding="utf-8")

    def invoke(self, *extra, batch=True):
        return subprocess.run([sys.executable, str(Path(__file__).with_name("medatrax_fill.py")),
            "--run", str(self.run), "--submission", "synthetic", "--profile", str(self.profile),
            *( ["--batch"] if batch else ["--notes", str(self.run / "note-1.md")] ), *extra],
            capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_clean_batch_keeps_nondefault_level_and_writes_ordered_list_and_script(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        record = json.loads((self.run / "medatrax-fill/fill-fields.json").read_text(encoding="utf-8"))
        fields = record["encounters"][0]["fields"]
        self.assertEqual(list(VALUES), [field["field"] for field in fields])
        self.assertEqual(list(VALUES.values()), [field["value"] for field in fields])
        self.assertTrue((self.run / "medatrax-fill/fill-note-1.js").exists())

    def test_field_edit_and_rebuilt_unapproved_manifest_both_refuse(self):
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace("Level 2", "Level 3"), encoding="utf-8")
        self.assertEqual(2, self.invoke().returncode)
        review_manifest.build(self.run, self.run / "inputs.json", batch=True,
                              constants=dict(course="Synthetic course", site="Synthetic site", preceptor="Example,Teacher"))
        passing_receipt(self.run)
        result = self.invoke()
        self.assertEqual(2, result.returncode)
        self.assertIn("recorded approval", result.stdout)
        self.assertFalse((self.run / "medatrax-fill").exists())

    def test_field_change_between_approval_validation_and_exact_fill_read_refuses(self):
        note = self.run / "note-1.md"
        changed = note.read_text(encoding="utf-8").replace("Level 2", "Level 3")
        original_open = Path.open
        note_reads = 0
        def source_open(path, *args, **kwargs):
            nonlocal note_reads
            if path == note and (not args or args[0] == "r"):
                note_reads += 1
                if note_reads == 2:
                    with original_open(path, "w", encoding="utf-8") as stream:
                        stream.write(changed)
            return original_open(path, *args, **kwargs)
        output = io.StringIO()
        with patch.object(Path, "open", source_open), redirect_stdout(output):
            status = medatrax_fill.main(["--run", str(self.run), "--submission", "synthetic",
                "--profile", str(self.profile), "--batch"])
        self.assertEqual(2, status, output.getvalue())
        self.assertIn("field fingerprint", output.getvalue())
        self.assertFalse((self.run / "medatrax-fill").exists())

    def test_exact_source_checks_refuse_without_output(self):
        for field, wrong in (("Age", "41"), ("Gender", "Male"), ("Start time", "08:00"),
                ("End time", "0700"), ("Interaction Level", "Level 6"), ("Preceptor", "Example, Teacher"),
                ("Site", "Other site"), ("Course", "Other course"), ("Case Type", "respiratory"),
                ("Visit Date", "2099-12-31"), ("Height", "65\x7f")):
            with self.subTest(field=field):
                self.values = {**VALUES, field: wrong}
                self.approve()
                result = self.invoke()
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertFalse((self.run / "medatrax-fill").exists())

    def test_clean_single_uses_its_approved_note_population(self):
        self.approve(batch=False)
        self.assertEqual(0, self.invoke(batch=False).returncode)
        other = self.root / "other.md"
        other.write_text("not approved", encoding="utf-8")
        result = self.invoke("--notes", str(other), batch=False)
        self.assertEqual(2, result.returncode)

    def test_profile_table_header_and_explanatory_prose_are_not_choices(self):
        self.profile.write_text("## Courses\n| Course | Dates |\n| --- | --- |\n| Synthetic course | private term |\n## Site\n- Synthetic site\n## Preceptor\n- Example,Teacher\nA prose explanation is not a picklist value.\n", encoding="utf-8")
        for field, value in (("Course", "Dates"), ("Preceptor", "A prose explanation is not a picklist value.")):
            self.values = {**VALUES, field: value}
            self.approve()
            self.assertEqual(2, self.invoke().returncode)

    def test_given_us_date_is_compared_without_rewriting_and_bare_age_does_not_infer_unit(self):
        self.values = {**VALUES, "Visit Date": "10/01/2026", "Age unit": "Months"}
        self.approve()
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        record = json.loads((self.run / "medatrax-fill/fill-fields.json").read_text(encoding="utf-8"))
        values = {row["field"]: row["value"] for row in record["encounters"][0]["fields"]}
        self.assertEqual("10/01/2026", values["Visit Date"])
        self.assertEqual("Months", values["Age unit"])

    def test_handwritten_content_damage_is_a_finding_not_unread_machine_evidence(self):
        self.profile.write_bytes(self.profile.read_bytes() + b"\x01")
        result = self.invoke()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("unread remainder", result.stdout)
        self.assertNotIn("Synthetic site", result.stdout)

    def test_damaged_records_are_preserved_and_refuse(self):
        for relative in (approval_record.RECORD, review_manifest.MANIFEST, review_manifest.RECEIPT,
                         "openers.json", "medatrax-fill/fill-fields.json"):
            with self.subTest(record=relative):
                target = self.run / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                prior = target.read_bytes() if target.exists() else None
                target.write_bytes(b'{"broken":')
                result = self.invoke()
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertIn("unread remainder 1", result.stdout)
                self.assertEqual(b'{"broken":', target.read_bytes())
                if prior is None:
                    target.unlink()
                else:
                    target.write_bytes(prior)

    def test_missing_or_duplicate_field_and_unread_shift_refuse(self):
        note = self.run / "note-1.md"
        for body in ("| Age | 40 |\n", "| Age | 40 |\n| Age | 40 |\n"):
            self.approve()
            text = note.read_text(encoding="utf-8")
            note.write_text(text[:text.index("| Field |")] + body, encoding="utf-8")
            # Reapprove this synthetic field population so the field parser is reached.
            review_manifest.build(self.run, self.run / "inputs.json", batch=True,
                constants=dict(course="Synthetic course", site="Synthetic site", preceptor="Example,Teacher"))
            passing_receipt(self.run)
            approval = json.loads((self.run / approval_record.RECORD).read_text())
            approval["items"][0]["sha256"] = approval_record.source_sha256(review_manifest.approval_binding(self.run, batch=True).sources)
            (self.run / approval_record.RECORD).write_text(json.dumps(approval))
            self.assertEqual(2, self.invoke().returncode)
        self.approve()
        (self.run / "shift-values.json").unlink()
        self.assertEqual(2, self.invoke().returncode)

    def test_two_encounters_use_shared_order_spacing_and_midnight_window(self):
        other = self.root / "two"
        other.mkdir()
        source = other / "source.txt"
        source.write_text("Note 1 Example Person\n40 female\nNote 2 Example Person\n40 female\n", encoding="utf-8")
        readings = other / "readings.json"
        readings.write_text(json.dumps([dict(note=n, name="Example Person", age="40", sex="female") for n in (1, 2)]), encoding="utf-8")
        run = other / "run"
        encounter_openers.create(run, source, readings, "2026-10-01", "split", None)
        (run / "worksheets").mkdir()
        rows = []
        for n, times in ((1, ("2330", "0000")), (2, ("0005", "0035"))):
            values = {**VALUES, "Start time": times[0], "End time": times[1]}
            (run / f"note-{n}.md").write_text("# Encounter\nCough.\n## Medatrax entry fields\n" + "".join(f"{key}: {value}\n" for key, value in values.items()), encoding="utf-8")
            for path in (run / f"visible-{n}.md", run / f"worksheets/note-{n}.md"):
                path.write_text("ICD-10-CM R05.9 Cough\nCPT 99283 Emergency visit\n", encoding="utf-8")
            rows.append(dict(note=f"note-{n}.md", worksheet=f"visible-{n}.md", setting="emergency-department",
                codes=dict(icd10=["R05.9"], em="99283", cpt=[], hcpcs=[])))
        inputs = run / "inputs.json"
        inputs.write_text(json.dumps(rows), encoding="utf-8")
        (run / "shift-values.json").write_text(json.dumps(dict(start="2300", duration=dict(hours=3, minutes=0))))
        self.run = run
        def retain_approval():
            review_manifest.build(run, inputs, batch=True, constants=dict(course="Synthetic course", site="Synthetic site", preceptor="Example,Teacher"))
            passing_receipt(run)
            binding = review_manifest.approval_binding(run, batch=True)
            item = dict(skill="batch-shift", submission="synthetic", clinical_manifest_binding=True,
                note_sources=list(map(str, binding.notes)), sources=list(map(str, binding.sources)),
                sha256=approval_record.source_sha256(binding.sources), grader_args=[str(run)],
                pregrade_status="clean", posting_route="awaiting-posting", approval_revision=1)
            (run / approval_record.RECORD).write_text(json.dumps(dict(version=1, approval_revision=1, items=[item])))
        retain_approval()
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        second = run / "note-2.md"
        second.write_text(second.read_text(encoding="utf-8").replace("Start time: 0005", "Start time: 0000"), encoding="utf-8")
        retain_approval()
        result = self.invoke()
        self.assertEqual(2, result.returncode)
        self.assertIn("spacing", result.stdout)

    @unittest.skipUnless(shutil.which("node"), "Node required for synthetic script execution")
    def test_generated_script_executes_and_preflights_all_targets(self):
        self.assertEqual(0, self.invoke().returncode)
        script = self.run / "medatrax-fill/fill-note-1.js"
        harness = self.root / "synthetic-dom.cjs"
        harness.write_text(r'''
const fs = require('fs');
class Input { constructor() { this._value = ''; this.tagName = 'INPUT'; this.events = []; } get value(){return this._value;} set value(v){this._value=v;} dispatchEvent(e){this.events.push(e.type);} }
class Select extends Input { constructor(value) { super(); this.tagName = 'SELECT'; this.options = [{textContent: value, value: 'opaque:' + value}]; } get value(){return this._value;} set value(v){this._value=v;} }
global.HTMLInputElement = Input; global.HTMLSelectElement = Select;
global.Event = class {constructor(type){this.type=type;}};
const expected = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const record = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const kinds = new Map(record.encounters[0].fields.map(field => [field.field, field.kind]));
const controls = Object.entries(expected).map(([field, value]) => ({textContent: field, control: kinds.get(field) === 'select' ? new Select(value) : new Input()}));
if (process.argv[5] === 'missing') controls.pop();
global.document = {querySelectorAll: () => controls};
try { eval(fs.readFileSync(process.argv[2], 'utf8')); } catch (error) {
  if (process.argv[5] !== 'missing' || controls.some(label => label.control.value !== '')) throw error;
  process.exit(0);
}
if (process.argv[5] === 'missing') throw Error('Missing target was accepted');
for (const label of controls) {
  const wanted = kinds.get(label.textContent) === 'select' ? 'opaque:' + expected[label.textContent] : expected[label.textContent];
  if (label.control.value !== wanted || label.control.events.join(',') !== 'input,change') throw Error('Incorrect synthetic assignment');
}
''', encoding="utf-8")
        expected = self.root / "expected.json"
        expected.write_text(json.dumps(VALUES), encoding="utf-8")
        for mode in ("clean", "missing"):
            result = subprocess.run(["node", str(harness), str(script), str(expected),
                str(self.run / "medatrax-fill/fill-fields.json"), mode], capture_output=True, text=True,
                encoding="utf-8", errors="replace")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
