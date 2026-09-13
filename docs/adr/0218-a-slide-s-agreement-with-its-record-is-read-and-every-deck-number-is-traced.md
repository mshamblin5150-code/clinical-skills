# A slide's agreement with its record is read and every deck number is traced

**Measured at:** a60ba82da4dffb62c5851c4393a6eb39dcd69505

[#1034](https://github.com/mshamblin5150-code/clinical-skills/issues/1034) was filed after an
independent adversarial reader found four defects in a `course-assignment` deck that
`tools/deck_scan.py` had passed: a caveat whose sense was inverted between its claim record and the
slide, a sentence standing alone on a slide although its record said it must not stand without its
qualifier, a figure on a slide face with no record behind it, and a claim record left stale after the
deck text it sources was revised. The open decision was how much record-to-slide agreement a
mechanical row can reach. Grilled 2026-09-13; the clinician ruled every point below on the same day.
Freshness gate `STALE` at `639f59c0`, then `FRESH` at `a60ba82d` after a rebase that touched none of
the code measured below. Nothing is built here; this is the record the build reads.

## Measured before ruling

### The record format cannot say which slide a record sources or what its qualifier is

A claim record carries a heading and the fields `STATUS`, `SOURCE`, `REFERENCE`, `RESTATEMENT`,
`RECENCY`, `RESOLVED`, `PAGE-YEAR`, `REFUTATION`, `SECOND-ROUTE`, `INSTRUMENTS` and `STATED-EXPIRY`.
None names a slide and none declares a qualifier; either can only sit in free text.

### Slides paraphrase their records

On the one `course-assignment` run that exists, a ledger of 701 records behind a 10-slide deck, no
record heading appears word for word on a slide face or in the speaker notes. Exactly one record
names a slide number. Counts were taken at `639f59c0` against private working material; nothing
committed re-derives them.

### The adversarial reader is not told to check agreement

`skills/course-assignment/SKILL.md` has the reader attack the rendered artifact for records that do
not exist. It is not told to compare a slide with the record behind it. Its report on that run
carries keyword hits for three of the four defects and none for the stale record, read by keyword
only. That report is older than both the final ledger and the submitted deck.

### A general number trace fires on real figures on the one deck available

`discussion_post_scan`'s number extraction and stripping, driven read-only over the submitted deck
and that run's believed records with both heading and restatement as trace text, left 6 non-dollar
numbers untraced on slide faces and 11 with speaker notes. None was year-shaped, an integer of 20 or
less, or a number standing alone in a short paragraph, and the stripping removed nothing. Tracing
from the heading alone left 2 more numbers untraced on faces and 5 more with notes. Driven at
`639f59c0` and re-run at this record's commit with the same counts. `discussion_post_scan.py` and `discussion_artifact.py`
are unchanged between that commit and this record's.

**That deck is not a clean control.** `python tools/deck_scan.py` over it exits 1 at this record's
commit, with `untraced-costed-figure: 23` and `rendered-record: 3`, because it predates the
believed-record requirement and the rendered record. *Had the widened row been tried only on a deck
that already fails, a false positive on a correct deck would read the same as a true one*, so the
measurement above supports the shape of what the row reads and not a rate on correct decks.

## Ruled 2026-09-13

### 1. Record-to-slide agreement is the adversarial reader's to check

The adversarial reader's brief in `skills/course-assignment/SKILL.md` gains an agreement job beside
its existing one. For every slide it reports, keyed to slide number:

- a figure or assertion whose value or sense differs from the claim heading of the record behind it;
- a record qualifier that does not appear with its claim, per ruling 5;
- a record whose heading no longer matches the slide text it sources.

The claim-record grammar gains no slide field and no qualifier field, and no grader row compares a
record with a slide. `deck_scan.DECLARED_LIMITS` gains a limit saying no mechanical row checks that a
believed record agrees with the slide it sources, and `tools/test_course_assignment_skill.py` binds
the new brief text beside its existing adversarial-read assertions. A repaired heading is a new claim
under ADR 0208 ruling 3.

### 2. Whether the reader read the final deck stays with #1229

The agreement read protects only the deck the reader was given. Binding `adversarial.md` to the
final deck, and the order in which the reader receives rendered slides, are
[#1229](https://github.com/mshamblin5150-code/clinical-skills/issues/1229)'s. The limit ruling 1 adds
says so.

### 3. The untraced-figure row reads every number

`untraced-costed-figure` becomes `untraced-figure` and traces every number on slide faces and in
speaker notes rather than `$`-prefixed amounts only. It reuses `discussion_artifact.NUMBER` and the
stripping `discussion_post_scan` applies before it, rather than writing a third number reader. A
number absent from every record and one present only in a disbelieved record stay distinguished, as
they are for costs today. The ADRs that name the old row keep its name as historical record.

### 4. Only the claim heading certifies a deck number

`deck_scan` keeps taking numbers from a believed record's heading line alone. ADR 0208 ruling 1 makes
the heading the claim the document makes, including any number it states, so a slide number found
only in a restatement is a heading to correct. `claim-support-unverified` keeps naming the heading,
widened from a cost token to a figure.

### 5. A qualifier travels onto the slide face

A record's qualifier appears on the same slide face as the claim it conditions. Speaker notes do not
satisfy it: the reader of the deck judges the slide in front of them, and the recorded defect was a
slide face standing alone. Where the qualifier does not fit the bullet limit, the claim moves or
splits rather than dropping its condition.

### 6. The agreement read is ruled for `course-assignment` only

The shared `skills/_shared/reference/sourcing.md` gains nothing. Of the other four claim-ledger
skills, two have no second reader and two have readers with other subjects, so a shared rule would
promise a read that has no home. Whether those skills get one, and whether their certifiers also
narrow to the heading, is
[#1245](https://github.com/mshamblin5150-code/clinical-skills/issues/1245)'s.

## Rejected options

**A slide field and a qualifier field with a row requiring the qualifier phrase on its slide.** It
reaches one defect of four, and it fires whenever a slide paraphrases the qualifier. Slides on the
measured run always paraphrase, so the row either refuses correct decks or forces word-for-word
qualifiers into bullets with a word limit.

**Tracing each record's restatement back to the slide text.** It would catch a stale record and fire
on legitimate paraphrase, which the ticket itself named.

**Absorbing #1229.** One ruling for the brief and the binding would grade a record ADR 0210 ruling 9
declined to widen `deck_scan` into, and the brief is complete whichever deck the reader receives.

**Heading plus restatement, as the three sibling certifiers read.** It clears 5 numbers on the
measured deck and certifies numbers ADR 0208 ruling 1 requires in the heading.

**Widening this ruling to the sibling certifiers.** Nothing measured them, and ADR 0208 left them
reading the restatement the same day. Filed as #1245.

**A qualifier satisfied in speaker notes, or by a bar field declaring a narrated deck.** Either would
have passed the recorded defect, and no run has shown a narrated deck.

## What none of this reaches

- **Whether the reader actually compared each slide with its record.** Ruling 1 is prose;
  `adversarial.md` has no closed expected set, which `adversarial-completeness-unverified` already
  declares.
- **A reader given a stale deck.** #1229.
- **Numbers held in SmartArt or chart parts.** The widened row still reads the slide's own XML;
  [#1065](https://github.com/mshamblin5150-code/clinical-skills/issues/1065).
- **A number written in words or converted to another unit.** The shared number pattern reads digits.
- **The widened row's rate on a correct deck.** The only deck measured already fails.
