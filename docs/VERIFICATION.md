# Verification — BakeDown 1.5.0

## Automated (headless Blender)

`tests/run_tests.py` — **30/30 PASS** on Blender **5.1.2** and **4.5.0** (macOS):

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
| `metallic_albedo_is_not_darkened` | a fully metallic material bakes its exact base colour |
| `faceted_original_gets_faceted_shading` | faceted originals get flat / by-angle shading, smooth ones stay smooth |
| `triangle_budget_is_used` | the result lands within 3 % below the requested triangle count |
| `api_normal_strength_sticks` | `bake(normal_strength=…)` survives the settings restore; default 1.0 |
| `normal_map_repair_flattens_misses` | sideways / backward tangent normals are flattened, valid ones kept |
| `ambient_occlusion_map_is_baked_and_exported` | AO map is plausible, exported as PNG, in the ORM red channel and as glTF occlusion; temporary world removed |
| `bake_without_ambient_occlusion` | `ao=False` bakes the other maps and reports them as complete |
| `translations_complete` | every UI string has ru / es / de / zh translations with matching placeholders |

A live check with Blender's interface language switched to `ru_RU`, `es`, `de_DE` and `zh_HANS` shows the translated strings.

## Desktop runs (Blender 5.1.2 GUI, macOS)

A scripted GUI session built a 251,904-triangle textured mesh, simplified it to 2,713 triangles (≈0.37% distortion), ran the real modal Cycles bake at 2K (Base Color, Roughness, Metallic, Normal — finished, no rollback), and exported a Unity FBX with four PNG maps. The README comparison screenshots come from a second GUI run on a 49,988-triangle character (2,734 after Simplify, 4K bake). Versions 1.3.0 and 1.4.0 repeated the modal bake and Unity FBX export successfully. In 1.4.0 the CLI processed the same character headless in 4.8 s (2,734 triangles, 2K bake, LOD 2,734 / 1,366 / 682 / 272, Unity FBX + 4 PNG).

## Quality measurements (`tools/quality_eval.py`)

Four orthographic views of original vs result, per-pixel error (0–255, lower is better) over the shared silhouette: *shape* = Workbench studio light, plain colour; *colour* = base-colour texture, flat light; *full* = EEVEE with materials and the normal map; *close-up* = full render of the top quarter at about texture resolution. *geo mean* = mean two-way surface distance in % of object size. 2K bake.

Test models: a stylised Hunyuan character (49,988 triangles, faceted) and a metallic sculpt (251,904 triangles, smooth, procedural material).

| Model, target | Triangles | geo mean % | Shape | Colour | Full | Close-up |
|---|---|---|---|---|---|---|
| Character, 1k | 964 → 1,000 | 0.114 → 0.108 | 19.2 → 6.9 | 8.4 → 1.3 | 10.5 → 3.1 | 9.3 → 4.1 |
| Character, 3k | 2,734 → 3,000 | 0.023 → 0.014 | 13.5 → 3.0 | 6.9 → 0.4 | 7.4 → 1.9 | 7.6 → 2.2 |
| Character, 10k | 7,750 → 10,000 | 0.013 → 0.005 | 10.1 → 2.7 | 7.0 → 0.3 | 6.6 → 1.8 | 7.0 → 2.1 |
| Sculpt, 1k | 971 → 999 | 0.115 → 0.110 | 9.4 → 8.7 | — | 21.5 → 1.8 | 31.0 → 3.1 |
| Sculpt, 3k | 2,713 → 2,999 | 0.051 → 0.047 | 6.7 → 6.3 | — | 21.1 → 0.8 | 29.4 → 1.2 |
| Sculpt, 10k | 8,952 → 10,000 | 0.022 → 0.019 | 5.2 → 4.7 | — | 21.1 → 0.4 | 29.5 → 0.7 |

Values: 1.4.1 → 1.5.0. AO (1K, character): full resolution with 8 samples differs from a 64-sample reference by 0.020 on average (p95 0.067); 16 samples 0.012; half resolution + upscale 0.053 (p95 0.30, at UV borders). Removing the planar-dissolve options changed none of the numbers (also checked on a 29,672-triangle building model). Tried and **not** kept because they did not measurably help: average-island-scale and concave UV packing (lower utilisation, 3–4× slower bake), 8 bake samples, half / double automatic ray distance, automatic symmetric decimation, disabling the pre-collapse planar dissolve.

### 1.6.0: emission and transparency

The test character (49,988 → 3,000 triangles, 2K bake) was given four material variants on its real geometry and UVs, and each was evaluated with 1.5.0 and 1.6.0 (EEVEE full-render pixel error, lower is better):

| Variant | 1.5.0 | 1.6.0 |
|---|---|---|
| Glow — bright texture areas emit at strength 4 | 105.5 | 3.6 |
| Cutout — Voronoi holes in UV space (0/1 alpha) | 3.5 | 2.0 |
| Glass — alpha 0.5 | 11.0 | 2.6 |
| Glow + cutout | 105.0 | 3.8 |

On the unmodified (opaque) character all five maps baked by 1.5.0 and 1.6.0 are bit-identical, and every quality metric is unchanged. In *albedo* mode the cutout variants read 0.37 → 1.65 because Workbench shows the baked texture's alpha but not the original's node-driven alpha; full renders show the holes match.

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
