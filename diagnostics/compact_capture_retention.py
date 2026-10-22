"""Bounded, invocation-local compact retention; never a path-unlink fallback.

Windows sharing/metadata qualification is separate from portable coordinator
tests. Flush acknowledgment does not promise power-loss durability, permanent
receipt protection, secure erasure, or reclaimed storage. Missing or unread
terminal evidence always means unknown retention and an inconclusive run.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time
from dataclasses import asdict

import generated_output_contract as contract
from windows_job_probe import ProbeResult, ProbeSnapshot


MAX_OUTER_PAIRS = 1600
MAX_MEASURED_PAIRS = 584
MAX_PAIRS = MAX_OUTER_PAIRS + MAX_MEASURED_PAIRS
MAX_RECEIPT_BYTES = 16 * 1024
RECEIPTS_PER_PAIR = 3
MAX_RECEIPT_FILES = MAX_PAIRS * RECEIPTS_PER_PAIR
MAX_TOTAL_RECEIPT_BYTES = MAX_RECEIPT_FILES * MAX_RECEIPT_BYTES
FINAL_CONSUMERS = frozenset({"measured_pair", "planted_method", "outer_control", "helper_result"})
SOURCE_BINDINGS = frozenset({"source_sha", "candidate_sha256", "payload_sha256",
                             "source_manifest_sha256", "interpreter_sha256",
                             "command_token", "owner_token", "clone_root_token", "pair_token"})
REASONS = frozenset({
    "compact_authority_close_failed", "compact_authority_recheck_failed", "compact_bytes_changed",
    "compact_capture_acquisition_failed", "compact_capture_close_failed", "compact_capture_root_failed",
    "compact_capture_root_invalid", "compact_deadline_exhausted", "compact_deadline_invalid",
    "compact_directory_changed", "compact_directory_invalid", "compact_disposition_failed",
    "compact_eligibility_receipt_failed", "compact_evidence_changed", "compact_final_consumer_invalid",
    "compact_measured_pair_limit", "compact_native_identity_changed", "compact_native_snapshot_invalid",
    "compact_original_metrics_invalid", "compact_original_result_invalid", "compact_outcome_receipt_failed",
    "compact_outer_pair_limit", "compact_owner_incomplete", "compact_owner_metrics_invalid",
    "compact_owner_pid_changed", "compact_owner_result_changed", "compact_owner_reused", "compact_pair_limit",
    "compact_receipt_limit", "compact_receipt_write_failed", "compact_receipt_writer_close_failed",
    "compact_receipt_writer_unreadable",
    "compact_record_close_failed", "compact_registration_failed", "compact_report_invalid",
    "compact_report_not_fresh", "compact_reservation_failed", "compact_retirement_precondition_failed",
    "compact_root_not_fresh", "compact_source_binding_invalid", "compact_store_blocked",
    "compact_stream_alias", "compact_stream_reads_invalid", "compact_summary_invalid",
    "compact_terminal_receipt_failed", "compact_ticket_invalid", "compact_ticket_state",
})


class CompactRefused(RuntimeError):
    """A finite category, never raw paths, stream contents or OS messages."""


def _need(condition, reason):
    if not condition:
        raise CompactRefused(reason)


def _directory(path):
    _need(isinstance(path, Path) and path.is_absolute() and ".." not in path.parts,
          "compact_directory_invalid")
    identities = []
    for ancestor in (path, *path.parents):
        item = ancestor.lstat()
        _need(stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode)
              and not getattr(item, "st_file_attributes", 0) & 0x400,
              "compact_directory_invalid")
        identities.append((str(ancestor), item.st_dev, item.st_ino))
    _need(path.resolve(strict=True) == path, "compact_directory_invalid")
    return tuple(identities)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _native_snapshot(snapshot, size):
    _need(type(snapshot) is contract.WindowsSnapshot
          and all(type(getattr(snapshot, name)) is int for name in
                  (*contract.METADATA_FIELDS, "st_birthtime_ns", "file_type", "reparse_tag"))
          and snapshot.delete_pending is False and snapshot.file_type == 1
          and snapshot.reparse_tag == 0 and stat.S_ISREG(snapshot.st_mode)
          and snapshot.st_nlink == 1 and not snapshot.st_file_attributes & 0x400
          and 0 <= snapshot.st_size == size <= contract.MAX_FILE_BYTES,
          "compact_native_snapshot_invalid")


def _owner_result(owner, result, report):
    _need(type(result) is ProbeResult and result is owner.result
          and Path(owner.report_dir) == report
          and Path(owner.stdout_path) == Path(result.stdout_path) == report / "stdout.bin"
          and Path(owner.stderr_path) == Path(result.stderr_path) == report / "stderr.bin",
          "compact_owner_result_changed")
    snapshot = result.snapshot
    _need(type(snapshot) is ProbeSnapshot and type(snapshot.root_pid) is int
          and snapshot.root_pid > 0 and snapshot.root_pid == owner._info.dwProcessId,
          "compact_owner_pid_changed")
    _need(result.reason == "completed" and snapshot.state == "closed"
          and snapshot.cleanup_verified is True and snapshot.root_reaped is True
          and type(snapshot.active_processes) is int and snapshot.active_processes == 0,
          "compact_owner_incomplete")
    _need(type(snapshot.total_processes) is int and snapshot.total_processes > 0
          and type(snapshot.root_exit_code) is int
          and all(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1e9
                  for value in (snapshot.user_cpu_seconds, snapshot.kernel_cpu_seconds,
                                snapshot.tree_cpu_seconds, snapshot.wall_seconds)),
          "compact_owner_metrics_invalid")
    return asdict(snapshot)


class CompactStore:
    """A single invocation's reserve/register/explicit-last-consumer boundary."""
    def __init__(self, root, deadline, api=None):
        self.root, self.deadline = Path(root), deadline
        self._roots, self._tickets, self._reports = {}, {}, set()
        self._first_failure = None
        self._written = 0
        self._outer_pairs, self._measured_pairs = 0, 0
        _need(type(deadline) in (int, float) and math.isfinite(deadline)
              and time.monotonic() < deadline, "compact_deadline_invalid")
        self._roots[self.root] = _directory(self.root)
        _need(not any(self.root.iterdir()), "compact_root_not_fresh")
        if api is None:
            from compact_capture_native import WindowsCompactAPI
            api = WindowsCompactAPI()
        self.api = api

    @property
    def blocked(self):
        return self._first_failure is not None

    @property
    def first_failure(self):
        if self._first_failure is None:
            return None
        return (self._first_failure if type(self._first_failure) is str and self._first_failure in REASONS
                else "compact_retirement_precondition_failed")

    @property
    def remaining_receipt_bytes(self):
        return (MAX_RECEIPT_FILES - self._written) * MAX_RECEIPT_BYTES

    @property
    def remaining_receipt_files(self):
        return MAX_RECEIPT_FILES - self._written

    def _ready(self):
        _need(not self.blocked, "compact_store_blocked")
        _need(time.monotonic() < self.deadline, "compact_deadline_exhausted")
        for path, identity in self._roots.items():
            _need(_directory(path) == identity, "compact_directory_changed")

    def _failed(self, error, fallback):
        if self._first_failure is None:
            reason = str(error) if type(error) is CompactRefused else None
            self._first_failure = reason if reason in REASONS else (
                fallback if type(fallback) is str and fallback in REASONS
                else "compact_retirement_precondition_failed")

    def public_summary(self):
        """Read-only finite accounting, not proof the containing invocation passed.

        Pending includes failed or never-retired reservations. The digest binds
        reserved order and each returned eligibility/outcome/terminal digest,
        with null for an unavailable digest. No native reads or retries occur.
        """
        rows = sorted(self._tickets.values(), key=lambda row: row["ordinal"])
        triplets = [row.get("receipt_digests", (None, None, None)) for row in rows]
        _need(len(rows) <= MAX_PAIRS and type(self._written) is int
              and 0 <= self._written <= MAX_RECEIPT_FILES
              and all(type(triplet) is tuple and len(triplet) == 3
                      and all(value is None or type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)
                              for value in triplet) for triplet in triplets), "compact_summary_invalid")
        complete = sum(row.get("retired_verified") is True and row["state"] == "retired" for row in rows)
        encoded = json.dumps(triplets, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        reason = self.first_failure  # Revalidate the category at the public boundary.
        return {"reserved_pairs": len(rows), "retired_complete_pairs": complete,
                "pending_pairs": len(rows) - complete, "receipt_files_written": self._written,
                "blocked": self.blocked, "first_failure": reason,
                "receipt_chain_sha256": _digest(encoded),
                "all_retired_verified": not self.blocked and complete == len(rows)}

    def add_capture_root(self, root):
        _need(not self.blocked, "compact_store_blocked")
        try:
            self._ready()
            root = Path(root)
            _need(root.parent == self.root and root.name in ("cap1-captures", "cap2-captures")
                  and root not in self._roots, "compact_capture_root_invalid")
            identity = _directory(root)
            _need(not any(root.iterdir()), "compact_root_not_fresh")
            self._roots[root] = identity
        except BaseException as error:
            self._failed(error, "compact_capture_root_failed")
            raise CompactRefused(self.first_failure) from None

    def reserve(self, capture_root, report_dir, source_bindings):
        _need(not self.blocked, "compact_store_blocked")
        try:
            self._ready()
            capture_root, report_dir = Path(capture_root), Path(report_dir)
            _need(capture_root in self._roots and report_dir.parent == capture_root
                  and re.fullmatch(r"command-[0-9]{4,10}", report_dir.name),
                  "compact_report_invalid")
            _need(report_dir not in self._reports and not os.path.lexists(report_dir),
                  "compact_report_not_fresh")
            _need(len(self._tickets) < MAX_PAIRS, "compact_pair_limit")
            _need(capture_root != self.root or self._outer_pairs < MAX_OUTER_PAIRS,
                  "compact_outer_pair_limit")
            _need(capture_root == self.root or self._measured_pairs < MAX_MEASURED_PAIRS,
                  "compact_measured_pair_limit")
            _need(type(source_bindings) is dict and 0 < len(source_bindings) <= 16
                  and all(k in SOURCE_BINDINGS and type(v) is str
                          and re.fullmatch(r"[0-9a-f]{40}" if k == "source_sha" else r"[0-9a-f]{64}", v)
                          for k, v in source_bindings.items()), "compact_source_binding_invalid")
            ticket = object()
            self._tickets[ticket] = {"ordinal": len(self._tickets) + 1,
                                     "capture_root": capture_root, "report": report_dir,
                                     "source_bindings": dict(source_bindings), "state": "reserved"}
            self._reports.add(report_dir)
            if capture_root == self.root:
                self._outer_pairs += 1
            else:
                self._measured_pairs += 1
            return ticket
        except BaseException as error:
            self._failed(error, "compact_reservation_failed")
            raise CompactRefused(self.first_failure) from None

    def _ticket(self, ticket, state):
        _need(ticket in self._tickets, "compact_ticket_invalid")
        entry = self._tickets[ticket]
        _need(entry["state"] == state, "compact_ticket_state")
        return entry

    def register(self, ticket, owner, result, stream_reads):
        """Bind the exact completed result and bytes from its original reader."""
        _need(not self.blocked, "compact_store_blocked")
        try:
            self._ready()
            entry = self._ticket(ticket, "reserved")
            report = entry["report"]
            owner_summary = _owner_result(owner, result, report)
            _need(all(row.get("owner") is not owner for row in self._tickets.values()),
                  "compact_owner_reused")
            _need(type(stream_reads) is tuple and len(stream_reads) == 2,
                  "compact_stream_reads_invalid")
            streams = []
            for name, reading in zip(("stdout.bin", "stderr.bin"), stream_reads):
                _need(type(reading) is tuple and len(reading) == 2 and type(reading[0]) is bytes,
                      "compact_stream_reads_invalid")
                raw, snapshot = reading
                _native_snapshot(snapshot, len(raw))
                streams.append({"name": name, "bytes": len(raw), "sha256": _digest(raw),
                                "snapshot": snapshot})
            _need(len({(s["snapshot"].st_dev, s["snapshot"].st_ino) for s in streams}) == 2,
                  "compact_stream_alias")
            report_identity = _directory(report)
            self._ready()
            entry.update(state="registered", owner=owner, result=result,
                         owner_summary=owner_summary, streams=streams, report_identity=report_identity)
            return {"registered": True, "pair": entry["ordinal"]}
        except BaseException as error:
            self._failed(error, "compact_registration_failed")
            raise CompactRefused(self.first_failure) from None

    def _check_entry(self, entry):
        for path, identity in self._roots.items():
            _need(_directory(path) == identity, "compact_directory_changed")
        _need(_directory(entry["report"]) == entry["report_identity"], "compact_directory_changed")
        _need(_owner_result(entry["owner"], entry["result"], entry["report"])
              == entry["owner_summary"], "compact_owner_result_changed")

    def _evidence(self, entry, final_consumer, evidence):
        _need(final_consumer in FINAL_CONSUMERS and type(evidence) is dict
              and set(evidence) == {"completed", "validated", "original_success", "result"}
              and all(evidence[k] is True for k in ("completed", "validated", "original_success"))
              and type(evidence["result"]) is dict, "compact_final_consumer_invalid")
        row, code = evidence["result"], entry["result"].snapshot.root_exit_code
        if final_consumer in ("measured_pair", "planted_method", "helper_result"):
            for name, stream in zip(("stdout", "stderr"), entry["streams"]):
                _need(type(row.get(name + "_bytes")) is int
                      and row.get(name + "_bytes") == stream["bytes"]
                      and row.get(name + "_sha256") == stream["sha256"], "compact_evidence_changed")
        if final_consumer in ("measured_pair", "planted_method"):
            _need(row.get("completion") == "completed" and type(row.get("returncode")) is int
                  and row.get("returncode") == code
                  and (row.get("classification"), code) in (("reader", 1), ("nonreader", 0))
                  and all(row.get(k) is True for k in ("screen_clean", "capture_read_verified",
                          "cleanup_verified", "root_identity_verified")), "compact_original_result_invalid")
            counts = ("test_count", "failures", "errors", "skipped", "expected_failures")
            timings = ("owned_wall_seconds", "tree_cpu_seconds", "call_wall_seconds", "analysis_seconds")
            _need(all(type(row.get(k)) is int and 0 <= row[k] <= 1000000 for k in counts)
                  and row["test_count"] > 0
                  and all(type(row.get(k)) in (int, float) and math.isfinite(row[k])
                          and 0 <= row[k] <= 1e9 for k in timings)
                  and row["owned_wall_seconds"] == entry["result"].snapshot.wall_seconds
                  and row["tree_cpu_seconds"] == entry["result"].snapshot.tree_cpu_seconds,
                  "compact_original_metrics_invalid")
        elif final_consumer == "helper_result":
            _need((row.get("category") == "validated_helper" and code == 0)
                  or (row.get("category") == "detached_head" and code == 1
                      and entry["streams"][0]["bytes"] == 0), "compact_original_result_invalid")
            _need("returncode" not in row or type(row["returncode"]) is int and row["returncode"] == code,
                  "compact_original_result_invalid")
        else:
            _need(code == 0, "compact_original_result_invalid")
        # Freeze private evidence before any disposal. Complete control JSON may
        # carry private paths; none of it is copied into the public outcome.
        return json.loads(self._encode(evidence))

    def _encode(self, value):
        raw = (json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
        _need(len(raw) <= MAX_RECEIPT_BYTES, "compact_receipt_limit")
        return raw

    def _write_receipt(self, entry, kind, value):
        self._check_entry(entry)
        _need(time.monotonic() < self.deadline, "compact_deadline_exhausted")
        raw = self._encode(value)
        path = self.root / ("compact-%06d-%s.json" % (entry["ordinal"], kind))
        _need(self._written < MAX_RECEIPT_FILES, "compact_receipt_limit")
        stream = path.open("x+b")
        self._written += 1  # A partial file consumes its complete reserved slot.
        primary = None
        try:
            _need(stream.write(raw) == len(raw), "compact_receipt_write_failed")
            stream.flush()
            os.fsync(stream.fileno())
            _need(stream.readable(), "compact_receipt_writer_unreadable")
            snapshot = contract.windows_snapshot(self.api, self.api.from_fd(stream.fileno()),
                                                 MAX_RECEIPT_BYTES, path.name, self.deadline)
            _native_snapshot(snapshot, len(raw))
        except BaseException as error:
            primary = error
            raise
        finally:
            try:
                stream.close()
            except BaseException:
                if primary is None:
                    raise CompactRefused("compact_receipt_writer_close_failed") from None
        return {"path": path, "raw": raw, "snapshot": snapshot}

    def _verify(self, handle, snapshot, size, digest, limit):
        before = contract.windows_snapshot(self.api, handle, limit, "compact-evidence", self.deadline)
        _need(before == snapshot, "compact_native_identity_changed")
        raw = self.api.read(handle, limit, self.deadline)
        after = contract.windows_snapshot(self.api, handle, limit, "compact-evidence", self.deadline)
        _need(after == snapshot and type(raw) is bytes and len(raw) == size
              and _digest(raw) == digest, "compact_bytes_changed")

    def _verify_receipt(self, handle, receipt):
        self._verify(handle, receipt["snapshot"], len(receipt["raw"]),
                     _digest(receipt["raw"]), MAX_RECEIPT_BYTES)

    def _handoff_receipt(self, handle, receipt):
        """Bind the existing read handle once after the exclusive writer closed.

        Only our writer-close LastWriteTime/ChangeTime finalization is allowed
        here. Identity, creation, link/type/reparse state and exact bytes must
        survive the handoff; every subsequent read requires the full snapshot.
        """
        snapshot = contract.windows_snapshot(self.api, handle, MAX_RECEIPT_BYTES,
                                             "compact-receipt", self.deadline)
        fields = (*contract.METADATA_FIELDS, "st_birthtime_ns", "file_type", "reparse_tag", "delete_pending")
        _need(all(getattr(snapshot, name) == getattr(receipt["snapshot"], name)
                  for name in fields if name not in ("st_mtime_ns", "st_ctime_ns")),
              "compact_native_identity_changed")
        self._verify(handle, snapshot, len(receipt["raw"]), _digest(receipt["raw"]), MAX_RECEIPT_BYTES)
        receipt["snapshot"] = snapshot

    def _record_verified(self, entry, kind, value):
        receipt = self._write_receipt(entry, kind, value)
        handle = self.api.open(receipt["path"])
        primary = None
        try:
            self._handoff_receipt(handle, receipt)
        except BaseException as error:
            primary = error
            raise
        finally:
            try:
                self.api.close(handle)
            except BaseException:
                if primary is None:
                    raise CompactRefused("compact_record_close_failed") from None
        return _digest(receipt["raw"])

    def retire(self, ticket, final_consumer, evidence):
        """Dispose once, after the original final consumer explicitly validates.

        A terminal record reports the *earlier* authority close, not its own
        readback/close. The returned complete flag additionally requires that
        terminal file's flush, coherent readback and reader close. No record can
        prove its own final close. This is not a restart/resume interface: offline
        readers also need the containing invocation's final successful result;
        even a readable three-record chain alone does not certify completion.
        """
        _need(not self.blocked, "compact_store_blocked")
        entry, authority, receipt = None, None, None
        handles = [None, None]
        states = [{"stream": name, "mark": "not_requested", "close": "not_opened"}
                  for name in ("stdout", "stderr")]
        authority_state = {"recheck": "not_attempted", "close": "not_opened"}
        receipts = {"eligibility": None, "outcome": None, "terminal": None}
        stage = "compact_retirement_precondition_failed"
        try:
            self._ready()
            entry = self._ticket(ticket, "registered")
            entry["state"] = "retiring"  # No destructive retry, including after uncertainty.
            self._check_entry(entry)
            frozen_evidence = self._evidence(entry, final_consumer, evidence)
            stage = "compact_capture_acquisition_failed"
            for index, stream in enumerate(entry["streams"]):
                handles[index] = self.api.open_capture(entry["report"] / stream["name"])
                states[index]["close"] = "pending"
                self._verify(handles[index], stream["snapshot"], stream["bytes"],
                             stream["sha256"], contract.MAX_FILE_BYTES)
            stage = "compact_eligibility_receipt_failed"
            content = {"version": 1, "kind": "eligibility", "pair": entry["ordinal"],
                       "source_bindings": entry["source_bindings"],
                       "report_token": _digest(str(entry["report"]).encode("utf-8")),
                       "capture_root_identity_token": _digest(self._encode(self._roots[entry["capture_root"]])),
                       "report_identity_token": _digest(self._encode(entry["report_identity"])),
                       "owner": entry["owner_summary"], "final_consumer": final_consumer,
                       "evidence": frozen_evidence,
                       "streams": [{**s, "snapshot": asdict(s["snapshot"])} for s in entry["streams"]],
                       "retention": "intent_only_unknown_without_authenticated_terminal"}
            receipt = self._write_receipt(entry, "eligibility", content)
            authority = self.api.open(receipt["path"])
            authority_state["close"] = "pending"
            self._handoff_receipt(authority, receipt)
            receipts["eligibility"] = _digest(receipt["raw"])
            self._check_entry(entry)
            for handle, stream in zip(handles, entry["streams"]):
                self._verify(handle, stream["snapshot"], stream["bytes"],
                             stream["sha256"], contract.MAX_FILE_BYTES)
            stage = "compact_disposition_failed"
            for index in range(2):
                # Closing the prior stream can consume the remaining work
                # budget. Cleanup never authorizes starting another mark.
                _need(time.monotonic() < self.deadline, "compact_deadline_exhausted")
                states[index]["mark"] = "uncertain"
                self.api.mark_delete(handles[index])
                states[index]["mark"] = "verified"
                handle, handles[index] = handles[index], None
                states[index]["close"] = "uncertain"
                self.api.close(handle)
                states[index]["close"] = "verified"
        except BaseException as error:
            self._failed(error, stage)
        finally:
            for index, handle in enumerate(handles):
                if handle is not None:
                    handles[index] = None  # Close exactly once, even on a failed close.
                    states[index]["close"] = "uncertain"
                    try:
                        self.api.close(handle)
                        states[index]["close"] = "verified"
                    except BaseException as error:
                        self._failed(error, "compact_capture_close_failed")

        # These are bounded failure/evidence finalization steps, not new work.
        if entry is not None:
            try:
                receipts["outcome"] = self._record_verified(entry, "outcome", {
                    "version": 1, "kind": "outcome", "pair": entry["ordinal"],
                    "eligibility_sha256": receipts["eligibility"], "streams": states,
                    "first_failure": self.first_failure, "receipt_authority": "pending",
                    "retention": "unknown_without_authenticated_terminal"})
            except BaseException as error:
                self._failed(error, "compact_outcome_receipt_failed")
        if authority is not None:
            try:
                self._check_entry(entry)
                self._verify_receipt(authority, receipt)
                authority_state["recheck"] = "verified"
            except BaseException as error:
                authority_state["recheck"] = "uncertain"
                self._failed(error, "compact_authority_recheck_failed")
            authority_state["close"] = "uncertain"
            try:
                self.api.close(authority)
                authority_state["close"] = "verified"
            except BaseException as error:
                self._failed(error, "compact_authority_close_failed")
            authority = None
        if entry is not None:
            try:
                receipts["terminal"] = self._record_verified(entry, "terminal", {
                    "version": 1, "kind": "terminal", "pair": entry["ordinal"],
                    "eligibility_sha256": receipts["eligibility"], "outcome_sha256": receipts["outcome"],
                    "streams": states, "receipt_authority": authority_state,
                    "first_failure": self.first_failure,
                    "invocation_success": "requires_containing_invocation_result",
                    "terminal_readback": "not_asserted_by_this_record"})
            except BaseException as error:
                self._failed(error, "compact_terminal_receipt_failed")
            entry["state"] = "retired" if not self.blocked else "blocked"
        complete = not self.blocked and receipts["terminal"] is not None
        if entry is not None:
            entry["receipt_digests"] = tuple(receipts[k] for k in ("eligibility", "outcome", "terminal"))
            entry["retired_verified"] = complete
        return {"complete": complete, "reason": self.first_failure,
                "pair": entry["ordinal"] if entry is not None else None,
                "retention": "disposition_verified" if complete else "unknown",
                "streams": states, "receipt_authority": authority_state,
                "receipt_files": receipts}
