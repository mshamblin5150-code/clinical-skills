"""Private, unexecuted linear-history candidate; merges use unchanged oracle."""
from datetime import datetime
import re
import subprocess
import os
import types

SAFE = re.compile(r"[A-Za-z0-9_./ -]+\Z")
MARK = b"BATCH:"
BASE_RUN = subprocess.run


def table(root):
    """Optimization failure is opaque: the ordered oracle remains authoritative."""
    try:
        # Git environment can change revision/pathspec interpretation. No proof
        # is claimed for such invocations, including case-insensitive pathspecs.
        allowed_environment = {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}
        if subprocess.run is not BASE_RUN or any(
                key.startswith('GIT_') and allowed_environment.get(key) != value
                for key, value in os.environ.items()):
            return None
        config = subprocess.run(['git', 'config', '--null', '--list'], cwd=root,
                                capture_output=True, check=False)
        harmless = {'user.name', 'user.email', 'core.repositoryformatversion',
                    'core.filemode', 'core.bare', 'core.logallrefupdates',
                    'core.autocrlf', 'core.symlinks', 'core.worktree',
                    'core.hookspath', 'commit.gpgsign'}
        if config.returncode:
            return None
        for setting in config.stdout.split(b'\0'):
            if not setting:
                continue
            key, separator, value = setting.partition(b'\n')
            if not separator:
                return None
            name = key.decode('ascii').lower()
            if name == 'core.ignorecase' and value == b'false':
                continue
            if name not in harmless:
                return None
        graph = subprocess.run(['git', 'rev-list', '--parents', 'HEAD'], cwd=root,
                               capture_output=True, check=False)
        if graph.returncode or not graph.stdout:
            return None
        rows = graph.stdout.splitlines()
        if any(len(row.split()) > 2 for row in rows):
            return None
        result = subprocess.run(
            ['git', 'log', '--no-renames', '--no-ext-diff', '--no-textconv',
             '--raw', '-z', '--root', '--no-abbrev',
             '--format=%x00BATCH:%H %cI%x00', 'HEAD'],
            cwd=root, capture_output=True, check=False)
        if result.returncode or len(result.stdout) > 64 * 1024 * 1024:
            return None
        records = result.stdout.split(b'\0')
        found, directories, commits, stamp = {}, set(), [], None
        i = 0
        while i < len(records):
            record = records[i].lstrip(b'\n')
            i += 1
            if not record:
                continue
            if record.startswith(MARK):
                oid, raw_stamp = record[len(MARK):].split(b' ', 1)
                commits.append(oid)
                stamp = datetime.fromisoformat(raw_stamp.decode('ascii').replace('Z', '+00:00'))
            elif record.startswith(b':') and stamp is not None:
                if not re.fullmatch(rb':[0-7]{6} [0-7]{6} [0-9a-f]+ [0-9a-f]+ [AMDT]', record):
                    return None
                if i >= len(records):
                    return None
                path = records[i].decode('utf-8', 'surrogateescape')
                i += 1
                found.setdefault(path, (stamp, oid.decode('ascii')))
                # A currently indexed file may historically have named a
                # directory. Git's pathspec also selects its descendants.
                # Keep that spelling on the unchanged oracle.
                pieces = path.split('/')
                directories.update('/'.join(pieces[:n]) for n in range(1, len(pieces)))
            else:
                return None
        if commits != [row.split()[0] for row in rows]:
            return None
        return found, directories
    except (OSError, ValueError, UnicodeError):
        return None


def install(module, observe=None):
    """Keep the original ordered grading/body-read loop and invocation-local state."""
    original_grade, oracle = module.grade_adrs, module._last_touch

    def grade(root):
        current_oracle = module._last_touch
        # A caller/test owns any later replacement. Never optimize past it.
        owned_original = (isinstance(oracle, types.FunctionType)
                          and oracle.__module__ == module.__name__
                          and oracle.__name__ == '_last_touch')
        batch = table(root) if current_oracle is oracle and owned_original else None

        def lookup(path_root, relative):
            value = None
            used_batch = (batch is not None and SAFE.fullmatch(relative)
                          and relative not in batch[1])
            if used_batch:
                value = batch[0].get(relative)
                result = None if value is None else value[0]
            else:
                result = current_oracle(path_root, relative)
            if observe is not None:
                observe(path_root, relative, result, None if value is None else value[1], bool(used_batch))
            return result

        module._last_touch = lookup
        try:
            return original_grade(root)
        finally:
            if module._last_touch is lookup:
                module._last_touch = current_oracle

    module.grade_adrs = grade
    return original_grade

