# Approved-run status

Apply this contract after `assignment_submission.stage` records approval for either
course-assignment branch. Every reply that touches the open run ends with exactly one current line:

```text
Run status: awaiting upload
Run status: awaiting posted reading
Run status: awaiting AAR
Run status: stopped - <reason>
Run status: complete
```

Use `awaiting upload` from approval until either upload route is recorded, `awaiting posted
reading` until the downloaded posted artifact has been read, and `awaiting AAR` until the
after-action review and terminal grade are clean. A posted-reading divergence, Composer refusal,
or clinician decision not to submit this version uses `stopped - <reason>`. That run stays stopped
until it completes or another approval is recorded; there is no separate close action.

Use `complete` only after the artifact-aware `--submission` grade exits 0. That clean completion
closes the approved run, so later replies need no status line unless another approval opens it.
