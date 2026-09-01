"""A merged PR leaves an immutable state receipt on every ticket it names."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tracker_merge_receipt as receipt


def merged_pr(body: str, **changes):
    document = {
        "number": 401,
        "url": "https://github.com/example/clinical-skills/pull/401",
        "title": "Implement the tracker receipt",
        "body": body,
        "baseRefName": "main",
        "mergedAt": "2026-08-20T22:30:00Z",
        "mergeCommit": {"oid": "0123456789abcdef0123456789abcdef01234567"},
        "commits": [],
    }
    document.update(changes)
    return document


class ExplicitTicketReferencesBecomeReceipts(unittest.TestCase):
    def test_every_declared_reference_form_owns_its_decorated_line(self):
        for alternative in receipt.REFERENCE_ALTERNATIVES:
            reference = alternative.example
            with self.subTest(form=alternative.name, shape="period"):
                self.assertIsNotNone(receipt.REFERENCE.fullmatch(f"{reference}."))
            with self.subTest(form=alternative.name, shape="bold-list"):
                self.assertIsNotNone(
                    receipt.REFERENCE.fullmatch(f"- **{reference}.**")
                )
            with self.subTest(form=alternative.name, shape="punctuation-after-bold"):
                self.assertIsNotNone(
                    receipt.REFERENCE.fullmatch(f"- **{reference}**.")
                )
            with self.subTest(form=alternative.name, shape="ordered-blockquote"):
                self.assertIsNotNone(
                    receipt.REFERENCE.fullmatch(f"> 1. _{reference}._")
                )
            with self.subTest(form=alternative.name, shape="comma-list"):
                self.assertIsNotNone(
                    receipt.REFERENCE.fullmatch(f"{reference}, #531, #532.")
                )
            for shared_line in (
                f"{reference}. More work remains.",
                f"Ruling only. {reference}.",
            ):
                with self.subTest(form=alternative.name, shape="shared-line"):
                    self.assertIsNone(receipt.REFERENCE.search(shared_line))
            with self.subTest(form=alternative.name, shape="mismatched-emphasis"):
                self.assertIsNone(receipt.REFERENCE.fullmatch(f"**{reference}_"))

    def test_recorded_530_instances_stay_on_their_ruled_side_of_the_line(self):
        instances = {
            "1956c7d": ("Part of #530.", True),
            "5b0a465": ("Part of #530, #531, #532.", True),
            "da4fee2 / PR #522": ("Nothing built. Part of #530.", False),
            "PR #508": ("Implements #530's decisions 1-3. Sweep follows.", False),
            "PR #543": ("Ruling only. Part of #530", False),
            "PR #559": ("Implements #530's option 1, and option 3.", False),
            "PR #560": ("Part of #530; the build is still to come.", False),
        }

        for instance, (line, expected) in instances.items():
            with self.subTest(instance=instance):
                self.assertEqual(receipt.REFERENCE.fullmatch(line) is not None, expected)

    def test_whole_and_partial_ticket_forms_each_get_one_receipt(self):
        document = merged_pr(
            "Closes #290\n\nPart of #298\n\nImplements #300's lead 2\n"
        )

        rows = receipt.plan_receipts(document)

        self.assertEqual([row.ticket for row in rows], [290, 298, 300])
        for row in rows:
            self.assertIn("PR #401", row.body)
            self.assertIn("`main`", row.body)
            self.assertIn("`0123456789abcdef0123456789abcdef01234567`", row.body)
            self.assertIn("2026-08-20", row.body)
            self.assertIn("does not make later names or claims current", row.body)

    def test_distinct_leads_on_one_ticket_keep_their_claim_identity(self):
        document = merged_pr(
            "Implements #300's lead 1\n\nImplements #300's lead 2\n"
        )

        rows = receipt.plan_receipts(document)

        self.assertEqual([row.ticket for row in rows], [300, 300])
        self.assertIn("`Implements #300's lead 1`", rows[0].body)
        self.assertIn("`Implements #300's lead 2`", rows[1].body)

    def test_comma_list_binds_each_ticket_and_preserves_the_authors_unit_noun(self):
        rows = receipt.plan_receipts(
            merged_pr("Implements #530's options 1-3, #531.\n")
        )

        self.assertEqual([row.ticket for row in rows], [530, 531])
        self.assertIn("`Implements #530's options 1-3`", rows[0].body)
        self.assertIn("`Implements #531's options 1-3`", rows[1].body)
        for row in rows:
            self.assertEqual(
                receipt.parse_merge_receipt(row.body).claim,
                row.body.partition("Merge claim: `")[2].partition("`")[0],
            )

    def test_duplicate_references_across_pr_and_commit_text_are_one_receipt(self):
        document = merged_pr("Part of #290\n")
        document["commits"] = [
            {
                "messageHeadline": "Implement receipt",
                "messageBody": "Part of #290\n",
            }
        ]

        self.assertEqual(
            [row.ticket for row in receipt.plan_receipts(document)],
            [290],
        )

    def test_prose_and_ambiguous_references_do_not_bind(self):
        document = merged_pr(
            "This follows #290.\n"
            "The branch was merged with main for #278.\n"
            "Implements the idea in #300.\n"
        )

        self.assertEqual(receipt.plan_receipts(document), [])

    def test_an_unbounded_partial_description_is_not_republished(self):
        document = merged_pr("Implements #300's arbitrary claim with `markup`\n")

        self.assertEqual(receipt.plan_receipts(document), [])

    def test_a_pr_title_is_not_a_ticket_binding(self):
        document = merged_pr("", title="Part of #290")

        self.assertEqual(receipt.plan_receipts(document), [])


class OnlyACompletedMainMergeCanProduceReceipts(unittest.TestCase):
    def test_an_open_pr_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not merged"):
            receipt.plan_receipts(merged_pr("Part of #290\n", mergedAt=None))

    def test_a_merge_to_another_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "base branch"):
            receipt.plan_receipts(
                merged_pr("Part of #290\n", baseRefName="release")
            )

    def test_a_missing_full_merge_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "full merge commit"):
            receipt.plan_receipts(
                merged_pr("Part of #290\n", mergeCommit={"oid": "0123456"})
            )

    def test_the_pr_url_must_name_the_same_pull_request(self):
        with self.assertRaisesRegex(ValueError, "pull request URL"):
            receipt.plan_receipts(
                merged_pr(
                    "Part of #290\n",
                    url="https://github.com/example/clinical-skills/pull/999",
                )
            )


class CommandLineOutputIsMachineReadable(unittest.TestCase):
    def test_one_authored_message_cannot_both_bind_and_declare_no_ticket(self):
        report = io.StringIO()
        document = merged_pr(
            "Part of #629\nBinds no ticket: this message contradicts itself.\n"
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 1)
        self.assertIn(
            "authored message body has a binding at body line 1 and a no-ticket "
            "declaration at body line 2",
            report.getvalue(),
        )

    def test_pr_628s_bound_pull_request_and_unbound_sync_commit_are_clean(self):
        report = io.StringIO()
        document = merged_pr(
            "> **Branch state:** `codex/518-reader-alias-lookup` at "
            "`3115ec5ed46bf41acc9159606ae73ec991bbaff5` is not on `main` as of "
            "`2026-08-29`.\n\n"
            "## Summary\n\n"
            "- read recommendation records from the sweep alias before the exact-name recs root\n"
            "- preserve explicit record precedence and report the selected origin per source\n"
            "- distinguish the four ruled alias absence states and document both reader paths\n\n"
            "## Verification\n\n"
            "- focused reader tests: 22 passed\n"
            "- full suite: 3,946 passed, 1 machine-local external-manifest trust refusal, 2 skipped\n"
            "- compile, PHI, spelling, scratch census, implementation-map, and freshness checks passed\n"
            "- independent Standards and Spec reviews passed\n\n"
            "Closes #518",
            commits=[
                {
                    "messageHeadline": "Read recommendation records from sweep alias",
                    "messageBody": "Closes #518",
                },
                {
                    "messageHeadline": (
                        "Merge origin/main into codex/518-reader-alias-lookup"
                    ),
                    "messageBody": (
                        "Binds no ticket: brings the implementation branch to the "
                        "current base."
                    ),
                },
            ],
            number=628,
            url="https://github.com/mshamblin5150-code/clinical-skills/pull/628",
            title="Read recommendation records from sweep alias",
            mergedAt="2026-08-29T09:02:59Z",
            mergeCommit={"oid": "b5ce2d015f70fe3afb9af540e7d3ecf7ae7a975b"},
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 0)
        self.assertIn(
            "commits[1].messageBody line 1: Binds no ticket "
            "(pull request also contains bindings): brings the implementation "
            "branch to the current base.",
            report.getvalue(),
        )
        self.assertNotIn("finding:", report.getvalue())

    def test_commit_headline_and_body_are_one_authored_message(self):
        report = io.StringIO()
        document = merged_pr(
            "",
            commits=[
                {
                    "messageHeadline": "Part of #629",
                    "messageBody": (
                        "Binds no ticket: the two fields still form one message."
                    ),
                }
            ],
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 1)
        self.assertIn(
            "authored message commits[0] has a binding at "
            "commits[0].messageHeadline line 1 and a no-ticket declaration at "
            "commits[0].messageBody line 1",
            report.getvalue(),
        )

    def test_a_standalone_declaration_names_the_no_bindings_case(self):
        report = io.StringIO()
        document = merged_pr("Binds no ticket: documentation-only housekeeping.\n")
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 0)
        self.assertIn(
            "Binds no ticket (pull request contains no bindings)",
            report.getvalue(),
        )

    def test_json_lines_mode_reads_standard_input(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch("sys.stdin", io.StringIO(json.dumps(merged_pr("Part of #290\n")))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 0)
        record = json.loads(output.getvalue())
        self.assertEqual(record["ticket"], 290)
        self.assertIn("PR #401", record["body"])

    def test_malformed_input_is_not_a_clean_empty_plan(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bad.json"
            path.write_text("[]", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                status = receipt.main([str(path)])

        self.assertEqual(status, 2)

    def test_an_empty_plan_is_a_reported_finding(self):
        report = io.StringIO()
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(merged_pr("No binding.\n")))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 1)
        self.assertIn("plan is empty", report.getvalue())

    def test_a_declined_line_is_named_without_destroying_valid_receipts(self):
        output = io.StringIO()
        report = io.StringIO()
        document = merged_pr("Part of #530\nPart of #531 once tests pass\n")
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())["ticket"], 530)
        self.assertIn("body line 2", report.getvalue())
        self.assertIn("Part of #531", report.getvalue())

    def test_pre_merge_entry_point_accepts_a_declared_no_ticket_reason(self):
        report = io.StringIO()
        document = merged_pr(
            "Binds no ticket: documentation-only housekeeping.\n",
            mergedAt=None,
            mergeCommit=None,
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["--check-plan", "-"])

        self.assertEqual(status, 0)
        self.assertIn("Binds no ticket", report.getvalue())
        self.assertIn("documentation-only housekeeping", report.getvalue())

    def test_pre_merge_entry_point_reports_an_open_prs_empty_plan(self):
        document = merged_pr("No binding.\n", mergedAt=None, mergeCommit=None)
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = receipt.main(["--check-plan", "-"])

        self.assertEqual(status, 1)

    def test_a_bare_no_ticket_marker_does_not_count(self):
        report = io.StringIO()
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(report),
            mock.patch("sys.stdin", io.StringIO(json.dumps(merged_pr("Binds no ticket:\n")))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 1)
        self.assertIn("Binds no ticket", report.getvalue())

class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    def test_the_ratified_population_is_present_in_both_directions(self):
        self.assertEqual(
            set(dict(receipt.NOT_REACHED)),
            {
                "a well-formed binding can name the wrong ticket",
                "the pre-merge check cannot watch a local merge",
                "a no-ticket declaration is graded for shape, not truth",
                "a receipt makes only its bounded relation current",
                "a declaration line is not the three-bucket measurement",
                "publication ordering is outside the message-scope change",
            },
        )


if __name__ == "__main__":
    unittest.main()
