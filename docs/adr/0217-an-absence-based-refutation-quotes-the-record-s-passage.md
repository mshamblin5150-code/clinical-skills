# An absence-based refutation quotes the record's passage

[#1033](https://github.com/mshamblin5150-code/clinical-skills/issues/1033) was filed from a
`course-assignment` run of 2026-09-03. A refutation context attacked a claim record by searching its
source for a phrase, found nothing, and reported that the record's supporting language did not
exist. The search string was a near miss of the source's actual wording. The orchestrator measured
the source itself, found the language present, and rejected the refutation. Had it accepted the
return, a correct record would have been repaired into a wrong one.

The ticket proposed a **positive control**: an absence names the string searched, the instrument,
and a control string the same instrument found in the same source.

Grilled 2026-09-13 to an empty frontier. **Ten rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. The tracker sweep that normally closes a grilling
was **limited to the tickets this record moves**, by the clinician's word for that day only; it is
not a precedent.

## Measured before ruling, at `173d6d7`

**The proposed control does not discriminate the recorded failure.** The instrument in the incident
worked and the source was readable; the query was wrong. A control string on the same source would
have been found, the rule would have been satisfied, and the absence would have stood. The control
prints the same thing whether the absence is real or a near miss, so by `CLAUDE.md`'s discrimination
rule it settles nothing about the claim it was filed to protect. What it does establish, that the
instrument reached the source, is already ADR 0149 rule (ii)'s subject.

**No claim record says where its support sits.** The sourced-record templates in `course-assignment`,
`discussion-post`, `discussion-reply`, `peer-critique` and `practicum-case-study` carry `RESTATEMENT`
(what the source says), `RESOLVED` (the address opened) and `PAGE-YEAR` (where the *year* is stated).
None locates the supporting language, so a refuter has no named place to read.

**The ledger cannot tell an absence-based refutation from any other.** In `tools/research_ledger.py`
every `REFUTATION: refuted` fires `REFUTED_CITATION`, a failure row, whatever the reason says. A wrong
year, a wrong reference and a failed phrase search are the same verdict to the grader.

**A sourced field added to one tuple reaches every consumer.** `REQUIRED_WHEN_SOURCED` holds nine
fields. `SOURCE_FIELDS` is that tuple, so the rule forbidding source fields on a sourceless record
covers any addition without a new row, and `REFUTATION_EVIDENCE_COMPLEMENT` is derived from it and
imported by `deck_scan`, `discussion_post_scan` and `discussion_reply_scan`. The recognized-field
pattern in the same module lists field names explicitly and does not derive from the tuple.

**No field has been grandfathered.** `SECOND-ROUTE`, `STATED-EXPIRY` and `INSTRUMENTS` each joined the
record without a cutoff for older ledgers, and the module carries none.

**The glossary names three of the four candidate words already.** **Anchor** is the `icd10-cpt` term
for note text supporting a code, **Span** is a named page range of a guideline, and **Source locator**
is a threshold row's pinned passage address; `RESOLVED` already carries the locator sense for a
claim record. No entry or ledger field uses *passage*.

**Not re-derived**: the 2026-09-03 run itself. Its ledger lives under `scratch/`, and the ticket body
is the only committed account of it.

## Ruling 1. An absence rests on a read, not on a search

A refutation that reports a record's supporting language absent quotes what the source actually says
at the place that language was claimed to be. A string search may lead a refuter to that place; it
never settles the question.

**The positive control is refused.** It checks that an instrument is live, which ADR 0149 rule (ii)
already governs, and it cannot see a query that missed the source's wording. The quoted read contains
the control: a passage quoted from the source proves the instrument reached it.

## Ruling 2. The rule binds refutation returns and leaves research returns alone

A research absence becomes `STATUS: unsourced` and loses a citation nobody had. A refutation absence
becomes `REFUTATION: refuted` and removes a record that was sourced and possibly right. ADR 0149
ruling 7 measured that asymmetry. Research negatives stay under ADR 0149 rule (i): they report the
corpus read and what was not opened.

## Ruling 3. A sourced claim record gains `PASSAGE`

`PASSAGE: <where in the source the supporting language sits>` is written by the research pass, which
was on the page when it read the support. It is required on a `sourced` record and forbidden on an
`unsourced` or `unreadable` one. It joins `REQUIRED_WHEN_SOURCED`, which carries it to the
sourceless-record rule and to the three graders importing the complement, and it joins the
recognized-field pattern by hand.

**Folding the location into `RESTATEMENT` is refused**, because nothing could then tell a restatement
that locates its support from one that does not. **Letting the refuter find the place itself is
refused**, because it discards what the research pass already knew and turns every refutation back
into an open search.

## Ruling 4. The field is named `PASSAGE`

`ANCHOR`, `SPAN` and `LOCATION` each collide with a filed sense: a code's supporting note text, a
guideline's named page range, and the locator `RESOLVED` and **Source locator** already carry.
`SUPPORT` names what the field is for rather than what it holds, and reads as a verdict. `CONTEXT.md`
gains **Passage**.

## Ruling 5. `PASSAGE` is graded for presence and substance only; the quote is a declared reading

Presence and the sourceless prohibition come from the existing rows. **A bare row is refused**: a
page number alone is a complete location for a one-paragraph page or a table, so a row requiring more
would fail correct records.

**Grading the quote is refused.** Telling an absence-based `refuted` from any other needs a matcher
over the refutation's prose, which ADR 0149 ruling 5 and ADR 0042 ruling 2 both refused; a quoted
wrong year and a quoted near miss would both satisfy one. `research_ledger.DECLARED_LIMITS` gains a
declared-reading row stating that the grader cannot establish that a refutation reporting absent
language read and quoted the record's `PASSAGE`.

## Ruling 6. An absence refutation without the quote is a defective return, not a verdict

The orchestrator does not write it to the ledger. It re-briefs a refutation leg that must read
`PASSAGE` and quote it. Until a compliant return arrives the record's refutation evidence is empty,
and `sourcing.md` already refuses such a record the ability to certify a value.

**Recording it as `REFUTATION: unreadable` is refused**: that value means an instrument refused the
read, the source here was read, and it would demand an `INSTRUMENTS` pair describing a failure that
did not happen. **The orchestrator checking `PASSAGE` itself is refused**: the orchestrator writes the
ledger, and the writer of a record is never its second reader. **Accepting the verdict and letting the
rewrite settle it** is the incident.

## Ruling 7. A `PASSAGE` that does not hold the language is refuted, and correcting it reopens the refutation

A refutation that quotes the named passage and finds the language absent returns `refuted`. That is a
correct finding about the record as written, even where the support exists elsewhere in the source.
The repair corrects `PASSAGE`, and a record whose `PASSAGE` changed needs a fresh `REFUTATION` and
`SECOND-ROUTE`, on the terms `sourcing.md` already sets for a changed heading.

## Ruling 8. `PASSAGE` is never inherited

`discussion-post` lets a claim inherit `REFERENCE`, `RESOLVED`, `PAGE-YEAR` and `STATED-EXPIRY` from a
page already read in the same ledger, because those describe the page. A passage describes where one
claim's support sits on it, so it belongs to the claim and is written fresh on every record.

## Ruling 9. There is no cutoff for older ledgers

No earlier sourced field was grandfathered, and this one follows them. A ledger written before
`PASSAGE` fails `missing-field` when re-graded.

## Ruling 10. The text lives in `sourcing.md`; the field lives in the five templates

The rule is written once in `skills/_shared/reference/sourcing.md`, on ADR 0149 ruling 4's terms,
because every research and refutation brief already reads that file first. The `PASSAGE` line is
added to the sourced-record templates of the five skills named above, and to `practicum-case-study`'s
worked example so the scanner test over it stays green.

## What this record does not settle

**Whether a refuter actually read and quoted the passage.** Ruling 5 declares it a reading, and
nothing here narrows that.

**Whether a research return's absence should also quote a place.** Ruling 2 leaves research negatives
under ADR 0149 rule (i); nothing measured here argues for widening it.

**Whether a quoted passage is the right one.** A refuter can quote the named place faithfully while
the record names the wrong place; ruling 7 turns that into a correct `refuted`, but no check can
confirm that the passage the research pass named is where the support really is.
