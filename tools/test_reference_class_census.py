"""Public-contract tests for the cross-checkout reference-class census."""

from __future__ import annotations

import ast
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import reference_class_census as census
import reference_scan

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_MEMBER = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"


def document(entry: str, citation: str) -> str:
    return f"# Case\n\n{citation}\n\n## Reference\n\n{entry}\n"


COCHRANE = (
    "Laver, K. E., Lange, B., George, S., Deutsch, J. E., Saposnik, G., "
    "Chapman, M., & Crotty, M. (2025). Virtual reality for stroke rehabilitation. "
    "*Cochrane Database of Systematic Reviews*. "
    "https://doi.org/10.1002/14651858.CD008349.pub5"
)
LEGAL = (
    "Payment for nurse practitioners' and clinical nurse specialists' services, "
    "42 C.F.R. § 414.56 (2026)."
)


class TheCensusWalksTheRuledAsymmetricPopulation(unittest.TestCase):
    def test_every_registered_scratch_root_and_main_output_are_read(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            main = base / "main"
            worktree = base / "worktree"
            for root in (main, worktree):
                (root / "scratch").mkdir(parents=True)
            output = main / "output"
            output.mkdir()

            (main / "scratch" / "a.md").write_text(
                document(LEGAL, "42 C.F.R. § 414.56 (2026)."), encoding="utf-8"
            )
            (worktree / "scratch" / "b.md").write_text(
                document(COCHRANE, "Laver et al. (2025)."), encoding="utf-8"
            )
            (output / "c.md").write_text(
                document(LEGAL, "42 C.F.R. § 414.56 (2026)."), encoding="utf-8"
            )

            with (
                patch.object(census.scratch_census, "worktree_roots", return_value=(main, worktree)),
                patch.object(census.repo_root, "output_root", return_value=output),
            ):
                result = census.scan_corpus(worktree)

        self.assertEqual(result.checkouts, 2)
        self.assertEqual(result.roots_read, 3)
        self.assertEqual(result.roots_unreadable, 0)
        self.assertEqual(result.text_files, 3)
        self.assertEqual(result.candidate_documents, 3)
        self.assertEqual(result.documents, 3)
        self.assertEqual(result.documents_unreadable, 0)
        self.assertEqual(result.entries, 3)
        populations = {item.name: item.population for item in result.bucket_counts}
        self.assertEqual(populations["legal"], 2)
        self.assertEqual(populations["cochrane"], 1)

    def test_repo_root_scratch_root_is_not_the_population(self):
        source = Path(census.__file__).read_text(encoding="utf-8")
        calls = {
            (node.func.value.id, node.func.attr)
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
        }
        self.assertNotIn(("repo_root", "scratch_root"), calls)
        self.assertIn(("scratch_census", "worktree_roots"), calls)


class TheExtractorCoverageHasAnIndependentPopulation(unittest.TestCase):
    def test_one_real_committed_member_is_read(self):
        result = census.read_text_file(REAL_MEMBER)
        self.assertTrue(result.candidate)
        self.assertIsNotNone(result.document)
        self.assertFalse(result.unreadable)

    def test_a_heading_with_zero_entries_is_an_unreadable_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "partial.md"
            path.write_text("# Case\n\n## References\n", encoding="utf-8")
            result = census.read_text_file(path)

        self.assertTrue(result.candidate)
        self.assertIsNone(result.document)
        self.assertTrue(result.unreadable)

    def test_a_wrong_but_extractable_heading_stays_in_the_population(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-heading.md"
            path.write_text("# Case\n\n## Literature Cited\n", encoding="utf-8")
            result = census.read_text_file(path)

        self.assertTrue(result.candidate)
        self.assertIsNone(result.document)
        self.assertTrue(result.unreadable)

    def test_reference_ranges_is_not_a_reference_list_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ranges.md"
            path.write_text(
                "# Lab guide\n\n## Reference Ranges\n\nSodium: 135–145 mEq/L\n",
                encoding="utf-8",
            )
            result = census.read_text_file(path)

        self.assertFalse(result.candidate)
        self.assertIsNone(result.document)
        self.assertFalse(result.unreadable)

    def test_the_renderers_plural_prefix_heading_stays_in_the_population(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plural-prefix.md"
            path.write_text(
                document(LEGAL, "42 C.F.R. § 414.56 (2026).").replace(
                    "## Reference", "## References and Resources"
                ),
                encoding="utf-8",
            )
            result = census.read_text_file(path)

        self.assertTrue(result.candidate)
        self.assertIsNotNone(result.document)
        self.assertFalse(result.unreadable)


class TheCensusReportIsCountsOnlyAndHasAHouseExit(unittest.TestCase):
    def run_main(self, roots: tuple[Path, ...], output: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(census.scratch_census, "worktree_roots", return_value=roots),
            patch.object(census.repo_root, "output_root", return_value=output),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = census.main([])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_completed_count_is_zero_and_report_names_no_corpus_text(self):
        marker = "private-corpus-marker"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            scratch.mkdir()
            output = root / "output"
            output.mkdir()
            (scratch / "case.md").write_text(
                document(COCHRANE + marker, "Laver et al. (2025)."), encoding="utf-8"
            )
            status, stdout, _ = self.run_main((root,), output)

        self.assertEqual(status, 0)
        self.assertNotIn(marker, stdout)
        self.assertIn("checkouts enumerated", stdout)
        self.assertIn("roots read", stdout)
        self.assertIn("roots unreadable", stdout)
        self.assertIn("reference-list candidates", stdout)
        self.assertIn("candidate documents unreadable", stdout)
        for bucket in reference_scan.REFERENCE_BUCKETS:
            self.assertIn(bucket.name, stdout)
            self.assertIn(bucket.state, stdout)
        self.assertNotIn("uncovered-class", stdout)

    def test_the_census_has_no_exit_one_path(self):
        source = Path(census.__file__).read_text(encoding="utf-8")
        module = ast.parse(source)
        main = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        returns = [
            node.value
            for node in ast.walk(main)
            if isinstance(node, ast.Return) and node.value is not None
        ]
        self.assertFalse(
            any(
                isinstance(node, ast.Constant) and node.value == 1
                for returned in returns
                for node in ast.walk(returned)
            )
        )

    def test_clean_is_zero_and_unreadable_is_two(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scratch").mkdir()
            output = root / "output"
            output.mkdir()
            (root / "scratch" / "case.md").write_text(
                document(LEGAL, "42 C.F.R. § 414.56 (2026)."), encoding="utf-8"
            )
            clean, _, _ = self.run_main((root,), output)
            with patch.object(census, "read_root", side_effect=OSError("denied")):
                not_scanned, stdout, stderr = self.run_main((root,), output)

        self.assertEqual(clean, 0)
        self.assertEqual(not_scanned, 2)
        self.assertIn("roots unreadable", stdout)
        self.assertIn("NOT SCANNED", stderr)

    def test_a_partial_match_is_exit_two_and_reports_the_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            scratch.mkdir()
            output = root / "output"
            output.mkdir()
            (scratch / "partial.md").write_text(
                "# Case\n\n## References\n", encoding="utf-8"
            )
            status, stdout, stderr = self.run_main((root,), output)

        self.assertEqual(status, 2)
        self.assertIn("reference-list candidates         1", stdout)
        self.assertIn("candidate documents unreadable    1", stdout)
        self.assertIn("NOT SCANNED", stderr)

    def test_show_does_not_exist(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(census.main(["--show"]), 2)
        self.assertEqual(stderr.getvalue().strip(), census.USAGE)

    def test_module_states_both_inherited_population_limits(self):
        self.assertIn("separate clone", census.__doc__)
        self.assertIn("outside every checkout", census.__doc__)


if __name__ == "__main__":
    unittest.main()
