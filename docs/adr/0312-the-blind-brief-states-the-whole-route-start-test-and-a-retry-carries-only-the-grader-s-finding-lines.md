# The blind brief states the whole route-start test and a retry carries only the grader's finding lines

**Measured at:** 290acba60ab8fa0b0af073fe1ba273e7d4a1cd34

[#1476](https://github.com/mshamblin5150-code/clinical-skills/issues/1476) was filed from the
after-action review of a `batch-shift` run on the shift of 2026-09-30. Its first two items moved to
[#1416](https://github.com/mshamblin5150-code/clinical-skills/issues/1416) and were ruled as
[ADR 0291](0291-a-writing-pass-stages-patient-text-in-a-scratch-root-and-a-hook-refuses-heredoc-writes-there.md)
ruling 1. The two that remained are about what the blind descriptor-agreement reader receives:
retry instructions sent as extra files beside its brief, and a reader that could not see the rule
for where an index route starts. Grilled 2026-10-09 against `main`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The brief already named the route start on the day of the run.** The sentence "join a referral
chain with ' | ', beginning at a term in agreeing_words and ending at the subject code" entered the
reader's instructions in `6191083f` on 2026-09-15, fifteen days before the shift. The reader had
that sentence, could not tell what "a term" meant, tried to read the scanner's source, was refused,
and judged route starts by eye.

**The scanner's test is narrower than that sentence.** `_route_status` in `tools/anchor_scan.py`
takes the route's first index entry, keeps the main term before its first `>`, and splits that term
on commas into alternative spellings. `_route_starts_in_words` drops parenthesized words and the word
`NEC` from both sides, then passes when every remaining word of one alternative occurs in
`agreeing_words` in the same order, not necessarily adjacent. It also passes one case the brief never
states: for a code whose first character is V, W, X or Y, a route whose first entry contains
"sharp object" starts in words that say cut, edge, edged, laceration or sharp.

**The start is the only step of the path the scanner compares with the note.** After the first
entry, `_route_status` checks referral links between steps, the final code's stem, and the
characters the tabular adds beyond that stem. A subterm on the path, such as a site, is never
compared with `agreeing_words`. Driven on 2026-10-09: R19.00 by the route `Mass > abdominal` grades
valid on the words "Reducible groin mass" and invalid on "Reducible groin bulge", so the start is
checked and the site is not. Whether each later step is reached by the note's words is the
reader's judgment under the brief's existing rule that agreement needs note words reaching the
descriptor through an official index path.

**Since [ADR 0301](0301-the-agreement-read-quotes-a-code-label-by-one-convention-stated-in-the-first-brief.md)
ruling 6 the brief is the reader's only copy of its rules.** They are the module constant
`anchor_scan.AGREEMENT_READER_INSTRUCTIONS`, and `skills/icd10-cpt/SKILL.md` names the constant
rather than restating it. A rule the constant leaves vague therefore has nowhere else to be read.

**The retry list is safe to put in a message.** Each finding line `--show` prints for an agreement
read is the note's filename stem, the subject ID, and the finding kind, for example
`note-4: <subject ID> agreeing words are from the wrong place`. No anchor, worksheet, or self-record
text reaches it. `skills/icd10-cpt/SKILL.md` says only that "If a reader's span fails, the reader
retries" and names no delivery; on the recorded shift the orchestrator wrote the retry lists as two
more files under `private/`, one reader's read of them was refused as PII handling, and others read
them without refusal.

## Ruling 1 — the brief states the scanner's whole route-start test

`AGREEMENT_READER_INSTRUCTIONS` states the test above in words: the route's first index entry's main
term, or one of its comma spellings, appears word for word and in order in `agreeing_words`,
ignoring parenthesized words and `NEC`. It also states the external-cause allowance for "sharp
object", and says that the start is the only step the scanner checks against the note: every later
step on the path still needs note words that reach it, and that judgment is the reader's. A test
binds that wording to the scanner's behavior, so the sentence and the check cannot drift apart.

Stating the start alone would let a reader take the mechanical test for the whole agreement test
and accept a path whose later step the note does not support, so the limit is stated with it.

Sharpening only the existing phrase was declined because the external-cause allowance is a real pass
condition the reader cannot discover any other way. Leaving the sentence as it stood was declined
because it was there on the recorded shift and did not suffice.

## Ruling 2 — a retry reaches the reader in the message, never as a file

The blind reader's only file remains its one brief. Retry instructions travel in the message, and
no retry writes another file under `private/` or anywhere else for the reader to open. This binds
every blind agreement read: the `batch-shift` step that runs it and the `icd10-cpt` retry loop it
uses.

A fresh brief limited to the failing notes with `--stem` was declined because it leaves a reader two
briefs of different scope from one run and answers a reading-volume problem the recorded rounds do
not show. Keeping extra files under a fixed name and a written permission was declined because the
permission check refused such a read once and "one file" would stop meaning one.

## Ruling 3 — a retry carries only the grader's finding lines and one fixed sentence

A retry message is the grader's `--show` finding lines for the failing subjects plus one fixed
sentence held as a committed constant beside `AGREEMENT_READER_INSTRUCTIONS`, directing the reader
to redo only those subjects under the brief's instructions and leave every other record unchanged.
The orchestrator composes nothing of its own into a retry. A retry that would need a rule the brief
does not state is a defect in the brief and goes to the tracker; it is not supplied in the run.

Finding lines plus orchestrator guidance restating the brief's rules was declined because it rebuilds,
one shift at a time, the second copy ADR 0301 ruling 6 removed. Anything the orchestrator judges
helpful was declined because no check can hold that boundary, and a coordinator who can see the
anchors can leak them in its own words without noticing. This keeps
[ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)
ruling 7's bar on self-record text and ADR 0301 ruling 1's decline of a per-code location hint, and
narrows what remains.

## What this does not reach

A retry message travels through the orchestrator, so nothing mechanical shows that it carried only
the finding lines and the fixed sentence; ruling 3 is a written rule the after-action review can
read in a transcript, not a gate. Stating the route-start test does not make a reader apply it
correctly. The grade decides the start, the links between steps and the final code; whether a later
step such as a site is reached by the note stays a reading the grade does not check. The writer's
own route check before hand-off is ADR 0296's Writer self-grade, which runs the same test, and
[ADR 0311](0311-a-label-carries-index-words-beside-the-clinician-s-and-a-refusal-quotes-its-official-descriptor.md)
ruling 1, which has the writer look the route up in the index.
