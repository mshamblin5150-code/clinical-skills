# Dedicated synthetic Windows compact validation

## Authority and isolation

This is a locally prepared validation packet, not publication or execution authority. It preserves the cleared compact implementation tree `658ccdae556c73508b38d8ab8c6ed39645d3af78` through the exact 30-file source pin map. The complete publication delta is against observer commit `05434f875f7e1af570335cff3f324d15e65c0fe7`, tree `9316da7140771a03f48fa60c8b9f261cccf05d8e`, not the sparse scratch HEAD.

Only `ci-compact-native.yml` admits the first push on the established diagnostic branch. Current parallel, threshold, reader, full-pair and discovery push/tag routes are disabled. Unchanged general workflows were read from their exact base blobs: checks `c3c7ca2e8abca1d42ad2d10b2585317184220c97` pushes only on main; tracker `98914a86441b38bc080a5e8bdbe6c3dfe0a66e80` has no push event. No PR, application/source clone, application import, suite, benchmark, automatic rerun, artifact upload, main/canary change or adoption is part of this route. The full observer checkout is read solely to authenticate its raw Git objects; its application code is never imported or executed.

One Windows X64 / Python 3.14.4 job has a 600-second ceiling. Origin is recorded before checkout and setup. Work ends at origin + 540 seconds; the final 60 seconds are reserved for process cleanup and finite terminal reporting. Planning blocks are 180 seconds setup/source authentication, 300 seconds controls and 60 seconds final verification, not completion guarantees. Controls are declined unless all 360 estimated work seconds still fit. No per-test or lock timeout is changed. Final cleanup uses the same remaining hard deadline, never a renewed reserve. The unchanged serial source Session retains its existing bounded five-second cancel/finish paths inside run; the native runtime and CheckpointSession final cleanup use remaining global time. The source-specific pre-launch gate requires every previous owner to report verified cleanup, a reaped root, zero active processes and closed state. Thus optional dirty-status diagnostics cannot launch after a poll/cancel uncertainty; unavailable diagnostics cannot replace the original first-status refusal. Only one source command or top-level native command is admitted at a time, and work expiry prevents another launch. These bounds reserve cleanup opportunity, not a guarantee an OS operation will return on time. A job timeout, absent terminal, failed cleanup, failed publication or post-publication deadline crossing cannot qualify.

## Executable population and interpretation

Thirteen core IDs, in fixed order, admit fourteen owned synthetic command pairs:

1. snapshot_share_receipt_success
2. replacement_identity_refusal
3. hardlink_refusal
4. reparse_refusal
5. before_first_mark_refusal
6. second_mark_partial
7. deadline_after_first_close
8. raw_close_partial
9. outcome_readback_partial
10. authority_recheck_partial
11. authority_close_partial
12. terminal_readback_unknown
13. coordinator_death_unknown (one outer coordinator and one owned inner output child)

Five direct-consumer IDs admit twenty-one further pairs: source_guard_success (6), source_guard_refusal (10: wrong HEAD 2, changed refs 2, dirty status 6), detached_expected_nonzero (1), outer_control_full_receipt (1), measured_original_outcomes (3). These reuse original source predicates, explicit final-consumer acknowledgments, original classification, runner and scheduler against owned fixed synthetic output. They are not Git or application qualification. The source driver separately uses real owned Git commands.

The core opens only newly created synthetic captures with the approved READ|DELETE, OPEN_EXISTING, FILE_SHARE_READ policy. Receipt writers remain the cleared receipt-only x+b handoff; their coherent read-only authority stays held through disposition. No ACL/share widening, DELETE_ON_CLOSE or path-unlink fallback exists. The negative authority probes attempt a denied WRITE open, DELETE open, replacement and deletion of that newly created held eligibility receipt. Unexpected native sharing success is failure, not permission to proceed. Unsupported hardlink/reparse prerequisites are inconclusive, never skipped or simulated native success.

The replacement fixture preserves content and LastWriteTime but not artificially identical CreationTime/ChangeTime. It proves native replacement refusal, not an isolated file-ID-only native proof. Independent eight-field/file-ID discrimination, root/report-directory replacement and byte-only mutants remain portable coverage. No metadata-write policy expansion is introduced. Native writer-close behavior is exercised by the actual cleared receipt handoff; a normal successful close need not demonstrate that Windows chose to change a particular timestamp on that invocation.

Expected injected partial/unknown store outcomes are successful *negative controls* only when their exact finite state, retained evidence and refusal of another pair match. They never qualify such a partial outcome for a comparison. A coordinator is stopped after its owned inner child finished and its first disposition mark was witnessed, before terminal evidence. The original eligibility receipt cannot establish that raw files still exist. Missing, corrupt, uncertain or incomplete terminal evidence means unknown retention; no destructive retry occurs. Process-cleanup and native-handle cleanup are independent requirements.

## Ownership, output and evidence

The driver uses one native runtime ledger: 34 top-level native owners plus one nested capture-pair reservation. Successful coordinator readiness and the owned Job's two-process count authenticate the inner launch; on failure, a reserved nested slot is not represented as proof of execution. Every original owner remains visible on launch, poll, finish or cancellation failure. Before another control, no observed native handle may remain open or uncertain. Final cleanup uses the original owner methods and reports uncertainty rather than retrying an uncertain native close.

There are 15 real source commands on success: first_clean 3; raw inventory 2 and verify_sources 4 before controls; raw inventory 2 and verify_sources 4 afterward. The source session caps commands at 18, conservatively allowing three dirty-status diagnostics. This is an allowance, not a claim that all eighteen can occur on a successful path. Native controls cap their pair admission at 35. Thus success is 50 capture pairs and the conservative packet ceiling is 53, including the inner pair. Every stream retains the existing 16 MiB cap. Source captures are retained. Consumer controls retain eleven intentional refusal pairs and retire ten fully acknowledged pairs.

Public output consists of bounded source diagnostics, environment identity, exact finite control IDs/counts, per-control wall time and hashes, and a finite terminal record. An aggregate 4 MiB public limit includes terminal reserve. No raw output, private fixture path or arbitrary exception text is public. Per-control private evidence is limited to 16 KiB; the assembled verified retained JSON is capped at 1 MiB. The terminal reports measured minimum free bytes, not inferred reclaimed space. Control wall times include fixture/child/receipt work and are not isolated disposition overhead or an application speedup measurement. The expected compact receipts contain their original owner timing/identity evidence; missing or refused receipts are not invented.

The final retained JSON uses the existing coherent retained-receipt reader. It is verified retained evidence, not a power-loss durability promise. Compact eligibility receipts separately use the cleared flush/fsync and held-authority protocol. Successful raw output that is disposed cannot later be reanalysed. Mark-plus-close does not prove secure erasure, absent pathname or reclaimed allocation. Existing historical evidence is untouched and raw captures are never uploaded.

## Storage admission

No volume capacity is assumed from the runner label. Both fresh evidence root and observer root must remain canonical non-reparse directories with the originally recorded device/file identities. Actual free bytes are checked before launches and during live polls. Evidence volume must retain a constant conservative 4 GiB of measured free space; observer volume must retain 1 GiB. On one volume these checks do not create an additional 1 GiB reservation. No disposal credit is added and no lower capture cap or fallback route is selected.

The 53-pair raw ceiling is 106 streams × 16 MiB = 1,778,384,896 content bytes (1,696 MiB). Compact records have a conservative 69 × 16 KiB = 1,130,496-byte content allowance. Additional content allowance is one coordinator-ready payload of at most 16 KiB, one final aggregate of at most 1 MiB, one private failure file of at most 64 KiB, and fixed fixture bodies of 37 and 17 bytes. The independent accounting receipt binds these source counts; pending ready-file rename does not create a second body. The remaining 4 GiB threshold is conservative planning headroom for the 1 GiB floor, small receipt/fixture allocations, interpreter/Git temporary activity and filesystem overhead. It is not a hard physical quota, a source-proved TEMP bound or a promise the runner can admit the packet. No clone or future checkout is performed after admission. Pre-existing checkout storage is already reflected in measured free space. Capacity failure is inconclusive, not authority to reclaim historical files or retry another route.

## Release boundary

Portable tests use only fresh disposable synthetic fixtures and injected owners/native APIs. They do not verify Windows behavior. Both independent reviews must bind the exact immutable publication tree and manifest before an approval request for one upload and one first-attempt ten-minute synthetic validation job. A passing native result, if later authorized, is not authority to run the held comparison or deploy an optimization.
