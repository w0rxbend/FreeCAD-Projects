"""Snap saddle for a low-ESR capacitor, hung outboard of the bottom plate at the waist."""

from math import tan

from build123d import Part

from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "cap_holder"
TITLE = "Capacitor saddle (outboard L-bracket)"
MATERIAL = "TPU95A"
PRINT = {"cap_holder_right": (0, 0, -1), "cap_holder_left": (0, 0, -1)}
EXCLUSIVE = ()
ASSEMBLY_LABELS = ("cap_holder_right",)  # install ONE side; the pair is the left/right choice
MOUNTS = ("plate_bottom underside Z 0 (the tab seats on it)",
          "Ø4.5 waist hole (±28, 0) - the Ø4.0 boss locates in it, the bolt passes through",
          "plate_bottom outboard edge at y ±7 (two 2.5 mm key posts bear on it, Z 0-1.8)")
HARDWARE = ("1 x M3 x 8 up from below + 1 x M3 nut on top of the plate (grip 5.7 mm; M3 x 12 also "
            "fits and leaves 6 mm of thread standing)",
            "1 x 2.5 mm zip tie round the closed ring at |y| 10.5-13.5 as a capacitor backup")
NOTES = (
    "Install ONE (right or left). The tab seats on the plate_bottom underside; the Ø4.0 boss locates in "
    "the Ø4.5 waist hole (±28, 0) and an M3 x 8 comes up from below (head in the Ø6.6 x 1.7 recess at "
    "Z -3, nut on top of the plate at Z 2-4.4 in the empty arm-root gap; grip is 5.7 mm, so M3 x 12 "
    "leaves 6 mm of thread standing). Two 3.4-4.0 x 2.5 key posts (Z 0-1.8) bear on the plate edge at "
    "y ±7 and take the yaw the single bolt cannot. The Ø12.5 x 25 capacitor snaps in through the "
    "mouth and is held by two 0.3 mm lips; its crown stands 3.2 mm proud of the mouth face, so a "
    "2.5 mm zip tie wrapped round the closed ring at |y| 10.5-13.5 (outboard of the tab) presses "
    "straight down on it as a backup. Leads exit +Y and must bend inboard: a straight lead at "
    "x 43 meets arm_front_right after 11 mm. Ø16 x 20 variant: build(CAP_D=16, CAP_L=20) - it fits "
    "the frame but grows the envelope to x 21-54.5, Z -3-12.1. "
    "Deviations from the spec sheet: the mouth points 75° (up, 15° outboard) instead of +X, which is "
    "what makes the Ø12.8 bore self-supporting (worst cavity normal n_z -0.259) without a bridge "
    "exemption; each lip is a 20° ramp off the full bore radius instead of a square step, which "
    "removes the two 0.04 mm sliver faces the step used to leave; the head recess is 1.7 deep, not "
    "2.0, so 1.3 mm of tab is left above it; and there are NO zip-tie windows - any window at "
    "(43, ±9) opens tangentially to the Ø16 outer surface and tapers the 1.6 mm wall to nothing, "
    "and with 0.15 mm radial clearance a tie cannot pass round the capacitor inside the bore anyway. "
    "The Ø4.0 boss is a deliberate 0.3 mm collar round the Ø3.4 bore (rev-2 mandates Ø4.0): slice "
    "with thin-wall/single-perimeter on, or set BOSS_DIA=0 and let the bolt alone locate the bracket."
)

# --- parameters (mm) --------------------------------------------------------------------------
CAP_D = 12.5            # capacitor Ø (Ø16 variant: build(CAP_D=16, CAP_L=20))
CAP_L = 25.0
LIP = 0.3               # radial grip of each retaining lip on the capacitor
WALL_T = 1.6
X_HOLE = 28.0           # Ø4.5 waist accessory hole
X_WALL = 35.0           # inboard extreme of the saddle: 1.0 mm clear of the plate edge (x 33.974 at y 0)
X_CAP = 43.0            # saddle axis = X_WALL + outer radius (recomputed when CAP_D changes)
AXIS_Z = 5.0            # axis height = -TAB_T + outer radius, i.e. the shell sits on the bed plane
BOSS_DIA = 4.0
BOSS_H = 1.8
TAB_T = 3.0
MOUTH_ANGLE = 75.0      # mouth direction in the XZ plane, 0 = +X; keeps the whole cavity < 45° overhang
LIP_RAMP = 20.0         # lip lead-in angle off the mouth axis; <= MOUTH_ANGLE - 46 stays self-supporting
MOUTH_FACE = 3.0        # the mouth ends in a flat face this far out from the axis (kills feather horns)
RECESS_H = 1.7          # M3 button head recess depth; leaves TAB_T - RECESS_H of tab above it
CAV_FIT = 0.3           # cavity Ø = CAP_D + CAV_FIT
TAB_X0 = 22.0           # inboard edge: 0.8 clear of the (18, 0) sandwich-bolt nut under the plate
TAB_HY = 9.5
BLOCK_H = 7.0           # foot block height above the bed plane (top at Z 4 with TAB_T 3)
BLOCK_INSET = 1.0       # foot block half width = outer radius - this, so its top corners stay inside
BLOCK_FILLET = 0.8      # softens the two concave corners where the block meets the shell circle
KEY_Y = 7.0             # anti-rotation posts bearing on the plate edge at y ±KEY_Y
KEY_HY = 1.25
KEY_H = 1.8             # below the plate top face (Z 2), so the posts never reach the arms
KEY_GAP = 0.35          # clearance from the post face to the plate outline


def _dir(deg: float) -> tuple[float, float]:
    return cos(radians(deg)), sin(radians(deg))


def _params(**overrides) -> dict:
    p = {"CAP_D": CAP_D, "CAP_L": CAP_L, "LIP": LIP, "WALL_T": WALL_T, "X_HOLE": X_HOLE,
         "X_WALL": X_WALL, "BOSS_DIA": BOSS_DIA, "BOSS_H": BOSS_H, "TAB_T": TAB_T,
         "MOUTH_ANGLE": MOUTH_ANGLE, "CAV_FIT": CAV_FIT, **overrides}
    p["cav_r"] = (p["CAP_D"] + p["CAV_FIT"]) / 2
    p["out_r"] = p["cav_r"] + p["WALL_T"]
    p["mh"] = p["CAP_D"] / 2 - p["LIP"]     # half mouth width: the lips reach LIP inside the capacitor
    p["ramp_t"] = (p["cav_r"] - p["mh"]) / max(1e-6, tan(radians(LIP_RAMP)))
    p["z_bed"] = -p["TAB_T"]
    p["hl"] = (p["CAP_L"] + 2.0) / 2        # saddle half length
    # The shell sits on the bed plane and its inboard extreme lands on X_WALL, so both the axis and
    # the block follow CAP_D (Ø12.5 -> the spec's X_CAP 43, AXIS_Z 5, block x 36-50).
    p.setdefault("X_CAP", p["X_WALL"] + p["out_r"])
    p.setdefault("AXIS_Z", p["z_bed"] + p["out_r"])
    p["blk_hx"] = p["out_r"] - BLOCK_INSET
    p["blk_z1"] = p["z_bed"] + BLOCK_H
    if not overrides:  # the documented defaults must agree with what the geometry derives
        assert (p["X_CAP"], p["AXIS_Z"]) == (X_CAP, AXIS_Z), (p["X_CAP"], p["AXIS_Z"])
    return p


def _plate_edge(y0: float, y1: float, step: float = 0.25) -> float:
    """Outermost plate_bottom outline x over y0..y1 (the key posts must clear all of it)."""
    ys = [y0 + i * step for i in range(int((y1 - y0) / step) + 1)] + [y1]
    xs = [max(s)[1] for s in (outline_spans("plate_bottom", y) for y in ys) if s]
    return max(xs)


def _section(p: dict) -> Part:
    """Saddle cross-section extruded along Y: outer circle + foot block, minus the bore, the
    ramped mouth and the flat mouth face."""
    xc, zc, a = p["X_CAP"], p["AXIS_Z"], p["MOUTH_ANGLE"]
    cav_r, out_r, mh, z_bed, hl = p["cav_r"], p["out_r"], p["mh"], p["z_bed"], p["hl"]

    blk = Pos(xc, (z_bed + p["blk_z1"]) / 2) * Rectangle(2 * p["blk_hx"], p["blk_z1"] - z_bed)
    outer_sk = Pos(xc, zc) * Circle(out_r) + blk

    # Cavity in mouth-local (t, s): t along MOUTH_ANGLE, s across it. Back half of the bore, plus a
    # mouth polygon whose walls ramp from the full bore radius down to the lips over LIP_RAMP. The
    # ramp replaces the square step that used to leave a 0.05 mm ledge at each lip tip.
    back = Pos(xc, zc) * Rectangle(80, 80, align=(Align.MAX, Align.CENTER)).rotate(Axis.Z, a)
    big = out_r + 5
    mouth_pts = [(-cav_r / 2, cav_r * 0.6), (0, cav_r), (p["ramp_t"], mh), (big, mh),
                 (big, -mh), (p["ramp_t"], -mh), (0, -cav_r), (-cav_r / 2, -cav_r * 0.6)]
    mouth = Pos(xc, zc) * Polygon(*mouth_pts, align=None).rotate(Axis.Z, a)
    chop = Pos(xc, zc) * (Pos(MOUTH_FACE, 0) * Rectangle(60, 60, align=(Align.MIN, Align.CENTER))).rotate(Axis.Z, a)

    prof = outer_sk - ((Pos(xc, zc) * Circle(cav_r) & back) + mouth + chop)
    if BLOCK_FILLET > 0:  # the two concave corners where the block face meets the shell circle
        zj = zc - (out_r ** 2 - p["blk_hx"] ** 2) ** 0.5
        corners = [Vector(xc - p["blk_hx"], zj, 0), Vector(xc + p["blk_hx"], zj, 0)]
        try:
            prof = fillet(prof.vertices().filter_by(
                lambda v: any((Vector(v.X, v.Y, 0) - c).length < 0.02 for c in corners)), BLOCK_FILLET)
        except Exception:  # noqa: BLE001  a variant may put the junction elsewhere
            pass
    return extrude(Plane.XZ.offset(-hl) * prof, amount=2 * hl)


def _tab(p: dict) -> Part:
    tab_x1 = p["X_CAP"] - p["blk_hx"] + 1.0     # 1 mm overlap onto the foot block
    sk = Pos((TAB_X0 + tab_x1) / 2, 0) * Rectangle(tab_x1 - TAB_X0, 2 * TAB_HY)
    sk = fillet(sk.vertices().filter_by(lambda v: v.X < TAB_X0 + 1e-6), 3.0)
    return extrude(Plane.XY.offset(p["z_bed"]) * sk, amount=p["TAB_T"])


def _keys(p: dict) -> Part:
    """Two posts standing on the tab whose inboard faces bear on the plate outline at y ±KEY_Y.
    The bolt alone cannot resist yaw; a post 5-8 mm off the bolt axis swings inboard faster than
    the plate edge falls away, so it jams into the carbon in either direction."""
    part = Part()
    x1 = p["X_CAP"] - p["blk_hx"]               # merges into the foot block
    for yc in (KEY_Y, -KEY_Y):
        x0 = _plate_edge(yc - KEY_HY, yc + KEY_HY) + KEY_GAP
        part += box(x0, yc - KEY_HY, 0.0, x1, yc + KEY_HY, KEY_H)
    return part


def _build_one(p: dict) -> Part:
    part = _section(p) + _tab(p) + _keys(p)
    if p["BOSS_DIA"] > 0:
        part += cylinder(p["X_HOLE"], 0, 0, p["BOSS_H"], p["BOSS_DIA"])
    part -= cylinder(p["X_HOLE"], 0, p["z_bed"] - 0.5, p["BOSS_H"] + 0.5, D_M3_THRU)
    part -= cylinder(p["X_HOLE"], 0, p["z_bed"] - 0.5, p["z_bed"] + RECESS_H, D_M3_HEAD_RECESS)
    assert len(part.solids()) == 1, f"cap_holder: {len(part.solids())} solids"
    return Part(part.wrapped)


def build(**overrides) -> dict[str, Part]:
    return pair(_build_one(_params(**overrides)), NAME)


# --- probes ------------------------------------------------------------------------------------
def _bore_cylinder(p: dict) -> Part:
    """The full Ø(CAP_D + CAV_FIT) cylinder: holder material inside it is the two lips."""
    hl = p["hl"] + 2
    return extrude(Plane.XZ.offset(-hl) * (Pos(p["X_CAP"], p["AXIS_Z"]) * Circle(p["cav_r"])), amount=2 * hl)


def _lip_solids(holder: Part, p: dict) -> tuple[Part, Part, Part]:
    lips = holder & _bore_cylinder(p)
    upper = box(p["X_CAP"] - 30, -p["hl"] - 3, p["AXIS_Z"], p["X_CAP"] + 30, p["hl"] + 3, p["AXIS_Z"] + 30)
    return lips, lips & upper, lips - upper


def _collar(p: dict) -> Part:
    """The 0.3 mm registration collar: the one intentional sub-WALL feature."""
    return (cylinder(p["X_HOLE"], 0, 0, p["BOSS_H"], p["BOSS_DIA"])
            - cylinder(p["X_HOLE"], 0, -1, p["BOSS_H"] + 1, D_M3_THRU))


def _cap_probe(p: dict, d: float | None = None, length: float | None = None) -> Part:
    d = p["CAP_D"] if d is None else d
    length = p["CAP_L"] if length is None else length
    return Pos(p["X_CAP"], 0, p["AXIS_Z"]) * Cylinder(d / 2, length, rotation=(-90, 0, 0))


def _inboard_probe(p: dict) -> Part:
    """Everything inboard of the plate_bottom outline + 0.25 above Z 0, minus the Ø4.5 waist hole
    (where the boss belongs). Nothing of the holder may be in it."""
    probe = Part()
    y = -p["hl"]
    while y <= p["hl"] + 1e-6:
        spans = outline_spans("plate_bottom", y)
        if spans:
            probe += box(-5, y - 0.25, Z_BOTTOM_UNDER + 0.01, max(spans)[1] + 0.25, y + 0.25, 40)
        y += 0.5
    return probe - cylinder(p["X_HOLE"], 0, -1, 3, 5.0)


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    right = parts["cap_holder_right"]
    left = parts["cap_holder_left"]
    p = _params()
    out: list[tuple[str, bool, str]] = []

    hits = interference(right)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))

    # --- Ø4.0 registration boss in the Ø4.5 waist hole ---
    d_hole = hole_d("waist_accessory")
    annulus = (cylinder(X_HOLE, 0, 0.0, BOSS_H, d_hole)
               - cylinder(X_HOLE, 0, -0.5, BOSS_H + 0.5, d_hole - 0.4))
    v_ann = isect(right, annulus)
    out.append((f"boss clear of the Ø{d_hole} hole wall (annulus probe)", v_ann < EPS, f"{v_ann:.4f} mm³"))
    bss = right & cylinder(X_HOLE, 0, 0.1, BOSS_H - 0.1, d_hole + 0.2)
    bb = bss.bounding_box()
    r_meas = max(bb.size.X, bb.size.Y) / 2
    off = max(abs(bb.center().X - X_HOLE), abs(bb.center().Y))
    ok_boss = abs(r_meas - (d_hole - 0.5) / 2) <= 0.05 and off <= 0.05
    out.append(("boss radius 2.0 ±0.05, coaxial with the Ø4.5 axis ±0.05", ok_boss,
                f"r {r_meas:.3f}, axis offset {off:.3f} mm"))
    ok_bore, det = coaxial(right, (X_HOLE, 0), D_M3_THRU, -TAB_T + RECESS_H + 0.1, BOSS_H - 0.1)
    out.append(("M3 bore coaxial with the waist hole", ok_bore, det))

    # --- seating, hardware under the plate, the nut pocket above it ---
    contact = seated(right, Z_BOTTOM_UNDER)
    out.append(("tab seated on the plate_bottom underside Z 0.000", contact >= 150.0, f"{contact} mm² contact"))
    nut = hex_pocket(5.5, 2.4, at=(X_HOLE, 0, Z_BOTTOM_TOP))
    blockers = {n: isect(nut, frame[n]) for n in (*PLATES, *ARM_NAMES) if isect(nut, frame[n]) > EPS}
    out.append(("M3 nut at Z 2-4.4 clears the arms and plates", not blockers, f"{blockers or 'gap empty'}"))
    # The frame carries no fasteners: the sandwich bolt at (18, 0) is plate_bottom-only, so its
    # nut hangs below Z 0 right beside the tab. Probe an M3 nyloc (6.35 across corners) + 0.25.
    hw = cylinder(18.0, 0.0, -4.5, Z_BOTTOM_UNDER, 6.35 + 2 * 0.25)
    v_hw = isect(right, hw)
    out.append(("tab clears the (18, 0) sandwich-bolt nut under the plate", v_hw < EPS,
                f"{v_hw:.4f} mm³ against a Ø6.85 x 4.5 nyloc probe; tab starts at x {TAB_X0}"))

    # --- capacitor fit ---
    lips, up, lo = _lip_solids(right, p)
    v_probe = isect(right, _cap_probe(p))
    v_out = isect(right - lips, _cap_probe(p))
    v_up, v_lo = isect(up, _cap_probe(p)), isect(lo, _cap_probe(p))
    out.append(("Ø12.5 x 25 capacitor clear of the holder except the two lips", v_out < EPS,
                f"{v_probe:.2f} mm³ total, {v_out:.4f} mm³ outside the lips"))
    deep = isect(right, _cap_probe(p, d=CAP_D - 2 * LIP - 0.02))
    out.append((f"no lip intrudes more than LIP {LIP} mm into the capacitor", deep < EPS, f"{deep:.4f} mm³"))
    ok_lips = all(1.0 <= v <= 20.0 for v in (v_up, v_lo))
    out.append(("both lips grip the capacitor (the spec's 0.2-0.4 mm³ band is arithmetically "
                f"unreachable: a {LIP} mm lip over {CAP_L + 2:.0f} mm is several mm³)", ok_lips,
                f"upper {v_up:.2f} mm³, lower {v_lo:.2f} mm³"))

    # --- envelope, keep-outs, printability ---
    bb = right.bounding_box()
    out.append(("above the landing plane Z -3", bb.min.Z >= LANDING_Z - 1e-6, f"min Z {bb.min.Z:.3f}"))
    out.append(("inside the x 21-51 / y ±13.5 / Z -3-13 envelope",
                bb.min.X >= 21.0 - 1e-6 and bb.max.X <= 51.001 and bb.max.Y <= 13.501 and bb.max.Z <= 13.001,
                f"x {bb.min.X:.2f}-{bb.max.X:.2f}, y ±{bb.max.Y:.2f}, Z {bb.min.Z:.2f}-{bb.max.Z:.2f}"))
    v_prop = prop_disc_violation(right)
    out.append(("outside the prop keep-out discs", v_prop < EPS, f"{v_prop:.3f} mm³"))
    edge = max(outline_spans("plate_bottom", 0.0))[1]
    inb = isect(right, _inboard_probe(p))
    out.append(("everything above Z 0 stays >= 0.25 mm outboard of the plate outline",
                inb < EPS and X_WALL - edge >= 1.0 - 1e-6,
                f"{inb:.4f} mm³ inboard; saddle wall x {X_WALL:.2f} vs plate edge {edge:.3f} at y 0"))

    bed = sum(f.area for f in right.faces()
              if f.geom_type == GeomType.PLANE and abs(f.center().Z - (-TAB_T)) < 1e-4 and f.normal_at().Z < -0.999)
    out.append(("bed faces at Z -3 >= 400 mm²", bed >= 400.0, f"{bed:.1f} mm²"))
    over = overhangs(right, PRINT["cap_holder_right"], bridge_ok=BRIDGE_OK["cap_holder_right"], material=MATERIAL)
    out.append(("no unsupported overhangs", not over, "; ".join(over) or "none"))

    # min_wall runs on the SHIPPED solid; the only sub-WALL features are the two 0.3 lips and the
    # rev-2 mandated 0.3 mm boss collar, both declared.
    ok_wall, _v, wdet = min_wall(right, WALL, allow=(lips, _collar(p)))
    out.append((f"min wall >= {WALL} on the shipped part (allow: lips, boss collar)", ok_wall, wdet))
    # Ray sampling is blind to knife edges, so the prismatic shell (where a tapering lip or horn
    # would hide) also gets the erode/dilate treatment on its own, without the tab and the collar.
    ok_shell, _vs, sdet = min_wall(_section(p), WALL, allow=(lips,))
    out.append((f"min wall >= {WALL} on the bare shell (erode/dilate, allow: lips)", ok_shell, sdet))
    short = min(e.length for e in right.edges())
    # A sliver face is long and hair-thin: ignore the zero bbox dimension of a planar face and
    # look at the smaller of its two in-plane extents.
    slivers = [f for f in right.faces() if f.area > 0.2 and sorted(f.bounding_box().size)[1] < 0.15]
    out.append(("no sliver faces or degenerate edges", short >= 0.15 and not slivers,
                f"shortest edge {short:.3f} mm, {len(slivers)} sliver face(s)"))

    # --- Ø16 x 20 variant: still clean on the frame, but it needs its own envelope ---
    var = _build_one(_params(CAP_D=16.0, CAP_L=20.0))
    vb = var.bounding_box()
    ok_var = (not interference(var) and prop_disc_violation(var) < EPS and vb.min.Z >= LANDING_Z - 1e-6
              and seated(var, Z_BOTTOM_UNDER) >= 150.0 and len(var.solids()) == 1)
    out.append(("Ø16 x 20 variant fits the frame (envelope grows past the catalog x 51)", ok_var,
                f"x {vb.min.X:.2f}-{vb.max.X:.2f}, y ±{vb.max.Y:.2f}, Z {vb.min.Z:.2f}-{vb.max.Z:.2f}"))

    out.append(("left copy is the mirror of the right", abs(left.volume - right.volume) < 1e-3,
                f"{right.volume:.1f} vs {left.volume:.1f} mm³"))
    return out


# Counterbore shoulder (Ø3.4 -> Ø6.6) bridging over the bolt hole, in PRINT coordinates
# (bed normal (0,0,-1): no rotation, X/Y centred on the bbox, Z shifted up by TAB_T).
BRIDGE_OK = {
    "cap_holder_right": (("box", -13.0, -4.5, 1.2, -4.0, 4.5, 2.2),),
    "cap_holder_left": (("box", 4.0, -4.5, 1.2, 13.0, 4.5, 2.2),),
}
