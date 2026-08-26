# The scratch baseline is a count because the set is PHI and the repo is public

[#466](https://github.com/mshamblin5150-code/clinical-skills/issues/466) was carved out of
[#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) by the clinician on
2026-08-23, ruling 11, because #417's decision 8 had ruled a `scratch/` cleanup **by category** and
the categories do not match the disk. Grilled 2026-08-25. **Six decisions, ruled by the clinician on
that date.** Nothing is built here; this is the record the build reads.

## The measurement came before the ruling and falsified three of the ticket's premises

**Nothing ever said a run deletes its harvest.** The body opens *"`docs/agents/issue-tracker.md`
documents one tracker harvest path and says a run deletes its own."* It does not. A tree-wide
`git grep` for any such instruction returns exactly one line — `CLAUDE.md:744`, *"the three
gitignored harvest files were deleted after the run"* — which is a past-tense record of
[#260](https://github.com/mshamblin5150-code/clinical-skills/issues/260)'s one-time full harvest,
addressed to nobody. Decision 1 was written as *a rule that failed*, and
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail* was its argument for skipping past prose to a check. **That argument
was unavailable: there was no instruction.** The honest position is weaker than the ticket's, and it
is why the rule is written down here as well as checked.

**Two of the ticket's own "unclassified" files are documented, and its own instrument says so.**
The block lists seven loose files with no home. `git grep` — the same command the ticket runs on
`case-study-spec.md` and `case-study-style.md` to get its headline zero — was evidently not run on
the rest. `identity-map.md` is a standing `setup-clinical-skills` account artifact, named at
`skills/setup-clinical-skills/SKILL.md:59`, `:72`, `:130` and `:219`, on the same line as
`medatrax-profile.md`, `voice-model.md` and `shorthand.md`. `rule-amendments.md` is cited at
`docs/agents/issue-tracker.md:37` as the source #7's and #8's destroyed bodies were reconstructed
from. So the inventory is wrong in **both** directions — three tracker sweeps found it short by
four, and it also over-claims by two.

**Decision 4 asks about the wrong axis.** It asks whether the `*-run` and `*-reference` directories
stay; [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438)'s sweep objected that
those suffixes cover only 7 of 21. Both are downstream of a false assumption — the suffix was never
what accounted for a directory. Measured at `0c39452`, counts only:

| | total | accounted for | unaccounted |
| --- | ---: | ---: | ---: |
| directories | 21 | 17 | **4** |
| files | 27 | 10 | **17** |
| **top level** | **48** | **27** | **21** |

**A directory documents itself** — a tool or a skill writes it at a named path, so 17 of 21 already
have an owner. A loose file is dropped by a session and nothing names it. This is not a `scratch/`
litter problem; it is a top-level loose-file problem, and 17 of 27 is where all of it lives.

**All nine documented artifacts are among the accounted-for**, checked one at a time rather than
assumed — the floor in decision 2 is asserted against a set that holds it today.

**The hand count taken during the grilling read 20 and the derived instrument reads 21**, because
one file qualifies only as a bare quoted name and never as a path. That is this ticket's own defect
arriving inside the session ruling on it, and it is the argument for the command computing the
figure rather than a person typing it.

## The decisions

**1. The rule is a closed top level, not a per-file list.** The top of the scratch root holds
standing account artifacts only. Session-scoped material goes under one namespace directory, which
is itself a single accounted-for entry, so session churn can never move the number. `scratch/runs/`
is the precedent in the tree. A per-file disposition was refused on the ticket's own evidence: it
was not merely destined to go stale, it was already wrong in both directions when written.

**2. The accounted-for set is derived, never typed.** A top-level entry is accounted for iff some
tracked file names it as `scratch/<name>`. A hand-kept tuple is a second copy of a fact the tree
already states, editable without failing anything —
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) — and this ticket is the
standing evidence that the copy does not hold. The nine documented artifacts are asserted as a
**floor** on the derived set, so a rename that orphans `identity-map.md` fails the suite instead of
silently reclassifying a standing account file as litter.

**The declined closure is recorded because it will be re-proposed.** Requiring the tuple to *equal*
the derived set forbids exactly the divergence the tuple exists to permit, and would fail the suite
on the day a legitimate tenth artifact lands.

**3. The check refuses on a rise and the baseline is 19.** Twenty-one entries are unaccounted for today
and clearing them needs a person's word on PHI, so refusing from day one would produce a check
people learn to `--no-verify` around, which `CLAUDE.md` warns about by name. A ratchet holds at the
recorded figure and refuses the entry that would raise it — deployable with no cleanup, and it
prevents the only thing this ticket can prevent, which is the next one.

## Why the baseline is a count, which is this record's subject

**A set baseline is unavailable and that is a firewall constraint, not a design preference.** The
natural mechanism is to record what is unaccounted for today and refuse anything new. That requires
committing a list of `scratch/` filenames. The ticket's own decision 2 states that *a filename under
`scratch/` may itself carry PHI*, and this repository is **public**. Committing that list is
standing rule 1 broken by the mechanism built to keep the firewall's own directory tidy.

**Hashing the names was considered and is worse.** A short filename is a dictionary away from its
hash, the hash would be published irrevocably, and
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) established that GitHub
serves a pre-edit revision of every edited record to anyone with read access with no API to delete
one. A redaction would not retract it.

**So the baseline can only be an integer, and the cost is declared rather than closed.** A count is
swappable: delete one unaccounted entry, add another, and the number does not move. That hole is
written into the module rather than papered over, because the only closure available is the one the
firewall forbids. **A future reader who proposes replacing the integer with a list is proposing to
publish patient-derived filenames, and this paragraph is the answer.**

## The vocabulary collision, ruled rather than avoided

`CONTEXT.md`'s **Sitting** entry carried `_Avoid_: session`, while `CLAUDE.md` uses *session*
throughout in a different sense — an agent's working pass, not a person's occasion of working on a
graded artifact. Naming the namespace `scratch/sessions/` would have used a deprecated word to mean
something other than what the deprecation was about, which is *five naming schemes for one path*
arriving inside its own remedy.

**The avoidance is scoped, and both senses are now defined.** `CONTEXT.md` gains a **Session** entry
for the pass sense and **Sitting** cross-references it. The alternative — banning the word and
renaming to `passes` or `sweeps` — was refused on the measurement: `CLAUDE.md` names the pass sense
dozens of times, so a directory named for a word nobody writes is not a naming scheme retired but a
sixth one added deliberately.

## What this does not do

**It deletes nothing, and no work list may.** Ruling 11 carved this ticket out precisely because
`ready-for-agent` cannot sit over an `rm` on PHI needing a person's word. Two entries gain owners by
a one-line citation in each of `skills/practicum-case-study/reference/rubric.md` and
`reference/style.md` naming their own derivation input — a tracked-file edit requiring no PHI
judgment, which is what takes the baseline from 21 to 19. **Everything else stays on disk.**
Disposing of the residue is the clinician's, per file, and is deliberately outside this record.

**It cannot run in CI, permanently.** `.github/workflows/checks.yml:126` — *"`scratch/` is
gitignored PHI and must never reach a runner."* So the check inherits `phi_scan`'s corpus-layer
obligation: from a clone with no scratch root it says *did not scan*, never *clean*. It does run
correctly from a worktree, because
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)'s `scratch_root()` already
resolves through the checkout that owns the tree.

**Its report is bounded by what it can name.** A path is printed only where a tracked file already
names it; everything else is a bare integer, because an entry the walk cannot account for is exactly
the one that might carry a patient's name. Counts only, no `--show`.
