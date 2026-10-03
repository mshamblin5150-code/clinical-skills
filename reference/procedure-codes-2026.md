# 2026 procedure-code database

`procedure-codes-2026.sqlite` is the date-aware verification source for CPT and
HCPCS worksheet entries. It is committed under the maintainer's written
permission for internal database storage. That permission belongs to this
repository; downstream consumers must not infer their own CPT redistribution or
electronic-product rights from the presence of the file.

## Authorities

- **CPT Professional 2026**, Professional Edition, American Medical Association,
  ISBN 9781640163232, in the maintainer's authenticated VitalSource Bookshelf.
- **HCPCS 2026 Level II Professional Edition**, Elsevier, ISBN 9781640163317, in
  the maintainer's authenticated VitalSource Bookshelf.
- CMS's quarterly **Alpha-Numeric HCPCS public-use file**, used as the complete
  machine-readable Level II and modifier source. The exact downloaded filename,
  SHA-256, and effective date live in the database's `source` table.

The books are the human authorities for instructions, symbols, parentheticals,
cross-references, and worked guidance. The database verifies code identity,
descriptor, modifier identity, and service-date status only.

The licensed, two-reader E/M MDM grid and its dependent definitions are in
[`cpt-em-mdm-2026.md`](cpt-em-mdm-2026.md), with printed-page locators. The sheet
is separate from this database and does not carry other CPT instructions.

## Rebuild

```bash
python tools/procedure_codes_build.py \
  --hcpcs october-2026-alpha-numeric-hcpcs-file.zip \
  --hcpcs-effective 2026-10-01 \
  --cpt /owning-checkout/scratch/cpt-2026/agreed.csv \
  --cpt-agreement /owning-checkout/scratch/cpt-2026/agreement.json \
  --cpt-agreement-sha256 EXPECTED_AGREEMENT_SHA256 \
  --cpt-complete
```

The normalized licensed CPT CSV requires `code` and `description`. It may also
carry `short_description`, `effective_date`, `termination_date`, `category`, and
`locator`. Omit `--cpt-complete` for an excerpt or incremental transcription;
the lookup will then refuse to treat a miss as evidence that no CPT code exists.

Descriptor verification is separate from completeness. Without a matching
agreement record, the build writes `meta.cpt_descriptors = unverified`. A matching
record can set `verified` only with `--cpt-complete` and an agreed code set
containing every code in the previously shipped database. It must name both
full-code readings and the agreed CSV under the owning
checkout's `scratch/cpt-2026/`, with their SHA-256 digests. The two methods are
`page_structure` and `rendered_screenshots`. The record reports each reader's
`codes_read`, `disagreement_count`, every disagreement's agreed `description`
and `printed_page` in `resolutions`, and an empty `unread_remainder`. The build
compares every code and descriptor across the three CSVs and records all four
input digests in `source`. A mismatched agreement digest leaves descriptors
unverified; a missing or changed recorded input refuses the build. Bulleted
descriptors use each printed `•` in the single description field.

## Lookup

```bash
python tools/procedure_codes_lookup.py J1100 --on 2026-09-14
python tools/procedure_codes_lookup.py --modifier AB --on 2026-09-14
python tools/procedure_codes_lookup.py 12001 --on 2026-09-14
```

When a code system is partial, the command says so. Verify that candidate on the
rendered destination page in VitalSource; a search count or snippet is only a
locator.
