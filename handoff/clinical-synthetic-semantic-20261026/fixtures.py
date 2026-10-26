"""Private adversarial fixture producer. Inert until explicitly invoked by worker."""
import os
from pathlib import Path
import subprocess
from failure_evidence import retain_git_failure

CASES = ('before', 'equal', 'after', 'skew', 'rename', 'readd', 'directory',
         'staged', 'unborn', 'missing-body', 'pathspec', 'spaces', 'merge-same',
         'merge-divergent', 'merge-conflict', 'duplicate-index', 'bytes')


def build(parent):
    """Never adopt an existing fixture root. All names and contents are synthetic."""
    parent = Path(parent)
    parent.mkdir(exist_ok=False)
    for case in CASES:
        root = parent / case
        root.mkdir()
        environment = dict(os.environ)
        for key in tuple(environment):
            if key.startswith('GIT_'):
                del environment[key]
        environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        def git(*args, data=None, date='2026-09-12T09:51:07+00:00', accepted=(0,)):
            env = dict(environment, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
            command = ['git', '-c', 'core.hooksPath=' + str(root / 'empty-hooks'),
                       '-c', 'commit.gpgsign=false', '-c', 'tag.gpgsign=false',
                       '-c', 'maintenance.auto=false', *args]
            try:
                result = subprocess.run(command, cwd=root, env=env,
                                        input=data, capture_output=True, timeout=10)
            except BaseException as error:
                retain_git_failure(parent.parent / 'git-first-failure.json', command, root, error)
                raise
            if result.returncode not in accepted:
                error = RuntimeError(f'Fixture {case}: git {args[0]} failed')
                retain_git_failure(parent.parent / 'git-first-failure.json', command, root, error, result=result)
                raise error
            return result.stdout
        def write(name, text='Unanchored tools/synthetic.py:12\n'):
            path = root / 'docs' / 'adr' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        def commit(message, date='2026-09-12T09:51:07+00:00'):
            git('add', '-A')
            git('commit', '-qm', message, date=date)
        (root / 'empty-hooks').mkdir()
        git('init', '-q', '--template=', '--initial-branch=main')
        git('config', 'core.ignorecase', 'false')
        git('config', 'user.name', 'Synthetic Writer')
        git('config', 'user.email', 'synthetic@example.invalid')
        if case == 'unborn':
            write('a.md')
            git('add', '-A')
            continue
        write('base.md', 'Anchored by `symbol` at tools/synthetic.py:12.\n')
        commit('base', '2026-09-12T09:51:05+00:00')
        if case in ('before', 'equal', 'after', 'skew'):
            write('a.md')
            commit('target', {'before':'2026-09-12T09:51:05+00:00',
                             'equal':'2026-09-12T09:51:06+00:00'}.get(case,
                             '2026-09-12T09:51:07+00:00'))
            if case == 'skew':
                write('base.md', 'Different synthetic prose.\n')
                commit('skew', '2020-01-01T00:00:00+00:00')
        elif case == 'directory':
            write('a.md/child.md')
            commit('directory')
            git('rm', '-r', 'docs/adr/a.md')
            commit('remove directory')
            write('a.md')
            git('add', '-A')
        elif case in ('staged', 'missing-body'):
            write('a.md')
            git('add', '-A')
            if case == 'missing-body':
                (root / 'docs/adr/a.md').unlink()
        elif case in ('pathspec', 'spaces'):
            write('a[1].md' if case == 'pathspec' else 'a b.md')
            commit('name')
        elif case in ('rename', 'readd'):
            write('a.md')
            commit('create')
            if case == 'rename':
                git('mv', 'docs/adr/a.md', 'docs/adr/b.md')
                commit('rename')
            else:
                git('rm', 'docs/adr/a.md')
                commit('delete')
                write('a.md', 'Readded tools/synthetic.py:13\n')
                commit('readd')
        elif case.startswith('merge-'):
            git('checkout', '-qb', 'side')
            write('side.md' if case == 'merge-same' else 'base.md', 'Side prose.\n')
            commit('side')
            git('checkout', '-q', 'main')
            write('main.md' if case != 'merge-conflict' else 'base.md', 'Main prose.\n')
            commit('main')
            if case == 'merge-conflict':
                git('merge', '--no-ff', '--no-commit', 'side', accepted=(1,))
                write('base.md', 'Resolved tools/synthetic.py:14\n')
                commit('resolved')
            else:
                git('merge', '--no-ff', '-qm', 'merge', 'side')
        elif case == 'duplicate-index':
            write('a.md')
            blob = git('hash-object', '-w', '--stdin', data=b'Fixture\n').strip()
            git('update-index', '--index-info', data=b''.join(
                b'100644 ' + blob + b' ' + str(stage).encode() + b'\tdocs/adr/a.md\n'
                for stage in (1, 2, 3)))
        elif case == 'bytes':
            blob = git('hash-object', '-w', '--stdin', data=b'Fixture\n').strip()
            # The index carries bytes even on a platform unable to materialize
            # the filename. Both readers must preserve the same failure outcome.
            git('update-index', '-z', '--index-info',
                data=b'100644 ' + blob + b'\tdocs/adr/raw\xe9.md\0')
    return [parent / case for case in CASES]
