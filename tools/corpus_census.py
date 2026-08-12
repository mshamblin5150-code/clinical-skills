"""Recompute the measured claims this repo asserts in prose.

Six of them are in skills/clinical-note/SKILL.md, a seventh is in
fixtures/obesity-bmi, where the counts are what justify a fixture set existing at
all, an eighth is drift row 13's rate — how often a hedge reaches the shorthand at
all, against a differential that is generated every time — and a ninth is the
social-slot split, which decides whether silence about a slot is a transcription
gap or a real absence and so which value the note fills into it. All are
counts over the clinician's shorthand corpus, all are load-bearing — rulings have
turned on them — and until this script existed none could be re-derived. Run it
when a claim is about to be relied on again, or when the corpus grows:

    python tools/corpus_census.py [path-to-day-files]

The corpus lives in ``scratch/``, which is gitignored PHI. **This script prints
counts only and never emits note text or a matched value**, so its output is safe
to paste into a ticket. ``format_report`` reads from a ``Census`` of integers and
never sees a note; the only non-numeric things it prints are its own fixed labels
and the corpus directory name. ``test_corpus_census.py`` guards it.

Extractor limits worth knowing before quoting a number:

- A note is a block introduced by a line starting ``Note <n>``. Text before the
  first such line is a day-file header and is dropped.
- Heights without the ``ht`` token are only caught in the ``5'10`` and ``36in``
  forms. A height written any other way reads as absent.
- A date of birth is the ``dob`` token or a bare date alone on its own line.
  A date embedded in prose is not counted, because visit dates and LMP dates
  outnumber birth dates in that position. Audited 2026-08-11 against every
  date literal in the 38 encounters the census reads as carrying neither an
  age nor a birth date: ten literals across nine of those encounters, every
  one of them a menstrual, follow-up, referral or administrative date, and
  none a birth date. Counting all nine encounters anyway is what lands at
  522 of 551 -- the reading the prose carried before 2026-08-11. Issue #9.
- ``OTHER_VITALS`` matches the bare words ``hr``, ``temp``, ``rr`` and ``spo2``
  with no number after them, so an encounter that merely *mentions* a
  temperature in prose counts as carrying a vital. This is load-bearing for the
  band report: of the 18 under-6 encounters counted as a vital line missing only
  its pressure, **17 carry a structured line and one carries the word "temp"**
  inside the exam narrative. Audited 2026-08-11. The claim survives either
  reading, and ``fixtures/peds-bp`` preserves that one case rather than hiding
  it. Every other band's figure is structured throughout.
- A band count is only as good as ``age_in_years``, which takes the **first**
  age in the note and cannot tell a patient's from a parent's or a sibling's.
  Ages sit at the top of these notes, so it is usually the patient's — but no
  band figure should be quoted about an individual encounter, only about the
  distribution. And the ``no age`` band is large: 194 of 551 as of 2026-08-11,
  so every other band is a **floor**, not a population. Quote the ratio within
  a band, never the count as though it were exhaustive.
- ``HEDGE`` counts a **token**, never a hedged diagnosis. ``possibly
  ultrasounds there`` hedges a past test and counts;
  ``fixtures/obesity-bmi/shorthand/case-01.md`` is that case, and it is why
  issue #19's "zero committed fixtures carry a hedge token" was wrong while its
  point -- that none can anchor an assertion about a hedged *diagnosis* -- still
  stands. **It is neither a floor nor a ceiling** either, for the same reason
  the pain-score line below is not: it over-counts tokens that hedge a history
  and under-counts hedges the token list never reaches. Quote it as a proxy.
- **The pain-score line reports a figure no prose asserts yet**, which is the
  one place this script runs ahead of the repo rather than behind it. Issue #30
  made an OLDCARTS severity mandatory on every note without a count behind it,
  and the count that would justify the rule -- how often he writes one himself
  -- was not computable while ``scratch/`` was out of reach. The line is here so
  the first person with the corpus can produce it. **It is neither a floor nor
  a ceiling**: a written date has a score's exact shape and is counted as one,
  and a "12/10" is dropped as out of range. The two errors run opposite ways
  and neither is measured, so quote it as an estimate and say so.
- ``HYPERTENSION`` carries no negation guard, so "denies htn" would count as a
  documented history. Audited 2026-08-11: none of the 175 encounters writing the
  token writes a negated form, so a guard would be exercised by nothing. The
  hypertensive-pressure figures are therefore a **ceiling** on the population and
  not a floor -- but by nothing measurable today. Issue #23.
- The allergy and tobacco slot counts answer **which way silence reads**, not how
  complete the social history is, and only the second column of that block bears
  on it. ``ALLERGY_NONE`` matches a written "none" and ``TOBACCO_POSITIVE``
  matches a written history, so each slot's other reading is a complement --
  which is why a note carrying an allergy denial *and* a stated allergen reads as
  a denial, and a note carrying a tobacco history *and* a denial reads as a
  history. Both are absent from the 31 committed inputs. **These two slots are
  the only ones measurable at all** -- and only one of them, tobacco, is a social
  slot; the allergy line is a heading of its own in both branch templates. No
  count of the unmeasurable remainder is quoted here, because the two templates
  enumerate different lists and any number would be wrong on one of them, which
  is the reasoning ``SKILL.md`` states where it declines to quote one. What
  defeats them is transcription frequency for occupation, education, marital
  status, spiritual, cultural, environmental, nutrition, fitness and sleep, and
  for alcohol and recreational drugs a shared denial -- "no smoke, drink, drugs"
  -- where the negation does not sit adjacent to the word it negates. Issue #29.
- ``\bppd\b`` is packs per day throughout this corpus and is also the standard
  abbreviation for a **purified protein derivative**. Nothing here can tell them
  apart, so a TB skin test written that way counts as a positive tobacco history
  and inflates that column. Audited against the 31 committed inputs, where every
  instance is a pack-per-day quantity; unaudited against ``scratch/``.
- ``dob`` welded straight to its date, with no space between token and value,
  is the shape that defeated ``\\bht\\b`` for ``ht5'7"`` and it would not match
  here either. There is no instance of it in the corpus as of 2026-08-11, so
  the alternative is not carried; this is the line to change if one appears.
"""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# A note opens with "Note 1" at the start of a line. Case-insensitive: the corpus
# contains "NOte 3", and fixtures/day-a/shorthand/case-03.md preserves it.
NOTE_DELIMITER = re.compile(r"(?im)^\s*note\s*#?\s*\d+")

# Two to three digits either side, not touching another digit, slash, dot or dash.
# The negative look-around is what keeps a three-part date and "200/5ml" out; the
# plausibility range below is what keeps "10/10 pain" out.
BP_PAIR = re.compile(r"(?<![\d/.\-])(\d{2,3})\s*/\s*(\d{2,3})(?![\d/.\-])")
SYSTOLIC_RANGE = (70, 260)
DIASTOLIC_RANGE = (30, 160)

# Normal is below 130/80. The threshold is stated in SKILL.md next to the figure,
# because a different threshold gives a materially different percentage.
NORMAL_SYSTOLIC = 130
NORMAL_DIASTOLIC = 80

# The OLDCARTS severity, for issue #30. ``clinical-note`` now requires a pain
# scale on every note, so the number worth having is how often he writes one --
# the population the rule fills for is everything else.
#
# Nearly BP_PAIR's shape, for the same reason in reverse: BP_PAIR's plausibility
# range is what keeps "10/10 pain" out of the pressures, and the
# ``(?<![\d/.\-])`` here is what keeps the "10" inside a systolic of 110 from
# pairing with what follows it.
#
# **The trailing guard is narrower than BP_PAIR's, and deliberately.** A score
# ends a sentence -- "rates his pain 2/10." -- so a dot after it is punctuation,
# not a decimal point. Copying BP_PAIR's ``(?![\d/.\-])`` verbatim silently lost
# two of day-b's seven transcribed scores, and the fixture guard in
# ``test_corpus_census.py`` is what found it. A pressure is written onto a vital
# line where a following dot really is a decimal; a severity is written into
# prose. Same characters, different neighbors.
#
# **A written date is the false positive this cannot exclude.** "3/10" is a
# score and a date in the same characters, and nothing in a line of shorthand
# distinguishes them. Two things keep it small: the denominator must be exactly
# 10, so only the tenth of a month collides, and ``fixtures/day-b`` -- the set
# the split is guarded against -- contains no bare month/day token at all
# (day-b/shorthand/README states it). It runs the opposite way to the
# out-of-range drop below, and neither error is measured; see the module
# docstring for how to quote the figure.
PAIN_SCORE = re.compile(r"(?<![\d/.\-])(\d{1,2})\s*/\s*10\b(?![\d/])")
PAIN_SCALE_MAX = 10

# The spelled-out "63 inches" form must be matched without relying on the "ht"
# token, because the token is sometimes mistyped: fixtures/day-a/shorthand/case-08
# preserves "hr 65 inches", and its README names that typo as a defect the set
# exists to find. A bare "165 in the office" is excluded by requiring either the
# full word or no space before "in".
#
# ``\bht\s*\d`` is the token run straight into its value -- he writes both
# "ht 62.5" and "ht5'7"". The trailing ``\b`` on the plain token cannot match the
# second, and neither can the feet-and-inches alternative, because there is no
# word boundary between the "t" and the "5". It is an extra alternative rather
# than a replacement, so nothing the plain token caught is lost; requiring the
# digit is what keeps "htn" out.
HEIGHT = re.compile(
    r"(?i)\b(?:ht|hgt|height)\b|\bht\s*\d"
    r"|\b\d\s*'\s*\d{1,2}|\b\d{2,3}\s*inch(?:es)?\b|\b\d{2,3}in\b"
)
WEIGHT = re.compile(r"(?i)\b(?:wt|weight)\b|\bwt\s*\d|\b\d{2,3}\s?lbs?\b")
OTHER_VITALS = re.compile(r"(?i)\b(?:hr|pulse|rr|spo2|sao2|temp)\b|\bt\s*\d{2,3}(?:\.\d)?\b")

# Documented obesity, and the two things adjacent to it. Added for issue #15,
# which turns on whether the corpus holds a case that can anchor a row about a
# *filled* BMI -- one whose shorthand documents obesity and supplies no body
# measurement to derive the BMI from.
#
# The three markers stay separate because they are not the same claim:
#
# - ``OBESITY`` is the anchor. The word is written, so a filled BMI below 30
#   contradicts a given.
# - ``BARIATRIC`` is the control. A post-surgical history documents a *past*
#   obesity, which is exactly where a sub-30 BMI is plausible and accountable.
#   Folding it into OBESITY would lose the distinction ``fixtures/obesity-bmi``
#   is built on.
# - ``SLEEP_APNEA`` associates with obesity and entails none of it. It is
#   counted so the set's README can say what it left out and be checked on it.
#
# The leading ``\b`` is load-bearing and was learned the hard way: a bare
# ``obes`` matches inside **lobes**, and this clinician writes lung fields in
# almost every note. "crackles in the bilateral upper lobes" counted as a
# documented obesity until 2026-08-11 and inflated the very figure issue #15
# turned on.
#
# No negation guard is carried. ``\bobes`` matches whatever word precedes it, so
# "no obesity" would count -- and audited 2026-08-11 the corpus contains no
# negated form among the encounters that write the token, so a guard would be
# exercised by nothing. This is the line to change if one appears.
OBESITY = re.compile(r"(?i)\bobes")

# Documented hypertension, for issue #23 -- which turned on whether the rule
# "a known hypertensive gets a hypertensive pressure" describes this clinician's
# own charting. It does not, and the count is the whole of the argument, so the
# marker has to stay extractable.
#
# Three forms, and the boundaries are load-bearing on the first. ``\bhtn\b``
# cannot match inside "ht5'7"" -- the welded height token that defeated
# ``\bht\b`` and cost three encounters their height -- and the leading boundary
# is what keeps it out of longer words, the lesson OBESITY was fixed by.
# ``hypertensi(?:on|ve)`` is closed at both ends rather than left open, and
# ``I10`` is the code, which he writes into pre-existing lists.
#
# **Three ways this can be wrong, all measured to cost nothing today.** Audited
# 2026-08-11 across the 551-encounter corpus, each occurring **zero** times: the
# plural "hypertensives", which the closing ``\b`` wrongly excludes; and two the
# pattern wrongly *includes* -- "pulmonary hypertension", which is I27 and a
# different disease entirely, and "pre-hypertensive", which is not a diagnosis
# at all. The open-ended ``\bhypertensi`` variant returns the same 175, so
# closing it costs nothing either. Each is listed because it costs nothing *in
# this corpus*, which is not the same as being safe, and the next corpus gets no
# such promise.
#
# The leading ``(?i)`` covers ``I10`` as well, so a lowercase "i10" matches.
# That is wanted, not tolerated -- he writes codes both ways -- and it is noted
# because a reader scanning the alternatives sees a capital letter and can
# reasonably assume the opposite.
#
# No negation guard, on OBESITY's reasoning: audited the same day, none of the
# 175 encounters writing the token writes a negated form, so a guard would be
# exercised by nothing. "denies htn" would count. This is the line to change if
# one appears, and ``test_a_negated_mention_still_counts`` is what will fail.
HYPERTENSION = re.compile(r"(?i)\bhtn\b|\bhypertensi(?:on|ve)\b|\bI10\b")

# The procedures are spelled several ways and hyphenated inconsistently, so the
# separator is ``[ -]?`` rather than ``.`` -- a dot would match any character at
# all and let "lapXband" through, which is looser than anything the corpus needs.
# Every alternative is leading-``\b``-anchored on the same reasoning that fixed
# OBESITY above: a three- or four-letter token with no boundary hides inside
# longer words, and this corpus is where that was learned.
BARIATRIC = re.compile(
    r"(?i)\bbariatric|\bgastric bypass|\bsleeve gastrectomy|\blap[ -]?band"
    r"|\broux[ -]?en[ -]?y"
)

# Counted only so the set that leaves these encounters out can say how many it
# left out and be checked on it -- OSA associates with obesity and entails none
# of it. ``osa`` and ``cpap`` need their boundaries for the reason above;
# ``apnea`` gets one for consistency rather than against a known decoy. The
# British ``apnoea`` is deliberately not carried: this is an American corpus,
# the spelling appears in it zero times, and an alternative matched by nothing
# is one nothing can catch going wrong.
SLEEP_APNEA = re.compile(r"(?i)\bosa\b|\bcpap\b|\bapnea")

# A hedge on a diagnosis: the shorthand marks the thing as suspected rather than
# established. Added for issue #19, whose rule for a hedged diagnosis fires on
# whatever share of encounters this measures -- while the differential half of
# the same ticket fires on all of them. Drift row 13 in ``clinical-note`` cites
# the ratio, so it has to be re-derivable rather than recalled.
#
# Every alternative is boundary- or prefix-anchored, on the lesson OBESITY paid
# for. Three of them carry a decoy that is live in this repo:
#
# - ``\bprob\b`` and not ``\bprob``, because **problem** starts the same way and
#   this clinician writes it. ``fixtures/day-a/shorthand/case-10.md`` reads "he
#   states he has problems urinatin"; a bare prefix counts that encounter as
#   hedged, and ``test_corpus_census.py`` asserts against that exact file.
# - ``\bvs\b(?![\s:.\-]*\d)`` because **VS** opens a vital line. The colon is not
#   what separates them, which a first version of this guard assumed: he writes
#   "VS 138/86" and "VS- 138/86" as well as "VS:", and a lookahead rejecting only
#   the colon let every one of those read as a differential. What actually
#   separates them is what comes next -- **a vital line runs into a number and a
#   differential runs into a diagnosis** -- so the guard rejects a digit however
#   it is punctuated.
# - ``\bsusp(?!en)`` because a drug **suspension** is ordinary pediatric
#   prescribing and would inflate the count. ``(?!ension)`` was too narrow and
#   let "suspended" through; ``suspect``, ``suspected`` and ``suspicion`` all
#   take "susp" + a letter other than "e"-"n", so nothing wanted is lost. Unlike
#   the OBESITY negation guard, this one is carried without a corpus audit behind
#   it: ``scratch/`` is not present in every clone, and a guard against a common
#   word is the cheaper error than a figure quietly inflated by it. An
#   abbreviated ``susp`` that really did mean suspension still counts, and
#   nothing can tell those apart.
#
# ``unlikely`` is deliberately absent. A rejection is a conclusion, not a hedge,
# and ``\blikely\b`` cannot match inside it -- so leaving it out costs nothing
# and saying so is what stops it being "fixed" in.
#
# **The figure is a proxy, not a bound, and it errs in both directions.**
#
# It over-counts, because a token is not a hedged diagnosis:
# ``fixtures/obesity-bmi/shorthand/case-01.md`` writes "possibly ultrasounds
# there", hedging a *past test*, and it counts. ``[a-z]\?`` is looser still and
# cannot tell "strep?" from a question typed into the prose.
#
# It under-counts, because the shorthand hedges other ways: **presumed**,
# **concern for**, **c/f**, **query**, **cannot exclude**, **ddx** and the
# prefixed **?fx** are all absent from the alternatives above.
#
# **The seven tokens are the ones issue #19 published**, and that is why the set
# is not being extended here. The ticket's table is the only prior measurement of
# this corpus, and a regex that counted a different set would produce a number
# nobody could compare to it. Widen it deliberately, re-run against the corpus,
# and update every figure that cites it -- do not widen it in passing.
HEDGE = re.compile(
    r"(?i)\bprob\b|\bprobabl"
    r"|\bposs"
    r"|\bsusp(?!en)"
    r"|\br/o\b"
    r"|\bvs\b(?![\s:.\-]*\d)"
    r"|\blikely\b"
    r"|[a-z]\?"
)

# Issue #29. ``clinical-note`` reads silence about a section two ways -- an
# unmentioned exam system is normal because abnormals get charted, while an
# omitted history section is inferred from the rest of the encounter -- and it
# never said which reading a given social slot takes. These two count that.
#
# **The question is not how often he writes the slot. It is what he writes in
# it.** A slot he fills even when the answer is nothing is a habitual template
# field, so silence there is a transcription gap and the note fills the
# unremarkable value. A slot he fills only when there *is* something is charted
# like an abnormal, so silence there is a real absence and the note fills the
# negative. The corpus can decide exactly two slots; the rest of the twelve the
# templates enumerate are transcribed too rarely to classify, which is why
# ``clinical-note`` sends those to the grounding rule instead.
#
# Neither pair carries a negation guard in the ``HYPERTENSION`` sense, because
# here the negation *is* the measurement -- ``ALLERGY_NONE`` and the absence of a
# positive tobacco marker are the whole point.
ALLERGY_SLOT = re.compile(r"(?i)\ballerg|\bnkda\b|\bnka\b")

# The "nothing there" form. ``nkda`` is the corpus's dominant spelling by far;
# the longhand alternatives are carried so a day file that spells it out is not
# read as a stated allergen.
#
# **A note writing both is counted as none, and no committed case does.** ``NKDA``
# means no known *drug* allergy and coexists with a seasonal one, so "nkda,
# seasonal allergies" is a real shape this would misclassify. It is absent from
# all 31 committed inputs, so the branch is untested rather than wrong; this is
# the line to change if one appears.
ALLERGY_NONE = re.compile(
    r"(?i)\bnkda\b|\bnka\b"
    r"|\bno\s+known\s+(?:drug\s+)?allerg"
    r"|\bno\s+allerg|\bdenies\s+allerg"
    r"|\ballerg\w*\s*[:\-]?\s*(?:none|neg)\b"
)

# ``\bnon-?smok`` is a separate alternative because ``\bsmok`` cannot match inside
# "nonsmoker" -- there is no word boundary between "non" and "smoker" when the
# hyphen is dropped, the same shape that defeated ``\bht\b`` for "ht5'7"".
#
# ``\bsnuff\b(?!\s*box)`` is the one exclusion, and it is not hypothetical:
# ``fixtures/day-a/shorthand/case-09.md`` writes "anitomical snuff box
# tenderness" about a scaphoid exam. A bare ``\bsnuff\b`` reads a wrist injury as
# tobacco use. Chewing is required to name tobacco for the same reason --
# ``fixtures/peds-bp/shorthand/case-03.md`` writes "he chews on cardboard".
# The spelled-out pack-per-day form is here *and* in TOBACCO_POSITIVE below, and
# it has to be in both. ``tobacco_negated`` is the slot count minus the positive
# count, so a string the second pattern matches and the first does not makes that
# subtraction go negative. ``survey`` gates the second counter behind the first,
# which hides such a divergence instead of preventing it -- so the invariant is
# asserted directly by
# ``test_corpus_census.py::test_a_positive_tobacco_marker_always_implies_the_slot``,
# which is what caught this alternative missing here.
PACK_PER_DAY = r"\d+\s*(?:pack|pk)s?\s*(?:per|/|a)\s*day"

TOBACCO_SLOT = re.compile(
    r"(?i)\btobacco\b|\bsmok|\bnon-?smok|\bppd\b"
    r"|" + PACK_PER_DAY +
    r"|\bvap(?:e|es|er|ing)\b|\bnicotine\b|\bcigarette"
    r"|\bchew(?:s|ing)?\s+tobacco|\bdips?\s+now\b|\bsnuff\b(?!\s*box)"
)

# Positive is matched explicitly and the denial is the complement, which is the
# opposite of how ``ALLERGY_NONE`` works and is deliberate. A note carrying both a
# history and a denial -- "1 ppd smoker, no smoke in the home" -- would read as a
# denial under a negation regex, and that error inflates the very count the
# ruling turns on. Matching the history instead makes the safe reading the
# default.
#
# ``\bppd\b`` is packs per day throughout this corpus. It is also the abbreviation
# for a purified protein derivative, and nothing here can tell them apart; a TB
# skin test written that way would count as a smoking history.
#
# Second-hand exposure counts as positive. It is not the patient smoking, and it
# is equally not an absence -- the slot was written because there was something to
# write, which is the only thing being measured.
TOBACCO_POSITIVE = re.compile(
    r"(?i)\bppd\b"
    r"|" + PACK_PER_DAY +
    r"|(?<!non-)\bsmoker\b|\bsmokes\b"
    r"|\bformer\s+(?:\d+\s*)?(?:ppd\s+)?(?:smok|vap)"
    r"|\bvaper\b|\bvapes\b"
    r"|\bchew(?:s|ing)?\s+tobacco|\bdips?\s+now\b"
    r"|\bexposed\s+to\s+.{0,20}smoke"
)

# ``y\.?/?o\.?[mf]\b`` is the run-together form -- "45yof", "45y/om" -- where the
# sex letter is welded to the token and defeats the trailing ``\b`` after "o",
# the same shape that defeated ``\bht\b`` for "ht5'7"". It is an extra
# alternative, never a replacement. Requiring the sex letter is what keeps a
# stray "3 your" out; today the corpus's one instance is counted only because it
# sits alone on a line and AGE_AND_SEX_LINE catches it.
AGE_IN_YEARS = re.compile(
    r"(?i)\b(\d{1,3})\s*(?:y\.?o\.?\b|y/o\b|y\.?/?o\.?[mf]\b"
    r"|years?\s*old\b|yrs?\s*old\b|years?\s*of\s*age\b)"
)
# Infants are written "8 months old" or "13 month male". A bare "[mf]" is not
# accepted here: it would read "x 3 days f/u" as a three-day-old.
AGE_UNDER_ONE = re.compile(
    r"(?i)\b\d{1,3}\s*(?:month|mo|week|wk|day)s?\s*(?:old\b|male\b|female\b)"
)
# "51 f" / "48f" / "61F" — always alone on its own line in this corpus. Anchoring
# to the line is what stops "t 98 F" reading as a 98-year-old and "toradol 10 m"
# as a ten-year-old. Audited 2026-08-11: exactly three digit+sex matches in the
# corpus sit anywhere other than alone on a line, and all three are decoys — two
# doses, and the "f/u" follow-up token taking the "f", which is the form the
# anchor most has to reject. No encounter loses an age to it.
AGE_AND_SEX_LINE = re.compile(r"(?im)^\s*(\d{1,3})\s*(?:yo|y/o)?\s*[mf]\b\.?\s*$")

# Age bands. Both boundaries are borrowed rather than invented, because a fourth
# age line in this repo is a defect waiting to happen:
#
# - 6 is where the corpus changes shape. Below it the clinician has never
#   recorded a blood pressure, and the absence is selective rather than a
#   transcription gap. Issue #11.
# - 20 is ``Z68``'s own tabular boundary between the pediatric and adult BMI
#   codes, already ratified in this repo by the shipped code set. It is used
#   here only to name a band; nothing about blood pressure switches on at 20.
#
# The SIX_TO_NINETEEN band exists to hold what neither claim is about, so the bands
# partition the corpus instead of sampling it.
UNDER_SIX = "0-5"
SIX_TO_NINETEEN = "6-19"
ADULT = "20+"
AGE_UNKNOWN = "no age"
BANDS = (UNDER_SIX, SIX_TO_NINETEEN, ADULT, AGE_UNKNOWN)

DOB_TOKEN = re.compile(r"(?i)\bd\.?o\.?b\.?\b")
DOB_BARE_LINE = re.compile(r"(?m)^\s*\d{1,2}[/-]\d{1,2}[/-](?:19|20)?\d{2}\s*$")

Reading = tuple[int, int]


def split_notes(text: str) -> list[str]:
    """Split a day file into encounters, dropping the day-file header."""
    return NOTE_DELIMITER.split(text)[1:]


def bp_readings(note: str) -> list[Reading]:
    """Every plausible blood pressure in a note, as (systolic, diastolic)."""
    readings: list[Reading] = []
    for match in BP_PAIR.finditer(note):
        systolic, diastolic = int(match.group(1)), int(match.group(2))
        if not SYSTOLIC_RANGE[0] <= systolic <= SYSTOLIC_RANGE[1]:
            continue
        if not DIASTOLIC_RANGE[0] <= diastolic <= DIASTOLIC_RANGE[1]:
            continue
        readings.append((systolic, diastolic))
    return readings


def is_normal_bp(reading: Reading) -> bool:
    systolic, diastolic = reading
    return systolic < NORMAL_SYSTOLIC and diastolic < NORMAL_DIASTOLIC


def has_bp(note: str) -> bool:
    return bool(bp_readings(note))


def pain_scores(note: str) -> list[int]:
    """Every transcribed OLDCARTS severity in a note, as whole numbers out of 10.

    Values above 10 are dropped. That loses the occasional "12/10" a patient
    really did say, and it is the deliberate trade: above 10 the shape is far
    likelier to be a date than a score, and the date collision is the error
    this extractor cannot otherwise reduce at all.
    """
    scores = [int(m.group(1)) for m in PAIN_SCORE.finditer(note)]
    return [s for s in scores if s <= PAIN_SCALE_MAX]


def has_pain_score(note: str) -> bool:
    return bool(pain_scores(note))


def has_height(note: str) -> bool:
    return bool(HEIGHT.search(note))


def has_weight(note: str) -> bool:
    return bool(WEIGHT.search(note))


def has_other_vitals(note: str) -> bool:
    """Pulse, temperature, respiratory rate or oxygen saturation."""
    return bool(OTHER_VITALS.search(note))


def has_body_measurement(note: str) -> bool:
    """A height or a weight -- either one makes a BMI partly given.

    Named separately from ``has_any_vital`` because a BMI needs both, and an
    encounter carrying one of them is not a case where the whole measurement had
    to be invented.
    """
    return has_height(note) or has_weight(note)


def has_documented_hypertension(note: str) -> bool:
    return bool(HYPERTENSION.search(note))


def all_bp_readings_normal(note: str) -> bool:
    """True when a note has readings and **every** one of them is normal.

    Nothing here is about hypertension -- the name says pressures because that
    is all it looks at, and the hypertension filter is applied by the caller.

    Per note, not per reading, and the strict leg is deliberate. A note that
    transcribes a recheck after treatment carries two readings, and counting it
    normal on its *best* one would overstate how often this clinician's
    hypertensives sit at target. That is the direction that would flatter the
    rule the figure was measured to test, so it is the direction refused.

    ``any_bp_reading_normal`` is the lenient counterpart, counted beside it in
    the report for exactly one reason: the two agree today, and a report
    showing both is the only thing that will say so when they stop.
    """
    readings = bp_readings(note)
    return bool(readings) and all(is_normal_bp(reading) for reading in readings)


def any_bp_reading_normal(note: str) -> bool:
    """The lenient leg of ``all_bp_readings_normal``, kept only to be compared.

    Quoting a figure that depends on a definition, while the alternative
    definition is uncomputable, is how a number outlives the reasoning behind
    it. This makes the difference a printed integer instead of a claim.
    """
    return any(is_normal_bp(reading) for reading in bp_readings(note))


def has_documented_obesity(note: str) -> bool:
    return bool(OBESITY.search(note))


def has_bariatric_history(note: str) -> bool:
    return bool(BARIATRIC.search(note))


def has_sleep_apnea(note: str) -> bool:
    return bool(SLEEP_APNEA.search(note))


def has_allergy_status(note: str) -> bool:
    """The allergy slot was written, whatever it says. Issue #29."""
    return bool(ALLERGY_SLOT.search(note))


def has_stated_allergy(note: str) -> bool:
    """The slot was written *and* names something. The complement is ``NKDA``."""
    return has_allergy_status(note) and not ALLERGY_NONE.search(note)


def has_tobacco_status(note: str) -> bool:
    """The tobacco slot was written, whatever it says. Issue #29."""
    return bool(TOBACCO_SLOT.search(note))


def has_positive_tobacco(note: str) -> bool:
    """A tobacco history, past or present, or a second-hand exposure.

    The complement over the notes writing the slot at all is the denial count,
    and that ratio is what tells this slot apart from the allergy one.
    """
    return bool(TOBACCO_POSITIVE.search(note))


def has_hedge(note: str) -> bool:
    """A token marking something as suspected rather than established.

    A ceiling on hedged diagnoses rather than a count of them -- see ``HEDGE``
    for what it cannot separate, and for the three decoys it does reject.
    """
    return bool(HEDGE.search(note))


def has_any_vital(note: str) -> bool:
    return has_bp(note) or has_height(note) or has_weight(note) or has_other_vitals(note)


def has_stated_age(note: str) -> bool:
    return bool(
        AGE_IN_YEARS.search(note)
        or AGE_UNDER_ONE.search(note)
        or AGE_AND_SEX_LINE.search(note)
    )


def has_dob(note: str) -> bool:
    return bool(DOB_TOKEN.search(note) or DOB_BARE_LINE.search(note))


def age_in_years(note: str) -> int | None:
    """The stated age in whole years, or None where none is stated.

    The value counterpart to ``has_stated_age``, and it reads the same three
    forms in the same order so the two can never disagree — a note the presence
    check accepts always yields a number here, and one it rejects always yields
    None. ``test_corpus_census.py`` asserts that against every committed fixture.

    **An infant floors to 0.** ``9 months old`` and ``3 week old`` are all the
    same band for every purpose this census serves, and a fractional year would
    invite arithmetic nobody wants on a corpus this size.

    **The first stated age in the note wins**, and a year form beats a month
    form wherever both appear — ``2 yo M`` with ``x 3 months`` later in the
    prose reads as 2. What it cannot do is tell the patient's age from a
    sibling's or a parent's: a note saying the mother is 28 has no marker
    distinguishing that from the patient, and this returns whichever comes
    first. Ages sit at the top of these notes, so that is usually the patient,
    and it is the reason no band count here is quoted to the encounter.
    """
    match = AGE_IN_YEARS.search(note)
    if match:
        return int(match.group(1))
    if AGE_UNDER_ONE.search(note):
        return 0
    match = AGE_AND_SEX_LINE.search(note)
    if match:
        return int(match.group(1))
    return None


def band_of(note: str) -> str:
    age = age_in_years(note)
    if age is None:
        return AGE_UNKNOWN
    if age < 6:
        return UNDER_SIX
    if age < 20:
        return SIX_TO_NINETEEN
    return ADULT


@dataclass(frozen=True)
class Census:
    """Counts only. Nothing here can carry note text."""

    notes: int = 0
    with_bp: int = 0
    with_height: int = 0
    with_weight: int = 0
    with_other_vitals: int = 0
    with_no_vital: int = 0
    bp_and_weight_no_height: int = 0
    readings: int = 0
    readings_normal: int = 0
    with_stated_age: int = 0
    with_dob: int = 0
    with_both_age_and_dob: int = 0
    with_neither: int = 0
    with_obesity: int = 0
    obesity_no_measurement: int = 0
    with_bariatric: int = 0
    bariatric_no_measurement: int = 0
    with_sleep_apnea: int = 0
    sleep_apnea_no_measurement: int = 0
    with_hedge: int = 0
    with_pain_score: int = 0
    with_hypertension: int = 0
    hypertension_with_bp: int = 0
    hypertension_bp_normal: int = 0
    hypertension_bp_normal_lenient: int = 0
    with_allergy_status: int = 0
    allergy_status_none: int = 0
    with_tobacco_status: int = 0
    tobacco_positive: int = 0

    @property
    def allergy_status_stated(self) -> int:
        """Written and naming something. Issue #29."""
        return self.with_allergy_status - self.allergy_status_none

    @property
    def tobacco_negated(self) -> int:
        """Written and denying it -- the count that separates the two slots."""
        return self.with_tobacco_status - self.tobacco_positive

    @property
    def hypertension_bp_not_normal(self) -> int:
        """The population the retired "gets a hypertensive pressure" rule fitted."""
        return self.hypertension_with_bp - self.hypertension_bp_normal

    @property
    def without_pain_score(self) -> int:
        """The population the OLDCARTS severity rule fills for. Issue #30."""
        return self.notes - self.with_pain_score

    @property
    def without_bp(self) -> int:
        return self.notes - self.with_bp

    @property
    def with_either_age_or_dob(self) -> int:
        return self.notes - self.with_neither

    @property
    def with_dob_instead_of_age(self) -> int:
        """A date of birth where no age is stated -- the "instead" in the claim."""
        return self.with_dob - self.with_both_age_and_dob


def survey(notes: list[str]) -> Census:
    bp_n = height_n = weight_n = other_n = no_vital_n = 0
    bp_weight_no_height_n = readings_n = readings_normal_n = 0
    age_n = dob_n = both_n = neither_n = 0
    obes_n = obes_bare_n = bar_n = bar_bare_n = osa_n = osa_bare_n = 0
    hedge_n = pain_n = 0
    htn_n = htn_bp_n = htn_normal_n = htn_lenient_n = 0
    allergy_n = allergy_none_n = tobacco_n = tobacco_pos_n = 0

    for note in notes:
        hedge_n += has_hedge(note)

        if has_allergy_status(note):
            allergy_n += 1
            allergy_none_n += not has_stated_allergy(note)
        if has_tobacco_status(note):
            tobacco_n += 1
            tobacco_pos_n += has_positive_tobacco(note)

        # Parsed once and reused: the hypertension counters, the reading loop
        # below and ``has_bp`` all want the same list, and three passes over the
        # same note to build it three times is three chances to diverge.
        readings = bp_readings(note)

        if has_documented_hypertension(note):
            htn_n += 1
            if readings:
                htn_bp_n += 1
                htn_normal_n += all(is_normal_bp(r) for r in readings)
                htn_lenient_n += any(is_normal_bp(r) for r in readings)

        measured = has_body_measurement(note)
        if has_documented_obesity(note):
            obes_n += 1
            obes_bare_n += not measured
        if has_bariatric_history(note):
            bar_n += 1
            bar_bare_n += not measured
        if has_sleep_apnea(note):
            osa_n += 1
            osa_bare_n += not measured

        bp, height, weight = bool(readings), has_height(note), has_weight(note)
        other, age, dob = has_other_vitals(note), has_stated_age(note), has_dob(note)

        bp_n += bp
        height_n += height
        weight_n += weight
        other_n += other
        no_vital_n += not has_any_vital(note)
        bp_weight_no_height_n += bp and weight and not height
        pain_n += has_pain_score(note)

        for reading in readings:
            readings_n += 1
            readings_normal_n += is_normal_bp(reading)

        age_n += age
        dob_n += dob
        both_n += age and dob
        neither_n += not (age or dob)

    return Census(
        notes=len(notes),
        with_bp=bp_n,
        with_height=height_n,
        with_weight=weight_n,
        with_other_vitals=other_n,
        with_no_vital=no_vital_n,
        bp_and_weight_no_height=bp_weight_no_height_n,
        readings=readings_n,
        readings_normal=readings_normal_n,
        with_stated_age=age_n,
        with_dob=dob_n,
        with_both_age_and_dob=both_n,
        with_neither=neither_n,
        with_obesity=obes_n,
        obesity_no_measurement=obes_bare_n,
        with_bariatric=bar_n,
        bariatric_no_measurement=bar_bare_n,
        with_sleep_apnea=osa_n,
        sleep_apnea_no_measurement=osa_bare_n,
        with_hedge=hedge_n,
        with_pain_score=pain_n,
        with_hypertension=htn_n,
        hypertension_with_bp=htn_bp_n,
        hypertension_bp_normal=htn_normal_n,
        hypertension_bp_normal_lenient=htn_lenient_n,
        with_allergy_status=allergy_n,
        allergy_status_none=allergy_none_n,
        with_tobacco_status=tobacco_n,
        tobacco_positive=tobacco_pos_n,
    )


@dataclass(frozen=True)
class BandCensus:
    """Counts only, for one age band. Nothing here can carry note text."""

    notes: int = 0
    with_bp: int = 0
    no_vital_at_all: int = 0
    vital_line_no_bp: int = 0

    @property
    def without_bp(self) -> int:
        return self.notes - self.with_bp


def survey_bands(notes: list[str]) -> dict[str, BandCensus]:
    """Split the corpus by age and count how a missing pressure goes missing.

    The distinction the whole thing exists for is between the two ways an
    encounter can lack a blood pressure:

    - ``no_vital_at_all`` -- nothing was transcribed. The absence says nothing
      about the value, which is the premise the filled-vitals license rests on.
    - ``vital_line_no_bp`` -- a line **was** transcribed and the pressure alone
      is missing. A selective absence is a decision, not a transcription gap.

    They are exhaustive over ``without_bp`` by construction: a note with no
    pressure either carries some other vital or carries none.
    """
    fields = ("notes", "with_bp", "no_vital_at_all", "vital_line_no_bp")
    tally = {name: dict.fromkeys(fields, 0) for name in BANDS}
    for note in notes:
        row = tally[band_of(note)]
        row["notes"] += 1
        # Exactly one of the three, which is what makes the invariant hold.
        if has_bp(note):
            row["with_bp"] += 1
        elif has_any_vital(note):
            row["vital_line_no_bp"] += 1
        else:
            row["no_vital_at_all"] += 1
    return {name: BandCensus(**row) for name, row in tally.items()}


def _pct(part: int, whole: int) -> str:
    return f"{round(100 * part / whole)}%" if whole else "n/a"


def format_band_report(bands: dict[str, BandCensus]) -> list[str]:
    """The issue #11 claim, as lines. Integers and fixed labels only."""
    lines = [
        'claim: "18 of the 21 encounters under 6 carry a vital line with the',
        '        blood pressure alone missing" (Filled vitals: a small child)',
        "  band      n    BP  no BP   no vital  line, no BP",
    ]
    for name in BANDS:
        b = bands[name]
        lines.append(
            f"  {name:<8}{b.notes:>4}  {b.with_bp:>4}  {b.without_bp:>5}  "
            f"{b.no_vital_at_all:>9}  {b.vital_line_no_bp:>11}"
        )
    lines.append(
        "  a selective absence is a decision; a whole missing line is not"
    )
    return lines


def format_report(
    census: Census,
    source: str,
    date: str,
    bands: dict[str, BandCensus],
    files: FileCensus,
) -> str:
    c = census
    # ASCII only: this output is read in a Windows console and pasted into tickets.
    header = f"files: {files.files}"
    if files.files != files.unique_files:
        header += f" ({files.unique_files} unique)"
    lines = [
        f"corpus census - {source} - {date}",
        header,
        f"encounters: {c.notes}",
        "",
        'claim: "about 93% carry an age or a date of birth"',
        'claim: "age given 69%, both 15%, dob only 12%, neither 5%"',
        "  (batch-shift step 3, over 548 encounters in 48 unique day files)",
        f"  stated age            {c.with_stated_age:>5}  {_pct(c.with_stated_age, c.notes)}",
        f"  date of birth         {c.with_dob:>5}  {_pct(c.with_dob, c.notes)}",
        f"  dob and no age        {c.with_dob_instead_of_age:>5}  "
        f"{_pct(c.with_dob_instead_of_age, c.notes)}",
        f"  both                  {c.with_both_age_and_dob:>5}  "
        f"{_pct(c.with_both_age_and_dob, c.notes)}",
        f"  either                {c.with_either_age_or_dob:>5}  "
        f"{_pct(c.with_either_age_or_dob, c.notes)}",
        f"  neither               {c.with_neither:>5}  {_pct(c.with_neither, c.notes)}",
        "",
        'claim: "this catalog holds day files in which not one encounter states',
        '        an age" (clinical-note step 1, which is why it quotes no share)',
        f"  day files with none   {files.with_no_stated_age:>5}  of {files.unique_files}",
        "",
        'claim: "transcription is all-or-nothing"',
        "  (Filled vitals, body measurements and the pain score)",
        f"  no vital at all       {c.with_no_vital:>5}  {_pct(c.with_no_vital, c.notes)}",
        f"  blood pressure        {c.with_bp:>5}  {_pct(c.with_bp, c.notes)}",
        f"  height                {c.with_height:>5}  {_pct(c.with_height, c.notes)}",
        f"  weight                {c.with_weight:>5}  {_pct(c.with_weight, c.notes)}",
        f"  pulse/temp/rr/spo2    {c.with_other_vitals:>5}  "
        f"{_pct(c.with_other_vitals, c.notes)}",
        f"  BP + weight, no ht    {c.bp_and_weight_no_height:>5}",
        "",
        f'claim: "half the blood pressures he transcribes are below '
        f'{NORMAL_SYSTOLIC}/{NORMAL_DIASTOLIC}"',
        f"  readings              {c.readings:>5}",
        f"  normal                {c.readings_normal:>5}  "
        f"{_pct(c.readings_normal, c.readings)}",
        "",
        'claim: "a documented hypertensive is not reliably hypertensive on the day"',
        "  (Filled vitals: a documented condition never mandates an abnormal;",
        "   issue #23. a note counts normal only when every reading of it is)",
        f"  hypertension written  {c.with_hypertension:>5}  "
        f"{_pct(c.with_hypertension, c.notes)}",
        f"  ...and a BP with it   {c.hypertension_with_bp:>5}",
        f"     normal             {c.hypertension_bp_normal:>5}  "
        f"{_pct(c.hypertension_bp_normal, c.hypertension_with_bp)}",
        f"     not normal         {c.hypertension_bp_not_normal:>5}  "
        f"{_pct(c.hypertension_bp_not_normal, c.hypertension_with_bp)}",
        f"     normal, lenient    {c.hypertension_bp_normal_lenient:>5}  "
        "(any reading vs every reading; quote the strict one)",
        "",
        'claim: "the corpus holds a case that can anchor a filled-BMI row"',
        "  (fixtures/obesity-bmi; issue #15. no ht and no wt is the fixturable shape)",
        "                        any  no ht/wt",
        f"  obesity written     {c.with_obesity:>5}  {c.obesity_no_measurement:>9}",
        f"  bariatric history   {c.with_bariatric:>5}  {c.bariatric_no_measurement:>9}",
        f"  sleep apnea / cpap  {c.with_sleep_apnea:>5}  {c.sleep_apnea_no_measurement:>9}",
        "",
        'claim: "a hedge in the shorthand is rare" (drift row 13; issue #19)',
        "  (a proxy, not a bound - the tokens also hedge a history, and the",
        "   shorthand hedges in ways the token list never reaches)",
        f"  hedge token           {c.with_hedge:>5}  {_pct(c.with_hedge, c.notes)}",
        "",
        'claim: "the severity the note fills is the one he did not write"',
        "  (issue #30. an estimate, not a bound - a written date reads as a",
        "   score and a 12/10 is dropped, and the two errors run opposite ways)",
        f"  pain score written    {c.with_pain_score:>5}  "
        f"{_pct(c.with_pain_score, c.notes)}",
        f"  no score written      {c.without_pain_score:>5}  "
        f"{_pct(c.without_pain_score, c.notes)}",
        "",
        'claim: "silence about allergies is a gap; silence about tobacco is an',
        '        absence" (Silence is undocumented, never absent; issue #29)',
        "  (what matters is the second column, not the first: a slot written to",
        "   say nothing is habitual, so silence in it says nothing either)",
        "                        written   says none   names something",
        f"  allergies           {c.with_allergy_status:>7}  "
        f"{c.allergy_status_none:>10}  {c.allergy_status_stated:>15}",
        f"  tobacco             {c.with_tobacco_status:>7}  "
        f"{c.tobacco_negated:>10}  {c.tobacco_positive:>15}",
        f"  allergies saying none  {_pct(c.allergy_status_none, c.with_allergy_status):>4}"
        f"     tobacco denying it  "
        f"{_pct(c.tobacco_negated, c.with_tobacco_status):>4}",
        "  the two slots must land opposite ways or the ruling has no basis",
    ]
    lines += ["", *format_band_report(bands)]
    return "\n".join(lines)


@dataclass(frozen=True)
class Corpus:
    """The day files read from a directory, byte-identical copies already dropped.

    Grouped by file rather than flattened, because two of this repo's claims are
    about *files* and not about encounters: ``GLOSSARY.md`` counts the catalog in
    files, and ``clinical-note`` step 1 rests on there being whole day files in
    which no encounter states an age. A flat list of notes cannot answer either.

    ``files`` and ``unique_files`` differ by design rather than by accident. One
    day file in the catalog is on disk twice, byte for byte. ``GLOSSARY.md``
    already said so — 49 files, 48 unique — but this script did not, and counted
    that shift's encounters twice. Issue #16.

    **This holds note text.** It is the one thing here that does, so it never
    reaches ``format_report``; ``survey_files`` reduces it to integers first.
    """

    day_files: tuple[tuple[str, ...], ...]
    files: int

    @property
    def notes(self) -> list[str]:
        return [note for day in self.day_files for note in day]

    @property
    def unique_files(self) -> int:
        return len(self.day_files)


@dataclass(frozen=True)
class FileCensus:
    """Counts *of day files*, not of encounters. Integers only, so it can be printed."""

    files: int
    unique_files: int
    with_no_stated_age: int


def survey_files(corpus: Corpus) -> FileCensus:
    """Reduce a ``Corpus`` to integers — the boundary note text does not cross."""
    return FileCensus(
        files=corpus.files,
        unique_files=corpus.unique_files,
        with_no_stated_age=sum(
            1
            for day in corpus.day_files
            if day and not any(has_stated_age(note) for note in day)
        ),
    )


def read_corpus(directory: Path) -> Corpus:
    """Read every day file in ``directory``, dropping byte-identical copies.

    Deduplication is by content, not by filename: the copy in the catalog does
    not share a name with its original. It is also per *file* — two identical
    encounters inside one shift are two encounters, and always were.
    """
    day_files: list[tuple[str, ...]] = []
    seen: set[str] = set()
    files = 0
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in (".txt", ".md") or not path.is_file():
            continue
        files += 1
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        text = path.read_text(encoding="utf-8", errors="replace")
        day_files.append(tuple(split_notes(text)))
    return Corpus(day_files=tuple(day_files), files=files)


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    directory = Path(argv[1]) if len(argv) > 1 else repo_root / "scratch" / "day-file-text"
    if not directory.is_dir():
        print(f"no corpus at {directory}", file=sys.stderr)
        return 1
    corpus = read_corpus(directory)
    if not corpus.notes:
        print(f"no notes found in {directory}", file=sys.stderr)
        return 1
    today = __import__("datetime").date.today().isoformat()
    print(
        format_report(
            survey(corpus.notes),
            source=directory.name,
            date=today,
            bands=survey_bands(corpus.notes),
            files=survey_files(corpus),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
