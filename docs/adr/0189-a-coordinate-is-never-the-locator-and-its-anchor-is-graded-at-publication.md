# A coordinate is never the locator and its anchor is graded at publication

[#928](https://github.com/mshamblin5150-code/clinical-skills/issues/928) was filed on 2026-09-06 out
of [#791](https://github.com/mshamblin5150-code/clinical-skills/issues/791)'s grilling. #791 ratchets
`path:NNN` citations to zero in tracked prose; this is the half a repository walk cannot reach,
because an issue body is not in the tree. Thirty-two sweep comments followed over six days, every one
supplying a fresh instance and none answering a decision — the thread names a coordinate published,
corrected, and the correction stale within the hour; a symbol deleted rather than moved; a statement
moved to another module, which a same-file history search reads as a deletion; and a ratified record
stale at its own merge commit because a sibling branch grew the file twenty minutes earlier.

The ticket asked four things: what distinguishes a dated measurement from a live pointer, where a
check would run, whether the honest answer is to fix the instruction rather than gate it, and whether
an already-published stale coordinate gets corrected.

Grilled 2026-09-12 to an empty frontier. **Nine rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.

## Measured before ruling, at `084152c`

Freshness gate `FRESH` at `084152c` before any reading. Every figure below was measured at that
commit against a harvest of the 60 open tracker records and their 467 comments, and against the
tracked tree. The tracker figures move whenever anybody comments; they are a dated measurement and
not a current property of the tracker.

**The naive gate catches almost nothing.** Of 357 coordinate occurrences in open tracker records, 355
name a file that resolves and **2 name a line beyond that file's end**. *Had the class been
line-numbers-pointing-past-EOF, that count would be most of 357; it is two, both the same coordinate
on one ticket.* A check asking *does line N exist* fires on 0.6% of the population. The defect is a
line that is present and says something else.

**The remedy is already the practice.** 314 of the 326 occurrences outside fenced blocks — **96%** —
carry a symbol name, a quoted span, a prose quotation or a quoted block in the same paragraph. What
is missing is not the content but a rule naming which of the two a reader resolves by.

**The population is invisible to the grader that owns tracker citations.** 347 of 357 occurrences are
bare prose rather than URLs, and `tracker_branch_scope` reads only URL and Markdown-link destinations.
Re-derived in-process against the live module:

```
_cited_main_paths("…/blob/main/tools/threshold_draft.py:109")   -> path 'tools/threshold_draft.py:109'  (unresolved)
_cited_main_paths("…/blob/main/tools/threshold_draft.py#L109")  -> path 'tools/threshold_draft.py'      (resolves)
_cited_main_paths("the call is at tools/threshold_draft.py:109") -> ()
```

*Had the module been able to see a bare coordinate, the third call would return a `CitedPath`; it
returns the empty tuple.* Two consequences: the colon-suffixed URL form is **already refused** as
`branch:unresolved-path`, by accident rather than by design, and the canonical `#L` fragment form —
used **twice** in the whole corpus — passes with the coordinate unread.

**And that module structurally cannot be widened to see it.** It reads through
`tracker_bodies.prose_outside_code`, which masks inline code; ADR 0139 ruling 5 requires the opposite
policy, *"It reads inline code spans, because both repaired instances live in one."* Re-derived:

```
prose_outside_code("use `tools/foo.py:12` here")    -> 'use                   here'
prose_outside_fences("use `tools/foo.py:12` here")  -> 'use `tools/foo.py:12` here'
```

**`docs/adr/` is the larger and more decayed population, and it is reachable.** 369 coordinates
outside fenced blocks across 187 records, 92% anchored, and **23 of the 369 name a file that no
longer resolves at all** — 6%, against effectively none in the tracker. Tracked Markdown outside
`docs/adr/` holds **zero**, which is ADR 0139 ruling 5's ratchet holding.

**A discriminator the thread proposed does not survive its own sample.** #837's sweep observed that
#987's three ADR-into-ADR citations still resolve while every `tools/*.py` citation had drifted, and
proposed *what the coordinate points into* as a cheaper key than record kind. Only **10** of the 369
`docs/adr/` coordinates point into another ADR, so the observation rests on about three instances.
The two other proposed keys fail outright: four repeat-sweeps that copied one coordinate forward
without re-measuring all carried base commits, and `ready-for-agent` covers 30 of 357 occurrences on
exactly **one** ticket.

**Commit messages carry 34 occurrences across 25 of the last 1500 commits.**

## Ruling 1. The coordinate is never the locator; the symbol or quoted span beside it is

A `path:NNN` in a record is a **coordinate**: a dated statement of where something stood. A reader
resolves by the **anchor** — the symbol name, quoted span, prose quotation or quoted block in the
same paragraph. Both terms enter `CONTEXT.md` with this record.

ADR 0048's dated-not-rewritten posture does **not** rescue this class, and its ruling 15 says so
first: *"never early, never self-healing, and dating it changes nothing."* That ruling is about a
path citation, which heals when the path lands. A coordinate heals never. So the surviving instruction
is ADR 0170's, which is the only one of the two in-tree precedents that tells a reader what to do:
*"the anchors are dated, not durable ... so a builder resolves a coordinate by the symbol beside it."*
ADR 0165 declares its coordinates dated and gives no resolution instruction; 0170's wording is the one
to copy.

**Considered and rejected: split by record kind**, the ticket's decision 1 as filed — a build spec's
coordinate is a live pointer, a sweep comment's is a dated fact. It needs a discriminator, all three
proposed keys are falsified above, and it would buy the strict treatment for a build-spec population
of one ticket.

## Ruling 2. The obligation is accompaniment, not a ban, and the written rule explains it

A coordinate may appear only beside an anchor. Refused, then accepted:

```
the coverage limb moved to `tools/differential_scan.py:1484`

`coverage_limbs.append(NO_DIFFERENTIAL_ENTRY)` is at `tools/differential_scan.py:1484`
```

**The claim the rule makes is narrow and is stated as such: accompaniment does not keep a coordinate
true. It converts a silent landing on the wrong line into a search that finds nothing.** A record on
this thread proves the limit — #948's body quotes a sentence with a coordinate, and
`grep -c "type the reply into the LMS" skills/discussion-reply/SKILL.md` returns **0**, because the
passage no longer exists in any form. The anchor does not recover it; it stops the reader mistaking a
plausible neighboring line for the rule.

**Considered and rejected: ban it, as tracked prose bans it.** ADR 0139 ruling 5 took a zero ratchet
because the population was already two. Here it is 326, and the ticket's own *what must not come out
of this* forbids a gate that fires on a dated sweep measurement — those are the passes that found the
class.

**Considered and rejected: a written convention alone.** `docs/agents/issue-tracker.md` contains
**zero** occurrences of `path:NNN` today, so the instruction genuinely does not exist and writing it
is the cheap half of the ticket's decision 3. It is not sufficient alone: [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s
*what a written instruction cannot do is fail* applies, and the 3% that already violate the rule are
the instances the thread found by hand rather than by any check.

## Ruling 3. The window is the paragraph or the block beneath, and the mention case fires

Measured against the live corpus:

| window | complies | violates |
| --- | ---: | ---: |
| same physical line, or the block beneath | 78% | 79 |
| same paragraph, or the block beneath | **96%** | **12** |

The line window fails on the commonest correct shape — a coordinate, a colon, and the quoted content
as its own block — and on a bulleted item whose symbol opens the bullet. The anchor vocabulary is a
backticked identifier, a backticked span, a prose quotation, or a fenced or quoted block immediately
beneath; **presence only, never resolution**, because resolution needs file contents at a stated
commit.

**The residue is declared and fires.** Eight of the twelve violations are on threads whose subject is
coordinate decay, where the sentence is about the number and there is no symbol to anchor to —
`spelling_scan`'s mention-versus-use distinction arriving uninvited for the fifth recorded time.

**Considered and rejected: exempt a paragraph carrying two or more coordinates**, which is the
decay-report shape. It is a shape guessed from eight instances, and it would exempt a build spec's
table of several coordinates in one paragraph, which is the worst case the ticket names. Refusing it
costs eight comments a rewording; closing it would be a matcher tuned on its own bug reports.

**One honesty note on the instrument.** The anchor detector credits any backticked identifier in the
paragraph, so 96% is a **ceiling on current compliance rather than a floor**. As a rule that
permissiveness is the point; as a measurement it flatters.

**A worked example of a refusal is unanchored by construction, and this record was graded against its
own rule and went red on exactly that.** The two examples above were written as blockquotes; the
refused one carries no anchor because carrying one is what would make it pass. They are fenced now,
which is the exemption ADR 0139 ruling 5 already provides and is what it is for. Any document
teaching this rule has to fence its counter-example, and that is the same shape as
[#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) — describing a rule breaking
the check for it — arriving inside the record that declares the mention case one paragraph above.

## Ruling 4. A new module, refusing at the hook and reporting at the workflow

`tools/tracker_coordinates.py`, one rule `coordinate:unanchored`. `tracker_publish_hook.analyze`
calls it and **denies**; `.github/workflows/tracker.yml` runs it on the changed record and
**reports after publication**. That is `tracker_bodies.py`'s arrangement exactly, and the workflow
half is not redundant: `tracker_publish_hook.NOT_REACHED` says the hook *"covers one of two
publishers"* — the GitHub web UI bypasses it entirely.

**It needs no tree read, no network and no file contents.** It is the only tracker grader whose whole
input is the record's own text, so it adds nothing to the hook's cost and cannot fail for an
environmental reason.

**Considered and rejected: widen `tracker_branch_scope`.** Its `NOT_REACHED` row *"citation
coordinates need file contents"* would survive untouched, since this rule never checks whether a
coordinate is correct — which also means [#1002](https://github.com/mshamblin5150-code/clinical-skills/issues/1002)'s
instruction not to reword that row is honoured either way. The cost is the reader: the module would
hold two Markdown readers with opposite inline-code policies, and ADR 0171 ruling 4 has already
declined converging that module's reader without a recorded escape.

## Ruling 5. One recognizer, two verdicts, and the reader moves to a shared home

`test_python_floor.PATH_COORDINATE_CEILING` and `prose_outside_fences` move to `prose_bind.py`, where
`prose_outside_code` already lives, and both the tracked-prose ratchet and this grader import them.
The same bytes are recognized as a coordinate on both sides of the tree.

**What is not shared is the verdict.** Tracked prose bans, the tracker requires an anchor, `docs/adr/`
requires an anchor from the cutoff forward. Sharing the recognizer is `reference_scan` importing
`docx_write.REFERENCE_HEADING`; sharing the verdict would forbid the asymmetry this whole ticket is
about.

**The move carries its declaration rather than resolving it.** ADR 0158 left `prose_outside_fences`
in a test module as *"a declared narrower reader"*, on the measurement that it and
`prose_outside_code` disagree on 404 of 476 tracked Markdown files. That disagreement is ADR 0139
ruling 5's policy and is not a defect to fix, so this is a relocation and not a convergence.

## Ruling 6. `docs/adr/` is graded, forward-only, and the cutoff is computed rather than promised

A `docs/adr/` record's coordinates are graded only when the record's own last-touching commit is at or
after the cutoff, derived from `git log -1 -- <path>` and stored nowhere. Editing a record for any
reason pulls it into the walk whole, so the exemption cannot silently grow and no baseline list is
kept. That is `tracker_filed_from.FILED_FROM_CUTOFF`'s constant applied to a file's last commit rather
than to a record's creation.

**Considered and rejected: retrofit the existing unanchored coordinates.** The cost is not the edits.
Retrofitting an anchor requires knowing what the coordinate pointed at when the record was ratified,
and a wrong guess writes a false sentence into a ratified record — ADR 0048 ruling 16's named failure,
*"Qualifying a typo writes a false sentence that permanently silences a real dead link"* — against
ADR 0131 ruling 6 and ADR 0182's 2026-09-11 correction, *"Nothing here licenses correcting a path, a
link, or any other dated citation in a ratified record."* The failure is asymmetric: a wrong retrofit
is permanent and silent, an unanchored coordinate is merely useless.

**Considered and rejected: tracker only**, matching the ticket's title. `docs/adr/` is the larger and
more decayed population, and unlike the tracker a repository test can already see it. The title
describes the half that was unreachable, not the scope of the answer.

## Ruling 7. A record-level declaration does not waive the anchor

ADR 0165, 0170, 0181 and 0184 each wrote a sentence declaring their coordinates dated. That sentence
is worth requiring and it **exempts nothing**: it says the number is not the locator, and an anchor
says what is. A record needs both. A sentence that waived every coordinate in its record would be an
off switch.

**No marker hatch is built.** The `<!-- unresolved-step-citations: N -->` shape with its
`EXEMPT_CEILING` is available in `test_skill_agreement.py` and stays on the shelf: that check had
three known-good exceptions to name, and this one has zero, ruling 3 having declared its only measured
residue and let it fire.

## Ruling 8. Nothing already published is repaired, and no harvest is built

The 314 stale-but-anchored coordinates need nothing — the anchor beside them still resolves. The 12
unanchored ones are comments, and `docs/agents/issue-tracker.md` says *"Do not rewrite or delete the
dated branch-state record after merge. A comment is evidence of what was true when written."* That
answers the ticket's decision 4: **no.**

**Considered and rejected: a `--harvest` mode**, on `tracker_filed_from`'s precedent. The disanalogy is
decisive: a missing Filed-from line **can** be added to a body, which is what that harvest is for. An
unanchored coordinate in a published comment has no repair ADR 0048 permits. A harvest would produce a
standing list nobody may act on, which reads as a backlog and is a monument.

The one actionable slice is a `ready-for-agent` body, which can be respec'd. That is 30 of 357
occurrences on a single ticket — a sentence in the respec instruction, not a mode.

## Ruling 9. Tracker surfaces only, and commit messages are out on a stated property

`tracker_publish_hook.PUBLISH_ROUTES` already covers issue create, comment, edit and close, pull
request create, comment, edit and review, and the `api` route, so the hook placement picks up issue
bodies, issue comments, pull request bodies, reviews and review comments at no extra cost.

**Commit messages are outside the walk**, and not on grounds of population size. **A commit message is
attached to a tree and an issue comment is not.** A coordinate in a commit message resolves exactly
and permanently — `git show <that commit>:tools/foo.py` — because the record and the tree it was
measured against are the same object. No other surface here has that property; a `Branch state:` block
*names* a commit, which is the nearest available thing and is exactly why it is a convention somebody
can forget.

## What the build verifies

- The recognizer and reader are one object each, imported by both the tracked-prose ratchet and the new grader, asserted by identity rather than by equal behavior.
- The paragraph window and the anchor vocabulary, driven by fixtures in both directions, with a mutant that removes the anchor going red.
- Refusal at the hook and report at the workflow, each driven through its real entry point rather than through the grader function.
- The `docs/adr/` cutoff, driven by a throwaway repository whose record is committed on both sides of the cutoff date.
- `docs/agents/issue-tracker.md`, `CLAUDE.md` and the module docstring bound by `prose_bind`'s `NAMING` mode against `tracker_coordinates.DECLARED_LIMITS`, so no surface copies a row.
- The grader's disposition in `run_grader`: it joins `REFUSED` **with its own written reason**, not by inheriting `tracker_bodies`'s.
- Exit status 0 clean, 1 for an unanchored coordinate, 2 for every way of not having scanned, with the unreadable-body limb reaching `tracker_publish_hook`'s existing `UNSCANNED_REFUSAL`.
- Output safe to paste: the rule, the record URL and the coordinate itself, which is a repository path and an integer. No `--show`.

## What this record does not settle

- **Whether an anchor resolves.** Presence only. A symbol that no longer exists satisfies the rule, and that is the limit `tracker_branch_scope.NOT_REACHED` already declares for the coordinate itself.
- **The mention case.** A record reporting that a coordinate moved is refused. Declared in ruling 3, measured at 12 occurrences across 8 records.
- **The commit-message exemption's own edge.** Ruling 9 rests on a commit message being attached to the tree it measured. A commit message quoting a coordinate for a file it does not touch is **not** self-anchoring, and nothing distinguishes those.
- **When a `docs/adr/` record is pulled in.** Ruling 6 grades a record edited for any reason, including an unrelated typo, so the archaeology arrives at a moment nobody chose. That is the right direction to fail and it is a cost.
- **Whether the anchor an author wrote is the right one.** A backticked identifier unrelated to the coordinate satisfies the rule, which is what keeps the false-alarm rate near zero and what makes the 96% a ceiling.
- **The tracker figures.** Every count above is dated to `084152c` and moves whenever anybody comments.
