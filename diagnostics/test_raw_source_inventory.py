"""Synthetic real-Git tests. Set RAW_ORACLE_MODULE to the reviewed module path."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import time
import unittest
import zipfile
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = (HERE.parent / 'scratch/sessions'
        if HERE.name == 'diagnostics' else HERE)
ROOT.mkdir(parents=True, exist_ok=True)
if os.environ.get('RAW_ORACLE_MODULE'):
    MODULE = Path(os.environ['RAW_ORACLE_MODULE']).resolve()
    sys.path.insert(0, str(MODULE.parent))
    spec = importlib.util.spec_from_file_location('raw_oracle_under_test', MODULE)
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
else:
    import raw_source_inventory as oracle

class LocalSession:
    def __init__(self, repo, env):
        self.repo, self.env = repo, env
        self.deadline = time.monotonic() + 60
        self.calls = []

    def git_bytes(self, repo, *args):
        if Path(repo).resolve() != self.repo.resolve():
            raise AssertionError('fixture repo boundary exceeded')
        self.calls.append(args)
        return subprocess.check_output(['git', '-C', str(self.repo), *args], env=self.env,
                                       stderr=subprocess.PIPE, timeout=10)

    def git(self, repo, *args):
        return self.git_bytes(repo, *args).decode('utf-8')

class RawSourceInventoryTests(unittest.TestCase):
    def setUp(self):
        self.run = Path(tempfile.mkdtemp(prefix='raw-fixture-', dir=ROOT))
        self.addCleanup(shutil.rmtree, self.run)
        self.repo = self.run / 'repo'
        self.repo.mkdir()
        config = self.run / 'global.gitconfig'
        config.write_text('[core]\n autocrlf = true\n')
        self.session = LocalSession(self.repo, dict(os.environ,
            GIT_CONFIG_GLOBAL=str(config), GIT_CONFIG_NOSYSTEM='1',
            GIT_CONFIG_COUNT='0'))
        self.git('init', '-q')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'user.name', 'Synthetic Fixture')

    def git(self, *args):
        return self.session.git(self.repo, *args)

    def commit(self, files):
        self.files = files
        for name, data in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.git('-c', 'core.autocrlf=false', 'add', '.')
        self.git('-c', 'core.autocrlf=false', 'commit', '-qm', 'Synthetic fixture')
        self.pin = self.git('rev-parse', 'HEAD').strip()
        for name, data in files.items():
            self.assertEqual(self.session.git_bytes(self.repo, 'cat-file', 'blob', self.pin + ':' + name), data)
        return self.pin

    def check(self):
        return oracle.raw_source_inventory(self.session, self.repo, self.pin)

    def test_raw_lf_survives_inherited_autocrlf(self):
        self.commit({'source.txt': b'alpha\nbeta\n', '.gitignore': b'scratch/\n'})
        (self.repo / 'source.txt').unlink()
        self.git('-c', 'core.autocrlf=false', 'checkout', '--', '.')
        self.assertEqual(self.check(), {name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()})
        self.assertFalse(any('archive' in args for args in self.session.calls))

    def test_legacy_archive_conversion_discriminates_raw_from_converted_bytes(self):
        # Archive is a negative fixture only, never the replacement oracle.
        self.commit({'source.txt': b'alpha\nbeta\n', '.gitignore': b'scratch/\n'})
        source = self.repo / 'source.txt'
        source.unlink()
        self.git('-c', 'core.autocrlf=false', 'checkout', '--', 'source.txt')
        raw = self.session.git_bytes(self.repo, 'cat-file', 'blob', self.pin + ':source.txt')
        self.assertEqual(self.git('config', '--get', 'core.autocrlf').strip(), 'true')
        self.assertEqual(source.read_bytes(), raw)
        archive = self.session.git_bytes(self.repo, 'archive', '--format=zip', self.pin)
        with zipfile.ZipFile(io.BytesIO(archive)) as fixture:
            converted = fixture.read('source.txt')
        self.assertEqual(raw, b'alpha\nbeta\n')
        self.assertEqual(converted, b'alpha\r\nbeta\r\n')
        self.assertNotEqual(converted, raw)  # The legacy equality oracle fails here.
        self.assertEqual(self.check(), {
            name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()})
        source.write_bytes(converted)
        with self.assertRaises(oracle.RawIdentityMismatch) as caught:
            self.check()
        self.assertEqual(caught.exception.diagnostics['changed'], 1)

    def test_attributes_do_not_convert_omit_or_substitute_raw_oracle(self):
        self.commit({'.gitattributes': b'crlf.txt text eol=crlf\nlf.txt text eol=lf\nomitted.txt export-ignore\nsubst.txt export-subst\nblob.bin -text\n',
                     'crlf.txt': b'alpha\nbeta\n', 'lf.txt': b'gamma\ndelta\n',
                     'omitted.txt': b'still committed\n', 'subst.txt': b'$Format:%H$\n',
                     'blob.bin': bytes(range(256)) + b'\x00\r\n\xff', '.gitignore': b'scratch/\n'})
        self.assertEqual(self.check(), {name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()})

    def test_actual_converted_checkout_is_rejected_not_normalized(self):
        self.commit({'source.txt': b'alpha\nbeta\n', '.gitignore': b'scratch/\n'})
        (self.repo / 'source.txt').unlink()
        self.git('checkout', '--', '.')
        self.assertEqual((self.repo / 'source.txt').read_bytes(), b'alpha\r\nbeta\r\n')
        with self.assertRaises(oracle.Refused):
            self.check()

    def test_explicit_crlf_checkout_is_rejected_even_with_autocrlf_false(self):
        self.commit({'.gitattributes': b'source.txt text eol=crlf\n',
                     'source.txt': b'alpha\nbeta\n', '.gitignore': b'scratch/\n'})
        (self.repo / 'source.txt').unlink()
        self.git('-c', 'core.autocrlf=false', 'checkout', '--', 'source.txt')
        self.assertEqual((self.repo / 'source.txt').read_bytes(), b'alpha\r\nbeta\r\n')
        with self.assertRaises(oracle.Refused):
            self.check()

    def test_missing_extra_text_and_binary_mutations_have_safe_diagnostics(self):
        self.commit({'.gitignore': b'scratch/\n', 'private-missing.txt': b'SECRET CONTENT\n',
                     'private-changed.txt': b'alpha\n', 'private-binary.bin': b'\x00\xff\r\n'})
        (self.repo / 'private-missing.txt').unlink()
        (self.repo / 'private-extra.txt').write_bytes(b'EXTRA SECRET')
        (self.repo / 'private-changed.txt').write_bytes(b'CHANGED SECRET\n')
        (self.repo / 'private-binary.bin').write_bytes(b'\x00\xfe\r\n')
        with self.assertRaises(oracle.Refused) as caught:
            self.check()
        details = caught.exception.diagnostics
        self.assertEqual((details['missing'], details['extra'], details['changed']), (1, 1, 2))
        self.assertEqual(len(details['entries']), 4)
        self.assertEqual(details['omitted_entries'], 0)
        self.assertFalse(details['raw_paths_disclosed'])
        self.assertFalse(details['raw_contents_disclosed'])
        public = str(caught.exception) + json.dumps(details)
        for raw in ('private-', 'SECRET', 'alpha'):
            self.assertNotIn(raw, public)
        expected = {('missing', 'private-missing.txt'), ('extra', 'private-extra.txt'),
                    ('changed', 'private-changed.txt'), ('changed', 'private-binary.bin')}
        self.assertEqual({(row['category'], row['path_token']) for row in details['entries']},
                         {(category, hashlib.sha256(name.encode()).hexdigest()) for category, name in expected})

    def test_diagnostics_cap_and_counts_survive_many_discrepancies(self):
        files = {'.gitignore': b'scratch/\n'}
        files.update({f'private-missing-{i}.txt': b'alpha\n' for i in range(11)})
        files.update({f'private-changed-{i}.txt': b'alpha\n' for i in range(11)})
        self.commit(files)
        for i in range(11):
            (self.repo / f'private-missing-{i}.txt').unlink()
            (self.repo / f'private-changed-{i}.txt').write_bytes(b'CHANGED SECRET\n')
            (self.repo / f'private-extra-{i}.txt').write_bytes(b'EXTRA SECRET\n')
        with self.assertRaises(oracle.Refused) as caught:
            self.check()
        details = caught.exception.diagnostics
        self.assertEqual((details['missing'], details['extra'], details['changed']), (11, 11, 11))
        self.assertLessEqual(len(details['entries']), 8)
        self.assertEqual(details['omitted_entries'], 33 - len(details['entries']))
        public = str(caught.exception) + json.dumps(details)
        self.assertNotIn('private-', public)
        self.assertNotIn('SECRET', public)
        self.assertLess(len(public), 2000)

    def test_unsupported_object_format_refused(self):
        self.commit({'.gitignore': b'scratch/\n'})
        with mock.patch.object(self.session, 'git', return_value='sha512\n'):
            with self.assertRaises(oracle.Refused):
                self.check()

    def test_committed_symlink_tree_refused(self):
        self.commit({'.gitignore': b'scratch/\n', 'target.txt': b'alpha\n'})
        (self.repo / 'synthetic-link').symlink_to('target.txt')
        self.git('-c', 'core.autocrlf=false', 'add', 'synthetic-link')
        self.git('-c', 'core.autocrlf=false', 'commit', '-qm', 'Synthetic symlink')
        self.pin = self.git('rev-parse', 'HEAD').strip()
        with self.assertRaises(oracle.Refused):
            self.check()

    def test_malformed_tree_outputs_refused_without_raw_leaks(self):
        self.commit({'.gitignore': b'scratch/\n'})
        oid = b'a' * 40
        good = b'100644 blob ' + oid + b'\t.gitignore\0'
        bad_rows = (b'', good[:-1], b'PRIVATE SECRET\0',
                    b'100644 blob BAD\tprivate-name\0',
                    good + good, good + b'100644 blob ' + oid + b'\t../private-name\0',
                    good + b'100644 blob ' + oid + b'\t\xff\0')
        original = self.session.git_bytes
        for payload in bad_rows:
            with self.subTest(payload_sha256=hashlib.sha256(payload).hexdigest()):
                def intercept(repo, *args):
                    return payload if 'ls-tree' in args else original(repo, *args)
                with mock.patch.object(self.session, 'git_bytes', side_effect=intercept):
                    with self.assertRaises(oracle.Refused) as caught:
                        self.check()
                self.assertNotIn('PRIVATE', str(caught.exception))
                self.assertNotIn('private-name', str(caught.exception))

    def test_sha256_object_format_real_git(self):
        # Reinitialize this empty fixture before its first commit with SHA-256.
        other = self.run / 'sha256-repo'
        other.mkdir()
        self.repo = other
        self.session.repo = other
        self.git('init', '-q', '--object-format=sha256')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'user.name', 'Synthetic Fixture')
        self.commit({'.gitignore': b'scratch/\n', 'blob.bin': b'\x00\xff\n'})
        self.assertEqual(len(self.pin), 64)
        self.assertEqual(self.check(), {name: hashlib.sha256(data).hexdigest() for name, data in self.files.items()})

if __name__ == '__main__':
    unittest.main(verbosity=2)
