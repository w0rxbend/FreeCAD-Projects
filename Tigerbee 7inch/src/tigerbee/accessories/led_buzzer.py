"""Rear underside bar: Ø12 buzzer cup, rear-facing WS2812 strip, rear landing pad."""

from build123d import GeomType, Part, Plane, Polygon, Pos, Rectangle, extrude, fillet

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "led_buzzer"
TITLE = "LED / buzzer bar"
MATERIAL = "TPU95A"
PRINT = {"led_buzzer": (0, 0, -1)}
EXCLUSIVE = ()
MIN_Z = -12.0
NOTES = (
    "Seats on the plate_bottom underside; two pads locate in the (0, -83.5) strap slot and two M3 x 8 "
    "self-tappers come down through rear_30p5_row (heads on the plate top face, Z 2-3.65, clear of the "
    "tail_block skirts). SCREWS=False leaves the two holes as a zip-tie path. The LED channel is open "
    "against the carbon: plate_bottom is its ceiling, so a full 10 mm WS2812 strip fits over a 1.6 mm "
    "landing floor - a 12 mm bar cannot hold 10 mm of strip under a closed shelf. The strip is held by the lip along the bottom of the mouth, by the carbon above and by its own tape; "
    "the groove runs the full width because the r3 rear corners leave only a 34 mm rear face. The 4 x 4 "
    "wire window is the cup's only vent - it opens into the strap slot, the one place the carbon is open, "
    "and the buzzer's leads through it are also what keep the slip-fit buzzer in its cup. If a VTX is "
    "bolted to the 25.5 pattern at (0, -73) with the heads underneath, use countersunk M2 there or keep to "
    "the 20x20 pads: those two heads hang 1.3 mm into the top of the strip channel. BEEPER='vifly' deepens "
    "the bar to 18.5 mm for a 24 x 13 x 16 beeper, 6.5 mm below the landing plane the checks use."
)

# --- parameters (mm) ------------------------------------------------------------------------
BEEPER = "tmb12"  # "tmb12" (Ø12 x 9.5 active buzzer) | "vifly" (24 x 13 x 16 lost-model beeper)
LED_LEN = 36.0
DROP = 12.0
WALL_T = 1.6
SCREWS = True

Y_FRONT, Y_REAR, Y_FULL = -69.0, -88.0, -79.0  # plan: ±16 at the front, widening to ±20 by y -79
HALF_X, HALF_X_FRONT = 20.0, 16.0
R_CORNER, R_TAPER = 3.0, 2.0

CUP_XY, CUP_D, CUP_H = (0.0, -77.5), 12.3, 9.5
VIFLY = (24.5, 13.5, 16.5)

NUB_X_IN, NUB_X_OUT = 2.6, 5.15  # two pads, 0.25 clear of the 10.8 wide slot
NUB_Y0, NUB_Y1 = -85.25, -82.3
NUB_H, NUB_R = 1.8, 1.0

# 4 x 4 wire and vent window, cup ceiling -> strap slot, between the pads. A round Ø4 hole would
# cross the cup wall at 29 deg and leave two knife edges in the 2.5 mm ceiling; straight sides cross
# it at ~70 deg instead.
WIRE_W, WIRE_Y = 4.0, (-84.0, -80.0)

RELIEF_D, RELIEF_H = 5.0, 1.5  # clearance for the VTX M2 screw heads under the plate
RELIEF_W = 4.6  # rear pair: narrower, so 1.3 mm of wall is left to the (±15.25, -81) pilot holes
SCREW_DEPTH = 9.0

LED_D = 2.5  # channel depth into +Y
LED_FLOOR = 1.6  # solid floor between the strip and the landing face
LIP_D, LIP_H = 0.6, 0.4  # retaining lip along the bottom of the mouth (the carbon caps the top)

SCREW_AXES = tuple(sorted(hole_xy("rear_30p5_row")))  # (±15.25, -81)
M2_AXES = tuple(sorted([xy for xy in hole_xy("rear_20") if xy[1] < -70]
                       + [xy for xy in hole_xy("rear_25p5") if xy[1] < -80]))

Y_LIP = Y_REAR + LIP_D
Y_IN = Y_REAR + LED_D
Z_FLOOR = -DROP + LED_FLOOR

# print frame = frame coordinates shifted by (0, -(Y_FRONT + Y_REAR) / 2, DROP); bed normal (0, 0, -1)
_DY, _DZ = -(Y_FRONT + Y_REAR) / 2, DROP
BRIDGE_OK = {"led_buzzer": (
    ("box", -7.0, CUP_XY[1] - CUP_D / 2 - 0.9 + _DY, -DROP + CUP_H - 0.3 + _DZ,
     7.0, CUP_XY[1] + CUP_D / 2 + 0.9 + _DY, -DROP + CUP_H + 0.3 + _DZ),  # buzzer-cup ceiling
)}


def _outline():
    pts = [(-HALF_X_FRONT, Y_FRONT), (-HALF_X, Y_FULL), (-HALF_X, Y_REAR),  # CCW: extrudes +Z
           (HALF_X, Y_REAR), (HALF_X, Y_FULL), (HALF_X_FRONT, Y_FRONT)]
    sk = Polygon(*pts, align=None)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_FRONT) < 1e-6), R_CORNER)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_REAR) < 1e-6), R_CORNER)
    return fillet(sk.vertices().filter_by(lambda v: abs(v.Y - Y_FULL) < 1e-6), R_TAPER)


def _channel(zf: float) -> Part:
    """Cutting tool for the LED groove: a (y, z) section extruded along X, right through the bar.

    The groove is open at the top - plate_bottom closes it and retains the strip - so a 10 mm strip
    fits over a solid floor; a closed shelf would leave 0.6 mm of floor in a 12 mm bar. The mouth is
    narrowed by a lip along its bottom edge, thinner than WALL by intent (see _led_lips).
    It runs the full width: the r3 rear corners leave a 34 mm rear face, so a 36 mm strip cannot
    have end walls - stopping the groove at x ±18 would leave two knife-edge slivers instead."""
    pts = [(Y_REAR - 0.5, zf + LIP_H), (Y_LIP, zf + LIP_H), (Y_LIP, zf), (Y_IN, zf),
           (Y_IN, 1.0), (Y_REAR - 0.5, 1.0)]
    return extrude(Plane.YZ * Polygon(*pts, align=None), amount=HALF_X + 1.0, both=True)


def _nubs() -> Part:
    """Two locating pads into the (0, -83.5) strap slot, clear of the wire hole between them."""
    sk = Pos(0, (NUB_Y0 + NUB_Y1) / 2) * (Rectangle(2 * NUB_X_OUT, NUB_Y1 - NUB_Y0)
                                          - Rectangle(2 * NUB_X_IN, NUB_Y1 - NUB_Y0 + 2))
    # start 0.2 below the seating face so the pads fuse with the bar instead of just touching it
    return extrude(Plane.XY.offset(-0.2) * fillet(sk.vertices(), NUB_R), amount=NUB_H + 0.2)


def _led_lips() -> Part:
    """The intentionally thin 0.4 x 0.6 retaining lip along the bottom of the channel mouth."""
    lx = HALF_X + 0.2
    return box(-lx, Y_REAR - 0.2, Z_FLOOR - 0.05, lx, Y_LIP + 0.05, Z_FLOOR + LIP_H + 0.05)


def build(**overrides) -> dict[str, Part]:
    p = {"BEEPER": BEEPER, "LED_LEN": LED_LEN, "DROP": DROP, "WALL_T": WALL_T, "SCREWS": SCREWS, **overrides}
    drop = p["DROP"] if p["BEEPER"] != "vifly" else max(p["DROP"], VIFLY[2] + p["WALL_T"] + 0.4)
    zb = -drop

    bar = extrude(Plane.XY.offset(zb) * _outline(), amount=drop)
    bar -= _channel(zb + LED_FLOOR)
    bar += _nubs()

    # beeper cavity, opening downward with a flat ceiling
    if p["BEEPER"] == "vifly":
        ceiling = zb + VIFLY[2]
        bar -= box(-VIFLY[0] / 2, CUP_XY[1] - VIFLY[1] / 2, zb - 0.1, VIFLY[0] / 2, CUP_XY[1] + VIFLY[1] / 2, ceiling)
    else:
        ceiling = zb + CUP_H
        bar -= cylinder(*CUP_XY, zb - 0.1, ceiling, CUP_D)

    # wire and vent window: cavity ceiling -> the strap slot (the carbon is solid everywhere else)
    wsk = fillet((Pos(0, sum(WIRE_Y) / 2) * Rectangle(WIRE_W, WIRE_Y[1] - WIRE_Y[0])).vertices(), 0.8)
    bar -= extrude(Plane.XY.offset(ceiling) * wsk, amount=-ceiling + 0.1)

    # VTX M2 screw-head reliefs; the rear pair opens through the rear face into the LED groove
    for rx, ry in M2_AXES:
        if ry < -80:
            y_front = ry + D_M2_HEAD / 2  # just clears the Ø3.8 head, keeps wall to the pilot hole
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


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    bar = parts["led_buzzer"]
    out: list[tuple[str, bool, str]] = []

    hits = interference(bar)
    out.append(("no interference with any frame part", not hits, f"overlaps {hits or 'none'}"))

    nub = bar & box(-8, -90, 0.001, 8, -76, 4)
    gap = nub.distance_to(frame["plate_bottom"])
    v = isect(nub, frame["plate_bottom"])
    out.append(("nubs free in the (0, -83.5) slot", v < EPS and gap >= 0.2, f"{v:.3f} mm³, gap {gap:.3f} mm"))

    for sx, sy in SCREW_AXES:
        ok, detail = coaxial(bar, (sx, sy), D_M3_TAP, -SCREW_DEPTH + 0.1, -0.05)
        out.append((f"M3 pilot coaxial with rear_30p5_row ({sx:+.2f}, {sy})", ok, detail))
        vp = isect(bar, cylinder(sx, sy, -8.0, 0.0, 2.5))
        out.append((f"Ø2.5 x 8 screw probe fits at ({sx:+.2f}, {sy})", vp < EPS, f"{vp:.3f} mm³"))

    contact = seated(bar, 0.0)
    out.append(("seated on the plate_bottom underside at Z 0.000", contact >= 300, f"{contact} mm² contact"))

    worst = 0.0
    for mx, my in M2_AXES:
        worst = max(worst, isect(bar, cylinder(mx, my, -1.3, 0.0, 3.8)))
    out.append(("Ø3.8 x 1.3 VTX M2 head probes clear", worst < EPS, f"worst {worst:.3f} mm³ of 4 axes"))

    heads = cylinder(*SCREW_AXES[0], Z_BOTTOM_TOP, Z_BOTTOM_TOP + H_M3_HEAD, D_M3_HEAD)
    heads += cylinder(*SCREW_AXES[1], Z_BOTTOM_TOP, Z_BOTTOM_TOP + H_M3_HEAD, D_M3_HEAD)
    ok, detail = _tail_block_clear(heads)
    out.append(("M3 heads at Z 2-3.65 clear of the tail_block skirts", ok, detail))

    vb = isect(bar, cylinder(*CUP_XY, -DROP, -DROP + CUP_H, 12.0))
    out.append(("Ø12 x 9.5 buzzer probe fits in the cup", vb < EPS, f"{vb:.3f} mm³"))

    lx = LED_LEN / 2
    strip = box(-lx, Y_REAR, Z_FLOOR, lx, Y_REAR + 2.0, Z_FLOOR + 10.0)
    res = bar & strip
    vl = volume(res - _led_lips()) if res is not None else 0.0
    out.append(("36 x 2 x 10 LED strip fits (lips excepted)", vl < EPS, f"{vl:.3f} mm³ outside the lips"))

    bb = bar.bounding_box()
    out.append((f"lowest point at Z {-DROP}", bb.min.Z >= -DROP - 1e-6, f"min Z {bb.min.Z:.3f}"))

    bed = sum(f.area for f in bar.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z + DROP) < 1e-4 and f.normal_at().Z < -0.999)
    out.append(("landing pad on the bed plane", bed >= 350, f"{bed:.1f} mm² at Z {-DROP}"))

    over = overhangs(bar, PRINT["led_buzzer"], bridge_ok=BRIDGE_OK["led_buzzer"], material=MATERIAL)
    out.append(("printable without supports", not over, "; ".join(over) or "none"))

    ok_wall, _resid, detail = min_wall(bar, WALL, allow=(_led_lips(),))
    out.append((f"min wall >= {WALL} (LED mouth lips allowed)", ok_wall, detail))
    return out
