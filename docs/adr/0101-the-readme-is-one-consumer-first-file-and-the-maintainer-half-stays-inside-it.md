# The README is one consumer-first file, and the maintainer half stays inside it

`README.md` opened on the directory layout, then wiring, then the PHI firewall and the hook install. Every word of it was true and none of it told a reader what the skills do or how to invoke one. The repository is public. A person landing on it learned where `scratch/` is before learning there is a skill that turns shorthand into a note.

[#401](https://github.com/mshamblin5150-code/clinical-skills/issues/401) was filed on that on 2026-08-21 and its first decision was *audience* — stated in the ticket as *"a consumer with no interest in the tooling, or a maintainer? Both is possible and is a structure decision, not a paragraph."* Ruled by the clinician on 2026-09-01.

## What made it a decision rather than an ordering

The obvious move is to split: a consumer README and a `docs/maintaining.md`. The maintainer material is genuinely a different document for a different reader — the layout block, the worktree mirror trap, the guideline corpus rebuild, the tooling. Nothing in it is needed to *use* a skill.

**The PHI section is what stops that being clean.** It reads as maintainer material — hooks, `tools/phi_scan.py`, `--no-verify`, exemption pragmas — and the person who most needs it is a consumer. They run `clinical-note` against real bedside shorthand and, within a minute, hold a patient record in `scratch/`. Move the PHI section into a maintainer document and the one safety instruction in the repository is now in the file the person generating PHI has no reason to open.

So the decision is not *which reader* but *whether the two readers can be given separate files at all when one section belongs to both*.

## Considered options

**Split into `README.md` and `docs/maintaining.md`, PHI duplicated into both.** Rejected outright. Two copies of a safety instruction, each editable without failing anything, is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) applied to the highest-stakes paragraph in the repository — and #220's finding is that the reader misled is whichever copy they happened to open. This repository has recorded that failure more often than any other.

**Split, with PHI kept only in the consumer README.** Rejected, and it was the closest alternative. It works for PHI and fails on the install steps, which the grilling then made much longer: a plain-language walkthrough with a `git clone`, a mirror command and a setup invocation. Those same commands are what a maintainer runs, so either the maintainer document repeats them or it links back — and the version that repeats them is #220 again on the steps most likely to change. **The general shape is that any split puts some paragraph in both files or in the wrong one**, because the two readers overlap at exactly the points that are hardest to keep true.

**Keep the README maintainer-first and prepend a consumer section.** Rejected. It leaves the layout block and the wiring discussion between the reader and everything they came for, which is the defect as filed with a paragraph added on top.

**One file, consumer-first, maintainer material below the fold.** Chosen.

## Decision

One `README.md`. Sections in order: what the repository is, the skills grouped by what they produce, what ships with them, the voice model, getting started, PHI, then *Maintaining* — which holds the layout block, the agent wiring, the mirror trap, the guideline corpus rebuild, and the tooling. Everything currently in the file survives; it moves.

**PHI sits above the fold and before *Maintaining*, and it is rewritten around a fact the old section never stated**: nobody but the maintainer can push to this repository. A consumer's clone is theirs, their commits are private to their machine, and the real hazard is a fork they make public — which [#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) established is unretractable, since GitHub retains earlier revisions of edited files. Leading with the no-push fact is what lets the fork warning land as the one real hazard rather than as one item in a list.

**The cost is accepted and named.** A reader evaluating the repository scrolls past a long beginner walkthrough to reach the maintainer material. That is the right trade because the evaluating reader still gets *what it does* and *what ships* in the first two screens, which is the entire complaint #401 was filed over, and because the alternative charges a beginner a wrong answer on the day two files disagree.

## What this does not decide

**It does not make the README a maintainer document.** `AGENTS.md` remains deliberately sufficient on its own, the clinical skills depend on none of `tools/`, and the *Maintaining* section is explicitly marked as not needed to use anything. #401's second prohibition — *nothing that makes the tooling read as required* — is why the only `pip install` in the repository stays below the fold and why the consumer's guideline refresh is one line reading `git pull`.

**It does not settle what the README may claim.** Currency, coverage and standing are [#772](https://github.com/mshamblin5150-code/clinical-skills/issues/772) and [#767](https://github.com/mshamblin5150-code/clinical-skills/issues/767), and the gap between what a document *is* and whether it still *stands* is recorded in `CONTEXT.md` rather than here.

**It does not exempt the file from a gate.** `README.md` was the only substantial tracked prose in the repository with nothing binding it, which is how #401 came to be filed against a body asserting *"Five of them"* while the tree held seven. The rewrite binds skill-table membership in `tools/test_skill_agreement.py`; #772 owns the generated currency block; [#776](https://github.com/mshamblin5150-code/clinical-skills/issues/776) owns whether the file joins the blind-instruction guard. **A single file was chosen partly because one file can be gated once**, and three copies of a claim cannot.
