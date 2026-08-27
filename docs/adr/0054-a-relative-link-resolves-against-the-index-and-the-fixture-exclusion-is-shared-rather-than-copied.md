# A relative link resolves against the index and the fixture exclusion is shared rather than copied

[#538](https://github.com/mshamblin5150-code/clinical-skills/issues/538) was filed over two
ratified ADRs on `main` linking ADR 0016 at a filename that does not exist, and nothing in the
suite resolving a relative link.

Grilled 2026-08-27. **Eight decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `3d8d745`

The ticket's own closing line is *no count of links is asserted in a test*, and the thread is the
argument for it: **six populations have been published on #538 — `56`, `92`, `74`, `124`, `139`,
and this session's — and not one re-derives.** Every one was taken with a differently-written
matcher over substantially the same tree. **The dead set has survived every pass; not one
denominator has.** So the figures below are dated and stamped, stated here once, and the build
asserts none of them.

**Under the scope ruled below, 27 dead**: four in `docs/adr/`, twenty-three in
`fixtures/*/shorthand/README.md`, and **nothing dead anywhere else**. The four are cited by
`file:line` under *The repairs*; the twenty-three are one substitution in six files. **No denominator
is stated here**, which is this record's own ruling 9 applied to this record — see the correction
line at the foot.

**The title is stale and the body's account of the cause is half of one.** It is four files and two
causes: the ADR 0016 boilerplate typo at `0034:49`, `0036:55` and `0049:173`, and ADR 0045's
remembered slug for ADR 0044 at `0045:57`.

**The `fixtures/` cost is one cause, not the two a sweep reported.** All 46 are a wrong relative
depth. The 23 in prose are `[fixtures/README](../README.md)` written from
`fixtures/<set>/shorthand/`, where `../` lands in the set directory; `[assertions.md](../assertions.md)`
in the same files resolves. **`fixtures/hedged-dx/shorthand/README.md` writes both depths** — the
correct `../../README.md` once, the dead `../README.md` seven times. The #518 sweep's reading of
the prose half as a distinct defect class, and this session's first reading of it as a wrong
*filename*, were both wrong and are both withdrawn.

**Two of the body's stated costs price populations that do not exist.** There are **zero relative
image links** in the graded set, so option 2's *"needs a rule for anchors, images and
intentionally-relative paths"* is empty on two of its three limbs. And the graded set holds **37
relative non-`.md` targets — 31 directories, three `.py`, two `.yml`, one `.json` — none dead**.

**Of the four records that paste the ADR 0016 link into a correction line, three have the filename
wrong.** Most records carrying a correction line cite no ADR at all. The citation is decorative and
it is where the whole defect lives.

## Ruled 2026-08-27

### The scope

**1. Every tracked Markdown file except `fixtures/`.**

The body offered `docs/adr/` only or every tracked file, and the measurement collapsed the middle:
everything outside `fixtures/` is already clean, so widening from `docs/adr/` costs **zero repairs
and no new rule**. It is not a compromise between the two — it is **the widest scope that is
clean today**, which means the instrument starts green over the whole consumer-facing tree and the
only thing keeping it green is that nobody writes a dead link there.

`docs/adr/` alone was refused as a saving that does not exist: the walk is one `git ls-files` either
way, and it would leave `docs/agents/`, `skills/`, `reference/` and the two root contracts ungraded.

**2. The `fixtures/` exclusion is `graded_files()`, imported rather than restated.**

`tools/test_skill_agreement.py` already holds this ruling — `FIXTURE_PROSE = {"README.md",
"assertions.md"}` graded, preserved run records excluded, *"the only repair available would be to
falsify it"* — and the default under `fixtures/` is already to exclude, so a new kind of record
lands outside rather than inside.

**Sharing rather than copying, and #253's test is what decides it.** That rule refuses a shared
helper where two modules *happen* to have written the same thing, because a bind would forbid the
divergence the copy exists to permit. This is the other case: **a preserved run record may not be
edited is a fact about this repo, not a fact about step citations.** If somebody ever widens
`graded_files()` to grade a run record, the link check should move with it, and the failure a copy
would cost is somebody widening the exclusion for citation reasons without opening the file where
the second consumer lives.

**What it costs is named: 23 repairs beyond the four.** One substitution in six files.

**Grading preserved run records was refused on a measurement.**
`fixtures/filled-anchor/notes/case-07.md:3` links into
`.claude/worktrees/ticket-26-end-to-end-072f91/`, a worktree that no longer exists.

### The instrument

**3. It lands in `tools/test_skill_agreement.py`, beside `EveryCitedStepResolvesToADeclaredStep`.**

The body's suggested home is retired by ruling 1: `tools/test_adr_numbering.py` was offered because
*"it already walks that directory"*, and the scope is no longer that directory — its walk is
`iterdir()` over four-character stems and has nothing to give a link resolver.

**[ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)
ruling 4's reason for a new module does not transfer.** It refused `test_glossary_vocabulary.py`
because that module declares `CODE_VOCABULARIES` as its ceiling in as many words, and a whole-file
walk under that docstring would make the ceiling untrue. This module declares no such ceiling; it
declares a walker, and explains in its own docstring why it grew one.

**The two walkers are the same defect at two widths.** #233 resolves `step 7` against a file's
headings; this resolves a path against the tree. Both are a cross-reference whose second end is
unknown in advance, both walk `graded_files()`, both are excluded from `fixtures/` for the identical
reason. Splitting them puts *which files are editable* in one module and one of its two consumers in
another.

**The cost is one sentence.** The module docstring opens *"Every defect this file guards is one
document contradicting another"*, and a dead link is not a contradiction — there is no second
document, only an absent one. It gains **or naming one that is not there** in the same change.

**4. The resolver is a pure function with the existence check injected, and the graded class carries
a denominator floor.**

`dead_links(text, owner, exists)`. The liveness class then drives synthetic text and needs no
temporary checkout, which is `TheStepResolverIsLive`'s arrangement in the same module and for its
stated reason: *a repaired tree is not a reason to stop testing the shape it was repaired out of.*

**The failure this buys cheaply is the one that would otherwise land green.** Resolve against the
repository root instead of the linking file's directory and **all four known defects still fail**,
so the check looks correct while every `../`-bearing target in `fixtures/*/README.md` and `skills/`
is graded wrong. Under an injected `exists` the mutant is caught by recording what the resolver
asked for; under a filesystem resolver it needs a scratch tree built to make the two bases differ.

**The seam it opens is named and answered.** Nothing stops a later edit passing a stub in the graded
class, so that class asserts it walked a non-trivial file count and found a non-trivial target count
before it asserts zero dead. `tools/test_build_artifacts_ignored.py` shipped *"three of four
assertions against a check that says yes to everything"*, and this is that shape's remedy.

**5. Every relative target, resolved by membership in the index.**

Two bounds, one decision, because both are the definition of `exists`.

**The `.md` bound is closed rather than declared**, because the population that would have made it
expensive does not exist: 37 non-`.md` targets, none dead, no images at all. The 31 directory links
are cross-references graded by nothing today, and a rename of one of the seven fixture-set
directories would take `fixtures/README.md`'s table dead in seven places.

**The index rather than the disk**, and it closes a limit instead of declaring one. CI runs on
`windows-latest`, where `os.path.exists` is case-insensitive, so a target differing only in case
passes on every machine this suite runs on and 404s for a reader on github.com, which serves the
repository case-sensitively. Set membership is exact-case by construction, and it additionally
guarantees a resolved target is a file a cloner gets. **The switch is free**: both resolvers give
the identical 27 dead today, and no target in the graded set is untracked or gitignored.

**What it weakens is stated: a directory target says the directory exists, not that it holds what
the sentence says it holds.** That is a declared limit below rather than a reason to refuse the 31.

**6. Five limits in the class docstring, controls on the three that are re-derivable, and the two
inherited ones are pointed at.**

**A docstring rather than a declared-limits object, and the tree decides it.** All thirteen such
objects in `tools/` are production modules; **no test module holds one**, and both nearby ceilings —
`tools/test_ls_files_coverage.py` and `EveryCitedStepResolvesToADeclaredStep` — are docstrings.
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 8 says its three-field row shape is *"ruled as a shape and cited as no precedent"*, so it does
not reach here.

**And [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s defect is a
two-copies defect.** A prose edit failing nothing is a hazard because a second copy exists to drift
against; a test-class docstring with no second copy anywhere has nothing to drift against. That is
what decides it, not the convention count.

The five it declares, and the two it does not:

- An **absolute URL** is not resolved. That is
  [#516](https://github.com/mshamblin5150-code/clinical-skills/issues/516)'s surface, and the
  misspelled ADR 0016 slug is live there now. *Control.*
- A target **inside a fence or code span** is skipped. One live instance, an elided illustrative
  path in ADR 0048. *Control.*
- An **anchor fragment** is dropped, so a link to a heading that does not exist resolves clean.
  *Control.*
- **The target's identity is not read.** A link resolving to a file that exists is not a link to the
  right file. **Zero instances today, which is why it is declared rather than left to be found** —
  it is `EveryCitedStepResolvesToADeclaredStep`'s own sharper half arriving on paths.
- A **directory target** says the directory exists, not that it holds what the sentence says.

The untracked window and the `fixtures/` run-record exclusion are declared at `graded_files()` and
are **pointed at, never restated**. Copying that window sentence here would manufacture the second
copy [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) exists to prevent,
inside the change that cites it.

**ADR 0053 ruling 7's control discipline transfers even though its row shape does not.** An
`assertNotIn` passes vacuously against a dead detector, so each control asserts the skipped form is
unreported **and** asserts the same input unskipped is reported, proving the absence was caused by
the thing named.

**7. A method note, because the thread has it backwards three times.**

Three sweeps record that *a good-slug / bad-slug mutation does not discriminate, and what does is a
link whose stem is a plausible slug for a number that exists.* **That is true of the predicates it
was aimed at and false of this one.** Those were number-keyed — *test each `NNNN` against
`git ls-tree`* — and `0016` exists either way. Against a path resolver the pair discriminates
perfectly.

The plausible-slug case is kept, for a different reason than the one on the record: **it is the case
that fails if somebody later simplifies this into a number-keyed check.** A forward-looking
regression guard, not a discrimination test — and building it as the latter would have produced a
case that proves nothing.

### Where it does not go

**8. No command, no hook, and the window stays open.**

**A hook is refused by ADR 0041 ruling 4's door.** `tools/hooks/pre-commit` does not fire on an
automatic merge commit at all, while CI runs the suite on the `pull_request` merge result and on a
push to `main`. A link walk needs no corpus, no network and no `scratch/`, so it runs anywhere the
suite does.

**Widening the walk to `--others --exclude-standard` is refused by precedent rather than by
preference.** [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254) priced that
exact change and the clinician declined it on 2026-08-19; `graded_files()`'s docstring records the
ruling. Reopening it inside a ticket that is not about it would overturn a ruling by side effect.

**A `tools/` command was the strongest declined option and it is worth the paragraph.** ADR 0053's
sweep comment on #538 is the only thing on that thread that ever *prevented* an instance rather than
counting one — *"those links were verified by a resolver run over the record before it was
committed"* — and every instance the thread traced to its commit arrived in a **new** record, which
is exactly the population the index cannot see at authoring time.

**It is refused on the window's measured width.** A new ADR is invisible to `git ls-files` when
written and visible the moment it is staged, so the gap is **written-but-not-staged**, not
written-but-not-merged. Under ruling 4 the check an author needs is one `git add` away from being
the suite. A dedicated module owes a `console_codec` call, an exit-status contract in this
repository's 0/1/2 grammar, a decision about whether its output is PHI, and its own test module —
which is a great deal of surface for a window that closes when you stage the file you just wrote.

**So the authoring-time guard is one sentence in `docs/agents/domain.md`** telling whoever writes a
record to stage it before running the suite, beside the correction rule already there.

**The residue is ADR 0041 ruling 4's own accepted price, arriving on a second check**: a test fires
when somebody runs the suite, and between a hand insertion and the next run nothing watches.

### The repairs

**9. This ticket carries all 27, and the title is rewritten.**

Ruling 2 forced the fork: taking the shared exclusion made 23 fixture-prose links this ticket's
problem, and the test cannot land green until they are fixed. Splitting them out was refused on the
thread's own strongest recorded argument — **a copy lands faster than a reader finds one** — and the
23 are one substitution in six files, a smaller diff than the test that grades them.

**Every population figure is struck and the `file:line` cites are kept**, which is the ticket's own
closing line applied to the ticket. The title and `## The state` say *two ratified ADRs*; it is four
files and two causes.

**The three ADR 0016 links are repaired by fixing the slug, not by deleting the citation.** Deleting
is tidier — the citation is decorative, most records omit it, and three of the four that paste it
are wrong — and it is rewriting ratified records past what the ticket asks.

**The instance in a #456 comment stays on
[#516](https://github.com/mshamblin5150-code/clinical-skills/issues/516)**, on
[ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)'s
ruling: a dated tracker comment is evidence and is not rewritten.

## The glossary

**Two terms, and two more were refused.** `Graded file` is a function's return value and
`CONTEXT.md` is a glossary and nothing else; `Cross-reference` would have been a synonym coined for
the occasion.

**Relative link** is filed in `### Checks` beside **Citation**, the term it is defined against, on
[ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)
ruling 1. The distinction is the whole reason #538 is not #516: a citation is tracker text and a
relative link is a tracked file, which is why one check cannot reach both. Its second sentence
carries ruling 5, and that clause is what makes the term something a check can hold rather than a
synonym for *link* — a word `Binding`'s `_Avoid_` list already steers away from one meaning without
ever saying what it is.

**Preserved run record** is filed beside **Fixture**. It is load-bearing for ruling 2 and it
currently exists only inside a Python docstring.

## What this does not reach

**Whether a resolving link is the right link**, which is declared limit 4 and is permanent.

**A record written and never staged before the suite runs.** Ruling 8, and it is inherited from
`graded_files()` rather than introduced here.

**Whether the two prose repairs in `fixtures/*/shorthand/README.md` should have been the run
records' repair too.** They should not — the records are excluded by ruling 2 — but nothing in the
build re-derives that the 23 prose instances and the 23 record instances share one cause. That is
stated here and graded nowhere.

## Consequences

`tools/test_skill_agreement.py` gains a class, a docstring clause and eight liveness members. Ten
files gain link repairs. `docs/agents/domain.md` gains one sentence. `CONTEXT.md` gains two terms.
No module is created, no hook changes, and no command ships.

**The check is obligatory at the merge and advisory nowhere**, which is the posture ADR 0041 ruling
4 set and this record does not spend.

*(Corrected in place 2026-08-27, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. **The population figure published
here did not re-derive, and it is the seventh on #538's thread to fail that way.** This section read
*105 graded files, 598 relative targets, 27 dead*. Re-derived by one walk over the ruled scope the
same day: **853** relative targets across 106 files. The 598 was never measured — it was assembled,
by adding a `.md`-only subtotal to an **estimated** fixture-prose subtotal and a non-`.md` count,
rather than by running the ruled scope once. So it is the same failure as the `56`, `92`, `74`,
`124` and `139` before it: a figure and the matcher that produced it coming apart.

**The dead set and every `file:line` cite re-derive exactly, and did through every pass.** That is
ruling 9's own reasoning — *strike the figure, keep the cites* — arriving on the record that ruled
it, which is why the denominator is dropped here rather than replaced. The build asserts no count of
links, so nothing downstream moves.

Ruling 1 carried the same defect one ruling over and is struck the same way: it read *adds 368
targets*, which is a `.md`-only subtotal inside a record whose ruling 5 grades **every** relative
target. The honest form of that sentence never needed a number — what makes the widening free is
that it costs no repair and no rule, and both of those re-derive. No ruling is rewritten.)*
