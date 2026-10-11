# An invoked attribution is researched before drafting and never cut or changed without asking

**Measured at:** d66c9ca4c76e0c821a19357bfc6f37a74c92dfe0

[#1497](https://github.com/mshamblin5150-code/clinical-skills/issues/1497) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 10) on 2026-10-01. That draft
attributed a named concept to a philosophical school with no claim record behind it. The heading
read caught the sentence as unrecorded, and the run repaired it by recasting the line as the
clinician's own principle and dropping the name. The clinician then asked for the philosopher to be
named with a referenced line explaining the idea, which took a fresh research and refutation round
after drafting. Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The ticket's proposed sentence names a set the research step cannot see.** It asks step 2 to
research "every attribution … the voice model will bring into the prose". In `course-assignment`,
`discussion-reply`, `peer-critique` and `practicum-case-study`, the claim questions are derived and
researched before the step that runs `voice_model_identity.py` and opens the canonical model
immediately before drafting. `discussion-post` is the exception: it opens the model before its blind
outline and derives research questions from that outline's factual points, but its derivation does
not name attributions either.

**The shared repair permits the strip.** `skills/_shared/reference/sourcing.md`'s heading-read
section says to give an unrecorded sentence "a full researched and refuted record or cut it". The
filed run took the second branch.

**ADR 0316 already covers the refuted case for these names.** It gives a refuted claim one fresh
round with a different source and requires asking the clinician before cutting a
**Clinician-supplied claim** that ends unsourced. Its population includes an invoked source in the
clinician's reasoning and a domain the canonical voice model records as the clinician's, so every
attribution in ruling 3 below is already inside it. ADR 0316 does not cover research that succeeds
and shows the attribution itself is wrong.

**Every past attribution record used an existing source class.** Over every `claims.md` under the
owning checkout's `scratch/runs/*/`, the records whose text names Musashi, Epictetus, Picard or
Marcus Aurelius (a case-insensitive name match, read 2026-10-11) were five, in three runs, and all
five carry `SOURCE: tertiary reference`. None names Picard. A name written in another form is outside
that match, so the five are a floor on the population rather than its count.

**Fictional and historical names are in the model, not only philosophers.** A case-insensitive line
count over the canonical voice model on the same day found Picard on more lines than any philosopher
it searched for. This is context for ruling 3; the ruling rests on the clinician's reason, not on the
count.

**The pointer rule bounds any reuse.** `sourcing.md` opens with: material recalled from "a memory
store, summary, index, or prior run" is a pointer that may direct a search and may not carry a
sentence.

## Ruling 1 — research looks ahead at the voice model

In each of the five coursework skills, the step that derives research questions also reads the
canonical voice model's stated principles and invoked sources beside the planned outline or deck.
Each attribution the piece is likely to lean on enters the first research round as a claim
question. The heading read remains the backstop: an attribution drafting reaches for that the
look-ahead missed is found unrecorded and is researched then, under ruling 4.

Researching each attribution on demand mid-draft was declined because it interrupts drafting on
every attribution and carries a half-written draft through a research round. Changing only the
repair rule was declined because it leaves every attribution's research after drafting, which is
the cost the ticket was filed over.

## Ruling 2 — a pointer library saves the search, and each paper still checks

The account keeps `scratch/attributions.md`, resolved through the owning checkout like the canonical
voice model, so a worktree reads the same file. It holds one entry per attribution: the name and the
idea or line as the clinician uses it, the source address and section, the APA reference and source
class, the date last checked and the paper that checked it, and any dated ruling of the clinician's.
The look-ahead opens it first. A paper reopens the named source, confirms the passage, and runs its
own refutation pass; the library entry never carries a sentence. The run adds or refreshes an entry
once that paper's record has passed `research_ledger.py` and refutation, and writes a ruling when the
clinician gives one. The build seeds the file from the five records above and from the clinician's
existing memory notes on Musashi's authorship and the Epictetus source.

The file has no grader. A malformed entry costs at most a wasted lookup, because every paper
rechecks the source, so the new `sourcing.md` section states that the library is ungraded and is a
pointer only.

Saving a copy of the source text and reusing the refuted record without reopening it was declined:
it needs a saved-source store with its own grader, and a paper would not notice a revised source,
such as an encyclopedia entry substantively revised since the record was written. Keeping the
rulings only in memory notes was declined because no research step is told to open them.

## Ruling 3 — the rule covers whatever the voice model brings in

An **Invoked attribution** is any person, school, or work named in the clinician's stated
principles or invoked sources, whatever kind it is: a philosopher, a philosophical school, a
historical figure, or a fictional character. The test is where the name came from, not what kind of
name it is. An invoked attribution is researched and is never cut unresearched. A content
attribution the run's own research introduced keeps the ordinary choice of researching it or
cutting it.

Limiting the rule to philosophers and schools was declined because it leaves the most frequently
named figure in the model exposed to the same strip. Extending it to every named attribution was
declined because it removes a repair that is correct for a content claim the run cannot source.

## Ruling 4 — an unrecorded invoked attribution is researched, and a failed one is asked about

The heading-read repair's "or cut it" does not apply to an invoked attribution: it gets a full
researched and refuted record. When that research fails, ADR 0316 applies as written: one fresh round
with a different source, then the clinician is asked before any cut.

## Ruling 5 — research that shows the attribution wrong is brought to the clinician

When research succeeds and shows the attribution itself is wrong, the run stops before the draft is
final and shows the clinician what was attributed, what the sources say, and which sources say it.
Examples are a line that is another philosopher's, a quotation absent from the work it is credited
to, or real doctrine in wording no translation carries. The clinician corrects it, supplies a source,
or keeps it as written. The run records his ruling in the library, so a later paper does not ask
again about the same line.

Correcting the attribution silently and reporting it at the go-ahead was declined: on the NUR 5042
Module 9 discussion a run cut Musashi's authorship on one source's hedge, and the clinician overruled
it. Keeping the attribution with a hedge was declined because it puts a hedge in a voice the model
records as stating positions plainly and leaves a known misattribution standing in graded work.

## Ruling 6 — the source classes do not change; a class gap is asked about

An invoked attribution is sourced first to a reference work that documents it, which is how all
five past records were carried. When no class the signed bar admits can carry it, the run asks the
clinician whether to add a class to this paper's bar and re-sign it, to supply a source, or to drop
the line, and the library records the answer.

A seventh `primary work` class was declined until the library shows a recurring answer that warrants
it; whether a course accepts a television episode in its reference list is a per-assignment ruling,
not a vocabulary property. Treating the signed bar as final and dropping the name was declined
because it is the strip the clinician ruled against.

## Ruling 7 — the rule lives once in sourcing.md

`skills/_shared/reference/sourcing.md` gains one section on invoked attributions carrying rulings 1
through 6 and the library's location and entry shape, beside the heading-read repair and the
refuted-record disposition it narrows and extends. In each of the five coursework skills, the
sentence that says what to research gains a clause pointing at that section, so the look-ahead runs
at that skill's research step.

Writing the full rule into each skill was declined because five copies drift apart while each still
reads as correct. Placing it in `skills/_shared/reference/voice.md`, the ticket's alternative, was
declined because that file instructs building the model and no research step opens it.

## What the build changes

- `skills/_shared/reference/sourcing.md`: the invoked-attribution section, and the heading-read
  repair sentence naming its exception.
- `skills/course-assignment/SKILL.md`, `skills/discussion-post/SKILL.md`,
  `skills/discussion-reply/SKILL.md`, `skills/peer-critique/SKILL.md`, and
  `skills/practicum-case-study/SKILL.md`: the pointer clause in each research-derivation sentence.
- `tools/repo_root.py`: an accessor resolving the library path through the owning checkout, so the
  scratch census counts `scratch/attributions.md` as accounted.
- A test that each of the five skills points at the section and that the section names the library
  path the accessor returns.
- Seeding `scratch/attributions.md` in the owning checkout; it is gitignored and never committed.

## What this does not reach

- **Whether the look-ahead predicted well.** Nothing grades which attributions a run chose to
  research early; the heading read catches a miss after drafting.
- **The library's contents.** It is ungraded by ruling 2; each paper's own claim record is what is
  graded.
- **Whether a source supports the attribution.** That remains the refutation reader's judgment.
