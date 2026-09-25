"""Twin-ring TPU sling: the camera hangs from the two front-tip standoffs on one ~5 g part.

The reference clamp-slings grip each standoff with an independent clamp, so the only thing stopping
the camera from creeping nose-down is friction at two separate Ø6 pins. This part closes that loop:
both rings are COMPLETE (they thread on with the front-tip standoffs out) and they are joined by a
single tie bar that passes UNDER the camera, so the two ring axes are 38.0 mm apart in one rigid
solid. Rotation about either pin would need the part to change length. It cannot creep.

Everything else is deliberately absent. Nothing wraps the camera, nothing sits ahead of the lens,
and nothing reaches above Z 30.5: the top of the bay, the whole fork window and the pigtail exit
stay open, and `camera_visor` / `lens_cover` still have the lens mouth to themselves. The camera is
held by its own two M2 side screws into two compliant tongues that flex outboard, which is what
lets ONE part take a 19, a 21 and a 22 mm body.

Tilt is fixed per variant (t0 / t10 / t20) and that is the honest trade: an arc slot would hand the
creep straight back. The part is ~5 g, so print the two you fly.
"""

from math import atan2, cos, degrees, radians, sin

from build123d import (Axis, Circle, Part, Plane, Pos, Sketch, SlotCenterToCenter, Vector,
                       extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_standoff_sling"
TITLE = "Twin-ring standoff sling (19 / 21 / 22 mm)"
MATERIAL = "TPU95A"
# Every camera mount owns the same bay, and camera_damped_cradle also owns the same two standoff
# shafts: fit one. Stated from both ends; resolve_exclusive() reads EXCLUSIVE symmetrically.
EXCLUSIVE = ("camera_pod", "camera_pod_22", "camera_damped_cradle", "camera_detent_bracket",
             "camera_hoop_guard")
PRINT = {"camera_standoff_sling": (0, -1, 0)}

VARIANTS = {
    "t0": {"params": {"TILT": 0.0}, "notes": "0 deg: cruise / line-of-sight and bench setup."},
    "t10": {"params": {"TILT": 10.0}, "notes": "10 deg: long-range cruise at moderate speed."},
    "t20": {"params": {"TILT": 20.0}, "notes": "20 deg: freestyle and fast cruise."},
}
ASSEMBLY_VARIANT = "t10"

MOUNTS = ("standoff_front_tip_left / _right Ø6 shafts (±19, 109) through two CLOSED Ø6.5 rings, "
          "Z 10-26",)
HARDWARE = ("2 x M2 camera side screws - the camera's own, through the Ø2.4 tongue holes into the "
            "camera body; no frame hardware is touched",)
NOTES = (
    "Thread the two rings onto the front-tip standoffs with the standoffs out (or over them before "
    "plate_top goes back on), then bolt the camera to the two tongues with its own M2 side screws. "
    "The tie bar sits 1.0 mm above plate_mid's Z 9 face and 2.35 mm under a 21 mm body at 0 deg - it "
    "carries no load onto the plate, it only keeps the two rings from turning. Nothing is seated or "
    "bolted to any plate, and no frame fastener is touched. "
    "The tongues are the size adapter: their pad faces sit at |x| 9.5 unloaded, so a 19 mm body "
    "springs each one 0.25 mm outboard, a 21 mm body 1.25 mm and a 22 mm Foxeer Mini Cat 1.75 mm - "
    "all inside the 2.0 mm flex budget, which is 10.3% peak fibre strain in TPU95A at the widest "
    "body. ONE 0.5 mm proud landing strip spans both holes on each flank, so an M2 head always "
    "lands on a flat whatever the body width. "
    "DEVIATIONS from the brief, each forced by a check: (1) the pads reach Z 30.5, not Z 26 - the "
    "upper M2 hole IS the tilt pivot at Z 27 and needs 3.5 mm of material over it; the RINGS still "
    "stop at Z 26, so Z 26-31.5 stays clear outboard of |x| 12.5 and the side-panel band "
    "31.7-33.75 is untouched. (2) The tie bar's leading face is a Ø3.4 round nose, not a 45 deg "
    "chamfer: a chamfer steep enough to pass the overhang check leaves a knife edge along all "
    "38 mm of the bar, while the nose is an arch of d 3.4 that the same check exempts and that "
    "min_wall is happy with. (3) The tongues run y 90.5-104 (13.5 mm, not 9) and the pad strip is "
    "one capsule rather than a boss per hole: the rear M2 hole needs 3.5 mm of edge distance at "
    "every tilt, and two Ø6 bosses 6.0 mm apart are exactly tangent, which tessellates into an "
    "invalid 3MF mesh. (4) The tongue is 2.5 mm thick and the arm 4.0 mm, so the arm's inboard "
    "face sits at |x| 11.6 - 0.35 mm clear of the widest camera flank, which is what keeps the "
    "tongues the only thing the camera ever touches."
)

# --- parameters (mm) ---------------------------------------------------------------------------
RING_XY = FRONT_TIP_XY  # (19, 109)
RING_Z0, RING_H = 10.0, 16.0  # Z 10.0-26.0, inside the standoff's Z 9-34 run
RING_BORE = D_CLIP_BORE  # 6.5 round the Ø6 standoff -> 0.25 radial fit
RING_WALL = CLIP_WALL  # 1.6 -> OD 9.7, outer material |x| <= 23.85

BAR_Y = (105.5, 112.0)  # tie bar under the camera; rear face flush with nothing, nose rounded
BAR_Z = (10.0, 13.4)  # 1.0 mm over plate_mid's Z 9 face
BAR_NOSE_R = (BAR_Z[1] - BAR_Z[0]) / 2  # 1.7: the leading edge is an arch, not a knife chamfer

ARM_X = (11.6, 15.6)  # 4.0 thick; inboard face clears the widest camera flank (|x| 11.25)
ARM_A = (109.5, 16.5)  # (y, z) capsule centre at the ring
ARM_B = (98.5, 22.5)  # (y, z) capsule centre inside the tongue root
ARM_W = 7.0  # capsule width -> both end caps are d 7 arches

PAD_X = 9.5  # unloaded pad face; the flank of a 19 mm body sits at 9.75
TONGUE_T = 2.5  # pad face 9.5 -> outer face 12.0
TONGUE_Y = (90.5, 104.0)  # 3.5 mm of edge round the rear M2 hole at every supported tilt
TONGUE_Z = (21.0, 30.5)
PAD_PROUD = 0.5  # landing strip out to x 12.5 so the M2 head always lands on a flat
PAD_BOSS_D = 6.0  # width of that strip; it is a capsule through both hole axes
HOLE_PITCH = 6.0  # second M2 hole 6.0 mm behind the pivot, in the TILTED lens frame
HOLE_D = D_M2_THRU  # 2.4
TILT = 10.0

FLEX_MAX = 2.0  # design flex budget per tongue (checked against every supported body width)
CAM_WIDTHS = (19.0, 21.0, 22.0)


# --- helpers -----------------------------------------------------------------------------------
def _yz(sk: Sketch, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in (frame Y, frame Z) along +X from x0 to x1."""
    plane = Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return extrude(plane * sk, amount=x1 - x0)


def _capsule(a: tuple[float, float], b: tuple[float, float], w: float) -> Sketch:
    """Stadium in the YZ plane between centres a and b, width w (round caps = printable arches)."""
    d = Vector(b[0] - a[0], b[1] - a[1], 0)
    sk = SlotCenterToCenter(d.length, w).rotate(Axis.Z, degrees(atan2(d.Y, d.X)))
    return Pos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) * sk


def hole_centres(tilt: float, pitch: float = HOLE_PITCH) -> tuple[tuple[float, float], ...]:
    """The two M2 axes in (frame Y, frame Z): the tilt pivot, and `pitch` behind it in the tilted
    lens frame (rotated about Axis(CAM_PIVOT, +X), so the pair lies along the camera's own flank)."""
    _px, py, pz = CAM_PIVOT
    t = radians(tilt)
    return ((py, pz), (py - pitch * cos(t), pz - pitch * sin(t)))


def _right_half(p: dict) -> Part:
    """Ring + arm + tongue for the +X side, before the bores are cut."""
    x, y = RING_XY
    ring = c_clip((x, y), z0=RING_Z0, h=RING_H, closed=True, bore_d=RING_BORE, wall=RING_WALL)
    arm = _yz(_capsule(p["ARM_A"], p["ARM_B"], p["ARM_W"]), *p["ARM_X"])
    ty0, ty1 = p["TONGUE_Y"]
    tz0, tz1 = p["TONGUE_Z"]
    tongue = box(p["PAD_X"], ty0, tz0, p["PAD_X"] + p["TONGUE_T"], ty1, tz1)
    # ONE proud landing strip spanning both holes, not a boss per hole: two Ø6 circles 6.0 mm
    # apart are exactly tangent, and a tangent pair tessellates into an invalid 3MF mesh.
    strip = _capsule(*hole_centres(p["TILT"]), p["PAD_BOSS_D"])
    x1 = p["PAD_X"] + p["TONGUE_T"]
    return ring + arm + tongue + _yz(strip, x1, x1 + p["PAD_PROUD"])


def _tie_bar(p: dict) -> Part:
    x, _y = RING_XY
    y0, y1 = p["BAR_Y"]
    z0, z1 = p["BAR_Z"]
    r = p["BAR_NOSE_R"]
    bar = box(-x, y0 + r, z0, x, y1, z1)
    return bar + _yz(Pos(y0 + r, (z0 + z1) / 2) * Circle(r), -x, x)


def build(variant: str = "t10", **overrides) -> dict[str, Part]:
    p = {k: globals()[k] for k in ("RING_Z0", "RING_H", "BAR_Y", "BAR_Z", "BAR_NOSE_R", "ARM_X",
                                   "ARM_A", "ARM_B", "ARM_W", "PAD_X", "TONGUE_T", "TONGUE_Y",
                                   "TONGUE_Z", "PAD_PROUD", "PAD_BOSS_D", "HOLE_D", "TILT")}
    p.update(overrides)
    right = _right_half(p)
    part = right + right.mirror(Plane.YZ) + _tie_bar(p)
    x, y = RING_XY
    for sx in (1, -1):
        part -= cylinder(sx * x, y, RING_Z0 - 2, RING_Z0 + RING_H + 2, RING_BORE)
    for hy, hz in hole_centres(p["TILT"]):
        part -= _yz(Pos(hy, hz) * Circle(p["HOLE_D"] / 2), -30.0, 30.0)
    part = part.clean()
    part.label = NAME
    return {NAME: part}


# --- checks ------------------------------------------------------------------------------------
_TILTS = tuple(sorted(v["params"]["TILT"] for v in VARIANTS.values()))


def _tilt_of(variant: str | None) -> float:
    return VARIANTS.get(variant or ASSEMBLY_VARIANT, {}).get("params", {}).get("TILT", TILT)


def _pad_zone() -> Part:
    """Everything the camera body is ALLOWED to touch: the two tongue plates and their bosses."""
    x0, x1 = PAD_X - 0.2, PAD_X + TONGUE_T + PAD_PROUD + 0.1
    y0, y1 = TONGUE_Y[0] - 0.2, TONGUE_Y[1] + 0.2
    z0, z1 = TONGUE_Z[0] - 0.2, TONGUE_Z[1] + 0.2
    right = box(x0, y0, z0, x1, y1, z1)
    return right + right.mirror(Plane.YZ)


def _hole_axis(part: Part, hy: float, hz: float, d: float = HOLE_D, tol: float = 0.05) -> tuple[bool, str]:
    """coaxial() for a bore whose axis runs along +X instead of +Z: a Ø(d - tol) probe must be void
    through the tongue and an annulus round it must hit material on both flanks."""
    x0, x1 = PAD_X - 0.1, PAD_X + TONGUE_T + PAD_PROUD + 0.1
    inside = around = 0.0
    for sx in (1, -1):
        lo, hi = (x0, x1) if sx > 0 else (-x1, -x0)
        inside += isect(part, _yz(Pos(hy, hz) * Circle((d - tol) / 2), lo, hi))
        ring = _yz(Pos(hy, hz) * (Circle(d / 2 + tol + 0.6) - Circle(d / 2 + tol)), lo, hi)
        around += isect(part, ring)
    ok = inside < EPS and around > EPS
    return ok, f"Ø{d} bore: {inside:.3f} mm³ in the bore, {around:.1f} mm³ round it"


def _spans_bay(part: Part, z: float = 12.0, step: float = 0.5) -> tuple[bool, float]:
    """Is there material at every x from -19 to +19 in the Z z section? That, plus one solid, is
    what makes rotation about either standoff impossible: the two ring axes are tied together by a
    continuous run of material, so creeping nose-down would have to shorten the part."""
    x = -RING_XY[0]
    worst = 1e9
    while x <= RING_XY[0] + 1e-9:
        v = isect(part, box(x - 0.05, TONGUE_Y[1], z - 0.1, x + 0.05, 114.0, z + 0.1))
        worst = min(worst, v)
        if v <= EPS:
            return False, round(x, 2)
        x += step
    return True, round(worst, 4)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list[tuple[str, bool, str]]:
    part = parts[NAME]
    tilt = _tilt_of(variant)
    rows: list[tuple[str, bool, str]] = []

    ok, detail = single_solid(part)
    rows.append(("one valid solid", ok, detail))

    hits = interference(part)
    rows.append(("no interference with any frame part", not hits, f"overlaps {hits or 'none'}"))
    seat = seated(part, Z_MID_TOP)
    gap = distance_to_frame(part, near=3.0).get("plate_mid", -1.0)
    rows.append((f"floats clear of plate_mid (no seat at Z {Z_MID_TOP})", seat == 0.0 and gap >= 0.95,
                 f"{seat} mm² of contact, {gap} mm gap to plate_mid"))

    so = standoff_interference(part)
    rows.append((f"clear of the Ø{STANDOFF_D} standoff cylinders", not so, f"overlaps {so or 'none'}"))
    for sx, side in ((1, "right"), (-1, "left")):
        ok, detail = coaxial(part, (sx * RING_XY[0], RING_XY[1]), RING_BORE, RING_Z0, RING_Z0 + RING_H)
        rows.append((f"{side} ring coaxial with standoff_front_tip_{side}", ok, detail))

    v = prop_disc_violation(part)
    rows.append(("outside the prop keep-out discs", v < EPS,
                 f"{v:.3f} mm³; |x| 23.85 used of {max_abs_x_at(RING_XY[1]):.2f} allowed at y {RING_XY[1]}"))

    ok, worst = _spans_bay(part)
    rows.append(("anti-rotation: material continuous from x -19 to +19 at Z 12", ok,
                 f"thinnest probe {worst} mm³" if ok else f"gap at x {worst}"))

    zone = _pad_zone()
    rest = part - zone
    for w in CAM_WIDTHS:
        cam = camera_envelope(width=w, tilt_deg=tilt)
        v = isect(part, cam)
        v_rest = isect(rest, cam)
        flex = (w / 2 + FIT) - PAD_X
        rows.append((f"{w:g} mm body: the tongue pads are the ONLY contact", v > EPS and v_rest < EPS,
                     f"{v:.1f} mm³ on the pads, {v_rest:.3f} mm³ everywhere else, "
                     f"each tongue flexes {flex:.2f} mm"))
        rows.append((f"{w:g} mm body: tongue flex within the {FLEX_MAX} mm budget", flex <= FLEX_MAX + 1e-9,
                     f"{flex:.2f} mm of {FLEX_MAX} mm"))
    # The compliance claim, measured: a straight cantilever of thickness TONGUE_T deflected `flex`
    # over its free length L carries peak fibre strain 3*t*d/(2*L^2). L is taken as the shortest
    # free run there is - the arm's attachment centre to the top of the pad - so the number is the
    # worst case, not the average one. TPU95A yields well past 20%; 15% is the design ceiling here.
    L = TONGUE_Z[1] - ARM_B[1]
    strain = 3 * TONGUE_T * ((max(CAM_WIDTHS) / 2 + FIT) - PAD_X) / (2 * L * L)
    rows.append(("tongue peak fibre strain <= 15% at the widest body", strain <= 0.15,
                 f"{strain:.1%} (t {TONGUE_T}, free length {L:.1f} mm)"))

    # One part, three fixed tilts: the rings, the tie bar and the arms have to clear the camera at
    # EVERY tilt this accessory ships, not just this variant's, or the t0 and t20 prints would need
    # different rings. tilt_sweep() is the exact swept volume over the whole 0-20 deg band.
    sweep = tilt_sweep(width=max(CAM_WIDTHS), a0=0.0, a1=max(_TILTS))
    v = isect(rest, sweep)
    rows.append((f"rings, tie bar and arms clear the whole 0-{max(_TILTS):g} deg camera sweep",
                 v < EPS, f"{v:.3f} mm³"))

    for i, (hy, hz) in enumerate(hole_centres(tilt)):
        want = (CAM_PIVOT[1], CAM_PIVOT[2]) if i == 0 else \
            (CAM_PIVOT[1] - HOLE_PITCH * cos(radians(tilt)), CAM_PIVOT[2] - HOLE_PITCH * sin(radians(tilt)))
        err = max(abs(hy - want[0]), abs(hz - want[1]))
        ok, detail = _hole_axis(part, hy, hz)
        name = "tilt pivot" if i == 0 else f"{HOLE_PITCH} mm arc point"
        rows.append((f"M2 hole on the {name} of the {tilt:g} deg lens frame", ok and err <= 0.05,
                     f"axis (y {hy:.3f}, Z {hz:.3f}), {err:.4f} mm from the tilted point; {detail}"))

    band = fov_wedge(0.0) + fov_wedge(12.5) + fov_wedge(25.0)
    for label, wedge in ((f"{tilt:g} deg", fov_wedge(tilt)), ("the 0-25 deg tilt band", band)):
        v = isect(part, wedge)
        rows.append((f"nothing in the camera's field of view at {label}", v < EPS, f"{v:.3f} mm³"))

    ok_wall, _resid, wall_detail = min_wall(part, WALL)
    rows.append((f"min wall >= {WALL} mm (TPU95A)", ok_wall, wall_detail))
    over = overhangs(part, PRINT[NAME], material=MATERIAL)
    rows.append(("prints on its back with no unsupported overhang", not over, "; ".join(over) or "none"))
    vol = volume(part)
    rows.append(("mass sanity: <= 5500 mm³ (~6 g in TPU95A)", vol <= 5500.0, f"{vol:.0f} mm³, ~{vol * 1.21e-3:.1f} g"))
    bb = part.bounding_box()
    rows.append(("envelope: nothing ahead of y 114, nothing above Z 31.5", bb.max.Y <= 114.0 and bb.max.Z <= 31.5,
                 f"x ±{max(abs(bb.min.X), abs(bb.max.X)):.2f}, y {bb.min.Y:.1f}-{bb.max.Y:.2f}, Z {bb.min.Z:.1f}-{bb.max.Z:.1f}"))
    return rows
