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
      "status": "proposed"
    }
  ]
}
```

At the go-ahead, show each proposal in the skill's table and ask whether to approve it separately
from whether the artifact's substance is right. A yes changes `status` to
`proposed-and-approved`, keeps the exact image text, and removes only the working marker. A no
changes `status` to `proposed-and-removed` and removes both marker and image. An unapproved or
unanswered proposal stays `proposed` and blocks submission.

The terminal completion grader reports proposed, approved, and unresolved counts. It refuses an
unrecorded domain, an approved image absent from the artifact, a removed image still present, an
unresolved proposal, or a record not bound to the terminal artifact. Its complete coverage
boundary is `imagery_proposals.DECLARED_LIMITS`; coursework skills point to that object and copy no
row.

The JSON is also a co-writing record. If a later voice-model build or harvest treats a coursework
artifact as a writing sample, it reads the owning run's record and excludes every exact `image`
whose status is `proposed-and-approved` from attestation. `imagery_proposals.harvest_exclusions`
returns that population. The sentence may remain in the submitted work; it never becomes evidence
that the clinician independently wrote it.
