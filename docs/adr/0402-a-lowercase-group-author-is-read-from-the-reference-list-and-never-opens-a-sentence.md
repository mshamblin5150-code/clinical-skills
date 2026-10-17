# A lowercase group author is read from the reference list and never opens a sentence

**Measured at:** d366ac2f1e6bdc34870718044c209b795df44998

[#1797](https://github.com/mshamblin5150-code/clinical-skills/issues/1797) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 3) on 2026-10-12. A drug label's
publisher renders its corporate name with a lowercase first letter; written that way as the group
author, `tools/reference_scan.py` did not resolve the in-text citation to its entry, and the sitting
capitalized the name in both places so the scan would pass. The ticket asked two things: what APA 7
requires for such a name, and whether the scanner's join should tolerate a case-only difference.
Grilled 2026-10-17 against `main` at the commit above, where the freshness gate read `FRESH`. The
clinician ruled every point below in that session, one question at a time. **Nothing is built
here; this is the record the build reads.**

## Measured before ruling

**The join already ignores case; recognition is what fails.** An invented lowercase group author
was driven through `reference_scan.read_document` and `survey` in six shapes. A capitalized
citation against a lowercase entry, parenthetical or narrative, reports nothing. A lowercase
parenthetical citation against the same entry reports only `uncited-entry`: `citation_key` requires
the first word to look like an author (a capital, a quoted title, or a `PARTICLES` member), so the
citation is never read. A lowercase narrative citation reports `uncited-entry` and
`unlisted-citation`, because `NARRATIVE`'s name pattern also requires a capital and reads only the
capitalized second word as the author. The `(systolic, 2000 to 3000)` control stays clean. So the
ticket's second decision, a join that tolerates case, describes a defect that does not exist, and
**capitalizing only the in-text citation would have passed** — the sitting's change to the
reference entry was not even needed to satisfy the scan.

**The existing spelling row deliberately excludes case.** `citation-author-spelling` fires when two
words fold to the same letters and differ after `.lower()`, so a diacritic difference is a finding
and a capitalization difference is silent.

**APA settles only people.** The #1794 sweep found that `apa7.md` section 39 already says to
preserve group names as published, including capitalization, which settles the reference entry.
APA's own pages, read as archived snapshots of apastyle.apa.org because the live site served a bot
block, were re-derived word for word: the reference-element page says "Retain the author's
preferred capitalization", with `hooks, b.` and `van der Waal, P. N.` as its examples, and the
capitalization page says to capitalize the first word of a sentence "unless the sentence begins with
the name of a person whose name starts with a lowercase letter." That exception names a **person**.
No APA page reached, and no record of #976's signed-in Manual read of §6.14 or §9.11, addresses a
lowercase **group** name opening a sentence.

## Ruling 1 — a lowercase author is read only when the reference list names it

The scanner accepts a lowercase first word as a citation author, in parenthetical and narrative
citations alike, only when an entry in the draft's own reference list has that author. The list
supplies the vocabulary, so `(systolic, 2000 to 3000)` stays unread unless some entry's author is
`systolic`. Accepting any lowercase first word was declined because it reopens that false alarm on
every clinical draft. Leaving the scanner unchanged and declaring the gap was declined because the
next sitting faces the same choice and changes the source's rendering again — the outcome the
ticket says the grader must not cause. The cost is declared rather than closed: **a lowercase
author cited with no entry at all stays invisible**, so `unlisted-citation` cannot see it.

## Ruling 2 — a lowercase group name never opens a sentence, as a house rule

The reference entry and every mid-sentence citation keep the group's published lowercase, which
section 39 already requires. A lowercase group name never opens a sentence; the writer rewords so
it falls mid-sentence or in parentheses. `apa7.md` writes this as the house's rule and says so,
not as APA's text. Keeping the lowercase at a sentence opening by analogy to APA's person rule was
declined because it writes an inference into a sheet verified against APA. Capitalizing it was
declined because it departs from the publisher's rendering at exactly the spot the ticket objects
to, and makes the citation disagree with its entry. A targeted signed-in Manual read was declined
for now because #976's read of the governing sections records nothing on the case; it remains
available if a grader disputes the house rule.

## Ruling 3 — a capitalization-only difference is a spelling finding

With Ruling 2, every legitimate citation copies its entry's capitalization exactly, and APA's
person rule says the same for people. `citation-author-spelling` therefore widens so that a
difference in capitalization alone is a finding. Its message tells the writer to match the entry
and, where the name opens a sentence, to reword. A separate capitalization row was declined: its
remedy differs from the spelling row's only at a sentence opening, which the message can carry.
No row was declined because the grader would then stay blind to the rendering change this ticket
is about.

## Ruling 4 — a lowercase group name opening a sentence is its own finding

A new row fires on a narrative citation whose matched entry is a group author with a lowercase
first letter, where the citation opens a paragraph or follows sentence-ending punctuation. Telling
a group entry from a person's is the build's to establish and test: `personal_authors` was tried
during the grilling and returned nothing for `zentrova Labs.`, `hooks, b.` and
`van der Waal, P. N.` alike, so it does not separate them as called there. Where the position is
ambiguous, such as after an abbreviation like `e.g.`, the row does not fire, and that limit is
declared. Leaving the house rule to the post-draft
reader was declined: a written instruction cannot fail a draft, which is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s reason for every grader
here.

## Build checklist

- `skills/_shared/reference/apa7.md`: beside section 39's preservation sentence, the sentence-opening
  house rule, marked as house rule and citing APA's person-only exception; the capitalization
  paragraph's "Capitalize sentence openings" points to it.
- `tools/reference_scan.py`: `citation_key` and the narrative reader admit a lowercase first word
  when it resolves to a reference-entry author; `citation-author-spelling` compares case; the new
  sentence-opening row with its `apa7` binding; `CITATION_RESOLUTION_NOT_REACHED` or
  `NOT_REACHED` rows for the unlisted lowercase author and the ambiguous sentence position.
- `skills/practicum-case-study/SKILL.md` step 7's defect table and any other table that writes out
  `reference_scan.KINDS` gain the new row.
- Tests drive, through `read_document` and `survey`, a lowercase group author in parenthetical,
  mid-sentence narrative and sentence-opening narrative position; a capitalized citation against a
  lowercase entry; a lowercase person particle; the `systolic` control with and without a matching
  entry; and an abbreviation-ambiguous opening.
- **Measure the widened spelling row against every committed worked reference list and test
  before believing it moves nothing**; a case-only difference already in the tree would start
  failing.

## What this record does not reach

- **A lowercase author cited with no entry.** Ruling 1 reads lowercase authors only through the
  list, so a citation whose entry is missing is not seen.
- **Whether APA would accept the house rule.** Ruling 2 avoids the unsettled case rather than
  settling it.
- **An ambiguous sentence opening.** Ruling 4 fails toward silence there.
- **Whether the publisher's rendering was copied correctly.** The scanner compares citation with
  entry; neither is compared with the source.
