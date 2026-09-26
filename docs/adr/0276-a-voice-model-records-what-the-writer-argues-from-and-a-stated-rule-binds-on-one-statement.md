# A voice model records what the writer argues from, and a stated rule binds on one statement

**Measured at:** faed48af31199da580a3592de504e8290eddce2b

[#1427](https://github.com/mshamblin5150-code/clinical-skills/issues/1427) was filed from the
review sitting of [#1424](https://github.com/mshamblin5150-code/clinical-skills/issues/1424), where
the clinician corrected the harvest's scope twice, first for philosophy and then for imagery. The
sitting added a hand-written v3 block to the canonical voice model; nothing in
`skills/_shared/reference/voice.md` directs a rebuild to produce it again. Grilled against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## What the ticket had half right

The ticket says §4 never directs a build to harvest imagery. **That is false of the tree.**
[ADR 0038](0038-a-figure-marker-names-what-it-spends-and-the-domain-stays-open.md) ruling 9 added
item 8, the invoked source and what it spends, because §4 then had no imagery item, and its ruling 7
says the same form covers a craft metaphor and a named philosopher alike. What §4 lacks is narrower,
and it is three things:

- **The level.** Item 8 records one use at a time: one sentence, one domain, one property spent.
  `voice_model_scan.py` requires exactly one such observation to exist. Nothing asks for the
  writer's domains across the corpus or for how an image works for them.
- **Beliefs.** A principle the writer states and argues from is not spent by one sentence; it is the
  ground the claim stands on. Item 8's form, which exists to refuse a decorative figure because it
  names no property, has nothing to ask of it.
- **Instructions.** Rules the writer has given about their own writing bind on one statement and can
  be retired by a later one. §4's two-sample rule would quarantine them as seen once.

[PR #1429](https://github.com/mshamblin5150-code/clinical-skills/pull/1429) made the cost
mandatory rather than advisory: `voice_read.DECLARED_LIMITS` row `model-gaps-remain` records that
content absent from the canonical model cannot be found by the completion voice read.

## Ruling 1 — stated principles take their own §4 item

§4 gains an item, appended as item 9, for the writer's **stated principles and the structure they
sit in**, quoted in the writer's own words. It is recorded once for the corpus rather than per
sample, and each principle needs two conversations or samples, on the two-sample rule. Item 8 is
unchanged in kind and keeps single uses. Widening item 8 to hold principles was refused: its
property field has nothing to name for a belief stated as a belief, so the form would either stop
fitting or loosen until the refusal of decorative figures weakened. Leaving §4 silent and relying on
a harvest step was refused on ADR 0038 ruling 9's own ground: a rule a rebuild is never told about
is a record a rebuild drops.

`CONTEXT.md` defines **Stated principle** beside **Invoked source**.

## Ruling 2 — item 8 widens in place and keeps its name

Item 8 keeps its per-use record, domain and property, and gains two corpus-level records: **the
domains the writer draws images from**, each needing two conversations and each quoted, and **how an
image works for the writer**, each point quoted. ADR 0038 ruling 3 stands: the domain is open, and
no enumeration becomes the recognizer. The item's name is unchanged because `voice_model_scan.py`
reads it verbatim from the tracked spec and its tests pin that name. A separate item for
corpus-level imagery was refused as two homes for one subject that a build could satisfy one at a
time.

## Ruling 3 — size and consequence are a floor

Item 8 records the **scale an image is written at and the consequence it spends**, quoted. A run
reuses an image of the writer's whole or not at all: it never shrinks one, and never replaces its
consequence with a flat generic payoff. It never enlarges one, adds one, or reaches for a larger one
to meet a rate. This is ADR 0038 ruling 2 kept, not moved: that ruling refuses magnitude as the
axis a run writes toward, and this records the writer's magnitude only so a run cannot strip it.
It is §8's rule that a finding is a floor and never a target, applied to an image. #1427's own
boundary, no amplification target, holds.

The clinician's question at the sitting was whether a run could reproduce his recorded images. The
answer the record gives is yes, whole, where the argument fits; the floor is what makes the reuse
carry the consequence rather than only the noun.

## Ruling 4 — stated writing rules take their own §4 item

§4 gains an item, appended as item 10, for **rules the writer has stated about their own writing**:
rules for using philosophy and imagery, word rules, and the profanity list. Each is quoted and
dated. **One clear statement binds**, and that exception is written beside the two-sample rule
rather than left for a build to infer. A later statement that replaces an earlier one is recorded as
a retirement, not a deletion. A rule that is house style by kind goes to the style sheet, on
[ADR 0275](0275-a-voice-read-compares-a-planted-copy-of-the-draft-with-the-voice-model.md) ruling 8,
and not into the model. Splitting stated rules across items 8 and 9 was refused because word rules
and the profanity list would still have no home and the binding and retirement rules would be
written twice.

`CONTEXT.md` defines **Stated writing rule**.

Appending items 9 and 10 rather than inserting them keeps every existing citation of an item number
pointing where it did.

## Ruling 5 — the scanner fails a rebuild that drops a record

`voice_model_scan.py` fails a model missing any of the three new records, or carrying one with no
quoted entry: stated principles, corpus-level imagery (its domains and how an image works,
including the size-and-consequence clauses), and stated writing rules. This is ADR 0038 ruling 11's
arrangement extended: a written rule a rebuild can silently skip is the failure #1427 records.
**Presence and quotation only.** Whether a quote is the writer's, whether a list is complete and
whether a principle is stated rightly remain the clinician's confirmation at
`setup-clinical-skills` step 10, and the scanner's declared limits say so. Enforcing only the
profanity list, because a reader already consumes it, was refused as leaving the other two
droppable in silence.

## Ruling 6 — the three records get fixed whole-writer sections

§8's template gains fixed sections after the three register sections and before `Seen once`:

- `## Stated principles`, holding the structure and the principles in the writer's words
- `## Imagery`, holding the domains and how an image works
- `## Stated writing rules`, which also takes the philosophy-use rules the v3 block holds under its
  philosophy section
- `## Profanity — the list graded copy never carries`, **character for character**, because
  `voice_read.read_profanity_terms` finds the list by that exact line

These records describe the writer rather than one register, so per-register placement was refused:
it copies one belief three times and counts the two-sample rule inside a thin register. Keeping
dated version blocks was refused because each rebuild would append another and the fixed layout
would stop being fixed. **The v3 block's content moves into these sections on the next build with
nothing reworded.**

## Ruling 7 — two searches per record, and the open one is a committed tool

For each of the three records a build over a chat corpus runs **a seeded search and an open
search**. The seeded search confirms counts for items already known. The open search counts phrases
recurring across distinct conversations with no seed list, so the seed list does not decide what is
found; it is what found the philosophy and imagery the first #1424 harvest missed. It becomes a mode
of `tools/voice_corpus.py`, which today has only `--match`, and it reports the conversations read
and the unread remainder on every run, on the extractor-coverage rule, with a planted control before
its coverage is believed. Counts only by default; the phrases are private working material.
`skills/_shared/reference/voice-corpus.md` owns the step and §4 points to it. Describing the open
search in prose alone was refused on [#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388)'s
record of a throwaway script reading part of the export as all of it.

A finding from either search is a candidate until it is quoted, meets its item's attestation rule,
and is confirmed by the clinician.

## Ruling 8 — a searched-and-ruled-out candidate has one owner

§8's template gains a fixed `## Searched and ruled out` section. Each entry names the candidate, the
search that surfaced it, its conversation count and the clinician's ruling with its date. A build
checks it before proposing anything, so a ruled "no" is neither re-asked nor re-added. The model is
the single owner and the profile keeps a pointer. The #1424 faith ruling, today written in both the
model and the profile, is the first entry. Keeping both copies was refused on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143): two editable copies of one
ruling go stale in one of them.

## Ruling 9 — two run-side residues are filed, not folded

Two rulings from the sitting change the drafting skills rather than the model, and each is filed as
its own ticket:

- **A proposed image.** When none of the writer's recorded images fits, a run may propose a new one
  from a domain the model records the writer using. It is marked in the draft and shown at the
  go-ahead with its domain and the property it spends, asked separately from the substance, and
  goes out only on the clinician's yes. The run record marks it proposed and approved, so a later
  harvest never reads it back as attested writing, which is §6's co-written-sample trap. This
  reverses the discussion skills' rule that a run adds none.
- **A supplied image survives.** The completion voice read reports, for each image or principle the
  clinician supplied in a run's input, whether the draft kept it whole, shrank it, or dropped it; a
  shrunk or dropped one is a finding. It never judges whether a draft uses enough of either, which
  would be the target this record refuses.

#1427 is correct without either: both need the model's records to exist, and neither changes how the
model is built.

## What this record does not settle

**Whether an approved proposed image may later be harvested as the writer's.** Ruling 9 marks it so
a harvest can tell; whether the clinician's approval makes it attested writing for a later model is
not ruled here.
