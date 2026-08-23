"""Behavior tests for content-addressed guideline builds."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import guidelines_build
import artifact_lock
import artifact_provenance


class BuildCommandCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "guidelines-src"
        self.source.mkdir()
        self.pdf = self.source / "one.pdf"
        self.pdf.write_bytes(b"synthetic guideline bytes")
        self.catalog_root = self.root / "builds"
        self.text_alias = self.root / "guidelines-text"
        self.index_alias = self.root / "guidelines-index" / "guidelines.sqlite"
        self.launches: list[str] = []
        self.stdout = io.StringIO()
        self.producer = {"commit": "a" * 40, "dirty": False}

    @property
    def arguments(self) -> list[str]:
        return [
            str(self.source),
            "--catalog-root",
            str(self.catalog_root),
            "--text-alias",
            str(self.text_alias),
            "--index-alias",
            str(self.index_alias),
        ]

    def produce(self, command: list[str], **_: object) -> mock.Mock:
        script = Path(command[1]).name
        self.launches.append(script)
        if script == "guidelines_extract.py":
            out = Path(command[command.index("--out") + 1])
            out.mkdir(parents=True, exist_ok=True)
            (out / "one.txt").write_text(
                self.pdf.read_bytes().hex(), encoding="utf-8"
            )
            (out / "manifest.json").write_text(
                json.dumps(
                    {
                        "producer": self.producer,
                        "documents": [
                            {
                                "doc_id": "one",
                                "society": None,
                                "title": None,
                                "source": "one.pdf",
                                "output": "one.txt",
                                "document_class": "unknown",
                                "pages": 1,
                                "boilerplate": [],
                                "margin_stripped": [],
                                "error": None,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
        elif script == "guidelines_index.py":
            database = Path(command[3])
            database.parent.mkdir(parents=True, exist_ok=True)
            with contextlib.closing(sqlite3.connect(database)) as connection:
                connection.execute("CREATE TABLE meta (key TEXT, value TEXT)")
                connection.execute(
                    "INSERT INTO meta VALUES ('text', ?)",
                    ((Path(command[2]) / "one.txt").read_text(encoding="utf-8"),),
                )
                connection.execute(
                    "INSERT INTO meta VALUES ('provenance', ?)",
                    (
                        json.dumps(
                            {
                                "producer": self.producer,
                                "source": self.producer,
                                "untrusted_reasons": [],
                            }
                        ),
                    ),
                )
                connection.commit()
        else:  # pragma: no cover - a failed assertion explains this branch
            self.fail(f"unexpected producer: {script}")
        return mock.Mock(returncode=0, stdout="", stderr="")

    def run_command(self, *, producer: dict[str, str | bool] | None = None) -> int:
        with (
            mock.patch("guidelines_build.subprocess.run", side_effect=self.produce),
            mock.patch(
                "guidelines_build.artifact_provenance.current_producer",
                return_value=producer or self.producer,
            ),
            contextlib.redirect_stdout(self.stdout),
        ):
            return guidelines_build.main(self.arguments)


class ReusingAnIdenticalBuild(BuildCommandCase):
    def test_the_second_cli_run_does_not_launch_either_producer(self):
        self.assertEqual(self.run_command(), 0)
        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches, ["guidelines_extract.py", "guidelines_index.py"]
        )
        self.assertIn("extraction  BUILT", self.stdout.getvalue())
        self.assertIn("extraction  REUSED", self.stdout.getvalue())
        self.assertIn("index       BUILT", self.stdout.getvalue())
        self.assertIn("index       REUSED", self.stdout.getvalue())


class SeparatingDifferentInputs(BuildCommandCase):
    def test_a_source_change_gets_new_extraction_and_index_builds(self):
        self.assertEqual(self.run_command(), 0)
        self.pdf.write_bytes(b"different synthetic guideline bytes")

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_extract.py",
                "guidelines_index.py",
            ],
        )
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(catalog["artifacts"]["extraction"]), 2)
        self.assertEqual(len(catalog["artifacts"]["index"]), 2)

    def test_an_extractor_runtime_change_rebuilds_both_stages(self):
        with mock.patch("guidelines_build._package_version", return_value="engine-one"):
            self.assertEqual(self.run_command(), 0)
        with mock.patch("guidelines_build._package_version", return_value="engine-two"):
            self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_extract.py",
                "guidelines_index.py",
            ],
        )

    def test_an_index_runtime_change_rebuilds_only_the_index(self):
        self.assertEqual(self.run_command(), 0)
        with mock.patch.object(
            guidelines_build.sqlite3, "sqlite_version", "different-sqlite"
        ):
            self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_index.py",
            ],
        )

    def test_index_only_producer_changes_do_not_rekey_extraction(self):
        extraction_files = {
            row["path"] for row in guidelines_build.extraction_identity(self.source)[
                "producer_files"
            ]
        }
        index_files = {
            row["path"]
            for row in guidelines_build.index_identity(
                guidelines_build.SelectedArtifact(
                    "extraction", "key", self.source, True, ()
                )
            )["producer_files"]
        }

        self.assertIn("tools/guidelines_manifest.py", extraction_files)
        self.assertNotIn("tools/guidelines_index_artifact.py", extraction_files)
        self.assertIn("tools/guidelines_index_artifact.py", index_files)
        self.assertIn("tools/guidelines_manifest.py", index_files)

    def test_both_cache_keys_are_derived_from_the_shared_identity_table(self):
        identities = {
            "extraction": ("tools/extraction-sentinel.py",),
            "index": ("tools/index-sentinel.py",),
        }
        selected = guidelines_build.SelectedArtifact(
            "extraction", "key", self.source, True, ()
        )
        with (
            mock.patch.object(artifact_provenance, "CACHE_IDENTITY", identities),
            mock.patch.object(
                guidelines_build, "_code_inputs", return_value=()
            ) as code_inputs,
        ):
            guidelines_build.extraction_identity(self.source)
            guidelines_build.index_identity(selected)

        self.assertEqual(
            code_inputs.call_args_list,
            [
                mock.call("tools/extraction-sentinel.py"),
                mock.call("tools/index-sentinel.py"),
            ],
        )

    def test_extraction_stamping_is_owned_by_the_manifest_module(self):
        import guidelines_manifest

        self.assertIs(guidelines_build.stamp_manifest, guidelines_manifest.stamp)

    def test_index_identity_includes_extracted_content_not_commit_lineage(self):
        self.assertEqual(self.run_command(), 0)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        extraction_row = next(iter(catalog["artifacts"]["extraction"].values()))
        extraction_path = Path(extraction_row["path"])
        record = json.loads(
            (extraction_path / "artifact.json").read_text(encoding="utf-8")
        )
        selected = guidelines_build.SelectedArtifact(
            "extraction",
            record["key"],
            extraction_path,
            True,
            tuple(record["files"]),
        )
        before = guidelines_build.index_identity(selected)
        manifest_path = extraction_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["producer"]["commit"] = "b" * 40
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        lineage_only = guidelines_build.index_identity(selected)
        (extraction_path / "one.txt").write_text("changed content", encoding="utf-8")
        content_changed = guidelines_build.SelectedArtifact(
            selected.kind,
            selected.key,
            selected.path,
            selected.reused,
            guidelines_build._files(selected.path),
        )

        self.assertEqual(
            before["extraction_inventory"], lineage_only["extraction_inventory"]
        )
        self.assertNotEqual(
            before["extraction_inventory"],
            guidelines_build.index_identity(content_changed)["extraction_inventory"],
        )


class PreservingContentAddressedTrust(BuildCommandCase):
    def test_cached_artifacts_remain_trusted_on_an_unrelated_commit(self):
        self.assertEqual(self.run_command(), 0)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        extraction = Path(
            next(iter(catalog["artifacts"]["extraction"].values()))["path"]
        )
        index = Path(next(iter(catalog["artifacts"]["index"].values()))["path"])
        manifest = json.loads(
            (extraction / "manifest.json").read_text(encoding="utf-8")
        )
        with contextlib.closing(
            sqlite3.connect(index / "guidelines.sqlite")
        ) as connection:
            provenance = json.loads(
                connection.execute(
                    "SELECT value FROM meta WHERE key = 'provenance'"
                ).fetchone()[0]
            )

        extraction_floor = set(artifact_provenance.TRUST_FLOOR["extraction"])
        index_floor = set(artifact_provenance.TRUST_FLOOR["index"])
        self.assertEqual(
            {row["path"] for row in manifest["producer"]["inputs"]},
            extraction_floor,
        )
        self.assertEqual(
            {row["path"] for row in provenance["producer"]["inputs"]},
            index_floor,
        )
        self.assertEqual(
            {row["path"] for row in provenance["source"]["inputs"]},
            extraction_floor,
        )
        self.assertTrue(
            artifact_provenance.check_producer(
                manifest["producer"],
                extraction / "manifest.json",
                expected_commit="b" * 40,
                unchanged_paths=("tools/guidelines_extract.py",),
            ).trusted
        )
        self.assertTrue(
            artifact_provenance.check_derived(
                provenance, index / "guidelines.sqlite"
            ).trusted
        )
        mismatched = copy.deepcopy(manifest["producer"])
        mismatched["inputs"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance,
            "producer inputs do not match",
        ):
            artifact_provenance.check_producer(
                mismatched,
                extraction / "manifest.json",
                expected_commit="b" * 40,
                unchanged_paths=("tools/guidelines_extract.py",),
            )


class RecoveringInterruptedRegistration(BuildCommandCase):
    def test_a_complete_orphan_is_registered_without_rebuilding(self):
        real_replace = guidelines_build.os.replace
        interrupted = False

        def stop_catalog_write(source: Path, destination: Path) -> None:
            nonlocal interrupted
            if Path(destination).name == "catalog.json" and not interrupted:
                interrupted = True
                raise OSError("simulated interruption")
            real_replace(source, destination)

        with (
            mock.patch("guidelines_build.os.replace", side_effect=stop_catalog_write),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(self.run_command(), 2)

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches, ["guidelines_extract.py", "guidelines_index.py"]
        )
        self.assertEqual(
            list(self.catalog_root.glob(".catalog.json.*.building")), []
        )
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(catalog["artifacts"]["extraction"]), 1)


class TrustingDirtyConsumersButNotPublishers(BuildCommandCase):
    def test_a_dirty_checkout_reuses_a_hit_and_refuses_a_miss(self):
        self.assertEqual(self.run_command(), 0)
        dirty = {"commit": "a" * 40, "dirty": True}

        self.assertEqual(self.run_command(producer=dirty), 0)
        self.pdf.write_bytes(b"a cache miss from dirty code")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_command(producer=dirty), 2)

        self.assertEqual(
            self.launches, ["guidelines_extract.py", "guidelines_index.py"]
        )
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(catalog["artifacts"]["extraction"]), 1)
        self.assertEqual(len(catalog["artifacts"]["index"]), 1)

    def test_a_dirty_checkout_does_not_register_a_clean_orphan(self):
        self.assertEqual(self.run_command(), 0)
        catalog_path = self.catalog_root / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["artifacts"]["extraction"] = {}
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        dirty = {"commit": "a" * 40, "dirty": True}

        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_command(producer=dirty), 2)

        repaired = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(repaired["artifacts"]["extraction"], {})
        self.assertEqual(
            self.launches, ["guidelines_extract.py", "guidelines_index.py"]
        )

    def test_a_dirty_orphan_is_not_adopted_as_a_trusted_build(self):
        self.assertEqual(self.run_command(), 0)
        catalog_path = self.catalog_root / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        key, extraction_row = next(
            iter(catalog["artifacts"]["extraction"].items())
        )
        artifact_record = Path(extraction_row["path"]) / "artifact.json"
        record = json.loads(artifact_record.read_text(encoding="utf-8"))
        record["producer"]["dirty"] = True
        artifact_record.write_text(json.dumps(record), encoding="utf-8")
        del catalog["artifacts"]["extraction"][key]
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_extract.py",
            ],
        )


class RecoveringAMissingArtifact(BuildCommandCase):
    def test_a_catalog_row_with_no_artifact_is_rebuilt(self):
        self.assertEqual(self.run_command(), 0)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        extraction_row = next(iter(catalog["artifacts"]["extraction"].values()))
        shutil.rmtree(Path(extraction_row["path"]))

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_extract.py",
            ],
        )
        repaired = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        repaired_row = next(iter(repaired["artifacts"]["extraction"].values()))
        self.assertTrue(Path(repaired_row["path"]).is_dir())


class RejectingADamagedArtifact(BuildCommandCase):
    def test_a_hash_mismatch_is_quarantined_and_rebuilt(self):
        next_commit = {"commit": "b" * 40, "dirty": False}
        self.assertEqual(self.run_command(producer=next_commit), 0)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        extraction_row = next(iter(catalog["artifacts"]["extraction"].values()))
        (Path(extraction_row["path"]) / "one.txt").write_text(
            "tampered", encoding="utf-8"
        )

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches,
            [
                "guidelines_extract.py",
                "guidelines_index.py",
                "guidelines_extract.py",
            ],
        )
        quarantined = list((self.catalog_root / "quarantine").iterdir())
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(
            (quarantined[0] / "one.txt").read_text(encoding="utf-8"),
            "tampered",
        )


class RefusingConcurrentOwnership(BuildCommandCase):
    def test_a_catalog_writer_makes_the_command_exit_with_retry_context(self):
        catalog = self.catalog_root / "catalog.json"
        stderr = io.StringIO()

        with (
            artifact_lock.hold(catalog, "another catalog writer"),
            contextlib.redirect_stderr(stderr),
        ):
            self.assertEqual(self.run_command(), 2)

        self.assertEqual(self.launches, [])
        self.assertIn("retry after that task finishes", stderr.getvalue())


class CleaningIncompleteBuilds(BuildCommandCase):
    def test_a_verified_hit_removes_an_incomplete_sibling(self):
        self.assertEqual(self.run_command(), 0)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        key = next(iter(catalog["artifacts"]["extraction"]))
        partial = (
            self.catalog_root
            / "artifacts"
            / "extraction"
            / f".{key}.interrupted.building"
        )
        partial.mkdir()

        self.assertEqual(self.run_command(), 0)

        self.assertFalse(partial.exists())


class DetectingSourceChangesDuringProduction(BuildCommandCase):
    def test_a_source_change_during_extraction_is_not_registered(self):
        original = self.produce

        def changing_source(command: list[str], **options: object) -> mock.Mock:
            result = original(command, **options)
            if Path(command[1]).name == "guidelines_extract.py":
                self.pdf.write_bytes(b"changed while extraction was running")
            return result

        stderr = io.StringIO()
        with (
            mock.patch(
                "guidelines_build.subprocess.run", side_effect=changing_source
            ),
            mock.patch(
                "guidelines_build.artifact_provenance.current_producer",
                return_value=self.producer,
            ),
            contextlib.redirect_stdout(self.stdout),
            contextlib.redirect_stderr(stderr),
        ):
            self.assertEqual(guidelines_build.main(self.arguments), 2)

        self.assertIn("source files changed during extraction", stderr.getvalue())
        self.assertFalse((self.catalog_root / "catalog.json").exists())


class RunningCompetingCommands(BuildCommandCase):
    def test_competing_hits_leave_one_valid_catalog(self):
        self.assertEqual(self.run_command(), 0)
        command = [
            sys.executable,
            str(Path(guidelines_build.__file__)),
            *self.arguments,
        ]
        processes = [
            subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for _ in range(2)
        ]
        completed = [process.communicate(timeout=20) for process in processes]
        statuses = [process.returncode for process in processes]

        self.assertTrue(any(status == 0 for status in statuses), completed)
        self.assertTrue(all(status in {0, 2} for status in statuses), completed)
        catalog = json.loads(
            (self.catalog_root / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(catalog["artifacts"]["extraction"]), 1)
        self.assertEqual(len(catalog["artifacts"]["index"]), 1)
        self.assertEqual(list(self.catalog_root.glob("*.building")), [])

    def test_a_competing_artifact_writer_prevents_duplicate_work(self):
        identity = guidelines_build.extraction_identity(self.source)
        key = guidelines_build.identity_key(identity)
        destination = self.catalog_root / "artifacts" / "extraction" / key
        stderr = io.StringIO()

        with (
            artifact_lock.hold(destination, "another extraction writer"),
            contextlib.redirect_stderr(stderr),
        ):
            self.assertEqual(self.run_command(), 2)

        self.assertEqual(self.launches, [])
        self.assertIn("retry after that task finishes", stderr.getvalue())


class RecoveringInterruptedAliasPublication(BuildCommandCase):
    def test_a_rerun_repairs_the_alias_without_rebuilding(self):
        real_replace = guidelines_build.os.replace
        interrupted = False

        def stop_alias_write(source: Path, destination: Path) -> None:
            nonlocal interrupted
            if (
                Path(destination).name == self.text_alias.name
                and not interrupted
            ):
                interrupted = True
                raise OSError("simulated alias interruption")
            real_replace(source, destination)

        with (
            mock.patch("guidelines_build.os.replace", side_effect=stop_alias_write),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(self.run_command(), 2)

        self.assertEqual(self.run_command(), 0)

        self.assertEqual(
            self.launches, ["guidelines_extract.py", "guidelines_index.py"]
        )
        self.assertTrue((self.text_alias / "one.txt").is_file())
        self.assertEqual(
            list(self.root.glob(".guidelines-text.*.building")), []
        )
        self.assertEqual(
            list(self.root.glob(".guidelines-text.*.previous")), []
        )

if __name__ == "__main__":
    unittest.main()
