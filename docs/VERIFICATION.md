# Verification — BakeDown 1.4.1

## Automated (headless Blender)

`tests/run_tests.py` — **20/20 PASS** on Blender **5.1.2** and **4.5.0** (macOS):

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
| `version_label_matches_bl_info` | panel title follows `bl_info`; minimum Blender is 4.5 |
| `destructive_operators_support_undo` | Undo on destructive operators; Delete backup has a confirmation |
| `fbx_settings_per_engine` | Unity / Unreal FBX settings, accepted by the exporter |
| `glb_never_flips_normal_green` | GLB export keeps OpenGL normal maps even with the flip option on |
| `ui_strings_use_own_translation_context` | "Bake" shows BakeDown's Russian / Spanish wording, not Blender's |
| `distortion_sampling_is_dense_and_fast` | ~8,000 samples, exact zero on identical meshes, under 10 s on a dense ico sphere |
| `api_full_pipeline_headless` | `simplify` → blocking `bake` → `generate_lods` → `export` in background mode; settings restored |
| `api_accepts_objects_linked_from_code` | an object created with `bpy.data.objects.new` + link is accepted by the API |
| `api_errors_are_readable` | wrong arguments raise `BakeDownError` with a clear message |
| `cli_processes_a_file_and_reports_json` | CLI turns a .glb into a baked GLB with LODs and a JSON report; exit code 1 on a missing file |
| `translations_complete` | every UI string has ru / es / de / zh translations with matching placeholders |

A live check with Blender's interface language switched to `ru_RU`, `es`, `de_DE` and `zh_HANS` shows the translated strings.

## Desktop runs (Blender 5.1.2 GUI, macOS)

A scripted GUI session built a 251,904-triangle textured mesh, simplified it to 2,713 triangles (≈0.37% distortion), ran the real modal Cycles bake at 2K (Base Color, Roughness, Metallic, Normal — finished, no rollback), and exported a Unity FBX with four PNG maps. The README comparison screenshots come from a second GUI run on a 49,988-triangle character (2,734 after Simplify, 4K bake). Versions 1.3.0 and 1.4.0 repeated the modal bake and Unity FBX export successfully. In 1.4.0 the CLI processed the same character headless in 4.8 s (2,734 triangles, 2K bake, LOD 2,734 / 1,366 / 682 / 272, Unity FBX + 4 PNG).

## Blender MCP run (user's Blender 5.1.2, live scene)

An agent session reloaded the add-on in the running Blender through Blender MCP, copied the user's character from its original backup and called `bakedown.process(obj, triangles=3000, resolution=2048, lods=(50, 25, 10), export_dir=…, engine="UNITY")`: 49,988 → 2,734 triangles, 2K bake, LOD 2,734 / 1,366 / 682 / 272, Unity FBX + 4 PNG in 5.2 s. The user's own object was not modified. The run exposed the view-layer bug fixed in 1.4.1.

## Still manual

1. A long 4K bake on a real AI-generated asset.
2. Pressing Esc between real 4K bake passes; Ctrl+Z is ignored while baking.
3. Visual inspection of Base Color, Roughness, Metallic and tangent Normal quality.
4. Importing the exported FBX into Unreal and checking materials and the LOD Group.
5. Importing the Unity FBX into Unity and checking that rotation is 0 and scale is 1 (static and rigged).
6. Installation on Windows.

## History

1.2.1 reported a 17/17 suite run on Blender 5.1.2, but those test scripts were not part of the release. Since 1.2.2 the tests live in this repository.
