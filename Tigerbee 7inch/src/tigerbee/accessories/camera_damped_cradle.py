"""Vibration-isolated TPU camera cradle - the only soft-mounted camera holder in the lineup.

Every other camera option on this frame bolts the sensor to carbon: `camera_pod` clamps the two
front-tip standoffs and seats on plate_mid, `camera_pod_22` does the same with a hood. That is
rigid by design, and rigid is exactly what puts motor-order vibration into a rolling-shutter
sensor. This part does the opposite. Two CLOSED rings own the standoffs - they are the rigid,
repeatable interface - and the camera shell is not attached to them. It hangs off four short TPU
flexure fins that bridge a 1.8 mm air gap, and it touches nothing else: not plate_mid (2.0 mm
clear at the ring feet, more under the shell), not a standoff, not the top plate.

  The claim is measured, not asserted. checks() deletes the air-gap slab from the finished solid
  and requires the remainder to fall into exactly THREE separate solids - shell, left ring, right
  ring. If any other path existed the count would be one. It then measures the fins' second moment
  of area in that slab and requires it to be under 1/100 of a solid bridge filling the same gap.

Tilt is moulded in, one angle per variant - 5 deg and 15 deg, deliberately the long-range band
that `camera_pod`'s 15-40 deg arc slot cannot serve at the bottom. There is no slot and no screw
to creep, so the horizon cannot walk mid-pack.

Four variants, one code path: t5_19, t5_21, t15_19, t15_21. A 22 mm body is reachable with
CAM_W=22 but is not shipped (camera_pod_22 owns that size).
"""

from math import cos, radians, sin

from build123d import (Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, SlotOverall,
                       Vector, extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_damped_cradle"
TITLE = "Vibration-isolated camera cradle (19/21 mm, 5 deg / 15 deg)"
MATERIAL = "TPU95A"
BASE = "camera_damped_cradle"
# Every camera mount owns the same bay, and these two also own the same two standoff shafts: fit
# one. Stated from both ends so the assembly resolver cannot install a second mount beside this one.
EXCLUSIVE = ("camera_pod", "camera_pod_22", "camera_standoff_sling", "camera_detent_bracket",
             "camera_hoop_guard")

# --- camera (mm) -------------------------------------------------------------------------------
CAM_W = 21.0        # 19 or 21 mm micro/nano body; the variant picks it
CAM_H = 22.0        # both classes are 22 mm tall over the mounting ears
CAM_D = 24.0        # body depth behind the lens flange
LENS_D = 14.0       # M12 holder OD
LENS_LEN = 6.0      # lens protrusion ahead of the body front face
FRONT_OFF = 10.0    # repo datum: CAM_PIVOT is the front M2 hole, 10 mm behind the front face
HOLE_PITCH = 6.0    # the two M2 side screws, fore/aft on the flank
TILT = 15.0         # moulded-in tilt, per variant

# --- the flexure mount --------------------------------------------------------------------------
RING_Z0 = 11.0      # rings sit Z 11.0-29.0 on the Ø6 front-tip standoffs: 2.0 mm off plate_mid
RING_H = 18.0       # (Z 9) at the bottom and 5.0 mm below plate_top (Z 34) at the top, which
#                     leaves the Z 31.7-33.75 band free for side_panel_system.
GAP = 1.8           # air gap between the shell flank and the ring's nearest material
WEB_T = 1.6         # fin thickness (Z) - THE SPRING. Do not fatten it: k scales with t^3.
WEB_H = 2.4         # fin width (Y)
WEB_Y = (106.0, 109.4)   # the two fin centres per side. Both live in the band where the ring
#                     (y 104.15-113.85) and the shell flank overlap with room to spare: further
#                     forward the tilted flank has shrunk to a sliver and a flat fin would graze
#                     it instead of meeting it.
Z_FLOOR = 11.0      # the whole part is cut off flat at Z 11.0 - FLOOR_CLEAR above plate_mid and
#                     level with the ring feet. At 15 deg the tilted tail would otherwise reach
#                     Z 10.7. The cut face is horizontal, so in print orientation its normal is
#                     level with the bed, not facing it: no overhang, and the clearance is
#                     guaranteed by construction rather than by arithmetic.
WEB_X_OUT = 18.0    # fins run this far outboard and are then cut by the Ø6.5 bore
SHELL_WALL = 1.8    # nominal shell wall; waisted to whatever GAP leaves (1.6 at 21 mm)
FLOOR_CLEAR = 2.0   # design clearance under the part over plate_mid
RIB_PROUD = 0.6     # grip ribs standing proud of the cavity - the TPU squeezes the body
RIB_W, RIB_L = 1.5, 7.0          # flank rib footprint (xi x v)
RIB_XI = (7.5, -3.5, -12.0)      # three per flank, clear of both M2 holes
FLOOR_RIB_X, FLOOR_RIB_W, FLOOR_RIB_L = 4.5, 1.5, 12.0   # two under the body
CABLE_OPEN_FRAC = 0.55           # rear opening: everything above this fraction of the body height
Y_BED = 83.0        # the flat -Y plane the part prints on, and the pigtail exit
V_TOP = 9.0         # flank top edge at the lens end, 2.25 below the body top: the camera drops
#                     straight in past the ribs and nothing roofs it.
TOP_FALL = 0.22     # the flank top does not run level - it falls 0.22 per mm going aft, so the
#                     part reads as a saddle round the lens rather than a box. The limit is a
#                     print limit: that face's frame normal is -sin(atan(TOP_FALL) + tilt), and
#                     at 0.22 with 15 deg of tilt it is -0.52 against the -0.70 floor.
FRONT_CH = 2.5      # the front-top corner is cut back 2.5 mm - a prow, and it faces up in print
XI_CH = -14.4       # the swept tail: the underside chamfers up-and-back from here. It must stay
#                     OUTBOARD of the cavity's rear-bottom inner corner (-14.25, -11.25) by more
#                     than WALL, or the 45 deg cut shaves that corner into a knife edge; -14.4
#                     leaves 1.38 mm measured perpendicular to the chamfer.
CH_DEG = 45.0       # ... at 45 deg. The face's own normal then sits 45 deg off -Y in the camera
#                     frame, and the moulded tilt only rotates it further away from the bed, so
#                     the tail is self-supporting at both 5 and 15 deg. 50 deg is NOT enough:
#                     it measures -0.71 against the -0.70 limit at 5 deg of tilt.
XI_FRONT_OUT = 10.0 # shell front edge, 0.25 behind the body front face - no bezel over the glass

VARIANTS = {
    "t5_19":  {"style": "shard", "params": {"TILT": 5.0,  "CAM_W": 19.0},
               "notes": "19 mm nano body, 5 deg: the flattest long-range setting, moulded in."},
    "t5_21":  {"style": "shard", "params": {"TILT": 5.0,  "CAM_W": 21.0},
               "notes": "21 mm micro body, 5 deg."},
    "t15_19": {"style": "shard", "params": {"TILT": 15.0, "CAM_W": 19.0},
               "notes": "19 mm nano body, 15 deg: the softest mount of the four - the smaller "
                        "body widens the air gap to 2.6 mm, so the fins are longer and softer."},
    "t15_21": {"style": "shard", "params": {"TILT": 15.0, "CAM_W": 21.0},
               "notes": "21 mm micro body, 15 deg - the shipped default."},
}
ASSEMBLY_VARIANT = "t15_21"

PRINT = {BASE: (0, -1, 0)}
MOUNTS = ("standoff_front_tip_left / _right Ø6 shafts (±19, 109), Z 11-29, through two CLOSED "
          "Ø6.5 rings",)
HARDWARE = ("none - the two closed rings are threaded onto the front-tip standoffs while they are "
            "out, and the camera is a friction fit on the grip ribs",
            "optional 2 x M2 x 4 camera side screws (the camera's own) through the Ø2.4 flank "
            "holes, if you want belt and braces")
NOTES = ("THREADED ON, NOT CLIPPED ON. Both rings are complete circles: take the two front-tip "
         "standoffs out (or lift plate_top), slide the cradle down over them, put them back. That "
         "is deliberate - an open C-mouth on a soft mount lets the camera lever itself off under "
         "load, and this part carries the camera on nothing but four 1.6 mm fins. "
         "The camera drops in from ABOVE between the flanks and is held by five 0.6 mm ribs; its "
         "own M2 screws are optional. The pigtail leaves through the open rear-upper corner and "
         "over the top of the rear wall. Tilt is moulded in - pick the variant, there is no slot. "
         "Nothing but the fins crosses the air gap, so keep the gap clean of zip ties and hot "
         "glue: bridging it re-couples the camera to the frame and undoes the whole part. "
         "Prints on its back on the flat y 83.0 rear face; no supports, no bridges declared.")


# --- the camera frame ---------------------------------------------------------------------------
# CAM_PL is the untilted lens-axis plane through CAM_PIVOT: sketch u = frame +Y (xi, along the lens
# axis), sketch v = frame +Z, plane normal = frame +X. Everything inside the shell is drawn here and
# the finished shell is rotated about Axis(CAM_PIVOT, +X) by TILT at the very end, so the cavity,
# the ribs and the M2 holes are all built in the tilted frame by construction.
CAM_PL = Plane(Vector(*CAM_PIVOT), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
RING_X, RING_Y = FRONT_TIP_XY            # (19.0, 109.0)
RING_OD = D_CLIP_BORE + 2 * CLIP_WALL    # 9.7
RING_X_IN = RING_X - RING_OD / 2         # 14.15: the ring's innermost material
_BUILT: dict[str, dict] = {}


def _cav_half(cam_w: float) -> float:
    """Cavity half-width: the camera body plus the TPU radial fit."""
    return cam_w / 2 + FIT


def _shell_half(cam_w: float) -> float:
    """Flank outer half-width. SHELL_WALL is the nominal, but the 1.8 mm air gap outranks it: at
    21 mm the flank is waisted to 1.6 (== CLIP_WALL, still well over WALL 1.2) so the gap stays
    1.8; at 19 mm the full 1.8 wall fits and the gap opens to 2.6."""
    return min(_cav_half(cam_w) + SHELL_WALL, RING_X_IN - GAP)


def _slab(sk, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in CAM_PL from frame x0 to x1 (x0 < x1)."""
    return extrude(CAM_PL.offset(x0) * sk, amount=x1 - x0)


def _tilt(part: Part, t: float) -> Part:
    return part.rotate(Axis(Vector(*CAM_PIVOT), (1, 0, 0)), t) if t else part


def _outer_profile(cam_w: float):
    """The U silhouette in (xi, v). Front edge, flank top, a long swept tail that the Y_BED cut
    trims, and an underside that chamfers up-and-back from XI_CH so nothing hangs low over
    plate_mid and no face turns into a down-face when the part prints on its back."""
    v_bot = -(CAM_H / 2 + FIT) - SHELL_WALL
    reach = 12.0  # long enough to cross y = Y_BED at both tilts; the rest is trimmed away
    dx, dv = reach * cos(radians(CH_DEG)), reach * sin(radians(CH_DEG))
    xi_prow, xi_tail = XI_FRONT_OUT - FRONT_CH, XI_CH - dx
    # counter-clockwise in (xi, v) so the face normal is +X and _slab extrudes the right way
    return Polygon((XI_CH, v_bot), (XI_FRONT_OUT, v_bot), (XI_FRONT_OUT, V_TOP - FRONT_CH),
                   (xi_prow, V_TOP), (xi_tail, V_TOP - TOP_FALL * (xi_prow - xi_tail)),
                   (xi_tail, v_bot + dv), align=None), v_bot


def _ribs(cam_w: float) -> list[Part]:
    """Five grip ribs standing RIB_PROUD into the cavity: three per flank, two on the floor."""
    wc = _cav_half(cam_w)
    out = []
    for xi in RIB_XI:
        sk = Pos(xi, -2.0) * Rectangle(RIB_W, RIB_L)
        out.append(_slab(sk, wc - RIB_PROUD, wc + 0.6))
        out.append(_slab(sk, -(wc + 0.6), -(wc - RIB_PROUD)))
    v_floor = -(CAM_H / 2 + FIT)
    sk = Pos(-2.0, v_floor + RIB_PROUD / 2) * Rectangle(FLOOR_RIB_L, RIB_PROUD)
    for sx in (1.0, -1.0):
        x0 = sx * FLOOR_RIB_X - FLOOR_RIB_W / 2
        out.append(_slab(sk, min(x0, x0 + FLOOR_RIB_W), max(x0, x0 + FLOOR_RIB_W)))
    return out


def _m2_holes(cam_w: float) -> Part:
    """Ø2.4 through both flanks at the pivot and HOLE_PITCH behind it, in the tilted frame."""
    wc, xo = _cav_half(cam_w), _shell_half(cam_w)
    tool = Part()
    for xi in (0.0, -HOLE_PITCH):
        sk = Pos(xi, 0.0) * Circle(D_M2_THRU / 2)
        tool += _slab(sk, wc - 1.0, xo + 1.0)
        tool += _slab(sk, -(xo + 1.0), -(wc - 1.0))
    return tool


def _shell(cam_w: float, t: float) -> tuple[Part, list[Part]]:
    """The U-section sock: flanks, floor, rear wall, open at the top and across the rear-upper
    corner. Returned tilted and trimmed to the flat y = Y_BED bed plane."""
    wc, xo = _cav_half(cam_w), _shell_half(cam_w)
    prof, _v_bot = _outer_profile(cam_w)
    sh = _slab(prof, -xo, xo)
    sh -= camera_envelope(cam_w, CAM_H, CAM_D, LENS_D, LENS_LEN, tilt_deg=0.0)
    v_notch = -(CAM_H / 2 + FIT) + CABLE_OPEN_FRAC * (CAM_H + 2 * FIT)
    sh -= _slab(Polygon((-80.0, v_notch), (XI_FRONT_OUT + 1, v_notch),
                        (XI_FRONT_OUT + 1, 60.0), (-80.0, 60.0), align=None), -wc, wc)
    ribs = _ribs(cam_w)
    for r in ribs:
        sh += r
    sh -= _m2_holes(cam_w)
    sh = _tilt(sh, t) & box(-40.0, Y_BED, Z_FLOOR, 40.0, 130.0, 60.0)
    return sh, [_tilt(r, t) for r in ribs]


def _rings() -> Part:
    """Two CLOSED Ø6.5 rings on the front-tip standoffs. closed=True is not a default here, it is
    the design: the shell hangs on four 1.6 mm fins, so the interface that carries it must not be
    able to spread. The part is threaded on with the standoffs out."""
    r = Part()
    for sx in (1.0, -1.0):
        r += c_clip((sx * RING_X, RING_Y), z0=RING_Z0, h=RING_H, closed=True)
    return r


def _gap_slab(cam_w: float) -> Part:
    """The air gap itself: the two slabs between the flank outer face and the ring's innermost
    material. Only the fins may cross it - checks() deletes it and counts the pieces."""
    xo = _shell_half(cam_w)
    s = Part()
    for sx in (1.0, -1.0):
        xa, xb = sorted((sx * (xo + 0.02), sx * (RING_X_IN - 0.02)))
        s += box(xa, RING_Y - RING_OD, RING_Z0 - 1.0, xb, RING_Y + RING_OD, RING_Z0 + RING_H + 1.0)
    return s


def _shell_band(shell: Part, cam_w: float, sx: float, y: float) -> tuple[float, float] | None:
    """Z range of the shell flank at this y, inside the ring's own Z band. None if absent."""
    xo = _shell_half(cam_w)
    xa, xb = sorted((sx * (xo - 1.2), sx * (xo + 0.3)))
    sl = shell & box(xa, y - 0.15, RING_Z0 + 1.0, xb, y + 0.15, RING_Z0 + RING_H - 1.0)
    if volume(sl) < EPS:
        return None
    bb = sl.bounding_box()
    return bb.min.Z, bb.max.Z


def _fin(shell: Part, cam_w: float, sx: float, yw: float) -> tuple[Part, float]:
    """One flexure fin: a horizontal plate WEB_T thick in Z and WEB_H wide in Y, spanning the gap
    from inside the flank to inside the ring, where the Ø6.5 bore cuts it off.

    Its section is a STADIUM, not a rectangle, and that is a print decision: a square -Y long face
    would be a 10 mm^2 down-face on the bed, and a chamfered one tapers to a knife edge. Rounded,
    its two long faces are Ø1.6 cylinders on a frame-X axis - horizontal arches in print
    orientation, which need no support and leave no thin tip.

    Its Z centre is the middle of the band the flank offers across the fin's WHOLE width, not the
    middle of the union: the flank is a tilted parallelogram, so its Z range shrinks as y grows,
    and centring on the union would push the fin off the front end of the flank and leave a
    tapering sliver of wall above it. Returns the fin and the wall margin it left."""
    xo = _shell_half(cam_w)
    y0, y1 = yw - WEB_H / 2, yw + WEB_H / 2
    bands = [b for b in (_shell_band(shell, cam_w, sx, y0 + i * (y1 - y0) / 4.0)
                         for i in range(5)) if b is not None]
    if bands:
        lo, hi = max(b[0] for b in bands), min(b[1] for b in bands)
    else:
        lo, hi = RING_Z0 + 1.0, RING_Z0 + RING_H - 1.0
    zc = min(max((lo + hi) / 2, RING_Z0 + 1.0 + WEB_T / 2), RING_Z0 + RING_H - 1.0 - WEB_T / 2)
    sk = Pos(yw, zc) * SlotOverall(WEB_H, WEB_T)
    x0, x1 = sorted((sx * (xo - 1.2), sx * WEB_X_OUT))
    fin = extrude(Plane.YZ.offset(x0) * sk, amount=x1 - x0)
    fin -= cylinder(sx * RING_X, RING_Y, RING_Z0 - 2.0, RING_Z0 + RING_H + 2.0, D_CLIP_BORE)
    return fin, round(min(zc - WEB_T / 2 - lo, hi - zc - WEB_T / 2), 3)


def build(variant: str = "t15_21", **overrides) -> dict[str, Part]:
    cfg = VARIANTS.get(variant, VARIANTS["t15_21"])
    p = dict(TILT=TILT, CAM_W=CAM_W)
    p.update(cfg.get("params", {}))
    p.update(overrides)
    t, cam_w = float(p["TILT"]), float(p["CAM_W"])

    shell, ribs = _shell(cam_w, t)
    part = shell + _rings()
    fins, margins = [], []
    for sx in (1.0, -1.0):
        for yw in WEB_Y:
            f, margin = _fin(shell, cam_w, sx, yw)
            fins.append(f)
            margins.append(margin)
            part += f

    assert len(part.solids()) == 1, f"{BASE} {variant}: {len(part.solids())} solids"
    part.label = BASE
    _BUILT[variant] = dict(tilt=t, cam_w=cam_w, ribs=tuple(ribs), fins=tuple(fins),
                           shell=shell, margins=tuple(margins))
    return {BASE: part}


# --- checks ------------------------------------------------------------------------------------
def _second_moment(lumps, axis: str = "z") -> float:
    """Sum of w*t^3/12 over a set of solids, t measured in `axis`. The bending stiffness of a
    short guided beam is E*I/L^3, so I is the geometry half of the isolation claim."""
    tot = 0.0
    for s in lumps:
        bb = s.bounding_box()
        w, t = (bb.size.Y, bb.size.Z) if axis == "z" else (bb.size.Z, bb.size.Y)
        tot += w * t ** 3 / 12.0
    return tot


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = "") -> list:
    part = parts[BASE]
    info = _BUILT.get(variant) or _BUILT.get("t15_21") or {}
    t = float(info.get("tilt", TILT))
    cam_w = float(info.get("cam_w", CAM_W))
    ribs = list(info.get("ribs", ()))
    fins = list(info.get("fins", ()))
    shell = info.get("shell")
    xo = _shell_half(cam_w)
    out: list = []

    # --- fabric -------------------------------------------------------------------------------
    ok, detail = single_solid(part)
    out.append(("one closed manifold solid", ok, detail))
    ok_w, _v, wd = min_wall(part, WALL, allow=tuple(ribs))
    out.append((f"min wall >= {WALL} (TPU95A)", ok_w, wd))
    over = overhangs(part, PRINT[BASE], material="TPU95A")
    out.append(("prints on its back with no support and no declared bridge", not over,
                "; ".join(over) or "none"))

    # --- the mounting interface ---------------------------------------------------------------
    for side, sx in (("right", 1.0), ("left", -1.0)):
        xy = (sx * RING_X, RING_Y)
        ok, detail = coaxial(part, xy, D_CLIP_BORE, RING_Z0, RING_Z0 + RING_H)
        out.append((f"{side} ring bore coaxial with standoff_front_tip_{side}", ok, detail))
        probe = cylinder(*xy, RING_Z0, RING_Z0 + RING_H, STANDOFF_D)
        gap = round(part.distance_to(probe), 4)
        out.append((f"{side} ring {STANDOFF_FIT} mm off the Ø{STANDOFF_D} standoff",
                    abs(gap - STANDOFF_FIT) <= 0.05 and isect(part, probe) < EPS, f"gap {gap} mm"))
        annulus = (cylinder(*xy, RING_Z0, RING_Z0 + RING_H, RING_OD)
                   - cylinder(*xy, RING_Z0 - 1, RING_Z0 + RING_H + 1, D_CLIP_BORE))
        frac = isect(part, annulus) / volume(annulus)
        out.append((f"{side} ring is a CLOSED circle, not a C-clip - no mouth anywhere in its "
                    f"{RING_H:g} mm", frac >= 0.999,
                    f"{100 * frac:.2f} % of the full Ø{D_CLIP_BORE}/Ø{RING_OD} collar present"))
    so = standoff_interference(part, STANDOFF_D)
    out.append((f"clear of every Ø{STANDOFF_D} standoff", not so, f"{so or 'none'}"))
    hits = interference(part)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))
    out.append((f"prop keep-out discs clear", prop_disc_violation(part) < EPS,
                f"{prop_disc_violation(part):.3f} mm³"))

    # --- the air gap: nothing touches, nothing seats ------------------------------------------
    out.append(("nothing seats on plate_mid at Z 9 (this part never touches it)",
                seated(part, Z_MID_TOP) == 0.0 and seats_on(part, "plate_mid", Z_MID_TOP) == 0.0,
                f"{seats_on(part, 'plate_mid', Z_MID_TOP)} mm² contact"))
    gaps = {n: d for n, d in distance_to_frame(part, near=12.0).items()
            if not n.startswith("standoff_front_tip")}
    worst = min(gaps.values()) if gaps else 99.0
    out.append((f"every frame surface except the two standoffs it rides on is >= {GAP} mm away",
                worst >= GAP - 1e-6,
                f"closest {min(gaps, key=gaps.get) if gaps else 'none'} at {worst:.3f} mm"))
    if shell is not None:
        d_ring = round(shell.distance_to(_rings()), 4)
        out.append((f"shell hangs >= {GAP} mm clear of both rings",
                    d_ring >= GAP - 0.02, f"{d_ring} mm of free travel"))
        sg = distance_to_frame(shell, near=20.0)
        out.append((f"shell clears plate_mid by >= {FLOOR_CLEAR} mm - the air gap under it",
                    sg.get("plate_mid", 99.0) >= FLOOR_CLEAR - 1e-6,
                    f"{sg.get('plate_mid', 99.0):.3f} mm"))
        out.append((f"shell clears every other frame surface by >= {GAP} mm",
                    min(sg.values()) >= GAP - 1e-6,
                    ", ".join(f"{n} {d:.3f}" for n, d in sg.items() if d < 6.0)))

    # --- THE CLAIM: the camera is on flexures, not on the frame -------------------------------
    slab = _gap_slab(cam_w)
    cut = part - slab
    n = len(cut.solids())
    out.append(("delete the air gap and the part falls into 3 pieces - shell + 2 rings, so the "
                "ONLY load path is the flexures", n == 3,
                f"{n} solid(s): {[round(s.volume, 1) for s in cut.solids()]} mm³"))
    in_gap = [s for s in (part & slab).solids()]
    i_web = _second_moment(in_gap)
    i_solid = RING_OD * RING_H ** 3 / 12.0
    ratio = i_web / i_solid if i_solid else 1.0
    k_rel = ratio  # same gap length, same modulus: stiffness scales with I
    out.append(("flexure path <= 1/100 the bending stiffness of a solid bridge across the same "
                "gap", k_rel <= 0.01,
                f"{len(in_gap)} web(s), I {i_web:.2f} mm⁴ vs {i_solid:.0f} mm⁴ solid = 1/"
                f"{1 / k_rel:.0f}"))
    out.append((f"{len(fins)} flexures, each <= {WEB_T} mm thick (the spring must stay thin)",
                len(fins) == 4 and all(round(s.bounding_box().size.Z, 3) <= WEB_T + 0.01
                                       for s in in_gap),
                f"thicknesses {[round(s.bounding_box().size.Z, 2) for s in in_gap]} mm"))
    free = round(min(s.bounding_box().size.X for s in in_gap), 3) if in_gap else 0.0
    out.append((f"free flexure length >= {GAP} mm", free >= GAP - 0.05, f"{free} mm of air spanned"))

    # --- the camera ---------------------------------------------------------------------------
    cam = camera_envelope(cam_w, CAM_H, CAM_D, LENS_D, LENS_LEN, tilt_deg=t)
    v = isect(part, cam)
    rib_v = sum(volume(r & cam) for r in ribs)
    out.append((f"{cam_w:g} mm body at {t:g}°: only the grip ribs touch it",
                EPS < v <= 90.0 and abs(v - rib_v) < 1.0,
                f"{v:.2f} mm³ of interference, {rib_v:.2f} mm³ of it ribs"))
    out.append((f"{cam_w:g} mm body at {t:g}° clears the frame", not interference(cam),
                f"{interference(cam) or 'none'}"))
    drop = Part()
    for dz in (0.0, 2.0, 4.0, 6.0, 9.0, 12.0, 15.0, 20.0):
        drop += Pos(0, 0, dz) * cam
    v_drop = isect(part, drop)
    out.append(("camera drops straight in from above between the flanks - only the ribs are in "
                "the way", v_drop - v < 1.0,
                f"{v_drop:.2f} mm³ swept down vs {v:.2f} mm³ seated"))
    for xi, nm in ((0.0, "front"), (-HOLE_PITCH, "rear")):
        sk = Pos(xi, 0.0) * Circle(D_M2_THRU / 2)
        probe = _tilt(_slab(sk, _cav_half(cam_w) - 0.2, xo + 2.0), t)
        probe += _tilt(_slab(sk, -(xo + 2.0), -(_cav_half(cam_w) - 0.2)), t)
        out.append((f"M2 {nm} screw hole clear through both flanks", isect(part, probe) < EPS,
                    f"{isect(part, probe):.3f} mm³"))

    # --- what the camera can see --------------------------------------------------------------
    worst_fov = max((round(isect(part, fov_wedge(a, cam_w)), 3), a)
                    for a in (0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0))
    out.append(("nothing inside the 50° half-angle FOV anywhere in 0-20° of tilt",
                worst_fov[0] < EPS, f"worst {worst_fov[0]} mm³ at {worst_fov[1]:g}°"))
    v = isect(part, fov_wedge(t, cam_w))
    out.append((f"FOV clear at the moulded {t:g}° itself", v < EPS, f"{v:.3f} mm³"))

    # --- envelope -----------------------------------------------------------------------------
    hi = part & box(-40.0, 70.0, Z_TOP_UNDER, 40.0, 125.0, 60.0)
    hx = max(abs(hi.bounding_box().min.X), abs(hi.bounding_box().max.X)) if volume(hi) > EPS else 0.0
    out.append((f"above Z {Z_TOP_UNDER:g} only the shell, inside the fork waist (|x| <= 14.0)",
                hx <= 14.0, f"|x| max {hx:.3f} mm, {volume(hi):.0f} mm³ above the top plate"))
    v = sum(isect(part, cylinder(sx * RING_X, RING_Y, 31.7, 33.75, 12.0)) for sx in (1, -1))
    out.append(("leaves the Z 31.7-33.75 standoff band free for side_panel_system", v < EPS,
                f"{v:.3f} mm³"))
    bb = part.bounding_box()
    out.append(("bed plane is the flat rear face at y 83.0", abs(bb.min.Y - Y_BED) < 1e-6,
                f"y {bb.min.Y:.3f}-{bb.max.Y:.3f}, Z {bb.min.Z:.3f}-{bb.max.Z:.3f}"))
    out.append((f"ring feet {FLOOR_CLEAR} mm above plate_mid", abs(bb.min.Z - Z_MID_TOP - FLOOR_CLEAR) < 1e-6,
                f"min Z {bb.min.Z:.3f}"))
    vol = part.volume / 1000.0
    out.append(("volume 3-9 cm³", 3.0 <= vol <= 9.0, f"{vol:.2f} cm³"))
    return out
