"""Behavior tests for the shared heading-read record at its text-and-bytes seam.

All drafts and claim records are synthetic. No patient or classmate is represented.

phi-scan: synthetic
"""

from __future__ import annotations

import unittest

import heading_read
import research_ledger
from prose_bind import NAMING, bind


CLAIMS = """\
DATE: 2026-09-13

## CLAIM: Supported heading.
STATUS: sourced

## CLAIM: Dropped heading.
STATUS: sourced
DROPPED: the draft no longer makes this claim
"""
DRAFT = b"Draft sentence.\n"
DRAFT_DIGEST = "ab80d41641dd1eb842c7e9716e6302ceaafb8bb9b36cf999d9f961f094b2cfcb"
CONTEXT_DIGEST = "c" * 64


def record(
    *,
    route: str = "separate context",
    pairs: tuple[str, ...] = ("paragraph 1 -> 1cb3a5b6",),
    verdict: str = "clean",
    findings: tuple[str, ...] = (),
    context_digest: str = CONTEXT_DIGEST,
    context_verdict: str = "agrees",
) -> str:
    lines = [
        "## HEADING-READ: draft.md",
        f"DRAFT: {DRAFT_DIGEST}",
        f"ROUTE: {route}",
        "SENTENCES: 1 factual, 1 clinician's own",
        *(f"PAIR: {pair}" for pair in pairs),
        f"CONTEXT-DIGEST: {context_digest}",
        f"CONTEXT-VERDICT: {context_verdict}",
        f"VERDICT: {verdict}",
        *(f"FINDINGS: {finding}" for finding in findings),
    ]
    return "\n".join(lines) + "\n"


def scan(text: str) -> heading_read.Scan:
    binding = heading_read.Binding(
        artifact="draft.md",
        draft=DRAFT,
        claims=tuple(research_ledger.read_records(CLAIMS)),
        context_digest=CONTEXT_DIGEST,
    )
    return heading_read.scan(text, (binding,))


class AHeadingReadBindsTheDraftToCurrentClaimHeadings(unittest.TestCase):
    def test_the_declared_limits_have_their_no_copy_bind(self):
        self.assertEqual((), bind(heading_read.DECLARED_LIMITS, heading_read.__doc__, mode=NAMING))

    def test_a_clean_current_record_passes_and_reports_its_coverage(self):
        result = scan(record())

        self.assertEqual((), result.findings)
        self.assertEqual((result.records_read, result.unread), (1, 0))

    def test_an_absent_record_is_a_finding(self):
        self.assertEqual(
            [heading_read.MISSING_RECORD],
            [finding.kind for finding in scan("").findings],
        )

    def test_two_records_for_one_draft_are_refused(self):
        result = scan(record() + "\n" + record())
        self.assertIn(heading_read.DUPLICATE_RECORD, [f.kind for f in result.findings])

    def test_a_heading_shaped_candidate_the_parser_cannot_read_is_only_the_remainder(self):
        result = scan(record() + "\n## HEADING-READ draft-without-a-colon.md\n")
        self.assertEqual(1, result.unread)
        self.assertEqual((), result.findings)
        self.assertEqual(
            "heading-read records: 1\nunread remainder 1",
            heading_read.format_coverage(result),
        )

    def test_only_the_two_ruled_routes_are_recognized(self):
        self.assertEqual(
            [heading_read.UNKNOWN_ROUTE],
            [finding.kind for finding in scan(record(route="same context")).findings],
        )
        self.assertFalse(scan(record(route="orchestrator walk")).findings)

    def test_pairs_plus_findings_must_equal_the_declared_factual_count(self):
        self.assertIn(
            heading_read.SENTENCE_COUNT_MISMATCH,
            [finding.kind for finding in scan(record(pairs=())).findings],
        )
        balanced = record(pairs=(), verdict="defect - one sentence is unrecorded", findings=("unrecorded - paragraph 1, no heading states it",))
        self.assertNotIn(
            heading_read.SENTENCE_COUNT_MISMATCH,
            [finding.kind for finding in scan(balanced).findings],
        )

    def test_a_clean_pair_becomes_stale_when_its_heading_is_edited(self):
        edited_claims = CLAIMS.replace("Supported heading.", "Supported heading!")
        changed = heading_read.Binding(
            artifact="draft.md",
            draft=DRAFT,
            claims=tuple(research_ledger.read_records(edited_claims)),
            context_digest=CONTEXT_DIGEST,
        )
        result = heading_read.scan(record(), (changed,))
        self.assertEqual(
            [heading_read.UNKNOWN_HEADING],
            [finding.kind for finding in result.findings],
        )

    def test_a_pair_to_a_dropped_record_is_a_finding(self):
        self.assertEqual(
            [heading_read.DROPPED_HEADING],
            [finding.kind for finding in scan(record(pairs=("paragraph 1 -> 54440ec8",))).findings],
        )

    def test_a_changed_draft_expires_the_read(self):
        changed = heading_read.Binding(
            artifact="draft.md",
            draft=b"Draft sentence!\n",
            claims=tuple(research_ledger.read_records(CLAIMS)),
            context_digest=CONTEXT_DIGEST,
        )
        result = heading_read.scan(record(), (changed,))
        self.assertEqual([heading_read.DRAFT_MISMATCH], [f.kind for f in result.findings])

    def test_a_defect_verdict_blocks_even_without_a_findings_line(self):
        self.assertIn(
            heading_read.DEFECT_VERDICT,
            [finding.kind for finding in scan(record(verdict="defect - the pairing drifted")).findings],
        )

    def test_any_findings_line_blocks_even_when_the_verdict_says_clean(self):
        result = scan(record(verdict="clean", findings=("drifted - paragraph 1, subject broadened",)))
        self.assertIn(heading_read.REPORTED_FINDING, [f.kind for f in result.findings])

    def test_the_context_digest_must_equal_the_project_context_record(self):
        result = scan(record(context_digest="d" * 64))
        self.assertIn(heading_read.CONTEXT_DIGEST_MISMATCH, [f.kind for f in result.findings])

    def test_agrees_is_the_only_clean_context_verdict(self):
        for verdict in (
            "narrows - planning file, founder motive lost",
            "contradicts - memory index, audience differs",
            "sources-conflict - memory index and thought-17, motives differ",
        ):
            with self.subTest(verdict=verdict):
                result = scan(record(context_verdict=verdict))
                self.assertIn(
                    heading_read.CONTEXT_DEFECT_VERDICT,
                    [finding.kind for finding in result.findings],
                )

    def test_a_non_agreeing_verdict_needs_location_and_difference(self):
        result = scan(record(context_verdict="narrows"))
        self.assertIn(
            heading_read.CONTEXT_VERDICT_SHAPE,
            [finding.kind for finding in result.findings],
        )

    def test_a_sources_conflict_verdict_names_two_sources(self):
        one_source = scan(
            record(context_verdict="sources-conflict - memory index, motives differ")
        )
        two_sources = scan(
            record(
                context_verdict=(
                    "sources-conflict - memory index and thought-17, motives differ"
                )
            )
        )

        self.assertIn(
            heading_read.CONTEXT_VERDICT_SHAPE,
            [finding.kind for finding in one_source.findings],
        )
        self.assertNotIn(
            heading_read.CONTEXT_VERDICT_SHAPE,
            [finding.kind for finding in two_sources.findings],
        )
        for verdict in (
            "sources-conflict - memory index and  , motives differ",
            "sources-conflict - memory index and memory index, motives differ",
        ):
            with self.subTest(verdict=verdict):
                result = scan(record(context_verdict=verdict))
                self.assertIn(
                    heading_read.CONTEXT_VERDICT_SHAPE,
                    [finding.kind for finding in result.findings],
                )

    def test_a_none_run_requires_both_context_fields_to_be_none(self):
        binding = heading_read.Binding(
            artifact="draft.md",
            draft=DRAFT,
            claims=tuple(research_ledger.read_records(CLAIMS)),
            context_digest="none",
        )
        clean = heading_read.scan(
            record(context_digest="none", context_verdict="none"), (binding,)
        )
        self.assertEqual((), clean.findings)
        wrong = heading_read.scan(
            record(context_digest="none", context_verdict="agrees"), (binding,)
        )
        self.assertIn(
            heading_read.CONTEXT_DEFECT_VERDICT,
            [finding.kind for finding in wrong.findings],
        )

    def test_records_for_another_draft_are_the_unread_remainder(self):
        text = record().replace("draft.md", "other.md", 1)
        result = scan(text)
        self.assertEqual((result.records_read, result.unread), (0, 1))
        self.assertIn(heading_read.MISSING_RECORD, [f.kind for f in result.findings])


if __name__ == "__main__":
    unittest.main()
