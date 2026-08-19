"""Tests for the corpus census extractors.

These run against the committed, PHI-free fixtures in ``fixtures/day-a/shorthand/``
and ``fixtures/day-b/shorthand/`` and against inline strings. They never touch
``scratch/``. Their job is to catch the silent failure mode the census exists to
prevent: an extractor that stops matching and reports a confident wrong number.

``DayBIsTheAbsenceSet`` does a second job: it guards the properties of the
*inputs* that day-b's assertion rows rest on, so an edit to one voids the set
loudly rather than quietly. Three shapes, and the first two are absences. Nine of
the twelve encounters carry no vital at all, which is that set's whole reason for
existing; case 9 documents a COVID contact and orders no swab, which is what makes
D6 checkable; and the twelve split seven / two / three on whether the shorthand
writes a pain score, writes "no pain", or writes neither, which is what B7, B8 and
B14 divide on. A well-meaning edit that "completes" any of them would leave every row
above it passing with nothing tested.

phi-scan: synthetic

Testing a date-of-birth extractor requires date-shaped literals, so this file is
exempt from the shape rules. **Every date below is invented.** The pragma does not
exempt it from the corpus layer: a real patient name or a real date lifted from
``scratch/`` is still refused here, which is exactly how the first version of this
file was caught using both.
"""

import ast
import re
import tempfile
import unittest
from pathlib import Path
from typing import NamedTuple

import corpus_census as cc

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "fixtures" / "day-a" / "shorthand"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "shorthand"
PEDS_BP = REPO_ROOT / "fixtures" / "peds-bp" / "shorthand"

# day-b/shorthand/README.md states this split in prose; the numbers are here so a
# change to either one has to be made in both places on purpose.
DAY_B_NO_VITAL = (1, 5, 6, 7, 8, 9, 10, 11, 12)
DAY_B_CONTROL = (2, 3, 4)
DAY_B_HYPERTENSIVE = (8, 9)  # the two B2 anchors: htn documented, no pressure
# Every case documenting hypertension, which is wider than the B2 anchors. Cases
# 2 and 3 carry a given pressure, so the run has nothing to fill and B2 does not
# score them -- but they are what stops the extractor test being vacuous, and
# case 2's given 121/61 is the reading day-b/assertions.md cites as the in-corpus
# proof that a normal pressure in a hypertensive is a real patient. Issue #23.
DAY_B_DOCUMENTS_HTN = (2, 3, 8, 9)
DAY_B_HTN_WITH_BP = (2, 3)

# The three chest findings D2, D3 and D7 anchor on. Every one of these cases is
# also in DAY_B_NO_VITAL, which is what leaves all three rows open to a filled
# dismissal -- "deferred, afebrile with SpO2 97%" names the finding in the Plan
# and passes. B9 is what closes that. Issue #27.
DAY_B_LUNG_FINDING = {
    1: "lungs diminished in all four fields",
    9: "lung sounds diminished",
    11: "inspiratory wheezing noted in all fields",
}

# The OLDCARTS severity split B5-B8 rest on, for issue #30. Every case is in
# exactly one of the three, and which one decides whether its severity is a
# given the run must preserve or a value the run must invent.
DAY_B_PAIN_SCORE = {1: 8, 4: 5, 5: 2, 7: 7, 8: 8, 10: 8, 11: 6}
DAY_B_NO_PAIN = (2, 12)  # the shorthand writes the absence, so 0/10 is a given
DAY_B_SEVERITY_FILLED = (3, 6, 9)  # neither a score nor an absence: the run invents one
DAY_B_SEVERITY_PAINFUL = (6, 9)  # B8's anchors: the complaint itself is painful
DAY_B_B14 = (3,)  # B14's anchor, for issue #42. The complaint does not hurt

# The exam findings B14's "reasoned from a pain source" limb rests on. Case 3's
# shorthand never says pain and never says its absence, so the only thing that
# can carry her score above 0/10 is broken skin in the exam. Remove either
# string and B14 becomes a row demanding a number with nothing to derive it
# from -- which is the invented abnormal *Which value was chosen* forbids.
DAY_B_B14_PAIN_SOURCE = ("abrasions", "scratch marks")

# B9's ten: every case where *anything* in the filled-vitals license class was
# generated. The vital-less nine plus case 3, whose vital line is complete and
# whose severity the run has to invent. Not B1's list, which is the mistake the
# first draft of the row made. Issue #27.
DAY_B_B9 = (1, 3, 5, 6, 7, 8, 9, 10, 11, 12)
NO_PAIN = r"(?i)\bno pain\b"

# B10 and B11's anchors, for issue #33: the two cases that hang one duration off
# a multi-symptom chief complaint and then date a *different* symptom to
# yesterday. Both values each case must keep are named rather than positional --
# ``[1]`` never says *second onset statement* -- because the two limbs of the
# rule divide on a property of that second string. Case 8 writes ``right
# earache``, so attaching it is reading; case 9 writes ``this``, so attaching it
# rests on the ``is worse`` marker beside it and is an inference B11 declares.
class Timelines(NamedTuple):
    cc_duration: str
    second_onset: str


DAY_B_TWO_TIMELINES = {
    8: Timelines("x 2 days", "right earache yesterday"),
    9: Timelines("x 2 days", "states this started yesterday"),
}

# The other two cases that state a timeline twice and state the *same* one both
# times, which is why B10 sits on 8 and 9 rather than on all four. Case 12's
# second statement carries the ``saturdy`` typo, so both halves match on a
# prefix rather than on the whole word.
DAY_B_TIMELINES_AGREE = {4: "x 5 days", 12: "started saturd"}

# The span form row 16 falls back to when one symptom carries two durations is
# the clinician's own idiom rather than this repo's invention, and case 11 is
# where day-b writes it. Asserted because ``clinical-note`` rests the rule's
# residual limb on that claim in prose.
DAY_B_SPAN_IDIOM = (11, ("11-12 yrs ago", "3-4 days"))

# peds-bp keeps its source shift's numbering, so the gaps are the omitted cases.
PEDS_BP_CASES = (2, 3, 5, 8, 9)
PEDS_BP_VITAL_LINE = (3, 5)  # a structured line was written; only the BP is missing
# Case 8 joins them under the census's reading, which counts the bare word "temp"
# in "temp this vist is 99.5" as a vital. That is a real given temperature written
# into the exam prose rather than onto a vital line -- the distinction peds-bp's
# assertions list under *Still unresolved*, and the reason these are two constants.
PEDS_BP_ANY_VITAL = (3, 5, 8)

# Issue #29's measurement. ``clinical-note`` reads silence about a section two
# ways -- undocumented-and-inferable, or genuinely absent -- and which way a given
# slot takes is a property of how this clinician transcribes it. A slot he writes
# even when the answer is nothing is a transcription gap when silent. A slot he
# writes only when there *is* something is a real absence when silent.
#
# The two slots the corpus can decide split opposite ways, which is the whole
# ruling: allergies are written to say "none" eleven times out of sixteen, and
# tobacco is written to say "none" once out of fifteen.
#
# **Per case, not per clause.** Three cases write two allergy clauses and two
# write two tobacco clauses; counting clauses double-counts a patient and was the
# first reading taken of this, off a grep rather than off these constants.
DAY_A_ALLERGY_NONE = (2, 3, 7, 8, 9, 10)
DAY_A_ALLERGY_STATED = (6,)  # "seasonal allergies"
DAY_B_ALLERGY_NONE = (3, 10, 12)
DAY_B_ALLERGY_STATED = (2, 7, 11)
PEDS_BP_ALLERGY_NONE = (2, 9)
PEDS_BP_ALLERGY_STATED = (5,)

# Issue #78's split of that "names something" column, and it is the column the
# ruling actually turns on: ``NKDA`` is *no known drug allergy*, so a patient with
# hay fever is NKDA and a note naming one is no evidence against filling it.
#
# **Three of the five name nothing but an environmental allergy**, and only two
# name a drug. The constant above carried the comment *"7's 'allergic to
# prednisone' is the only drug one"* until 2026-08-16 and it was wrong: case 11
# writes ``allergies: seasonal allergies, levaquin``, and levaquin is a drug. The
# same undercount was published in ``skills/clinical-note/SKILL.md``, which said
# one of the sixteen written statuses named a drug allergy. Two do.
ALLERGY_DRUG_CASES = ((DAY_B, 7), (DAY_B, 11))
ALLERGY_FOOD_CASES = ()  # no committed input names a food allergen; untested, not wrong
ALLERGY_ENVIRONMENTAL_CASES = (
    (FIXTURES, 6), (DAY_B, 2), (DAY_B, 7), (DAY_B, 11), (PEDS_BP, 5),
)

DAY_A_TOBACCO_POSITIVE = (1, 2, 4, 7, 9)
DAY_B_TOBACCO_POSITIVE = (1, 2, 3, 4, 5, 7, 8, 11, 12)
DAY_B_TOBACCO_NEGATED = (6,)  # "no smoke, drink, drugs" -- the corpus's one denial


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def case(directory: Path, number: int) -> str:
    """One committed input, by set directory and case number."""
    return (directory / f"case-{number:02d}.md").read_text(encoding="utf-8")


OBESITY_BMI_SHORTHAND = REPO_ROOT / "fixtures" / "obesity-bmi" / "shorthand"


def all_fixture_shorthand():
    """Every committed shorthand input, all six sets -- 37 as of 2026-08-16.

    Separate from ``all_committed_cases`` on purpose. That helper reads the four
    sets the social-slot figures were measured over and is pinned at 31; this one
    reads the tree. The gap between them is
    `#143 <https://github.com/mshamblin5150-code/clinical-skills/issues/143>`_,
    which holds the decision about which is *the* denominator. Nothing here
    re-aims an existing figure.
    """
    for path in sorted((REPO_ROOT / "fixtures").glob("*/shorthand/case-*.md")):
        yield path, path.read_text(encoding="utf-8")


def all_committed_cases():
    """The 31 inputs both social-slot classes count against.

    Module-level rather than a method, because ``AllergyKindSplitsThreeWays``
    reads the same denominator and instantiating a ``TestCase`` to borrow one is
    a trick that breaks quietly across Python versions.
    """
    for directory in (FIXTURES, DAY_B, PEDS_BP, OBESITY_BMI_SHORTHAND):
        for path in sorted(directory.glob("case-*.md")):
            yield path, path.read_text(encoding="utf-8")


def day_b(number: int) -> str:
    return (DAY_B / f"case-{number:02d}.md").read_text(encoding="utf-8")


def day_b_line(number: int, prefix: str) -> str:
    """The first line of a day-b input starting with ``prefix``, lowercased.

    Crude in the same way ``day_b_plan`` is, and for the same reason: the two
    duration rows turn on *where* a timeline was written, so a whole-file
    substring test would score a chief complaint and a narrative onset as the
    same statement. These twelve write one ``cc`` line and one ``exam`` line
    each, which is the whole structure this needs. Case 12 punctuates its exam
    line with a period rather than a colon, so the prefix carries neither.
    """
    for line in day_b(number).splitlines():
        if line.strip().lower().startswith(prefix):
            return line.lower()
    return ""


def day_b_cc(number: int) -> str:
    return day_b_line(number, "cc")


def day_b_exam(number: int) -> str:
    return day_b_line(number, "exam")


def day_b_plan(number: int) -> str:
    """Everything after the last ``plan`` token in a day-b input, lowercased.

    Crude on purpose, and it has one job: separate an order the clinician placed
    from the same word appearing earlier in the note for another reason. Case 9
    writes ``covid`` in the exam prose, as the contact's diagnosis, and orders no
    swab -- so a whole-file substring test for ``covid`` would report the
    exposure as a test that was run. The plans in these twelve are all a trailing
    ``plan``-prefixed run of comma-separated items, which is the whole structure
    this needs.

    Two things keep the crudeness from failing open. The token is matched on word
    boundaries, so ``planned``, ``plantar`` and ``explains`` do not split the
    note and silently truncate the half being searched. And a note with no plan
    token raises rather than returning "", which would make every ``assertNotIn``
    below pass on an empty string.
    """
    parts = re.split(r"\bplan\b", day_b(number).lower())
    if len(parts) == 1:
        raise AssertionError(f"day-b case {number} has no plan line to read")
    return parts[-1]


def peds_bp(number: int) -> str:
    return (PEDS_BP / f"case-{number:02d}.md").read_text(encoding="utf-8")


class SplitNotes(unittest.TestCase):
    def test_splits_on_the_note_delimiter(self):
        text = "Date: 5-06-20\nNote 1\nfirst\n\nnote 2\nsecond\n"
        self.assertEqual(len(cc.split_notes(text)), 2)

    def test_drops_the_preamble_before_the_first_note(self):
        text = "Date: 5-06-20\nNote 1\nfirst\n"
        self.assertNotIn("Date:", cc.split_notes(text)[0])

    def test_delimiter_is_case_insensitive(self):
        # fixtures/day-a/shorthand/case-03.md really does open "NOte 3".
        text = "Note 1\na\n\nnote 2\nb\n\nNOte 3\nc\n"
        self.assertEqual(len(cc.split_notes(text)), 3)

    def test_tolerates_a_hash_before_the_number(self):
        self.assertEqual(len(cc.split_notes("Note #1\na\n\nNote #2\nb\n")), 2)

    def test_every_committed_fixture_is_one_note(self):
        for path in sorted(FIXTURES.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_concatenated_fixtures_split_back_into_ten(self):
        day = "\n\n".join(
            p.read_text(encoding="utf-8") for p in sorted(FIXTURES.glob("case-*.md"))
        )
        self.assertEqual(len(cc.split_notes(day)), 10)


class ReadCorpusDropsDuplicateDayFiles(unittest.TestCase):
    """One day file in the clinician's catalog is on disk twice, byte for byte.

    ``GLOSSARY.md`` and ``batch-shift`` both describe the catalog as 48 unique
    files; the census walked all 49 and reported a corpus eight encounters
    larger, with nothing to reconcile the two. Issue #16.

    Deduplication is by **content**, not by name: the copy does not share a
    filename with its original, so a name-based check would not have seen it.
    """

    SHIFT = "day header\nNote 1\n51 f\ncc: cough\n\nNote 2\n7 yo M\ncc: rash\n"
    OTHER = "day header\nNote 1\n34 f\ncc: fever\n"

    def corpus_of(self, files: dict[str, str]) -> cc.Corpus:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in files.items():
                (root / name).write_text(text, encoding="utf-8")
            return cc.read_corpus(root)

    def test_identical_content_under_different_names_is_read_once(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "scan-copy.txt": self.SHIFT})
        self.assertEqual(len(corpus.notes), 2)
        self.assertEqual(corpus.files, 2)
        self.assertEqual(corpus.unique_files, 1)

    def test_files_that_differ_are_all_kept(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "b.txt": self.OTHER})
        self.assertEqual(len(corpus.notes), 3)
        self.assertEqual(corpus.files, 2)
        self.assertEqual(corpus.unique_files, 2)

    def test_a_repeated_encounter_inside_one_file_is_not_deduplicated(self):
        """Dedup is per file. A shift that saw two alike patients saw two patients."""
        corpus = self.corpus_of({"a.txt": "hdr\nNote 1\n51 f\n\nNote 2\n51 f\n"})
        self.assertEqual(len(corpus.notes), 2)
        self.assertEqual(corpus.unique_files, 1)

    def test_encounters_stay_grouped_by_the_file_they_came_from(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "b.txt": self.OTHER})
        self.assertEqual([len(day) for day in corpus.day_files], [2, 1])


class EveryFileQuotesOneCatalogSize(unittest.TestCase):
    """One catalog, one denominator. Issue #63.

    This repo carried three at once: ``batch-shift`` step 3 and ``GLOSSARY.md``
    said 548 encounters, the census said 551, and drift row 13 said 559. Each was
    right about something and no file said which, so a reader picked whichever one
    they opened first. #129 retired the 559 and 2026-08-15 settled the rest --
    ``scratch/name-index.json`` holds one entry per encounter *that yielded a
    name*, three encounters put something other than the name on the line after
    ``Note N``, and 548 was that harvest's total rather than the catalog's.

    **Nothing in the repo noticed, which is the defect one level up.** The figure
    is prose in a dozen files and no two of them are read together. This is the
    check that reads them together, and it is deliberately a sweep rather than a
    list of the three files #63 named: the next disagreement will be in a file
    nobody thought to name.

    ``test_spelling_scan.py``'s reasoning, applied to a number instead of a
    table -- a figure that has drifted from the file beside it is worse than an
    absent one, because it reads as agreement.
    """

    #: What ``corpus_census.py`` reports over ``scratch/day-file-text``, and the
    #: only encounter total any file may state as current. Re-derive it with
    #: ``python tools/corpus_census.py`` -- this constant is not the measurement.
    CATALOG_SIZE = 551

    #: The figures this repo has retired, each mapped to the token its line must
    #: carry. A retired number stays quotable, and only where it is being put
    #: down: quoting one bare is how the disagreement started.
    #:
    #: - 548 is the tally the page read came away with, three short. Where it
    #:   appears, ``#63`` has to appear too, because that is where the
    #:   reconciliation lives and a bare 548 is indistinguishable from a relapse.
    #: - 559 is the pre-dedup reading, quoted twice by drift row 13 to say *why*
    #:   the denominator moved -- reading the directory without ``read_corpus``'s
    #:   byte-identical drop still returns it. Issue #16 moved it, issue #19
    #:   published it.
    RETIRED = {548: "#63", 559: "dedup"}

    #: Three digits opening with a 5, followed by the word: a *stated catalog
    #: size*. Narrow on purpose -- a bare ``\b5\d\d\b`` sweep over these trees
    #: also collects a 570 and a 500 out of two filled-anchor notes, a 513
    #: subtotal in clinical-note step 1, and two ICD-10 codes in
    #: setup-clinical-skills. The retired figures are checked bare as well, by
    #: ``RETIRED_ANYWHERE`` below, which is where that looseness is affordable.
    FIGURE = re.compile(r"\b(5\d\d)\s+(?:encounters|notes)\b")
    RETIRED_ANYWHERE = re.compile(r"\b(548|559)\b")

    #: Where a catalog size is prose, and the three trees deliberately left out:
    #:
    #: - ``docs/`` -- an ADR records what was true when it was written and is not
    #:   brought into line afterwards.
    #: - ``reference/`` -- holds no encounter figure today. **Not because it is
    #:   generated**, which was this comment's first reason and is only half
    #:   true: ``guidelines-catalog.md`` is curated with the tool auditing it,
    #:   and #106 is open on exactly that. The honest reason is the narrow one.
    #: - ``tools/`` -- a figure there is as likely to be a *test input* as a
    #:   claim. ``test_phi_scan.py`` feeds the scanner the literal string
    #:   ``measured 2026-08-11 across 559 encounters`` to prove ISO dates are not
    #:   flagged; sweeping it would refuse a string that asserts nothing.
    SEARCHED = ("skills", "fixtures")

    #: **A preserved run record is evidence, not prose, and may not be edited to
    #: satisfy a scanner.** ``fixtures/filled-anchor/notes/case-*.md`` is day-b
    #: run 1 byte for byte apart from two redacted site names; ADR 0001 and issue
    #: #73 are why it stays that way, and ``spelling_scan.py`` carries the same
    #: exemption at ``EVIDENCE_PREFIXES``.
    #:
    #: ``FIGURE`` cannot reach those notes -- a finished note does not write "551
    #: encounters" -- but ``RETIRED_ANYWHERE`` is a **bare** three-digit match and
    #: reaches anything. Those notes already carry bare 5xx literals as doses and
    #: values (a 500, a 561, a 582), so a future run whose record happened to
    #: contain 548 or 559 would fail this test in a file nobody is allowed to fix.
    #: Found sweeping #137, which is open on what that tree costs.
    #:
    #: **There are two such directories since #124, and the second is the sharper
    #: exposure.** ``fixtures/filled-anchor/run-2/`` is the first committed
    #: ``icd10-cpt`` run, immutable on the same terms -- and **a worksheet is made
    #: of ICD-10 codes**, so the exposure is not a coincidental dose literal. In the
    #: dotted form those worksheets use, **27 real FY2026 codes contain ``548`` or
    #: ``559``** -- ``M25.559 Pain in unspecified hip``,
    #: ``H60.559 Acute reactive otitis externa, unspecified ear``,
    #: ``M71.559 Other bursitis, not elsewhere classified, unspecified hip`` among
    #: them, all ordinary primary-care codes. That run already proposes ``M25.561``,
    #: ``M25.562``, ``H60.543`` and ``H60.501``, which are one digit away. Nothing
    #: matches **today**, so this is a latent trap rather than a live failure --
    #: which is exactly the state the ``notes/`` exemption was added in.
    EVIDENCE_PREFIXES = (
        Path("fixtures") / "filled-anchor" / "notes" / "case-",
        Path("fixtures") / "filled-anchor" / "run-2" / "case-",
    )

    #: The two files #63 named. **A sweep passes when a figure is deleted as
    #: happily as when it is corrected**, so each is pinned to state the current
    #: size *and* to keep pointing at the reconciliation. Without the second
    #: half, dropping the whole #63 paragraph from ``GLOSSARY.md`` still passes.
    MUST_QUOTE_IT = (
        Path("skills") / "batch-shift" / "SKILL.md",
        Path("skills") / "clinical-note" / "GLOSSARY.md",
    )

    class Figure(NamedTuple):
        """One stated figure, and the line it was stated on.

        The line text travels with it because every check below wants it. The
        first version returned a bare ``(path, line, value)`` and then reopened
        the file to recover the text it had already read.
        """

        path: Path
        line: int
        value: int
        text: str

        def __str__(self) -> str:
            return f"{self.path}:{self.line}"

    def scan(self, pattern: re.Pattern[str]) -> list["EveryFileQuotesOneCatalogSize.Figure"]:
        """Every match of ``pattern`` in the searched trees, in file order."""
        found = []
        for tree in self.SEARCHED:
            for path in sorted((REPO_ROOT / tree).rglob("*.md")):
                relative = path.relative_to(REPO_ROOT)
                if any(
                    str(relative).startswith(str(prefix))
                    for prefix in self.EVIDENCE_PREFIXES
                ):
                    continue
                lines = path.read_text(encoding="utf-8").splitlines()
                for number, text in enumerate(lines, 1):
                    for match in pattern.finditer(text):
                        found.append(
                            self.Figure(relative, number, int(match.group(1)), text)
                        )
        return found

    def figures(self):
        return self.scan(self.FIGURE)

    def test_the_sweep_finds_something(self):
        """A regex that has stopped matching would pass every assertion below."""
        self.assertGreater(len(self.figures()), 5)
        self.assertGreater(len(self.scan(self.RETIRED_ANYWHERE)), 0)

    def test_the_preserved_run_record_is_out_of_reach(self):
        """The exemption is asserted, because the trap it avoids is not here yet.

        No note under ``filled-anchor/notes/`` carries a 548 or a 559 today, so
        deleting the exemption breaks nothing and the sweep would look fine. What
        would break is a *later* run record, in a file ADR 0001 forbids editing.
        So the property pinned is that the tree is not read at all, checked
        against a bare digit sweep that every note matches.

        **The expected paths are written out here rather than taken from
        ``EVIDENCE_PREFIXES``.** Checking the constant against itself passes for
        any value it holds -- point it at a directory that does not exist and the
        sweep reads the notes while this test still goes green. That is how the
        first version of this was written and it is why the literals are repeated.

        **Both preserved run records are named, and the second one is why the
        constant became a tuple.** ``run-2/`` is the first committed ``icd10-cpt``
        run, immutable on ADR 0001's terms, and made of ICD-10 codes -- 27 real
        FY2026 codes contain ``548`` or ``559``, so its trap is a routine coding
        outcome rather than a coincidence.
        """
        expected = (
            "fixtures/filled-anchor/notes/case-",
            "fixtures/filled-anchor/run-2/case-",
        )
        swept = {str(figure.path) for figure in self.scan(re.compile(r"(\d)"))}
        self.assertTrue(swept, "the sweep read nothing at all")
        leaked = sorted(
            path
            for path in swept
            if path.replace("\\", "/").startswith(expected)
        )
        self.assertEqual(leaked, [])

        # And both trees really are there, so the assertion above is not vacuous.
        for directory in ("notes", "run-2"):
            records = sorted(
                (REPO_ROOT / "fixtures" / "filled-anchor" / directory).glob("case-*.md")
            )
            self.assertGreater(len(records), 5, directory)

    def test_no_file_states_a_second_catalog_size(self):
        wrong = [
            str(figure)
            for figure in self.figures()
            if figure.value != self.CATALOG_SIZE and figure.value not in self.RETIRED
        ]
        self.assertEqual(wrong, [], f"a catalog size other than {self.CATALOG_SIZE}")

    def test_a_retired_figure_appears_only_where_it_is_retired(self):
        """548 and 559 stay quotable, and only beside the reason they moved.

        Checked bare rather than only as ``N encounters``, because the sentence
        putting a figure down rarely repeats the noun -- *this step said 548
        until 2026-08-15* would otherwise sail straight through.
        """
        for figure in self.scan(self.RETIRED_ANYWHERE):
            marker = self.RETIRED[figure.value]
            self.assertIn(
                marker,
                figure.text,
                f"{figure} quotes {figure.value} without '{marker}' on the line",
            )

    def test_the_two_provenance_sentences_still_state_it(self):
        for relative in self.MUST_QUOTE_IT:
            stated = [f.value for f in self.figures() if f.path == relative]
            self.assertIn(
                self.CATALOG_SIZE, stated, f"{relative} states no catalog size"
            )
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "#63", text, f"{relative} states the size and drops the reconciliation"
            )


class SurveyFilesCase(unittest.TestCase):
    """Shared day files and the one-line survey call, for the two cases below.

    They are separate cases because they are separate claims by separate skills
    — ADR 0001's reasoning — but the fixtures and the call are the same three
    lines either way, and a second copy of them is a second thing to keep in
    step. Nothing here asserts; both subclasses do.
    """

    AGELESS = ("Note 1\ndob 4/4/44\ncc: cough\n", "Note 2\ndob 5/5/55\ncc: rash\n")
    MIXED = ("Note 1\ndob 4/4/44\ncc: cough\n", "Note 2\n51 f\ncc: rash\n")
    EVERY = ("Note 1\n51 f\ncc: cough\n", "Note 2\n7 yo M\ncc: rash\n")

    def survey(self, *days: tuple[str, ...]) -> cc.FileCensus:
        return cc.survey_files(cc.Corpus(day_files=days, files=len(days)))


class SurveyFilesCountsFilesNotEncounters(SurveyFilesCase):
    """The claim clinical-note step 1 rests on, made re-derivable. Issue #16.

    Step 1 quotes no share deliberately, and says instead that whole day files
    state no age at all. Nothing printed that until this existed, which left the
    replacement claim exactly as unverifiable as the 353-encounter one it
    replaced.
    """

    def test_a_file_with_no_age_anywhere_counts(self):
        self.assertEqual(self.survey(self.AGELESS).with_no_stated_age, 1)

    def test_one_stated_age_is_enough_to_clear_a_file(self):
        self.assertEqual(self.survey(self.MIXED).with_no_stated_age, 0)

    def test_counts_files_and_not_the_encounters_inside_them(self):
        census = self.survey(self.AGELESS, self.AGELESS, self.MIXED)
        self.assertEqual(census.with_no_stated_age, 2)
        self.assertEqual(census.unique_files, 3)

    def test_an_empty_file_is_not_a_file_without_an_age(self):
        """A file the delimiter found nothing in says nothing about ages."""
        self.assertEqual(self.survey(()).with_no_stated_age, 0)

    def test_the_duplicate_is_not_counted_twice(self):
        corpus = cc.Corpus(day_files=(self.AGELESS,), files=2)
        self.assertEqual(cc.survey_files(corpus).files, 2)
        self.assertEqual(cc.survey_files(corpus).unique_files, 1)


class SurveyFilesSplitsTheCatalogByAgeExtreme(SurveyFilesCase):
    """The evidence for *measure the file in front of you*. Issue #36.

    ``batch-shift`` step 3 quoted four corpus-wide shares and, in the very next
    paragraph, told the reader not to carry a share between the two halves of
    the catalog. The shares are gone; what replaces them is the shape of the
    per-file distribution, which is what makes the instruction an argument
    rather than an assertion. A corpus that really is bimodal has files piled at
    both ends; one sitting uniformly at its own corpus-wide rate -- 65% of 551
    encounters state an age, measured 2026-08-11 -- would have almost none.

    **No threshold is invented.** "Dominant" needs a boundary, and a fourth
    boundary in this repo is a defect waiting to happen — see the age bands. The
    two ends are *every* and *none*, which need no boundary at all, and
    everything else is mixed.

    The three counts overlap the case above at ``with_no_stated_age`` on
    purpose: that field is now one leg of a partition, and a change that got the
    other two right while quietly moving it would pass every test up there.
    """

    def test_a_file_stating_an_age_throughout_counts_at_the_every_end(self):
        self.assertEqual(self.survey(self.EVERY).with_age_in_every_note, 1)

    def test_one_ageless_encounter_moves_a_file_out_of_every(self):
        census = self.survey(self.MIXED)
        self.assertEqual(census.with_age_in_every_note, 0)
        self.assertEqual(census.with_mixed_age, 1)

    def test_a_file_with_no_age_anywhere_is_not_mixed(self):
        census = self.survey(self.AGELESS)
        self.assertEqual(census.with_mixed_age, 0)
        self.assertEqual(census.with_no_stated_age, 1)

    def test_a_single_encounter_file_is_an_end_and_never_the_middle(self):
        """One encounter cannot disagree with itself, so it is always an extreme."""
        census = self.survey(("Note 1\n51 f\n",), ("Note 1\ndob 4/4/44\n",))
        self.assertEqual(census.with_age_in_every_note, 1)
        self.assertEqual(census.with_no_stated_age, 1)
        self.assertEqual(census.with_mixed_age, 0)

    def test_an_empty_file_lands_in_none_of_the_three(self):
        """``all()`` of nothing is true, and an empty file states no ages at all.

        Letting it in at the *every* end is the vacuous-truth bug, and it would
        inflate the exact figure batch-shift now rests on. ``with_no_stated_age``
        already excludes it; this is the same exclusion on the other end.
        """
        census = self.survey(())
        self.assertEqual(census.with_age_in_every_note, 0)
        self.assertEqual(census.with_no_stated_age, 0)
        self.assertEqual(census.with_mixed_age, 0)

    def test_the_three_partition_the_files_that_hold_encounters(self):
        days = (self.AGELESS, self.EVERY, self.MIXED, self.EVERY)
        census = self.survey(*days)
        self.assertEqual(
            census.with_age_in_every_note
            + census.with_no_stated_age
            + census.with_mixed_age,
            len(days),
        )

    def test_it_counts_files_and_not_the_encounters_inside_them(self):
        census = self.survey(self.EVERY, self.EVERY)
        self.assertEqual(census.with_age_in_every_note, 2)


class BloodPressure(unittest.TestCase):
    def test_reads_a_lowercase_reading(self):
        self.assertEqual(cc.bp_readings("bp 134/77 hr 79"), [(134, 77)])

    def test_reads_an_uppercase_reading(self):
        self.assertEqual(cc.bp_readings("BP 139/85 hr 91"), [(139, 85)])

    def test_reads_an_unprefixed_reading(self):
        self.assertEqual(cc.bp_readings("126/83 hr 84 t 97.1"), [(126, 83)])

    def test_ignores_a_date_of_birth(self):
        self.assertEqual(cc.bp_readings("dob 03/04/1990"), [])

    def test_ignores_a_pain_score(self):
        self.assertEqual(cc.bp_readings("c/o 8/10 pain, 10/10 at worst"), [])

    def test_ignores_heart_sounds(self):
        self.assertEqual(cc.bp_readings("s1,s2, 2/2. positive bowel"), [])

    def test_ignores_a_drug_fraction(self):
        self.assertEqual(cc.bp_readings("zithromax 200/5ml 3/4 t x 3 days"), [])

    def test_has_bp_follows_the_readings(self):
        self.assertTrue(cc.has_bp("bp 117/74"))
        self.assertFalse(cc.has_bp("hx: htn, djd"))

    def test_normal_is_below_130_over_80(self):
        self.assertTrue(cc.is_normal_bp((117, 74)))
        self.assertFalse(cc.is_normal_bp((134, 77)))  # systolic out
        self.assertFalse(cc.is_normal_bp((126, 83)))  # diastolic out
        self.assertFalse(cc.is_normal_bp((130, 80)))  # boundary is exclusive

    def test_fixture_readings(self):
        self.assertEqual(cc.bp_readings(fixture("case-01.md")), [(134, 77)])
        self.assertEqual(cc.bp_readings(fixture("case-03.md")), [(139, 85)])


class BodyMeasurements(unittest.TestCase):
    def test_height_in_feet_and_inches(self):
        self.assertTrue(cc.has_height("ht 5'4\" wt 212 lbs"))

    def test_height_in_bare_inches(self):
        self.assertTrue(cc.has_height("spo2 95 ht 62.5 wt 141"))

    def test_height_without_the_token(self):
        self.assertTrue(cc.has_height("rr 20 spo2 96 36in 33lb"))

    def test_height_spelled_out_in_inches(self):
        self.assertTrue(cc.has_height("spo2 99% ht 63 inches wt 160"))

    def test_height_survives_a_mistyped_token(self):
        # case-08 really does read "hr 65 inches"; the fixture README names that
        # typo as a defect the set exists to find, so "ht" cannot be relied on.
        self.assertTrue(cc.has_height(fixture("case-08.md")))
        self.assertTrue(cc.has_height(fixture("case-05.md")))
        self.assertTrue(cc.has_height(fixture("case-10.md")))

    def test_height_with_no_space_after_the_token(self):
        # He writes the vital line both ways. "ht5'7"" defeats a trailing \b on the
        # token, and the feet-and-inches alternative cannot rescue it either: there
        # is no word boundary between the "t" and the "5". Three encounters in the
        # corpus were read as having no height because of this.
        self.assertTrue(cc.has_height("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertTrue(cc.has_height("spo2 100% ht62.5 wt141"))

    def test_a_bare_token_is_still_a_height(self):
        # The no-space form is added, never substituted for the plain token.
        self.assertTrue(cc.has_height("ht 62.5 wt 141"))

    def test_a_measurement_in_prose_is_not_a_height(self):
        self.assertFalse(cc.has_height("wt 165 in the office today"))

    def test_ht_inside_a_word_is_not_a_height(self):
        self.assertFalse(cc.has_height("hx: htn, hypothyroid, right knee pain"))

    def test_weight_with_the_token(self):
        self.assertTrue(cc.has_weight("ht 5'10 wt 285"))

    def test_weight_by_unit_alone(self):
        self.assertTrue(cc.has_weight("36in 33lb"))

    def test_weight_with_no_space_after_the_token(self):
        self.assertTrue(cc.has_weight("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertTrue(cc.has_weight("ht 5'10 wt285"))

    def test_no_weight(self):
        self.assertFalse(cc.has_weight("hx: htn, djd, l knee surgery"))

    def test_the_no_space_form_still_requires_a_number(self):
        # "htn" is the decoy the digit exists to exclude: without it the new
        # alternative would read every hypertension history as a height.
        self.assertFalse(cc.has_height("hx: htn, gerd, hypothyroid"))

    def test_weight_has_no_equivalent_decoy(self):
        """Stated rather than asserted, because there is nothing to assert.

        The plain ``\\bwt\\b`` alternative predates this change and still counts a
        bare "wt" with no value as a weight. So there is no string that the
        no-space alternative must reject and the plain one accepts, and a
        mirror of the height test above would be vacuous -- it would pass
        whatever the new alternative did.
        """
        self.assertTrue(cc.has_weight("wt not recorded"))  # by the plain token

    def test_fixtures_carry_both(self):
        for name in ("case-01.md", "case-03.md"):
            with self.subTest(case=name):
                self.assertTrue(cc.has_height(fixture(name)))
                self.assertTrue(cc.has_weight(fixture(name)))


class OtherVitals(unittest.TestCase):
    def test_pulse_temp_rr_spo2(self):
        self.assertTrue(cc.has_other_vitals("hr 130 t 97.3 rr 32 spo2 99%"))

    def test_absent(self):
        self.assertFalse(cc.has_other_vitals("cc: right foot pain x 3-4 months"))

    def test_any_vital_is_the_union(self):
        self.assertTrue(cc.has_any_vital("hr 130 t 97.3 rr 32 spo2 99% wt 15"))
        self.assertTrue(cc.has_any_vital("bp 170/78"))
        self.assertFalse(cc.has_any_vital("cc: cough x 2 days\nallergy nkda"))


class PainScore(unittest.TestCase):
    """The severity marker behind issue #30.

    ``clinical-note`` now requires an OLDCARTS severity on every note, written
    as a pain scale. What the census answers is how often the clinician writes
    one himself -- the population the rule fills for is the remainder, and a
    rule about it should be able to say how large it is.

    The extractor lives beside ``BP_PAIR`` because they read the same shape and
    must not read each other's: ``BloodPressure.test_ignores_a_pain_score``
    is this class seen from the other side.
    """

    def test_a_bare_score(self):
        self.assertEqual(cc.pain_scores("he c/o 8/10 pain"), [8])

    def test_spaces_around_the_slash(self):
        self.assertEqual(cc.pain_scores("rates his pain 2 / 10"), [2])

    def test_both_ends_of_the_scale_are_in_range(self):
        self.assertEqual(cc.pain_scores("0/10 now, was 10/10 overnight"), [0, 10])

    def test_above_the_scale_is_not_a_score(self):
        """``12/10`` is rejected, and the reason is the decoy it shares.

        Patients do say "twelve out of ten", so this loses a real score now and
        then. Above 10 the same characters are far likelier to be a written
        date -- the false positive the module cannot otherwise exclude at all,
        see the limit in ``corpus_census`` -- so the range check is spent where
        it buys the most.
        """
        self.assertEqual(cc.pain_scores("12/10"), [])

    def test_a_score_that_ends_a_sentence(self):
        """The form BP_PAIR's trailing guard would have thrown away.

        Two of day-b's seven scores are written this way, and copying that
        guard verbatim dropped both. On a vital line a following dot is a
        decimal point; in prose it is a full stop.
        """
        self.assertEqual(cc.pain_scores("rates his pain 2/10. there is swelling"), [2])
        self.assertEqual(cc.pain_scores("exacerbated by movment 6/10."), [6])

    def test_a_date_after_the_score_is_still_not_a_score(self):
        # Loosening the trailing guard must not reach the digits: "10/10/25"
        # is a date, and the slash and digit alternatives are what refuse it.
        self.assertEqual(cc.pain_scores("f/u 10/10/25"), [])
        self.assertEqual(cc.pain_scores("wbc 6/100"), [])

    def test_heart_sounds_are_not_a_score(self):
        self.assertEqual(cc.pain_scores("s1,s2 2/2"), [])

    def test_a_blood_pressure_is_not_a_score(self):
        self.assertEqual(cc.pain_scores("bp 121/61 hr 64 t 96.9"), [])

    def test_a_pressure_whose_digits_end_in_ten_is_not_a_score(self):
        # The lookaround is what does this: "10" sits inside "110", so the
        # character before it is a digit and the match is refused. Without it
        # every systolic in the hundreds would offer a "10" to pair with.
        self.assertEqual(cc.pain_scores("bp 110/104"), [])

    def test_a_concentration_is_not_a_score(self):
        self.assertEqual(cc.pain_scores("zithromax 200/5ml 3/4 t x 3 days"), [])

    def test_a_suture_size_is_not_a_score(self):
        # day-b case 6 writes "5 5-0 sutures placed" and carries no pain score;
        # a run that read one there would make the fixture's own split wrong.
        self.assertEqual(cc.pain_scores("lidocaine 1% 5 5-0 sutures placed"), [])

    def test_presence_follows_the_values(self):
        self.assertTrue(cc.has_pain_score("c/o 8/10 body aches"))
        self.assertFalse(cc.has_pain_score("cc: itching, can feel ince in her ears"))

    def test_the_survey_counts_the_notes_not_the_scores(self):
        c = cc.survey(["c/o 8/10 pain, later 6/10", "no score here", "2/10"])
        self.assertEqual(c.with_pain_score, 2)


class DocumentedHypertension(unittest.TestCase):
    """The marker behind the counts issue #23 turned on.

    ``clinical-note`` used to instruct that a documented hypertensive gets a
    hypertensive filled pressure. What decided that rule was how often the
    clinician's *own* transcribed pressures agree with it, and that count is
    only computable if the history marker is extractable. An extractor that
    quietly stopped matching would leave the rule's stated evidence asserting a
    number nobody could recompute -- the failure this whole module exists for.
    """

    def test_the_abbreviation(self):
        self.assertTrue(cc.has_documented_hypertension("hx: htn, djd"))

    def test_the_word_both_ways(self):
        self.assertTrue(cc.has_documented_hypertension("hx of hypertension"))
        self.assertTrue(cc.has_documented_hypertension("known hypertensive"))

    def test_the_code(self):
        self.assertTrue(cc.has_documented_hypertension("pre-existing: I10, E11.9"))

    def test_absent(self):
        self.assertFalse(cc.has_documented_hypertension("cc: cough x 2 days"))

    def test_height_is_not_hypertension(self):
        """``ht`` welded to its value is the shape that defeated other tokens.

        ``\\bhtn\\b`` cannot match inside "ht5'7"" and must not, but the pair is
        close enough in this corpus's shorthand to be worth pinning: three
        encounters were misread once already over exactly this welding.
        """
        self.assertFalse(cc.has_documented_hypertension("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertFalse(cc.has_documented_hypertension("ht 5'4\" wt 212 lbs"))

    def test_a_negated_mention_still_counts(self):
        """Asserted so the known over-count is visible rather than assumed away.

        No negation guard is carried, on the same reasoning as ``OBESITY``: the
        corpus holds no negated form among the 175 encounters that write the
        token, audited 2026-08-11, so a guard would be exercised by nothing.
        This is the line to change if one appears -- and the test that would
        start failing when it does.
        """
        self.assertTrue(cc.has_documented_hypertension("denies htn"))

    def test_day_b_documents_it_in_exactly_four_cases(self):
        """Two with a pressure and two without, and the pair matters.

        ``DAY_B_HYPERTENSIVE`` is narrower than this on purpose -- it is the two
        B2 anchors, which need the pressure *absent* so the run has to fill one.
        Cases 2 and 3 document the same history and carry a given pressure, so
        they are hypertensives the extractor must find and B2 must not score.
        An extractor matching everything would pass the first assertion alone.
        """
        matched = [n for n in range(1, 13) if cc.has_documented_hypertension(day_b(n))]
        self.assertEqual(matched, list(DAY_B_DOCUMENTS_HTN))
        self.assertEqual(
            [n for n in matched if cc.has_bp(day_b(n))], list(DAY_B_HTN_WITH_BP)
        )

    def test_case_2_is_the_normal_hypertensive_the_rule_rests_on(self):
        """day-b/assertions.md cites this reading by value; here it is checked.

        A *given* 121/61 against a documented hypertension is the in-corpus
        proof that B2's second exit describes a real patient rather than a
        loophole -- and the single clearest refutation of the retired rule that
        a documented hypertensive gets a hypertensive pressure. Case 3 is the
        other way at 147/81, which is what stops the pair being one-sided.
        """
        self.assertEqual(cc.bp_readings(day_b(2)), [(121, 61)])
        self.assertTrue(cc.all_bp_readings_normal(day_b(2)))
        self.assertEqual(cc.bp_readings(day_b(3)), [(147, 81)])
        self.assertFalse(cc.all_bp_readings_normal(day_b(3)))

    def test_the_documented_false_positives_are_the_ones_documented(self):
        """Each is audited at zero in the corpus; each would still match here.

        The comment beside ``HYPERTENSION`` lists three ways it can be wrong and
        says all three cost nothing today. That is a claim about the corpus, not
        about the regex, and this is what stops the two being confused: the
        regex really does behave this way, and the comment is honest only for
        as long as the audit holds.
        """
        # Included wrongly: a different disease, and a non-diagnosis.
        self.assertTrue(cc.has_documented_hypertension("hx: pulmonary hypertension"))
        self.assertTrue(cc.has_documented_hypertension("pre-hypertensive"))
        # Excluded wrongly: the plural defeats the closing boundary.
        self.assertFalse(cc.has_documented_hypertension("two hypertensives seen"))

    def test_the_code_is_matched_in_either_case(self):
        """Wanted, not tolerated -- and asserted because it looks accidental.

        ``I10`` is written with a capital in the pattern, under a leading
        ``(?i)`` that a reader scanning the alternatives can easily miss.
        """
        self.assertTrue(cc.has_documented_hypertension("pre-existing: i10"))
        self.assertTrue(cc.has_documented_hypertension("pre-existing: I10"))

    def test_the_lenient_leg_is_counted_beside_the_strict_one(self):
        """Both legs are printed so the day they diverge is visible.

        The strict figure is the one the rule was written on. It is only safe
        to quote while the difference is inspectable, which is what the lenient
        counter exists to make it.
        """
        c = cc.survey(["hx: htn. bp 162/98, recheck 128/78", "hx: htn. bp 118/70"])
        self.assertEqual(c.hypertension_bp_normal, 1)
        self.assertEqual(c.hypertension_bp_normal_lenient, 2)

    def test_the_survey_counts_the_population_and_its_pressures(self):
        notes = [
            "hx: htn. bp 117/74",  # documented, and normal
            "hx: htn. bp 148/92",  # documented, and not
            "hx: htn, no vitals taken",  # documented, no pressure to count
            "cc: cough. bp 118/70",  # a pressure, but no hypertension
        ]
        c = cc.survey(notes)
        self.assertEqual(c.with_hypertension, 3)
        self.assertEqual(c.hypertension_with_bp, 2)
        self.assertEqual(c.hypertension_bp_normal, 1)
        self.assertEqual(c.hypertension_bp_not_normal, 1)

    def test_a_note_is_normal_only_when_every_reading_is(self):
        """Per note, not per reading, and the strict leg is the safe one.

        A recheck after treatment is the case: counting the note normal on its
        best reading would overstate how often his hypertensives sit at target,
        which is the direction that would flatter the rule being written.
        """
        c = cc.survey(["hx: htn. bp 162/98, recheck 128/78"])
        self.assertEqual(c.hypertension_with_bp, 1)
        self.assertEqual(c.hypertension_bp_normal, 0)


class DocumentedObesity(unittest.TestCase):
    """The markers behind the counts issue #15 turned on.

    A row demanding that a *filled* BMI be consistent with a documented obesity
    needs a case whose shorthand documents one. day-b has none, so the figures
    naming how many the corpus holds are what justify ``fixtures/obesity-bmi``
    existing at all -- and an extractor that quietly stopped matching would leave
    that justification asserting a number nobody could recompute.
    """

    def test_obesity_in_a_history_line(self):
        self.assertTrue(cc.has_documented_obesity("hx: htn, obesity, gerd"))

    def test_the_adjective_counts_too(self):
        self.assertTrue(cc.has_documented_obesity("exam: obese female, nad"))

    def test_morbid_obesity(self):
        self.assertTrue(cc.has_documented_obesity("hx morbid obesity, osa"))

    def test_absent(self):
        self.assertFalse(cc.has_documented_obesity("hx: dm, copd, prostate ca"))

    def test_a_lung_lobe_is_not_an_obesity(self):
        """The decoy that was live in the corpus, not a hypothetical one.

        ``obes`` with no leading boundary matches inside "lobes", and the
        clinician writes lung fields constantly: "crackles in the bilateral
        upper lobes" counted as documented obesity until 2026-08-11. It
        inflated the corpus figure this whole fixture set is justified by,
        which is the silent wrong number this file exists to prevent.
        """
        self.assertFalse(cc.has_documented_obesity("crackles in the bilateral upper lobes"))
        self.assertFalse(cc.has_documented_obesity("wheezing in the b/l lower lobes"))

    def test_a_negated_obesity_is_not_excluded(self):
        """Stated rather than asserted, because there is nothing to exclude.

        ``\bobes`` matches whatever word precedes it, so "no obesity" would
        count. A negation guard is not carried: audited 2026-08-11, the corpus
        contains zero negated forms among the encounters that write the token,
        so the guard would be exercised by nothing and could break silently in
        either direction. This is the line to change if one appears.

        **No count is quoted here on purpose.** An earlier draft said "the five
        encounters", which was the pre-``\b`` figure and stayed behind when the
        lobes decoy dropped it. A number in a docstring is one nothing
        recomputes; ``corpus_census.py`` prints the live one.
        """
        self.assertTrue(cc.has_documented_obesity("denies obesity"))  # by design

    def test_bariatric_surgery(self):
        for shorthand in (
            "hx gastric bypass 2016",
            "s/p bariatric surgery",
            "hx: sleeve gastrectomy, chole",
            "lap band placed, then removed",
            "s/p roux-en-y",
        ):
            with self.subTest(shorthand=shorthand):
                self.assertTrue(cc.has_bariatric_history(shorthand))

    def test_bariatric_absent(self):
        self.assertFalse(cc.has_bariatric_history("hx: chole, btl, d&c"))

    def test_bariatric_is_not_obesity(self):
        """The two markers are deliberately separate, and O2 rests on the split.

        A post-bypass patient is where a sub-30 BMI is *plausible and
        accountable* -- the second exit -- while a written "obesity" is where an
        unexplained sub-30 BMI is the defect. Folding them into one marker would
        lose the distinction the set is built on.
        """
        self.assertFalse(cc.has_documented_obesity("s/p gastric bypass"))
        self.assertFalse(cc.has_bariatric_history("hx: obesity"))

    def test_sleep_apnea(self):
        for shorthand in ("hx osa", "uses cpap nightly", "obstructive sleep apnea"):
            with self.subTest(shorthand=shorthand):
                self.assertTrue(cc.has_sleep_apnea(shorthand))

    def test_osa_needs_its_own_word(self):
        # The token is three letters and would otherwise fire inside a longer one.
        self.assertFalse(cc.has_sleep_apnea("hx: rosacea, gerd"))

    def test_body_measurement_is_the_union_of_height_and_weight(self):
        self.assertTrue(cc.has_body_measurement("ht 5'4\" wt 212 lbs"))
        self.assertTrue(cc.has_body_measurement("wt 212"))
        self.assertTrue(cc.has_body_measurement("36in"))
        self.assertFalse(cc.has_body_measurement("bp 142/88 hr 79 t 98.1"))

    def test_the_survey_counts_the_qualifying_shape(self):
        """Documented obesity *and* no body measurement -- the fixturable case."""
        c = cc.survey(
            [
                "hx: obesity, htn\ncc: cough",          # qualifies
                "hx: obesity\nht 5'4\" wt 240",          # documented, measured
                "hx: gastric bypass\ncc: sore throat",   # bariatric, qualifies
                "hx: dm\ncc: rash",                      # neither
            ]
        )
        self.assertEqual(c.with_obesity, 2)
        self.assertEqual(c.obesity_no_measurement, 1)
        self.assertEqual(c.with_bariatric, 1)
        self.assertEqual(c.bariatric_no_measurement, 1)


class HedgedDiagnosis(unittest.TestCase):
    """Guards the figure drift row 13 cites, and the decoys that inflate it.

    The row is in ``skills/clinical-note/SKILL.md`` and it turns on a rate: a
    differential is generated in every note, a hedge appears in the shorthand of
    about one in sixteen, and the row's two halves therefore fire at very
    different frequencies. Issue #19 published that percentage before anything
    could recompute it. This is what recomputes it.

    Every token here is a **prefix or boundary** match for the same reason
    ``OBESITY`` is: a four-letter clinical token hides inside longer words, and
    this corpus is where that was learned. ``prob`` is the live case --
    ``fixtures/day-a/shorthand/case-10.md`` writes "he states he has problems
    urinatin", and a bare ``prob`` counts that encounter as hedged.
    """

    OBESITY_BMI = REPO_ROOT / "fixtures" / "obesity-bmi" / "shorthand"

    def test_prob_alone(self):
        self.assertTrue(cc.has_hedge("dx prob viral uri"))

    def test_probable_and_probably(self):
        self.assertTrue(cc.has_hedge("probable strep"))
        self.assertTrue(cc.has_hedge("probably viral"))

    def test_a_problem_is_not_a_hedge(self):
        """The decoy, asserted against the fixture that carries it."""
        self.assertFalse(cc.has_hedge("he states he has problems urinatin"))
        self.assertFalse(cc.has_hedge(fixture("case-10.md")))

    def test_possible_forms(self):
        for text in ("poss ptx", "possible cellulitis", "possibly viral"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_hedge(text))

    def test_suspected_forms(self):
        for text in ("susp fx", "suspected strep", "suspicion for pe"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_hedge(text))

    def test_rule_out(self):
        self.assertTrue(cc.has_hedge("r/o pna"))
        self.assertTrue(cc.has_hedge("R/O fracture"))

    def test_versus(self):
        self.assertTrue(cc.has_hedge("bronchitis vs pna"))

    def test_a_vital_signs_header_is_not_a_versus(self):
        """``VS`` opens a vital line and would otherwise read as a hedge.

        The colon is **not** what distinguishes them, which a first version of
        this guard assumed: he writes ``VS 138/86`` and ``VS- 138/86`` too, and
        both slipped through a lookahead that only rejected ``VS:``. What
        actually separates the two is what follows -- a vital line runs into a
        number, a differential runs into a diagnosis.
        """
        for text in ("VS: 138/86, hr 88, t 98.8", "vs : 138/86", "VS 138/86 hr 88",
                     "VS- 138/86", "VS. 98.6"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_hedge(text))

    def test_a_spelled_out_suspension_is_not_a_suspicion(self):
        """Ordinary pediatric prescribing, and it would inflate the count."""
        for text in ("amoxicillin suspension 400/5", "amox suspended"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_hedge(text))

    def test_an_abbreviated_suspension_still_counts(self):
        """The limit the guard cannot reach, pinned rather than wished away.

        ``susp 250/5ml`` is a suspension and ``susp fx`` is a suspicion, and the
        four letters are identical. HEDGE says so in prose; this is the test that
        makes the claim checkable, and it is why the figure is a proxy.
        """
        self.assertTrue(cc.has_hedge("susp 250/5ml"))

    def test_a_genuine_question_counts_and_that_is_deliberate(self):
        """A known over-count, pinned so it stays a decision rather than a bug.

        ``[a-z]\\?`` is the loosest alternative in HEDGE and it cannot tell
        ``strep?`` from a question written into the prose. It is kept because
        issue #19's published table counted the same seven tokens, so the figure
        stays comparable to the one already on the ticket -- and because the
        figure is quoted as a proxy rather than a bound.
        """
        self.assertTrue(cc.has_hedge("pt asks: is this contagious?"))

    def test_the_prefixed_question_mark_is_not_matched(self):
        """``?fx`` is the other shorthand form, and it is deliberately absent.

        No committed fixture carries it and the corpus cannot be audited from
        every clone, so an alternative matched by nothing is one nothing can
        catch going wrong -- the reasoning ``SLEEP_APNEA`` already carries for
        ``apnoea``. This is the line to change if the form turns up.
        """
        self.assertFalse(cc.has_hedge("?fx right wrist"))

    def test_likely(self):
        self.assertTrue(cc.has_hedge("likely viral"))

    def test_unlikely_is_deliberately_not_counted(self):
        """A rejection is a conclusion, not a hedge, and the count says so."""
        self.assertFalse(cc.has_hedge("unlikely to be bacterial"))

    def test_a_question_mark_suffix(self):
        self.assertTrue(cc.has_hedge("strep? throat cx sent"))

    def test_a_plain_note_carries_none(self):
        self.assertFalse(cc.has_hedge("cc: sore throat x 3 days\ndx strep pharyngitis"))

    def test_day_a_and_day_b_carry_no_hedge(self):
        """Why no hedged-input assertion can be written against either set."""
        for path in sorted(FIXTURES.glob("case-*.md")) + sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertFalse(cc.has_hedge(path.read_text(encoding="utf-8")))

    def test_obesity_bmi_case_1_does_carry_one(self):
        """Issue #19 said no committed fixture carries a hedge token. One does.

        ``possibly ultrasounds there`` hedges **a past test**, not a diagnosis,
        so the ticket's substantive point survives: nothing committed can anchor
        an assertion about a hedged *diagnosis*. The token count is what was
        wrong, and this is the case that would have failed a blanket claim.
        """
        self.assertTrue(cc.has_hedge((self.OBESITY_BMI / "case-01.md").read_text(encoding="utf-8")))

    def test_the_survey_counts_hedged_encounters(self):
        c = cc.survey(
            [
                "dx prob viral uri",              # hedged
                "bronchitis vs pna",              # hedged
                "he has problems urinatin",       # the decoy
                "cc: rash\ndx contact dermatitis",  # plain
            ]
        )
        self.assertEqual(c.with_hedge, 2)


class OrganismSpecificPool(unittest.TestCase):
    """Guards the pool ``fixtures/hedged-dx`` says it drew from.

    That set is a **pick, not a population** -- three encounters out of
    seventeen, chosen by reading them -- so the only thing it can offer instead
    of recomputability is a re-derivable pool. Its README publishes 17 and the
    census prints it. This is what stops the two drifting apart.

    Nothing here runs against ``scratch/``: the three committed inputs are the
    worked examples, and the decoys are literals. Issue #49.
    """

    HEDGED_DX = REPO_ROOT / "fixtures" / "hedged-dx" / "shorthand"

    def test_every_hedged_dx_case_is_in_the_pool(self):
        """All three carry a hedge token *and* an organism-specific term."""
        for number in (1, 2, 3):
            with self.subTest(case=number):
                text = case(self.HEDGED_DX, number)
                self.assertTrue(cc.has_hedge(text))
                self.assertTrue(cc.has_organism_specific(text))

    def test_the_three_hedges_the_set_was_built_on(self):
        self.assertTrue(cc.has_hedge("dx CAP likely mycoplasma"))
        self.assertTrue(cc.has_hedge("right tib/fib r/o osteomyelitis"))
        self.assertTrue(cc.has_hedge("dx: URI vs mycoplasma"))

    def test_a_bare_mycoplasma_line_is_in_the_pool(self):
        """The regression. ``mycoplasma`` was absent from the first list.

        Every other spelling in this suite carries a second matching token --
        ``mycoplasma pneumonia`` matches on ``pneumon``, and both real cases
        match on a ``strep`` elsewhere in the encounter -- so the omission was
        invisible from the set's own membership. This line has neither.
        """
        self.assertTrue(cc.has_organism_specific("dx CAP likely mycoplasma"))
        self.assertTrue(cc.has_organism_specific("URI vs mycoplasma"))

    def test_organisms_and_named_diseases(self):
        for text in ("likely mycoplasma pneumonia", "r/o osteomyelitis",
                     "poss strep", "flu a+", "influenza b", "covid contact",
                     "r/o dvt", "susp cellulitis", "monospot sent"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_organism_specific(text))

    def test_flu_does_not_hide_inside_ordinary_words(self):
        """``\\bflu\\b`` and not ``\\bflu``, on OBESITY's lesson.

        ``fluid``, ``flush`` and ``fluticasone`` are all live in this corpus and
        none of them is an organism.
        """
        for text in ("po fluids", "flush the line", "fluticasone 50 mcg"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_organism_specific(text))

    def test_mono_does_not_match_monotherapy(self):
        self.assertFalse(cc.has_organism_specific("continue monotherapy"))
        self.assertTrue(cc.has_organism_specific("r/o mono"))

    def test_h_pylori_takes_the_form_it_is_actually_written_in(self):
        """The repair. It shipped as a bare ``h pylori`` and matched nothing real.

        ``c diff`` was rejected one bullet above for exactly this shape, and this
        alternative was carried with it anyway. ``H. pylori`` is the dominant
        written form; before the fix it did not match, so the entry was inert
        against the only spelling that matters.
        """
        for text in ("H. pylori", "h. pylori", "h pylori", "hpylori"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_organism_specific(text))

    def test_factor_v_does_not_swallow_the_other_clotting_factors(self):
        """The second repair, and it is OBESITY's lesson in one alternative.

        ``factor v`` without a trailing boundary matches ``factor vii`` and
        ``factor viii`` -- ordinary coagulation panel entries, not the
        hereditary thrombophilia the entry is for.
        """
        self.assertTrue(cc.has_organism_specific("r/o factor v leiden"))
        self.assertFalse(cc.has_organism_specific("factor vii deficiency"))
        self.assertFalse(cc.has_organism_specific("factor viii 82%"))

    def test_the_four_rejected_tokens_stay_rejected(self):
        """Each was in a draft and each was dropped for an ambiguity.

        ``PE`` is physical exam here as often as pulmonary embolism, ``CA`` is
        calcium on a lab panel as well as cancer in a family history, ``BV``
        appears in a history line more than in a hedge, and ``c diff`` spells
        three ways the boundary handles badly. ``ORGANISM_SPECIFIC`` records the
        reasoning; this pins the behavior.
        """
        for text in ("PE: lungs clear", "CA 9.1, Mg 1.8", "hx: bv",
                     "c diff negative"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_organism_specific(text))

    def test_a_plain_encounter_is_not_in_the_pool(self):
        self.assertFalse(cc.has_organism_specific("cc: rash\ndx contact dermatitis"))

    def test_the_survey_counts_the_pool_as_a_subset_of_the_hedges(self):
        """The pool can never exceed the hedge count, and it is not equal to it."""
        c = cc.survey(
            [
                "dx CAP likely mycoplasma",              # hedged, organism
                "r/o osteomyelitis",                     # hedged, named disease
                "likely due to being out of alignment",  # hedged, neither
                "dx strep pharyngitis",                  # organism, not hedged
                "cc: rash\ndx contact dermatitis",       # neither
            ]
        )
        self.assertEqual(c.with_hedge, 3)
        self.assertEqual(c.hedge_with_organism, 2)


class RestatedDurationPool(unittest.TestCase):
    """Guards the pool ``fixtures/duration-span`` says it drew from.

    Same arrangement as ``OrganismSpecificPool`` and for the same reason. That
    set is a **pick, not a population** -- three encounters out of the pool this
    prints, chosen by reading them -- because the distinction drift row 16 turns
    on is *whether two durations are about the same symptom*, and no regex makes
    it. So the pool over-counts by construction and the honest defense is that
    anyone can re-derive what it picked from.

    The over-counting is not a caveat here, it is a property with a worked
    example: day-b's cases 8 and 9 are the **attribution** limb, where the two
    durations belong to two different symptoms and there is no conflict at all.
    Both are in this pool and neither is what ``fixtures/duration-span`` was
    built on. A filter that excluded them would be one reverse-engineered to
    return the pick, which ``fixtures/README.md`` refuses outright.

    Nothing here runs against ``scratch/``: the committed inputs are the worked
    examples and the decoys are literals. Issue #65.
    """

    DURATION_SPAN = REPO_ROOT / "fixtures" / "duration-span" / "shorthand"

    def test_every_duration_span_case_is_in_the_pool(self):
        for number in (1, 2, 3):
            with self.subTest(case=number):
                self.assertTrue(
                    cc.restates_a_duration(case(self.DURATION_SPAN, number))
                )

    def test_day_b_s_attribution_cases_are_in_the_pool_too(self):
        """The pool cannot tell the span limb from the attribution limb.

        Cases 8 and 9 date a *different* symptom -- day-b's B10 -- so there is
        no conflict in either and no span to write. This is the over-count
        stated as a test rather than as a sentence.
        """
        for number in (8, 9):
            with self.subTest(case=number):
                self.assertTrue(cc.restates_a_duration(case(DAY_B, number)))

    def test_day_b_s_two_agreeing_cases_are_out_of_the_pool_for_different_reasons(self):
        """Both are correctly out, and only one of them is out by design.

        Case 4 writes ``x 5 days`` three times, so there are no two *different*
        durations and the value rule excludes it. **Case 12 writes ``started
        saturday`` and then ``states started saturdy``** -- one timeline and a
        typo -- and those are two different strings, so the value rule does not
        exclude it. It is out because no symptom sits within the window of the
        second one. Move a symptom word next to that typo and the pool admits an
        encounter that agrees with itself.

        The filter cannot spell-normalize, and this is the one place in the
        corpus where that shows. Recorded rather than repaired: normalizing
        would be guessing which of two spellings was meant, and
        ``fixtures/duration-span`` reads its pool anyway.
        """
        for number in (4, 12):
            with self.subTest(case=number):
                self.assertFalse(cc.restates_a_duration(case(DAY_B, number)))

        values = {text for text, _ in cc.duration_mentions(case(DAY_B, 4))}
        self.assertEqual(values, {"x 5 days"})

        twelve = cc.duration_mentions(case(DAY_B, 12))
        self.assertEqual(len({text for text, _ in twelve}), 2)
        self.assertEqual(twelve[1][1], frozenset())

    def test_one_duration_is_not_a_restatement(self):
        self.assertFalse(
            cc.restates_a_duration("cc: cough, congestion x 3 days\nexam: TMs wnl")
        )

    def test_a_duration_with_no_symptom_near_it_does_not_pair(self):
        """The window is what makes this a *symptom* pool rather than a date one.

        **The precondition is asserted rather than assumed**, and the first
        version of this test is why. It used ``smokes 1 ppd x 20 years`` against
        ``chole 3 years ago``, and ``DURATION`` matches no year-scale unit at
        all -- so the note yielded **zero** duration mentions and the assertion
        held because the regex had seen nothing. A test that passes for want of
        input is the failure ``tools/test_icd10.py`` refuses by never running
        against the shipped database, one layer down.
        """
        note = (
            "cc: cough x 2 days\n"
            "hx: tonsillectomy, appendectomy, cholecystectomy, hysterectomy 3 months ago"
        )
        mentions = cc.duration_mentions(note)
        self.assertEqual(
            mentions, [("x 2 days", frozenset({"cough"})), ("3 months", frozenset())]
        )
        self.assertFalse(cc.restates_a_duration(note))

    def test_the_year_scale_is_outside_the_pool_entirely(self):
        """A deliberate scope, and the cost is named in ``DURATION``.

        Nothing in the corpus writes an acute onset in years, and a year-scale
        interval there is a smoking history, a surgery or a chronic condition.
        Admitting the unit would widen the published figure to buy those. What
        it costs is real and is not nothing: a chronic pain dated two ways in
        years is a same-symptom conflict this pool cannot see.
        """
        self.assertEqual(cc.duration_mentions("chronic back pain x 15 years"), [])
        self.assertEqual(cc.duration_mentions("11-12 yrs ago"), [])

    def test_the_same_duration_written_twice_is_not_a_restatement(self):
        """Two mentions of one value are one timeline, however often it is written."""
        self.assertFalse(
            cc.restates_a_duration("cc: cough x 2 days\nexam: cough x 2 days")
        )

    def test_a_treatment_sig_beside_the_symptom_it_treats_counts(self):
        """A named over-count, kept rather than filtered.

        ``zithromax ... x 3 days`` sits within the window of the cough it
        treats, so an encounter whose only second duration is a sig lands in the
        pool. Excluding it would need the filter to know a sig from a history,
        which is the same judgment row 16 itself needs and the same one this
        pool does not claim to make.
        """
        self.assertTrue(
            cc.restates_a_duration(
                "cc: fever, cough, congestion starting 5 days ago\n"
                "plan zithromax 7.5 mL qd x 3 days albuterol q4h cough"
            )
        )

    def test_the_survey_counts_the_pool(self):
        c = cc.survey(
            [
                "cc: cough x 2 days\nexam: cough started yesterday",   # in
                "cc: cough, congestion x 3 days\nexam: TMs wnl",       # one duration
                "hx: smokes 1 ppd x 20 years. chole 3 years ago",      # no symptom
            ]
        )
        self.assertEqual(c.restating_a_duration, 1)


class DurationSpanIsTheSameSymptomSet(unittest.TestCase):
    """Guards the properties of the *inputs* ``fixtures/duration-span`` rests on.

    ``DayBIsTheAbsenceSet``'s job, on a set whose whole subject is four strings.
    S1 asks that both stated values reach the note as the endpoints of a span,
    and S3 asks that the one restatement which **agrees** is not spanned. Repair
    any of these in the inputs and every row above it passes with nothing tested.

    Issue #65.
    """

    DURATION_SPAN = REPO_ROOT / "fixtures" / "duration-span" / "shorthand"

    # The two durations each case states for one symptom, and for case 3 the
    # pair that agrees. fixtures/duration-span/assertions.md states these in
    # prose; they are here so a change has to be made in both places on purpose.
    CONFLICTS = {
        1: ("x 2 days", "started yesterday"),
        2: ("x 2 days", "started yesterday"),
        3: ("x 3 days", "started 2 days ago"),
    }
    AGREES = ("x 4 days", "started 4 days ago")

    def test_the_set_has_three_cases(self):
        self.assertEqual(len(sorted(self.DURATION_SPAN.glob("case-*.md"))), 3)

    def test_every_case_is_exactly_one_note(self):
        for number in (1, 2, 3):
            with self.subTest(case=number):
                text = case(self.DURATION_SPAN, number)
                self.assertEqual(len(cc.split_notes(text)), 1)

    def test_every_case_states_both_durations_it_is_scored_on(self):
        for number, (first, second) in self.CONFLICTS.items():
            with self.subTest(case=number):
                text = case(self.DURATION_SPAN, number).lower()
                self.assertIn(first, text)
                self.assertIn(second, text)

    def test_case_three_also_carries_the_pair_that_agrees(self):
        """S3's whole subject. Lose it and a run that spans everything passes."""
        text = case(self.DURATION_SPAN, 3).lower()
        for token in self.AGREES:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_every_case_states_an_age(self):
        """No case may quietly become a missing-age test. fixtures/README."""
        for number in (1, 2, 3):
            with self.subTest(case=number):
                self.assertTrue(cc.has_stated_age(case(self.DURATION_SPAN, number)))

    def test_no_case_carries_a_date_of_birth(self):
        for number in (1, 2, 3):
            with self.subTest(case=number):
                self.assertFalse(cc.has_dob(case(self.DURATION_SPAN, number)))

    def test_case_two_s_onset_statement_is_a_bare_pronoun(self):
        """S1's inference limb. ``this all started yesterday`` names no symptom.

        Drift row 16 routes a pronoun with no new-or-worse marker to the whole
        illness, which is what makes case 2 a conflict rather than an
        attribution. Rewrite it to name the symptom and the case becomes case 1.
        """
        text = case(self.DURATION_SPAN, 2).lower()
        self.assertIn("this all started yesterday", text)
        for marker in ("now also", "new", "worsening", "worse today"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, text.split("this all started")[0])


class Age(unittest.TestCase):
    def test_years_spelled_out(self):
        self.assertTrue(cc.has_stated_age("48 year old F"))

    def test_yo_abbreviation(self):
        self.assertTrue(cc.has_stated_age("60 yo F"))
        self.assertTrue(cc.has_stated_age("44 y/o female"))

    def test_years_of_age(self):
        self.assertTrue(cc.has_stated_age("[PT] is 54 years of age"))

    def test_bare_age_and_sex_on_its_own_line(self):
        self.assertTrue(cc.has_stated_age("[PT]\n51 f\ncc: dysuria"))
        self.assertTrue(cc.has_stated_age("[PT]\n48f\ncc: dysuria"))
        self.assertTrue(cc.has_stated_age("61F\n"))

    def test_yo_run_together_with_the_sex_letter(self):
        # The form that broke HEIGHT, in the age extractor: "45yof" welds the
        # value, the token and the sex letter, so the trailing \b after "o"
        # cannot match. One note in the corpus writes it. That note is counted
        # today only because the token happens to sit alone on its own line and
        # AGE_AND_SEX_LINE rescues it -- move it into a sentence and the age
        # disappears, which is the silent failure this file exists to prevent.
        self.assertTrue(cc.has_stated_age("[PT] presents, 45yof c/o dysuria x 2 days"))
        self.assertTrue(cc.has_stated_age("[PT] presents, 45y/om c/o cough"))

    def test_the_welded_form_has_no_decoy_the_older_rule_misses(self):
        """Stated rather than asserted, because the obvious decoy is vacuous.

        The tempting test for the ``[mf]`` guard is "hold 3 your own meds" --
        and it does not exercise the guard at all. The pre-existing
        ``y\\.?o\\.?\\b`` alternative already rejects it, so the assertion
        passes identically with the guard deleted. Writing it as an assert
        would name a finding it never checks, which is the ADR 0001 failure
        mode. The guard earns its place by argument, not by this test:
        without it the alternative would end in nothing at all.
        """
        self.assertFalse(cc.has_stated_age("hold 3 your own meds"))  # by the older rule

    def test_a_follow_up_token_is_not_an_age(self):
        # "f/u" puts an "f" directly after a number, and audited 2026-08-11 it is
        # the commonest of the three digit+sex shapes in the corpus that sit
        # anywhere but alone on a line -- the form AGE_AND_SEX_LINE's line anchor
        # most has to reject. Unanchor that rule and every "augmentin 500 f/u"
        # becomes a 500-year-old.
        self.assertFalse(cc.has_stated_age("plan augmentin 500 f/u prn"))
        self.assertFalse(cc.has_stated_age("wbc 12 f/u in 2 weeks"))

    def test_pediatric_months(self):
        self.assertTrue(cc.has_stated_age("[PT]\n8 months old\nhr 130"))
        self.assertTrue(cc.has_stated_age("[PT]\n13 month male\nBp 164"))

    def test_a_temperature_is_not_an_age(self):
        # "t 98 F" would read as a 98-year-old under an unanchored digit+sex rule.
        self.assertFalse(cc.has_stated_age("bp 120/86 hr 97 t 98 F rr 20"))

    def test_a_dose_is_not_an_age(self):
        self.assertFalse(cc.has_stated_age("plan toradol 10 mg IM"))
        self.assertFalse(cc.has_stated_age("plan augmentin 875 for 10 days"))

    def test_gestational_age_is_not_patient_age(self):
        self.assertFalse(cc.has_stated_age("[PT]\n8 weeks g1p0a0\nbp 131/84"))

    def test_fixtures(self):
        self.assertTrue(cc.has_stated_age(fixture("case-01.md")))
        self.assertTrue(cc.has_stated_age(fixture("case-03.md")))


class TheAnchorReportsWhatItCouldCost(unittest.TestCase):
    """Issue #64. The line anchor's cost, measured rather than asserted.

    ``AGE_AND_SEX_LINE`` carried a dated prose audit claiming its anchors cost
    no encounter its age. The audit was right -- read by hand 2026-08-15, all
    three were decoys -- and **it was also unreproducible**, which is ADR 0001's
    objection landing the other way: four readings of "a digit+sex match" gave
    38, 36, 36 and 2, and the number the comment stated was none of them. A
    correct claim nobody can re-derive is indistinguishable from a wrong one.

    So the number is printed now instead of remembered. These tests pin what it
    counts, because a ceiling that quietly stopped counting something would look
    exactly like a corpus that had stopped containing it -- issue #56's failure,
    which is what put this ticket's priority up.
    """

    def test_a_decoy_still_counts_toward_the_ceiling(self):
        """The whole point of a ceiling: it over-reports and never misses.

        Every one of these is a decoy and every one is counted. Reading them is
        what says so, and reading them is PHI -- so the printed figure has to be
        the thing a human can *check*, not the thing that has already been
        judged.

        **These are not an inventory of the corpus's three.** That inventory is
        stated once, in ``AGE_AND_SEX_OFF_LINE``'s comment, and restating it
        here is how a first draft of this change ended up shipping three
        descriptions of the same three encounters that disagreed with each
        other. Two of the shapes below are shapes the read found; the
        Fahrenheit temperature is **synthetic**, carried because it is the form
        the anchor most has to reject, and because the class above already pins
        the other side of that same question.

        **Every value below is invented**, per this file's pragma.
        """
        for decoy in (
            "plan augmentin 875 f/u prn",
            "bp 120/86 hr 97 t 98 F rr 20",
            "was here 6-22 f/u pulmonary",
        ):
            with self.subTest(decoy=decoy):
                self.assertTrue(cc.could_have_lost_an_age_to_the_anchor(decoy))

    def test_an_ordinary_mg_dose_is_not_even_a_candidate(self):
        """And the corpus's one dose decoy is only a candidate by a typo.

        ``\\b`` after the sex letter cannot match against the "g" of "mg", so a
        correctly written dose never reaches the ceiling at all. The corpus's
        two dose candidates are a mistyped milligram abbreviation and an
        antibiotic strength written bare before an ``f/u``.

        Worth pinning because it cuts the other way from everything else here:
        the ceiling over-reports on temperatures and follow-ups and **under**-
        reports on doses, so it is a bound on ages rather than a tally of
        digit+sex shapes. A future edit widening the letter class to catch "mg"
        would raise the printed figure without a single age having moved.
        """
        self.assertFalse(cc.could_have_lost_an_age_to_the_anchor("plan toradol 10 mg IM"))
        self.assertTrue(cc.could_have_lost_an_age_to_the_anchor("plan toradol 10 m, IM"))

    def test_a_real_off_line_age_counts(self):
        # The failure the ceiling exists to make visible: the corpus's own
        # "51 f" form, written into a sentence instead of onto a line of its
        # own. ``has_stated_age`` cannot see it, and this can.
        note = "[PT] presents, 51 f c/o dysuria x 2 days"
        self.assertFalse(cc.has_stated_age(note))
        self.assertTrue(cc.could_have_lost_an_age_to_the_anchor(note))

    def test_a_note_that_states_an_age_is_never_counted(self):
        """Nothing was lost, so nothing is at risk -- however many decoys follow.

        This is what keeps the ceiling from drifting into a count of ``f/u``
        tokens. 24 encounters carry an off-line digit+sex form; 3 of them state
        no age. Only the second number bounds anything.
        """
        note = "[PT]\n51 f\nplan augmentin 875 f/u prn, toradol 10 mg IM"
        self.assertTrue(cc.has_stated_age(note))
        self.assertFalse(cc.could_have_lost_an_age_to_the_anchor(note))

    def test_the_digit_and_the_sex_letter_must_share_a_line(self):
        """Ruled by the clinician 2026-08-15, and it is not a tidy.

        A date of birth in this corpus is always a month, a day and a year, so
        the trailing two-digit year is a date component and can never be an age
        -- and the "f" that follows it across the line break belongs to
        ``f/u``. Allowing whitespace to span the newline pairs them and prints
        a fourth encounter that lost nothing, because its age was never on a
        line for the anchor to reject in the first place.

        Refusing it is also what makes the 2026-08-11 audit reproduce exactly:
        three, and the same three it described.

        **The date below is invented**, per this file's pragma. One real
        encounter has this shape and its value is not reproduced here or in
        ``corpus_census.py`` -- ``phi_scan`` refused the first draft of this
        test for carrying the real one, which is the corpus layer doing its job
        against the very session that read the note.
        """
        note = "dob 3-04-88\nf/u for being in the hospital"
        self.assertFalse(cc.has_stated_age(note))
        self.assertFalse(cc.could_have_lost_an_age_to_the_anchor(note))

    def test_a_spelled_sex_word_is_the_ceiling_s_own_blind_spot(self):
        """Pinned as a known gap, because a ceiling has to say what it cannot see.

        ``[mf]\\b`` cannot match "female" -- the boundary fails against the "e"
        -- so ``51 female`` is invisible to ``has_stated_age`` **and** to the
        ceiling published as bounding what ``has_stated_age`` costs. It is zero
        in the corpus today in all three orderings, measured 2026-08-15, and
        zero is not the same as covered.

        Asserted rather than left implicit so that widening ``[mf]`` fails here
        and sends whoever does it to ``AGE_AND_SEX_OFF_LINE``'s comment, where
        the rule is ``HEDGE``'s: widen deliberately, re-run against the corpus,
        update every figure that cites it. The gap is narrow because
        ``AGE_IN_YEARS`` rescues ``51 yo female`` and ``AGE_UNDER_ONE`` rescues
        ``13 month female``; it is the bare number-plus-spelled-word that falls
        through.
        """
        for form in ("51 female", "48 male", "51female"):
            with self.subTest(form=form):
                self.assertFalse(cc.has_stated_age(form))
                self.assertFalse(cc.could_have_lost_an_age_to_the_anchor(form))
        for rescued in ("51 yo female", "13 month female"):
            with self.subTest(rescued=rescued):
                self.assertTrue(cc.has_stated_age(rescued))

    def test_no_digit_sex_form_at_all_is_not_a_ceiling(self):
        self.assertFalse(cc.could_have_lost_an_age_to_the_anchor("cc: cough x 3 days"))

    def test_the_ceiling_counts_through_survey_and_not_only_in_isolation(self):
        """The coverage assertion, in the form issue #64's own comment asked for.

        **Built from synthetic notes rather than run over the fixtures**, and
        that is the whole point. Every committed set gives
        ``no_age_with_off_line_form = 0`` -- day-a lands 0 of 1, and day-b,
        peds-bp, hedged-dx and obesity-bmi all land 0 of 0 -- so a fixture-based
        assertion is ``0 <= 1`` and passes identically with the function
        hardwired to return False. That is ADR 0001's failure exactly, and the
        first draft of this test shipped it.

        The four notes below are one of each kind, so the counter has to
        discriminate rather than merely stay small: an age stated plainly, an
        age stated plainly *beside* a decoy, no age and a decoy, and no age and
        nothing.
        """
        notes = [
            "Note 1\n44 f\ncc: dysuria",                          # age, no decoy
            "Note 2\n44 f\nplan augmentin 875 f/u prn",           # age *and* a decoy
            "Note 3\ndob 3-04-88\nplan augmentin 875 f/u prn",    # no age, a decoy
            "Note 4\ndob 3-04-88\ncc: cough",                     # no age, no decoy
        ]
        c = cc.survey(notes)
        self.assertEqual(c.notes, 4)
        self.assertEqual(c.with_stated_age, 2)
        self.assertEqual(c.without_stated_age, 2)
        # Note 3 only. Note 2 carries the same decoy and states its age, so it
        # is not at risk; note 4 states no age and has no candidate.
        self.assertEqual(c.no_age_with_off_line_form, 1)
        self.assertLessEqual(c.no_age_with_off_line_form, c.without_stated_age)

    def test_the_report_prints_the_ceiling_over_the_population_it_bounds(self):
        """#56's ``matched 6 of 12`` shape, which is what the comment asked for.

        A bare count of what an extractor *found* is uncheckable; a count
        against the population it was looking through is not. So the ratio has
        to reach the printed report, not merely exist on the dataclass.
        """
        notes = [
            "Note 1\n44 f\ncc: dysuria",
            "Note 2\ndob 3-04-88\nplan augmentin 875 f/u prn",
        ]
        report = cc.format_report(
            cc.survey(notes), source="synthetic", date="2026-08-15",
            bands=cc.survey_bands(notes),
            files=cc.FileCensus(
                files=1, unique_files=1, with_no_stated_age=0,
                with_age_in_every_note=0, with_mixed_age=1,
            ),
        )
        self.assertIn("no age stated             1", report)
        self.assertIn("off-line form in       1", report)

    def test_the_ceiling_matches_every_shape_the_anchor_does(self):
        """The two patterns are hand-copied, so something has to pin them.

        ``AGE_AND_SEX_OFF_LINE`` is ``AGE_AND_SEX_LINE``'s body with the anchors
        removed and ``\\s`` narrowed to ``[ \\t]``. Nothing in the language ties
        them together, so widening the anchored form -- a welded ``45yof``
        alternative, say -- would leave the ceiling silently no longer bounding
        it, and the printed figure would stay plausible while measuring the
        wrong pattern.

        Asserted as an implication rather than string equality, because the two
        bodies are deliberately not identical: anything the anchor accepts on a
        line of its own, the ceiling must accept inline.
        """
        for form in ("51 f", "48f", "61F", "45 yo m", "7 y/o F", "103 M"):
            with self.subTest(form=form):
                self.assertTrue(cc.AGE_AND_SEX_LINE.search(f"cc: cough\n{form}\nhx: none"))
                self.assertTrue(cc.AGE_AND_SEX_OFF_LINE.search(f"pt is {form} and here"))

    def test_the_ceiling_is_not_wired_into_the_age_extractors(self):
        """A ceiling that changed the figures would be a fix, not a measurement.

        ``AGE_AND_SEX_OFF_LINE`` exists to measure ``AGE_AND_SEX_LINE``, and the
        moment ``has_stated_age`` consults it the two stop being independent --
        which is the exact self-audit ADR 0001 refuses. Asserted here because
        wiring it in is a one-line change that no other test would fail on.

        **Both directions are pinned.** The second is what
        ``could_have_lost_an_age_to_the_anchor`` silently depends on: it does no
        span bookkeeping, and it is entitled not to only because a false
        ``has_stated_age`` guarantees ``AGE_AND_SEX_LINE`` matched nothing in
        that note. Drop that alternative from ``has_stated_age`` and the ceiling
        starts counting forms the anchor accepted, while still printing a
        plausible number.

        Read with ``ast`` rather than by slicing to the next ``def``, which the
        first draft did and which would have broken the moment either function
        became the last in the file.
        """
        bodies = {
            node.name: ast.unparse(node)
            for node in ast.parse(Path(cc.__file__).read_text(encoding="utf-8")).body
            if isinstance(node, ast.FunctionDef)
        }
        for name in ("has_stated_age", "age_in_years"):
            self.assertIn(name, bodies)
            with self.subTest(function=name, direction="the ceiling stays out"):
                self.assertNotIn("AGE_AND_SEX_OFF_LINE", bodies[name])
            with self.subTest(function=name, direction="the anchor stays in"):
                self.assertIn("AGE_AND_SEX_LINE", bodies[name])


class DateOfBirth(unittest.TestCase):
    """Every date here is synthetic. The shapes are real; the values are not."""

    def test_token_with_slashes(self):
        self.assertTrue(cc.has_dob("dob 03/04/1990"))

    def test_token_with_dashes_and_two_digit_year(self):
        self.assertTrue(cc.has_dob("dob 7-8-91"))
        self.assertTrue(cc.has_dob("DOB 10-11-01"))

    def test_bare_date_alone_on_a_line(self):
        self.assertTrue(cc.has_dob("[PT]\nHR 132 t 97.3\n3/04/2020\nVaccs utd"))

    def test_an_lmp_is_not_a_birth_date(self):
        self.assertFalse(cc.has_dob("ht 5'6\" wt 110 8/10 pain. lmp 5-06-2020"))

    def test_a_visit_date_header_is_not_a_birth_date(self):
        self.assertFalse(cc.has_dob("Date: 5-06-20\ncc: cough"))


class DayBIsTheAbsenceSet(unittest.TestCase):
    """Guards the property every day-b assertion rests on."""

    def test_the_set_has_twelve_cases(self):
        self.assertEqual(len(sorted(DAY_B.glob("case-*.md"))), 12)

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_nine_cases_carry_no_vital_at_all(self):
        for n in DAY_B_NO_VITAL:
            with self.subTest(case=n):
                self.assertFalse(cc.has_any_vital(day_b(n)))

    def test_the_three_controls_carry_a_full_vital_line(self):
        for n in DAY_B_CONTROL:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertTrue(cc.has_bp(note))
                self.assertTrue(cc.has_weight(note))
                self.assertTrue(cc.has_other_vitals(note))

    def test_only_two_controls_carry_an_unambiguous_height(self):
        """Case 2's height is a preserved typo, and this test must not hide it.

        Case 2 reads ``wt 62in wt 131`` -- ``wt`` written where ``ht`` was meant.
        ``has_height`` returns True for it, but only via the bare ``62in`` form,
        not via a height token, so asserting it beside cases 3 and 4 would make
        the *input* look tidier than it is.

        What the reference read settled (2026-08-11) is the clinical question --
        62 is a height, so day-b's B4 now covers case 2. It did not settle the
        extraction question this test guards: the shorthand still carries no
        height token, and an extractor that only looked for one would miss it.
        """
        for n in (3, 4):
            with self.subTest(case=n, form="ht token"):
                self.assertRegex(day_b(n), r"(?i)\bht\s*\d|\bht\b")
        self.assertNotRegex(day_b(2), r"(?i)\bht\b")
        self.assertTrue(cc.has_height(day_b(2)))  # by "62in" alone

    def test_the_split_is_the_whole_set(self):
        self.assertEqual(sorted(DAY_B_NO_VITAL + DAY_B_CONTROL), list(range(1, 13)))

    def test_the_b1_anchors_document_hypertension_and_no_pressure(self):
        """B1 is only checkable where the history says htn and no BP was taken."""
        for n in DAY_B_HYPERTENSIVE:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertIn("htn", note.lower())
                self.assertFalse(cc.has_bp(note))

    def test_every_case_states_an_age(self):
        """No day-b row is about a missing age; day-a case 10 already covers that."""
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertTrue(cc.has_stated_age(path.read_text(encoding="utf-8")))

    def test_no_case_carries_a_date_of_birth(self):
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertFalse(cc.has_dob(path.read_text(encoding="utf-8")))

    def test_the_d6_anchor_documents_a_contact_and_orders_no_test(self):
        """D6 is only checkable while case 9's plan stays empty of testing.

        The row asks the skill to order COVID-19, influenza and strep swabs from
        a documented positive contact ([issue #32]). Writing any of those into
        the input would make it a *given* order, and the row would pass having
        tested nothing -- the same way a vital added to one of the nine would
        void B1. The exposure itself is asserted rather than assumed for the
        opposite reason: remove it and the row fails a correct note.

        [issue #32]: https://github.com/mshamblin5150-code/clinical-skills/issues/32
        """
        self.assertIn("postive for covid", day_b(9).lower())  # typo preserved
        for token in ("covid", "flu", "strep", "swab", "rsv"):
            with self.subTest(token=token):
                self.assertNotIn(token, day_b_plan(9))

    def test_the_two_contacts_he_did_swab_carry_the_order(self):
        """D6's prose claims swabbing a documented contact is his own practice.

        Cases 8 and 12 are where the same shift did it, and they are what makes
        case 9 a lapse rather than a house style. Asserted here so the claim
        breaks loudly if either input is edited.
        """
        self.assertIn("covid", day_b_plan(8))
        for token in ("covid", "strep", "flu"):
            with self.subTest(token=token):
                self.assertIn(token, day_b_plan(12))

    def test_the_d7_anchor_documents_a_lung_finding_and_orders_no_imaging(self):
        """D7 is only checkable while case 9's plan stays empty of imaging.

        The same shape as D6 one row up, and asserted for the same two opposite
        reasons. The finding is asserted because removing it would fail a
        correct note; the absent order is asserted because writing a film into
        the input would make it a *given* and the row would pass having tested
        nothing -- exactly how a vital added to one of the nine would void B1.

        [issue #27]: https://github.com/mshamblin5150-code/clinical-skills/issues/27
        """
        self.assertIn("lung sounds diminished", day_b(9).lower())
        for token in ("cxr", "xray", "x-ray", "radiograph", "film", "imaging"):
            with self.subTest(token=token):
                self.assertNotIn(token, day_b_plan(9))

    def test_the_film_he_did_order_is_on_the_same_shift(self):
        """D7's prose claims imaging a diminished lung base is his own practice.

        Case 7 is where this shift did it -- ``diminished in bases`` on exam and
        ``cxr`` in the plan -- which is what makes case 9 a lapse rather than a
        house style. It is also why case 7 cannot host the row itself: the order
        is a given there, so a run that merely copied the input would pass. Same
        reason case 10 is not a second D6.
        """
        self.assertIn("diminished in bases", day_b(7).lower())
        self.assertIn("cxr", day_b_plan(7))

    def test_the_three_lung_rows_sit_on_vital_less_cases(self):
        """B9's ground: D2, D3 and D7 are each open to a filled dismissal.

        All three cases are filled a complete vital set, so all three rows can
        be answered by naming the finding and disposing of it on two invented
        numbers. That is the cheat B9 closes, and it stops being the reason B9
        exists the moment any of these three acquires a vital line.
        """
        for n, finding in DAY_B_LUNG_FINDING.items():
            with self.subTest(case=n):
                note = day_b(n)
                self.assertIn(finding, note.lower())
                self.assertFalse(cc.has_any_vital(note))

    def test_b9_reaches_every_case_with_something_generated(self):
        """B9's list is a union, and case 3 is the member easy to lose.

        The row reaches any case where something in the filled-vitals license
        class was generated -- a vital, a body measurement, or the OLDCARTS
        severity. That is the vital-less nine *plus* case 3, whose vital line is
        complete and whose severity the run must invent. Derived from the inputs
        here rather than copied from B1's list, because the first draft of the
        row did copy B1 and dropped her.

        [issue #27]: https://github.com/mshamblin5150-code/clinical-skills/issues/27
        """
        reached = tuple(
            n
            for n in range(1, 13)
            if not cc.has_any_vital(day_b(n))
            or not (cc.has_pain_score(day_b(n)) or re.search(NO_PAIN, day_b(n)))
        )
        self.assertEqual(reached, DAY_B_B9)

    def test_the_two_cases_b9_does_not_reach_supply_both(self):
        """Cases 2 and 4 are outside B9, and the row is vacuous on them.

        Both carry a full vital line and both settle the severity in the
        shorthand, so a run has nothing generated to reason from and B9 has
        nothing to check. This is what makes the exclusion a property of the
        inputs rather than an oversight.

        **The two settle it differently**, and asserting a score on both would
        be wrong: case 4 writes ``5``, while case 2 writes ``no pain`` -- an
        absence, which is a given scoring 0/10 rather than a value to invent.
        ``DAY_B_NO_PAIN`` is the split, and the first version of this test
        failed on exactly that distinction.
        """
        for n in (2, 4):
            with self.subTest(case=n):
                note = day_b(n)
                self.assertTrue(cc.has_any_vital(note))
                self.assertTrue(cc.has_pain_score(note) or re.search(NO_PAIN, note))

    def test_seven_cases_transcribe_a_severity(self):
        """B7's list, with the value each case must survive with."""
        for n, score in DAY_B_PAIN_SCORE.items():
            with self.subTest(case=n):
                self.assertEqual(cc.pain_scores(day_b(n)), [score])

    def test_two_cases_write_the_absence_of_pain(self):
        """B7's other half, and it is a given rather than a silence.

        Cases 2 and 12 say "no pain" outright, so 0/10 there is transcribed and
        not the bland fill the rule forbids. A run that scores either of them
        above zero has invented a symptom, which standing rule 2 covers without
        any exception -- the severity license buys a number for a complaint the
        shorthand documents, not a complaint.
        """
        for n in DAY_B_NO_PAIN:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertRegex(note, NO_PAIN)
                self.assertFalse(cc.has_pain_score(note))

    def test_three_cases_leave_the_severity_to_be_filled(self):
        """No number written, and no absence written either.

        B5 and B6 reach all twelve, but these three are the only ones where the
        severity is *invented* rather than transcribed. Writing a score into any
        of them, or writing "no pain" into one, would start failing correct
        notes -- the same trap ``obesity-bmi``'s control guard exists for.
        """
        for n in DAY_B_SEVERITY_FILLED:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertFalse(cc.has_pain_score(note))
                self.assertNotRegex(note, NO_PAIN)

    def test_two_of_the_seven_scores_end_a_sentence(self):
        """The count day-b's prose quotes, computed rather than eyeballed.

        It is the count that justifies the narrowed trailing guard in
        ``PAIN_SCORE``. Written by hand it would have been the one figure in
        this set nothing recomputes -- and it was, until the review caught it.
        """
        sentence_final = [
            n for n in sorted(DAY_B_PAIN_SCORE) if re.search(r"/\s*10\s*\.", day_b(n))
        ]
        self.assertEqual(sentence_final, [5, 11])

    def test_b8_and_b14_partition_the_three_filled_severities(self):
        """Every invented severity is claimed by exactly one row, and by a row.

        This used to assert that B8 left case 3 out and that *nothing* picked
        her up, because whether a non-painful complaint scores 0/10 was a
        ruling nobody had made. Issue #42 made it -- she scores above zero and
        B14 is hers -- so the assertion changes shape rather than going away.
        The three cases still split two-and-one, and the split still has to be
        deliberate: B8's two are painful complaints where the run merely has to
        not write zero, and B14's one is a complaint that does not hurt, whose
        anchor sits in the exam. A future edit that folded them together would
        stop testing the difference the ruling turns on.
        """
        self.assertEqual(sorted(set(DAY_B_SEVERITY_PAINFUL) & set(DAY_B_B14)), [])
        self.assertEqual(
            sorted(set(DAY_B_SEVERITY_PAINFUL) | set(DAY_B_B14)),
            sorted(DAY_B_SEVERITY_FILLED),
        )

    def test_b14s_case_carries_a_pain_source_in_its_exam(self):
        """B14 demands a score above 0/10 from a complaint that does not hurt.

        What licenses that number is broken skin in the exam, so the strings
        are pinned here for the reason every other input in this file is: a
        tidy that dropped them would leave B14 demanding an abnormal with
        nothing behind it, and the row would go on passing.
        """
        for case in DAY_B_B14:
            exam = day_b_exam(case)
            for source in DAY_B_B14_PAIN_SOURCE:
                with self.subTest(case=case, source=source):
                    self.assertIn(source, exam)

    def test_the_severity_split_is_the_whole_set(self):
        self.assertEqual(
            sorted(tuple(DAY_B_PAIN_SCORE) + DAY_B_NO_PAIN + DAY_B_SEVERITY_FILLED),
            list(range(1, 13)),
        )

    def test_the_two_duration_anchors_state_a_timeline_twice(self):
        """B10's ground: a chief complaint duration and a later onset that differ.

        Both cases hang ``x 2 days`` off the end of a multi-symptom chief
        complaint and then date one symptom to yesterday. Remove either half of
        either case and B10 passes on a note that never attributed anything.
        """
        for n, timelines in DAY_B_TWO_TIMELINES.items():
            with self.subTest(case=n):
                self.assertIn(timelines.cc_duration, day_b_cc(n))
                self.assertIn(timelines.second_onset, day_b_exam(n))
                self.assertNotIn(timelines.second_onset, day_b_cc(n))

    def test_case_eight_names_the_symptom_its_second_onset_belongs_to(self):
        """B10's first limb: the onset line names its own symptom.

        ``right earache yesterday`` needs no referent resolved -- the duration
        is written next to the thing it describes, so attaching it is reading
        rather than inferring, and B11 does not reach this case. The earache is
        also what the shorthand's own ``right AOM`` rests on, so a run that
        folded it into the chief complaint's two days would misdate the
        diagnosis.
        """
        self.assertIn("earache", DAY_B_TWO_TIMELINES[8].second_onset)
        self.assertIn("right aom", day_b(8).lower())

    def test_case_nine_uses_a_pronoun_and_supplies_the_marker(self):
        """B11's ground, and it is two properties rather than one.

        The onset line names no symptom -- ``states this started yesterday`` --
        so the attribution rests entirely on ``pain inface is worse`` in the
        next clause. Delete the marker and the pronoun means the whole illness,
        which is a genuine conflict and a different rule; add a symptom name and
        the case stops testing B11 and becomes a second case 8.
        """
        onset = DAY_B_TWO_TIMELINES[9].second_onset
        self.assertIn("this started yesterday", onset)
        for symptom in ("pain", "sinus", "congestion", "cough", "sneeze"):
            with self.subTest(symptom=symptom):
                self.assertNotIn(symptom, onset)
        self.assertIn("pain inface is worse", day_b_exam(9))  # typo preserved

    def test_the_two_restating_cases_agree_and_are_not_rows(self):
        """Cases 4 and 12 restate a timeline and state the same one twice.

        They are why B10 sits on 8 and 9 rather than on every case that says a
        duration twice: a run that ignored the rule entirely would still write
        the right number here, so neither case can separate a run that
        attributed from one that copied. Asserted so an edit that made either
        disagree gets noticed as the new row it would be.

        Case 12's second statement carries the ``saturdy`` typo, which is why
        both halves are matched on a prefix rather than on the whole word.
        """
        for n, token in DAY_B_TIMELINES_AGREE.items():
            with self.subTest(case=n):
                self.assertIn(token, day_b_cc(n))
                self.assertIn(token, day_b_exam(n))

    def test_the_four_timeline_cases_are_the_whole_of_them(self):
        """B10's two and the two that agree do not overlap, and nothing else states one twice."""
        self.assertEqual(
            sorted(set(DAY_B_TWO_TIMELINES) | set(DAY_B_TIMELINES_AGREE)), [4, 8, 9, 12]
        )
        self.assertFalse(set(DAY_B_TWO_TIMELINES) & set(DAY_B_TIMELINES_AGREE))

    def test_the_span_form_is_the_clinicians_own(self):
        """`clinical-note` rests row 16's residual limb on this, so assert it.

        The rule says a same-symptom duration conflict is written as a span
        containing both endpoints, and argues that this is his idiom rather than
        a shape invented here. Case 11 is where day-b writes it -- twice, on two
        different scales -- and the claim breaks loudly if that input is edited.
        """
        case, spans = DAY_B_SPAN_IDIOM
        note = day_b(case).lower()
        for span in spans:
            with self.subTest(span=span):
                self.assertIn(span, note)


class Row15AndB9StateOneRule(unittest.TestCase):
    """Drift row 15 and ``fixtures/day-b`` B9 are one rule written twice.

    [#69](https://github.com/mshamblin5150-code/clinical-skills/issues/69) is what
    made this worth a test. The row shipped with an opening sentence -- *every
    reassurance in the note traces to a given* -- **broader than the method the
    row then gave for checking it**, which reaches only a decision not to act. Two
    clauses in day-b run 2 and one in run 3 sat in that gap, and which reading
    governed decided two recorded scores. **Ruled 2026-08-16: the method
    governs**, and the broad sentence is retired from both files.

    So the failure this guards is not a typo. It is one file being narrowed and
    the other left broad, which reads as agreement until someone grades a run
    against the wrong copy -- and the two copies live in different trees, cited by
    different readers, moved by different tickets.

    **A quotation is not a statement of the rule**, which is why this reads the
    table cell rather than the file. Both files argue about the retired sentence
    in prose below their tables, and must go on being able to: that is the record
    of what the ruling cost. ``spelling_scan``'s mention-versus-use distinction,
    arriving here for the same reason.

    Neither file is read for the *pain-score* limb or row 4's boundary -- those
    are #59's and settled separately, and a test that pinned the whole cell would
    fail on any later ruling rather than on a disagreement between the two.
    """

    #: Both tables head their rule column identically, which is what makes one
    #: extractor serve both -- ``| # | Test | Passes when |`` in the skill and
    #: ``| # | Cases | Passes when | Fails when | Reference did |`` here.
    #:
    #: **Resolved off the header rather than hard-coded**, and the difference is
    #: not stylistic. Two of the three tests below assert a string is *absent*,
    #: and a position that has quietly stopped pointing at the rule column makes
    #: an absence test pass by reading the wrong cell. Inserting a column ahead
    #: of *Passes when* in either table is an ordinary edit; it must fail here
    #: rather than turn the guard off.
    RULE_HEADING = "Passes when"

    #: The reading #69 retired. Kept as a string rather than described, because a
    #: test that looked for *some* broad sentence would pass against a reworded
    #: one.
    RETIRED = "Every reassurance in the note traces to a given"

    #: What both cells must now carry. The first is the method, promoted to being
    #: the rule; the second is the boundary the ruling bought, and without it the
    #: cells agree on what fails and say nothing about what passes.
    SHARED = (
        "No decision to withhold, defer or narrow the workup of a documented "
        "finding rests on a filled vital, body measurement or pain score",
        "A reassuring clause that changes no action is not a discharge",
    )

    def rule_cell(self, path: Path, row_label: str) -> str:
        """Return the *Passes when* cell of the table row labeled ``row_label``.

        The label is matched against the first cell whole, not by substring:
        ``B9`` would otherwise match nothing here, but ``1`` in the drift table
        would match rows 1, 10 through 19 and 21 and silently grade the wrong
        one.

        The column is taken from the nearest preceding header rather than by
        position, and the header is re-read at every table -- both files carry
        several, and one shared index across all of them is the same guess in a
        cheaper disguise.
        """
        column = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if self.RULE_HEADING in cells:
                column = cells.index(self.RULE_HEADING)
                continue
            if cells and cells[0] == row_label:
                self.assertIsNotNone(
                    column,
                    f"{path.name} row {row_label} sits under no "
                    f"{self.RULE_HEADING!r} header",
                )
                self.assertGreater(
                    len(cells),
                    column,
                    f"{path.name} row {row_label} has no rule column",
                )
                return cells[column]
        self.fail(f"{path.name} carries no table row labeled {row_label}")

    def rows(self):
        return (
            ("drift row 15", REPO_ROOT / "skills" / "clinical-note" / "SKILL.md", "15"),
            ("day-b B9", REPO_ROOT / "fixtures" / "day-b" / "assertions.md", "B9"),
        )

    def test_neither_row_still_states_the_retired_reading(self):
        """The sentence #69 was filed over is gone from both rule cells.

        Failing this from one side is the whole point: a pass that narrowed the
        skill and left the fixture broad would leave the set grading runs by a
        rule the skill no longer states.
        """
        for name, path, label in self.rows():
            with self.subTest(row=name):
                self.assertNotIn(self.RETIRED, self.rule_cell(path, label))

    def test_both_rows_state_the_ruling(self):
        """Both cells carry the method and the boundary, word for word.

        Word for word rather than in substance, because *in substance* is what
        two files drifting apart always look like on the day they part.
        """
        for name, path, label in self.rows():
            cell = self.rule_cell(path, label)
            for clause in self.SHARED:
                with self.subTest(row=name, clause=clause[:40]):
                    self.assertIn(clause, cell)

    def test_the_retired_reading_survives_as_prose_in_both_files(self):
        """The record of what was retired is not deleted along with the rule.

        This runs the other way from the two above and is the reason they read a
        cell rather than a file. #69 turned on a real ambiguity that produced
        real findings across two runs; a later reader who cannot see the sentence
        that was rejected cannot tell a settled question from one nobody asked.
        """
        for name, path, _ in self.rows():
            with self.subTest(row=name):
                self.assertIn(self.RETIRED, path.read_text(encoding="utf-8"))


class AgeInYears(unittest.TestCase):
    """The value extractor, as opposed to ``has_stated_age``'s presence check.

    Every decoy ``Age`` rejects must resolve to ``None`` here, not to a number:
    a presence check that over-matches inflates a percentage, but a value
    extractor that over-matches puts an encounter in the wrong age band, which
    is the thing issue #11's ruling turns on.
    """

    def test_years(self):
        self.assertEqual(cc.age_in_years("45 yo M"), 45)
        self.assertEqual(cc.age_in_years("a 7 years old male"), 7)
        self.assertEqual(cc.age_in_years("62 years of age"), 62)

    def test_bare_age_and_sex_on_its_own_line(self):
        self.assertEqual(cc.age_in_years("cc: cough\n51 f\nhx: none"), 51)

    def test_months_floor_to_zero(self):
        self.assertEqual(cc.age_in_years("9 months old M"), 0)
        self.assertEqual(cc.age_in_years("11 month old F"), 0)
        self.assertEqual(cc.age_in_years("3 week old female"), 0)

    def test_a_stated_year_beats_a_month_form_later_in_the_note(self):
        self.assertEqual(cc.age_in_years("2 yo M\ncough x 3 months old habit"), 2)

    def test_decoys_resolve_to_none(self):
        for decoy in (
            "t 98 F",              # a temperature on its own line
            "toradol 10 m",        # a dose
            "x 3 days f/u",        # the follow-up token taking the sex letter
            "32 weeks gestation",  # not the patient's age
            "no age anywhere",
        ):
            with self.subTest(decoy=decoy):
                self.assertIsNone(cc.age_in_years(decoy))

    def test_agrees_with_the_presence_check_on_every_committed_fixture(self):
        """The two must never disagree: one says there is an age, the other reads it."""
        for directory in (FIXTURES, DAY_B, PEDS_BP):
            for path in sorted(directory.glob("case-*.md")):
                note = path.read_text(encoding="utf-8")
                with self.subTest(case=f"{directory.name}/{path.name}"):
                    self.assertEqual(
                        cc.has_stated_age(note), cc.age_in_years(note) is not None
                    )

    def test_reads_the_day_b_adolescents(self):
        """Issue #11 turned on these two not being small children."""
        self.assertEqual(cc.age_in_years(day_b(6)), 17)
        self.assertEqual(cc.age_in_years(day_b(12)), 16)


class PedsBpIsTheSelectiveAbsenceSet(unittest.TestCase):
    """Guards the property every peds-bp assertion rests on.

    day-b's set is defined by encounters carrying *no* vital. This one is
    defined by the opposite shape -- a vital line that was written and is
    missing only the blood pressure -- and a well-meaning edit that added a
    pressure to case 3 or 5 would void the set rather than fail it.
    """

    def test_the_set_has_five_cases(self):
        self.assertEqual(len(sorted(PEDS_BP.glob("case-*.md"))), 5)

    def test_the_case_numbers_are_the_shifts_own(self):
        """Gaps in the numbering are the four school-age controls left out."""
        numbers = [int(p.stem.split("-")[1]) for p in sorted(PEDS_BP.glob("case-*.md"))]
        self.assertEqual(numbers, list(PEDS_BP_CASES))

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(PEDS_BP.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_no_case_carries_a_blood_pressure(self):
        for n in PEDS_BP_CASES:
            with self.subTest(case=n):
                self.assertFalse(cc.has_bp(peds_bp(n)))

    def test_every_case_is_under_six(self):
        for n in PEDS_BP_CASES:
            with self.subTest(case=n):
                age = cc.age_in_years(peds_bp(n))
                self.assertIsNotNone(age)
                self.assertLess(age, 6)

    def test_the_two_anchors_carry_a_vital_line_without_a_pressure(self):
        """Cases 3 and 5 are the inversion the set exists to test."""
        for n in PEDS_BP_VITAL_LINE:
            with self.subTest(case=n):
                note = peds_bp(n)
                self.assertTrue(cc.has_other_vitals(note))
                self.assertTrue(cc.has_weight(note))
                self.assertFalse(cc.has_bp(note))

    def test_case_three_carries_the_given_height_and_weight_percentiles(self):
        """P4 asserts these survive, and the anchor argument rests on them."""
        note = peds_bp(3)
        self.assertTrue(cc.has_height(note))
        self.assertIn("99.9th percentile", note)


class ObesityBmiIsTheDocumentedObesitySet(unittest.TestCase):
    """Guards the property every obesity-bmi assertion rests on.

    Two properties, and O2 needs both. The set's cases must carry **no body
    measurement**, so the BMI under test is wholly invented -- a weight alone
    would be enough to void it, because a given weight plus a filled height
    makes the arithmetic partly real. And the anchors must document obesity
    while the controls must not: fold those two groups together and the row
    loses the distinction between "a BMI below 30 contradicts a given" and "a
    BMI below 30 is exactly what a successful bypass looks like".
    """

    OBESITY_BMI = REPO_ROOT / "fixtures" / "obesity-bmi" / "shorthand"
    ANCHORS = (1, 2)      # the shorthand writes "obese" / "obesity"
    CONTROLS = (3, 4)     # a bariatric history, and no claim about today

    def case(self, number: int) -> str:
        return (self.OBESITY_BMI / f"case-{number:02d}.md").read_text(encoding="utf-8")

    def test_the_set_has_four_cases(self):
        self.assertEqual(len(sorted(self.OBESITY_BMI.glob("case-*.md"))), 4)

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(self.OBESITY_BMI.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_no_case_carries_a_body_measurement(self):
        """The row under test is about a BMI with no given input at all."""
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_body_measurement(self.case(n)))

    def test_no_case_carries_any_vital(self):
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_any_vital(self.case(n)))

    def test_the_anchors_document_obesity(self):
        for n in self.ANCHORS:
            with self.subTest(case=n):
                self.assertTrue(cc.has_documented_obesity(self.case(n)))

    def test_the_controls_document_a_bariatric_history_and_not_an_obesity(self):
        """Both halves are load-bearing, and O5 is why the second one is.

        O5 forbids obesity being written into these two patients' histories,
        on the ground that the shorthand documents the surgery and never the
        diagnosis. Add the word to either input and the row starts failing
        correct notes -- so this asserts the premise rather than trusting it.
        """
        for n in self.CONTROLS:
            with self.subTest(case=n):
                note = self.case(n)
                self.assertTrue(cc.has_bariatric_history(note))
                self.assertFalse(cc.has_documented_obesity(note))

    def test_the_anchors_carry_no_bariatric_history(self):
        """Otherwise O2's second exit would be available on every case."""
        for n in self.ANCHORS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_bariatric_history(self.case(n)))

    def test_every_case_states_an_age(self):
        """Including case 2, whose age was derived before its birth date came out."""
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertIsNotNone(cc.age_in_years(self.case(n)))

    def test_no_case_carries_a_date_of_birth(self):
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_dob(self.case(n)))

    def test_the_split_is_the_whole_set(self):
        numbers = [
            int(p.stem.split("-")[1]) for p in sorted(self.OBESITY_BMI.glob("case-*.md"))
        ]
        self.assertEqual(numbers, sorted(self.ANCHORS + self.CONTROLS))


class SocialSlotsSplitTwoWays(unittest.TestCase):
    """Issue #29. The two slots the corpus can classify, and they go opposite ways.

    This class does the second job ``DayBIsTheAbsenceSet`` does: it guards a
    property of the *inputs* that a ruling rests on. day-a R14 forbids filling a
    positive tobacco status and day-b R1 no longer forbids filling ``NKDA``, and
    both of those follow from the split asserted here. A well-meaning edit that
    "completed" a fixture's social history would leave the rows standing on
    nothing.

    **These are 31 committed fixture cases, a floor on the corpus and not the
    corpus.** They were also the figures ``SKILL.md`` and both assertion files
    quoted until 2026-08-16; those three now quote the corpus, which issue #78
    ran. Nothing here should be read as a corpus measurement -- what is pinned is
    the direction, which is what the ruling turns on.

    **The allergy figure this class pins is not the one the ruling rests on, and
    that is deliberate rather than an oversight.** ``NKDA`` is *no known drug
    allergy*, so ``allergy_status_none`` is the wrong denominator for it;
    ``AllergyKindSplitsThreeWays`` below carries the right one. This class is
    kept counting the undivided column because the undivided column is what
    ``ALLERGY_NONE`` measures, and a test that quietly re-aimed at a different
    population would stop guarding the extractor it was written for.
    """

    OBESITY_BMI = OBESITY_BMI_SHORTHAND

    ALLERGY_SPLIT = (
        (FIXTURES, DAY_A_ALLERGY_NONE, DAY_A_ALLERGY_STATED),
        (DAY_B, DAY_B_ALLERGY_NONE, DAY_B_ALLERGY_STATED),
        (PEDS_BP, PEDS_BP_ALLERGY_NONE, PEDS_BP_ALLERGY_STATED),
    )
    TOBACCO_SPLIT = (
        (FIXTURES, DAY_A_TOBACCO_POSITIVE, ()),
        (DAY_B, DAY_B_TOBACCO_POSITIVE, DAY_B_TOBACCO_NEGATED),
    )

    def all_cases(self):
        return all_committed_cases()

    def test_thirty_one_committed_cases(self):
        """The denominator every figure below is quoted against."""
        self.assertEqual(len(list(self.all_cases())), 31)

    def test_the_allergy_slot_is_written_even_to_say_none(self):
        """The gap reading: eleven of sixteen written statuses are ``NKDA``."""
        none = stated = 0
        for directory, none_cases, stated_cases in self.ALLERGY_SPLIT:
            for number in none_cases:
                with self.subTest(set=directory.parent.name, case=number, says="none"):
                    note = case(directory, number)
                    self.assertTrue(cc.has_allergy_status(note))
                    self.assertFalse(cc.has_stated_allergy(note))
                none += 1
            for number in stated_cases:
                with self.subTest(set=directory.parent.name, case=number, says="an allergen"):
                    note = case(directory, number)
                    self.assertTrue(cc.has_allergy_status(note))
                    self.assertTrue(cc.has_stated_allergy(note))
                stated += 1
        self.assertEqual((none, stated), (11, 5))

    def test_the_tobacco_slot_is_written_only_when_there_is_something_in_it(self):
        """The absence reading: fourteen of fifteen written statuses are positive."""
        positive = negated = 0
        for directory, positive_cases, negated_cases in self.TOBACCO_SPLIT:
            for number in positive_cases:
                with self.subTest(set=directory.parent.name, case=number, says="positive"):
                    note = case(directory, number)
                    self.assertTrue(cc.has_tobacco_status(note))
                    self.assertTrue(cc.has_positive_tobacco(note))
                positive += 1
            for number in negated_cases:
                with self.subTest(set=directory.parent.name, case=number, says="denied"):
                    note = case(directory, number)
                    self.assertTrue(cc.has_tobacco_status(note))
                    self.assertFalse(cc.has_positive_tobacco(note))
                negated += 1
        self.assertEqual((positive, negated), (14, 1))

    def test_no_other_committed_case_writes_either_slot(self):
        """Both case lists are exhaustive, so the denominators mean something."""
        allergy = {(d, n) for d, none, stated in self.ALLERGY_SPLIT
                   for n in none + stated}
        tobacco = {(d, n) for d, pos, neg in self.TOBACCO_SPLIT for n in pos + neg}
        for path, note in self.all_cases():
            number = int(path.stem.split("-")[1])
            key = (path.parent, number)
            with self.subTest(case=str(path.relative_to(REPO_ROOT))):
                self.assertEqual(cc.has_allergy_status(note), key in allergy)
                self.assertEqual(cc.has_tobacco_status(note), key in tobacco)

    def test_the_two_slots_classify_opposite_ways(self):
        """The ruling itself, as one comparison rather than two counts.

        A slot written to say nothing is a transcription gap when silent; a slot
        written only when positive is a real absence. Stated as a ratio so it
        survives the corpus growing, which the raw counts above do not.

        **The allergy limb of that promise was not kept, and issue #78 is where
        it broke.** Over the corpus the undivided allergy ratio is 38%, so this
        assertion holds on the fixtures and is false of the population they are a
        floor on. It is left as it is because it guards ``ALLERGY_NONE`` against
        a fixture edit, which is a real job; what it is not is a statement about
        the clinician. ``AllergyKindSplitsThreeWays::test_the_row_the_nkda_fill_rests_on``
        makes the claim this docstring thought it was making, on the drug-allergy
        reading, where the fixtures give 14 of 16 and the corpus 195 of 284.
        """
        allergy_none = sum(
            1 for _, note in self.all_cases()
            if cc.has_allergy_status(note) and not cc.has_stated_allergy(note)
        )
        allergy_any = sum(1 for _, n in self.all_cases() if cc.has_allergy_status(n))
        tobacco_negated = sum(
            1 for _, note in self.all_cases()
            if cc.has_tobacco_status(note) and not cc.has_positive_tobacco(note)
        )
        tobacco_any = sum(1 for _, n in self.all_cases() if cc.has_tobacco_status(n))
        self.assertGreater(allergy_none / allergy_any, 0.5)
        self.assertLess(tobacco_negated / tobacco_any, 0.2)

    def test_the_anatomical_snuff_box_is_a_wrist_exam(self):
        """A bare ``snuff`` reads day-a case 9's scaphoid exam as tobacco use."""
        self.assertFalse(cc.has_tobacco_status("she has anitomical snuff box tenderness"))

    def test_chewing_cardboard_is_not_chewing_tobacco(self):
        """A bare ``chew`` reads peds-bp case 3's sensory habit as tobacco use."""
        note = case(PEDS_BP, 3)
        self.assertIn("chews on cardboard", note)
        self.assertFalse(cc.has_tobacco_status(note))

    def test_day_a_case_9_survives_its_own_decoy(self):
        """It carries both: second-hand smoke exposure *and* the snuff box."""
        note = case(FIXTURES, 9)
        self.assertTrue(cc.has_tobacco_status(note))
        self.assertTrue(cc.has_positive_tobacco(note))

    def test_second_hand_exposure_is_a_positive_status(self):
        """Not the patient smoking, and still not an absence. day-a 7 and 9."""
        self.assertTrue(cc.has_positive_tobacco("is exposed to second hand smoke"))

    def test_a_former_smoker_is_a_positive_status(self):
        for text in ("is a former smoker 0", "former 3 ppd smoker for 30 yrs",
                     "former vaper", "former smoker 1 ppd x 1 yr dips now"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_positive_tobacco(text))

    def test_the_denial_forms_are_not_positive(self):
        for text in ("no smoke, drink, drugs,", "non-smoker", "nonsmoker",
                     "denies tobacco", "never smoked", "no tobacco use"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_tobacco_status(text))
                self.assertFalse(cc.has_positive_tobacco(text))

    def test_a_positive_tobacco_marker_always_implies_the_slot(self):
        """The invariant ``tobacco_negated`` subtracts on, asserted rather than assumed.

        ``Census.tobacco_negated`` is ``with_tobacco_status - tobacco_positive``, so a
        string matching ``TOBACCO_POSITIVE`` and not ``TOBACCO_SLOT`` makes that
        subtraction produce a negative count. ``survey`` happens to gate the second
        counter behind the first, which hides the divergence rather than preventing
        it -- ``\\bppd\\b`` was in both patterns and the spelled-out pack-per-day form
        was in neither, and no case-list test could have caught it.
        """
        for text in ("2 packs a day", "1 pack per day", "3 pks/day", "1 ppd",
                     "he is a smoker", "former vaper", "chews tobacco now",
                     "is exposed to second hand smoke"):
            with self.subTest(text=text):
                if cc.has_positive_tobacco(text):
                    self.assertTrue(cc.has_tobacco_status(text))

    def test_the_invariant_holds_on_every_committed_case(self):
        for path, note in self.all_cases():
            with self.subTest(case=str(path.relative_to(REPO_ROOT))):
                if cc.has_positive_tobacco(note):
                    self.assertTrue(cc.has_tobacco_status(note))
                if cc.has_stated_allergy(note):
                    self.assertTrue(cc.has_allergy_status(note))

    def test_neither_slot_count_can_go_negative(self):
        """The two derived properties, over the whole committed corpus."""
        c = cc.survey([note for _, note in self.all_cases()])
        self.assertGreaterEqual(c.tobacco_negated, 0)
        self.assertGreaterEqual(c.allergy_status_stated, 0)

    def test_survey_counts_both_slots(self):
        notes = [note for _, note in self.all_cases()]
        c = cc.survey(notes)
        self.assertEqual(c.with_allergy_status, 16)
        self.assertEqual(c.allergy_status_none, 11)
        self.assertEqual(c.allergy_status_stated, 5)
        self.assertEqual(c.with_tobacco_status, 15)
        self.assertEqual(c.tobacco_positive, 14)
        self.assertEqual(c.tobacco_negated, 1)


class AllergyKindSplitsThreeWays(unittest.TestCase):
    """Issue #78. Which *kind* of allergy the "names something" column named.

    ``SocialSlotsSplitTwoWays`` above measures whether the allergy slot was
    written to say nothing. This class measures the other half, and it is the
    half the ruling turns on: ``NKDA`` is *no known drug allergy*, so a note
    naming a seasonal one is fully compatible with filling ``NKDA`` and is no
    evidence at all against the gap reading. The corpus run owed by #78 came back
    with **173 of 284 written allergy statuses naming something**, which fires
    that ticket's own reopen trigger -- and three of the five committed cases in
    that column name nothing but an environmental allergy, so the trigger fires
    on a column that cannot tell the two apart. The clinician ruled on
    2026-08-16 that a note naming only environmental allergies still takes
    ``NKDA``, and named **food** as the third category to separate.

    Drug, food and environmental are the three ``DAVID`` checks, per the
    clinician, and they are what these three token sets carry. A stated allergy
    matching none of them is counted **unclassified** rather than assigned, so a
    name the lists miss is a printed number instead of a silent misfiling.
    """

    def kinds(self, note):
        return (cc.has_drug_allergy(note),
                cc.has_food_allergy(note),
                cc.has_environmental_allergy(note))

    def test_the_two_drug_allergy_cases(self):
        """day-b 7 names six drugs; day-b 11 names levaquin. Nothing else does."""
        for directory, number in ALLERGY_DRUG_CASES:
            with self.subTest(set=directory.parent.name, case=number):
                self.assertTrue(cc.has_drug_allergy(case(directory, number)))

    def test_case_eleven_is_a_drug_case_and_was_recorded_as_not_one(self):
        """The correction this class exists to pin, on its own line.

        ``allergies: seasonal allergies, levaquin`` -- both kinds in one clause.
        Both the constant above and ``SKILL.md`` counted one drug case where
        there are two, and the undercount is the sort a wider sweep never sees
        because it reads as agreement between a file and a comment.
        """
        note = case(DAY_B, 11)
        self.assertEqual(self.kinds(note), (True, False, True))

    def test_the_environmental_only_cases(self):
        """The three that fired the reopen trigger while meaning nothing by it."""
        for directory, number in ((FIXTURES, 6), (DAY_B, 2), (PEDS_BP, 5)):
            with self.subTest(set=directory.parent.name, case=number):
                note = case(directory, number)
                self.assertTrue(cc.has_stated_allergy(note))
                self.assertEqual(self.kinds(note), (False, False, True))

    def test_lactose_intolerance_is_not_a_food_allergy(self):
        """peds-bp case 3's ``chews on cardboard`` shape, on the allergy side.

        ``hx: strep pharyngitis, lactose intollaerance seasonal allergies`` is a
        real committed input, an intolerance is not an allergy, and ``lactose``
        sits outside the window because the window reaches one word back from
        the allergy token and no further. It is excluded structurally rather
        than by a token, which is why no ``lactose`` exclusion appears anywhere.
        """
        note = case(PEDS_BP, 5)
        self.assertIn("lactose", note)
        self.assertFalse(cc.has_food_allergy(note))

    def test_a_drug_in_the_plan_is_not_an_allergen(self):
        """The window is the allergy token's own sentence, not the note.

        day-b 11 proposes bactrim in a plan while its allergy is levaquin. A
        note-wide match would read every antibiotic prescribed anywhere as an
        allergen, which would put ``allergies: nkda`` cases into the drug column
        the moment anything was prescribed.
        """
        note = "Note 1\nallergies: seasonal allergies\nPlan bactrim ds BID\n"
        self.assertEqual(self.kinds(note), (False, False, True))

    def test_an_allergen_the_lists_miss_lands_in_unclassified(self):
        """The safety valve, and the reason a token list is publishable at all."""
        note = "Note 1\nallergies: zorbaxin\n"
        self.assertTrue(cc.has_stated_allergy(note))
        self.assertEqual(self.kinds(note), (False, False, False))
        c = cc.survey([note])
        self.assertEqual(c.allergy_unclassified, 1)

    def test_a_denial_longhand_is_not_a_named_drug_allergen(self):
        """The worst defect this class was written to guard, found in review.

        ``ALLERGY_NONE`` required the negation to sit *adjacent* to the word, so
        a qualifier between them broke it -- and ``ALLERGY_DRUG``'s generic
        ``drug allerg`` form then read the denial as a **named drug allergen**.
        A note saying the patient has no drug allergies became the strongest
        evidence the corpus could offer against filling ``NKDA``. Two corpus
        encounters were affected; the direction is what makes it worth a test of
        its own rather than a figure.
        """
        for text in ("no drug allergies", "denies drug allergies",
                     "denies any medication allergies", "no history of drug allergies",
                     "no known drug allergies", "allergies: denies",
                     "no hx allergies", "no sig hx allergies"):
            with self.subTest(text=text):
                note = f"Note 1\n{text}\n"
                self.assertFalse(cc.has_stated_allergy(note))
                self.assertFalse(cc.has_drug_allergy(note))

    def test_a_negation_of_something_else_is_not_a_denial(self):
        """The latent wrong branch the qualifier list exists to keep out.

        An arbitrary-word gap reads ``no dm seasonal allergies`` as denying the
        seasonal allergy, because nothing in a regex can tell the negation
        belongs to the diabetes. It costs nothing on today's corpus -- the fix
        moves the count by exactly the two real denials either way -- so it would
        have been latent rather than visible.
        """
        for text in ("hx: htn no dm seasonal allergies",
                     "no fever, seasonal allergies"):
            with self.subTest(text=text):
                note = f"Note 1\n{text}\n"
                self.assertTrue(cc.has_stated_allergy(note))
                self.assertTrue(cc.has_environmental_allergy(note))

    def test_a_denial_that_names_a_drug_anyway_is_counted_apart(self):
        """The one error running against ``allergy_no_drug``. Issue #78.

        Everything else miscounts the safe way. This shape puts a real drug
        allergy on the *no drug* side, which is why it is counted and printed
        rather than argued about -- one corpus encounter, measured 2026-08-16.
        """
        note = "Note 1\nallergies: nkda except penicillin\n"
        self.assertFalse(cc.has_stated_allergy(note))
        self.assertTrue(cc.denies_allergies_but_names_a_drug(note))
        self.assertEqual(cc.survey([note]).allergy_denied_but_drug, 1)

    def test_no_committed_case_denies_and_names_a_drug(self):
        """So the fixture figure of 14 of 16 needs no adjustment."""
        c = cc.survey([note for _, note in all_committed_cases()])
        self.assertEqual(c.allergy_denied_but_drug, 0)

    def test_a_food_allergen_is_read(self):
        """Untested against the corpus rather than unbuilt -- no committed input
        names one, and the clinician named food as a category DAVID checks."""
        for text in ("allergies: peanuts", "allergic to shellfish",
                     "food allergy - eggs", "allergies: tree nuts"):
            with self.subTest(text=text):
                note = f"Note 1\n{text}\n"
                self.assertTrue(cc.has_food_allergy(note))
                self.assertFalse(cc.has_drug_allergy(note))

    def test_a_kind_never_fires_where_the_slot_says_none(self):
        """``NKDA`` and a kind cannot both hold, or the columns do not sum."""
        for directory, numbers in ((FIXTURES, DAY_A_ALLERGY_NONE),
                                   (DAY_B, DAY_B_ALLERGY_NONE),
                                   (PEDS_BP, PEDS_BP_ALLERGY_NONE)):
            for number in numbers:
                with self.subTest(set=directory.parent.name, case=number):
                    self.assertEqual(self.kinds(case(directory, number)),
                                     (False, False, False))

    def test_every_kind_implies_a_stated_allergy(self):
        """The invariant ``allergy_unclassified`` subtracts on.

        ``SocialSlotsSplitTwoWays::test_a_positive_tobacco_marker_always_implies_the_slot``
        is this test with the slot changed, and it exists for that test's reason:
        ``survey`` gates the kind counters behind ``has_stated_allergy``, which
        hides a divergence rather than preventing one.
        """
        for path, note in all_committed_cases():
            with self.subTest(case=str(path.relative_to(REPO_ROOT))):
                if any(self.kinds(note)):
                    self.assertTrue(cc.has_stated_allergy(note))

    def test_survey_counts_the_three_kinds(self):
        notes = [note for _, note in all_committed_cases()]
        c = cc.survey(notes)
        self.assertEqual(c.allergy_status_stated, 5)
        self.assertEqual(c.allergy_drug, len(ALLERGY_DRUG_CASES))
        self.assertEqual(c.allergy_food, len(ALLERGY_FOOD_CASES))
        self.assertEqual(c.allergy_environmental, len(ALLERGY_ENVIRONMENTAL_CASES))
        self.assertEqual(c.allergy_unclassified, 0)

    def test_the_row_the_nkda_fill_rests_on(self):
        """14 of 16 written statuses name no drug allergen, over the fixtures.

        The figure ``SocialSlotsSplitTwoWays`` publishes for the same population
        is 11 of 16, and 11 of 16 is not what ``NKDA`` is a claim about. Read on
        drug allergens the fixture floor is *stronger* than the one #29 ruled on,
        not weaker -- which is why #78's reopen trigger, written against the
        undivided column, fired on a set that agrees with the ruling.
        """
        c = cc.survey([note for _, note in all_committed_cases()])
        self.assertEqual(c.allergy_no_drug, 14)
        self.assertEqual(c.allergy_no_drug_worst_case, 14)  # nothing unclassified
        self.assertGreater(c.allergy_no_drug / c.with_allergy_status, 0.5)

    def test_the_kinds_overlap_and_the_report_may_not_sum_them(self):
        """Two of the five name a drug *and* an environmental allergy.

        So the three columns are not a partition and adding them double-counts a
        patient -- the error ``SocialSlotsSplitTwoWays``'s own comment records
        being made once already, counting clauses instead of cases.
        """
        notes = [note for _, note in all_committed_cases()]
        c = cc.survey(notes)
        self.assertGreater(
            c.allergy_drug + c.allergy_food + c.allergy_environmental,
            c.allergy_status_stated,
        )


class PpdIsPacksPerDayByShape(unittest.TestCase):
    """Issue #78's last residual, settled by form rather than by reading.

    ``ppd`` is packs per day and is also a purified protein derivative, and the
    census counts the first as a positive tobacco history. #78 asked for a hand
    audit of the corpus and called it *"the first thing to check"* if the tobacco
    figure looked high.

    **It was closed without one, on the clinician's ruling of 2026-08-16, because
    the two senses are not the same shape.** A pack count is a small number in
    front of the token and usually a span behind it. A skin test has no quantity
    in front at all: it is placed, it is read, and its result is millimetres of
    induration. Nobody writes a tuberculin test as a number of packs followed by
    years.

    Measured over 551 encounters the same day, counts only: **102 write a bare
    ``ppd``, 13 carry no independent tobacco token** -- the only ones at risk,
    since the rest are named smokers whatever ``ppd`` means -- and of those 13,
    **13 are a pack quantity and 0 are a skin test**. The census prints those
    four numbers now, so the audit is re-derivable rather than quoted.

    **This is inference from form and not a reading, and the class name says so.**
    What it does not establish is that no encounter anywhere writes a tuberculin
    test in a shape both patterns miss. What makes that survivable is the bound
    #78 already had: charge all 13 as skin tests anyway and tobacco is still 159
    of 197 positive, 81%, so no reading of them can move #29's ruling.
    """

    def bare_ppd_cases(self):
        for path, note in all_fixture_shorthand():
            if cc.writes_bare_ppd(note):
                yield path, note

    def test_the_committed_inputs_writing_a_bare_ppd(self):
        """Twelve of them, over **all six** sets rather than the usual four.

        ``all_committed_cases`` reads day-a, day-b, peds-bp and obesity-bmi, and
        that omission is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143):
        the denominator those figures are quoted against is 31 while the tree
        holds 37. This class reads all six deliberately, because the audit's
        claim is about *every* committed input writing the token and leaving two
        sets out would make it arbitrary. It costs two real cases --
        ``duration-span`` and ``hedged-dx`` each write one.

        **The existing figures are not re-aimed here.** #143 holds that decision,
        and changing a published denominator sideways inside a new test class is
        how a figure ends up meaning two things.
        """
        self.assertEqual(len(list(self.bare_ppd_cases())), 12)

    def test_every_committed_bare_ppd_is_a_pack_quantity(self):
        for path, note in self.bare_ppd_cases():
            with self.subTest(case=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(cc.ppd_written_as_quantity(note))
                self.assertFalse(cc.ppd_written_as_skin_test(note))

    def test_two_committed_inputs_have_the_corpus_shortlist_shape(self):
        """A bare ``ppd`` and no other tobacco word -- the at-risk shape.

        These two are why the discriminator is not tested only against strings
        this file invented. day-b case 8 writes the pack count with no smoking
        word anywhere near it, which is exactly the shape the 13 corpus
        encounters have, and it still reads as a quantity on both limbs -- a
        number in front and a span behind.
        """
        shortlist = [(d, n) for d, n in ((DAY_B, 7), (DAY_B, 8))]
        for directory, number in shortlist:
            with self.subTest(case=number):
                note = case(directory, number)
                self.assertTrue(cc.writes_bare_ppd(note))
                self.assertFalse(cc.has_independent_tobacco(note))
                self.assertTrue(cc.ppd_written_as_quantity(note))
                self.assertFalse(cc.ppd_written_as_skin_test(note))
        found = {(p.parent, int(p.stem.split("-")[1]))
                 for p, n in self.bare_ppd_cases() if not cc.has_independent_tobacco(n)}
        self.assertEqual(found, set(shortlist))

    def test_a_tuberculin_test_reads_as_one(self):
        """The other sense, which no committed input writes."""
        for text in ("PPD placed today", "ppd read at 48 hrs", "PPD 12mm",
                     "ppd 0 mm", "induration 15mm", "quantiferon negative",
                     "mantoux placed", "ppd for tb screening"):
            with self.subTest(text=text):
                self.assertTrue(cc.ppd_written_as_skin_test(text))

    def test_the_two_shapes_do_not_both_fire_on_a_pack_count(self):
        """A quantity form must never read as a skin test, or the audit is noise."""
        for text in ("1 ppd x 20 yrs", "0.5 ppd smoker for 40 years",
                     "<0.25 ppd x 3 yrs", "3 ppd for 30 yrs",
                     "1 ppd since 18 yrs of age", "1.5 ppd 34 years"):
            with self.subTest(text=text):
                self.assertTrue(cc.ppd_written_as_quantity(text))
                self.assertFalse(cc.ppd_written_as_skin_test(text))

    def test_the_audit_population_is_the_one_the_tobacco_patterns_see(self):
        """A welded ``1ppd`` is outside it, and that is issue #146 and not this.

        ``\\bppd\\b`` cannot match a digit-welded quantity -- the leading boundary
        needs a non-word character and a digit is a word character. So the audit
        counts what ``TOBACCO_SLOT`` counts and is silent about what it misses.
        Counting the welded form here would make this class quietly answer a
        different ticket.
        """
        self.assertFalse(cc.writes_bare_ppd("1ppd x 24 yrs"))
        self.assertTrue(cc.writes_bare_ppd("1 ppd x 24 yrs"))

    def test_the_slot_is_the_bare_token_or_an_independent_one(self):
        """The composition the audit's exclusion rests on, asserted not assumed.

        ``TOBACCO_SLOT`` and ``TOBACCO_INDEPENDENT`` are built from one shared
        string so they cannot drift, and this is the test that says what the
        relationship is meant to be: every slot match is either a bare ``ppd`` or
        an independent token, and nothing else.
        """
        for text in ("1 ppd x 20 yrs", "smoker", "chews tobacco", "non-smoker",
                     "2 packs a day", "vapes", "nicotine", "cigarettes",
                     "exposed to second hand smoke", "dips now"):
            with self.subTest(text=text):
                if cc.has_tobacco_status(text):
                    self.assertTrue(cc.writes_bare_ppd(text)
                                    or cc.has_independent_tobacco(text))

    def test_survey_counts_the_audit(self):
        """Over all six sets, matching the class's own denominator."""
        c = cc.survey([note for _, note in all_fixture_shorthand()])
        self.assertEqual(c.with_bare_ppd, 12)
        self.assertEqual(c.bare_ppd_no_other_token, 2)
        self.assertEqual(c.bare_ppd_alone_as_quantity, 2)
        self.assertEqual(c.bare_ppd_alone_as_skin_test, 0)

    def test_the_two_denominators_differ_and_the_gap_is_named(self):
        """37 against 31, and the two sets it is.

        Asserted rather than left in prose, so #143's gap fails a test the day
        somebody closes it instead of going quietly stale like the figure it is
        about.
        """
        wide = {p for p, _ in all_fixture_shorthand()}
        narrow = {p for p, _ in all_committed_cases()}
        self.assertEqual(len(wide), 37)
        self.assertEqual(len(narrow), 31)
        self.assertEqual({p.parent.parent.name for p in wide - narrow},
                         {"duration-span", "hedged-dx"})


class Bands(unittest.TestCase):
    """The age-band counts behind the two figures issue #11 wrote into SKILL.md."""

    def test_bands_partition_the_notes(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES] + [day_b(n) for n in (1, 6, 12)]
        bands = cc.survey_bands(notes)
        self.assertEqual(sum(b.notes for b in bands.values()), len(notes))

    def test_the_peds_set_lands_entirely_under_six(self):
        bands = cc.survey_bands([peds_bp(n) for n in PEDS_BP_CASES])
        self.assertEqual(bands[cc.UNDER_SIX].notes, 5)
        self.assertEqual(bands[cc.UNDER_SIX].without_bp, 5)
        self.assertEqual(bands[cc.UNDER_SIX].vital_line_no_bp, len(PEDS_BP_ANY_VITAL))
        self.assertEqual(bands[cc.UNDER_SIX].no_vital_at_all, 5 - len(PEDS_BP_ANY_VITAL))

    def test_a_missing_age_lands_in_its_own_band_rather_than_an_age_one(self):
        bands = cc.survey_bands(["cc: cough\nbp 120/80\n"])
        self.assertEqual(bands[cc.AGE_UNKNOWN].notes, 1)
        for name in (cc.UNDER_SIX, cc.ADULT):
            with self.subTest(band=name):
                self.assertEqual(bands[name].notes, 0)

    def test_no_vital_at_all_and_vital_line_no_bp_are_disjoint(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES] + [day_b(n) for n in range(1, 13)]
        for name, band in cc.survey_bands(notes).items():
            with self.subTest(band=name):
                self.assertEqual(
                    band.no_vital_at_all + band.vital_line_no_bp, band.without_bp
                )

    def test_the_band_report_emits_no_note_text(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES]
        report = cc.format_report(
            cc.survey(notes), source="fixtures", date="2026-08-11",
            bands=cc.survey_bands(notes),
            files=cc.FileCensus(
                files=1, unique_files=1, with_no_stated_age=0,
                with_age_in_every_note=1, with_mixed_age=0,
            ),
        )
        self.assertIn("line, no BP", report)  # the section really rendered
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan ", "percentile"):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)


class Survey(unittest.TestCase):
    def setUp(self):
        self.notes = [
            p.read_text(encoding="utf-8") for p in sorted(FIXTURES.glob("case-*.md"))
        ]

    def test_counts_the_fixture_set(self):
        c = cc.survey(self.notes)
        self.assertEqual(c.notes, 10)
        self.assertEqual(c.with_bp + c.without_bp, 10)
        self.assertEqual(c.with_either_age_or_dob + c.with_neither, 10)

    def report(self, files: int = 11, unique: int = 10) -> str:
        return cc.format_report(
            cc.survey(self.notes), source="fixtures", date="2026-08-11",
            bands=cc.survey_bands(self.notes),
            files=cc.FileCensus(
                files=files, unique_files=unique, with_no_stated_age=1,
                with_age_in_every_note=4, with_mixed_age=5,
            ),
        )

    def test_report_emits_no_note_text(self):
        """Standing rule 1: the census output must be safe to paste anywhere."""
        report = self.report()
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan "):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)

    def test_format_report_is_never_handed_a_note(self):
        """The invariant the module docstring states, asserted rather than trusted.

        ``Corpus`` holds note text and ``FileCensus`` does not, which is the whole
        reason the second type exists. A signature that took the first would put
        note text one formatting mistake away from the console.
        """
        # ``from __future__ import annotations`` keeps these as strings.
        annotations = cc.format_report.__annotations__
        self.assertNotIn("Corpus", annotations.values())
        self.assertEqual(annotations["files"], "FileCensus")
        for field in cc.FileCensus.__dataclass_fields__.values():
            with self.subTest(field=field.name):
                self.assertEqual(field.type, "int")

    def test_reports_the_duplicate_when_there_is_one(self):
        self.assertIn("files: 11 (10 unique)", self.report())

    def test_says_nothing_about_uniqueness_when_no_file_repeats(self):
        report = self.report(files=10, unique=10)
        files_line = next(l for l in report.splitlines() if l.startswith("files:"))
        self.assertEqual(files_line, "files: 10")


if __name__ == "__main__":
    unittest.main()
