# Historical CPT descriptor correction pass

On October 11, 2026, the maintainer performed the private artifact correction pass requested by
[#1384](https://github.com/mshamblin5150-code/clinical-skills/issues/1384), following
[ADR 0269, ruling 8](../adr/0269-the-cpt-descriptor-set-is-rebuilt-by-two-readers-and-a-verified-flag-gates-it.md).

The pass searched the owning checkout's run and output trees against the retained defective
database descriptors, using the issue's stacking, doubled-separator, and trailing-colon predicates.
It matched exact descriptor substrings in readable text without requiring a nearby code token.
The dated census, producer, artifact paths, hashes, submission evidence, and correction records
remain private. Census counts belong on the issue tracker.

Each affected code received a fresh authenticated rendered-page reading of its descriptor and
shared stem in CPT Professional 2026, with the book, edition, and printed page retained. Each
affected run received a correction record identifying the defective code, its historical source,
its affected artifacts, and its corrected rendered-page descriptor. Submitted-run evidence was
preserved byte for byte. No active unsubmitted run was identified, so no worksheet repair or new
descriptor agreement was claimed.

Historical Review-sheet copies were associated with their owning run's entry evidence. Their
individual submission status has no artifact-hash posting bind; the correction records retain
that uncertainty and preserve every copy. They do not assert that every retained brief, backup,
or Review-sheet draft was itself submitted.

This was an exact-copy floor. Paraphrases, wrong-parent descriptors outside the issue's predicate,
unsupported formats, other Office package components, and untranscribed image text were not
cleared. A PDF refused by the text adapter was separately read, including its image-only covers,
and its reading was retained. The pass changes no clinical content, code selection, portal entry,
database, lookup, or agreement-brief implementation.
