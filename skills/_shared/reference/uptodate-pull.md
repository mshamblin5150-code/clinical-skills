# UpToDate puller brief

Give this whole file to every clinical or coursework UpToDate puller, word for word.

Use the Authenticated route. On UpToDate, an agent on the route may click the sign-in
form's own Sign In button when the clinician's password manager has already filled
every field. A signed-out page alone is not a completed read.

Before each search, run `outbound_search.py check` with its clinical words, run and new
search id. Type only after exit 0. Read the received query from the results page's
search box, address-bar `search=` parameter, or Showing results for line. Pass that
exact readback as `--query-readback` on `pull` or `failed-pull`. A mismatch records
`UPTODATE MISMATCHED SEARCHES`, including whether the sent words passed the identifier
check, and exits 2; search again with a new checked id.

Open the actual topic or drug page before declaring a failed pull. A failed pull uses
`failed-pull`, keeping `--decision` and `--instrument` and one `--reason`:

- `signed-out`: `--page-url` of the sign-in page and `--sign-in-tried yes|no`.
- `service-unavailable`: `--page-url` of the error page.
- `no-match`: the query readback and `--results-read` count.
- `page-unreadable`: `--page-url` of the opened page and `--second-method` tried.

For a drug page, click every Expand All on the page, including adult and pediatric
dosing, renal dosing, and the separate Pediatric drug information profile when relevant.
Inventory every indication control; continue until none is folded. Read each relevant
section's full text. Retain the ordinary whole-page pasted text privately. For filing,
also retain rendered HTML of the page's title heading, `#topicArticle`, and
`#topicVersionRevision`, in that order; this preserves the page's own section and
indication boundaries. Do not remove empty or folded indication controls. File that
live source with `uptodate_store.py ingest <source.html> --drug-page --read-on <date>`
and the ordinary dump-id/module/received-on arguments. The filing command refuses
folded indications or indications lacking dosing text. Plain clipboard text alone
cannot establish those boundaries and is refused as a live drug source.

A drug page is identified by its exact title, closing Topic / Version line, and read
date. Use `[uptodate drug: <page title>, version <N>, <dump id>]` on a proposed clinical
item. A filed drug page is current for one year from its read date; refresh an older
copy on use. Keep adult and pediatric page identities separate. Store search returns
the matched section, title, version, and read date. Coursework cites a filed drug page
in APA's drug-information form, `n.d.`, with a retrieval date; see apa7.md section 21.

A drug page fills a gap and never overrides a threshold sheet. If it disagrees, pull
the clinical topic. Only a topic that settles the conflict can win; otherwise the
sheet stands. Record the drug live pull with `--sheet`, `--row`, `--difference` and
`--sheet-kept`; `UPTODATE CONFLICTS` must show the disagreement as sheet kept.

A drug page in a handed-over coursework dump is left out of the Titled copy. Record
its exact title and the reason for the drop in the block-to-title mapping. Pull it
live through this brief if needed; a handover establishes neither its read date nor
its expanded indications.
