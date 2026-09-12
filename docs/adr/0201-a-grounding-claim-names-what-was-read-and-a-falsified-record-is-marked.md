# A grounding claim names what was read and a falsified record is marked

**Measured at:** 2f814d1f9d6e6bf0b86b6730eaab85a049531afc

[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md)
line 9 grounds its in-text legal form on *"guide consensus across seven independent university
library guides"* and cites four. [#987](https://github.com/mshamblin5150-code/clinical-skills/issues/987)
reports the figure, its copies, and a path in the same sentence that no longer exists. Grilled
2026-09-12; the clinician ruled every point below on the same day. Freshness gate `FRESH` at both
checkpoints, `main` having advanced to `2f814d1f` mid-session, where every measurement below
re-derived unchanged. Nothing is built here; this is the record the build reads.

**The ticket is right about the sentence and wrong about three things around it**, and each was
wrong in the direction that made the repair look bigger than it is.

## Measured before ruling

### The figure was false at birth and its origin names nobody

`db31e493`, the record's first commit, already reads *seven* and links four. There is no lost
seventh guide to recover. [#497](https://github.com/mshamblin5150-code/clinical-skills/issues/497)
is the originating ticket, and across its body and all ten comments the string `libguide` appears
**zero** times and no institution is named; its 2026-08-26 ruling comment carries
*"Guide consensus across seven university library guides"* with no links at all. So the figure is
unsupported in the record, in the ticket that filed it, and in the tree.

### `independent` is the false word, not the numeral

All four cited pages return real documents — HTTP 200, 30 to 63 KB, no interstitial, measured
2026-09-12. They are four institutions and they are not four attestations:

- **CCCS is a verbatim clone of a fifth institution's box** — 751 characters, `difflib` similarity
  **1.0000** against `libguides.umgc.edu/c.php?g=756085&p=7242692`, down to a shared stray
  zero-width space.
- **Three of the four reproduce one example string**, `Protection of Human Subjects, 45 C.F.R. § 46
  (2009)`, identical in name, title number, section and year. Bradley's carries a stray period,
  which is a transcription artifact.
- **Two of the four state the claim directly.** Bradley gives only the general legal in-text rule
  and no regulation in-text example. **NMU carries no federal regulation example at all** and
  borrows the template for a school-board policy.
- **The pages name their own upstream and it is the manual.** CCCS: *"See Publication Manual,
  11.7."* NMU: *"the Federal regulation, codified template which appears in the APA Manual, 7th
  ed. p. 365."* None of the four cites `apastyle.apa.org`.

So the sentence was a fourth-hand read of the *Publication Manual* §11.7 while declaring itself
*not a read of APA's own page*. Only the surrounding commentary is independently written, and the
one page whose commentary is genuinely its own does not cover federal regulations.

### The ground was already replaced, twice, and the second landed before the ticket

[ADR 0088](0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md)
ruling 6 is headed *"the sheet's authority is APA's own page, and the library-guide caveat is
retired"*, and `0088:94` confirms ADR 0039 rulings 1 and 5 *"from the source rather than from guide
consensus"*. Then `3a1b5215`, **2026-09-08T22:50:34Z**, gave `skills/_shared/reference/apa7.md` §8
the provenance *"APA Style's Nursing Student References page, item 14, read 2026-08-30;
Publication Manual §§11.3 and 11.5, read 2026-09-08."* That commit is an ancestor of `f7fd264`,
the commit #987's own branch-state block declares it rests on, and it landed **69 minutes** before
the ticket was filed. `apa7_coverage.py --quiet` reports 345 manual items, 345 read to root, 0
never checked, 0 gone stale. The sheet carries no library guide and no Imperva caveat anywhere.

### The path is already ruled, and the other way

[ADR 0131](0131-the-shared-sheet-directory-moves-whole-and-the-mirror-gains-a-non-skill-rule.md)
ruling 6, 2026-09-05: *"**The mentions in ratified ADRs stay.** A path in a ratified record is a
dated statement about the tree at ratification, and editing one to keep it true would falsify the
record."* Twelve ADR files carry the retired path and **zero** files outside `docs/adr/` do; the
directory was scoped out deliberately. ADR 0039's mention is inline code, so that record's own
correction — a Markdown link from `docs/adr/` into a moved directory is a suite failure with no
permitted repair — does not reach it either.

**What ruling 6 does not cover is a clause that instructs.** ADR 0039's is
*"That caveat travels with the claim, on `...apa7.md`'s terms"* — a live pointer, and the caveat it
points at was retired by name and is absent from the sheet. Repointing it to
`skills/_shared/reference/apa7.md` would resolve the path and still point at nothing.

### ADR 0145 recounts the figure in order to revive the caveat

`0145:15` reads *"The guide-consensus caveat travels with ADR 0039's legal claims for the separate
reason in ruling 5, not because the site cannot be read."* Its ruling 5 rests on *"APA publishes no
legal reference examples"* and concludes *"There is no rule to check the scanner against. Settling
it needs a clinician ruling on which convention this repository adopts."*

**Both halves are now false, and neither by this session's doing.** `0088:84` had already found the
form published on a page outside the examples index that `0145:83` checked, three days earlier, and
ADR 0145 does not cite ADR 0088 on the point. Then §11.5 — `read-root` in `apa7-coverage.md`,
checked 2026-09-08 — records *"The in-text key is popular/official act name plus that year, even
when it differs from the year embedded in the act's name."* That is St. Scholastica's convention
and it refutes Franklin's, which is the contradiction ruling 5 declared unresolvable.
[#941](https://github.com/mshamblin5150-code/clinical-skills/issues/941) read it and closed on it at
**2026-09-08T21:52:41Z**. ADR 0145 carries no correction footer and no marker; neither does ADR
0039. ADR 0088 carries two.

**So ADR 0088 and ADR 0145 are not two copies of one figure.** One recounts it to overturn it and
one recounts it to keep it alive.

### The ticket's own copy count is wrong, by its own instrument

#987 reports the figure *"a fourth time in #976's own body."* It is not there.
[#976](https://github.com/mshamblin5150-code/clinical-skills/issues/976)'s only `seven` is
*"Scope is nine chapters, not seven"* — the manual read's chapter scope. The real fourth site is
#497's ruling comment, which #987 does not name. A search for the numeral that never checked what
the numeral counted, inside a ticket about a figure nobody re-derives.

### Unmarked supersession is a class, and its population is not known

Across 200 ADRs, **15 of 31 superseded targets carry no marker** a cold reader would see. ADR 0097
ruling 7 is one, and is doubly unmarked — ADR 0130 supersedes its ruling 6 in part as well. **15 is
a floor.** The instrument is a supersession-verb-plus-ADR-number matcher, and the instance it was
sent after was invisible to it: `0131:7` reads *"ADR 0097 ruling 7 refused to move `apa7.md` alone
and declared the set a separate question. This is that question, answered"* — no verb anywhere. A
second pass on falsification phrasings returned roughly forty more ADR-naming lines of which the
strongest dozen were read.

## Ruled 2026-09-12

### 1. The corrected sentence states no figure and names what was read

`seven` and `independent` both go, and no number replaces them. Four links stay and become the
statement: a reader re-derives the whole claim with four `curl`s. The sentence records that the
guides are not independent attestations, that two of four state the form, and that the shared
example reproduces the *Publication Manual* §11.7 / p. 365 template two of the pages cite by
number.

**`four` was refused rather than overlooked.** It is true of the links and false under
*consensus*, which asserts convergent attestation that the measurement says is absent — a true
number under a word that stays false. It also leaves a figure for the next record to copy, and
this one has been copied three times. Eliminating the figure is the only permanent answer to
#987's own *"a fifth copy"*.

### 2. Line 9 is corrected in place under ADR 0016, with a dated line

ADR 0039's rulings begin at `:45`; line 9 sits in the narrative section above them. It is
therefore not *"the paragraph that does the deciding"* and
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
permission applies without qualification. **No ruling of ADR 0039 changes.**

### 3. The superseded grounding is marked, not edited

*"and **not** a read of APA's own page"* was true on 2026-08-26 and the Imperva measurement behind
it still reproduces — 200, 212 bytes cold, and a 1,033-byte variant carrying an incident ID, on
every `apastyle.apa.org` URL probed. It is a dated statement of what that session stood on, so a
dated marker records that ADR 0088 ruling 6 retired the caveat and that the manual read replaced
the ground. The sentence is not rewritten.

### 4. The pointer clause is deleted rather than repointed

ADR 0131 ruling 6 protects the *path*; nothing protects an instruction to follow a rule that has
been retired. Repointing resolves the path and preserves a pointer to nothing, which is worse than
a stale one because it reads as current.

### 5. ADR 0088 and ADR 0145 take different treatments

ADR 0088 gets a pointer to ADR 0039's grounding, carrying **no number**, so it cannot go stale when
the guides are next measured. ADR 0145 gets the same pointer **and** one dated marker recording
that *Publication Manual* §11.5 supplies the rule its ruling 5 said did not exist, that #941
discharged the deferral on 2026-09-08, and that `:15`'s revival of the caveat falls with the
premise. **Ruling 5's text is left as written**, being the dated record of what was decided on
2026-09-07 — ADR 0033's arrangement, by way of ADR 0169's.

### 6. #497's ruling comment is left exactly as posted

`docs/agents/issue-tracker.md` states that *a published comment is not corrected in place* and that
editing one *"is a per-defect authorization a ruling has to give."* **This ruling declines to give
it.** ADR 0191 ruling 9 already ruled the shape, four days ago and in the same breath as the
authorization it granted: *"**#781's comment**, which carries the sentence and cites nobody. There
is nothing to correct: it is the origin, and it is a member of the phrase population and of no
repair."* #497's comment is where the figure entered. Editing it erases that, and a per-defect bar
applied a second time within a week stops being one.

### 7. Unmarked ADR supersession is a separate ticket, and ADR 0097 goes with it

Fifteen-plus records, an underived population and an unruled rule is a grilling of its own and a
larger one than #987. **Taking ADR 0097 alone would be repairing 1 of 16 because it is the one this
session already had open**, which is the relevance filter `CLAUDE.md` rules against for sweeps.

Ruling 5's marker is not a member of that class and does not prejudge it: ADR 0145 ruling 5 was
falsified by a manual read and a closed ticket rather than by a later ADR, and it appears nowhere
among the 31.

### 8. #987 corrects itself at respec

Its #976 miscount, #497's comment as the unnamed fourth site, and the retirement of decision 1's
`ready-for-human` premise — the Bookshelf read it asks for landed 69 minutes before it was filed.

## Rejected options

**Correct `seven` to `four` in three records.** #987's decision 1, and the cheap answer. Refused on
the measurement in ruling 1: it repairs the numeral and leaves *independent* and *consensus*
standing over four pages that are one upstream seen four times, one of them a verbatim clone.

**Commission a Bookshelf read and label the ticket `ready-for-human`.** #987's own preferred branch.
Refused because the read exists: §§11.3 and 11.5 are `read-root` in `apa7-coverage.md`, dated
2026-09-08, with evidence and an independent refutation, and `apa7.md` §8 already carries them as
provenance.

**One marker over the whole of line 9.** Argue the numeral is part of the same dated statement,
because the session believed it had consulted seven. Cheaper and touches nothing. Refused on ADR
0016's own reasoning at `:52` — *"A reader opens the file, reads the figure at `:40`, copies it,
and never scrolls to the footnote"* — which is not hypothetical for a figure already copied three
times.

**Leave ADR 0145 to #941's closure.** Defensible: the discharge is recorded where the work was
done. Refused because the tracker is not where a ratified record is read, and #987 found ADR 0145
by following the figure, which is evidence that it is.

**Move the corrected statement into `apa7.md` or `apa7-coverage.md`.** Refused twice over. The
sheet's authority is the manual and ADR 0088 ruling 6 retired the guide caveat by name, so this
would reintroduce what that ruling removed; and every Chapter 11 registry row binds §8's digest, so
it would move twelve rows to stale for a sentence about a source the sheet no longer rests on.

**Authorize the #497 comment edit with one dated line.** Refused in ruling 6, and it is the closest
call here: the origin argument protects a *dated reading*, and this is a statement of fact that was
false when posted.

## Consequences

**ADR 0039 stops being re-derivable by counting and starts being re-derivable by fetching.** Four
`curl`s settle the sentence, and no figure in it can go stale.

**Two ratified records stop contradicting each other in silence.** ADR 0088 and ADR 0145 disagree
today about whether APA publishes a legal reference example; ruling 5's marker records that the
manual settled it.

**A reader arriving at ADR 0145 by an old link stops standing on falsified ground with no marker on
it**, which is ADR 0191 ruling 6's stated reason for marking ADR 0169.

**The unmarked-supersession class becomes visible as a class**, with its population declared
underived rather than inherited as 15.

## What this does not reach

**Whether the four guides state APA's rule correctly.** They agree with the manual read at §§11.3
and 11.5, and this record grades their independence rather than their accuracy.

**Whether any ruling of ADR 0039 is right.** Rulings 1 and 5 were confirmed from the source by ADR
0088 and are untouched here. This record governs the stated ground.

**The other fourteen-plus unmarked supersessions**, and whether a superseding ADR must mark its
target at all. ADR 0145 declined to edit ADR 0135 deliberately, so *leave the target alone* is a
live ratified position and not an oversight to be swept up.

**That anybody notices the next one.** Nothing checks that a ratified record's ground is still
what it says, and ADR 0016 already declares that gap at `:64`.
