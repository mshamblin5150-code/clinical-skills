# The one-row-object refusal was a claim about a module's prose population and it expired for every queued row

[ADR 0052](0052-a-codification-year-is-provenance-and-the-snapshot-behind-it-is-declared-unreached.md)'s
second addendum ruled this for [#534](https://github.com/mshamblin5150-code/clinical-skills/issues/534)'s
piece B on 2026-08-27 and closed by naming the other two rows **as unexamined**:

> *"#498's and #500's rows are named by ADR 0053 ruling 1 in the same sentence as #534, so the same
> reasoning appears to reach them, and neither was examined here. Not asserted, and not filed as a
> finding, because a claim about two tickets nobody read is the shape this sweep spent the day
> removing."*

They were read the same day. **Ruled 2026-08-27 by the clinician**, on the same instruction that
settled #534. This record supersedes that paragraph and is what it points at.

## Measured before ruling, at `cd8e4cf`

**Three ratified records refuse a one-row `research_ledger` limits object, and all three refuse the
same narrower thing in the same words.** Read verbatim rather than summarized:

- [ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
  ruling 9 — *"Introducing the object with one row **while five stay in prose** is ruling 7's
  numerator-without-denominator one level up — it would read as* these are the limits*."*
- [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
  ruling 9 — *"introducing the object with one row **while the others stay in prose** reads as* these
  are the limits *— a numerator with no denominator."*
- [ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
  ruling 11 — *"ADR 0042 ruling 9's objection does not survive the transfer, and the reason is
  specific to this module. It was made about `research_ledger`, **which holds five prose limits**, so
  an object with one row genuinely would have been a numerator with no denominator."*

**None of the three refuses a row in a populated object.** ADR 0050 ruling 11 is the proof rather
than the restatement: having said the objection is specific to the module's prose population, it went
on to **build** the object for `discussion_reply_scan`, on the ground that one row there *is* the
whole population.

**So the refusal was never about arity.** It was a claim about a ratio — one row against many
prose limits — and
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 1 changes the denominator by building `research_ledger.DECLARED_LIMITS` whole, over a
population derived by reading the module end to end.

**And ADR 0053 ruling 1 had already ruled the consequence, naming all three tickets in one
sentence:** *"#498, #500 and #534's piece B each own a limit that is not true yet [...] **each ticket
appends its row when it lands** [...] piece B stops being prose no test binds and becomes one row
appended to a bound object."*

**None of the three tickets was told.** At `cd8e4cf`, before this record:

| ticket | what its body still said | where |
| --- | --- | --- |
| #534 | *the limit lands as prose beside the row* | B1 — **corrected 2026-08-27** by ADR 0052's second addendum |
| #498 | *"Do not introduce `research_ledger.NOT_REACHED` in this change. The module has five limits in prose [...] declare it in prose beside the row."* | *What must not come out of this* |
| #500 | ADR 0042 ruling 9's *"The narrowed limit lands as prose here"* | inherited from its record |

**#498 names the remedy and assumes it has not happened**: *"The migration is its own ticket."* That
ticket is #535, and ADR 0053 ruling 1 builds it.

**#500 has been contradicting itself since 2026-08-26 and this resolves it in its own favor.** Its
`Done when` asks for the limit *"on `#241`'s terms, **as a named declared limit rather than as
prose**"* while its record ruled prose. Both cannot hold. The row is what the `Done when` already
asked for.

## Ruled 2026-08-27

**1. Every queued row lands in `research_ledger.DECLARED_LIMITS`, and the one-row-object prohibition
survives exactly as written.**

Only the prohibition's scope was ever in question: **do not create the object for this row**.
Appending to one built for the module's whole population is the thing all three records were
distinguishing, and ADR 0050 ruling 11 demonstrates the distinction by going the other way on the
same question for a different module.

The row's shape is ADR 0053 ruling 8's and is not any of these tickets' to invent — a `key`, a
`limit` sentence and an `evidence` disposition.

**2. The rows are unconditional, never conditional on whether the object exists at merge time.**

The accommodating option — *a row if #535 has landed, prose if not* — was declined for #534 and is
declined here for the same reason. #535, #498 and #500 all carry zero blockers, so it makes the
build outcome depend on merge order: **one specification, two different trees**, which is
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s subject, and the prose
branch is what ADR 0053 ruling 1 calls *prose no test binds*.

**3. #498 and #500 split rather than block, and that is where they part from #534.**

#534's piece B was already blocked on #498 and is the whole of what remains there, so an edge to
#535 cost nothing. These two are different: each carries a **substantial independent build** — #500
adds a field to three tuples and three new kinds, #498 adds `STATED-EXPIRY` and six `Done when`
bullets — and in each the limit is one deliverable among several.

So each takes #534's arrangement: **piece A is the independent build and is unblocked; piece B is
the row and waits on #535.** `blocked_by #535` is recorded against the ticket, and each body says
plainly that piece A is unblocked by it.

**Two alternatives were declined.** Blocking each whole ticket stops work that depends on nothing
#535 builds. Recording no edge at all leaves a builder to finish piece A, find no object to append
to, and either break or **close the ticket without its declared limit** — the quiet failure, and the
one [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) exist to prevent.

**4. No ruling in ADR 0040, 0042, 0050 or 0052 is rewritten.**

Each stands as ruled on its date with its ground stated. What this record says is that one ground was
shared by all of them, that it was a claim about the module's prose population rather than about
arity, and that ADR 0053 ruling 1 ended it. ADR 0052's second addendum said the same for #534 and its
closing *not asserted* paragraph is superseded by this record rather than corrected in place, because
what changed is that the two tickets were read.

## What this does not reach

**Whether either ticket's other rulings still hold.** Only the limit's home was examined. #498's
six `Done when` bullets and #500's three kinds were read for structure and not re-adjudicated.

**Whether a fourth queued row exists.** Three are named by ADR 0053 ruling 1 and three were read. A
limit queued by a ticket that record does not name is outside this, and nothing here derives the
population of queued rows — that is #535's object to state once it exists.

**Whether `checks_ledger.py` and `discussion_reply_scan.py` take the same reasoning.** Both hold no
limits object and both are named in ADR 0053 ruling 2, which files them rather than absorbing them —
`checks_ledger` to [#565](https://github.com/mshamblin5150-code/clinical-skills/issues/565) and
`discussion_reply_scan` to ADR 0050 ruling 11's unbuilt order. Their populations are their own and
the ratio argument here says nothing about either.

## Consequences

#498 and #500 each gain a piece split, a corrected limit instruction and `blocked_by #535`. #535 is
unchanged and is still blocked by nothing — ADR 0053 ruling 1 refused to put it behind the tickets
queuing rows, and every edge here points the other way, so no cycle is closed.
