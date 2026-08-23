# An ADR carries no status field, because no record waits on `main` for a decision

[#472](https://github.com/mshamblin5150-code/clinical-skills/issues/472) found `tools/adr_next.py` scaffolding every new record as `---\nstatus: proposed\n---` above its heading, and no ratified ADR carrying that frontmatter. The clinician ruled on 2026-08-23.

## What was measured before anything was ruled

**No record has ever reached `main` carrying it.** Every record on `main` opens on its `# ` heading. `0017`, `0019`, `0020` and `0021` were all written after the tool landed and all four were stripped by hand; none of those sessions filed.

**And the field is being redefined as well as deleted, which was measured live rather than reasoned.** While this ticket was being grilled on 2026-08-23, two further sessions claimed numbers with the defective tool. `0023` carries `status: proposed` — while [#474](https://github.com/mshamblin5150-code/clinical-skills/issues/474), the ticket that produced it, says *"Ratified as ADR 0023"* in its own body. `0024` carries **`status: accepted`**: that session did not strip the field, it flipped it, inventing the transition this ticket's decision 2 says nobody has defined. **`0024` was committed to its branch during this grilling**, so a record carrying frontmatter is now on a ref awaiting merge, and the honest form of the claim above is about `main` rather than about every ref. That is the state a status field reaches when nothing says what it means: two documents assert it as house convention, four sessions silently delete it, one silently redefines it, and one is called ratified by its ticket while declaring itself proposed.

**The obvious re-derivation is compromised by this record, and that is worth more than the figure.** `git log --all -S "status: proposed" -- docs/adr/` returned zero until the commit carrying this record, which quotes the string in order to describe it and so answers **one — itself**. It also misses `0024` entirely, because that record says `accepted`. Describing the rule broke the instrument that checks it, which is [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153)'s shape arriving on an ADR. What re-derives durably is the corpus itself — every record on `main` opens on `# ` — which is exactly what the bind below asserts, and is the reason the bind reads the directory rather than searching history.

**Nothing reads it.** The only occurrence of `status:` in `tools/`, `docs/agents/`, `CLAUDE.md` and `AGENTS.md` outside exit-status vocabulary is `tools/adr_next.py` writing it. The field has no consumer.

**The format sheet this corpus otherwise follows calls it optional.** `ADR-FORMAT.md` in the `domain-modeling` skill lists Status frontmatter under *Optional sections*: include it only when it adds genuine value, "useful when decisions are revisited."

**The ticket's premise that nothing said which was right is false, and that is what made this worth a record.** [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) states under *What is ruled* that the command "writes the file with its heading and status lines already in it", and #452's respecced build spec says the file contains "the `# <Title>` heading and the house status lines." A convention was asserted twice on one day, in a ticket spec and in a ratified record, about a corpus that had never had one. Nobody opened `docs/adr/` to check, and no gate could have: a ratified record's prose fails nothing.

**No record on `main` is an open proposal.** Most say the clinician ruled them in as many words; `0001`, `0002`, `0003`, `0004` and `0011` do not, and record decisions taken in review, on a ticket, or in a grilling worded differently. Not one is parked awaiting a verdict. The count is `git ls-files docs/adr/`'s to answer and is deliberately not stated here, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms — it moved once while this record was being written.

## What is ruled

**An ADR here carries no status field.** `tools/adr_next.py` writes the heading and nothing above it.

**The reason is that there is no state to represent.** A status marks a record as proposed but not yet accepted, and a record reaches `main` here only after its decision is taken. `status: proposed` was therefore false on the day it was written, for every record the scaffold has produced.

**If the flow ever admits a record to `main` before its decision is taken** — a draft parked for a later ruling, a record kept after being superseded — **this reopens**, because that is exactly the state a status exists to represent. The rule is conditional on a property of the workflow rather than on taste, and stating the conclusion without the hinge would invite the next session to re-argue it from the format sheet with nothing to argue against.

**ADR 0016's clause is a fact and is corrected in place.** What that paragraph decides is *when* a number is claimed — "a number is claimed at the moment it is handed out… the claim and the check are the same act" — and that survives untouched. The clause enumerating what lands in the file describes the scaffold's contents, and its status half was untrue about the tree when it was ratified, which is [ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md)'s case exactly. The `## What is ruled` heading is a location; 0016 states the test as fact versus ruling.

**A test binds the scaffold to the corpus.** It derives the opening marker from `write_claim`'s own output rather than typing one, and asserts every `docs/adr/*.md` in the checkout opens the same way. One equality covers both directions: the scaffold gaining frontmatter stops matching the records, and a record gaining one by hand stops matching the scaffold. The denominator is reported and a floor assertion keeps an empty glob from passing vacuously.

## Considered options

**Keep the field and define what flips it.** Rejected. It would make every ratified record wrong, need a rule for the flip that [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s correction rule does not cover — a status is neither a fact nor a ruling — and buy a marker nothing reads. It also does not escape the correction: 0016's "house status lines" was false either way and would need the same dated line.

**Treat 0016's clause as a ruling and supersede it with this record**, keeping 0016's text behind a forward pointer, which is the arrangement [ADR 0014](0014-a-run-is-keyed-to-the-graded-artifact.md) used against [ADR 0005](0005-a-run-is-keyed-to-the-board.md). Rejected. That precedent handled a collision the earlier ruling could not have known about, where rewriting the sentence would have made the ruling look wider than it was. Here the clause was simply untrue, and 0014's arrangement would spend a record to say two words should go.

**Pin the scaffold to a literal in its existing test and stop.** Rejected as the ticket's own diagnosis. `test_adr_numbering.py` already pinned the frontmatter to a typed string, and a session editing the tool edits the literal beside it without the directory ever being consulted — two unbound copies, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

**Record the rule in 0016's correction line alone.** Rejected. A reader asking why there is no status has no reason to open a record about numbering, so the rule would be findable only by someone who already knew it — [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape on a rule instead of a figure. Adding the rule to 0016's body was worse: 0016 is ratified, and appending a ruling to a ratified record is not what its correction rule permits.

**A sentence in [`docs/agents/domain.md`](../agents/domain.md) instead of a record.** Rejected as the enforcement and adopted as neither. A prose rule that fails nothing is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) again, which is the defect this ticket was filed over. That file gains this record's number beside the [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) link it already carries, and no sentence restating the shape.

**Binding across every registered worktree.** Rejected. Another agent's half-written draft would turn this suite red for a reason that is not this repository's business, and CI has one checkout.

## What this does not reach, declared rather than left to be found

**The opening shape only.** A future scaffold appending a `## Status` section at the bottom of the file passes the bind untouched. What is bound is where a record starts, because that is the only part of a record the scaffold writes and every record shares.

**This checkout's `docs/adr/`.** A draft in another worktree is outside the population by choice, so the bind says nothing about a record until it is written here. That is why the build's own scope is *every record on `main` at build time* rather than a list: `0023` and `0024` were sitting with frontmatter in other worktrees when this was ruled, `0024` was committed to its branch before the grilling finished, and a named list would have been stale before the drone read it. A record that lands carrying frontmatter after the build turns the suite red for a session that did nothing wrong, and stripping two lines is the whole remedy.

**A convention invented in prose.** Nothing stopped "the house status lines" being asserted in a build spec and ratified in a record, and nothing added here would. A test binds a tool to a directory; it cannot bind a sentence to the tree it describes.

**Whether the correction to 0016 was honest.** [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) already declares that nothing checks an in-place edit for its dated line or for having touched a fact rather than a ruling. That is a reading, and this record does not change it.
