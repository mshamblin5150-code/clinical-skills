"""Public-boundary tests for tracker population probe derivation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import tracker_population


ISSUE_TRACKER = (
    Path(__file__).resolve().parent.parent / "docs" / "agents" / "issue-tracker.md"
)


def response(body: object, link: str = "") -> str:
    headers = "HTTP/2.0 200 OK\nContent-Type: application/json"
    if link:
        headers += f"\nLink: {link}"
    return headers + "\n\n" + json.dumps(body)


class PopulationRoutesAreIndependent(unittest.TestCase):
    def test_issue_population_sums_graphql_issue_and_pull_totals(self):
        text = json.dumps({
            "data": {"repository": {
                "issues": {"totalCount": 7},
                "pullRequests": {"totalCount": 5},
            }}
        })
        self.assertEqual(tracker_population.issue_population(text), 12)

    def test_comment_population_uses_the_last_page_at_per_page_one(self):
        link = (
            '<https://api.github.test/comments?per_page=1&page=2>; rel="next", '
            '<https://api.github.test/comments?per_page=1&page=37>; rel="last"'
        )
        self.assertEqual(tracker_population.comment_population(response([{}], link)), 37)

    def test_absent_link_and_an_empty_probe_establish_zero(self):
        self.assertEqual(tracker_population.comment_population(response([])), 0)

    def test_absent_link_and_one_probe_row_establish_one(self):
        self.assertEqual(tracker_population.comment_population(response([{}])), 1)

    def test_absent_link_cannot_establish_a_larger_population(self):
        with self.assertRaises(tracker_population.PopulationError):
            tracker_population.comment_population(response([{}, {}]))

    def test_a_last_page_from_any_page_size_beside_one_is_refused(self):
        link = (
            '<https://api.github.test/comments?per_page=100&page=2>; rel="next", '
            '<https://api.github.test/comments?per_page=100&page=37>; rel="last"'
        )
        with self.assertRaises(tracker_population.PopulationError):
            tracker_population.comment_population(response([{}], link))


class TheCommandWritesTheScannerManifest(unittest.TestCase):
    def test_three_kept_probes_produce_the_per_file_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            issues = root / "issues.json"
            comments = root / "comments.http"
            reviews = root / "reviews.http"
            target = root / "population.json"
            issues.write_text(json.dumps({
                "data": {"repository": {
                    "issues": {"totalCount": 7},
                    "pullRequests": {"totalCount": 5},
                }}
            }), encoding="utf-8")
            comments.write_text(response([{}], (
                '<https://api.github.test/comments?per_page=1&page=9>; rel="last"'
            )), encoding="utf-8")
            reviews.write_text(response([]), encoding="utf-8")

            status = tracker_population.main([
                str(issues), str(comments), str(reviews),
                "--write", str(target),
            ])

            self.assertEqual(status, 0)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {
                "version": 1,
                "populations": {
                    "tracker-issues.json": 12,
                    "tracker-comments.json": 9,
                    "tracker-reviews.json": 0,
                },
            })


class DocumentedPopulationCommands(unittest.TestCase):
    def test_the_label_numerator_uses_compatible_gh_flags(self):
        prose = ISSUE_TRACKER.read_text(encoding="utf-8")
        refused_combination = "--jq " + "'add | length'"
        self.assertNotIn(refused_combination, prose)
        self.assertIn("sum(len(page) for page in json.load(sys.stdin))", prose)


if __name__ == "__main__":
    unittest.main()
