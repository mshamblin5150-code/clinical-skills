"""The shared walk never follows links and reports incomplete directory reads."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tree_walk
from prose_bind import NAMING, bind


class TreeWalkTests(unittest.TestCase):
    def test_declared_boundary_is_named(self):
        self.assertEqual((), bind(tree_walk.DECLARED_LIMITS, tree_walk.__doc__, mode=NAMING))

    def test_symbolic_links_are_counted_without_reading_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "real").mkdir()
            target = root / "real" / "file.txt"
            target.touch()
            try:
                (root / "ancestor").symlink_to(root, target_is_directory=True)
                (root / "dangling").symlink_to(root / "absent", target_is_directory=True)
                (root / "file-link").symlink_to(target)
            except OSError as error:
                self.skipTest(str(error))
            report = tree_walk.walk_files(root)
            self.assertEqual(report.files, (target,))
            self.assertEqual(report.links_not_entered, 3)
            self.assertEqual(report.unreadable_directories, 0)

    def test_deep_failure_is_counted_and_siblings_are_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            denied = root / "denied"
            denied.mkdir()
            reached = root / "reached.txt"
            reached.touch()
            scandir = os.scandir

            def read(path):
                if Path(path) == denied:
                    raise PermissionError("private directory")
                return scandir(path)

            with mock.patch("tree_walk.os.scandir", side_effect=read):
                report = tree_walk.walk_files(root)
            self.assertEqual(report.files, (reached,))
            self.assertEqual(report.unreadable_directories, 1)
            self.assertEqual(report.links_not_entered, 0)
            with mock.patch("tree_walk.os.scandir", side_effect=PermissionError):
                with self.assertRaises(PermissionError):
                    tree_walk.walk_files(root)

    @unittest.skipUnless(os.name == "nt", "Windows junctions")
    def test_live_dangling_and_ancestor_junctions_are_not_entered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real"
            real.mkdir()
            reached = real / "reached.txt"
            reached.touch()
            for name, target in (("live", real), ("dangling", root / "absent"), ("ancestor", root)):
                result = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / name), str(target)], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            report = tree_walk.walk_files(root)
            self.assertEqual(report.files, (reached,))
            self.assertEqual(report.links_not_entered, 3)
            self.assertEqual(report.unreadable_directories, 0)

    @unittest.skipUnless(os.name == "nt", "Windows reparse attributes")
    def test_python_310_fallback_recognizes_a_junction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            junction = root / "junction"
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(root / "absent")], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with mock.patch.object(os.path, "isjunction", None, create=True):
                self.assertTrue(tree_walk.is_link(junction))

