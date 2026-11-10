# Changelog

## 1.4.1 — 2026-11-10

### Fixed

- API: objects created from code (`bpy.data.objects.new` + link) were rejected as "not in the current view layer" until Blender updated the scene — the usual way AI agents build scenes. Found while driving BakeDown through Blender MCP.
- The panel marks distortion red only above 1 % (was 0.5 %), matching the denser 1.3 estimate and the guidance in AGENTS.md.

## 1.4.0 — 2026-11-10

### Added

- **Python API** for scripts and AI agents: `bakedown.process()`, `simplify()`, `bake()`, `generate_lods()`, `export()`, `report()`. One mesh per call, JSON-friendly results, `BakeDownError` with readable messages, scene settings restored after each call.
- **Command-line tool** `tools/bakedown_cli.py`: model file in (`.glb .gltf .fbx .obj .ply .stl .blend`), game-ready export + `bakedown_report.json` out, runs without a window.
- **AGENTS.md** — instructions for AI agents (CLI, Blender MCP / Python API, recommended values, what not to do).
- The bake operator can run blocking (`EXEC_DEFAULT`) in background mode; the interactive panel still uses the modal bake with progress and Esc.

### Changed

- Description and READMEs: BakeDown works with any heavy mesh — AI-generated, scanned, sculpted or downloaded.

## 1.3.0 — 2026-11-10

### Changed

- **Minimum Blender version is now 4.5** (tested on 4.5.0 and 5.1.2).
- Unity FBX export uses `FBX All` scaling and the Unity axis convention, applying the transform to static meshes, so models no longer arrive rotated by −90° or scaled ×100. Rigged exports keep the conversion on the object transforms.
- Distortion is estimated from up to 8,000 evenly spread samples per direction (numpy) instead of ~1,200, so values are higher and more realistic.
- UI strings use their own translation context, so BakeDown's wording is no longer replaced by Blender's built-in translation (e.g. Russian "Bake").
- The panel title reads the version from `bl_info`.

### Fixed

- GLB export never flips the normal-map green channel (glTF requires OpenGL normal maps); the option is disabled for GLB.
- **Delete backup** asks for confirmation; Delete backup, Generate LODs, Compare and Import rig template support Undo.
- Rig transfer warns when it falls back to the only armature in the scene and when weight smoothing fails.

## 1.2.2 — 2026-11-10

### Added

- Spanish, German and Simplified Chinese interface translations (alongside Russian).
- README in English, Russian, Spanish, German and Simplified Chinese.
- Headless test suite `tests/run_tests.py` (Blender 5.1.2 and 4.5.0: 10/10).

### Changed

- Code comments and developer documentation are now in English.

### Fixed

- Export no longer adds the base mesh next to LOD0 when the base object is active.
- Exporting LODs that are older than the base mesh's last Simplify or Bake is refused with a clear message; the LOD panel shows an "out of date" warning.
- A file saved during a bake (Ctrl+S, autosave, crash recovery) no longer opens with a permanently "baking" panel and a blocked Bake button.
- Ctrl+Z is blocked while a bake is running; deleting the target object mid-bake cancels cleanly instead of raising errors.
- Object-linked materials are kept on the high-poly bake source and no longer hide the bake material on the target.
- Base Color sharpening no longer mixes opposite edges of the texture.
- The comparison helper object can no longer be simplified or baked.
- Author name spelling in metadata and docs.

## 1.2.1 — 2026-07-11

### Fixed

- Processing is strictly limited to the active mesh; unrelated scene objects remain unchanged.
- Real triangle counts are used for targets, LODs, statistics, and reports.
- Existing modifier stacks are no longer baked into the simplified mesh and applied twice.
- Failed simplification restores geometry and all BakeDown custom properties.
- Failed or cancelled baking restores mesh, UVs, material state, temporary images, render settings, viewport state, selection, and active object.
- Live Normal strength no longer invalidates baked pixels; legacy 1.2 signatures remain accepted.
- Distortion values respect scene units and stale values are cleared after measurement failure.
- Compare objects are scoped to their own result asset.
- LOD preview uses explicit level metadata instead of fragile object-name parsing.
- Rig import removes partial imports and orphan data after failure.
- Rig transfer restores Rest/Pose Position through a guaranteed `finally` path.
- FBX texture references now resolve to exported PNG files.
- GLB normal green-channel conversion is temporary and the Blender image is restored.
- Reset and backup deletion preserve the user's selection and active object.

### Changed

- FBX texture references use relative paths.
- Viewport helpers are safe in contexts without a screen.
- Version raised to 1.2.1.

## 1.2.0 — 2026-07-11

- Added active-object isolation, real triangle counting, transactional bake groundwork, bidirectional distortion, safer export, English source UI, Russian localization, GPL-3.0-or-later licensing, and author metadata.
