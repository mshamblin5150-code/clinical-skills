# a floor is cited by api and symbol and coordinates are ratcheted to zero

Ruled by the clinician on 2026-09-06, in the grilling of
[#791](https://github.com/mshamblin5150-code/clinical-skills/issues/791). Freshness gate `FRESH` at
both checkpoints. Nothing is built here; this is the record the build reads.

[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) states the repository's Python floor and the
evidence for it. #791 was filed over one stale coordinate in that evidence, carried byte-identically
in `CLAUDE.md` and in ADR 0002 itself. The measurement taken before ruling found the coordinate was
the smallest of the defects, and that the reconciliation four tracker sweeps had published for the
ADR half rested on a false premise.

## Measured before ruling, at `9dccd9b`

**The coordinate was correct at ratification.** Commit `83b7f13`, 2026-08-16, wrote
`tools/guidelines_catalog.py:148` into both files, and at that commit line 148 of that module *is*
the `zip(COLUMNS, cells, strict=True)` call. It decayed through unrelated edits to the same module.
Comments 11, 12 and 13 on #791 each reconcile the ADR repair against
[ADR 0131](0131-the-shared-sheet-directory-moves-whole-and-the-mirror-gains-a-non-skill-rule.md)
ruling 6 by asserting the coordinate *"was never right at any commit"*. **That premise is false**,
and the reconciliation built on it does not hold.

**Every other figure in the published evidence is wrong, and the floor itself is right.**

| claim as tracked | re-derived |
| --- | --- |
| the `zip(strict=)` call, framed as *the* pin | **8** sites in non-test `tools/`, **12** including test modules |
| `-> ast.If \| None`, framed as the one evaluated annotation | coordinate correct; it is **1 of 13** evaluated PEP 604 annotations |
| *"the modules without the line are test modules"* | **false** — `tools/prose_bind.py` is not a test module and is imported by 21 test modules |
| *"one of the ten modules without the future import"* | **22**, of which `prose_bind.py` is the only non-test one |
| *"their annotations are never evaluated"* | **false** — `get_type_hints` re-evaluates stringified annotations |
| ADR 0002: the floor is *"set entirely by files no consumer imports"* | **false** — a declared consumer dependency carries a pin |
| the floor is 3.10 | **correct.** Nothing in `tools/` requires 3.11 or later |

**Nothing executable asserts the floor anywhere.** No `sys.version_info`, no `requires-python`, no
packaging file. CI pins the 3.14 ceiling only. The floor exists in prose in exactly two tracked
files plus `README.md`, and `README.md` acts on it: it tells macOS users to install Homebrew Python
because Apple ships 3.9.6, *below this repository's 3.10 floor*. **That instruction is correct and
the record it should rest on denies it.**

**The `path:NNN` class is not the wide class #791 assumed.** In tracked prose there are 268 such
citations. **266 are in `docs/adr/`.** The two outside it are the two this record repairs, both on
one line of `CLAUDE.md`, and **zero** appear in fenced blocks anywhere outside `docs/adr/`. The four
further drifted citations #791 cites live in tracker issue bodies, which no repository test reads,
and `tracker_branch_scope.NOT_REACHED` already declares that gap: *"citation coordinates need file
contents… this detector reads only tree membership."*

**Ceiling on the measurement.** Both walks read literal call shapes and literal annotation positions
by AST. A call assembled by indirection, or an annotation built at run time, is invisible to them,
and the version-gated feature list is a named vocabulary rather than the language. This is a floor
on the shapes in the tree, not proof that no other pin exists.

## Ruled 2026-09-06

### 1. The evidence is cited by API and symbol, and by no coordinate or count

Both copies name `zip(strict=)` as a runtime API no future import defuses, and name
`test_console_codec.main_guard` as a symbol. **Neither names a line number and neither states a
count** — not of call sites, not of annotations, not of modules carrying or lacking the future
import.

The count is decoration in both copies: one `zip(strict=)` call pins 3.10 exactly as hard as twelve
do, so the enumeration was never load-bearing and has been falsified three times in five days —
three, then four, then eight. A line number fails nothing when it rots, which is why it rotted for
three weeks with fourteen tracker comments re-deriving it.

**A draft of this ruling wrote *"one evaluated annotation"* into the replacement text.** There are
thirteen. That is the defect arriving inside its own repair, and it is recorded here because the
count is the thing the ruling removes.

### 2. The ratified record is corrected in place, with a dated line at the bottom

[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
rules this case and names the remedy — facts corrected in place, a dated line recording what they
said and why they changed, the deciding paragraph untouched. It **rejected** the leave-it-and-
annotate option by name, on a reader argument that applies here word for word: a reader opens the
file, reads the figure, copies it, and never scrolls to the footnote.

**ADR 0131 ruling 6 does not override it.** Its *"the mentions in ratified ADRs stay"* governs the
paths that record's own ruling 1 was deliberately moving — a reader of that record has the repoint
in front of them — and ADR 0131 corrected itself in place, inline, hours after ratification. The
line that separates the two cases is that **a pointer is not a decision**. ADR 0002's deciding
paragraph is the advisory `windows-latest` and 3.14 ruling, and nothing here touches it.

**This does not license editing the other 266.** Applying the same argument across roughly 45
ratified records is a mass rewrite of the decision log and is not ruled here.

### 3. The committed check asserts the evidence exists, never how much of it there is

A test fails when no non-test module under `tools/` calls `zip(strict=)`, and when the evaluated
PEP 604 annotation the prose names stops being evaluated. It states no count, so it cannot itself go
stale, and it is exactly co-extensive with what ruling 1 leaves the prose claiming.

**The direction that costs something is the population reaching zero**, not growing. Eight sites is
not permanent — four arrived in one commit — and a refactor could remove the last of them, leaving
two tracked files asserting a 3.10 floor with nothing behind it and nothing red.

### 4. The wider floor derivation is filed rather than folded in

A walk that derives the minimum interpreter from a declared vocabulary of version-gated features,
and reports it twice — over the whole tree and over the consumer roots `AGENTS.md` declares — is a
separate ticket. It grades what the floor **is** rather than whether the stated evidence stands, and
#791's own scope forbids touching the floor.

Its ceiling is `spelling_scan.py`'s and must be declared in the object rather than in prose: it
holds a vocabulary, not the language, so a clean run means no *listed* feature was used.

### 5. A coordinate citation is ratcheted to zero outside `docs/adr/`

A check fails when tracked prose outside `docs/adr/` carries a `path:NNN` citation. After ruling 1
the population is zero, so its measured false-positive rate is zero and this is a ratchet rather
than a widened instrument — the arrangement `scratch_census.py` already uses for a non-owning
checkout.

- It **reads inline code spans**, because both repaired instances live in one. `spelling_scan.py`'s
  mention-versus-use rule does not transfer.
- **Fenced blocks are exempt**, declared in advance rather than discovered: a fence quoting `grep -n`
  output legitimately carries the shape, and there are zero such blocks outside `docs/adr/` today.
- `docs/adr/` is outside the walk entirely, on ruling 2's boundary.
- The tracker half is filed separately. A repository test cannot read an issue body, and the
  existing grader declares that limit.

What it costs is a genuinely useful future line citation in `CLAUDE.md` or a skill. **That cost is
the finding**: such a citation fails nothing and rots silently, which is the whole of #791.

### 6. The false statements around the coordinate are corrected in the same edit

The measured table above lists them. Each is a **fact** rather than a decision, so ruling 2 already
licenses correcting them, and one dated line covers all of it.

**Repairing the pointer while leaving a stale count in the same table row is #791's own instrument
finding one level in.** That ticket records a pass scoped to `CLAUDE.md` walking past the identical
defect in a ratified ADR; a pass scoped to the *coordinate* walks past three false sentences
touching it.

**The consumer-path correction goes in because leaving it strands a live instruction.**
`README.md` tells macOS users to install a newer Python on the strength of the 3.10 floor, and ADR
0002 currently denies that any consumer reaches it. The **decision** that finding raises — whether
the consumer path gets its own floor check, and what a consumer should be told — is ruling 4's
ticket and not this record's.

## What this record does not settle

**Whether the floor is right for a reason nobody has measured.** Nothing has run this suite on 3.10.
The floor is inferred by static reading, which ADR 0002 already records as having been wrong twice,
and ruling 3's check does not change that — it grades whether the stated evidence exists, not
whether the number is correct.

**The 266 coordinate citations inside `docs/adr/`.** Ruling 2 carves out one record on a stated
argument and explicitly declines to generalize it.

**Any coordinate published to the tracker.** Ruling 5 is a repository walk. The class demonstrably
lives on the tracker as well, and the grader that could reach it declares the gap as a limit rather
than closing it.

**Whether a pin exists that neither walk can see.** Both instruments are floors on literal shapes,
stated in the measurement above.
