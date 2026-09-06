"""Pin the cross-file agreements [#90](https://github.com/mshamblin5150-code/clinical-skills/issues/90) settled.

**Every defect this file guards is one document contradicting another or naming
one that is not there**, which is the shape #90 turned out to be twice over. ``batch-shift``'s ``description`` said
the input was a pasted shift while the first third of the same file opened a PDF;
and ``setup-clinical-skills`` kept the unmapped-preceptor sentence
[#91](https://github.com/mshamblin5150-code/clinical-skills/pull/91) had already
retired in ``batch-shift``, so for four days two skills stated one rule at
different strengths.

**Different strengths, not opposite ones, and the distinction is the finding.**
The retired sentence -- *reported, never substituted* -- was **stricter** than
what replaced it, and both forbid an agent guessing a surname. What #91 separated
out was the clinician's own deliberate substitution, which the old wording swept
in alongside the guess. A reader of ``setup-clinical-skills`` alone would not have
done anything unsafe; they would have refused something that was not theirs to
refuse. **Calling it a contradiction overstates it**, and this paragraph said so
before a review caught it.

**A single-file reader cannot see either.** Both read as coherent on their own
page, which is why they survived a review that opened one file at a time and why
the check has to name pairs rather than rules.

There is nothing to run here and no scanner to keep parity with -- this is
``test_spelling_scan.py``'s *the scanner must not drift from the file a reader
opens*, with the second reader being another Markdown file rather than a tool.

**Substrings, deliberately, and phrased as the ruling rather than as the
sentence.** A test asserting a paragraph verbatim fails on every rewrite and
teaches the next session to delete it; these assert the load-bearing clause, so
the prose around them stays free.

**One class here is not a named pair, and it is the reason the file grew a
walker.** [#233](https://github.com/mshamblin5150-code/clinical-skills/issues/233)
is the same defect with the second document unknown in advance: a skill's steps
are numbered headings and other files cite them **by number**, so inserting a
step silently redirects every citation. The pairs above are enumerated because
somebody noticed them; this one cannot be, because the whole point is that
nobody notices. So ``EveryCitedStepResolvesToADeclaredStep`` walks the tracked
tree instead of naming files, and the ruling it asserts -- *a cited step
exists* -- is the one thing about a cross-reference that holds without reading
either end.
"""

from __future__ import annotations

import posixpath
import re
import subprocess
import unittest
from pathlib import Path
from typing import Callable, Iterator, NamedTuple

from prose_bind import ProseBind, normalized

REPO_ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SKILLS_DIR = REPO_ROOT / "skills"
BATCH_SHIFT = REPO_ROOT / "skills" / "batch-shift" / "SKILL.md"
CLINICAL_NOTE = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
ICD10_CPT = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
FILLED_ANCHOR_ASSERTIONS = REPO_ROOT / "fixtures" / "filled-anchor" / "assertions.md"
FIXTURES_README = REPO_ROOT / "fixtures" / "README.md"
SETUP = REPO_ROOT / "skills" / "setup-clinical-skills" / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"
README = REPO_ROOT / "README.md"
MEDATRAX = REPO_ROOT / "reference" / "medatrax-fields.md"
DAY_A_ASSERTIONS = REPO_ROOT / "fixtures" / "day-a" / "assertions.md"
BLOCK_SCAN = REPO_ROOT / "tools" / "block_scan.py"
CASE_STUDY = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"
CASE_STUDY_STYLE = REPO_ROOT / "skills" / "_shared" / "reference" / "style.md"
CASE_STUDY_VOICE = REPO_ROOT / "skills" / "_shared" / "reference" / "voice.md"
DISCUSSION_POST = REPO_ROOT / "skills" / "discussion-post" / "SKILL.md"
DISCUSSION_REPLY = REPO_ROOT / "skills" / "discussion-reply" / "SKILL.md"
VOICE_CORPUS_REFERENCE = (
    REPO_ROOT / "skills" / "_shared" / "reference" / "voice-corpus.md"
)
VOICE_CORPUS_MODULE = REPO_ROOT / "tools" / "voice_corpus.py"
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"


class InferredAgeHasOnePrivateRecordAndPlainEntry(ProseBind, unittest.TestCase):
    """#158: fill the age, but never label the submitted values as guesses.

    The public seam is the note body plus the Medatrax field block.  Provenance
    belongs in ``FILLED·asserted``, which travels beside the note as the private
    review record; it is not copied into either submitted surface.
    """

    def test_clinical_note_keeps_age_provenance_out_of_medatrax(self):
        step_five = read(CLINICAL_NOTE).split("### 5. Emit the Medatrax entry", 1)[1]
        step_five = step_five.split("### 6. Emit the tier block", 1)[0]
        self.assertIn("plain field values", step_five)
        self.assertIn("only in `FILLED·asserted`", step_five)
        self.assertIn("never copied into the Medatrax block", step_five)
        self.assertIn("The final note body follows the same boundary", step_five)

    def test_medatrax_reference_forbids_a_provenance_label_on_filled_age(self):
        text = read(MEDATRAX)
        self.assertIn("**A filled age is entered without a provenance label.**", text)
        self.assertIn("The private `FILLED·asserted` record", text)

    def test_f5_enforces_the_same_boundary(self):
        row = next(
            line for line in read(DAY_A_ASSERTIONS).splitlines()
            if line.startswith("| F5 |")
        )
        for required in ("FILLED·asserted", "Age + unit", "Patient Time"):
            with self.subTest(required=required):
                self.assertIn(required, row)
        self.assertIn(
            "neither the note body nor the Medatrax block labels the age or band "
            "as filled, inferred, guessed, or needing confirmation",
            row,
        )
        self.assertProseNotIn("under GAPS", row)
        self.assertNotIn("unfilled", row)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PendingTestsGateOnlyWhatTheirResultsWouldEstablish(ProseBind, unittest.TestCase):
    """#149's converse descriptor rule stays aligned across both consumers."""

    SHARED = (
        "A pending test refuses only what its result would establish",
        "A pending test is not a finding",
        "Imaging is different because its result may establish the disease itself",
        "Every refusal resting on a pending test names what that result would establish",
    )

    def test_both_skills_state_the_culture_and_imaging_rule(self):
        for path in (CLINICAL_NOTE, ICD10_CPT):
            with self.subTest(path=path):
                for clause in self.SHARED:
                    self.assertProseIn(clause, read(path))

    def test_filled_anchor_declares_the_committed_split(self):
        text = read(FILLED_ANCHOR_ASSERTIONS)
        # The pipe-delimited row is the subject, so its formatting stays raw.
        self.assertIn("| F2 | 5, 7, 8, 10, 12 |", text)
        self.assertProseIn(
            "a pending culture does not by itself refuse a code whose descriptor names no organism",
            text,
        )
        # The backticks make J18.9 a literal code, so its formatting is subject.
        self.assertIn(
            "case 10 refuses `J18.9` because the absent film would establish the disease itself",
            text,
        )

    def test_the_new_row_is_unscored_and_in_both_denominators(self):
        assertions = read(FILLED_ANCHOR_ASSERTIONS)
        fixtures = read(FIXTURES_README)
        for text in (assertions, fixtures):
            with self.subTest(text=text[:40]):
                # The backticks distinguish the literal score marker from prose.
                self.assertIn("`REFUSAL 1/2`", text)
                self.assertProseIn("eight of fourteen rows", text)
                self.assertProseIn("F2 is unscored", text)

    def test_the_pre_landing_marker_is_retired(self):
        self.assertProseNotIn(
            "until it lands this example is the only place the distinction is written down",
            read(CLINICAL_NOTE),
        )


#: A skill's own step heading -- ``### 4. Draft the body``. Two to four hashes
#: because the skills are not uniform about depth and the number is the subject.
STEP_HEADING = re.compile(r"^#{2,4}\s+(\d+)\.\s")

#: A citation of one. ``steps?`` for the plural opener of *steps 1 and 2*, which
#: this reads as a citation of 1 and misses the 2 -- a floor rather than a
#: ceiling, on ``differential_scan.py``'s terms. The separator admits any
#: whitespace so a **hard-wrapped** citation is still seen. That costs nothing
#: today -- it finds not one match the single-space form misses, measured
#: 2026-08-19 -- and ``test_run_record_claim`` is where a wrapped phrase went
#: unread by the very check written to find it.
STEP_CITATION = re.compile(r"\bsteps?[-‑\s]+(\d+)\b", re.IGNORECASE)

#: ADRs express rulings as numbered paragraphs, numbered nested headings, or a
#: number in an H2 ruling heading. Addenda deliberately remain in the ruling
#: sequence; another H2 takes numbered prose back out of it.
ADR_HEADING = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
#: Declaration spellings are grounded in ADR headings and bold ruling items.
#: They intentionally differ from ``RULING_CITATION``'s four-word prose
#: vocabulary: accepting a citation word must not bless it as a writer's form.
RULING_HEADING = re.compile(r"^(?:ruling|decision)\s+(\d+)\b", re.IGNORECASE)
NUMBERED_HEADING = re.compile(r"^(\d+)\.\s")
RULING_SECTION = re.compile(
    r"^(?:what is ruled|the ruling|rulings|the decisions|ruled\b|(?:\w+\s+)?addendum\b)",
    re.IGNORECASE,
)
RULING_ITEM = re.compile(r"^(?:\*\*(?:ruling\s+)?)?(\d+)\.\s", re.IGNORECASE)
#: A fenced block is a specimen rather than document structure, and the record
#: whose ruling shows a record shape puts a literal ``## `` line inside one.
#: ADR 0087's ruling 2 does exactly that, and reading it as an H2 took the
#: section marker down and hid rulings 3 to 9 from every citation in the tree.
#: ``spelling_scan``'s mention-versus-use rule, which ``differential_scan``
#: already adopted for the same reason.
CODE_FENCE = re.compile(r"^\s*(```|~~~)")
RULING_CITATION = re.compile(
    r"\bADR\s+0*(\d+)(?:\]\([^\r\n]+?\))?(?:'s)?\s+"
    r"(ruling|point|decision|rule)\s+(\d+)\b",
    re.IGNORECASE,
)
RULING_EXEMPT_MARKER = re.compile(
    r"<!--\s*unresolved-ruling-citations:\s*(\d+)\s*-->"
)
RULING_EXEMPT_CEILING = 2
RULING_UNNUMBERED_MARKER = re.compile(r"<!--\s*no-numbered-rulings\s*-->")
RULING_UNNUMBERED_CEILING = 18

#: A reference-style Markdown destination. Link labels are deliberately opaque:
#: only the destination participates in relative-path resolution.
REFERENCE_DESTINATION = re.compile(r"(?m)^[ \t]{0,3}\[[^\]\r\n]+\]:[ \t]*")
ABSOLUTE_TARGET = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)

#: Under ``fixtures/``, these two names are prose about a run and everything
#: else is the run. See ``graded_files``.
FIXTURE_PROSE = {"README.md", "assertions.md"}

#: The two documents at the repo root that cite steps, and whether either may
#: declare a citation no skill name can resolve. **Ruled separately, 2026-08-19,
#: because [#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246)
#: put them in one row and they are not one kind of document.**
#:
#: ``AGENTS.md`` is short and it is a contract: it tells a consumer which skills
#: need which tools, and every ``step N`` in it is a genuine cross-reference. It
#: takes **no escape hatch**, so nobody can quietly buy their way out of the one
#: file a consumer reads.
#:
#: ``CLAUDE.md`` is an order of magnitude longer and is where every checker in
#: this repo gets described, so it is structurally where **every**
#: rule's mention-versus-use problem lands, and this file already records three
#: earlier instances: ``spelling_scan`` died on the paragraph documenting its own
#: homoglyph map, ``differential_scan``
#: [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) broke
#: on prose describing the row it grades, and two files exempted themselves from
#: ``phi_scan`` by explaining its pragma near the top. The three citations
#: declared there today are the fourth instance, not an anomaly.
#:
#: **No figure is stated for that asymmetry, and a draft of this docstring stated
#: two.** One counted ``CLAUDE.md``'s own lines, which the very commit writing it
#: changed; the other quoted a match count with no pattern beside it, so two
#: sweeps re-deriving it reasonably got different numbers. Both are
#: [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
#: arriving inside the change whose subject is #143.
#: ``TheTwoRootDocumentsAreNotOneKind`` pins the asymmetry as a **floor** instead,
#: and holds the pattern in code so *describes a checker* means one thing.

#: What *describes a checker* means, in code rather than left to a reader's grep.
CHECKER_PROSE = re.compile(r"scanner|parser|resolver|regex", re.IGNORECASE)
ROOT_DOCUMENTS = ((REPO_ROOT / "AGENTS.md", False), (REPO_ROOT / "CLAUDE.md", True))

#: The narrow opt-out #246 named as the honest remedy, and it declares a
#: **count** rather than opening a hole. On its own line, comment punctuation
#: aside, on ``phi_scan.py``'s reasoning -- a marker mentioned mid-sentence is
#: not a marker -- and it covers the **next paragraph only**, on
#: ``spelling_scan.py``'s: the unit is the span, so no document can exempt itself.
EXEMPT_MARKER = re.compile(r"<!--\s*unresolved-step-citations:\s*(\d+)\s*-->")

#: How many citations the hatch may hold in the one document that has it. A
#: ceiling and not a measurement: without one the marker is a wholesale opt-out
#: and the gate is theater. Deliberately close to what is declared today, so the
#: next one has to be argued for in a diff rather than typed. The count is not
#: restated in prose anywhere: it would go stale one short of this ceiling, which
#: is the one window where nothing here would fire.
EXEMPT_CEILING = 4


def skill_names() -> list[str]:
    """Every ``skills/<name>/`` holding a ``SKILL.md``, longest name first.

    Longest first so an alternation cannot match a shorter name inside a longer
    one. No pair overlaps today; the ordering is here so that a sixth skill
    called ``clinical-note-lite`` could not quietly resolve as ``clinical-note``.
    """
    names = [path.name for path in SKILLS_DIR.iterdir() if (path / "SKILL.md").is_file()]
    return sorted(names, key=lambda name: (-len(name), name))


README_SKILL_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")


def readme_skill_names() -> set[str]:
    """Skill names in the tables under README.md's consumer skill index."""
    section = read(README).split("## The skills", 1)[1]
    section = section.split("\n## ", 1)[0]
    return {
        found.group(1)
        for line in section.splitlines()
        for found in [README_SKILL_ROW.match(line)]
        if found
    }


class TheReadmeNamesEveryShippedSkill(unittest.TestCase):
    """#401: the public landing page and shipped skill tree stay complete."""

    def test_every_skill_directory_appears_in_the_readme_table(self):
        self.assertEqual(set(skill_names()) - readme_skill_names(), set())

    def test_every_readme_skill_row_has_a_skill_directory(self):
        self.assertEqual(readme_skill_names() - set(skill_names()), set())


def declared_steps(name: str) -> set[int]:
    """The numbered step headings ``skills/<name>/SKILL.md`` declares."""
    return {
        int(found.group(1))
        for line in read(SKILLS_DIR / name / "SKILL.md").splitlines()
        for found in [STEP_HEADING.match(line)]
        if found
    }


def ruling_ordinals(text: str) -> list[int]:
    """Ruling ordinals in document order, across the record and its addenda."""
    ordinals = []
    # Early ADRs place their ruling list directly below the H1. Any later H2
    # distinguishes the sections that follow, including correction lists.
    in_ruling_section = True
    accepts_items = True
    for line in unfenced_lines(text):
        heading = ADR_HEADING.match(line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2)
            numbered = RULING_HEADING.match(title)
            if level == 2 and numbered:
                ordinals.append(int(numbered.group(1)))
                in_ruling_section = False
                accepts_items = False
            elif level == 2:
                in_ruling_section = bool(RULING_SECTION.match(title))
                accepts_items = in_ruling_section
            elif in_ruling_section:
                numbered_item = NUMBERED_HEADING.match(title)
                if numbered_item and (
                    accepts_items or int(numbered_item.group(1)) == len(ordinals) + 1
                ):
                    ordinals.append(int(numbered_item.group(1)))
                    accepts_items = True
                    continue
                # A nested heading distinguishes its numbered material from
                # the parent ruling list. The next expected ordinal may resume
                # that parent list after the nested discussion.
                accepts_items = bool(RULING_SECTION.match(title))
            else:
                accepts_items = False
            continue
        if in_ruling_section:
            numbered = RULING_ITEM.match(line)
            if numbered and (accepts_items or int(numbered.group(1)) == len(ordinals) + 1):
                ordinals.append(int(numbered.group(1)))
                accepts_items = True
    return ordinals


def unfenced_lines(text: str) -> Iterator[str]:
    """Document lines excluding fenced specimens and their delimiters."""
    fence = None
    for line in text.splitlines():
        opener = CODE_FENCE.match(line)
        if fence is not None:
            # Only the marker that opened the block closes it, so a nested
            # fence of the other kind stays specimen text.
            if opener and line.strip().startswith(fence):
                fence = None
            continue
        if opener:
            fence = opener.group(1)
            continue
        yield line


def ruling_shape_findings(text: str) -> list[str]:
    """Every gap, restart, or other break in a record's ruling sequence."""
    findings = []
    previous = 0
    for ordinal in ruling_ordinals(text):
        expected = previous + 1
        if ordinal != expected:
            findings.append(
                f"ruling {ordinal} follows ruling {previous}; expected ruling {expected}"
            )
        previous = ordinal
    return findings


def unnumbered_ruling_marker_count(text: str) -> int:
    """Own-line empty-parse declarations outside fenced specimens."""
    return sum(
        1
        for line in unfenced_lines(text)
        if RULING_UNNUMBERED_MARKER.fullmatch(line.strip())
    )


def unnumbered_ruling_findings(text: str) -> list[str]:
    """An ADR's empty/non-empty parse agrees with exactly one declaration."""
    markers = unnumbered_ruling_marker_count(text)
    if not ruling_ordinals(text):
        if markers == 0:
            return ["an empty ruling parse lacks the no-numbered-rulings marker"]
        if markers > 1:
            return [f"an empty ruling parse carries {markers} no-numbered-rulings markers"]
        return []
    if markers:
        return ["a numbered ruling parse carries the no-numbered-rulings marker"]
    return []


def unnumbered_ruling_ceiling_findings(texts: list[str]) -> list[str]:
    """The tree-wide ceiling over deliberate empty ruling parses."""
    markers = sum(unnumbered_ruling_marker_count(text) for text in texts)
    if markers <= RULING_UNNUMBERED_CEILING:
        return []
    return [
        f"{markers} no-numbered-rulings markers exceed the ceiling of "
        f"{RULING_UNNUMBERED_CEILING}"
    ]


class RulingCitation(NamedTuple):
    """One ADR coordinate citation found at the adjacency ruled by ADR 0075."""

    line: int
    record: int
    number: int
    word: str


def ruling_citations(text: str) -> Iterator[RulingCitation]:
    """Every adjacent ``ADR NNNN`` plus one of the four ordinal words."""
    for found in RULING_CITATION.finditer(text):
        yield RulingCitation(
            text.count("\n", 0, found.start()) + 1,
            int(found.group(1)),
            int(found.group(3)),
            found.group(2).lower(),
        )


def ruling_exemptions(text: str) -> list[Exemption]:
    """Every ruling-citation marker paired with its next paragraph."""
    blocks = list(paragraphs(text))
    found = []
    for index, (start, block) in enumerate(blocks):
        if "\n" in block:
            continue
        matched = RULING_EXEMPT_MARKER.fullmatch(block.strip())
        if not matched:
            continue
        declared = int(matched.group(1))
        if index + 1 == len(blocks):
            found.append(Exemption(start, start, start, declared))
            continue
        next_start, next_block = blocks[index + 1]
        found.append(
            Exemption(start, next_start, next_start + next_block.count("\n"), declared)
        )
    return found


def unresolved_ruling_citations(
    text: str,
    declared: dict[int, set[int]],
) -> list[str]:
    """Dangling ADR coordinates not exactly covered by a counted marker."""
    unresolved = [
        cite
        for cite in ruling_citations(text)
        if cite.record not in declared or cite.number not in declared[cite.record]
    ]
    spans = ruling_exemptions(text)
    covering = [span for span in spans if span.declared >= 1]
    complaints = []
    for cite in unresolved:
        if not any(span.first <= cite.line <= span.last for span in covering):
            complaints.append(
                f"{cite.line}: ADR {cite.record:04d} {cite.word} {cite.number} does not exist"
            )
    for span in spans:
        held = len([cite for cite in unresolved if span.first <= cite.line <= span.last])
        if span.declared < 1:
            complaints.append(f"{span.marker}: a marker declaring nothing exempts nothing")
        elif held != span.declared:
            complaints.append(f"{span.marker}: declares {span.declared}, paragraph holds {held}")
    return sorted(complaints, key=lambda line: int(line.split(":")[0]))


def declared_rulings() -> dict[int, set[int]]:
    """Each tracked ADR number joined to the shared parser's ordinal set."""
    declared = {}
    for record in sorted((REPO_ROOT / "docs" / "adr").glob("*.md")):
        matched = re.match(r"^(\d{4})-", record.name)
        if not matched:
            continue
        number = int(matched.group(1))
        if number in declared:
            raise AssertionError(f"ADR {number:04d} has more than one tracked record")
        declared[number] = set(ruling_ordinals(read(record)))
    return declared


def walk_ruling_citations() -> list[tuple[Path, RulingCitation]]:
    """Every adjacent ADR coordinate in the shared graded-file population."""
    return [
        (path, cite)
        for path in graded_files()
        for cite in ruling_citations(read(path))
    ]


def ruling_marker_ceiling_findings(texts: list[str]) -> list[str]:
    """The global declared-count ceiling over every graded document."""
    declared = sum(
        span.declared
        for text in texts
        for span in ruling_exemptions(text)
    )
    if declared <= RULING_EXEMPT_CEILING:
        return []
    return [
        f"{declared} unresolved ruling citations exceed the ceiling of "
        f"{RULING_EXEMPT_CEILING}"
    ]


def paragraphs(text: str) -> Iterator[tuple[int, str]]:
    """Blocks of consecutive non-blank lines, with the line each one opens on.

    The paragraph is the resolution scope rather than the line, because this
    repo hard-wraps its prose: a subject named at the end of one line is carried
    by the next, and a line-scoped reader would drop it.
    """
    block: list[str] = []
    start = 1
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not block:
                start = number
            block.append(line)
        elif block:
            yield start, "\n".join(block)
            block = []
    if block:
        yield start, "\n".join(block)


def _markdown_prose(text: str) -> str:
    """Mask fenced and inline code while preserving offsets and line breaks."""
    visible = list(text)
    offset = 0
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        stripped = content.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if fence is not None:
            for index in range(offset, offset + len(content)):
                visible[index] = " "
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1]:
                fence = None
            offset += len(line)
            continue
        if marker:
            fence = (marker.group(1)[0], len(marker.group(1)))
            for index in range(offset, offset + len(content)):
                visible[index] = " "
            offset += len(line)
            continue

        index = 0
        while index < len(content):
            if content[index] != "`":
                index += 1
                continue
            end = index
            while end < len(content) and content[end] == "`":
                end += 1
            delimiter = content[index:end]
            close = content.find(delimiter, end)
            if close < 0:
                index = end
                continue
            for masked in range(offset + index, offset + close + len(delimiter)):
                visible[masked] = " "
            index = close + len(delimiter)
        offset += len(line)
    return "".join(visible)


class MarkdownTarget(NamedTuple):
    """One Markdown link destination and its source offset."""

    offset: int
    target: str


def _angle_destination(text: str, start: int) -> tuple[str, int] | None:
    """An angle-bracket destination beginning at ``start``."""
    target = []
    cursor = start + 1
    while cursor < len(text):
        if text[cursor] == "\\" and cursor + 1 < len(text):
            target.append(text[cursor + 1])
            cursor += 2
            continue
        if text[cursor] == ">":
            return "".join(target), cursor + 1
        if text[cursor] in "\r\n":
            return None
        target.append(text[cursor])
        cursor += 1
    return None


def _raw_destination(
    text: str,
    start: int,
    *,
    inline: bool,
) -> tuple[str, int] | None:
    """A whitespace-free destination, retaining balanced parentheses."""
    target = []
    depth = 0
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text):
            target.append(text[cursor + 1])
            cursor += 2
            continue
        if char == "(":
            depth += 1
            target.append(char)
            cursor += 1
            continue
        if char == ")":
            if inline and depth == 0:
                break
            if depth == 0:
                return None
            depth -= 1
            target.append(char)
            cursor += 1
            continue
        if char.isspace() and depth == 0:
            break
        target.append(char)
        cursor += 1
    if depth or (not target and not inline):
        return None
    return "".join(target), cursor


def _closing_inline_link(text: str, start: int) -> int | None:
    """The offset after an inline link's optional title and closing parenthesis."""
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor < len(text) and text[cursor] == ")":
        return cursor + 1
    if cursor >= len(text) or text[cursor] not in "\"'(":
        return None
    opener = text[cursor]
    closer = ")" if opener == "(" else opener
    cursor += 1
    while cursor < len(text):
        if text[cursor] == "\\" and cursor + 1 < len(text):
            cursor += 2
            continue
        if text[cursor] == closer:
            cursor += 1
            break
        cursor += 1
    else:
        return None
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    return cursor + 1 if cursor < len(text) and text[cursor] == ")" else None


def _inline_destination(text: str, start: int) -> tuple[str, int] | None:
    """The destination and end offset for ``](...)`` beginning after ``(``."""
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor < len(text) and text[cursor] == "<":
        parsed = _angle_destination(text, cursor)
    else:
        parsed = _raw_destination(text, cursor, inline=True)
    if parsed is None:
        return None
    target, cursor = parsed
    end = _closing_inline_link(text, cursor)
    return (target, end) if end is not None else None


def markdown_targets(text: str) -> Iterator[MarkdownTarget]:
    """Inline and reference-style Markdown destinations outside code."""
    prose = _markdown_prose(text)
    for found in REFERENCE_DESTINATION.finditer(prose):
        cursor = found.end()
        if cursor < len(prose) and prose[cursor] == "<":
            parsed = _angle_destination(prose, cursor)
        else:
            parsed = _raw_destination(prose, cursor, inline=False)
        if parsed is not None:
            yield MarkdownTarget(found.start(), parsed[0])

    cursor = 0
    while cursor < len(prose):
        label = prose.find("[", cursor)
        if label < 0:
            return
        close = prose.find("]", label + 1)
        if close < 0:
            return
        if close + 1 >= len(prose) or prose[close + 1] != "(":
            cursor = close + 1
            continue
        parsed = _inline_destination(prose, close + 2)
        if parsed is None:
            cursor = close + 1
            continue
        target, cursor = parsed
        yield MarkdownTarget(label, target)


def dead_links(
    text: str,
    owner: Path,
    exists: Callable[[Path], bool],
) -> list[tuple[int, str]]:
    """Relative Markdown targets in ``text`` that ``exists`` cannot find."""
    dead = []
    parent = owner.parent.as_posix()
    for found in markdown_targets(text):
        target = found.target
        if ABSOLUTE_TARGET.match(target) or target.startswith(("/", "//")):
            continue
        path_target = target.split("#", 1)[0]
        resolved = owner if not path_target else Path(
            posixpath.normpath(posixpath.join(parent, path_target))
        )
        if not exists(resolved):
            dead.append((text.count("\n", 0, found.offset) + 1, target))
    return dead


class Exemption(NamedTuple):
    """One ``unresolved-step-citations`` marker and the paragraph it covers."""

    marker: int
    first: int
    last: int
    declared: int


def exemptions(text: str) -> list[Exemption]:
    """Every marker in ``text``, paired with the line range of the next paragraph.

    **A count rather than a license, and that is the whole of why this is not a
    hole.** #246 asked whether the repo root could take #238's rule, and three
    paragraphs of ``CLAUDE.md``'s own section *about* citations say no: each
    **quotes** a citation -- ``GLOSSARY.md``'s line, offered as the evidence for
    the ``carried`` limb, and two forms quoted **because they do not resolve**.
    Naming a skill beside any of them would falsify the quotation, which is
    ``differential_scan.py``'s
    [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) --
    *describing the rule broke the tool that checks the rule* -- arriving on a
    document instead of a parser.

    **So the marker declares how many the paragraph holds**, and a further
    citation wandering into an exempted paragraph fails exactly as it would
    anywhere else. A bare *ignore this paragraph* would not, and that is the
    difference between an opt-out and an off switch.

    **On its own line and blank-line separated from what it covers.** Glue it to
    the paragraph and ``paragraphs`` reads the two as one block, which this
    declines to match -- so the paragraph stays graded. That is the safe
    direction to be wrong in, and it is ``phi_scan.py``'s own-line pragma rule
    rather than a new one.

    **A marker with nothing under it covers itself**, so it reports zero against
    a declared count and goes red. A stale marker left behind by a rewrite is a
    license nobody is using, and this is the only thing that ever notices.
    """
    blocks = list(paragraphs(text))
    found = []
    for index, (start, block) in enumerate(blocks):
        if "\n" in block:
            continue
        matched = EXEMPT_MARKER.fullmatch(block.strip())
        if not matched:
            continue
        declared = int(matched.group(1))
        if index + 1 == len(blocks):
            found.append(Exemption(start, start, start, declared))
            continue
        next_start, next_block = blocks[index + 1]
        last = next_start + next_block.count("\n")
        found.append(Exemption(start, next_start, last, declared))
    return found


class Citation(NamedTuple):
    """One ``step N``, and whose step N it turned out to be."""

    line: int
    number: int
    skill: str | None
    how: str


def step_citations(text: str, owner: str | None, names: list[str]) -> Iterator[Citation]:
    """Every ``step N`` in ``text``, resolved to the skill it names -- or to nothing.

    **Three limbs, and they are how a person reads one rather than a heuristic.**

    - ``beside`` -- a skill is named immediately before the words, with nothing
      but its own link or path punctuation in between. ``[clinical-note](../
      clinical-note/SKILL.md) step 5`` and ```icd10-cpt`` step 4`` are both this,
      and it is the only limb that can name a skill other than the file's own.
    - ``carried`` -- a bare ``step N`` continues the subject of the citation
      before it, **unless another skill has been named in between**. That last
      clause is the whole of it: *"[clinical-note] step 2 and [batch-shift], for
      step 9's shorthand"* is ``setup-clinical-skills``'s own step 9, and
      dropping the clause resolves it to ``batch-shift`` and fails a correct line.
    - ``owner`` -- otherwise, the skill whose directory the file sits in.

    **Both simpler rules were tried against the tree first and both failed.**
    Nearest-name-anywhere fails two correct lines in
    ``setup-clinical-skills/SKILL.md``; adjacency with no carry fails
    ``clinical-note/GLOSSARY.md``'s *"on the same terms as the voice model in
    step 8"*, which continues a ``setup-clinical-skills`` subject set earlier in
    the same sentence. Three limbs is what it took to reach zero false alarms,
    and each was added because a real line demanded it.

    **A file outside ``skills/`` with nothing beside the citation is unresolved,
    and stays that way.** ``anchor_scan.py`` said ``step-4`` six times meaning
    ``icd10-cpt``, and no rule here could know that. The alternative is a guess,
    and ``differential_scan.py``'s first version is what a positional guess
    costs: it failed in both directions. Unresolved citations are counted and
    reported; they are never failed -- which is what made
    [#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238)'s
    repair safe to make: naming the skill beside those six converted them with no
    change here. **The repo root followed on
    [#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246)**, on
    the same terms and at the same price bar a handful of quotations -- see
    ``ROOT_DOCUMENTS``. What is left unresolved is ``fixtures/`` prose.
    """
    beside = re.compile("(" + "|".join(re.escape(name) for name in names) + r")\S*\s*$")
    anywhere = re.compile("|".join(re.escape(name) for name in names))
    for start, block in paragraphs(text):
        previous: str | None = None
        end = 0
        for found in STEP_CITATION.finditer(block):
            before = block[: found.start()]
            adjacent = beside.search(before)
            if adjacent:
                skill, how = adjacent.group(1), "beside"
            elif previous and not anywhere.search(block[end : found.start()]):
                skill, how = previous, "carried"
            else:
                skill, how = owner, "owner"
            previous, end = skill, found.end()
            yield Citation(start + before.count("\n"), int(found.group(1)), skill, how)


def owning_skill(path: Path, names: list[str]) -> str | None:
    """The skill whose directory ``path`` sits in, if any."""
    try:
        parts = path.resolve().relative_to(SKILLS_DIR).parts
    except ValueError:
        return None
    return parts[0] if parts and parts[0] in names else None


def graded_files() -> list[Path]:
    """Tracked ``.md`` and ``.py``, minus the preserved run records.

    **``fixtures/`` is excluded bar its own prose, and the reason is that a
    record cannot be edited to fix a stale citation.** A note under
    ``fixtures/filled-anchor/notes/`` cites the skill **as it stood when the run
    happened** -- that is what makes it evidence -- so grading one would refuse a
    faithful record, and the only repair available would be to falsify it. The
    two prose names are graded because they are maintained documents *about* a
    run, and a stale ``step 7`` in one is an ordinary defect.

    **The default under ``fixtures/`` is to exclude**, so a new kind of record
    lands outside the check rather than inside it. What that costs is measured:
    140 of the 164 citations under ``fixtures/`` are in records, and every one of
    them is unresolved anyway -- so today the exclusion drops nothing the
    resolver could have graded. It is here for the record that arrives tomorrow
    naming its skill.

    **This module is dropped too, and it is the only other exclusion.** The
    resolver's own test cases are deliberately hostile strings -- a link labeled
    for one skill pointing at another, a citation to a step that does not exist
    -- and grading them would fail the file for containing its own fixtures. The
    cost is real and narrow: a genuine ``step N`` citation written into the prose
    *here* is the one the tree-wide walk cannot see. It is asserted below rather
    than only described, because ``test_run_record_claim.py`` carried this exact
    exemption in its docstring for one round while the walk had no filter wired.

    **Tracked, which is the whole of what a clean result covers.**
    [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254):
    ``git ls-files`` is the index, an untracked file is not in it, and the
    honest form of a green ``EveryCitedStepResolvesToADeclaredStep`` is *no
    tracked file cites a step that does not exist*.

    **This walk is the one #254 was filed over.** ``tools/checks_ledger.py``
    landed on #240's branch with two ``step N`` citations naming no skill,
    ``test_every_citation_in_tools_resolves`` was on that branch's base, and the
    suite ran green three times at 1788 tests before the ``git add`` that made
    the file visible here. A review agent found it; this walk could not have.

    **The window stays open, ruled on 2026-08-19.** Widening to ``--others
    --exclude-standard`` closes it and was declined -- CI catches it at push and
    the next local run catches it after the stage.
    """
    finished = subprocess.run(
        ["git", "ls-files", "--cached", "--", "*.md", "*.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    kept = []
    for line in finished.stdout.splitlines():
        if not line.strip():
            continue
        path = REPO_ROOT / line
        if line.startswith("fixtures/") and path.name not in FIXTURE_PROSE:
            continue
        if path.resolve() == SELF:
            continue
        kept.append(path)
    return kept


def walk_citations() -> list[tuple[Path, Citation]]:
    """Every ``step N`` in every graded file, paired with the file it is in.

    Three tests in ``EveryCitedStepResolvesToADeclaredStep`` want this walk under
    different filters -- the per-limb floors, the unresolved report, and #238's
    ``tools/`` rule -- and the third is what made repeating it worth removing.
    ``stale_citations`` deliberately does **not** use this: it takes ``declared``
    as a parameter so the check can be pointed at a renumbering that has not
    happened, and deriving the skill names from that map rather than from the
    tree is the whole of how that works.
    """
    names = skill_names()
    return [
        (path, cite)
        for path in graded_files()
        for cite in step_citations(read(path), owning_skill(path, names), names)
    ]


def stale_citations(declared: dict[str, set[int]]) -> list[str]:
    """Every resolved ``step N`` naming a step ``declared`` does not hold.

    ``declared`` is a parameter rather than a lookup so the check can be pointed
    at a **renumbering that has not happened**. Asserting the tree is clean today
    proves the walk found nothing; asserting it goes red when a step is taken
    away proves the walk would find something. Only the second is evidence.
    """
    names = sorted(declared, key=lambda name: (-len(name), name))
    stale = []
    for path in graded_files():
        owner = owning_skill(path, names)
        for cite in step_citations(read(path), owner, names):
            if cite.skill is None or cite.number in declared[cite.skill]:
                continue
            where = path.relative_to(REPO_ROOT).as_posix()
            stale.append(f"{where}:{cite.line} cites {cite.skill} step {cite.number} ({cite.how})")
    return stale


def undeclared_citations(text: str, names: list[str], hatch: bool) -> list[str]:
    """Every ``step N`` in a repo-root document that no skill name and no marker covers.

    A parameter rather than a file walk, on ``stale_citations``'s reasoning: the
    gate can then be pointed at text the tree does not hold. Asserting the two
    root documents are clean today proves the walk found nothing; pointing it at
    a bare citation and watching it complain proves it would find something.

    **The count is enforced in both directions and that is the point of it.** A
    marker declaring fewer than the paragraph holds means a citation arrived
    unnoticed; declaring more means a rewrite left a license nobody is using.
    Both are reported, because a marker is a statement about a paragraph and a
    stale statement is what this whole class of check exists to refuse.

    **``hatch`` is False for ``AGENTS.md`` and the marker becomes a complaint in
    its own right**, rather than merely being unnecessary there. Silence would
    make the hatch available to that file the moment somebody typed one; a file
    with no legitimate use for a specimen citation should say so when one
    arrives, which is ``skills_mirror.py``'s *a stale mirror has no legitimate
    form* applied to an escape hatch. See ``ROOT_DOCUMENTS`` for why the two
    documents are ruled apart.

    **Required rather than defaulted**, because a default here picks a policy
    for whoever forgets the argument -- and the permissive branch is the one a
    forgetful call would have got. Two call sites, both explicit.
    """
    cites = list(step_citations(text, None, names))
    spans = exemptions(text)
    unresolved = [cite for cite in cites if cite.skill is None]
    complaints = []
    # A marker declaring nothing covers nothing, so the citations beneath it are
    # still loose. Letting the span suppress them would make ``: 0`` the widest
    # license in the file rather than the narrowest -- an off switch reached by
    # typing the smallest number, which is the shape this marker exists to refuse.
    covering = [span for span in spans if span.declared >= 1] if hatch else []
    for cite in unresolved:
        if not any(span.first <= cite.line <= span.last for span in covering):
            complaints.append(f"{cite.line}: step {cite.number} names no skill")
    for span in spans:
        if not hatch:
            complaints.append(f"{span.marker}: this document takes no exemption marker")
            continue
        held = len([c for c in unresolved if span.first <= c.line <= span.last])
        if span.declared < 1:
            complaints.append(f"{span.marker}: a marker declaring nothing exempts nothing")
        elif held != span.declared:
            complaints.append(f"{span.marker}: declares {span.declared}, paragraph holds {held}")
    return sorted(complaints, key=lambda line: int(line.split(":")[0]))


def names_the_same_field(claimed: str, field: str) -> bool:
    """Does a phrase from ``setup``'s per-account sentence name a declared field?

    The two files write one field differently on purpose: ``setup`` pluralizes
    (*case types*) and qualifies (*Patient Time bands*) in running prose, while
    the reference uses the bare dropdown label. So the comparison strips one
    trailing ``s`` and matches **in both directions** -- a one-way containment
    test read *Patient Time bands* correctly and would have missed a bare
    *case*, which the spec axis of #222's review found by trying it.

    Deliberately blunt, and it can only ever produce a **false alarm**: two
    documents disagreeing about one field, reported for a person to settle. That
    is the safe direction here, and the alternative is the name vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build.
    """
    def norm(value: str) -> str:
        value = value.strip().lower()
        return value[:-1] if value.endswith("s") else value

    a, b = norm(claimed), norm(field)
    return a == b or a in b or b in a


def frontmatter_description(path: Path) -> str:
    """The ``description:`` line of a skill's YAML frontmatter.

    Read by line rather than with a YAML parser because the frontmatter is three
    keys and the repo is stdlib-only. A skill whose description wrapped onto a
    second line would return only the first, so the assertions below check for
    what must be **absent** on the whole file as well.
    """
    for line in read(path).splitlines():
        if line.startswith("description:"):
            return line
    raise AssertionError(f"{path} has no description line in its frontmatter")


class BatchShiftHasOneEntryPointAndItIsAFile(unittest.TestCase):
    """#90 decision 2, ruled 2026-08-16: a day file, and no second input shape.

    The clinician still scans each shift to a PDF, so steps 1 and 2 fire on live
    work -- and a whole shift never arrives as a paste, because a paste is one or
    two encounters and those are ``clinical-note``'s. **Both halves are asserted**:
    without the second, a description naming a day file *and* a paste would pass
    while re-opening the exact ambiguity the ruling closed.
    """

    def test_the_description_names_a_day_file(self):
        self.assertIn("day file", frontmatter_description(BATCH_SHIFT))

    def test_the_description_does_not_offer_a_pasted_shift(self):
        # **The description line, not the file.** The first version of this test
        # searched the whole file and failed on the skill's own paragraph
        # recording what the description used to say -- a **mention**, quoted in
        # order to rule against it, which is ``spelling_scan``'s distinction
        # arriving uninvited in a third place. Widening the search would force
        # the next session to delete the sentence explaining the ruling in order
        # to satisfy a test guarding that ruling.
        self.assertNotIn("pastes a whole shift", frontmatter_description(BATCH_SHIFT))

    def test_the_description_routes_a_small_paste_to_clinical_note(self):
        self.assertIn("clinical-note", frontmatter_description(BATCH_SHIFT))

    def test_the_agents_index_row_agrees_with_the_description(self):
        row = [
            line for line in read(AGENTS).splitlines()
            if line.startswith("| batch-shift ")
        ]
        self.assertEqual(len(row), 1, "AGENTS.md must carry exactly one batch-shift row")
        self.assertIn("day file", row[0])
        self.assertNotIn("pasted", row[0])

    def test_the_skill_says_the_steps_fire_on_live_work(self):
        # The whole ruling in one clause. Deleting the paragraph that explains
        # *why* steps 1 and 2 stay is how the question gets reopened by a session
        # that reads them as archaeology, which is what #90 was filed on.
        self.assertIn("still scans each shift", read(BATCH_SHIFT))


class TheBranchIsNamedBeforeAShiftIsWritten(ProseBind, unittest.TestCase):
    """#90 decision 4: ``clinical-note`` standalone picks its own branch.

    ``fixtures/day-a`` run 2 is the evidence: given the shorthand with no branch
    stated, several passes chose the FNP H&P unprompted and were discarded. **The
    count is in ``fixtures/day-a/assertions.md`` and deliberately not repeated
    here**, because it was measured against a directory under ``scratch/`` and
    nothing committed re-derives it.

    **This docstring restated that count until a sweep caught it**, on the same
    branch as the two skill paragraphs that forbid restating it -- so the rule and
    its violation shipped together, which is
    [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
    thesis demonstrated by the change that cites it. A ``.py`` docstring reads as
    exempt from a rule about prose, and it is not.

    The fix is two lines in two files and **neither works alone**: the default
    makes a shift uniform, and the confirm block is where a wrong default is
    caught on note one instead of note eleven.
    """

    def test_the_confirm_block_prints_the_branch(self):
        self.assertIn("Branch for the whole shift", read(BATCH_SHIFT))

    def test_clinical_note_defaults_to_soap_when_nobody_named_one(self):
        text = read(CLINICAL_NOTE)
        self.assertIn("write SOAP, say which you chose", text)

    def test_clinical_note_forbids_defaulting_silently(self):
        # The default is wrong during the first six encounters of a course, so
        # announcing it is the entire mitigation. A run that defaults quietly has
        # kept the behavior and dropped the thing that makes it survivable.
        self.assertIn("Never silently default", read(CLINICAL_NOTE))

    def test_a_named_branch_still_wins(self):
        self.assertIn("Where a branch was named, that is the branch", read(CLINICAL_NOTE))

    def test_a_named_branch_does_not_suspend_the_program_rule(self):
        # The first version of this ruling read "the rule above is not consulted",
        # which contradicted the *first six encounters must be H&P* rule four
        # lines above it -- and the current course started from zero, so it was
        # live rather than theoretical. Caught by the spec axis of the review.
        self.assertIn("This does not suspend the rule above", read(CLINICAL_NOTE))

    def test_the_shift_default_does_not_reach_step_5_as_a_choice(self):
        # **The seam, and the hole the first version of this work left open.**
        # Step 4 defaulting to SOAP and step 5 reading it as *the branch the user
        # named* would hand ``clinical-note`` a named branch, so its offer-to-redo
        # would never fire and the mitigation would be silently defeated for a
        # whole shift. Step 4 stops for confirmation anyway, which is what makes
        # the default survivable -- so the two clauses have to stay welded.
        text = read(BATCH_SHIFT)
        self.assertIn("must not reach step 5 disguised as a choice", text)
        self.assertIn("on the branch step 4 settled", text)
        self.assertProseNotIn("on the branch the user named", text)


class BothSkillsRuleTheSameWayOnAnUnmappedPreceptor(unittest.TestCase):
    """#91's ruling, and the copy of it #91 did not sweep for.

    The retired sentence welded two acts together: an agent guessing a nearest
    surname match, which is forbidden, and the clinician entering his own
    preceptor of record where the picklist has no row for the physician he
    rounded with, which is his call and already made. **Only the first is an
    agent's to refuse.**
    """

    def test_neither_skill_carries_the_retired_sentence_as_a_rule(self):
        # Both files may *report* the old wording -- ``setup-clinical-skills``
        # does, in a parenthetical recording what it replaced -- so the check is
        # that neither states it as an instruction. A mention is not a use, which
        # is ``spelling_scan``'s distinction reused rather than reinvented.
        for path in (BATCH_SHIFT, SETUP):
            for line in read(path).splitlines():
                if "reported, never substituted" not in line:
                    continue
                self.assertTrue(
                    line.lstrip().startswith("*("),
                    f"{path.name} states the retired rule rather than reporting it: {line}",
                )

    def test_both_skills_forbid_guessing_a_surname(self):
        for path in (BATCH_SHIFT, SETUP):
            self.assertIn(
                "guess a nearest surname match",
                read(path),
                f"{path.name} dropped the prohibition that survived #91",
            )

    def test_the_two_skills_split_collecting_the_answer_from_using_it(self):
        # **A bare ``"profile" in text`` passed with the ruling deleted**, because
        # both files name ``scratch/medatrax-profile.md`` for unrelated reasons --
        # the vacuous-row problem ``fixtures/README.md`` names, caught in review.
        # So each side is pinned to its own half: setup **writes** the ruling,
        # batch-shift **reads** it, and neither restates the other's.
        self.assertIn("write the ruling into the profile", read(SETUP))
        self.assertIn("Read the profile", read(BATCH_SHIFT))

    def test_setup_does_not_restate_the_lookup_order_it_points_at(self):
        # The cure for a copy that drifted cannot be a second copy. #91 fixed one
        # of two near-identical paragraphs and the other went stale; duplicating
        # the ruling again would rebuild exactly that.
        self.assertIn("not restated here on purpose", read(SETUP))




class ThePerAccountPicklistsAreNotInTheReference(ProseBind, unittest.TestCase):
    """#212's ruling, and the one half of it a reader can check without a name.

    ``setup-clinical-skills`` states the split this repo runs on -- *this file
    holds the universal Medatrax behavior and the profile holds everything about
    them* -- and ``reference/medatrax-fields.md`` inlined the preceptor and site
    picklists anyway, for the whole life of the file. That is what #212 found
    while scanning for a public flip, and the tree was cleared on the broken
    split rather than on de-identification: **#212 re-ruled #50 the same way**,
    no site layer and the historical blobs stay.

    **These assertions name no site and no preceptor, deliberately.** A test
    holding the strings would put them back in the tree the ruling just emptied,
    which is ``spelling_scan``'s mention-versus-use problem with the sign
    flipped -- here the mention is the leak. So each check is structural: the
    reference must *point at* the profile, and the two skills that consume the
    rules must not send a reader to the file that no longer holds them.

    What no test here can reach is a *new* per-account value arriving in the
    reference under some other heading. #50 ruled that hole acceptable and #212
    left it ruled; nothing below is a fourth ``phi_scan`` layer.
    """

    def test_the_reference_points_at_the_profile_for_both_picklists(self):
        text = read(MEDATRAX)
        self.assertIn("Preceptor and Location / Site are per-account", text)
        self.assertIn("scratch/medatrax-profile.md", text)

    def test_the_reference_keeps_the_format_it_gave_up_the_values_for(self):
        # The move is only safe if the universal half survives it. ``Last,First``
        # with no space is Medatrax behavior on every account, and an entry
        # written with a space does not match the picklist.
        self.assertIn("`Last,First` with no space", read(MEDATRAX))

    def test_the_payer_rule_is_not_claimed_to_live_in_the_reference(self):
        # ``clinical-note`` step 5 read *The rules live in the reference; do not
        # restate them here* while one of the two rules keys on a site name. A
        # reader following that sentence after the move finds nothing and has to
        # guess, which is the failure #212's move would otherwise have created.
        note = read(CLINICAL_NOTE)
        self.assertProseNotIn("The rules live in the reference", note)
        self.assertIn("keys on the site, which makes it per-account", note)

    def test_no_consumer_still_addresses_the_payer_rule_to_the_reference(self):
        # **The first pass of this class checked one consumer and there were
        # three**, which is #137's partial instrument arriving on the sweep meant
        # to prevent it. ``block_scan.py`` grades the F1 row that rests on this
        # rule and its docstring gave the old address; ``setup-clinical-skills``
        # step 1 asserted the per-account content was *written into* the
        # reference, eighty lines above the rule this branch added saying it must
        # not be. Both read as coherent alone, which is this file's whole subject.
        self.assertProseNotIn(
            "**declared rule** in ``reference/medatrax-fields.md``",
            read(BLOCK_SCAN),
        )
        self.assertProseNotIn(
            "all of it is currently written into", read(SETUP)
        )

    def test_setup_rules_where_a_site_keyed_rule_belongs(self):
        # The durable half. Without it the next declared default keyed on a
        # placement lands back in the reference and the split breaks again.
        self.assertIn(
            "keys on a preceptor or a site is per-account", read(SETUP)
        )


class TheVoiceModelIsPerAccountAndTheMethodIsNot(ProseBind, unittest.TestCase):
    """#213's build, on the rule #212 settled and this class already pins above.

    **The ticket asked for one file and the answer is two**, so the thing most
    likely to go wrong later is a tidy that collapses them back. ``voice.md`` is
    the *method* and travels in ``reference/``; the *model* it builds is
    ``scratch/voice-model.md``, gitignored, one per clinician. Shipping a
    register in ``reference/`` would make every other user of the skill sound
    like this one, **which #213 names as worse than no model at all** -- so the
    failure is not a leak the way the picklists were, it is a skill that is
    silently wrong for everybody except its author.

    **Three files have to agree and each reads as coherent alone**, which is this
    module's whole subject. ``SKILL.md`` sends a run to the model, ``style.md``
    §11 sends a reader from the mechanics to the register, and ``voice.md`` says
    which of the two it is. A single-file reader sees no contradiction in any
    arrangement of them.

    **Nothing here quotes a sample or names the clinician**, on
    ``ThePerAccountPicklistsAreNotInTheReference``'s reasoning one step out: a
    test holding a line of his writing would put it in the tree that the split
    exists to keep it out of.
    """

    def test_the_method_travels_and_the_model_does_not(self):
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("This file is the method. It is not the model.", voice)
        self.assertIn("scratch/voice-model.md", voice)

    def test_the_skill_sends_a_run_to_the_gitignored_model(self):
        # Not to ``reference/voice.md``, which holds no register and never will.
        self.assertIn("scratch/voice-model.md", read(CASE_STUDY))

    def test_the_unmodeled_declaration_survives_the_build(self):
        # The rule predates the file and is the one thing a run does when there
        # are no samples. A build that quietly dropped it would leave a run
        # claiming a register it was never given.
        for path in (CASE_STUDY, CASE_STUDY_VOICE):
            self.assertIn("the voice is unmodeled", read(path))

    def test_each_discussion_skill_points_at_section_eights_no_model_rule(self):
        voice = read(CASE_STUDY_VOICE)
        section_eight = voice.split("## 8. What the built model looks like", 1)[1]
        section_eight = section_eight.split("\n## 9.", 1)[0]
        self.assertIn("Where there is no model.", section_eight)

        pointer = "[voice.md](../_shared/reference/voice.md) §8"
        for path in (DISCUSSION_POST, DISCUSSION_REPLY):
            with self.subTest(skill=path.parent.name):
                step_three = read(path).split("## 3.", 1)[1]
                step_three = step_three.split("\n## 4.", 1)[0]
                self.assertProseIn(
                    pointer,
                    step_three,
                    f"{path.relative_to(REPO_ROOT)} does not inherit voice.md "
                    "section 8's no-model rule in step 3",
                )

    def test_the_declaration_is_per_register(self):
        # ``voice.md`` §7. A whole-document declaration reads as complete
        # coverage the moment one register is modeled, which is this repo's most
        # repeated defect wearing a new hat.
        self.assertIn("declaration is per register", read(CASE_STUDY))
        self.assertIn("fewer than two samples", read(CASE_STUDY_VOICE))

    def test_the_style_sheet_hands_the_register_off_rather_than_claiming_it(self):
        # §11 was written by reading finished documents for what they *do*, and
        # a run satisfied every bullet while reading as a stranger. The sheet has
        # to say so where the bullets are, or the next reader takes the list for
        # the whole answer -- which is exactly what happened.
        style = read(CASE_STUDY_STYLE)
        self.assertIn("These are the mechanics", style)
        self.assertIn("[voice.md](voice.md)", style)

    def test_setup_is_the_collector_and_does_not_restate_the_spec(self):
        # The clinician's ruling of 2026-08-18 on the one question #213 left
        # open. It is the same shape step 4 of ``setup`` already runs on with
        # ``batch-shift``'s lookup order -- **collecting the answer and deciding
        # what to ask for are two jobs**, and #90 is what happens when one rule
        # gets written into both files. So ``setup`` must point at the spec, and
        # must not carry the counts that would go stale against it.
        setup = read(SETUP)
        self.assertIn("_shared/reference/voice.md", setup)
        self.assertIn("not restated here on purpose", setup)
        self.assertProseNotIn("Ask for 5 at minimum", setup)

    def test_the_skill_names_the_collector_rather_than_collecting(self):
        # The other direction. A run drafting against a deadline that stopped to
        # elicit eight writing samples would be doing setup's job at the worst
        # possible moment, and the clinician may not even be at the keyboard.
        case_study = read(CASE_STUDY)
        self.assertIn("setup-clinical-skills", case_study)
        self.assertIn("this run does not stop to build one", case_study)

    def test_the_model_is_confirmed_by_the_clinician_before_it_is_written(self):
        # **Caught in review, on this branch, after the collector ruling landed.**
        # Step 8 added a third artifact and steps 1 and 9 still enumerated two,
        # so the model was built with no re-run check in front of it and no
        # confirmation behind it. That is the wrong artifact to drop: ``voice.md``
        # §9 says a model cannot be verified by the run that built it, which
        # makes *Confirm, then write* the only verification that exists.
        setup = read(SETUP)
        self.assertIn("`scratch/voice-model.md` and `scratch/shorthand.md`", setup)
        self.assertIn("Let the clinician edit before writing", setup)
        self.assertIn("this step is the whole verification", setup)

    def test_a_rerun_looks_for_the_model_before_it_asks(self):
        # Step 1 owns re-run detection. Without the model on its list a returning
        # clinician is asked for writing he already handed over, or asked again
        # after declining -- and the refusal step 8 records in the profile is
        # only ever read here.
        self.assertIn("`writing-samples/` or `shorthand.md` already exist", read(SETUP))

    def test_the_quote_rule_names_its_audience_rather_than_its_channel(self):
        # **The first build of a real model is what caught this.** The rule read
        # *never leaves scratch/, not into a summary handed back in conversation*,
        # which forbids the *Confirm, then write* step outright -- and §9 says that
        # confirmation is the only verification a voice model has. A rule that
        # bans the one check reads as caution and leaves the model unverifiable.
        #
        # **The first version of this test failed on the file it was written
        # for**, and the reason is worth keeping: it asserted the retired
        # wording was absent, and the paragraph recording the retirement quotes
        # it. That is ``spelling_scan.py``'s mention-versus-use distinction
        # arriving in an assertion -- a rule stated and a rule quoted as retired
        # are not the same string in the same role. So the check is that the new
        # rule is stated and that the old one appears only in its retirement.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("never goes anywhere the author is not the audience", voice)
        self.assertIn("It read *never leaves", voice)

    def test_the_paired_version_and_the_co_written_sample_are_both_written_down(self):
        # Two things the samples taught the method rather than the other way
        # round, and neither was predicted. A paired document yields a pair whose
        # generic half is **attested** rather than composed; a co-written one
        # models the co-author, which is §6's trap with the sign flipped and is
        # harder to see because the result reads better rather than worse.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("where both halves are attested", voice)
        self.assertIn("a sample somebody else helped write", voice)

    def test_the_default_is_full_voice_and_damping_is_not_a_register(self):
        # **This rule was written backwards first and the clinician reversed it
        # within the hour**, which is why it is pinned rather than left to prose.
        # Two damped documents were read as evidence of a register he uses for
        # academic audiences, and the correction was *"i don't want this to be
        # tame because that is not me, those were outliers."*
        #
        # **The failure it now guards runs one way and is the worse one.** A
        # model that treats damping as a register produces a tame draft **and can
        # cite the author's own corpus in its defense** -- which is #213 closed by
        # institutionalizing the defect it was filed on. So the assertion is on
        # the default, on the named-constraint limb that is the only way down
        # from it, and on the damped samples being pairs rather than targets.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("The default is full voice", voice)
        self.assertIn("Intensity is only ever reduced against a constraint the author names", voice)
        self.assertIn("Constraints on the setting", voice)

    def test_the_defect_list_is_cited_rather_than_copied(self):
        # #143: a list restated in two files goes stale in one of them. §12 owns
        # the mechanical defects; ``voice.md`` §6 is the rule that a model must
        # not imitate them, which is a different claim and needs no second copy.
        voice = read(CASE_STUDY_VOICE)
        self.assertIn("deliberately not restated here", voice)
        self.assertProseNotIn("isvery commonand", voice)


class TheExportMethodHasOneConsumerContract(ProseBind, unittest.TestCase):
    """#400's export option crosses setup, the voice method and one reader.

    A clinician using another assistant must be offered the same corpus-grade
    route without being sent to a tool whose input it cannot read. The shared
    Markdown sheet owns that route; ``voice_corpus.py`` is the ChatGPT worked
    implementation rather than a claim that every vendor shape is supported.
    """

    def test_setup_and_voice_point_to_the_vendor_neutral_method(self):
        corpus_method = read(VOICE_CORPUS_REFERENCE)
        self.assertIn("voice_corpus.py", corpus_method)
        self.assertIn("reference implementation", corpus_method)
        self.assertIn("voice-corpus.md", read(SETUP))
        self.assertIn("voice-corpus.md", read(CASE_STUDY_VOICE))

    def test_the_method_publishes_the_complete_walk_and_report(self):
        corpus_method = read(VOICE_CORPUS_REFERENCE)
        for required in (
            "population off the export's structure",
            "classes sum to that population",
            "unrecognized type",
            "export's own timestamp",
            "distinct conversation",
            "hop distribution",
            "Only typed text",
            "Counts only by default",
            "exits non-zero",
            "population by role",
            "unread remainder",
            "undated count",
        ):
            with self.subTest(required=required):
                self.assertIn(required, corpus_method)

    def test_the_reference_implementation_states_the_converter_shape(self):
        module = read(VOICE_CORPUS_MODULE)
        for required in (
            "Converter contract",
            "top-level JSON list",
            "mapping",
            "author.role",
            "content_type",
            "create_time",
            "voice-corpus.md",
        ):
            with self.subTest(required=required):
                self.assertIn(required, module)

    def test_the_contract_does_not_claim_a_runtime_change_to_the_existing_reader(self):
        corpus_method = read(VOICE_CORPUS_REFERENCE)
        self.assertProseIn("changes no runtime behavior", corpus_method)
        self.assertProseIn("converter's own counts-only report", corpus_method)

    def test_the_export_is_optional_and_consent_is_staged(self):
        voice = read(CASE_STUDY_VOICE)
        for required in (
            "Writing samples come first",
            "offered as an enhancement",
            "ChatGPT, Claude, Grok",
            "first yes",
            "counts-only run",
            "second yes",
            "real figures",
            "ten named conversations",
            "coverage-driven second ask",
        ):
            with self.subTest(required=required):
                self.assertProseIn(required, voice)

    def test_setup_records_an_export_no_separately_from_the_whole_step(self):
        setup = read(SETUP)
        self.assertProseIn("export refusal separately", setup)
        self.assertProseIn("whole voice-model step", setup)

    def test_the_model_records_source_and_confirmation_does_not_amplify(self):
        voice = read(CASE_STUDY_VOICE)
        setup = read(SETUP)
        for required in (
            "| Register | Coverage | Source |",
            "A finding is a floor, not a target",
            "Withheld findings: <n>",
        ):
            with self.subTest(required=required):
                self.assertIn(required, voice)
        self.assertIn("two-tier rows", setup)
        self.assertIn("direction", setup)
        self.assertIn("per-register coverage and its source", setup)
        self.assertIn("withheld count", setup)

class TheReferenceDeclaresWhichFieldsItHoldsValuesFor(unittest.TestCase):
    """#222's ruling of 2026-08-18: a declared inventory, and it states its own gap.

    #212 emptied the per-account picklists out of the reference and left nothing
    that would notice a new one arriving. The ticket offered three ways to fix
    that and the clinician took the middle one: **the reference names, once, the
    exact set of fields it holds values for**, and this class asserts the file
    holds values for exactly those and no others. So a ninth picklist cannot land
    quietly -- it forces a one-line diff in a sentence whose entire subject is
    *is this universal?*, which is a better review surface than the whole file.

    **What it reaches is a field label; what it cannot reach is a value, and the
    reference says so beside the inventory.** The preceptor and site lists were
    fenced values under a bold label, so they are reachable wherever in the file
    they land. A site name appended to the ``Case Type`` list is not, and neither
    was the ``Primary Payment Method`` rule -- a **pipe table keyed on site
    names** under a different heading. No structural test tells one site name
    from one payer string without exactly the vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build and #212 re-ruled. **A green run here is not a walked
    file**, which is ``differential_scan.py``'s *a clean scan is not a walked
    row* arriving on a document instead of a run.

    **The decision 2 the ticket proposed was weaker than this and would have
    caught neither defect.** It asked the reference to declare an allow-list of
    *headings* it owns -- and both defects arrived under headings the reference
    legitimately owns, the picklists under *Picklists* and the payer table under
    *Field selection rules*. The unit had to drop to the field for the check to
    have any grip at all. Re-derived from ``c588e2f`` rather than taken from the
    ticket body.

    **The inventory names fields, never values**, so nothing here puts an account
    back in the tree that ``ThePerAccountPicklistsAreNotInTheReference`` above
    just emptied.
    """

    #: The inventory sentence's opener. Held once because the parse and the
    #: presence check must key on the same string, and two copies is how they
    #: drift apart.
    INVENTORY_OPENER = "**This file holds values for exactly these fields"

    def declared_fields(self):
        for line in read(MEDATRAX).splitlines():
            if line.startswith(self.INVENTORY_OPENER):
                _, _, tail = line.partition(":**")
                return [part.strip() for part in tail.split("·") if part.strip()]
        raise AssertionError(
            "reference/medatrax-fields.md declares no field inventory under Picklists"
        )

    def labeled_fields(self):
        """Every ``**Field:**`` line opener in the file, bar the inventory itself.

        A value line is bold, colon-terminated **inside** the bold span, and at
        the start of its line. The pointer paragraph -- *Preceptor and Location /
        Site are per-account* -- and the override sweep both end their bold span
        with a period rather than a colon, so neither is read as a field. Checked
        against the real file rather than assumed.

        **The whole file, and a first version of this read one section.** The
        ticket's hole is a per-account value arriving *under some other heading*,
        so a bounded read answers a narrower question than the one asked -- and
        worse, it was escapable by adding a heading, since the terminator matched
        ``###`` as well as ``##``. The paragraph fenced off behind such a heading
        is reworded now instead. Found by the spec axis of the review.

        **Prose that does open that way is read as a field, and the reference says
        so beside the inventory.** The paragraph naming what this check cannot
        reach tripped it while being written, which is ``differential_scan``'s
        *describing the rule broke the tool that checks the rule* arriving a third
        time. The parse stays blunt anyway: telling a label from a sentence is a
        judgment, and a judgment is the seam a ninth picklist would come through.
        """
        found = []
        for line in read(MEDATRAX).splitlines():
            if line.startswith(self.INVENTORY_OPENER):
                continue
            match = re.match(r"\*\*([^*]+):\*\*", line)
            if match:
                found.append(match.group(1).strip())
        return found

    def test_the_inventory_and_the_value_lines_agree(self):
        declared = self.declared_fields()
        labeled = self.labeled_fields()
        self.assertEqual(
            len(set(declared)), len(declared), "the inventory names a field twice"
        )
        undeclared = sorted(set(labeled) - set(declared))
        self.assertEqual(
            undeclared,
            [],
            "reference/medatrax-fields.md holds values for a field its inventory "
            "does not declare. Add it to the inventory sentence if it really is a "
            "Medatrax dropdown every account renders; move it to "
            "scratch/medatrax-profile.md if it is one account's; or reword it if "
            "it is prose that opened with a bold span ending in a colon, which is "
            f"the field-label form and cannot be told apart from one: {undeclared}",
        )
        stale = sorted(set(declared) - set(labeled))
        self.assertEqual(
            stale,
            [],
            f"the inventory declares a field the file no longer holds values for: {stale}",
        )

    def test_the_inventory_states_the_shape_it_cannot_reach(self):
        # **The load-bearing half of the ruling.** A gate that reaches one of two
        # shapes and does not say so reads as coverage it does not have, which is
        # the failure this repo names in every scanner it ships. Asserting the
        # sentence is what stops a tidy quietly upgrading the claim.
        text = read(MEDATRAX)
        self.assertIn("does not reach", text)
        self.assertIn("keyed on a site", text)

    def test_setup_does_not_call_an_inventoried_field_per_account(self):
        """The cross-file half, and the defect that was live when #222 was built.

        ``setup-clinical-skills`` step 4 read *Preceptors, sites, case types and
        Patient Time bands are per-account picklists* while the reference held
        Case Type's values and the Patient Time bands as universal. Both
        files read as coherent alone, which is this module's whole subject, and
        no assertion in the class above could see it. The clinician ruled
        2026-08-18 that the reference is right: Medatrax renders the same two
        dropdowns on every account, and what varies is the program's hour
        breakdown across the bands -- a different fact, in a different file.
        """
        sentences = [
            line for line in read(SETUP).splitlines()
            if "are per-account picklists" in line
        ]
        # **Every such line, not exactly one.** Requiring a single line would
        # report a rewrite of step 4 into two sentences as a contradiction, which
        # is the failure this module's own docstring rules against -- *a test
        # asserting a paragraph verbatim fails on every rewrite and teaches the
        # next session to delete it*. Caught by the standards axis of the review.
        self.assertTrue(
            sentences,
            "setup-clinical-skills no longer names which picklists are per-account",
        )
        for sentence in sentences:
            head = sentence.split("are per-account picklists")[0]
            claimed = [
                part.strip(" *`")
                for chunk in head.split(",")
                for part in chunk.split(" and ")
                if part.strip(" *`")
            ]
            for item in claimed:
                for field in self.declared_fields():
                    self.assertFalse(
                        names_the_same_field(item, field),
                        f"setup-clinical-skills calls {item!r} per-account while "
                        "reference/medatrax-fields.md holds its values as universal. "
                        "One of the two files is wrong",
                    )


class TheStepResolverIsLive(unittest.TestCase):
    """A resolver that named nothing would pass every assertion in the class below.

    Each case here is a shape taken off the real tree rather than invented, and
    the two marked *false alarm* are lines a simpler rule failed. They are the
    reason the resolver has three limbs instead of one.
    """

    NAMES = ["setup-clinical-skills", "practicum-case-study", "clinical-note", "batch-shift"]

    def resolve(self, text: str, owner: str | None = None) -> list[Citation]:
        return list(step_citations(text, owner, self.NAMES))

    def test_a_step_heading_is_read_and_a_numbered_list_is_not(self) -> None:
        """The hashes are load-bearing, and a list item must not inflate the set.

        Relax ``STEP_HEADING`` to tolerate a missing ``#`` and every ordinary
        numbered list in a ``SKILL.md`` registers as a declared step. The set
        inflates, and every stale citation then resolves clean -- the silent-pass
        shape, arriving through the half of the check nobody looks at.
        """
        self.assertEqual(declared_steps("icd10-cpt"), {1, 2, 3, 4, 5})
        self.assertEqual(declared_steps("setup-clinical-skills") & {0}, {0})
        for not_a_heading in ("1. Read the chart", "  ### 2. Indented", "##### 3. Too deep"):
            with self.subTest(line=not_a_heading):
                self.assertIsNone(STEP_HEADING.match(not_a_heading))
        self.assertEqual(STEP_HEADING.match("### 4. Draft the body").group(1), "4")

    def test_a_link_beside_the_words_names_the_skill(self) -> None:
        cite, = self.resolve("See [batch-shift](../batch-shift/SKILL.md) step 6.", "clinical-note")
        self.assertEqual((cite.skill, cite.number, cite.how), ("batch-shift", 6, "beside"))

    def test_a_backticked_name_beside_the_words_names_the_skill(self) -> None:
        """``anchor_scan.py`` and ``corpus_census.py`` cite this way, from ``tools/``."""
        cite, = self.resolve("``clinical-note`` step 1 rests on whole day files.")
        self.assertEqual((cite.skill, cite.how), ("clinical-note", "beside"))

    def test_a_bare_path_beside_the_words_names_the_skill(self) -> None:
        """``docx_write.py``'s form, and it is one of the citations #233 was filed over."""
        cite, = self.resolve("``skills/practicum-case-study/SKILL.md`` step 9's sentence.")
        self.assertEqual((cite.skill, cite.number), ("practicum-case-study", 9))

    def test_a_bare_citation_takes_the_skill_whose_file_it_is(self) -> None:
        cite, = self.resolve("| **Neither** | Report it -- see step 4 |", "batch-shift")
        self.assertEqual((cite.skill, cite.how), ("batch-shift", "owner"))

    def test_a_second_citation_carries_the_first_ones_subject(self) -> None:
        """``voice.md``'s *"step 5, before drafting, and step 9"*.

        The first resolves by ``owner`` rather than ``beside``, and that is the
        point of the case: a **relative** link back to the skill's own file
        spells no skill name anywhere, so only the directory settles it. The
        second then carries the first's subject.
        """
        first, second = self.resolve(
            "[SKILL.md](../SKILL.md) step 5, before drafting, and step 9, where the draft is read.",
            "practicum-case-study",
        )
        self.assertEqual((first.skill, first.how), ("practicum-case-study", "owner"))
        self.assertEqual((second.skill, second.how), ("practicum-case-study", "carried"))

    def test_a_relative_self_link_is_not_a_named_skill(self) -> None:
        """``[SKILL.md](../SKILL.md)`` names nothing, so outside ``skills/`` it is unresolved."""
        cite, = self.resolve("[SKILL.md](../SKILL.md) step 5, before drafting.", None)
        self.assertIsNone(cite.skill)

    def test_the_subject_carries_across_a_hard_wrap(self) -> None:
        """The paragraph is the scope, so a wrapped line does not restart it."""
        first, second = self.resolve(
            "[setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects it,\n"
            "on the same terms as the voice model in step 8.",
            "clinical-note",
        )
        self.assertEqual(first.skill, "setup-clinical-skills")
        self.assertEqual((second.skill, second.line, second.how), ("setup-clinical-skills", 2, "carried"))

    def test_a_hard_wrapped_citation_is_still_read(self) -> None:
        """No line in the tree wraps between the word and the number. One will."""
        cite, = self.resolve("...which is [batch-shift](../batch-shift/SKILL.md) step\n3.", "clinical-note")
        self.assertEqual((cite.skill, cite.number), ("batch-shift", 3))

    def test_a_name_in_between_breaks_the_carry(self) -> None:
        """False alarm 1, from ``setup-clinical-skills/SKILL.md``.

        *"[clinical-note] step 2 and [batch-shift], for step 9's shorthand"* --
        the ``step 9`` is ``setup``'s own, and both a nearest-name rule and a
        carry with no interruption clause resolve it to a skill with 7 steps and
        fail a correct line.
        """
        first, second = self.resolve(
            "**Hard** -- [clinical-note](../clinical-note/SKILL.md) step 2 and "
            "[batch-shift](../batch-shift/SKILL.md), for step 9's shorthand.",
            "setup-clinical-skills",
        )
        self.assertEqual(first.skill, "clinical-note")
        self.assertEqual((second.skill, second.how), ("setup-clinical-skills", "owner"))

    def test_a_sentence_boundary_does_not_carry_a_stale_subject(self) -> None:
        """False alarm 2, the other ``setup-clinical-skills`` line a nearest-name rule failed."""
        cites = self.resolve(
            "[clinical-note](../clinical-note/SKILL.md) expands shorthand at step 2. Read it\n"
            "before asking; it is not restated here, on step 8's arrangement.",
            "setup-clinical-skills",
        )
        self.assertEqual(cites[-1].skill, "setup-clinical-skills")

    def test_a_bare_citation_outside_a_skill_stays_unresolved(self) -> None:
        """``anchor_scan.py``'s ``step-4`` meant ``icd10-cpt`` and nothing here could know it.

        The line is that module's, as it stood before #238 named the skill beside
        it. Kept verbatim: the shape is what this grades, and a repaired tree is
        not a reason to stop testing the shape it was repaired out of.
        """
        cite, = self.resolve("# Step 4's heading. The lookbehind is load-bearing.", None)
        self.assertIsNone(cite.skill)

    def test_the_plural_opener_is_a_floor_and_says_so(self) -> None:
        """*steps 1 and 2* is read as a citation of 1. The 2 is missed, deliberately."""
        self.assertEqual([c.number for c in self.resolve("if steps 1 and 2 move", "batch-shift")], [1])


class TheDeadLinkResolverIsLive(unittest.TestCase):
    """#538's relative-link resolver is driven against synthetic text."""

    OWNER = Path("docs/adr/0054-relative-links.md")

    def test_a_good_slug_passes(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        exists = existing.__contains__

        self.assertEqual(
            dead_links("[ADR 0016](0016-real-record.md)", self.OWNER, exists),
            [],
        )

    def test_a_plausible_wrong_slug_fails(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        cases = (
            (
                "[ADR 0016](0016-plausible-record.md)",
                [(1, "0016-plausible-record.md")],
            ),
            (
                '[ADR 0016](0016-plausible-record.md "title")',
                [(1, "0016-plausible-record.md")],
            ),
            (
                "[ADR 0016](<0016 plausible record.md>)",
                [(1, "0016 plausible record.md")],
            ),
            (
                "[ADR 0016](0016-plausible(record).md)",
                [(1, "0016-plausible(record).md")],
            ),
            (
                "[ADR 0016][plausible]\n\n[plausible]: 0016-plausible-record.md",
                [(3, "0016-plausible-record.md")],
            ),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(dead_links(text, self.OWNER, existing.__contains__), expected)

    def test_an_anchor_is_dropped_without_hiding_a_missing_file(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        exists = existing.__contains__

        self.assertEqual(
            dead_links("[section](0016-real-record.md#ruling)", self.OWNER, exists),
            [],
        )
        self.assertEqual(
            dead_links("[section](0016-missing.md#ruling)", self.OWNER, exists),
            [(1, "0016-missing.md#ruling")],
        )

    def test_an_absolute_url_is_skipped_without_hiding_a_relative_target(self) -> None:
        exists = set().__contains__

        self.assertEqual(
            dead_links("[ticket](https://github.com/example/repo/issues/1)", self.OWNER, exists),
            [],
        )
        self.assertEqual(
            dead_links("[record](missing.md)", self.OWNER, exists),
            [(1, "missing.md")],
        )

    def test_code_targets_are_skipped_without_shifting_line_numbers(self) -> None:
        text = (
            "Inline example: `[record](missing.md)`\n"
            "```markdown\n"
            "[record](missing.md)\n"
            "```\n"
            "[record](missing.md)\n"
        )

        self.assertEqual(
            dead_links(text, self.OWNER, set().__contains__),
            [(5, "missing.md")],
        )

    def test_a_code_target_is_reported_when_unquoted(self) -> None:
        self.assertEqual(
            dead_links("[record](missing.md)", self.OWNER, set().__contains__),
            [(1, "missing.md")],
        )

    def test_graded_files_returns_a_nontrivial_population(self) -> None:
        files = graded_files()
        self.assertGreater(len(files), 50)
        self.assertIn(REPO_ROOT / "fixtures" / "day-a" / "shorthand" / "README.md", files)

    def test_resolution_uses_the_linking_files_directory(self) -> None:
        asked: list[Path] = []

        def record(path: Path) -> bool:
            asked.append(path)
            return True

        self.assertEqual(
            dead_links(
                "[fixture set](../README.md)",
                Path("fixtures/day-a/shorthand/README.md"),
                record,
            ),
            [],
        )
        self.assertEqual(asked, [Path("fixtures/day-a/README.md")])


class TheRulingOrdinalParserIsLive(unittest.TestCase):
    """#554's shared parser, driven before either tree-wide gate consumes it."""

    def test_addenda_continue_across_a_shape_change(self) -> None:
        record = next((REPO_ROOT / "docs" / "adr").glob("0049-*.md"))
        self.assertEqual(ruling_ordinals(read(record)), list(range(1, 12)))

    def test_a_restarted_addendum_sequence_is_ambiguous(self) -> None:
        text = """\
## Rulings

1. First ruling.
2. Second ruling.

## Addendum

**1. A second referent for ruling one.**
"""
        self.assertEqual(
            ruling_shape_findings(text),
            ["ruling 1 follows ruling 2; expected ruling 3"],
        )

    def test_the_bold_item_word_is_read_and_the_bare_continuation_is_not(self) -> None:
        record = """\
## Ruled 2026-01-01

**Ruling 1. A declared ruling.**
ruling 5. **The sharp reason is #545's own consequence 2 rather than the precedent.**
"""
        self.assertEqual(ruling_ordinals(record), [1])

    def test_decision_headings_are_read_but_point_and_rule_headings_are_not(self) -> None:
        record = """\
## Decision 1: a declared decision
## Point 2: citation vocabulary is not declaration vocabulary
## Rule 3: citation vocabulary is not declaration vocabulary
"""
        self.assertEqual(ruling_ordinals(record), [1])

    def test_the_four_live_alternate_spellings_resolve_to_their_ordinals(self) -> None:
        expected = {
            94: set(range(1, 7)),
            96: set(range(1, 6)),
            126: set(range(1, 9)),
            127: set(range(1, 10)),
        }
        declared = declared_rulings()
        self.assertEqual({number: declared[number] for number in expected}, expected)

    def test_the_alternate_declaration_spellings_belong_to_exactly_four_records(self) -> None:
        found = set()
        for record in sorted((REPO_ROOT / "docs" / "adr").glob("*.md")):
            text = read(record)
            without_alternates = "\n".join(
                ""
                if re.match(
                    r"^(?:\*\*ruling\s+\d+\.\s|#{2,4}\s+decision\s+\d+\b)",
                    line,
                    re.IGNORECASE,
                )
                else line
                for line in text.splitlines()
            )
            if ruling_ordinals(text) != ruling_ordinals(without_alternates):
                found.add(int(record.name[:4]))
        self.assertEqual(found, {94, 96, 126, 127})


class EveryADRHasOneRulingSequence(unittest.TestCase):
    """#554: one ordinal has one referent across a record and its addenda."""

    def test_every_record_has_one_monotonic_ruling_sequence(self) -> None:
        findings = []
        for record in sorted((REPO_ROOT / "docs" / "adr").glob("*.md")):
            findings.extend(
                f"{record.name}: {finding}"
                for finding in ruling_shape_findings(read(record))
            )
        self.assertEqual(findings, [])

    def test_every_empty_parse_is_declared_within_the_tree_ceiling(self) -> None:
        records = sorted((REPO_ROOT / "docs" / "adr").glob("*.md"))
        findings = [
            f"{record.name}: {finding}"
            for record in records
            for finding in unnumbered_ruling_findings(read(record))
        ]
        findings.extend(
            unnumbered_ruling_ceiling_findings([read(record) for record in records])
        )
        self.assertEqual(findings, [])


class AnEmptyRulingParseIsDeclared(unittest.TestCase):
    """#759: an empty parse is deliberate and the declaration is bounded."""

    MARKER = "<!-- no-numbered-rulings -->"

    def test_an_empty_parse_without_the_marker_fails(self) -> None:
        self.assertEqual(
            unnumbered_ruling_findings("# A record with no numbered rulings"),
            ["an empty ruling parse lacks the no-numbered-rulings marker"],
        )

    def test_an_empty_parse_with_the_marker_passes(self) -> None:
        self.assertEqual(
            unnumbered_ruling_findings(
                "# A record with no numbered rulings\n\n" + self.MARKER
            ),
            [],
        )

    def test_a_marker_mentioned_inside_prose_is_not_a_declaration(self) -> None:
        self.assertEqual(
            unnumbered_ruling_findings(
                "# A record\n\nThe text mentions <!-- no-numbered-rulings --> here."
            ),
            ["an empty ruling parse lacks the no-numbered-rulings marker"],
        )

    def test_a_marker_shown_inside_a_fence_is_not_a_declaration(self) -> None:
        record = """\
# A record

```text
<!-- no-numbered-rulings -->
```
"""
        self.assertEqual(
            unnumbered_ruling_findings(record),
            ["an empty ruling parse lacks the no-numbered-rulings marker"],
        )

    def test_a_nineteenth_marker_breaks_the_ceiling(self) -> None:
        texts = [self.MARKER] * 19
        self.assertEqual(
            unnumbered_ruling_ceiling_findings(texts),
            ["19 no-numbered-rulings markers exceed the ceiling of 18"],
        )


class TheRulingCitationResolverIsLive(unittest.TestCase):
    """#554's four coordinate words and adjacency bound, driven synthetically."""

    def test_all_four_coordinate_words_are_read(self) -> None:
        text = "\n".join(
            (
                "ADR 0016 ruling 1",
                "ADR 0016's point 2",
                "[ADR 0016](0016-record.md) decision 3",
                "[ADR 0016](0016-record.md)'s rule 4",
            )
        )
        self.assertEqual(
            [(cite.record, cite.number, cite.word) for cite in ruling_citations(text)],
            [(16, 1, "ruling"), (16, 2, "point"), (16, 3, "decision"), (16, 4, "rule")],
        )

    def test_proximity_does_not_bind_an_ordinal_to_the_wrong_record(self) -> None:
        text = "ADR 0016's terms leave ruling 4 beside another subject"
        self.assertEqual(list(ruling_citations(text)), [])

    def test_a_dangling_ordinal_is_caught_against_the_shared_parser(self) -> None:
        record = next((REPO_ROOT / "docs" / "adr").glob("0030-*.md"))
        declared = {30: set(ruling_ordinals(read(record)))}
        self.assertEqual(
            unresolved_ruling_citations("ADR 0030 ruling 9", declared),
            ["1: ADR 0030 ruling 9 does not exist"],
        )


class TheRulingCitationMarkerIsNarrow(unittest.TestCase):
    """#554's counted next-paragraph marker is a declaration, not an opt-out."""

    MARKER = "<!-- unresolved-ruling-citations: 1 -->"
    DECLARED = {30: set(range(1, 9))}

    def complain(self, *blocks: str) -> list[str]:
        return unresolved_ruling_citations("\n\n".join(blocks), self.DECLARED)

    def test_the_marker_covers_only_the_next_paragraph(self) -> None:
        self.assertEqual(
            self.complain(self.MARKER, "quoted ADR 0030 ruling 9", "later ADR 0030 ruling 10"),
            ["5: ADR 0030 ruling 10 does not exist"],
        )

    def test_a_second_mention_in_the_paragraph_fails_the_count(self) -> None:
        self.assertEqual(
            self.complain(self.MARKER, "ADR 0030 ruling 9 and ADR 0030 ruling 10"),
            ["1: declares 1, paragraph holds 2"],
        )

    def test_a_stale_marker_fails(self) -> None:
        self.assertEqual(
            self.complain(self.MARKER, "this paragraph cites nothing"),
            ["1: declares 1, paragraph holds 0"],
        )

    def test_zero_exempts_nothing(self) -> None:
        marker = "<!-- unresolved-ruling-citations: 0 -->"
        self.assertEqual(
            self.complain(marker, "ADR 0030 ruling 9"),
            [
                "1: a marker declaring nothing exempts nothing",
                "3: ADR 0030 ruling 9 does not exist",
            ],
        )

    def test_three_declared_mentions_exceed_the_global_ceiling(self) -> None:
        texts = [self.MARKER + "\n\nADR 0030 ruling 9"] * 3
        self.assertEqual(
            ruling_marker_ceiling_findings(texts),
            ["3 unresolved ruling citations exceed the ceiling of 2"],
        )


class EveryCitedRulingResolvesToADeclaredRuling(unittest.TestCase):
    """#554's third walker: every adjacent ADR coordinate joins to that record."""

    DECLARED_LIMITS = (
        (
            "adjacent-ruling-slip",
            "An in-range ordinal can resolve to the wrong ruling; existence is not meaning.",
            "ADR 0075 ruling 9 records two observed slips that no existence join can see.",
        ),
        (
            "line-coordinates",
            "File and glossary line coordinates move when text is inserted above them.",
            "ADR 0075 ruling 9 records the unrelated-commit false-alarm cost.",
        ),
        (
            "tracker-text",
            "Issue, pull-request, and comment prose is outside graded_files().",
            "ADR 0075 ruling 4 uses #554's own title as the counterexample.",
        ),
        (
            "possessive-drift",
            "An ordinal not adjacent to its ADR is deliberately left unread.",
            "ADR 0075 ruling 6 records the measured false positives from proximity.",
        ),
        (
            "ticket-number-citations",
            "A #N citation would require a join against the tracker, not this tree.",
            "ADR 0075 ruling 9 keeps the tracker surface outside this mechanism.",
        ),
    )

    def test_the_declared_limit_population_is_the_five_ruled_rows(self) -> None:
        self.assertEqual(
            [key for key, _limit, _evidence in self.DECLARED_LIMITS],
            [
                "adjacent-ruling-slip",
                "line-coordinates",
                "tracker-text",
                "possessive-drift",
                "ticket-number-citations",
            ],
        )
        for _key, limit, evidence in self.DECLARED_LIMITS:
            self.assertTrue(limit)
            self.assertTrue(evidence)

    def test_the_walk_reads_a_nontrivial_live_population_in_all_four_words(self) -> None:
        citations = [cite for _path, cite in walk_ruling_citations()]
        self.assertGreater(len(citations), 100)
        self.assertEqual({cite.word for cite in citations}, {"ruling", "point", "decision", "rule"})

    def test_the_gate_and_resolver_share_the_record_parser(self) -> None:
        declared = declared_rulings()
        self.assertEqual(declared[49], set(range(1, 12)))

    def test_a_fenced_specimen_heading_does_not_close_the_ruling_section(self) -> None:
        """A ``## `` line inside a fence is a specimen, not document structure.

        ADR 0087's ruling 2 shows a record shape whose first line is
        ``## RENDERED: post.md``. Read as an H2 it took the ruling section down
        and hid rulings 3 to 9, so every tree-side citation of them failed while
        nothing exercised one. The live record is asserted beside the synthetic
        case because the synthetic one cannot go stale into agreement.
        """

        record = "\n".join(
            (
                "# A record",
                "",
                "## Ruled 2026-01-01",
                "",
                "### 1. The first",
                "",
                "```text",
                "## SPECIMEN: a shape a ruling shows",
                "```",
                "",
                "### 2. The second",
                "",
                "## What this does not reach",
                "",
                "### 3. Not a ruling",
            )
        )
        self.assertEqual(ruling_ordinals(record), [1, 2])
        self.assertEqual(declared_rulings()[87], set(range(1, 10)))

    def test_only_the_opening_marker_closes_a_fence(self) -> None:
        record = "\n".join(
            (
                "## Ruled 2026-01-01",
                "",
                "~~~text",
                "```",
                "## SPECIMEN: still inside the outer fence",
                "~~~",
                "",
                "### 1. The first",
            )
        )
        self.assertEqual(ruling_ordinals(record), [1])

    def test_every_tree_side_coordinate_resolves(self) -> None:
        declared = declared_rulings()
        findings = []
        for path in graded_files():
            findings.extend(
                f"{path.relative_to(REPO_ROOT).as_posix()}:{finding}"
                for finding in unresolved_ruling_citations(read(path), declared)
            )
        self.assertEqual(findings, [])

    def test_the_global_marker_ceiling_is_held(self) -> None:
        self.assertEqual(
            ruling_marker_ceiling_findings([read(path) for path in graded_files()]),
            [],
        )


class TheTwoRootDocumentsAreNotOneKind(unittest.TestCase):
    """The evidence ``ROOT_DOCUMENTS``' split rests on, pinned rather than stated.

    #246 put ``AGENTS.md`` and ``CLAUDE.md`` in one row and they were ruled
    apart, which makes the asymmetry between them load-bearing: it is the whole
    argument for one document taking an escape hatch and the other refusing one.
    **A self-serving ruling whose evidence is a figure nobody re-derives is the
    weakest shape this repo has**, and a draft of that docstring shipped exactly
    that -- a line count already wrong when written, and a match count with no
    pattern beside it.

    **Floors, on ``test_each_limb_of_the_resolver_carries_real_citations``'s
    reasoning**, and deliberately far under today's measurement so the next
    paragraph anybody appends cannot move them. What they assert is the *kind*
    of difference, not its size: a short contract against a long file that
    describes machinery.
    """

    def counts(self, path: Path) -> tuple[int, int]:
        lines = read(path).splitlines()
        return len(lines), sum(1 for line in lines if CHECKER_PROSE.search(line))

    def test_the_consumer_document_is_the_short_one(self) -> None:
        long_lines, _ = self.counts(REPO_ROOT / "CLAUDE.md")
        short_lines, _ = self.counts(REPO_ROOT / "AGENTS.md")
        self.assertGreater(long_lines, short_lines * 5)

    def test_only_the_maintainer_document_describes_the_checkers(self) -> None:
        """The half that matters: mention-versus-use lands where checkers are written up."""
        _, long_prose = self.counts(REPO_ROOT / "CLAUDE.md")
        _, short_prose = self.counts(REPO_ROOT / "AGENTS.md")
        # The instrument is live. A pattern matching nothing would satisfy the
        # ratio below vacuously, which is the silent-pass shape this whole
        # directory exists to refuse.
        self.assertGreater(short_prose, 0, "CHECKER_PROSE matched nothing in AGENTS.md")
        self.assertGreater(long_prose, short_prose * 5)


class TheExemptionMarkerIsNarrow(unittest.TestCase):
    """#246's escape hatch, exercised against text the tree does not hold.

    **The gate above asserts the two root documents are clean, which proves the
    walk found nothing.** These cases point ``undeclared_citations`` at a bare
    citation, a miscounted marker and a stale one, and watch it complain. Only
    the second is evidence, which is ``stale_citations``'s own argument arriving
    on the check built beside it.

    **Every hostile string here is synthetic**, and it has to be: this module is
    dropped from ``graded_files`` precisely so its own test material cannot fail
    the tree, and a marker typed into a real document to exercise a test would
    be a license granted for the test's benefit.
    """

    NAMES = ["setup-clinical-skills", "practicum-case-study", "clinical-note", "batch-shift"]
    MARKER = "<!-- unresolved-step-citations: 1 -->"

    def complain(self, *blocks: str) -> list[str]:
        return undeclared_citations("\n\n".join(blocks), self.NAMES, hatch=True)

    def test_a_bare_citation_at_the_root_is_caught(self) -> None:
        """The whole reason the gate exists. ``owner`` is None outside ``skills/``."""
        self.assertEqual(self.complain("a reader following step 7 lands elsewhere"), 
                         ["1: step 7 names no skill"])

    def test_naming_the_skill_beside_the_words_clears_it(self) -> None:
        """#238's repair, and the price #246 assumed for all twelve."""
        self.assertEqual(self.complain("walked by `practicum-case-study` step 7"), [])

    def test_a_declared_citation_is_exempt_and_only_within_its_paragraph(self) -> None:
        """The marker covers the next paragraph and stops there.

        A span running to the end of the document would swallow every citation
        below it, which is ``differential_scan.py``'s refusal clause bug exactly
        -- the mirror of the hole the thing exists to close.
        """
        self.assertEqual(
            self.complain(self.MARKER, "quoted: *'see step 7'*", "and later, a bare step 4"),
            ["5: step 4 names no skill"],
        )

    def test_a_second_citation_wandering_into_an_exempt_paragraph_is_caught(self) -> None:
        """A count, not a license. This is the difference between an opt-out and an off switch."""
        self.assertEqual(
            self.complain(self.MARKER, "quoted: *'see step 7'*, and also a fresh step 4"),
            ["1: declares 1, paragraph holds 2"],
        )

    def test_a_marker_left_behind_by_a_rewrite_is_caught(self) -> None:
        """A license nobody is using, and nothing else would ever notice."""
        self.assertEqual(
            self.complain(self.MARKER, "this paragraph cites nothing at all"),
            ["1: declares 1, paragraph holds 0"],
        )

    def test_a_marker_with_nothing_under_it_covers_itself(self) -> None:
        """So it reports zero against its own declaration rather than reaching forward."""
        self.assertEqual(self.complain("a bare step 4", self.MARKER),
                         ["1: step 4 names no skill", "3: declares 1, paragraph holds 0"])

    def test_a_marker_glued_to_its_paragraph_is_not_read_as_one(self) -> None:
        """``paragraphs`` reads the two as one block, and the paragraph stays graded.

        The safe direction to be wrong in, and it is ``phi_scan.py``'s own-line
        pragma rule rather than a new one.
        """
        glued = self.MARKER + "\nquoted: *'see step 7'*"
        self.assertEqual(self.complain(glued), ["2: step 7 names no skill"])

    def test_a_marker_mentioned_mid_sentence_is_not_a_marker(self) -> None:
        """Otherwise a paragraph explaining the marker exempts itself by explaining it.

        Two files once did exactly that to ``phi_scan`` merely by documenting
        its pragma near the top, and ``CLAUDE.md``'s section about this rule is
        the one paragraph in the repo most likely to try it.
        """
        prose = "declare it with an " + self.MARKER + " line, or the bare step 7 fails"
        self.assertEqual(self.complain(prose), ["1: step 7 names no skill"])

    def test_the_consumer_document_takes_no_marker_even_a_correct_one(self) -> None:
        """``AGENTS.md``'s half of the split ruling, and it is asserted rather than described.

        A marker that would have been perfectly well-formed in ``CLAUDE.md`` is
        a complaint here **and** leaves the citation beneath it loose. Reporting
        only the second would let the hatch drift into the consumer document one
        silent marker at a time; reporting only the first would let the marker be
        deleted and the citation stay hidden.
        """
        self.assertEqual(
            undeclared_citations(
                self.MARKER + "\n\nquoted: *'see step 7'*", self.NAMES, hatch=False
            ),
            ["1: this document takes no exemption marker", "3: step 7 names no skill"],
        )

    def test_the_maintainer_document_takes_the_same_marker(self) -> None:
        """The other half. Same text, same parser, one ruling apart."""
        self.assertEqual(
            undeclared_citations(
                self.MARKER + "\n\nquoted: *'see step 7'*", self.NAMES, hatch=True
            ),
            [],
        )

    def test_a_marker_declaring_nothing_exempts_nothing(self) -> None:
        self.assertEqual(
            self.complain("<!-- unresolved-step-citations: 0 -->", "a bare step 4"),
            ["1: a marker declaring nothing exempts nothing", "3: step 4 names no skill"],
        )


class EveryRelativeLinkResolvesToAnIndexedPath(unittest.TestCase):
    """#538: every relative link in ``graded_files()`` resolves in the index.

    Five limits are declared here. Absolute URLs are outside this tracked-file
    check. Targets inside fences or code spans are examples rather than links.
    Anchor fragments are dropped, so headings are not verified. A resolving
    target is not read to establish that it is the right target. A directory
    target establishes only that the directory has an indexed descendant.

    The untracked-file window and the preserved-run-record exclusion are the
    inherited limits declared at ``graded_files()`` and are not repeated here.
    """

    def indexed_paths(self) -> set[str]:
        """Exact-case tracked files and the directories derived from them.

        A clean result covers only those tracked paths; see ``graded_files()``
        for the untracked-file window.
        """
        finished = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        indexed = {line for line in finished.stdout.splitlines() if line.strip()}
        for path in tuple(indexed):
            parent = posixpath.dirname(path)
            while parent:
                indexed.add(parent)
                parent = posixpath.dirname(parent)
        return indexed

    def test_index_membership_is_exact_case(self) -> None:
        indexed = self.indexed_paths()
        self.assertIn("CONTEXT.md", indexed)
        self.assertNotIn("context.md", indexed)

    def test_every_relative_link_resolves(self) -> None:
        files = [path for path in graded_files() if path.suffix == ".md"]
        self.assertGreater(len(files), 50, "graded_files returned too little to be a checkout")

        indexed = self.indexed_paths()

        resolved: list[Path] = []

        def exists(path: Path) -> bool:
            resolved.append(path)
            return path.as_posix() in indexed

        dead = [
            f"{path.relative_to(REPO_ROOT).as_posix()}:{line}: {target}"
            for path in files
            for line, target in dead_links(
                read(path), path.relative_to(REPO_ROOT), exists
            )
        ]
        self.assertGreater(len(resolved), 50, "the relative-link matcher read too little")
        self.assertEqual(dead, [], "dead relative links:\n" + "\n".join(dead))


class EveryCitedStepResolvesToADeclaredStep(unittest.TestCase):
    """#233: a ``step N`` citation must point at a step that exists.

    **Two renumberings in a week, and correctness rested on somebody
    remembering.** ``setup-clinical-skills``'s silently redirected ``voice.md``'s
    citation; ``practicum-case-study``'s on #214 moved seven citations across
    five files and all seven re-derive correct only because the author went
    looking with a ``grep``. Nothing required that, and nothing would have failed
    if one had been missed. A reader following *"see step 7"* to the wrong step
    gets a coherent, wrong answer, which is worse than landing on nothing.

    **What it reaches, and the gap is the sharper half.** It catches a citation
    to a step that does not exist. It cannot catch a citation to a step that
    still exists and now **means something else** -- insert a step at the top and
    every number below it shifts, and only citations at or above the old maximum
    come back missing. On #214, steps 3 to 8 became 4 to 9: the four ``step 9``
    citations would have fired and the ``step 5``, ``6`` and ``7`` ones would
    have resolved silently to the wrong step. **A green run here is not a walked
    citation**, which is ``differential_scan.py``'s *a clean scan is not a walked
    row* arriving on a cross-reference.

    **A minority of citations are unresolved and are never failed.** Guessing
    would have been the alternative, and this class asserts a floor on each limb
    below so that a resolver quietly falling back to *unresolved* for everything
    cannot read as a clean run.

    **``tools/`` is no longer among them, and that half is now a rule.**
    [#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238)
    priced the repair -- ``anchor_scan.py`` alone said ``step-4`` six times
    meaning ``icd10-cpt`` -- and it was prose, not a parser change.
    ``test_every_citation_in_tools_resolves`` keeps it, because a reword that
    dropped a name would put those citations back out of reach in silence. **The
    repo root followed on #246**, ruled apart into a document that takes no escape
    hatch and one that takes a counted three. What stays unresolved is
    ``fixtures/`` prose, left deliberately: several of those sentences name a
    skill **as it stood at run time**.

    **No count is stated here, and the reason is that the first draft's went
    stale before it was merged.** It read *38 unresolved* against a tree that had
    120 resolved; merging ``origin/main`` the same day -- #226 and #228, neither
    of which has anything to do with this ticket -- moved both, because every
    paragraph either adds carries a citation or does not. That is
    [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)
    exactly: **a measurement's expiry date is the next commit to the thing it
    measures**, and here the thing measured is the whole tracked tree. Anything
    wanting the live numbers runs this module's own ``step_citations`` over
    ``graded_files()``, which is one loop and cannot go stale.
    """

    def declared(self) -> dict[str, set[int]]:
        return {name: declared_steps(name) for name in skill_names()}

    def test_the_walk_reaches_the_repo(self) -> None:
        files = graded_files()
        self.assertGreater(len(files), 50, "git ls-files returned too little to be a checkout")
        self.assertIn(REPO_ROOT / "CLAUDE.md", files)
        self.assertIn(CASE_STUDY_VOICE, files)

    def test_the_walk_grades_fixture_prose_and_not_the_records(self) -> None:
        """A record cites the skill as it stood at run time and may not be edited."""
        walked = {path.relative_to(REPO_ROOT).as_posix() for path in graded_files()}
        self.assertIn("fixtures/README.md", walked)
        self.assertIn("fixtures/filled-anchor/assertions.md", walked)
        self.assertNotIn("fixtures/filled-anchor/notes/case-01.md", walked)
        self.assertNotIn("fixtures/filled-anchor/run-2/case-01.md", walked)

    def test_the_walk_drops_this_module_and_only_this_module(self) -> None:
        """Asserted rather than described, on ``test_run_record_claim.py``'s lesson."""
        walked = graded_files()
        self.assertNotIn(SELF, [path.resolve() for path in walked])
        self.assertIn(REPO_ROOT / "tools" / "test_run_record_claim.py", walked)

    def test_every_skill_declares_steps(self) -> None:
        """A heading pattern that matched nothing would grade every citation clean.

        The floor is 3 and not the 5 the shortest skill happens to declare today.
        ``icd10-cpt`` has exactly five steps, so a floor of 5 would go red the
        first time somebody folded its E/M step into the one above -- a content
        decision with nothing to do with #233, reported as a broken regex.
        """
        for name in skill_names():
            with self.subTest(skill=name):
                self.assertGreaterEqual(len(declared_steps(name)), 3)

    def test_each_limb_of_the_resolver_carries_real_citations(self) -> None:
        """Floors, not counts. A limb that stopped firing must not read as clean.

        **Deliberately well below what the tree holds**, and the margin is the
        whole design: a figure pinned at the measurement is
        [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
        and would fail on the next paragraph anybody writes. That is not
        hypothetical here -- the numbers this docstring first quoted were stale
        within the day, moved by a merge from two tickets unrelated to this one.
        The floors were not, which is the argument for stating a bound rather
        than a measurement.
        """
        seen = {"beside": 0, "carried": 0, "owner": 0, "unresolved": 0}
        for _path, cite in walk_citations():
            seen[cite.how if cite.skill else "unresolved"] += 1
        for limb, floor in (("beside", 20), ("carried", 5), ("owner", 25)):
            with self.subTest(limb=limb):
                self.assertGreaterEqual(seen[limb], floor)

    def test_the_unresolved_limb_is_reported_and_never_floored(self) -> None:
        """The gap is counted, and deliberately has **no** floor under it.

        A floor on ``unresolved`` would assert that the gap persists, so teaching
        ``anchor_scan.py`` to name ``icd10-cpt`` beside its six ``step-4``
        mentions -- which is exactly the repair #233 invited -- would have turned
        the suite red for an improvement. **#238 then made that repair**, so this
        is no longer a hypothetical: an early draft carrying a floor here would
        have gone red on it. The three limbs above are what keep a resolver that
        quietly resolved *nothing* from reading as a clean run.
        """
        unresolved = [cite for _path, cite in walk_citations() if cite.skill is None]
        self.assertEqual([cite for cite in unresolved if cite.how != "owner"], [])

    def test_shared_instructions_never_depend_on_an_owning_skill(self) -> None:
        """#758: a shared sheet has no owner, so every step names its skill."""
        shared = SKILLS_DIR / "_shared"
        names = skill_names()
        unresolved = [
            f"{path.relative_to(REPO_ROOT)}:{cite.line}: step {cite.number}"
            for path in graded_files()
            if path.is_relative_to(shared)
            for cite in step_citations(read(path), None, names)
            if cite.skill is None
        ]
        self.assertEqual(unresolved, [])

    def test_every_citation_in_tools_resolves(self) -> None:
        """#238: a ``tools/`` module names the skill whose step it cites.

        **The repair was prose, and nothing held it.** A bare ``step-4`` cited a
        skill whose steps could be renumbered tomorrow with nothing to notice,
        because unresolved is never failed. Naming the skill once per paragraph
        converted every such citation in the directory with **no change to the
        resolver**, which is why #238 priced it as cheap -- and it is why a
        reword dropping a name would put them straight back, in silence. So the
        state is pinned rather than described. **The ticket enumerated ten in
        three modules and the directory held more**; no figure is repeated here,
        because the count moves with the next docstring anybody writes.

        **Scoped to ``tools/`` because that is where #238 stopped.** The
        citations still unresolved are in ``fixtures/`` prose and the repo-root
        documents. The fixture half is left deliberately: several of those
        sentences name a skill **as it stood at run time**, and rewording one to
        resolve risks making a historical statement read as a current one. That
        is a judgment rather than a mechanical fix, and it is not this test's.

        **What it costs, stated because it is real.** A ``tools/`` docstring
        writing *step 2 of the rebuild* -- a step of something that is not a
        skill at all -- fails here, and the only remedy is a reword. Every
        ``step N`` in ``tools/`` today is a skill's step, so the rule costs
        nothing now; it is a bet that the next one will be too, and the ticket's
        own *not worth doing at all* fork is the argument against it.

        **The whole subtree, and ``tools/testdata/`` carved out of it.** The
        first version tested ``path.parent`` and so reached the top level only:
        a ``tools/<subdir>/module.py`` would have escaped in silence, with both
        floors below still green, and it costs nothing today because no graded
        file sits below ``tools/`` bar one -- which is exactly why nobody would
        have noticed. ``tools/testdata/`` is then excluded on ``graded_files``'s
        own reasoning about ``fixtures/``: a sample of a catalog is a record of
        what one looks like, and editing it to name a skill would falsify the
        sample rather than fix a citation. It holds no ``step N`` today; the
        carve-out is for the sample that arrives tomorrow.
        """
        def in_scope(path: Path) -> bool:
            tools = REPO_ROOT / "tools"
            return tools in path.parents and (tools / "testdata") not in path.parents

        walked = [path for path in graded_files() if in_scope(path)]
        cites = [(path, cite) for path, cite in walk_citations() if in_scope(path)]
        # The instrument is live, on ``test_build_artifacts_ignored.py``'s
        # reasoning: a directory filter that selected nothing, or a directory
        # that stopped citing steps at all, would report a clean run and be
        # indistinguishable from one. ``anchor_scan.py`` is named because it is
        # the module #238 was filed over, and the floors are far under today's.
        self.assertGreater(len(walked), 20, "the tools/ filter selected too little")
        self.assertGreater(len(cites), 10, "no step citation in tools/ was read at all")
        self.assertIn(REPO_ROOT / "tools" / "anchor_scan.py", walked)
        self.assertEqual(
            [
                f"{path.relative_to(REPO_ROOT).as_posix()}:{cite.line} step {cite.number}"
                for path, cite in cites
                if cite.skill is None
            ],
            [],
            "a 'step N' in tools/ names no skill, so nothing checks it survives a "
            "renumbering. Name the skill beside the words -- once per paragraph is enough",
        )

    def test_every_citation_at_the_repo_root_resolves(self) -> None:
        """#246: ``CLAUDE.md`` and ``AGENTS.md`` name the skill whose step they cite.

        **The two documents with the most to lose and, until this, no gate at
        all.** ``AGENTS.md`` is what a consumer reads and nothing else;
        ``CLAUDE.md`` is what every session in this repo reads first. A ``step
        7`` pointing at the wrong step does more damage in either than anywhere
        under ``tools/``.

        **The root is the one row with a growth rate, and that is the argument
        for gating it rather than sweeping it.** #238's table put the root at 5;
        re-derived at its own parent commit it was 10, and the growth was all in
        ``CLAUDE.md``, from two tickets with nothing to do with citations. It
        then grew again to 12 while #246 sat open. A sweep repairs a number; only
        a gate holds it, and #244 is the near miss that says naming the skill is
        easy to forget rather than expensive.

        **The price was *not* #238's, and finding that out is what this ticket
        bought.** The ticket priced the repair as *name the skill once per
        paragraph, no parser change*, and that held for nine of the twelve --
        eight renamed and one de-cited, because *"a reader following a
        cross-reference"* says what *"see step 7"* said. The other three are in
        ``CLAUDE.md``'s section about this rule and every one is a **quotation**:
        ``GLOSSARY.md``'s line, quoted as the evidence for the ``carried`` limb;
        *step 2 of the rebuild*, which this file already calls a deliberate
        demonstration; and the apostrophe form #238 caught at the merge, quoted
        **because it does not resolve**. Naming a skill beside any of them
        falsifies the quotation. That is ``differential_scan.py``'s #153 --
        *describing the rule broke the tool that checks the rule* -- arriving on
        a document, and it is why the marker exists.

        **The marker is #246's own remedy and deliberately not the one it
        refused.** The ticket weighed ``spelling_scan.py``'s mention-versus-use
        rule and rejected it: this repo writes ``step 4`` in backticks meaning a
        real citation all over the tree, so a punctuation heuristic would stop
        grading the citations most likely to be precise. What it named instead
        was *a narrow opt-out marker*, and ``exemptions`` is that -- a declared
        **count**, so a new citation wandering into an exempted paragraph fails
        exactly as it would anywhere else.

        **Ruled apart rather than together, which #246 did not propose.**
        ``AGENTS.md`` takes no marker at all; ``CLAUDE.md`` takes up to
        ``EXEMPT_CEILING``. The two documents fail differently and the reasoning
        is on ``ROOT_DOCUMENTS``.

        **``docs/adr/`` is outside this and that is the ticket's scoping, not an
        oversight.** #246 argued the repo-root two; the ADR row is one citation
        in a ratified record, and it is left where #238 left it.
        """
        names = skill_names()
        for path, hatch in ROOT_DOCUMENTS:
            with self.subTest(document=path.name):
                text = read(path)
                # The instrument is live, on ``test_build_artifacts_ignored.py``'s
                # reasoning: a document that stopped citing steps at all would
                # report a clean run and be indistinguishable from one. The floor
                # is far under what either file holds.
                self.assertGreater(
                    len(list(step_citations(text, None, names))),
                    1,
                    f"no step citation in {path.name} was read at all",
                )
                self.assertEqual(
                    undeclared_citations(text, names, hatch),
                    [],
                    f"{path.name}: a 'step N' names no skill, so nothing checks it "
                    "survives a renumbering. Name the skill beside the words -- once "
                    "per paragraph is enough. Where the citation is a quotation that "
                    "must not resolve, and only in CLAUDE.md, declare it with an "
                    "'<!-- unresolved-step-citations: N -->' line above the paragraph",
                )
                if not hatch:
                    continue
                self.assertLessEqual(
                    sum(span.declared for span in exemptions(text)),
                    EXEMPT_CEILING,
                    "the escape hatch is meant to be narrow, and the argument for it "
                    "is that the paragraphs needing it are few and nameable. Past the "
                    "ceiling it is a wholesale opt-out and this gate is theater",
                )

    def test_a_citation_to_a_step_that_does_not_exist_is_caught(self) -> None:
        """#214's renumbering, run backwards. This is the whole evidence for the class.

        Take ``practicum-case-study`` back to the eight steps it had before #214
        and the four surviving ``step 9`` citations come back stale -- in
        ``apa7.md``, ``style.md``, ``voice.md`` and ``tools/docx_write.py``, which
        is four of the five files the ticket names.
        """
        declared = self.declared()
        declared["practicum-case-study"] = declared["practicum-case-study"] - {9}
        stale = stale_citations(declared)
        self.assertGreaterEqual(len(stale), 4)
        for expected in (
            "skills/_shared/reference/apa7.md",
            "skills/_shared/reference/style.md",
            "skills/_shared/reference/voice.md",
            "tools/docx_write.py",
        ):
            with self.subTest(file=expected):
                self.assertTrue(
                    any(line.startswith(expected + ":") for line in stale),
                    f"{expected} cites practicum-case-study step 9 and was not caught",
                )

    def test_no_citation_in_the_tree_is_stale(self) -> None:
        stale = stale_citations(self.declared())
        self.assertEqual(
            stale,
            [],
            "a 'step N' citation points at a step its skill does not declare. "
            "Either the citation or the skill's numbering moved and the other did not",
        )


class TheReferenceHoldsNoOneProgramsEnrollment(unittest.TestCase):
    """#226's ruling of 2026-08-19. **Not** a per-account detector.

    #222 ruled the same day that the prose-and-table shape is a person's job,
    because telling one account's site name from a universal payer string needs
    the name vocabulary
    [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50)
    declined to build and #212 re-ruled. **That ruling stands and nothing here
    reverses it.** What this class reaches is four *literal* shapes that can
    never be universal Medatrax behavior: a course code, a learning-management
    vendor's host, a term date, and an accumulated hours total. The first three
    catch #226's own material arriving back; the fourth is
    [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235)'s,
    and it reaches one figure of the seven that ticket removed because it is
    the only one with a shape. Nothing wider.

    **A per-account *figure* still has no shape in general, and #235 measured
    that rather than assuming it.** Of three candidates it weighed, a
    sampled-day breakdown (``eight of eleven``) sits on 28 lines of legitimate
    fixture prose and was refused; a totals table row was keyable but escapable
    by writing the same figure as a sentence, and was refused too. Only the
    hours shape survived. **One shape having been found does not make the class
    a per-account detector**, and #222's ceiling is where it was.

    **A green run here is not a read file**, and what it passes is the larger
    half. The block #226 emptied out of ``reference/medatrax-fields.md`` also
    carried an hours table, a planning target above the documented figure, a
    prior-coursework ruling, a five-row area breakdown and an evaluation
    cadence -- five kinds of per-program **figure**, none of which has a shape a
    regex can key on, and all of which stay a reader's job. *Field selection
    rules* is a reader's job too. **No count of them is stated here**: the
    ticket's own enumeration and a draft of this docstring disagreed on it,
    which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
    arriving inside the paragraph arguing for honest proportion.

    **Every pattern is exercised against synthetic material, never against the
    strings the ticket removed.** A checker asserting the reference holds no LMS
    host must not become the one file that holds one -- which a first version of
    this class did, with the real institution's host and both real term dates
    typed into its own assertions. That is ``phi_scan``'s *no file may exempt
    itself* arriving on a test, and it was caught by the standards axis of the
    review rather than by anything here.

    **Three of the four patterns are narrower than their names**, and every
    narrowing is measured rather than guessed:

    - A four-digit number reading as a year, or zero-padded, is **not** a course
      code. Without that the pattern fires on ``ADR 0001``, ``AHA/ACC 2025``,
      ``GOLD 2026``, ``ADA 2026`` and ``IDSA 2023`` -- society-plus-year
      citations and this repo's own ADR links, seven distinct shapes across the
      tracked tree. What it costs is a course genuinely numbered ``0100`` or
      ``2026``, which is invisible.
    - A term date is a date with a term word **beside** it, not merely on the
      same line. A bare ISO date cannot be the trigger at all -- this repo
      writes ``read 2026-08-09`` and ``measured 2026-08-11`` everywhere, which
      is ``phi_scan.py``'s own reason for not flagging one in its shape layer.
      Same-line proximity was not enough either: it fired on seven lines across
      the tree including **this ticket's own new prose in CLAUDE.md**, green
      only because the reference is the sole haystack. Within 40 characters and
      no sentence break, it fires on **zero** lines tree-wide and still catches
      the shape the block was written in. Measured 2026-08-19.
    - An hours total needs **three** hour digits, not two. The per-pattern
      figures and the false alarm this one does *not* exclude are on
      ``ACCUMULATED_HOURS`` itself, where the regex a reader is checking sits.

    ``test_the_instrument_is_live`` carries a positive case for every pattern
    and a negative for every false alarm above, on
    ``test_build_artifacts_ignored.py``'s reasoning -- four patterns that
    matched nothing would report a clean file and be indistinguishable from
    four patterns aimed at the wrong thing.

    **Every false-alarm case is quoted verbatim from the tracked tree**, and
    that is not decoration: a case stitched together from a real clause and an
    invented one reads as a measured false alarm while being a sentence nobody
    wrote. Three such cases shipped in #235's first draft and were caught by
    the standards axis of the review.
    """

    #: Letters then four digits, excluding a year and a zero-padded number.
    COURSE_CODE = re.compile(r"\b[A-Z]{3,4} ?(?!19\d\d\b|20\d\d\b|0)\d{4}\b")

    #: Vendor hosts, never a bare product name. An earlier draft matched
    #: ``canvas\.`` and would have fired on any sentence ending in the word
    #: *Canvas*, which is a check that has to be worked around on the day it
    #: lands. A floor: a vendor not listed here is invisible.
    LMS_HOST = re.compile(
        r"\b(?:instructure|blackboard|brightspace|canvaslms|moodle|d2l)\.[a-z]{2,}",
        re.IGNORECASE,
    )

    #: An accumulated hours total, as the portal renders one under *Hours to
    #: Date* or *Total time log*. Three or more hour digits, and the
    #: narrowing is measured rather than guessed. **Over every tracked file
    #: at the base commit**, two digits sits on **84** lines and almost all
    #: are real -- a visit time is ``0:35``, a shift is ``12:00``, a recorded
    #: portal time is ``19:20``. Three digits sits on **3**: the two
    #: [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235)
    #: removed, and one that is **not** an hours total at all.
    #:
    #: **The haystack is named because a first draft of this line measured a
    #: different one.** It read *67 tree-wide*, counted over ``*.md`` only,
    #: and the sentence claiming *tree-wide* read exactly like one that had
    #: been. That is ``guidelines_extract``'s retired N=3 boundary arriving
    #: on a regex -- a figure measured against the wrong input is not
    #: distinguishable from a right one by looking at it. Caught by the
    #: standards axis of the review. Re-derived 2026-08-19.
    #:
    #: **The third hit is a false alarm this pattern does not exclude**, and
    #: it is named rather than engineered around: ``Ann Intern Med.
    #: 2015;162:35-45`` in ``tools/testdata/uspstf/``, a volume-and-page
    #: citation. It costs nothing because the haystack is one reference file
    #: that carries no journal citation -- checked, not assumed -- and a
    #: narrowing to exclude it would be tuning against a file the check
    #: never reads.
    #:
    #: **A floor, and a low one**: a bare count of visits is an integer and
    #: has no shape at all, which is why this limb is not a per-account
    #: detector and #222's ceiling is not moved by it.
    ACCUMULATED_HOURS = re.compile(r"\b\d{3,}:[0-5]\d\b")

    #: A term word, then within 40 characters and no sentence break, a date.
    TERM_DATE = re.compile(
        r"\b(?:start|starts|starting|due|deadline|semester|end date|term date)\b"
        r"[^.]{0,40}?\b20\d{2}-\d{2}-\d{2}\b",
        re.IGNORECASE,
    )

    def assert_reference_is_free_of(self, pattern, holds, remedy):
        """Assert ``reference/medatrax-fields.md`` matches ``pattern`` nowhere.

        One helper for all four limbs rather than four near-identical bodies,
        and it reports the **matched spans** rather than the whole file: the
        haystack is a reference document, and a failure that prints it is a
        failure nobody reads.
        """
        found = sorted({match.group(0) for match in pattern.finditer(read(MEDATRAX))})
        self.assertEqual(
            found, [], f"reference/medatrax-fields.md {holds}. {remedy}: {found}"
        )

    def test_the_instrument_is_live(self):
        # Synthetic throughout -- see the docstring. The vendor host is real
        # because the pattern is about vendors; the institution in front of it
        # is not.
        self.assertTrue(self.COURSE_CODE.search("ABC 1234 - a course, across the lifespan"))
        self.assertTrue(self.COURSE_CODE.search("prior coursework (ABC1234, ABC1235)"))
        self.assertTrue(self.LMS_HOST.search("https://example.instructure.com/courses/1/pages/x"))
        self.assertTrue(self.LMS_HOST.search("https://learn.blackboard.com/hours"))
        self.assertTrue(self.LMS_HOST.search("https://example.moodle.org/course/view.php"))
        self.assertTrue(self.TERM_DATE.search("Both courses start **2019-01-07**, due **2019-05-03**."))
        self.assertTrue(self.TERM_DATE.search("Documentation deadline 2019-05-10."))
        # Synthetic hours, deliberately not the two #235 removed -- see the
        # docstring. A checker asserting the reference states no hours total
        # must not become the one file that states one.
        self.assertTrue(self.ACCUMULATED_HOURS.search("| Total time log | 100:00 |"))
        self.assertTrue(self.ACCUMULATED_HOURS.search("Hours to Date reads 987:04."))

        # And every false alarm the review found. **Each case below is quoted
        # verbatim from the tracked tree** -- checked, not remembered. A first
        # version of the two hours cases stitched a real clause to an invented
        # one and to a hyphen where the source writes an en dash, which reads
        # as a measured false alarm and is a sentence nobody ever wrote.
        for citation in ("ADR 0001", "AHA/ACC 2025", "GOLD 2026", "ADA 2026", "IDSA 2023"):
            self.assertIsNone(
                self.COURSE_CODE.search(citation),
                f"{citation} is a citation or an ADR link, not a course code",
            )
        self.assertIsNone(self.LMS_HOST.search("the program's hours breakdown on Canvas."))
        for duration in (
            "Visit Time 0:35 = 08:35 - 08:00, both estimated.",
            "0:30 to 0:45 across one sampled day, a flat 0:15 across another",
            "The portal has case 10 at 19:20–19:50",
        ):
            self.assertIsNone(
                self.ACCUMULATED_HOURS.search(duration),
                f"a clock time or a visit duration is not an hours total: {duration}",
            )
        for measurement in (
            "The offsets are one-based over the LF form, measured 2026-08-11",
            "The reference was read 2026-08-11",
            "**#69 was ruled on 2026-08-16 and moved no digit, so one of the two remains.**",
        ):
            self.assertIsNone(
                self.TERM_DATE.search(measurement),
                "a measurement date is not a term date",
            )

    def test_the_reference_names_no_course(self):
        self.assert_reference_is_free_of(
            self.COURSE_CODE,
            "names a course code, which is one clinician's enrollment rather "
            "than Medatrax behavior",
            "setup-clinical-skills step 3 collects it and "
            "scratch/medatrax-profile.md holds it",
        )

    def test_the_reference_links_no_learning_management_system(self):
        self.assert_reference_is_free_of(
            self.LMS_HOST,
            "links one institution's learning-management system",
            "the authoritative-source rule is universal and belongs here; the "
            "URL is per-program and belongs in the profile",
        )

    def test_the_reference_states_no_hours_to_date_total(self):
        """#235's decision 4, ruled 2026-08-19, and it reaches one figure.

        #226 moved the **ruling** about the hours-to-date figure to the profile
        and left the figure itself thirty lines above where its explanation had
        been -- an unexplained account-specific integer where an explained one
        had stood, which is worse than either end state. This is the only one
        of that section's seven totals with a shape, and it is the one the
        ticket calls the sharp one.

        **The figure is not quoted here, and that is the rule rather than
        fastidiousness.** A first version of this docstring named it, which put
        the removed string back into the repo inside the check built to keep it
        out -- the same self-exemption the class docstring above records being
        caught once already, arriving one method lower.
        """
        self.assert_reference_is_free_of(
            self.ACCUMULATED_HOURS,
            "states an hours-to-date total, which is what one account had "
            "accrued on one afternoon rather than Medatrax behavior",
            "the figure and the ruling about what it does and does not carry "
            "both belong in scratch/medatrax-profile.md",
        )

    def test_the_reference_states_no_term_date(self):
        self.assert_reference_is_free_of(
            self.TERM_DATE,
            "states a term date",
            "course start and end dates are collected by setup-clinical-skills "
            "step 3 and live in scratch/medatrax-profile.md",
        )

    def test_the_reference_keeps_the_why_it_gave_up_the_numbers_for(self):
        """Decision 1's whole point, and the half a delete would have lost.

        The documentation deadline is described across this repo as *the
        constraint the whole toolchain exists to satisfy*. Moving the number to
        the profile is the ruling; moving the motivation with it is not, and a
        later tidy that shortened the abstracted block to a bare pointer would
        do exactly that with nothing to notice.
        """
        text = read(MEDATRAX)
        self.assertIn("the constraint this whole toolchain exists to satisfy", text)
        self.assertIn("area breakdown", text)
        self.assertIn("Objectives page", text)

    def test_setup_collects_what_the_reference_now_defers(self):
        """The cross-file half. A pointer at a step that collects nothing is
        worse than the leak it replaced, because it reads as a split that was
        made.

        **Scoped to the collecting steps, and that is not tidiness.** Checking
        the whole file passed ``evaluation`` on step 2's sentence about the
        ``evaluations.medatrax.com`` host -- green for the wrong reason, on a
        fact step 3 did not collect until #226 added it.
        """
        setup = read(SETUP)
        start = setup.find("### 3. Program and hours")
        self.assertNotEqual(
            start, -1, "setup-clinical-skills has no step 3 heading to read from"
        )
        end = setup.find("### 5.", start + 1)
        self.assertNotEqual(
            end,
            -1,
            "setup-clinical-skills has no step 5 heading, so steps 3 and 4 have "
            "no end. Renumbering a step redirects every citation to it -- see "
            "that skill's own step 10",
        )
        collecting = setup[start:end]
        for asked in (
            "hour requirement",
            "area breakdown",
            "start and end dates",
            "documentation deadline",
            "evaluation schedule",
            "Women's Health",
        ):
            # ``assertTrue`` rather than ``assertIn``: the haystack is two whole
            # steps, and a failure that prints them is a failure nobody reads.
            self.assertTrue(
                asked in collecting,
                f"reference/medatrax-fields.md defers {asked!r} to "
                "setup-clinical-skills steps 3 and 4, which do not collect it",
            )


class TheWorkedReadingBehindTheDuplicateArgumentLivesInOnePlace(unittest.TestCase):
    """#244's decision 1, ruled by the clinician 2026-08-19. **Not** a
    per-account detector, and decision 3 declined to make it one.

    #235 deleted seven per-account totals from ``## Current state`` and swept
    that section rather than the file. Two survived under other headings: the
    patient-and-visit pair in *The identity problem*, and a form count in
    *Navigating the portal*. The pair is the harder one because it is the
    **premise of an argument** rather than a standing -- ten more visits than
    patients, fifteen Patient Detail pages all reading ``1 Visit(s)``,
    therefore most of that gap is duplicates already made.

    **The ruling was to abstract and point rather than to qualify in place.**
    The ticket's own comment recommended adopting ``setup-clinical-skills``'s
    sentence -- *"On one account the figures were ..."* -- into the reference,
    which is the honest per-account form. The clinician ruled the other way:
    the reference states the **method** and the **inference** and points at
    ``setup-clinical-skills`` step 6, so the reading survives **as a sentence
    a reader can follow** in exactly one place, the file whose job is
    collecting one account's setup. That keeps #235's ruling intact in the
    file it was ruled about.

    **As a sentence, and not as the figures**, which is a narrowing this
    docstring stated for one commit by not stating it. The two integers are
    also in three notes under ``fixtures/filled-anchor/notes/``, welded into a
    hyphenated clause -- so *survives once* is true of the form and false of
    the numbers, and the paragraph below saying those notes must not be edited
    is what makes the difference matter. The same overclaim was caught in
    ``CLAUDE.md`` by the standards axis of the review and repaired there; it
    survived one level down, in the docstring describing the repair.

    **The needles are read out of ``setup-clinical-skills`` and never typed
    here.** A checker asserting the reference states no portal totals must not
    become a file that states them -- ``phi_scan``'s *no file may exempt
    itself* arriving on a test, which
    ``TheReferenceHoldsNoOneProgramsEnrollment`` above records being caught
    twice already. Reading them from the one file allowed to carry them also
    means the check follows a re-measurement instead of pinning a figure, which
    is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

    **The haystack is one file, and that is a safety property rather than
    tidiness.** Those same two integers are live in three notes under
    ``fixtures/filled-anchor/notes/``, which are day-b run 1 byte for byte
    apart from two redacted site names and are the evidence #73 rests on. A
    tree-wide check would fail in files nobody is allowed to fix -- exactly the
    exposure ``tools/test_corpus_census.py`` documents at ``RETIRED_ANYWHERE``,
    where one of these two figures is named among the bare 5xx literals those
    notes already carry as clinical values. **A ``git grep`` of either figure
    is not a to-do list**, and the verdicts are the finding rather than the
    count: the hits are a preserved run record, the skill that is the pattern
    to copy, and prose that happens to carry the digits. **No count is stated
    here** -- #244's comment put the pair in five files, this change removed
    one of them, and a bare ``582`` was never five to begin with.

    **A green run here is not a swept file**, and the limits are the ones #244
    decision 3 declined to move. A bare integer has no shape, so nothing here
    generalizes to *a per-account figure*; these two are reachable only because
    another file declares them. A restatement in words, or a differently
    phrased form count, escapes every assertion below.
    """

    #: The worked reading, as ``setup-clinical-skills`` step 6 writes it. The
    #: **shape** is typed and the **figures** are not, which is the whole
    #: reason this class can assert their absence without holding them.
    WORKED_READING = re.compile(r"\b(\d+) patients against (\d+) visits\b")

    #: The form count #235's table carried as ``1. FNP: H & P``, as
    #: *Navigating the portal* item 2 used to state it. A floor, and a low
    #: one: it keys on the sentence rather than on the integer, so any
    #: rephrasing that reintroduces a count escapes it.
    COUNTED_POSTBACK = re.compile(r"\ball \d+ in a single postback\b")

    def setUp(self):
        self.reference = read(MEDATRAX)
        self.setup_skill = read(SETUP)

    def spans(self, pattern):
        """The distinct spans ``pattern`` matches in the reference.

        ``TheReferenceHoldsNoOneProgramsEnrollment.assert_reference_is_free_of``
        above exists to justify this shape and is a method on that class; this
        is the same reasoning rather than a second opinion -- the haystack is a
        reference document, so a failure reports **what matched** and never the
        file it matched in.
        """
        return sorted({found.group(0) for found in pattern.finditer(self.reference)})

    #: The residue note #235 left in the reference for #244 to settle, keyed on
    #: the clause that made it a *record* rather than a fix. A floor: a rewrite
    #: that kept the sense in other words escapes it.
    RESIDUE_NOTE = "recorded rather than fixed"

    def test_the_instrument_is_live(self):
        """Every needle below matches something, on
        ``TheReferenceHoldsNoOneProgramsEnrollment.test_the_instrument_is_live``'s
        reasoning and ``test_build_artifacts_ignored.py``'s before it.

        **Two of these three are asserted only in the negative**, and that is
        what makes this method load-bearing rather than ceremonial: the
        sentences they were written against are **deleted by this very
        change**, so nothing else in the suite exercises them again. A typo in
        ``COUNTED_POSTBACK`` or a drifted ``RESIDUE_NOTE`` leaves its test green
        forever and indistinguishable from a rule being kept.

        **Synthetic throughout.** The positive cases are written here rather
        than quoted from the strings this change removed -- a checker asserting
        the reference states no portal totals must not become the file that
        states them, which is the self-exemption the class above records being
        caught twice.
        """
        self.assertTrue(
            self.WORKED_READING.search("the figures were 111 patients against 222 visits"),
            "WORKED_READING matches nothing, so every needle it supplies is empty "
            "and this class passes on a reference that restates both figures",
        )
        self.assertTrue(
            self.COUNTED_POSTBACK.search("clicking Search returns all 7 in a single postback."),
            "COUNTED_POSTBACK matches nothing, so #244 decision 2 is unchecked "
            "and a reinstated per-account count would read as clean",
        )
        self.assertIn(
            self.RESIDUE_NOTE,
            "two of the seven are recorded rather than fixed",
            "RESIDUE_NOTE no longer matches the clause it was written against",
        )
        # The negative half: the behavior sentence #244 replaced the count with
        # must not itself trip the pattern that forbids the count.
        self.assertFalse(
            self.COUNTED_POSTBACK.search(
                "returns the whole matching set in a single postback rather than paging it."
            ),
            "COUNTED_POSTBACK fires on the countless form #244 decision 2 chose, "
            "so the rule refuses its own remedy",
        )

    def test_setup_still_carries_the_worked_reading(self):
        """The instrument-is-live half, and it is load-bearing rather than
        ceremonial: every assertion below takes its needles from this match, so
        a ``setup-clinical-skills`` that stopped stating the figures would turn
        the whole class green while the reference kept them.

        On ``test_build_artifacts_ignored.py``'s ``TheInstrumentIsLive``
        reasoning.
        """
        # ``assertTrue`` rather than ``assertRegex`` throughout this class: the
        # haystacks are two whole documents, and an assertion that prints one on
        # failure is a failure nobody reads. Same reasoning as
        # ``test_setup_collects_what_the_reference_now_defers`` above.
        self.assertTrue(
            self.WORKED_READING.search(self.setup_skill),
            "skills/setup-clinical-skills/SKILL.md no longer states the "
            "patient-against-visit reading, so the reference points at a step "
            "that carries nothing and every assertion in this class is vacuous",
        )

    def test_setup_declares_the_reading_as_one_accounts(self):
        """The pattern the reference was ruled to point at rather than copy.

        A step that stated the pair flat would be the defect relocated, not the
        honest form -- so what makes ``setup-clinical-skills`` the right home is
        the qualifier, not the file name.

        **This is a constraint on a file #244 scoped out, and it is named
        rather than assumed harmless.** That ticket's second comment calls
        ``setup-clinical-skills`` *"the pattern to copy, not a sixth thing to
        fix"*. Pinning its wording is not fixing it, and the reason it is worth
        the reach is that the reference now **points** there: a step that
        dropped the qualifier would turn this file's abstraction into a pointer
        at a second unqualified figure, which is the defect moved rather than
        removed.
        """
        found = self.WORKED_READING.search(self.setup_skill)
        assert found is not None  # the test above is the guard
        opening = self.setup_skill[max(0, found.start() - 120) : found.start()]
        self.assertTrue(
            "On one account" in opening,
            "skills/setup-clinical-skills/SKILL.md states the figures without "
            "declaring them as one account's reading, which is the form "
            "reference/medatrax-fields.md was ruled to point at",
        )

    def test_the_reference_restates_neither_figure(self):
        """#244 decision 1. The figures are read off the file allowed to carry
        them, never typed here -- see the class docstring.

        **The cost is named rather than engineered around**: this reaches a
        bare integer, so an unrelated future number in the reference that
        happened to equal one of them would fail. That is the trade for a check
        that holds no copy of what it forbids.
        """
        found = self.WORKED_READING.search(self.setup_skill)
        assert found is not None  # the instrument-is-live test above is the guard
        restated = sorted(
            {figure for figure in found.groups() if figure in self.reference}
        )
        self.assertEqual(
            restated,
            [],
            "reference/medatrax-fields.md restates one account's portal totals "
            "in a file that opens 'single source of truth for the Medatrax NP "
            "portal'. The method and the inference belong here; the worked "
            "reading belongs in setup-clinical-skills step 6",
        )

    def test_the_reference_keeps_the_argument_it_gave_up_the_figures_for(self):
        """The half a delete would have lost, on #235's
        ``test_the_reference_keeps_the_why_it_gave_up_the_numbers_for``
        reasoning.

        The ticket's own objection to abstracting was that **the numbers are
        the inference** -- the gap, the sampled Patient Detail pages, and the
        conclusion drawn from both. Dropping the figures is the ruling; dropping
        the argument with them is not, and a later tidy that shortened this to a
        bare pointer would do exactly that with nothing to notice.
        """
        for kept in ("1 Visit(s)", "duplicates already made", "studentoverview.aspx"):
            self.assertTrue(
                kept in self.reference,
                f"reference/medatrax-fields.md dropped {kept!r} along with the "
                "figures. #244 abstracted the reading, not the argument it "
                "supports",
            )

    def test_the_reference_points_at_the_worked_reading(self):
        """The cross-file half. A pointer is the whole of decision 1's remedy,
        so an abstraction that points nowhere is worse than the figure it
        replaced: it reads as a split that was made.

        ``EveryCitedStepResolvesToADeclaredStep`` above is what keeps the step
        **number** honest; this only asserts the pointer is there at all.
        """
        opens = self.reference.find("### The identity problem")
        self.assertNotEqual(
            opens,
            -1,
            "reference/medatrax-fields.md has no '### The identity problem' "
            "heading, so #244's abstracted paragraph has no section to sit in",
        )
        section = self.reference[opens:]
        section = section[: section.find("\n#", 1)]
        self.assertTrue(
            "setup-clinical-skills" in section,
            "reference/medatrax-fields.md abstracts the patient-against-visit "
            "reading without naming where the worked one lives",
        )

    def test_the_navigation_example_states_no_per_account_count(self):
        """#244 decision 2, the cheapest of the three.

        The lower panel returning its whole filtered set in one postback rather
        than paging is the behavior worth recording, and any integer carries
        it. The one that was here happened to be one account's form count --
        the ``1. FNP: H & P`` row of the table #235 deleted.
        """
        self.assertEqual(
            self.spans(self.COUNTED_POSTBACK),
            [],
            "reference/medatrax-fields.md states one account's form count as "
            "the worked example of a portal behavior any integer would carry",
        )
        self.assertTrue(
            "single postback" in self.reference,
            "reference/medatrax-fields.md dropped the no-paging behavior along "
            "with the count. #244 decision 2 replaced the integer, not the rule",
        )

    def test_the_residue_note_does_not_outlive_the_residue(self):
        """#235 left a paragraph in the reference naming this residue and
        pointing here, explicitly for #244 to remove or rewrite. Leaving it
        standing after the fix is the stale-cross-reference shape #235 was
        itself filed about.
        """
        self.assertFalse(
            self.RESIDUE_NOTE in self.reference,
            "reference/medatrax-fields.md still says the residue is recorded "
            "rather than fixed, after #244 fixed it",
        )


class TheCatalogSettlesFormAndNeverStanding(unittest.TestCase):
    """[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s
    amended recency rule cited the guideline catalog as its evidence, and the
    evidence was false. Found in that ticket's own sweep, 2026-08-20, off
    [#107](https://github.com/mshamblin5150-code/clinical-skills/issues/107)'s
    ruling.

    ``skills/practicum-case-study/SKILL.md`` read: *"``reference/guidelines-catalog.md``
    spans 2009 to 2026 and every document in it is in force."* The catalog's own
    legend says otherwise **in the same tree** -- three rows are classed
    ``guideline`` because the vocabulary has nowhere better to put them, and it
    names them: a scope of work for a guideline that does not exist yet, a
    two-page errata, and a document whose cover says it is a public review
    draft. #107 then ruled ``class`` is document **form** and declined a
    standing field outright, so nothing in the catalog answers *is this in
    force* and nothing is going to.

    **Keyed on the legend and never on the ``class`` cell**, which is what makes
    it true either side of a merge rather than only today -- and the merge has
    since happened, so that is now checked rather than predicted. #107's
    widening landed while this branch was open: ``CLASSES`` carries ``draft``,
    ``errata`` and ``scope-of-work``, and the three rows have moved off
    ``guideline``. **Every needle still matches**, because each keys on the
    reason the catalog's prose gives rather than on the value in the cell. A
    check written the obvious way -- against the class value -- would have been
    wrong before the merge and would have had to be rewritten at it.

    **The direction of the harm is the reason this is a defect rather than a
    slip.** ``RECENCY: guideline in force`` stands the five-year window down,
    and ``research_ledger.py`` grades that excuse's presence and its reason and
    never its truth -- so the excuse is worth exactly the run's belief about
    standing. Telling a run that catalog membership settles standing hands it a
    warrant for every row where it is false, and the costly one is the public
    review draft -- the largest document in the corpus, so it out-ranks real
    guidelines on size and on recency while carrying recommendations that may
    not survive review. That is
    #215's own thesis pointing the other way: the shipped five-year rule refused
    a source for a property the rule did not care about, and this would have
    excused one for a property the row does not carry.

    **What survives is the narrower ruling**, and
    ``test_the_narrower_ruling_survives`` is here because striking false
    evidence must not take the claim it was offered for with it. A society
    guideline is dated by its own version rather than by the age of the evidence
    it cites; the 2013 KDIGO threshold is a real in-force guideline and the
    worked case is unmoved.

    **The reading it moves to is one axis over from one this repo already
    published**, and the first draft of this docstring called them the same
    thing. ``skills/clinical-note/SKILL.md`` refuses to read a document's
    **content** off a catalog row -- *"the catalog says what each document is
    and never what it says"* -- and standing is a different question about the
    same row. So the repair extends a settled refusal rather than inventing one,
    which is why it needed no ruling from the clinician; calling it the same
    ruling would be [#165](https://github.com/mshamblin5150-code/clinical-skills/issues/165)'s
    shape, where the wrong citation is the one a later sentence copies. Caught
    by the spec axis of ``/code-review``.

    **The needles for the catalog half are read out of the catalog and never
    typed here**, on
    ``TheWorkedReadingBehindTheDuplicateArgumentLivesInOnePlace``'s reasoning:
    a check asserting the skill must not restate the catalog's rows must not
    become the file that restates them, and reading them means the check follows
    a re-curation instead of pinning it.

    **The haystack for the skill half is ``skills/``**, which is every file a
    run reads as instruction, and it is wider than the one file that carried the
    defect on purpose -- the blanket claim is the same defect wherever a skill
    writes it. It is not tree-wide: ``fixtures/`` records what a skill said at
    run time and may not be edited to satisfy a rule made later.

    **What it cannot reach.** Every pattern below is a floor -- a blanket
    standing claim written in other words escapes ``BLANKET_STANDING``, and a
    qualifier reworded escapes ``MEMBERSHIP_IS_NOT_STANDING``. Nothing here
    reads whether a *particular* source a run cites is in force, which is a
    reading of that document and is what ``guideline in force`` asks a run for.
    A green run is not a checked excuse.
    """

    #: A blanket standing claim. Keyed on the recorded defect and the two
    #: nearest ways of writing it, bounded to one sentence so it cannot leap a
    #: full stop into an unrelated clause. A floor: any rephrasing that drops
    #: all three openers escapes it.
    BLANKET_STANDING = re.compile(r"\b(?:every|all|each)\b[^.]{0,60}\bin\s+force\b", re.I)

    #: The qualifier the repair puts in its place, keyed short so a rewrite of
    #: the surrounding sentence keeps it. A floor for the same reason.
    MEMBERSHIP_IS_NOT_STANDING = re.compile(r"\bmembership\s+is\s+not\s+standing\b", re.I)

    #: The surviving ruling, which the repair must not strike along with the
    #: evidence that was offered for it.
    NARROWER_RULING = re.compile(r"dated\s+by\s+the\s+guideline,\s+not\s+by\s+what\s+it\s+cites")

    #: The forms the catalog itself declines to call in-force guidelines, keyed
    #: on the **reason** rather than on a filename -- the property is what makes
    #: a document not in force, and it survives #107's reclassification of those
    #: three rows out of ``guideline``. Whitespace is loose because the catalog
    #: hard-wraps its prose, which is ``test_run_record_claim.py``'s finding.
    #:
    #: **Matched against the catalog's prose and never against a row**, which
    #: the first version got wrong and which cost a false claim on #107 --
    #: ``\berrata\b`` and ``public review draft`` both land in a hand-read
    #: ``title`` cell as well as in the legend, so the failure mode that comment
    #: named was unreachable and a re-curation of either cell would have moved
    #: this test. A title is a curated string that happens to carry the word;
    #: only the prose is the catalog **declaring** anything.
    NOT_IN_FORCE_FORMS = (
        re.compile(r"scope\s+of\s+work\s+for\s+a\s+guideline\s+that\s+does\s+not\s+exist", re.I),
        re.compile(r"\berrata\b", re.I),
        re.compile(r"public\s+review\s+draft", re.I),
    )

    def setUp(self):
        self.case_study = read(CASE_STUDY)
        self.catalog = read(CATALOG)

    def catalog_prose(self):
        """The catalog with its document rows dropped and prose normalized.

        **A table row is not the catalog declaring anything.** Two of
        ``NOT_IN_FORCE_FORMS`` match a hand-read ``title`` cell -- ``Errata`` and
        ``Public Review Draft`` are what those documents are *called* -- so a
        whole-file search reads a curated string as a declaration, and
        [#106](https://github.com/mshamblin5150-code/clinical-skills/issues/106)
        is the ticket saying nothing checks those columns. Keying on the prose
        keeps this check off them.
        """
        return normalized(
            "\n".join(
                line
                for line in self.catalog.splitlines()
                if not line.lstrip().startswith("|")
            )
        )

    def instruction_files(self):
        """Every Markdown file under ``skills/`` -- what a run reads as a rule.

        **A directory walk and deliberately not ``git ls-files``**, which is the
        opposite narrowing from
        [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)
        and is the safe direction here: an untracked draft under ``skills/`` is
        a file an agent can already load and follow, so it is graded before the
        commit that tracks it rather than after.
        """
        return sorted(SKILLS_DIR.rglob("*.md"))

    def citing_paragraph(self):
        """The case study's recency paragraph: the block that both names the
        catalog and states the ruling the catalog was offered as evidence for.

        The paragraph is the unit rather than the line because this repo
        hard-wraps, which ``paragraphs`` says in as many words.
        """
        found = [
            block
            for _, block in paragraphs(self.case_study)
            if "guidelines-catalog.md" in block and self.NARROWER_RULING.search(block)
        ]
        self.assertEqual(
            len(found),
            1,
            "skills/practicum-case-study/SKILL.md no longer has exactly one "
            "paragraph carrying both the catalog citation and the guideline-is-"
            "dated-by-the-guideline ruling, so this class is reading nothing",
        )
        return found[0]

    def test_the_instrument_is_live(self):
        """Every pattern in the class matches something, and the two skill
        patterns are mutually exclusive.

        **Every pattern, and the first version exercised half of them.** It
        opened on this same sentence while leaving ``NOT_IN_FORCE_FORMS``
        untested -- and because ``test_the_catalog_still_carries_a_row…`` passes
        on **any** one match, two of those three could have been typos and
        stayed green forever. That is the failure the paragraph below names,
        committed one method away from naming it, and it was found by the
        standards axis of ``/code-review`` rather than by a run.

        ``TheWorkedReadingBehindTheDuplicateArgumentLivesInOnePlace.test_the_instrument_is_live``'s
        reasoning: ``BLANKET_STANDING`` is asserted only in the negative against
        a tree this change makes clean, so a typo in it leaves its test green
        forever and indistinguishable from a rule being kept. The positives are
        written here rather than quoted from the sentence this change removes --
        a checker forbidding a claim must not become the file that makes it, so
        the string below names no real catalog.
        """
        self.assertTrue(
            self.BLANKET_STANDING.search("every document in that list is in force"),
            "BLANKET_STANDING matches nothing, so the defect it forbids would "
            "read as clean if it were written back",
        )
        self.assertTrue(
            self.MEMBERSHIP_IS_NOT_STANDING.search("Membership is not standing."),
            "MEMBERSHIP_IS_NOT_STANDING matches nothing, so the qualifier is "
            "unchecked and could be dropped silently",
        )
        self.assertTrue(
            self.NARROWER_RULING.search(
                "A guideline is dated by the guideline, not by what it cites."
            ),
            "NARROWER_RULING matches nothing, so the over-correction guard is dead",
        )
        # Synthetic, one per form, because the catalog test passes on any single
        # match and so cannot tell a live needle from a dead one.
        for form, sentence in zip(
            self.NOT_IN_FORCE_FORMS,
            (
                "a nine-page scope of work for a guideline that does not exist yet",
                "a two-page errata correcting two unrelated articles",
                "its cover says it is a public review draft",
            ),
            strict=True,
        ):
            self.assertTrue(
                form.search(sentence),
                f"NOT_IN_FORCE_FORMS entry {form.pattern!r} matches nothing, so "
                "it can never be the reason this class passes and a typo in it "
                "is indistinguishable from a form the catalog retired",
            )
        # The narrowing, pinned: a document row is not a declaration, however
        # its title reads. Without this the class rests on two hand-read cells,
        # which is #106's subject.
        self.assertNotIn(
            "|",
            self.catalog_prose(),
            "catalog_prose kept a table row, so NOT_IN_FORCE_FORMS can be "
            "satisfied by a hand-read title cell rather than by the catalog "
            "declaring anything",
        )
        # The two skill patterns must not be satisfiable by one sentence: the
        # qualifier is not allowed to carry the claim it replaces.
        self.assertFalse(
            self.BLANKET_STANDING.search("Catalog membership is not standing."),
            "BLANKET_STANDING fires on the qualifier itself, so the repair "
            "cannot satisfy both halves and the class is unsatisfiable",
        )
        self.assertFalse(
            self.MEMBERSHIP_IS_NOT_STANDING.search("every document in it is in force"),
            "MEMBERSHIP_IS_NOT_STANDING fires on the claim it exists to replace",
        )

    def test_the_catalog_still_carries_a_row_it_declines_to_call_in_force(self):
        """The fact the qualifier rests on, re-derived rather than asserted.

        **At least one, and deliberately not all three.** A corpus refresh that
        retired the errata leaves the qualifier true on the other two, and a
        class that went red on it would be pinning a curation rather than
        checking a claim. What it does catch is the catalog's **prose** ceasing
        to declare any of them -- at which point the skill is telling a run
        something nothing in the tree supports any more, and a person should
        look.

        **The prose, which is narrower than the whole file and narrower than
        the legend.** The comment this branch posted on #107 said the class
        would fail if *the legend* lost all three phrasings; against the first
        version that was false in the loose direction -- two needles also match
        a ``title`` cell, so the class stayed green with the legend deleted --
        and against this version it is still not the legend alone, because the
        closing ``?`` notes declare the errata too. The true statement is the
        one above: the catalog's prose, anywhere in it.
        """
        prose = self.catalog_prose()
        matched = [form.pattern for form in self.NOT_IN_FORCE_FORMS if form.search(prose)]
        self.assertTrue(
            matched,
            "reference/guidelines-catalog.md names no document it declines to "
            "call an in-force guideline, so skills/practicum-case-study/SKILL.md's "
            "qualifier rests on nothing re-derivable",
        )

    def test_no_skill_reads_catalog_membership_as_standing(self):
        """The defect itself, over every file a run reads as instruction."""
        offenders = []
        for path in self.instruction_files():
            for found in self.BLANKET_STANDING.finditer(normalized(read(path))):
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {found.group(0)}")
        self.assertEqual(
            offenders,
            [],
            "a skill claims blanket standing for a set of documents; the "
            "catalog settles what a document is and never whether it stands, "
            "and `guideline in force` stands the five-year window down on the "
            "strength of it: " + "; ".join(offenders),
        )

    def test_the_skill_says_membership_is_not_standing(self):
        """The positive half. An absence check alone passes on a paragraph that
        simply stopped citing the catalog, which would drop the warning along
        with the error.
        """
        self.assertTrue(
            self.MEMBERSHIP_IS_NOT_STANDING.search(self.citing_paragraph()),
            "skills/practicum-case-study/SKILL.md cites the guideline catalog "
            "in its recency rule without saying that membership is not "
            "standing, so a run may read a row as a warrant for "
            "`RECENCY: guideline in force`",
        )

    def test_the_narrower_ruling_survives(self):
        """Striking the false evidence must not take the ruling with it. #215's
        limb 4 is unamended: a society guideline is dated by its own version
        rather than by the age of the evidence it cites, and
        ``research_ledger.EXCUSES`` still holds ``guideline in force``.
        """
        self.assertTrue(
            self.NARROWER_RULING.search(self.case_study),
            "skills/practicum-case-study/SKILL.md dropped #215's limb 4 along "
            "with the false evidence offered for it",
        )


if __name__ == "__main__":
    unittest.main()
