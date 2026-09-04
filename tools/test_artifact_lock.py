"""Behavioral contract for the shared artifact lock. ADR 0126."""

from __future__ import annotations

import ast
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import artifact_lock_test_support
import artifact_lock
from repo_root import InsideCheckout


SUITE_LOCK_ROOT = artifact_lock_test_support.LOCK_ROOT


@contextmanager
def operating_system_lock(path: Path):
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


class LockIdentityLayout(unittest.TestCase):
    def test_one_identity_is_scoped_under_the_overridden_root(self):
        artifact = SUITE_LOCK_ROOT.parent / "an-artifact"

        path = artifact_lock.lock_path(artifact)

        self.assertEqual(path.name, "lock")
        self.assertEqual(path.parent.parent, SUITE_LOCK_ROOT)
        self.assertEqual(len(path.parent.name), 64)

    def test_a_lock_bearing_test_module_installs_its_own_run_root(self):
        tools = Path(__file__).resolve().parent
        result = subprocess.run(
            [
                os.environ.get("PYTHON", "python"),
                "-c",
                (
                    "import os; "
                    "os.environ.pop('CLINICAL_SKILLS_LOCK_ROOT', None); "
                    "import test_guidelines; "
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

    def test_the_override_cannot_put_lock_state_inside_a_checkout(self):
        checkout_root = Path(__file__).resolve().parent.parent
        with mock.patch.dict(
            os.environ,
            {artifact_lock.LOCK_ROOT_ENVIRONMENT_VARIABLE: str(checkout_root / "locks")},
        ):
            with self.assertRaises(InsideCheckout):
                artifact_lock.lock_path(checkout_root / "artifact")

    def test_writer_acquires_scoped_and_legacy_layouts_during_rollout(self):
        artifact = SUITE_LOCK_ROOT.parent / "rollout-artifact"
        path = artifact_lock.lock_path(artifact)
        legacy = path.parent.parent / f"{path.parent.name}.lock"
        handoff = legacy.with_suffix(".gate")

        with artifact_lock.hold(artifact, "build during rollout") as held:
            self.assertEqual(held, path)
            self.assertTrue(path.is_file())
            self.assertTrue(legacy.is_file())
            self.assertTrue(handoff.is_file())
            self.assertFalse((path.parent / "handoff").exists())

        self.assertTrue(path.parent.is_dir())

    def test_reader_advertises_in_both_layouts_and_cleans_up(self):
        artifact = SUITE_LOCK_ROOT.parent / "reader-artifact"
        path = artifact_lock.lock_path(artifact)
        legacy_pattern = f"{path.parent.name}.reader.*"

        with artifact_lock.hold(artifact, "read during rollout", mode="read"):
            self.assertEqual(len(tuple(path.parent.glob("reader.*"))), 1)
            self.assertEqual(len(tuple(path.parent.parent.glob(legacy_pattern))), 1)

        self.assertEqual(tuple(path.parent.glob("reader.*")), ())
        self.assertEqual(tuple(path.parent.parent.glob(legacy_pattern)), ())


class LockExclusion(unittest.TestCase):
    def test_an_active_reader_excludes_a_writer(self):
        artifact = SUITE_LOCK_ROOT.parent / "reader-excludes-writer"

        with artifact_lock.hold(artifact, "active read", mode="read"):
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(artifact, "overlapping write"):
                    self.fail("the writer overlapped an active reader")

    def test_a_legacy_reader_excludes_a_new_writer(self):
        artifact = SUITE_LOCK_ROOT.parent / "legacy-reader"
        path = artifact_lock.lock_path(artifact)
        path.parent.mkdir(parents=True, exist_ok=True)
        legacy_reader = path.parent.parent / f"{path.parent.name}.reader.fixture"

        with operating_system_lock(legacy_reader):
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(artifact, "new writer"):
                    self.fail("the new writer overlapped a legacy reader")

    def test_a_legacy_writer_excludes_a_new_reader(self):
        artifact = SUITE_LOCK_ROOT.parent / "legacy-writer"
        path = artifact_lock.lock_path(artifact)
        path.parent.mkdir(parents=True, exist_ok=True)
        legacy_writer = path.parent.parent / f"{path.parent.name}.lock"

        with operating_system_lock(legacy_writer):
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(artifact, "new reader", mode="read"):
                    self.fail("the new reader overlapped a legacy writer")


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
    def test_all_three_unguarded_properties_carry_a_key_and_reason(self):
        self.assertEqual(len(artifact_lock.NOT_GUARDED), 3)
        for key, reason in artifact_lock.NOT_GUARDED:
            self.assertTrue(key.strip())
            self.assertGreater(len(reason.split()), 12, key)

    def test_the_module_and_maintainer_prose_point_at_the_owned_object(self):
        self.assertIn("NOT_GUARDED", artifact_lock.__doc__)
        claude = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("artifact_lock.NOT_GUARDED", claude)


class CompatibilityRetirementTripwire(unittest.TestCase):
    def test_a_registered_worktree_still_needs_the_legacy_bridge(self):
        checkout = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=checkout,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        roots = tuple(
            Path(line.removeprefix("worktree ")).resolve()
            for line in result.stdout.splitlines()
            if line.startswith("worktree ")
        )
        self.assertTrue(roots, "git reported no registered worktrees")
        if len(roots) == 1:
            self.skipTest("one checkout has no local rollout window")

        scoped_marker = 'return lock_root() / digest / "lock"'
        legacy = []
        for root in roots:
            try:
                source = (root / "tools" / "artifact_lock.py").read_text(encoding="utf-8")
            except OSError:
                legacy.append(root)
                continue
            if scoped_marker not in source:
                legacy.append(root)

        self.assertTrue(
            legacy,
            "Every registered worktree carries the scoped artifact-lock layout. "
            "Implement #877 now: retire all three compatibility limbs together, "
            "switch to the scoped handoff file, and remove this tripwire.",
        )


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
                ("_legacy_reader_paths", "root", "pattern"),
                ("_hold_write", "scoped_record_path.parent", "'reader.*'"),
            ],
            "Only the declared non-Windows legacy fallback and one identity-scoped "
            "reader walk may enumerate; #877 removes the fallback with the bridge.",
        )


if __name__ == "__main__":
    unittest.main()
