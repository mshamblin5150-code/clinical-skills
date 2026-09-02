"""Tests for the offline tracker-record readback formatter.

phi-scan: synthetic

The records and identifiers in this file are invented.  The module under test
receives already-fetched data and never opens a socket.
"""

from __future__ import annotations

import unittest

import tracker_readback as readback


class CitationSetsIncludeEveryRuledSpelling(unittest.TestCase):
    def test_mentions_urls_and_the_publication_target_form_one_set(self) -> None:
        text = (
            "Prose names #17, `code names #18`, and a quote:\n> #19 moved\n"
            "https://github.com/example/project/issues/20 and "
            "https://github.com/example/project/pull/21. Duplicate #17."
        )

        self.assertEqual(
            readback.citation_numbers(text, publication_number=16),
            frozenset({16, 17, 18, 19, 20, 21}),
        )

    def test_no_number_is_invented_for_a_create_publication(self) -> None:
        self.assertEqual(
            readback.citation_numbers("A body with no citation."),
            frozenset(),
        )


class FingerprintsExposeMetadataAndNeverBodyText(unittest.TestCase):
    def test_resolved_and_unresolved_records_each_get_an_honest_line(self) -> None:
        records = {
            17: {
                "number": 17,
                "state": "OPEN",
                "labels": {"nodes": [{"name": "ready"}, {"name": "bug"}]},
                "updatedAt": "2026-09-01T12:34:56Z",
                "body": "private tracker prose",
            },
            18: None,
        }

        lines = readback.fingerprint_lines(records)

        self.assertEqual(
            lines,
            (
                "tracker readback: #17 state=OPEN labels=[bug, ready] "
                "updatedAt=2026-09-01T12:34:56Z body_length=21",
                "tracker readback: #18 unresolved",
            ),
        )
        self.assertNotIn("private tracker prose", "\n".join(lines))

    def test_body_changes_are_visible_only_when_the_length_changes(self) -> None:
        first = {
            17: {
                "number": 17,
                "state": "OPEN",
                "labels": {"nodes": []},
                "updatedAt": "2026-09-01T12:34:56Z",
                "body": "alpha",
            }
        }
        same_length = {17: {**first[17], "body": "bravo"}}
        longer = {17: {**first[17], "body": "charlie"}}

        self.assertEqual(
            readback.fingerprint_lines(first),
            readback.fingerprint_lines(same_length),
        )
        self.assertNotEqual(
            readback.fingerprint_lines(first),
            readback.fingerprint_lines(longer),
        )


class DeclaredLimitsHavePositiveControls(unittest.TestCase):
    def test_the_offline_module_owns_exactly_the_two_ruled_limits(self) -> None:
        self.assertEqual(
            set(dict(readback.NOT_REACHED)),
            {
                "a fingerprint says a record moved, never what moved",
                "class (c), a verdict naming no record, is permanently unreachable",
            },
        )

    def test_an_empty_citation_set_names_class_c(self) -> None:
        self.assertEqual(
            readback.empty_citation_line(),
            "tracker readback: no cited record number; class (c) is reached by no mechanism",
        )


if __name__ == "__main__":
    unittest.main()
