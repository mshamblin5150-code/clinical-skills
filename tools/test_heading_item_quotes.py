"""ADR 0401 native heading-quote controls; all run material is synthetic.

phi-scan: synthetic
"""
import artifact_lock_test_support
import mechanics_test_support
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import completion_checks
import heading_read
import project_context
import research_ledger
import test_discussion_post_scan as post_tests

setUpModule, tearDownModule = mechanics_test_support.module_hooks()


class ItemQuotesThroughThePostCommand(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run = post_tests.Run(self.root)
        self.root.joinpath("claims.md").write_text(
            post_tests.CLAIMS.replace(post_tests.CLAIMS.splitlines()[0], "DATE: 2026-10-20").replace("STATUS: sourced\n", "STATUS: sourced\nQUALIFIERS: none\n"), encoding="utf-8")
        self.item = self.root / "item.md"
        self.item.write_text("Alpha beta gamma.\n", encoding="utf-8")
        self.identifier = "item.md"

    def prepare(self, suffix=' | rests on "Alpha beta gamma."', *, service=False):
        digest = hashlib.sha256(self.item.read_bytes()).hexdigest()
        context_digest = hashlib.sha256((str(self.item) + digest + str(service)).encode()).hexdigest()
        self.root.joinpath("project-context.md").write_text(
            "PROJECT-CONTEXT: none - synthetic directed search\n"
            "OWN-SUBMISSION: none - no synthetic earlier work\n"
            "CASE-MATERIAL: none - no synthetic case\nCASE-RESEARCH: none - no synthetic research\n"
            "CONFIRMED: 2001-01-01\nCONTEXT-DIGEST: " + context_digest + "\n"
            + f"## PLACE: {'synthetic-service' if service else self.item.parent}\nSTATE: read\n"
            + ("" if service else f"ROOT: {self.item.parent}\n")
            + f"OPENED: {self.identifier} | SHA256: {digest}\n", encoding="utf-8")
        self.root.joinpath("heading-read.md").write_text(
            f"## HEADING-READ: {self.run.draft.name}\n"
            f"DRAFT: {hashlib.sha256(self.run.draft.read_bytes()).hexdigest()}\n"
            "ROUTE: separate context\nSENTENCES: 0 factual, 0 clinician's own, 1 item\n"
            f"ITEM: paragraph 1 -> {self.identifier}{suffix}\n"
            "CONTEXT-DIGEST: " + context_digest + "\nCONTEXT-VERDICT: agrees\nVERDICT: clean\n", encoding="utf-8")

    def command(self):
        code, output, error = self.run.grade(bind_heading_read=False)
        return code, output + error

    def test_real_committed_item_and_case_whitespace_normalization(self):
        self.item = Path(__file__).resolve().parents[1] / "tools" / "test_heading_read.py"
        self.identifier = str(self.item)
        self.prepare(' | rests on "All   drafts and CLAIM records are synthetic."')
        code, output = self.command()
        self.assertEqual(0, code, output)

    def test_missing_absent_and_overlapping_repeated_quotes_refuse(self):
        for suffix, text, kind in (
            ("", "Alpha beta gamma.", heading_read.ITEM_QUOTE_MISSING),
            (' | rests on "unwritten support"', "Alpha beta gamma.", heading_read.ITEM_QUOTE_ABSENT),
            (' | rests on "aaa"', "aaaa", heading_read.ITEM_QUOTE_REPEATED),
        ):
            with self.subTest(kind=kind):
                self.item.write_text(text, encoding="utf-8")
                self.prepare(suffix)
                code, output = self.command()
                self.assertEqual(1, code, output)
                self.assertIn(kind, output)

    def test_absence_sentinel_is_declared_unverified_and_service_is_count_only(self):
        self.prepare(" | rests on absent - whole item searched")
        code, output = self.command()
        self.assertEqual(0, code, output)
        self.assertIn("item absence claims: 1 not graded", output)
        self.prepare("", service=True)
        code, output = self.command()
        self.assertEqual(0, code, output)
        self.assertIn("service-item quotes: 1 counted, not graded", output)

    def test_moved_missing_and_unreadable_file_have_one_source_remainder(self):
        for damage in (lambda: self.item.write_text("moved", encoding="utf-8"),
                       lambda: self.item.unlink(),
                       lambda: self.item.write_bytes(b"\xff")):
            with self.subTest(damage=damage):
                self.item.write_text("Alpha beta gamma.", encoding="utf-8")
                self.prepare()
                damage()
                code, output = self.command()
                self.assertNotEqual(0, code, output)
                self.assertIn("unread item sources: 1", output)
                self.assertIn("unread remainder 1", output)
                self.assertIn(heading_read.ITEM_QUOTE_ABSENT + ": 0", output)

    def test_word_body_reader_and_post_read_digest(self):
        self.item = self.root / "item.docx"
        self.identifier = "item.docx"
        with zipfile.ZipFile(self.item, "w") as package:
            package.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Alpha beta gamma.</w:t></w:r></w:p></w:body></w:document>')
        self.prepare()
        code, output = self.command()
        self.assertEqual(0, code, output)
        import docx_read
        original = docx_read.read_docx
        def moved(path):
            result = original(path)
            path.write_bytes(b"moved Word bytes")
            return result
        with mock.patch.object(docx_read, "read_docx", side_effect=moved):
            code, output = self.command()
        self.assertNotEqual(0, code, output)
        self.assertIn("unread item sources: 1", output)

    def test_context_fault_preserves_independent_quote_shape_and_draft_findings(self):
        for suffix, change in (("", False), (' | rests on "Alpha beta gamma."', True)):
            self.prepare(suffix)
            self.root.joinpath("project-context.md").write_text("CONTEXT-DIGEST: broken\n", encoding="utf-8")
            if change:
                self.run.draft.write_text(self.run.draft.read_text(encoding="utf-8") + "\nSynthetic revision.\n", encoding="utf-8")
            code, output = self.command()
            self.assertEqual(1, code, output)
            self.assertIn("unread tool-written records 1", output)
            self.assertIn(heading_read.DRAFT_MISMATCH if change else heading_read.ITEM_QUOTE_MISSING, output)

    def test_old_approval_skips_quotes_and_exact_start_grades_them(self):
        from datetime import timedelta
        self.prepare("")
        start = completion_checks.registry()[heading_read.ITEM_QUOTE_CHECK][0]
        binding = heading_read.binding_from_context(self.run.draft.name, self.run.draft.read_bytes(), (), self.root)
        for moment, expected in ((start - timedelta(microseconds=1), 0), (start, 1)):
            token = completion_checks.MOMENTS.set({"approval": moment})
            try:
                result = heading_read.scan(self.root.joinpath("heading-read.md").read_text(encoding="utf-8"), (binding,))
            finally:
                completion_checks.MOMENTS.reset(token)
            self.assertEqual(bool(expected), any(f.kind == heading_read.ITEM_QUOTE_MISSING for f in result.findings))


if __name__ == "__main__":
    unittest.main()
