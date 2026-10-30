"""Synthetic stdin-JSON controls for the ADR 0439 subagent write fence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from repo_root import scratch_path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / 'tools/subagent_write_hook.py'


class SubagentWrites(unittest.TestCase):
    def setUp(self):
        sessions = scratch_path(ROOT / 'scratch', 'sessions')
        sessions.mkdir(parents=True, exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix='write-guard-test-', dir=sessions)
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.stage = self.folder / 'stage'
        self.stage.mkdir()
        self.parent = self.folder / 'parent.jsonl'
        self.brief_path = self.parent.with_suffix('') / 'subagents/agent-synthetic.jsonl'
        self.brief_path.parent.mkdir(parents=True)
        self.brief(f'Read output/synthetic/; stage only in `{self.stage}`. SYNTHETIC-BRIEF-CANARY')

    def brief(self, text):
        self.brief_path.write_text(json.dumps({'type': 'user', 'message': {'content': text}}) + '\n',
                                   encoding='utf-8')

    def response(self, tool, inputs, **extra):
        payload = {'tool_name': tool, 'tool_input': inputs, 'cwd': str(ROOT),
                   'transcript_path': str(self.parent), 'agent_id': 'synthetic', **extra}
        result = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                                capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('', result.stderr)
        self.assertNotIn('SYNTHETIC-BRIEF-CANARY', result.stdout)
        self.assertNotIn(str(self.stage), result.stdout)
        return json.loads(result.stdout)

    def assert_denied(self, response):
        specific = response['hookSpecificOutput']
        self.assertEqual('deny', specific['permissionDecision'])
        self.assertIn('report', specific['permissionDecisionReason'].lower())

    def test_file_writes_are_fenced_to_the_briefs_staging_folder(self):
        for tool, field in [('Write', 'file_path'), ('Edit', 'file_path'), ('NotebookEdit', 'notebook_path')]:
            with self.subTest(tool=tool):
                self.assertEqual({}, self.response(tool, {field: str(self.stage / 'inside.md')}))
                self.assert_denied(self.response(tool, {field: str(self.folder / 'outside.md')}))

    def test_unreadable_brief_refuses_private_targets_and_warns_on_other_writes(self):
        self.brief_path.unlink()
        self.assert_denied(self.response('Write', {'file_path': str(self.folder / 'outside.md')}))
        response = self.response('Write', {'file_path': str(ROOT / 'tools/synthetic.py')})
        specific = response['hookSpecificOutput']
        self.assertNotIn('permissionDecision', specific)
        self.assertIn('brief', specific['additionalContext'])
        self.assertEqual(specific['additionalContext'], response['systemMessage'])

    def test_shell_redirections_and_heredocs_use_the_same_fence(self):
        for tool in ('Bash', 'Monitor'):
            for template in ("echo fixture > '{path}'", "echo fixture >> '{path}'",
                             "cat > '{path}' <<'END'\nfixture\nEND",
                             "tee '{path}' <<'END'\nfixture\nEND",
                             "tee <<'END' '{path}'\nfixture\nEND",
                             "cat > '{path}' <<-'END'\n\tfixture\n\tEND",
                             "python - <<'END'\nopen({path!r}, 'w').write('fixture')\nEND"):
                with self.subTest(tool=tool, template=template):
                    inside = template.format(path=str(self.stage / 'inside.md'))
                    outside = template.format(path=str(self.folder / 'outside.md'))
                    self.assertEqual({}, self.response(tool, {'command': inside}))
                    self.assert_denied(self.response(tool, {'command': outside}))

    def test_bound_shell_writes_need_literal_targets(self):
        for command in ('echo fixture > "$DEST"', 'echo fixture > *.md',
                        'echo fixture > "$(pwd)/file.md"'):
            with self.subTest(command=command):
                response = self.response('Bash', {'command': command})
                self.assert_denied(response)
                self.assertIn('literal', response['hookSpecificOutput']['permissionDecisionReason'])

    def test_main_no_staging_and_read_calls_pass_untouched(self):
        self.assertEqual({}, self.response('Write', {'file_path': str(self.folder / 'outside.md')}, agent_id=None))
        self.assertEqual({}, self.response('Read', {'file_path': str(self.folder / 'outside.md')}))
        self.assertEqual({}, self.response('Bash', {'command': 'cat output/synthetic.md'}))
        self.assertEqual({}, self.response('Bash', {'command': "python - <<'END'\nopen(target, 'r').read()\nEND"}))
        self.brief('Read tools/synthetic.py; this code pass names no staging folder.')
        self.assertEqual({}, self.response('Write', {'file_path': str(self.folder / 'outside.md')}))
        self.assertEqual({}, self.response('Bash', {'command': 'echo fixture > "$DEST"'}))

    def test_shell_paths_follow_each_completed_literal_cd(self):
        self.assertEqual({}, self.response('Bash', {'command': f"cd '{self.stage}' && echo fixture > inside.md"}))
        self.assert_denied(self.response('Bash', {'command':
            f"cd '{self.stage}' && echo fixture > inside.md; cd '{self.folder}' && echo fixture > outside.md"}))
        self.assert_denied(self.response('Bash', {'command': 'cd "$DEST" && echo fixture > inside.md'}))

    def test_brief_is_reread_and_literal_relative_staging_uses_payload_cwd(self):
        relative = self.stage.relative_to(ROOT)
        self.brief(f'Read output/synthetic/; stage in `{relative}`.')
        self.assertEqual({}, self.response('Write', {'file_path': str(self.stage / 'inside.md')}))
        other = self.folder / 'other-stage'
        other.mkdir()
        self.brief(f'Read output/synthetic/; stage in `{other}`.')
        self.assert_denied(self.response('Write', {'file_path': str(self.stage / 'inside.md')}))
        self.assertEqual({}, self.response('Write', {'file_path': str(other / 'inside.md')}))

    def test_symlinks_and_parent_paths_cannot_escape_the_stage(self):
        self.assert_denied(self.response('Write', {'file_path': str(self.stage / '../outside.md')}))
        link = self.stage / 'link'
        try:
            link.symlink_to(self.folder, target_is_directory=True)
        except OSError:
            self.skipTest('directory symlinks unavailable')
        self.assert_denied(self.response('Write', {'file_path': str(link / 'outside.md')}))

    def test_malformed_first_rows_use_fixed_content_free_failure_reasons(self):
        for text in ('{SYNTHETIC-BRIEF-CANARY', '[]',
                     json.dumps({'type': 'assistant', 'message': {'content': 'SYNTHETIC-BRIEF-CANARY'}}),
                     json.dumps({'type': 'user', 'message': {'content': ['SYNTHETIC-BRIEF-CANARY']}})):
            with self.subTest(text=text):
                self.brief_path.write_text(text + '\n', encoding='utf-8')
                self.assert_denied(self.response('Write', {'file_path': str(self.folder / 'outside.md')}))
                response = self.response('Write', {'file_path': str(ROOT / 'tools/synthetic.py')})
                self.assertNotIn('permissionDecision', response['hookSpecificOutput'])

    def test_unreadable_brief_shell_targets_are_selective(self):
        self.brief_path.unlink()
        for path in (self.folder / 'outside.md', ROOT / 'output/synthetic.md',
                     Path(tempfile.gettempdir()) / 'synthetic-write.md'):
            with self.subTest(path=path):
                self.assert_denied(self.response('Bash', {'command': f"echo fixture > '{path}'"}))
        response = self.response('Bash', {'command': f"echo fixture > '{ROOT / 'tools/synthetic.py'}'"})
        self.assertNotIn('permissionDecision', response['hookSpecificOutput'])

    def test_unreadable_file_targets_refuse_without_a_traceback_or_content_echo(self):
        for value in (None, [], '', 'SYNTHETIC-TARGET-CANARY\0'):
            with self.subTest(value=value):
                response = self.response('Write', {'file_path': value})
                self.assert_denied(response)
                self.assertNotIn('SYNTHETIC-TARGET-CANARY', json.dumps(response))

    def test_raw_payload_denial_asks_for_reporting(self):
        result = subprocess.run([sys.executable, str(HOOK)],
            input='agent_id scratch/sessions/synthetic/', capture_output=True,
            text=True, encoding='utf-8', errors='replace')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_denied(json.loads(result.stdout))

    def test_multiline_quoted_no_write_command_passes(self):
        for command in ("printf '%s\\n' 'hello\nworld'",
                        "printf '%s\\n' 'hello > output/synthetic.md\nworld'"):
            with self.subTest(command=command):
                self.assertEqual({}, self.response('Bash', {'command': command}))

    def test_quoted_and_escaped_operators_are_data(self):
        for command in ("printf '%s\\n' '>' 'output/synthetic.md'",
                        'printf %s \\> output/synthetic.md',
                        "printf '%s\\n' '<<' 'END'\ncat output/synthetic.md"):
            with self.subTest(command=command):
                self.assertEqual({}, self.response('Bash', {'command': command}))
        self.assert_denied(self.response('Bash', {'command': 'echo fixture > output/synthetic.md'}))
        self.assert_denied(self.response('Bash', {'command':
            "printf '%s\\n' '<<' 'END'\necho fixture > output/synthetic.md"}))

    def test_tee_file_descriptors_are_not_confused_with_numeric_file_arguments(self):
        inside = self.stage / 'inside.md'
        errors = self.stage / 'stderr.md'
        self.assertEqual({}, self.response('Bash', {'command': f"tee '{inside}' 2>'{errors}'"}))
        self.assert_denied(self.response('Bash', {'command': f"tee 2 >'{inside}'"}))

    def test_grouped_commands_reach_their_redirection_and_tee_targets(self):
        inside, outside = self.stage / 'inside.md', self.folder / 'outside.md'
        for template in ("(echo x)>'{path}'", "(echo x) > '{path}'", "(tee '{path}')", "{{ tee '{path}'; }}"):
            with self.subTest(template=template):
                self.assertEqual({}, self.response('Bash', {'command': template.format(path=inside)}))
                self.assert_denied(self.response('Bash', {'command': template.format(path=outside)}))
        self.assertEqual({}, self.response('Bash', {'command': 'ls a > >(cat)'}))

    def test_bracket_and_brace_expansions_are_unresolvable_targets(self):
        for target in (f"'{self.stage}'/[ab].md", f"'{self.stage}'/{{../../x.md,y.md}}"):
            with self.subTest(target=target):
                response = self.response('Bash', {'command': f'tee {target}'})
                self.assert_denied(response)
                self.assertIn('literal', response['hookSpecificOutput']['permissionDecisionReason'])

    def test_unreadable_brief_judges_the_resolved_target_not_its_spelling(self):
        self.brief_path.unlink()
        temporary = Path(tempfile.gettempdir())
        self.assert_denied(self.response('Write', {'file_path': 'a.md'}, cwd=str(temporary)))
        self.assert_denied(self.response('Bash', {'command': f"cd '{temporary}' && echo x > a.md"}))

    def test_descriptor_duplications_and_null_devices_are_not_file_writes(self):
        for command in ('ls a 2>&1', 'ls a 2>&1 | head -5', 'echo x >&2', 'echo x 1>&2',
                        'ls a 2>/dev/null', 'ls a >/dev/null 2>&1', 'ls a &>/dev/null',
                        'ls a 2> /dev/null; ls b'):
            with self.subTest(command=command):
                self.assertEqual({}, self.response('Bash', {'command': command}))
        self.brief_path.unlink()
        self.assertEqual({}, self.response('Bash', {'command': 'ls a 2>&1'}))

    def test_combined_output_redirections_are_fenced(self):
        for operator in ('&>', '&>>', '>&'):
            with self.subTest(operator=operator):
                inside, outside = self.stage / 'inside.md', self.folder / 'outside.md'
                self.assertEqual({}, self.response('Bash', {'command': f"echo x {operator} '{inside}'"}))
                self.assert_denied(self.response('Bash', {'command': f"echo x {operator} '{outside}'"}))

    @unittest.skipUnless(sys.platform == 'win32', 'Git Bash drive spelling is Windows only')
    def test_git_bash_drive_spelling_names_the_same_path(self):
        def spelled(path):
            text = path.as_posix()
            return f'/{text[0].lower()}/{text[3:]}'
        inside, outside = spelled(self.stage / 'inside.md'), spelled(self.folder / 'outside.md')
        self.assertEqual({}, self.response('Bash', {'command': f"echo x > '{inside}'"}))
        self.assertEqual({}, self.response('Write', {'file_path': inside}))
        self.assert_denied(self.response('Bash', {'command': f"echo x > '{outside}'"}))
        self.brief(f'Read output/synthetic/; stage in `{spelled(self.stage)}`.')
        self.assertEqual({}, self.response('Write', {'file_path': str(self.stage / 'inside.md')}))
        self.brief_path.unlink()
        self.assert_denied(self.response('Bash', {'command': f"echo x > '{spelled(ROOT / 'output/synthetic.md')}'"}))

    def test_a_mention_of_the_namespace_or_a_template_names_no_staging_folder(self):
        target = str(ROOT / 'tools/synthetic.py')
        for mention in ('`scratch/sessions/<key>/<pass-label>/`', 'scratch/sessions/<key>/',
                        'scratch/sessions/', '`scratch/sessions/`', '`scratch/sessions/$KEY/pass/`',
                        '`scratch/sessions/{key}/`'):
            with self.subTest(mention=mention):
                self.brief(f'Review the tools; working material goes under {mention} by convention.')
                self.assertEqual({}, self.response('Write', {'file_path': target}))
        self.brief(f'See `scratch/sessions/<key>/`; stage in `{self.stage}`.')
        self.assert_denied(self.response('Write', {'file_path': target}))
        self.assertEqual({}, self.response('Write', {'file_path': str(self.stage / 'inside.md')}))


class SubagentWriteInstallation(unittest.TestCase):
    def test_hook_is_registered_for_file_tools_and_modeled_shell_tools(self):
        import command_reader
        import re
        settings = json.loads((ROOT / '.claude/settings.json').read_text(encoding='utf-8'))
        entries = [entry for entry in settings['hooks']['PreToolUse'] if any(
            'subagent_write_hook.py' in hook['command'] for hook in entry['hooks'])]
        self.assertEqual(1, len(entries))
        expected = {'Write', 'Edit', 'NotebookEdit'} | {
            name for name, shell in command_reader.COMMAND_TOOLS.items()
            if shell == command_reader.MODELED_SHELL}
        for tool in expected:
            self.assertIsNotNone(re.fullmatch(entries[0]['matcher'], tool), tool)
        self.assertIsNone(re.fullmatch(entries[0]['matcher'], 'Read'))
        self.assertIn('subagent_write_hook.DECLARED_LIMITS', (ROOT / 'CLAUDE.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
