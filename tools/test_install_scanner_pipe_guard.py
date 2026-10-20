"""Codex mechanical-hook installation preserves unrelated user content."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import install_scanner_pipe_guard as installer


class ScannerPipeInstallerTests(unittest.TestCase):
    def test_install_is_repeatable_and_preserves_hooks_and_other_rules(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            codex = home / '.codex'
            codex.mkdir()
            agents = codex / 'AGENTS.md'
            agents.write_text('Other instructions.\n', encoding='utf-8')
            original_agents = agents.read_bytes()
            hooks = codex / 'hooks.json'
            hooks.write_bytes(b'{"hooks":{"Stop":[]}}\r\n')
            installer.install(home=home, source_root=installer.SOURCE_ROOT,
                              owning_checkout=installer.SOURCE_ROOT)
            first = agents.read_bytes()
            installed_hooks = hooks.read_bytes()
            installer.install(home=home, source_root=installer.SOURCE_ROOT,
                              owning_checkout=installer.SOURCE_ROOT)
            self.assertEqual(agents.read_bytes(), first)
            self.assertEqual(first, original_agents)
            self.assertEqual(hooks.read_bytes(), installed_hooks)
            document = json.loads(installed_hooks)
            self.assertEqual(document['hooks']['Stop'], [])
            self.assertEqual(len(document['hooks']['PreToolUse']), 1)
            self.assertIn('scanner_pipe_hook.py', document['hooks']['PreToolUse'][0]['hooks'][0]['command'])

    def test_refresh_preserves_other_handlers_in_same_registration(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            path = home / '.codex' / 'hooks.json'
            path.parent.mkdir()
            other = {'type': 'command', 'command': 'other-guard'}
            document = {'custom': 'keep', 'hooks': {'PreToolUse': [
                {'matcher': 'Bash', 'hooks': [other, {'command': 'python old/scanner_pipe_hook.py'}]},
            ], 'Stop': [{'hooks': [other]}]}}
            path.write_text(json.dumps(document), encoding='utf-8')
            installer.install(home=home, source_root=installer.SOURCE_ROOT,
                              owning_checkout=installer.SOURCE_ROOT)
            result = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(result['custom'], 'keep')
            self.assertEqual(result['hooks']['Stop'], document['hooks']['Stop'])
            self.assertEqual(result['hooks']['PreToolUse'][0], {'matcher': 'Bash', 'hooks': [other]})

    def test_drift_refuses_before_touching_user_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(OSError):
                installer.install(home=root, source_root=installer.SOURCE_ROOT,
                                  owning_checkout=root)
            self.assertFalse((root / '.codex').exists())


    def test_refresh_keeps_every_pretooluse_hook_at_its_trust_key_position(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            path = home / '.codex' / 'hooks.json'
            path.parent.mkdir()
            first = {'matcher': 'Bash', 'hooks': [{'command': 'first-guard'}]}
            stale = {'matcher': 'Bash|Monitor',
                     'hooks': [{'command': 'python old/scanner_pipe_hook.py'}]}
            last = {'matcher': 'Bash', 'hooks': [{'command': 'last-guard'}]}
            path.write_text(json.dumps({'hooks': {'PreToolUse': [first, stale, last]}}),
                            encoding='utf-8')
            installer.install(home=home, source_root=installer.SOURCE_ROOT,
                              owning_checkout=installer.SOURCE_ROOT)
            result = json.loads(path.read_text(encoding='utf-8'))['hooks']['PreToolUse']
            self.assertEqual([result[0], result[2]], [first, last])
            self.assertNotIn('old/', result[1]['hooks'][0]['command'])
            self.assertEqual(len(result), 3)

    def test_an_argument_never_installs(self):
        for argument, status in (('--help', 0), ('--dry-run', 2)):
            with self.subTest(argument=argument):
                with mock.patch.object(installer, 'install') as install:
                    with mock.patch('sys.stdout'), mock.patch('sys.stderr'):
                        with self.assertRaises(SystemExit) as stopped:
                            installer.main([argument])
                self.assertEqual(stopped.exception.code, status)
                install.assert_not_called()

if __name__ == '__main__':
    unittest.main()
