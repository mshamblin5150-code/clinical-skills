# An owned asset is registered by the clinician and a purchase it already covers is a context finding

**Measured at:** ab5fb84924475f9ed161233f6cb36bb2e2b66cb0

[#1561](https://github.com/mshamblin5150-code/clinical-skills/issues/1561) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 11) on 2026-10-04. The run drafted
a change proposal that recommended renting a commercial scheduling product. The clinician then
pointed out that he already holds what he needs to build the same capability: a messaging account
with a toll-free number, a verified email domain, and a delivery app he shipped for an earlier course
project. The recommendation was redesigned around what he owns. Project-context retrieval had opened
his practice-planning material, but nothing asked which of his assets bear on the proposed change.
Grilled 2026-10-12 against `main`, where the freshness gate read `FRESH`; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The ticket's trigger is the judgment ADR 0272 refused.** The proposed text asks the run to raise
the asset question "when the assignment proposes, compares, or recommends a tool, vendor, product, or
service." That leaves the run to decide whether the question applies.
[ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md) ruling 1
refused exactly that judgment, because it is the one that failed on the run that ticket came from.

**The assets are written down, and nothing owes them.** After the Module 11 run, an agent memory
entry recorded the clinician's build-over-rent preference and his assets as of 2026-10-04. The memory
index is owed on every declared-project run, but the entries it points to are not. A run can satisfy
the gate without ever opening the asset entry.

**The registry cannot hold an asset today.** `project_context.read_registry` accepts `MEMORY-INDEX`,
`PROJECT`, `LOCATION`, and `SERVICE` lines and raises `unrecognized project registry line` on anything
else. An `ASSET:` line written to the registry before the parser accepts it breaks the project-context
gate for every coursework run.

**The go-ahead has no carrier for the ticket's "finding."** The tracker sweep that closed #1501's
grilling noted that [ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md)
gives the go-ahead a numbered list of reader remarks, and asked whether this is one. In `CONTEXT.md`
a finding is a graded defect that sets a status. The heading reader's existing `CONTEXT-VERDICT`
already answers whether a draft's statements about the clinician and his project agree with the
opened project-context items, and any answer other than `agrees` is a finding.

## Ruling 1 — owned assets live in the project registry, and the confirmed header shows them

Each project in the **Project registry** may carry `ASSET:` lines, one per **Owned asset**. The
registry gains them only on the clinician's word, as it gains every other line. The project-context
header that the clinician confirms before drafting shows every asset registered for the declared
project. Confirming that header therefore also confirms that the list is current. An asset he names
at confirmation is written to the registry and to the header before the gate runs. A run that
declares a project must carry that project's assets into its record; a `none` run carries none.

Asking on each run, when the run judges that the assignment recommends a tool or vendor, was declined
because it is the run's relevance judgment that ADR 0272 ruling 1 refused. A registry list without
the confirmation step was declined because it goes stale the first time the clinician ships something
and forgets to register it.

## Ruling 2 — the five coursework skills are bound

`course-assignment`, `discussion-post`, `practicum-case-study`, `discussion-reply`, and
`peer-critique` are bound, the five ADR 0272 ruling 2 binds. A run whose declaration is `none`, which
is how most replies and critiques run, shows and owes no assets.

Binding `course-assignment` alone was declined. The registry, the confirmed header, and the heading
reader's context check are already shared, so a single-skill scope would need a skill-specific
branch in each. A discussion post that recommends renting something the clinician owns would also go
unchecked, which is the Module 11 failure on another board.

## Ruling 3 — a purchase a listed asset already covers is a context finding

A draft sentence recommending that the clinician or his project buy, rent, or subscribe to something
a listed asset already provides is `CONTEXT-VERDICT: narrows`, unless the draft states why the owned
asset falls short. The Module 11 text-message case is the model of a stated reason: his number cannot
carry patient texts until a HIPAA-eligible agreement is priced and signed. Like every verdict other
than `agrees`, it is a finding that blocks the go-ahead until the draft is revised or the clinician
rules.

This answers the sweep's question: it is a finding, not a **Reader remark**, because comparing the
draft with an opened project-context item is the question the heading reader is already asked.
Filing it as a remark was declined because a reader that skipped the comparison would then have no
verdict depending on it. A separate asset-verdict field was declined because it would add a field and
a grader row in five skills to say what `CONTEXT-VERDICT` already says.

## Ruling 4 — an unlisted asset is a declared limit, not a second instrument

A purchase recommendation that no listed asset covers needs nothing beyond the confirmation in
ruling 1. An asset the clinician never registers, and does not name at confirmation, is owed by
nothing. That is declared in the project-context limits object, beside ADR 0272's statement that the
registry's completeness is the clinician's own.

Listing every purchase recommendation at the go-ahead was declined. It would add a record line and a
grader row in five skills for a gap that opens only when the clinician forgets at confirmation, and it
would still depend on the reader noticing every purchase sentence. If a forgotten asset gets through
after this lands, that is the evidence for filing it. Asking the clinician before drafting whenever
the run plans to recommend a purchase was declined as the run's relevance judgment again.

## Ruling 5 — the existing memory entry keeps the preference and points to the registry

The asset list in the agent memory entry moves to the registry. The clinician's approval in this
session is his word for the first Axion `ASSET:` lines, copied from that list: his own toll-free
number (his, not the clinic's; verification in progress; not yet wired to any app), the verified
practice email domain, the staff-schedule app with its delivery outbox, and Google Workspace in the
phase-one budget. He checks those lines at the first Axion run's confirmation. The memory entry keeps
the build-over-rent preference, which guides sessions outside the coursework skills, and points to
the registry for what he owns.

Keeping both copies was declined because they drift the next time an asset changes, such as the
number's verification finishing. Moving the preference into the registry was declined because the
preference is not an asset and a registry line cannot carry a working habit into other sessions.

## Build checklist

- `tools/project_context.py`: `read_registry` accepts `ASSET: <description>` under a `PROJECT:`,
  refuses an empty or duplicated asset, and keeps assets on the project. The gate requires the
  confirmed header to carry one line per registered asset of the declared project, refuses a missing
  one, and binds those lines into the context digest as it binds the `OWN-SUBMISSION`,
  `CASE-MATERIAL`, and `CASE-RESEARCH` lines. A `none` run carries no asset lines. The limits object
  gains ruling 4's limit.
- The registry seed waits for that parser. Writing an `ASSET:` line first makes every coursework
  gate exit 2 on `unrecognized project registry line`.
- `skills/_shared/reference/sourcing.md`: the header shape gains the asset line; the confirmation
  paragraph says the shown assets are confirmed current and a named asset goes to the registry and
  the header before the gate runs; the draft-order rule and the heading reader's brief gain ruling
  3's sentence.
- The project-declaration steps of the five bound skills: show the declared project's assets with
  the header being confirmed.
- The registry and the memory entry under ruling 5, once the parser accepts asset lines.
- Tests that drive the asset refusals through `project_context.py`'s public command, and a test that
  the shared reference states ruling 3's rule.

## What this record does not reach

- **Whether the reader judges "provides" correctly.** Whether an asset covers a recommended purchase
  is a reading, and a reader can miss it.
- **An asset never registered.** Ruling 4 declares it.
- **Assets outside the coursework skills.** Planning sessions for the practice are guided by the
  memory entry's preference, not graded by anything here.
- **The Module 11 paper.** It was redesigned before submission; nothing here re-grades it.
