"""Runs INSIDE Blender 5.2.2 (not importable by the package). Scene setup, mesh reporting, the
protected-region mask, the wall-thickness estimator and the repair sequence.

Every number and every trap in here is measured on this machine; see the comments. Blender 5.2
specifics: bpy.ops.wm.stl_import / wm.stl_export (the old bpy.ops.export_mesh.stl is gone),
SHRINKWRAP uses use_project_x/y/z booleans (there is no project_axis enum), and the boolean
solvers are FLOAT / EXACT / MANIFOLD.
"""

import json
import math
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SOLVER = "MANIFOLD"   # 11-14x faster than EXACT with byte-identical geometry (measured)
MERGE_DIST = 1e-5     # mandatory before every boolean: duplicate faces break FLOAT and MANIFOLD


def log(tag, payload=None):
    """Only `[BL] ...` lines are parsed by the bridge; everything else is noise it ignores."""
    if payload is None:
        print(f"[BL] {tag}", flush=True)
    else:
        print(f"[BL] {tag} {json.dumps(payload)}", flush=True)


def args():
    """The params dict, from the json path after the `--` separator."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    with open(argv[0]) as fh:
        return json.load(fh)


def setup_scene():
    """1 BU = 1 mm for DISPLAY; what matters is use_scene_unit=False on import and export, which
    keeps every coordinate in raw millimetres so bevel widths and displace strengths are in mm."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = "MILLIMETERS"
    return sc


def import_stl(path, name):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=1.0, use_scene_unit=False,
                          forward_axis="Y", up_axis="Z")
    obj = [o for o in bpy.data.objects if o not in before][0]
    obj.name = name
    return obj


def export_stl(obj, path):
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0,
                          use_scene_unit=False, apply_modifiers=True, ascii_format=False,
                          forward_axis="Y", up_axis="Z")


def export_obj(obj, path):
    """OBJ keeps n-gons, which is what makes the fast OCCT rebuild path possible (3-7x)."""
    for o in bpy.data.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, global_scale=1.0,
                          apply_modifiers=True, export_materials=False, export_triangulated_mesh=False,
                          forward_axis="Y", up_axis="Z")


def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except RuntimeError as exc:
            log("warn", {"modifier_apply": m.name, "error": str(exc)})


def bvh_of(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def report(obj, tag=""):
    """Authoritative in-Blender manifold report. `components` is NOT redundant with is_manifold:
    four separate closed blobs are manifold, closed, and four loose lumps on the bed (measured -
    OCCT sewed them into one IsValid()==False solid)."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    nonman = [e for e in bm.edges if not e.is_manifold]
    boundary = [e for e in bm.edges if e.is_boundary]
    wire = [e for e in bm.edges if e.is_wire]
    loose_v = [v for v in bm.verts if not v.link_edges]
    vol = bm.calc_volume(signed=True)   # SIGN MATTERS: a negative volume means an inside-out mesh
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    polys = len(bm.faces)
    bm.free()
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    seen, comps = set(), 0
    for v in bm2.verts:
        if v.index in seen:
            continue
        comps += 1
        stack = [v]
        seen.add(v.index)
        while stack:
            cur = stack.pop()
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
    bm2.free()
    manifold = not nonman and not boundary and not wire and not loose_v
    out = dict(tag=tag, tris=tris, polys=polys, components=comps, non_manifold_edges=len(nonman),
               boundary_edges=len(boundary), volume_mm3=round(vol, 4), is_manifold=manifold,
               ok_for_print=bool(manifold and comps == 1 and vol > 0))
    log("report", out)
    return out


LATERAL_RAYS = 16      # directions sampled in the plane normal to `axis`; 16 is 2 % worst-case error
SURFACE_EPS = 1e-4     # "on the guard's surface"; also the ray-origin offset (see the ramp below)
RIM_PROBE = 0.05       # how far inside the wall the rim probe starts, mm (see make_protect_group)


def _lateral_dirs(axis, count=LATERAL_RAYS):
    """`count` unit vectors evenly spaced in the plane NORMAL to `axis`."""
    a, b = {"X": ("Y", "Z"), "Y": ("Z", "X"), "Z": ("X", "Y")}[axis.upper()]
    idx = {"X": 0, "Y": 1, "Z": 2}
    out = []
    for k in range(count):
        t = 2.0 * math.pi * k / count
        v = Vector((0.0, 0.0, 0.0))
        v[idx[a]], v[idx[b]] = math.cos(t), math.sin(t)
        out.append(v)
    return out


def _vertex_normals(obj):
    """Outward per-vertex normals in world space, by index."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.normal_update()
    out = {v.index: v.normal.copy() for v in bm.verts}
    bm.free()
    return out


def make_protect_group(obj, guard_obj, inner=0.0, feather=3.0, name="protect", axis=None):
    """Weight 0 INSIDE the guard solid or within `inner` mm of it, ramping to 1 at inner+feather.
    Every modifier is then gated on this group - never on "I only sculpted over there".

    The inside test is not optional. BVHTree.find_nearest returns the distance to the guard's
    SURFACE, which for a point deep inside the guard is LARGE - so a distance-only rule frees exactly
    the vertices it is supposed to freeze. It happens to behave on a small guard (a bore collar,
    where everything inside is within inner+feather of the surface anyway) and inverts completely on
    a large one: a mask written as "everything except the skin I want swelled" froze the skin and
    freed the rest, and the dome displaced nothing at all. The sign of (v - nearest).normal settles
    it for any closed solid.

    `axis` - the displace axis - switches the RAMP (not the inside test) from the 3D distance to a
    LATERAL one, measured only in the plane normal to that axis. Pass it whenever the guard backs the
    surface being displaced, which is how every outward-skin mask in this project is written.

    Why, measured: a mask written as "the part minus a thin slab over the face I want domed" leaves
    the guard sitting `slab` mm BEHIND every vertex of that face, so the 3D nearest-surface distance
    is `slab` for the whole face and the ramp caps every weight at min(1, slab/feather). The ramp
    that was supposed to be a lateral run-out - 0 at the region's border, 1 in its middle - becomes
    a constant, and it is a SMALL constant. On side_panel_system's 0.62 mm slab that is 0.21 at
    feather 3.0, and the dome delivered 9.7 % of its requested rise (0.087 mm of a 0.9 mm ask);
    at feather 4.5 the cap is 0.14 and it delivered 6.1 % - the shortfall tracks 1/feather exactly,
    which is the signature of a fixed numerator. callsign_plate had the same bug written down
    without being traced: CA_SKIN 1.6 over feather 3.0 caps at 0.53, it asks CA_RISE 1.9 and its own
    comment recorded the result as "a 0.77 mm dome" - 0.405 of the ask.
    Worse than small, the constant field has NO run-out: every vertex of the face rises by the same
    amount and the swell meets the frozen border as a STEP. Deepening the region to raise the cap
    just makes the step bigger - measured, it then failed the mesh wall floor at every depth from
    1.0 mm up, on a 2.1 mm wall AND on a 2.9 mm one, at rises from 0.001 mm to 1.8 mm.
    The lateral ramp fixes both at once: distance to the guard measured in the plane normal to the
    displace axis is the distance to the REGION'S BORDER, which is what `feather` always meant.

    Dropping the through-thickness term does not risk the wall: `upward_group` already restricts
    every displaced vertex to faces whose normal is within `min_nz` of the axis, so the far side of
    the wall cannot move, and the vertices on it are inside the guard anyway.

    The lateral measure is taken to the guard AND to the part's OWN RIMS, and the second half is not
    optional. A guard cannot describe a hole in the middle of the surface being displaced, so skin
    beside one used to get a full-strength displacement with nowhere to go and PLEATED: measured at
    a finger window's edge, adjacent facets 0.02 mm apart with opposing normals and a wall reading
    of 0.0241 mm on a 2.105 mm wall - the same "pinched a 0.02-0.03 mm fold at the USB corner" that
    `side_panels.py` recorded. Three ways of masking the rim instead were measured and every one of
    them left a solid OCCT would not sew, at every rise down to 0.3: a collar out of the region, the
    same collar into the guard, and moving the region's border past the hole. A second mask boundary
    in the middle of a flank is the wrong shape of fix; feathering towards the rim itself is the
    right one, and it needs no mask at all."""
    tree = bvh_of(guard_obj)
    vg = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
    mw = obj.matrix_world
    dirs = _lateral_dirs(axis) if axis else None
    own, vnorm = (bvh_of(obj), _vertex_normals(obj)) if dirs else (None, None)
    frozen = 0
    for v in obj.data.vertices:
        co = mw @ v.co
        loc, nrm, _i, dist = tree.find_nearest(co)
        if loc is None:
            w = 1.0
        elif (nrm is not None and (co - loc).dot(nrm) < 0.0) or dist <= max(inner, SURFACE_EPS):
            w = 0.0                                  # inside the guard, or hugging its surface
        elif dirs is None:
            w = min(1.0, (dist - inner) / feather)
        else:
            # The rays are capped at inner+feather: past that the weight is 1 whatever the distance,
            # so there is nothing to gain by tracing further and the cast is bounded work per vertex.
            reach = inner + feather
            clear = reach
            # The rim probe starts just INSIDE the material, along the vertex's own inward normal,
            # so a lateral ray runs parallel to the surface through the wall and its first hit is
            # the nearest RIM - the far side of a through-hole, or the part's outline. Starting on
            # the surface instead puts the ray exactly in the plane of the faces it is supposed to
            # travel along, where it hits coplanar facets or nothing at all, on numerics alone.
            inward = co - vnorm[v.index] * RIM_PROBE
            for u in dirs:
                # Offset the origin: a vertex of the free surface can lie EXACTLY on a guard face
                # (they share the region's border), and a ray cast from exactly on a face hits or
                # misses on numerics alone - which gives neighbouring border vertices weights of 0
                # and 1 at random and leaves a jagged fringe that displaces into slivers. Measured:
                # without this the dome was refused above rise 0.6 with wall readings of 0.02 mm.
                hit = tree.ray_cast(co + u * SURFACE_EPS, u, reach)
                if hit[0] is not None and hit[3] + SURFACE_EPS < clear:
                    clear = hit[3] + SURFACE_EPS
                rim = own.ray_cast(inward + u * SURFACE_EPS, u, reach)
                if rim[0] is not None and rim[3] + SURFACE_EPS < clear:
                    clear = rim[3] + SURFACE_EPS
                if clear <= inner:
                    break
            w = min(1.0, max(0.0, (clear - inner) / feather))
        frozen += 1 if w <= 1e-6 else 0
        vg.add([v.index], w, "REPLACE")
    log("protect", {"verts": len(obj.data.vertices), "frozen": frozen,
                    "free": len(obj.data.vertices) - frozen,
                    "ramp": f"lateral({axis})" if dirs else "3d"})
    return vg


def promote_faces_outside(obj, guard_obj, name="protect"):
    """Give weight 1 to every vertex of every face whose CENTRE lies outside the guard.

    For the one case the vertex rule cannot express: a coarse mesh whose big flat faces have all
    their CORNERS on the region's border. Every corner is then inside the guard or hugging it, the
    whole mask comes back frozen, and `subdivide_masked` has nothing to cut - after which the old
    fallback subdivided the part UNMASKED, cut up the mating triangles too and handed OCCT a shell
    it refused to sew ("BRepCheck_Analyzer says invalid", measured on a skin whose only interior
    vertices had just been taken out of the mesh). A face's centre is the honest test of which side
    of the border the face is on, and it keeps the mating triangles whole because theirs lie inside
    the guard. Subdivision moves nothing; the re-mask that follows sets the real weights."""
    tree = bvh_of(guard_obj)
    vg = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    promoted = 0
    for f in bm.faces:
        c = f.calc_center_median()
        loc, nrm, _i, d = tree.find_nearest(c)
        # `d > SURFACE_EPS` matters as much as the sign: a face lying exactly ON the guard's surface
        # - every outer face of the skirt, and every mating face - reads as "outside" by the dot
        # test alone, and promoting those put the mating triangles back into the subdivision (254 of
        # 404 faces promoted, and the sewn solid was still refused). Only a face genuinely clear of
        # the guard is a decoration face.
        if loc is None or (d > SURFACE_EPS and (nrm is None or (c - loc).dot(nrm) >= 0.0)):
            for v in f.verts:
                vg.add([v.index], 1.0, "REPLACE")
            promoted += 1
    bm.free()
    log("promote", {"faces_outside_guard": promoted, "faces": len(obj.data.polygons)})
    return promoted


def subdivide_masked(obj, levels=2, group=None, strict=False):
    """SUBSURF cannot be masked by a vertex group, so subdivide with bmesh and keep the mating
    geometry's own faces out - that preserves its EXACT triangles.

    A face is kept out when it lies ENTIRELY in the protected region (`any` weight > 0 to subdivide),
    not merely when it touches it. `strict=True` restores the `all`-must-be-free rule, and it is a
    trap on a coarse STL: a plate's top face is triangulated in long thin triangles that each reach
    a bolt-hole rim, so every one of them touches the guard, nothing in the middle of the face gets
    subdivided, and the only movable vertices left are on the outline - where a centred dome profile
    is already zero. Measured symptom: a 9 mm dome that displaces exactly 0.000 mm.

    Subdivision does not MOVE anything; the weights are what stop movement, and the guard region is
    re-unioned from CAD afterwards - so subdividing a face that merely touches the guard is safe."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    layer = bm.verts.layers.deform.verify()
    vg_idx = obj.vertex_groups[group].index if group else None
    pick = all if strict else any
    for _ in range(levels):
        faces = ([f for f in bm.faces if pick(v[layer].get(vg_idx, 0.0) > 1e-6 for v in f.verts)]
                 if vg_idx is not None else list(bm.faces))
        edges = {e for f in faces for e in f.edges}
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()


def upward_group(obj, name="upward", min_nz=0.5, base="protect", axis="Z"):
    """The outward skin only, intersected with the protect weights. Displacing only this skin means
    the wall can only get THICKER - the whole safety argument for `chitin` and for the dome's
    mode="top". Never deform two opposite surfaces of a thin shell independently: CAST on a closed
    thin shell pinched a measured 4 mm wall to 0.0018 mm.

    `axis` is the part's THICKNESS direction: "Z" for a plate lying on the bed, "X" for a vertical
    side wall, "Y" for a transverse one. It must match the DISPLACE modifier's `direction`, and on a
    wall it must NOT be left at "Z" - the point of locking the axis is that the surface normal at a
    rim is nearly perpendicular to the thickness, so displacing along the normal pushes material
    sideways into a 0.005 mm flange."""
    comp = {"X": lambda n: n.x, "Y": lambda n: n.y, "Z": lambda n: n.z}[axis.upper()]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    up = {v.index for f in bm.faces if comp(f.normal) >= min_nz for v in f.verts}
    bm.free()
    prot = obj.vertex_groups.get(base)
    vg = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
    for v in obj.data.vertices:
        try:
            w = prot.weight(v.index) if prot else 1.0
        except RuntimeError:
            w = 0.0
        vg.add([v.index], w if v.index in up else 0.0, "REPLACE")
    return vg


def scaled_texture_coords(obj, modifier, period_mm, name="texcoord"):
    """The spatial frequency of a displace texture comes from its COORDINATES, not noise_scale:
    scale 3.0 and 8.0 gave byte-identical output, because a WOOD/BANDS texture ignores noise_scale
    entirely."""
    empty = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(empty)
    empty.scale = (period_mm, period_mm, period_mm)
    modifier.texture_coords = "OBJECT"
    modifier.texture_coords_object = empty
    bpy.context.view_layer.update()   # or the empty's matrix_world is still the identity on apply
    return empty


def repair(obj, merge=MERGE_DIST, voxel=0.0, triangulate=True):
    """Mandatory preprocessing before every boolean. Merge-by-distance fixes duplicate faces and
    zero-length edges (which otherwise break FLOAT and MANIFOLD); recalc_face_normals fixes an
    inverted cutter (which makes EXACT and MANIFOLD produce silently WRONG geometry - one measured
    case ADDED material and returned 2 components). An OPEN cutter is unsalvageable by merging and
    MANIFOLD silently returns the part UNCHANGED, so callers must also assert the volume moved.
    A voxel remesh guarantees closure but resamples every feature - NEVER on mating geometry."""
    if voxel > 0:
        m = obj.modifiers.new("vx", "REMESH")
        m.mode, m.voxel_size, m.adaptivity = "VOXEL", voxel, 0.0
        apply_all(obj)
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(me)
    bm.free()
    me.update()


def boolean(obj, other, operation="DIFFERENCE", solver=SOLVER):
    m = obj.modifiers.new("bool", "BOOLEAN")
    m.operation, m.object, m.solver = operation, other, solver
    apply_all(obj)


def manifold_counts(obj):
    """(non_manifold_edges, boundary_edges, components) - the cheap version of report()."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bd = sum(1 for e in bm.edges if e.is_boundary)
    bm.free()
    return nm, bd


def boolean_checked(obj, other, operation="DIFFERENCE", solvers=("MANIFOLD", "EXACT", "FLOAT")):
    """Boolean with a SOLVER RETRY, because the three solvers fail differently and none is reliable
    on every input. MANIFOLD is 11-14x faster than EXACT with byte-identical output on clean inputs,
    so it goes first - but wherever a cutter face lands exactly on another boolean's result surface it
    leaves non-manifold slivers (measured 1 to 14 non-manifold edges on a cell field, varying with the
    random seed). Rather than hunt for a seed that happens to work, try the next solver.

    The mesh is snapshotted before each attempt, so a failed attempt is genuinely undone. Returns the
    solver that produced a manifold result, or None when all of them failed."""
    saved = [tuple(v.co) for v in obj.data.vertices], [tuple(pp.vertices) for pp in obj.data.polygons]
    for solver in solvers:
        boolean(obj, other, operation, solver)
        nm, bd = manifold_counts(obj)
        if not nm and not bd:
            log("boolean", {"solver": solver, "operation": operation})
            return solver
        log("warn", {"boolean": solver, "non_manifold": nm, "boundary": bd, "retrying": True})
        me = obj.data
        me.clear_geometry()
        me.from_pydata(saved[0], [], saved[1])
        me.update()
    return None


def dissolve_ngons(obj, angle_deg=0.3):
    """Merge coplanar triangles into n-gons: 3-7x off the OCCT rebuild. MUST NOT run on smoothly
    curved surfaces - at 0.5 deg it flattened genuine curvature on a domed part and drifted the
    volume by 84.2 mm3 (0.5 %). Recipes that produce curvature pass ngon=False instead."""
    from math import radians
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.dissolve_limit(bm, angle_limit=radians(angle_deg), verts=bm.verts, edges=bm.edges)
    bm.to_mesh(me)
    bm.free()
    me.update()


def wall_thickness_report(obj, floor, samples=6000, guard_obj=None, guard_margin=0.0,
                          allow_objs=(), opposing_cos=0.7, min_face_area=0.10):
    """Wall thickness measured ON THE MESH, because OCCT's offset_3d returns an empty shape on a
    solid of ~900 planar triangle faces: _fit.erode() collapses to 0 mm3 and _fit.min_wall() falls
    back to rays and costs 36 s. Two traps, both hit and fixed:

      * the sign. The ray leaves a face inward and hits the far wall FROM THE INSIDE, so that
        wall's outward normal points ALONG the ray (dot ~ +1). Testing `<= -cos` rejects every
        legitimate ray and then reports "no thin wall found" on a mesh with ZERO rays - hence `ok`
        also requires rays > 0.
      * grazing. Without the opposing-normal filter, rays leaving a fillet facet hit the
        neighbouring facet of the same fillet and report 0.0018 mm on a part whose real minimum
        wall is 4 mm.

    A third trap, found on a SUBDIVIDED fillet: the defaults `opposing_cos=0.5, min_face_area=0.02`
    from the first measurement pass accept a ray between two nearly parallel slivers of the same
    fillet and report 0.41 mm on a part whose real wall is 4.0 mm (the unsubdivided same part reports
    4.0). A sliver of 0.02 mm2 is not a wall, and a "far wall" 60 deg off-axis is not opposite, so
    the defaults are 0.10 mm2 and cos 0.7 (within 45 deg). Both are accuracy, not leniency: a real
    thin wall presents a face of useful area whose opposite normal is genuinely opposed.

    `allow_objs` are declared thin features (emboss marks, lips): a narrow groove is indistinguishable
    from a thin wall to a ray sampler, so it must be excluded exactly like _fit.min_wall(allow=...).
    Float equality: a lattice inset produces walls of PRECISELY `w`, so the test is floor - 1e-3."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    guard = bvh_of(guard_obj) if guard_obj else None
    allows = [bvh_of(a) for a in allow_objs if a is not None]
    faces = sorted((f for f in bm.faces if f.calc_area() >= min_face_area), key=lambda f: -f.calc_area())
    step = max(1, len(faces) // samples)
    hits, grazing, thin, skipped = [], 0, 0, 0
    for f in faces[::step]:
        c, nn = f.calc_center_median(), f.normal.copy()
        if guard is not None:
            loc, _n, _i, d = guard.find_nearest(c)
            if loc is not None and d <= guard_margin:
                skipped += 1
                continue
        if any((lambda r: r[0] is not None and r[3] <= 0.35)(a.find_nearest(c)) for a in allows):
            skipped += 1
            continue
        direction = -nn
        hit, hn, _i, dist = tree.ray_cast(c + direction * 1e-4, direction, 500.0)
        if hit is None or dist is None or dist < 1e-9:
            continue
        if hn is not None and hn.dot(direction) < opposing_cos:
            grazing += 1
            continue
        hits.append((dist + 1e-4, tuple(round(x, 3) for x in c)))
        if dist < floor - 1e-3:
            thin += 1
    bm.free()
    hits.sort()
    out = dict(rays=len(hits), grazing_rejected=grazing, skipped=skipped,
               min_thickness=round(hits[0][0], 4) if hits else None,
               at=hits[0][1] if hits else None, thin_rays=thin,
               ok=bool(hits) and hits[0][0] >= floor - 1e-3)
    log("wall", out)
    return out
