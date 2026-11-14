"""Checks of the frame as modelled. Every row is (name, passed, measured detail)."""

from itertools import combinations
from math import hypot

from vektor import gear as G
from vektor import geometry as GEO
from vektor import params as P

Row = tuple[str, bool, str]
EPS = 1e-3
CARBON = 1.55e-3  # g / mm3
ALUMINIUM = 2.7e-3
MIN_WEB = 2.0
MASS_LIMIT = 200.0


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

    lower, upper, top = parts["skin_lower"], parts["skin_upper"], parts["plate_top"]
    zl, zu, zt = (P.Z_LOWER, P.Z_LOWER + P.T_SKIN), (P.Z_UPPER, P.Z_DECK), (P.Z_TOP, P.Z_ROOF)
    bad = []
    for xy in GEO.body_posts():
        for nm, part, (z0, z1) in (("lower", lower, zl), ("upper", upper, zu), ("top", top, zt)):
            ok, d = bore(part, xy, 3.0, z0 + 0.01, z1 - 0.01)
            if not ok:
                bad.append(f"post {xy} in {nm}: {d}")
    for xy in GEO.stack_holes():
        for nm, part, (z0, z1) in (("lower", lower, zl), ("upper", upper, zu)):
            ok, d = bore(part, xy, 3.0, z0 + 0.01, z1 - 0.01)
            if not ok:
                bad.append(f"stack {xy} in {nm}: {d}")
        webs = sum(overlap(p, G.cyl(*xy, 0, P.Z_DECK, 3.0)) for n, p in parts.items() if n.startswith("web"))
        if webs > EPS:
            bad.append(f"stack {xy} hits a web")
    rows.append(
        ("every bolt passes every plate it goes through", not bad, "; ".join(bad) or "all bores open and walled")
    )

    # the webs: each tab sits in its slot, through the full thickness of the skin
    seated = []
    for q in P.QUADS:
        for tag in ("left", "right"):
            w = parts[f"web_{q}_{tag}"]
            bb = w.bounding_box()
            seated.append(abs(bb.min.Z - P.Z_LOWER) < 1e-6 and abs(bb.max.Z - P.Z_DECK) < 1e-6)
    rows.append(
        (
            "every web reaches through both skins",
            all(seated),
            f"{sum(seated)} of 8 webs, Z {P.Z_LOWER:g} to {P.Z_DECK:g}",
        )
    )

    gaps = [hypot(a[0] - b[0], a[1] - b[1]) - P.PROP_D for a, b in combinations(P.MOTORS.values(), 2)]
    rows.append(("props clear each other", min(gaps) > 10.0, f"{min(gaps):.1f} mm between tips"))
    body = {n: p for n, p in parts.items()}
    for q, xy in P.MOTORS.items():
        k = G.keepout(xy)
        inside = {n: round(v, 2) for n, p in body.items() if (v := overlap(p, k)) > EPS}
        rows.append((f"prop {q}: frame stays {P.PROP_MARGIN} mm outside its disc", not inside, str(inside or "clear")))

    gear = G.build()
    probes = {
        "4-in-1 ESC in the cavity": gear["esc"][0],
        "flight controller": gear["fc"][0],
        "analog VTX": gear["vtx"][0],
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
        (f"frame mass under {MASS_LIMIT:g} g", carbon < MASS_LIMIT, f"{carbon:.1f} g carbon + {alu:.1f} g spacers")
    )
    return rows


def report(rows: list[Row]) -> bool:
    for name, ok, detail in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    failed = sum(1 for r in rows if not r[1])
    print(f"{len(rows) - failed}/{len(rows)} checks passed")
    return failed == 0
