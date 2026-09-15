# The publish marker records a hook run per checkout

[#1151](https://github.com/mshamblin5150-code/clinical-skills/issues/1151) found that the pre-publish
hook's marker advances only when a publication is graded, so a hook that was never registered and a
hook that saw nothing gradeable age it identically. Grilled 2026-09-15 against `39d1bece`; the
clinician ruled every point below on the same day. Nothing is built here; this is the record the
build reads.

## Measured before ruling

### There is one marker for the whole account

`phi_scan.TRACKER_PUBLISH_MARKER` is `SCRATCH / "runs" / "tracker-publish-hook.json"`, and `SCRATCH`
is `repo_root.scratch_root()`, which resolves to the owning checkout. Driven from a worktree holding
no `scratch/` directory, the path resolved to the main checkout's file and
`phi_scan.tracker_publish_notice()` printed an age of zero days. Every registered worktree was
checked for a copy of its own and none holds one. **So every worktree writes and reads one file**, and
a commit from a worktree whose hook never registered reads as fresh whenever any other session has
published.

[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 5 gave the marker the job of reaching the hook's own non-registration, and its *What none of it
reaches* names the case as a worktree one unaccepted trust dialog from a silently absent hook. The
shared file cannot reach that case, and #1151's body did not name it.

### The write sits after every early return

`tracker_publish_hook.handle` calls `write_marker()` only after `grade_command` has returned a grade
that was scanned or denied. It returns without writing for a payload with no command, for a
read-only or unrecognized command, for a command whose publication fields could not be found, for
the unmodeled-shell refusal on the `PowerShell` and `Monitor` registrations, and for a hook failure.
The `Bash` registration runs `tracker_publish_stub`, which returns before the full hook for any
command text without `gh`, so most `Bash` calls never reach `handle` at all.

### A commit passes through the registered stub

`git commit` issued by a session is a `Bash` tool call, and since
[ADR 0231](0231-an-unreproduced-publication-is-refused-unread-and-every-gh-command-reaches-the-hook.md)
ruling 2 the `Bash` entry carries no `if`, so the stub runs on the commit command before the
pre-commit hook prints the notice.

### Three recent records declined to mark what they overturned

ADR 0219, ADR 0225 and ADR 0231 each left an overturned record unedited, because whether a superseded
ruling carries a marker is [#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201)'s
open decision.

## Ruled 2026-09-15

### 1. The notice says whether the hook has run in this checkout

The marker answers one question for the committing checkout: has this checkout's registered hook
been invoked. **Keeping the account-wide reading and correcting only the prose was declined**: it
withdraws ADR 0083 ruling 5's job rather than doing it.

### 2. One record, and no graded record beside it

The record means only that the hook ran. **A second dated record for a graded publication was
declined**: the only reader of the marker is `phi_scan.tracker_publish_notice`, which spends a date,
and nothing asks when a publication was last graded.

### 3. The record carries no count

**Counting recognized against unrecognized commands was declined** on two grounds. The unrecognized
count mixes read-only calls such as `gh issue view` with publications assembled at run time, so it
prints the same whether publications went ungraded or not. And increments lost between concurrent
writers make a count silently wrong where a same-day date is not.

### 4. One date-only file per checkout, under the owning scratch root

Each checkout's record is its own small file in a subdirectory of the owning checkout's
`scratch/runs/`, named from the checkout's identity. The writer and the reader both derive that
identity the way `REPO_ROOT` is already derived, from the location of their own module, so they agree
without exchanging anything. A record left by a removed worktree is never read again and is not
cleaned up. **One shared file with an entry per checkout under `artifact_lock` was declined**: every
`gh`-bearing call would contend for a lock and the hook would acquire a way to block. **One shared file
without a lock was declined**: a concurrent writer can erase another checkout's entry, and a healthy
checkout would read as never run.

### 5. The write happens first, at every registered entry point

The stub writes the record before it filters on `gh`, and the full hook writes it before it parses
the payload, which covers `PowerShell` and `Monitor`. A registered checkout committing through a
session therefore reads zero days on its own commit, and a checkout whose hook never registered reads
never run or an older date. A hook failure, an unmodeled-shell refusal and a read-only command all
count as a run. **Writing only at the top of `handle` was declined**: a registered checkout that commits
without publishing would read never run, the same as an unregistered one. **Writing only in the stub
was declined**: it misses a session that issues commands only through `PowerShell` or `Monitor`.

### 6. The notice names the checkout and still names no threshold

It reads *"last tracker pre-publish hook run in this checkout"* followed by an age in days, by
*never*, or by *NOT RECORDED* for an invalid record. It remains a notice and never refuses, carrying
ADR 0083 ruling 5's no-threshold argument forward. **A remedy line on *never* was declined**: a commit
made by hand outside a session legitimately reads never, and a remedy printed there is wrong every
time. **Refusing on *never* was declined** for the same commit.

### 7. The old shared file is left untouched

`scratch/runs/tracker-publish-hook.json` in the owning checkout is retired and unread after the
build. It holds a version and a date and nothing else. The build performs no file operation on it,
because disposing of a `scratch/` entry is the clinician's decision per file.

### 8. ADR 0083's false fact is corrected in place, and ADR 0216 is not edited

ADR 0083 ruling 5 stated a fact that was false before anything overturned it, and
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
licenses correcting a ratified record's facts in place. A dated line sits beneath ruling 5 and beneath
the *What none of it reaches* paragraph naming the trust gate, stating what could not be reached and
why, and naming this record.
[ADR 0216](0216-a-pre-grade-grades-the-exact-publication-command-and-the-aar-quotation-gate-runs-on-it.md)
ruling 7 defined the marker as the hook invoked on a publication; that was true when written, this
record overturns it in part, and it is left unedited as #1201's question. That ruling's refusal to
write the marker from a pre-grade stands. **Marking both was declined**: it decides #1201 inside this
ticket.

## Taken as conventions, not ruled

- A failed record write never changes the hook's decision or the stub's response.
- The shared write helper lives in a module the stub can import without importing `phi_scan`.
- `tracker_publish_hook --command-file` writes no record, per ADR 0216 ruling 7.
- The record's schema version rises so that a reader cannot mistake the retired file's shape for it.
- The identity-to-filename encoding and the subdirectory name are the build's.

## Consequences

- `tracker_publish_stub` and `tracker_publish_hook` both write the per-checkout record first;
  `write_marker()` after the grade in `handle` is removed.
- `phi_scan.tracker_publish_notice` reads the committing checkout's record and prints the ruled
  wording.
- `test_the_hook_marker_is_dated_and_contains_no_tracker_text` and the notice tests in
  `test_phi_scan.py` change deliberately, and the tests that patch `write_marker` follow the new
  helper.
- `CLAUDE.md`'s **Tracker publish hook** paragraph is corrected now to state what the marker does
  today and to name this record; the build rewrites it to the ruled mechanism.
- `tracker_publish_hook.NOT_REACHED` gains the rows below that concern the marker.
- #1151 is respecified against these rulings and flipped to `ready-for-agent`.

## What this does not reach

**A commit made outside a session.** No hook runs, so the notice reads never or an older date, which
is correct and says nothing about registration.

**The checkout a command ran in.** The record belongs to the checkout whose hook module ran, which is
the session's project directory. A session that changes into a sibling worktree and commits there
reads that sibling's record, not its own.

**A session started with hooks disabled or with `--settings` overriding the project block**, where the
record only ages, as ADR 0083 already names.

**Publish time.** The record is a notice at commit time and never a guarantee at publish time; a
checkout can register, commit, and later lose its trust acceptance.

**A moved or renamed checkout**, which derives a new identity and reads never until its hook runs.
