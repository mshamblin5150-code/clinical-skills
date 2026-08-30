# A four-row limits object takes the enumerated skill bind the sibling's size refused

[#565](https://github.com/mshamblin5150-code/clinical-skills/issues/565) is
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 2's residue: `tools/checks_ledger.py` was the last ledger grader holding every limit it has
in prose, with no declared-limits object — the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) have ruled insufficient —
and the ticket's own `Done when` said the count of those limits was the first thing to produce.

Grilled 2026-08-29. **Five decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `3ef2e74`

The population was derived by an end-to-end read of all 709 lines of `tools/checks_ledger.py`,
applying ADR 0053 ruling 3's inclusion criterion — a limit tells a reader that a clean result
covers less than it appears to; rationale is not a limit.

**Four mechanism-scoped limits, live in prose that a prose edit fails nothing against:**

1. Every verdict is a reading — a well-formed `clean` from a reader that skimmed is
   indistinguishable from one that read, and whether the reader opened the draft at all is not in
   the record.
2. Substance is a shape, not a reading — one stock sentence satisfies the `FINDINGS` substance
   test on both the defect row and the #255 row. This is the class-wide R2 limit, and ADR 0053
   ruling 4's call transfers whole: **one row, not two and not none.**
3. The repair is unreached — a file of well-formed `defect` records exits 0, and that 0 means the
   verdicts are well formed, never that the draft was mended.
4. A heading outside the table is counted and never graded — a run adding checks of its own has
   failed nothing.

**Two limits are already at a destination and take no row here.** The
not-graded-for-substantiation residue on cleans off `SUBSTANTIATED_CLEAN` is run-scoped and the
report already prints it on every run — the `not graded for it` count and the named
`SUBSTANTIATED_CLEAN` list — which is
[ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md)
ruling 7's destination already occupied. And the `keyword_of` copy-parity limit is owned by
`research_ledger.DECLARED_LIMITS`'s `keyword-parser-copy-uncompared`, which names this module —
see ruling 3 below.

**Excluded per ADR 0053 ruling 3, worked calls:** `normalize`'s dropped-apostrophe miss (it fails
loud — a reported miss, never a silent pass — which is safe-direction rationale, not coverage);
the vocabulary-held-here-derived-there arrangement (a hole the bind test closes); the exit-status
semantics (mechanism); the `--show` PHI limb (not coverage).

**That figure is stated here, once, dated and stamped, and nowhere else.** It is a measurement of
a tree at a commit, not a live count; the live count is the object's to state. It refutes both
poles the ticket left open: the count is not one, so
[ADR 0056](0056-the-one-row-object-refusal-was-a-claim-about-a-module-s-prose-population-and-it-expired-for-every-queued-row.md)'s
one-row question never arises, and it is not thirty-six, so this is the small-population shape
ADR 0053 ruling 2 predicted — refined below, because the prediction's *"one prose ceiling class"*
turned out mixed.

## Ruled 2026-08-29

**1. The destination is the object, populated whole.**

The ticket's three destinations resolve on the count. *Declare and leave* was contingent on "few
and stable" with no evidence; the evidence is four unbound prose limits in a module that grades a
fan-out, which is the live #220 shape. *All onto the report* is refused by ADR 0063's own split:
all four are about the grader, true of every run, and a mechanism limit printed on every run is
noise — ADR 0053 ruling 9's distinction, inherited whole, so **the object does not print**. The
run-scoped floor stays on the report where it already prints, untouched except by ruling 5.

**2. The shape is the three-field row, and the module copied is named: `research_ledger.py`.**

ADR 0053 ruling 2 predicted this module was `discussion_reply_scan`'s shape — one prose ceiling
class — and the census changed that ground: **three of the four rows are re-derivable and one is a
declared reading.** Every test here builds its own checks file, so a handler with a positive
control is always constructible — which is also why ADR 0053 ruling 7's refusal of a `tripwire`
value transfers whole. A mixed population is what the `evidence` field exists to record, and the
identity-pinned behavior set — a row typed `behavior` fails the suite until it has a handler — is
what makes *behavior row without a control* a suite failure rather than a habit.

So: `DECLARED_LIMITS` of (`key`, `limit`, `evidence`), `NOT_REACHED` the order-preserving derived
view of the sentences, handlers keyed on `key`, `EvidenceDisposition` imported as
`research_ledger.py` imports it. Rows 2, 3 and 4 above take `BEHAVIOR` with a handler and a
positive control each; row 1 takes `DECLARED_READING`. The two-tuple was refused because it
records a mixed population as if it were uniform, and because ruling 8's citation argument holds
here — ratified records already reason about this module's limits, and a key is the name that
survives rewording.

**3. The `keyword_of` parity limit keeps one owner, and this module points rather than mirrors.**

`research_ledger.DECLARED_LIMITS` carries `keyword-parser-copy-uncompared`, naming this module,
ruled in there by elimination in ADR 0053 ruling 7. A mirror row here was refused on two grounds:
two rows stating one claim is the #220 shape ruling 4 refused when it collapsed five R2 copies to
one, and the claim fails ruling 3's criterion *for this module* — a clean `checks_ledger` run is
not overread because of it, since this module's `keyword_of` is tested directly on its own two
vocabularies and the divergence is permitted by design. The ruling 4 objection to
*declared elsewhere* does not bite: that refusal was about a limit on this module's rows held in
another module's **prose**; this one is held in an object under a bind. The repair is one pointer
in `keyword_of`'s docstring naming the sibling row's key, so a reader lands on the owned row
rather than re-deriving the arrangement.

**4. `SKILL.md` gets the enumerated both-directions bind, and the module copied is named:
`case_study_scan.py`.**

ADR 0053 ruling 10 gave the sibling's skills headline-plus-pointer and refused a completeness bind
**on row count** — *"at this size it means a consumer-facing skill enumerating every limit."* That
ground does not hold at four rows, and the closer precedent is already in this skill one command
over: `case_study_scan.NOT_REACHED` is enumerated in `practicum-case-study` step 9 and asserted
against the skill in both directions. The argument transfers whole — step 9's by-eye walk is the
only thing that reaches this grader's residue, so the enumeration is the reader's brief rather
than decoration.

The surfaces: **`skills/practicum-case-study/SKILL.md` step 9** enumerates the four `NOT_REACHED`
sentences under a both-directions bind. **`CLAUDE.md`'s post-draft-checks section** — whose
what-it-cannot-reach paragraph is a near-verbatim copy of row 1's sentence, the live #220 shape —
is repaired to point-and-no-copy under the shingle bind, through `tools/prose_bind.py`. **The
module docstring** keeps its arguments at their code points and states no row sentence, on ruling
6's terms: the object carries sentences, the docstring carries arguments. The existing presence
test on *"a clean scan is not a checked draft"* stays — that sentence survives as the headline,
not a row. `AGENTS.md` is not a surface: its mention is the tool-naming class and carries no limit
sentence, checked rather than assumed. No ADR bind, on ruling 10's exclusion.

**5. The report's one unqualified count takes its qualifier.**

`outside the table N` is the one count on the report that under-says — a reader can take it as a
graded population, when row 4's whole point is the opposite. The label becomes
`outside the table (counted, never graded)`, which is ADR 0063 ruling 7's mechanism: the
run-scoped face of a declared limit sits beside the count it qualifies, on every run, asserted by
a test. The mechanism-scoped sentence stays in the object. Nothing a run prints today goes quiet.

### Inherited without re-grilling

ADR 0053 ruling 9 (the object does not print — folded into ruling 1), ruling 12 (**it lands as one
change**, trivially at this size — every split point at four rows is the dishonest kind that
record names), and ruling 13 scaled (**the ceiling is declared and states its method**: the
population was derived by an end-to-end read of this module on 2026-08-29, and a limit written as
prose after that date is caught by a reader and by nothing else).

## What must not come out of this

**Do not restate the object's row count in prose.** How many there are is the object's to say. The
figure in *Measured before ruling* is a dated measurement of a tree at a commit and is not to be
copied forward. `tools/test_constant_prose_counts.py` guards the object itself; the prose is a
reader's job.

**Do not let the object become a second copy of the docstring.** Ruling 6's line, policed by the
shingle bind: the object carries sentences, the docstring carries arguments.

**Do not add a mirror of the parity row later without re-opening ruling 3.** The day a parity test
is written, the owned row's subject — *a test that deliberately does not exist* — is falsified,
and the remedy is retiring the sibling's row, not adding one here.

## Declared limits

**The census figure is a floor, and the instrument was reading.** ADR 0053's measurement showed
every name-keyed matcher under-reports; only the read found this set, and a limit assembled at run
time or written in a vocabulary nobody has used is outside the read as well.

**Ruling 2 buys a control per row, never a correct row.** A handler proves the blind spot is
caused by the thing the row names; whether the sentence is the best description of what the module
fails to reach is a reading.

**Ruling 4's binds prove that prose points and does not copy, and that the enumeration matches the
object. They prove nothing about whether either is true.**

**The ceiling is a declaration and not a mechanism.** Nothing mechanical stops a fifth limit
arriving as prose.

## Consequences

The build lands whole: the object, three handlers with positive controls, the reading row, the
sentences removed from every prose site that states one, the step 9 enumeration with its
both-directions bind, the `CLAUDE.md` repair and bind, the `keyword_of` pointer, and the report
label. [#565](https://github.com/mshamblin5150-code/clinical-skills/issues/565) is respecced for a
build drone and moves from `grilling` to `ready-for-agent`.

The three-module comparison this ticket was filed on is closed: every ledger grader in `tools/`
either holds a limits object or has one specified by a ratified record, and the family's shape
questions — population criterion, row shape, bind arrangement, report destination — each have a
ruling to cite rather than an "established arrangement" to guess at.
