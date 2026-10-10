# A sentence about who one of the clinician's documents is by or for needs his word, not the document's

**Measured at:** 4c1cc8958837c7c9aa4144f187e8e879c7fce86f

[#1487](https://github.com/mshamblin5150-code/clinical-skills/issues/1487) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 10) on 2026-10-01. The run opened one
of the clinician's own documents, read its purpose paragraph and the lines matching its search, and
wrote a first-person sentence attributing the document to the organization its opening named. He had
written it for a different organization that the text names only as a parent. Grilled 2026-10-10
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Reading the whole document would not have caught it.** Under ADR 0272 ruling 10 each heading reader
opens the recorded project-context items itself. Two independent heading reads returned
`CONTEXT-VERDICT: agrees` on the wrong sentence, because the document's own opening states the wrong
organization, and the full text names the right one only as a parent. The sentence was fixed by the
clinician's correction, not by the run's later full read. A read-whole rule therefore cannot tell the
wrong sentence from the right one, which is the discrimination test `CLAUDE.md` requires before a
measurement settles a claim.

**The question the run asked was compound.** It asked "is this accurate as written?"; his "yes, I
drafted it" answered authorship and was taken to answer the organization as well.

**The verdict vocabulary has no value for this case.** `heading_read.py` accepts `agrees`, `narrows`,
`contradicts`, `sources-conflict`, and `none`. When the only opened item that speaks to a claim is the
document describing itself, the reader has nothing to set against it, so `agrees` is the only value it
can give.

**[#1485](https://github.com/mshamblin5150-code/clinical-skills/issues/1485) was ruled the same day.**
It adds a drafting-time paragraph under `sourcing.md` "Draft order": statements about the clinician
and his projects agree with the opened items. This record is that rule's exception, and the clinician
ruled the two tickets independent.

## Ruling 1 — the defect is trusting a document's self-description, not reading part of it

A document's description of itself is never evidence of who wrote it, whom it was written for, or what
it covers. The proposed rule that an opened document is read whole was declined: it adds reading cost
on every run and does not discriminate the failure. With no read-whole rule there is nothing to grade
for it, which closes the ticket's open question about recording a read count.

## Ruling 2 — the rule reaches authorship, audience, and scope

A draft sentence is covered when it states who wrote one of the clinician's documents, which
organization or audience it was written for, or its scope: what it governs, covers, or applies to.
Content the document states about its subject, such as a callback interval, is not covered; the
document can honestly attest that, and the existing heading-read pairing reaches it.

Every first-person sentence resting on one of his documents was declined as a trigger because it
spends his attention on lines the document itself settles. Authorship and audience alone were declined
because the failure on this run was a statement of whom the document serves, which is scope.

## Ruling 3 — an opened memory settles it; otherwise he is asked, and the answer is written to memory

A covered sentence stands when an opened memory file states the claim. The document's own text never
counts. Otherwise the run asks him, and his answer lands as a memory write so the next run finds it
settled, on the terms ADR 0272 ruling 11 already sets for his answers.

Asking on every run was declined as repeating questions he has answered. Keeping the answer for one run
only was declined because it is lost when the run ends.

## Ruling 4 — one claim per question

The run asks about authorship, audience, and scope as separate questions, one at a time. Each names
what the document says about itself so he can see what he is correcting. A single message listing the
claims was declined because a reply answering only the first item looks complete, which is how the
compound question failed.

## Ruling 5 — the rule lives in "Draft order", directly after #1485's paragraph

The rule is written once in `skills/_shared/reference/sourcing.md` under `### Draft order`, directly
after the paragraph #1485 adds, or as that section's first paragraph if #1485 has not been built. The
five coursework skills' pointer sentences, as #1485 rewrites them, already name applying retrieved
context while drafting, so no skill file changes for this ruling.

The retrieval section the ticket proposed was declined because the drafter reads it before retrieval,
apart from the rule this one narrows. Copies in five skill files were declined as five texts to keep in
step.

## Ruling 6 — the heading read gains an `unconfirmed` context verdict

A heading reader that finds a covered sentence and no opened memory file stating its claim reports:

```text
CONTEXT-VERDICT: unconfirmed - <location>, <the authorship, audience, or scope claim no opened memory states>
```

It is a context-defect finding like `narrows`, `contradicts`, and `sources-conflict`, cleared by the
clinician's answer written to memory and a fresh heading read. This extends the verdict list ADR 0272
ruling 10 fixed; it overturns none of that ruling's other terms.

A written rule left ungraded, as #1485 was, was declined because here the backstop is the thing that
failed: two clean heading reads passed this sentence. A record field saying the question was asked,
graded by `project_context.py`, was declined because it is the run's own claim about itself and a run
that skipped the question can still write it. The new verdict discriminates the case: on this run no
opened memory stated whom the document served, so the reader would have stopped it.

## What this record does not settle

**Whether a sentence is a covered claim.** Classifying a sentence as authorship, audience, or scope is
a reading, declared beside the heading-read limits rather than graded.

**Whether memory files are opened at all.** The verdict can find a settling memory only among the
opened items, and a run that opens the memory index but not the files beneath it gives the reader
nothing to find. That gap is [#1600](https://github.com/mshamblin5150-code/clinical-skills/issues/1600)'s.
Until it is ruled, a covered sentence on such a run reports `unconfirmed`, which fails toward asking.

**A memory written mid-run and the completion gate.** Writing his answer to memory moves the memory
index the project-context record hashed. That interaction is
[#1496](https://github.com/mshamblin5150-code/clinical-skills/issues/1496)'s and is not changed here.
