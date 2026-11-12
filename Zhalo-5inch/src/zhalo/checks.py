"""Geometry checks for the frame. Every row is (name, passed, measured detail).

Run with `uv run zhalo check`. The same primitives (interference, bore probes, prop keep-out)
are reused by the accessory checks in `zhalo.accessories.fit`.
"""

from itertools import combinations
from math import hypot

from build123d import Part

from zhalo import design
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P

Row = tuple[str, bool, str]
EPS = 1e-3  # mm^3: a boolean intersection smaller than this is numerical noise
CARBON_DENSITY = 1.55e-3  # g / mm^3
ALUMINIUM_DENSITY = 2.7e-3
MIN_WEB = 2.0  # least carbon allowed between two cuts, or between a cut and the edge
MIN_RADIUS = 1.0  # every corner can be cut with a 2 mm router bit


def volume_of(shape) -> float:
    return 0.0 if shape is None else float(shape.volume)


def overlap(a: Part, b: Part) -> float:
    """Shared volume of two solids, 0 when they are apart."""
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
        return volume_of(a & b)
    except Exception:  # noqa: BLE001 - OCCT throws on some touching-only contacts
        return 0.0


def bore_clear(part: Part, xy, d: float, z0: float, z1: float, wall: float = 1.0) -> tuple[bool, str]:
    """True when a pin of diameter d on the vertical axis through xy passes `part` between z0 and z1
    without touching it, and the part really is there round the pin (so 'no part at all' fails)."""
    pin = E.cylinder(*xy, z0, z1, d)
    ring = E.cylinder(*xy, z0, z1, d + 2 * wall + 0.4) - E.cylinder(*xy, z0 - 1, z1 + 1, d + 0.4)
    inside, around = overlap(part, pin), overlap(part, ring)
    return inside < EPS and around > EPS, f"{inside:.3f} mm3 in the bore, {around:.1f} mm3 round it"


# name -> (points, pin diameter, [(part name pattern, z0, z1)])
EXTRA_BOLTS: dict[str, tuple[list, float, list]] = {}  # bolt axes a sibling design adds, same form as bolts()


def bolts() -> dict[str, tuple[list, float, list]]:
    """name -> (axes, pin diameter, [(part name pattern, z0, z1)]): every layer each bolt has to pass."""
    zb, za, zm, zd, zt, zr = P.Z_BOTTOM, P.Z_ARM, P.Z_MID, P.Z_DECK, P.Z_TOP, P.Z_ROOF
    arm = ("arm_{q}", za, zm)
    bottom, mid, top = ("plate_bottom", zb, za), ("plate_mid", zm, zd), ("plate_top", zt, zr)
    bay = [bottom, mid, top] if P.BAY_ON_DECK else [bottom, top]
    out = {
        "stack": (P.quad(P.S), 3.0, [bottom, arm, mid]),
        "arm_inner": (P.quad(P.B), 3.0, [bottom, arm, mid, top]),
        "arm_outer": (P.quad(P.C), 3.0, [bottom, arm, mid]),
        "front_standoff": (P.pair(P.F), 3.0, bay),
        "rear_standoff": (P.pair(P.R), 3.0, bay),
    }
    if P.BRACES:
        out["brace"] = (P.quad(P.LUG), 3.0, [("brace_{side}", P.Z_BRACE, za), arm])
    return {**out, **EXTRA_BOLTS}


def _quadrant(x: float, y: float) -> str:
    return f"{'front' if y > 0 else 'rear'}_{'right' if x > 0 else 'left'}"


def sheet_web(sheet: F.Sheet) -> tuple[float, str]:
    """Narrowest strip of carbon in a flat part: the smallest gap between any two of its boundaries."""
    face = sheet.face()
    wires = [face.outer_wire(), *face.inner_wires()]
    best, where = float("inf"), ""
    for a, b in combinations(wires, 2):
        A, B = a.bounding_box(), b.bounding_box()
        if A.min.X - B.max.X > best or B.min.X - A.max.X > best or A.min.Y - B.max.Y > best or B.min.Y - A.max.Y > best:
            continue
        d = a.distance_to(b)
        if d < best:
            c = b.center()
            best, where = d, f"near ({c.X:.1f}, {c.Y:.1f})"
    return best, where


def sheet_min_radius(sheet: F.Sheet) -> float:
    """Smallest arc in the profile: an inside corner tighter than the cutter cannot be machined."""
    return min((e.radius for e in sheet.face().edges() if e.geom_type.name == "CIRCLE"), default=float("inf"))


def mass() -> dict[str, float]:
    out = {}
    for name, (part, material) in F.build().items():
        out[name] = part.volume * (CARBON_DENSITY if material == F.CARBON else ALUMINIUM_DENSITY)
    return out


def frame_checks() -> list[Row]:
    rows: list[Row] = []
    parts = F.parts()

    wb = hypot(2 * P.MOTOR_X, 2 * P.MOTOR_Y)
    rows.append(("wheelbase", abs(wb - P.WHEELBASE) < 1e-6, f"{wb:.3f} mm"))
    gap_side, gap_fore = 2 * P.MOTOR_X - P.PROP_D, 2 * P.MOTOR_Y - P.PROP_D
    rows.append(
        (
            "prop tips clear each other",
            min(gap_side, gap_fore) > 6.0,
            f"{gap_side:.1f} mm side to side, {gap_fore:.1f} mm front to rear",
        )
    )

    for name, part in parts.items():
        solids = len(part.solids())
        rows.append(
            (f"{name}: one valid solid", solids == 1 and part.is_valid, f"{solids} solid(s), {part.volume:.0f} mm3")
        )

    hits = [(a, b, round(v, 3)) for (a, pa), (b, pb) in combinations(parts.items(), 2) if (v := overlap(pa, pb)) > EPS]
    rows.append(("no two frame parts overlap", not hits, str(hits or "none")))

    for name, (points, d, layers) in bolts().items():
        bad = []
        for x, y in points:
            for pattern, z0, z1 in layers:
                target = pattern.format(q=_quadrant(x, y), side="right" if x > 0 else "left")
                ok, detail = bore_clear(parts[target], (x, y), d, z0 + 0.01, z1 - 0.01)
                if not ok:
                    bad.append(f"{target} at ({x:.2f}, {y:.2f}): {detail}")
        rows.append(
            (
                f"{name} bolts pass every layer ({len(points)} axes)",
                not bad,
                "; ".join(bad) or "all bores open and walled",
            )
        )

    for name, (x, y, z0, h) in P.STANDOFFS.items():
        below = "plate_mid" if abs(z0 - P.Z_DECK) < 1e-9 else "plate_bottom"
        seat = bore_clear(parts[below], (x, y), 3.0, z0 - 1.5, z0 - 0.01, wall=(P.STANDOFF_OD - 3.4) / 2)
        roof = bore_clear(
            parts["plate_top"], (x, y), 3.0, P.Z_TOP + 0.01, P.Z_ROOF - 0.01, wall=(P.STANDOFF_OD - 3.4) / 2
        )
        rows.append(
            (
                f"{name} fully seated on {below} and under plate_top",
                seat[0] and roof[0] and abs(z0 + h - P.Z_TOP) < 1e-9,
                f"Z {z0}-{z0 + h}",
            )
        )

    body = {n: p for n, p in parts.items() if not n.startswith(("arm_", "brace_"))}
    for motor, xy in P.MOTORS.items():
        disc = E.prop_keepout(xy)
        inside = {n: round(v, 2) for n, p in body.items() if (v := overlap(p, disc)) > EPS}
        rows.append(
            (f"prop {motor}: body stays {P.PROP_MARGIN} mm outside the disc", not inside, str(inside or "clear"))
        )

    gear = E.build()
    cam = E.camera_sweep()
    probes = {
        "esc": gear["esc"][0],
        "fc": gear["fc"][0],
        "vtx 20x20": gear["vtx"][0],
        "vtx 30.5": E._slab(E.VTX_LARGE_SIZE, E.VTX_Z, (0.0, P.VTX_BAY_Y)),
        f"camera {E.CAM_TILT_RANGE[0]:.0f}-{E.CAM_TILT_RANGE[1]:.0f} deg": cam,
        "camera mini": E.camera_sweep(E.CAM_MINI),
        "battery": gear["battery"][0],
    }
    for label, probe in probes.items():
        inside = {n: round(v, 2) for n, p in parts.items() if (v := overlap(p, probe)) > EPS}
        rows.append((f"{label} fits", not inside, str(inside or "clear")))

    for name, make in F.SHEETS.items():
        web, where = sheet_web(make())
        rows.append((f"{name}: carbon webs >= {MIN_WEB} mm", web >= MIN_WEB, f"narrowest {web:.2f} mm {where}"))
        radius = sheet_min_radius(make())
        rows.append(
            (
                f"{name}: no corner tighter than R{MIN_RADIUS:g}",
                radius >= MIN_RADIUS - 1e-6,
                f"smallest arc R{radius:.2f}",
            )
        )

    m = mass()
    carbon = sum(v for n, v in m.items() if not n.startswith("standoff"))
    rows.append(
        (
            f"frame mass under {design.MASS_LIMIT:g} g",
            carbon < design.MASS_LIMIT,
            f"{carbon:.1f} g carbon + {sum(m.values()) - carbon:.1f} g standoffs",
        )
    )
    return rows


def report(rows: list[Row]) -> bool:
    for name, ok, detail in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    failed = sum(1 for r in rows if not r[1])
    print(f"{len(rows) - failed}/{len(rows)} checks passed")
    return failed == 0
