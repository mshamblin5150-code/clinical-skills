# A run is keyed to the board, and the date is provenance rather than identity

[#399](https://github.com/mshamblin5150-code/clinical-skills/issues/399) shipped `scratch/runs/<course>-<module>-<date>/` for the discussion-reply skill. Grilling [#416](https://github.com/mshamblin5150-code/clinical-skills/issues/416) on 2026-08-22 established that the date makes the key a **sitting** — one visit to the board — when the thing being graded is the **board**.

The clinician ruled the date out of the directory name on 2026-08-22. The key is `scratch/runs/<course>-<module>/`.

## What the dated key costs

An initial post and its replies are one graded conversation and are almost never written on one day. Under the dated key they land in two directories:

```
scratch/runs/nur5042-m2-2026-08-24/   claims.md   the initial post's references
scratch/runs/nur5042-m2-2026-08-27/   claims.md   the replies', knowing nothing of the above
```

Three consequences, and the third is the one that mattered.

**The reply run cannot see the post's ledger.** So a source verified three days earlier is re-researched from scratch, which is [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect — spending work to refuse a property the rule does not care about.

**`discussion_reply_scan.py`'s `respent-source` row can only ever be half a check.** It compares reply against reply because a reply-only run is all it could see.

**And [#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417)'s join key joins half the board.** That ticket exists because nothing joins a run's output to the ledger that produced it; a key that changes between the post and its replies reproduces the problem inside the fix for it.

## What was measured

`scratch/runs/` **did not exist** when this was ruled. Zero runs had been written on #399's convention, so the migration cost was nil on 2026-08-22 and rises with every board from then on. That is the whole reason this was ruled immediately rather than folded into #417.

## Considered options

**Keep the date.** Rejected. It is a fact about when somebody sat down, and identity should be the thing being graded. Its one genuine advantage is below.

**Keep the date and have `discussion-reply` locate the most recent prior run for the same course and module.** Rejected as the fallback rather than the answer. It preserves a landed skill untouched and buys the same join, at the price of a lookup rule that has to define *most recent* and fails silently when it picks wrong.

**Drop the date, version the snapshot.** Adopted. The date does not vanish; it moves to where it belongs — `board-<date>.md` per sitting, and `RESOLVED: <url> - read <ISO date>` already carries it per claim.

## The cost this accepts

A second sitting writes into a directory that already holds a board snapshot. #399 made the board authoritative **because** it holds edits, so overwriting the first snapshot would destroy the evidence of what a classmate had said when the post was written. Versioning the snapshot per sitting is the price of the board-keyed directory, and the dated key did not have to pay it.

**The key gained a third component on 2026-08-22 — see [ADR 0010](0010-a-run-is-keyed-to-the-graded-artifact.md).** `scratch/runs/<course>-<module>/` as written below is one component short: a module holds several graded artifacts, so the key is `<course>-<module>-<artifact>`. Nothing else in this record is retracted, and the ruling it makes was applied a second time by #417 to put the date on the submission filename. This pointer is an annotation rather than an amendment; the text stands as it was ruled.

`skills/discussion-reply/SKILL.md` carries the date in its run-key derivation, its path examples and its completion step. Those are text edits with nothing behind them to migrate, and they are owed to this decision rather than to #416's own build.
