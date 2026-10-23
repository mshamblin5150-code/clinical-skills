"""Supplemental sampled namespace/object/content survival, not causal proof.

The caller must supply the original handoff sample only after its store has
successfully authenticated that same continuously held authority. Observations
are bounded and non-atomic: no continuous-presence or transient-absence claim.
Nothing in this module accepts a replacement return/error or changes a verdict.
"""
import time

import compact_capture_retention as retention
import generated_output_contract as contract

REPLACEMENT_BYTES = b"synthetic replacement must be denied\n"
MAX_RECEIPT_BYTES = 16 * 1024
STATUSES = frozenset({'not_checked', 'prepared', 'verified', 'failed'})


class PoststateRefused(RuntimeError):
    def __init__(self):
        super().__init__('replacement_poststate_unverified')


def need(value):
    if not value:
        raise PoststateRefused()


class ReplacementPoststate:
    """Public portable proof seam, with real handle and namespace separation.

    api.open/read/record/close are the existing READ/shareREAD operations; handles
    is the observer's live ledger and close_uncertain is monotone. Baseline must
    be (full snapshot, exact bytes) from the original authenticated handoff read.
    Extra handles are never retained across prepare/verify returns, including
    failure. A failed close is never retried and prevents further challenges.
    """
    def __init__(self, api, authority, destination, source, *, baseline, deadline,
                 observation, directory=retention._directory):
        self.api, self.authority = api, authority
        self.destination, self.source = destination, source
        self.baseline, self.deadline = baseline, deadline
        self.observation, self.directory = observation, directory
        self.held = dict(api.handles)
        self.lifetimes = dict(api.lifetimes)
        self.prepared = False
        self.chain = self.source_baseline = None
        self._status('not_checked')

    def _status(self, value):
        # Observation is not proof authority. Remove any old success before a
        # fallible write, bypassing dict-subclass hooks only for invalidation.
        # Missing evidence projects to unknown, never a negative execution claim.
        try:
            if isinstance(self.observation, dict):
                dict.pop(self.observation, 'replacement_poststate', None)
                self.observation['replacement_poststate'] = value
        except BaseException:
            # Preserve the exact proof/call exception, including during unwind.
            # A setter could write and then raise; invalidate that too.
            if isinstance(self.observation, dict):
                dict.pop(self.observation, 'replacement_poststate', None)

    def _time(self):
        need(time.monotonic() < self.deadline)

    def _ledger(self):
        need(self.api.handles == self.held and self.api.lifetimes == self.lifetimes
             and not self.api.close_uncertain
             and self.authority in self.api.handles
             and self.api.handles[self.authority] == self.destination)
        self._time()

    def _sample(self, handle, limit):
        self._time()
        before = contract.windows_snapshot(self.api, handle, limit, 'replacement-poststate', self.deadline)
        raw = self.api.read(handle, limit, self.deadline)
        after = contract.windows_snapshot(self.api, handle, limit, 'replacement-poststate', self.deadline)
        need(before == after and type(raw) is bytes and len(raw) == before.st_size
             and len(raw) <= limit)
        retention._native_snapshot(before, len(raw))
        # Unsupported fixture attributes are refused, never changed. Ordinary
        # attributes still say nothing about ACLs, filters, or denial causation.
        need(not before.st_file_attributes & (0x1 | 0x2 | 0x4 | 0x100))
        self._time()
        return before, raw

    def _path_sample(self, path, limit):
        self._time()
        handle = self.api.open(path)
        primary = None
        try:
            need(handle not in self.held)
            return self._sample(handle, limit)
        except BaseException as error:
            primary = error
            raise
        finally:
            try:
                self.api.close(handle)
            except BaseException:
                if primary is None:
                    raise PoststateRefused() from None

    def _parent(self):
        self._time()
        need(self.source.parent == self.destination.parent)
        chain = self.directory(self.destination.parent)
        self._time()
        return chain

    def prepare(self):
        try:
            need(not self.prepared)
            self._ledger()
            self.chain = self._parent()
            need(self._sample(self.authority, MAX_RECEIPT_BYTES) == self.baseline)
            need(self._path_sample(self.destination, MAX_RECEIPT_BYTES) == self.baseline)
            self.source_baseline = self._path_sample(self.source, len(REPLACEMENT_BYTES))
            original, raw = self.baseline
            replacement, replacement_raw = self.source_baseline
            need(type(raw) is bytes and replacement_raw == REPLACEMENT_BYTES
                 and original.st_dev == replacement.st_dev
                 and original.st_ino != replacement.st_ino)
            need(self._parent() == self.chain)
            self._ledger()
            self.prepared = True
            self._status('prepared')
        except BaseException:
            self._status('failed')
            raise

    def verify(self):
        try:
            need(self.prepared)
            self._ledger()
            need(self._parent() == self.chain)
            need(self._sample(self.authority, MAX_RECEIPT_BYTES) == self.baseline)
            need(self._path_sample(self.destination, MAX_RECEIPT_BYTES) == self.baseline)
            need(self._path_sample(self.source, len(REPLACEMENT_BYTES)) == self.source_baseline)
            need(self._sample(self.authority, MAX_RECEIPT_BYTES) == self.baseline)
            need(self._parent() == self.chain)
            self._ledger()
            self._status('verified')
        except BaseException:
            self._status('failed')
            raise
