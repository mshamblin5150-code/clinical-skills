# An assertion record is read by row grammar, and the coverage registry's convention does not transplant

[#413](https://github.com/mshamblin5150-code/clinical-skills/issues/413) found the row identifier of `fixtures/*/assertions.md` defined more than once with different patterns, and asked whether the readers should share a parser, a row grammar or only a vocabulary. Grilling it on 2026-08-23 found the divergence is wider than the ticket measured, and that the tree had acquired a *second* convention for reading a structured Markdown record the day before, in [ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md)'s coverage registry.

**The decision is that the two artifacts keep different conventions, on a measured difference in their shape rather than on history.** The row grammar is unified into one constant that the general extractors import; nothing else is shared, and `assertions.md` gains no schema marker and no header anchoring.

## What was measured, on `16d1991`

**The ticket's own two headline figures were partial-instrument readings.** *18 modules read `assertions.md`* is a `grep` for the string, which cannot tell a mention from a use: **13 open one and 5 name it only in prose.** And the row grammar is written **four** ways, not two:

| where | pattern | scope |
| --- | --- | --- |
| `test_fixture_catalog.py` | `^\| ([A-Z]\d+) \|` | all 7 sets |
| `test_ruling_cohort.py` | `^\| ([A-Z]\d{1,2}) \|` | day-a, day-b |
| `test_allergy_reaction.py` | `^\| ([DBCGR][0-9]+) \|` | day-b only |
| `test_blind_fixture_instructions.py` | `^\|\s*([A-Z]\d+)\s*\|` | all 7 sets, inline and unnamed |

**Two of the narrowings are undeclared, and one fails with the wrong remedy.** `\d{1,2}` carries a comment that explains its `set()` dedupe and says nothing about the digit bound. `[DBCGR]` carries no comment at all — and day-b gaining a class letter outside it shrinks `row_ids()`, which fails `test_every_published_total_agrees_with_the_tables` with a message instructing the reader to *"re-derive both files together"*, i.e. to edit a published total to a wrong number. That is worse than a silent miss: it is a false alarm that prescribes the defect.

**The ticket's premise about the glossary was also wrong.** `CONTEXT.md` names five terms for this artifact and #413 says no module speaks any of them. At ratification, `test_ruling_cohort.py` held `GLOSSARY_TERMS`, asserted four of the five were present with an `_Avoid_:` line, and was the **only** module in `tools/` that opened `CONTEXT.md` at all. The honest form then was that one module asserted four of five were written down and none implemented any. That half was split out and is not this ADR's subject.

## Why the registry's convention cannot transplant

`tools/threshold_coverage.py` reads `reference/thresholds/coverage.md` with no identifier regex: a schema-marker gate, anchoring on the header row `| topic | state | artifact | record |`, cell-split with an exact width check, separator skipped by character-set test. It is padding-proof by construction, which is the latent trap all four row grammars sit on. Every threshold sheet and the registry carry a schema marker; **no `assertions.md` carries one.** A reader who meets the registry first will read the assertion side as the one that has not caught up.

It has not caught up because it cannot. **`coverage.md` is one table with a fixed header. An `assertions.md` is a document of many heterogeneous tables** — across the seven sets, **41 tables and 20 distinct header rows**, at 2, 3, 4 and 5 cells wide, with day-a holding 10 and day-b 13. The assertion rows are one family among them; the promotion tables (`| Successor | History | First verdict | ... |`) legitimately carry a row identifier in cell 0 as well, which is why `test_ruling_cohort` dedupes with a set. Header anchoring here would mean recognizing twenty headers, and a row identifier in cell 0 is the only stable handle the document offers.

Re-derive both figures with:

```bash
python - <<'PY'
import pathlib
hdrs=set(); tables=0
for p in sorted(pathlib.Path("fixtures").glob("*/assertions.md")):
    lines=p.read_text(encoding="utf-8").splitlines()
    for i,l in enumerate(lines):
        s=l.strip()
        if s.startswith("|") and s.replace("|","").strip() and set(s.replace("|","").strip())<=set("-: "):
            tables+=1
            if i: hdrs.add(lines[i-1].strip())
print(tables, len(hdrs))
PY
```

## Considered options

**Adopt the registry's convention for `assertions.md`.** The tidy answer, and the one a future reader will most want explained. Rejected on the measurement above: twenty headers and one row family appearing in two of them. It also costs a `<!-- schema: assertions/1 -->` marker in seven fixture files, and that cost grows with every set added.

**One shared reader over both artifacts.** Rejected because the key is not the same kind of thing. `coverage.md`'s key is a free-text topic cell derived from `reference/guidelines-catalog.md`; `assertions.md`'s is a two-token identifier. A `rows(text) -> dict[str, str]` general enough for both would be keyed on *whatever is in cell 0*, which is an abstraction with one real consumer and one specified one — [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s partial instrument, derived from the two files this session had open.

**Share a row fetch as well as the grammar.** Six modules fetch a named row and do it five ways — `line.startswith("| S4 ")`, `line.startswith("| C1 |")`, `re.search(r"^\| D2 \|.*$", re.M)`, `assertRegex(rf"\| R6 . {successor} \|")`, and one whole-file `assertIn` over normalized text. This was the recommendation until it was measured. **Every one of them fails loudly and with the correct remedy** — `assertEqual(len(rows), 1)`, `next()` raising `StopIteration`, `assertIsNotNone`, `assertRegex` — so unifying them is churn across six modules that closes no failure mode. The row grammars are different precisely because one of them fails loudly with the *wrong* remedy. A helper that costs six edits and prevents nothing is a line that costs a test.

**Leave all four grammars.** Rejected on `[DBCGR]` alone. The other three agree today, but two of them agree by accident rather than by a shared definition, and `test_blind_fixture_instructions`'s copy is inline and unnamed so nothing marks it as the reference spelling.

## Decision

`tools/assertion_record.py` holds one constant and nothing else:

```python
ROW_ID = re.compile(r"^\|\s*([A-Z]\d+)\s*\|", re.M)
```

It is the widest of the four spellings — any class letter, any digit count, tolerant of cell padding — and the four general extractors import it. Each keeps its own concern: `test_fixture_catalog` its `SET_DECLARATIONS` and denominator gate, `test_ruling_cohort` its `set()` dedupe, `test_blind_fixture_instructions` its `CLINICAL_ROW_HOMONYMS`. The six literal row fetches are untouched.

## Consequences

**The change is a verified no-op, so a green suite over it is not evidence.** All four grammars return the identical **129 distinct rows** across the seven sets today, `[DBCGR]` included — day-b's class letters are exactly `B`, `C`, `D`, `G`, `R`, no set has a three-digit row, and all 169 row lines pad the identifier cell with exactly one space either side. Every divergence is latent. `CLAUDE.md`'s extractor-coverage rule therefore binds: the claim may not be believed until the rule is fed a mutant. **Three planted cases ship with the change and must fail before it and pass after** — a day-b row under a class letter outside `DBCGR`, a three-digit row, and a padded identifier cell. Without them nothing in the tree can distinguish this change from doing nothing.

**#413's decisions 1 and 4 dissolved rather than were ruled, and that is recorded here so they are not re-opened.** Decision 1 asked where the line falls between parsing the record and grading it, against `test_ruling_cohort.py`'s standing *there is no scanner here and there cannot be one* and [ADR 0003](0003-a-ruling-cohort-promotes-when-fully-scored.md) behind it. A module that is one compiled pattern returning identifier strings cannot grade, so the line never has to be drawn. Decision 4 asked what happens to `fixtures/README.md`'s `Sets` column, whose denominators [#202](https://github.com/mshamblin5150-code/clinical-skills/issues/202) gated in `test_fixture_catalog.py`. That gate is untouched and the widening makes it **stronger**: a three-digit row becomes visible to the denominator check instead of invisible to it.

**The two conventions now coexist deliberately, and the next Markdown record will have to choose.** No general rule is stated here for which to pick, because there are exactly two instances to derive one from and they are one of each. The discriminator this ADR used — one table with a fixed header, or a document of many — is offered as the question to ask rather than as a rule that has been tested on anything.

**A schema marker for `assertions.md` is refused rather than deferred.** It would be the honest way to declare the row grammar in the file itself, and it is the first thing a reader will propose. The cost is an edit to seven committed fixture records to serve a reader, and `fixtures/README.md`'s standing position is that these files are evidence. Reversing this means paying that cost, which is what makes the decision worth recording.

*Corrected 2026-08-23: the glossary paragraph previously stated `test_ruling_cohort.py`'s uniqueness as current. [#444](https://github.com/mshamblin5150-code/clinical-skills/issues/444) later added `test_glossary_vocabulary.py`, a second module that opens `CONTEXT.md`; the correction dates the original fact and does not change this ADR's ruling.*
