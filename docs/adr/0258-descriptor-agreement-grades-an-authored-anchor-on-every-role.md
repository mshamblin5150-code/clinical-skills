# Descriptor agreement grades an authored anchor on every role

**Measured at:** 87dacf50461d08e2480616148d8ff69829ac82ab

[#1355](https://github.com/mshamblin5150-code/clinical-skills/issues/1355) was filed from the
2026-09-17 repair of six unsubmitted NUR 5144 shifts, where five blind descriptor-agreement reads
needed a second pass each and three independent readers described the same failure in the same
words. Grilled 2026-09-17; the clinician ruled every point below the same day. Freshness gate
`FRESH` at `87dacf50`. Nothing is built here; this is the record the build reads.

The ticket asks whether the blind brief withholds too much and whether the finding should name the
row's role. Both are real, and neither is the defect. ADR 0243 ruling 10 requires the reader's words
to occur verbatim in the note *and* inside the worksheet line's quotation, and for two of the four
roles no such quotation has ever existed.

## Measured before ruling

### The report names nothing at all

`_agreement_report` builds each finding, counts it by substring, and never prints it; neither
agreement mode takes `--show`. Driven at `87dacf50` over the committed positive control with one
differential row's `agreeing_words` replaced by a span present in the note and absent from its
support:

```
  codes read                           20
  agreement findings                 1
    non-verbatim agreeing words       1
```

Exit 1, and no code named. So the ticket's second limb understates itself: the reader is not told
which of a code's rows failed because it is not told which code failed, and `subject.code` becoming
`subject.key` changes nothing observable. No test asserts any finding string, which is consistent,
because none reaches stdout.

The default report is nevertheless not counts-only already. `unread cross-reference {stem}: {code}:
{referral}` prints ungated, and `test_anchor_scan.AgreementModes` pins that text.

### The support is two objects, and only one of them is a quotation

`skills/icd10-cpt/SKILL.md` rules, for a differential, that **anchor is the differential entry
itself, named rather than re-quoted**. Across all 17 committed worksheets there is no `ANCHOR:` line
below a differential or refusal heading. `_preceding_support` substitutes the nearest non-blank line
above the code, which is authored rationale prose. No record rules that substitution.

Longest verbatim run the support shares with its note, as a fraction of the support:

| set | role | rows | support wholly in note | mean shared/support |
| --- | --- | ---: | ---: | ---: |
| positive-control | entry | 9 | 9 | 1.00 |
| positive-control | differential | 8 | 0 | 0.18 |
| positive-control | refused | 3 | 0 | 0.28 |
| negative-control | entry | 11 | 11 | 1.00 |
| negative-control | differential | 7 | 0 | 0.19 |
| note-path-control | entry | 5 | 5 | 1.00 |
| note-path-control | differential | 5 | 1 | 0.91 |
| note-path-control | refused | 3 | 3 | 1.00 |
| index-table-control | entry | 3 | 3 | 1.00 |

Entry anchors are verbatim note text 28 times out of 28. Differential supports are 1 of 20, refused
3 of 7. Per row, the run a differential reader can reach is the authored diagnosis label at the head
of the rationale line, which the same pass wrote into both documents. That is **Shared-reader
blindness** on two of four roles.

### `filled-anchor/run-2` is not an agreement pair, and its rows are set aside

Covering each entry anchor with maximal runs of its paired note:

| set | covered by 1 run | 2 to 3 runs | 4 or more |
| --- | ---: | ---: | ---: |
| the four controls | 28 of 28 | 0 | 0 |
| `filled-anchor/run-2` | 57 of 106 | 20 | 29, up to 11 runs |

An anchor needing eleven separate runs was not copied from that note. Separately, `run-2` carries
200 entry rows of which **94 carry no `ANCHOR` at all**, and an empty support makes the containment
test true for every possible span, so those rows are guaranteed findings if anything grades them.
Nothing does. Every one of the 94 is in `run-2`; the four controls are clean. Collapsing whitespace
moves `run-2` only from 57 to 66, so the gap is the pairing rather than line wrapping.

### The reader's difficulty is where, not how much

Across the controls' retained reader records, 51 passing spans: median 26 characters, a median of
**25%** of the support, 39 strict subsets against 12 exact matches. Readers under-quote. Accepting a
superset would address a direction they do not err in, and would need an upper bound to stop a
whole-note span passing.

### Nine rows in ten take a route that checks nothing

`_route_status` returns `VALID` for `descriptor words` before reading anything else.

| role | `descriptor words` | index route | `none` |
| --- | ---: | ---: | ---: |
| entry | 22 | 5 | 1 |
| differential | 18 | 0 | 2 |
| refused | 7 | 0 | 0 |

47 of 52 routed rows take the unconditional branch, and no differential or refused row has ever
taken the other one. For those rows the whole mechanical check is the containment.

A shared content token between the span and the official descriptor was measured as the candidate
gate: **7 of the 47 accepted rows share none**, 3 differential and 4 entry, every one written by a
blind reader and accepted by a non-authoring check.

### Notes here are not hard-wrapped

Longest note lines run 510 to 2,153 characters, and whitespace collapsing changes no control's
result (9 of 9, 11 of 11, 5 of 5 either way).

### What the rule reaches

The grader reads 84 differential and 46 refused rows over the 17 worksheets. Of those, **27 are in
the three controls** and the remaining 103 are in `run-2`, set aside above. Three `run-2` files write
the headings as `### --- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---`, which neither
`DIFFERENTIAL_HEADING` nor `REFUSAL_HEADING` matches.

## Ruling 1 — a differential row and a refusal row carry an authored anchor

Each gains `ANCHOR: "<verbatim note text>"`, the field an entry already carries, and that quotation
is the support for every graded role. `_preceding_support` stops being the support for anything.
This reverses *named rather than re-quoted* in `skills/icd10-cpt/SKILL.md` for the agreement pass and
makes ADR 0243 ruling 10's own words true for all four roles.

The anchor line is placed immediately after the last physical line of the entry header and before
any other field. `worksheet_grammar.FIELD` includes `ANCHOR` and `entry_is_for_entry` closes the
header at the first field match, so an anchor after the first physical line of a wrapped descriptor
would flip that entry to for-entry; four committed rows are exposed to that. Placing it last instead
would move `_preceding_support` for 22 neighboring differential rows while the fallback still
exists.

A refusal's anchor quotes the note text naming the considered diagnosis rather than an awaited
study. That follows from ADR 0243 ruling 1 and is a briefing line for the skill, not a new rule; no
grader can hold it, because every refusal row routes through `descriptor words`.

## Ruling 2 — the read prints its findings under `--show`

Both agreement modes gain `--show`. Under it each finding prints keyed on `subject.key`, the string
the brief already tells the reader to copy, so a finding joins to the record without inference and
carries the occurrence index as well as the role. Bind findings name the symmetric difference rather
than only the label. The ungated `unread cross-reference` line moves behind the same gate, and the
module docstring stops claiming a posture the code does not keep.

The default report stays counts-only and pasteable. Making the whole report PHI was declined: the
counts are the part worth pasting into a ticket, and the coordinator is the non-authoring context
standing rule 6 already requires, which every sibling grader hands PHI under `--show`.

## Ruling 3 — an anchor is one contiguous verbatim run of its note

A support that is not is a finding. Every graded row then has a support wholly inside the note, so
any span of that support passes and no row can be unreachable. This closes the case the ticket's own
closing section says a fix must serve, where the support contains nothing the note also contains.

The comparison is raw rather than whitespace-collapsed, and the reason is transitivity rather than
the measurement: the reader's span check is raw, so a raw-verbatim support guarantees a raw-verbatim
span for free, while normalizing only the anchor side lets a row be accepted whose reader span then
fails as absent from the note.

Without this, ruling 1 would re-create the defect it repairs. Nothing would stop the authored
diagnosis label being written into the new anchor field, and the check would pass on the author's own
words wearing a quotation's clothes.

## Ruling 4 — the finding splits, and no figure derived from the support is echoed

`words not in pair.note or words not in subject.support` becomes two findings: the span is not the
note's words, or it is the note's words from the wrong place. The reader learns which error it made
and learns nothing about the support's length, extent, wording or position.

The ticket's echo proposal is deferred rather than refused. Its five stuck rows resolved on a
diagnostic, and the ticket also records why they were stuck: every one of those supports began with
the code's official descriptor, which is the rationale line ruling 1 abolishes and ruling 3 forbids.
Under rulings 1 and 3 the leading shared run becomes the whole support, so echoing its length and
first token is disclosure of the support one failure late; first token plus length already determined
a passing span on 35% to 62% of rows before ruling 3 guaranteed the support is note text. The bar for
reopening it is a shift graded after rulings 1, 3 and this split still showing a two-pass loop.

Accepting a superset was declined on the 25% median above: it serves a direction readers do not err
in, and bounding it needs a cut point nobody can ground.

The split's benefit is unmeasured. It is ruled on its shape, being the one information gain drawn
from nothing but the reader's own submitted string.

## Ruling 5 — the unconditional descriptor-words route stands and is declared

`anchor_scan.DECLARED_LIMITS` gains a row: on a `descriptor words` route a clean result establishes
that the reader's span is note text the worksheet also quotes, and not that those words state the
descriptor. The skill's completion prose stops implying the stronger claim.

Grading it was declined on the 7-of-47 false alarm above, which is `case_study_scan`'s
`no-stop-criterion` defect and a direction this repository has already ruled. Forcing an index route
wherever one exists was declined as incomplete by construction, because ADR 0243 ruling 12 leaves CPT
and HCPCS without an index.

After rulings 1 and 3 the pass is strictly a co-location test against a guaranteed-reachable target.
That is worth keeping and worth saying: what it proves is that an author's anchor is independently
findable from the note and the descriptor, which is the failure #1139 was filed over.

## Ruling 6 — the loop is bounded by an action rather than a count

The reader retries. Still failing, the author widens that one anchor to the sentence it sits in.
Still failing, the row enters the unread remainder naming that history and the run exits 2.

The bound is the sentence, which is finite and is a thing in the document rather than a number chosen
at an edge. A counted cap was declined on [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
objection even though two readers converged on three attempts independently. A minimum anchor width
was declined on the 25% median: widening every anchor buys the easy rows nothing and cheapens all of
them, and it is the mirror of the minimum-span rule ADR 0243 ruling 7 already declined. How often the
third step is reached is unmeasured, because it depends on rulings 1 and 3 being in the tree.

## Ruling 7 — the retained controls are divergent runs and one new control is generated

The three controls holding these rows stay byte-for-byte and their READMEs declare the divergence. An
anchor-less differential or refusal row enters the unread remainder, so each exits 2, and the tests
pinning them are rewritten to expect that posture rather than edited to look clean. Following ADR
0253 ruling 5, a test asserts the set of finding reasons rather than their number, so a later change
that starts accepting one of these shapes fails rather than leaving a README describing a divergence
that no longer holds.

Editing them was declined: each record was produced against a worksheet that would no longer exist,
and the negative control's is byte-pinned to `fixtures/worksheet-grammar-positive-control/case-01.md`,
which its own README retains byte for byte. Keeping the `_preceding_support` fallback for anchor-less
rows was declined because nothing would then force the new shape.

One new blind control is committed under the new shape, generated from a neutral de-identified input
and graded by a fresh reader that sees only the brief, so the tree still holds a demonstration of a
clean read. ADR 0243 ruling 19 declined a synthetic trap note as an input written knowing the rules;
this survives that because the blindness that carries the evidence is the reader's, not the
generator's, which is the arrangement the existing positive control already uses.

## What none of this reaches

**Whether the quoted words state what the descriptor names**, on a `descriptor words` route. Ruling 5
declares it rather than closing it.

**Whether the author's anchor is the right note text.** Ruling 3 establishes that an anchor is note
text and ruling 1 that every role has one. Neither establishes that the author quoted the passage
that earns the code.

**The three `###`-prefixed headings**, whose blocks this grader cannot see while `refusal_scan` reads
them. Filed separately rather than widened in, being inherited rather than entangled with anything
ruled here.

**`fixtures/filled-anchor/run-2` paired with `fixtures/filled-anchor/notes`.** The measurements above
set it aside as not a descriptor-agreement pair; nothing here repairs it or rules on what it is for.
