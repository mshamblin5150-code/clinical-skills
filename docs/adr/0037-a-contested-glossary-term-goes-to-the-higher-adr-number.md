# A contested glossary term goes to the higher ADR number
<!-- no-numbered-rulings -->

Two grilling sessions coined the same `CONTEXT.md` term for two different things. [ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md) defined **Recommendation record** as *one recommendation lifted out of a guideline*; [ADR 0034](0034-a-recommendation-record-is-resolved-by-exact-name-at-both-read-sites-and-the-directory-scan-hints-rather-than-selects.md) defined it as *the machine-readable extraction of one guideline document's recommendations* — a unit and the file that holds many of them.

Ruled by the clinician on 2026-08-26 while merging four unmerged ADR branches. **Nothing is built here; this is the record the next collision reads.**

## It was going to land silently

Both records sat on unmerged PRs (#514 and #517). Merged virtually with `git merge-tree --write-tree` **before** either was landed:

```
merged tree duplicate term headings: Declared limit, Recommendation record, Underived count
  line 242  **Recommendation record**:  The machine-readable extraction of one guideline document's...
  line 308  **Recommendation record**:  One recommendation lifted out of a guideline by...
```

**Git merges it clean — exit 0, no conflict** — because the two definitions land in different sections of the file. Both glossary readers resolve by first occurrence (`test_glossary_vocabulary.py` and `test_ruling_cohort.py` each call `.index(term)`), so one definition wins and the other becomes text nothing reads.

That is [#499](https://github.com/mshamblin5150-code/clinical-skills/issues/499)'s *byte-identical merge* mechanism one degree worse. #499's two duplicated terms are byte-identical, so the duplication is redundancy. These two **disagree about what the term means**, and the disagreement is invisible to git, to the suite and to a reader who stops at the first entry.

## Ruling — the higher ADR number takes the term

Where two ratified records define one `CONTEXT.md` term differently, the record with the **higher number** owns it.

The ground is how ADR numbers are handed out. `tools/adr_next.py` allocates the next free number at the moment a grilling writes its record, so the number is chronological by construction. And a grilling session is not an isolated act: it sweeps the tracker, reads the open tickets and posts on them before it rules. **The later session has read the earlier one's ticket and the earlier one has not read the later one's.** In the clinician's words, *"by the time i get to a later adr i am more informed, so that one wins."*

So the rule is not a tie-break by convenience. It selects the reading taken with more of the tracker in view, and it is decidable from the two file names without reading either record.

### The losing concept keeps its meaning and gets its own name

The rule settles which definition keeps the **term**. It does not delete the other **concept**. Both survived here: a threshold row cites one recommendation by `rec_id`, and `threshold_sheet.bind_recs` resolves a file. Two things, two entries.

ADR 0032's concept is now **Recommendation**, which is what `tools/guidelines_recs.py:276`'s `@dataclass(frozen=True) class Recommendation` already calls it, and it joins `Recommendation label` and `Dropped recommendation` in the glossary rather than standing alone. `entry` was the other candidate and was refused: ADR 0032's own `_Avoid_` line names `entry` as a word to push away from, and overruling a record's stated avoidance to solve a collision it did not cause is the wrong direction.

### ADR 0032's prose needed no edit, which is the finding rather than the fix

Both of its two uses of the phrase are the **file** sense — `:4` *"builds every recommendation record through a raw PyMuPDF read"* and `:160` *"Every stamped recommendation record is rebuilt… a `recs-<key>.json` is a build artifact"*. So the record's prose already agreed with ADR 0034, and only the glossary entry it contributed carried the unit sense.

**The entry was out of step with the record that wrote it, from the moment it was written.** Nothing catches that: a term's definition and the prose of the ADR contributing it are never compared, and neither `CONTEXT.md` reader looks at an ADR at all.

## What this does not reach

**Nothing detects a collision.** This rule tells a person which definition wins once someone has noticed two. Both readers take the first occurrence, so on `main` today the winner is decided by **file position** rather than by ADR number — it happens to agree here, and it agrees by luck. A duplicate-term check is #499's, and this ruling gives that check a resolution to apply rather than only a failure to report.

**It reaches `CONTEXT.md` terms and nothing else.** Two records disagreeing about a *ruling* rather than a *term* is a different problem: the later one supersedes on the same reasoning, but supersession is stated in the record, and nothing here changes that.

**Number order is not merge order.** A lower-numbered ADR can merge after a higher one, as three did on 2026-08-26. The rule keys on the number because the number records when the ruling was *made*, and that is what carries the better-informed claim; merge order records only when somebody got round to pressing the button.
