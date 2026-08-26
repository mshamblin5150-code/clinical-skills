# A glossary term is filed with the term it is defined against and a duplicate fails the suite rather than the hook

[#499](https://github.com/mshamblin5150-code/clinical-skills/issues/499) was filed over
`CONTEXT.md` defining **Declared limit** and **Underived count** twice on `main`, arrived at
through a byte-identical merge that neither parent produced and nothing in the suite noticed.

Grilled 2026-08-26. **Five decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `4f615cb`

- **93 term headings, 91 distinct, exactly two duplicated.** `Declared limit` at `:368`
  (`### Guidelines`) and `:394` (`### Checks`); `Underived count` at `:372` and `:398`. Both
  pairs byte-identical including their `_Avoid_` lines.
- **Eight cross-references between bolded terms, and two of them already cross sections** —
  `Prose mark` **[Checks]** points at `Glued run` **[Guidelines]** at `:391`, and
  `Underived count` **[Checks]** points at `Orphaned figure` **[Guidelines]** at `:399`.
  Neither dangles.
- **Exactly two modules read the file and both take the first occurrence** —
  `tools/test_glossary_vocabulary.py:43` (`text.index(heading)`) and
  `tools/test_ruling_cohort.py:146` (`self.text.index(term)`). Neither imports `Counter`.
- **One glossary in the tree.** No `CONTEXT-MAP.md`, and no other tracked `.md` carries more
  than two `**Term**:` headings.
- **Nothing outside `CONTEXT.md` cites either term by section.**
  [ADR 0028](0028-the-uspstf-interval-derivation-reaches-one-sentence-and-that-reach-is-ruled-permanent.md)
  cites `Declared limit` **by name**, which survives any filing decision; the other matches are
  `## Declared limits` ADR section headings, a different thing.
- **`tools/hooks/pre-commit` fires at `git commit`. `.github/workflows/checks.yml` runs the
  suite on `pull_request` — the merge result — and on `push` to `main`.**

## The ruling

### 1. The `### Guidelines` copies stay, and the reason the ticket gave is not the reason

The tie-breaker in the body, repeated verbatim by six tracker sweeps, is that
**Underived count** points at **Orphaned figure**, which stays under Guidelines either way, and
that *"whichever section loses a term gains a dangling cross-reference."*

**The file falsifies that.** Two of its eight cross-references already cross sections, one of
them belonging to the disputed copy itself, and none is dangling — a reference in `CONTEXT.md`
resolves by **term name within one file**, never by section. The cost the ticket used to choose
between the copies does not exist, and six sweeps re-derived the coordinates without ever
re-deriving the argument.

What decides instead is narrower and reusable: **Underived count** is defined *by contrast with*
**Orphaned figure** — *"that one is declared, this one is repaired."* A term is filed with the
term it is defined against, and section coherence loses to that.

**The cost is named rather than left to be found.** Three figure-discipline terms —
**Orphaned figure**, **Declared limit**, **Underived count** — stay filed under a section
otherwise about the guideline corpus. That is accepted, not unnoticed.

### 2. Moving the trio to its own section was refused

A new `### Figures` holding all three was the tidier answer and would have removed both pairs
without choosing between sections. It coins a section and edits a term this ticket did not open,
and section membership in this file is already loose enough — the two live cross-section
references above are the evidence — that it buys less than it looks like it buys.

### 3. Both kinds of duplicate fail, and the failure names its remedy

[ADR 0037](0037-a-contested-glossary-term-goes-to-the-higher-adr-number.md) split duplicates into
two kinds and #499's *Done when* was written before it:

| | what it is | remedy |
| --- | --- | --- |
| **Redundant** | two byte-identical definitions | delete one; mechanical |
| **Contested** | two headings, two different definitions | ADR 0037 — the higher ADR number keeps the term, the losing concept is renamed. **A clinician decision.** |

**Both fail.** Tolerating the redundant kind would make the check pass on the defect it was filed
for, which is the state of `main` today. The distinction costs one comparison of the two bodies
and buys a failure that names its own remedy: a person hitting `redundant` deletes a line, and a
person hitting `contested` knows to stop and read ADR 0037 rather than picking a copy by feel —
which is exactly how decision 1 could have been taken wrongly by an unrelated branch.

### 4. The assertion is a test and not a hook, because the mechanism is a merge

**`tools/hooks/pre-commit` does not fire on an automatic merge commit at all.** Both recorded
instances of this defect — the pair on `main`, and the `Recommendation record` collision ADR 0037
ruled — arrived at a merge. CI runs the suite on the merge result and on a push to `main`, so a
plain `unittest` reaches that door obligatorily and a hook reaches it not at all. **A refuser
would guard the weaker door and spend the posture.**

[#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83) decision 1 set this repo's
bar for refusing a commit, and it is clinical consequence — *a fabricated citation in a threshold
sheet is a number a clinician may act on.* A duplicated glossary heading corrupts reading, not a
patient.

**An advisory hook line was refused outright.** This repo's own record is that an advisory check
which crashed was indistinguishable from one that passed, and it cost a real finding; an advisory
line on a file edited three times in nine days is one more thing to read past.

**Home: a new `tools/test_glossary_terms.py`.** `test_glossary_vocabulary.py` declares
`CODE_VOCABULARIES` as its ceiling in as many words; a whole-file structural walk under that
docstring would make the ceiling untrue. The new module's subject is one sentence — every term in
`CONTEXT.md` is defined exactly once — and it is where the prose-collision limit below is declared.

**Residue, declared rather than closed.** A test fires when somebody runs the suite. Between a
hand insertion and the next run, nothing watches. That is true of every prose bind in this tree
and it is the price of taking the merge door over the commit door.

### 5. The two first-occurrence readers are not repaired, and the dependency is one sentence in each

Four sweeps flagged `text.index` as the latent hole, and ADR 0035's build made it a live editing
path by touching `Sweep state`, one of only two entries in `CODE_VOCABULARIES`. **Once no term
can be duplicated, `text.index` stops being a hazard and becomes the ordinary way to find a
unique thing.** So the question was never *repair the readers* — it was how strongly to write
down that their correctness now rests on another module. One sentence in each docstring naming
`tools/test_glossary_terms.py`.

Three stronger answers were refused:

- **Making each reader refuse a second occurrence.** *A second mechanism that cannot fail is not
  a belt and braces; it is a line that costs a test* — the `docx_write` mutation pair, where a
  redundant guard made the cleanup limb unreachable from the one test aimed at it.
- **A declared-limit object naming the two call sites, held by an AST walk.** It looks like the
  disciplined answer and points the wrong way: it fires when a reader **gains** duplicate
  handling, which is harmless, and it does not fire on the failure that matters — somebody
  weakening or deleting `test_glossary_terms.py`, after which both readers go silently wrong. A
  mechanism aimed at the harmless direction is the thing the bullet above is refused for.
- **Extracting a shared reader.** The two do different jobs — one pulls backticked values out of
  a term body, the other looks 600 characters ahead for an `_Avoid_` line — so
  [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s rule holds: *a
  helper two modules happen to have written the same way is not one that exists to be depended
  on.*

## What this does not reach

**A term colliding with a word already live in the file's prose.** #496's third kind:
**Invoked source** carries `_Avoid_: figure` because `figure` already means *a published number*
here. That is a heading against prose, not a heading against a heading, and no duplicate-heading
check sees it. Declared, not closed.

**Whether a definition is right.** One heading and one body is all this reaches; nothing compares
a body to the ADR that contributed it. ADR 0037 recorded that its own entry was out of step with
the record that wrote it *from the moment it was written*, and that stays true.

**Its own deletion.** Weaken or remove `test_glossary_terms.py` and both readers become silently
wrong again, with no walk anywhere that sees it. Decision 5 names this as the failure the refused
mechanisms did not reach; nothing here reaches it either.

**Any glossary but `CONTEXT.md`**, because there is not one.

## What this closes

ADR 0037's *What this does not reach* opens **Nothing detects a collision** and hands the check
to #499. Decision 3 is that check, and it applies ADR 0037's resolution rather than only
reporting a failure. On `main` today a contested term's winner is decided by **file position**,
which agreed with ADR 0037 by luck; after the build there is no winner, because there is no
second copy.
