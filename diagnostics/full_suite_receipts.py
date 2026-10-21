"""Bounded interpretation of the unchanged suite's native accounting summary.

The suite reconciles ID Counters internally. Its stdout is not an independent
executed-ID manifest and does not expose aggregate skip/expected-failure totals.
"""
import math
from pathlib import PurePosixPath
import re

from lazy_suite_support import digest, require

_PREFIXES = ('discovered:', 'unaccounted:', 'jobs:', 'weights:',
             "critical path (this run's elapsed time):")
_NUMBER = r'(?:0|[1-9][0-9]{0,9})'
_SECONDS = r'(?:0|[1-9][0-9]{0,9})\.[0-9]{3}'
_FAULT = re.compile(r'^(?:module did not load:|worker [0-9]+ ended without reporting\b|'
                    r'duplicate id:|duplicate worker id:|unexpected id:)', re.MULTILINE)


def parse_suite(stdout, stderr, returncode, expected_count, cpu_count):
    """Require native complete accounting; retain a regression's original exit1."""
    require(isinstance(stdout, str) and isinstance(stderr, str), 'suite_capture_unread')
    require(type(returncode) is int and returncode in (0, 1), 'suite_exit_incomplete')
    require(type(expected_count) is int and expected_count > 0
            and type(cpu_count) is int and cpu_count > 0, 'suite_expectation_invalid')
    lines = stdout.splitlines()
    all_lines = lines + stderr.splitlines()
    require(len(lines) >= 5 and all(sum(line.startswith(prefix) for line in all_lines) == 1
                                  for prefix in _PREFIXES), 'suite_summary_missing_or_duplicate')
    require(not _FAULT.search(stdout) and not _FAULT.search(stderr), 'suite_accounting_fault')
    tail = lines[-5:]
    count = re.fullmatch(r'discovered: (' + _NUMBER + r')', tail[0])
    unaccounted = re.fullmatch(r'unaccounted: (' + _NUMBER + r')', tail[1])
    jobs = max(1, cpu_count * 3 // 4)
    expected_jobs = (f'jobs: {jobs} (max(1, (os.cpu_count() or 1) * 3 // 4); '
                     f'os.cpu_count()={cpu_count})')
    timing = re.fullmatch(r"critical path \(this run's elapsed time\): (\S{1,1024}) (" + _SECONDS
                          + r')s; wall (' + _SECONDS + r')s; next-slowest worker (' + _SECONDS + r')s', tail[4])
    require(count is not None and unaccounted is not None and timing is not None
            and tail[2] == expected_jobs and tail[3] == 'weights: equal', 'suite_summary_invalid')
    require(int(count[1]) == expected_count and int(unaccounted[1]) == 0, 'suite_population_unaccounted')
    critical, wall, next_worker = (float(timing[index]) for index in (2, 3, 4))
    require(all(math.isfinite(value) and value >= 0 for value in (critical, wall, next_worker))
            and wall > 0, 'suite_timing_invalid')
    return {'discovered': expected_count, 'unaccounted': 0, 'jobs': jobs,
            'cpu_count': cpu_count, 'weights': 'equal', 'returncode': returncode,
            'successful': returncode == 0, 'internal_accounting': True,
            'independent_executed_id_manifest': False, 'skips': 'not separately exposed',
            'expected_failures': 'not separately exposed',
            'critical_unit_token': digest(timing[1].encode('utf-8')),
            'critical_unit_seconds': critical, 'suite_reported_wall_seconds': wall,
            'next_worker_seconds': next_worker}


def allowed_retained(name, expected):
    """Allow only native suite weights and bytecode of a pinned Python source."""
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or any(part in ('.', '..') for part in path.parts):
        return False
    if name in expected:
        return False
    if name == 'scratch/runs/suite-weights.json':
        return True
    if path.parent.name != '__pycache__':
        return False
    match = re.fullmatch(r'(.+)\.cpython-[0-9]{2,3}(?:\.opt-[12])?\.pyc', path.name)
    if not match:
        return False
    source = (path.parent.parent / (match[1] + '.py')).as_posix()
    return source in expected


def failure_target_receipt(stdout):
    """Tokens from native failure-target lines only; never raw output or paths."""
    prefix = 're-run (from tools/): python -m unittest '
    tokens, total, unread = [], 0, 0
    for line in stdout.splitlines():
        if not line.startswith(prefix):
            continue
        total += 1
        target = line[len(prefix):]
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){1,8}', target) or len(target) > 512:
            unread += 1
        elif len(tokens) < 100:
            tokens.append(digest(target.encode('ascii')))
    return {'failure_target_line_count': total, 'failure_target_tokens': tokens,
            'unread_target_count': unread, 'truncated': total > 100,
            'independent_failure_manifest': False}
