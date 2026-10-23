# Disposable replacement calibration only

This diagnostic route is explanatory, not native-control or production
qualification. The existing single diagnostic push workflow now passes
`--replacement-calibration` to the authenticated first-control driver. Its
calibration branch never invokes the original first control, the other seventeen
controls, an application or benchmark. Original strict false/error32 acceptance
and the original receipt-authority proof remain unchanged and unexecuted. All
other diagnostic workflows retain their disabled triggers. There is no new
workflow trigger/job or rerun permission. Publication and one hosted run follow
independent exact-tree review; the author executes only portable synthetic tests.

## Matched disposable comparison

Create an exclusive fresh directory with two exclusively created 37-byte files,
`target.bin` and `source.bin`. Their fixed distinct bytes are defined in the
calibration module. Writer native identities are sampled before writer closure;
reader handoff authenticates the same identities and exact bytes, allowing only
writer-close LastWriteTime/ChangeTime finalization. Writers and all extra observers
must close before replacement. Existing READ/shareREAD/native metadata behavior
is reused, never widened; readonly/hidden/system/temporary, unsafe type, multiple
links, reparse or delete-pending files refuse without attribute modification.

Hold the target fixture's own read authority. The existing public supplemental
proof authenticates fresh target/source names, exact contents, complete safe
native snapshots, same volume/distinct full FileIds and observed parent chain.
With only the fixture authority held, make one MoveFileExW(source,target,1) call.
A false result records its immediate last-error category but is not sufficient:
the held authority, both names and exact bytes must survive sampled poststate.
Unexpected success or any missing proof stops without resetting or retrying.

Only after verified held poststate, close this fixture authority exactly once.
No live receipt exists in this route. Uncertain closure stops subsequent
challenge/read work, while other still-owned handles may receive their one
cleanup close; an uncertain handle is never retried. Reobserve the same two
names/identities/bytes and parent chain, close all observers, then make exactly
one otherwise identical replacement call. A false result remains inconclusive,
regardless of error. True is necessary but not sufficient: a fresh destination
handle must identify the original source's full volume/FileId and exact bytes.
Coherent full safe snapshots are required before/after each read.

Only successful source-before/destination-after comparison permits ChangeTime
(st_ctime_ns) to differ. All other native metadata, including CreationTime and
LastWriteTime, must match. FILE_BASIC_INFO explicitly describes ChangeTime changes
for metadata operations such as rename:
https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_basic_info
This narrow allowed transition never applies to the held-denial/original receipt
proof. Source absence is a fresh non-following lstat observation accepting only
FileNotFoundError with ENOENT, surrounded by the same safe observed parent chain.
A dangling link, permission failure, missing/rebound parent, wrong destination
identity/content or incoherent snapshot refuses. This establishes sampled
namespace transition, not erasure, reclamation, continuous absence or a causal
claim excluding arbitrary concurrent actors.

## Evidence and failure semantics

The finite `replacement-calibration-v1` witness exposes held and released call
states/error categories separately, held poststate, positive namespace transition,
cleanup and overall status. Missing/malformed values are null/unknown. Raw paths,
IDs, bytes, attributes and exception strings never enter public projection.
Observation writes are best-effort, invalidate stale values and preserve original
exceptions, including a secondary cleanup failure. Native call/getter exceptions,
metadata/read failures and close uncertainty never qualify the comparison.

The distinct `compact_replacement_calibration_summary` is explicitly
calibration_only=true/native_control_qualified=false. A successful terminal needs
verified calibration, zero native owners/nested slots, verified source and final
receipt, both cleanup results and remaining hard budget. Existing first-control
`controls_verified` remains false and `control_count` remains zero. A calibration
failure never falls through into any original control. Failed fixtures and evidence
are retained, never path-deleted as cleanup. There are zero capture-disposition
calls; the second replacement intentionally replaces only the fresh fixture target.

## Exact unchanged ceilings

The existing 600-second job charges setup from before checkout, reserves 60 seconds
for cleanup and stops work at 540 seconds. Existing admission/free-space, capture
and public limits are unchanged. Calibration has zero native owned commands or
capture pairs; the authenticated source protocol still uses 15 successful source
commands within the existing maximum 18 source allowance. The previous conservative
19-pair/38-stream cap remains an upper bound, not a claimed execution population.

The two files have a combined peak of exactly 74 bytes. These bytes are explicitly
reallocated from the existing 1,048,576-byte final aggregate allowance, reducing
the actual encoded calibration receipt cap to 1,048,502 bytes. The executed receipt
boundary checks that identity and refuses cap/accounting mutations or cap+1 bytes
before writing. No extra standalone receipt is introduced. Existing unused native
capture/compact-receipt/fixed-payload reservations remain conservative allowances;
they are not reclaimed-space credits. Private logical-content ceiling remains
638,697,526 bytes and, including the unchanged 4-MiB public allowance, 642,891,830
bytes. Actual witness remains within 2 KiB and actual terminal within 4 KiB. These are
logical-content bounds, not physical disk quota or guaranteed admission.

Portable tests exercise actual synthetic namespace mutation, return-value lies,
source/target rebinding, exact identity/content and metadata discrimination,
observer/writer close failures, failed cleanup, finite projection, actual CLI
nonfallthrough and actual encoded receipt cap. They validate coordinator behavior
only, not Windows qualification or the cause of previous error5 observations.
