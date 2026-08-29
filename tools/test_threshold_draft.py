"""Tests for the threshold-sheet draft CLI introduced by issue #403."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import threshold_sheet  # noqa: E402
import threshold_draft as draft  # noqa: E402
import guidelines_recs  # noqa: E402
from guidelines_recs_test_support import trust_recommendation_record  # noqa: E402
from guidelines_manifest_test_support import (  # noqa: E402
    trusted_extraction_producer,
    write_trusted_extraction_manifest,
)


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "threshold_draft.py"
COMMITTED_RECS = ROOT / "fixtures" / "threshold-draft-records"


def catalog_row(topic: str = "hypertension") -> str:
    return (
        "| society | filename | title | topic | population | year | page_count | class |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| AHA ACC | guideline.pdf | Guideline title | {topic} | adult | 2025 | 12 | guideline |\n"
    )


def recommendation_record() -> dict:
    return trust_recommendation_record({
        "doc_id": "AHA ACC/guideline",
        "source": "C:/corpus/AHA ACC/guideline.pdf",
        "mode": "exact",
        "totals": {"recommendations": 2, "tables": 1},
        "recommendations": [
            {
                "rec_id": "p3/topic/1",
                "page": 3,
                "cor": "1",
                "text": "Adults should have an SBP goal below 130 mm Hg.",
            },
            {
                "rec_id": "p3/topic/2",
                "page": 3,
                "cor": "2a",
                "text": "Use standardized measurement technique.",
            },
        ],
    })


def seeded_sheet() -> str:
    return f"""# Hypertension

{threshold_sheet.SCHEMA_MARKER}

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| aha-2025 | AHA/ACC | AHA ACC/guideline | 2025 | 2025 | https://example.invalid | exact |

## Scope

**Read:** recommendation tables.

**Not read:** narrative.

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bp-goal-sbp | adults | <130 mm Hg | "an SBP goal below 130 mm Hg" | aha-2025 | p3 | p3/topic/1 | 1 |

## Conflicts

## Coverage

- `p3/topic/2` - no decision point
"""


class ThresholdDraftCli(unittest.TestCase):
    def run_cli(
        self,
        root: Path,
        *extra: str,
        record_name: str = "recs-aha-2025.json",
        record_payload: object | None = None,
        other_files: dict[str, object] | None = None,
        manifest_producer: object | None = None,
        source_available: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        catalog = root / "catalog.md"
        recs = root / "recs"
        sheets = root / "sheets"
        text_root = root / "text"
        catalog.write_text(catalog_row(), encoding="utf-8")
        recs.mkdir()
        sheets.mkdir(exist_ok=True)
        text_root.mkdir()
        write_trusted_extraction_manifest(text_root, manifest_producer)
        payload = record_payload or recommendation_record()
        if source_available and isinstance(payload, dict):
            source_name = Path(str(payload.get("source") or "guideline.pdf")).name
            source_pdf = root / "source" / source_name
            source_pdf.parent.mkdir()
            source_pdf.write_bytes(b"synthetic guideline")
            payload = dict(payload)
            payload["source"] = str(source_pdf)
            payload["source_sha256"] = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
        (recs / record_name).write_text(json.dumps(payload), encoding="utf-8")
        for name, payload in (other_files or {}).items():
            if isinstance(payload, bytes):
                (recs / name).write_bytes(payload)
                continue
            text = payload if isinstance(payload, str) else json.dumps(payload)
            (recs / name).write_text(text, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(COMMAND),
                "hypertension",
                "--catalog",
                str(catalog),
                "--recs-root",
                str(recs),
                "--recs-alias",
                str(root / "recs-alias"),
                "--sheet-root",
                str(sheets),
                "--text-root",
                str(text_root),
                *extra,
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def test_an_alternate_name_is_only_a_hint_and_never_the_selected_record(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                Path(directory), record_name="verify-recs-hypertension.json"
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("no recommendation record at", result.stderr)
        self.assertIn("verify-recs-hypertension.json", result.stderr)
        self.assertIn("rename this to recs-aha-2025.json", result.stderr)
        self.assertIn("scanned 1, 1 recommendation records, 0 not", result.stderr)
        self.assertNotIn("Adults should have an SBP goal", result.stdout)

    def test_the_refusal_scan_reads_a_committed_recommendation_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.md"
            sheets = root / "sheets"
            text_root = root / "text"
            catalog.write_text(catalog_row(), encoding="utf-8")
            sheets.mkdir()
            text_root.mkdir()
            write_trusted_extraction_manifest(text_root)
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "hypertension",
                    "--catalog",
                    str(catalog),
                    "--recs-root",
                    str(COMMITTED_RECS),
                    "--sheet-root",
                    str(sheets),
                    "--text-root",
                    str(text_root),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("verify-recs-guideline.json", result.stderr)
        self.assertIn("rename this to recs-aha-2025.json", result.stderr)
        self.assertIn("scanned 1, 1 recommendation records, 0 not", result.stderr)

    def test_the_refusal_scan_classifies_every_json_but_names_only_claimed_nonrecords(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                Path(directory),
                record_name="verify-recs-hypertension.json",
                other_files={
                    "recs-broken.json": "{not json",
                    "recs-binary.json": b"\xff",
                    "recs-sweep.json": [["document", "none", 0]],
                    "mode-tally.json": [["document", "none", 0]],
                },
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("recs-broken.json: would not parse", result.stderr)
        self.assertIn("recs-binary.json: would not parse", result.stderr)
        self.assertIn(
            "recs-sweep.json: parsed and is not a recommendation record",
            result.stderr,
        )
        self.assertNotIn("mode-tally.json:", result.stderr)
        self.assertIn("scanned 5, 1 recommendation records, 4 not", result.stderr)

    def test_an_exact_name_built_from_another_document_is_refused(self):
        wrong = recommendation_record()
        wrong["source"] = "C:/corpus/ADA/standards-of-care.pdf"
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory), record_payload=wrong)

        self.assertEqual(result.returncode, 2)
        self.assertIn("was built from standards-of-care.pdf", result.stderr)
        self.assertIn("scanned 1, 1 recommendation records, 0 not", result.stderr)
        self.assertNotIn("Adults should have an SBP goal", result.stdout)

    def test_an_untrusted_exact_name_is_refused_with_no_escape_hatch(self):
        payload = recommendation_record()
        payload.pop("producer")
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory), record_payload=payload)

        self.assertEqual(result.returncode, 2)
        self.assertIn("untrusted recommendation record", result.stderr)
        self.assertIn("has no producer provenance stamp", result.stderr)
        self.assertNotIn("Adults should have an SBP goal", result.stdout)

    def test_a_trusted_record_whose_source_pdf_left_the_corpus_is_not_drafted(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory), source_available=False)

        self.assertEqual(result.returncode, 2)
        self.assertIn("source PDF is not reachable", result.stderr)
        self.assertNotIn("Adults should have an SBP goal", result.stdout)

    def test_a_resolved_exact_record_does_not_scan_the_lookup_root(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                Path(directory),
                other_files={"recs-broken.json": "{not json"},
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("scanned", result.stderr)
        self.assertNotIn("recs-broken.json", result.stderr)

    def test_the_sweep_alias_wins_and_the_draft_reports_that_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.md"
            recs = root / "recs"
            recs_alias = root / "guidelines-recs"
            sheets = root / "sheets"
            text_root = root / "text"
            source_pdf = root / "source" / "guideline.pdf"
            catalog.write_text(catalog_row(), encoding="utf-8")
            recs.mkdir()
            sheets.mkdir()
            text_root.mkdir()
            source_pdf.parent.mkdir()
            source_pdf.write_bytes(b"synthetic guideline")
            write_trusted_extraction_manifest(text_root)
            alias_payload = recommendation_record()
            alias_payload["source"] = str(source_pdf)
            alias_payload["source_sha256"] = hashlib.sha256(
                source_pdf.read_bytes()
            ).hexdigest()
            alias_record = recs_alias / "AHA ACC" / "guideline.json"
            alias_record.parent.mkdir(parents=True)
            alias_record.write_text(json.dumps(alias_payload), encoding="utf-8")
            (recs_alias / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "documents": [
                            {
                                "doc_id": "AHA ACC/guideline",
                                "source": "AHA ACC/guideline.pdf",
                                "record": "AHA ACC/guideline.json",
                                "outcome": "recommendations-found",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "hypertension",
                    "--catalog",
                    str(catalog),
                    "--recs-root",
                    str(recs),
                    "--recs-alias",
                    str(recs_alias),
                    "--sheet-root",
                    str(sheets),
                    "--text-root",
                    str(text_root),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Adults should have an SBP goal", result.stdout)
        self.assertIn(
            "RECOMMENDATION RECORD source 'aha-2025' -- sweep alias",
            result.stderr,
        )

    def test_a_new_topic_prints_a_skeleton_with_only_machine_cells_filled(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Candidate set", result.stdout)
        candidates = result.stdout.split("## Candidate set", 1)[1].split("## ", 1)[0]
        self.assertIn("| source | rec | page | class |", candidates)
        self.assertNotIn("| source | rec | page | class | label |", candidates)
        self.assertNotIn("A drafted bound sheet intentionally fails structure", result.stdout)
        self.assertIn("## Rejected candidates", result.stdout)
        self.assertIn("## Quantities", result.stdout)
        self.assertIn("|  |  |  | \"Adults should have an SBP goal below 130 mm Hg.\"", result.stdout)
        self.assertIn("| aha-2025 | p3 | p3/topic/1 | 1 |", result.stdout)
        self.assertIn(
            "RECOMMENDATION RECORD source 'aha-2025' -- recs root",
            result.stderr,
        )
        source_row = next(
            line
            for line in result.stdout.splitlines()
            if line.startswith("| aha-2025 |") and "AHA ACC/guideline" in line
        )
        self.assertIn("/source/guideline.pdf", source_row)
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertNotIn("Read:", scope)
        self.assertNotIn("Not read:", scope)
        self.assertIn("| 2 | 2 | 0 |", scope)
        producer = trusted_extraction_producer()
        extractor = next(
            row["sha256"]
            for row in producer["inputs"]
            if row["path"] == "tools/guidelines_extract.py"
        )
        self.assertIn(
            f"extraction identity: producer {producer['commit']}; "
            f"tools/guidelines_extract.py sha256 {extractor}",
            scope,
        )

    def test_a_new_bound_draft_leaves_snippets_blank_and_moves_labels_to_candidates(self):
        payload = recommendation_record()
        payload["mode"] = "bound"
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory), record_payload=payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        self.assertEqual([row.snippet for row in drafted.rows], ["", ""])
        candidates = result.stdout.split("## Candidate set", 1)[1].split("## ", 1)[0]
        self.assertIn("Adults should have an SBP goal below 130 mm Hg.", candidates)
        self.assertIn("A drafted bound sheet intentionally fails structure", result.stdout)

    def test_a_seeded_bound_draft_skips_membership_and_containment_rejections(self):
        payload = recommendation_record()
        payload["mode"] = "bound"
        seed = seeded_sheet().replace("| exact |", "| bound |").replace(
            "## Conflicts",
            "|  |  |  | \"page-read narrative\" | aha-2025 | p4 | p4/narrative/1 | narrative |\n\n## Conflicts",
        ).replace("an SBP goal below 130 mm Hg", "page-read text absent from the label")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "sheets"
            sheets.mkdir()
            (sheets / "hypertension.md").write_text(seed, encoding="utf-8")
            result = self.run_cli(root, record_payload=payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        self.assertEqual(len(drafted.rows), 2)
        self.assertEqual(
            {row.rec for row in drafted.rows},
            {"p3/topic/1", "p4/narrative/1"},
        )
        self.assertNotIn("not in its recommendation record", result.stdout)
        self.assertNotIn("seeded snippet is not in its record", result.stdout)

    def test_the_real_diabetes_bound_sheet_rejects_no_rows_when_its_record_is_trusted(self):
        record_path = Path(threshold_sheet.DEFAULT_RECS_ROOT) / "recs-ada-2026.json"
        if not record_path.is_file():
            self.skipTest(f"acceptance record not present at {record_path}")
        try:
            record = guidelines_recs.load_recommendation_record(
                record_path, require_source_pdf=True
            )
        except (OSError, ValueError, guidelines_recs.UntrustedRecommendationRecord) as error:
            self.skipTest(f"acceptance record is not trusted in this checkout: {error}")
        sheet_path = ROOT / "reference" / "thresholds" / "diabetes.md"
        seeded = threshold_sheet.parse(
            sheet_path.read_text(encoding="utf-8"), sheet_path
        )
        source = draft.Source(
            key="ada-2026",
            society="ADA",
            document="ADA/standards-of-care-2026",
            version="2026",
            published="2026",
            url=str(record.get("source") or ""),
            mode="bound",
            record=record,
        )

        rows, scoped_out, rejected = draft.select_rows([source], seeded)

        self.assertEqual(len(rows), 357)
        self.assertEqual(scoped_out, seeded.scoped_out)
        self.assertEqual(rejected, [])

    def test_an_untrusted_manifest_cannot_supply_a_draft_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(
                Path(directory),
                manifest_producer={"commit": "f" * 40, "dirty": False},
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("untrusted artifact", result.stderr)
        self.assertNotIn("extraction identity:", result.stdout)

    def test_an_existing_curated_sheet_selects_rows_without_copying_judgment_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "sheets"
            sheets.mkdir()
            (sheets / "hypertension.md").write_text(seeded_sheet(), encoding="utf-8")
            result = self.run_cli(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        self.assertEqual(len(drafted.rows), 1)
        self.assertEqual(drafted.rows[0].quantity, "")
        self.assertEqual(drafted.rows[0].population, "")
        self.assertEqual(drafted.rows[0].value, "")
        self.assertEqual(drafted.rows[0].snippet, "an SBP goal below 130 mm Hg")
        self.assertEqual(drafted.rows[0].rec, "p3/topic/1")
        self.assertEqual(drafted.scoped_out, {"p3/topic/2": "no decision point"})
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertIn("| 2 | 1 | 1 |", scope)
        self.assertNotIn("recommendation tables", result.stdout)

    def test_same_society_and_year_documents_keep_distinct_source_keys_and_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.md"
            recs = root / "recs"
            sheets = root / "sheets"
            text_root = root / "text"
            recs.mkdir()
            sheets.mkdir()
            text_root.mkdir()
            write_trusted_extraction_manifest(text_root)
            catalog.write_text(
                "| society | filename | title | topic | population | year | page_count | class |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| USPSTF | adults.pdf | Adult oral health | oral health | adult | 2023 | 10 | recommendation-statement |\n"
                "| USPSTF | children.pdf | Child oral health | oral health | pediatric | 2023 | 11 | recommendation-statement |\n",
                encoding="utf-8",
            )
            source_names = {
                "adults": "uspstf-2023-adults-d94f77",
                "children": "uspstf-2023-children-751b2d",
            }
            source_root = root / "source"
            source_root.mkdir()
            for name, page in (("adults", 2), ("children", 4)):
                source_pdf = source_root / f"{name}.pdf"
                source_pdf.write_bytes(f"synthetic {name}".encode("utf-8"))
                payload = trust_recommendation_record({
                    "source": str(source_pdf),
                    "source_sha256": hashlib.sha256(source_pdf.read_bytes()).hexdigest(),
                    "mode": "exact",
                    "recommendations": [
                        {
                            "rec_id": f"p{page}/{name}/1",
                            "page": page,
                            "cor": "B",
                            "text": f"{name} recommendation text",
                        }
                    ],
                })
                (recs / f"recs-{source_names[name]}.json").write_text(
                    json.dumps(payload), encoding="utf-8"
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "oral health",
                    "--catalog",
                    str(catalog),
                    "--recs-root",
                    str(recs),
                    "--sheet-root",
                    str(sheets),
                    "--text-root",
                    str(text_root),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        self.assertEqual(len(drafted.sources), 2)
        self.assertEqual(len(set(drafted.sources)), 2)
        self.assertEqual({row.rec for row in drafted.rows}, {"p2/adults/1", "p4/children/1"})
        self.assertEqual({row.source for row in drafted.rows}, set(drafted.sources))

    def test_hypertension_reproduces_the_committed_data_half_when_records_exist(self):
        recs = Path(threshold_sheet.DEFAULT_RECS_ROOT) / "recs-aha-2025.json"
        if not recs.is_file():
            self.skipTest(f"acceptance record not present at {recs}")

        result = subprocess.run(
            [sys.executable, str(COMMAND), "hypertension"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        committed_path = ROOT / "reference" / "thresholds" / "hypertension.md"
        committed = threshold_sheet.parse(
            committed_path.read_text(encoding="utf-8"), committed_path
        )
        self.assertEqual(len(drafted.rows), 74)
        self.assertEqual(len({row.rec for row in drafted.rows}), 53)
        self.assertEqual(len(drafted.scoped_out), 50)
        self.assertEqual(
            len({row.rec for row in drafted.rows} | set(drafted.scoped_out)), 103
        )
        self.assertEqual(
            [
                (row.snippet, row.source, row.page, row.rec, row.klass)
                for row in drafted.rows
            ],
            [
                (row.snippet, row.source, row.page, row.rec, row.klass)
                for row in committed.rows
            ],
        )
        self.assertEqual(drafted.sources, committed.sources)
        self.assertEqual(drafted.scoped_out, committed.scoped_out)
        self.assertTrue(all(not row.quantity and not row.population and not row.value for row in drafted.rows))
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertNotIn("Read:", scope)
        self.assertNotIn("Not read:", scope)
        self.assertNotIn("quoting posture", result.stdout.casefold())
        self.assertNotIn("Recommendations for", result.stdout)
        self.assertIn("hypertension screening", result.stdout)


if __name__ == "__main__":
    unittest.main()
