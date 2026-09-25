"""Runs INSIDE Blender 5.2.2: one script, six recipes, dispatched by params["recipe"].

    blender --background --factory-startup --python recipe.py -- params.json

params.json carries: recipe, out (result path), part/guard/region/cuts STL paths, wall_floor,
tri_budget, ngon, plus the recipe's own parameters. Everything the bridge needs comes back on
`[BL] ...` lines; the mesh comes back as `out`.

The six recipes and the rule each one is safe by:
  elytra_dome      mode="top": only the OUTWARD skin moves, so the wall can only get thicker
  carapace_lattice r = (D - w)/2 on the CIRCUMRADIUS, so the ligament is D - 2r by arithmetic
  chitin           mid_level 0.0 + direction "Z" + amplitude <= period/12
  sculpt           voxel remesh at <= min_wall/3, joined to the base BEFORE remeshing
  emboss           SHRINKWRAP PROJECT (not NEAREST_SURFACEPOINT) + SOLIDIFY straddling the surface
  hardshell        BEVEL by weight + WEIGHTED_NORMAL on UNDISPLACED geometry only
"""

import math
import os
import random
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bl_lib import (apply_all, args, boolean, boolean_checked, dissolve_ngons,  # noqa: E402
                    manifold_counts,
                    export_obj, export_stl, import_stl, log, make_protect_group,
                    promote_faces_outside, report, repair,
                    scaled_texture_coords, setup_scene, subdivide_masked, upward_group,
                    wall_thickness_report)


# --- shared plumbing --------------------------------------------------------------------------
def load(p):
    """(part, guard, region, cuts, allow) - everything but `part` may be None."""
    part = import_stl(p["part"], "part")
    repair(part)
    guard = import_stl(p["guard"], "guard") if p.get("guard") else None
    region = import_stl(p["region"], "region") if p.get("region") else None
    cuts = import_stl(p["cuts"], "cuts") if p.get("cuts") else None
    allow = import_stl(p["allow"], "allow") if p.get("allow") else None
    for o in (guard, region, cuts, allow):
        if o is not None:
            repair(o)
            o.hide_set(True)
    return part, guard, region, cuts, allow


def protect(part, guard, feather=3.0, axis=None):
    """`axis` makes the feather a LATERAL run-out instead of a 3D distance; see make_protect_group.
    Pass it from the outward-skin path (`prepare`), where the guard backs the displaced face."""
    if guard is None:
        vg = part.vertex_groups.new(name="protect")
        for v in part.data.vertices:
            vg.add([v.index], 1.0, "REPLACE")
        return vg
    return make_protect_group(part, guard, inner=0.0, feather=feather, axis=axis)


def prepare(part, guard, subdiv, feather, min_nz, axis="Z"):
    """Mask, subdivide, RE-mask, then take the outward skin.

    The two masks do DIFFERENT jobs and are measured differently. The first one only decides which
    faces may be subdivided, so it keeps the 3D distance: a coarse mesh has vertices only at the
    corners of big flat faces, and on the LATERAL measure those all sit on the region's border with
    clearance 0 - which froze all 204 of them, tripped the "fully masked" fallback into subdividing
    the mating triangles as well, and handed OCCT a shell it could not sew ("BRepCheck_Analyzer says
    invalid", measured). The second mask is the one the modifiers are actually gated on, and it is
    LATERAL (see make_protect_group): this is the outward-skin path, `upward_group` below already
    stops anything but the outward faces moving, and a guard that backs the displaced face would
    otherwise cap every weight at (its depth)/feather - the bug that made the dome deliver a tenth
    of its rise.

    The second protect() is not redundant: bmesh.ops.subdivide_edges does NOT interpolate custom
    deform layers, so every vertex it creates lands in the protect group at weight 0. The only
    vertices left with weight 1 are then the original ones - which on a plate all sit on the
    OUTLINE, where a centred spherical blend is already ~0. Measured symptom: a dome that displaces
    exactly nothing (max Z 40.000 before and after) while the identical setup on an unmasked
    subdivision rises 1.3 mm. Re-running the mask is a cheap BVH distance query and exact."""
    protect(part, guard, feather=feather)                    # coarse mask: keep mating triangles whole
    before = len(part.data.polygons)
    subdivide_masked(part, levels=subdiv, group="protect")
    if len(part.data.polygons) == before and guard is not None:
        # No face had a free VERTEX - which on a coarse mesh usually means the faces are big and all
        # their corners sit on the region's border, not that there is nothing to decorate. Promote by
        # face CENTRE and try again; only if that still finds nothing is the part genuinely all
        # guard. Subdividing unmasked was the old fallback and it is the last resort, not the first:
        # it cuts the mating triangles up as well, and with restore=False nothing puts them back.
        promote_faces_outside(part, guard)
        subdivide_masked(part, levels=subdiv, group="protect")
    if len(part.data.polygons) == before:
        log("warn", {"subdivide": "coarse mesh fully masked, subdividing unmasked"})
        subdivide_masked(part, levels=subdiv, group=None)
    protect(part, guard, feather=feather, axis=axis)         # re-mask the subdivided mesh
    return upward_group(part, min_nz=min_nz, axis=axis)


def clip_to_region(cutter, region):
    """Let the CAD define where decoration may go. Ray-probing the border from Blender is guesswork;
    without this clip a border Voronoi cell runs straight through the rounded outline."""
    if region is None:
        return
    m = cutter.modifiers.new("clip", "BOOLEAN")
    m.operation, m.object, m.solver = "INTERSECT", region, "MANIFOLD"
    apply_all(cutter)


def new_mesh_obj(name, verts, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    return obj


def budget(part, tri_budget):
    """Decimate down to the triangle budget. OCCT sewing is the ENTIRE cost of the round trip and
    grows ~quadratically: 12 000 tris rebuilt in 13.8 s on one run and 115.6 s on another."""
    me = part.data
    tris = sum(len(f.vertices) - 2 for f in me.polygons)   # MeshPolygon.vertices, not .verts
    if tris <= tri_budget:
        return tris
    m = part.modifiers.new("dec", "DECIMATE")
    m.decimate_type, m.ratio = "COLLAPSE", max(0.05, tri_budget / tris)
    apply_all(part)
    return sum(len(f.vertices) - 2 for f in part.data.polygons)


# --- 1. elytra_dome ---------------------------------------------------------------------------
def elytra_dome(part, guard, region, p):
    """A domed elytral shell. mode="top" is the only thickness-safe mode: DISPLACE with
    mid_level 0.0 on the upward skin adds material outward and nothing else.

    Rejected, with evidence: SIMPLE_DEFORM BEND rotates the whole plate (measured Z -13.1..+13.1),
    so the bolt axes stop being vertical - freezing vertices does not help because the surrounding
    material tilts the bore - and it flipped the solid orientation, after which the re-boolean
    produced -24770 mm3. CAST on a closed thin shell pinched the wall to 0.0018 mm."""
    # min_nz 0.75, not 0.5: 0.5 catches the outline fillet faces too, and displacing those pushes a
    # 0.18 mm lip out of the rim (measured against a 1.5 mm floor).
    axis = p.get("axis", "Z").upper()
    prepare(part, guard, int(p.get("subdiv", 2)), float(p.get("feather", 3.0)),
            float(p.get("min_nz", 0.75)), axis=axis)
    co = [v.co for v in part.data.vertices]
    lo = {a: min(getattr(v, a.lower()) for v in co) for a in "XYZ"}
    hi = {a: max(getattr(v, a.lower()) for v in co) for a in "XYZ"}
    others = [a for a in "XYZ" if a != axis]
    rise = float(p.get("rise", 0.0))
    if rise <= 0.0:
        span = max(hi[a] - lo[a] for a in others)
        rise = float(p.get("rise_span", 0.32)) * span * 0.5
    tex = bpy.data.textures.new("domeprofile", type="BLEND")
    tex.progression, tex.use_clamp = "SPHERICAL", True
    d = part.modifiers.new("dome", "DISPLACE")
    d.texture, d.direction = tex, axis
    d.mid_level, d.strength, d.vertex_group = 0.0, rise, "upward"   # mid_level 0.0 => OUTWARD ONLY
    # The texture must be CENTRED AND SCALED ON THE PART. With texture_coords="GLOBAL" a SPHERICAL
    # BLEND is evaluated from the world origin, which for a part at Z 36 is far outside the clamped
    # unit sphere: the displacement comes out exactly zero and the only thing that changes the part
    # is the relax pass (measured: max Z unmoved at 40.00, volume ratio 0.93 from smoothing alone).
    empty = bpy.data.objects.new("domecentre", None)
    bpy.context.collection.objects.link(empty)
    empty.location = tuple((lo[a] + hi[a]) / 2 for a in "XYZ")
    spread = float(p.get("dome_spread", 1.0))
    # `flat` names axes the profile must NOT vary along: their texture scale is made huge, so the
    # blend is constant there and the swell becomes a ridge instead of a blister. On a vertical wall
    # printed Z-up that is what keeps the bulge's underside from becoming an unsupported overhang.
    flat = [a.upper() for a in p.get("flat", ())]
    half = {a: max((hi[a] - lo[a]) / 2, 1e-3) for a in "XYZ"}
    big = 40.0 * max(half.values())
    empty.scale = tuple(big if (a == axis or a in flat) else half[a] / spread for a in "XYZ")
    d.texture_coords, d.texture_coords_object = "OBJECT", empty
    bpy.context.view_layer.update()   # without this the empty's matrix_world is still the identity
    # when the modifier is applied, texture space collapses back to world space, and a part at Z 36
    # maps far outside the clamped unit sphere - the dome comes out exactly flat (measured)
    sm = part.modifiers.new("relax", "SMOOTH")
    sm.factor, sm.iterations, sm.vertex_group = 0.5, int(p.get("relax", 6)), "upward"
    apply_all(part)
    log("recipe", {"elytra_dome": {"rise": round(rise, 3), "mode": "top"}})
    return part, False   # ngon dissolve is unsafe on curvature


# --- 2. carapace_lattice ----------------------------------------------------------------------
def _poisson(x0, y0, x1, y1, d, seed):
    rng = random.Random(seed)
    target = max(4, int((x1 - x0) * (y1 - y0) / (0.72 * d * d)))
    pts = []
    for _ in range(target * 60):
        if len(pts) >= target * 2:
            break
        q = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if all(math.hypot(q[0] - r[0], q[1] - r[1]) >= d for r in pts):
            pts.append(q)
    return pts


def _clip(poly, px, py, nx, ny, offset):
    out = []
    for a in range(len(poly)):
        A, B = poly[a], poly[(a + 1) % len(poly)]
        da = (A[0] - px) * nx + (A[1] - py) * ny - offset
        db = (B[0] - px) * nx + (B[1] - py) * ny - offset
        if da <= 0:
            out.append(A)
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t))
    return out


def carapace_lattice(part, guard, region, p):
    """A cell field with a GUARANTEED ligament. The guarantee is arithmetic, not hope:

      sample cell centres with Poisson-disk minimum separation D, cut a cell of CIRCUMRADIUS r,
      then the material between any two cells is at least D - 2r, so r = (D - w)/2 for a target w.

    Measured: w 1.6 -> 1.8014, w 1.2 -> 1.2239, hex w 2.0 -> 2.542, voronoi w 1.6 -> 1.6000.
    Two bugs this encodes the fix for: using the INRADIUS for a hex gives 1.57 against a 2.0
    target, and "insetting" a Voronoi cell by scaling its vertices toward the centroid removes
    91 % of the volume and leaves 0.45 mm walls - the inset must offset each bisector HALF PLANE."""
    cell = p.get("cell", "round")
    w = float(p.get("ligament", 1.6))
    # `axis` is the direction the cell prisms run - the part's THICKNESS direction. "Z" for a plate on
    # the bed, "X" for a vertical side wall. The cells themselves live in the other two axes, so this
    # is not cosmetic: prisms extruded along Z through a wall standing in the YZ plane cut nothing.
    axis = p.get("axis", "Z").upper()
    ai = "XYZ".index(axis)
    order = [i for i in range(3) if i != ai] + [ai]   # (u, v, h): cell plane first, prism last
    co = [(v.co.x, v.co.y, v.co.z) for v in part.data.vertices]
    lo = [min(c[i] for c in co) for i in range(3)]
    hi = [max(c[i] for c in co) for i in range(3)]
    x0, x1 = lo[order[0]], hi[order[0]]
    y0, y1 = lo[order[1]], hi[order[1]]
    z0, z1 = lo[order[2]], hi[order[2]]

    def place(u, v, h):
        """(u, v) in the cell plane and h along the prism -> a world xyz tuple."""
        out = [0.0, 0.0, 0.0]
        out[order[0]], out[order[1]], out[order[2]] = u, v, h
        return tuple(out)
    D = float(p.get("cell_d", 0.0)) or max(5.0, 4.5 * w)
    seed = int(p.get("seed", 7))
    pts = _poisson(x0, y0, x1, y1, D, seed)
    if len(pts) >= 2:
        sep = min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
        assert sep >= D - 1e-6, f"poisson property violated: {sep} < {D}"
    verts, faces = [], []
    h0, h1 = z0 - 2.0, z1 + 2.0
    if cell == "voronoi":
        inset = w / 2 + 0.1   # an exact inset lands ON the floor, which fails a >= test
        pad = 2 * D
        frame = [(x0 - pad, y0 - pad), (x1 + pad, y0 - pad), (x1 + pad, y1 + pad), (x0 - pad, y1 + pad)]
        polys = []
        for i, (px, py) in enumerate(pts):
            poly = list(frame)
            for j, (qx, qy) in enumerate(pts):
                if i == j:
                    continue
                dx, dy = qx - px, qy - py
                n = math.hypot(dx, dy)
                poly = _clip(poly, (px + qx) / 2, (py + qy) / 2, dx / n, dy / n, -inset)
                if len(poly) < 3:
                    break
            if len(poly) >= 3:
                polys.append(poly)
    else:
        r = (D - w) / 2.0                       # CIRCUMRADIUS, every cell shape
        sides = 6 if cell == "hex" else int(p.get("sides", 16))
        polys = []
        rng = random.Random(seed + 1)
        for (px, py) in pts:
            a0 = rng.uniform(0, 2 * math.pi) if cell == "hex" else 0.0
            polys.append([(px + r * math.cos(a0 + 2 * math.pi * k / sides),
                           py + r * math.sin(a0 + 2 * math.pi * k / sides)) for k in range(sides)])
    for poly in polys:
        base = len(verts)
        n = len(poly)
        verts += [place(x, y, h0) for x, y in poly] + [place(x, y, h1) for x, y in poly]
        faces.append(list(range(base, base + n)))
        faces.append(list(range(base + 2 * n - 1, base + n - 1, -1)))
        for k in range(n):
            faces.append([base + k, base + (k + 1) % n, base + n + (k + 1) % n, base + n + k])
    if not faces:
        log("recipe", {"carapace_lattice": "no cells"})
        return part, True
    cutter = new_mesh_obj("lattice", verts, faces)
    repair(cutter)
    clip_to_region(cutter, region)
    if guard is not None and region is None:
        # Only when no region was given. Doing BOTH puts cell faces exactly on the guard's surface,
        # and the second boolean against the part then leaves non-manifold slivers there (measured: 1
        # to 14 non-manifold edges depending on the seed). A region built as
        # decor_region(part, ligament, minus=(guard,)) already excludes the clean zone, and should
        # exclude a slightly PADDED guard so no cutter face is coincident with it at all.
        boolean(cutter, guard, "DIFFERENCE")
    repair(cutter)                              # merge and re-orient after the clip, before cutting
    v0 = sum(1 for _ in part.data.polygons)
    solver = boolean_checked(part, cutter, "DIFFERENCE")
    bpy.data.objects.remove(cutter, do_unlink=True)
    assert solver, "no boolean solver produced a manifold cell field"
    log("recipe", {"carapace_lattice": {"cell": cell, "cells": len(polys), "D": round(D, 3),
                                        "ligament": w, "axis": axis, "faces_before": v0}})
    return part, cell != "round"


# --- 3. chitin --------------------------------------------------------------------------------
def chitin(part, guard, region, p):
    """Segmented ridge bands. Safe by construction from three rules, all measured:
      1. mid_level 0.0 (Blender's default 0.5 makes displacement bipolar - the usual cause of a
         texture eating a wall). With a clamped texture and positive strength material is only ADDED.
      2. the outward skin only, so opposing surfaces never approach.
      3. direction "Z", not "NORMAL". On a plate's rim the surface normal is nearly horizontal, so
         a NORMAL displacement pushes material sideways into a 0.005 mm flange. Locking the axis
         fixes it; a border feather does NOT.
    And the slope rule: amplitude <= period/12 (A/P <= 0.08). At A/P >= 0.1 thin ridges appear."""
    period = float(p.get("period", 12.0))
    amp = min(float(p.get("amplitude", 0.8)), period / 12.0)
    axis = p.get("axis", "Z").upper()
    prepare(part, guard, int(p.get("subdiv", 2)), float(p.get("feather", 3.0)),
            float(p.get("min_nz", 0.7)), axis=axis)          # ONE mask, ONE direction lock:
    # three stacked masks multiplied the weights to ~0 and the displacement did nothing (ratio 1.0000)
    tex = bpy.data.textures.new("chitin", type=p.get("texture", "WOOD").upper())
    if tex.type == "WOOD":
        tex.wood_type, tex.noise_basis_2 = "BANDS", "SIN"
    tex.use_clamp = True
    d = part.modifiers.new("ridges", "DISPLACE")
    d.texture, d.direction, d.mid_level, d.strength = tex, axis, 0.0, amp
    d.vertex_group = "upward"
    scaled_texture_coords(part, d, period)
    apply_all(part)
    log("recipe", {"chitin": {"amplitude": amp, "period": period, "A_over_P": round(amp / period, 4)}})
    return part, False


# --- 4. sculpt --------------------------------------------------------------------------------
def sculpt(part, guard, region, p):
    """Mandibles, claws, legs. The voxel remesh is NOT optional: a curve bevel self-intersects at
    tight radii, SKIN makes non-manifold junctions and metaballs tessellate coarsely. Measured min
    wall tracks 1.3-2.6 x voxel_size, so voxel <= min_wall/3. Cost: voxel 0.35 -> 19 k tris,
    voxel 0.15 -> 103 k. Join the sculpt to the base BEFORE remeshing so the junction is faired
    rather than a butt joint the slicer sees as two shells.

    Trap: bpy.ops.object.convert acts on SELECTED objects, not the active one."""
    mode = p.get("mode", "curve")
    voxel = float(p.get("voxel", 0.35))
    strokes = p.get("strokes") or []
    made = []
    for si, st in enumerate(strokes):
        pts = [tuple(map(float, q)) for q in st["points"]]
        radii = [float(r) for r in st.get("radii", [1.0] * len(pts))]
        if mode == "meta":
            mb = bpy.data.metaballs.new(f"mb{si}")
            mb.resolution = max(0.08, voxel * 0.8)
            obj = bpy.data.objects.new(f"meta{si}", mb)
            bpy.context.collection.objects.link(obj)
            for q, r in zip(pts, radii):
                el = mb.elements.new()
                el.co, el.radius = q, r
        elif mode == "skin":
            obj = new_mesh_obj(f"skin{si}", pts, [])
            me = obj.data
            me.edges.add(len(pts) - 1)
            for i, e in enumerate(me.edges):
                e.vertices = (i, i + 1)
            me.update()
            m = obj.modifiers.new("skin", "SKIN")
            m.use_smooth_shade = True
            bpy.context.view_layer.objects.active = obj
            for v, r in zip(obj.data.skin_vertices[0].data, radii):
                v.radius = (r, r)
        else:  # curve: a tapered bezier sweep, the sickle mandible
            cu = bpy.data.curves.new(f"cu{si}", "CURVE")
            cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", max(radii), 4
            cu.use_fill_caps = True
            sp = cu.splines.new("POLY")
            sp.points.add(len(pts) - 1)
            rmax = max(radii) or 1.0
            for i, (q, r) in enumerate(zip(pts, radii)):
                sp.points[i].co = (*q, 1.0)
                sp.points[i].radius = r / rmax
            obj = bpy.data.objects.new(f"curve{si}", cu)
            bpy.context.collection.objects.link(obj)
        for o in bpy.data.objects:
            o.select_set(False)
        obj.select_set(True)                       # convert() acts on the SELECTION
        bpy.context.view_layer.objects.active = obj
        if obj.type != "MESH":
            bpy.ops.object.convert(target="MESH")
            obj = bpy.context.view_layer.objects.active
        else:
            apply_all(obj)
        made.append(obj)
    if not made:
        log("recipe", {"sculpt": "no strokes"})
        return part, True
    for o in made:                                 # join to the base BEFORE remeshing
        boolean(part, o, "UNION")
        bpy.data.objects.remove(o, do_unlink=True)
    m = part.modifiers.new("vx", "REMESH")
    m.mode, m.voxel_size, m.adaptivity = "VOXEL", voxel, 0.0
    apply_all(part)
    log("recipe", {"sculpt": {"mode": mode, "voxel": voxel, "strokes": len(strokes)}})
    return part, False


# --- 5. emboss --------------------------------------------------------------------------------
def emboss(part, guard, region, p):
    """Constant-depth engraving on a curved surface. A plain extruded prism meets a curved surface
    at a varying angle, so a "0.6 mm" groove is 0.6 mm only where the surface is flat.

    Use PROJECT, not NEAREST_SURFACEPOINT: measured 0.651 vs 0.0004 mm, because NEAREST pulls mark
    vertices onto whatever surface is closest, including the sides of the dome. In 5.2 the axis is
    chosen by use_project_x/y/z booleans - there is no project_axis enum.

    A RAISED mark on a dome comes back non-manifold (the solidified wrapped mark self-intersects at
    letter counters), so `raised` runs the EXACT solver and re-checks."""
    depth = float(p.get("depth", 0.6))
    raised = bool(p.get("raised", False))
    mark_path = p.get("mark")
    if not mark_path:
        log("recipe", {"emboss": "no mark mesh"})
        return part, True
    mark = import_stl(mark_path, "mark")
    repair(mark)
    subdivide_masked(mark, levels=int(p.get("mark_subdiv", 3)))
    sw = mark.modifiers.new("wrap", "SHRINKWRAP")
    sw.target, sw.wrap_method = part, "PROJECT"
    sw.use_project_x = sw.use_project_y = False
    sw.use_project_z = True
    sw.use_negative_direction = sw.use_positive_direction = True
    sw.project_limit = 0.0
    apply_all(mark)
    so = mark.modifiers.new("thick", "SOLIDIFY")
    so.thickness, so.offset, so.use_even_offset = depth * 2.0, 0.0, True   # straddle the surface
    apply_all(mark)
    repair(mark)
    boolean(part, mark, "UNION" if raised else "DIFFERENCE", "EXACT" if raised else "MANIFOLD")
    bpy.data.objects.remove(mark, do_unlink=True)
    log("recipe", {"emboss": {"depth": depth, "raised": raised}})
    return part, False


# --- 6. hardshell -----------------------------------------------------------------------------
def hardshell(part, guard, region, p):
    """Bevel + weighted normals on UNDISPLACED geometry. Bevel AFTER a displacement is unsafe: width
    0.3 on a noisy displaced surface produced a non-manifold 46 471-tri result, and in a milder case
    3 thin rays at 0.79 mm.

    It bevels only the edges it is TOLD to, by weight, never every edge by angle. Bevelling every
    edge of an ordinary CAD part explodes the rebuilt B-rep: a 54-face panel came back with 1234
    faces, every check that walks them slowed to 23 s, and - the real damage - OCCT's booleans became
    unreliable on the result, silently answering 0 mm3 to an interior probe that is 12.5 mm3 of solid
    material. Selecting by length keeps the count near the original and the booleans exact.

    Selection: edges at least `min_len` long whose two faces meet at more than `angle`, excluding any
    edge with a vertex inside the guard (weight 0 there), i.e. the long creases of the silhouette."""
    width = float(p.get("width", 0.4))
    min_len = float(p.get("min_len", 6.0))
    angle = math.radians(float(p.get("angle", 35.0)))
    protect(part, guard, feather=float(p.get("feather", 1.5)))
    me = part.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    layer = bm.verts.layers.deform.verify()
    vg_idx = part.vertex_groups["protect"].index
    # Blender 4.x+ carries the bevel weight as a named float attribute, not edge.bevel_weight
    bw = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    picked = 0
    for e in bm.edges:
        if e.calc_length() < min_len or len(e.link_faces) != 2:
            continue
        if e.calc_face_angle(0.0) < angle:
            continue
        if any(v[layer].get(vg_idx, 0.0) <= 1e-6 for v in e.verts):
            continue                      # a mating feature's own edge: leave it exact
        e[bw] = 1.0
        picked += 1
    bm.to_mesh(me)
    bm.free()
    me.update()
    b = part.modifiers.new("bev", "BEVEL")
    b.width, b.segments, b.limit_method = width, int(p.get("segments", 2)), "WEIGHT"
    b.miter_outer = "MITER_ARC"
    b.harden_normals = False
    wn = part.modifiers.new("wn", "WEIGHTED_NORMAL")
    wn.keep_sharp = True
    apply_all(part)
    log("recipe", {"hardshell": {"width": width, "min_len": min_len, "edges": picked}})
    return part, True


# --- 7. gyroid --------------------------------------------------------------------------------
# Blender 5.2.2's bundled Python has NO numpy / scipy / skimage (verified), so the iso-surface is
# hand-built exactly like carapace_lattice's vert/face cutter: MARCHING TETRAHEDRA, 6 tets per grid
# cube sharing the 0-6 diagonal. Two interpolation cases only (1-vs-3 -> one triangle, 2-vs-2 -> two),
# so there is no 256-entry table to get wrong, and the shared diagonal makes neighbouring cubes agree
# on every face -> the surface is watertight apart from its rim at the grid boundary, which SOLIDIFY
# caps. Vertices are cached per grid EDGE (not per tet), which is what keeps it welded.
_GY_CORNERS = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))
_GY_TETS = ((0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6))


def _iso_tets(V, lo, h, n):
    """The zero set of a scalar grid `V` by MARCHING TETRAHEDRA: 6 tets per cube sharing the 0-6
    diagonal, so neighbouring cubes agree on every shared face and the surface comes out watertight.
    Two interpolation cases only - 1 vs 3 corners gives one triangle, 2 vs 2 gives two - which is why
    there is no 256-entry table here to get wrong. Vertices are cached per grid EDGE, not per tet,
    and that is what welds it. `V[i][j][m] < 0` is INSIDE."""
    n0, n1, n2 = n
    verts, faces, cache = [], [], {}

    def cut(a, b):
        key = (a, b) if a < b else (b, a)
        got = cache.get(key)
        if got is not None:
            return got
        (i0, j0, m0), (i1, j1, m1) = key
        va, vb = V[i0][j0][m0], V[i1][j1][m1]
        t = 0.5 if abs(vb - va) < 1e-12 else va / (va - vb)
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        verts.append((lo[0] + h * (i0 + t * (i1 - i0)), lo[1] + h * (j0 + t * (j1 - j0)),
                      lo[2] + h * (m0 + t * (m1 - m0))))
        cache[key] = len(verts) - 1
        return cache[key]

    for i in range(n0):
        for j in range(n1):
            for m in range(n2):
                g = [(i + dx, j + dy, m + dz) for dx, dy, dz in _GY_CORNERS]
                v = [V[a][b][c] for a, b, c in g]
                if min(v) >= 0.0 or max(v) < 0.0:
                    continue          # the whole cube is on one side: no tet in it can cross
                for tet in _GY_TETS:
                    neg = [t for t in tet if v[t] < 0.0]
                    pos = [t for t in tet if v[t] >= 0.0]
                    if not neg or not pos:
                        continue
                    # OUTWARD is decided by the field, never by a later recalc_face_normals: on a
                    # tangled two-network void Blender's recalc flipped a whole component, the
                    # DIFFERENCE then behaved as a UNION and the part came back 19 200 + 8 932 mm3
                    # instead of 19 200 - 8 932. `out` points from the inside corners to the outside
                    # ones, and any triangle whose winding disagrees is reversed here.
                    out = [sum(g[t][i] for t in pos) / len(pos) - sum(g[t][i] for t in neg) / len(neg)
                           for i in range(3)]
                    if len(neg) == 1 or len(pos) == 1:
                        a = neg[0] if len(neg) == 1 else pos[0]
                        rest = pos if len(neg) == 1 else neg
                        tris = [[cut(g[a], g[r]) for r in rest]]
                    else:
                        (a, b), (c, d) = neg, pos
                        ac, ad = cut(g[a], g[c]), cut(g[a], g[d])
                        bc, bd = cut(g[b], g[c]), cut(g[b], g[d])
                        tris = [[ac, ad, bd], [ac, bd, bc]]
                    for tri in tris:
                        p0, p1, p2 = (verts[t] for t in tri)
                        u = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
                        w = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
                        nrm = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2],
                               u[0] * w[1] - u[1] * w[0])
                        faces.append(tri if sum(a * b for a, b in zip(nrm, out)) >= 0.0
                                     else [tri[0], tri[2], tri[1]])
    return verts, [f for f in faces if len(set(f)) == 3]


def _gyroid_networks(lo, h, n, k, half, freeze=None, phase=0.0):
    """The TWO void networks either side of the gyroid sheet, as CLOSED, correctly oriented meshes.

    F = sin(kx)cos(ky) + sin(ky)cos(kz) + sin(kz)cos(kx) is the gyroid; F = 0 is the surface and
    F / |grad F| is the signed DISTANCE to it, to first order. So the sheet of thickness 2*half is
    {|F| <= half*|grad F|} and the void is everything else. Normalising by the gradient is not a
    flourish: at a constant iso level the sheet comes out 2*half / |grad F| thick, and |grad F|
    varies ~1.7x over the gyroid, so a "1.6 mm" sheet would land anywhere between 1.2 and 2.0.

    `freeze` is the axis index whose sin/cos tables are held at one phase. The field is then constant
    along that axis and the networks come out PRISMATIC - through-holes rather than closed pockets.
    That is the difference between a part that ships and one that cannot: a true 3D sheet inside a
    closed rind leaves interior cavities, which is 3 mesh components, and the bridge refuses anything
    but one. The frozen axis's gradient term is zeroed to match, so the in-plane thickness stays 2*half.

    The outermost grid layer is forced OUTSIDE, so both networks close inside the domain: two closed
    manifold shells, no SOLIDIFY, no rim, nothing for a boolean to trip over."""
    n0, n1, n2 = n
    tab = []
    for ax, cnt in enumerate((n0, n1, n2)):
        if freeze == ax:
            tab.append(([math.sin(k * phase)] * (cnt + 1), [math.cos(k * phase)] * (cnt + 1)))
        else:
            tab.append(([math.sin(k * (lo[ax] + i * h)) for i in range(cnt + 1)],
                        [math.cos(k * (lo[ax] + i * h)) for i in range(cnt + 1)]))
    (sx, cx), (sy, cy), (sz, cz) = tab
    mask = [0.0 if freeze == a else 1.0 for a in range(3)]
    BIG = 1e3
    A = [[[BIG] * (n2 + 1) for _ in range(n1 + 1)] for _ in range(n0 + 1)]
    B = [[[BIG] * (n2 + 1) for _ in range(n1 + 1)] for _ in range(n0 + 1)]
    for i in range(1, n0):
        for j in range(1, n1):
            for m in range(1, n2):
                f = sx[i] * cy[j] + sy[j] * cz[m] + sz[m] * cx[i]
                gx = k * (cx[i] * cy[j] - sz[m] * sx[i]) * mask[0]
                gy = k * (cz[m] * cy[j] - sx[i] * sy[j]) * mask[1]
                gz = k * (cx[i] * cz[m] - sy[j] * sz[m]) * mask[2]
                g = math.sqrt(gx * gx + gy * gy + gz * gz) or 1e-9
                A[i][j][m] = half * g - f          # inside network A where F >  half*|grad F|
                B[i][j][m] = half * g + f          # inside network B where F < -half*|grad F|
    va, fa = _iso_tets(A, lo, h, n)
    vb, fb = _iso_tets(B, lo, h, n)
    off = len(va)
    return va + vb, fa + [[x + off for x in f] for f in fb]


def _clean_slivers(obj, dist=1e-3):
    """Dissolve degenerate edges and faces left by a lattice boolean. A clip that grazes a void
    tangentially leaves triangles microns across: Blender calls the mesh manifold and OCCT then sews
    it into a shell BRepCheck_Analyzer refuses. Dissolving them is not a tolerance - the geometry
    they carry is below the export tolerance (0.02 mm) anyway."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    # RE-triangulate through a coplanar merge: the marching grid leaves a lattice wall as a column of
    # 8 sliver triangles where 2 will do, and OCCT sews slivers into a solid that is BRepCheck-valid
    # and geometrically wrong (measured 3521 mm3 sewn from a mesh of 2320). Merging the coplanar runs
    # and letting BEAUTY re-fill them gives the same surface out of well-shaped triangles.
    bmesh.ops.dissolve_limit(bm, angle_limit=0.0087, verts=bm.verts, edges=bm.edges)   # 0.5 deg
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(me)          # deliberately NO recalc_face_normals: on a part this full of holes
    bm.free()               # Blender's recalc inverted the whole shell, and the sewn solid then
    me.update()             # came back valid but empty - "after the re-boolean the part is 0 solids"


def _kill_tiny_faces(obj, min_area=1.2e-3, passes=4):
    """Collapse away triangles under `min_area` mm2. The bridge's tris_to_solid SKIPS any triangle
    under 1e-4 mm2, and a skipped triangle is a HOLE: the sewn shell then comes back open
    (Closed() False) and BRepCheck refuses the solid, while sewing at 5e-3 - 500x the real gap -
    hides it. A lattice boolean always leaves a few such caps, so they are collapsed here, at the
    source, with a snapshot to revert to if a collapse ever breaks manifoldness."""
    me = obj.data
    for _ in range(passes):
        saved = ([tuple(v.co) for v in me.vertices], [tuple(f.vertices) for f in me.polygons])
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
        tiny = [f for f in bm.faces if f.calc_area() < min_area]
        if not tiny:
            bm.free()
            return 0
        edges = list({min(f.edges, key=lambda e: e.calc_length()) for f in tiny})
        bmesh.ops.collapse(bm, edges=edges, uvs=False)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
        bm.to_mesh(me)
        bm.free()
        me.update()
        if manifold_counts(obj) != (0, 0):
            me.clear_geometry()
            me.from_pydata(saved[0], [], [list(f) for f in saved[1]])
            me.update()
            return len(tiny)
    return len(tiny)


def _dup(obj, name):
    me = obj.data.copy()
    out = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(out)
    out.matrix_world = obj.matrix_world.copy()
    return out


def _stretch(obj, ai, mid, f):
    """Scale the mesh along one axis about `mid`, in place. Vertex arithmetic, not an object scale:
    a modifier stack reading obj.matrix_world and a report() reading obj.data disagree otherwise."""
    for v in obj.data.vertices:
        v.co[ai] = mid + (v.co[ai] - mid) * f
    obj.data.update()


def _weld(obj, merge=1e-4):
    """repair() WITHOUT recalc_face_normals, for the one mesh in the set whose normals must be left
    alone: a SOLIDIFY at offset -1 on a closed surface returns the rind as two NESTED shells - outer
    outward, inner inward - which is a perfectly valid hollow solid that every solver reads
    correctly. recalc_face_normals turns the inner shell outward and the mesh then encloses
    box + core instead of box - core: measured 7483 mm3 where the rind is 5316."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(me)
    bm.free()
    me.update()


def gyroid(part, guard, region, p):
    """GYROID: the wall is replaced by a TPMS lattice, so the solid reads as a frozen fluid.

        core = part eroded by `rind`,   void = core AND NOT sheet,   result = part - void

    i.e. `rind + (sheet AND core)` written as one cut, which never re-derives the part's own outer
    surface - every mating face survives for the bridge's re-boolean. Each number is a construction:
      * the rind is a SOLIDIFY at offset -1, so every point of `core` is >= `rind` inside the
        surface BY DEFINITION and no void can ever come nearer than that;
      * the sheet is the band {|F| <= half*|grad F|} round the gyroid surface, extracted directly as
        its two bounding networks - the gradient normalisation is what holds its thickness at
        `sheet` mm (see _gyroid_networks);
      * `region` clips the void and the guard is cut out of it, so the mating zone keeps solid CAD
        wall whatever the lattice does.

    Two modes, and the default is the one that ships:
      prism  the field is frozen along `axis`, so the lattice runs THROUGH the part as the gyroid
             cross-section - the pattern a sliced gyroid infill shows on its top layer. The voids
             are through-holes, so the result is ONE component.
      sheet  the true 3D TPMS. Inside a closed rind its voids are interior cavities, which is 3+
             mesh components, and the bridge admits exactly one - so it is only usable on a part
             thick enough for skin="open" to break them out to the surface.
    And two skins: "open" erodes IN PLAN only, so the two faces normal to `axis` open into the
    lattice and the apertures EMERGE rather than being cut; "closed" keeps a full rind everywhere."""
    period = float(p.get("period", 10.0))
    sheet = float(p.get("sheet", 1.6))
    rind = float(p.get("rind", 1.6))
    voxel = float(p.get("voxel", 1.2))
    bias = float(p.get("sheet_bias", 0.12))   # faceting at `voxel` thins the even offset a little
    axis = p.get("axis", "Z").upper()
    mode = str(p.get("mode", "prism")).lower()   # "prism" (through-lattice) | "sheet" (3D TPMS)
    skin = str(p.get("skin", "open")).lower()    # "open" (lattice breaks the flat faces) | "closed"
    pad = 2.0
    co = [(v.co.x, v.co.y, v.co.z) for v in part.data.vertices]
    lo = [min(c[i] for c in co) - pad for i in range(3)]
    hi = [max(c[i] for c in co) + pad for i in range(3)]
    # AUTO-FIT TO THE TRIANGLE BUDGET, and this is not a nicety. The bridge decimates anything over
    # its budget, and a COLLAPSE decimation of a lattice is destructive in a way it is not on a solid:
    # measured, 265 000 tris collapsed to 20 000 came back as 4 components with a volume ratio of
    # 1.2939 on a DIFFERENCE - i.e. material appeared. So the recipe sizes its own grid instead.
    # The starting estimate is measured, not guessed - the F = 0 surface runs 30 * V_box /
    # (period * voxel**2) tris (32 296 at V 15 488, period 10, voxel 1.2, to three digits) and the
    # void is TWO such surfaces - and then the extraction is simply RUN and re-run: it is pure python
    # over a few 10 000 cubes and costs ~0.3 s, which is cheaper than trusting a model. `quality` is
    # the sampling floor: under ~9 samples per period the extracted sheet stops being the surface it
    # claims to be, so the budget is met by coarsening the voxel to that floor and then by GROWING
    # the period (fewer, larger cells) up to `period_max`.
    budget_tris = max(2000, int(p.get("tri_budget", 12000)))
    target = max(1500, int(float(p.get("iso_fraction", 0.75)) * budget_tris))
    quality = float(p.get("quality", 9.0))
    period_max = float(p.get("period_max", 3.0)) * period
    ai = "XYZ".index(axis)
    freeze = ai if mode == "prism" else None
    vol_box = (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])
    # prism mode is far cheaper per triangle than the 3D sheet (one contour, a handful of layers),
    # so it starts at the voxel it was asked for and lets the loop below coarsen only if it must;
    # sheet mode starts from the measured tri model, which saves several 30 000-triangle extractions.
    h = voxel if mode == "prism" else max(voxel, math.sqrt(60.0 * vol_box / max(1e-6, period * target)))
    verts = faces = None
    fitted = ""
    for _attempt in range(14):
        if h > period / quality:
            want = max(period * 1.15, quality * h)     # jump straight to the period `h` needs
            if want > period_max:
                fitted = "too large for a printable gyroid at this triangle budget"
                break
            period = want
        k = 2.0 * math.pi / period
        # the frozen axis needs its first live grid layer OUTSIDE the part, or the network's end cap
        # (which lands on that layer) would slice through it - so that axis is padded by h + 0.5
        pads = [(h + 0.5) if a == freeze else pad for a in range(3)]
        glo = [lo[i] + pad - pads[i] for i in range(3)]
        ghi = [hi[i] - pad + pads[i] for i in range(3)]
        n = [max(3, int(math.ceil((ghi[i] - glo[i]) / h))) for i in range(3)]
        if n[0] * n[1] * n[2] > 400_000:       # pure python: keep the grid inside the blender timeout
            h *= (n[0] * n[1] * n[2] / 400_000.0) ** (1 / 3.0)
            continue
        # the half-thickness is grown with the voxel: linear interpolation across a facet undershoots
        # the normalised distance, measured 1.5528 mm of a nominal 1.72 at voxel 2.489 (a deficit of
        # 0.067 x voxel), so the cut half-thickness carries 0.10 x voxel of compensation.
        half = 0.5 * (sheet + bias + 0.20 * h)
        verts, faces = _gyroid_networks(glo, h, n, k, half, freeze=freeze,
                                        phase=float(p.get("phase", 0.0)))
        if len(faces) <= target:
            break
        h *= max(1.1, (len(faces) / float(target)) ** 0.5)
    cells = round((hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2]) / period ** 3, 2)
    if faces and len(faces) > budget_tris:
        fitted = f"{len(faces)} void tris will not fit the {budget_tris} budget"
    if fitted or not faces:
        log("recipe", {"gyroid": {"skipped": fitted or "the field never crosses zero in this box",
                                  "period": round(period, 2), "period_max": round(period_max, 2),
                                  "voxel": round(h, 3), "box_mm3": round(vol_box, 1),
                                  "tri_budget": budget_tris, "cells": cells}})
        return part, False
    info = {"period": round(period, 3), "period_asked": float(p.get("period", 10.0)), "sheet": sheet,
            "sheet_cut": round(2.0 * half, 3), "rind": rind, "voxel": round(h, 3), "grid": n,
            "cells": cells, "iso_tris": len(faces), "axis": axis, "mode": mode,
            "tri_budget": budget_tris}
    if len(faces) < 8:
        log("recipe", {"gyroid": dict(info, skipped="the field never crosses zero in this box")})
        return part, False
    iso = new_mesh_obj("gyroid_void", verts, faces)
    _weld(iso)                                 # NOT repair(): the marching tets already oriented it
    _clean_slivers(iso, 5e-4)                  # a clean cutter is half of a clean result
    info["void_raw_mm3"] = report(iso, "gy_void_raw")["volume_mm3"]
    shell = _dup(part, "rind")                 # the inner `rind` layer, as nested shells
    ms = shell.modifiers.new("erode", "SOLIDIFY")
    ms.thickness, ms.offset, ms.use_even_offset = rind, -1.0, True
    ms.use_rim, ms.use_quality_normals = True, True
    apply_all(shell)
    _weld(shell)                               # NOT repair(): see _weld's docstring
    info["rind_mm3"] = report(shell, "gy_rind")["volume_mm3"]
    core = _dup(part, "core")
    if not boolean_checked(core, shell, "DIFFERENCE"):
        bpy.data.objects.remove(shell, do_unlink=True)
        bpy.data.objects.remove(core, do_unlink=True)
        bpy.data.objects.remove(iso, do_unlink=True)
        log("recipe", {"gyroid": dict(info, skipped="no solver eroded the part by the rind")})
        return part, False
    repair(core)
    bpy.data.objects.remove(shell, do_unlink=True)
    if skin == "open":
        # THE APERTURES. A uniform erosion also puts a `rind` skin on the two faces normal to `axis`,
        # which on a 4 mm plate leaves 0.8 mm of core - no lattice lives in that, and the family's
        # promise is that its openings EMERGE where the sheet breaks the outer surface instead of
        # being cut. So the erosion is made IN PLANE only: the eroded core is stretched along the axis
        # until it stands proud of the part, then clipped back to the part's own silhouette (stretched
        # the same way). The inset of `rind` in plan is untouched, so the silhouette wall and the
        # guard keep their full CAD thickness, while the two flat faces open into the lattice.
        # Stretching rather than unioning displaced copies is not a shortcut: at rind 1.6 on a 4 mm
        # plate the copies are 1.6 apart and the core is 0.8 thick, so a union leaves 3 components
        # with gaps (measured 3250 mm3 of a wanted 5416).
        ai = "XYZ".index(axis)
        mid = 0.5 * (lo[ai] + pad + hi[ai] - pad)
        span_p = (hi[ai] - pad) - (lo[ai] + pad)
        cz = [v.co[ai] for v in core.data.vertices]
        span_c = max(1e-3, max(cz) - min(cz))
        over = span_p + 2.0 * max(1.0, rind)          # proud of the part, so no coplanar faces
        _stretch(core, ai, mid, over / span_c)
        clip = _dup(part, "core_clip")
        _stretch(clip, ai, mid, over / span_p)
        boolean(core, clip, "INTERSECT")
        bpy.data.objects.remove(clip, do_unlink=True)
        repair(core)
    info["core_mm3"] = report(core, "gy_core")["volume_mm3"]
    info["skin"] = skin
    cspan = [0.0, 0.0, 0.0]
    if core.data.vertices:
        cspan = [round(max(v.co[i] for v in core.data.vertices)
                       - min(v.co[i] for v in core.data.vertices), 2) for i in range(3)]
    info["core_span"] = cspan
    if info["core_mm3"] <= 0.0 or min(cspan) < sheet + 2.0 * h:
        # Nothing a lattice can live in. A closed rind costs 2 x `rind` of the part's thickness, so a
        # 4 mm plate at rind 1.6 leaves 0.8 mm of core and the sheet has nowhere to go: the honest
        # answer is the undecorated part (the bridge's volume band allows a ratio of exactly 1.0),
        # not a void full of slivers. skin="open" is the mode for a thin plate.
        for o in (iso, core):
            bpy.data.objects.remove(o, do_unlink=True)
        log("recipe", {"gyroid": dict(info, skipped="core too thin for the sheet")})
        return part, False
    void = iso                                  # the void networks, clipped to the core
    solver = boolean_checked(void, core, "INTERSECT")
    repair(void)
    if not solver:
        bpy.data.objects.remove(core, do_unlink=True)
        bpy.data.objects.remove(void, do_unlink=True)
        log("recipe", {"gyroid": dict(info, skipped="no solver clipped the void to the core")})
        return part, False
    # clip_to_region() runs one MANIFOLD boolean; a lattice cutter meeting a region wall tangentially
    # needs the solver ladder instead - measured, a plate with a decor_region came back with a
    # non-manifold void and the whole decoration was dropped.
    # The guard is PADDED before it is cut out of the void, on carapace_lattice's own evidence: a
    # cutter face landing exactly ON the guard's surface leaves the bridge's re-boolean (mesh solid
    # UNION the CAD guard) with coincident faces, and the result then sews into a solid whose export
    # mesher refuses it - measured "3mf mesh is invalid" on a plate whose lattice was otherwise clean.
    fat = None
    if guard is not None:
        pad_g = float(p.get("guard_pad", 0.6))
        fat = _dup(guard, "guard_pad")
        mg = fat.modifiers.new("dilate", "SOLIDIFY")
        mg.thickness, mg.offset, mg.use_even_offset = pad_g, 1.0, True
        mg.use_rim, mg.use_quality_normals = True, True
        apply_all(fat)
        _weld(fat)                              # solidify's nested shells: normals are already right
        boolean(fat, guard, "UNION")
        repair(fat)
        info["guard_pad"] = pad_g
    for other, op, why in ((region, "INTERSECT", "region"), (fat, "DIFFERENCE", "guard")):
        if other is None:
            continue
        if not boolean_checked(void, other, op):
            for o in (core, void, fat):
                if o is not None:
                    bpy.data.objects.remove(o, do_unlink=True)
            log("recipe", {"gyroid": dict(info, skipped=f"no solver clipped the void to the {why}")})
            return part, False
        repair(void)
    for o in (core, fat):
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
    if manifold_counts(void) != (0, 0):
        # repair()'s merge-by-distance can weld two lattice vertices left a micron apart by the clip
        # and make the edge between them non-manifold. Dissolving the degenerate geometry it just
        # created is the fix; the solver ladder above has already agreed the boolean itself is clean.
        _clean_slivers(void, 5e-4)
        info["void_cleaned"] = list(manifold_counts(void))
    info["void_mm3"] = report(void, "gy_void")["volume_mm3"]
    info["void_nm"] = list(manifold_counts(void))
    if not void.data.polygons or info["void_mm3"] <= 0.0:
        bpy.data.objects.remove(void, do_unlink=True)
        log("recipe", {"gyroid": dict(info, skipped="no void survived the region/guard clips")})
        return part, False
    # A cutter with a stray non-manifold edge is not refused here: boolean_checked snapshots the part
    # before every attempt and only reports a solver when the RESULT is manifold and closed, so the
    # thing that actually ships is judged instead of a proxy for it. One such edge in a 6 000-triangle
    # lattice cutter was costing the whole decoration.
    solver = boolean_checked(part, void, "DIFFERENCE")
    bpy.data.objects.remove(void, do_unlink=True)
    if not solver:
        log("recipe", {"gyroid": dict(info, skipped="no solver cut the void out of the part")})
        return part, False
    _clean_slivers(part, float(p.get("sliver", 2e-3)))
    info["tiny_faces"] = _kill_tiny_faces(part, float(p.get("min_face_area", 1.2e-3)))
    info["solver"] = solver
    info["tris"] = sum(len(f.vertices) - 2 for f in part.data.polygons)
    log("recipe", {"gyroid": info})
    # NEVER the n-gon path: a limited dissolve over a face full of lattice holes merges the fan round
    # a hole into a slit polygon whose wire touches itself, and OCCT refuses the face (measured: 416
    # n-gon faces, sewn in 0.5 s, BRepCheck-invalid). The triangles go back instead.
    return part, False


RECIPES = {"elytra_dome": elytra_dome, "carapace_lattice": carapace_lattice, "chitin": chitin,
           "sculpt": sculpt, "emboss": emboss, "hardshell": hardshell, "gyroid": gyroid}


def main():
    p = args()
    setup_scene()
    part, guard, region, cuts, allow = load(p)
    before = report(part, "input")
    assert before["is_manifold"], "input mesh is not manifold"
    fn = RECIPES[p["recipe"]]
    part, ngon_safe = fn(part, guard, region, p)
    repair(part, triangulate=False)
    tris = budget(part, int(p.get("tri_budget", 12000)))
    after = report(part, "decorated")
    wall = wall_thickness_report(part, float(p.get("wall_floor", 1.2)), guard_obj=guard,
                                 guard_margin=float(p.get("guard_margin", 0.6)),
                                 opposing_cos=float(p.get("wall_opposing_cos", 0.7)),
                                 min_face_area=float(p.get("wall_min_face_area", 0.10)),
                                 allow_objs=(allow,) if allow is not None else ())
    ratio = (after["volume_mm3"] / before["volume_mm3"]) if before["volume_mm3"] else 0.0
    log("stats", {"tris": tris, "volume_ratio": round(ratio, 5), "ngon_safe": ngon_safe,
                  "wall_ok": wall["ok"], "min_thickness": wall["min_thickness"]})
    # The extension is chosen HERE, not by the caller: a recipe that creates curvature refuses the
    # n-gon path (dissolve_limit flattens genuine curvature and drifted a domed part by 0.5 %), and
    # writing an STL into a path called .obj makes the bridge parse it with the wrong reader.
    base = p["out_base"]
    if p.get("ngon", True) and ngon_safe:
        dissolve_ngons(part, float(p.get("ngon_angle", 0.3)))
        out = base + ".obj"
        export_obj(part, out)
        log("out", {"format": "obj", "path": out})
    else:
        out = base + ".stl"
        export_stl(part, out)
        log("out", {"format": "stl", "path": out})
    log("done")


if __name__ == "__main__":
    main()
