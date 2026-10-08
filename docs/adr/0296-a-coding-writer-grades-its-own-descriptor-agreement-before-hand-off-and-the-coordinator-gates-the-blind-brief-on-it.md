# A coding writer grades its own descriptor agreement before hand-off and the coordinator gates the blind brief on it

**Measured at:** 54e2da6f735031c2d1e75dac96389fe9d46566f1

[#1448](https://github.com/mshamblin5150-code/clinical-skills/issues/1448) was filed from the
after-action review of a `batch-shift` run. Five times in one shift, a per-encounter writer or a
revision agent chose a code whose descriptor the note's own words did not reach. Every one passed
the writer-side scanners and was caught only by the blind descriptor-agreement read after all the
notes existed. The writer had the index and the descriptor text at write time. Grilled 2026-10-08
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

Its siblings from the same pattern are
[#1447](https://github.com/mshamblin5150-code/clinical-skills/issues/1447), the history slice,
[#1452](https://github.com/mshamblin5150-code/clinical-skills/issues/1452), the refusal-substitute
slice, and [#1459](https://github.com/mshamblin5150-code/clinical-skills/issues/1459), the blind
reader's wrong-place failures.

## Measured before ruling

**The agreement rules bind only the blind reader.** `skills/icd10-cpt/SKILL.md` places the
descriptor-or-route requirement in *Descriptor agreement is a separate blind read*. Step 3's rules
carry no author-side agreement step, and `skills/clinical-note/SKILL.md` runs the blind read only
after the note and worksheet are saved. `skills/batch-shift/SKILL.md` runs it once across the
shift, after every pass has finished.

**A written brief line did not hold.** #1447's comment of 2026-10-01 records that the next shift's
pass brief carried the prior review's lesson in plain words, and seven of eleven notes repeated the
defect.

**The grader can already read several records, and can grade one note only after a change.**
`tools/anchor_scan.py` takes `--agreement-read` with one or more record files and merges them by
filename stem; a repeated stem enters the unread remainder. `--stem` restricts the population, but
the command refuses it outside `--agreement-brief`: `--stem requires --agreement-brief`. The stem
filter it would use already lives in `_pair_agreement_sources`. *During the grilling this record
follows, the clinician was told that `--agreement-read --stem note-N` grades one note today. That was
false; the rulings below do not rest on it, and the build adds the option.*

**The grader's checks are partly mechanical and partly a reading.** An index route is checked
against the committed index catalog, every field must be a nonempty string, the agreeing words must
be verbatim in the note and inside the row's anchor, and a refusal's `proposed instead` code must be
among the worksheet's for-entry ICD-10 codes. The route `descriptor words` is always accepted
mechanically; whether those words state the descriptor is the reader's judgment. The unread
remainder is one integer with no per-system breakdown.

**CPT descriptors are unverified.** `reference/procedure-codes-2026.sqlite` carries
`cpt_descriptors = unverified`, so every CPT code without a rendered-page record enters the unread
remainder and the grade exits 2.

## Ruling 1 — the writer grades itself with the existing agreement grader

Every `icd10-cpt` pass that writes a worksheet, including the pass `clinical-note` runs and each
`batch-shift` per-encounter pass, writes its own private agreement record before reporting done. It
generates its subjects with `--agreement-brief --stem <stem>`, fills the same six fields the blind
reader fills for every subject, and grades the record with `--agreement-read` restricted to its own
stem.

A list of descriptor words and routes in the hand-off report was declined because nothing fails on
it, which is what the measured brief line showed. A new per-code worksheet field was declined on
ADR 0243 ruling 4's ground that the worksheet grammar does not carry a sixth field, and because the
blind reader never sees the worksheet, so the field buys nothing the record does not.

The skill names the ceiling beside the step. A writer grading its own codes is **Shared-reader
blindness**: the self-grade catches a missing or invalid route, an absent waits-on-result or
open-status entry, words outside the anchor, and a substitute missing from the for-entry codes. It
cannot catch a writer who sincerely misjudges agreement, and `descriptor words` always passes. The
blind read remains the independent check and is unchanged.

## Ruling 2 — the step is written once, in icd10-cpt

The step is stated in `skills/icd10-cpt/SKILL.md`'s descriptor-agreement section.
`skills/clinical-note/SKILL.md`, where the worksheet is saved, and `skills/batch-shift/SKILL.md`'s
pass brief each carry a pointer to it and the command. Neither carries a second copy of the rule.

## Ruling 3 — a self-grade finding is fixed before hand-off

A self-grade finding, exit 1, is never handed off. The writer selects a code the note's words reach,
or writes a welded `NOT CODED:` refusal whose `proposed instead` code is supported, and grades again.

## Ruling 4 — while CPT descriptors are unverified, a batch writer may leave only CPT unread

In a `batch-shift` pass, a self-grade at exit 2 is acceptable only when every unread subject is a CPT
code with no rendered-page record. Every ICD-10 and HCPCS subject must be read and clean. The per-pass
writer does not read CPT pages: the shift's writers run concurrently and share one signed-in
browser, and the shift reads those pages once. In a single `clinical-note` run the rendered-page
record is needed by the blind read immediately afterward, so the writer saves it before grading and
requires exit 0. Once `cpt_descriptors` is `verified`, the exception has no members.

Per-writer page reading was declined because concurrent passes would contend for the authenticated
VitalSource session and the same pages would be read again at the roll-up. Grading CPT against the
unverified database descriptor was declined because that text is known to carry malformed shapes,
so the self-grade could pass or fail for the wrong reason.

## Ruling 5 — the self-records are kept, and the blind brief waits on them

Each writer's self-record is kept in the run. Before building the blind brief, the coordinator saves
the shift's rendered-page record and grades every note's self-record together in one
`--agreement-read`, which must exit 0. A missing or failing self-record sends that note back for
correction before any blind reader is briefed. In a single `clinical-note` run the writer's own exit
0 is that gate.

Keeping the records as unchecked evidence, or discarding them, was declined because a skipped
self-grade would then look like a clean one until the blind read found the defect a round later. The
gate also reads CPT against the shift's page record, so ruling 4's deferred CPT subjects are graded
before the blind round.

## Ruling 6 — this ticket is the mechanism; the history rule stays with #1447

The self-grade applies whatever the agreement rules say; this record adds no clinical rule. The
waits-on-a-result rule is already ADR 0243 ruling 9 and the skill's text, so the self-grade's
`waits_on_result` field enforces it, which answers #1447's question of where that rule lands. The
addressed-today rule's writer-side statement, its filled-medication corollary and #1447's open
clinical decisions remain #1447's.

## Ruling 7 — a self-record never reaches a blind reader, and its yield is counted

No self-record enters the blind brief or any retry hint, whichever option #1459 rules. The blind
reader is told the self-records exist and are not to be read; that is declared, not enforced,
because a reader could open a file in the run directory. ADR 0243 ruling 10's ground applies: a
reader starting from the author's framing is how the topical shapes passed.

The blind grade also prints, report-only and never graded, how many subjects passed the writer's
self-grade and failed the blind read. That count is what discriminates a self-check that catches
defects from one that does not; without it the after-action review has only retry-round counts.

## Consequences recorded as derived rather than ruled

- `tools/anchor_scan.py` accepts `--stem` with `--agreement-read`, counting a requested stem's
  absence as unread as `_pair_agreement_sources` already does for the brief.
- The agreement report distinguishes unread CPT subjects lacking a rendered-page record from every
  other unread subject, so ruling 4's acceptance is read off the report rather than inferred.
- A note sent back by ruling 5's gate has already been placed, so its correction is a **Repair
  pass** under [ADR 0294](0294-an-orchestrator-s-per-note-claims-and-every-repair-pass-are-derived-from-the-record.md):
  its brief names the coding fields it may change and its before and after hashes join the chain.
  A writer's own corrections before it reports done precede placement and are not repairs.
- Because the grader already refuses a `proposed instead` code absent from the for-entry ICD-10
  codes, the self-grade catches #1452's defect at write time. #1452's `refusal_scan` decisions are
  untouched.
- `CONTEXT.md` gains **Writer self-grade**.

## What this does not reach

Whether a writer's `descriptor words` route really states the descriptor, and whether its
open-status evidence really shows the condition addressed today, are readings the self-grade cannot
make about its own author. That an orchestrator never handed a self-record to a blind reader is
declared, not checked. A revision agent that changes codes after the blind read is outside this
record and inside ADR 0294's repair rules.
