# A code is also traced from the note's site, cause or type word and the trigger widens ADR 0373's location rule

**Measured at:** a22d9c58db035a2e5a2e4e17cd584c4189927079

[#1598](https://github.com/mshamblin5150-code/clinical-skills/issues/1598) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift, 2026-10-07. Three note passes
handed back codes their note text could not route to, and each surfaced only when the blind
descriptor-agreement reader tried an index route from the note's words. The ticket asked for an
author-side check, run before hand-back, that applies `anchor_scan`'s route test to the author's own
anchor words. The clinician ruled every point below on 2026-10-16, against `main` at the commit
above, where the freshness gate read `FRESH`. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The requested check is built.**
[ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)
has every coding writer grade its own record with `anchor_scan.py --agreement-read` before
hand-off, through the same `_route_status` the blind read uses, and an exit 1 is never handed off.
It landed the day after the ticket was filed.

**Each of the ticket's three cases meets that check differently.**

- A site-specific code where the note named a different site passes it, because the test compares
  only the route's first main term with the note's words.
  [ADR 0373](0373-a-site-bearing-symptom-code-is-chosen-from-the-note-s-location-word-and-the-grader-keeps-its-route-start-test.md)
  ruled that case on #1590 the same morning.
- A refusal whose condition the note never names in index terms is refused by it: the route's first
  main term is not in the note's words, so `_route_status` returns invalid.
- An unspecified intestinal obstruction refusal where the note described adhesions passes it. Driven
  on 2026-10-16 through `_route_status` in `tools/anchor_scan.py`, on the words "Small bowel
  obstruction due to adhesions": `K56.609 Unspecified intestinal obstruction, unspecified as to
  partial versus complete obstruction` by the route
  `Obstruction, obstructed, obstructive > intestine -> code K56.609` grades valid, and
  `K56.50 Intestinal adhesions [bands], unspecified as to partial versus complete obstruction` by
  the route `Adhesions, adhesive (postinfective) > intestine > with obstruction -> code K56.50`
  grades valid too.

**The adhesions miss and the site miss have one cause.** In both, the writer started the index
trace from the complaint's general word, `Mass` or `Obstruction`, while the note named the word that
decides the code: a location in one, a cause in the other. ADR 0373 ruling 1 reaches only the first,
because its trigger is a symptom code whose descriptor names a body site.

## Ruling 1 — a second trace starts from any site, cause or type word the note names

The writer-side rule ADR 0373 ruling 1 places in `skills/icd10-cpt/SKILL.md`, after the paragraph
that begins "**`Z03.-` is not proposed here**", is written once with a wider trigger. Before
handing back any code, entry or refusal, the writer finds the words in the note that say where the
condition is (its site), what caused it (the word after "due to", "from", "secondary to" or "with"),
or what kind it is (a named type, such as adhesions, or partial against complete). The writer traces
`--index` from each such word as well as from the complaint's general word. Where a trace reaches a
different code, the writer looks up both codes and reads the Excludes1 of each, because the tabular
can state a split on one side only, and keeps the code the note's words reach.

The paragraph carries two worked examples. ADR 0373's site example, `R19.00` against `R22.2`, keeps
its trap path, its correct path, and its observation that `R19.00`'s own notes say nothing of the
split. The cause example is `K56.609` against `K56.50`, with the two routes above. It says, as ADR
0373 ruling 1 did, that a code the note's words do not reach fails the blind reader's
descriptor-agreement judgment and the writer's own reading, not the grader.

Tracing from every word the index carries as a main term was declined because common words such as
pain, acute and history are main terms, so one code could owe dozens of lookups and the instruction
would be skimmed. Tracing only from words whose route ends in the chosen code's three-character
category was declined because `R19.00` and `R22.2` sit in different categories, so the site case
would need its own rule beside it for one cause.

## Ruling 2 — the grader stays unchanged and the adhesions case is a reading

`_route_status` and the Writer self-grade are unchanged, and ADR 0373 ruling 2 stands. An advisory
scan listing other index routes that start from a note word and end at a different code was declined:
nothing has measured how often it would fire on routes from common words, and a warning that fires on
most codes is one a writer learns to skip. The second trace is the writer-side guard.

## Ruling 3 — one build carries both rulings

#1590's build of ADR 0373 ruling 1 moves into #1598, which carries the single paragraph ruling 1
here describes. #1590 closes with a pointer to #1598. Its second item, a differential carried as a
coded entry while its establishment waited on a pending exam and tests, ADR 0373 records as a miss of
the existing step 3 rule, so nothing of #1590 is left unruled.

Building ADR 0373's narrower paragraph first and rewriting it under #1598 was declined: two builds on
one paragraph, with the narrower trigger standing as live guidance in between. Letting both tickets
build independently was declined because two branches would edit the same paragraph.

## What this does not reach

Ruling 1 is a reading instruction. Nothing mechanical shows that a writer found the note's site,
cause or type words or traced from them, and the Writer self-grade still passes a code whose route
starts from a general word the note contains. Deciding which words name a site, a cause or a type is
the writer's judgment; a word outside those three roles that would have led to a more specific code
is not traced. A reader who misjudges the same word in the same way as the writer is not caught,
which is the Shared-reader blindness the Writer self-grade already carries.

## Supersedes

- [ADR 0373](0373-a-site-bearing-symptom-code-is-chosen-from-the-note-s-location-word-and-the-grader-keeps-its-route-start-test.md) ruling 1,
  its words "For any symptom code whose descriptor names a body site, the writer traces `--index`
  from the location words the note uses". Ruling 1 here widens the trigger to any site, cause or type
  word the note names, for any code. The worked example, the instruction to read both codes'
  Excludes1, and the paragraph's placement survive.

## Build checklist

- `skills/icd10-cpt/SKILL.md`: one paragraph after "**`Z03.-` is not proposed here**" carrying
  ruling 1, with both worked examples, built for #1598. This is the paragraph #1590 would have
  built; no separate ADR 0373 paragraph is written.
- `tools/test_anchor_scan.py`, beside its existing read of `skills/icd10-cpt/SKILL.md`: a check that
  the paragraph names both example pairs and the three roles, and that `_route_status` still grades
  both adhesions routes valid on the words above, so the reading limit stays a measured one.
