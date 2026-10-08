# A refused-code clause opens its own sentence and its semicolon only joins two clauses

**Measured at:** 24651010bb5722d24b564bc12859d9e669c28955

[#1472](https://github.com/mshamblin5150-code/clinical-skills/issues/1472) and
[#1599](https://github.com/mshamblin5150-code/clinical-skills/issues/1599) were filed from two
after-action reviews of NUR5144 `batch-shift` runs. In each, `tools/entry_copy.py` removed a welded
`NOT CODED: <code> <descriptor>, <reason>` clause and left part of the sentence around it in the
Entry copy, and every check passed. Grilled 2026-10-08 against `main`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session and #1472 was widened to carry both.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The semicolon already bounds a clause in three places.** `skills/clinical-note/SKILL.md` says the
semicolon is what bounds a refusal and its reason.
[ADR 0254](0254-the-note-entered-in-medatrax-is-a-derived-entry-copy-and-its-plan-takes-four-labels.md)
ruling 3 says the clause is cut at its own bounds, which the welded form and its semicolon separator
already fix. `tools/differential_scan.py` ends a clause at the next `;` or the end of its line, and
`tools/entry_copy.py` ends it at the next `;` or sentence-ending period.

**#1472's shape.** A second welded clause whose reason held an internal semicolon was cut at that
semicolon, and the rest of the reason stayed in the Entry copy, where it read as describing the
entry's favored diagnosis:

```
Note:   ... NOT CODED: J18.9 Pneumonia, unspecified organism, no infiltrate on exam; NOT CODED: J20.9 Acute bronchitis, unspecified, cough under three days; a chest film would establish it.
Entry:  ... a chest film would establish it.
```

**#1599's shape.** A clause hung off a lead-in ending in a comma and a conjunction left the lead-in
stopping mid-sentence:

```
Note:   No endometrial sampling and no imaging this visit, so NOT CODED: N85.00 Endometrial hyperplasia, unspecified, a biopsy showing it would earn it.
Entry:  No endometrial sampling and no imaging this visit, so
```

**The skill's own worked example carries both.** The `Final diagnosis` example in
`skills/clinical-note/SKILL.md` writes `..., so NOT CODED: J13 Pneumonia due to Streptococcus
pneumoniae; an organism-specific result would earn it.`, a lead-in and a reason after a semicolon,
and the Entry copy derives `Nothing tested for the organism, so an organism-specific result would
earn it.` That residue is an ordinary-looking sentence, so a check for a lowercase sentence start
would pass it. The same shapes stand in preserved run records under `fixtures/`.

**The committed material otherwise follows the rule below.** Over tracked Markdown, outside inline
code mentions, a welded clause opens a line or follows a period or another clause's semicolon in
every instance but the lead-in shape above. No committed note or skill opens a clause after a
semicolon that follows anything other than another clause. One synthetic note in
`tools/test_entry_copy.py` does, and its expected Entry copy keeps a trailing `J18.9;`.

## Ruling 1 — a clause's semicolon only joins it to the next clause, and the Entry copy enforces it

A refusal's reason never contains a semicolon. A clause that ends at a semicolon must be followed,
after whitespace, by another welded `NOT CODED:` clause; otherwise `tools/entry_copy.py` refuses the
note, writes no copy, and exits nonzero, in its derive and `--check` routes alike. A reason that
needs two parts joins them with a comma and a conjunction or is split into its own sentence after
the clause. ADR 0254 ruling 3 stands unchanged, and `tools/differential_scan.py` keeps its bound.

Ending a clause at the next welded mark or the sentence's end instead was declined. It overturns ADR
0254 ruling 3, makes `differential_scan` and `entry_copy` read one clause two ways unless both move,
and only moves the ambiguity to where a sentence ends inside a reason. A general refusal of a
lowercase sentence after a stripped span was declined as the primary rule because it is a guess,
and the skill's own example shows a residue it would pass.

## Ruling 2 — a clause opens its own sentence, and the Entry copy enforces it

A welded clause opens at the start of a line, after any indentation, blockquote marker or list
marker, or after a sentence-ending period, or after another clause's joining semicolon. Any other
text before it on its line, such as a lead-in ending in a comma or a conjunction, or a semicolon
after a diagnosis, makes `tools/entry_copy.py` refuse the note on the same terms as ruling 1. The
synthetic note in `tools/test_entry_copy.py` that writes `Pneumonia - J18.9; NOT CODED: ...` is
therefore refused, and its expected Entry copy is rewritten.

Allowing lead-ins and refusing only a residue ending in a comma or a coordinating conjunction was
declined because a lead-in such as `therefore` passes it. Cutting the lead-in back to the previous
sentence end was declined because it silently removes the clinician's own reasoning from the text
entered in Medatrax. The finished note loses the `so` that tied a finding to its refusal; the order
of the two sentences still carries it.

## Ruling 3 — the skill states both rules and its worked example is rewritten

`skills/clinical-note/SKILL.md` states rulings 1 and 2 beside the welded form, and its `Final
diagnosis` worked example becomes
`Nothing tested for the organism. NOT CODED: J13 Pneumonia due to Streptococcus pneumoniae, an
organism-specific result would earn it.` Preserved run records are not edited, and notes already
posted to Medatrax are not corrected.

## What this does not reach

Coding worksheets carry the same welded form but are never stripped or entered, so neither rule
applies to them. A residue that the two shapes do not produce, such as a clause cut correctly from a
sentence whose remainder still misleads, stays the reading at approval. Whether a reason is
clinically right is unchanged by either rule.
