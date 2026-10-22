"""Portable synthetic tests of the approved scheduler/runner launch boundary.

No application imports or native process starts. Real synthetic capture files use
the unchanged coherent reader. These checks do not qualify Windows ownership.
"""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest

from current_parallel_runner import CurrentParallelRunner, LEDGER_KEYS, RunnerRefused
from generated_output_contract import read_owned_capture
from parallel_reader_scheduler import LOOKUPS, run_schedule
from windows_job_probe import ProbeResult, ProbeSnapshot


CLEAN = b"Ran 3 tests in 0.001s\n\nOK (skipped=1)\n"
PAYLOAD = "synthetic payload; never executed"
REFUSAL = (b"FAIL: test_synthetic (test_alpha.Example.test_synthetic)\n"
           b"Traceback (most recent call last):\n"
           b"  synthetic fixture frame\n"
           b"AssertionError: CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup\n"
           b"Ran 1 test in 0.001s\n\nFAILED (failures=1)\n")


class Clock:
    def __init__(self):
        self.now = time.monotonic()

    def __call__(self):
        return self.now

    def sleep(self, ignored):
        self.now += 1


class Owner:
    def __init__(self, factory, argv, cwd, env, report_dir):
        self.factory, self.argv, self.cwd, self.env = factory, argv, cwd, env
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir()
        self.stdout_path, self.stderr_path = (self.report_dir / name for name in ("stdout.bin", "stderr.bin"))
        self.plan = factory.plans.get((argv[-2], argv[-1]), {})
        self.stdout_path.write_bytes(self.plan.get("stdout", b""))
        self.stderr_path.write_bytes(self.plan.get("stderr", CLEAN))
        self.pid = len(factory.owners) + 100
        self.started = factory.clock()
        self.result = None
        self.cancel_timeouts = []

    def poll(self):
        if self.result is not None:
            return self.result.snapshot
        done = self.factory.clock() - self.started >= self.plan.get("delay", 1)
        return ProbeSnapshot(self.pid, self.plan.get("code", 0) if done else None, done,
                             0 if done else 2, 2, 0.125, 0.25,
                             self.factory.clock() - self.started, False, "running")

    def finish(self, timeout):
        if self.plan.get("finish_error"):
            raise RuntimeError("PRIVATE finish failure")
        snap = replace(self.poll(), cleanup_verified=True, state="closed")
        if self.plan.get("wrong_finish_pid"):
            snap = replace(snap, root_pid=snap.root_pid + 1)
        if self.plan.get("wrong_finish_total"):
            snap = replace(snap, total_processes=9)
        if self.plan.get("nan_cpu"):
            snap = replace(snap, user_cpu_seconds=float("nan"))
        self.result = ProbeResult(snap, "completed", str(self.stdout_path), str(self.stderr_path), ())
        if self.plan.get("substituted_result"):
            return replace(self.result)
        return self.result

    def cancel(self, reason, timeout):
        self.cancel_timeouts.append(timeout)
        if self.result is not None:
            return self.result
        if self.plan.get("cancel_failures", 0) >= len(self.cancel_timeouts):
            if self.plan.get("consume_cancel_budget"):
                self.factory.clock.now += timeout
            raise RuntimeError("PRIVATE cancellation failure")
        snap = replace(self.poll(), root_exit_code=7, root_reaped=True,
                       active_processes=0, cleanup_verified=True, state="closed")
        self.result = ProbeResult(snap, reason, str(self.stdout_path), str(self.stderr_path), ())
        return self.result


class Factory:
    def __init__(self, clock, plans=None):
        self.clock, self.plans = clock, plans or {}
        self.owners = []
        self.maximum = 0

    def start(self, argv, *, cwd, env, report_dir):
        owner = Owner(self, argv, cwd, env, report_dir)
        self.owners.append(owner)
        self.maximum = max(self.maximum, sum(item.result is None for item in self.owners))
        if owner.plan.get("partial_start"):
            error = RuntimeError("PRIVATE start failure at /secret/path")
            error.owner = owner
            raise error
        return owner


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.private = tempfile.TemporaryDirectory(prefix="parallel-runner-synthetic-")
        self.addCleanup(self.private.cleanup)
        self.root = Path(self.private.name).resolve()
        self.clones = (self.root / "lane0", self.root / "lane1")
        for root in self.clones:
            (root / "tools").mkdir(parents=True)
        self.clock = Clock()
        self.factory = Factory(self.clock)

    def runner(self, arm="serial", modules=("test_alpha",), **overrides):
        capture, temporary = self.root / (arm + "-capture"), self.root / (arm + "-temp")
        capture.mkdir()
        temporary.mkdir()
        args = dict(arm=arm, modules=modules, clones=self.clones,
                    capture_root=capture, temporary_root=temporary, payload=PAYLOAD,
                    source_sha="1" * 40, source_manifest_sha256="2" * 64,
                    candidate_sha256="3" * 64,
                    interpreter_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                    deadline=self.clock() + 100, hard_deadline=self.clock() + 120,
                    clock=self.clock, owner_factory=self.factory,
                    environment={"SYSTEMROOT": "synthetic-system"},
                    disk_usage=lambda path: SimpleNamespace(free=2**40))
        args.update(overrides)
        return CurrentParallelRunner(**args)

    def schedule(self, runner, cap):
        return run_schedule(runner.modules, cap, runner, deadline=runner.deadline,
                            clock=self.clock, sleep=self.clock.sleep)

    def test_complete_schedule_retains_exact_launch_bound_captures(self):
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, len(result.observations), result.unread_pairs), (True, 2, ()))
        rows = runner.attempt_ledger()
        self.assertEqual([(row["command_ordinal"], row["completion"], row["test_count"], row["skipped"])
                          for row in rows], [(1, "completed", 3, 1), (2, "completed", 3, 1)])
        self.assertEqual(rows[0]["stderr_sha256"], hashlib.sha256(CLEAN).hexdigest())
        self.assertEqual(rows[0]["tree_cpu_seconds"], 0.375)
        self.assertEqual(self.factory.owners[0].argv,
                         [sys.executable, "-c", PAYLOAD, str(self.clones[0] / "tools"), "test_alpha", LOOKUPS[0]])
        self.assertEqual(self.factory.owners[0].stderr_path.name, "stderr.bin")
        self.assertEqual(self.factory.owners[0].report_dir.name, "command-0001")
        self.assertEqual(runner.cleanup(), True)

    def test_cap1_measurement_label_launches_and_is_retained_unchanged(self):
        runner = self.runner("cap1")
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, len(result.observations), self.factory.maximum), (True, 2, 1))
        self.assertEqual([row["arm"] for row in runner.attempt_ledger()], ["cap1", "cap1"])
        self.assertEqual(runner.cleanup(), True)

    def test_slow_first_owner_cannot_hide_second_stream_exhaustion(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 50},
                              ("test_beta", LOOKUPS[0]): {"delay": 50}}
        runner = self.runner("cap2", ("test_alpha", "test_beta"))
        first = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        second = runner.start(1, 1, "test_beta", LOOKUPS[0])
        with second.stderr_path.open("ab") as stream:
            stream.truncate(16 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(RunnerRefused, "capture_limit_exceeded"):
            runner.poll(first)
        self.assertEqual(runner.first_failure["command_ordinal"], 2)
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual([row["active_processes"] for row in runner.attempt_ledger()], [0, 0])

    def test_receipt_identity_is_reference_pair_not_private_pid_or_arm(self):
        runner = self.runner()
        self.schedule(runner, 1)
        row = runner.attempt_ledger()[0]
        expected = hashlib.sha256(json.dumps(["repository", "test_alpha", "icd10_lookup"],
                                            separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
        self.assertEqual(row["pair_token"], expected)
        self.assertEqual(row["root_identity_verified"], True)
        self.assertNotIn("root_pid", row)

    def test_dynamic_disk_admission_includes_reserved_and_active_unwritten_bytes(self):
        samples = []
        runner = self.runner(resource_check=lambda: samples.append(runner.pending_capture_bytes()))
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        self.assertEqual(samples, [33554432])
        self.assertEqual(runner.pending_capture_bytes(), 33554432 - len(CLEAN))
        self.clock.sleep(1)
        observation = runner.poll(handle)
        self.assertEqual((observation.classification, runner.pending_capture_bytes()), ("nonreader", 0))

    def test_changed_terminal_pid_never_becomes_verified_cleanup(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"wrong_finish_pid": True}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, result.observations[0].cleanup_verified), (False, False))
        self.assertEqual(runner.cleanup(), False)
        self.assertEqual(runner.attempt_ledger()[0]["completion"], "incomplete")
        self.assertEqual(runner.first_failure["reason"], "completion_failed")

    def test_partial_start_is_reserved_once_retained_and_never_reused(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"partial_start": True}}
        runner = self.runner("cap2", ("test_alpha", "test_beta"))
        with self.assertRaises(RuntimeError):
            runner.start(0, 0, "test_alpha", LOOKUPS[0])
        later = runner.start(1, 1, "test_beta", LOOKUPS[0])
        rows = runner.attempt_ledger()
        self.assertEqual([(row["command_ordinal"], row["completion"], row["cleanup_verified"])
                          for row in rows], [(1, "incomplete", True), (2, "incomplete", False)])
        self.assertEqual((later.command_ordinal, rows[0]["returncode"], rows[0]["test_count"]), (2, 7, None))
        self.assertEqual(rows[0]["root_identity_verified"], True)
        self.assertEqual(set(rows[0]), LEDGER_KEYS)
        self.assertNotIn("PRIVATE", json.dumps(runner.first_failure))
        self.assertEqual(runner.cleanup(), True)

    def test_failed_cancel_keeps_owner_for_full_deadline_cleanup(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 1000, "cancel_failures": 1}}
        runner = self.runner(deadline=self.clock() + 3, hard_deadline=self.clock() + 12)
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, result.observations[0].reason), (False, "cleanup_unverified"))
        self.assertEqual(runner.attempt_ledger()[0]["tree_cpu_seconds"], None)
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual(self.factory.owners[0].cancel_timeouts, [5.0, 5.0])
        self.assertEqual(runner.attempt_ledger()[0]["completion"], "incomplete")

    def test_finish_failure_preserves_first_cause_through_cleanup(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"finish_error": True, "cancel_failures": 1}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        first = runner.first_failure
        self.assertEqual((result.complete, first["reason"]), (False, "completion_failed"))
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual(runner.first_failure, first)
        self.assertEqual(runner.attempt_ledger()[0]["completion"], "incomplete")

    def test_caps_cover_same_146_module_pairs_and_sequential_lanes(self):
        modules = tuple("test_module_%03d" % index for index in range(146))
        serial = self.runner("serial", modules, deadline=self.clock() + 2000,
                             hard_deadline=self.clock() + 2200)
        first = self.schedule(serial, 1)
        parallel = self.runner("cap2", modules, deadline=self.clock() + 2000,
                               hard_deadline=self.clock() + 2200)
        second = self.schedule(parallel, 2)
        self.assertEqual((first.complete, second.complete, len(first.observations), len(second.observations)),
                         (True, True, 292, 292))
        self.assertEqual([(row.module, row.lookup, row.classification, row.test_count) for row in first.observations],
                         [(row.module, row.lookup, row.classification, row.test_count) for row in second.observations])
        self.assertEqual(self.factory.maximum, 2)
        self.assertEqual([(row["module"], row["lookup"], row["lane"]) for row in serial.attempt_ledger()],
                         [(row["module"], row["lookup"], row["lane"])
                          for row in sorted(parallel.attempt_ledger(), key=lambda item: item["pair_index"])])
        self.assertEqual(second.observations[-1].module, "test_module_145")

    def test_earlier_second_lookup_error_wins_over_faster_later_error(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 5},
                              ("test_alpha", LOOKUPS[1]): {"delay": 2, "code": 1},
                              ("test_beta", LOOKUPS[0]): {"delay": 1, "code": 1}}
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"))
        result = self.schedule(runner, 2)
        self.assertEqual((result.complete, result.first_error, result.first_error_resolved),
                         (False, ("test_alpha", "procedure_codes_lookup"), True))
        self.assertEqual([(row["module"], row["lookup"]) for row in runner.attempt_ledger()],
                         [("test_alpha", "icd10_lookup"), ("test_beta", "icd10_lookup"),
                          ("test_alpha", "procedure_codes_lookup")])

    def test_earlier_hang_leaves_first_error_unresolved_and_drains_both(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 1000},
                              ("test_beta", LOOKUPS[0]): {"delay": 1, "code": 1}}
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"),
                             deadline=self.clock() + 5)
        result = self.schedule(runner, 2)
        self.assertEqual((result.complete, result.first_error_resolved, len(runner.attempt_ledger())),
                         (False, False, 2))
        self.assertEqual([row["active_processes"] for row in runner.attempt_ledger()], [0, 0])
        self.assertEqual(runner.cleanup(), True)

    def test_same_pid_result_with_changed_tree_metrics_is_not_completed(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"wrong_finish_total": True}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.attempt_ledger()[0]["capture_read_verified"]), (False, False))
        self.assertEqual(runner.attempt_ledger()[0]["completion"], "incomplete")

    def test_failed_cancel_does_not_release_the_lane_for_another_tree(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 1000, "cancel_failures": 1}}
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"))
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        self.assertEqual(runner.cancel(handle, "synthetic_cancel").cleanup_verified, False)
        with self.assertRaisesRegex(RunnerRefused, "launch_lane_already_active"):
            runner.start(2, 0, "test_gamma", LOOKUPS[0])
        self.assertEqual(runner.cleanup(), True)
        later = runner.start(2, 0, "test_gamma", LOOKUPS[0])
        self.assertEqual(later.command_ordinal, 2)
        self.assertEqual(runner.cleanup(), True)

    def test_same_content_capture_replacement_after_launch_is_refused(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        handle.stderr_path.rename(self.root / "original-retained.bin")
        handle.stderr_path.write_bytes(CLEAN)
        self.clock.sleep(1)
        with self.assertRaisesRegex(RunnerRefused, "capture_stream_identity_changed"):
            runner.poll(handle)
        self.assertEqual(runner.attempt_ledger()[0]["capture_read_verified"], False)
        self.assertEqual(runner.cleanup(), True)

    def test_both_streams_and_lane_free_reserve_are_checked_before_new_launch(self):
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"))
        first = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        second = runner.start(1, 1, "test_beta", LOOKUPS[0])
        checked = []
        def disk(path):
            checked.append(Path(path))
            return SimpleNamespace(free=1024 * 1024 * 1024 - (Path(path) == second.temporary))
        runner.disk_usage = disk
        with self.assertRaisesRegex(RunnerRefused, "disk_reserve_exhausted"):
            runner.poll(first)
        self.assertEqual(runner.first_failure["command_ordinal"], 2)
        self.assertIn(first.temporary, checked)
        self.assertIn(second.temporary, checked)
        self.assertEqual(runner.cleanup(), True)

    def test_expired_tick_cancels_all_without_clocks_reset(self):
        runner = self.runner("cap2", ("test_alpha", "test_beta"), deadline=self.clock() + 3)
        first = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        runner.start(1, 1, "test_beta", LOOKUPS[0])
        self.clock.now += 3
        with self.assertRaisesRegex(RunnerRefused, "work_deadline_exhausted"):
            runner.poll(first)
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual([row["completion"] for row in runner.attempt_ledger()], ["incomplete", "incomplete"])
        self.assertEqual([row["active_processes"] for row in runner.attempt_ledger()], [0, 0])

    def test_pair_and_ordinal_handle_substitution_is_refused(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        for changed in (replace(handle), replace(handle, command_ordinal=2), replace(handle, lookup=LOOKUPS[1])):
            with self.assertRaisesRegex(RunnerRefused, "launch_handle_changed"):
                runner.poll(changed)
        self.clock.sleep(1)
        self.assertEqual(runner.poll(handle).classification, "nonreader")

    def test_returned_owner_and_same_count_result_cannot_be_substituted(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"substituted_result": True}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.attempt_ledger()[0]["capture_read_verified"]), (False, False))
        self.assertEqual(runner.attempt_ledger()[0]["completion"], "incomplete")

    def test_nonfinite_metrics_stay_unread_not_zero(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"nan_cpu": True}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.attempt_ledger()[0]["tree_cpu_seconds"]), (False, None))
        self.assertNotIn("NaN", json.dumps(runner.attempt_ledger(), allow_nan=False))

    def test_same_tree_capture_ancestor_replacement_is_refused(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        old = self.root / "retained-original-command"
        handle.report_dir.rename(old)
        handle.report_dir.mkdir()
        for stream in ("stdout.bin", "stderr.bin"):
            (old / stream).rename(handle.report_dir / stream)
        self.clock.sleep(1)
        with self.assertRaisesRegex(RunnerRefused, "directory_identity_changed"):
            runner.poll(handle)
        self.assertEqual(runner.attempt_ledger()[0]["capture_read_verified"], False)
        self.assertEqual(runner.cleanup(), True)

    def test_capture_hardlink_is_refused(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        os.link(handle.stderr_path, self.root / "linked-capture.bin")
        self.clock.sleep(1)
        with self.assertRaisesRegex(RunnerRefused, "capture_stream_unsafe"):
            runner.poll(handle)
        self.assertEqual(runner.attempt_ledger()[0]["capture_read_verified"], False)
        self.assertEqual(runner.cleanup(), True)

    def test_classification_uses_verified_bytes_without_reopening_paths(self):
        def coherent_then_replaced(root, relative, limit, deadline):
            raw = read_owned_capture(root, relative, limit, deadline)
            if relative.endswith("stderr.bin"):
                (root / relative).write_bytes(b"unread replacement after authenticated read")
            return raw
        runner = self.runner(capture_reader=coherent_then_replaced)
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, result.observations[0].test_count), (True, 3))
        self.assertEqual(runner.attempt_ledger()[0]["stderr_sha256"], hashlib.sha256(CLEAN).hexdigest())

    def test_authentic_refusal_is_reader_and_mixed_failure_is_not_clean(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"code": 1, "stderr": REFUSAL},
                              ("test_alpha", LOOKUPS[1]): {"code": 1, "stderr": REFUSAL.replace(
                                  b"AssertionError: CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup",
                                  b"ValueError: CODE_SET_DATABASE_OPEN_REFUSED:procedure_codes_lookup")}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual([(row.classification, row.unexpected) for row in result.observations],
                         [("reader", False), ("reader", True)])
        self.assertEqual((result.complete, result.first_error), (False, ("test_alpha", "procedure_codes_lookup")))

    def test_orphan_unread_traceback_never_passes_clean_summary(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {
            "stderr": b"Traceback (most recent call last):\nValueError: synthetic\n" + CLEAN}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, result.observations[0].classification,
                          result.observations[0].unexpected), (False, "nonreader", True))

    def test_independent_temp_roots_replace_inherited_case_aliases(self):
        runner = self.runner("cap2", ("test_alpha", "test_beta"),
                             environment={"SystemRoot": "synthetic", "temp": "shared", "Tmp": "shared"})
        first = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        second = runner.start(1, 1, "test_beta", LOOKUPS[0])
        self.assertEqual([owner.env for owner in self.factory.owners],
                         [{"SystemRoot": "synthetic", "TEMP": str(first.temporary), "TMP": str(first.temporary)},
                          {"SystemRoot": "synthetic", "TEMP": str(second.temporary), "TMP": str(second.temporary)}])
        self.assertEqual(first.temporary == second.temporary, False)
        self.assertEqual(any(first.temporary.is_relative_to(root) for root in self.clones), False)
        self.assertEqual(runner.cleanup(), True)

    def test_shared_clone_root_is_refused(self):
        with self.assertRaisesRegex(RunnerRefused, "runner_roots_overlap"):
            self.runner(clones=(self.clones[0], self.clones[0]))

    def test_temp_directory_replacement_is_refused(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        handle.temporary.rename(self.root / "old-temporary")
        handle.temporary.mkdir()
        with self.assertRaisesRegex(RunnerRefused, "directory_identity_changed"):
            runner.poll(handle)
        self.assertEqual(runner.cleanup(), True)

    def test_sibling_file_mutation_is_not_misrepresented_as_process_isolation(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        sibling = self.clones[1] / "tools" / "synthetic-change.txt"
        sibling.write_text("synthetic persistent change", encoding="utf-8")
        self.clock.sleep(1)
        self.assertEqual(runner.poll(handle).classification, "nonreader")
        self.assertEqual(sibling.read_text(encoding="utf-8"), "synthetic persistent change")
        # The separate quiescent driver guard must reject this persistent change.

    def test_completed_metadata_stays_exact_across_cleanup_and_copies_are_detached(self):
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.clock.now += 10
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual(tuple(row.metadata for row in result.observations), runner.attempt_ledger())
        copied = runner.attempt_ledger()[0]
        copied["classification"] = "error"
        self.assertEqual(runner.attempt_ledger()[0]["classification"], "nonreader")

    def test_unread_summary_stays_incomplete_even_when_capture_and_cleanup_verify(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"stderr": b"unread synthetic output"}}
        runner = self.runner()
        result = self.schedule(runner, 1)
        row = runner.attempt_ledger()[0]
        self.assertEqual((row["completion"], row["reason"], row["test_count"]),
                         ("incomplete", "capture_unread", None))
        self.assertEqual((row["capture_read_verified"], row["cleanup_verified"], result.complete),
                         (True, True, False))
        self.assertIn(("test_alpha", "icd10_lookup"), result.unread_pairs)

    def test_capture_replacement_between_poll_and_coherent_read_is_refused(self):
        def replace_before_read(root, relative, limit, deadline):
            if relative.endswith("stderr.bin"):
                path = root / relative
                path.rename(path.with_suffix(".original"))
                path.write_bytes(CLEAN)
            return read_owned_capture(root, relative, limit, deadline)
        runner = self.runner(capture_reader=replace_before_read)
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.attempt_ledger()[0]["capture_read_verified"]), (False, False))
        self.assertEqual(runner.first_failure["reason"], "completion_failed")

    def test_slow_earliest_module_blocks_third_admission_after_later_retirement(self):
        origin = self.clock()
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 5}}
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"))
        result = self.schedule(runner, 2)
        self.assertEqual((result.complete, len(result.observations)), (True, 6))
        self.assertEqual([owner.argv[-2] for owner in self.factory.owners],
                         ["test_alpha", "test_beta", "test_beta", "test_alpha", "test_gamma", "test_gamma"])
        self.assertEqual(self.factory.owners[4].started - origin, 6)

    def test_reverse_failure_completion_keeps_canonical_first_error(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 5, "code": 1},
                              ("test_beta", LOOKUPS[0]): {"delay": 1, "code": 1}}
        runner = self.runner("cap2", ("test_alpha", "test_beta", "test_gamma"))
        result = self.schedule(runner, 2)
        self.assertEqual((result.first_error, result.first_error_resolved),
                         (("test_alpha", "icd10_lookup"), True))
        self.assertEqual([row["module"] for row in runner.attempt_ledger()], ["test_alpha", "test_beta"])

    def test_reused_previous_owner_cannot_bind_a_new_attempt(self):
        original_start = self.factory.start
        def reuse(argv, **kwargs):
            return original_start(argv, **kwargs) if not self.factory.owners else self.factory.owners[0]
        self.factory.start = reuse
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, len(runner.attempt_ledger())), (False, 2))
        self.assertEqual([(row["completion"], row["capture_read_verified"]) for row in runner.attempt_ledger()],
                         [("completed", True), ("incomplete", False)])

    def test_unknown_exception_class_and_message_do_not_escape(self):
        SensitiveName = type("PRIVATE_EXCEPTION_CANARY", (Exception,), {})
        def refuse():
            raise SensitiveName("PRIVATE_MESSAGE_CANARY /secret/path")
        runner = self.runner(resource_check=refuse)
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.first_failure["diagnostic"]["exception_type"]),
                         (False, "unavailable"))
        self.assertNotIn("PRIVATE", json.dumps({"failure": runner.first_failure,
                                               "ledger": runner.attempt_ledger(),
                                               "diagnostics": result.diagnostics}))

    def test_exact_stream_limit_remains_a_qualifying_size_not_hard_quota_claim(self):
        runner = self.runner()
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        with handle.stdout_path.open("ab") as stream:
            stream.truncate(16 * 1024 * 1024)
        self.clock.sleep(1)
        row = runner.poll(handle)
        self.assertEqual((row.unexpected, row.metadata["stdout_bytes"]), (False, 16777216))
        self.assertEqual(runner.cleanup(), True)

    def test_first_slow_cancel_cannot_spend_the_second_owners_cleanup_reserve(self):
        origin = self.clock()
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {
            "delay": 1000, "cancel_failures": 1, "consume_cancel_budget": True},
            ("test_beta", LOOKUPS[0]): {"delay": 1000}}
        runner = self.runner("cap2", ("test_alpha", "test_beta"), deadline=origin + 3,
                             hard_deadline=origin + 15)
        result = self.schedule(runner, 2)
        self.assertEqual((result.complete, result.observations[0].cleanup_verified,
                          result.observations[1].cleanup_verified), (False, False, True))
        self.assertEqual([owner.cancel_timeouts for owner in self.factory.owners], [[5.0], [5.0]])
        self.assertEqual(self.clock() - origin, 8)
        self.assertEqual(runner.cleanup(), True)
        self.assertEqual([row["completion"] for row in runner.attempt_ledger()], ["incomplete", "incomplete"])

    def test_exhausted_hard_budget_still_attempts_second_cancel_with_zero_not_negative(self):
        origin = self.clock()
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {
            "delay": 1000, "cancel_failures": 1, "consume_cancel_budget": True},
            ("test_beta", LOOKUPS[0]): {"delay": 1000}}
        runner = self.runner("cap2", ("test_alpha", "test_beta"), deadline=origin + 3,
                             hard_deadline=origin + 4)
        result = self.schedule(runner, 2)
        self.assertEqual((result.complete, result.observations[1].cleanup_verified), (False, True))
        self.assertEqual([owner.cancel_timeouts for owner in self.factory.owners], [[1.0], [0.0]])
        self.assertEqual(runner.cleanup(), True)

    def test_quiescence_reflects_live_and_cleanup_failed_ownership_without_polling(self):
        self.factory.plans = {("test_alpha", LOOKUPS[0]): {"delay": 1000, "cancel_failures": 1}}
        runner = self.runner()
        self.assertEqual(runner.is_quiescent, True)
        handle = runner.start(0, 0, "test_alpha", LOOKUPS[0])
        self.assertEqual(runner.is_quiescent, False)
        self.assertEqual(runner.cancel(handle, "synthetic_cancel").cleanup_verified, False)
        self.assertEqual(runner.is_quiescent, False)
        self.assertEqual(runner.cleanup(), True)
        def cannot_poll():
            raise AssertionError("a quiescence read must not poll a native owner")
        self.factory.owners[0].poll = cannot_poll
        self.assertEqual(runner.is_quiescent, True)

    def test_later_cleanup_verification_failure_makes_runner_nonquiescent(self):
        runner = self.runner()
        result = self.schedule(runner, 1)
        self.assertEqual((result.complete, runner.is_quiescent), (True, True))
        owner = self.factory.owners[0]
        owner.result = replace(owner.result, snapshot=replace(owner.result.snapshot, cleanup_verified=False))
        self.assertEqual(runner.cleanup(), False)
        self.assertEqual(runner.is_quiescent, False)


if __name__ == "__main__":
    unittest.main()
