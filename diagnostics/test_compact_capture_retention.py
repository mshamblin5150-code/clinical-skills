"""Synthetic coordinator-seam checks, not native Windows qualification."""
from pathlib import Path
from dataclasses import replace
import hashlib
import json
import os
import stat
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from compact_capture_retention import CompactRefused, CompactStore
from generated_output_contract import WindowsSnapshot
from windows_job_probe import ProbeResult, ProbeSnapshot


class FakeNative:
    """Handle/disposition model for freshly created synthetic fixtures only.

    Native IDs here are synthetic stat-derived values, not a production mapping.
    A successful model disposition is observable without deleting real files.
    """
    def __init__(self):
        self.handles, self.disposed, self.events = {}, [], []
        self.failure = None
        self.read_fail_at = None
        self.reads = {}
        self.failures = set()
        self.barrier = None
        self.mark_barriers = []

    def from_fd(self, fd):
        return fd

    def record(self, handle):
        item = os.fstat(handle)
        return WindowsSnapshot(item.st_dev, item.st_ino, stat.S_IFREG | 0o666,
                               item.st_nlink, item.st_size, item.st_mtime_ns,
                               item.st_ctime_ns, 0, item.st_ctime_ns, 1, 0, False)

    def open(self, path):
        return self._open(path, "receipt")

    def open_capture(self, path):
        return self._open(path, "capture")

    def _open(self, path, kind):
        if ("open", Path(path).name) in self.failures:
            raise PermissionError("PRIVATE sharing refusal")
        handle = os.open(path, os.O_RDONLY)
        self.handles[handle] = {"path": Path(path), "kind": kind, "marked": False}
        self.events.append(("open", Path(path).name, kind))
        return handle

    def read(self, handle, limit, deadline):
        name = self.handles[handle]["path"].name
        self.reads[name] = self.reads.get(name, 0) + 1
        os.lseek(handle, 0, os.SEEK_SET)
        raw = os.read(handle, limit + 1)
        return raw + b"tampered" if self.read_fail_at == (name, self.reads[name]) else raw

    def mark_delete(self, handle):
        row = self.handles[handle]
        self.mark_barriers.append(tuple(sorted((r["path"].name, r["kind"]) for r in self.handles.values())))
        self.events.append(("mark", row["path"].name, row["kind"]))
        if ("mark", row["path"].name) in self.failures:
            raise OSError("PRIVATE mark error")
        self.handles[handle]["marked"] = True

    def close(self, handle):
        row = self.handles.pop(handle)
        self.events.append(("close", row["path"].name, row["kind"]))
        if row["marked"]:
            self.disposed.append(row["path"].name)
        os.close(handle)
        if ("close", row["path"].name) in self.failures:
            raise OSError("PRIVATE close error after uncertain side effect")


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.private = tempfile.TemporaryDirectory(prefix="compact-synthetic-")
        self.addCleanup(self.private.cleanup)
        self.root = Path(self.private.name).resolve()

    def prepared(self, code=0):
        api = FakeNative()
        store = CompactStore(self.root, time.monotonic() + 30, api=api)
        report = self.root / "command-0001"
        ticket = store.reserve(self.root, report, {"source_sha": "a" * 40})
        report.mkdir()
        paths = (report / "stdout.bin", report / "stderr.bin")
        raw = (b"synthetic output", b"synthetic diagnostic")
        reads = []
        for path, data in zip(paths, raw):
            path.write_bytes(data)
            with path.open("rb") as stream:
                reads.append((data, api.record(stream.fileno())))
        snapshot = ProbeSnapshot(71, code, True, 0, 1, 0.1, 0.2, 0.3, True, "closed")
        result = ProbeResult(snapshot, "completed", str(paths[0]), str(paths[1]), ())
        owner = SimpleNamespace(report_dir=report, stdout_path=paths[0], stderr_path=paths[1],
                                result=result, _info=SimpleNamespace(dwProcessId=71))
        return store, api, ticket, owner, result, tuple(reads)

    def test_reservation_requires_a_fresh_invocation_and_absent_report(self):
        store = CompactStore(self.root, time.monotonic() + 30, api=object())
        ticket = store.reserve(self.root, self.root / "command-0001", {"source_sha": "a" * 40})
        self.assertIsNotNone(ticket)
        report = self.root / "command-0002"
        report.mkdir()
        (report / "stdout.bin").write_bytes(b"synthetic retained evidence")
        with self.assertRaisesRegex(CompactRefused, "report_not_fresh"):
            store.reserve(self.root, report, {"source_sha": "a" * 40})
        self.assertEqual((report / "stdout.bin").read_bytes(), b"synthetic retained evidence")
        self.assertTrue(store.blocked)
        with self.assertRaisesRegex(CompactRefused, "root_not_fresh"):
            CompactStore(self.root, time.monotonic() + 30, api=object())

    def test_register_binds_original_complete_owner_result_and_native_reads(self):
        store, api, ticket, owner, result, reads = self.prepared()
        self.assertEqual(store.register(ticket, owner, result, reads), {"registered": True, "pair": 1})
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.result.snapshot.root_pid, 71)
        with self.assertRaisesRegex(CompactRefused, "ticket_state"):
            store.register(ticket, owner, result, reads)
        self.assertTrue(store.blocked)

    def test_a_substituted_equal_result_cannot_register(self):
        store, api, ticket, owner, result, reads = self.prepared()
        with self.assertRaisesRegex(CompactRefused, "owner_result"):
            store.register(ticket, owner, replace(result), reads)
        self.assertEqual((owner.stdout_path.read_bytes(), owner.stderr_path.read_bytes()),
                         (b"synthetic output", b"synthetic diagnostic"))
        self.assertTrue(store.blocked)

    def helper_evidence(self, reads, category="validated_helper"):
        result = {"category": category}
        for name, (raw, _) in zip(("stdout", "stderr"), reads):
            result[name + "_bytes"] = len(raw)
            result[name + "_sha256"] = hashlib.sha256(raw).hexdigest()
        return {"completed": True, "validated": True, "original_success": True, "result": result}

    def test_receipt_writer_has_read_capability_for_native_metadata(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        readable_writers = []
        def require_readable(fd):
            # A real descriptor read refuses O_WRONLY even with a zero limit.
            self.assertEqual(os.read(fd, 0), b"")
            readable_writers.append(fd)
            return fd
        api.from_fd = require_readable
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertTrue(outcome["complete"])
        self.assertEqual(len(readable_writers), 3)
        self.assertEqual(api.handles, {})

    def test_receipt_writer_close_finalizes_times_before_retained_readonly_snapshot(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_record = api.record
        def close_finalized_record(handle):
            snapshot = original_record(handle)
            if handle not in api.handles:
                return replace(snapshot, st_mtime_ns=snapshot.st_mtime_ns - 100,
                               st_ctime_ns=snapshot.st_ctime_ns - 200)
            return snapshot
        api.record = close_finalized_record
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertTrue(outcome["complete"])
        self.assertEqual(api.disposed, ["stdout.bin", "stderr.bin"])
        self.assertEqual(api.events.count(("open", "compact-000001-eligibility.json", "receipt")), 1)
        self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 1)
        self.assertEqual(api.reads["compact-000001-eligibility.json"], 2)
        self.assertEqual(api.handles, {})

    def test_receipt_handoff_rejects_every_nontime_identity_or_safety_change(self):
        changes = {"st_dev": 1, "st_ino": 1, "st_birthtime_ns": 1, "st_size": 1,
                   "st_mode": 1, "st_nlink": 1, "st_file_attributes": 0x400,
                   "file_type": 1, "reparse_tag": 1, "delete_pending": True}
        for field, increment in changes.items():
            with self.subTest(field=field):
                case = RetentionTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
                store, api, ticket, owner, result, reads = case.prepared()
                store.register(ticket, owner, result, reads)
                original_record = api.record
                def changed_receipt(handle):
                    snapshot = original_record(handle)
                    row = api.handles.get(handle)
                    if row and row["path"].name == "compact-000001-eligibility.json":
                        value = True if field == "delete_pending" else getattr(snapshot, field) + increment
                        return replace(snapshot, **{field: value})
                    return snapshot
                api.record = changed_receipt
                outcome = store.retire(ticket, "helper_result", case.helper_evidence(reads))
                self.assertFalse(outcome["complete"])
                self.assertEqual(api.disposed, [])
                self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")
                self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 1)
                self.assertEqual(api.handles, {})

    def test_same_length_receipt_byte_change_keeps_primary_when_authority_close_fails(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_read = api.read
        def changed_bytes(handle, limit, deadline):
            raw = original_read(handle, limit, deadline)
            return raw[:-1] + b"!" if api.handles[handle]["kind"] == "receipt" else raw
        api.read = changed_bytes
        api.failures = {("close", "compact-000001-eligibility.json")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_bytes_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(outcome["receipt_authority"]["close"], "uncertain")
        self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 1)
        self.assertEqual(api.handles, {})

    def test_receipt_read_failure_keeps_primary_and_closes_owned_authority_once(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_read = api.read
        def failed_read(handle, limit, deadline):
            if api.handles[handle]["path"].name == "compact-000001-eligibility.json":
                raise OSError("PRIVATE receipt read failure")
            return original_read(handle, limit, deadline)
        api.read = failed_read
        api.failures = {("close", "compact-000001-eligibility.json")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_eligibility_receipt_failed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 1)
        self.assertEqual(api.handles, {})
        self.assertNotIn("PRIVATE", json.dumps(outcome))

    def test_receipt_acquisition_failure_keeps_primary_over_capture_close_failure(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("open", "compact-000001-eligibility.json"), ("close", "stdout.bin")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual(outcome["reason"], "compact_eligibility_receipt_failed")
        self.assertEqual(api.disposed, [])
        self.assertEqual(api.events.count(("close", "stdout.bin", "capture")), 1)
        self.assertEqual(api.events.count(("close", "stderr.bin", "capture")), 1)
        self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 0)
        self.assertEqual(api.handles, {})

    def test_outcome_and_terminal_readonly_close_failures_never_report_success(self):
        for kind in ("outcome", "terminal"):
            with self.subTest(kind=kind):
                case = RetentionTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
                store, api, ticket, owner, result, reads = case.prepared()
                store.register(ticket, owner, result, reads)
                name = "compact-000001-%s.json" % kind
                api.failures = {("close", name)}
                outcome = store.retire(ticket, "helper_result", case.helper_evidence(reads))
                self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_record_close_failed"))
                self.assertEqual(api.events.count(("close", name, "receipt")), 1)
                self.assertEqual(api.handles, {})

    def test_receipt_writer_refuses_unreadable_before_query_and_closes_once(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        writers, queried = [], []
        original_open = Path.open
        class UnreadableWriter:
            def __init__(self, stream):
                self.stream, self.close_calls, self.readable_calls = stream, 0, 0
            def __getattr__(self, name):
                return getattr(self.stream, name)
            def readable(self):
                self.readable_calls += 1
                return False
            def close(self):
                self.close_calls += 1
                self.stream.close()
        def open_writer(path, *args, **kwargs):
            writer = UnreadableWriter(original_open(path, *args, **kwargs))
            writers.append(writer)
            return writer
        def from_fd(fd):
            queried.append(fd)
            return fd
        api.from_fd = from_fd
        with patch.object(Path, "open", open_writer):
            outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual(outcome["reason"], "compact_receipt_writer_unreadable")
        self.assertEqual(queried, [])
        self.assertEqual(len(writers), 3)
        self.assertTrue(all(w.close_calls == w.readable_calls == 1 and w.stream.closed for w in writers))
        self.assertEqual(api.disposed, [])
        self.assertEqual(api.handles, {})

    def test_receipt_writer_close_failure_never_transfers_and_keeps_prior_write_failure(self):
        for prior_failure in (False, True):
            with self.subTest(prior_failure=prior_failure):
                case = RetentionTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
                store, api, ticket, owner, result, reads = case.prepared()
                store.register(ticket, owner, result, reads)
                writers = []
                original_open = Path.open
                class FailingWriter:
                    def __init__(self, stream):
                        self.stream, self.close_calls = stream, 0
                    def __getattr__(self, name):
                        return getattr(self.stream, name)
                    def write(self, raw):
                        if prior_failure:
                            raise CompactRefused("compact_receipt_write_failed")
                        return self.stream.write(raw)
                    def close(self):
                        self.close_calls += 1
                        self.stream.close()
                        raise OSError("PRIVATE writer close failure")
                def open_writer(path, *args, **kwargs):
                    writer = FailingWriter(original_open(path, *args, **kwargs))
                    writers.append(writer)
                    return writer
                with patch.object(Path, "open", open_writer):
                    outcome = store.retire(ticket, "helper_result", case.helper_evidence(reads))
                expected = "compact_receipt_write_failed" if prior_failure else "compact_receipt_writer_close_failed"
                self.assertEqual(outcome["reason"], expected)
                self.assertTrue(all(w.close_calls == 1 and w.stream.closed for w in writers))
                self.assertFalse(any(event[0] == "open" and event[2] == "receipt" for event in api.events))
                self.assertEqual(api.disposed, [])
                self.assertEqual(api.handles, {})

    def test_receipt_handoff_does_not_relax_later_receipt_timestamps(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_record = api.record
        def later_timestamp_change(handle):
            snapshot = original_record(handle)
            row = api.handles.get(handle)
            if row and row["kind"] == "receipt" and api.reads.get(row["path"].name, 0):
                return replace(snapshot, st_mtime_ns=snapshot.st_mtime_ns + 100,
                               st_ctime_ns=snapshot.st_ctime_ns + 200)
            return snapshot
        api.record = later_timestamp_change
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_bytes_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(api.handles, {})

    def test_receipt_handoff_never_relaxes_registered_capture_timestamps(self):
        for field in ("st_mtime_ns", "st_ctime_ns"):
            with self.subTest(field=field):
                case = RetentionTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
                store, api, ticket, owner, result, reads = case.prepared()
                altered = ((reads[0][0], replace(reads[0][1], **{field: getattr(reads[0][1], field) - 100})), reads[1])
                store.register(ticket, owner, result, altered)
                outcome = store.retire(ticket, "helper_result", case.helper_evidence(reads))
                self.assertEqual(outcome["reason"], "compact_native_identity_changed")
                self.assertEqual(api.disposed, [])
                self.assertEqual(api.handles, {})

    def test_last_validated_consumer_retains_three_bounded_receipts_before_reporting_success(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], api.disposed),
                         (True, "disposition_verified", ["stdout.bin", "stderr.bin"]))
        receipts = sorted(self.root.glob("compact-*.json"))
        self.assertEqual(len(receipts), 3)
        eligibility = json.loads(next(path for path in receipts if "eligibility" in path.name).read_bytes())
        terminal = json.loads(next(path for path in receipts if "terminal" in path.name).read_bytes())
        self.assertEqual(eligibility["evidence"], self.helper_evidence(reads))
        self.assertEqual(terminal["receipt_authority"], {"recheck": "verified", "close": "verified"})
        self.assertNotIn(str(self.root), json.dumps(outcome))
        self.assertTrue(all(path.stat().st_size <= 16384 for path in receipts))
        self.assertEqual(api.handles, {})

    def test_failure_before_receipt_flush_retains_both_and_stops_new_work(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        with patch("compact_capture_retention.os.fsync", side_effect=OSError("PRIVATE flush error")):
            outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_eligibility_receipt_failed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")
        with self.assertRaisesRegex(CompactRefused, "compact_store_blocked"):
            store.reserve(self.root, self.root / "command-0002", {"source_sha": "a" * 40})
        self.assertEqual(api.handles, {})

    def test_second_mark_failure_is_partial_unknown_and_never_retried(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("mark", "stderr.bin"), ("close", "stderr.bin")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], outcome["reason"]),
                         (False, "unknown", "compact_disposition_failed"))
        self.assertEqual(api.disposed, ["stdout.bin"])
        self.assertEqual(outcome["streams"][1], {"stream": "stderr", "mark": "uncertain", "close": "uncertain"})
        before = list(api.events)
        with self.assertRaisesRegex(CompactRefused, "compact_store_blocked"):
            store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual(api.events, before)
        self.assertNotIn("PRIVATE", json.dumps(outcome))

    def test_changed_native_identity_retains_exact_original_bytes(self):
        store, api, ticket, owner, result, reads = self.prepared()
        wrong = ((reads[0][0], replace(reads[0][1], st_ino=2 ** 120)), reads[1])
        store.register(ticket, owner, result, wrong)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_native_identity_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")

    def test_receipt_recheck_failure_after_disposition_remains_unknown(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.read_fail_at = ("compact-000001-eligibility.json", 2)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], api.disposed),
                         (False, "unknown", ["stdout.bin", "stderr.bin"]))
        self.assertEqual(outcome["receipt_authority"], {"recheck": "uncertain", "close": "verified"})
        terminal = json.loads((self.root / "compact-000001-terminal.json").read_bytes())
        self.assertEqual(terminal["first_failure"], "compact_bytes_changed")

    def test_invalid_final_consumer_cannot_mark_even_complete_owner(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        evidence = self.helper_evidence(reads)
        evidence["validated"] = False
        outcome = store.retire(ticket, "helper_result", evidence)
        self.assertEqual(outcome["reason"], "compact_final_consumer_invalid")
        self.assertEqual((outcome["complete"], api.disposed), (False, []))
        self.assertEqual(owner.stderr_path.read_bytes(), b"synthetic diagnostic")

    def test_outer_and_measured_reservations_have_separate_finite_bounds(self):
        store = CompactStore(self.root, time.monotonic() + 30, api=object())
        capture = self.root / "cap1-captures"
        capture.mkdir()
        store.add_capture_root(capture)
        for ordinal in range(1, 1601):
            store.reserve(self.root, self.root / ("command-%04d" % ordinal), {"source_sha": "a" * 40})
        for ordinal in range(1, 585):
            store.reserve(capture, capture / ("command-%04d" % ordinal), {"source_sha": "a" * 40})
        self.assertEqual(store.remaining_receipt_bytes, 107347968)
        with self.assertRaisesRegex(CompactRefused, "compact_pair_limit"):
            store.reserve(capture, capture / "command-0585", {"source_sha": "a" * 40})
        self.assertTrue(store.blocked)

    def test_outer_limit_cannot_spend_the_measured_reserve(self):
        store = CompactStore(self.root, time.monotonic() + 30, api=object())
        for ordinal in range(1, 1601):
            store.reserve(self.root, self.root / ("command-%04d" % ordinal), {"source_sha": "a" * 40})
        with self.assertRaisesRegex(CompactRefused, "compact_outer_pair_limit"):
            store.reserve(self.root, self.root / "command-1601", {"source_sha": "a" * 40})
        self.assertTrue(store.blocked)

    def test_expected_reader_nonzero_is_eligible_only_through_original_validated_row(self):
        store, api, ticket, owner, result, reads = self.prepared(code=1)
        store.register(ticket, owner, result, reads)
        evidence = self.helper_evidence(reads)
        evidence["result"].update(completion="completed", classification="reader", returncode=1,
                                  screen_clean=True, capture_read_verified=True,
                                  cleanup_verified=True, root_identity_verified=True,
                                  test_count=1, failures=1, errors=0, skipped=0, expected_failures=0,
                                  owned_wall_seconds=0.3, tree_cpu_seconds=0.1 + 0.2,
                                  call_wall_seconds=0.3, analysis_seconds=0.01)
        outcome = store.retire(ticket, "planted_method", evidence)
        self.assertEqual((outcome["complete"], api.disposed), (True, ["stdout.bin", "stderr.bin"]))

    def test_bad_root_pid_cannot_register_even_an_equal_owner_result(self):
        store, api, ticket, owner, result, reads = self.prepared()
        owner._info.dwProcessId = 72
        with self.assertRaisesRegex(CompactRefused, "compact_owner_pid_changed"):
            store.register(ticket, owner, result, reads)
        self.assertEqual(owner.result.snapshot.root_pid, 71)
        self.assertTrue(store.blocked)

    def test_hardlink_snapshot_cannot_register(self):
        store, api, ticket, owner, result, reads = self.prepared()
        unsafe = ((reads[0][0], replace(reads[0][1], st_nlink=2)), reads[1])
        with self.assertRaisesRegex(CompactRefused, "compact_native_snapshot_invalid"):
            store.register(ticket, owner, result, unsafe)
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")
        self.assertTrue(store.blocked)

    def test_two_stream_names_cannot_register_one_native_object(self):
        store, api, ticket, owner, result, reads = self.prepared()
        alias = (reads[0], reads[0])
        with self.assertRaisesRegex(CompactRefused, "compact_stream_alias"):
            store.register(ticket, owner, result, alias)
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")
        self.assertTrue(store.blocked)

    def test_changed_bytes_under_the_same_snapshot_cannot_be_disposed(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.read_fail_at = ("stdout.bin", 1)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_bytes_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")

    def test_receipt_readback_failure_prevents_either_disposition(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.read_fail_at = ("compact-000001-eligibility.json", 1)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_bytes_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stderr_path.read_bytes(), b"synthetic diagnostic")

    def test_authority_close_failure_is_recorded_in_terminal_without_success(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("close", "compact-000001-eligibility.json")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_authority_close_failed"))
        terminal = json.loads((self.root / "compact-000001-terminal.json").read_bytes())
        self.assertEqual(terminal["receipt_authority"]["close"], "uncertain")
        self.assertEqual(api.disposed, ["stdout.bin", "stderr.bin"])

    def test_measured_counts_and_timings_cannot_be_missing(self):
        store, api, ticket, owner, result, reads = self.prepared(code=1)
        store.register(ticket, owner, result, reads)
        evidence = self.helper_evidence(reads)
        evidence["result"].update(completion="completed", classification="reader", returncode=1,
                                  screen_clean=True, capture_read_verified=True,
                                  cleanup_verified=True, root_identity_verified=True)
        outcome = store.retire(ticket, "measured_pair", evidence)
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_original_metrics_invalid"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")

    def test_terminal_readback_failure_does_not_claim_a_verified_result(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.read_fail_at = ("compact-000001-terminal.json", 1)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], outcome["receipt_files"]["terminal"]),
                         (False, "unknown", None))
        terminal = json.loads((self.root / "compact-000001-terminal.json").read_bytes())
        self.assertEqual(terminal["terminal_readback"], "not_asserted_by_this_record")
        self.assertEqual(api.disposed, ["stdout.bin", "stderr.bin"])

    def test_both_capture_handles_and_receipt_authority_precede_first_mark(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertTrue(outcome["complete"])
        self.assertEqual(api.mark_barriers[0], (("compact-000001-eligibility.json", "receipt"),
                                               ("stderr.bin", "capture"), ("stdout.bin", "capture")))
        authority_close = api.events.index(("close", "compact-000001-eligibility.json", "receipt"))
        self.assertLess(api.events.index(("close", "stderr.bin", "capture")), authority_close)
        self.assertLess(api.events.index(("close", "compact-000001-outcome.json", "receipt")), authority_close)
        self.assertEqual(api.disposed, ["stdout.bin", "stderr.bin"])

    def test_second_capture_sharing_refusal_preserves_both(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("open", "stderr.bin")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_capture_acquisition_failed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"synthetic output")

    def test_receipt_authority_sharing_refusal_preserves_both(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("open", "compact-000001-eligibility.json")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_eligibility_receipt_failed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stderr_path.read_bytes(), b"synthetic diagnostic")

    def test_missing_terminal_after_disposition_stays_unknown(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_open = Path.open
        def fail_terminal(path, *args, **kwargs):
            if path.name == "compact-000001-terminal.json":
                raise PermissionError("PRIVATE terminal unavailable")
            return original_open(path, *args, **kwargs)
        with patch.object(Path, "open", fail_terminal):
            outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], outcome["reason"]),
                         (False, "unknown", "compact_terminal_receipt_failed"))
        self.assertEqual(api.disposed, ["stdout.bin", "stderr.bin"])
        self.assertFalse((self.root / "compact-000001-terminal.json").exists())
        eligibility = json.loads((self.root / "compact-000001-eligibility.json").read_bytes())
        self.assertEqual(eligibility["retention"], "intent_only_unknown_without_authenticated_terminal")

    def test_replaced_report_directory_cannot_authorize_old_stream_paths(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        report = owner.report_dir
        report.rename(self.root / "synthetic-original-report")
        report.mkdir()
        owner.stdout_path.write_bytes(b"new synthetic output")
        owner.stderr_path.write_bytes(b"new synthetic diagnostic")
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_directory_changed"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stdout_path.read_bytes(), b"new synthetic output")

    def test_oversize_private_receipt_never_marks_either_stream(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        evidence = self.helper_evidence(reads)
        evidence["result"]["private_control"] = "x" * 16384
        outcome = store.retire(ticket, "helper_result", evidence)
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_receipt_limit"))
        self.assertEqual(api.disposed, [])
        self.assertEqual(owner.stderr_path.read_bytes(), b"synthetic diagnostic")

    def test_public_summary_accounts_for_pending_and_complete_without_more_native_work(self):
        store, api, ticket, owner, result, reads = self.prepared()
        pending = store.public_summary()
        self.assertEqual((pending["reserved_pairs"], pending["retired_complete_pairs"],
                          pending["pending_pairs"], pending["receipt_files_written"],
                          pending["blocked"], pending["all_retired_verified"]),
                         (1, 0, 1, 0, False, False))
        self.assertEqual(pending["receipt_chain_sha256"],
                         hashlib.sha256(b"[[null,null,null]]").hexdigest())
        store.register(ticket, owner, result, reads)
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        before = list(api.events)
        summary = store.public_summary()
        self.assertEqual((summary["reserved_pairs"], summary["retired_complete_pairs"],
                          summary["pending_pairs"], summary["receipt_files_written"],
                          summary["blocked"], summary["first_failure"], summary["all_retired_verified"]),
                         (1, 1, 0, 3, False, None, True))
        triplet = [outcome["receipt_files"][kind] for kind in ("eligibility", "outcome", "terminal")]
        self.assertEqual(summary["receipt_chain_sha256"],
                         hashlib.sha256(json.dumps([triplet], separators=(",", ":")).encode()).hexdigest())
        outcome["receipt_files"]["terminal"] = "caller mutation"
        summary["retired_complete_pairs"] = 999
        self.assertEqual(store.public_summary()["retired_complete_pairs"], 1)
        self.assertEqual(store.public_summary()["receipt_chain_sha256"],
                         hashlib.sha256(json.dumps([triplet], separators=(",", ":")).encode()).hexdigest())
        self.assertEqual(api.events, before)
        self.assertNotIn(str(self.root), json.dumps(store.public_summary()))
        store.reserve(self.root, self.root / "command-0002", {"source_sha": "a" * 40})
        mixed = store.public_summary()
        self.assertEqual((mixed["reserved_pairs"], mixed["retired_complete_pairs"],
                          mixed["pending_pairs"], mixed["all_retired_verified"]), (2, 1, 1, False))
        self.assertEqual(mixed["receipt_chain_sha256"], hashlib.sha256(
            json.dumps([triplet, [None, None, None]], separators=(",", ":")).encode()).hexdigest())

    def test_public_summary_keeps_partial_failure_inconclusive_without_sensitive_details(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        api.failures = {("mark", "stderr.bin"), ("close", "stderr.bin")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        summary = store.public_summary()
        self.assertEqual((summary["reserved_pairs"], summary["retired_complete_pairs"],
                          summary["pending_pairs"], summary["receipt_files_written"],
                          summary["blocked"], summary["first_failure"], summary["all_retired_verified"]),
                         (1, 0, 1, 3, True, "compact_disposition_failed", False))
        self.assertEqual(outcome["streams"][0]["mark"], "verified")
        self.assertEqual(outcome["streams"][1]["mark"], "uncertain")
        self.assertNotIn("PRIVATE", json.dumps(summary))
        self.assertNotIn(str(self.root), json.dumps(summary))

    def test_injected_compact_refusal_cannot_publish_arbitrary_private_text(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        def untrusted_failure(handle):
            raise CompactRefused("PRIVATE_SENTINEL")
        api.mark_delete = untrusted_failure
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]),
                         (False, "compact_disposition_failed"))
        summary = store.public_summary()
        self.assertEqual(summary["first_failure"], "compact_disposition_failed")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(outcome))
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(summary))
        self.assertNotIn(b"PRIVATE_SENTINEL", b"".join(path.read_bytes() for path in self.root.glob("compact-*.json")))

    def test_expiry_during_first_raw_close_never_starts_second_mark(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_close = api.close
        def close_and_expire(handle):
            name = api.handles[handle]["path"].name
            original_close(handle)
            if name == "stdout.bin":
                store.deadline = time.monotonic() - 1
        api.close = close_and_expire
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["retention"], outcome["reason"]),
                         (False, "unknown", "compact_deadline_exhausted"))
        self.assertEqual(api.disposed, ["stdout.bin"])
        self.assertEqual([event for event in api.events if event[0] == "mark"],
                         [("mark", "stdout.bin", "capture")])
        self.assertEqual(outcome["streams"], [
            {"stream": "stdout", "mark": "verified", "close": "verified"},
            {"stream": "stderr", "mark": "not_requested", "close": "verified"}])
        self.assertEqual(owner.stderr_path.read_bytes(), b"synthetic diagnostic")
        self.assertEqual(api.events.count(("close", "stdout.bin", "capture")), 1)
        self.assertEqual(api.events.count(("close", "stderr.bin", "capture")), 1)
        self.assertEqual(api.events.count(("close", "compact-000001-eligibility.json", "receipt")), 1)
        self.assertEqual(api.handles, {})
        self.assertFalse(store.public_summary()["all_retired_verified"])
        self.assertEqual(store.public_summary()["pending_pairs"], 1)

    def test_expiry_during_started_first_mark_still_closes_once_and_keeps_primary_deadline(self):
        store, api, ticket, owner, result, reads = self.prepared()
        store.register(ticket, owner, result, reads)
        original_mark = api.mark_delete
        def mark_and_expire(handle):
            original_mark(handle)
            store.deadline = time.monotonic() - 1
        api.mark_delete = mark_and_expire
        api.failures = {("close", "stderr.bin")}
        outcome = store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual((outcome["complete"], outcome["reason"]), (False, "compact_deadline_exhausted"))
        self.assertEqual(api.disposed, ["stdout.bin"])
        self.assertEqual(outcome["streams"][1],
                         {"stream": "stderr", "mark": "not_requested", "close": "uncertain"})
        self.assertEqual(api.events.count(("close", "stdout.bin", "capture")), 1)
        self.assertEqual(api.events.count(("close", "stderr.bin", "capture")), 1)
        self.assertEqual(api.handles, {})
        before = list(api.events)
        with self.assertRaisesRegex(CompactRefused, "compact_store_blocked"):
            store.retire(ticket, "helper_result", self.helper_evidence(reads))
        self.assertEqual(api.events, before)


if __name__ == "__main__":
    unittest.main()
