# Approved-run status

Apply this contract after `assignment_submission.stage` records approval for either
course-assignment branch. Every reply that touches an open run ends with one line naming that run's
key. When a reply touches several open approved runs, give each one a line in a final contiguous
block:

```text
Run status: <run-key> — awaiting posting
Run status: <run-key> — awaiting posted reading
Run status: <run-key> — awaiting AAR
Run status: <run-key> — stopped - <reason>
Run status: <run-key> — complete
```

Use `awaiting posting` from approval until either posting route is recorded, `awaiting posted
reading` until the downloaded posted artifact has been read, and `awaiting AAR` until the
after-action review and terminal grade are clean. A posted-reading divergence, Composer refusal,
or clinician decision not to submit this version uses `stopped - <reason>`. That run stays stopped
until it completes or another approval is recorded; there is no separate close action.

Use `complete` only after the artifact-aware `--submission` grade exits 0. That clean completion
closes the approved run, so later replies need no status line unless another approval opens it.
A run holding several approved items reports the item furthest behind and reaches `complete` only
when every item grades clean. Never put a classmate or patient name in the line.
