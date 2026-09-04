"""Public-contract tests for lossless Git path readers."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import git_paths


TOOLS = Path(__file__).resolve().parent


class PathRecordReader(unittest.TestCase):
    def test_argv_and_nul_parse_are_pinned(self):
        completed = subprocess.CompletedProcess(
            ["git"], 0, stdout=b"caf\xc3\xa9.md\0raw\xe9.md\0", stderr=b""
        )
        with patch.object(git_paths.subprocess, "run", return_value=completed) as run:
            paths = git_paths.read_path_records(
                Path("repo"), "ls-tree", "-r", "-z", "--name-only", "origin/main"
            )
        self.assertEqual(paths[0], "caf\N{LATIN SMALL LETTER E WITH ACUTE}.md")
        self.assertEqual(paths[1].encode("utf-8", errors="surrogateescape"), b"raw\xe9.md")
        run.assert_called_once_with(
            ["git", "ls-tree", "-r", "-z", "--name-only", "origin/main"],
            cwd=Path("repo"), capture_output=True, check=False,
        )

    def test_a_failed_git_read_raises(self):
        """The tracked population fails; no untracked path is implied to pass."""
        completed = subprocess.CompletedProcess(["git"], 128, stdout=b"", stderr=b"fatal: no tree")
        with patch.object(git_paths.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(git_paths.GitPathError, "fatal: no tree"):
                git_paths.read_path_records(Path("repo"), "ls-files", "-z")

    def test_text_mode_is_refused(self):
        """A tracked walk must be lossless; an untracked path remains outside it."""
        with self.assertRaisesRegex(ValueError, "must request -z"):
            git_paths.read_path_records(Path("repo"), "ls-files")

    def test_rev_list_path_records_bind_to_the_preceding_object(self):
        completed = subprocess.CompletedProcess(
            ["git"], 0,
            stdout=b"a" * 40 + b"\0" + b"b" * 40 + b"\0path=notes/one.md\0",
            stderr=b"",
        )
        with patch.object(git_paths.subprocess, "run", return_value=completed):
            records = git_paths.read_rev_list_objects(Path("repo"), "--all")

        self.assertEqual(records, (("a" * 40, ""), ("b" * 40, "notes/one.md")))


class RealGitPathPopulation(unittest.TestCase):
    def test_distinct_bytes_round_trip_through_a_real_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            blob = subprocess.run(
                ["git", "hash-object", "-w", "--stdin"], cwd=repo,
                input=b"x", capture_output=True, check=True,
            ).stdout.strip()
            names = (
                "caf\N{LATIN SMALL LETTER E WITH ACUTE}.md".encode(),
                b"a b.md",
                b"a%20b.md",
                b"car\rriage.md",
                b"car\nriage.md",
                b"raw\xe9.md",
            )
            tree_input = b"".join(
                b"100644 blob " + blob + b"\t" + name + b"\0" for name in names
            )
            tree = subprocess.run(
                ["git", "mktree", "-z"], cwd=repo, input=tree_input,
                capture_output=True, check=True,
            ).stdout.decode().strip()

            paths = git_paths.read_path_records(
                repo, "ls-tree", "-r", "-z", "--name-only", tree
            )

            self.assertEqual(
                {path.encode("utf-8", errors="surrogateescape") for path in paths},
                set(names),
            )
            self.assertIn("car\rriage.md", paths)
            self.assertIn("car\nriage.md", paths)


class SharedReaderAdoption(unittest.TestCase):
    """Literal argv floor for non-test tools that list repository paths.

    The walk reads string literals directly from each call. A subcommand built
    at run time or passed through a variable is invisible, so this is a floor
    over the source shapes in the tree rather than proof that no hidden reader
    can exist.
    """

    @staticmethod
    def _literal_arguments(call: ast.Call) -> set[str]:
        values: set[str] = set()

        class Direct(ast.NodeVisitor):
            def visit_Constant(self, node: ast.Constant) -> None:
                if isinstance(node.value, str):
                    values.add(node.value)

            def visit_Call(self, node: ast.Call) -> None:
                return

        reader = Direct()
        for argument in call.args:
            reader.visit(argument)
        for keyword in call.keywords:
            reader.visit(keyword.value)
        return values

    def test_path_listing_subcommands_only_appear_through_git_paths(self):
        offenders = []
        for path in sorted(TOOLS.glob("*.py")):
            if path.name.startswith("test_") or path.name == "git_paths.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
                literals = self._literal_arguments(call)
                path_listing = bool(
                    literals & {"ls-files", "ls-tree"}
                    or ("diff" in literals and literals & {"--name-only", "--numstat"})
                    or ("rev-list" in literals and "--objects" in literals)
                )
                function = call.func
                shared = (
                    isinstance(function, ast.Attribute)
                    and isinstance(function.value, ast.Name)
                    and function.value.id == "git_paths"
                )
                if path_listing and not shared:
                    offenders.append(f"{path.name}:{call.lineno}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
