"""Install the VitalSource attachment boundary in Codex Chrome."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


ORIGINAL_DOMAIN_GATE = 'JG.has(r)||YG.has(e)'
PATCHED_DOMAIN_GATE = '(JG.has(r)&&e!=="Target.setAutoAttach")||YG.has(e)'
ORIGINAL_PARAM_GATE = 'case"Tracing.start":return iK(t);default:return!1'
LEGACY_PATCHED_PARAM_GATE = (
    'case"Tracing.start":return iK(t);'
    'case"Target.setAutoAttach":return t?.autoAttach!==!1||'
    't?.waitForDebuggerOnStart===!0;default:return!1'
)
PATCHED_PARAM_GATE = (
    'case"Tracing.start":return iK(t);'
    'case"Target.setAutoAttach":return t?.autoAttach!==!1||'
    't?.waitForDebuggerOnStart===!0||t?.flatten!==!0;default:return!1'
)
ORIGINAL_ATTACH_HANDLER = (
    'this.addTabAttachHandler(async(i,s)=>{await this.call(i,"Page.enable",void 0,s),'
    'await this.enableOopifAutoAttach(i,s)})'
)
PATCHED_ATTACH_HANDLER = (
    'this.addTabAttachHandler(async(i,s)=>{await this.call(i,"Page.enable",void 0,s);'
    'let a=await this.readDocumentState(i);'
    'a?.href?.startsWith("https://bookshelf.vitalsource.com/")||'
    'await this.enableOopifAutoAttach(i,s)})'
)
ORIGINAL_NAVIGATION_START = (
    'async function vs(e,t,r){let n=Number(e.tab_id),o=e.url,'
    'i=typeof e.timeout_ms=="number"?e.timeout_ms:1e4,s=new AbortController;'
)
LEGACY_PATCHED_NAVIGATION_START = (
    'async function vs(e,t,r){let n=Number(e.tab_id),o=e.url,'
    'i=typeof e.timeout_ms=="number"?e.timeout_ms:1e4;'
    "if(!t.isIabBackend&&o.startsWith(\"https://bookshelf.vitalsource.com/\")){"
    'await r;let s;try{s=await t.cdp.call(n,"Page.navigate",{url:o})}'
    'finally{await t.cdp.detachTab(n)}'
    'if(s?.errorText)throw new Error(`Browser Use cannot open VitalSource in tab ${n}. '
    'Browser reported: ${s.errorText}`);'
    'let a=Date.now()+i;for(;;){let u=await t.executeUnhandledCommand('
    '{type:"browser_management_call",browser_id:t.browserId,namespace:"tabs",'
    'method:"get",args:[n]});if(u?.value?.status==="complete")break;'
    'if(Date.now()>=a)throw new Error(`Timed out waiting for VitalSource tab ${n} to load.`);'
    'await new Promise(c=>setTimeout(c,100))}'
    'await new Promise(u=>setTimeout(u,4e3));return{}}let s=new AbortController;'
)
PATCHED_NAVIGATION_START = (
    'async function vs(e,t,r){let n=Number(e.tab_id),o=e.url,'
    'i=typeof e.timeout_ms=="number"?e.timeout_ms:1e4;'
    "if(!t.isIabBackend&&o.startsWith(\"https://bookshelf.vitalsource.com/\")){"
    'await r;let s;try{s=await t.cdp.call(n,"Page.navigate",{url:o})}'
    'finally{await t.cdp.detachTab(n)}'
    'if(s?.errorText)throw new Error(`Browser Use cannot open VitalSource in tab ${n}. '
    'Browser reported: ${s.errorText}`);'
    'await new Promise(u=>setTimeout(u,4e3));return{}}let s=new AbortController;'
)
ORIGINAL_COMMAND_DISPATCH = (
    'oe?await c.withCommandTelemetry(P,A,async()=>await oe(A,U)):'
    'await c.withCommandTelemetry(P,A,async()=>await '
    'U.executeUnhandledCommand({type:P,...A}))'
)
LEGACY_PATCHED_COMMAND_DISPATCH = (
    'oe?await c.withCommandTelemetry(P,A,async()=>{let V=Number(A.tab_id),'
    'J=Number.isFinite(V)&&U.cdp.currentTopLevelUrl(V);'
    'J?.startsWith("https://bookshelf.vitalsource.com/")&&await U.cdp.detachTab(V);'
    'return await oe(A,U)}):await c.withCommandTelemetry(P,A,async()=>await '
    'U.executeUnhandledCommand({type:P,...A}))'
)
PATCHED_COMMAND_DISPATCH = (
    'oe?await c.withCommandTelemetry(P,A,async()=>{let V=Number(A.tab_id),'
    'J=Number.isFinite(V)&&U.cdp.currentTopLevelUrl(V);'
    'typeof J==="string"&&J.startsWith("https://bookshelf.vitalsource.com/")&&'
    'await U.cdp.detachTab(V);'
    'return await oe(A,U)}):await c.withCommandTelemetry(P,A,async()=>await '
    'U.executeUnhandledCommand({type:P,...A}))'
)
ALREADY_PATCHED = "already-patched"


class PatchError(RuntimeError):
    """Raised when a bundle cannot be changed without guessing."""


@dataclass(frozen=True)
class PatchResult:
    status: str
    bundle_path: Path
    backup_path: Path


def patch_source(source: str) -> str:
    """Return a patched bundle or fail closed when reviewed seams drifted."""
    pristine_security_gate = (
        source.count(ORIGINAL_DOMAIN_GATE) == 1
        and source.count(ORIGINAL_PARAM_GATE) == 1
        and PATCHED_DOMAIN_GATE not in source
        and PATCHED_PARAM_GATE not in source
        and LEGACY_PATCHED_PARAM_GATE not in source
    )
    current_raw_cdp_patch = (
        source.count(PATCHED_DOMAIN_GATE) == 1
        and source.count(PATCHED_PARAM_GATE) == 1
        and ORIGINAL_DOMAIN_GATE not in source
        and ORIGINAL_PARAM_GATE not in source
        and LEGACY_PATCHED_PARAM_GATE not in source
    )
    legacy_raw_cdp_patch = (
        source.count(PATCHED_DOMAIN_GATE) == 1
        and source.count(LEGACY_PATCHED_PARAM_GATE) == 1
        and ORIGINAL_DOMAIN_GATE not in source
        and ORIGINAL_PARAM_GATE not in source
        and PATCHED_PARAM_GATE not in source
    )
    original_attach = source.count(ORIGINAL_ATTACH_HANDLER) == 1
    patched_attach = source.count(PATCHED_ATTACH_HANDLER) == 1
    original_navigation = source.count(ORIGINAL_NAVIGATION_START) == 1
    patched_navigation = source.count(PATCHED_NAVIGATION_START) == 1
    legacy_navigation = source.count(LEGACY_PATCHED_NAVIGATION_START) == 1
    original_dispatch = source.count(ORIGINAL_COMMAND_DISPATCH) == 1
    patched_dispatch = source.count(PATCHED_COMMAND_DISPATCH) == 1
    legacy_dispatch = source.count(LEGACY_PATCHED_COMMAND_DISPATCH) == 1

    if sum((pristine_security_gate, current_raw_cdp_patch, legacy_raw_cdp_patch)) != 1:
        raise PatchError(
            "Codex Chrome's raw-CDP security gate does not match a reviewed state; "
            "refusing a partial or speculative patch."
        )
    if original_attach == patched_attach:
        raise PatchError(
            "Codex Chrome's tab-attachment handler does not match the reviewed bundle; "
            "refusing a partial or speculative patch."
        )
    if sum((original_navigation, patched_navigation, legacy_navigation)) != 1:
        raise PatchError(
            "Codex Chrome's navigation handler does not match the reviewed bundle; "
            "refusing a partial or speculative patch."
        )
    if sum((original_dispatch, patched_dispatch, legacy_dispatch)) != 1:
        raise PatchError(
            "Codex Chrome's command dispatcher does not match the reviewed bundle; "
            "refusing a partial or speculative patch."
        )

    patched = source
    if current_raw_cdp_patch:
        patched = patched.replace(PATCHED_DOMAIN_GATE, ORIGINAL_DOMAIN_GATE, 1).replace(
            PATCHED_PARAM_GATE, ORIGINAL_PARAM_GATE, 1
        )
    elif legacy_raw_cdp_patch:
        patched = patched.replace(PATCHED_DOMAIN_GATE, ORIGINAL_DOMAIN_GATE, 1).replace(
            LEGACY_PATCHED_PARAM_GATE, ORIGINAL_PARAM_GATE, 1
        )
    if original_attach:
        patched = patched.replace(ORIGINAL_ATTACH_HANDLER, PATCHED_ATTACH_HANDLER, 1)
    if original_navigation:
        patched = patched.replace(
            ORIGINAL_NAVIGATION_START, PATCHED_NAVIGATION_START, 1
        )
    elif legacy_navigation:
        patched = patched.replace(
            LEGACY_PATCHED_NAVIGATION_START, PATCHED_NAVIGATION_START, 1
        )
    if original_dispatch:
        patched = patched.replace(
            ORIGINAL_COMMAND_DISPATCH, PATCHED_COMMAND_DISPATCH, 1
        )
    elif legacy_dispatch:
        patched = patched.replace(
            LEGACY_PATCHED_COMMAND_DISPATCH, PATCHED_COMMAND_DISPATCH, 1
        )

    return patched


def patch_file(bundle_path: Path) -> PatchResult:
    """Patch one bundle and retain its exact pre-patch bytes once."""
    bundle_path = bundle_path.resolve()
    backup_path = bundle_path.with_suffix(bundle_path.suffix + ".vitalsource-original")
    original_bytes = bundle_path.read_bytes()
    source = original_bytes.decode("utf-8")
    patched = patch_source(source)

    if patched == source:
        return PatchResult(ALREADY_PATCHED, bundle_path, backup_path)

    if not backup_path.exists():
        backup_path.write_bytes(original_bytes)
    bundle_path.write_text(patched, encoding="utf-8", newline="")
    return PatchResult("patched", bundle_path, backup_path)


def unique_paths(paths: list[Path]) -> list[Path]:
    """Return paths once, using their resolved spelling as identity."""
    return list(dict.fromkeys(path.resolve() for path in paths))


def installed_bundles(codex_root: Path, local_app_data: Path) -> list[Path]:
    patterns = (
        (
            codex_root,
            "plugins/cache/openai-bundled/chrome/*/scripts/browser-service.mjs",
        ),
        (
            local_app_data,
            "OpenAI/Codex/runtimes/cua_node/*/bin/node_modules/"
            "@oai/browser-desktop/scripts/browser-service.mjs",
        ),
    )
    return sorted(
        unique_paths(
            [bundle for root, pattern in patterns for bundle in root.glob(pattern)]
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch installed Codex Chrome bundles for VitalSource OOPIF compatibility."
    )
    parser.add_argument(
        "--codex-root",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex data directory (default: the current user's .codex directory)",
    )
    parser.add_argument(
        "--local-app-data",
        type=Path,
        default=Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")),
        help="Windows Local AppData directory containing Codex runtimes",
    )
    parser.add_argument("--bundle", type=Path, help="Patch exactly one browser-service.mjs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundles = (
        [args.bundle]
        if args.bundle
        else installed_bundles(args.codex_root, args.local_app_data)
    )
    if not bundles:
        raise PatchError("No installed Codex Chrome browser-service.mjs was found.")

    for bundle in bundles:
        result = patch_file(bundle)
        print(f"{result.status}: {result.bundle_path}")
        print(f"backup: {result.backup_path}")
    print("Restart Codex before opening a VitalSource reader tab.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
