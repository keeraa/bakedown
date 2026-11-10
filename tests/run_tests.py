# SPDX-License-Identifier: GPL-3.0-or-later
"""Headless BakeDown test suite. Run inside real Blender:

    blender -b --factory-startup --python-exit-code 1 --python tests/run_tests.py

Exits with a non-zero code when any test fails.
"""

import ast
import importlib.util
import os
import re
import sys
import tempfile
import traceback

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, "bakedown.py")

spec = importlib.util.spec_from_file_location("bakedown", ADDON)
bd = importlib.util.module_from_spec(spec)
sys.modules["bakedown"] = bd
spec.loader.exec_module(bd)

C = bpy.context
OUT = tempfile.mkdtemp(prefix="bakedown_tests_")
RESULTS = []


def test(fn):
    RESULTS.append(fn)
    return fn


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not hasattr(bpy.types.Scene, "bakedown"):
        bd.register()


def sphere(name, sub=5, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, location=loc)
    o = C.active_object
    o.name = name
    return o


def make_active(o):
    o.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    C.view_layer.objects.active = o


def simplify(o, target):
    make_active(o)
    C.scene.bakedown.target_mode = 'FACES'
    C.scene.bakedown.target_faces = target
    assert bpy.ops.object.bakedown_decimate() == {'FINISHED'}


def glb_meshes(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    names = sorted(o.name.split(".")[0] for o in new)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return names


# ---------------------------------------------------------------------------
@test
def register_cycle():
    bd.register()
    bd.unregister()
    assert bd._bakedown_load_post not in bpy.app.handlers.load_post
    bd.register()
    assert bd._bakedown_load_post in bpy.app.handlers.load_post


@test
def only_active_object_changes():
    fresh()
    a = sphere("A")
    b = sphere("B", loc=(3, 0, 0))
    polys_b = len(b.data.polygons)
    a.select_set(True)
    b.select_set(True)
    C.view_layer.objects.active = a
    C.scene.bakedown.target_faces = 2000
    assert bpy.ops.object.bakedown_decimate() == {'FINISHED'}
    assert bd._triangle_count_object(a) <= 2000
    assert len(b.data.polygons) == polys_b
    assert a.select_get() and b.select_get()


@test
def distortion_mode():
    fresh()
    o = sphere("D", 6)
    make_active(o)
    C.scene.bakedown.target_mode = 'DISTORTION'
    assert bpy.ops.object.bakedown_decimate() == {'FINISHED'}
    assert bd._triangle_count_object(o) < 81920
    assert o.get("bakedown_distort_pct") is not None


@test
def export_with_base_active_has_no_duplicate():
    fresh()
    a = sphere("A")
    simplify(a, 2000)
    assert bpy.ops.object.bakedown_lod() == {'FINISHED'}
    make_active(a)
    assert bpy.ops.object.bakedown_export(
        directory=OUT, target_engine='GLTF', save_textures=False) == {'FINISHED'}
    assert glb_meshes(os.path.join(OUT, "A", "A.glb")) == [
        "A_LOD0", "A_LOD1", "A_LOD2", "A_LOD3"]


@test
def stale_lods_are_refused():
    fresh()
    a = sphere("A")
    simplify(a, 2000)
    bpy.ops.object.bakedown_lod()
    lods = [o for o in bpy.data.collections["A_LODs"].objects]
    assert bd._lod_state(a, lods) == 'OK'
    simplify(a, 500)
    assert bd._lod_state(a, lods) == 'STALE'
    make_active(a)
    try:
        result = bpy.ops.object.bakedown_export(
            directory=OUT, target_engine='GLTF', save_textures=False)
    except RuntimeError:
        result = {'CANCELLED'}
    assert result == {'CANCELLED'}
    make_active(a)
    bpy.ops.object.bakedown_lod()
    lods = [o for o in bpy.data.collections["A_LODs"].objects]
    assert bd._lod_state(a, lods) == 'OK'


@test
def comparison_object_cannot_be_processed():
    fresh()
    a = sphere("A")
    simplify(a, 1000)
    make_active(a)
    bpy.ops.object.bakedown_compare()
    assert C.active_object.get("bakedown_compare")
    assert not bpy.ops.object.bakedown_decimate.poll()
    assert not bpy.ops.object.bakedown_bake.poll()
    bpy.ops.object.bakedown_compare()
    assert not any(o.get("bakedown_compare") for o in bpy.data.objects)


@test
def stale_bake_flag_is_cleared_on_load():
    fresh()
    sphere("S", 3)
    C.scene.bakedown.is_baking = True
    path = os.path.join(OUT, "stuck.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    assert C.scene.bakedown.is_baking is False
    assert bd._BAKE_RUNNING is False


@test
def sharpen_does_not_wrap_edges():
    import numpy as np
    fresh()
    im = bpy.data.images.new("S", 64, 64)
    px = np.zeros((64, 64, 4), np.float32)
    px[:, :32, :3] = 1.0
    px[..., 3] = 1.0
    im.pixels.foreach_set(px.ravel())
    bd._sharpen_image(im, 1.0)
    out = np.empty(64 * 64 * 4, np.float32)
    im.pixels.foreach_get(out)
    out = out.reshape(64, 64, 4)
    assert abs(out[32, 0, 0] - 1.0) < 1e-3
    assert abs(out[32, 63, 0]) < 1e-3


@test
def rigged_lods_keep_weights():
    fresh()
    o = sphere("R", 4)
    bpy.ops.object.armature_add()
    arm = C.active_object
    vg = o.vertex_groups.new(name="Bone")
    vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    o.modifiers.new("Armature", 'ARMATURE').object = arm
    simplify(o, 1000)
    assert all(v.groups for v in o.data.vertices)
    make_active(o)
    bpy.ops.object.bakedown_lod()
    lod1 = bpy.data.objects["R_LOD1"]
    assert lod1.parent == arm
    assert all(v.groups for v in lod1.data.vertices)


@test
def translations_complete():
    source = open(ADDON, encoding="utf-8").read()
    tree = ast.parse(source)
    used = set()
    for node in ast.walk(tree):
        # _tr("literal")
        if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_tr"
                and node.args and isinstance(node.args[0], ast.Constant)):
            used.add(node.args[0].value)
        # name= / description= of properties and bl_label / bl_description
        if isinstance(node, ast.keyword) and node.arg in ("name", "description"):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                used.add(node.value.value)
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and getattr(node.targets[0], "id", None) in ("bl_label", "bl_description")
                and isinstance(node.value, ast.Constant)):
            used.add(node.value.value)
    used = {s for s in used if s and not s.startswith("__")}
    table = bd._TRANSLATIONS
    placeholder = re.compile(r"\{[^}]*\}")
    problems = []
    for locale in ("ru_RU", "es", "de_DE", "zh_HANS", "zh_CN"):
        keys = {k[1] for k in table[locale]}
        for msg in sorted(used - keys):
            # internal/technical names that Blender shows untranslated anyway
            if msg in {"LOD1", "LOD2", "LOD3", "cast_shadow", "UVMap"} or msg.startswith("BakeDown  ·"):
                continue
            problems.append(f"{locale}: missing {msg!r}")
        for (_ctx, src), dst in table[locale].items():
            if placeholder.findall(src) != placeholder.findall(dst):
                problems.append(f"{locale}: placeholder mismatch in {src!r}")
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------------------
def main():
    failed = 0
    for fn in RESULTS:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} passed  (Blender {bpy.app.version_string})")
    if failed:
        sys.exit(1)


main()
