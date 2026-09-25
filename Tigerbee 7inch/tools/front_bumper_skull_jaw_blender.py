"""Standalone sculpt pass for the skull-jaw bumper - the same strokes, outside the pipeline.

    blender --background --factory-startup --python tools/front_bumper_skull_jaw_blender.py -- job.json

`job.json` is what src/tigerbee/accessories/front_bumper_skull_jaw.py writes:

    {"base": "build/skull_jaw/full/base.stl",     # the parametric base, STL, frame coordinates
     "voxel": 0.4,                                # <= min_wall / 3
     "tri_budget": 12000,                         # decimated down to this (hard ceiling 20000)
     "wall_floor": 1.2,                           # the material's minimum wall, measured on the mesh
     "strokes": [{"points": [[x, y, z], ...], "radii": [r, ...]}, ...],
     "out": "build/skull_jaw/full/skull.stl"}

It imports the base, sweeps every stroke as a TAPERED BEZIER (curve + bevel depth + per-point
radius), JOINS the sweeps to the base BEFORE the voxel remesh so the junctions are faired rather
than butted, remeshes, decimates to the budget, and prints ONE line the module parses:

    [SKULLJAW] {"verts": ..., "tris": ..., "is_manifold": true, "components": 1, "bbox": [...]}

Why it exists next to `_blender.decorate(recipe="sculpt")`, which builds the geometry that ships:
it is the independent second opinion. The module runs it on the same base with the same strokes and
compares - and the regeneration check deletes its output and runs it again, which is the only real
proof that the sculpt is deterministic.

TRAPS, all of them hit at least once here:
  * Blender 5.2 exports with bpy.ops.wm.stl_export / imports with wm.stl_import. bpy.ops.export_mesh
    .stl does not exist any more.
  * bpy.ops.object.convert acts on the SELECTION, not on the active object. Select explicitly.
  * bmesh sequences need ensure_lookup_table() before they can be indexed.
  * MANIFOLD DOES NOT MEAN CONNECTED. Four closed blobs pass every manifold test and print as four
    loose lumps, so `components` is counted and reported separately.
  * Deterministic by construction: fixed ordering, no random, no viewport operators, no seeds.

The harmless cattrs / EXTENSIONS_OT_repo_sync tracebacks Blender prints at startup are not ours.
"""

import json
import os
import sys

import bmesh
import bpy

TAG = "[SKULLJAW] "
# The package's own mesh-ray wall sampler, imported (never edited): it carries the two filters this
# measurement needs - grazing rays on a fillet facet otherwise report 0.0018 mm on a 4 mm wall, and
# a 0.02 mm² sliver is not a wall. _fit.min_wall cannot stand in for it here: OCCT refuses to offset
# this plate's spline outline at all ("Null TopoDS_Shape"), and _fit's own ray fallback has neither
# filter and reports 0.29 mm on a plain 2.5 mm plate.
_BL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "src", "tigerbee", "accessories", "_bl")
sys.path.insert(0, _BL)
try:
    from bl_lib import wall_thickness_report
except Exception:  # noqa: BLE001 - report it rather than dying; the module reads the reason
    wall_thickness_report = None


def argv_job():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    assert args, "usage: blender --background --python this.py -- job.json"
    return json.loads(open(args[0]).read())


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.objects):
        for item in list(block):
            block.remove(item)


def import_stl(path, name):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=1.0, use_scene_unit=False,
                          forward_axis="Y", up_axis="Z")
    obj = [o for o in bpy.data.objects if o not in before][0]
    obj.name = name
    return obj


def select_only(obj):
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_all(obj):
    select_only(obj)
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def merge_and_fix(obj, dist=1e-4):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()


def sweep(stroke, index):
    """One tapered sweep: a POLY spline with a per-point radius and a round bevel."""
    pts = [tuple(float(v) for v in q) for q in stroke["points"]]
    radii = [float(r) for r in stroke.get("radii", [1.0] * len(pts))]
    assert len(pts) >= 2 and len(radii) == len(pts), f"stroke {index}: {len(pts)} points, {len(radii)} radii"
    cu = bpy.data.curves.new(f"cu{index}", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = max(radii)
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    rmax = max(radii) or 1.0
    for i, (q, r) in enumerate(zip(pts, radii)):
        sp.points[i].co = (*q, 1.0)
        sp.points[i].radius = r / rmax
    obj = bpy.data.objects.new(f"stroke{index}", cu)
    bpy.context.collection.objects.link(obj)
    select_only(obj)
    bpy.ops.object.convert(target="MESH")          # acts on the SELECTION
    obj = bpy.context.view_layer.objects.active
    merge_and_fix(obj)
    return obj


def union(part, other):
    m = part.modifiers.new("bool", "BOOLEAN")
    m.operation, m.object, m.solver = "UNION", other, "MANIFOLD"
    apply_all(part)


def remesh(part, voxel):
    m = part.modifiers.new("vx", "REMESH")
    m.mode, m.voxel_size, m.adaptivity = "VOXEL", float(voxel), 0.0
    apply_all(part)


def decimate(part, budget):
    tris = sum(len(f.vertices) - 2 for f in part.data.polygons)
    if tris <= budget:
        return tris
    m = part.modifiers.new("dec", "DECIMATE")
    m.decimate_type, m.ratio = "COLLAPSE", max(0.05, budget / tris)
    apply_all(part)
    return sum(len(f.vertices) - 2 for f in part.data.polygons)


def report(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    vol = bm.calc_volume(signed=True)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    seen, comps = set(), 0
    for v in bm.verts:                      # MANIFOLD DOES NOT MEAN CONNECTED
        if v.index in seen:
            continue
        comps += 1
        stack = [v]
        seen.add(v.index)
        while stack:
            cur = stack.pop()
            for e in cur.link_edges:
                nxt = e.other_vert(cur)
                if nxt.index not in seen:
                    seen.add(nxt.index)
                    stack.append(nxt)
    bb = [round(c, 4) for c in (
        min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts),
        max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts))]
    out = {"verts": len(bm.verts), "tris": tris, "faces": len(bm.faces),
           "is_manifold": nonman == 0 and boundary == 0, "non_manifold_edges": nonman,
           "boundary_edges": boundary, "components": comps, "volume_mm3": round(vol, 3), "bbox": bb}
    bm.free()
    return out


def export_stl(obj, path):
    select_only(obj)
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0,
                          use_scene_unit=False, apply_modifiers=True, ascii_format=False,
                          forward_axis="Y", up_axis="Z")


def main():
    job = argv_job()
    clear_scene()
    part = import_stl(job["base"], "base")
    merge_and_fix(part)
    made = [sweep(st, i) for i, st in enumerate(job.get("strokes", []))]
    for obj in made:                        # join BEFORE the remesh, so the junctions are faired
        union(part, obj)
        bpy.data.objects.remove(obj, do_unlink=True)
    remesh(part, job.get("voxel", 0.4))
    merge_and_fix(part)
    tris = decimate(part, int(job.get("tri_budget", 12000)))
    merge_and_fix(part)
    rep = report(part)
    rep["strokes"] = len(made)
    rep["decimated_to"] = tris
    floor = float(job.get("wall_floor", 1.2))
    if wall_thickness_report is None:
        rep["wall"] = {"ok": False, "reason": "bl_lib.wall_thickness_report unavailable"}
    else:
        rep["wall"] = wall_thickness_report(part, floor)
    rep["wall_floor"] = floor
    if job.get("out"):
        export_stl(part, job["out"])
        rep["out"] = job["out"]
    print(TAG + json.dumps(rep, sort_keys=True))


if __name__ == "__main__":
    main()
