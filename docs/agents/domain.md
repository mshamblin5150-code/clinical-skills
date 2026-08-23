# Domain Docs

How the engineering skills should consume this repo's domain documentation.

**Maintainer tooling.** Consumers of the clinical skills need nothing here — [AGENTS.md](../../AGENTS.md) is the entry point and stands alone.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root
- **`docs/adr/`** — read ADRs touching the area you're about to work in

If these don't exist, **proceed silently**. Don't flag their absence or suggest creating them upfront. `/domain-modeling` creates them lazily when terms or decisions actually get resolved.

When an ADR is warranted, claim its number and create its file together:

```bash
python tools/adr_next.py "short title of the decision"
```

Do not choose a number by eyeballing `docs/adr/`; the command reads every registered worktree's on-disk claims. A ratified record's facts may be corrected in place, with a dated correction line at the bottom recording what changed and why. Its ruling may not be rewritten. A filename is an index and may be corrected only with `git mv`, preserving `git log --follow`. [ADR 0016](../adr/0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md).

## File structure

Single-context repo:

```
/
├── CONTEXT.md
├── docs/adr/
├── skills/           ← the deliverable
└── reference/
```

## Use the glossary's vocabulary

When output names a domain concept, use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary avoids.

This repo's vocabulary is load-bearing and already carries meaning across [clinical-note](../../skills/clinical-note/SKILL.md), [batch-shift](../../skills/batch-shift/SKILL.md), and [icd10-cpt](../../skills/icd10-cpt/SKILL.md) — **shorthand**, **encounter**, **day file**, **given / derived / filled**, **proposed / asserted**, **branch**. Changing one of these words changes behavior in more than one skill, so treat a rename as a domain decision, not an edit.

If a concept isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use, or there's a real gap worth taking to `/domain-modeling`.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it rather than silently overriding:

> _Contradicts ADR-0007 — but worth reopening because…_
