"""Behavior tests for the scratch-rooted UpToDate evidence store."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx_read
import uptodate_store as store


def topic(title: str, *, updated: str = "Jan 09, 2026") -> str:
    return f"""{title}

Author:
Author, A., MD
Section Editor:
Editor, E., MD
Literature review current through: Jul 2026.
This topic last updated: {updated}.
INTRODUCTION
This body explains {title} and gives enough literal text for a searchable result.
"""


def untitled_block(detail: str) -> str:
    return f"""Author:
Author, A., MD
Section Editor:
Editor, E., MD
Literature review current through: Jul 2026.
This topic last updated: Jan 09, 2026.
INTRODUCTION
{detail}
Terms of use
"""


class AnIngestedDumpBecomesAccumulatedEvidence(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = self.root / "uptodate"

    def write_dump(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_ingest_writes_one_manifest_and_a_searchable_index(self):
        source = self.write_dump("evidence.txt", topic("Acute cervicitis"))

        report = store.ingest_dump(
            source,
            self.store,
            dump_id="nur5144-m1-2026-09-05",
            module="NUR5144 Module 1",
            received_on=date(2026, 9, 5),
        )

        manifest = json.loads(report.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["module"], "NUR5144 Module 1")
        self.assertEqual([row["title"] for row in manifest["topics"]], ["Acute cervicitis"])
        self.assertEqual((report.blocks_read, report.candidates, report.unread), (1, 1, 0))
        self.assertEqual(
            store.search(self.store, "searchable result")[0].title,
            "Acute cervicitis",
        )

    def test_rebuild_applies_a_later_fold_to_stored_bytes_and_to_the_query(self):
        salted = "Acute сervicitis"
        source = self.write_dump("evidence.txt", topic(salted))
        without_cyrillic_c = {
            key: value for key, value in docx_read.HOMOGLYPHS.items() if key != "с"
        }
        with mock.patch.object(docx_read, "HOMOGLYPHS", without_cyrillic_c):
            report = store.ingest_dump(
                source,
                self.store,
                dump_id="before-map-change",
                module="Module 1",
                received_on=date(2026, 1, 2),
            )
        stored = report.manifest.parent / store.SOURCE_NAME
        before_bytes = stored.read_bytes()
        before_manifest = json.loads(report.manifest.read_text(encoding="utf-8"))

        store.rebuild_index(self.store)

        self.assertEqual(
            store.search(self.store, "сervicitis")[0].dump_id,
            "before-map-change",
        )
        self.assertEqual(
            store.search(self.store, "cervicitis")[0].dump_id,
            "before-map-change",
        )
        self.assertEqual(stored.read_bytes(), before_bytes)
        self.assertEqual(
            json.loads(report.manifest.read_text(encoding="utf-8"))["source_sha256"],
            before_manifest["source_sha256"],
        )

    def test_every_rebuild_reports_remaining_non_latin_letters_per_dump(self):
        first = self.write_dump("first.txt", topic("TNFα treatment"))
        second = self.write_dump("second.txt", topic("Plain topic"))
        store.ingest_dump(
            first,
            self.store,
            dump_id="greek-notation",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        store.ingest_dump(
            second,
            self.store,
            dump_id="plain",
            module="Module 2",
            received_on=date(2026, 2, 2),
        )
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            store.rebuild_index(self.store)

        report = stderr.getvalue()
        self.assertIn(
            "dump greek-notation: non-Latin letter remaining after normalization: "
            "U+03B1 GREEK SMALL LETTER ALPHA: 2",
            report,
        )
        self.assertIn(
            "dump plain: non-Latin letters remaining after normalization: 0",
            report,
        )

    def test_topics_from_an_earlier_manifest_remain_entitled(self):
        first = self.write_dump("first.txt", topic("Earlier topic"))
        second = self.write_dump("second.txt", topic("Current topic"))
        store.ingest_dump(
            first,
            self.store,
            dump_id="first",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        store.ingest_dump(
            second,
            self.store,
            dump_id="second",
            module="Module 4",
            received_on=date(2026, 4, 2),
        )

        self.assertEqual(store.entitled_topics(self.store), {"Earlier topic", "Current topic"})

    def test_entitled_topic_details_come_from_the_same_validated_manifest_rows(self):
        source = self.write_dump("evidence.txt", topic("A stored topic"))
        store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )

        self.assertEqual(
            store.entitled_topic_details(self.store),
            (
                store.StoredTopic(
                    title="A stored topic",
                    authors="Author, A., MD",
                    last_updated="2026-01-09",
                    received_on="2026-01-02",
                    literature_review_current_through="2026-07",
                ),
            ),
        )

    def test_a_newer_topic_version_supplies_both_masthead_and_currency(self):
        older = self.write_dump("older.txt", topic("Repeated topic"))
        newer = self.write_dump(
            "newer.txt",
            topic("Repeated topic")
            .replace("Author, A., MD", "New Author, MD")
            .replace("Jul 2026", "Mar 2026")
            .replace("Jan 9, 2026", "Mar 9, 2026"),
        )
        store.ingest_dump(
            older,
            self.store,
            dump_id="older",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        store.ingest_dump(
            newer,
            self.store,
            dump_id="newer",
            module="Module 2",
            received_on=date(2026, 3, 2),
        )

        snapshot = store.store_snapshot(self.store)

        self.assertEqual(snapshot.topics[0].authors, "New Author, MD")
        self.assertEqual(dict(snapshot.currencies)["repeated topic"], "2026-03")

    def test_an_existing_dump_id_is_never_overwritten(self):
        source = self.write_dump("evidence.txt", topic("Original topic"))
        store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        source.write_text(topic("Replacement topic"), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "already exists"):
            store.ingest_dump(
                source,
                self.store,
                dump_id="one",
                module="Module 1",
                received_on=date(2026, 1, 3),
            )
        self.assertEqual(store.entitled_topics(self.store), {"Original topic"})

    def test_byte_identical_topic_blocks_are_merged(self):
        source = self.write_dump(
            "evidence.txt", topic("Repeated topic") + topic("Repeated topic")
        )

        report = store.ingest_dump(
            source,
            self.store,
            dump_id="duplicates",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )

        self.assertEqual((report.blocks_read, report.candidates, report.merged), (2, 2, 1))

    def test_one_title_over_different_bodies_is_refused(self):
        first = topic("Repeated topic")
        second = topic("Repeated topic").replace(
            "gives enough literal text for a searchable result",
            "has materially different clinical content",
        )
        source = self.write_dump("evidence.txt", first + second)

        with self.assertRaisesRegex(ValueError, "untitled 2 of 2"):
            store.ingest_dump(
                source,
                self.store,
                dump_id="ambiguous",
                module="Module 1",
                received_on=date(2026, 1, 2),
            )

    def test_a_malformed_accumulated_manifest_never_grants_entitlement(self):
        source = self.write_dump("evidence.txt", topic("Original topic"))
        report = store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        manifest = json.loads(report.manifest.read_text(encoding="utf-8"))
        manifest["literature_review_current_through"] = "recent"
        report.manifest.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "currency stamp"):
            store.entitled_topics(self.store)

    def test_a_manifest_source_name_cannot_escape_its_dump_directory(self):
        source = self.write_dump("evidence.txt", topic("Original topic"))
        report = store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        manifest = json.loads(report.manifest.read_text(encoding="utf-8"))
        manifest["source_file"] = "../source.txt"
        report.manifest.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "source file"):
            store.entitled_topics(self.store)

    def test_a_manifest_without_its_matching_raw_source_grants_no_entitlement(self):
        source = self.write_dump("evidence.txt", topic("Original topic"))
        report = store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
        )
        (report.manifest.parent / store.SOURCE_NAME).unlink()

        with self.assertRaisesRegex(ValueError, "source does not match"):
            store.entitled_topics(self.store)

    def test_an_independent_metadata_marker_cannot_disappear_from_ingest(self):
        source = self.write_dump(
            "partial.txt",
            "Unrecognized topic\n\nLiterature review current through: Jul 2026.\n"
            "This topic last updated: Jan 09, 2026.\n",
        )

        with self.assertRaisesRegex(ValueError, "read 0 of 1"):
            store.ingest_dump(
                source,
                self.store,
                dump_id="partial",
                module="Module 1",
                received_on=date(2026, 1, 2),
            )

    def test_an_untitled_layout_is_refused_before_population_completeness(self):
        source = self.write_dump(
            "untitled.txt",
            untitled_block("First body")
            + untitled_block("Second body")
            + untitled_block("Second body")
            + untitled_block("Third body"),
        )

        with self.assertRaisesRegex(ValueError, "untitled 4 of 4"):
            store.ingest_dump(
                source,
                self.store,
                dump_id="untitled",
                module="Module 1",
                received_on=date(2026, 1, 2),
            )

    def test_a_supplied_reference_list_is_retained_with_its_provenance(self):
        source = self.write_dump("evidence.txt", topic("Original topic"))
        references = self.write_dump("references.txt", "Primary source list\n")

        report = store.ingest_dump(
            source,
            self.store,
            dump_id="one",
            module="Module 1",
            received_on=date(2026, 1, 2),
            references=references,
        )

        manifest = json.loads(report.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["reference_file"], store.REFERENCE_NAME)
        self.assertEqual(
            (report.manifest.parent / store.REFERENCE_NAME).read_text(encoding="utf-8"),
            "Primary source list\n",
        )


class TheSweepReportsAndIngestsNothing(unittest.TestCase):
    def test_topic_bodies_outside_the_store_are_only_counted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "unfiled.txt"
            candidate.write_text(topic("Unfiled topic"), encoding="utf-8")
            evidence_store = root / "uptodate"

            report = store.sweep_unfiled(root, evidence_store)

            self.assertEqual(report.files, 1)
            self.assertEqual(report.topic_bodies, 1)
            self.assertFalse(evidence_store.exists())

    def test_an_incomplete_topic_shape_is_reported_without_becoming_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "partial.txt").write_text(
                "Partial topic\n\nAuthor:\nAuthor, A.\n", encoding="utf-8"
            )
            evidence_store = root / "uptodate"

            report = store.sweep_unfiled(root, evidence_store)

            self.assertEqual((report.files, report.topic_bodies), (1, 1))
            self.assertFalse(evidence_store.exists())

    def test_a_copy_of_an_already_ingested_dump_is_not_reported_as_unfiled(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "filed.txt"
            candidate.write_text(topic("Filed topic"), encoding="utf-8")
            evidence_store = root / "uptodate"
            store.ingest_dump(
                candidate,
                evidence_store,
                dump_id="filed",
                module="Module 1",
                received_on=date(2026, 1, 2),
            )

            self.assertEqual(store.sweep_unfiled(root, evidence_store), store.SweepReport(0, 0))


if __name__ == "__main__":
    unittest.main()
