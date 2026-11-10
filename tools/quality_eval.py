# SPDX-License-Identifier: GPL-3.0-or-later
"""Measure how close a BakeDown result is to the original.

    blender -b --factory-startup --python tools/quality_eval.py -- model.glb \
        --triangles 3000 --resolution 2048 [--addon path/to/bakedown.py] [--json out.json]

Runs simplify + bake through the API, then compares original and result:
  * geometry: mean / 95th-percentile / max surface distance (% of object size), both directions
  * silhouette IoU and per-pixel error over 4 orthographic views in three modes:
      shape  — Workbench, studio light, plain colour (pure geometry shading)
      albedo — Workbench, flat light, base-colour texture
      full   — EEVEE with materials (includes the baked normal map)
  * UV utilisation of the result (share of the texture covered by UV islands)
Lower errors / higher IoU and utilisation are better.
"""

import argparse
import importlib.util
import json
import math
import os
import sys
import tempfile
import time

import bpy
import numpy as np
from mathutils import Vector


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--triangles", type=int, required=True)
    p.add_argument("--resolution", type=int, default=2048)
    p.add_argument("--addon")
    p.add_argument("--json")
    p.add_argument("--size", type=int, default=512)
    p.add_argument("--keep-renders")
    return p.parse_args(argv)


def _load(path):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = path or os.path.join(here, "bakedown.py")
    spec = importlib.util.spec_from_file_location("bakedown", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bakedown"] = mod
    spec.loader.exec_module(mod)
    if not hasattr(bpy.types.Scene, "bakedown"):
        mod.register()
    return mod


def _import(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
    meshes = [o for o in bpy.context.view_layer.objects if o.type == 'MESH']
    meshes.sort(key=lambda o: len(o.data.polygons), reverse=True)
    if len(meshes) > 1:
        with bpy.context.temp_override(active_object=meshes[0], object=meshes[0],
                                       selected_objects=meshes, selected_editable_objects=meshes):
            bpy.ops.object.join()
    obj = meshes[0]
    mw = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mw
    for o in list(bpy.data.objects):
        if o.type in {'LIGHT', 'CAMERA'}:
            bpy.data.objects.remove(o, do_unlink=True)
    return obj


def _surface_stats(bd, a_mesh, b_mesh, mw, diag):
    pts = bd._sample_mesh_points(a_mesh, mw, max_points=20000)
    tree = bd._mesh_bvh_world(b_mesh, mw)
    d = []
    for p in pts:
        hit = tree.find_nearest(p)
        if hit[0] is not None:
            d.append(hit[3])
    d = np.array(d) / diag * 100.0
    return float(d.mean()), float(np.percentile(d, 95)), float(d.max())


def _uv_utilisation(mesh):
    uv = mesh.uv_layers.active
    if uv is None:
        return 0.0
    mesh.calc_loop_triangles()
    n = len(mesh.loop_triangles)
    loops = np.empty(n * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("loops", loops)
    co = np.empty(len(mesh.loops) * 2, dtype=np.float64)
    uv.data.foreach_get("uv", co)
    co = co.reshape(-1, 2)[loops].reshape(n, 3, 2)
    a, b, c = co[:, 0], co[:, 1], co[:, 2]
    area = 0.5 * np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1]))
    return float(area.sum())


def _show_base_color_node(obj):
    """Workbench 'Texture' colour shows the active image node: make it the base colour."""
    for slot in obj.material_slots:
        m = slot.material
        if m is None or not m.use_nodes:
            continue
        bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None or not bsdf.inputs['Base Color'].is_linked:
            continue
        node = bsdf.inputs['Base Color'].links[0].from_node
        seen = 0
        while node.type != 'TEX_IMAGE' and seen < 10:
            linked = [i for i in node.inputs if i.is_linked]
            if not linked:
                break
            node = linked[0].links[0].from_node
            seen += 1
        if node.type == 'TEX_IMAGE':
            m.node_tree.nodes.active = node


def _render(scene, cam, path):
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)


def main():
    args = _args()
    t0 = time.time()
    bd = _load(args.addon)
    ref = _import(os.path.abspath(args.input))
    scene = bpy.context.scene
    low = bpy.data.objects.new("LOW", ref.data.copy())
    scene.collection.objects.link(low)
    low.matrix_world = ref.matrix_world.copy()
    bpy.context.view_layer.update()
    t1 = time.time()
    rep = bd.simplify(low, triangles=args.triangles)
    t_simplify = time.time() - t1
    t1 = time.time()
    if args.resolution:
        rep = bd.bake(low, resolution=args.resolution)
    t_bake = time.time() - t1

    mw = ref.matrix_world.copy()
    pts = [mw @ Vector(c) for c in ref.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    center, size = (mn + mx) / 2, mx - mn
    diag = size.length
    # world space for both: same transform
    lw = low.matrix_world.copy()
    fwd = _surface_stats(bd, low.data, ref.data, lw, diag)
    rev = _surface_stats(bd, ref.data, low.data, lw, diag)

    # --- renders
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    cam_data = bpy.data.cameras.new("EvalCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = max(size.x, size.y, size.z) * 1.1
    cam = bpy.data.objects.new("EvalCam", cam_data)
    scene.collection.objects.link(cam)
    sun = bpy.data.objects.new("EvalSun", bpy.data.lights.new("EvalSun", 'SUN'))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("EvalWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scene.world = world
    _show_base_color_node(ref)
    _show_base_color_node(low)
    eevee = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [
        e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    modes = {
        "shape": ('BLENDER_WORKBENCH', 'STUDIO', 'SINGLE'),
        "albedo": ('BLENDER_WORKBENCH', 'FLAT', 'TEXTURE'),
        "full": (eevee, None, None),
        # close-up of the top 25 % of the object at roughly texture resolution
        "closeup": ('BLENDER_WORKBENCH', 'FLAT', 'TEXTURE'),
        "closeup_full": (eevee, None, None),
    }
    tmp = args.keep_renders or tempfile.mkdtemp(prefix="bd_eval_")
    os.makedirs(tmp, exist_ok=True)
    out = {}
    views = [0, 90, 180, 270]
    for mode, (engine, light, color) in modes.items():
        scene.render.engine = engine
        if engine == 'BLENDER_WORKBENCH':
            sh = scene.display.shading
            sh.light = light
            sh.color_type = color
            sh.single_color = (0.8, 0.8, 0.8)
            sh.show_shadows = False
            sh.show_cavity = False
            scene.display.render_aa = '8'
        errs, ious = [], []
        close = mode.startswith("closeup")
        cam_data.ortho_scale = max(size.x, size.y, size.z) * (0.25 if close else 1.1)
        target = center + Vector((0, 0, size.z * 0.36)) if close else center
        for az in views:
            a = math.radians(az)
            dist = diag * 2
            cam.location = target + Vector((math.sin(a) * dist, -math.cos(a) * dist, 0))
            cam.rotation_euler = (math.radians(90), 0, a)
            imgs = []
            for show, name in ((ref, "ref"), (low, "low")):
                ref.hide_render = show is not ref
                low.hide_render = show is not low
                imgs.append(_render(scene, cam, os.path.join(tmp, f"{mode}_{az}_{name}.png")))
            ra, la = imgs[0][..., 3] > 0.5, imgs[1][..., 3] > 0.5
            union, inter = (ra | la).sum(), (ra & la).sum()
            ious.append(inter / union if union else 1.0)
            both = ra & la
            diff = np.abs(imgs[0][..., :3] - imgs[1][..., :3])[both].mean() * 255 if both.any() else 0
            errs.append(float(diff))
        out[mode] = {"pixel_error": round(float(np.mean(errs)), 2),
                     "silhouette_iou": round(float(np.mean(ious)), 4)}
    result = {
        "input": os.path.basename(args.input),
        "addon_version": ".".join(str(n) for n in bd.bl_info["version"]),
        "triangles_target": args.triangles,
        "triangles": rep["triangles"],
        "original_triangles": rep["original_triangles"],
        "distortion_pct_reported": round(rep["distortion_pct"], 3),
        "surface_mean_pct": round((fwd[0] + rev[0]) / 2, 4),
        "surface_p95_pct": round(max(fwd[1], rev[1]), 4),
        "surface_max_pct": round(max(fwd[2], rev[2]), 4),
        "uv_utilisation": round(_uv_utilisation(low.data), 3),
        "renders": out,
        "seconds_simplify": round(t_simplify, 2),
        "seconds_bake": round(t_bake, 2),
        "seconds_total": round(time.time() - t0, 1),
    }
    text = json.dumps(result, indent=2)
    print("QUALITY " + json.dumps(result))
    if args.json:
        with open(args.json, "w") as fh:
            fh.write(text)


main()
