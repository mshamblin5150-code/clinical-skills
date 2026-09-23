# One-question grilling format

This is the binding question format for every grilling pass. It overrides the installed
`grilling` skill's instruction to ask the whole frontier in one round. Ask one decision question,
wait for the answer, recompute what remains, and only then ask the next question.

Every reply that asks a decision question uses this order:

1. State why the question exists before giving the options. Name the actual uncertainty,
   contradiction, or missing ruling that prevents the work from continuing.
2. Use plain words to carry the real facts. Do not make the clinician translate internal names,
   row numbers, ticket vocabulary, or implementation jargon before deciding.
3. Give lettered options. State the concrete cost of each option beside it.
4. Ask exactly one question in one block beginning with `❓`. Several question marks may clarify
   that one decision inside the same block; they must not introduce another decision.
5. Give a recommendation beginning with `➡️` and explain the reasons for it.
6. Write one line beginning `Held for later:`. Name the decisions deliberately deferred to later
   replies, or write `Held for later: nothing.`

When no decision remains, write this exact closing line:

**Frontier empty — confirm shared understanding.**

That line ends Stop-hook grading until a `grilling`, `grill-me`, or `grill-with-docs` skill file is
opened again. Questions after the closing line belong to the ordinary tail of the task.

Install or refresh this format and its Codex Stop check with one command from a clinical-skills
checkout:

```powershell
python tools/install_grilling_guard.py
```

The command replaces only its marked block in `~/.codex/AGENTS.md`, keeps every other line, and
registers the tracked Stop check beside existing user-level hooks. It also reduces an existing
Claude memory file named `grill-one-question-at-a-time.md` to a pointer to this tracked source.
