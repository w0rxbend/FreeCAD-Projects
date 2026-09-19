"""Anti-slip TPU pack seat on the top plate: grip ribs, relief windows and a proud front stop."""

from math import sqrt

from build123d import Axis, Face, Part, Plane, Pos, Rectangle, Sketch, Vertex, extrude, offset

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks
from tigerbee.profiles import _outer_face, cutouts

NAME = "battery_pad"
TITLE = "Battery pad"
MATERIAL = "TPU95A"
# Seating face down. The catalog's PRINT (0, 0, 1) (grip side on the bed) makes a proud front stop
# geometrically impossible: whatever is highest in frame Z becomes the only bed contact, so the bar
# meant to stop the pack can never stand above the surface the pack lies on. Printing on the flat
# seating face instead gives ~4000 mm² of first-layer contact, needs no bridges, and lets the stop
# be genuinely proud - at the price of the relief collars, which would protrude below the bed plane.
PRINT = {"battery_pad": (0, 0, -1)}
EXCLUSIVE = ()
BATTERY_OK = True  # the pad is what the pack sits on, so it lives inside the BATTERY envelope
NOTES = (
    "Drops onto plate_top between y -80 and 55 and is held by the battery strap and the pack; "
    "the outline is inset 1.0 from the carbon edge and clipped to |x| 22 so it clears the four "
    "arm-root standoff bolt heads (nearest head 1.2 mm) and never fouls a strap wrapping the plate "
    "edge. The twelve windows sit 0.25 mm outside the plate_top reliefs, so the pad never narrows "
    "them: the two rear pairs (y -49.5 and -69) open into the empty tail bay, so a zip tie or a "
    "12 mm strap can loop through pad + plate there and lock the pad down; the six over the FC "
    "stack and the pair at y -30 are drainage and lightening only. Battery straps of 16/20/25 mm "
    "wrap the top-plate side edges (the reliefs themselves pass at most a 16 mm band, and nothing "
    "can loop through the ones above the stack) - the pad is not a strap slot. The front stop bar "
    "stands 3.0 mm above the rib tops at y 51-55, 3 mm behind the gopro_mount / gps_mount base. "
    "The plate_top SMA hole (0, -56.5) is under the pack and unusable with a pad fitted - the tail "
    "SMA seat is the primary one."
)

# --- parameters (mm) ------------------------------------------------------------------------
T = 2.5  # sheet thickness: Z 36.0 (seated on plate_top) .. 38.5
INSET = 1.0  # pad outline = plate_top outline offset inwards by this
X_MAX = 22.0  # and clipped to this half-width: the standoff tabs carry the M3 bolt heads
Y_FRONT, Y_REAR = 55.0, -80.0  # pad ends (plate_top runs to 75 / -82 on the centre line)
RIB_H, RIB_W, RIB_PITCH = 1.5, 1.5, 6.0  # +-45 deg crosshatch: grip fore-aft AND sideways
RIB_MARGIN = 1.2  # solid border kept round the outline and every window
POCKET_D, POCKET_MIN = 2.5, 2.0  # valleys sink 1.0 into the sheet (1.5 left); slivers below this go
STOP = True
STOP_Y0, STOP_H = 51.0, 4.5  # stop bar y 51..55, Z 38.5..43.0 = RIB_H + 3.0 proud of the rib tops
WINDOWS = True
WINDOW_CLEAR = 0.25  # windows are the plate reliefs grown by this, never smaller
HEAD_AXES = ("standoff_front_arm_right", "standoff_front_arm_left",
             "standoff_rear_arm_right", "standoff_rear_arm_left")

Z0 = Z_TOP_TOP  # 36.0: seating face on plate_top

_DEFAULTS = dict(T=T, INSET=INSET, X_MAX=X_MAX, Y_FRONT=Y_FRONT, Y_REAR=Y_REAR, RIB_H=RIB_H,
                 RIB_W=RIB_W, RIB_PITCH=RIB_PITCH, RIB_MARGIN=RIB_MARGIN, POCKET_D=POCKET_D,
                 POCKET_MIN=POCKET_MIN, STOP=STOP, STOP_Y0=STOP_Y0, STOP_H=STOP_H,
                 WINDOWS=WINDOWS, WINDOW_CLEAR=WINDOW_CLEAR)
_BUILT = dict(_DEFAULTS)  # parameters of the last build(), so checks() measures what was built


def _zs(p: dict) -> tuple[float, float, float, float]:
    """Seating face, sheet top, rib top, stop top."""
    return Z0, Z0 + p["T"], Z0 + p["T"] + p["RIB_H"], Z0 + p["T"] + p["STOP_H"]


def _opened(sk: Sketch, t: float = WALL) -> Sketch:
    """Morphological opening: everything thinner than t (the knife edges a straight cut leaves where
    it crosses the curved plate outline) disappears, convex corners keep a t/2 radius. Erosion and
    dilation run per face because OCCT's 2D offset raises instead of returning nothing when a
    fragment vanishes."""
    out = Sketch()
    for face in sk.faces():
        try:
            eroded = offset(face, -t / 2)
        except Exception:  # noqa: BLE001 - fragment thinner than t everywhere
            continue
        for part in eroded.faces() if eroded is not None else []:
            if part.area > 1e-9:
                out += offset(part, t / 2)
    return out


def _reliefs() -> list[Face]:
    """The twelve diagonal plate_top reliefs (kidneys, long slots and the centre slot are elsewhere)."""
    wires = [w for w in cutouts("plate_top")
             if abs(w.bounding_box().center().X) > 1.0 and w.bounding_box().center().Y < 40.0]
    assert len(wires) == 12, f"expected 12 reliefs, got {len(wires)}"
    return [Face(w) for w in wires]


def _outline(p: dict) -> Sketch:
    crop = Pos(0, (p["Y_REAR"] + p["Y_FRONT"]) / 2) * Rectangle(2 * p["X_MAX"], p["Y_FRONT"] - p["Y_REAR"])
    return _opened(offset(_outer_face("plate_top"), -p["INSET"]) & crop)


def _windows(p: dict) -> Sketch:
    return Sketch() + [offset(f, p["WINDOW_CLEAR"]) for f in _reliefs()]


def _sheet_profile(p: dict) -> Sketch:
    sk = _outline(p)
    return sk - _windows(p) if p["WINDOWS"] else sk


def _stop_profile(p: dict, sheet: Sketch) -> Sketch:
    if not p["STOP"]:
        return Sketch()
    band = Pos(0, (p["STOP_Y0"] + p["Y_FRONT"]) / 2) * Rectangle(400, p["Y_FRONT"] - p["STOP_Y0"])
    return _opened(sheet & band)


def _pockets(p: dict, sheet: Sketch) -> Sketch:
    """Valleys of the +-45 deg rib crosshatch. The diamond lattice is clipped to the sheet eroded by
    RIB_MARGIN, so every pocket keeps a full-thickness border of at least that much to the outline,
    to a window and to the stop band - no rib ever ends in a knife edge - while partial cells at the
    rim still get their relief. Fragments below POCKET_MIN are dropped."""
    side, pitch, r2 = p["RIB_PITCH"] - p["RIB_W"], p["RIB_PITCH"], sqrt(2)
    inner = Sketch()
    for f in sheet.faces():
        try:
            eroded = offset(f, -p["RIB_MARGIN"])
        except Exception:  # noqa: BLE001 - nothing of this fragment survives the erosion
            continue
        for g in eroded.faces() if eroded is not None else []:
            if g.area > 1e-9:
                inner += g
    if not inner.faces():
        return Sketch()
    bb = inner.bounding_box()
    y_max = (p["STOP_Y0"] - p["RIB_MARGIN"]) if p["STOP"] else bb.max.Y + 1
    inner &= Pos(0, (bb.min.Y - 5 + y_max) / 2) * Rectangle(400, y_max - bb.min.Y + 5)
    diamond = Rectangle(side, side).rotate(Axis.Z, 45)
    # lattice in the rib frame u = (x+y)/sqrt2, v = (x-y)/sqrt2; a cell there is a diamond in XY
    n = int((bb.size.X + bb.size.Y) / r2 / pitch) + 2
    grid = Sketch()
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = (i + 0.5) * pitch, (j + 0.5) * pitch
            x, y = (u + v) / r2, (u - v) / r2
            if bb.min.X - pitch <= x <= bb.max.X + pitch and bb.min.Y - pitch <= y <= y_max + pitch:
                grid += Pos(x, y) * diamond
    cut = grid & inner
    return Sketch() + [f for f in cut.faces() if f.area >= p["POCKET_MIN"]]


def build(**overrides) -> dict[str, Part]:
    p = {**_DEFAULTS, **overrides}
    assert p["T"] + p["RIB_H"] - p["POCKET_D"] >= WALL, "pocket floor thinner than the minimum wall"
    assert not p["STOP"] or p["STOP_H"] >= p["RIB_H"] + 2.0, "front stop not proud of the rib tops"
    _BUILT.clear()
    _BUILT.update(p)
    z0, _z1, z2, z3 = _zs(p)
    sheet = _sheet_profile(p)
    stop = _stop_profile(p, sheet)
    pockets = _pockets(p, sheet)

    # Subtractive throughout: fusing a bar onto a slab welds coincident faces into trimmed surfaces
    # that _common.overhangs can no longer read.
    pad = extrude(Plane.XY.offset(z0) * sheet, amount=z3 - z0, dir=(0, 0, 1))
    above = Rectangle(400, 400) - stop if stop.area > 1e-6 else Rectangle(400, 400)
    pad -= extrude(Plane.XY.offset(z2) * above, amount=z3 - z2 + 1, dir=(0, 0, 1))
    if pockets.area > 1e-6:
        pad -= extrude(Plane.XY.offset(z2 - p["POCKET_D"]) * pockets, amount=p["POCKET_D"] + 1, dir=(0, 0, 1))

    pad.label = NAME
    return {NAME: pad}


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    pad, p = parts[NAME], dict(_BUILT)
    z0, _z1, z2, z3 = _zs(p)
    sheet = _sheet_profile(p)
    area = sheet.area
    out = []

    hits = interference(pad)
    out.append(("no interference with the frame", not hits, f"{hits or 'none'}"))

    # the collars of the catalog are gone (see PRINT), so the equivalent check is that the pad stays
    # out of every relief instead of hanging into it: the windows may never narrow a plate aperture
    probes = [extrude(Plane.XY.offset(Z_TOP_UNDER) * f, amount=z3 - Z_TOP_UNDER, dir=(0, 0, 1))
              for f in _reliefs()]
    gaps = [round(pad.distance_to(q), 4) for q in probes]
    vols = [isect(pad, q) for q in probes]
    out.append(("every window clears its plate_top relief (>= 0.2 mm, no overlap)",
                not p["WINDOWS"] or (min(gaps) >= 0.2 - 1e-6 and max(vols) < EPS),
                f"gap {min(gaps)}..{max(gaps)} mm, max overlap {max(vols):.4f} mm³"
                if p["WINDOWS"] else "WINDOWS=False, the reliefs are covered"))

    head = max(isect(pad, cylinder(*STANDOFF_XY[n], z0, z0 + H_M3_HEAD, D_M3_HEAD)) for n in HEAD_AXES)
    head_gap = min(pad.distance_to(cylinder(*STANDOFF_XY[n], z0, z0 + H_M3_HEAD, D_M3_HEAD)) for n in HEAD_AXES)
    out.append((f"clears the four Ø{D_M3_HEAD} x {H_M3_HEAD} standoff bolt heads",
                head < EPS and head_gap >= 0.5, f"{head:.4f} mm³, nearest head {head_gap:.3f} mm"))

    contact = seated(pad, z0)
    out.append(("seated on plate_top at Z 36.000 over >= 60 % of the pad area",
                contact >= 0.60 * area, f"{contact} mm² of {area:.0f} mm² ({contact / area:.0%})"))

    plate = _outer_face("plate_top")
    wire = sheet.faces()[0].outer_wire()
    pts = [wire.position_at(i / 600) for i in range(600)]
    outside = [(round(q.X, 2), round(q.Y, 2)) for q in pts if not plate.is_inside((q.X, q.Y, 0), 1e-4)]
    rim = plate.outer_wire()
    edge = min(Vertex(q.X, q.Y, 0).distance_to(rim) for q in pts)
    out.append(("every outline sample inside the plate_top outline", not outside,
                f"{len(outside)} of 600 outside {outside[:3]}"))
    out.append(("outline inset >= 0.5 mm from the carbon edge (strap wraps the plate, not the pad)",
                edge >= 0.5 - 1e-6, f"closest {edge:.3f} mm"))

    disc = prop_disc_violation(pad)
    out.append(("outside the prop keep-out discs", disc < EPS, f"{disc:.3f} mm³"))

    front = box(-40, 58, Z_TOP_UNDER, 40, 100, 80)  # gopro_mount / gps_mount both start at y 58
    gap = pad.distance_to(front)
    out.append((">= 2.0 mm to the gopro_mount / gps_mount footprint (y >= 58)", gap >= 2.0, f"{gap:.3f} mm"))

    def _level(z: float) -> float:
        return sum(f.area for f in pad.faces() if f.geom_type.name == "PLANE"
                   and abs(f.center().Z - z) < 1e-4 and f.normal_at().Z > 0.999)

    ribs = _level(z2)
    out.append((f"rib tops at Z {z2} carry >= 15 % of the pad area (pack seat)",
                ribs >= 0.15 * area, f"{ribs:.0f} mm² of {area:.0f} mm² ({ribs / area:.0%})"))

    proud = z3 - z2
    stop_area = _level(z3)
    out.append(("front stop stands proud of the pack seat by >= 2 mm",
                not p["STOP"] or (proud >= 2.0 and stop_area > 20.0),
                f"stop top Z {z3}, rib tops Z {z2}, {proud:.3f} mm proud over {stop_area:.0f} mm²"
                if p["STOP"] else "STOP=False, no bar built"))

    over = overhangs(pad, PRINT[NAME], material=MATERIAL)
    out.append(("printable seating-face-down without bridges or supports", not over, "; ".join(over) or "none"))

    ok_solid, detail = single_solid(pad)
    out.append(("one solid", ok_solid and len(pad.solids()) == 1, detail))

    # The sheet is prismatic, so its wall thicknesses are a 2D property; measure the profile rims and
    # confirm with the 3D heuristic on the sheet alone (the rib crosshatch would dominate otherwise).
    face = sheet.faces()[0]
    rims = [face.outer_wire(), *face.inner_wires()]
    walls = [round(min(a.distance_to(b) for j, b in enumerate(rims) if j != i), 3)
             for i, a in enumerate(rims[1:], start=1)]
    want = 12 if p["WINDOWS"] else 0
    out.append((f"min wall >= {WALL} from every window to the next window or the edge",
                len(walls) == want and (not walls or min(walls) >= WALL - 1e-6),
                f"{min(walls) if walls else 'n/a'} mm over {len(walls)} windows"))
    ok_mw, resid, detail = min_wall(extrude(Plane.XY.offset(z0) * sheet, amount=p["T"], dir=(0, 0, 1)), WALL)
    out.append((f"sheet has no feature thinner than {WALL} mm", ok_mw, f"{detail} (residual {resid} mm³)"))

    floor = p["T"] + p["RIB_H"] - p["POCKET_D"]
    thin = sum(f.area for f in pad.faces() if f.geom_type.name == "PLANE"
               and abs(f.center().Z - (z2 - p["POCKET_D"])) < 1e-4 and f.normal_at().Z > 0.999)
    out.append((f"grip pockets leave >= {WALL} mm of sheet over the seating face",
                floor >= WALL - 1e-6 and thin > 0, f"{floor:.3f} mm floor over {thin:.0f} mm² of pockets"))
    return out
