"""ADR 0299 controls at the PreToolUse JSON boundary."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ScannerPipeHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'tools').mkdir()
        for name in ('spelling_scan', 'suite', 'tracker_freshness', 'block_scan'):
            (self.root / 'tools' / (name + '.py')).touch()

    def response(self, command, tool='Bash'):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name('scanner_pipe_hook.py'))],
            input=json.dumps({'cwd': str(self.root), 'tool_name': tool,
                              'tool_input': {'command': command}}),
            text=True, capture_output=True, encoding='utf-8',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_whole_pipeline_is_denied_before_execution(self):
        output = self.response('python tools/suite.py 2>&1 | tail -6')
        self.assertEqual(output['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('> <file> 2>&1', output['hookSpecificOutput']['permissionDecisionReason'])

    def test_adr_positive_and_near_miss_controls(self):
        for command in (
            'for s in a b; do python tools/spelling_scan.py | tail -5; echo "exit=$?"; done',
            'python tools/tracker_freshness.py | head -1 && gh issue list',
            'python tools/spelling_scan.py | tail -5 || echo failed',
            'if python tools/spelling_scan.py | grep -q y; then echo yes; fi',
            'while python tools/spelling_scan.py | grep -q y; do echo yes; done',
            'until python tools/spelling_scan.py | grep -q y; do echo yes; done',
            'python tools/spelling_scan.py | tail -5; true; echo "${PIPESTATUS[0]}"',
            'python tools/spelling_scan.py | tail -5; echo "${PIPESTATUS[1]}"',
            'set -o pipefail; python tools/spelling_scan.py | tail -5; echo $?',
            'python tools/spelling_scan.py | tail -5; echo "${PIPESTATUS[0]} $?"',
            'for s in a; do python tools/suite.py | tail; done',
        ):
            with self.subTest(command=command):
                self.assertEqual(self.response(command)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_adr_negative_controls(self):
        for command in (
            'python tools/spelling_scan.py > result.txt 2>&1; echo "exit=$?"',
            'python tools/spelling_scan.py | tail -5; echo "exit=${PIPESTATUS[0]}"',
            'git log | head',
            'gh api repos/example | python -c "print(1)"',
            'python tools/spelling_scan.py; python tools/block_scan.py',
            'python tools/missing.py | tail -5',
            'python tools/spelling_scan.py | tail; echo finished',
            'echo "python tools/spelling_scan.py | tail"',
            'python tools/spelling_scan.py | tail; echo \'$?\'',
            'python tools/spelling_scan.py | tail; echo \'${PIPESTATUS[1]}\'',
            'cat <<\'EOF\'\npython tools/suite.py | tail\nEOF',
            'cat input | python tools/suite.py | tail; echo "${PIPESTATUS[1]}"',
        ):
            with self.subTest(command=command):
                self.assertEqual(self.response(command), {})

    def test_roster_and_existing_path_spellings(self):
        for tool in ('Bash', 'Monitor'):
            for invocation in ('python', 'python3', 'command python', 'env X=y python'):
                command = invocation + ' "./tools/suite.py" | tail'
                with self.subTest(tool=tool, invocation=invocation):
                    self.assertEqual(self.response(command, tool)['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(self.response('python tools/suite.py | tail', 'PowerShell'), {})

    def test_every_scanner_stage_needs_its_own_status(self):
        self.assertEqual(self.response('python tools/suite.py | python tools/block_scan.py | tail; echo "${PIPESTATUS[0]}"')['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(self.response('python tools/suite.py | python tools/block_scan.py | tail; echo "${PIPESTATUS[0]} ${PIPESTATUS[1]}"'), {})


if __name__ == '__main__':
    unittest.main()
