"""Own figures through the five public grader commands; all material is synthetic.

phi-scan: synthetic
"""

from __future__ import annotations

import hashlib
import importlib
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest import mock

import assignment_docx
import heading_read
from test_assignment_docx_scan import empty_population_input as docx_fixture
from test_deck_scan import Run as DeckRun, slide_xml
from test_discussion_post_scan import Run as PostRun
from test_discussion_reply_scan import Run as ReplyRun
from test_peer_critique_scan import empty_population_input as critique_fixture


CONTEXT_DIGEST = "e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf"
ITEM_ID = "planning.md"
CONSUMERS = (
    "assignment_docx_scan", "deck_scan", "discussion_post_scan",
    "discussion_reply_scan", "peer_critique_scan",
)


def reader_record(artifact: Path, lines: str = "", *, items: int = 0) -> str:
    return (
        f"## HEADING-READ: {artifact.name}\n"
        f"DRAFT: {hashlib.sha256(artifact.read_bytes()).hexdigest()}\n"
        "ROUTE: separate context\n"
        f"SENTENCES: 0 factual, 2 clinician's own, {items} item\n"
        f"{lines}"
        f"CONTEXT-DIGEST: {CONTEXT_DIGEST}\n"
        "CONTEXT-VERDICT: agrees\nVERDICT: clean\n"
    )


def fixture(name: str, root: Path, sentence: str) -> tuple[Path, Path, list[str]]:
    """Use existing synthetic producers, retaining real loading and grading."""
    if name == "assignment_docx_scan":
        case = docx_fixture(root)
        run, artifact = Path(case.argv[0]), Path(case.argv[2])
        spec = replace(
            assignment_docx.fixture_spec(),
            sections=(assignment_docx.Section("Review Plan", (sentence,)),),
            command_rows=(), figure_image="", references=(),
        )
        assignment_docx.build(spec, artifact, force=True)
        argv = list(case.argv)
    elif name == "deck_scan":
        deck = DeckRun(root)
        deck.write_deck((slide_xml("Review Plan", sentence),))
        run, artifact = root, deck.deck
        argv = [str(run), "--pptx", str(artifact)]
    elif name == "discussion_post_scan":
        post = PostRun(root)
        run, artifact = root, post.draft
        artifact.write_text(sentence + "\n\n## References\n", encoding="utf-8")
        argv = [str(run), "--draft", str(artifact)]
    elif name == "discussion_reply_scan":
        ReplyRun(root, posted=False)
        run, artifact = root, root / "response-maren.md"
        artifact.write_text("Maren,\n\n" + sentence + "\n\n**References**\n", encoding="utf-8")
        argv = [str(run)]
    else:
        case = critique_fixture(root)
        run, artifact = root, root / "critique.md"
        artifact.write_text("Maren,\n\n" + sentence + "\n\n**References**\n", encoding="utf-8")
        argv = list(case.argv)
    (run / "claims.md").write_text("DATE: 2026-10-12\n", encoding="utf-8")
    item = run / ITEM_ID
    item.write_text("The plan names a 90-day review.\n", encoding="utf-8")
    (run / "project-context.md").write_text(
        "PROJECT-CONTEXT: none - synthetic directed search\n"
        "OWN-SUBMISSION: none - no synthetic earlier work\n"
        "CASE-MATERIAL: none - no synthetic case\nCASE-RESEARCH: none - no synthetic research\n"
        "CONFIRMED: 2001-01-01\n"
        f"CONTEXT-DIGEST: {CONTEXT_DIGEST}\n## PLACE: {run}\nSTATE: read\nROOT: {run}\n"
        f"OPENED: {ITEM_ID} | SHA256: {hashlib.sha256(item.read_bytes()).hexdigest()}\n", encoding="utf-8")
    return run, artifact, argv


def command(name: str, argv: list[str]) -> str:
    stdout, stderr = io.StringIO(), io.StringIO()
    with (
        redirect_stdout(stdout), redirect_stderr(stderr),
    ):
        status = importlib.import_module(name).main([*argv, "--show"])
    if status not in (0, 1):
        raise AssertionError(f"{name}: command did not grade: {stderr.getvalue()}")
    return stdout.getvalue()


class OwnFiguresAtThePublicCommands(unittest.TestCase):
    def check_rows(self, lines: str, *, untraced: int, absent: int = 0,
                   items: int = 0, sentence: str = "I propose a 90-day review.",
                   other_artifact: bool = False) -> None:
        for name in CONSUMERS:
            with self.subTest(consumer=name), tempfile.TemporaryDirectory() as directory:
                run, artifact, argv = fixture(name, Path(directory), sentence)
                record = reader_record(artifact, lines, items=items)
                if other_artifact:
                    record = reader_record(artifact) + record.replace(
                        f"HEADING-READ: {artifact.name}", "HEADING-READ: other.md", 1
                    )
                (run / "heading-read.md").write_text(record, encoding="utf-8")
                output = command(name, argv)
                kind = "untraced-figure" if name == "deck_scan" else "untraced-number"
                self.assertRegex(output, rf"(?m)^{kind}: {untraced}$", output)
                self.assertRegex(output, rf"(?m)^{heading_read.OWN_FIGURE_ABSENT}: {absent}$", output)
                self.assertRegex(output, r"(?m)^heading-read-unopened-item: 0$", output)
                self.assertRegex(output, r"(?m)^heading-read-item-count: 0$", output)

    def test_a_plan_figure_needs_an_own_line(self):
        self.check_rows("", untraced=1)
        self.check_rows("OWN: review plan -> 90\n", untraced=0)

    def test_a_listed_own_figure_absent_from_the_artifact_is_reported(self):
        self.check_rows("OWN: review plan -> 90, 99\n", untraced=0, absent=1)

    def test_an_item_suffix_excuses_the_figure_and_matches_the_opened_item(self):
        self.check_rows('ITEM: review plan -> planning.md | rests on "90-day review" | figures 90\n', items=1, untraced=0)

    def test_a_listed_item_figure_absent_from_the_artifact_is_reported(self):
        self.check_rows('ITEM: review plan -> planning.md | rests on "90-day review" | figures 90, 99\n', items=1,
                        untraced=0, absent=1)

    def test_the_accepted_value_match_leak_includes_a_research_sentence(self):
        self.check_rows("OWN: review plan -> 90\n", untraced=0,
                        sentence="I propose a 90-day review. Research reports a 90-day recovery.")

    def test_other_artifacts_cannot_excuse_figures_or_add_absence_findings(self):
        self.check_rows("OWN: another artifact -> 90, 99\n", untraced=1,
                        other_artifact=True)


class OwnFigureReaderGrammar(unittest.TestCase):
    def test_both_forms_expose_the_same_numeric_grammar_and_filter_by_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "draft.md"
            artifact.write_text("Synthetic draft.\n", encoding="utf-8")
            text = reader_record(
                artifact,
                "OWN: proposed interval -> 90, 30, 12.5%, 1,200\n"
                "ITEM: prior interval -> planning.md | figures 45, 90\n",
                items=1,
            )
            record, = heading_read.read_records(text)
            expected = frozenset(("90", "30", "12.5%", "1,200", "45"))
            self.assertEqual(expected, record.own_figures)
            other = reader_record(artifact, "OWN: other -> 99\n").replace(
                "HEADING-READ: draft.md", "HEADING-READ: other.md", 1
            )
            self.assertEqual(expected, heading_read.own_figures(text + other, "draft.md"))
            self.assertEqual(frozenset(("99",)), heading_read.own_figures(text + other, "other.md"))
            self.assertEqual(frozenset(), heading_read.own_figures(text + other, "absent.md"))

    def test_quote_preserves_optional_figure_suffix_and_excuses_only_listed_values(self):
        with tempfile.TemporaryDirectory() as directory:
            run, artifact, _argv = fixture("discussion_post_scan", Path(directory), "Synthetic draft.")
            for suffix in ("", " | figures 90"):
                with self.subTest(suffix=suffix):
                    text = reader_record(artifact, f'ITEM: plan -> planning.md | rests on "90-day review"{suffix}\n', items=1)
                    binding = heading_read.Binding(
                        artifact.name, artifact.read_bytes(), (), CONTEXT_DIGEST,
                        as_of=date(2026, 10, 12), opened_items=(ITEM_ID,), context_run=run,
                    )
                    result = heading_read.scan(text, (binding,))
                    self.assertEqual((), result.findings)
                    expected = frozenset(("90",)) if suffix else frozenset()
                    self.assertEqual(expected, heading_read.own_figures(text, artifact.name))


if __name__ == "__main__":
    unittest.main()
