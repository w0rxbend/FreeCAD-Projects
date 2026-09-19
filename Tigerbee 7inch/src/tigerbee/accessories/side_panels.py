"""FC/ESC side protection panels between plate_mid and plate_top: dirt guard, crash bumper,
vents, USB window and lead notches, clipped onto the two arm-root standoffs of each side."""

from build123d import Axis, Circle, Location, Part, Plane, Pos, Rectangle, Sketch, extrude, fillet

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "side_panels"
TITLE = "FC/ESC side panels"
MATERIAL = "PETG"
PRINT = {"side_panel_right": (0, 0, -1), "side_panel_left": (0, 0, -1)}
EXCLUSIVE = ()
NOTES = ("Hold the panel ~8 mm outboard of its seat and push it INBOARD: both C-clip mouths face -X, "
         "so the standoffs enter from the inboard side and a side impact loads the closed outboard half "
         "of each ring instead of walking the standoffs out through the mouths. The bottom notches pass "
         "over the inner arm-clamp nyloc nuts during that stroke and double as capacitor/XT60 lead exits. "
         "Each web meets its ring on one side of the mouth only, so the opposite lip is a free 200 deg "
         "arc and takes the 0.6 mm snap over ~15 mm of curved beam (front: upper lip; rear: lower lip). "
         "The wall top (33.8) sits 0.2 under the plate_top side tabs, which are the anti-lift stop; the "
         "rear clip stops at Z 21.5 so xt60_holder can take Z 22-33.8. "
         "Deviations from the spec sheet, all measured in checks(): mouths face -X, not +X (the spec's own "
         "INSTALLATION paragraph, its +X nut sweep and the notches all describe an inboard stroke, which a "
         "+X mouth cannot perform); the spec's front neck probe at (24, 29.5) therefore lands in the mouth "
         "throat and is checked as open, with the real neck probed at (24, 27); the clip lips are squared "
         "off to a uniform 1.6 mm instead of tapering to a knife edge on the bore circle, so no min-wall "
         "allowance is needed; vents are slanted 60 deg (45 deg flanks exceed the overhang limit) in a "
         "Z 22-32 band clear of the USB window; the flat USB lintel is declared a bridge.")

# --- parameters (mm) ------------------------------------------------------------------------
WALL_MIN = 1.5                                  # PETG floor; the min-wall threshold
WALL = 1.5 if MATERIAL == "PETG" else 1.6
X_OUT = 23.0                                    # outer face of the wall
X_IN = X_OUT - WALL                             # 21.5, inboard face
Z_BOT = Z_MID_TOP                               # 9.0, seats on the plate_mid top face
Z_TOP_PANEL = 33.8                              # 0.2 under the plate_top tabs
REAR_CLIP_H = 12.5                              # Z 9.0-21.5; Z 22-33.8 belongs to xt60_holder
SNAP = MATERIALS[MATERIAL]["snap"]              # 0.6 PETG / 0.8 TPU
MOUTH = STANDOFF_D - SNAP                       # 5.4 throat over a Ø6 standoff
R_OUT = D_CLIP_BORE / 2 + CLIP_WALL             # 4.85
LIP_Y = MOUTH / 2 + CLIP_WALL                   # 4.3: squared lip flanks, uniform CLIP_WALL thick
MOUTH_REACH = R_OUT + 0.4                       # mouth cut length from the ring centre
WALL_Y = (-29.0, 28.0)                          # the plain wall; the webs carry it further fore/aft
FILLET_2D = 1.0
FILLET_LIP = MOUTH_FILLET                       # 0.45 on every lip tip corner

# Webs: (inboard-side limit, outboard-side limit). Each one runs from the wall to past the ring
# centre and stops flush with the mouth floor/ceiling, so the union leaves no crevice and no web
# material can sit in the throat. The bores and mouths are cut after the union.
FRONT_WEB = (25.0, 30.0)                        # y0, x1  (top edge = front mouth floor)
REAR_WEB = (-26.0, 28.0)                        # y1, x1  (bottom edge = rear mouth ceiling)

NOTCH_H = 8.0                                   # Z 9-17: nut (6.35 across corners x 4) + bolt tip
NOTCHES = ((14.5, 22.0), (-23.5, -16.0))        # y windows over the inner arm-clamp bolts

USB = True
USB_Y, USB_W, USB_H, USB_Z = 0.0, 12.0, 9.0, 17.0   # flat 12 mm lintel: a PETG bridge, not an arch

VENT = True
VENT_W, VENT_L, VENT_ANGLE, VENT_Z = 3.0, 11.0, 60.0, 27.0
VENT_YS = (-22.0, -16.0, -10.0, 10.0, 16.0, 22.0)   # 6 mm pitch -> 2.2 mm ligaments across the slots

INNER_CLAMP_XY = (P.place(*P.root_holes()[1], P.ARM_PLACEMENTS["arm_front_right"]),
                  P.place(*P.root_holes()[1], P.ARM_PLACEMENTS["arm_rear_right"]))
NUT_ACROSS_CORNERS, NUT_H, BOLT_TIP_D, BOLT_TIP_H = 6.35, 4.0, 4.0, 4.0
SLIDE_ON = 6.0                                  # install stroke the nut sweep must stay clear over

_FY_TOP = FRONT_ARM_XY[1] - MOUTH / 2           # 29.131, front mouth floor
_RY_BOT = REAR_ARM_XY[1] + MOUTH / 2            # -30.673, rear mouth ceiling
_NECK_FRONT = (24.0, 27.0)                      # real front neck (the spec point is in the throat)
_NECK_REAR = (23.5, -28.5)

# Downward faces that are bridges between two supported ends, in PRINT coordinates
# (PRINT is (0,0,-1), so print xy = frame xy minus the bbox centre and print z = frame z - 9).
_DX = -(REAR_ARM_XY[0] - R_OUT + FRONT_ARM_XY[0] + R_OUT) / 2
_DY = -(REAR_ARM_XY[1] - R_OUT + FRONT_ARM_XY[1] + R_OUT) / 2
_BRIDGES = (*(("box", -60.0, y0 + _DY - 0.6, NOTCH_H - 0.6, 60.0, y1 + _DY + 0.6, NOTCH_H + 0.6)
              for y0, y1 in NOTCHES),
            ("box", -60.0, USB_Y - USB_W / 2 + _DY - 0.6, USB_Z + USB_H / 2 - Z_BOT - 0.6,
             60.0, USB_Y + USB_W / 2 + _DY + 0.6, USB_Z + USB_H / 2 - Z_BOT + 0.6))
BRIDGE_OK = {"side_panel_right": _BRIDGES, "side_panel_left": _BRIDGES}


# --- 2D helpers -----------------------------------------------------------------------------
def _rect(x0, y0, x1, y1) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _slot(length: float, width: float, angle: float = 0.0) -> Sketch:
    """Stadium of overall `length` x `width`, rotated by `angle` in the sketch plane."""
    straight = length - width
    sk = (Rectangle(straight, width) + Pos(-straight / 2, 0) * Circle(width / 2)
          + Pos(straight / 2, 0) * Circle(width / 2))
    return sk.rotate(Axis.Z, angle) if angle else sk


def _round(sk: Sketch, corners) -> tuple[Sketch, int]:
    """Fillet every listed (x, y, r) that is still a vertex of the profile; corners swallowed by
    a later union are skipped. Returns the count applied so checks() can see one went missing."""
    done = 0
    for cx, cy, r in corners:
        hits = sk.vertices().filter_by(
            lambda v, cx=cx, cy=cy: abs(v.X - cx) < 1e-4 and abs(v.Y - cy) < 1e-4)
        if hits:
            sk = fillet(hits, r)
            done += 1
    return sk, done


def _lip_reach(cx: float) -> float:
    """Inboard end of a clip's squared lips: R_OUT from the axis, but never inboard of the wall."""
    return max(cx - R_OUT, X_IN)


def _plan(p: dict) -> tuple[Sketch, int]:
    """Plan view: wall + both webs + both full clip rings (circle plus a squared lip block on the
    inboard side), then the Ø6.5 bores and the -X mouths. Cutting the rings only after the union
    keeps every bore free of web material; the squared block keeps both lips CLIP_WALL thick
    instead of letting them taper into the bore circle."""
    mouth, lip = p["MOUTH"] / 2, p["MOUTH"] / 2 + CLIP_WALL
    fy_top, ry_bot = FRONT_ARM_XY[1] - mouth, REAR_ARM_XY[1] + mouth
    fx1, ry1, rx1 = FRONT_WEB[1], REAR_WEB[0], REAR_WEB[1]

    sk = (_rect(X_IN, WALL_Y[0], p["X_OUT"], WALL_Y[1])
          + _rect(X_IN, FRONT_WEB[0], fx1, fy_top)
          + _rect(X_IN, ry_bot, rx1, ry1))
    for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY):
        sk += Pos(cx, cy) * Circle(R_OUT) + _rect(_lip_reach(cx), cy - lip, cx, cy + lip)

    # where each web's outboard edge runs into the ring circle
    fy_cross = FRONT_ARM_XY[1] - (R_OUT ** 2 - (fx1 - FRONT_ARM_XY[0]) ** 2) ** 0.5
    ry_cross = REAR_ARM_XY[1] + (R_OUT ** 2 - (rx1 - REAR_ARM_XY[0]) ** 2) ** 0.5
    sk, n = _round(sk, [(p["X_OUT"], FRONT_WEB[0], FILLET_2D), (fx1, FRONT_WEB[0], FILLET_2D),
                        (fx1, fy_cross, FILLET_2D), (X_IN, fy_top, FILLET_2D),
                        (p["X_OUT"], ry1, FILLET_2D), (rx1, ry1, FILLET_2D),
                        (rx1, ry_cross, FILLET_2D),
                        (_lip_reach(FRONT_ARM_XY[0]), FRONT_ARM_XY[1] + lip, FILLET_LIP),
                        (_lip_reach(REAR_ARM_XY[0]), REAR_ARM_XY[1] - lip, FILLET_LIP)])

    for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY):
        sk -= Pos(cx, cy) * Circle(D_CLIP_BORE / 2)
        sk -= _rect(cx - MOUTH_REACH, cy - mouth, cx, cy + mouth)
    sk, n2 = _round(sk, [(_lip_reach(cx), cy + s * mouth, FILLET_LIP)
                         for cx, cy in (FRONT_ARM_XY, REAR_ARM_XY) for s in (1, -1)])
    return sk, n + n2


def _windows(p: dict) -> Sketch | None:
    """Openings cut through the wall, sketched in (frame Y, frame Z) on Plane.YZ."""
    sk = Sketch()
    if p["USB"]:
        y0, y1 = p["USB_Y"] - p["USB_W"] / 2, p["USB_Y"] + p["USB_W"] / 2
        z0, z1 = p["USB_Z"] - p["USB_H"] / 2, p["USB_Z"] + p["USB_H"] / 2
        win = _rect(y0, z0, y1, z1)
        win, _ = _round(win, [(y, z, FILLET_2D) for y in (y0, y1) for z in (z0, z1)])
        sk += win
    for y0, y1 in NOTCHES:
        notch = _rect(y0, Z_BOT - 1.0, y1, Z_BOT + p["NOTCH_H"])
        notch, _ = _round(notch, [(y, Z_BOT + p["NOTCH_H"], FILLET_2D) for y in (y0, y1)])
        sk += notch
    if p["VENT"]:
        sk += [Pos(yc, VENT_Z) * _slot(VENT_L, VENT_W, VENT_ANGLE) for yc in VENT_YS]
    return sk if sk.faces() else None


def _lip_probe(cx: float, cy: float, side: int, z0: float, z1: float) -> Part:
    """Slab occupying one snap lip's full CLIP_WALL cross-section, clear of the bore. Solid
    everywhere = the lip is a parallel 1.6 mm slab, not a wedge tapering onto the bore circle."""
    y0 = cy + side * MOUTH / 2
    return box(_lip_reach(cx) + 0.5, min(y0, y0 + side * CLIP_WALL), z0,
               cx - 2.6, max(y0, y0 + side * CLIP_WALL), z1)


def build(**overrides) -> dict[str, Part]:
    p = dict(WALL=WALL, X_OUT=X_OUT, MOUTH=MOUTH, Z_TOP_PANEL=Z_TOP_PANEL, REAR_CLIP_H=REAR_CLIP_H,
             NOTCH_H=NOTCH_H, USB=USB, USB_Y=USB_Y, USB_W=USB_W, USB_H=USB_H, USB_Z=USB_Z, VENT=VENT)
    p.update(overrides)
    z_rear = Z_BOT + p["REAR_CLIP_H"]

    plan, _ = _plan(p)
    panel = extrude(Plane.XY.offset(Z_BOT) * plan, amount=p["Z_TOP_PANEL"] - Z_BOT)
    # The rear clip ends at Z 21.5; above it only the plain wall may reach back to y -29.
    # The second cut clears REAR_WEB's root fillet as well, or its tapering wedge would survive
    # above the clip as a knife edge along y -26.
    panel -= box(X_IN - 5, -60, z_rear, 45, WALL_Y[0], p["Z_TOP_PANEL"] + 1)
    panel -= box(p["X_OUT"], -60, z_rear, 45, REAR_WEB[0] + FILLET_2D, p["Z_TOP_PANEL"] + 1)

    win = _windows(p)
    if win is not None:
        panel -= extrude(Plane.YZ.offset(X_IN - 1) * win, amount=p["WALL"] + 2)
    return pair(panel, "side_panel")


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    right, left = parts["side_panel_right"], parts["side_panel_left"]
    z_rear = Z_BOT + REAR_CLIP_H
    bb = right.bounding_box()
    out = []

    hits = interference(right)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    out.append(("one solid", len(right.solids()) == 1, f"{len(right.solids())} solid(s)"))

    for name, (px, py), h in (("front", _NECK_FRONT, 24.0), ("rear", _NECK_REAR, 12.5)):
        probe = box(px - 0.5, py - 0.5, Z_BOT, px + 0.5, py + 0.5, Z_BOT + h)
        v = isect(right, probe)
        out.append((f"{name} neck fully solid at ({px}, {py})", abs(v - h) < 1e-3, f"{v:.4f} of {h} mm³"))
    # The spec's front neck probe sits at (24, 29.5) - with -X mouths that point is the insertion
    # channel, so it is checked open rather than solid, over the whole channel and clip height.
    for side, (cx, cy), z1 in (("front", FRONT_ARM_XY, Z_TOP_PANEL), ("rear", REAR_ARM_XY, z_rear)):
        chan = box(X_IN - 8, cy - MOUTH / 2 + 0.05, Z_BOT, cx, cy + MOUTH / 2 - 0.05, z1)
        v = isect(right, chan)
        out.append((f"{side} standoff insertion channel clear to the mouth", v < EPS, f"{v:.4f} mm³"))

    for side, xy, span in (("front", FRONT_ARM_XY, (Z_BOT + 0.2, Z_TOP_PANEL - 0.2)),
                           ("rear", REAR_ARM_XY, (Z_BOT + 0.2, z_rear - 0.2))):
        for hand, part, cx in (("right", right, xy[0]), ("left", left, -xy[0])):
            ok, detail = coaxial(part, (cx, xy[1]), D_CLIP_BORE, *span)
            out.append((f"{side} bore coaxial with standoff_{side}_arm_{hand}", ok, detail))

    cyls = standoff_cylinders()
    for nm in ("standoff_front_arm_right", "standoff_rear_arm_right"):
        d = right.distance_to(cyls[nm])
        out.append((f"gap to the Ø{STANDOFF_D} {nm}", abs(d - STANDOFF_FIT) <= 0.05, f"{d:.4f} mm"))

    probes = None
    for cx, cy in INNER_CLAMP_XY:
        nut = hex_pocket(NUT_ACROSS_CORNERS * cos(radians(30)), NUT_H, (cx, cy, Z_BOT))
        tip = cylinder(cx, cy, Z_BOT + NUT_H, Z_BOT + NUT_H + BOLT_TIP_H, BOLT_TIP_D)
        probes = nut + tip if probes is None else probes + nut + tip
    worst, worst_dx = 0.0, 0.0
    for step in range(int(SLIDE_ON / 0.5) + 1):
        dx = step * 0.5
        v = isect(right if dx == 0 else right.moved(Location((dx, 0, 0))), probes)
        if v > worst:
            worst, worst_dx = v, dx
    out.append((f"inner arm-clamp nuts clear over the {SLIDE_ON} mm slide-on", worst < EPS,
                f"max {worst:.4f} mm³ at +{worst_dx:.1f} mm"))

    # Nothing but the two standoffs may be in the way while the panel is pushed inboard; the
    # standoff overlap that does appear is the snap itself and must come back to zero when seated.
    rigid = {n: pt for n, pt in frame.items() if not n.startswith("standoff")}
    blocked, snap_peak = [], 0.0
    for step in range(int(SLIDE_ON / 0.5) + 1):
        moved = right if step == 0 else right.moved(Location((step * 0.5, 0, 0)))
        blocked += [(step * 0.5, *h) for h in interference(moved, against=rigid)]
        snap_peak = max(snap_peak, sum(v for _n, v in standoff_interference(moved)))
    out.append((f"slide-on path clear of the plates and arms over {SLIDE_ON} mm", not blocked,
                f"{blocked or 'none'}; snap interference peaks at {snap_peak:.1f} mm³ and is 0 when seated"))

    contact = seated(right, Z_BOT)
    out.append(("wall bottom seated at Z 9.000", abs(bb.min.Z - Z_BOT) < 1e-6,
                f"min Z {bb.min.Z:.4f}, {contact} mm² on plate_mid"))
    bed = sum(f.area for f in right.faces() if f.geom_type == GeomType.PLANE
              and abs(f.center().Z - Z_BOT) < 1e-4 and abs(f.normal_at().Z) > 0.999)
    out.append(("bed-plane faces >= 90 mm²", bed >= 90.0, f"{bed:.1f} mm²"))
    out.append((f"max Z <= {Z_TOP_PANEL}", bb.max.Z <= Z_TOP_PANEL + 1e-6, f"max Z {bb.max.Z:.3f}"))
    out.append(("inboard faces >= 21.2", bb.min.X >= 21.2 - 1e-6, f"min X {bb.min.X:.3f}"))
    out.append(("envelope x <= 33.4, y -38.2..36.7", bb.max.X <= 33.4 and bb.min.Y >= -38.25
                and bb.max.Y <= 36.7, f"x {bb.min.X:.3f}..{bb.max.X:.3f}, y {bb.min.Y:.3f}..{bb.max.Y:.3f}"))

    v = isect(right, box(-20, -20, Z_BOT, 20, 20, Z_BOT + 25))
    out.append(("clear of the 40 x 40 x 25 FC/ESC envelope", v < EPS, f"{v:.3f} mm³"))
    v = prop_disc_violation(right)
    out.append(("outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))

    over = overhangs(right, PRINT["side_panel_right"], bridge_ok=BRIDGE_OK["side_panel_right"],
                     material=MATERIAL)
    out.append(("no unsupported overhangs (notch and USB lintels bridged)", not over,
                "; ".join(over) or "none"))

    ok, _residual, detail = min_wall(right, WALL_MIN)
    out.append((f"min wall >= {WALL_MIN}", ok, detail))
    # min_wall's ray fallback cannot see a tapering tip, so measure the four lips directly.
    worst_lip, lips = 1.0, []
    for (cx, cy), z1 in ((FRONT_ARM_XY, Z_TOP_PANEL), (REAR_ARM_XY, z_rear)):
        for side in (1, -1):
            probe = _lip_probe(cx, cy, side, Z_BOT + 0.05, z1 - 0.05)
            frac = isect(right, probe) / probe.volume
            worst_lip = min(worst_lip, frac)
            lips.append(f"{frac:.4f}")
    out.append((f"snap lips a full {CLIP_WALL} mm slab (no tapering tip)", worst_lip > 1 - 1e-4,
                f"solid fractions {', '.join(lips)}"))

    # 9 structural corners + 3 lip tips; the front lower lip has no tip (the web's top face is the
    # mouth floor there), so 12 is the full set.
    _, filleted = _plan(dict(WALL=WALL, X_OUT=X_OUT, MOUTH=MOUTH))
    out.append(("every plan corner filleted", filleted == 12, f"{filleted} of 12 corners"))

    out.append(("volume 2.5-5.5 cm³", 2500.0 <= right.volume <= 5500.0, f"{right.volume / 1000:.3f} cm³"))
    out.append(("left mirror has the same volume", abs(left.volume - right.volume) < 0.01,
                f"Δ {abs(left.volume - right.volume):.6f} mm³"))
    return out
