# A producer file's identity is its git-normalized bytes, and the corpus binary limb keeps the raw hash

[#643](https://github.com/mshamblin5150-code/clinical-skills/issues/643) recorded that
`python tools/threshold_sheet.py --all --quiet` exits `2` on an untrusted recommendation
record, refusing every commit that stages a threshold sheet, and asked whether
[ADR 0057](0057-the-corpus-sweep-is-comprehensive-and-every-ruling-it-needs-is-already-ruled.md)
ruling 7 — which made the sibling extraction identity **warn** — should generalize.

Grilling it on 2026-08-29 found the ticket's framing wrong. The refusal is not a stale
build artifact and not ADR 0057's argument arriving one artifact over. It is a defect in
the identity function: `artifact_provenance.producer_file_identity` hashes raw
working-tree bytes, and under `core.autocrlf=true` those bytes are **not a function of the
commit**. Two clean checkouts of one commit legitimately hold different bytes, so a record
built in one is untrusted in the other, permanently, with no rebuild that satisfies both.

The clinician ruled on 2026-08-29.

1. **A producer file's identity is its git-normalized bytes.** `producer_file_identity`
   and `_content_inputs` collapse `\r\n` to `\n` before digesting. The stamp stops meaning
   *these exact bytes* and means *these bytes up to the normalization git itself applies*,
   which is the only thing git guarantees is stable across checkouts.
2. **The corpus binary limb keeps the raw hash, declared rather than left implied.** A PDF
   may legitimately contain `\r\n`, so normalizing a corpus document's identity would let
   two documents collide on one key — worse than the defect being repaired. The
   normalization is keyed on *repo-relative text producer files* and nothing else.
3. **One identity rule, used by both hashers.** `tools/guidelines_build.py`'s own
   `_sha256` carries the same instability into the content-addressed cache key, so
   `_code_inputs` and the `curated_table` row consume the shared helper. Leaving the build
   cache raw would put two answers to *what is this file's identity* in one tree, which is
   the condition that produced this ticket.
4. **[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md)
   ruling 5 is reaffirmed, not reopened.** An untrusted recommendation record stays a
   did-not-scan at `2`. #643's premise that *"nothing I found states which of the two this
   is"* is false: ruling 5 states it in as many words, and that ADR's own Consequences
   section predicts this commit-time refusal by name.
5. **The asymmetry with ADR 0057 ruling 7 is deliberate.** Extraction identity is a
   **proxy** — that record's own reason is *"the refusal stays where the evidence is: tier
   1 and tier 2 already fail a snippet that stops resolving"* — so the defect it points at
   is independently graded. An untrusted recommendation record has no second limb:
   COVERAGE's whole substance is the `rec_id` denominator the record supplies, and no
   other gate reads it. Downgraded to a warning, a stale denominator prints
   `0 refusing, 0 warning`, byte for byte what a clean sheet prints.
6. **A producer-code edit means a recs rebuild before the next sheet commit, and it is
   written down.** The hook comment and
   [`reference/thresholds/README.md`](../../reference/thresholds/README.md) say so. The
   hook is not narrowed and does not disagree with the command.
7. **The untrusted case gets its own explanation and names its ordinary remedy.** It stops
   falling into the missing-record paragraph, and names the recommendation sweep and the
   `--recs-alias` root it publishes to — never a corpus path this module cannot know, and
   never as a guarantee, because ADR 0030 already declares that a record whose PDF has
   left the corpus cannot be rebuilt.

## What was measured

Every figure was re-derived on `a92a271` with the freshness gate reporting `FRESH`, before
the ruling.

**The reported symptom reproduces, and its cause is not the one the ticket names.** The
three refusing records resolve from the **sweep alias**, not from the exact-name recs root
— so the rebuild already performed into `C:/codeing/guidelines-index` could never have
fixed it, and that shadowing is correct behavior under ADR 0030 ruling 7 and the alias
precedence `CLAUDE.md` states, rather than a second defect. All three are `curated-table`;
the `ruled-table` and `text-marker` records pass. The only floor file the others lack is
`reference/guidelines-uspstf.md`.

**One committed blob, three byte sequences, every checkout clean.** At blob `41cd9c1d`:

| | sha256 | line breaks |
| --- | --- | --- |
| the record's stamp, and the main checkout | `427a0b3c…` | 322 CRLF + 3 bare LF |
| eight worktrees at that blob | `d259ea57…` | 325 CRLF |
| the committed blob | `fbaa27f1…` | 325 LF |

The files are byte-identical after `\r\n` → `\n`. `git status` reports clean in both
checkouts, because both round-trip to the same blob. Across all 35 registered checkouts,
nine hold that blob and the main checkout is the lone outlier — and it is the checkout
every record is built from and every commit is made from.

**It is systemic rather than a one-off.** `tools/uspstf_table.py:1041` writes that file
with `newline="\n"`. So the moment [#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434)
regenerates it, the main checkout holds a pure-LF copy while every fresh worktree checkout
holds pure CRLF, and every `curated-table` record is untrusted in whichever half of the
machine did not build it.

**Ruling 1 clears the symptom, measured rather than reasoned.** Re-stamping the alias
record under a normalizing digest and re-running `check_producer` returns no reasons at
all — the commit-mismatch limb is suppressed with it, because `inputs_match is True`
already gates that limb.

**The explanation that prints names two failure modes that did not occur.**
`gate_coverage` appends its *"a source with no recommendation record… a `--recs` path that
does not resolve"* paragraph whenever a blocking ungraded source exists, untrusted
included. The record is present, it resolved, and no `--recs` was given.

## Why ADR 0030's cross-worktree premise does not hold

That record chose an `inputs` stamp over a commit-only one on this ground:

> The same mechanism is what makes the change survivable across worktrees.
> `C:/codeing/guidelines-index` is written by eleven live worktrees. A commit-only stamp
> would fail every cross-worktree read; an `inputs` stamp passes wherever the producer's
> bytes agree.

The sentence is literally true. The premise it rests on — that a clean checkout's producer
bytes agree across worktrees — is false, one checkout in nine, and the outlier is the one
that matters. [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
permits correcting a ratified record's facts in place, and that is a fact rather than a
ruling; ADR 0030 carries a dated note pointing here. **Its choice survives the
correction** — a commit-only stamp would still fail every cross-worktree read, and the
repair is to key the inputs on something stable rather than to abandon them.

## Considered options

**Hash the git blob id instead of the file.** Rejected. It is exactly git's own notion of
identity and would agree across checkouts, but it cannot see an uncommitted edit to a
producer file — a case `check_producer`'s working-tree limb currently catches — and it
costs a subprocess per floor file on a path the pre-commit hook runs.

**Repair the outlier and leave the identity alone.** Rejected. `git checkout --` in the
main checkout plus a rebuild fixes today only; `uspstf_table.py` reintroduces it by
construction on the next regeneration, and nothing fails when it does. It is the shape
`CLAUDE.md` keeps recording: a repair scoped to the one file the finding arrived in,
leaving the generator that produced it untouched.

**Normalize the trust floors and leave the build cache raw.** Rejected under ruling 3.

**Scope the normalization to the recs floor.** Rejected, and it is not cheap: `_content_inputs`
is one function verifying all three floors, so recs-only means branching on the floor key
— a second rule about what a file's identity is, which is [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)
and [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s subject.

**Make the hook treat provenance-untrust as non-refusing while the command refuses.**
Rejected. It is ADR 0057's `--no-verify` avoidance, and it makes the command and the hook
disagree about what an untrusted record means — the condition ruling 3 exists to remove,
reintroduced one file over. CI cannot demonstrate the difference either, because a runner
has no recommendation records and takes the never-built branch. If the rebuild cost ever
becomes prohibitive, the honest move is to reopen ADR 0030 ruling 5 in the open rather
than to route around it in a hook.

**Narrow the hook trigger to sheets whose own sources are affected.** Rejected. `--all` is
deliberate; `CLAUDE.md` records that grading one sheet in isolation would miss a
cross-sheet conflict.

**Accept either the raw or the normalized digest during a transition.** Rejected. It is
the two-answers condition a third time, and the one-time rebuild it would avoid is the
same event as ruling 3's one-time cache invalidation rather than an additional cost.

## What this does not reach

Declared so the builder does not have to discover it.

- **The normalization is not a general text-identity rule.** It collapses `\r\n` only. A
  file differing by trailing whitespace, a final newline, or encoding is a different file
  to this check, as it is to git.
- **A binary producer file would be mis-keyed.** Ruling 2 excludes the corpus limb by
  path; a future floor naming a repo-relative binary would be normalized wrongly and
  nothing here detects that. The exclusion is a declared boundary, not an inferred one.
- **A stamped, trusted record can still be wrong about the guideline.** ADR 0030's limit,
  unchanged: ownership answers *which code and which inputs built this*, never whether the
  extraction read the page correctly.
- **This says nothing about whether the main checkout's mixed line endings should be
  repaired.** Under ruling 1 they stop mattering to trust; they remain a working-tree
  oddity nothing grades.

## Consequences

**Every existing recommendation record and cache entry is invalidated once.** They hold
raw digests, which no longer compare equal to a normalized one. That is a single recs
sweep, and it is the same event as the cache-key change rather than a second cost.

**The pins are three, and two of them need a discriminating case the obvious test does not
supply.** A test that writes the producer file once passes identically with and without
normalization; the case that separates them is a record stamped against a CRLF file,
validated after that file is rewritten as LF with no other change — and the inverse, that a
one-character content change still refuses. The venue for the third is
`main(["--all", "--quiet", …])` with `threshold_sheet.SHEET_ROOT` pointed at a temp
directory, because the hook's path — the sheet glob, the `worst = max(...)` accumulation,
alias resolution — is exercised by no untrusted test today; the existing pin calls
`grade(...)`. All three are driven red by reverting the change before they are believed,
and ruling 2's exclusion takes a positive control proving the binary path still hashes raw,
because an exclusion that stops being exercised looks exactly like one that still works.
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s rule — write the
discriminating cases before the fix — and `voice_corpus.py`'s UUID-dating prohibition,
which survived its first mutation because the fixture failed by accident rather than by
refusal.

**`artifact_provenance.TRUST_FLOOR["recs"]` is dead and is not repaired here.** Nothing
reads it, in `tools/` or in the tests; ADR 0030 ruling 2 moved that key to
`guidelines_recs.RECORD_TRUST_FLOOR` and the old copy stayed behind. Two copies of one
rule where a prose edit to either fails nothing. Filed separately rather than folded in,
so the deletion is reviewed on its own terms.
