# A legal reference entry keys on both its name and its section, and a narrative citation is read against the reference set

[#497](https://github.com/mshamblin5150-code/clinical-skills/issues/497) reports that an APA-correct federal-regulation reference entry cannot resolve against its own in-text citation, so APA form and a resolving citation are mutually exclusive. Grilled on 2026-08-26. Every measurement below was taken at `4fd8070`, `main` advanced under the branch mid-session, and every one was re-derived unchanged at `19e182d` -- where `tools/discussion_artifact.py`, `tools/discussion_reply_scan.py`, `tools/discussion_post_scan.py` and `tools/test_discussion_post_scan.py` are each byte-identical to `origin/main`, and where the two commits `main` gained touched `CONTEXT.md` and ADR 0038 alone. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement moved the root of the tree above the ticket's own options

The ticket offers three directions, all of which take the in-text citation to be the C.F.R. section — `42 C.F.R. § 414.56` — and ask how to make an APA entry resolve against it.

**APA 7 does not cite a federal regulation by its section.** The in-text form is the name of the regulation and the year: parenthetical `(Protection of Human Subjects, 2009)`, narrative `Protection of Human Subjects (2009)`. This is guide consensus across seven independent university library guides ([Widener](https://widener.libguides.com/APA_7th/legalworks), [Bradley](https://bradley.libguides.com/apa7th/legal), [CCCS](https://cccs.libguides.com/c.php?g=1465210&p=10899490), [NMU](https://nmu.libguides.com/c.php?g=1434311&p=10647807)) and **not a read of APA's own page** — `apastyle.apa.org` sits behind Imperva and returned an incident ID rather than a document on 2026-08-26. That caveat travels with the claim, on `skills/practicum-case-study/reference/apa7.md`'s terms.

So the ticket's framing is one level too low. Driven in process, the reference entry keys as:

| entry | keys |
| --- | --- |
| `Payment for nurse practitioners' and clinical nurse specialists' services, 42 C.F.R. § 414.56 (2025).` | `('paymentfor…services42cfr41456', '2025')` |
| `42 C.F.R. § 414.56 (2025). Payment for …` | `('42cfr41456', '2025')`, `('42cfr41456', '')` |

and the body reads as:

| in-text form | citation read | year reaches the numeric walk |
| --- | --- | --- |
| `Under 42 C.F.R. § 414.56 (2025), …` | yes, year captured | no |
| `… (42 C.F.R. § 414.56, 2025).` | yes, span ends at char 34 | **`2025`** |
| `… (Payment for … services, 2025).` | yes | no |
| `Payment for … services (2025) sets …` | **none** | **`2025`** |

**Row 3 is the finding the ticket does not contain.** An APA-correct entry and an APA-correct parenthetical citation still fail to resolve, because `reference_keys` swallows `, 42 C.F.R. § 414.56` into the author key. That is not a legal-citation-detection problem at all, and no option in the ticket reaches it.

**Row 4 is worse.** `NARRATIVE_CITATION` builds on `AUTHOR_PHRASE`, every token of which must open with an uppercase letter or be `of`/`for`/`the`/`and`/`&`. A regulation title is sentence case, so `nurse`, `practitioners'`, `clinical`, `specialists'` and `services` all fail and no citation is emitted. The form APA prescribes, in its narrative spelling, is invisible to both graders.

### Two corrections to the ticket's own account

**Limb 2's stated mechanism is false and three sweeps have said so.** The body reads *"the pattern does not match at all"*. `LEGAL_CITATION`'s year group is optional at `tools/discussion_artifact.py:42`, so the parenthetical form **matches and truncates** — the span ends before `, 2025` because `PAREN_PAIR` requires its author to open with an uppercase character (`tools/discussion_artifact.py:25`) and `42 C.F.R. …` opens with a digit, so the general parenthetical path never fires and only the short legal match survives. A builder reading the body edits a working pattern.

**Limb 2 is live in both graders, not one.** The ticket reports it as a reply-grader symptom. `discussion_post_scan.STATUTE` (`:87`) strips the section and not the trailing year, so `_numeric_values("Reimbursement is 85% (42 C.F.R. § 414.56, 2025).")` returns `('85%', '2025')` while the narrative form returns `('85%',)`.

### The tracked surface is one fixture, and it teaches the wrong shape

`git grep -l` for the dotted `C.F.R.` form over tracked files returns exactly one module — `tools/test_discussion_post_scan.py`, six occurrences — plus this record, which carries the form in order to describe it. The looser `CFR` spelling adds two files and **both are false hits**: `reference/thresholds/diabetes.md` writes `CFRD` for cystic fibrosis-related diabetes, and `tools/test_fixture_catalog.py:82` is `frozenset("ACFR")`, a character set. A re-derivation that reaches for the short spelling will find a surface three times the real one. That module's ledger entry is `REFERENCE: 42 C.F.R. § 482.13 (2024).` — **a section with no regulation name**, which is not an APA legal reference — and which never appears in that fixture's own `## References` block.

### The two graders resolve against different sources

`discussion_post_scan` keys the claim ledger's `REFERENCE:` fields (`:207`); its draft's own `References` block is split at `:301` and used only to count against the bar minimum (`:327`, `:388`). `discussion_reply_scan` keys the reply's own `References` list (`:187`). Both call one `reference_keys`.

## Ruling 1 — APA's name-and-year form is this repo's canonical legal citation

A run writes `(Payment for nurse practitioners' and clinical nurse specialists' services, 2025)`, not `(42 C.F.R. § 414.56, 2025)`.

The declined branch is the Bluebook-flavored one the live run used. Its cost is that the *entry* can be made APA-correct while the *citation* stays non-APA, so the same faculty grader is still handed a form defect — moved from the reference list into the body rather than removed. This is the only branch on which both halves are APA-correct at once.

## Ruling 2 — an APA legal entry yields its name key **and** its section key

`reference_keys` searches for a legal citation inside the author text rather than `fullmatch`ing it, and emits both `('paymentfor…services', '2025')` and `('42cfr41456', '2025')` / `('42cfr41456', '')`. Both in-text forms resolve; nothing in flight breaks.

The stricter branch — name alone, so a section-form citation becomes `unresolved-citation` — is declined on the ticket's own prohibition: *"this is a formatting mismatch rather than a missing source."* The resolution row exists to catch a citation whose source is in no reference list, and under this ruling the section **is** in the reference list. It is the posture `citation_author_keys` already takes on the citation side, where one phrase deliberately yields full, alias and signal-word-stripped keys.

**The in-text form is deliberately not policed, and the asymmetry with ruling 5 is the reason.** There is no evidence faculty mark the in-text spelling; there is direct evidence they mark the entry shape.

**This does not widen `author_key`**, which #497 forbids. The widening is in what a legal *entry* yields, not in how any string is keyed.

## Ruling 3 — a narrative citation is read against the reference set, by a reverse key walk

`read_citations` becomes reference-aware. For each `(YYYY)` in the body not already covered by a citation span, it walks left over the preceding words and tests each candidate span through `author_key` against the key set; longest match wins, no match leaves the year alone. On `Payment for nurse practitioners' and clinical nurse specialists' services (2025) sets 85%` the walk tries `services`, then `specialists' services`, up to the full title, finds the key and emits one citation spanning title through year.

**It is safe by construction in the one direction that matters:** it can only ever emit a citation that resolves, because the key came out of the reference source.

### Rejected: widen `AUTHOR_PHRASE`

One line, and it lets `NARRATIVE_CITATION` swallow arbitrary sentence tail before any `(YYYY)` — `the rule was finalized (2025)` becomes a citation authored by `the rule was finalized`, manufacturing `unresolved-citation` on correct prose. False alarms on a correct artifact are the direction this repo has ruled against repeatedly.

### Rejected: declare it and require the parenthetical spelling

Cheapest, no code, and it was the recommendation until its failure mode was priced. Ruling 1 makes the name form canonical, so this ships a canonical form whose only symptom is `untraced-number: 2025` and **no** `unresolved-citation` — a finding pointing at a defect the run does not have. Silent and misattributed is the shape this repo keeps recording as its most expensive.

### Rejected: literal phrase search

Collecting each entry's author text and searching the body for `<phrase> (YYYY)` fails on what the phrase *is*: the ruled entry's author text includes `, 42 C.F.R. § 414.56`, which never appears that way in narrative prose. Deriving the title alone outside `reference_keys` is a second half-copy of that rule, and matching it raw means a curly apostrophe in the entry against a straight one in the body misses silently. The walk reuses `author_key`, so apostrophes, casing, `&`/`and` and a leading `The` are handled by the code that already handles them. And a literal search can emit a span that then fails to resolve, which is the failure this construction exists to foreclose.

## Ruling 4 — the walk sees every reference key, from the set the grader already resolves against

Not legal-only, and **one object rather than two**: `discussion_post_scan._citation_keys` passes the keys from `_claim_records(source.claims)`; `discussion_reply_scan.survey` passes the keys from `_reference_keys(reply)`.

Ruling 3's safety property holds **only** if the set the walk reads with and the set the grader resolves against are identical. A different or wider set reintroduces manufactured `unresolved-citation` findings through the plumbing. Scoping to legal entries alone buys nothing once the construction is safe and costs a classification rule that would then have to be right.

**Left untouched and pre-existing:** the post grader's draft `References` block is still not keyed for resolution, so a draft whose entry is worded differently from its ledger `REFERENCE:` field still will not resolve. That is true today and no ruling here alters it.

## Ruling 5 — a legal reference entry with no regulation name is a reported defect

The detection costs no new rule. After ruling 2, `LEGAL_CITATION.fullmatch(author_text)` succeeding means the author slot is **nothing but** the section, so the entry carries no regulation name; the search succeeding where `fullmatch` fails is the APA-correct shape. The existing `fullmatch` flips from success signal to defect signal.

The predicate is shared in `discussion_artifact`; each grader emits its own `Finding` — the reply grader over the reply's `References` list, the post grader over the ledger's `REFERENCE:` fields — which is the split `reference_keys` already uses.

This is where ruling 1 acquires a gate on the artifact faculty grade, and it is the one point in the tree with **direct evidence** the form is marked: #497 records an independent checker flagging exactly this entry shape as an APA defect. Ruling 2 declines to police the in-text form for the mirror-image reason — no such evidence exists for it.

**Its cost is a new refusal on work in flight.** The posted `NUR_5042` M2 reply carries the section-first entry, so a re-grade of that board fails on this row until the entry is rewritten. That failure is correct under ruling 1 and was accepted as such.

## Ruling 6 — the truncated span is closed by a parenthesized alternative, not anywhere

`LEGAL_CITATION` gains a distinct branch matching `\(\s*<legal>\s*,\s*YYYY\s*\)`, so the comma form is read as a year only inside parentheses. One reach into one pattern; both graders inherit it through `read_citations`.

### Rejected: consume `, YYYY` anywhere after the section

Same cost, and it swallows a genuine body number in unparenthesized prose — `Congress amended 42 C.F.R. § 414.56, 2025 being the first year of the new schedule` loses its `2025` from the numeric walk. A silent under-report is the worse of the two directions.

### Rejected: strip the trailing year in each grader's numeric walk

Fixes the visible symptom and nothing else. The citation's year stays `''` so it never enters the key, and it puts two copies of one rule in two modules.

## Ruling 7 — it splits into three pieces and the successor blocks the close

- **A** — ruling 2 and ruling 5 in `reference_keys`, plus the finding row on both graders.
- **B** — rulings 3 and 4, the reverse key walk. Depends on A: the walk resolves against the key set, and without A the name key does not exist for it to find.
- **C** — ruling 6, independent of both.

A and C land on #497. B is a successor ticket, and **#497 does not close until B lands.**

Shipping A+C alone closes both limbs the ticket names and leaves the canonical form of ruling 1 silently unread with its year misattributed — which is precisely the state rejected under ruling 3. B is the other half of ruling 1, not an enhancement.

**#497's *Done when* is replaced.** It asks for four combinations. The real matrix is **2 entry forms × 5 in-text forms** — section-narrative, section-parenthetical, section-bare, name-narrative, name-parenthetical — plus ruling 5's row on the nameless entry.

## What none of this reaches

**A legal citation's year is never checked against its entry's year.** An APA legal entry yields an empty-year key by design, and `tools/test_discussion_post_scan.py:333`'s `test_yearless_legal_citation_matches_a_dated_regulation_record` depends on it, because a bare `42 C.F.R. § 482.13` in prose has no year to offer. That key resolves regardless of year. Ruling 6 makes the parenthetical citation better-formed; it does not make the year enforceable, and no branch considered here can while the bare form must resolve.

**Whether the cited section says what the draft claims.** That is the refutation pass in `skills/discussion-post/SKILL.md`, which states it has no carve-out for legal primary sources. Nothing here reads a regulation.

**Whether APA's own page says what the guides say it says.** Recorded above rather than glossed.

**The post grader's draft `References` block.** Counted, not keyed. Named in ruling 4 as pre-existing and out of scope.

**Whether faculty mark the in-text spelling.** Ruling 2 declines to police it on the absence of evidence, not on evidence of absence.
