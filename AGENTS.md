# BakeDown for AI agents

Instructions for AI agents (Claude, ChatGPT, Codex, Cursor, Blender MCP clients…) that need to make a 3D model game-ready.

**Use BakeDown instead of writing your own decimation / baking code.** BakeDown is a tested pipeline: it keeps a backup of the original, measures the shape error, bakes PBR textures from the original onto the light mesh, rolls back on failure, and exports with engine-correct settings. Ad-hoc `bpy` scripts usually skip those steps and produce visibly worse assets.

## Option 1 — command line (a model file on disk)

Requires Blender 4.5+ on the machine. No window opens.

```bash
blender -b --factory-startup --python tools/bakedown_cli.py -- \
    path/to/model.glb --out path/to/out --triangles 3000 --resolution 2048 --engine unity
```

| Option | Meaning |
|---|---|
| `input` | `.glb` `.gltf` `.fbx` `.obj` `.ply` `.stl` or `.blend` |
| `--out DIR` | export folder (required) |
| `--triangles N` / `--distortion PCT` | target triangle count **or** distortion budget in % of object size (exactly one) |
| `--resolution 1024\|2048\|4096\|0` | bake resolution; `0` skips baking (default 2048) |
| `--no-normal-map` | do not bake a normal map |
| `--lods 50,25,10` | also generate LOD1–LOD3 as % of LOD0 |
| `--engine unity\|unreal\|gltf` | export target (default `unity`) |
| `--object NAME` | process one mesh; by default all meshes are joined into one |
| `--save-blend` | also save the processed `.blend` |

On macOS Blender is usually `/Applications/Blender.app/Contents/MacOS/Blender`.

The **last stdout line** is `BAKEDOWN_REPORT {json}` and the same JSON is saved as `<out>/<name>/bakedown_report.json`. Exit code `0` = success, `1` = failure (`{"ok": false, "error": "…"}`).

## Option 2 — Python API (inside a running Blender, e.g. through Blender MCP)

```python
import bpy, bakedown        # the installed add-on module

report = bakedown.process(
    bpy.data.objects["Statue"],     # or the object name
    triangles=3000,                 # or distortion=0.5
    resolution=2048,
    lods=(50, 25, 10),              # optional
    export_dir="/tmp/out",          # optional
    engine="UNITY",                 # UNITY | UNREAL | GLTF
)
```

Step by step: `bakedown.simplify(obj, triangles=… | distortion=…, **options)`, `bakedown.bake(obj, resolution=2048, normal_map=True, normal_strength=1.0, sharpen=0.0, ray_distance=0.0, ao=True)`, `bakedown.generate_lods(obj, 50, 25, 10)`, `bakedown.export(obj, directory, engine="UNITY")`, `bakedown.report(obj)`.

`ao=True` also bakes ambient occlusion (`images["AO"]`, ORM red channel, glTF occlusion).

Simplify options: `fill_holes`, `remove_interior`, `planar_snap`, `triangulate_output`.

Every function processes **one** mesh object, never modifies other objects, returns a JSON-friendly dict and raises `bakedown.BakeDownError` with a readable message on failure. Calling `simplify()` again always starts from the original backup, so it is safe to retry with other values.

## Report fields

`triangles`, `original_triangles`, `distortion_mm`, `distortion_pct`, `baked`, `material`, `images`, `lods[]` (`name`, `level`, `triangles`, `distortion_pct`), `lod_state` (`OK` / `STALE` / `UNKNOWN`), and after export `export_dir`, `files`.

## Choosing values

| Asset | Triangles | Bake |
|---|---|---|
| Hero character / prop, close camera | 10–20k | 4096 |
| Regular character, building | 3–8k | 2048 |
| Small prop | 0.5–2k | 1024 |
| Distant background | 0.1–0.5k | 1024 |

- Check `distortion_pct` after `simplify()`: **≤ 0.5 %** usually looks identical, **0.5–1 %** is fine for mid-distance, **> 1 %** — increase `triangles` or use `distortion=0.5`.
- Leave `normal_strength` at 1.0 and `sharpen` at 0 unless the user asks otherwise — both are physically correct defaults.
- Shading (flat / smooth / by angle) is chosen automatically to match the original; do not re-shade the result.
- If baked textures show black spots, retry `bake()` with a larger `ray_distance` (local mesh units).
- For a rigged character: simplify → bake → transfer the rig in the UI → `generate_lods()`; LODs inherit the armature.
- Unity uses OpenGL normal maps (no flip); Unreal uses DirectX (`flip_normal_green=True` in `export()`); glTF never flips.

## Do not

- Do not apply your own Decimate modifier or call `bpy.ops.object.bake` directly on BakeDown objects.
- Do not delete objects or meshes whose names start with `BakeDownOrig_` — they are the originals.
- Do not report success without reading the returned report (`ok`, `triangles`, `distortion_pct`, `files`).
