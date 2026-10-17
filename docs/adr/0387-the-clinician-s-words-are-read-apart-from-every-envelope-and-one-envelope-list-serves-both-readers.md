# The clinician's words are read apart from every envelope and one envelope list serves both readers

**Measured at:** facb29d452bac3431393882ed80d2c79902db8c2

[#1693](https://github.com/mshamblin5150-code/clinical-skills/issues/1693) was filed from the
grilling of #1495. `aar_scan` labels a transcript user row as a whole, by the first
declared envelope tag found anywhere in it, so the clinician's typed words beside a system reminder
become one `system-reminder` entry and no `clinician` entry carries them. Grilled 2026-10-17 against
`main`; the clinician ruled every point below in that session. **Nothing is built here; this is the
record the build reads.**

## Measured before ruling

**Two readers decide what is machine text, from two lists.** `aar_scan._human_kind` labels a row by
`ENVELOPE_KINDS`, which [ADR 0193](0193-an-extract-entry-s-kind-names-its-envelope-and-a-matcher-may-label-where-it-may-not-reduce.md)
seeded from recorded instances on 2026-09-12. `aar_scan.clinician_text`, which
`approval_record.verify_clinician_reply` reads for every approval under
[ADR 0310](0310-an-approval-carries-the-clinician-s-whole-reply-and-is-refused-when-his-messages-do-not-hold-it.md),
strips `ENVELOPE_KINDS` blocks and keeps the rest, but first returns nothing for the whole row when
any of a second, hard-coded tuple of tags appears, "even if a trailer follows the wrapper". That
tuple and its comment arrived with #1474's build. No ADR rules the whole-row drop; ADR 0310's
Definition says the clinician's message is the row's text with the harness envelopes removed.
`hook-context`, `scheduled-trigger` and `automation-trigger` are on the second list and have never
been on the first.

**The real mixed rows were counted.** On 2026-10-17 every Claude Code main-session transcript and
every Codex rollout on the maintainer's machine was read by the repository's own readers, reporting
integers only: 616 Claude files and 390 Codex rollouts, none unreadable. These figures were taken
against private transcripts, so nothing committed re-derives them.

- 104 unflagged Claude user rows hold a `system-reminder` block with typed text after it, most of it
  under twenty characters. `_human_kind` labels all 104 `system-reminder`; `clinician_text` recovers
  all 104.
- 396 Codex user messages carry an `environment_context` item. In 384 the other item is the injected
  instructions file, opening with the line `# AGENTS.md instructions`, and in none is it typed text.
  39 more Codex messages are that instructions item alone. All 423 reach `clinician_text` as his
  text, and the 39 are labeled `clinician`.
- `hook-context`, `scheduled-trigger` and `automation-trigger` reach no unflagged Claude user row and
  no Codex user message. Where the first two appear in a Claude user row at all, the row carries
  `isMeta`, which both readers already exclude.
- Unlisted machine wrappers reach both readers as his words: in Codex, 152
  `external_codex_apps_open_page` items, 22 `skill` items and 13 `send_user_message_question_reply`
  items; in Claude, 3 `cross-session-message` rows and 3 `david_lifecycle_wake` rows.
- Each `send_user_message_question_reply` item holds a JSON list whose entries carry exactly
  `question`, `answer` and `questionItemId`.
- 643 Claude rows open a slash command. 628 carry `<command-args>` text, 222 of it longer than twenty
  characters. `_human_text` blanks 614 of the rows, and the other 29 are labeled `command-name`, so no
  slash command's typed arguments reach a `clinician` entry.

## Ruling 1 — a row holding envelopes and his words becomes separate entries

A transcript user row is read as pieces in text order. Envelope text forms a machine entry labeled by
its envelope, and the **Clinician's words** form a separate `clinician` entry. A row with no
recognized envelope stays one entry as today. Keeping one entry labeled by its remainder was declined
because the envelope text would then be read as his, which is ADR 0193's defect in the other
direction. Keeping the envelope label with a note beside it was declined because his words would stay
under a machine label, which is this ticket's defect.

## Ruling 2 — the injected instructions item is recognized by its opening line

A Codex user item opening with the line `# AGENTS.md instructions` is a machine entry with its own
kind, `agents-instructions`, whether or not an `environment_context` item travels with it. Both
readers set it aside. The extract prints how many items it recognized this way on every run, so a
changed header shows as that count falling to zero rather than as a silent relabel. Refusing to split
any Codex message carrying `environment_context` was declined: it leaves the 39 lone instructions
messages labeled `clinician` and would hide his words if Codex ever put them in such a message.

## Ruling 3 — one envelope list serves both readers

`ENVELOPE_KINDS` is the single declared list of machine envelopes, and the after-action extract and
the approval reader both read it. Each listed envelope is set aside and whatever remains is the
Clinician's words. Two lists with a parity test, and two lists allowed to differ, were declined: the
first catches drift only after someone writes it, and the second is today's state.

## Ruling 4 — no envelope erases the whole row, and the three unobserved tags leave the code

The second tag tuple in `clinician_text` and its whole-row drop are retired. `hook-context`,
`scheduled-trigger` and `automation-trigger` are removed rather than listed, keeping the list seeded
from recorded instances as ADR 0193 ruled. What excludes them is the form they were measured to
arrive in, a flagged row, and a test pins that a flagged row never supplies a reply. Keeping the three
as ordinary listed envelopes was declined as labels for things never observed; keeping the whole-row
drop was declined because its only measured effect is refusing a real reply, which ADR 0384 rulings 2
and 4 would turn into a refused submission or coding batch.

## Ruling 5 — a Codex question reply splits into the question and his answer

A `send_user_message_question_reply` envelope is read through its declared JSON fields. Each entry's
`question` and `questionItemId` are machine text, and each `answer` is the Clinician's words. The
extract gives the question its own envelope kind, `codex-question`, and each answer a `clinician`
entry; the approval reader reads only the answers. Setting the whole envelope aside was declined
because every answer he gives in a Codex question dialog would vanish from both readers. Leaving it
unlisted was declined because the agent's question would keep reading as his words.

**This is a declared exception to ADR 0193 ruling 2's refusal to read inside an envelope.** That
refusal was against inferring an envelope's origin from its contents. Here the envelope's own field
names say which part is his, so the reader takes a structured field rather than guessing an author.
No other envelope is opened.

## Ruling 6 — words typed after a slash command are the Clinician's words

A slash-command row's `<command-name>` and `<command-message>` blocks are one machine entry labeled
`command-name`, and its `<command-args>` text is the Clinician's words, read by both readers. The
`<command-message>` prefix drop in `_human_text` is retired. Filing this separately was declined
because it is the same defect in the same function, fixed by the same rule.

## Consequences the rulings fix without a further choice

**The four observed unlisted wrappers join the list.** Under rulings 3 and 4 the list holds what was
recorded. `external_codex_apps_open_page` takes kind `codex-app-page`, `skill` takes `codex-skill`,
`cross-session-message` takes `cross-session-message`, and `david_lifecycle_wake` takes
`david-lifecycle-wake`. ADR 0310 already rules that a relayed session's message never counts as his.

**Contiguous envelope text is one machine entry.** Adjacent envelope blocks, with only whitespace
between them, form one entry labeled by the first recognized envelope, which is today's labeling
applied to a piece instead of a row. Each contiguous run of the Clinician's words is one `clinician`
entry.

**Entry identity.** A row's first piece keeps the row's identifier, and each later piece takes the
identifier with `#2`, `#3` and so on appended. A prior watermark naming a row still names its first
piece, so nothing already reviewed reopens. A watermark on a mixed row places that row's later pieces
after it.

**Approval compares each piece whole.** ADR 0310 ruling 4's whole-message comparison applies to each
piece of the Clinician's words separately, so a reply equal to the words beside a reminder verifies,
and a reply equal to one Codex answer verifies.

**The `clinician` description narrows.** `ENTRY_KIND_DESCRIPTIONS["clinician"]` describes the
Clinician's words in an unflagged user row, read apart from every recognized envelope.

## Supersedes

- [ADR 0193](0193-an-extract-entry-s-kind-names-its-envelope-and-a-matcher-may-label-where-it-may-not-reduce.md)
  ruling 2, its definition of `clinician` as a user row with no harness flag and no recognized
  envelope. Under ruling 1 here `clinician` is the Clinician's words read apart from every recognized
  envelope, and ruling 5 here is a declared exception to its refusal to read inside an envelope. Its
  rule that a kind names the envelope and never the origin stands.

## What this does not reach

**The two lifecycle-wake rows with outside text.** Two `david_lifecycle_wake` rows carry text outside
the envelope whose author was not established, because establishing it means reading it. Under
ruling 3 that text becomes a `clinician` entry, and the classifier reads it.

**A future unflagged `hook-context` row.** Under ruling 4 such a row would be unlisted, so a reply
beside the block would not equal the row's text and the approval would refuse, as it does today but
for a different reason. The extract's undeclared-envelope count would show it. None has occurred.

**Words inside a reminder.** Text the harness carries inside a recognized envelope is never read as
his, even where the harness is relaying something he typed. Only ruling 5's declared fields are
opened.

**Only this machine's transcripts were measured.** Remote and cloud sessions are outside the
population, and a wrapper first appearing there is caught only by the undeclared-envelope count.

## Build checklist

- `tools/aar_scan.py`:
  - Split each user row into pieces in text order under the rulings above. Give a later piece the
    `#n` identifier, and keep the watermark and prior-review readers working on piece identifiers.
  - Add `agents-instructions`, `codex-question`, `codex-app-page`, `codex-skill`,
    `cross-session-message` and `david-lifecycle-wake` to `ENTRY_KIND_DESCRIPTIONS`, and the four tag
    mappings plus `command-message` to `ENVELOPE_KINDS` and `ENVELOPE_ENTRY_KINDS`.
  - Print the recognized `agents-instructions` count on every extract.
  - Give `clinician_text`'s successor the pieces' Clinician's words and remove its second tag tuple.
- `tools/approval_record.py`: `verify_clinician_reply` compares the reply with each piece of a row's
  Clinician's words.
- `CLAUDE.md` **After-action review** names the split without copying the kind list.
- Tests, each driven through `reduce_transcript` or `verify_clinician_reply` on synthetic rows:
  - A reminder followed by a sentence gives a `system-reminder` entry and a `clinician` entry holding
    the sentence, and that sentence verifies as an approval.
  - A Codex `environment_context` item plus an instructions item gives no `clinician` entry, and a
    lone instructions item is `agents-instructions`. Replace the header with another line and the
    printed recognized count falls to zero.
  - A question reply with two entries gives one `codex-question` entry and two `clinician` entries,
    and either answer verifies.
  - A slash command with arguments gives a `command-name` entry and a `clinician` entry holding the
    arguments.
  - A flagged row containing `<hook-context>` or `<scheduled-trigger>` supplies no reply.
  - Each of the four observed wrappers alone gives its own kind and no `clinician` entry.
  - A prior watermark naming a mixed row still resolves.
  - The ticket's 2026-10-16 comment shapes, an unflagged `<hook-context>` or `<scheduled-trigger>`
    block followed by `Submit it.`, still refuse `Submit it.`, as the limit above records.
