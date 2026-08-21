"""Contract tests for the extracted-guideline manifest handoff."""

from __future__ import annotations

import dataclasses
import contextlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import guidelines_manifest as manifest
import guidelines_extract as extract


class ManifestSerializationTests(unittest.TestCase):
    def test_the_producer_uses_the_owned_record_and_filename(self):
        self.assertIs(extract.Record, manifest.Record)
        self.assertIs(extract.MANIFEST_NAME, manifest.MANIFEST_NAME)

    def test_the_declared_order_covers_every_record_field_exactly(self):
        self.assertEqual(
            set(manifest.SERIALISED_ORDER),
            {field.name for field in dataclasses.fields(manifest.Record)},
        )
        self.assertEqual(
            len(manifest.SERIALISED_ORDER),
            len(dataclasses.fields(manifest.Record)),
        )

    def test_a_record_keeps_the_existing_on_disk_key_order(self):
        record = manifest.Record(
            doc_id="USPSTF/screening",
            society="USPSTF",
            title="Screening",
            source="USPSTF/screening.pdf",
            output="USPSTF/screening.txt",
            document_class="recommendation-statement",
            pages=2,
            empty_pages=1,
            chars=12,
            chars_stripped=10,
            sampled_pages=2,
            codec="utf-8",
            boilerplate=["folio"],
            margin_patterns=["S#"],
            margin_stripped=["S1"],
            year_page_counts={"2024": 2},
            symbol_glyphs={"Symbol U+2265": 1},
            error=None,
        )

        rendered = json.dumps(manifest.serialize_record(record), ensure_ascii=False)

        self.assertEqual(
            rendered,
            '{"doc_id": "USPSTF/screening", "society": "USPSTF", '
            '"title": "Screening", "source": "USPSTF/screening.pdf", '
            '"output": "USPSTF/screening.txt", '
            '"document_class": "recommendation-statement", "pages": 2, '
            '"empty_pages": 1, "chars": 12, "chars_stripped": 10, '
            '"sampled_pages": 2, "codec": "utf-8", '
            '"boilerplate": ["folio"], "margin_patterns": ["S#"], '
            '"margin_stripped": ["S1"], "year_page_counts": {"2024": 2}, '
            '"symbol_glyphs": {"Symbol U+2265": 1}, "error": null}',
        )

    def test_reordering_the_declared_order_refuses_cache_invalidation(self):
        reordered = tuple(reversed(manifest.SERIALISED_ORDER))
        with mock.patch.object(manifest, "SERIALISED_ORDER", reordered):
            with self.assertRaisesRegex(ValueError, "cache invalidation"):
                manifest.serialize_record(manifest.Record(doc_id="USPSTF/screening"))

    def test_write_manifest_keeps_the_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(extract, "_engine_version", return_value="engine-test"):
                path = extract.write_manifest(
                    root,
                    [manifest.Record(doc_id="USPSTF/screening")],
                    Path("C:/outside/guidelines-src"),
                    producer={"commit": "f" * 40, "dirty": False},
                )

            expected = {
                "producer": {"commit": "f" * 40, "dirty": False},
                "source": str(Path("C:/outside/guidelines-src")),
                "codec": "utf-8",
                "engine": "engine-test",
                "boilerplate_threshold": 0.75,
                "minimum_occurrences": 3,
                "margin_lines": 2,
                "totals": {"documents": 1, "failures": 0, "pages": 0, "chars": 0},
                "documents": [manifest.serialize_record(manifest.Record(doc_id="USPSTF/screening"))],
            }
            expected_bytes = (json.dumps(expected, indent=2, ensure_ascii=False) + "\n").encode()
            self.assertEqual(path.read_bytes(), expected_bytes)


class ManifestReadingTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.provenance = mock.patch.object(
            manifest.artifact_provenance,
            "check_producer",
            return_value=mock.sentinel.provenance,
        )
        self.provenance.start()
        self.addCleanup(self.provenance.stop)

    def write(self, documents):
        (self.root / manifest.MANIFEST_NAME).write_text(
            json.dumps({"producer": {}, "documents": documents}),
            encoding="utf-8",
        )

    def entry(self, doc_id="Society/one", **changes):
        values = manifest.serialize_record(
            manifest.Record(
                doc_id=doc_id,
                society="Society",
                title="One",
                source=f"{doc_id}.pdf",
                output=f"{doc_id}.txt",
                document_class="guideline",
                pages=1,
            )
        )
        values.update(changes)
        return values

    def text(self, doc_id="Society/one", body="one page"):
        path = self.root / f"{doc_id}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def test_read_returns_valid_documents_and_each_invalid_problem(self):
        self.text()
        missing = self.entry("Society/two")
        del missing["title"]
        self.write([self.entry(), missing])

        result = manifest.read(self.root)

        self.assertEqual(set(result.documents), {"Society/one"})
        self.assertEqual(len(result.problems), 1)
        self.assertIn("title", result.problems[0].message)

    def test_read_checks_the_page_count_inside_the_handoff(self):
        self.text(body="page one\fpage two")
        self.write([self.entry(pages=1)])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertIn("2", result.problems[0].message)

    def test_read_resolves_before_it_takes_the_shared_lock(self):
        self.text()
        self.write([self.entry()])
        calls = []

        @contextlib.contextmanager
        def held(path, reason, *, mode="write"):
            calls.append((path, reason, mode))
            yield

        with mock.patch.object(manifest.artifact_lock, "hold", held):
            result = manifest.read(self.root / ".")

        self.assertEqual(result.root, self.root.resolve())
        self.assertEqual(calls[0][0], self.root.resolve())
        self.assertEqual(calls[0][2], "read")

    def test_read_turns_an_in_progress_artifact_into_a_problem(self):
        with mock.patch.object(
            manifest.artifact_lock,
            "hold",
            side_effect=manifest.artifact_lock.ArtifactBusy("rebuilding"),
        ):
            result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertIn("rebuilding", result.problems[0].message)

    def test_read_or_raise_refuses_any_problem(self):
        with self.assertRaisesRegex(ValueError, "manifest.json"):
            manifest.read_or_raise(self.root)


if __name__ == "__main__":
    unittest.main()
