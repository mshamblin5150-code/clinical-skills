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
    return f"""# Guideline edition currency

{currency.SCHEMA_MARKER}

## Society indexes

| society | index | reader | join key | access | last observed | state | state observed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADA | https://example.invalid/ada | ada | dcYY-srev | plain | {society_observed} | read |  |
| AHA ACC | https://example.invalid/aha | aha-acc | DOI | agent | {society_observed} | read |  |

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
            coverage = root / "coverage.md"
            audit = root / "audit.md"
            sheet = root / "topic.md"
            sheet.write_text("old sheet bytes", encoding="utf-8")
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
            before = sheet.read_bytes()
            with mock.patch.object(currency, "download_bytes", return_value=payload), mock.patch.object(
                currency, "run_rebuild_pipeline"
            ) as rebuild:
                record = currency.fetch_replacement(
                    "https://example.invalid/new.pdf",
                    "KDIGO/new.pdf",
                    corpus,
                    coverage,
                    "lipids",
                    "old.pdf",
                    audit,
                )
            self.assertEqual(sheet.read_bytes(), before)
            self.assertEqual(record.sha256, "8db6673ffd1a5cc0b9e0a05881c2364eda5d97c5750d8810d63e0a473510ddb4")
            self.assertIn("| lipids | lipids | unread | topic.md | superseded old.pdf by KDIGO/new.pdf;", coverage.read_text(encoding="utf-8"))
            self.assertIn(
                f"| KDIGO | new.pdf | {record.sha256} | {len(payload)} | {record.fetched} |",
                audit.read_text(encoding="utf-8"),
            )
            rebuild.assert_called_once_with(corpus)


if __name__ == "__main__":
    unittest.main()
