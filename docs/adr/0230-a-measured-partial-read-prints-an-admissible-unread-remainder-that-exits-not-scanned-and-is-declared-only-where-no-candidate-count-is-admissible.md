# A measured partial read prints an admissible unread remainder that exits not scanned, and is declared only where no candidate count is admissible

[#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066) asked whether the
extractor-coverage rule, which [ADR 0170](0170-every-grader-declares-the-posture-its-empty-population-takes.md)
enforces only for an empty population, owes the family a remainder obligation, and what each of its
partial-read leads receives. Grilled 2026-09-14 against `90b16be0`, freshness gate `FRESH`; the
clinician ruled every point below on the same day. Nothing is built here; this is the record the build
reads.

## Measured before ruling

Every lead was driven by the real command on synthetic inputs built from each module's committed test
helpers, beside a control that carries one defect in a form the grader reads. *Had a lead been false,
its shape would print the control's status or a nonzero unread count.* None of these inputs is
committed.

### Silent partial reads with nothing declared

| member | shape | control | shape |
| --- | --- | --- | --- |
| `refusal_scan` | a refusal missing `needs:` moved into a second refusal block | exit 1, 2 records | exit 0, 1 record |
| `refusal_scan` | a `###` heading inside the refusal block before that refusal | exit 1, 2 records | exit 0, 1 record |
| `voice_model_scan` | a pair with no His half headed `**B3:**` rather than `**B3.**` | exit 1, 7 pairs | exit 0, 6 pairs |
| `discussion_reply_scan` | a duplicated reference entry whose second copy has no year | exit 1, `respent-source: 1` | exit 0, `respent-source: 0` |
| `discussion_post_scan` | a stale submission fingerprint with `POST-URL` and `POSTED` removed from `post.md` | exit 1, `submission-fingerprint: 1` | exit 0, `submission-fingerprint: 0` |

The `voice_model_scan` shape is silent only from three pairs in a register; with two, `pair-floor` fires.
The `discussion_post_scan` rows print `0`, not `not graded`, and `reread.md` held the post's record.
`skills/discussion-post/SKILL.md` appends that record only after submission, so its presence without
the two fields is a submitted run, not a pre-post one.

### Narrowed or not a silent pass

- **`peer_critique_scan`.** A post with no `AUTHOR` line leaves the roster, and the report already
  prints `roster posts read 1 of 2`. The narrowed roster makes the addressed-name row stricter, but
  the run exits 1 or 0 where `discussion_reply_scan` refuses the same roster with exit 2, and a
  critique of the unread classmate opening with another roster name exits 0.
- **`reference_scan`.** A cp1252 draft grades identically to UTF-8. A cp1252 en dash in a
  translated-work citation, like an ASCII hyphen there, drops the citation from the population
  (`candidates 0`) and produces a false `uncited-entry`, exit 1. The loss is a citation, loud through a
  false finding, never counted as unread.
- **`case_study_scan`.** A misspelled optional heading exits 0 with `headings not recognized 1`.
  Correct drafts also carry unrecognized headings: `SKILL.md` permits `## Discussion`, and the tests'
  own `Growth Assessment` shape counts one.

### ADR 0178 ruling 8's declared rows, tested for a candidate count

| row | candidate | on committed correct sets | fires on the control |
| --- | --- | --- | --- |
| `block_scan` unreadable or absent tier block | notes read against notes carrying a block | 0 unread; `clinical-note` requires a block on every note | yes |
| `filled_vitals_census` height and weight units | per class per note, a height or weight label followed by a number inside the block | 0 unread, except `slot-form-run`'s `peds-bp-case-05`, whose decimal-inch height the parser misses | yes |
| `filled_vitals_census` FILLED·asserted key lines | a `FILLED`-then-`asserted` opener after markup | 2 unread in correct notes, both column-0 prose | yes |
| `anchor_scan` per-run gradeable coverage | worksheets read against worksheets with a mark, listing or band | 3 in run-2, each correctly having nothing to grade | yes |
| `anchor_scan`, `specificity_scan` code-entry openings | any line opening on a code-shaped token | 69 unread in run-2, all step-4 listings, undocumented-block lines and wrapped rationale | yes |
| the same | `ENTRY` with an optional markup prefix before the system token | 296 of 296 in run-2, 3 of 3 in the skill's examples | yes |
| `specificity_scan` flags | a case-sensitive `SPECIFICITY` opener after markup | 200 of 200, 9 of 9 | yes |

`heading_read`, the shared reader #1257 added, already counts `HEADING_CANDIDATE`, which is `HEADER`
without its required colon, and turns a remainder into the finding `unread-heading-read`, exit 1.
ADR 0170 ruling 10 made `specificity_scan`'s unflagged remainder not scanned, exit 2. The family had no
settled posture.

## Ruled 2026-09-14

### 1. A measured partial read may not be silent and undeclared

A form measured to go unread beside forms a grader reads either prints an unread remainder or is a
declared limit with a control. This is not an obligation on every `run_grader.MEMBERS` name: no
mapping beside `EMPTY_POPULATION_POSTURES` is added, and a member where nobody has measured a partial
read declares nothing. **A universal mapping was declined**: an empty population is something every
member has, while a partial read belongs to a form, so a required entry would make members assert an
absence nobody measured, which ADR 0093 ruling 4 and ADR 0167 ruling 3 refuse. **Leaving each module to
choose was declined**: that is how `peer_critique_scan` and `discussion_reply_scan` split on one roster
shape.

### 2. A nonzero unread remainder exits 2, and a finding outranks it

The run reports that part of its input went unread; it does not claim the unread form is wrong.
`heading_read`'s remainder moves from exit 1 to exit 2, and ADR 0170 ruling 10 already agrees.
**Exit 1 was declined**: a grader cannot tell a malformed member from a legitimate form it does not
recognize, so a template that gains a second shape would fail a correct run under a confident finding.
**Splitting by whether a skill template fixes the form was declined**: it needs a per-form ownership
judgment in every module.

### 3. A remainder is required wherever an admissible candidate count exists

A declared limit names only the forms the candidate count cannot see. The ADR 0178 ruling 8 entries
naming #1066 retire, with their controls, wherever ruling 5's test admits a count. **Accepting a
declaration alone was declined**: it prints nothing, so the silent clean the declaration describes
keeps happening. **Keeping ADR 0178's declarations frozen was declined**: that record named them
interim, owned here.

### 4. A replaced byte is not an unread member

ADR 0116 ruling 3's grade posture for `reference_scan`, `case_study_scan`, `checks_ledger` and
`research_ledger` stands. The measured loss was a citation, so `reference_scan` gets a citation
candidate count under ruling 3, and the build drives the U+FFFD citation into it rather than assuming
it lands. **Counting replaced bytes as a remainder was declined**: a cp1252 draft that grades
identically would exit 2 in four modules. **A report-only byte count was declined**: it decides nothing.

### 5. A candidate count is admissible when it grades nothing, reads zero unread on every committed correct set, and fires on the shape's control

Relaxing a matcher on the one restriction whose miss is being counted qualifies, because the count then
does not share the cause of the miss. `heading_read`'s candidate already has this shape. A candidate
that fires on a correct committed set is not admissible, and its row stays declared. **Refusing any
count derived from the extractor was declined**: it would leave `heading_read` as an unexplained
exception, and the noisy independent candidates show independence alone does not make a count usable.

### 6. The posture is held by opt-in conformance with one shared remainder line

Every member that prints a remainder prints it through one shared line, `unread remainder N`. A test
module joins by naming its membership and supplying one input with an unread form beside read forms
and its read twin; the kit asserts a nonzero remainder and exit 2, exit 1 when a finding is added, and
0 unread on the twin. ADR 0080's opt-in `gate_conformance` is the precedent. **Record-only enforcement
was declined**: the split this ruling closes arose between two modules written after ADR 0170.
**Conformance on status alone was declined**: it grades the exit and not the printed remainder a reader
sees. The kit certifies agreement with a member's declaration, never that a member has no partial read.

### 7. Each measured lead receives

| member | disposition |
| --- | --- |
| `refusal_scan` | remainder over refusal headings and over refusal marks after the first refusal heading, kept apart from the differential's marks |
| `voice_model_scan` | remainder over pairs-body lines opening `**` at column 0 |
| `discussion_reply_scan` | remainder over reference entries dropped by `_valid_references` |
| `discussion_post_scan` | a `reread.md` record for the draft beside a `post.md` with neither posting field is a remainder; with no record, the posted-reading rows print `not graded` |
| `peer_critique_scan` | a roster post with no `AUTHOR` line is a remainder and exits 2, agreeing with `discussion_reply_scan` |
| `reference_scan` | remainder over citation candidates, with the ASCII hyphen and U+FFFD controls |
| `block_scan` | remainder over notes read without a readable tier block |
| `filled_vitals_census` | remainder over height and weight candidates per class per note; `fixtures/slot-form-run` then exits 2 on its decimal-inch height, and the fixture is not edited |
| `anchor_scan`, `specificity_scan` | remainder over relaxed-prefix code entries and `SPECIFICITY` flags, in `worksheet_grammar` since ADR 0186 ruling 10 shares that grammar |
| `case_study_scan` optional headings | declared, no admissible count; ADR 0209 ruling 7's limit stands and `headings not recognized` stays printed and ungated |
| `anchor_scan` per-run gradeable coverage | declared, no admissible count |
| `filled_vitals_census` FILLED·asserted keys | declared, no admissible count |
| `aar_scan` | built by #1173 |

A declared row that stays declared stops naming #1066 as the owner of its repair and names this record.

## Taken as conventions, not ruled

- `CONTEXT.md` gains **Unread remainder**.
- #1066 is the one build ticket, landed across `Part of #1066` pull requests. The first carries the
  shared line, the kit and at least one member, so the kit is proven live.
- The shared line's module and exact function name are the build's.
- `CPT 12001 — ...` step-4 lines prefixed with a system token read as entries in `case-06.md`. That is
  not a partial read and not filed: ADR 0186 ruling 3 already holds a compliant listing to no system
  token and records the join as a latent shape.

## Consequences

- `heading_read`'s five hosts, `checks_ledger`, `deck_scan`, `discussion_post_scan`,
  `discussion_reply_scan` and `peer_critique_scan`, see an unread heading-read record exit 2 unless
  another finding fails the run. Where [ADR 0225](0225-a-refused-reference-label-voids-only-its-declared-kinds-and-a-partial-gate-keeps-what-it-read.md)
  derives precedence from gated row sets, `unread-heading-read` stops being a counted finding kind.
- Tests pinning today's exit on a declared row's control flip deliberately when that row becomes a
  remainder; which ones is established by running the suite, not listed here.
- `CLAUDE.md`'s *Extractor coverage* section and the per-module sections name the exit-2 posture where
  they describe a remainder.

## What this does not reach

**A partial read nobody has measured.** Ruling 1's limb that a measured partial read may not sit
undeclared is not mechanically checkable; the kit sees only members that opted in.

**Whether a candidate count sees every form.** Ruling 5's zero-unread test is a floor against false
exits on committed material, and a form neither the matcher nor the candidate recognizes stays
invisible, which is why each remainder keeps a declared floor.

**Whether the unread form is a defect.** An exit 2 says a member went unread, not that the artifact is
wrong.
