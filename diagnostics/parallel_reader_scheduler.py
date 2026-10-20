"""Proof-only, deterministic two-checkout reader scheduling; not production code.

No process implementation lives here. The injected runner owns each complete tree.
The window bounds *unretired modules*, not just active processes, so one slow early
module cannot permit an unbounded queue of later completions. Inputs stay sorted.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from parallel_reader_diagnostics import safe_exception


LOOKUPS = ("icd10_lookup", "procedure_codes_lookup")
MARKER = "CODE_SET_DATABASE_OPEN_REFUSED"


@dataclass(frozen=True)
class Observation:
    module: str
    lookup: str
    classification: str
    unexpected: bool = False
    cleanup_verified: bool = True
    test_count: int | None = None
    failures: int = 0
    errors: int = 0
    wall_seconds: float = 0.0
    tree_cpu_seconds: float | None = 0.0
    reason: str = "completed"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScheduleResult:
    complete: bool
    observations: tuple[Observation, ...]
    unread_pairs: tuple[tuple[str, str], ...]
    first_error: tuple[str, str] | None
    first_error_resolved: bool
    stop_reason: str | None
    events: tuple[dict[str, Any], ...]
    diagnostics: tuple[dict[str, Any], ...] = ()


def account_pairs(modules, observations):
    """Equality, not totals: a duplicate cannot cancel a missing pair."""
    expected = {(module, lookup) for module in modules for lookup in LOOKUPS}
    counts = Counter((row.module, row.lookup) for row in observations)
    return {
        "missing": sorted(expected - counts.keys()),
        "duplicate": sorted(pair for pair, count in counts.items() if count != 1),
        "unexpected": sorted(counts.keys() - expected),
    }


def audit_sets(modules, pinned, observations):
    accounting = account_pairs(modules, observations)
    if any(accounting.values()):
        raise ValueError("pair_accounting_incomplete")
    if any(row.unexpected or not row.cleanup_verified for row in observations):
        raise ValueError("screen_not_clean")
    readers = frozenset((row.module, row.lookup) for row in observations
                        if row.classification == "reader")
    pinned = frozenset(pinned)
    return {
        "reaching": sorted(modules),
        "readers": sorted(readers),
        "pinned": sorted(pinned),
        "unpinned_readers": sorted(readers - pinned),
        "stale_pins": sorted(pinned - readers),
    }


def run_schedule(modules, cap, runner, *, deadline, clock, sleep):
    """runner.start(index, lane, module, lookup), poll(handle), cancel(handle, reason).

poll returns None until the complete tree is retired, then an Observation. cancel
must return an Observation describing verified cleanup, including failed cleanup.
The serial-first-error is unresolved if an earlier module cannot finish. The only
time limit is the caller's whole-experiment deadline, never a per-test timeout.
"""
    modules = tuple(modules)
    if not modules or modules != tuple(sorted(set(modules))) or cap not in (1, 2):
        raise ValueError("invalid_schedule_population_or_cap")
    states = {}
    head = 0
    next_index = 0
    cutoff = None
    first_error = None
    first_error_resolved = False
    stop_reason = None
    observations = []
    events = []
    diagnostics = []

    def diagnose(error):
        sink = getattr(runner, "diagnose_exception", None)
        try:
            diagnostics.append(sink(error) if sink is not None else safe_exception(error))
        except Exception:
            diagnostics.append(safe_exception(error))

    def record(row):
        observations.append(row)
        events.append({"event": "result", "module": row.module,
                       "lookup": row.lookup, "unexpected": row.unexpected})

    def cancel_later(index, reason):
        nonlocal stop_reason
        for later, state in sorted(states.items()):
            if later > index and state["handle"] is not None:
                row = runner.cancel(state["handle"], reason)
                record(row)
                state["handle"] = None
                state["canceled"] = True
                if not row.cleanup_verified:
                    stop_reason = "cleanup_unverified"

    try:
        while head < len(modules):
            if clock() >= deadline:
                stop_reason = "whole_job_measurement_budget_exhausted"
                break

            # Read every already-running result before launching any new work.
            for index, state in sorted(states.items()):
                if state["handle"] is None:
                    continue
                row = runner.poll(state["handle"])
                if row is None:
                    continue
                state["handle"] = None
                record(row)
                state["rows"].append(row)
                if not row.cleanup_verified:
                    stop_reason = "cleanup_unverified"
                    break
                if row.unexpected:
                    state["failed"] = True
                    cutoff = index if cutoff is None else min(cutoff, index)
                    cancel_later(cutoff, "later_than_first_known_error")
                else:
                    state["next_lookup"] += 1
            if stop_reason:
                break

            while head in states:
                state = states[head]
                if state["failed"]:
                    failing = next(row for row in state["rows"] if row.unexpected)
                    first_error = (failing.module, failing.lookup)
                    first_error_resolved = True
                    stop_reason = "unexpected_probe_result"
                    break
                if state["next_lookup"] != len(LOOKUPS):
                    break
                events.append({"event": "retire", "module": modules[head], "index": head})
                del states[head]
                head += 1
            if stop_reason or head == len(modules):
                break

            # Only the previously dispatched earlier module can advance after
            # a later error; no brand-new module is admitted after that signal.
            if cutoff is None:
                while next_index < len(modules) and next_index < head + cap:
                    states[next_index] = {"handle": None, "next_lookup": 0,
                                          "rows": [], "failed": False, "canceled": False}
                    next_index += 1
            for index, state in sorted(states.items()):
                if state["handle"] is not None or state["failed"] or state["canceled"]:
                    continue
                if state["next_lookup"] == len(LOOKUPS) or (cutoff is not None and index >= cutoff):
                    continue
                lookup = LOOKUPS[state["next_lookup"]]
                # Modulo assignment never changes between A and B.
                state["handle"] = runner.start(index, index % 2, modules[index], lookup)
                events.append({"event": "start", "module": modules[index],
                               "lookup": lookup, "index": index, "lane": index % 2})
            sleep(0.01)
    except Exception as error:
        stop_reason = "scheduler_or_runner_exception"
        diagnose(error)
    finally:
        for index, state in sorted(states.items()):
            if state["handle"] is not None:
                try:
                    row = runner.cancel(state["handle"], stop_reason or "scheduler_cleanup")
                    record(row)
                    if not row.cleanup_verified:
                        stop_reason = "cleanup_unverified"
                        first_error_resolved = False
                except Exception as error:
                    stop_reason = "cleanup_unverified"
                    first_error_resolved = False
                    diagnose(error)
                state["handle"] = None

    observations.sort(key=lambda row: (row.module, LOOKUPS.index(row.lookup)))
    accounting = account_pairs(modules, observations)
    # Canceled/unexpected probes are not successful accounted work.
    unread = set(map(tuple, accounting["missing"]))
    unread.update((row.module, row.lookup) for row in observations
                  if row.reason != "completed" or not row.cleanup_verified)
    complete = (head == len(modules) and stop_reason is None
                and not any(accounting.values())
                and not any(row.unexpected or not row.cleanup_verified for row in observations))
    return ScheduleResult(complete, tuple(observations), tuple(sorted(unread)),
                          first_error, first_error_resolved, stop_reason, tuple(events), tuple(diagnostics))
