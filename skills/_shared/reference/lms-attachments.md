# LMS attachments

Read this sheet during the first live-page step of `course-assignment`, `discussion-post`,
`discussion-reply`, `peer-critique`, and `practicum-case-study`, before looking for or reading a
local **Faculty file** or **Classmate file**. [ADR 0324](../../../docs/adr/0324-a-faculty-or-classmate-file-is-identified-on-the-live-page-and-matched-by-fingerprint-before-a-run-reads-it.md)
records the ruling; [CONTEXT.md](../../../CONTEXT.md) defines both file populations.

## Identify on the page, then find the copy

1. Open the live assignment or board in the clinician's signed-in browser. Identify every linked
   Faculty file and Classmate file from the course site's own file record: its id, name, size in
   bytes, and `url`. For Canvas, read the linked file's record through the authenticated
   `/api/v1/files/<file-id>` endpoint. If the current browser fails, use another working signed-in
   browser to finish this step before searching the disk. An unread page stops file retrieval.
2. Compute the SHA-256 in the page from bytes fetched from that record's `url` with credentials.
   The measured route is the record's `url`, never the page's `/download` link, which redirects
   across origins and fails. A page evaluation uses the equivalent of:

   ```javascript
   const response = await fetch(fileRecord.url, {credentials: "include"});
   if (!response.ok) throw new Error("file response unavailable");
   const bytes = await response.arrayBuffer();
   if (bytes.byteLength !== fileRecord.size) throw new Error("file response size mismatch");
   const hash = await crypto.subtle.digest("SHA-256", bytes);
   return Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2, "0")).join("");
   ```

   Return the digest and byte count, keeping the file bytes in the page. When the page script cannot
   read the file, retain `sha256: null` and use the record's byte size as the identity fallback;
   note the failed page read in the assignment or board snapshot. A readable digest always takes
   precedence over size. The browser does not download or transfer file bytes: the clinician's
   Chrome prompts for a save location, and the browser tool cannot return bytes exactly.
3. Derive the first search location from this account's configured save location or browser
   download-directory setting. Search that location and the clinician's other usual save
   locations; if the account has no configured location, start at its OS Downloads folder. Compare
   candidate copies by SHA-256, or size only when the page digest was unavailable. A different
   filename is noted once and never stops a matching copy. If nothing matches, ask the clinician
   once to save the original file and say where, then apply the same identity test. A Word copy
   that was opened and re-saved is not the original bytes.
4. Record the matching path and its raw-byte local SHA-256 before reading its content. The local
   fingerprint also freezes a size-fallback copy for the later completion check. Read every
   matched file; unresolved files stop the live-source step.

## Posted files

After submission, identify each posted attachment from that entry's own course-site file record.
Follow [ADR 0350](../../../docs/adr/0350-a-posted-file-is-fingerprinted-in-the-page-and-never-downloaded.md):
fetch the record's `url` with credentials and compute its SHA-256 in the page with the script above,
returning only the digest and byte count. Compare the digest with the approved file: each filename's
Gate 1 fingerprint on `course-assignment`, or the local checked `.docx` on an attachment fallback.
On equality, read the local approved file; identical bytes are the same document. The run never
clicks a posted entry's Download link and never searches a download folder.

**Measured 2026-10-12, read-only in the clinician's signed-in Chrome:** the assignment route read
`/api/v1/courses/<course-id>/assignments/<assignment-id>/submissions/self` and its `attachments`;
the discussion route read `/api/v1/courses/<course-id>/discussion_topics/<topic-id>/view` and the
posted entry's `attachment` in `view` (including nested `replies`). Each attachment's
`/api/v1/files/<file-id>` record returned HTTP 200. Fetching each record's `url` with
`credentials: "include"` failed with `TypeError: Failed to fetch`, so neither page digest nor
comparison with the local posted file was available. No download or submission occurred. The
single-entry `/entries/<entry-id>` request returned HTML rather than a JSON record; use the
discussion `view` route. On these measured assignment and discussion surfaces, the
clinician-supplied route below is the only route. ADR 0324's successful faculty-file measurement
does not establish a posted-file route. A later successful measurement must record its date and
API paths here before enabling the page route for that surface.

When the page cannot read the file, ask the clinician once to save it from the posted entry's own
attachment link and say where. Copy that supplied file into `<run>/posted/<submitted basename>`
and compute its raw-byte SHA-256 with `python tools/file_digest.py "<run>/posted/<basename>"`.
Require equality with the approved fingerprint before reading it. A copy from the general files
area does not establish what the entry carries. There is no size fallback.

Before `/AAR` extracts the posted reading, write one line per submitted file using exactly one
of these forms:

```text
POSTED-FILE: <submitted basename> | sha256=<64 lowercase hex> | route=page
POSTED-FILE: <submitted basename> | sha256=<64 lowercase hex> | route=clinician-supplied | path=posted/<basename>
```

The completion grader compares each line with its approved fingerprint and re-hashes each
clinician-supplied copy. A missing, malformed, or unequal line, or an absent or changed supplied
copy, is a finding. The reader still records a substantive verdict about the document's content.
The grader cannot prove a `page` fingerprint came from the page: a digest copied from the approved
record passes, as declared beside the implementation.

## Attachment appendix of the sitting snapshot

The assignment or board snapshot links its attachment appendix at
`<run>/lms-attachments/<submission-key>.md`. This appendix is part of that sitting's snapshot,
not a record of the current live page. Use exactly the key passed to the scoped grader's
`--submission` option, including a reply's `.md` when that option requires it. For selected
replies from the same sitting, give each key its own appendix containing the same complete
linked-file population. Each subsequent sitting gets a new submission key and appendix; preserve
earlier snapshots and appendices.

For a page with no linked Faculty file or Classmate file, the entire appendix is:

```text
ATTACHMENTS: none
```

Otherwise write `ATTACHMENTS: files` on the first line, followed by a JSON list without a Markdown
fence in the saved appendix. Each file has exactly these fields:

```text
ATTACHMENTS: files
[
  {
    "file_id": "<course-site file id as a string>",
    "name": "<course-site file name>",
    "size": 0,
    "sha256": "<page SHA-256, or null for the size fallback>",
    "local_sha256": "<local raw-byte SHA-256>",
    "local_path": "<absolute path read, with JSON-escaped backslashes>",
    "location_source": "found",
    "test": "sha256"
  }
]
```

Replace `size` with the record's integer byte count. Use JSON `null`, without quotes, when the
page digest is unavailable and set `test` to `size`; otherwise `test` is `sha256` and both
fingerprints must agree. `location_source` is `found` or `clinician-supplied`, according to who
located the copy. Compute the local fingerprint with `file_digest.sha256(Path(<local path>))`.
Keep the appendix private in the run, alongside its snapshot.

## Completion

Before handoff, run `python tools/lms_attachments.py <run> --submission <key[,key]>`.
Exit 0 is required. The shared row `the LMS attachment identity` is also enabled by
`--submission` in all five scoped completion graders, through both artifact branches of
`course-assignment` and through `checks_ledger.py` for `practicum-case-study`.
It re-fingerprints the selected appendices' local copies against the sitting's retained size and
fingerprints. An absent or invalid record, unavailable local copy, or mismatch is a finding.
Without `--submission` the row is not graded. The check never re-reads the live page before
submission; the instructor owns revisions after the sitting opens.

The complete ceiling belongs to `lms_attachments.DECLARED_LIMITS`.
