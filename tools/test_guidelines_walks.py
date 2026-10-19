"""Corpus boundaries reach every ADR 0432 guideline walk and public refuser."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import guidelines_build as build
import guidelines_extract as extract
import guidelines_index as index
import guidelines_manifest as manifest
import guidelines_recs as recs
import split_census
from tree_walk_test_support import denied_listing, junctions


class CorpusWalkTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "corpus"
        self.root.mkdir()
        (self.root / "manifest.json").write_text("[]", encoding="utf-8")
        self.destination = self.base / "destination"
        self.destination.mkdir()

    def walks(self):
        return {
            "build inventory": lambda: build._files(self.root, "*.pdf"),
            "extract corpus": lambda: extract._run(
                argparse.Namespace(jobs=1, quiet=True), self.root, self.destination
            ),
            "orphan outputs": lambda: extract.orphaned_outputs(self.root, []),
            "index sources": lambda: index._sources(self.root),
            "manifest": lambda: manifest._read_locked(
                self.root, allow_untrusted_provenance=True,
                expected_commit=None, verify_provenance=False,
            ),
            "recommendation sweep": lambda: recs.build_sweep(
                self.root, self.destination, {"commit": "fixture", "dirty": False}
            ),
            "reader comparison": lambda: recs.compare_reader_corpus(self.root),
            "split census": lambda: split_census._pdfs(self.root),
        }

    def assert_walk_boundaries(self, links):
        # No PDF or text exists outside the excluded boundaries. An empty result
        # protects against reading a linked society, even when its target is live.
        for name, run in self.walks().items():
            with self.subTest(walk=name), contextlib.redirect_stdout(io.StringIO()) as out:
                with mock.patch.object(extract.pdf_engine, "engine_version", return_value="fixture"):
                    if name == "extract corpus":
                        with self.assertRaisesRegex(SystemExit, "no PDFs"):
                            run()
                    else:
                        result = run()
                        if name == "manifest":
                            self.assertFalse(result.problems)
                            self.assertEqual(result.documents, {})
                        elif name == "reader comparison":
                            self.assertEqual(result, (0, 0, 0))
                        elif name != "recommendation sweep":
                            self.assertFalse(result)
                self.assertIn(f"links not entered {links}", out.getvalue())

    def test_every_walk_prints_zero_links(self):
        self.assert_walk_boundaries(0)

    def test_every_walk_excludes_symbolic_link_mutants(self):
        target = self.base / "linked-society"
        target.mkdir()
        (target / "hidden.pdf").write_bytes(b"invented PDF fixture")
        (target / "hidden.txt").write_text("invented prose", encoding="utf-8")
        try:
            (self.root / "live").symlink_to(target, target_is_directory=True)
            (self.root / "dangling").symlink_to(self.base / "absent", target_is_directory=True)
            (self.root / "ancestor").symlink_to(self.root, target_is_directory=True)
        except OSError as failure:
            self.skipTest(str(failure))
        self.assert_walk_boundaries(3)

    def test_every_walk_excludes_native_junctions(self):
        target = self.base / "linked-society"
        target.mkdir()
        (target / "hidden.pdf").write_bytes(b"invented PDF fixture")
        (target / "hidden.txt").write_text("invented prose", encoding="utf-8")
        junctions(self.root, target)
        self.assert_walk_boundaries(3)

    def assert_successful_commands_exclude_links(self):
        (self.root / "one.pdf").write_bytes(b"invented ordinary PDF")
        (self.root / "one.txt").write_text("invented ordinary prose", encoding="utf-8")
        record = manifest.Record(doc_id="one", source="one.pdf", output="one.txt", pages=1)
        (self.root / "manifest.json").write_text(
            json.dumps([manifest.serialize_record(record)]), encoding="utf-8"
        )

        def extract_pdf(job):
            self.assertEqual(job[1], Path("one.pdf"))
            return record

        def compare_pdf(path, doc_id):
            self.assertEqual(path, self.root / "one.pdf")
            self.assertEqual(doc_id, "one")
            return 1, 1, 0

        def scan_pdf(path):
            self.assertEqual(Path(path), self.root / "one.pdf")
            return split_census.Census()

        commands = {
            "extract": lambda: extract.main([
                str(self.root), "--out", str(self.destination), "--jobs", "1", "--quiet"
            ]),
            "index": lambda: index.main([
                str(self.root), str(self.base / "index.sqlite"), "--allow-untrusted-provenance"
            ]),
            "recommendation comparison": lambda: recs.main([str(self.root), "--compare-readers"]),
            "split census": lambda: split_census.main([str(self.root), "--jobs", "1"]),
        }
        for name, run in commands.items():
            with self.subTest(command=name), contextlib.ExitStack() as stack:
                out = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                stack.enter_context(mock.patch.object(extract.pdf_engine, "engine_version", return_value="fixture"))
                stack.enter_context(mock.patch.object(extract, "_extract_one", side_effect=extract_pdf))
                stack.enter_context(mock.patch.object(extract, "_engine_version", return_value="fixture"))
                stack.enter_context(mock.patch.object(recs, "compare_marker_readers", side_effect=compare_pdf))
                stack.enter_context(mock.patch.object(split_census, "_scan_document", side_effect=scan_pdf))
                self.assertEqual(run(), 0)
                self.assertIn("links not entered 3", out.getvalue())

    def test_successful_public_commands_exclude_native_junctions(self):
        target = self.base / "linked-society"
        target.mkdir()
        (target / "hidden.pdf").write_bytes(b"invented linked PDF")
        (target / "hidden.txt").write_text("invented linked prose", encoding="utf-8")
        junctions(self.root, target)
        self.assert_successful_commands_exclude_links()

    def test_successful_public_commands_exclude_symbolic_link_mutants(self):
        target = self.base / "linked-society"
        target.mkdir()
        (target / "hidden.pdf").write_bytes(b"invented linked PDF")
        (target / "hidden.txt").write_text("invented linked prose", encoding="utf-8")
        try:
            (self.root / "live").symlink_to(target, target_is_directory=True)
            (self.root / "dangling").symlink_to(self.base / "absent", target_is_directory=True)
            (self.root / "ancestor").symlink_to(self.root, target_is_directory=True)
        except OSError as failure:
            self.skipTest(str(failure))
        self.assert_successful_commands_exclude_links()

    def assert_refusers(self):
        commands = {
            "build": lambda: build.main([
                str(self.root), "--catalog-root", str(self.base / "builds"), "--no-recs"
            ]),
            "extract": lambda: extract.main([
                str(self.root), "--out", str(self.destination), "--jobs", "1"
            ]),
            "index": lambda: index.main([
                str(self.root), str(self.base / "index.sqlite"), "--allow-untrusted-provenance"
            ]),
            "recommendation comparison": lambda: recs.main([str(self.root), "--compare-readers"]),
            "split census": lambda: split_census.main([str(self.root)]),
        }
        for name, run in commands.items():
            with self.subTest(command=name), contextlib.ExitStack() as stack:
                out, err = io.StringIO(), io.StringIO()
                stack.enter_context(contextlib.redirect_stdout(out))
                stack.enter_context(contextlib.redirect_stderr(err))
                stack.enter_context(mock.patch.object(extract.pdf_engine, "engine_version", return_value="fixture"))
                stack.enter_context(mock.patch.object(build.artifact_provenance, "current_producer", return_value={"commit": "fixture", "dirty": False}))
                self.assertEqual(run(), 2)
                self.assertIn("subfolders unreadable: 1", err.getvalue())
                self.assertNotIn("private-society", err.getvalue())
                self.assertIn("links not entered 0", out.getvalue())
        # The manifest is a shared reader rather than a command; its strict
        # interface refuses and its tolerant interface returns an explicit problem.
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "subfolders unreadable: 1"):
                manifest.read_or_raise(self.root, expected_commit="fixture")

    def test_public_refusers_exit_two_for_an_unlisted_society(self):
        denied = self.root / "private-society"
        denied.mkdir()
        scandir = os.scandir

        def read(path):
            if Path(path) == denied:
                raise PermissionError("private-society must not be printed")
            return scandir(path)

        with mock.patch("tree_walk.os.scandir", side_effect=read):
            self.assert_refusers()

    def test_public_refusers_exit_two_for_native_directory_denial(self):
        denied = self.root / "private-society"
        denied.mkdir()
        with denied_listing(denied):
            self.assert_refusers()

    def test_manifest_never_reads_a_document_through_a_linked_society(self):
        target = self.root / "ordinary-society"
        target.mkdir()
        (target / "hidden.txt").write_text("invented prose", encoding="utf-8")
        try:
            (self.root / "linked").symlink_to(target, target_is_directory=True)
        except OSError as failure:
            self.skipTest(str(failure))
        record = manifest.Record(
            doc_id="linked/hidden", source="linked/hidden.pdf",
            output="linked/hidden.txt", pages=1,
        )
        (self.root / "manifest.json").write_text(
            json.dumps([manifest.serialize_record(record)]), encoding="utf-8"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            result = manifest._read_locked(
                self.root, allow_untrusted_provenance=True,
                expected_commit=None, verify_provenance=False,
            )
        self.assertEqual(result.pages, {})
        self.assertTrue(any("extracted text is missing" in problem.message for problem in result.problems))
