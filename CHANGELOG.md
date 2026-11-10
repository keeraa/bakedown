# Changelog

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
