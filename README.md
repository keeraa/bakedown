# BakeDown

**English** · [Русский](README.ru.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [简体中文](README.zh-CN.md)

**Version 1.3.0 · Blender 4.5+ · GPL-3.0-or-later**

BakeDown is a Blender add-on that turns heavy AI-generated and photogrammetry meshes (Hunyuan, Meshy, Tripo, Rodin, scans — often 50k+ polygons with a single 4K texture) into **game-ready assets**. It simplifies only the active mesh, bakes PBR textures from the original onto the light mesh, generates LODs, transfers rigs, and exports to Unity, Unreal Engine or glTF.

The workflow is **non-destructive**: the original is kept as a backup, you can try different values freely, and **Reset** brings everything back.

Author: **Kirill Migachev**

[![BakeDown demo: 49,988 → 2,734 triangles, then a 4K texture bake](docs/images/demo_poster.jpg)](docs/media/bakedown_demo.mp4)

▶ **[Watch the 40-second demo](docs/media/bakedown_demo.mp4)**

### Same look, 95% fewer triangles

| Full figure, textured | Full figure, wireframe |
|---|---|
| ![Full figure, textured](docs/images/compare_full_textured.jpg) | ![Full figure, wireframe](docs/images/compare_full_wireframe.jpg) |
| **Close-up, textured** | **Close-up, wireframe** |
| ![Close-up, textured](docs/images/compare_closeup_textured.jpg) | ![Close-up, wireframe](docs/images/compare_closeup_wireframe.jpg) |

Original (left) vs BakeDown result (right): 49,988 → 2,734 triangles, approx. distortion 7.3 mm (0.56%), 4K bake.

## Installation

1. Download `bakedown.py` from the [latest release](https://github.com/keeraa/bakedown/releases/latest).
2. In Blender: **Edit → Preferences → Add-ons → Install from Disk…** and select `bakedown.py`.
3. Enable **BakeDown — Game Asset Optimizer**.
4. Open the 3D View sidebar with **N** and select the **BakeDown** tab.

To update, install the new `bakedown.py` over the old one and restart Blender.

## Workflow

Static asset (building, prop):

```text
Simplify → Bake → (LOD) → Export
```

Character:

```text
Simplify → Bake → Rig → LOD → Export
```

Generate LODs **after** the rig so they inherit the armature. When several objects are selected, BakeDown processes only the active mesh (the one with the brighter outline).

## Features

### Simplification
- Target by real triangle count (slider + 1K/3K/5K/10K/20K presets) or by an approximate distortion budget (binary search finds the triangle count).
- Weld, loose-geometry cleanup, normal fixes (including custom split normals from AI meshes), planar dissolve, collapse decimation; optional hole filling, interior-face removal, plane flattening and explicit triangulation.
- Distortion estimate in millimetres and % of object size right in the panel.
- **Shape** inspection (Solid + MatCap + wireframe) and **Compare** original ↔ result.

### Texture baking
- Cycles bake of Base Color, Roughness, Metallic and an optional tangent-space Normal map onto a fresh UV layout, at 1K/2K/4K.
- Modal, with progress and cancellation; transactional rollback on cancel or error.
- Automatic ray distance, live Normal strength, Base Color sharpening.

### LOD
- LOD0–LOD3 with Strategy, 3D Shooter, Mobile and Custom presets. All LODs share one texture set.
- Armature-aware: LODs of a rigged mesh inherit the armature and weights.
- Naming `<object>_LOD0..3`, so Unity builds a LOD Group automatically.
- Warns when LODs are out of date after a new Simplify or Bake, and refuses to export stale LODs.

### Rig transfer
- Import a skinned FBX as a template and transfer the armature and vertex weights to the active mesh (for similar humanoids).
- Works in Rest Position and restores the pose state even after an error.

### Export
- Unity FBX, Unreal FBX (smoothing groups) and self-contained GLB.
- Model and PNG textures go into a sub-folder named after the .blend file; FBX references the PNGs with relative paths.
- Options: normal-map green-channel flip (DirectX convention), ORM packing.
- Exports a single object or its whole LOD collection (with the armature) as one file.

## Interface languages

The source interface is English. Translations are included for **Russian, Spanish, German and Simplified Chinese**; Blender shows them automatically when its interface language is set accordingly (**Preferences → Interface → Translation**).

## Tips

- Baking uses Cycles on the CPU: from tens of seconds to a couple of minutes per object at 4K.
- Black spots after baking → increase **Ray distance**; smeared thin details → set it back to 0 (auto).
- Triangulation is off by default: engines triangulate on import, and the GPU cost is the same.
- For Mixamo animations: rig once; animations are separate FBX files retargeted in Unity through a Humanoid Avatar.

## Limitations

- Distortion is an approximate sampled metric, not an exact Hausdorff distance.
- A running bake pass cannot be interrupted; cancellation takes effect between maps.
- Interior-face detection is experimental and off by default.
- Review unusual negative and non-uniform transforms before engine import.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the architecture and pitfalls, and [docs/VERIFICATION.md](docs/VERIFICATION.md) for the test status. Headless tests:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py
```

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE).
