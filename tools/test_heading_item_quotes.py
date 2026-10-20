"""ADR 0401 native heading-quote controls; all run material is synthetic.

phi-scan: synthetic
"""
import artifact_lock_test_support
import mechanics_test_support
import hashlib
import importlib
import io
import json
import tempfile
import struct
import unittest
import zipfile
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

import completion_checks
import heading_read
import project_context
import research_ledger
import test_discussion_post_scan as post_tests
import test_own_figures as figure_tests
import test_checks_ledger as checks_tests
from prose_bind import ProseBind

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

    def context_with_escaped_damage(self, text):
        row = {"submission": "synthetic", "report": "synthetic\tline", "digest": "none",
               "finding": False, "coverage": False, "moved_places": [], "added_lines": []}
        return text.replace("## PLACE:", "GO-AHEAD: " + json.dumps(row) + "\n## PLACE:", 1)

    def test_real_committed_item_and_case_whitespace_normalization(self):
        self.item = Path(__file__).resolve().parents[1] / "AGENTS.md"
        self.identifier = str(self.item)
        self.prepare(' | rests on "Agent-agnostic   skills for a NURSE practitioner student\'s written work"')
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

    def test_moved_or_missing_file_has_one_source_remainder(self):
        for damage in (lambda: self.item.write_text("moved", encoding="utf-8"),
                       lambda: self.item.unlink()):
            with self.subTest(damage=damage):
                self.item.write_text("Alpha beta gamma.", encoding="utf-8")
                self.prepare()
                damage()
                code, output = self.command()
                self.assertNotEqual(0, code, output)
                self.assertIn("unread item sources: 1", output)
                self.assertIn("unread remainder 1", output)
                self.assertIn(heading_read.ITEM_QUOTE_ABSENT + ": 0", output)

    def test_unreadable_text_at_its_recorded_digest_is_coverage_not_a_finding(self):
        for name, raw in (("item.md", b"\xff"), ("item.docx", b"not a Word package")):
            with self.subTest(name=name):
                self.item = self.root / name
                self.identifier = name
                self.item.write_bytes(raw)
                self.prepare()
                code, output = self.command()
                self.assertEqual(2, code, output)
                self.assertIn("unread item sources: 1", output)
                self.assertIn("unread remainder 1", output)
                self.assertIn("findings: 0", output)

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

    def test_unsupported_or_encrypted_word_package_is_unread_at_matching_digest(self):
        self.item = self.root / "item.docx"
        self.identifier = "item.docx"
        for unsupported in (True, False):
            with self.subTest(unsupported=unsupported):
                with zipfile.ZipFile(self.item, "w") as package:
                    package.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Alpha beta gamma.</w:t></w:r></w:p></w:body></w:document>')
                raw = bytearray(self.item.read_bytes())
                local, central = raw.index(b"PK\x03\x04"), raw.index(b"PK\x01\x02")
                for offset in ((local + 8, central + 10) if unsupported else (local + 6, central + 8)):
                    struct.pack_into("<H", raw, offset, 99 if unsupported else 1)
                self.item.write_bytes(raw)
                self.prepare()
                code, output = self.command()
                self.assertEqual(2, code, output)
                self.assertIn("unread item sources: 1", output)
                self.assertIn("unread remainder 1", output)
                self.assertIn("findings: 0", output)

    def test_corrupt_compressed_word_body_is_unread_at_matching_digest(self):
        self.item = self.root / "item.docx"
        self.identifier = "item.docx"
        for compression in (zipfile.ZIP_DEFLATED, zipfile.ZIP_LZMA):
            with self.subTest(compression=compression):
                with zipfile.ZipFile(self.item, "w", compression=compression) as package:
                    package.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Alpha beta gamma.</w:t></w:r></w:p></w:body></w:document>')
                raw = bytearray(self.item.read_bytes())
                local = raw.index(b"PK\x03\x04")
                name, extra = struct.unpack_from("<HH", raw, local + 26)
                data = local + 30 + name + extra
                raw[data + (4 if compression == zipfile.ZIP_LZMA else 0)] = 0xff
                self.item.write_bytes(raw)
                self.prepare()
                code, output = self.command()
                self.assertEqual(2, code, output)
                self.assertIn("unread item sources: 1", output)
                self.assertIn("unread remainder 1", output)
                self.assertIn("findings: 0", output)

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
        before = start - timedelta(microseconds=1)
        for moment, item_moment, expected in ((before, before, 0), (start, start, 1), (before, None, 1)):
            @contextmanager
            def approval_context(_run, _submission):
                token = completion_checks.MOMENTS.set({"approval": moment})
                item_token = completion_checks.ITEM_MOMENTS.set({"old.md": before, "new.md": start, self.run.draft.name: item_moment})
                try:
                    yield
                finally:
                    completion_checks.ITEM_MOMENTS.reset(item_token)
                    completion_checks.MOMENTS.reset(token)
            with mock.patch.object(completion_checks, "grading", approval_context):
                code, output = self.command()
            self.assertEqual(expected, code, output)
            self.assertIn(f"{heading_read.ITEM_QUOTE_MISSING}: {expected}", output)

    def test_retained_digest_resolves_its_own_item_path_after_current_context_moves(self):
        self.prepare()
        self.assertEqual(0, self.command()[0])  # Retains the original context population.
        record = (self.root / "heading-read.md").read_text(encoding="utf-8")
        self.item = self.root / "later" / "item.md"
        self.item.parent.mkdir()
        self.item.write_text("Later unrelated source.", encoding="utf-8")
        self.prepare(' | rests on "Later unrelated source."')
        (self.root / "heading-read.md").write_text(record, encoding="utf-8")
        code, output = self.command()
        self.assertEqual(1, code, output)  # The existing context-population comparison refuses.
        self.assertIn(heading_read.CONTEXT_DIGEST_MISMATCH + ": 1", output)
        self.assertIn(heading_read.ITEM_QUOTE_ABSENT + ": 0", output)
        self.assertIn("unread remainder 0", output)

    def test_damaged_current_context_keeps_independent_missing_quote_and_draft_checks(self):
        for service in (False, True):
            with self.subTest(service=service):
                self.prepare("", service=service)
                path = self.root / "project-context.md"
                path.write_text(self.context_with_escaped_damage(path.read_text(encoding="utf-8")), encoding="utf-8")
                self.run.draft.write_text(self.run.draft.read_text(encoding="utf-8") + "\nSynthetic revision.\n", encoding="utf-8")
                code, output = self.command()
                self.assertEqual(1, code, output)
                self.assertIn("heading-read context comparisons: not graded", output)
                self.assertIn(heading_read.ITEM_QUOTE_MISSING + ": 1", output)
                self.assertIn(heading_read.DRAFT_MISMATCH + ": 1", output)
                self.assertIn(heading_read.ITEM_QUOTE_ABSENT + ": 0", output)
                self.assertNotIn("service-item quotes:", output)
                self.assertNotIn("unread item sources:", output)
                self.assertEqual(1, sum(line.startswith("unread remainder ") for line in output.splitlines()), output)

    def test_retained_context_damage_uses_each_items_own_moment_and_continues(self):
        from datetime import timedelta
        self.prepare()
        current = self.root / "project-context.md"
        text = current.read_text(encoding="utf-8")
        digest = project_context.read_record(text).value("CONTEXT-DIGEST")
        retained = self.root / "private" / "heading-contexts" / (digest + ".md")
        retained.parent.mkdir(parents=True)
        retained.write_text(self.context_with_escaped_damage(text), encoding="utf-8")
        current.write_text(text.replace(digest, "a" * 64), encoding="utf-8")
        start = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        before = start - timedelta(microseconds=1)
        for moment, status in ((before, 0), (start, 1), (None, 1)):
            with self.subTest(moment=moment):
                @contextmanager
                def item_context(_run, _submission):
                    token = completion_checks.MOMENTS.set({"approval": before})
                    items = completion_checks.ITEM_MOMENTS.set({"old.md": before, "current.md": start,
                                                               self.run.draft.name: moment})
                    try:
                        yield
                    finally:
                        completion_checks.ITEM_MOMENTS.reset(items)
                        completion_checks.MOMENTS.reset(token)
                with mock.patch.object(completion_checks, "grading", item_context):
                    code, output = self.command()
                self.assertEqual(status, code, output)
                self.assertIn(heading_read.ITEM_QUOTE_ABSENT + ": 0", output)
                self.assertNotIn("unread item sources:", output)
                self.assertEqual(1, sum(line.startswith("unread remainder ") for line in output.splitlines()), output)
                if status:
                    self.assertIn("heading-read item quotes: not graded", output)
                else:
                    self.assertNotIn("damaged text", output)
        # A current damaged member must not prevent an independent draft refusal.
        self.run.draft.write_text(self.run.draft.read_text(encoding="utf-8") + "\nSynthetic revision.\n", encoding="utf-8")
        code, output = self.command()
        self.assertEqual(1, code, output)
        self.assertIn(heading_read.DRAFT_MISMATCH + ": 1", output)
        self.assertIn("heading-read item quotes: not graded", output)


class EveryNativeHostCarriesItemCoverage(unittest.TestCase):
    def test_service_count_and_one_unread_source_reach_all_six_reports(self):
        for name in (*figure_tests.CONSUMERS, "checks_ledger"):
            for service in (True, False):
                with self.subTest(host=name, service=service), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    if name == "checks_ledger":
                        run, artifact = root, root / "draft.md"
                        artifact.write_text(checks_tests.DRAFT_TEXT, encoding="utf-8")
                        checks_path = root / "checks.md"
                        checks_path.write_text(checks_tests.whole_file(), encoding="utf-8")
                        argv = [str(checks_path), "--document", str(artifact)]
                    else:
                        run, artifact, argv = figure_tests.fixture(name, root, "The plan names a review.")
                    item = run / "source.md"
                    item.write_bytes(b"\xff")
                    digest = hashlib.sha256(item.read_bytes()).hexdigest()
                    context_digest = hashlib.sha256((str(run) + str(service)).encode()).hexdigest()
                    (run / "project-context.md").write_text(
                        "PROJECT-CONTEXT: none - synthetic source\n"
                        "OWN-SUBMISSION: none - no synthetic earlier work\nCASE-MATERIAL: none - no synthetic case\n"
                        "CASE-RESEARCH: none - no synthetic research\nCONFIRMED: 2001-01-01\n"
                        f"CONTEXT-DIGEST: {context_digest}\n"
                        f"## PLACE: {'synthetic-service' if service else run}\nSTATE: read\n"
                        + ("" if service else f"ROOT: {run}\n")
                        + f"OPENED: source.md | SHA256: {digest}\n", encoding="utf-8")
                    record = (
                        f"## HEADING-READ: {artifact.name}\nDRAFT: {hashlib.sha256(artifact.read_bytes()).hexdigest()}\n"
                        "ROUTE: separate context\nSENTENCES: 0 factual, 0 clinician's own, 2 item\n"
                        'ITEM: paragraph 1 -> source.md | rests on "support"\n'
                        'ITEM: paragraph 2 -> source.md | rests on "other support"\n'
                        f"CONTEXT-DIGEST: {context_digest}\nCONTEXT-VERDICT: agrees\nVERDICT: clean\n")
                    if name == "checks_ledger":
                        checks_path.write_text(checks_tests.whole_file() + "\n" + record, encoding="utf-8")
                    else:
                        (run / "heading-read.md").write_text(record, encoding="utf-8")
                    (run / "claims.md").write_text("DATE: 2026-10-20\n", encoding="utf-8")
                    output = io.StringIO()
                    with redirect_stdout(output), redirect_stderr(output):
                        code = importlib.import_module(name).main(argv)
                    report = output.getvalue()
                    self.assertIn(code, (0, 1, 2), report)
                    self.assertEqual(1, sum(line.startswith("unread remainder ") for line in report.splitlines()), report)
                    if service:
                        self.assertIn("service-item quotes: 2 counted, not graded", report)
                        self.assertNotIn("unread item sources:", report)
                    else:
                        self.assertNotEqual(0, code, report)
                        self.assertIn("unread item sources: 1", report)
                        self.assertNotIn("unread item sources: 2", report)


class ReaderBriefsCarryTheSharedQuoteContract(ProseBind, unittest.TestCase):
    def test_all_five_briefs_name_reader_written_support(self):
        root = Path(__file__).resolve().parents[1]
        for skill in ("discussion-post", "discussion-reply", "peer-critique", "course-assignment", "practicum-case-study"):
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertProseIn("Each ITEM quotes its unique supporting place", text)
                self.assertProseIn("shared service-item exception", text)


if __name__ == "__main__":
    unittest.main()
