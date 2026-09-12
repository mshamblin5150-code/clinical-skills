# A carried claim is corrected where it stands and #436 never ruled it

Sixteen tracker records, two ratified records and a standing practice rest on one sentence:

> *on [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436)'s ruling: a correction below the advice is not a correction for anyone who acts on the advice*

[#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) rules nothing about corrections. It is titled *"guidelines_recs bound records are labels: the 160-char window cuts mid-word and reads the wrong recommendation for 44.5% of the corpus"*, and it was closed on 2026-08-29.

Found by [#803](https://github.com/mshamblin5150-code/clinical-skills/issues/803)'s sweep on 2026-09-06 and filed as [#934](https://github.com/mshamblin5150-code/clinical-skills/issues/934). Re-derived 2026-09-12 against a full REST harvest, proven complete against the GraphQL issue and pull-request totals and the comments probe's last page before it was read. That proof is required rather than tidy: [#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993) records the committed REST reader returning short valid populations with status 0, and a #934 comment asked for the proof by name. The harvest's size is dated and is deliberately not restated outside this paragraph. Grilled 2026-09-12; the clinician ruled every point below on the same day.

**The failure this repairs is not a broken link.** A dead citation announces itself; a live one to an unrelated closed ticket does not, and the rule being miscited is itself the rule about corrections, so the failure it describes is the one that protected it.

## Measured before ruling

### The population, and it is not the one the ticket recorded

Counted from `repos/OWNER/REPO/issues?state=all` plus `issues/comments`, because `gh issue list` excludes pull requests. The predicate is three phrase variants — `below the advice`, `acts on the advice`, `acting on the advice` — and a `#436` or `issues/436` reference in the same paragraph. #934's own body and comments are excluded, since the ticket quotes the sentence in order to report it.

| | count | members |
| --- | ---: | --- |
| issue bodies | 8 | 772, 773, 777, 802, 816, 823, 826, 864 |
| comments | 8 | 87, 756, 772, 781, 795 ×2, 828, 836 |
| records carrying the sentence | 16 | 14 distinct issues, 0 pull requests |
| of those citing #436 beside it | 15 | #781's comment cites nobody |

**#934's list is two members off today.** It names #866, whose body was rewritten on 2026-09-10 and lost the footer with it — a member leaving the population by accident rather than by repair. It does not name #87 or #756, which acquired the sentence after it was filed. Every count in that ticket's history has been hand-maintained and every sweep has found it stale.

### The sentence's origin cites nobody

[#781's comment of 2026-09-04](https://github.com/mshamblin5150-code/clinical-skills/issues/781#issuecomment-5537515531) reasons it out in its own words, as the justification for editing a body rather than adding a fifth comment:

> *the premise was **advice**, sitting in the body, telling a reader to use `--text` as a pre-flight. A correction one screen below advice is not a correction for anyone who acts on the advice.*

That comment is the whole authority behind sixteen records, and it makes no claim to be one. [#773](https://github.com/mshamblin5150-code/clinical-skills/issues/773)'s body half-knows this: it cites *"#436's ruling and #781's 2026-09-04 precedent"*, treating #781 as the practice and #436 as the ruling, when #781 is the only one of the two that exists.

### ADR 0016 rules the neighboring thing

[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) is *"An ADR number is claimed when it is handed out, and a ratified record's facts may be corrected in place"*, ratified 2026-08-23 on #452 and #459. Its rejected-option paragraph carries the reasoning verbatim:

> **Correcting ADR 0007 by annotation only.** Rejected. A reader opens the file, reads the figure at `:40`, copies it, and never scrolls to the footnote — which is the failure this repo keeps recording.

**Its ruling scope is a ratified record.** A ticket body is not one, so nothing in ADR 0016 reaches the tracker, and the two instances differ in their ground: ADR 0016's was a **figure** nobody acts on and everybody copies, #781's was **advice** a builder was about to run.

### Two ratified records carry the miscitation

[ADR 0140](0140-a-measurement-must-discriminate-and-a-re-run-is-not-a-re-derivation.md) names the real authority and then adds five words that are false:

> ADR 0016 rejects annotation-only correction in as many words — *a reader opens the file, reads the figure, copies it, and never scrolls to the footnote* — and #436 rules the same.

[ADR 0146](0146-both-apa7-sections-append-and-the-translation-rule-lives-once-at-section-31.md) is the stronger instance, because it reproduces the miscited rule as a full sentence in a ratified record:

> Corrected in place on #816 under [#436]'s rule that a correction below the advice is not a correction for anyone who acts on the advice.

### ADR 0169 ruling 7 is both the nearest precedent and the contradiction

[ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md) ruling 7, ratified 2026-09-10, refuses a bottom footer for the Filed-from line on ADR 0016's reasoning — the same argument, ruled for one line while the general case stayed unruled — and then grants what this record takes away:

> Other corrections of the body may go anywhere below the line, never above it.

`docs/agents/issue-tracker.md` carries the implementation of that ruling in its Filed-from paragraph, in the same words.

### The predicate needs no constant, which was measured rather than assumed

Across the fifteen citing records the citation sits between **24 and 120 characters** from the sentence. A character window is flat from 120 upward — 15 records at 121, at 500, at 100,000 — so any value inside it is a value named on an unbounded plateau, and this repo has a recorded cost for naming one at an edge.

**A same-paragraph predicate reproduces the same fifteen with no constant at all**, and excludes #781's comment, which carries the sentence and cites nobody. The two instruments agree on every member of the population, and only one of them has a number to defend.

## Ruled 2026-09-12

### 1. The rule is ruled here rather than repointed at ADR 0016

#436 was cited because nothing true existed to cite. Repointing sixteen records at ADR 0016 would fix the link and leave the hole: a rule that binds four `ready-for-agent` tickets would still have never been ruled for the tracker.

### 2. The unit is a carried claim

A statement in a tracker body that a reader takes away and uses elsewhere: an instruction, a build premise, a *Done when* item, a figure, a coordinate, a citation. **Not advice alone.** Splitting advice from figures would put this repo's two recorded instances under two rules with the same reasoning, and the class this record was filed over — a wrong citation — is neither.

Distinct from a **dated reading**: a sweep verdict that was true when written. A reading is superseded, never corrected.

### 3. A carried claim is corrected in place, and a dated line beneath records what it said

The sentence carrying the claim is edited where it stands. A dated line directly beneath it states what it said and why it changed. **A correction below a carried claim reaches nobody who carried it**, which is ADR 0016's reasoning and #781's, stated once for the tracker.

The **Filed-from line** is the declared exception and keeps ADR 0169 ruling 7's arrangement: it is append-only, its own correction goes on its own dated line directly beneath it, and nothing goes above it. A body carrying the implementation map's exact producer stamp is outside this rule, as it is outside ADR 0169's.

### 4. A comment's reading is never corrected; its citation is, once

The eight comments have their citation corrected in place and **nothing else** — no re-verdict, no re-measurement, no rewriting of what the sweep found — with one dated line at the foot of the comment. All sixteen records were published by the same account, and 137 of the tracker's comments have already been edited after posting, so this is that account correcting its own past sessions rather than editing a third party's record. GitHub retains the prior revision and this repository has already ruled that acceptable.

**This authorizes one repair of one defect class and is not a standing permission to edit comments.** A dated reading deserves protection; a statement of fact that was false the moment it was posted has nothing to preserve.

### 5. The in-line replacement is ADR 0016, and the dated line names this record

This record postdates every record being corrected, and most of the sixteen state **the ground a past session acted on** — *"Edited in place rather than commented, on #436's ruling: …"* — so pointing them here would write an anachronism into every one of them, two being ratified records. Naming ADR 0016 in line makes the sentence true as a historical statement and checkable today; the dated line beneath carries this record as the rule that now governs.

ADR 0140's repair is therefore deleting the five words *"and #436 rules the same"* and adding the dated line. **It carries a second instance the phrase predicate cannot see** — *"which #436's ruling makes feel authoritative"*, attributing the same phantom rule in different words — and both are repaired together.

### 6. This supersedes one sentence of ADR 0169 ruling 7

*"Other corrections of the body may go anywhere below the line, never above it."* is superseded by ruling 3. Its remaining sentences — the append-only line, its correction directly beneath, no escape — are untouched and become the declared exception.

**Superseded by quotation rather than by ordinal**, and that is this record's own subject arriving inside it: the sentence above is ruling 7's **third**, a first draft of this heading called it the second, and ruling 7's second sentence is the one ruling 3 *preserves* — so a reader who counted would have withdrawn the exception this record grants. A live citation resolving to the wrong thing is what ADR 0191 exists to repair, and it was caught by review rather than by anything that fails.

*"May go anywhere below"* is a granted permission and this withdraws it, which is why it is a supersession and not a clarification. **ADR 0169 carries a dated marker saying so**, on [ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)'s arrangement rather than [ADR 0058](0058-a-bound-label-reads-to-its-own-recommendation-and-every-window-adr-0029-measured-was-forward.md)'s: a reader arriving at ADR 0169 by an old link must not be standing on a falsified ground with no marker on it, and 0058 states that reason while leaving ADR 0029 unmarked, so following it would have been inheriting the sentence without the act. The marker records the supersession and changes no ruling.

### 7. The written home is `docs/agents/issue-tracker.md`, in one paragraph

The two rules land as one paragraph rather than two sentences a reader must reconcile, because two copies of one rule is the arrangement [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled insufficient and the reader misled is whichever copy they read first.

Both terms enter `CONTEXT.md`'s **Tracker** section with their `_Avoid_` rows. **`_Avoid_` on the unit lists *advice***, which retires that word going forward while leaving every historical instance of the sentence standing and correctly attributed.

### 8. The pairing is reported at publication and never refused

One advisory row in `tools/tracker_publish_hook.py`: a publication whose paragraph carries the rule sentence beside a `#436` reference prints a line naming the true authority, at the moment the copy happens. It **advises and never denies**, because a record legitimately discussing this defect quotes the sentence beside #436 on purpose — #934's body does, its sweep comments do, and so does this record — which is `spelling_scan`'s mention-versus-use problem. **Tracker prose has no mention-versus-use exemption**: the two this repository has are a backticked span in a file a scanner walks and a counted Python pragma, and the own-line marker it built when neither transferred is a tracked-file device, not something a published comment can carry.

A general check is refused and stays refused: **nothing can verify that a cited ticket says what a sentence claims it says.** This grades one literal pairing, grown on the instances recorded above, which is the bar `spelling_scan`'s table grows on.

### 9. The record repair is a second ticket, and its denominator is derived for one part and enumerated for two

The tracked half — this record, the two terms, the paragraph, the advisory row and its tests — is an ordinary pull request. #934 is respecified to the record repair alone.

**The repair has three populations and only one of them is derived.** Conflating them is how a closing condition comes to mean nothing:

- **The tracker records citing #436**, derived by the same paragraph predicate the advisory row uses, over a REST harvest, excluding #934's own body and comments — which quote the sentence in order to report it, and which the predicate fires on. That exclusion is one record number rather than a kept list, so the derivation survives it.
- **#781's comment**, which carries the sentence and cites nobody. There is nothing to correct: it is the origin, and it is a member of the phrase population and of no repair.
- **The two ratified records**, ADR 0140 and ADR 0146, which are tracked files the predicate never reads and are therefore enumerated by name. ADR 0140 carries two instances and one of them states the miscitation in words the predicate cannot match at all.

**The first population's closing condition is a command's output rather than a list somebody keeps**, and that is what #934 has never had: every count in its history was hand-maintained and every sweep that checked one found it stale. The other two are closed sets of known size, and saying so is the honest form — **a derived count that silently excluded a member the instrument cannot see would be this repository's extractor-coverage rule broken inside the record citing it.**

**What is not built is the walk itself.** `retired_citation_paragraphs` takes one string; nothing here harvests the tracker and applies it. #934's build spec carries that walk, importing the predicate rather than restating it, on `tracker_filed_from.py --harvest`'s precedent.

## Rejected options

**Repoint the sixteen records at ADR 0016 and write no new rule.** Rejected. Cheapest, and it leaves the tracker-facing rule unruled while sixteen records assert it — one degree less wrong than today rather than right.

**Keep "advice" and define it wide in the glossary.** Rejected. A reader who has not opened `CONTEXT.md` reads the plain English word, reads it narrowly, and corrects a figure by footer. That failure is silent, which is the class this record exists for.

**Leave every comment alone.** Rejected. The alternative repair is one new comment per affected ticket — fourteen more comments, each sitting below the miscitation it corrects, which is the defect wearing the repair's clothes. The 2026-09-06 wave that put the sentence on #828, #795 twice, #836 and #772 was two comments 31 seconds apart and three more inside 11 minutes, ten and a half hours later — each copying the last. *(A first draft of this sentence read "five comments in fourteen minutes", which re-derives to neither span: a figure a reader carries away, wrong in the record that defines what a carried claim is, caught by review.)*

**Swap the citation with no dated line**, on the ground that GitHub's retained revision is the record. Rejected. A record that changed with no marker is one the next sweep re-derives as never having been wrong, which is how this survived seven sweeps.

**Point every corrected record at this ADR.** Rejected under ruling 5. Uniform, one string, and it makes an explicit claim about what a past session relied on false in a fresh way.

**Refuse the pairing at publication.** Rejected under ruling 8. It refuses the ticket documenting the defect and every sweep comment reporting it, and any escape marker is one a copying session can paste too.

**A character window for the predicate.** Rejected on measurement. The plateau is unbounded above 120 characters, so every value inside it is arbitrary, and the same-paragraph rule reproduces the identical population with nothing to defend.

**One ticket carrying both halves.** Rejected. Eighteen tracker publications as the tail of a build session is the shape that has already exhausted GitHub's secondary rate limit here, and a session dying mid-tail leaves a half-repaired population with nothing recording which half.

## Consequences

**The sixteen records stop resting on a phantom**, and the two ratified records stop telling a reader that a closed extraction ticket rules corrections.

**One sentence of a two-day-old ratified record is superseded**, which is the price of ruling the general case after the special one.

**A wrong citation is now cheaper to repeat than to detect, by exactly one advisory line.** The row catches the one pairing with evidence behind it and no other, and says so in its module.

**The repair itself is measurable.** Its denominator is derived from the tracker rather than kept by hand, which no earlier count in #934's history was.

## What this does not reach

**Any wrong citation other than this pairing.** A paraphrase of the sentence, the same sentence citing a different wrong ticket, or a correct-looking citation to a record that rules something else are all invisible to the advisory row and to every other instrument here. The general form is not buildable and no session should refile it.

**A publication that never runs the hook.** The row lives at one publisher's pre-publication seam; anything published by another route is ungraded, as `tracker_publish_hook.NOT_REACHED` already states for its other rows.

**GitHub's retained revisions.** Every corrected body and comment keeps its pre-repair text, readable by anyone with read access and unreachable by the API — ruled acceptable on 2026-08-19 and unchanged here. Pre-repair text therefore remains copyable, which is the reason the advisory row exists at all rather than trusting the repair to be self-sealing.

**Whether a carried claim is true.** This rules where a correction goes, never that anybody noticed the thing needed correcting.
