# Verification — BakeDown 1.2.2

## Automated (headless Blender)

`tests/run_tests.py` — **10/10 PASS** on Blender **5.1.2** and **4.5.0** (macOS):

| Test | Checks |
|---|---|
| `register_cycle` | register → unregister → register; `load_post` handler added and removed |
| `only_active_object_changes` | with two meshes selected only the active one is simplified; selection restored |
| `distortion_mode` | distortion-budget mode finishes and stores a distortion value |
| `export_with_base_active_has_no_duplicate` | exporting with the base object active writes only `LOD0`–`LOD3` |
| `stale_lods_are_refused` | after a new Simplify LODs are `STALE`, export is cancelled; regeneration makes them `OK` |
| `comparison_object_cannot_be_processed` | the comparison helper cannot be simplified or baked |
| `stale_bake_flag_is_cleared_on_load` | a .blend saved with `is_baking = True` opens with the flag cleared |
| `sharpen_does_not_wrap_edges` | Base Color sharpening does not mix opposite texture edges |
| `rigged_lods_keep_weights` | LODs of a skinned mesh keep weights and the armature parent |
| `translations_complete` | every UI string has ru / es / de / zh translations with matching placeholders |

A live check with Blender's interface language switched to `ru_RU`, `es`, `de_DE` and `zh_HANS` shows the translated strings.

## Still manual (cannot run in background mode)

1. A complete Cycles selected-to-active bake through the desktop modal event loop.
2. Pressing Esc between real 4K bake passes; Ctrl+Z is ignored while baking.
3. Visual inspection of Base Color, Roughness, Metallic and tangent Normal quality.
4. Importing the exported FBX into Unity / Unreal and checking materials and the LOD Group.
5. Installation in Blender 4.2 LTS (the declared minimum) on macOS and Windows.

## History

1.2.1 reported a 17/17 suite run on Blender 5.1.2, but those test scripts were not part of the release. Since 1.2.2 the tests live in this repository.
