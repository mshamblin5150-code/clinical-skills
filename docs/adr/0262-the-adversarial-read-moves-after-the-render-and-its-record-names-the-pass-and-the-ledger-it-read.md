# The adversarial read moves after the render and its record names the pass and the ledger it read

**Measured at:** 10e22383327f0c5e64dba660824e53e15080150e

[#1229](https://github.com/mshamblin5150-code/clinical-skills/issues/1229) was filed from #1020's
grilling. `skills/course-assignment/SKILL.md` section 3 gives the adversarial investor reader "the
rendered slide images", but the only command that renders them, `tools/deck_render.py`, runs in
section 5. The skill did not say which images the reader receives, and nothing checked. ADR 0210
ruling 9 left `adversarial.md` ungraded and unbound to the deck's bytes; ADR 0218 ruling 2 gave this
reader a record-to-slide agreement job and left binding it to the final deck here. The clinician
ruled every point below in one grilling session. Freshness gate `FRESH` at
`10e22383`. Nothing is built here; this is the record the build reads.

## Measured before ruling

### Section 3 hands over images two sections before any exist

At this record's commit, section 3, *Produce the deck*, briefs the adversarial reader on "the
rendered slide images, the speaker-note text, and `claims.md`". Section 4 runs `deck_scan.py`, and
section 5 is the first to run `deck_render.py`, which writes `render/pass-N/` with `deck.sha256`. A
run therefore renders ad hoc outside a numbered pass, hands over an earlier deck's images, or skips
the images.

### The final deck already has one bound reader and one unbound one

Section 5's heading read carries the deck digest, and `deck_scan.py` refuses a stale one before the
go-ahead. `rendered.md` is joined to the highest retained pass and its `deck.sha256`.
`adversarial.md` is read by nothing: `deck_scan.DECLARED_LIMITS` carries `adversarial-bytes-unbound`,
and `record-slide-agreement-unverified` says the agreement read "is not bound to the final deck until
#1229".

### The stale path has a recorded instance

#1034's grilling recorded on #1229 that, on the one `course-assignment` run that exists,
`adversarial.md` is older by file modification time than both the final `claims.md` and the submitted
deck. That comparison was taken against private working material and is not re-derived here. It is
the path ADR 0210's rejected options said no run had shown.

### Standing rule 6 already settles the no-subagent case

`AGENTS.md` standing rule 6: a **Second reader** does not complete when no second context is
available. The adversarial reader is a Second reader, so it takes no orchestrator-walk route.

## Ruling 1 — the adversarial read moves after section 5's render

Section 3 produces the deck and nothing more. The adversarial reader receives the PNGs of the
highest retained `render/pass-N/`, the final speaker-note text, and `claims.md`. Section 5's render
is the only render path the skill names. A repair to the deck makes a new pass, and the adversarial
read repeats on it as the visual read does.

## Ruling 2 — `adversarial.md` names the pass it read and `deck_scan` grades it

The orchestrator writes one record per read:

```text
## ADVERSARIAL: <course>-<module>-course-assignment-<date>.pptx
PASS: <positive retained pass number>
SLIDES: <read PNG count> of <deck slide count> read
UNSEEN: none | <what was not read>
CLAIMS: <SHA-256 of claims.md when the reader was briefed>
VERDICT: clean - <reason> | defect - <reason>
<findings keyed to slide number>
```

`deck_scan.py --pptx` and `--submission` gain an `adversarial-record` row joined the way
`rendered.md` is joined today. It refuses a missing or malformed record, a record naming another deck,
no record naming the highest retained pass, a highest pass whose `deck.sha256` differs from the named
`.pptx`, a slide or PNG count that does not match the deck, `UNSEEN` other than `none`, or a latest
verdict that is not clean with a reason. The bind to the deck's bytes, and so to its speaker notes,
comes through the pass; the record carries no deck fingerprint of its own. Like the rendered record,
the row fires on section 4's pre-render scan by design.

## Ruling 3 — the record is also bound to `claims.md`

`CLAIMS` is computed with `file_digest.sha256` when the orchestrator briefs the reader, named in the
brief, and written into the record. `deck_scan` refuses the record when it differs from the current
`claims.md`. A ledger-only repair, including section 3's own "add records for supported claims",
therefore sends the read back to a fresh adversarial reader. This narrows ADR 0210 ruling 8's "only
the draft is bound" for this one reader, which reads the ledger; the rejected per-row fingerprint in
ADR 0210 was declined for a path no run had shown, and #1034 has since shown it. The other readers
stay unbound to the ledger.

## Ruling 4 — the three final-deck readers run in a fixed order

Section 5 runs `deck_render.py`, `render_scan.py`, the visual read, the adversarial read, the heading
read, then `deck_scan.py --pptx` before the go-ahead. A repair that changes the deck returns to
`deck_render.py`; a repair that changes only `claims.md` returns to the adversarial read. Visual
repairs come first because they most often change the deck, and the heading read stays last because
the adversarial remedy edits the ledger it reads. The order is guidance: whatever order a run follows,
a stale record fails ruling 2 or 3 rather than passing.

## Ruling 5 — the declared limits move with the binding

`adversarial-bytes-unbound` retires. `record-slide-agreement-unverified` drops its "not bound to the
final deck until #1229" clause and keeps its first half. `adversarial-completeness-unverified` stays,
because the read still has no closed expected set. `tools/test_course_assignment_skill.py` binds the
moved brief and the record shape, and `tools/test_deck_scan.py` drives each refusal in ruling 2 and
ruling 3 with a clean control.

## Rejected options

**Section 3 names its own render into a numbered pass.** It keeps the read early, where a finding is
cheapest, and binds it by design to a pass that is not the final one whenever the deck changes after
it. That is the stale read ADR 0218 ruling 2 describes.

**Name the pass in the record and grade nothing.** The recorded stale instance would still pass in
silence.

**Leave `claims.md` unbound and rely on the final heading read.** The heading read checks that
headings agree with the slides. It does not look for an assertion with no record behind it, which is
the adversarial job.

**Run the three readers in parallel on one pass.** One repair discards the other two results.

## What none of this reaches

- **Whether the reader read what the record says it read.** A reader's work is unobservable; the
  record binds a verdict to inputs, not to attention.
- **Whether the reader found every unsupported assertion.** `adversarial-completeness-unverified`.
- **The DOCX branch.** It has no adversarial reader, so nothing here applies to it.
- **The run that already exists.** It is not re-graded under the new row.
