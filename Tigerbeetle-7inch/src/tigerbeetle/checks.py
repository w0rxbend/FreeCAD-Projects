"""Checks of the reconstructed frame. Every row is (name, passed, measured detail).

Two kinds: how faithful the reconstruction is to the tracings (it cannot be better than the
pen, so the limits are the pen's), and whether the parts as modelled go together and carry
what they should.
"""

from itertools import combinations
from math import hypot

from zhalo.checks import bore_clear, overlap, report  # noqa: F401 - report is re-exported for the CLI

from tigerbeetle import equipment as E
from tigerbeetle import frame as F
from tigerbeetle import model as M

Row = tuple[str, bool, str]
EPS = 1e-3
CARBON_DENSITY = 1.55e-3
ALUMINIUM_DENSITY = 2.7e-3
MIN_WEB = 1.5  # the real parts have what they have; anything thinner than this is a reconstruction error
LAYERS = {
    "bottom_plate": ("plate_bottom", M.Z_BOTTOM),
    "camera_plate": ("plate_camera", M.Z_CAMERA),
    "top_plate": ("plate_top", M.Z_TOP),
}


def _quad(x: float, y: float) -> str:
    return f"{'front' if y > 0 else 'rear'}_{'right' if x > 0 else 'left'}"


def fidelity() -> list[Row]:
    d = M.data()
    rows = []
    for name, p in d["plates"].items():
        a = p["mirror_agreement"]
        rows.append((f"{name}: traced left and right halves agree", a > 0.94, f"{a:.1%} of the area"))
    a = d["arm"]["tracing_agreement"]
    rows.append(("arm: the two tracings agree", a > 0.92, f"{a:.1%} of the area, second tracing is the other face"))
    worst = max((h.spread, h.group) for p in M.plates().values() for h in p.holes)
    rows.append(
        (
            "a bolt's holes line up across the plates as traced",
            worst[0] < M.SAME_AXIS,
            f"worst {worst[0]:.2f} mm ({worst[1]})",
        )
    )
    for quad, (pl, part) in M.arms().items():
        traced = [h for h in M.arm_local().holes if h.group == "root"]
        placed = [h for h in part.holes if h.group.startswith("root:")]
        res = max(min(hypot(t.x - p.x, t.y - p.y) for p in placed) for t in traced)
        rows.append((f"arm {quad}: traced root holes land on the plates' holes", res < 1.0, f"worst {res:.2f} mm"))
        held = M._root_held(pl, M.arm_local())
        rows.append((f"arm {quad}: root lies between the lower plates", held > 0.5, f"{held:.0%} of its last 40 mm"))
    return rows


def frame_checks() -> list[Row]:
    rows = fidelity()
    parts = F.parts()
    for name, part in parts.items():
        n = len(part.solids())
        rows.append((f"{name}: one valid solid", n == 1 and part.is_valid, f"{n} solid(s), {part.volume:.0f} mm3"))
    hits = [(a, b, round(v, 3)) for (a, pa), (b, pb) in combinations(parts.items(), 2) if (v := overlap(pa, pb)) > EPS]
    rows.append(("no two frame parts overlap", not hits, str(hits or "none")))

    arm_z = (M.Z_ARM, M.Z_ARM + M.T_ARM)
    bad = []
    for g, members in M.bolts().items():
        h = members[0][1]
        for plate, hole in members:
            part, z = LAYERS[plate]
            ok, detail = bore_clear(parts[part], (hole.x, hole.y), hole.d - 0.2, z + 0.01, z + M.T_PLATE - 0.01)
            if not ok:
                bad.append(f"{g} in {part}: {detail}")
        names = {n for n, _ in members}
        if {"bottom_plate", "camera_plate"} <= names:  # the bolt crosses the arm layer
            pin = E.cylinder(h.x, h.y, arm_z[0] + 0.01, arm_z[1] - 0.01, 3.0)
            arm = parts[f"arm_{_quad(h.x, h.y)}"]
            root = any(
                o.group == f"root:{g}" or o.group == f"root:{_mirror(g)}"
                for _q, (_pl, p) in M.arms().items()
                for o in p.holes
            )
            if root:
                ok, detail = bore_clear(arm, (h.x, h.y), 3.0, *arm_z)
                if not ok:
                    bad.append(f"{g} in the arm: {detail}")
            else:
                v = sum(overlap(parts[a], pin) for a in parts if a.startswith("arm_"))
                if v > EPS:
                    bad.append(f"{g} between the plates hits an arm: {v:.2f} mm3")
    rows.append(
        (f"every bolt passes every layer it crosses ({len(M.bolts())} axes)", not bad, "; ".join(bad) or "all open")
    )

    for name, (x, y, z0, h) in F.standoffs().items():
        below = "plate_camera" if abs(z0 - M.Z_CAMERA - M.T_PLATE) < 1e-6 else "plate_bottom"
        zb = M.Z_CAMERA if below == "plate_camera" else M.Z_BOTTOM
        seat = bore_clear(parts[below], (x, y), 3.0, zb + 0.01, zb + M.T_PLATE - 0.01, wall=0.8)
        roof = bore_clear(parts["plate_top"], (x, y), 3.0, M.Z_TOP + 0.01, M.Z_TOP + M.T_PLATE - 0.01, wall=0.8)
        rows.append((f"{name} on {below} and under plate_top", seat[0] and roof[0], f"{h:g} mm, Z {z0:g}-{z0 + h:g}"))

    motors = F.motors()
    gaps = [hypot(a[0] - b[0], a[1] - b[1]) - E.PROP_D for a, b in combinations(motors.values(), 2)]
    diag = hypot(motors["front_right"][0] - motors["rear_left"][0], motors["front_right"][1] - motors["rear_left"][1])
    rows.append(
        (
            "7 inch props clear each other",
            min(gaps) > 2.0,
            f"{min(gaps):.1f} mm at the closest pair; diagonal {diag:.1f} mm",
        )
    )
    body = {n: p for n, p in parts.items() if not n.startswith("arm_")}
    for name, xy in motors.items():
        disc = E.prop_keepout(xy)
        inside = {n: round(v, 2) for n, p in body.items() if (v := overlap(p, disc)) > EPS}
        rows.append(
            (f"prop {name}: body stays {E.PROP_MARGIN} mm outside the disc", not inside, str(inside or "clear"))
        )

    probes = {
        "stack 30.5": E.stack(),
        "VTX 30.5 in the front bay": E.vtx(),
        "camera 19 mm, 15-45 deg": E.camera_sweep(E.CAM_MICRO),
        "battery": E.battery(),
    }
    for label, probe in probes.items():
        inside = {n: round(v, 2) for n, p in parts.items() if (v := overlap(p, probe)) > EPS}
        rows.append((f"{label} fits", not inside, str(inside or "clear")))

    from zhalo.checks import sheet_web  # noqa: F401 - same measurement, different parts

    for name, part in {**M.plates(), "arm": M.arm_local()}.items():
        f = F.face(part if name != "arm" else M.arms()["front_right"][1])
        wires = [f.outer_wire(), *f.inner_wires()]
        web = min(a.distance_to(b) for a, b in combinations(wires, 2))
        rows.append((f"{name}: narrowest carbon web", web >= MIN_WEB, f"{web:.2f} mm"))

    carbon = sum(p.volume * CARBON_DENSITY for n, (p, m) in F.build().items() if m == F.CARBON)
    rows.append(("frame mass as modelled", 120 < carbon < 260, f"{carbon:.1f} g of carbon"))
    return rows


def _mirror(g: str) -> str:
    """The group of the hole mirrored across X = 0 (left arms use the right arm's holes turned over)."""
    for _p, part in M.plates().items():
        for h in part.holes:
            if h.group == g:
                for o in part.holes:
                    if abs(o.x + h.x) < 1e-6 and abs(o.y - h.y) < 1e-6:
                        return o.group
    return g
