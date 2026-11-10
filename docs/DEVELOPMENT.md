# BakeDown — developer notes

**v1.3.0 · single file `bakedown.py` · Blender 4.5+**
Author: **Kirill Migachev** · License: **GPL-3.0-or-later**

Read this before changing the add-on. Section 3 lists hard-won pitfalls.

---

## 0. Architecture changes in 1.2–1.4

- All geometry processing is bound to `context.active_object`; `_activate_only()` deselects every other object before `bpy.ops` calls.
- Geometry statistics go through `_triangle_count_mesh()` / `_triangle_count_object()` and count `mesh.loop_triangles`, not `mesh.polygons`.
- Baking is transactional: a working copy of the mesh plus temporary images and a temporary material; `_commit()` accepts the result, `_rollback()` restores the original state completely.
- Render settings are saved with `_capture_render_state()` and restored with `_restore_render_state()`.
- After success, cancellation or failure the viewport mode is restored with `_capture_viewport_state()` / `_restore_viewport_state()`.
- Distortion is an approximate two-way estimate: result → original and original → result.
- Export saves and restores selection, active object, visibility, image paths and formats; it checks that the folder is writable, that the exporter exists, that only one armature is involved, and warns about unusual scale.
- **1.2.2:** a module-level `_BAKE_RUNNING` flag tells whether a bake is really running; a `load_post` handler clears a stale `scene.bakedown.is_baking` saved into a .blend file.
- **1.2.2:** each LOD stores `bakedown_lod_src_sig` (geometry version + bake signature + material of its base). `_lod_state()` returns `OK`, `STALE` or `UNKNOWN`; export refuses `STALE` LODs.
- **1.3.0:** `_fbx_export_kwargs(engine, path, has_armature)` holds the per-engine FBX settings (Unity: `FBX_SCALE_ALL`, `-Z` forward / `Y` up, `bake_space_transform` only without an armature).
- **1.3.0:** distortion sampling and BVH construction use numpy (`_world_array`, up to 8,000 samples per direction).
- **1.3.0:** `_tr()` translates in the `BakeDown` context (`_I18N_CTX`); every translation is registered in both the default and the BakeDown context.
- **1.4.0:** the bake operator is split into `_prepare()` + `invoke()` (modal, interactive) + `execute()` (blocking, for scripts / background mode).
- **1.4.0:** public Python API at the end of the module (`process`, `simplify`, `bake`, `generate_lods`, `export`, `report`, `BakeDownError`, `API_VERSION`). It drives the operators with `EXEC_DEFAULT` and restores `scene.bakedown` through `_SceneSettings`. `tools/bakedown_cli.py` wraps it for files on disk. Keep `AGENTS.md` in sync when the API changes, and bump `API_VERSION` on breaking changes.
- UI source strings are English; translations are registered with `bpy.app.translations` (see section 6).

## 1. Architecture

One module, top to bottom:
1. `bl_info` (name, version, description).
2. Translation tables (`_TRANSLATIONS`).
3. **Helper functions** (module level, `_` prefix).
4. **PropertyGroup** `BakeDownSettings` (all settings) → `bpy.types.Scene.bakedown`.
5. **Operators** `OBJECT_OT_bakedown_*`.
6. **Panel** `VIEW3D_PT_bakedown` (one panel, three tabs via `ui_mode`).
7. `_classes` tuple + `register()` / `unregister()`.

`register()` registers translations, all classes from `_classes`, the `Scene.bakedown` PointerProperty and the `load_post` handler.

### Operators
| Operator | Purpose |
|---|---|
| `bakedown_decimate` | Simplify (calls `_run_pipeline` or `_auto_target`) |
| `bakedown_reset` | Restore the original from the backup |
| `bakedown_inspect` | Toggle "Shape" mode (Solid + MatCap + wireframe) |
| `bakedown_distort_info` | Empty operator — only a tooltip on the distortion row |
| `bakedown_bake` | **Modal** bake of 4 maps (progress / cancel) |
| `bakedown_bake_cancel` | Sets the bake cancel flag |
| `bakedown_finalize` | Release the backup (`use_fake_user = False`) |
| `bakedown_compare` | Original ↔ result toggle |
| `bakedown_export` | Unity / Unreal / glTF export + textures |
| `bakedown_lod` | Generate LOD0–3 (armature-aware) |
| `bakedown_rigimport` | Import an .fbx rig as a template |
| `bakedown_rigtransfer` | Transfer armature + weights from the template |

### Key helpers
- **Backup:** `_get_backup`, `_ensure_backup` (creates the mesh datablock `BakeDownOrig_<name>` with a fake user), `_restore_from_backup`.
- **Pipeline:** `_run_pipeline` (the whole simplification pipeline), `_auto_target` (binary search for the distortion budget), `_finish_simplify`, `_planar_snap`.
- **Bake:** `_bake_ray` (automatic distance from the LOCAL size), `_metallic_emit_copy`, `_sharpen_image`, `_measure_distortion` (two-way sampled BVH estimate).
- **Bake signature:** `_bake_sig` / `_needs_bake` (the Bake button is enabled only when bake inputs changed).
- **LOD / rig:** `_lod_base_name`, `_not_lod`, `_lod_source_sig`, `_lod_state`, `_meshes_coincide` (do the meshes match by position — KDTree).
- **Inspect:** `_enter_inspect` / `_exit_inspect`.

---

## 2. Data model

### Custom properties on the OBJECT (`o["..."]`)
| Key | Meaning |
|---|---|
| `bakedown_orig_mesh` | name of the backup mesh datablock |
| `bakedown_simplified` | whether the object was simplified (button gate) |
| `bakedown_geo_version` | geometry version (incremented on every Simplify; part of the bake signature) |
| `bakedown_baked_sig` | signature of the last bake's inputs |
| `bakedown_material_name` | actual name of the baked material |
| `bakedown_image_<suffix>` | actual names of the baked images (`BaseColor`, `Rough`, `Metal`, `Normal`) |
| `bakedown_distort_mm` / `_pct` | distortion measurement |
| `bakedown_lod_of` | on a LOD object — name of its base |
| `bakedown_lod_level` | explicit level `LOD0`–`LOD3` |
| `bakedown_lod_src_sig` | on a LOD object — state of the base when the LOD was generated |
| `bakedown_compare` | marks the temporary comparison object |
| `bakedown_result` | on the comparison object — name of the result |

### Scene settings (`context.scene.bakedown`, PropertyGroup)
Simplify: `target_mode`, `target_faces`, `target_distortion`, `dissolve_angle`, `do_dissolve_faces`, `final_dissolve`, `fill_holes`, `remove_interior`, `planar_snap`, `triangulate_output`.
Bake: `bake_resolution`, `bake_normal`, `bake_normal_strength` (live update), `bake_extrusion`, `bake_sharpen`, `is_baking` / `bake_progress` / `bake_cancel` / `bake_stage`.
UI: `ui_mode` (STEPS / RIG / LOD), `show_adv_*`.
LOD: `lod_preset`, `lod1/2/3_on`, `lod1/2/3_pct` (linked through update callbacks), `lod_preview`.
Rig: `rig_template` (PointerProperty to an Object).

### Naming
- Working mesh: `<name>_work`. Backup mesh: `BakeDownOrig_<name>` (fake user).
- LODs: collection `<base>_LODs`, objects `<base>_LOD0..3`.
- Textures are usually `<base>_BaseColor/_Rough/_Metal/_Normal`; on a name clash a suffixed version is created and the real names are stored in `bakedown_image_*`. The material name is stored in `bakedown_material_name`.
- Temporary: `__BakeDownBefore_<asset>` (compare), `__bakedown_hipoly_<token>` and `__bd_probe` (bake / import).

---

## 3. Pitfalls (read before editing)

1. **Custom split normals (e.g. Hunyuan meshes) block `dissolve_limited`.** Clear them with `customdata_custom_splitnormals_clear()` + `normals_make_consistent` **before every** dissolve.
2. **Triangulating after dissolve inflates the count** again (n-gons → triangles). That is why `triangulate_output` is OFF by default.
3. **Bake needs `use_clear=True`**, otherwise old pixels from a previous UV layout remain.
4. **Circular dependency while baking:** connect the target image nodes to the BSDF ONLY AFTER baking, otherwise the result is black.
5. **Black spots after baking = ray misses.** `cage_extrusion` / `max_ray_distance` are in the mesh's LOCAL coordinates. AI imports often have scale 0.01, so the automatic distance is computed from the LOCAL size (`_bake_ray`); otherwise it is ~1/scale times too small.
6. **Metallic** is baked through an EMIT reroute on a COPY of each material (never touch the original).
7. **Armature-aware LODs:** add the armature AFTER `new_from_object` (otherwise the pose is baked in); copy vertex group names by hand (they live on the object, `mesh.copy()` does not carry them).
8. **Rig transfer — three critical conditions** (otherwise spikes / creases):
   - `NEAREST` mapping (not `POLYINTERP` — it interpolates and tears weights at polygon borders).
   - Decide whether the meshes coincide by POSITION (`_meshes_coincide`, KDTree), NOT by vertex count (FBX splits vertices at UV seams).
   - Both meshes in **REST / bind pose** — the tool sets `pose_position='REST'` during the transfer.
   - Do NOT apply `limit_total(4)` (it breaks smooth Mixamo weights; the engine limits influences on import).
9. **FBX rig import crashes on lights** (Blender 5.1 bug: `CyclesLightSettings.cast_shadow`). Workaround: temporarily add the property to the light settings type (obtained via `bpy.data.lights.new(...).cycles`), then remove it.
10. **Never fix rig scale automatically.** FBX / Mixamo may import at scale 0.01; BakeDown warns about unusual transforms on export but never changes scale silently.
11. **Modal bake:** packing 4K images is split into one timer tick per image (otherwise the UI hangs at 100%). Timer cleanup is guaranteed in `_cleanup`. Ctrl+Z is swallowed while a bake runs; deleted datablocks are detected with `_alive()`.
12. Runtime objects / materials that must not be saved use temporary `__...` names and are removed in cleanup.
13. `scene.bakedown.is_baking` is saved in .blend files. Never trust it alone — check `_BAKE_RUNNING`.

---

## 4. How to extend

**New operator:** class `OBJECT_OT_bakedown_<name>` → add it to `_classes`. Use `@classmethod poll` for gates (e.g. `_not_lod` blocks LOD and comparison objects).
**New setting:** a property in `BakeDownSettings`. For a live effect use an `update=` callback. If it requires a new bake, add it to `_bake_sig`.
**New tab:** an item in the `ui_mode` enum + a branch in `VIEW3D_PT_bakedown.draw` + a `_draw_<name>` method.
**Reuse the shared logic:** `_run_pipeline`, `_bake_ray`, `_measure_distortion` — call them, do not duplicate.
**New UI string:** wrap it in `_tr()` and add a translation for every language (section 6). `tests/run_tests.py` fails when a translation is missing.

---

## 5. Testing

Automated tests run headless in real Blender:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py
```

They cover the Python API and the command-line tool, registration, active-object isolation, LOD export, stale-LOD detection, the stale bake flag, comparison-object gating, sharpening, rig weights in LODs, distortion mode and translation completeness. See `docs/VERIFICATION.md` for what still needs a manual desktop check (a real Cycles bake and Esc cancellation cannot run in background mode).

---

## 6. Translations

English is the source language. `_TRANSLATIONS` maps a Blender locale to `{("*", english): translated}`:

| Language | Locale(s) |
|---|---|
| Russian | `ru_RU` |
| Spanish | `es` |
| German | `de_DE` |
| Simplified Chinese | `zh_HANS` (Blender 4.x+), `zh_CN` (older builds) |

Strings drawn through `_tr()` use the `BakeDown` context, so BakeDown's own wording is used even when Blender has a built-in translation of the same English text (e.g. "Bake"). Property names and operator labels use the default context.

---

## 7. Ideas for later
- Triangle presets by viewing distance (hero / background) — partially covered by LODs.
- Saved export presets (folder / engine / Y-flip) per project.
- Texture atlas for a batch of objects (fewer draw calls).
- Albedo de-lighting (remove baked lighting from AI textures).
- Interior geometry removal via raycast visibility (the current `select_interior_faces` is unreliable, hence OFF).
- Package as a folder add-on / Blender extension (`blender_manifest.toml`) for the Extensions platform.
