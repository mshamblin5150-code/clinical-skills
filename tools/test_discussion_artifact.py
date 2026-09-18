"""Public parser tests for shared discussion artifact shapes.

All records are synthetic. No classmate or patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

import discussion_artifact as artifact
from prose_bind import NAMING, bind
from run_grader import EvidenceDisposition


APA_SHEET = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "reference" / "apa7.md"


def shared_claim_consumers_without_certifier(
    sources: dict[str, str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return shared-parser consumers and the subset missing the certifier call."""

    consumers = []
    missing = []
    for name, source in sorted(sources.items()):
        tree = ast.parse(source, filename=name)
        imports_claim_block = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "discussion_artifact"
            and any(alias.name == "CLAIM_BLOCK" for alias in node.names)
            for node in ast.walk(tree)
        )
        if not imports_claim_block:
            continue
        consumers.append(name)
        predicate_names = {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "discussion_artifact"
            for alias in node.names
            if alias.name == "claim_record_can_certify_values"
        }
        calls_shared_predicate = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in predicate_names
            for node in ast.walk(tree)
        )
        if not calls_shared_predicate:
            missing.append(name)
    return tuple(consumers), tuple(missing)


class ClaimValueCertificationRequiresRefutationEvidence(unittest.TestCase):
    def test_both_refutation_evidence_fields_need_substance(self):
        complete = (
            "A result was confirmed.\n"
            "STATUS: sourced\n"
            "REFUTATION: stands - the result was confirmed.\n"
            "TESTED-HEADING: 116a0979d429b49e41c8c3702b97d17570f7445895c37ca5c1c968796ae150e0\n"
            "SECOND-ROUTE: publisher HTML -> journal PDF\n"
        )
        cases = (
            complete.replace("REFUTATION: stands - the result was confirmed.\n", ""),
            complete.replace("REFUTATION: stands - the result was confirmed.", "REFUTATION: --"),
            complete.replace(
                "TESTED-HEADING: 116a0979d429b49e41c8c3702b97d17570f7445895c37ca5c1c968796ae150e0\n",
                "",
            ),
            complete.replace("SECOND-ROUTE: publisher HTML -> journal PDF\n", ""),
            complete.replace("SECOND-ROUTE: publisher HTML -> journal PDF", "SECOND-ROUTE: ->"),
        )

        self.assertTrue(artifact.claim_record_can_certify_values(complete))
        for block in cases:
            with self.subTest(block=block):
                self.assertFalse(artifact.claim_record_can_certify_values(block))

    def test_a_digest_for_the_heading_before_an_edit_is_disbelieved(self):
        block = (
            "A result was confirmed!\n"
            "STATUS: sourced\n"
            "REFUTATION: stands - the result was confirmed.\n"
            "TESTED-HEADING: 116a0979d429b49e41c8c3702b97d17570f7445895c37ca5c1c968796ae150e0\n"
            "SECOND-ROUTE: publisher HTML -> journal PDF\n"
        )
        self.assertFalse(artifact.claim_record_can_certify_values(block))

    def test_a_dropped_record_cannot_certify_values(self):
        dropped = (
            "A result was confirmed.\n"
            "STATUS: sourced\n"
            "REFUTATION: stands - the result was confirmed.\n"
            "TESTED-HEADING: 116a0979d429b49e41c8c3702b97d17570f7445895c37ca5c1c968796ae150e0\n"
            "SECOND-ROUTE: publisher HTML -> journal PDF\n"
            "DROPPED: the draft no longer makes this claim\n"
        )

        self.assertFalse(artifact.claim_record_can_certify_values(dropped))


class EverySharedClaimBlockConsumerUsesTheSharedCertificationRule(unittest.TestCase):
    def test_every_importer_calls_the_shared_predicate(self):
        """A module spelling its own ``## CLAIM:`` pattern is outside this guard."""

        tools = Path(__file__).resolve().parent
        sources = {
            path.name: path.read_text(encoding="utf-8")
            for path in tools.glob("*.py")
            if not path.name.startswith("test_")
        }
        consumers, missing = shared_claim_consumers_without_certifier(sources)

        self.assertTrue(consumers)
        self.assertEqual((), missing)

    def test_a_missing_call_is_detected_and_a_private_pattern_is_outside_the_guard(self):
        consumers, missing = shared_claim_consumers_without_certifier(
            {
                "missing.py": "from discussion_artifact import CLAIM_BLOCK\nCLAIM_BLOCK.findall('')\n",
                "passing.py": (
                    "from discussion_artifact import CLAIM_BLOCK, "
                    "claim_record_can_certify_values as certifies\n"
                    "certifies('')\n"
                ),
                "private_pattern.py": "CLAIM_BLOCK = r'## CLAIM:'\n",
            }
        )

        self.assertEqual(("missing.py", "passing.py"), consumers)
        self.assertEqual(("missing.py",), missing)


def republished_work_rows() -> tuple[tuple[str, str], ...]:
    sheet = APA_SHEET.read_text(encoding="utf-8")
    section = sheet.split(
        "## 31. Two dates for republished, translated, reissued, religious, and classical works",
        1,
    )[1].split("\n## ", 1)[0]
    return tuple(
        (cells[0], cells[1])
        for line in section.splitlines()
        for cells in (re.findall(r"`([^`]*)`", line),)
        if line.startswith("| `") and len(cells) >= 2
    )


class ReferenceKeysUseTheTitleProper(unittest.TestCase):
    def test_a_trailing_translator_credit_is_not_part_of_the_key(self):
        entry = next(
            entry
            for entry, _citation in republished_work_rows()
            if entry.startswith("The epic of Gilgamesh")
        )

        self.assertEqual(
            (("epicofgilgamesh", "1998"),),
            artifact.reference_keys(entry),
        )


class CitationResolutionIsDirectional(unittest.TestCase):
    def test_first_name_form_joins_only_a_listed_first_initial(self):
        entries = (
            "Williams, S. M. (2019). First study. Publisher.",
            "Williams, S. (2020). Second study. Publisher.",
        )
        references = artifact.ReferenceKeySet.from_references(entries)
        cases = (
            ("Sarah Williams (2019) stated this.", True),
            ("(Shonda Williams, 2020) stated this.", True),
            ("(Range Williams, 2019) stated this.", False),
            ("Sarah M. Williams (2019) stated this.", False),
            ("Mary-Kate Williams (2019) stated this.", False),
        )
        for body, expected in cases:
            with self.subTest(body=body):
                citations = artifact.read_citations(body, references)
                occurrences = artifact.citation_occurrence_keys(citations, body, references)
                self.assertEqual(expected, any(references.resolves(key) for keys in occurrences for key in keys))
                self.assertFalse(any(references.missing_first_author_initials(c.author) for c in citations))

        wrong_name = artifact.ReferenceKeySet.from_references(
            ("Williams, R. (2019). Study. Publisher.",)
        )
        body = "(Range Williams, 2019)"
        citations = artifact.read_citations(body, wrong_name)
        occurrences = artifact.citation_occurrence_keys(citations, body, wrong_name)
        self.assertTrue(any(wrong_name.resolves(key) for keys in occurrences for key in keys))

    def test_first_name_form_keeps_coauthor_tails_and_satisfies_initials(self):
        references = artifact.ReferenceKeySet.from_references((
            "Williams, S., & Jones, P. (2019). First study. Publisher.",
            "Williams, S., Jones, P., & Doe, R. (2020). Second study. Publisher.",
            "Williams, R. (2021). Third study. Publisher.",
        ))
        for body in (
            "(Sarah Williams & Jones, 2019)",
            "Sarah Williams and Jones (2019) report this.",
            "(Shonda Williams et al., 2020)",
            "Shonda Williams et al. (2020) report this.",
        ):
            with self.subTest(body=body):
                citations = artifact.read_citations(body, references)
                occurrences = artifact.citation_occurrence_keys(citations, body, references)
                self.assertEqual(1, len(citations))
                self.assertTrue(any(references.resolves(key) for keys in occurrences for key in keys))
                self.assertFalse(references.missing_first_author_initials(citations[0].author))

        body = "(Range Williams, 2019)"
        citations = artifact.read_citations(body, references)
        occurrences = artifact.citation_occurrence_keys(citations, body, references)
        self.assertFalse(any(references.resolves(key) for keys in occurrences for key in keys))

    def test_group_abbreviation_requires_an_earlier_reference_backed_definition(self):
        references = artifact.ReferenceKeySet.from_references((
            "American Psychological Association. (2017). Report. Publisher.",
        ))
        cases = (
            "The American Psychological Association (APA) reported this (APA, 2017).",
            "The American Psychological Association (APA, 2017) reported this. "
            "Later (APA, 2017).",
            "(American Psychological Association [APA], 2017). Later (APA, 2017).",
            "American Psychological\nAssociation (APA) reported this (APA, 2017).",
        )
        for body in cases:
            with self.subTest(body=body):
                citations = artifact.read_citations(body, references)
                occurrences = artifact.citation_occurrence_keys(citations, body, references)
                self.assertTrue(occurrences)
                self.assertTrue(all(any(references.resolves(key) for key in keys) for keys in occurrences))

        before = "(APA, 2017). The American Psychological Association (APA) reported this."
        citations = artifact.read_citations(before, references)
        keys = artifact.citation_occurrence_keys(citations, before, references)
        self.assertFalse(any(references.resolves(key) for key in keys[0]))

    def test_colliding_group_abbreviations_resolve_for_neither_group(self):
        references = artifact.ReferenceKeySet.from_references((
            "American Psychological Association. (2017). Report. Publisher.",
            "American Pediatric Association. (2017). Report. Publisher.",
        ))
        body = (
            "American Psychological Association (APA) and American Pediatric "
            "Association (APA) reported this (APA, 2017)."
        )
        citations = artifact.read_citations(body, references)
        keys = artifact.citation_occurrence_keys(citations, body, references)
        self.assertFalse(any(references.resolves(key) for key in keys[-1]))

    def test_a_shortened_title_resolves_without_becoming_a_member(self):
        references = artifact.ReferenceKeySet.from_references(
            (
                "Diagnostic and statistical manual of mental disorders "
                "(5th ed., text rev.). (2022). Publisher.",
            )
        )
        citation_key = ("diagnosticandstatisticalmanual", "2022")

        self.assertTrue(references.resolves(citation_key))
        self.assertNotIn(citation_key, references)
        self.assertNotIn(citation_key, tuple(references))

    def test_a_personal_surname_still_requires_equality(self):
        references = artifact.ReferenceKeySet.from_references(
            ("Smith, J. (2022). A title. Publisher.",)
        )

        self.assertFalse(references.resolves(("smi", "2022")))
        self.assertTrue(references.resolves(("smith", "2022")))

    def test_every_republished_work_form_in_the_apa_sheet_resolves(self):
        rows = republished_work_rows()
        self.assertTrue(rows)

        for entry, written_citation in rows:
            with self.subTest(citation=written_citation):
                references = artifact.ReferenceKeySet.from_references((entry,))
                citations = artifact.read_citations(written_citation, references)
                occurrences = artifact.citation_occurrence_keys(citations)

                self.assertTrue(citations)
                self.assertTrue(
                    all(
                        any(references.resolves(key) for key in occurrence)
                        for occurrence in occurrences
                    )
                )

    def test_synthetic_credit_edition_and_shortened_title_forms_resolve(self):
        cases = (
            (
                "The handbook of nursing (J. Smith, Ed.). (2021). Publisher.",
                ("handbookofnursing", "2021"),
            ),
            (
                "Nursing today (2nd ed.). (2020). Publisher.",
                ("nursingtoday", "2020"),
            ),
            (
                "Diagnostic and statistical manual of mental disorders "
                "(5th ed., text rev.). (2022). Publisher.",
                ("diagnosticandstatisticalmanual", "2022"),
            ),
        )

        for entry, citation_key in cases:
            with self.subTest(entry=entry):
                references = artifact.ReferenceKeySet.from_references((entry,))
                self.assertTrue(references.resolves(citation_key))

    def test_legal_entries_are_classified_before_the_no_surname_fallback(self):
        cases = (
            (
                "Professional and Vocational Regulations, 16 CCR § 1481",
                (("professionalandvocationalregulations", ""),),
            ),
            (
                "Eligibility for prescriptive authority, W. Va. Code § 30-7-15b",
                (("eligibilityforprescriptiveauthority", ""),),
            ),
            (
                "Consolidated Appropriations Act, 2023, Pub. L. No. 117-328, § 1263",
                (("consolidatedappropriationsact2023", ""),),
            ),
            (
                "Payment for nurse practitioners' services, 42 C.F.R. § 414.56",
                (("paymentfornursepractitionersservices", ""),),
            ),
            (
                "Advanced practice registered nurse licensure requirements "
                "(W. Va. Code R. § 19-7, 2024)",
                (("advancedpracticeregisterednurselicensurerequirements", ""),),
            ),
            ("King James Bible.", ()),
            ("World Health Organization.", ()),
            ("Smith, J.", ()),
        )

        for entry, expected in cases:
            with self.subTest(entry=entry):
                self.assertEqual(expected, artifact.reference_keys(entry))

    def test_resolution_residues_share_one_declared_object(self):
        self.assertIn(
            "whether a republished citation's original element matches its source",
            {
                subject
                for subject, _reason, _disposition in artifact.CITATION_RESOLUTION_NOT_REACHED
            },
        )
        self.assertTrue(
            all(
                disposition is EvidenceDisposition.BEHAVIOR
                for _subject, _reason, disposition in artifact.CITATION_RESOLUTION_NOT_REACHED
            )
        )
        self.assertEqual(
            (),
            bind(
                artifact.CITATION_RESOLUTION_NOT_REACHED,
                artifact.__doc__ or "",
                mode=NAMING,
            ),
        )


class PostedReadingsAreSharedArtifacts(unittest.TestCase):
    def test_a_portal_record_preserves_each_visit_locator(self):
        records = artifact.read_posted_readings(
            """\
## REREAD: shift-2026-08-17
POST-URL: https://example.org/patient-visits
POSTED: 08/17/2026 21:14
READ: 2 of 2 read
VERDICT: matches - Every saved visit and note form matched the approved review.
SUBMISSION-SHA256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
VISIT: 1 | reference matched | patient-detail=/patients/17 | note-view=/forms/view?resultid=31 | visit-date=08/17/2026 | matches
VISIT: 2 | reference new | patient-detail=/patients/18 | note-view=/forms/view?resultid=32 | created=08/17/2026 21:14 | matches
"""
        )

        self.assertEqual(1, len(records))
        self.assertEqual(2, len(records[0].visits))
        self.assertIn("resultid=31", records[0].visits[0])
        self.assertIn("reference new", records[0].visits[1])

    def test_one_record_preserves_the_entry_and_verdict_substance(self):
        records = artifact.read_posted_readings(
            """\
## REREAD: response-maren.md
POST-URL: https://example.org/courses/1/discussion_topics/2?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
SUBMISSION-SHA256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
VERDICT: matches - The paragraphs, references, and bold label are present.
"""
        )

        self.assertEqual(1, len(records))
        self.assertEqual("response-maren.md", records[0].artifact)
        self.assertEqual("matches", records[0].verdict)
        self.assertEqual(
            "The paragraphs, references, and bold label are present.",
            records[0].verdict_detail,
        )
        self.assertEqual((), records[0].missing_fields)

    def test_an_absent_file_can_be_represented_by_no_records(self):
        self.assertEqual((), artifact.read_posted_readings(""))

    def test_a_malformed_fingerprint_is_parsed_for_a_grader_to_refuse(self):
        records = artifact.read_posted_readings(
            """\
## REREAD: response-maren.md
POST-URL: https://example.org/topic?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
SUBMISSION-SHA256: NOT-A-DIGEST
VERDICT: matches - The entry was read from the board.
"""
        )

        self.assertEqual("NOT-A-DIGEST", records[0].submission_sha256)
        self.assertFalse(records[0].submission_sha256_is_valid)

    def test_duplicate_entry_records_are_unreadable(self):
        record = """\
## REREAD: response-maren.md
POST-URL: https://example.org/topic?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
VERDICT: matches - The entry was read from the board.
"""

        with self.assertRaisesRegex(ValueError, "duplicate REREAD"):
            artifact.read_posted_readings(record + "\n" + record)

    def test_nonrecord_content_is_unreadable(self):
        with self.assertRaisesRegex(ValueError, "no readable REREAD"):
            artifact.read_posted_readings("VERDICT: matches - trust me\n")

    def test_unrecognized_content_inside_a_record_is_unreadable(self):
        with self.assertRaisesRegex(ValueError, "unreadable content"):
            artifact.read_posted_readings(
                """\
## REREAD: post.md
POST-URL: https://example.org/topic?entry_id=41
POSTED: 2026-08-28T19:30:00-04:00
READ: 2026-08-28
VERDICT: matches - The board was read.
TRUST-ME: yes
"""
            )

    def test_both_discussion_skills_publish_a_record_the_shared_parser_reads(self):
        root = Path(__file__).resolve().parents[1]
        for skill_name in ("discussion-post", "discussion-reply"):
            with self.subTest(skill=skill_name):
                skill = (root / "skills" / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                block = re.search(
                    r"```text\n(?P<record>## REREAD:.*?VERDICT:.*?\n)```",
                    skill,
                    re.DOTALL,
                )
                self.assertIsNotNone(block)
                records = artifact.read_posted_readings(block.group("record"))
                self.assertEqual(1, len(records))
                self.assertEqual((), records[0].missing_fields)


if __name__ == "__main__":
    unittest.main()
