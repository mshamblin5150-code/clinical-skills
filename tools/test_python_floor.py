"""Regression checks for the repository's stated Python floor."""

from __future__ import annotations

import ast
import contextlib
import io
import re
import sys
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

import test_console_codec
from git_paths import read_path_records
import python_floor
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent
FLOOR_STATEMENT = re.compile(
    r"\b(?:"
    r"(?P<label_first>consumer|tooling) floor is Python "
    r"(?P<first_major>[0-9]+)\.(?P<first_minor>[0-9]+)"
    r"|Python (?P<second_major>[0-9]+)\.(?P<second_minor>[0-9]+) "
    r"is (?:the )?(?P<label_second>consumer|tooling) floor"
    r"|(?P<requires>requires?|needs?) Python "
    r"(?P<third_major>[0-9]+)\.(?P<third_minor>[0-9]+)"
    r")\b",
    re.IGNORECASE,
)

# This object declares the check's ceiling: a portable path containing a
# directory separator or filename dot, followed by a positive decimal
# coordinate. Bare words before a colon are not path-shaped.
PATH_COORDINATE_CEILING = re.compile(
    r"(?<![\w./:-])(?:"
    r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
    r"|[A-Za-z_][A-Za-z0-9_-]*\.[A-Za-z][A-Za-z0-9_.-]*"
    r"):[1-9][0-9]*\b"
)
FENCE = re.compile(
    r"^(?:(?:[ ]{0,3}>[ ]?)+)?"
    r"(?:[ \t]*(?:[-+*]|[0-9]+[.)])[ \t]+)?"
    r"[ \t]*(`{3,}|~{3,})(.*)$"
)


def prose_outside_fences(text: str) -> str:
    """Return prose outside Markdown fences while preserving line positions."""

    kept: list[str] = []
    marker = ""
    width = 0
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if not marker:
            if match:
                marker = match.group(1)[0]
                width = len(match.group(1))
                kept.append("\n" if line.endswith("\n") else "")
            else:
                kept.append(line)
            continue
        if (
            match
            and match.group(1)[0] == marker
            and len(match.group(1)) >= width
            and not match.group(2).strip()
        ):
            marker = ""
            width = 0
        kept.append("\n" if line.endswith("\n") else "")
    return "".join(kept)


def tracked_prose(root: Path) -> tuple[str, ...]:
    """Return tracked Markdown outside ``docs/adr/``.

    A clean walk means no tracked Markdown file in that scope carries a line
    coordinate. An untracked or unstaged file is invisible until it enters the
    index.
    """

    return tuple(
        relative
        for relative in read_path_records(
            root, "ls-files", "--cached", "-z", "--", "*.md"
        )
        if PurePosixPath(relative).parts[:2] != ("docs", "adr")
    )


def calls_zip_strict(source: str) -> bool:
    """Return whether source calls the built-in-shaped ``zip(strict=)`` API."""

    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "zip"
        and any(keyword.arg == "strict" for keyword in node.keywords)
        for node in ast.walk(ast.parse(source))
    )


def floor_statements(text: str) -> tuple[tuple[str, tuple[int, int]], ...]:
    statements = []
    for match in FLOOR_STATEMENT.finditer(text):
        label = (match.group("label_first") or match.group("label_second") or "consumer").lower()
        major = match.group("first_major") or match.group("second_major") or match.group("third_major")
        minor = match.group("first_minor") or match.group("second_minor") or match.group("third_minor")
        statements.append((label, (int(major), int(minor))))
    return tuple(statements)


def stated_floors(path: Path) -> tuple[tuple[str, tuple[int, int]], ...]:
    return floor_statements(path.read_text(encoding="utf-8"))


class TheCoordinateInstrumentIsLive(unittest.TestCase):
    def test_inline_code_is_read(self):
        text = "The anchor is `tools/hooks/pre-commit:12`."
        self.assertIsNotNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_fenced_output_is_exempt(self):
        text = "before\n```text\ntools/example.py:12\n```\nafter\n"
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_block_quoted_fence_is_exempt(self):
        text = "> ```text\n> tools/example.py:12\n> ```\n"
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_list_continuation_fence_is_exempt(self):
        text = (
            "10. item\n"
            "    ```text\n"
            "    tools/hooks/pre-commit:12\n"
            "    ```\n"
        )
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_real_tracked_member_with_an_injected_coordinate_is_refused(self):
        source = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        mutant = source + "\nThe injected anchor is `tools/hooks/pre-commit:12`.\n"
        matches = PATH_COORDINATE_CEILING.findall(prose_outside_fences(mutant))
        self.assertIn("tools/hooks/pre-commit:12", matches)


class TrackedProseHasNoLineCoordinates(unittest.TestCase):
    def test_the_tracked_population_is_zero(self):
        findings: list[str] = []
        for relative in tracked_prose(REPO_ROOT):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8", errors="replace")
            for match in PATH_COORDINATE_CEILING.finditer(prose_outside_fences(text)):
                findings.append(f"{relative}: {match.group(0)}")
        self.assertEqual([], findings)


class TheStatedFloorHasEvidence(unittest.TestCase):
    def test_non_test_tooling_calls_zip_strict(self):
        sources = (
            path.read_text(encoding="utf-8")
            for path in sorted((REPO_ROOT / "tools").glob("*.py"))
            if not path.name.startswith("test_")
        )
        self.assertTrue(
            any(calls_zip_strict(source) for source in sources),
            "no non-test module under tools/ calls zip(strict=)",
        )

    def test_main_guard_evaluates_its_pep_604_return_annotation(self):
        self.assertEqual(
            ast.If | None,
            test_console_codec.main_guard.__annotations__.get("return"),
        )


class TheDeclaredFloors(unittest.TestCase):
    def test_both_floors_begin_at_the_ruled_baseline(self):
        self.assertEqual((3, 10), python_floor.CONSUMER_FLOOR)
        self.assertEqual((3, 10), python_floor.TOOLING_FLOOR)

    def test_only_syntax_and_resolved_api_witnesses_grade(self):
        self.assertEqual(
            {"syntax", "api", "api-heuristic"},
            {feature.tier for feature in python_floor.FEATURES},
        )
        self.assertEqual(
            {"syntax", "api"},
            python_floor.GRADING_TIERS,
        )


class TheInstrumentIsLive(unittest.TestCase):
    def scan(self, source: str):
        return python_floor.scan_source(source, "control.py")

    def test_a_positive_control_reaches_each_tier(self):
        witnesses = self.scan(
            "import contextlib\n"
            "def sample(rows):\n"
            "    match rows:\n"
            "        case []: return list(zip(rows, rows, strict=True))\n"
            "    contextlib.chdir('.')\n"
            "    self.walk()\n"
        )
        self.assertEqual(
            {"syntax", "api", "api-heuristic"},
            {w.feature.tier for w in witnesses},
        )

    @unittest.skipIf(sys.version_info < (3, 12), "the complete syntax control needs 3.12")
    def test_the_positive_control_carries_every_vocabulary_item(self):
        source = (
            "import contextlib, tomllib, enum, typing, datetime, itertools, pathlib, os\n"
            "def annotated() -> int | None:\n    return None\n"
            "def sample(self, rows):\n"
            "    match rows:\n        case []: pass\n"
            "    try:\n        pass\n    except* ValueError:\n        pass\n"
            "    zip(rows, strict=True)\n"
            "    contextlib.chdir('.')\n"
            "    enum.StrEnum\n    typing.Self\n    datetime.UTC\n"
            "    itertools.batched(rows, 2)\n"
            "    path = pathlib.Path('.')\n"
            "    path.unlink(missing_ok=True)\n"
            "    path.is_relative_to(pathlib.Path('/'))\n"
            "    pathlib.Path('.').walk()\n"
            "    typing.override\n    os.process_cpu_count()\n    self.walk()\n"
            "type Alias = int\n"
        )
        names = {w.feature.name for w in self.scan(source)}
        self.assertEqual({feature.name for feature in python_floor.FEATURES}, names)

    def test_python_37_only_code_yields_no_witness(self):
        self.assertEqual(
            (),
            self.scan("def sample(value):\n    return '{}'.format(value)\n"),
        )

    def test_future_annotations_defers_the_pep_604_witness(self):
        immediate = self.scan("def sample() -> int | None:\n    return None\n")
        deferred = self.scan(
            "from __future__ import annotations\n"
            "def sample() -> int | None:\n    return None\n"
        )
        self.assertIn("evaluated PEP 604 annotation", {w.feature.name for w in immediate})
        self.assertNotIn("evaluated PEP 604 annotation", {w.feature.name for w in deferred})

    def test_an_unknown_receiver_walk_is_advisory_not_pathlib(self):
        witnesses = self.scan("def sample(self):\n    return self.walk()\n")
        self.assertEqual(["api-heuristic"], [w.feature.tier for w in witnesses])

    def test_an_import_bound_path_walk_is_resolved(self):
        witnesses = self.scan(
            "from pathlib import Path\n"
            "def sample():\n    return Path('.').walk()\n"
        )
        self.assertIn("pathlib.Path.walk", {w.feature.name for w in witnesses})

    def test_an_import_alias_is_still_a_resolved_api(self):
        witnesses = self.scan("import contextlib as context\ncontext.chdir('.')\n")
        self.assertIn("contextlib.chdir", {w.feature.name for w in witnesses})

    def test_importing_a_version_gated_symbol_is_itself_a_witness(self):
        witnesses = self.scan("from contextlib import chdir\n")
        self.assertIn("contextlib.chdir", {w.feature.name for w in witnesses})

    def test_a_shadowed_import_is_not_a_resolved_api(self):
        witnesses = self.scan(
            "import contextlib\n"
            "contextlib = object()\n"
            "contextlib.chdir('.')\n"
        )
        self.assertNotIn("contextlib.chdir", {w.feature.name for w in witnesses})

    def test_a_local_parameter_does_not_shadow_an_unrelated_builtin_call(self):
        witnesses = self.scan(
            "def helper(zip):\n    return zip\n"
            "rows = zip([], [], strict=True)\n"
        )
        self.assertIn("zip(strict=)", {w.feature.name for w in witnesses})

    def test_path_runtime_apis_hold_the_downward_floor_at_39(self):
        witnesses = self.scan(
            "from pathlib import Path\n"
            "def sample(raw):\n"
            "    target = Path(raw).resolve()\n"
            "    target.unlink(missing_ok=True)\n"
            "    return target.is_relative_to(Path('/'))\n"
        )
        versions = {
            witness.feature.name: witness.feature.version for witness in witnesses
        }
        self.assertEqual((3, 8), versions["pathlib.Path.unlink(missing_ok=)"])
        self.assertEqual((3, 9), versions["pathlib.Path.is_relative_to"])

    def test_a_shadowed_zip_is_not_a_builtin_witness(self):
        witnesses = self.scan(
            "def sample(zip, rows):\n    return zip(rows, strict=True)\n"
        )
        self.assertNotIn("zip(strict=)", {w.feature.name for w in witnesses})


class TheConsumerPopulation(unittest.TestCase):
    def test_literal_skill_commands_are_roots_and_prose_pointers_are_not(self):
        roots = python_floor.invoked_roots(
            (
                ("skills/sample/SKILL.md", "Run `python tools/alpha.py --all`."),
                ("skills/_shared/reference/sheet.md", "python tools/beta.py input"),
                ("skills/sample/other.md", "See tools/merely_named.py for details."),
            )
        )
        self.assertEqual({"alpha", "beta"}, roots)

    def test_the_roots_are_closed_over_local_imports(self):
        sources = {
            "alpha": "import beta\nimport json\n",
            "beta": "from gamma import helper\n",
            "gamma": "def helper(): pass\n",
            "unreached": "import alpha\n",
        }
        self.assertEqual(
            {"alpha", "beta", "gamma"},
            python_floor.import_closure({"alpha"}, sources),
        )


class TheRepositoryVerdict(unittest.TestCase):
    def test_the_current_tree_holds_both_declared_floors(self):
        report = python_floor.scan_repository(REPO_ROOT)
        self.assertEqual(python_floor.CONSUMER_FLOOR, report.consumer_floor)
        self.assertLessEqual(report.tooling_floor, python_floor.TOOLING_FLOOR)
        self.assertFalse(report.unread)

    def test_removing_the_310_witnesses_would_expose_the_39_consumer_floor(self):
        report = python_floor.scan_repository(REPO_ROOT)
        closure = set(report.consumer_closure)
        surviving = [
            witness.feature.version
            for witness in report.witnesses
            if witness.feature.tier in python_floor.GRADING_TIERS
            and PurePosixPath(witness.path).stem in closure
            and witness.feature.version < (3, 10)
        ]
        self.assertEqual((3, 9), max(surviving))

    def test_both_populations_and_floors_are_always_rendered(self):
        report = python_floor.scan_repository(REPO_ROOT)
        text = python_floor.render(report)
        self.assertIn("consumer floor", text)
        self.assertIn("consumer roots", text)
        self.assertIn("consumer closure", text)
        self.assertIn("tooling floor", text)
        self.assertIn("tracked Python", text)
        self.assertIn("api-heuristic", text)
        for module in report.consumer_roots:
            self.assertIn(f"ROOT tools/{module}.py", text)
        for module in report.consumer_closure:
            self.assertIn(f"CLOSURE tools/{module}.py", text)
        for path in report.tracked_python:
            self.assertIn(f"TRACKED {path}", text)

    def test_the_static_limits_have_one_bound_owner(self):
        self.assertEqual(
            (),
            bind(python_floor.NOT_REACHED, python_floor.__doc__ or "", mode=NAMING),
        )


class TheCommandContract(unittest.TestCase):
    @staticmethod
    def report(*, finding=False, unread=()):
        consumer = (3, 11) if finding else python_floor.CONSUMER_FLOOR
        return python_floor.Report(
            consumer_floor=consumer,
            tooling_floor=python_floor.TOOLING_FLOOR,
            consumer_roots=("alpha",),
            consumer_closure=("alpha", "beta"),
            tracked_python=("tools/alpha.py", "tools/beta.py"),
            undeclared_roots=(),
            witnesses=(),
            unread=unread,
        )

    def run_main(self, report):
        output, error = io.StringIO(), io.StringIO()
        with mock.patch.object(python_floor, "scan_repository", return_value=report):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                status = python_floor.main()
        return status, output.getvalue(), error.getvalue()

    def test_clean_is_exit_0(self):
        status, output, error = self.run_main(self.report())
        self.assertEqual((0, ""), (status, error))
        self.assertIn("CLEAN", output)

    def test_a_floor_disagreement_is_exit_1(self):
        status, output, error = self.run_main(self.report(finding=True))
        self.assertEqual((1, ""), (status, error))
        self.assertIn("FINDING", output)

    def test_an_incomplete_walk_is_exit_2(self):
        status, output, error = self.run_main(self.report(unread=("broken.py",)))
        self.assertEqual((2, ""), (status, output))
        self.assertIn("DID NOT WALK", error)


class TheProseCopiesAreBound(unittest.TestCase):
    def test_reversed_and_requirement_spellings_cannot_evade_the_bind(self):
        self.assertEqual(
            (("consumer", (3, 11)), ("consumer", (3, 12))),
            floor_statements(
                "Python 3.11 is the consumer floor. This path requires Python 3.12."
            ),
        )

    def test_readme_states_both_declared_floors(self):
        self.assertEqual(
            (
                ("consumer", python_floor.CONSUMER_FLOOR),
                ("tooling", python_floor.TOOLING_FLOOR),
            ),
            stated_floors(REPO_ROOT / "README.md"),
        )

    def test_claude_states_both_declared_floors(self):
        self.assertEqual(
            (
                ("consumer", python_floor.CONSUMER_FLOOR),
                ("tooling", python_floor.TOOLING_FLOOR),
            ),
            stated_floors(REPO_ROOT / "CLAUDE.md"),
        )

    def test_agents_states_the_declared_consumer_floor(self):
        self.assertEqual(
            (("consumer", python_floor.CONSUMER_FLOOR),),
            stated_floors(REPO_ROOT / "AGENTS.md"),
        )


if __name__ == "__main__":
    unittest.main()
