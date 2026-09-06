# Each escape-collapse shape gets its own refusing row and a record may fail more than one

[#777](https://github.com/mshamblin5150-code/clinical-skills/issues/777), split from
[#723](https://github.com/mshamblin5150-code/clinical-skills/issues/723) by
[ADR 0099](0099-a-control-character-in-a-published-tracker-body-is-refused-at-the-publish-event-and-graded-at-every-one.md)
ruling 1, which scoped that ticket to the one symptom a check could recognize without firing on
correct text and sent the rest here. Grilled 2026-09-06 at `origin/main` `e36502d`, freshness gate
`FRESH`. Every figure below was re-derived in process from a fresh harvest of every issue, pull
request and issue comment taken that day into `scratch/`, and the instruments are throwaway scripts
under `scratch/` — so **nothing committed re-derives them** and each is a dated floor. Counts and
record identifiers only; no body text is quoted. The clinician ruled every point below on that date.
**Nothing is built here; this is the record the build reads.**

## The measurement falsified the ticket's premise before the first decision

The ticket's decisions 2 and 3 ask whether a rule is *possible* for the literal-newline and
doubled-separator shapes. It is, for all three ungraded shapes, at **zero false alarms** over 4,467
text-bearing bodies:

| shape | ticket | re-derived 2026-09-06 | false alarms |
| --- | ---: | ---: | ---: |
| 1 · a C0 control character | 4 | **3** | graded by #723 |
| 2 · a carriage return flanked by non-space | 3 | **3** | **0** |
| 3 · a literal newline escape on the page | 5 | **5** | **0** |
| 4 · a doubled path separator | 2 | **2** | **0** |

The harvest holds 5,382 records, of which 915 are titles and 4,467 are bodies.

**Shape 1 is three, not four, and the fourth was repaired rather than missed.** #9's comment carried
the only `U+0008` outside the 2026-08-30 batch and ADR 0099 ruling 6 repaired it. The row's live
population is exactly the three comments
[#802](https://github.com/mshamblin5150-code/clinical-skills/issues/802) covers.

**The cosmetic lone-carriage-return population is 19, not 17.** Twenty-two bodies carry a carriage
return not followed by a line feed; three of those are the damaged ones. ADR 0099 correction 4's
figure has drifted on a growing tracker, which is what a dated floor does.

### Shape 3 has two independent discriminators and they do not disagree

Each returns the same five records alone, and the answer does not move anywhere in between:

```text
no exclusion at all   : 48   (with the zero-real-line-break clause: 5)
inline spans only     :  5   (with the zero-real-line-break clause: 5)
fenced blocks only    : 37   (with the zero-real-line-break clause: 5)
both                  :  5   (with the zero-real-line-break clause: 5)
```

**The five firing bodies carry zero backticks**, so the code exclusion is *inert* on them: the rule
stands on the shape rather than on the parser. That is two orthogonal instruments agreeing over a
flat interval, which is `SPACE_ADVANCE_FRACTION`'s discipline — take the plateau, never a value at an
edge — arriving on a tracker body instead of on a page.

### The mention-versus-use trap two sweeps flagged does not fire

Comments on this ticket recorded that any gate for these shapes would fire on the ticket describing
them. **Naively yes; under either discriminator no.** #777's own body and three of its own sweep
comments sit among the 43 records the code exclusion removes, because they write the shape inside
backticks — and the zero-real-line-break clause excludes them a second way, since a body *about* the
damage has line breaks and a body *carrying* it has none.

So [ADR 0104](0104-the-freshness-gate-s-subject-is-the-commit-base-and-a-publication-s-cited-records-are-read-back-without-a-baseline.md)
ruling 4's *the mention rule belongs to a checker that refuses, and this one only reports* is not the
escape hatch here. It offers a reporting checker the right to skip an exclusion; the exclusion cost
nothing, so the offer buys nothing.

### Shape 4 cannot fire on a correct Windows path, and every spelling agrees

```text
C: + doubled separator                    : 2
any drive letter + doubled separator      : 2
any doubled backslash                     : 2
doubled separator between word characters : 2
```

The two records are the recorded pair. ADR 0099 finding 3's two correct Windows paths, pull/368 and
pull/631, are invisible to all four spellings because a correct path carries a *single* separator —
so the ticket's *what must not come out of this* constraint is met structurally rather than by
tuning.

### First-match-wins would understate a new row by two thirds

`grade` is an `if`/`elif` chain appending at most one `Finding` per record in `KINDS` order. Two of
the four damaged comments carry two shapes at once:

```text
c0,cr   #429 comment 5471066342
c0,cr   #519 comment 5471067862
c0      #689 comment 5471077562
cr      #662 comment 5471101892
```

A carriage-return row appended after #723's shipped row reports **1** where its population is **3**.
Placed before it, #723's row drops to 1 instead. **Merging the three shapes into one row does not
dodge it** — a merged row's population is ten records and it would report eight for the same reason.

The rule is sound today and its reason is written down: `@-` is *also* a lone `@` token, so
`literal-at-path` is suppressed to keep #130's eight instances from double-counting. Run over the
fresh harvest, that nesting is the **only** overlap among the shipped rows:

```text
lost-at-dash             reported=8   independent=8
empty-body               reported=0   independent=0
literal-at-path          reported=0   independent=8   <- suppressed, correctly
double-encoded           reported=9   independent=9
c0-control-character     reported=3   independent=3
```

So the rule handles a **nesting** — one defect satisfying two spellings — and would silently
mishandle a **co-occurrence** — two distinct damages in one body, both true, both needing separate
repair.

### The predicate ADR 0099 finding 3 refused reaches none of the four damaged comments

Over bodies alone that predicate — *no backticks and at least one backslash* — selects **10**: two
correct Windows paths, seven the rows below now grade, and one residue. It fires on **none** of the
four comments this class is about, because each carries eight backticks alongside its six to fourteen
backslashes. Finding 3 priced and refused a rule that was never going to reach them.

### An instrument defect, recorded because it is the shape this repository keeps finding

The first pass handed **titles** to `tracker_bodies.Record` as bodies. `records_from_github` reads
`item.get("body")` and nothing else, so the module never sees a title. **No row figure moved** when
it was corrected — the contamination reached only the residue list, where one hit proved to be an
issue *title* whose body is correct prose full of backticked regex. A measurement taken against the
wrong population reads exactly like one taken against the right one, which is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) arriving on the instrument
built to settle #137's own shape.

## Ruling 1 — all three ungraded shapes get a row, because each predicate is safe for a structural reason

The ticket asks whether a rule is possible and the answer is measured. What decided it is not the
zero itself — a zero is a dated floor — but that each zero has a **structural** cause rather than a
lucky one: a damaged body has no real line break, a doubled separator is not a spelling of a correct
path, and a carriage return flanked by non-space is not a line terminator.

`literal-at-path` is the standing precedent that a row may be built on a documented trap with zero
measured instances; ADR 0099 ruling 1's *declare the coverage rather than widen the instrument* is
the standing precedent against widening. Neither is in tension here, because nothing below is a
widening: each row is narrower than the class and says so.

Building two and declaring the third would leave the next sweep re-deriving this measurement to
answer this question, which this ticket has already been through twice.

## Ruling 2 — three rows named for their symptoms, not one row named for the cause

The cause is one route. The **counts** are the product: a reader who sees `literal-newline-escape 5`
knows which symptom is live without opening a record, and a merged row makes every count line say
only *something in this family*.

Three rows also let each predicate declare its own ceiling honestly — shape 3's rests on a body
having no real line break, shape 4's on the damaged form being disjoint from the correct one,
shape 2's on the flanking test. A single `NOT_REACHED` entry would blur three different claims into
one.

`ROW_TICKET`'s own comment says it is spelled out rather than derived precisely so a row cannot
inherit a ticket it does not belong to. Three explicit entries honor that; one merged entry quietly
stops distinguishing #723's cause from #777's symptoms.

**ADR 0099 ruling 1's stated ground for the split is now false and is superseded here.** It reads
*"The other three shapes have different causes, different homes and — in the `U+FFFD` case — an
unsolved ambiguity."* The `U+FFFD` shape was retracted by that record's own correction 1, and the
cause is one route rather than three. What survives is the ruling's real argument, which was about a
wide **predicate** firing on correct text and does not reach a row-naming question. The verdict —
#723 ships one row and the rest are a separate ticket — is untouched.

## Ruling 3 — a record may fail more than one row, and the nesting becomes a declared object

Every row that matches produces a finding. A module-level `SUBSUMED_BY` states that
`literal-at-path` is subsumed by `lost-at-dash`, and `grade` applies it, so row order in `grade`
becomes cosmetic and the suppression survives any reordering.

The nesting is real and stays suppressed. What changes is that it is recorded as a **fact about two
predicates** rather than as a fact about two lines' order. `block_scan`'s ruling is the precedent in
as many words — *the safe direction of a rule is a property of the rule and not of the pair it
belongs to* — and a positional rule is one a sixth row inserted between them breaks with nothing
failing.

It also gives the completeness walk something to check: `SUBSUMED_BY`'s keys and values must be
members of `KINDS`, so a subsumption cannot name a row that does not exist, and a reader learns the
overlap exists without reverse-engineering it from branch order.

**The report's `bodies failed` line counts distinct records and prints a findings total beside it.**
Today those are equal only because at-most-one holds; under multiplicity `len(findings)` silently
becomes a finding count under a label that says bodies.

**Declaring the counts as floors was refused.** It would make a row report a third of its population
with nothing on the page saying so, in the module whose own docstring names *a search that could not
have worked, answering like a settled negative* as this repository's recurring shape.

## Ruling 4 — each predicate is fixed, and shape 3 requires both of its clauses

**Shape 2, `carriage-return-flanked`** — a carriage return with a non-space on **both** sides. The
wider spelling, *a backslash immediately before*, fires on six and picks up three shell continuations
in pasted snippets with CRLF endings, which are legitimate authored content. The two agree on today's
corpus, so the narrower one costs nothing measured. **No backslash clause**: a carriage return
flanked by non-space is malformed whatever produced it, and adding the clause would make the
predicate depend on a theory about the route rather than on the damage.

**Shape 3, `literal-newline-escape`** — the two characters outside code spans and fences **and** the
body carrying no real line break. Both clauses are required, and not as belt and braces: each guards
a **different** false-positive class. The exclusion protects a multi-line body that writes the escape
in prose; the line-break clause protects a one-line comment that writes it inside backticks. Neither
class exists in the corpus today and both are plausible.

**The row does not grade titles.** A title can never carry a real line break, so on one the row
degrades to the exclusion alone and its safety rests entirely on an author reaching for backticks.
Zero of 915 titles carry the shape, so the exclusion costs nothing measured and removes the one
surface where the discriminator does not exist. The alternative — grade titles under the exclusion
alone and declare the missing clause — was available and was not taken.

**Shape 4, `doubled-path-separator`** — a drive letter followed by a doubled separator. The plateau
is flat, so the measurement does not choose; what chooses is that a doubled backslash in Markdown
prose is a *legitimate* escape for a literal backslash, making the widest spelling the one most
likely to fire on correct text later. The drive-letter form names the damage rather than a character
pair and is not hardcoded to one drive.

## Ruling 5 — all three refuse at the pre-publish hook

[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4's bar is no PHI, no one-for-one false block, and a remedy that is a line of text the agent
applies alone. All three clear it, and shapes 2 and 3 clear it without a judgment call:

- **Shape 2** is immune the way ADR 0099 ruling 2 argues #723's row is immune: a publication
  describing a carriage return writes the words, never the character.
- **Shape 3** is immune through its second clause: a publication describing it has real line breaks
  whatever the author does with backticks.
- **Shape 4** is **not** structurally immune. It depends on the author putting the path in a code
  span. Its remedy is *put the path in backticks*, which is both a line of text the agent applies
  alone and the house style that would have removed the ambiguity anyway, so the refusal enforces the
  convention that makes the row safe rather than fighting it.

**There are four host surfaces, not the three ADR 0099 ruling 4 names.** Three come for free the
moment a row is in `grade` — the harvest sweep, the workflow's `--github-event` step, and
`tracker_publish_hook.authorize_issue_body`, which feeds the in-process direct writer's bytes to
`grade` and turns any finding of any kind into a `ValueError`. Only the hook's `analyze` path needs
explicit wiring, because it calls `has_c0_control_character` directly rather than `grade`.

**That coupling is why an advisory posture would not have been free.** `authorize_issue_body` would
keep hard-refusing on the same row, so advising at `analyze` means one predicate refusing on one hook
entry point and advising on the other unless that function is edited to filter by row. Refusal is the
posture that is consistent across both without an edit.

**The honest declaration ships with it**, and it is ADR 0099 ruling 4's unchanged: the hook covers one
of two publishers. Every damaged record was published from a `codex/*` branch, so refusing here
prevents nothing that has happened. The workflow step stays advisory under ADR 0002 and reaches both
publishers a minute late.

## Ruling 6 — the eight newly red records are declared, not registered, and #662 goes to #802

The proposed report over the fresh harvest:

```text
#130  - lost-at-dash             8      #777  - carriage-return-flanked  3
#130  - empty-body               0      #777  - literal-newline-escape   5
#130  - literal-at-path          0      #777  - doubled-path-separator   2
#155  - double-encoded           9
#723  - c0-control-character     3      findings 30, distinct records 28
```

`literal-at-path` still reports 0, so `SUBSUMED_BY` reproduces today's behavior exactly. Eight
records go newly red: one comment and **seven pull request bodies** ADR 0099 ruling 6 deliberately
declines to repair.

**The decisive asymmetry is that this red appears in exactly one place.** The workflow grades only
the changed record, the hook only the publication being made, `authorize_issue_body` only the bytes
handed to it. None of them ever sees a historical record. The 28 are visible solely to whoever runs
the manual harvest sweep, a command that gates nothing.

**So no register and no ratchet.** The per-row count line is already the comparison instrument, and a
better one than the scratch census has: there the baseline had to be a bare integer because the
population is PHI and cannot be listed
([ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)),
whereas here each row's population is three, five and two records, named by URL, in the record a
reader arrives with. A register automates a comparison for a command nothing gates on and buys it by
writing the population down a second time, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) with a schedule. If the
sweep ever becomes a gate, the register to build is the validated kind — a listed record that stops
firing fails, on `threshold_coverage`'s inert-path discipline.

**#662's comment is the fourth member of one repair set, not a separate case.** All four damaged
comments have the same shape:

```text
#429 comment   5 lines   damage on line 3   c0=1  flankedCR=1   backslashes on that line: 8
#519 comment   5 lines   damage on line 3   c0=1  flankedCR=2   backslashes on that line: 14
#689 comment   7 lines   damage on line 3   c0=1  flankedCR=0   backslashes on that line: 10
#662 comment   5 lines   damage on line 3   c0=0  flankedCR=1   backslashes on that line: 6
```

Line 1, the branch-state block, is repaired on all four; the surviving damage sits on line 3 in every
case with the collapsed backticks still there. The only reason #723's row cannot see #662 is that its
particular collapse happened to produce no backspace character. **#802 gains it as its fourth
member.** Repairing it inside this ticket was the tempting half of ruling 6's default and is refused
for the reason the table shows: it would split one four-record repair across two tickets because this
ticket happens to own the row that sees the fourth.

**The seven pull request bodies stay.** ADR 0099 ruling 6 already weighed them and its two reasons
hold — nothing reads them as a form, nothing is copied out of them, each describes merged work.

## Ruling 7 — decision 4 closes here and the route is not pursued further

The measurement adds a **mechanism** to ADR 0099 finding 6's branch-level attribution: five bodies
with zero real line breaks and the escape in place of every one is the signature of a body passed as
an inline command-line string instead of through `--body-file`. `docs/agents/issue-tracker.md` has
carried that rule since 2026-08-11, which is #130's whole finding — a written instruction cannot
fail.

Three alternatives were priced and refused:

- **Auto-repair in the workflow**, the only option reaching the other publisher with an effect rather
  than a report, is refused outright. Repair here is a *ruled* act per record —
  [ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md) ruling 14's
  default, met case by case in ADR 0099 ruling 6 — and an auto-repairing workflow standingly
  delegates that ruling to a matcher. It also publishes, which the same workflow then grades.
- **Reporting the mechanism upstream** rests on an inference nobody has reproduced. The signature is
  strong; this repository does not report a diagnosis it has not measured.
- **A cause-side route check at the hook** — refusing an inline body argument on a publish route and
  requiring `--body-file` — is a live question and is **filed rather than built**. There is no
  measured instance from the Claude Code publisher, and requiring the flag everywhere changes how
  every publication here is written for zero measured benefit. `literal-at-path` is the precedent
  that a documented trap with zero instances can still earn a row, which is why it is a ticket rather
  than a closed question.

## What none of this reaches

**Backtick loss is the fifth symptom of the same route and stays ungraded.** It is the underlying
damage on all four comments — six to fourteen backslashes on line 3 of each — and ADR 0099 finding 3
refused the only candidate predicate because it fires on correct Windows paths. After these three
rows its residue over bodies is **one record**,
[#471's comment 5471029771](https://github.com/mshamblin5150-code/clinical-skills/issues/471#issuecomment-5471029771),
itself a member of ADR 0099 ruling 6's repair set. **`NOT_REACHED` row 1 becomes false and is
rewritten rather than appended to**: it currently says the wider escape-collapse class is outside the
module and that ADR 0099 owns its measurement, and after this build the class is graded except for
this.

**Partial literal-newline damage is not reached.** A body in which some line breaks survived and some
collapsed fails the second clause. No such record exists; the damaged five had their entire body
passed as one argument.

**A doubled separator in a relative path is not reached**, and neither is a literal newline escape or
a doubled separator in a **title** — the first by ruling 4's drive-letter form, the second by its
title exclusion.

**A publication that writes a doubled separator outside a code span is refused whether or not it is
damage.** That is the one row here whose exclusion is author-dependent rather than structural, named
in ruling 5 rather than discovered later.

**Every figure in this record is a dated floor.** The harvest is under `scratch/`, nothing committed
re-derives any of it, and the next record anybody publishes moves the denominators.

**The ticket's title says three shapes where its own table has four**, and is corrected with this
record.
