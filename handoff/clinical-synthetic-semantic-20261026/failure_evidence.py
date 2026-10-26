"""Private failure evidence. Secondary failures never replace the first error."""
import base64
import hashlib
import json
from pathlib import Path


def describe(error):
    return {'type': type(error).__name__, 'message': str(error)}


def write_new(path, value):
    from budget import write
    write(Path(path), value)


def stream_record(value):
    if value is None:
        return None
    if not isinstance(value, bytes):
        raise TypeError('Captured diagnostic stream is not bytes')
    return {'base64': base64.b64encode(value).decode('ascii'), 'bytes': len(value),
            'sha256': hashlib.sha256(value).hexdigest()}


def retain_git_failure(path, command, cwd, error, *, result=None):
    """Record exact captured bytes; absent/partial streams are labeled, not filled."""
    try:
        value = {'command': command, 'cwd': str(cwd), 'primary': describe(error),
                 'returncode': None if result is None else result.returncode,
                 'streams_complete': result is not None,
                 'stdout': stream_record(result.stdout if result is not None else getattr(error, 'stdout', None)),
                 'stderr': stream_record(result.stderr if result is not None else getattr(error, 'stderr', None))}
        stdout = result.stdout if result is not None else getattr(error, 'stdout', None)
        stderr = result.stderr if result is not None else getattr(error, 'stderr', None)
        if len(stdout or b'') + len(stderr or b'') > 16384:
            value['streams_complete'] = False
            value['overflow'] = True
            value['original_counts'] = [len(stdout or b''), len(stderr or b'')]
            first = (stdout or b'')[:16384]
            second = (stderr or b'')[:16384-len(first)]
            value['stdout'], value['stderr'] = stream_record(first), stream_record(second)
            error.add_note('First-failure raw output cap exceeded; retained prefix incomplete')
        write_new(path, value)
    except BaseException as secondary:
        error.add_note('Git diagnostic persistence failed: ' + repr(secondary))
        # The original traceback still reaches the worker stderr even if the
        # diagnostic file cannot be written. No retry or truncation as success.


class Cleanup:
    def __init__(self):
        self.actions = []
        self.errors = []

    def call(self, name, action):
        try:
            value = action()
            self.actions.append({'action': name, 'state': 'OK'})
            return value
        except BaseException as error:
            self.errors.append((name, error))
            self.actions.append({'action': name, 'state': 'UNKNOWN', 'error': describe(error)})
            return None

    def persist(self, path, value):
        self.call('write ' + Path(path).name, lambda: write_new(path, value))

    def conclude(self, primary):
        if not self.errors:
            return
        notes = '; '.join(name + ': ' + repr(error) for name, error in self.errors)
        if primary is not None:
            primary.add_note('Secondary cleanup/evidence failures: ' + notes)
            return
        first = self.errors[0][1]
        first.add_note('Cleanup/evidence actions: ' + notes)
        raise first
