"""Public-contract tests for the guideline edition-currency registry."""

from __future__ import annotations

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
            {"publisher completeness", "agent capture provenance", "download identity"},
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
        self.assertEqual(comparison.corpus_absent, ("old.pdf",))
        self.assertEqual(comparison.publisher_additions, ("10.1000/new",))


class CommandContract(unittest.TestCase):
    def test_hook_reports_unconditionally_and_grades_staged_registry(self):
        hook = (ROOT / "tools" / "hooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('guidelines_currency.py" --hook-summary >&2 || true', hook)
        self.assertIn("guidelines-currency)\\.md", hook)
        self.assertIn('guidelines_currency.py" >&2 || status=1', hook)

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
            build.assert_called_once_with(corpus)
            catalog_check.assert_called_once_with(corpus, catalog, audit)
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

    def test_failed_rebuild_rolls_back_received_bytes_and_registry_mutations(self):
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

    def test_post_build_check_failure_keeps_source_and_digest_coherent(self):
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
            self.assertIn("| KDIGO | new.pdf |", audit.read_text(encoding="utf-8"))
            self.assertEqual(coverage.read_bytes(), coverage_before)


if __name__ == "__main__":
    unittest.main()
