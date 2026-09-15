# The index tables ship, and an index path carries only a code's stem

[#1310](https://github.com/mshamblin5150-code/clinical-skills/issues/1310) was filed from #1139's
grilling after the clinician ruled that the ICD-10-CM external-cause index and Neoplasm Table ship
beside the alphabetic index
[ADR 0243](0243-descriptor-agreement-is-read-blind-against-the-note-and-the-index.md) ruling 2
already loads. #1139's build landed as #1314 before this grilling began. Grilled 2026-09-15; the
clinician ruled every point below on that date. Nothing is built here; this is the record the build
reads.

**Measured at:** 5314d90a1a02dfa0ca59f78f06af13fef2c4a0ba

## Measured before ruling

**No index source gives an injury or external-cause code its seventh character.** In the committed
database, 6,956 index rows store a code ending in a dash and 26,437 billable S and T codes sit under
those dash prefixes. Only 150 index rows carry a full seven-character code, none of them in S, T, V,
W, X or Y. `Laceration > thumb > right` reaches `S61.011`; the committed worksheet at
`fixtures/filled-anchor/run-2/case-06.md` proposes `S61.011A`. The external-cause index is the same:
its 6,671 codes run three to six characters, and `W26.8` is as far as it goes toward `W26.8XXA`.
`anchor_scan._valid_route` requires the route's last code to equal the subject code, so every
seventh-character code on an index route fails today with "has no descriptor or index route".

**A pointer into a table the database does not hold is a finding, not unread.** 119 main-index rows
point to the Table of Drugs and Chemicals, 901 name a Neoplasm target and 12 more read *Table of
Neoplasms*, and one points to the external-cause index. None can reach a code, so each route fails.

**The three sources, from the CMS FY2026 April 1 release zip.** The Neoplasm Table is one main term
with seven column headings: Neoplasm, Malignant Primary, Malignant Secondary, Ca in situ, Benign,
Uncertain Behavior, Unspecified Behavior. The Table of Drugs and Chemicals heads its columns
Substance, Poisoning Accidental (unintentional), Poisoning Intentional self-harm, Poisoning Assault,
Poisoning Undetermined, Adverse effect, Underdosing, and every code it gives falls in T36 through
T65. The external-cause index reaches every `Y92` code under *Place of occurrence*, every `Y93` code
under *Activity*, and all but two of its `Y99` codes under *External cause status* and a duplicate
*Status of external cause* main term.

**The official guidelines are not in the release zips.** The April 1, 2026 ICD-10-CM Official
Guidelines for Coding and Reporting were read from the CDC NCHS FTP publication. Section I.C.20 makes
external-cause reporting voluntary, matches a mechanism code's seventh character to the injury's,
limits place, activity and status codes to the initial encounter, and forbids `Y92.9`, `Y93.9` and
`Y99.9` when the fact is not stated. Section I.C.19.e defines adverse effect, poisoning and
underdosing, and codes an unknown or unspecified intent as accidental, with undetermined reserved for
documentation that says intent cannot be determined. The D37–D48 tabular section note defines
uncertain behavior as histology that cannot settle malignant or benign; the D49 note defines
unspecified morphology and behavior and says *mass* is not a neoplastic growth unless otherwise
stated. Section IV.H forbids coding a suspected diagnosis in the outpatient setting.

**Cross-references do not always name the heading they point to.** Across all four sources, 15,412
cross-references were run through `_valid_route`'s word-subsequence test against every path, with a
table cell rendered as its row path ending in its column heading. 14,256 were followed, 75 name only
a table, and 1,081 were not followed: reordered words (*Neoplasm, malignant, stomach*), placeholders
(*by type of instrument*, *by animal or substance, poisoning*), character instructions (*categories
T36-T50, with 6th character 5*), and headings absent in that wording (*Defect, reduction, upper
limb*).

**What the skills and fixtures carry.** `skills/icd10-cpt/SKILL.md` and `skills/clinical-note/SKILL.md`
say nothing about external-cause codes, seventh characters or neoplasm behavior. Two committed runs
proposed `W26.8XXA`; neither proposed `Y92`, `Y93` or `Y99`, which the #1310 filing had recorded as
proposed. Committed notes propose `D25.9` and refuse `C54.1`, `D21.11` and `C49.11`. No committed
fixture carries a T36–T65 code.

## Ruling 1 — an index path that stops early carries only the code's stem

An index path that reaches a code's first characters, whether a subcategory or a dash form, agrees
as that code's stem. Every character the tabular adds must still agree with the note: laterality,
site detail, the placeholder, and the seventh character under ADR 0243 ruling 4's this-encounter
rule. `Laceration > thumb > right` carries `S61.011`; the note earns `S61.011A`'s final character by
documenting an initial encounter. This repairs #1139's route test inside #1310, because the
external-cause load does nothing without it. Accepting the stem with nothing further checked was
declined because *ankle sprain* would agree with the left-ankle or sequela code; keeping exact
equality was declined because injury and external-cause codes could then agree only by repeating
their descriptors.

## Ruling 2 — external-cause codes follow Section I.C.20 and only what the note documents

`icd10-cpt` proposes a mechanism code whenever the note states how the injury happened, on every
encounter treating it. Place, activity and status codes are proposed only at an initial encounter and
only when the note states them; `Y92.9`, `Y93.9` and `Y99.9` are never proposed, and `Y99` needs
another external-cause code beside it. External-cause codes follow the injury code. The mechanism
code's seventh character copies the associated injury line's, which earned its own under ruling 1.
Proposing mechanism codes only was declined because it leaves most of the shipped index idle;
proposing none was declined for the same reason, although national reporting is voluntary.

## Ruling 3 — the note's words choose the neoplasm column

*Mass*, *lump* or *nodule* takes its sign code and never a neoplasm code. *Tumor*, *growth* or
*neoplasm* with no stated behavior takes unspecified behavior, `D49`. Uncertain behavior, `D37`
through `D44` and `D48`, agrees only with a documented pathology result that could not settle
malignant or benign; before one exists the code waits on a result, which ADR 0243 ruling 9 makes a
finding. A suspected malignancy stays in the differential, its malignant code is refused as waiting
on tissue, and the sign code is proposed instead. Malignant primary, secondary, in situ and benign
agree only with a stated behavior or a morphology term the index sends to that column. For *left
breast mass, concerning for malignancy, biopsy scheduled*, `N63.20` is proposed and `C50.912` refused.
Letting unspecified behavior absorb every pending case was declined because it contradicts the D49
note on *mass*; treating the two columns as interchangeable was declined because it lets `D48.62`
stand where no tissue has been read.

## Ruling 4 — a benign neoplasm code does not wait on tissue

A benign code agrees when the note names a benign morphology or states *benign*, whether reached by
examination or imaging, and the ordinary hedge rule applies, so *likely lipoma* documents it. A code
naming benign behavior with no morphology, such as `D21.11`, needs the word *benign*, and a lump the
clinician did not call a neoplasm keeps its sign code. Only malignant, in situ, secondary and
uncertain-behavior codes can wait on a result. Requiring tissue for every benign code was declined
because it refuses lipomas diagnosed on examination and fibroids read on ultrasound.

## Ruling 5 — the Table of Drugs and Chemicals ships too

All three parts ADR 0243 ruling 2 excluded load into `reference/icd10cm-2026.sqlite`: the Neoplasm
Table, the external-cause index, and the Table of Drugs and Chemicals. The clinician's reason: *"i
don't want to miss billable codes just because it is rare."* Counting a pointer into an unloaded drug
table as unread, guarded to T36 through T65, was declined with it; so was keeping that pointer a
finding.

## Ruling 6 — the guideline's definitions choose the drug column, and accidental is its default

Section I.C.19.e's definitions choose the column against the note's words: overdose, a wrong
substance, a wrong route, a nonprescribed drug taken with a prescribed one, or a drug with alcohol is
poisoning; a drug correctly prescribed and properly administered is an adverse effect; taking less
than prescribed or stopping on one's own is underdosing. Self-harm and assault need the note's words,
and undetermined needs the note to say intent cannot be determined. Where the note states no intent,
accidental agrees through the guideline's own default, as ruling 2's copied seventh character agrees
through the guideline's matching rule. *2-year-old got into the ibuprofen* takes `T39.311A`. Requiring
note words for every column was declined because it fails the guideline-correct code on nearly every
pediatric ingestion.

## Ruling 7 — a hedged intent agrees only with undetermined

A hedged self-harm or assault intent agrees only with the undetermined column. The poisoning is
established; only its intent is uncertain, and the hedge documents that. *Acetaminophen ingestion,
possibly intentional, patient denies* takes `T39.1X4A`. Applying the ordinary hedge rule was declined
because it writes a self-harm code on a *possibly*; treating the hedge as silence was declined because
it records as accidental what the clinician flagged as perhaps not accidental.

## Ruling 8 — following a cross-reference is forgiving, and its residue is unread

Word order within a cross-reference is ignored. A *by site*, *by type* or *by substance* placeholder
is filled by the next step's words, which must themselves be note words under ruling 1. A character
or code-range instruction, such as *categories T36-T50, with 6th character 5*, is satisfied by the
subject code. A step still unmatched, whose next path is real and ends at the subject code, enters
the shared unread remainder and exits 2, naming the cross-reference. Keeping that residue a finding
was declined because it calls a correct code wrong on CMS's own wording; keeping the current ordered
word test was declined because it leaves every mismatch above a live false finding.

## Ruling 9 — one index mode reads one catalog of all four sources

`tools/icd10_lookup.py --index` reads the alphabetic index, the external-cause index and both tables
as one catalog. A table cell prints as its row path ending in its column heading, as in `Neoplasm,
neoplastic > lung > Malignant Primary -> code C34.9-`, and a cell holding no code prints nothing. The
route format #1139's committed agreement records use is unchanged. A flag per source was declined
because a route crossing sources, as the index's own pointers do, would then need a source marker on
every step.

## Ruling 10 — injury and neoplasm controls read real notes, and the drug rules declare their gap

A fresh agreement reader, told nothing about which rows are suspect, grades
`fixtures/filled-anchor/notes/case-06.md` against its worksheet's codes and must pass `S61.011A` and
`W26.8XXA` through index stems; a planted laterality or sequela mutation must fail. The same
arrangement over the committed neoplasm notes must pass `D25.9` and fail a planted uncertain-behavior
or malignant code with no pathology. The drug rules take synthetic tests only, for the column words,
the accidental default and ruling 7, and `anchor_scan.DECLARED_LIMITS` states that no committed note
exercises them until a real poisoning note is committed. A synthetic poisoning fixture read blind was
declined as ADR 0243 ruling 19's input written knowing the rules; holding the drug table was declined
as ruling 5 reversed.

## Consequences recorded as derived rather than ruled

- **ADR 0243 ruling 2's exclusion sentence is superseded** and left as written, with a dated marker
  beneath it.
- **`CONTEXT.md`'s Descriptor agreement entry carries ruling 1.**
- **`skills/icd10-cpt/SKILL.md` gains the external-cause, neoplasm and drug rules**, and the agreement
  reader's brief states rulings 1, 3, 4, 6, 7 and 8 without the worksheet's quotations, as ADR 0243
  ruling 10 requires.
- **Ruling 1 widens every dash-form index code, not only chapters 19 and 20.**
- **#1217's Second-reader population is unchanged**; the agreement reader's brief grows.

## What this does not reach

- **Whether the note should have documented an external cause it omits.** A code the note does not
  support is not proposed, and no refusal records it.
- **A real poisoning note**, which ruling 10 declares.
- **Cross-references ruling 8 still cannot follow**, which are unread rather than graded.
