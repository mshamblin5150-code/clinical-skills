"""Behavioral contract for the shared artifact lock. ADR 0126."""

from __future__ import annotations

import ast
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support
import artifact_lock
from repo_root import InsideCheckout


SUITE_LOCK_ROOT = artifact_lock_test_support.LOCK_ROOT


class LockIdentityLayout(unittest.TestCase):
    def test_every_lock_bearing_test_module_reaches_the_shared_bootstrap(self):
        tools = Path(__file__).resolve().parent
        sources = {path.stem: path for path in tools.glob("*.py")}
        imports = {}
        for name, path in sources.items():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            imports[name] = imported & sources.keys()

        def reaches(start: str, target: str, seen: set[str] | None = None) -> bool:
            if start == target:
                return True
            visited = set() if seen is None else seen
            if start in visited:
                return False
            visited.add(start)
            return any(reaches(name, target, visited) for name in imports[start])

        lock_bearing = sorted(
            name
            for name in sources
            if name.startswith("test_") and reaches(name, "artifact_lock")
        )
        missing = [
            name
            for name in lock_bearing
            if not reaches(name, "artifact_lock_test_support")
        ]
        self.assertEqual(
            missing,
            [],
            "Every focused lock-bearing test run needs one private inherited root.",
        )

    def test_one_identity_is_scoped_under_the_overridden_root(self):
        artifact = SUITE_LOCK_ROOT.parent / "an-artifact"

        scoped_record_path = artifact_lock.lock_path(artifact)

        self.assertEqual(scoped_record_path.name, "lock")
        self.assertEqual(scoped_record_path.parent.parent, SUITE_LOCK_ROOT)
        self.assertEqual(len(scoped_record_path.parent.name), 64)

    def test_a_lock_bearing_test_module_installs_its_own_run_root(self):
        tools = Path(__file__).resolve().parent
        for module in (
            "test_guidelines",
            "test_threshold_draft",
            "test_uspstf_table",
        ):
            with self.subTest(module=module):
                result = subprocess.run(
                    [
                        os.environ.get("PYTHON", "python"),
                        "-c",
                        (
                            "import importlib, os; "
                            "os.environ.pop('CLINICAL_SKILLS_LOCK_ROOT', None); "
                            f"importlib.import_module('{module}'); "
                            "print(os.environ.get('CLINICAL_SKILLS_LOCK_ROOT', ''))"
                        ),
                    ],
                    cwd=tools,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_a_lock_bearing_test_module_preserves_an_inherited_run_root(self):
        tools = Path(__file__).resolve().parent
        inherited_root = SUITE_LOCK_ROOT.parent / "inherited-lock-root"
        result = subprocess.run(
            [
                os.environ.get("PYTHON", "python"),
                "-c",
                (
                    "import test_guidelines; "
                    "import os; "
                    "print(os.environ['CLINICAL_SKILLS_LOCK_ROOT'])"
                ),
            ],
            cwd=tools,
            env={
                **os.environ,
                artifact_lock.LOCK_ROOT_ENVIRONMENT_VARIABLE: str(inherited_root),
            },
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()), inherited_root)

    def test_package_style_lock_bearing_modules_install_the_run_root(self):
        checkout = Path(__file__).resolve().parent.parent
        for module in (
            "tools.test_artifact_provenance",
            "tools.test_guidelines_recs",
            "tools.test_threshold_coverage",
        ):
            with self.subTest(module=module):
                result = subprocess.run(
                    [
                        os.environ.get("PYTHON", "python"),
                        "-c",
                        (
                            "import importlib, os; "
                            "os.environ.pop('CLINICAL_SKILLS_LOCK_ROOT', None); "
                            f"importlib.import_module('{module}'); "
                            "print(os.environ.get('CLINICAL_SKILLS_LOCK_ROOT', ''))"
                        ),
                    ],
                    cwd=checkout,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_the_override_cannot_put_lock_state_inside_a_checkout(self):
        checkout_root = Path(__file__).resolve().parent.parent
        with mock.patch.dict(
            os.environ,
            {artifact_lock.LOCK_ROOT_ENVIRONMENT_VARIABLE: str(checkout_root / "locks")},
        ):
            with self.assertRaises(InsideCheckout):
                artifact_lock.lock_path(checkout_root / "artifact")

    def test_writer_uses_only_the_scoped_layout(self):
        artifact = SUITE_LOCK_ROOT.parent / "scoped-artifact"
        scoped_record_path = artifact_lock.lock_path(artifact)
        legacy = (
            scoped_record_path.parent.parent
            / f"{scoped_record_path.parent.name}.lock"
        )
        legacy_handoff = legacy.with_suffix(".gate")
        scoped_handoff = scoped_record_path.parent / "handoff"

        with artifact_lock.hold(artifact, "scoped build") as held:
            self.assertEqual(held, scoped_record_path)
            self.assertTrue(scoped_record_path.is_file())
            self.assertTrue(scoped_handoff.is_file())
            self.assertFalse(legacy.exists())
            self.assertFalse(legacy_handoff.exists())

        self.assertTrue(scoped_record_path.parent.is_dir())

    def test_reader_advertises_only_in_the_scoped_layout_and_cleans_up(self):
        artifact = SUITE_LOCK_ROOT.parent / "reader-artifact"
        scoped_record_path = artifact_lock.lock_path(artifact)
        legacy_pattern = f"{scoped_record_path.parent.name}.reader.*"

        with artifact_lock.hold(artifact, "scoped read", mode="read"):
            self.assertEqual(
                len(tuple(scoped_record_path.parent.glob("reader.*"))), 1
            )
            self.assertEqual(
                tuple(scoped_record_path.parent.parent.glob(legacy_pattern)), ()
            )

        self.assertEqual(tuple(scoped_record_path.parent.glob("reader.*")), ())


class LockExclusion(unittest.TestCase):
    def test_an_active_reader_excludes_a_writer(self):
        artifact = SUITE_LOCK_ROOT.parent / "reader-excludes-writer"

        with artifact_lock.hold(artifact, "active read", mode="read"):
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(artifact, "overlapping write"):
                    self.fail("the writer overlapped an active reader")

class AcquisitionCost(unittest.TestCase):
    def _enumerated_entries(self, junk_entries: int) -> int:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            lock_root = root / "locks"
            lock_root.mkdir()
            for index in range(junk_entries):
                (lock_root / f"junk-{index}").touch()

            enumerated = 0
            real_scandir = os.scandir

            class CountedScandir:
                def __init__(self, path):
                    self._entries = real_scandir(path)

                def __enter__(self):
                    return self

                def __exit__(self, *exc):
                    self._entries.close()

                def __iter__(self):
                    nonlocal enumerated
                    for entry in self._entries:
                        enumerated += 1
                        yield entry

            with (
                mock.patch.dict(
                    os.environ,
                    {artifact_lock.LOCK_ROOT_ENVIRONMENT_VARIABLE: str(lock_root)},
                ),
                mock.patch.object(os, "scandir", CountedScandir),
                artifact_lock.hold(root / "artifact", "cost probe"),
            ):
                pass
            return enumerated

    def test_acquisition_enumerates_the_same_entries_after_unrelated_identities_accumulate(self):
        self.assertEqual(self._enumerated_entries(0), self._enumerated_entries(5_000))


class DeclaredLimits(unittest.TestCase):
    def test_both_unguarded_properties_carry_a_key_and_reason(self):
        self.assertEqual(len(artifact_lock.NOT_GUARDED), 2)
        for key, reason in artifact_lock.NOT_GUARDED:
            self.assertTrue(key.strip())
            self.assertGreater(len(reason.split()), 12, key)

    def test_the_module_and_maintainer_prose_point_at_the_owned_object(self):
        self.assertIn("NOT_GUARDED", artifact_lock.__doc__)
        claude = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("artifact_lock.NOT_GUARDED", claude)


class SourceEnumerationFloor(unittest.TestCase):
    def test_every_python_directory_enumeration_is_named_and_bounded(self):
        source = Path(artifact_lock.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = []
        for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
            for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
                target = call.func
                if not isinstance(target, ast.Attribute):
                    continue
                if target.attr not in {"glob", "rglob", "iterdir", "scandir", "listdir"}:
                    continue
                found.append(
                    (
                        function.name,
                        ast.unparse(target.value),
                        ast.unparse(call.args[0]) if call.args else "",
                    )
                )

        self.assertEqual(
            found,
            [
                ("_hold_write", "scoped_record_path.parent", "'reader.*'"),
            ],
            "Only one identity-scoped reader walk may enumerate.",
        )


if __name__ == "__main__":
    unittest.main()
