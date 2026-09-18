# The discussion post, reply and peer critique certifiers take a number from the claim heading alone

**Measured at:** 726c97123730d3e652861bbe60055cc1f1f75f50

[#1245](https://github.com/mshamblin5150-code/clinical-skills/issues/1245) was filed from
[#1034](https://github.com/mshamblin5150-code/clinical-skills/issues/1034)'s grilling, whose
[ADR 0218](0218-a-slide-s-agreement-with-its-record-is-read-and-every-deck-number-is-traced.md)
ruling 4 kept `deck_scan` certifying a number from a believed record's claim heading alone and
ruling 6 left the three sibling certifiers and their second readers to this ticket.
[ADR 0220](0220-a-dropped-record-vouches-for-no-number-and-every-claim-certifier-calls-the-shared-check.md)
kept heading plus restatement pending this ruling. Grilled against `main` at `726c9712`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## What was measured before ruling

The three certifiers build their numeric trace text from the claim heading plus `RESTATEMENT`:
`discussion_post_scan._claim_records`, `discussion_reply_scan._number_findings` and
`peer_critique_scan._claim_tokens`. None reads `PASSAGE`. A number in that text certifies a body
number only when `discussion_artifact.claim_record_can_certify_values` believes the record.

Each scanner's own load and grade path was driven in-process over every retained run, once as
shipped and once with the module's `RESTATEMENT` pattern replaced by one that never matches:

| | discussion post | discussion reply | peer critique |
| --- | ---: | ---: | ---: |
| runs graded | 3 | 5 | 0 |
| believed claim records in graded runs | 0 | 0 | - |
| numbers heading-only leaves untraced beyond shipped | 0 | 0 | - |

Five discussion-post run directories held no output draft and one draft unit was refused for lacking
its run's `bar.md` and `claims.md`; they are the unread remainder. No `critique.md` is retained in
any scratch or output root. Every graded run already exits 1 for other reasons, so none is a clean
control.

**The zero settles nothing.** With no believed record in any graded run, the restatement can never
reach the traced set, so shipped and heading-only must print the same result whatever the true
effect is. The records predate the refutation-evidence fields and `TESTED-HEADING` that believing a
record now requires. A planted control in each certifier did discriminate: one real believed
record, borrowed from a run outside these populations, carrying a body number only in its
restatement, traced as shipped and was untraced with the restatement removed. The instrument works;
the population cannot yet be measured. Counts were taken against private working material, and
nothing committed re-derives them.

The one earlier measurement is ADR 0218's deck, where reading the restatement cleared 2 numbers on
slide faces and 5 with speaker notes.

## Ruling 1 — the ticket's second question is settled by #1257

[#1257](https://github.com/mshamblin5150-code/clinical-skills/pull/1257) gave every claim-ledger
skill the final `## HEADING-READ:` second reader in `skills/_shared/reference/sourcing.md`. A fresh
context pairs every factual sentence of the final draft with a current claim heading and reports a
changed number, an added entity or condition, a dropped limitation, or an unrecorded claim. Its
record is bound to the draft's bytes and graded by each skill's heading-read rows. That reaches the
three defects the ticket found unread: disagreement with the record, a qualifier missing from the
text, and a record gone stale after revision. No further reader is added, and the ticket's item 4 —
a declared limit wherever no reader exists — is moot.

## Ruling 2 — the three certifiers take numbers from the claim heading alone

`discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan` stop adding restatement
numbers to the traced set, matching `deck_scan` under ADR 0218 ruling 4. ADR 0208 ruling 1 makes the
heading the claim the finished document makes, including any number it states, and the heading
reader under ruling 1 already reports a number that differs from its heading as drifted. Keeping the
restatement would leave the mechanical row certifying a sentence the reader contract calls drift.

`PASSAGE` stays excluded. A locator number there — a table or page number — never certifies a body
number, and a fixture pins it.

Deferring until a run holds believed records was refused: it holds the certifiers in a state the
reader contract already contradicts, waiting on a population that may take courses to accumulate.

## Ruling 3 — a restatement-only number is named as one

The row and exit status do not change. The finding detail gains a third wording between the two it
has:

- `<n> appears only in a disbelieved claim record`
- `<n> appears only in a claim record's restatement; state it in the heading`
- `<n> is absent from claims.md`

In that order, the first that applies wins. Without the second wording a restatement-only number reads as absent
from `claims.md`, which is false and points the run at researching a new claim instead of correcting
a heading. The restatement is read for this wording only and never certifies.

## Ruling 4 — tests and declared limits move with the narrowing

- `peer_critique_scan`'s `test_a_number_traced_to_an_unrelated_restatement_passes` writes its number
  into both heading and restatement through `claim_record(47)`, so it never isolated the restatement
  branch; it becomes a test that a restatement-only number fails with the ruling 3 wording.
- `test_numeric_identity_does_not_establish_restatement_support` in the post and reply suites, and
  the declared limits that name it and read *whether a believed record's heading and restatement
  support the number traced from it*, are rewritten to the heading.
- Each certifier gains a positive control: a number in a believed heading traces, and the same
  number only in the restatement, and only in `PASSAGE`, does not.

## What none of this reaches

- Whether a heading's number is true of its source. That remains the refuter's under ADR 0208.
- Whether a body sentence claims more than its heading beyond the number. That is the heading
  reader's under ruling 1, not a mechanical row.
- The rate at which heading-only fires on correct posts, replies and critiques. No run with believed
  records exists to measure it.
