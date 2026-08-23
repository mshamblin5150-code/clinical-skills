# A run is keyed to the graded artifact, and the artifact slot is a vocabulary rather than a name

[ADR 0005](0005-a-run-is-keyed-to-the-board.md) ruled the date out of the run key on 2026-08-22 and settled on `scratch/runs/<course>-<module>/`. Grilling [#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) on 2026-08-22 into 2026-08-23 found that `<course>-<module>` is not a key.

**This record was ratified as `0010` and renumbered to `0014` on 2026-08-23**, by `git mv`, because it took a number [#406](https://github.com/mshamblin5150-code/clinical-skills/issues/406)'s untrusted-read ADR already held by ten hours. Nothing in the ruling changed. The allocation mechanism is [#452](https://github.com/mshamblin5150-code/clinical-skills/issues/452).

**Nothing in this repo states that a module holds one graded artifact, and a Canvas module normally holds several.** Both discussion skills derive their key from the course and module breadcrumbs and stop there, so a module carrying both a discussion board and a case study puts two skills on one `claims.md`. That is #417's own defect 1 — one ledger path, several runs, silent overwrite — rebuilt inside the fix for it.

The clinician ruled the artifact slot on 2026-08-22. The key is `scratch/runs/<course>-<module>-<artifact>/`.

**0005 is not superseded.** Its ruling — the date is provenance rather than identity, so it moves to the filename inside — is untouched, and was applied a second time during this grilling to decide that the *output* file carries the date. What is corrected is one sentence of its text, and 0005 keeps that text with a forward pointer rather than being amended, because the collision below was not known on the day it was ruled and rewriting the sentence would make the ruling look wider than it was.

## The collision was live, not predicted

`output/case-studies/` held three drafts under two schemes: two keyed `<course>-m1`, naming a module, and one keyed `<course>-cs1`, naming an artifact in the module slot. They are **three sittings of one assignment**. The tree could not decide which unit it meant, which is the same confusion one level down from the one that loses a ledger.

## What fills the artifact slot

**A fixed vocabulary, one word per skill** — `discussion`, `case-study`. It is not typed: it is a fact about which skill is running, derived in the same sense `<course>` is derived from a breadcrumb.

**The slugged breadcrumb leaf was refused on evidence.** It is the more derived option and the obvious one. But `skills/practicum-case-study/reference/rubric.md` already records that the graded wrappers carry copy-paste damage, that one still bore a title the faculty had reused from a different assignment, and that the case title overrides the wrapper header. A key built from free text a faculty member edits mid-term fails the stability test derivation exists to pass — the key would change without the assignment changing, which is the failure a derived key was chosen to avoid.

## Derivation becomes universal

`practicum-case-study` never opened the LMS on its faculty-material branch. Its whole input is a `.docx` or an intake block transcribed from a module video, so its key had no source and would have been **typed** — the one place in the convention where the derivation guarantee did not hold.

It now takes the assignment URL, derives the key off the breadcrumbs, and transcribes a signed `bar.md` from its own topic and syllabus, which is [#416](https://github.com/mshamblin5150-code/clinical-skills/issues/416) ruling 12's arrangement applied to the unrouted branch.

**The ground is the multiple-classes requirement rather than the key.** `reference/rubric.md` is captured from one program's LMS. A second practicum course reading that file inherits the first course's bar — so a live bar is what makes the skill work for class two, and the derived key falls out of it for free. The clinician's words: *"i dont want this skill to be for one class i want it to be used for multiple practicum classes."*

## Considered options

**Keep `<course>-<module>` and assert one graded artifact per module.** Rejected, and it is the option that looks cheapest because it is what the convention already assumed without saying. It is an unverified claim about an LMS, holding up a join key, that this repo cannot check — which is its own recurring failure: a check that could not have worked, reading as a settled negative.

**Keep `<course>-<module>` as a container and distinguish the artifacts through ledger filenames inside** — `claims.md` for the board and a differently named case-study ledger beside it. Rejected. Ledger naming becomes artifact-specific, and two unrelated artifacts share a directory for no reason beyond sharing a module number.

**Key on the slugged breadcrumb leaf.** Rejected on the evidence above. Its one genuine advantage is that a module holding two case studies does not collide.

**Add a fixed-vocabulary artifact slot.** Adopted.

## The cost this accepts

**A module holding two case studies collides**, and the second takes an ordinal. That is the price of refusing a key built on a string faculty can rename, and it is a bounded, visible collision rather than a silent one.

**A post and its replies must keep sharing a directory**, which is 0005's whole reason. Both discussion skills use the same `discussion` slot, so the board-keyed join survives the change unaltered. A skill that invented its own slot word would reopen 0005.

**Three run-key components now have to agree across five skills and four graders.** The vocabulary is small enough to hold in one place, and disagreement is the defect rather than a permitted divergence — which is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s stated test for when a helper may be shared, passed rather than assumed.
