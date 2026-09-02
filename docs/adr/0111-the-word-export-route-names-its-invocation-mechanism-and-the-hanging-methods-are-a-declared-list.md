# The word export route names its invocation mechanism and the hanging methods are a declared list

[#768](https://github.com/mshamblin5150-code/clinical-skills/issues/768) was filed over
`tools/discussion_post_render.ps1` never returning from Word's fixed-format export, and was
respec'd on 2026-09-02 after a debugger attach found the caller blocked in a marshalled
`QueryInterface` raised by PowerShell's dynamic binder, with a typed late-bound call to the same
method exporting in under a second. Three decisions were declared open: whether to adopt the
late-bound invocation and where, whether the process bound belongs in a shared helper, and whether
[ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md)
ruling 5 is amended or annotated.

Grilled 2026-09-02. **Seven decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `4bc0658`

Freshness gate `FRESH` at both checkpoints. Four arms over one `docx_write` document, run
sequentially on the maintainer's machine with his authorization, in the tool's own invocation
shape — a Python parent, piped handles, `powershell -File` — bounded at 45 seconds with the owned
process killed by pid on every path. Zero `WINWORD` before each arm; machine verified clean after.

| arm | sequence | result |
| --- | --- | --- |
| **control** | dynamic `$doc.ExportAsFixedFormat2($pdf, 17)` | **HUNG** at 45 s, no output |
| **test** | typed late-bound export, then dynamic `$doc.Name`, `$doc.Close(0)`, `$word.Quit()` | **returned 0 in 7.1 s** |
| **namefirst** | dynamic `$doc.Name` **first**, then dynamic export | `Name` **211 ms**; export **HUNG** at 45 s |
| **sleep** | open, idle **8 s**, then dynamic export | **HUNG** at 45 s |

**The control reproduces**, which is what lets the other three be read at all. This route has
produced mutually inconsistent measurement sets on three separate days, so an arm that succeeds
means nothing without a hanging arm beside it in the same session.

**The ticket's stated cause is falsified, and the `namefirst` arm is what falsifies it.** The
respec'd body says the binder *"type-tests the COM wrapper before dispatching the method; that test
marshals a `QueryInterface` to Word, and it never returns."* That predicts every dynamic member
access on the `Document` wrapper hangs. `$doc.Name` is the first dynamic access on that wrapper, it
goes through the same binder on the same thread, and it returns in 211 ms — after which the very
next dynamic call, the export, hangs. The `QueryInterface` in the captured stack is real and is
genuinely where the thread is parked; what is wrong is the claim that any member would raise it.

**The readiness-window explanation is dead as well.** Eight idle seconds after `Open` — more than
five times the whole successful export — changes nothing.

**Option A is measured end to end rather than inferred.** The `test` arm is exactly the shape of
converting only the export: export **1,187 ms** and 111,677 bytes on disk, then `$doc.Name` in 8 ms,
`$doc.Close(0)` in **96 ms**, `$word.Quit()` in 9 ms, clean exit. `taskkill` returned 128 because
the process was already gone. The `finally` block's dynamic `Close` on the same object was the
open worry and it is not one.

**`$word.Documents.Open` was dynamic in all four arms and returned in every one**, between 369 and
395 ms, which is the same fact the ticket's original eight-attempt table records and is now
measured beside a per-method discriminator rather than alone.

## Ruled 2026-09-02

### 1. The route names its invocation mechanism, and that is the substance of this record

The two Word export call sites in `tools/discussion_post_render.ps1` invoke their method by typed
late binding:

```powershell
[void]$doc.GetType().InvokeMember("ExportAsFixedFormat2",
    [Reflection.BindingFlags]::InvokeMethod, $null, $doc,
    [object[]]@([string]$pdf, [int32]17))
```

The `[string]` and `[int32]` casts are load-bearing. An untyped `InvokeMember` returns
`DISP_E_TYPEMISMATCH` and writes a zero-byte file, which is a failure that does not hang and
therefore reaches a grader as a real export producing nothing.

**Option A, and options B, C and D are refused.** B converts working code on a hypothesis; C adds
a message filter or a retry, none of it measured; D keeps the clinician exporting by hand on every
submission indefinitely.

### 2. The predicate is per method, and the rest of the script stays dynamic

`Documents.Open`, `Document.Name`, `Document.Close` and `Application.Quit` are all measured
returning through the dynamic binder, three of them on the same `Document` wrapper that refuses the
export. **No rule is made about Word `Document` objects, or about COM, or about the binder.** Two
named methods hang and everything else measured does not.

**Converting the whole script was refused.** It would be a rule wider than its evidence, and #768's
own *what must not come out of this* forbids a blanket conversion by name.

### 3. The hanging methods are a declared list with its ceiling stated

The build carries a named tuple of the methods that must be reached by late binding, and a walk
over `tools/*.ps1` asserts each named method is invoked only through `InvokeMember`. **The ceiling
is declared in the object rather than in prose**: this holds a list of methods measured on one
machine, not a rule about COM, and a clean walk means no *listed* method was called dynamically.

This is `spelling_scan.py`'s arrangement adopted whole — an instrument that holds a vocabulary
rather than a language, saying so where the vocabulary lives. A third method nobody has hit is
outside it and the object says so.

**A predicate over every dynamic Word call was refused**, because ruling 2's measurements show it
would refuse four calls that work. A check that refuses correct code is the shape this repository
has declined suffix rules over, and it teaches the next author to route around the check.

**Declaring without checking was refused.** The conversion is two lines of PowerShell with nothing
holding them there, and `tools/` has no walk that reads a `.ps1` at all — these two scripts drive
the only external process this repository automates and are the least-checked files in it. That is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail*, landing on a call site.

### 4. `deck_render.ps1` is not converted, and the reason is a measurement rather than caution

`$presentation.SaveAs($OutputPdf, 32)` goes through the same dynamic binder against PowerPoint and
completes in 487 ms. Ruling 2 makes this stronger than *leave working code alone*: the failing
predicate is not the binder, and not the binder against an Office document object, but the binder
against two named Word methods. There is no near-miss here to pre-empt.

### 5. The ownership mechanism is shared, the bound is parameterized, and the method list is not shared

`tools/discussion_post_render.py` and `tools/deck_render.py` are independent re-implementations of
one mechanism: spawn, count the new process ids, refuse anything but exactly one, write
`<pid>|created` then `<pid>|opened`, and `taskkill.exe /PID /T /F`. **That much is shared**, on
`repo_root.py`'s precedent — it is one policy about one machine written twice, and the divergence
between the copies was never the point.

**The bound is a parameter of the shared helper and not a constant inside it.** The clinician
ruled on 2026-09-02 that `deck_render.EXPORT_TIMEOUT_SECONDS = 30` against the other's `20` was
typed rather than chosen, so the divergence is an accident — but a deck with many slides may
legitimately need longer than a three-page post, and one repository-wide number would forbid that.

**The method list of ruling 3 is not shared.** It is a Word measurement. Sharing it would either
walk `deck_render.ps1` looking for nothing, which is a green run that could not have failed, or
grow a PowerPoint entry on a hypothesis, which is ruling 4 refused through a back door.

This is [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test applied
rather than a preference: a shared helper is right where the copies encode one policy and wrong
where a test pinning their agreement would forbid a divergence the copy exists to permit. The three
parts of this mechanism answer that test differently and are split on the answer.

### 6. After the fix the bound guards ruling 3's declared residue, and that is why the two ship together

Before this record the bound was the only thing between a run and an unbounded spin — the recorded
instance reached 100,346 CPU-seconds on one thread. After ruling 1 the known hang is gone at the
two named methods, and export runs in about a second against a twenty-second stop. The bound is now
catching exactly what ruling 3's declared ceiling does not cover: a third method, a later edit, a
different machine.

**So the bound is not relaxed and not raised.** #768 forbids raising it and the reason survives
unchanged: where the call does not return there is no distribution to sit inside.

### 7. ADR 0087 ruling 5's rationale is falsified; its route stands and is completed here

[ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md)
ruling 5 states in bold that *"freshly spawned is load-bearing rather than hygiene"* and that what
differed between hanging and working calls *"was the process they were made in."* **That is
false.** The control arm above spawned a fresh process with no Word on the machine and hung, as did
#768's attempts 7 and 8. The variable is the invocation mechanism.

**Freshly spawned survives as hygiene**, which is not nothing: it keeps the automation off the
clinician's open document and keeps `Quit` off a shared instance. What it loses is the causal
claim.

**And ruling 5 was underspecified rather than merely mistaken about its reason.** It names a method
and its arguments and constrains only process state, so an implementer who follows it exactly
writes `$doc.ExportAsFixedFormat2($pdf, 17)` and reproduces the defect. `discussion_post_render.ps1`
is a faithful implementation of ruling 5. The record did not fail to be followed; it named the
wrong half of the route as the half that matters.

**Annotated in place and not rewritten.** ADR 0087 already carries a dated blockquote from the #676
implementation superseding four of its rulings with the original preserved beneath, and this takes
that form. **Amending ruling 5's text was refused**, because that rewrites decision history rather
than correcting it forward. **Leaving the bolded sentence standing as history was refused too**:
it is a live causal claim in a live ruling, and the next reader who needs to know why a fresh spawn
matters would read it and get a wrong answer.

## What this does not reach

**Why those two methods differ from the ones that bind.** Nothing here explains what the binder
asks for when it dispatches `ExportAsFixedFormat2` that it does not ask for when it dispatches
`Close`, or why Word does not answer it. The late-bound call is a measured workaround at one call
site and is not a diagnosis of Word, which is #768's own prohibition and is untouched by the
narrowing from per-object to per-method.

**Whether any of this is particular to one machine.** Every arm above is one machine on one day,
and this route has already produced three mutually inconsistent measurement sets across three days.
The control arm makes the comparison internally valid and says nothing about any other machine.

**Whether `SaveAs2` to XPS is fixed by ruling 1.** It is in the declared list and it is converted,
and #768 measures a typed late-bound `SaveAs2` to XPS at 869 ms — but no arm in this session
exercised the XPS path, so its conversion rests on the ticket's measurement rather than on this
record's.

**Any method not in ruling 3's list.** That is the declared ceiling, stated here so it is not
discovered later: a walk that passes establishes that no listed method was called dynamically, and
nothing about a method the list does not name.

**Whether the exported page is the right page.** Ruling 1 produces a page-faithful PDF and says
nothing about its content. The rendered-page verdict, its counted record and its kept pixels are
ADR 0087's subject and are unchanged by this record.

**`practicum-case-study`'s bounded export route**, which lives as prose in its skill with no
command implementing it. That is a separate finding, already filed, and folding it in here would
put a second skill's missing mechanism inside a record about one call site's invocation.
