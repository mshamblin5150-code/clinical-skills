"""Synthetic approval decisions; persistence and unrelated graders are isolated.

These tests do not establish lock, durable-record or live Canvas acceptance.
"""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
from prose_bind import NAMING, bind

import approval_record
import bar_signatures
import assignment_submission
import canvas_load_route


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_canvas_editor_names_the_limits_without_copying_them(self):
        path = Path(__file__).resolve().parents[1] / "skills/_shared/reference/canvas-editor.md"
        sheet = path.read_text(encoding="utf-8")
        self.assertIn("canvas_load_route.DECLARED_LIMITS", sheet)
        self.assertEqual((), bind(canvas_load_route.DECLARED_LIMITS, sheet, mode=NAMING))


class CanvasContentApproval(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name).resolve()
        self.source = self.run / "reply.md"
        self.source.write_text("Synthetic reply.", encoding="utf-8")
        os.utime(self.source, (100, 100))
        self.rows = [
            {"type": "assistant", "timestamp": "1970-01-01T00:03:20Z",
             "message": {"content": "Synthetic reply."}},
            {"type": "user", "timestamp": "1970-01-01T00:05:00Z",
             "message": {"content": "Approve this reply."}},
        ]
        self.published = []
        self.previous = None
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(approval_record, "_main_transcripts", side_effect=lambda run: ([self.rows], False)))
        stack.enter_context(mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "pregrade clean")))
        stack.enter_context(mock.patch.object(approval_record.project_context, "go_ahead", return_value=SimpleNamespace(report="", finding=False, coverage=False)))
        stack.enter_context(mock.patch.object(approval_record.reader_remarks, "verify", return_value=[]))
        # The real decision callback runs; this adapter captures its proposed bytes.
        def transaction(path, decoder, change):
            update = change(self.previous)
            self.published.append(json.loads(update.payload))
            self.previous = self.published[-1]
            return update.result
        stack.enter_context(mock.patch.object(approval_record, "update_tool_record", side_effect=transaction))

    def approve(self, skill="discussion-reply", kind="content", reply="Approve this reply."):
        return approval_record.approve(
            self.run, skill=skill, submission="reply", sources=(self.source,),
            grader_args=(str(self.run),), content_approved=True,
            clinician_reply=reply, approval_kind=kind,
        )

    def test_content_approval_without_a_shown_load_route_is_refused(self):
        with self.assertRaisesRegex(approval_record.ApprovalRecordError, "Canvas load route"):
            self.approve()
        self.assertEqual([], self.published)

    def test_known_route_and_cost_shown_before_approval_are_accepted(self):
        for skill in ("discussion-post", "discussion-reply"):
            with self.subTest(skill=skill):
                self.previous = None
                self.rows[0]["message"]["content"] = (
                    "Synthetic reply.\nCanvas load route (reply): Raw HTML — cost: "
                    "confirm the raw textarea, then return to formatted view."
                )
                self.assertEqual(skill, self.approve(skill).skill)

    def test_another_content_approval_needs_a_fresh_route_but_posting_does_not(self):
        self.rows[0]["message"]["content"] += "\nCanvas load route (reply): Typing — cost: apply formatting and URL links manually."
        self.approve()
        self.rows.append({"type": "user", "timestamp": "1970-01-01T00:06:40Z", "message": {"content": "Approve posting."}})
        with self.assertRaisesRegex(approval_record.ApprovalRecordError, "Canvas load route"):
            self.approve(reply="Approve posting.")
        self.assertEqual("discussion-reply", self.approve(kind="posting", reply="Approve posting.").skill)

    def test_peer_comment_content_approval_does_not_need_a_composer_route(self):
        self.assertEqual("peer-critique", self.approve("peer-critique").skill)

    def test_practicum_composer_bar_without_a_route_is_not_signed(self):
        bar = self.run / "bar.md"
        text = "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\nSUBMISSION-TYPE: canvas-composer\n"
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=repr(newline)):
                original = text.replace("\n", newline).encode("utf-8")
                bar.write_bytes(original)
                os.utime(bar, (100, 100))
                with mock.patch.object(bar_signatures, "update_tool_record", side_effect=lambda path, decoder, change: change(None).result):
                    with self.assertRaisesRegex(bar_signatures.run_grader.SourceError, "Canvas load route"):
                        bar_signatures.sign(self.run, "Approve this reply.", skill="practicum-case-study")
                self.assertEqual(original, bar.read_bytes())

    def test_composer_assignment_content_gate_requires_route_disclosure(self):
        from test_assignment_bar import DECK_BAR
        deck = self.run / "deck.pptx"
        deck.write_bytes(b"synthetic deck")
        os.utime(deck, (100, 100))
        (self.run / "bar.md").write_text(DECK_BAR.replace("SUBMISSION-TYPE: file-upload", "SUBMISSION-TYPE: canvas-composer"), encoding="utf-8")
        with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(
            assignment_submission, "_require_signed_bar"
        ), mock.patch.object(assignment_submission, "update_tool_record", side_effect=lambda path, decoder, change: change(None).result):
            with self.assertRaisesRegex(assignment_submission.GateError, "Canvas load route"):
                assignment_submission.stage(self.run, deck, artifact_approved=True, clinician_reply="Approve this reply.")

    def test_practicum_bar_disclosure_precedes_drafting_and_file_upload_is_exempt(self):
        bar = self.run / "bar.md"
        for surface in ("canvas-composer", "file-upload"):
            with self.subTest(surface=surface):
                bar.write_text("SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\nSUBMISSION-TYPE: " + surface + "\n", encoding="utf-8")
                os.utime(bar, (100, 100))
                self.rows[0]["message"]["content"] = (
                    "Canvas load route (bar.md): Raw HTML — cost: confirm the raw textarea and return to formatted view."
                    if surface == "canvas-composer" else "Approve the file-upload bar."
                )
                # Each synthetic branch owns its retained copy allocation.
                for copy in (self.run / "signed-bars").glob("*"):
                    copy.unlink()
                with mock.patch.object(bar_signatures, "update_tool_record", side_effect=lambda path, decoder, change: change(None).result):
                    self.assertEqual("practicum-case-study", bar_signatures.sign(self.run, "Approve this reply.", skill="practicum-case-study")["skill"])
                self.source.write_text("Synthetic draft after bar approval.", encoding="utf-8")
                os.utime(self.source, (400, 400))
                self.rows.append({"type": "user", "timestamp": "1970-01-01T00:08:20Z", "message": {"content": "Approve the draft."}})
                self.previous = None
                self.assertEqual("practicum-case-study", self.approve("practicum-case-study", reply="Approve the draft.").skill)

    def test_assignment_route_is_conditional_on_composer_surface(self):
        from test_assignment_bar import DECK_BAR
        deck = self.run / "deck.pptx"
        deck.write_bytes(b"synthetic deck")
        os.utime(deck, (100, 100))
        for surface in ("file-upload", "canvas-composer"):
            with self.subTest(surface=surface):
                (self.run / "bar.md").write_text(DECK_BAR.replace("SUBMISSION-TYPE: file-upload", "SUBMISSION-TYPE: " + surface), encoding="utf-8")
                self.rows[0]["message"]["content"] = (
                    "Canvas load route (deck): Typing — cost: apply formatting and URL links manually."
                    if surface == "canvas-composer" else "Approve the deck file."
                )
                with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(
                    assignment_submission, "_require_signed_bar"
                ), mock.patch.object(assignment_submission, "update_tool_record", side_effect=lambda path, decoder, change: change(None).result):
                    self.assertEqual(deck, assignment_submission.stage(self.run, deck, artifact_approved=True, clinician_reply="Approve this reply.").artifact)

    def test_repeated_composer_gate_matches_the_later_identical_reply(self):
        from test_assignment_bar import DECK_BAR
        deck = self.run / "deck.pptx"
        deck.write_bytes(b"synthetic deck")
        os.utime(deck, (100, 100))
        (self.run / "bar.md").write_text(DECK_BAR.replace("SUBMISSION-TYPE: file-upload", "SUBMISSION-TYPE: canvas-composer"), encoding="utf-8")
        self.rows.extend([
            {"type": "assistant", "timestamp": "1970-01-01T00:06:40Z", "message": {"content": "Canvas load route (deck): Typing — cost: format and link manually."}},
            {"type": "user", "timestamp": "1970-01-01T00:08:20Z", "message": {"content": "Approve this reply."}},
        ])
        for previous in ({"reply_matched_at": 300}, {"gate1_recorded_at": 300}):
            proposed = []
            def transaction(path, decoder, change):
                update = change(previous)
                proposed.append(json.loads(update.payload))
                return update.result
            with self.subTest(previous=previous), mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(
                assignment_submission, "_require_signed_bar"
            ), mock.patch.object(assignment_submission, "update_tool_record", side_effect=transaction):
                self.assertEqual(deck, assignment_submission.stage(self.run, deck, artifact_approved=True, clinician_reply="Approve this reply.").artifact)
            self.assertEqual(500, proposed[-1]["reply_matched_at"])

    def test_changed_bar_parse_failure_stays_a_gate_error(self):
        from test_assignment_bar import DECK_BAR
        deck = self.run / "deck.pptx"
        deck.write_bytes(b"synthetic deck")
        os.utime(deck, (100, 100))
        bar = self.run / "bar.md"
        bar.write_text(DECK_BAR, encoding="utf-8")
        def changed_after_check(run):
            bar.write_text("SIGNED: 2000-01-01\n", encoding="utf-8")
        with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(
            assignment_submission, "_require_signed_bar", side_effect=changed_after_check
        ), mock.patch.object(assignment_submission, "update_tool_record", side_effect=lambda path, decoder, change: change(None).result):
            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.stage(self.run, deck, artifact_approved=True, clinician_reply="Approve this reply.")

    def test_composer_reapproval_with_unreadable_history_time_is_refused(self):
        from test_assignment_bar import DECK_BAR
        deck = self.run / "deck.pptx"
        deck.write_bytes(b"synthetic deck")
        os.utime(deck, (100, 100))
        (self.run / "bar.md").write_text(DECK_BAR.replace("SUBMISSION-TYPE: file-upload", "SUBMISSION-TYPE: canvas-composer"), encoding="utf-8")
        for previous in ({}, {"reply_matched_at": "bad", "gate1_recorded_at": "bad"}):
            with self.subTest(previous=previous), mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(
                assignment_submission, "_require_signed_bar"
            ), mock.patch.object(assignment_submission, "update_tool_record", side_effect=lambda path, decoder, change: change(previous).result):
                with self.assertRaisesRegex(assignment_submission.GateError, "previous Canvas content approval time unreadable"):
                    assignment_submission.stage(self.run, deck, artifact_approved=True, clinician_reply="Approve this reply.")


class ShownRouteContract(unittest.TestCase):
    def message(self, declaration, timestamp="1970-01-01T00:03:20Z", **flags):
        return {"type": "assistant", "timestamp": timestamp, "message": {"content": declaration}, **flags}

    def check(self, rows, unread=False):
        canvas_load_route.require_shown(Path("synthetic-run"), "reply", after=100, before=300, transcripts=([rows], unread))

    def test_each_named_route_can_carry_its_declared_burden(self):
        for route, cost in (
            ("Raw HTML", "confirm raw textarea and switch back to formatted view."),
            ("Content interface", "register with a keystroke away from URLs to avoid autolinking."),
            ("Typing", "apply formatting and each URL link manually."),
        ):
            with self.subTest(route=route):
                self.check([self.message(f"Canvas load route (reply): {route} — cost: {cost}")])

    def test_incomplete_unknown_or_wrong_item_declarations_refuse(self):
        for declaration in (
            "Canvas load route (reply): Raw HTML",
            "Canvas load route (reply): Raw HTML — cost: ",
            "Canvas load route (reply): Unknown — cost: confirm view.",
            "Canvas load route (another-reply): Raw HTML — cost: confirm view.",
        ):
            with self.subTest(declaration=declaration), self.assertRaises(canvas_load_route.LoadRouteError):
                self.check([self.message(declaration)])

    def test_disclosure_must_be_strictly_before_approval_and_after_source_boundary(self):
        declaration = "Canvas load route (reply): Raw HTML — cost: confirm raw and return to formatted view."
        for timestamp in ("1970-01-01T00:01:40Z", "1970-01-01T00:01:00Z", "1970-01-01T00:05:00Z", "1970-01-01T00:06:00Z"):
            with self.subTest(timestamp=timestamp), self.assertRaises(canvas_load_route.LoadRouteError):
                self.check([self.message(declaration, timestamp)])

    def test_latest_malformed_or_conflicting_declaration_does_not_inherit_an_old_one(self):
        valid = "Canvas load route (reply): Typing — cost: format and link manually."
        for latest in ("Canvas load route (reply): Typing", valid + "\n" + valid):
            with self.subTest(latest=latest), self.assertRaises(canvas_load_route.LoadRouteError):
                self.check([self.message(valid), self.message(latest, "1970-01-01T00:04:00Z")])

    def test_unreadable_population_or_message_time_cannot_verify_disclosure(self):
        declaration = "Canvas load route (reply): Typing — cost: format and link manually."
        with self.assertRaisesRegex(canvas_load_route.LoadRouteError, "unreadable"):
            self.check([self.message(declaration)], unread=True)
        with self.assertRaisesRegex(canvas_load_route.LoadRouteError, "unreadable"):
            self.check([self.message(declaration, "not-a-time")])

    def test_user_tool_meta_sidechain_and_analysis_text_are_not_a_showing(self):
        declaration = "Canvas load route (reply): Typing — cost: format and link manually."
        for row in (
            {"type": "user", "timestamp": "1970-01-01T00:03:20Z", "message": {"content": declaration}},
            self.message(declaration, isMeta=True), self.message(declaration, isSidechain=True),
            {"type": "response_item", "timestamp": "1970-01-01T00:03:20Z", "payload": {"type": "message", "role": "assistant", "channel": "analysis", "content": [{"type": "output_text", "text": declaration}]}},
            {"type": "response_item", "timestamp": "1970-01-01T00:03:20Z", "payload": {"type": "function_call_output", "output": declaration}},
        ):
            with self.subTest(row=row), self.assertRaises(canvas_load_route.LoadRouteError):
                self.check([row])
