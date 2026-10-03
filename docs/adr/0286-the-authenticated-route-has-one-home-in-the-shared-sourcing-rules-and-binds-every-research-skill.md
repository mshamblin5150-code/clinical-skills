# The authenticated route has one home in the shared sourcing rules and binds every research skill

**Measured at:** 4cb3818a65326472252ef6084b91530a06fcc34a

[#1282](https://github.com/mshamblin5150-code/clinical-skills/issues/1282) was filed from
[ADR 0235](0235-a-browser-tab-is-a-private-output-location-and-a-page-action-naming-none-is-refused.md)
ruling 3. It found the authenticated-route rule restated across skills with no home and its
try-before-giving-up obligation written three ways. Grilled 2026-10-03 against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

### The rule has three parts and the skills carry different subsets

The route is the clinician's signed-in Chrome through `mcp__claude-in-chrome__*`, never the in-app
browser pane. The paywall test lets a refuter write `paywalled` only when the body stays
inaccessible through that route. The research obligation requires a research agent to try the
route before giving up on a sought source, settling for an open substitute, or writing
`STATUS: unsourced` because of a wall.

Three phrasings were counted over whitespace-normalized text in every Markdown file under
`skills/`, 26 files: `in-app browser pane`, `must (attempt|try) it before giving up`, and
``before (writing )?`paywalled` ``, case-insensitive.

| skill | pane | before giving up | before `paywalled` |
| --- | ---: | ---: | ---: |
| `discussion-post` | 1 | 1 | 1 |
| `discussion-reply` | 1 | 1 | 1 |
| `practicum-case-study` | 1 | 1 | 1 |
| `course-assignment` | 0 | 1 | 0 |
| `peer-critique` | 0 | 1 | 0 |

No other file under `skills/`, `skills/_shared/reference/sourcing.md` included, carries any of the
three. Had the copies not existed, every cell would read `0`.

**The two short versions lack the paywall test while both skills keep `paywalled` in their record
shape.** In `course-assignment` and `peer-critique` a refuter can therefore write `paywalled` on an
anonymous login wall, which the other three forbid. Both versions entered with the skill's own
creating commit, `1803736d` on 2026-09-02 and `7e5244b6` on 2026-09-10, and no ruling records the
difference.

### The condition on the research obligation has no recorded input

Four skills apply the research obligation *"if the profile records the Authenticated route as
available"*, and `course-assignment` applies it if *"the clinician's profile says an available
research agent has an authenticated route"*. `setup-clinical-skills` step 1 asks while exploring
whether a browser tool reaches the clinician's logged-in session, and writes no profile line for
the answer. The only related profile line is `UPTODATE-ACCOUNT`, which governs the UpToDate store's
re-read window alone. Read literally, the research obligation never applies.

### The condition and the per-skill copies were ruled

[ADR 0055](0055-the-research-fan-out-s-authenticated-route-is-required-where-the-profile-has-one-and-the-substitution-it-would-prevent-stays-unreached.md)
ruled the research obligation when it was grilled. Its ruling 4 puts the tool string at exactly one site
per skill, its ruling 5 binds the obligation's existence in each ledger-publishing skill, and its
ruling 6 makes the obligation required where the profile records a browser and silent where it does
not. `tools/test_research_ledger.py` carries ruling 5 as
`EveryLedgerPublishingSkillCarriesTheAuthenticatedResearchRoute`, whose matcher requires the words
`profile` and `available` in each skill's block. This record was found after the first five rulings
below were given and was put to the clinician before any of them was recorded.

### The home already has a guard

All five skills link `skills/_shared/reference/sourcing.md`.
`EveryRuledFanOutReadsTheSharedSourcingRules` asserts that file's rule headings as an exact list and
that every derived briefing skill links it, and its local-copy ratchet already refuses retired
phrasings of a shared rule. ADR 0235's refusal of a new shared sheet rested on a sheet binding only
by link; this file's link is itself under test.

## Ruling 1. It is one rule for every research skill

All five research skills follow all three parts. The narrower statements in `course-assignment` and
`peer-critique` are drift, not narrowings. Nothing about a course assignment or a peer critique
makes an anonymous login wall better evidence of a paywall.

## Ruling 2. The shared sourcing file is the rule's one home

A new section of `skills/_shared/reference/sourcing.md`, titled *A wall counts only after the
Authenticated route is tried*, follows *A failed read is not a negative* and holds all three parts.
It is the only site under `skills/` that names `mcp__claude-in-chrome__*` for this rule. The five
skills delete their copies of the route, the paywall test and the research obligation, and keep
their existing link to the file and `paywalled` in their record shapes. The section must sit beside
the VitalSource section PR #1322 added rather than replace it.

`CONTEXT.md`'s **Authenticated route** definition stands unchanged; it defines the path, and the
shared section holds what an agent must do with it.

## Ruling 3. The route is required unconditionally

No profile line decides whether it applies, and none is added. Where the route cannot be reached in
a run, because the extension is disconnected or the agent has no browser, the attempt is a failed
read under *A failed read is not a negative*: the research record is `STATUS: unreadable` and the
refutation is `REFUTATION: unreadable`, each with `INSTRUMENTS` naming the attempts. An unreachable
route never yields `paywalled`, and never yields `STATUS: unsourced` on the ground of a wall.
`UPTODATE-ACCOUNT` keeps its UpToDate-only role.

## Ruling 4. Two checks guard the home and one limit is declared

`EveryRuledFanOutReadsTheSharedSourcingRules` adds the new title to its exact heading list and
asserts the section's load-bearing sentences: the route and tool string, the pane exclusion, the
paywall test, the research obligation's three giving-up moments, and the unreachable-route outcome.

A second check fails when any Markdown file under `skills/` other than the shared file carries one
of the three phrasings measured above, over whitespace-normalized text. It reads nonzero on the
tree at the measured commit and zero after the build, and a planted copy in a synthetic skill text
drives it red. `paywalled` alone is not a trigger. The local-copy ratchet is the natural home.

Its declared limit stands beside it: a restatement in other words passes. ADR 0235 measured that a
browser-word detector misses most browsing passages; this check asks a narrower question, whether a
known copy returned, and claims nothing wider.

`EveryLedgerPublishingSkillCarriesTheAuthenticatedResearchRoute` and
`authenticated_research_route_blocks` are retired, because they require the copies ruling 2
removes.

## Ruling 5. The copies outside `skills/` stay

ADR 0042 is where the refuter's route requirement was ruled, and the new section cites it as the
source. `reference/medatrax-fields.md`'s *real Chrome, not an in-app browser* sentence is a portal
login rule resting on the password manager, not a research rule, and it stays. The second check
reads `skills/` only.

## Ruling 6. ADR 0055 rulings 4, 5 and 6 are overturned

Ruling 6's ground was that an unconditional rule is false wherever no browser exists. Ruling 3
answers that ground directly: a missing browser becomes a named failed read, so the rule is true in
both environments, and the profile switch it rested on was never recorded. Rulings 4 and 5 bound one
copy per skill because the surrounding prose differs per skill; ruling 2 leaves no copy to bind, and
the shared file's link and heading tests bind the one home. ADR 0055 rulings 1, 2, 3 and 7 stand,
including the `CONTEXT.md` term and the obligation's trigger at the moment of giving up.

**The ADR 0280 marker and declaration are deferred, not skipped.** `tools/test_adr_supersession.py`
reads a marker only beneath a `## Ruling N` heading, and ADR 0055 numbers its rulings as items
under a dated heading. A planted marker beneath ruling 6, with the matching declaration in a
synthetic copy of this record, produced *unread supersession marker* and *has no matching marker*
against a clean baseline, so writing either here turns the suite red. The reader gap is filed as its
own ticket, whose build writes ADR 0055's three markers and this record's declaration.

## Rejected options

**Keep the narrower statements as deliberate.** No reason was ever recorded, and it leaves the
paywall loophole open in two skills.

**Fold the rule into *A failed read is not a negative*.** It saves one heading-list edit and buries a
paywall rule under a section about retrying instruments.

**Identical copies in each skill bound by a test.** Five sites move in lockstep on every wording
change, the copy-held-by-check shape ADR 0182 refused where one home exists.

**Add an `AUTHENTICATED-ROUTE` profile line.** It adds a setup question, reopens the loophole where
the answer is `no`, and still cannot say whether Chrome is connected on the day.

**Keep the profile condition as written.** It is a switch nothing turns on.

**Widen the phrase check to `reference/` and `docs/adr/`.** It fires on ADR 0042, which cannot be
honestly edited, and on the Medatrax login rule, which is not a copy.

**Keep ADR 0055 rulings 4 to 6 and reopen rulings 2 and 3.** The five copies stay and the drift is
repaired copy by copy.

## Consequences

**`course-assignment` and `peer-critique` refuters gain the paywall test**, a little more browser work
per walled source and no new kind of step.

**A run without a browser reports unreadable sources rather than paywalled ones.** Both pass; the
completion report counts more unreadable records.

**The rule's wording changes in one file**, and a returned copy of the old wording fails a test.

## What this does not reach

**Whether an agent actually opened the browser.** ADR 0055's *required, not verified* limit stands;
the checks reach the sentence and nothing reaches the behavior.

**A restatement in other words**, by ruling 4's declared limit.

**ADR 0055's markers until the filed reader ticket is built**, by ruling 6.
