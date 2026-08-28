# The scratch census walks every checkout that owns a scratch root and the worktree half is held at zero

[ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)
ruled six decisions out of
[#466](https://github.com/mshamblin5150-code/clinical-skills/issues/466) on 2026-08-25 and closed
with *"It does run correctly from a worktree:
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)'s `scratch_root()` resolves
through the checkout that owns the tree."* That sentence is true about resolution and false about
coverage, and the difference is most of the material. Grilled again 2026-08-27. **Eight decisions,
ruled by the clinician on that date.** Nothing is built here; this is the record the build reads.

**This record supersedes ADR 0033's ruling 3 and nothing else in it.** That paragraph stays as
written, being the dated record of what was decided on 2026-08-25;
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
holds that a deciding paragraph is untouchable. ADR 0033's *facts* are corrected in place there,
with the dated line that record requires.

## The measurement that reopened it

Nothing had ever pointed the ruled instrument at more than one checkout. Doing so, at
`19cc19f` on 2026-08-27, counts only:

| | |
| --- | --- |
| checkouts holding a scratch root | **9** — the owning checkout and **8** of 19 worktrees |
| owning checkout, top level | **45** entries, **27** accounted, **18** unaccounted |
| worktree top-level entries unaccounted | **10**, all in one worktree |
| union unaccounted | **28** against ADR 0033's recorded **19** |

**More scratch material lives outside the root the census walks than inside it.** The eight worktree
roots held more files between them than the owning checkout's did — and the figure moved during the
grilling session itself, which is why no file count is recorded here as a figure.

**The eight split in a way that decides most of what follows.** Seven hold `sessions/` and nothing
else: `docs/agents/scratch.md`'s rule obeyed exactly, zero unaccounted, and by that document's own
logic disposable as one directory. One holds ten loose top-level entries and no `sessions/` — the
rule disobeyed, which is #466's subject verbatim, in a checkout the ruled check was never going to
open. **A worktree-local scratch root is therefore not the defect; a loose top-level entry is the
defect wherever it lives.**

**Seven of the eight were removable at the moment of measurement** — merged, clean, zero commits
ahead — so an ordinary `git worktree remove` or prune takes their roots with them and nothing warns.
No standing artifact (`runs/`, `day-file-text/`, `writing-samples/`) sits in any of them at any
depth, checked before the hazard was priced, so no graded-artifact provenance record was at risk.

## What is ruled

**1. The walk covers every registered checkout that owns a scratch root.** Enumerated with
`git worktree list --porcelain`, which is `tools/adr_next.py`'s mechanism and its reporting
convention: say how many were enumerated and name every root that could not be read. The declined
alternative — one root plus a declared limit — was refused because a check reporting clean over the
majority of its subject is the shape this repository has spent
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254) and
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258) making honest. Refusing the
*existence* of a worktree root was refused for a different reason: it cannot refuse what it cannot
see, so it needs the same enumeration and is not an alternative to it.

**2. The population is split by whether it has history, and the two halves are graded differently.**
The **owning checkout** keeps a grandfathered integer baseline, because its residue predates the rule
and clearing it needs the clinician's word on unrecoverable patient material. **Every other checkout
is held at zero unaccounted, from day one.** A worktree is created after the rule, so it has no
residue predating it and nothing about it needs a person's word. A single union integer was refused
on the arithmetic: remove a worktree carrying ten unaccounted entries and a union baseline goes slack
by ten, which widens ADR 0033's declared swap hole from one entry to whatever the largest worktree
happens to be carrying.

**3. The baseline is stated by the module and by nothing else.** `EXEMPT_CEILING` in
`tools/test_skill_agreement.py` is the precedent and its own comment predicts this ticket's defect
verbatim — *"The count is not restated in prose anywhere: it would go stale one short of this
ceiling, which is the one window where nothing here would fire."* ADR 0033 recorded the figure twice
and three separate sweeps then reported the ratchet slack by exactly one. **No digit for it appears
in this record, in `docs/agents/scratch.md`, or anywhere else in prose**; the build records the live
figure from a live run, in a diff, and the command re-derives it. The worktree half carries no
constant at all, because a hard zero is a rule rather than a baseline.

**4. The worktree-root hazard is reported on every run and graded never.** How many roots exist and
how many files sit beneath them prints beside every verdict, on #258's ruling and for its reason: a
reader who learns to read a qualifier reads its absence as the stronger claim. It is not graded,
because the only threshold available would fire on seven worktrees whose entire content is the rule
being obeyed —
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s recurring defect, a
refusal aimed at correct behavior. `filled_vitals_census.py` counts five vital classes and grades
none on the same ground.

**5. Merged-clean-and-ahead is behind a flag, on a measurement.** The census proper is two
subprocesses; determining removability naively is 27 and batched is 11, six to twelve times the whole
check. ADR 0033's respec warned about exactly this — *"39 subprocesses per commit is how a check gets
disabled."* Root and file counts fall out of a walk the census already makes and cost nothing, so
they stay on the hook; the removability breakdown moves to `--worktrees`, which is the only moment it
is actionable, being the moment somebody is pruning.

**6. A failing worktree is drained to the owning checkout, and that is the only authorized remedy.**
Three cheaper ones were refused. Moving the entries into that worktree's own `sessions/` buries them
inside a directory the rule calls disposable as one unit, which is
[#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) ruling 10's two rescued
captures put straight back in the bin. **Citing them is forbidden** — see below. Grandfathering
worktree residue spends ruling 1 by never grading the population it was widened to see. A drain
reads nothing, classifies nothing, publishes nothing and deletes nothing; it moves material out of a
root that vanishes on `git worktree remove` into the one that does not, and the owning checkout's
baseline is then re-recorded in a diff by however many arrived. **A drain loosens the ratchet
visibly, which is the correct direction**: `EXEMPT_CEILING`'s comment asks that the next one be
argued for in a diff rather than typed, and a drain is that argument.

**7. The documented harvest moves into the namespace and gains no producer.** Every copy of the
harvest block writes into `scratch/sessions/<key>/`. **There are five, and the grilling argued the
decision over three** — `docs/agents/issue-tracker.md`, two in `CLAUDE.md`, and the module
docstrings of `tools/tracker_bodies.py` and `tools/tracker_scan.py`, the last two found by the
verification grep run *after* the first three were moved rather than by the search that scoped the
decision. That is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving
inside the ruling whose subject is one path written five ways, and it is recorded because the
recommendation put to the clinician carried the wrong number. They wrote three files at the top
level, and the derived rule *blessed*
them there because they are cited, so the repository's most-run documented command was the exemplar
for the habit that produced the four undocumented schemes. A producer owning the fetch, on
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)
ruling 4's model, was refused as unavailable rather than expensive: it constrains only sessions that
call it, and the sessions #466 recorded left the checkout entirely. **The census is the enforcement**
— a name at the top level refuses whatever it is called, and a name inside the namespace is accounted
for whatever it is called, so the count of naming schemes stops being a thing anyone has to police.

**8. `docs/agents/scratch.md`'s "cite it" remedy takes a qualifier, and this is a defect found in the
ratified rule rather than a clarification of it.** That document closes by recommending citation as
the cheap remedy for an entry that deserves to stay, *"needs no PHI judgment"* — and citation writes
the filename into a tracked file in a public repository. ADR 0033's central argument is that a
filename under the scratch root may itself carry PHI, which is the whole reason the baseline could
not be a set. **So the recommended remedy is standing rule 1 broken by the remedy, for exactly the
class the record was written to handle.** It is correct for an entry whose name is safe to publish —
`case-study-spec.md` is the worked instance — and forbidden for one whose name is not. Nothing had
caught it because nothing had ever had to remedy an entry.

## What this does not reach, declared rather than left to be found

**Material outside every checkout.** #466 recorded sessions harvesting the whole tracker into
`%TEMP%` and writing nothing into the repository at all. That is directionally good — no PHI
accumulates in a checkout — and it is permanently outside this walk by construction. **So the number
this check prints is how many unaccounted entries landed in a checkout, and never how many harvests
happened.** No producer closes it either; a session that leaves calls nothing.

**A separate clone.** `git worktree list` is a registry of one repository's worktrees. A fresh
`git clone` elsewhere on the disk has its own `.git`, its own scratch root, and is not in it. ADR
0016 declares the same edge for the same mechanism and for the same reason.

**The swap hole, unchanged and one entry wide per graded root.** Delete one unaccounted entry, add
another, and the owning checkout's number does not move. ADR 0033's reasoning is untouched: the only
closure is a set baseline, a set baseline is a committed list of `scratch/` filenames, and
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) established GitHub serves a
pre-edit revision of every edited record with no API to delete one. Ruling 2 narrows it rather than
closing it — a hard zero has no hole, so the hole now exists only in the one root that has history.

**Whether a drain was honest.** Nothing checks that material moved out of a worktree arrived in the
owning checkout rather than going somewhere else, and nothing could without reading what moved. That
is a reading and it stays one.

**Deletion, which is still nobody's to schedule.** Ruling 11 of #417 carved #466 out precisely
because `ready-for-agent` cannot sit over an `rm` on unrecoverable patient material. A drain is a
move and is authorized; disposal remains the clinician's, per file, and no work list may schedule it.
