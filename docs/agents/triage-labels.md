# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

**Maintainer tooling.** Not a dependency of the clinical skills — see [AGENTS.md](../../AGENTS.md).

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

Defaults kept as-is. **All five exist on the repo**, created on first use.

## One local addition: `grilling`

| Label | Meaning |
| --- | --- |
| `grilling` | Carries unsettled decisions; run a grilling session before building |

Not from the skills — added here because this repo kept producing tickets that looked specified and were not.

**`grilling` and `ready-for-agent` are mutually exclusive.** A ticket with a decision still open is by definition not fully specified, and labeling it `ready-for-agent` sends an unattended agent off to guess. That is not hypothetical: [#8](https://github.com/mshamblin5150-code/clinical-skills/issues/8) carried a *"Settle before building"* section with two open questions **and** the `ready-for-agent` label, and its central premise turned out to be false as well — it named a fixture set that could not host the work at all.

So: if a ticket has a *"Settle before building"* section, an options list, or a question the maintainer has to answer, it gets `grilling` and **not** `ready-for-agent`.

## Choosing between them

- **`grilling`** — a decision is open. Options with trade-offs, a question only the clinician can settle, or a rule that would have to be invented to proceed.
- **`needs-info`** — nothing to decide, something to look up. A figure that has to be re-measured, or a contradiction where somebody knows which side is right.
- **`needs-triage`** — real, not yet sized or scheduled. Pairs with `grilling` where the decision is also unmade.
- **`ready-for-agent`** — every decision made, every input identified, no judgment left. If an agent could get it wrong by choosing reasonably, it is not this.
- **`ready-for-human`** — needs a signed-in browser session, a clinical judgment, or anything the agent must not do alone.

GitHub's own `bug`, `enhancement` and `documentation` are orthogonal and may be added alongside any of the above.
