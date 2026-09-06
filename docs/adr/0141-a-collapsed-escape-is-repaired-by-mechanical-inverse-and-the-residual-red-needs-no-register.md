# A collapsed escape is repaired by mechanical inverse and the residual red needs no register

[#802](https://github.com/mshamblin5150-code/clinical-skills/issues/802), whose fourth member was
handed to it by
[ADR 0136](0136-each-escape-collapse-shape-gets-its-own-refusing-row-and-a-record-may-fail-more-than-one.md)
ruling 6 so that one four-record repair would not be split across two tickets. Grilled 2026-09-06 at
`origin/main` `3ed25f8`, freshness gate `FRESH`. Every figure below was re-derived in process from
the four live comment records and from the committed tree; the tracker reads were taken through
`gh api` into a session scratchpad, so **nothing committed re-derives the tracker half** and each of
those is a dated floor. Counts, record identifiers and repaired token names only. The clinician
ruled every point below on that date. **Nothing is built here; this is the record the build reads.**

## What the grilling found that the ticket did not

**1. Three of the ticket's four decisions were already answered by records it predates.** Decision 2
by ADR 0136 ruling 6 — *"So no register and no ratchet"* — and decision 4 by ADR 0099 ruling 6,
which ordered #9's comment repaired and is why that population went four to three. Decision 3
dissolves under finding 4 below: the repair turns out to be mechanically checkable, so the worry
that a silent failed write would be undetectable on an invisible-character edit has an instrument.

**2. Decision 1's premise inverts on a finding nothing on the thread cites.** The 2026-09-02 sweep
read the residue as falling back to
[ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)
ruling 14's *nothing is repaired*. **ADR 0099 finding 10 rules that default does not reach this
class and that both of its reasons invert** — a collapsed escape *"was never a state anything was
posted in; it is not a claim but a rendering fault, so repairing it makes the comment agree with what
its author asserted"*, and the retained-revision reason bites only where the original holds something
that should never have been public, whereas here it holds corruption already served. The sweep's
reading was reasonable on the text it quoted and is superseded by a finding one section above it.

**3. The residue is not cosmetic, and what it corrupts is the class ADR 0099 ruling 6 repairs for.**
That ruling's test is *"exactly where the damage falsifies something a reader copies or a rule
grades"*, and it scoped its own repair by **construct** — the `**Branch state:**` block — rather than
by record, which is why line 1 of these four is clean and line 3 is not. Measured against the live
records, line 3 corrupts two label names from
[`docs/agents/triage-labels.md`](../agents/triage-labels.md), one catalog topic cell, and #662's own
committed null-span contract form quoted inside #519:

| record | published as | reads as | verifies against |
| --- | --- | --- | --- |
| #429 | `blocked` | backslash, `U+0008`, `locked` | `triage-labels.md:33` |
| #429, #662 | `ready-for-agent` | backslash, `U+000D`, `eady-for-agent` | `triage-labels.md:11` |
| #519 | `read YYYY-MM-DD; blind YYYY-MM-DD` | backslash, `U+000D`, `ead …` | #662's contract |
| #689 | `babesiosis` | backslash, `U+0008`, `abesiosis` | `guidelines-catalog.md:161,163` |

**GitHub does not sanitize it.** Fetched with `Accept: application/vnd.github.html+json`, the control
character is passed through into `body_html`, so the corrupted token is what a reader of the page
gets. This is the repository's recurring shape — *a documented shape the grader would refuse teaches
the next run to write one that fails* — sitting on the label vocabulary, a catalog key and a
committed contract at once.

**4. The repair is a mechanical inverse of a measured transformation, not a reconstruction of
intent.** Re-derived over all four records: **line 3 is the only damaged line**, every other line
byte-clean; line 3 carries **zero backticks**; and its backslash count is **even** in every case —
8, 14, 10 and 6 — with the backslashes alternating strictly between a span's first character and a
following space, colon or comma. So they pair as delimiters and no backslash on those lines was ever
intended. Where a span's first character formed an escape it collapsed, and which escape fired says
which letter it ate: `U+0008` was `b`, `U+000D` was `r`, and the two literal characters `^[` were
`e`. Line 1 carries **eight** backticks in all four, which re-derives ADR 0136 ruling 6's
*"eight backticks restored by its own line-1 repair"* exactly.

**5. Republishing these four is not blocked by their stale branch-state line, measured rather than
assumed.** `3199d606` **is** now an ancestor of `origin/main`, so line 1's *"is not on `main` as of
`2026-08-30`"* is a dated claim that has gone stale. It is never read: all four issues are closed,
none carries `in flight`, and `tracker_branch_scope` returns
**`record has no branch-state trigger`, exit 0** on every one — none of its three triggers fires.
The repair route is recognized: `("api",)` is in `tracker_publish_hook.PUBLISH_ROUTES` and a
`-F body=@<path>` argument is read, so the edit is graded before publication rather than after.

**6. ADR 0099 finding 5's account of the `\e` claim is right in its verdict and wrong in its
mechanism.** That finding calls the earlier sweep's escape claim false, and it is — but not because
no escape fired. #519 carries no `U+001B`; it carries the **two literal characters** `^[`, which is
why no control-character row can see that occurrence and why the eaten letter is still recoverable.
The verdict stands; the reason is corrected here.

## Ruling 1 — the four are repaired, and the default that would have left them does not reach them

ADR 0048 ruling 14's *nothing is repaired* is the standing default and ADR 0099 finding 10 already
ruled it inapplicable to this class, by name and in both of its reasons. Finding 3 above then meets
ADR 0099 ruling 6's own repair test on measured grounds rather than by analogy: the damage falsifies
a documented label vocabulary, a committed catalog cell and a quoted contract form, and GitHub serves
the corruption to a reader rather than swallowing it.

**The set is four and not three**, on ADR 0136 ruling 6, which handed #662 here precisely so that the
one record no shipped row can see would not be orphaned by the ticket boundary.

**Ruling 6's ordering precondition is already satisfied three times over** — *record first, repair
second* — because all four are cited by URL and date in ADR 0099 finding 1's table, in ADR 0136
ruling 6's table, and in #802's own body. Nothing is repaired ahead of the record that cites it.

## Ruling 2 — the repair is the full mechanical inverse of line 3, and the minimum is refused

Every backslash on line 3 becomes a backtick; every collapsed escape becomes the letter it ate.

**The minimum-that-clears-the-row is incoherent and that is why it is refused rather than merely
declined.** Deleting the `U+0008` from #429 leaves `locked` where the author wrote `blocked`, so even
the smallest honest repair already restores a letter. Given that, stopping short leaves the spans
whose only damage is backtick loss standing as backslashes — and that is a state **no route ever
produced**: neither what the author wrote nor what was published. A later reader could not tell a
half-repaired line from a differently damaged one.

**This repairs the fifth symptom in four records and does not grade the class.** Backtick loss
alone stays ungraded and stays ADR 0136's, which names it *"the fifth symptom of the same route"*.
Repairing it where the line is already being edited is not a decision to grade it anywhere.

**The acceptance test is derived rather than eyeballed.** After the edit each record must read: line
3 with **backslashes 0**, **backticks equal to that record's prior backslash count** — 8, 14, 10 and
6 — **no C0 character** and **no `^[`**; lines 1 and 2 byte-identical; every remaining original line
byte-identical; and exactly one line appended under ruling 4.

## Ruling 3 — #777 builds first and #802 is blocked on it, because #662 is graded by nothing today

#662 carries no control character at all — that is the whole reason ADR 0136 had to hand it here —
so no shipped row can see it. Repairing it before
[#777](https://github.com/mshamblin5150-code/clinical-skills/issues/777) lands publishes the one
record whose correctness turns on invisible characters with **nothing grading the publication**,
which is #802's own decision 3 arriving as an outcome rather than a worry. ADR 0136 ruling 5 puts all
three new rows on the pre-publish hook, so with #777 landed a repair that leaves a flanked carriage
return behind is refused at publication and the read-back stops being a discipline.

#802 takes `blocked` alongside its role label, which
[`docs/agents/triage-labels.md`](../agents/triage-labels.md) expressly permits, with a `blocked_by`
edge on #777.

**Nothing is falsified by the order and that was checked rather than assumed.** #777's brief carries
no live re-derivation as an acceptance criterion, and `tools/test_tracker_bodies.py` asserts no
tracker count anywhere, so no test moves. What moves is only ADR 0136 ruling 6's dated table, which
is a dated floor and stays true as written.

**One consequence is named here so a builder does not discover it as a surprise.** After the repair
**no record fails more than one row**, so ADR 0136 ruling 3's co-occurrence architecture has no live
instance left. It is unaffected as a ruling, and #777's tests must construct the co-occurrence
synthetically — which that module's no-live-fixtures rule requires of them in any case.

## Ruling 4 — a second dated correction line is appended and the first is not touched

Each record already carries `**Correction, 2026-09-01:**` describing the branch-state repair, and
that line is **true**: the earlier pass really was scoped to the block.

**The distinction that authorizes this repair is the one that forbids editing that line.** ADR 0099
finding 10 permits repairing a *rendering fault* because doing so makes the record agree with what
its author asserted, and leaves a *dated claim* standing because editing one makes the record
disagree with the state it was posted in. The 2026-09-01 line is a dated claim. Amending it to cover
both passes, or replacing it with a single history, would repair a claim — the act finding 10
declines to authorize — so the record gains a line and loses none.

The appended line names the line repaired, the transformation applied, and this record as the
authority, and **states that the earlier correction was correctly scoped**, so a reader arriving at
two correction lines does not read them as one repair done twice.

## Ruling 5 — the residual red needs no register, because the populations are closed at the publish boundary

With #777 landed and this repair made, the harvest sweep reports:

```text
#130 - lost-at-dash             8      #777 - carriage-return-flanked  0
#130 - empty-body               0      #777 - literal-newline-escape   5
#130 - literal-at-path          0      #777 - doubled-path-separator   2
#155 - double-encoded           9
#723 - c0-control-character     0      findings 24, distinct records 24
```

Still exit 1, so #802's complaint — *a reader cannot tell a new failure from a triaged one* —
survives the repair and is answered rather than repaired away.

**It is answered by construction rather than by bookkeeping.** `authorize_issue_body` raises on
**any** finding from `tracker_bodies.grade`, and the command path refuses a damaged title or body, so
no row's population can grow through the Claude Code publisher. A nonzero row is therefore historical
by definition, and `ROW_TICKET` already names whose it is in every report line. A register would
write those populations down a second time to automate a comparison for a command that gates
nothing, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) with a schedule. ADR 0136
ruling 6 reached the same answer for its own eight; this extends it to the whole report and states
the ground that makes it stronger than a ledger.

**ADR 0136's escalation condition is unchanged.** If the sweep ever becomes a gate, the register to
build is the validated kind — a listed record that stops firing fails, on `threshold_coverage`'s
inert-path discipline.

**Two things are declared alongside it, or the ruling overclaims.** *Closed by construction* holds
for **one publisher**: all four records repaired here were published from `codex/tickets-550-645`,
which the hook does not reach, and for any such publisher the workflow grades after publication with
the harvest sweep as the third net. That boundary is `tracker_publish_hook.NOT_REACHED`'s and is
[#916](https://github.com/mshamblin5150-code/clinical-skills/issues/916)'s subject on the cause side,
so it is declared rather than newly opened. And **two rows will ship carrying zero live instances** —
`c0-control-character` and `carriage-return-flanked` — which is `literal-at-path`'s precedent, cited
by name in ADR 0136 ruling 7: a documented trap with zero instances still earns a row, and a zero
there is not dead code.

## Ruling 6 — ADR 0099 finding 5's escape mechanism is corrected and its verdict stands

That finding's conclusion — the earlier sweep's `\e` claim is false — is correct and is not reopened.
Its mechanism is not: #519 carries no `U+001B`, it carries the two literal characters `^[`. The
correction is recorded here rather than by editing ADR 0099, on that record's own ruling 6 boundary,
and it matters to a builder because the token is recoverable and would be missed by anyone searching
for an escape character.

## What this does not reach

**Whether the four repaired bodies are otherwise correct.** This grades a rendering fault and
restores tokens verified against committed files. Whether each comment's *claims* were true when
posted is untouched, and under ruling 4's reasoning is not this record's to touch.

**Any record outside the four.** ADR 0136 ruling 6's eight standing pull request bodies are
untouched, ADR 0099 ruling 6 already weighed them, and the seventeen historical `lost-at-dash` and
`double-encoded` records are #130's and #155's.

**The route that caused the damage.** ADR 0136 ruling 7 refused auto-repair and an upstream report
and filed the cause-side check, which is #916. Nothing here reduces the chance of a next one.

**Retained pre-edit revisions.** GitHub serves an earlier revision of every edited record with no API
to delete one, so the damaged text stays readable to anyone who asks for it. ADR 0099 finding 10
already priced this: the original holds corruption that is already public, so the edit publishes
nothing that was not already served.

**Whether a fifth record exists.** The population of four is a dated floor taken from a harvest, not
a closed set derived from the tree. The build re-derives it before repairing.
