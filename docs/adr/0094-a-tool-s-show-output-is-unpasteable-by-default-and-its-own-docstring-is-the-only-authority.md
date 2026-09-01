# A tool's show output is unpasteable by default and its own docstring is the only authority

Found while grilling [#708](https://github.com/mshamblin5150-code/clinical-skills/issues/708),
2026-09-01, at `origin/main` `2dcbf69`, freshness gate `FRESH` at both checkpoints. **Ruled by
the clinician on that date.** Nothing is built here; this is the record the build reads.

**#708 is about a file outside this repository and this record is not.** That ticket concerns one
machine's `autoMode.environment` brief, which no tool here may write. What the grilling turned up on
the way is a rule about `tools/` — where it belongs, where a tool author reads, and where it is
subject to a check. Splitting them was settled in that grilling on this ground: the brief may state
the rule, and the rule may not live only in the brief, because a rule held solely in a file outside
every checkout is the decay the ticket itself is about.

## Measured before ruling, at `2dcbf69`

Every module in `tools/` carrying a `--show` flag, with its own docstring's verdict read as a
sentence rather than matched as a substring:

| what the docstring declares | modules |
| --- | ---: |
| the output is PHI | 12 |
| private working material, **not** PHI | 3 |
| copyright-restrained — a line into a ticket, never a table | 1 |
| safe to paste | 1 |
| no verdict at all | 2 |

**Re-derived unchanged at `f05cedf`.** `main` advanced twice while this record was being written,
and the second advance landed [#678](https://github.com/mshamblin5150-code/clinical-skills/issues/678)'s
legal-reference work **inside `tools/reference_scan.py`** — one of the modules the table above
classifies. Its declared class did not move. The re-derivation is recorded because a table measured
at a base the branch has left is a measurement about a tree that no longer exists, which is
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180).

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. They move the day
a tool lands, and ruling 1 below is what stops them mattering.

**"PHI" was doing two jobs and they came apart.** The second row is the finding: `--show` on the
discussion and voice-model scanners names **classmates**, who are real people and not patients, so
the output must not be pasted and `phi_scan` will never flag it — its corpus layer harvests patient
names and its shape layer matches identifier shapes, and a classmate's name is neither. A vocabulary
with one bucket called *PHI* and one called *safe* cannot express that row, or the copyright row
beneath it. The operative question was never *is this PHI*; it is *may this leave the machine*, and
those were one predicate until the discussion tooling landed.

**The measurement was taken three times, because the first two instruments were prose matchers and
both failed.** The first searched each docstring for a verdict phrase and reported
`discussion_post_scan` as carrying none — its verdict is **hard-wrapped**, and a phrase broken across
two lines is invisible to a substring search, which is `test_run_record_claim.py`'s recorded finding
arriving on a fresh check. The second keyed on `safe to paste` appearing anywhere in the docstring
and filed three PHI-declaring modules as safe, because each **mentions** the blessed exception while
ruling the opposite for itself — `spelling_scan.py`'s mention-versus-use problem, uninvited, on the
one question where a false *safe* is the expensive direction. The third split the normalized
docstring into sentences and read them, and is what the table above rests on. **That sequence is the
evidence ruling 3 stands on and it is this session's own record rather than a hypothetical.**

## What is ruled

**Ruling 1. A tool's `--show` output is unpasteable by default.** The default is the refusal, and it
holds for every module in `tools/` carrying the flag, including one written after this record. A
module may rule otherwise **for itself, in its own docstring**, and only that ruling clears its
output.

**The inversion is the whole of the fix, and the reason is the direction each arrangement fails
in.** Under an enumeration, a module absent from the list reads as cleared, so a new tool is safe
until somebody remembers to add it — the failure lands on a paste. Under the default, a module that
declares nothing reads as unpasteable, so a new tool is refused until somebody remembers to bless it
— the failure lands on an inconvenience. The two arrangements are equally forgetful and they are not
equally expensive.

**Ruling 2. The module's own docstring is the only authority, and no second copy is kept anywhere.**
Not in `CLAUDE.md`, not in `AGENTS.md`, not in a brief. A roster held in two places is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220): a prose edit to either
copy fails nothing, and the reader misled is whichever one they had nearer to hand.

**It has already drifted exactly that way, which is why this is a ruling rather than a preference.**
`reference_scan.py`'s docstring lists the sibling scanners whose `--show` stays PHI and declares in
as many words that the list *is the ruling's own and not a sweep of `tools/` for `--show`* — the
in-tree copy carries its qualifier honestly. The copy in one machine's brief inherited that list and
dropped the qualifier, and by 2026-09-01 it named six modules where twelve declare PHI, with no row
at all for the other two classes. **The authoritative copy was correct and the derived copy was
short, which is the direction a second copy always fails in.**

**Ruling 3. No check accompanies ruling 1, and the absence is declared rather than left to read as
an oversight.** [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s thesis —
*what a written instruction cannot do is fail* — is the obvious pull here and it does not reach this
case, for two reasons.

**An inverted default is the one arrangement where silence is the safe answer.** A module that
declares nothing is refused, which is the correct verdict for both modules that declare nothing
today. A check would compel a sentence to be written where its absence already produces the right
behavior: ceremony, not a gate. That is precisely the asymmetry ruling 1 buys, and building a gate
on top of it spends the thing it bought.

**And the instrument would be a prose matcher, which failed twice in this record's own
measurement.** Grading *does this docstring state a verdict* means searching prose for a phrase.
Normalizing for hard-wrap fixes the first failure and not the second, and neither fixes the ceiling:
such a check grades whether a sentence **exists**, never whether it is **true**. A green run would
certify ceremony and read as certifying disclosure.

**Ruling 4. The one claim here that is load-bearing already carries a check, and it is not this
record's to build.** `reference_scan.py --show` is the single blessed output, ruled by the clinician
on 2026-08-19, and its blessing rests on the module's findings being bounded by what its code can
draw from. `reference_scan.BODY_ROWS` declares the rows that read the draft's prose and an AST walk
asserts both directions against it, so a fifth body row cannot arrive quietly and widen the
aperture the blessing was measured through. **The default needs no check and the exception already
has one**, which is the correct distribution: the safe answer is silent and the dangerous one is
guarded.

**And the guard fired in the wild while this record was being written, which is worth more than the
argument for it.** #678's work merged at `f05cedf` on 2026-09-01, hours after the measurement above,
and it added a finding kind to `reference_scan.py`. The test that arrived with it asserts that kind
is **not** in `BODY_ROWS` — the new row does not read the draft's prose, **declared in the diff that
introduced it** rather than found by a later sweep. A blessing that survives a change written by
somebody who had never read this record is the only kind worth resting a ruling on.

**Ruling 5. The class vocabulary is `CONTEXT.md`'s and is named there rather than here.** Four
classes were observed and the glossary held a term for none of them. The record of *what the classes
are* belongs in the glossary; the record of *what the default is* belongs here. Neither restates the
other.

**Ruling 6. A partial permission is a docstring's to state and is never flattened into the
default.** `guidelines_recs.py --show` is not PHI and is not freely pasteable: it prints a society's
copyrighted expression, and the standing rule is a line into a ticket and never a table. Ruling 1
refuses it by default and ruling 2 sends the reader to the module, which states the narrower
permission. **A vocabulary that could only say *yes* or *no* would have to choose between forbidding
a blessed quotation and clearing a whole table**, and both are wrong.

## What this does not reach, declared rather than left to be found

**Whether a docstring's verdict is true.** Ruling 2 makes the module the authority and nothing
grades it. A tool whose `--show` quietly widens — a new finding kind that starts quoting note prose —
keeps whatever verdict it was written with, and no check here notices. That is ruling 3's ceiling
stated as a limit rather than as a caveat.

**The two modules carrying no verdict are not thereby reviewed.** `phi_scan.py --show` reveals the
matches it otherwise redacts, so its output is PHI by construction; `run_grader.py` is the shared
runner and its members declare their own. Both read as unpasteable under ruling 1, which is correct
for both today. **Reading correctly is not the same as having been read**, and neither has been
ruled on.

**`run_grader` does not speak for its members.** A verdict on the runner would be a claim about
every grader that delegates to it, and those are separate modules with separate populations. The
runner owning the console codec for the family does not make it own their disclosure posture.

**Nothing here reaches a file outside the checkout.** The brief on one machine states the rule under
[#708](https://github.com/mshamblin5150-code/clinical-skills/issues/708) and that ticket owns the
edit; this record owns the rule. A brief that falls out of step with this record is #708's defect
and not a defect in `tools/`.
