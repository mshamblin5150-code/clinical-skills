# The voice read ignores line endings and its fingerprints stay on raw bytes

**Measured at:** 4c1cc8958837c7c9aa4144f187e8e879c7fce86f

[#1488](https://github.com/mshamblin5150-code/clinical-skills/issues/1488) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 10) on 2026-10-01. During a
correction the run rewrote its draft through Python text-mode writes on Windows, which turned every
line ending into CRLF. The planter remarked that the grader's rebuild of the planted copy would no
longer match, so the run converted both files back to LF and repeated the plant, the voice read and
the heading read. The ticket asked for either a named refusal of a CRLF draft or LF-only draft
writers. Grilled 2026-10-10 against `main`, where the freshness gate read `FRESH`; the clinician
ruled every point below in that session. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The planter's remark was wrong for the grader that run used.** `discussion_post_scan.py`,
`discussion_reply_scan.py` and `peer_critique_scan.py` read the draft with `Path.read_text`, whose
universal-newline mode turns CRLF into LF. The voice surface those graders hand to
`voice_read.draft_surface` is therefore LF text, and the rebuild from it matches an LF planted copy.
Driven on a two-line CRLF draft: the rebuild matched.

**The fingerprints never depended on the line endings.** `draft_surface` hashes the single
artifact's raw bytes, the planter and Voice reader records carry the same raw-byte digest, and the
heading read binds raw bytes through `file_digest`. A CRLF draft is one consistent fingerprint
until something rewrites it. The repeated reads in the filing run were caused by the run's own
conversion back to LF, which changed the bytes and so expired both reads.

**One grader does keep CRLF in the voice surface.** `checks_ledger.py` builds the case study's
surface from `document_bytes.decode("utf-8", errors="replace")`, which preserves carriage returns.
Driven on the same draft: the rebuild from that surface did not match the LF planted copy, and the
grader would report "planted copy differs in other than the named sentence," a finding that names
the wrong cause. The ticket's title is false for the run it came from and true, with a misleading
message, for `practicum-case-study`.

## Ruling 1 — line endings are not part of the compared voice surface

Every comparison the voice read makes is made on text whose line endings are normalized to LF:
CRLF and a lone CR each become LF, matching Python's universal-newline reading. The normalization
belongs to `voice_read` itself, so every completion grader inherits it whatever way it read the
draft. A CRLF draft then grades the same in every scoped skill, and the case study's misleading
finding has nothing left to fire on.

The ticket's refusal option was declined. Refusing a CRLF draft would turn away discussion drafts
that pass today, and complying with the refusal means converting the file, which changes its
fingerprint and forces both independent reads to be taken again: the exact cost the ticket was
filed over. Requiring the draft writers to emit LF was declined as the remedy: a written rule
cannot fail, drafts are written by several tools, and it would leave the case-study divergence
standing.

## Ruling 2 — the planted copy is normalized the same way

The planted copy's text is normalized to LF before it is compared with the rebuild and before quotes
are matched against it. The brief's instruction that the planter write LF stays as the convention,
and is no longer a pass-or-fail requirement. Refusing a CRLF planted copy would force the plant and
the Voice reader's read to repeat for a difference the voice read does not judge.

## Ruling 3 — fingerprints stay on raw bytes

The draft digest, the planted-copy digest and the heading read's draft digest remain SHA-256 of the
file's raw bytes. Normalization changes only the text being compared, never what a record binds to.
**So converting a draft's line endings after a read was taken still expires that read**, as the
`CONTEXT.md` entry for a voice read says of any change to the draft. That is the cost the filing run
paid, and after this ruling it is a cost only a conversion can cause.

## Ruling 4 — the heading read is unchanged

The heading read compares no rebuilt text. It binds the draft's raw bytes on both sides, so a CRLF
draft is consistent there already, and nothing in `heading_read.py` moves.

## What the build changes

- `tools/voice_read.py`: one normalization helper applied in `draft_surface` to `text` and
  `plantable_text`, and to the decoded planted copy before the rebuild comparison and quote checks.
  Digest computation does not move.
- `tools/test_voice_read.py`: a CRLF draft with an LF planted copy grades clean through each
  completion-grader shape, both the `read_text` shape and `checks_ledger.py`'s raw-bytes decode; a
  CRLF planted copy against an LF draft grades clean; a draft whose bytes change after the read still
  reports that the draft digest moved.
- `skills/_shared/reference/voice-read.md`: the planter section's LF instruction is marked as the
  convention, and one sentence states that the comparison ignores line endings while every digest
  binds raw bytes.

## What this record does not reach

- **Any check outside the voice read.** `research_ledger.py`, `reference_scan.py`,
  `discussion_post_scan.py`'s other rows, `post_html.py` and `docx_write.py` were named in the ticket
  as accepting a CRLF draft. Each reads in text mode, and nothing here claims or changes what any of
  them does with one.
- **A line-ending conversion after a read.** Ruling 3 keeps it expiring the read on purpose; the
  record cannot tell a conversion from a content edit.
