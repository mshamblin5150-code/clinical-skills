"""Clinician's words are separate from harness envelopes. ADR 0387, #1693."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import aar_scan
import approval_record


class ClinicianWords(unittest.TestCase):
    def reduce(self, text, *, codex=False, **flags):
        row = self.row(text, codex=codex, **flags)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.jsonl"
            path.write_text(json.dumps(row), encoding="utf-8")
            return aar_scan.reduce_transcript(path)

    def row(self, text, *, codex=False, **flags):
        if codex:
            values = text if isinstance(text, list) else [text]
            return {"type": "response_item", "uuid": "u1", "timestamp": "2100-01-01T00:00:00Z",
                    "payload": {"type": "message", "role": "user", "content": [
                        {"type": "input_text", "text": value} for value in values]}, **flags}
        return {"type": "user", "uuid": "u1", "timestamp": "2100-01-01T00:00:00Z",
                "message": {"content": text}, **flags}

    def verify(self, row, reply):
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([[row]], False)):
            return approval_record.verify_clinician_reply(Path("."), reply, (), source_modified_at=0).state

    def test_reminder_and_words_have_separate_kinds_and_identifiers(self):
        entries = self.reduce("<system-reminder>Machine.</system-reminder>\nSubmit it.")
        self.assertEqual([(e.identifier, e.kind, e.text) for e in entries], [
            ("u1", "system-reminder", "<system-reminder>Machine.</system-reminder>"),
            ("u1#2", "clinician", "Submit it."),
        ])
        for codex in (False, True):
            self.assertEqual(self.verify(self.row("<system-reminder>Machine.</system-reminder>\nSubmit it.", codex=codex), "Submit it."), "verified")

    def test_instructions_items_and_recognized_count(self):
        header = "# AGENTS.md instructions for synthetic\nMachine instructions."
        context = "<environment_context>Machine.</environment_context>"
        self.assertEqual([e.kind for e in self.reduce(header, codex=True)], ["agents-instructions"])
        self.assertNotIn("clinician", [e.kind for e in self.reduce([context, header], codex=True)])
        self.assertEqual(self.verify(self.row(header, codex=True), header), "not found")
        for heading, expected in ((header, 1), (header.replace("# AGENTS.md instructions", "# Changed header"), 0)):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "synthetic.jsonl"
                path.write_text(json.dumps(self.row([context, heading], codex=True)), encoding="utf-8")
                population = aar_scan.reduce_transcript(path)
                self.assertEqual(aar_scan.extract_diagnostics([path], population).agents_instructions, expected)

    def test_question_answers_are_whole_separate_pieces(self):
        text = '<send_user_message_question_reply>' + json.dumps([
            {"question": "Submit?", "questionItemId": "q1", "answer": "Yes."},
            {"question": "Which?", "questionItemId": "q2", "answer": "One and three."},
        ]) + '</send_user_message_question_reply>'
        entries = self.reduce(text, codex=True)
        self.assertEqual([e.kind for e in entries], ["codex-question", "clinician", "clinician"])
        self.assertEqual([e.text for e in entries[1:]], ["Yes.", "One and three."])
        for answer in ("Yes.", "One and three."):
            self.assertEqual(self.verify(self.row(text, codex=True), answer), "verified")
        for answer in ("Submit?", "Yes. One and three.", "One"):
            self.assertEqual(self.verify(self.row(text, codex=True), answer), "not found")

    def test_adjacent_codex_text_items_are_one_whole_reply(self):
        for prefix in ([], ["<system-reminder>Machine.</system-reminder>"]):
            text = [*prefix, "Submit", "it."]
            entries = self.reduce(text, codex=True)
            words = [(e.kind, e.text) for e in entries if e.kind == "clinician"]
            self.assertEqual(words, [("clinician", "Submit\nit.")])
            self.assertEqual(self.verify(self.row(text, codex=True), "Submit it."), "verified")
            self.assertEqual(self.verify(self.row(text, codex=True), "Submit"), "not found")

    def test_slash_command_arguments_are_words(self):
        text = '<command-message>implement</command-message>\n<command-name>/implement</command-name>\n<command-args>1693 and merge</command-args>'
        entries = self.reduce(text)
        self.assertEqual([e.kind for e in entries], ["command-name", "clinician"])
        self.assertEqual(entries[1].text, "1693 and merge")
        self.assertEqual(self.verify(self.row(text), "1693 and merge"), "verified")

    def test_observed_wrappers_set_aside_only_their_own_text(self):
        for tag, kind in (("external_codex_apps_open_page", "codex-app-page"), ("skill", "codex-skill"),
                          ("cross-session-message", "cross-session-message"), ("david_lifecycle_wake", "david-lifecycle-wake")):
            with self.subTest(tag=tag):
                text = f"<{tag}>Submit it.</{tag}>"
                self.assertEqual([e.kind for e in self.reduce(text)], [kind])
                self.assertEqual(self.verify(self.row(text), "Submit it."), "not found")
                self.assertEqual(self.verify(self.row(text + "\nSubmit it."), "Submit it."), "verified")

    def test_flagged_and_unlisted_trigger_rows_never_supply_a_reply(self):
        for tag in ("hook-context", "scheduled-trigger", "automation-trigger"):
            text = f"<{tag}>Machine.</{tag}>\nSubmit it."
            for codex in (False, True):
                for flags in ({}, {"isMeta": True}, {"isSidechain": True}, {"isCompactSummary": True}):
                    with self.subTest(tag=tag, codex=codex, flags=flags):
                        self.assertEqual(self.verify(self.row(text, codex=codex, **flags), "Submit it."), "not found")

    def test_prior_watermark_still_resolves_and_leaves_later_pieces(self):
        entries = self.reduce('<system-reminder>Machine.</system-reminder>\nSubmit it.')
        self.assertEqual([e.identifier for e in aar_scan._after_watermark(entries, "u1")], ["u1#2"])
        self.assertEqual(aar_scan._after_watermark(entries, "u1#2"), [])

    def test_contiguous_envelopes_keep_first_kind_and_nested_text_stays_machine(self):
        text = '<system-reminder>Outer <system-reminder>Inner.</system-reminder> tail.</system-reminder>\n<skill>Machine.</skill>\nSubmit it.'
        entries = self.reduce(text)
        self.assertEqual([e.kind for e in entries], ["system-reminder", "clinician"])
        self.assertIn("tail.</system-reminder>", entries[0].text)
        self.assertEqual(entries[1].text, "Submit it.")

    def test_malformed_question_payload_never_supplies_an_answer(self):
        for payload in ('invalid', '{}', '[{"answer": "Yes."}]'):
            text = f'<send_user_message_question_reply>{payload}</send_user_message_question_reply>'
            self.assertEqual([e.kind for e in self.reduce(text)], ["codex-question"])
            self.assertEqual(self.verify(self.row(text), "Yes."), "not found")


if __name__ == "__main__":
    unittest.main()
