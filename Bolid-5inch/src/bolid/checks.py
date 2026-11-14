"""Checks of the frame as modelled. Every row is (name, passed, measured detail)."""

from itertools import combinations
from math import hypot

from bolid import gear as G
from bolid import geometry as GEO
from bolid import params as P

Row = tuple[str, bool, str]
EPS = 1e-3
CARBON = 1.55e-3  # g / mm3
ALUMINIUM = 2.7e-3
MIN_WEB = 2.0
MASS_LIMIT = 140.0  # a heavy-duty 5" freestyle class frame: 6 mm arms


def overlap(a, b) -> float:
    A, B = a.bounding_box(), b.bounding_box()
    if (
        A.max.X < B.min.X
        or B.max.X < A.min.X
        or A.max.Y < B.min.Y
        or B.max.Y < A.min.Y
        or A.max.Z < B.min.Z
        or B.max.Z < A.min.Z
    ):
        return 0.0
    try:
        return float((a & b).volume)
    except Exception:  # noqa: BLE001 - OCCT throws on some touching-only contacts
        return 0.0


def bore(part, xy, d: float, z0: float, z1: float) -> tuple[bool, str]:
    """A pin of diameter d passes the part between z0 and z1, and the part is there round it."""
    pin = G.cyl(*xy, z0, z1, d)
    ring = G.cyl(*xy, z0, z1, d + 2.4) - G.cyl(*xy, z0 - 1, z1 + 1, d + 0.4)
    inside, around = overlap(part, pin), overlap(part, ring)
    return inside < EPS and around > EPS, f"{inside:.3f} mm3 in the bore, {around:.1f} mm3 round it"


def plate_web(face) -> float:
    f = face.faces()[0]
    wires = [f.outer_wire(), *f.inner_wires()]
    best = float("inf")
    for a, b in combinations(wires, 2):
        A, B = a.bounding_box(), b.bounding_box()
        if A.min.X - B.max.X > best or B.min.X - A.max.X > best or A.min.Y - B.max.Y > best or B.min.Y - A.max.Y > best:
            continue
        best = min(best, a.distance_to(b))
    return best


def frame_checks() -> list[Row]:
    rows: list[Row] = []
    parts = GEO.parts()
    for name, part in parts.items():
        n = len(part.solids())
        rows.append((f"{name}: one valid solid", n == 1 and part.is_valid, f"{n} solid(s), {part.volume:.0f} mm3"))
    hits = [(a, b, round(v, 3)) for (a, pa), (b, pb) in combinations(parts.items(), 2) if (v := overlap(pa, pb)) > EPS]
    rows.append(("no two frame parts overlap", not hits, str(hits or "none")))

    bad = []
    layers = {
        "plate_bottom": (P.Z_BOT, P.Z_ARM),
        "plate_press": (P.Z_PRESS, P.Z_BAY),
        **{f"arm_{q}": (P.Z_ARM, P.Z_PRESS) for q in P.QUADS},
    }
    for xy in GEO.clamp_bolts():
        for nm, (z0, z1) in layers.items():
            if nm.startswith("arm_") and not GEO.in_quad(nm[4:], xy):
                continue
            ok, d = bore(parts[nm], xy, 3.0, z0 + 0.01, z1 - 0.01)
            if not ok:
                bad.append(f"{xy} in {nm}: {d}")
    for xy in P.STANDOFFS:
        ok, d = bore(parts["plate_top"], xy, 3.0, P.Z_TOP + 0.01, P.Z_ROOF - 0.01)
        if not ok:
            bad.append(f"{xy} in plate_top: {d}")
    rows.append(("every bolt passes every plate it clamps", not bad, "; ".join(bad) or "all bores open and walled"))

    # the roots: each arm bears on its neighbours along the centre lines, across a 1 mm gap
    bearing = []
    for a, b in (
        ("front_right", "front_left"),
        ("rear_right", "rear_left"),
        ("front_right", "rear_right"),
        ("front_left", "rear_left"),
    ):
        A, B = GEO.arm(a).face, GEO.arm(b).face
        bearing.append(A.distance_to(B))
    rows.append(
        (
            "arm roots bear on each other",
            max(bearing) <= 2 * P.ROOT_GAP + 0.01,
            f"gaps {[round(g, 2) for g in bearing]} mm",
        )
    )

    gaps = [hypot(a[0] - b[0], a[1] - b[1]) - P.PROP_D for a, b in combinations(P.MOTORS.values(), 2)]
    rows.append(("props clear each other", min(gaps) >= P.TIP_GAP_MIN, f"{min(gaps):.1f} mm between tips"))
    body = {n: p for n, p in parts.items()}
    for q, xy in P.MOTORS.items():
        k = G.keepout(xy)
        inside = {n: round(v, 2) for n, p in body.items() if (v := overlap(p, k)) > EPS}
        rows.append((f"prop {q}: frame stays {P.PROP_MARGIN} mm outside its disc", not inside, str(inside or "clear")))

    gear = G.build()
    probes = {
        "4-in-1 ESC": gear["esc"][0],
        "flight controller": gear["fc"][0],
        "digital VTX on the tail": gear["vtx"][0],
        "receiver": gear["rx"][0],
        f"camera {G.TILT[0]:g}-{G.TILT[1]:g} deg": G.camera_sweep(),
        "battery": gear["battery"][0],
    }
    for label, probe in probes.items():
        inside = {n: round(v, 2) for n, p in parts.items() if (v := overlap(p, probe)) > EPS}
        rows.append((f"{label} fits", not inside, str(inside or "clear")))
    for q, xy in P.MOTORS.items():
        k = G.keepout(xy)
        hit = {n: round(v, 1) for n in ("battery", "camera") if (v := overlap(gear[n][0], k)) > EPS}
        rows.append((f"prop {q}: clear of the battery and camera", not hit, str(hit or "clear")))

    for name, make in GEO.PLATES.items():
        web = plate_web(make().face)
        rows.append((f"{name}: narrowest carbon web", web >= MIN_WEB - 1e-6, f"{web:.2f} mm"))
    carbon = sum(p.volume * CARBON for n, (p, m) in GEO.build().items() if m == "carbon")
    alu = sum(p.volume * ALUMINIUM for n, (p, m) in GEO.build().items() if m == "aluminium")
    rows.append(
        (f"frame mass under {MASS_LIMIT:g} g", carbon < MASS_LIMIT, f"{carbon:.1f} g carbon + {alu:.1f} g standoffs")
    )
    return rows


def report(rows: list[Row]) -> bool:
    for name, ok, detail in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    failed = sum(1 for r in rows if not r[1])
    print(f"{len(rows) - failed}/{len(rows)} checks passed")
    return failed == 0
