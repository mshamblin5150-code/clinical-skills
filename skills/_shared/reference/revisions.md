# Show a revised draft with its computed change list

Before showing a draft in `discussion-reply`, `discussion-post`, `peer-critique`, or
`practicum-case-study`, retain exactly the Markdown being shown. Keep one copy per showing,
including the first, under `<run-directory>/revisions/<key stem>/`; compute the stem with
`coursework_run.voice_records_directory(run, submission_key).name`. Use a new filename for each
showing and keep earlier copies. These copies are private working material.

The first showing needs no comparison. Before every later showing, compare the new copy with
the copy the clinician last saw, whoever caused the changes:

```bash
python tools/change_list.py <last-shown-copy.md> <new-showing-copy.md>
```

Show the command's complete output verbatim with the revised draft, including when it reports
no sentence changed. Exit 0 means the list was printed; exit 2 means a file could not be read:
repair the path or reading and rerun before showing the revision. After showing, that copy
becomes the last-seen version for the next comparison. Edits that were never shown do not
advance it.

The comparison boundary lives in `change_list.DECLARED_LIMITS`. It computes a change list;
approval does not refuse when a list was skipped. Keep the copies in the keyed subdirectory:
the run root's `response-*.md` files are graded as replies, so a showing copy there becomes an
extra reply.
