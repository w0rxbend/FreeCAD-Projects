"""Rigid PETG mast lifting a 20-22 mm GPS puck above the front of the top plate."""

from build123d import Part, Plane, Polygon, Pos, Rectangle, extrude, fillet, loft

from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "gps_mount"
TITLE = "GPS mast and platform (front)"
MATERIAL = "PETG"
PRINT = {"gps_mount": (0, 0, -1)}
EXCLUSIVE = ("gopro_mount",)
NOTES = (
    "Bridge Z 36-40 on plate_top, two M3 x 8 buttons with nyloc nuts through the Ø4.6 accessory holes "
    "at (±31.3, 63.5). The bridge outline is the plate_top outline inset 1 mm, also held off the prop "
    "keep-out by 0.4 and capped at |x| 35.2, so no PETG stands proud of the carbon (832 mm² of it "
    "bears on the plate). It is 4 mm thick inboard of |x| 21 and steps down to a 1.5 mm bolt-head "
    "seat outboard of that, each wing carrying a rib: the Ø6.6 driver column has to be clear above "
    "Z 37.5, and the plate's tab neck (y 60-68) is too short to carry a 1.5 mm ring round a "
    "counterbore, so the seat is a step that runs the full length of the bridge instead of a pocket "
    "(a pocket wall would graze the outline at y 60 and leave a knife-edge sliver). Mast 10 x 12 at "
    "(0, 66) Z 40-55 on a 45 deg skirt (18 x 12 at the bridge: the gussets), flare to 25 x 25 at "
    "Z 66, platform 25 x 25 x 4 Z 66-70, puck Z 70-83. 1 mm fillets blend the skirt into the bridge "
    "on all four roots. The GPS cable drops the 6 x 8 slot, leaves through the gabled window in the "
    "mast's rear wall and falls through the notch behind it into the plate_top slot at (0, 55.5). "
    "Deviations from the spec, each forced by a check: platform 25 not 24 (a 20x20 M2 hole 2.5 mm "
    "from the edge of a 24 mm platform leaves 1.15 mm of wall); platform 4 thick not 3 (below Z 66 "
    "the flare has tapered in, so an M2 hole deeper than the platform runs out of wall); FLARE_Z 55 "
    "not 59 (a 45.0 deg flare face is exactly on the overhang limit); platform centred y 68, mast 12 "
    "deep centred y 66 (at y 65 with a 25 mm platform the rear corner sits inside the BATTERY box, "
    "which reaches y 55 up to Z 83.5; 12 deep leaves 2 mm of bridge fore and aft for the root "
    "fillets); bridge y 58-74.5 and |x| <= 35.2 rather than 58-72 / 33.5 (an M3 head at x 31.3 is "
    "34.15 wide on its own, and the extra bearing length ahead of the two-bolt hinge line is what "
    "stiffens the mount - the widest point is still 1.5 mm inside the prop keep-out and 3.3 mm "
    "inboard of the plate edge, which itself pokes into that margin). The (0, 68) hole is unused: "
    "the mast stands on it and no driver reaches it through the 6 mm cable slot. Each platform "
    "corner carries both M2 holes (18 x 18 and 20 x 20); at 1.4 mm apart they break into each other, "
    "which leaves each screw about 250 deg of thread-forming arc."
)

# --- parameters (mm) -------------------------------------------------------------------------
BRIDGE_T = 4.0                 # Z 36.0 (seated) .. 40.0
BRIDGE_Y = (58.0, 74.5)        # rear edge 3.0 behind the battery_pad stop; front edge short of the crotch
PLATE_INSET = 1.0              # bridge outline = plate_top outline inset this much
KEEPOUT_MARGIN = 0.4           # ... and never closer than this to the prop keep-out envelope
HALF_X_MAX = 35.2              # ... and never wider than the M3 head (Ø5.7 at x 31.3) plus a 1.05 rim
OUTLINE_STEP = 0.5
OUTLINE_TOL = 0.15             # outline simplification tolerance (fewer, longer segments)
CORNER_R = 2.0

SEAT_T = 1.5                   # bolt-head seat: Z 36 .. 37.5, the most the Ø6.6 driver column allows
STEP_X = 21.0                  # bridge is BRIDGE_T thick inboard of this, SEAT_T outboard
RIB = (27.0, 6.0, 1.5)         # wing rib: outboard end (1 mm clear of the driver column), width, height

MAST = (10.0, 12.0)            # X, Y: 12 deep leaves 2 mm of bridge fore and aft for the root blend
MAST_Y = 66.0                  # mast y 60 .. 72 inside the bridge's y 58 .. 74
MAST_H = 26.0                  # Z 40 .. 66
FLARE_Z = 55.0                 # column up to here, then the flare opens out to the platform
GUSSET = 4.0                   # 45 deg skirt: the mast root is MAST[0] + 2*GUSSET wide at Z 40
PLATFORM = 25.0                # square
PLATFORM_T = 4.0               # Z 66 .. 70
PLAT_Y = 68.0                  # platform/puck centre: 2 mm ahead of the mast to clear the BATTERY box
SLOT = (6.0, 8.0)              # cable slot through mast, flare and platform (2 mm mast walls)
EXIT = (6.0, 3.0, 4.0)         # rear cable window in the mast wall: width, straight height, gable
PATTERNS = (18.0, 20.0)        # M2 screw patterns (GEP-M10 / Matek M10Q)
M2_DEPTH = 3.6                 # blind, inside the platform's vertical wall (below it the flare tapers)
STRAP = (3.0, 2.5, 2.5)        # strap grooves at the platform edge midpoints: width, depth, height
ROOT_R = 1.0
WALL_MIN = 1.5                 # PETG minimum wall
PUCK = (22.5, 22.5, 13.0)

PARAMS = ("BRIDGE_T", "BRIDGE_Y", "PLATE_INSET", "KEEPOUT_MARGIN", "HALF_X_MAX", "OUTLINE_STEP",
          "CORNER_R", "SEAT_T", "STEP_X", "RIB", "MAST", "MAST_Y", "MAST_H", "FLARE_Z", "GUSSET",
          "PLATFORM", "PLATFORM_T", "PLAT_Y", "SLOT", "EXIT", "PATTERNS", "STRAP")

# battery_pad proxy (sheet on plate_top + front stop bar) for the clearance check
_BATTERY_PAD = box(-21, -80, Z_TOP_TOP, 21, 55, Z_TOP_TOP + 2.5) + box(-21, 52, 38.5, 21, 55, 41.5)


def _bolts() -> list[tuple[float, float]]:
    """The two outer top_accessory holes (±31.3, 63.5); the third at (0, 68) is not used."""
    return sorted(sorted(hole_xy("top_accessory"), key=lambda xy: -abs(xy[0]))[:2])


def _levels(p) -> tuple[float, float, float, float]:
    z_bridge = Z_TOP_TOP + p["BRIDGE_T"]
    z_plat = Z_TOP_TOP + p["BRIDGE_T"] + p["MAST_H"]
    return z_bridge, p["FLARE_Z"], z_plat, z_plat + p["PLATFORM_T"]


def _half_x(y: float, p) -> float:
    """Bridge half width at y: the plate_top outline inset, or the prop keep-out, whichever is nearer.
    The plate's own side tabs (±38.5 at y 64) already poke into the keep-out margin, so both bind."""
    spans = [s for s in outline_spans("plate_top", y) if s[1] - s[0] > 1.0]  # drop tangency slivers
    return min(max(s[1] for s in spans) - p["PLATE_INSET"], max_abs_x_at(y) - p["KEEPOUT_MARGIN"],
               p["HALF_X_MAX"])


def _simplify(pts: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Douglas-Peucker: keeps the sampled outline inside `tol` of the plate curve with as few
    segments as possible (short segments would block the corner fillets and the wall check's offset)."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    norm = (dx * dx + dy * dy) ** 0.5 or 1.0
    devs = [abs((x - x0) * dy - (y - y0) * dx) / norm for x, y in pts[1:-1]]
    worst = max(devs)
    if worst <= tol:
        return [pts[0], pts[-1]]
    i = devs.index(worst) + 1
    return _simplify(pts[:i + 1], tol)[:-1] + _simplify(pts[i:], tol)


def _bridge_sketch(p):
    y0, y1 = p["BRIDGE_Y"]
    n = max(2, round((y1 - y0) / p["OUTLINE_STEP"]))
    ys = [y0 + (y1 - y0) * i / n for i in range(n + 1)]
    right = _simplify([(_half_x(y, p), y) for y in ys], OUTLINE_TOL)
    sk = Polygon(*right, *[(-x, y) for x, y in reversed(right)], align=None)
    corners = [v for v in sk.vertices() if abs(v.Y - y0) < 1e-6 or abs(v.Y - y1) < 1e-6]
    rounded = None
    for r in (p["CORNER_R"], 1.0, 0.6):
        try:
            rounded = fillet(corners, r)
            break
        except Exception:  # noqa: BLE001 - shorten the corner radius until the edges are long enough
            continue
    assert rounded is not None, "bridge corner fillet failed"
    return rounded


def _bridge(p) -> Part:
    """4 mm slab inboard of STEP_X, 1.5 mm bolt-head seat outboard of it, one rib per wing.
    The step runs the whole length of the bridge and never meets its outline, so it leaves no
    knife-edge sliver; a counterbore cannot be used here because the plate's tab neck (y 60-68)
    is too short to carry a 1.5 mm ring round the Ø6.6 driver column."""
    z_bridge = _levels(p)[0]
    z_seat = Z_TOP_TOP + p["SEAT_T"]
    y0, y1 = p["BRIDGE_Y"]
    slab = extrude(Plane.XY.offset(Z_TOP_TOP) * _bridge_sketch(p), amount=p["BRIDGE_T"])
    step = box(p["STEP_X"], y0 - 1, z_seat, 60, y1 + 1, z_bridge + 1)
    slab = slab - step - step.mirror(Plane.YZ)
    rx, rw, rh = p["RIB"]
    _bx, by = _bolts()[1]
    rib = extrude(Plane.XZ.offset(-(by - rw / 2)) * Polygon(
        (p["STEP_X"] - 1, z_seat), (rx, z_seat), (rx, z_seat + rh), (p["STEP_X"] - 1, z_bridge),
        align=None), amount=-rw)
    slab = slab + rib + rib.mirror(Plane.YZ)
    corners = [e for e in slab.edges() if abs(e.center().Z - z_seat) < 1e-6
               and abs(abs(e.center().X) - p["STEP_X"]) < 1e-6 and e.length > 2]
    for r in (ROOT_R, 0.6):  # blend the step into the seat; cosmetic if OCCT refuses
        try:
            return Part() + slab.fillet(r, corners)
        except Exception:  # noqa: BLE001
            continue
    return slab


def _bolt_holes(p) -> Part:
    """Ø3.4 through-bores; the M3 button head bears on the 1.5 mm seat and stands below the slab top."""
    tool = Part()
    for x, y in _bolts():
        tool += cylinder(x, y, Z_TOP_TOP - 0.1, Z_TOP_TOP + p["SEAT_T"] + 0.1, D_M3_THRU)
    return tool


def _mast(p) -> Part:
    """Skirt (45 deg root flare in X) + column + flare + platform, as one fused solid."""
    z_bridge, z_flare, z_plat, z_top = _levels(p)
    mw, md, my, g = p["MAST"][0], p["MAST"][1], p["MAST_Y"], p["GUSSET"]
    skirt = extrude(Plane.XZ.offset(-(my - md / 2)) * Polygon(
        (-mw / 2 - g, z_bridge), (mw / 2 + g, z_bridge), (mw / 2, z_bridge + g), (-mw / 2, z_bridge + g),
        align=None), amount=-md)
    column = extrude(Plane.XY.offset(z_bridge) * Pos(0, my) * Rectangle(mw, md), amount=z_flare - z_bridge)
    side, py = p["PLATFORM"], p["PLAT_Y"]
    flare = loft([Plane.XY.offset(z_flare) * Pos(0, my) * Rectangle(mw, md),
                  Plane.XY.offset(z_plat) * Pos(0, py) * Rectangle(side, side)], ruled=True)
    platform = extrude(Plane.XY.offset(z_plat) * Pos(0, py) * Rectangle(side, side), amount=z_top - z_plat)
    return skirt + column + flare + platform


def _cable_cuts(p) -> Part:
    """Vertical slot through mast, flare and platform; a gabled window through the mast's rear wall;
    a notch through the bridge behind it, over the open part of the plate_top slot at (0, 55.5)."""
    z_bridge, _zf, _zp, z_top = _levels(p)
    my, (sw, sd) = p["MAST_Y"], p["SLOT"]
    tool = extrude(Plane.XY.offset(z_bridge) * Pos(0, my) * Rectangle(sw, sd), amount=z_top - z_bridge + 0.1)
    w, h, gable = p["EXIT"]
    y_back = my - p["MAST"][1] / 2
    window = Polygon((-w / 2, z_bridge - 0.1), (w / 2, z_bridge - 0.1), (w / 2, z_bridge + h),
                     (0, z_bridge + h + gable), (-w / 2, z_bridge + h), align=None)
    wall = p["MAST"][1] / 2 - sd / 2  # mast rear wall: from y_back to the slot
    tool += extrude(Plane.XZ.offset(-(y_back - 0.1)) * window, amount=-(wall + 0.2))
    # the notch reaches above the root fillet so no 0.1 mm flake of it is left hanging over the notch
    return tool + box(-w / 2, p["BRIDGE_Y"][0] - 0.1, Z_TOP_TOP - 0.1, w / 2, y_back, z_bridge + ROOT_R + 0.2)


def _platform_cuts(p) -> Part:
    """M2 holes on both patterns, strap grooves at the four edge midpoints."""
    _zb, _zf, z_plat, z_top = _levels(p)
    my, half = p["PLAT_Y"], p["PLATFORM"] / 2
    tool = Part()
    for pitch in p["PATTERNS"]:
        for sx in (1, -1):
            for sy in (1, -1):
                tool += cylinder(sx * pitch / 2, my + sy * pitch / 2, z_top - M2_DEPTH, z_top + 0.1, D_M2_TAP)
    w, d, h = p["STRAP"]
    z0 = z_top - h  # the groove keeps a 1.5 mm floor: below Z 66 the flare has already tapered in
    for sign in (1, -1):
        a, b = sorted((sign * (half - d), sign * (half + 1)))
        tool += box(a, my - w / 2, z0, b, my + w / 2, z_top + 0.1)
        tool += box(-w / 2, my + a, z0, w / 2, my + b, z_top + 0.1)
    return tool


def _root_fillet(part: Part, p) -> Part:
    """1 mm blend all round the mast skirt where it meets the bridge top."""
    z_bridge = _levels(p)[0]
    reach = p["MAST"][0] / 2 + p["GUSSET"] + 0.5
    edges = [e for e in part.edges()
             if abs(e.center().Z - z_bridge) < 1e-6 and abs(e.center().X) < reach
             and abs(e.center().Y - p["MAST_Y"]) < p["MAST"][1] / 2 + 0.5 and e.length > 0.5]
    assert len(edges) >= 4, f"root fillet found {len(edges)} edges"
    for r in (ROOT_R, 0.8, 0.6):
        try:
            return Part() + part.fillet(r, edges)  # .fillet() returns a bare Solid
        except Exception:  # noqa: BLE001 - retry with a smaller radius
            continue
    raise RuntimeError("root fillet failed")


def build(**overrides) -> dict[str, Part]:
    p = {k: globals()[k] for k in PARAMS}
    p.update(overrides)
    mount = _root_fillet(_bridge(p) + _mast(p), p)
    return {"gps_mount": mount - _cable_cuts(p) - _platform_cuts(p) - _bolt_holes(p)}


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    m = parts["gps_mount"]
    p = {k: globals()[k] for k in PARAMS}
    z_bridge, _zf, _zp, z_top = _levels(p)
    z_seat = Z_TOP_TOP + SEAT_T
    out = []

    hits = interference(m)
    out.append(("no frame interference", not hits, str(hits or "none")))

    for x, y in _bolts():
        ok, detail = coaxial(m, (x, y), D_M3_THRU, Z_TOP_TOP + 0.05, z_seat - 0.05)
        out.append((f"bore coaxial with top_accessory ({x:g}, {y:g})", ok, detail))
        v = isect(m, cylinder(x, y, Z_TOP_TOP - 2, z_seat + 2, 3.2))
        out.append((f"M3 Ø3.2 probe clear at ({x:g}, {y:g})", v < EPS, f"{v:.3f} mm³"))
        v = isect(m, cylinder(x, y, z_seat, z_seat + 40, D_M3_HEAD_RECESS))
        out.append((f"driver Ø6.6 column clear above Z {z_seat:g} at ({x:g}, {y:g})", v < EPS, f"{v:.3f} mm³"))
        head = isect(m, cylinder(x, y, Z_TOP_TOP - 0.1, z_seat, D_M3_HEAD) - cylinder(x, y, Z_TOP_TOP - 0.2, z_seat + 0.1, D_M3_THRU))
        out.append((f"head bears on the seat floor at ({x:g}, {y:g})", head > 10.0, f"{head:.1f} mm³ of floor under the head"))

    contact = seated(m, Z_TOP_TOP)
    out.append(("bridge seated on plate_top at Z 36.000", contact >= 800, f"{contact} mm² contact"))
    off = _off_plate_area(m)
    out.append(("bridge underside stays on the carbon", off < 1.0, f"{off:.2f} mm² outboard of the plate outline"))

    xmax = _span(m, 65.0)
    out.append(("|x| <= 36.4 at y 65", xmax <= 36.4, f"max |x| {xmax:.3f}"))
    bb = m.bounding_box()
    ys = [bb.min.Y + 0.02 + 0.25 * i for i in range(int((bb.max.Y - bb.min.Y) * 4))]
    tight = min(((max_abs_x_at(y) - _span(m, y), y) for y in ys), key=lambda t: t[0])
    out.append(("outline inside the prop keep-out envelope (sampled every 0.25 mm)",
                tight[0] >= KEEPOUT_MARGIN - 0.1,
                f"tightest margin {tight[0]:.3f} mm at y {tight[1]:g}; the plate itself is 2 mm further out there"))
    v = prop_disc_violation(m)
    out.append(("prop discs clear", v < EPS, f"{v:.3f} mm³"))

    v = isect(m, BATTERY)
    out.append(("outside the battery envelope", v < EPS, f"{v:.3f} mm³"))
    d = m.distance_to(_BATTERY_PAD)
    out.append(("distance to battery_pad >= 2.0", d >= 2.0, f"{d:.3f} mm"))

    cam = max(isect(m, camera_envelope(21, tilt_deg=a)) for a in (0, 10, 20, 30, 40))
    out.append(("camera envelope 0/10/20/30/40 deg clear", cam < EPS, f"{cam:.3f} mm³"))
    v = isect(m, tilt_sweep(21, 0, 40))
    out.append(("camera tilt sweep clear", v < EPS, f"{v:.3f} mm³"))
    fov = max(isect(m, fov_wedge(a)) for a in (15, 20, 30, 40))
    out.append(("camera FOV wedge 15-40 deg clear", fov < EPS, f"{fov:.3f} mm³"))

    over = overhangs(m, PRINT["gps_mount"], material=MATERIAL)
    out.append(("no unsupported overhangs", not over, "; ".join(over) or "none"))
    down = [f for f in m.faces() if f.geom_type.name == "PLANE" and f.normal_at().Z < -0.999
            and f.center().Z > z_bridge + 1e-6 and f.area > 5.0]
    out.append(("platform underside fully supported (no downward face above Z 40)", not down,
                "; ".join(f"{f.area:.1f} mm² at Z {f.center().Z:.1f}" for f in down) or "none"))

    puck = box(-PUCK[0] / 2, PLAT_Y - PUCK[1] / 2, z_top, PUCK[0] / 2, PLAT_Y + PUCK[1] / 2, z_top + PUCK[2])
    out.append(("puck 22.5 x 22.5 x 13 fits on the platform", isect(m, puck) < EPS and isect(puck, BATTERY) < EPS,
                f"{isect(m, puck):.3f} mm³ vs mount, {isect(puck, BATTERY):.3f} mm³ vs the pack"))
    engage = min(_bore_depth(m, (sx * pitch / 2, PLAT_Y + sy * pitch / 2), z_top)
                 for pitch in PATTERNS for sx in (1, -1) for sy in (1, -1))
    out.append(("every M2 hole is a blind bore (>= 3 mm of thread)", engage >= 3.0, f"shortest {engage:.2f} mm"))

    blends = [f for f in m.faces() if f.geom_type.name in ("CYLINDER", "TORUS")
              and abs(_face_radius(f) - ROOT_R) < 1e-6
              and abs(f.center().X) < MAST[0] / 2 + GUSSET + 1.5
              and abs(f.center().Y - MAST_Y) < MAST[1] / 2 + 1.5]
    out.append(("mast root blended with 1 mm fillets on all four sides", len(blends) >= 4,
                f"{len(blends)} blend face(s)"))

    ok_w, _resid, detail = min_wall(m, WALL_MIN)
    out.append((f"min wall >= {WALL_MIN}", ok_w, detail))
    return out


def _span(part: Part, y: float) -> float:
    """Largest |x| of the part in the 0.01 mm slice at y (0 where the part is absent)."""
    res = part & box(-60, y - 0.005, Z_TOP_TOP - 1, 60, y + 0.005, 90)
    if res is None or not res.faces():
        return 0.0
    bb = res.bounding_box()
    return max(abs(bb.min.X), abs(bb.max.X))


def _off_plate_area(part: Part) -> float:
    """Underside area at Z 36 that hangs outside the plate_top outline (holes do not count)."""
    from tigerbee.profiles import _outer_face
    outline = _outer_face("plate_top")
    outline = Pos(0, 0, Z_TOP_TOP - outline.center().Z) * outline
    total = on = 0.0
    for f in part.faces():
        if f.geom_type.name != "PLANE" or abs(f.center().Z - Z_TOP_TOP) > 1e-6 or f.normal_at().Z > -0.999:
            continue
        total += f.area
        res = f & outline
        on += sum(x.area for x in res.faces()) if res is not None and hasattr(res, "faces") else 0.0
    return round(total - on, 3)


def _face_radius(face) -> float:
    """Radius of a cylindrical or toroidal face (0 when the surface has none)."""
    try:
        surf = face.geom_adaptor()
        return surf.Cylinder().Radius() if face.geom_type.name == "CYLINDER" else surf.Torus().MinorRadius()
    except Exception:  # noqa: BLE001 - trimmed surfaces expose no primitive
        return 0.0


def _bore_depth(part: Part, xy: tuple[float, float], z_top: float) -> float:
    """Depth of the blind Ø1.7 bore at xy measured from the platform top face."""
    res = part & cylinder(*xy, z_top - 30, z_top + 0.1, D_M2_TAP - 0.2)
    if res is None or not res.solids():
        return 0.0
    return round(z_top - res.bounding_box().max.Z, 3)
