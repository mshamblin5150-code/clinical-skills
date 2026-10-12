# The paper language picks the filing alphabet and English files a special letter as its plain letter

**Measured at:** 5433dba9749b5d0109c6b490abd502fb7505a5c0

[#1568](https://github.com/mshamblin5150-code/clinical-skills/issues/1568) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. `reference_scan`
sorted a surname beginning with a slashed O after every entry beginning with Z, the run left the
entry last in the submitted list, and later readers were briefed to accept it. The ticket left one
decision open: whether filing follows the English rule for every such letter or keeps source-language
order where the reference is not in English. Grilled 2026-10-12; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The defect reproduces on `main`, and it is wider than the ticket's list.** At the measured commit,
`reference_scan.ordering_text` keeps the first letter of `Øvretveit`, `Æsop`, `Łukasz`, `Ðor`,
`Þórsson`, `Œuvre` and `Đorđević` unchanged, and each compares greater than `Zhang`. `Œ` and the
Croatian `Đ` were not on the ticket. `Straße` already folds to `strasse` through `casefold`, as the
tracker sweep recorded on 2026-10-11, and `Öberg` and `Kübler` already fold, because NFKD decomposes
them. The cause is the one the ticket named: these letters carry no Unicode decomposition, so
stripping combining marks leaves them in place and they sort by code point.

**The matcher has the same gap, which the ticket did not name.** `reference_scan.normalize` uses the
same NFKD step, so a citation written `Ovretveit` does not match an entry listed `Øvretveit`. The
grader then reports one citation with no entry and one entry never cited.

**APA's manual is silent on these letters; APA's practice is not.** ADR 0151 ruling 7 already
recorded §9.44 and Figure 9.2 as silent on diacritics. Two research passes in this session, each
checked by the orchestrator before it was believed, found the following:

- APA Style's 2010 blog post *Alphabetization in APA Style* (archived copy, read) says to
  "Ignore spaces, capitalization, hyphens, apostrophes, periods, and accent marks."
- APA's own journal *Emotion* (2014, doi:10.1037/a0037225, publisher XML parsed) runs Muris,
  Öhman, Olsson, Öst, Pine: both `Ö` names file under O. Author manuscripts in five more APA
  journals file `Ø`, `Ö` and `Å` names under their plain letters; none sits after Z.
- Yale's library filing table, derived from the Library of Congress shelflisting rules, files
  `ø` as O, `æ` as AE, `ð` as D and `þ` as TH.
- Unicode collation (UTS #10, and CLDR as ICU applies it) files these letters under their plain
  letter for English and moves them to their home positions for Danish, Norwegian, Swedish,
  Icelandic, Polish, Czech and Turkish. Under English CLDR `Þ` alone sorts after Z.
- Zotero sorts by the bibliography's language setting. Its developer wrote on the Zotero forums
  (comment 346153) that "a paper in English would not sort Ø after Z", and that a Danish
  bibliography would.
- National APA adaptations almost all say only "alphabetical". Aalborg University's Danish guide
  orders "A to Å", the paper's own alphabet. Bifröst's Icelandic guide keys the name form on the
  cited work's language. German guides disagree with one another on umlauts and `ß`. **No guide
  found keys ordering on the origin of the author's name.**

**No skill uses a citation manager.** No skill or tool drives Zotero, EndNote or Mendeley; the drone
writes the reference list directly, so the drone and the grader are the only sorters in play.

## Ruling 1 — the language of the paper decides the filing alphabet

The alphabet a reference list files under is the alphabet of the language the paper is written in.
It is not decided by the origin of a cited author's name, nor by the language of the cited work.

A name-origin rule had no supporting source and was withdrawn in the session. A cited-work rule
splits one author's works across the list when they publish in two languages, which breaks the
same-author grouping APA requires. The paper-language rule is what APA's journals, Zotero and the
Unicode standard do. It is also what lets a clinician who writes APA in another language use these
skills in that language.

**The printed entry never changes.** The name is printed exactly as published, special letter
included, under every ruling here. The filing alphabet decides only where the entry sits.

## Ruling 2 — an English paper files every such letter under its plain letter, and Þ as "th"

The English row folds a letter with no Unicode decomposition to its plain filing letters: `Ø` and
`Œ` to O and OE, `Æ` to AE, `Ł` to L, `Ð` and `Đ` to D, `Þ` to TH, and dotless `ı` to I. Letters that
NFKD already decomposes (`Ö`, `Å`, `Ä`, `Ü`, `Ñ`, `Č`, `Ş` and the rest) keep their current folding,
and `ß` keeps its `casefold` to SS. The folding applies at every position in the name, not only the
first letter, because §9.44 compares letter by letter.

`Þ` follows library practice rather than English CLDR, which sorts it after Z. That keeps the English
row to a single principle. The cost is accepted: a list built in a citation manager would place a
`Þ` name after Z and the grader would name it as misplaced. The build cites each row entry's source.

## Ruling 3 — a committed table holds each language's alphabet, and an absent row is never guessed

The filing alphabets live in one committed table. The grader reads the paper's language, looks up
that language's row, and compares in that order. A language without a row is not graded: the order
row reports `not graded` with the language named, and the command takes its did-not-scan status. A
finding established on the same run still wins.

The first table carries English (ruling 2) and Danish, Norwegian Bokmål, Swedish, Finnish, Icelandic,
Polish, Czech, Turkish and Spanish. Each non-English row is taken from the CLDR collation data for
that locale, cites the CLDR release and file it was read from, and covers what that data says,
contractions included where CLDR defines one (Danish and Norwegian `aa`, for example). No national
APA guide confirms these rows, and the record says so beside them.

**German has no row** until the clinician rules on umlauts and `ß`. German universities' APA guides
disagree: one files `ä` as A, another as AE, and two disagree on whether `ß` precedes `ss`. A German
paper is therefore not graded on order until that ruling lands.

## Ruling 4 — the paper's language is asked once, saved in the profile, and overridable per paper

The paper's language is an account setting. `setup-clinical-skills` asks for it in the same step as
the title-page and clinical credentials, and records it in `scratch/medatrax-profile.md`. English is
the answer the question offers first; it is never a value the grader assumes. Each skill that runs
`reference_scan.py` asks once before drafting when the saved answer is missing, on the same pattern
the credentials use. A single paper written in another language carries an explicit override on
that run.

The grader takes the language from the override when one is given and from the profile otherwise.
With neither, the order row is `not graded` under ruling 3.

## Ruling 5 — a citation matches its entry across the folding, and a spelling difference is reported

Citation-to-entry matching folds these letters the way ADR 0151 ruling 7 already folds accented
ones, in every paper language, so `Ovretveit` in the text and `Øvretveit` in the list are the same
author. Where the two spellings differ, the grader reports a new finding that the citation spells the
author differently from the reference list. The same finding covers the accented letters ADR 0151
already folds, so `Kubler` cited against a `Kübler` entry, which passes silently today, is reported
too.

APA prints the name as published in the text as well as the list, so the misspelling is a real
error. Refusing the match instead would turn a typo into a missing reference and an uncited one,
which ADR 0151 ruling 7 measured and rejected.

## What the build does

- Fold the English row's letters in `reference_scan`'s ordering and matching keys, with the table as
  the one source both read.
- Add the per-language table with its cited sources, the language input, the `not graded` path, and
  the spelling-difference finding.
- Add the paper-language question to `setup-clinical-skills` and the ask-once step to each skill
  that runs `reference_scan.py`, with the override described where the command is.
- Test with a slashed-O surname filed among O entries in English and after Z in Norwegian, a `Þ`
  surname filed among the Th's in English, an unsupported language, a German paper, the override,
  and a `Kubler`/`Kübler` citation.
- Fix the ordering controls each non-English row is tested against at build time from ICU, and name
  the ICU and CLDR versions beside them, because the suite has no collation library to call.

## What this record does not settle

**Whether the CLDR rows are what a reader of those languages expects.** They are the only published
order found, and no national APA guide confirms them.

**The German row**, which waits for its own ruling.

**Whether another grader orders reference lists.** The build checks for one and applies the same
table if it finds one.

## Supersedes

- [ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) ruling 7,
  its words "Folding is what letter-by-letter comparison means." Folding is what letter-by-letter
  comparison means in an English paper; the paper's language now picks the alphabet. Its
  elimination of code-point order and its acceptance of folded equality still stand.
