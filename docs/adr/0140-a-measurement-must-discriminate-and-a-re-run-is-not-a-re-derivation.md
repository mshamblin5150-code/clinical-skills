# A measurement must discriminate and a re-run is not a re-derivation

Ruled by the clinician on 2026-09-06, in the grilling of
[#795](https://github.com/mshamblin5150-code/clinical-skills/issues/795). Freshness gate `FRESH` at
both checkpoints. Nothing is built here; this is the record the build reads.

#795 was filed as a disagreement between
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
finding 1 and Anthropic's published hooks reference, at one fixed release. **The measurement taken
before ruling found that the disagreement never existed**, that the ADR was right on both counts,
and that the ticket's own premise was false on the day it was filed. What is left is the reason five
tracker sweeps could not establish any of that — and it is a defect in how a claim is settled rather
than in anything either record says.

## Measured before ruling, at `ab406eb`

**Every figure below is measured against a vendor binary and a third-party website, neither of which
is in this repository. Nothing committed re-derives one.** They are stated here and nowhere else, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms, and each carries
the instrument that produced it — which is ruling 2's discipline applied to this record's own
evidence.

**The installed releases, by `ls ~/.local/share/claude/versions/`.** Three are present: `2.1.238`,
`2.1.241` and `2.1.261`. `claude --version` reports `2.1.261 (Claude Code)`.

**The option space, by `grep -a` over the version files themselves.** Both `2.1.241` — the release
ADR 0083 names — and `2.1.261` carry, twice each, the zod enum `["allow","deny","ask","defer"]`, the
exhaustive-switch diagnostic `Valid types are: allow, deny, ask, defer`, and the JSON shape hint
`"allow" | "deny" | "ask" | "defer" (optional)`.

**And both carry, twice each, a hook-authoring prose block that lists three:**

```text
  - `additionalContext` - Text injected into model context
  - `permissionDecision` - "allow", "deny", or "ask" (PreToolUse only)
```

**So one shipped binary states its own option space two ways and they disagree.** The phrase ADR 0083
finding 1 quotes verbatim — *text injected into model context* — is the line directly above the
three-value list. Its author read the narrower source, quoted it, and counted from the wider one.

**The published reference, by `curl` on the markdown mirror** — the HTML route is a 2.8 MB Next.js
shell and `WebFetch` truncates before the table, which is a fact about those instruments and not
about the documentation. `https://docs.claude.com/en/docs/claude-code/hooks.md` returns 200,
`text/markdown`, 317,632 bytes, and reads *"four outcomes (allow, deny, ask, or defer)"* with
`deny > defer > ask > allow` precedence.

**The reference as it stood the day before the ticket, by `curl` on the Wayback capture**
`20260831233437id_` of `code.claude.com/docs/en/hooks`: 200, 309,098 bytes, `four outcomes` **2**,
`three outcomes` **0**, `\"ask\"` **12**, `\"defer\"` **10**. Every capture from 2026-08-20 to
2026-09-05 reads the same and a clean markdown capture of 2026-08-04 carries the identical sentence.
**The documentation said four continuously across the whole window.**

**What the tree emits, and it is narrower than either account.** `permissionDecision` is assigned at
one site in production code, `tools/tracker_publish_hook.py`, guarded so the emitted vocabulary is
`deny` plus omission. A quoted `ask` or `defer` appears nowhere in `tools/` or `.claude/`. The tree
never emits `allow` either.

### The ticket was wrong when filed, and the way it went wrong is the subject

#795 asserts the reference gives *"`allow`, `deny`, and `null` or omitted"*. The third item is real
and is not a value of the field: it is the no-decision path, written in the reference's own example
as `exit 0  # no decision; normal permission flow applies`. **A count of three is what reading the
example rather than the table produces** — a correct source, answering an adjacent question.

### Four sweeps confirmed the one half that was false, and they followed every rule that existed

Comments of 2026-09-04, 2026-09-05, 2026-09-06 12:45 and 2026-09-06 14:38 each record that
`claude --version` returns `2.1.261`, that the body's `2.1.241` premise is therefore false, and that
decision 1's instrument is **no longer runnable on this machine**. The measurement is true. The
verdict drawn from it is false: `2.1.241` was on disk throughout.

**`claude --version` reports which release is active. The claim it was used to settle was which
releases are present.** It prints `2.1.261` whether or not `2.1.241` is installed, so against that
claim it separates nothing.

**None of the four relayed.** Each ran the command itself and said so in the repository's approved
words — *re-derived by the parent, not relayed*. Each named its instrument, which is
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 6's requirement. **Two standing rules were obeyed and the false claim propagated anyway.**

**Repetition was counted and misread.** The third sweep wrote *"This is the third sweep to record
it"* and the fourth *"That is the fourth sweep to record it and the body still asserts it"*. The
rising count was read as evidence of neglect — four sweeps have said this and nobody has fixed the
body — when the same fact reads equally well as evidence of a shared instrument. Confidence rose
with the count, which is the inversion this record is about.

### The shape is already ratified twice, and the recurrence is the argument

**ADR 0074 ruling 6** was ruled on seven sweeps that *"published 5, 8, 11, 14 and 24 over one tree,
converged on one another, and were confidently wrong together."*
**[ADR 0077](0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md)**
records two sweeps that both verdicted `HOLDS`, where *"HOLDS meant the scanner still fires, never a
patient date is still exposed. **Those are different claims.**"* `CLAUDE.md` records the same shape a
third time on `tracker_bodies.py`, where every sweep ran `gh issue list`, which excludes pull
requests, and re-derived *six, not eight* — *"surviving longer than any other instance of it here
because each re-derivation agreed with the last."*

**Three prior instances, all in prose, and it happened again.** That is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail*, pointed at the paragraphs describing this exact failure.

### The verdict vocabulary those sweeps used is undocumented

`PARTLY STALE` has **zero** occurrences in `docs/` or `tools/`. `HOLDS` appears once, in ADR 0077, as
a report of what two past sweeps wrote. `docs/agents/issue-tracker.md` names one verdict word,
`untouched`. **The vocabulary carrying five verdicts on this ticket was invented by the sweeps using
it**, which is why ruling 4 has somewhere to put a distinction and nothing to displace.

### What was not re-derived

The runtime's dispatch switch, its multi-hook precedence loop and its SDK-boundary sanitizer were
read by a subagent and are reported here as its claims. The enum counts, the three-value prose block,
the live reference, the archived captures and the emitted vocabulary were each re-derived by the
parent. **The rulings below rest only on the re-derived half.**

## Ruled 2026-09-06

### 1. The disagreement does not exist and ADR 0083's five rulings are untouched

Finding 1 is correct at the release it names, at the release installed now, and against the
documentation as published on the day #795 was filed. **Nothing in ADR 0083 is reopened.** Its
rulings rest on `additionalContext` being text the model reads and on plain stdout not reaching it;
both accounts confirm both, in different words, and the tree consumes neither disputed value.

### 2. A measurement settles a claim only if it discriminates

**Before a figure is allowed to settle a claim, say what the instrument would have printed if the
claim were false.** Where the answer is *the same thing*, the instrument settles nothing, however
correctly it ran and however carefully it was re-derived.

`claude --version` prints `2.1.261` whether or not `2.1.241` is installed. `gh issue list` prints six
whether or not there are eight. A live instrument aimed at the wrong claim is what four competent
sweeps had, and neither running it again nor naming it repairs that.

**This is not the liveness case, and the difference is the whole of what was missing.** Liveness is a
property of the **instrument** — can it produce a different answer at all? `claude --version` is
perfectly live; it changed when the release moved. Discrimination is a property of the **pairing** of
instrument and claim. `CLAUDE.md`'s extractor-coverage rule already requires the population, the
extraction and the liveness case; discrimination is the fourth thing and no rule here had it.

### 3. Agreement between sweeps that ran one instrument is not corroboration

Four verdicts drawn from one command are one measurement repeated. **A rising count of sweeps
recording a claim is not evidence for it**, and reading it as evidence of neglect — which is the
reading the record invites and which #436's ruling makes feel authoritative — accelerates the error
rather than catching it.

**The neglect reading is rejected explicitly, not merely not chosen.** It is a true observation about
a false claim. Acting on it here would have produced a fifth comment asserting the same wrong thing
more loudly.

### 4. `re-derived` and `re-run` are separate words and a sweep says which

**`re-derived` means a fresh instrument. `re-run` means the same command again.** A sweep repeating a
prior verdict names which it did, and a `re-run` carries no weight beyond the comment it repeats.

The four sweeps here told the truth when they said *re-derived by the parent, not relayed* — the
repository's vocabulary had no way for them to say that they had independently **run** an instrument
without independently **deriving** anything. It has one now.

### 5. The rule is measurement-scoped, and the sweep is where it gets a trigger

Ruling 2 is not a fact about tracker sweeps. `CLAUDE.md` already records six instances outside the
tracker — `gh issue list` and pull requests, a scan for `U+00B3` blind to the same operator in the
private use area, a fourteen-document sample that named the one tuning constant that loses to the
library it replaced, an `N=3` bound measured against already-stripped text rather than the PDFs, a
case-sensitive `NUMERAL` that ungraded every sentence-initial figure, and a `git check-ignore` query
that answered *ignored* to everything.

**Drawing the wider rule from six instances the repository had already written down, across six
unrelated subsystems, is not the generalization
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) forbids** — that trap is
generalizing from the files one session happened to open.

**It is a disqualifier and never a checklist item.** It is one question asked of a command before its
output is allowed to settle a claim, not a line required under every figure.

### 6. The trigger is a figure settling a claim somebody else wrote down

Not every published figure, which is the noise this repository has already ruled against; and not
negative verdicts only, which undercovers — of the six instances, the `N=3` bound was a positive
claim and `git check-ignore` was a false positive, and both would escape.

**The condition is that the measurement is being used to overturn or confirm an existing written
claim** — a ticket body, an ADR finding, a docstring, a prior verdict. It is the sweep's whole job,
it is what all six instances were doing, and an author can check it without introspection.

The written form is one clause, not a paragraph:

```text
`claude --version` -> `2.1.261`. Under the claim's negation this prints the same thing, so it
does not settle "2.1.241 is absent"; `ls ~/.local/share/claude/versions/` does.
```

**A figure merely reported for context is outside the rule**, deliberately. That is a real hole — the
fourteen-document sample was context before it became a tuning table — and a rule that fires on the
sweep's verdicts and is obeyed is worth more than one that fires on every number and is skimmed.

### 7. The rule's home is `CLAUDE.md` beside the three-piece rule it completes

Ruling 2 lands in `CLAUDE.md`'s extractor-coverage section, which already carries the population, the
extraction and the liveness case. `docs/agents/issue-tracker.md` **points at it** and carries only
what is sweep-specific: ruling 4's vocabulary and ruling 6's trigger. This record points and does not
restate.

**Two prose copies each editable without failing anything is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)**, whose recorded lesson is
that the reader misled is whichever one checked the file nearer to hand. **A test binds the pointer**,
on the arrangement `reference_scan.py` and `docx_write.NOT_APPLIED` already use. Without that test
this is two copies with nothing between them, which is the defect rather than the fix.

### 8. A form check rides in the publish hook, advisory first

A tracker comment carrying a `**Verdict:**` line must also carry ruling 6's clause.
`tools/tracker_publish_hook.py` grades it, which is the class of thing `tracker_branch_scope` already
does with the `**Branch state:**` block.

**[ADR 0072](0072-blocked-is-one-kind-agnostic-gate-label-on-an-axis-orthogonal-to-the-roles-and-the-sweep-holds-its-invariant.md)
ruling 3 does not reach this, and the reason is its own.** That ruling refused a scanner for the
`blocked` invariant because *"the tools open no sockets, so a grader would need a new documented
harvest step feeding a new tool."* A form check on the text being published needs neither: the hook
already holds the body, offline, at `PreToolUse`. **The cost argument that carried ADR 0072 ruling 3
is absent here, so its conclusion does not transfer**, and *declare the coverage, do not widen the
instrument* is satisfied — this widens no instrument, it requires one to be described.

**Advisory, not refusing, until there is a measurement.** A refused publication mid-sweep costs a
whole exhaustive read, and this rule has no measured false-positive rate. It takes `spelling_scan`'s
posture and is promoted on evidence rather than on confidence.

**What it buys is the shape and never the reading.** A sweep can satisfy it with a stock sentence,
which is `specificity_scan.py`'s R2 limit that every substance test here inherits and
`checks_ledger.SUBSTANTIATED_CLEAN`'s ruled position. What changes is that a verdict stops being
unfalsifiable by eye. **Nothing more is claimed for it.**

### 9. ADR 0083 finding 1 is corrected in place to name its instrument

[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
governs: facts are corrected in place with a dated line at the bottom, and the deciding paragraph
stays untouchable. Finding 1 is a finding.

**The edit names the two sources and which was taken**: four from the runtime schema in the `2.1.241`
binary, the quoted description from that same binary's hook-authoring prose block, **which lists
three**. So the record says on its face that the vendor disagrees with itself and which side finding
1 took.

**A dated bottom line alone is refused.** ADR 0016 rejects annotation-only correction in as many
words — *a reader opens the file, reads the figure, copies it, and never scrolls to the footnote* —
and #436 rules the same. Recording this correction below the sentence it corrects would be #795's own
defect committed inside its repair.

**#795's second *Done when* is the one clause of the ticket that survives intact**, and it stated
this rule before the rule existed: *the correction says which instrument produced it, because the
current text says "In Claude Code 2.1.241" and a reader cannot tell whether that was read or run.*

### 10. #795 is converted in place rather than closed

Its original subject **dissolved** rather than being completed, so nothing is left to close; and its
own comments are the entire evidence base for this record. It is retitled to the sweep subject,
relabelled `grilling` to `ready-for-agent`, and its body rewritten. ADR 0016 is the nearest
precedent: *the filename is an index rather than the ruling* — a title is an index too.

**The rewritten body must do two things or the conversion is dishonest.** It says at the top what the
ticket was filed as, that it was measured false on 2026-09-06, and with which instruments — so nobody
re-derives the dead premise from the comments. And it says the comments below are verdicts on the
**retired** subject, retained because four of them are the evidence for the current one.

**The four sweeps are named as an instrument failure and no session is faulted.** Every one followed
the rules that existed, named its instrument, and re-derived rather than relayed. That is the point:
the rules were obeyed and were not enough.

## What this record does not settle

**Whether the vendor's binary and its published reference will continue to agree.** Both say four
today; the binary's own prose block says three and has since at least `2.1.241`. Nothing here
watches that, and no mechanism in this repository can.

**Whether a sweep's discriminator clause is true.** Ruling 8 grades that a clause is present, on the
same terms as every substance test here. A stock sentence satisfies it.

**Whether ruling 2 should ever refuse rather than warn.** Ruling 8 fixes the posture as advisory and
names a measurement as what would move it; it does not predict the answer.

**Whether the six non-tracker instances in ruling 5 need repairs of their own.** They are cited as
evidence that the shape is not sweep-specific. Each was ruled where it was found, and reopening them
is outside this record.

**Anything about ADR 0083's five rulings.** Ruling 1 confirms their shared premise and touches
nothing else, which is #795's own *What must not come out of this* honored.
