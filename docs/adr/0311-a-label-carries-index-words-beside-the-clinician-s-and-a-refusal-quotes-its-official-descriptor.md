# A label carries index words beside the clinician's and a refusal quotes its official descriptor

**Measured at:** 83e3e9b681a9af8d6991bdd701b5b1ddc41c98bf

[#1475](https://github.com/mshamblin5150-code/clinical-skills/issues/1475) was filed from the
after-action review of a NUR5144 `batch-shift` run, shift of 2026-09-30. Across eleven notes the
blind descriptor-agreement read failed seven diagnosis labels and refusal clauses whose words could
not reach their code. Each was repaired by rewording, and no code changed. Grilled 2026-10-09
against `main`, where the freshness gate read `FRESH` after a rebase onto `83e3e9b6`; the clinician
ruled every point below in that session. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The ticket's second question is already built.** It asked whether note passes should check their
own labels. [ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)
put a **Writer self-grade** in every pass before hand-off, and
[ADR 0301](0301-the-agreement-read-quotes-a-code-label-by-one-convention-stated-in-the-first-brief.md)
made that self-grade and the blind reader quote the whole **Code label**. Both are in
`skills/icd10-cpt/SKILL.md` and `skills/clinical-note/SKILL.md` on `main`. A label whose words do not
reach its code now fails before hand-off when its writer records the honest route. ADR 0301 ruling 3
left to this ticket how a note writer words a label so that it reaches its code.

**The self-grade has one blind spot, and the recorded label sits in it.** ADR 0296 ruling 1 states
that the route `descriptor words` always passes mechanically. A writer that sincerely reads
`seasonal allergies` as stating `J30.2 Other seasonal allergic rhinitis` passes its own grade and
fails the blind read a round later.

**The ticket's proposed command does not do what its text says.** It told the writer to run
`python tools/icd10_lookup.py --index "<term>"` on the label's main word. That mode is an exact
final-term match. Run 2026-10-09 against the committed database: `--index "Allergies"` and
`--index "Rhinitis"` reach no `J30.2` path, and `--index "seasonal NEC"` prints both of them,
`Allergy, allergic (reaction) (to) > seasonal NEC` and `Rhinitis ... > allergic > seasonal NEC`.

**The refusal clause already has a rule, and nothing checks it.** `skills/clinical-note/SKILL.md`
writes a refusal `NOT CODED: <code> <official descriptor>, <reason>`. A poisoning code's official
descriptor opens `Poisoning by`, so the recorded refusal naming no poisoning word broke an existing
rule. `tools/refusal_scan.py` declares that it cannot judge whether a refused descriptor is the
official tabular text, and `tools/differential_scan.py` reads only the welded pair's shape.

**Most committed refusals already carry the official descriptor verbatim.** A throwaway script
matched `NOT CODED: <code>` in every tracked Markdown file under `fixtures/` and `skills/`, collapsed
whitespace, and compared the text after the code with that code's `long` descriptor in
`reference/icd10cm-2026.sqlite`. Of 144 matches, 136 begin with the official descriptor. Seven are in
`fixtures/filled-anchor` worksheets, a preserved run record. One is the skill's own deliberately
malformed example of a missing second mark. The code-shape pattern is a floor: a refusal whose code
it does not recognize is not in the 144.

## Ruling 1 — a label carries words that reach its own code

`skills/clinical-note/SKILL.md` gains an author-side rule beside the hyphen rule: the words before
the hyphen either state the code's official descriptor or reach that code through the alphabetic
index. The writer checks a route with `python tools/icd10_lookup.py --index "<final index term>"`,
naming the index path's last term rather than the label's main word. This states the writer's side
of ADR 0301 ruling 1's convention and repeats none of the reader's rules, which stay in the brief's
constant under ADR 0301 ruling 6.

Relying on the self-grade and the blind read alone was declined because the self-grade's
`descriptor words` route is where the recorded failures sit. A rule only for repairs was declined
because first drafts would keep failing at the recorded rate.

## Ruling 2 — the clinician's words stay on the line beside the index words

When a label needs index words, they come first and the clinician's own words follow after a comma:
`Seasonal allergic rhinitis, seasonal allergies - J30.2`. A brand-only allergy-status label gains
the drug-class words, and the clinician's wording stays beside them. Under ADR 0301 ruling 4 the
anchor is the whole code label, so the added words sit inside it.

Replacing the clinician's words was declined because his phrase would survive only in the history
and the label would stop reading as his. Keeping them only when they are a lay term was declined
because the writer would judge what counts as lay, pass by pass.

## Ruling 3 — the clinician's diagnosis decides the code, and index words only narrow it

Index words added to a label may make the clinician's diagnosis more specific, by site, trimester,
season or drug class. They never name a different condition. Where no wording of his diagnosis
reaches the chosen code, the code is wrong and the writer selects one his diagnosis reaches. The
recorded instance is a pregnancy urinary tract infection relabeled as bacteriuria without symptoms.

A relabel raised as a pre-approval question was declined because the right answer is this one in
nearly every case. Leaving it to the blind reader was declined because the recorded instance reached
the clinician's review. Whether two phrasings name one condition is a reading; no check reaches it.

## Ruling 4 — a refusal clause's descriptor is checked against the committed database

A welded refusal's text after its code must begin with that code's official long descriptor in
`reference/icd10cm-2026.sqlite`, after whitespace is collapsed. Anything else is a finding before
hand-off. The seven non-verbatim refusals in `fixtures/filled-anchor` keep their text, and their
tests expect the new finding, on ADR 0301 ruling 7's arrangement for preserved records.

Restating the rule in prose was declined because the recorded defect already broke a prose rule.
Leaving it to the blind reader was declined because a miss costs a full round, and the self-grade's
`descriptor words` route cannot see it.

## Ruling 5 — the descriptor check covers notes and coding worksheets through one comparison

The check binds a note's welded refusals and an `icd10-cpt` worksheet's refusal block. One shared
comparison serves both graders, so the rule cannot pass in one artifact and fail in the other.

Notes only, with the worksheet filed separately, was declined because the comparison would likely be
written twice. Notes only, with the worksheet gap declared, was declined because it keeps a known
gap open on purpose.

## Consequences recorded as derived rather than ruled

- `tools/refusal_scan.py` loses its declared limit that it cannot judge whether a refused descriptor
  is official, and `tools/differential_scan.py`'s declared limits are re-derived to match.
- `skills/batch-shift/SKILL.md`'s pass brief points to the clinical-note rule and carries no second
  copy, on ADR 0296 ruling 2's arrangement.
- The two row-24 guideline-tail misses the ticket also records were caught by
  `tools/differential_scan.py` and need nothing here.
- No `CONTEXT.md` term is added; **Code label** and **Writer self-grade** already name the parts.

## What this does not reach

- Whether a label's index words name the clinician's condition rather than a neighboring one, which
  ruling 3 leaves a reading.
- Whether a `descriptor words` route really states the descriptor, which stays ADR 0296's ceiling.
- A refusal whose code the build's matcher does not recognize as a code.
- Whether the refused code is the right refusal for the encounter.
