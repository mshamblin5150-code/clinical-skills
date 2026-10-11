# A scratch path code resolves is accounted by the resolver list and an entry main accounts is never drained

**Measured at:** a7848f3d971867acac1901ccdf5dab4ca4212870

[#1511](https://github.com/mshamblin5150-code/clinical-skills/issues/1511) was filed from #1184's
grilling after the pre-commit scratch census refused every commit from the owning checkout over
`scratch/project-registry.md`. The #1395 build had added that account-owned file, resolved through
the constant `repo_root.PROJECT_REGISTRY_NAME`, and no tracked file spelled out the path, so the
census counted the file unaccounted on the day the clinician first wrote it. On 2026-10-03 a session
on a branch based before the stopgap citation followed the census's printed remedy, moved the
registry under a Ticket directory, and left project-context retrieval with no registry for about an
hour. Grilled 2026-10-11 against `main`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Nothing is broken today.** Eleven top-level names are resolved by code under a scratch root:
`runs`, `day-file-text`, `medatrax-profile.md`, `name-index.json`, `harvest-reviewed.json`,
`voice-model.md`, `project-registry.md`, `attributions.md`, `cpt-2026`, `sessions` and `uptodate`.
`scratch_census.accounted_names` returns all eleven at the measured commit, because some tracked
document names each as `scratch/<name>`. The defect is the next one added.

**The name comes from three places and the root from more.** The name is an inline literal
(`scratch_root() / "cpt-2026"`), a module constant in the consuming tool
(`uptodate_store.STORE_DIRECTORY`), or a constant in `repo_root` (`PROJECT_REGISTRY_NAME`). The root
it is joined to is the resolver call itself, a checkout-relative `"scratch"` join
(`ROOT / "scratch" / "sessions"` in `cpt_mdm_sheet.py`), a module-level constant
(`phi_scan.SCRATCH`), that constant read from another module (`harvest_review`), a local variable
(`day_file_text`, `scratch_work`), a loop over a set of roots (`coursework_run`), or a function
parameter with no scratch marker anywhere in the function (`suite`, `claim_ledger_census`). Only the
first two shapes mark a scratch root at the join site. The joins are spread across nineteen modules
besides `repo_root`. The ticket's option (a) example, reading `repo_root`'s constants, would see
only one name source and already misses `attributions.md`, `cpt-2026` and `uptodate`.

**`STANDING_ARTIFACTS` accounts for nothing.** The census never reads it. One test asserts it is a
proper subset of the document-derived set; that is its whole effect. The ticket's 2026-10-09 comment
called option (a) half-built on the strength of this object, which overstates it.

**Three standing artifacts are reached only by skill text.** `writing-samples`, `identity-map.md` and
`shorthand.md` are named by skills and by no code path. A skill must write `scratch/<name>` to tell
the agent where the file is, and that text is exactly what the census already reads, so those three
cannot have this ticket's gap.

**The census reads the committing branch.** Its accounted set is derived from the committing
checkout's tracked tree. A branch older than an artifact cannot account for it, whichever source the
census reads, and the printed remedy for every finding is `move it under scratch/sessions/ticket-<n>/`.
Every checkout carries a local `origin/main` ref the census can read without a network fetch.

## Ruling 1 — code-resolved scratch paths go through one list in repo_root

`repo_root` holds one list of the top-level names code resolves under a scratch root, and every code
path to such a name goes through an accessor reading that list. Which root the name sits under stays
the caller's argument, so a checkout-relative join is migrated as well as the owning-root ones. The
census adds every name on the list to the accounted set. A guard test refuses a direct join of a
literal or constant name to a scratch root outside `repo_root`. It recognizes the root shapes it can
trace to a resolver call or a `"scratch"` join, including through a module constant, a cross-module
attribute and a local variable; the shapes it recognizes are a floor declared in
`scratch_census.DECLARED_LIMITS`, and a root passed in as a parameter is named there as outside it.

The list is not a hand-kept copy of a fact the tree states elsewhere: a name absent from it fails to
resolve, so the code that needs the file and the census's knowledge of it ship in one commit and CI
sees both. Keeping documents as the only source with a test requiring every code path to be cited
was declined, because that test is the only protection and an unrecognized spelling passes it
silently, where here the guard backs up a list the code cannot run without. Declaring the limit and
changing nothing was declined because the refusal recurs on the first day the next artifact is
written, usually days after its build passed a CI that has no scratch root.

## Ruling 2 — an entry main's list accounts is not counted against a branch that is behind

The census also reads the list from the local `origin/main` ref, by parsing `tools/repo_root.py` at
that revision rather than importing it. An entry the committing branch cannot account for but main's
list can is not counted against either gating root; the census prints that main accounts for it,
that the branch is behind, that the remedy is to rebase, and that the entry is not to be moved. For
an entry neither accounts for, the remedy reads: bring the branch up to date with main and run again,
and move the entry under `scratch/sessions/ticket-<n>/` only if it still refuses. An absent or
unparseable `origin/main` copy leaves today's behavior and says so on the report.

Still refusing a branch that is behind, with the remedy reworded, was declined: the entry is
legitimate, so the refusal protects nothing and leaves a long-running branch blocked over a correct
file. Rewording the remedy alone was declined because it leaves the move one reading lapse away, and
that lapse is what happened on 2026-10-03.

## Ruling 3 — the list holds the code-resolved names only

The list holds the eleven names code resolves and no other. The three skill-only standing artifacts
stay accounted by their skills' own `scratch/<name>` text. `STANDING_ARTIFACTS` is rebuilt as the
list together with those three, and remains a floor on the accounted set and never the set.

Putting every standing artifact on the list was declined because the skill-only names would sit on a
code list no code reads, which is a hand-kept list with no resolver behind it to fail. Making the
list the only source was declined because it reverses this ADR's predecessor instead of extending
it, and every document-cited name, including archived material, would have to be listed.

## Supersedes

- [ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md) ruling 2, the words "A top-level entry is accounted for iff some tracked file names it as `scratch/<name>`." A code-resolved name on `repo_root`'s list is a second source; the derived document half, its floor assertion and the refusal of a typed tuple stand.

## Build checklist

- `tools/repo_root.py`: the list and its accessor; `VOICE_MODEL_NAME`, `PROJECT_REGISTRY_NAME` and
  `attribution_library`'s inline name read through it.
- Every module joining a name to a scratch root moves to the accessor. The joins measured here are in
  `aar_scan`, `claim_ledger_census`, `corpus_census`, `coursework_run`, `cpt_descriptor_agreement`, `cpt_mdm_sheet`,
  `day_file_text`, `exam_scheme`, `harvest_review`, `implementation_map`, `name_index`, `phi_scan`,
  `procedure_codes_build`, `research_ledger`, `scratch_work`, `suite`, `title_page_credentials`,
  `tracker_publish_marker` and `uptodate_store`; the build re-derives that population rather than
  trusting this list.
- `tools/scratch_census.py`: the list joins `accounted_names`; the `origin/main` parse, its
  report line and the two remedy texts; `STANDING_ARTIFACTS` rebuilt per ruling 3; declared-limit
  rows for the guard's floor, the `origin/main` currency, and the two limits below.
- Tests: the guard over each recognized name source and root shape with a planted mutant of each,
  and a parameter-rooted join shown unrecognized beside its declared limit; a name on the list and on
  no document is accounted; an entry on `origin/main`'s list and not the branch's is not a finding
  and prints the rebase remedy, driven through the public command in a throwaway repository; an
  absent `origin/main` falls back.
- Prose: `CLAUDE.md`'s *The scratch root* and *Scratch census* sections and `docs/agents/scratch.md`
  state the second source. `CONTEXT.md`'s **Accounted** and **Standing artifact** entries already do.

## What this record does not reach

- **A branch predating this build.** It runs the old census, so it neither reads main's list nor
  prints the new remedy.
- **A newer artifact than the local `origin/main` copy.** The pre-commit hook does not fetch, so an
  artifact on an unfetched `main` or an unpushed branch gets ruling 2's reworded remedy, not the
  exemption.
- **A document-only name added on `main`.** Ruling 2 reads main's list, not main's documents, so a
  branch behind a newly cited skill-only name is still refused, with the reworded remedy.
- **A spelling the guard does not recognize.** The list stays complete only as far as the guard's
  floor reaches. A root passed in as a parameter, as `suite` and `claim_ledger_census` do today, and
  a path assembled at run time are invisible to it; those call sites are migrated by the build and
  held only by review afterward.
