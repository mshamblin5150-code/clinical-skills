"""Codex mechanical-hook installation preserves unrelated user content."""
import json
from pathlib import Path
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main()
