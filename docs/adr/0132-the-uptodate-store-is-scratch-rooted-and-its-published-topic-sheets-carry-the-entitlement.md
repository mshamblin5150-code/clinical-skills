# The uptodate store is scratch rooted and its published topic sheets carry the entitlement

Ruled by the clinician on 2026-09-05, in the grilling of
[#758](https://github.com/mshamblin5150-code/clinical-skills/issues/758). Freshness gate `FRESH` at
both checkpoints. Nothing is built here; this is the record the build reads.

**The subject is not #758's.** That ticket asks where four reference sheets live. This record
answers a question the clinician opened inside its grilling: a supplied evidence dump is consumed
once by one skill and then reachable by nothing, and he wants the material available across skills
and across courses — *"similar to how the guideline sheets work but they are not a guideline they
are generally from up to date."*

## Measured before ruling, at `b26ea2a`

**The state before this record.** One `evidence.txt` in thirteen run directories. Only
`practicum-case-study` has an evidence concept and only it mentions UpToDate. So this is a new
capability rather than a consolidation of an existing one.

**The filed dump.** 759,626 characters, 109,929 words, **18 topic bodies**, each carrying an
`Authors:` masthead, a `Literature review current through` line and a `This topic last updated`
line — 18 of 18 on all three. Roughly 6,107 words per topic; roughly 192,000 tokens to read whole.

**Its structure, which decided the distillation unit.** 15 of 18 topics carry a
`SUMMARY AND RECOMMENDATIONS` section, **8,154 words in total — 7% of the dump**, averaging 543
words and ranging 181 to 915. The 872 `(See …)` navigation crosslinks are **8,339 words**, larger
than every summary combined. No topic carries a reference list and no topic carries a URL.

**The corpus the clinician actually holds**, in OneDrive, named with `UpToDate` or `References`:
**18 dump files, 11,879,218 bytes, 2,481,564 words, 396 topic bodies.** Mastheads, currency lines
and last-updated lines each come to exactly 396, so nothing is partially captured. 340 of 396 carry
a summary section; **118 of 396 carry a real `uptodate.com` URL**; none carries a reference list.
Five distinct currency stamps — Dec 2025 (21), Jan 2026 (178), Feb 2026 (133), Jul 2026 (18),
Aug 2026 (46).

**The two dates do different jobs, and only one of them varies.** Every topic in a single dump
carries the *same* `Literature review current through` value, so that field dates the dump rather
than the topic. `This topic last updated` has 16 distinct values across the filed dump's 18 topics,
and
[apa7.md](../../skills/practicum-case-study/reference/apa7.md) §2 already rules it the APA year
element: *"the date element is the year of the topic's last update. Not the year it was read."*

**The gate this collides with.** `research_ledger.CITED_TOPIC_NOT_IN_EVIDENCE` joins every cited
UpToDate topic against the set the **current dump** carries and refuses anything outside it, exit 1.
Its ground is that the companion evidence is the required supplied-source set.

**The quoting posture that already exists.**
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223), re-ruled on
[#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429), rests every non-USPSTF
work on short attributed quotation tied to society, document, page and locator — explicitly not on
public-domain status. `hypertension.md` commits 298 distinct verbatim snippets, median 8 words,
across a 105-page source.

**Where a sheet may not go.** `threshold_coverage.py` globs every `*.md` under
`reference/thresholds/` and refuses any the registry does not name, and that registry's topic
population is derived from the guideline PDF catalog. A topic sheet there would be refused at the
pre-commit hook.

## Ruled 2026-09-05

### 1. The raw dump stays out of the repository and the distilled snippets go in

The clinician's words: *"we keep the core gitignored we can publish the snipits."* This is the
guideline corpus's arrangement — copyrighted source outside, derived facts committed — arriving at a
second source class, and it inherits #223's posture rather than opening it again.

### 2. The raw store is `scratch/`-rooted, not outside every checkout

One accounted top-level entry. The guideline corpus lives outside the tree because it is
copyrighted; a dump is copyrighted **and** faculty case material, and `scratch/` is the only
directory in this system with a commit-time refusal attached — `phi_scan`'s path layer turns away a
commit from it even under `git add -f`. `repo_root.scratch_root()` already resolves it from a
worktree, so every checkout reaches one store.

### 3. The published sheets are `reference/uptodate/`, keyed to the clinical topic

Publisher-named and a sibling of `reference/thresholds/`. A topic sheet is data about the literature,
which is what the whole of `reference/` already holds, and
[ADR 0131](0131-the-shared-sheet-directory-moves-whole-and-the-mirror-gains-a-non-skill-rule.md)
ruling 2 sends instruction the other way for the matching reason.

**Publisher-named rather than role-named**, so a second publisher becomes a sibling directory
rather than a migration, and two publishers on one topic are two files rather than a filename
collision. No `*.md` walk exists under `reference/` outside `thresholds/`, so a new subdirectory
collides with nothing.

**Keyed to the topic and never to the dump**, so a topic supplied twice is one sheet read twice, and
the second course costs less than the first. A per-dump **manifest** carries provenance.

### 4. The store is the entitlement and the sheets are citable, including without an account

A topic sheet may be cited by anyone holding the repository. The clinician's ground: the dump is the
entire article, so every element of a complete entry can be carried on the sheet.

**What the sheet records is the read that produced it** — its retrieval date and its currency line —
and a citer inherits those rather than asserting a fresh read. That is accurate about the version,
and it is what makes ruling 5's window the mechanism doing the real work.

**Volume is not what makes a citation legitimate.** Bibliographic completeness plus an honest
retrieval record is, and all 396 topics carry the fields for it. This was ruled against the
recommendation of the session, which argued for research-aid-only; the clinician's reason answered
the completeness objection and the ruling stands as his.

### 5. The recency window is UpToDate's own stated review date, two years, waived without an account

`Literature review current through` drives the re-read window because it is what dates the dump.
`This topic last updated` supplies the APA year and, beside the review date, gives *old by date but
current in force* mechanically: a topic last revised years ago that the publisher swept last month
is the publisher saying it stands.

**Two years, which is the clinician's existing preference made enforceable for this class only.**
`practicum-case-study` step 3 already states *within two years is the target*, and
`research_ledger.DECLARED_LIMITS` records `two-year-target-unenforced`. The graded window is already
per-artifact data in each signed bar's `RECENCY-WINDOW-YEARS`, so this needs no new mechanism.

**Waived where there is no UpToDate account**, falling back to the guidelines-style rule that a
source may look stale by date and be in force. `setup-clinical-skills` asks whether the clinician has
an account, and the answer lands in the profile.

**No cut point here was invented**, which is [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
standing objection satisfied: the expiry is measured against a date the publisher prints.

### 6. The sheet body is the source's own summary section, restated, with verbatim confined to numbers

The `SUMMARY AND RECOMMENDATIONS` section in this repository's prose — roughly 400 to 550 words —
with verbatim quotation only where a number, dose, criterion or cut point is the honesty mechanism.
The 56 of 396 topics carrying no summary section fall back to a whole-article compression.

**The selection judgment is the source's rather than ours**, which is why this beats compressing the
whole article: UpToDate marks its own actionable core, and it is 7% of the words.

**Claims joined to their primary sources is the target and is not buildable today** — no dump carries
a reference list. The skill asks for reference lists at dump time, and the join lands as they arrive.

### 7. The store ingests what is handed over, reports what is not, and mines nothing

A dump is a file the clinician deliberately supplies. It is indexed **and** distilled on receipt,
all of its topics. A file on disk that has not been handed over is **reported and never touched**.

**Mining was refused with a recorded failure behind it.** `voice_corpus.py`'s lesson is that a
matcher over heterogeneous material turns a partial read into a clean-looking whole, and the twelve
`scratch/` files carrying UpToDate markers already show mismatched marker counts. Worse, mining
would break ruling 4: a topic pasted into a conversation was never *supplied as faculty material*,
so filing it would manufacture a citation entitlement out of a chat.

**Reporting rather than silence is `name_index.py`'s arrangement** — state the shortfall, name the
remedy, write nothing.

### 8. A malformed topic sheet refuses a commit, on the staged-sheet condition

The sixth refuser, joining `phi_scan`, `scratch_census`, `threshold_sheet`, `threshold_coverage` and
`subject_ledger`. The ground is the one already written for the middle three: a fabricated citation
is clinical guidance a consumer may rely on. The conditional trigger means it costs nothing on a
commit touching no sheet, which is the property that keeps a refuser from being routed around.

What a grader can settle: required fields present, the year matching the topic's own last-updated
line, a parseable currency stamp, a retrieval date on or after the dump date, a `uptodate.com`-shaped
URL, and the verbatim share inside a declared cap. **Whether the restatement is faithful is a
reading and is declared as one.**

### 9. The first ticket carries the mechanism and exactly one real sheet

The mechanism is startable unattended. One real sheet — chosen from the three in the filed dump with
**no** summary section, because that is ruling 6's fallback path and the likeliest to be wrong —
meets the repository's standing requirement that a grader face real material before it is trusted.
`block_scan` and `threshold_sheet` both shipped parser defects no fixture caught.

The remaining 17 sheets are a follow-on, cheap once the shape is proven.

### 10. Locator resolution is authorized against the clinician's own signed-in session

His words: *"I give my explicit authorization to use my Chrome session and go to uptodate.com… It
just has to simply click through the authentication step."*

The builder opens topic pages in the clinician's already-signed-in Chrome, **clicks through a saved
authentication, never types a credential, never creates an account, and reads only.** 118 of 396
topics already carry a URL, so the outstanding work is roughly 278 lookups.

**A constructed slug was refused.** `RESOLVED` is defined in this repository as *the URL the agent
actually opened*, and a guessed locator that 404s in a graded reference list is the fabricated
citation every gate here exists to catch.

## What this record does not settle

**How the manifest is shaped**, beyond carrying which topics arrived, for which module, on what date.

**Whether the index is FTS5 over the store**, though `guidelines_index.py`'s arrangement is the
obvious reuse and costs no dependency.

**Whether the verbatim cap in ruling 8 is a word count, a share, or both**, and what its value is.

**Whether a second publisher is ever ingested.** Ruling 3 makes one cheap and predicts nothing.

**Whether the 378 topics outside the filed dump are ever handed over.** That stays the clinician's
choice per file, which is what keeps ruling 7 safe: handing over all 18 OneDrive files would mean
396 eagerly distilled sheets.
