# A voice read compares a planted copy of the draft with the voice model

**Measured at:** fc276381e93646714e0f8508d2a3a7f950b83b84

[#1400](https://github.com/mshamblin5150-code/clinical-skills/issues/1400) was filed from the
grilling of [#1393](https://github.com/mshamblin5150-code/clinical-skills/issues/1393), whose
[ADR 0270](0270-the-canonical-voice-model-is-resolved-by-one-owner-and-identity-is-the-graded-row.md)
ruling 10 declared that **use is not voice** and filed the residue: nothing compares a finished
coursework draft with the voice model the run resolved, and a run with the model correctly in hand
still produced a draft the clinician reopened as not his voice, NUR 5144 Module 2, 2026-09-09.
Grilled against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below
in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

The ticket required the discriminating pairs' mechanical reach to be **measured rather than
argued**. The instrument parsed the pairs with `voice_model_scan`'s own pair grammar from the model
`repo_root.canonical_voice_model()` resolves, and matched each half exactly — case, whitespace,
quotes and dashes normalized — and loosely, by word 4-grams.

**The model carries 11 pairs, and one is a phrase a draft could contain verbatim.** Nine generic
halves are full sentences of 10 to 27 words tied to one topic; one pair's halves share every token
and differ only in pacing, so no token matcher can separate them by construction. The one
phrase-level pair is the one ADR 0270 quotes.

**The population was 28 finished documents with an unread remainder of 0**: the disowned draft, the
accepted version of the same case study in two forms, and 25 other finished pieces across all five
coursework skills. The disowned draft is the render the run handed over; it is the only preserved
copy, identified by its page count and by the handover and correction times in the run transcript.

**The instrument cannot discriminate the recorded instance.** The disowned and the accepted drafts
return the identical result — zero exact matches on either half. Across the other 25, the single
exact generic-half match is the reply the phrase-level pair was harvested from, so the instrument
re-found its own source. Every loose generic match sat inside a quotation or a cited sentence. The
instrument is live: each half of all 11 pairs planted into the disowned text fired, 11 of 11 on each
side. What it would print if the pairs had no mechanical reach is what it printed.

**What the clinician corrected on 9/9 is not in the model.** Temperature in Fahrenheit with the
degree symbol, standard clinical abbreviations, one intake field per line, his own reasoning image
carrying the Assessment, and profanity out of graded copy. The model holds no match for the first
two. The field layout is already a style-sheet rule graded by `case_study_scan`. The corrections
were recorded only in a memory file one harness reads.

**A draft-versus-pairs reading already existed as an instruction and could not fail.** The
`practicum-case-study` step 9 by-eye walk has told the run to read the draft back against the
discriminating pairs since [#213](https://github.com/mshamblin5150-code/clinical-skills/issues/213) built the model. No expected check names it, so it was in force the night the
disowned draft was handed over. The other four skills have no post-draft reading against the model
at all.

**The captured-thought store's chat-history thoughts are not the clinician's words.** Of roughly
eleven thousand thoughts, 2,822 carry the chat-history source, all imported on 2026-06-20 from
conversations dated 2024-07 to 2026-01. In a 22-result sample on writing, 13 were model-written
summaries about him and 9 were stated preferences. All predate the damping reversal.
The clinician's typed chat corpus is a separate export the model already draws on.

## Ruling 1 — a reader's record, and no pair-matching row

Drafts are compared with the voice model by a **voice read**: a reader's written record, expected by
all five coursework completion graders. A mechanical row over the pairs was refused on the
measurement above: it cannot tell the disowned draft from the accepted one, and a row that cannot
fail on the recorded instance is the written instruction this ticket exists because instructions
cannot fail. Building both was refused because a clean result from the dead row would read as
coverage it does not have.

## Ruling 2 — the comparison is forced three ways

A well-formed verdict from a reader who skimmed prints what a verdict from a reader who compared
prints, so the record is made to discriminate.

**It is bound to three identities.** The real draft's digest, the planted copy's digest, and the
model's digest, which must equal the one the run's `voice_model_identity` record holds. The read
expires when the draft changes.

**Every pair is answered.** For each pair — the population derived from the model at grading time,
never from the reader's count — the reader quotes the closest draft sentence verbatim and states
which half it resembles, or `no counterpart`. The grader confirms every pair is present and every
quoted sentence is in the planted copy. `no counterpart` is legal: a reply may never touch a pair's
kind of sentence.

**One planted sentence must be flagged.** The reader reads a copy in which one of the draft's own
sentences has been rewritten toward a pair's generic half, and is not told. A read that does not flag
it is void. This is the only limb that separates a comparison from a plausible verdict, and it is the
clinician's own act on 9/9: he read the draft and caught what was not him.

## Ruling 3 — a separate planter writes the plant

The **planted sentence** is written by a context that neither authored the draft nor performs the
read. It receives the draft and the model's pairs, rewrites one sentence, and records which sentence
it changed in a record the reader never receives.

The author planting was refused: the smoothing that produced a disowned draft would produce a plant
that reads as his, and the test would measure nothing. Planting a pair's generic half verbatim was
refused: ten of the eleven are about an unrelated topic and are caught as off-topic rather than as
generic, and the one topic-free phrase is a fixed pattern.

The grader confirms mechanically that the planted copy differs from the real draft in exactly one
sentence and that the planter's record names it. **Whether the rewrite is truly generic is a reading
no check reaches**, and is declared as such.

## Ruling 4 — its own reader and its own record

The voice read is a separate reader with a **purpose-named record** in the run directory, not a field
on the heading read. The heading read is bound to the real draft's digest; a reader that had seen the
real draft could find the plant by difference rather than by voice, and a heading read taken on the
planted copy would certify a file that is never submitted. ADR 0270 ruling 6's purpose-named-record
rule applies.

## Ruling 5 — no subagents means not run, never clean

Where the harness has no subagent tool, the voice read is **recorded as not run** and the completion
grader reports it as incomplete coverage rather than clean. The clinician's go-ahead is then that
run's only voice gate, and the report says so.

A self-read without a plant was refused: it is a self-authored second read, it cannot fail, and it
rebuilds the 9/9 condition. Refusing completion was refused: it blocks a submission on the tooling
rather than on the work. Both harnesses the clinician uses have subagents, so this branch is rare
and has **no recorded instance**.

## Ruling 6 — what fails the read

**A missed plant voids the read**, and a new reader runs on a fresh plant. **A real draft sentence
the reader places on a pair's generic side is a finding**: it returns to the author, and the planter
and reader run again on the revised draft, with a fresh plant, because the draft digest moved.

Listing generic sentences for the clinician at the go-ahead without forcing a rewrite was refused:
that delivers the 9/9 draft with a list attached. The damping ruling binds the remedy — a flagged
sentence is rewritten the way the clinician writes, never by amplifying a measured feature toward a
rate.

## Ruling 7 — the reader consumes the canonical model and nothing else

The voice read compares against the model `repo_root.canonical_voice_model()` resolves, and no second
voice reference. Reading the captured-thought store or the chat export directly on each run was
refused: it is the second reference #1400 forbids, it compares against summaries of the clinician
rather than his words, and it carries superseded rulings unmarked.

What is worth having there reaches the reader **through the model**: a one-time, date-checked harvest
of stated voice and word-choice preferences, reviewed in `setup-clinical-skills`' confirmation step
with the clinician present. That harvest is filed as its own ticket.

## Ruling 8 — the 9/9 corrections are split by kind

Fahrenheit with the degree symbol and standard clinical abbreviations are **house style**. They go
into the style sheet, with a mechanical row where one is checkable. The reasoning-image lesson is
**voice** and goes into the model at the harvest's review sitting. The field-layout rule already
exists and is graded. The style half is filed as its own ticket.

Putting everything in the model was refused: the voice reader would be judging unit symbols, and a
string-checkable convention would become a judgment.

## Ruling 9 — profanity is mechanical, the typing-defect lists are the reader's

The model's hard rule against profanity in graded work becomes a **mechanical row** in the five
completion graders. Its word list is read from the canonical model and never held as a second copy;
if the model holds none, adding one belongs to the harvest's review sitting and is not invented by
the build.

The model's two never-reproduce lists — defects seen in the samples and in the typed corpus — join the
voice reader's brief rather than a row. A machine draft reproduces them only by imitating the samples,
and imitation is what the voice read examines.

**Before either is built it is measured** against the finished coursework population with a planted
control, on the bar the pairs had to clear. A row that cannot fire becomes a declared limit instead.

## Ruling 10 — decks carry the voice read beside the talk-style read

`course-assignment` decks keep [#1394](https://github.com/mshamblin5150-code/clinical-skills/issues/1394)'s
presentation-intent record, which grades the deck against the signed bar's talk style and never
opens the voice model. The voice read runs beside it on slide text and speaker notes, planting in a
copy of the notes. The DOCX branch, which has no intent record, carries the voice read too.

**The two reads answer different questions.** The talk style is what the assignment asked for; the
voice model is how the clinician writes and speaks. A deck can have the right shape and not sound
like him. Each record's declared limits name the other's ground. Merging the voice read into the
intent reader was refused on ruling 4's ground; exempting decks was refused because it leaves the
talk-style string standing in for a voice it never reads.

## Ruling 11 — two residues are filed, not folded

The harvest of ruling 7 and the style half of ruling 8 are filed as **separate tickets**. The voice
read is correct without either: the harvest only improves the model the reader already consumes, and
the style rows are graded by a different checker against a different sheet. Folding them would hold
the voice read on a review sitting it does not depend on.

## Ruling 12 — one limits object carries the ceiling

The voice read's ceiling is declared in **one object** beside the mechanism that grades it, named by
the five graders and by `CLAUDE.md`, with no row copied. It states, at least:

- **Consistency is not identity.** A clean voice read establishes consistency with the model's
  samples, never that the draft sounds like its clinician.
- **The plant's genericness is a reading.** Whether the planted sentence was truly generic is not
  checked.
- **A well-formed record cannot prove the reader judged well.** The plant proves the reader
  compared; it does not prove every other placement is right.
- **The model's gaps are the read's gaps.** What the model does not hold, the read cannot find; the
  recorded instance's formatting corrections were outside the model.

ADR 0270's `use-is-not-voice` limb is narrowed by this mechanism, not retired: a clean voice read is
still not the clinician's word that the draft is his.

## What this record does not settle

**The captured-thought store's superseded positions.** Ruling 7 routes the store through a reviewed
harvest; retiring or marking its superseded statements in the store itself is not ruled here.
