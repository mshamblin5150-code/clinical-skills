# A currency write re-applies its change under a short lock and a fetch resumes its own handoff

**Measured at:** 2021e2b985c9d924250729e556589ad2aeb96751

*Re-declared from `f7be858` on 2026-09-13, for the addendum below. The base moved across ADR 0202,
the #993 build, ADR 0206, ADR 0203 and the #986, #991 and #1209 builds; none of them changed
`tools/guidelines_currency.py`,
`tools/artifact_lock.py`, `tools/guidelines_build.py`, `tools/threshold_coverage.py`,
`tools/test_guidelines_currency.py` or `tools/hooks/pre-commit`, so the figures still re-derive by
construction.*

*Re-declared from `b9456cc` on 2026-09-12. The base moved once between the measurement and
publication, carrying ADR 0204 and a `CONTEXT.md` addition and nothing else. Every artifact the
figures below rest on — `tools/guidelines_currency.py`, `tools/artifact_lock.py`,
`tools/guidelines_build.py`, `tools/threshold_coverage.py` and `tools/hooks/pre-commit` — is
byte-identical across that move, so the figures re-derive by construction.*

Out of [#994](https://github.com/mshamblin5150-code/clinical-skills/issues/994), grilled on
2026-09-12; the clinician ruled every point below the same day. The freshness gate stopped the first
push as `STALE` and the branch was brought forward to the base above. Nothing is built here; this is
the record the build reads.

#994 reported that `tools/guidelines_currency.py` writes tracked reference files with a plain
`write_text`, taking neither `artifact_lock` nor a sibling-and-`os.replace`, and offered three
options: atomic replace, a lock as well, or a declared limit. Reading the code at the base above moved
the question before any option could be weighed. The ticket framed the concurrent failure as *last
writer wins, whole-file*, and located the contention in several worktrees; neither holds.

## What was measured before ruling

**Separate worktrees do not contend for these files.** `reference/guidelines-currency.md`,
`reference/thresholds/coverage.md` and `reference/guidelines-catalog-audit.md` are all tracked, so each
checkout writes its own copy and git reconciles them at a merge. `artifact_lock.lock_path` keys on the
resolved path, so two checkouts already compute different **lock identities**, which is correct for
different files. The real concurrent case is two commands in one checkout.

**The `--read` loss window spans every download, not one write.** `main` loads `registry_text` at
`tools/guidelines_currency.py:1134`, `_run_reads` then downloads each requested society index, and the
write at `tools/guidelines_currency.py:1104` renders `record_index_matches(registry_text, ...)` from
that early text. Two parallel reads in one checkout, `--read USPSTF` and `--read IDSA`, each load the
registry, and whichever writes second erases the first one's observation dates. Atomic replacement
does not close that, and neither does a lock taken only around the write. `record_index_matches` is a
pure function of registry text, so the change can be re-applied to a fresh read.

**The rollback pair the ticket calls disagreeing restores bytes that never changed.** In
`fetch_replacement`, the `audit_text` and `coverage_text` captured at
`tools/guidelines_currency.py:862` and `tools/guidelines_currency.py:869` are read before the
download. The forward writes, `_upsert_audit_digest` and `_mark_topic_unread`, run only after
`build_completed` is set, and the rollback writes at `tools/guidelines_currency.py:906` and
`tools/guidelines_currency.py:907` run only while it is unset. `tools/guidelines_build.py` names
neither file. So the rollback either rewrites identical bytes or, if the file was edited during a
download, reverts that edit.

**The corpus writes have the same defect and a worse recovery.** `destination.write_bytes` at
`tools/guidelines_currency.py:881` and the `.fetch.json` sidecar write beneath it go straight to the
shared external corpus. The cleanup is `except Exception`, so `KeyboardInterrupt` during the build
leaves both, and the `destination.exists()` refusal at `tools/guidelines_currency.py:829` then refuses
every retry.

**An interruption after the build leaves a handoff nothing finishes.** Between
`_upsert_audit_digest` and `_mark_topic_unread` the audit binds the replacement while coverage still
names the retired document. The rerun is refused by the same `destination.exists()` check. Neither
`guidelines_currency.audit`, which grades the registry against the catalog, nor `threshold_coverage`,
which honors a handoff already written through `SUPERSESSION_HANDOFF`, reads that half-state.

**The hook cannot see the files that half-state lands in.** `tools/hooks/pre-commit` runs the
refusing `guidelines_currency.py` invocation only when `guidelines-catalog` or `guidelines-currency`
is staged; the audit ledger and `coverage.md` are the two a fetch writes.

## Ruling 1. A write re-applies its change to a fresh read under a short lock

Each tracked write takes `artifact_lock` on its own file, re-reads the file under the lock, applies
the command's change to that text, and replaces the file. For `--read`, the change is the matched set
passed to `record_index_matches`. Lost updates within one checkout are closed; truncation is closed by
ruling 6's sibling write.

**Chosen over the ticket's option 2, a lock over the command**, because that lock would be held
through minutes of downloads and refuse an ordinary second run for the duration. **Chosen over
option 1, atomic replace alone**, because it leaves the parallel-read loss standing. **Chosen over
option 3, declared**, because since #772 every `--read` writes, and a truncated tracked file is
committable.

## Ruling 2. The rollback writes are deleted

`audit_path.write_text(audit_text, ...)` and `coverage_path.write_text(coverage_text, ...)` in the
`except` block of `fetch_replacement` go. Neither tracked file has been written when they run, so they
restore nothing and can only revert a concurrent edit or truncate an untouched file. The block keeps
removing the sidecar and the fetched PDF. A test drives a build failure and asserts both tracked files
are byte-identical to before.

## Ruling 3. The corpus writes are in scope

The fetched PDF and its sidecar are written through siblings and replaced, the destination takes
`artifact_lock`, and the cleanup catches `BaseException`. This widens #994 past its title's three
tracked files because `fetch_replacement` is one transaction and its cleanup is the block ruling 2
edits: repairing the tracked half while Ctrl+C still blocks every retry would ship half the repair.

## Ruling 4. No lock is held across network I/O

The destination lock wraps the write alone. At the write it re-checks `destination.exists()` under the
lock and refuses if another fetch landed first. The early `destination.exists()` refusal stays as an
advisory preflight, so a fetch that is certain to be refused never spends a download. A collision
costs one wasted download. Every lock this command takes is therefore held for the length of a read,
a render and a replace.

## Ruling 5. A busy lock retries for about a second, then refuses

A write that finds its lock busy retries a bounded number of times over roughly one second, then exits
2 with `ArtifactBusy`'s owner and artifact. A refused `--read` also names the societies whose reads
were lost, so the rerun is exact.

**This agrees with [ADR 0199](0199-a-map-overwrite-is-attributed-rather-than-prevented.md) ruling 3
rather than departing from it.** That ruling refused a retry on a measured hold of minutes, where a
retry that mattered would block for minutes. Here ruling 4 bounds the hold to milliseconds, so a busy
lock is almost always a collision that clears inside the retry, and refusing it would discard every
download a `--read` completed. The shared principle is that the hold's length decides; the outcome
differs because the length does. `artifact_lock` gains no blocking mode.

## Ruling 6. Every write goes through one private helper, held by a walk

One private helper in `tools/guidelines_currency.py` performs the sibling write, the optional lock,
the bounded retry and `os.replace`. A test walks the module by AST and fails on any `write_text`,
`write_bytes` or write-mode `open` outside that helper. The walk declares its ceiling beside the
implementation: a write assembled by indirection is invisible to it.

**Not a shared module.** The existing `os.replace` writers across `tools/` do not share one policy —
some lock, some do not, some write bytes — and
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test for extraction is a
policy that exists to be depended on. None is migrated.

`--draft` writes through the helper without a lock, since its destination is a scaffold path the
person names.

## Ruling 7. A rerun resumes an interrupted handoff, and the audit reports one left unresumed

When the destination PDF exists and its SHA-256 equals the digest in its sidecar receipt,
`--fetch-replacement` skips the download and the build and continues from `_upsert_audit_digest`.
Both remaining writes are idempotent: the upsert replaces its row and the coverage mark sets a fixed
value. A PDF with no receipt, or a digest that disagrees with it, is still refused.

The default `guidelines_currency.py` audit gains a finding for a **supersession handoff** with one
half: a `superseded` registry binding whose replacement is bound in the audit ledger while the
coverage row records no handoff to it. An interrupted fetch nobody reran is then visible on every
ordinary run rather than only to the command that failed.

## Ruling 8. A half-finished handoff refuses, and the hook reads the files it lands in

The finding exits 1, as registry damage does, and unlike the advisory `superseded`, `absent` and
out-of-cycle observations. It is state this repository's own interrupted command left rather than an
observation about a publisher, and it lets coverage go on treating retired guidance as a live source.
The hook's refusing invocation widens its staged trigger to `reference/guidelines-catalog-audit.md`
and `reference/thresholds/coverage.md` as well as the catalog and registry.

## Declared limits the build adds

`guidelines_currency.DECLARED_LIMITS` gains rows for what these rulings do not guard, pointing at
`artifact_lock.NOT_GUARDED` rather than copying it: processes configured with different lock roots; an
editor or git operation writing a file between the re-read and the replace; separate checkouts, which
write separate copies and are reconciled by a merge; and ruling 6's walk ceiling.

## Rejected options

**A lock on the read path.** Every consumer reads these files; only the write needs ownership, which
is #994's own refusal and stands.

**Keeping the rollback writes, made atomic or guarded.** Atomic keeps the stale revert; guarded adds a
comparison that exists to restore a state never left.

**A lock spanning the fetch's download.** It refuses a colliding second fetch earlier, at the cost of
the long hold ruling 1 refused for `--read`.

**Refusing a busy lock at once, or blocking until free.** The first discards a `--read`'s downloads
over a collision that would clear in milliseconds; the second widens a shared nonblocking module for
one caller.

**Detect the half-finished handoff but leave recovery to a person, or only declare it.** Detection
alone leaves the same command that failed unable to finish its own work.

## What this record does not settle

**What `--read` writes.** [ADR 0156](0156-the-readme-gate-is-a-set-difference-and-standing-stays-distinct-from-edition-currency.md)
ruling 6 settles which documents are stamped; this record governs how the bytes land.

**Concurrency in `tools/implementation_map.py`.** ADR 0199 owns that artifact.

**Whether the published `CLAUDE.md` account of the fetch is corrected now.** Its *Guideline edition
currency* section describes behavior as built. It is corrected by the build that changes the behavior,
so the prose never describes a mechanism the tree does not have.

## Addendum, 2026-09-13 — what the exhaustive sweep changed, hours after ratification

The sweep closing this grilling read all 64 open tickets and read this record adversarially. It found
six facts overstated and two decisions the rulings left open. The facts are corrected in place, on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, and change no ruling. The two decisions went to the clinician and are rulings 9 and 10.

**Corrected facts.**

- **"since #772 every `--read` writes"**, in ruling 1, overstated: `_run_reads` writes the registry
  only under `if matched:`, so a read whose join matches no document writes nothing. Ruling 1's
  reason holds for every read that matches.
- **"`_run_reads` then downloads each requested society index"** is true of plain reads only. A
  society read through `--capture` downloads nothing, so its loss window is a file read rather than a
  network fetch.
- **"The hook cannot see the files that half-state lands in"** was wider than the hook. A staged
  `reference/thresholds/coverage.md` does run two refusing checks, `threshold_coverage.py` and
  `subject_ledger.py`; neither detects the half-state, and the audit ledger triggers no refusing check.
- **"a measured hold of minutes"**, describing ADR 0199 ruling 3, overstated that record: it gives an
  observed upper bound, a hold from `00:44:07Z` to some time before `00:50Z`, not a measured duration.
- **"the coverage mark sets a fixed value"**, in ruling 7, holds only when the resume reuses the
  receipt. `_mark_topic_unread` and `_upsert_audit_digest` both write `observed`, which
  `fetch_replacement` takes from `date.today()`, so a resume on a later day writes the same bytes only
  if it takes `observed` from the sidecar's `FetchRecord`. That record's digest field is `sha256`.
- **Ruling 2's test already exists and does not discriminate.** Deleting the two rollback writes leaves
  `test_failed_rebuild_rolls_back_received_bytes_and_registry_mutations` green, and making them write
  junk turns it red. A test that shows ruling 2 applied edits a tracked file inside the mocked build
  and asserts the edit survives.

**The half-state has a designed route, not only an interrupted one.** "An interruption after the build
leaves a handoff nothing finishes" is incomplete. `run_catalog_check` sits between
`_upsert_audit_digest` and `_mark_topic_unread`, and an ordinary failure there leaves the same state
on purpose: `test_post_build_check_failure_keeps_source_and_digest_coherent` asserts the fetched PDF
and the audit row survive while coverage is byte-identical, and `CLAUDE.md` describes that outcome as
intended. Ruling 7's resume reaches it unchanged; ruling 8's refusal was ruled without this route in
view, which is why ruling 9 exists.

**Rulings 7 and 8 collide at the preflight.** `fetch_replacement` raises when `audit(...)` returns
failures, and `main`'s `--read` path does the same before any read. A finding in `audit().failures`
would therefore refuse the very rerun ruling 7 depends on, and every `--read`, which is why ruling 10
exists.

## Ruling 9. A half-finished handoff refuses whichever route left it

Ruling 8's refusal applies whether an interruption or a failed catalog check left the state. The files
cannot tell the two apart, and both would commit coverage that treats retired guidance as a live
source. The remedy is the same for both: correct the cause and rerun, which ruling 7 resumes. The
build rewords `test_post_build_check_failure_keeps_source_and_digest_coherent` so *coherent* names the
digest agreeing with the fetched bytes, never a complete handoff.

**Rejected:** refusing only an interruption, which would record a stop reason in the receipt and let a
stale failure marker hide a real interruption; and an advisory finding, which lets the state be
committed.

## Ruling 10. The finding blocks the commit and the default audit, and neither preflight

The half-finished handoff finding exits 1 from the default `guidelines_currency.py` audit and so from
the hook. Both preflights set it aside, and nothing else:

- **`--read`** sets it aside always. A read stamps the registry and writes neither the audit ledger nor
  `coverage.md`, so it cannot deepen the state.
- **`--fetch-replacement`** sets it aside only for the handoff it is resuming: the same retired
  document and replacement, with the destination PDF's SHA-256 equal to its receipt's. A different
  unfinished handoff still refuses a new fetch.

Every other registry failure refuses both preflights as it does today.

**Rejected:** refusing `--read` as well, which blocks observations over a state they cannot worsen; and
letting a resume skip the preflight, which drops every other registry check along with the one it
needs to pass.
