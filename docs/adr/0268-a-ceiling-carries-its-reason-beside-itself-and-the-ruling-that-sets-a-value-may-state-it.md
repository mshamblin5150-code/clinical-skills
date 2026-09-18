# A ceiling carries its reason beside itself and the ruling that sets a value may state it

**Measured at:** 5b13b9705d13a5e342b53428f31af962fec1de63

[#1160](https://github.com/mshamblin5150-code/clinical-skills/issues/1160) was filed out of
[ADR 0192](0192-a-ceiling-names-a-relationship-and-a-count-sits-beside-what-it-counts.md)'s own
grilling, which found `RULING_EXEMPT_CEILING` violating that record's ruling 2 and deliberately did
not repair it. Grilled against `main` at `5b13b970`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is the
record the build reads.**

## Measured before ruling, at `5b13b970`

Driven through the gate's own reader over `graded_files()`:

```python
import test_skill_agreement as t
sum(s.declared
    for p in t.graded_files()
    for s in t.marker_exemptions(t.read(p), t.RULING_EXEMPT_MARKER))
```

*Under the hatch being full that prints 2; it printed 1.* The one declaration is in
[ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md),
the only graded file carrying the marker. `RULING_EXEMPT_CEILING` is `2` and has no comment of any
kind; every other ceiling in `tools/test_skill_agreement.py` carries one.

`git grep -n "ceiling of 2" docs/adr/` returns three records, not the two the ticket body names:
[ADR 0075](0075-a-ruling-ordinal-has-one-referent-addenda-continue-the-numbering-and-the-citation-resolver-is-a-third-walker-joining-against-the-record-s-own-list.md)
ruling 7, which set the value;
[ADR 0128](0128-a-read-once-cache-of-a-committed-reference-file-gets-a-public-reset-and-a-declared-limit-and-the-pattern-is-not-generalized.md)'s
*What this record does not settle*, which restates the digit and adds the live slack; and ADR 0192's
own *What this record does not settle*, which quotes both. ADR 0192 also carries a table row giving
the slack, under its dated *Measured before ruling* heading. [ADR 0133](0133-a-ruling-is-identified-by-its-ordinal-and-an-empty-parse-is-declared-rather-than-guessed-at.md)
cites the constant as a precedent and states neither figure. Both sweep comments on #1160 found the
ADR 0192 limb; this record adopts it.

**Two of those four sentences are carried claims and two are not, and the rulings below turn on that
split.** A sentence written in the present tense outside a dated measurement goes false without any
edit the moment the thing it describes moves; a dated measurement is true of its date and is
superseded, never corrected, under
[ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md) ruling 3.

## Ruling 1 — the constant carries its reason and a pointer, and no count

`RULING_EXEMPT_CEILING` gains a `#:` comment block stating the relationship — a deliberate mention
is a declared count and not an opt-out, and the ceiling sits just above what is declared, so an
exemption past it has to be argued for in a diff rather than typed — and citing ADR 0075 ruling 7 as
the record that set it.

**The comment states no number of declared exemptions and no ordinal.** The declared count lives in
ADR 0048, a file sharing no diff with the constant, so ADR 0192 ruling 2 forbids restating it here;
and ADR 0192 ruling 1 forbids naming the refused exemption by its ordinal. The comment is the live
copy of the reason. ADR 0075's paragraph is the decision and remains history, so the two are not
competing copies of one claim.

Pointer-only was refused because it leaves a reader at the constant with no reason in front of
them, which is the defect. Reason-only was refused because it loses the join to the record that set
the value.

## Ruling 2 — ADR 0128's clause is corrected in place, and ADR 0192's table row stays

ADR 0128's clause sits in *What this record does not settle*, in the present tense, outside its
dated measurement block, so it is a carried claim. It is edited where it stands to name the constant
with no digit and no slack — the natural way to cite one of those records by ordinal is unresolvable
except through the ruling hatch, whose limit is `RULING_EXEMPT_CEILING` — and a dated line
directly beneath records what it said and cites #1160.

**The dated line paraphrases the retired clause rather than quoting it**, saying it named the
ceiling's digit and a count of slots already spent. Quoting it verbatim would put the retired phrase
back into the one file ruling 5's bind refuses it in.

ADR 0192's slack row is under *Measured before ruling, at `9c78d3f`*. It is a dated reading and is
left exactly as written.

## Ruling 3 — the ruling that sets a value may state it, and nothing else may

ADR 0075 ruling 7 states the digit, and it is the deciding paragraph, which
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
makes untouchable. **ADR 0192 ruling 2 governs live counts.** A ruling that sets a value and states
the value it set records what was decided on its ratification date; a later change to the value
makes that sentence history rather than false, and the live value is always the constant's.

The carve-out is exactly that narrow. It covers the setting ruling alone. A record that restates a
value some other record set — ADR 0128 here — gets no cover from it, which is why ruling 2 corrects
that record and leaves ADR 0075 untouched. No dated pointer is added to ADR 0075: the constant's
comment already joins the value to its reason, and a line at the foot of ADR 0075 would be a fourth
place the arrangement is described.

## Ruling 4 — ADR 0192's unsettled paragraph is corrected in place and marked settled

ADR 0192's *What this record does not settle* paragraph on this ceiling says, in the present tense,
that the constant carries no comment, and quotes ADR 0128's clause. After the build both are false.
Its present-tense claims are anchored to that record's ratification — the constant carried no
comment when it was ratified — and its quotation stays a quotation of what ADR 0128 said then. A
dated line directly beneath records that this record settled it.

**The paragraph's own decision stands untouched**: that record chose to file this rather than
repair it, and that choice is history.

## Ruling 5 — two regression binds, declared as a floor

Beside `ACeilingsProseNamesNoOrdinal`, and on its reader:

- `comment_block(SELF, "RULING_EXEMPT_CEILING")` is non-empty and names ADR 0075 ruling 7, so the
  silent constant cannot return.
- ADR 0128 no longer carries the retired clause, asserted with `assertProseNotIn`, so a revert or a
  merge cannot restore it.

**Both reach only those exact shapes, and the docstring says so.** A reworded slack claim anywhere
else escapes them. A detector over prose is not re-proposed: ADR 0192 measured every widening of
`test_constant_prose_counts` and none reached a defect of this kind. Each bind is driven red by
mutation before it is believed, and the liveness control for the comment block is driven through the
reader rather than built from an inline string, on ADR 0192 ruling 3's finding.

## Rejected options

**Raising `RULING_EXEMPT_CEILING`.** Nothing here is refused by it, and moving a ceiling to meet what is on disk retires the check rather than discharging it.

**Adding a ruling-exemption marker.** Nothing here needs one.

**Correcting ADR 0192's dated slack row.** That would treat a dated measurement as a carried claim,
which is the distinction ADR 0191 ruling 3 exists to keep.

**Relying on a bind instead of correcting ADR 0128.** Nothing mechanical can tell when a live slack
figure has gone false, so a bind cannot hold the clause true; it can only refuse its return once it
is gone.

## What this record does not settle

**Whether any other record restates a value it did not set.** The carve-out in ruling 3 names the
class; this record corrected the members #1160 and its sweeps found and ran no census of the rest.

**Every ceiling and baseline in `tools/`.** ADR 0192 declined that sweep and this record does not
reopen it.
