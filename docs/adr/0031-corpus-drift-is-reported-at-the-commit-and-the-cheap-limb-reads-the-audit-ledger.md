# Corpus drift is reported at the commit and the cheap limb reads the audit ledger

[#439](https://github.com/mshamblin5150-code/clinical-skills/issues/439) was filed because a
guideline PDF can be dropped into `C:/codeing/guidelines-src` and every artifact derived from that
corpus keeps answering, cleanly, about a corpus one document smaller than the one on disk. That is
*partial coverage reading as complete* at the level of the corpus rather than of a parser, and it is
[#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s name-index defect one
level up.

The charge is right about the consequence and wrong about the cause. Grilled 2026-08-25. **Five
decisions, ruled by the clinician on that date.** Nothing is built here; this is the record the
build reads.

## The measurement came before the ruling and falsified two of the ticket's premises

**The detector the ticket quotes is not the detector that would catch this.** *What exists* cites
`tools/guidelines_catalog.py:544` and `:546`, the two filename messages. Those run inside `check`,
whose `docs` argument comes from `read_corpus_handoff` over the **extracted text** root — a build
artifact. They compare the catalog against the last extraction, so a PDF that lands and is never
extracted is invisible to them.

**The detector that does reach the live PDF root already runs by default.**
`check_audit_digests` compares `reference/guidelines-catalog-audit.md` against a scan of
`--pdf-src`, whose default is `DEFAULT_PDF_SRC = Path("C:/codeing/guidelines-src")`, and reports
three directions rather than two: missing from the corpus, present in the corpus without an audit
row, and same filename with a different SHA-256. `python tools/guidelines_catalog.py` with **no
arguments** printed `179 row(s)`, `verified 179 document digest(s)`, `ok` on 2026-08-25.

**So the gap is not a missing detector. Nothing calls the one that exists.**

**And the hook was ruled out on a premise that is false where it matters.** The ticket says the
pre-commit hook cannot see the corpus *"for the same reason on a different machine."* That is true
of CI and false of the machine every commit is made from: `C:/codeing/guidelines-src` is an absolute
path outside every checkout, so it is reachable from the main clone **and from every worktree** —
the default-argument run above was made from a worktree.

## The four dated figures the ruling rests on

Taken 2026-08-25 on the maintainer's machine, against the live corpus. **They are dated evidence and
not live figures**: the corpus is out of repo, so nothing committed re-derives any of them and the
next refresh moves all four.

| | |
| --- | ---: |
| corpus | 179 PDFs, 410,197,235 bytes |
| walk every filename and size | **0.032 s** |
| SHA-256 every byte | **5.975 s** |
| `python tools/guidelines_catalog.py`, no arguments, end to end | **4.8 s** |

The two-order-of-magnitude gap between the first and second rows is what makes every ruling below
possible. Listing the corpus is a directory operation; reading it is not.

## Ruling 1 — the venue is the pre-commit hook, advisory, on the cheap limb

Every ordinary commit runs a filename-and-size walk of the corpus and compares it to the committed
ledger. It prints nothing when they agree, prints what arrived or left when they do not, and names
`python tools/guidelines_catalog.py` as the remedy. **It never refuses**, on the ticket's own
ground: a PDF arriving is not a defect.

`skills_mirror.py` and `spelling_scan.py` are the shape — run, print to stderr, `|| true`. This is
[#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s arrangement whole: print
the shortfall, name the remedy, refuse nothing.

**It runs unconditionally rather than on a staged-path trigger.** The two refusing guideline checks
fire only when their own artifact is staged, which is what keeps them from being the checks people
learn to bypass. Corpus drift has no staged artifact by construction — the whole defect is that the
corpus moved and the tree did not — so a trigger keyed on staged paths would fire on exactly the
commits where nothing changed. 32 ms is affordable unconditionally; `phi_scan` already runs on the
same terms.

### Rejected: run the real command in the hook

`python tools/guidelines_catalog.py` catches strictly more — including a same-size rewrite — and
costs 4.8 s on every commit. `CLAUDE.md` states the counter-argument in its own words about the
threshold gate: what keeps a refusing check from being `--no-verify`'d is that ordinary commits pay
nothing. Two orders of magnitude of cost for one residue case is the wrong trade at a venue that
fires many times a day.

### Rejected: let `guidelines_build.py` report it instead

`extraction_identity` already walks every PDF recording a full-file SHA-256 and byte size, and
`artifact.json` retains that `source_files` list per registered build — so the delta against the
previous build is computable with **zero new reads**. It is the richer report and it is not the
answer, because it only speaks when the maintainer has already decided to rebuild. #439's first
*Done when* requires a route that does not need the person to already suspect it. Worth adding
afterwards as the detailed report for whoever *is* rebuilding; it does not close the ticket alone.

### Rejected: declare the limit and build nothing

`declare the coverage` is the standing preference where an instrument reports clean about a tree it
cannot fully see. It does not fit here: the declaration would be read by nobody at the moment the
PDF lands, and #275 already narrowed the preference to *declare the limit you are keeping and fix
the thing you actually named*.

## Ruling 2 — the cheap limb reads `reference/guidelines-catalog-audit.md`, which gains a `bytes` column

The corpus is exactly one level deep — `<society>/<file>.pdf`, nine societies, **zero duplicate
basenames** — so `(society, filename)` is a clean key, and it is the key `check_audit_digests`
already uses.

The audit ledger gains one column. It is written by the same scan that already writes each
`sha256`, which is opening every file regardless, so it carries no maintenance the tree is not
already carrying.

**Why the ledger rather than the catalog.** The ledger's own opening states that `sha256` binds each
reading to the exact PDF bytes. A byte count is the cheap half of that same claim, so it belongs in
the file whose subject is file identity rather than in the catalog, whose subject is metadata about
documents. Putting it there also means the 32 ms limb and the 5.975 s limb read one table and key on
one tuple, so they cannot come to disagree about what the corpus is — which is this repo's most
frequently recorded failure.

**Why a size and not names alone.** The realistic silent case is a society reissuing a guideline for
a new year under an unchanged filename; GOLD, GINA and ADA all ship annually. A names-only check is
blind to it. A re-issued PDF is essentially never the same byte count.

### Rejected: a new committed digest artifact

#439 decision 2 asks whether a committed count and hash of the corpus filename set is worth
building. It is not, because **the tree already holds two** committed 179-row ledgers, and
`check_audit` pins them to each other in both directions with no corpus needed — a ledger row with
no catalog row fails at `tools/guidelines_catalog.py:663`, a catalog row with no ledger row at
`:738`. A third artifact would be a third answer to one question. **Decision 2 is closed rather
than deferred.**

### The residue, declared

Same filename, same byte count, different bytes. Only the full hash reaches it, and that stays a
by-hand run. The hook line must say so, so that a silent hook is not read as *the corpus is
unchanged*.

## Ruling 3 — corpus drift and topic coverage stay two mechanisms with one visible sentence

The chain is **179 PDFs → 179 catalog rows → 169 distinct `topic` cells → the coverage registry**.
`threshold_coverage.py` derives its topics from `reference/guidelines-catalog.md` and grades them
against `reference/thresholds/coverage.md`; it reads two committed files and a directory and
**never touches the corpus**, which is exactly why it is allowed to be a refusing hook check.

So a PDF that lands and never gets a catalog row breaks the chain at link one and every number
downstream stays clean and wrong — which is #429's *Done when* asking for a count that is
*re-derivable and wrong at the same time*.

The repair is one printed line and no new reads: the report states its denominator's basis rather
than a bare `topics 169`. That is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
ruling applied here — state the population beside the clean number, so a reader who learns to read
the qualifier reads a disagreement with what the hook just said as the signal.

### Rejected: make `threshold_coverage.py` the single host

Joining the two inside that command means giving a **refusing** check a corpus dependency. It would
then either lose the corpus-free property that makes refusal safe, or carry a two-tier degrade
inside a refuser — a check that sometimes cannot check, at the venue where that is most expensive.

## Ruling 4 — silence must mean checked, so an absent corpus prints

Where the corpus is absent the hook prints one line saying it did not check. It prints on **zero**
commits made on the maintainer's machine, because the corpus is reachable from every worktree there;
it prints wherever the check is genuinely dead.

**The argument is that the alternative rebuilds this ticket's defect inside its own fix.** If
silence means both *the corpus matches the ledger* and *there was no corpus to look at*, a clean
commit on a fresh clone reads as a checked corpus. Silence has to mean **checked and agreed**, and
nothing else.

This is not the warning-on-every-clean-commit that #141 declined. That one would have fired when
everything was fine. This one fires only when the check is dead.

## Ruling 5 — the absent-corpus line names the remedy, and the remedy is what the checkout holds

The line states what the tree expects and how to verify a replacement, with every figure derived at
run time from the catalog rather than typed:

```
guideline corpus: NOT CHECKED -- nothing at C:/codeing/guidelines-src
  the tree expects 179 documents: USPSTF 90, IDSA 41, AHA ACC 23, KDIGO 18,
  ACIP 3, ADA 1, CDC 1, GINA 1, GOLD 1
  download them from those societies; reference/guidelines-catalog-audit.md
  lists every filename with a SHA-256 to check each download against
```

`guidelines_catalog.parse_catalog` returned `179 rows, 0 problems` against the committed catalog on
2026-08-25, and the society breakdown above is its output. **Nothing in the line is a literal**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

**No committed file records where any document came from.** The catalog carries three URLs and none
of them is a document source; the ledger carries none. So the checkout holds a complete shopping
list and no links, and the SHA-256 beside each filename is what makes an unattended re-download
checkable in a way a bare URL would not be.

### Rejected here and filed instead: a per-document source URL

It is a useful artifact and it is not this ticket. It is 179 lookups, it introduces a class of
committed fact nothing in the tree can re-derive or verify, and it needs its own decision about a
URL that stops resolving. It splits unevenly — 90 of the 179 are USPSTF, federal work already
tabulated in `reference/guidelines-uspstf.md`, so the cheap half and the expensive half should be
priced apart rather than as 179.

## The venue trap the build must not repeat

#141's ruled shortfall line went into `phi_scan.layer_report`, and the hook runs that scanner bare —
so a clinician-ruled feature printed on **no commit at all** while the prose said it printed on every
one, and every test drove the reporting function directly and stayed green.

**Test the command the hook runs, not the function that formats the line.** A declaration has a
venue, and getting it wrong is invisible to the suite.
