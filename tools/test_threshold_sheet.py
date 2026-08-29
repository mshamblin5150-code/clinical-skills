"""Tests for tools/threshold_sheet.py.

**Synthetic sheets built in this file drive the gate tests.** The one explicit
exception grades the committed set only to pin the command's loud/quiet line-count
contract; it does not use that run as evidence that the sheets or gates are correct.
That is `test_icd10.py`'s reasoning: a test reading the sheet its own gates passed
would pass for two reasons, one of them being that the sheet and the grader are wrong
together. `reference/thresholds/hypertension.md` is graded by running the command,
which is one line a reader can run and check.

Two classes matter more than the rest. ``RangeGate`` pins each of the ten false
positives the first version produced on that real sheet -- every one of them was a
number in a unit the row was not about. ``ConflictRule`` pins the clinician's ruling
that two populations disagreeing is not a conflict, which is the one rule here that
came from outside the corpus.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import artifact_lock  # noqa: E402
import artifact_provenance  # noqa: E402
import guidelines_extract as extract  # noqa: E402
from guidelines_recs_test_support import trust_recommendation_record  # noqa: E402
from guidelines_manifest_test_support import (  # noqa: E402
    ReadingManifestConformance,
    write_trusted_extraction_manifest,
)
import threshold_sheet as gate  # noqa: E402


def grade(
    sheet_path: Path,
    recs_arguments: list[str] | None,
    pdf_root: Path | None,
    quiet: bool = False,
    recs_root: Path | None = None,
    text_root: Path | None = None,
    second_read_path: Path | None = None,
    allow_untrusted_provenance: bool = False,
) -> int:
    """Exercise the separated survey and command emitter with the old test inputs."""
    scan = gate.survey(
        sheet_path,
        recs_arguments,
        pdf_root,
        recs_root,
        text_root,
        second_read_path,
        allow_untrusted_provenance,
        {
            "Society/doc": 60,
            "Society/aha": 60,
            "Society/kdigo": 60,
        },
    )
    return gate._emit_scan(scan, quiet=quiet)


def header(mode: str = "exact") -> str:
    """The sheet preamble, with the source's declared mode parameterized.

    Parameterized because gate_coverage now cross-checks the sheet's declared mode
    against the recommendation record's, so a fixture hard-coding `exact` cannot be
    used to test the `bound` path -- it would fail on the disagreement rather than on
    the thing under test. That mismatch is itself a finding now, and it has its own
    test below.
    """
    return HEADER.replace("| 2025 | 2025 | https://example.invalid | exact |",
                          f"| 2025 | 2025 | https://example.invalid | {mode} |")


TEST_PDF_ROOT = Path(__file__).resolve().parent.as_posix()


HEADER = f"""# Test sheet

{gate.SCHEMA_MARKER}

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| src | AHA/ACC | Society/doc | 2025 | 2025 | https://example.invalid | exact |

## Scope

**Read:** the recommendation tables.

**Not read:** the narrative sections and the appendices.

| span | pages | read |
| --- | --- | --- |
| recommendation tables | 1-50 | yes |
| narrative sections and appendices | 51-60 | no |

citations resolved against {TEST_PDF_ROOT} on 2026-08-16
extraction identity: producer {'a' * 40}; tools/guidelines_extract.py sha256 {'b' * 64}

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |
| adults-ckd | adults with chronic kidney disease |

## Quantities

| key | verbatim |
| --- | --- |
| bp-goal | blood pressure goal |
"""


def sheet(rows: str, conflicts: str = "", coverage: str = "", mode: str = "exact") -> gate.Sheet:
    text = (
        header(mode)
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + rows
        + "\n## Conflicts\n\n"
        + conflicts
        + "\n## Coverage\n\n"
        + coverage
    )
    return gate.parse(text, Path("test-sheet.md"))


def row(quantity="bp-goal", population="adults", value="<130 mm Hg",
        snippet="an SBP goal of <130 mm Hg", page="p41", rec="p41/goal/1", klass="1",
        source="src") -> str:
    return (
        f"| {quantity} | {population} | {value} | \"{snippet}\" | {source} | {page} "
        f"| {rec} | {klass} |\n"
    )


def _mixed_tier0_marker_sources(sheet_: gate.Sheet) -> tuple[set[str], set[str]]:
    """Return marked exact and non-exact sources when both classes are present."""
    marked_sources = {
        item.source
        for item in sheet_.rows
        if item.snippet.startswith(gate.RENDERED_MARKER)
    }
    marked_exact = {
        key
        for key in marked_sources
        if sheet_.sources.get(key, {}).get("mode") == gate.MODE_EXACT
    }
    marked_non_exact = marked_sources - marked_exact
    if marked_exact and marked_non_exact:
        return marked_exact, marked_non_exact
    return set(), set()


def conflicting_rows(second_value: str = "<120 mm Hg") -> str:
    return row(value="<130 mm Hg") + row(
        value=second_value, page="p50", rec="p50/goal/1"
    )


# A two-source sheet, which is what #177 is about: until that ticket the grader took
# one recommendation record for the whole sheet, so whichever source `--recs` did not
# name went omission-unchecked and nothing said so. Every fixture in this file had
# one source, which is why no test could express the defect.
TWO_SOURCE_HEADER = f"""# Test sheet

{gate.SCHEMA_MARKER}

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| aha | AHA/ACC | Society/aha | 2025 | 2025 | https://example.invalid | exact |
| kdigo | KDIGO | Society/kdigo | 2021 | 2021 | https://example.invalid | exact |

## Scope

**Read:** the recommendation tables.

**Not read:** the narrative sections and the appendices.

**Source: `aha`**

| span | pages | read |
| --- | --- | --- |
| recommendation tables | 1-50 | yes |
| narrative sections and appendices | 51-60 | no |

**Source: `kdigo`**

| span | pages | read |
| --- | --- | --- |
| recommendation tables | 1-50 | yes |
| narrative sections and appendices | 51-60 | no |

citations resolved against {TEST_PDF_ROOT} on 2026-08-16
extraction identity: producer {'a' * 40}; tools/guidelines_extract.py sha256 {'b' * 64}

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |
| adults-ckd | adults with chronic kidney disease |

## Quantities

| key | verbatim |
| --- | --- |
| bp-goal | blood pressure goal |
"""


def two_source_sheet(rows: str, coverage: str = "", header_text: str = "") -> gate.Sheet:
    text = (
        (header_text or TWO_SOURCE_HEADER)
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + rows
        + "\n## Conflicts\n\n"
        + "\n## Coverage\n\n"
        + coverage
    )
    return gate.parse(text, Path("test-sheet.md"))


def record(*rec_ids: str, mode: str = "exact", doc_id: str = "Society/doc",
           built_from: str | None = None, cor: dict[str, str] | None = None) -> dict:
    """A `guidelines_recs.py` record. ``cor`` gives a class where a test needs one.

    ``built_from`` is the ``source`` field -- the PDF the record was extracted from --
    and it is left off by default so the document cross-check stays out of the way of
    the tests that are not about it. That check claims nothing where the record is
    silent, which is what makes leaving it off legitimate rather than convenient.
    """
    cor = cor or {}
    record_ = {
        "doc_id": doc_id,
        "mode": mode,
        "recommendations": [{"rec_id": rec_id, "cor": cor.get(rec_id)} for rec_id in rec_ids],
    }
    if built_from is not None:
        record_["source"] = built_from
    return trust_recommendation_record(record_)


class Parsing(unittest.TestCase):
    def test_a_sheet_without_the_marker_is_not_graded_rather_than_clean(self):
        """The #153 shape at the file level. A sheet the parser cannot read must not
        report zero violations."""
        parsed = gate.parse("# Not a sheet\n\nsome prose\n", Path("x.md"))
        self.assertFalse(parsed.ok)
        self.assertIn("marker", parsed.why_not)

    def test_a_sheet_with_the_marker_but_no_rows_is_not_graded_either(self):
        parsed = gate.parse(HEADER, Path("x.md"))
        self.assertFalse(parsed.ok)
        self.assertIn("no row", parsed.why_not)

    def test_a_pipe_row_outside_the_thresholds_section_is_not_a_threshold(self):
        """The load-bearing parser choice, and `block_scan.py`'s rule adopted whole.

        A sheet's own prose discusses its rules, and the README beside it is full of
        example rows. A parser matching a row shape anywhere would read the
        explanation of a threshold as a threshold.
        """
        parsed = sheet(row())
        self.assertEqual(len(parsed.rows), 1)
        self.assertEqual(len(parsed.sources), 1)
        self.assertEqual(len(parsed.populations), 2)
        self.assertEqual(parsed.quantities, {"bp-goal": "blood pressure goal"})


class SchemaGate(unittest.TestCase):
    def test_an_undeclared_quantity_key_fails(self):
        result = gate.gate_schema(sheet(row(quantity="screening-interval")))
        self.assertTrue(
            any("'## Quantities'" in message for message in result.findings),
            result.findings,
        )

    def test_an_undeclared_population_key_fails(self):
        """The key is the whole conflict mechanism, so an undeclared one is not a
        typo -- it is a row that can never be compared with any other."""
        result = gate.gate_schema(sheet(row(population="adults-pregnancy")))
        failures = result.findings
        self.assertTrue(any("not declared" in message for message in failures))

    def test_an_undeclared_source_key_fails(self):
        parsed = sheet(row())
        parsed.rows = [parsed.rows[0].__class__(**{**parsed.rows[0].__dict__, "source": "ghost"})]
        self.assertTrue(
            any(
                "'## Sources'" in message
                for message in gate.gate_schema(parsed).findings
            )
        )

    def test_a_source_locator_must_have_page_kind_and_identifier_segments(self):
        findings = gate.gate_schema(sheet(row(rec="recommendation-1"))).findings

        self.assertTrue(any("source locator" in finding for finding in findings), findings)

    def test_a_source_locator_page_must_match_the_page_column(self):
        findings = gate.gate_schema(
            sheet(row(page="p41", rec="p42/recommendation/1"))
        ).findings

        self.assertTrue(any("page column" in finding for finding in findings), findings)

    def test_a_symbol_font_pound_sign_in_a_value_fails(self):
        """A less-or-equal sign that lost its encoding. A sheet holds the fact and
        must not hold the mis-encoding."""
        result = gate.gate_schema(sheet(row(value="\u00a3120 mm Hg")))
        failures = result.findings
        self.assertTrue(any("Symbol-font" in message for message in failures))

    def test_every_slot_the_extractor_repairs_is_refused_here_too(self):
        """#172 found the gate reaching half its own subject.

        It blocked ``\u00a3`` and ``\u00b3`` and not the double dagger -- and the double
        dagger is where most of the corpus's greater-or-equal signs landed, so a
        transcriber pasting ``\u20216 months`` cleared a gate written to stop exactly
        that. The two C0 controls are worse again: invisible, and a value cell can
        carry one with nothing on screen to see. **The counts live on
        ``guidelines_extract.SYMBOL_FONT_OPERATORS`` and are not restated here.**

        Derived from ``guidelines_extract.SYMBOL_FONT_OPERATORS`` rather than
        listed, on ``test_spelling_scan.py``'s reasoning -- a sixth slot added to
        the extractor and not here would leave this passing while the artifact it
        guards could hold the character.

        The destructive C0 controls are refused at the raw-input seam before Python can erase
        them; every other slot is refused from the parsed value.
        """
        for mapping in extract.SYMBOL_FONT_OPERATORS.values():
            for glyph in mapping:
                with self.subTest(glyph=f"U+{ord(glyph):04X}"):
                    parsed = sheet(row(value=f"{glyph}120 mm Hg"))
                    if glyph in gate.FORBIDDEN_IN_RAW_TEXT:
                        self.assertFalse(parsed.ok)
                    else:
                        result = gate.gate_schema(parsed)
                        failures = result.findings
                        self.assertTrue(
                            any("mis-encoding" in message for message in failures),
                            f"U+{ord(glyph):04X} passed the value gate",
                        )


class RawInputOperatorGate(unittest.TestCase):
    """#285 refuses #172's destructive C0 controls before Python can erase them.

    ``U+001E`` and ``U+001F`` are the greater- and less-or-equal signs of one
    AHA/ACC document. They cannot be refused in a parsed value cell, for two separate
    reasons that are both Python's rather than this module's. The raw-input seam sees
    both, preserves the source row, and refuses to guess which operator was meant.

    The error directs an agent to render the cited PDF page, visually verify the
    operator, and write the explicit ASCII form. The parser never rewrites clinical
    meaning automatically.
    """

    def test_the_raw_gate_is_narrowly_the_destructive_slots(self):
        self.assertEqual(set(gate.FORBIDDEN_IN_RAW_TEXT), {"\u001e", "\u001f"})

    def test_the_operator_is_refused_before_cell_trimming_can_eat_it(self):
        """The raw-input refusal preserves the sheet line that needs a visual read."""
        parsed = sheet(row(value="\u001f120 mm Hg"))
        self.assertFalse(parsed.ok)
        self.assertIn("test-sheet.md:42", parsed.why_not)
        self.assertIn("U+001F", parsed.why_not)
        self.assertIn("PyMuPDF", parsed.why_not)

    def test_the_row_is_refused_before_line_splitting_can_erase_it(self):
        """The raw-input refusal preserves the locator for a row splitlines loses."""
        self.assertEqual("a\u001eb".splitlines(), ["a", "b"])
        parsed = sheet(row(value="\u001e120 mm Hg"))
        self.assertFalse(parsed.ok)
        self.assertIn("test-sheet.md:42", parsed.why_not)
        self.assertIn("U+001E", parsed.why_not)
        self.assertIn("PyMuPDF", parsed.why_not)

    def test_a_unicode_comparison_sign_in_a_value_fails(self):
        result = gate.gate_schema(sheet(row(value="\u2265130 mm Hg")))
        failures = result.findings
        self.assertTrue(any("ASCII" in message for message in failures))

    def test_a_verbatim_snippet_may_keep_the_unicode_sign_the_value_may_not(self):
        """The asymmetry is deliberate and it is the point of having two columns.

        A snippet is a citation anchor and must match the page exactly, typography
        included. A value is what a clinician reads back, and it is normalized.
        """
        result = gate.gate_schema(
            sheet(row(value=">=130 mm Hg", snippet="average SBP is \u2265130 mm Hg"))
        )
        failures = result.findings
        self.assertEqual(failures, [])


class ConflictRule(unittest.TestCase):
    def test_same_quantity_and_population_with_different_values_needs_a_conflict_block(self):
        result = gate.gate_schema(sheet(conflicting_rows()))
        failures = result.findings
        self.assertTrue(any("CONFLICT" in message for message in failures))

    def test_a_conflict_block_that_names_both_values_satisfies_it(self):
        parsed = sheet(
            conflicting_rows(),
            conflicts=(
                "**CONFLICT: bp-goal** - one recommendation says below 130 mm Hg; "
                "the other says <120 mm Hg.\n"
            ),
        )
        self.assertEqual(gate.gate_schema(parsed).findings, [])

    def test_a_conflict_block_that_names_only_one_value_fails(self):
        parsed = sheet(
            conflicting_rows(),
            conflicts="**CONFLICT: bp-goal** - one recommendation says <130 mm Hg.\n",
        )
        result = gate.gate_schema(parsed)
        failures = result.findings
        self.assertTrue(any("<120 mm Hg" in message for message in failures), failures)

    def test_a_todo_conflict_block_does_not_discharge_the_rule(self):
        result = gate.gate_schema(
            sheet(conflicting_rows(), conflicts="**CONFLICT: bp-goal** - TODO\n")
        )
        failures = result.findings
        self.assertTrue(any("CONFLICT" in message for message in failures), failures)

    def test_one_longer_value_mention_cannot_satisfy_two_distinct_rows(self):
        """The suffix of one value is not evidence that the other was compared."""
        parsed = sheet(
            conflicting_rows("<130 mm Hg in clinic"),
            conflicts="**CONFLICT: bp-goal** - below 130 mm Hg in clinic.\n",
        )
        result = gate.gate_schema(parsed)
        failures = result.findings
        self.assertTrue(any("<130 mm Hg" in message for message in failures), failures)

    def test_the_live_blocks_pass_and_the_instrument_reads_their_prose(self):
        """#182's two correct blocks are the acceptance material, not imagined prose.

        The mutation is the live-instrument half: a predicate that merely notices the
        quantity key would leave the second assertion green after the prose vanished.
        """
        path = Path(__file__).resolve().parents[1] / "reference" / "thresholds" / "hypertension.md"
        parsed = gate.parse(path.read_text(encoding="utf-8"), path)
        self.assertEqual(gate.gate_schema(parsed).findings, [])

        parsed.conflicts["acute-stroke-bp-treatment-threshold"] = "- TODO"
        result = gate.gate_schema(parsed)
        failures = result.findings
        self.assertTrue(any("acute-stroke-bp-treatment-threshold" in message for message in failures))

    def test_different_populations_are_not_a_conflict(self):
        """The clinician's ruling, made mechanical.

        KDIGO targets SBP <120 in CKD and AHA/ACC targets <130/80 in general adults.
        Those are two rows about two patients, and calling them a contradiction would
        be the sheet inventing one. This is the reason the population key exists at
        all -- without it this case is indistinguishable from the one above.
        """
        rows = (
            row(quantity="bp-goal", population="adults", value="<130 mm Hg")
            + row(
                quantity="bp-goal",
                population="adults-ckd",
                value="<120 mm Hg",
                page="p50",
                rec="p50/goal/1",
            )
        )
        self.assertEqual(gate.gate_schema(sheet(rows)).findings, [])

    def test_the_same_value_stated_twice_is_not_a_conflict(self):
        """A guideline restates its own targets in several sections, so a sheet
        legitimately carries the same number from several recommendations."""
        rows = row(rec="p41/goal/1") + row(page="p48", rec="p48/goal/1")
        self.assertEqual(gate.gate_schema(sheet(rows)).findings, [])


class CitationTier1(unittest.TestCase):
    def test_a_value_whose_number_is_absent_from_its_snippet_fails(self):
        result = gate.gate_citation_tier1(
            sheet(row(value="<140 mm Hg", snippet="an SBP goal of <130 mm Hg"))
        )
        failures = result.findings
        self.assertEqual(len(failures), 1)
        self.assertIn("140", failures[0])

    def test_a_value_with_no_number_is_not_checked(self):
        """`monthly` and `once daily` are real rows in the first sheet. A gate that
        demanded a digit would refuse a correct row."""
        self.assertEqual(
            gate.gate_citation_tier1(
                sheet(row(value="monthly", snippet="at monthly intervals"))
            ).findings,
            [],
        )

    def test_it_runs_with_no_pdfs_anywhere(self):
        """The whole reason tier 1 exists. Decision 2: there must be no machine on
        which citation checking drops to zero."""
        result = gate.gate_citation_tier2(
            sheet(row()), Path("C:/nowhere-at-all")
        )
        failures, skipped, rendered = result.findings, result.skip_reason, result.rendered
        self.assertEqual(failures, [])
        self.assertIsNotNone(skipped)
        self.assertEqual(rendered, 0)
        self.assertEqual(gate.gate_citation_tier1(sheet(row())).findings, [])


class TierTwoHoldsItsResolutionDeclaration(unittest.TestCase):
    @staticmethod
    def require_pymupdf():
        try:
            import pymupdf
        except ImportError:
            raise unittest.SkipTest("pymupdf absent; tier 2 cannot produce a verdict")
        return pymupdf

    @staticmethod
    def parsed(text: str = HEADER) -> gate.Sheet:
        return gate.parse(
            text
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(page="p1"),
            Path("test-sheet.md"),
        )

    @staticmethod
    @contextlib.contextmanager
    def live_pdf_root():
        pymupdf = TierTwoHoldsItsResolutionDeclaration.require_pymupdf()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf_path = root / "Society" / "doc.pdf"
            pdf_path.parent.mkdir()
            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((72, 72), "an SBP goal of <130 mm Hg")
            document.save(pdf_path)
            document.close()
            yield root

    def test_a_skipped_run_refuses_a_missing_resolution_declaration(self):
        text = HEADER.replace(
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16\n",
            "",
        )
        parsed = self.parsed(text)

        result = gate.gate_citation_tier2(parsed, Path("C:/nowhere-at-all"))

        self.assertIsNotNone(result.skip_reason)
        self.assertTrue(
            any("resolution" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_a_resolution_mention_outside_scope_cannot_satisfy_the_hold(self):
        text = HEADER.replace(
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16\n",
            "",
        )
        parsed = self.parsed(
            text
            + "\nA footer mentions citations resolved against C:/fiction on 2026-08-16.\n"
        )

        result = gate.gate_citation_tier2(parsed, Path("C:/nowhere-at-all"))

        self.assertTrue(
            any("resolution" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_a_missing_declaration_exits_one_even_when_tier_two_skips(self):
        text = HEADER.replace(
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16\n",
            "",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(
                text
                + "\n## Thresholds\n\n"
                + "| quantity | population | value | snippet | source | page | rec | class |\n"
                + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + row(page="p1"),
                encoding="utf-8",
            )
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = grade(path, [], Path(directory) / "absent", quiet=True)

        self.assertEqual(status, 1)
        self.assertIn("CITATION tier 2", err.getvalue())

    def test_a_live_failing_verdict_also_refuses_a_missing_declaration(self):
        self.require_pymupdf()
        text = HEADER.replace(
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16\n",
            "",
        )

        result = gate.gate_citation_tier2(
            self.parsed(text),
            Path(__file__).resolve().parent,
        )

        self.assertIsNone(result.skip_reason)
        self.assertTrue(any("no such PDF" in finding for finding in result.findings))
        self.assertTrue(
            any("resolution" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_corpus_disagreement_prints_beside_a_failing_live_verdict(self):
        self.require_pymupdf()
        fictional = HEADER.replace(TEST_PDF_ROOT, "C:/nowhere")

        result = gate.gate_citation_tier2(
            self.parsed(fictional),
            Path(__file__).resolve().parent,
        )

        self.assertTrue(any("no such PDF" in finding for finding in result.findings))
        self.assertTrue(
            any("different corpus" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_a_live_run_refuses_the_existing_fictional_fixture_path(self):
        with self.live_pdf_root() as root:
            fictional = HEADER.replace(TEST_PDF_ROOT, "C:/nowhere")
            result = gate.gate_citation_tier2(self.parsed(fictional), root)

        self.assertTrue(
            any("different corpus" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_a_live_run_refuses_a_future_resolution_date(self):
        with self.live_pdf_root() as root:
            text = HEADER.replace(
                f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16",
                f"citations resolved against {root.as_posix()} on 9999-12-31",
            )

            result = gate.gate_citation_tier2(self.parsed(text), root)

        self.assertTrue(
            any("future" in finding.lower() for finding in result.findings),
            result.findings,
        )

    def test_a_matching_older_declaration_adds_no_finding(self):
        self.require_pymupdf()
        result = gate.gate_citation_tier2(
            self.parsed(),
            Path(__file__).resolve().parent,
        )

        self.assertFalse(
            any(
                phrase in finding.lower()
                for finding in result.findings
                for phrase in ("resolution declaration", "different corpus", "future")
            ),
            result.findings,
        )

    def test_the_page_gate_uses_the_same_repaired_reader_as_marker_records(self):
        words = ("an", "SBP", "goal", "of", "<130", "mm", "Hg")
        glyph_text = "".join(words)
        boundaries: set[int] = set()
        offset = 0
        for word in words[:-1]:
            offset += len(word)
            boundaries.add(offset - 1)
        chars: list[dict] = []
        cursor = 0.0
        for index, glyph in enumerate(glyph_text):
            chars.append(
                {
                    "c": glyph,
                    "origin": (cursor, 10.0),
                    "bbox": (cursor, 0.0, cursor + 5.0, 10.0),
                }
            )
            cursor += 5.0 + (4.0 if index in boundaries else 0.0)
        raw = {
            "blocks": [
                {
                    "type": 0,
                    "lines": [{"spans": [{"size": 10.0, "chars": chars}]}],
                }
            ]
        }

        class FakePage:
            def get_text(self, kind="text"):
                return raw if kind == "rawdict" else glyph_text

        class FakeDocument:
            def __getitem__(self, _index):
                return FakePage()

            def close(self):
                pass

        class FakePyMuPDF:
            @staticmethod
            def open(_path):
                return FakeDocument()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "Society" / "doc.pdf"
            path.parent.mkdir()
            path.write_bytes(b"stubbed PDF boundary")
            sheet_text = HEADER.replace(TEST_PDF_ROOT, root.as_posix())
            parsed = self.parsed(sheet_text)
            with mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}):
                result = gate.gate_citation_tier2(parsed, root)

        self.assertEqual(result.findings, [])


class CitationTier0(unittest.TestCase):
    def recs(self, text: str, *, mode: str = "exact") -> dict:
        return {
            "mode": mode,
            "recommendations": [
                {
                    "rec_id": "p41/goal/1",
                    "text": text,
                }
            ],
        }

    def test_an_exact_source_refuses_a_snippet_absent_from_its_own_record(self):
        result = gate.gate_citation_tier0(
            sheet(row(snippet="fabricated <130 mm Hg")),
            {"src": self.recs("an SBP goal of <130 mm Hg")},
            {},
        )

        self.assertEqual(len(result.findings), 1)
        self.assertIn("not in its recommendation record", result.findings[0])
        self.assertFalse(result.not_graded)

    def test_an_exact_source_passes_the_same_text_under_the_auditors_normalization(self):
        result = gate.gate_citation_tier0(
            sheet(row(snippet="an SBP goal of <130 mm Hg")),
            {"src": self.recs("An SBP goal of <130\u00a0mm Hg is recommended")},
            {},
        )

        self.assertEqual(result.findings, [])
        self.assertFalse(result.not_graded)
        self.assertEqual(result.report, ("  CITATION tier 0 0",))

    def test_a_bound_source_reports_not_run_and_never_passes(self):
        result = gate.gate_citation_tier0(
            sheet(row(), mode="bound"),
            {"src": self.recs("an SBP goal of <130 mm Hg", mode="bound")},
            {},
        )

        self.assertEqual(result.findings, [])
        self.assertTrue(result.not_graded)
        self.assertIn("NOT RUN", result.report[0])
        self.assertIn("bound", result.report[0])

    def test_a_rendered_snippet_is_exempt_and_counted(self):
        result = gate.gate_citation_tier0(
            sheet(row(snippet="RENDERED: an SBP goal of <130 mm Hg")),
            {"src": self.recs("different record text")},
            {},
        )

        self.assertEqual(result.findings, [])
        self.assertEqual(result.rendered, 1)
        self.assertIn("1 row(s) declared RENDERED:", "\n".join(result.report))

    def test_one_textless_exact_record_does_not_hide_another_rows_fabrication(self):
        parsed = sheet(
            row(rec="p41/goal/1", snippet="first <130 mm Hg")
            + row(rec="p41/goal/2", snippet="fabricated <120 mm Hg")
        )
        result = gate.gate_citation_tier0(
            parsed,
            {
                "src": {
                    "mode": "exact",
                    "recommendations": [
                        {"rec_id": "p41/goal/1", "text": ""},
                        {"rec_id": "p41/goal/2", "text": "actual <120 mm Hg"},
                    ],
                }
            },
            {},
        )

        self.assertEqual(len(result.findings), 2)
        self.assertTrue(any("has no text" in finding for finding in result.findings))
        self.assertTrue(any("not in its recommendation" in finding for finding in result.findings))

    def test_a_repeated_identifier_checks_every_record_occurrence(self):
        result = gate.gate_citation_tier0(
            sheet(row(snippet="an SBP goal of <130 mm Hg")),
            {
                "src": {
                    "mode": "exact",
                    "recommendations": [
                        {
                            "rec_id": "p41/goal/1",
                            "text": "an SBP goal of <130 mm Hg is recommended",
                        },
                        {"rec_id": "p41/goal/1", "text": "another occurrence"},
                    ],
                }
            },
            {},
        )

        self.assertEqual(result.findings, [])

    def test_a_narrative_locator_is_outside_the_recommendation_index(self):
        result = gate.gate_citation_tier0(
            sheet(row(rec="p41/narrative/1", klass="narrative")),
            {"src": self.recs("different recommendation text")},
            {},
        )

        self.assertEqual(result.findings, [])

    def test_a_narrative_page_transcription_inside_a_same_page_record_refuses(self):
        recs = {
            "mode": "exact",
            "recommendations": [
                {
                    "rec_id": "p41/goal/1",
                    "page": 41,
                    "text": "an SBP goal of <130 mm Hg is recommended",
                }
            ],
        }
        result = gate.gate_citation_tier0(
            sheet(
                row(
                    rec="p41/narrative/1",
                    klass="narrative",
                    snippet="RENDERED: an SBP goal of <130 mm Hg",
                )
            ),
            {"src": recs},
            {},
        )

        self.assertTrue(any("page transcription" in finding for finding in result.findings))

    def test_plain_narrative_text_inside_a_same_page_record_refuses(self):
        recs = {
            "mode": "exact",
            "recommendations": [
                {
                    "rec_id": "p41/goal/1",
                    "page": 41,
                    "text": "an SBP goal of <130 mm Hg is recommended",
                }
            ],
        }
        result = gate.gate_citation_tier0(
            sheet(row(rec="p41/narrative/1", klass="narrative")),
            {"src": recs},
            {},
        )

        self.assertTrue(any("page transcription" in finding for finding in result.findings))

    def test_the_narrative_negative_check_is_page_scoped(self):
        recs = {
            "mode": "exact",
            "recommendations": [
                {
                    "rec_id": "p42/goal/1",
                    "page": 42,
                    "text": "an SBP goal of <130 mm Hg is recommended",
                }
            ],
        }
        result = gate.gate_citation_tier0(
            sheet(row(rec="p41/narrative/1", klass="narrative")),
            {"src": recs},
            {},
        )

        self.assertEqual(result.findings, [])

    def test_a_textless_cited_recommendation_does_not_hide_a_narrative_collision(self):
        parsed = sheet(
            row(rec="p41/goal/1", snippet="unavailable recommendation text")
            + row(
                rec="p41/narrative/1",
                klass="narrative",
                snippet="an SBP goal of <130 mm Hg",
            )
        )
        recs = {
            "mode": "exact",
            "recommendations": [
                {"rec_id": "p41/goal/1", "page": 41, "text": ""},
                {
                    "rec_id": "p41/goal/2",
                    "page": 41,
                    "text": "an SBP goal of <130 mm Hg is recommended",
                },
            ],
        }

        result = gate.gate_citation_tier0(parsed, {"src": recs}, {})

        self.assertTrue(any("page transcription" in item for item in result.findings))
        self.assertTrue(result.not_graded)

    def test_an_incomplete_record_population_cannot_clean_pass_the_narrative_check(self):
        for incomplete_item in (
            {"rec_id": "p41/goal/1", "text": "different text"},
            {"rec_id": "p41/goal/1", "page": 41, "text": ""},
        ):
            with self.subTest(incomplete_item=incomplete_item):
                result = gate.gate_citation_tier0(
                    sheet(row(rec="p41/narrative/1", klass="narrative")),
                    {"src": {"mode": "exact", "recommendations": [incomplete_item]}},
                    {},
                )

                self.assertEqual(result.findings, [])
                self.assertTrue(result.not_graded)
                self.assertIn("narrative negative check", result.report[0])

    def test_the_aaa_ever_smoker_definition_needs_no_fabricated_recommendation_id(self):
        recommendation_rows = "".join(
            row(
                value="65 years",
                snippet=f"screening arm {number} begins at 65 years",
                page="p1",
                rec=f"p1/aaa/{number}",
                klass="B",
            )
            for number in range(1, 5)
        )
        narrative_row = row(
            value="100 cigarettes",
            snippet="ever smoking is commonly defined as 100 cigarettes",
            page="p3",
            rec="p3/narrative/1",
            klass="narrative",
        )
        parsed = sheet(recommendation_rows + narrative_row)
        recs = {
            "doc_id": "USPSTF/abdominal-aortic-aneurysm-screening",
            "mode": "exact",
            "recommendations": [
                {
                    "rec_id": f"p1/aaa/{number}",
                    "page": 1,
                    "cor": "B",
                    "text": f"screening arm {number} begins at 65 years",
                }
                for number in range(1, 5)
            ],
        }

        self.assertEqual(
            gate.gate_citation_tier0(parsed, {"src": recs}, {}).findings, []
        )
        self.assertEqual(gate.gate_coverage(parsed, {"src": recs}).findings, [])


class TierZeroRenderedCounterScope(unittest.TestCase):
    """ADR 0043 ruling 5's mixed-source tripwire and positive control."""

    def test_the_tripwire_detects_a_synthetic_mixed_mode_sheet_with_markers(self):
        mixed_header = TWO_SOURCE_HEADER.replace(
            "| kdigo | KDIGO | Society/kdigo | 2021 | 2021 | https://example.invalid | exact |",
            "| kdigo | KDIGO | Society/kdigo | 2021 | 2021 | https://example.invalid | bound |",
        )
        parsed = two_source_sheet(
            row(source="aha", snippet="RENDERED: exact-source transcription")
            + row(
                source="kdigo",
                snippet="RENDERED: bound-source transcription",
                page="p42",
                rec="p42/goal/2",
            ),
            header_text=mixed_header,
        )

        self.assertEqual(_mixed_tier0_marker_sources(parsed), ({"aha"}, {"kdigo"}))

    def test_no_committed_sheet_silently_mixes_the_tier_zero_marker_denominator(self):
        paths = sorted(
            path
            for path in gate.SHEET_ROOT.glob("*.md")
            if path.name.casefold() not in {"readme.md", "coverage.md"}
        )
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(sheet=path.name):
                parsed = gate.parse(path.read_text(encoding="utf-8"), path)
                exact, non_exact = _mixed_tier0_marker_sources(parsed)
                self.assertFalse(
                    exact or non_exact,
                    "A sheet now carries RENDERED: rows on both exact and non-exact "
                    "sources. Re-examine gate_citation_tier0's per-graded-source "
                    "rendered counter before accepting its printed denominator: "
                    f"exact={sorted(exact)}, non-exact={sorted(non_exact)}",
                )


class EveryGateReturnsOneNamedShape(unittest.TestCase):
    def test_every_gate_returns_a_gate_result_that_names_its_gate(self):
        parsed = sheet(row())
        results = (
            ("SCHEMA", gate.gate_schema(parsed)),
            (
                "EXTRACTION IDENTITY",
                gate.gate_extraction_identity(
                    parsed,
                    gate.ExtractionIdentity("a" * 40, "b" * 64),
                ),
            ),
            ("PAGE COVERAGE", gate.gate_page_coverage(parsed, {"Society/doc": 60})),
            ("CITATION tier 0", gate.gate_citation_tier0(parsed, {}, {})),
            ("CITATION tier 1", gate.gate_citation_tier1(parsed)),
            ("CITATION tier 2", gate.gate_citation_tier2(parsed, Path("C:/nowhere"))),
            ("COVERAGE", gate.gate_coverage(parsed, {})),
            ("RANGE", gate.gate_range(parsed)),
            ("WATERMARK", gate.gate_watermark(parsed, None)),
            (
                "SECOND READ",
                gate.gate_second_read(
                    parsed,
                    gate.SecondRead(
                        Path("read.json"), values=[],
                        briefed=gate.BriefedSpan(
                            "Society/doc", "recommendation tables", 1, 50
                        ),
                        read_on="2026-08-21",
                    ),
                ),
            ),
        )

        for name, result in results:
            with self.subTest(gate=name):
                self.assertIsInstance(result, gate.GateResult)
                self.assertEqual(result.gate, name)
                self.assertIsInstance(result.findings, list)


class ExtractionIdentityGate(unittest.TestCase):
    @staticmethod
    def write_manifest(root: Path) -> gate.ExtractionIdentity:
        producer = write_trusted_extraction_manifest(root)
        assert isinstance(producer, dict)
        extractor = next(
            row["sha256"]
            for row in producer["inputs"]
            if row["path"] == "tools/guidelines_extract.py"
        )
        return gate.ExtractionIdentity(str(producer["commit"]), extractor)

    def test_the_declaration_is_parsed_from_scope(self):
        parsed = sheet(row())

        self.assertEqual(
            parsed.extraction_identity,
            gate.ExtractionIdentity("a" * 40, "b" * 64),
        )

    def test_the_current_identity_is_read_from_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = self.write_manifest(root)

            identity, problems = gate.extraction_identity_from_manifest(root)

        self.assertEqual(problems, [])
        self.assertEqual(identity, expected)

    def test_a_different_extraction_warns_without_refusing(self):
        parsed = sheet(row())
        parsed.extraction_identity = gate.ExtractionIdentity(
            "a" * 40,
            "b" * 64,
        )
        current = gate.ExtractionIdentity("c" * 40, "d" * 64)

        result = gate.gate_extraction_identity(parsed, current)

        self.assertEqual(result.findings, [])
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("test-sheet.md", result.warnings[0])
        self.assertIn("different extraction", result.warnings[0])

    def test_the_same_extraction_is_quiet(self):
        parsed = sheet(row())
        identity = gate.ExtractionIdentity("a" * 40, "b" * 64)
        parsed.extraction_identity = identity

        result = gate.gate_extraction_identity(parsed, identity)

        self.assertEqual(result.findings, [])
        self.assertEqual(result.warnings, [])

    def test_a_sheet_without_a_declaration_fails_the_format_schema(self):
        parsed = sheet(row())
        parsed.extraction_identity = None

        result = gate.gate_schema(parsed)

        self.assertTrue(
            any("has no extraction identity" in finding for finding in result.findings)
        )

    def test_an_unavailable_manifest_says_the_comparison_did_not_run(self):
        result = gate.gate_extraction_identity(
            sheet(row()),
            None,
            ["manifest is unavailable"],
        )

        self.assertEqual(result.warnings, [])
        self.assertEqual(result.skip_reason, "manifest is unavailable")
        self.assertIn("NOT RUN", result.report[0])
        self.assertIn("NOT RUN", result.diagnostics[0])

    def test_survey_compares_the_sheet_with_its_text_root_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(root)
            path = root / "sheet.md"
            path.write_text(
                HEADER
                + "\n## Thresholds\n\n"
                + "| quantity | population | value | snippet | source | page | rec | class |\n"
                + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + row(),
                encoding="utf-8",
            )

            scan = gate.survey(
                path,
                [],
                None,
                text_root=root,
                page_counts={"Society/doc": 60},
            )

        identity = next(
            result for result in scan.results if result.gate == "EXTRACTION IDENTITY"
        )
        self.assertEqual(len(identity.warnings), 1)

    def test_all_quiet_counts_and_names_the_affected_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = (root / "one.md", root / "two.md")
            for path in paths:
                path.write_text("selected", encoding="utf-8")
            scans = {
                paths[0]: gate.Scan(
                    gate.Sheet(paths[0]),
                    (
                        gate.GateResult(
                            "EXTRACTION IDENTITY",
                            warnings=["one.md was read against a different extraction"],
                        ),
                    ),
                ),
                paths[1]: gate.Scan(
                    gate.Sheet(paths[1]),
                    (gate.GateResult("EXTRACTION IDENTITY"),),
                ),
            }
            stderr = io.StringIO()
            with mock.patch.object(gate, "SHEET_ROOT", root), mock.patch.object(
                gate, "survey", side_effect=lambda path, *_, **__: scans[path]
            ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                status = gate.main(["--all", "--quiet"])

        self.assertEqual(status, 0)
        self.assertIn("EXTRACTION IDENTITY 1 affected sheet(s): one.md", stderr.getvalue())


class ACompletedScanCanBeRenderedWithoutRunningAGate(unittest.TestCase):
    def test_format_report_only_reads_the_scan_it_is_given(self):
        parsed = sheet(row())
        scan = gate.Scan(
            sheet=parsed,
            results=(gate.GateResult("SCHEMA", report=("  SCHEMA          0",)),),
            status=0,
        )

        with mock.patch.object(gate, "gate_schema", side_effect=AssertionError("gate ran")):
            report = gate.format_report(scan)

        self.assertIn("== test-sheet.md", report)
        self.assertIn("SCHEMA          0", report)

    def test_loud_cli_emission_uses_the_pure_formatter(self):
        scan = gate.Scan(
            sheet=sheet(row()),
            results=(gate.GateResult("SCHEMA", report=("  SCHEMA          0",)),),
        )
        with mock.patch.object(
            gate, "format_report", wraps=gate.format_report
        ) as formatter, contextlib.redirect_stdout(io.StringIO()):
            gate._emit_scan(scan, quiet=False)

        formatter.assert_called_once_with(scan)


class CoverageGate(unittest.TestCase):
    RECS = {
        "doc_id": "Society/doc",
        "mode": "exact",
        "recommendations": [
            {"rec_id": "p41/goal/1"},
            {"rec_id": "p41/goal/2"},
            {"rec_id": "p41/goal/3"},
        ],
    }

    def test_an_uncited_unscoped_recommendation_refuses_on_an_exact_source(self):
        parsed = sheet(row(rec="p41/goal/1"), coverage="- `p41/goal/2` - no number stated\n")
        result = gate.gate_coverage(parsed, {"src": self.RECS})
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(len(refusals), 1)
        self.assertIn("p41/goal/3", refusals[0])
        self.assertEqual(warnings, [])

    def test_an_exact_row_citing_an_identifier_its_record_does_not_carry_refuses(self):
        """[#270](https://github.com/mshamblin5150-code/clinical-skills/issues/270).

        The invented identifier used to disappear from both set differences. With
        every real recommendation accounted for, all four gates read clean.
        """
        parsed = sheet(
            row(rec="p999/invented/7"),
            coverage="".join(
                f"- `p41/goal/{number}` - no threshold stated\n" for number in (1, 2, 3)
            ),
        )
        result = gate.gate_coverage(parsed, {"src": self.RECS})
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(len(refusals), 1)
        self.assertIn("p999/invented/7", refusals[0])
        self.assertIn("does not carry", refusals[0])
        self.assertEqual(warnings, [])

    def test_the_same_omission_only_warns_on_a_bound_source(self):
        """Gate 2's two behaviors, and the mode is read off the recommendation record
        rather than decided here. A marker count over-reports, so enforcing it would
        refuse a correct sheet for recommendations that do not exist."""
        parsed = sheet(
            row(rec="p41/goal/1"),
            coverage="- `p41/goal/2` - no number stated\n",
            mode="bound",
        )
        result = gate.gate_coverage(parsed, {"src": {**self.RECS, "mode": "bound"}})
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("over-reports", warnings[0])

    def test_bound_row_membership_is_deliberately_not_graded(self):
        """A marker record can under-report, so absence from it proves nothing."""
        parsed = sheet(
            row(rec="p999/extractor-missed/7"),
            coverage="".join(
                f"- `p41/goal/{number}` - no threshold stated\n" for number in (1, 2, 3)
            ),
            mode="bound",
        )
        result = gate.gate_coverage(
            parsed, {"src": {**self.RECS, "mode": "bound"}}
        )
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [])
        self.assertIn("under-report", gate.WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED)

    def test_an_unknown_scope_out_refuses_when_every_source_record_is_exact(self):
        parsed = sheet(
            row(rec="p41/goal/1"),
            coverage=(
                "- `p41/goal/2` - no threshold stated\n"
                "- `p41/goal/3` - no threshold stated\n"
                "- `p999/invented/7` - reviewed separately\n"
            ),
        )
        result = gate.gate_coverage(parsed, {"src": self.RECS})
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(len(refusals), 1)
        self.assertIn("p999/invented/7", refusals[0])
        self.assertIn("no exact recommendation record carries it", refusals[0])
        self.assertEqual(warnings, [])

    def test_unknown_scope_out_membership_is_not_graded_for_a_bound_record(self):
        parsed = sheet(
            row(rec="p41/goal/1"),
            coverage=(
                "- `p41/goal/2` - no threshold stated\n"
                "- `p41/goal/3` - no threshold stated\n"
                "- `p999/extractor-missed/7` - reviewed separately\n"
            ),
            mode="bound",
        )
        result = gate.gate_coverage(
            parsed, {"src": {**self.RECS, "mode": "bound"}}
        )
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [])

    def test_a_sheet_declaring_a_mode_its_record_disagrees_with_is_refused(self):
        """Found in review: the `mode` column was decorative.

        `gate_coverage` read the mode off the recommendation record and never off the
        sheet, so a sheet could declare `exact` over a `bound` record and pass — while
        README.md tells a reader that column is what decides refuse-versus-warn.
        Neither value is trusted over the other, because only the disagreement is
        knowable; what produced it is not.
        """
        parsed = sheet(row(rec="p41/goal/1"), mode="exact")
        result = gate.gate_coverage(parsed, {"src": {**self.RECS, "mode": "bound"}})
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertTrue(any("declares mode" in message for message in refusals))

    def test_a_row_carrying_the_wrong_class_for_its_recommendation_is_refused(self):
        """The one check here that catches a row pinned to the WRONG recommendation.

        Every other gate passes such a row: its number is real, its snippet is on the
        page it names, and its rec_id exists. Only the class disagrees.
        """
        recs = {**self.RECS, "recommendations": [{"rec_id": "p41/goal/1", "cor": "2a"}]}
        result = gate.gate_coverage(sheet(row(rec="p41/goal/1", klass="1")), {"src": recs})
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertTrue(any("does not match" in message for message in refusals))

    def test_a_bound_source_carries_no_class_so_the_class_check_stays_quiet(self):
        """Running text does not put the class in a cell, so `cor` is None on every
        marker hit and there is nothing to compare. The check declines rather than
        inventing a disagreement."""
        recs = {
            "doc_id": "Society/doc",
            "mode": "bound",
            "recommendations": [{"rec_id": "p41/goal/1", "cor": None}],
        }
        result = gate.gate_coverage(sheet(row(rec="p41/goal/1"), mode="bound"), {"src": recs})
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])

    def test_a_narrative_locator_requires_the_narrative_class(self):
        parsed = sheet(
            row(rec="p41/narrative/1", klass="1"),
            coverage="".join(
                f"- `p41/goal/{number}` - no threshold stated\n" for number in (1, 2, 3)
            ),
        )
        result = gate.gate_coverage(parsed, {"src": self.RECS})

        self.assertTrue(any("class 'narrative'" in item for item in result.findings))

    def test_a_recommendation_locator_cannot_use_the_narrative_class(self):
        recs = {
            **self.RECS,
            "recommendations": [{"rec_id": "p41/goal/1", "cor": "1"}],
        }
        result = gate.gate_coverage(
            sheet(row(rec="p41/goal/1", klass="narrative")), {"src": recs}
        )

        self.assertTrue(any("reserved" in item for item in result.findings))

    def test_a_record_cannot_claim_the_reserved_narrative_kind(self):
        recs = {
            **self.RECS,
            "recommendations": [{"rec_id": "p41/narrative/1", "cor": "narrative"}],
        }
        result = gate.gate_coverage(
            sheet(row(rec="p41/narrative/1", klass="narrative")), {"src": recs}
        )

        self.assertTrue(any("collision" in item for item in result.findings))

    def test_a_narrative_row_does_not_discharge_exact_recommendation_coverage(self):
        parsed = sheet(row(rec="p41/narrative/1", klass="narrative"))
        result = gate.gate_coverage(parsed, {"src": self.RECS})

        self.assertTrue(any("3 of 3" in item for item in result.findings))
        self.assertFalse(any("does not carry" in item for item in result.findings))

    def test_every_coverage_run_declares_the_narrative_floor(self):
        result = gate.gate_coverage(sheet(row()), {"src": self.RECS})

        qualifier = "\n".join(result.report)
        self.assertIn("narrative row", qualifier)
        self.assertIn("outside the recommendation index", qualifier)
        self.assertIn("Scope", qualifier)

    def test_the_coverage_qualifier_counts_rendered_narrative_rows(self):
        result = gate.gate_coverage(
            sheet(
                row(
                    rec="p41/narrative/1",
                    klass="narrative",
                    snippet="RENDERED: an SBP goal of <130 mm Hg",
                )
            ),
            {"src": self.RECS},
        )

        self.assertIn("1 page transcription", "\n".join(result.report))

    def test_it_fires_on_one_unread_item_not_only_on_total_absence(self):
        """#153's lesson, from this ticket's own comment: fire on ANY unread item.

        A gate that only fires when nothing was covered reads green over partial
        coverage, which is the case that actually ships -- there it was 2 of 83.
        """
        covered = "".join(f"- `p41/goal/{n}` - no number\n" for n in (2, 3))
        parsed = sheet(row(rec="p41/goal/1"), coverage=covered)
        result = gate.gate_coverage(parsed, {"src": self.RECS})
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])

        parsed = sheet(row(rec="p41/goal/1"), coverage="- `p41/goal/2` - no number\n")
        result = gate.gate_coverage(parsed, {"src": self.RECS})
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(len(refusals), 1)

    def test_no_recommendation_record_is_reported_as_ungraded_never_as_clean(self):
        result = gate.gate_coverage(sheet(row()), {})
        refusals, warnings, ungraded = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual((refusals, warnings), ([], []))
        self.assertEqual(ungraded, ["src"])


class RangeGate(unittest.TestCase):
    """Each of these was a false failure on the first real sheet.

    The first version matched a bound by substring against the row's QUANTITY name and
    then graded every number in the value against it. Ten rows failed and all ten were
    correct. The bound is keyed on the unit now, and each shape below is one of those
    ten.
    """

    def test_catches_the_failure_it_exists_for(self):
        result = gate.gate_range(sheet(row(value="<1300 mm Hg", snippet="1300")))
        failures, _ = result.findings, result.ungraded
        self.assertEqual(len(failures), 1)
        self.assertIn("1300", failures[0])

    def test_a_bmi_unit_suffix_is_not_a_bmi(self):
        """`>=27 kg/m2` -- the 2 in m2 was being graded as a body mass index."""
        result = gate.gate_range(sheet(row(quantity="bmi-threshold", value=">=27 kg/m2")))
        failures, _ = result.findings, result.ungraded
        self.assertEqual(failures, [])

    def test_a_duration_in_a_row_whose_quantity_name_contains_bp_is_not_a_pressure(self):
        """`acute-ich-bp-control-duration` = `>=7 days`. The name contains `bp`; the
        number is a count of days."""
        result = gate.gate_range(
            sheet(row(quantity="acute-ich-bp-control-duration", value=">=7 days"))
        )
        failures, _ = result.findings, result.ungraded
        self.assertEqual(failures, [])

    def test_a_percentage_beside_a_time_window_is_not_a_pressure(self):
        """`15% in 24 h` failed twice: once on the 15 and once on the 24."""
        result = gate.gate_range(
            sheet(row(quantity="acute-stroke-bp-reduction-target", value="15% in 24 h"))
        )
        failures, _ = result.findings, result.ungraded
        self.assertEqual(failures, [])

    def test_a_pressure_and_a_time_window_in_one_value_grade_separately(self):
        """`<160/110 mm Hg within 30 to 60 min` -- both pressures graded, both
        minutes left alone, in a single value."""
        result = gate.gate_range(
            sheet(row(value="<160/110 mm Hg within 30 to 60 min"))
        )
        failures, ungraded = result.findings, result.ungraded
        self.assertEqual(failures, [])
        self.assertEqual(ungraded, 2)

    def test_a_paired_systolic_and_diastolic_bound_grades_both_numbers(self):
        result = gate.gate_range(sheet(row(value="140-159/90-109 mm Hg")))
        failures, _ = result.findings, result.ungraded
        self.assertEqual(failures, [])
        result = gate.gate_range(sheet(row(value="140-159/900-109 mm Hg")))
        failures, _ = result.findings, result.ungraded
        self.assertEqual(len(failures), 1)

    def test_a_number_in_no_recognized_unit_is_counted_rather_than_passed(self):
        """The ungraded count is returned and printed. A gate that grades 4 of 200
        numbers and reports clean is the shape #153 caught reading green."""
        result = gate.gate_range(sheet(row(value="once daily after 3 doses")))
        _, ungraded = result.findings, result.ungraded
        self.assertEqual(ungraded, 1)


class QuietSuppressesTheReportAndNeverAFinding(unittest.TestCase):
    """The pre-commit hook runs `--quiet`, so this is the contract that decides
    whether the gate can be made silent.

    **It was broken once, between writing the flag and wiring the hook.** Every FAIL
    line went through the quiet shim, which does not take ``file=``, so a failing
    sheet raised a TypeError instead of naming what was wrong. That is worse than
    either outcome it sits between: the commit was refused, and by a traceback rather
    than by a finding. Anything written to stderr is a finding and goes to ``print``.
    """

    @staticmethod
    def run_grade(quiet: bool, sheet_text: str) -> tuple[int, str, str]:
        import io
        import contextlib
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(sheet_text, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = grade(path, [], Path("C:/nowhere-at-all"), quiet=quiet)
            return status, out.getvalue(), err.getvalue()

    BROKEN = (
        HEADER
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + row(value="<1300 mm Hg", snippet="an SBP goal of <1300 mm Hg")
    )

    def test_quiet_hides_the_report_on_a_clean_sheet(self):
        text = (
            HEADER
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
        )
        _, loud, _ = self.run_grade(False, text)
        _, quiet, _ = self.run_grade(True, text)
        self.assertIn("SCHEMA", loud)
        self.assertNotIn("SCHEMA", quiet)

    def test_quiet_still_prints_every_finding(self):
        status, _, err = self.run_grade(True, self.BROKEN)
        self.assertEqual(status, 1)
        self.assertIn("FAIL", err)
        self.assertIn("1300", err)

    def test_quiet_still_prints_the_tier_two_banner(self):
        """The banner is the one thing decision 2 turns on: a skipped tier 2 must not
        be readable as a pass, and the hook runs quiet."""
        _, out, _ = self.run_grade(True, self.BROKEN)
        self.assertIn("CITATION TIER 2 DID NOT RUN", out)

    def test_all_quiet_suppresses_exactly_the_31_report_lines(self):
        def stdout_for(*arguments: str) -> str:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                gate.main(["--all", *arguments])
            return out.getvalue()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = (root / "one.md", root / "two.md")
            for path in paths:
                path.write_text("fixture selected through --all", encoding="utf-8")

            reports = (tuple(f"  one report line {index}" for index in range(7)),
                       tuple(f"  two report line {index}" for index in range(8)))
            scans = {
                path: gate.Scan(
                    gate.Sheet(path),
                    (gate.GateResult("fixture", report=report),),
                )
                for path, report in zip(paths, reports, strict=True)
            }
            with mock.patch.object(gate, "SHEET_ROOT", root), mock.patch.object(
                gate, "survey", side_effect=lambda path, *_, **__: scans[path]
            ):
                loud = stdout_for()
                quiet = stdout_for("--quiet")

        self.assertEqual(len(loud.splitlines()) - len(quiet.splitlines()), 31)

    def test_all_excludes_the_topic_coverage_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet_path = root / "topic.md"
            sheet_path.write_text("sheet", encoding="utf-8")
            (root / "coverage.md").write_text("registry", encoding="utf-8")
            scan = gate.Scan(gate.Sheet(sheet_path))
            with mock.patch.object(gate, "SHEET_ROOT", root), mock.patch.object(
                gate, "survey", return_value=scan
            ) as survey:
                status = gate.main(["--all"])

        self.assertEqual(status, 0)
        self.assertEqual(survey.call_count, 1)
        self.assertEqual(survey.call_args.args[0], sheet_path)


class TheExitStatusSaysWhichKindOfNotGraded(unittest.TestCase):
    """Found in review, and it is this ticket's own lesson failing on its own gate.

    ``grade`` tested ``recs_path is None`` to decide whether to report that omission
    went unchecked. A ``--recs`` pointing at a file that does not exist is not None,
    so COVERAGE silently did not run, nothing printed, and the sheet exited **0**.
    That is exactly *"a test that goes green because its input vanished"*, and the
    pre-commit hook was one typo away from it.
    """

    CLEAN = (
        header()
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + row()
    )

    def grade_with(self, recs_arguments: list[str]) -> int:
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return grade(path, recs_arguments, Path("C:/nowhere-at-all"), quiet=True)

    def test_a_recs_path_that_does_not_exist_is_2_and_not_0(self):
        self.assertEqual(self.grade_with(["C:/nowhere-at-all/recs.json"]), 2)

    def test_no_recs_at_all_is_also_2(self):
        self.assertEqual(self.grade_with([]), 2)

    def test_a_missing_recs_file_says_so_by_name(self):
        """The two 2s are not the same event and the message has to distinguish them:
        one is a run that never meant to check omission, the other is a typo."""
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                grade(path, ["C:/nowhere/recs.json"], Path("C:/nowhere"), quiet=True)
            self.assertIn("no such file", err.getvalue())

    def test_a_record_never_built_under_the_lookup_root_warns_and_exits_0(self):
        """The hook's ``--all`` lookup is not an explicit path somebody typed.

        A fresh clone has no recommendation records, so that absence must remain loud
        under ``--quiet`` without turning every sheet edit into a refused commit.
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            empty_root = Path(directory) / "recs"
            empty_root.mkdir()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = grade(
                    path,
                    [],
                    Path("C:/nowhere-at-all"),
                    quiet=True,
                    recs_root=empty_root,
                )
            self.assertEqual(status, 0)
            self.assertIn("COVERAGE", err.getvalue())
            self.assertIn("NOT RUN", err.getvalue())
            self.assertIn("not a clean COVERAGE pass", err.getvalue())

    def test_an_unreadable_record_under_the_lookup_root_still_exits_2(self):
        """Only absence is the declared degradation; a broken artifact is an error."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-src.json").write_text("{not json", encoding="utf-8")
            path = root / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                status = grade(
                    path,
                    [],
                    Path("C:/nowhere-at-all"),
                    quiet=True,
                    recs_root=root,
                )
            self.assertEqual(status, 2)


class TheReportBodySaysCoverageDidNotRun(unittest.TestCase):
    """The sibling of the class above, and it survived that fix because every test
    there passes ``quiet=True`` and so never reads the report.

    The exit status was right and the stderr notice was right; the **report body**
    still printed ``COVERAGE  0 refusing, 0 warning``, which is what a clean coverage
    pass prints. Redirect stdout to keep the report -- which is the only reason to
    print one -- and the notice is on the stream you dropped, leaving an artifact
    that reads as a full pass over a gate that never ran.

    That is this ticket's comment 3 exactly, *"a count printed beside a green verdict
    is read as a footnote to a pass"*, one turn sharper: a **zero** printed beside a
    gate that did not run. ``CITATION tier 2`` already prints ``SKIPPED`` in the body
    for the same situation, so the fix is to make COVERAGE symmetric with the gate
    standing next to it rather than to invent a convention.
    """

    def report_for(self, recs_arguments: list[str]) -> str:
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(TheExitStatusSaysWhichKindOfNotGraded.CLEAN, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                grade(path, recs_arguments, Path("C:/nowhere-at-all"), quiet=False)
            return out.getvalue()

    def coverage_line(self, report: str) -> str:
        lines = [line for line in report.splitlines() if line.startswith("  COVERAGE")]
        self.assertEqual(len(lines), 1, f"expected one COVERAGE line, got {lines}")
        return lines[0]

    def test_a_missing_recs_file_does_not_print_a_zero_count(self):
        line = self.coverage_line(self.report_for(["C:/nowhere/recs.json"]))
        self.assertIn("NOT RUN", line)
        self.assertNotIn("0 refusing", line)

    def test_no_recs_at_all_does_not_print_a_zero_count_either(self):
        line = self.coverage_line(self.report_for([]))
        self.assertIn("NOT RUN", line)
        self.assertNotIn("0 refusing", line)

    def test_a_graded_sheet_still_prints_its_counts(self):
        """The fix must not swallow the ordinary line: a run that did check omission
        and found nothing has to keep saying so, or this trades one silence for
        another."""
        import contextlib
        import io
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            recs = Path(directory) / "recs.json"
            recs.write_text(
                json.dumps(
                    trust_recommendation_record({
                        "doc_id": "d",
                        "source": "C:/corpus/Society/doc.pdf",
                        "mode": "exact",
                        "totals": {"recommendations": 1, "tables": 1},
                        "recommendations": [
                            {"rec_id": "p1/topic/1", "page": 1, "cor": "1", "text": "t"}
                        ],
                    })
                ),
                encoding="utf-8",
            )
            path = Path(directory) / "sheet.md"
            path.write_text(TheExitStatusSaysWhichKindOfNotGraded.CLEAN, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                grade(path, [str(recs)], Path("C:/nowhere-at-all"), quiet=False)
            line = self.coverage_line(out.getvalue())
            self.assertIn("refusing", line)
            self.assertNotIn("NOT RUN", line)


class TheScopeSectionIsGraded(unittest.TestCase):
    """#83 names this as a thing each sheet *carries*: *"a **sections-read scope
    line**. A synthesis pass is a reading and readings miss things ... so that
    'absent from the sheet' is never misread as 'absent from the guideline'."*

    It was the one format element with no gate behind it. Deleting the entire
    ``## Scope`` section from the real sheet left every gate at 0 and exit 0 -- the
    only trace was ``last resolved NOT RECORDED``, which touches no exit status. So a
    sheet could drop the sentence that bounds what it claims and still read as fully
    graded, which inverts the clause's whole purpose: **the less a sheet admits it
    skipped, the cleaner it scored.**

    Both limbs are required, and the second is the one that does the work. *Read:*
    alone lists what was covered; only *Not read:* tells a clinician that a number's
    absence here is not evidence of its absence in the guideline.
    """

    def schema_findings(self, text: str) -> list[str]:
        return gate.gate_schema(gate.parse(text, Path("test-sheet.md"))).findings

    def full(self, scope: str) -> str:
        return (
            HEADER.replace(
                "**Read:** the recommendation tables.\n\n"
                "**Not read:** the narrative sections and the appendices.\n",
                scope,
            )
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
        )

    def test_the_unmodified_header_still_passes(self):
        """Guards the replace() above: if HEADER's wording drifts, the substitution
        silently stops matching and every test below would pass vacuously."""
        self.assertEqual(self.schema_findings(self.full(
            "**Read:** the recommendation tables.\n\n"
            "**Not read:** the narrative sections and the appendices.\n")), [])

    def test_a_sheet_with_no_scope_section_fails(self):
        text = re.sub(r"\n## Scope\n.*?(?=\n## )", "\n", self.full(""), flags=re.S)
        self.assertNotIn("## Scope", text)
        findings = self.schema_findings(text)
        self.assertTrue(any("scope" in f.lower() for f in findings), findings)

    def test_a_scope_that_never_says_what_was_not_read_fails(self):
        findings = self.schema_findings(self.full("**Read:** the recommendation tables.\n"))
        self.assertTrue(any("not read" in f.lower() for f in findings), findings)

    def test_a_scope_that_never_says_what_was_read_fails(self):
        findings = self.schema_findings(self.full("**Not read:** the appendices.\n"))
        self.assertTrue(any("read" in f.lower() for f in findings), findings)

    def test_an_empty_scope_section_fails_rather_than_counting_as_present(self):
        findings = self.schema_findings(self.full("\n"))
        self.assertTrue(findings)

    def test_the_words_are_read_off_the_scope_section_and_not_the_whole_sheet(self):
        """A row whose snippet happens to contain 'not read' must not satisfy the
        scope rule -- `block_scan.py`'s mention-versus-use distinction, which this
        repo applies everywhere a keyword decides a verdict."""
        text = self.full("nothing here bounds anything.\n").replace(
            '"an SBP goal of <130 mm Hg"', '"read the label; not read elsewhere"')
        findings = self.schema_findings(text)
        self.assertTrue(any("scope" in f.lower() for f in findings), findings)


class ScopeSummaryTracksTheUnreadList(unittest.TestCase):
    """ADR 0046's conservative direction at the public SCHEMA seam."""

    def cervical_sheet_with_unread_fixture(self) -> tuple[Path, str]:
        path = gate.SHEET_ROOT / "cervical-cancer.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(
            "**Read:** all five recommendation statements in the USPSTF recommendation table. "
            "The rationale, clinical considerations, and evidence review on pp. 1-11 were read "
            "on 2026-08-29. "
            "The reference list is retired by class because it is a citation list with no "
            "clinical prose.",
            " ".join(text.split()),
        )
        current = "**Not read:** nothing in the source page range."
        self.assertIn(current, text)
        fixture = text.replace(
            current,
            "**Not read:** the rationale, clinical considerations, and evidence review.",
        )
        return path, fixture

    def test_a_retired_span_named_as_unread_is_refused(self):
        path, text = self.cervical_sheet_with_unread_fixture()
        planted = text.replace(
            "clinical considerations, and evidence review.",
            "clinical considerations, evidence review, and references.",
        )
        self.assertIn("evidence review, and references.", planted)

        findings = gate.gate_schema(gate.parse(planted, path)).findings

        self.assertTrue(
            any("references" in finding and "Not read" in finding for finding in findings),
            findings,
        )

    def test_index_does_not_match_prose_after_the_unread_lists_first_sentence(self):
        path = gate.SHEET_ROOT / "diabetes.md"
        parsed = gate.parse(path.read_text(encoding="utf-8"), path)

        findings = gate.gate_schema(parsed).findings

        self.assertFalse(any("span 'index'" in finding for finding in findings), findings)

    def test_a_hard_wrapped_retired_span_label_is_still_refused(self):
        path, text = self.cervical_sheet_with_unread_fixture()
        planted = text.replace(
            "and evidence review.",
            "evidence review, and recommendation\nstatements.",
        )
        self.assertIn("recommendation\nstatements", planted)

        findings = gate.gate_schema(gate.parse(planted, path)).findings

        self.assertTrue(
            any("recommendation statements" in finding for finding in findings),
            findings,
        )

    def test_a_span_label_inside_a_longer_list_item_does_not_match(self):
        path, text = self.cervical_sheet_with_unread_fixture()
        planted = text.replace(
            "and evidence review.",
            "evidence review, and a references appendix.",
        )
        self.assertIn("a references appendix", planted)

        findings = gate.gate_schema(gate.parse(planted, path)).findings

        self.assertFalse(any("span 'references'" in finding for finding in findings), findings)

    def test_every_current_sheet_passes_the_scope_summary_gate(self):
        paths = sorted(
            path
            for path in gate.SHEET_ROOT.glob("*.md")
            if path.name.casefold() not in {"readme.md", "coverage.md"}
        )
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(sheet=path.name):
                parsed = gate.parse(path.read_text(encoding="utf-8"), path)
                self.assertEqual(gate.gate_schema(parsed).findings, [])


class ScopeSummaryDeclaredLimits(unittest.TestCase):
    """ADR 0046's single object and its no-copy README pointer."""

    OBJECT = "SCOPE_SUMMARY_NOT_REACHED"

    def assignment(self) -> ast.Assign:
        tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
        return next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == self.OBJECT
                    for target in node.targets)
        )

    def ast_rows(self) -> list[tuple[str, str]]:
        value = self.assignment().value
        self.assertIsInstance(value, ast.Tuple)
        rows = []
        for node in value.elts:
            self.assertIsInstance(node, ast.Tuple)
            self.assertEqual(len(node.elts), 2)
            key = ast.literal_eval(node.elts[0])
            reason_node = node.elts[1]
            reason = (
                getattr(gate, reason_node.id)
                if isinstance(reason_node, ast.Name)
                else ast.literal_eval(reason_node)
            )
            rows.append((key, reason))
        return rows

    def test_the_object_carries_every_ruled_limit_once(self):
        expected = {
            "unread spans omitted from Not read",
            "compound span labels",
            "sentences after the first",
            "unread spans named under Read",
            "class-retirement placement",
            "items that are not span labels",
            "null-sheet wording",
            "misdrawn span boundaries",
        }
        rows = self.ast_rows()
        self.assertEqual({key for key, _ in rows}, expected)
        self.assertEqual(len(rows), len(expected))
        for key, reason in rows:
            self.assertTrue(key.strip())
            self.assertGreater(len(reason.split()), 8, key)

    def test_the_boundary_row_points_at_the_existing_constant(self):
        assignment = self.assignment()
        boundary = next(
            row
            for row in assignment.value.elts
            if ast.literal_eval(row.elts[0]) == "misdrawn span boundaries"
        )
        self.assertIsInstance(boundary.elts[1], ast.Name)
        self.assertEqual(
            boundary.elts[1].id,
            "PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES",
        )

    def test_the_readme_points_to_the_object_and_copies_no_row(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        pointer = f"threshold_sheet.{self.OBJECT}"
        self.assertEqual(readme.count(pointer), 1)
        for key, reason in self.ast_rows():
            with self.subTest(key=key):
                self.assertNotIn(key, readme)
                self.assertNotIn(reason, readme)


class ScopeSpanTable(unittest.TestCase):
    """Issue #478 makes source-section spans the arithmetic behind Scope."""

    def findings(self, text: str) -> list[str]:
        if "## Thresholds" not in text:
            text += (
                "\n## Thresholds\n\n"
                "| quantity | population | value | snippet | source | page | rec | class |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + row()
            )
        return gate.gate_schema(gate.parse(text, Path("test-sheet.md"))).findings

    def test_a_sheet_without_a_span_table_is_refused(self):
        text = re.sub(
            r"\n\| span \| pages \| read \|.*?\| narrative sections and appendices \| 51-60 \| no \|\n",
            "\n",
            HEADER,
            flags=re.S,
        )
        self.assertNotIn("| span | pages | read |", text)
        self.assertTrue(any("span table" in item for item in self.findings(text)))

    def test_the_three_column_table_is_parsed_and_overlap_is_permitted(self):
        parsed = gate.parse(
            HEADER.replace("| narrative sections and appendices | 51-60 | no |",
                           "| narrative sections and appendices | 41-60 | no |"),
            Path("test-sheet.md"),
        )
        self.assertEqual([(span.name, span.first_page, span.last_page)
                          for span in parsed.spans], [
            ("recommendation tables", 1, 50),
            ("narrative sections and appendices", 41, 60),
        ])
        result = gate.gate_page_coverage(parsed, {"Society/doc": 60})
        self.assertEqual(result.findings, [])
        rendered = "\n".join(result.stdout)
        self.assertIn("page_count: 60", rendered)
        self.assertIn("unaccounted pages: none", rendered)

    def test_a_multi_source_span_table_must_name_its_source(self):
        text = TWO_SOURCE_HEADER.replace("**Source: `aha`**\n\n", "")
        parsed = gate.parse(
            text + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(source="aha"),
            Path("test-sheet.md"),
        )
        findings = gate.gate_schema(parsed).findings
        self.assertTrue(any("multi-source sheet" in item for item in findings), findings)

    def test_an_unaccounted_page_refuses_and_the_remainder_is_printed(self):
        parsed = gate.parse(
            HEADER.replace("| narrative sections and appendices | 51-60 | no |",
                           "| narrative sections and appendices | 52-60 | no |"),
            Path("test-sheet.md"),
        )
        result = gate.gate_page_coverage(parsed, {"Society/doc": 60})
        self.assertEqual(len(result.findings), 1)
        self.assertIn("51", result.findings[0])
        self.assertIn("unaccounted pages: 51", "\n".join(result.stdout))

    def test_an_unresolved_source_page_count_is_not_graded(self):
        result = gate.gate_page_coverage(gate.parse(HEADER, Path("test-sheet.md")), {})
        self.assertTrue(result.not_graded)
        self.assertIn("Society/doc", result.skip_reason)
        self.assertIn("page_count: NOT RESOLVED", "\n".join(result.stdout))

    def test_a_read_span_with_neither_a_row_nor_a_dated_marker_is_refused(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| narrative sections and appendices | 51-60 | yes |",
        )
        findings = self.findings(text)
        self.assertTrue(any("neither rows nor a dated marker" in item for item in findings))

    def test_a_real_span_with_no_rows_cannot_be_retired_without_a_marker(self):
        path = (Path(__file__).resolve().parent.parent / "reference" / "thresholds"
                / "cervical-cancer.md")
        text = path.read_text(encoding="utf-8").replace(
            "| references | 11-13 | exempt: citation list has no clinical prose |",
            "| references | 11-13 | yes |",
        )
        self.assertIn("| references | 11-13 | yes |", text)
        findings = gate.gate_schema(gate.parse(text, path)).findings
        self.assertTrue(any(
            "references" in item
            and "neither rows nor a dated marker" in item
            for item in findings
        ), findings)

    def test_overlapping_positive_spans_do_not_make_table_order_semantic(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| overlapping recommendation summary | 41-60 | yes |",
        )
        self.assertEqual(self.findings(text), [])

    def test_a_dated_null_marker_retires_a_span(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| narrative sections and appendices | 51-60 | read 2026-08-23 |",
        )
        self.assertEqual(self.findings(text), [])

    def test_a_row_cannot_cite_a_page_covered_only_by_a_dated_null_marker(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| narrative sections and appendices | 51-60 | read 2026-08-23 |",
        )
        findings = self.findings(text + "\n## Thresholds\n\n" + row(
            page="p55", rec="p55/narrative/1", klass="narrative"
        ))

        self.assertTrue(any("read: yes" in item for item in findings), findings)

    def test_one_read_yes_span_is_enough_when_spans_overlap(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| narrative sections and appendices | 51-60 | no |\n"
            "| supplemental narrative read | 51-60 | yes |",
        )
        rows = row() + row(
            page="p55", rec="p55/narrative/1", klass="narrative"
        )

        self.assertEqual(self.findings(text + "\n## Thresholds\n\n" + rows), [])

    def test_an_impossible_null_marker_date_is_refused(self):
        text = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| narrative sections and appendices | 51-60 | read 2026-99-99 |",
        )
        self.assertTrue(any("invalid read value" in item for item in self.findings(text)))

    def test_only_references_may_use_a_reasoned_class_exemption(self):
        allowed = HEADER.replace(
            "| narrative sections and appendices | 51-60 | no |",
            "| references | 51-60 | exempt: citation list has no clinical prose |",
        )
        refused = allowed.replace("| references |", "| appendices |")
        self.assertEqual(self.findings(allowed), [])
        self.assertTrue(any("only a references span" in item for item in self.findings(refused)))


class TheSourceRowCarriesItsProvenance(unittest.TestCase):
    """#83: *"Each sheet carries source, **version, publication date, URL**"*, and
    `reference/thresholds/README.md` claims *"every part of it is read by the
    grader."* Three of those cells were parsed past -- `parse` kept `society`,
    `document` and `mode` -- so a sheet could leave version, published and url blank
    and grade clean. A threshold with no edition behind it is the failure this whole
    format exists to prevent: guidelines are revised, and 2017's number under 2025's
    heading is wrong in the most expensive way.
    """

    def blanked(self, column: str) -> list[str]:
        cells = {"version": "2025", "published": "2025", "url": "https://example.invalid"}
        cells[column] = ""
        line = (f"| src | AHA/ACC | Society/doc | {cells['version']} | "
                f"{cells['published']} | {cells['url']} | exact |")
        text = HEADER.replace(
            "| src | AHA/ACC | Society/doc | 2025 | 2025 | https://example.invalid | exact |",
            line,
        ) + ("\n## Thresholds\n\n"
             "| quantity | population | value | snippet | source | page | rec | class |\n"
             "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + row())
        return gate.gate_schema(gate.parse(text, Path("test-sheet.md"))).findings

    def test_a_blank_version_fails(self):
        self.assertTrue(any("version" in f.lower() for f in self.blanked("version")))

    def test_a_blank_publication_date_fails(self):
        self.assertTrue(any("published" in f.lower() for f in self.blanked("published")))

    def test_a_blank_url_fails(self):
        self.assertTrue(any("url" in f.lower() for f in self.blanked("url")))

    def test_the_real_sheet_carries_all_three(self):
        """The one committed sheet has to satisfy the rule this adds, or the rule is
        aspirational rather than enforced."""
        path = Path(__file__).resolve().parent.parent / "reference" / "thresholds" / "hypertension.md"
        parsed = gate.parse(path.read_text(encoding="utf-8"), path)
        self.assertTrue(parsed.sources)
        for key, source in parsed.sources.items():
            for column in ("version", "published", "url"):
                self.assertTrue(source.get(column), f"{key} has no {column}")


class TheRenderedPageEscapeHatch(unittest.TestCase):
    """#83: *"a per-row annotation meaning read off the rendered page, extraction
    garbles this table. Declaring it is a deliberate act that leaves a trace."*

    **This is the one class in `tools/` that needs something installed, and #86's
    first CI run is what found that out.** `gate_citation_tier2` returns early
    with the reason ``pymupdf is not installed``, so on a clean machine the
    first test below fails outright -- and, worse, two of the other three pass
    for the wrong reason, asserting ``rendered == 0`` against a gate that
    short-circuited before it could count anything. That is `test_icd10.py`'s
    two-reasons objection, hidden by a dependency the maintainer's machine
    happens to satisfy.

    So the whole class skips rather than the one test: a partial run here reads
    as a pass, which is the shape this repo keeps naming. It also means
    CLAUDE.md's *"the test suite needs nothing installed"* is now true of every
    module except this class, which skips instead.
    """

    def setUp(self):
        try:
            import pymupdf  # noqa: F401
        except ImportError:
            self.skipTest("pymupdf absent; tier 2 short-circuits and these grade nothing")

    def test_a_declared_row_is_skipped_by_tier_two_and_counted(self):
        marked = row(snippet=f"{gate.RENDERED_MARKER} an SBP goal of <130 mm Hg")
        result = gate.gate_citation_tier2(
            sheet(marked), Path(__file__).parent
        )
        failures, skipped, rendered = result.findings, result.skip_reason, result.rendered
        self.assertIsNone(skipped)
        self.assertEqual(rendered, 1)
        self.assertEqual(failures, [])

    def test_an_undeclared_row_is_not_skipped(self):
        result = gate.gate_citation_tier2(sheet(row()), Path(__file__).parent)
        _, _, rendered = result.findings, result.skip_reason, result.rendered
        self.assertEqual(rendered, 0)

    def test_the_marker_must_start_the_snippet_not_merely_appear_in_it(self):
        """`phi-scan: synthetic`'s own-line rule, adopted for the reason it was added
        there: a bare substring test let two files exempt themselves just by
        explaining the pragma."""
        mentioned = row(snippet=f"a row may declare {gate.RENDERED_MARKER} to opt out, <130")
        result = gate.gate_citation_tier2(sheet(mentioned), Path(__file__).parent)
        _, _, rendered = result.findings, result.skip_reason, result.rendered
        self.assertEqual(rendered, 0)

    def test_tier_one_still_grades_a_declared_row(self):
        """The hatch buys out of tier 2 only. A value whose number is absent from its
        own snippet is still a refusal, because that check needs no page at all."""
        marked = row(value="<140 mm Hg", snippet=f"{gate.RENDERED_MARKER} a goal of <130 mm Hg")
        self.assertEqual(len(gate.gate_citation_tier1(sheet(marked)).findings), 1)


class TheGraderMatchesTheFormatItDocuments(unittest.TestCase):
    """`test_spelling_scan.py`'s reasoning: a checker that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    def test_the_readme_names_every_section_the_parser_reads(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        for section in ("## Sources", "## Scope", "## Populations", "## Thresholds",
                        "## Conflicts", "## Coverage"):
            self.assertIn(f"### `{section}`", readme, f"{section} is not documented")

    def test_the_readme_states_the_schema_marker_the_parser_requires(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(gate.SCHEMA_MARKER, readme)

    def test_the_readme_still_names_the_three_citation_tiers(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        for tier in ("| 0 |", "| 1 |", "| 2 |"):
            self.assertIn(tier, readme)
        self.assertIn("`NOT RUN` on bound sources", readme)


def quote_footprint(sheet_name: str, *, strip_rendered: bool = False):
    """Return the parser-backed quote measures shared by each shipped sheet."""
    path = gate.SHEET_ROOT / sheet_name
    sheet_ = gate.parse(path.read_text(encoding="utf-8"), path)
    snippets = [row.snippet for row in sheet_.rows]
    distinct = set(snippets)
    quoted = [
        snippet.removeprefix(gate.RENDERED_MARKER).strip()
        if strip_rendered
        else snippet
        for snippet in distinct
    ]
    words = sorted(len(snippet.split()) for snippet in quoted)
    return sheet_, snippets, distinct, words


class TheQuotingPostureFiguresAreReDerived(unittest.TestCase):
    """README.md's *quoting posture* section states how much is quoted, and #223's
    ruling rests on those numbers -- so they are re-derived from the sheet here
    rather than left as prose nobody checks.

    That is [#143]'s shape, and this repo has watched one figure go stale in four
    files at once. The section says ``python -m unittest test_threshold_sheet -k
    Quoting`` beside itself, so a reader is pointed at this class by name.

    **Through `gate.parse` and never a parser of its own.** The first version
    hand-rolled a section-aware table reader and reached the snippet positionally
    as ``cells[3]``, which agreed with the real parser on today's file and would
    have gone on agreeing with itself after a column reorder -- counting a
    different column and staying green. Using the parser the gates use means a
    schema change fails here rather than quietly changing what is measured.
    """

    SHEET = "hypertension.md"

    def _sheet(self) -> gate.Sheet:
        return quote_footprint(self.SHEET)[0]

    def _readme(self) -> str:
        return (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")

    def _snippets(self) -> list[str]:
        """``parse`` has already stripped the surrounding quotes, so there is one
        definition of a snippet here rather than two that agree by luck."""
        return quote_footprint(self.SHEET)[1]

    def test_the_row_and_snippet_counts(self):
        snippets = self._snippets()
        self.assertEqual(len(snippets), 74)
        self.assertEqual(len(set(snippets)), 70)
        readme = self._readme()
        self.assertIn("| rows | 74 |", readme)
        self.assertIn("**70**", readme)

    def test_the_quoted_word_count(self):
        """Distinct snippets, because a snippet repeated on two rows is quoted once."""
        words = [len(snippet.split()) for snippet in set(self._snippets())]
        self.assertEqual(sum(words), 773)
        self.assertEqual(max(words), 15)
        self.assertEqual(min(words), 6)
        self.assertEqual(sorted(words)[len(words) // 2], 11)
        readme = self._readme()
        self.assertIn("**773**", readme)
        self.assertIn("15 / 11 / 6", readme)

    def test_the_populations_table_word_count(self):
        values = list(self._sheet().populations.values())
        self.assertEqual(len(values), 19)
        self.assertEqual(sum(len(value.split()) for value in values), 115)
        readme = self._readme()
        self.assertIn("**115**", readme)
        self.assertIn("19 rows", readme)

    def test_the_source_page_count_is_the_catalogs(self):
        """105 is the catalog's ``page_count`` for the cited document, not a recollection.

        The one figure in that table which does **not** come from the sheet, and the
        README says so rather than claiming the whole table re-derives from one file.
        """
        catalog = (gate.SHEET_ROOT.parent / "guidelines-catalog.md").read_text(encoding="utf-8")
        matching = [
            line for line in catalog.splitlines()
            if line.startswith("|") and "jones-et-al-2025" in line
        ]
        self.assertEqual(len(matching), 1)
        cells = [cell.strip() for cell in matching[0].strip("|").split("|")]
        self.assertEqual(cells[6], "105")
        self.assertIn("**105**", self._readme())

    def test_the_document_the_figures_describe_is_the_one_the_sheet_cites(self):
        """Otherwise the page count is a fact about some other guideline."""
        sources = self._sheet().sources
        self.assertEqual(list(sources), ["aha-2025"])
        self.assertIn("jones-et-al-2025", sources["aha-2025"]["document"])

    def test_the_posture_section_still_names_why_verbatim(self):
        """The gates are the argument. A section that lost that limb is a taste claim."""
        readme = self._readme()
        self.assertIn("## The quoting posture", readme)
        for claim in ("tier 0", "tier 1", "tier 2", "Paraphrase"):
            self.assertIn(claim, readme, f"the posture no longer states: {claim}")


class TheDiabetesQuotingPostureFiguresAreReDerived(unittest.TestCase):
    """The second sheet gets its own measured public-repo ruling; #223 explicitly
    says the hypertension figures do not license the class of future sheets."""

    def test_the_diabetes_quote_footprint_is_measured_from_the_shipped_sheet(self):
        # ``RENDERED:`` is this repo's evidentiary marker, not ADA expression. It
        # stays in the cell count and is removed only from the copied-word measure.
        sheet_, snippets, distinct, words = quote_footprint(
            "diabetes.md", strip_rendered=True
        )

        self.assertEqual(len(snippets), 357)
        self.assertEqual(len(distinct), 354)
        self.assertEqual(sum(words), 5063)
        self.assertEqual((max(words), words[len(words) // 2], min(words)), (55, 12, 1))
        self.assertEqual(len(sheet_.populations), 125)
        self.assertEqual(sum(len(value.split()) for value in sheet_.populations.values()), 1022)

        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        for claim in (
            "| rows | **357** |",
            "**354** are distinct",
            "**5,063**",
            "55 / 12 / 1",
            "125 rows",
            "**1,022**",
            "**377**",
        ):
            self.assertIn(claim, readme)

        catalog = (gate.SHEET_ROOT.parent / "guidelines-catalog.md").read_text(
            encoding="utf-8"
        )
        matching = [
            line
            for line in catalog.splitlines()
            if line.startswith("|") and "standards-of-care-2026.pdf" in line
        ]
        self.assertEqual(len(matching), 1)
        cells = [cell.strip() for cell in matching[0].strip("|").split("|")]
        self.assertEqual(cells[6], "377")


class TheDiabetesSheetPassesTheExternalCliSeam(unittest.TestCase):
    """The agreed #186 integration seam, skipped only where its deliberately
    uncommitted source, recommendation record, or blind read is unavailable."""

    PDF_ROOT = Path("C:/codeing/guidelines-src")
    TEXT_ROOT = Path("C:/codeing/guidelines-text")
    RECS_ROOT = Path("C:/codeing/guidelines-index")
    SECOND_READ = RECS_ROOT / "second-read-diabetes.json"

    def test_the_complete_gate_set_grades_the_committed_diabetes_sheet(self):
        required = (
            self.PDF_ROOT / "ADA" / "standards-of-care-2026.pdf",
            self.TEXT_ROOT / "manifest.json",
            self.RECS_ROOT / "recs-ada-2026.json",
            self.SECOND_READ,
        )
        absent = [str(path) for path in required if not path.is_file()]
        if absent:
            self.skipTest("external gate input absent: " + ", ".join(absent))
        external_read = gate.load_second_read(self.SECOND_READ)
        if not external_read.ok:
            self.skipTest("external second-read record predates threshold-sheet/2: "
                          + str(external_read.why_not))

        handoff_stderr = io.StringIO()
        with contextlib.redirect_stderr(handoff_stderr):
            handoff = gate.read_extraction(
                self.TEXT_ROOT, allow_untrusted_provenance=True
            )
        self.assertFalse(handoff.problems, handoff.problems)

        source_sheet = gate.SHEET_ROOT / "diabetes.md"
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        sheet_path = source_sheet
        if handoff.provenance and handoff.provenance.reasons:
            declaration = artifact_provenance.render_accepted_distrust(
                handoff.root, handoff.provenance.reasons
            )
            sheet_path = Path(temporary.name) / source_sheet.name
            text = source_sheet.read_text(encoding="utf-8")
            text = text.replace("## Scope\n", "## Scope\n\n" + declaration + "\n", 1)
            sheet_path.write_text(text, encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = gate.main(
                [
                    str(sheet_path),
                    "--recs-root",
                    str(self.RECS_ROOT),
                    "--pdf-root",
                    str(self.PDF_ROOT),
                    "--text-root",
                    str(self.TEXT_ROOT),
                    "--second-read",
                    str(self.SECOND_READ),
                    # This seam grades the committed sheet against deliberately
                    # uncommitted inputs. Their producing commit is not the subject
                    # of this test, and every feature branch would otherwise turn
                    # the ownership refusal into a failure before any gate ran.
                    "--allow-untrusted-provenance",
                ]
            )

        report = output.getvalue()
        self.assertEqual(code, 0, report)
        for verdict in (
            "SCHEMA          0",
            "CITATION tier 0 NOT RUN",
            "CITATION tier 1 0",
            "CITATION tier 2 0",
            "COVERAGE        0 refusing, 0 warning",
            "RANGE           0",
            "WATERMARK       0 refusing",
            "SECOND READ     0 refusing",
        ):
            self.assertIn(verdict, report)


class CoverageIsPerSource(unittest.TestCase):
    """[#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177).

    ``gate_coverage`` took **one** recommendation record for the whole sheet and never
    filtered ``known`` by ``row.source``. On a sheet citing two societies the named
    source had its omissions checked and the other one silently did not -- and the
    count that would have surfaced it was derived from ``recs is None``, so it could
    only ever be 0 or 1 however many sources went unchecked.

    It cost nothing while one sheet with one source existed, which is exactly why
    every fixture above has one source and no test in this file could express it.
    """

    def test_a_second_sources_omissions_are_checked(self):
        """The defect, stated as a test. Under the one-record grader the KDIGO
        omission below was unreachable: whichever record `--recs` named, the other
        source's `known` set was never built."""
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_,
            {"aha": record("p1/aha/1"), "kdigo": record("p9/kdigo/1", "p9/kdigo/2")},
        )
        refusals, _, ungraded = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(ungraded, [])
        self.assertEqual(len(refusals), 1)
        self.assertIn("kdigo", refusals[0])
        self.assertIn("p9/kdigo/1", refusals[0])

    def test_known_is_filtered_to_the_rows_citing_that_source(self):
        """The filtering is the fix and not a tidy-up. A row citing AHA must not
        discharge a KDIGO recommendation that happens to share its identifier --
        records can repeat a `rec_id` within one document and separate documents can
        share one too, so the source key remains part of the membership boundary.
        """
        sheet_ = two_source_sheet(row(rec="p1/goal/1", source="aha"))
        result = gate.gate_coverage(
            sheet_,
            {"aha": record("p1/goal/1"), "kdigo": record("p1/goal/1")},
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(len(refusals), 1)
        self.assertIn("kdigo", refusals[0])

    def test_the_ungraded_count_is_a_real_count_of_sources(self):
        """The ticket's headline: the old signal was derived from ``recs is None`` and
        so could not exceed 1 regardless of how many sources went unchecked."""
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(sheet_, {"aha": None, "kdigo": None})
        _, _, ungraded = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(ungraded, ["aha", "kdigo"])

    def test_one_source_graded_and_one_not_reports_both_halves(self):
        """Partial coverage is the shape this ticket series keeps finding. The graded
        half still refuses, and the ungraded half is named rather than absorbed."""
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_, {"aha": record("p1/aha/1", "p1/aha/2"), "kdigo": None}
        )
        refusals, _, ungraded = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(ungraded, ["kdigo"])
        self.assertEqual(len(refusals), 1)
        self.assertIn("p1/aha/2", refusals[0])

    def test_a_scope_out_still_discharges_its_recommendation(self):
        """`## Coverage` is sheet-wide and stays so: a `rec_id` is scoped out once,
        and which source it belongs to is decided by which record carries it."""
        sheet_ = two_source_sheet(
            row(rec="p1/aha/1", source="aha"),
            coverage="- `p9/kdigo/1` - no number stated\n",
        )
        result = gate.gate_coverage(
            sheet_, {"aha": record("p1/aha/1"), "kdigo": record("p9/kdigo/1")}
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual(refusals, [])

    def test_the_mode_cross_check_is_per_source(self):
        """It looped over every source comparing each against the one record's mode,
        so on a two-source sheet it graded one source's declaration against the
        other's record -- a false refusal and a missed one in the same loop."""
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_,
            {
                "aha": record("p1/aha/1"),
                "kdigo": record("p9/kdigo/1", mode="bound"),
            },
        )
        refusals, warnings, _ = result.findings, result.warnings, result.ungraded_sources
        declared = [message for message in refusals if "declares mode" in message]
        self.assertEqual(len(declared), 1)
        self.assertIn("'kdigo'", declared[0])
        # And the bound source's omission warns rather than refusing, per source.
        self.assertTrue(any("over-reports" in message for message in warnings))

    def test_a_record_built_from_another_document_is_refused(self):
        """The hazard #177's own fix introduces, and it is not in the ticket.

        The lookup is keyed on a source key that is **sheet-local**, so two sheets
        using `aha` for different guidelines resolve one `recs-aha.json` and each is
        graded against the other's document. Nothing else here would notice: a
        `rec_id` absent from the record is never counted as omitted, and every other
        gate reads the sheet alone.
        """
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_,
            {
                "aha": record("p1/aha/1", built_from="C:/corpus/Society/lipids.pdf"),
                "kdigo": record("p9/kdigo/1", built_from="C:/corpus/Society/kdigo.pdf"),
            },
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        named = [message for message in refusals if "was built from" in message]
        self.assertEqual(len(named), 1)
        self.assertIn("'aha'", named[0])

    def test_where_the_corpus_was_mounted_is_not_a_finding(self):
        """Only the disagreement is claimed. The record names an absolute path from
        the machine it was built on; the sheet names a `doc_id` relative to the corpus
        root. Comparing those whole would refuse every correct record."""
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_,
            {
                "aha": record("p1/aha/1", built_from="D:/elsewhere/whatever/aha.pdf"),
                "kdigo": record("p9/kdigo/1", built_from="C:\\corpus\\Society\\kdigo.pdf"),
            },
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual([message for message in refusals if "was built from" in message], [])

    def test_a_record_that_names_no_document_is_not_guessed_at(self):
        sheet_ = two_source_sheet(row(rec="p1/aha/1", source="aha"))
        result = gate.gate_coverage(
            sheet_, {"aha": record("p1/aha/1"), "kdigo": record("p9/kdigo/1")}
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertEqual([message for message in refusals if "was built from" in message], [])

    def test_the_class_check_reads_the_rows_own_source_record(self):
        """The one check that catches a row pinned to the wrong recommendation. Read
        against the wrong source's record it either invents a disagreement or misses
        a real one."""
        sheet_ = two_source_sheet(row(rec="p9/kdigo/1", klass="1", source="kdigo"))
        result = gate.gate_coverage(
            sheet_,
            {
                "aha": record("p9/kdigo/1", cor={"p9/kdigo/1": "1"}),
                "kdigo": record("p9/kdigo/1", cor={"p9/kdigo/1": "2a"}),
            },
        )
        refusals, _, _ = result.findings, result.warnings, result.ungraded_sources
        self.assertTrue(any("does not match" in message for message in refusals))


class BindingARecordToEachSource(unittest.TestCase):
    """``--recs`` is per source now, and this is the seam that decides which record
    answers for which key.

    **A bare path is still accepted and only where it cannot be ambiguous.** A sheet
    declaring one source binds it to that source; a sheet declaring two is asked
    rather than guessed at, because guessing is what the ticket is about.
    """

    def bind(self, sheet_, arguments, recs_root=None):
        records, why, errors, _ = gate.bind_recs(sheet_, arguments, recs_root)
        return records, why, errors

    def test_the_sweep_alias_wins_over_the_exact_name_root_and_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recs_root = root / "recs"
            recs_alias = root / "guidelines-recs"
            alias_record = recs_alias / "Society" / "doc.json"
            recs_root.mkdir()
            alias_record.parent.mkdir(parents=True)
            alias_record.write_text(
                json.dumps(record("p41/goal/alias", built_from="C:/corpus/Society/doc.pdf")),
                encoding="utf-8",
            )
            (recs_alias / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "documents": [
                            {
                                "doc_id": "Society/doc",
                                "source": "Society/doc.pdf",
                                "record": "Society/doc.json",
                                "outcome": "recommendations-found",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (recs_root / "recs-src.json").write_text(
                json.dumps(record("p41/goal/fallback", built_from="C:/corpus/Society/doc.pdf")),
                encoding="utf-8",
            )

            bound = gate.bind_recs(
                sheet(row(rec="p41/goal/alias")),
                [],
                recs_root,
                recs_alias=recs_alias,
                corpus_documents={"Society/doc"},
            )

            records, why, errors, _ = bound

        self.assertEqual(errors, [])
        self.assertEqual(why, {})
        self.assertEqual(records["src"]["recommendations"][0]["rec_id"], "p41/goal/alias")
        self.assertIn("sweep alias", bound.origins["src"])
        self.assertIn("doc.json", bound.origins["src"])

    def test_each_sweep_alias_absence_is_named_before_recs_root_fallback(self):
        cases = (
            ("no-alias", "no sweep alias at"),
            ("listed-file-missing", "manifest lists 'Society/doc'"),
            ("manifest-lacks-document", "manifest lacks corpus document 'Society/doc'"),
            ("not-a-corpus-document", "'Society/doc' is not a corpus document"),
        )
        for case, expected in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                recs_root = root / "recs"
                recs_alias = root / "guidelines-recs"
                recs_root.mkdir()
                (recs_root / "recs-src.json").write_text(
                    json.dumps(record("p41/goal/1")), encoding="utf-8"
                )
                corpus_documents = {"Society/doc"}
                if case != "no-alias":
                    recs_alias.mkdir()
                    documents = []
                    if case == "listed-file-missing":
                        documents.append(
                            {
                                "doc_id": "Society/doc",
                                "source": "Society/doc.pdf",
                                "record": "Society/doc.json",
                                "outcome": "recommendations-found",
                            }
                        )
                    if case == "not-a-corpus-document":
                        corpus_documents = {"Society/other"}
                    (recs_alias / "manifest.json").write_text(
                        json.dumps({"schema_version": 1, "documents": documents}),
                        encoding="utf-8",
                    )

                bound = gate.bind_recs(
                    sheet(row()),
                    [],
                    recs_root,
                    recs_alias=recs_alias,
                    corpus_documents=corpus_documents,
                )

            self.assertIsNotNone(bound.records["src"])
            self.assertIn("recs root", bound.origins["src"])
            self.assertIn(expected, bound.origins["src"])

    def test_an_explicit_recs_argument_beats_both_lookup_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            explicit = root / "explicit.json"
            explicit.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")

            bound = gate.bind_recs(
                sheet(row()),
                [str(explicit)],
                root / "recs",
                recs_alias=root / "guidelines-recs",
                corpus_documents={"Society/doc"},
            )

        self.assertIsNotNone(bound.records["src"])
        self.assertEqual(bound.origins["src"], f"--recs override {explicit}")

    def test_a_keyed_argument_binds_to_that_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "anything.json"
            path.write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            records, why, errors = self.bind(
                two_source_sheet(row(source="aha")), [f"aha={path}"]
            )
            self.assertEqual(errors, [])
            self.assertIsNotNone(records["aha"])
            self.assertIsNone(records["kdigo"])
            self.assertIn("kdigo", why)

    def test_an_untrusted_record_is_not_bound(self):
        payload = record("p41/goal/1")
        payload.pop("producer")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            records, why, errors = self.bind(sheet(row()), [str(path)])

        self.assertEqual(errors, [])
        self.assertIsNone(records["src"])
        self.assertIn("untrusted record: has no producer provenance stamp", why["src"])

    def test_the_existing_provenance_hatch_can_accept_an_untrusted_record(self):
        payload = record("p41/goal/1")
        payload.pop("producer")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                records, why, errors, _ = gate.bind_recs(
                    sheet(row()),
                    [str(path)],
                    None,
                    allow_untrusted_provenance=True,
                )

        self.assertEqual(errors, [])
        self.assertEqual(why, {})
        self.assertIsNotNone(records["src"])
        self.assertIn(artifact_provenance.FLAG, stderr.getvalue())

    def test_a_bare_path_binds_to_the_only_source(self):
        """The form the README documents and the one a single-source sheet keeps."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")
            records, _, errors = self.bind(sheet(row()), [str(path)])
            self.assertEqual(errors, [])
            self.assertIsNotNone(records["src"])

    def test_a_bare_path_on_a_two_source_sheet_is_refused_rather_than_guessed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            records, _, errors = self.bind(two_source_sheet(row(source="aha")), [str(path)])
            self.assertEqual(len(errors), 1)
            self.assertIn("which source", errors[0])
            self.assertEqual([key for key, value in records.items() if value], [])

    def test_an_unknown_source_key_is_an_error_and_not_a_silent_no_op(self):
        """A run that meant to check a source and named it wrongly checked nothing,
        which is `--recs`' own typo lesson one level up."""
        _, _, errors = self.bind(two_source_sheet(row(source="aha")), ["ada=C:/nowhere/x.json"])
        self.assertEqual(len(errors), 1)
        self.assertIn("ada", errors[0])
        self.assertIn("does not declare", errors[0])

    def test_the_same_key_twice_is_an_error(self):
        _, _, errors = self.bind(
            two_source_sheet(row(source="aha")), ["aha=a.json", "aha=b.json"]
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("twice", errors[0])

    def test_recs_root_resolves_one_record_per_source_key(self):
        """`--all` used to resolve `recs-<sheet stem>.json`, which is one file for a
        sheet however many societies it cites. Keyed on the source instead."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-aha.json").write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            (root / "recs-kdigo.json").write_text(
                json.dumps(record("p9/kdigo/1")), encoding="utf-8"
            )
            records, why, errors = self.bind(two_source_sheet(row(source="aha")), [], root)
            self.assertEqual(errors, [])
            self.assertEqual(why, {})
            self.assertEqual(sorted(records), ["aha", "kdigo"])
            self.assertTrue(all(records.values()))

    def test_an_explicit_path_that_does_not_exist_says_no_such_file(self):
        """The typo. It is not the same event as a record nobody has built yet, and
        the two have to read differently -- `TheExitStatusSaysWhichKindOfNotGraded`
        is that lesson, and this is it per source."""
        records, why, errors = self.bind(sheet(row()), ["src=C:/nowhere-at-all/recs.json"])
        self.assertEqual(errors, [])
        self.assertIsNone(records["src"])
        self.assertIn("no such file", why["src"])
        _, _, _, missing = gate.bind_recs(
            sheet(row()), ["src=C:/nowhere-at-all/recs.json"], None
        )
        self.assertEqual(missing, set())

    def test_a_record_the_root_does_not_hold_reads_as_never_built(self):
        with tempfile.TemporaryDirectory() as directory:
            _, why, _ = self.bind(sheet(row()), [], Path(directory))
            self.assertIn("no recommendation record", why["src"])
            self.assertNotIn("no such file", why["src"])
            _, _, _, missing = gate.bind_recs(sheet(row()), [], Path(directory))
            self.assertEqual(missing, {"src"})

    def test_no_argument_and_no_root_says_none_was_given(self):
        _, why, _ = self.bind(sheet(row()), [], None)
        self.assertIn("no --recs", why["src"])

    def test_a_file_that_parses_and_is_not_a_record_is_ungraded_too(self):
        """The same event through a door that looks legitimate: `null` and `[]` are
        valid JSON. Untyped, `null` left the record None with nothing saying why and
        the report raised a KeyError; `[]` reached the gate and raised there. Found by
        the Spec axis of `/code-review`."""
        for payload in ("null", "[]", '"a string"', "7"):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "recs.json"
                    path.write_text(payload, encoding="utf-8")
                    records, why, errors = self.bind(sheet(row()), [f"src={path}"])
                self.assertEqual(errors, [])
                self.assertIsNone(records["src"])
                self.assertIn("not a record", why["src"])

    def test_every_absent_record_says_why(self):
        """The invariant `grade`'s report reads, walked across every way of not having
        a record rather than asserted in the module -- it was false for one of them,
        and the symptom was a traceback rather than a verdict."""
        with tempfile.TemporaryDirectory() as directory:
            broken = Path(directory) / "broken.json"
            broken.write_text("{not json", encoding="utf-8")
            null = Path(directory) / "null.json"
            null.write_text("null", encoding="utf-8")
            cases = [
                ([], None),                                    # never asked for
                ([], Path(directory) / "empty-root"),          # never built
                (["src=C:/nowhere-at-all/x.json"], None),      # a typo
                ([f"src={broken}"], None),                     # does not parse
                ([f"src={null}"], None),                       # parses, not a record
            ]
            for arguments, root in cases:
                with self.subTest(arguments=arguments, root=root):
                    records, why, _ = self.bind(sheet(row()), arguments, root)
                    absent = [key for key, value in records.items() if value is None]
                    self.assertEqual(absent, ["src"])
                    self.assertIn("src", why)
                    self.assertTrue(why["src"].strip())

    def test_an_unreadable_record_is_ungraded_rather_than_a_traceback(self):
        """A half-written JSON file is a way of not having graded, and a traceback out
        of the pre-commit hook is not a verdict."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text("{not json", encoding="utf-8")
            records, why, errors = self.bind(sheet(row()), [f"src={path}"])
            self.assertEqual(errors, [])
            self.assertIsNone(records["src"])
            self.assertIn("unreadable", why["src"])


class TheReportNamesEverySourceItDidNotCheck(unittest.TestCase):
    """`grade`'s half of #177: a partly checked sheet must not print a line a reader
    takes for a pass, and it must not exit 0."""

    TWO = (
        TWO_SOURCE_HEADER
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + row(page="p1", rec="p1/aha/1", source="aha")
        + row(page="p9", rec="p9/kdigo/1", source="kdigo")
    )

    def run_grade(self, arguments, recs_root=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.TWO, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = grade(
                    path, arguments, Path("C:/nowhere-at-all"), quiet=False, recs_root=recs_root
                )
            return status, out.getvalue(), err.getvalue()

    def coverage_line(self, report):
        lines = [line for line in report.splitlines() if line.startswith("  COVERAGE")]
        self.assertEqual(len(lines), 1, f"expected one COVERAGE line, got {lines}")
        return lines[0]

    def test_a_successful_run_names_the_lookup_root_for_every_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recs_root = root / "recs"
            recs_root.mkdir()
            (recs_root / "recs-aha.json").write_text(
                json.dumps(record("p1/aha/1")), encoding="utf-8"
            )
            (recs_root / "recs-kdigo.json").write_text(
                json.dumps(record("p9/kdigo/1")), encoding="utf-8"
            )

            status, _, err = self.run_grade([], recs_root)

        self.assertEqual(status, 0)
        self.assertIn("RECOMMENDATION RECORD source 'aha' -- recs root", err)
        self.assertIn("RECOMMENDATION RECORD source 'kdigo' -- recs root", err)

    def test_one_record_for_a_two_source_sheet_is_2_and_names_the_other(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            status, out, err = self.run_grade([f"aha={path}"])
        self.assertEqual(status, 2)
        self.assertIn("kdigo", self.coverage_line(out))
        self.assertIn("NOT RUN", self.coverage_line(out))
        self.assertIn("kdigo", err)

    def test_the_body_line_does_not_read_as_a_pass(self):
        """`0 refusing, 0 warning` is byte for byte what a clean pass prints, which is
        `TheReportBodySaysCoverageDidNotRun`'s finding. Half a sheet is the same
        event."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            _, out, _ = self.run_grade([f"aha={path}"])
        self.assertNotEqual(
            self.coverage_line(out).strip(), "COVERAGE        0 refusing, 0 warning"
        )

    def test_both_records_present_is_0_and_prints_the_ordinary_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-aha.json").write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            (root / "recs-kdigo.json").write_text(
                json.dumps(record("p9/kdigo/1")), encoding="utf-8"
            )
            status, out, _ = self.run_grade([], root)
        self.assertEqual(status, 0)
        line = self.coverage_line(out)
        self.assertIn("refusing", line)
        self.assertNotIn("NOT RUN", line)

    def test_an_untrusted_record_is_not_run_and_exit_2(self):
        payload = record("p1/aha/1")
        payload.pop("producer")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-aha.json").write_text(json.dumps(payload), encoding="utf-8")
            (root / "recs-kdigo.json").write_text(
                json.dumps(record("p9/kdigo/1")), encoding="utf-8"
            )
            status, out, err = self.run_grade([], root)

        self.assertEqual(status, 2)
        self.assertIn("COVERAGE        NOT RUN for source 'aha' -- untrusted record:", err)
        self.assertIn("NOT RUN", self.coverage_line(out))

    def test_a_trusted_finding_wins_over_an_untrusted_source(self):
        untrusted = record("p9/kdigo/1")
        untrusted.pop("producer")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-aha.json").write_text(
                json.dumps(record("p1/aha/1", "p1/aha/omitted")), encoding="utf-8"
            )
            (root / "recs-kdigo.json").write_text(json.dumps(untrusted), encoding="utf-8")
            status, _, err = self.run_grade([], root)

        self.assertEqual(status, 1)
        self.assertIn("COVERAGE        NOT RUN for source 'kdigo' -- untrusted record:", err)

    def test_an_argument_error_is_2_rather_than_a_quiet_full_pass(self):
        """Both records resolve from the root, so COVERAGE runs on everything -- and
        the run still asked for a source that does not exist, which is a typo and not
        a decision."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "recs-aha.json").write_text(json.dumps(record("p1/aha/1")), encoding="utf-8")
            (root / "recs-kdigo.json").write_text(
                json.dumps(record("p9/kdigo/1")), encoding="utf-8"
            )
            status, _, err = self.run_grade(["ada=x.json"], root)
        self.assertEqual(status, 2)
        self.assertIn("does not declare", err)

    def test_a_sheet_declaring_no_source_does_not_print_a_clean_coverage_line(self):
        """`gate_coverage` iterates the declared sources, so a sheet whose Sources
        table did not parse has nothing to iterate -- and `0 refusing, 0 warning` is
        byte for byte what a clean pass prints. SCHEMA already refuses every row for
        an undeclared source key, so this is about what the *report* says."""
        text = TheExitStatusSaysWhichKindOfNotGraded.CLEAN.replace(
            "| src | AHA/ACC | Society/doc | 2025 | 2025 | https://example.invalid | exact |\n",
            "",
        )
        self.assertNotIn("| src |", text.split("## Scope")[0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(text, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                status = grade(path, [], Path("C:/nowhere-at-all"), quiet=False)
        line = [row_ for row_ in out.getvalue().splitlines() if row_.startswith("  COVERAGE")]
        self.assertEqual(status, 1)
        self.assertEqual(len(line), 1)
        self.assertIn("NOT RUN", line[0])

    def test_a_refusal_still_wins_over_a_source_that_was_not_checked(self):
        """`differential_scan.py`'s ordering: 1 beats 2 where both hold, and the note
        says the count is a floor."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs.json"
            path.write_text(json.dumps(record("p1/aha/1", "p1/aha/2")), encoding="utf-8")
            status, _, err = self.run_grade([f"aha={path}"])
        self.assertEqual(status, 1)
        self.assertIn("floor", err)


class TheRecordsStayOutsideTheRepo(unittest.TestCase):
    """#177's guard clause, and the reason it is a test rather than a comment.

    A `recs-*.json` holds the society's recommendation text **in full**, which is the
    copyrighted expression the sheet format exists to avoid committing.
    `guidelines_recs` refuses to write one inside a checkout, on
    `repo_root.ensure_outside_checkout`'s one rule since #176; what
    this pins is the other end, that the lookup does not quietly invite one to be put
    beside the sheet to make `--all` work.
    """

    def test_the_default_recs_root_is_outside_the_checkout(self):
        root = Path(gate.build_parser().parse_args(["--all"]).recs_root).resolve()
        self.assertFalse(
            str(root).startswith(str(gate.REPO_ROOT.resolve())),
            f"--recs-root defaults inside the repo: {root}",
        )

    def test_the_sweep_alias_has_an_environment_override(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(os.environ, {gate.RECS_ALIAS_ENV: directory}):
                arguments = gate.build_parser().parse_args(["--all"])

        self.assertEqual(arguments.recs_alias, Path(directory))

    def test_all_takes_no_recs_at_all(self):
        """A bare path binds to *the* source of a one-source sheet, so it would bind
        one society's record to every sheet citing a single source; a keyed one binds
        by a key that is sheet-local, so it lands on every sheet declaring that key and
        exits 2 on every sheet that does not. Neither is a thing anybody means, and the
        document cross-check only reaches a record that names the PDF it came from."""
        for argument in ("C:/anywhere/recs.json", "aha-2025=C:/anywhere/recs.json"):
            with self.subTest(argument=argument):
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    with self.assertRaises(SystemExit):
                        gate.main(["--all", "--recs", argument])
                self.assertIn("takes no", err.getvalue())

    def test_the_lookup_never_falls_back_to_the_sheet_directory(self):
        """The one convenience that would undo the guard: resolving beside the sheet
        when the root holds nothing.

        **Driven with a real, empty root and not with `recs_root=None`**, which is how
        the first version was written -- with no root there is no lookup to fall back
        *from*, so it would have stayed green with a sheet-directory fallback in place.
        That is #137's instrument problem, in the test written to pin the guard.
        """
        with tempfile.TemporaryDirectory() as directory:
            beside = Path(directory) / "recs-src.json"
            beside.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")
            path = Path(directory) / "sheet.md"
            path.write_text(TheExitStatusSaysWhichKindOfNotGraded.CLEAN, encoding="utf-8")
            empty_root = Path(directory) / "root"
            empty_root.mkdir()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                no_lookup_status = grade(
                    path, [], Path("C:/nowhere-at-all"), quiet=True, recs_root=None
                )
                empty_root_status = grade(
                    path, [], Path("C:/nowhere-at-all"), quiet=True, recs_root=empty_root
                )
            self.assertEqual(no_lookup_status, 2)
            self.assertEqual(empty_root_status, 0)


class TheHookGradesSheetsAndNotTheDirectoryReadme(unittest.TestCase):
    """Drive the hook command itself, because that is where #181's cost lands."""

    def test_readme_only_is_ignored_and_a_sheet_is_graded(self):
        shell = shutil.which("sh")
        git = shutil.which("git")
        if not shell or not git:
            self.skipTest("the hook contract needs sh and git")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools" / "hooks").mkdir(parents=True)
            (root / "reference" / "thresholds").mkdir(parents=True)
            hook = root / "tools" / "hooks" / "pre-commit"
            hook.write_text(
                (gate.REPO_ROOT / "tools" / "hooks" / "pre-commit").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            marker = root / "threshold-ran"
            coverage_marker = root / "coverage-ran"
            for name in (
                "skills_mirror.py",
                "spelling_scan.py",
                "guidelines_catalog.py",
                "scratch_census.py",
                "phi_scan.py",
            ):
                (root / "tools" / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
            (root / "tools" / "threshold_sheet.py").write_text(
                "import os, pathlib\n"
                "pathlib.Path(os.environ['THRESHOLD_HOOK_MARKER']).write_text('ran')\n",
                encoding="utf-8",
            )
            (root / "tools" / "threshold_coverage.py").write_text(
                "import os, pathlib\n"
                "pathlib.Path(os.environ['COVERAGE_HOOK_MARKER']).write_text('ran')\n",
                encoding="utf-8",
            )
            subprocess.run([git, "init", "--quiet"], cwd=root, check=True)
            subprocess.run([git, "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run([git, "config", "user.name", "Threshold Test"], cwd=root, check=True)
            subprocess.run([git, "commit", "--allow-empty", "--quiet", "-m", "base"], cwd=root, check=True)

            readme = root / "reference" / "thresholds" / "README.md"
            readme.write_text("prose only\n", encoding="utf-8")
            subprocess.run([git, "add", "--", str(readme)], cwd=root, check=True)
            environment = {
                **os.environ,
                "THRESHOLD_HOOK_MARKER": str(marker),
                "COVERAGE_HOOK_MARKER": str(coverage_marker),
            }
            subprocess.run([shell, str(hook)], cwd=root, env=environment, check=True)
            self.assertFalse(marker.exists(), "README.md invoked the sheet grader")
            self.assertFalse(coverage_marker.exists(), "README.md invoked the coverage auditor")

            actual_sheet = root / "reference" / "thresholds" / "hypertension.md"
            actual_sheet.write_text("a sheet\n", encoding="utf-8")
            subprocess.run([git, "add", "--", str(actual_sheet)], cwd=root, check=True)
            subprocess.run([shell, str(hook)], cwd=root, env=environment, check=True)
            self.assertTrue(marker.exists(), "an actual sheet did not invoke the grader")
            self.assertTrue(
                coverage_marker.exists(), "an actual sheet did not invoke the coverage auditor"
            )

    def test_the_hook_command_warns_and_passes_without_a_recommendation_record(self):
        shell = shutil.which("sh")
        git = shutil.which("git")
        if not shell or not git:
            self.skipTest("the hook contract needs sh and git")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "tools"
            (tools / "hooks").mkdir(parents=True)
            sheets = root / "reference" / "thresholds"
            sheets.mkdir(parents=True)
            for name in (
                "threshold_sheet.py",
                "artifact_lock.py",
                "artifact_provenance.py",
                "guidelines_extract.py",
                "guidelines_catalog.py",
                "guidelines_manifest.py",
                "guidelines_recs.py",
                "console_codec.py",
                "repo_root.py",
            ):
                shutil.copy2(gate.REPO_ROOT / "tools" / name, tools / name)
            shutil.copy2(
                gate.REPO_ROOT / "tools" / "hooks" / "pre-commit",
                tools / "hooks" / "pre-commit",
            )
            for name in (
                "skills_mirror.py",
                "spelling_scan.py",
                "scratch_census.py",
                "phi_scan.py",
            ):
                (tools / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
            (tools / "threshold_coverage.py").write_text(
                "raise SystemExit(0)\n", encoding="utf-8"
            )
            sheet_path = sheets / "hypertension.md"
            shutil.copy2(gate.SHEET_ROOT / "hypertension.md", sheet_path)
            shutil.copy2(
                gate.DEFAULT_CATALOG,
                root / "reference" / "guidelines-catalog.md",
            )

            subprocess.run([git, "init", "--quiet"], cwd=root, check=True)
            subprocess.run([git, "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run([git, "config", "user.name", "Threshold Test"], cwd=root, check=True)
            subprocess.run([git, "commit", "--allow-empty", "--quiet", "-m", "base"], cwd=root, check=True)
            subprocess.run([git, "add", "--", str(sheet_path)], cwd=root, check=True)
            empty_recs = root / "empty-recs"
            empty_recs.mkdir()
            environment = {
                **os.environ,
                "CLINICAL_GUIDELINES_RECS": str(empty_recs),
                "CLINICAL_GUIDELINES_TEXT": str(root / "absent-text"),
            }
            result = subprocess.run(
                [shell, str(tools / "hooks" / "pre-commit")],
                cwd=root,
                env=environment,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("COVERAGE        NOT RUN for source 'aha-2025'", result.stderr)
            self.assertIn("not a clean COVERAGE pass", result.stderr)


if __name__ == "__main__":
    unittest.main()


def text_corpus(root: Path, doc_id: str, body: str, boilerplate=(), margin=()) -> Path:
    """A throwaway `guidelines_extract.py` output directory: manifest plus one `.txt`.

    Built here rather than pointed at `C:/codeing/guidelines-text` on
    `test_guidelines.py`'s reasoning: the real corpus is 179 copyrighted PDFs'
    extracted text, outside the repo, and a build artifact that may not exist on the
    machine running the tests. Every figure gate 4's design rests on was measured
    against it once and is stated where it was measured, never asserted here.
    """
    output = f"{doc_id}.txt"
    (root / output).parent.mkdir(parents=True, exist_ok=True)
    (root / output).write_text(body, encoding="utf-8")
    producer = artifact_provenance.current_producer()
    producer["dirty"] = False
    producer["inputs"] = artifact_provenance.producer_file_identity(
        artifact_provenance.TRUST_FLOOR["extraction"]
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "producer": producer,
                "documents": [
                    {
                        "doc_id": doc_id,
                        "society": doc_id.partition("/")[0] or None,
                        "title": None,
                        "source": f"{doc_id}.pdf",
                        "output": output,
                        "document_class": "guideline",
                        "pages": body.count("\f") + 1,
                        "boilerplate": list(boilerplate),
                        "margin_stripped": list(margin),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return root


class WatermarkGate(ReadingManifestConformance, unittest.TestCase):
    """Gate 4, #83's watermark interleave: *"If a string stripped by #80 appears
    inside an extracted table row, that row is suspect and must be read off the
    rendered page."*

    The `RENDERED:` marker was the declaration half and shipped with #83. This is the
    detection half -- until #174 nothing told a writer that a given row needed it.
    """

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def build_conformance_corpus(self, root, producer):
        text_corpus(root, "Society/doc", "an SBP goal of <130 mm Hg")
        path = root / "manifest.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["producer"] = producer
        path.write_text(json.dumps(value), encoding="utf-8")

    def conformance_read(self, root, *, allow):
        with contextlib.redirect_stderr(io.StringIO()):
            result = gate.gate_watermark(
                sheet(row()), root, allow_untrusted_provenance=allow
            )
            _, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        return skip is None, skip or ""

    def conformance_command(self, root, *, allow):
        sheet_path = root / "sheet.md"
        sheet_path.write_text(header() + "\n## Thresholds\n\n" + row(), encoding="utf-8")
        recs_path = root / "recs.json"
        recs_path.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return grade(
                sheet_path,
                [str(recs_path)],
                Path("C:/nowhere-at-all"),
                quiet=True,
                text_root=root,
                allow_untrusted_provenance=allow,
            )

    def test_it_does_not_read_an_extraction_in_progress(self):
        text_root = self.root / "first-guidelines-text"
        with artifact_lock.hold(text_root, "guideline extraction"):
            result = gate.gate_watermark(
                sheet(row()), text_root
            )
            failures, skip, rendered, unprobed = result.findings, result.skip_reason, result.rendered, result.unprobed_sources

        self.assertEqual(failures, [])
        self.assertEqual(rendered, 0)
        self.assertEqual(unprobed, [])
        self.assertIn("another task is rebuilding", skip)
        self.assertIn(str(text_root.resolve()), skip)

    def test_a_snippet_carrying_a_stripped_running_head_is_refused(self):
        text_corpus(
            self.root, "Society/doc", "an SBP goal of <130 mm Hg for adults",
            boilerplate=["Jones et al"],
        )
        suspect = row(snippet="an SBP goal of Jones et al <130 mm Hg")
        result = gate.gate_watermark(sheet(suspect), self.root)
        failures, skip, rendered, unprobed = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNone(skip)
        self.assertEqual(unprobed, [])
        self.assertEqual(rendered, 0)
        self.assertEqual(len(failures), 1)
        self.assertIn("Jones et al", failures[0])

    def test_a_clean_snippet_passes(self):
        text_corpus(
            self.root, "Society/doc", "an SBP goal of <130 mm Hg for adults",
            boilerplate=["Jones et al"],
        )
        result = gate.gate_watermark(sheet(row()), self.root)
        failures, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNone(skip)
        self.assertEqual(failures, [])

    def test_a_stripped_string_that_also_occurs_in_the_body_is_not_a_probe(self):
        """The whole discrimination, and it is measured rather than chosen.

        A string the extractor strips in one place and keeps in another proves
        nothing by appearing in a snippet. That is not hypothetical: `JAMA` is
        stripped as a running head across AHA/ACC documents and occurs up to 52
        times in the body of one of them, and a document's own title is stripped as
        a page-repeated line while the body states it too. A length or letter-run
        threshold was tried first and cannot separate them -- `JAMA` and
        `Jones et al` are the same shape and only one is a usable probe.
        """
        text_corpus(
            self.root, "Society/doc", "JAMA published an SBP goal of <130 mm Hg",
            boilerplate=["JAMA"],
        )
        suspect = row(snippet="JAMA an SBP goal of <130 mm Hg")
        result = gate.gate_watermark(sheet(suspect), self.root)
        failures, _, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertEqual(failures, [])

    def test_the_margin_rules_strings_are_probes_too(self):
        """#100 split the record in two, and a detector reading only `boilerplate`
        misses the margin half entirely -- gate 4's own failure shape arriving in
        gate 4's input. The three documents that matter most lose a welded running
        head there rather than a folio."""
        text_corpus(
            self.root, "Society/doc", "an SBP goal of <130 mm Hg for adults",
            margin=["Global Strategy for Prevention"],
        )
        suspect = row(snippet="an SBP goal of Global Strategy for Prevention <130 mm Hg")
        result = gate.gate_watermark(sheet(suspect), self.root)
        failures, _, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertEqual(len(failures), 1)

    def test_a_rendered_row_is_exempt_and_counted(self):
        """The remedy #83 names for a suspect row is to read it off the rendered
        page, so a row declaring it has already applied the remedy and refusing it
        anyway would leave the gate unsatisfiable. Counted and printed, on tier 2's
        terms: the trace the hatch exists to leave is worth nothing if the run
        honoring it stays silent."""
        text_corpus(
            self.root, "Society/doc", "an SBP goal of <130 mm Hg",
            boilerplate=["Jones et al"],
        )
        marked = row(snippet=f"{gate.RENDERED_MARKER} Jones et al <130 mm Hg")
        result = gate.gate_watermark(sheet(marked), self.root)
        failures, _, rendered, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertEqual(failures, [])
        self.assertEqual(rendered, 1)

    def test_a_document_with_no_usable_probe_is_reported_and_never_clean(self):
        """A sheet citing a document with no usable probe is a sheet gate 4 said
        nothing about, and a silent zero there is the shape every scanner in `tools/`
        refuses. **How many of the corpus that is stays
        `reference/thresholds/README.md`'s to say** -- it is measured outside this
        repo, and spelling it out in words here was a restatement a `grep` for the
        figure could not even find."""
        text_corpus(self.root, "Society/doc", "JAMA and a goal of <130 mm Hg",
                    boilerplate=["JAMA"])
        result = gate.gate_watermark(sheet(row()), self.root)
        failures, skip, _, unprobed = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNone(skip)
        self.assertEqual(failures, [])
        self.assertEqual(unprobed, ["src"])

    def test_a_source_with_no_manifest_entry_is_reported_and_never_clean(self):
        text_corpus(self.root, "Society/other", "a goal of <130 mm Hg",
                    boilerplate=["Jones et al"])
        result = gate.gate_watermark(sheet(row()), self.root)
        _, skip, _, unprobed = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNone(skip)
        self.assertEqual(unprobed, ["src"])

    def test_an_absent_corpus_is_a_skip_and_never_a_pass(self):
        """Tier 2's arrangement and for tier 2's reason: the extracted corpus lives
        outside every checkout, so on a fresh clone and in CI there is nothing to
        probe. A skip is returned and the caller prints a banner."""
        result = gate.gate_watermark(sheet(row()), self.root / "nowhere")
        failures, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertEqual(failures, [])
        self.assertIsNotNone(skip)

    def test_a_manifest_from_the_unchanged_extractor_is_graded(self):
        text_corpus(self.root, "Society/doc", "an SBP goal of <130 mm Hg")
        extractor_commit = subprocess.run(
            [
                "git",
                "-C",
                str(Path(__file__).resolve().parent.parent),
                "log",
                "-1",
                "--format=%H",
                "--",
                "tools/guidelines_extract.py",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
        manifest_path = self.root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["producer"]["commit"] = extractor_commit
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        result = gate.gate_watermark(sheet(row()), self.root)
        _, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources

        self.assertIsNone(skip)

    def test_a_manifest_present_but_unusable_is_a_skip_carrying_its_reason(self):
        (self.root / "manifest.json").write_text("not json at all", encoding="utf-8")
        result = gate.gate_watermark(sheet(row()), self.root)
        _, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNotNone(skip)
        self.assertIn("manifest", skip.lower())

    def test_a_foreign_manifest_is_not_graded_without_the_override(self):
        text_corpus(
            self.root,
            "Society/doc",
            "an SBP goal of <130 mm Hg",
            boilerplate=["Jones et al"],
        )
        path = self.root / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["producer"]["commit"] = "f" * 40
        manifest["producer"].pop("inputs")
        path.write_text(json.dumps(manifest), encoding="utf-8")

        result = gate.gate_watermark(sheet(row()), self.root)
        _, skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        with self.assertWarnsRegex(RuntimeWarning, "untrusted"):
            result = gate.gate_watermark(
                sheet(row()),
                self.root,
                allow_untrusted_provenance=True,
            )
            _, allowed_skip, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources

        self.assertIn("different commit", skip)
        self.assertIsNone(allowed_skip)

    def _sheet_with_accepted_distrust(self, declaration: str) -> gate.Sheet:
        marked_header = header().replace(
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16",
            f"citations resolved against {TEST_PDF_ROOT} on 2026-08-16\n\n"
            + declaration,
        )
        return gate.parse(
            marked_header + "\n## Thresholds\n\n" + row(),
            Path("test-sheet.md"),
        )

    def _dirty_corpus(self) -> tuple[Path, tuple[str, ...]]:
        text_corpus(
            self.root,
            "Society/doc",
            "an SBP goal of <130 mm Hg",
            boilerplate=["Jones et al"],
        )
        manifest_path = self.root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["producer"]["dirty"] = True
        manifest["producer"].pop("inputs")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return self.root.resolve(), (
            "records no producer-file identity",
            "was produced by a dirty checkout",
        )

    def test_an_untrusted_pass_without_a_declaration_is_not_graded(self):
        corpus, _ = self._dirty_corpus()

        with self.assertWarns(RuntimeWarning):
            result = gate.gate_watermark(
                sheet(row()), corpus, allow_untrusted_provenance=True
            )

        self.assertTrue(result.not_graded)
        self.assertIn("NOT GRADED", "\n".join(result.report))

    def test_the_command_exits_two_when_the_untrusted_pass_is_not_declared(self):
        corpus, _ = self._dirty_corpus()
        sheet_path = self.root / "sheet.md"
        sheet_path.write_text(
            header() + "\n## Thresholds\n\n" + row(), encoding="utf-8"
        )
        recs_path = self.root / "recs.json"
        recs_path.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")
        stderr = io.StringIO()

        with self.assertWarns(RuntimeWarning), contextlib.redirect_stdout(
            io.StringIO()
        ), contextlib.redirect_stderr(stderr):
            status = grade(
                sheet_path,
                [str(recs_path)],
                Path("C:/nowhere-at-all"),
                quiet=True,
                text_root=corpus,
                allow_untrusted_provenance=True,
            )

        self.assertEqual(status, 2)
        self.assertIn("add this declaration under ## Scope", stderr.getvalue())

    def test_an_exact_declaration_holds_the_untrusted_pass(self):
        corpus, reasons = self._dirty_corpus()
        declaration = artifact_provenance.render_accepted_distrust(corpus, reasons)

        with self.assertWarns(RuntimeWarning):
            result = gate.gate_watermark(
                self._sheet_with_accepted_distrust(declaration),
                corpus,
                allow_untrusted_provenance=True,
            )

        self.assertFalse(result.not_graded)
        self.assertEqual(result.findings, [])
        self.assertIn("WATERMARK       0 refusing", "\n".join(result.report))

    def test_a_declaration_for_different_distrust_refuses(self):
        corpus, _ = self._dirty_corpus()
        declaration = artifact_provenance.render_accepted_distrust(
            corpus, ("has no producer provenance stamp",)
        )

        with self.assertWarns(RuntimeWarning):
            result = gate.gate_watermark(
                self._sheet_with_accepted_distrust(declaration),
                corpus,
                allow_untrusted_provenance=True,
            )

        self.assertTrue(any("different distrust" in finding for finding in result.findings))

    def test_a_trusted_pass_refuses_until_the_declaration_is_deleted(self):
        text_corpus(
            self.root,
            "Society/doc",
            "an SBP goal of <130 mm Hg",
            boilerplate=["Jones et al"],
        )
        declaration = artifact_provenance.render_accepted_distrust(
            self.root.resolve(), ("was produced by a dirty checkout",)
        )

        result = gate.gate_watermark(
            self._sheet_with_accepted_distrust(declaration), self.root
        )

        self.assertTrue(any("delete the accepted distrust" in finding for finding in result.findings))

    def test_a_foreign_manifest_makes_the_command_exit_two(self):
        text_corpus(self.root, "Society/doc", "an SBP goal of <130 mm Hg")
        manifest_path = self.root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["producer"]["commit"] = "f" * 40
        manifest["producer"].pop("inputs")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        sheet_path = self.root / "sheet.md"
        sheet_path.write_text(header() + "\n## Thresholds\n\n" + row(), encoding="utf-8")
        recs_path = self.root / "recs.json"
        recs_path.write_text(json.dumps(record("p41/goal/1")), encoding="utf-8")
        stderr = io.StringIO()

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            status = grade(
                sheet_path,
                [str(recs_path)],
                Path("C:/nowhere-at-all"),
                quiet=True,
                text_root=self.root,
            )

        self.assertEqual(status, 2)
        self.assertIn("different commit", stderr.getvalue())

    def test_the_manifest_reader_is_the_owner_and_not_a_copy(self):
        import guidelines_manifest

        self.assertIs(gate.read_extraction, guidelines_manifest.read)

    def test_every_tolerant_read_reports_its_problem_count(self):
        text_corpus(self.root, "Society/doc", "an SBP goal of <130 mm Hg")

        result = gate.gate_watermark(sheet(row()), self.root)

        self.assertIn("0 manifest problem(s)", "\n".join(result.diagnostics))

    def test_one_bad_sibling_does_not_discard_a_valid_documents_probes(self):
        text_corpus(
            self.root,
            "Society/doc",
            "an SBP goal of <130 mm Hg",
            boilerplate=["Jones et al"],
        )
        path = self.root / "manifest.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["documents"].append({"doc_id": "Society/broken"})
        path.write_text(json.dumps(value), encoding="utf-8")
        result = gate.gate_watermark(
            sheet(row(snippet="Jones et al goal <130 mm Hg")), self.root
        )
        failures, skip, _, _ = (
            result.findings,
            result.skip_reason,
            result.rendered,
            result.unprobed_sources,
        )

        self.assertIsNone(skip)
        self.assertEqual(len(failures), 1)
        self.assertIn("1 manifest problem(s)", "\n".join(result.diagnostics))

    def test_the_value_cell_is_probed_as_well_as_the_snippet(self):
        """#83 says *inside an extracted table row*, and both cells are transcribed
        off the same page."""
        text_corpus(self.root, "Society/doc", "a goal of <130 mm Hg",
                    boilerplate=["Jones et al"])
        suspect = row(value="<130 Jones et al mm Hg",
                      snippet="a goal of <130 Jones et al mm Hg")
        result = gate.gate_watermark(sheet(suspect), self.root)
        failures, _, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertTrue(failures)


class TheWatermarkGateAgainstTheCommittedSheet(unittest.TestCase):
    """The one real sheet this repo has, on `block_scan.py`'s and this module's own
    precedent: both of gate 3's parser bugs were found by pointing a gate at a real
    sheet and neither by a synthetic fixture.

    Skips where the extracted corpus is absent, which is every fresh clone and CI.
    """

    def setUp(self):
        parser = gate.build_parser()
        self.text_root = gate.text_root_for(
            parser.parse_args([str(gate.SHEET_ROOT / "hypertension.md")])
        )
        if not (self.text_root / "manifest.json").is_file():
            self.skipTest(f"no extracted corpus at {self.text_root}")
        result = gate.read_extraction(self.text_root)
        if result.problems:
            self.skipTest("; ".join(problem.message for problem in result.problems))

    def test_the_committed_sheet_has_no_interleaved_row(self):
        path = gate.SHEET_ROOT / "hypertension.md"
        parsed = gate.parse(path.read_text(encoding="utf-8"), path)
        result = gate.gate_watermark(parsed, self.text_root)
        failures, skip, _, unprobed = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertIsNone(skip)
        self.assertEqual(unprobed, [])
        self.assertEqual(failures, [])


def briefed(document: str = "Society/doc", span: str = "recommendation tables",
            pages: str = "1-50") -> dict:
    return {"document": document, "span": span, "pages": pages}


def second_read(*values: dict, read_on: str = "2026-08-19",
                briefed_block: dict | None = None) -> dict:
    """A `--second-read` record: what an independent reader found on the cited pages."""
    return {
        "read_on": read_on,
        "briefed": briefed_block or briefed(),
        "values": list(values),
    }


def seen(value: str, about: str = "the office BP treatment target",
         document: str = "Society/doc", page: int = 41) -> dict:
    return {"document": document, "page": page, "value": value, "about": about}


class SecondReadGate(unittest.TestCase):
    """Gate 5, #83's second independent read: *"A subagent extracts the same table
    with no access to the sheet; the diff is the gate. The only mechanism that
    catches misreading rather than miscitation."*

    And, in the same breath, the caveat #174 calls a build instruction: *"Weakness is
    correlated error, same model, same PDF, same mangling, same wrong answer, so it
    is a strong smoke test and must be documented as one, never as proof."*

    **Correlated error weakens the pass and not the fail**, which is the distinction
    the whole arrangement here turns on: two readers agreeing is cheap, and two
    readers disagreeing is not something correlation manufactures. So a disagreement
    refuses, and a clean gate 5 prints the smoke-test line every time rather than
    only when it fires.
    """

    def test_a_reader_miss_where_the_sheet_has_a_row_only_warns(self):
        read = gate.load_second_read_record(
            second_read(seen("<140 mm Hg")), Path("read.json")
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg")), read
        )
        refusals, _, _, _, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(uncovered, [])
        self.assertEqual(refusals, [])
        self.assertGreaterEqual(len(result.warnings), 1)
        self.assertIn("<130 mm Hg", result.warnings[0])

    def test_an_agreeing_value_passes_and_is_paired_for_a_reader(self):
        read = gate.load_second_read_record(
            second_read(seen("an SBP goal of <130 mm Hg")), Path("read.json")
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg")), read
        )
        refusals, warnings, pairings, undiffed, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [])
        self.assertEqual(undiffed, [])
        self.assertEqual(uncovered, [])
        self.assertEqual(len(pairings), 1)
        self.assertIn("bp-goal", pairings[0])
        self.assertIn("the office BP treatment target", pairings[0])

    def test_the_pairing_is_the_misreading_limb_and_is_never_graded(self):
        """The hole `threshold_sheet.py`'s own docstring names -- *a sheet whose
        numbers are all real and all filed under the wrong heading passes every gate
        here* -- is closed by a reader comparing the row's `quantity` to what the
        independent reader said the number was about. Comparing two free-text
        descriptions is a reading, so the tool sets them side by side and grades
        neither. `research_ledger.py`'s ruling on restatements, for its reason.
        """
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", about="the threshold for stage 2 hypertension")),
            Path("read.json"),
        )
        result = gate.gate_second_read(
            sheet(row(quantity="bp-goal", value="<130 mm Hg")), read
        )
        refusals, warnings, pairings, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [])
        self.assertEqual(len(pairings), 1)

    def test_a_value_the_second_read_found_that_no_row_carries_only_warns(self):
        """It over-reports by construction: the independent reader has no access to
        the sheet, so it cannot know what `## Coverage` scoped out. That is
        `gate_coverage`'s bound rule -- an over-reporting count may only warn."""
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg"), seen("<80 mm Hg", about="the diastolic goal")),
            Path("read.json"),
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg")), read
        )
        refusals, warnings, _, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("<80 mm Hg", warnings[0])

    def test_a_read_of_a_page_the_sheet_does_not_cite_warns_and_refuses_nothing(self):
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", page=99)), Path("read.json")
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg")), read
        )
        refusals, warnings, _, _, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [], "the read never opened the page the row cites")
        self.assertEqual(uncovered, [])
        self.assertTrue(any("99" in warning for warning in warnings))

    def test_a_citation_the_read_did_not_cover_is_uncovered_and_never_refused(self):
        """The first version refused it, and running the gate against the committed
        sheet is what showed that up: a read of three pages produced sixty-odd
        confident refusals about pages nobody had opened. That is #153's shape with
        the sign flipped, and it is how a gate gets learned around."""
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", page=41)), Path("read.json")
        )
        rows = row(page="p41") + row(page="p7", value="<80 mm Hg",
                                     snippet="a DBP goal of <80 mm Hg", rec="p7/goal/1")
        result = gate.gate_second_read(sheet(rows), read)
        refusals, _, _, _, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(uncovered, [])
        self.assertTrue(any("<80 mm Hg" in warning for warning in result.warnings))

    def test_the_page_is_part_of_the_match_and_not_only_the_document(self):
        """A value found on a different page of the same document is a miscitation,
        which is the one thing tier 2 already reaches -- so agreeing on the number
        while disagreeing on the page must not read as agreement. Both pages are
        covered here, so the row is genuinely diffed and genuinely disagrees."""
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", page=7), seen("<80 mm Hg", page=41)),
            Path("read.json"),
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg", page="p41")), read
        )
        refusals, _, _, _, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(uncovered, [])
        self.assertEqual(refusals, [])
        self.assertTrue(result.warnings)

    def test_a_value_carrying_no_number_is_reported_as_undiffed_and_never_clean(self):
        """`monthly`, `at every visit`. Nothing mechanical pairs those, and a gate
        that quietly counted them as agreeing would report coverage it does not
        have -- `gate_range`'s ungraded count, for its reason."""
        read = gate.load_second_read_record(second_read(), Path("read.json"))
        result = gate.gate_second_read(
            sheet(row(value="at every visit", snippet="measured at every visit")), read
        )
        refusals, _, _, undiffed, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(len(undiffed), 1)

    def test_a_rendered_row_is_still_diffed(self):
        """The hatch buys out of tier 2 and of gate 4, both of which read the
        extracted text stream. A second reader looks at the page, which is exactly
        what a `RENDERED:` row claims to have been read off, so there is nothing for
        it to buy out of here."""
        read = gate.load_second_read_record(
            second_read(seen("<140 mm Hg")), Path("read.json")
        )
        marked = row(value="<130 mm Hg", snippet=f"{gate.RENDERED_MARKER} a goal of <130 mm Hg")
        result = gate.gate_second_read(sheet(marked), read)
        refusals, _, _, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertGreaterEqual(len(result.warnings), 1)

    def test_a_value_found_in_a_span_the_sheet_retired_as_null_refuses(self):
        parsed = gate.parse(
            HEADER.replace(
                "| narrative sections and appendices | 51-60 | no |",
                "| narrative sections and appendices | 41-60 | read 2026-08-23 |",
            )
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(),
            Path("test-sheet.md"),
        )
        read = gate.load_second_read_record(
            second_read(
                seen("<80 mm Hg", page=55),
                briefed_block=briefed(span="narrative sections and appendices", pages="41-60"),
            ),
            Path("read.json"),
        )
        result = gate.gate_second_read(parsed, read)
        self.assertEqual(len(result.findings), 1)
        self.assertIn("retired as null", result.findings[0])

    def test_a_value_found_in_a_references_exemption_refuses(self):
        parsed = gate.parse(
            HEADER.replace(
                "| narrative sections and appendices | 51-60 | no |",
                "| references | 51-60 | exempt: citation list has no clinical prose |",
            )
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(),
            Path("test-sheet.md"),
        )
        read = gate.load_second_read_record(
            second_read(
                seen("<80 mm Hg", page=55),
                briefed_block=briefed(span="references", pages="51-60"),
            ),
            Path("read.json"),
        )
        result = gate.gate_second_read(parsed, read)
        self.assertEqual(len(result.findings), 1)
        self.assertIn("retired as null", result.findings[0])


class LoadingASecondReadRecord(unittest.TestCase):
    """Every way of being present and unusable, on `bind_recs`' ruling: a record that
    parses and is not a record is the same event as one that does not parse, and both
    arrive through a door that looks legitimate."""

    def test_a_record_with_no_values_key_is_not_a_record(self):
        read = gate.load_second_read_record({"read_on": "2026-08-19"}, Path("read.json"))
        self.assertFalse(read.ok)

    def test_a_json_list_is_not_a_record(self):
        read = gate.load_second_read_record([], Path("read.json"))
        self.assertFalse(read.ok)
        self.assertIn("list", read.why_not)

    def test_an_empty_values_list_is_not_a_read(self):
        """A second read that found nothing at all is a read that did not happen, and
        a clean diff against it would be every row refused or every row passed
        depending on which way the diff ran. Neither is a verdict."""
        read = gate.load_second_read_record(second_read(), Path("read.json"))
        self.assertTrue(read.ok, "an empty read is loadable")
        self.assertFalse(read.values)

    def test_an_entry_missing_a_field_is_named_rather_than_dropped(self):
        read = gate.load_second_read_record(
            {"read_on": "2026-08-19", "values": [{"page": 41, "value": "<130 mm Hg"}]},
            Path("read.json"),
        )
        self.assertFalse(read.ok)
        self.assertIn("document", read.why_not)

    def test_a_record_with_no_read_on_is_not_a_record(self):
        """`research_ledger.py`'s dateless-ledger limb: a read with no date cannot be
        told from a read taken against a corpus that has since been re-extracted, and
        this repo has a ticket about exactly that."""
        read = gate.load_second_read_record(
            {"briefed": briefed(), "values": [seen("<130 mm Hg")]}, Path("read.json")
        )
        self.assertFalse(read.ok)
        self.assertIn("read_on", read.why_not)

    def test_a_record_with_no_briefed_block_is_not_a_record(self):
        read = gate.load_second_read_record(
            {"read_on": "2026-08-19", "values": []}, Path("read.json")
        )
        self.assertFalse(read.ok)
        self.assertIn("briefed", read.why_not)


class TheBriefLeaksTheLocatorAndNeverTheAnswer(unittest.TestCase):
    """#83 asks for a read *"with no access to the sheet"*. A page range is a
    locator rather than an answer, and without one the second reader has a hundred
    pages to search -- so the brief names document, span, and range and nothing else.
    That it names them at all is a leak, named here rather than left implied.
    """

    def test_the_brief_names_every_cited_document_and_page(self):
        text = gate.brief(sheet(row(page="p41") + row(page="p7", rec="p7/goal/1")),
                          "recommendation tables")
        self.assertIn("Society/doc", text)
        self.assertIn("recommendation tables", text)
        self.assertIn("1-50", text)

    def test_the_brief_carries_no_value_quantity_or_snippet_from_the_sheet(self):
        marked = row(
            quantity="quantity-secret",
            population="population-secret",
            value="<133 mm Hg",
            snippet="a very distinctive snippet",
            source="source-secret",
            page="p47",
            rec="rec-secret",
            klass="class-secret",
        )
        text = gate.brief(sheet(marked), "recommendation tables")
        for secret in (
            "quantity-secret", "population-secret", "133", "distinctive",
            "source-secret", "47", "rec-secret", "class-secret",
        ):
            self.assertNotIn(secret, text)

    def test_the_brief_states_the_record_shape_the_grader_reads(self):
        text = gate.brief(sheet(row()), "recommendation tables")
        for field_name in ("document", "span", "pages", "briefed", "page", "value", "about", "read_on"):
            self.assertIn(field_name, text)


class GateFiveIsDocumentedAsASmokeTest(unittest.TestCase):
    """#83's caveat is a build instruction and #174 says so: *"it is a strong smoke
    test and must be documented as one, never as proof"*. So the line prints on a
    clean run too, which is the only run where anybody would mistake it for proof.
    """

    def _report(self, **kwargs) -> str:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            grade(**kwargs)
        return stream.getvalue()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )

    def test_a_clean_second_read_still_says_it_is_a_smoke_test(self):
        path = self.root / "read.json"
        path.write_text(json.dumps(second_read(seen("<130 mm Hg"))), encoding="utf-8")
        report = self._report(
            sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
            text_root=None, second_read_path=path,
        )
        self.assertIn("SECOND READ", report)
        self.assertIn("smoke test", report.lower())

    def test_without_a_second_read_the_body_says_it_did_not_run(self):
        report = self._report(
            sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
            text_root=None, second_read_path=None,
        )
        self.assertIn("SECOND READ", report)
        self.assertIn("NOT RUN", report)

    def test_an_unloadable_second_read_is_a_way_of_not_having_graded(self):
        path = self.root / "read.json"
        path.write_text("[]", encoding="utf-8")
        status = grade(
            sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
            text_root=None, second_read_path=path, quiet=True,
        )
        self.assertEqual(status, 2)

    def test_a_second_read_path_that_does_not_resolve_is_a_typo_and_not_a_decision(self):
        status = grade(
            sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
            text_root=None, second_read_path=self.root / "nowhere.json", quiet=True,
        )
        self.assertEqual(status, 2)


class TheWatermarkBannerIsHardToReadPast(unittest.TestCase):
    """`gate_citation_tier2`'s banner, for its reason: a gate that did not run must
    not be readable as one that passed."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )

    def test_an_absent_corpus_prints_a_banner_that_survives_quiet(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                       text_root=self.root / "nowhere", second_read_path=None, quiet=True)
        printed = stream.getvalue()
        self.assertIn("WATERMARK", printed)
        self.assertIn("NOT", printed)

    def test_the_body_names_the_sources_that_could_not_be_probed(self):
        text_corpus(self.root / "text", "Society/other", "a goal", boilerplate=["Jones et al"])
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                       text_root=self.root / "text", second_read_path=None)
        self.assertIn("src", stream.getvalue())


class TheCommandLineRefusesWhatItCannotBind(unittest.TestCase):
    """`--all`'s `--recs` rule, one gate over. A record and a read are both bound to
    one sheet's own vocabulary -- a source key in one case, a declared span in the
    other -- so pointed at a directory neither knows which sheet it
    answers for."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def test_all_takes_no_second_read(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                gate.main(["--all", "--second-read", str(self.root / "read.json")])

    def test_brief_on_a_file_that_is_not_a_sheet_grades_nothing(self):
        path = self.root / "not-a-sheet.md"
        path.write_text("# just prose\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate.main([str(path), "--brief"]), 2)

    def test_brief_on_a_missing_file_grades_nothing(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate.main([str(self.root / "nowhere.md"), "--brief"]), 2)

    def test_brief_emits_one_named_span(self):
        path = self.root / "sheet.md"
        path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(),
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = gate.main([
                str(path), "--brief", "--span", "recommendation tables"
            ])
        self.assertEqual(status, 0)
        self.assertIn("span: recommendation tables", output.getvalue())

    def test_the_text_root_is_derived_from_the_pdf_root_rather_than_typed(self):
        """A second literal path here is what would let #80's output rule and this
        module's idea of it go quietly out of step."""
        args = gate.build_parser().parse_args(["sheet.md", "--pdf-root", "/data/guidelines-src"])
        self.assertEqual(
            gate.text_root_for(args), extract.default_output(Path("/data/guidelines-src"))
        )

    def test_a_named_text_root_wins(self):
        args = gate.build_parser().parse_args(
            ["sheet.md", "--pdf-root", "/data/guidelines-src", "--text-root", "/elsewhere"]
        )
        self.assertEqual(gate.text_root_for(args), Path("/elsewhere"))

    def test_the_text_root_can_be_supplied_to_the_hook_by_environment(self):
        with mock.patch.dict(os.environ, {"CLINICAL_GUIDELINES_TEXT": "/shared/text"}):
            args = gate.build_parser().parse_args(["sheet.md"])

        self.assertEqual(gate.text_root_for(args), Path("/shared/text"))


class TheSheetReadmeDocumentsTheTwoNewGates(unittest.TestCase):
    """`TheGraderMatchesTheFormatItDocuments`' reasoning, for the two gates #174 added:
    a checker that has drifted from the file a reader opens is worse than none,
    because it reads as agreement."""

    def readme(self) -> str:
        return (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")

    def test_the_readme_names_both_commands(self):
        readme = self.readme()
        self.assertIn("--brief", readme)
        self.assertIn("--second-read", readme)
        self.assertIn("--text-root", readme)

    def test_the_readme_states_every_field_the_second_read_grader_requires(self):
        readme = self.readme()
        for field_name in gate.SECOND_READ_FIELDS + ("read_on", "briefed", "span", "pages"):
            self.assertIn(f'"{field_name}"', readme, f"{field_name} is not documented")

    def test_the_readme_says_a_second_read_is_a_smoke_test(self):
        self.assertIn("smoke test", self.readme().lower())

    def test_the_readme_still_says_the_marker_is_what_a_suspect_row_declares(self):
        self.assertIn(gate.RENDERED_MARKER, self.readme())

    def test_the_readme_defines_the_source_locator_contract(self):
        readme = self.readme()

        self.assertIn("p<digits>/<kind>/<id>", readme)
        self.assertIn("page prefix", readme)
        self.assertIn("reserved kind", readme)
        self.assertIn("class `narrative`", readme)

    def test_the_readme_states_the_strict_narrative_provenance_floor(self):
        readme = self.readme()

        self.assertIn("read` cell is exactly `yes`", readme)
        self.assertIn("outside the recommendation index", readme)
        self.assertIn("same page", readme)


class TheNotProbedNoticeSurvivesQuiet(unittest.TestCase):
    """The pre-commit hook runs `--all --quiet`, so anything that reaches a committer
    only through the report reaches nobody. `--quiet` suppresses the report and never
    a finding, and a gate that could not probe a source is a finding about the run --
    `gate_citation_tier2`'s banner rule, applied to the limb that first missed it.
    """

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )
        # A corpus that HAS a manifest -- so the gate ran -- but nothing in it the
        # sheet's source resolves to. The whole-corpus banner does not fire here,
        # which is exactly why this limb needed its own channel.
        text_corpus(self.root / "text", "Society/other", "a goal", boilerplate=["Jones et al"])

    def _quiet(self) -> tuple[str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                       text_root=self.root / "text", second_read_path=None, quiet=True)
        return out.getvalue(), err.getvalue()

    def test_quiet_still_names_the_source_that_could_not_be_probed(self):
        printed, errors = self._quiet()
        self.assertNotIn("WATERMARK", printed, "the report itself is suppressed")
        self.assertIn("NOT PROBED", errors)
        self.assertIn("src", errors)


class TheBriefAndTheDiffReadOneSetOfCitations(unittest.TestCase):
    """Two copies of the citation walk could drift into a work order naming a page the
    grader then reports as read off the brief -- the reader blamed for covering
    exactly what it was sent to. Shared rather than written twice, and pinned rather
    than asserted in a comment."""

    def test_every_page_the_brief_names_is_a_page_the_diff_counts_as_cited(self):
        rows = (
            row(page="p41")
            + row(page="p7", value="<80 mm Hg", snippet="a DBP goal of <80 mm Hg", rec="p7/g/1")
        )
        parsed = sheet(rows)
        work_order = gate.brief(parsed, "recommendation tables")
        self.assertIn("document: Society/doc", work_order)
        self.assertIn("span: recommendation tables", work_order)
        self.assertIn("pages: 1-50", work_order)
        read = gate.load_second_read_record(
            second_read(*[seen("<130 mm Hg", document=document, page=int(page))
                          for document, page in sorted(gate.cited_citations(parsed))]),
            Path("read.json"),
        )
        result = gate.gate_second_read(parsed, read)
        _, warnings, _, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertFalse(
            [warning for warning in warnings if "cites nowhere" in warning],
            "a read that covered exactly the brief must not be told it went off it",
        )


class GateFourRefusesUntilTheRenderedPageIsChecked(unittest.TestCase):
    """#296 rules that a suspect row turns the commit away until a working agent
    checks the rendered page. ``RENDERED:`` records that visual confirmation, so the
    clinician is not the routine verification bottleneck.
    """

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        text_corpus(self.root / "text", "Society/doc", "an SBP goal of <130 mm Hg",
                    boilerplate=["Jones et al"])
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row(snippet="an SBP goal of Jones et al <130 mm Hg")
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )

    def _run(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = grade(
                sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                text_root=self.root / "text", second_read_path=None,
                recs_root=self.root / "recs",
            )
        return status, out.getvalue(), err.getvalue()

    def test_the_gate_really_fires_on_this_sheet(self):
        """Otherwise the posture assertion below passes for the wrong reason."""
        _, printed, errors = self._run()
        self.assertIn("Jones et al", errors)
        self.assertIn("WATERMARK       1 refusing", printed)

    def test_it_refuses_until_an_agent_records_visual_confirmation(self):
        status, _, errors = self._run()
        interleave = [line for line in errors.splitlines() if "Jones et al" in line]
        self.assertEqual(status, 1)
        self.assertEqual(len(interleave), 1)
        self.assertTrue(interleave[0].strip().startswith("FAIL"), interleave[0])

        original = self.sheet_path.read_text(encoding="utf-8")
        self.sheet_path.write_text(
            original.replace(
                "an SBP goal of Jones et al <130 mm Hg",
                f"{gate.RENDERED_MARKER} an SBP goal of Jones et al <130 mm Hg",
            ),
            encoding="utf-8",
        )
        confirmed_status, confirmed_report, confirmed_errors = self._run()
        self.assertEqual(confirmed_status, 0)
        self.assertNotIn("Jones et al", confirmed_errors)
        self.assertIn(
            f"1 row(s) declared {gate.RENDERED_MARKER}", confirmed_report
        )

    def test_every_probe_that_hits_is_reported_and_not_only_the_first(self):
        """#83 asks for *every place* the text stream was interleaved, and a running
        head and a folio land on one line often enough that stopping at the first
        would report one and read as the whole. The first version broke out."""
        text_corpus(self.root / "text2", "Society/doc", "an SBP goal of <130 mm Hg",
                    boilerplate=["Jones et al"], margin=["Circulation 2025"])
        suspect = row(snippet="Jones et al an SBP goal of <130 mm Hg Circulation 2025")
        result = gate.gate_watermark(sheet(suspect), self.root / "text2")
        findings, _, _, _ = result.findings, result.skip_reason, result.rendered, result.unprobed_sources
        self.assertEqual(len(findings), 2)


class ASecondReadRecordsPageIsReadAsItsDigits(unittest.TestCase):
    """The brief prints locators as `p.41`, and `lstrip("pP")` left the dot — so a
    reader copying exactly what it was shown produced `.41`, matched no row, and had
    its work reported as read off the brief. Blaming a reader for covering what it
    was sent to is the worst failure this gate has, because it looks like a finding.
    """

    def test_a_page_written_the_way_the_brief_prints_it_still_matches(self):
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", page="p.41")), Path("read.json")
        )
        self.assertTrue(read.ok, read.why_not)
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg", page="p41")), read
        )
        refusals, warnings, pairings, _, uncovered = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual((refusals, warnings, uncovered), ([], [], []))
        self.assertEqual(len(pairings), 1)

    def test_a_page_with_no_digit_in_it_is_not_a_page(self):
        """Tolerant of a spelling, never of an absence: an entry keyed on something no
        row can carry reads as the reader having gone off the brief."""
        read = gate.load_second_read_record(
            second_read(seen("<130 mm Hg", page="the appendix")), Path("read.json")
        )
        self.assertFalse(read.ok)
        self.assertIn("page", read.why_not)


class TheSmokeTestCaveatSurvivesQuiet(unittest.TestCase):
    """#174 calls it a build instruction: *the tool's own output must say it is a
    smoke test*. `--quiet --second-read` printed WARN and NOT DIFFED lines with the
    caveat suppressed, which is the one configuration where a reader sees gate 5's
    findings and not what they are worth."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )
        self.read_path = self.root / "read.json"
        self.read_path.write_text(
            json.dumps(second_read(seen("<130 mm Hg"), seen("<80 mm Hg", about="the DBP goal"))),
            encoding="utf-8",
        )

    def test_quiet_suppresses_the_report_and_not_the_caveat(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                       text_root=None, second_read_path=self.read_path, quiet=True)
        printed = out.getvalue()
        self.assertNotIn("SECOND READ     ", printed, "the report itself is suppressed")
        self.assertIn(gate.SECOND_READ_IS_A_SMOKE_TEST, printed)

    def test_loud_keeps_the_caveat_beside_the_second_read_summary(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                  text_root=None, second_read_path=self.read_path)
        printed = out.getvalue()
        summary = printed.index("SECOND READ     0 refusing")
        caveat = printed.index(gate.SECOND_READ_IS_A_SMOKE_TEST)
        pairing = printed.index("bp-goal / adults")
        resolved = printed.index("last resolved")
        tier2_banner = printed.index("CITATION TIER 2 DID NOT RUN")
        self.assertLess(summary, caveat)
        self.assertLess(caveat, pairing)
        self.assertLess(pairing, resolved)
        self.assertLess(resolved, tier2_banner)

    def test_quiet_keeps_the_caveat_before_the_gate_banners(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            grade(sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                  text_root=None, second_read_path=self.read_path, quiet=True)
        printed = out.getvalue()
        self.assertLess(
            printed.index(gate.SECOND_READ_IS_A_SMOKE_TEST),
            printed.index("CITATION TIER 2 DID NOT RUN"),
        )


class OneStatementCanAnswerTwoRows(unittest.TestCase):
    """A guideline states one threshold in two places on a page and a sheet carries it
    as two rows for two populations, so a read comes back with duplicate values at one
    citation. Marking only the entry the match loop broke on left the duplicates
    unconsumed and warned that no row carried them.

    **Found by round-tripping the committed sheet through its own values** -- 74
    entries built from 74 rows produced 20 warnings, every one false. Neither the
    fixtures nor the earlier partial read reached it, which is `gate_range`'s and
    `block_scan.py`'s lesson a further time.
    """

    def _read(self, *values):
        return gate.load_second_read_record(second_read(*values), Path("read.json"))

    def test_two_entries_of_one_value_are_both_answered_by_one_row(self):
        read = self._read(
            seen("<130 mm Hg", about="stated in the recommendation table"),
            seen("<130 mm Hg", about="stated again in the summary figure"),
        )
        result = gate.gate_second_read(
            sheet(row(value="<130 mm Hg")), read
        )
        refusals, warnings, _, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [], "the second statement is the same threshold")

    def test_two_rows_sharing_a_value_do_not_consume_one_entry_between_them(self):
        """The other direction, and it is why entries are not matched one-to-one: a
        one-to-one pairing would refuse the second row for a number that is on the
        page. A false refusal is worse than a false warning."""
        read = self._read(seen("<130 mm Hg"))
        rows = (
            row(population="adults", value="<130 mm Hg")
            + row(population="adults-ckd", value="<130 mm Hg", rec="p41/goal/2")
        )
        result = gate.gate_second_read(sheet(rows), read)
        refusals, warnings, pairings, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(refusals, [])
        self.assertEqual(warnings, [])
        self.assertEqual(len(pairings), 2)

    def test_an_entry_no_row_accounts_for_still_warns(self):
        """Otherwise the fix would have bought its silence by never warning at all."""
        read = self._read(seen("<130 mm Hg"), seen("<80 mm Hg", about="the DBP goal"))
        result = gate.gate_second_read(sheet(row(value="<130 mm Hg")), read)
        _, warnings, _, _, _ = result.findings, result.warnings, result.pairings, result.undiffed, result.uncovered
        self.assertEqual(len(warnings), 1)
        self.assertIn("<80 mm Hg", warnings[0])


class AReadThatCoversNothingIsNotAGradedSheet(unittest.TestCase):
    """A well-formed record whose entries all land on pages the sheet does not cite
    makes every row `uncovered` and used to print `SECOND READ  0 refusing, 0 warning`
    and exit 0 — a gate that ran over nothing, reporting what a clean diff reports.

    That is `gate_coverage`'s NOT RUN case one gate over, and the shape every scanner
    in `tools/` exists to refuse. Found by the tracker sweep on this branch, not by a
    fixture: every fixture handed the gate a read that covered at least one citation.
    """

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.sheet_path = self.root / "sheet.md"
        self.sheet_path.write_text(
            header() + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
            + "\n## Conflicts\n\n\n## Coverage\n\n",
            encoding="utf-8",
        )
        self.read_path = self.root / "read.json"

    def _grade(self, *values) -> tuple[int, str]:
        self.read_path.write_text(json.dumps(second_read(*values)), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            status = grade(
                sheet_path=self.sheet_path, recs_arguments=[], pdf_root=None,
                text_root=None, second_read_path=self.read_path,
                recs_root=self.root / "recs",
            )
        return status, out.getvalue()

    def test_a_value_outside_the_brief_warns_but_the_named_span_is_graded(self):
        _, printed = self._grade(seen("<130 mm Hg", page=99))
        self.assertIn("SECOND READ     0 refusing", printed)

    def test_a_reader_finding_nothing_in_a_span_with_rows_warns(self):
        _, printed = self._grade()
        self.assertIn("SECOND READ     0 refusing, 1 warning", printed)

    def test_a_read_covering_one_citation_is_graded_and_not_reported_as_not_run(self):
        """The other direction, so the limb cannot be satisfied by never grading."""
        _, printed = self._grade(seen("<130 mm Hg"))
        self.assertIn("SECOND READ     0 refusing", printed)
        self.assertNotIn("SECOND READ     NOT RUN", printed)

    def test_the_smoke_test_caveat_prints_for_a_named_span_even_on_a_reader_miss(self):
        _, printed = self._grade(seen("<130 mm Hg", page=99))
        self.assertIn(gate.SECOND_READ_IS_A_SMOKE_TEST, printed)
