"""Registry exception controls for real LiveRunner, not Windows ownership proof."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from measure_parallel_readers import (LiveRunner, OwnedCommands, Hold, corpus_preflight,
                                     exception_diagnostics, work_signature, inventory,
                                     reviewed_budget, BASE, CANDIDATE_HASH, sha)
from parallel_reader_diagnostics import child_failure_diagnostic
from parallel_reader_scheduler import Observation, run_schedule
import test_parallel_reader_controls as reader_controls
from test_parallel_reader_controls import Clock, control_case


LOCAL_CLEANUP_PROOF_EXECUTED = False


class OwnedFailure(RuntimeError):
    def __init__(self, owner):
        self.owner = owner


class FakeOwner:
    def __init__(self, failure):
        self.failure = failure
        self.live = True
        self.result = None
        self.cancel_calls = 0

    def poll(self):
        if self.failure == "poll":
            raise OwnedFailure(self)
        return SimpleNamespace(root_reaped=False, active_processes=1)

    def cancel(self, reason, timeout):
        self.cancel_calls += 1
        if self.failure == "cancel" and self.cancel_calls == 1:
            raise OwnedFailure(self)
        self.live = False
        self.result = SimpleNamespace(reason=reason, snapshot=SimpleNamespace(
            cleanup_verified=True, active_processes=0, root_reaped=True,
            wall_seconds=0.0, tree_cpu_seconds=0.0))
        return self.result


class FakeFactory:
    def __init__(self, failure):
        self.failure = failure
        self.created = []

    def start(self, argv, *, cwd, env, report_dir):
        owner = FakeOwner(self.failure)
        self.created.append(owner)
        if self.failure == "start":
            raise OwnedFailure(owner)
        return owner


class RegistryControls(unittest.TestCase):
    def synthetic_budget_plan(self, total_seconds):
        """Synthetic boundary input, never a reviewed estimate for publication."""
        return {"schema_version": 1, "status": "reviewed-complete-lazy-proof",
                "base": BASE, "candidate_sha256": CANDIDATE_HASH,
                "lazy_proof_complete": True, "all_lazy_controls_passed": True,
                "evidence_run_url": "https://github.com/mshamblin5150-code/clinical-skills/actions/runs/0",
                "per_pass_upper_seconds": total_seconds / 4 - 2,
                "clone_setup_upper_seconds": 1, "receipt_cleanup_upper_seconds": 1,
                "per_pass_retained_disk_upper_bytes": 1,
                "minimum_free_disk_reserve_bytes": 1024 ** 3}

    def test_reviewed_budget_accepts_four_pass_bounds_through_approved_130_minutes(self):
        for total in (6000, 7799, 7800):
            with self.subTest(total_seconds=total), control_case(prefix="synthetic-budget-boundary-") as name:
                plan = self.synthetic_budget_plan(total)
                raw = json.dumps(plan, sort_keys=True).encode("utf-8")
                path = Path(name) / "synthetic-budget.json"
                path.write_bytes(raw)
                try:
                    accepted = reviewed_budget(path, sha(raw))
                except Hold as error:
                    self.fail("approved measurement bound was refused: " + str(error))
                self.assertEqual(accepted, plan)

    def test_reviewed_budget_refuses_to_borrow_preflight_or_cleanup_reserve(self):
        for total in (7801, 8100, 9000):
            with self.subTest(total_seconds=total), control_case(prefix="synthetic-budget-overflow-") as name:
                raw = json.dumps(self.synthetic_budget_plan(total), sort_keys=True).encode("utf-8")
                path = Path(name) / "synthetic-budget.json"
                path.write_bytes(raw)
                with self.assertRaises(Hold) as caught:
                    reviewed_budget(path, sha(raw))
                self.assertEqual(str(caught.exception), "four_pass_budget_does_not_fit")

    def test_reviewed_budget_digest_tolerates_checkout_crlf_but_not_content_mutation(self):
        plan = self.synthetic_budget_plan(7800)
        lf = (json.dumps(plan, sort_keys=True, indent=2) + "\n").encode("utf-8")
        crlf = lf.replace(b"\n", b"\r\n")
        with control_case(prefix="synthetic-budget-line-endings-") as name:
            path = Path(name) / "synthetic-budget.json"
            with self.subTest(content="same reviewed JSON with checkout CRLF"):
                path.write_bytes(crlf)
                try:
                    accepted = reviewed_budget(path, sha(lf))
                except Hold as error:
                    self.fail("line-ending-only checkout change was refused: " + str(error))
                self.assertEqual(accepted, plan)
            with self.subTest(content="different JSON still refuses"):
                mutated = crlf.replace(b'"schema_version": 1', b'"schema_version": 2')
                self.assertNotEqual(mutated, crlf)
                path.write_bytes(mutated)
                with self.assertRaises(Hold) as caught:
                    reviewed_budget(path, sha(lf))
                self.assertEqual(str(caught.exception), "budget_plan_hash_mismatch")

    def test_source_only_150_minute_job_and_130_minute_measurement_authority_agree(self):
        """AST/text contract only, not evidence of hosted runtime duration."""
        root = Path(__file__).resolve().parent
        tree = ast.parse((root / "measure_parallel_readers.py").read_text(encoding="utf-8"))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        assignments = [(target.id, ast.dump(node.value)) for node in ast.walk(main)
                       if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)]
        for name, expression in (
                ("job_deadline", "started + max(0, 9000 - elapsed)"),
                ("preflight_deadline", "started + max(0, 900 - elapsed)"),
                ("measurement_deadline", "job_deadline - 300"),
                ("measurement_deadline", "min(measurement_deadline, time.monotonic() + 7800)")):
            with self.subTest(assignment=name, expression=expression):
                self.assertIn((name, ast.dump(ast.parse(expression, mode="eval").body)), assignments)
        qualified = next(node for node in ast.walk(main) if isinstance(node, ast.Call)
                         and isinstance(node.func, ast.Name) and node.func.id == "emit" and node.args
                         and isinstance(node.args[0], ast.Constant) and node.args[0].value == "qualified")
        fields = {item.arg: item.value.value for item in qualified.keywords if isinstance(item.value, ast.Constant)}
        for name, value in (("total_budget_seconds", 9000), ("preflight_budget_seconds", 900),
                            ("measurement_budget_seconds", 7800), ("cleanup_reserve_seconds", 300)):
            with self.subTest(receipt_field=name):
                self.assertEqual(fields.get(name), value)
        workflow = root / "ci-parallel-proof.yml"
        if not workflow.is_file():
            workflow = root.parent / ".github/workflows/ci-parallel-proof.yml"
        timeouts = [line.strip() for line in workflow.read_text(encoding="utf-8").splitlines()
                    if line.strip().startswith("timeout-minutes:")]
        # The old planner is retained as dormant source; the shared trigger now
        # funds only the separately approved replacement lazy qualification.
        self.assertEqual(timeouts, ["timeout-minutes: 10"])
        self.assertNotIn("python observer/diagnostics/diagnose_lazy_setup.py", workflow.read_text(encoding="utf-8"))
        self.assertNotIn("python observer/diagnostics/diagnose_staging_layout.py", workflow.read_text(encoding="utf-8"))
        self.assertNotIn("python observer/diagnostics/measure_maintainer_pair.py", workflow.read_text(encoding="utf-8"))
        self.assertIn("python observer/diagnostics/diagnose_generated_outputs.py", workflow.read_text(encoding="utf-8"))
        self.assertNotIn("python observer/diagnostics/measure_parallel_readers.py", workflow.read_text(encoding="utf-8"))

    def test_inventory_slow_read_cannot_cross_experiment_deadline_and_return_success(self):
        with control_case(prefix="synthetic-inventory-deadline-") as name:
            root = Path(name)
            (root / "synthetic.txt").write_text("synthetic", encoding="utf-8")
            clock = Clock()
            original = Path.read_bytes

            def slow_read(path):
                data = original(path)
                clock.tick = 2
                return data

            with patch("measure_parallel_readers.time.monotonic", side_effect=clock), patch.object(Path, "read_bytes", slow_read):
                with self.assertRaises(Hold, msg="a completed slow read must not authorize a late receipt") as caught:
                    inventory(root, deadline=1)
            self.assertEqual(str(caught.exception), "measurement_budget_expired")

    def check_local_cleanup_contract(self):
        global LOCAL_CLEANUP_PROOF_EXECUTED
        if reader_controls.CONTROL_EVIDENCE_ROOT is not None:
            return False
        with patch.object(reader_controls, "CONTROL_EVIDENCE_ROOT", None):
            with control_case(prefix="synthetic-local-case-") as local:
                local_path = Path(local)
                (local_path / "synthetic.txt").write_text("local synthetic", encoding="utf-8")
            self.assertFalse(local_path.exists())
        LOCAL_CLEANUP_PROOF_EXECUTED = True
        return True

    def test_hosted_control_cases_are_retained_while_local_cases_keep_normal_cleanup(self):
        with control_case(prefix="synthetic-control-retention-") as name:
            retained_root = Path(name) / "hosted-evidence"
            retained_root.mkdir()
            with patch.object(reader_controls, "CONTROL_EVIDENCE_ROOT", retained_root), patch.object(
                    reader_controls.tempfile, "TemporaryDirectory",
                    side_effect=AssertionError("hosted mode must not enter a destructive local context")):
                self.assertFalse(self.check_local_cleanup_contract())
            if reader_controls.CONTROL_EVIDENCE_ROOT is None:
                self.assertTrue(self.check_local_cleanup_contract())
            with patch.object(reader_controls, "CONTROL_EVIDENCE_ROOT", retained_root):
                with control_case(prefix="synthetic-hosted-case-") as hosted:
                    hosted_path = Path(hosted)
                    (hosted_path / "synthetic.txt").write_text("retained synthetic", encoding="utf-8")
                self.assertTrue(hosted_path.is_relative_to(retained_root))
                self.assertTrue((hosted_path / "synthetic.txt").is_file())

    def test_source_only_cli_policy_preludes_are_ordered_and_command_local(self):
        """AST source-shape check only, not a runtime codec/floor proof."""
        root = Path(__file__).resolve().parent
        for name in ("measure_parallel_readers.py", "test_parallel_reader_controls.py",
                     "test_parallel_observer_controls.py"):
            with self.subTest(command=name):
                tree = ast.parse((root / name).read_text(encoding="utf-8"))
                guards = [node for node in tree.body if isinstance(node, ast.If)
                          and ast.dump(node.test) == ast.dump(ast.parse('__name__ == "__main__"', mode="eval").body)]
                self.assertEqual(len(guards), 1)
                guard = guards[0]
                policy_imports = [node for node in guard.body if isinstance(node, ast.ImportFrom)
                                  and node.module == "console_codec"]
                self.assertEqual(len(policy_imports), 1, "CLI imports unchanged repository policy helpers")
                self.assertEqual({alias.name for alias in policy_imports[0].names},
                                 {"use_utf8", "require_python_floor"})
                policy_calls = [node for node in guard.body if isinstance(node, ast.Expr)
                                and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                                and node.value.func.id in ("use_utf8", "require_python_floor")]
                self.assertEqual([node.value.func.id for node in policy_calls], ["use_utf8", "require_python_floor"])
                floor_index = guard.body.index(policy_calls[1])
                for node in guard.body[:floor_index]:
                    self.assertIsInstance(node, (ast.Import, ast.ImportFrom, ast.Expr))
                    if isinstance(node, ast.Expr):
                        call = node.value
                        self.assertIsInstance(call, ast.Call)
                        self.assertTrue((isinstance(call.func, ast.Name) and call.func.id == "use_utf8")
                                        or ast.unparse(call.func) == "sys.path.insert")
                outside = ast.Module(body=[node for node in tree.body if node is not guard], type_ignores=[])
                self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                                     and node.func.id in ("use_utf8", "require_python_floor")
                                     for node in ast.walk(outside)))
                bootstrap = [node for node in guard.body if isinstance(node, ast.Expr)
                             and isinstance(node.value, ast.Call)
                             and ast.unparse(node.value.func) == "sys.path.insert"]
                self.assertEqual(len(bootstrap), 1)
                self.assertEqual(ast.dump(bootstrap[0].value.args[1]), ast.dump(ast.parse(
                    'str(Path(__file__).resolve().parent.parent / "tools")', mode="eval").body))

    def test_source_only_sparse_checkout_includes_unchanged_command_policy_dependencies(self):
        root = Path(__file__).resolve().parent
        workflow = root / "ci-parallel-proof.yml"
        if not workflow.is_file():
            workflow = root.parent / ".github/workflows/ci-parallel-proof.yml"
        source = workflow.read_text(encoding="utf-8")
        for path in ("/tools/console_codec.py", "/tools/python_floor.py", "/tools/git_paths.py"):
            with self.subTest(path=path):
                sparse_lines = source.splitlines()[source.splitlines().index("          sparse-checkout: |") + 1:]
                sparse_lines = sparse_lines[:next((index for index, line in enumerate(sparse_lines)
                                                  if line.strip() and not line.startswith("            ")), len(sparse_lines))]
                self.assertIn(path, [line.strip() for line in sparse_lines])

    def test_source_only_population_and_result_receipts_use_audit_owned_import_walk_limit(self):
        """Checks the recognized receipt source shapes, not emitted runtime JSON."""
        tree = ast.parse((Path(__file__).resolve().parent / "measure_parallel_readers.py").read_text(encoding="utf-8"))
        expected = ast.dump(ast.parse('audit.DECLARED_LIMITS["import walk"]', mode="eval").body)
        population = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "static_population")
        returned = next(node.value for node in ast.walk(population) if isinstance(node, ast.Return))
        self.assertIsInstance(returned, ast.Dict)
        self.assertTrue(any(isinstance(key, ast.Constant) and key.value == "import_walk_declared_limit"
                            and ast.dump(value) == expected for key, value in zip(returned.keys, returned.values)))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        records = [node.value for node in ast.walk(main) if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "record" for target in node.targets)]
        self.assertEqual(len(records), 1)
        self.assertTrue(any(isinstance(key, ast.Constant) and key.value == "import_walk_declared_limit"
                            and ast.dump(value) == expected for key, value in zip(records[0].keys, records[0].values)))
        complete = [node for node in ast.walk(main) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == "emit" and node.args
                    and isinstance(node.args[0], ast.Constant) and node.args[0].value == "screening_complete"]
        self.assertEqual(len(complete), 1)
        self.assertTrue(any(item.arg == "import_walk_declared_limit" and ast.dump(item.value) == expected
                            for item in complete[0].keywords))

    def test_work_signature_distinguishes_skips_and_expected_failures(self):
        ordinary = Observation("test_a", "icd10_lookup", "nonreader", test_count=2,
                               metadata={"skipped": 0, "expected_failures": 0})
        skipped = Observation("test_a", "icd10_lookup", "nonreader", test_count=2,
                              metadata={"skipped": 1, "expected_failures": 0})
        expected_failure = Observation("test_a", "icd10_lookup", "nonreader", test_count=2,
                                       metadata={"skipped": 0, "expected_failures": 1})
        self.assertNotEqual(work_signature([ordinary]), work_signature([skipped]))
        self.assertNotEqual(work_signature([ordinary]), work_signature([expected_failure]))

    def test_real_owner_failure_schema_preserves_reviewed_codes_and_frames(self):
        import windows_job_probe_controls as owner_controls
        from windows_job_probe import ProbeError

        with patch.object(owner_controls, "sys", SimpleNamespace(flags=SimpleNamespace(optimize=1))):
            try:
                owner_controls.require_unoptimized()
            except ProbeError as cause:
                error = ProbeError("JOB_LIST_ATTRIBUTE_FAILED",
                                   diagnostic_codes=("CONTROL_OPTIMIZATION_UNSUPPORTED",)).with_traceback(cause.__traceback__)
                receipt = owner_controls.failure_report(error)
        with control_case(prefix="synthetic-real-owner-schema-") as name:
            stdout = Path(name) / "stdout"
            stdout.write_text(json.dumps(receipt), encoding="utf-8")
            parsed = child_failure_diagnostic(SimpleNamespace(stdout_path=str(stdout),
                                              snapshot=SimpleNamespace(root_exit_code=2)))
        self.assertEqual(parsed["diagnostic_codes"], ["JOB_LIST_ATTRIBUTE_FAILED", "CONTROL_OPTIMIZATION_UNSUPPORTED"])
        self.assertTrue(parsed["source_frames"])
        self.assertEqual(parsed["source_frames"][-1]["source"], "windows_job_probe_controls.py")

    def test_nonzero_owned_command_exposes_only_sanitized_child_failure_receipt(self):
        with control_case(prefix="synthetic-child-failure-") as name:
            root = Path(name)

            def start(argv, *, cwd, env, report_dir):
                report = Path(report_dir)
                report.mkdir()
                stdout, stderr = report / "stdout", report / "stderr"
                stdout.write_text(json.dumps({"schema": "windows-job-probe-controls-v1", "status": "failed",
                    "error_type": "ProbeError", "diagnostic_codes": ["JOB_ASSIGNMENT_NOT_VERIFIED", "arbitrary-private-content"],
                    "source_frames": [{"source": "windows_job_probe.py", "line": 1, "function": "start"}],
                    "error": "synthetic-sensitive-content", "retained_evidence_root": "C:/private/path"}), encoding="utf-8")
                stderr.write_text("synthetic-sensitive-content", encoding="utf-8")
                snap = SimpleNamespace(root_reaped=True, active_processes=0, cleanup_verified=True,
                                       root_exit_code=2, tree_cpu_seconds=0.0)
                result = SimpleNamespace(snapshot=snap, reason="completed", stdout_path=str(stdout), stderr_path=str(stderr))
                return SimpleNamespace(poll=lambda: snap, finish=lambda timeout: result, result=result)

            commands = OwnedCommands(root / "commands")
            with patch("measure_parallel_readers.WindowsJobProbe.start", side_effect=start):
                with self.assertRaises(Hold) as caught:
                    commands.git(root, "rev-parse", "HEAD", deadline=float("inf"))
            diagnostic = getattr(caught.exception, "diagnostics", None)
            self.assertTrue(diagnostic, "nonzero child receipt must survive the hold")
            self.assertEqual(diagnostic["child_exit_code"], 2)
            self.assertEqual(diagnostic["exception_type"], "ProbeError")
            self.assertEqual(diagnostic["diagnostic_codes"], ["JOB_ASSIGNMENT_NOT_VERIFIED"])
            self.assertNotIn("synthetic-sensitive-content", json.dumps(diagnostic))
            self.assertNotIn("C:/private/path", json.dumps(diagnostic))

    def test_generated_scratch_after_sample_is_receipted_not_private_admission(self):
        with control_case(prefix="synthetic-generated-root-") as name:
            clone = Path(name) / "clone"
            (clone / "scratch/runs").mkdir(parents=True)
            (clone / "scratch/runs/suite-weights.json").write_text("{}", encoding="utf-8")
            try:
                corpus_preflight((clone,), admission=False)
            except Hold:
                self.fail("post-sample generated scratch is evidence, not preexisting private corpus")

    def test_private_scratch_before_sample_still_refuses(self):
        with control_case(prefix="synthetic-private-admission-") as name:
            clone = Path(name) / "clone"
            (clone / "scratch").mkdir(parents=True)
            with self.assertRaises(Hold):
                corpus_preflight((clone,), admission=True)

    def test_exception_diagnostics_keep_safe_frames_and_private_bounded_detail(self):
        with control_case(prefix="synthetic-exception-evidence-") as name:
            try:
                raise ValueError("synthetic-sensitive-content-must-not-be-public " + "x" * 100000)
            except ValueError as error:
                public = exception_diagnostics(error, Path(name))
            self.assertEqual(public.get("exception_type"), "ValueError")
            self.assertTrue(public.get("source_frames"))
            self.assertNotIn("synthetic-sensitive-content", json.dumps(public))
            private = Path(name) / "private-observer-error.txt"
            self.assertTrue(private.is_file())
            self.assertLessEqual(private.stat().st_size, 65536)

    def test_git_command_requires_absolute_preinstalled_executable(self):
        with control_case(prefix="synthetic-git-executable-") as name:
            root = Path(name)
            observed = []

            def start(argv, *, cwd, env, report_dir):
                observed.append(argv)
                self.assertTrue(Path(argv[0]).is_absolute(), "owner requires absolute executable")
                self.assertTrue(Path(argv[0]).is_file(), "resolved executable must exist")
                report = Path(report_dir)
                report.mkdir()
                stdout = report / "stdout"
                stdout.write_text("synthetic git result", encoding="utf-8")
                snap = SimpleNamespace(root_reaped=True, active_processes=0,
                                       cleanup_verified=True, root_exit_code=0)
                result = SimpleNamespace(snapshot=snap, reason="completed", stdout_path=str(stdout))
                return SimpleNamespace(poll=lambda: snap, finish=lambda timeout: result,
                                       delete_owned_files=lambda: stdout.unlink(), result=result)

            commands = OwnedCommands(root / "commands")
            with patch("measure_parallel_readers.WindowsJobProbe.start", side_effect=start):
                self.assertEqual(commands.git(root, "rev-parse", "HEAD", deadline=float("inf")), "synthetic git result")
            self.assertEqual(len(observed), 1)

    def observe(self, failure):
        with control_case(prefix="synthetic-registry-") as name:
            root = Path(name)
            clones = [root / "clone0", root / "clone1"]
            for clone in clones:
                (clone / "tools").mkdir(parents=True)
            factory = FakeFactory(failure)
            runner = LiveRunner(clones, "synthetic", root / "outside-clones", owner_factory=factory)
            clock = Clock()
            result = run_schedule(("test_a",), 1, runner, deadline=3,
                                  clock=clock, sleep=clock.sleep)
            self.assertFalse(result.complete)
            self.assertEqual(len(factory.created), 1)
            self.assertEqual(len(runner.owners), 1)
            self.assertTrue(runner.cleanup())
            self.assertFalse(factory.created[0].live)
            self.assertGreater(factory.created[0].cancel_calls, 0)
            return result

    def test_start_exception_keeps_partial_owner_for_cleanup(self):
        self.assertEqual(self.observe("start").stop_reason, "scheduler_or_runner_exception")

    def test_poll_exception_cancels_registered_owner(self):
        self.assertEqual(self.observe("poll").stop_reason, "scheduler_or_runner_exception")

    def test_cancel_exception_is_not_success_and_registry_cleanup_remains(self):
        self.assertEqual(self.observe("cancel").stop_reason, "cleanup_unverified")

    def test_runner_exception_preserves_safe_type_and_source_frames(self):
        result = self.observe("poll")
        diagnostics = getattr(result, "diagnostics", None)
        self.assertTrue(diagnostics, "runner exception diagnosis must not disappear")
        self.assertEqual(diagnostics[0]["exception_type"], "OwnedFailure")
        self.assertTrue(diagnostics[0]["source_frames"])
        self.assertNotIn("traceback", diagnostics[0])


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    from console_codec import require_python_floor, use_utf8
    use_utf8()
    require_python_floor()
    retained_evidence = reader_controls.configure_control_evidence()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    print(json.dumps({"schema_version": 1, "kind": "observer-registry-controls",
                      "tests_run": result.testsRun, "failures": len(result.failures),
                      "errors": len(result.errors), "successful": result.wasSuccessful(),
                      "retained_evidence_requested": retained_evidence,
                      "local_cleanup_proof_executed": LOCAL_CLEANUP_PROOF_EXECUTED}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
