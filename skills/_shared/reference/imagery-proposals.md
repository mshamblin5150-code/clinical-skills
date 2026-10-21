# Proposed imagery in coursework

This sheet owns the one exception to reusing only imagery the clinician supplied or the canonical
voice model records. When none of those images fits the argument, a drafting run may propose one
new image. It does not add a second image because the first worked, and it obeys the canonical
model's scale-and-consequence floor.

The proposal must come from a domain recorded under the canonical model's
`## Imagery` / `### The domains`. Copy the complete exact entry that establishes the domain into
`domain`: the `Domain` cell when the section uses a table, or the whole blockquote when it uses
quoted prose. A fragment, paraphrase, ordinary prose sentence, or quote embedded inside ordinary
prose is refused. The table therefore shows the recorded domain in the writer's own words rather
than a machine-created taxonomy. A domain outside that section is refused, never improvised.

Mark the proposed sentence in the working draft with an own-line
`[[PROPOSED IMAGE <key>]]` immediately before it. Create `<run-directory>/imagery-proposals.json`
with this exact envelope and one record per proposal:

```json
{
  "proposals": [
    {
      "key": "image-1",
      "artifact": "<terminal submission key>",
      "image": "<exact proposed sentence or sentences>",
      "domain": "<complete exact model domain entry>",
      "behavior": "<the real behavior the image spends>",
      "central_point": "<the exact point in this artifact's recorded-image match>",
      "status": "proposed"
    }
  ]
}
```

Once the draft is complete, stop before its first grade, carrier build, render or reader.
Show each proposal in its surrounding paragraph with its recorded domain and the real behavior
it spends, and ask yes or no separately from the later substance question. Show the recorded-image
match beside it: its central point, the recorded images weighed and why none fit. Retain that exact
point in the proposal's `central_point`. The clinician's verified yes settles the match for that
point, so the Voice reader skips only its new unused-recorded-image question. The existing planted
pair, supplied-voice and profanity populations remain owed. Historical proposals without the new
optional field retain their existing gates but establish no same-point skip.
In a deck the completed `.pptx` is the draft: generate it
first and take this stop before `deck_scan.py`; edit the deck to apply the answer. The Word
assignment's completed JSON spec is its draft before the DOCX producer.

This stop shows proposals, not the full draft, and is not a showing under
[Revisions](revisions.md). Retain no shown-draft copy for it. The first full go-ahead carries no
change list; later full showings compare against that full draft.

A yes changes `status` to
`proposed-and-approved`, keeps the exact image text, and removes only the working marker. A no
changes `status` to `proposed-and-removed` and removes both marker and image. An unapproved or
unanswered proposal stays `proposed` and blocks every grade over the draft.

On either answer, add this `ruling` object to the proposal. `shown_draft_at` is the draft's
modification time recorded before showing the proposal, never the time of the edit applying the
answer. `reply_at` is the clinician message's timestamp, and `clinician_reply` is that whole
verbatim message, including conditions. Both times accept a UTC ISO timestamp or Unix seconds.

```json
{
  "ruling": {
    "clinician_reply": "<whole clinician answer>",
    "reply_at": "<clinician message UTC timestamp>",
    "shown_draft_at": "<shown draft modification UTC timestamp>"
  }
}
```

The graders verify the whole reply against the clinician's transcript messages after the shown
draft time. Unreadable transcripts report `the image answer: not verified - transcript unreadable`
and incomplete coverage; readable messages that do not hold that whole reply at its recorded
time refuse. The check never uses the modified time of the draft after applying the answer.

## Reconfirm an approved image changed during repair

A repair may reword or remove an approved image without another mid-check stop. Keep `image`
as the last approved wording and add `changed_image` with the new exact wording, or `""` for
removal. Keep the original `ruling`. Pre-submission grades count the change without refusing it;
submission refuses a change still awaiting reconfirmation.

At the final go-ahead, show old and new wording as a separate image question. For
course-assignment this is Gate 1. A yes changes only the record: for a rewording, set `image` to
the new wording and keep `proposed-and-approved`; for removal, keep the old `image` and set
`proposed-and-removed`. Remove `changed_image` and replace `ruling` with the go-ahead's whole
reply, its time and the modification time of the draft that go-ahead showed. No rebuild, reread
or second ask follows that record-only confirmation. A no restores or removes the sentence;
rebuild every affected carrier, repeat the required render and its reader, heading and voice
reads, and take a new ask.

All six coursework graders run the image-stop check even without `--submission` and during
approval preparation. They report proposed, approved, unresolved and changed counts. They refuse an
unrecorded domain, an approved image absent from the artifact, a removed image still present, an
unresolved proposal, a surviving working marker, or a record not bound to the artifact. Only the
submission grade refuses a still-unconfirmed repair change. Earlier approvals use the check's
precise start in the completion-check registry and report not graded. Its complete coverage
boundary is `imagery_proposals.DECLARED_LIMITS`; coursework skills point to that object and copy no
row.

The JSON is also a co-writing record. If a later voice-model build or harvest treats a coursework
artifact as a writing sample, it reads the owning run's record and excludes every exact `image`
whose status is `proposed-and-approved` from attestation. `imagery_proposals.harvest_exclusions`
returns that population. The sentence may remain in the submitted work; it never becomes evidence
that the clinician independently wrote it.
