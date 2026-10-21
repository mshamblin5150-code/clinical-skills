"""Synthetic unchanged-hook and empty retained-parent boundaries.

Local controls only; no repository full-suite or Windows qualification claim.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / 'tools'), str(REPO / 'diagnostics')]
import subagent_staging_hook as hook
import measure_maintainer_pair as harness

HOOK_SHA256 = '76ccb56e576163fda9d33d9e7f7ded6aafd1a1dbad3a8c7ad1767db8fc677bed'
OUTSIDE = REPO / 'scratch/sessions'


def make_stage(root):
    stage = root / 'scratch/sessions/synthetic/pass'
    stage.mkdir(parents=True)
    return stage


def brief(stage):
    return {'tool_name': 'Agent', 'tool_input': {'prompt': f'Read output/synthetic/; stage in `{stage}`'}}


class UnchangedHookBoundary(unittest.TestCase):
    def test_frozen_hook_bytes_are_unchanged(self):
        self.assertEqual(hashlib.sha256(Path(hook.__file__).read_bytes()).hexdigest(), HOOK_SHA256)

    def test_same_absolute_registered_route_refused_in_temp_accepted_outside(self):
        before = {name: os.environ.get(name) for name in ('TEMP', 'TMP')}
        actual_temp = tempfile.gettempdir()
        self.assertFalse(hook.names_temp(str(OUTSIDE)), 'Proof directory must be outside actual temp and recognized temp syntax')
        with tempfile.TemporaryDirectory(prefix='synthetic-hook-') as inside, \
             tempfile.TemporaryDirectory(prefix='synthetic-hook-', dir=OUTSIDE) as outside:
            for root, expected_temp in ((Path(inside), True), (Path(outside), False)):
                stage = make_stage(root)
                self.assertEqual(hook.names_temp(str(stage)), expected_temp)
                with mock.patch.object(hook, 'registered_roots', return_value=[root]) as roots:
                    result = hook.handle(brief(stage))
                    if expected_temp:
                        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
                        roots.assert_not_called()  # Temp check happens before registration.
                    else:
                        self.assertEqual(result, {})
                        roots.assert_called_once_with()
        self.assertEqual(tempfile.gettempdir(), actual_temp)
        self.assertEqual({name: os.environ.get(name) for name in before}, before)

    def test_real_git_registered_synthetic_checkout_outside_temp_accepts(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-git-', dir=OUTSIDE) as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            stage = make_stage(root)
            # Real worktree registration; only module ROOT points to our tiny disposable repo.
            with mock.patch.object(hook, 'ROOT', root):
                self.assertEqual(hook.registered_roots(), [root])
                self.assertEqual(hook.handle(brief(stage)), {})


class RetainedFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='retained-synthetic-', dir=OUTSIDE)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'tools').mkdir()
        (self.root / 'tools/a.py').write_bytes(b'pass\n')
        self.target = {'tools/a.py': harness.q.digest(b'pass\n')}
        self.session = mock.Mock(deadline=time.monotonic() + 30)
        # Isolate the retained-output boundary, as existing test_maintainer_pair does.
        for owner, attr in ((harness.q, 'verify_sources'), (harness, 'verify_refs')):
            patcher = mock.patch.object(owner, attr)
            patcher.start()
            self.addCleanup(patcher.stop)

    def guard(self):
        return harness.retained_guard(self.session, self.root, self.target, False)


class RetainedCorrectionControls(RetainedFixture):
    def test_empty_sessions_should_be_allowed_after_correction(self):
        (self.root / 'scratch/sessions').mkdir(parents=True)
        self.assertEqual(self.guard()['allowed_retained_file_count'], 0)
    def test_sessions_contents_and_unread_directory_still_refuse(self):
        sessions=self.root/'scratch/sessions';sessions.mkdir(parents=True)
        (sessions/'unexpected').write_bytes(b'synthetic')
        with self.assertRaisesRegex(harness.q.Refused,'scratch_sessions_not_empty'):
            self.guard()
        (sessions/'unexpected').unlink()
        (sessions/'nested').mkdir()
        with self.assertRaisesRegex(harness.q.Refused,'scratch_sessions_not_empty'):
            self.guard()



if __name__ == '__main__':
    unittest.main()
