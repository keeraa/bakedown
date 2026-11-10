# SPDX-License-Identifier: GPL-3.0-or-later
"""BakeDown command-line tool: heavy model in, game-ready asset + JSON report out.

Runs inside Blender without a window:

    blender -b --factory-startup --python tools/bakedown_cli.py -- \
        model.glb --out ./out --triangles 3000 --resolution 2048 --engine unity

Options (after the `--`):
    input                     .glb .gltf .fbx .obj .ply .stl or .blend
    --out DIR                 export folder (required)
    --triangles N             target triangle count            } exactly one
    --distortion PCT          distortion budget, % of object size }
    --resolution 1024|2048|4096   bake resolution (0 = skip baking; default 2048)
    --no-normal-map           do not bake a normal map
    --lods 50,25,10           also generate LOD1–LOD3 (percent of LOD0)
    --engine unity|unreal|gltf    export target (default unity)
    --object NAME             mesh to process (default: all meshes joined into one)
    --save-blend              also save the processed .blend next to the export
    --addon PATH              bakedown.py to use (default: the one next to tools/)

The last line printed to stdout is `BAKEDOWN_REPORT {json}`; the same JSON is written
to <out>/<name>/bakedown_report.json. Exit code 0 on success, 1 on failure.
"""

import argparse
import importlib.util
import json
import os
import sys
import time
import traceback

import bpy


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="bakedown_cli.py")
    p.add_argument("input")
    p.add_argument("--out", required=True)
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--triangles", type=int)
    target.add_argument("--distortion", type=float)
    p.add_argument("--resolution", type=int, default=2048, choices=(0, 1024, 2048, 4096))
    p.add_argument("--no-normal-map", action="store_true")
    p.add_argument("--lods")
    p.add_argument("--engine", default="unity", choices=("unity", "unreal", "gltf"))
    p.add_argument("--object")
    p.add_argument("--save-blend", action="store_true")
    p.add_argument("--addon")
    return p.parse_args(argv)


def _load_addon(path):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = path or os.path.join(here, "bakedown.py")
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location("bakedown", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["bakedown"] = module
        spec.loader.exec_module(module)
    else:
        import bakedown as module          # installed add-on
    if not hasattr(bpy.types.Scene, "bakedown"):
        module.register()
    return module


def _import(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    importers = {
        ".glb": lambda: bpy.ops.import_scene.gltf(filepath=path),
        ".gltf": lambda: bpy.ops.import_scene.gltf(filepath=path),
        ".fbx": lambda: bpy.ops.import_scene.fbx(filepath=path),
        ".obj": lambda: bpy.ops.wm.obj_import(filepath=path),
        ".ply": lambda: bpy.ops.wm.ply_import(filepath=path),
        ".stl": lambda: bpy.ops.wm.stl_import(filepath=path),
    }
    if ext not in importers:
        raise SystemExit(f"Unsupported input format: {ext}")
    importers[ext]()


def _pick_mesh(name):
    meshes = [o for o in bpy.context.view_layer.objects if o.type == 'MESH']
    if name:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH':
            raise SystemExit(f"Mesh object not found: {name}")
        return obj
    if not meshes:
        raise SystemExit("The input contains no mesh objects")
    if len(meshes) > 1:
        # BakeDown processes one mesh: join everything into the largest one.
        meshes.sort(key=lambda o: len(o.data.polygons), reverse=True)
        with bpy.context.temp_override(active_object=meshes[0], object=meshes[0],
                                       selected_objects=meshes, selected_editable_objects=meshes):
            bpy.ops.object.join()
    obj = meshes[0]
    if obj.parent is not None and obj.parent.type != 'ARMATURE':
        mw = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = mw
    return obj


def main():
    args = _args()
    started = time.time()
    try:
        bakedown = None
        _import(os.path.abspath(args.input))
        bakedown = _load_addon(args.addon)
        obj = _pick_mesh(args.object)
        lods = tuple(float(x) for x in args.lods.split(",")) if args.lods else None
        if lods is not None and len(lods) != 3:
            raise SystemExit("--lods needs three comma-separated percentages, e.g. 50,25,10")
        result = bakedown.process(
            obj, triangles=args.triangles, distortion=args.distortion,
            resolution=args.resolution, normal_map=not args.no_normal_map,
            lods=lods, export_dir=os.path.abspath(args.out), engine=args.engine)
        if args.save_blend:
            blend = os.path.join(result["export_dir"], f"{bakedown._safe_name(obj.name)}.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend, copy=True)
            result["files"].append(blend)
        result.update(ok=True, input=os.path.abspath(args.input),
                      seconds=round(time.time() - started, 1))
        with open(os.path.join(result["export_dir"], "bakedown_report.json"), "w") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print("BAKEDOWN_REPORT " + json.dumps(result, ensure_ascii=False), flush=True)
    except BaseException as exc:          # report SystemExit/BakeDownError the same way
        message = str(exc) or exc.__class__.__name__
        if not isinstance(exc, SystemExit):
            traceback.print_exc()
        print("BAKEDOWN_REPORT " + json.dumps({"ok": False, "error": message}), flush=True)
        sys.exit(1)


main()
