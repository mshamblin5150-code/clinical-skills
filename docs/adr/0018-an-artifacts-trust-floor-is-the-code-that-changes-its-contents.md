# An artifact's trust floor is the code that changes its contents, and its cache key is broader

[#443](https://github.com/mshamblin5150-code/clinical-skills/issues/443) recorded that an uncommitted edit to `tools/guidelines_index.py` turns `tools/test_guidelines.py` red 31 ways, with a message naming provenance rather than the working tree. Grilling it on 2026-08-23 found the ticket's diagnosis correct, its premise too generous, and its scope narrower than the defect.

The clinician ruled on 2026-08-23.

1. **Trust is content identity, not session identity.** An artifact records the sha256 of the code that produced it, and a reader compares hashes rather than inferring from a commit.
2. **There are two lists per artifact kind and they are named apart.** `CACHE_IDENTITY` decides whether a content-addressed build hits or misses; `TRUST_FLOOR` decides whether a found artifact may be believed. The superset relation between them is asserted rather than left to hold by luck.
3. **`TRUST_FLOOR`'s membership rule is: files that change what the artifact contains.** A file that changes only how an artifact is *stamped* is excluded.
4. **A refusal says which condition it is.** An artifact recording no producer-file identity at all is named as predating the scheme; a difference that is uncommitted in the working tree is named as such.

## The premise the ticket held fixed, and why it does not hold

#443 states, in its own words, `the behaviour is right and the moment is wrong` and offers three remedies that all leave the check's verdict alone — add a clause to the message, skip the suite, or write a paragraph.

[#184](https://github.com/mshamblin5150-code/clinical-skills/issues/184)'s rule is that an artifact stops being trusted when its producer changes, and that is plainly right about an artifact **somebody else built earlier**. The artifacts `test_guidelines.py` fails on are not that. `TempCorpus.setUp` builds an index into a temp directory out of the working-tree code, in that process, and the check then reports that the producer has changed. It has not changed since the build — it *is* the build.

The check reaches that verdict because `commit` is a lossy stand-in for *which code built this*. It can name a commit and nothing finer, so it cannot distinguish **your edit landed after the build** from **your edit was the build**. `_paths_unchanged` shells `git diff --quiet <commit> -- <paths>` with no second commit and no `--cached`, which compares the recorded commit against the working tree, so both cases produce the same answer.

So this is not a true warning arriving at an awkward time. It is one question being asked with an instrument that cannot separate two cases, and the fix is to ask it with one that can.

## What was measured

Every claim below was re-derived on the merged tree at `9389070` before the ruling.

**The content-hash path is already built and already working on one path.** `_content_inputs` hashes each recorded producer file and, when every hash matches and the recorded path set covers the reader's `unchanged_paths`, suppresses **both** the commit-mismatch reason and the producer-changed reason. `guidelines_build._trusted_producer` records those hashes; `guidelines_index_artifact.stamp` writes them into the database. `tools/test_guidelines_build.py` is immune to #443 for exactly this reason. This ADR does not invent the mechanism, it extends it to the producer that lacks it.

**`guidelines_index.build` records no such identity.** `current_producer()` returns `{"commit", "dirty"}` and nothing else, so `inputs_match` is `None` there and both commit branches apply.

**The ticket understates its scope in two directions.** It is not test-only: an ordinary `python tools/guidelines_search.py` from a working clone refuses with exit 2 on the same condition. And the sibling instance is a **different call site** — `guidelines_manifest._read_locked` passes `unchanged_paths=("tools/guidelines_extract.py",)`, and every manifest read funnels through it, so a dirty extractor reddens the indexer's suite, the catalog's, the USPSTF builder's and the threshold sheet's. A remedy scoped to `check_derived` reaches none of that.

**There are three producer-file lists, not two, and they answer different questions.** `guidelines_build.index_identity` names four files, `extraction_identity` names three, and the two reader call sites name one each. The readers' singletons are values nobody derived — they are what was typed at a call site. The superset check means the writer's list and the reader's list are already coupled, and nothing compares them.

## Considered options

**Add a clause to the message and leave the verdict alone** — #443's decision 1. Rejected as the whole remedy and kept as part of one. It leaves the suites red for the entire interval anybody is editing those producers, which is the interval anybody working on them is in, and it leaves the consumer-facing search command refusing.

**Skip the suite from a `setUpModule`** — #443's decision 2. Rejected. It would have to live in five test files keyed on two producer paths, and this repo treats a partial run as reading like a pass; [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86) records a class that skipped in part and passed for the wrong reason.

**Document it and change nothing** — #443's decision 3. Rejected. A prose claim fails nothing when it goes stale, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220), and the condition would still fire.

**Exempt an artifact built in the same run.** Rejected. It buys the same green with a claim nothing can check afterwards — an exemption keyed on the session is invisible to a reader the moment the artifact outlives the process, where a hash is re-derivable in one command.

**One shared list serving both questions.** The tempting symmetry, and rejected twice over. A cache key wants to be broad, because a change to `artifact_provenance.py` *should* miss and rebuild and the cost is a rebuild. A trust floor wants to be narrow, because if it were broad then editing `artifact_provenance.py` would distrust every index in existence — which is #443's own defect at maximum blast radius, landing on the module this fix is written in. Fusing them buys the fix by reintroducing the bug one file over. This is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s ruling: two lists that look alike but exist to permit different answers are not one object, and a test pinning their agreement would forbid the divergence the split exists to allow.

**Freeze the readers' current singletons as `TRUST_FLOOR`.** Rejected. They were never derived, so the table's rows would be a value with no principle behind them and the next module added to a producer would have no rule saying whether it belongs. Deciding membership on *does this change what the artifact contains* puts `guidelines_manifest.py` on both rows — the manifest reader supplies the society, title and class that go **into** the database — and leaves `artifact_provenance.py` and `guidelines_index_artifact.py` off, because neither changes a byte of what the artifact says about the corpus. That is a widening of the current floor, not a narrowing, and #184 is not reopened.

**Rebuild automatically when an artifact records no identity.** Rejected. An artifact that cannot say what built it is exactly the artifact #184 exists to distrust, and silently rebuilding a 61 MB index under a command that asked to search is a side effect nobody requested.

## The cost this accepts

**Nothing on disk is fixed until it is rebuilt.** Every index and manifest already written carries `{"commit", "dirty"}`, so the day this lands the condition still fires everywhere until somebody rebuilds. This is why the refusal has to name *records no producer-file identity* as its own reason rather than reporting `producer code has changed since the artifact was built` — otherwise the fix arrives invisibly and the person who hits it learns nothing new.

**Build-then-edit-then-read still refuses, and that is the point rather than a residue.** The scheme sorts the two cases the commit proxy conflates. Edit, then build, then read passes, because the code on disk is the code that built it. Build, then edit, then read refuses, because the code really did change since the build. A remedy that made both pass would be suppressing a true finding.

**A published index is trusted across a stamp-only edit.** Under the content-versus-stamp line, editing `artifact_provenance.py` no longer distrusts an index read directly by `guidelines_search`; it changes the cache key, so nothing stale can arrive *through the cache*, but an artifact published earlier and read at its compatibility path is believed. That is the deliberate consequence of deciding trust on contents. The alternative reinstates #443 in the provenance module itself.

**Sharing the object is necessary and not sufficient.** [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218) records an identity test passing while `reference_scan` and `docx_write` still disagreed about where a reference list ends. So the pin is the hand-off — a real build in a throwaway checkout, an uncommitted producer edit, a real read — with the table test beside it and the mutants driven red before either is believed. A test that only drives the index leaves five suites' worth of the same defect unpinned while reading as coverage.
