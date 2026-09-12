# An extract entry's kind names its envelope and a matcher may label where it may not reduce

[#1014](https://github.com/mshamblin5150-code/clinical-skills/issues/1014) was filed on 2026-09-10
by both passes of one `practicum-case-study` after-action review: `tools/aar_scan.py --extract`
labels harness text `KIND: clinician`, so a subagent's finding read as the clinician's correction
and a compaction summary read as his words. [ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 1 makes the corrector the review's central signal, and both errors push attribution the same
way.

The ticket listed four defects and three decisions. **Measurement retired one decision's instrument,
merged two of the defects into one, and found a fifth the ticket did not have.**

Grilled 2026-09-12 to an empty frontier. **Thirteen rulings, by the clinician, on that date.**

## Measured before ruling, at `9c78d3f`

Freshness gate `FRESH` at `9c78d3f` before any reading. Every Claude-format figure is `reduce_transcript`
driven over 386 transcripts in 177 `clinical-skills` project directories under `~/.claude/projects/`
— the harness's state, not this repository's, so nothing committed re-derives one.

**The candidate population.** `tool-status` 49,075; `tool-call` 49,024; `assistant` 17,512;
`clinician` 4,280; `subagent-result` 1,775.

**The `clinician` bucket partitions, and the three classes are disjoint.** 2,571 carry no flag and no
envelope; 836 carry `isMeta`; 827 open `<task-notification>`; 21 `<system-reminder>`; 11
`<command-name>`; 7 `<local-command-stdout>`; 2 `isCompactSummary`; 1 `<ci-monitor-event>`. *The
earlier sweep on this ticket could not compute the overlap and the partition is what settles it:
`isMeta` and the notification prefix share no row.*

**The inversion, which is the ticket's items 1 and 3 being one defect.** Of 1,775 `subagent-result`
entries, **1,593 contain only launch metadata**, because a backgrounded `Agent` returns later; and
**510 of the 827 notifications carry a `<result>`** while labeled `clinician`. *If the kinds were
sound, the launch-metadata count would be 0 and the notification-borne-result count would be 0; they
are 1,593 and 510.*

**`isMeta` is not one thing.** 817 of 836 are skill-prompt injections. The other 19 are 5 image
pastes, 5 harness resumptions or re-invocations, 1 peer session's message, and 8 command-delivered
prompt bodies. *A rule keyed on the flag alone demotes the clinician's own screenshots.*

**The launch-versus-result gap reproduces.** 1,580 background launches, ~504 joined to a
notification, **1,076 with no notification anywhere in the project directory**. Both join keys are
present in the data — 827 of 827 notifications carry a `task-id`, 792 of 827 a `tool-use-id`, and
1,593 launch bodies an `agentId` — *so this is a missing result and not a missing key.* Why the
1,076 are absent is unmeasured.

**Two instruments of this session were wrong first and are recorded because the next reader reaches
for them.** A first-line anchor on the notification envelope matched 827 of 827 historical rows and
would have missed the banner-prefixed wrapper; the measurement was retaken on containment.
**This paragraph claimed that banner occurs 0 times in the 386 transcripts, and that is false — see
correction 5.** And the first launch-accounting join was launches to `tool_result`, which returns
**1,770 of 1,770** on every transcript and discriminates nothing — it is the ticket's own item 4
arriving on the ticket's own decision 3.

**The wrapper is a moving target and the harness says so.** 208,498 of 271,839 rows carry a `version`
field, spanning 16 versions from 2.1.220 to 2.1.266.

**The injection hole is latent.** 0 of 4,276 kept rows contain a line opening `## ENTRY:`, while
`write_extract` writes bodies raw and `_extract_metadata` scans every line of the file for that
marker.

**The second transcript format is barely read.** **Three populations, and the selector for each is
named because the correction below is that they were conflated.** `find ~/.codex -name '*.jsonl'`
gave 5,189 files and 14.3 GB; `grep -rl clinical_skills ~/.codex` gave 1,942; and **the 60-file
sample was drawn from `~/.codex/sessions/**/*.jsonl`, which holds 1,204** — so the sample's
denominator is 1,204 and never 5,189. Over that sample: 349 `role: user` messages, **all labeled `clinician`**; 71 carry a
harness envelope (`<recommended_plugins>` 27, `<codex_delegation>` 23, `<environment_context>` 21);
278 carry no tag; **0 carry any harness flag**, so two of the three limbs available on the Claude side
do not exist there. The 349 are only **72 distinct** bodies, because Codex re-sends context each
turn. Its row types are `event_msg` 5,987, `response_item` 5,167, `turn_context` 340,
`token_usage_record` 142, `inter_agent_communication_metadata` 70, `world_state` 68, `session_meta`
60, `compacted` 23 — **eight, and this sentence published six until the correction below** — and
`reduce_transcript` reads `response_item` only, so Codex compaction and Codex delegation are both
structural and both unread. There is no `user_message` event, so nothing marks a typed turn.

## Ruled 2026-09-12

### 1. A matcher may label where it may not reduce, and the remainder is the condition

ADR 0109 ruling 9 rules that *reduction by shape is safe; reduction by content is a matcher, and a
matcher never turns a partial read into a clean whole.* Nothing here reduces. But recognizing a
`<task-notification>` is reading content, and ruling 9 does not contemplate it, so the relationship
is stated rather than left to be inferred.

**Labeling by content is permitted where reduction by content is not** — because a wrong label is
visible to the reader holding the body, while a wrong drop is visible to nobody. **The condition is
that the unrecognized remainder is printed**, so a matcher that has gone stale reports a gap rather
than a clean partition.

**This extends ADR 0109 ruling 9 and does not amend it.** That record is a ratified fourteen-ruling
account of one grilling on one date; editing a ruling inside it makes it stop being what it says it
is. ADR 0059's naming of ADR 0033 ruling 3 is the convention followed.

### 2. A kind names the envelope, never the origin

The defect is not that the extract failed to say where content came from. It is that the extract
**asserted** an origin it had not established, in the one direction that inflates the clinician's
role.

So `task-notification` says the harness wrote this wrapper. `subagent-launch` says a tool
acknowledged a launch. `subagent-result` says a return is in this body. `clinician` narrows to its
true meaning: **a user row with no harness flag and no recognized envelope.**

**The reader does the rest**, which is ADR 0109 ruling 2's own division — detection mechanical,
classification adversarial. Reading inside the envelope to set a kind was priced and refused: it buys
the classifier one inference it can already make from the body in front of it, and pays a second
moving matcher for it.

### 3. The label is keyed on three things and the remainder is printed

Row shape, the harness's own row flags, and a declared envelope set, matched by containment rather
than position. Flags are shape — `isMeta` and `isCompactSummary` are fields the harness writes onto
the row.

### 4. A flagged row matching no envelope is `harness-meta`

`isMeta` establishes *the harness wrote onto this row*. It does not establish *the clinician typed
this*, and on the 19 unrecognized rows it is wrong about roughly three quarters of them in the
ticket's own direction. The cost is the 5 image pastes, which carry a placeholder and no prose, so
there is no correction in them to lose; his words are in the adjacent typed turn either way.

`skill-prompt` takes the **conjunction** of the flag and the opening, so only the genuinely
unrecognized fall through.

### 5. `subagent-result` splits, and nothing leaves the population

The 1,593 launch-metadata entries become `subagent-launch`; `subagent-result` keeps only a body
carrying a return. **Both halves are relabels.** A launch acknowledgement is not a result and must
stop claiming to be one, but it is still an entry and the population does not narrow.

### 6. A prior pass's verdicts are marked by identity and never excluded

On a resumed run the pass-1 classifier's return lands after the pass-1 watermark, so it is in pass 2's
population by construction, and the skill briefs that reader as fresh. The record now carries the
extract identifier of the entry holding its classifier's return, and the next extract labels that one
entry `prior-review` **by identity, not by matching its body**. The brief says: re-derive, do not
adopt.

**Excluding it is refused, and not on the population rule alone.** Exclusion by a self-declared
identifier lets a pass delete an entry from the next pass's population by naming it, which is exactly
the invisible veto ADR 0109 ruling 8 closes. The same field used to label cannot do it: a wrong
identifier mislabels one entry, it cannot hide one. **Same information, one failure mode instead of
two.**

**It is a finding whenever the run has a prior watermark**, so a resumed review cannot silently fall
back to an unmarked population.

### 7. Launch-versus-result accounting is reported and never graded

Over the extract's own population: launches, launches joined to a result, the unjoined remainder, and
the count of notifications carrying neither join key.

**The join reads inside the envelope, and that is not ruling 2 reversed.** Ruling 2 refuses an inner
matcher setting a **kind** — an assertion that travels to the classifier and is believed. A count
that always prints its denominator and changes no exit status is the opposite act, and it is
`differential_scan`'s orphan count and `case_study_scan`'s em dashes.

**Two bounds on what it may say.** Scoped to the extract's own population, never the corpus: 1,076
unjoined of 1,580 is a number nobody can act on, while *4 launches, 1 result* in one window is the
finding. And it claims **no result in this population**, never *no result was produced* — compaction
and cross-directory delivery are both live and neither is measured.

**Not a finding.** ADR 0109 ruling 7 already declares subagent silence permanent, and grading a
remainder whose cause is unmeasured fails honest runs.

### 8. The remainder is three instruments, and the one that discriminates is the gap

An undeclared-tag count; the harness version set printed as a bare fact; and ruling 7's
launch-versus-result gap, named in the limits object as the drift detector.

**The version field is not a gate.** Sixteen bumps in this corpus, nearly none of which moved a
wrapper, so a warning on *version outside the measured range* fires after every release — a nag on a
hot path, which ADR 0109 ruling 4 refused here once already. Printed bare it costs nothing and
carries its own coverage, since 23% of rows have no such field.

**The gap is the real detector because it needs no recognition of the new wrapper.** Launches are
counted structurally from the tool result; results are counted by joining inside the envelope. If the
envelope matcher stops recognizing notifications, the launch count holds and the joined-result count
collapses. *`subagent-launch: 12, joined results: 0` in a window that plainly ran readers is one
number the matcher does not produce set against one it does.* The undeclared-tag count alone prints 0
whether the vocabulary is complete or the next wrapper is unrecognizable, and therefore settles
nothing.

### 9. The vocabulary is a declared object and the extract carries a generated legend

It is five bare literals inside `reduce_transcript` today, asserted once as a list in a Codex test,
and named in no ADR and no line of `skills/aar/SKILL.md`.

It becomes `ENTRY_KINDS` — **not `KINDS`**, which is already the finding-kind tuple the shared
conformance kit binds through `tuple(ROWS) == KINDS` under ADR 0118 ruling 2. Two objects called
kinds in one module, one under a family-wide invariant, is a trap.

**`write_extract` emits a legend derived from it**, because the classifier is a fresh context given
only the extract and the memory index and cannot follow a pointer into the module. `skills/aar/SKILL.md`
and `CLAUDE.md` point and copy no row. Enumerating the kinds in the skill was refused: two hand-kept
copies of one vocabulary with nothing between them is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220),
and the prose copy is the one that goes stale.

Bound by an **AST walk** asserting every `Candidate(...)` kind argument is a member — not a substring
search, which this module's own docstring would satisfy while explaining the vocabulary — and by
**two-directional** envelope-table parity.

### 10. Entry bodies are length-prefixed

Each entry writes `TEXT-LINES: <n>` and the reader consumes exactly *n* lines. No escaping, no
scanning, and a body cannot be read as structure whatever it contains.

Ruling 6 is what makes this due now rather than later: a prior classifier's return is the body most
likely to quote entry identifiers in heading form, because that is the shape the record template
uses. Today the collision inflates `identifiers`, fires `population-mismatch`, and **sends the next
reader to hunt the classifier, which is the one place the defect is not.**

Escaping was refused: it changes the bytes the classifier reads, and the reader's whole job is judging
wording.

### 11. Both transcript formats are first-class, and each half is built from its own kind of evidence

**Structure can be closed; content cannot.** The Codex **row and payload type vocabulary is measured
exhaustively** across the 1,942 rollouts naming this repository — two keys per line, so it streams
without parsing bodies — and `compacted` and `inter_agent_communication_metadata` become first-class,
as `isMeta` is on the Claude side. The **envelope table stays evidence-seeded** from recorded
instances with its remainder printed, because envelopes keep growing.

**Declaring the row types from a 60-file sample is the avoidable error**, and that sample has already
turned up two the code does not read — fair warning that a third exists. Shipping the Claude fix and
declaring Codex unreached was refused: the branch is reachable, and it over-asserts more freely than
the one it was modeled on, labeling 349 of 349 user messages `clinician`. Claiming the mechanism
understands Codex while `compacted` rows go unread claims it in the one register — compaction
summaries — the ticket opened with.

The repetition needs no ruling: once the injections are labeled, five copies are five labeled
duplicates rather than five phantom clinician turns, and nothing narrows.

### 12. The format is versioned and the record requirement takes a dated cutoff

An explicit `FORMAT:` field; a missing one is version 1; **an unrecognized one is exit 2, did not
scan, never a guess.** Ruling 6's field becomes a finding only for records written on or after a
declared UTC cutoff, which is `tracker_filed_from.FILED_FROM_CUTOFF`'s arrangement already in this
tree.

**The extract header is read to its blank-line terminator rather than by a fixed line count**, which
is the repair [#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066)'s `aar_scan`
lead actually needs. The header `write_extract` emits is **exactly 8 lines** and `_extract_metadata`
reads `lines[:8]` — flush, so this ruling's own `FORMAT:` field still fits and **ruling 9's generated
legend is the second addition that silently drops the last field line**. Reading to the terminator is
reading the structure the writer already emits, not widening a matcher, so it stays inside #1066's
*what must not come out of this*. *(Correction, 2026-09-12: this paragraph was missing. The repair was
ruled in the grilling and recorded only under* Rejected options *below, where a builder working the
ruling list would never reach it — found by the tracker sweep of this record's own branch.)*

**A tolerant reader is refused outright.** Falling back to scanning when `TEXT-LINES` is absent keeps
ruling 10's hole alive permanently, reachable by any extract that omits a field. *A framing that can
be declined is not framing.* A hard cutover is honest and converts every historical review into a
finding, misattributed the same way ruling 10 describes.

### 13. The extract gets its own finding kind

An extract-side parse failure reports `unscannable-review` today, naming the record when the problem
is the extract. It becomes a row of its own — an addition to `ROWS`, which `tuple(ROWS) == KINDS`
already watches.

## What this does not reach

**Why 1,076 background launches have no result in the transcript.** Never delivered, another project
directory, or removed by compaction — all live, none measured. Ruling 7 reports the gap and explains
none of it.

**Whether a label is right.** Ruling 2 bounds what a kind asserts; it cannot establish that the
envelope set is complete, and ruling 8's remainder makes a miss visible rather than impossible.

**A row the harness does not flag carrying an envelope not yet declared.** `harness-meta` cannot see
it and the envelope set cannot name it. Ruling 8's gap is the only instrument that reaches it, and
only when the unrecognized wrapper carries a subagent result.

**An untagged Codex user message.** Nothing distinguishes a typed Codex turn from an untagged
injection, because there is no flag and no `user_message` event. Ruling 11 closes the structural half
and declares this one.

**ADR 0109 ruling 7's residue is untouched.** A subagent that erred and was never contradicted is
still invisible; none of this changes the signal.

**`locate_transcript`'s attribution asymmetry.** A Claude transcript must carry an `attributionSkill`
in `SCOPED_SKILLS`; a Codex rollout qualifies on being Codex-shaped alone. That is a selection defect
rather than a labeling one — inherited, not entangled — and it files rather than widening this
record.

## Rejected options

**Keying the relabel on the harness flag alone.** Reaches the 836 and the 2 and leaves all 827
notifications, therefore all 510 misattributed subagent results, exactly as they are — and demotes
the clinician's screenshots on the way past.

**The ticket's decision 3 as written.** *Print subagent launches against returned results* keyed on
the tool result prints 1,770 of 1,770, always. Measured before it was believed.

**Excluding a prior pass's verdicts.** Ruling 6.

**Enumerating the kinds in the skill.** Ruling 9.

**A tolerant reader, and a hard cutover.** Ruling 12.

**Splitting this into two records.** The format changes exist *because* of the vocabulary changes —
`TEXT-LINES` because ruling 6 puts a colliding body in the population, the header terminator because
rulings 7 and 9 add fields. Two records would each be missing the other's reason.

## Correction, 2026-09-12

**Found by the exhaustive tracker sweep of this record's own branch, hours after it merged.** Four
items, three of them defects in this record and one a build dependency it never named. They are kept
here rather than silently repaired, because the first two are this record's own subject arriving on
this record.

**1. The Codex row-type list published six types and the measurement found eight.** `token_usage_record`
142 and `world_state` 68 were dropped in transcription between the measurement and the write-up. The
sentence is corrected above and says so where it stands. **This is a partial read presented as
complete, in the record whose ruling 1 makes printing the remainder the condition of reading content
at all** — and it lands on ruling 11, which requires that same vocabulary *measured exhaustively*. A
reader taking the six as the population would have built against a closed set that was already wrong.

**2. The Codex populations were conflated and no selector was named.** 5,189 is every `*.jsonl` under
`~/.codex`; 1,942 is what names this repository; the 60-file sample was drawn from
`~/.codex/sessions/`, which holds **1,204**. Three numbers, one paragraph, and the stated denominator
was not the sampled one. Corrected above by naming each selector. The disclaimer that nothing
committed re-derives a harness figure does not cover this: without a selector the next reader cannot
tell a moved corpus from a different glob.

**3. The header-terminator repair was recorded only under *Rejected options*.** It is ruling 12's
now. A builder working the numbered list would have shipped `FORMAT:` and the generated legend — two
header additions against a header read at a flush `lines[:8]` — and left the defect that #1066's lead
is about, while both this record and that ticket read as though it were settled.

**4. Ruling 6 has a build dependency on [#1015](https://github.com/mshamblin5150-code/clinical-skills/issues/1015),
the one ticket this record never names.** Recovering the `prior-review` identifier means reading the
prior record, and `_last_watermarks` is what reads prior records: it globs `aar/*.md` sorted, skips
only `*.extract.md`, and assigns on each pass, so **the last file read wins**. #1015's defect 3 is
that a kept per-pass record therefore rewinds the watermark. **A ruling 6 build inherits that defect
unless the two are built together**, and nothing in the numbered rulings says so. Re-derived at
`595fbb88`; `grep -c prior-review tools/aar_scan.py` is 0, so nothing is built yet and the sequencing
is still free.

**What none of the four changes:** no ruling is reversed, and no figure outside the Codex paragraph
moved. Every Claude-format measurement was re-derived by a second reader at `595fbb88` and stands.

**5. The banner's `0` was a partial read presented as a corpus fact, and it was load-bearing.**
This record claimed the `[SYSTEM NOTIFICATION ...]` wrapper *"occurs 0 times in the 386
transcripts"* and reasoned from that zero that the wrapper is new. Re-measured over the same
directories, counting rows of **every** type rather than the one the original instrument read:

| | |
| --- | ---: |
| rows containing the banner | **469**, in 65 transcripts |
| by row type: `attachment` / `assistant` / `user` / `queue-operation` | 459 / 6 / **2** / 2 |
| earliest | **2026-09-05** |
| carrying a `task-id` / a `<result>` | 465 / 310 |

*Under the published claim that walk prints 0 rows and 0 files; it printed 469 and 65.* The zero was
true only of the population the instrument walked — `_human_text` over `type: "user"` rows — and the
sentence named a corpus. **That is [#961](https://github.com/mshamblin5150-code/clinical-skills/issues/961)'s
unstated-instrument species, published in a ratified record**, and it is this record's own ruling 1
failing inside the record that makes it: a matcher's remainder was not printed, so a partial read
read as a clean whole. The inference drawn from it — that the wrapper is new — is refuted by the
2026-09-05 first sighting. **Even the narrow claim is false by two**: the banner reaches `user` rows
twice.

**6. It supplies a measured candidate cause for the 1,076, which *What this does not reach* calls
unmeasured.** Those 469 rows carry `task-notification`, 465 carry a `task-id` and **310 carry a
`<result>`** — subagent results sitting on a row type `reduce_transcript` never branches on. The
string `attachment` appears in `tools/aar_scan.py` **0 times**. So an unknown share of the 1,076
launches with no notification in the population have one in the *transcript*, on an unread row type.
That does not retire the residue, and it moves it from *cause unknown* to *one measured candidate,
unquantified*.

**7. A builder seeding the envelope set from this record's own text would match 1 of 469.** The
banner is spelled here with an em dash; **the corpus writes a hyphen-minus in all but ten of the
occurrences near it**, and this record's copy is additionally hard-wrapped mid-phrase. Ruling 3 has
the builder declare an envelope set matched by containment — seeded from this prose it would match
almost nothing, and against a row type ruling 3 does not reach at all. **The envelope set is seeded
from the corpus, never from this record**, and `attachment` rows are inside ruling 11's exhaustive
row-type measurement rather than outside it.

**How 5, 6 and 7 were found:** the exhaustive tracker sweep of this record's own branch, by the
reader assigned #961 — a ticket about unstated instruments in published claims, and one this work
had no other reason to open. That is the sweep rule's own argument: a relevance filter selects on
what you already understand.
