# A briefing surface declares its kind and points at standing rule 6

[#962](https://github.com/mshamblin5150-code/clinical-skills/issues/962) was filed on 2026-09-08
out of [#818](https://github.com/mshamblin5150-code/clinical-skills/issues/818)'s fan-out mapping,
and left deliberately unbuilt by
[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md) ruling 9. Its
claim was *four structural rules, restated across nine agent-briefing surfaces in seven skill
files, with no check between any copy*. It asked for an unattended measurement first and named four
decisions behind it.

Eleven sweep comments followed over four days. They corrected the headline population twice, the
shared sheet's rule count three times, two stale test coordinates, and the directory's file count
twice. **Not one of them ran the measurement the ticket opens by requiring**, and every correction
was taken against the body's own enumeration rather than against the tree.

Grilled 2026-09-12 to an empty frontier. **Eight rulings, by the clinician, on that date.** Nothing
is built here; this is the record the build reads.

## Measured before ruling, at `595fbb88`

Freshness gate `FRESH` at `595fbb88` before any ticket was read. The measurement was run by five
readers over the ten `skills/*/SKILL.md` files, each reading its files in full rather than
searching them, with the surface population derived by reading rather than from the ticket's list.
Every figure below was re-derived by hand afterwards.

**The population is roughly forty surfaces, not nine and not twelve.** `practicum-case-study` alone
carries fourteen. The exact denominator is deliberately not stated as a figure: three readers
flagged borderline surfaces, and the count moves with whatever rule a build adopts for what counts
as one. What is stated is the order of magnitude and the direction, because both decide the ruling.

**Three of the ten skill files have no briefing surface at all.** `batch-shift`,
`setup-clinical-skills` and `clinical-note`, the last being 1302 lines and carrying more
verification machinery than any other file here, all of it performed by the authoring pass.

**The four rules are not one rule with N spellings, and they do not have the same answer.**

| | measured | shape |
| --- | --- | --- |
| prewrite the headings | temporal at `discussion-reply:108`, `peer-critique:130`, `practicum-case-study:532`, `:1055`; positional only in `discussion-post` and `course-assignment`; inverted in `aar`, which fixes the population before the spawn and writes headings after; absent in `icd10-cpt` | a family |
| one writer | stated twice in each of the five fan-out skills, and once in `aar` in its own words | near-invariant, one exception |
| independence | stated everywhere, in four incompatible vocabularies | a family with a real tightening and real looseners |
| serial fallback | `practicum-case-study` only, at `:474`, `:812`, `:1262` | not a shared rule |

*Had the serial fallback been a restated rule, `grep -rn "no subagent tool" skills/` would print
hits in several files; it prints three lines in one file.* `icd10-cpt:184`'s *"a serial harness may
run the reader later, provided its context contains the brief and not the worksheet"* is a
different rule: it preserves blinding under serialization and says nothing about having no second
context at all.

**The one-writer exception is an inversion rather than a tightening.** `icd10-cpt:186` briefs the
reader itself to "record:" its JSON. Every other skill says the subagent returns and the
orchestrating context alone writes.

**The independence vocabularies are "a fresh non-authoring context", "a different agent briefed to
refute", a bare "a fresh reader" who is handed the draft, and delegation by reference to standing
rule 6.** Only `discussion-post:271` states the underlying principle as a rule: *"One context never
grades an artifact it authored."*

**The shared home already exists and already binds every skill.** `AGENTS.md:117`, standing rule 6,
states one writer verbatim — *"Where several results belong in one artifact, passes return them and
the orchestrating context is the sole writer"* — and states independence with its re-check limb —
*"Authors do not check or tune their own generated artifacts… a fresh non-authoring context checks
the correction again. An author's self-report is never substituted for either read."* The section
preamble reads *"These bind every skill in this repo."* Five skills already point at it by name.
**So the forty surfaces are restatements of a rule that already binds them**, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s defect in its pure form,
and the ticket's premise that there is no shared home is false for two of its four rules.

**What standing rule 6 does not carry**: the prewrite rule, whose "before a fan-out starts" clause
is about private paths rather than record headings; either half of the serial fallback; the
refute-rather-than-confirm brief, which is stronger than non-authoring; and blinding by whitelist.

**The existing checks are eight hand-typed assertions in four files, and seven of the eight pin one
skill.** `test_research_ledger.py:2089`, `:2107`, `:2108`, `:2112`; `test_checks_ledger.py:1180`,
`:1181`; `test_reference_scan.py:1539`, `:1549` all read `practicum-case-study`;
`test_specificity_scan.py:973` reads `icd10-cpt`. **`grep -rl "non-authoring" tools/*.py` returns
nothing**, so the vocabulary the other five briefed skills use to state independence is bound by
nothing at all.

**`EveryRuledFanOutReadsTheSharedSourcingRules` at `tools/test_research_ledger.py:1661` binds
sourcing-sheet pointing, not fan-out governance**, and its `SURFACES` population at `:1665` is a
hand-typed dict. It is correct today. A fan-out skill that never links the sheet is invisible to
it. `apa7.md:34` carries a `**Readers:**` line held equal to the tree-derived linked set;
`sourcing.md` carries no such line.

**A prose detector is available here, which is the measured difference from
[ADR 0182](0182-the-refusing-check-roster-lives-in-the-hook-and-prose-keeps-only-its-own-claim.md)
ruling 4.** That record measured three candidate keys for finding a prose surface and declared the
blind spot rather than closing it, its best key being blind to the four largest real surfaces. Here:

```bash
grep -lEi "fan out|fresh (reader|checker|context|adversarial)|non-authoring|a different (agent|context)" skills/*/SKILL.md
```

returns exactly the seven skills the readers found briefing surfaces in, and **zero** in the three
they found briefing-free, at 44 line hits against a reader estimate near forty. *Had the vocabulary
been as diffuse as #914's roster language, that command would hit the 1302-line briefing-free file;
it hits none of the three.* Zero false positives on the briefing-free files is the direction that
matters, because firing on correct prose is what made all three of #914's keys unusable.

## Ruling 1. The bound population is the skill files and the rules are citable from anywhere

`skills/*/SKILL.md` is the population a check may grade. The shared rules are written so that a
brief living anywhere else — an ADR, a ticket spec, a registry — points at the same sentence and is
**ungraded**, and the record says so rather than implying coverage.

The alternative of ruling over every briefing surface wherever it lives was refused because no walk
enumerates ticket specs, so the wider claim buys a check that cannot exist. The alternative of
ruling only over `skills/` was refused because ADR 0154 ruling 6 already briefs a refutation reader
that will never live in a `SKILL.md`, so a skill-local sheet would have that reader re-inventing
independence as instance ten.

## Ruling 2. This record rules deduplication and coverage in one pass

The ticket's premise is duplication, whose fix is one home plus a bind. The measurement falsifies
that for two of its four rules: the serial fallback is stated once and missing from five briefed
skills, and one-writer has an inversion rather than a divergence. Deduplicating either is a no-op.

**So the ruling also states what a run must do**, and a surface that falls short fails rather than
passing silently. Ruling only the wording would leave the strongest finding the measurement
produced — five skills with no floor for a harness that cannot spawn — recorded on a ticket and
fixed by nobody, which is #59's defect one level up.

## Ruling 3. A briefing surface is one of three kinds, and the serial fallback is two rules

The surfaces sort into three shapes that take the rules differently.

- **A fan-out brief.** N workers, one record each, one file.
- **A second reader.** One reader returning one record.
- **A grader handoff.** A non-authoring context runs a committed command and returns its result.

A uniform floor was refused on the measurement: roughly fifteen of the forty surfaces are grader
handoffs, which write no record, so demanding a prewritten ledger of one fires on correct prose
across more than a third of the population by construction. Collapsing to two kinds was refused
because it hides the asymmetry the ticket turns on — in a fan-out, independence is a property of
the refutation leg, and in a second reader it is the property of the surface itself.

**And the serial fallback is two rules wearing one name.** *No parallelism* is stated today and is
meaningful only for a fan-out. *No second context* is stated nowhere in the repo and is the floor
the second readers and grader handoffs are missing. Keeping them as one rule is why five skills
look like they have the same gap when two different things are absent.

## Ruling 4. What a run does without a second context is answered per kind

The tree answers this twice, oppositely, and nothing notices. `practicum-case-study:812` works the
briefs *"one at a time in the main context, into the same ledger"* because *"the parallelism is a
speed property, and the grader cannot tell the difference"*, which read with `:652` — *"The
independence is an instruction and not a check"* — permits the author to refute itself and says so.
`icd10-cpt:433` rules that *"A missing, partial, or self-authored read is not completion."*

- **A fan-out degrades and declares.** The ledger and the brief are the mechanism, so serial work is
  genuine, and the record states that the refutation leg was self-authored.
- **A second reader stops.** The reader's independence is the deliverable, so nothing is left when
  the reader is the author, and the surface does not complete.
- **A grader handoff degrades with the raw result preserved.** A committed command's result is
  mechanical and re-derivable by anyone, so the author may run it provided it reports that result
  verbatim rather than a summary of it.

Applying either existing answer everywhere was refused. `practicum-case-study`'s would keep the
concession that voids its own independence rule on a serial harness. `icd10-cpt`'s would block a
research fan-out for nothing, since the ledger is still one record per claim against one brief and
the second-route field must still differ.

**`icd10-cpt` is not a local tightening.** It is the second-reader answer, correct, stated where a
second-reader surface lives, and the ticket's worry that centralizing would flatten it is answered
by the kind rather than by an exception.

**This changes a shipping skill.** `practicum-case-study:1262` currently sends step 9's readers
serially into the main context; step 9 is a second-reader fan-out, so it loses that. Step 3 keeps
its behavior.

## Ruling 5. Standing rule 6 is the home and the glossary names the kinds

`AGENTS.md` standing rule 6 grows to carry the prewrite rule, both halves of the serial fallback,
and the refute-rather-than-confirm brief, with scope carried by the noun rather than by a table. No
new shared sheet is created.

A new `skills/_shared/reference/` sheet was refused because it would move a rule that binds every
skill into one that binds by link, and the rule being centralized is precisely the rule about not
trusting a context to police itself. Splitting by altitude was refused because it creates the second
home this ticket exists to remove.

**`CONTEXT.md` names the three kinds and `AGENTS.md` states the rules.** A taxonomy is glossary work
and belongs where the glossary is, which is what keeps the addition to the root contract file to a
few sentences and what makes a per-kind floor writable without that file carrying a table.

## Ruling 6. A surface names the rule, declares its kind, and states only its narrowing

A briefing surface names standing rule 6, declares which of the three kinds it is, states its own
narrowing if it has one, and **copies no shared row**. A narrowing is a sentence the shared rule
does not contain — a blinding whitelist, a capability requirement, an ordering gate.

Saying nothing and relying on the rule's reach was refused. Ruling 4's content is that a fan-out
degrades and a second reader stops, and a rule nothing can attribute to a kind is a rule nothing can
apply — this ticket's own subject arriving inside its fix. Declaring the kind once per section was
refused because a mixed section is the normal case here rather than the exception: a fan-out and its
grader handoff sit under one heading in every one of the five fan-out skills, and `practicum-case-study` step
9 is both at once.

The cost is one clause at each surface, on the order of forty, most of them a single noun inserted
into a sentence that already exists.

## Ruling 7. The check derives its population at two levels

Skill level is the detector's file partition, measured above. Surface level is the declared kind
clauses. The check then asserts that **every detector line sits inside a declared surface**, so a
spawn-shaped sentence carrying no declaration fails rather than passing unseen.

A hand-typed surface list and a marker-keyed population were both refused for the same reason: each
prints the same thing whether or not the thing it is named for has happened. A marker-keyed
population is structurally blind to the one surface this ticket is about, which is a surface that
forgot.

*If a skill gained an undeclared fan-out, the detector would find its line, that line would sit in
no declared surface, and the check would go red. If the claim holds, the unaccounted count is zero.*

**`EveryRuledFanOutReadsTheSharedSourcingRules.SURFACES` is retired in the same change**, since the
same file partition derives it. One edit removes two hand-kept populations.

## Ruling 8. The browser-brief family is filed rather than widened

A recorded incident on 2026-09-10 had a refutation subagent navigate the clinician's live Canvas tab
away, the tab the run later posts from. The authenticated-route rule is already copied four times
across `discussion-post` and `discussion-reply`; the own-tab rule is stated nowhere.

That is this record's shape and not its subject. The four rules here are all about who writes and
who reads a record; the browser rules are about not disturbing the clinician's live session, and
nothing about the rulings above changes if they exist.

**It is already filed, as
[#1120](https://github.com/mshamblin5150-code/clinical-skills/issues/1120), and that ticket is wider
than this thread priced it.** The grilling sized the family at the three skills #962's comment
names; #1120 re-derived six, because `course-assignment`, `peer-critique` and
`setup-clinical-skills` also reach the signed-in session. *Had the split been the three, its
`grep -ln` would print three files; it prints six.* Nothing further is filed here, and the widening
is recorded because it was found by searching the tracker before filing rather than by the
measurement above.

The mechanism ruled here — standing rule 6 as the home, a declared kind, a two-level derived
population — holds a browser rule with no redesign, and that is asserted rather than measured.
**It does not settle #1120's first decision.** A browser rule governs a side effect on the
clinician's session rather than who writes or reads a record, so whether standing rule 6 is its home
too is that ticket's question and not this one's.

## What this record does not settle

- **Whether a surface is the kind it declares.** A fan-out that calls itself a grader handoff
  passes. The same ceiling as every membership claim here, declared rather than closed.
- **Line-level recall of the detector.** The file partition is clean and measured; the line set is a
  floor. A surface phrased outside the detector's vocabulary is invisible to it.
- **Whether independence was obtained.** Standing rule 6 and `practicum-case-study:652` both already
  say a record cannot show which context wrote it. Nothing here changes that, and a declared kind
  does not make it checkable.
- **The exact surface denominator.** Deliberately not fixed as a figure; a build adopting a rule for
  what counts as one surface derives it and states it where the code that produces it lives.
- **Whether `icd10-cpt`'s one-writer inversion is a defect or an unstated narrowing.** It is
  recorded as measured. Ruling 6 requires it to become one or the other, and which one is the
  build's finding to file.
