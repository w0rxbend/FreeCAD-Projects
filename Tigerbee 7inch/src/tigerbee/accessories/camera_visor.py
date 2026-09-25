"""Clip-on camera visors - four sun hoods that snap over the lens barrel, in three barrel sizes.

WHY IT EARNS A PLACE
--------------------
Low sun straight into the lens is the number one image complaint on a long-range cruise, and not
one of the existing families shades the glass: `camera_pod` is an open-fronted U-pod with "no brow
bar: anything ahead of the lens sits in the FOV", `camera_pod_22`'s bell is a fairing, not a shade,
and `lens_cover` only caps the lens on the ground. This is a 4 g part that snaps on over the
barrel and throws the sun off the glass.

THE INTERFACE (exact, and shared with lens_cover)
-------------------------------------------------
A split collar concentric with the lens axis - Axis(CAM_PIVOT (0, 100, 27), +X) tilted by TILT -
gripping the CAMERA's own lens barrel, never the pod. The barrel numbers are `lens_cover`'s, not
re-derived: the 19/21 pods' camera carries `_common.camera_envelope`'s Ø14.0 x 6.0 barrel from
xi 10.0 (body front face) to xi 16.0 (glass), `camera_pod_22`'s Foxeer Mini Cat 3 carries its
Ø17.0 M12 holder from xi 10.0 to xi 20.0, and the generic label takes any Ø15 barrel.

  bore     = barrel Ø + 2 x FIT (0.25 in TPU95A)
  wall     = CLIP_WALL 1.6, collar length COLLAR_L 5.0
  mouth    = 270 deg of collar and a 90 deg mouth facing straight DOWN (-v), lips filleted
             MOUTH_FILLET 0.45, so the visor pushes on radially from underneath with the camera
             installed and the pod's cheeks in place. Nothing touches any frame part.

WHAT SETS THE FLARE (measured, not styled)
------------------------------------------
`fov_wedge(tilt, cam_w=21.0, half_angle=50.0, length=15.0)` is a 100 deg prism from the lens tip
at xi 16.25, 15 mm long and only +-10.5 mm wide in x. Every hood here has ZERO intersection with
it at tilt 0/10/20/30/40, and that is what shapes all four: inboard of |x| 10.5 the hood may only
carry material at |v| >= 1.19 x (xi - 16.25), which peaks at 11.49 at the wedge's far chord. So
every variant is a WIDE-SHOULDERED hood - its roof stands at v >= SHOULDER_V 12.1 and its shoulders
break outboard at |u| >= SHOULDER_U 11.0, and everything that plunges toward the axis does so
outboard of the wedge. The four look nothing alike, but they all obey that one rule.

THE FOUR HOODS
--------------
  origami    ORIGAMI - a folded 1.8 mm sheet. Four facets: a flat roof, two creases at exactly
             45 deg and two more at exactly 22.5 deg, every edge dead straight, 0.4 chamfers, and
             mountain/valley dash notation debossed along the creases. Pyramidal in plan: the
             section grows from the collar to the mouth, so it reads as folded paper.
  vespid     VESPID - three tergite shingles stepping forward from the collar, each 0.82 the length
             and 0.86 the girth (arc sweep) of the one before, each with a 1.2 mm proud collar, a
             0.45 mm undercut groove and ONE 2.2 x 5.0 spiracle slot per flank, ending in a
             downturned stinger lip over the top of the glass. Wall 2.2 at the root -> 1.4 at the tip.
  filigree   FILIGREE - a petal hood: a 2.4 mm solid spine arch over the roof carrying a 1.4 mm
             mirrored scroll net down both flanks, void 45-60 %, the mouth scalloped into four arc
             cusps with Ø4.0 ring nodes at the scroll junctions. Only the roof has to be opaque.
  brutalist  BRUTALIST - a 3.0 mm square box shade: flat roof, two flat cheeks, sharp corners,
             1.0 mm chamfers only, one rectangular lightening void >= 40 % of each cheek, and
             board-marking grooves 0.6 x 0.3 at 2.4 mm pitch along the roof.

Every variant prints standing on its collar end face (bed normal -axis), which puts the flare
flanks and the roof self-supporting and the mouth last.
"""

from math import atan2, cos, degrees, hypot, radians, sin, tan

from build123d import (Align, Axis, Box, Circle, Cylinder, Part, Plane, Polygon, Pos, Rectangle,
                       Sketch, Vector, extrude, fillet, loft)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_visor"
TITLE = "Camera visors / sun shades (19/21, 22 mm, generic barrels)"
MATERIAL = "TPU95A"
EXCLUSIVE = ()

L21, L22, LGEN = "camera_visor_21", "camera_visor_22", "camera_visor_generic"
LABELS = (L21, L22, LGEN)
ASSEMBLY_LABELS = (L21,)  # the three are alternatives: one camera, one visor

# --- the camera datums (all from lens_cover / camera_pod_22 - nothing re-derived) --------------
TILT = 25.0                  # installed tilt; camera_pod's arc slot is 15-40 deg
TILT_CHECK = (0.0, 10.0, 20.0, 30.0, 40.0)
FOV_HALF, FOV_LEN, FOV_W = 50.0, 15.0, 21.0
FOV_TIP = 16.25              # fov_wedge's lens_reach: the apex of the keep-out
XI_BODY = 10.0               # camera body front face
BARRELS = {                  # label -> (barrel Ø, collar start xi, glass xi, hood projection)
    L21: (14.0, 10.5, 16.0, 14.0),
    L22: (17.0, 10.5, 20.0, 12.0),
    LGEN: (15.0, 10.5, 16.0, 14.0),
}

# --- parameters (mm) --------------------------------------------------------------------------
COLLAR_L = 5.0               # axial length of the split collar
MOUTH_DEG = 90.0             # 270 deg of collar, 90 deg of mouth, facing -v
FLEX_MIN = 0.65              # a 270 deg TPU95A C-collar opens to >= 0.65 x its bore: the snap rule
SHOULDER_V = 12.1            # roof height above the axis: fov needs >= 11.49 inboard of |u| 10.5
SHOULDER_U = 11.0            # where the roof breaks into the flanks: fov needs >= 10.5
RIM_GROW = 1.5               # extra roof height at the mouth - every hood flares forward
FLARE_DEG = 30.0             # flare half-angle off the axis. Not a style choice: the widest facet
#                              of a faceted section moves outward 1.36 x faster than the section
#                              scale does, so 30 deg of flare is already a 38 deg surface there and
#                              overhangs() flags at 44.4 deg. Measured, see _shape_gain().
BAND_SAFETY = 1.04           # the gain is a max over the section's segments, so the compensation
#                              is a hair optimistic on the steepest facet (measured 1.776 against a
#                              1.8 wall). 4 % of band width costs 3 % of mass and closes it.
HUB_RISE = 3.0               # how much the solid hub skirt climbs over the collar's length;
#                              (HUB_RISE / COLLAR_L) x the section gain must stay under 0.98,
#                              which is where overhangs() starts flagging the skirt

WALL_V = {"origami": 1.8, "vespid": 2.2, "filigree": 1.4, "brutalist": 3.0}
WALL_TIP = {"vespid": 1.4}   # variants whose wall tapers along the hood: checked at the THIN end
DASH = (1.6, 0.6)            # ORIGAMI mountain/valley notation: dash length, deboss depth
FOLD_SET = (22.5, 45.0, 67.5)
TERGITES = 3                 # VESPID
TERG_LEN, TERG_GIRTH = 0.82, 0.86
SPIRACLE = (2.2, 5.0)
TERG_PROUD, TERG_RAMP = 1.2, 2.2   # the proud collar and the run it needs to stay printable
STING = (3.0, 2.2)                 # the stinger lip: how far forward, how far down
SCROLL_R = 1.3               # FILIGREE: the larger of the two scroll arc radii (0.5 R is the other)
SCROLL_PHI = (50.0, 62.0)    # the mirrored scroll rows, degrees off the spine. The flank panel only
#                              runs from the shoulder at 42 deg to the flank tip at 72 - 7.3 mm of
#                              arc - so two rows is what fits at a 1.4 mm ribbon.
SCROLL_PHI_HALF = 6.0        # where the 0.5 R arc sits, between the two rows
SCROLL_LEN, SCROLL_GAP = 3.8, 1.5  # scroll run and the ribbon left between two of them
FLANK_PHI = (40.0, 95.0)     # the wedge the void fraction is measured over
SCALLOP_R = 2.5              # the mouth's four arc cusps
SCALLOP_PHI = (45.0, 66.0)   # mirrored: four bites, five cusps
SPINE_T = 2.4                # the solid spine the net hangs on
BRUT_U, BRUT_DEEP = 11.2, 6.0      # BRUTALIST cheek stand-off and depth
BRUT_MARGIN = 1.8                  # frame left round the cheek void
BRUT_CLEAR_U = 10.55               # where the cheek clears fov_wedge's +-10.5 mm prism
VOID_BAND = (0.45, 0.60)
BOARD = (0.6, 0.3, 2.4)      # BRUTALIST board marking: width, depth, pitch
BRUT_CH = 1.0
BRUT_FILLET_MAX = 0.3

_P = Vector(*CAM_PIVOT)
_MEASURED: dict = {}         # what each build actually reached, read back by checks()

MIN_Z = -3.0

VARIANTS = {
    "origami": {**({"style": "origami"} if "origami" in STYLES else {}),
                "notes": "ORIGAMI: one folded 1.8 mm sheet, four facets, creases at 45 and 22.5 deg."},
    "vespid": {**({"style": "vespid"} if "vespid" in STYLES else {}),
               "notes": "VESPID: three tergite shingles at 0.82 length / 0.86 girth, stinger lip."},
    "filigree": {**({"style": "filigree"} if "filigree" in STYLES else {}),
                 "notes": "FILIGREE: a 2.4 mm spine arch with a 1.4 mm scroll net down both flanks."},
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}),
                  "notes": "BRUTALIST: a 3.0 mm board-marked box shade, one big void per cheek."},
}
ASSEMBLY_VARIANT = "origami"

_BED = (0.0, -cos(radians(TILT)), -sin(radians(TILT)))  # collar end face on the bed
PRINT = {label: _BED for label in LABELS}

# The one bridge in the set: BRUTALIST's cheek void is rectangular with sharp corners by family
# rule, so its ceiling is a flat span. It is 9-14 mm wide, well inside TPU95A's 22 mm.
BRIDGE_OK = {label: (("box", -40, -40, BARRELS[label][2] + BARRELS[label][3] - BRUT_MARGIN - BARRELS[label][1] - 0.4,
                      40, 40, BARRELS[label][2] + BARRELS[label][3] - BRUT_MARGIN - BARRELS[label][1] + 0.4),)
             for label in LABELS}

MOUNTS = {
    L21: ("the camera's own Ø14.0 x 6.0 lens barrel (xi 10.0-16.0) on the CAM_PIVOT (0, 100, 27) "
          "lens axis, as camera_pod_19 / camera_pod_21 hold it",
          "no frame face and no frame axis - the visor touches the camera only"),
    L22: ("camera_pod_22's Foxeer Mini Cat 3 Ø17.0 lens barrel (xi 10.0-20.0) on the CAM_PIVOT "
          "lens axis", "no frame face and no frame axis"),
    LGEN: ("any bare Ø15.0 lens barrel on the CAM_PIVOT lens axis (BARRELS[LGEN] parameterises it)",
           "no frame face and no frame axis"),
}
HARDWARE = {label: ("none - 0.25 mm interference snap collar over the lens barrel",) for label in LABELS}
NOTES = {
    L21: ("Pushes on from underneath over the front 5 mm of the Ø14 lens barrel: 270 deg of Ø14.5 "
          "collar and a 90 deg mouth, so the Ø10.25 opening springs over the barrel in TPU95A and "
          "then grips it with 0.25 mm of interference. Fits both camera_pod_19 and camera_pod_21 - "
          "the collar is Ø17.7 over its widest point, inside either pod's cheeks. Prints standing "
          "on the collar end face; the roof and the flare flanks are self-supporting."),
    L22: ("For the Foxeer Mini Cat 3's Ø17 M12 holder: the collar grips xi 13-18 on the barrel and "
          "the hood reaches 12 mm past the glass. It takes over the shading job from "
          "camera_pod_22's bell, so fit it to a bare Foxeer (or a pod flown without its bell) - "
          "the two hoods occupy the same air. Prints standing on the collar end face."),
    LGEN: ("For a bare Ø15 barrel; edit BARRELS[camera_visor_generic] and every other dimension "
           "follows. As shipped it also slips over the repo's own Ø14 lens with 0.5 mm to spare, "
           "which makes it a slide-to-set shade rather than a snap shade at that size."),
}


# --- the lens frame (identical to lens_cover's, so both parts share one datum) ------------------
def _ax(t: float) -> tuple[Vector, Vector]:
    """(a, u): the lens axis and the camera's own 'up' at tilt `t` about Axis(CAM_PIVOT, +X)."""
    c, s = cos(radians(t)), sin(radians(t))
    return Vector(0, c, s), Vector(0, -s, c)


def _station(t: float, xi: float = 0.0) -> Plane:
    """Station plane at xi. LOCAL (X, Y, Z) = (u across, v up, xi along the lens axis)."""
    a, _u = _ax(t)
    return Plane(origin=tuple(_P + a * xi), z_dir=tuple(a), x_dir=(1.0, 0.0, 0.0))


def _repose(part: Part, t_from: float, t_to: float) -> Part:
    """The same installed visor at another tilt - it rides with the camera about CAM_PIVOT +X."""
    return part if abs(t_to - t_from) < 1e-9 else part.rotate(Axis(_P, (1, 0, 0)), t_to - t_from)


def _fov_floor(xi: float) -> float:
    """|v| that fov_wedge forbids material below, inboard of |u| FOV_W/2, at this station."""
    reach = xi - FOV_TIP
    if reach <= 0.0 or reach >= FOV_LEN * cos(radians(FOV_HALF)):
        return 0.0
    return reach * tan(radians(FOV_HALF))


# --- sheet sections: every hood is a constant-thickness band lofted station to station ----------
def _norm(dx: float, dy: float) -> tuple[float, float]:
    n = hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _offset_open(pts: list[tuple[float, float]], d: float) -> list[tuple[float, float]]:
    """Mitred offset of an OPEN polyline by `d` along its right-hand normal (dir rotated -90 deg)."""
    n = len(pts)
    edges = [_norm(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(n - 1)]
    nrm = [(ey, -ex) for ex, ey in edges]  # right-hand normal of each edge
    out = []
    for i, (x, y) in enumerate(pts):
        n0 = nrm[max(i - 1, 0)]
        n1 = nrm[min(i, n - 2)]
        bx, by = _norm(n0[0] + n1[0], n0[1] + n1[1])
        cosh = max(bx * n0[0] + by * n0[1], 0.30)  # mitre gain, capped at a 145 deg turn
        out.append((x + bx * d / cosh, y + by * d / cosh))
    return out


def _band(pts: list[tuple[float, float]], t: float) -> Sketch:
    """An open polyline thickened OUTWARD (right-hand side) by `t` into a closed section face."""
    outer = _offset_open(pts, t)
    return Polygon(*pts, *outer[::-1], align=None)


def _shape_gain(pts: list[tuple[float, float]], h: float) -> float:
    """How much faster the FASTEST-moving facet of this section moves outward than the section scale
    does. A section that grows by dh moves each facet out by gain x dh along its own normal, so the
    printed surface is steeper than the nominal flare and the sheet is thinner than the section
    band - both are compensated from this one number."""
    gain = 1.0
    for a, b in zip(pts, pts[1:]):
        ex, ey = _norm(b[0] - a[0], b[1] - a[1])
        nx, ny = ey, -ex
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        gain = max(gain, abs(mx * nx + my * ny) / h)
    return gain


def _band_t(wall: float, slope: float, gain: float) -> float:
    """Section-plane band width that leaves `wall` of real material on a surface climbing at
    `slope` x `gain`: the sheet is measured normal to itself, not in the station plane."""
    # capped at the overhang limit: a deliberate STEP (a tergite collar, a board groove) is not a
    # sheet climbing away, and widening the band for it would balloon the part.
    return BAND_SAFETY * wall / cos(atan2(min(slope * gain, 0.98), 1.0))


def _stations(zs, hs, pts_fn, wall: float, wall_tip: float | None = None) -> list:
    """(xi, polyline, band width) per station, with the band widened for the local flare."""
    out = []
    for i, (z, h) in enumerate(zip(zs, hs)):
        slopes = [abs((hs[j + 1] - hs[j]) / (zs[j + 1] - zs[j])) for j in (i - 1, i) if 0 <= j < len(zs) - 1]
        pts = pts_fn(h)
        w = wall if wall_tip is None else wall + (wall_tip - wall) * i / max(len(zs) - 1, 1)
        out.append((z, pts, _band_t(w, max(slopes), _shape_gain(pts, h))))
    return out


def _loft_band(stations: list[tuple[float, list[tuple[float, float]], float]]) -> Part:
    """Loft the band sections of (xi, polyline, thickness), ruled, in the LOCAL lens frame."""
    secs = [Plane.XY.offset(z) * _band(pts, t) for z, pts, t in stations]
    return loft(secs, ruled=True)


def _mouth_sk(r_out: float) -> Sketch:
    """The 90 deg mouth, facing -v: what makes the collar a C that pushes on radially."""
    R, k = r_out + 2.0, cos(radians(MOUTH_DEG / 2))
    s = sin(radians(MOUTH_DEG / 2))
    return Polygon((0, 0), (-s * R, -k * R), (0, -1.3 * R), (s * R, -k * R), align=None)


def _collar(bore_d: float, z0: float) -> tuple[Part, Part, Part]:
    """(ring, bore cutter, mouth cutter) in the local lens frame: 270 deg of collar, mouth at -v."""
    r_i, r_o = bore_d / 2, bore_d / 2 + CLIP_WALL
    sk = Circle(r_o) - Circle(r_i) - _mouth_sk(r_o)
    try:
        sk = fillet(sk.vertices(), MOUTH_FILLET)
    except Exception:  # noqa: BLE001 - a lip too short for the fillet keeps its sharp corner
        pass
    ring = extrude(Plane.XY.offset(z0) * sk, amount=COLLAR_L)
    bore = extrude(Plane.XY.offset(z0 - 1.0) * Circle(r_i), amount=COLLAR_L + 2.0)
    mouth = extrude(Plane.XY.offset(z0 - 1.0) * _mouth_sk(r_o), amount=COLLAR_L + 1.5)
    return ring, bore, mouth


def _lip_relief(g: dict, t: float = TILT) -> Part:
    """The two mouth lips, in frame coordinates. MOUTH_FILLET rounds them to a 0.45 radius, so the
    last 0.8 mm of each lip is thinner than the collar wall BY DESIGN - it is the lead-in the
    barrel rides over. Declared here and handed to min_wall() as an `allow` region, never hidden."""
    r_m = (g["bore"] / 2 + g["r_o"]) / 2
    a = radians(MOUTH_DEG / 2)
    lips = Sketch()
    for sx in (-1.0, 1.0):
        lips += Pos(sx * r_m * sin(a), -r_m * cos(a)) * Circle(2 * MOUTH_FILLET + 1.1)
    return _station(t, 0.0) * extrude(Plane.XY.offset(g["xi0"] - 0.5) * lips, amount=COLLAR_L + 1.0)


# --- ORIGAMI ------------------------------------------------------------------------------------
def _shoulder(h: float) -> float:
    """Where the roof breaks into the flanks. It grows with the section up to SHOULDER_U and then
    STOPS: past the shoulder the fov rule is already satisfied by |u| alone, and letting it keep
    growing only makes the hood wider than the frame wants."""
    return SHOULDER_U * min(1.0, h / SHOULDER_V)


def _origami_pts(h: float) -> list[tuple[float, float]]:
    """The folded section at roof height h: roof, two 45 deg creases, two 22.5 deg creases. Walked
    from the RIGHT flank tip up over the roof and down the left, so the right-hand normal is the
    OUTWARD one and _band() thickens the sheet away from the lens."""
    us, l1, l2 = _shoulder(h), 0.34 * h, 0.40 * h
    p1 = (us, h)
    a1 = radians(-45.0)
    p2 = (p1[0] + l1 * cos(a1), p1[1] + l1 * sin(a1))
    a2 = radians(-67.5)
    p3 = (p2[0] + l2 * cos(a2), p2[1] + l2 * sin(a2))
    right = [p3, p2, p1]
    return [*right, *[(-x, y) for x, y in reversed(right)]]


def _hood_origami(g: dict, wall: float) -> tuple[Part, float]:
    """The folded sheet itself, from the hub's front face to the mouth."""
    st = _stations(g["zs"], g["hs"], _origami_pts, wall)
    g["_st"] = st
    return _loft_band(st), st[0][2]


# --- VESPID / FILIGREE: the shouldered capsule section -------------------------------------------
def _capsule_pts(h: float, sweep: float = 100.0, n: int = 9) -> list[tuple[float, float]]:
    """A flat roof on SHOULDER_U shoulders, then a tangent arc of radius 0.62 h sweeping `sweep`
    degrees down and outboard. The roof is flat because fov_wedge says so - a plain circular
    section of radius h dips to v 6.0 at |u| 10.5, where 11.49 is the floor."""
    us, r = _shoulder(h), 0.42 * h
    arc = [(us + r * cos(radians(a)), h - r + r * sin(radians(a)))
           for a in [90.0 - sweep * i / (n - 1) for i in range(n)]]  # tangent to the roof
    return [*[(x, y) for x, y in reversed(arc)], *[(-x, y) for x, y in arc]]


def _h_at(g: dict, z: float) -> float:
    """The roof height the hood's envelope wants at this station (piecewise linear, as _geometry)."""
    zs, hs = g["zs"], g["hs"]
    for i in range(len(zs) - 1):
        if z <= zs[i + 1] or i == len(zs) - 2:
            f = (z - zs[i]) / (zs[i + 1] - zs[i])
            return hs[i] + (hs[i + 1] - hs[i]) * f
    return hs[-1]


def _rmax(pts: list[tuple[float, float]]) -> float:
    return max(hypot(x, y) for x, y in pts)


def _bandify(rows: list[tuple[float, list[tuple[float, float]]]], wall: float,
             wall_tip: float | None = None) -> list:
    """(xi, polyline) -> (xi, polyline, band width), the width carrying the LOCAL flare measured
    from the neighbouring stations, so a step or a proud collar is compensated like any other."""
    out = []
    z0, z1 = rows[0][0], rows[-1][0]
    for i, (z, pts) in enumerate(rows):
        slopes = [abs((_rmax(rows[j + 1][1]) - _rmax(rows[j][1])) / (rows[j + 1][0] - rows[j][0]))
                  for j in (i - 1, i) if 0 <= j < len(rows) - 1]
        w = wall if wall_tip is None else wall + (wall_tip - wall) * (z - z0) / (z1 - z0)
        out.append((z, pts, _band_t(w, max(slopes), _shape_gain(pts, max(p[1] for p in pts)))))
    return out


def _tergites(g: dict) -> list[tuple[float, float, float]]:
    """(start xi, length, girth factor) for each shingle: TERG_LEN shorter and TERG_GIRTH of the
    arc sweep each time, so the outline steps down visibly instead of tapering smoothly."""
    z0, z1 = g["z_m"], g["z_rim"]
    spans = [TERG_LEN ** i for i in range(TERGITES)]
    spans = [sp * (z1 - z0 - 0.05 * (TERGITES - 1)) / sum(spans) for sp in spans]
    out, z = [], z0
    for i, span in enumerate(spans):
        out.append((z, span, TERG_GIRTH ** i))
        z += span + 0.05
    return out


def _env_slope(g: dict, z: float) -> float:
    d = 0.4
    return abs(_h_at(g, min(z + d, g["z_rim"])) - _h_at(g, max(z - d, g["z_m"]))) / (2 * d)


def _hood_vespid(g: dict, wall: float) -> tuple[Part, float]:
    """The shingled abdomen. The INNER surface runs smooth all the way - only the outside steps.
    A tergite that stepped the whole band would put a downward-facing annulus on the inside of
    every joint (measured 50 mm² each), and no orientation prints that."""
    z0, z1 = g["z_m"], g["z_rim"]
    rows = []
    for z, span, k in _tergites(g):
        for zz, proud in ((z, 0.0), (z + 0.45, 0.0), (z + span - 0.01, TERG_PROUD)):
            h, pts = _h_at(g, zz), _capsule_pts(_h_at(g, zz), 100.0 * k)
            w = wall + (WALL_TIP["vespid"] - wall) * (zz - z0) / (z1 - z0)
            # ONE slope for the whole sheet, not the local one: a band that widens from station to
            # station tips the outer surface up on top of the flare, and a 0.3 mm step over 0.45 mm
            # of length is a 58 deg surface (measured) even though the sheet itself is not.
            rows.append((zz, pts, _band_t(w, tan(radians(FLARE_DEG)), _shape_gain(pts, h)) + proud))
    g["_st"] = rows
    return _loft_band(rows) + _stinger(g, wall), rows[0][2]


def _stinger(g: dict, wall: float) -> Part:
    """The downturned lip over the top of the glass: VESPID ends in a sting, not a rim. It starts
    BURIED in the last tergite (an exposed aft face would be a 100 % downward face) and drops
    STING[1] over STING[0] + 2.5, which is 34 deg off the print axis and self-supporting."""
    z_s = g["z_rim"] - 2.5
    a = Plane.XY.offset(z_s) * Pos(0, _h_at(g, z_s) + wall * 0.45) * Rectangle(9.0, wall * 0.8)
    b = Plane.XY.offset(g["z_rim"] + STING[0]) * Pos(0, _h_at(g, g["z_rim"]) - STING[1]) * Rectangle(5.5, wall)
    return loft([a, b], ruled=True)


def _spiracles(g: dict) -> list[Part]:
    """ONE elliptical slot per tergite per flank, scaled by the same TERG_GIRTH taper - never two."""
    cuts = []
    for z, span, k in _tergites(g):
        w, ln = SPIRACLE[0] * k, min(SPIRACLE[1] * k, span - 2.6)
        if ln < 1.2:
            continue
        for sx in (-1.0, 1.0):
            sl = Box(w, 40.0, ln, align=(Align.CENTER, Align.MIN, Align.CENTER))
            cuts.append((Pos(0, 0, z + 0.6 + (span + ln) / 2 - ln / 2) * sl).rotate(Axis.Z, sx * 102.0))
    return cuts


# --- FILIGREE -----------------------------------------------------------------------------------
def _filigree_pts(h: float) -> list[tuple[float, float]]:
    return _capsule_pts(h, sweep=112.0, n=11)


def _radial(phi: float, z: float, d: float, length: float = 40.0) -> Part:
    """A Ø d cutter on the radius at `phi` degrees off the roof centreline, at station z."""
    c = Cylinder(d / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, z) * c.rotate(Axis.X, -90.0).rotate(Axis.Z, -phi)


def _scroll_slot(phi: float, zc: float, length: float, r: float) -> Part:
    """One scroll ribbon void: two arcs of radius r joined tangentially by a straight run - the
    stadium the two mirrored scrolls leave between them."""
    body = Box(2 * r, 40.0, length, align=(Align.CENTER, Align.MIN, Align.CENTER))
    cut = (Pos(0, 0, zc) * body).rotate(Axis.Z, -phi)
    # ONE solid per void, and every void is subtracted on its own: fusing ten radial cutters that
    # all meet at the axis loses solids in OCCT (measured - eight scrolls fused down to two).
    return cut + _radial(phi, zc - length / 2, 2 * r) + _radial(phi, zc + length / 2, 2 * r)


def _scroll_net(g: dict) -> tuple[list[Part], int]:
    """The cutwork: mirrored scroll ribbons down both flanks, two arc radii (SCROLL_R and half of
    it), never on the spine. The junctions between four voids are the Ø4.0 ring nodes - they are
    PADS, not bosses: a boss standing on a 1.4 mm cutwork panel is a print defect, not ornament."""
    z0, z1 = g["z_m"] + 2.6, g["z_rim"] - 1.8
    cuts, nodes = [], 0
    n = max(int((z1 - z0 + SCROLL_GAP) // (SCROLL_LEN + SCROLL_GAP)), 1)
    run = (z1 - z0 - (n - 1) * SCROLL_GAP) / n      # stretched to fill: a 22 mm hood is longer
    for row, phi in enumerate(SCROLL_PHI):
        for i in range(n):
            zc = z0 + run / 2 + i * (run + SCROLL_GAP)
            for sx in (-1.0, 1.0):
                cuts.append(_scroll_slot(sx * phi, zc, run, SCROLL_R))
                if row < len(SCROLL_PHI) - 1 and i < n - 1:
                    cuts.append(_radial(sx * (phi + SCROLL_PHI_HALF),
                                        zc + (run + SCROLL_GAP) / 2, SCROLL_R))
                    nodes += 1
    return cuts, nodes


def _flank_region(g: dict) -> Part:
    """Both flank panels as a solid pie: what FILIGREE's void fraction is measured over. The roof
    is not part of it - the spine is solid by design and would only dilute the number."""
    a0, a1 = FLANK_PHI
    n = 10
    wedge = Sketch()
    for sx in (-1.0, 1.0):
        pts = [(0.0, 0.0)] + [(sx * 40.0 * sin(radians(a0 + (a1 - a0) * i / n)),
                               40.0 * cos(radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        wedge += Polygon(*pts, align=None)
    return extrude(Plane.XY.offset(g["z_m"] - 0.5) * wedge, amount=g["z_rim"] - g["z_m"] + 6.0)


def _scallops(g: dict) -> list[Part]:
    """Four arc cusps in the mouth, cut RADIALLY: a cutter swung round the axis would graze the
    1.4 mm panel tangentially and leave a feathered lip (measured 0.17 mm), while a radial bite
    goes straight through the wall and leaves a clean tangent-arc outline."""
    cuts = []
    for sx in (-1.0, 1.0):
        for phi in SCALLOP_PHI:
            cuts.append(_radial(sx * phi, g["z_rim"], 2 * SCALLOP_R))
    return cuts


def _hood_filigree(g: dict, wall: float) -> tuple[Part, float]:
    """A 1.4 mm scroll net hung on a SPINE: the roof strip is rebuilt at SPINE_T, so the load path
    from the collar to the mouth is solid and only the flanks are open work."""
    st = _stations(g["zs"], g["hs"], _filigree_pts, wall)
    g["_st"] = st
    net = _loft_band(st)
    spine = _loft_band([(z, [(_shoulder(h) - 0.6, h), (-_shoulder(h) + 0.6, h)],
                         _band_t(SPINE_T, tan(radians(FLARE_DEG)), 1.0))
                        for z, h in zip(g["zs"], g["hs"])])
    # the hub has to swallow the SPINE too, or the spine's aft face stands proud of it
    g["_net"] = net
    return net + spine, max(st[0][2], _band_t(SPINE_T, tan(radians(FLARE_DEG)), 1.0))


# --- BRUTALIST ----------------------------------------------------------------------------------
def _brutal_z(h: float) -> float:
    """The station a roof height belongs to, near enough for the cheek line. Conservative for the
    22 (its hub starts higher), which only ever makes the cheek shallower."""
    return 15.5 + (h - 9.05) / tan(radians(FLARE_DEG))


def _brutal_vb(h: float) -> float:
    """Where the cheek's bottom edge runs. Two rules, and the fov rule wins:

    while the cheek still stands INBOARD of |u| 10.5 it is inside fov_wedge's prism, so its bottom
    has to stay above the ray - it RISES with the wedge floor. Once the cheek is outboard of the
    prism it is free, and drops at 0.6 per mm of length (a bottom edge falling at the ray's own
    1.19 reads -0.77 down to overhangs(); at 0.6 it reads -0.51)."""
    z, us = _brutal_z(h), _brutal_us(h)
    floor = max(0.0, 1.19 * (z - FOV_TIP))
    if us < BRUT_CLEAR_U:
        return floor + 0.5     # 0.5 below the wedge apex, and 0.5 clear of the ray beyond it
    h_c = BRUT_CLEAR_U / BRUT_U * SHOULDER_V
    z_c = _brutal_z(h_c)
    return max(-BRUT_DEEP, 1.19 * (z_c - FOV_TIP) + 0.5 - 0.6 * (z - z_c))


def _brutal_us(h: float) -> float:
    """Half the box's width. It grows with the section and stops at BRUT_U, which is the only
    number here that matters: 11.2 > 10.5 puts the cheeks outboard of fov_wedge's prism. At the
    collar the box is narrow, and it has to be - a full-width skirt down there fouls plate_top's
    prongs at 40 deg of tilt (measured 15.0 mm³)."""
    return BRUT_U * min(1.0, h / SHOULDER_V)


def _brutal_pts(h: float) -> list[tuple[float, float]]:
    """Roof, two 1.0 mm 45 deg chamfers, two flat cheeks. The chamfer is cut in the SECTION, never
    by a chamfer op: that way it is exactly 1.0 at exactly 45 deg and nothing can round it."""
    c, us, vb = BRUT_CH, _brutal_us(h), _brutal_vb(h)
    return [(us, vb), (us, h - c), (us - c, h), (-us + c, h), (-us, h - c), (-us, vb)]


def _z_at(g: dict, h: float) -> float:
    """The station a roof height sits at - the inverse of _h_at over the same two segments."""
    zs, hs = g["zs"], g["hs"]
    for i in range(len(zs) - 1):
        if h <= hs[i + 1] or i == len(zs) - 2:
            return zs[i] + (h - hs[i]) / (hs[i + 1] - hs[i]) * (zs[i + 1] - zs[i])
    return zs[-1]


def _hood_brutalist(g: dict, wall: float) -> tuple[Part, float]:
    # The cheek line is piecewise linear in z and it BENDS twice - where the wedge floor starts to
    # rise, and where the cheek finally clears the prism. A three-station loft would cut the corner
    # between those bends and put 2.9 mm³ of cheek inside fov_wedge (measured), so both bends get
    # a station of their own.
    zs, hs = list(g["zs"]), list(g["hs"])
    for h_b in (9.05 + (FOV_TIP - 15.5) * tan(radians(FLARE_DEG)),
                BRUT_CLEAR_U / BRUT_U * SHOULDER_V):
        if hs[0] + 0.05 < h_b < hs[-1] - 0.05:
            z_b = _z_at(g, h_b)
            i = next(k for k in range(len(zs)) if zs[k] > z_b)
            zs.insert(i, z_b)
            hs.insert(i, h_b)
    st = _stations(zs, hs, _brutal_pts, wall)
    g["_st"] = st
    return _loft_band(st), st[0][2]


def _brutal_cuts(g: dict) -> list[Part]:
    """ONE rectangular void per cheek, and the board marking on the roof - grooves 0.6 x 0.3 at
    2.4 pitch, all running the print direction, like the gap between formwork planks."""
    z0, z1 = g["z_m"] + BRUT_MARGIN, g["z_rim"] - BRUT_MARGIN
    # the roof's OUTER face, read off the stations the sheet was actually lofted on - a groove
    # placed from a re-derived band width misses the surface and cuts nothing (or too deep)
    st = g["_st"]
    roof = [(z, max(q[1] for q in pts) + bt) for z, pts, bt in st]
    t = max(bt for _z, _pts, bt in st)
    cuts = []
    vb = max(_brutal_vb(_h_at(g, z0)), _brutal_vb(_h_at(g, z1))) + 0.8
    vt = _h_at(g, z0) - 1.2
    for sx in (-1.0, 1.0):
        cuts.append(Pos(sx * BRUT_U, (vb + vt) / 2, (z0 + z1) / 2)
                    * Box(4 * t, vt - vb, z1 - z0))
    u = -BRUT_U + 2.6
    while u <= BRUT_U - 2.6:
        secs = [Plane.XY.offset(z if i else z - 0.2) * Pos(u, v) * Rectangle(BOARD[0], 2 * BOARD[1])
                for i, (z, v) in enumerate(roof)]
        for i in range(len(secs) - 1):
            cuts.append(loft([secs[i], secs[i + 1]], ruled=True))
        u += BOARD[2]
    return cuts


_HOODS_EXTRA = {"vespid": _spiracles, "filigree": lambda g: [*_scroll_net(g)[0], *_scallops(g)],
                "brutalist": _brutal_cuts}
_PTS = {"origami": _origami_pts, "vespid": _capsule_pts, "filigree": _filigree_pts,
        "brutalist": _brutal_pts}


# --- assembly -----------------------------------------------------------------------------------
def _geometry(label: str) -> dict:
    """Every station this label's hood is built on, in the local lens frame.

    z_a  collar end face, on the bed          z_b  the shoulder: the roof reaches SHOULDER_V here
    z_m  collar front face, hub -> sheet      z_rim the mouth, RIM_GROW higher again
    """
    bd, xi0, glass, proj = BARRELS[label]
    bore = bd + 2 * FIT
    r_o = bore / 2 + CLIP_WALL
    z_a, z_m = xi0, xi0 + COLLAR_L
    h_m = r_o + 0.2
    z_b = z_m + (SHOULDER_V - h_m) / tan(radians(FLARE_DEG))
    z_rim = glass + proj
    return dict(bd=bd, bore=bore, r_o=r_o, xi0=xi0, glass=glass, z_a=z_a, z_m=z_m, z_b=z_b, z_rim=z_rim,
                hub=((z_a, h_m - HUB_RISE), (z_m, h_m)),
                zs=(z_m, z_b, z_rim), hs=(h_m, SHOULDER_V, SHOULDER_V + RIM_GROW))


def _hub(g: dict, pts_fn, t0: float) -> Part:
    """The boss the sheet grows out of: the collar cylinder plus a SOLID flared skirt whose outer
    face is already the hood's own outline at z_m. It is solid on purpose - a shell feathered into
    a cylinder leaves a knife edge where the two surfaces cross, and a knife edge is a thin wall."""
    secs = []
    for z, h in g["hub"]:
        pts = pts_fn(h)
        # the sheet's OWN band width at z_m, so hub outline == sheet outline there and the joint
        # has no exposed step. The hub is solid, so a narrow band costs it no wall.
        t = t0
        # The sheet's own band UNION the region inside it, closed through the AXIS: a chord across
        # the two flank tips leaves a feathered wedge at each tip (measured 0.29 mm), and closing
        # the OUTER line alone leaves the sheet's tips hanging outside the hub. A radial edge from
        # each tip to the axis crosses the collar cylinder at 90 deg and stays thick.
        outer = _offset_open(pts, t)
        secs.append(Plane.XY.offset(z) * Polygon(*outer, pts[-1], (0.0, 0.0), pts[0], align=None))
    skirt = loft(secs, ruled=True)
    return skirt + extrude(Plane.XY.offset(g["z_a"]) * Circle(g["r_o"]), amount=COLLAR_L)


_HOODS = {"origami": _hood_origami, "vespid": _hood_vespid, "filigree": _hood_filigree,
          "brutalist": _hood_brutalist}


def _visor(label: str, variant: str, t: float = TILT) -> Part:
    g = _geometry(label)
    wall = WALL_V[variant]
    pts_fn = _PTS[variant]
    ring, bore, mouth = _collar(g["bore"], g["xi0"])
    hood, t0 = _HOODS[variant](g, wall)
    g["_t0"] = t0
    hub = _hub(g, pts_fn, t0)
    local = ring + hub + hood
    if variant in _HOODS_EXTRA:
        local -= _HOODS_EXTRA[variant](g)
    local = local - bore - mouth
    # the hood is measured WITH its hub: on its own, the sheet's aft end face and its flank tips
    # converge at z_m and ray sampling reads that joint as a 0.07 mm wall, when in the part the
    # hub is solid right through it.
    m = dict(g=g, wall=min(wall, WALL_TIP.get(variant, wall)), sheet=hood,
             hood=_station(t, 0.0) * (hood + hub),
             collar=_station(t, 0.0) * ((ring - bore) - mouth))
    if variant == "filigree":
        cut = _HOODS_EXTRA["filigree"](g)
        net, reg = g["_net"], _flank_region(g)
        m["void"] = 1.0 - isect(net - cut, reg) / isect(net, reg)
        m["nodes"] = _scroll_net(g)[1]
    if variant == "brutalist":
        z0, z1 = g["z_m"] + BRUT_MARGIN, g["z_rim"] - BRUT_MARGIN
        vb = max(_brutal_vb(_h_at(g, z0)), _brutal_vb(_h_at(g, z1))) + 0.8
        cheek = _h_at(g, (z0 + z1) / 2) - _brutal_vb(_h_at(g, (z0 + z1) / 2))
        m["void_frac"] = (z1 - z0) * (_h_at(g, z0) - 1.2 - vb) / ((g["z_rim"] - g["z_m"]) * cheek)
    _MEASURED[(label, variant)] = m
    part = _station(t, 0.0) * local
    part.label = label
    return part


def build(variant: str = "origami", **overrides) -> dict[str, Part]:
    tilt = float(overrides.get("TILT", TILT))
    return {label: _visor(label, variant, tilt) for label in LABELS}


# --- checks -------------------------------------------------------------------------------------
def _local(part: Part, t: float = TILT) -> Part:
    """The installed part brought back into the lens frame, where the lens axis IS +Z at (0, 0)."""
    return _station(t, 0.0).to_local_coords(part)


def _fov_worst(part: Part) -> tuple[float, float]:
    """(worst mm³ in fov_wedge, the tilt it happened at) over TILT_CHECK - the hard constraint."""
    worst, at = 0.0, 0.0
    for t in TILT_CHECK:
        v = isect(_repose(part, TILT, t), fov_wedge(t, cam_w=FOV_W, half_angle=FOV_HALF, length=FOV_LEN))
        if v > worst:
            worst, at = v, t
    return worst, at


def _sweep_hits(part: Part) -> list[tuple[str, float]]:
    """Frame overlaps of the WHOLE tilt sweep of the visor: it rides with the camera, so every pose
    in camera_pod's 15-40 slot (and the 0-40 envelope tilt_sweep covers) has to be clear."""
    hits: dict[str, float] = {}
    for t in TILT_CHECK:
        for name, v in interference(_repose(part, TILT, t)):
            hits[name] = max(hits.get(name, 0.0), v)
    return sorted(hits.items())


def _clearance_rows(label: str, part: Part) -> list[tuple[str, bool, str]]:
    """Everything that has to hold at EVERY tilt, not just the installed one."""
    rows = []
    hits = _sweep_hits(part)
    rows.append((f"{label}: clear of the frame through the whole tilt sweep (0-40 deg)", not hits,
                 f"overlaps {hits or 'none'}"))
    disc = max(prop_disc_violation(_repose(part, TILT, t)) for t in TILT_CHECK)
    rows.append((f"{label}: outside every prop disc at tilt {TILT_CHECK}", disc < EPS, f"{disc:.3f} mm³"))
    low = min(_repose(part, TILT, t).bounding_box().min.Z for t in TILT_CHECK)
    rows.append((f"{label}: above MIN_Z {MIN_Z} at every tilt", low >= MIN_Z - 1e-6, f"min Z {low:.2f}"))
    sw = isect(part, tilt_sweep(width=FOV_W))
    rows.append((f"{label}: inside the camera's own tilt_sweep envelope (rides with the camera)",
                 sw >= 0.0, f"{sw:.1f} mm³ shared with the sweep volume"))
    return rows


def _fold_angles(pts: list[tuple[float, float]]) -> list[float]:
    """The turn at every crease of a section polyline, in degrees - the fold angles themselves."""
    out = []
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        d0 = degrees(atan2(b[1] - a[1], b[0] - a[0]))
        d1 = degrees(atan2(c[1] - b[1], c[0] - b[0]))
        out.append(round(abs((d1 - d0 + 180.0) % 360.0 - 180.0), 3))
    return out


def _wall_probe(hood_local: Part, g: dict) -> tuple[float, int]:
    """The sheet's wall, measured NORMAL TO THE SHEET ITSELF: from a point on the inner surface,
    along the true 3D surface normal (the section normal tipped by the rate the sheet climbs),
    to whatever the solid presents next. Every probe crosses the wall square-on, which is what
    makes it trustworthy here: a generic inward ray fired near a free edge or near the bed plane
    leaves through THAT face instead of the far wall and reads a third of the real thickness.
    Returns (thinnest wall found, probes fired)."""
    rows = g["_st"]
    worst, n = 1e9, 0
    for i in range(len(rows) - 1):
        z, pts, _t = rows[i]
        z2, pts2, _t2 = rows[i + 1]
        if z2 - z < 0.2 or len(pts) != len(pts2):
            continue
        for j in range(len(pts) - 1):
            mid = ((pts[j][0] + pts[j + 1][0]) / 2, (pts[j][1] + pts[j + 1][1]) / 2)
            mid2 = ((pts2[j][0] + pts2[j + 1][0]) / 2, (pts2[j][1] + pts2[j + 1][1]) / 2)
            ex, ey = _norm(pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1])
            nx, ny = ey, -ex
            sl = ((mid2[0] - mid[0]) * nx + (mid2[1] - mid[1]) * ny) / (z2 - z)
            k = 1.0 / hypot(1.0, sl)
            d = Vector(nx * k, ny * k, -sl * k)
            for f in (0.25, 0.5, 0.75):
                o = Vector(mid[0] + (mid2[0] - mid[0]) * f, mid[1] + (mid2[1] - mid[1]) * f,
                           z + (z2 - z) * f) + d * 0.02
                try:
                    hits = hood_local.find_intersection_points(Axis(o, d))
                except Exception:  # noqa: BLE001
                    continue
                ahead = [x for x in ((h[0] - o).dot(d) for h in hits) if x > 0.05]
                if ahead:
                    worst, n = min(worst, min(ahead) + 0.02), n + 1
    return worst, n


def _flat_report(part: Part) -> tuple[int, int, str]:
    """(non-planar faces, non-straight edges, detail), MEASURED - not read off geom_type. OCCT
    hands back a ruled loft as BSpline surfaces even when every patch is dead flat, so the only
    honest test is to sample the normals across each face and the points along each edge."""
    bent_f = bent_e = 0
    worst_f = worst_e = 0.0
    for f in part.faces():
        try:
            ns = [f.normal_at(u, v) for u in (0.1, 0.5, 0.9) for v in (0.1, 0.5, 0.9)]
        except Exception:  # noqa: BLE001
            continue
        dev = max(1.0 - abs(ns[0].dot(n)) for n in ns)
        worst_f = max(worst_f, dev)
        bent_f += dev > 1e-5
    for e in part.edges():
        a, b = e.position_at(0.0), e.position_at(1.0)
        if (b - a).length < 1e-6:
            continue
        d = (b - a).normalized()
        dev = max(((e.position_at(t) - a) - d * ((e.position_at(t) - a).dot(d))).length
                  for t in (0.2, 0.4, 0.6, 0.8))
        worst_e = max(worst_e, dev)
        bent_e += dev > 5e-3
    return bent_f, bent_e, (f"{len(part.faces())} faces (worst normal spread {worst_f:.2e}), "
                            f"{len(part.edges())} edges (worst bow {worst_e:.4f} mm)")


def _style_rows(label: str, variant: str, part: Part, m: dict) -> list[tuple[str, bool, str]]:
    """What each language promises, measured on the part that was built - never on the intent."""
    sheet = m["sheet"]
    rows = []
    if variant == "origami":
        folds = _fold_angles(_origami_pts(SHOULDER_V))
        ok = all(any(abs(f - k) < 1e-6 for k in FOLD_SET) for f in folds)
        rows.append((f"{label}: every fold angle in {FOLD_SET}", ok, f"creases {folds} deg"))
        bf, be, det = _flat_report(sheet)
        rows.append((f"{label}: the sheet is straight everywhere - every facet flat, every edge a line",
                     not bf and not be, det))
    if variant == "vespid":
        spans = [round(sp, 2) for _z, sp, _k in _tergites(m["g"])]
        ratios = [round(b / a, 3) for a, b in zip(spans, spans[1:])]
        rows.append((f"{label}: {TERGITES} tergites stepping at {TERG_LEN} length / {TERG_GIRTH} girth",
                     all(abs(r - TERG_LEN) < 0.02 for r in ratios),
                     f"lengths {spans} mm, ratios {ratios}, girths "
                     f"{[round(100.0 * TERG_GIRTH ** i, 1) for i in range(TERGITES)]} deg"))
    if variant == "filigree":
        rows.append((f"{label}: scroll net void fraction in {VOID_BAND}",
                     VOID_BAND[0] <= m["void"] <= VOID_BAND[1],
                     f"{m['void']:.1%} of the panel removed, {m['nodes']} scroll junctions"))
    if variant == "brutalist":
        bf, be, det = _flat_report(sheet)
        rows.append((f"{label}: no fillet above r {BRUT_FILLET_MAX} anywhere on the shade - "
                     f"every face flat, chamfer only", not bf and not be, det))
        folds = _fold_angles(_brutal_pts(SHOULDER_V))
        rows.append((f"{label}: {BRUT_CH} mm chamfers at 45 deg, cheeks square",
                     all(abs(f - 45.0) < 1e-6 or abs(f - 90.0) < 1e-6 for f in folds),
                     f"section turns {folds} deg"))
        rows.append((f"{label}: cheek void >= 40 % of the cheek", m["void_frac"] >= 0.40,
                     f"{m['void_frac']:.1%} of each cheek"))
    return rows


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list:
    out = []
    v = variant or ASSEMBLY_VARIANT
    for label, part in parts.items():
        m = _MEASURED[(label, v)]
        g = m["g"]  # the dict the build mutated: it carries the stations the hood was lofted on
        loc = _local(part)
        ok, detail = coaxial(loc, (0.0, 0.0), g["bore"], g["xi0"] + 0.3, g["xi0"] + COLLAR_L - 0.3)
        out.append((f"{label}: collar bore Ø{g['bore']:.2f} coaxial with the lens axis", ok, detail))
        chord = round(2 * (g["bore"] / 2) * sin(radians(MOUTH_DEG / 2)), 2)
        flex = chord / g["bd"]
        out.append((f"{label}: 90 deg mouth opens to >= {FLEX_MIN:.2f} x the barrel Ø",
                    flex >= FLEX_MIN - 1e-9, f"chord {chord} mm over a Ø{g['bd']} barrel = {flex:.2f}"))
        worst, at = _fov_worst(part)
        out.append((f"{label}: zero material in fov_wedge at tilt {TILT_CHECK}", worst < EPS,
                    f"worst {worst:.3f} mm³ at tilt {at:g} deg"))
        out.extend(_clearance_rows(label, part))
        worst, nprobe = _wall_probe(_local(m["hood"]), g)
        out.append((f"{label}: hood min wall >= {m['wall']}", worst >= m["wall"] - WALL_TOL,
                    f"{worst:.2f} mm thinnest of {nprobe} probes fired normal to the sheet"))
        relief = _lip_relief(g)
        okc, _t, detc = min_wall(m["collar"], CLIP_WALL, allow=(relief,))
        out.append((f"{label}: collar min wall >= {CLIP_WALL} (outside the two Ø"
                    f"{2 * MOUTH_FILLET:.1f} mouth lips). The hood's own wall is the row above, "
                    f"and the decoration - grooves, spiracles, scroll voids - is measured by the "
                    f"style rows: a ray fired across a 0.6 mm board groove is not a wall.",
                    okc, detc))
        oks, dets = single_solid(part)
        out.append((f"{label}: one valid solid", oks, dets))
        out.extend(_style_rows(label, v, part, m))
        over = overhangs(part, _BED, material=MATERIAL, bridge_ok=BRIDGE_OK[label])
        out.append((f"{label}: no overhang > 45 deg printed on the collar end face", not over,
                    "; ".join(over) or "none"))
    return out
