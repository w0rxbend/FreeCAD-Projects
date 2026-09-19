"""Verify the built frame and the exported files (spec section 6).

Run after `python -m tigerbee`: `uv run python scripts/verify.py [--dist DIR]`.
Prints one PASS line per check and exits non-zero on the first failure.
"""

import sys
from itertools import combinations
from math import hypot, pi
from pathlib import Path

from build123d import Axis, CenterOf, Face, GeomType, Mesher, import_step, import_stl

from tigerbee import params as P
from tigerbee.export import reopen_counts
from tigerbee.frame import PLATES, build_frame, motor_centers
from tigerbee.mounts import HOLES, PATTERNS, holes_for
from tigerbee.profiles import arm_holes, build_arm, column, cutouts, motor_bolts

DIST = Path(sys.argv[sys.argv.index("--dist") + 1]) if "--dist" in sys.argv else Path(__file__).resolve().parents[1] / "dist"
NAMES = ["plate_bottom", "plate_mid", "plate_top", "arm_front_left", "arm_front_right", "arm_rear_left",
         "arm_rear_right", "standoff_front_tip_left", "standoff_front_tip_right", "standoff_front_arm_left",
         "standoff_front_arm_right", "standoff_rear_arm_left", "standoff_rear_arm_right",
         "standoff_rear_tip_left", "standoff_rear_tip_right"]
WEB = 2.5


def check(ok: bool, msg: str) -> None:
    if not ok:
        print(f"FAIL {msg}")
        sys.exit(1)
    print(f"PASS {msg}")


def is_void(shape, probe) -> bool:
    res = shape.intersect(probe)  # ShapeList or None in build123d 0.11
    return res is None or sum(s.volume for s in res.solids()) < 1e-3


def solid_volume(shape, probe) -> float:
    res = shape.intersect(probe)
    return 0.0 if res is None else sum(s.volume for s in res.solids())


def top_circles(part) -> list[tuple[float, float, float]]:
    """(x, y, r) of every circular edge on the part's top face."""
    face = part.faces().sort_by(Axis.Z)[-1]
    return [(e.arc_center.X, e.arc_center.Y, e.radius) for e in face.edges() if e.geom_type == GeomType.CIRCLE]


def has_circle(circles, x, y, d) -> bool:
    return any(abs(r - d / 2) < 0.01 and hypot(cx - x, cy - y) < 0.02 for cx, cy, r in circles)


def arm_for(x: float, y: float) -> str:
    """Placed arm whose root covers the stack/root axis at (x, y)."""
    return f"arm_{'front' if y > 0 else 'rear'}_{'right' if x > 0 else 'left'}"


def rel_close(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-9)


def bbox_close(a, b, tol: float) -> bool:
    scale = max(a.size.X, a.size.Y, a.size.Z)
    return all(abs(getattr(a.min, k) - getattr(b.min, k)) <= tol * scale
               and abs(getattr(a.max, k) - getattr(b.max, k)) <= tol * scale for k in "XYZ")


def main() -> None:
    bb = column(0, 0, 0, 9, 1.55).bounding_box()
    check(abs(bb.min.Z) < 1e-6 and abs(bb.max.Z - 9) < 1e-6, "column() probe is lower-face aligned")

    compound, parts = build_frame()
    check(list(parts) == NAMES, "15 parts with the expected labels")
    L = P.ROOT_TO_MOTOR
    circles = {name: top_circles(parts[name]) for name in NAMES if not name.startswith("standoff")}

    # 1. wheelbase
    m = motor_centers()
    d1 = hypot(m["front_right"][0] - m["rear_left"][0], m["front_right"][1] - m["rear_left"][1])
    d2 = hypot(m["front_left"][0] - m["rear_right"][0], m["front_left"][1] - m["rear_right"][1])
    check(abs(d1 - P.WHEELBASE) < 0.01 and abs(d2 - P.WHEELBASE) < 0.01, f"wheelbase {d1:.4f} / {d2:.4f} = {P.WHEELBASE}")
    check(all(any(abs(r - P.D_MOTOR_BORE / 2) < 0.01 and hypot(cx - x, cy - y) < 0.01 for cx, cy, r in circles[f"arm_{k}"])
              for k, (x, y) in m.items()), "motor bores of the built arms sit at the motor centres")

    # 2. every hole exists
    located: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for h in HOLES:
        for plate in h.plates:
            check(has_circle(circles[plate], h.x, h.y, h.d), f"{plate}: {h.name} Ø{h.d} at ({h.x:.4f}, {h.y:.4f})")
            located.setdefault((h.name, plate), []).append((h.x, h.y))
    stack_axis = {"arm_front_right": (1, 1), "arm_front_left": (-1, 1), "arm_rear_right": (1, -1), "arm_rear_left": (-1, -1)}
    for name, placement in P.ARM_PLACEMENTS.items():
        local = [(c, P.D_M3) for c in P.root_holes()] + [(c, P.D_M3) for c in motor_bolts(L)] + [((0, L), P.D_MOTOR_BORE)]
        for (lx, ly), d in local:
            x, y = P.place(lx, ly, placement)
            check(has_circle(circles[name], x, y, d), f"{name}: Ø{d} at ({x:.3f}, {y:.3f})")
        dx, dy = P.place(0, L + P.DIAMOND_OFFSET, placement)
        check(is_void(parts[name], column(dx, dy, P.Z_ARM, P.ARM_T, 0.5)), f"{name}: diamond cutout open")
        sx, sy = stack_axis[name]
        gx, gy = sx * P.PITCH_30 / 2, sy * P.PITCH_30 / 2
        check(is_void(parts[name], column(gx, gy, P.Z_ARM, P.ARM_T, P.D_STACK_NOTCH / 2 - 0.15)),
              f"{name}: stack notch relief open over Z 2-7 at ({gx}, {gy})")
    for h in [h for h in HOLES if h.through_arm]:
        r, arm = h.d / 2 - 0.05, arm_for(h.x, h.y)
        for layer, part, z0, hh in (("plate_bottom", parts["plate_bottom"], 0, P.PLATE_T), (arm, parts[arm], P.Z_ARM, P.ARM_T),
                                    ("plate_mid", parts["plate_mid"], P.Z_MID, P.PLATE_T), ("frame", compound, 0, P.Z_MID + P.PLATE_T)):
            check(is_void(part, column(h.x, h.y, z0, hh, r)), f"{h.name} ({h.x:.3f}, {h.y:.3f}) through {layer} Z {z0}-{z0 + hh}")
    for plate, z in PLATES.items():
        for w in cutouts(plate):
            c = Face(w).center(CenterOf.MASS)
            check(is_void(parts[plate], column(c.X, c.Y, z, P.PLATE_T, 0.5)), f"{plate}: cutout at ({c.X:.2f}, {c.Y:.2f}) open")

    # 3. pitches
    for name, pat in PATTERNS.items():
        pts = located[(name, next(h.plates[0] for h in HOLES if h.name == name))]
        dists = sorted(hypot(a[0] - b[0], a[1] - b[1]) for a, b in combinations(pts, 2))
        cx, cy = sum(p[0] for p in pts) / 4, sum(p[1] for p in pts) / 4
        check(len(pts) == 4 and all(abs(d - pat["pitch"]) < 0.01 for d in dists[:4])
              and abs(cx - pat["center"][0]) < 0.01 and abs(cy - pat["center"][1]) < 0.01,
              f"pattern {name}: pitch {pat['pitch']} centre {pat['center']}")

    # 4. web clearance
    for plate, z in PLATES.items():
        hs = holes_for(plate)
        worst = min((hypot(a.x - b.x, a.y - b.y) - a.d / 2 - b.d / 2, a.name, b.name) for a, b in combinations(hs, 2))
        check(worst[0] >= WEB, f"{plate}: min hole-to-hole web {worst[0]:.2f} mm ({worst[1]} / {worst[2]})")
        for h in [h for h in hs if h.new]:
            ring = column(h.x, h.y, z, P.PLATE_T, h.d / 2 + WEB)
            expected = pi * ((h.d / 2 + WEB) ** 2 - (h.d / 2) ** 2) * P.PLATE_T
            got = solid_volume(parts[plate], ring)
            check(rel_close(got, expected, 0.01), f"{plate}: NEW {h.name} ({h.x}, {h.y}) has {WEB} mm web all round ({got:.1f}/{expected:.1f} mm³)")

    # 5. no interference
    boxes = {n: p.bounding_box() for n, p in parts.items()}
    pairs = 0
    for a, b in combinations(NAMES, 2):
        ba, bb_ = boxes[a], boxes[b]
        if all(getattr(ba.min, k) <= getattr(bb_.max, k) and getattr(bb_.min, k) <= getattr(ba.max, k) for k in "XYZ"):
            pairs += 1
            v = solid_volume(parts[a], parts[b])
            if v >= 1e-3:
                check(False, f"{a} intersects {b}: {v:.3f} mm³")
    check(True, f"no interference in {pairs} bbox-overlapping part pairs ({len(NAMES) * (len(NAMES) - 1) // 2} total)")
    arms = [n for n in NAMES if n.startswith("arm")]
    gaps = [(parts[a].distance_to(parts[b]), a, b) for a, b in combinations(arms, 2)]
    check(min(gaps)[0] >= 0.1, f"arm roots stay apart, min gap {min(gaps)[0]:.3f} mm")

    # 6. valid solids, arm relief depth
    for name, part in parts.items():
        check(len(part.solids()) == 1 and part.is_valid and part.volume > 0, f"{name}: one valid solid, {part.volume:.1f} mm³")
    arm, arm_full = build_arm(), build_arm(relief=False)
    removed = arm_full.volume - arm.volume
    check(abs(removed - 30.9) < 1.5 and len(arm.solids()) == 1, f"arm notch relief removes {removed:.2f} mm³ over the full thickness")
    check(is_void(arm, column(*P.STACK_NOTCH_XY, 0, P.ARM_T, P.D_STACK_NOTCH / 2 - 0.15)), "arm-local keyhole open over Z 0-5")

    # 7. round trip of the exported files
    for name, part in parts.items():
        bb = part.bounding_box()
        s = import_step(DIST / "step" / f"{name}.step")
        check(rel_close(s.volume, part.volume, 0.005) and bbox_close(s.bounding_box(), bb, 0.005), f"{name}.step round trip")
        meshes = Mesher().read(DIST / "3mf" / f"{name}.3mf")
        vol = sum(x.volume for x in meshes)
        mb = meshes[0].bounding_box()
        for x in meshes[1:]:
            mb = mb.add(x.bounding_box())
        check(rel_close(vol, part.volume, 0.005) and bbox_close(mb, bb, 0.005), f"{name}.3mf round trip")
        stl = import_stl(DIST / "stl" / f"{name}.stl")
        check(len(stl.faces()) > 0 and bbox_close(stl.bounding_box(), bb, 0.005), f"{name}.stl round trip")
    asm = import_step(DIST / "step" / "tigerbee.step")
    check([c.label for c in asm.children] == NAMES, "tigerbee.step has 15 labelled children")

    # 8. FCStd files reopen in FreeCAD
    files = [DIST / "freecad" / f"{n}.FCStd" for n in ("tigerbee", *NAMES)]
    rows = {Path(r["out"]).stem: r for r in reopen_counts(files)}
    for f in files:
        row, want = rows[f.stem], len(NAMES) if f.stem == "tigerbee" else 1
        check(row["features"] == want and row["doc"] == f.stem, f"{f.name}: reopens as '{row['doc']}' with {row['features']} Part::Feature")

    # 9. summary
    counts = {plate: len(holes_for(plate)) for plate in PLATES}
    counts["arm"] = len(arm_holes(L)) + 1
    check(counts == {"plate_bottom": 31, "plate_mid": 31, "plate_top": 14, "arm": 9}, f"hole counts {counts}")
    nfiles = {ext: len(list((DIST / sub).glob(f"*.{ext}"))) for sub, ext in (("step", "step"), ("stl", "stl"), ("3mf", "3mf"), ("freecad", "FCStd"))}
    check(all(n == 16 for n in nfiles.values()), f"files {nfiles}")
    print(f"OK wheelbase {P.WHEELBASE} mm, root_to_motor {L:.4f} mm, {len(NAMES)} parts, dist = {DIST}")


if __name__ == "__main__":
    main()
