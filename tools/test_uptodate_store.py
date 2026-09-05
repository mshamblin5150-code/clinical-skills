"""Behavior tests for the scratch-rooted UpToDate evidence store."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
        self.assertEqual((report.topics, report.candidates, report.unread), (1, 1, 0))
        self.assertEqual(
            store.search(self.store, "searchable result")[0].title,
            "Acute cervicitis",
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

    def test_duplicate_topic_titles_refuse_the_dump(self):
        source = self.write_dump(
            "evidence.txt", topic("Repeated topic") + "\n" + topic("Repeated topic")
        )
        with self.assertRaisesRegex(ValueError, "duplicate topic"):
            store.ingest_dump(
                source,
                self.store,
                dump_id="duplicates",
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
