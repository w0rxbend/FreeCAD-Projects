"""Bolted side plates with a 5 deg V-detent tilt fan for a 19 / 21 / 22 mm FPV camera.

Nothing else in the set mounts this way. Every other camera holder in this frame hangs off the two
Ø6 front-tip standoffs: a clip, a sleeve or a C-channel that is held by friction and by the standoff
bolts, and whose tilt is set by how hard you do up an M2 screw in a smooth arc slot. That tilt walks.
After a hard landing the friction joint slips and the horizon is somewhere else.

This one does the opposite of all of it:

  * It NEVER TOUCHES A STANDOFF. Two flat PETG blades bolt to the **fwd_30p5** M3 pair at
    (+/-15.25, 76.75) through plate_mid - holes no other accessory claims - and stand up in the bay
    beside the camera. The standoff shafts stay bare, so the frame comes apart normally.
  * The tilt is POSITIVELY INDEXED, not clamped. Each blade carries a fan of seven 90 deg V-grooves
    radiating from the CAM_PIVOT axis at a 5.0 deg pitch; the swappable cradle carries one matching
    V-rib. The rib sits in a groove and the joint cannot rotate at all until you back the clamp screw
    out far enough to lift the rib clear. 0 / 5 / 10 / 15 / 20 / 25 deg, repeatable, and a crash
    cannot move it by 2 deg without shearing the rib.
  * 0-25 deg is the LONG-RANGE BAND. camera_pod's arc starts at 15 deg and camera_pod_22's hood is
    fixed; nothing in the set could point a 7-inch cruiser's camera at 0-10 deg for a level,
    low-drag cruise. This can, and it indexes the whole way.
  * The camera size lives in ONE cheap part. The blades never change: the detent interface, the
    pivot recess and the clamp slot are identical for all three variants. Only the cradle's flank
    spacing moves, so a new camera costs under 4 g of PETG, not a new bracket.

Rigid on purpose. This is the stiff, repeatable end of the lineup - the one to pair with a
soft-mounted flight controller, where the damping belongs.
"""

from math import cos, radians, sin

from build123d import (Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, Sketch, Vector, extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_detent_bracket"
TITLE = "Camera detent bracket (5 deg indexed tilt, 19 / 21 / 22 mm)"
MATERIAL = "PETG"
# One bay holds one camera, so every other camera holder is mutually exclusive with this one -
# not because they would foul (this one touches no standoff, so most of them physically could
# coexist) but because there is only one camera to hold. `camera_visor` and `lens_cover` are NOT
# on the list: they dress the lens mouth, this leaves the lens mouth empty, and the
# "coexists with" check below measures that rather than claiming it.
EXCLUSIVE = ("camera_pod", "camera_pod_22", "camera_damped_cradle", "camera_standoff_sling",
             "camera_hoop_guard")

# --- variants: one blade pair, three cradles ----------------------------------------------------
# The blades are byte-for-byte identical in all three; only the cradle's flank spacing changes, so
# the detent interface (recess, groove fan, clamp slot) never moves. That is the whole point of
# splitting the camera size out into its own part.
VARIANTS = {
    "cam19": {"params": {"CAM_W": 19.0, "CAM_H": 19.0, "CAM_D": 19.0, "LENS_D": 12.0},
              "notes": "19 mm nano cradle: flanks at |x| 9.80, 3.15 mm thick. The lightest of the three."},
    "cam21": {"params": {"CAM_W": 21.0, "CAM_H": 22.0, "CAM_D": 24.0, "LENS_D": 14.0},
              "notes": "21 mm micro cradle: flanks at |x| 10.80, 2.15 mm thick. The stock size."},
    "cam22": {"params": {"CAM_W": 22.0, "CAM_H": 22.0, "CAM_D": 24.0, "LENS_D": 14.0},
              "notes": "22 mm cradle (Foxeer Mini Cat 3 class): flanks at |x| 11.30, 1.65 mm thick - "
                       "still over the 1.5 mm PETG wall, and the widest body the blades will take."},
}
ASSEMBLY_VARIANT = "cam21"

PRINT = {"detent_plate_left": (-1, 0, 0), "detent_plate_right": (1, 0, 0), "detent_cradle": (0, -1, 0)}
MOUNTS = {"detent_plate_left": ("plate_mid top face Z 9 (the blade foot)",
                         "Ø3.2 fwd_30p5 hole (-15.25, 76.75) through plate_mid"),
          "detent_plate_right": ("plate_mid top face Z 9 (the blade foot)",
                          "Ø3.2 fwd_30p5 hole (15.25, 76.75) through plate_mid"),
          "detent_cradle": ("the two blades' CAM_PIVOT recesses and V-groove fans (no frame contact)",)}
HARDWARE = ("2 x M3 x 8 button head (UP from under plate_mid through the fwd_30p5 hole into the "
            "self-tapped Ø2.5 boss in each blade foot - 5.0 mm of thread in PETG, no nut, and the "
            "head lands under the mid plate where nothing else is)",
            "2 x M3 x 12 button head (clamp screws, through each blade's arc slot into the "
            "cradle's self-tapping boss - 6.5 mm of thread in PETG)",
            "2 x M2 camera side screws - the camera's own, into the cradle flanks")
NOTES = {
    "detent_plate_left": "Bolts to the LEFT fwd_30p5 hole and touches no standoff. Prints flat on its own "
                  "outer face (-X): the groove fan, the pivot recess, the M2-head arc pocket, the "
                  "lightening eye and the clamp slot are ALL cut into the one up-facing side, so it "
                  "needs no support anywhere - unlike camera_pod, which prints on its back and has to "
                  "justify two lintels. The blade is 5.5 mm thick because that outer face has to be "
                  "ONE plane and the tapped Ø2.5 boss at x 15.25 needs 1.5 mm of wall outboard of it; "
                  "the mass comes back out as pockets on the up-facing side, which are free. Bending "
                  "stiffness goes as the cube of the thickness, which is the whole argument for "
                  "spending the material here rather than on a thicker cradle.",
    "detent_plate_right": "Mirror of detent_plate_left; prints flat on its +X outer face.",
    "detent_cradle": "To change tilt: slacken ONE M3 per side about two turns, lift the cradle until the rib "
              "clears the fan, click it to the next tooth and retighten. The rib carries the moment; "
              "the screw only clamps. Prints on its back (-Y); the V-rib's 90 deg included angle gives "
              "45 deg flanks, so it bridges itself.",
}

# --- parameters (mm, frame coordinates; the pivot is CAM_PIVOT = (0, 100, 27)) -------------------
PET = MATERIALS["PETG"]
X_IN, X_OUT = 12.95, 18.45      # blade inboard / outboard faces (right side; left is mirrored)
# 5.5 mm is not styling. The blade prints FLAT ON ITS OUTER FACE, so that face has to be ONE plane -
# any local thinning would leave a face hanging over the bed - and the tapped Ø2.5 boss on the frame
# hole at x 15.25 needs 1.5 mm of wall outboard of it, which puts that plane at x >= 18.0. So the
# whole blade carries the thickness its own foot needs, and the mass comes back out as pockets and
# slots cut into the UP-facing inboard side, which cost nothing to print. The pay-off is a genuinely stiff blade - the stiffness of a cantilever goes as
# the cube of its thickness, so the blade is where the material is worth spending.
HUB_R = 5.7            # 1.55 mm of rim round the Ø8.3 pivot recess
PLATE_Y1 = 105.7       # forward end, 0.3 mm short of the y 106-112 standoff band; the measured 3D
                       # gap to the Ø6 front-tip shaft is reported by checks()
FOOT_Y = (70.0, 84.0)  # the foot is simply the blade run down to plate_mid's top face; its
                       # outboard 1.2 mm strip overhangs the plate edge outside y 74-82, which is
                       # air, and checks() reports the seated area that is left
FOOT_Z1 = 14.0         # top of the inboard foot ear, and the depth of the tapped M3 boss
EAR_X = (12.4, 13.2)   # the ear puts 1.6 mm of wall inboard of the tapped boss. It is the only
EAR_Y = (73.0, 80.5)   # part of a blade that crosses its own inboard face, and the cradle's arm
EAR_GAP = 0.5          # swings over it at 25 deg - this is the gap checks() proves at every detent
BOLT_XY = (15.25, 76.75)   # the fwd_30p5 forward pair - unclaimed by any other module

FAN_R = (16.0, 22.0)   # V-groove fan: 0.50 mm land at R 16 is the printability floor for a
FAN_PITCH = 5.0        # 5.0 deg pitch with a 0.9 mm tooth - never open the pitch below this
FAN_STEPS = 7          # grooves at 0, 5, 10, 15, 20, 25, 30 deg
TOOTH_W, TOOTH_D = 0.9, 0.45   # a TRUE 90 deg V 0.9 mm wide is 0.45 deep - the brief's
                       # "0.7 deep" cannot also be 90 deg at that width, and the 0.50 mm
                       # land at R 16 it quotes is the 0.9 mm figure, so width wins
RIB_W, RIB_H = 0.80, 0.40      # the rib seats on the groove FLANKS, never bottoms out
RIB_R = (16.5, 21.5)   # the cradle's single matching rib, 5 mm shorter than the fan at both ends

SLOT_R = 26.0          # clamp screw arc radius (clear of the fan band by 2.2 mm)
SLOT_W = 3.6
CLAMP_OFF = -4.0       # the clamp sits 4 deg ABOVE the rib, which keeps the boss out of the foot's
                       # airspace at 25 deg and under plate_top at 0 deg
TILT_RANGE = (0.0, 25.0)
TILT_STEPS = tuple(float(t) for t in range(0, 26, 5))
DEFAULT_TILT = 0.0     # what build() installs; every step in TILT_STEPS is checked

PIVOT_BOSS = (8.0, 5.0, 1.1)   # OD, ID (swallows the M2 head), proud of the cradle flank
PIVOT_RECESS = (8.3, 1.8)      # bore, depth into the blade's inboard face
HOLE_PITCH = 6.0               # camera M2 side-screw spacing
M2_SLOT_W = 5.2                # arc POCKET in the blade clearing the second M2 head
EYE_R, EYE_W = 12.3, 4.4       # lightening eye: the widest round pocket that keeps 1.5 mm to
                               # the M2 pocket at R 8.6, to the fan at R 16 and to both radial
                               # edges of the blade. An arc slot here would break out of the
                               # t = 35 deg edge, which is what the first cut of this did
R_OUT = 29.3                   # blade outer radius over the clamp band (1.5 mm past the slot)
POCKET_D = 2.0                 # depth of the inboard lightening pockets
R_FAN_OUT = 23.8               # blade outer radius over the fan band
CLAMP_BOSS_D = 5.5             # Ø2.5 self-tapping PETG boss, 1.5 mm wall
CLAMP_TAP = 7.0                # total M3 tap depth: flank + a boss projecting inboard into the
                               # empty air behind the camera. 6.5 mm of thread for an M3 x 12
SPINE_Y1 = 75.2                # front of the cradle's back strap; its REAR face is REAR_Y,
SPINE_Z = (27.0, 32.5)         # computed from the clamp boss so the bed face is one plane


# --- geometry helpers -----------------------------------------------------------------------
PY, PZ = CAM_PIVOT[1], CAM_PIVOT[2]
_YZ0 = Plane(Vector(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))  # sketch u -> frame Y, v -> frame Z


def _yz(sk: Sketch, x0: float, x1: float) -> Part:
    """Extrude a YZ sketch (u = frame Y, v = frame Z) from frame x = x0 to x = x1.

    It grows SYMMETRICALLY about the midplane on purpose: a one-sided extrude follows the sketch
    face's own normal, so a Polygon wound clockwise would quietly come out on the far side of the
    frame. Extruding both ways from the midplane lands on x0..x1 whatever the winding is."""
    mid = (x0 + x1) / 2
    return extrude(Plane(Vector(mid, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * sk,
                   amount=abs(x1 - x0) / 2, both=True)


def _part(shape) -> Part:
    """Booleans between a Part and an intersected Compound can come back as a Compound;
    the exporter contract says Part, so normalise once here."""
    return shape if isinstance(shape, Part) else Part(shape.wrapped)


def _pol(r: float, t: float) -> tuple[float, float]:
    """(y, z) at radius r and detent angle t from the pivot; t = 0 points straight aft, +t down."""
    a = radians(t)
    return PY - r * cos(a), PZ - r * sin(a)


def _sector(r: float, t0: float, t1: float, steps: int = 10) -> Sketch:
    """Disc of radius r about the pivot, clipped to the angular band t0..t1."""
    fan = [_pol(2.2 * r, t0 + (t1 - t0) * i / steps) for i in range(steps + 1)]
    return (Pos(PY, PZ) * Circle(r)) & Polygon((PY, PZ), *fan, align=None)


def _vee(t: float, r0: float, r1: float, w: float, d: float, x_face: float, out: float = 1.0) -> Part:
    """A 90 deg V prism of face width `w` and height `d` running from radius r0 to r1 at angle t,
    its base on the plane x = x_face and its apex `d` further along +x (out = +1) or -x.

    Subtracted from the blade it IS the detent groove; added to the cradle it IS the rib. One
    generator, so the two halves of the joint cannot drift apart."""
    c, s_ = cos(radians(t)), sin(radians(t))
    axis = Vector(0.0, -c, -s_)          # outward along the tooth, in the YZ plane
    across = Vector(0.0, -s_, c)
    ym, zm = _pol((r0 + r1) / 2, t)
    pl = Plane(Vector(x_face, ym, zm), x_dir=across * out, z_dir=axis)
    over = 0.25                          # run the base past the face so the cut is clean
    tri = Polygon((-(w / 2 + over), over), (w / 2 + over, over), (0.0, -d), align=None)
    # both=True for the same reason as _yz: the winding of `tri` must not decide which way the
    # tooth grows, or the whole fan lands inboard of its own radii.
    return extrude(pl * tri, amount=(r1 - r0) / 2, both=True)


def _arc_band(r: float, w: float, t0: float, t1: float, steps: int = 16) -> Sketch:
    """Annular slot of width w on radius r, from t0 to t1 (a real arc, not a chord)."""
    outer = [_pol(r + w / 2, t0 + (t1 - t0) * i / steps) for i in range(steps + 1)]
    inner = [_pol(r - w / 2, t1 + (t0 - t1) * i / steps) for i in range(steps + 1)]
    band = Polygon(*outer, *inner, align=None)
    for t in (t0, t1):
        band += Pos(*_pol(r, t)) * Circle(w / 2)
    return band


# --- the blade ------------------------------------------------------------------------------
FAN_T = tuple(i * FAN_PITCH for i in range(FAN_STEPS))   # 0, 5, ... 30 deg
CLAMP_YZ = _pol(SLOT_R, CLAMP_OFF)                       # clamp boss centre, cradle frame
REAR_Y = CLAMP_YZ[0] - CLAMP_BOSS_D / 2                  # the cradle's flat print bed face
SLOT_T = (CLAMP_OFF - 0.5, CLAMP_OFF + TILT_RANGE[1] + 0.5)
SECTOR_PAD = 7.5   # how far the blade's outline runs past the slot's end caps: at R 26
                   # that is 3.39 mm of arc, so the 1.8 mm cap still keeps a 1.59 mm rim
M2_SLOT_T = (-1.0, TILT_RANGE[1] + 1.0)


def _blade() -> Part:
    """The right-hand blade, as installed. The left is its mirror."""
    sk = _sector(R_OUT, SLOT_T[0] - SECTOR_PAD, SLOT_T[1] + SECTOR_PAD) + _sector(R_FAN_OUT, -5.0, 35.0)
    sk += Pos(PY, PZ) * Circle(HUB_R)
    # Foot and web in one piece: full depth on plate_mid from y 70 to 84, with the rear-top
    # corner cut back at 45 deg - nothing needs material there, it is 1.5 g of PETG, and it
    # stops the foot reading as a block bolted to a blade.
    sk += Polygon((FOOT_Y[0], Z_MID_TOP), (FOOT_Y[1], Z_MID_TOP), (FOOT_Y[1], 15.5),
                  (73.5, 15.5), (FOOT_Y[0], 12.0), align=None)
    blade = _yz(sk, X_IN, X_OUT)
    # The inboard ear is the ONLY thing that reaches past the blade's inboard face, and it exists
    # for one reason: the M3 at x 15.25 needs 1.5 mm of wall on its inboard side too. It is a raised
    # pad on the up-facing side in print orientation, and checks() proves the cradle clears it
    # by EAR_GAP at every detent, 25 deg included - that is the tightest gap in the assembly.
    blade += box(EAR_X[0], EAR_Y[0], Z_MID_TOP, EAR_X[1], EAR_Y[1], FOOT_Z1)

    bx, by = BOLT_XY
    blade -= cylinder(bx, by, Z_MID_TOP - 1.0, FOOT_Z1, PET["m3_tap"])   # M3 self-tapped, 5.0 mm
    blade -= _yz(_arc_band(HOLE_PITCH, M2_SLOT_W, *M2_SLOT_T), X_IN - 0.5, X_IN + PIVOT_RECESS[1])
    blade -= _yz(Pos(PY, PZ) * Circle(PIVOT_RECESS[0] / 2), X_IN - 0.5, X_IN + PIVOT_RECESS[1])
    blade -= _yz(_arc_band(SLOT_R, SLOT_W, *SLOT_T), X_IN - 1.0, X_OUT + 1.0)
    blade -= _yz(Pos(*_pol(EYE_R, 12.0)) * Circle(EYE_W / 2), X_IN - 0.5, X_IN + POCKET_D)
    for t in FAN_T:
        blade -= _vee(t, FAN_R[0], FAN_R[1], TOOTH_W, TOOTH_D, X_IN)
    return _part(blade)


# --- the cradle -----------------------------------------------------------------------------
def _cradle(cam_w: float, cam_h: float, tilt: float) -> Part:
    """One U-piece: two flanks joined by the back strap, built untilted and then rotated to `tilt`
    about the CAM_PIVOT axis, exactly as the rib indexes it."""
    x_in = cam_w / 2 + PET["fit"]
    flank_t = X_IN - x_in
    # Each lobe is extruded and fused as a SOLID: adding overlapping faces inside one Sketch only
    # splits them at the seam, and the extrusion then comes out as separate solids.
    # The arm runs 2 mm past the body's rear edge and covers its Z span there, so the two fuse
    # and the body has no rearward face left hanging above the print bed.
    flank = _yz(Pos(94.25, 26.5) * Rectangle(18.5, 15.0), x_in, X_IN)    # y 85..103.5, Z 19..34
    # The arm's underside is a shallow V: (87, 18) -> (80, 24) -> (REAR_Y, 27). The rear leg
    # lifts the tail so that at 25 deg it swings OVER the blade's foot ear rather than into
    # it, and the front leg is held under 45 deg so it is not an overhang on its own bed.
    flank += _yz(Polygon((REAR_Y, 27.0), (REAR_Y, 32.5), (87.0, 34.0), (87.0, 18.0), (80.0, 24.0),
                         align=None), x_in, X_IN)                        # the rib arm
    flank += _yz(Pos(PY, PZ) * Circle(HUB_R - 0.2), x_in, X_IN)          # pivot lobe
    flank += _vee(0.0, RIB_R[0], RIB_R[1], RIB_W, RIB_H, X_IN)            # the detent rib
    flank += _yz(Pos(PY, PZ) * (Circle(PIVOT_BOSS[0] / 2) - Circle(PIVOT_BOSS[1] / 2)),
                 X_IN, X_IN + PIVOT_BOSS[2])                              # pivot boss
    cy, cz = CLAMP_YZ
    flank += _yz(Pos(cy, cz) * Circle(CLAMP_BOSS_D / 2), X_IN - (CLAMP_TAP - flank_t), X_IN)
    flank -= _yz(Pos(cy, cz) * Circle(PET["m3_tap"] / 2), X_IN - CLAMP_TAP, X_IN + 0.1)
    for y in (PY, PY - HOLE_PITCH):                                       # camera M2 side screws
        flank -= _yz(Pos(y, PZ) * Circle(D_M2_THRU / 2), x_in - 1.0, X_IN + PIVOT_BOSS[2] + 1.0)
    cradle = flank + flank.mirror(Plane.YZ)
    cradle += _yz(Pos((REAR_Y + SPINE_Y1) / 2, sum(SPINE_Z) / 2)
                  * Rectangle(SPINE_Y1 - REAR_Y, SPINE_Z[1] - SPINE_Z[0]), -X_IN, X_IN)
    return _part(cradle.rotate(Axis(Vector(*CAM_PIVOT), (1, 0, 0)), tilt) if tilt else cradle)


def build(variant: str = ASSEMBLY_VARIANT, CAM_W: float = 21.0, CAM_H: float = 22.0,
          CAM_D: float = 24.0, LENS_D: float = 14.0, TILT: float = DEFAULT_TILT,
          **overrides) -> dict[str, Part]:
    # Labels carry the module name. "plate_left" would sit in dist/ beside the frame's own
    # plate_bottom / plate_mid / plate_top, and a bare "cradle" collides with any other module
    # that grows one; every sibling here prefixes, so this does too.
    blade = _blade()
    parts = pair(blade, "detent_plate")
    cradle = _cradle(CAM_W, CAM_H, TILT)
    cradle.label = "detent_cradle"
    parts["detent_cradle"] = cradle
    return parts


# --- checks ---------------------------------------------------------------------------------
def _coax_x(part: Part, yz: tuple[float, float], d: float, x0: float, x1: float,
            tol: float = 0.05) -> tuple[bool, str]:
    """coaxial() for a bore on an X axis: _fit.coaxial only probes vertical ones, and every
    camera-screw and pivot bore in this module runs across the frame."""
    y, z = yz
    bore = _yz(Pos(y, z) * Circle((d - tol) / 2), x0, x1)
    ring = _yz(Pos(y, z) * (Circle(d / 2 + tol + 0.6) - Circle(d / 2 + tol)), x0, x1)
    inside, around = isect(part, bore), isect(part, ring)
    return (inside < EPS and around > EPS,
            f"Ø{d} on X at (y {y:.3f}, Z {z:.3f}): {inside:.4f} mm³ in bore, {around:.1f} mm³ round it")


def _fan_band() -> Part:
    """The detent band, handed to min_wall as a DECLARED thin feature.

    The 0.50 mm land between two 0.9 mm grooves at R 16 is the one place on the blade thinner than
    a PETG wall, and it is not a wall: it is the material left between two cuts in a 5.5 mm slab,
    supported on all four sides, and it is what makes a 5 deg index possible at all. It is measured
    for real by the "land between grooves" row, which is an exact number, not a sample. Everything
    else on the blade still has to clear 1.5 mm.
    """
    ring = Pos(PY, PZ) * (Circle(FAN_R[1] + 0.9) - Circle(FAN_R[0] - 0.9))
    fan = [_pol(2.2 * (FAN_R[1] + 0.9), -8.0 + 46.0 * i / 10) for i in range(11)]
    band = ring & Polygon((PY, PZ), *fan, align=None)
    return _yz(band, X_IN - 0.4, X_IN + TOOTH_D + 0.4)


_NEIGHBOURS: dict[str, dict[str, Part]] = {}


def _neighbours() -> dict[str, dict[str, Part]]:
    """The two camera accessories this one is NOT exclusive with, built once and cached.

    The module's claim is that it leaves the lens mouth completely free - "nothing ahead of
    y 104" - so a visor or a lens cover still goes on. That is a measurable claim, so it is
    measured against the real parts rather than asserted in a docstring. Imported inside the
    function: checks() is the only thing that needs them, and nothing else in this module
    depends on another accessory."""
    if not _NEIGHBOURS:
        from tigerbee.accessories import camera_visor, lens_cover
        _NEIGHBOURS["camera_visor"] = camera_visor.build()
        _NEIGHBOURS["lens_cover"] = lens_cover.build()
    return _NEIGHBOURS


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str = ASSEMBLY_VARIANT):
    cam_w = VARIANTS[variant]["params"]["CAM_W"]
    cam_h = VARIANTS[variant]["params"]["CAM_H"]
    cam_d = VARIANTS[variant]["params"]["CAM_D"]
    lens_d = VARIANTS[variant]["params"]["LENS_D"]
    pr, pl = parts["detent_plate_right"], parts["detent_plate_left"]
    plates = pr + pl
    out = []

    for name, part in parts.items():
        ok, detail = single_solid(part)
        out.append((f"{name}: one valid solid", ok, detail))
        hits = interference(part)
        out.append((f"{name}: no frame interference", hits == [], str(hits)))
        so = standoff_interference(part)
        out.append((f"{name}: clear of the Ø6 standoff shafts", so == [], str(so)))
        v = prop_disc_violation(part)
        out.append((f"{name}: outside the 7-inch prop discs", v < EPS, f"{v:.3f} mm³"))
        allow = (_fan_band(),) if name.startswith("plate") else ()
        ok_w, _v, det = min_wall(part, PET["wall"], allow)
        out.append((f"{name}: min wall >= {PET['wall']}"
                    + (" (outside the declared detent band)" if allow else ""), ok_w, det))

    d = distance_to_frame(pr)
    tips = {k: v for k, v in d.items() if "front_tip" in k or "standoff" in k}
    gap = min(tips.values()) if tips else 99.0
    out.append(("plate_right: >= 0.2 mm from every standoff (it touches none)", gap >= 0.2,
                f"{gap:.3f} mm, nearest {min(tips, key=tips.get) if tips else 'none within 10 mm'}"))

    for lbl, sign in (("detent_plate_right", 1.0), ("detent_plate_left", -1.0)):
        ok, det = coaxial(parts[lbl], (sign * BOLT_XY[0], BOLT_XY[1]), PET["m3_tap"], Z_MID_TOP,
                          FOOT_Z1 - 0.5)
        out.append((f"{lbl}: tapped M3 boss coaxial with the fwd_30p5 hole", ok, det))
        area = seats_on(parts[lbl], "plate_mid", Z_MID_TOP)
        out.append((f"{lbl}: seated on plate_mid at Z 9", area >= 60.0, f"{area} mm²"))

    sweep = tilt_sweep(cam_w, *TILT_RANGE, height=cam_h, depth=cam_d, lens_d=lens_d)
    v = isect(plates, sweep)
    out.append(("blades clear the whole 0-25 deg camera sweep", v < EPS, f"{v:.3f} mm³"))
    v = isect(_yz(Pos((REAR_Y + SPINE_Y1) / 2, sum(SPINE_Z) / 2)
                  * Rectangle(SPINE_Y1 - REAR_Y, SPINE_Z[1] - SPINE_Z[0]), -X_IN, X_IN), sweep)
    out.append(("the cradle's back strap clears the sweep too", v < EPS, f"{v:.3f} mm³"))

    rib0 = _vee(0.0, RIB_R[0], RIB_R[1], RIB_W, RIB_H, X_IN)
    ribs = rib0 + rib0.mirror(Plane.YZ)
    pivot_axis = Axis(Vector(*CAM_PIVOT), (1, 0, 0))
    ear = box(EAR_X[0] - EAR_GAP, EAR_Y[0] - EAR_GAP, Z_MID_TOP, X_IN, EAR_Y[1] + EAR_GAP,
              FOOT_Z1 + EAR_GAP)
    ear_guard = ear + ear.mirror(Plane.YZ)     # the ear grown by EAR_GAP on every free side
    worst_cam, worst_lock, worst_seat, worst_hole, worst_ear = 0.0, 1e9, 0.0, "", 0.0
    for t in TILT_STEPS:
        cra = _cradle(cam_w, cam_h, t)
        worst_cam = max(worst_cam, isect(cra, camera_envelope(cam_w, cam_h, cam_d, lens_d, tilt_deg=t)))
        for yz, nm in ((_pol(0.0, 0.0), "pivot"), (_pol(HOLE_PITCH, t), f"6 mm hole @ {t:g}")):
            ok, det = _coax_x(cra, yz, D_M2_THRU, -X_IN + 0.2, X_IN - 0.2)
            if not ok:
                worst_hole = f"{nm}: {det}"
        worst_seat = max(worst_seat, isect(ribs.rotate(pivot_axis, t), plates))
        worst_ear = max(worst_ear, isect(cra, ear_guard))
        for nudge in (-2.0, 2.0):
            worst_lock = min(worst_lock, isect(ribs.rotate(pivot_axis, t + nudge), plates))
    out.append((f"camera envelope free of the cradle at {len(TILT_STEPS)} detents", worst_cam < EPS,
                f"worst {worst_cam:.3f} mm³"))
    out.append(("both M2 bores on the pivot axis and the 6 mm arc at every detent", worst_hole == "",
                worst_hole or f"{2 * len(TILT_STEPS)} bores true within 0.05"))
    out.append(("rib drops into every groove free (0.05 mm per flank)", worst_seat < EPS,
                f"worst {worst_seat:.4f} mm³"))
    out.append((f"cradle clears the blades' inboard foot ears by >= {EAR_GAP} mm at every detent",
                worst_ear < EPS, f"worst {worst_ear:.3f} mm³ inside the grown guard"))
    out.append(("DETENT LOCKS: 2 deg off a tooth the RIB ITSELF fouls the blade", worst_lock >= 0.2,
                f"worst rib/blade interference when nudged 2 deg: {worst_lock:.3f} mm³"))

    whole = plates + parts["detent_cradle"]
    for nb, nb_parts in _neighbours().items():
        v = sum(isect(whole, q) for q in nb_parts.values())
        out.append((f"coexists with {nb} - the lens mouth is left to it", v < EPS,
                    f"{v:.3f} mm³ against {len(nb_parts)} part(s)"))

    angles = [t for t in FAN_T]
    steps = [round(b - a, 9) for a, b in zip(angles, angles[1:])]
    land = radians(FAN_PITCH) * FAN_R[0] - TOOTH_W
    out.append((f"{FAN_STEPS} groove centres exactly {FAN_PITCH} deg apart",
                all(abs(s - FAN_PITCH) < 1e-6 for s in steps), str(steps)))
    out.append(("land between grooves at R 16 >= 0.45", land >= 0.45, f"{land:.3f} mm"))

    for t in range(0, int(TILT_RANGE[1]) + 1, 5):
        v = sum(isect(p, fov_wedge(float(t), cam_w=cam_w)) for p in parts.values())
        out.append((f"nothing in the field of view at {t} deg", v < EPS, f"{v:.3f} mm³"))

    for lbl, part in parts.items():
        bad = overhangs(part, PRINT[lbl], material="PETG")
        out.append((f"{lbl}: prints on {PRINT[lbl]} without support", bad == [], str(bad)))
    return out
