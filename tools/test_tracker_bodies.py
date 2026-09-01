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
import subprocess
import sys
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


class TheDoubleEncodedRow(unittest.TestCase):
    """#155's first mechanism: UTF-8 bytes decoded through cp1252."""

    def test_cp1252_mojibake_is_double_encoded(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        records = read(harvest(issue(97, f"before {mojibake_em_dash} after")))
        self.assertEqual(kinds_of(records), [tb.DOUBLE_ENCODED])

    def test_literal_unicode_escape_is_double_encoded(self):
        records = read(harvest(issue(215, r"before \u2014 after")))
        self.assertEqual(kinds_of(records), [tb.DOUBLE_ENCODED])

    def test_a_shape_named_in_backticks_is_clean(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        body = f"Search for `{mojibake_em_dash}` and `\\u2014`."
        self.assertEqual(kinds_of(read(harvest(issue(172, body)))), [])

    def test_shapes_named_in_a_fenced_example_are_clean(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        body = f"Example:\n```text\n{mojibake_em_dash}\n\\u2014\n```"
        self.assertEqual(kinds_of(read(harvest(comment(1, body)))), [])

    def test_several_damaged_sequences_are_one_failed_record(self):
        records = read(harvest(issue(215, r"\u2014 one \u2014 two \u2014")))
        self.assertEqual(len(tb.grade(records)), 1)

    def test_cp1252_threshold_and_pound_shapes_are_caught(self):
        mojibake_greater_or_equal = "\u00e2\u2030\u00a5"
        mojibake_pound = "\u00c2\u00a3"
        for number, shape in ((97, mojibake_greater_or_equal),
                              (190, mojibake_pound)):
            with self.subTest(number=number):
                self.assertEqual(
                    kinds_of(read(harvest(issue(number, f"before {shape} after")))),
                    [tb.DOUBLE_ENCODED],
                )


class TheC0ControlCharacterRow(unittest.TestCase):
    """#723 grades the raw body, including code spans and body edges."""

    def test_every_c0_control_except_tab_line_feed_and_carriage_return_fails(self):
        excluded = {"\t", "\n", "\r"}
        for point in range(0x20):
            character = chr(point)
            if character in excluded:
                continue
            with self.subTest(code_point=f"U+{point:04X}"):
                records = read(harvest(issue(723, f"before{character}after")))
                self.assertEqual(kinds_of(records), [tb.C0_CONTROL_CHARACTER])

    def test_a_control_character_inside_a_code_span_fails(self):
        records = read(harvest(issue(723, "copy `word\bword` exactly")))

        self.assertEqual(kinds_of(records), [tb.C0_CONTROL_CHARACTER])

    def test_python_whitespace_at_the_raw_body_edge_is_not_stripped(self):
        records = read(harvest(issue(723, "ordinary body\v")))

        self.assertEqual(kinds_of(records), [tb.C0_CONTROL_CHARACTER])

    def test_tab_line_feed_and_carriage_return_remain_clean(self):
        records = read(harvest(issue(723, "tab\tline\ncarriage\rreturn")))

        self.assertEqual(kinds_of(records), [])

    def test_del_and_replacement_character_remain_outside_the_row(self):
        records = read(harvest(issue(723, "DEL\x7f replacement\ufffd")))

        self.assertEqual(kinds_of(records), [])


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
        self.assertEqual({r.surface for r in records}, {tb.PULL, tb.ISSUE})

    def test_a_comment_is_its_own_surface(self):
        records = read(harvest(comment(1, "@-")))
        self.assertEqual(records[0].surface, tb.COMMENT)


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

    The encoding row reads arbitrary prose, so the report's safety rests on the
    body never reaching it rather than on every trigger coming from a fixed set.
    """

    def test_a_marker_in_a_body_never_reaches_the_report(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        records = read(harvest(
            issue(6, f"@{MARKER}.md"),
            issue(7, "@-"),
            issue(8, ""),
            issue(9, f"{MARKER} {mojibake_em_dash}"),
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

    def rows_the_module_builds(self) -> set:
        """Every row a ``Finding(...)`` call in the module actually constructs.

        An AST walk, on ``test_console_codec``'s instrument and for its reason: a
        substring search over the source is satisfied by the docstring that
        *describes* the row. The call is matched by the name at the end of the
        dotted path, so a qualified ``tb.Finding(...)`` is read as one too.
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
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name != "Finding":
                continue
            first = node.args[0] if node.args else next(
                (kw.value for kw in node.keywords if kw.arg == "kind"), None)
            if isinstance(first, ast.Name):
                built.add(declared.get(first.id))
            elif isinstance(first, ast.Constant):
                built.add(first.value)
        return built

    def test_every_finding_the_module_builds_is_a_declared_kind(self):
        """A row written but never declared would be counted nowhere."""
        built = self.rows_the_module_builds()
        self.assertTrue(built, "no Finding(...) call found -- the walk is dead")
        self.assertLessEqual(built, set(tb.KINDS))

    def test_every_declared_kind_is_a_row_the_module_builds(self):
        """The other direction, which the first version of this class lacked.

        A row declared in ``KINDS`` that nothing constructs prints a permanent
        zero and reads as a rule being enforced. ``reference_scan``'s standard is
        that both directions are asserted, and only one of them was.
        """
        self.assertEqual(self.rows_the_module_builds(), set(tb.KINDS))

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

    def test_a_harvest_that_is_not_utf8_did_not_scan(self):
        """#150's defect, which this module had.

        ``UnicodeDecodeError`` is a ``ValueError`` and not an ``OSError``, so a
        bare ``read_text`` let it escape ``main`` -- and the traceback exits
        **1**, which this module's contract reads as *a lost body found*. The
        documented harvest is a shell redirection, which is exactly where a
        UTF-16 payload comes from.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.json"
            payload = json.dumps(harvest(issue(6, "@-")))
            path.write_bytes(b"\xff\xfe" + payload.encode("utf-16-le"))
            self.assertEqual(self.run_main(str(path))[0], tb.NOT_SCANNED)

    def test_an_unknown_flag_did_not_scan(self):
        """A flag this module does not have must not be swallowed.

        The first version filtered every ``--`` argument out of the path list,
        so ``--show`` was accepted and ignored -- the ordinary report, the
        ordinary status, and a caller believing it had asked for something. A
        silent no-op is the one behavior worse than an error here, since the
        module's own claim is that no such flag exists.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "@-")))
            status, _, err = self.run_main("--show", str(path))
            self.assertEqual(status, tb.NOT_SCANNED)
            self.assertIn("--show", err)

    def test_an_unreadable_file_names_it_without_its_path(self):
        """A harvest sits under ``scratch/``, so the report names the file only.

        ``str(OSError)`` carries the full path, which is what the first version
        printed beside a comment promising it did not.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.json"
            path.write_bytes(b"\x00\x01\x02")
            good = self.write(Path(tmp), "g.json", harvest(issue(6, "@-")))
            _, _, err = self.run_main(str(good), str(path))
            self.assertIn("t.json", err)
            self.assertNotIn(tmp, err)

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

    def test_dash_reads_one_payload_from_standard_input(self):
        """The read-back, driven rather than documented.

        ``issue-tracker.md`` first spelled this ``/dev/stdin``, which is not a
        file on the platform every commit here is made from -- the module
        answered *no harvest file named dev/stdin* and exited 2, so a documented
        command could not run and read as a checked one. Caught by review.
        """
        payload = io.StringIO(json.dumps({"number": 6, "body": "@-",
                                          "url": "https://github.com/O/R/issues/6"}))
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = tb.main(["-"], stdin=payload)
        self.assertEqual(status, tb.FOUND)
        self.assertIn("https://github.com/O/R/issues/6", out.getvalue())

    def test_a_clean_record_on_standard_input_is_zero(self):
        payload = io.StringIO(json.dumps({"number": 6, "body": "A real body."}))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(tb.main(["-"], stdin=payload), tb.CLEAN)

    def test_a_github_comment_event_is_a_first_class_surface(self):
        event = {
            "action": "created",
            "comment": {
                "id": 7,
                "html_url": "https://github.com/O/R/issues/723#issuecomment-7",
                "body": "damaged\bbody",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "event.json", event)
            status, out, _ = self.run_main(
                "--github-event", str(path), "--event-name", "issue_comment"
            )

        self.assertEqual(status, tb.FOUND)
        self.assertIn(tb.C0_CONTROL_CHARACTER, out)

    def test_an_edited_event_grades_only_a_changed_body(self):
        event = {
            "action": "edited",
            "changes": {"body": {"from": "old body"}},
            "issue": {
                "number": 723,
                "title": "unchanged\btitle",
                "body": "clean body",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "event.json", event)
            status, _, _ = self.run_main(
                "--github-event", str(path), "--event-name", "issues"
            )

        self.assertEqual(status, tb.CLEAN)

    def test_each_workflow_event_selects_its_body_record(self):
        cases = (
            ("issues", "issue", {"number": 723}),
            ("issue_comment", "comment", {"id": 1}),
            ("pull_request_target", "pull_request", {"number": 12}),
            ("pull_request_review", "review", {"id": 2}),
            ("pull_request_review_comment", "comment", {"id": 3}),
        )

        for event_name, key, identity in cases:
            with self.subTest(event_name=event_name):
                item = {**identity, "body": "damaged\bbody"}
                records = tb.records_from_github_event(
                    {"action": "created", key: item}, event_name, "event.json"
                )
                self.assertEqual(kinds_of(records), [tb.C0_CONTROL_CHARACTER])

    def test_clearing_an_event_body_is_an_empty_body_finding(self):
        records = tb.records_from_github_event(
            {
                "action": "edited",
                "changes": {"body": {"from": "old body"}},
                "issue": {"number": 723, "body": None},
            },
            "issues",
            "event.json",
        )

        self.assertEqual(kinds_of(records), [tb.EMPTY_BODY])

    def test_github_event_and_event_name_are_required_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                Path(tmp),
                "event.json",
                {"action": "created", "comment": {"id": 7, "body": "clean"}},
            )
            event_only = self.run_main("--github-event", str(path))[0]
            name_only = self.run_main("--event-name", "issue_comment")[0]

        self.assertEqual(event_only, tb.NOT_SCANNED)
        self.assertEqual(name_only, tb.NOT_SCANNED)

    def test_clean_utf8_bytes_have_the_same_verdict_through_file_and_pipe(self):
        """#389's real boundary: a pipe, not a codec-free ``StringIO``."""
        payload = json.dumps(
            {"number": 389, "body": "Section § — ‘clean’."},
            ensure_ascii=False,
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clean.json"
            path.write_bytes(payload)
            through_file = subprocess.run(
                [sys.executable, str(MODULE), str(path)],
                capture_output=True,
            )
            through_pipe = subprocess.run(
                [sys.executable, str(MODULE), "-"],
                input=payload,
                capture_output=True,
            )
        self.assertEqual(through_file.returncode, tb.CLEAN)
        self.assertEqual(through_pipe.returncode, through_file.returncode)

    def test_double_encoded_utf8_bytes_fail_through_file_and_pipe(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        payload = json.dumps(
            {"number": 389, "body": f"before {mojibake_em_dash} after"},
            ensure_ascii=False,
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "double-encoded.json"
            path.write_bytes(payload)
            through_file = subprocess.run(
                [sys.executable, str(MODULE), str(path)],
                capture_output=True,
            )
            through_pipe = subprocess.run(
                [sys.executable, str(MODULE), "-"],
                input=payload,
                capture_output=True,
            )
        self.assertEqual(through_file.returncode, tb.FOUND)
        self.assertEqual(through_pipe.returncode, through_file.returncode)

    def test_standard_input_that_is_not_json_did_not_scan(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            status = tb.main(["-"], stdin=io.StringIO("not json"))
        self.assertEqual(status, tb.NOT_SCANNED)

    def test_dash_takes_no_other_argument(self):
        """Rather than silently reading one and ignoring the other."""
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "@-")))
            status, _, _ = self.run_main("-", str(path))
            self.assertEqual(status, tb.NOT_SCANNED)

    def test_the_report_names_the_record_a_reader_has_to_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), "t.json", harvest(issue(6, "@-")))
            _, out, _ = self.run_main(str(path))
            self.assertIn("https://github.com/O/R/issues/6", out)

    def test_a_comment_finding_does_not_offer_the_issue_edit_command(self):
        mojibake_em_dash = "\u00e2\u20ac\u201d"
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                Path(tmp), "t.json", harvest(comment(1, mojibake_em_dash))
            )
            _, _, err = self.run_main(str(path))
            self.assertNotIn("gh issue edit", err)
            self.assertIn("matching GitHub edit path", err)


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

    def test_the_doc_names_the_encoding_row_and_both_mechanisms(self):
        self.assertIn("fourth row", self.doc)
        self.assertIn("cp1252", self.doc)
        self.assertIn(r"`\uXXXX`", self.doc)

    def test_the_doc_names_the_raw_c0_row(self):
        self.assertIn("fifth row", self.doc)
        self.assertIn("raw body", self.doc)

    def test_the_doc_names_both_publication_hosts(self):
        self.assertIn("tracker_publish_hook.py", self.doc)
        self.assertIn("tracker_bodies.py --github-event", self.doc)
        self.assertNotIn("Nothing runs any of this", self.doc)


class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    def test_the_ruled_exclusions_and_wider_class_are_declared(self):
        limits = dict(tb.NOT_REACHED)

        self.assertIn("other escape-collapse damage without a C0 control character", limits)
        self.assertIn("DEL U+007F", limits)
        self.assertIn("replacement character U+FFFD", limits)

    def test_the_module_points_at_the_object_without_copying_it(self):
        module_doc = tb.__doc__ or ""

        self.assertIn("NOT_REACHED", module_doc)
        for key, reason in tb.NOT_REACHED:
            self.assertNotIn(key, module_doc)
            self.assertNotIn(reason, module_doc)
            self.assertGreater(len(reason.split()), 8)


if __name__ == "__main__":
    unittest.main()
