# A partial body-file path resolves against the folder the command names

Ruled by the clinician on 2026-09-06, in the grilling of
[#781](https://github.com/mshamblin5150-code/clinical-skills/issues/781). Freshness gate `FRESH` at
both checkpoints; `main` did not move during the session. Nothing is built here; this is the record
the build reads.

**The subject.** `tools/tracker_publish_hook.py` resolves a relative `--body-file` path with a bare
`Path(source).read_text(...)`, so it resolves against the hook process's own working directory. The
hook is `PreToolUse` and therefore runs **before** the shell, and the Claude Code Bash tool's working
directory persists across calls — so that folder is one the author never chose and cannot see. A
present, readable body file is refused as `missing-file`, whose remedy is *create the file first*.
That advice is false for a file sitting exactly where its author put it, and an author who follows it
concludes the hook is broken.

## Measured before ruling, at `38ff616`

Every figure below was re-derived in this session by the parent, not relayed from a reader. The
population is 1,752 `.jsonl` transcripts under `~/.claude/projects`, **0 unreadable**, read by
parsing each Bash `tool_use` block's `input.command`. A subagent produced the first pass; the parent
re-derived the headline split in its own process and corrected one mis-binning, which is why the
shape table below differs from the sweep figure on the ticket.

**The form of every `--body-file` argument ever published from this machine — 2,789 occurrences:**

```
whole path (drive letter or leading /)        681
shell variable or substitution                818
partial path                                ~1242
```

**What sits in front of a partial path, and whether a reader could use it — 1,242 occurrences:**

```
cd to a literal drive path                   1152   readable
cd to a literal /c/ or / path                  41   readable, and the MSYS rule already exists
cd to a variable or substitution                0   --
cd to a folder relative to something unknown    6   not readable
no cd at all                                   43   not readable
                                            readable 1193 of 1242 = 96.1%
```

Eleven commands carry more than one `cd` before the flag.

**The population is live.** Three passes over roughly fifteen minutes returned 2,782, 2,784 and
2,789 occurrences; eight transcripts were modified during the session. Every figure here is ±10 and
is a floor on a matcher, never a certified total: a `--body-file` value assembled by string
concatenation the flag regex tokenizes short is unread, and gh invocations issued outside the Bash
tool are outside the population entirely.

**[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
finding 5 cannot answer this question and the ticket should not have leaned on it.** Its 1,028
`--body-file` publishes are split by *writability* — variable assigned in the same string, literal
not written, literal written by an earlier stage, variable assigned elsewhere — and **relative versus
whole path is not one of its axes**. The instrument it used was ad hoc and is not in the tree; the
measurement above was written for this ruling and is also not in the tree, for the reason ruling 5
gives.

### Two prior readings this session overturned

**The unquoted-backslash route is not this defect.** The ticket's 2026-09-05 sweep comment records
`--body-file C:\codeing\...\CLAUDE.md` yielding `source='C:codeingclinical_skills...'` and reads it
as a second route to the same refusal. Measured here: of the 2,789 occurrences, **52 backslash paths
were quoted and the hook reads every one**, and **1 was unquoted**. Driven through `bash` itself, an
unquoted backslash path has its separators stripped before anything downstream sees them, so `gh`
would have failed on that command too. The hook is reproducing the shell rather than diverging from
it — the resolution is correct and only the diagnostic is wrong, which is why ruling 3 reaches it and
ruling 1 does not.

**`--text` is not a second code path and the two limbs do not disagree.** The ticket's body already
records this as `SETTLED`; what the record adds is the mechanism. `main`'s `--text` limb resolves
against its own process's working directory exactly as the extraction does. It is nonetheless
*correct* where the hook is not, and for a reason that is a property of the process rather than of
the code: `--text` is run **by** the shell, so its working directory is the shell's, while the hook
runs **before** the shell and inherits an unrelated one. One rule, two processes.

## Ruling 1 — a partial path resolves against a folder the command names, and against nothing else

When a recognized publish command carries a `cd` to a literal folder, a partial `--body-file` path is
resolved against that folder. This is not the hook inferring a root. Given `cd X && gh … --body-file
P`, the shell will resolve `P` against `X`; a hook trying to read the same bytes `gh` will read has
one correct answer and that is it.

This is
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
ruling 3 applied rather than amended — *expansion is reconstructed from the command as typed* — and a
`cd` in the same command is the one thing written in that string the reconstructor did not read.

**Every root the hook could have supplied itself was refused, and the refusal is measured rather than
stylistic.** `Path(__file__).resolve().parent.parent`, offered by three prior sweeps as the cheapest
answer, and `CLAUDE_PROJECT_DIR`, which `.claude/settings.json` already interpolates, are both roots
the *hook* picks. This machine carries **41 registered checkouts and 15 of them own a `scratch`
directory**, so a partial path such as `scratch/sessions/<key>/body.md` names fifteen candidate
files. A root the hook picks can open the wrong one and report a clean scan of text nobody is
publishing, which #781's own *what must not come out of this* names as worse than the refusal it
would replace. A root the command names cannot: the shell has already decided.

`main_repo_root()` is refused for a second and independent reason.
[ADR 0121](0121-the-module-root-literal-is-the-worktree-and-is-bound-by-a-property-rather-than-a-walk-and-a-failed-tree-read-is-a-coverage-gap-while-an-unvouched-publication-is-refused.md)
ruling 2 already declares this module's two subprocess `cwd` literals correct and unchanged, and a
body file written inside a worktree would be resolved into the main clone.

## Ruling 2 — the hook's own working directory is never a fallback

Where no folder can be read from the command — no `cd`, a `cd` to a variable or a substitution, `cd
..`, `cd -`, `cd ~`, or a `cd` to a folder relative to something unknown — the publication is
**refused**. The hook does not try its own working directory, does not try it and declare the
uncertainty, and does not offer a list of candidate roots.

**Two cheaper postures were priced and both are refused.** Keeping today's silent attempt is the only
remaining way this hook can grade one file and pass the publication of another; trying it and
declaring the uncertainty is the *declaring* that ADR 0096 ruling 4 already weighed and rejected in
this module for the sibling case, in as many words: *"declaring is the remedy for a limit that cannot
be closed, and this one is closed by ruling 1."* An unresolvable expansion is refused there and an
unrootable path is refused here, on one rule.

**The cost is stated rather than estimated: 49 of 1,242 partial-path publications**, 43 with no `cd`
and 6 with a folder-relative one. Both remedies are a single edit.

## Ruling 3 — a refusal reports what was actually tried, and one report serves every cause

Whatever the cause, a refusal states the folder the path was resolved against and the path as it
stood after the command was reconstructed. That line is shared, not written once per condition.

The missing fact is the same fact under every cause: the author cannot see what the hook was handed,
so an eaten backslash, an unrooted path and a file not yet written all read as *the hook is broken*.
This is
[ADR 0105](0105-the-branch-scope-vocabulary-gains-a-verified-on-main-sentence-and-the-in-flight-label-is-discharged-at-merge.md)
ruling 5's shape — repair the diagnostic rather than widen the grammar — applied to a report instead
of to a marker.

**It does not absorb [#897](https://github.com/mshamblin5150-code/clinical-skills/issues/897).** That
ticket owns recognizing `python`, `cp` and `tee` as file writes, which is a detection question and
its own subject; this ruling gives it a report line it no longer has to word for itself. Splitting
one repair across two tickets is the shape
[ADR 0136](0136-each-escape-collapse-shape-gets-its-own-refusing-row-and-a-record-may-fail-more-than-one.md)
ruling 7 refused, and swallowing a neighboring ticket whole is that error from the other side.

## Ruling 4 — the condition is `unrooted-path` and its remedy names the `cd`

A partial path with no folder readable from the command is `unrooted-path`, a kind of its own in
`UNREADABLE_REMEDIES` rather than a widening of `missing-file`. The in-tree precedent is exact:
`external-variable` exists because a real, distinguishable condition was being funnelled into
`missing-file` and printing its remedy, and the repair was a new kind rather than a wider read.

Its remedy directs the author to put `cd "<folder>" && ` in front of the command, naming *or write
the whole path in quotes* as the alternative in the same line. **The order is measured**: 1,152 of
1,242 partial-path publications already open with exactly that `cd`, so the remedy names the form the
corpus overwhelmingly uses rather than teaching a second one — and the standing publish idiom here
begins `cd "…" && python tools/tracker_freshness.py && gh …`, so a publication refused for having no
`cd` has usually dropped the freshness gate with it. `docs/agents/issue-tracker.md` carries the same
instruction, because a tool and a manual that give different advice is the two-copies defect this
repository keeps recording.

## Ruling 5 — the `cd` reader's ceiling is a literal folder, and it is declared rather than widened

The reader resolves a `cd` to a literal folder and refuses every other spelling. That ceiling is a
row in `NOT_REACHED`, not a sentence in a docstring, because a prose limit fails nothing.

**Nothing is guessed above the ceiling**, which is what makes a floor safe here: an unread spelling
reaches ruling 2 and refuses. The measurement supports the narrow reader — **zero** occurrences use a
`cd` to a variable or a substitution — and the six folder-relative cases are unresolvable in
principle, since resolving them needs the very folder the hook does not have.

**No transcript census is committed and none should be.** The figures above are counted against
1,752 session records that are patient-adjacent working material, live, and outside this repository;
nothing committed re-derives one, and a figure nothing re-derives copied into several files is what
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) is about. They are stated
here, once, dated.

## What none of this reaches

**Whether the file the hook read is the file `gh` will publish.** Ruling 1 reproduces the shell's
resolution; it does not observe it. A file rewritten between the hook's read and the shell's run is
already `NOT_REACHED` row 5 and is unchanged.

**A `cd` whose target is correct and whose folder does not exist.** The path resolves, the read
misses, and `missing-file` is then the true kind with a true remedy — which is the pre-existing
behavior and is right.

**Whether a body worth publishing is a body worth reading.** Every gate here grades a publication's
text; none grades its content.

## What the build must not trip over

Recorded here so the builder does not rediscover them. Each was measured or read in this session.

- **`_written_before_publish` matches the path as it was typed.** Resolving before that check
  degrades #897's condition back into `missing-file`, which is exactly the misclassification ADR 0096
  was written to fix. Resolution happens after it.
- **The registration block in `.claude/settings.json` is pinned byte-exactly by a test.** Nothing
  here changes how the hook is invoked, so no environment variable is passed in and no `os` import is
  needed — the module has none today.
- **`NOT_REACHED` is pinned in both directions by a test**, so ruling 5's row is a test edit as well
  as a module edit.
- **Eleven commands carry more than one `cd` before the flag.** The shell composes them; the last one
  wins where it is absolute.
- **The same reading seam serves `-F body=@<path>`, `gh api --input`, and the AAR run-directory
  lookup.** Paths that begin resolving may make the AAR quotation gate fire where it previously could
  not reach.
- **No test anywhere constructs a relative `--body-file` argument today** — every one derives its path
  from a temporary directory — and no test perturbs the process working directory. All of this is new
  coverage rather than changed coverage.
- **`--text` keeps resolving against its own working directory**, which is correct for it. The
  asymmetry is recorded in the module rather than repaired.
