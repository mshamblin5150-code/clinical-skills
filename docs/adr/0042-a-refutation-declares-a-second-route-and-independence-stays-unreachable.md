# A refutation declares a second route and independence stays unreachable

[#500](https://github.com/mshamblin5150-code/clinical-skills/issues/500) was filed over a live
`discussion-reply` run in which one agent was briefed as a combined research-and-refutation pass by
mistake. It downloaded a scanned rule filing with a zero-length text layer, rasterized it at 160 dpi,
read the numbers **visually**, wrote them into the `RESTATEMENT`, and then cleared **its own
transcription** in the `REFUTATION`. `tools/research_ledger.py` returned exit 0, every `#231` row
passed, and an independent reader caught it on a coincidence of phrasing.

Grilled 2026-08-26 against `fdaa097`. **Ten decisions, ruled by the clinician on that date.**
Nothing is built here; this is the record the build reads.

## Measured before ruling, at `fdaa097`

- **`tools/research_ledger.py` has no declared-limits object.** The limit is prose in the module
  docstring and again in a code comment above the refutation rows. `#535` is the filed fix and is
  itself unruled.
- **`STATED-EXPIRY`, `#498`'s ninth field, is not in the tree.** `REQUIRED_WHEN_SOURCED` is seven
  fields.
- **Two of the ticket's own four candidates are falsified in its own sweeps.** The substance row is
  refuted by the `#496` sweep — the failing record *did* name what it checked, about its own
  transcription. The identifier pair is refuted by the body — an orchestrator that briefs one agent
  writes two tags for it.
- **ADR 0038 is a ruled precedent, not a worked one.** `INVOKED` appears nowhere in `tools/` or
  `skills/`; the marker in code is still `AMPLIFICATION` at `tools/discussion_artifact.py:17`, the
  name ruling 7 renamed. The `#500` sweep calling it a *worked* precedent overstates it.
- **Three skills publish the ledger template** — `discussion-post`, `discussion-reply`,
  `practicum-case-study` — and **exactly one worked example is bound to the scanner**,
  `tools/test_research_ledger.py:1198`, `practicum-case-study` only.
- **Two of the three skills declare no limit at all.** `skills/practicum-case-study/SKILL.md:727`
  states one in prose; `discussion-post` and `discussion-reply` return zero hits.
- **`tools/test_discussion_post_skill.py:14-16` already opens all three SKILL.md files.**
- **`paywalled` passes on a stated ground the environment contradicts.** The module docstring, a code
  comment, and `skills/practicum-case-study/SKILL.md:582` all rest it on *failing them would refuse
  every UpToDate record*. `skills/setup-clinical-skills/SKILL.md:75` already asks whether a browser
  tool reaching the clinician's real logged-in session is available, for portal steps, and it is
  wired to the research fan-out nowhere.
- **No `claims.md` is tracked.** Two live ledgers exist under `scratch/runs/` in the owning checkout,
  both from finished submitted work, one of them the run this ticket was filed off.
- **Name census.** `SECOND-READ`/`SECOND READ` is 42/67 in `tools/` — `threshold_sheet.py` gate 5
  owns it. `INSTRUMENT` is 123 in `tools/` and 67 in `docs/` — this repository's word for a checker.
  `SECOND-ROUTE`, `REFUTATION-ROUTE`, `SECOND-PASS`, `REACHED-BY` and `OPENED-VIA` are zero
  everywhere.

## Ruled 2026-08-26

### The mechanism

1. **Build the route candidate and declare what it does not reach — both, not one instead of the
   other.** The ticket's option 1 and option 2 are dead on its own evidence. Option 4 alone leaves
   the one recorded instance's discriminator on the floor; option 3 alone republishes the overclaim
   this repository keeps recording. The declaration is not the alternative to the row, it is the
   other half of it.

2. **The route gets a named slot; it is not graded inside `REFUTATION`'s reason.** `BARE_REFUTATION`
   already requires that reason to have substance and the failing record passed it. Grading a route
   inside prose means hunting for route-shaped wording, which has no honest general text pattern —
   `discussion_post_scan.NOT_REACHED` already declares that shape — and which is the neighbour of the
   one thing `#500` forbids by name.

3. **The slot holds a declared difference in two halves, and the row fires when they match.** Not one
   route, and not a dated route. Those two both let the recorded failure through *in its honest
   form*, which makes them a shape that reads as coverage. An honest combined agent has one route, so
   it writes the same thing twice and fails; that is the mistake that actually happened, as opposed
   to a lie, which nothing here stops and ruling 1 accepted.

4. **Every disposition owes it — `stands`, `refuted` and `paywalled` alike.** Exempting `refuted`
   leaves the repair path open, and the repair path is where a run under time pressure goes.
   Blessing a `paywalled` escape sentence rebuilds the hatch: one sentence, satisfying every
   substance test, available verbatim to the self-clearer. Where a second route genuinely was not
   available the truthful entry is the identical pair and **the row firing is correct**.

5. **The clinician's authenticated Chrome is a required attempt before `paywalled` may be written.**
   He pays for UpToDate and holds ENA and ANA journal access through that session. A refutation that
   never tried the only route that would have worked is a second reading that declined to read. This
   needs **no new row** — under ruling 3 a refuter that tries it has two different halves and one
   that does not has the identical pair, which the equality check already fires on. What is missing
   is only that no skill names the route. It is `mcp__claude-in-chrome__*`, the real browser with its
   existing sessions, **not** the in-app Browser pane, which is a separate unauthenticated surface a
   run would truthfully report a wall from.

6. **The slot is `SECOND-ROUTE`.** `INDEPENDENCE` is refused on principle rather than on collision:
   the field cannot establish independence, that is the exact thing ruling 1 accepts as unreachable,
   and a field named for a property it cannot prove is the name a future reader would cite as
   evidence the hole is closed. `RE-READ` is refused because it excludes an independent corroborating
   source, which is a blessed form. `REACHED-BY` and `OPENED-VIA` name one route over a two-part
   value. `PAGE-YEAR` is the precedent for a hyphenated compound in this ledger.

### The rows

7. **Three new kinds, attributed `#500`: `unsplit-second-route`, `bare-second-route`,
   `second-route-unchanged`.** `MISSING_FIELD` and `UNSOURCED_WITH_CITATION_FIELD` come free by
   adding the field to `REQUIRED_WHEN_SOURCED` and `CITATION_FIELDS`. **An unparseable value is a
   finding and not exit 2**, on `UNKNOWN_STATUS`'s and `UNKNOWN_REFUTATION`'s stated reason — the
   field gates the row below it, and a clean report over a row that never ran is the silent pass this
   directory exists to refuse. **Separator is ASCII `->`, split on the first occurrence with the
   remainder joining the right half**, so a second arrow does not make three halves and fail for a
   reason nobody meant. `bare-second-route` is not redundant with `second-route-unchanged`: an empty
   right half normalizes *unequal* to the left.

### Where it lands

8. **The template and the declaration land in all three publishing skills, and the bind is derived
   rather than a typed list of three.** A hand-list of three is the matcher that turns a partial read
   into a clean whole, and writing one inside a change whose own finding is *only one of three is
   bound* would be the defect committed in its own repair. Discover the publishing skills by their
   template, then assert both directions: every discovered template carries every
   `REQUIRED_WHEN_SOURCED` field, and every discovered worked example passes the scanner. The
   discovery predicate's ceiling goes in the test's docstring rather than being claimed away.
   `practicum-case-study:727`'s existing sentence is **corrected rather than left**, because *cannot
   see whether the refutation came from a second agent at all* is about to be true and misleading.
   **The declaration text is not bound three ways** — the surrounding prose differs per skill and
   asserting three copies match would forbid the divergence `#253` already ruled permissible.

9. **The narrowed limit lands as prose here; `#535` stays the object's owner and is told the new
   text.** `#535` has already ruled that introducing the object with one row while the others stay in
   prose reads as *these are the limits* — a numerator with no denominator — and it is itself unruled
   on four points including whether its population is derived. Building it whole inside `#500` is
   scope creep wearing a completeness argument. `#500`'s own *Done when* is a disjunction and the row
   satisfies its first limb outright. **A comment on `#535` replacing its fifth bullet is part of
   this ticket's close, not something that follows it.**

10. **Hard cutover. Pre-existing ledgers fail `MISSING_FIELD` and are not backfilled.** A branch on
    the `DATE:` header is keyed on a value the graded party writes, so the escape is one back-dated
    line. Backfilling the two live ledgers means authoring a declared difference nobody recorded at
    the time — inventing the evidence the field exists to demand, in the ledger of the run that
    produced the defect. **The two failures are the mechanism working on its own founding instance**,
    and suppressing them would make the build a worse record than the prose it replaces.

## What must not come out of this

**Do not key any row on wording.** *"a second agent"* versus *"the agent"* is how the live instance
was caught and it is an accident of style. The equality check reads two halves of one field; it does
not read vocabulary.

**Do not make the ledger assert agent identity.** The module is offline and reads one file. A field
claiming two agents ran is worth exactly what the writer's discipline is worth, which is the thing in
question.

**Do not read a clean `SECOND-ROUTE` as an independent refutation.** It establishes that the record
*declares* a second route. Ruling 1 bought the declaration and never the fact.

## Declared limits

`SECOND-ROUTE` reaches only that the record **declares** a route the first pass did not take. **No
row can see that the refuter was a different agent, that it actually took the route it declared, or
that it opened anything.** That is the three-clause replacement for the module's current single
clause, and it is the text `#535` must carry rather than the one it was filed with.

Ruling 5 makes the authenticated route **required**, not verified: nothing here can see that Chrome
was opened.

## Consequences

- Every ledger written before this build fails `MISSING_FIELD` on every sourced record. That is
  correct and is worth knowing before reading it as breakage — `differential_scan.py`'s precedent for
  a documented non-zero exit.
- `paywalled` narrows from *behind a subscription* to *walled even through the clinician's
  authenticated session*, which retires the objection that ruling 4 fails honest paywalled records.
- Two things are **filed rather than folded in**, because neither is `#500`'s: the corrected grounding
  for `paywalled` in the three places it is stated, which is `#231`'s ruling narrowed by a fact; and
  whether `RESOLVED` gains the same authenticated-route instruction on the research side, which is a
  different fan-out.
