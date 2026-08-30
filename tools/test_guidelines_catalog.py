"""Tests for the guideline catalog's parsers, classifiers and checker.

These run against the committed fixtures in ``tools/testdata/`` and never against
``C:/codeing/guidelines-src`` or ``reference/guidelines-catalog.md``. Same
reasoning as ``test_icd10.py``: a test that read the real corpus would pass for
two different reasons, one of them being that the extractor and the test are
wrong in the same way. Nothing here opens a PDF; the public reader fixture builds
#80's text-and-manifest artifact directly.

The page fixtures are ``%%PAGE%%``-delimited plain text standing in for what the
extractor hands back per page. They carry no patient data of any kind — they are
public-domain USPSTF and CDC material plus the functional running heads of a
journal PDF — so this file needs no ``phi-scan: synthetic`` pragma and
deliberately does not claim one.

``AccessLinesAreNotPublicationDates`` is the load-bearing class. Every AHA/ACC
file in the corpus, and most IDSA ones, carry ``Downloaded from ... 2026`` on
every page. That line is the most-repeated year in the document, so a year rule
that does not exclude it reports the day the corpus was collected as the
publication year of a 2018 guideline — and ``year`` is the only staleness signal
this catalog has.
"""

from __future__ import annotations

import json
import contextlib
import dataclasses
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import artifact_lock
import artifact_provenance
import guidelines_catalog as gc
from guidelines_manifest_test_support import ReadingManifestConformance
import guidelines_extract as extract


def clean_producer():
    producer = artifact_provenance.current_producer()
    producer["dirty"] = False
    return producer

TESTDATA = Path(__file__).resolve().parent / "testdata"


def pages(name: str) -> list[str]:
    """Read a page fixture as the list of page texts the extractor would hand back.

    Anything before the first ``%%PAGE%%`` is preamble, not a page — which is
    what lets ``guidelines_capture_pages.txt`` carry its ``phi-scan: synthetic``
    declaration and the note explaining why it needs a date-shaped literal.
    """
    text = (TESTDATA / name).read_text(encoding="utf-8")
    return [p for p in text.split("%%PAGE%%")[1:] if p.strip()]


USPSTF_PAGES = pages("guidelines_uspstf_pages.txt")
JOURNAL_PAGES = pages("guidelines_journal_pages.txt")
CAPTURE_PAGES = pages("guidelines_capture_pages.txt")
CATALOG = (TESTDATA / "guidelines_catalog_sample.md").read_text(encoding="utf-8")

# Pinned so a fixture that grows or loses a page fails here rather than turning
# some other assertion green for the wrong reason. The capture fixture earned
# this: its preamble once spelled out the page delimiter and split into a third
# page that was pure prose, and the only symptom was one classify test flipping.
assert (len(USPSTF_PAGES), len(JOURNAL_PAGES), len(CAPTURE_PAGES)) == (3, 4, 2)


def row(**overrides) -> gc.Row:
    base = dict(
        society="USPSTF",
        filename="copd-screening.pdf",
        title="Screening for Chronic Obstructive Pulmonary Disease",
        topic="COPD screening",
        population="adult",
        year="2022",
        page_count="6",
        cls="recommendation-statement",
        citation="10.1001/jama.2022.5690",
    )
    base.update(overrides)
    return gc.Row(**base)


def doc(**overrides) -> gc.Document:
    base = dict(
        society="USPSTF",
        filename="copd-screening.pdf",
        page_count=6,
        cls="recommendation-statement",
        title_guess="Screening for Chronic Obstructive Pulmonary Disease",
        year_guess="2022",
        citation_candidate="UNCONFIRMED: 10.1001/jama.2022.5690",
    )
    base.update(overrides)
    return gc.Document(**base)


class ReadingTheExtractedCorpus(ReadingManifestConformance, unittest.TestCase):
    def build_conformance_corpus(self, root, producer):
        record = extract.build_document(
            Path("USPSTF/screening.pdf"),
            ["US Preventive Services Task Force Recommendation Statement"],
            root,
            "Screening for Example Disease",
        )
        extract.write_manifest(
            root, [record], Path("C:/outside/guidelines-src"), producer=producer
        )
        path = root / extract.MANIFEST_NAME
        value = json.loads(path.read_text(encoding="utf-8"))
        value["producer"] = producer
        path.write_text(json.dumps(value), encoding="utf-8")

    def conformance_read(self, root, *, allow):
        try:
            gc.read_corpus(root, allow_untrusted_provenance=allow)
        except ValueError as failure:
            return False, str(failure)
        return True, ""

    def conformance_command(self, root, *, allow):
        args = ["--draft", str(root)]
        if allow:
            args.insert(0, "--allow-untrusted-provenance")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gc.main(args)

    def test_the_manifest_reader_is_the_owner_and_not_a_copy(self):
        import guidelines_manifest

        self.assertIs(gc.read_or_raise, guidelines_manifest.read_or_raise)

    """The catalog consumes #80's public artifact, not the source PDFs."""

    def test_two_read_commands_can_share_one_completed_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(
                Path("USPSTF/screening.pdf"),
                ["US Preventive Services Task Force Recommendation Statement"],
                text_dir,
                "Screening for Example Disease",
            )
            extract.write_manifest(
                text_dir,
                [record],
                Path("C:/outside/guidelines-src"),
                producer=clean_producer(),
            )
            out, err = io.StringIO(), io.StringIO()
            with artifact_lock.hold(
                text_dir, "first catalog read", mode="read"
            ), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = gc.main(["--draft", str(text_dir)])

            self.assertEqual(status, 0, err.getvalue())
            self.assertIn("screening.pdf", out.getvalue())

    def test_manifest_metadata_and_stripped_year_survive_the_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            repeated = "Journal of Preventive Medicine 2021; 10: 1-4"
            pages = [
                f"{repeated}\nUS Preventive Services Task Force Recommendation Statement\n"
                "The USPSTF recommends screening in adults.\nA recommendation."
            ] + [f"{repeated}\nPrior recommendation published in 2014." for _ in range(3)]
            record = extract.build_document(
                Path("USPSTF/screening.pdf"),
                pages,
                text_dir,
                "Screening for Example Disease",
            )
            extract.write_manifest(
                text_dir, [record], Path("C:/outside/guidelines-src"),
                producer=clean_producer(),
            )

            self.assertNotIn(repeated, (text_dir / "USPSTF" / "screening.txt").read_text())
            self.assertEqual(
                gc.read_corpus(text_dir),
                [
                    gc.Document(
                        society="USPSTF",
                        filename="screening.pdf",
                        page_count=4,
                        cls=extract.CLASS_RECOMMENDATION_STATEMENT,
                        title_guess="Screening for Example Disease",
                        year_guess="2021",
                        citation_candidate=gc.UNSETTLED,
                    )
                ],
            )

    def test_a_text_directory_without_the_manifest_is_not_a_catalog_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            (text_dir / "USPSTF").mkdir()
            (text_dir / "USPSTF" / "screening.txt").write_text("body\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "manifest.json"):
                gc.read_corpus(text_dir)

    def test_the_manifest_must_carry_the_title_key_even_when_its_value_is_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(Path("KDIGO/guideline.pdf"), ["body"], text_dir)
            manifest_path = extract.write_manifest(
                text_dir, [record], Path("C:/outside/guidelines-src"),
                producer=clean_producer(),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["documents"][0]["title"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "title"):
                gc.read_corpus(text_dir)

    def test_year_voting_keeps_page_frequency_after_the_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            pages = [
                "Journal 2019\nUpdate 2021 page 1\nbody",
                "Journal 2019\nUpdate 2021 page 2\nbody",
                "Journal 2019\nUpdate 2021 page 3\nbody",
                "Journal 2019\nbody",
            ]
            record = extract.build_document(
                Path("KDIGO/guideline.pdf"), pages, text_dir, "Clinical Practice Guideline"
            )
            extract.write_manifest(
                text_dir, [record], Path("C:/outside/guidelines-src"),
                producer=clean_producer(),
            )

            self.assertEqual(gc.read_corpus(text_dir)[0].year_guess, "2019")


def reading(column: str, value: str) -> gc.AuditReading:
    return gc.AuditReading(
        society="USPSTF",
        filename="copd-screening.pdf",
        column=column,
        value=value,
        page="1",
        evidence="title-page",
    )


def ruling(column: str, value: str) -> gc.AuditRuling:
    return gc.AuditRuling(
        society="USPSTF",
        filename="copd-screening.pdf",
        column=column,
        confirmed_value=value,
        confirmed_date="2026-08-20",
        rationale="Clinician confirmed the narrower front-matter population.",
    )


def audit_document() -> gc.AuditDocument:
    return gc.AuditDocument(
        society="USPSTF",
        filename="copd-screening.pdf",
        sha256="a" * 64,
        bytes="10",
        audited="2026-08-20",
    )


AUDIT = """# Independent audit

## Documents

| society | filename | sha256 | bytes | audited |
| --- | --- | --- | --- | --- |
| USPSTF | copd-screening.pdf | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 10 | 2026-08-20 |

## Independent readings

| society | filename | column | value | page | evidence |
| --- | --- | --- | --- | --- | --- |
| USPSTF | copd-screening.pdf | title | Screening for Chronic Obstructive Pulmonary Disease | 1 | title-page |
| USPSTF | copd-screening.pdf | topic | COPD screening | 1 | title-page |
| USPSTF | copd-screening.pdf | population | adult | 1 | front-matter |
| USPSTF | copd-screening.pdf | year | 2022 | 1 | title-page |
| USPSTF | copd-screening.pdf | citation | 10.1001/jama.2022.5690 | 1 | publication-line |

## Clinician rulings

| society | filename | column | confirmed_value | confirmed_date | rationale |
| --- | --- | --- | --- | --- | --- |
"""


class TableRows(unittest.TestCase):
    def test_splits_on_pipes_and_trims(self):
        self.assertEqual(gc.split_table_row("| a | b | c |"), ["a", "b", "c"])

    def test_an_escaped_pipe_stays_inside_its_cell(self):
        # The ACIP captures really are titled "... | Vaccines & Immunizations |
        # CDC", so a title with pipes in it is a corpus fact, not a hypothetical.
        cells = gc.split_table_row(r"| ACIP | f.pdf | Adults \| Vaccines \| CDC | t |")
        self.assertEqual(cells[2], "Adults | Vaccines | CDC")
        self.assertEqual(len(cells), 4)

    def test_cells_are_assigned_by_column_name_not_position(self):
        built = gc.row_from_cells(
            [
                "USPSTF",
                "f.pdf",
                "T",
                "topic",
                "adult",
                "2022",
                "6",
                "recommendation-statement",
                "10.1001/example",
            ]
        )
        self.assertEqual(built.cls, "recommendation-statement")
        self.assertEqual(built.cells["class"], "recommendation-statement")

    def test_the_wrong_number_of_cells_raises_rather_than_shifting_columns(self):
        with self.assertRaises(ValueError):
            gc.row_from_cells(["USPSTF", "f.pdf", "T"])

    def test_separator_row_is_recognized(self):
        self.assertTrue(gc.is_separator_row(["---", ":---", "---:"]))
        self.assertFalse(gc.is_separator_row(["---", "USPSTF"]))


class ParsingTheCatalog(unittest.TestCase):
    def setUp(self):
        self.rows, self.unsettled, self.problems = gc.parse_catalog(CATALOG)

    def test_the_legend_table_above_the_catalog_is_not_read_as_rows(self):
        self.assertEqual(self.problems, [])
        self.assertEqual(len(self.rows), 3)
        self.assertEqual({r.society for r in self.rows}, {"ACIP", "KDIGO", "USPSTF"})

    def test_the_table_ends_at_the_first_line_that_is_not_one(self):
        self.assertNotIn("Prose after the table", [r.society for r in self.rows])

    def test_cells_land_in_the_right_columns(self):
        acip = next(r for r in self.rows if r.society == "ACIP")
        self.assertEqual(acip.title, "Recommended Vaccinations for Adults | Vaccines & Immunizations | CDC")
        self.assertEqual(acip.page_count, "7")
        self.assertEqual(acip.cls, "web-capture")

    def test_the_closing_comment_indexes_by_filename_and_column(self):
        self.assertEqual(self.unsettled["schedule-adults.pdf"], {"year"})
        self.assertEqual(self.unsettled["KDIGO-2024-CKD-Guideline.pdf"], {"population"})

    def test_a_row_with_the_wrong_cell_count_is_reported_not_dropped_silently(self):
        broken = CATALOG.replace(
            "| USPSTF | copd-screening.pdf |", "| USPSTF | copd-screening.pdf | extra |"
        )
        rows, _, problems = gc.parse_catalog(broken)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("10 cells, expected 9" in p for p in problems))

    def test_a_file_with_no_catalog_table_says_so(self):
        _, _, problems = gc.parse_catalog("# Nothing here\n\nJust prose.\n")
        self.assertTrue(any("no table headed" in p for p in problems))

    def test_a_closing_comment_naming_a_column_that_cannot_be_unsettled_is_refused(self):
        text = CATALOG + "\n- `copd-screening.pdf` — `page_count` — nope\n"
        _, _, problems = gc.parse_catalog(text)
        self.assertTrue(any("page_count" in p for p in problems))


class AccessLinesAreNotPublicationDates(unittest.TestCase):
    def test_the_download_stamp_does_not_become_the_year(self):
        self.assertEqual(gc.year_from_running_head(JOURNAL_PAGES), "2019")

    def test_the_year_in_the_running_head_wins_over_a_year_mentioned_once(self):
        self.assertEqual(gc.year_from_running_head(USPSTF_PAGES), "2022")

    def test_a_document_that_never_repeats_a_year_is_unsettled(self):
        self.assertEqual(gc.year_from_running_head(CAPTURE_PAGES), gc.UNSETTLED)

    def test_no_pages_at_all_is_unsettled(self):
        self.assertEqual(gc.year_from_running_head([]), gc.UNSETTLED)

    def test_a_year_in_the_title_beats_the_running_head(self):
        # The AHA fixture is the 2018 cholesterol guideline printed in a 2019
        # issue: the running head says 2019 on every page and the title says 2018.
        title = "2018 AHA/ACC Guideline on the Management of Blood Cholesterol"
        self.assertEqual(gc.year_guess(title, JOURNAL_PAGES), "2018")

    def test_without_a_year_in_the_title_the_running_head_is_used(self):
        self.assertEqual(gc.year_guess("Screening for COPD", USPSTF_PAGES), "2022")

    def test_a_tie_goes_to_the_later_year(self):
        # A reaffirmation prints the year it supersedes as often as its own, and
        # the earlier one is the superseded one. Ties only reach this rule when
        # the title carries no year, so the "2018 guideline in a 2019 issue" case
        # is not what is being decided here.
        reaffirmation = [
            "Screening for Asymptomatic Carotid Artery Stenosis\nJAMA. 2021 update of 2014",
            "The 2014 recommendation is reaffirmed. JAMA 2021;325(5):476-481",
        ]
        self.assertEqual(gc.year_from_running_head(reaffirmation), "2021")


class TitleGuess(unittest.TestCase):
    def test_a_usable_pdf_title_is_taken(self):
        got = gc.title_guess(
            "Screening for Chronic Obstructive Pulmonary Disease", USPSTF_PAGES, "copd.pdf"
        )
        self.assertEqual(got, "Screening for Chronic Obstructive Pulmonary Disease")

    def test_placeholder_pdf_titles_are_rejected(self):
        for junk in ("untitled", "Topic", "ajt_9_S3-cover", "KISU_v7_i1_COVER.indd"):
            self.assertFalse(gc.looks_like_title(junk, "x.pdf"), junk)

    def test_a_title_that_is_only_the_filename_is_rejected(self):
        self.assertFalse(gc.looks_like_title("GOLD REPORT 2026 v1", "GOLD REPORT 2026 v1.pdf"))

    def test_falling_back_to_the_title_page_takes_a_substantial_line(self):
        got = gc.title_guess("untitled", USPSTF_PAGES, "copd.pdf")
        self.assertEqual(got, "Screening for Chronic Obstructive Pulmonary Disease")

    def test_nothing_substantial_anywhere_is_unsettled(self):
        self.assertEqual(gc.title_guess(None, ["S3", "9", "2009"], "x.pdf"), gc.UNSETTLED)


class StatedCitationCandidate(unittest.TestCase):
    def test_a_page_one_doi_is_only_an_unconfirmed_catalog_candidate(self):
        pages = [
            "JAMA. 2022;327(18):1806-1811. doi:10.1001/jama.2022.5690\nbody",
            "References doi:10.1001/jama.2021.0001",
        ]

        self.assertEqual(
            gc.stated_citation_candidate(pages),
            "UNCONFIRMED: 10.1001/jama.2022.5690",
        )

    def test_the_catalog_draft_carries_the_marker_but_the_blind_draft_does_not(self):
        drafted = gc.draft_rows([doc()])
        blind = gc.render_audit_draft([audit_document()])

        self.assertEqual(drafted[0].citation, doc().citation_candidate)
        self.assertNotIn(gc.UNCONFIRMED_PREFIX, blind)


class TheDeclaredLimitsObject(unittest.TestCase):
    def test_every_declared_limit_has_a_key_and_reason(self):
        self.assertIn("link rot", dict(gc.NOT_REACHED))
        for key, reason in gc.NOT_REACHED:
            self.assertTrue(key.strip(), key)
            self.assertGreater(len(reason.split()), 8, key)


class CheckAgainstTheCorpus(unittest.TestCase):
    def test_a_catalog_that_matches_the_corpus_passes(self):
        self.assertEqual(gc.check([row()], {}, [doc()]), [])

    def test_a_dropped_row_fails(self):
        failures = gc.check([], {}, [doc()])
        self.assertTrue(any("missing from the catalog" in f for f in failures))

    def test_a_row_for_a_file_that_is_gone_fails(self):
        failures = gc.check([row()], {}, [])
        self.assertTrue(any("missing from the corpus" in f for f in failures))

    def test_a_stale_page_count_fails(self):
        failures = gc.check([row(page_count="5")], {}, [doc()])
        self.assertTrue(any("page_count" in f for f in failures))

    def test_a_wrong_society_fails(self):
        failures = gc.check([row(society="IDSA")], {}, [doc()])
        self.assertTrue(any("society" in f for f in failures))

    def test_a_class_the_corpus_disagrees_with_fails(self):
        failures = gc.check([row(cls="guideline")], {}, [doc()])
        self.assertTrue(any("class is 'guideline'" in f for f in failures))

    def test_the_same_file_twice_fails(self):
        failures = gc.check([row(), row()], {}, [doc()])
        self.assertTrue(any("more than one row" in f for f in failures))


class CheckTheIndependentAudit(unittest.TestCase):
    def complete_readings(self) -> list[gc.AuditReading]:
        return [
            reading("title", row().title),
            reading("topic", row().topic),
            reading("population", row().population),
            reading("year", row().year),
            reading("citation", row().citation),
        ]

    def test_deleting_the_stated_citation_reading_fails(self):
        readings = self.complete_readings()[:-1]

        failures = gc.check_audit([row()], [audit_document()], readings, [])

        self.assertTrue(any("citation has no independent reading" in f for f in failures))

    def test_a_disagreement_without_a_clinician_ruling_fails(self):
        readings = self.complete_readings()
        readings[2] = reading("population", "adult, older adult")

        failures = gc.check_audit([row()], [audit_document()], readings, [])

        self.assertTrue(any("population disagrees" in f for f in failures))

    def test_a_clinician_ruling_can_confirm_the_catalog_value(self):
        readings = self.complete_readings()
        readings[2] = reading("population", "adult, older adult")

        failures = gc.check_audit(
            [row()], [audit_document()], readings, [ruling("population", "adult")]
        )

        self.assertEqual(failures, [])

    def test_readings_without_a_document_binding_fail(self):
        failures = gc.check_audit([row()], [], self.complete_readings(), [])

        self.assertTrue(any("has no document audit" in f for f in failures))

    def test_changed_pdf_bytes_fail_document_binding(self):
        failures = gc.check_audit_digests(
            [audit_document()], {("USPSTF", "copd-screening.pdf"): "b" * 64}
        )

        self.assertTrue(any("SHA-256 disagrees" in f for f in failures))

    def test_duplicate_document_and_reading_entries_fail(self):
        readings = self.complete_readings()
        failures = gc.check_audit(
            [row()],
            [audit_document(), audit_document()],
            readings + [readings[0]],
            [],
        )

        self.assertTrue(any("document audit appears more than once" in f for f in failures))
        self.assertTrue(any("title reading appears more than once" in f for f in failures))

    def test_unrecognized_or_unbound_entries_fail(self):
        extra = reading("summary", "anything")
        extra = dataclasses.replace(extra, filename="gone.pdf")
        failures = gc.check_audit(
            [row()], [audit_document()], self.complete_readings() + [extra], []
        )

        self.assertTrue(any("unknown audit column" in f for f in failures))
        self.assertTrue(any("has no catalog row" in f for f in failures))

    def test_document_identity_and_completion_fields_are_validated(self):
        document = dataclasses.replace(
            audit_document(), society="IDSA", sha256="not-a-digest", bytes="ten", audited="?"
        )
        failures = gc.check_audit([row()], [document], self.complete_readings(), [])

        self.assertTrue(any("document society" in f for f in failures))
        self.assertTrue(any("SHA-256 is not" in f for f in failures))
        self.assertTrue(any("byte count" in f for f in failures))
        self.assertTrue(any("audit date" in f for f in failures))

    def test_reading_locator_and_evidence_are_required(self):
        readings = self.complete_readings()
        readings[0] = dataclasses.replace(readings[0], page="0", evidence="")
        failures = gc.check_audit([row()], [audit_document()], readings, [])

        self.assertTrue(any("page '0' is not within" in f for f in failures))
        self.assertTrue(any("evidence is empty" in f for f in failures))

    def test_stale_and_incomplete_rulings_fail(self):
        stale = dataclasses.replace(ruling("population", "adult"), rationale="")
        failures = gc.check_audit(
            [row()], [audit_document()], self.complete_readings(), [stale]
        )

        self.assertTrue(any("ruling exists without a disagreement" in f for f in failures))
        self.assertTrue(any("rationale is empty" in f for f in failures))

    def test_a_missing_corpus_digest_fails(self):
        failures = gc.check_audit_digests([audit_document()], {})

        self.assertTrue(any("missing from the corpus digest scan" in f for f in failures))


class ParsingTheIndependentAudit(unittest.TestCase):
    def test_the_three_named_tables_are_parsed(self):
        documents, readings, rulings, problems = gc.parse_audit(AUDIT)

        self.assertEqual(problems, [])
        self.assertEqual(documents[0].filename, "copd-screening.pdf")
        self.assertEqual(documents[0].bytes, "10")
        self.assertEqual([item.column for item in readings], list(gc.AUDITED_COLUMNS))
        self.assertEqual(rulings, [])


class DraftingTheIndependentAudit(unittest.TestCase):
    def test_the_blind_draft_exposes_no_judgment_values_or_machine_guesses(self):
        text = gc.render_audit_draft([audit_document()])

        self.assertIn("copd-screening.pdf", text)
        self.assertIn("a" * 64, text)
        self.assertIn("| 10 |", text)
        self.assertNotIn(row().title, text)
        self.assertNotIn(row().year, text)
        self.assertEqual(text.count("| ? | ? | ? |"), len(gc.AUDITED_COLUMNS))

    def test_the_cli_builds_a_blind_draft_from_file_identity_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "corpus"
            society = src / "USPSTF"
            society.mkdir(parents=True)
            (society / "opaque.pdf").write_bytes(b"not parsed")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = gc.main(["--audit-draft", str(src)])

        self.assertEqual(result, 0)
        self.assertIn("opaque.pdf", stdout.getvalue())
        self.assertIn("| 10 |", stdout.getvalue())


class CheckingCheapCorpusDrift(unittest.TestCase):
    def _write_inputs(self, root: Path, documents: list[gc.AuditDocument]) -> tuple[Path, Path]:
        catalog = root / "catalog.md"
        audit = root / "audit.md"
        rows = [
            row(society=document.society, filename=document.filename)
            for document in documents
        ]
        catalog.write_text(
            "# Catalog\n\n" + gc.render_table(rows) + "\n\n## Unsettled cells\n",
            encoding="utf-8",
        )
        audit.write_text(gc.render_audit_draft(documents), encoding="utf-8")
        return catalog, audit

    def _run(self, root: Path, documents: list[gc.AuditDocument]) -> tuple[int, str, str]:
        catalog, audit = self._write_inputs(root, documents)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = gc.main(
                [
                    "--check-corpus-size",
                    "--catalog", str(catalog),
                    "--audit", str(audit),
                    "--pdf-src", str(root / "corpus"),
                ]
            )
        return status, out.getvalue(), err.getvalue()

    def test_matching_names_and_sizes_are_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "corpus" / "USPSTF" / "copd-screening.pdf"
            pdf.parent.mkdir(parents=True)
            pdf.write_bytes(b"0123456789")
            status, out, err = self._run(root, [audit_document()])

        self.assertEqual(status, 0)
        self.assertEqual((out, err), ("", ""))

    def test_arrivals_removals_and_size_disagreements_name_the_full_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            society = root / "corpus" / "USPSTF"
            society.mkdir(parents=True)
            (society / "copd-screening.pdf").write_bytes(b"changed size")
            (society / "arrived.pdf").write_bytes(b"new")
            missing = dataclasses.replace(
                audit_document(), filename="removed.pdf", bytes="7"
            )
            status, out, err = self._run(root, [audit_document(), missing])

        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertIn("arrived.pdf: in the corpus, missing from the audit ledger", err)
        self.assertIn("removed.pdf: in the audit ledger, missing from the corpus", err)
        self.assertIn("copd-screening.pdf: byte size", err)
        self.assertIn("same-name same-size rewrite", err)
        self.assertIn("python tools/guidelines_catalog.py", err)

    def test_an_absent_corpus_prints_a_runtime_derived_shopping_list(self):
        second = dataclasses.replace(
            audit_document(), society="IDSA", filename="idsa.pdf", bytes="4"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, out, err = self._run(root, [audit_document(), second])

        self.assertEqual(status, 2)
        self.assertEqual(out, "")
        self.assertIn(
            f"guideline corpus: NOT CHECKED -- nothing at {(root / 'corpus').as_posix()}",
            err,
        )
        self.assertIn("the tree expects 2 documents: USPSTF 1, IDSA 1", err)
        self.assertIn("reference/guidelines-catalog.md", err)
        self.assertIn("reference/guidelines-catalog-audit.md", err)

    def test_the_pre_commit_command_runs_the_check_unconditionally_and_advisory(self):
        shell = shutil.which("sh")
        git = shutil.which("git")
        if not shell or not git:
            self.skipTest("the hook contract needs sh and git")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / "tools"
            (tools / "hooks").mkdir(parents=True)
            shutil.copy2(gc.REPO_ROOT / "tools" / "hooks" / "pre-commit", tools / "hooks" / "pre-commit")
            marker = root / "guideline-check-args"
            (tools / "guidelines_catalog.py").write_text(
                "import os, pathlib, sys\n"
                "pathlib.Path(os.environ['GUIDELINE_CHECK_MARKER']).write_text(' '.join(sys.argv[1:]))\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            for name in (
                "skills_mirror.py",
                "spelling_scan.py",
                "scratch_census.py",
                "phi_scan.py",
            ):
                (tools / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
            subprocess.run([git, "init", "--quiet"], cwd=root, check=True)
            environment = {**os.environ, "GUIDELINE_CHECK_MARKER": str(marker)}
            result = subprocess.run(
                [shell, str(tools / "hooks" / "pre-commit")],
                cwd=root,
                env=environment,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            marker_text = marker.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(marker_text, "--check-corpus-size")


class CheckingTheAuditFromTheCli(unittest.TestCase):
    def test_absent_corpus_bytes_are_reported_as_skipped_not_passed(self):
        catalog = (
            "# Catalog\n\n"
            "| `class` | `guideline`, `recommendation-statement`, `web-capture`, "
            "`draft`, `errata`, or `scope-of-work` |\n\n"
            + gc.render_table([row()])
            + "\n\n## Unsettled cells\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog_path = root / "catalog.md"
            audit_path = root / "audit.md"
            catalog_path.write_text(catalog, encoding="utf-8")
            audit_path.write_text(AUDIT, encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                result = gc.main(
                    [
                        "--catalog",
                        str(catalog_path),
                        "--audit",
                        str(audit_path),
                        "--src",
                        str(root / "absent-corpus"),
                        "--pdf-src",
                        str(root / "absent-corpus"),
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("SKIPPED document digest verification", stdout.getvalue())


class AcceptedDistrustOnTheCatalogCli(unittest.TestCase):
    def _catalog(self, declaration: str = "") -> str:
        return (
            "# Catalog\n\n"
            "| `class` | `guideline`, `recommendation-statement`, `web-capture`, "
            "`draft`, `errata`, or `scope-of-work` |\n\n"
            + (declaration + "\n\n" if declaration else "")
            + gc.render_table([row()])
            + "\n\n## Unsettled cells\n"
        )

    def _corpus(self, root: Path, *, dirty: bool) -> Path:
        corpus = root / "corpus"
        record = extract.build_document(
            Path("USPSTF/copd-screening.pdf"),
            [
                "Screening for Chronic Obstructive Pulmonary Disease 2022\n"
                "US Preventive Services Task Force Recommendation Statement"
                for _ in range(6)
            ],
            corpus,
            "Screening for Chronic Obstructive Pulmonary Disease",
        )
        producer = clean_producer()
        producer["dirty"] = dirty
        extract.write_manifest(
            corpus,
            [record],
            Path("C:/outside/guidelines-src"),
            producer=producer,
        )
        if dirty:
            manifest_path = corpus / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["producer"].pop("inputs")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return corpus

    def _run(self, root: Path, corpus: Path, catalog: str, *, allow: bool) -> tuple[int, str]:
        catalog_path = root / "catalog.md"
        audit_path = root / "audit.md"
        catalog_path.write_text(catalog, encoding="utf-8")
        audit_path.write_text(AUDIT, encoding="utf-8")
        arguments = [
            "--catalog", str(catalog_path),
            "--audit", str(audit_path),
            "--src", str(corpus),
            "--pdf-src", str(root / "absent-pdfs"),
        ]
        if allow:
            arguments.insert(0, "--allow-untrusted-provenance")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            status = gc.main(arguments)
        return status, output.getvalue()

    def test_an_undeclared_untrusted_audit_reports_shape_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = self._corpus(root, dirty=True)
            status, output = self._run(root, corpus, self._catalog(), allow=True)

        self.assertEqual(status, 0, output)
        self.assertIn("shape only", output)
        self.assertNotIn("row(s) against", output)

    def test_an_exact_declaration_holds_the_untrusted_audit_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = self._corpus(root, dirty=True)
            declaration = artifact_provenance.render_accepted_distrust(
                corpus,
                (
                    "records no producer-file identity",
                    "was produced by a dirty checkout",
                ),
            )
            status, output = self._run(
                root, corpus, self._catalog(declaration), allow=True
            )

        self.assertEqual(status, 0, output)
        self.assertIn(f"against {corpus}", output)

    def test_a_declaration_for_different_distrust_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = self._corpus(root, dirty=True)
            declaration = artifact_provenance.render_accepted_distrust(
                corpus, ("has no producer provenance stamp",)
            )
            status, output = self._run(
                root, corpus, self._catalog(declaration), allow=True
            )

        self.assertEqual(status, 1, output)
        self.assertIn("different distrust", output)

    def test_a_trusted_audit_pass_refuses_until_the_declaration_is_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = self._corpus(root, dirty=False)
            declaration = artifact_provenance.render_accepted_distrust(
                corpus, ("was produced by a dirty checkout",)
            )
            status, output = self._run(
                root, corpus, self._catalog(declaration), allow=False
            )

        self.assertEqual(status, 1, output)
        self.assertIn("delete the accepted distrust", output)


class CheckShape(unittest.TestCase):
    def test_an_unsettled_cell_nobody_listed_fails(self):
        failures = gc.check_shape([row(population="?")], {})
        self.assertTrue(any("is not listed under" in f for f in failures))

    def test_an_unsettled_cell_that_is_listed_passes(self):
        self.assertEqual(
            gc.check_shape([row(population="?")], {"copd-screening.pdf": {"population"}}), []
        )

    def test_a_listing_for_a_cell_the_table_fills_fails(self):
        failures = gc.check_shape([row()], {"copd-screening.pdf": {"population"}})
        self.assertTrue(any("but the table fills it" in f for f in failures))

    def test_a_listing_for_a_file_with_no_row_fails(self):
        failures = gc.check_shape([row()], {"gone.pdf": {"population"}})
        self.assertTrue(any("with no table row" in f for f in failures))

    def test_an_unknown_class_fails(self):
        failures = gc.check_shape([row(cls="review")], {})
        self.assertTrue(any("is not one of" in f for f in failures))

    def test_a_year_that_is_not_a_year_fails(self):
        failures = gc.check_shape([row(year="2022a")], {})
        self.assertTrue(any("not a 4-digit year" in f for f in failures))

    def test_a_column_that_may_not_be_unsettled_fails(self):
        failures = gc.check_shape([row(society="?")], {"copd-screening.pdf": {"society"}})
        self.assertTrue(any("society may not be ?" in f for f in failures))

    def test_an_empty_cell_fails(self):
        failures = gc.check_shape([row(topic="")], {})
        self.assertTrue(any("topic is empty" in f for f in failures))


class Rendering(unittest.TestCase):
    def test_a_rendered_table_parses_back_to_the_same_rows(self):
        original = [row(), row(filename="other.pdf", title="Adults | Vaccines | CDC")]
        text = "# x\n\n" + gc.render_table(original) + "\n"
        parsed, _, problems = gc.parse_catalog(text)
        self.assertEqual(problems, [])
        self.assertEqual(parsed, original)


class TheHeaderAgreesWithTheColumnBeneathIt(unittest.TestCase):
    """The catalog's opening paragraph states a corpus size, and nothing checked it.

    It read *"roughly 6,800 pages"* while the `page_count` column it sits above
    summed to **7,733** -- a 933-page contradiction inside one file, in the one
    committed artifact three other tickets read. Found in the tracker sweep on
    #223's branch, 2026-08-18, and it is [#106]'s own subject arriving in the half
    that ticket puts under *Not in scope*: the column is re-derived on every
    `guidelines_catalog.py` run and the prose beside it was checked by nothing.

    **The header states the derived figure now, so this asserts agreement rather
    than a constant.** A corpus refresh moves both together or fails here.
    """

    CATALOG = TESTDATA.parent.parent / "reference" / "guidelines-catalog.md"

    def _rows(self) -> list[list[str]]:
        rows = []
        for line in self.CATALOG.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and ".pdf" in line:
                rows.append([cell.strip() for cell in line.strip("|").split("|")])
        return rows

    def test_the_document_count_in_the_header_is_the_number_of_rows(self):
        rows = self._rows()
        self.assertEqual(len(rows), 180)
        self.assertIn(f"{len(rows)} PDFs", self.CATALOG.read_text(encoding="utf-8"))

    def test_the_page_total_in_the_header_is_the_column_sum(self):
        total = sum(int(cells[6]) for cells in self._rows())
        self.assertEqual(total, 7749)
        self.assertIn(f"{total:,} pages", self.CATALOG.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
