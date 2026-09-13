# A claim heading is the claim the document makes and the refuter tests it

**Measured at:** 6158340faf780dec495af594248023503648e002

[#1018](https://github.com/mshamblin5150-code/clinical-skills/issues/1018) was filed by the
after-action review of one `practicum-case-study` run. Four claim headings on that run asserted a
numeric answer before research, and the research falsified all four. The ticket proposed rewriting
non-drug headings, and the skill's worked record, as questions. Grilled 2026-09-13; the clinician
ruled every point below on the same day. Freshness gate `STALE` at `f51daf03`, then `FRESH` at
`6158340f` after a rebase. Nothing is built here; this is the record the build reads.

**The ticket was framed as one skill's wording, and the heading is not only a brief.** It is certified
evidence in three other artifact families, and that finding moved the ruling from a practicum wording
change to a rule for all five skills that keep a claim ledger.

## Measured before ruling

### A believed record certifies its heading's number even when its restatement contradicts it

Driven through `discussion_post_scan._claim_records` and `deck_scan._claim_costs` with a synthetic
record marked `STATUS: sourced`, whose heading says a permit costs $50,000 and whose `RESTATEMENT`
says the fee schedule lists it at $45,000:

| heading | `REFUTATION` | discussion-post traced numbers | deck traced costs |
| --- | --- | --- | --- |
| `A permit costs $50,000.` | `stands` | 45,000 and 50,000 | $50,000 only |
| `Does a permit cost $50,000?` | `stands` | 45,000 and 50,000 | $50,000 only |
| `A permit costs $50,000.` | `refuted` | none | none |

**The instrument discriminates.** Had the certifiers taken numbers from the restatement alone, the
first two rows would read 45,000 alone and nothing on the deck. Had question form mattered, the second
row would differ from the first. Neither holds. `discussion_reply_scan._number_findings` and
`peer_critique_scan._believed_tokens` build their trace text from the heading plus `RESTATEMENT` in
the same way; they were read, not driven.

`discussion_post_scan`'s behavior control for its support limit,
`test_numeric_identity_does_not_establish_restatement_support`, replaces the restatement with an
unrelated figure and still passes, because the body's number traces from the heading. The control
exercises the heading case, while the limit it binds names only the restatement.

### No refuter is told to test the heading

The refutation leg in `skills/practicum-case-study/SKILL.md` reads whether the source says what the
restatement says it says. `skills/course-assignment/SKILL.md` and `skills/discussion-reply/SKILL.md`
attack the reference, locator, year, bibliographic details and restatement.
`skills/discussion-post/SKILL.md` checks whether the cited section says what the draft claims.
`skills/peer-critique/SKILL.md` names no target. So `stands` can truthfully describe a restatement
beside a false heading.

### The worked record's heading is broader than its source

Its heading places a white count of 15,000 within physiologic leukocytosis in pregnancy; its
restatement gives a third-trimester range only. The answer it asserts is inside that range, so the
record is not wrong about the number. It claims a population its own source does not cover, and its
`REFUTATION` checks only bibliographic details and the page.

### The research on that run tested the headings

The ticket records that the agents sent to source the four asserted answers falsified all four. The
recorded harm is not an agent confirming a pre-committed answer; it is a wrong number standing in a
heading.

## Ruled 2026-09-13

### 1. A claim heading is the claim the finished document will make

This holds in all five claim-ledger skills. Before research the heading is a working statement,
including any number the document will state. Where the source does not support it, the run corrects
the heading before drafting. The glossary already defines a claim ledger as the record of every
factual claim a graded document makes, and the four sibling templates already describe the heading as
the drafted claim, so this makes one grammar out of five.

### 2. The refuter tests the heading

The refutation leg tests whether the source supports the heading as written, as well as the
restatement. A heading the source does not support is `refuted`, which ADR 0153's ruling 3 already
makes every certifier disbelieve. No grader row is added.

### 3. A heading changed after its refutation is a new claim

It gets a fresh `REFUTATION` and `SECOND-ROUTE` before any citation spends the record or any certifier
takes a number from it. This extends `skills/discussion-post/SKILL.md`'s rule that a claim is never
inherited from another sentence, from a reused page to a repaired heading. How a grader detects an
edit made after refutation stays with
[#1032](https://github.com/mshamblin5150-code/clinical-skills/issues/1032).

### 4. The worked record is corrected in place

Its heading narrows to the third trimester and keeps the 15,000, so `NUMERIC_CLAIM_UNQUANTIFIED` still
reaches it. Its `REFUTATION` names the heading check. Test fixtures that copy the worked record move
with it; the echo-row tests' own strings do not.

### 5. The certifier limits name the heading

The support limits of `discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan` name
both the heading and the restatement, and say the refutation leg owns heading agreement. Each module's
`HANDLERS` key moves with its subject. `deck_scan`'s `claim-support-unverified` already names the
heading and is unchanged. ADR 0153's *What this record does not settle* line on restatement support
is corrected where it stands.

### 6. The rule is written once

It goes in `skills/_shared/reference/sourcing.md`, which every research and refutation brief in the
five skills already reads first and which already holds the claim-record certification rule. The
three skills that enumerate what the refuter tests add the heading to that enumeration, so no local
line contradicts the shared rule. A test binds the shared statement and those three enumerations.

## Rejected options

**A question heading.** The ticket's proposal. The first measured table shows a question heading's
number is certified exactly as a statement's is, so it closes nothing. It would also give practicum
two heading grammars, with drug headings staying orders, and it never becomes the sentence the
document states.

**A verdict-free subject line.** Avoids pre-committing to an answer, and the certifiers still read
its number.

**A row requiring every heading number in the restatement.** Restatements use the source's own units,
so a count of 15,000 is correctly answered in `10^9/L`. The row fires on the skill's own worked record.

**Certifiers read only the restatement.** Removes the heading's contribution and fails a correct body
figure whose form differs from the source's units. It also rewrites `deck_scan`, which reads the
heading alone.

**Rule text in each of the five skills.** Five prose copies of one rule, where an edit to any copy fails
nothing.

**Practicum only.** Leaves the rule out of the three families whose certifiers read the heading.

## What none of this reaches

- **Whether a refuter actually tested the heading.** Ruling 2 is prose. `REFUTATION: stands` still
  cannot show which target a refuter examined; refuter independence was already orchestrator-owned.
- **A heading edited after refutation.** Ruling 3 states the obligation, and no grader detects its
  breach; that is #1032's open decision.
- **Whether a believed record supports a traced number at all.** The limits in ruling 5 remain limits,
  and [#1034](https://github.com/mshamblin5150-code/clinical-skills/issues/1034) carries the
  deck-agreement case.
- **`peer_critique_scan` believing refuted and sourceless records.** Its trace does not read the
  status predicate, which is [#1056](https://github.com/mshamblin5150-code/clinical-skills/issues/1056);
  ruling 2's `refuted` state protects that certifier only after #1056 lands.
- **The four headings on the run that prompted the ticket.** They were read through the ticket and its
  sweep comments, not reopened; the ledger is private working material.
