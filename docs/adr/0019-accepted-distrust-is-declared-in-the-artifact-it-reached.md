# Accepted distrust is declared in the artifact it reached

[#460](https://github.com/mshamblin5150-code/clinical-skills/issues/460) was split from
[#406](https://github.com/mshamblin5150-code/clinical-skills/issues/406)'s reopen comment,
which found one piece of that ticket's decision 2 unanswered: what a command owes a
committed artifact when its only output is a human. [ADR 0010](0010-an-untrusted-read-may-not-publish-into-the-checkout.md)
answered it for the two cases that have a machine-written artifact — `guidelines_index`
writes `untrusted_reasons` into the index, and `uspstf_table` may no longer publish inside
a checkout at all. Neither reaches a person reading a console and committing a file.

Grilled 2026-08-23. **Five decisions, ruled by the clinician on that date.**

## The ticket's own scenario is not the load-bearing one

#460 is framed on `guidelines_search --allow-untrusted-provenance` → a value read off an
untrusted index → hand-copied into a threshold sheet. Measured, that path is mostly closed
and the ticket does not know it. `threshold_sheet`'s flag reaches exactly one gate —
WATERMARK, through `read_extraction`. The row's number is anchored by three gates that
never touch the index: tier 0 against the recommendation record built straight off the
PDF, tier 1 against the row's own snippet, tier 2 against the cited page. The untrusted
search located a page; it did not supply a fact. Its residue is narrow and real — on a
machine with no PDFs and a bound source, tier 1 is the only live gate, and the snippet it
checks against could have come from the same untrusted read.

**The uncovered case the ticket does not name is a verdict rather than a value.** Run
`threshold_sheet <sheet> --allow-untrusted-provenance` and WATERMARK genuinely *passes*
against a dirty, foreign or unstamped extraction. Drop the flag and `guidelines_manifest.read`
turns that into a problem and the gate skips loudly instead. So the commit machine's hook
run — `--all --quiet`, no flag — reports WATERMARK as skipped, which is what every
corpus-free clone reports. What crossed into the committed sheet is not a copied number.
It is a gate verdict nothing downstream can re-derive or contradict.

Both halves are ruled here as one question, because they are one: what a human-mediated
derivation from an untrusted read owes the artifact it lands in.

## The ruling

**1. The artifact retains it, narrowly — for the gate actually graded under distrust.**
Not because a record beats a guard; this repo's posture is the reverse and ADR 0010 is
right about it. Because on this path **there is no guard to be had**. ADR 0010 rejected
stamping the USPSTF table on the ground that it *"records the problem where the refusal
prevents it"*, and here nothing prevents it: the crossing is a person committing a file.
The ground that rejected a record does not hold.

`artifact_provenance.NOT_GUARDED`'s first row already declares the neighboring shape, and
this is not that row restated. A hand-copied file is the same bytes the guard saw. A
WATERMARK pass is an assertion that a gate was satisfied, and the hook's own re-grade
cannot contradict it — it returns *skipped*, not *disagrees*.

**2. Threshold sheets and the guideline catalog.** The catalog is the stronger instance
rather than a courtesy extension: `guidelines_catalog --allow-untrusted-provenance` audits
`page_count`, `class` and `year` against the corpus and blesses a *committed* file, and its
`--draft` prints rows to stdout that a person pastes into that same file. ADR 0010's
sentence that `guidelines_catalog` *"produces no durable artifact"* is true of the command
and misses the paste; that sentence is not withdrawn, because the rule it supports is about
a write, and this record covers what that rule deliberately does not.

`reference/thresholds/coverage.md` is **out**: it reads the committed catalog through
`parse_catalog`, never a corpus, and carries no flag. A mark there would be a fact about
another file written into a second one, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143), and it would go
stale the day the catalog is re-audited. `guidelines_search` is in the question and cannot
be in the record: it owns no artifact, so #406's unsuppressible stderr line is the whole of
what it can leave.

Symmetry between the sheet and the catalog was tested rather than assumed, on
`block_scan.py`'s recorded lesson that the safe direction of a rule is a property of the
rule and not of the pair it belongs to. The failure direction is the same in both — a
committed artifact holding a verified-looking verdict earned against an untrusted corpus —
so the arrangement mirrors. The catalog's independent audit ledger is a real asymmetry and
does not reach this: that ledger covers what a human read off a PDF, and the mark covers
what a machine verified against an extraction.

**`--draft` takes no mark of its own.** A pasted row is a value with no verdict attached,
and the next audit run grades it — covered by the mark under the flag, confirmed outright
under a trusted run. A second mark would record one event twice.

**3. The declaration is what holds the pass.** Under the flag, the gate does not report a
pass unless the artifact declares the mark; without it the gate reports the not-graded
state it already reports when the flag is absent, and for the catalog the `check_shape`
mode that already exists.

This is the half that could most easily have gone wrong. The precedent the mark copies —
`citations resolved against <corpus> on <date>` in a sheet's `## Scope` — is hand-written
and touches no exit status, and `reference/thresholds/README.md` records what that costs
in a neighboring clause: it was *"the one part of the format a sheet could drop for free,
and dropping it scored cleaner."* A mark on those terms would make the honest artifact
score worse than the silent one, in a file about clinical numbers. Holding the pass inverts
the incentive: omit the mark and you have not claimed a pass, you have a skip — which is
the truthful state of a gate satisfied only against a corpus nobody trusts.

**4. Corpus, date, and the reasons verbatim — and a flagged run refuses a mark that
describes a different distrust.** The reasons `artifact_provenance` computes are not one
event: *was produced by a dirty checkout* is a person mid-rebuild on their own machine, and
*has no producer provenance stamp* is an artifact nobody can account for. A later reader of
the artifact has no other way to tell them apart, and they are the whole difference in what
the mark should cost them. They are free to author, because the run that requires the mark
is the run that just printed them. The comparison is free too: decision 3 already forces the
grader to parse the mark, so checking that it describes *this* distrust is the same read.
Without it a mark copied from a neighboring sheet satisfies the rule while describing an
event that never happened to that file — #460's own complaint rebuilt inside its fix.

**5. A run in which the gate genuinely passes against a trusted corpus refuses while the
mark stands**, naming the deletion. The mark is a *status*, not an event log — its precedent
names the last resolution, singular — so a status that has stopped being true has to go, or
a rebuild can never lift it and the declaration decision 3 made mandatory becomes a
permanent smear. The clearing event is a trusted passing run and nothing else: not elapsed
time, and not a rebuild nobody graded against. This is decision 3's mirror and inherits its
argument — you cannot hold the pass without declaring, and you cannot keep the declaration
once a trusted run has superseded it.

## What is declared rather than built

**The commit machine cannot know a flagged run happened.** The pre-commit hook runs
`--all --quiet` with no flag, so nothing stops an operator ignoring the console and
committing. What decision 3 guarantees is narrower and is the whole of what is claimed:
**there is no way to hold a pass earned under distrust without saying so in the file.**

Where the corpus is absent — a fresh clone, a worktree, CI — the gate skips, there is no
trusted pass, nothing is superseded and nothing refuses. Decision 5 bites on exactly one
person: the operator who rebuilt clean and left the line behind.

## Rejected alternatives

**Declare only — a fourth `NOT_GUARDED` row, and close.** The standing answer where
widening an instrument would require a guess, and it is the wrong instrument here: this
needs no guess, and it would leave a committed clinical artifact carrying a pass nothing
can re-derive.

**Refuse to grade under the flag**, in its strongest form by dropping the flag from
`threshold_sheet` entirely. Tidiest and wrong. That command's own help reads *"grade against
a dirty, foreign, or unstamped extracted corpus"* — producing a verdict under distrust is
the documented purpose of the flag there, not a side effect — so this deletes the one
capability it exists for to close a hole a line of text closes.

**The grader writes the line itself.** Makes a grader mutate a committed curated artifact,
which is the opposite of this directory's posture everywhere else — `guidelines_catalog`
audits a curated file and never writes it — and it would need a write guard of its own.

**Retain the mark permanently.** There is a real reading where *this artifact was once
graded under distrust* is worth keeping forever. Rejected because a WATERMARK pass is not a
claim about the numbers — it is a claim that no stripped string interleaved the rows — and a
trusted re-probe of the same rows genuinely supersedes it. Retaining it would record a fact
the gate never asserted.

**A predicate over which commands qualify.** Refused as the guess
[#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176) rejected and ADR
0010 already declined: nothing mechanical can decide which command's durable output is a
human decision. The enumeration stays hand-kept and declared, the way ADR 0010's is.

**Widening `Publish`.** That term is defined tightly *because* a guard acts on it —
`refuse_publication` intercepts a write. Stretching it to cover a human paste would make the
guard's own definition describe something the guard cannot see. `CONTEXT.md` carries
**Accepted distrust** as the term for what this record rules on, and it is deliberately the
thing `Publish` does not reach.

## Filed rather than folded in

The sheet's existing `citations resolved against <corpus> on <date>` has exactly the defect
decision 3 turns on: unenforced, droppable for free, and dropping it still scores cleaner.
After this record a sheet carries two status lines of one shape obeying two rules. It is
**not** repaired here, because tier 2's coverage is a different gate's question and nobody
has ruled it — folding it in would rest this record on a ruling that does not exist. And the
cost is measurable rather than theoretical: every committed sheet carries the line today, so
enforcing it retroactively passes everywhere, which is the condition under which nobody
notices what the rule costs the next one.
