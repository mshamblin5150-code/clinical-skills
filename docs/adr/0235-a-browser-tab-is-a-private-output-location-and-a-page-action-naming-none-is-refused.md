# A browser tab is a private output location and a page action naming none is refused

[#1120](https://github.com/mshamblin5150-code/clinical-skills/issues/1120) was filed on
2026-09-11, split out of [#962](https://github.com/mshamblin5150-code/clinical-skills/issues/962)'s
thread after a `discussion-reply` refutation subagent navigated the run's open Canvas discussion tab
away on 2026-09-10. Nothing was typed or submitted, but that tab was the one the run later posts
from. [ADR 0194](0194-a-briefing-surface-declares-its-kind-and-points-at-standing-rule-6.md) ruling
8 declined to give the ticket a home and recorded that it did not settle where the rule lives.

Grilled 2026-09-14 to an empty frontier. **Ten rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.

## Measured before ruling

Every figure below is a historical measurement taken on 2026-09-14. The skill-file readings were
taken at `main` commit `9770b1a0` by reading the files; the transcript readings are over the local
Claude Code and Codex session transcripts, which are untracked and carry patient material, so they
were derived by throwaway scripts that printed counts only and are not re-derivable by anything
committed.

**The mechanism is stated by the tool itself.** The Claude in Chrome `navigate` tool, called with no
tab id, acts on the first tab in the session's tab group. A subagent shares that group with the
context that spawned it, so a call naming no tab lands on whichever tab happens to be first. That is
the incident exactly, and it is also the shape of a quieter failure: two parallel passes that both
omit the id read the same page, and one records a quote from the other's source.

**No tracked file tells any agent which tab to use.** A search of `skills/`, `AGENTS.md`,
`CONTEXT.md` and `reference/` for `tabId`, `tabs_create`, `tab group` and `own tab` as a word prints
nothing. *Had the rule been written in those words anywhere, the search would print a line.*

**The ticket's population was wrong in both directions and stopped mattering.** It named six skills;
its own thread corrected that to five, because `setup-clinical-skills` performs a capability check
and briefs no agent. Since then `vitalsource-chrome` landed and drives Codex Chrome, and
`icd10-cpt` sends its main agent through it. Ruling 9 binds every browsing context, so no skill list
is load-bearing.

**A browser-word detector cannot find the passages that use a browser.** Across the tracked
Markdown under `skills/`, reading found roughly forty lines instructing an agent to act in the
signed-in browser. The best of four candidate keys caught fewer than half of them with about a third
of its hits false, and most misses read as ordinary steps with no browser word — an upload, a
submission read-back, a Composer load. Three of the four keys also missed `vitalsource-chrome`'s
own instruction to open a new reader tab. This is [ADR 0182](0182-the-refusing-check-roster-lives-in-the-hook-and-prose-keeps-only-its-own-claim.md)
ruling 4's finding arriving on a new population, and it is why no ruling below keys a check on skill
prose.

**The ticket's decision 3 was false as written for Claude Code.** It said no mechanical reader can
see what a subagent did to a browser. Transcripts record every tool call's input, subagent calls
included, in `subagents/agent-*.jsonl` files beside each session. The liveness case is the incident:
on 2026-09-10 exactly one subagent Claude in Chrome `navigate` carries no tab id. The same reading
found 34 further subagent calls with no tab id on 2026-09-03, which nobody filed. *Had inputs not
been recorded, every call would read as naming no tab; batched actions name one on nearly every
call.*

**It is true for Codex.** Codex performs browser work through REPL code whose only parameters are
the code, a title and a timeout, so a tab choice sits inside the code and no parameter-level reader
sees it.

**A PreToolUse hook fires inside subagents.** Subagent transcripts carry PreToolUse hook rows, and
subagent `gh` calls switch from unhooked to hooked on 2026-08-31, the date the tracker publish hook
landed, in the same step as main transcripts do. *A broken join would read zero hooked on both
sides of that date.* A handful of subagent `gh` calls after that date carry no hook row and were not
classified; the hook's `if` guard skipping nested or heredoc shapes, and sessions started on an
older base, both fit. The ruling below rests on hooks firing in subagents at all, which those
exceptions do not contradict, and its hook takes no `if` guard.

**Which tab a call acted on is not settled by the transcripts.** Many page actions, main and
subagent, name a tab id the same context did not create through `tabs_create_mcp`, and none of the
subagent ones name a tab its parent created. But a tab also comes into existence through
`tabs_context_mcp` with `createIfEmpty` and through a `navigate` that names no tab, and the reading
parsed neither, so those counts overstate reuse by an unknown amount. What they establish is that
reusing a tab found in the group is common, not how often a ruling below would be broken.

## Ruling 1. A browser tab is a private output location

Each context opens its own tab, names that tab's id on every page action, acts on no tab it did not
open, and closes its tabs when done. This is standing rule 6's first sentence — one private output
location per writer — applied to the one shared location the rule does not yet name: subagents in
one task share a tab group the way they share a worktree, and the first tab is the fixed default a
call naming none writes into.

A narrower rule that only told an agent to open its own tab was refused because it leaves the
parallel-pass collision open, which is the quieter and more damaging form. A wider rule that an
agent does not disturb the clinician's live session was refused because it takes in logouts, cookie
banners, editor content and closed tabs, a class nobody has measured.

## Ruling 2. Standing rule 6 is the home, and the clause names no tool

The rule is a clause in `AGENTS.md` standing rule 6. It names no tool, so it binds a Codex run as
well as a Claude Code one.

A second standing rule was refused because it would state rule 6's principle twice. A new
`skills/_shared/reference/` sheet was refused on ADR 0194 ruling 5's ground: a sheet binds only by
link, so a skill that forgets the link is unbound. Writing it into each skill is the drift the
ticket's own *what must not come out of this* forbids.

## Ruling 3. The authenticated-route rule is filed, not consolidated here

The rule that research and refutation agents take the clinician's signed-in Chrome rather than the
in-app Browser pane is restated in several skills and in files outside `skills/`, and the
obligation to try it before giving up is stated in differing words. It is a different rule — which
browser reaches a subscription, not isolation between passes — and ruling 1 is correct whatever
happens to its copies. They share lines, not correctness, so it is filed as its own ticket rather
than widening this one.

## Ruling 4. Only the clinician hands over a tab, and only in chat

A context may act on a tab it did not open only when the clinician hands that tab to it in chat;
the context then owns it, including closing it unless asked to keep it. The main agent never hands a
tab to a subagent.

Refusing every handover was refused because a half-typed reply in the clinician's own tab would be
unreachable. Letting the main agent hand a tab to a subagent was refused because it rebuilds the
shared location ruling 1 removes, and no current skill needs it: the one reader that reads live
pages can open its own tab at the same address, and Canvas-box evidence is retained as captures.

## Ruling 5. A browsing subagent learns the rule from its brief

The rule 6 clause obliges the orchestrating context to state the tab rule in every brief that may
reach a browser. No skill file copies it; the sentence is written at run time.

Copying it into each skill's browsing paragraphs was refused because the population is not
derivable, measured above. Having the orchestrator create one tab per pass and name it in the brief,
rule 6's exact shape for paths, was refused because rule 6 allocates paths centrally only because
two passes could choose one name, and creating a tab returns a fresh id with no collision to prevent.
Relying on a subagent to read `AGENTS.md` for itself was refused because nothing shows it does and
the incident shows the rule did not reach it.

## Ruling 6. A tool that cannot address a tab degrades and declares

Where a browsing tool cannot name a tab by id, browsing passes run one at a time, each opens a fresh
tab before its first page action and acts only while no other context is acting in the browser, and
the record states that tabs were not addressed by id and that the clinician switching tabs mid-pass
is unprotected. This is rule 6's degrade-and-declare for a fan-out without parallelism.

Stopping browsing was refused because it would silently shrink the research these skills depend on.
Proceeding unchanged is the incident.

## Ruling 7. A tab is closed when its owner's task ends, and a leftover is reported

A subagent closes every tab it opened before returning its record; the main agent closes its tabs
after its terminal step, so a submission page held across the clinician's go-ahead stays open until
submission and read-back. A tab kept at the clinician's request, or one that fails to close, is
named in the report, so silence means none remain. This is rule 6's cleanup paragraph applied to
tabs.

Closing only on success was refused because an aborted fan-out would leave tabs in the shared group
for the next call naming no tab to land on.

## Ruling 8. The glossary names an Owned tab

`CONTEXT.md` gains **Owned tab**, with *the clinician's tab*, *the current tab*, *the active tab*
and *the live tab* as terms to avoid. The ticket and its thread said *the clinician's live Canvas
tab* for a tab the run had opened in the agent group, and a measurement pass in this grilling read
the group listing as the clinician's personal tabs. One word was carrying three things whose fixes
differ.

## Ruling 9. The clause binds every browser surface agents share

Signed-in or not, the in-app Browser pane included. The pane carries no clinician session, but it is
where parallel reading passes run most, and the transcripts show its calls name a tab id far less
often than Claude in Chrome's do. Ruling 1's reason — passes colliding with each other — applies to
it unchanged.

Narrowing to the authenticated route was refused because it leaves that collision open where it is
most likely. Exempting the pane from part of ruling 6 was refused because an exception for one
surface makes the word *tab* mean two things again, which ruling 8 just removed.

## Ruling 10. A pin, a refusing hook, and a reported row

- **The clause is pinned.** `briefing_surface.standing_rule_findings` already fails when standing
  rule 6 loses a shared floor; the tab clause becomes one more.
- **A PreToolUse hook refuses a page action naming no tab.** It covers the Claude in Chrome and in-app
  Browser tool families, inspects each inner action of a `browser_batch`, fires in subagents as
  measured, and names the remedy. Under ruling 1 a page action with no tab id is a violation in every
  case, a handed-over tab included, because the owner still names that tab — so the refusal cannot
  fire on a correct call.
- **The after-action review reports actions on a tab the context does not own.** It is reported and
  never graded, because a handover in chat cannot be read mechanically, and it states how many tab
  creations it parsed across all three ways a tab comes into existence.

Pinning the clause alone was refused because a prevention was measured available. Refusing an
unowned tab id in the hook was refused because a tab the clinician handed over is indistinguishable
there from another context's tab, so it would refuse correct calls.

## What this record does not settle

- **Whether a run obeyed the clause.** The hook reaches only a page action that names no tab, and the
  review reports ownership without grading it.
- **Codex.** A tab choice inside REPL code is invisible to a parameter-level hook or reader; ruling 6
  is the only protection there, and it is prose.
- **A page action naming another context's tab id.** It passes the hook and is only reported.
- **The ownership denominator.** The review row states its own parse coverage; this record states no
  figure for it.
- **Whether a brief carried the sentence.** A brief is written at run time into a context the
  review reads only as tool calls and results.
