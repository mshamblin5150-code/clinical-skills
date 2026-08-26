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

## The check ratchets on a count

`tools/scratch_census.py` walks the top of the scratch root, derives the accounted-for set in **one**
`git grep` pass over tracked files, and reports the remainder.

- **0** clean, **1** when the unaccounted count has risen above the recorded baseline, **2** for
  every way of not having scanned — including an absent scratch root, which is `phi_scan --layers`'
  arrangement and its reason. A clone with no scratch root says *did not scan*, never *clean*.
- **The recorded baseline is an integer and nothing else.** Not a list, not hashes.
- **Counts only, and there is no `--show`.** A path is printed only where a tracked file already
  names it. Everything else is a bare number, because an entry the walk cannot account for is
  precisely the one that might carry a patient's name.

**It runs on the hook and never in CI.** `.github/workflows/checks.yml` — the scratch root is
gitignored PHI and must never reach a runner — so this check is permanently dead there. It does run
correctly from a worktree: [#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)'s
`scratch_root()` resolves through the checkout that owns the tree.

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
naming `scratch/<name>` accounts for it by the rule above, needs no PHI judgment, and is usually
correct on its own merits — a reference sheet that does not name its own derivation input is a
citation gap whether or not the file is litter.
