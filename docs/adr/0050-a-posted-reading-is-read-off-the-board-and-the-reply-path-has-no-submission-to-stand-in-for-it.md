# A posted reading is read off the board and the reply path has no submission to stand in for it

[#521](https://github.com/mshamblin5150-code/clinical-skills/issues/521) was filed off the observation
that `skills/discussion-reply/SKILL.md:186` instructs a run to *"reread the posted board version"* and
nothing writes down what it saw. The reply is typed into the LMS by hand, so no renderer sits between
the artifact and the board, and the artifact is a statement of **intent** that nothing corroborates.
The ticket offered three options — record the reread, enrich the capture, or declare the gap — and
said they were not exclusive.

Grilled 2026-08-27 against `d3c9f6a`. **Eleven decisions, ruled by the clinician on that date.**
Nothing is built here; this is the record the build reads.

## Measured before ruling, at `d3c9f6a`

- **The ticket's headline measurement re-derives and is wider than it was filed.** Across both live
  discussion run keys, of **13** captured classmate posts: **0** carry bold, **0** carry italics,
  **0** carry a Markdown heading, **0** carry a bullet. The capture strips every inline formatting
  mark, not only the bold the ticket reasoned from. The two `board-*.md` files carry 4 headings
  each; those are the capture-writer's own structure.
- **No board capture in the tree contains any posted reply.** Each run holds exactly one
  `board-<date>.md` and it predates the posting. Longest shared character run between a board and a
  reply artifact in the same run: **40**, **14** and **10** characters, against response lengths of
  **1,876**, **1,827** and **4,189**. Option 2 as filed asks about the fidelity of an artifact that
  does not cover the reply at any fidelity.
- **`post.md` is already the artifact this ticket wants, on the other path.** The clinician's own
  initial-post record carries `AUTHOR`, `REPLIES`, `POST-URL` and `POSTED`. The locator and the
  timestamp do not exist before submission, so the post path already goes back to the board and
  writes down what it found. What it never writes down is what the reread **concluded**.
- **The locator is a Canvas deep link and the roster is full of them.** All 13 captures carry a
  non-empty `POST-URL`, 13 distinct values, one host. **12 of 13** carry `?entry_id=N`; the
  thirteenth is a bare topic URL.
- **The capture records no nested entry.** The roster's `REPLIES:` fields count **12** nested
  replies across the twelve posts, and **zero** nested `entry_id`s were captured. The instrument
  writes one URL per top-level post, which is why no artifact in the tree could settle the nesting
  question.
- **Both skills share one run directory.** `discussion-post` and `discussion-reply` each derive
  `<course>-<module>-discussion` and write into it, per [ADR 0005](0005-a-run-is-keyed-to-the-board.md).
  `board-<date>.md`, `claims.md` and `posts/` are written by both.
- **A reply is a graded artifact with no submission.** `skills/discussion-reply/SKILL.md` mentions
  `output/` exactly once, at `:23`, and it is a prohibition. `discussion-post` mentions it seven
  times and writes two files there. The post path's `.docx` is a faithful record of what went into
  the paste box; the reply path has no counterpart, so nothing in the tree is the thing the course
  marks.
- **The reread asymmetry between the siblings.** `discussion-post:262` names what its reread owns —
  *lost headings, broken paragraphs, missing references, and any change introduced by paste* — and
  its Completion line reports *the posted reread*. `discussion-reply`'s Completion reports the
  addressees, the grader exits and the amplification counts, and nothing about the reread.
- **`discussion_reply_scan` has no declared-limits object.** `discussion_post_scan.NOT_REACHED`
  holds five rows; the reply scanner holds one ceiling, in prose, in its docstring. No open ticket
  owns the reply scanner's limits — [#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535)
  owns `research_ledger`'s and [#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550)
  owns `threshold_sheet`'s.
- **A locator inside a reply artifact fires the numeric-trace row.** `_split_reply` puts everything
  before the References heading into `body`, and `_numeric_values` walks that whole body.
  `NUMBER.findall` over a Canvas entry URL returns **three** matches — the course id, the topic id
  and the entry id.

## Measured from the Canvas source, because the browser was unreachable

The nesting question was re-derived from `instructure/canvas-lms` rather than from the board.

- `ui/features/discussion_topics_post/react/components/ThreadActions/ThreadActions.tsx` — the kebab
  menu on an individual entry — builds its Copy Link as
  `` `${window.location.origin}/courses/${ENV.course_id}/discussion_topics/${ENV.discussion_topic_id}?entry_id=${props.permalinkId}` ``,
  rendered when `permalinkId` is present and `ENV.FEATURES.discussion_permalink` is on.
- `ui/features/discussion_topics_post/react/containers/SplitScreenThreadsContainer/SplitScreenThreadsContainer.tsx`
  renders that menu inside its `.map()` over subentries and passes `permalinkId={props.discussionEntry._id}`
  — each nested reply's **own** id, not its parent's.
- **The join settles the feature flag without asking Canvas.** That template is byte-for-byte the
  shape measured in the run directory, so those twelve URLs could only have come from this menu
  item, so `discussion_permalink` is on for this instance. The same component renders top-level and
  nested entries.

**Conclusion: a nested reply has its own copyable `?entry_id=` deep link and this instance exposes
it.** The residue is that `master` was read and the containers passing `permalinkId` are three —
`DiscussionThreadContainer`, `SplitScreenParent`, `SplitScreenThreadsContainer`. A view rendering
nested replies through some other container would not offer the menu. The first run settles it.

**Why the browser was unreachable, recorded so it is not re-attempted blind.** The Claude in Chrome
extension and its native messaging host are registered on the machine and Chrome was running, but
the session was started without `--chrome`, which is a session-start flag, and Chrome carried no
`--remote-debugging-port`, so no DevTools route existed either. `ToolSearch` returns no browser tool
under any name. Two attempts to discover CDP client tooling were denied by the harness classifier.
**The re-derivation above is what replaced the measurement, and it is stronger** — it establishes the
mechanism rather than one instance of it.

## Ruled 2026-08-27

### The record

1. **The reread gets a recorded artifact, not a reported one.** Three tiers were available:
   *reported* to the clinician at Completion, which is what `discussion-post` already does;
   *recorded* into the run directory, gradeable; and *captured*, holding the posted text back.
   **Recorded.** Reported is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s
   *what a written instruction cannot do is fail*, stated twice — the measurement above is what an
   unrecordable reread bought: three posted replies, zero board-side bytes. Captured is worse than
   expensive: the instrument that would write it is measured stripping bold, italics, headings and
   bullets from thirteen posts, so **a captured reply cannot carry the formatting evidence this
   ticket was filed over**, and a diff against a plain-text capture would fire on every legitimate
   run, which is what the ticket forbids by name. Capture is unavailable until a richer capture
   format exists; nothing here blocks one.

2. **The record's un-fakeable half is the board's own locator, and substance and coverage ride
   beside it.** A substance test reaches a bare keyword and a coverage test reaches a skipped reply;
   **neither reaches a run that skipped the reread and wrote one plausible sentence.** [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md)'s
   transferable half is that the row must reach a shape the degenerate case cannot produce, and an
   `entry_id` does not exist until the reply is submitted and is readable in exactly one place. All
   three rows land; the locator carries the weight.

3. **A recorded divergence obligates nothing automatically.** The record says what the board says;
   the artifact keeps saying what was drafted. Repairing the **board** is available on the
   clinician's word per instance and is never a rule the skill makes, because it is a live edit to
   submitted coursework. Repairing the **artifact** is refused: `discussion_reply_scan` has already
   graded that file, so editing it afterwards leaves the artifact that passed and the artifact in
   the record as different files with nothing recording which was graded. It also inverts
   [ADR 0036](0036-a-references-label-is-a-per-pipeline-source-spelling-for-one-rendered-outcome.md)
   ruling 5, which declined to correct four artifacts because *the edit would assert a fact rather
   than repair one*; here the edit would repair a fact and destroy the graded one.

4. **The record is `reread.md`, one per run directory, beside `claims.md`.** One `## REREAD:`
   record per posted entry, carrying `POST-URL`, `POSTED`, `READ` and `VERDICT`. **`POST-URL` and
   `POSTED` are `post.md`'s own field names for exactly these two facts** and are spelled the same
   way rather than renamed; `READ` is the reread's own date and is the one new field. `VERDICT` is
   `checks_ledger.py`'s vocabulary — two words, and a third is a finding because the field gates the
   row below it.

   A sidecar directory mirroring `posts/` was refused: `posts/` is the classmate roster the grader
   joins `AUTHOR:` against, the house pattern for the clinician's own entry is already a top-level
   file, and a second directory whose only occupant is him invites the next reader to join it into
   the roster. Appending the header to `response-<name>.md` was refused on the measurement above —
   three false `UNTRACED_NUMBER` findings per reply, repairable only by excluding the locator from
   the numeric walk, which is widening an instrument to accommodate a new field.

5. **Every disposition owes substance, `matches` included.** A bare `VERDICT: matches` is the
   degenerate case surviving the substance row. ADR 0042 ruling 4's ground transfers unchanged:
   exempting the easy disposition is where a run under time pressure goes.
   `checks_ledger.SUBSTANTIATED_CLEAN` is the precedent for making a clean verdict say what it
   walked on.

6. **`reread.md` covers every entry the run posted, not the replies only.** `post.md` when present,
   plus every `response-*.md`. Each grader grades only its own artifacts' records —
   `discussion_post_scan` the initial post's, `discussion_reply_scan` the replies' — and each
   declares in its limits that it does not grade the other's. A file named for the whole reading,
   sitting in a directory shared by both skills, covering two of three posted entries is a partial
   read presented as complete, in a repository whose extractor-coverage rule exists for that, and
   **#521's own body was corrected once this month for presenting a floor as a census.** The post
   path is also the cheaper half: its locator and timestamp are already captured, so it needs only
   the `VERDICT` line.

   **The parse belongs in `discussion_artifact.py`** beside the shapes both scanners already import,
   not copied into each. That is the coupling that already exists rather than a new one.

### The rows

7. **Five kinds, attributed `#521`.** `missing-posted-reading` — a posted entry with no record, the
   ruling-6 join. `unknown-verdict` — a `VERDICT` outside the two-word vocabulary, **a finding and
   not exit 2**, on `UNKNOWN_STATUS`'s and `UNKNOWN_REFUTATION`'s stated ground that the field gates
   the row below it. `bare-verdict` — no substance past the keyword, on `BARE_REFUTATION`'s test,
   binding `matches` as well as `diverges` per ruling 5. `unlocated-reading` — no `POST-URL`, or one
   carrying no `entry_id`. `borrowed-locator` — an `entry_id` already captured in this run.

8. **`POST-URL` takes no escape sentence.** ADR 0042 ruling 4 already priced one: blessing it
   *rebuilds the hatch — one sentence, satisfying every substance test, available verbatim to the
   self-clearer.* A run that skipped the reread would write `unavailable -> this instance does not
   expose permalinks` and pass forever, and the field's whole value is being the one thing a run
   cannot produce from its chair. Resting the weight on `POSTED` instead was refused because a
   timestamp is **guessable** — a run that posted at 14:30 and skipped the reread can write 14:32
   and be right — where an entry id is a database key with no plausible guess. `POSTED` stays
   required and carries none of the weight.

9. **`borrowed-locator` exists because the tree already holds the forgery.** The laziest way to
   fill `POST-URL` without opening the board is to copy a URL out of `posts/`, and all thirteen are
   on disk. Two limbs: a reply's `entry_id` may equal no classmate's and no other record's, and the
   initial post's record **must** equal `post.md`'s, which is already on file. Building the
   un-fakeable field without this leaves the one available forgery unguarded, for five lines.

10. **An absent `reread.md` is exit 1 with findings, never exit 2.** Every existing `SourceError` in
    that module is something the other rows need in order to run; the six existing rows run
    perfectly well with no reread record in sight. Returning 2 would suppress real
    `UNTRACED_NUMBER`, `RESPENT_SOURCE` and `UNRESOLVED_CITATION` findings — **the exact inversion
    `research_ledger` shipped and `/code-review` caught**, where the 2 returned at the branch before
    `survey` ran and a ledger with real findings reported *did not scan*. The population is known
    independently from the files on disk, so *zero records for three posted entries* is a counted
    result rather than an absence of one; `filled_vitals_census` exits 2 in its analogous case
    because there the denominator itself is missing. An **unreadable** `reread.md` stays exit 2.

### Where it lands

11. **The declared-limits object is built here rather than deferred to a sibling ticket.**
    `discussion_reply_scan` gains `NOT_REACHED`, carrying its existing roster-coverage ceiling and
    the new one, with this file and the module docstring pointing at it and copying no row, and a
    test binding both directions — [ADR 0047](0047-a-corpus-document-s-stated-citation-is-read-off-its-own-page-and-a-link-is-not-one.md)
    ruling 12's arrangement, on [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s
    ground that a prose edit to a limit fails nothing.

    **ADR 0042 ruling 9's objection does not survive the transfer, and the reason is specific to
    this module.** It was made about `research_ledger`, which holds five prose limits, so an object
    with one row genuinely would have been a numerator with no denominator. This scanner holds
    **one** prose ceiling, so the object is populated with everything the module currently claims.
    And ruling 6 puts `discussion_post_scan` in this change, which **already has `NOT_REACHED`** —
    so deferring would put the same claim about the same file into a checked object on one side and
    unchecked prose on the other, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
    verbatim.

12. **The four entries already on disk get a late reread, not a backfill and not four red rows.**
    Two replies in `nur5042-m2-discussion`, one in `nur5144-m1-discussion`, one initial post. Those
    boards are still live, so the records are written now with a truthful `READ:` date, a `VERDICT`
    that is a real reading, and a `POST-URL` read off the board rather than recalled. **Backfilling
    is refused** — writing `VERDICT: matches` against a reply posted on 2026-08-23 asserts that a
    reread happened and agreed, which nobody recorded, and that is ADR 0036 ruling 5's ground
    exactly.

    **ADR 0042 ruling 10's hard cutover does not transfer**, and the difference is why. Its ledgers
    were unrepairable: the declared difference it wanted had to have been observed at refutation
    time and that moment was gone. Here the observation is still available. A hard cutover would
    choose four failures over a reading that can actually be taken, which is the opposite of what
    ruling 10 protected.

13. **The glossary gains one term, `Posted reading`, filed in `### Artifacts` immediately after
    `Submission`.** [ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)
    rules that a term is filed with the term it is defined against and section coherence loses to
    that, and this term is defined by contrast with `Submission`: the post path has both, the reply
    path has only this. **`Reread record` was refused as the name** — it names the action, and the
    action is what already exists and produces nothing, so calling the new artifact by the old
    instruction's word invites the next reader to think the instruction was already the record.
    `reread` stays in the `_Avoid_` list because the skills keep saying it for the act.

    **A second term for the locator was refused as over-coining.** It is a field of the posted
    reading; nothing else joins to it and nothing else grades it. When something does, it earns a
    name.

## What must not come out of this

**No grader that fetches the board and diffs it against the artifact.** #521's own prohibition. The
board carries other people's posts, the reply is one nested comment in a page that keeps changing,
and a diff of rendered LMS text against Markdown fires on every legitimate run.

**No escape sentence on `POST-URL`.** Ruling 8. The next session will find the hard row inconvenient
on some instance and reach for one; the answer is that a person rules on it, not a sentence written
today.

**No freshness join on `POSTED`.** The board's clock, the run's dates and the machine's clock are
three different things, and a late reread legitimately carries a `READ` days after `POSTED` — three
of the four founding records will. A rule there fires on the honest case, which is
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect, recorded in this
repository five times already.

**Do not key any row on wording.** `matches` and `diverges` are a declared vocabulary; what a
divergence *says* is prose and is a reading.

**Do not read a clean `reread.md` as a checked post.** It establishes that a reading was recorded
and that its locator could only have come from the board. It does not establish that the reading was
careful, or that the reader compared anything.

## Declared limits

`NOT_REACHED` is the object; this record names its subject and copies no row. The subject is that a
posted reading establishes **that a reading was recorded and located**, never that the board says
what the record says. No row opens the board, compares any text, or reaches a fabricated
`entry_id` that collides with nothing — ADR 0042 ruling 1 accepted that class outright, and ruling 9
narrows it from *a value sitting one file away* to *an integer somebody had to invent*.

Ruling 12's late reread carries a limit of its own: it cannot distinguish a divergence introduced by
hand-typing from one introduced by a later edit to the board, and says nothing about the state at the
moment of posting. That applies to those four records and to no later one.

Ruling 8 couples `unlocated-reading` to a Canvas feature flag this repository does not control. If
`discussion_permalink` is turned off, every run fails until somebody rules on it. That is deliberate:
it is a decision about evidence and it should reach a person rather than be pre-absolved.

## Consequences

The four entries on disk fail with named findings until ruling 12's late reread is done, and
repairing them is the work rather than an inconvenience — ADR 0042 ruling 10's *the failures are the
mechanism working on its own founding instance*, with the difference that these are repairable.

`reread.md` is read by two graders, so its parse lives in `discussion_artifact.py` and a change to it
moves both. That is the existing coupling, not a new one.

#521's option 2 — should the capture preserve formatting — is **untouched and still open**. Nothing
here makes it cheaper or dearer; ruling 1 records only that capture cannot be the mechanism while the
capture instrument is measured to strip every mark a reread would be checking.
