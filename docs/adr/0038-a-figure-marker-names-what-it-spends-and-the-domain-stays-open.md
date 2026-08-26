# A figure marker names what it spends and the domain stays open

A NUR_5144 M1 discussion reply was drafted, graded clean by both commands, shown to the clinician, approved, and posted. **After it was on the board** he returned two voice corrections and ruled the posted reply final. [#496](https://github.com/mshamblin5150-code/clinical-skills/issues/496) is the two defects that produced it.

Grilled on 2026-08-26 against `88c888e`. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The ticket's own framing was falsified by the artifact

#496 reads finding 1 as *step 3 governs rate and is silent on magnitude*, and offers three ways to word a magnitude sentence. The run record says otherwise.

`scratch/runs/nur5144-m1-discussion/response-kiersten.md` carries **exactly one** `AMPLIFICATION` marker, on line 45, reading `named philosopher`. The figure the clinician corrected — *"An entry you never make is a hole"*, line 40 — carries **no marker at all**, and neither does the speculum-and-hand figure above it.

So the ticket's *"one marked amplification, a named philosopher, no second instance"* is accurate about the marker and misleading about the reply. **The figure that was wrong is the one nothing named**, and every option the ticket offered edits prose that would never have been consulted about it. A magnitude sentence keyed on *the instance already being written* reaches only marked instances.

## The two corrections are not one defect

> *"in this response i would have said What concerns me instead of what worries me"*
> *"and an entry you never make is a hole should have been something like An entry you never make is a giant black hole (maybe even a slight reference to how it drags down the whole disposition)"*

The second is a rule gap. The first is not: `scratch/voice-model.md` carries no evidence about either word, so no rule was broken. It is per-account lexical evidence the model lacked. The ticket bundles them and only one is step 3's.

## Ruled 2026-08-26

### The figure

1. **The marker keys on the figure being present, not on the author having added it consciously.** *"consciously"* comes out of `skills/discussion-reply/SKILL.md` step 3. It was the escape hatch: a figure written rather than deliberately added owed no marker, so it left no trace and no later reader could ask about it.

2. **The axis is function, not magnitude.** A retained figure carries the argument, and its payoff sentence states what it does. **Nothing here raises the rate or the size.** The v2 damping ruling of 2026-08-21 and [#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388) stand untouched — a run obeying this writes the consequence clause and leaves the noun alone where the noun already carries.

   The clinician's correction supports both readings and the function one was chosen because it reaches the correction exactly while being unable to become *reach for a bigger image*. A hole is inert and illustrates; a black hole acts on what is near it, which is why *drags down the whole disposition* belongs and is not decoration on top of a bigger noun.

3. **The model's observation 4 is rewritten and keyed on the move, with the domain left open.** It currently reads *"The metaphor is martial or metallurgical, and it is load-bearing rather than decorative — it carries the argument rather than illustrating it. Seven samples."* The second half is the finding and is correct. The first half is a taxonomy and is what failed: *hole* is on no list, so the drafter classified it as outside the category and wrote nothing.

   **The replacement is not a longer list.** The clinician stated the move directly: he argues by mapping a domain whose rules he genuinely knows onto the situation, then spending the domain's real behavior as the argument. The domains measured in his own typing run well past any enumeration — martial, forging, physics, survival physiology, Star Trek and Borg, chemistry — and he named further ones unprompted.

   **An enumeration is refused as a *shape*, not merely as an incomplete list.** The same domain appears literally and figuratively in one corpus: *triage* is the job in an emergency department and the figure when it is applied to coursework. Nothing keyed on a domain can tell those apart, so no list of nine or ninety recognizes an instance. Only the move is recognizable.

4. **The marker records the domain and the property it spends, not a kind.** The form becomes a domain and the behavior the claim rides on, replacing a classification the drafter has to judge. **A decorative figure has no property to name**, so the blank cannot be filled — which converts a reading into a form a run either can or cannot complete. It also makes the count honest: the grader printed `amplifications: 1` for a reply containing at least three figures.

5. **`tools/discussion_artifact.py` owns the form; both skill steps state it; a test binds the prose to the constant.** The module already owns the regex both graders import, so no second implementation exists to drift. This is [ADR 0036](0036-a-references-label-is-a-per-pipeline-source-spelling-for-one-rendered-outcome.md)'s mechanism, one merge old, and it is what #496's third *Done when* asks for.

### The gate

6. **One approval, not two.** `tools/discussion_reply_scan.py` gains a row that **refuses** an unfilled or self-restating property field, so a decorative figure never reaches the clinician. `skills/discussion-reply/SKILL.md` step 4 stops being a bare *here is the clean reply, may I post* and puts the figure table in front of him — each figure, its domain, the property it spends — with the voice question asked **by name and separately** from the substance question.

   The ticket's option 1, a second gate, was declined on the ground step 5 already states: *"The clinician's review is the pacing."* Replies are due the night they are written. It stays available on evidence: a second defect getting past the figure table is the measurement that would justify its own trip.

   **The cost is named rather than left to be found.** It is still one approval, so a quick read of the figure table reproduces this run. What changes is that the thing being skimmed is a named table with a blank in it rather than prose with nothing in it.

7. **`AMPLIFICATION` is renamed `FIGURE`, and the retired keyword is still read.** Two of the reported words became false: the axis is function rather than magnitude, so *amplification* teaches the framing ruling 2 retires, and `(counted, never graded)` stops being true once ruling 6 lands.

   A `FIGURE`-only parser reads **zero** markers in the preserved run record, strips nothing from the word count, and reports a clean scan — this ticket's own defect, on this ticket's own evidence. So the retired keyword is parsed, stripped from the word count, and reported on its own line as a pre-#496 marker that is **not graded**: neither silently passed nor failed.

8. **The form lands in both discussion skills; the refusal lands in `discussion-reply` only.** `skills/discussion-post/SKILL.md` step 3 permits no added figure — *"already present in the clinician's reasoning may stay; the skill is licensed to add none"* — so in a post every figure is the clinician's. An unfillable property field there means the run kept a figure of his and cannot say what it does, and **refusing that is a scanner overruling his own sentence.** `tools/discussion_post_scan.py` counts unfilled fields without failing, on `filled_vitals_census.py`'s counted-never-graded arrangement. The record still forces a run to demonstrate it understood a figure before keeping it.

### Durability

9. **`skills/practicum-case-study/reference/voice.md` §4 gains an eighth item — the figure and what it spends.** §4 lists seven things a build records per sample and **none of them is imagery**; item 4, *the characteristic move*, is structural — how a paragraph opens, closes, concedes. So observation 4 exists because some build noticed it, not because the spec required it, and `setup-clinical-skills` step 8 may rebuild the model without it. The damping ruling's negative rule — do not strip his figures from graded prose — would then rest on nothing, and the failure is his voice being flattened rather than an error.

   It is added as its own item rather than folded into item 4, because burying the move inside a category about paragraph shape is how *martial or metallurgical* buried it the first time.

10. **`concerns` / `worries` is recorded as a discriminating pair, both halves attested.** The generic half is the machine's actual draft and his half is his actual correction, so it is the paired-attested kind §5 prizes rather than a generic half the build composed.

    **The distinction is attachment, not vocabulary.** When the subject is his own judgment about a clinical or professional matter it is *concerns*; *worry* is a state he attributes to other people. The draft put someone else's word in his mouth, which is why no rate or magnitude rule could have reached it. Which register it lands in is a build call, the instance sitting in both.

### The model bind

11. **A model shape grader is built: `tools/voice_model_scan.py`.** Counts only by default, `--show` output is private working material, exit 0 clean / 1 finding / 2 did-not-scan, on its siblings' arrangement. It grades **shape** — every register carrying its pairs, every observation carrying a quote, and the figure observation naming a domain and a property.

    **It gates.** `skills/discussion-reply/SKILL.md` step 3 runs it before drafting with exit 0 required, which is `tools/research_ledger.py`'s arrangement four steps up in the same file, and `setup-clinical-skills` runs it as the acceptance check when it builds a model — so a rebuild that drops the figure observation fails where it is built rather than on the next reply. **This is what makes ruling 9 fail rather than merely be written down**, which is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written instruction cannot do is fail*.

    **The grilling published a claim that this was impossible and it was wrong.** The claim was that no test can reach a gitignored per-account model. `repo_root.scratch_root()` resolves from inside a worktree to the main checkout — measured from this branch's tree — and the repository already carries ten `skipTest` precedents for an absent external input. The honest limit is narrower and is stated in ruling 13.

12. **An absent model is exit 2 with a declared door, and neither door buys silence.** `tools/phi_scan.py`'s corpus-layer arrangement, adopted whole: the banner prints either way, a run proceeds only by taking the door explicitly, and the run record carries *voice unmodeled*.

    Making it a hard stop was refused because `voice.md` §8 blesses the state in as many words — a run declares the gap, names the skill that closes it, and proceeds, *"A run does not stop to collect samples mid-draft."* Making it exit 0 is the silent pass §8 already refuses as *sounding like a stranger silently*.

    **This exposed a live defect older than #496 and independent of it.** `voice.md` §8's no-model branch is inherited by `practicum-case-study` through the sheet. **Neither discussion skill inherits anything** — both reference `scratch/voice-model.md` directly and neither states what happens when it is absent. That is filed separately and is a bug today with or without this record.

13. **The grader reads two inputs for two purposes.** A committed **synthetic** model under `tools/testdata/` — invented person, invented domains, free of patient and personal material — grades *the grader* and runs everywhere including CI. A live class reads the **real** model through `scratch_root()`, grades *that model*, and skips with the gap named where `scratch/` is absent. `tools/test_corpus_census.py`'s arrangement.

    **A copy of the real model into each worktree was proposed and declined on two measurements.** It is unnecessary — `scratch_root()` already reaches the real one from a worktree — and it does not reach CI, because `.gitignore` line 5 is a bare `scratch/` and a copy stays ignored wherever it sits. Its cost is `tools/skills_mirror.py`'s recorded defect: a second copy of per-account state looks like a working install and answers with whatever it said the day it was copied, which is how a worktree kept certifying a rule [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23) had deleted.

## What none of it reaches

- **A figure the drafter never marked.** The row grades the marked set. Rulings 1 and 4 narrow that and do not close it, and it is the exact hole this ticket came from.
- **Whether a payoff sentence actually spends the property.** A reading, and the clinician's at the step-4 show.
- **Whether a model's figure observation is *right* about him.** The grader reaches shape. A model can carry a well-formed observation that is wrong, and `voice.md` §9 already rules that a model cannot be verified by the run that built it.
- **The real model's content, in CI.** `scratch/` must never reach a runner, so the live class is permanently dark there and says so. The synthetic fixture grades the grader; it cannot grade his model.

## Provenance, and what is deliberately not published here

Every corpus figure behind rulings 3 and 10 was measured against `scratch/voice-mining/register-3-prose.md`, which holds the clinician's own messages and is gitignored. **No line of it is quoted in this record**, and the counts are stated on the tickets rather than restated across files, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms — nothing committed re-derives them and the next export moves them all. The only quotations here are the two corrections and the draft line the clinician published in #496 himself.

**The domain counts are ceilings on a matcher and were never read as counts of figurative use.** A regex matching a domain word cannot separate the literal use from the figure, which is ruling 3's own subject arriving on the instrument that measured it. What the rulings rest on is the instances that were read, not the totals.

The run artifacts under `scratch/runs/nur5144-m1-discussion/` stay in the **as-posted** form. The corrections live on the ticket, and an artifact that reads better than the board is a worse provenance record.
