# A ruling is identified by its ordinal and an empty parse is declared rather than guessed at

Ruled by the clinician on 2026-09-05, in the grilling of
[#759](https://github.com/mshamblin5150-code/clinical-skills/issues/759). Freshness gate `FRESH` at
both checkpoints; `main` moved once mid-session and every figure below was re-derived at the new
base. Nothing is built here; this is the record the build reads.

**The subject.** `ruling_ordinals` in `tools/test_skill_agreement.py` reads an ADR's numbered
rulings, and four ratified records write theirs in spellings it does not read. Those records parse
to the empty set, which is indistinguishable from a record that rules nothing, so the failure is
invisible from inside the record and lands on the next author who writes a coordinate to it.

## Measured before ruling, at `557fa94`

Every figure here was re-derived in this session by importing `ruling_ordinals` and running it over
`docs/adr/*.md`, first at `a48e308` and again at `557fa94` after `main` advanced. Nothing moved
between the two bases.

**The empty set carries three different meanings.** 131 records; 22 declare nothing:

```
numbered rulings the resolver cannot read   4   0094, 0096 (**Ruling N.)  0126, 0127 (## Decision N)
rulings written without ordinals            4   0016, 0017, 0022 (## What is ruled)  0037
no rulings at all                          14   0001-0006, 0008, 0010, 0011, 0013-0015, 0020, 0021
```

**The ticket's own constraint was a two-way partition of a three-way tree.** It asks that no check
fire on *"the eighteen records that legitimately declare nothing"*. Four of those eighteen carry a
ruling section and rule substantively: ADR 0017's `## What is ruled` holds eight bold rulings and
resolves to the empty set. That record rules more than most numbered ones.

**The defect is latent in every instance.** Of 592 ruling coordinates in the graded population,
**zero** cite any of the four unread records. Nothing is red today.

**Widening the two patterns moves exactly four records and nothing else.**

```
0094  [] -> [1..6]      0126  [] -> [1..8]
0096  [] -> [1..5]      0127  [] -> [1..9]
127 other records byte-identical; 0 shape findings; 0 new unresolved citations
```

**The bold anchor is load-bearing, and the collision is located rather than feared.** Tolerating a
bare `Ruling` word before the numeral matches three hard-wrapped citation continuations, where a
sentence ends on one line with an ADR link and the next line opens with the ordinal word:
`0040:293`, `0054:258` and `0069:124`. One of the three sits inside a ruling section and corrupts
that record's sequence to `[1, 2, 5, 3, 4, 5, ...]`, producing two false shape findings. The other
two fall outside a ruling section and are read by nothing **today**, which is luck and not safety,
because a record's section structure is editable. Requiring the bold removes all three.

**The declaration vocabulary is grounded and the citation vocabulary is not the same list.**
Heading declarations across `docs/adr/`: `## Ruling N` in 12 records, `## Decision N` in 2, and
`## Point N` and `## Rule N` in none, at any heading level. Across the 592 citations the ordinal
words used are `ruling` 532, `point` 46, `decision` 8 and `rule` 6 — so `point` is the second
most-used citation word and has no declaration form anywhere.

**Both cheaper checks are falsified by measurement.** A check keyed on a record having a ruling
section that declares nothing **misses ADR 0126 and 0127 entirely**, because neither carries a
`RULING_SECTION` H2 at all — their ruling headings are the `Decision` form, which that pattern does
not match. A tripwire keyed on a loose numbered-ruling shape the parser did not return fires on six
records, three of them false alarms on numbered correction and consequence material the parser
deliberately excludes, and still misses ADR 0127, whose headings put no punctuation after the digit.

**The recurrence needs no arguing.** The class grew from one member to two on the day the ticket was
filed, and to four two days later. ADR 0127 was written by a session that had read neither the
ticket nor the convention.

## Ruled 2026-09-05

### 1. The repair is the grammar, and the four ratified records are not edited

Two patterns widen. No record's content moves. Editing 28 headings across four ratified records
would fix today and nothing prospectively, and this repository's precedent for correcting a
ratified record in place is ADR 0016's — a **fact that went wrong**, with the deciding paragraph
untouchable. A spelling the resolver cannot read is not a fact the record got wrong.

### 2. An unnumbered record is a legitimate shape and is out of the defect class

A record that rules without ordinals is not the same thing as one whose ordinals are unread, and the
ground is which failure is silent. An unnumbered ruling refuses a coordinate **visibly**: the citer
opens the record, sees no numbers, and quotes the ruling's own words, which is
[#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246)'s de-citing precedent
working as intended. An unread ruling refuses one **silently**: the citer sees a numeral, writes the
coordinate in good faith, and the suite goes red on their branch for a defect in somebody else's
record. Same empty set, opposite failure modes, and only one of them is what this record is about.

### 3. An empty parse must be declared, and the declaration is bounded

A record whose parse is empty carries a marker on its own line and is a finding without one:

```
<!-- no-numbered-rulings -->
```

A tree-wide ceiling bounds the total at the count standing when this lands, on
`RULING_EXEMPT_CEILING`'s precedent in the same module. Forgetting the marker refuses rather than
clears. Escaping by adding one pushes the total over the ceiling, so the escape costs a defended
integer in a diff rather than a quiet comment.

Own-line on `phi_scan`'s pragma reasoning: a marker mentioned mid-sentence is not a marker, which
this repository has already been bitten by twice.

### 4. The declaration grammar takes two words and the citation grammar keeps four

The heading form admits `ruling` and `decision` and refuses `point` and `rule`, on the measurement
above: 14 records write the two, and none writes the other two. Admitting a form for symmetry with a
matcher that has a different job is `spelling_scan`'s declined suffix families arriving on a
grammar — the table grows on evidence that this repository writes a form, never on the shape of a
neighboring list.

The two lists are **not one vocabulary and do not become one**. `RULING_CITATION` reads prose, where
four words are safe because an adjacent record number and digit pin the coordinate regardless. The
declaration grammar is a writer's grammar, where every admitted word is a spelling somebody may
adopt. The asymmetry is written down here so the next reader does not repair it as an oversight.

### 5. The resolver is permissive and the guidance is not

Reading a form is not blessing a dialect. `## Ruling N` is the recommended spelling; the others are
read so that no record is ever silently invisible, and are not offered to a new author as choices.
Without this clause the next session reads the accepted spellings as endorsed ones, which is how a
grammar acquires dialects nobody chose.

### 6. One marker, worded so it is true of everything it is stamped on

The marker's job is to make an empty parse **deliberate**, never to classify why it is empty, and
the two classes under ruling 2 answer that question identically. A second marker would make every
future author answer a question nothing consumes, which is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s catalog of known formats
and [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s prose limit arriving
on a comment. Nothing in the tree asks how many records carry uncitable rulings, so under
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) that is a figure not worth
a mechanism to keep true.

The wording follows from ruling 2: a marker asserting a record declares no rulings would be false of
ADR 0017, which declares eight of them unnumbered. `no-numbered-rulings` is true of that record and
of one that rules nothing.

### 7. ADR 0097 keeps its quotations and gains a pointer, and no general rule is made

ADR 0097 cites the unread record's rulings by their own words and explains why in a paragraph whose
present tense this record falsifies. The quotations stay: a quotation says everything the coordinate
said and here says more, and rewriting the paragraph would destroy the account of the defect written
by the record that surfaced it. It gains one dated line at the bottom naming
[#759](https://github.com/mshamblin5150-code/clinical-skills/issues/759) and this record, which is
ADR 0016's own mechanism, **because it carries no forward pointer at all** — its only ticket
reference in that passage is the de-citing precedent, and it never names what it filed.

ADR 0128 is untouched. Its entry under *what this record does not settle* points at a ticket closed
as a duplicate of #759, so a reader following it arrives here.

**No rule is made that a record falsified by a later one gets a correction line.** That is a
standing obligation on every future grilling with no measurement behind it, and
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s discipline is to ground a
rule where the corpus grounds one. Two records, named, for a stated reason.

### 8. `adr_next.py` is unchanged, and `CONTEXT.md` gains one term

The scaffold keeps writing the heading and nothing else. A ruling-section stub helps exactly the
authors the widened grammar already helps and cannot reach the one the check exists to catch, since
an author who invents a further spelling is by definition one who did not follow the scaffold. It
would also stamp a date at claim time, before the grilling that sets it, and stamping one of the
working forms is ruling 5's line crossed by default.

`CONTEXT.md` gains **Ruling** in the ADR sense, with the declared candidate row its arrival
requires against `Ruling cohort`'s clinician sense. The entry states what this session established:
a ruling is identified by its record and its ordinal, and the words around the ordinal are spelling.
The reason it is worth adding is that `candidate_headings` derives its population from glossary
**headings**, so a word carrying two senses across 592 lines of prose is invisible to the collision
inventory by construction — the instrument that hunts collisions reports clean about the one in
front of it. Ruling 4's second accepted spelling makes that gap worse rather than merely inheriting
it.

The two terms this grilling coined for ruling 2's distinction stay in this record and do not enter
the glossary. Nothing in the tree writes them, and a glossary entry for a phrase nobody uses is
ruling 4's refusal arriving on the glossary.

## What this record does not settle

**Whether a truncated read is worth a check.** Nothing ruled here catches a record writing rulings
1 to 8 where the parser returns a clean, gapless `[1, 2, 3]`. It parses non-empty, so no marker is
due, and the shape check sees no gap. That shape has one recorded instance in this parser — a fenced
`## ` line hid rulings 3 to 9 until `CODE_FENCE` was added — and no live instance today. It is
declared rather than built for, on #97's ground.

**Whether the marker's ceiling ever rises.** A record deliberately ruling without ordinals is a
legitimate shape under ruling 2 and is not forbidden, so the ceiling is a ratchet and not a
prohibition. Raising it is a one-line diff somebody defends.

**Whether the eleven other spellings a record could invent are worth enumerating.** They are not
enumerated and cannot be. A rule that cannot recognize a member cannot count it as unread, which is
the extractor-coverage ceiling this repository already states; ruling 3's marker is what makes a
sixth spelling fail rather than a wider matcher, and that is the whole reason the check is a
declaration and not a guess.
