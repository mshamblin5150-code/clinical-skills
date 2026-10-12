"""Unposted reads retain their opened population, ADR 0346. Synthetic."""
import unittest

import heading_read
import project_context as context
from test_project_context import ProjectContextFixture
from test_heading_read import DRAFT
import file_digest


class HeadingContextHistory(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.complete_record()
        result = self.write()
        self.assertEqual(0, result.exit_code)
        self.digest = result.digest
        self.record_text = ("## HEADING-READ: draft.md\n"
                            f"DRAFT: {file_digest.sha256_bytes(DRAFT)}\n"
                            "ROUTE: separate context\nSENTENCES: 0 factual, 1 clinician's own\n"
                            f"CONTEXT-DIGEST: {self.digest}\n"
                            "CONTEXT-VERDICT: agrees\nVERDICT: clean\n")

    def grade(self):
        binding = heading_read.Binding("draft.md", DRAFT, (), context.recorded_digest(self.run), context_run=self.run)
        return heading_read.scan(self.record_text, (binding,))

    def test_memory_append_survives_a_context_refresh_but_edit_and_removal_break(self):
        self.memory.write_text("memory index\nanother session's pointer\n", encoding="utf-8")
        self.assertEqual(0, self.write().exit_code)
        self.assertNotEqual(self.digest, context.recorded_digest(self.run))
        self.assertEqual((), self.grade().findings)
        for text in ("edited original line\nanother session's pointer\n", "another session's pointer\n"):
            with self.subTest(text=text):
                self.memory.write_text(text, encoding="utf-8")
                self.assertEqual(0, self.write().exit_code)
                self.assertIn(heading_read.CONTEXT_DIGEST_MISMATCH, {f.kind for f in self.grade().findings})

    def test_edited_file_or_added_opened_item_breaks_the_read(self):
        self.plan.write_text("edited plan", encoding="utf-8")
        self.assertIn(heading_read.CONTEXT_DIGEST_MISMATCH, {f.kind for f in self.grade().findings})
        self.plan.write_text("atlas plan\n", encoding="utf-8")
        second = self.location / "second.md"
        second.write_text("new direction", encoding="utf-8")
        self.record(self.memory_entry(), self.plan_entry() + f"\nOPENED: {second}", self.service_entry())
        self.assertEqual(0, self.write().exit_code)
        self.assertIn(heading_read.CONTEXT_DIGEST_MISMATCH, {f.kind for f in self.grade().findings})

    def test_added_edited_or_removed_asset_breaks_an_unposted_heading_read(self):
        original = self.registry.read_text(encoding='utf-8')
        for before, after in (((), ('owned outbox',)),
                              (('owned outbox',), ('new outbox',)),
                              (('owned outbox',), ())):
            with self.subTest(before=before, after=after):
                for values in (before, after):
                    self.registry.write_text(original + ''.join(f'ASSET: {v}\n' for v in values),
                                             encoding='utf-8')
                    self.record(self.memory_entry(), self.plan_entry(), self.service_entry(),
                                header=tuple(f'ASSET: {v}' for v in values))
                    result = self.write()
                    self.assertEqual(0, result.exit_code, result.report)
                    if values is before:
                        digest = result.digest
                self.assertFalse(context.heading_context_matches(self.run, digest, 'draft.md'))


if __name__ == "__main__":
    unittest.main()
