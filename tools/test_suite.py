"""The suite runner accounts for isolated ``test*.py`` populations. Issue #874."""

from __future__ import annotations

import io
import json
import os
import re
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

import suite
import run_grader


class SuiteRunControls(unittest.TestCase):
    def run_tree(self, source: str | None, *, jobs: int = 1, slowest: int = 0):
        return self.run_sources(
            [] if source is None else [source], jobs=jobs, slowest=slowest
        )

    def run_sources(self, sources: list[str], *, jobs: int = 1, slowest: int = 0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            return self.run_at(
                root, sources, root / "absent-scratch", jobs=jobs, slowest=slowest
            )

    def run_at(
        self,
        root: Path,
        sources: list[str],
        scratch: Path,
        *,
        jobs: int = 1,
        slowest: int = 0,
    ):
        for source in sources:
            module = root / f"test_{uuid.uuid4().hex}.py"
            module.write_text(source, encoding="utf-8")
        stream = io.StringIO()
        status = suite.run_suite(
            root,
            jobs=jobs,
            slowest=slowest,
            scratch=scratch,
            stream=stream,
        )
        return status, stream.getvalue()

    def test_a_clean_tree_is_complete_and_passing(self):
        status, report = self.run_tree(
            "import unittest\n"
            "class Passing(unittest.TestCase):\n"
            "    def test_yes(self):\n"
            "        self.assertTrue(True)\n"
        )

        self.assertEqual(status, 0)
        self.assertIn("discovered: 1", report)
        self.assertIn("unaccounted: 0", report)

    def test_a_failing_test_exits_one_with_its_rerun_line(self):
        status, report = self.run_tree(
            "import unittest\n"
            "class Failing(unittest.TestCase):\n"
            "    def test_no(self):\n"
            "        self.fail('broken')\n"
        )

        self.assertEqual(status, 1)
        self.assertRegex(
            report,
            r"re-run \(from tools/\): python -m unittest test_[^.]+\.Failing\.test_no",
        )

    def test_an_empty_tree_is_incomplete(self):
        status, report = self.run_tree(None)

        self.assertEqual(status, 2)
        self.assertIn("discovered: 0", report)
        self.assertIn("unaccounted: 0", report)

    def test_a_module_that_does_not_import_is_incomplete_and_named(self):
        status, report = self.run_tree("raise RuntimeError('cannot import')\n")

        self.assertEqual(status, 2)
        self.assertRegex(report, r"module did not load: test_[0-9a-f]+")
        self.assertIn("unaccounted: 1", report)

    def test_a_test_failure_wins_beside_a_module_that_does_not_import(self):
        status, report = self.run_sources(
            [
                "raise RuntimeError('cannot import')\n",
                "import unittest\n"
                "class Failing(unittest.TestCase):\n"
                "    def test_no(self):\n"
                "        self.fail('broken')\n",
            ]
        )

        self.assertEqual(status, 1)
        self.assertRegex(report, r"module did not load: test_[0-9a-f]+")
        self.assertIn("unaccounted: 1", report)

    def test_a_duplicated_discovered_id_is_incomplete(self):
        status, report = self.run_tree(
            "import unittest\n"
            "class DuplicateId(unittest.TestCase):\n"
            "    def id(self):\n"
            "        return 'duplicate.id'\n"
            "    def test_one(self):\n"
            "        pass\n"
            "    def test_two(self):\n"
            "        pass\n"
        )

        self.assertEqual(status, 2)
        self.assertIn("duplicate id: duplicate.id", report)
        self.assertIn("unaccounted: 1", report)

    def test_jobs_one_runs_in_the_calling_process(self):
        status, report = self.run_tree(
            "import os\n"
            "import unittest\n"
            "class CallingProcess(unittest.TestCase):\n"
            "    def test_process_name(self):\n"
            f"        self.assertEqual(os.getpid(), {os.getpid()})\n",
            jobs=1,
        )

        self.assertEqual(status, 0, report)

    def test_parallel_jobs_run_whole_classes_in_workers(self):
        status, report = self.run_tree(
            "import multiprocessing\n"
            "import unittest\n"
            "class First(unittest.TestCase):\n"
            "    def test_worker(self):\n"
            "        self.assertNotEqual(multiprocessing.current_process().name, 'MainProcess')\n"
            "class Second(unittest.TestCase):\n"
            "    def test_worker(self):\n"
            "        self.assertNotEqual(multiprocessing.current_process().name, 'MainProcess')\n",
            jobs=2,
        )

        self.assertEqual(status, 0, report)

    def test_a_worker_killed_mid_run_is_incomplete(self):
        status, report = self.run_tree(
            "import os\n"
            "import unittest\n"
            "class Killed(unittest.TestCase):\n"
            "    def test_exit(self):\n"
            "        os._exit(7)\n",
            jobs=2,
        )

        self.assertEqual(status, 2)
        self.assertIn("ended without reporting", report)
        self.assertIn("unaccounted: 1", report)

    def test_a_complete_run_atomically_replaces_the_unit_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            (scratch / "runs").mkdir(parents=True)
            weights = scratch / "runs" / "suite-weights.json"
            weights.write_text('{"old.Unit": 99}', encoding="utf-8")

            status, report = self.run_at(
                root,
                [
                    "import unittest\n"
                    "class Passing(unittest.TestCase):\n"
                    "    def test_yes(self):\n"
                    "        pass\n"
                ],
                scratch,
            )

            self.assertEqual(status, 0, report)
            self.assertIn("weights: recorded", report)
            written = json.loads(weights.read_text(encoding="utf-8"))
            self.assertEqual(len(written), 1)
            self.assertRegex(next(iter(written)), r"test_[0-9a-f]+\.Passing")

    def test_an_absent_scratch_root_stays_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"

            status, report = self.run_at(
                root,
                [
                    "import unittest\n"
                    "class Passing(unittest.TestCase):\n"
                    "    def test_yes(self):\n"
                    "        pass\n"
                ],
                scratch,
            )

            self.assertEqual(status, 0, report)
            self.assertIn("weights: equal", report)
            self.assertFalse(scratch.exists())

    def test_an_incomplete_run_does_not_rewrite_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            (scratch / "runs").mkdir(parents=True)
            weights = scratch / "runs" / "suite-weights.json"
            original = '{"kept.Unit": 12}\n'
            weights.write_text(original, encoding="utf-8")

            status, report = self.run_at(
                root,
                ["raise RuntimeError('cannot import')\n"],
                scratch,
            )

            self.assertEqual(status, 2, report)
            self.assertEqual(weights.read_text(encoding="utf-8"), original)

    def test_a_unit_missing_from_recorded_weights_uses_the_recorded_mean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            (scratch / "runs").mkdir(parents=True)
            (scratch / "runs" / "suite-weights.json").write_text(
                json.dumps({"test_pack.Heavy": 100, "test_pack.Light": 10}),
                encoding="utf-8",
            )
            source = "import os\nimport time\nimport unittest\nfrom pathlib import Path\n"
            for name in ("Heavy", "Light", "Missing"):
                marker = root / name.lower()
                source += (
                    f"class {name}(unittest.TestCase):\n"
                    "    def test_worker(self):\n"
                    f"        Path({str(marker)!r}).write_text(str(os.getpid()), encoding='utf-8')\n"
                    "        time.sleep(0.2)\n"
                )
            (root / "test_pack.py").write_text(source, encoding="utf-8")

            stream = io.StringIO()
            status = suite.run_suite(
                root,
                jobs=2,
                slowest=0,
                scratch=scratch,
                stream=stream,
            )

            self.assertEqual(status, 0, stream.getvalue())
            self.assertEqual(
                (root / "missing").read_text(encoding="utf-8"),
                (root / "light").read_text(encoding="utf-8"),
            )
            self.assertNotEqual(
                (root / "missing").read_text(encoding="utf-8"),
                (root / "heavy").read_text(encoding="utf-8"),
            )

    def test_a_test_case_class_is_assigned_whole(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "class-fixture"
            source = (
                "import unittest\n"
                "from pathlib import Path\n"
                "class WholeClass(unittest.TestCase):\n"
                "    @classmethod\n"
                "    def setUpClass(cls):\n"
                f"        with Path({str(marker)!r}).open('a', encoding='utf-8') as handle:\n"
                "            handle.write('x')\n"
                "    def test_one(self):\n"
                "        pass\n"
                "    def test_two(self):\n"
                "        pass\n"
            )

            status, report = self.run_at(root, [source], root / "absent", jobs=2)

            self.assertEqual(status, 0, report)
            self.assertEqual(marker.read_text(encoding="utf-8"), "x")

    def test_the_parent_neither_sets_nor_removes_the_lock_root(self):
        with mock.patch.dict(
            os.environ, {"CLINICAL_SKILLS_LOCK_ROOT": "inherited-sentinel"}
        ):
            status, report = self.run_tree(
                "import os\n"
                "import unittest\n"
                "class LockRoot(unittest.TestCase):\n"
                "    def test_inherited(self):\n"
                "        self.assertEqual(os.environ.get('CLINICAL_SKILLS_LOCK_ROOT'), "
                "'inherited-sentinel')\n",
                jobs=2,
            )

        self.assertEqual(status, 0, report)

    def test_an_unexpected_worker_id_is_incomplete(self):
        status, report = self.run_tree(
            "import os\n"
            "import unittest\n"
            "class ProcessShapedId(unittest.TestCase):\n"
            "    def id(self):\n"
            f"        if os.getpid() == {os.getpid()}:\n"
            "            return super().id()\n"
            "        return 'id.' + str(os.getpid())\n"
            "    def test_yes(self):\n"
            "        pass\n",
            jobs=2,
        )

        self.assertEqual(status, 2)
        self.assertIn("unexpected id: id.", report)
        self.assertIn("unaccounted: 2", report)

    def test_a_duplicated_worker_id_is_incomplete(self):
        status, report = self.run_tree(
            "import os\n"
            "import unittest\n"
            "class ProcessId:\n"
            "    def id(self):\n"
            f"        if os.getpid() == {os.getpid()}:\n"
            "            return super().id()\n"
            "        return 'duplicate.worker.id'\n"
            "class First(ProcessId, unittest.TestCase):\n"
            "    def test_yes(self):\n"
            "        pass\n"
            "class Second(ProcessId, unittest.TestCase):\n"
            "    def test_yes(self):\n"
            "        pass\n",
            jobs=2,
        )

        self.assertEqual(status, 2)
        self.assertIn("duplicate worker id: duplicate.worker.id", report)

    def test_the_critical_path_and_requested_slowest_units_are_reported(self):
        status, report = self.run_tree(
            "import time\n"
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_wait(self):\n"
            "        time.sleep(0.001)\n"
            "class Slow(unittest.TestCase):\n"
            "    def test_wait(self):\n"
            "        time.sleep(0.03)\n",
            slowest=1,
        )

        self.assertEqual(status, 0, report)
        self.assertRegex(
            report,
            r"critical path \(this run's elapsed time\): test_[^.]+\.Slow ",
        )
        slow_rows = [line for line in report.splitlines() if line.startswith("slow unit:")]
        self.assertEqual(len(slow_rows), 1)
        self.assertIn(".Slow ", slow_rows[0])

    def test_a_units_measured_time_includes_its_class_fixture(self):
        status, report = self.run_tree(
            "import time\n"
            "import unittest\n"
            "class FixtureCost(unittest.TestCase):\n"
            "    @classmethod\n"
            "    def setUpClass(cls):\n"
            "        time.sleep(0.03)\n"
            "    def test_yes(self):\n"
            "        pass\n",
            slowest=1,
        )

        self.assertEqual(status, 0, report)
        match = re.search(r"slow unit: .*\.FixtureCost ([0-9.]+)s", report)
        self.assertIsNotNone(match, report)
        self.assertGreaterEqual(float(match.group(1)), 0.02)

    def test_a_class_fixture_error_has_a_resolvable_rerun_without_disturbing_accounting(self):
        status, report = self.run_tree(
            "import unittest\n"
            "class BrokenFixture(unittest.TestCase):\n"
            "    @classmethod\n"
            "    def tearDownClass(cls):\n"
            "        raise RuntimeError('fixture broke')\n"
            "    def test_yes(self):\n"
            "        pass\n"
        )

        self.assertEqual(status, 1)
        self.assertIn("unaccounted: 0", report)
        self.assertRegex(
            report,
            r"(?m)^re-run \(from tools/\): python -m unittest test_[^.]+\.BrokenFixture$",
        )


class DeclaredLimits(unittest.TestCase):
    def test_the_hang_and_discovery_population_are_declared(self):
        self.assertEqual(
            [row[2] for row in suite.DECLARED_LIMITS],
            [
                run_grader.EvidenceDisposition.DECLARED_READING,
                run_grader.EvidenceDisposition.BEHAVIOR,
            ],
        )

    def test_a_file_outside_test_star_py_is_outside_the_population(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_visible.py").write_text(
                "import unittest\n"
                "class Visible(unittest.TestCase):\n"
                "    def test_yes(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            (root / "hidden_check.py").write_text(
                "raise RuntimeError('must not load')\n",
                encoding="utf-8",
            )
            stream = io.StringIO()

            status = suite.run_suite(
                root,
                jobs=1,
                slowest=0,
                scratch=root / "absent",
                stream=stream,
            )

            self.assertEqual(status, 0, stream.getvalue())
            self.assertIn("discovered: 1", stream.getvalue())


class CommandInterface(unittest.TestCase):
    def test_the_default_job_count_is_three_quarters_of_the_cpu_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_clean.py").write_text(
                "import unittest\n"
                "class Clean(unittest.TestCase):\n"
                "    def test_yes(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            stream = io.StringIO()

            with mock.patch.object(suite.os, "cpu_count", return_value=8):
                status = suite.main(
                    [], module_dir=root, scratch=root / "absent", stream=stream
                )

            self.assertEqual(status, 0, stream.getvalue())
            self.assertIn(
                "jobs: 6 (max(1, (os.cpu_count() or 1) * 3 // 4); os.cpu_count()=8)",
                stream.getvalue(),
            )

    def test_test_names_and_shards_are_not_command_modes(self):
        for arguments in (["test_sample.Case.test_one"], ["--shard", "1/2"]):
            with self.subTest(arguments=arguments), self.assertRaises(SystemExit) as raised:
                suite.main(arguments)
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
