"""Source-only worker. External containment and explicit runtime release required."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import time
import subprocess
import hashlib
import os

sys.dont_write_bytecode = True


def outcome(module, root):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            status = ('exit', module.main([], root=root))
        except Exception as exc:
            status = ('exception', type(exc).__name__, str(exc))
    return status, out.getvalue(), err.getvalue()


def parity(module, root):
    original = module._last_touch
    before, after, routes = [], [], []

    def row(path_root, relative, stamp, oid=None):
        if oid is None:
            raw = subprocess.run(['git', 'log', '-1', '--format=%H', '--', relative],
                                 cwd=path_root, capture_output=True, check=False)
            if raw.returncode:
                raise RuntimeError('Independent selected-commit oracle failed')
            oid = raw.stdout.decode('ascii').strip() or None
        return (relative.encode('utf-8', 'surrogateescape').hex(),
                None if stamp is None else stamp.isoformat(), oid)

    def traced(path_root, relative):
        stamp = original(path_root, relative)
        before.append(row(path_root, relative, stamp))
        return stamp

    module._last_touch = traced
    try:
        baseline = outcome(module, root)
    finally:
        module._last_touch = original
    from candidate import install
    def observed(path_root, path, stamp, oid, used):
        after.append(row(path_root, path, stamp, oid))
        routes.append([path, used])
    old_grade = install(module, observed)
    try:
        candidate = outcome(module, root)
    finally:
        module.grade_adrs = old_grade
    if baseline != candidate or before != after:
        raise RuntimeError('Ordered selected-commit/date or public parity mismatch')
    return {'parity': True, 'ordered_paths': before, 'outcome': baseline, 'routes': routes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['qualify'])
    parser.add_argument('--checkout', type=Path, required=True)
    parser.add_argument('--side', choices=['A', 'B'], required=True)
    parser.add_argument('--refusal', choices=['icd10_lookup', 'procedure_codes_lookup'])
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--admission', type=Path, required=True)
    args = parser.parse_args()
    # This source release intentionally contains no usable execution grant.
    grant = json.loads(args.release.read_bytes())
    if grant.get('runtime_authorized') is not True:
        raise RuntimeError('Runtime is held')
    deadline = time.monotonic() + 10
    while not (args.admission / 'admitted.json').exists():
        if time.monotonic() >= deadline:
            raise RuntimeError('External containment admission absent')
        time.sleep(.02)
    admission = json.loads((args.admission / 'admitted.json').read_bytes())
    if admission['pid'] != os.getpid():
        raise RuntimeError('Wrong admitted process')
    for name, expected in admission['sources'].items():
        if hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Admitted source drift')
    def receipt(value):
        value.update(pid=os.getpid(), side=args.side, mode=args.mode)
        from budget import write
        write(args.admission / 'receipt.json', value)
    sys.path.insert(0, str(args.checkout / 'tools'))
    import tracker_coordinates as module
    if args.mode == 'qualify':
        os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        from fixtures import build, CASES
        paths = build(args.admission / 'fixtures')
        results = [parity(module, path) for path in paths]
        if len(results) != len(CASES):
            raise RuntimeError('Missing adversarial fixture')
        for case, result in zip(CASES, results):
            if case in ('before', 'equal', 'after', 'skew', 'rename', 'readd', 'spaces'):
                if not result['routes'] or not all(used for _, used in result['routes']):
                    raise RuntimeError('Required linear fastpath was not consumed: ' + case)
            if case.startswith('merge-') and any(used for _, used in result['routes']):
                raise RuntimeError('Merge did not use unchanged oracle')
        directory = results[list(CASES).index('directory')]
        if ['docs/adr/a.md', False] not in directory['routes']:
            raise RuntimeError('Historical directory fallback missing')
        # Error-precedence and population failures are injected at the same
        # public grading seam, with independent original implementation as A.
        from unittest import mock
        for failure in ('population', 'last-touch', 'body'):
            root = paths[2]
            if failure == 'population':
                context = mock.patch.object(module, 'read_path_records', side_effect=module.GitPathError('synthetic'))
            elif failure == 'last-touch':
                context = mock.patch.object(module, '_last_touch', side_effect=module.SourceError('synthetic touch'))
            else:
                context = mock.patch.object(Path, 'read_text', side_effect=OSError('synthetic body'))
            with context:
                results.append(parity(module, root))
        # Competing source failures must select the same first error as A.
        with mock.patch.object(module, '_last_touch', side_effect=module.SourceError('first touch')):
            with mock.patch.object(Path, 'read_text', side_effect=OSError('later body')):
                results.append(parity(module, paths[2]))
        with mock.patch.dict(os.environ, {'GIT_ICASE_PATHSPECS': '1'}):
            result = parity(module, paths[2])
            if any(used for _, used in result['routes']):
                raise RuntimeError('Case-insensitive pathspec environment not refused')
            results.append(result)
        from candidate import table, install
        real_run = subprocess.run
        def malformed(command, *values, **kwargs):
            if command[:2] == ['git', 'log'] and '-1' not in command:
                return subprocess.CompletedProcess(command, 0, b'broken', b'')
            return real_run(command, *values, **kwargs)
        with mock.patch.object(subprocess, 'run', malformed):
            result = parity(module, paths[2])
            if any(used for _, used in result['routes']):
                raise RuntimeError('Acquisition replacement was not refused')
            results.append(result)
        import candidate as candidate_module
        with mock.patch.object(subprocess, 'run', malformed):
            with mock.patch.object(candidate_module, 'BASE_RUN', malformed):
                if table(paths[2]) is not None:
                    raise RuntimeError('Malformed acquisition bytes accepted')
        # Later caller-owned patches must be honored and restored exactly.
        old_grade = install(module)
        original_touch = module._last_touch
        replacement = mock.Mock(side_effect=module.SourceError('owned caller patch'))
        module._last_touch = replacement
        try:
            outcome(module, paths[2])
            if module._last_touch is not replacement or replacement.call_count != 1:
                raise RuntimeError('Caller patch ownership changed')
        finally:
            module._last_touch, module.grade_adrs = original_touch, old_grade
        original_body_grade = module.grade
        for side in ('A', 'B'):
            touch, grade_function = module._last_touch, module.grade_adrs
            replacement = mock.Mock(side_effect=module.SourceError('during invocation'))
            def replace_during_body(text, locator):
                module._last_touch = replacement
                return original_body_grade(text, locator)
            module.grade = replace_during_body
            if side == 'B':
                install(module)
            try:
                value = outcome(module, paths[2])
                if module._last_touch is not replacement or replacement.call_count != 1:
                    raise RuntimeError('In-flight caller patch was overwritten')
                if side == 'A':
                    expected_error = value
                elif value != expected_error:
                    raise RuntimeError('In-flight patch changed first error')
            finally:
                module._last_touch, module.grade_adrs, module.grade = touch, grade_function, original_body_grade
        receipt({'coverage': list(CASES) + ['population', 'last-touch', 'body',
                 'competing-failures', 'case-insensitive', 'acquisition-replacement',
                 'malformed-acquisition', 'caller-patch-ownership', 'in-flight-patch'], 'results': results})
        return
    if args.mode == 'parity':
        if args.fixture is None or args.side != 'B':
            raise ValueError('Parity requires fixture and B')
        print(json.dumps(parity(module, args.fixture)))
        return
    if args.refusal is None:
        raise ValueError('Probe requires refusal')
    import code_set_database_reader_check as audit
    if audit.PHASE_ENV in os.environ:
        raise RuntimeError('Other instrumentation environment is unsupported')
    calls, git_calls, tests = [], [], []
    original_run = subprocess.run
    def timed(command, *pos, **kwargs):
        started = time.perf_counter()
        code, error = None, None
        try:
            result = original_run(command, *pos, **kwargs)
            code = result.returncode
            return result
        except Exception as exc:
            error = type(exc).__name__
            raise
        finally:
            if command and command[0] == 'git':
                git_calls.append({'seconds': time.perf_counter() - started, 'code': code,
                                  'error': error, 'real': Path(kwargs.get('cwd', '.')).resolve() == args.checkout.resolve()})
    subprocess.run = timed
    def observed(root, path, stamp, oid, used):
        calls.append((path.encode('utf-8', 'surrogateescape').hex(), used,
                      root.resolve() == args.checkout.resolve()))
    if args.side == 'B':
        from candidate import install
        install(module, observed)
    else:
        original_grade = module.grade_adrs
        def grade(root):
            original = module._last_touch
            def traced(path_root, relative):
                result = original(path_root, relative)
                observed(path_root, relative, result, None, False)
                return result
            module._last_touch = traced
            try:
                return original_grade(root)
            finally:
                if module._last_touch is traced:
                    module._last_touch = original
        module.grade_adrs = grade
    sys.argv = ['-c', str(args.checkout / 'tools'), 'test_tracker_coordinates', args.refusal]
    started = time.perf_counter()
    status = None
    namespace = {'__name__': '__main__'}
    import unittest
    original_loader = unittest.defaultTestLoader.loadTestsFromName
    def flatten(suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from flatten(test)
            else:
                yield test.id()
    def load(*values, **kwargs):
        suite = original_loader(*values, **kwargs)
        tests.extend(flatten(suite))
        return suite
    unittest.defaultTestLoader.loadTestsFromName = load
    try:
        exec(compile(audit._SUBPROCESS, '<unchanged-reader-probe>', 'exec'),
             namespace)
    except SystemExit as exc:
        status = exc.code
    finally:
        elapsed = time.perf_counter() - started
        subprocess.run = original_run
        unittest.defaultTestLoader.loadTestsFromName = original_loader
    if type(status) is not int or status != 0:
        raise RuntimeError('Probe did not exit successfully')
    result = namespace.get('result')
    if (result is None or result.testsRun != 20 or result.skipped
            or result.errors or result.failures or result.expectedFailures
            or result.unexpectedSuccesses):
        raise RuntimeError('Complete unchanged 20-test coverage not established')
    if len(tests) != 20:
        raise RuntimeError('Test identity population incomplete')
    real_paths = [bytes.fromhex(path) for path, _, real in calls if real]
    sequence = hashlib.sha256(b''.join(hashlib.sha256(path).digest() for path in real_paths)).hexdigest()
    if len(real_paths) != 880 or sequence != 'ae98800ada145e3741734fc66000fef84dc4b4cd96539c337d6428e9e6f4b472':
        raise RuntimeError('Frozen real path population differs from retained baseline')
    if any(row['real'] and (row['code'] != 0 or row['error'] is not None) for row in git_calls):
        raise RuntimeError('Real Git failure invalidates timing')
    receipt({'refusal': args.refusal, 'seconds': elapsed, 'status': status,
             'logical_calls': calls, 'tests': tests, 'git_calls': git_calls,
             'logical_digest': hashlib.sha256(json.dumps([p for p, _, _ in calls]).encode()).hexdigest(),
             'batch_calls': sum(used for _, used, _ in calls), 'real_sequence': sequence})


if __name__ == '__main__':
    main()
