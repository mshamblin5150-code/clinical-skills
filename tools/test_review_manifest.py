"""Synthetic public-command checks for ADR 0427 build 2."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import encounter_openers
import encounter_status
import review_manifest
from prose_bind import bind, NAMING
from run_record_reader import UnreadableRecord


def synthetic_run(root: Path, *, batch: bool = True, setting="emergency-department") -> Path:
    """Create a minimal synthetic run and build its manifest (no real currency claim)."""
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    run = root / "run"
    source = root / "source.txt"
    source.write_text("Note 1 Example Person\n40 female\n", encoding="utf-8")
    readings = root / "readings.json"
    readings.write_text(json.dumps([dict(note=1, name="Example Person", age="40", sex="female")]), encoding="utf-8")
    encounter_openers.create(run, source, readings, "2026-10-01", "split" if batch else "single", None)
    (run / "note-1.md").write_text("# Encounter\n\n## Subjective\nCough.\n\n## Objective\nAlert.\n\n## Assessment\nCough.\n\n## Plan\nEducation: Rest.\n\n## Medatrax entry fields\n| Field | Value |\n| --- | --- |\n| Gender | Female |\n\n## Tier block\nPrivate working text.\n", encoding="utf-8")
    (run / "visible-worksheet-1.md").write_text("ICD-10-CM R05.9 Cough\nCPT 99283 Emergency visit\n", encoding="utf-8")
    (run / "worksheets").mkdir()
    (run / "worksheets/note-1.md").write_text("ICD-10-CM R05.9 Cough\n  ANCHOR: Cough.\nCPT 99283 Emergency visit\n  ANCHOR: Cough.\n", encoding="utf-8")
    codes = dict(icd10=["R05.9"], em="99283" if setting == "emergency-department" else "99213", cpt=[], hcpcs=[])
    inputs = run / "inputs.json"
    inputs.write_text(json.dumps([dict(note="note-1.md", worksheet="visible-worksheet-1.md", setting=setting, codes=codes)]), encoding="utf-8")
    if setting == "office":
        for path in (run / "visible-worksheet-1.md", run / "worksheets/note-1.md"):
            path.write_text(path.read_text().replace("99283", "99213"), encoding="utf-8")
    return run


def passing_receipt(run: Path, *, batch: bool = True) -> None:
    """Synthetic receipt fixture only: never assert live freshness from this helper."""
    manifest = review_manifest.manifest_for(run, batch=batch)
    findings = []
    population = review_manifest.coding_freshness.read_encounters(manifest, findings)
    assert not findings
    sources = {
        "icd10": {"release": "synthetic-release", "database_sha256": "a" * 64,
                  "authoritative_url": "https://example.test/icd"},
        "cpt": {"source_id": "synthetic-cpt", "edition": "synthetic-edition", "source_sha256": "b" * 64,
                "database_sha256": "c" * 64, "valid_through": "2026-12-31",
                "mdm_sheet_filename": "synthetic-mdm.md", "mdm_sheet_sha256": "d" * 64},
        "hcpcs": {"source_id": "synthetic-hcpcs", "edition": "synthetic-edition", "source_sha256": "e" * 64,
                  "database_sha256": "f" * 64, "authoritative_url": "https://example.test/hcpcs"}}
    (run / review_manifest.RECEIPT).write_text(json.dumps(dict(schema=1, verdict="PASS", service_date=manifest["service_date"], checked_as_of="2026-10-21", encounters=population, sources=sources)), encoding="utf-8")


class ManifestCommands(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.run = synthetic_run(self.root)

    def test_declared_limits_are_named_in_shared_contract(self):
        contract = (Path(__file__).resolve().parent.parent / "skills/_shared/reference/clinical-manifest.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(encounter_status.DECLARED_LIMITS, contract, mode=NAMING))
        self.assertEqual((), bind(review_manifest.DECLARED_LIMITS, contract, mode=NAMING))

    def invoke(self, command, *args):
        return subprocess.run([sys.executable, str(Path(__file__).with_name(command)), *map(str, args)], capture_output=True, text=True, encoding="utf-8", errors="replace")

    def build(self, *extra):
        return self.invoke("review_manifest.py", "build", self.run, "--inputs", self.run / "inputs.json",
                           "--course", "Synthetic course", "--preceptor", "Synthetic preceptor",
                           "--site", "Synthetic site", *extra)

    def test_clean_batch_and_standalone_build_public_commands(self):
        result = self.build()
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        passing_receipt(self.run)
        binding = review_manifest.approval_binding(self.run, batch=True)
        self.assertEqual((self.run / "note-1.md",), binding.notes)
        self.assertEqual(5, len(binding.source_times))
        other = synthetic_run(self.root / "single", batch=False)
        result = self.invoke("review_manifest.py", "build", other, "--inputs", other / "inputs.json", "--single")
        self.assertEqual(0, result.returncode, result.stderr)
        with self.assertRaises(ValueError):
            review_manifest.approval_binding(other, batch=True)

    def test_native_short_alias_fixture_returns_canonical_record_paths(self):
        from tree_walk_test_support import short_alias
        target = self.root / "Long clinical fixture directory"
        target.mkdir()
        alias = short_alias(target)
        run = synthetic_run(alias, batch=False)
        self.assertEqual(target.resolve() / "run", run)
        review_manifest.build(run, run / "inputs.json", batch=False)
        passing_receipt(run, batch=False)
        binding = review_manifest.approval_binding(alias / "run", batch=False)
        self.assertEqual((run / "note-1.md",), binding.notes)
        self.assertEqual((run / review_manifest.MANIFEST, run / review_manifest.RECEIPT), binding.sources)

    def test_office_refuses_missing_status_and_status_command_fingerprints_evidence(self):
        inputs = self.run / "inputs.json"
        rows = json.loads(inputs.read_text())
        rows[0]["setting"] = "office"; rows[0]["codes"]["em"] = "99213"
        inputs.write_text(json.dumps(rows))
        for path in (self.run / "visible-worksheet-1.md", self.run / "worksheets/note-1.md"):
            path.write_text(path.read_text().replace("99283", "99213"), encoding="utf-8")
        self.assertEqual(2, self.build().returncode)
        evidence = self.root / "evidence.md"
        evidence.write_text("Selected row: established patient.", encoding="utf-8")
        result = self.invoke("encounter_status.py", self.run, "--note", 1, "--value", "established", "--evidence", "identity-map", "--evidence-path", evidence, "--pointer", "Selected row")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(encounter_openers.digest(evidence.read_bytes()), encounter_status.status_for(self.run, 1)["evidence_sha256"])
        self.assertEqual(0, self.build().returncode)
        evidence.write_text("Changed evidence", encoding="utf-8")
        self.assertEqual(2, self.build().returncode)

    def test_receipt_missing_stale_and_current_sources_checked(self):
        self.assertEqual(0, self.build().returncode)
        self.assertEqual(2, self.invoke("review_manifest.py", "render", self.run, "--output", self.root / "review.docx").returncode)
        passing_receipt(self.run)
        review_manifest.approval_binding(self.run, batch=True)
        worksheet = self.run / "visible-worksheet-1.md"
        worksheet.write_text(worksheet.read_text().replace("R05.9", "I10"))
        with self.assertRaisesRegex(ValueError, "stale|disagree"):
            review_manifest.approval_binding(self.run, batch=True)
        self.assertEqual(2, self.build().returncode)
        rows = json.loads((self.run / "inputs.json").read_text())
        rows[0]["codes"]["icd10"] = ["I10"]
        (self.run / "inputs.json").write_text(json.dumps(rows))
        private = self.run / "worksheets/note-1.md"
        private.write_text(private.read_text().replace("R05.9", "I10"))
        self.assertEqual(0, self.build().returncode)
        with self.assertRaisesRegex(ValueError, "stale"):
            review_manifest.approval_binding(self.run, batch=True)

    def test_private_selected_code_mutation_refuses_without_visible_change(self):
        self.assertEqual(0, self.build().returncode)
        passing_receipt(self.run)
        binding = review_manifest.approval_binding(self.run, batch=True)
        private = self.run / "worksheets/note-1.md"
        self.assertIn(private, binding.worksheets)
        self.assertIn(private, binding.source_times)
        # Provenance is not part of the clinical/code identity projection.
        private.write_text(private.read_text().replace("ANCHOR: Cough.", "ANCHOR: Changed provenance."))
        review_manifest.approval_binding(self.run, batch=True)
        private.write_text(private.read_text().replace("R05.9", "I10"))
        with self.assertRaisesRegex(ValueError, "private worksheet selected codes"):
            review_manifest.approval_binding(self.run, batch=True)
        self.assertEqual(2, self.build().returncode)

    def test_selected_code_adapter_uses_visible_labels_and_excludes_private_differentials(self):
        visible = self.run / "visible-worksheet-1.md"
        visible.write_text("ICD-10-CM: R05.9 - Cough\nE/M: 99283 - Emergency visit\nProblems: Low\nData: Minimal\nRisk: Low\nMDM: Low\nCPT: None\nHCPCS: None\n", encoding="utf-8")
        private = self.run / "worksheets/note-1.md"
        private.write_text(private.read_text() + "\n--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\nICD-10-CM I10 Hypertension NOT FOR ENTRY\n  ANCHOR: Differential.\n", encoding="utf-8")
        self.assertEqual(0, self.build().returncode)
        passing_receipt(self.run)
        review_manifest.approval_binding(self.run, batch=True)
        visible.write_text(visible.read_text().replace("R05.9", "I10"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "visible worksheet selected codes"):
            review_manifest.approval_binding(self.run, batch=True)

    def test_field_edits_bind_separately_and_trailing_spaces_do_not(self):
        self.assertEqual(0, self.build().returncode)
        passing_receipt(self.run)
        manifest_path = self.run / review_manifest.MANIFEST
        original = manifest_path.read_bytes()
        note = self.run / "note-1.md"
        note.write_text(note.read_text().replace("Cough.", "Cough.  "))
        review_manifest.approval_binding(self.run, batch=True)
        self.assertEqual(0, self.build().returncode)
        self.assertEqual(original, manifest_path.read_bytes())
        note.write_text(note.read_text().replace("Female", "Male"))
        with self.assertRaisesRegex(ValueError, "stale"):
            review_manifest.approval_binding(self.run, batch=True)
        self.assertEqual(0, self.build().returncode)
        current = json.loads(manifest_path.read_text())
        before = json.loads(original)
        self.assertEqual(before["encounters"][0]["normalized_sha256"], current["encounters"][0]["normalized_sha256"])
        self.assertNotEqual(before["encounters"][0]["field_block_sha256"], current["encounters"][0]["field_block_sha256"])

    def test_damaged_records_are_preserved_by_public_writers(self):
        target = self.run / review_manifest.MANIFEST
        target.write_bytes(b'{"broken":')
        result = self.build()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual(b'{"broken":', target.read_bytes())
        self.assertNotIn("Traceback", result.stderr)

    def test_render_calls_plain_writer_with_same_visible_content(self):
        self.assertEqual(0, self.build().returncode)
        passing_receipt(self.run)
        import docx_write
        with patch.object(docx_write, "write_docx", return_value=self.root / "review.docx") as writer:
            review_manifest.render(self.run, self.root / "review.docx")
        args, kwargs = writer.call_args
        self.assertEqual("plain", kwargs["layout"])
        self.assertNotIn("Private working text", args[0])
        self.assertNotIn("Gender", args[0])
        self.assertNotIn("Example Person", args[0])
        self.assertEqual(1, args[0].count("**Course:** Synthetic course"))
        self.assertEqual(1, args[0].count("**Preceptor:** Synthetic preceptor"))
        self.assertEqual(1, args[0].count("**Site:** Synthetic site"))
        self.assertEqual(1, args[0].count("**Date:**"))
        self.assertIn("**Coding freshness:** PASS", args[0])

    def test_public_render_writes_docx_and_layout_rerender_preserves_binding(self):
        self.assertEqual(0, self.build().returncode)
        passing_receipt(self.run)
        output = self.root / "review.docx"
        binding = review_manifest.approval_binding(self.run, batch=True)
        before = tuple(path.read_bytes() for path in binding.sources)
        result = self.invoke("review_manifest.py", "render", self.run, "--output", output)
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        with zipfile.ZipFile(output) as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("Cough.", xml)
        self.assertNotIn("Private working text", xml)
        self.assertNotIn("Gender", xml)
        result = self.invoke("review_manifest.py", "render", self.run, "--output", output, "--force")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(before, tuple(path.read_bytes() for path in binding.sources))

    def test_plain_markers_embedded_worksheet_and_fenced_tiers(self):
        note = self.run / "note-1.md"
        original = note.read_text()
        note.write_text(original.replace("## Medatrax entry fields", "Medatrax entry fields").replace("## Tier block\nPrivate working text.", "```\nDERIVED hidden arithmetic\nFILLED hidden history\n```"))
        self.assertEqual(0, self.build().returncode)
        manifest = review_manifest.manifest_for(self.run, batch=True)
        text, _, _, _ = review_manifest.content(self.run, manifest["encounters"][0])
        self.assertNotIn("hidden", text)
        self.assertNotIn("Gender", text)
        worksheet = (self.run / "visible-worksheet-1.md").read_text()
        note.write_text(original.replace("## Medatrax", "Coding worksheet\n" + worksheet + "\n## Medatrax"))
        self.assertEqual(0, self.build().returncode)
        note.write_text(note.read_text().replace("Coding worksheet\nICD-10-CM R05.9", "Coding worksheet\nICD-10-CM I10"))
        self.assertEqual(2, self.build().returncode)

    def test_status_whole_reply_and_damaged_record_preservation(self):
        evidence = self.root / "answer.txt"
        evidence.write_text("He has been seen here before.\n", encoding="utf-8")
        result = self.invoke("encounter_status.py", self.run, "--note", 1, "--value", "established", "--evidence", "clinician-answer", "--evidence-path", evidence, "--pointer", "Whole answer", "--reply-file", evidence)
        self.assertEqual(0, result.returncode, result.stderr)
        item = encounter_status.status_for(self.run, 1)
        self.assertEqual(evidence.read_text(), item["clinician_reply"])
        self.assertEqual(str(self.root / "source.txt"), item["source_path"])
        target = self.run / "encounter-status.json"
        target.write_bytes(b'{"broken":')
        result = self.invoke("encounter_status.py", self.run, "--note", 1, "--value", "new", "--evidence", "medatrax", "--evidence-path", evidence, "--pointer", "Selected reading")
        self.assertEqual(2, result.returncode)
        self.assertEqual(b'{"broken":', target.read_bytes())
        self.assertNotIn("Traceback", result.stderr)

    def test_preserved_notes_keep_clinical_prefix_and_exclude_working_appendices(self):
        root = Path(__file__).resolve().parents[1]
        members = (
            ("fixtures/filled-anchor/notes/case-01.md", "\n## Medatrax entry"),
            ("fixtures/slot-form-run/day-b-case-02.md", "\n## Tier block"),
        )
        for relative, boundary in members:
            with self.subTest(member=relative):
                source = (root / relative).read_text(encoding="utf-8")
                expected = source[:source.index(boundary)].rstrip()
                if expected.endswith("---"):
                    expected = expected[:-3].rstrip()
                # Independent expected prefix; no production section regex is reused.
                expected = "\n".join(line.rstrip() for line in expected.splitlines()) + "\n"
                visible, fields = review_manifest.split_note(source)
                self.assertEqual(expected, visible)
                self.assertIn("Patient Reference", fields)
                self.assertNotIn("FILLED·", visible)
                self.assertNotIn("## Drift", visible)
                self.assertNotIn("## PROPOSED", visible)
                # Zero-recognized-field mutant must refuse instead of silently omitting it.
                mutated = source.replace("## Medatrax entry", "## Unrecognized portal entry")
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    review_manifest.split_note(mutated)

    def test_both_committed_branch_templates_retain_all_clinical_lines(self):
        root = Path(__file__).resolve().parents[1]
        for branch in ("SOAP", "HP"):
            with self.subTest(branch=branch):
                source = (root / "skills" / "clinical-note" / (branch + ".md")).read_text(encoding="utf-8")
                template = source.split("```", 2)[1].lstrip("\n")
                clinical, _worksheet = template.split("\nCoding worksheet\n", 1)
                note = template + "\n## Medatrax entry fields\nGender: Female\n"
                visible, fields, worksheets = review_manifest.note_parts(note)
                self.assertEqual(clinical.rstrip() + "\n", visible)
                self.assertEqual(1, len(worksheets))
                self.assertIn("Gender: Female", fields)
                if branch == "HP":
                    self.assertIn("History of Present Illness (OLDCARTS)", visible)
                    self.assertIn("Discussion", visible)


if __name__ == "__main__":
    unittest.main()
