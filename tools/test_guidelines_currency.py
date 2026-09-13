"""Public-contract tests for the guideline edition-currency registry."""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "guidelines_currency.py"
sys.path.insert(0, str(ROOT / "tools"))

import artifact_lock_test_support  # noqa: E402, F401
import guidelines_currency as currency  # noqa: E402


CATALOG = """| society | filename | title | topic | population | year | page_count | class | citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADA | diabetes.pdf | Diabetes | diabetes | adult | 2026 | 2 | guideline | ? |
| AHA ACC | old.pdf | Old | cholesterol | adult | 2018 | 3 | guideline | 10.1000/old |
| AHA ACC | new.pdf | New | dyslipidemia | adult | 2026 | 4 | guideline | 10.1000/new |
"""


def registry(*documents: str, society_observed: str = "2026-09-05") -> str:
    ada = currency.SOCIETY_INDEXES["ADA"]
    aha = currency.SOCIETY_INDEXES["AHA ACC"]
    return f"""# Guideline edition currency

{currency.SCHEMA_MARKER}

## Society indexes

| society | index | reader | join key | access | last observed | state | state observed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADA | {ada[0]} | {ada[1]} | {ada[2]} | {ada[3]} | {society_observed} | read |  |
| AHA ACC | {aha[0]} | {aha[1]} | {aha[2]} | {aha[3]} | {society_observed} | read |  |

## Documents

| filename | society | join value | verdict | observed | superseded by |
| --- | --- | --- | --- | --- | --- |
{"".join(documents)}"""


class RegistryBind(unittest.TestCase):
    def audit(self, text: str):
        rows, _, catalog_problems = currency.guidelines_catalog.parse_catalog(CATALOG)
        self.assertEqual(catalog_problems, [])
        parsed = currency.parse_registry(text)
        return currency.audit(rows, parsed, today=date(2026, 9, 5))

    def test_grades_both_catalog_bind_directions_and_supersession_target(self):
        result = self.audit(
            registry(
                "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
                "| old.pdf | AHA ACC | 10.1000/old | superseded | 2026-09-05 | new.pdf |\n",
                "| ghost.pdf | AHA ACC | 10.1000/ghost | current | 2026-09-05 |  |\n",
            )
        )
        self.assertIn("catalog document 'new.pdf' has no currency row", result.failures)
        self.assertIn("currency row 'ghost.pdf' names no catalog document", result.failures)

    def test_stale_annual_observation_is_report_only(self):
        result = self.audit(
            registry(
                "| diabetes.pdf | ADA | dc26-srev | current | 2025-01-01 |  |\n",
                "| old.pdf | AHA ACC | 10.1000/old | current |  |  |\n",
                "| new.pdf | AHA ACC | 10.1000/new | current |  |  |\n",
                society_observed="2025-01-01",
            )
        )
        self.assertEqual(result.failures, ())
        self.assertTrue(any("ADA" in item and "publication cycle" in item for item in result.findings))

    def test_malformed_and_unruled_document_rows_refuse(self):
        result = self.audit(
            registry(
                "| diabetes.pdf | ADA | dc26-srev | maybe | 2026-09-05 |  |\n",
                "| old.pdf | AHA ACC | 10.1000/old | current | 2026-02-30 |  |\n",
                "| new.pdf | AHA ACC | 10.1000/new | current |  | extra |\n",
            )
        )
        self.assertGreaterEqual(len(result.failures), 3)

    def test_society_reader_contract_cannot_drift_from_the_ruled_route(self):
        text = registry(
            "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
            "| old.pdf | AHA ACC | 10.1000/old | current |  |  |\n",
            "| new.pdf | AHA ACC | 10.1000/new | current |  |  |\n",
        ).replace("| ada |", "| invented-reader |", 1)
        result = self.audit(text)
        self.assertTrue(any("reader" in failure and "ruled contract" in failure for failure in result.failures))

    def test_annual_cycle_ages_even_when_the_new_edition_is_not_in_the_catalog(self):
        older_catalog = CATALOG.replace("| 2026 | 2 |", "| 2025 | 2 |", 1)
        rows, _, problems = currency.guidelines_catalog.parse_catalog(older_catalog)
        self.assertEqual(problems, [])
        parsed = currency.parse_registry(
            registry(
                "| diabetes.pdf | ADA | dc25-srev | current | 2025-09-05 |  |\n",
                "| old.pdf | AHA ACC | 10.1000/old | current |  |  |\n",
                "| new.pdf | AHA ACC | 10.1000/new | current |  |  |\n",
                society_observed="2025-09-05",
            )
        )
        early = currency.audit(rows, parsed, today=date(2026, 1, 1))
        self.assertFalse(any("ADA" in item and "publication cycle" in item for item in early.findings))
        due = currency.audit(rows, parsed, today=date(2026, 9, 5))
        self.assertTrue(any("ADA" in item and "publication cycle" in item for item in due.findings))


class ReaderCoverage(unittest.TestCase):
    def test_declared_limits_name_the_unreachable_claims(self):
        self.assertEqual(
            {row[0] for row in currency.DECLARED_LIMITS},
            {
                "publisher completeness",
                "agent capture provenance",
                "download identity",
                "different lock roots",
                "unguarded editors and git operations",
                "separate checkouts",
                "writer-walk indirection",
            },
        )

    def test_all_nine_society_readers_are_declared(self):
        self.assertEqual(
            set(currency.SOCIETY_INDEXES),
            {"ACIP", "ADA", "AHA ACC", "CDC", "GINA", "GOLD", "IDSA", "KDIGO", "USPSTF"},
        )
        self.assertEqual(set(currency.SOCIETY_COVERAGE), set(currency.SOCIETY_INDEXES))

    def test_empty_200_is_not_a_successful_empty_read(self):
        with self.assertRaisesRegex(currency.ReadError, "no guideline content"):
            currency.read_society_index("IDSA", "<html><body>Loading...</body></html>")

    def test_reader_names_denominator_and_unread_remainder(self):
        html = """
        <a href='https://doi.org/10.1000/one'>Practice guideline one</a>
        <a href='/guideline/two'>Practice guideline two without DOI</a>
        """
        result = currency.read_society_index("IDSA", html)
        self.assertEqual(result.denominator, 2)
        self.assertEqual(result.join_values, ("10.1000/one",))
        self.assertEqual(result.unread, 1)

    def test_detectable_pagination_cannot_report_a_clean_whole(self):
        html = """
        <a href='https://doi.org/10.1000/one'>Practice guideline one</a>
        <a rel='next' href='?page=2'>Next</a>
        """
        result = currency.read_society_index("IDSA", html)
        self.assertEqual(result.denominator, 2)
        self.assertEqual(result.join_values, ("10.1000/one",))
        self.assertEqual(result.unread, 1)

    def test_doi_reader_follows_each_counted_index_entry(self):
        html = """
        <a href='/guideline/one'>Practice guideline one</a>
        <a href='/guideline/two'>Practice guideline two</a>
        """
        pages = {
            "https://example.invalid/guideline/one": "DOI 10.1000/one",
            "https://example.invalid/guideline/two": "no DOI here",
        }
        result = currency.follow_doi_links(
            "IDSA", html, "https://example.invalid/index", pages.__getitem__
        )
        self.assertEqual(result.denominator, 2)
        self.assertEqual(result.join_values, ("10.1000/one",))
        self.assertEqual(result.unread, 1)

    def test_index_comparison_answers_both_join_directions(self):
        documents = (
            currency.DocumentEntry("one.pdf", "IDSA", "10.1000/one", "current", "", "", 1),
            currency.DocumentEntry("old.pdf", "IDSA", "10.1000/old", "current", "", "", 2),
        )
        result = currency.ReaderResult(
            "IDSA", 2, ("10.1000/one", "10.1000/new"), 0
        )
        comparison = currency.compare_index(documents, result)
        self.assertEqual(comparison.matched, ("one.pdf",))
        self.assertEqual(comparison.corpus_absent, ("old.pdf",))
        self.assertEqual(comparison.publisher_additions, ("10.1000/new",))


class CommandContract(unittest.TestCase):
    def test_hook_reports_unconditionally_and_grades_staged_registry(self):
        hook = (ROOT / "tools" / "hooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('guidelines_currency.py" --hook-summary >&2 || true', hook)
        self.assertIn(
            "guidelines-(catalog|currency|catalog-audit)\\.md|thresholds/coverage\\.md",
            hook,
        )
        self.assertIn('guidelines_currency.py" >&2 || status=1', hook)

    def test_every_module_write_goes_through_the_atomic_helper(self):
        tree = ast.parse(COMMAND.read_text(encoding="utf-8"))
        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent

        def enclosing_functions(node: ast.AST) -> set[str]:
            names = set()
            while node in parents:
                node = parents[node]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(node.name)
            return names

        direct_writes = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "write_text",
                "write_bytes",
            }:
                direct_writes.append((node.lineno, enclosing_functions(node)))
            mode = None
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                mode = node.args[1] if len(node.args) > 1 else None
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "open":
                mode = node.args[0] if node.args else None
            if mode is None:
                mode = next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "mode"),
                    None,
                )
            if (
                isinstance(mode, ast.Constant)
                and any(flag in str(mode.value) for flag in "wax+")
            ):
                direct_writes.append((node.lineno, enclosing_functions(node)))
        self.assertTrue(direct_writes)
        self.assertTrue(
            all("_replace_file" in owners for _, owners in direct_writes),
            direct_writes,
        )

    def test_hook_grades_an_audit_or_coverage_change_on_its_own(self):
        shell = shutil.which("sh")
        git = shutil.which("git")
        if not shell or not git:
            self.skipTest("the hook contract needs sh and git")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / "tools"
            (tools / "hooks").mkdir(parents=True)
            (root / "reference" / "thresholds").mkdir(parents=True)
            shutil.copy2(ROOT / "tools" / "hooks" / "pre-commit", tools / "hooks" / "pre-commit")
            marker = root / "currency-ran"
            (tools / "guidelines_currency.py").write_text(
                "import os, pathlib, sys\n"
                "if '--hook-summary' not in sys.argv:\n"
                "    pathlib.Path(os.environ['CURRENCY_HOOK_MARKER']).write_text('ran')\n",
                encoding="utf-8",
            )
            for name in (
                "skills_mirror.py",
                "spelling_scan.py",
                "guidelines_catalog.py",
                "threshold_coverage.py",
                "subject_ledger.py",
                "scratch_census.py",
                "phi_scan.py",
            ):
                (tools / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
            subprocess.run([git, "init", "--quiet"], cwd=root, check=True)
            subprocess.run(
                [git, "config", "user.email", "test@example.invalid"], cwd=root, check=True
            )
            subprocess.run(
                [git, "config", "user.name", "Currency Test"], cwd=root, check=True
            )
            subprocess.run(
                [git, "commit", "--allow-empty", "--quiet", "-m", "base"],
                cwd=root,
                check=True,
            )
            environment = {**os.environ, "CURRENCY_HOOK_MARKER": str(marker)}
            for staged in (
                root / "reference" / "guidelines-catalog-audit.md",
                root / "reference" / "thresholds" / "coverage.md",
            ):
                with self.subTest(staged=staged.name):
                    marker.unlink(missing_ok=True)
                    staged.write_text("changed\n", encoding="utf-8")
                    subprocess.run([git, "add", "--", str(staged)], cwd=root, check=True)
                    completed = subprocess.run(
                        [shell, str(tools / "hooks" / "pre-commit")],
                        cwd=root,
                        env=environment,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(marker.read_text(encoding="utf-8"), "ran")
                    subprocess.run(
                        [git, "commit", "--quiet", "-m", staged.name],
                        cwd=root,
                        check=True,
                    )

    def test_draft_writes_one_row_per_catalog_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "catalog.md"
            output = root / "currency.md"
            catalog.write_text(CATALOG, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(COMMAND), "--catalog", str(catalog), "--draft", str(output)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            parsed = currency.parse_registry(output.read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.documents), 3)
        self.assertEqual({row.filename for row in parsed.documents}, {"diabetes.pdf", "old.pdf", "new.pdf"})
        self.assertTrue(all(row.state == "unread" for row in parsed.societies))
        self.assertTrue(all(not row.last_observed for row in parsed.societies))
        self.assertTrue(all(not row.state_observed for row in parsed.societies))

    def test_missing_input_is_not_graded(self):
        completed = subprocess.run(
            [sys.executable, str(COMMAND), "--registry", "does-not-exist.md"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("NOT GRADED", completed.stderr)

    def test_superseded_document_does_not_make_command_refuse(self):
        text = registry(
            "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
            "| old.pdf | AHA ACC | 10.1000/old | superseded | 2026-09-05 | new.pdf |\n",
            "| new.pdf | AHA ACC | 10.1000/new | current | 2026-09-05 |  |\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "catalog.md"
            registry_path = root / "currency.md"
            catalog.write_text(CATALOG, encoding="utf-8")
            registry_path.write_text(text, encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--registry",
                    str(registry_path),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("superseded 1", completed.stdout)
        self.assertIn("societies 2", completed.stdout)

    def test_read_stamps_only_documents_matched_on_the_society_index(self):
        text = registry(
            "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
            "| old.pdf | AHA ACC | 10.1000/old | current | 2025-01-01 |  |\n",
            "| new.pdf | AHA ACC | 10.1000/new | absent |  |  |\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = root / "catalog.md"
            registry_path = root / "currency.md"
            capture = root / "aha.html"
            catalog.write_text(CATALOG, encoding="utf-8")
            registry_path.write_text(text, encoding="utf-8")
            capture.write_text(
                "<a href='https://doi.org/10.1000/new'>New guideline</a>",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--registry",
                    str(registry_path),
                    "--read",
                    "AHA-ACC",
                    "--capture",
                    f"AHA-ACC={capture}",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            updated = currency.parse_registry(registry_path.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("corpus absent: old.pdf", completed.stdout)
        rows = {row.filename: row for row in updated.documents}
        self.assertEqual(rows["new.pdf"].verdict, "current")
        self.assertEqual(rows["new.pdf"].observed, date.today().isoformat())
        self.assertEqual(rows["old.pdf"].verdict, "current")
        self.assertEqual(rows["old.pdf"].observed, "2025-01-01")

    def test_read_reapplies_matches_to_the_registry_text_under_the_lock(self):
        text = registry(
            "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
            "| old.pdf | AHA ACC | 10.1000/old | current | 2025-01-01 |  |\n",
            "| new.pdf | AHA ACC | 10.1000/new | absent |  |  |\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "currency.md"
            capture = root / "aha.html"
            registry_path.write_text(text, encoding="utf-8")
            capture.write_text(
                "<a href='https://doi.org/10.1000/new'>New guideline</a>",
                encoding="utf-8",
            )
            parsed = currency.parse_registry(text)
            registry_path.write_text(
                text.replace("2025-01-01", "2026-01-02"), encoding="utf-8"
            )
            args = mock.Mock(
                read=["AHA-ACC"],
                capture=[f"AHA-ACC={capture}"],
                registry=registry_path,
                verbose=False,
            )
            self.assertEqual(currency._run_reads(args, parsed), 0)
            updated = currency.parse_registry(registry_path.read_text(encoding="utf-8"))

        rows = {row.filename: row for row in updated.documents}
        self.assertEqual(rows["old.pdf"].observed, "2026-01-02")
        self.assertEqual(rows["new.pdf"].observed, date.today().isoformat())

    def test_read_busy_refusal_names_owner_artifact_and_lost_societies(self):
        text = registry(
            "| diabetes.pdf | ADA | dc26-srev | current |  |  |\n",
            "| old.pdf | AHA ACC | 10.1000/old | current | 2025-01-01 |  |\n",
            "| new.pdf | AHA ACC | 10.1000/new | absent |  |  |\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "currency.md"
            capture = root / "aha.html"
            ada_capture = root / "ada.html"
            registry_path.write_text(text, encoding="utf-8")
            capture.write_text("captured", encoding="utf-8")
            ada_capture.write_text("captured", encoding="utf-8")
            args = mock.Mock(
                read=["AHA-ACC", "ADA"],
                capture=[f"AHA-ACC={capture}", f"ADA={ada_capture}"],
                registry=registry_path,
                verbose=False,
            )
            busy = currency.artifact_lock.ArtifactBusy(
                f"another task owns {registry_path} (reader, process 42)"
            )
            reads = {
                "AHA ACC": currency.ReaderResult(
                    "AHA ACC", 1, ("10.1000/new",), 0
                ),
                "ADA": currency.ReaderResult("ADA", 1, ("not-a-match",), 0),
            }
            with mock.patch.object(
                currency,
                "read_society_index",
                side_effect=lambda society, _content: reads[society],
            ), mock.patch.object(
                currency.artifact_lock, "hold", side_effect=busy
            ), mock.patch.object(
                currency.time, "monotonic", side_effect=[0.0, 2.0]
            ):
                with self.assertRaises(currency.ReadError) as raised:
                    currency._run_reads(args, currency.parse_registry(text))

        message = str(raised.exception)
        self.assertIn(str(registry_path), message)
        self.assertIn("process 42", message)
        self.assertIn("lost society reads: AHA-ACC", message)
        self.assertNotIn("lost society reads: AHA-ACC, ADA", message)


class FetchBoundary(unittest.TestCase):
    def handoff_files(self, root: Path) -> tuple[Path, Path, Path, Path]:
        catalog = root / "catalog.md"
        registry_path = root / "currency.md"
        coverage = root / "coverage.md"
        audit = root / "audit.md"
        catalog.write_text(
            "| society | filename | title | topic | population | year | page_count | class | citation |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| KDIGO | old.pdf | Old | lipids | adult | 2013 | 1 | guideline | 10.1000/old |\n"
            "| KDIGO | new.pdf | New | ckd | adult | 2024 | 1 | guideline | 10.1000/new |\n",
            encoding="utf-8",
        )
        route = currency.SOCIETY_INDEXES["KDIGO"]
        registry_path.write_text(
            f"# Currency\n\n{currency.SCHEMA_MARKER}\n\n## Society indexes\n\n"
            "| society | index | reader | join key | access | last observed | state | state observed |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            f"| KDIGO | {route[0]} | {route[1]} | {route[2]} | {route[3]} | 2026-09-05 | read |  |\n\n"
            "## Documents\n\n"
            "| filename | society | join value | verdict | observed | superseded by |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| old.pdf | KDIGO | 10.1000/old | superseded | 2026-09-05 | new.pdf |\n"
            "| new.pdf | KDIGO | 10.1000/new | current | 2026-09-05 |  |\n",
            encoding="utf-8",
        )
        coverage.write_text(
            "| topic | subject | state | artifact | record |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| lipids | lipids | sheet | topic.md | prior |\n",
            encoding="utf-8",
        )
        audit.write_text(
            "## Documents\n\n"
            "| society | filename | sha256 | bytes | audited |\n"
            "| --- | --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        return catalog, registry_path, coverage, audit

    def test_html_response_is_not_accepted_as_a_guideline_pdf(self):
        with self.assertRaisesRegex(currency.ReadError, "not a PDF"):
            currency.validate_pdf_bytes(b"<html>Just a moment...</html>")

    def test_fetch_refuses_a_corpus_root_inside_a_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            with mock.patch.object(currency, "download_bytes", return_value=b"pdf"):
                with self.assertRaisesRegex(ValueError, "refusing to write inside a git checkout"):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf",
                        "KDIGO/new.pdf",
                        root / "corpus",
                        root / "coverage.md",
                        "lipids",
                        "old.pdf",
                        root / "audit.md",
                    )

    def test_fetch_records_digest_and_never_edits_a_sheet(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "corpus"
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            sheet = root / "topic.md"
            sheet.write_text("old sheet bytes", encoding="utf-8")
            before = sheet.read_bytes()
            with mock.patch.object(currency, "download_bytes", return_value=payload), mock.patch.object(
                currency, "run_guidelines_build"
            ) as build, mock.patch.object(currency, "run_catalog_check") as catalog_check, mock.patch.object(
                currency, "run_coverage_check"
            ) as coverage_check:
                record = currency.fetch_replacement(
                    "https://example.invalid/new.pdf",
                    "KDIGO/new.pdf",
                    corpus,
                    coverage,
                    "lipids",
                    "old.pdf",
                    audit,
                    catalog,
                    registry_path,
                )
            self.assertEqual(sheet.read_bytes(), before)
            self.assertEqual(record.sha256, "8db6673ffd1a5cc0b9e0a05881c2364eda5d97c5750d8810d63e0a473510ddb4")
            self.assertIn("| lipids | lipids | unread | topic.md | superseded old.pdf by KDIGO/new.pdf;", coverage.read_text(encoding="utf-8"))
            self.assertIn(
                f"| KDIGO | new.pdf | {record.sha256} | {len(payload)} | {record.fetched} |",
                audit.read_text(encoding="utf-8"),
            )
            resolved_corpus = corpus.resolve()
            build.assert_called_once_with(resolved_corpus)
            catalog_check.assert_called_once_with(resolved_corpus, catalog, audit)
            coverage_check.assert_called_once_with(catalog, coverage)

    def test_fetch_preflights_the_catalog_handoff_before_downloading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            catalog.write_text(catalog.read_text(encoding="utf-8").replace("| KDIGO | new.pdf", "| KDIGO | other.pdf"), encoding="utf-8")
            with mock.patch.object(currency, "download_bytes") as download:
                with self.assertRaisesRegex(ValueError, "catalog has no replacement"):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )
            download.assert_not_called()

    def test_failed_rebuild_removes_received_bytes_without_mutating_tracked_files(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            coverage_before = coverage.read_bytes()
            audit_before = audit.read_bytes()
            with mock.patch.object(currency, "download_bytes", return_value=payload), mock.patch.object(
                currency, "run_guidelines_build", side_effect=subprocess.CalledProcessError(1, ["build"])
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )
            self.assertFalse((root / "corpus" / "KDIGO" / "new.pdf").exists())
            self.assertEqual(coverage.read_bytes(), coverage_before)
            self.assertEqual(audit.read_bytes(), audit_before)

    def test_failed_build_does_not_revert_concurrent_tracked_edits(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)

            def edit_tracked_files(_corpus: Path) -> None:
                audit.write_text(
                    audit.read_text(encoding="utf-8") + "concurrent audit edit\n",
                    encoding="utf-8",
                )
                coverage.write_text(
                    coverage.read_text(encoding="utf-8") + "concurrent coverage edit\n",
                    encoding="utf-8",
                )
                raise subprocess.CalledProcessError(1, ["build"])

            with mock.patch.object(
                currency, "download_bytes", return_value=payload
            ), mock.patch.object(
                currency, "run_guidelines_build", side_effect=edit_tracked_files
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )
            self.assertIn("concurrent audit edit", audit.read_text(encoding="utf-8"))
            self.assertIn(
                "concurrent coverage edit", coverage.read_text(encoding="utf-8")
            )

    def test_keyboard_interrupt_during_build_removes_pdf_and_receipt(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            destination = root / "corpus" / "KDIGO" / "new.pdf"
            sidecar = destination.with_suffix(".pdf.fetch.json")
            with mock.patch.object(
                currency, "download_bytes", return_value=payload
            ), mock.patch.object(
                currency, "run_guidelines_build", side_effect=KeyboardInterrupt
            ):
                with self.assertRaises(KeyboardInterrupt):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf",
                        "KDIGO/new.pdf",
                        root / "corpus",
                        coverage,
                        "lipids",
                        "old.pdf",
                        audit,
                        catalog,
                        registry_path,
                    )
            self.assertFalse(destination.exists())
            self.assertFalse(sidecar.exists())

    def test_fetch_refuses_when_the_destination_lands_during_download(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        competing = b"%PDF-1.7\ncompeting fetch"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            destination = root / "corpus" / "KDIGO" / "new.pdf"

            def land_competing_fetch(_url: str) -> bytes:
                destination.parent.mkdir(parents=True)
                destination.write_bytes(competing)
                return payload

            with mock.patch.object(
                currency, "download_bytes", side_effect=land_competing_fetch
            ):
                with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf",
                        "KDIGO/new.pdf",
                        root / "corpus",
                        coverage,
                        "lipids",
                        "old.pdf",
                        audit,
                        catalog,
                        registry_path,
                    )
            self.assertEqual(destination.read_bytes(), competing)

    def test_existing_pdf_without_a_matching_receipt_is_refused(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            destination = root / "corpus" / "KDIGO" / "new.pdf"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(payload)
            with mock.patch.object(currency, "download_bytes") as download:
                with self.assertRaisesRegex(FileExistsError, "receipt"):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )
            download.assert_not_called()

            sidecar = destination.with_suffix(".pdf.fetch.json")
            sidecar.write_text(
                '{"url":"https://example.invalid/new.pdf","filename":"KDIGO/new.pdf",'
                '"sha256":"' + "0" * 64 + '","bytes":1,"fetched":"2026-09-05"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(FileExistsError, "digest"):
                currency.fetch_replacement(
                    "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                    coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                )

    def test_rerun_resumes_after_build_and_keeps_the_receipt_observed_date(self):
        payload = b"%PDF-1.7\nreplacement guideline"

        class FetchDay(date):
            @classmethod
            def today(cls):
                return cls(2026, 9, 5)

        class ResumeDay(date):
            @classmethod
            def today(cls):
                return cls(2026, 9, 13)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            with mock.patch.object(currency, "date", FetchDay), mock.patch.object(
                currency, "download_bytes", return_value=payload
            ), mock.patch.object(currency, "run_guidelines_build"), mock.patch.object(
                currency,
                "run_catalog_check",
                side_effect=subprocess.CalledProcessError(1, ["catalog"]),
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )

            with mock.patch.object(currency, "date", ResumeDay), mock.patch.object(
                currency, "download_bytes"
            ) as download, mock.patch.object(currency, "run_guidelines_build") as build, mock.patch.object(
                currency, "run_catalog_check"
            ), mock.patch.object(currency, "run_coverage_check"):
                record = currency.fetch_replacement(
                    "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                    coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                )
            download.assert_not_called()
            build.assert_not_called()
            self.assertEqual(record.fetched, "2026-09-05")
            self.assertIn(
                "fetched 2026-09-05",
                coverage.read_text(encoding="utf-8"),
            )

    def test_post_build_failure_keeps_fetched_digest_coherent_and_reports_handoff(self):
        payload = b"%PDF-1.7\nreplacement guideline"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            coverage_before = coverage.read_bytes()
            with mock.patch.object(currency, "download_bytes", return_value=payload), mock.patch.object(
                currency, "run_guidelines_build"
            ), mock.patch.object(
                currency, "run_catalog_check", side_effect=subprocess.CalledProcessError(1, ["catalog"])
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    currency.fetch_replacement(
                        "https://example.invalid/new.pdf", "KDIGO/new.pdf", root / "corpus",
                        coverage, "lipids", "old.pdf", audit, catalog, registry_path,
                    )
            self.assertTrue((root / "corpus" / "KDIGO" / "new.pdf").exists())
            audit_text = audit.read_text(encoding="utf-8")
            self.assertIn("| KDIGO | new.pdf |", audit_text)
            self.assertEqual(coverage.read_bytes(), coverage_before)
            rows, _, problems = currency.guidelines_catalog.parse_catalog(
                catalog.read_text(encoding="utf-8")
            )
            self.assertEqual(problems, [])
            result = currency.audit(
                rows,
                currency.parse_registry(registry_path.read_text(encoding="utf-8")),
                audit_text=audit_text,
                coverage_text=coverage.read_text(encoding="utf-8"),
            )
            self.assertTrue(
                any("half-finished supersession handoff" in item for item in result.failures)
            )

    def test_default_audit_refuses_a_half_finished_supersession_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            currency._upsert_audit_digest(
                audit, "KDIGO", "new.pdf", "a" * 64, 123, "2026-09-05"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--registry",
                    str(registry_path),
                    "--coverage",
                    str(coverage),
                    "--audit",
                    str(audit),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("half-finished supersession handoff", completed.stderr)

    def test_read_ignores_a_half_finished_handoff_and_stamps_the_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            currency._upsert_audit_digest(
                audit, "KDIGO", "new.pdf", "a" * 64, 123, "2026-09-05"
            )
            capture = root / "kdigo.html"
            capture.write_text(
                "<a href='https://doi.org/10.1000/new'>New guideline</a>",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--registry",
                    str(registry_path),
                    "--coverage",
                    str(coverage),
                    "--audit",
                    str(audit),
                    "--read",
                    "KDIGO",
                    "--capture",
                    f"KDIGO={capture}",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            updated = currency.parse_registry(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        replacement = next(row for row in updated.documents if row.filename == "new.pdf")
        self.assertEqual(replacement.observed, date.today().isoformat())

    def test_different_unfinished_handoff_refuses_a_new_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog, registry_path, coverage, audit = self.handoff_files(root)
            catalog.write_text(
                catalog.read_text(encoding="utf-8")
                + "| KDIGO | old-2.pdf | Old 2 | renal | adult | 2020 | 1 | guideline | 10.1000/old-2 |\n"
                + "| KDIGO | new-2.pdf | New 2 | renal | adult | 2026 | 1 | guideline | 10.1000/new-2 |\n",
                encoding="utf-8",
            )
            registry_path.write_text(
                registry_path.read_text(encoding="utf-8")
                + "| old-2.pdf | KDIGO | 10.1000/old-2 | superseded | 2026-09-05 | new-2.pdf |\n"
                + "| new-2.pdf | KDIGO | 10.1000/new-2 | current | 2026-09-05 |  |\n",
                encoding="utf-8",
            )
            coverage.write_text(
                coverage.read_text(encoding="utf-8")
                + "| renal | renal | sheet | renal.md | prior |\n",
                encoding="utf-8",
            )
            currency._upsert_audit_digest(
                audit, "KDIGO", "new.pdf", "a" * 64, 123, "2026-09-05"
            )
            with mock.patch.object(currency, "download_bytes") as download:
                with self.assertRaisesRegex(
                    ValueError, "old.pdf to KDIGO/new.pdf"
                ):
                    currency.fetch_replacement(
                        "https://example.invalid/new-2.pdf",
                        "KDIGO/new-2.pdf",
                        root / "corpus",
                        coverage,
                        "renal",
                        "old-2.pdf",
                        audit,
                        catalog,
                        registry_path,
                    )
            download.assert_not_called()

    def test_interrupted_atomic_write_leaves_each_tracked_file_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in ("currency.md", "audit.md", "coverage.md"):
                with self.subTest(filename=filename):
                    destination = root / filename
                    destination.write_bytes(b"prior bytes")
                    real_open = Path.open

                    class PartialStream:
                        def __init__(self, path: Path, mode: str):
                            self.path = path
                            self.mode = mode
                            self.stream = None

                        def __enter__(self):
                            self.stream = real_open(self.path, self.mode)
                            return self

                        def write(self, payload: bytes):
                            assert self.stream is not None
                            self.stream.write(payload[:3])
                            self.stream.flush()
                            raise OSError("interrupted sibling write")

                        def __exit__(self, *_args):
                            assert self.stream is not None
                            self.stream.close()

                    def interrupt_sibling(path: Path, mode: str = "r", *args, **kwargs):
                        if path.name.startswith(f".{filename}.") and mode == "wb":
                            return PartialStream(path, mode)
                        return real_open(path, mode, *args, **kwargs)

                    with mock.patch.object(Path, "open", interrupt_sibling):
                        with self.assertRaisesRegex(OSError, "interrupted sibling write"):
                            currency._replace_file(
                                destination,
                                b"replacement bytes",
                                lock=False,
                                action="test interrupted write",
                            )
                    self.assertEqual(destination.read_bytes(), b"prior bytes")
                    self.assertEqual(list(root.glob(f".{filename}.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
