# UpToDate topic sheets

These are publisher-keyed distillations of topic bodies the clinician deliberately supplied. Raw
dumps, per-dump manifests, and the FTS5 index stay under `scratch/uptodate/`; a sheet contains only
the bibliographic record and a short restatement. One topic has one file even when several dumps
carry it.

At intake, ask whether the supplied dump came with a separate reference list. Pass one with
`--references <file>` so its bytes and digest remain beside the dump for the future primary-source
join; omitting it records no list and claims no join. Run `python tools/uptodate_store.py ingest ...`
before authoring a sheet. Use the source's own
`SUMMARY AND RECOMMENDATIONS` as the selection boundary. Where none exists, compress the whole
article and declare `DISTILLATION-BASIS: whole article`. The normal restatement is 400–550 words.
Exact source language is reserved for a number, dose, criterion, or cut point whose wording is the
honesty mechanism. Standing rule 5 still applies: no current exact figure from this gitignored
source reaches a sheet unless a tracked source and equality-backed test can support it.

Every sheet carries these fields exactly once:

```text
AUTHORS: <the topic author line>
TITLE: <the topic title>
APA-YEAR: <year from This topic last updated>
LITERATURE-REVIEW-CURRENT-THROUGH: <YYYY-MM>
RETRIEVED: <YYYY-MM-DD for the read that produced this sheet>
URL: <the https://www.uptodate.com/contents/... page actually opened>
DUMP-ID: <the manifest's dump id>
DISTILLATION-BASIS: summary and recommendations | whole article
FAITHFULNESS-READING: completed against the summary and recommendations | completed against the whole article
```

`python tools/uptodate_sheet.py --all` grades those fields against the gitignored source manifest,
checks retrieval chronology and URL shape, and measures the exact-language cap. It counts exact
runs of at least five words and refuses more than 10 percent of the restatement or 60 words,
whichever is reached first. Its complete mechanical limits live in
`uptodate_sheet.DECLARED_LIMITS`; faithfulness remains a reading despite the required declaration.

The sheet's retrieval and currency fields belong to the read that produced it. A later citation
inherits those fields and never implies that the page was freshly opened. `research_ledger.py`
uses the signed UpToDate window and the profile's `UPTODATE-ACCOUNT` answer to decide when another
authenticated read is required.
