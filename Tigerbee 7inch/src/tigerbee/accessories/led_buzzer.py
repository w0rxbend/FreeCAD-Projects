"""Rear underside bar: buzzer cup, rear-facing WS2812 strip in a closed groove, rear landing pad."""

from build123d import Axis, GeomType, Part, Plane, Polygon, Pos, Rectangle, extrude, fillet

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "led_buzzer"
TITLE = "LED / buzzer bar"
MATERIAL = "TPU95A"
PRINT = {"led_buzzer": (0, 0, -1)}
MOUNTS = ("plate_bottom underside Z 0 (the seating face bears on it)",
          "the (0, -83.5) strap slot - a 10.3 x 7.1 x 1.8 nub keys X, Y and yaw",
          "rear_30p5_row bolt axes (±15.25, -81), screwed down from the plate top face")
HARDWARE = ("2 x M3 x 8 self-tappers down through rear_30p5_row (heads on the plate top face, "
            "Z 2-3.65); build(SCREWS=False) turns the two holes into a zip-tie path instead",)
EXCLUSIVE = ()

# --- parameters (mm) ------------------------------------------------------------------------
BEEPER = "tmb12"  # "tmb12" (Ø12 x 9.5 active buzzer) | "vifly" (24 x 13 x 16 lost-model beeper)
BEEPERS = ("tmb12", "vifly")  # every documented variant; checks() runs over all of them
LED_LEN = 36.0  # strip length; the groove runs the full width, so this is a check datum only
SCREWS = True

Y_FRONT, Y_REAR, Y_FULL = -69.0, -88.0, -79.0  # plan: ±16 at the front, widening to ±20 by y -79
HALF_X, HALF_X_FRONT = 20.0, 16.0
R_CORNER, R_TAPER = 3.0, 2.0

CUP_XY, CUP_D, CUP_H = (0.0, -77.5), 12.3, 9.5
VIFLY = (24.5, 13.5, 16.5)

# LED groove: a CLOSED 10.4 x 2.5 channel in the rear face (10 mm WS2812 strip + 0.4), floor
# LED_FLOOR above the bed, roof ROOF below the seating face. It must not break through to the
# seating face: the rear M2 heads of the 25.5 pattern sit at (±12.75, -85.75) right above it.
LED_D, LED_H = 2.5, 10.4
LED_FLOOR = 2.0  # WALL_IMPACT: this floor is also a landing pad, coplanar with motor_guard's feet
LIP_D, LIP_H = 0.6, 0.4  # retaining lip along the bottom of the mouth (snap the strip past it)

RELIEF_D, RELIEF_H = 5.0, 1.4  # clearance pockets for the VTX M2 screw heads (Ø3.8 x 1.3)
RELIEF_W = 4.6  # rear pair: narrower, so 1.3 mm of wall is left to the (±15.25, -81) pilot holes
ROOF = RELIEF_H + 1.4  # 2.8: material over every internal ceiling. The M2 head reliefs cut
# RELIEF_H into the seating face, so this leaves 1.4 mm of wall over the channel and the cavity.
DROP = LED_FLOOR + LED_H + ROOF  # 15.2 - the closed 10.4 groove sets the depth of the bar,
# and with it the airframe's ground plane: _fit.GROUND_Z is this bar's bed, and motor_guard's four
# landing feet derive their DROP from that constant so the quad stands level on all five contacts.
SCREW_DEPTH = 9.0
MIN_Z = -(VIFLY[2] + ROOF)  # -19.3: the vifly cavity makes that variant the deepest build

# Locating nub: the full 10.3 x 7.1 (r1.45) pad in the (0, -83.5) 10.8 x 7.6 strap slot, 0.25 per
# side on all four sides, so it locates the bar laterally AND fore-aft and binds in yaw.
SLOT_XY, SLOT_W, SLOT_L, SLOT_R = (0.0, -83.5), 10.8, 7.6, 1.2
NUB_FIT = 0.25
NUB_W, NUB_L, NUB_R = SLOT_W - 2 * NUB_FIT, SLOT_L - 2 * NUB_FIT, SLOT_R + NUB_FIT
NUB_Y = (SLOT_XY[1] - NUB_L / 2, SLOT_XY[1] + NUB_L / 2)  # (-87.05, -79.95)
NUB_H = 1.8  # 0.2 shy of the plate top face

# 4 x 4 wire and vent window, cavity ceiling -> strap slot. It runs out through the front of the
# nub (WIRE_Y[1] > NUB_Y[1]), which leaves the pad a П (a full-width rear bar plus two arms)
# instead of a 0.05 mm web. min_wall() cannot police that web here, so nub_front_web() sections it
# and the "nub is a П" check enforces WALL - keep WIRE_Y[1] past NUB_Y[1], or a full 1.2 behind it.
# A round Ø4 hole would cross the cup wall at 29 deg and leave two knife edges in the ceiling;
# straight sides cross it at ~70 deg instead.
WIRE_W, WIRE_Y = 4.0, (-84.0, NUB_Y[1] + 0.1)

SCREW_AXES = tuple(sorted(hole_xy("rear_30p5_row")))  # (±15.25, -81)
M2_AXES = tuple(sorted([xy for xy in hole_xy("rear_20") if xy[1] < -70]
                       + [xy for xy in hole_xy("rear_25p5") if xy[1] < -80]))
M2_HEAD_H = 1.3  # the head the reliefs must clear, and the fastener envelope under the plate

Y_LIP = Y_REAR + LIP_D
Y_IN = Y_REAR + LED_D

NOTES = (
    "Seats on the plate_bottom underside; a 10.3 x 7.1 x 1.8 nub locates in the (0, -83.5) strap "
    "slot (0.25 mm per side on all four sides, so it fixes X, Y and yaw) and two M3 x 8 "
    "self-tappers come down through rear_30p5_row (heads on the plate top face, Z 2-3.65, clear of "
    "the tail_block skirts). SCREWS=False leaves the two holes as a zip-tie path; the nub alone "
    f"still locates the bar. The LED groove is closed: {LED_H} x {LED_D} with a {LIP_H} x {LIP_D} "
    f"lip along the bottom of the mouth, its roof {ROOF} mm below the seating face, which is what "
    f"sets DROP to {DROP}. A 12 mm bar cannot hold a 10 mm strip under a roof, and an open channel "
    "would cut the seating face open across the rear M2 pair at (±12.75, -85.75). The groove runs "
    "the full width: the r3 rear corners leave only a 34 mm rear face, so a 36 mm strip cannot "
    "have end walls - stopping it at x ±18 would leave two knife-edge slivers. The 4 x 4 wire "
    "window is the cup's only vent - it opens into the strap slot, the one place the carbon is "
    "open, and the buzzer's leads through it are also what keep the slip-fit buzzer in its cup. "
    "If a VTX is bolted to the 25.5 pattern at (0, -73) with the heads underneath, the four Ø5 x "
    f"{RELIEF_H} reliefs in the seating face take the heads. The bar's underside IS the airframe's "
    f"ground plane (frame Z {-DROP}): motor_guard's four landing feet are built to the same plane, so "
    "the quad rests level on five coplanar contacts instead of on a tail-first tripod. "
    f"BEEPER='vifly' deepens the bar to {VIFLY[2] + ROOF} mm for a 24 x 13 x 16 beeper; both variants "
    f"are checked, but the vifly bar drops {VIFLY[2] + ROOF - DROP} mm below the shipped ground plane, "
    f"so build it with motor_guard(DROP={Z_BOTTOM_TOP + VIFLY[2] + ROOF:.1f}) or the stance tips again."
)


# --- per-variant Z references ---------------------------------------------------------------
def _drop(beeper: str = BEEPER, drop: float = DROP) -> float:
    """Effective depth of the bar: the vifly cavity needs its own height plus ROOF."""
    return drop if beeper != "vifly" else max(drop, VIFLY[2] + ROOF)


def zref(beeper: str = BEEPER, drop: float = DROP) -> dict[str, float]:
    """Every Z datum of one variant. Checks must read these, never the module-level DROP."""
    d = _drop(beeper, drop)
    z_floor = -d + LED_FLOOR
    return {"drop": d, "bed": -d, "floor": z_floor, "ceil": z_floor + LED_H,
            "cavity": -d + (VIFLY[2] if beeper == "vifly" else CUP_H)}


# print frame = frame coordinates shifted by (0, -(Y_FRONT + Y_REAR) / 2, drop); bed normal (0, 0, -1)
_DY = -(Y_FRONT + Y_REAR) / 2


def bridge_boxes(beeper: str = BEEPER, drop: float = DROP) -> tuple:
    """Declared bridges in PRINT coordinates: the groove roof and the beeper-cavity ceiling."""
    z = zref(beeper, drop)
    dz = z["drop"]
    cy = CUP_XY[1] + _DY
    w, h = (VIFLY[0] / 2 + 0.9, VIFLY[1] / 2 + 0.9) if beeper == "vifly" else (7.0, CUP_D / 2 + 0.9)
    return (
        ("box", -(HALF_X + 1.5), Y_REAR - 1.0 + _DY, z["ceil"] - 0.3 + dz,
         HALF_X + 1.5, Y_IN + 1.0 + _DY, z["ceil"] + 0.3 + dz),  # LED groove roof, 2.5 mm span
        ("box", -w, cy - h, z["cavity"] - 0.3 + dz, w, cy + h, z["cavity"] + 0.3 + dz),  # cavity ceiling
    )


BRIDGE_OK = {"led_buzzer": bridge_boxes(BEEPER)}


# --- geometry -------------------------------------------------------------------------------
def _outline():
    pts = [(-HALF_X_FRONT, Y_FRONT), (-HALF_X, Y_FULL), (-HALF_X, Y_REAR),  # CCW: extrudes +Z
           (HALF_X, Y_REAR), (HALF_X, Y_FULL), (HALF_X_FRONT, Y_FRONT)]
    sk = Polygon(*pts, align=None)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_FRONT) < 1e-6), R_CORNER)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_REAR) < 1e-6), R_CORNER)
    return fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_FULL) < 1e-6), R_TAPER)


def channel_tool(zf: float) -> Part:
    """Cutting tool for the LED groove: a (y, z) section extruded along X, right through the bar.

    CLOSED at the top: the roof at zf + LED_H stays ROOF below the seating face, so the groove
    never breaks the seating face open and never reaches the M2 head reliefs or the rear M2
    fastener columns at (±12.75, -85.75). The mouth is narrowed by a lip along its bottom edge,
    thinner than WALL by intent (see lips_tool).
    It runs the full width: the r3 rear corners leave a 34 mm rear face, so a 36 mm strip cannot
    have end walls - stopping the groove at x ±18 would leave two knife-edge slivers instead."""
    pts = [(Y_REAR - 0.5, zf + LIP_H), (Y_LIP, zf + LIP_H), (Y_LIP, zf), (Y_IN, zf),
           (Y_IN, zf + LED_H), (Y_REAR - 0.5, zf + LED_H)]
    return extrude(Plane.YZ * Polygon(*pts, align=None), amount=HALF_X + 1.0, both=True)


def lips_tool(zf: float) -> Part:
    """The intentionally thin 0.4 x 0.6 retaining lip along the bottom of the channel mouth."""
    lx = HALF_X + 0.2
    return box(-lx, Y_REAR - 0.2, zf - 0.05, lx, Y_LIP + 0.05, zf + LIP_H + 0.05)


def _nub() -> Part:
    """One 10.3 x 7.1 r1.45 pad into the (0, -83.5) strap slot: X, Y and yaw location."""
    sk = Pos(SLOT_XY[0], SLOT_XY[1]) * Rectangle(NUB_W, NUB_L)
    # start 0.2 below the seating face so the pad fuses with the bar instead of just touching it
    return extrude(Plane.XY.offset(-0.2) * fillet(sk.vertices(), NUB_R), amount=NUB_H + 0.2)


def build(**overrides) -> dict[str, Part]:
    p = {"BEEPER": BEEPER, "DROP": DROP, "SCREWS": SCREWS, **overrides}
    z = zref(p["BEEPER"], p["DROP"])
    zb = z["bed"]

    bar = extrude(Plane.XY.offset(zb) * _outline(), amount=z["drop"])
    bar -= channel_tool(z["floor"])
    bar += _nub()

    # beeper cavity, opening downward with a flat ceiling ROOF below the seating face
    if p["BEEPER"] == "vifly":
        bar -= box(-VIFLY[0] / 2, CUP_XY[1] - VIFLY[1] / 2, zb - 0.1,
                   VIFLY[0] / 2, CUP_XY[1] + VIFLY[1] / 2, z["cavity"])
    else:
        bar -= cylinder(*CUP_XY, zb - 0.1, z["cavity"], CUP_D)

    # wire and vent window: cavity ceiling -> through the nub into the strap slot (the one place
    # the carbon is open). It clears the front of the nub, leaving no 0.05 mm web there.
    wsk = fillet((Pos(0, sum(WIRE_Y) / 2) * Rectangle(WIRE_W, WIRE_Y[1] - WIRE_Y[0])).vertices(), 0.8)
    bar -= extrude(Plane.XY.offset(z["cavity"]) * wsk, amount=NUB_H + 0.2 - z["cavity"])

    # VTX M2 screw-head reliefs; the rear pair opens through the rear face above the groove roof
    for rx, ry in M2_AXES:
        if ry < -80:
            y_front = ry + D_M2_HEAD / 2  # just clears the Ø4.2 head, keeps wall to the pilot hole
            sk = Pos(rx, (Y_REAR - 0.5 + y_front) / 2) * Rectangle(RELIEF_W, y_front - Y_REAR + 0.5)
            sk = fillet(sk.vertices().filter_by(lambda v: v.Y > ry), 1.5)
            tool = extrude(Plane.XY.offset(-RELIEF_H) * sk, amount=RELIEF_H + 0.1)
        else:
            tool = cylinder(rx, ry, -RELIEF_H, 0.1, RELIEF_D)
        bar -= tool

    for sx, sy in SCREW_AXES:
        if p["SCREWS"]:
            bar -= cylinder(sx, sy, -SCREW_DEPTH, 0.1, D_M3_TAP)
        else:
            bar -= cylinder(sx, sy, zb - 0.1, 0.1, D_M3_THRU)

    return {"led_buzzer": bar}


# --- check helpers --------------------------------------------------------------------------
def _tail_block_clear(heads: Part) -> tuple[bool, str]:
    """M3 head probes on the plate_bottom top face must not hit the tail_block skirts."""
    try:
        from tigerbee.accessories import build_accessory, tail_block  # noqa: PLC0415
        block = next(iter(build_accessory(tail_block).values()))
        v = isect(heads, block)
        return v < EPS, f"{v:.3f} mm³ against tail_block"
    except Exception as exc:  # noqa: BLE001 - tail_block is a sibling module, may be absent
        bb = heads.bounding_box()
        ok = bb.max.X <= 19.75 and bb.min.Y >= -86.0
        return ok, f"tail_block unavailable ({type(exc).__name__}); heads |x| <= {bb.max.X:.2f} (skirt 19.75), " \
                   f"y >= {bb.min.Y:.2f} (skirt -86)"


def _freedom(nub: Part, plate: Part, move, hi: float, tol: float = 0.005) -> float:
    """Largest displacement (mm, or deg for a rotation) of the nub inside the slot before it
    touches the plate. `move(nub, t)` applies the displacement; returns hi when nothing binds."""
    if isect(move(nub, hi), plate) < EPS:
        return hi
    lo = 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if isect(move(nub, mid), plate) < EPS:
            lo = mid
        else:
            hi = mid
    return lo


def nub_front_web(bar: Part, x_pad: float = 0.8) -> tuple[float, float]:
    """Material left between the wire window and the FRONT face of the nub, measured by section.

    A П pad returns (0.0, 0.0): the window runs past NUB_Y[1], so inside the window's own x band
    there is nothing in front of it. Pulling WIRE_Y[1] back behind NUB_Y[1] leaves a membrane
    WIRE_W x (NUB_Y[1] - WIRE_Y[1]) x NUB_H there, and min_wall() cannot see it - erode()/
    offset_3d collapses on this solid, so min_wall permanently degrades to ray_thickness(), whose
    rays run ALONG a 1.8 mm tall web and measure its height, not its thickness (verified: a 0.80
    mm web passes every other check). Hence the direct section probe.
    x_pad keeps the band between the window's r0.8 corner fillets, so the probe reads the
    membrane and never the rounded ends of the window itself.
    Returns (volume mm³, Y thickness mm) of the membrane."""
    x = WIRE_W / 2 - x_pad
    y0 = min(WIRE_Y[1], NUB_Y[1]) - 0.01
    probe = box(-x, y0, 0.05, x, NUB_Y[1] + 0.01, NUB_H - 0.05)
    try:
        web = bar & probe
    except Exception:  # noqa: BLE001 - OCCT can throw on a degenerate contact; nothing there
        return 0.0, 0.0
    v = volume(web)
    return v, 0.0 if v < EPS else web.bounding_box().size.Y


def fastener_columns() -> list[tuple[str, Part]]:
    """Fastener envelope of every plate_bottom hole under the bar, grown by WALL: what the LED
    channel must stay clear of. Under the plate the VTX M2 pattern carries only its Ø4.2 x 1.3
    heads; the two rear_30p5_row axes carry the bar's own M3 x 8, so their column runs the full
    pilot depth."""
    out = []
    for h in HOLES:
        if "plate_bottom" not in h.plates or not (Y_REAR <= h.y <= Y_FRONT) or abs(h.x) > HALF_X + 1:
            continue
        tapped = (h.x, h.y) in SCREW_AXES
        z0, d = (-SCREW_DEPTH, h.d) if tapped else (-(M2_HEAD_H + WALL), D_M2_HEAD)
        out.append((f"{h.name} ({h.x:+.2f}, {h.y:+.2f})",
                    cylinder(h.x, h.y, z0, Z_BOTTOM_TOP, d + 2 * WALL)))
    return out


def _variant_checks(bar: Part, beeper: str, frame: dict[str, Part], plate_local: Part) -> list[tuple[str, bool, str]]:
    """Every check of one BEEPER variant. All Z references come from zref(beeper)."""
    z = zref(beeper)
    tag = f"[{beeper}]"
    out: list[tuple[str, bool, str]] = []

    ok, detail = single_solid(bar)
    out.append((f"{tag} one valid solid", ok, detail))
    hits = interference(bar)
    out.append((f"{tag} no interference with any frame part", not hits, f"overlaps {hits or 'none'}"))

    # --- the locating nub: lateral, fore-aft and yaw ---------------------------------------
    nub = bar & box(-8, -90, 0.001, 8, -76, 4)
    gap = nub.distance_to(frame["plate_bottom"])
    v = isect(nub, frame["plate_bottom"])
    out.append((f"{tag} nub free in the (0, -83.5) slot", v < EPS and gap >= NUB_FIT - 0.05,
                f"{v:.3f} mm³, gap {gap:.3f} mm"))
    lat = _freedom(nub, plate_local, lambda n, t: Pos(t, 0, 0) * n, 3.0)
    fwd = _freedom(nub, plate_local, lambda n, t: Pos(0, t, 0) * n, 3.0)
    aft = _freedom(nub, plate_local, lambda n, t: Pos(0, -t, 0) * n, 3.0)
    lim = NUB_FIT + 0.1
    out.append((f"{tag} nub locates X and Y in the slot within {lim} mm", max(lat, fwd, aft) <= lim,
                f"free ±x {lat:.2f}, +y {fwd:.2f}, -y {aft:.2f} mm"))
    yaw = _freedom(nub, plate_local, lambda n, a: n.rotate(Axis((*SLOT_XY, 0.0), (0, 0, 1)), a), 25.0)
    out.append((f"{tag} nub binds the bar in yaw within 5 deg", yaw <= 5.0,
                f"{yaw:.2f} deg about (0, -83.5)"))

    # --- fasteners and seating --------------------------------------------------------------
    for sx, sy in SCREW_AXES:
        ok, detail = coaxial(bar, (sx, sy), D_M3_TAP, -SCREW_DEPTH + 0.1, -0.05)
        out.append((f"{tag} M3 pilot coaxial with rear_30p5_row ({sx:+.2f}, {sy})", ok, detail))
        vp = isect(bar, cylinder(sx, sy, -8.0, 0.0, 2.5))
        out.append((f"{tag} Ø2.5 x 8 screw probe fits at ({sx:+.2f}, {sy})", vp < EPS, f"{vp:.3f} mm³"))

    contact = seated(bar, 0.0)
    out.append((f"{tag} seated on the plate_bottom underside at Z 0.000", contact >= 300, f"{contact} mm² contact"))

    worst = 0.0
    for mx, my in M2_AXES:
        worst = max(worst, isect(bar, cylinder(mx, my, -M2_HEAD_H, 0.0, 3.8)))
    out.append((f"{tag} Ø3.8 x {M2_HEAD_H} VTX M2 head probes clear", worst < EPS,
                f"worst {worst:.3f} mm³ of {len(M2_AXES)} axes"))

    # --- the beeper cavity -------------------------------------------------------------------
    if beeper == "vifly":
        probe = box(-12.0, CUP_XY[1] - 6.5, z["bed"], 12.0, CUP_XY[1] + 6.5, z["bed"] + 16.0)
        label = "24 x 13 x 16 vifly beeper probe fits in the cavity"
    else:
        probe = cylinder(*CUP_XY, z["bed"], z["bed"] + CUP_H, 12.0)
        label = f"Ø12 x {CUP_H} buzzer probe fits in the cup"
    vb = isect(bar, probe)
    out.append((f"{tag} {label}", vb < EPS, f"{vb:.3f} mm³"))
    return out


def _groove_checks(bar: Part, beeper: str) -> list[tuple[str, bool, str]]:
    """The LED groove is a closed channel: roofed, and clear of every frame fastener column."""
    z = zref(beeper)
    tag = f"[{beeper}]"
    tool = channel_tool(z["floor"])
    out: list[tuple[str, bool, str]] = []

    # 1. nothing of the groove within WALL of the seating face (it used to be cut wide open there)
    v_open = isect(tool, box(-30.0, -95.0, -WALL, 30.0, -60.0, 5.0))
    out.append((f"{tag} LED groove closed: no opening within {WALL} mm of the seating face",
                v_open < EPS, f"{v_open:.3f} mm³ above Z {-WALL}; roof at Z {z['ceil']:.2f}, "
                              f"{-z['ceil']:.2f} mm of material over it"))

    # 2. the roof over the strip is solid material (x ±16.5 stays on the 34 mm flat rear face)
    cap = box(-16.5, Y_REAR, z["ceil"], 16.5, Y_IN, z["ceil"] + 1.0)
    frac = isect(bar, cap) / volume(cap)
    out.append((f"{tag} groove roof solid over the strip", frac >= 0.999, f"{100 * frac:.2f} % material "
                f"in {2 * 16.5} x {LED_D} x 1.0 over Z {z['ceil']:.2f}"))

    # 3. the groove must not cross any frame fastener column under the plate
    worst, worst_name = 0.0, "none"
    for name, col in fastener_columns():
        v = isect(tool, col)
        if v > worst:
            worst, worst_name = v, name
    out.append((f"{tag} groove clear of every frame fastener column (+{WALL} mm wall)", worst < EPS,
                f"worst {worst:.3f} mm³ at {worst_name} of {len(fastener_columns())} columns"))

    # 4. the strip itself: 36 x 2 x 10 in the groove, the mouth lips excepted
    lx = LED_LEN / 2
    strip = box(-lx, Y_REAR, z["floor"], lx, Y_REAR + 2.0, z["floor"] + 10.0)
    vl = isect(bar, strip - lips_tool(z["floor"]))
    out.append((f"{tag} {LED_LEN} x 2 x 10 LED strip fits (lips excepted)", vl < EPS,
                f"{vl:.3f} mm³ outside the lips, strip Z {z['floor']:.2f}-{z['floor'] + 10:.2f}"))
    return out


def _print_checks(bar: Part, beeper: str) -> list[tuple[str, bool, str]]:
    z = zref(beeper)
    tag = f"[{beeper}]"
    bb = bar.bounding_box()
    out = [(f"{tag} lowest point at Z {z['bed']:.1f}", abs(bb.min.Z - z["bed"]) < 1e-6, f"min Z {bb.min.Z:.3f}"),
           (f"{tag} above the declared landing plane Z {MIN_Z}", bb.min.Z >= MIN_Z - 1e-6, f"min Z {bb.min.Z:.3f}")]

    bed = sum(f.area for f in bar.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z - z["bed"]) < 1e-4 and f.normal_at().Z < -0.999)
    out.append((f"{tag} landing pad on the bed plane", bed >= 350, f"{bed:.1f} mm² at Z {z['bed']:.1f}"))

    over = overhangs(bar, PRINT["led_buzzer"], bridge_ok=bridge_boxes(beeper), material=MATERIAL)
    out.append((f"{tag} printable without supports", not over, "; ".join(over) or "none"))

    ok_wall, _resid, detail = min_wall(bar, WALL, allow=(lips_tool(z["floor"]),))
    out.append((f"{tag} min wall >= {WALL} (LED mouth lip allowed)", ok_wall, detail))

    # min_wall() above runs on rays here (offset_3d collapses on this solid) and rays cannot see a
    # membrane across the front of the nub, so section-probe that one region directly: the pad must
    # be the declared П - open in front of the wire window - or carry a full WALL there.
    web_v, web_t = nub_front_web(bar)
    overrun = WIRE_Y[1] - NUB_Y[1]
    out.append((f"{tag} nub is a П: no membrane in front of the wire window",
                web_v < EPS or web_t >= WALL - WALL_TOL,
                f"{web_v:.3f} mm³ / {web_t:.3f} mm thick between the window and the nub front face "
                f"at y {NUB_Y[1]:.2f}; window overruns it by {overrun:+.2f} mm"))
    return out


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    """Runs over BOTH documented beeper variants; the default build is reused for its own."""
    out: list[tuple[str, bool, str]] = []
    plate_local = frame["plate_bottom"] & box(-13.0, -92.0, -0.2, 13.0, -75.0, 2.2)  # slot walls
    for beeper in BEEPERS:
        bar = parts["led_buzzer"] if beeper == BEEPER else build(BEEPER=beeper)["led_buzzer"]
        out += _variant_checks(bar, beeper, frame, plate_local)
        out += _groove_checks(bar, beeper)
        out += _print_checks(bar, beeper)

    # --- the stance: this bar defines the ground plane the landing feet are built to -----------
    shipped = zref(BEEPER)["bed"]
    out.append((f"the shipped bar stands exactly on the airframe ground plane Z {GROUND_Z}",
                abs(shipped - GROUND_Z) < 1e-6,
                f"[{BEEPER}] bed Z {shipped:.2f} vs _fit.GROUND_Z {GROUND_Z}; motor_guard's four feet "
                f"derive DROP from the same constant"))
    vifly_bed = zref("vifly")["bed"]
    req = Z_BOTTOM_TOP - vifly_bed  # motor_guard's foot DROP is measured from the arm underside Z 2
    out.append((f"[vifly] its {shipped - vifly_bed:.1f} mm of extra depth is declared, with the guard "
                f"DROP it needs", f"motor_guard(DROP={req:.1f})" in NOTES,
                f"bed Z {vifly_bed:.2f}, {shipped - vifly_bed:.1f} mm below the shipped plane; NOTES "
                f"names motor_guard(DROP={req:.1f})"))

    heads = cylinder(*SCREW_AXES[0], Z_BOTTOM_TOP, Z_BOTTOM_TOP + H_M3_HEAD, D_M3_HEAD)
    heads += cylinder(*SCREW_AXES[1], Z_BOTTOM_TOP, Z_BOTTOM_TOP + H_M3_HEAD, D_M3_HEAD)
    ok, detail = _tail_block_clear(heads)
    out.append(("M3 heads at Z 2-3.65 clear of the tail_block skirts", ok, detail))
    return out
