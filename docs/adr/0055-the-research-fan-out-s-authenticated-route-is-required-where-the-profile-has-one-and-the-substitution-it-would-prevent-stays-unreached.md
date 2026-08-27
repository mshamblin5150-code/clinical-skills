# The research fan-out's authenticated route is required where the profile has one and the substitution it would prevent stays unreached

[#500](https://github.com/mshamblin5150-code/clinical-skills/issues/500) and
[ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)
ruling 5 made the clinician's authenticated Chrome a required attempt **for the refuter** before
`paywalled` may be written. That ruling deliberately said nothing about the **researcher**, and
ADR 0042's own consequences filed the other half rather than folding it in.
[#541](https://github.com/mshamblin5150-code/clinical-skills/issues/541) is that half.

Grilled 2026-08-27 against `3376292`. **Seven decisions, ruled by the clinician on that date.**
Nothing is built here; this is the record the build reads.

## Measured before ruling, at `3376292`

Re-derived in this session by command, not carried from the ticket.

| | |
| ---: | --- |
| `REQUIRED_WHEN_SOURCED` | 7 fields; the `FIELD` regex parses 8 names |
| `SECOND-ROUTE`, ADR 0042's field | **unbuilt** — 0 hits in `tools/` |
| `STATED-EXPIRY`, ADR 0040's field | **unbuilt** — 0 hits in `tools/` |
| `RESOLVED` spec sites | 3, one per publishing skill, identical line |
| `mcp__claude-in-chrome` in `skills/` | **0** |

**Dispositions across every claim ledger in the owning checkout** — 4 ledgers, 23 records, counts
only, on `corpus_census.py`'s terms:

| disposition | count |
| --- | ---: |
| `STATUS: sourced` | 22 of 23 |
| `STATUS: unsourced` | **1 of 23** |
| `REFUTATION: paywalled` | **0 of 23** |

**`paywalled` has never been written.** ADR 0042 ruling 5 makes a required attempt before a word
with a zero base rate, which is the datum every ruling below turns on.

**Three findings the ticket did not have.**

- **`tools/test_discussion_post_skill.py:14-16` types the three skill paths as constants.** That is
  the hand-list of three ADR 0042 ruling 8 calls *the matcher that turns a partial read into a clean
  whole* — already live in the file #500's own derived bind will land beside.
- **Two tickets are queued to write `mcp__claude-in-chrome__*` into the same three files** from
  separate branches. [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s
  byte-identical trap, visible before the merge rather than after, which is the second time ADR 0042's
  lineage has caught this shape in advance.
- **`skills/setup-clinical-skills/SKILL.md:75` asks whether the browser tool is available**, so the
  answer is per-account and can be *no*. Neither #500 nor #541 had named that limb.

## Ruled 2026-08-27

### What the rule attaches to

1. **The research-side attachment point is `unsourced`, not `RESOLVED`.** The ticket assumed
   `RESOLVED` and its own decision 2 correctly found nothing there to grade — one locator, no second
   half, so ADR 0042's equality trick does not transfer. It does not transfer because the field is
   wrong. Ruling 5 attaches its requirement to a **passing disposition**: `paywalled` is the weakest
   thing that exits 0, so the rule is *you may not take the free pass without trying the route that
   would have worked*. The researcher has no disposition field, and what a walled researcher writes
   is `STATUS: unsourced - <what was searched>`, which `tools/research_ledger.py:66` says in as many
   words **is not a failure**. Same shape as `paywalled`: a wall routes to a passing branch, the
   reason sentence satisfies every substance test, and nothing asks whether the one route that works
   was tried.

   **The ticket's own prohibition becomes self-satisfying, and that is a derivation rather than a
   concession.** *Do not require an authenticated fetch for a source the clinician already supplied
   in the evidence dump* — a supplied source produces a **`sourced`** record. The two sets are
   disjoint by construction, the rule cannot fire on the ordinary case, and decision 1's *is that one
   answer or per skill?* has nothing left to split on. **One answer, all three skills, for free.**

2. **The subject is both shapes under one instruction: the declared wall and the silent
   substitution.** The zero above has two readings and they point at different tickets. Walls may be
   rare here; or **a walled researcher does not write `unsourced`, it finds something else** — which
   is honest, desirable, and produces exactly this table. The second shape is a record that is
   `sourced`, passes every row, would pass `SECOND-ROUTE`, and took a weaker open substitute because
   the better source was walled and the account's own access was never tried. **No field records what
   was wanted and not gotten**, and there is no second half to build an equality check from.

   So the obligation attaches at **the moment the agent decides to give up**, which is the moment
   both shapes share. One sentence, **zero new fields and no row.** That is ruling 5's own posture
   rather than a new one — *required, not verified* — and it is what
   #541's *Do not assume the answer is a field* asks for.

   **A row is refused on the measurement and not on cost.** At 1 of 23 and 0 of 23 there is no
   population to ground a false-alarm rate on, which is
   [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection holding where
   it was not answered.

3. **A refuter that reached a page the researcher did not does not escalate on a thin-but-true
   restatement, and never rewrites the `RESTATEMENT`.** The ticket's decision 3 asks what names the
   state where the researcher was walled and the refuter was not. **Once #500 is built, that state
   names itself** — `SECOND-ROUTE` holds a declared difference in two halves and fires when they
   match, so such a record writes two genuinely different halves, passes, and is legible on its face.
   The premise that nothing names it is true only of the tree today.

   The remedy the ticket floats is refused by name. *"It may want a `RESTATEMENT` rewritten from the
   reachable page"* — the only agent that reached the page is the refuter, and a refuter that
   rewrites the `RESTATEMENT` becomes the author of the thing it exists to check. **That is #500's
   founding defect performed deliberately** instead of by mistake.

   Widening `refuted` to cover it is refused too, and it fails
   [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s line twice: it fires on
   a record that is **true**, and it asks the refuter to judge which page a sentence *was written
   from*, which is a reading with no honest test behind it and the neighbour of the wording-keying
   ADR 0042 forbids outright. The residue is real and is declared below. **What shrinks it is ruling
   2's instruction, not a row** — a researcher that tried the session in the first place does not
   produce this record.

### Where it lands and what holds it

4. **It lands after #500, extends the paragraph #500 writes, and names no tool string.** ADR 0042
   ruling 5 says *what is missing is only that no skill names the route*, so #500's build introduces
   `mcp__claude-in-chrome__*` to all three skills. This ruling puts a research-side sentence in the
   same three files. **Exactly one site per skill holds the tool string**, and this ticket's sentence
   refers to *the authenticated route* that paragraph establishes.

   The restriction is not tidiness. A tool rename with two naming sites is
   [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two-copies shape, whose
   recorded instance in this repository — `docx_write.NOT_APPLIED` — is precisely *a prose edit to
   either copy fails nothing*. Folding this into #500 was refused as the scope creep ADR 0042
   ruling 9 already refuses by name; #500 is ruled and waiting to be built, and reopening it costs a
   re-grill. **Queue: `#500` then `{#540, #541}`**, both of which touch the same three skills.

5. **Bind the obligation, not the text.** Discover the publishing skills by their ledger template —
   ADR 0042 ruling 8's derived discovery, so a fourth skill cannot arrive uncovered — then assert
   each discovered skill's research brief carries the route obligation, matched against a
   `prose_bind.normalized` block and never a line, because every sentence in these skills is
   hard-wrapped. **Assert existence per skill; do not assert the three texts match.**

   That is ruling 8's own split applied one level down: it binds the *template* derivedly and refuses
   to bind the *declaration text* three ways, because the surrounding prose differs per skill and
   [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) already ruled that
   divergence permissible. Three typed copies is refused by that reasoning; no bind at all is what
   this repository has recorded rotting twice by name.

6. **Required where the profile records that the browser tool is available, and silent where it does
   not.** The modality is a separate choice from the trigger, because ruling 5 is required *before a
   specific word may be written* and ruling 2 widened the trigger to a moment with no word attached.

   Unconditional requirement writes a rule the environment can falsify, **which is #540's defect
   exactly** — a stated ground that is false of the account it is stated for, one artifact over.
   Merely offering it is what the tree has now: `setup-clinical-skills` names the route and it is
   *wired to the research fan-out nowhere*, which is why this ticket exists. Keying on the profile's
   own recorded answer makes the rule true in both environments and neither run has to lie.

### The glossary

7. **`CONTEXT.md` gains `Authenticated route` under `### Checks`, filed against `Second route`.**
   The term is named in two ADRs and two tickets and in no glossary, and the conflation it invites is
   live: a second route is a **comparison between two passes' paths**, an authenticated route is
   **one particular path**, and ruling 5 gets read as being about independence the moment they blur.

   **`Reachable substitute` is not filed.** It is ruling 2's shape and it has **zero measured
   instances** — inferred from an absence, consistent with substitution and equally consistent with
   walls being rare. A glossary is the one place in this repository where a name reads as a settled
   thing, and `Second route`'s own `_Avoid_` line refuses `independence` on exactly that ground: *a
   field named for a property it cannot prove is the name a future reader would cite as evidence the
   hole is closed*. Same argument, one artifact over. It stays in this record's prose, where it is
   visibly an inference with its evidence beside it, and earns an entry if an instance is ever read
   off a run.

## What must not come out of this

**Do not build a row.** Ruling 2 refused one on a measurement, and the measurement is 1 of 23 and
0 of 23. A row here would be a cut point named at an edge with no distribution under it —
`SPACE_ADVANCE_FRACTION`'s recorded failure and #97's objection at once.

**Do not add a field.** Three of this module's last four decisions added one and two of those are
still unbuilt. The obligation attaches to a moment, not to a value, and nothing offline can read the
moment.

**Do not let the refuter author the `RESTATEMENT`.** Ruling 3 refuses it; the reason is that it
rebuilds #500's founding defect, and a future reader reaching for it will be reaching for the
cheapest-looking repair.

**Do not read a skill that states the obligation as a run that met it.** Ruling 5's bind reaches the
sentence and nothing reaches the behaviour.

## Declared limits

The research-side authenticated route is **required, not verified**, and the limit has two clauses
where ruling 5's had one. **Nothing can see whether the browser was opened**, which ruling 5 already
concedes; **and nothing can see whether the profile's answer was consulted**, which is new with
ruling 6's conditional. The bind reaches that each publishing skill states the obligation. No check
reaches either half of whether a run met it.

**The substitution shape is unreached and stays unreached.** A record that took a weaker open source
because a better one was walled is `sourced`, passes every row, and passes `SECOND-ROUTE`. Ruling 2
covers it with an instruction precisely because no field can hold it.

**A thin-but-true `RESTATEMENT` written off an abstract is not a finding.** Ruling 3 declares it
rather than closing it.

`tools/research_ledger.py` still has **no declared-limits object**;
[#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535) is the filed fix and is
itself unruled. On ADR 0042 ruling 9's precedent the text above lands as **prose in the module
docstring**, and #535 stays the object's owner and is told this text in a comment as part of closing
#541 rather than as work that follows it.

## Consequences

- **#541 is blocked on #500.** It was not before; ruling 4 makes it so, and #540 was already ordered
  there. Nothing in this record can be written into a skill until #500's route paragraph exists.
- **#541 ships no code in `tools/`.** Its whole deliverable is a sentence in three skills, a bind, a
  prose limit and a glossary term. That is unusual for this directory and is ruling 2's measurement
  rather than an omission.
- **ADR 0042 ruling 5's asymmetry is closed in the direction the ticket did not expect.** The
  researcher's requirement is *broader* in trigger — any settling, not one word — and *narrower* in
  modality, being conditioned on the profile. Neither ticket predicted that split.
- **`paywalled`'s zero base rate is now on the record.** Ruling 5 requires an attempt before a word
  nobody has written; that is not an argument against it, and it is the datum any future
  re-derivation of either ruling has to start from.
- **The hand-list at `tools/test_discussion_post_skill.py:14-16` is named and not repaired here.**
  It is #500's bind's problem before it is this one's, and repairing it inside #541 would be the
  scope creep ruling 4 just refused.
