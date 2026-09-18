# Reference scan resolves a no-surname entry by title-proper prefix and reads APA 8.21 group abbreviations through one shared recognizer

**Measured at:** 1f0aba9f2d58db0bc83a71b2bb2905ad0985e4e5

[#1169](https://github.com/mshamblin5150-code/clinical-skills/issues/1169) was filed from [ADR 0195](0195-citation-resolution-is-a-named-directional-relation-and-the-no-surname-branch-keys-on-the-title-proper.md) ruling 10 item 3. Grilled against `main` at `10e22383`, brought forward to `1f0aba9f` before publication with no change to the modules measured; the freshness gate read `FRESH` there. The clinician ruled every point below in that session. **Nothing is built here; this is the record the build reads.**

## What was measured before ruling

Driven through `tools/reference_scan.py` with synthetic drafts:

```text
entry  The epic of Gilgamesh (M. G. Kovaks, Trans.). (1998). Academy.
(The Epic of American Civilization, 1998)   -> 'epic'   resolves clean   -- a different work
entry  World Health Organization. (2020). Report. WHO.
(World Bank, 2020)                          -> 'world'  resolves clean   -- a different organization
(The epidemiology of sepsis, 1998)          -> counted unread; its entry raises uncited-entry
```

The collision reaches every entry with no personal surname, group authors included, not only a title in the author slot. The ticket's second half is disproved as its sweep comments already said: the lowercase-opening citation is counted in the unread remainder and fails loud.

The clinician directed that APA 7's manual be read rather than inferred. From the authenticated VitalSource copy (ISBN 9781433832185):

- **§8.14** — an unnamed author's title moves into the in-text citation in title case, italicized or quoted to match the reference, and *"If the title is long, shorten it for the in-text citation."* No shortening method is given; every example keeps the leading words.
- **§8.21** — a group abbreviation is given with the full name at first mention in the text: in a narrative citation inside the year parentheses, `The American Psychological Association (APA, 2017)`; in a parenthetical citation in square brackets, `(American Psychological Association [APA], 2017)`. The entry always spells the group out; the abbreviation is introduced once even for several entries; two groups sharing an abbreviation are spelled out every time.

§8.21's own narrative example fails today — `uncited-entry` 1 and `unlisted-citation` 1, both false — and the bracket form resolves only because the first word alone is compared.

A counts-only measurement over tracked Markdown and `output/` (Markdown and rendered `.docx`) found the prefix relation newly fails no APA-correct citation, no non-prefix shortened title, and no same-key-and-year pair of distinct entries. It found one entry, cited twice, whose first author has an unhyphenated two-word surname and so reads as having no surname; ruling 2 exists for it. **`scratch/` is unmeasured** — its walk did not finish and 1,414 files are the unread remainder. The rulings rest on the manual rather than the corpus.

## Ruling 1 — `reference_scan` adopts Citation resolution for entries with no personal surname

The first-word test is replaced, for that branch only, by `CONTEXT.md`'s **Citation resolution**: the citation's full normalized author phrase must be a character prefix of the entry's title proper, and the years must agree. The title proper is the author slot with any trailing run of parenthesized groups removed, by position and never by a vocabulary, as ADR 0195 ruling 4 states.

- The new key is added **beside** `Entry.key`, as **Grouping key** requires. `Entry.key` and the `a`/`b` rows do not move, which is the part ADR 0150 ruling 1's preserved prohibition protects.
- `Citation` carries the full author phrase; today it keeps only the first word.
- The key function stays this module's own. ADR 0195 ruling 3 and #942 refuse a shared key function; the relation is shared, not the code that produces keys.
- `uncited-entry` uses the same relation from the entry's side.
- The surname path is unchanged: first-word equality there stays, and is declared.

A trailing `[ABBR]` group in a citation phrase is dropped before comparison. Without that, the repair turns §8.21's bracket form into a new false finding.

## Ruling 2 — an entry has no personal surname only when its author slot carries no initials

Every personal author in an APA entry is written `Surname, I.` (§9.8). An entry goes to the prefix branch only when its author slot, trailing parenthesized groups removed, carries no `, X.` initials. So `Garcia Lopez, M., & Smith, J.` and `Van der Berg, A.` stay on today's surname path with their keys untouched, although the single-token surname detector misses them.

Widening that detector was refused here: it moves every such entry's keys and the `missing-first-author-initials` row, and it is a defect #1169 inherits rather than one it introduces. It is filed as [#1368](https://github.com/mshamblin5150-code/clinical-skills/issues/1368), which also records that `discussion_artifact` keys the same entry on its second author. Declaring it instead was refused because it would ship a false finding on a real draft.

## Ruling 3 — this ticket builds §8.21, widened from the bracket alone

The bracket must be read anyway, and the manual states §8.21 as one rule in three forms, so building one form and leaving two broken was refused. The later bare-acronym form was already failing before this ticket; it is built here on the clinician's direction to follow the manual rather than filed.

## Ruling 4 — a definition is recognized in prose, narrative and parenthetical forms, keyed on the reference list

`Name (ABBR)` in prose, `Name (ABBR, year)` narratively, and `(Name [ABBR], year)` parenthetically all define. §8.21's first bullet says *first mention in the text*, and a first mention need not be a citation. A span defines only when the full name, normalized, equals the title-proper key of an entry with no personal surname — the same evidence rule [ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) uses, and what keeps `(MRI)` from reading as a group.

## Ruling 5 — an abbreviation stands for its group only after its definition

A bare use before the definition raises the existing `unlisted-citation`, whose detail names the abbreviation. The earliest definition wins, so an abstract that defines its own abbreviations only helps.

## Ruling 6 — an abbreviation defined for two groups stands for neither

Every bare use raises `unlisted-citation`; spelled-out citations still resolve. A paper following §8.21 never triggers it. Silently resolving to the first or last definition was refused as the wrong answer this ticket exists to remove.

## Ruling 7 — one §8.21 recognizer, in `discussion_artifact`, consumed by both readers

`discussion_artifact` already reads the narrative and bracket definitions positionally, but has no prose definition and lets a later definition silently overwrite an earlier one. The recognizer is built once there, carrying rulings 4 to 6, and `reference_scan` — which already imports from that module — consumes it under its own normalization. #942 permits a shared recognizer; two copies of one APA rule is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220). This widens the ticket to the three discussion graders, whose two gaps it repairs.

## Ruling 8 — `NOT_REACHED` gains rows, derived rather than retyped

`reference_scan.NOT_REACHED` gains the three Citation-resolution residues ADR 0195 ruling 8 declares — a shortened title prefixing two entries, part of a group's name, a citation stopping mid-word — derived from `discussion_artifact.CITATION_RESOLUTION_NOT_REACHED`'s subject and reason rather than written a second time. It also gains: a spelled-out group citation after its abbreviation is defined resolves and is not graded for consistency; and the surname path resolves on the first significant word, so two authors sharing a surname are one key.

The part-of-a-group-name residue is weightier than ADR 0195 recorded: the manual never shortens a group name. It stays declared because nothing distinguishes a group author from a title in the author slot (ADR 0195 ruling 1).

## Ruling 9 — the sentence-case in-text title keeps today's behavior

It is an APA error under §8.14, and the run already says so: unread remainder, and `uncited-entry` on its entry. A title-case row and a clean resolution were both refused — the first is a separate rule, the second a silent pass. The ticket's headline and body are corrected.

## Ruling 10 — fixtures and controls

§8.21's examples and §31's Gilgamesh row are extracted from `apa7.md` where the sheet carries them; the collision, two-word surname, misordered and colliding abbreviation cases are synthetic beside them. ADR 0195 ruling 9's legal-entry control is mandatory here too, because ruling 1 changes which entries reach the prefix branch.

## What none of this reaches

Whether a cited work exists or says what the draft claims. Whether an abbreviation is well known enough to use, which §8.21 leaves to the writer. The `scratch/` population.
