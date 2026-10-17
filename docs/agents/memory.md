# Memory index filing rule

This is the tracked source of the rule that decides where a Claude Code auto-memory is indexed.
[ADR 0391](../adr/0391-the-memory-index-keeps-everywhere-rules-flat-and-files-situation-memories-under-generated-subject-lists.md)
records the rulings. `tools/memory_index.py` reads this file; edit the rule here, never in an
installed copy.

Claude Code loads one memory file into every session, the auto-memory index `MEMORY.md`, and stops
loading it at its line and character limits. Every other memory file is reached through a line in
that index. So a memory that applies in every session stays a **flat line** in `MEMORY.md`, and a
memory that matters only during one subject's work is listed in that subject's **subject list**,
which `MEMORY.md` reaches through one line per subject.

## Filing a memory

A memory belongs to a subject when it matters only while that subject's work is the task: a named
portal, tool, course, project, or kind of task. Everything else is flat, including a trap a session
can walk into without knowing it is in that subject's work.

Each memory file declares its placement in its own header, under `metadata:`:

```text
---
name: canvas-pause-in-box
description: "Load, switch to formatted view, show him, save only on his word."
metadata:
  type: feedback
  subjects: canvas, coursework
---
```

`subjects: none` keeps the memory flat. A memory that fits two subjects names both. A memory whose
header has no `subjects` line keeps whatever flat line it already has, which is how a line appended
under Claude Code's built-in instruction stays visible until somebody files it.

After writing a memory, rebuild the index from the clinical-skills checkout:

```bash
python tools/memory_index.py <path to MEMORY.md> --write
```

The rebuild writes every subject list and the flat part of `MEMORY.md` from each file's own
`description`. It keeps an existing line's title. A memory that fits no subject below stays flat until
an ordinary reviewed change to this file adds one.

## Subjects

| Subject | Name | Open when |
| --- | --- | --- |
| clinical | Clinical notes, coding, and Medatrax | the task writes or codes a clinical note, or enters one in Medatrax |
| coursework | Coursework writing and voice | the task drafts a case study, discussion post or reply, peer critique, or course assignment |
| canvas | Canvas and LMS posting | the task reads from or posts to Canvas or another LMS |
| research | Research sources | the task reads UpToDate, VitalSource, a textbook, or a statute |
| tracker | Tracker, pull requests, and the publish hook | the task files, comments on, or edits a GitHub issue or pull request, or merges one |
| adr-grilling | ADRs and grilling | the task grills a ticket or writes an ADR |
| side-projects | Axion, DAVID, and side projects | the task is Axion, DAVID, Open Brain, or another repository |

## When a memory was missed

When an after-action review finds a correction that an existing memory already covered, it promotes
that memory one step: a subject memory becomes flat (`subjects: none`), and a flat memory becomes a
tracked rule in `AGENTS.md`, a skill, or a reference sheet. Land the first as a `memory-write` and
the second through the review's `skill-file` or `check` disposition.

## Installed block

`python tools/memory_index.py <MEMORY.md> --write --install-rule` places the text below at the top of
`MEMORY.md`, between its marker lines; later `--write` runs refresh it. `{SUBJECTS}` becomes the
subject identifiers from the table above.

```text
Filing rule (ADR 0391): a memory that matters only during one subject's work gets `subjects: <subject>` under `metadata:` in its header, several allowed; any other memory gets `subjects: none` and stays a flat line. Subjects: {SUBJECTS}.
After writing a memory, run `python tools/memory_index.py <this file> --write` from the clinical-skills checkout; if you cannot, add a flat line as usual. Before a subject's work, open its list below.
```
