# Project context is retrieved into a confirmed record before drafting

**Measured at:** 9c70aa19551c6c0303d37a2a2530e8e18a03da9b

[#1395](https://github.com/mshamblin5150-code/clinical-skills/issues/1395) was filed from the
after-action review of a course-assignment run, 2026-09-22: a talk narrowed the founder's motivation
for the clinician's own project to one narrative, though his broader account already existed in
project memory and in named planning material, and reading that material later materially changed
the accepted talk. Grilled against `main`, where the freshness gate read `FRESH`; the clinician ruled
every point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**No bound skill reads project context before drafting.** Across the five coursework skills, no step
names the memory index, a project, or a planning location before the first prose. The only reader of
the memory index in the tree is the after-action review, and it runs after submission — so the one
instrument that can tell *we never knew this* from *we knew this and did not look* fires only once
the draft is handed in.

**The reader that ran after the draft had an exemption shaped exactly like the failure.** All five
skills already spawn a heading read, on the shared shape in the sourcing reference, and that shape
says:

> The clinician's own reasoning and experience are counted but need no pair.

A founder's motivation is the clinician's own experience, so the narrowed account was counted and
checked against nothing.

**The signed bar is transcription.** [ADR 0270](0270-the-canonical-voice-model-is-resolved-by-one-owner-and-identity-is-the-graded-row.md)
ruling 6 holds that every bar field is transcribed from the live assignment page or syllabus and that
the clinician's signature certifies the transcription. A project name, a one-off search direction and
a waiver are none of those. The grilling first placed all three in the bar and moved them when that
record was read; the scope was widened in the same session for the reason the move dissolved.

**A captured-thought service is one of the places the clinician directs a search.** It answered from
this session through its MCP server, reporting a corpus of a little under eleven thousand items drawn
from mail, agent memory and personal records. Its route in the other harness is a URL of 141
characters, not published here. It is a semantic search, so it can report its corpus size, the
queries run and what came back, and never what ranked below its cutoff.
[ADR 0270](0270-the-canonical-voice-model-is-resolved-by-one-owner-and-identity-is-the-graded-row.md)
measured the same store carrying positions that were later reversed, with nothing marking them
superseded.

## Ruling 1 — the obligation is declared by the clinician and never inferred by the run

Every bound run writes a **project context record** before its first prose. Its header is the
clinician's declaration, shown to him and confirmed the way the bar is: either the project the work
concerns, or `none` with a reason. **A missing record is a finding**, so silence can never read as
*no project*.

The run deciding relevance for itself was refused: that is the judgment that failed on the run this
ticket came from. Searching on every run whatever the assignment was refused: it pays for a search
where nothing is at stake and grades nothing useful there. The bar was refused as the home, on ADR
0270 ruling 6's contract, rather than read an exception into it.

## Ruling 2 — the five coursework skills are bound and the note skill is not

`course-assignment`, `discussion-post`, `practicum-case-study`, `discussion-reply` and
`peer-critique` are bound — the same five ADR 0270 binds, for its reasons. `clinical-note` is out on
that record's ruling.

The grilling first held scope at the one skill that failed, on the reasoning that binding the others
added a bar field for the clinician to sign on every discussion post. Ruling 1 moved the declaration
out of the bar, which dissolved that cost. What remained argued for five: every narrower scope makes
the run's relevance judgment one level up, per skill, and a discussion post on rural access to care
is the same trap as the talk. The price is one confirmed `none` on a critique of a classmate's case.

## Ruling 3 — a project registry names what is owed, and one resolver owns its location

A **project registry** in the account's `scratch/` names each of the clinician's projects and, for
each, its planning locations and services. It states the **memory index once**, owed on every run
whose declaration is not `none`, whatever the project. A literal shape:

```
MEMORY-INDEX: <absolute path of the memory index>

PROJECT: <name>
  LOCATION: <absolute path>
  SERVICE: <MCP server name>
```

`repo_root` owns the registry's location with **one resolver one artifact wide**, on ADR 0270 ruling
5's terms — the account-state owner already holds that record's resolver, and a general account-file
resolver stays refused. The registry is not a section of the portal profile, whose subject is the
portal.

**The memory index path is stated, never derived.** Deriving it from one harness's project-slug
convention would owe a file the other harness does not keep; stating it makes one fact live in one
place.

A declared project the registry does not hold **stops the run with a question**, as an unmapped
preceptor does. A memory entry pointing somewhere outside the registry is recorded as a lead and is
not owed; the registry grows only on the clinician's word, never because a run wrote to it.

## Ruling 4 — one-off directions and waivers live in the confirmed header

A direction the clinician gives during a run — search a cloud-synced folder, search the
captured-thought service — is written into the record's header and confirmed with it, and it is owed
exactly as a registry entry is:

```
PROJECT-CONTEXT: <name>
PROJECT-SEARCH: <location or service> - "<terms>"
PROJECT-WAIVE: <location or service> - <what failed and when>; proceed without, per the clinician
CONFIRMED: <date>
```

A direction given after confirmation amends the header and is confirmed again before drafting. One
that recurs on every run for a project moves into the registry on the clinician's word. Recording a
direction only in the run's own entries was refused: whether it was obeyed would rest on the run
remembering it was given.

## Ruling 5 — each owed place has one entry, and a miss states where it looked

Every owed location or service has exactly one entry, in one of four states: `read`, `searched`,
`unreadable`, `absent`.

A **searched path** states its root, its terms, how many files were examined and how many could not
be read, and what was opened. A **service** states its corpus size, the queries, the threshold and
limit, the hit count per query, and the opened items **by identifier only** — never their text, which
would copy personal records into the run directory for no reader that needs them. A service is named
by its server name and **never by URL**, which can carry a credential.

`OPENED: none` is how a miss is written: these terms over this corpus found nothing. It is never a
settled negative about the project, on the sourcing reference's rule that a search reports the corpus
it read.

## Ruling 6 — an unreachable owed place blocks the gate until the clinician waives it

An `unreadable` or `absent` owed entry fails the pre-draft gate until a `PROJECT-WAIVE:` line in the
confirmed header names that place. The entry keeps its failed state and says what failed, and the
report prints how many owed places were waived, so a waived run never reads as complete. Refusing to
proceed until every place is reachable was refused: a service outage would block a deadline.

## Ruling 7 — the gate function writes the fingerprint

Each opened item carries a SHA-256 — a file's bytes, or a thought's returned text hashed at retrieval
and never stored — and one **context digest** over the sorted location, item and hash triples is the
retrieval result the draft is held to. The hashes and the digest are **written by the gate function,
not by the agent**, on ADR 0270 ruling 6's machine-written precedent.

## Ruling 8 — a pre-draft gate, with the ordering declared rather than claimed

The first prose of a bound run starts only after the project-context gate exits 0. No file can prove
that the retrieval preceded the draft — a record written afterwards reads like an honest one — so the
ordering is a **declared limit**, not a graded claim. The gate is what would have stopped the failing
run, because drafting could not have begun with the record missing.

File modification times were refused as an instrument a copy or a touch rewrites. Grading the order
from the session transcript at the after-action review is real evidence and is **filed separately**:
it lands after submission and makes that review a second grader of each skill, which is a decision
of its own.

## Ruling 9 — each completion grader declares the same row, and drift is a coverage state

The five completion graders each declare one shared expected row, on ADR 0270 ruling 7's precedent,
and the row is owned by the module that owns the record.

At completion the file items are hashed again. **An item that moved since retrieval is reported with
an exit-2 coverage state**, on ADR 0270 ruling 4's terms, and a finding still wins over it. Reporting
drift without grading it was the grilling's first answer and was reversed: a line that cannot fail is
a written instruction, and an exit 2 already says *true about what was read, not about what exists
now* without calling the run wrong. The clinician edits his planning material as a project moves, so
an honest run can end in a 2; it never ends in a 1 for that alone. Thought items are not hashed again,
because the grader opens no service; that is declared.

## Ruling 10 — the heading read decides whether the draft used the context

The shared heading-read record gains two fields on every bound run:

```
CONTEXT-DIGEST: <must equal the project context record's digest>
CONTEXT-VERDICT: agrees | narrows | contradicts | sources-conflict - <location>, <what differs>
```

The reader opens the recorded items itself and never a summary of them. The limb matters most for
the sentences the draft counts as the clinician's own, which the heading read otherwise passes with
no pair. A verdict other than `agrees` is a finding, cleared by revising the draft or by the
clinician's ruling. On a `none` run both fields read `none`. The rows live once in the shared
heading-read module and reach all five graders through it.

The course-assignment adversarial reader alone was refused because it would leave four bound skills
with a record and no check of use; a new reader in all five was refused because the heading read
already exists in all five and is where the exemption that let the failure through lives.

**Retrieved items stay pointers.** A memory entry, a planning file or a captured thought is evidence
of what the clinician has said about his project and is never cited; it may constrain what the draft
says in his voice about himself and may not carry a sourced sentence.

## Ruling 11 — the reader never resolves a disagreement between sources

When retrieved sources disagree with each other — the memory index stating one motive and a captured
thought another — the verdict is `sources-conflict`, naming both. It is a finding, cleared only by the
clinician's ruling, and his ruling lands as a memory write so the next run finds it settled.

Fixed precedence was refused because it would silently bury the one case where current thinking
lives only in a new planning file. Newest-wins was refused on ADR 0270's measurement: a store whose
items carry no superseded marker makes *newest* meaningless. The reader's judgment was refused as the
judgment that failed.

## Ruling 12 — one limits object carries the ceiling

The ceiling is declared in **one object**, owned by the module that owns the row and named by the
five graders and by `CLAUDE.md`, copying no row, on ADR 0270 ruling 10's terms. Its known members:
the draft following the retrieval is unobservable; whether an `agrees` is true is a reading; a
semantic search cannot show what ranked below its cutoff; thought items cannot be hashed again at
completion; and a run that records a true retrieval and then drafts from its own narrower account is
caught only as far as the heading read catches it.

## What this record does not settle

**Whether the draft sounds like its clinician.** That is the voice model's subject and
[#1394](https://github.com/mshamblin5150-code/clinical-skills/issues/1394)'s; this record governs
what the draft says about the project, not how it says it.

**Whether the registry's contents are complete.** A project the clinician never registered, or a
location he never named, is owed by nothing. The registry is his statement and the mechanism holds
runs to it.

**The captured-thought store's superseded positions.** Ruling 11 routes a conflict to the clinician
when one surfaces; nothing here marks, retires or reconciles the store.
