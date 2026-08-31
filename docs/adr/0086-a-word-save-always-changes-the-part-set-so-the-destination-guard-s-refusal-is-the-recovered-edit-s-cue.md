# A word save always changes the part set so the destination guard's refusal is the recovered edit's cue

[#675](https://github.com/mshamblin5150-code/clinical-skills/issues/675) reported that a clinician
Word save changes `docx_write`'s archive part set, so the destination guard refuses every later
re-render, while `CLAUDE.md` records the opposite as a measured fact. Grilled 2026-08-30 against
`origin/main` at `0d26b95`, freshness gate `FRESH`. **Eight decisions, all the clinician's, all on
that date.** Nothing is built here.

The ticket's own framing is preserved because it was right about the defect and wrong about its
depth. It says of [#424](https://github.com/mshamblin5150-code/clinical-skills/issues/424)'s row,
*"I am not claiming the measurement was wrong when it was taken. I am claiming it does not
generalize."* The measurement was wrong when it was taken, and the reason is in the instrument.

## Measured before ruling, 2026-08-30

`tools/docx_word_probe.ps1` opens `word-saved.docx`, calls `.Save()`, and closes. **It never edits
the document.** Word declines to write an unmodified document, so nothing in that sequence
exercises a save at all.

Three variants were run against installed Word, version 16.0, build `16.0.20326`, on a document
this renderer wrote. The instrument is a scratch PowerShell script driving Word COM, and it is
corroborating evidence rather than the record: on [ADR 0008](0008-word-is-a-one-time-calibration-instrument.md)'s
terms the committed row comes from `tools/docx_word_probe.py --word` and from nothing else.

| variant | file rewritten | parts added |
| --- | --- | --- |
| open, `Save()`, no edit — the #424 probe verbatim | **no**; `Saved` was already `True` and the mtime did not move | none |
| open, type text, `Save()` | yes | 8 |
| open, set `Saved = $false`, `Save()`, no edit | yes | 8 |

**The third variant is the one that decides the question.** It is unedited and it is written, and it
adds exactly what the edited save adds. So the variable is not whether the document was edited, and
it is not the open-versus-closed condition the first tracker sweep proposed as the discriminator. It
is only whether Word wrote the file. Any real edit means it did.

**A second measurement settles the paragraph-text question that decision 6 rests on.** The unedited
rewrite's paragraph-text sequence is identical to what `docx_write` emits, and the edited one's is
not. A text-level comparison therefore has a live negative control. It was taken on a two-paragraph
document, so it is a floor: tables, lists, hyperlinks and the header field are unmeasured.

**The added set is not stable.** This probe recorded 8 additions and the live run that filed the
ticket recorded 9, on one machine five days apart; the difference is `docProps/custom.xml`. That
disagreement is the evidence decision 3 turns on and it exists nowhere in the tree today.

## What rested on the no-op

Four things, and the fourth had not been noticed by the ticket or by either tracker sweep.

1. `skills/practicum-case-study/reference/word-renderer-calibration.json`'s `word_save_guard` row,
   whose `original_and_saved_part_sets_equal` and `destination_guard_would_refuse` both invert.
2. `tools/test_docx_word_probe.py::test_the_word_save_guard_limit_is_recorded_from_the_same_instrument`,
   which asserts both values, so the suite pins a no-op as evidence.
3. `docx_write.NOT_GUARDED`'s first row, which names a closed Word save as a real declared limit.
4. **`docx_write.refusal`'s message.** Its docstring records that `a Word save, most likely` was
   removed from the message on this measurement's authority — *"Word 16.0 was measured on #424
   preserving the exact part set after a save, so the message cannot diagnose Word from a changed
   set at all."* The guess was correct and was deleted by a no-op. This is the sharpest form of the
   defect, because the false measurement did not merely sit in prose: it made a live diagnostic
   worse.

`docx_word_probe.word_report` would reproduce the row today, which is why decision 1 is about the
instrument rather than about the record.

## What is ruled

**1. The instrument is repaired and the row is retaken.** `word_report` and its PowerShell probe
edit the document before saving. Retiring the row instead was rejected: it removes the row without
removing the blind spot that produced it, and ADR 0008's whole ruling is that a Word claim rests on
a Word measurement.

**2. The Markdown is the authoritative artifact on both rendering paths.** When a clinician's saved
document and the graded Markdown disagree, the Markdown moves: the change is read back out of the
document and written into it, and only then may a re-render proceed. The `.docx` stays derived, as
it is everywhere else in this repo.

**3. The destination guard's predicate does not change.** `written_by_this_renderer` stays set
equality. Recognizing Word would delete the signal decision 2 now depends on.

**4. The refusal message names three causes, reports the delta, and names the remedy.** An editor
saved it, another writer produced it, or an older version of this renderer wrote it; the parts the
archive carries that this renderer does not write, and any it is missing, are printed beside that;
and the remedy is *read it, recover the edit, then force* rather than the flag alone. The guard does
not branch on the delta. It hands it over, which is `differential_scan`'s candidates and
`block_scan`'s wrap count arriving on a refusal.

**5. The retaken row carries the verdict, the observed additions, and the variance**, and the
refused allowlist is written down as an executable test — the superset-plus-known-parts rule
implemented and run against both recorded observations, asserting that it disagrees with itself.

**6. Both skills state the rule and `tools/discussion_post_scan.py` gains a row** comparing the
archive's paragraph text against what `docx_write.blocks` renders from the Markdown. It must be
measured against a real rendered post before it is believed; if a real post raises a false alarm the
row reports rather than grades, and the prose stands either way.

**7. This record carries the ruling and ADR 0008's facts are corrected in place** on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms. ADR 0008's ruling — Word is a one-time calibration instrument — is untouched and is
reaffirmed by this: the defect is that the instrument asked the wrong question once, not that it
should be replaced by a permanent Word test.

**8. The vocabulary is a destination guard with two signals, and a recovered edit.** Both land in
`CONTEXT.md`.

## Why the allowlist is refused

Decision 3's alternative is *the saved set is a superset of `PART_NAMES` and every extra part is one
Word is known to add*. It is refused on three grounds, in increasing order of weight.

**It is an allowlist of parts that look harmless**, which is the shape this repository already
refuses in `guidelines_extract`'s symbol-glyph census, and for the same reason: the residue such a
list hides is invisible precisely because the list was written from what somebody had already seen.

**Its list is falsified by its second observation.** Two measurements on one machine five days apart
disagree by one part. A list that is wrong the second time it is checked is not a list.

**And it deletes the signal.** Under ruling 2 the refusal is what tells a run there may be an
unrecovered edit. A predicate that recognized Word and passed it would let the run re-render
straight over the clinician's change with nothing raised. The narrowing would therefore buy quiet on
the one path where quiet is the failure.

## Rejected alternatives

**Make the saved document authoritative.** Rejected. It is what the live run did and it works, but
it answers *which artifact is the work* differently on `discussion-post` than on
`practicum-case-study`, for no reason a reader could reconstruct, and the sync it requires is a
lossy reverse transform: `docx_read` yields paragraph text, not the Markdown the graders read.

**Record the divergence and change neither artifact.** Rejected. `discussion-post` step 8 has that
rule for the *posted board*, where nothing can be fixed because submission has happened. Applying it
before submission ships a graded artifact that knowingly differs from what was handed in.

**Prose in the skills and no grader row.** Rejected as the resting place, though it is a legitimate
partial. The renderer's remedy has been written down on `discussion-post` since it shipped and the
live run still had to invent the read-back, which is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail* landing on this ticket's own subject.

**Two records, one for the measurement and one for artifact authority.** Rejected. The halves are
one decision in both directions: the guard stays adversarial because the read-back gives its
refusal a job, and the read-back is enforceable because the guard still fires. Splitting them puts
the rule in one file and its reason in another, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape with a file
boundary between the halves.

**Condition the refusal message on the calling skill.** Rejected. `docx_write` is a library and does
not know which skill invoked it, and *read it before you overwrite it* is correct on every path.
