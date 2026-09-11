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
COMPREHENSION_SCOPES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _looks_like_patch_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    function = node.func
    if isinstance(function, ast.Name):
        return function.id == "patch"
    if not isinstance(function, ast.Attribute):
        return False
    if function.attr == "patch":
        return isinstance(function.value, ast.Name) and function.value.id == "mock"
    return (
        function.attr == "object"
        and (
            isinstance(function.value, ast.Name)
            and function.value.id == "patch"
            or isinstance(function.value, ast.Attribute)
            and function.value.attr == "patch"
            and isinstance(function.value.value, ast.Name)
            and function.value.value.id == "mock"
        )
    )


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


def _scope_bindings(scope: ast.AST) -> dict[str, set[str]]:
    bindings: dict[str, set[str]] = {}

    def bind(name: str, kind: str) -> None:
        bindings.setdefault(name, set()).add(kind)

    class BindingCollector(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                name = alias.asname or alias.name.split(".", 1)[0]
                bind(name, "git_paths_module" if alias.name == "git_paths" else "other")

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            for alias in node.names:
                name = alias.asname or alias.name
                if node.module == "git_paths" and alias.name == "read_path_records":
                    kind = "read_path_records"
                elif node.module == "unittest" and alias.name == "mock":
                    kind = "unittest_mock_module"
                elif node.module == "unittest.mock" and alias.name == "patch":
                    kind = "mock_patch"
                else:
                    kind = "other"
                bind(name, kind)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Store):
                bind(node.id, "other")

        def visit_arg(self, node: ast.arg) -> None:
            bind(node.arg, "other")

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node is scope:
                self.visit(node.args)
                for statement in node.body:
                    self.visit(statement)
            else:
                bind(node.name, "other")

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Lambda(self, node: ast.Lambda) -> None:
            if node is scope:
                self.visit(node.args)
                self.visit(node.body)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            if node is scope:
                for statement in node.body:
                    self.visit(statement)
            else:
                bind(node.name, "other")

        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
            if node.name:
                bind(node.name, "other")
            for statement in node.body:
                self.visit(statement)

        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                self.visit(item.context_expr)
                if isinstance(item.optional_vars, ast.Name) and _looks_like_patch_call(
                    item.context_expr
                ):
                    bind(item.optional_vars.id, "mock_object")
                elif item.optional_vars is not None:
                    self.visit(item.optional_vars)
            for statement in node.body:
                self.visit(statement)

        visit_AsyncWith = visit_With

        def _visit_comprehension_scope(self, node: ast.AST) -> None:
            if node is scope:
                for generator in node.generators:
                    self.visit(generator.target)

        visit_ListComp = _visit_comprehension_scope
        visit_SetComp = _visit_comprehension_scope
        visit_DictComp = _visit_comprehension_scope
        visit_GeneratorExp = _visit_comprehension_scope

    collector = BindingCollector()
    if isinstance(scope, ast.Module):
        for statement in scope.body:
            collector.visit(statement)
    else:
        collector.visit(scope)
    return bindings


def _resolves_to_import(
    name: str,
    kind: str,
    call: ast.Call,
    parents: dict[ast.AST, ast.AST],
    binding_cache: dict[ast.AST, dict[str, set[str]]],
) -> bool:
    node: ast.AST | None = call
    inside_function = False
    while node is not None:
        is_function = isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        )
        is_visible_class = isinstance(node, ast.ClassDef) and not inside_function
        if is_function:
            inside_function = True
        if isinstance(node, (ast.Module, *COMPREHENSION_SCOPES)) or is_function or is_visible_class:
            bindings = binding_cache.setdefault(node, _scope_bindings(node))
            if name in bindings:
                return bindings[name] == {kind}
        node = parents.get(node)
    return False


def _is_mock_expectation(
    call: ast.Call,
    parents: dict[ast.AST, ast.AST],
    binding_cache: dict[ast.AST, dict[str, set[str]]],
) -> bool:
    if (
        isinstance(call.func, ast.Attribute)
        and call.func.attr in MOCK_EXPECTATION_METHODS
        and isinstance(call.func.value, ast.Name)
        and _resolves_to_import(
            call.func.value.id,
            "mock_object",
            call,
            parents,
            binding_cache,
        )
    ):
        return True
    is_mock_call = (
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.attr == "call"
        and _resolves_to_import(
            call.func.value.id,
            "unittest_mock_module",
            call,
            parents,
            binding_cache,
        )
    )
    if not is_mock_call:
        return False
    node: ast.AST | None = parents.get(call)
    while node is not None:
        if isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"assert_has_calls", "assert_has_awaits"}
            and isinstance(node.func.value, ast.Name)
            and _resolves_to_import(
                node.func.value.id,
                "mock_object",
                node,
                parents,
                binding_cache,
            )
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
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        binding_cache: dict[ast.AST, dict[str, set[str]]] = {}
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            literals = _literal_arguments(call)
            path_listing = bool(
                literals & {"ls-files", "ls-tree"}
                or ("diff" in literals and literals & {"--name-only", "--numstat"})
                or ("rev-list" in literals and "--objects" in literals)
            )
            function = call.func
            uses_shared_reader = (
                isinstance(function, ast.Name)
                and _resolves_to_import(
                    function.id,
                    "read_path_records",
                    call,
                    parents,
                    binding_cache,
                )
            ) or (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.attr == "read_path_records"
                and _resolves_to_import(
                    function.value.id,
                    "git_paths_module",
                    call,
                    parents,
                    binding_cache,
                )
            )
            if (
                path_listing
                and not uses_shared_reader
                and not _is_mock_expectation(call, parents, binding_cache)
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
with mock.patch("target") as run, mock.patch("other") as read:
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

    def test_python_scope_boundaries_do_not_bless_or_refuse_aliases(self):
        source = """\
import git_paths as paths

def comprehension_target_is_its_own_scope():
    [item for paths in items]
    return paths.read_path_records(ROOT, "ls-files", "-z")

def exception_alias_shadows_the_import():
    try:
        pass
    except Exception as paths:
        paths.read_path_records(ROOT, "ls-files", "-z")

class ClassBody:
    import git_paths as local_paths
    records = local_paths.read_path_records(ROOT, "ls-files", "-z")
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), ["test_reader.py:11"])

    def test_a_mock_named_method_on_an_ordinary_receiver_is_not_suppressed(self):
        source = 'probe.assert_called_with(["git", "ls-files"])\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), ["test_reader.py:1"])

    def test_an_alias_imported_in_another_scope_is_not_adoption(self):
        source = """\
def compliant():
    import git_paths as paths
    paths.read_path_records(ROOT, "ls-files", "-z")

def offender(paths):
    paths.read_path_records(ROOT, "ls-files", "-z")
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "test_reader.py").write_text(source, encoding="utf-8")

            self.assertEqual(shared_reader_offenders(root), ["test_reader.py:6"])


if __name__ == "__main__":
    unittest.main()
