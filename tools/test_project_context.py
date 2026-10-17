"""Behavior tests for the project-context gate. #1395.

Every project, path, service, and payload is synthetic.

phi-scan: synthetic
"""

from __future__ import annotations

import hashlib
import importlib
import json
import io
import sys
from contextlib import redirect_stderr, redirect_stdout
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import project_context as context
import repo_root
import run_grader
import approval_record
import assignment_submission
from test_discussion_reply_scan import Run


class ProjectContextFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name).resolve()
        self.run = self.root / "atlas-discussion"
        self.run.mkdir()
        self.memory = self.root / "memory-index.md"
        self.location = self.root / "atlas"
        self.location.mkdir()
        self.plan = self.location / "atlas-plan.md"
        self.memory.write_bytes(b"memory index\n")
        self.plan.write_bytes(b"atlas plan\n")
        self.registry = self.root / "project-registry.md"
        self.registry.write_text(
            "\n".join(
                (
                    f"MEMORY-INDEX: {self.memory}",
                    "",
                    "PROJECT: Atlas",
                    f"  LOCATION: {self.location}",
                    "  SERVICE: open-brain",
                    "",
                )
            ),
            encoding="utf-8",
        )
        self.service_payloads = {"open-brain": {"thought-17": "founder account"}}

    def record(self, *entries: str, header: tuple[str, ...] = ()) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "\n".join(
                (
                    "PROJECT-CONTEXT: Atlas",
                    *(("OWN-SUBMISSION: none - no earlier synthetic submission",)
                      if not any(line.startswith("OWN-SUBMISSION:") for line in header) else ()),
                    *(("CASE-MATERIAL: none - no synthetic case material",)
                      if not any(line.startswith("CASE-MATERIAL:") for line in header) else ()),
                    *(("CASE-RESEARCH: none - no synthetic case research",)
                      if not any(line.startswith("CASE-RESEARCH:") for line in header) else ()),
                    *header,
                    "CONFIRMED: 2001-01-01",
                    "",
                    *entries,
                    "",
                )
            ),
            encoding="utf-8",
        )

    def memory_entry(self, state: str = "read") -> str:
        return "\n".join(
            (
                f"## PLACE: {self.memory}",
                f"STATE: {state}",
                f"OPENED: {self.memory}",
            )
        )

    def plan_entry(self, *, terms: str = "founder motivation", opened: str | None = None) -> str:
        return "\n".join(
            (
                f"## PLACE: {self.location}",
                "STATE: searched",
                f"ROOT: {self.location}",
                f"TERMS: {terms}",
                "EXAMINED: 4",
                "UNREADABLE: 0",
                f"OPENED: {opened or self.plan}",
            )
        )

    def service_entry(self, *, opened: str = "thought-17") -> str:
        return "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: searched",
                "CORPUS-SIZE: 42",
                "QUERY: founder motivation | THRESHOLD: 0.75 | LIMIT: 5 | HITS: 1",
                f"OPENED: {opened}",
            )
        )

    def complete_record(self) -> None:
        self.record(self.memory_entry(), self.plan_entry(), self.service_entry())

    def write(self, payloads: dict[str, dict[str, str]] | None = None) -> context.GateResult:
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.write_record(
                self.run,
                service_payloads=self.service_payloads if payloads is None else payloads,
                submission="submission",
            )

    def complete(self, submission: str | None = "submission") -> context.CompletionGate:
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.completion_gate(self.run, submission)


class CourseHistory(ProjectContextFixture):
    def prepare(self, *history, confirmed="2026-10-12T20:34:01Z"):
        self.record(self.memory_entry(), self.service_entry(),
                    self.plan_entry().replace("STATE: searched", "STATE: read"),
                    header=tuple(f"COURSE-HISTORY: {value}" for value in history))
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace(
            "CONFIRMED: 2001-01-01", f"CONFIRMED: {confirmed}"), encoding="utf-8")

    def command(self, *arguments):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(self.service_payloads))), \
                redirect_stdout(output), redirect_stderr(output):
            options = arguments or ("--write", "--submission", "submission", "--service-payloads", "-")
            code = context.main([str(self.run), *options])
        return code, output.getvalue()

    def test_missing_course_history_refuses(self):
        self.prepare()
        code, output = self.command()
        self.assertEqual(1, code, output)
        self.assertIn("COURSE-HISTORY is missing", output)

    def test_malformed_or_unopened_history_refuses(self):
        for values, message in (
            (("none",), "none needs a reason"),
            (("none - first module", str(self.plan)), "cannot put none beside"),
            ((str(self.plan), str(self.plan.parent / "." / self.plan.name)), "duplicate COURSE-HISTORY path"),
            ((str(self.memory.parent / "unopened.md"),), "not OPENED in a read PLACE"),
            (("relative.md",), "absolute file path"),
        ):
            with self.subTest(values=values):
                self.prepare(*values)
                code, output = self.command()
                self.assertEqual(1, code, output)
                self.assertIn(message, output)

    def test_path_and_reasoned_none_pass_and_survive_the_go_ahead(self):
        for value in (str(self.plan), "none - first module"):
            with self.subTest(value=value):
                self.prepare(value)
                code, output = self.command()
                self.assertEqual(0, code, output)
                self.assertIn(f"COURSE-HISTORY: {value}",
                              (self.run / context.RECORD_NAME).read_text(encoding="utf-8"))
                code, output = self.command("--go-ahead", "submission")
                self.assertEqual(0, code, output)
                self.assertIn("course history: clean", output)

    def test_pre_build_record_is_not_graded_or_backfilled(self):
        for confirmed in ("2026-10-11", "2026-10-12", "2026-10-12T20:34:00Z"):
            with self.subTest(confirmed=confirmed):
                self.prepare(confirmed=confirmed)
                code, output = self.command()
                self.assertEqual(0, code, output)
                self.assertIn("course history: not graded; pre-cutoff records: 1", output)
                self.assertNotIn("COURSE-HISTORY:", (self.run / context.RECORD_NAME).read_text(encoding="utf-8"))
                code, output = self.command("--go-ahead", "submission")
                self.assertEqual(0, code, output)
                self.assertIn("course history: not graded", output)

    def test_each_declared_paper_must_be_opened_in_a_read_place(self):
        self.prepare(str(self.plan), str(self.memory))
        code, output = self.command()
        self.assertEqual(0, code, output)
        text = (self.run / context.RECORD_NAME).read_text(encoding="utf-8")
        self.assertEqual(2, text.count("COURSE-HISTORY:"))
        self.prepare(str(self.plan))
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace(
            f"## PLACE: {self.location}\nSTATE: read", f"## PLACE: {self.location}\nSTATE: searched"),
            encoding="utf-8")
        code, output = self.command()
        self.assertEqual(1, code, output)
        self.assertIn("not OPENED in a read PLACE", output)

    def test_changed_history_declaration_breaks_the_digest_at_go_ahead(self):
        self.prepare(str(self.plan))
        self.assertEqual(0, self.command()[0])
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace(
            f"COURSE-HISTORY: {self.plan}", "COURSE-HISTORY: none - first module"), encoding="utf-8")
        code, output = self.command("--go-ahead", "submission")
        self.assertEqual(1, code, output)
        self.assertIn("record fingerprint is invalid", output)

    def test_course_history_without_a_project_still_owes_its_opened_file(self):
        self.prepare(str(self.plan))
        path = self.run / context.RECORD_NAME
        path.write_text(
            "PROJECT-CONTEXT: none - no project\n"
            "OWN-SUBMISSION: none - no submission\n"
            "CASE-MATERIAL: none - no case\nCASE-RESEARCH: none - no research\n"
            f"COURSE-HISTORY: {self.plan}\n"
            f'PROJECT-SEARCH: {self.location} - "earlier papers"\n'
            "CONFIRMED: 2026-10-12T20:34:01Z\n" + self.plan_entry().replace("STATE: searched", "STATE: read"),
            encoding="utf-8")
        self.assertEqual(0, self.command()[0])
        self.plan.write_text("changed course paper", encoding="utf-8")
        code, output = self.command("--go-ahead", "submission")
        self.assertEqual(2, code, output)
        self.assertIn("file item moved", output)

    def test_shared_rule_and_all_five_drafting_and_go_ahead_pointers(self):
        root = Path(__file__).resolve().parents[1]
        voice = (root / "skills/_shared/reference/voice.md").read_text(encoding="utf-8")
        section = voice.split("## Course history\n", 1)[1].split("\n## ", 1)[0]
        for rule in ("every earlier submission in the same", "replies", "critiques",
                     "Judge reuse by fit, never by repetition", "one line on its earlier framing",
                     "one line on its framing", "When there is none", "no grader checks",
                     "COURSE-HISTORY"):
            self.assertIn(rule, section)
        for skill in ("course-assignment", "discussion-post", "discussion-reply",
                      "peer-critique", "practicum-case-study"):
            text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                pointer = "Before drafting, follow [Course history](../_shared/reference/voice.md#course-history)."
                self.assertIn(pointer, text)
                image_end = text.index("\n\n", text.index("Reuse a recorded image whole where it fits."))
                self.assertLess(text.index(pointer), image_end)
                self.assertIn("At the go-ahead, show the reuse list required by [Course history]", text)


class OwnedAssets(ProjectContextFixture):
    def command(self):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), \
                mock.patch("sys.stdin", io.StringIO(json.dumps(self.service_payloads))), \
                mock.patch("sys.stdout", output), mock.patch("sys.stderr", output):
            code = context.main([str(self.run), "--write", "--submission", "submission",
                                 "--service-payloads", "-"])
        return code, output.getvalue()

    def assets(self, *values):
        self.registry.write_text(
            self.registry.read_text(encoding="utf-8") +
            "".join(f"ASSET: {value}\n" for value in values), encoding="utf-8")

    def test_registry_asset_refusals_use_the_public_command(self):
        original = self.registry.read_text(encoding="utf-8")
        for values, message in ((('',), 'ASSET needs a description'),
                                (('owned outbox', 'owned outbox'), 'duplicate ASSET entry')):
            with self.subTest(values=values):
                self.registry.write_text(original, encoding="utf-8")
                self.assets(*values)
                self.complete_record()
                code, output = self.command()
                self.assertEqual(1, code, output)
                self.assertIn(message, output)

    def test_header_owes_exactly_the_declared_projects_assets(self):
        self.assets('owned outbox', 'verified domain')
        for lines, message in (((), 'missing ASSET'),
                               (('owned outbox',), 'missing ASSET'),
                               (('owned outbox', 'verified domain', 'owned outbox'), 'duplicate ASSET'),
                               (('owned outbox', 'verified domain', 'unregistered tool'), 'unregistered ASSET'),
                               (('',), 'ASSET needs a description')):
            with self.subTest(lines=lines):
                self.record(self.memory_entry(), self.plan_entry(), self.service_entry(),
                            header=tuple(f'ASSET: {value}' for value in lines))
                code, output = self.command()
                self.assertEqual(1, code, output)
                self.assertIn(message, output)

    def test_assets_parse_render_and_move_the_digest(self):
        self.complete_record()
        self.assertEqual(0, self.command()[0])
        before = context.recorded_digest(self.run)
        self.assets('owned outbox', 'verified domain')
        self.record(self.memory_entry(), self.plan_entry(), self.service_entry(),
                    header=('ASSET: owned outbox', 'ASSET: verified domain'))
        code, output = self.command()
        self.assertEqual(0, code, output)
        self.assertNotEqual(before, context.recorded_digest(self.run))
        self.assertEqual(('owned outbox', 'verified domain'),
                         context.read_registry(self.registry.read_text(encoding='utf-8')).projects['Atlas'].assets)
        written = self.run.joinpath(context.RECORD_NAME).read_text(encoding='utf-8')
        self.assertIn('ASSET: owned outbox\nASSET: verified domain\n', written)
        self.assertFalse(self.complete().finding)
        self.assets('newly shipped tool')
        self.assertTrue(self.complete().finding)

    def test_none_refuses_assets_without_reading_the_registry(self):
        self.run.joinpath(context.RECORD_NAME).write_text(
            'PROJECT-CONTEXT: none - no project\n'
            'OWN-SUBMISSION: none - no submission\n'
            'CASE-MATERIAL: none - no case\nCASE-RESEARCH: none - no research\n'
            'ASSET: owned outbox\nCONFIRMED: 2001-01-01\n', encoding='utf-8')
        self.registry.unlink()
        code, output = self.command()
        self.assertEqual(1, code, output)
        self.assertIn('a none run cannot carry ASSET', output)
        self.assertTrue(self.complete().finding)

    def test_assets_belong_to_their_project(self):
        self.assets('owned outbox')
        self.registry.write_text(self.registry.read_text(encoding='utf-8') +
                                 'PROJECT: Other\nASSET: other tool\n', encoding='utf-8')
        self.record(self.memory_entry(), self.plan_entry(), self.service_entry(),
                    header=('ASSET: owned outbox',))
        code, output = self.command()
        self.assertEqual(0, code, output)

    def test_shared_reference_states_the_purchase_rule_in_both_briefs(self):
        text = (Path(__file__).resolve().parents[1] /
                'skills/_shared/reference/sourcing.md').read_text(encoding='utf-8')
        rule = ('A draft sentence recommending that the clinician or his project buy, rent, or subscribe to something\n'
                'a listed asset already provides is `CONTEXT-VERDICT: narrows`, unless the draft states why the owned\n'
                'asset falls short.')
        draft, reader = text.split('Before any go-ahead, a fresh context receives only', 1)
        self.assertIn(rule, draft)
        self.assertIn(rule, reader)


class DamagedProjectContextIsRefusedBeforeWriting(ProjectContextFixture):
    def command(self):
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), redirect_stdout(output), redirect_stderr(output), mock.patch.object(
            sys, "stdin", io.StringIO(json.dumps(self.service_payloads))
        ):
            status = context.main([str(self.run), "--write", "--submission", "submission", "--service-payloads", "-"])
        return status, output.getvalue()

    def test_a_damaged_free_text_line_is_named_and_preserved(self):
        self.record(self.memory_entry(), self.plan_entry(terms="founder\a motivation"), self.service_entry())
        path = self.run / context.RECORD_NAME
        before = path.read_bytes()
        status, report = self.command()
        self.assertEqual(status, 1)
        self.assertIn(f"{path}: line 13", report)
        self.assertIn("U+0007", report)
        self.assertIn("standing rule 6", report)
        self.assertEqual(path.read_bytes(), before)
        self.assertNotIn("ORDER-OBSERVATION", report)

    def test_path_text_and_registry_damage_are_refused_by_line(self):
        characters = ("\t", "\a", "\0", "\f", "\v", "\r")
        registry_text = self.registry.read_text(encoding="utf-8")
        for character in characters:
            for field in ("OPENED", "TERMS", "DETAIL", "registry"):
                with self.subTest(character=ascii(character), field=field):
                    self.registry.write_text(registry_text, encoding="utf-8")
                    self.complete_record()
                    path = self.registry if field == "registry" else self.run / context.RECORD_NAME
                    text = path.read_text(encoding="utf-8")
                    if field == "registry":
                        text = text.replace("LOCATION: ", f"LOCATION: damaged{character}")
                        line = 4
                    elif field == "DETAIL":
                        text += f"DETAIL: damaged{character}text\n"
                        line = len(text.split("\n")) - 1
                    else:
                        text = text.replace(f"{field}: ", f"{field}: damaged{character}", 1)
                        line = 9 if field == "OPENED" else 13
                    path.write_bytes(text.encode("utf-8"))
                    before = path.read_bytes()
                    record_before = (self.run / context.RECORD_NAME).read_bytes()
                    status, report = self.command()
                    self.assertEqual(status, 1, report)
                    self.assertIn(f"{path}: line {line}", report)
                    self.assertIn(f"U+{ord(character):04X}", report)
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual((self.run / context.RECORD_NAME).read_bytes(), record_before)
                    self.assertNotIn("could not be read", report)
                    self.assertNotIn("retrieval before draft", report)

    def test_every_damaged_line_and_character_is_reported_before_other_findings(self):
        path = self.run / context.RECORD_NAME
        path.write_bytes(b"PROJECT-CONTEXT: none\nTERMS: bad\x07\ttext\nDETAIL: bad\x00text\n")
        before = path.read_bytes()
        status, report = self.command()
        self.assertEqual(status, 1)
        for line, character in ((2, "U+0007"), (2, "U+0009"), (3, "U+0000")):
            self.assertIn(f"{path}: line {line}: {character}", report)
        self.assertNotIn("CONFIRMED", report)
        self.assertEqual(path.read_bytes(), before)

    def test_windows_line_endings_and_fingerprinted_control_bytes_are_accepted(self):
        self.complete_record()
        for path in (self.run / context.RECORD_NAME, self.registry):
            path.write_bytes(path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
        self.plan.write_bytes(b"opened binary\x00\x07\x0c\t\r")
        self.service_payloads["open-brain"]["thought-17"] = "service\x00\ttext"
        status, report = self.command()
        self.assertEqual(status, 0, report)
        self.assertIn("CONTEXT-DIGEST:", (self.run / context.RECORD_NAME).read_text(encoding="utf-8"))

    def test_none_does_not_read_a_damaged_or_absent_registry(self):
        for absent in (False, True):
            with self.subTest(absent=absent):
                self.record()
                path = self.run / context.RECORD_NAME
                path.write_text(path.read_text(encoding="utf-8").replace("PROJECT-CONTEXT: Atlas", "PROJECT-CONTEXT: none - no project in this synthetic run"), encoding="utf-8")
                if absent:
                    self.registry.unlink()
                else:
                    self.registry.write_bytes(b"LOCATION: bad\x00\t\rpath\n")
                status, report = self.command()
                self.assertEqual(status, 0, report)

    def test_final_bare_carriage_return_is_damage(self):
        self.complete_record()
        path = self.run / context.RECORD_NAME
        path.write_bytes(path.read_bytes() + b"\r")
        status, report = self.command()
        self.assertEqual(status, 1, report)
        self.assertIn("U+000D", report)


class AProjectContextGateWritesTheRetrievalFingerprint(ProjectContextFixture):
    def test_a_complete_record_is_canonicalized_with_machine_written_hashes(self) -> None:
        self.complete_record()

        result = self.write()

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.waived, 0)
        written = self.run.joinpath(context.RECORD_NAME).read_text(encoding="utf-8")
        memory_digest = hashlib.sha256(b"memory index\n").hexdigest()
        self.assertIn(
            f"OPENED: {self.memory} | SHA256: {memory_digest}",
            written,
        )
        self.assertIn(
            "OPENED: thought-17 | SHA256: "
            + hashlib.sha256(b"founder account").hexdigest(),
            written,
        )
        digest = context.recorded_digest(self.run)
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertIn(f"CONTEXT-DIGEST: {digest}", written)

    def test_the_context_digest_binds_own_submission_and_sorted_place_item_hash_triples(self) -> None:
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        triples = sorted(
            (
                (str(self.memory), str(self.memory), hashlib.sha256(b"memory index\n").hexdigest()),
                (str(self.location), str(self.plan), hashlib.sha256(b"atlas plan\n").hexdigest()),
                ("open-brain", "thought-17", hashlib.sha256(b"founder account").hexdigest()),
            )
        )
        expected = hashlib.sha256(
            ("OWN-SUBMISSION\0none - no earlier synthetic submission\n" +
             "CASE-MATERIAL\0none - no synthetic case material\n" +
             "CASE-RESEARCH\0none - no synthetic case research\n" +
             "".join("\0".join(triple) + "\n" for triple in triples)).encode("utf-8")
        ).hexdigest()
        self.assertEqual(context.recorded_digest(self.run), expected)

    def test_a_none_declaration_needs_a_reason_and_writes_none(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none - critique concerns a classmate's case\nOWN-SUBMISSION: none - no earlier synthetic submission\nCASE-MATERIAL: none - no synthetic case material\nCASE-RESEARCH: none - no synthetic case research\n"
            "CONFIRMED: 2001-01-01\n",
            encoding="utf-8",
        )

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(context.recorded_digest(self.run), "e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf")

    def test_none_without_a_reason_is_a_finding(self) -> None:
        self.run.joinpath(context.RECORD_NAME).write_text(
            "PROJECT-CONTEXT: none\nOWN-SUBMISSION: none - no earlier synthetic submission\nCASE-MATERIAL: none - no synthetic case material\nCASE-RESEARCH: none - no synthetic case research\nCONFIRMED: 2001-01-01\n", encoding="utf-8"
        )
        self.assertEqual(self.write(payloads={}).exit_code, 1)

    def test_an_unregistered_project_is_a_coverage_stop_that_asks_the_clinician(self) -> None:
        self.record()
        self.run.joinpath(context.RECORD_NAME).write_text(
            self.run.joinpath(context.RECORD_NAME)
            .read_text(encoding="utf-8")
            .replace("Atlas", "Unregistered", 1),
            encoding="utf-8",
        )

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 2)
        self.assertIn("ask the clinician", result.report)

    def test_a_missing_registry_is_a_coverage_stop(self) -> None:
        self.complete_record()
        with mock.patch.object(
            repo_root, "project_registry", return_value=self.root / "absent.md"
        ):
            result = context.write_record(self.run, service_payloads=self.service_payloads)
        self.assertEqual(result.exit_code, 2)


class EveryOwedPlaceHasOneSubstantiveEntry(ProjectContextFixture):
    def test_a_missing_owed_place_is_a_finding(self) -> None:
        self.record(self.memory_entry(), self.plan_entry())
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("open-brain", result.report)

    def test_a_duplicate_owed_place_is_a_finding(self) -> None:
        self.record(
            self.memory_entry(), self.plan_entry(), self.service_entry(), self.service_entry()
        )
        self.assertEqual(self.write().exit_code, 1)

    def test_a_searched_path_needs_terms_and_examined_count(self) -> None:
        self.record(
            self.memory_entry(),
            self.plan_entry().replace("TERMS: founder motivation\n", "").replace(
                "EXAMINED: 4\n", ""
            ),
            self.service_entry(),
        )
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("TERMS", result.report)
        self.assertIn("EXAMINED", result.report)

    def test_a_searched_path_records_opened_none_as_a_miss(self) -> None:
        self.record(self.memory_entry(), self.plan_entry(opened="none"), self.service_entry())
        result = self.write()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("OPENED: none", self.run.joinpath(context.RECORD_NAME).read_text())

    def test_a_read_location_cannot_open_an_unrelated_file(self) -> None:
        unrelated = self.root / "unrelated.md"
        unrelated.write_text("synthetic unrelated context\n", encoding="utf-8")
        self.record(
            self.memory_entry().replace(
                f"OPENED: {self.memory}", f"OPENED: {unrelated}"
            ),
            self.plan_entry(),
            self.service_entry(),
        )

        result = self.write()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("outside owed PLACE", result.report)

    def test_a_searched_location_root_must_be_the_owed_location(self) -> None:
        self.record(
            self.memory_entry(),
            self.plan_entry().replace(f"ROOT: {self.location}", f"ROOT: {self.root}"),
            self.service_entry(),
        )

        result = self.write()

        self.assertEqual(result.exit_code, 1)
        self.assertIn("ROOT does not match", result.report)

    def test_a_service_needs_corpus_query_threshold_limit_and_hits(self) -> None:
        incomplete = self.service_entry().replace("CORPUS-SIZE: 42\n", "").replace(
            " | HITS: 1", ""
        )
        self.record(self.memory_entry(), self.plan_entry(), incomplete)
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("CORPUS-SIZE", result.report)
        self.assertIn("HITS", result.report)

    def test_a_service_opened_item_needs_payload_text_for_the_gate_to_hash(self) -> None:
        self.complete_record()
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("thought-17", result.report)

    def test_a_prior_digest_never_substitutes_for_returned_service_text(self) -> None:
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

        result = self.write(payloads={})

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no returned text", result.report)

    def test_a_service_url_is_refused_in_the_registry(self) -> None:
        self.registry.write_text(
            self.registry.read_text(encoding="utf-8").replace(
                "SERVICE: open-brain", "SERVICE: https://credential.example/mcp"
            ),
            encoding="utf-8",
        )
        self.complete_record()
        result = self.write()
        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("credential.example", result.report)

    def test_one_off_search_is_owed_and_its_terms_must_match(self) -> None:
        extra = self.root / "extra"
        extra.mkdir()
        note = extra / "note.md"
        note.write_text("synthetic context\n", encoding="utf-8")
        extra_entry = "\n".join(
            (
                f"## PLACE: {extra}",
                "STATE: searched",
                f"ROOT: {extra}",
                "TERMS: rural access",
                "EXAMINED: 1",
                "UNREADABLE: 0",
                f"OPENED: {note}",
            )
        )
        self.record(
            self.memory_entry(),
            self.plan_entry(),
            self.service_entry(),
            extra_entry,
            header=(f'PROJECT-SEARCH: {extra} - "rural access"',),
        )
        self.assertEqual(self.write().exit_code, 0)

        text = self.run.joinpath(context.RECORD_NAME).read_text(encoding="utf-8")
        self.run.joinpath(context.RECORD_NAME).write_text(
            text.replace("TERMS: rural access", "TERMS: another topic"), encoding="utf-8"
        )
        self.assertEqual(self.write().exit_code, 1)

    def test_unreadable_and_absent_places_need_confirmed_waivers(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        self.record(self.memory_entry(), self.plan_entry(), failed)
        self.assertEqual(self.write(payloads={}).exit_code, 1)

        self.record(
            self.memory_entry(),
            self.plan_entry(),
            failed,
            header=(
                "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23; "
                "proceed without, per the clinician",
            ),
        )
        result = self.write(payloads={})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.waived, 1)
        self.assertIn("waived places: 1", result.report)

    def test_a_waiver_needs_a_date_and_the_clinician_attestation(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        for waiver in (
            "PROJECT-WAIVE: open-brain - service unavailable; proceed without, per the clinician",
            "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23",
            "PROJECT-WAIVE: open-brain - service unavailable on 2026-99-99; proceed without, per the clinician",
            "PROJECT-WAIVE: open-brain - 2026-09-23; proceed without, per the clinician",
        ):
            with self.subTest(waiver=waiver):
                self.record(self.memory_entry(), self.plan_entry(), failed, header=(waiver,))
                self.assertEqual(self.write(payloads={}).exit_code, 1)


class CompletionRechecksFileItems(ProjectContextFixture):
    def setUp(self) -> None:
        super().setUp()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

    def test_an_unchanged_record_is_clean(self) -> None:
        result = self.complete()
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)

    def test_a_location_cannot_suppress_rehashing_with_service_metadata(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        marker = f"## PLACE: {self.location}\nSTATE: searched\n"
        record.write_text(
            text.replace(marker, marker + "CORPUS-SIZE: 1\n"), encoding="utf-8"
        )
        self.plan.write_text("changed plan\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_a_hashed_location_cannot_be_relabeled_unreadable_to_suppress_rehashing(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        marker = f"## PLACE: {self.location}\nSTATE: searched\n"
        text = text.replace(
            "CONFIRMED: 2001-01-01\n",
            "PROJECT-WAIVE: "
            f"{self.location} - file unavailable on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2001-01-01\n",
        ).replace(marker, f"## PLACE: {self.location}\nSTATE: unreadable\nDETAIL: moved\n")
        record.write_text(text, encoding="utf-8")
        self.plan.write_text("changed plan\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_a_waiver_for_a_readable_place_is_a_finding_and_not_counted(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8").replace(
            "CONFIRMED: 2001-01-01\n",
            "PROJECT-WAIVE: "
            f"{self.memory} - stale lead on 2026-09-23; "
            "proceed without, per the clinician\nCONFIRMED: 2001-01-01\n",
        )
        record.write_text(text, encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertIn("waived places: 0", result.report)

    def test_a_changed_file_is_exit_two_coverage(self) -> None:
        self.plan.write_text("changed plan\n", encoding="utf-8")
        result = self.complete()
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("file item moved", result.report)

    def test_a_missing_record_is_a_finding_only_at_completion(self) -> None:
        self.run.joinpath(context.RECORD_NAME).unlink()
        result = self.complete()
        self.assertTrue(result.finding)
        early = self.complete(None)
        self.assertFalse(early.finding)
        self.assertIn("not graded", early.report)

    def test_a_record_tamper_is_a_finding_and_wins_over_file_drift(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        record.write_text(
            record.read_text(encoding="utf-8").replace(
                "CONTEXT-DIGEST: ", "CONTEXT-DIGEST: " + "0" * 64 + " # "
            ),
            encoding="utf-8",
        )
        self.plan.write_text("changed plan\n", encoding="utf-8")
        result = self.complete()
        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_deleting_an_owed_entry_after_the_gate_is_a_finding(self) -> None:
        record = self.run.joinpath(context.RECORD_NAME)
        text = record.read_text(encoding="utf-8")
        record.write_text(text.split(f"\n## PLACE: {self.location}", 1)[0] + "\n", encoding="utf-8")

        result = self.complete()

        self.assertTrue(result.finding)
        self.assertIn("record shape is invalid", result.report)

    def test_service_items_are_not_retrieved_again_at_completion(self) -> None:
        result = self.complete()
        self.assertNotIn("service", result.report.casefold())

    def test_completion_reports_the_waived_place_count(self) -> None:
        failed = "\n".join(
            (
                "## PLACE: open-brain",
                "STATE: unreadable",
                "DETAIL: service unavailable at retrieval",
            )
        )
        self.record(
            self.memory_entry(),
            self.plan_entry(),
            failed,
            header=(
                "PROJECT-WAIVE: open-brain - service unavailable on 2026-09-23; "
                "proceed without, per the clinician",
            ),
        )
        self.assertEqual(self.write(payloads={}).exit_code, 0)

        result = self.complete()

        self.assertIn("waived places: 1", result.report)

    def test_shared_adapter_preserves_finding_precedence(self) -> None:
        self.run.joinpath(context.RECORD_NAME).unlink()
        base = run_grader.Grade(scan=object(), source=str(self.run))
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            result = context.apply_completion_gate(base, self.run, "submission")
        self.assertTrue(result.findings_failed)
        self.assertIn("record is missing", result.reports[-1])


class GoAheadRechecks(ProjectContextFixture):
    def setUp(self):
        super().setUp()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)

    def check(self, key="submission"):
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            return context.go_ahead(self.run, key, approval_revision=1)

    def record_posting(self, *, required=True):
        # A pre-check durable record uses the historical public reader contract.
        (self.run / approval_record.RECORD).write_text(json.dumps({
            "items": [{"skill": "discussion-post", "submission": "submission",
                       "posting_route": "agent", "project_context_check": required,
                       "approval_revision": 1}]
        }), encoding="utf-8")

    def test_an_added_memory_line_is_shown_without_moving_the_index(self):
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        original_digest = context.recorded_digest(self.run)
        self.memory.write_text("memory index\nnew pointer\n", encoding="utf-8")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            result = context.go_ahead(self.run, "submission")
        self.assertFalse(result.coverage, result.report)
        self.assertFalse(result.finding, result.report)
        self.assertIn("new pointer", result.report)
        self.assertEqual(original_digest, context.recorded_digest(self.run))

    def test_edited_and_removed_memory_lines_each_move(self):
        for text in ("edited pointer\n", ""):
            with self.subTest(text=text):
                self.memory.write_text(text, encoding="utf-8")
                result = self.check()
                self.assertTrue(result.coverage, result.report)
                self.assertIn(str(self.memory), result.report)

    def test_every_subject_list_is_read_as_part_of_the_index(self):
        # ADR 0391 ruling 8: a memory edited or retired under a subject still moves.
        listing = self.memory.parent / "subjects" / "canvas.md"
        listing.parent.mkdir()
        listing.write_text("# Canvas\n\n- [A](../a.md) — first\n", encoding="utf-8")
        self.assertEqual(self.write().exit_code, 0)
        self.assertFalse(self.check().coverage)
        listing.write_text("# Canvas\n\n- [A](../a.md) — first\n- [B](../b.md) — second\n", encoding="utf-8")
        result = self.check()
        self.assertFalse(result.coverage, result.report)
        self.assertIn("[B](../b.md)", result.report)
        listing.write_text("# Canvas\n\n- [B](../b.md) — second\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)

    def test_reordering_whitespace_and_blank_lines_do_not_move_but_duplicate_loss_does(self):
        self.memory.write_text("first\nsecond\nfirst\n", encoding="utf-8")
        self.assertEqual(self.write().exit_code, 0)
        self.memory.write_text("second  \n\nfirst\nfirst\n", encoding="utf-8")
        self.assertFalse(self.check().coverage)
        self.memory.write_text("second\nfirst\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)

    def test_a_moved_planning_file_is_named_and_reapproval_replaces_only_its_key(self):
        self.check("another")
        self.plan.write_text("changed plan\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)
        self.plan.write_bytes(b"atlas plan\n")
        self.assertFalse(self.check().coverage)
        text = (self.run / context.RECORD_NAME).read_text(encoding="utf-8")
        rows = [json.loads(line.split(": ", 1)[1]) for line in text.splitlines() if line.startswith("GO-AHEAD:")]
        self.assertEqual({row["submission"] for row in rows}, {"submission", "another"})
        self.assertEqual(len(rows), 2)

    def test_posted_clean_result_is_carried_forward_without_reading_current_files(self):
        self.assertFalse(self.check().coverage)
        self.record_posting()
        self.plan.unlink()
        self.memory.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("carried forward", result.report)

    def test_posted_result_is_not_rebound_when_a_reply_refreshes_context(self):
        self.check()
        self.record_posting()
        self.memory.write_text("memory index\na later session's pointer\n", encoding="utf-8")
        self.assertEqual(0, self.write().exit_code)
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("carried forward", result.report)

    def test_posted_move_is_reported_as_approved_over_and_passes(self):
        self.plan.write_text("changed plan\n", encoding="utf-8")
        self.assertTrue(self.check().coverage)
        self.record_posting()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("clinician approved over moved places", result.report)
        self.assertIn(str(self.plan), result.report)

    def test_pre_check_posted_approval_is_named_counted_and_passes(self):
        self.record_posting(required=False)
        self.plan.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("approval predates the check", result.report)
        self.assertIn("pre-check approvals: 1", result.report)

    def test_new_posted_approval_cannot_use_the_pre_check_exemption(self):
        self.record_posting()
        self.assertTrue(self.complete().finding)

    def test_unposted_terminal_grade_keeps_whole_file_rechecking(self):
        self.check()
        self.memory.write_text("memory index\nnew pointer\n", encoding="utf-8")
        self.assertTrue(self.complete().coverage)

    def test_corrupt_saved_result_is_a_finding(self):
        self.check()
        path = self.run / context.RECORD_NAME
        path.write_text(path.read_text(encoding="utf-8").replace('"finding": false', '"finding": "false"'), encoding="utf-8")
        self.record_posting()
        self.assertTrue(self.complete().finding)

    def test_a_later_notice_preserves_the_result_approved_before_posting(self):
        self.check()
        self.record_posting()
        before = (self.run / context.RECORD_NAME).read_bytes()
        self.plan.write_bytes(b"changed after posting\n")
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), redirect_stdout(output):
            status = context.main([str(self.run), "--go-ahead", "submission"])
        self.assertEqual(status, 2)
        self.assertIn(str(self.plan), output.getvalue())
        self.assertEqual(before, (self.run / context.RECORD_NAME).read_bytes())
        result = self.complete()
        self.assertFalse(result.coverage, result.report)
        self.assertNotIn("approved over moved", result.report)
        with self.assertRaisesRegex(ValueError, "new approval revision"):
            context.go_ahead(self.run, "submission")

    def test_a_result_for_an_unrecorded_approval_revision_cannot_clear_a_move(self):
        self.check()
        self.record_posting()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry):
            context.go_ahead(self.run, "submission", approval_revision=2)
        result = self.complete()
        self.assertTrue(result.finding, result.report)
        self.assertIn("approval revision differs", result.report)

    def test_public_go_ahead_command_prints_every_added_line_and_exits_zero(self):
        self.memory.write_text("memory index\nnew pointer\nsecond pointer\n", encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), redirect_stdout(output):
            status = context.main([str(self.run), "--go-ahead", "submission"])
        self.assertEqual(status, 0, output.getvalue())
        self.assertIn("new pointer", output.getvalue())
        self.assertIn("second pointer", output.getvalue())

    def test_real_pre_post_grader_records_an_approved_move_as_incomplete(self):
        Run(self.run, posted=False)
        (self.run / "reread.md").unlink()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        claims = self.run / "heading-read.md"
        claims.write_text(claims.read_text(encoding="utf-8").replace("e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf", context.recorded_digest(self.run)), encoding="utf-8")
        # A concurrent writer moves the plan after the real pre-post read and
        # before the go-ahead recheck. A pre-read edit instead breaks the heading
        # read under ADR 0346 (covered in test_heading_context_history).
        actual_run = approval_record.subprocess.run
        def move_after_read(*args, **kwargs):
            result = actual_run(*args, **kwargs)
            if len(args[0]) > 1 and str(args[0][1]).endswith("discussion_reply_scan.py"):
                self.plan.write_bytes(b"changed plan\n")
            return result
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(
            approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)
        ), mock.patch.object(approval_record, "verify_shown_text", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)), mock.patch.object(approval_record.reader_remarks, "verify", return_value=[]), mock.patch.object(approval_record.subprocess, "run", side_effect=move_after_read):
            approved = approval_record.approve(
                self.run, skill="discussion-reply", submission="submission",
                sources=(self.run / "response-maren.md",), grader_args=(str(self.run),),
                content_approved=True, clinician_reply="Approve over the changed plan.",
            )
        payload = json.loads((self.run / approval_record.RECORD).read_text(encoding="utf-8"))
        self.assertEqual(payload["items"][0]["pregrade_status"], "incomplete")
        self.assertIn(str(self.plan), approved.pregrade_report)
        approval_record.record_agent_posting(self.run, skill="discussion-reply", submission="submission")
        self.memory.unlink()
        self.assertFalse(self.complete().coverage)
        self.assertFalse(self.complete().finding)

    def test_approval_refuses_when_the_go_ahead_result_cannot_be_written(self):
        Run(self.run, posted=False)
        (self.run / "reread.md").unlink()
        self.complete_record()
        self.assertEqual(self.write().exit_code, 0)
        claims = self.run / "heading-read.md"
        claims.write_text(claims.read_text(encoding="utf-8").replace("e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf", context.recorded_digest(self.run)), encoding="utf-8")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(Path, "replace", side_effect=OSError("synthetic write failure")), mock.patch.object(approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)), mock.patch.object(approval_record, "verify_shown_text", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0)), mock.patch.object(approval_record.reader_remarks, "verify", return_value=[]):
            with self.assertRaisesRegex(approval_record.ApprovalRecordError, "could not be written"):
                approval_record.approve(self.run, skill="discussion-reply", submission="submission", sources=(self.run / "response-maren.md",), grader_args=(str(self.run),), content_approved=True, clinician_reply="Approve the synthetic reply.")
        self.assertFalse((self.run / approval_record.RECORD).exists())

    def test_assignment_approval_and_upload_carry_forward_the_same_check(self):
        from test_assignment_bar import DECK_BAR
        (self.run / "bar.md").write_text(DECK_BAR, encoding="utf-8")
        artifact = self.run / "submission.pptx"
        artifact.write_bytes(b"synthetic deck")
        self.plan.write_bytes(b"changed plan\n")
        with mock.patch.object(repo_root, "project_registry", return_value=self.registry), mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), mock.patch.object(approval_record, "verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 4102444800)), mock.patch.object(assignment_submission.reader_remarks, "verify", return_value=[]):
            staged = assignment_submission.stage(self.run, artifact, artifact_approved=True, clinician_reply="Approve the synthetic artifact.")
        payload = json.loads((self.run / assignment_submission.RECORD).read_text(encoding="utf-8"))
        self.assertEqual(payload["pregrade_status"], "incomplete")
        assignment_submission.confirm(staged, uploaded_carriers=(artifact,), final_confirmation=True)
        self.plan.unlink()
        result = self.complete()
        self.assertFalse(result.finding, result.report)
        self.assertFalse(result.coverage, result.report)
        self.assertIn("approved over", result.report)


class ScopedCompletionGraders(unittest.TestCase):
    def test_the_scoped_completion_graders_declare_the_same_row(self) -> None:
        self.assertEqual(
            set(context.COMPLETION_GRADERS),
            {
                "course-assignment",
                "discussion-post",
                "discussion-reply",
                "peer-critique",
                "practicum-case-study",
            },
        )
        for skill, module_name in context.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                self.assertIn(context.EXPECTED_ROW, module.EXPECTED_COMPLETION_CHECKS)

    def test_each_scoped_skill_runs_the_gate_before_drafting(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for skill in context.COMPLETION_GRADERS:
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("project_context.py", text)
                self.assertIn("--write", text)
                self.assertIn("--submission", text)

    def test_graders_and_claude_name_one_limits_object_without_copying_rows(self) -> None:
        root = Path(__file__).resolve().parent.parent
        readers = [
            root / "tools" / f"{module_name}.py"
            for module_name in context.COMPLETION_GRADERS.values()
        ]
        readers.append(root / "CLAUDE.md")
        readers.append(root / "skills" / "_shared" / "reference" / "sourcing.md")
        for path in readers:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("project_context.DECLARED_LIMITS", text)
                for key, reason in context.DECLARED_LIMITS:
                    if path.name != "sourcing.md":
                        self.assertNotIn(key, text)
                    self.assertNotIn(reason, text)

    def test_the_shared_draft_rule_points_at_an_existing_limits_row(self) -> None:
        root = Path(__file__).resolve().parent.parent
        text = (root / "skills" / "_shared" / "reference" / "sourcing.md").read_text(
            encoding="utf-8"
        )
        keys = dict(context.DECLARED_LIMITS)
        self.assertIn("agreement-is-a-reading", keys)
        self.assertIn("agreement-inherits-item-errors", keys)
        self.assertIn(
            "`project_context.DECLARED_LIMITS`, row `agreement-inherits-item-errors`", text
        )


if __name__ == "__main__":
    unittest.main()
