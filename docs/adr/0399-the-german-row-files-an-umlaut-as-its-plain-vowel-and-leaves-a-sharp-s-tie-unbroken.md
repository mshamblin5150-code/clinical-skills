# The German row files an umlaut as its plain vowel and leaves a sharp-s tie unbroken

**Measured at:** 2bb7eb69f88edd45b4582c28ba8d4a0b826d7fba

[ADR 0356](0356-the-paper-language-picks-the-filing-alphabet-and-english-files-a-special-letter-as-its-plain-letter.md)
made the paper's language choose the reference list's filing alphabet and left German without a row,
so a German paper was not graded on order.
[#1772](https://github.com/mshamblin5150-code/clinical-skills/issues/1772) asked which German filing
the row carries and where `ß` falls against `ss`. Grilled 2026-10-17; the clinician ruled both points
in that session.

## Measured before ruling

**The four guides were re-read, and two of the ticket's labels were wrong.** Each was fetched and
its text read; the quoted sentences are the guides' own.

- **Göttingen**, Institute for Educational Science, *Leitfaden* dated 2022-05-10, based on DGPs
  (2016), §3.1: „die Umlaute ä, ö, ü, äu werden wie die nicht umgelauteten Vokale a, o, u, au
  behandelt". Silent on `ß` and on ties.
  <https://uni-goettingen.de/de/document/download/2ec38b1e5e66cf19a4a72cfab3e8b5a1.pdf/Leitfaden_DGPs_Zitierrichtlinen_20220510.pdf>
- **FernUniversität in Hagen, ZitFit**, chapter 3, APA 7, undated: „ä wird wie a eingeordnet, ö wie
  o, ü wie u. Bei sonst gleicher Schreibung steht erst der Grundbuchstabe. Das Eszett wird
  eingeordnet wie ss. Bei sonst gleicher Schreibung steht ss vor ß." Its cited source for the rule
  is a typography blog, not APA or DGPs.
  <https://www.fernuni-hagen.de/public/zitfit/teil_1/kapitel3/>
- **Freiburg**, sport psychology, PDF dated 2009-01-05, based on DGPs (1997): „Umlaute ä, ö, ü, äu
  = ae, oe, ue, aeu". This is the guide that files umlauts as vowel plus `e`; the ticket attributed
  that rule to Göttingen.
  <https://www.sport.uni-freiburg.de/material/pdfs/institut/arbeitsbereiche/sportpsychologie/hinweise-zur-zitation-im-text-und-zum-literaturverzeichnis.pdf>
- **Erlangen-Nürnberg**, art education unit, 01/2021, based on DGPs (2019): umlauts as the plain
  vowels, and „ß wird behandelt wie ss, bei gleichlautenden Wörtern Einordnung vor ss". This is one
  department's guide, not the university's.
  <https://www.kunst.phil.fau.de/files/2024/05/richtlinien_wiss-_arbeiten_nach-dgps_und_formale_vorgaben.pdf>

**DGPs (2019) §9.1 was not read.** The publisher's free preview confirms the section, „9.1
Reihenfolge der Werke im Literaturverzeichnis", in its table of contents and stops in chapter 1.
No guide found quotes §9.1 by number.

**At the grader's strength, CLDR's standard German order is the plain-vowel order.** CLDR's `de.xml`
says „"standard" is the same as in root", and at primary strength root files `ä` as `a` and `ß` as
`ss`. The vowel-plus-`e` order is CLDR's separate `phonebook` collation. Measured with ICU 78.3 and
CLDR 48.0: under `de` at base sensitivity `Müller` equals `Muller` and `Straße` equals `Strasse`;
under `de-u-co-phonebk` `Müller` equals `Mueller`. German's DIN 5007-1 carries the same split as
two variants, dictionary order and name-list order (secondary sources; the standard is paywalled).

**A tie is never graded today.** Every row compares primary weights only, and the order row flags an
entry only when it sorts strictly before the one above it. `Straße` and `Strasse` therefore pass in
either order under every row, as do two names differing only by an umlaut once that umlaut files as
its plain vowel.

## Ruling 1 — the German row files `ä`, `ö`, `ü` as their plain vowels and `ß` as `ss`

The German row is CLDR 48's standard German collation at primary strength. `Göbel` files with
`Gobel` and before `Goebel`; `Straße` files as `Strasse`. The vowel-plus-`e` filing is rejected.

The plain-vowel filing is what both guides built on a DGPs edition of the last decade state, what
ZitFit states, what German's dictionary order does and what CLDR's German default does. The only
vowel-plus-`e` guide rests on the 1997 edition. Keeping German ungraded until §9.1 is read was
declined: the two current DGPs-based guides already agree, and the row would wait on a purchase.

The row is CLDR's, so the letters ADR 0356 ruling 2 folds for English follow CLDR here: `Ø` files as
O, and `Þ` sorts after Z, as in every other non-English row.

## Ruling 2 — a tie between `ß` and `ss`, or an umlaut and its plain vowel, is left unbroken

Two names that differ only by `ß` against `ss`, or by an umlaut against its plain vowel, may stand in
either order. The German row adds no secondary comparison.

The sources split on the `ß` tie: ZitFit and CLDR's root order put `ss` first, the Erlangen-Nürnberg
department puts `ß` first, Göttingen and Freiburg are silent, and DGPs is unread. Breaking it would
add a mechanism no other row has, to flag an order no authority agrees is wrong. APA also files by
the whole author element, so initials usually decide such a pair before the letter does.

## What the build does

- Add `de` to `tools/reference_alphabets_build.cjs`, with German control names, and rebuild
  `reference/reference-alphabets.json`. Every existing row rebuilt byte-identical.
- Accept `german` and `deutsch` as paper-language answers.
- Test that `Göbel` ties `Gobel` and files before `Goebel`, that a `Goebel`-then-`Göbel` list is
  refused, and that `Straße`/`Strasse` and `Raben`/`Räben` pass in either order.

## What this record does not settle

**What DGPs (2019) §9.1 says.** If it is read and disagrees, this row is revisited.

**Whether a German reader expects ties broken.** The ruling accepts either order; it does not claim
either order is wrong.

## Supersedes

- [ADR 0356](0356-the-paper-language-picks-the-filing-alphabet-and-english-files-a-special-letter-as-its-plain-letter.md)
  ruling 3, its words "**German has no row** until the clinician rules on umlauts and `ß`." German now
  has a row; the rest of ruling 3 stands.
