import sys
import tempfile
import unittest
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vitalsource-chrome" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from patch_codex_chrome import (
    ALREADY_PATCHED,
    LEGACY_PATCHED_PARAM_GATE,
    LEGACY_PATCHED_NAVIGATION_START,
    ORIGINAL_ATTACH_HANDLER,
    ORIGINAL_COMMAND_DISPATCH,
    ORIGINAL_DOMAIN_GATE,
    ORIGINAL_NAVIGATION_START,
    ORIGINAL_PARAM_GATE,
    PATCHED_ATTACH_HANDLER,
    PATCHED_COMMAND_DISPATCH,
    PATCHED_DOMAIN_GATE,
    PATCHED_NAVIGATION_START,
    PATCHED_PARAM_GATE,
    PatchError,
    installed_bundles,
    unique_paths,
    patch_source,
)


class PatchSourceTests(unittest.TestCase):
    def test_skips_oopif_auto_attach_at_the_vitalsource_boundary(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}after"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertNotIn(ORIGINAL_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_DOMAIN_GATE, patched)
        self.assertIn(ORIGINAL_PARAM_GATE, patched)
        self.assertNotIn(PATCHED_DOMAIN_GATE, patched)
        self.assertNotIn(PATCHED_PARAM_GATE, patched)
        self.assertIn(PATCHED_NAVIGATION_START, patched)
        self.assertNotIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertIn(PATCHED_COMMAND_DISPATCH, patched)
        self.assertNotIn(ORIGINAL_COMMAND_DISPATCH, patched)
        self.assertIn('typeof J==="string"', PATCHED_COMMAND_DISPATCH)

    def test_is_idempotent(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{PATCHED_ATTACH_HANDLER}next{PATCHED_NAVIGATION_START}"
            f"dispatch{PATCHED_COMMAND_DISPATCH}after"
        )

        self.assertEqual(source, patch_source(source))

    def test_migrates_the_earlier_raw_cdp_patch(self) -> None:
        source = (
            f"before{PATCHED_DOMAIN_GATE}middle{LEGACY_PATCHED_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}after"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_DOMAIN_GATE, patched)
        self.assertIn(ORIGINAL_PARAM_GATE, patched)
        self.assertNotIn(PATCHED_DOMAIN_GATE, patched)
        self.assertNotIn(LEGACY_PATCHED_PARAM_GATE, patched)

    def test_migrates_the_rejected_browser_management_navigation(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{PATCHED_ATTACH_HANDLER}next{LEGACY_PATCHED_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}after"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_NAVIGATION_START, patched)
        self.assertNotIn(LEGACY_PATCHED_NAVIGATION_START, patched)

    def test_rejects_unknown_bundles_instead_of_guessing(self) -> None:
        with self.assertRaises(PatchError):
            patch_source("a future bundle with a different security gate")

    def test_rejects_partial_patch(self) -> None:
        source = (
            f"before{PATCHED_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}after"
        )

        with self.assertRaises(PatchError):
            patch_source(source)


class OnDiskPatchTests(unittest.TestCase):
    def test_installed_bundles_include_plugin_cache_and_active_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            codex_root = root / ".codex"
            local_app_data = root / "AppData" / "Local"
            cached = (
                codex_root
                / "plugins/cache/openai-bundled/chrome/1/scripts/browser-service.mjs"
            )
            runtime = (
                local_app_data
                / "OpenAI/Codex/runtimes/cua_node/hash/bin/node_modules"
                / "@oai/browser-desktop/scripts/browser-service.mjs"
            )
            cached.parent.mkdir(parents=True)
            runtime.parent.mkdir(parents=True)
            cached.touch()
            runtime.touch()

            self.assertEqual(
                sorted([cached.resolve(), runtime.resolve()]),
                installed_bundles(codex_root, local_app_data),
            )

    def test_duplicate_bundle_paths_are_collapsed(self) -> None:
        paths = [Path("bundle.mjs"), Path("bundle.mjs"), Path("other.mjs")]

        self.assertEqual(2, len(unique_paths(paths)))

    def test_backup_is_created_once_and_original_is_preserved(self) -> None:
        from patch_codex_chrome import patch_file

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir) / "browser-service.mjs"
            original = (
                f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
                f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
                f"dispatch{ORIGINAL_COMMAND_DISPATCH}after"
            )
            bundle.write_text(original, encoding="utf-8")

            result = patch_file(bundle)
            second = patch_file(bundle)

            self.assertEqual("patched", result.status)
            self.assertEqual(ALREADY_PATCHED, second.status)
            self.assertEqual(original, result.backup_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
