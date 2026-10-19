# Existing skill text after a live edit

On 2026-10-19, the #1806/#1879 build ran Claude Code CLI 2.1.284 against a
throwaway directory containing one project skill, `live-text-probe`. One process
stayed alive with `--input-format stream-json --output-format stream-json`.
Only project settings were enabled, MCP configuration was empty, and the Skill
tool was allowed. No repository or account material was opened.

The skill's first instruction was `Reply only with BEFORE_1806.` The first user
turn asked the model to invoke it through the Skill tool. After the result, the
driver rewrote that same SKILL.md to `Reply only with AFTER_1806.` and sent the
same request through the same process. The first trial returned `BEFORE_1806`
on both turns, with `is_error: false`. A second independent process repeated
the experiment while recording tool events: both turns emitted a Skill call
and a successful `Launching skill: live-text-probe` tool result, and the final
results were `BEFORE_1806` then `AFTER_1806`, both without an error. Each temporary
directory was removed after terminating its process.

The measured population is four invocations of one existing project skill across
two CLI processes, with no unread result. The second trial's `AFTER_1806`
demonstrates that edited text can reach an existing session; the first trial
shows that the observed answer does not reliably reflect it. The first trial
did not retain tool events, so its answer alone cannot distinguish a cached
answer from a missing invocation. This is distinct from ADR 0407's added-skill
probe. Neither trial establishes desktop-app reload behavior. The startup line
therefore promises updates for the next session, and `skills_mirror.NOT_REACHED`
owns the remaining boundary.
