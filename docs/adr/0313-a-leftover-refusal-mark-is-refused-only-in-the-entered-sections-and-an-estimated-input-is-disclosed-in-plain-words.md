# A leftover refusal mark is refused only in the entered sections and an estimated input is disclosed in plain words

**Measured at:** 290acba60ab8fa0b0af073fe1ba273e7d4a1cd34

[#1477](https://github.com/mshamblin5150-code/clinical-skills/issues/1477) was filed from the
after-action review of a NUR5144 `batch-shift` run (shift of 2026-09-30). Two note passes reported
independently that `skills/clinical-note/SKILL.md`'s worked drift-row-20 disclosure contradicts
drift row 12 and the Entry copy. A tracker sweep after
[ADR 0307](0307-a-refused-code-clause-opens-its-own-sentence-and-its-semicolon-only-joins-two-clauses.md)
added that the skill's advice on mentioning the `NOT CODED` mark is false for the Entry copy.
Grilled 2026-10-09 against `main`, where the freshness gate read `FRESH`; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The note file holds more than what is entered.** A finished note carries its four Note sections
and, around them, the tier block and the drift check. Only the four sections become the Form
sections typed into Medatrax. `tools/entry_copy.py` nonetheless refuses a `NOT CODED` mark that
survives anywhere in the stripped copy, in any letter case, while its check for clinician-directed
instructions such as `before entry` already reads only the four sections.

**The skill instructs the shape the Entry copy refuses.** The `clinical-note` paragraph opening "So
when a note talks *about* the mark rather than making one, put it in backticks" says a backticked
mention costs nothing and that a drift matrix row is already safe. Driven through
`entry_copy.check` at the commit above, a backticked mention in a drift-check table row and a
lowercase mention in a GAPS line are both refused with `NOT CODED mark survived Entry copy
derivation`; a welded clause in the Assessment derives. That advice holds for
`tools/differential_scan.py` and not for the Entry copy.

**The committed real notes carry the refused shape.** Read with the Plan-label check set aside, three
of the six notes in `fixtures/slot-form-run` are refused for a surviving mark and for nothing else
the Entry copy reads. In each, every surviving mark sits outside the four Note sections, in the
drift table's row-22 verdict. The other three are refused earlier on ADR 0307's clause grammar.
Under this record's ruling 1, the mark limb would refuse none of the three.

**The disclosure example breaks three rules at once.** It writes "a filled height" and "derived",
which drift row 12 bans from the note body; it ends "Confirm the measurements before entry.", which
the skill's process-commentary rule bans and the Entry copy refuses in section A. The conflict is
between the rows and not only in the example: drift row 20 requires the note to name which inputs
were filled, and row 12 bans the words that named them. Both passes in the run and the orchestrator
reached "estimated", "measured" and "computed". The skill already uses "estimated" this way for
visit start and end times.

## Ruling 1 — the leftover-mark refusal reads only the four Note sections

`tools/entry_copy.py` refuses a `NOT CODED` mark, in any case, that survives clause removal inside
any of the four Note sections. A mark in the preamble, the tier block, the drift check or any other
text outside those sections is not refused for being a mark. The refusal names the section and
quotes no note text, as the clinician-instruction refusal already does, and it still writes no copy,
removes any prior derived copy, and exits nonzero in the derive and `--check` routes alike. Where
the four sections cannot be read, the whole copy is checked as today, so a note whose structure is
unread is never passed on the narrower read.

Refusing the words everywhere in the note and rewriting the skill to avoid them was declined: every
run would have to work around the vocabulary of the row it grades, and two passes in one run tripped
on it. Making the Entry copy hold only the four sections was declined as a larger change to what the
Entry copy is, for the same protection.

## Ruling 2 — the skill's mention advice is rewritten to match both readers

The backtick paragraph in `skills/clinical-note/SKILL.md` is rewritten. Inside the four Note
sections the mark appears only as a welded clause; a backticked or lowercase mention there is still
refused by the Entry copy. Outside them, a mention in backticks costs nothing for either
`tools/differential_scan.py` or the Entry copy, and a pipe-table row needs no backticks. The line
#1477 proposed, never writing the phrase anywhere outside a welded clause, is declined with ruling
1's first alternative.

## Ruling 3 — an estimated input is disclosed as estimated, not filled

The worked drift-row-20 disclosure becomes:

```
E66.3 and Z68.26 rest on an estimated height of 5'10" and an estimated weight
of 185 lb; neither was measured, and the body mass index of 26.5 is computed
from the two.
```

It carries no instruction to confirm anything before entry; that belongs to the tier block. Drift
row 12 gains a sentence: the drift-row-20 disclosure may say an input was estimated and not
measured, and may not use a tier word or instruct the clinician. Drift row 20 and the prose beside
the example say the line names which inputs were estimated rather than measured, in place of which
were filled. A midpoint age month filled for a pediatric `Z68.5-` is disclosed the same way. The
tier block keeps its own vocabulary unchanged. Preserved run records are not edited, and notes
already posted to Medatrax are not corrected.

Keeping the tier words in this one line as an exception to row 12 was declined because it puts the
skill's own vocabulary into the submitted note and invites the exception elsewhere. Moving the
disclosure into the tier block alone was declined because it reverses
[#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46): the entered note would show
the codes as though the measurements were observed.

## Supersedes

- [ADR 0254](0254-the-note-entered-in-medatrax-is-a-derived-entry-copy-and-its-plan-takes-four-labels.md)
  ruling 3, its refusal when any `NOT CODED` mark survives anywhere in the output. Ruling 1 narrows
  it to the four Note sections. The committed command, its clause bounds, the no-copy refusal and the
  portal readback stand.

## What this does not reach

Whether a mark outside the four sections is a correct statement about the note is unchanged, and
`tools/differential_scan.py` keeps reading the whole note. Whether "estimated" is clinically the
right word for a particular value, and whether the estimate itself is plausible, stay readings under
drift rows 19 and 20. Coding worksheets are never stripped or entered, so ruling 1 does not apply to
them.
