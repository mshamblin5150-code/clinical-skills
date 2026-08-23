"""Every claim that ``fixtures/filled-anchor/notes/`` is a run record says what was edited.

[#221](https://github.com/mshamblin5150-code/clinical-skills/issues/221). The set
is day-b run 1 **apart from two site names**, redacted to ``[SITE-A]`` and
``[SITE-B]`` in nine of the twelve by ``c0ff261`` -- and the unqualified form was
written across a dozen committed files, with the exception stated in exactly one
of them. A reader who opens ``AGENTS.md`` or ``CLAUDE.md`` learned the set was
unedited and had no path to the exception.

**The surface this repaired was 16 blocks in 12 files**, plus 2 more the check
cannot reach, measured here on 2026-08-19 by running the predicate below over the
pre-change tree. **Nothing re-derives that now** and it is stated in this one
place for exactly that reason: it is a fact about a tree that no longer exists,
the check's own answer today is zero, and a figure like that copied into
``CLAUDE.md`` needed mental subtraction the moment the section explaining it
became another block about the set. **The nine-of-twelve below is the opposite
case** -- it is a fact about the notes, so it is re-derived rather than restated,
and the command that does it lives in the set's README.

**Nothing downstream turns on it**, which is why it survived: the edit is a
two-token swap inside one ``Primary Payment Method`` row and no figure anyone
cites moves. What it is, is one claim in many places with one of them corrected,
and **the corrected copy is the one nobody reads first**.

**A check rather than a sweep, because the claim is cheap to restate.** #221's
own decision 3 asks whether the durable fix is a test, and the shape answers it:
a surface this wide across two file types, one of them a console string, is not
something anyone re-qualifies by hand and keeps qualified. This is the
``spelling_scan``-versus-standing-rule-4 arrangement again.

**The instrument is why the surface kept growing, and that is #221's own thesis
arriving on the ticket that filed it.** The body counted five files by grepping
one spelling of the phrase in one file type; a comment re-derived fifteen with
``git grep -ln``. Both undercount, because a ``git grep`` for the phrase cannot
see it **wrapped across a line** -- ``tools/test_filled_vitals_census.py`` opens
with *"day-b run 1, byte for"* then *"byte"* on the next -- and cannot see it
**split across two string literals**, which is how ``spelling_scan.py`` prints it
to stdout. So the comparison here is against a whitespace-and-quote-normalized
block, not against a line.

**A block is contiguous non-blank lines**, which is a Markdown paragraph and a
wrapped docstring or comment run alike. That unit is ``block_scan.py``'s
entry-versus-wrap reading, borrowed for a smaller job.

**This module is exempt by path, and that is not a self-exemption.** The
positive-case fixtures in ``TheInstrumentIsLive`` are bare claims on purpose --
a detector that could not hold its own uncorrected example would be untestable --
so ``tracked_prose`` drops this one file by resolved path. The distinction from
``phi_scan``'s hole, which ``README.md`` and ``phi_scan.py`` both fell into by
mentioning its pragma near the top, is that **nothing here can be exempted by
saying so in the text**: the path is a constant in the walker, and the docstring
you are reading is graded by ``TheDefiningModuleQualifiesItsOwnProse``.

**It shipped red for one commit's worth of time and the reason is worth keeping.**
The suite passed at 1455 while this file was **untracked** -- ``git ls-files
--cached`` could not see it, so the walk skipped the fixtures without anyone
choosing to. ``git add`` turned the same tree red. That is
[#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the
merge is the unguarded moment* arriving one step earlier: **a check that walks
the index is blind to the file being added in the same change**, and the local
run that proves it green is the one taken before staging.

## What this cannot reach

**A block that makes the claim and names the set nowhere in itself is invisible.**
Two existed when this was written -- ``skills/clinical-note/SKILL.md``'s *"that
set is a byte-for-byte record"* and ``test_spelling_scan.py``'s *"it is a
byte-for-byte record of"*, neither naming ``filled-anchor``, ``day-b`` or the
redacted site names -- and both were rewritten to name what they are about, so
the limit is real and has no live instance. It is the price of the subject test:
without one, every ``.docx`` round-trip paragraph and ``threshold_sheet.py``'s
*"byte for byte what a clean coverage pass prints"* would be graded as a claim
about a fixture directory.

**And the qualifier is a vocabulary rather than a sentence.** A block mentioning
site names for an unrelated reason while making the bare claim would pass. That
is a false negative rather than a false alarm, which is the safe direction here,
and asserting a paragraph verbatim is what ``test_skill_agreement.py`` says
teaches the next session to delete the test.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"
NOTES_README = NOTES / "README.md"

#: The claim, both spellings. Matched against a normalized block, never a line.
CLAIM = re.compile(r"byte[ -]for[ -]byte", re.IGNORECASE)

#: Names the preserved set. A block that names neither is about something else --
#: a ``.docx`` round trip, a duplicated day file, a printed report.
#:
#: **A bare ``run 1`` was in here and had to come out.** It matched
#: ``test_differential_scan.py``'s *"hedged-dx run 1's case 2 ... it is a
#: byte-for-byte run record"*, which is a **different** set: ``fixtures/hedged-dx/``
#: commits no notes at all, so no site name was ever redacted from it and the
#: claim there is true as written. Every real site names ``filled-anchor`` or
#: ``day-b`` in its own block, checked rather than assumed, so nothing is lost.
SUBJECT = re.compile(r"filled-anchor|day-b", re.IGNORECASE)

#: Any one of these is the exception, stated. Deliberately a vocabulary: the
#: sites word it differently on purpose and a verbatim pin would fail on every
#: rewrite.
EXCEPTION = re.compile(r"SITE-A|SITE-B|site name|site-name|redact|notes/README", re.IGNORECASE)

#: Quotes, comment marks and emphasis are glue between the words of the claim,
#: not part of it. Stripping them is what lets a split string literal and a
#: hard-wrapped docstring be read as the sentence a reader hears.
#:
#: **A backslash was in this set and came out.** It changed nothing on the real
#: corpus -- measured both ways over every tracked ``.md`` and ``.py``, same
#: result -- while quietly turning a literal ``\n`` into an ``n`` mid-sentence.
#: A transform that alters text and buys nothing is an escape route nobody
#: declared, which is what a review called it.
PROSE_MARK = re.compile(r"[\"'#>*`]")

#: This module, dropped from the walk by resolved path. See the docstring: its
#: fixtures are bare claims on purpose and a path constant cannot be talked into
#: existing by the file it exempts.
SELF = Path(__file__).resolve()


def normalized(block: str) -> str:
    return re.sub(r"\s+", " ", PROSE_MARK.sub(" ", block)).strip()


def blocks(text: str) -> list[tuple[int, str]]:
    """Contiguous non-blank lines, each with its 1-indexed first line number."""
    found: list[tuple[int, str]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        end = index
        while end < len(lines) and lines[end].strip():
            end += 1
        found.append((index + 1, "\n".join(lines[index:end])))
        index = end
    return found


def bare_claim_lines(text: str) -> list[int]:
    """First line of each block claiming the set is a run record without the exception."""
    return [
        line
        for line, block in blocks(text)
        for shape in [normalized(block)]
        if CLAIM.search(shape) and SUBJECT.search(shape) and not EXCEPTION.search(shape)
    ]


def tracked_prose() -> list[Path]:
    """Tracked ``.md`` and ``.py``, which is the whole of what a clean result covers.

    [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254).
    ``git ls-files`` is the index, so an untracked file is not in it, and the
    honest form of a clean run of ``EveryClaimCarriesTheException`` is *no
    tracked file states the claim bare*.

    **This module holds the worked instance of its own blind spot**, and the
    docstring above tells it: the suite passed at 1455 while this file was
    untracked, and ``git add`` turned the same tree red. The statement here is
    the part that was missing -- the incident was recorded and the walk still
    reported like a tree-wide negative.

    **The window stays open, which is #254's ruling rather than an omission.**
    Widening this to ``--others --exclude-standard`` was priced and declined; a
    file written this session is graded after it is staged, by CI at push, and
    by the next local run.
    """
    finished = subprocess.run(
        ["git", "ls-files", "--cached", "--", "*.md", "*.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    paths = [REPO_ROOT / line for line in finished.stdout.splitlines() if line.strip()]
    return [path for path in paths if path.resolve() != SELF]


class TheInstrumentIsLive(unittest.TestCase):
    """A detector that matched nothing would pass every assertion below."""

    def test_a_bare_claim_is_caught(self) -> None:
        self.assertEqual(bare_claim_lines("These twelve are day-b run 1 byte for byte.\n"), [1])

    def test_the_exception_clears_it(self) -> None:
        self.assertEqual(
            bare_claim_lines("These twelve are day-b run 1 byte for byte, apart from two site names.\n"),
            [],
        )

    def test_a_claim_about_something_else_is_not_graded(self) -> None:
        """``.docx`` and ``threshold_sheet.py`` use the phrase about their own subjects."""
        for other in (
            "A .docx Word refuses to open is byte-for-byte indistinguishable from a good one.\n",
            "A gate that did not run printed 0 refusing, which is byte for byte\nwhat a clean pass prints.\n",
            "One day file in the clinician's catalog is on disk twice, byte for byte.\n",
        ):
            with self.subTest(other=other[:40]):
                self.assertEqual(bare_claim_lines(other), [])

    def test_a_hard_wrapped_claim_is_caught(self) -> None:
        """``git grep`` cannot see this one, and a real site is written this way."""
        self.assertEqual(bare_claim_lines("Those twelve notes are day-b run 1, byte for\nbyte.\n"), [1])

    def test_a_claim_split_across_string_literals_is_caught(self) -> None:
        """``spelling_scan.py`` prints the banner in two pieces, so grep misses it."""
        source = (
            "    lines = [\n"
            '        "day-b run 1, byte for "\n'
            '        "byte. Issue 73.",\n'
            "    ]\n"
        )
        self.assertEqual(bare_claim_lines(source), [1])

    def test_the_walk_reaches_the_repo(self) -> None:
        paths = tracked_prose()
        self.assertGreater(len(paths), 50, "git ls-files returned too little to be a checkout")
        self.assertIn(REPO_ROOT / "CLAUDE.md", paths)

    def test_the_walk_drops_this_module_and_only_this_module(self) -> None:
        """The exemption has to be narrow, and it has to actually be applied.

        It was declared and not wired for one round -- ``SELF`` existed, the
        docstring said the walk dropped it, and ``tracked_prose`` had no filter.
        The suite went red and the prose was false at the same time, which is why
        this asserts the behavior rather than the constant.
        """
        walked = tracked_prose()
        self.assertNotIn(SELF, [path.resolve() for path in walked])
        self.assertIn(REPO_ROOT / "tools" / "test_spelling_scan.py", walked)


class EveryClaimCarriesTheException(unittest.TestCase):
    def test_no_tracked_file_states_it_bare(self) -> None:
        offenders = [
            f"{path.relative_to(REPO_ROOT).as_posix()}:{line}"
            for path in tracked_prose()
            if path.exists()
            for line in bare_claim_lines(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(
            offenders,
            [],
            "these claim fixtures/filled-anchor/notes/ is a run record and do not say "
            "two site names were redacted from nine of the twelve: " + ", ".join(offenders),
        )


class TheDefiningModuleQualifiesItsOwnProse(unittest.TestCase):
    """The path exemption covers the fixtures, not the reasoning around them.

    Without this, exempting the file would buy exactly the self-exemption
    ``phi_scan`` was caught giving itself -- a file explaining a rule and thereby
    escaping it. The fixtures have to be bare; the docstring does not.
    """

    def test_the_module_docstring_carries_the_exception(self) -> None:
        self.assertIsNotNone(__doc__)
        self.assertEqual(bare_claim_lines(__doc__ or ""), [])


class TheExceptionIsStatedWhereTheRecordIs(unittest.TestCase):
    """The set's own README is what the other sites point at, so it has to hold it."""

    def test_the_readme_names_the_edit(self) -> None:
        text = NOTES_README.read_text(encoding="utf-8")
        self.assertIn("[SITE-A]", text)
        self.assertIn("[SITE-B]", text)

    def test_nine_of_the_twelve_re_derives_from_the_tree(self) -> None:
        """No ``git`` here on purpose -- CI checks out shallow and ``c0ff261`` is not in it.

        The figure the prose states is a fact about the notes, so the notes are
        what settles it.
        """
        cases = sorted(NOTES.glob("case-*.md"))
        self.assertEqual(len(cases), 12)
        redacted = [
            case
            for case in cases
            for text in [case.read_text(encoding="utf-8")]
            if "[SITE-A]" in text or "[SITE-B]" in text
        ]
        self.assertEqual(len(redacted), 9)

    def test_seven_of_the_nine_name_both_re_derives_from_the_tree(self) -> None:
        """``SITE-B`` means both only while every such note also names ``SITE-A``."""
        cases = sorted(NOTES.glob("case-*.md"))
        self.assertEqual(len(cases), 12)
        texts = {case: case.read_text(encoding="utf-8") for case in cases}
        site_a = {case for case, text in texts.items() if "[SITE-A]" in text}
        site_b = {case for case, text in texts.items() if "[SITE-B]" in text}

        self.assertEqual(len(site_b), 7)
        self.assertLessEqual(site_b, site_a)


if __name__ == "__main__":
    unittest.main()
