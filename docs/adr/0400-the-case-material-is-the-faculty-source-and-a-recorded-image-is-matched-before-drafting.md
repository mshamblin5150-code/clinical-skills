# The case material is the faculty source and a recorded image is matched before drafting

**Measured at:** 4014ae1d7d8c42cb0ec41b8cd594eeadca5cd723

[#1793](https://github.com/mshamblin5150-code/clinical-skills/issues/1793) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 3) on 2026-10-12. The run quoted the
clinician's own capture of a video case to the classmate as though it were the case, nearly faulted
a choice the classmate had matched to the faculty slide, charged the classmate with an inconsistency
inside the case itself, left unused a recorded image that fit the critique's central defect, and
faulted a thin differential without stating how the clinician's own paper had argued each
alternative. Grilled 2026-10-17 against `main` at the commit above, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The run followed the glossary.** `CONTEXT.md` defined **Case material** as "the fixed data set a
case gives every student, whether a file the course supplies or the clinician's own transcription
of a case presented by video." Only lines the clinician added to his copy were excluded. Declaring
his capture as the case was the defined behavior, so the defect sat in the term rather than in
`peer-critique`.

**The record line can name only a file.** [ADR 0332](0332-case-material-and-case-research-are-declared-context-places-and-both-libraries-come-first.md)
ruling 1 gave every coursework run `CASE-MATERIAL: <path> | none - <reason>`, and
`tools/project_context.py` refuses a declared path the record does not show opened and
fingerprinted. A Canvas-hosted video streams and is not a file, so for a video case the
clinician's transcription was the only thing the line could name.

**No skill says how a run reaches a case video, and nothing transcribes audio.** `peer-critique`,
`discussion-post` and `discussion-reply` never mention a video. `practicum-case-study` reads "the
case study document," which for a video case is the clinician's capture. No module under `tools/`
handles audio, speech or captions.

**The image-reuse sentence is copied five times.** "Reuse a recorded image whole where it fits.
Where none fits, follow imagery-proposals.md" appears in `course-assignment`, `discussion-post`,
`discussion-reply`, `peer-critique` and `practicum-case-study`. The judgment of reuse by fit lives
once, in `skills/_shared/reference/voice.md`. Nothing requires a run to attempt the match.
[ADR 0394](0394-a-proposed-image-is-ruled-at-its-own-stop-before-any-grade-render-or-reader-and-the-ruling-is-the-clinician-s-verified-reply.md)'s
build, [#1743](https://github.com/mshamblin5150-code/clinical-skills/issues/1743), rewrites the same
sentence and had not landed.

**A description of the clinician's paper already has a checker.** Under
`skills/_shared/reference/sourcing.md`, a sentence stating what an opened item says is an **Item
description**, and the heading reader opens that item and compares the sentence claim by claim.
That reader is what caught the Module 3 redrafts that described the clinician's paper more widely
than it reads.

## Ruling 1 — the case material is the faculty's own source

**Case material** is the fixed data set in the faculty's own form: the case document as posted, or
the slides, video and narration of a case presented by video. The clinician's transcription or
shorthand capture of that source is his working material, a way to find things in it, never the
case. Its wording is checked against the source before it is quoted, and before anything is
charged as missing from it. `CONTEXT.md` is rewritten with this record.

A rule in `peer-critique` alone was declined because the term itself licensed the error, and every
coursework skill that reads the glossary would repeat it. Leaving the definition unchanged was
declined because the Module 3 error stays reachable.

## Ruling 2 — the record names the faculty source, and the capture has its own line

`CASE-MATERIAL` takes either a faculty file path, opened and fingerprinted as now, or the course
site's address of the page carrying the case video. A new optional header line names the
clinician's transcription file, fingerprinted and labeled as working material. An address cannot
be fingerprinted, so a video re-recorded between sittings goes undetected; that limit is declared
in the module's limits object rather than hidden.

A run-made verbatim transcript named on the line was declined because every video case would pay
for a full transcription, and the result is again a capture subject to ruling 1. Keeping the line
on the capture with the address beside it was declined because the record would then label the
capture as the case.

## Ruling 3 — the rule lives once beside the record line

The check-before-quoting rule and the narration rule of ruling 4 live in
`skills/_shared/reference/sourcing.md`, beside `CASE-MATERIAL`. `peer-critique` step 1 points to
them rather than restating them.

`peer-critique` alone was declined because `practicum-case-study` and the discussion skills read
the same kind of video case. A shared rule plus a restatement was declined as two copies that can
drift with nothing failing.

## Ruling 4 — a narration-only datum is confirmed by the clinician

Where a datum the work depends on exists only in a case video's narration, the run quotes the
course site's auto-caption with its timestamp, marks it unconfirmed, and the clinician confirms or
corrects the wording before it is quoted or used to fault anyone. A committed transcription tool is
[#1865](https://github.com/mshamblin5150-code/clinical-skills/issues/1865), a separate grilling
ticket.

Requiring the run to transcribe the audio was declined because no committed tool can, and an
instruction a run cannot follow falls back silently to the captions it distrusts. Accepting the
captions with the limit stated was declined because auto-captions mangle drug names, doses and
numbers, the class of datum a critique turns on.

## Ruling 5 — a contradiction inside the case is never the classmate's error

Where the case material contradicts itself, the critique never charges the contradiction to the
classmate. How the classmate handled it is gradable only where a silent choice of one figure
changed a clinical decision, on the standard `skills/_shared/reference/style.md` holds the
clinician to: name both accounts, never reconcile a conflict silently. This sits in
`peer-critique`'s paragraph on what the case supplied.

Barring the subject entirely was declined because a plan built on the wrong one of two figures,
unnoticed, would go unsaid. Adding nothing was declined because the existing scope rule let the
Module 3 charge through once.

## Ruling 6 — a recorded image is matched before drafting, in every coursework skill

Before drafting, every coursework run names the piece's central point, checks it against the
canonical voice model's recorded images, and records which image will carry it or why none fits.
The rule lives once in `skills/_shared/reference/voice.md`, beside the judgment of reuse by fit;
each of the five copied sentences becomes a pointer to it.

`peer-critique` alone was declined because any piece with a central point can have a fitting image,
and the miss was not specific to critiques. Exempting replies and initial posts was declined as a
carve-out that saves a cheap check.

## Ruling 7 — the match is graded mechanically and by the voice reader

A row in the completion check the five skills share refuses a missing match record, a named image
absent from the canonical model's recorded imagery, and a named image absent from the finished
artifact. The existing voice reader gains one question: whether a recorded image fits the central
point that the draft does not use.

An instruction alone was declined because a skipped match looks like one that found nothing. The
mechanical row alone was declined because a stock "none fits" passes it. The reader question alone
was declined because it has no drafting record to judge against.

## Ruling 8 — the image stop shows the match record and the clinician's yes settles it

Where a run proposes an image under ADR 0394 ruling 1, the image stop shows the run's match record
beside each proposal: the recorded images weighed and why none fit. The clinician's yes settles the
match, and ruling 7's reader question skips a point carried by an image he approved there.

Having the reader still ask, returning a finding against an approved image at the go-ahead, was
declined because it reopens a verified ruling and keeps two records about one image that can
disagree. Leaving the interaction to whichever build lands second was declined because it leaves
the one path where both mechanisms fire unspecified. ADR 0394's stop, its domain and behavior
columns, and its yes-or-no ruling are unchanged.

## Ruling 9 — the critique states how the clinician's own paper handled each alternative

In a peer critique, where the clinician's own paper argued alternatives for and against that the
classmate never made, the Clinical Reasoning heading says so and states how his paper handled each
one: argued down, kept, or deferred. Each such sentence is written as an **Item description** of
his **Own submission**, so the existing heading reader checks it against his paper and it never
reads more widely than the paper does. This sits in `peer-critique` step 2.

Requiring it in replies too was declined because a reply is short and conversational, and the
shared rule's "name a shared gap as shared" already covers them. Leaving it optional was declined
because a fault charged without the comparison reads as criticism from nowhere, the Module 3
correction.

## Build checklist

- `CONTEXT.md`: **Case material**, rewritten with this record.
- `tools/project_context.py`: `CASE-MATERIAL` accepts a course-site address as well as a path; the
  new optional capture line is parsed, fingerprinted, opened and bound into the context digest; a
  `DECLARED_LIMITS` row for an address that cannot be fingerprinted; tests through the public
  command, including the fixtures that write the header. Like `CASE-MATERIAL`, the capture line is
  not a declared retrieval under `_has_declared_retrieval`.
  [#1600](https://github.com/mshamblin5150-code/clinical-skills/issues/1600) adds header lines to the
  same field sets and digest, so whichever build lands second keeps the other's lines.
- `skills/_shared/reference/sourcing.md`: both header lines, the check-before-quoting rule, and the
  narration-confirmation rule.
- `skills/peer-critique/SKILL.md`: step 1's pointer; ruling 5 in the scope paragraph; ruling 9 in
  step 2; step 4's sentence reduced to a pointer.
- `skills/_shared/reference/voice.md`: ruling 6's match rule; the other four skills' copied
  sentences reduced to pointers.
- The shared completion row and the voice reader's question of ruling 7, with
  `skills/_shared/reference/voice-read.md` and the five completion graders. An unreadable canonical
  model is incomplete coverage, as for the existing voice-read row, and counts on the one unread
  remainder line [ADR 0393](0393-the-unread-remainder-is-one-line-per-report-that-counts-each-member-once-and-names-a-nonzero-population.md)
  requires. The match record is a new agent-written record kind, so it is read through
  [ADR 0395](0395-a-hand-written-run-record-is-read-through-one-shared-reader-that-refuses-a-control-character-by-line-or-field.md)'s
  shared reader; [#1755](https://github.com/mshamblin5150-code/clinical-skills/issues/1755) builds
  that reader. A clinician edit carried into the Markdown that removes the matched image updates the
  match record rather than failing the row.
- `skills/_shared/reference/imagery-proposals.md` and the image-stop table: ruling 8's match-record
  column, reconciled with #1743's build, whichever lands second.

## Supersedes

- [ADR 0332](0332-case-material-and-case-research-are-declared-context-places-and-both-libraries-come-first.md)
  ruling 1, the words "The tool locates nothing: the run names the file". For a video case the line
  names the course site's address of the video page, and the clinician's capture is declared on its
  own line. The line itself, its exactly-once requirement, the refusal of a reasonless `none`, the
  opened-and-fingerprinted requirement for a declared path, and its place in the confirmed header
  and context digest still stand.
