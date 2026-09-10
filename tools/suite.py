#!/usr/bin/env python3
"""Run and account for the repository's complete unittest population."""

from __future__ import annotations

import argparse
import io
import json
import multiprocessing
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import run_grader
import repo_root
from console_codec import use_utf8


TOOLS = Path(__file__).resolve().parent


DECLARED_LIMITS = (
    (
        "whether a worker that never finishes is reported",
        "the suite sets no time bound and waits for the worker",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a test outside test*.py under tools ran",
        "discovery defines that population and excludes every other file shape",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
)


@dataclass(frozen=True)
class Unit:
    """One discovered ``TestCase`` class and its tests in discovery order."""

    name: str
    test_ids: tuple[str, ...]
    order: int


@dataclass(frozen=True)
class Outcome:
    test_id: str
    status: str
    detail: str = ""


@dataclass(frozen=True)
class WorkerReport:
    outcomes: tuple[Outcome, ...]
    unit_times: tuple[tuple[str, float], ...]
    elapsed: float
    output: str = ""
    load_errors: tuple[str, ...] = ()


class AccountingResult(unittest.TextTestResult):
    """A normal unittest result that also emits one outcome per test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes: list[Outcome] = []
        self._recorded: set[int] = set()
        self._started: dict[int, float] = {}
        self.test_times: dict[str, float] = {}
        self.unit_times: list[tuple[str, float]] = []

    def startTest(self, test):
        self._started[id(test)] = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        started = self._started.pop(id(test), time.perf_counter())
        self.test_times[test.id()] = self.test_times.get(test.id(), 0.0) + (
            time.perf_counter() - started
        )
        if id(test) not in self._recorded:
            self._record(test, "pass")
        super().stopTest(test)

    def _record(self, test, status: str, detail: str = ""):
        marker = id(test)
        if marker in self._recorded:
            return
        self._recorded.add(marker)
        self.outcomes.append(Outcome(test.id(), status, detail))

    def addSuccess(self, test):
        self._record(test, "pass")
        super().addSuccess(test)

    def addFailure(self, test, err):
        self._record(test, "failure", self._exc_info_to_string(err, test))
        super().addFailure(test, err)

    def addError(self, test, err):
        self._record(test, "error", self._exc_info_to_string(err, test))
        super().addError(test, err)

    def addSkip(self, test, reason):
        self._record(test, "skip", reason)
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._record(test, "skip", self._exc_info_to_string(err, test))
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._record(test, "failure", "unexpected success")
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            status = "failure" if issubclass(err[0], test.failureException) else "error"
            self._record(test, status, self._exc_info_to_string(err, test))
        super().addSubTest(test, subtest, err)


class TimedUnitSuite(unittest.TestSuite):
    """Measure one class unit, including its class fixture."""

    def __init__(self, unit_name: str, tests):
        super().__init__(tests)
        self.unit_name = unit_name

    def run(self, result, debug=False):
        started = time.perf_counter()
        try:
            return super().run(result, debug)
        finally:
            self._tearDownPreviousClass(object(), result)
            self._handleModuleTearDown(result)
            result._previousTestClass = None
            result.unit_times.append((self.unit_name, time.perf_counter() - started))


def _test_cases(member):
    if isinstance(member, unittest.TestSuite):
        for child in member:
            yield from _test_cases(child)
    else:
        yield member


def _units(tests) -> tuple[Unit, ...]:
    grouped: dict[type, list[str]] = {}
    for test in tests:
        grouped.setdefault(test.__class__, []).append(test.id())
    return tuple(
        Unit(
            f"{test_class.__module__}.{test_class.__qualname__}",
            tuple(test_ids),
            order,
        )
        for order, (test_class, test_ids) in enumerate(grouped.items())
    )


def _weight_plan(
    units: tuple[Unit, ...], scratch: Path
) -> tuple[dict[str, float], str]:
    path = scratch / "runs" / "suite-weights.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        recorded = {
            str(name): float(value)
            for name, value in raw.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0
        }
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        recorded = {}
    if not recorded:
        return {unit.name: 1.0 for unit in units}, "equal"
    mean = sum(recorded.values()) / len(recorded)
    return {unit.name: recorded.get(unit.name, mean) for unit in units}, "recorded"


def _pack(
    units: tuple[Unit, ...], jobs: int, weights: dict[str, float]
) -> tuple[tuple[Unit, ...], ...]:
    bins: list[list[Unit]] = [[] for _ in range(min(jobs, len(units)))]
    totals = [0.0] * len(bins)
    for unit in sorted(units, key=lambda item: (-weights[item.name], item.order)):
        index = min(range(len(bins)), key=lambda candidate: (totals[candidate], candidate))
        bins[index].append(unit)
        totals[index] += weights[unit.name]
    return tuple(tuple(bin_) for bin_ in bins)


def _write_weights(scratch: Path, unit_times: dict[str, float]) -> None:
    if not scratch.is_dir():
        return
    runs = scratch / "runs"
    runs.mkdir(exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=runs, prefix="suite-weights-", suffix=".tmp", delete=False
        ) as handle:
            json.dump(dict(sorted(unit_times.items())), handle, indent=2)
            handle.write("\n")
            temporary = Path(handle.name)
        os.replace(temporary, runs / "suite-weights.json")
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _loaded_suite(unit: Unit, module_dir: Path):
    module_text = str(module_dir)
    if module_text not in sys.path:
        sys.path.insert(0, module_text)
    loader = unittest.TestLoader()
    loaded = unittest.TestSuite(loader.loadTestsFromName(name) for name in unit.test_ids)
    failed = tuple(
        test
        for test in _test_cases(loaded)
        if test.__class__.__name__ == "_FailedTest"
        and test.__class__.__module__ == "unittest.loader"
    )
    return loaded, tuple(loader.errors), failed


def _worker(module_dir_text: str, assignment: tuple[Unit, ...]) -> WorkerReport:
    started = time.perf_counter()
    errors: list[str] = []
    unit_suites: list[TimedUnitSuite] = []
    for unit in assignment:
        loaded, load_errors, failed = _loaded_suite(unit, Path(module_dir_text))
        if load_errors or failed:
            errors.extend(load_errors or (f"worker could not load {unit.name}",))
            continue
        unit_suites.append(TimedUnitSuite(unit.name, tuple(_test_cases(loaded))))
    output = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=output,
        verbosity=0,
        resultclass=AccountingResult,
    )
    result = runner.run(unittest.TestSuite(unit_suites))
    return WorkerReport(
        tuple(result.outcomes),
        tuple(result.unit_times),
        time.perf_counter() - started,
        output.getvalue() if not result.wasSuccessful() else "",
        tuple(errors),
    )


def _in_process(tests, units: tuple[Unit, ...], stream: TextIO) -> WorkerReport:
    started = time.perf_counter()
    grouped: dict[type, list[unittest.TestCase]] = {}
    for test in tests:
        grouped.setdefault(test.__class__, []).append(test)
    unit_suites = tuple(
        TimedUnitSuite(unit.name, members)
        for unit, members in zip(units, grouped.values())
    )
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=1,
        resultclass=AccountingResult,
    )
    result = runner.run(unittest.TestSuite(unit_suites))
    return WorkerReport(
        tuple(result.outcomes),
        tuple(result.unit_times),
        time.perf_counter() - started,
    )


def _parallel(
    module_dir: Path,
    assignments: tuple[tuple[Unit, ...], ...],
) -> tuple[tuple[WorkerReport, ...], tuple[str, ...]]:
    context = multiprocessing.get_context("spawn")
    reports: list[WorkerReport | None] = [None] * len(assignments)
    receive_errors: list[str | None] = [None] * len(assignments)
    processes = []
    receivers = []

    def receive(index, connection):
        try:
            reports[index] = connection.recv()
        except (EOFError, OSError) as error:
            receive_errors[index] = str(error) or error.__class__.__name__
        finally:
            connection.close()

    for index, assignment in enumerate(assignments):
        receiving, sending = context.Pipe(duplex=False)
        process = context.Process(
            target=_worker_entry,
            args=(sending, str(module_dir), assignment),
            name=f"suite-worker-{index + 1}",
        )
        process.start()
        sending.close()
        receiver = threading.Thread(target=receive, args=(index, receiving))
        receiver.start()
        processes.append(process)
        receivers.append(receiver)

    for process in processes:
        process.join()
    for receiver in receivers:
        receiver.join()

    missing = tuple(
        f"worker {index + 1} ended without reporting "
        f"(exit {process.exitcode}; {receive_errors[index] or 'no report'})"
        for index, process in enumerate(processes)
        if reports[index] is None
    )
    return tuple(report for report in reports if report is not None), missing


def _worker_entry(connection, module_dir_text: str, assignment: tuple[Unit, ...]) -> None:
    try:
        connection.send(_worker(module_dir_text, assignment))
    finally:
        connection.close()


def _loader_module(error: str) -> str:
    match = re.search(r"Failed to import test module: ([^\n]+)", error)
    return match.group(1) if match else "unknown module"


def run_suite(
    module_dir: Path,
    *,
    jobs: int,
    slowest: int,
    scratch: Path,
    stream: TextIO,
    job_derivation: str = "requested",
) -> int:
    """Run the suite discovered under ``module_dir`` and return its status."""
    started = time.perf_counter()
    loader = unittest.TestLoader()
    discovered = tuple(
        _test_cases(loader.discover(start_dir=module_dir, top_level_dir=module_dir))
    )
    discovered_ids = tuple(test.id() for test in discovered)
    loader_failures = tuple(
        test
        for test in discovered
        if test.__class__.__name__ == "_FailedTest"
        and test.__class__.__module__ == "unittest.loader"
    )
    runnable = tuple(test for test in discovered if test not in loader_failures)
    units = _units(runnable)
    weights, weight_source = _weight_plan(units, scratch)
    assignments = _pack(units, jobs, weights) if units else ()

    if jobs == 1:
        reports = (_in_process(runnable, units, stream),)
        missing_workers: tuple[str, ...] = ()
    elif assignments:
        reports, missing_workers = _parallel(module_dir, assignments)
        for report in reports:
            if report.output:
                print(report.output, end="", file=stream)
    else:
        reports, missing_workers = (), ()

    outcomes = tuple(outcome for report in reports for outcome in report.outcomes)
    actual = Counter(outcome.test_id for outcome in outcomes)
    expected = Counter(discovered_ids)
    mismatched = sorted(
        test_id
        for test_id in set(expected) | set(actual)
        if expected[test_id] != 1 or actual[test_id] != 1
    )
    duplicate_ids = sorted(test_id for test_id, count in expected.items() if count != 1)
    duplicate_worker_ids = sorted(
        test_id for test_id, count in actual.items() if count != 1
    )
    unexpected_ids = sorted(test_id for test_id in actual if test_id not in expected)

    for error in loader.errors:
        print(f"module did not load: {_loader_module(error)}", file=stream)
    for report in reports:
        for error in report.load_errors:
            print(f"module did not load in worker: {_loader_module(error)}", file=stream)
    for message in missing_workers:
        print(message, file=stream)
    for test_id in duplicate_ids:
        print(f"duplicate id: {test_id}", file=stream)
    for test_id in duplicate_worker_ids:
        print(f"duplicate worker id: {test_id}", file=stream)
    for test_id in unexpected_ids:
        print(f"unexpected id: {test_id}", file=stream)
    for outcome in outcomes:
        if outcome.status in {"failure", "error"}:
            print(
                f"re-run (from tools/): python -m unittest {outcome.test_id}",
                file=stream,
            )

    wall = time.perf_counter() - started
    unit_times = dict(pair for report in reports for pair in report.unit_times)
    ordered_times = sorted(unit_times.items(), key=lambda pair: (-pair[1], pair[0]))
    worker_times = sorted((report.elapsed for report in reports), reverse=True)
    slowest_name, slowest_time = ordered_times[0] if ordered_times else ("none", 0.0)
    next_worker = worker_times[1] if len(worker_times) > 1 else 0.0

    print(f"discovered: {len(discovered)}", file=stream)
    print(f"unaccounted: {len(mismatched)}", file=stream)
    print(f"jobs: {jobs} ({job_derivation})", file=stream)
    print(f"weights: {weight_source}", file=stream)
    print(
        "critical path (this run's elapsed time): "
        f"{slowest_name} {slowest_time:.3f}s; wall {wall:.3f}s; "
        f"next-slowest worker {next_worker:.3f}s",
        file=stream,
    )
    for name, elapsed in ordered_times[:slowest]:
        print(f"slow unit: {name} {elapsed:.3f}s", file=stream)

    has_test_failure = any(
        outcome.status in {"failure", "error"} for outcome in outcomes
    )
    incomplete = bool(
        not discovered
        or loader.errors
        or any(report.load_errors for report in reports)
        or missing_workers
        or mismatched
    )
    if discovered and not incomplete:
        _write_weights(scratch, unit_times)
    if has_test_failure:
        return 1
    return 2 if incomplete else 0


def _positive(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def _nonnegative(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be at least 0")
    return parsed


def main(
    argv: list[str] | None = None,
    *,
    module_dir: Path = TOOLS,
    scratch: Path | None = None,
    stream: TextIO | None = None,
) -> int:
    """Run every discovered test; use ``--jobs 1`` to reproduce a failure.

    The three-quarter default is ADR 0164's one-machine measurement, not a
    general claim about the best fraction on another machine.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--jobs", type=_positive)
    parser.add_argument("--slowest", type=_nonnegative, default=0, metavar="N")
    args = parser.parse_args(argv)
    cpu_count = os.cpu_count()
    jobs = args.jobs if args.jobs is not None else max(1, (cpu_count or 1) * 3 // 4)
    derivation = (
        "--jobs"
        if args.jobs is not None
        else "max(1, (os.cpu_count() or 1) * 3 // 4); "
        f"os.cpu_count()={cpu_count}"
    )
    return run_suite(
        module_dir,
        jobs=jobs,
        slowest=args.slowest,
        scratch=scratch if scratch is not None else repo_root.scratch_root(),
        stream=stream if stream is not None else sys.stdout,
        job_derivation=derivation,
    )


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
