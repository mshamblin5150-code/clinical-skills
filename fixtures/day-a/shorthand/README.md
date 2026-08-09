# day-a — inputs

Ten encounters, one file each, transcribed from the day-file scan. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the scan, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## What was changed on the way across

Everything else is verbatim, typos included. The shorthand is typo-ridden by nature and the skill has to handle it, so `diminisnished`, `famliy hx`, `+ rosvig` and `hr 65 inches` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[SCHOOL]` | A named elementary school in cases 7 and 9. School plus age plus county narrows a child sharply — the same reasoning that removes the site name. Nothing clinical is lost; what mattered was school attendance and second-hand smoke exposure, and both survive. |
| `[7 days before visit]`, `[day of visit]`, `[11 days before visit]` | Absolute dates in cases 5, 8 and 2. The visit date is removed per [fixtures/README](../README.md), but an LMP is clinical content — case 8's LMP is the day of the visit, which matters. Replacing the token with its offset keeps the content and drops the identifier. |

Case 2's substitution keeps an inconsistency rather than resolving it: the shorthand dates the flu shot 11 days back and then calls it "1 week ago". Both are in the file. The skill should notice, not the transcription.

## Case 10 has no age and no sex line

Every other encounter opens `<age> yo <M/F>`. Case 10 goes from the name straight to `cc: feet pain`. This is a genuine gap in the source, not a transcription loss, and it is left in place deliberately — a real input the skill has to handle rather than one it never sees.

The portal supplies 25, male. Do not write that into the input file: an input that already answers the question cannot test whether the skill asks it.
