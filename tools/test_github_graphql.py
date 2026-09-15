"""Public-boundary tests for GitHub GraphQL payload verdicts."""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

import github_graphql


TESTDATA = Path(__file__).resolve().parent / "testdata"
TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent


def measured(name: str) -> str:
    return (TESTDATA / name).read_text(encoding="utf-8")


class MeasuredResponsesDecideFromTheirPayload(unittest.TestCase):
    def test_mixed_container_not_found_is_accounted_only_when_declared(self):
        text = measured("github-graphql-mixed-containers.json")
        declared = github_graphql.DeclaredAbsence(
            "NOT_FOUND", ("repository", "issue_18")
        )

        result = github_graphql.read_response(text, (declared,))

        self.assertEqual(result.data["repository"]["pull_18"]["number"], 18)
        self.assertEqual(result.accounted_absences, (declared,))

    def test_issue_or_pull_request_absence_is_accounted(self):
        text = measured("github-graphql-issue-or-pull-request-absent.json")
        declared = github_graphql.DeclaredAbsence(
            "NOT_FOUND", ("repository", "record_999999")
        )

        result = github_graphql.read_response(text, (declared,))

        self.assertIsNone(result.data["repository"]["record_999999"])
        self.assertEqual(result.accounted_absences, (declared,))

    def test_an_untyped_schema_complaint_is_never_declarable(self):
        text = measured("github-graphql-undefined-field.json")
        declared = github_graphql.DeclaredAbsence(
            "undefinedField",
            ("query", "repository", "issue", "fieldThatDoesNotExist"),
        )

        with self.assertRaises(github_graphql.GraphQLResponseError) as raised:
            github_graphql.read_response(text, (declared,))

        self.assertEqual(len(raised.exception.complaints), 1)
        self.assertIn("fieldThatDoesNotExist", str(raised.exception))


class ComplaintMutantsRefuse(unittest.TestCase):
    def response(self, error: dict, record: object = None) -> str:
        return json.dumps({
            "data": {"repository": {"record_17": record}},
            "errors": [error],
        })

    def test_forbidden_on_a_declared_record_alias_refuses(self):
        text = self.response({
            "type": "FORBIDDEN",
            "path": ["repository", "record_17"],
            "message": "Resource not accessible",
        })
        declared = github_graphql.DeclaredAbsence(
            "NOT_FOUND", ("repository", "record_17")
        )

        with self.assertRaises(github_graphql.GraphQLResponseError) as raised:
            github_graphql.read_response(text, (declared,))

        self.assertIn("FORBIDDEN", str(raised.exception))

    def test_nested_not_found_inside_a_present_record_refuses(self):
        text = self.response(
            {
                "type": "NOT_FOUND",
                "path": ["repository", "record_17", "labels"],
                "message": "Labels could not be read",
            },
            {"number": 17, "labels": None},
        )
        declared = github_graphql.DeclaredAbsence(
            "NOT_FOUND", ("repository", "record_17")
        )

        with self.assertRaises(github_graphql.GraphQLResponseError) as raised:
            github_graphql.read_response(text, (declared,))

        self.assertIn("labels", str(raised.exception))


class EnvelopeAndScope(unittest.TestCase):
    def test_a_short_complaint_free_response_passes(self):
        text = json.dumps({"data": {"repository": {"nodes": []}}})

        result = github_graphql.read_response(text)

        self.assertEqual(result.data, {"repository": {"nodes": []}})
        self.assertEqual(result.accounted_absences, ())

    def test_non_json_is_a_typed_reader_error(self):
        with self.assertRaises(github_graphql.GraphQLResponseError):
            github_graphql.read_response("not json")

    def test_every_declared_limit_is_named(self):
        keys = {row.key for row in github_graphql.DECLARED_LIMITS}
        self.assertEqual(keys, {"literal-command-walk", "caller-completeness"})


def _call_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return ""


def _is_graphql_command(call: ast.Call) -> bool:
    arguments = [*call.args, *(keyword.value for keyword in call.keywords)]
    return any(
        isinstance(argument, (ast.List, ast.Tuple))
        and any(
            isinstance(item, ast.Constant) and item.value == "graphql"
            for item in argument.elts
        )
        for argument in arguments
    )


def _reader_imported(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "github_graphql"
        and any(
            alias.name == "read_response"
            and alias.asname in (None, "read_response")
            for alias in node.names
        )
        for node in tree.body
    )


def _reader_is_rebound(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and node.id == "read_response"
            and isinstance(node.ctx, (ast.Store, ast.Del))
        ):
            return True
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == "read_response"
        ):
            return True
        if isinstance(node, ast.arg) and node.arg == "read_response":
            return True
        if isinstance(node, ast.ExceptHandler) and node.name == "read_response":
            return True
        if isinstance(node, ast.MatchAs) and node.name == "read_response":
            return True
        if isinstance(node, ast.Constant) and node.value == "read_response":
            return True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound_name = alias.asname or (
                    alias.name if isinstance(node, ast.ImportFrom)
                    else alias.name.partition(".")[0]
                )
                legitimate = (
                    isinstance(node, ast.ImportFrom)
                    and node.module == "github_graphql"
                    and alias.name == "read_response"
                )
                if bound_name == "read_response" and not legitimate:
                    return True
        if isinstance(node, ast.keyword) and node.arg == "read_response":
            return True
    return False


def _reads_command_result(function: ast.AST, command: ast.Call) -> bool:
    process = _is_subprocess_run(command)
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or _call_name(node) != "read_response":
            continue
        if not node.args:
            continue
        argument = node.args[0]
        if (not process and argument is command) or (
            process
            and isinstance(argument, ast.Attribute)
            and argument.attr == "stdout"
            and argument.value is command
        ):
            return True
    return False


def _is_subprocess_run(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "run"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "subprocess"
    )


def graphql_consumer_failures(
    trees: dict[Path, ast.Module],
) -> tuple[str, ...]:
    failures: list[str] = []
    for path, tree in sorted(trees.items()):
        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        graphql_commands = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and _is_graphql_command(node)
        ]
        if graphql_commands and not _reader_imported(tree):
            failures.append(f"{path.name}: does not import read_response")
        if graphql_commands and _reader_is_rebound(tree):
            failures.append(f"{path.name}: rebinds imported read_response")
        for command in graphql_commands:
            scope = "<module>"
            parent = parents.get(command)
            while parent is not None:
                if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    scope = parent.name
                    break
                parent = parents.get(parent)
            if not _reads_command_result(tree, command):
                failures.append(
                    f"{path.name}:{scope}: GraphQL stdout bypasses read_response"
                )

        declaring_functions = [
            function
            for function in ast.walk(tree)
            if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                isinstance(node, ast.Call) and _call_name(node) == "DeclaredAbsence"
                for node in ast.walk(function)
            )
        ]
        for function in declaring_functions:
            reached = [function]
            helper_names = {
                _call_name(node)
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
            }
            reached.extend(
                helper for name, helper in functions.items() if name in helper_names
            )
            query_text = "\n".join(
                node.value
                for reached_function in reached
                for node in ast.walk(reached_function)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            )
            if re.search(r"\b(?:issue|pullRequest)\s*\(", query_text):
                failures.append(
                    f"{path.name}:{function.name}: declares absence on a container-specific lookup"
                )
    return tuple(failures)


class EveryLiteralGraphqlConsumerUsesTheReader(unittest.TestCase):
    def trees(self) -> dict[Path, ast.Module]:
        return {
            path: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for path in TOOLS.glob("*.py")
            if not path.name.startswith("test_")
        }

    def test_every_literal_graphql_command_routes_stdout_through_the_reader(self):
        self.assertEqual(graphql_consumer_failures(self.trees()), ())

    def test_all_three_ruled_consumers_import_and_call_the_reader(self):
        expected = {
            "implementation_map.py",
            "tracker_publish_hook.py",
            "tracker_population.py",
        }
        trees = self.trees()
        for path, tree in trees.items():
            if path.name not in expected:
                continue
            with self.subTest(module=path.name):
                self.assertTrue(_reader_imported(tree))
                self.assertTrue(any(
                    isinstance(node, ast.Call) and _call_name(node) == "read_response"
                    for node in ast.walk(tree)
                ))
        self.assertEqual({path.name for path in trees} & expected, expected)

    def test_removing_the_reader_from_a_real_consumer_makes_the_walk_fail(self):
        trees = self.trees()
        target = TOOLS / "tracker_publish_hook.py"

        class RemoveReader(ast.NodeTransformer):
            def visit_Call(self, node: ast.Call) -> ast.AST:
                node = self.generic_visit(node)
                if (
                    _call_name(node) == "read_response"
                    and node.args
                    and any(
                        isinstance(candidate, ast.Call)
                        and _is_graphql_command(candidate)
                        for candidate in ast.walk(node.args[0])
                    )
                ):
                    return node.args[0]
                return node

        trees[target] = RemoveReader().visit(trees[target])

        failures = graphql_consumer_failures(trees)

        self.assertTrue(any(
            "tracker_publish_hook.py:fetch_readback" in finding
            for finding in failures
        ))

    def test_a_separated_result_cannot_hide_an_overwrite_before_the_reader(self):
        path = TOOLS / "synthetic_consumer.py"
        source = '''
from github_graphql import read_response

def fetch():
    def overwrite_later():
        completed.stdout = unrelated_result.stdout
    completed = subprocess.run(["gh", "api", "graphql"])
    overwrite_later()
    return read_response(completed.stdout)
'''

        failures = graphql_consumer_failures({path: ast.parse(source)})

        self.assertTrue(any("synthetic_consumer.py:fetch" in row for row in failures))

    def test_keyword_and_module_scope_commands_are_discovered(self):
        cases = {
            "keyword": '''
from github_graphql import read_response
def fetch():
    return subprocess.run(args=["gh", "api", "graphql"])
''',
            "module-scope": '''
from github_graphql import read_response
completed = subprocess.run(["gh", "api", "graphql"])
''',
        }
        for label, source in cases.items():
            with self.subTest(shape=label):
                path = TOOLS / f"synthetic_{label}.py"
                failures = graphql_consumer_failures({path: ast.parse(source)})

                self.assertTrue(any(path.name in row for row in failures))

    def test_the_imported_reader_cannot_be_shadowed_or_rebound(self):
        mutations = {
            "local-definition": '''
from github_graphql import read_response
def fetch():
    def read_response(value):
        return value
    return read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
            "module-definition": '''
from github_graphql import read_response
def read_response(value):
    return value
result = read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
            "assignment": '''
from github_graphql import read_response
read_response = identity
result = read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
            "reflective-assignment": '''
from github_graphql import read_response
setattr(sys.modules[__name__], "read_response", identity)
result = read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
            "second-import": '''
from github_graphql import read_response
from counterfeit import read_response
result = read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
            "keyword-binding": '''
from github_graphql import read_response
globals().update(read_response=identity)
result = read_response(subprocess.run(["gh", "api", "graphql"]).stdout)
''',
        }
        for label, source in mutations.items():
            with self.subTest(mutation=label):
                path = TOOLS / f"synthetic_{label}.py"
                failures = graphql_consumer_failures({path: ast.parse(source)})

                self.assertTrue(any(path.name in row for row in failures))

    def test_no_declared_absence_sits_on_issue_or_pull_request_queries(self):
        failures = graphql_consumer_failures(self.trees())
        self.assertFalse(any("container-specific lookup" in row for row in failures))


class RepositoryProseNamesTheSharedVerdict(unittest.TestCase):
    def test_context_defines_declared_absence(self):
        context = (ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("**Declared absence**:", context)

    def test_each_consumer_section_names_the_reader(self):
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        headings = (
            "### Tracker population",
            "### Tracker publish hook",
            "### Implementation map helper",
        )
        for heading in headings:
            start = claude.index(heading)
            end = claude.find("\n### ", start + len(heading))
            section = claude[start:] if end == -1 else claude[start:end]
            with self.subTest(heading=heading):
                self.assertIn("github_graphql", section)


if __name__ == "__main__":
    unittest.main()
