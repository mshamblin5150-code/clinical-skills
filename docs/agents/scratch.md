# The scratch root

Everything under `scratch/` is a patient record. It is gitignored, `phi_scan`'s path layer refuses a
commit from it even under `git add -f`, and **nothing in it is recoverable** — the firewall working
as designed is also the reason there is no copy.

**Maintainer tooling.** Not a dependency of the clinical skills — see [AGENTS.md](../../AGENTS.md).

The rule below is [ADR 0033](../adr/0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md),
ruled by the clinician on 2026-08-25 out of
[#466](https://github.com/mshamblin5150-code/clinical-skills/issues/466). Read that record for why
each half is shaped the way it is; this file is the rule itself.

## The top level is closed

**A top-level entry in the scratch root is accounted for iff some tracked file names it as
`scratch/<name>`.** That is the whole rule, and it is *derived* — there is no hand-kept list to
consult and none to keep in step.

Two consequences, and the second is the one sessions get wrong:

- **A directory documents itself.** A tool or a skill writes it at a named path, so it is accounted
  for by the line that writes it. This is why most directories were already clean when #466 was
  measured, and why that ticket's decision 4 — asking whether the `*-run` and `*-reference`
  directories stay — was asking about the wrong axis. The suffix never accounted for anything.
- **A loose file at the top is not.** A session drops it, nothing names it, and it is unaccounted for
  the moment it lands. **Most top-level files** were in that state when #466 was measured. This is
  where all of the mess lives. **The figure is deliberately not restated here** — ADR 0033 states the
  dated measurement, and the command re-derives the live one.

### So write session residue into the namespace, not at the top

A session's working material goes under `scratch/sessions/<key>/`. That directory is itself one
accounted-for top-level entry, so **session churn can never move the number**, and disposing of a
session's residue is dropping one directory rather than ruling on files one at a time.

`scratch/runs/<run key>/` is the precedent and is **not** the same thing. A run directory is a
graded artifact's provenance record, keyed by course, module and artifact, and it outlives every
sitting. A session directory is one agent's working pass. `CONTEXT.md` defines both — see
**Session** and **Run directory** there, and note that `Sitting`'s `_Avoid_: session` rejects the
word as a name for *a sitting*, not as a name for a pass.

### The standing artifacts

Nine names are documented and every one of them is a legitimate top-level entry:

| | |
| --- | --- |
| `runs/`, `day-file-text/`, `writing-samples/` | directories a tool or skill writes at a named path |
| `name-index.json`, `harvest-reviewed.json` | the PHI firewall's own corpus-layer inputs |
| `medatrax-profile.md`, `identity-map.md`, `voice-model.md`, `shorthand.md` | `setup-clinical-skills` account artifacts |

**They are asserted as a floor on the derived set, never as the set.** A rename that orphans one of
them fails the suite rather than silently reclassifying a standing account file as litter. The
declined alternative is recorded in ADR 0033 because it will be re-proposed: requiring the tuple to
*equal* the derived set forbids exactly the divergence the floor exists to permit, and would go red
the day a legitimate tenth artifact lands.

## The check ratchets on a count, and it walks every checkout

**A worktree can own a scratch root of its own, and most of the material lives in them.** That is
[ADR 0059](../adr/0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md),
ruled by the clinician on 2026-08-27, and it supersedes ADR 0033's ruling 3. `scratch_root()`
resolves through the checkout that owns the tree — **which is resolution and not coverage**: a
worktree that has a `scratch/` of its own is a root that resolution points away from.

`tools/scratch_census.py` enumerates every registered checkout with
`git worktree list --porcelain`, walks the top of each scratch root it finds, derives the
accounted-for set in **one** `git grep` pass over tracked files, and reports the remainder.

- **0** clean, **1** when the owning checkout's unaccounted count has risen above the recorded
  baseline **or any other checkout's is not zero**, **2** for every way of not having scanned —
  including an absent scratch root, which is `phi_scan --layers`' arrangement and its reason. A
  clone with no scratch root says *did not scan*, never *clean*. **Where a finding and a
  not-scanned limb both hold, 1 wins**, on `differential_scan.py`'s ordering.
- **Two halves, graded differently.** The **owning checkout** keeps a grandfathered integer
  baseline, because its residue predates the rule and clearing it needs the clinician's word.
  **Every other checkout is held at zero unaccounted, from day one** — a worktree is created after
  the rule, so it has no residue predating it and nothing about it needs a person's word.
- **The baseline is the module's to state and appears in no prose, including here.** Not a list,
  not hashes, and not a digit in this document or in either ADR. `EXEMPT_CEILING` is the precedent:
  a figure restated in prose goes stale one short of the ceiling, which is the one window where
  nothing fires — and that is exactly what three sweeps reported against ADR 0033's recorded copy.
  The worktree half carries no constant at all, a hard zero being a rule rather than a baseline.
- **Counts only, and there is no `--show`.** A path is printed only where a tracked file already
  names it. Everything else is a bare number, because an entry the walk cannot account for is
  precisely the one that might carry a patient's name.
- **It reports the worktree-root hazard on every run and grades it never.** How many checkouts own
  a scratch root and how many files sit beneath them prints beside every verdict, on
  [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling: a reader who
  learns to read a qualifier reads its absence as the stronger claim. It is not graded because the
  only available threshold fires on worktrees holding nothing but `sessions/`, which is the rule
  being obeyed. `--worktrees` adds the merged-clean-and-ahead breakdown, and it is behind a flag on
  a measurement — that determination costs six to twelve times the whole check, and ADR 0033's own
  respec warns that subprocess count per commit is how a check gets disabled.

**It runs on the hook and never in CI.** `.github/workflows/checks.yml` cannot run it — the scratch root is
gitignored PHI and must never reach a runner — so this check is permanently dead there.

### The remedy for a failing worktree is a drain

**Move the entries to the owning checkout's scratch root.** Not into that worktree's own
`sessions/`, which buries them inside a directory this document calls disposable as one unit — the
two captures [#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) ruling 10
rescued, put straight back in the bin. Not by citing them, for the reason below. A drain reads
nothing, classifies nothing, publishes nothing and deletes nothing, and it moves material out of a
root that vanishes on `git worktree remove` into the one that does not. **The owning checkout's
baseline is then re-recorded in a diff** by however many arrived — a visible loosening, argued for
in a diff rather than typed.

### Why the baseline is a count, and the reply to the obvious improvement

A set baseline would be strictly better and **it is unavailable.** Recording *which* entries are
unaccounted for means committing a list of `scratch/` filenames, and a filename under the scratch
root may itself carry PHI. This repository is public. Hashing them is worse rather than better — a
short filename is a dictionary away from its hash, and
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) established that GitHub
serves a pre-edit revision of every edited record with no API to delete one, so a later redaction
would not retract it.

**The cost is declared and not closed.** A count is swappable: delete one unaccounted entry, add
another, and the number does not move. That is a real hole, it is written into the module, and the
only closure available is the one the firewall forbids.

## Two things this rule does not do

**It deletes nothing, and no work list may.** Disposing of an unaccounted entry is an `rm` on
unrecoverable patient material and needs the clinician's word, per file. That is why
[#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417)'s ruling 11 carved #466 out
in the first place: `ready-for-agent` cannot sit over it. A ticket may report the count; it may not
schedule the deletion.

**An unaccounted entry is not litter.** #417's ruling 10 caught `scratch/case-study-spec.md` and
`scratch/case-study-style.md` by *opening* them rather than by reading their filenames, and both are
the raw capture behind a tracked reference sheet. **No deletion on a filename pattern** — those two
were two files away from being swept, and they are the recorded instance of why the report is a
question rather than a delete list.

The cheap remedy for an entry that deserves to stay is not an exemption: **cite it.** A tracked file
naming `scratch/<name>` accounts for it by the rule above, and is usually correct on its own merits
— a reference sheet that does not name its own derivation input is a citation gap whether or not the
file is litter.

**But citation is only available where the name is safe to publish, and that qualifier is
load-bearing rather than cautious.** Citing writes the filename into a tracked file in a **public**
repository. ADR 0033's central argument is that a filename under the scratch root may itself carry
PHI — which is the whole reason the baseline could not be a set — so for exactly that class the
recommended remedy is standing rule 1 broken by the remedy, and
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212)'s pre-edit revisions mean a
later redaction would not retract it. `scratch/case-study-spec.md` is the worked instance of a name
that is safe and a citation that was correct. **A name that is not safe has no cheap remedy, and
that is the honest position**: it stays on disk, unaccounted, inside the baseline, until the
clinician rules on it per file. This sentence read *"needs no PHI judgment"* unqualified until
[ADR 0059](../adr/0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 8; nothing had caught it because nothing had ever had to remedy an entry.
