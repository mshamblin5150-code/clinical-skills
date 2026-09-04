"""Tiered checks for the generated USPSTF provenance sections."""

from __future__ import annotations

import re
import sys
import unittest
from collections import defaultdict
from pathlib import Path

import artifact_lock_test_support  # noqa: F401

import guidelines_catalog
import guidelines_recs
import uspstf_table
import artifact_provenance
from guidelines_manifest import read_or_raise


REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE = REPO_ROOT / "reference" / "guidelines-uspstf.md"
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
CORPUS = Path("C:/codeing/guidelines-text")
FIELD_HEADING = "Population cells quoted from the declared field"
TOPIC_FIELD_HEADING = "Topic cells quoted from the declared field"
ABSENCE_HEADING = "Documents stating no interval evidence was found"


def section_rows(markdown: str, heading: str, width: int = 3) -> list[list[str]]:
    return guidelines_recs._markdown_rows(markdown, heading, width)


def curated_rows(markdown: str) -> list[guidelines_recs.CuratedRow]:
    return [
        row
        for document_rows in guidelines_recs.parse_curated_table(markdown).values()
        for row in document_rows
    ]


def statement_lookup(
    rows: list[guidelines_recs.CuratedRow], *, collapse: bool = False
) -> dict[tuple[str, int, str], list[str]]:
    lookup: dict[tuple[str, int, str], list[str]] = defaultdict(list)
    for row in rows:
        key = (row.filename, row.page, row.grade)
        if collapse:
            lookup[key] = [row.statement]
        else:
            lookup[key].append(row.statement)
    return lookup


def field_quoted_rows(
    rows: list[guidelines_recs.CuratedRow],
    lookup: dict[tuple[str, int, str], list[str]],
) -> list[guidelines_recs.CuratedRow]:
    marked = []
    for row in rows:
        candidates = lookup.get((row.filename, row.page, row.grade), [])
        if not candidates:
            raise AssertionError(f"no statement candidates for {row.filename} p{row.page}")
        if row.population != uspstf_table.NOT_STATED and not any(
            uspstf_table.derive_population(statement, "") == row.population
            for statement in candidates
        ):
            marked.append(row)
    return marked


def field_pairs(
    rows: list[guidelines_recs.CuratedRow],
) -> set[tuple[str, str, int]]:
    return {(row.population, row.filename, row.page) for row in rows}


def topic_field_entries(markdown: str) -> list[tuple[str, str]]:
    return [
        (topic, filename.strip("`"))
        for topic, filename in section_rows(markdown, TOPIC_FIELD_HEADING, 2)
    ]


def assert_topic_tier1(test: unittest.TestCase, markdown: str) -> None:
    named_rows = topic_field_entries(markdown)
    named = set(named_rows)
    recommendations = guidelines_recs._markdown_rows(markdown, "Recommendations", 9)
    topics_by_file: dict[str, set[str]] = defaultdict(set)
    for row in recommendations:
        topics_by_file[row[7].strip("`")].add(row[0])

    test.assertEqual(len(named_rows), len(named), "topic entries must be unique")
    for topic, filename in named:
        test.assertIn(filename, topics_by_file)
        test.assertEqual(topics_by_file[filename], {topic})

    section = markdown.split(f"## {TOPIC_FIELD_HEADING}", 1)[1].split("\n## ", 1)[0]
    test.assertIn(
        f"{uspstf_table.plural(len(named_rows), 'document')} quote the PDF's declared "
        "title field",
        section,
    )
    test.assertIn("The filename-slug route is excluded", section)

    listed_files = {filename for _, filename in named}
    for filename, topics in topics_by_file.items():
        if filename in listed_files:
            continue
        filename_topic = uspstf_table.derive_topic([], filename)
        test.assertNotIn(
            filename_topic,
            topics,
            f"unlisted {filename} has the filename-route topic {filename_topic!r}",
        )


def declared_field_topic_entries(
    documents: dict[str, tuple[list[str], str]],
) -> set[tuple[str, str]]:
    entries = set()
    for filename, (pages, metadata_title) in documents.items():
        page_title = uspstf_table._title_from_page(
            uspstf_table.normalize(pages[0][:800]) if pages else ""
        )
        declared_title = uspstf_table._clean_title(
            uspstf_table.TITLE_STOP.split(
                uspstf_table.normalize(metadata_title)
            )[0]
        )
        if not uspstf_table._looks_like_a_title(
            page_title
        ) and uspstf_table._looks_like_a_title(declared_title):
            entries.add(
                (
                    uspstf_table.derive_topic(pages, filename, metadata_title),
                    filename,
                )
            )
    return entries


def assert_topic_tier2(
    test: unittest.TestCase,
    named: set[tuple[str, str]],
    documents: dict[str, tuple[list[str], str]],
) -> None:
    expected = declared_field_topic_entries(documents)
    test.assertEqual(named, expected)
    for topic, filename in named:
        pages, metadata_title = documents[filename]
        test.assertEqual(
            topic,
            uspstf_table.derive_topic(pages, filename, metadata_title),
        )


class PopulationFieldQuotationTier1(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markdown = REFERENCE.read_text(encoding="utf-8")
        cls.rows = curated_rows(cls.markdown)
        cls.derived_rows = field_quoted_rows(cls.rows, statement_lookup(cls.rows))
        cls.derived_pairs = field_pairs(cls.derived_rows)
        cls.named_pair_rows = [
            (population, filename.strip("`"), int(page))
            for population, filename, page in section_rows(cls.markdown, FIELD_HEADING)
        ]
        cls.named_pairs = set(cls.named_pair_rows)

    def test_section_names_exactly_the_multiset_join_result(self) -> None:
        self.assertEqual(len(self.named_pair_rows), len(self.named_pairs))
        self.assertEqual(self.named_pairs, self.derived_pairs)
        self.assertEqual(len(self.derived_rows), 15)
        self.assertEqual(len(self.derived_pairs), 13)

    def test_every_named_triple_matches_a_recommendation_row(self) -> None:
        recommendation_pairs = {
            (row.population, row.filename, row.page) for row in self.rows
        }
        self.assertTrue(self.named_pairs <= recommendation_pairs)
        self.assertTrue({pair[1] for pair in self.named_pairs} <= {r.filename for r in self.rows})

    def test_rendered_counts_are_derived_from_the_named_populations(self) -> None:
        row_count = len(self.derived_rows)
        pair_count = len(self.named_pair_rows)
        self.assertIn(
            f"{uspstf_table.plural(row_count, 'recommendation row')} form "
            f"{uspstf_table.plural(pair_count, 'population-and-document pair')}.",
            self.markdown,
        )

    def test_a_dict_collapsed_lookup_reproduces_the_withdrawn_failure(self) -> None:
        collapsed = field_quoted_rows(
            self.rows, statement_lookup(self.rows, collapse=True)
        )
        collapsed_pairs = field_pairs(collapsed)

        self.assertEqual((len(collapsed), len({row.filename for row in collapsed})), (26, 21))
        with self.assertRaises(AssertionError):
            self.assertEqual(collapsed_pairs, self.named_pairs)

    def test_multivitamin_grade_i_rows_are_identical_across_all_nine_columns(self) -> None:
        raw_rows = guidelines_recs._markdown_rows(self.markdown, "Recommendations", 9)
        repeated = [
            row
            for row in raw_rows
            if row[2] == "I"
            and row[7].strip("`")
            == "multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf"
        ]
        self.assertEqual(len(repeated), 2)
        self.assertEqual(repeated[0], repeated[1])


class TopicFieldQuotationTier1(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markdown = REFERENCE.read_text(encoding="utf-8")

    def test_shipped_artifact_names_declared_field_topics(self) -> None:
        assert_topic_tier1(self, self.markdown)

    def test_an_unlisted_filename_route_topic_turns_tier_1_red(self) -> None:
        filename = "synthetic-filename-route.pdf"
        topic = uspstf_table.derive_topic([], filename)
        row = (
            f"| {topic} | adults | B | not stated | 2026 |  |  | `{filename}` | 1 |"
        )
        mutant = self.markdown.replace("\n## Statements", f"\n{row}\n\n## Statements", 1)

        with self.assertRaisesRegex(AssertionError, "filename-route topic"):
            assert_topic_tier1(self, mutant)


class IntervalEvidenceAbsenceTier1(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.markdown = REFERENCE.read_text(encoding="utf-8")
        cls.rows = curated_rows(cls.markdown)
        cls.named = [
            uspstf_table.IntervalAbsence(
                filename.strip("`"),
                int(page),
                quotation.removeprefix("RENDERED: "),
                rendered=quotation.startswith("RENDERED: "),
            )
            for filename, page, quotation in section_rows(cls.markdown, ABSENCE_HEADING)
        ]
        catalog_rows, _, problems = guidelines_catalog.parse_catalog(
            CATALOG.read_text(encoding="utf-8")
        )
        if problems:
            raise AssertionError("; ".join(problems))
        cls.page_counts = {
            Path(row.filename).name: int(row.page_count) for row in catalog_rows
        }

    def test_section_is_the_declared_reading(self) -> None:
        self.assertEqual(tuple(self.named), uspstf_table.INTERVAL_ABSENCES)

    def test_every_named_file_contributes_only_not_stated_interval_rows(self) -> None:
        rows_by_file: dict[str, list[guidelines_recs.CuratedRow]] = defaultdict(list)
        for row in self.rows:
            rows_by_file[row.filename].append(row)
        for entry in self.named:
            self.assertTrue(rows_by_file[entry.filename], entry.filename)
            self.assertTrue(
                all(row.interval == uspstf_table.NOT_STATED for row in rows_by_file[entry.filename]),
                entry.filename,
            )

    def test_pages_are_within_the_catalog_and_quotes_are_not_statements(self) -> None:
        statements_by_file: dict[str, set[str]] = defaultdict(set)
        for row in self.rows:
            statements_by_file[row.filename].add(row.statement)
        for entry in self.named:
            self.assertGreaterEqual(entry.page, 1)
            self.assertLessEqual(entry.page, self.page_counts[entry.filename])
            self.assertNotIn(entry.quotation, statements_by_file[entry.filename])

    def test_declared_vocabulary_can_refuse_but_never_propose_membership(self) -> None:
        for entry in self.named:
            quotation = entry.quotation.casefold()
            self.assertTrue(
                any(phrase in quotation for phrase in uspstf_table.INTERVAL_ABSENCE_VOCABULARY),
                entry.filename,
            )
        for excluded in ("evidence is limited", "not well established"):
            self.assertFalse(
                any(phrase in excluded for phrase in uspstf_table.INTERVAL_ABSENCE_VOCABULARY)
            )


class ExtractedCorpusTier2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (CORPUS / "manifest.json").exists():
            message = f"TIER 2 SKIPPED: extracted guideline corpus is absent at {CORPUS}"
            print(message, file=sys.stderr)
            raise unittest.SkipTest(message)
        handoff = read_or_raise(
            CORPUS,
            expected_commit=artifact_provenance.checkout_commit(REPO_ROOT),
            allow_untrusted_provenance=True,
        )
        cls.topic_documents = {
            Path(document.source).name: (
                list(handoff.pages[doc_id]),
                document.title or "",
            )
            for doc_id, document in handoff.documents.items()
            if document.society == "USPSTF"
        }
        cls.pages = {
            filename: pages for filename, (pages, _title) in cls.topic_documents.items()
        }
        markdown = REFERENCE.read_text(encoding="utf-8")
        cls.field_pairs = {
            (population, filename.strip("`"), int(page))
            for population, filename, page in section_rows(markdown, FIELD_HEADING)
        }
        cls.topic_entries = set(topic_field_entries(markdown))

    def test_field_quoted_cells_equal_the_declared_document_field_verbatim(self) -> None:
        for population, filename, _page in self.field_pairs:
            self.assertEqual(population, uspstf_table.document_population(self.pages[filename]))

    def test_interval_absence_quotes_occur_on_the_cited_extracted_page(self) -> None:
        for entry in uspstf_table.INTERVAL_ABSENCES:
            quotation = entry.quotation
            if entry.rendered:
                continue
            page = uspstf_table.unwrap(
                uspstf_table.normalize(self.pages[entry.filename][entry.page - 1])
            )
            normalized_quote = uspstf_table.unwrap(uspstf_table.normalize(quotation))
            self.assertIn(normalized_quote, page, entry.filename)

    def test_topic_membership_and_values_equal_the_corpus_derivation(self) -> None:
        assert_topic_tier2(self, self.topic_entries, self.topic_documents)

    def test_substituting_a_page_route_document_turns_tier_2_red(self) -> None:
        expected = declared_field_topic_entries(self.topic_documents)
        page_route = next(
            (
                uspstf_table.derive_topic(pages, filename, metadata_title),
                filename,
            )
            for filename, (pages, metadata_title) in self.topic_documents.items()
            if uspstf_table._looks_like_a_title(
                uspstf_table._title_from_page(uspstf_table.normalize(pages[0][:800]))
            )
        )
        mutant = set(expected)
        mutant.remove(next(iter(mutant)))
        mutant.add(page_route)

        with self.assertRaises(AssertionError):
            assert_topic_tier2(self, mutant, self.topic_documents)


if __name__ == "__main__":
    unittest.main()
