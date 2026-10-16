# A code waits on a pending test only for what its result would establish and the reader may say why it does not

**Measured at:** 9f6ee5f560707da7f4a0eeb8c44416344be1f161

[#1591](https://github.com/mshamblin5150-code/clinical-skills/issues/1591) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift, 2026-10-06. In the blind
descriptor-agreement read, a reader marked two diagnoses the clinician stated, a hand contusion and
an ankle sprain each with a confirmatory radiograph pending, as waiting on a result. The coordinator
overruled the reader in the retry brief, and the grade went clean. The next day's review recorded
the same move on a `Type 2 diabetes mellitus without complications` code: the note left
hyperglycemia and retinopathy open as explanations for a symptom, both complication codes were
already refused naming their establishing tests, and the retry readers wrote `none` "per the
coordinator ruling". The clinician ruled every point below on 2026-10-16, against `main` at the
commit above, where the freshness gate read `FRESH`. **Nothing is built here; this is the record
the build reads.**

## Measured before ruling

**The writer already has the rule and the reader does not.** `skills/icd10-cpt/SKILL.md` step 3
carries #149's rule, "A pending test refuses only what its result would establish", and its imaging
paragraph says that "when the note already establishes the diagnosis clinically, the pending film
does not erase it". `anchor_scan.AGREEMENT_READER_INSTRUCTIONS`, which
[ADR 0301](0301-the-agreement-read-quotes-a-code-label-by-one-convention-stated-in-the-first-brief.md)
ruling 6 makes the only copy of the reader's rules, says only "name any result the descriptor still
waits on" and that an entry descriptor still waiting on an absent or pending result fails. The two
roles were applying different tests to the same note.

**The in-run repair is closed.**
[ADR 0312](0312-the-blind-brief-states-the-whole-route-start-test-and-a-retry-carries-only-the-grader-s-finding-lines.md)
ruling 3, built by PR #1658, limits a retry to the grader's finding lines and one fixed sentence. A
run in this state therefore cannot reach a clean grade until the reader's instructions carry the
rule.

**The grader fails any value but `none`.** `anchor_scan.py` reads `waits_on_result` for entry and
differential subjects and records `entry waits on <value>` for every value other than the literal
`none`, so a reader that weighed a pending test and judged it irrelevant has no way to say so.

**The ticket's proposed field is taken.** The proposed diff named the pending test in
`open_status_evidence`. That field must be note text quoted verbatim, the grader turns any other
value into a finding, and it already carries the coexisting-history test.

**The tabular is silent on the uncomplicated default.** `tools/icd10_lookup.py E11.9` prints the
descriptor and the `E11` category notes and nothing about when the uncomplicated code applies while
a complication is being worked up. The question put to the clinician cited the convention that the
uncomplicated code is used when no complication is documented. That convention was not measured
against the Official Guidelines PDF, which is outside this repository, so it is argument and not
evidence here.

## Ruling 1 — the reader applies the writer's pending-test test

`AGREEMENT_READER_INSTRUCTIONS` gains the general rule. A code waits on a pending or absent result
only when that result would establish something the code's own descriptor asserts. A pending film
or culture does not make a diagnosis the encounter already establishes clinically wait, and where
its result could only replace the code with a more specific one, the code does not wait on it.

The ticket's narrow wording, naming only a confirmatory test that could add a more specific code,
was declined because it reaches the injury case and not the culture case #149 already ruled, so
each further variant would return as a ticket. Keeping the reader strict and leaving each case to
the clinician at review was declined because, under ADR 0312, every run with a pending confirmatory
test would then fail its grade on a correct note.

## Ruling 2 — a without-complications descriptor does not wait on an open workup

`AGREEMENT_READER_INSTRUCTIONS` also says, in so many words, that a descriptor stating "without
complications" or "uncomplicated" records the state the note documents. An open or pending workup
that might find a complication refuses only that complication's code.

Treating the uncomplicated code as waiting was declined because it leaves the condition uncodeable
for the length of any workup: the complication codes are refused because nothing established them
and the uncomplicated one would be refused because something might. Relying on Ruling 1 alone was
declined because a reader on 2026-10-07 already read the general test the other way.

## Ruling 3 — the reader may record why a code does not wait

`waits_on_result` accepts the literal `none` or the fixed form `none (pending: <test> could only add
<what>)`, for example `none (pending: right ankle radiograph could only add a fracture code)`. The
grader passes those two shapes and keeps failing every other value. The reason inside the
parentheses is the reader's judgment and is graded only for its shape. The rule applies wherever the
grader reads the field, so the Writer self-grade takes the same form.

A bare `none` alone was declined because it cannot show whether a reader weighed the pending test or
missed it, which is the gap the 2026-10-07 review recorded. Quoting the test in
`open_status_evidence` was declined because that field already carries one test and must hold note
text only.

## Ruling 4 — step 3 states the uncomplicated case for the writer

`skills/icd10-cpt/SKILL.md` step 3's pending-test paragraph gains its own sentence, worded
independently of the reader's block, saying the uncomplicated code is coded while a complication is
still being worked up and only the complication's code waits. Step 3 is the writer's rule and the
constant is the reader's, so this is one rule per role rather than the repeated copy ADR 0301
forbids. The existing test that no sentence of the constant appears verbatim in the skill still
holds.

## Ruling 5 — the overrule record is #1702's

The separate proposal in #1591's 2026-10-07 comment, a coordinator overrule recorded beside a
reader's verdict, is not ruled here. The clinician routed the coding agreement reader's remark
channel to [#1702](https://github.com/mshamblin5150-code/clinical-skills/issues/1702), and this
record borrows nothing from
[ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md)'s coursework
channel.

## What this does not reach

The reader's judgment of what a pending result would establish is a reading; a reader that
misjudges it leniently is not caught, and the form in Ruling 3 shows the reasoning without checking
it. A note whose own findings already document a complication still owes that complication's code,
and Ruling 2 does not excuse its absence; that remains the reader's judgment. Whether the
uncomplicated default matches the Official Guidelines text is not measured here.
