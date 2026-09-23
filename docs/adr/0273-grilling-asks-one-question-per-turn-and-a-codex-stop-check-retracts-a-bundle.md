# Grilling asks one question per turn and a Codex Stop check retracts a bundle

[#1392](https://github.com/mshamblin5150-code/clinical-skills/issues/1392) was filed from the
after-action review of the NUR 5042 Module 5 course-assignment run. A grilling pass asked several
decision questions in one turn although the clinician's workflow is one question at a time. Grilled
against `main` at `9c70aa19`, where the freshness gate read `FRESH`. The clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling, 2026-09-23

- **The failure was in Codex, not Claude.** The bundled turn is one plain-text assistant message
  (`phase: final_answer`, no tool call) in the archived Codex rollout of 2026-09-13
  (`rollout-2026-09-13T14-59-51-01a09c23-…`). It carries a `Grilling round 1` heading and four
  questions labeled `Q1` to `Q4`, each with a recommendation. The clinician corrected it in the next
  turn and the agent re-asked one question.
- **The skill Codex loaded asks for the bundle.** The rollout reads
  `~/.agents/skills/grilling/SKILL.md`, whose text says to ask the whole frontier in one round. The
  copy that update replaced, preserved under
  `~/.agents/backups/mattpocock-before-claude-1.2.3-20260910-162259/grilling/`, said to ask the
  questions one at a time; its `agents/openai.yaml` short description changed from *one question at
  a time* to *a round of questions at a time*. The skill update of 2026-09-10 is what introduced
  the bundling instruction.
- **Codex never held the rule.** The one-question correction lives only in Claude's memory folder
  (`grill-one-question-at-a-time.md`). Codex's memory store is empty, `~/.codex/AGENTS.md` is 0
  bytes, and the repo's `AGENTS.md` does not state it. The ticket's *retrieval alone did not prevent
  the recurrence* is therefore false for Codex: nothing was retrieved.
- **No hook in either harness refuses a chat reply before it is displayed.** Codex's Stop event
  (desktop build 26.915.4065.0) receives `last_assistant_message`, `stop_hook_active` and
  `transcript_path`, and a `{"decision": "block", "reason": …}` output starts a new model turn with
  the reason as its prompt — after the reply was shown. Read from the binary's embedded hook schemas
  and messages, not yet observed live. Claude Code's documented hooks have the same limit. The
  ticket's *fail before the turn is sent* is not reachable for a plain-text reply.

## Ruling 1. The question format lives in one tracked file

`docs/agents/grilling.md` holds the format both agents follow: say why the question exists before
the options; plain words carrying the real facts, not the repo's internal vocabulary; lettered
options, each with its cost; exactly one `❓` question per reply; a `➡️` recommendation with its
reasons; a held-for-later line, or a line saying nothing is held; and the fixed closing line of
ruling 5. It states that it overrides the grilling skill's instruction to ask the whole frontier in
one round. Claude's memory file points at it rather than keeping a second copy.

## Ruling 2. The installed grilling skill is not edited

The clinician refused rewriting the skill: *"i only want it to ask questions like you i don't want
to rewrite the whole damn skill."* The upstream text stays as installed, and the override sentence
in ruling 1 is the only answer to it. A differently named replacement skill was also refused,
because `grill-with-docs` loads `grilling` by name.

## Ruling 3. The format reaches Codex as an installed copy with a staleness report

One install command writes the format file's text into `~/.codex/AGENTS.md` as a marked block,
leaving the rest of that file alone. The Stop check reports when the block no longer matches the
tracked file. A pointer from `AGENTS.md` to the tracked file was refused because the 2026-09-13
turn shows the text in context winning over anything a pointer asks the model to open. Two hand-kept
copies were refused as the drift shape this repository keeps recording. The repository's own
`AGENTS.md` was refused because it is the consumer contract for the clinical skills and grilling is
maintainer tooling, and because the rule is the clinician's in every repository, not this one's.

## Ruling 4. A Codex Stop check retracts a bundle after display

A script tracked and tested in this repository is registered in the user-level
`~/.codex/hooks.json` by the main checkout's absolute path, beside the DAVID lifecycle hook, which
is the working precedent for that arrangement. A project-level `.codex/hooks.json` was refused
because it fires only in a trusted folder, the incident ran in a Codex worktree whose trust was not
confirmed, and the rule is not repository-scoped. The check exits at once when the session has not
opened a `grilling`, `grill-me` or `grill-with-docs` skill file, and honors `stop_hook_active` so it
never loops.

Inside an active grilling session it blocks, with a reason telling the model to retract and re-ask
one question in the format, when the final message has:

- two or more `❓` questions or plain-text question labels (`Q1`, `**Q2**`, `Question 3`);
- a `❓` question without its `➡️` recommendation or without its held-for-later line; or
- a sentence ending in `?` outside the `❓` block that is not inside quotation marks, backticks or a
  blockquote.

Question marks inside the `❓` block never count, so one decision written with several question
marks passes. A reply with no question passes. Grading wording for plainness was refused because
it is a reading, and a false refusal there teaches the reader to ignore the check.

## Ruling 5. A fixed closing line ends grilling for the check

A grilling session is graded from the skill load until a reply carries the fixed closing line
**Frontier empty — confirm shared understanding.** Replies after it are not graded, so the tail can
ask *merge?*; loading the grilling skill again restarts grading. Grading to the end of the session
was refused because it forbids the tail's own questions, and grading only marked replies was
refused because it drops the prose limb of ruling 4.

## Ruling 6. The acceptance is rewritten, and the refusal is honestly after display

The ticket's *refused before the turn is sent* is replaced by the after-display retraction of
ruling 4. The tests carry a synthetic reply shaped like the 2026-09-13 turn (heading, four labels,
plain text) that must be refused, and one case per passing shape. One live Codex run shows a block
really re-prompts, because that behavior is read from the binary and not yet observed. Codex holds a
new or changed hook until the clinician reviews it, so approving the hook is the clinician's step
and no build can take it.

## What this record does not settle

The Claude plugin copy of the grilling skill carries the same whole-frontier sentence. Claude's
memory has overridden it in practice and nothing here changes that copy; if it starts to bundle, it
is a separate ticket. Routing grilling questions through a question tool, so a pre-call hook could
refuse a bundle before display, was not taken up: Codex's default mode steers questions to plain
text, and the incident used no tool.
