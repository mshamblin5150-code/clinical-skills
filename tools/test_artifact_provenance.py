"""Behavior tests for shared artifact provenance trust."""

from __future__ import annotations

import ast
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
import warnings
from datetime import date
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import artifact_provenance  # noqa: E402
import uspstf_table  # noqa: E402
from repo_root import InsideCheckout  # noqa: E402
from prose_bind import ProseBind  # noqa: E402


class ArtifactIdentityTables(unittest.TestCase):
    def test_each_cache_identity_contains_its_content_trust_floor(self):
        expected_cache = {
            "extraction": {
                "tools/guidelines_extract.py",
                "tools/guidelines_manifest.py",
                "tools/artifact_provenance.py",
            },
            "index": {
                "tools/guidelines_index.py",
                "tools/guidelines_index_artifact.py",
                "tools/guidelines_manifest.py",
                "tools/artifact_provenance.py",
            },
        }
        expected_floor = {
            "extraction": {
                "tools/guidelines_extract.py",
                "tools/guidelines_manifest.py",
            },
            "index": {
                "tools/guidelines_index.py",
                "tools/guidelines_manifest.py",
            },
        }

        self.assertEqual(
            {kind: set(paths) for kind, paths in artifact_provenance.CACHE_IDENTITY.items()},
            expected_cache,
        )
        self.assertEqual(
            {kind: set(paths) for kind, paths in artifact_provenance.TRUST_FLOOR.items()},
            expected_floor,
        )
        for kind in expected_cache:
            self.assertGreater(
                set(artifact_provenance.CACHE_IDENTITY[kind]),
                set(artifact_provenance.TRUST_FLOOR[kind]),
            )

    def test_the_derived_reader_uses_both_shared_trust_floors(self):
        floors = {
            "extraction": ("tools/extraction-sentinel.py",),
            "index": ("tools/index-sentinel.py",),
        }
        trusted = artifact_provenance.ProvenanceCheck({}, ())
        with (
            mock.patch.object(artifact_provenance, "TRUST_FLOOR", floors),
            mock.patch.object(
                artifact_provenance, "check_producer", return_value=trusted
            ) as check,
        ):
            artifact_provenance.check_derived(
                {"producer": {}, "source": {}, "untrusted_reasons": []},
                "index.sqlite",
            )

        self.assertEqual(
            [call.kwargs["unchanged_paths"] for call in check.call_args_list],
            [floors["index"], floors["extraction"]],
        )


class AcceptedDistrustDeclarations(unittest.TestCase):
    def test_reasons_round_trip_without_splitting_a_semicolon(self):
        reasons = (
            "was produced by a different commit (abc; current is def)",
            "was produced by a dirty checkout",
        )
        rendered = artifact_provenance.render_accepted_distrust(
            Path("C:/corpus"), reasons, on=date(2026, 8, 23)
        )

        declaration, problems = artifact_provenance.parse_accepted_distrust(rendered)

        self.assertEqual(problems, ())
        self.assertEqual(declaration.reasons, reasons)

    def test_a_fenced_format_example_is_a_mention_not_a_declaration(self):
        text = """The artifact uses this form:\n\n```text
accepted distrust against <corpus> on <date>:
  - <reason>
```\n"""

        declaration, problems = artifact_provenance.parse_accepted_distrust(text)

        self.assertIsNone(declaration)
        self.assertEqual(problems, ())


class MergeParentTrustTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self._git("init", "--initial-branch=main")
        self._git("config", "user.email", "fixture@example.com")
        self._git("config", "user.name", "Fixture")
        (self.repo / "tools").mkdir()
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'stable'\n", encoding="utf-8"
        )
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self._git("add", "tools/guidelines_extract.py", "base.txt")
        self._git("commit", "-m", "base")
        self._git("branch", "feature")

    def _git(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()

    def test_a_legacy_stamp_names_its_missing_producer_file_identity(self):
        commit = self._git("rev-parse", "HEAD")

        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance,
            "records no producer-file identity",
        ):
            artifact_provenance.check_producer(
                {"commit": commit, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )

    def test_an_older_stamp_also_names_a_new_uncommitted_working_tree_edit(self):
        recorded = self._git("rev-parse", "HEAD")
        (self.repo / "later.txt").write_text("later\n", encoding="utf-8")
        self._git("add", "later.txt")
        self._git("commit", "-m", "later commit")
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'uncommitted'\n", encoding="utf-8"
        )

        with self.assertRaises(artifact_provenance.UntrustedProvenance) as refused:
            artifact_provenance.check_producer(
                {"commit": recorded, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )

        self.assertIn("different commit", str(refused.exception))
        self.assertIn("uncommitted changes in the working tree", str(refused.exception))

    def test_an_unchanged_extractor_built_on_the_incoming_parent_is_trusted(self):
        (self.repo / "main.txt").write_text("main\n", encoding="utf-8")
        self._git("add", "main.txt")
        self._git("commit", "-m", "main work")
        incoming_parent = self._git("rev-parse", "HEAD")
        self._git("switch", "feature")
        (self.repo / "feature.txt").write_text("feature\n", encoding="utf-8")
        self._git("add", "feature.txt")
        self._git("commit", "-m", "feature work")
        self._git("merge", "--no-commit", "--no-ff", "main")
        inputs = artifact_provenance.producer_file_identity(
            ("tools/guidelines_extract.py",), repo_root=self.repo
        )

        result = artifact_provenance.check_producer(
            {"commit": incoming_parent, "dirty": False, "inputs": inputs},
            self.repo / "manifest.json",
            repo_root=self.repo,
            unchanged_paths=("tools/guidelines_extract.py",),
        )

        self.assertTrue(result.trusted)

    def test_a_changed_extractor_from_the_incoming_parent_is_refused(self):
        incoming_parent = self._git("rev-parse", "HEAD")
        self._git("switch", "feature")
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'changed'\n", encoding="utf-8"
        )
        self._git("add", "tools/guidelines_extract.py")
        self._git("commit", "-m", "change extractor")
        self._git("merge", "--no-commit", "--no-ff", "main")

        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance, "different commit"
        ):
            artifact_provenance.check_producer(
                {"commit": incoming_parent, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )

    def test_an_artifact_from_head_is_refused_when_the_merge_changes_its_extractor(self):
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'changed on main'\n", encoding="utf-8"
        )
        self._git("add", "tools/guidelines_extract.py")
        self._git("commit", "-m", "change extractor on main")
        self._git("switch", "feature")
        (self.repo / "feature.txt").write_text("feature\n", encoding="utf-8")
        self._git("add", "feature.txt")
        self._git("commit", "-m", "feature work")
        current_parent = self._git("rev-parse", "HEAD")
        self._git("merge", "--no-commit", "--no-ff", "main")

        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance, "working tree"
        ):
            artifact_provenance.check_producer(
                {"commit": current_parent, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )


class TheTraceSurvivesAHostileFilter(unittest.TestCase):
    """#406. The escape hatch's trace was a ``RuntimeWarning`` and nothing else, so an
    operator with ``PYTHONWARNINGS=ignore`` set for unrelated reasons read a dirty or
    foreign artifact, got no trace at all, and exited 0 exactly as a trusted read does.

    **A test run under default filters cannot tell the two designs apart**, which is why
    every case here makes the filter hostile first. The subprocess case exists because
    ``PYTHONWARNINGS`` is read at interpreter startup and an in-process filter is a
    stand-in for it -- #150's end-to-end case had to be a subprocess for the same reason.
    """

    def _trace_lines(self, stderr: str) -> list[str]:
        return [line for line in stderr.splitlines() if line.startswith("untrusted artifact")]

    def _run_with_pythonwarnings(self, setting: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "run.py"
            script.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(TOOLS)!r})\n"
                "import artifact_provenance as ap\n"
                "ap.check_producer(None, 'X', allow_untrusted=True, expected_commit='abc')\n",
                encoding="utf-8",
            )
            environment = dict(os.environ, PYTHONWARNINGS=setting)
            return subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
            )

    def test_the_line_survives_an_in_process_ignore_filter(self):
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                artifact_provenance.check_producer(
                    None, "the-artifact", allow_untrusted=True, expected_commit="abc"
                )
        self.assertEqual(len(self._trace_lines(stderr.getvalue())), 1)

    def test_the_line_names_the_flag_that_let_the_run_continue(self):
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                artifact_provenance.check_producer(
                    None, "the-artifact", allow_untrusted=True, expected_commit="abc"
                )
        line = self._trace_lines(stderr.getvalue())[0]
        self.assertIn(artifact_provenance.FLAG, line)
        self.assertIn("has no producer provenance stamp", line)

    def test_the_line_is_not_shouted(self):
        """#258's register ruling. A shout is what ``PATIENT NAMES ARE NOT CHECKED``
        spends on a check going *unenforced*; this one ran and was overridden on purpose.
        """
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                artifact_provenance.check_producer(
                    None, "the-artifact", allow_untrusted=True, expected_commit="abc"
                )
        line = self._trace_lines(stderr.getvalue())[0]
        shouted = [word for word in line.split() if len(word) > 3 and word.isupper()]
        self.assertEqual(shouted, [])

    def test_pythonwarnings_ignore_does_not_reach_it(self):
        """The row #406 measured as *printed not at all*, driven end to end."""
        completed = self._run_with_pythonwarnings("ignore")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr.count("untrusted artifact X"), 1)
        self.assertNotIn("RuntimeWarning", completed.stderr)

    def test_pythonwarnings_error_cannot_abort_or_hide_it(self):
        completed = self._run_with_pythonwarnings("error")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr.count("untrusted artifact X"), 1)
        self.assertNotIn("Traceback", completed.stderr)

    def test_an_error_filter_cannot_preempt_the_audit_line(self):
        """Ambient warning policy cannot erase the trace or abort the override."""
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with contextlib.redirect_stderr(stderr):
                check = artifact_provenance.check_producer(
                    None,
                    "the-artifact",
                    allow_untrusted=True,
                    expected_commit="abc",
                )
        self.assertFalse(check.trusted)
        self.assertEqual(len(self._trace_lines(stderr.getvalue())), 1)
        self.assertIn(artifact_provenance.FLAG, stderr.getvalue())

    def test_the_trace_stays_off_stdout(self):
        """A command's stdout is its result. A trace on it would corrupt every caller
        that pipes ``guidelines_search`` into something."""
        stdout, stderr = io.StringIO(), io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                artifact_provenance.check_producer(
                    None, "the-artifact", allow_untrusted=True, expected_commit="abc"
                )
        self.assertEqual(stdout.getvalue(), "")
        self.assertNotEqual(stderr.getvalue(), "")

    def test_a_trusted_check_traces_nothing(self):
        """The instrument has to be able to stay quiet, or every case above passes for
        a reason that has nothing to do with distrust."""
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                check = artifact_provenance.check_producer(
                    {"commit": "abc", "dirty": False},
                    "the-artifact",
                    allow_untrusted=True,
                    expected_commit="abc",
                )
        self.assertTrue(check.trusted)
        self.assertEqual(stderr.getvalue(), "")

    def test_the_refusal_path_is_untouched(self):
        """Without the flag this still raises. #406 claims nothing about that branch."""
        with self.assertRaises(artifact_provenance.UntrustedProvenance):
            artifact_provenance.check_producer(
                None, "the-artifact", allow_untrusted=False, expected_commit="abc"
            )


class TheDedupIsDeclaredRatherThanFixed(unittest.TestCase):
    """#406's third decision. ``warnings`` prints one message per unique message and
    site, which is correct for a deprecation and wrong for an audit record. The print
    carries the audit trace and never deduplicates, so the warning's dedup is left as
    correct semantics for its remaining job as a programmatic hook.
    """

    def test_the_same_artifact_checked_twice_traces_twice(self):
        stderr = io.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                for _ in range(2):
                    artifact_provenance.check_producer(
                        None, "the-artifact", allow_untrusted=True, expected_commit="abc"
                    )
        self.assertEqual(stderr.getvalue().count("untrusted artifact the-artifact"), 2)

    def test_the_warning_still_deduplicates_under_the_default_filter(self):
        """Pinned as intended rather than left to be rediscovered as a defect. Driven
        under the *default* filter, because ``assertWarns`` forces ``always`` and would
        report the opposite while proving nothing."""
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "run.py"
            script.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(TOOLS)!r})\n"
                "import artifact_provenance as ap\n"
                "for _ in range(2):\n"
                "    ap.check_producer(None, 'X', allow_untrusted=True, expected_commit='abc')\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=dict(os.environ, PYTHONWARNINGS="default"),
            )
        self.assertEqual(completed.stderr.count("RuntimeWarning"), 1)
        self.assertEqual(completed.stderr.count("continuing because"), 2)

    def test_the_declaration_is_beside_the_mechanism(self):
        reasons = dict(artifact_provenance.NOT_GUARDED)
        self.assertIn("the warning deduplicates and the stderr line does not", reasons)


class TheDerivedCheckTracesToo(unittest.TestCase):
    """#406 named ``check_producer`` and there are two emission sites. ``check_derived``
    reports *inherited* distrust -- the reasons an upstream artifact carried -- and had
    the identical suppressible warning."""

    def test_inherited_distrust_reaches_stderr(self):
        stderr = io.StringIO()
        provenance = {
            "producer": {"commit": "abc", "dirty": False},
            "source": {"commit": "abc", "dirty": False},
            "untrusted_reasons": ["was produced by a dirty checkout"],
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(stderr):
                artifact_provenance.check_derived(
                    provenance, "derived-artifact", allow_untrusted=True
                )
        self.assertIn("derived-artifact", stderr.getvalue())
        self.assertIn("was produced by a dirty checkout", stderr.getvalue())
        self.assertIn(artifact_provenance.FLAG, stderr.getvalue())

    def test_neither_site_is_left_on_the_bare_warning(self):
        """An AST walk rather than a substring search, because this module's own
        docstring and ``NOT_GUARDED`` both discuss ``warnings`` -- ``spelling_scan``'s
        mention-versus-use problem arriving on a test."""
        tree = ast.parse(Path(artifact_provenance.__file__).read_text(encoding="utf-8"))
        emitters = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "warn"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "warnings"
        ]
        self.assertEqual(len(emitters), 1, "every warn goes through the one mechanism")
        traces = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_trace"
        ]
        self.assertEqual(len(traces), 2, "check_producer and check_derived")


class ThePublicationRule(unittest.TestCase):
    """docs/adr/0010. An untrusted read may not publish into a checkout.

    ``uspstf_table`` is the only caller because it is the only flag-bearing command that
    can publish inside the repo at all: the others either produce no durable artifact or
    already guard their destination outside every checkout.
    """

    def test_the_flag_off_is_a_no_op_even_inside_a_checkout(self):
        inside = REPO / "reference" / "guidelines-uspstf.md"
        self.assertEqual(
            artifact_provenance.refuse_publication(inside, allow_untrusted=False),
            Path(inside),
        )

    def test_the_flag_on_refuses_a_path_inside_a_checkout(self):
        inside = REPO / "reference" / "guidelines-uspstf.md"
        with self.assertRaises(InsideCheckout):
            artifact_provenance.refuse_publication(inside, allow_untrusted=True)

    def test_the_refusal_names_the_flag_and_the_remedy(self):
        inside = REPO / "reference" / "guidelines-uspstf.md"
        with self.assertRaises(InsideCheckout) as raised:
            artifact_provenance.refuse_publication(inside, allow_untrusted=True)
        message = str(raised.exception)
        self.assertIn(artifact_provenance.FLAG, message)
        self.assertIn("outside every checkout", message)

    def test_the_flag_on_allows_a_path_outside_every_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "table.md"
            self.assertEqual(
                artifact_provenance.refuse_publication(target, allow_untrusted=True),
                target.resolve(),
            )

    def test_a_sibling_worktree_is_a_checkout_too(self):
        """``ensure_outside_checkout`` walks up for a ``.git`` entry rather than
        comparing against known roots, which is #176's stronger rule. Pinned here
        because a publish into another checkout is the same defect."""
        with tempfile.TemporaryDirectory() as directory:
            other = Path(directory) / "other"
            (other / ".git").mkdir(parents=True)
            with self.assertRaises(InsideCheckout):
                artifact_provenance.refuse_publication(
                    other / "table.md", allow_untrusted=True
                )


class TheCommandRefusesBeforeItReads(unittest.TestCase):
    """The status and the ordering, driven through ``uspstf_table``'s own entry point.

    **Exit 2**, on ``docx_write``'s recorded rule that a writer's refusal is 2 and there
    is no 1, because a writer has no *found nothing* to report. #303 ruled the command
    boundary owns what a shared refusal means for its run.

    **Before the read**, on #176's lesson: ``guidelines_extract`` used to ask this after
    loading a PDF library and ``guidelines_recs`` after reading the document, so a
    refused run had already spent the half that costs.
    """

    def _run(self, *arguments: str):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = uspstf_table.main(list(arguments))
        return status, stderr.getvalue()

    def test_the_committed_default_out_is_refused_under_the_flag(self):
        status, stderr = self._run("C:/no-such-corpus", "--allow-untrusted-provenance")
        self.assertEqual(status, 2)
        self.assertIn(artifact_provenance.WHY_NO_PUBLISH, stderr)

    def test_the_refusal_beats_the_missing_corpus(self):
        """Both conditions hold at once. The placement question is about argv alone, so
        it is answered first and the expensive read never happens."""
        _, stderr = self._run("C:/no-such-corpus", "--allow-untrusted-provenance")
        self.assertNotIn("extracted corpus not found", stderr)

    def test_without_the_flag_the_guard_does_not_fire(self):
        status, stderr = self._run("C:/no-such-corpus")
        self.assertEqual(status, 2)
        self.assertNotIn(artifact_provenance.WHY_NO_PUBLISH, stderr)
        self.assertIn("extracted corpus not found", stderr)

    def test_an_out_outside_every_checkout_passes_the_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            status, stderr = self._run(
                "C:/no-such-corpus",
                "--allow-untrusted-provenance",
                "--out",
                str(Path(directory) / "table.md"),
            )
        self.assertEqual(status, 2)
        self.assertNotIn(artifact_provenance.WHY_NO_PUBLISH, stderr)
        self.assertIn("extracted corpus not found", stderr)


class EveryParserUsesTheSharedEffectClause(unittest.TestCase):
    """#406's fifth decision. All five parsers said ``and warn``, which the fix
    falsifies, and five hand-kept copies of one sentence is #220's shape.

    **The narrow predicate, not the one #176 refused.** It keys on *declares this
    argument*, which is a literal in the parser, and asserts a property of the help
    string. It never has to guess which commands publish.
    """

    def _declarations(self):
        found = []
        for path in sorted(TOOLS.glob("*.py")):
            if path.name.startswith("test_"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add_argument"
                ):
                    continue
                if not (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == artifact_provenance.FLAG
                ):
                    continue
                helps = [kw.value for kw in node.keywords if kw.arg == "help"]
                found.append((path.name, helps[0] if helps else None))
        return found

    @staticmethod
    def _cites_the_constant(node) -> bool:
        if node is None or isinstance(node, ast.Constant):
            return False
        names = EveryParserUsesTheSharedEffectClause._referenced_names(node)
        return "FLAG_HELP_EFFECT" in names

    @staticmethod
    def _referenced_names(node) -> set[str]:
        return {
            child.attr if isinstance(child, ast.Attribute) else child.id
            for child in ast.walk(node)
            if isinstance(child, (ast.Attribute, ast.Name))
        }

    def test_the_population_is_not_empty(self):
        """Without this the class passes on a walk that found nothing."""
        self.assertGreaterEqual(len(self._declarations()), 5)

    def test_no_parser_spells_the_effect_out(self):
        offenders = [
            name
            for name, node in self._declarations()
            if not self._cites_the_constant(node)
        ]
        self.assertEqual(offenders, [])

    def test_none_of_them_still_says_and_warn(self):
        """The literal words the fix falsified."""
        for path in sorted(TOOLS.glob("*.py")):
            if path.name.startswith("test_"):
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("unstamped extracted corpus and warn", text, path.name)
            self.assertNotIn("unstamped index and warn", text, path.name)

    def test_the_predicate_catches_a_planted_bare_literal(self):
        """Mutation-driven. A predicate that cannot fail is not a check."""
        planted = ast.parse(
            'p.add_argument("--allow-untrusted-provenance", help="read one and warn")'
        )
        node = next(n for n in ast.walk(planted) if isinstance(n, ast.Call))
        helps = [kw.value for kw in node.keywords if kw.arg == "help"]
        self.assertFalse(self._cites_the_constant(helps[0]))

    def test_the_predicate_accepts_the_shape_the_tree_uses(self):
        accepted = ast.parse(
            'p.add_argument("--allow-untrusted-provenance",'
            ' help=("read one; " f"{artifact_provenance.FLAG_HELP_EFFECT}"))'
        )
        node = next(n for n in ast.walk(accepted) if isinstance(n, ast.Call))
        helps = [kw.value for kw in node.keywords if kw.arg == "help"]
        self.assertTrue(self._cites_the_constant(helps[0]))

    def test_a_declaration_with_no_help_at_all_is_caught(self):
        planted = ast.parse('p.add_argument("--allow-untrusted-provenance")')
        node = next(n for n in ast.walk(planted) if isinstance(n, ast.Call))
        self.assertFalse(self._cites_the_constant(None))
        self.assertEqual([kw for kw in node.keywords if kw.arg == "help"], [])

    def test_the_one_command_that_refuses_says_so_in_its_help(self):
        """`uspstf_table` builds its parser inside `main`, so this is read off the
        declaration rather than off a parser object that does not exist."""
        declarations = dict(self._declarations())
        node = declarations["uspstf_table.py"]
        names = self._referenced_names(node)
        self.assertIn("FLAG_HELP_NO_PUBLISH", names)

    def test_no_other_command_claims_to_refuse_a_publish(self):
        """The rule lands on one command. A second claiming it in help text without
        calling the guard would be worse than silence."""
        for name, node in self._declarations():
            if name == "uspstf_table.py":
                continue
            names = self._referenced_names(node)
            self.assertNotIn("FLAG_HELP_NO_PUBLISH", names, name)


class TheDeclaredLimitsArePointedAtRatherThanCopied(ProseBind, unittest.TestCase):
    """#241's repair adopted at the outset rather than after two copies drifted.

    The object is named in three places -- the module docstring, ``CLAUDE.md``, and
    docs/adr/0010 -- and no row of it is written into any of them. A prose edit to a
    limit fails nothing, so a limit written as prose goes stale in the direction nobody
    notices; #220 is the recorded instance.

    ``ProseBind`` rather than a raw ``assertNotIn``, because every one of these files
    hard-wraps and a phrase broken across two lines is invisible to a substring search
    -- #412, and ``test_run_record_claim``'s finding before it.
    """

    def _copies(self):
        return {
            "the module docstring": artifact_provenance.__doc__,
            "CLAUDE.md": (REPO / "CLAUDE.md").read_text(encoding="utf-8"),
            "the ADR": (
                REPO / "docs" / "adr"
                / "0010-an-untrusted-read-may-not-publish-into-the-checkout.md"
            ).read_text(encoding="utf-8"),
        }

    def test_every_copy_points_at_the_object(self):
        for where, prose in self._copies().items():
            self.assertProseIn("NOT_GUARDED", prose, where)

    def test_no_copy_carries_a_row_of_it(self):
        for where, prose in self._copies().items():
            for headline, reason in artifact_provenance.NOT_GUARDED:
                self.assertProseNotIn(headline, prose, f"{where}: {headline}")
                self.assertProseNotIn(reason, prose, f"{where}: reason for {headline}")

    def test_the_bind_is_live(self):
        """Without this the class passes on an empty tuple, which is the shape it
        exists to refuse one level up."""
        self.assertGreaterEqual(len(artifact_provenance.NOT_GUARDED), 3)
        for where, prose in self._copies().items():
            self.assertGreater(len(prose), 200, where)

    def test_the_needle_would_be_found_if_a_row_were_copied(self):
        """Mutation-driven, on the walk rather than on the tree: the guard above is
        only worth its run if a planted copy fails it."""
        headline, reason = artifact_provenance.NOT_GUARDED[0]
        planted = f"""some prose that
happens to say {headline} across a wrap"""
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(headline, planted)
        self.assertProseIn(headline, planted)
        self.assertTrue(reason.strip())

    def test_every_row_carries_a_reason(self):
        for headline, reason in artifact_provenance.NOT_GUARDED:
            self.assertTrue(headline.strip())
            self.assertGreater(len(reason.split()), 8, headline)


if __name__ == "__main__":
    unittest.main()
