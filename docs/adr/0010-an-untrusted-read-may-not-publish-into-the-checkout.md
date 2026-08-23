# An untrusted read may not publish into the checkout

Issue [#406](https://github.com/mshamblin5150-code/clinical-skills/issues/406) was filed
about the trace on `--allow-untrusted-provenance`: it is a `RuntimeWarning`, so
`PYTHONWARNINGS=ignore` silences it and the run exits 0. Its second decision asked the
wider question — whether the acceptance of distrust belongs recorded in the artifact
rather than only on the console.

Grilling it surfaced the instance the question was really about. `tools/uspstf_table.py`
defaults `--out` to `reference/guidelines-uspstf.md`, which is committed. So this works
today, and the committed table it produces says nothing about where it came from:

```
python tools/uspstf_table.py "C:/codeing/guidelines-text" --allow-untrusted-provenance
git add reference/guidelines-uspstf.md
```

The clinician ruled on 2026-08-22: **when the escape hatch is set, a write aimed at a
path inside any git checkout is refused.** The flag is documented as existing for
deliberate development work, and publishing a committed artifact is not development work.

## The arrangement

`artifact_provenance.refuse_publication(destination, *, allow_untrusted)` is a no-op when
the flag is off and `repo_root.ensure_outside_checkout` when it is on. `uspstf_table` is
its only caller today, because it is the only one of the flag-bearing commands that can
write into the repo at all: `guidelines_search`, `guidelines_catalog` and
`threshold_sheet` write nothing durable, `guidelines_index` is already guarded
unconditionally, and `guidelines_manifest` writes into the extraction directory, which
the extractor already refuses to place inside a checkout.

The refusal exits 2, on `docx_write.py`'s recorded rule that a writer's refusal is 2 and
there is no 1, because a writer has no *found nothing* to report.
[#303](https://github.com/mshamblin5150-code/clinical-skills/issues/303) ruled that the
command boundary owns what a shared refusal means for its run, so this is derived rather
than newly decided.

The precedent is [#383](https://github.com/mshamblin5150-code/clinical-skills/issues/383)'s,
one artifact over: *a dirty checkout may reuse a trusted build but may not publish a new
one*. `CONTEXT.md` now carries **Publish** as the term for the distinction the rule turns
on — writing inside a checkout, as against writing outside one.

## What is declared rather than built

`artifact_provenance.NOT_GUARDED` carries what neither the trace nor the rule reaches,
each row with its own reason. **This record deliberately copies no row of it**, and a
test asserts that of all three places the object is named -- here, the module docstring
and `CLAUDE.md`. A limit written as prose in several places fails nothing when it stops
being true, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241); the rows
themselves are the object's to state.

## Rejected alternatives

**Stamp the committed table instead.** Add a provenance line to `render_markdown` naming
the extraction, the commit and the untrusted reasons. Rejected because it records the
problem where the refusal prevents it, because it changes a committed artifact's format
and every consumer contract that reads it, and because this repo's posture on `output/`
and `scratch/` is already that a guard beats a record.

**Console trace only.** Rejected because it leaves the one committed artifact in the set
buildable from a dirty, foreign or unstamped corpus with nothing downstream able to tell.
Four currently-open tickets are arguing about the contents of that exact file.

**An AST completeness walk over every flag-bearing command.** Rejected as the predicate
#176 already refused: it would have to decide mechanically which commands "write," and
three of the six write nothing at all. Declaring the coverage is the standing answer where
widening the instrument would require a guess.
