"""Drive the heredoc guard through its public stdin JSON boundary."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HOOK = Path(__file__).with_name("heredoc_write_hook.py")


class HeredocWrites(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.checkout = Path(self.folder.name) / "checkout"
        self.checkout.mkdir()
        (self.checkout / ".git").mkdir()

    def response(self, command, tool="Bash", cwd=None):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"tool_name": tool, "cwd": str(cwd or self.checkout),
                             "tool_input": {"command": command}}),
            text=True, capture_output=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_refuses_redirect_into_scratch(self):
        path = (self.checkout / "scratch/runs/x/note-1.md").as_posix()
        response = self.response(f"cat > '{path}' <<'EOF'\nfixture\nEOF")
        output = response["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("Write tool", output["permissionDecisionReason"])
        self.assertIn("standing rule 6", output["permissionDecisionReason"])

    def test_refuses_append_and_tee_in_either_private_root(self):
        for root in ("scratch", "output"):
            path = (self.checkout / root / "note-1.md").as_posix()
            for header in (f"cat >> '{path}' <<'EOF'", f"tee '{path}' <<'EOF'",
                           f"cat <<'EOF' | tee -a '{path}'"):
                with self.subTest(header=header):
                    response = self.response(header + "\nfixture\nEOF")
                    self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_refuses_literal_python_file_writes(self):
        path = (self.checkout / "scratch/runs/x/note-1.md").as_posix()
        bodies = (f"open({path!r}, 'w').write('fixture')",
                  f"from pathlib import Path\nPath({path!r}).write_text('fixture')",
                  "from pathlib import Path\np = Path('output/note-1.md')\np.write_bytes(b'fixture')")
        for body in bodies:
            with self.subTest(body=body):
                response = self.response("python - <<'PY'\n" + body + "\nPY")
                self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_allows_commit_message_and_tracked_file_splice(self):
        for command in (
            'git commit -m "$(cat <<\'EOF\'\nmessage\nEOF\n)"',
            "cat > tools/fixture.py <<'EOF'\nfixture\nEOF",
            "python - <<'PY'\nfrom pathlib import Path\nPath('tools/fixture.py').write_text('fixture')\nPY",
            "python - <<'PY'\nopen('scratch/fixture.md', 'r').read()\nPY",
            "cat <<'EOF'\ncat > scratch/fixture.md <<'OTHER'\nEOF",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.response(command), {})

    def test_refuses_relative_writes_after_literal_cd_and_in_a_worktree(self):
        worktree = Path(self.folder.name) / "worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: ../checkout/.git/worktrees/test\n", encoding="utf-8")
        command = f"cd '{worktree.as_posix()}' && cat > output/note-1.md <<'EOF'\nfixture\nEOF"
        response = self.response(command, cwd=Path(self.folder.name))
        self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unresolved_path_and_powershell_are_reported_unread(self):
        for command, tool in (("cat > \"$DEST\" <<'EOF'\nfixture\nEOF", "Bash"),
                              ("cat > scratch/note.md <<'EOF\nfixture\nEOF", "Bash"),
                              ("cd $DEST && cat > scratch/note.md <<'EOF'\nfixture\nEOF", "Bash"),
                              ("python - <<'PY'\nopen(\nPY", "Bash"),
                              ("python - <<'PY'\nopen(target, 'w')\nPY", "Bash"),
                              ("@'\nfixture\n'@ | Set-Content scratch/note-1.md", "PowerShell")):
            with self.subTest(tool=tool):
                output = self.response(command, tool)["hookSpecificOutput"]
                self.assertNotIn("permissionDecision", output)
                self.assertIn("unread", output["additionalContext"])


if __name__ == "__main__":
    unittest.main()
