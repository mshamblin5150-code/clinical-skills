"""Case declarations through the public context command. #1503.

phi-scan: synthetic
"""
from datetime import date
from unittest import mock

import contextlib
import io

import project_context as context
import uptodate_store
from test_project_context import ProjectContextFixture
import repo_root
from test_uptodate_store import topic


class CaseContextCommand(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.registry.write_text(f"MEMORY-INDEX: {self.memory}\nPROJECT: Atlas\n", encoding="utf-8")
        self.store = self.root / "store"
        self.dump = self.store / "dumps" / "synthetic-case"
        supplied = self.root / "supplied.txt"
        supplied.write_text(topic("Synthetic research"), encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            uptodate_store.ingest_dump(supplied, self.store, dump_id="synthetic-case",
                                       module="Synthetic", received_on=date(2026, 10, 11))
        self.source = self.dump / "source.txt"
        self.manifest = self.dump / "manifest.json"
        patcher = mock.patch.object(uptodate_store, "default_store", return_value=self.store)
        patcher.start()
        self.addCleanup(patcher.stop)

    def command(self, *arguments):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output), \
                mock.patch("sys.stdin", io.StringIO("{}")):
            status = context.main([str(self.run), *(arguments or (
                "--write", "--submission", "submission", "--service-payloads", "-"))])
        return status, output.getvalue()

    def case_record(self, material="none - no case", research="none - no research"):
        self.record(self.memory_entry(), header=(
            f"CASE-MATERIAL: {material}", f"CASE-RESEARCH: {research}",
        ))

    def test_missing_material_is_refused(self):
        self.case_record()
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace("CASE-MATERIAL: none - no case\n", ""), encoding="utf-8")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-MATERIAL", report)

    def test_clean_declarations_are_canonicalized(self):
        self.case_record(material=str(self.memory))
        status, report = self.command()
        self.assertEqual(status, 0, report)
        self.assertIn(f"CASE-MATERIAL: {self.memory}", (self.run / context.RECORD_NAME).read_text(encoding="utf-8"))
        self.assertFalse(self.complete().finding)

    def test_missing_research_is_refused(self):
        self.case_record()
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace("CASE-RESEARCH: none - no research\n", ""), encoding="utf-8")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-RESEARCH", report)

    def test_duplicate_material_is_refused(self):
        self.record(self.memory_entry(), header=("CASE-MATERIAL: none - no case",) * 2)
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-MATERIAL", report)

    def test_duplicate_research_is_refused(self):
        self.record(self.memory_entry(), header=("CASE-RESEARCH: none - no research",) * 2)
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-RESEARCH", report)

    def test_material_none_without_reason_is_refused(self):
        self.case_record(material="none")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-MATERIAL none needs a reason", report)

    def test_research_none_without_reason_is_refused(self):
        self.case_record(research="none")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-RESEARCH none needs a reason", report)

    def test_unopened_material_is_refused(self):
        self.case_record(material=str(self.plan))
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-MATERIAL path is not OPENED", report)

    def test_research_without_manifest_is_refused(self):
        self.case_record(research="missing-case")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("no manifest", report)

    def test_changed_filed_copy_is_refused(self):
        self.source.write_bytes(b"changed research")
        self.case_record(research="synthetic-case")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("fingerprint", report)

    def test_unopened_research_is_refused(self):
        self.case_record(research="synthetic-case")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("CASE-RESEARCH path is not OPENED", report)

    def filed_record(self):
        self.registry.write_text(f"MEMORY-INDEX: {self.memory}\nPROJECT: Atlas\n"
                                 f"  LOCATION: {self.source}\n", encoding="utf-8")
        self.record(self.memory_entry(), f"## PLACE: {self.source}\nSTATE: read\nOPENED: {self.source}",
                    header=(f"CASE-MATERIAL: {self.memory}", "CASE-RESEARCH: synthetic-case"))
        status, report = self.command()
        self.assertEqual(status, 0, report)

    def test_filed_opened_research_passes(self):
        self.filed_record()
        self.assertFalse(self.complete().finding)

    def test_go_ahead_rechecks_material(self):
        self.filed_record()
        self.memory.write_bytes(b"changed material")
        status, report = self.command("--go-ahead", "submission")
        self.assertEqual(status, 2, report)
        self.assertIn(str(self.memory), report)

    def test_go_ahead_rechecks_research_manifest(self):
        self.filed_record()
        self.source.write_bytes(b"changed research")
        status, report = self.command("--go-ahead", "submission")
        self.assertEqual(status, 1)

    def test_changed_case_declarations_break_the_digest(self):
        self.filed_record()
        path = self.run / context.RECORD_NAME
        for name, value in (("CASE-MATERIAL", str(self.memory)), ("CASE-RESEARCH", "synthetic-case")):
            with self.subTest(name=name):
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace(f"{name}: {value}", f"{name}: none - changed reason"), encoding="utf-8")
                self.assertTrue(self.complete().finding)
                path.write_text(original, encoding="utf-8")
