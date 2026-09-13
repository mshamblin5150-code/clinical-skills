# A refutation fingerprints its heading and a reader pairs the draft

**Measured at:** a60ba82da4dffb62c5851c4393a6eb39dcd69505

[#1032](https://github.com/mshamblin5150-code/clinical-skills/issues/1032) was filed after a
2026-09-02 `discussion-post` run. The clinician challenged a legal claim in a drafted post; the
orchestrator rewrote the sentence with a rule belonging to a different kind of business entity and
posted it without a fresh refutation. The ticket left open how a grader binds a refutation to the
claim text it refuted, and
[ADR 0208](0208-a-claim-heading-is-the-claim-the-document-makes-and-the-refuter-tests-it.md)
ruling 3 returned exactly that question here. Grilled 2026-09-13; the clinician ruled every point
below on the same day and widened the ticket to cover the draft sentence as well as the heading.
Freshness gate `STALE` at `639f59c0`, then `FRESH` at `a60ba82d` after a rebase. Nothing is built
here; this is the record the build reads.

**The ticket's own incident is a draft sentence, not a heading.** A binding on the heading alone
would have graded that run clean if the heading was never edited, so part B exists.

## Read before ruling

These were read, not driven.

- **A record carries a day and no time.** `RESOLVED: <locator> - read <ISO date>` is the only date on
  a record, the refutation carries none, and `claims.md` lives under `scratch/`, outside git. The
  incident's research, challenge, rewrite and post fell on one day. *Had a date comparison been able
  to discriminate, an edit and no edit on that day would print differently; they print the same.*
- **Three certifiers share one belief predicate.** `discussion_artifact.claim_record_can_certify_values`
  decides whether a record may vouch for a value for `deck_scan`, `discussion_post_scan` and
  `discussion_reply_scan`, and it iterates `research_ledger.REFUTATION_EVIDENCE_FIELDS`.
  `peer_critique_scan._believed_tokens` does not call it, which is
  [#1056](https://github.com/mshamblin5150-code/clinical-skills/issues/1056).
- **No tool splits a draft into sentences, and no tool reports which record a sentence rests on.**
  `discussion_post_scan._maximum_record_assignment` allocates citations to records internally to count
  a shortfall and reports no pairing.
- **Only practicum has a pre-post reader record.** `practicum-case-study` step 9's `checks.md` is
  required row by row through `checks_ledger.EXPECTED_CHECKS` and carries `DRAFT:`.
  `course-assignment`'s `adversarial.md` has no field shape and no grader;
  `discussion-post`, `discussion-reply` and `peer-critique` require only the after-action review row
  in `EXPECTED_COMPLETION_CHECKS`.
- **`skills/discussion-post/SKILL.md` already promises "the draft-to-ledger read"**, and no step
  dispatches one.

## Ruled 2026-09-13

### 1. A refutation carries the fingerprint of the heading it tested

Every record that carries `REFUTATION` carries `TESTED-HEADING: <SHA-256>`, the digest of its
`## CLAIM:` heading as the refuter received it. `research_ledger.py` recomputes the digest from the
current heading and reports a mismatch as a finding, exit 1, until a fresh refutation replaces the
line. A date comparison was declined as reading above.

### 2. The digest ignores whitespace only

Runs of spaces and line breaks collapse to one space and the ends are trimmed. Letter case and
punctuation are part of the heading: `MG` and `mg` are different claims, and `1.5 mg` and `15 mg` differ
by a tenfold dose. A typo repaired after refutation therefore needs a fresh refutation, which is
automated work, as ADR 0210 ruling 6 accepted for check records.

### 3. The parent writes the digest from a command at dispatch

`research_ledger.py` gains a mode that reads `claims.md` and prints each heading's digest under
ruling 2. The parent runs it when it sends a refuter out, names the value in the refuter's brief, and
writes it into the record with `REFUTATION` and `SECOND-ROUTE`. A heading changed during the leg
leaves the old digest and ruling 1 refuses it. The mode reads headings from the file, never from a
command-line argument, because a shell expands `$50` inside double quotes and would digest a
different heading without saying so. This is ADR 0210 ruling 7's arrangement applied to a heading.

### 4. `TESTED-HEADING` is required wherever `REFUTATION` is, and is never inherited

It is required on all four verdicts and its absence is a finding, as an absent `SECOND-ROUTE` is. It
joins `REFUTATION_EVIDENCE_FIELDS`. Where `discussion-post` lets a second claim inherit a page's
`REFERENCE`, `RESOLVED`, `PAGE-YEAR` and `STATED-EXPIRY`, `TESTED-HEADING` stays with the refutation
and is never inherited, like `SECOND-ROUTE`.

### 5. A mismatched record is disbelieved by the shared predicate

`claim_record_can_certify_values` recomputes the digest and treats a mismatch as it treats `refuted`,
so a certifier that calls it traces no value to a heading nobody refuted. The three callers print
their existing disbelieved-record detail. `peer_critique_scan` gains this only with #1056.

### 6. No cutoff and no stamping of existing ledgers

A ledger written before the build carries no `TESTED-HEADING` and fails. A run in flight re-dispatches
its refuters once; a finished run is never graded again. No command stamps existing records, because
it would digest whatever each heading says now, which is the breach. The worked records in the five
claim-ledger skills carry real digests, and a test asserts each matches its own heading.

### 7. Every factual sentence of the final draft is paired with a heading

A factual sentence is `unrecorded` when no heading states it and `drifted` when it claims more than its
heading or differs from it: a broader subject or population, a different number, an added entity or
condition, or a dropped limitation. A paraphrase that claims no more is a match. The clinician's own
reasoning and experience are exempt, as the skills already exempt them from records. A finding names
its kind and a location, never the sentence.

### 8. Findings block the go-ahead and every repair re-runs the read

A `drifted` sentence is repaired toward whichever side is right: the sentence returns to its heading,
or the heading changes and, under ruling 1, is refuted again. Editing only the heading never resolves
it. An `unrecorded` claim gets a full record under the skill's research and refutation steps or is
cut. Any repair edits the draft, so the read runs again before the go-ahead. Whether a challenged
claim is right stays the clinician's; the read establishes agreement between draft and ledger.

### 9. The reader is a fresh context given only the draft and `claims.md`

Its brief says it is not given the sources and judges only whether each sentence claims more than a
heading. It receives the headings with their digests from ruling 3's command, so it copies digests and
never computes them; a copying error names no heading and refuses. A harness with no subagent tool
uses a written walk by the orchestrator, and the record's `ROUTE:` states which ran.

### 10. One record shape, required by each skill's own pre-post grader

One shared module owns the **heading read** record:

```text
## HEADING-READ: <draft file>
DRAFT: <SHA-256 of the draft>
ROUTE: separate context | orchestrator walk
SENTENCES: <n> factual, <n> clinician's own
PAIR: <location> -> <first 8 hex of the heading digest>
VERDICT: clean | defect - <substance>
FINDINGS: <kind> - <location>, <what differs>
```

`practicum-case-study` carries it as a `checks.md` row in `EXPECTED_CHECKS`. `discussion-post`,
`discussion-reply`, `peer-critique` and `course-assignment` write `heading-read.md` in the run
directory, required by `discussion_post_scan`, `discussion_reply_scan`, `peer_critique_scan` and
`deck_scan` on their existing pre-post runs. The draft is the output Markdown for `discussion-post`
and practicum, each `response-<name>.md` for `discussion-reply` with one record per reply file and
pairs only to that reply's `[REPLY: <slug>]` records, `critique.md` for `peer-critique`, and the
`.pptx` bytes for the deck, whose sentences are slide bullets and speaker-note sentences. Practicum
step 9's by-eye question on whether a claim reads the way its record says, and `discussion-post`'s
promised draft-to-ledger read, point at this record. Generalizing `checks_ledger` to all five skills
was declined: it is practicum-specific in its required document, its render fingerprint and its
`output/` lookup.

### 11. A clean read commits to its pairs, and a changed draft or heading makes it stale

A `clean` record lists one `PAIR` per factual sentence. The grader requires, as findings otherwise:

- pairs plus findings equal the stated factual count;
- every `PAIR` digest prefix names a heading currently in `claims.md`;
- `DRAFT:` equals the draft's digest.

A heading edited after the read removes its old digest, so the read expires with no further
mechanism. This supersedes [ADR 0210](0210-a-render-pass-and-a-check-record-carry-the-fingerprint-of-what-they-graded.md)
ruling 8 for this one record, which is bound to `claims.md` headings as well as to the draft. Because
[#1021](https://github.com/mshamblin5150-code/clinical-skills/issues/1021)'s `DROPPED` field says the
draft no longer makes a record's claim, a `PAIR` naming a dropped record is a finding; this follows
from that field's meaning and was not separately put to the clinician.

## Rejected options

**Compare dates.** A record's only date is a day, and the incident fell within one.

**Require a fresh refutation whenever a heading changes, with no binding.** That restates ADR 0208
ruling 3; something still has to show that the heading changed.

**Ignore case or punctuation in the digest.** Each forgives an edit that changes the claim.

**The refuter computes the digest, or a command stamps records after the refutations return.** An
agent copies or invents a digest; a later stamp digests an edited heading.

**Check the digest only when present, or only on `stands`.** Omission becomes the silent pass, and a
corrected `refuted` or `paywalled` heading keeps its old verdict.

**Enforce in the ledger alone, or in each certifier separately.** The first leaves a deck graded clean
on a value nobody refuted; the second is three copies of one rule.

**Exempt ledgers dated before the build.** The window it exempts is the one this ticket is about.

**Cited sentences only, or numbers only.** Both miss the 2026-09-02 legal rule, which carried no
number and whose rewrite sat beside a citation to a different entity's rule.

**The orchestrator reads its own draft, or the refuter reads it.** The first is the context that
missed it; the second compares with the source instead of the heading.

**A `clean` stating a count alone.** A skimmed read writes the same count, and nothing expires it when
a heading changes.

**Prose in five skills with no grader, or a separate ticket for the reader.** The first fails nothing
when the read is skipped. The second leaves the ticket's own incident open; the clinician widened this
ticket instead.

## What none of this reaches

- Whether the reader paired each sentence correctly or judged "claims no more than its heading"
  correctly. That is a reading.
- Whether a refuter tested the heading. ADR 0208's limit is unchanged.
- Whether `ROUTE: separate context` is true. Reader independence is orchestrator-owned, as refuter
  independence is.
- `peer_critique_scan` disbelieving a mismatched record, until #1056 lands.
- A draft that changed and changed back to identical bytes during one read.
- Markers on the targets this record moves: ADR 0208's *What none of this reaches* bullet on a heading
  edited after refutation, and ADR 0210 ruling 8. Whether a ratified record is edited to carry one is
  [#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201)'s open question, so
  neither record is edited here.
