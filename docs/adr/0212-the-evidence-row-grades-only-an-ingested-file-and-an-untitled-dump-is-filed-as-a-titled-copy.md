# The evidence row grades only an ingested file and an untitled dump is filed as a titled copy

**Measured at:** 038024fcb6a245f2946004ff1cb3158abad4864a

[#1022](https://github.com/mshamblin5150-code/clinical-skills/issues/1022) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2). Its UpToDate dump arrived
without topic titles, `research_ledger.py --evidence` reported every correct UpToDate citation as a
topic the faculty never supplied, and the run rebuilt the titles by hand with no command recording
the work. The ticket blamed `carried_topics` and offered two options that both repair it. Two tracker
sweeps then showed the join does not read that function's result. Grilled 2026-09-13; the clinician
ruled every point below on the same day. Freshness gate `FRESH` at `038024fc`. Nothing is built here;
this is the record the build reads.

## Measured before ruling

### The dump's parse is a gate, and the join reads the store

In `research_ledger._load`, `carried_topics(evidence_text)` decides only whether the membership row
runs; its result is then discarded and the row joins against `accumulated_evidence_topics()`, every
title in the store's per-dump manifests. *Had the parse been the join set, the load would pass it on;
it calls a different function and drops it.* So the untitled dump's single boilerplate "topic" never
reached the join. Its only effect was to be non-empty, which let the row run against a store that
held none of that dump's topics, because `uptodate_store.parse_topics` had refused the ingest.

### A titled dump nobody ingested fails the same way

The tracker sweep of 2026-09-10, at `8e3744e`, ran a temporary store: a titled 22-topic dump never
ingested produced 22 `cited-topic-not-in-evidence` findings, and the same dump ingested produced
none. That measurement is the sweep's and is cited, not repeated here. It is what disqualifies both
of the ticket's options: each changes how the dump is parsed, and a titled dump already parses.

### The store already fingerprints what it filed

Every dump manifest carries `source_sha256`, the digest of the retained source copy, and
`uptodate_store.sweep_unfiled` already decides "filed or not" by that digest. The question the row
needs answered, whether this file is in the store, has an exact mechanical answer.

### The real untitled dump carries no title anywhere

The run directory's supplied dump holds 22 author mastheads and 22 review and update lines. The first
masthead is the file's first line, and the line above each of the other 21 is the previous topic's
closing terms-of-use sentence, so ingest refuses it as `read 21 of 22`. Two of its blocks are
byte-identical from masthead to next masthead. A read of every block found no title slot: no topic
URL, print header, repeated page header, or title line near the masthead. Titles appear only as
related-topic text, not one per block. The Module 2 manifest's digest is that of the run's hand-titled
copy, with the duplicate removed, not of the supplied dump.

### The check-ledger set cannot expect a row conditionally

`checks_ledger.EXPECTED_CHECKS` is a fixed tuple, so a reader row expected only on runs that filed a
titled copy is not available without widening that grader.

## Ruled 2026-09-13

### 1. The membership row runs only on a file the store filed

`--evidence` names a file whose SHA-256 must equal some dump manifest's `source_sha256`. When none
does, the membership row and the UpToDate currency row, which already hangs off it, print
`not graded`; the run sets `coverage_failed`, so it exits 2 with the report printed, and a finding
from any other row still outranks it in the runner's order. The diagnostic names
`uptodate_store.py ingest` as the remedy, or pointing `--evidence` at the exact file that was
ingested. This catches the refused untitled ingest and the never-ingested titled dump with one exact
test.

### 2. `carried_topics` is deleted and the ungraded lines say why

A digest match implies ingest accepted the file, and ingest refuses both a file with no authored
topic body and a partial read, so the parse has nothing left to decide. `carried_topics` and
`evidence_unreadable` are replaced by the not-filed state. The report's two `not graded` evidence
lines state the true reason, either that no `--evidence` was given or that the named file is not in
the UpToDate store. Today they print `no --evidence was given` when evidence was given and could not
be read, one line above a diagnostic saying it was read. The declared limit that describes
cross-referenced topics as outside "the carried set" is reworded to name the filed set.

### 3. Ingest refuses an untitled dump by shape, and the run files a titled copy

`uptodate_store` recognizes an untitled dump without reading UpToDate's wording, so a publisher
rewording cannot break it:

- a masthead with no non-blank line above it, or
- one candidate title line standing above two or more blocks that still differ after ruling 4's
  merge.

It refuses with the count of untitled blocks against the population and names the remedy. The
`practicum-case-study` evidence step directs the run to write a **Titled copy**, keep the
block-to-title mapping in its run directory, ingest that copy, and name it in `--evidence`. The term
is added to `CONTEXT.md`, and **Dump manifest** now says it fingerprints the file filed. No title
is inferred from cross-reference text, because that text is not a per-block slot and would put a
guess into the join key.

### 4. Byte-identical blocks merge at ingest; a shared title over different bodies still refuses

Blocks identical from masthead to next masthead are a repeated paste. Ingest keeps the first, reports
how many it merged, and counts the merged blocks toward the population it read. The retained source
stays the file as supplied, so its digest is unchanged. Two blocks with one title and different
bodies remain a refusal, because that is ambiguous. The hand deletion that made the Module 2 filed
file differ from its source is no longer required.

### 5. A titled copy's titles are declared, not graded

The membership join trusts the titles a titled copy carries. A block titled with a topic the dump
never carried, then cited, passes the row. `research_ledger.DECLARED_LIMITS` gains a row saying so.
The kept mapping keeps the reading auditable, and the after-action review reads the run.

## Rejected options

**Recognize the closing boilerplate, the ticket's option 2.** It reads the publisher's wording and
goes stale when that wording changes. It leaves the never-ingested titled dump firing on every
citation. It also reports a refused ingest as a row that did not run, hiding the refusal.

**Count markers in `carried_topics`, the ticket's option 1.** It copies `parse_topics`' population
rule into a second module, and a titled dump that was never ingested still passes the gate.

**Keep `carried_topics` as a cheap check before the digest.** It keeps the title-above-masthead guess
this ticket was filed over, for a case the digest already decides.

**`ingest --titles <file>`.** It makes the mapping a command's record but cannot verify a title, which
stays a reading. It adds a flag, a second retained source and a second digest the gate must accept,
all for one observed dump. It can be added later without undoing ruling 3.

**Infer titles from cross-reference text.** It would let a guess become the join key.

**An independent reader row for the titles.** The fixed check set would put it on every case-study
run for a shape seen once. It depends on nothing here and can be built if a wrong title is ever
observed.

## What none of this reaches

Whether a titled copy's titles are correct. Whether the file named in `--evidence` is the dump the
clinician handed over, rather than some other ingested file. Whether a filed dump is the whole of what
the faculty supplied for the module. A dump carrying none of the three topic markers remains outside
ingest's population floor, as `uptodate_store` already declares.
