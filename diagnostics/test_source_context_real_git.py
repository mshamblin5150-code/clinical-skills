"""Real local Git preparation regression; no owner or hosted qualification claim."""
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock
import measure_maintainer_pair as m

class LocalSession:
    def __init__(self):
        self.deadline = time.monotonic() + 60
        self.first_status = []
    def run(self, argv, cwd):
        result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=15)
        return {'returncode': result.returncode, 'stdout': result.stdout.decode(), 'stderr':result.stderr.decode()}
    def git_bytes(self, repo, *args):
        result = subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.PIPE, timeout=15)
        if args[0]=='status':
            self.first_status.append((repo.name, args, result, (repo/m.q.SUITE_PATH).read_bytes()))
        return result
    def git(self, repo, *args):
        return self.git_bytes(repo, *args).decode()

class RealSourceContext(unittest.TestCase):
    def test_ancestry_refs_first_status_and_only_candidate_delta(self):
        with tempfile.TemporaryDirectory(prefix='context-local-') as directory:
            root=Path(directory); seed=root/'seed'; seed.mkdir(); session=LocalSession()
            session.git(seed,'init','-b','main')
            session.git(seed,'config','user.name','Synthetic Fixture')
            session.git(seed,'config','user.email','fixture@example.invalid')
            module='tools/test_suite_ids.py'; (seed/'tools').mkdir()
            original=b'VALUE = "original"\n'; candidate=b'VALUE = "lazy"\n'
            (seed/module).write_bytes(original)
            session.git(seed,'add','.'); session.git(seed,'commit','-m','synthetic ancestor')
            ancestor=session.git(seed,'rev-parse','HEAD').strip()
            (seed/'README.md').write_bytes(b'synthetic source\n')
            session.git(seed,'add','.'); session.git(seed,'commit','-m','synthetic pinned source')
            base=session.git(seed,'rev-parse','HEAD').strip(); expected=m.q.inventory(seed)
            session.git(seed,'tag','source-tag')
            (seed/'later.txt').write_bytes(b'not in frozen source\n')
            session.git(seed,'add','.'); session.git(seed,'commit','-m','synthetic later tip')
            source_refs=session.git(seed,'for-each-ref','--format=%(refname) %(objectname)')
            source_head=session.git(seed,'rev-parse','HEAD')
            source_inventory=m.q.inventory(seed)
            with mock.patch.object(m.q,'BASE',base), mock.patch.object(m.q,'SUITE_PATH',module):
                for variant in ('baseline','candidate'):
                    repo=root/variant
                    target=m.source_context(session,seed,repo,variant,expected,candidate)
                    m.verify_refs(session,repo)
                    self.assertEqual(session.git(repo,'rev-list','HEAD').splitlines(),[base,ancestor])
                    self.assertEqual(session.git(repo,'show',ancestor+':'+module).encode(),original)
                    self.assertEqual(session.git(repo,'ls-files').splitlines(),sorted(expected))
                    self.assertEqual(session.git(repo,'diff','--cached','--name-only'),'')
                    self.assertEqual(session.git(repo,'diff','--name-only','HEAD').splitlines(),[module] if variant=='candidate' else [])
                    self.assertEqual(m.q.inventory(repo),target)
                    self.assertEqual((repo/module).read_bytes(),candidate if variant=='candidate' else original)
                    session.git(repo,'update-ref','refs/tags/unexpected',base)
                    with self.assertRaisesRegex(m.q.Refused,'source_refs_changed'): m.verify_refs(session,repo)
                    session.git(repo,'update-ref','-d','refs/tags/unexpected')
                    m.verify_refs(session,repo)
                self.assertEqual(session.first_status,[
                    (variant,('status','--porcelain=v1','--untracked-files=all'),b'',original)
                    for variant in ('baseline','candidate')])
                shallow=root/'shallow'
                subprocess.run(['git','clone','--quiet','--depth=1',seed.as_uri(),str(shallow)],check=True,capture_output=True,timeout=15)
                with self.assertRaisesRegex(m.q.Refused,'source_history_shallow'): m.verify_refs(session,shallow)
            self.assertEqual(session.git(seed,'for-each-ref','--format=%(refname) %(objectname)'),source_refs)
            self.assertEqual(session.git(seed,'rev-parse','HEAD'),source_head)
            self.assertEqual(m.q.inventory(seed),source_inventory)

if __name__=='__main__': unittest.main()
