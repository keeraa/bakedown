# BakeDown — FAQ & troubleshooting

## Which models does it work with?

Any heavy mesh: AI-generated (Hunyuan, Meshy, Tripo, Rodin…), 3D scans and photogrammetry, sculpts, high-poly marketplace or kitbash models, CAD conversions. BakeDown processes one mesh at a time — the active one. If a model consists of several meshes, join them first (Ctrl+J) or process them one by one.

## How many triangles should I target?

| Asset | Triangles | Bake |
|---|---|---|
| Hero character / prop, close camera | 10–20k | 4K |
| Regular character, building | 3–8k | 2K |
| Small prop | 0.5–2k | 1K |
| Distant background | 0.1–0.5k | 1K |

Or switch to **By distortion** and set a budget — BakeDown finds the lowest triangle count that stays within it.

## What does "Approx. distortion" mean?

The largest distance between the original and the simplified surface, sampled in both directions, in millimetres and in % of the object size. As a rule of thumb: **≤ 0.5 %** looks identical, **0.5–1 %** is fine at mid distance, **> 1 %** (shown in red) is visibly different — raise the triangle count. It is an approximate sampled metric, not an exact Hausdorff distance, so always look at the model too (**Shape** mode helps).

## The bake has black spots

Rays missed the original surface. Open **2 — Texture → Settings** and increase **Ray distance** a little, then bake again. If thin details look smeared, set it back to 0 (automatic).

## The baked colours look slightly darker / sharper than the original

Check **Sharpen** (0 = off) and **Normal strength** — both change the look without a new bake (Normal strength is live).

## Can I cancel a bake?

Yes — **Cancel** or Esc. A bake pass that is already running cannot be interrupted; cancellation takes effect between maps and restores everything (mesh, UVs, materials, render settings).

## My model is rigged

Recommended order: **Simplify → Bake → Rig transfer → LOD → Export**. LODs generated after the rig inherit the armature and weights. For rig transfer the template and the target must be in the same bind pose, scale and place (Mixamo rigs import at scale 0.01 — fix that before transferring).

## The model is rotated or ×100 in Unity

Export with **Unity FBX** (1.3.0 or newer): it uses *FBX All* scaling and Unity's axes, and applies the transform for static meshes. Rigged exports keep the conversion on the object transforms, as Unity expects for skinned meshes. If you still see a −90° rotation on a rigged model, apply rotation and scale in Blender before exporting.

## Normal maps look inverted in Unreal

Unreal uses DirectX normal maps: enable **Flip normal-map green channel** when exporting for Unreal. Unity and glTF use OpenGL normal maps (no flip; the option is disabled for GLB).

## Do LODs share the textures?

Yes — LOD0–LOD3 use the same baked texture set and UVs. Objects are named `<name>_LOD0…3`, so Unity builds a LOD Group automatically. If you simplify or bake again after generating LODs, BakeDown marks them as out of date and refuses to export them until you regenerate.

## Should I triangulate?

Usually not. Engines triangulate on import and the GPU cost is the same; quads/n-gons keep the mesh easier to edit. Triangle counts in BakeDown are always real render triangles.

## Can AI agents or scripts use BakeDown?

Yes — see [AGENTS.md](../AGENTS.md): a Python API (`bakedown.process(...)`) for use inside Blender (e.g. through Blender MCP) and a command-line tool for files on disk, both returning a JSON report.

## Limitations

- Distortion is an approximate sampled metric.
- Interior-face removal uses Blender's detector, is experimental and off by default.
- Review unusual negative and non-uniform scales before engine import.
- One mesh per run (join parts first).
- Check the license of the model you process — e.g. the terms of the AI service it came from — before publishing or selling the result.
