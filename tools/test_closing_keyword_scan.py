"""GitHub closing-keyword hazards are found on every surface. Issue #183."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import closing_keyword_scan as scan


REPO_ROOT = Path(__file__).resolve().parent.parent


class GitHubClosingGrammar(unittest.TestCase):
    def findings(self, text):
        return scan.scan_text(text, "artifact")

    def test_a_closing_keyword_inside_prose_is_a_finding(self):
        findings = self.findings("Filed rather than fixed: #180, which stays open.\n")
        self.assertEqual([(row.ticket, row.line) for row in findings], [(180, 1)])

    def test_probe_2_intervening_prose_breaks_the_closing_grammar(self):
        text = "The stale citation was resolved in #172.\n"
        self.assertEqual(self.findings(text), [])

    def test_probe_2_a_later_ticket_in_the_clause_is_not_a_hazard(self):
        text = "This fixes the citations #143 warned about.\n"
        self.assertEqual(self.findings(text), [])

    def test_a_finished_sentence_stops_the_keyword(self):
        text = "A fix is planned. See #183 for the decision.\n"
        self.assertEqual(self.findings(text), [])

    def test_the_explanation_of_an_absent_keyword_is_still_a_finding(self):
        findings = self.findings(
            'A subject reading `Fix #215` would take the decision away.\n'
        )
        self.assertEqual([row.ticket for row in findings], [215])

    def test_a_possessive_partial_close_is_a_finding(self):
        findings = self.findings("Closes #178's lead 1.\n")
        self.assertEqual([row.ticket for row in findings], [178])

    def test_probe_5_a_markdown_list_marker_breaks_the_closing_grammar(self):
        findings = self.findings("The defects are fixed:\n\n- #180 remains open.\n")
        self.assertEqual(findings, [])

    def test_probe_3_a_bare_line_wrap_preserves_a_closing_hazard(self):
        findings = self.findings("The defects are fixed\n#180 remains open.\n")
        self.assertEqual([row.ticket for row in findings], [180])

    def test_colon_and_whitespace_preserve_a_measured_closing_hazard(self):
        findings = self.findings("The defects are fixed:\n\n#180 remains open.\n")
        self.assertEqual([row.ticket for row in findings], [180])

    def test_wrapping_the_reference_breaks_the_closing_grammar(self):
        for text in ("fix (#180)\n", "fix **#180**\n", "fix:\n\n> #180\n"):
            with self.subTest(text=text):
                self.assertEqual(self.findings(text), [])

    def test_keywords_are_whole_words_and_the_matcher_stays_live(self):
        cases = (
            ("fixtures", "fix"),
            ("fixture-", "fix"),
            ("closest", "closes"),
            ("closed-loop", "closed"),
            ("resolver", "resolve"),
            ("resolvers", "resolve"),
        )
        for written, keyword in cases:
            with self.subTest(written=written):
                self.assertEqual(self.findings(f"{written} #123\n"), [])
                findings = self.findings(f"{keyword} #123\n")
                self.assertEqual([row.ticket for row in findings], [123])

    def test_leading_word_boundary_still_rejects_prefix_and_affix(self):
        for written in ("prefix", "affix"):
            with self.subTest(written=written):
                self.assertEqual(self.findings(f"{written} #123\n"), [])

    def test_the_standalone_deliberate_form_is_allowed(self):
        self.assertEqual(self.findings("Closes #183\n"), [])

    def test_the_standalone_deliberate_form_is_allowed_with_crlf(self):
        self.assertEqual(self.findings("Closes #183\r\n"), [])

    def test_the_standalone_form_inside_a_code_fence_is_not_inert(self):
        findings = self.findings("The unsafe form is:\n```\nCloses #183\n```\n")
        self.assertEqual([row.ticket for row in findings], [183])

    def test_non_closing_references_are_allowed(self):
        self.assertEqual(
            self.findings("Implements #178's lead 1. See #183 for the rest.\n"),
            [],
        )

    def test_declared_limits_name_the_measured_grammar_and_its_margins(self):
        keys = [row.key for row in scan.DECLARED_LIMITS]
        self.assertEqual(
            keys,
            [
                "measured-closing-grammar",
                "colon-whitespace-margin",
                "fences-uniform-margin",
                "non-surfaces-ungraded",
                "github-parser-unversioned",
            ],
        )
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(row.limit.strip() for row in scan.DECLARED_LIMITS))
        self.assertTrue(all(row.evidence for row in scan.DECLARED_LIMITS))
        self.assertEqual(
            scan.NOT_REACHED,
            tuple(row.limit for row in scan.DECLARED_LIMITS),
        )

    def test_every_behavior_limit_is_bound_to_live_scanner_controls(self):
        controls = {
            "measured-closing-grammar": (
                ("fixtures #123\n", []),
                ("fix #123\n", [123]),
            ),
        }
        behavior_keys = {
            row.key
            for row in scan.DECLARED_LIMITS
            if row.evidence is scan.EvidenceDisposition.BEHAVIOR
        }
        self.assertEqual(set(controls), behavior_keys)
        for key, (
            (clean_text, clean_tickets),
            (hazard_text, hazard_tickets),
        ) in controls.items():
            with self.subTest(key=key, control="negative"):
                self.assertEqual(
                    [row.ticket for row in self.findings(clean_text)], clean_tickets
                )
            with self.subTest(key=key, control="positive"):
                self.assertEqual(
                    [row.ticket for row in self.findings(hazard_text)], hazard_tickets
                )


class GitHubPullRequestInput(unittest.TestCase):
    def test_title_body_and_commit_messages_are_all_scanned(self):
        document = {
            "title": "Implement part of #183",
            "body": "This would have closed #215 on merge.",
            "commits": [
                {
                    "messageHeadline": "Keep #183 open",
                    "messageBody": "Does not fix #94.",
                }
            ],
        }
        rows = scan.scan_github_document(document)
        self.assertEqual(
            [(row.source, row.ticket) for row in rows],
            [("body", 215), ("commits[0]", 94)],
        )

    def test_a_commit_headline_and_body_are_one_artifact(self):
        document = {
            "title": "",
            "body": "",
            "commits": [
                {"messageHeadline": "Defects fixed:", "messageBody": "#180 stays open"}
            ],
        }
        rows = scan.scan_github_document(document)
        self.assertEqual([(row.source, row.ticket) for row in rows], [("commits[0]", 180)])

    def test_github_json_mode_reads_stdin(self):
        document = {"title": "Fix: #94", "body": ""}
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch("sys.stdin", io.StringIO(json.dumps(document))),
        ):
            status = scan.main(["--github-json", "-"])
        self.assertEqual(status, 1)
        self.assertIn("title:1", output.getvalue())
        self.assertIn("#94", output.getvalue())
        self.assertIn("would close", output.getvalue())


class CommitMessageHook(unittest.TestCase):
    def test_the_hook_warns_and_keeps_the_advisory_exit_status(self):
        with tempfile.TemporaryDirectory() as raw:
            message = Path(raw) / "COMMIT_EDITMSG"
            message.write_text("This does not fix #135.\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "sh",
                    (REPO_ROOT / "tools" / "hooks" / "commit-msg").as_posix(),
                    message.as_posix(),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("closing-keyword-scan", result.stderr)
        self.assertIn("#135", result.stderr)


if __name__ == "__main__":
    unittest.main()
