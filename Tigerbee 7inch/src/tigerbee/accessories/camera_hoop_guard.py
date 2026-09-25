"""Nose-horn camera guard - a bolted TPU holder that puts sacrificial material AHEAD of the glass.

The frame's carbon nose tip (plate_mid, y 116) ends level with the camera bezel (y 116.25 at 0 deg
tilt), so on a flat nose-in landing the LENS is the most forward thing on the aircraft and it takes
the hit. Every other camera part in this catalogue - `camera_pod`, `camera_pod_22`, `camera_visor`,
`lens_cover` - holds or shades the camera; none of them stands in front of it.

This one does. Two rails bolt to the fwd_30p5 M3 pair on plate_mid, run forward OUTBOARD of the
sight line, and end in two crushable horns 15.75 mm ahead of the 0 deg lens tip, tied underneath by
a chin bar that stays below the field of view. A nose-in folds the horns, slides the chin, and the
bezel never reaches the ground. The horns are hollow (two Ø4/Ø3.5 cross bores through each tip) so
they buckle instead of punching the lens backwards, and the whole part is TPU95A: it is meant to
deform.

It is NOT a pod. The camera is carried on the standard two-M2-per-side interface - a Ø2.4 pivot at
CAM_PIVOT and a 2.6 mm arc slot of radius 6.0 behind it - between two 2.5 mm cheeks, so the camera
is bolted straight to this part and the lens barrel over xi 10-20 is left completely free, so
`lens_cover` still clips on (measured: 0.000 mm³ against all four of its sizes). `camera_visor`
does NOT fit and is declared EXCLUSIVE: its wings sweep forward over y 117-130 at Z 22-26, |x|
11.5-15.0, which is exactly where the legs and horn tops are (40-215 mm³ of overlap depending on
the visor style). Nothing short of cutting the horns down to Z 21 would clear it, and a horn that
stops below the lens axis does not protect the lens. Tilt 0-25 deg, set by the camera's own rear
screw.

It coexists with `front_bumper` and `front_bumper_skull_jaw` (their material starts at Z 31.8 / 36.0
outboard of |x| 14.2; nothing here reaches above Z 26.0 out there) - checked, not asserted. That is
the point of anchoring to fwd_30p5 instead of the front-tip bolt heads: choosing this guard does not
force a bumper choice on you.
"""

from math import cos, radians, sin, tan

from build123d import (Axis, Circle, Cylinder, Location, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, Vector, extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_hoop_guard"
TITLE = "Nose-horn camera guard (19/21 mm, crushable horns ahead of the lens)"
MATERIAL = "TPU95A"
BASE = "camera_hoop_guard"
PRINT = {BASE: (0, -1, 0)}
VARIANTS = {
    "cam21": {"params": {"cam_w": 21.0}, "notes": "21 mm micro camera: cheek inner faces |x| 10.75"},
    "cam19": {"params": {"cam_w": 19.0}, "notes": "19 mm nano camera: cheek inner faces |x| 9.75"},
}
ASSEMBLY_VARIANT = "cam21"
EXCLUSIVE = ("camera_pod", "camera_pod_22", "camera_damped_cradle", "camera_detent_bracket",
             "camera_standoff_sling", "camera_visor", "front_bumper_feet")
MOUNTS = ("plate_mid top face Z 9 (y 73-87, |x| 10.5-17.0)",
          "M3 fwd_30p5 holes (±15.25, 76.75) through plate_mid")
HARDWARE = ("2 x M3 x 10 button head (up through plate_mid from below, into the guard)",
            "2 x M3 nyloc (dropped into the rear-loading hex slot in each foot)",
            "2 x M2 x 5 (the camera's own front/pivot screws, one per side)",
            "2 x M2 x 5 (the camera's own rear screws, through the tilt arc slots)")
NOTES = ("Prints on its BACK: bed normal (0, -1, 0), so the foot rear faces at y 73.0 lie on the "
         "bed and the horn tips point straight up - the extrusion fibres then run ALONG the impact "
         "direction, which is the orientation that makes a crushable horn crush instead of "
         "delaminating. Use a brim: the bed footprint is ~75 mm² under a 59 mm tall part. "
         "The nut slots load from the bed face, so there is no bridged nut roof anywhere. "
         "Coexists with front_bumper / front_bumper_skull_jaw (checked: nothing here is above "
         "Z 26.0 outboard of |x| 14.2, their material starts at Z 31.8). "
         "Honest caveat on the field of view: the repo's fov_wedge models a 50 deg half angle and "
         "the horns clear it at every tilt with the wedge run out to 20 mm. A real 165 deg micro "
         "camera WILL see the horns as two thin bars in the extreme lower corners - the same place "
         "the props already show. That is why the horn tips are only 3.5 mm wide and taper back "
         "from y 132; do not fatten them 'for strength'. "
         "The foot carries a 19.4 mm ear round each nut slot: the M3 bore's outboard wall is at "
         "x 16.95 and the nut flats at 18.1, so a 17.0 mm foot would have left a 0.05 mm wall. "
         "The ear overhangs plate_mid's edge by at most 1.4 mm (at y 73) and carries no load "
         "there - the bolt at x 15.25 is well inside the carbon.")

# --- camera interface (mm) -------------------------------------------------------------------
CAM_W = 21.0                 # overridden per variant; 22.0 also builds (reachable by parameter)
CHEEK_T = 2.5
SLOT_R = 6.0                 # the camera's rear M2 screw sits 6.0 behind the pivot
SLOT_W = 2.6
TILT_RANGE = (0.0, 25.0)
SLOT_DEG = (-1.0, 26.0)      # slot ends 1 deg outside the usable range so 0 and 25 are reachable
_TAN30 = tan(radians(30))
CLEAN = 2.0                  # solid material required all round the slot-plus-pivot clean zone

# --- frame interface -------------------------------------------------------------------------
BOLT_XY = (15.25, 76.75)     # fwd_30p5, plate_mid
FOOT_Y = (73.0, 87.0)
PAD_X = (10.5, 17.0)
PAD_EAR_X = 19.4             # local widening round the nut: the M3 bore's outboard face is at
PAD_EAR_Y = 82.0             # x 16.95 and the nut flats at 18.1, so 17.0 would leave a 0.05 mm
#                              wall. 19.4 keeps 1.3 mm outboard of the flats. The lip overhangs
#                              plate_mid's edge by at most 1.4 mm (at y 73, edge x 18.0).
PAD_Z = (Z_MID_TOP, 13.0)    # 9.0 -> 13.0
NUT_Z = 10.4                 # hex slot floor; 2.6 deep to the pad top face
NUT_PEAK = 5.2               # teardrop cap ahead of the hex: in print, frame +Y is UP, so the far
#                              end of the nut slot is its ROOF and a flat or 60 deg hex end there
#                              would need support. A peak at 1.25:1 does not.

# --- the rails, horns and chin -----------------------------------------------------------------
RAIL_X = (11.5, 15.0)        # outboard of the ±10.5 FOV prism, inboard of the Ø6 standoffs at x 16
HORN_Y = 132.0
HORN_Z = (14.0, 26.0)
CHIN_Y = (116.5, 132.0)      # 116.5, not 116.0: plate_mid's nose spike survives to y 116 at x ±0.1
CHIN_Z = (5.0, 10.0)
CHIN_X = 15.0
CHIN_CAP_R = 2.5             # rounded rear cap: a Ø5 arch, printable, and never a knife edge

# YZ silhouette of one rail, extruded over RAIL_X. Every rear-facing edge is steeper than 45 deg
# (|dy| > |dz|) or lies on the bed plane y 73, because in the print orientation frame -Y is DOWN.
RAIL_PTS = ((73.0, 9.0), (100.0, 9.0), (112.0, 9.6), (117.0, 5.0), (132.0, 5.0), (132.0, 20.0),
            (128.5, 26.0), (106.0, 22.0), (97.0, 21.0), (88.0, 16.0), (73.0, 20.0))
# YZ silhouette of one cheek, extruded over CHEEK_T from the camera's flank.
CHEEK_PTS = ((93.0, 18.0), (106.0, 18.0), (106.0, 29.0), (103.0, 32.0), (96.0, 33.0), (83.0, 24.0))
# (y, z, Ø) lightening / crush bores, all on frame-X axes so they print as self-supporting arches.
RAIL_BORES = ((92.0, 13.5, 5.0), (110.0, 16.0, 7.0), (120.0, 16.0, 6.5),
              (127.8, 15.5, 4.0), (126.0, 21.5, 3.0))


# --- helpers: every solid is a YZ profile extruded along +X ------------------------------------
def _yz(x: float) -> Plane:
    """Sketch plane at frame X = x whose local (x, y) are frame (+Y, +Z); extrude runs along +X."""
    return Plane(Vector(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))


def _prism(sk: Sketch, x0: float, x1: float) -> Part:
    return extrude(_yz(x0) * sk, amount=x1 - x0)


def _poly(pts, x0: float, x1: float) -> Part:
    return _prism(Polygon(*pts, align=None), x0, x1)


def _xbore(y: float, z: float, d: float, x0: float, x1: float) -> Part:
    """Ø d bore on a frame-X axis: horizontal in the print orientation, so overhangs() exempts it
    as an arch for any d <= MATERIALS['TPU95A']['arch_d'] (10.0)."""
    return _prism(Pos(y, z) * Circle(d / 2), x0, x1)


def cheek_inner(cam_w: float) -> float:
    """|x| of the cheek's inner face = the camera's own flank plus the TPU fit."""
    return cam_w / 2 + FIT


def _slot_sketch(grow: float = 0.0) -> Sketch:
    """The tilt arc slot: a chain of Ø(SLOT_W + 2 grow) discs on radius SLOT_R about the pivot,
    from SLOT_DEG[0] to SLOT_DEG[1]. Built from discs so every boundary face is a small cylinder
    on a frame-X axis - rounded ends for free, and no flat slot roof to bridge."""
    py, pz = CAM_PIVOT[1], CAM_PIVOT[2]
    r = SLOT_W / 2 + grow
    sk = Sketch()
    n = 20
    for i in range(n + 1):
        t = radians(SLOT_DEG[0] + (SLOT_DEG[1] - SLOT_DEG[0]) * i / n)
        sk += Pos(py - SLOT_R * cos(t), pz - SLOT_R * sin(t)) * Circle(r)
    return sk


def _pivot_sketch(grow: float = 0.0) -> Sketch:
    return Pos(CAM_PIVOT[1], CAM_PIVOT[2]) * Circle(D_M2_THRU / 2 + grow)


def cheek_plate(cam_w: float) -> Part:
    """The uncut cheek - what the clean-zone check measures the slot against."""
    xi = cheek_inner(cam_w)
    return _poly(CHEEK_PTS, xi, xi + CHEEK_T)


def clean_zone(cam_w: float) -> Part:
    """Slot + pivot grown by CLEAN, across the cheek: must lie entirely inside cheek_plate()."""
    xi = cheek_inner(cam_w)
    return _prism(_slot_sketch(CLEAN) + _pivot_sketch(CLEAN), xi, xi + CHEEK_T)


def chin_bar() -> Part:
    """Full-width bar under the field of view, y CHIN_Y, Z CHIN_Z, with a Ø5 rear cap."""
    y0, y1 = CHIN_Y[0] + CHIN_CAP_R, CHIN_Y[1]
    z0, z1 = CHIN_Z
    zc = (z0 + z1) / 2
    sk = Pos((y0 + y1) / 2, zc) * Rectangle(y1 - y0, z1 - z0) + Pos(y0, zc) * Circle(CHIN_CAP_R)
    return _prism(sk, -CHIN_X, CHIN_X)


def _nut_peak(bx: float, by: float, z0: float, z1: float) -> Part:
    """Teardrop cap on the forward end of the nut slot. The part prints on its back, so frame +Y
    is UP: the slot loads from the bed at y 73 and its FAR end is the roof. A hex end there is a
    60 deg overhang and a flat one is worse, so the pocket is capped with a NUT_PEAK-tall peak
    (1.46 : 1) that needs no support. It adds no rotational freedom - the nut still sits between
    the two flats at x bx +- HEX_M3_AF / 2."""
    a = HEX_M3_AF / 2                       # 2.85: the hex flats, at x = bx +- a
    yb = by + a * _TAN30                    # 1.645 ahead of the axis: where those flats end
    tri = Polygon((bx - a, yb), (bx + a, yb), (bx, by + NUT_PEAK), align=None)
    return extrude(Plane.XY.offset(z0) * tri, amount=z1 - z0)


def lens_corridor(tilt: float, d: float = 20.0, xi0: float = 10.0, xi1: float = 20.0) -> Part:
    """The airspace a lens accessory needs: a Ø d tube on the lens axis from xi0 to xi1 ahead of
    CAM_PIVOT, at this tilt. Ø20 is the Ø14 barrel plus 3 mm of clip wall per side - what
    `lens_cover` and any barrel-clamped shade actually occupy. This part must stay out of it."""
    c = (Pos(0, xi0, 0) * Cylinder(d / 2, xi1 - xi0, rotation=(-90, 0, 0), align=MIN_Z_ALIGN))
    c = c.moved(Location(Vector(*CAM_PIVOT)))
    return c.rotate(Axis(Vector(*CAM_PIVOT), (1, 0, 0)), tilt) if tilt else c


def build(variant: str = "cam21", cam_w: float = CAM_W, **overrides) -> dict[str, Part]:
    p = {"cam_w": cam_w, **overrides}
    w = p["cam_w"]
    xi = cheek_inner(w)

    half = _poly(RAIL_PTS, *RAIL_X)
    half += box(PAD_X[0], FOOT_Y[0], PAD_Z[0], PAD_X[1], FOOT_Y[1], PAD_Z[1])
    half += box(PAD_X[0], FOOT_Y[0], PAD_Z[0], PAD_EAR_X, PAD_EAR_Y, PAD_Z[1])
    half += cheek_plate(w)

    # M3 anchor: through bore, plus a hex nut slot that loads from the BED face at y 73 - a
    # rear-loading channel, not a roofed pocket, so nothing above the nut has to be bridged.
    bx, by = BOLT_XY
    cut = cylinder(bx, by, PAD_Z[0] - 1.0, PAD_Z[1] + 0.01, D_M3_THRU)
    cut += hex_pocket(HEX_M3_AF, PAD_Z[1] - NUT_Z, (bx, by, NUT_Z), rotation_deg=30.0)
    cut += box(bx - HEX_M3_AF / 2, FOOT_Y[0] - 2.0, NUT_Z, bx + HEX_M3_AF / 2, by, PAD_Z[1])
    cut += _nut_peak(bx, by, NUT_Z, PAD_Z[1])
    # camera interface: Ø2.4 pivot and the 2.6 arc slot, through the 2.5 mm cheek only
    cut += _prism(_slot_sketch() + _pivot_sketch(), xi - 1.0, xi + CHEEK_T + 1.0)
    for y, z, d in RAIL_BORES:
        cut += _xbore(y, z, d, RAIL_X[0] - 0.5, RAIL_X[1] + 0.5)
    half -= cut

    part = half + half.mirror(Plane.YZ) + chin_bar()
    part = part.clean()
    part.label = BASE
    return {BASE: part}


# --- the claims, measured ----------------------------------------------------------------------
LENS_TIP_Y = CAM_PIVOT[1] + 16.25  # 116.25: the 0 deg lens tip, _common.camera_envelope's datum
PROTECTION_MIN = 14.0              # horn tips must stand at least this far ahead of the glass
BUMPER_X, BUMPER_Z = 14.2, 31.8    # front_bumper's material starts here; we must stay under it


def _cam_w(variant: str | None) -> float:
    return float(VARIANTS.get(variant or ASSEMBLY_VARIANT, {}).get("params", {}).get("cam_w", CAM_W))


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None):
    part = parts[BASE]
    w = _cam_w(variant)
    bb = part.bounding_box()
    out = []

    ok, detail = single_solid(part)
    out.append(("one valid solid", ok, detail))
    out.append(("no frame interference", not interference(part), f"{interference(part) or 'none'}"))
    so = standoff_interference(part)
    gaps = {n: d for n, d in distance_to_frame(part, near=6.0).items() if n.startswith("standoff")}
    tip = min((d for n, d in gaps.items() if "front_tip" in n), default=99.0)
    out.append((f"clear of the Ø{STANDOFF_D} standoffs by >= 0.2 mm", not so and tip >= 0.2,
                f"overlaps {so or 'none'}, front-tip gap {tip:.3f} mm"))

    for sx in (1, -1):
        okc, d = coaxial(part, (sx * BOLT_XY[0], BOLT_XY[1]), D_M3_THRU, Z_MID_TOP, 12.0)
        out.append((f"M3 bore coaxial with fwd_30p5 ({sx * BOLT_XY[0]:+.2f}, {BOLT_XY[1]})", okc, d))

    seat = seats_on(part, "plate_mid", Z_MID_TOP)
    out.append(("seated on plate_mid at Z 9", seat >= 80.0, f"{seat} mm² contact"))
    pv = prop_disc_violation(part)
    out.append(("outside the prop keep-out discs", pv < EPS, f"{pv:.3f} mm³"))

    # (7) the critical one: the camera must see nothing of this part, at any tilt it can be set to.
    worst, worst_t = 0.0, None
    for t in list(range(0, 26, 2)) + [25]:
        v = isect(part, fov_wedge(float(t), cam_w=max(w, 21.0)))
        if v > worst:
            worst, worst_t = v, t
    margin = isect(part, fov_wedge(0.0, cam_w=max(w, 21.0), length=20.0))
    out.append(("outside the 50 deg FOV prism at every tilt 0-25 (and at 20 mm reach)",
                worst < EPS and margin < EPS,
                f"worst {worst:.3f} mm³ at {worst_t} deg, 20 mm-reach margin test {margin:.3f} mm³"))

    # (8) the chin ceiling, asserted directly rather than trusted to the wedge sampling
    inside = part & box(-10.5, 112.0, -5.0, 10.5, 133.0, 60.0)
    chin_top = inside.bounding_box().max.Z if inside is not None and inside.volume > EPS else -99.0
    out.append(("chin ceiling Z <= 10.0 inside |x| 10.5, y 112-133", chin_top <= 10.0 + 1e-6,
                f"max Z {chin_top:.3f}"))

    # (9) + the camera body itself has to fit, at every size and tilt
    sweep = isect(part, tilt_sweep(w, *TILT_RANGE))
    env = max(isect(part, camera_envelope(width=w, tilt_deg=float(t))) for t in range(0, 26, 5))
    out.append((f"{w:.0f} mm camera clears the part through tilt 0-25", sweep < EPS and env < EPS,
                f"swept volume {sweep:.3f} mm³, worst single pose {env:.3f} mm³"))

    # (10) 2.0 mm of solid all round the slot-plus-pivot clean zone
    spill = volume(clean_zone(w) - cheek_plate(w))
    out.append((f"arc slot + pivot keep {CLEAN} mm of cheek all round", spill < EPS,
                f"{spill:.3f} mm³ of the clean zone outside the cheek"))

    okw, vw, dw = min_wall(part, WALL)
    out.append((f"min wall >= {WALL}", okw, dw))
    # y 114.0, not CHIN_Y[0]: the clip face must not land 1 mm behind a lightening bore, or the
    # ray sampler measures the slab the CLIP made and reports it as a thin wall of the part.
    impact = part & box(-CHIN_X - 0.5, 114.0, CHIN_Z[0] - 1.0, CHIN_X + 0.5,
                        HORN_Y + 0.5, HORN_Z[1] + 1.0)
    oki, vi, di = min_wall(impact, WALL_IMPACT)
    out.append((f"horns + chin wall >= {WALL_IMPACT} (WALL_IMPACT)", oki, di))

    out.append((f"above the landing plane Z {LANDING_Z}", bb.min.Z >= LANDING_Z - 1e-6,
                f"min Z {bb.min.Z:.3f}"))
    over = overhangs(part, PRINT[BASE])
    out.append(("printable on its back, no unsupported overhangs", not over, "; ".join(over) or "none"))

    # (14) the protection claim itself, measured
    ahead = bb.max.Y - LENS_TIP_Y
    cam_fwd = max(camera_envelope(width=w, tilt_deg=float(t)).bounding_box().max.Y
                  for t in range(0, 26, 5))
    out.append((f"horn tips >= {PROTECTION_MIN} mm ahead of the 0 deg lens tip",
                ahead >= PROTECTION_MIN, f"{ahead:.2f} mm ahead (tips y {bb.max.Y:.1f})"))
    out.append(("no camera pose is the most forward material", cam_fwd < bb.max.Y - 1e-6,
                f"camera reaches y {cam_fwd:.2f}, guard reaches y {bb.max.Y:.2f}"))

    # the lens barrel stays free, so a barrel-clipped cover still goes on over the top
    corridor = max(isect(part, lens_corridor(float(t))) for t in range(0, 26, 5))
    out.append(("lens barrel corridor (Ø20, xi 10-20) free at every tilt", corridor < EPS,
                f"{corridor:.3f} mm³"))
    try:
        from tigerbee.accessories import build_variants
        from tigerbee.accessories import lens_cover as LC
        cov = max(isect(part, q) for v in build_variants(LC).values() for q in v.values())
        out.append(("lens_cover still fits over the top", cov < EPS, f"worst {cov:.3f} mm³"))
    except Exception as exc:  # noqa: BLE001 - a sibling that will not build is reported, not hidden
        out.append(("lens_cover still fits over the top", False, f"could not build lens_cover: {exc}"))

    # (15) the selling point: this guard leaves the nose bumpers' volume alone
    outboard = part & box(BUMPER_X, 60.0, -5.0, 40.0, 140.0, 60.0)
    top = outboard.bounding_box().max.Z if outboard is not None and outboard.volume > EPS else -99.0
    out.append((f"coexists with front_bumper: nothing above Z {BUMPER_Z} outboard of |x| {BUMPER_X}",
                top < BUMPER_Z, f"max Z {top:.3f} outboard of |x| {BUMPER_X}"))
    return out
