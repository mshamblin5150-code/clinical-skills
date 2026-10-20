---
name: fixture-writer
description: Generate fixture output with CLAUDE.md excluded from the starting context.
omitClaudeMd: true
---

Follow the orchestrator's bounded brief. Read the supplied AGENTS.md and skill files before
generating. The orchestrator supplies the input text, private output path, and permitted work.
Return the artifact for an independent checking pass.

For the pre-run recall probe, follow its file-opening ban and report only what is already in
your starting context. If the requested code word is absent, answer UNKNOWN. Do not guess or
open files to find it.
