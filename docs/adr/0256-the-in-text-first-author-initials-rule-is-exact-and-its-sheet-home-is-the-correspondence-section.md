# The in-text first-author initials rule is exact and its sheet home is the correspondence section

**Measured at:** d2dc54c1be927106933aa3a95f348bbf2b1975e3

[#1167](https://github.com/mshamblin5150-code/clinical-skills/issues/1167) was filed from
[#959](https://github.com/mshamblin5150-code/clinical-skills/issues/959)'s grilling as ADR 0195
ruling 10 item 1. Neither citation reader resolves an in-text citation carrying the first author's
initials, and the ticket held that whether APA obliges the form was an open reading of
`skills/_shared/reference/apa7.md` §38. Grilled 2026-09-17; the clinician ruled every point below
the same day. Freshness gate `FRESH` at `d2dc54c1`. Nothing is built here; this is the record the
build reads.

## Measured before ruling

### Both readers still miss the form

Driven at `d2dc54c1` through the modules rather than through a description:

```
discussion_artifact.citation_author_keys('J. M. Taylor')             -> ('jmtaylor',)
discussion_artifact.citation_author_keys('J. M. Taylor & Neimeyer')  -> ('jmtaylorandneimeyer',)
discussion_artifact.reference_keys('Taylor, T. (2014). ...')         -> (('taylor', '2014'),)
reference_scan.citation_key('J. M. Taylor')                          -> 'j'
control: citation_author_keys('Taylor') -> ('taylor',); citation_key('Taylor') -> 'taylor'
```

The entry side keeps no initials at all, so an exact comparison needs the entry reader to retain the
first author's initials as well as the citation reader to separate them.

### The question the ticket asked was the wrong one

`apa7-coverage.md` already records §8.20 as read to root on 2026-09-08, and its evidence cell names
initials outright. The ticket read §38's generic *disambiguate authors or dates* as the whole of the
rule; the registry shows the rule was read and only the sheet's summary was lossy. So what was open
was where the sheet states it, not whether APA obliges it.

### The manual, read in the clinician's signed-in Bookshelf

Read 2026-09-17 by one reader, so every item is a claim until the build's registry re-read (ruling 6)
records it. §8.20: where the first authors of several references share a surname and have different
initials, the first authors' initials go in all in-text citations, even across different years,
because initials help a reader "locate the correct entry." The example gives each entry's
first-author initials in full. Same surname and same initials take the standard author–date form.
Coauthors of one reference who share a surname take no initials. A name-change clarification, which
is seldom relevant, uses the first author's first name instead.

## Ruling 1 — APA obliges the form

A run writes the first author's initials in every in-text citation of a work whose first author
shares a surname, but not initials, with another listed first author. This supersedes the ticket's
framing that the obligation was an open reading of §38.

## Ruling 2 — an initialed citation resolves only on exact initials

The citation's initials must equal the entry's first-author initials, compared after normalizing
punctuation and spacing. Against `Taylor, J. M., & Neimeyer, R. A. (2015)` and `Taylor, T. (2015)`,
`J. M. Taylor & Neimeyer, 2015` and `T. Taylor, 2015` resolve; `J. Taylor, 2015` and
`R. Taylor, 2015` are unlisted citations. A prefix match was refused because §8.20 licenses no dropped
initial, and a surname-only match because it resolves a citation naming no listed author.

## Ruling 3 — a missing-initials finding is built with this ticket

Where the reference list holds two first authors with one surname and different initials, a citation
of either that omits the initials is a finding in both readers. It is built with #1167 rather than
filed, because it is the other half of the same §8.20 sentence. It does not fire where the first
authors share initials too, since the manual prescribes the standard form there.

## Ruling 4 — unneeded initials resolve clean

Initials on a citation whose first author collides with no other listed first author, or on
coauthors of one entry, resolve under ruling 2 and raise nothing. §8.20 says such initials are not
needed; it does not forbid them.

## Ruling 5 — the first-name form is filed separately

`Sarah Williams (2019)` keys `sarahwilliams` and `sarah` against an entry keyed `williams`, so both
readers report it unlisted. It is a different form, the manual calls it seldom relevant, and #1167 is
correct without it. It is filed with that measurement and declared in both readers' limits until it
is built.

## Ruling 6 — the sheet states the rule in §5, and §38 is not edited

`apa7.md` §5, which owns citation-to-entry correspondence, gains the rule: different first authors
sharing a surname carry initials in every in-text citation, while shared initials and same-entry
coauthors do not. The §8.20 registry row binds §5 beside §38. Editing §38 was the first choice and was
withdrawn once its cost was counted: 45 registry rows bind §38, against three for §5 (8.4, 9.51 and
9.52), and every staled item needs a re-read in the clinician's signed-in session. ADR 0214 ruling 6
set that precedent. The ticket is done when those items and §8.20 are re-read and
`python tools/apa7_coverage.py` reports `gone-stale 0`.

## Ruling 7 — the two readers are repaired separately

ADR 0150, ADR 0151 and ADR 0195 ruling 3 ratify the key-function divergence, and #942 refuses a shared
key function. Each module gains its own initials handling, and the missing-initials finding lands in
each reader under that module's own row vocabulary.

## Rejected options

**Editing §38.** Stales 45 items for a clause §5 can carry at a cost of three.

**Declaring the gap instead of repairing either reader.** APA obliges the form, so a run that follows
the sheet would be refused.

## What none of this reaches

**Whether two same-surname entries are different people.** The readers compare strings; two people
with identical surname and initials are indistinguishable to them, and the manual's standard form for
that case is what both readers already accept.

**The name-change first-name form.** Ruling 5's ticket owns it.
