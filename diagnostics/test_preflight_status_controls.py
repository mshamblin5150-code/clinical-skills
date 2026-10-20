"""Portable focused controls; never invoked by the diagnostic workflow itself."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import preflight_status_diagnostic as diagnostic
from preflight_status_diagnostic import DiagnosticHold, capture_owned_status, require_clean_status, sanitize_status


class StatusPrivacyControls(unittest.TestCase):
    def test_empty_status_is_the_only_clean_status(self):
        result = sanitize_status(b"")
        self.assertTrue(result["valid"])
        self.assertTrue(result["clean"])
        self.assertEqual(result["records"], 0)

    def test_allowlisted_source_and_exact_cache_paths(self):
        raw = (b" M tools/console_codec.py\r\n"
               b"?? diagnostics/__pycache__/parallel_reader_capture.cpython-314.pyc\r\n")
        result = sanitize_status(raw)
        self.assertTrue(result["valid"])
        self.assertFalse(result["clean"])
        self.assertEqual(result["categories"], {"tracked": 1, "untracked": 1})
        self.assertEqual(result["records"], 2)
        self.assertEqual(len(result["known_paths"]), 2)
        self.assertEqual(result["unknown_paths"], 0)

    def test_unknown_and_main_module_cache_names_are_not_exposed(self):
        private = "private-subject-DO-NOT-EMIT.txt"
        raw = ("?? " + private + "\n?? diagnostics/__pycache__/measure_parallel_readers.cpython-314.pyc\n").encode()
        result = sanitize_status(raw)
        self.assertTrue(result["valid"])
        self.assertEqual(result["unknown_paths"], 2)
        self.assertNotIn(private, json.dumps(result))
        self.assertNotIn("measure_parallel_readers.cpython-314.pyc", json.dumps(result))
        self.assertEqual(result["known_paths"], [])

    def test_rename_quoted_and_unicode_unknown_paths_are_opaque(self):
        raw = 'R  private-old -> private-new\n?? "private-quoted"\n?? private-\u03bb\n'.encode()
        result = sanitize_status(raw)
        self.assertTrue(result["valid"])
        self.assertEqual(result["unknown_paths"], 3)
        self.assertNotIn("private-", json.dumps(result))

    def test_mixed_valid_and_invalid_status_refuses_without_partial_paths(self):
        for invalid in (b"garbage secret\n", b"?M secret\n", b"   secret\n", b" M \n",
                        b"?? \xff\n", b"?? secret\0", b"?? secret", b"?? secret\r"):
            with self.subTest(invalid=invalid):
                result = sanitize_status(b" M tools/console_codec.py\n" + invalid)
                self.assertFalse(result["valid"])
                self.assertFalse(result["clean"])
                self.assertEqual(result["known_paths"], [])
                self.assertNotIn("secret", json.dumps(result))

    def test_unknown_output_is_bounded(self):
        result = sanitize_status(b"".join(("?? private-%d\n" % number).encode() for number in range(50)))
        self.assertTrue(result["valid"])
        self.assertEqual(result["unknown_paths"], 50)
        self.assertEqual(len(result["unknown_path_sha256"]), 16)
        self.assertTrue(result["detail_truncated"])


class ExactGuardBoundaryControls(unittest.TestCase):
    def test_clean_and_every_nonempty_status_use_the_original_predicate(self):
        def original_require(condition, code):
            if not condition:
                raise RuntimeError(code)

        require_clean_status("", original_require)
        for status in ("?? unknown\n", " M tools/console_codec.py\n", " ", "\n", "invalid"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(RuntimeError, "^observer_not_clean$"):
                    require_clean_status(status, original_require)


class CaptureOwnershipControls(unittest.TestCase):
    def make_original(self, *, fail=False, cleanup=True):
        root = Path("synthetic-private-capture").resolve()
        captured = root / "commands/command-0001/stdout.bin"

        class Commands:
            cleaned = False

            def __init__(self):
                self.counter = 0
                self.owners = []

            def git(self, *args, **kwargs):
                self.counter += 1
                self.owners.append(SimpleNamespace(result=SimpleNamespace(stdout_path=str(captured))))
                if fail:
                    raise RuntimeError("synthetic_capture_failure")
                return ""

            def cleanup(self):
                self.cleaned = True
                return cleanup

        commands = Commands()
        original = SimpleNamespace(OwnedCommands=lambda path: commands)
        return original, commands, root, captured

    def test_success_returns_capture_only_after_verified_cleanup(self):
        original, commands, root, captured = self.make_original()
        self.assertEqual(capture_owned_status(original, root, root, time.monotonic() + 1), captured)
        self.assertTrue(commands.cleaned)

    def test_failed_capture_still_cleans(self):
        original, commands, root, _ = self.make_original(fail=True)
        with self.assertRaisesRegex(RuntimeError, "^synthetic_capture_failure$"):
            capture_owned_status(original, root, root, time.monotonic() + 1)
        self.assertTrue(commands.cleaned)

    def test_unverified_cleanup_refuses_a_successful_capture(self):
        original, commands, root, _ = self.make_original(cleanup=False)
        with self.assertRaisesRegex(DiagnosticHold, "^command_cleanup_unverified$"):
            capture_owned_status(original, root, root, time.monotonic() + 1)
        self.assertTrue(commands.cleaned)


class CommandPolicyControls(unittest.TestCase):
    def synthetic_policy(self, root, refuse=False):
        tools = root / "tools"
        tools.mkdir()
        console = (
            "from pathlib import Path\n"
            "def use_utf8():\n"
            "    Path(__file__).with_name('events').write_text('utf8\\n')\n"
            "def require_python_floor():\n"
            "    import python_floor\n"
            "    with Path(__file__).with_name('events').open('a') as stream:\n"
            "        stream.write('floor\\n')\n"
            + ("    raise SystemExit(2)\n" if refuse else "")
        )
        sources = {"tools/console_codec.py": console,
                   "tools/python_floor.py": "import git_paths\n", "tools/git_paths.py": ""}
        for relative, source in sources.items():
            (root / relative).write_text(source, encoding="utf-8")
        return {relative: diagnostic.digest(source.encode()) for relative, source in sources.items()}

    def test_policy_order_and_import_state_restored(self):
        previous = sys.path[:]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hashes = self.synthetic_policy(root)
            with mock.patch.dict(diagnostic.SOURCE_HASHES, hashes):
                diagnostic.bootstrap_command_policy(root)
            self.assertEqual((root / "tools/events").read_text(), "utf8\nfloor\n")
        self.assertEqual(sys.path, previous)
        self.assertTrue(all(Path(path).stem not in sys.modules for path in diagnostic.POLICY_PATHS))

    def test_floor_refusal_restores_path_and_removes_only_introduced_modules(self):
        previous = sys.path[:]
        sentinel = object()
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(sys.modules, {"unrelated_policy_control": sentinel}):
            root = Path(directory)
            hashes = self.synthetic_policy(root, refuse=True)
            with mock.patch.dict(diagnostic.SOURCE_HASHES, hashes), self.assertRaises(SystemExit):
                diagnostic.bootstrap_command_policy(root)
            self.assertEqual((root / "tools/events").read_text(), "utf8\nfloor\n")
            self.assertIs(sys.modules["unrelated_policy_control"], sentinel)
        self.assertEqual(sys.path, previous)
        self.assertTrue(all(Path(path).stem not in sys.modules for path in diagnostic.POLICY_PATHS))

    def test_preloaded_policy_is_refused_without_substitution(self):
        previous = sys.path[:]
        sentinel = SimpleNamespace()
        with mock.patch.dict(sys.modules, {"console_codec": sentinel}):
            with self.assertRaisesRegex(DiagnosticHold, "^unexpected_preloaded_module$"):
                diagnostic.bootstrap_command_policy(Path("unused-synthetic-root"))
            self.assertIs(sys.modules["console_codec"], sentinel)
        self.assertEqual(sys.path, previous)


class FinalOperationBudgetControls(unittest.TestCase):
    def test_slow_final_seed_identity_cannot_claim_clean_completion(self):
        clock = [0.0]

        def git(repo, *args, **kwargs):
            if args[-1] == "HEAD^{tree}":
                return diagnostic.OBSERVER_TREE
            clock[0] = 2.0
            return diagnostic.SEED_HEAD

        with mock.patch.object(diagnostic.time, "monotonic", side_effect=lambda: clock[0]):
            with self.assertRaisesRegex(DiagnosticHold, "^diagnostic_budget_expired$"):
                diagnostic.verify_final_identities(SimpleNamespace(require=diagnostic.require),
                                                   SimpleNamespace(git=git), Path("observer"), Path("seed"), 1.0)

    def test_slow_final_capture_emission_cannot_return_success(self):
        clock = [0.0]

        def slow_emit(*args, **kwargs):
            clock[0] = 2.0

        with mock.patch.object(diagnostic.time, "monotonic", side_effect=lambda: clock[0]), \
                mock.patch.object(diagnostic, "emit", side_effect=slow_emit), \
                mock.patch.object(Path, "open", mock.mock_open()), \
                mock.patch.dict(diagnostic.os.environ, {"GITHUB_OUTPUT": "synthetic-routing-file"}):
            with self.assertRaisesRegex(DiagnosticHold, "^diagnostic_budget_expired$"):
                diagnostic.complete_before_capture(Path("synthetic-capture"), 1.0)


class FailedStatusEvidenceControls(unittest.TestCase):
    def test_undecodable_retained_status_is_bounded_evidence_not_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            capture = root / "commands/command-0002/stdout.bin"
            capture.parent.mkdir(parents=True)
            capture.write_bytes(b"?? private-\xff\n")
            result = SimpleNamespace(stdout_path=str(capture), snapshot=SimpleNamespace(cleanup_verified=True))
            commands = SimpleNamespace(counter=2, owners=[SimpleNamespace(result=result)])
            output = io.StringIO()
            with redirect_stdout(output):
                diagnostic.emit_retained_status(commands, (2, 0), root, "unprimed", "failed_original_guard_capture")
            row = json.loads(output.getvalue())
            self.assertEqual(row["event"], "status")
            self.assertFalse(row["clean"])
            self.assertFalse(row["valid"])
            self.assertFalse(row["original_status_call_returned"])
            self.assertTrue(row["read_complete"])
            self.assertNotIn("private-", output.getvalue())

    def test_unrelated_last_command_is_not_reported_as_status(self):
        output = io.StringIO()
        with redirect_stdout(output):
            diagnostic.emit_retained_status(SimpleNamespace(counter=3, owners=[]), (2, 0),
                                            Path("unused-private-root"), "unprimed", "failed_original_guard_capture")
        self.assertEqual(json.loads(output.getvalue())["event"], "status_unread")


class ABOutcomeControls(unittest.TestCase):
    # Independently recorded seven-cache status from run 39511662886.
    baseline_status = """?? diagnostics/__pycache__/parallel_reader_capture.cpython-314.pyc
?? diagnostics/__pycache__/parallel_reader_diagnostics.cpython-314.pyc
?? diagnostics/__pycache__/parallel_reader_scheduler.cpython-314.pyc
?? diagnostics/__pycache__/windows_job_probe.cpython-314.pyc
?? tools/__pycache__/console_codec.cpython-314.pyc
?? tools/__pycache__/git_paths.cpython-314.pyc
?? tools/__pycache__/python_floor.cpython-314.pyc
"""

    def test_exact_baseline_hold_is_reproduction_not_clean_prefix(self):
        self.assertEqual(diagnostic.comparison_result("baseline", self.baseline_status,
                                                     "observer_not_clean", verified=True),
                         "baseline_reproduced")

    def test_clean_baseline_is_inconclusive_and_only_clean_candidate_passes(self):
        self.assertEqual(diagnostic.comparison_result("baseline", "", None, verified=True), "inconclusive")
        self.assertEqual(diagnostic.comparison_result("candidate", "", None, verified=True), "candidate_clean")
        for mode, status, reason, verified in (
                ("candidate", self.baseline_status, "observer_not_clean", True),
                ("baseline", self.baseline_status, "owned_command_failed", True),
                ("baseline", self.baseline_status, "observer_not_clean", False),
                ("candidate", "", None, False),
                ("candidate", "", "diagnostic_budget_expired", True),
                ("baseline", self.baseline_status + "?? private-path\n", "observer_not_clean", True),
                ("baseline", self.baseline_status.splitlines(keepends=True)[0] * 7, "observer_not_clean", True)):
            with self.subTest(mode=mode, reason=reason, verified=verified):
                self.assertEqual(diagnostic.comparison_result(mode, status, reason, verified=verified), "failed")


class IgnoreInputControls(unittest.TestCase):
    def test_baseline_requires_absence_candidate_requires_exact_pinned_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(diagnostic.verify_ignore_input(root, "baseline"), None)
            with self.assertRaisesRegex(DiagnosticHold, "^candidate_ignore_unavailable$"):
                diagnostic.verify_ignore_input(root, "candidate")
            (root / ".gitignore").write_bytes(b"synthetic\r\n")
            with self.assertRaisesRegex(DiagnosticHold, "^baseline_ignore_materialized$"):
                diagnostic.verify_ignore_input(root, "baseline")
            with self.assertRaisesRegex(DiagnosticHold, "^candidate_ignore_hash_mismatch$"):
                diagnostic.verify_ignore_input(root, "candidate")
            with mock.patch.object(diagnostic, "IGNORE_HASH", diagnostic.digest(b"synthetic\n")):
                self.assertEqual(diagnostic.verify_ignore_input(root, "candidate"), diagnostic.IGNORE_HASH)


class ABCommandControls(unittest.TestCase):
    def run_observation(self, mode, status, *, cleanup=True, final_error=False, job_elapsed=0):
        calls = []
        class Hold(RuntimeError):
            diagnostics = None
        def require(condition, reason):
            if not condition:
                raise Hold(reason)
        class Commands:
            counter = 0
            owners = []
            def git(self, repo, *args, **kwargs):
                self.counter += 1
                calls.append(args)
                if args[0] == "status":
                    return status if self.counter == 2 else ""
                if args[-1] == "HEAD^{tree}":
                    if final_error:
                        raise Hold("observer_tree_mismatch")
                    return diagnostic.OBSERVER_TREE
                return diagnostic.OBSERVER_HEAD if self.counter == 1 else diagnostic.SEED_HEAD
            def cleanup(self):
                return cleanup
        original = SimpleNamespace(
            Hold=Hold, require=require, OwnedCommands=lambda root: Commands(),
            environment_preflight=lambda: None, reviewed_budget=lambda *a: None,
            corpus_preflight=lambda *a: None, sha=diagnostic.digest,
            normalized=lambda path: b"synthetic-suite", SUITE_PATH="suite.py", outside=lambda *a: True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observer, seed = root / "observer", root / "seed"
            for path, head in ((observer, diagnostic.OBSERVER_HEAD), (seed, diagnostic.SEED_HEAD)):
                (path / ".git").mkdir(parents=True)
                (path / ".git/HEAD").write_text(head)
            if mode == "candidate":
                (observer / ".gitignore").write_bytes(b"synthetic-ignore\n")
            helper_head = Path(diagnostic.__file__).resolve().parent.parent / ".git/HEAD"
            output_file = root / "routing"
            output_file.touch()
            stream = io.StringIO()
            with mock.patch.object(diagnostic, "load_original", return_value=original), \
                    mock.patch.object(diagnostic, "os", SimpleNamespace(name="nt", environ=diagnostic.os.environ)), \
                    mock.patch.object(diagnostic.platform, "python_version", return_value="3.14.4"), \
                    mock.patch.object(diagnostic, "IGNORE_HASH", diagnostic.digest(b"synthetic-ignore\n")), \
                    mock.patch.object(diagnostic, "CANDIDATE_HASH", diagnostic.digest(b"synthetic-suite")), \
                    mock.patch.dict(diagnostic.os.environ, {"GITHUB_SHA": helper_head.read_text().strip(),
                        "GITHUB_RUN_ATTEMPT": "1", "GITHUB_REF": diagnostic.BRANCH,
                        "RUNNER_TEMP": str(root), "GITHUB_OUTPUT": str(output_file)}), redirect_stdout(stream):
                code = diagnostic.main(["--mode", mode, "--observer", str(observer), "--seed", str(seed),
                                        "--job-start-epoch", str(time.time() - job_elapsed)])
            return code, [json.loads(line) for line in stream.getvalue().splitlines()], output_file.read_text(), calls

    def test_baseline_cli_retains_original_hold_and_publishes_reproduction_receipt(self):
        code, rows, routing, calls = self.run_observation("baseline", ABOutcomeControls.baseline_status)
        self.assertEqual(code, 0)
        self.assertEqual(calls[:2], [("rev-parse", "HEAD"), ("status", "--porcelain=v1", "--untracked-files=all")])
        self.assertTrue(any(row.get("reason") == "observer_not_clean" for row in rows))
        receipt = next(row for row in rows if row["event"] == "diagnostic_stop")
        self.assertFalse(receipt["prefix_clean"])
        self.assertEqual(receipt["comparison_result"], "baseline_reproduced")
        self.assertEqual(routing, "comparison_result=baseline_reproduced\n")

    def test_candidate_refuses_when_checkout_consumed_full_observation_margin(self):
        code, rows, routing, calls = self.run_observation("candidate", "", job_elapsed=421)
        self.assertEqual(code, 2)
        self.assertEqual(calls, [])
        self.assertEqual(routing, "")
        self.assertTrue(any(row.get("reason") == "second_observation_budget_unavailable" for row in rows))

    def test_candidate_cli_passes_only_with_clean_guard_and_verified_finish(self):
        code, rows, routing, calls = self.run_observation("candidate", "")
        self.assertEqual(code, 0)
        self.assertEqual(calls[:2], [("rev-parse", "HEAD"), ("status", "--porcelain=v1", "--untracked-files=all")])
        self.assertEqual(routing, "comparison_result=candidate_clean\n")
        receipt = next(row for row in rows if row["event"] == "diagnostic_stop")
        self.assertTrue(receipt["prefix_clean"])
        self.assertEqual(receipt["comparison_result"], "candidate_clean")
        for mode, status, cleanup, final_error in (
                ("baseline", "", True, False),
                ("candidate", ABOutcomeControls.baseline_status, True, False),
                ("baseline", ABOutcomeControls.baseline_status, False, False),
                ("baseline", ABOutcomeControls.baseline_status, True, True),
                ("candidate", "", False, False),
                ("candidate", "", True, True)):
            with self.subTest(mode=mode, cleanup=cleanup, final_error=final_error):
                code, rows, routing, _ = self.run_observation(mode, status, cleanup=cleanup, final_error=final_error)
                self.assertEqual(code, 2)
                self.assertEqual(routing, "")


class ABWorkflowControls(unittest.TestCase):
    def test_two_unprimed_checkouts_differ_only_by_pinned_ignore_input(self):
        workflow = (Path(__file__).resolve().parent.parent / ".github/workflows/ci-parallel-proof.yml").read_text()
        self.assertNotIn("--mode status-primed", workflow)
        self.assertNotIn("--mode capture-before", workflow)
        self.assertIn("--mode baseline", workflow)
        self.assertIn("--mode candidate", workflow)
        self.assertIn("timeout-minutes: 10", workflow)
        self.assertIn("if: github.run_attempt == 1", workflow)
        self.assertIn("BASELINE_RESULT: ${{ steps.baseline.outputs.comparison_result }}", workflow)
        self.assertIn("CANDIDATE_RESULT: ${{ steps.candidate.outputs.comparison_result }}", workflow)
        self.assertIn("$env:BASELINE_RESULT -ne 'baseline_reproduced'", workflow)
        self.assertIn("$env:CANDIDATE_RESULT -ne 'candidate_clean'", workflow)
        blocks = workflow.split("      - name:")
        observer_blocks = [block for block in blocks if "ref: 96a8c794b71184881fbaa9b3df471fecf2f9b331" in block]
        self.assertEqual(len(observer_blocks), 2)
        first, second = observer_blocks
        def options(block):
            return [line for line in block.split("        with:")[1].splitlines()
                    if "path: observer" not in line and line.strip() != "/.gitignore"]
        self.assertEqual(options(first), options(second))
        self.assertNotIn("/.gitignore", first)
        self.assertIn("/.gitignore", second)


if __name__ == "__main__":
    try:
        diagnostic.bootstrap_command_policy()
    except Exception as error:
        diagnostic.emit_hold(error, "command_policy", None, None)
        raise SystemExit(2)
    unittest.main()
