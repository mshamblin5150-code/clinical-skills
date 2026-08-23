# A declared verdict is held by the machine that can re-derive it

[#473](https://github.com/mshamblin5150-code/clinical-skills/issues/473) is the spillover
[ADR 0019](0019-accepted-distrust-is-declared-in-the-artifact-it-reached.md) named under
*Filed rather than folded in*: the threshold sheet's `citations resolved against <corpus> on
<date>` line has the defect that record's decision 3 turns on — unenforced, droppable for
free, and dropping it scores cleaner — and it was not repaired there because tier 2's
coverage is a different gate's question nobody had ruled.

Grilled 2026-08-23. **Six decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## The ticket's framing assumes the two lines are one shape, and they are not

#473 is written as *two declarations of identical shape obeying two different rules*, and
asks whether they should obey one. Measured first, that premise does not hold, and every
decision below turns on why.

#460's mark holds WATERMARK's pass because **no later run can produce that pass**. Drop the
flag and every corpus-free clone reports `skipped`, forever. The declaration is the only
carrier there will ever be.

Tier 2 is not that. `gate_citation_tier2` opens the cited PDFs live on every run. Where the
corpus is present the verdict is **re-derived, not inherited**; where it is absent,
`_citation_tier2_not_run` prints a banner saying in capitals that the sheet has **not** been
checked against source PDFs on this machine. So the line is not the sole evidence of a
verdict. It is a historical claim about another machine, printed a few rows beneath a live
gate answering the same question for itself.

That reframes the danger the ticket correctly identifies. **A stale line is harmless exactly
where it is detectable and undetectable exactly where it matters** — where the corpus is
present the live gate supersedes it, and where the corpus is absent there is nothing on the
machine to compare it to. The lever is not on the reader's machine. It is on the machine
that has the corpus, which is the only one that can ever know.

## The ruling

**1. The line is held in tier 2's *skip*, not its pass.** Where tier 2 produced no verdict,
the line is the only thing standing between *checked once against a real corpus* and *never
page-checked by anybody*, and a corpus-free clone today reports those two identically. Where
tier 2 ran, the line is ignored — gating a live verdict on a hand-written claim about a
different day is backwards, and was rejected as such.

**2. A run that produced a tier 2 verdict refuses a line that disagrees with it.** The run
resolved against a known `--pdf-root`; a line naming a different corpus describes a
resolution that is not the one that happened. That refuses, and so does a date in the
future. **The date is otherwise not checked**, and that is a ruling rather than an omission:
requiring it to be current would refuse a prose typo fix for having failed to re-date the
sheet, on a hook that runs `--all --quiet` over every sheet on every commit touching one,
which is how a check gets learned around.

**3. Presence is required in both states.** The line exists **for the corpus-free reader,
and the corpus-carrying author is the only person who can write it truthfully**, so the
obligation sits on the machine that can discharge it. This is not decision 1 reversed: the
verdict never depends on the line's *content*, only its presence, and decision 2 already
holds the content. Without this, a sheet committed with no line at all passes the pre-commit
hook in silence and is caught only by CI, which ADR 0002 makes advisory.

The finding attaches to **CITATION tier 2** and exits **1**, never 2. The tool scanned
fine; the artifact is deficient, and this repo's ordering already puts a violation above a
did-not-scan. SCHEMA is the wrong home because it cannot know whether tier 2 ran.

**4. The corpus token stays a path, and the ping-pong is declared.** `--pdf-root` defaults
to a machine-local absolute path and every committed sheet records that literal, so decision
2 passes forever on the maintainer's machine and **churns on a second one**: a green run
there legitimately refuses, its owner edits the line, and the first machine's next run
refuses for the mirror reason. Ruled a declared limit rather than designed around. It fires
loudly and costs one edit, never a silent wrong answer, and building a machine-independent
corpus identity now would be inventing a mechanism for a machine nobody has — the ground
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97) refuses a cut point
the corpus cannot supply.

**5. The principle is named, and membership stays hand-kept.** `CONTEXT.md` gains **Held
declaration**. This is ADR 0019's decision 3 applied one level down: it refused a mechanical
walk over which *commands* qualify on
[#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176)'s terms, and the
same refusal holds for which *lines* do. The term's final clause forbids the date-arithmetic
version of this rule, which is where decisions 2 and 4 both nearly went and which no machine
can ground.

**6. The build does not block on #460.** The two touch different gates and different lines.
The term is the relationship — #460's mark is an instance of **Held declaration** and its
builder reads the term rather than this branch's prose. Writing forward-looking prose about
a mark not yet in the tree was refused as the shape this repo records going stale.

## The relationship to #460's mark, explicit

The two lines do **not** obey one mechanism, and saying they do would be false: one holds a
pass, the other holds a skip and a presence requirement. They obey one principle, and it now
has a name.

The stronger statement, and the one `## Scope` carries: **after this record, every line in
that section is held by something.** `Read:` and `Not read:` are already refused when
missing, the resolution line is held in both states, and #460's mark holds WATERMARK's pass.
Nothing in `## Scope` is droppable for free any more, which is what ADR 0019's decision 3
was really about.

## The finding that shaped the build

Before this build, the committed sheets already carried the line, so enforcing it
retroactively **passed everywhere on the first run** — the condition under which nobody
would notice what the rule costs the next sheet. The ticket names the remedy: drive the rule
red with a sheet built to fail it.

The sheet built to fail it was **already in the tree, and it was the grader's own shared
fixture**. Its synthetic `## Scope` declared `citations resolved against C:/nowhere on
2026-08-16`. `_RESOLVED` accepted that corpus token, and the footer printed it as a
resolution **against a path that had never existed on any machine**. The tests treated
`last resolved` only as an ordering landmark, so none held the declaration's content. The
format's own fixture was therefore the worked example of the defect this ticket was filed
over and the red driver for decision 2.

## What is declared rather than built

**The date is not checked past the future bound**, by decision 2. A sheet resolved in
August against a corpus that has since gained a revision of the same guideline is caught by
a live tier 2 run — the page moved, the snippet is not on it — and by nothing at all on a
corpus-free clone. That is not closed here and is not closable there.

**Decision 4's ping-pong is live the day a second machine exists.** It is written into
`## Scope`'s prose so its owner reads it before hitting it, and it is a re-ruling trigger
rather than a bug report.

**Nothing reaches a sheet whose line is a fiction and whose corpus is absent.** Decision 3
requires the line be present; only decision 2 checks it says anything true, and decision 2
needs the corpus. A reader on a corpus-free clone learns that somebody claimed a resolution,
never that one happened.

## Rejected alternatives

**Hold tier 2's pass, mirroring #460 exactly.** Backwards. When tier 2 has just run, the
line is redundant — the gate did the work in front of you — so this gates a live verdict on
a stale hand-written claim.

**Bind the line to the committed corpus digests.** `reference/guidelines-catalog-audit.md`
holds a per-PDF SHA-256 in the checkout and is recomputable from `--pdf-root`, so a
corpus-free clone could check the claim rather than merely observe it. Rejected on ADR
0019's own decision 3: `coverage.md` was ruled out of that mark because *"a mark there is a
fact about another file, #143"*, and a sheet carrying a digest of the audit ledger is that
shape exactly. It buys reach at the cost of the rule #460 had just made.

**A machine-independent corpus identity in place of the path.** Closes the fiction properly
and never ping-pongs, and costs a format rewrite of every sheet plus hashing the whole PDF
corpus on the hook path, for a second clinician who does not exist. Decision 4 instead.

**A predicate over which lines qualify as held.** Refused twice over — as the guess #176
rejected, and as the walk ADR 0019 already declined one level up.

**Requiring the date be current on a green run.** Refuses correct work: a prose fix to a
sheet would fail for not re-dating a resolution that did not change. The failure direction
is the one [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) has
produced repeatedly — a rule cutting a correct artifact for a property it does not care
about.

**A grader that rewrites the line itself.** ADR 0019 rejected the same move for its mark:
it makes a grader mutate a committed curated artifact, which is the opposite of this
directory's posture, and it would need a write guard of its own.

Correction, 2026-08-23: decision 4's second-machine ping-pong is narrower than the
paragraph above states, and the narrowing was found by the tracker sweep this record's
own merge triggered. `tools/hooks/pre-commit` invokes `threshold_sheet.py --all --quiet`
with no `--pdf-root`, and unlike `--recs-root` and `--text-root` that flag has **no
environment-variable override** — so on a second machine the hook resolves the absent
maintainer path, tier 2 skips, and decision 2 never fires there at all. The ping-pong
requires somebody running an explicit `--pdf-root`, which is a deliberate act rather than
the ordinary commit path. That makes the declared limit smaller than it reads, not larger,
so the ruling itself is unchanged — but a second machine's owner meets it at a command
they typed rather than at a hook they did not.
