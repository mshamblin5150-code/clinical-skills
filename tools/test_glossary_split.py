"""Pin the split [#228](https://github.com/mshamblin5150-code/clinical-skills/issues/228) made in ``GLOSSARY.md``.

**This is [#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212)'s
defect one skill over, and the higher-stakes copy.** A wrong picklist string fails
to match and somebody notices; **a wrong expansion produces a fluent note stating a
finding the patient does not have**, and neither direction is recoverable
downstream because both read perfectly well.

So the file a second clinician inherits holds **the field's forms**, and one
person's hand lives in ``scratch/shorthand.md``. ``GLOSSARY.md``'s *Two
glossaries* section is the rule; this file is the gate it had none of, which is
what [#222](https://github.com/mshamblin5150-code/clinical-skills/issues/222) was
filed over for the picklists.

**The ruling this encodes is the ticket's option 2 -- keep the tells, move the
verdicts** -- taken from the clinician 2026-08-19. An ambiguous token stays in the
reference with **both** of its readings and the tell that separates them, because
a second clinician who inherits the ambiguity flagged but unresolved is strictly
safer than one who inherits nothing. What leaves is the *verdict* -- *every
instance in this catalog is packs per day* -- which is a count over one account's
notes and is evidence about one hand rather than about English.

**One check is row-scoped and the rest are whole-file, and the split is
deliberate rather than uniform.** ``HIS_FORMS`` reads the first cell of a table row
and nothing else, because the *Two glossaries* section names ``rec 4 days`` and
``36in 33lb`` on purpose -- they are how it explains what a per-account form **is**
-- so a whole-file search would refuse the paragraph stating the rule. That is
``spelling_scan.py``'s mention-versus-use distinction borrowed for one check, **not
adopted whole**, and the polarity is inverted: there a backticked span is exempt,
here the backticked cell is exactly what is refused. ``VERDICTS`` and ``HIS_TYPOS``
are whole-file, because a moved verdict has no legitimate mention left.

**What it cannot reach**: a per-account form nobody listed here. The denylist is
the forms #228 named plus the confirmed misspellings that were sitting in the
tables beside them, so a *new* row in one clinician's hand lands unflagged. That
is the same limit ``test_skill_agreement.py`` states for #222's gate -- it reaches
a declared name and not an undeclared one -- and it is why the rule is written in
the file as well as checked here.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOSSARY = REPO_ROOT / "skills" / "clinical-note" / "GLOSSARY.md"
CLINICAL_NOTE = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"

#: A table row's first cell, for any line that is one. Separator rows and the
#: repeated header are dropped by content below rather than by position -- this
#: file holds a dozen tables and the second one's first data row is not a header.
ROW = re.compile(r"^\|([^|]+)\|", re.M)

#: Every backticked span, which is how a cell names the forms it covers. A cell
#: can carry more than one, so this returns a list rather than a first match.
TICKED = re.compile(r"`([^`]+)`")

#: The forms #228 named, plus the confirmed misspellings that were rows of their
#: own. Every one is a fact about one person's typing rather than about the
#: field: ``36in 33lb`` is a compression he uses, ``wic`` reads as *walk-in
#: clinic* here while the same string nationally names a federal nutrition
#: program, and the rest are misspellings confirmed as tokens.
HIS_FORMS = (
    "rec 4 days",
    "36in 33lb",
    "2/2j",
    "rosvig",
    "rovsig",
    "xeroisis",
    "homen sign",
    "oturbator",
    "decaron",
    "teselon perle",
    "wic",
)

#: Recurring misspellings that were listed with occurrence counts over one
#: account's catalog. Checked against the **whole file** rather than against
#: rows, because unlike the forms above they have no legitimate mention here --
#: the rule they illustrated is stated without naming an instance.
HIS_TYPOS = ("buldging", "cetrazine", "dimnished", "obsucred", "netti pot")

#: The verdicts. Each is a count over one catalog, and each is the sentence that
#: told a reader which way to resolve. They belong in the per-account file.
#:
#: **Matched case-insensitively, and that is a fix rather than a convenience.** The
#: first version listed the ``PPD`` verdict lowercase, which matched only the
#: *quotation* of it in the intro paragraph and never the verdict itself --
#: ``**Every instance in this catalog is packs per day**``. Both happened to be
#: deleted together, so the check went green while being unable to see the sentence
#: it names. A restored verdict would have sailed through. Caught by the standards
#: axis of ``/code-review``, and it is this repo's signature failure landing inside
#: the class whose docstring claims to guard against it.
VERDICTS = (
    "every instance in this catalog is packs per day",
    "every instance here is culture and sensitivity",
    "it appears only in surgical histories here",
    "both readings are common in this catalog",
    "appendectomy, not appendicitis",
    "from the 2025 scans",
)

#: Field forms that must **still** be rows. The absence checks above cannot tell a
#: per-account form being moved from a field form being deleted with it, and that
#: is not hypothetical: #228's first pass deleted ``rovsing`` along with the two
#: misspellings of it, leaving the paragraph above the table asserting that a sign
#: with no row *appears below*. Only the spellings were one person's; the sign is
#: the field's, and ``setup-clinical-skills`` calls a positive Rovsing's
#: **Universal** in its own words.
FIELD_FORMS = ("hx", "wnl", "spo2 96", "rovsing", "psoas", "appy", "dips")

#: Every ambiguous token keeps **both** readings, which is the whole of what
#: option 2 preserves. Stated as the pair rather than as the sentence, on
#: ``test_skill_agreement.py``'s reasoning: a test pinning a paragraph verbatim
#: fails on every rewrite and teaches the next session to delete it.
BOTH_READINGS = {
    "CVA": ("costovertebral angle", "cerebrovascular accident"),
    "dm": ("diabetes mellitus", "diminished"),
    "PPD": ("packs per day", "purified protein derivative"),
    "c/s": ("culture and sensitivity", "cesarean section"),
    "hs": ("at bedtime", '"has"'),
    "appy": ("appendectomy", "appendicitis"),
    "WIC": ("walk-in clinic", "federal nutrition program"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row_forms(text: str) -> set[str]:
    """Every backticked form opening a table row, lowercased."""
    forms = set()
    for cell in ROW.findall(text):
        stripped = cell.strip()
        if stripped in ("Shorthand", "") or set(stripped) <= set("- :"):
            continue
        for form in TICKED.findall(cell):
            forms.add(form.strip().lower())
    return forms


def ambiguous_section(text: str) -> str:
    """The ``## Ambiguous`` section, heading to the next ``## `` heading."""
    start = text.index("## Ambiguous")
    return text[start : text.index("\n## ", start + 1)]


class GlossaryCase(unittest.TestCase):
    """The file and its parsed rows, for every case that wants either."""

    def setUp(self):
        self.text = read(GLOSSARY)
        self.forms = row_forms(self.text)
        self.section = ambiguous_section(self.text)


class TheInstrumentIsLive(GlossaryCase):
    """Asserted before anything else, because every check below is an absence.

    A row parser that had stopped matching would report every per-account form
    gone and every one of these tests would pass. That is this repo's recurring
    shape -- a search that could not have worked answering like a settled
    negative -- and ``test_build_artifacts_ignored.py`` was written after its own
    first version passed three of four assertions against exactly that.
    """

    def test_the_parser_reads_the_tables(self):
        self.assertGreater(len(self.forms), 80, "the row parser read almost nothing")

    def test_a_field_form_is_found(self):
        # `hx` is the file's own example of what stays. If this stops matching,
        # every absence check below is measuring nothing.
        self.assertIn("hx", self.forms)

    def test_a_form_that_was_never_here_is_absent(self):
        self.assertNotIn("qwerty", self.forms)

    def test_the_ambiguous_section_is_findable(self):
        self.assertGreater(len(ambiguous_section(read(GLOSSARY))), 500)


class NoPerAccountFormOpensARow(GlossaryCase):
    """The move itself: the field's forms stay, one person's hand goes.

    **Both halves are asserted.** A sweep that deleted everything it touched
    would satisfy the absence half completely, and #228's first pass did exactly
    that to ``rovsing``.
    """

    def test_each_field_form_still_opens_a_row(self):
        for form in FIELD_FORMS:
            with self.subTest(form=form):
                self.assertIn(form, self.forms)

    def test_each_named_form_is_gone_from_the_tables(self):
        for form in HIS_FORMS:
            with self.subTest(form=form):
                self.assertNotIn(form.lower(), self.forms)

    def test_the_rule_may_still_quote_them_in_prose(self):
        """Mention versus use, and it is asserted rather than left implicit.

        The *Two glossaries* section explains what a per-account form is by
        naming two, and a check that refused them would refuse the paragraph
        stating the rule. Requiring them also means a session deleting the rule
        fails a test rather than quietly leaving the tree clean and the rule
        gone.
        """
        text = read(GLOSSARY)
        self.assertIn("`rec 4 days`", text)
        self.assertIn("`36in 33lb`", text)


class TheAmbiguousSectionKeepsTheTellAndDropsTheVerdict(GlossaryCase):
    """Option 2, which is the ruling that made this ticket buildable.

    Both limbs matter and neither is the other. A section with the verdicts
    removed and the tells removed with them leaves a second clinician no warning
    that ``dm`` is a trap; a section with the verdicts kept hands them one
    account's answer with the authority of a reference.
    """

    def test_no_verdict_survives(self):
        # `assertFalse` rather than `assertNotIn`, here and below: the failure
        # message for a whole-file containment prints the whole file, and a
        # quarter of a megabyte of glossary buries the one line that matters.
        folded = self.text.lower()
        for verdict in VERDICTS:
            with self.subTest(verdict=verdict):
                self.assertFalse(
                    verdict.lower() in folded,
                    f"GLOSSARY.md still states {verdict!r}",
                )

    def test_every_token_keeps_both_readings(self):
        for token, readings in BOTH_READINGS.items():
            with self.subTest(token=token):
                self.assertIn(f"`{token}`", self.section)
                for reading in readings:
                    self.assertIn(reading, self.section)

    def test_the_section_routes_the_resolution_to_the_per_account_file(self):
        # Without this the section states an ambiguity and names nowhere to
        # resolve it, which is worse than the verdict it replaced.
        self.assertIn("scratch/shorthand.md", self.section)

    def test_the_flag_rather_than_guess_rule_survives(self):
        self.assertIn("flag rather than guess", self.section)


class TheTypoHabitsAreGoneAndTheRuleRemains(unittest.TestCase):
    """A list of one person's misspellings, with counts over his catalog.

    **The rule those instances illustrated is the field's and stays.** A drug
    typo produces a prescription, so an unrecognized drug spelling is a candidate
    for correction rather than something to pass through -- that is true whoever
    typed it, and it is the half a second clinician needs.
    """

    def test_no_counted_misspelling_survives(self):
        text = read(GLOSSARY)
        for typo in HIS_TYPOS:
            with self.subTest(typo=typo):
                self.assertFalse(
                    typo in text, f"GLOSSARY.md still lists the misspelling {typo!r}"
                )

    def test_the_drug_spelling_rule_survives(self):
        self.assertIn("unrecognized drug spelling", read(GLOSSARY))

    def test_the_skill_no_longer_cites_a_moved_instance(self):
        """``SKILL.md`` pointed at ``cetrazine`` as the glossary's worked case.

        A cross-reference to a row that has moved is worse than none: it reads as
        agreement while sending the reader to a file that no longer holds the
        thing. Same failure ``skills_mirror.py`` exists for, one file over.
        """
        self.assertFalse(
            "cetrazine" in read(CLINICAL_NOTE),
            "clinical-note/SKILL.md still cites a form that has moved",
        )


class EveryWholeFileLiteralCanStillMatchSomething(unittest.TestCase):
    """The positive control the absence checks had none of.

    ``VERDICTS`` and ``HIS_TYPOS`` are literals compared against a file they are
    supposed to be absent from, so **nothing about a passing run distinguishes a
    clean file from a typo in the literal.** The first version of ``VERDICTS``
    carried exactly that defect and was green.

    So each literal is fed a string built to contain it. This cannot prove the
    literal is the sentence that used to be in the glossary -- no test can, once
    the sentence is gone -- but it does prove the comparison is capable of firing,
    which is the half that was missing.
    """

    def test_each_verdict_literal_fires_against_a_string_holding_it(self):
        for verdict in VERDICTS:
            with self.subTest(verdict=verdict):
                planted = f"prose before. **{verdict.capitalize()}**, and after."
                self.assertIn(verdict.lower(), planted.lower())

    def test_each_typo_literal_fires_against_a_string_holding_it(self):
        for typo in HIS_TYPOS:
            with self.subTest(typo=typo):
                self.assertIn(typo, f"`{typo}` -> corrected (7)")


class TheRuleAndTheRoutingAreStillWrittenDown(unittest.TestCase):
    """A tree cleaned with no rule written down fills back up.

    #228's own framing, and the reason the rule landed one ticket before the move
    did.
    """

    def setUp(self):
        self.text = read(GLOSSARY)

    def test_the_two_glossaries_section_is_there(self):
        self.assertIn("## Two glossaries, and this is the one that travels", self.text)

    def test_the_per_account_file_wins_where_they_disagree(self):
        self.assertIn("`scratch/shorthand.md` wins", self.text)

    def test_the_known_defect_disclaimer_is_retired(self):
        """It said the tables still held per-account entries. They do not now.

        Left standing, it is a file telling a reader to distrust rows that are
        already clean -- and it is the sentence a later session would cite as
        permission to add another.
        """
        self.assertFalse(
            "still hold entries that are this clinician's" in self.text,
            "GLOSSARY.md still calls its own tables a known defect",
        )


if __name__ == "__main__":
    unittest.main()
