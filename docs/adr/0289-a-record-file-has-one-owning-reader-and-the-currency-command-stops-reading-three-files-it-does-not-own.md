# A record file has one owning reader and the currency command stops reading three files it does not own

**Measured at:** 614bfe9c1b9eb5b4bfeb625f0899527f9fcaf6f1

[#1331](https://github.com/mshamblin5150-code/clinical-skills/issues/1331) was filed from an
architecture review on 2026-09-16. It found that `reference/thresholds/coverage.md` is read by two
parsers with different row rules, and counted five table splitters across the guideline
registries. Triage on 2026-10-03 added a third coverage read, which rewrites the file, and showed
that the import reason was a cycle rather than a heavy import. Grilled 2026-10-03 against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

### The defect is one module reading files it does not own

`guidelines_currency` splits table rows with its private `_cells` and `_is_rule`. It applies them
to its own registry and to three files other modules own:

- **The coverage registry**, in three places: the supersession-handoff check in `audit`, the topic
  preflight in `fetch_replacement`, and `_mark_topic_unread`, which rewrites the file. All three
  accept any five-cell row anywhere in the file, with no schema marker and no header anchor. The
  owner, `threshold_coverage.parse_registry`, requires the marker and reads only rows below the
  `| topic | subject | state | artifact | record |` header.
- **The catalog audit ledger**, in the handoff check, which collects a binding from every
  five-cell row in the file. The owner, `guidelines_catalog.parse_audit`, reads the `## Documents`
  table by its heading and column header. On the committed ledger the loose read finds 181
  bindings and the owner finds 180 documents. The extra one is the table's own header row. The
  row writer, `_upsert_audit_digest`, is already anchored to `## Documents` but carries its own copy
  of the header.
- **The threshold sheets' `## Sources` tables**, read by draft mode's `_source_metadata`. Its
  docstring says importing the sheet grader would cycle. That is true of `threshold_sheet` and false
  of `threshold_grammar`, which owns the sheet parser and imports only `artifact_provenance` and
  `guidelines_manifest`, neither of which imports `guidelines_currency`. On the committed sheets
  both readers return the same 180 source documents, with no field differing.

The other three splitters the ticket named, `threshold_grammar._cells`,
`guidelines_catalog.split_table_row` and `guidelines_recs._markdown_rows`, each read only their own
file. No file is read two ways by them.

### The import cycle is real and the reader does not need its cause

`threshold_coverage` imports `threshold_sheet`, and `threshold_sheet` imports
`guidelines_currency`, so the currency command cannot import the owner. `parse_registry` itself
uses only the schema marker, the row record and one regular expression. The sheet grader is used by
the owner's audit and command line: `gate_schema`, `DECLARED_NON_SOURCE_CLASSES` and
`load_catalog_facts`.

### The splitters differ only on features no committed file uses

No coverage registry, catalog, audit ledger, currency registry, USPSTF table or threshold sheet
contains an escaped pipe or an HTML entity, and the currency registry contains no `&` at all.
`guidelines_currency._cells` is the only splitter that decodes entities. It came in with the
module's first commit and no test exercises it. Python's `html.unescape` also decodes some legacy
entity names without a closing semicolon, so `https://x/?a=1&not=2&sect=3&copy=4` reads back with
the three parameters replaced by `¬`, `§` and `©`.

Re-derive the two reader comparisons from the repository root:

```bash
python - <<'PY'
import sys; sys.path.insert(0, "tools")
from pathlib import Path
import guidelines_catalog as g, guidelines_currency as c, threshold_grammar as t
text = Path("reference/guidelines-catalog-audit.md").read_text(encoding="utf-8")
docs = g.parse_audit(text)[0]
loose = {(x[0], x[1]) for l in text.splitlines()
         if (x := c._cells(l)) is not None and len(x) == 5 and not c._is_rule(x)}
print("audit", len(loose), len({(d.society, d.filename) for d in docs}))
root = Path("reference/thresholds")
mine = c._source_metadata(root)
own = {}
for p in sorted(root.glob("*.md")):
    if p.name in ("README.md", "coverage.md", "subjects.md"):
        continue
    for v in t.parse(p.read_text(encoding="utf-8"), p).sources.values():
        own[Path(v["document"]).name + ".pdf"] = v
print("sources", len(mine), len(own), sorted(set(mine) ^ set(own)))
PY
```

## Ruling 1. The scope is every file the currency command reads that another module owns

The coverage registry, the catalog audit ledger and the threshold sheets' `## Sources` tables are
each read through their owning reader. The three splitters that read only their own file are not
unified. A module parsing a file it does not own with its own rule is the defect. A module reading
its own file with its own splitter is not, because no file is read two ways and the splitters
disagree only on features no committed file uses.

## Ruling 2. The coverage registry's reader moves to its own module

`tools/coverage_registry.py` holds the schema marker, the row record, `parse_registry`, and a pure
function that rewrites one topic's row. It imports nothing from the threshold-sheet tools.
`threshold_coverage`, `guidelines_currency`, `subject_ledger`, `threshold_draft`, `uspstf_table`
and `differential_scan` import the reader from it. This removes the cycle through `threshold_sheet`
rather than deferring an import into a function.

## Ruling 3. Marking a topic unread refuses a broken registry before anything is downloaded

The replacement fetch's preflight reads the coverage registry with `coverage_registry`. It refuses
when the reader reports a problem, when the topic is absent, or when the topic appears more than
once. The rewrite changes exactly the line the reader found and writes it in the module's one row
format. `guidelines_currency` keeps the artifact lock and the atomic replace that wrap every write
it makes. A correct committed registry fetches exactly as it does today.

## Ruling 4. Draft mode reads sheet Sources through the sheet grammar

`_source_metadata` calls `threshold_grammar.parse` and its private table walk is deleted, together
with the docstring's false claim about a cycle.

## Ruling 5. No registry cell is decoded as HTML

`guidelines_currency._cells` stops calling `html.unescape`. Every registry reader then reads cells
exactly as written, so no shared table helper needs a ruling on entities.

## Ruling 6. The audit ledger's row writer moves to the catalog module

`guidelines_catalog` gains a pure function that returns the ledger text with one `## Documents` row
added or replaced. It uses the catalog's own column definition and refuses what `parse_audit`
refuses. `guidelines_currency` keeps the artifact lock and the atomic replace. The currency
command's ledger reads use `parse_audit`.

## Ruling 7. A malformed owned file makes the supersession check not graded

When `coverage_registry` or `parse_audit` reports a problem, the currency command's supersession
check is reported as not graded. The report names the file and the owner command to run,
`python tools/threshold_coverage.py` or `python tools/guidelines_catalog.py`, and the full report
still prints. The command exits 2, and a registry failure found on the same run still exits 1. The
check never grades the rows an owner returned beside a reported problem.

## Ruling 8. The glossary names the owning reader

`CONTEXT.md` gains **Owning reader**, defined against **Second reader** and **Declared narrower
reader**. A duplicate parser of a file's format is not an independent check of its content.

## What the build must not change

`python tools/threshold_coverage.py`, `python tools/guidelines_currency.py` and
`python tools/guidelines_catalog.py` refuse nothing new on a correct committed registry, ledger or
sheet. The pre-commit gates that run them keep their trigger conditions.

## Rejected options

**Fix only the coverage registry.** The audit ledger and sheet Sources reads keep the same defect
in the same module.

**Unify all five splitters on one table helper.** It changes three readers that disagree with
nothing and has to rule on escaped pipes and entities that no committed file uses.
[ADR 0011](0011-an-assertion-record-is-read-by-row-grammar-and-the-registry-convention-does-not-transplant.md)
refused a comparable unification for the same lack of a measured need.

**Defer the owner's `threshold_sheet` import into the functions that use it.** The cycle stays and
returns as soon as the import moves back to the top of the file.

**Put the coverage reader in `threshold_grammar`.** That module would then own two files' formats.

**Tolerate a duplicated topic by rewriting its first copy.** The fetch would leave one copy marked
`unread` and the other pointing at the retired document, which is a half-finished supersession
handoff.

**Keep entity decoding, or add encoding on write.** The first can silently change a web address.
The second invents a convention for one registry that nothing needs.

**Turn a malformed owned file into a registry failure, or grade the rows the owner returned.** The
first reports a broken coverage file as a currency defect. The second presents a partial read as a
clean one.
