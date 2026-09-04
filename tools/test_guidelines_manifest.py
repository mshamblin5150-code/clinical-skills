"""Contract tests for the extracted-guideline manifest handoff."""

from __future__ import annotations

import dataclasses
import contextlib
import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import guidelines_manifest as manifest
import guidelines_extract as extract


class ManifestSerializationTests(unittest.TestCase):
    def test_the_producer_uses_the_owned_record_and_filename(self):
        self.assertIs(extract.Record, manifest.Record)
        self.assertIs(extract.MANIFEST_NAME, manifest.MANIFEST_NAME)

    def test_the_declared_order_covers_every_record_field_exactly(self):
        self.assertEqual(
            set(manifest.SERIALIZED_ORDER),
            {field.name for field in dataclasses.fields(manifest.Record)},
        )
        self.assertEqual(
            len(manifest.SERIALIZED_ORDER),
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
            split_boundaries={"digit|digit": 1},
            quantity_split_shapes={"2024 -> 20|24": 1},
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
            '"symbol_glyphs": {"Symbol U+2265": 1}, '
            '"split_boundaries": {"digit|digit": 1}, '
            '"quantity_split_shapes": {"2024 -> 20|24": 1}, "error": null}',
        )

    def test_reordering_the_declared_order_refuses_cache_invalidation(self):
        reordered = tuple(reversed(manifest.SERIALIZED_ORDER))
        with mock.patch.object(manifest, "SERIALIZED_ORDER", reordered):
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

            inputs = manifest.artifact_provenance.producer_file_identity(
                manifest.artifact_provenance.TRUST_FLOOR["extraction"]
            )
            expected = {
                "producer": {
                    "commit": "f" * 40,
                    "dirty": False,
                    "inputs": inputs,
                },
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

    def test_the_extraction_writer_imports_the_shared_trust_floor(self):
        floors = {
            "extraction": ("tools/extraction-sentinel.py",),
            "index": ("tools/index-sentinel.py",),
        }
        inputs = [{"path": floors["extraction"][0], "sha256": "a" * 64}]
        with tempfile.TemporaryDirectory() as tmp:
            with (
                mock.patch.object(extract.artifact_provenance, "TRUST_FLOOR", floors),
                mock.patch.object(
                    extract.artifact_provenance,
                    "producer_file_identity",
                    return_value=inputs,
                ) as identity,
                mock.patch.object(extract, "_engine_version", return_value="engine-test"),
            ):
                extract.write_manifest(
                    Path(tmp),
                    [manifest.Record(doc_id="USPSTF/screening")],
                    Path("C:/outside/guidelines-src"),
                    producer={"commit": "f" * 40, "dirty": False},
                )

        identity.assert_called_once_with(floors["extraction"])


class ManifestOwnershipTests(unittest.TestCase):
    def test_only_the_owner_assigns_manifest_name(self):
        tools = Path(__file__).resolve().parent
        owners = []
        for path in tools.glob("*.py"):
            if path.name.startswith("test_"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), path)
            if any(
                isinstance(node, (ast.Assign, ast.AnnAssign))
                and any(
                    isinstance(target, ast.Name) and target.id == "MANIFEST_NAME"
                    for target in (
                        node.targets if isinstance(node, ast.Assign) else [node.target]
                    )
                )
                for node in ast.walk(tree)
            ):
                owners.append(path.name)
        self.assertEqual(owners, ["guidelines_manifest.py"])

    def test_every_lexically_visible_manifest_consumer_imports_the_owner(self):
        tools = Path(__file__).resolve().parent
        missing = {}
        for path in tools.glob("*.py"):
            if path.name.startswith("test_") or path.name == "guidelines_manifest.py":
                continue
            source = path.read_text(encoding="utf-8")
            if not any(token in source for token in manifest.DISCOVERY_CEILING):
                continue
            if path.name in manifest.NON_EXTRACTION_MANIFEST_OWNERS:
                continue
            tree = ast.parse(source, path)
            imports_owner = any(
                (isinstance(node, ast.Import) and any(alias.name == "guidelines_manifest" for alias in node.names))
                or (isinstance(node, ast.ImportFrom) and node.module == "guidelines_manifest")
                for node in ast.walk(tree)
            )
            if not imports_owner:
                missing[path.name] = manifest.NOT_MIGRATED.get(path.name)
        self.assertEqual(missing, manifest.NOT_MIGRATED)
        self.assertTrue(all(manifest.NOT_MIGRATED.values()))
        self.assertEqual(
            manifest.NON_EXTRACTION_MANIFEST_OWNERS,
            {"guidelines_recs.py": "recommendation sweep manifest"},
        )


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

    def test_the_reader_uses_the_shared_extraction_trust_floor(self):
        self.text()
        self.write([self.entry()])
        floors = {
            "extraction": ("tools/extraction-sentinel.py",),
            "index": ("tools/index-sentinel.py",),
        }
        with (
            mock.patch.object(manifest.artifact_provenance, "TRUST_FLOOR", floors),
            mock.patch.object(
                manifest.artifact_provenance,
                "check_producer",
                return_value=mock.sentinel.provenance,
            ) as check,
        ):
            manifest.read(self.root)

        self.assertEqual(check.call_args.kwargs["unchanged_paths"], floors["extraction"])

    def test_read_checks_the_page_count_inside_the_handoff(self):
        self.text(body="page one\fpage two")
        self.write([self.entry(pages=1)])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertIn("2", result.problems[0].message)

    def test_read_rejects_an_output_that_does_not_match_its_document_id(self):
        self.text("Society/wrong")
        self.write([self.entry(output="Society/wrong.txt")])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertTrue(
            any("must be Society/one.txt" in problem.message for problem in result.problems)
        )

    def test_read_rejects_an_output_outside_the_corpus(self):
        self.write([self.entry(output="../outside.txt")])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertTrue(
            any("must be Society/one.txt" in problem.message for problem in result.problems)
        )

    def test_read_rejects_matching_document_and_output_traversal(self):
        outside = self.root.parent / f"{self.root.name}-outside.txt"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        self.write([self.entry(doc_id="../outside", output="../outside.txt")])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertTrue(
            any("safe relative path" in problem.message for problem in result.problems)
        )

    def test_read_turns_a_malformed_field_type_into_a_problem(self):
        self.write([self.entry(output=["Society/one.txt"])])

        result = manifest.read(self.root)

        self.assertEqual(result.documents, {})
        self.assertEqual(len(result.problems), 1)
        self.assertIn("output must be", result.problems[0].message)

    def test_read_rejects_malformed_split_census_maps(self):
        self.text()
        for field in ("split_boundaries", "quantity_split_shapes"):
            with self.subTest(field=field):
                self.write([self.entry(**{field: {"shape": "one"}})])

                result = manifest.read(self.root)

                self.assertEqual(result.documents, {})
                self.assertTrue(
                    any(
                        f"{field} must map strings to integers" in problem.message
                        for problem in result.problems
                    )
                )

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
