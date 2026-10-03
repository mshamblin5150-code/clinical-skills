# AAR row types

`claude.jsonl` is derived from the top-level main transcripts under the clinician's
Claude projects directory, excluding subagents. The derivation retains one row
per distinct top-level `type` and discards every other field. No text, identity,
path, date, site, or original row is retained.

`codex.jsonl` is derived from the counts-only census of active and archived Codex
rollouts. It retains one row per distinct top-level type or response payload kind,
keeping only `type` and, for response items, `payload.type`. All other fields are
discarded on the same terms as the Claude fixture.

Each fixture checks the named population against the unread counter. It does not
establish that the reducer reads nested content; that boundary remains in
`aar_scan.DECLARED_LIMITS`. The synthetic planted controls test liveness separately.
