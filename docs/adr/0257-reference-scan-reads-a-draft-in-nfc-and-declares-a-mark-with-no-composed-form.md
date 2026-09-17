# Reference scan reads a draft in NFC and declares a mark with no composed form

**Measured at:** 8e098e18ac90beafdf22cb2229a5e236a8c31f19

[#1168](https://github.com/mshamblin5150-code/clinical-skills/issues/1168) was filed from
[#959](https://github.com/mshamblin5150-code/clinical-skills/issues/959)'s grilling as ADR 0195
ruling 10 item 2. [#943](https://github.com/mshamblin5150-code/clinical-skills/issues/943)'s repair,
ratified in ADR 0151, folds a non-ASCII surname in `reference_scan`, and the ticket found that the
repair reaches NFC input only. Grilled 2026-09-17; the clinician ruled both points below the same
day. Freshness gate `FRESH` at `8e098e18`. Nothing is built here; this is the record the build reads.

## Measured before ruling

### The truncation is live, and its cause is one module's missing step

Driven at `8e098e18`:

```
reference_scan.citation_key(NFC 'Kübler-Ross') -> 'kubler ross'   NFD -> 'ku'
reference_scan.citation_key(NFC 'Muñoz')       -> 'munoz'         NFD -> 'mun'
reference_scan.citation_key(NFC 'Ångström')    -> 'angstrom'      NFD -> 'a'
reference_scan.first_word(<same, as an entry head>) -> the same pairs
```

`normalize()` already takes NFKD and strips combining marks, so the fold handles either form. The
truncation happens earlier: `NAME` and `FIRST_WORD` are built from `LETTER`, imported from
`discussion_artifact`, and `[^\W\d_]` does not match a combining mark. `discussion_artifact` puts its
value into NFC before matching; `reference_scan` matches the raw text. That is the whole difference
the ticket's control column shows.

### NFD is reachable in pasted evidence and absent from every draft measured

Counts only, over the owning checkout's roots on 2026-09-17:

| root | text files read | unread | not NFC | not NFC after a references heading |
| --- | ---: | ---: | ---: | ---: |
| `output/` | 44 | 0 | 0 | 0 |
| `scratch/` | 1,949 | 1 | 3 | 0 |

All three are `.txt` files, one in the UpToDate store and two under run directories, and every
combining mark in them composes under NFC. No Markdown draft is decomposed. So the form can reach a
draft by being copied out of a paste, and has not yet been observed to.

### What NFC leaves behind

A combining mark with no precomposed partner survives NFC. `Ą̃žuolas` in NFC is U+0104 followed by
U+0303, and `citation_key` still returns `a`. No such sequence occurs in the population above.

### #943's measurement cannot move, and the discriminating control is synthetic

NFC is idempotent on NFC text, and the measured `output/` population is entirely NFC, so a before
and after comparison of finding sets over it would print the same result whether or not the repair
worked. It settles only that the change does not disturb composed input. The claim that the repair
works is settled by an NFD twin driven through the public command, which fails before the build and
passes after it.

## Ruling 1 — the draft is put into NFC once, at the top of `read_document`

`read_document` normalizes its input text to NFC before any pattern runs. It is the one seam that
yields the body, the entries and the citations, so both sides of every join see composed letters,
and its four callers (`reference_scan`, `research_ledger`, `reference_class_census` and
`assignment_docx_scan`) inherit the repair without edits. The existing NFKD fold is unchanged and
still runs afterward, so composed input keys exactly as it does today.

This is not the second fold the ticket forbids. NFC composes and removes nothing; the fold #943 chose
stays the only fold. ADR 0151's recorded costs, including `Kübler` and `Kubler` reading as one author,
are neither widened nor narrowed.

## Ruling 2 — a mark with no composed form is declared, not built

A surname holding a combining mark that NFC cannot compose still truncates. `reference_scan.NOT_REACHED`
gains a row saying so, and a test drives `Ą̃žuolas` through the scanner and asserts the truncation, so
the row fails the suite the day a change makes it false rather than going stale. The clinician's
standing preference is to declare coverage rather than widen an instrument, and the measured
population holds no instance.

## Rejected options

**Widening the name patterns to accept combining marks.** It needs a local character class in
`reference_scan`, because the shared `LETTER` is `discussion_artifact`'s and that module is correct
as it is, and it changes several patterns instead of one entry point.

**Declaring the NFD gap and building nothing.** The composable case is closed by one line at a seam
that already exists, and its failure is a silent collision or exemption rather than a visible miss.

**Closing the non-composable residue now.** That is the widened-pattern option again, for a case the
corpus does not contain.

## What none of this reaches

**Text outside `read_document`.** A caller that matches draft text through another path is not
repaired by ruling 1.

**Whether a folded surname is the author the writer meant.** ADR 0151's accepted cost stands.
