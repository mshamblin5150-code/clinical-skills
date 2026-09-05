"""Behavior tests for the committed UpToDate topic-sheet grader."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uptodate_sheet as sheet
import uptodate_store as store


SOURCE = """Patient education: Chlamydia (Beyond the Basics)

Author:
Katherine Hsu, MD, MPH, FAAP
Section Editor:
Jeanne Marrazzo, MD
Literature review current through: Jul 2026.
This topic last updated: Dec 31, 2099.
INTRODUCTION
The source body has clinical guidance and deliberately has no summary heading.
"""


def restatement(words: int = 420) -> str:
    return " ".join(f"paraphrase{number}" for number in range(words))


def topic_sheet(**changes: str) -> str:
    fields = {
        "AUTHORS": "Katherine Hsu, MD, MPH, FAAP",
        "TITLE": "Patient education: Chlamydia (Beyond the Basics)",
        "APA-YEAR": "2099",
        "LITERATURE-REVIEW-CURRENT-THROUGH": "2026-07",
        "RETRIEVED": "2026-09-05",
        "URL": "https://www.uptodate.com/contents/chlamydia-beyond-the-basics",
        "DUMP-ID": "module-1",
        "DISTILLATION-BASIS": "whole article",
        "FAITHFULNESS-READING": "completed against the whole article",
    }
    fields.update(changes)
    metadata = "\n".join(f"{name}: {value}" for name, value in fields.items())
    return f"# {fields['TITLE']}\n\n{metadata}\n\n## Restatement\n\n{restatement()}\n"


class ATopicSheetIsGradedAgainstItsIngestedSource(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        source = self.root / "evidence.txt"
        source.write_text(SOURCE, encoding="utf-8")
        self.store = self.root / "uptodate"
        store.ingest_dump(
            source,
            self.store,
            dump_id="module-1",
            module="Module 1",
            received_on=date(2026, 9, 5),
        )

    def kinds(self, text: str) -> list[str]:
        return [finding.kind for finding in sheet.grade_text(text, self.store).findings]

    def test_a_complete_fallback_sheet_passes(self):
        self.assertEqual(self.kinds(topic_sheet()), [])

    def test_the_reader_owned_boundary_is_declared(self):
        self.assertTrue(sheet.DECLARED_LIMITS)
        self.assertTrue(all(limit.strip() for limit in sheet.DECLARED_LIMITS))

    def test_the_apa_year_comes_from_the_sources_last_updated_line(self):
        self.assertIn(sheet.APA_YEAR_MISMATCH, self.kinds(topic_sheet(**{"APA-YEAR": "2026"})))

    def test_a_summaryless_topic_requires_the_whole_article_basis(self):
        self.assertIn(
            sheet.DISTILLATION_BASIS_MISMATCH,
            self.kinds(topic_sheet(**{"DISTILLATION-BASIS": "summary"})),
        )

    def test_the_retrieval_date_cannot_precede_the_dump(self):
        self.assertIn(
            sheet.RETRIEVAL_BEFORE_DUMP,
            self.kinds(topic_sheet(**{"RETRIEVED": "2026-09-04"})),
        )

    def test_the_url_must_be_a_real_uptodate_host_and_topic_path(self):
        self.assertIn(sheet.BAD_URL, self.kinds(topic_sheet(URL="https://example.com/topic")))

    def test_the_body_stays_inside_the_declared_word_range(self):
        text = topic_sheet().replace(restatement(), restatement(399))
        self.assertIn(sheet.BODY_WORD_COUNT, self.kinds(text))

    def test_exact_source_language_over_the_declared_cap_is_refused(self):
        copied = ("The source body has clinical guidance and deliberately has no summary heading. " * 8)
        text = topic_sheet().replace(restatement(), copied + restatement(420))
        self.assertIn(sheet.VERBATIM_CAP_EXCEEDED, self.kinds(text))

    def test_a_duplicate_required_field_is_not_silently_overwritten(self):
        text = topic_sheet().replace("APA-YEAR: 2099", "APA-YEAR: 2099\nAPA-YEAR: 2099")
        self.assertIn(sheet.DUPLICATE_FIELD, self.kinds(text))

    def test_the_heading_and_title_field_must_name_the_same_topic(self):
        text = topic_sheet().replace(
            "# Patient education: Chlamydia (Beyond the Basics)", "# Another topic", 1
        )
        self.assertIn(sheet.HEADING_TITLE_MISMATCH, self.kinds(text))


if __name__ == "__main__":
    unittest.main()
