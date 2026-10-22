"""Portable public-boundary controls, never native Windows qualification."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from dataclasses import replace

from test_compact_capture_retention import FakeNative
from windows_job_probe import ProbeResult, ProbeSnapshot
import generated_output_contract as contract

import compact_native_controls as subject


class SyntheticOwners:
    """Fresh fixtures only, no process launch or native disposition."""
    def __init__(self):
        self.owners = []

    def start(self, argv, *, cwd, env, report_dir):
        report_dir.mkdir()
        # The public synthetic child protocol carries bytes as hex, never code
        # supplied by tests or an application module to import.
        stdout, stderr, code = bytes.fromhex(argv[-3]), bytes.fromhex(argv[-2]), int(argv[-1])
        paths = [report_dir / (name + ".bin") for name in ("stdout", "stderr")]
        for path, raw in zip(paths, (stdout, stderr)):
            path.write_bytes(raw)
        pid = 100 + len(self.owners)
        snapshot = ProbeSnapshot(pid, code, True, 0, 1, 0.1, 0.1, 0.2, True, "closed")
        result = ProbeResult(snapshot, "completed", str(paths[0]), str(paths[1]), ())
        owner = SimpleNamespace(report_dir=report_dir, stdout_path=paths[0], stderr_path=paths[1],
            _info=SimpleNamespace(dwProcessId=pid), result=None, poll=lambda: snapshot)
        def finish(timeout):
            owner.result = result
            return result
        owner.finish = finish
        owner.cancel = lambda reason, timeout: finish(timeout)
        self.owners.append(owner)
        return owner


class SharingNative(FakeNative):
    """Portable incompatible-sharing model, explicitly not native evidence."""
    def __init__(self):
        super().__init__()
        self.c = SimpleNamespace(get_last_error=lambda: 32, c_void_p=lambda value: SimpleNamespace(value=-1))
        class Operation:
            def __init__(self, call): self.call = call
            def __call__(self, *args): return self.call(*args)
        self.kernel = SimpleNamespace(CreateFileW=Operation(lambda *args: -1),
            MoveFileExW=Operation(lambda *args: 0), DeleteFileW=Operation(lambda *args: 0))
        self.opens = []

    def _open(self, path, kind):
        self.opens.append((0x80010000 if kind == "capture" else 0x80000000, 1, 3, 0x08200000))
        if any(row["path"] == Path(path) and (kind == "capture" or row["kind"] == "capture")
               for row in self.handles.values()):
            raise contract.q.Refused("compact_capture_unread" if kind == "capture" else "generated_file_unread")
        return super()._open(path, kind)

    def record(self, handle):
        record = super().record(handle)
        row = self.handles.get(handle)
        if row and row["path"].is_symlink():
            record = replace(record, st_file_attributes=0x400, reparse_tag=0xA000000C)
        return record


class SyntheticCoordinatorOwners(SyntheticOwners):
    def start(self, argv, *, cwd, env, report_dir):
        if "runpy.run_path" not in argv[-4]:
            return super().start(argv, cwd=cwd, env=env, report_dir=report_dir)
        root = Path(argv[-3])
        report_dir.mkdir()
        paths = [report_dir / (name + ".bin") for name in ("stdout", "stderr")]
        for path in paths:
            path.write_bytes(b"")
        inner = root / "inner"
        inner.mkdir()
        eligibility = b'{"synthetic":"owned-coordinator-model"}\n'
        (inner / "compact-000001-eligibility.json").write_bytes(eligibility)
        import hashlib
        ready = {"version": 1, "inner_commands": 1, "inner_cleanup_verified": True,
            "inner_active_processes": 0, "mark": "verified", "stream": "stdout",
            "eligibility_sha256": hashlib.sha256(eligibility).hexdigest(), "terminal_written": False}
        (root / "coordinator-ready.json").write_bytes(json.dumps(ready, sort_keys=True, separators=(",", ":")).encode())
        pid = 100 + len(self.owners)
        owner = SimpleNamespace(report_dir=report_dir, stdout_path=paths[0], stderr_path=paths[1],
            _info=SimpleNamespace(dwProcessId=pid, hProcess=pid + 1000), result=None, stopped=False)
        def poll():
            return ProbeSnapshot(pid, 9 if owner.stopped else None, owner.stopped,
                                 0 if owner.stopped else 1, 2, 0.1, 0.1, 0.2, owner.stopped,
                                 "closed" if owner.stopped else "running")
        def finish(timeout):
            owner.result = ProbeResult(poll(), "completed", str(paths[0]), str(paths[1]), ())
            return owner.result
        def cancel(reason, timeout):
            owner.stopped = True
            return finish(timeout)
        owner.poll, owner.finish, owner.cancel = poll, finish, cancel
        self.owners.append(owner)
        return owner


class NativePacketControls(unittest.TestCase):
    def runtime(self, native=None):
        factory, api = SyntheticOwners(), native or FakeNative()
        def read(root, relative, limit, deadline):
            with (root / relative).open("rb") as stream:
                return stream.read(limit + 1), api.record(stream.fileno())
        runtime = subject.ControlRuntime(owner_factory=factory, api_factory=lambda: api,
                                         snapshot_reader=read)
        runtime.work_deadline = time.monotonic() + 30
        runtime.hard_deadline = runtime.work_deadline + 60
        return runtime, factory, api

    def test_fresh_pair_is_owned_registered_and_retired_by_real_store(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, factory, api = self.runtime()
            root = Path(temporary).resolve() / "pair"
            pair = subject.prepare_pair(root, runtime, stdout=b"exact stdout\r\n", stderr=b"")
            self.assertEqual(pair.reads[0][0], b"exact stdout\r\n")
            self.assertEqual(pair.result.reason, "completed")
            self.assertEqual(pair.store.public_summary()["pending_pairs"], 1)
            result = pair.retire()
            self.assertEqual((result["complete"], result["retention"]), (True, "disposition_verified"))
            self.assertEqual([row["mark"] for row in result["streams"]], ["verified", "verified"])
            self.assertEqual(runtime.cleanup(), True)
            self.assertEqual(len(factory.owners), 1)
            with self.assertRaises(subject.ControlError):
                subject.prepare_pair(root, runtime)

    def test_operation_faults_keep_exact_partial_states_and_unknown_retention(self):
        expectations = {
            "before_first_mark_refusal": (["uncertain", "not_requested"], "compact_disposition_failed"),
            "second_mark_partial": (["verified", "uncertain"], "compact_disposition_failed"),
            "deadline_after_first_close": (["verified", "not_requested"], "compact_deadline_exhausted"),
            "raw_close_partial": (["verified", "not_requested"], "compact_disposition_failed"),
            "outcome_readback_partial": (["verified", "verified"], "compact_outcome_receipt_failed"),
            "authority_recheck_partial": (["verified", "verified"], "compact_authority_recheck_failed"),
            "authority_close_partial": (["verified", "verified"], "compact_authority_close_failed"),
            "terminal_readback_unknown": (["verified", "verified"], "compact_terminal_receipt_failed"),
        }
        for control_id, (marks, reason) in expectations.items():
            with self.subTest(control_id=control_id), tempfile.TemporaryDirectory(
                    prefix="compact-packet-synthetic-") as temporary:
                runtime, _, api = self.runtime()
                result = subject.run_control(control_id, Path(temporary).resolve() / "new", runtime)
                self.assertEqual(result["outcome"]["reason"], reason)
                self.assertEqual([row["mark"] for row in result["outcome"]["streams"]], marks)
                self.assertEqual(result["retention"], "unknown")
                self.assertEqual(result["next_pair_refused"], True)
                self.assertEqual(runtime.cleanup(), True)
                self.assertEqual(api.handles, {})

    def test_snapshot_share_receipt_authority_control_uses_original_readbacks(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, _, _ = self.runtime(SharingNative())
            result = subject.run_control("snapshot_share_receipt_success",
                Path(temporary).resolve() / "new", runtime)
            self.assertEqual(result["retention"], "disposition_verified")
            self.assertEqual(result["authority_denials"], ["write", "delete_open", "replace", "delete"])
            self.assertEqual(result["snapshot_fields"], list(contract.METADATA_FIELDS))
            self.assertEqual(result["outcome"]["receipt_authority"],
                             {"recheck": "verified", "close": "verified"})

    def test_identity_link_and_reparse_mutants_refuse_before_disposition(self):
        for control_id in ("replacement_identity_refusal", "hardlink_refusal", "reparse_refusal"):
            with self.subTest(control_id=control_id), tempfile.TemporaryDirectory(
                    prefix="compact-packet-synthetic-") as temporary:
                runtime, _, api = self.runtime(SharingNative())
                with contextlib.redirect_stdout(io.StringIO()):
                    evidence = subject.run_control(control_id, Path(temporary).resolve() / "new", runtime)
                self.assertEqual((evidence["outcome"]["complete"], evidence["retention"],
                    evidence["next_pair_refused"]), (False, "unknown", True))
                self.assertEqual([row["mark"] for row in evidence["outcome"]["streams"]],
                                 ["not_requested", "not_requested"])
                self.assertEqual(api.disposed, [])

    def test_missing_terminal_and_containing_result_never_assert_raw_retention(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, _, _ = self.runtime()
            pair = subject.prepare_pair(Path(temporary).resolve() / "new", runtime)
            outcome = pair.retire()
            self.assertEqual(subject.reconstruct_retention(pair.root, pair.api,
                runtime.work_deadline, outcome=outcome, invocation_complete=True), "disposition_verified")
            terminal = pair.root / "compact-000001-terminal.json"
            terminal.rename(pair.root / "retained-terminal.json")
            self.assertEqual(subject.reconstruct_retention(pair.root, pair.api,
                runtime.work_deadline, outcome=outcome, invocation_complete=True), "unknown")
            self.assertEqual(subject.reconstruct_retention(pair.root, pair.api,
                runtime.work_deadline), "unknown")

    def test_coordinator_receipt_is_bounded_and_requires_owned_inner_cleanup(self):
        good = {"version": 1, "inner_commands": 1, "inner_cleanup_verified": True,
                "inner_active_processes": 0, "mark": "verified", "stream": "stdout",
                "eligibility_sha256": "a" * 64, "terminal_written": False}
        raw = json.dumps(good, sort_keys=True, separators=(",", ":")).encode("ascii")
        self.assertEqual(subject.read_coordinator_ready(raw), good)
        for field, wrong in (("inner_cleanup_verified", False), ("inner_active_processes", 1),
                             ("terminal_written", True), ("inner_commands", 2), ("mark", "uncertain")):
            bad = dict(good, **{field: wrong})
            with self.assertRaises(subject.ControlError):
                subject.read_coordinator_ready(json.dumps(bad, sort_keys=True, separators=(",", ":")).encode())

    def test_whole_packet_has_exact_population_and_owned_coordinator_cleanup(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, _, _ = self.runtime(SharingNative())
            runtime.owner_factory = SyntheticCoordinatorOwners()
            runtime.terminate_coordinator = lambda owner: setattr(owner, "stopped", True)
            counts, outcomes = [], []
            with contextlib.redirect_stdout(io.StringIO()):
                for control_id in subject.CONTROL_IDS:
                    before = len(runtime.owners) + runtime.nested_command_slots
                    evidence = subject.run_control(control_id, Path(temporary).resolve() / control_id, runtime)
                    counts.append(len(runtime.owners) + runtime.nested_command_slots - before)
                    outcomes.append(evidence["retention"])
                    self.assertLessEqual(len(json.dumps(evidence).encode("ascii")), 16384)
            self.assertEqual(counts, [1] * 12 + [2])
            self.assertEqual(outcomes, ["disposition_verified"] + ["unknown"] * 12)
            self.assertEqual((len(runtime.owners), runtime.nested_command_slots), (13, 1))
            self.assertTrue(runtime.cleanup())
            self.assertFalse(any(api.handles or api.close_uncertain for api in runtime.apis))

    def test_cleanup_reports_native_close_uncertainty_without_retry(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, _, native = self.runtime()
            pair = subject.prepare_pair(Path(temporary).resolve() / "new", runtime)
            native.failures = {("close", "stdout.bin")}
            outcome = pair.retire()
            self.assertEqual((outcome["complete"], outcome["retention"]), (False, "unknown"))
            self.assertEqual(runtime.cleanup(), False)
            self.assertEqual(native.events.count(("close", "stdout.bin", "capture")), 1)

    def test_unexpected_sharing_stays_primary_when_native_cleanup_also_fails(self):
        class BrokenSharing(SharingNative):
            def _open(self, path, kind):
                self.opens.append((0x80010000 if kind == "capture" else 0x80000000, 1, 3, 0x08200000))
                return FakeNative._open(self, path, kind)
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            native = BrokenSharing()
            native.failures = {("close", "stdout.bin")}
            runtime, _, _ = self.runtime(native)
            with self.assertRaisesRegex(subject.ControlError, "control_native_sharing_unexpected"):
                subject.run_control("snapshot_share_receipt_success", Path(temporary).resolve() / "new", runtime)
            self.assertEqual(runtime.cleanup(), False)
            self.assertEqual(native.handles, {})

    def test_shared_admission_and_resource_failure_never_launch_an_extra_pair(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            runtime, owners, _ = self.runtime()
            runtime.nested_command_slots = 35
            with self.assertRaisesRegex(subject.ControlError, "control_stream_cap"):
                runtime.launch(Path(temporary).resolve() / "command-0001", b"", b"")
            self.assertEqual(len(owners.owners), 0)
            runtime.nested_command_slots = 0
            runtime.resource_check = lambda: (_ for _ in ()).throw(subject.ControlError("control_stream_cap"))
            with self.assertRaisesRegex(subject.ControlError, "control_stream_cap"):
                runtime.launch(Path(temporary).resolve() / "command-0001", b"", b"")
            self.assertEqual(len(owners.owners), 0)

    def test_unknown_control_and_work_expiry_never_create_a_destination(self):
        with tempfile.TemporaryDirectory(prefix="compact-packet-synthetic-") as temporary:
            root = Path(temporary).resolve() / "new"
            runtime, owners, _ = self.runtime()
            with self.assertRaisesRegex(subject.ControlError, "control_proof_failed"):
                subject.run_control("PRIVATE unknown control", root, runtime)
            runtime.work_deadline = runtime.clock() - 1
            with self.assertRaisesRegex(subject.ControlError, "control_deadline"):
                subject.run_control("snapshot_share_receipt_success", root, runtime)
            self.assertFalse(root.exists())
            self.assertEqual(len(owners.owners), 0)


if __name__ == "__main__":
    unittest.main()
