"""Finite synthetic Windows capability controls; not an application benchmark.

Native execution needs separate authorization. Portable injected APIs prove only
coordinator behavior. No ACL/share widening, DELETE_ON_CLOSE, path-unlink fallback,
historical cleanup, destructive retry, or power-loss/space-reclamation claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

import compact_capture_retention as retention
import compact_replacement_poststate as poststate
from compact_capture_native import WindowsCompactAPI
import generated_output_contract as contract
from windows_job_probe import WindowsJobProbe


CONTROL_IDS = (
    "snapshot_share_receipt_success", "replacement_identity_refusal",
    "hardlink_refusal", "reparse_refusal", "before_first_mark_refusal",
    "second_mark_partial", "deadline_after_first_close", "raw_close_partial",
    "outcome_readback_partial", "authority_recheck_partial", "authority_close_partial",
    "terminal_readback_unknown", "coordinator_death_unknown",
)
CONTROL_COMMAND_COUNTS = (1,) * 12 + (2,)
OWNED_COMMANDS = sum(CONTROL_COMMAND_COUNTS)
MAX_OWNED_COMMANDS = 35  # Core plus the separately declared direct-consumer population.
CAPTURE_SLOTS = OWNED_COMMANDS * 2
MAX_STREAM_BYTES = 16 * 1024 * 1024
MAX_RECEIPT_BYTES = 16 * 1024
MAX_COMPACT_RECEIPTS = len(CONTROL_IDS) * 3
MAX_PRIVATE_RECEIPTS = MAX_COMPACT_RECEIPTS + len(CONTROL_IDS) + 2
NATIVE_COVERAGE_LIMITS = (
    "Replacement preserves bytes and LastWriteTime, not CreationTime/ChangeTime; file-ID-only discrimination is unproved.",
    "Root/report-directory and byte-only mutants have portable coverage, not separate native controls in this population.",
    "Flush/close acknowledgments do not prove power-loss durability, pathname absence, secure erasure or reclaimed space.",
    "A passed finite control population does not authorize or qualify an application comparison.",
)
DIAGNOSTICS = frozenset({
    "control_platform_unsupported", "control_optimization_unsupported",
    "control_deadline", "control_deadline_invalid", "control_root_invalid",
    "control_proof_failed", "control_cleanup_unverified", "control_native_close_uncertain",
    "control_unavailable", "control_receipt_invalid", "control_stream_cap",
    "control_owner_incomplete", "control_reparse_prerequisite_unsupported",
    "control_hardlink_prerequisite_unsupported", "control_native_sharing_unexpected",
})


class ControlError(RuntimeError):
    def __init__(self, code):
        self.code = code if code in DIAGNOSTICS else "control_unavailable"
        super().__init__(self.code)


def require(value, code="control_proof_failed"):
    if not value:
        raise ControlError(code)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")




WITNESS_PHASES = frozenset({"prepare", "coordinator", "read_share", "capture_snapshot",
    "capture_bytes", "capture_share", "retirement", "retirement_proof",
    "receipt_reconstruction", "missing_invocation_proof"})
AUTHORITY_PHASES = frozenset({"not_attempted", "binding", "write", "delete_open",
                            "replace", "delete", "readback"})
REPLACEMENT_CALLS = frozenset({"not_returned", "entered", "returned_false",
                             "returned_true", "call_raised", "error_read_raised"})
REPLACEMENT_ERRORS = frozenset({"sharing_32", "access_5", "other"})
MAX_FAILURE_WITNESS_BYTES = 2048


def failure_witness(runtime):
    """Copy only finite control evidence before cleanup, never exception text.

    A returned store outcome is not the containing control's verdict. Missing or
    malformed evidence stays unknown; mark states never imply syscall counts.
    """
    source = getattr(runtime, "control_observation", None)
    if type(source) is not dict or type(source.get("control")) is not str or source.get("control") not in CONTROL_IDS:
        return None
    witness = {"version": 1, "control": source["control"],
        "phase": source.get("phase") if type(source.get("phase")) is str and source.get("phase") in WITNESS_PHASES else "unknown",
        "authority_phase": source.get("authority_phase")
            if type(source.get("authority_phase")) is str and source.get("authority_phase") in AUTHORITY_PHASES else "unknown",
        "replacement_call": None, "replacement_error": None,
        "replacement_poststate": source.get("replacement_poststate")
            if type(source.get("replacement_poststate")) is str and source["replacement_poststate"] in poststate.STATUSES else None,
        "outcome_state": "not_returned", "outcome": None,
        "reconstruction": source.get("reconstruction")
            if source.get("reconstruction") in ("not_attempted", "unknown", "disposition_verified") else "unknown",
        "overall_retention": "unknown",
        "authority_callbacks": source.get("authority_callbacks")
            if type(source.get("authority_callbacks")) is int and 0 <= source["authority_callbacks"] <= 2 else None,
        "same_authority": source.get("same_authority") if type(source.get("same_authority")) is bool else None,
        "receipt_observation": {"kind": None, "phase": "not_attempted", "reason": None, "close": "not_opened"}}
    call, error = source.get("replacement_call"), source.get("replacement_error")
    if (type(call) is str and call in REPLACEMENT_CALLS
            and "replacement_error" in source
            and ((call == "returned_false" and type(error) is str and error in REPLACEMENT_ERRORS)
                 or (call != "returned_false" and error is None))):
        witness.update(replacement_call=call, replacement_error=error)
    receipt = source.get("receipt_observation")
    if type(receipt) is dict:
        witness["receipt_observation"] = {
            "kind": receipt.get("kind") if receipt.get("kind") in ("eligibility", "outcome", "terminal") else None,
            "phase": receipt.get("phase") if receipt.get("phase") in ("open", "snapshot_before", "read",
                "snapshot_after", "bytes_proof", "decode", "close", "chain") else "unknown",
            "reason": receipt.get("reason") if receipt.get("reason") in
                (None, "control_proof_failed", "receipt_operation_unavailable", "receipt_chain_mismatch")
                else "receipt_operation_unavailable",
            "close": receipt.get("close") if receipt.get("close") in
                ("not_opened", "pending", "verified", "uncertain") else "uncertain"}
    if source.get("outcome_state") == "returned":
        witness["outcome_state"] = "invalid"
        try:
            row = source["outcome"]
            require(type(row) is dict and set(row) == {"complete", "reason", "pair", "retention",
                "streams", "receipt_authority", "receipt_files"})
            require(type(row["complete"]) is bool
                and (row["reason"] is None or type(row["reason"]) is str and row["reason"] in retention.REASONS)
                and (row["pair"] is None or type(row["pair"]) is int and 1 <= row["pair"] <= retention.MAX_PAIRS)
                and row["retention"] in ("unknown", "disposition_verified"))
            require(type(row["streams"]) is list and len(row["streams"]) == 2)
            for name, stream in zip(("stdout", "stderr"), row["streams"]):
                require(type(stream) is dict and set(stream) == {"stream", "mark", "close"}
                    and stream["stream"] == name
                    and stream["mark"] in ("not_requested", "uncertain", "verified")
                    and stream["close"] in ("not_opened", "pending", "uncertain", "verified"))
            authority = row["receipt_authority"]
            require(type(authority) is dict and set(authority) == {"recheck", "close"}
                and authority["recheck"] in ("not_attempted", "uncertain", "verified")
                and authority["close"] in ("not_opened", "pending", "uncertain", "verified"))
            receipts = row["receipt_files"]
            require(type(receipts) is dict and set(receipts) == {"eligibility", "outcome", "terminal"}
                and all(value is None or type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)
                        for value in receipts.values()))
            witness["outcome"] = json.loads(_canonical(row))
            witness["outcome_state"] = "returned"
            require(len(_canonical(witness)) <= MAX_FAILURE_WITNESS_BYTES)
        except BaseException:
            witness.update(outcome_state="invalid", outcome=None)
    return witness


def _phase(runtime, phase):
    observation = getattr(runtime, "control_observation", None)
    if observation is not None:
        observation["phase"] = phase


class ObservedAPI:
    """Delegate every successful native operation; faults may only raise.

    Close injection happens after the real close, and records that distinction.
    A real close failure is never retried. Writer descriptors remain writer-owned.
    """
    def __init__(self, native, check_work=lambda: None):
        self.native, self.handles, self.events = native, {}, []
        self.mode, self.mark_count, self.read_counts = None, 0, {}
        self.close_uncertain = False
        self.lifetimes, self.next_lifetime = {}, 0
        self.observe_authority_handoff, self.authority_handoff = False, None
        self.after_mark = self.after_close = self.before_mark = None
        self.check_work = check_work

    def from_fd(self, fd):
        return self.native.from_fd(fd)

    def record(self, handle):
        return self.native.record(handle)

    def _open(self, path, capture):
        handle = (self.native.open_capture if capture else self.native.open)(path)
        require(handle not in self.handles)
        self.handles[handle] = Path(path)
        self.next_lifetime += 1
        self.lifetimes[handle] = self.next_lifetime
        self.events.append(("capture_open" if capture else "read_open", Path(path).name))
        return handle

    def open(self, path):
        return self._open(path, False)

    def open_capture(self, path):
        return self._open(path, True)

    def read(self, handle, limit, deadline):
        name = self.handles[handle].name
        count = self.read_counts[name] = self.read_counts.get(name, 0) + 1
        if ((self.mode == "outcome_readback_partial" and name.endswith("-outcome.json"))
                or (self.mode == "authority_recheck_partial" and name.endswith("-eligibility.json") and count == 2)
                or (self.mode == "terminal_readback_unknown" and name.endswith("-terminal.json"))):
            raise OSError("injected exact read operation failure")
        if (self.observe_authority_handoff and self.authority_handoff is None
                and name.endswith("-eligibility.json")):
            # This read is the core store's original handoff read. The store
            # authenticates its returned bytes and records before entering the
            # first mark callback; the callback may then use this exact sample.
            before = contract.windows_snapshot(self, handle, limit, "replacement-handoff", deadline)
            raw = self.native.read(handle, limit, deadline)
            after = contract.windows_snapshot(self, handle, limit, "replacement-handoff", deadline)
            require(before == after and type(raw) is bytes and len(raw) == before.st_size)
            self.authority_handoff = (handle, self.lifetimes[handle], before, raw)
            return raw
        return self.native.read(handle, limit, deadline)

    def mark_delete(self, handle):
        self.mark_count += 1
        self.events.append(("mark_attempt", self.handles[handle].name))
        if self.before_mark is not None:
            self.before_mark(handle)
        self.check_work()
        if (self.mode == "before_first_mark_refusal" and self.mark_count == 1
                or self.mode == "second_mark_partial" and self.mark_count == 2):
            raise OSError("injected exact disposition operation failure")
        self.native.mark_delete(handle)
        self.events.append(("mark_verified", self.handles[handle].name))
        if self.after_mark is not None:
            self.after_mark(handle)

    def close(self, handle):
        path = self.handles.pop(handle)
        self.lifetimes.pop(handle, None)
        try:
            self.native.close(handle)
        except BaseException:
            self.close_uncertain = True
            raise
        self.events.append(("close_verified", path.name))
        if self.after_close is not None:
            self.after_close(path)
        if (self.mode == "raw_close_partial" and path.name == "stdout.bin"
                or self.mode == "authority_close_partial" and path.name.endswith("-eligibility.json")):
            raise OSError("injected result uncertainty after native close")


def _native_api():
    api = WindowsCompactAPI()
    kernel = api.kernel
    api.opens = []
    class Kernel:
        def __getattr__(self, name):
            return getattr(kernel, name)
        def CreateFileW(self, path, access, share, security, creation, flags, template):
            api.opens.append((access, share, creation, flags))
            return kernel.CreateFileW(path, access, share, security, creation, flags, template)
    api.kernel = Kernel()
    return api


SYNTHETIC_CHILD = ("import sys;sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]));"
                   "sys.stdout.buffer.flush();sys.stderr.buffer.write(bytes.fromhex(sys.argv[2]));"
                   "sys.stderr.buffer.flush();raise SystemExit(int(sys.argv[3]))")


class ControlRuntime:
    """Shared process ownership and exact native-boundary injection seam."""
    def __init__(self, *, owner_factory=WindowsJobProbe, api_factory=_native_api,
                 snapshot_reader=contract.read_owned_capture_snapshot, clock=time.monotonic,
                 sleep=time.sleep, environment=None, resource_check=lambda: None,
                 terminate_coordinator=None):
        self.owner_factory, self.api_factory = owner_factory, api_factory
        self.snapshot_reader, self.clock, self.sleep = snapshot_reader, clock, sleep
        self.environment = dict(os.environ if environment is None else environment)
        self.owners, self.apis = [], []
        self.resource_check = resource_check
        self.nested_command_slots = 0
        self.terminate_coordinator = terminate_coordinator or (
            lambda owner: owner._api.terminate_process(owner._info.hProcess))
        self.work_deadline = self.hard_deadline = None

    def api(self):
        api = ObservedAPI(self.api_factory(), self.check_time)
        self.apis.append(api)
        return api

    def check_time(self):
        require(self.clock() < self.work_deadline, "control_deadline")

    def start_owned(self, argv, report_dir):
        self.check_time()
        require(len(self.owners) + self.nested_command_slots < MAX_OWNED_COMMANDS,
                "control_stream_cap")
        self.resource_check()
        try:
            owner = self.owner_factory.start(argv, cwd=report_dir.parent,
                env=self.environment, report_dir=report_dir)
        except BaseException as error:
            owner = getattr(error, "owner", None)
            if owner is not None and all(owner is not item for item in self.owners):
                self.owners.append(owner)
            raise
        self.owners.append(owner)
        return owner

    def stream_cap(self, owner):
        for path in (owner.stdout_path, owner.stderr_path):
            require(Path(path).lstat().st_size <= MAX_STREAM_BYTES, "control_stream_cap")

    def complete(self, owner):
        while True:
            self.check_time()
            self.resource_check()
            self.stream_cap(owner)
            snapshot = owner.poll()
            if snapshot.root_reaped and snapshot.active_processes == 0:
                break
            self.sleep(min(.02, max(0, self.work_deadline - self.clock())))
        result = owner.finish(timeout=max(0, self.work_deadline - self.clock()))
        snapshot = result.snapshot
        require(result is owner.result and result.reason == "completed"
                and snapshot.cleanup_verified is True and snapshot.root_reaped is True
                and snapshot.active_processes == 0 and snapshot.state == "closed",
                "control_owner_incomplete")
        self.stream_cap(owner)
        return result

    def launch(self, report_dir, stdout, stderr, exit_code=0):
        require(isinstance(report_dir, Path) and report_dir.is_absolute()
                and type(stdout) is bytes and type(stderr) is bytes
                and max(len(stdout), len(stderr)) <= MAX_STREAM_BYTES
                and type(exit_code) is int and 0 <= exit_code <= 255)
        owner = self.start_owned([sys.executable, "-I", "-S", "-B", "-c", SYNTHETIC_CHILD,
                                  stdout.hex(), stderr.hex(), str(exit_code)], report_dir)
        result = self.complete(owner)
        reads = tuple(self.snapshot_reader(report_dir.parent,
            report_dir.name + "/" + name + ".bin", MAX_STREAM_BYTES, self.work_deadline)
            for name in ("stdout", "stderr"))
        require(reads[0][0] == stdout and reads[1][0] == stderr
                and result.snapshot.root_exit_code == exit_code)
        return owner, result, reads

    def cleanup(self):
        okay = True
        for owner in reversed(self.owners):
            try:
                result = owner.result
                if result is None or result.snapshot.cleanup_verified is not True:
                    require(self.clock() < self.hard_deadline, "control_cleanup_unverified")
                    result = owner.cancel("compact-control-finally", timeout=self.hard_deadline - self.clock())
                snapshot = result.snapshot
                require(snapshot.cleanup_verified is True and snapshot.root_reaped is True
                        and snapshot.active_processes == 0 and snapshot.state == "closed",
                        "control_cleanup_unverified")
            except BaseException:
                okay = False
        return okay and not any(api.handles or api.close_uncertain for api in self.apis)


@dataclass
class PreparedPair:
    root: Path
    store: retention.CompactStore
    ticket: object
    api: ObservedAPI
    owner: object
    result: object
    reads: tuple
    runtime: object

    def retire(self):
        from compact_parallel_consumers import helper_evidence
        record = {"reads": self.reads, "result": {"returncode": self.result.snapshot.root_exit_code}}
        _phase(self.runtime, "retirement")
        result = self.store.retire(self.ticket, "helper_result", helper_evidence(record))
        observation = getattr(self.runtime, "control_observation", None)
        if observation is not None:
            observation.update(outcome_state="returned", outcome=result)
        _phase(self.runtime, "retirement_proof")
        return result


def prepare_pair(root, runtime, stdout=b"synthetic output\n", stderr=b"", exit_code=0):
    """Create only one fresh registered synthetic owner pair; never reuse roots."""
    require(isinstance(root, Path) and root.is_absolute() and ".." not in root.parts
            and root.resolve() == root and not os.path.lexists(root), "control_root_invalid")
    api = runtime.api()
    root.mkdir(parents=False, exist_ok=False)
    store = retention.CompactStore(root, runtime.work_deadline, api=api)
    report = root / "command-0001"
    ticket = store.reserve(root, report, {"payload_sha256": _digest(SYNTHETIC_CHILD.encode("ascii"))})
    owner, result, reads = runtime.launch(report, stdout, stderr, exit_code)
    store.register(ticket, owner, result, reads)
    return PreparedPair(root, store, ticket, api, owner, result, reads, runtime)


FAULT_EXPECTATIONS = {
    "before_first_mark_refusal": (("uncertain", "not_requested"), "compact_disposition_failed"),
    "second_mark_partial": (("verified", "uncertain"), "compact_disposition_failed"),
    "deadline_after_first_close": (("verified", "not_requested"), "compact_deadline_exhausted"),
    "raw_close_partial": (("verified", "not_requested"), "compact_disposition_failed"),
    "outcome_readback_partial": (("verified", "verified"), "compact_outcome_receipt_failed"),
    "authority_recheck_partial": (("verified", "verified"), "compact_authority_recheck_failed"),
    "authority_close_partial": (("verified", "verified"), "compact_authority_close_failed"),
    "terminal_readback_unknown": (("verified", "verified"), "compact_terminal_receipt_failed"),
}


def reconstruct_retention(root, api, deadline, *, outcome=None, invocation_complete=False, observation=None):
    """Read-only chain check. Receipts alone NEVER certify an invocation's exit.

    A missing containing successful result, missing/corrupt record, read/close
    uncertainty or partial disposal returns unknown, not a claim originals remain.
    """
    if invocation_complete is not True or type(outcome) is not dict or outcome.get("complete") is not True:
        return "unknown"
    expected = outcome.get("receipt_files")
    if (type(expected) is not dict or set(expected) != {"eligibility", "outcome", "terminal"}
            or outcome.get("reason") is not None or outcome.get("retention") != "disposition_verified"):
        return "unknown"
    records = {}
    receipt_observation = {"kind": None, "phase": "not_attempted", "reason": None, "close": "not_opened"}
    if observation is not None:
        observation["receipt_observation"] = receipt_observation
    for kind in ("eligibility", "outcome", "terminal"):
        handle = None
        try:
            digest = expected[kind]
            require(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest))
            path = root / ("compact-%06d-%s.json" % (outcome["pair"], kind))
            receipt_observation.update(kind=kind, phase="open", close="not_opened")
            handle = api.open(path)
            receipt_observation.update(phase="snapshot_before", close="pending")
            before = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES, "compact-control", deadline)
            receipt_observation["phase"] = "read"
            raw = api.read(handle, MAX_RECEIPT_BYTES, deadline)
            receipt_observation["phase"] = "snapshot_after"
            after = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES, "compact-control", deadline)
            receipt_observation["phase"] = "bytes_proof"
            require(before == after and len(raw) == before.st_size and _digest(raw) == digest)
            receipt_observation["phase"] = "decode"
            records[kind] = json.loads(raw)
            closing, handle = handle, None
            receipt_observation.update(phase="close", close="uncertain")
            api.close(closing)
            receipt_observation["close"] = "verified"
        except BaseException as error:
            receipt_observation["reason"] = ("control_proof_failed" if type(error) is ControlError
                and error.code == "control_proof_failed" else "receipt_operation_unavailable")
            if handle is not None:
                receipt_observation["close"] = "uncertain"
                try:
                    api.close(handle)
                    receipt_observation["close"] = "verified"
                except BaseException:
                    pass
            return "unknown"
    receipt_observation.update(kind=None, phase="chain")
    terminal, recorded = records["terminal"], records["outcome"]
    if (terminal.get("eligibility_sha256") != expected["eligibility"]
            or terminal.get("outcome_sha256") != expected["outcome"]
            or recorded.get("eligibility_sha256") != expected["eligibility"]
            or terminal.get("first_failure") is not None or recorded.get("first_failure") is not None
            or terminal.get("streams") != outcome.get("streams")
            or recorded.get("streams") != outcome.get("streams")
            or terminal.get("receipt_authority") != {"recheck": "verified", "close": "verified"}
            or any(row != {"stream": name, "mark": "verified", "close": "verified"}
                   for name, row in zip(("stdout", "stderr"), outcome.get("streams", ())))):
        receipt_observation["reason"] = "receipt_chain_mismatch"
        return "unknown"
    return "disposition_verified"


def _blocked_next_pair(pair):
    try:
        pair.store.reserve(pair.root, pair.root / "command-0002", {"source_sha": "a" * 40})
    except retention.CompactRefused as error:
        require(str(error) == "compact_store_blocked")
        return True
    raise ControlError("control_proof_failed")


def _denied_by_sharing(operation, api):
    handle = None
    try:
        handle = operation()
    except contract.q.Refused:
        require(api.native.c.get_last_error() == 32, "control_native_sharing_unexpected")
        return
    finally:
        if handle is not None:
            try:
                api.close(handle)
            except BaseException:
                pass  # The known sharing failure is primary; close uncertainty is retained.
    raise ControlError("control_native_sharing_unexpected")


@contextmanager
def _owned_handle(api, path, *, capture=False):
    handle = api.open_capture(path) if capture else api.open(path)
    primary = None
    try:
        yield handle
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            api.close(handle)
        except BaseException:
            if primary is None:
                raise


def _replacement_observation(runtime, call, error=None):
    """Best-effort finite evidence must not replace a native/control exception."""
    try:
        runtime.control_observation.update(replacement_call=call, replacement_error=error)
    except BaseException:
        pass


def _authority_denials(pair):
    """Attack only the fresh eligibility name while its read authority is held.

    The two path API calls are denied controls, never deletion/replacement cleanup
    fallbacks. Any unexpected success immediately stops before a capture mark.
    """
    handles = [(h, p) for h, p in pair.api.handles.items() if p.name.endswith("-eligibility.json")]
    require(len(handles) == 1)
    handle, path = handles[0]
    api = pair.api.native
    denials = []
    for label, access in (("write", 0x40000000), ("delete_open", 0x00010000)):
        pair.runtime.control_observation["authority_phase"] = label
        opened = api.kernel.CreateFileW(str(path), access, 1, None, 3, 0x08200000, None)
        if opened not in (None, api.c.c_void_p(-1).value):
            pair.api.handles[opened] = path
            try:
                pair.api.close(opened)
            finally:
                raise ControlError("control_native_sharing_unexpected")
        require(api.c.get_last_error() == 32, "control_native_sharing_unexpected")
        denials.append(label)
    replacement = pair.root / "receipt-replacement.bin"
    with replacement.open("xb") as stream:
        stream.write(b"synthetic replacement must be denied\n")
    supplemental = None
    if getattr(pair.runtime, "replacement_poststate", False):
        bound = pair.api.authority_handoff
        require(bound is not None and bound[0] == handle
                and pair.api.lifetimes.get(handle) == bound[1])
        supplemental = poststate.ReplacementPoststate(pair.api, handle, path, replacement,
            baseline=bound[2:], deadline=pair.store.deadline,
            observation=pair.runtime.control_observation)
        supplemental.prepare()
    import ctypes as c
    move = api.kernel.MoveFileExW
    move.argtypes, move.restype = (c.c_wchar_p, c.c_wchar_p, c.c_uint32), c.c_int
    pair.runtime.control_observation["authority_phase"] = "replace"
    # This is the Python invocation boundary, not evidence of Windows entry.
    _replacement_observation(pair.runtime, "entered")
    try:
        returned_false = not move(str(replacement), str(path), 1)
    except BaseException:
        _replacement_observation(pair.runtime, "call_raised")
        raise
    error = None
    if returned_false:
        try:
            error = api.c.get_last_error()
        except BaseException:
            _replacement_observation(pair.runtime, "error_read_raised")
            raise
    _replacement_observation(pair.runtime,
        "returned_false" if returned_false else "returned_true",
        ("sharing_32" if error == 32 else "access_5" if error == 5 else "other")
            if returned_false else None)
    primary = None
    try:
        require(returned_false and error == 32, "control_native_sharing_unexpected")
    except ControlError as refused:
        primary = refused
    # Sample after a failed call, even error5, but never adopt that sample as
    # acceptance. The known original refusal remains primary if proof also fails.
    if supplemental is not None and returned_false:
        try:
            supplemental.verify()
        except BaseException:
            if primary is None:
                raise
    if primary is not None:
        raise primary
    denials.append("replace")
    delete = api.kernel.DeleteFileW
    delete.argtypes, delete.restype = (c.c_wchar_p,), c.c_int
    pair.runtime.control_observation["authority_phase"] = "delete"
    require(not delete(str(path)) and api.c.get_last_error() == 32,
            "control_native_sharing_unexpected")
    denials.append("delete")
    # The same acquired handle must still identify and read the original receipt.
    pair.runtime.control_observation["authority_phase"] = "readback"
    require(pair.api.read(handle, MAX_RECEIPT_BYTES, pair.store.deadline))
    return denials


def _snapshot_share_success(pair, runtime):
    path = Path(pair.owner.stdout_path)
    _phase(runtime, "read_share")
    with _owned_handle(pair.api, path):
        require(pair.api.native.opens[-1] == (0x80000000, 1, 3, 0x08200000))
        _denied_by_sharing(lambda: pair.api.open_capture(path), pair.api)
    _phase(runtime, "capture_snapshot")
    with _owned_handle(pair.api, path, capture=True) as capture:
        require(pair.api.native.opens[-1] == (0x80010000, 1, 3, 0x08200000))
        observed = contract.windows_snapshot(pair.api, capture, MAX_STREAM_BYTES,
                                             "compact-control", runtime.work_deadline)
        require(observed == pair.reads[0][1])
        _phase(runtime, "capture_bytes")
        require(pair.api.read(capture, MAX_STREAM_BYTES, runtime.work_deadline) == pair.reads[0][0])
        _phase(runtime, "capture_share")
        _denied_by_sharing(lambda: pair.api.open(path), pair.api)
    denials = []
    authority_handles = []
    def before_mark(handle):
        runtime.control_observation["authority_phase"] = "binding"
        authorities = [h for h, p in pair.api.handles.items() if p.name.endswith("-eligibility.json")]
        require(len(authorities) == 1)
        authority_handles.append(authorities[0])
        if not denials:
            denials.extend(_authority_denials(pair))
    pair.api.before_mark = before_mark
    pair.api.observe_authority_handoff = getattr(runtime, "replacement_poststate", False)
    result = pair.retire()
    runtime.control_observation.update(authority_callbacks=len(authority_handles),
        same_authority=(authority_handles[0] == authority_handles[1]) if len(authority_handles) == 2 else None)
    require(result["complete"] is True and len(authority_handles) == 2
            and authority_handles[0] == authority_handles[1])
    _phase(runtime, "receipt_reconstruction")
    runtime.control_observation["reconstruction"] = "unknown"
    retained = reconstruct_retention(pair.root, pair.api, runtime.work_deadline,
                                      outcome=result, invocation_complete=True,
                                      observation=runtime.control_observation)
    runtime.control_observation["reconstruction"] = retained
    require(retained == "disposition_verified")
    _phase(runtime, "missing_invocation_proof")
    require(reconstruct_retention(pair.root, pair.api, runtime.work_deadline, outcome=result) == "unknown")
    return {"outcome": result, "retention": retained, "authority_denials": denials,
            "replacement_poststate": runtime.control_observation.get("replacement_poststate"),
            "snapshot_fields": list(contract.METADATA_FIELDS), "events": pair.api.events}


def read_coordinator_ready(raw):
    require(type(raw) is bytes and len(raw) <= MAX_RECEIPT_BYTES, "control_receipt_invalid")
    try:
        row = json.loads(raw)
        require(type(row) is dict and set(row) == {"version", "inner_commands", "inner_cleanup_verified",
            "inner_active_processes", "mark", "stream", "eligibility_sha256", "terminal_written"}
            and type(row["version"]) is int and row["version"] == 1
            and type(row["inner_commands"]) is int and row["inner_commands"] == 1
            and row["inner_cleanup_verified"] is True
            and type(row["inner_active_processes"]) is int and row["inner_active_processes"] == 0
            and row["mark"] == "verified" and row["stream"] == "stdout"
            and row["terminal_written"] is False and type(row["eligibility_sha256"]) is str
            and re.fullmatch(r"[0-9a-f]{64}", row["eligibility_sha256"])
            and _canonical(row) == raw, "control_receipt_invalid")
        return row
    except (ValueError, TypeError, KeyError, RecursionError):
        raise ControlError("control_receipt_invalid") from None


def _write_private(path, evidence):
    raw = _canonical(evidence)
    require(len(raw) <= MAX_RECEIPT_BYTES, "control_receipt_invalid")
    with path.open("x+b") as stream:
        require(stream.write(raw) == len(raw), "control_receipt_invalid")
        stream.flush()
        os.fsync(stream.fileno())
    with path.open("rb") as stream:
        require(stream.read(MAX_RECEIPT_BYTES + 1) == raw, "control_receipt_invalid")
    return _digest(raw)


def _read_native_record(path, api, deadline):
    with _owned_handle(api, path) as handle:
        before = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES, "compact-control", deadline)
        raw = api.read(handle, MAX_RECEIPT_BYTES, deadline)
        after = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES, "compact-control", deadline)
        require(before == after and len(raw) == before.st_size)
        return raw


def coordinator(root, work_deadline, hard_deadline):
    """Owned child: pause after one real mark, retaining its authority handle.

    The parent kills this exact coordinator through its original process handle.
    No unowned subprocess, PID-opened termination, or path cleanup occurs.
    """
    runtime = ControlRuntime()
    runtime.work_deadline, runtime.hard_deadline = work_deadline, hard_deadline
    pair = prepare_pair(root / "inner", runtime)
    def pause_after_mark(handle):
        require(pair.api.mark_count == 1)
        authority = [(h, p) for h, p in pair.api.handles.items() if p.name.endswith("-eligibility.json")]
        require(len(authority) == 1)
        raw = pair.api.read(authority[0][0], MAX_RECEIPT_BYTES, work_deadline)
        ready = {"version": 1, "inner_commands": 1, "inner_cleanup_verified": pair.result.snapshot.cleanup_verified,
            "inner_active_processes": pair.result.snapshot.active_processes,
            "mark": "verified", "stream": "stdout", "eligibility_sha256": _digest(raw),
            "terminal_written": False}
        pending = root / "coordinator-ready.pending"
        _write_private(pending, ready)
        pending.rename(root / "coordinator-ready.json")
        while runtime.clock() < work_deadline:
            runtime.sleep(min(.02, work_deadline - runtime.clock()))
        # If the parent did not kill us, this becomes an ordinary failed fixture,
        # never synthetic evidence of a coordinator death.
        raise ControlError("control_deadline")
    pair.api.after_mark = pause_after_mark
    try:
        pair.retire()
        return 2
    finally:
        runtime.cleanup()


def _coordinator_death(root, runtime):
    require(isinstance(root, Path) and root.is_absolute() and root.resolve() == root
            and not os.path.lexists(root), "control_root_invalid")
    root.mkdir()
    runtime.nested_command_slots += 1  # Conservatively admit the inner owner before dispatch.
    script = Path(__file__).resolve()
    payload = ("import runpy,sys;from pathlib import Path;sys.path.insert(0,%r);"
               "raise SystemExit(runpy.run_path(%r)['coordinator'](Path(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])))"
               % (str(script.parent), str(script)))
    owner = runtime.start_owned([sys.executable, "-I", "-S", "-B", "-c", payload,
        str(root), str(runtime.work_deadline), str(runtime.hard_deadline)], root / "command-0001")
    ready_path = root / "coordinator-ready.json"
    while not ready_path.exists():
        runtime.check_time()
        runtime.resource_check()
        runtime.stream_cap(owner)
        snapshot = owner.poll()
        require(not snapshot.root_reaped, "control_owner_incomplete")
        runtime.sleep(min(.02, max(0, runtime.work_deadline - runtime.clock())))
    api = runtime.api()
    ready = read_coordinator_ready(_read_native_record(ready_path, api, runtime.work_deadline))
    snapshot = owner.poll()
    require(not snapshot.root_reaped and snapshot.active_processes == 1 and snapshot.total_processes == 2)
    runtime.terminate_coordinator(owner)
    result = runtime.complete(owner)
    require(result.snapshot.total_processes == 2)
    inner = root / "inner"
    eligibility = _read_native_record(inner / "compact-000001-eligibility.json", api, runtime.work_deadline)
    require(_digest(eligibility) == ready["eligibility_sha256"]
            and not os.path.lexists(inner / "compact-000001-outcome.json")
            and not os.path.lexists(inner / "compact-000001-terminal.json"))
    require(reconstruct_retention(inner, api, runtime.work_deadline) == "unknown")
    return {"ready": ready, "retention": "unknown", "terminal_present": False,
        "coordinator_cleanup_verified": result.snapshot.cleanup_verified,
        "coordinator_total_processes": result.snapshot.total_processes,
        "inner_cleanup_verified": True}


def run_control(control_id, root, runtime):
    """One fixed control, used by the complete packet and portable seam tests."""
    require(control_id in CONTROL_IDS)
    runtime.control_observation = {"control": control_id, "phase": "prepare",
        "authority_phase": "not_attempted", "outcome_state": "not_returned",
        "replacement_call": "not_returned", "replacement_error": None,
        "outcome": None, "reconstruction": "not_attempted"}
    runtime.check_time()
    if control_id == "coordinator_death_unknown":
        _phase(runtime, "coordinator")
        return _coordinator_death(root, runtime)
    pair = prepare_pair(root, runtime)
    if control_id == "snapshot_share_receipt_success":
        return _snapshot_share_success(pair, runtime)
    if control_id in ("replacement_identity_refusal", "hardlink_refusal", "reparse_refusal"):
        path = Path(pair.owner.stdout_path)
        if control_id == "hardlink_refusal":
            try:
                os.link(path, pair.root / "synthetic-hardlink.bin")
            except OSError:
                raise ControlError("control_hardlink_prerequisite_unsupported") from None
        else:
            # Preserve the old bytes under a new fresh-fixture name; never unlink.
            moved = pair.root / "retained-original.bin"
            path.rename(moved)
            if control_id == "reparse_refusal":
                try:
                    path.symlink_to(moved)
                except OSError:
                    raise ControlError("control_reparse_prerequisite_unsupported") from None
            else:
                with path.open("xb") as stream:
                    stream.write(pair.reads[0][0])
                initial = pair.reads[0][1]
                os.utime(path, ns=(initial.st_mtime_ns, initial.st_mtime_ns))
        result = pair.retire()
        require(result["complete"] is False and result["retention"] == "unknown"
                and [row["mark"] for row in result["streams"]] == ["not_requested", "not_requested"])
        require(result["reason"] == ("compact_native_identity_changed"
                if control_id == "replacement_identity_refusal" else "compact_capture_acquisition_failed"))
        return {"outcome": result, "retention": "unknown",
                "next_pair_refused": _blocked_next_pair(pair), "events": pair.api.events}
    if control_id in FAULT_EXPECTATIONS:
        pair.api.mode = control_id
        if control_id == "deadline_after_first_close":
            def exhaust_after_close(path):
                if path.name == "stdout.bin":
                    pair.store.deadline = runtime.clock() - 1
            pair.api.after_close = exhaust_after_close
        result = pair.retire()
        marks, reason = FAULT_EXPECTATIONS[control_id]
        require(result["complete"] is False and result["reason"] == reason
                and tuple(row["mark"] for row in result["streams"]) == marks
                and result["retention"] == "unknown")
        return {"outcome": result, "retention": reconstruct_retention(root, pair.api,
            runtime.work_deadline, outcome=result, invocation_complete=True),
            "next_pair_refused": _blocked_next_pair(pair), "events": pair.api.events}
    raise ControlError("control_unavailable")


