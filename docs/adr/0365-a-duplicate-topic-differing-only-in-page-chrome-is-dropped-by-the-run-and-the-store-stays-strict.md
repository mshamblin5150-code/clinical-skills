# A duplicate topic differing only in page chrome is dropped by the run and the store stays strict

**Measured at:** 8276712c3fd211714ea8ac1f7e38883f5a05543e

[#1578](https://github.com/mshamblin5150-code/clinical-skills/issues/1578) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). Its section 7
is the one item still open. The store refused that run's Titled copy because one topic appeared
twice, the two copies differing only in trailing page chrome. The agent compared them, kept one,
and recorded the drop. The clinician accepts that outcome, but the Titled copy route in
`skills/practicum-case-study/SKILL.md` step 3 says nothing about the case, so the next run has to
work it out again. Grilled 2026-10-16 against `main` at `8276712c`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The store cannot tell a chrome-only duplicate from a content duplicate.** Synthetic dumps were
driven through `uptodate_store.parse_topics`, each carrying one topic title twice over otherwise
identical blocks:

| second copy | result |
| --- | --- |
| byte-identical to the first | parsed, 1 topic |
| adds a trailing `Print \| Share \| Back to top` line | refused, `untitled 2 of 2` |
| adds a trailing clinical sentence | refused, `untitled 2 of 2` |
| absent, the run having dropped the chrome copy | parsed, 1 topic |

The chrome-only and content-differs rows produce the same refusal, so the store holds no signal
separating the case this ticket asks about from the case
[ADR 0212](0212-the-evidence-row-grades-only-an-ingested-file-and-an-untitled-dump-is-filed-as-a-titled-copy.md)
ruling 4 keeps refused on purpose. Had the store already recognized chrome, the second row would
have parsed. Separating the two rows takes either a reading or a list of chrome wording.

**The refusal names the wrong remedy for this case.** Both refused rows say `untitled` and tell the
run to write a Titled copy, including when the input already is one. The refusal still sends the run
to the Titled copy route, which is where ruling 1's instruction lands, so this record leaves the
message alone. It is recorded on the ticket as a finding.

## Ruling 1 — the run decides that a duplicate differs only in chrome, and records the drop

When one topic appears twice in a dump and the two copies differ only in page chrome (a trailing
navigation line, a print footer), the run keeps one copy, adds the dropped copy and the exact
difference to the Titled copy's block-to-title mapping, and then ingests. Copies whose bodies differ
in content are not chrome. The store's refusal stands for them until the run resolves which topic
each block is.

`uptodate_store.py` does not change. Its refusal of a shared title over different bodies, ruled in
ADR 0212 ruling 4, stays the strict backstop: an error the run makes in the strict direction is
still caught.

**Teaching the store a list of chrome patterns was declined.** It is ADR 0212's rejected
closing-boilerplate option arriving at a second boundary. The list reads the publisher's page
wording and grows only when a new pattern is observed. A pattern that is too loose would merge two
copies whose content differs, and nothing downstream would catch it. **A run-and-store check was
also declined**, one that would accept a drop only when one copy equals the other plus trailing
lines. The store never sees the dropped copy, so the filing route would have to carry it. That rule
would also pass a copy cut short at the end. The accepted cost is that "only chrome" is the run's
reading and the store cannot check it. Titles in a Titled copy stand on the same footing, and the
mapping is what makes either reading auditable.

## Ruling 2 — keep the clean copy, and never edit a kept block

The run keeps the copy that carries no trailing chrome. Where both carry some, it keeps the first
in dump order exactly as written. A Titled copy chooses blocks and adds titles. It never rewrites
the source's text.

Always keeping the first copy was declined because it can file chrome that a clean neighbor lacked,
for no gain. Trimming the chrome from the kept copy was declined because it makes the run an editor
of the source's words, with only the mapping showing what was deleted. The accepted cost is one
stray chrome line filed with a topic when no clean copy exists. Nothing reads that line as a date or
as content.

## Ruling 3 — the glossary's Titled copy names the drop

`CONTEXT.md`'s **Titled copy** entry gains the second permitted difference from the handover, so
the definition does not describe only titles once ruling 1 lands. That edit lands with this record.

## Build checklist

- `skills/practicum-case-study/SKILL.md` step 3, the Titled copy route paragraph: state rulings 1
  and 2 after the sentence naming what `uptodate_store.py ingest` merges and refuses. The text says
  what the mapping records (the dropped copy and the difference), that a content difference is not
  chrome and stays refused, and that a kept block is never edited.
- No change to `tools/uptodate_store.py` or its tests.

## What this record does not reach

- **Whether a dropped copy really differed only in chrome.** That is the run's reading. The mapping
  records it and the after-action review reads the run.
- **A duplicate whose copies both differ in content.** ADR 0212 ruling 4's refusal and the run's
  resolution of which topic each block is still govern it.
- **The other coursework skills.** The Titled copy route is written in `practicum-case-study` step 3
  alone today. Where another skill files an untitled dump, the same reading applies when that skill
  gains the route.
