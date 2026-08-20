"""Recompute the measured claims this repo asserts in prose.

Six of them are in skills/clinical-note/SKILL.md, a seventh is in
fixtures/obesity-bmi, where the counts are what justify a fixture set existing at
all, an eighth is drift row 13's rate — how often a hedge reaches the shorthand at
all, against a differential that is generated every time — and a ninth is the
social-slot split, which decides whether silence about a slot is a transcription
gap or a real absence and so which value the note fills into it, and a tenth is
the organism-specific pool in fixtures/hedged-dx, which is that set's whole
defense of a three-of-seventeen pick. All are
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
- ``AGE_AND_SEX_LINE`` is line-anchored, and what that costs is **printed
  rather than promised**. The report's ``off-line form`` line is a ceiling on
  it: encounters stating no age at all which nonetheless carry a digit+sex
  form on a line with something else. It over-counts on purpose -- a
  Fahrenheit temperature and a bare antibiotic strength are both in it -- and
  it under-counts a correctly written ``10 mg``, so read it as a bound on ages
  and never as a tally of shapes. Turning it into a finding means reading the
  encounters, which is PHI; 3 of 551 on 2026-08-15, read with the clinician's
  authorization, all three decoys. Issue #64, which was filed because the
  claim this replaces was a dated comment produced by the pass that wrote it
  -- and which was **correct**, and still unreproducible until the reading it
  used was written down. See ``AGE_AND_SEX_OFF_LINE``.
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
- ``ORGANISM_SPECIFIC`` narrows that count to encounters also writing an
  organism or a named disease, and it is **a candidate pool rather than a
  population**: the token may sit anywhere in the encounter, so a hedge on
  something else entirely still counts. ``fixtures/hedged-dx`` is three
  encounters picked out of the seventeen this reports, by reading them, and the
  set says so -- what is re-derivable is the pool, never the pick. It errs both
  ways and the comment above names the missing tokens.
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
  history. **Both are absent from every committed input**, and no number is
  quoted for that because the claim is that the population is empty -- the
  denominator behind it moved every time a fixture set landed, which is issue
  #143. **Only one limb of it is pinned, and the sentence says which**: the
  allergy-denial-plus-named-drug shape is counted by
  ``allergy_denied_but_drug``, which
  ``AllergyKindSplitsThreeWays::test_no_committed_case_denies_and_names_a_drug``
  asserts is 0 over the glob. The tobacco limb, and the allergy limb for an
  environmental or food allergen, are **readings** taken over the inputs and
  re-derived by nothing -- a kind fires only where the slot named something, so
  no counter here can see one sitting inside a denial. **These two slots are
  the only ones measurable at all** -- and only one of them, tobacco, is a social
  slot; the allergy line is a heading of its own in both branch templates. No
  count of the unmeasurable remainder is quoted here, because the two templates
  enumerate different lists and any number would be wrong on one of them, which
  is the reasoning ``SKILL.md`` states where it declines to quote one. What
  defeats them is transcription frequency for occupation, education, marital
  status, spiritual, cultural, environmental, nutrition, fitness and sleep, and
  for alcohol and recreational drugs a shared denial -- "no smoke, drink, drugs"
  -- where the negation does not sit adjacent to the word it negates. Issue #29.
- **The allergy slot's "names something" column was the wrong measurement for
  the rule it fed, and it was published as the right one.** ``NKDA`` is *no
  known drug allergy*: a patient with hay fever is NKDA, so a note naming a
  seasonal allergy is no evidence at all against filling it. Issue #78 ran the
  corpus and its own reopen trigger fired -- 173 of 284 written statuses naming
  something, against a fixture floor of 8 of 20 -- and the trigger fired on a
  count that could not tell a drug allergen from a seasonal one. Four of those
  eight fixture cases name nothing but an environmental allergy. **That pair is
  stated here and nowhere else in this module, and it is re-derived rather than
  typed** -- ``test_allergy_reaction.py`` counts both halves off the tree and
  fails when either moves. Issue #143. ``ALLERGY_DRUG``,
  ``ALLERGY_FOOD`` and ``ALLERGY_ENVIRONMENTAL`` split it; the three are the
  categories the clinician named on 2026-08-16, and they are **not a partition**
  -- two of the eight name a drug *and* an environmental allergen, so the report
  never sums them.
- ``allergy_no_drug`` is the row the ``NKDA`` fill actually rests on, and it is a
  **floor**. Three errors bear on it and all three are measured rather than
  assumed. Two run the safe way: ``ALLERGY_DRUG`` is a token list matched inside
  a window that cannot tell an allergen from a medication written beside it on
  the same line, so ``allergy_drug`` is a ceiling; and any of
  ``allergy_unclassified`` that is really a drug belongs on the other side --
  charge every one of them as a drug and the share falls only from 69% to 63%.
  The third runs against it and is ``allergy_denied_but_drug``: **one encounter
  in 551**. Issue #78.
- ``allergy_unclassified`` is **the token lists' miss rate and not a category**.
  It is what makes a hand-written allergen list publishable here at all: a name
  the lists do not carry becomes a printed number rather than a silent
  misfiling. 16 of 173 against the corpus on 2026-08-16, and 0 of 8 against the
  committed inputs -- so the lists are audited on the fixtures and measured, not
  audited, on the corpus.
- ``\bppd\b`` is packs per day throughout this corpus and is also the standard
  abbreviation for a **purified protein derivative**, and a TB skin test written
  that way would count as a positive tobacco history. **Issue #78's audit is
  closed, and it was closed by shape rather than by reading** -- ruled by the
  clinician 2026-08-16. The premise everything here used to rest on, *"nothing
  can tell them apart"*, is false as written: the two senses are not the same
  shape. A pack count is a small number in front of the token and usually a span
  behind it. A skin test has no quantity in front at all -- it is placed, it is
  read, and its result is millimetres of induration. Nobody writes a tuberculin
  test as a number of packs followed by years.
- **The audit is printed rather than quoted**, so it is re-derivable by anyone
  with the corpus: ``with_bare_ppd``, ``bare_ppd_no_other_token`` and the two
  shape counters. 2026-08-16 over 551 encounters: **102 write a bare ``ppd``, 13
  carry no independent tobacco token** -- the only ones at risk, since the rest
  name a smoker whatever ``ppd`` means -- and of those 13, **13 read as a pack
  quantity and 0 as a skin test**. Four independent checks agree and none is the
  one the audit started from.
- **What that does not establish**, stated because the class name says so and the
  prose should too: nobody has read the encounters. It does not rule out a
  tuberculin test written in a shape both patterns miss. What makes that
  survivable is the bound rather than the discriminator -- charge all 13 as skin
  tests anyway and tobacco is still 159 of 197 positive, **81%**, so no reading
  of them can move issue #29's ruling. Do not confuse this 13 with issue #146's:
  that is the opposite condition on the same token, encounters writing a
  **welded** ``1ppd`` that ``\bppd\b`` cannot match at all.
- ``dob`` welded straight to its date, with no space between token and value,
  is the shape that defeated ``\\bht\\b`` for ``ht5'7"`` and it would not match
  here either. There is no instance of it in the corpus as of 2026-08-11, so
  the alternative is not carried; this is the line to change if one appears.
"""

from __future__ import annotations

import hashlib
import itertools
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8
from repo_root import scratch_root

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
# The British variant is deliberately not carried: this is an American corpus,
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

# An organism or a named disease entity: the thing whose ICD-10-CM descriptor
# would assert what a hedge says is not established. Added for issue #49, which
# needed a *candidate pool* rather than a claim -- ``fixtures/hedged-dx`` takes
# three encounters, and the set is a pick rather than a population, so the honest
# defense is that anyone can re-derive what it picked from.
#
# **It counts a co-occurrence, not a hedged organism.** The token may sit
# anywhere in the encounter: a history line, a resolved illness, a negative
# result. So it narrows ``HEDGE``'s 33 to something readable and settles nothing
# about any one of them -- reading the seventeen is what chose the three, and
# nothing here reproduces that judgment.
#
# **The list is deliberately short and deliberately frozen.** Every entry names
# a thing an ICD-10-CM descriptor can *confirm* -- an organism, or a disease no
# code calls "unspecified" -- because that is the only class drift row 13's
# second half fires on. Widening it changes the 17 that ``fixtures/hedged-dx``
# publishes, and the same rule ``HEDGE`` carries applies here: widen it
# deliberately, re-run, and update the figure the set cites. Do not widen it in
# passing.
#
# Four rejections worth recording, because each was in a draft:
#
# - ``\bpe\b`` for pulmonary embolism. "pe" hides in nothing useful at a word
#   boundary, but the corpus writes ``PE`` for *physical exam* and for *peak
#   expiratory*, and neither is a disease. The cost of keeping it was a pool
#   nobody could trust; the cost of dropping it is a missed candidate.
# - ``\bbv\b`` for bacterial vaginosis, on the same reasoning inverted -- it is
#   unambiguous and it is also in a history line in half its appearances, so it
#   inflated the pool with encounters whose hedge was somewhere else entirely.
# - ``\bca\b`` for cancer. It is this clinician's abbreviation for *cancer* in a
#   family history and also the chemical symbol he writes for calcium in a lab
#   panel. Nothing separates them.
# - ``c diff``. The space makes it a two-token match that ``\b`` handles badly
#   next to ``c/diff`` and ``cdiff``, and the corpus holds no hedged instance.
#
# **Two entries shipped broken and a code review caught both**, which is worth
# recording because each was broken in a way the paragraph above had already
# named and neither changed the count:
#
# - ``h pylori`` was carried as a bare two-token match -- the exact shape
#   ``c diff`` was **rejected** for one bullet up. ``H. pylori`` is the dominant
#   written form and it did not match, so the alternative was inert against the
#   form it exists for. Now ``h\.?\s*pylori``, which takes all four spellings.
# - ``factor v`` had no trailing ``\b``, so it matched ``factor vii`` and
#   ``factor viii`` -- ordinary coagulation panel entries and not the hereditary
#   thrombophilia meant. This is ``OBESITY``'s lesson exactly, in the one
#   alternative that was written without it.
#
# **The pool read 17 before both repairs and 17 after**, measured 2026-08-15, so
# ``fixtures/hedged-dx``'s published figure is unaffected. **That is luck rather
# than vindication** and it is the reason to write the repairs down: an
# alternative that matches nothing and an alternative that matches too much both
# look identical from a count that did not move.
#
# **It is neither a floor nor a ceiling**, on ``HEDGE``'s terms. It over-counts,
# because a token anywhere in the encounter counts and the hedge may be
# somewhere else entirely -- a resolved illness in a history line, a negative
# result, a family member's diagnosis. It under-counts, because the list is
# short by construction: **abscess**, **sepsis**, **tick-borne**, **fungal**,
# **parasit**, **viral** and every organism nobody in this corpus has written
# yet are all absent. Quote it as a candidate pool, never as a population.
#
# **``mycoplasma`` was missing from the first version of this list and the pool
# was published without it**, which is worth recording rather than quietly
# fixing. It is the organism ``fixtures/hedged-dx`` is built on: two of that
# set's three cases hedge it by name. Both were still in the pool, because case
# 1 carries a sibling's ``strep`` and case 3 lists ``strep, flu and COVID`` as
# negatives -- so **the omission was invisible from the set's own membership**
# and only showed up when a unit test asserted the bare diagnosis line
# ``dx CAP likely mycoplasma`` against it. A pool that admits the right cases
# for the wrong reason looks exactly like one that works.
#
# **Adding it moved the figure not at all -- 17 before and 17 after**, measured
# 2026-08-15, because every encounter in this corpus that hedges mycoplasma also
# writes another organism somewhere. So ``fixtures/hedged-dx``'s published pool
# stands as written. That the count is unchanged is the reason to record the
# repair here rather than to leave it implied by a regex nobody rereads.
ORGANISM_SPECIFIC = re.compile(
    r"(?i)\b(strep|flu\b|influenza|covid|mono\b|monospot|pneumon|mycoplasma"
    r"|uti\b|pyelo|cellulit|shingle|zoster|herpes|hsv|rsv|pertussis|lyme"
    r"|h\.?\s*pylori|gono|chlam|trich|staph|mrsa|scabies|impetigo|osteomyel"
    r"|appendic|divertic|dvt|von will|factor v\b)"
)

# A duration expression, and a symptom vocabulary to read one *beside*. Added for
# issue #65, which needed a **candidate pool** rather than a claim, the way #49
# did -- ``fixtures/duration-span`` takes three encounters out of what this
# prints, and the set is a pick rather than a population.
#
# **The distinction drift row 16 turns on is not in here and cannot be.** That
# row separates two durations written about *different* symptoms -- which is not
# a conflict and is fixtured as day-b's B10 -- from two written about the
# **same** symptom, which is the conflict a span resolves. Deciding which is
# reading, not matching: the second statement may name its symptom, may use a
# pronoun, and may or may not carry the new-or-worse marker that redirects the
# pronoun to a newer complaint. So what this prints is a pool to read, and every
# figure quoted from it says so.
#
# **It over-counts in two ways, each with a worked example in the test file.**
# day-b's cases 8 and 9 are the attribution limb -- two durations about two
# symptoms, no conflict and no span -- and both are in the pool. And a treatment
# sig lands inside the window of the symptom it treats, so ``zithromax ... x 3
# days`` beside a cough counts. **Both are kept rather than filtered.** A filter
# that excluded them would need row 16's own judgment, and one tuned until it
# returned exactly the three cases picked would read as recomputable while
# proving nothing -- which ``fixtures/README.md`` refuses by name.
#
# **A restatement that agrees is excluded, and only by its value.** Two mentions
# of one interval are one timeline, so day-b's case 4 -- ``x 5 days`` written
# three times -- is out. **day-b's case 12 is out by luck**: it writes ``started
# saturday`` and then ``started saturdy``, which are two different strings, and
# what excludes it is that no symptom sits within the window of the typo. Put
# one there and the pool admits an encounter agreeing with itself. This cannot
# spell-normalize, and normalizing would be guessing which spelling was meant.
#
# **It under-counts in two ways, and both are deliberate rather than missed.**
#
# A timeline anchored to a weekday or a holiday -- ``started saturday``, ``since
# christmas eve`` -- is matched here, but an encounter whose two statements are
# *both* anchors resolves only against the visit date, which a fixture removes,
# so nothing downstream can use one. The pool holds them and the set's README
# records why none was picked.
#
# **The year scale is outside this entirely**: no ``year``, ``yr`` or ``yrs``
# unit appears above. Nothing in this corpus writes an acute onset in years, and
# a year-scale interval here is a smoking history, a surgery or a chronic
# condition -- so admitting the unit would widen the figure to buy those. **What
# it costs is real**: a chronic pain dated two ways in years is a same-symptom
# conflict this pool cannot see, and ``clinical-note``'s own corroboration for
# the span form -- the clinician's ``11-12 yrs ago`` -- is a string this regex
# does not match. ``test_corpus_census.py`` pins both.
#
# The window is 45 characters either side, chosen against this corpus's line
# lengths and not derived from anything.
#
# **43 of 551 encounters, 8%, measured 2026-08-15** -- the figure
# ``fixtures/duration-span`` publishes, and all 43 were read one at a time to
# pick its three. Widen the window, the duration units or the symptom list
# deliberately, re-run, and update that figure -- do not widen any of them in
# passing. ``HEDGE`` carries the same rule for the same reason.
#
# **Re-deriving it needs the main checkout.** ``scratch/`` is gitignored and a
# worktree does not get one, so running this from a worktree finds no corpus.
# That is issue #93's subject on ``phi_scan``'s side and it bites here too.
DURATION = re.compile(
    r"(?i)\b("
    r"x\s*\d+\s*(?:-\s*\d+\s*)?(?:day|days|d|week|weeks|wk|wks|month|months|mo)\b"
    r"|\d+\s*(?:-\s*\d+\s*)?\s*(?:day|days|week|weeks|wk|wks|month|months|mo)\b"
    r"|yesterday|last night|overnight|this morning"
    r"|start(?:ed|ing)\s+(?:on\s+)?(?:mon|tues|wednes|thurs|fri|satur|sun)\w*"
    r"|since\s+(?:mon|tues|wednes|thurs|fri|satur|sun)\w*"
    r")"
)

# The complaints a duration in this corpus is written beside. Short and frozen,
# on ``ORGANISM_SPECIFIC``'s rule: it decides the pool's size, so widening it
# changes a published figure.
DURATION_SYMPTOM = re.compile(
    r"(?i)\b(cough|fever|congestion|sneez\w*|sore throat|throat|headache|ha\b"
    r"|earache|ear pain|rash|pain|nausea|vomit\w*|diarrhea|dizz\w*|weakness"
    r"|swelling|drainage|discharge|sinus|chest|abd\w*|back|knee|shoulder"
    r"|wheez\w*|sob\b|itch\w*|burn\w*)\b"
)

DURATION_WINDOW = 45


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
# **A note writing both is counted as none. No committed case does, and 17
# corpus encounters do** -- measured 2026-08-16 on issue #78, and the branch is
# no longer untested. ``NKDA`` means no known *drug* allergy and coexists with a
# seasonal one, so "nkda, seasonal allergies" is a real shape. **All 17 name an
# environmental allergen and none names a drug or a food one**, so every one of
# them is counted as saying none *correctly* -- ``NKDA`` is exactly what those
# notes mean. #78's body predicted this would make the allergy figure "a slight
# over-count of the gap reading" and it does not: it is the clinician writing the
# drug-allergy denial beside a non-drug allergy 17 times, which is the same
# reading he gave on 2026-08-16 and is corpus evidence for it rather than
# against.
#
# **Three denial longhands were read as *stated allergens* until 2026-08-16**,
# because the qualifier between the negation and the word broke the adjacency
# every alternative here required: "no drug allergies", "denies drug allergies",
# "denies any medication allergies". Two corpus encounters were affected. The
# cost of leaving it was not the two: it was that ``ALLERGY_DRUG``'s generic
# ``drug allerg`` form then read those denials as a **named drug allergen** --
# the strongest possible evidence against the ruling the column exists to
# support, manufactured out of a denial. Found by the standards review on #78.
#
# **The gap is a named qualifier list and not ``\w+``, and that is the whole
# care in this fix.** An arbitrary-word gap reads "no dm seasonal allergies" as a
# denial of the seasonal allergy, because nothing in a regex can tell that the
# negation belongs to the diabetes. That shape costs nothing on today's corpus --
# the widening moves the count by exactly the 2 real denials either way -- so it
# would have been a latent wrong branch, kept out by measurement rather than
# found by one. A comma already blocks the run-on: ``\w+\s+`` cannot cross the
# comma in "no fever, seasonal allergies".
ALLERGY_NEGATION_QUALIFIER = (
    r"(?:known|any|other|new|current|active|significant|true|reported"
    r"|history|hx|of|drugs?|meds?|medications?|medicine|food|foods"
    r"|environmental|seasonal|latex|pcn|penicillin)"
)

ALLERGY_NONE = re.compile(
    r"(?i)\bnkda\b|\bnka\b"
    r"|\b(?:no|denies|denied|denying)\s+"
    r"(?:" + ALLERGY_NEGATION_QUALIFIER + r"\s+){0,3}allerg"
    # The ``hx`` limb takes an unrestricted filler where the others do not, and
    # ``hx`` is what earns it: "no <anything> hx allergies" is a denial whatever
    # the filler is, because the history word anchors the negation to the
    # allergy rather than to the filler. Both corpus encounters this fix is for
    # write a filler that is in no qualifier list -- found by counting, since
    # printing the word would be printing note text.
    r"|\b(?:no|denies|denied|denying)\s+(?:\w+\s+){0,2}(?:hx|history)\s+"
    r"(?:of\s+)?(?:" + ALLERGY_NEGATION_QUALIFIER + r"\s+){0,2}allerg"
    r"|\ballerg\w*\s*[:\-]?\s*(?:none|neg\w*|denie[sd])\b"
)

# Issue #78. Which *kind* of allergy the slot named, once it named one.
#
# **This is the column the ruling turns on, and until #78 it was one column.**
# ``NKDA`` is *no known drug allergy*: a patient with hay fever is NKDA, so a
# note naming a seasonal allergy is fully compatible with filling ``NKDA`` and is
# no evidence at all against the gap reading. The corpus run #78 was owed came
# back **173 of 284 written statuses naming something**, which fires that
# ticket's own reopen trigger -- against a fixture floor where most of the column
# names nothing but an environmental allergy. **The figures are in this module's
# docstring and deliberately not repeated here**, on #143's terms: they moved when
# #143 widened the denominator, and this comment is a third place for them to go
# stale in. So the trigger fired on a count that could not tell the two apart.
# The clinician ruled on 2026-08-16 that
# an environmental-only note still takes ``NKDA``, and named **food** as the
# third category, which is what ``DAVID`` checks.
#
# **The window runs from one word before the allergy token to the end of its
# sentence *or* the end of its line, whichever comes first** -- ``[^.\n]*``, and
# the line limb matters as much as the sentence one, because this shorthand
# writes a whole history as one unpunctuated line and a whole plan as another.
# That is what keeps a prescribed drug out of the allergen column: day-b case 11
# writes ``allergies: seasonal allergies, levaquin`` and then proposes bactrim in
# its plan, so a note-wide match would read every antibiotic prescribed anywhere
# as an allergen -- and would put an ``NKDA`` case in the drug column the moment
# anything was prescribed. One word back is what catches the allergen written
# *before* the token (``peanut allergy``, ``seasonal allergies``) rather than
# after it (``allergic to prednisone``); those are the only two positions an
# allergen occupies. It is also what excludes ``lactose intollaerance seasonal
# allergies`` in ``fixtures/peds-bp/shorthand/case-05.md`` -- an intolerance is
# not an allergy, and it falls outside the window structurally rather than by an
# exclusion someone had to think of.
#
# **What the window cannot do is tell an allergen from a medication written
# beside it on the same line.** ``allergic rhinitis on zyrtec`` reads as a drug
# allergy, and so does ``allergies: seasonal, meds: lisinopril``. There is no fix
# inside a regex, and the ``unclassified`` column does not help -- that failure
# lands a note in the wrong bucket rather than in none. It runs one way only:
# it inflates ``allergy_drug`` and so deflates ``allergy_no_drug``, which is what
# lets that figure be published as a floor.
#
# **A stated allergy matching none of the three is counted ``unclassified``, and
# that is what makes a token list publishable at all.** These lists are common
# allergen classes and nothing more; a name they miss becomes a printed number
# instead of a silent misfiling, so the lists' quality is measurable from the
# report rather than taken on trust.
ALLERGY_WINDOW = re.compile(r"(?i)(?:\S+\s+)?(?:\ballerg|\bnkda\b|\bnka\b)[^.\n]*")

ALLERGY_ENVIRONMENTAL = re.compile(
    r"(?i)\bseasonal\b|\benvironmental\b|\bpollen\b|\bragweed\b|\bhay\s*fever\b"
    r"|\bdust\b|\bmites?\b|\bmold\b|\bdander\b|\bgrass\b|\blatex\b"
    r"|\bbees?\b|\bwasps?\b|\bhornets?\b|\binsect\b|\bstings?\b"
    r"|\badhesive\b|\bnickel\b|\bcats?\b|\bdogs?\b|\banimals?\b"
)

# ``\bnuts?\b`` rather than a bare ``nut``, which would match "nutrition". No
# committed input names a food allergen, so every alternative here is untested
# against a real case rather than wrong -- the clinician named the category.
ALLERGY_FOOD = re.compile(
    r"(?i)\bfoods?\b|\bpeanuts?\b|\bnuts?\b|\bshellfish\b|\bshrimps?\b"
    r"|\bcrab\b|\blobster\b|\bfish\b|\beggs?\b|\bmilk\b|\bdairy\b|\bsoy\b"
    r"|\bwheat\b|\bgluten\b|\bsesame\b|\bstrawberr|\btomato|\bchocolate\b"
    r"|\bmango\b|\bbanana\b|\bavocado\b|\bgelatin\b"
)

# Seeded from the allergens the committed inputs name -- prednisone, bactrim,
# doxy, zyrtec, noroxin, pyridium, levaquin -- and widened to the classes a
# primary-care allergy list carries. It is a list, so it is incomplete by
# construction; ``unclassified`` is where that incompleteness is reported.
ALLERGY_DRUG = re.compile(
    # The generic forms are spelled as the whole phrase on purpose. A bare
    # ``\bmeds?\b`` would fire on the ``meds:`` line the shorthand writes beside
    # the allergy one, and a bare ``\bdrugs?\b`` on the shared social denial
    # "no smoke, drink, drugs" -- two of the commonest lines in this corpus.
    r"(?i)(?:drug|medication|med|antibiotic|abx)\w*\s+allerg"
    r"|\ballergic\s+to\s+(?:a\s+|an\s+)?(?:drug|medication|antibiotic)"
    r"|\bantibiotics?\b"
    r"|\bpenicillins?\b|\bpcn\b|\bamoxicillin\b|\baugmentin\b|\bampicillin\b"
    r"|\bcephalexin\b|\bkeflex\b|\bceftriaxone\b|\brocephin\b|\bcephalosporin"
    r"|\bsulfa\w*\b|\bbactrim\b|\bseptra\b|\btmp\b"
    r"|\bdoxy\w*\b|\btetracycline\b|\bminocycline\b"
    r"|\bazithromycin\b|\bzithromax\b|\bz-?pak\b|\berythromycin\b|\bclindamycin\b"
    r"|\blevaquin\b|\blevofloxacin\b|\bcipro\w*\b|\bmoxifloxacin\b|\bavelox\b"
    r"|\bnorfloxacin\b|\bnoroxin\b|\bfluoroquinolone\w*\b"
    r"|\bnitrofurantoin\b|\bmacrobid\b|\bvancomycin\b|\bmetronidazole\b|\bflagyl\b"
    r"|\bprednisone\b|\bprednisolone\b|\bsteroids?\b"
    r"|\bmorphine\b|\bcodeine\b|\bhydrocodone\b|\boxycodone\b|\bpercocet\b"
    r"|\bvicodin\b|\btramadol\b|\bdilaudid\b|\bhydromorphone\b|\bfentanyl\b"
    r"|\bdemerol\b|\bmeperidine\b|\bopioids?\b|\bopiates?\b"
    r"|\bnsaids?\b|\bibuprofen\b|\bmotrin\b|\badvil\b|\bnaproxen\b|\baleve\b"
    r"|\btoradol\b|\bketorolac\b|\baspirin\b|\basa\b"
    r"|\bacetaminophen\b|\btylenol\b|\bstatins?\b|\blisinopril\b"
    r"|\bmetformin\b|\bgabapentin\b|\blithium\b|\bphenytoin\b|\bdilantin\b"
    r"|\blamotrigine\b|\blamictal\b|\bcarbamazepine\b|\btegretol\b"
    r"|\ballopurinol\b|\bwarfarin\b|\bheparin\b|\blovenox\b"
    r"|\bcontrast\b|\biodine\b|\bgadolinium\b|\bdye\b"
    r"|\blidocaine\b|\bnovocaine\b|\banesthesia\b|\bpropofol\b"
    r"|\bbenadryl\b|\bdiphenhydramine\b|\bzyrtec\b|\bcetirizine\b"
    r"|\bclaritin\b|\bloratadine\b|\bpyridium\b|\bphenazopyridine\b"
    r"|\bzofran\b|\bondansetron\b|\breglan\b|\bmetoclopramide\b"
    r"|\bprilosec\b|\bomeprazole\b"
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

# Every way this corpus names tobacco **except** a bare ``ppd``. Written once and
# composed into both patterns rather than spelled twice, because the ``ppd``
# audit below needs exactly "the slot, minus the ambiguous token" and a second
# copy of the list is a second thing to keep in step.
TOBACCO_NOT_PPD = (
    r"\btobacco\b|\bsmok|\bnon-?smok"
    r"|" + PACK_PER_DAY +
    r"|\bvap(?:e|es|er|ing)\b|\bnicotine\b|\bcigarette"
    r"|\bchew(?:s|ing)?\s+tobacco|\bdips?\s+now\b|\bsnuff\b(?!\s*box)"
)

TOBACCO_SLOT = re.compile(r"(?i)\bppd\b|" + TOBACCO_NOT_PPD)

TOBACCO_INDEPENDENT = re.compile(r"(?i)" + TOBACCO_NOT_PPD)

PPD_TOKEN = re.compile(r"(?i)\bppd\b")

# Issue #78's audit, and the pair that settles it. A packs-per-day quantity and a
# purified protein derivative are the same three letters, but they are **not the
# same shape**, and the shape is decidable without reading an encounter.
#
# A pack count is a small number in front of the token and usually a span behind
# it -- "0.5 ppd x 15 yrs". A skin test has no quantity in front: it is placed,
# it is read, and its result is millimetres of induration. **Nobody writes a
# tuberculin test as a number of packs followed by years**, which is what makes
# this a discriminator rather than a guess.
PPD_AS_QUANTITY = re.compile(
    r"(?i)(?:\d|\.\d|<|>|half|quarter|one|two|three)\s*-?\s*ppd\b"
    r"|\bppd\b\s*(?:x|for|since|@)\s*\d"
)

# ``(?<![a-z])mm\b`` rather than ``\bmm\b``, and it is this module's own named
# failure class arriving again. ``\bmm\b`` cannot match inside "12mm" -- the
# leading boundary needs a non-word character and a digit is a word character,
# which is exactly what defeated ``\bht\b`` for "ht5'7"" and what defeats
# ``\bppd\b`` for "1ppd" (issue #146). **An induration is written welded to its
# number more often than not**, so the plain boundary would have missed the
# commonest form of the very thing this pattern exists to find, and the audit
# would have reported zero skin tests for the wrong reason. Caught by a test.
PPD_AS_SKIN_TEST = re.compile(
    r"(?i)\bppd\b[^.\n]{0,25}(?<![a-z])mm\b|(?<![a-z])mm\b[^.\n]{0,25}\bppd\b"
    r"|\bindurat"
    r"|\bppd\b[^.\n]{0,15}\b(?:placed|planted|read|applied)\b"
    r"|\btuberculosis\b|\bquantiferon\b|\bmantoux\b|\bppd\b[^.\n]{0,15}\btb\b"
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
# as a ten-year-old. Nobody is proposing to remove the anchors; what the anchors
# *cost* is the question, and it is now printed rather than asserted -- see
# ``AGE_AND_SEX_OFF_LINE`` below and the ``off-line form`` line of the report.
AGE_AND_SEX_LINE = re.compile(r"(?im)^\s*(\d{1,3})\s*(?:yo|y/o)?\s*[mf]\b\.?\s*$")

# The same body with the anchors taken off, and **the only pattern in this file
# that measures the extractor instead of the corpus**. Issue #64.
#
# It exists because the claim it replaces was true and uncheckable at once. The
# comment above used to read: *"Audited 2026-08-11: exactly three digit+sex
# matches in the corpus sit anywhere other than alone on a line, and all three
# are decoys -- two doses, and the 'f/u' follow-up token taking the 'f'. No
# encounter loses an age to it."* That audit was produced by the census auditing
# itself, which is ADR 0001's objection, and #64 was filed on it.
#
# **The audit was right and the ticket was still right to distrust it.** Four
# readings of "a digit+sex match" over the same corpus gave 38, 36, 36 and 2, and
# the stated three was none of them; the number only reproduces once you know it
# meant *same line, in encounters stating no age at all*. That reading is what is
# coded here, and the figure now comes out of a run. A claim that happens to be
# correct but that nobody can re-derive looks exactly like #56's -- 52 codes and
# 11 unspecified, published against real figures of 106 and 23, because a
# line-shape assumption matched half a set and reported a plausible number.
#
# **It is a ceiling and it is meant to over-report.** ``t 98 F`` is a Fahrenheit
# temperature and is counted; so is a dose. Padding a ceiling with decoys keeps
# it a true bound, and a tighter figure that excluded them would be an estimate
# wearing a count's clothes. Read the encounters to convert it into a finding --
# that is PHI and it is the clinician's, which is exactly why the *count* has to
# be runnable by someone who cannot.
#
# **``[ \t]`` rather than ``\s``, ruled 2026-08-15, and it is not a tidy.** A
# date of birth in this corpus is always a month, a day and a year, so the final
# component of a ``dob`` line is a two-digit year and can never be an age -- and
# under ``\s`` that year pairs with the "f" of an ``f/u`` beginning the *next
# line* and prints a fourth encounter that lost nothing, its age having never
# been on a line for the anchor to reject. The anchored form cannot span a line
# by construction, so neither may the thing measuring it. One encounter in the
# corpus has exactly this shape; ``test_corpus_census.py`` carries an invented
# date of the same shape rather than that one.
#
# **Nothing may wire this into ``has_stated_age`` or ``age_in_years``.** The
# moment it feeds a figure it stops being independent of the extractor it
# measures, and the self-audit is back;
# ``test_the_ceiling_is_not_wired_into_the_age_extractors`` is what fails.
#
# **The three, read by hand 2026-08-15 with the clinician's authorization.** All
# decoys; no encounter loses an age. Two are drug doses -- one a mistyped
# milligram abbreviation, one a bare antibiotic strength -- and the third is a
# written visit date. In two of the three the "f" belongs to a follow-up token,
# which is the form the anchor most has to reject. Only the verdict was
# published: no note text, name or date literal was written anywhere from that
# read, which is the standing rule and also why this description names shapes
# rather than quoting them.
#
# That inventory is stated once and repeated nowhere. A first draft of this
# change carried three descriptions of the same three encounters across two
# files and they disagreed on how many were doses and on whether a temperature
# was among them -- a change whose whole purpose is re-derivability, shipping
# three readings of its own headline figure. ``test_corpus_census.py`` cites
# this comment rather than restating it.
#
# **#36's hand count is the wrong measurement, and this is what settles it.**
# That ticket read the demographic line as stating an age in 84% of encounters
# against this census's 65%, and as writing *both* an age and a birth date in
# 15% -- about 82 encounters -- against a census figure of 6. It named the line
# anchor as one of the two things that could explain the gap, and #64 is the
# half that was split out to test it. It cannot: a 19-point gap is roughly 105
# encounters and the ceiling above is **3**, so the anchor is two orders of
# magnitude too small to be the cause. The remainder is not hiding in another
# shape either -- measured 2026-08-15 across the 194 encounters stating no age:
# a sex-first ``F 45`` returns 1, a bare number alone on a line returns 2, and
# ``age: 45`` returns 0. **The spelled sex word returns 0 in all three of its
# orderings** -- ``female 45``, ``45 female`` and a welded ``45female`` -- and
# all three were run, because naming only one of them is how a sweep reports
# coverage it does not have. This whole ticket is what an unstated reading
# costs.
#
# **The spelled form is nonetheless this ceiling's blind spot, and the count
# being zero is not the same as the ceiling covering it.** ``[mf]\b`` cannot
# match "female" -- the boundary fails against the "e" -- so ``51 female`` is
# invisible to ``has_stated_age`` *and* to the ceiling that is published as
# bounding what ``has_stated_age`` costs. Should such a form ever appear, the
# report would go on printing a small number and nothing would say otherwise.
# It is left uncarried rather than fixed in passing, on ``HEDGE``'s rule: widen
# deliberately, re-run, and update every figure that cites it. That the
# clinician spells the word somewhere is not hypothetical -- ``AGE_UNDER_ONE``
# accepts ``male``/``female`` and was written against the corpus.
#
# And the clinician ruled it directly the same day: a date of birth here is
# always a month, a day and a year, and he writes **a birth date or an age and
# a sex letter, not both**. A corpus charted that way has almost no "both",
# which is the census's 6 and not the hand count's 82. The hand count was a
# human reading 130 rendered pages and it miscounted the *split*; its total for
# birth dates corroborates the census, which is exactly what that error looks
# like. #36 is closed and this is recorded here rather than reopened.
AGE_AND_SEX_OFF_LINE = re.compile(r"(?i)(\d{1,3})[ \t]*(?:yo|y/o)?[ \t]*[mf]\b\.?")

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


def allergy_windows(note: str) -> list[str]:
    """The spans a named allergen can occupy. See ``ALLERGY_WINDOW``. Issue #78."""
    return ALLERGY_WINDOW.findall(note)


def _allergy_kind(note: str, pattern: re.Pattern) -> bool:
    """A kind fires only where the slot named something, and only in a window.

    Gated on ``has_stated_allergy`` rather than left open, so the three kinds
    partition the same population the report subtracts ``unclassified`` from --
    and so ``no known drug allergies`` cannot be read as naming a drug, which is
    the collision ``ALLERGY_DRUG``'s generic ``drug allerg`` form invites.

    **The gate is not sufficient on its own, and saying so is the point.** It
    only helps where ``ALLERGY_NONE`` recognised the denial; where that pattern
    missed one -- as it did for "no drug allergies" until 2026-08-16 -- the gate
    opens and the denial is read as a named drug allergen. The fix had to be in
    ``ALLERGY_NONE``, and this docstring claimed the gate was the whole of it.
    """
    if not has_stated_allergy(note):
        return False
    return any(pattern.search(w) for w in allergy_windows(note))


def has_drug_allergy(note: str) -> bool:
    """A named drug allergen -- the only kind ``NKDA`` speaks to. Issue #78."""
    return _allergy_kind(note, ALLERGY_DRUG)


def has_food_allergy(note: str) -> bool:
    """A named food allergen. The category the clinician added on 2026-08-16."""
    return _allergy_kind(note, ALLERGY_FOOD)


def has_environmental_allergy(note: str) -> bool:
    """A named environmental allergen; seasonal allergies are the corpus's form."""
    return _allergy_kind(note, ALLERGY_ENVIRONMENTAL)


def has_unclassified_allergy(note: str) -> bool:
    """Named something the three lists do not carry. The lists' miss rate."""
    return has_stated_allergy(note) and not (
        has_drug_allergy(note)
        or has_food_allergy(note)
        or has_environmental_allergy(note)
    )


def denies_allergies_but_names_a_drug(note: str) -> bool:
    """A denial that names a drug allergen anyway -- "nkda except penicillin".

    **The one error that pushes against ``allergy_no_drug`` rather than with
    it**, and the reason that figure can be called a floor at all. Everything
    else miscounts in the safe direction: ``ALLERGY_DRUG`` over-matches, and an
    unclassified note might be a drug. This is the shape that would quietly put a
    real drug allergy on the *no drug* side, and issue #78's body named it as the
    branch nothing had measured -- *"if the corpus has some, the allergy figure
    is a slight over-count of the gap reading"*. It has one. Measured 2026-08-16.

    Counted separately rather than folded into ``ALLERGY_NONE``, because a note
    denying drug allergies and then naming one is a contradiction in the source
    and not a classification this tool gets to resolve.
    """
    if has_stated_allergy(note) or not has_allergy_status(note):
        return False
    return any(ALLERGY_DRUG.search(w) for w in allergy_windows(note))


def has_tobacco_status(note: str) -> bool:
    """The tobacco slot was written, whatever it says. Issue #29."""
    return bool(TOBACCO_SLOT.search(note))


def has_positive_tobacco(note: str) -> bool:
    """A tobacco history, past or present, or a second-hand exposure.

    The complement over the notes writing the slot at all is the denial count,
    and that ratio is what tells this slot apart from the allergy one.
    """
    return bool(TOBACCO_POSITIVE.search(note))


def writes_bare_ppd(note: str) -> bool:
    """A ``ppd`` the token boundary can see. Issue #78's audit population.

    Deliberately the same ``\\bppd\\b`` the tobacco patterns use, welded forms and
    all -- so it counts what those patterns count and not what they miss, which
    is issue #146's separate finding.
    """
    return bool(PPD_TOKEN.search(note))


def has_independent_tobacco(note: str) -> bool:
    """Names tobacco without using ``ppd``. The audit's exclusion."""
    return bool(TOBACCO_INDEPENDENT.search(note))


def ppd_written_as_quantity(note: str) -> bool:
    """A pack count -- a small number in front, usually a span behind."""
    return bool(PPD_AS_QUANTITY.search(note))


def ppd_written_as_skin_test(note: str) -> bool:
    """A tuberculin test -- placed, read, and measured in millimetres."""
    return bool(PPD_AS_SKIN_TEST.search(note))


def has_hedge(note: str) -> bool:
    """A token marking something as suspected rather than established.

    A ceiling on hedged diagnoses rather than a count of them -- see ``HEDGE``
    for what it cannot separate, and for the three decoys it does reject.
    """
    return bool(HEDGE.search(note))


def has_organism_specific(note: str) -> bool:
    """An organism or named disease anywhere in the encounter.

    Not "the hedge is on an organism" -- see ``ORGANISM_SPECIFIC``. Paired with
    ``has_hedge`` it prints the candidate pool ``fixtures/hedged-dx`` drew from,
    and it is that pool rather than that set's three cases which is meant to be
    re-derivable.
    """
    return bool(ORGANISM_SPECIFIC.search(note))


def duration_mentions(note: str) -> list[tuple[str, frozenset[str]]]:
    """Every duration in a note, with the symptoms written within the window.

    Returns the duration text normalized to lowercase single spaces, so two
    spellings of one interval do not read as two values, paired with the
    symptom vocabulary found either side of it. Emits no note text beyond the
    duration itself and the fixed vocabulary in ``DURATION_SYMPTOM``.
    """
    mentions: list[tuple[str, frozenset[str]]] = []
    for match in DURATION.finditer(note):
        low = max(0, match.start() - DURATION_WINDOW)
        high = min(len(note), match.end() + DURATION_WINDOW)
        nearby = {m.group(1).lower() for m in DURATION_SYMPTOM.finditer(note[low:high])}
        text = re.sub(r"\s+", " ", match.group(1).strip().lower())
        mentions.append((text, frozenset(nearby)))
    return mentions


def restates_a_duration(note: str) -> bool:
    """Two **different** durations written beside a symptom they share.

    The candidate pool ``fixtures/duration-span`` drew from, and a pool rather
    than a count -- ``DURATION`` says at length what it cannot separate. Two
    mentions of the *same* interval are one timeline however often it is
    written, so the durations must differ; and they must share a symptom, which
    is what keeps a tobacco history and a surgical date out.
    """
    pairs = itertools.combinations(duration_mentions(note), 2)
    return any(
        text != other_text and symptoms & other_symptoms
        for (text, symptoms), (other_text, other_symptoms) in pairs
    )


def has_any_vital(note: str) -> bool:
    return has_bp(note) or has_height(note) or has_weight(note) or has_other_vitals(note)


def has_stated_age(note: str) -> bool:
    return bool(
        AGE_IN_YEARS.search(note)
        or AGE_UNDER_ONE.search(note)
        or AGE_AND_SEX_LINE.search(note)
    )


def could_have_lost_an_age_to_the_anchor(note: str) -> bool:
    """A ceiling on what ``AGE_AND_SEX_LINE``'s anchors cost this encounter.

    True where the note states no age by any of the three readings **and**
    carries a digit-plus-sex form somewhere on a line with something else. Both
    halves are load-bearing:

    - Without the first, this counts ``f/u`` tokens rather than lost ages. Most
      encounters carrying an off-line digit+sex form state their age plainly
      somewhere else, so nothing was lost and nothing is at risk. **No figure
      is quoted for that here on purpose**: it would be an undated prose count
      the report does not print, which is the defect issue #64 was filed on and
      would be a poor thing to reintroduce in its fix.
    - Without the second there is no candidate at all.

    Because ``has_stated_age`` is false here, ``AGE_AND_SEX_LINE`` matched
    nothing in this note, so every ``AGE_AND_SEX_OFF_LINE`` hit is necessarily
    off-line and no span bookkeeping is needed to say so.

    **It over-reports on purpose** -- see ``AGE_AND_SEX_OFF_LINE``. Converting
    the ceiling into a finding means reading the encounters, which is PHI; the
    count is here so that the part which does not require reading can be run by
    anyone, on any corpus, without a dated promise in a comment.
    """
    return not has_stated_age(note) and bool(AGE_AND_SEX_OFF_LINE.search(note))


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
    no_age_with_off_line_form: int = 0
    with_obesity: int = 0
    obesity_no_measurement: int = 0
    with_bariatric: int = 0
    bariatric_no_measurement: int = 0
    with_sleep_apnea: int = 0
    sleep_apnea_no_measurement: int = 0
    with_hedge: int = 0
    hedge_with_organism: int = 0
    restating_a_duration: int = 0
    with_pain_score: int = 0
    with_hypertension: int = 0
    hypertension_with_bp: int = 0
    hypertension_bp_normal: int = 0
    hypertension_bp_normal_lenient: int = 0
    with_allergy_status: int = 0
    allergy_status_none: int = 0
    allergy_drug: int = 0
    allergy_food: int = 0
    allergy_environmental: int = 0
    allergy_unclassified: int = 0
    allergy_denied_but_drug: int = 0
    with_bare_ppd: int = 0
    bare_ppd_no_other_token: int = 0
    bare_ppd_alone_as_quantity: int = 0
    bare_ppd_alone_as_skin_test: int = 0
    with_tobacco_status: int = 0
    tobacco_positive: int = 0

    @property
    def allergy_status_stated(self) -> int:
        """Written and naming something. Issue #29."""
        return self.with_allergy_status - self.allergy_status_none

    @property
    def allergy_no_drug(self) -> int:
        """Written, and naming no drug allergen. Issue #78, and the decisive row.

        ``NKDA`` is *no known drug allergy*, so this is the population the fill
        is right for -- the ``says none`` column plus every note whose only named
        allergen is a food or an environmental one. It is a **floor**, by two
        errors that both run the same way: ``ALLERGY_DRUG`` is a token list that
        cannot tell an allergen from a medication named in the same sentence, so
        ``allergy_drug`` is a ceiling, and any of ``allergy_unclassified`` that
        is really a drug belongs on the other side. Read the report's own worst
        case, which counts every unclassified note as a drug and still lands in
        the majority.
        """
        return self.with_allergy_status - self.allergy_drug

    @property
    def allergy_no_drug_worst_case(self) -> int:
        """``allergy_no_drug`` with every unclassified note charged as a drug.

        Printed rather than left to a reader, because the ruling survives it and
        a ruling that survives its own worst case is worth more than one quoted
        at its best. Issue #78.
        """
        return self.allergy_no_drug - self.allergy_unclassified

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
    def without_stated_age(self) -> int:
        """The population ``no_age_with_off_line_form`` bounds. Issue #64.

        Named rather than inlined so the report prints a ratio whose denominator
        is a field of this class -- the coverage assertion #64's own comment
        asked for, and the shape that would have failed #56 loudly at
        ``matched 6 of 12``.
        """
        return self.notes - self.with_stated_age

    @property
    def with_dob_instead_of_age(self) -> int:
        """A date of birth where no age is stated -- the "instead" in the claim."""
        return self.with_dob - self.with_both_age_and_dob


def survey(notes: list[str]) -> Census:
    bp_n = height_n = weight_n = other_n = no_vital_n = 0
    bp_weight_no_height_n = readings_n = readings_normal_n = 0
    age_n = dob_n = both_n = neither_n = off_line_n = 0
    obes_n = obes_bare_n = bar_n = bar_bare_n = osa_n = osa_bare_n = 0
    hedge_n = hedge_org_n = pain_n = restated_n = 0
    htn_n = htn_bp_n = htn_normal_n = htn_lenient_n = 0
    allergy_n = allergy_none_n = tobacco_n = tobacco_pos_n = 0
    allergy_drug_n = allergy_food_n = allergy_env_n = allergy_unclassified_n = 0
    allergy_denied_drug_n = 0
    ppd_n = ppd_alone_n = ppd_qty_n = ppd_skin_n = 0

    for note in notes:
        if has_hedge(note):
            hedge_n += 1
            hedge_org_n += has_organism_specific(note)

        restated_n += restates_a_duration(note)

        if has_allergy_status(note):
            allergy_n += 1
            allergy_none_n += not has_stated_allergy(note)
            # Not a partition: some committed cases name a drug *and* an
            # environmental allergen, so these three never get summed. No count
            # here -- it is the docstring's, and #143 is what a third copy
            # becomes.
            allergy_drug_n += has_drug_allergy(note)
            allergy_food_n += has_food_allergy(note)
            allergy_env_n += has_environmental_allergy(note)
            allergy_unclassified_n += has_unclassified_allergy(note)
            allergy_denied_drug_n += denies_allergies_but_names_a_drug(note)
        if writes_bare_ppd(note):
            ppd_n += 1
            if not has_independent_tobacco(note):
                ppd_alone_n += 1
                ppd_qty_n += ppd_written_as_quantity(note)
                ppd_skin_n += ppd_written_as_skin_test(note)

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
        off_line_n += could_have_lost_an_age_to_the_anchor(note)

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
        no_age_with_off_line_form=off_line_n,
        with_obesity=obes_n,
        obesity_no_measurement=obes_bare_n,
        with_bariatric=bar_n,
        bariatric_no_measurement=bar_bare_n,
        with_sleep_apnea=osa_n,
        sleep_apnea_no_measurement=osa_bare_n,
        with_hedge=hedge_n,
        hedge_with_organism=hedge_org_n,
        restating_a_duration=restated_n,
        with_pain_score=pain_n,
        with_hypertension=htn_n,
        hypertension_with_bp=htn_bp_n,
        hypertension_bp_normal=htn_normal_n,
        hypertension_bp_normal_lenient=htn_lenient_n,
        with_allergy_status=allergy_n,
        allergy_status_none=allergy_none_n,
        allergy_drug=allergy_drug_n,
        allergy_food=allergy_food_n,
        allergy_environmental=allergy_env_n,
        allergy_unclassified=allergy_unclassified_n,
        allergy_denied_but_drug=allergy_denied_drug_n,
        with_bare_ppd=ppd_n,
        bare_ppd_no_other_token=ppd_alone_n,
        bare_ppd_alone_as_quantity=ppd_qty_n,
        bare_ppd_alone_as_skin_test=ppd_skin_n,
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
        'claim: "about 7% carry neither" (both clinical-note step 1, and the',
        "   only two rows below that any skill quotes. batch-shift step 3 quoted",
        "   the other four until 2026-08-11 and now sends you to the file in",
        "   front of you instead; issue #36. read them as raw material)",
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
        'claim: "the line anchor on the bare \'51 f\' form costs no encounter',
        '        its age" (issue #64, replacing a dated prose audit that was',
        "   correct and unreproducible at once. a CEILING, not a count: every",
        "   digit+sex form on a line with something else, in an encounter that",
        "   states no age at all. a temperature and a dose are both counted, and",
        "   that padding is what makes it a true bound. reading them is what",
        "   turns it into a finding, and reading them is PHI)",
        f"  no age stated         {c.without_stated_age:>5}  "
        f"{_pct(c.without_stated_age, c.notes)}",
        f"  ...off-line form in   {c.no_age_with_off_line_form:>5}  "
        f"{_pct(c.no_age_with_off_line_form, c.without_stated_age)}"
        "  <- the most the anchor can be costing",
        "",
        'claim: "this catalog holds day files in which not one encounter states',
        '        an age" (clinical-note step 1, which is why it quotes no share)',
        'claim: "the mix differs so sharply between day files that a corpus-wide',
        '        share describes none of them" (batch-shift step 3; issue #36)',
        "  a day file states an age in every encounter, in none, or in some",
        f"  every encounter       {files.with_age_in_every_note:>5}  "
        f"of {files.unique_files}",
        f"  no encounter          {files.with_no_stated_age:>5}  of {files.unique_files}",
        f"  some                  {files.with_mixed_age:>5}  of {files.unique_files}",
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
        f"  beside an organism    {c.hedge_with_organism:>5}  "
        f"{_pct(c.hedge_with_organism, c.notes)}"
        "  <- fixtures/hedged-dx drew from here",
        "  (a co-occurrence, not a hedged organism - the pool issue #49 picked",
        "   three encounters out of, by reading them. the pool is re-derivable;",
        "   the pick is a judgment and the set's README says so)",
        "",
        'claim: "the corpus dates one symptom two ways" (drift row 16; issue #65)',
        f"  restated duration     {c.restating_a_duration:>5}  "
        f"{_pct(c.restating_a_duration, c.notes)}"
        "  <- fixtures/duration-span drew from here",
        "  (two different durations sharing a symptom - NOT the same-symptom",
        "   conflict row 16 turns on, which no regex decides. it counts day-b's",
        "   two attribution cases, and a treatment sig beside the symptom it",
        "   treats. read the pool, and see DURATION for what it misses)",
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
        "",
        "  the ppd audit (issue #78. ppd is packs per day and is also a",
        "   purified protein derivative, and the two are told apart by SHAPE:",
        "   a pack count has a small number in front and a span behind; a skin",
        "   test is placed, read, and measured in mm of induration)",
        f"    writes a bare ppd                {c.with_bare_ppd:>5}",
        f"    ...and no other tobacco token    {c.bare_ppd_no_other_token:>5}"
        f"  <- the only ones at risk",
        f"       of those, a pack quantity     {c.bare_ppd_alone_as_quantity:>5}",
        f"       of those, a skin test         {c.bare_ppd_alone_as_skin_test:>5}",
        "    established by form, not by reading an encounter",
        "",
        "  of those naming an allergy, which kind (issue #78. NKDA is no known",
        "   DRUG allergy, so only the first row is evidence against filling it.",
        "   a note may name two kinds - these NEVER sum to the column above)",
        f"    drug             {c.allergy_drug:>7}",
        f"    food             {c.allergy_food:>7}",
        f"    environmental    {c.allergy_environmental:>7}",
        f"    unclassified     {c.allergy_unclassified:>7}"
        f"  <- the token lists' misses, not a kind",
        f"  writes the slot and names NO drug allergen  "
        f"{c.allergy_no_drug:>5}  {_pct(c.allergy_no_drug, c.with_allergy_status)}",
        f"   worst case, every unclassified charged as a drug  "
        f"{c.allergy_no_drug_worst_case:>4}  "
        f"{_pct(c.allergy_no_drug_worst_case, c.with_allergy_status)}",
        f"   against it, a denial that names a drug anyway  "
        f"{c.allergy_denied_but_drug:>7}",
        "  this is the row the NKDA fill rests on, and it is a floor",
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
    with_age_in_every_note: int
    with_mixed_age: int


def survey_files(corpus: Corpus) -> FileCensus:
    """Reduce a ``Corpus`` to integers — the boundary note text does not cross.

    The three age counts partition the files that hold encounters: a day file
    states an age in every one, in none, or in some. **The two ends are not
    thresholds**, which is the point of measuring them rather than a
    "dominant" share — a boundary would have to be invented, and issue #36 is
    what an invented figure costs. Bimodality shows up as weight at both ends;
    a corpus sitting uniformly at the corpus-wide rate would have almost none.

    **An empty file is in none of the three.** ``all()`` of nothing is true, so
    a file the delimiter found no encounters in would otherwise count at the
    *every* end and inflate the figure ``batch-shift`` step 3 rests on.
    """
    with_age = [
        [has_stated_age(note) for note in day] for day in corpus.day_files if day
    ]
    return FileCensus(
        files=corpus.files,
        unique_files=corpus.unique_files,
        with_no_stated_age=sum(1 for day in with_age if not any(day)),
        with_age_in_every_note=sum(1 for day in with_age if all(day)),
        with_mixed_age=sum(1 for day in with_age if any(day) and not all(day)),
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
    # Resolved through the checkout that owns this tree rather than through this
    # file's own location -- issue #93. `scratch/` is gitignored, so a worktree
    # never has one, and the old default pointed at a path that had never
    # existed there. #78 was blocked on exactly that and got its figures by
    # typing the main checkout's path as an argument.
    #
    # This tool degraded *loudly* -- it named the path it looked at and stopped
    # -- which is why it cost a ticket rather than a firewall. `phi_scan` shared
    # the line and degraded silently. One resolution now, in `repo_root`.
    directory = Path(argv[1]) if len(argv) > 1 else scratch_root() / "day-file-text"
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
    use_utf8()
    raise SystemExit(main(sys.argv))
