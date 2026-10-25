"""Synthetic contracts for diagnostic classification and bounded receipts."""

import artifact_lock_test_support
import copy
import io
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

import ci_diagnostics as diagnostics
import suite


def edited():
    return {
        "action": "edited", "number": 7, "repository": {"id": 10},
        "changes": {"title": {"from": "old"}},
        "pull_request": {
            "number": 7,
            "head": {"sha": "a" * 40, "repo": {"id": 11}},
            "base": {"sha": "b" * 40, "repo": {"id": 10}},
            "merge_commit_sha": "c" * 40,
        },
    }


def identity():
    return {
        "checkout_sha": "c" * 40, "event_sha": "c" * 40,
        "head_sha": "a" * 40, "base_sha": "b" * 40, "merge_sha": "c" * 40,
        "checkout_parents": ["b" * 40, "a" * 40], "workflow_sha": "d" * 40,
        "workflow_digest": "e" * 64, "suite_digest": "f" * 64,
        "diagnostics_digest": "a" * 64, "run_id": 123, "attempt": 1,
        "event": "pull_request", "job_role": "suite", "python_release": "3.14.0",
        "python_implementation": "CPython", "os": "Windows", "architecture": "AMD64",
    }


def classify(event, name, attempt):
    return diagnostics.classify_event(event, name, attempt, identity())


class Classifier(unittest.TestCase):
    def test_only_strict_metadata_edits_are_candidates(self):
        for changes in ({"title": {"from": ""}}, {"body": {"from": "old"}},
                        {"title": {"from": "old"}, "body": {"from": ""}}):
            with self.subTest(changes=changes):
                event = edited()
                event["changes"] = changes
                self.assertEqual(classify(event, "pull_request", "1"), "CANDIDATE")

    def test_unknown_empty_and_malformed_changes_are_full(self):
        for changes in (None, {}, [], "title", {"base": {"ref": {"from": "main"}}},
                        {"unknown": {"from": "x"}}, {"body": {"from": None}},
                        {"title": {}}, {"title": {"from": 1}}, {"title": "old"},
                        {"title": {"from": "x", "extra": 1}},
                        {"title": {"from": "x"}, "base": {}}):
            with self.subTest(changes=changes):
                event = edited()
                event["changes"] = changes
                self.assertEqual(classify(event, "pull_request", "1"), "FULL")

    def test_all_other_triggers_and_reruns_are_full(self):
        for name, attempt in (("push", "1"), ("workflow_dispatch", "1"),
                              ("pull_request_target", "1"), ("pull_request", "2"),
                              ("pull_request", None), ("pull_request", 1)):
            self.assertEqual(classify(edited(), name, attempt), "FULL")
        for action in (None, "opened", "synchronize", "reopened", "closed"):
            event = edited()
            event["action"] = action
            self.assertEqual(classify(event, "pull_request", "1"), "FULL")

    def test_incomplete_or_inconsistent_identity_is_full(self):
        original = edited()
        for field in original:
            event = copy.deepcopy(original)
            del event[field]
            self.assertEqual(classify(event, "pull_request", "1"), "FULL")
        for key, value in (("number", True), ("number", 8), ("head", None),
                           ("base", {}), ("merge_commit_sha", None)):
            event = edited()
            event["pull_request"][key] = value
            self.assertEqual(classify(event, "pull_request", "1"), "FULL")
        for side in ("head", "base"):
            for field, value in (("sha", "short"), ("repo", {"id": True}), ("repo", None)):
                event = edited()
                event["pull_request"][side][field] = value
                self.assertEqual(classify(event, "pull_request", "1"), "FULL")
        event = edited()
        event["pull_request"]["base"]["repo"]["id"] = 99
        self.assertEqual(classify(event, "pull_request", "1"), "FULL")
        for event in (None, [], "text"):
            self.assertEqual(classify(event, "pull_request", "1"), "FULL")

    def test_missing_or_changed_checkout_run_and_workflow_identity_is_full(self):
        for field in identity():
            with self.subTest(field=field):
                value = identity()
                del value[field]
                self.assertEqual(diagnostics.classify_event(edited(), "pull_request", "1", value), "FULL")
                for malformed in (None, [], {}, "", True, 0):
                    value = identity()
                    value[field] = malformed
                    self.assertEqual(diagnostics.classify_event(edited(), "pull_request", "1", value), "FULL")
        for field, changed in (("checkout_sha", "f" * 40), ("event_sha", "f" * 40),
                               ("checkout_parents", ["a" * 40, "b" * 40]),
                               ("run_id", True), ("attempt", True)):
            value = identity()
            value[field] = changed
            self.assertEqual(diagnostics.classify_event(edited(), "pull_request", "1", value), "FULL")
        self.assertEqual(diagnostics.classify_event(edited(), "pull_request", "1"), "FULL")


class Receipts(unittest.TestCase):
    def test_event_reads_missing_truncated_oversize_and_nonobject_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.json"
            self.assertEqual(diagnostics.read_event(path), {})
            for raw in (b'{"action":', b'[]', b'"text"', b'{"changes":{},"changes":{}}',
                        b'x' * (diagnostics.MAX_EVENT_BYTES + 1)):
                path.write_bytes(raw)
                self.assertEqual(diagnostics.read_event(path), {})
            path.write_text(json.dumps(edited()), encoding="utf-8")
            self.assertEqual(diagnostics.read_event(path), edited())

    def test_byte_cap_is_enforced_before_writing(self):
        raw = diagnostics.encode_receipt({"text": "x" * (diagnostics.MAX_BYTES - 12)})
        self.assertLessEqual(len(raw), diagnostics.MAX_BYTES)
        with self.assertRaises(ValueError):
            diagnostics.encode_receipt({"text": "x" * diagnostics.MAX_BYTES})
        with self.assertRaises(ValueError):
            diagnostics.encode_receipt({"number": float("nan")})

    def test_only_allowlisted_provenance_and_fixed_summary_are_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = edited()
            event["changes"]["title"]["from"] = "DO-NOT-RETAIN"
            event_path = root / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            env = {"CI_DIAGNOSTIC_RECEIPT": str(root / "receipt.json"),
                   "GITHUB_EVENT_PATH": str(event_path), "GITHUB_EVENT_NAME": "pull_request",
                   "GITHUB_RUN_ATTEMPT": "1", "GITHUB_RUN_ID": "123", "GITHUB_JOB": "suite",
                   "GITHUB_STEP_SUMMARY": str(root / "summary.md"),
                   "SECRET": "DO-NOT-RETAIN", "ImageVersion": "C:/private/path"}
            with mock.patch.object(diagnostics, "_git_sha", return_value=None):
                diagnostics.write_receipt({"exit_code": 1, "discovered": 2, "unaccounted": 0}, env=env)
            raw = (root / "receipt.json").read_bytes()
            receipt = json.loads(raw)
            self.assertLessEqual(len(raw), diagnostics.MAX_BYTES)
            self.assertEqual(receipt["schema_version"], 1)
            self.assertEqual(receipt["classification"], "FULL")
            self.assertIsNone(receipt["provenance"]["checkout_sha"])
            self.assertIsNone(receipt["provenance"]["hosted_image_version"])
            self.assertEqual(receipt["provenance"]["attempt"], 1)
            self.assertEqual(receipt["provenance"]["base_sha"], "b" * 40)
            self.assertNotIn(b"DO-NOT-RETAIN", raw)
            self.assertNotIn(str(root), raw.decode())
            self.assertIn("Suite exit: 1", (root / "summary.md").read_text())

    def test_oversize_receipt_refuses_before_creating_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "receipt.json"
            with mock.patch.object(diagnostics, "MAX_BYTES", 1), \
                    mock.patch.object(diagnostics, "provenance", return_value=identity()):
                with self.assertRaises(ValueError):
                    diagnostics.write_receipt({}, env={"CI_DIAGNOSTIC_RECEIPT": str(target)})
            self.assertFalse(target.exists())

    def test_absent_opt_in_never_reads_provenance(self):
        with mock.patch.object(diagnostics, "provenance") as probe:
            diagnostics.write_receipt({}, env={})
        probe.assert_not_called()


class SuiteReceiptSeam(unittest.TestCase):
    def run_synthetic(self, sources, writer=None, jobs=1):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in sources:
                (root / f"test_{uuid.uuid4().hex}.py").write_text(source, encoding="utf-8")
            stream = io.StringIO()
            with mock.patch.object(diagnostics, "write_receipt", side_effect=writer) as receipt:
                status = suite.run_suite(root, jobs=jobs, slowest=0, scratch=root / "absent",
                                         stream=stream, diagnostics=True)
            return status, receipt.call_args.args[0], stream.getvalue()

    def test_success_failure_loader_fixture_and_empty_population(self):
        passing = "import unittest\nclass Example(unittest.TestCase):\n    def test_yes(self): pass\n"
        failing = passing.replace("pass\n", "self.fail('synthetic')\n")
        fixture = passing.replace("    def test_yes", "    @classmethod\n    def tearDownClass(cls): raise RuntimeError('synthetic')\n    def test_yes")
        cases = (([passing], 0, True, 0, 0), ([failing], 1, True, 0, 0),
                 (["raise RuntimeError('synthetic')"], 2, False, 1, 0),
                 ([fixture], 1, True, 0, 1), ([], 2, False, 0, 0),
                 ([failing, "raise RuntimeError('synthetic')"], 1, False, 1, 0))
        for sources, expected, complete, loader, fixtures in cases:
            with self.subTest(expected=expected, sources=sources):
                status, receipt, output = self.run_synthetic(sources)
                self.assertEqual(status, expected, output)
                self.assertEqual(receipt["exit_code"], status)
                self.assertEqual(receipt["full_suite_execution"], complete)
                self.assertEqual(receipt["loader_failures"], loader)
                self.assertEqual(receipt["fixture_failures"], fixtures)
                self.assertEqual(receipt["actual_workers"], 1)
                self.assertLessEqual(len(receipt["top_classes"]), 5)
                self.assertEqual(len(receipt["population_sha256"]), 64)

    def test_receipt_failure_preserves_suite_verdict_and_stdout(self):
        source = "import unittest\nclass Example(unittest.TestCase):\n    def test_yes(self): self.fail('synthetic')\n"
        with mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
            status, receipt, output = self.run_synthetic([source], writer=OSError("SECRET"))
        self.assertEqual(status, 1)
        self.assertIn("unaccounted: 0", output)
        self.assertEqual(errors.getvalue(), "CI diagnostic receipt unavailable\n")

    def test_duplicate_accounting_is_not_reported_as_a_complete_execution(self):
        source = ("import unittest\nclass Example(unittest.TestCase):\n"
                  "    def id(self): return 'same.id'\n"
                  "    def test_one(self): pass\n    def test_two(self): pass\n")
        status, receipt, output = self.run_synthetic([source])
        self.assertEqual(status, 2, output)
        self.assertFalse(receipt["full_suite_execution"])
        self.assertEqual(receipt["unaccounted"], 1)
        self.assertEqual(receipt["duplicate_discovered_ids"], 1)
        self.assertEqual(receipt["duplicate_worker_ids"], 1)

    def test_missing_worker_is_incomplete_and_requested_workers_are_not_actual(self):
        source = "import unittest\nclass Example(unittest.TestCase):\n    def test_yes(self): pass\n"
        with mock.patch.object(suite, "_parallel", return_value=((), ("synthetic missing worker",))):
            status, receipt, output = self.run_synthetic([source], jobs=8)
        self.assertEqual(status, 2, output)
        self.assertEqual(receipt["requested_workers"], 8)
        self.assertEqual(receipt["actual_workers"], 1)
        self.assertEqual(receipt["reporting_workers"], 0)
        self.assertEqual(receipt["missing_workers"], 1)
        self.assertFalse(receipt["full_suite_execution"])

    def test_top_class_timings_are_bounded_and_do_not_include_names(self):
        source = "import unittest\n" + "".join(
            f"class Example{i}(unittest.TestCase):\n    def test_yes(self): pass\n"
            for i in range(8)
        )
        status, receipt, output = self.run_synthetic([source])
        self.assertEqual(status, 0, output)
        self.assertEqual(len(receipt["top_classes"]), 5)
        self.assertEqual(receipt["outcomes"], {"pass": 8, "failure": 0, "error": 0, "skip": 0})
        self.assertNotIn("Example", json.dumps(receipt))
        for item in receipt["top_classes"]:
            self.assertEqual(len(item["class_sha256"]), 64)
            self.assertGreaterEqual(item["elapsed_seconds"], 0)

    def test_successful_multiworker_receipt_uses_real_report_accounting_and_top_five(self):
        source = "import unittest\n" + "".join(
            f"class Example{i}(unittest.TestCase):\n    def test_yes(self): pass\n"
            for i in range(8)
        )

        def reports(assignments):
            return tuple(
                suite.WorkerReport(
                    tuple(suite.Outcome(test.id(), suite.OutcomeKind.PASS)
                          for unit in assignment for test in unit.tests),
                    tuple((unit.name, float(unit.order + 1)) for unit in assignment),
                    50.0,
                ) for assignment in assignments
            ), ()

        with mock.patch.object(suite, "_parallel", side_effect=reports):
            status, receipt, output = self.run_synthetic([source], jobs=2)
        self.assertEqual(status, 0, output)
        self.assertTrue(receipt["full_suite_execution"])
        self.assertEqual(receipt["actual_workers"], 2)
        self.assertEqual(receipt["reporting_workers"], 2)
        self.assertEqual(receipt["unaccounted"], 0)
        self.assertEqual([item["elapsed_seconds"] for item in receipt["top_classes"]],
                         [8.0, 7.0, 6.0, 5.0, 4.0])


class WorkflowDiagnostics(unittest.TestCase):
    def test_each_existing_job_keeps_full_suite_and_receipt_is_not_a_gate(self):
        import test_ci_workflow as workflow
        text = workflow.workflow_text()
        for role in ("suite", "canary", "floor"):
            job = workflow.job_text(text, role)
            self.assertEqual(job.count("python tools/suite.py"), 1)
            self.assertIn("fetch-depth: 0", job)
            self.assertIn(f"CI_DIAGNOSTIC_RECEIPT: ${{{{ runner.temp }}}}/ci-{role}.json", job)
            self.assertIn(f"name: ci-diagnostic-{role}-${{{{ github.run_id }}}}-${{{{ github.run_attempt }}}}", job)
            self.assertIn("retention-days: 3", job)
            self.assertIn("if-no-files-found: warn", job)
            upload = job.partition("- name: Diagnostic receipt")[2]
            self.assertIn("if: always()", upload)
            self.assertNotIn("--jobs", job)
            self.assertNotIn("CANDIDATE", job)
        self.assertNotIn("cancel-in-progress", text)
