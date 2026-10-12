# Paper language

Before first prose, read `PAPER-LANGUAGE` from the account's
`scratch/medatrax-profile.md`. If absent, empty, or duplicated, ask once which
language the clinician writes papers in, offering English first; resolve to one
answered `PAPER-LANGUAGE: <language>` line and save it before drafting. Reuse that
answer on later runs. English is an offered answer, never an assumed default.

For a single paper in another language, retain its explicit answer in the run as
`PAPER-LANGUAGE: <language>` and pass `--paper-language "<language>"` to
`tools/reference_scan.py`. The override wins over the profile; `--profile <path>`
selects a different account profile. For a Word course assignment, put the override
in `bar.md` or pass the same flag through `tools/course_assignment_scan.py`.

The paper's language chooses the filing alphabet, regardless of the cited work's
language or the author's name. Preserve the published name in entries and citations.
The committed `reference/reference-alphabets.json` carries English and the CLDR
rows named by [ADR 0356](../../../docs/adr/0356-the-paper-language-picks-the-filing-alphabet-and-english-files-a-special-letter-as-its-plain-letter.md).
The non-English rows use primary collation weights; national APA guides have not
confirmed them. Their fixed controls name the ICU and CLDR versions that produced
them. German awaits its own ruling. With no language answer or a language absent
from the table, ordering is `not graded`, with the language named, and a scan with
no other finding exits 2. A finding still takes exit 1.

Citation matching uses the table's English plain-letter folding in every language.
A match across different spellings carries `citation-author-spelling`: restore
the name as published rather than adding another reference or dropping the citation.
