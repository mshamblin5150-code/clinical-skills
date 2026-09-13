# A salted letter is folded only where observed as salt and the rest is counted

[#1025](https://github.com/mshamblin5150-code/clinical-skills/issues/1025) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2). Six code points survived
`tools/docx_read.py --normalize` on that run's **Evidence dump**, so a search of the normalized text
missed up to half of a term's occurrences and read as a settled negative. The ticket proposed adding
the six and asked whether to count what the fold leaves behind. Grilled 2026-09-13; the clinician
ruled every point below the same day. Nothing is built here; this is the record the build reads.

## Measured before ruling

Every figure below was counted on 2026-09-13 against the raw text of the 18 UpToDate dumps on the
clinician's machine, read with `docx_read` and no fold. The dumps are copyrighted faculty material
outside the repository, so nothing committed re-derives these counts.

### The ticket's six reproduce, and two more code points are salt

The six counts (U+057D 462, U+0405 203, U+0406 68, U+053C 47, U+0555 40, U+051D 15, total 835)
reproduce exactly on the Module 2 dump. The ticket's figure of 57 word forms reproduces under one
unstated rule only: fold the six, ignore case, and keep words that are then pure ASCII. Every other
rule tried gives 58 to 74. The dump holds 22 topic blocks rather than 21, and its run files are dated
2026-09-08.

The ticket called U+03F3 GREEK LETTER YOT genuine scientific notation. It is not. It stands for `j`
429 times across 7 dumps, inside English words, and occurs genuinely nowhere. U+0408 CYRILLIC CAPITAL
LETTER JE stands for `J` 20 times across 2 dumps.

### The map already corrupts genuine Greek

Occurrences of each Greek letter in `HOMOGLYPHS` were classified by position: beside a Latin letter,
beside only other substituted letters, touching only digits or hyphens, or standalone. Within each
position, occurrences were split into salt and genuine notation. An occurrence counted as salt
automatically when its folded word appears spelled in ASCII elsewhere in the 18 dumps. The rest were
read by hand. The automatically marked occurrences were not hand-checked one by one.

| letter | salt | genuine |
| --- | ---: | ---: |
| U+03B1 α | 0 | 4 |
| U+03BF ο | 9,898 | 0 |
| U+03F2 ϲ | 7,389 | 0 |
| the 14 Greek capitals drawn as Latin capitals, together | about 7,600 | 0 |
| U+03B5, U+03B9, U+03BD, U+03C1, U+03C2, U+03C3, U+03C5 | 0 | 0 |

The four genuine `α` are `TNFα-induced`, `α-tocopherol`, and "interferons α, β, and λ" in two dumps.
The fold turned each into `a`.

### No position rule separates genuine from salt

`TNFα` is genuine and touches Latin letters. `Ρ-selectin`, `Β2`, `Α1С` and `Τ1DΜ` are salt and touch
only digits or hyphens, exactly as the genuine `α-tocopherol` does. Only a per-code-point decision
has zero errors in both directions.

### The Evidence store never folds

`tools/uptodate_store.py` reads text files only. Its ingest copies the source byte for byte, records
its fingerprint, and never calls `docx_read.normalize`, so it relies on the caller having folded.
The index is rebuilt from the stored copies, which a later map change never re-folds. The stored
Module 2 copy still carries U+03F3.

## Ruling 1. A letter is folded only when it is observed as salt and never observed as real notation

The map stays a list of observations rather than a table of Unicode confusables, which would fold
glyphs nobody has seen in a dump. A code point observed both ways is kept as written: real notation
in a clinical source outranks search completeness, and ruling 5's count reports the letter.

## Ruling 2. The map gains eight entries

The ticket's six fold to `u`, `S`, `I`, `L`, `O` and `w`, U+03F3 folds to `j`, and U+0408 folds to
`J`.

## Ruling 3. The map loses eight entries

U+03B1 is removed on its four genuine occurrences. U+03B5, U+03B9, U+03BD, U+03C1, U+03C2, U+03C3 and
U+03C5 are removed because none occurs in any dump, as salt or as notation, and each carries real
medical meaning. The 14 capitals, `ο` and `ϲ` stay, because every occurrence of each is salt.

## Ruling 4. The docstring and the skill stop saying "letters only"

Two entries fold U+2010 and U+2011 to an ASCII hyphen. `tools/docx_read.py` and
`skills/practicum-case-study/SKILL.md` state ruling 1 instead.

## Ruling 5. Every fold prints a count of the non-Latin letters left behind

Every `--normalize` run writes to stderr each remaining letter whose Unicode name does not begin with
`LATIN`, with its code point, name and occurrence count. When none remains it writes a zero line.
Stdout carries only the document text, because the skill redirects stdout into the evidence file. The
exit status is unchanged, so the count reports and never refuses.

The zero line prints because a count missing from a clean run would read as the stronger claim, and
would look the same as an old version of the tool that never counted. Refusal was declined because
genuine `β` and `λ` are counted too, and a status that fires on real notation teaches a run to ignore
it. Accented Latin is excluded because it is never salt. Restricting the count to Greek, Cyrillic and
Armenian was declined because an allowlist of expected alphabets would hide the next one, which is
`symbol_glyph_census`'s reason for having none.

## Ruling 6. The Evidence store folds when it indexes, and never rewrites what it stored

The index is built from `docx_read.normalize` applied to each stored `source.txt`, and every query is
folded by the same object before it is matched. Stored copies and their fingerprints are untouched,
so the **Dump manifest** keeps recording the file actually filed. Every rebuild applies the current
map to every stored dump. Re-folding the stored copies in place was declined because it breaks that
provenance record. Leaving stored dumps unfolded was declined because it keeps the defect in the one
surface a later run searches.

## Ruling 7. Every index rebuild prints ruling 5's count per stored dump

A letter added to the map after a dump was stored, or one still missing from it, then shows up at the
next rebuild rather than only when a new dump is read.

## What this record does not settle

Whether any other reader of dump text needs the fold as well — the store's topic parser counting
author mastheads, or `research_ledger.py`'s evidence join over titles — is left to the build. Where one
does, it uses the same `docx_read.normalize` object rather than a copy of the map.
