"""Synthetic event controls for choosing full code validation."""

import copy
import contextlib
import io
import json
import unittest
from unittest.mock import patch

import ci_event_scope


def text_edit(field="title"):
    return {
        "action": "edited",
        "changes": {field: {"from": "old text"}},
        "pull_request": {
            "title": "current title", "body": "current body",
            "head": {"ref": "topic", "sha": "a" * 40},
            "base": {"ref": "main", "sha": "b" * 40},
        },
    }


class EventScope(unittest.TestCase):
    def test_confirmed_title_body_and_combined_text_edits_skip_code(self):
        for fields in (("title",), ("body",), ("title", "body")):
            with self.subTest(fields=fields):
                event = text_edit()
                event["changes"] = {field: {"from": "old"} for field in fields}
                self.assertFalse(ci_event_scope.requires_code("pull_request", event))

    def test_all_code_event_types_keep_full_validation(self):
        for action in ("opened", "synchronize", "reopened", "unknown", None):
            with self.subTest(action=action):
                event = text_edit()
                event["action"] = action
                self.assertTrue(ci_event_scope.requires_code("pull_request", event))
        for name in ("push", "workflow_dispatch", "pull_request_target", "unknown"):
            with self.subTest(event_name=name):
                self.assertTrue(ci_event_scope.requires_code(name, text_edit()))

    def test_base_ref_sha_head_and_unknown_changes_keep_full_validation(self):
        for field, value in (
            ("base", {"ref": {"from": "release"}}),
            ("base", {"sha": {"from": "c" * 40}}),
            ("head", {"sha": {"from": "c" * 40}}),
            ("unknown", {"from": "anything"}),
        ):
            for mixed in (False, True):
                with self.subTest(field=field, value=value, mixed=mixed):
                    event = text_edit()
                    event["changes"] = {field: value}
                    if mixed:
                        event["changes"]["body"] = {"from": "old"}
                    self.assertTrue(ci_event_scope.requires_code("pull_request", event))

    def test_missing_and_malformed_payloads_keep_full_validation(self):
        for event in (None, [], "edited", {}, {"action": "edited"}):
            with self.subTest(event=event):
                self.assertTrue(ci_event_scope.requires_code("pull_request", event))
        for changes in (None, [], {}, {"title": None}, {"title": {}},
                        {"title": {"from": 1}}, {"title": {"from": "old", "extra": 1}}):
            with self.subTest(changes=changes):
                event = text_edit()
                event["changes"] = changes
                self.assertTrue(ci_event_scope.requires_code("pull_request", event))

    def test_unreadable_or_incomplete_pr_identity_keeps_full_validation(self):
        for section in ("head", "base"):
            for field, value in (("sha", None), ("sha", "not-a-sha"),
                                 ("ref", ""), ("ref", None)):
                with self.subTest(section=section, field=field, value=value):
                    event = text_edit()
                    event["pull_request"][section][field] = value
                    self.assertTrue(ci_event_scope.requires_code("pull_request", event))
        for pr in (None, {}, [], {"title": "text"}):
            event = text_edit()
            event["pull_request"] = pr
            self.assertTrue(ci_event_scope.requires_code("pull_request", event))

    def test_nullable_body_is_a_valid_text_edit(self):
        event = text_edit("body")
        event["changes"]["body"]["from"] = None
        event["pull_request"]["body"] = None
        self.assertFalse(ci_event_scope.requires_code("pull_request", event))

    def test_classification_does_not_mutate_the_event(self):
        event = text_edit()
        before = copy.deepcopy(event)
        ci_event_scope.requires_code("pull_request", event)
        self.assertEqual(before, event)


    def test_cli_prints_only_the_fixed_scope_output(self):
        for event, expected in ((text_edit(), "false\n"), ({}, "true\n")):
            output = io.StringIO()
            with patch.object(ci_event_scope.Path, "read_text", return_value=json.dumps(event)), contextlib.redirect_stdout(output):
                status = ci_event_scope.main([
                    "--event-name", "pull_request", "--github-event", "synthetic.json"
                ])
            self.assertEqual(0, status)
            self.assertEqual(expected, output.getvalue())

    def test_unreadable_or_invalid_event_file_selects_full_code(self):
        for fault in (OSError("synthetic"), UnicodeError("synthetic"), None):
            output, errors = io.StringIO(), io.StringIO()
            with patch.object(ci_event_scope.Path, "read_text", side_effect=fault,
                              return_value="{"):
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    status = ci_event_scope.main([
                        "--event-name", "pull_request", "--github-event", "synthetic.json"
                    ])
            self.assertEqual(0, status)
            self.assertEqual("true\n", output.getvalue())
            self.assertIn("full code validation selected", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
