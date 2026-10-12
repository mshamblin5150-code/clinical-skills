"""Public-command regressions for proposed-image working annotations. #1559.

All artifacts are synthetic; no clinician or patient is represented.
phi-scan: synthetic
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest import mock

import assignment_docx
import assignment_docx_scan
import course_assignment_scan
import deck_scan
import discussion_artifact
import discussion_post_scan
import discussion_reply_scan
import peer_critique_scan
from test_assignment_docx_scan import empty_population_input as docx_input
from test_deck_scan import Run as DeckRun, slide_xml
from test_discussion_post_scan import Run as PostRun
from test_discussion_reply_scan import Run as ReplyRun
from test_peer_critique_scan import FILLER, build_run


ROOT = Path(__file__).resolve().parents[1]


def example_key() -> str:
    """Read the documented envelope rather than copying its example key."""
    sheet = ROOT / "skills/_shared/reference/imagery-proposals.md"
    fences = re.findall(r"```json\s*\n(.*?)\n```", sheet.read_text(encoding="utf-8"), re.S)
    envelopes = [json.loads(fence) for fence in fences]
    return next(value["proposals"][0]["key"] for value in envelopes if "proposals" in value)


def marked(text: str, marker: str, placement: str) -> str:
    """Insert before prose and its later citations, preserving the real words."""
    if placement == "own-line":
        return "\n" + marker + "\n" + text
    if placement == "inline":
        first, rest = text.split(" ", 1)
        return first + " " + marker + " " + rest
    return text


def refresh_heading(run: Path, artifact: Path) -> None:
    path = run / "heading-read.md"
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    path.write_text(
        re.sub(r"(?m)^DRAFT:.*$", f"DRAFT: {digest}", path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


class ProposedImageWorkingMarkers(unittest.TestCase):
    def setUp(self) -> None:
        self.key = example_key()
        self.digits = re.findall(r"\d+", self.key)
        self.assertTrue(self.digits, "The documented example must exercise a numeric key.")
        self.marker = f"[[PROPOSED IMAGE {self.key}]]"

    def assert_marker_present(self, artifact: Path, placement: str) -> None:
        if artifact.suffix == ".md":
            text = artifact.read_text(encoding="utf-8")
        else:
            with zipfile.ZipFile(artifact) as archive:
                text = "\n".join(
                    archive.read(name).decode("utf-8")
                    for name in archive.namelist()
                    if name.endswith(".xml")
                )
        if placement == "baseline":
            self.assertNotIn(self.marker, text)
        else:
            self.assertIn(self.marker, text)

    def prepare(self, root: Path, target: str, placement: str):
        root.mkdir()
        if target == "post":
            run = PostRun(root)
            text = run.draft.read_text(encoding="utf-8")
            text = text.replace("Access becomes meaningful", marked("Access becomes meaningful", self.marker, placement), 1)
            run.draft.write_text(text, encoding="utf-8")
            run.write_heading_read()
            self.assert_marker_present(run.draft, placement)
            return discussion_post_scan, [str(root), "--draft", str(run.draft)], "words:"
        if target == "reply":
            run = ReplyRun(root, posted=False)
            path = root / "response-maren.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("your distinction", marked("your distinction", self.marker, placement), 1)
            path.write_text(text, encoding="utf-8")
            run.write_heading_read()
            run.refresh_fingerprint()
            self.assert_marker_present(path, placement)
            return discussion_reply_scan, [str(root)], "words:"
        if target == "peer":
            build_run(root=root, filler=marked(FILLER, self.marker, placement), reread=None, posted=False)
            self.assert_marker_present(root / "critique.md", placement)
            return peer_critique_scan, [str(root)], "words:"
        if target in {"deck", "dispatch-deck"}:
            run = DeckRun(root)
            text = marked("Synthetic explanation remains supported", self.marker, placement)
            # Separate paragraphs model an own-line marker on a slide.
            run.write_deck((slide_xml("Synthetic title", *text.splitlines()),))
            run.retain(1, 1)
            run.write_rendered()
            run.write_adversarial()
            run.write_intent()
            self.assert_marker_present(run.deck, placement)
            if target == "dispatch-deck":
                return course_assignment_scan, [str(root), "--artifact", str(run.deck)], "words read"
            return deck_scan, [str(root), "--pptx", str(run.deck)], "words read"
        inputs = docx_input(root)
        run, artifact = Path(inputs.argv[0]), Path(inputs.argv[2])
        text = marked("Synthetic explanation remains supported.", self.marker, placement)
        spec = replace(
            assignment_docx.fixture_spec(),
            sections=(assignment_docx.Section("Purpose", tuple(text.splitlines())),),
            command_rows=(),
            figure_image="",
        )
        assignment_docx.build(spec, artifact, force=True)
        refresh_heading(run, artifact)
        self.assert_marker_present(artifact, placement)
        if target == "dispatch-docx":
            return course_assignment_scan, [str(run), "--artifact", str(artifact)], "body words"
        return assignment_docx_scan, list(inputs.argv), "body words"

    def command(self, module, argv: list[str]) -> str:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            module.main([*argv, "--show"])
        # An incomplete posting row may exit 2 after the artifact was graded.
        # Minimal synthetic packages may need review after successful loading;
        # a source-loading error must still fail, as must a missing count report.
        self.assertIn(
            stderr.getvalue(),
            ("", "deck findings require review\n", "DOCX findings require review\n"),
            stdout.getvalue() + stderr.getvalue(),
        )
        self.assertTrue(stdout.getvalue(), "The public command produced no report.")
        return stdout.getvalue()

    def word_count(self, report: str, label: str) -> int:
        match = re.search(r"(?m)^\s*" + re.escape(label) + r"\s+(\d+)(?:\s+\([^\n]*\))?\s*$", report)
        self.assertIsNotNone(match, report)
        return int(match.group(1))

    def check_target(self, target: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            module, argv, label = self.prepare(root / "baseline", target, "baseline")
            baseline = self.command(module, argv)
            baseline_words = self.word_count(baseline, label)
            for placement in ("own-line", "inline"):
                with self.subTest(target=target, placement=placement):
                    module, argv, label = self.prepare(root / placement, target, placement)
                    report = self.command(module, argv)
                    self.assertEqual(baseline_words, self.word_count(report, label), report)
                    finding_pattern = (
                        r"(?m)^\s*untraced-(?:number|figure):.*?\b"
                        + re.escape(self.digits[0])
                        + r"\b.*(?:absent from claims\.md|has no claim record)"
                    )
                    self.assertNotRegex(report, finding_pattern)
                    # Only disable the owner's imported marker cleanup. All
                    # other annotation and citation handling stays active.
                    with mock.patch.object(discussion_artifact, "WORKING_MARKER", re.compile(r"(?!)")):
                        control = self.command(module, argv)
                    self.assertRegex(control, finding_pattern)

    def test_discussion_post_command(self) -> None:
        self.check_target("post")

    def test_discussion_reply_command(self) -> None:
        self.check_target("reply")

    def test_peer_critique_command(self) -> None:
        self.check_target("peer")

    def test_deck_command(self) -> None:
        self.check_target("deck")

    def test_assignment_docx_command(self) -> None:
        self.check_target("docx")

    def test_course_assignment_dispatches_deck(self) -> None:
        self.check_target("dispatch-deck")

    def test_course_assignment_dispatches_docx(self) -> None:
        self.check_target("dispatch-docx")


if __name__ == "__main__":
    unittest.main()
