# A claim names its qualifiers and an item description is tied to the item it describes

**Measured at:** 09e4e15e1dfbcbd5d4a67ca3ef5face9cb423752

[#1494](https://github.com/mshamblin5150-code/clinical-skills/issues/1494) was filed from the
after-action review of a `discussion-reply` run (NUR 5144 Module 2) on 2026-10-01. Three fresh
heading readers read the same reply against the same heading and gave opposite verdicts: two paired a
sentence that had dropped "community-acquired" from its claim heading's disease name, one of them on
a byte-identical draft, and a third recorded it as `drifted`. The same sitting's first reader
returned `CONTEXT-VERDICT: agrees` over a sentence misdescribing a classmate's document that was one
of the opened project-context items. A comment the same day recorded the qualifier defect a second
time in a `peer-critique` run, between a claim heading and its own record: the orchestrator's
rewrite dropped the source's "not thought to be due to S. aureus" condition, which the research
return had kept. Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The heading-read record cannot hold the sentence it grades.** A `PAIR` line is a free-text
location and the first eight hex characters of a heading digest. `heading_read.py` grades the
record's shape, its fingerprints and each prefix against current headings; it never sees the
sentence text, so no code can compare a heading's words with the draft sentence paired to it.

**The heading, its restatement and its passage are all in `claims.md`.** The comment's case
happened there, so a comparison between a heading and its own record is within reach of
`research_ledger.py` without any new input.

**The comment's dropped qualifier is a condition, not a population word.** A fixed vocabulary of
population, setting and age words would not have contained it. ADR 0315 ruling 6 already declined
reading natural-language phrases as a guess that misses the next phrasing.

**The record has two sentence classes and the misdescribed sentence fits neither.**
`SENTENCES: <n> factual, <n> clinician's own` is the whole vocabulary. A factual sentence must pair
with a claim heading or it is `unrecorded`; the clinician's own reasoning needs no pair and is
checked only by the context verdict. A sentence stating what a classmate's document says has no
claim heading, because its source is the document. In
[#1506](https://github.com/mshamblin5150-code/clinical-skills/issues/1506)'s run one reader reported
such a sentence as unsupported; in this ticket's run another passed it under `agrees`.

**Two open tickets edit the same reader instructions.** #1506 gives the `discussion-reply` reader the
board and posts files and adds a pre-draft walk; #1524 adds the project-context item pointers to the
same "receives only" sentence.

## Ruling 1 — each sourced claim record names its own qualifiers, quoted from its passage

A record with a source carries a field listing every limiting qualifier its `PASSAGE` carries, each
quoted word for word from the passage: population, setting, comparator, condition, eligibility,
device, adjustment and tense. A claim with no limiting qualifier writes `none`; an absent field is
never read as `none`. The researcher writes the field and the refuter checks it is complete as part
of the refutation ADR 0315 ruling 5 already requires. A record with no source has no passage and
carries no such field, on the existing rule that a sourceless record carries no source-claim field;
a `DROPPED` record certifies nothing and is exempt.

`research_ledger.py` checks that each named qualifier appears in the passage, the heading and the
restatement. A qualifier the heading or restatement lacks is a finding, which catches the comment's
case when the ledger is written rather than when a refuter happens to read it. Matching ignores case
and runs of whitespace and is otherwise word for word, so a capital opening a heading does not break
a match.

A fixed qualifier vocabulary in code was declined because it misses any condition not on the list,
the recorded one included, and fires on correct shorthand. A check on every content word of the
heading was declined because it fires on every correct paraphrase. Leaving the choice of qualifiers
to the heading reader alone was declined because that is the reading that already gave opposite
verdicts on identical input.

## Ruling 2 — each heading-read pair line carries the reader's qualifier count

A pair line states how many of the paired claim's qualifiers the reader found in the sentence, for
example `PAIR: <location> -> <prefix> | qualifiers 3 of 3`. `heading_read.py` checks that the total
equals the number the paired record lists and that a shortfall is written as a finding. The count
proves the reader addressed every qualifier, never that the reader judged it correctly; that limit
is declared. Naming each qualifier on the line was declined because copying names costs a careless
reader no more than copying a count. Leaving the tick in the brief alone was declined because it
leaves the draft side exactly as ungradeable as the ticket found it.

## Ruling 3 — the new rows bind ledgers dated on or after the build

The ledger's existing `DATE:` header is the cutoff. A ledger dated on or after the day this is built
must carry the qualifier field; an earlier ledger prints the qualifier rows as `not graded` with the
count of records left unread, never as a clean zero. A pair line owes a qualifier count only when
its paired record carries the field, and the three-class sentence line of ruling 5 follows the same
cutoff. Requiring the field everywhere at once was declined because a backfill is a fresh research
reading that changes headings and forces fresh refutations in runs that could not have followed the
rule. An optional field was declined because nothing would make a run write it.

## Ruling 4 — the shared item-description rule is written in `sourcing.md` and ruled here

The rule binding a sentence about an opened item to that item is written once in
`skills/_shared/reference/sourcing.md`, which all five coursework skills read first, under ADR 0315
ruling 1. #1506 keeps its `discussion-reply` items, the pre-draft walk and the reader's board and
posts inputs. Moving the rule to #1506 was declined because that ticket would grow from one skill to
five mid-grilling, and because this defect was observed with the item already in the reader's hands
while #1506's reader never had it. A separate third ticket was declined as a third record of one
reader sentence.

## Ruling 5 — an item description is its own sentence class with a pair line naming its item

An **Item description** is a draft sentence stating what an item opened for the run's project
context record says, such as a classmate's plan or a prior submission. The heading-read record counts
it as a third class, `SENTENCES: <n> factual, <n> clinician's own, <n> item`, and ties each one to
its item with a line such as `ITEM: <location> -> <opened item identifier>`. The reader compares the
sentence with that item claim by claim before writing the context verdict. `heading_read.py` checks
that the item lines equal the item count and that each names an item `project-context.md` records as
opened. Whether the comparison was right remains a declared reading.

Counting it among the clinician's own sentences, the ticket's proposed wording, was declined because
nothing would show which sentences were compared, so a bare `agrees` passes as it did on this run.
Counting it as factual was declined because it would make every description of a document the reader
already holds a researched and refuted claim.

## Ruling 6 — an omission is a finding only when the omitted part bears on the sentence's point

An item description that leaves out part of the item bearing on the point the sentence makes is
`narrows` at that location. One that states something otherwise, drops a qualifier the item carries,
or asserts an absence the item does not state is `contradicts`. Both block the go-ahead. This is the
same test #1506 proposes for the drafter, so the drafter and the reader judge one line. Treating
omission as never a finding was declined because #1506's selective plan summary would pass; treating
every omission as `narrows` was declined because no reply can restate a whole plan and the finding
would be learned around.

## Build checklist

- `skills/_shared/reference/sourcing.md`: the qualifier field and its `none` form in the record
  rules; the refuter's completeness check; the heading reader's qualifier count; the item-description
  class, its `ITEM` line, the claim-by-claim comparison and ruling 6's `narrows` and `contradicts`
  split; the template's `SENTENCES` and `PAIR` forms.
- The record shapes and return lists in the five coursework skills that keep a claim ledger, so
  each brief names the field.
- `tools/research_ledger.py`: the field's parse and the three-way presence rows, the `DATE:` cutoff,
  `not graded` with an unread count on earlier ledgers, and a `DECLARED_LIMITS` row for an added
  condition, which presence cannot see.
- `tools/heading_read.py`: the `qualifiers N of M` pair suffix checked against the paired record,
  the third sentence class and `ITEM` lines checked against `project-context.md`'s opened items,
  both on the same cutoff, and `DECLARED_LIMITS` rows for count-not-correctness and
  item-comparison-not-verified.
- Tests that drive a dropped heading qualifier, a dropped restatement qualifier, `none`, an absent
  field before and after the cutoff, a short pair count, a missing `ITEM` line and an `ITEM` naming
  an unopened item through the public commands, with a committed real claim record as the positive
  control.

## What this record does not reach

- **Whether a record's qualifier list is complete.** Code checks that each named qualifier appears;
  it cannot find one the researcher and refuter both missed.
- **A condition added to a heading.** The comment's second defect welded another organization's
  condition onto the source's sentence; presence of named qualifiers cannot see an addition, and the
  refuter remains the only check.
- **Whether a reader's count or item comparison is right.** Both are recorded and graded for
  completeness only.
