"""Cover ``tracker_bodies``'s parser and rows against synthetic harvest files.

Every harvest here is written in this file and a temp directory, on
``test_tracker_scan``'s arrangement and for its reason: **the real tracker is
deliberately not a fixture.** It is fetched over the network and changes every
time anybody comments, so a test keyed on it would be measuring the day it ran.
No count of issues, pull requests or lost bodies is asserted anywhere here.

**One class reads a committed file** -- ``docs/agents/issue-tracker.md`` -- on
``test_spelling_scan``'s reasoning: a scanner that has drifted from the file a
reader opens is worse than none, because it reads as agreement.

**And one class is the ticket's own finding, pinned.** #130's reproduce command
is ``gh issue list``, which excludes pull requests, so two members of its own
population were invisible to every sweep that ran it. ``PullRequestsAreRead``
is why this module parses the ``issues`` REST payload instead.
"""

from __future__ import annotations

import ast
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import tracker_bodies as tb

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_DOC = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"
MODULE = Path(tb.__file__)

# A string that appears in no legitimate report, driven through every aperture a
# body has onto the output. ``reference_scan``'s salted draft, at one field.
MARKER = "ZZMARKERZZ"


def issue(number: int, body, pull: bool = False) -> dict:
    """One record in the shape ``gh api repos/O/R/issues`` returns.

    ``body`` is passed through untouched, including ``None``, because a body
    GitHub stores as JSON null is one of the shapes the empty row exists for.
    """
    item = {
        "number": number,
        "title": f"a title for {number}",
        "body": body,
        "html_url": f"https://github.com/O/R/issues/{number}",
    }
    if pull:
        item["pull_request"] = {"url": f"https://api.github.com/repos/O/R/pulls/{number}"}
    return item


def comment(ident: int, body) -> dict:
    return {
        "id": ident,
        "body": body,
        "html_url": f"https://github.com/O/R/issues/1#issuecomment-{ident}",
    }


def harvest(*items: dict) -> list[dict]:
    return list(items)


def kinds_of(records) -> list[str]:
    return [finding.kind for finding in tb.grade(records)]


def read(data, source: str = "t.json"):
    return tb.records_from_github(data, source)


class TheDocumentedTrap(unittest.TestCase):
    """``@-`` is the shape eight bodies in this repo were actually lost as."""

    def test_a_body_of_at_dash_is_a_lost_body(self):
        records = read(harvest(issue(6, "@-")))
        self.assertEqual(kinds_of(records), [tb.LOST_AT_DASH])

    def test_surrounding_whitespace_does_not_hide_it(self):
        records = read(harvest(issue(6, "  @-\n")))
        self.assertEqual(kinds_of(records), [tb.LOST_AT_DASH])

    def test_a_real_body_that_merely_contains_the_characters_is_clean(self):
        body = "Never write `--body @-`; it sets the body to two characters."
        self.assertEqual(kinds_of(read(harvest(issue(6, body)))), [])

    def test_at_dash_is_graded_once_and_not_also_as_a_literal_path(self):
        records = read(harvest(issue(6, "@-")))
        self.assertEqual(len(tb.grade(records)), 1)


class TheEmptyRow(unittest.TestCase):
    """Ruled 2026-08-19: an empty body is a failure here, not a legitimate shape.

    Four ways a body arrives with nothing in it, and they are one row because the
    repair is the same for all four. Which *call* produced it is not knowable from
    the payload, so the row names the state and never guesses the cause.
    """

    def test_json_null_is_empty(self):
        self.assertEqual(kinds_of(read(harvest(issue(6, None)))), [tb.EMPTY_BODY])

    def test_the_key_absent_altogether_is_empty(self):
        item = issue(6, "x")
        del item["body"]
        self.assertEqual(kinds_of(read(harvest(item))), [tb.EMPTY_BODY])

    def test_the_empty_string_is_empty(self):
        self.assertEqual(kinds_of(read(harvest(issue(6, "")))), [tb.EMPTY_BODY])

    def test_whitespace_only_is_empty(self):
        self.assertEqual(kinds_of(read(harvest(issue(6, " \n\t ")))), [tb.EMPTY_BODY])


class TheLiteralPathRow(unittest.TestCase):
    """The sibling of ``@-`` that ``issue-tracker.md`` names beside it.

    ``-F body=@file`` belongs to ``gh api``; typed at ``--body`` it writes the
    filename. **Zero instances in the tracker on 2026-08-19**, so the row is
    grounded in the documented trap rather than in a measurement -- which is why
    it is deliberately the narrowest of the three.
    """

    def test_a_lone_at_path_is_a_literal_path(self):
        records = read(harvest(issue(6, "@body.md")))
        self.assertEqual(kinds_of(records), [tb.LITERAL_AT_PATH])

    def test_an_at_mention_with_anything_after_it_is_clean(self):
        """The narrowing, stated as a test so widening the row fails here first.

        ``@someone please look`` is an ordinary body. Nothing distinguishes a
        one-word at-mention from a swallowed filename, so the rule requires the
        whole body to be one token and accepts that a bare ``@someone`` fires.
        """
        self.assertEqual(kinds_of(read(harvest(issue(6, "@someone please look")))), [])

    def test_a_body_merely_starting_with_at_is_clean(self):
        body = "@- is what a collapsed heredoc leaves behind."
        self.assertEqual(kinds_of(read(harvest(issue(6, body)))), [])


class ACleanHarvest(unittest.TestCase):
    def test_ordinary_bodies_produce_nothing(self):
        records = read(harvest(issue(6, "A real body.\n\nWith paragraphs."),
                               comment(1, "A real comment.")))
        self.assertEqual(tb.grade(records), [])

    def test_every_record_is_read_whatever_its_body(self):
        records = read(harvest(issue(6, "ok"), issue(7, "@-"), comment(1, None)))
        self.assertEqual(len(records), 3)


class PullRequestsAreRead(unittest.TestCase):
    """#130's own finding, pinned.

    Its reproduce command is ``gh issue list``, which excludes pull requests.
    Two of the eight lost bodies are pull requests, so every sweep that ran the
    command re-derived *six, not eight* and concluded the title was stale. The
    title was right and the instrument could not see two of its members.
    """

    def test_a_pull_request_with_a_lost_body_is_a_finding(self):
        records = read(harvest(issue(71, "@-", pull=True)))
        self.assertEqual(kinds_of(records), [tb.LOST_AT_DASH])

    def test_the_report_says_which_surface_a_record_came_from(self):
        records = read(harvest(issue(71, "@-", pull=True), issue(6, "@-")))
        self.assertEqual({r.record_kind for r in records}, {tb.PULL, tb.ISSUE})

    def test_a_comment_is_its_own_surface(self):
        records = read(harvest(comment(1, "@-")))
        self.assertEqual(records[0].record_kind, tb.COMMENT)


class WhatAHarvestMayBe(unittest.TestCase):
    def test_a_single_object_is_one_record_so_a_read_back_works(self):
        """``gh issue view N --json number,body`` emits an object, not a list.

        Accepted on purpose: it makes this module the read-back step
        ``issue-tracker.md`` already asks for, rather than only a sweep tool.
        This is where it departs from ``tracker_scan.records_from_github``,
        which refuses anything but a list.
        """
        records = read({"number": 6, "body": "@-"})
        self.assertEqual(kinds_of(records), [tb.LOST_AT_DASH])

    def test_a_scalar_is_not_a_harvest(self):
        with self.assertRaises(tb.HarvestError):
            read(7)

    def test_a_non_record_inside_a_list_is_skipped_rather_than_fatal(self):
        records = read(harvest(issue(6, "@-")) + ["not a record"])
        self.assertEqual(len(records), 1)

    def test_a_record_with_no_number_or_id_still_gets_a_label(self):
        records = read([{"body": "@-"}], source="t130-issues.json")
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].label)


class TheSiblingsParserCannotBeReused(unittest.TestCase):
    """Why this module has its own reader, asserted rather than claimed.

    ``tracker_scan.records_from_github`` drops a body that is empty or whitespace
    -- correct for a PHI scan, since there is no text to find -- and that is
    exactly the record this module exists to report.
    """

    def test_the_sibling_drops_the_record_this_module_reports(self):
        import tracker_scan

        payload = [{"number": 6, "title": "t", "body": "   "}]
        sibling = [r for r in tracker_scan.records_from_github(payload, "t")
                   if r.kind == "body"]
        self.assertEqual(sibling, [])
        self.assertEqual(kinds_of(read(payload)), [tb.EMPTY_BODY])


class TheReportCarriesNoBodyText(unittest.TestCase):
    """The property the *no ``--show``* claim rests on, driven rather than argued.

    Every row fires on a body drawn from a fixed set bar one, and that one --
    the literal path -- is the reason this is a test and not a paragraph: it is
    the only row whose trigger is run-authored text.
    """

    def test_a_marker_in_a_body_never_reaches_the_report(self):
        records = read(harvest(
            issue(6, f"@{MARKER}.md"),
            issue(7, "@-"),
            issue(8, ""),
            comment(1, f"@{MARKER}.md"),
        ))
        report = tb.format_report(tb.survey(records), source="t.json")
        self.assertNotIn(MARKER, report)

    def test_a_marker_in_a_title_never_reaches_the_report(self):
        item = issue(6, "@-")
        item["title"] = MARKER
        report = tb.format_report(tb.survey(read(harvest(item))), source="t.json")
        self.assertNotIn(MARKER, report)

    def test_the_report_takes_no_parameter_that_could_widen_it(self):
        """Structural, not a substring search over the source.

        The first version of this test asserted ``--show`` appears nowhere in
        the module and failed on the docstring paragraph explaining why there is
        no ``--show`` -- ``spelling_scan``'s mention-versus-use problem arriving
        on a test rather than on prose. A signature cannot be satisfied by
        describing itself.
        """
        import inspect

        self.assertEqual(
            list(inspect.signature(tb.format_report).parameters),
            ["scan", "source"],
        )


class TheRowsAreOneTuple(unittest.TestCase):
    def test_every_kind_has_a_ticket(self):
        self.assertEqual(set(tb.KINDS), set(tb.ROW_TICKET))

    def test_kinds_are_distinct(self):
        self.assertEqual(len(tb.KINDS), len(set(tb.KINDS)))

    def test_every_finding_the_module_builds_is_a_declared_kind(self):
        """An AST walk, on ``test_console_codec``'s instrument and for its reason.

        A fourth row that was written but never declared would leave every
        assertion above green while the report counted it nowhere.
        """
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        declared = {node.targets[0].id: node.value.value
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)}
        built = set()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Finding"):
                continue
            first = node.args[0] if node.args else next(
                (kw.value for kw in node.keywords if kw.arg == "kind"), None)
            if isinstance(first, ast.Name):
                built.add(declared.get(first.id))
            elif isinstance(first, ast.Constant):
                built.add(first.value)
        self.assertTrue(built, "no Finding(...) call found -- the walk is dead")
        self.assertLessEqual(built, set(tb.KINDS))

    def test_the_counts_line_up_with_the_kinds(self):
        records = read(harvest(issue(6, "@-"), issue(7, ""), issue(8, "@f.md")))
        scan = tb.survey(records)
        self.assertEqual([kind for kind, _ in scan.counts], list(tb.KINDS))
        self.assertEqual(sum(count for _, count in scan.counts), 3)


class TheCommandLine(unittest.TestCase):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = tb.main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def write(self, directory: Path, name: str, data) -> Path:
        path = directory / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_no_argument_did_not_scan(self):
        self.assertEqual(self.run_main()[0], tb.NOT_SCANNED)

    def test_a_file_that_is_not_there_did_not_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.json"
            self.assertEqual(self.run_main(str(missing))[0], tb.NOT_SCANNED)

    def test_a_file_that_is_not_json_did_not_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(self.run_main(str(path))[0], tb.NOT_SCANNED)

    def test_a_harvest_with_no_record_did_not_scan(self):
        """The limb that matters.

        An empty payload would otherwise report zero lost bodies and read
        exactly like a tracker that has none.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", [])
            status, _, err = self.run_main(str(path))
            self.assertEqual(status, tb.NOT_SCANNED)
            self.assertIn("no record", err)

    def test_a_clean_harvest_is_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "A real body.")))
            self.assertEqual(self.run_main(str(path))[0], tb.CLEAN)

    def test_a_lost_body_is_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "@-")))
            status, out, err = self.run_main(str(path))
            self.assertEqual(status, tb.FOUND)
            self.assertIn("6", out + err)

    def test_several_harvest_files_are_read_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.write(Path(tmp), "a.json", harvest(issue(6, "@-")))
            b = self.write(Path(tmp), "b.json", harvest(comment(1, "ok")))
            status, out, _ = self.run_main(str(a), str(b))
            self.assertEqual(status, tb.FOUND)
            self.assertIn("2", out)

    def test_one_unreadable_file_among_several_did_not_scan(self):
        """A partial read is not a clean read, which is this directory's rule."""
        with tempfile.TemporaryDirectory() as tmp:
            good = self.write(Path(tmp), "a.json", harvest(issue(6, "@-")))
            status, _, _ = self.run_main(str(good), str(Path(tmp) / "gone.json"))
            self.assertEqual(status, tb.NOT_SCANNED)

    def test_the_report_names_the_record_a_reader_has_to_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "@-")))
            _, out, _ = self.run_main(str(path))
            self.assertIn("https://github.com/O/R/issues/6", out)


class TheDocSaysWhatThisChecks(unittest.TestCase):
    """``test_spelling_scan``'s reasoning.

    The file a reader opens and the scanner must not hold different answers,
    because agreement is what a reader assumes.
    """

    def setUp(self):
        self.doc = TRACKER_DOC.read_text(encoding="utf-8")

    def test_the_doc_names_the_command(self):
        self.assertIn("tools/tracker_bodies.py", self.doc)

    def test_the_doc_says_a_clean_scan_is_not_a_read_ticket(self):
        self.assertIn("A clean scan is not a body worth reading", self.doc)

    def test_the_doc_records_that_gh_issue_list_hides_pull_requests(self):
        self.assertIn("`gh issue list` excludes pull requests", self.doc)


if __name__ == "__main__":
    unittest.main()
