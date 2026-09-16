# The CPT MDM table is a committed two-reader sheet and the CPT edition is judged by service date

Ticket [#1333](https://github.com/mshamblin5150-code/clinical-skills/issues/1333) was filed when a
`batch-shift` run for one shift finished every note and could not select an E/M level,
because `icd10-cpt` step 5 reads the medical decision making (MDM) table only from the rendered CPT
Professional 2026 book and the session had no browser connection. The procedure-code database carries
every E/M code and descriptor but not the table that defines what problems, data, and risk each
level requires. The clinician ruled on 2026-09-16 that the table is committed and that the waiting
shift waits for this change; the rulings below were settled in the grilling that followed, the same
day.

## Ruling 1 — the sheet holds the MDM grid and the guideline definitions it depends on

The committed text is the MDM grid (straightforward, low, moderate, and high across problems, data,
and risk) **and** the CPT E/M guideline definitions a reader needs to apply it, such as what an
acute, uncomplicated illness or injury is or what counts as independent interpretation. Both are
transcribed verbatim. A grid without its definitions would move the recall that step 5 forbids one
layer down: a run could match a cell and still have to remember what the cell's words mean.

The clinician recorded the repository's AMA permission as covering internal database storage and
extended it, on 2026-09-16, to the MDM table and its guideline definitions. That extension belongs to
this repository, as the database's permission already does; it does not license other CPT text.

## Ruling 2 — the sheet is Markdown under `reference/`, one file per edition

The artifact is `reference/cpt-em-mdm-2026.md`, beside `reference/procedure-codes-2026.md`, which
points to it. It is not a table inside `procedure-codes-2026.sqlite` and not both: an agent reads the
sheet directly and a diff shows its text, while two copies of one text would need a test to hold them
equal and would buy nothing. The edition is in the filename, so a new edition is a new file rather
than an edit.

Every grid row and definition carries a locator naming the book, the edition, and the **printed page
number** visible on the rendered page, for example `CPT Professional 2026, p. 13`. ADR 0247 makes the
printed number the reading standard; the VitalSource sequence number the database's code rows carry
is not a page a person can turn to. The sheet's header restates the permission scope of ruling 1.

## Ruling 3 — `icd10-cpt` step 5 reads the sheet, and the book remains required in two cases

A note-path run selects an MDM-based E/M level from the committed sheet whose edition covers the
encounter's service date, instead of from the rendered book. The rendered book is still required, and
without it the line stays pending rather than being finalized from recall, in exactly two cases:

- the service date falls outside every committed sheet's edition;
- the level turns on CPT E/M guidance the sheet does not hold, such as selection by total time,
  modifier 25 on a same-day procedure, critical care, or prolonged services.

Step 5's statement that the MDM phrasing is recalled and unverified is removed. The `clinical-note`
coding-worksheet requirement reads the applicable committed MDM sheet or rendered CPT instructions.

## Ruling 4 — the family follows the stated place of service, and only ED and office are supported

The E/M family follows the place of service the note states. An emergency department encounter takes
99281 through 99285 by MDM alone. An office or clinic encounter takes 99202 through 99215 by MDM, with
new-or-established status from the private identity map or Medatrax evidence under ADR 0250 ruling 4;
its time route stays book-only under ruling 3. An unstated or unrecognized setting — urgent care,
observation, or a hospital inpatient visit — blocks selection, as unknown patient status does, until a
later ticket adds that family. The first reader confirms from the book's own text, not from recall,
that the one grid governs both supported families.

## Ruling 5 — agents transcribe and a blind second reader must agree exactly

Verification is done by agents and needs no reading by the clinician.

- A first reader opens CPT Professional 2026 through `vitalsource-chrome` under ADR 0247's reading
  standard and writes each grid row and definition with its printed page.
- A separate second reader that has not seen the sheet receives only the list of printed pages and
  transcribes the same entries independently. A self-authored second read is not a second read.
- `tools/cpt_mdm_sheet.py` normalizes whitespace and compares the two transcriptions entry by entry.
  Any disagreement returns to a rendered-page reading; neither copy is preferred because it looks
  more plausible.
- The sheet records, per entry, the SHA-256 of its normalized text and the date of the agreeing
  two-reader read. The grader refuses an entry whose current text no longer matches its digest, so a
  later edit without a new two-reader read fails. The pre-commit hook runs the grader when the sheet
  is staged, which adds it to the checks that can refuse a commit.

What this cannot establish is that either agent actually looked at the page; exact agreement and
digests prove agreement and the absence of a later edit. That limit belongs in the grader's declared
limits.

## Ruling 6 — the first reader's session writes the private CPT receipt

Before transcribing, the first reader confirms that the rendered book's edition and ISBN match the
procedure-code database's `source` row. It then writes the private CPT receipt with a command that
derives every receipt field from the database, so no field is typed by hand. The receipt lives in the
owning checkout's `scratch/`, and the skill names its path once. The receipt still proves only that
its edition, fingerprint, and boundary match the database, not that the reading occurred, as
`coding_freshness.DECLARED_LIMITS` already states.

## Ruling 7 — the CPT edition boundary is judged by service date

A CPT receipt and an MDM sheet serve an encounter when that encounter's **service date** falls within
their edition, not when the day the gate runs does. A 2026-12-20 encounter coded on 2027-01-04 uses the
2026 receipt and sheet and passes; a 2027 service date needs 2027 materials. This matches how
`coding_freshness.py` already selects the ICD-10-CM release, and how CPT codes are assigned by date of
service. It supersedes ADR 0250 ruling 5's wording that the CPT receipt expires when the edition
boundary passes; a fingerprint change still invalidates the receipt.

## Ruling 8 — the freshness gate refuses an E/M code no verified sheet covers

For every E/M code in the supported families, `tools/coding_freshness.py` requires a committed
`reference/cpt-em-mdm-<edition>.md` whose edition covers that code's service date and which passes
`tools/cpt_mdm_sheet.py`. A missing or failing sheet writes no pass receipt. The private receipt
records the sheet's filename and the SHA-256 of its bytes; the rendered artifact still carries only
`Coding freshness: PASS`. Whether the selected level is supported by the note remains a reading and
stays outside the gate's claim.

## Ruling 9 — nothing carries across an edition

At the 2027 edition, the procedure-code database is rebuilt from the 2027 licensed source, a new
two-reader sheet is transcribed, and a new receipt is written. The 2026 sheet and receipt continue to
serve 2026 service dates.

## Consequences

- The waiting shift's E/M lines stay pending until this build merges and the 2026 sheet and
  receipt exist.
- `icd10-cpt`, `clinical-note`, `reference/procedure-codes-2026.md`, `tools/coding_freshness.py`, the
  new `tools/cpt_mdm_sheet.py`, and the pre-commit hook change together.
- ADR 0250 ruling 5's expiry wording is superseded in part by ruling 7; its other rulings stand.
