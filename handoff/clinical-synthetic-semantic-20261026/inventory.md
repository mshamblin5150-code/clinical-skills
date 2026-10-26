# Synthetic-only portable qualification handoff

SOURCE PREPARATION ONLY. No upload/transfer, code execution, migration or install.
Cloud base reported61440f0d7a8a4c4fccf12c9a9404daf199c23e53, Python3.12.14/Git2.52.0;
local producer Python3.14.4. ClinicalWindowsreservation held. Windowsfrozen inputs
unchanged; no cloud equivalence or runtime admission claimed.

## Exact minimal code payload and provenance

candidate.py, harness.py, fixtures.py, failure_evidence.py, budget.py: unmodified
copies from git-qualification-maintenance-20261026, reviewed source manifest
72136e8e329fa7db134a27f408bdf3323c5a392d9a41976aca9be6214a898515. Total28537bytes.
These are agent-authored source, not clinician material. Fixtures create only
declared synthetic strings/dates/paths/identities (Synthetic Writer and
synthetic@example.invalid), not real encounters. Candidate and harness are code;
failure_evidence and budget are generic producers. No capturedrun output/data.
The accompanying inventory/manifest/tracked-verify-only.json are new agent-authored
handoff records, not account metadata. Eachactualfile size/hash/mode in manifest.

No surroundingworktree, .git directory, privategrant/frozen-inputpopulation,
scratch corpus, patient/name map, profile, uservoice/LMSdata, clinicaldocument,
database, secrets, credentials, runtime receipts/logs or Gitobjects are included.
No Windowsrunner/Job/monitor/nativehelper: probe.py, launch.ps1, frozen.py,
frozen-inputs.json, storage_monitor.py, owned_job.py, owned_process.py and
native_support.py are deliberately excluded. Do not recursively copy sessions.

Independentoracle tools/tracker_coordinates.py and its trackedimportclosure already
belong to verifiedbase. DO NOTTRANSFER those files; verify cloudbytes against
tracked-verify-only.json. OracleSHAec8b3e9c455b687a4fc68128b12bf7c526ef2e860a76d6243d50e07fa3377fbf.
Eachlistedlocalfile matched its retained frozen input digest duringpreparation.
No reset/rebaseline ofWindows frozenidentities. Cloudrawbyte mismatch, including
checkoutnewlineconversion, requires explanation and explicitreview, not silent
oracle replacement. No corpus is needed for the shownqualification limb.

## Private and tracked import boundary

qualify CLI: harness -> candidate; fixtures -> failure_evidence -> budget;
harnessreceipt -> budget. All other privateimports in this limb are stdlib.
Unreachable probe branch mentions code_set_database_reader_check/unittest20tests;
it is excluded frompayload because CLIadmitsqualify only and returns before it.

Tracked eagerclosure: tracker_coordinates -> console_codec/git_paths/prose_bind/
tracker_bodies -> tracker_records/tracker_scan -> phi_scan -> name_index/repo_root/
tracker_publish_marker; name_index -> corpus_census. All are verify-only source,
not corpusdata. console_codec's python_floor import is conditional commandfloor,
not normal in-process module.main. Recorded as optional verify-only dependency.
phi_scan has a lazy adr_supersession_population path, which is not exercised by
tracker_coordinates ADR/body qualification; do not widenpayload to unrelatedtools.
Importing phi_scan resolves scratch paths through repo_root; do not populate or
transfer those paths or call scanner/corpus entrypoints. Qualification calls
tracker_coordinates.main([], root=<freshsyntheticrepo>) and its graders only.

## Fixture construction contract

Exactly17CASES, all made fresh with exist_ok=False. Centralhelper's argv prefix:
git -c core.hooksPath=<fixture>/empty-hooks -c commit.gpgsign=false
    -c tag.gpgsign=false -c maintenance.auto=false <original arguments>.
Emptytemplate init --initial-branch=main; core.ignorecase=false; syntheticname/email.
Clear inheritedGIT_* for construction and set GIT_CONFIG_GLOBAL=os.devnull,
GIT_CONFIG_NOSYSTEM=1. No persistent maintenance setting, no tracker/oracleoverride.
Defaultauthor/committerdate2026-09-12T09:51:07+00:00; base09:51:05; equal09:51:06;
before09:51:05; skew latercommit2020-01-01T00:00:00+00:00. ADRcutoff09:51:06 UTC.
37explicitcommits, twomerge-createdcommits; conflictmerge expects1 beforeexplicit
resolution. Exactarg/data/branch/indexstage operations remain in fixtures.py.

Path.write_text UTF8/newline=None is preserved: LF onLinux vsCRLF onWindows.
Compare A/B within the sameLinuxfixture, not againstWindowsOIDs/workingbytes.
The literal rawindexfilename contains byteE9; filesystem/materialization effects
can differ. Record platform-specific outcomes; don't skiporweaken assertions.

## Complete26-check inventory and expected outcomes

Common17-case assertion: originaloracle andcandidate capturedpublicstatus tuple,
stdout/stderr AND ordered(pathbytes,date,selectedOID) population must be equal.
Publicstatus is relational: ('exit', code) OR capturedexception(type,message).
The source does NOT declare26fixed numeric publicexitcodes; none invented here.
The harness process itself mustexit0 and receipt.coverage equal allnames below.
No skip/xfail substitution. These rows state the actual declared controls.

|#|Name|Additional expected control/status|
|---|---|---|
|1|before|Nonempty routes; allfastpath; beforecutoff date preserved|
|2|equal|Nonempty routes; allfastpath; inclusivecutoff preserved|
|3|after|Nonempty routes; allfastpath|
|4|skew|Nonempty routes; allfastpath; nonmonotoniccommitterdates|
|5|rename|Nonempty routes; allfastpath; no rename-history shortcut|
|6|readd|Nonempty routes; allfastpath; deletion/readd sequence|
|7|directory|Exact docs/adr/a.md historicaldirectory route usesoracleFalse|
|8|staged|Commonparity; staged/notcommitted state unchanged|
|9|unborn|Commonparity; no basecommit created|
|10|missing-body|Commonparity; intentionallymissingworkingfile|
|11|pathspec|Commonparity; bracketpathspec semantics preserved|
|12|spaces|Nonempty routes; allfastpath; filenamewithspace|
|13|merge-same|Everyobservedroute usesunchangedoracle, notfastpath|
|14|merge-divergent|Everyobservedroute usesunchangedoracle|
|15|merge-conflict|Constructionmergeaccepted1, resolve+commit; everyrouteoracle|
|16|duplicate-index|Commonparity; stages1/2/3 retained as duplicatepathrecords|
|17|bytes|Commonparity; indexrawE9 path, no lossydecode|
|18|population|Injected GitPathError('synthetic'); same firsterror/outcome|
|19|last-touch|Injected SourceError('synthetic touch'); same outcome|
|20|body|Injected Path.read_text OSError('synthetic body'); same outcome|
|21|competing-failures|Firsttouch error wins over laterbody error identically|
|22|case-insensitive|GIT_ICASE_PATHSPECS=1 refusesfastpath for everyroute|
|23|acquisition-replacement|Replaced subprocess.run refusesfastpath|
|24|malformed-acquisition|Directtable returnsNone for malformed batchoutput|
|25|caller-patch-ownership|Callerpatch remainsidentical, calledexactlyonce|
|26|in-flight-patch|A/B firsterroroutcomes equal; newpatchnot overwritten, once|

Qualification receipt contains exactcoverage list, not necessarily26independent
results entries: someownership assertions are inline. Preserve that contract.
Commonparity alone can allow equalerroroutcomes; additionalfastpath/fallback
assertions boundtheclaim. Do not relabel thisinventory as broadersemanticproof.

## Exact CLI surface, not runnable admission

Actual existingargv (paths supplied by future cloudadmission, not invented here):
<cloud Python3.12.14> -B <private source dir>/harness.py qualify
  --checkout <verified cloudcheckout> --side B
  --release <private run>/release.json --admission <private run>

The filenames harness.py, release.json and admitted.json are existingcode names.
No cloudrunner/admissionproducer exists in thispayload; cloudabsolute paths were
not supplied, so no fullybound executable invocation isclaimed. Harness requires
release.runtime_authorized=true plus admitted.pid equal its realprocess and
sourcehashes. These files must come from authorizedactualcloudadmission; creating
them merelyto bypass thegate would not establish containment. No command ran.

## Separate portability/readiness needs — not implemented

Bind thispayload and existingcloudoracleclosure to an approvedcloudmanifest;
verifybytes/dependencies beforeimport andafterrun. Provide reviewedcloudnative
admission/cleanup and explicit observedlimits. No strictperrunaggregatecgroupPID/
storagequota iscurrently available perparent; WindowsJob/2GiB/4process/hardquota
equivalence isNOTclaimed. Any monitored-only resource policy needs an exactuser
decision beforeexecution, including overshootlimits/unknowns. Python3.12.14 vs
3.14.4 andGit2.52.0 must be recorded; no installs/upgrades inferred.

No semanticadaptation implemented. Source syntax/dependency/runtimecompatibility
has notbeen tested. Windows-mode metadata cannot supply POSIXexecbits: manifest
recordsactualWindowsattributes and nullPOSIXmode; proposedfuturewiremode0644 for
text is explicitly a proposal, not an observedmode/chmod. InvokePython directly.
LinuxPASS would not proveWindowsfilesystem/rawbyte behavior, nativecontainment,
sourcebuildidentity, matchedtiming or CIsavings. No automaticbenchmark/retry.
