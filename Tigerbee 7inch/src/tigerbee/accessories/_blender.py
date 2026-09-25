"""The Blender bridge: build123d solid in, decorated build123d solid out, or the input unchanged.

    from tigerbee.accessories import _blender as BL

    part = BL.decorate(base, "elytra_dome", {"rise_span": 0.32},
                       protect=clean_zone_solid, cuts=bolt_bores, region=decor_region,
                       cache_key="side_panel_right__carapace", wall_floor=1.5)
    ...
    def checks(parts, frame):
        return [*BL.decor_checks("side_panel_right__carapace"), ...]

DIVISION OF LABOUR, non-negotiable: build123d owns every MATING and FUNCTIONAL feature (bolt axes,
clip bores, seats, pockets, load-carrying walls) because those must match the frame numerically.
Blender owns decoration and organic form on top. The decorated mesh then runs the IDENTICAL module
checks plus the four extra rows in decor_checks(). A pretty part that does not fit is a failed part.

THE TWO MECHANISMS THAT MAKE THIS SAFE
  1. the protected region (`protect`), a guard solid EXACTLY FLUSH with every functional face, which
     becomes a vertex-group mask in Blender; no modifier may move a vertex inside it.
  2. the re-boolean on the way back: final = (mesh_solid + protect) - cuts. That restores genuine
     B-rep mating faces, so coaxial()/seats_on()/interference() are exact rather than tessellated -
     and it collapses the face count (measured 512 mesh faces -> 104 B-rep faces, full check suite
     0.6 s instead of tens of seconds).

A GUARD IS A MASK, NOT A TOLERANCE. A guard 0.2 mm proud of the part became real material after the
union: min Z 35.900 instead of 36.000, and the run failed both `no interference with the frame` and
`no unsupported overhangs`. Pad it tangentially if you like; never through a seating face. And it
must be the SMALLEST volume containing the mating features - a guard covering the whole bed froze
480 of 514 vertices and left nothing to sculpt.

DEGRADATION. decorate() never raises. If Blender is missing, the run fails, or any validation gate
fails, it returns the input part unchanged and records why; decor_checks() then reports
("decor: blender applied", False, "<reason>") - FALSE, not skipped, so the manifest records that the
part shipped undecorated. The geometry still passes every mating check, because the undecorated part
IS the verified functional solid. TIGERBEE_BLENDER="" forces that branch so CI can prove both.

NEVER WEAKEN A GATE TO MAKE A PRETTY PART PASS. Change the recipe parameters instead. The measured
rules exist precisely so parameters can be chosen to pass by construction:
    r = (D - w)/2 on the circumradius   amplitude <= period/12   direction "Z" on a plate
    voxel <= min_wall/3                 tri budget <= 12 000     export tolerance 0.02 / 0.3
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from build123d import Part, Solid, export_stl
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon,
                                BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing)
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt
from OCP.GProp import GProp_GProps
from OCP.ShapeFix import ShapeFix_Solid
from OCP.TopAbs import TopAbs_ShapeEnum
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

BLENDER = os.environ.get("TIGERBEE_BLENDER", "/usr/bin/blender")
ROOT = Path(__file__).resolve().parents[3]
CACHE = Path(os.environ.get("TIGERBEE_BLENDER_CACHE", ROOT / "build" / "blender"))
SCRIPTS = Path(__file__).resolve().parent / "_bl"
RECIPE_SCRIPT = SCRIPTS / "recipe.py"

RECIPES = ("elytra_dome", "carapace_lattice", "chitin", "sculpt", "emboss", "hardshell",
           "gyroid")
EXPORT_TOL, EXPORT_ANG = 0.02, 0.3   # volume error 0.0001 %, chord 0.02 mm - far below a 0.4 nozzle
TRI_BUDGET, TRI_CEILING = 12_000, 20_000
SEW_TOL = 1e-5
PLANAR_TOL = 1e-4
MIN_FACE_AREA = 1e-4   # mm2: below this an n-gon is a sliver whose OCCT face has no triangulation
WELD = 1e-4            # mm: near-duplicate mesh vertices merged on read (see _read_obj)
TIMEOUT = 240.0
# recipe -> (min, max) acceptable decorated/base volume ratio. `chitin` only ADDS material;
# a lattice only removes it - and a CHASSIS panel is MEANT to be mostly void (the family spec asks
# for >= 45 % of the plan bbox), so its lower bound is deliberately generous where the others are not.
VOLUME_BAND = {"elytra_dome": (0.90, 1.35), "carapace_lattice": (0.25, 1.02), "chitin": (0.98, 1.35),
               "sculpt": (0.90, 1.60), "emboss": (0.95, 1.06), "hardshell": (0.92, 1.02),
               # gyroid only ever REMOVES material (the void is cut out of the part) and is meant to
               # hollow it out hard: a slab thick enough for 1.5 periods keeps ~30-70 % of its volume,
               # and a part too thin for a void to survive keeps 100 % - which is a legal outcome.
               "gyroid": (0.22, 1.001)}
DEFAULT_BAND = (0.65, 1.35)


@dataclass
class DecorResult:
    """What decorate_ex() returns. `part` is always usable: decorated, or the untouched input."""

    part: Part
    applied: bool
    reason: str
    recipe: str
    stats: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)   # check rows for the module's checks()

    @property
    def ok(self) -> bool:
        return self.applied


RESULTS: dict[str, DecorResult] = {}   # cache_key -> last result, read by decor_checks()


def available() -> tuple[bool, str]:
    """(usable, reason). A probe, not a guess: an empty TIGERBEE_BLENDER is the documented way to
    force the degraded path."""
    if not BLENDER:
        return False, "TIGERBEE_BLENDER is empty (degraded path forced)"
    exe = shutil.which(BLENDER) or (BLENDER if Path(BLENDER).is_file() else None)
    if not exe:
        return False, f"blender not found at {BLENDER}"
    if not RECIPE_SCRIPT.is_file():
        return False, f"recipe script missing at {RECIPE_SCRIPT}"
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return False, f"blender --version failed: {exc}"
    return (r.returncode == 0), (r.stdout.splitlines() or [""])[0].strip() or "blender ok"


# --- mesh I/O --------------------------------------------------------------------------------
def _read_stl(path: Path) -> np.ndarray:
    """(n, 3, 3) float array of triangle corners, binary or ascii."""
    buf = path.read_bytes()
    if len(buf) >= 84:
        n = int.from_bytes(buf[80:84], "little")
        if 84 + n * 50 == len(buf):
            rec = np.frombuffer(buf, dtype=np.uint8, offset=84).reshape(n, 50)
            return rec[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(float)
    tri, cur = [], []
    for line in buf.decode("utf-8", "replace").splitlines():
        s = line.strip().split()
        if s and s[0] == "vertex":
            cur.append([float(s[1]), float(s[2]), float(s[3])])
            if len(cur) == 3:
                tri.append(cur)
                cur = []
    return np.array(tri, dtype=float)


def _read_obj(path: Path, weld: float = WELD) -> tuple[np.ndarray, list[list[int]]]:
    """Read the n-gon mesh and WELD near-duplicate vertices onto a `weld` grid.

    Welding is not cosmetic. Blender writes OBJ coordinates at six decimals, so two vertices that are
    the same point come back a few 1e-6 apart, and every such pair leaves a sliver face: measured
    smallest face areas of 1.1e-05 mm2 on a real panel. Those slivers are what make the sewn solid
    BRepCheck-invalid and give it faces with null triangulation - which build123d's Mesher rejects as
    "3mf mesh is invalid" while STL export silently drops them. This is the same merge-by-distance
    that bl_lib.repair() applies on the Blender side, done again after the text round trip."""
    verts, faces = [], []
    for line in path.read_text().splitlines():
        if line.startswith("v "):
            f = line.split()
            verts.append((float(f[1]), float(f[2]), float(f[3])))
        elif line.startswith("f "):
            faces.append([int(t.split("/")[0]) - 1 for t in line.split()[1:]])
    v = np.array(verts, dtype=float)
    if weld <= 0 or not len(v):
        return v, faces
    _uniq, inverse = np.unique(np.round(v / weld).astype(np.int64), axis=0, return_inverse=True)
    inverse = inverse.ravel()
    n = int(inverse.max()) + 1
    merged = np.zeros((n, 3))
    np.add.at(merged, inverse, v)
    merged /= np.bincount(inverse, minlength=n)[:, None]
    out = []
    for face in faces:
        idx = [int(inverse[i]) for i in face]
        ded = [idx[0]] + [b for a, b in zip(idx, idx[1:]) if a != b]
        if len(ded) > 2 and ded[0] == ded[-1]:
            ded.pop()
        if len(ded) >= 3:
            out.append(ded)
    return merged, out


def _sew(faces_occt) -> Solid:
    """Sew planar faces into a shell and close it into a solid, fixing an inside-out result.

    BRepBuilderAPI_MakeSolid can return an INSIDE-OUT solid from a correctly oriented mesh. It
    passes BRepCheck_Analyzer, and then every boolean returns the COMPLEMENT of what you asked -
    which is why the volume sign is checked and the solid reversed."""
    sew = BRepBuilderAPI_Sewing(SEW_TOL, True, True, True, False)
    for f in faces_occt:
        sew.Add(f)
    sew.Perform()
    shells = []
    exp = TopExp_Explorer(sew.SewedShape(), TopAbs_ShapeEnum.TopAbs_SHELL)
    while exp.More():
        shells.append(TopoDS.Shell_s(exp.Current()))
        exp.Next()
    if not shells:
        raise RuntimeError("sewing produced no shell")
    mk = BRepBuilderAPI_MakeSolid()
    for sh in shells:
        mk.Add(sh)
    fx = ShapeFix_Solid(mk.Solid())
    fx.Perform()
    solid = Solid(fx.Solid())
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(solid.wrapped, props)
    if props.Mass() < 0:
        solid = Solid(solid.wrapped.Reversed())
    return solid


def tris_to_solid(tris: np.ndarray) -> Solid:
    """Every triangle -> one planar Face, sewn into a Solid. Zero-area triangles are skipped, which
    leaves a HOLE - so merge-by-distance upstream (bl_lib.repair) rather than relying on this."""
    out = []
    for a, b, c in tris:
        if np.linalg.norm(np.cross(b - a, c - a)) / 2.0 < MIN_FACE_AREA:
            continue
        poly = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
        mf = BRepBuilderAPI_MakeFace(poly.Wire())
        if mf.IsDone():
            out.append(mf.Face())
    return _sew(out)


def _polygon_area(pts: np.ndarray) -> float:
    """Area of a planar polygon by the fan cross-product sum. An n-gon of essentially zero area is
    still a valid wire and OCCT will happily make a Face from it - and then that face has NULL
    triangulation, build123d's Mesher refuses the whole solid with "3mf mesh is invalid", and STL
    export quietly skips it instead. One such face out of 781 is enough; hence the area gate."""
    if len(pts) < 3:
        return 0.0
    a = pts[0]
    return float(sum(np.linalg.norm(np.cross(pts[i] - a, pts[i + 1] - a)) for i in range(1, len(pts) - 1)) / 2.0)


def polys_to_solid(verts: np.ndarray, faces: list[list[int]], planar_tol: float = PLANAR_TOL) -> Solid:
    """One OCCT face per planar n-gon - 3-7x off the OCCT rebuild versus the triangle path
    (measured: 7980 tris 7.50 s -> 973 n-gons 1.41 s; a sculpted mandible 115.59 s -> 15.80 s).

    Non-planar n-gons FALL BACK to a fan, because limited dissolve at 0.5 deg flattens genuine
    curvature: on a smoothly domed part the n-gon path drifted 84.2 mm3 (0.5 %). Recipes that
    produce curvature therefore never take this path at all."""
    out = []
    for idx in faces:
        pts = verts[idx]
        if len(pts) < 3:
            continue
        planar = True
        if len(pts) > 3:
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            ln = np.linalg.norm(n)
            if ln < 1e-12:
                planar = False
            else:
                n = n / ln
                planar = bool(np.max(np.abs((pts - pts[0]) @ n)) <= planar_tol)
        if planar and _polygon_area(pts) >= MIN_FACE_AREA:
            poly = BRepBuilderAPI_MakePolygon()
            for q in pts:
                poly.Add(gp_Pnt(*q))
            poly.Close()
            mf = BRepBuilderAPI_MakeFace(poly.Wire())
            if mf.IsDone():
                out.append(mf.Face())
                continue
        for k in range(1, len(pts) - 1):
            a, b, c = pts[0], pts[k], pts[k + 1]
            if np.linalg.norm(np.cross(b - a, c - a)) / 2.0 < MIN_FACE_AREA:
                continue
            tri = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
            mf = BRepBuilderAPI_MakeFace(tri.Wire())
            if mf.IsDone():
                out.append(mf.Face())
    return _sew(out)


# --- cache -----------------------------------------------------------------------------------
def _stl_bytes(shape, tol: float, ang: float, tmp: Path, name: str) -> bytes:
    path = tmp / f"{name}.stl"
    assert export_stl(shape, str(path), tolerance=tol, angular_tolerance=ang, ascii_format=False), name
    return path.read_bytes()


def _key(recipe: str, params: dict, blobs: dict[str, bytes], extra: dict) -> str:
    """BLAKE2b over recipe, sorted params, tolerances, the STL bytes of every input, the recipe
    script's own source and the Blender version. Hashing a 3 MB STL costs 11 ms; a hit skips the
    whole run, which is 0.5-1.2 s of Blender plus seconds to tens of seconds of OCCT sewing."""
    h = hashlib.blake2b(digest_size=20)
    h.update(recipe.encode())
    h.update(json.dumps(params, sort_keys=True, default=str).encode())
    h.update(json.dumps(extra, sort_keys=True, default=str).encode())
    for name in sorted(blobs):
        h.update(name.encode())
        h.update(blobs[name])
    h.update(RECIPE_SCRIPT.read_bytes() if RECIPE_SCRIPT.is_file() else b"")
    lib = SCRIPTS / "bl_lib.py"
    h.update(lib.read_bytes() if lib.is_file() else b"")
    h.update(available()[1].encode())
    return h.hexdigest()


# --- validation ------------------------------------------------------------------------------
def _valid_solid(solid) -> tuple[bool, str]:
    try:
        ok = bool(BRepCheck_Analyzer(solid.wrapped).IsValid())
    except Exception as exc:  # noqa: BLE001
        return False, f"BRepCheck threw: {exc}"
    return ok, "valid" if ok else "BRepCheck_Analyzer says invalid"


def _mesh_gates(stats: dict, tri_budget: int, band: tuple[float, float]) -> str:
    """The hard gates, in the order a failure is most informative. Returns "" when all pass."""
    rep = stats.get("decorated", {})
    if not rep.get("is_manifold"):
        return (f"decorated mesh is not manifold: {rep.get('non_manifold_edges')} non-manifold and "
                f"{rep.get('boundary_edges')} boundary edges")
    if rep.get("components", 1) != 1:
        return f"decorated mesh has {rep.get('components')} components (manifold does not mean connected)"
    if not rep.get("volume_mm3", 0) > 0:
        return f"decorated mesh signed volume {rep.get('volume_mm3')} - the mesh is inside out"
    ratio = stats.get("volume_ratio", 0.0)
    if not band[0] <= ratio <= band[1]:
        return f"volume ratio {ratio:.4f} outside the recipe band {band}"
    tris = stats.get("tris", 0)
    if tris > tri_budget:
        return f"{tris} triangles over the {tri_budget} budget"
    wall = stats.get("wall", {})
    if wall and not wall.get("ok"):
        return (f"mesh wall {wall.get('min_thickness')} mm under the floor at {wall.get('at')} "
                f"({wall.get('thin_rays')} thin of {wall.get('rays')} rays)")
    return ""


def _parse(stdout: str) -> dict:
    """Only `[BL] ...` lines are data; the cattrs / EXTENSIONS_OT_repo_sync / Fontconfig noise on
    stderr is harmless and ignored."""
    out: dict = {"reports": {}}
    for line in stdout.splitlines():
        if not line.startswith("[BL] "):
            continue
        rest = line[5:].strip()
        tag, _, payload = rest.partition(" ")
        try:
            data = json.loads(payload) if payload else True
        except json.JSONDecodeError:
            data = payload
        if tag == "report" and isinstance(data, dict):
            out["reports"][data.get("tag", "?")] = data
            out[data.get("tag", "?")] = data
        elif tag == "stats" and isinstance(data, dict):
            out.update(data)
        elif tag == "wall":
            out["wall"] = data
        else:
            out.setdefault(tag, data)
    return out


# --- the bridge ------------------------------------------------------------------------------
def decorate_ex(part: Part, recipe: str, params: dict | None = None, *, protect=None, cuts=None,
                region=None, mark=None, allow: tuple = (), restore=None, cache_key: str | None = None,
                wall_floor: float = 1.2, tri_budget: int = TRI_BUDGET, tolerance: float = EXPORT_TOL,
                angular: float = EXPORT_ANG, timeout: float = TIMEOUT, ngon: bool = True,
                guard_margin: float = 0.6) -> DecorResult:
    """Full result. See decorate() for the arguments; this one also hands back stats and check rows."""
    assert recipe in RECIPES, f"unknown recipe {recipe!r}; recipes: {RECIPES}"
    assert tri_budget <= TRI_CEILING, f"tri_budget {tri_budget} over the hard ceiling {TRI_CEILING}"
    params = dict(params or {})
    key = cache_key or getattr(part, "label", None) or f"{recipe}"

    def degrade(reason: str, stats: dict | None = None) -> DecorResult:
        res = DecorResult(part=part, applied=False, reason=reason, recipe=recipe, stats=stats or {})
        res.rows = _rows(res, wall_floor)
        RESULTS[key] = res
        return res

    ok, why = available()
    if not ok:
        return degrade(why)
    if protect is not None:
        pb, bb = protect.bounding_box(), part.bounding_box()
        proud = {ax: round(v, 4) for ax, v in
                 (("-" + a, getattr(bb.min, a) - getattr(pb.min, a)) for a in "XYZ")
                 if v > 1e-4}
        proud.update({ax: round(v, 4) for ax, v in
                      (("+" + a, getattr(pb.max, a) - getattr(bb.max, a)) for a in "XYZ")
                      if v > 1e-4})
        if proud:
            # A guard is a MASK, not a tolerance: 0.2 mm proud became real material after the union
            # and cost two frame checks. Refuse rather than ship it.
            return degrade(f"guard is proud of the part by {proud} mm - it must be exactly flush")
    n_solids = len(part.solids())
    if n_solids != 1:
        return degrade(f"input is {n_solids} solids, not one")

    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = CACHE / "_in"
    tmp.mkdir(parents=True, exist_ok=True)
    allow_union = None
    for a in allow:
        allow_union = a if allow_union is None else allow_union + a
    blobs = {"part": _stl_bytes(part, tolerance, angular, tmp, "part")}
    for name, shape in (("guard", protect), ("region", region), ("cuts", cuts), ("mark", mark),
                        ("allow", allow_union)):
        if shape is not None:
            blobs[name] = _stl_bytes(shape, tolerance, angular, tmp, name)
    extra = dict(tolerance=tolerance, angular=angular, wall_floor=wall_floor, tri_budget=tri_budget,
                 ngon=ngon, guard_margin=guard_margin)
    digest = _key(recipe, params, blobs, extra)
    slot = CACHE / digest
    cached_stats = slot / "stats.json"
    result_files = [slot / "result.obj", slot / "result.stl"]
    hit = cached_stats.is_file() and any(f.is_file() for f in result_files)
    t0 = time.time()
    if not hit:
        slot.mkdir(parents=True, exist_ok=True)
        for name, blob in blobs.items():
            (slot / f"{name}.stl").write_bytes(blob)
        job = dict(params)
        job.update(recipe=recipe, out_base=str(slot / "result"), wall_floor=wall_floor, tri_budget=tri_budget,
                   ngon=ngon, guard_margin=guard_margin,
                   **{n: str(slot / f"{n}.stl") for n in blobs})
        (slot / "params.json").write_text(json.dumps(job, indent=1, default=str))
        cmd = [BLENDER, "--background", "--factory-startup", "--python", str(RECIPE_SCRIPT), "--",
               str(slot / "params.json")]
        env = {**os.environ, "BLENDER_USER_SCRIPTS": "/nonexistent"}  # keep user addons out
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return degrade(f"blender timed out after {timeout} s")
        stats = _parse(proc.stdout)
        stats["blender_s"] = round(time.time() - t0, 3)
        if proc.returncode != 0 or "done" not in stats:
            tail = (proc.stderr or proc.stdout or "")[-500:]
            return degrade(f"blender rc={proc.returncode}: ...{tail}", stats)
        got = stats.get("out", {})
        produced = Path(got["path"]) if isinstance(got, dict) and got.get("path") else slot / "result.stl"
        if not produced.is_file():
            return degrade(f"blender produced no output at {produced}", stats)
        stats["result"] = produced.name
        cached_stats.write_text(json.dumps(stats, indent=1, default=str))
    else:
        stats = json.loads(cached_stats.read_text())
        produced = slot / stats.get("result", "result.stl")
        if not produced.is_file():
            produced = next(f for f in result_files if f.is_file())

    band = VOLUME_BAND.get(recipe, DEFAULT_BAND)
    gate = _mesh_gates(stats, tri_budget, band)
    if gate:
        return degrade(gate, stats)

    t1 = time.time()
    try:
        if produced.suffix == ".obj":
            verts, faces = _read_obj(produced)
            solid = polys_to_solid(verts, faces)
            stats["rebuild_faces"] = len(faces)
        else:
            solid = tris_to_solid(_read_stl(produced))
    except Exception as exc:  # noqa: BLE001
        return degrade(f"mesh -> solid failed: {exc}", stats)
    stats["sew_s"] = round(time.time() - t1, 3)
    ok, why = _valid_solid(solid)
    if not ok:
        try:    # one ShapeFix pass: a sewn mesh solid often only needs its tolerances rebuilt
            fx = ShapeFix_Solid(solid.wrapped)
            fx.Perform()
            cand = Solid(fx.Solid())
            if _valid_solid(cand)[0]:
                solid, ok = cand, True
                stats["shapefix_sewn"] = True
        except Exception as exc:  # noqa: BLE001
            why = f"{why}; ShapeFix threw {type(exc).__name__}"
    if not ok:
        return degrade(f"rebuilt solid: {why}", stats)

    # THE RE-BOOLEAN: final = (mesh_solid + guard) - cuts. Restores exact B-rep mating faces and
    # collapses the face count. A mesh-derived solid can make OCCT throw outright, so this whole
    # block degrades rather than propagating - decorate() must never raise.
    try:
        final = Part() + solid
        back = protect if restore is None else restore
        if back:   # falsy (None or False) means re-union nothing
            final = final + back
        if cuts is not None:
            final = final - cuts
    except Exception as exc:  # noqa: BLE001
        return degrade(f"re-boolean threw: {type(exc).__name__}: {exc}", stats)
    if len(final.solids()) != 1:
        return degrade(f"after the re-boolean the part is {len(final.solids())} solids", stats)
    ok, why = _valid_solid(final.solid())
    if not ok:
        # one repair attempt: ShapeFix on the sewn solid, then the same gate again. A mesh-derived
        # solid often only needs its tolerances rebuilt; if it still fails, ship undecorated.
        try:
            fx = ShapeFix_Solid(final.solid().wrapped)
            fx.Perform()
            repaired = Part() + Solid(fx.Solid())
            if cuts is not None:
                repaired = repaired - cuts
            if len(repaired.solids()) == 1 and _valid_solid(repaired.solid())[0]:
                final, ok = repaired, True
                stats["shapefix"] = True
        except Exception as exc:  # noqa: BLE001
            why = f"{why}; ShapeFix threw {type(exc).__name__}"
    if not ok:
        return degrade(f"re-booleaned solid: {why}", stats)
    # The FINAL volume, not just the mesh's: the re-boolean can hand back a valid single solid that is
    # geometric nonsense. One measured run returned 1 solid, BRepCheck valid, 2 faces and -0.0 mm3 -
    # and every gate above passed it. Check the thing that actually ships.
    # against the part PLUS whatever `restore` adds back - a restore that reassembles CAD structure
    # round a decorated sub-part legitimately multiplies the volume, and comparing to the sub-part
    # alone rejects a perfectly good result (measured 1.4477 against a 1.02 ceiling)
    reference = part.volume
    if back is not None and back is not False and back is not part:
        try:
            reference = (Part() + part + back).volume
        except Exception:  # noqa: BLE001
            reference = part.volume + float(back.volume)
    final_ratio = (final.volume / reference) if reference else 0.0
    stats["final_volume_ratio"] = round(final_ratio, 5)
    if not band[0] <= final_ratio <= band[1]:
        return degrade(f"re-booleaned volume ratio {final_ratio:.4f} outside the recipe band {band} "
                       f"({final.volume:.1f} of {part.volume:.1f} mm³)", stats)
    # Can the thing actually be EXPORTED? A sewn solid can be BRepCheck-valid and still contain a
    # face with null triangulation, which makes build123d's Mesher refuse it ("3mf mesh is invalid")
    # while STL export silently skips the face. Catching it here means a decorated part either
    # exports cleanly or ships undecorated - the exporter never dies halfway through a run.
    try:
        from build123d import Mesher
        probe = Mesher()
        probe.add_shape(final, linear_deflection=tolerance, angular_deflection=angular,
                        part_number="decor-probe")
    except Exception as exc:  # noqa: BLE001
        return degrade(f"decorated solid will not mesh for export: {exc}", stats)
    bb0, bb1 = part.bounding_box(), final.bounding_box()
    growth = max(max(getattr(bb0.min, a) - getattr(bb1.min, a) for a in "XYZ"),
                 max(getattr(bb1.max, a) - getattr(bb0.max, a) for a in "XYZ"))
    stats["envelope_growth_mm"] = round(growth, 4)
    stats["b_rep_faces"] = len(final.faces())
    stats["cached"] = hit
    stats["total_s"] = round(time.time() - t0, 3)
    final.label = getattr(part, "label", "") or ""
    res = DecorResult(part=final, applied=True, reason="cached" if hit else "", recipe=recipe, stats=stats)
    res.rows = _rows(res, wall_floor)
    RESULTS[key] = res
    return res


def decorate(part: Part, recipe: str, params: dict | None = None, protect=None, cache_key: str | None = None,
             **kw) -> Part:
    """Decorate `part` with `recipe` and hand back a build123d Part - the decorated one, or the
    input unchanged when Blender is unavailable or any gate fails. Never raises.

      part        the FUNCTIONAL solid: 100 % of the mating and load geometry, plus the style's
                  silhouette (plan outline, apertures, ribs, cusps)
      recipe      one of RECIPES
      params      the recipe's own parameters (see RECIPE_PARAMS)
      protect     the MASK: the clean zone Blender may not move a vertex inside, exactly flush with
                  every functional face. It may be large - stating it as "everything except the skin
                  I want swelled" is the safest way to write it.
      restore     the solid re-unioned on the way back, defaulting to `protect`. Keep it SMALL and
                  exact: it exists to turn the mating faces back into real B-rep geometry, and a mask
                  that covers most of the part makes a terrible boolean operand - a whole-panel mask
                  re-unioned with its own tessellation came back as 242 solids. Mask big, restore
                  small; they are different jobs.
      cache_key   the label this result is filed under, for decor_checks(); defaults to part.label
      cuts        functional cuts re-applied after decoration (bores, seats, the suture, the mark)
      region      where decoration is ALLOWED (the outline inset by the ligament, minus load paths)
      mark        an emboss mark mesh, for recipe "emboss"
      allow       declared thin features (a deboss mark, a lip). A ray sampler cannot tell a narrow
                  groove from a thin wall - a 0.6 deep mark on a 1.5 wall reads as 0.9 mm - so the
                  mark's own solid is passed here and those samples are skipped, exactly as
                  _fit.min_wall(allow=...) does on the CAD side. Declare it; do not lower the floor.
      wall_floor  the material minimum wall, measured on the mesh in Blender
      tri_budget  <= 12 000 (hard ceiling 20 000): OCCT sewing is the entire cost and ~quadratic
      ngon        rebuild through the OBJ/n-gon path; recipes that create curvature ignore it

    Splice the result's rows into the module's checks() with decor_checks(cache_key)."""
    return decorate_ex(part, recipe, params, protect=protect, cache_key=cache_key, **kw).part


def _rows(res: DecorResult, wall_floor: float) -> list[tuple[str, bool, str]]:
    s = res.stats
    wall = s.get("wall", {}) or {}
    rows = [(f"decor: blender applied ({res.recipe})", res.applied,
             res.reason or f"{s.get('tris', '?')} tris, ratio {s.get('volume_ratio', '?')}, "
                           f"{s.get('b_rep_faces', '?')} B-rep faces, {s.get('total_s', '?')} s")]
    if not res.applied:
        return rows
    rep = s.get("decorated", {})
    rows.append(("decor: one closed manifold solid, one component",
                 bool(rep.get("is_manifold")) and rep.get("components") == 1,
                 f"manifold={rep.get('is_manifold')}, components={rep.get('components')}, "
                 f"{rep.get('boundary_edges')} boundary edges"))
    rows.append((f"decor: mesh wall >= {wall_floor} (Blender rays, guard and allow skipped)",
                 bool(wall.get("ok")),
                 f"min {wall.get('min_thickness')} mm at {wall.get('at')}, {wall.get('rays')} rays, "
                 f"{wall.get('thin_rays')} thin, {wall.get('grazing_rejected')} grazing rejected"))
    growth = s.get("envelope_growth_mm", 0.0)
    rows.append(("decor: envelope growth <= 2.0 mm", growth <= 2.0 + 1e-6, f"{growth} mm"))
    if res.recipe == "gyroid":
        gy = (s.get("recipe") or {}).get("gyroid") or {}
        if isinstance(gy, dict):
            rows.append((f"decor: gyroid sheet {gy.get('sheet')} mm held over {gy.get('cells')} cells "
                         f"(period {gy.get('period')})", bool(wall.get("ok")),
                         f"measured min {wall.get('min_thickness')} mm, voxel {gy.get('voxel')}, "
                         f"grid {gy.get('grid')}, {gy.get('iso_tris')} iso tris"))
    if res.recipe == "carapace_lattice":
        lat = (s.get("recipe") or {}).get("carapace_lattice") or {}
        if isinstance(lat, dict):
            rows.append((f"decor: ligament >= {lat.get('ligament')} ({lat.get('cell')}, "
                         f"{lat.get('cells')} cells)", bool(wall.get("ok")),
                         f"measured min {wall.get('min_thickness')} mm"))
    return rows


def decor_checks(cache_key: str, absent_ok: bool = False) -> list[tuple[str, bool, str]]:
    """The rows a module splices into its own checks(). When nothing was recorded under this key the
    module either did not call decorate() or called it with a different key, which is itself worth a
    failing row rather than a silent skip."""
    res = RESULTS.get(cache_key)
    if res is None:
        return [] if absent_ok else [(f"decor: recorded for {cache_key}", False, "no decorate() call recorded")]
    return list(res.rows)


def clear_results() -> None:
    RESULTS.clear()


def decor_region(part: Part, inset: float, minus=(), pad: float = 2.0, axis: str = "Z"):
    """The region a lattice or vent cutter may live in: the part's largest face normal to `axis`,
    inset by `inset` in its own plane and extruded back through the whole part plus `pad`, minus
    anything in `minus` (the guard, load paths).

    PASS THIS, not the raw outline. Without the inset, the recipe's region clip cuts border cells
    flush with the silhouette and leaves a knife edge - measured 0.0121 mm against a 1.5 mm floor on
    a hex field whose interior ligaments were all correct. Set `inset` to the ligament.

    `axis` is the part's thickness direction, the same one the recipe is given: "Z" for a plate on the
    bed, "X" for a vertical side wall. Returns None when the part has no face normal to that axis or
    OCCT cannot offset its outline; the recipe then runs unclipped, which is only safe when the cutter
    is already inside the outline."""
    from build123d import Plane, Sketch
    from build123d import extrude as _extrude
    from build123d import offset as _offset
    ax = axis.upper()
    n = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[ax]
    faces = [f for f in part.faces() if f.geom_type.name == "PLANE"
             and abs(sum(a * b for a, b in zip(f.normal_at().to_tuple(), n))) > 0.999]
    if not faces:
        return None
    top = max(faces, key=lambda f: f.area)
    local = Plane(origin=top.center().to_tuple(), z_dir=n)
    try:
        inner = _offset(Sketch() + local.to_local_coords(top), -abs(inset))
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(inner, Sketch) or not inner.faces():
        return None
    bb = part.bounding_box()
    lo, size = {"X": (bb.min.X, bb.size.X), "Y": (bb.min.Y, bb.size.Y), "Z": (bb.min.Z, bb.size.Z)}[ax]
    # the sketch came back in the face's OWN local frame, so it must be replaced on a plane with the
    # same origin and x_dir, slid along the axis to the start of the extrusion - not on a plane at the
    # world origin, which drops the face's in-plane offset and lands the region 20 mm away
    c = top.center()
    origin = tuple((lo - pad) if abs(ni) > 0.5 else ci for ni, ci in zip(n, c.to_tuple()))
    base = Plane(origin=origin, z_dir=n, x_dir=local.x_dir.to_tuple())
    reg = _extrude(base * inner, amount=size + 2 * pad, dir=n)
    for m in minus:
        reg = reg - m
    return reg if reg is not None and reg.volume > 0 else None


# --- recipe parameter reference (what `params` accepts) ---------------------------------------
RECIPE_PARAMS = {
    "elytra_dome": dict(rise_span=0.32, rise=0.0, subdiv=2, relax=6, min_nz=0.75, feather=3.0,
                        axis="Z", flat=(), dome_spread=1.0),
    "carapace_lattice": dict(cell="round|hex|voronoi", ligament=1.6, cell_d=0.0, sides=16, seed=7,
                             axis="Z"),
    "chitin": dict(period=12.0, amplitude=0.8, texture="WOOD|STUCCI|CLOUDS", subdiv=2, min_nz=0.7,
                   axis="Z"),
    "sculpt": dict(mode="curve|skin|meta", voxel=0.35,
                   strokes=[{"points": [[0, 0, 0]], "radii": [1.0]}]),
    "emboss": dict(depth=0.6, raised=False, mark_subdiv=3),
    "hardshell": dict(width=0.4, segments=2, angle=35.0, min_len=6.0, feather=1.5),
    # `skin`: "closed" keeps a full `rind` on every face (the wall floor is then a construction);
    # "open" erodes IN PLAN only, so the sheet breaks the two faces normal to `axis` and the openings
    # emerge instead of being cut - at the price of a wall the bridge's own gate has to judge.
    # `period` is a REQUEST: the recipe grows it and coarsens `voxel` until the mesh fits tri_budget.
    # CALL IT WITH restore=False: the void is cut back from a PADDED guard, so the mating zone is
    # already untouched CAD, and re-unioning the guard solid on top is a geometric no-op that still
    # restructures the shape (1998 faces -> 808) and leaves a solid the 3MF mesher refuses.
    "gyroid": dict(period=10.0, sheet=1.6, rind=1.6, voxel=1.2, axis="Z", skin="closed|open",
                   sheet_bias=0.12, quality=9.0, period_max=3.0, iso_fraction=0.75),
}
