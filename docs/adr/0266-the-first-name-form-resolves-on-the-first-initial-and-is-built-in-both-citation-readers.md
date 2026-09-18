# The first-name form resolves on the first initial and is built in both citation readers

**Measured at:** 0df4b6a900e347fd6e020fa6730febd0181f07a8

[#1350](https://github.com/mshamblin5150-code/clinical-skills/issues/1350) was filed from
[ADR 0256](0256-the-in-text-first-author-initials-rule-is-exact-and-its-sheet-home-is-the-correspondence-section.md)
ruling 5. Neither citation reader resolves the APA §8.20 first-name form, and the ticket left open
whether to build it at all and what it joins against. Grilled against `main` at
`0df4b6a9`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## What was measured before ruling

#1167 has been built since the ticket was filed. Driven at `0df4b6a9` through the modules:

```text
discussion_artifact.citation_author_keys('Sarah Williams') -> ('sarahwilliams',)
reference_scan.citation_key('Sarah Williams')              -> 'sarah'
discussion_artifact.reference_keys('Williams, S. (2019). ...')
                                  -> (('williams', '2019'), ('swilliams', '2019'))
control: 'S. Williams' -> ('swilliams',) and 'swilliams'; 'Williams' -> ('williams',) and 'williams'
```

Both readers already declare the form in their limits, as ruling 5 required.

The ticket and the repository described the form differently. The ticket said it clarifies two
different people. ADR 0256, `apa7.md` §5, the §8.20 registry evidence cell and both readers'
limit strings said it serves an author whose name changed. §8.20 was read in the clinician's
signed-in Bookshelf copy (ISBN 9781433832185, reader page 267). The form sits inside the manual's
name-change paragraph, but its stated use is clarifying that two names refer to **different**
people, and its example pairs two first authors sharing both surname and first initial:
*"Sarah Williams (2019) stated X, whereas Shonda Williams (2020) stated Y."* That is exactly the
case where §8.20's initials rule falls back to the standard author–date form, so the first name is
the only in-text device left to separate them. Both earlier descriptions were half right, and the
repository's four copies state the purpose wrongly.

An APA reference entry carries initials, never given names, so the join can only reach the entry
through its initials. That answers the ticket's first open question.

## Ruling 1 — the form is built, not declared permanent

Each reader gains its own first-name handling, separately, under ADR 0150, ADR 0151, ADR 0195
ruling 3 and ADR 0256 ruling 7; no key function is shared. Declaring the form a permanent limit was
refused: a draft following §8.20 correctly would receive an unlisted-citation finding, and a checker
that cannot match a published APA rule is defective rather than bounded.

## Ruling 2 — a given name resolves on the entry's first initial

A single given name immediately before a surname resolves when its first letter equals the first
initial of a listed first author with that surname, compared after the normalization each reader
already applies. `Sarah Williams` resolves against `Williams, S.` and against `Williams, S. M.`; the
year selects among entries as it already does. No capitalized word is dropped unless it matches an
initial that is actually listed, so `Range Williams` stays unlisted against `Williams, S.`.

Gating resolution on a same-surname, same-initial collision was refused, on ADR 0256 ruling 4's
ground: §8.20 says such clarification is needed only sometimes and forbids it nowhere, so an
unneeded first name resolves clean. Requiring the given name to account for every initial was
refused because one given name can never cover `S. M.`.

## Ruling 3 — a first name satisfies the missing-initials rule

Where listed first authors share a surname and differ in initials, `Sarah Williams (2019)` resolves
clean against `Williams, S. (2019)` and raises no `missing-first-author-initials` finding. The first
name identifies the entry at least as well as the initial it begins with, which is what that finding
exists to ensure. No new row is added, so ADR 0256 ruling 3's finding keeps its one meaning: nothing
on the citation separates the colliding authors.

## Ruling 4 — accepted shapes, and declared ones

Both the narrative `Sarah Williams (2019)` and the parenthetical `(Sarah Williams, 2019)` resolve,
and so do the `&` coauthor and `et al.` tails each reader already reads after a bare surname.

A given name combined with initials (`Sarah M. Williams`) and a hyphenated given name
(`Mary-Kate Williams`) are declared in each reader's limits rather than built: neither appears in
the manual, and each would need its own matching rule. These rows replace the current #1350 limit
rows, which describe the form's purpose wrongly and stop being true once it is built.

## Ruling 5 — the sheet and the registry move with the build

`apa7.md` §5's closing sentence is rewritten to state the form's purpose (distinguishing different
people who share a surname and initials), its join (the given name's first letter against the
entry's first initial), and that it resolves clean where initials differ. The §8.20 registry
evidence cell is corrected in the same re-read. Editing §5 stales the registry rows bound to it;
under ADR 0214 ruling 6 and ADR 0256 ruling 6 each is re-read in the clinician's signed-in session,
and the ticket is done when `python tools/apa7_coverage.py` reports `gone-stale 0`. The ticket is
labeled `ready-for-human` on #1167's precedent: an agent can make every edit, but the re-read needs
the signed-in session.

## Ruling 6 — controls

The manual's own Sarah and Shonda Williams pair, against two `Williams, S.` entries, is the positive
control in each reader. `Range Williams (2019)` against `Williams, S. (2019)` is the negative
control and must stay unlisted. The declared cost is that `Range Williams` resolves against a listed
`Williams, R.`; a test pins that direction so the cost is visible rather than discovered.

## Rejected options

**Declaring the form permanent.** Refused under ruling 1.

**Resolving only where surname and first initial collide.** Refused under ruling 2.

**A new finding for a first name where initials differ.** Refused under ruling 3; it would fire on a
citation any reader resolves without effort.

**A separate ticket for the §5 edit.** Leaving the sheet describing a limit the code no longer has
is the two-copies drift #220 records.

## What none of this reaches

**Whether the given name is the author's actual name.** The readers compare one letter against a
listed initial; a wrong given name sharing that letter resolves.

**The name-change clarification for one person.** §8.20 routes that to the person's own preference,
which is not a mechanical question.
