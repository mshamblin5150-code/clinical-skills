# Classmate context command control

`project-context.md.in` is a synthetic positive-control record for ADR 0336.
It represents two reply keys with separate classmate posts, a shared board,
one retained attachment, and one explicit absence of attachments. It contains
no patient, classmate, or course text from a live run.

`tools/test_classmate_context.py` supplies temporary absolute paths and synthetic
file contents, then drives the public project-context and discussion-reply commands.
The passing record is the control for its missing, duplicated, unopened, wrong-key,
and changed-declaration variants. The pre-cutoff variant checks the ungraded
record count; the heading-read variants check own, shared, and other-key items.
