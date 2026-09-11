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

MOCK_EXPECTATION_METHODS = {
    "assert_any_call",
    "assert_any_await",
    "assert_called",
    "assert_called_once",
    "assert_called_once_with",
    "assert_called_with",
    "assert_has_calls",
    "assert_has_awaits",
    "assert_awaited",
    "assert_awaited_once",
    "assert_awaited_once_with",
    "assert_awaited_with",
    "assert_not_awaited",
    "assert_not_called",
}


def _literal_arguments(call: ast.Call) -> set[str]:
    values: set[str] = set()

    class DirectStringLiteralCollector(ast.NodeVisitor):
        def visit_Constant(self, node: ast.Constant) -> None:
            if isinstance(node.value, str):
                values.add(node.value)

        def visit_Call(self, node: ast.Call) -> None:
            return

    reader = DirectStringLiteralCollector()
    for argument in call.args:
        reader.visit(argument)
    for keyword in call.keywords:
        reader.visit(keyword.value)
    return values


def _git_paths_imports(tree: ast.Module) -> tuple[set[str], set[str]]:
    modules: set[str] = set()
    readers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "git_paths":
                    modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "git_paths":
            for alias in node.names:
                if alias.name == "read_path_records":
                    readers.add(alias.asname or alias.name)
    return modules, readers


def _is_mock_expectation(
    call: ast.Call, parents: dict[ast.AST, ast.AST]
) -> bool:
    if (
        isinstance(call.func, ast.Attribute)
        and call.func.attr in MOCK_EXPECTATION_METHODS
    ):
        return True
    is_mock_call = (
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "mock"
        and call.func.attr == "call"
    )
    if not is_mock_call:
        return False
    node: ast.AST | None = parents.get(call)
    while node is not None:
        if isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"assert_has_calls", "assert_has_awaits"}
        ):
            return True
        node = parents.get(node)
    return False


def shared_reader_offenders(root: Path) -> list[str]:
    """Find path-listing Git calls that bypass the lossless shared reader."""
    offenders = []
    for path in sorted(root.glob("*.py")):
        if path.name in {"git_paths.py", "test_git_paths.py"}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules, readers = _git_paths_imports(tree)
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            literals = _literal_arguments(call)
            path_listing = bool(
                literals & {"ls-files", "ls-tree"}
                or ("diff" in literals and literals & {"--name-only", "--numstat"})
                or ("rev-list" in literals and "--objects" in literals)
            )
            function = call.func
            uses_shared_reader = (
                isinstance(function, ast.Name) and function.id in readers
            ) or (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id in modules
                and function.attr == "read_path_records"
            )
            if (
                path_listing
                and not uses_shared_reader
                and not _is_mock_expectation(call, parents)
            ):
                offenders.append(f"{path.name}:{call.lineno}")
    return offenders


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
            cwd=Path("repo"), input=None, capture_output=True, check=False,
        )

    def test_stdin_bytes_are_forwarded_without_text_decoding(self):
        completed = subprocess.CompletedProcess(
            ["git"], 0, stdout=b"raw\xe9.md\0", stderr=b""
        )
        stdin = b"caf\xc3\xa9.md\0raw\xe9.md\0"
        with patch.object(git_paths.subprocess, "run", return_value=completed) as run:
            paths = git_paths.read_path_records(
                Path("repo"), "check-ignore", "--stdin", "-z", stdin=stdin
            )

        self.assertEqual(paths[0].encode("utf-8", errors="surrogateescape"), b"raw\xe9.md")
        run.assert_called_once_with(
            ["git", "check-ignore", "--stdin", "-z"],
            cwd=Path("repo"), input=stdin, capture_output=True, check=False,
        )

    def test_a_failed_git_read_raises(self):
        """The tracked population fails; no untracked path is implied to pass."""
        completed = subprocess.CompletedProcess(["git"], 128, stdout=b"", stderr=b"fatal: no tree")
        with patch.object(git_paths.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(git_paths.GitPathError, "fatal: no tree"):
                git_paths.read_path_records(Path("repo"), "ls-files", "-z")

    def test_an_explicitly_accepted_empty_match_status_returns_no_records(self):
        completed = subprocess.CompletedProcess(["git"], 1, stdout=b"", stderr=b"")
        with patch.object(git_paths.subprocess, "run", return_value=completed):
            paths = git_paths.read_path_records(
                Path("repo"), "check-ignore", "--stdin", "-z",
                stdin=b"visible.md\0", accepted_returncodes=(0, 1),
            )

        self.assertEqual(paths, ())

    def test_text_mode_is_refused(self):
        """A clean index walk covers tracked paths; an untracked path stays outside it."""
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
    """Literal argv floor for tools that list repository paths.

    The walk reads string literals directly from each call. A subcommand built
    at run time or passed through a variable is invisible, so this is a floor
    over the source shapes in the tree rather than proof that no hidden reader
    can exist.
    """

    def test_path_listing_subcommands_only_appear_through_git_paths(self):
        self.assertEqual(shared_reader_offenders(TOOLS), [])

    def test_a_test_module_listing_paths_through_subprocess_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(
                "import subprocess\n"
                "subprocess.run(['git', 'ls-files'])\n",
                encoding="utf-8",
            )

            self.assertEqual(
                shared_reader_offenders(root),
                ["test_reader.py:2"],
            )

    def test_import_aliases_and_mock_expectations_are_not_refused(self):
        source = """\
from unittest import mock
from git_paths import read_path_records as records
import git_paths as paths

records(ROOT, "ls-files", "-z")
paths.read_path_records(ROOT, "ls-tree", "-z")
def local_imports():
    from git_paths import read_path_records as local_records
    import git_paths as local_paths
    local_records(ROOT, "ls-files", "-z")
    local_paths.read_path_records(ROOT, "ls-tree", "-z")
run.assert_any_call(["git", "ls-files"])
run.assert_any_await(["git", "ls-files"])
run.assert_called(["git", "ls-files"])
run.assert_called_once(["git", "ls-files"])
run.assert_called_once_with(["git", "ls-files"])
read.assert_called_with("ls-tree")
run.assert_has_calls([mock.call(["git", "ls-files"])])
run.assert_has_awaits([mock.call(["git", "ls-files"])])
run.assert_awaited(["git", "ls-files"])
run.assert_awaited_once(["git", "ls-files"])
run.assert_awaited_once_with(["git", "ls-files"])
run.assert_awaited_with(["git", "ls-files"])
run.assert_not_awaited(["git", "ls-files"])
run.assert_not_called(["git", "ls-files"])
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), [])

    def test_an_executable_listing_inside_a_mock_expectation_is_still_refused(self):
        source = """\
import subprocess
probe.assert_called_with(subprocess.run(["git", "ls-files"]))
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), ["test_reader.py:2"])

    def test_an_unimported_git_paths_name_is_not_adoption(self):
        source = 'git_paths.read_path_records(ROOT, "ls-files", "-z")\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), ["test_reader.py:1"])


if __name__ == "__main__":
    unittest.main()
