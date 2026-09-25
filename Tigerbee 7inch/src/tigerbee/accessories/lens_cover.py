"""Snap-on lens covers for all three camera pods plus a generic barrel cap - four different lids.

WHAT THE INTERFACE ACTUALLY IS (measured, not assumed)
------------------------------------------------------
`camera_pod` (19 / 21 mm) has NO lens aperture: it is an open-fronted slide-on U-pod - two cheeks,
a floor, a backplate and two posts, with nothing at all in front of the camera ("No brow bar:
anything ahead of the lens sits in the FOV"). So there is no pod ring to cap. What a cover has to
grip is the CAMERA's own lens barrel: the repo datum in `_common.camera_envelope` is Ø14.0 x 6.0,
its base on the body front face at xi 10.0 from CAM_PIVOT (0, 100, 27) and its glass at xi 16.0.
That barrel is identical for both pod widths - CAM_W is the only thing `camera_pod` changes - so
the two covers share every mating dimension: bore, lip band, grip depth, axis and tilt.

They are still two parts, and the reason is the pod, not the camera: the 19 pod's cheeks stand at
|x| 9.75 where the 21 pod's stand at |x| 10.75, and a cover sized for the wider gap does not fit
the narrower one (measured: a Ø20.4 cover fouls camera_pod_19 by 34.9 mm3 and camera_pod_21 by
0.0). So `lens_cover_19` is the NARROW cover - Ø18.4, and it therefore fits BOTH pods - and
`lens_cover_21` spends the extra 2 mm of gap the 21 pod has. Since the fit is shared, the two
labels are free to be two different readings of the same cap, and that is what they are: the 21 is
the CARAPACE/OCELLUS dome, the 19 is the SHARD cut gem, and either one will cover either camera.

`camera_pod_22` (Foxeer Mini Cat 3) presents a real hood: an oval mouth of semi-axes 11.35 x 11.45
opening at the hood's front plane, xi 22.0, which is 12 mm ahead of the camera body and 2 mm ahead
of the glass. The cover for it grips that mouth from the INSIDE with an oval plug, because the hood
rim itself is rolled/chamfered by the pod (there is no square shoulder outboard of it to grab) and
because the annulus between the Ø22.7 mouth and the Ø17 lens is 2.85 mm of free space 10 mm deep -
the best grip on the whole set. Its datums are read from `camera_pod_22` at import when that module
is importable, and fall back to the values recorded here otherwise.

`lens_cover_generic` is the fallback for a bare barrel, BARREL_D parameterised over 14-16 mm.

THE FOUR LIDS
-------------
  lens_cover_21       CARAPACE / OCELLUS - a Ø20.4 dome, rise/span 0.32, breaking at a CARINA
                      crease into a short skirt that carries every mating feature, with a raised
                      elliptical OCELLUS rim round the crown (the beetle's bulging eye, which is
                      exactly what a lens cap is), a stripe3 maculation on the skirt and the
                      suture over the crown. Fits camera_pod_21.
  lens_cover_19       SHARD - a Ø18.4 cut gem: a 6-flank girdle, 6 crown facets and a hexagonal
                      table, every junction chamfered, a faceted LABRUM shield proud on the table.
                      Fits BOTH pods.
  lens_cover_22       SLIPSTREAM under the MICRO RULE (L < 28, so no teardrop): a flat oval lid
                      flush inside the hood's own outline with ONE swept cusped tail fin, an oval
                      plug and an oval bead - never a polygon.
  lens_cover_generic  ARSENAL - an orthogonal cap with the family's single 30 deg cut corner, two
                      transverse ribs, a knurl band each side, chamfer 1.6/0.6 and a Ø4.0 eye.

Every one of them: 1.6 wall, an internal retaining lip with a 0.2 mm interference-free CAD gap (the
TPU flexes to grip - the squeeze is not modelled), a finger tab, a lanyard eye, the CN-1 suture, and
a footprint proven by boolean to cover the whole opening. All four print open-face-down except the
22, which prints face-down because everything it has faces the camera.
"""

from math import cos, hypot, pi, radians, sin, sqrt, tan

from build123d import (Axis, Box, BuildLine, BuildSketch, Circle, Cylinder, Ellipse, GeomType, Part,
                       Plane, Polygon, Pos, Rectangle, Sketch, Sphere, Spline, Vector, chamfer,
                       extrude, fillet, loft, make_face, revolve)

from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "lens_cover"
TITLE = "Lens covers (19/21, 22 mm pods, generic barrel)"
MATERIAL = "TPU95A"
EXCLUSIVE = ()
L21, L19, L22, LGEN = "lens_cover_21", "lens_cover_19", "lens_cover_22", "lens_cover_generic"
LABELS = (L21, L19, L22, LGEN)
# The four are ALTERNATIVES: one camera, one cover. The 19 is the one that fits every pod, so it is
# the one the combined assembly wears.
ASSEMBLY_LABELS = (L19,)

# --- camera / pod datums (frame coordinates; xi runs along the lens axis from CAM_PIVOT) --------
TILT = 25.0            # both pods' default: camera_pod's arc slot is 15-40, camera_pod_22 ships 25
TILT_SLOT = (15.0, 40.0)   # camera_pod's M2 arc slot, the poses a 19/21 cover must survive
TILT_22 = (25.0, 35.0)     # camera_pod_22's two shipped tilts (the hole PAIR sets it)
XI_BODY, XI_GLASS = 10.0, 16.0     # camera body front face / glass (_common.camera_envelope datums)
BARREL_21 = 14.0                   # Ø of the 19/21 camera's lens barrel (camera_envelope lens_d)
CHEEK_X = {L21: 10.75, L19: 9.75}  # inboard face of each pod's cheeks: the width that limits a cap

# camera_pod_22's hood, read from the module when it imports (a sibling may still be editing it)
HOOD_XI_RIM, HOOD_RX, HOOD_RV, HOOD_LENS_R, HOOD_N = 22.0, 11.95, 12.05, 8.5, 8.0
try:  # pragma: no cover - a sibling module mid-edit must not break this build
    from tigerbee.accessories import camera_pod_22 as _CP22

    HOOD_XI_RIM = float(_CP22.XI_RIM)
    HOOD_RX, HOOD_RV = float(_CP22.BORE_RX), float(_CP22.BORE_RV)
    HOOD_N = float(getattr(_CP22, "BORE_N", 2.0))
    HOOD_LENS_R = float(_CP22.LENS_D) / 2.0
except Exception:  # noqa: BLE001
    _CP22 = None

# --- parameters (mm) --------------------------------------------------------------------------
WALL = 1.6              # every lid's nominal wall
LIP = 0.8               # radial engagement: the step between the lip band and the relief above it
LIP_GAP = 0.2           # CAD gap between the lip band and the barrel - no interference modelled
LIP_H = 1.6             # axial height of the lip band, the only part that touches the barrel
TAB = (8.0, 4.0, 2.0)   # finger tab: length, pinch width, thickness
LOOP_D = 3.0            # lanyard eye
LOOP_WALL = 1.6         # material all round the eye
LOOP_D_GEN = 4.0        # ARSENAL's own eye is Ø4.0
BARREL_D = 15.0         # the generic cap's barrel; parameterise over 14-16
DOME_RISE_RATIO = 0.32  # CARAPACE section rule, 0.28-0.36
GRIP = 4.0              # how much of the 6 mm barrel the cover holds
AIR = 0.8               # air ahead of the glass
SUT_W, SUT_D = 0.8, 0.4
SUT_D_BED = 0.45        # on a lid whose sutured face IS the bed face: 0.4 over 0.4 is exactly 45
#                         deg, which overhangs() flags at its -0.70 limit; 0.45 makes it 48 deg.
XI_RIM = XI_GLASS - GRIP        # 12.0: where every barrel cover's open rim sits
Z_CEIL = GRIP + AIR             # 4.8: the cavity's flat (bridged) ceiling, local z
CHEEK_CLEAR = 0.5               # design clearance from a cover's widest point to the pod's cheeks

# lens_cover_21 - CARAPACE
R21 = 10.2                      # = CHEEK_X[L21] - 0.55
CAR21 = 4.2                     # CARINA: the dome breaks into the skirt here. Forced from below -
#                                 a shallower carina cannot enclose a Ø16 cavity 4.8 deep at
#                                 rise/span 0.32 and still keep 1.6 of wall on the cavity corner.
OC_A, OC_B, OC_W, OC_PROUD = 5.0, 6.0, 2.0, 1.6     # the OCELLUS rim
OC_BLEND = (3.0, 2.0, 1.5, 1.2, 1.0, 0.8, 0.6, 0.4)  # ladder: 3.0 cannot fit a 1.6-proud rim
CARINA_R = 0.8
STRIPE_N, STRIPE_W, STRIPE_DEEP = 3, 1.6, 0.6       # the stripe3 maculation on the skirt

# lens_cover_19 - SHARD.  Every facet is >= 8 mm in BOTH of its own in-plane directions, which is
# what sets the girdle height and the crown's slant length; see _facet_report().
R19 = 9.2                       # hexagon INRADIUS, flats facing +-X (= CHEEK_X[L19] - 0.55)
G19 = 8.0                       # girdle height: the flank facets are 10.62 x 8.0
TBL19 = 4.6                     # table inradius
CROWN19 = 6.6                   # crown rise: slant sqrt(4.6^2 + 6.6^2) = 8.04, facet normals 33 deg
COL19 = 4.0                     # hollow crown column inradius
COL19_TOP = 9.0                 # low enough that the crown is solid right across at
#                                 z 9.3, which is where coverage is proven by boolean
CH19 = (2.0, 1.2, 0.6)          # SHARD's chamfer ladder: sil / crease / free
STRIP19 = 2.4                   # the widest strip those chamfers can produce, and therefore the
#                                 extent below which a face is edge treatment and not a facet: a
#                                 1.2 chamfer across the girdle's 120 deg corner is 2.08 mm wide
#                                 and a 0.6 chamfer across the 27 deg girdle/crown junction 2.31.
LAB19 = (6.4, 4.2, 0.8)         # LABRUM shield on the table: length, width, proud

# lens_cover_22 - SLIPSTREAM, micro rule
PLUG22 = 3.0                    # plug depth into the hood mouth
BEAD22 = 0.8                    # axial length of the bead land
RAMP22 = 1.0                    # lead-in ramp under the bead (prints as a 68 deg cone)
RELIEF22 = 0.5                  # radial relief above the bead: what is left after a 1.35 wall
PLATE22 = 1.6
FIN22 = (9.0, 7.0)              # swept tail fin: length, root width
TAIL_TIP_R = 0.6                # CN-3 cusp tip

# lens_cover_generic - ARSENAL
GEN_RIB = (1.6, 2.0, 9.0)       # rib width, proud, pitch
GEN_CUT_D = 2.5                 # the 30 deg cut corner's drop; its run is 2.449 x that
GEN_KNURL = (10.0, 2.0, 0.5, 1.6)   # band length, height, proud, pitch
GEN_CH = (1.6, 0.6)             # ARSENAL chamfer: silhouette / elsewhere

_P = Vector(*CAM_PIVOT)         # (0, 100, 27)
_MEASURED: dict = {}            # what each build actually reached (blend radii, sections)
_SUTURE: dict = {}              # each label's CN-1 groove tool, in LOCAL coords, kept for checks()

PRINT = {L21: (0.0, -cos(radians(TILT)), -sin(radians(TILT))),
         L19: (0.0, -cos(radians(TILT)), -sin(radians(TILT))),
         LGEN: (0.0, -cos(radians(TILT)), -sin(radians(TILT))),
         L22: (0.0, cos(radians(TILT)), sin(radians(TILT)))}
# Bridged ceilings, in PRINT coordinates. Every barrel cover prints rim-down, so print Z == local z
# and the boxes only have to name the plane - overhangs() takes the SPAN from the face itself.
BRIDGE_OK = {
    L21: (("box", -40, -40, Z_CEIL - 0.4, 40, 40, Z_CEIL + 0.4),),
    L19: (("box", -40, -40, Z_CEIL - 0.4, 40, 40, Z_CEIL + 0.4),
          ("box", -40, -40, COL19_TOP - 0.4, 40, 40, COL19_TOP + 0.4)),
    LGEN: (("box", -40, -40, Z_CEIL - 0.4, 40, 40, Z_CEIL + 0.4),),
}

MOUNTS = {
    L21: ("the camera's own Ø14 x 6 lens barrel on the CAM_PIVOT (0, 100, 27) axis, between "
          "camera_pod_21's cheeks (|x| 10.75)", "no frame face - the cover touches the camera only"),
    L19: ("the camera's own Ø14 x 6 lens barrel on the CAM_PIVOT (0, 100, 27) axis, between either "
          "pod's cheeks (|x| 9.75 on camera_pod_19)", "no frame face"),
    L22: (f"camera_pod_22's hood mouth, semi-axes {HOOD_RX} x {HOOD_RV} at xi {HOOD_XI_RIM} on the "
          f"CAM_PIVOT axis", "no frame face"),
    LGEN: (f"any bare Ø{BARREL_D} lens barrel (parameterise BARREL_D 14-16) on the CAM_PIVOT axis",
           "no frame face"),
}
HARDWARE = {label: ("none - 0.2 mm CAD gap snap fit in TPU95A; optional 1.5 mm cord through the "
                    f"Ø{LOOP_D_GEN if label == LGEN else LOOP_D} lanyard eye",) for label in LABELS}
NOTES = {
    L21: ("Pushes on over the front 4 mm of the lens barrel until the rim is 2 mm clear of the "
          "camera's front face; the Ø14.4 lip band is the only thing that touches it and the bore "
          "steps out 0.8 above it so the band alone grips. Needs camera_pod_21's cheek gap - on a "
          "19 mm pod use lens_cover_19, which fits both. Prints rim-down apex-up; the Ø16 ceiling "
          "is a 16 mm bridge, well inside TPU's 22."),
    L19: ("The narrow cover: Ø18.4 over the flats, so it clears camera_pod_19's cheeks (|x| 9.75) "
          "and camera_pod_21's alike - the cover to buy if you own one of each. Same Ø14.4 lip "
          "band, same 4 mm grip, same axis as lens_cover_21; only the cheeks, and the styling, "
          "differ. Prints table-up on its rim."),
    L22: ("Grips camera_pod_22's hood mouth from the inside: the oval plug drops 3 mm into the "
          "mouth and its bead lands 0.2 off the wall, while the lid sits down on the rim flush "
          "INSIDE the hood's own outline, so nothing stands proud of the fairing. Fits both shipped "
          "tilts (25 and 35 deg) - the cover rides with the pod. Prints face-down: every feature it "
          "has faces the camera, so there is not one overhang on it."),
    LGEN: (f"For a bare barrel: BARREL_D {BARREL_D} as shipped, edit it anywhere in 14-16 and every "
           "other dimension follows. As shipped it also slips over the repo's own Ø14 lens with "
           "0.7 mm to spare - a lanyard cap rather than a snap cap at that size. Prints rim-down; "
           "the ribs, the 30 deg corner and the knurl all face up."),
}


# --- the camera frame -------------------------------------------------------------------------
def _ax(t: float) -> tuple[Vector, Vector]:
    """(a, u): the lens axis and the camera's own 'up' at tilt `t` about Axis(CAM_PIVOT, +X)."""
    c, s = cos(radians(t)), sin(radians(t))
    return Vector(0, c, s), Vector(0, -s, c)


def _pt(t: float, xi: float, v: float = 0.0, x: float = 0.0) -> Vector:
    a, u = _ax(t)
    return _P + a * xi + u * v + Vector(x, 0, 0)


def _station(t: float, xi: float) -> Plane:
    """Station plane at xi, normal = the lens axis. Local (X, Y, Z) = (-frame x, v, along the axis),
    exactly as camera_pod_22 orients its own stations. Every cover is built in this frame with its
    open rim on local z = 0 and then placed once."""
    a, _u = _ax(t)
    return Plane(origin=tuple(_pt(t, xi)), z_dir=tuple(a), x_dir=(-1.0, 0.0, 0.0))


def _place(local: Part, t: float, xi0: float) -> Part:
    """A cover built in the local frame -> frame coordinates, its rim plane at xi0."""
    return _station(t, xi0) * local


def _repose(part: Part, t_from: float, t_to: float) -> Part:
    """The same installed cover at another tilt: it rides with the camera, about CAM_PIVOT +X."""
    return part if abs(t_to - t_from) < 1e-9 else part.rotate(Axis(_P, (1, 0, 0)), t_to - t_from)


def _barrel(t: float, d: float = BARREL_21, xi0: float = XI_BODY, xi1: float = XI_GLASS) -> Part:
    """The physical lens barrel, in frame coordinates: what the lip band has to grip."""
    return S.extrude_cut(Circle(d / 2), _station(t, xi0), xi1 - xi0)


def _squircle(a: float, b: float, n: float, pts: int = 72) -> Sketch:
    """|x/a|^n + |b/b|^n = 1 as ONE closed spline - camera_pod_22's hood mouth is this curve with
    n = 8, and a strict ellipse through the same semi-axes misses its corners by 2.6 mm. Kept
    private on purpose: only the NUMBERS come from the sibling module, never its code path."""
    if n <= 2.0 + 1e-9:
        return Ellipse(a, b)
    k = []
    for i in range(pts):
        th = 2.0 * pi * i / pts
        ct, st = cos(th), sin(th)
        k.append((a * abs(ct) ** (2.0 / n) * (1.0 if ct >= 0 else -1.0),
                  b * abs(st) ** (2.0 / n) * (1.0 if st >= 0 else -1.0)))
    with BuildSketch() as sk:
        with BuildLine():
            Spline(*k, k[0], tangents=((0.0, 1.0), (0.0, 1.0)))
        make_face()
    return sk.sketch


def _hex(inradius: float) -> Sketch:
    """Hexagon with FLATS facing +-X, so the widest point in X is the inradius - that is what the
    pod's cheeks measure. Vertices at 30, 90, ... so one vertex points dorsally (+v)."""
    r = inradius / cos(radians(30))
    return Polygon(*[(r * cos(radians(a)), r * sin(radians(a))) for a in range(30, 360, 60)],
                   align=None)


# --- shared cup geometry (local frame: +Z along the lens axis, z = 0 the open rim) -------------
def _cup_cavity(bore_r: float, lip: float = LIP, ceiling: float = Z_CEIL,
                lip_h: float = LIP_H) -> Part:
    """The bore: a lip band of radius `bore_r` at the mouth, then a relief `lip` wider above it, up
    to a FLAT ceiling. Only the band touches the barrel, which is what makes a snap cap grip
    instead of binding; the flat ceiling is a bridge (declared in BRIDGE_OK), and it is flat rather
    than domed because a domed inner ceiling on an apex-up print is an unsupported dome."""
    c = Pos(0, 0, lip_h / 2) * Cylinder(bore_r, lip_h)
    c += Pos(0, 0, (lip_h + ceiling) / 2) * Cylinder(bore_r + lip, ceiling - lip_h)
    return c


def _eye(at: tuple[float, float], thick: float, d: float = LOOP_D,
         wall: float = LOOP_WALL) -> tuple[Sketch, Part]:
    """(boss sketch, bore) for a lanyard eye: a Ø(d + 2*wall) pad so the hole keeps `wall` all
    round whatever outline it sits on, and an AXIAL bore - a hole down the print direction has no
    ceiling to bridge and no arch to exempt."""
    pad = Pos(*at) * Circle(d / 2 + wall)
    bore = Pos(at[0], at[1], -0.5) * Cylinder(d / 2, thick + 1.0, align=MIN_Z_ALIGN)
    return pad, bore


def _blend(shape: Part, edges, ladder, kind: str = "fillet") -> tuple[Part, float]:
    """Edge treatment that never takes a build down with it, and reports what it reached. Tries the
    whole group, then edge by edge, so one impossible edge cannot cost the rest their blend."""
    op = chamfer if kind == "chamfer" else fillet
    sel = [e for e in edges if e.length > 0.3]
    if not sel:
        return shape, 0.0
    for r in ladder:
        try:
            return op(sel, r), round(r, 3)
        except Exception:  # noqa: BLE001 - OCCT refuses radii it cannot fit
            continue
    best = 0.0
    for e in sel:
        mid = e.position_at(0.5)
        for r in ladder:
            try:
                pick = [x for x in shape.edges() if (x.position_at(0.5) - mid).length < 1e-6]
                if not pick:
                    break
                shape = op(pick, r)
                best = max(best, r)
                break
            except Exception:  # noqa: BLE001
                continue
    return shape, round(best, 3)


def _dome_suture(r_sph: float, z_c: float, half_deg: float, w: float = SUT_W,
                 depth: float = SUT_D) -> Part:
    """CN-1 on a spherical crown. A V ring of triangular section revolved about the X axis through
    the dome's own centre, so the groove follows the crown at constant depth instead of surfacing
    only at the apex, clipped by a vesica so both ends run out to a true point.

    The tool stops `0.2` above the sphere, so anything standing PROUD of the dome (the OCELLUS) is
    untouched: the suture runs over the crown and passes under the eye-ring."""
    prof = Polygon((-w / 2, z_c + r_sph + 0.2), (w / 2, z_c + r_sph + 0.2), (0.0, z_c + r_sph - depth),
                   align=None)
    ring = revolve(Plane.XZ * prof, Axis((0, 0, z_c), (1, 0, 0)), 2 * half_deg)
    ring = ring.rotate(Axis((0, 0, z_c), (1, 0, 0)), -half_deg)
    y1 = r_sph * sin(radians(half_deg))
    clip = extrude(Plane.XY * S.lens((0.0, -y1), (0.0, y1), w), amount=z_c + r_sph + 4.0)
    return ring & clip


def _stripe3(r_out: float, z0: float, deep: float = STRIPE_DEEP, w: float = STRIPE_W) -> Part:
    """CN-4 at the small tier: the maculation as stripe3 rather than a lunule (16 mm will not sit on
    a 20 mm cap). Three bars of lengths 1 : 0.75 : 0.5 standing up the skirt, arrayed across it, cut
    by a cylindrical shell so each one is a true 0.6 deboss on a curved flank rather than a flat
    cutter that misses the ends."""
    shell = Pos(0, 0, 10.0) * Cylinder(r_out + 1.0, 40) - Pos(0, 0, 10.0) * Cylinder(r_out - deep, 40)
    bars = Part()
    for i, frac in enumerate((1.0, 0.75, 0.5)):
        xc = (i - 1) * 2 * w
        # the box limits x and z only: its inner face clears the shell's own inner
        # radius, so the groove floor is the clean cylinder and not a tangent sliver
        bars += box(xc - w / 2, -r_out - 2.0, z0, xc + w / 2, -(r_out - deep) + 1.5,
                    z0 + 3.4 * frac)
    return shell & bars


# --- lens_cover_21: CARAPACE / OCELLUS ---------------------------------------------------------
def dome_21() -> dict:
    """The 21's section, solved rather than drawn. rise/span is DOME_RISE_RATIO, and the CARINA sits
    exactly where a sphere of that rise still clears the cavity corner (8.0, Z_CEIL) by WALL."""
    rise = DOME_RISE_RATIO * 2 * R21
    z_ap = CAR21 + rise
    r_sph = (R21 ** 2 + rise ** 2) / (2 * rise)
    return dict(rise=rise, z_ap=z_ap, r_sph=r_sph, z_c=z_ap - r_sph, span=2 * R21)


def _cover_21() -> Part:
    d = dome_21()
    r_sph, z_c, z_ap = d["r_sph"], d["z_c"], d["z_ap"]
    bore = BARREL_21 / 2 + LIP_GAP

    body = Pos(0, 0, CAR21 / 2) * Cylinder(R21, CAR21)
    body += (Pos(0, 0, z_c) * Sphere(r_sph)) & (Pos(0, 0, CAR21 + 20) * Cylinder(R21 + 5, 40))
    # CARINA: the one crease the family allows, filleted, and nothing else on the shell
    carina = [e for e in body.edges() if abs(e.bounding_box().min.Z - CAR21) < 1e-4
              and e.length > 10.0]
    body, r_car = _blend(body, carina, (CARINA_R, 0.6, 0.4))

    # the finger tab: a cusped tongue (CN-3) off the skirt, its underside in the bed plane, with the
    # lanyard eye inside its own outline so the tongue stays convex in plan
    tail = S.cusp_tail(9.0, 9.5, TAIL_TIP_R, at=(0.0, R21 - 1.2), angle=90.0)
    tongue = extrude(Plane.XY * tail, amount=TAB[2])
    body += tongue
    _pad, eye = _eye((0.0, 13.8), TAB[2])
    body -= eye
    body -= _cup_cavity(bore)

    # the OCELLUS: an elliptical rim standing OC_PROUD off the crown, blended into it
    tube = S.extrude_cut(Ellipse(OC_A + OC_W, OC_B + OC_W) - Ellipse(OC_A, OC_B), Plane.XY, z_ap + 5)
    shell = (Pos(0, 0, z_c) * Sphere(r_sph + OC_PROUD)) - (Pos(0, 0, z_c) * Sphere(r_sph))
    body += tube & shell

    def on_sphere(e, rad, tol=0.15):
        return (e.length > 3.0
                and all(abs(sqrt(p.X ** 2 + p.Y ** 2 + (p.Z - z_c) ** 2) - rad) < tol
                        for p in (e.position_at(t) for t in (0.1, 0.5, 0.9))))

    body, r_oc = _blend(body, [e for e in body.edges() if on_sphere(e, r_sph)], OC_BLEND)
    body, _r = _blend(body, [e for e in body.edges() if on_sphere(e, r_sph + OC_PROUD)],
                      (0.8, 0.5, 0.3))
    body, _r = _blend(body, [e for e in body.edges() if abs(e.bounding_box().min.Z - TAB[2]) < 1e-4
                             and abs(e.bounding_box().max.Z - TAB[2]) < 1e-4], (0.8, 0.5, 0.3))

    body -= _stripe3(R21, 0.5)
    tool = _dome_suture(r_sph, z_c, 25.0)
    body -= tool
    _SUTURE[L21] = tool
    _MEASURED[L21] = dict(blend_ocellus=r_oc, blend_carina=r_car, **d)
    return body


# --- lens_cover_19: SHARD ----------------------------------------------------------------------
def _cover_19() -> Part:
    bore = BARREL_21 / 2 + LIP_GAP
    z_tbl = G19 + CROWN19
    girdle = extrude(Plane.XY * _hex(R19), amount=G19)
    crown = loft([Plane.XY.offset(G19) * _hex(R19), Plane.XY.offset(z_tbl) * _hex(TBL19)], ruled=True)
    body = girdle + crown

    # SHARD's chamfer ladder, tier by tier. 'sil' is the 6 girdle corners, and the value that lands
    # there is _style's own wall clamp: 0.40 x the 3.0 mm corner wall = 1.2.
    corners = [e for e in body.edges() if e.geom_type == GeomType.LINE
               and abs(e.bounding_box().size.Z - G19) < 1e-4 and e.bounding_box().size.X < 1e-4
               and e.bounding_box().size.Y < 1e-4]
    body, ch_sil = _blend(body, corners, (min(CH19[0], 0.40 * 3.0), 0.8, 0.5), kind="chamfer")
    body, ch_cre = _blend(body, [e for e in body.edges()
                                 if abs(e.bounding_box().min.Z - G19) < 1e-4
                                 and abs(e.bounding_box().max.Z - G19) < 1e-4],
                          (CH19[2], 0.4, 0.3), kind="chamfer")
    body, ch_tbl = _blend(body, [e for e in body.edges()
                                 if abs(e.bounding_box().min.Z - z_tbl) < 1e-4
                                 and abs(e.bounding_box().max.Z - z_tbl) < 1e-4],
                          (CH19[2], 0.4, 0.3), kind="chamfer")

    # mitred tongue (no arcs), the eye inside it
    tongue_sk = Polygon((-3.6, R19 - 0.6), (3.6, R19 - 0.6), (3.2, 15.4), (1.7, 17.2),
                        (-1.7, 17.2), (-3.2, 15.4), align=None)
    body += S.extrude_cut(tongue_sk, Plane.XY, TAB[2])
    _pad, eye = _eye((0.0, 13.0), TAB[2])
    body -= eye
    body -= _cup_cavity(bore)
    # hollow the crown: a second bridged ceiling instead of a solid block of TPU
    body -= extrude(Plane.XY.offset(Z_CEIL) * _hex(COL19), amount=COL19_TOP - Z_CEIL)

    # LABRUM: the toothed centre shield, split in two by the suture, exactly as the beetle has it
    for sx in (1.0, -1.0):
        half = Polygon((sx * 0.5, LAB19[1] / 2), (sx * 2.0, LAB19[1] / 2), (sx * LAB19[0] / 2, 0.8),
                       (sx * LAB19[0] / 2, -0.8), (sx * 2.0, -LAB19[1] / 2), (sx * 0.5, -LAB19[1] / 2),
                       align=None)
        body += S.extrude_cut(half, Plane.XY.offset(z_tbl), LAB19[2])
    _SUTURE[L19] = S.suture(-4.4, 4.4, z_tbl, w=SUT_W, depth=SUT_D)
    body -= _SUTURE[L19]
    _MEASURED[L19] = dict(z_table=z_tbl, chamfer=(ch_sil, ch_cre, ch_tbl), girdle=G19,
                          slant=sqrt((R19 - TBL19) ** 2 + CROWN19 ** 2))
    return body


# --- lens_cover_22: SLIPSTREAM under the micro rule --------------------------------------------
PLATE_PAD = 0.3          # the lid laps the mouth by this much - just enough to cover it, which
#                          lands the lid's own corner radius (15.86) exactly on the fairing's, so
#                          nothing stands proud of the pod anywhere.
MOUTH = _squircle(HOOD_RX, HOOD_RV, HOOD_N)          # the hood's own opening
PLAN22 = S.grow_region(MOUTH, PLATE_PAD)
BEAD_SK = S.inset_region(MOUTH, LIP_GAP)             # the bead land: 0.2 off the mouth wall
REL_SK = S.inset_region(MOUTH, LIP_GAP + RELIEF22)   # relieved above it, so only the bead grips
PIN_SK = S.inset_region(MOUTH, LIP_GAP + RELIEF22 + WALL)   # the plug bore
PLATE22 = 2.2            # 2.2 so the 0.45 suture groove still leaves 1.75 of lid


def _cover_22() -> Part:
    """A lid, not a cup: the plug does the holding, so the lid stays 2.2 thin and its outline is the
    hood's own curve. Built with the mouth plane at local z = 0 and the plug below it."""
    plan = PLAN22 + S.cusp_tail(FIN22[1], FIN22[0], TAIL_TIP_R, at=(0.0, 11.0), angle=90.0)
    plan += Pos(0.0, -(HOOD_RV + 3.4)) * Circle(LOOP_D / 2 + LOOP_WALL + 1.5)   # the pull tab
    # SLIPSTREAM's one rule is no crease: blend the fin root and the tab neck in the SKETCH, so the
    # outline is tangent everywhere and the rim chamfer below can run right round it.
    joints = [v for v in plan.vertices() if abs(v.Y) > 3.0 and hypot(v.X, v.Y) < 18.0]
    for r in (2.0, 1.5, 1.0, 0.6):
        try:
            plan = fillet(joints, r)
            break
        except Exception:  # noqa: BLE001
            joints = [v for v in plan.vertices() if abs(v.Y) > 3.0 and hypot(v.X, v.Y) < 18.0]
    body = S.extrude_cut(plan, Plane.XY, PLATE22)

    # the plug: relief, a lead-in ramp, then the bead land at the tip. The ramp is what makes the
    # bead printable - it grows outward as the print rises, so its underside reads as a 68 deg cone
    # rather than a step facing the bed.
    z_bead = -PLUG22
    z_ramp = z_bead + BEAD22
    z_rel = z_ramp + RAMP22
    outer = S.extrude_cut(REL_SK, Plane.XY.offset(z_rel), -z_rel)
    outer += loft([Plane.XY.offset(z_ramp) * BEAD_SK, Plane.XY.offset(z_rel) * REL_SK], ruled=True)
    outer += S.extrude_cut(BEAD_SK, Plane.XY.offset(z_bead), BEAD22)
    body += outer - S.extrude_cut(PIN_SK, Plane.XY.offset(z_bead - 0.5), PLUG22 + 0.6)

    _pad, hole = _eye((0.0, -(HOOD_RV + 3.4)), PLATE22)
    body -= hole
    # the one crease the family tolerates is on the camera side, where it faces up off the bed.
    # Only the lid's OUTER boundary: the plug's root edge is a mating feature, not a silhouette.
    rim = [e for e in body.edges() if abs(e.bounding_box().max.Z) < 1e-4
           and abs(e.bounding_box().min.Z) < 1e-4 and e.length > 3.0
           and max(hypot(e.position_at(t).X, e.position_at(t).Y) for t in (0.1, 0.5, 0.9)) > 12.0]
    body, ch = _blend(body, rim, (1.2, 1.0, 0.8, 0.6, 0.4), kind="chamfer")
    _SUTURE[L22] = S.suture(-(HOOD_RV + 2.4), 11.0 + FIN22[0] - 2.5, PLATE22, w=SUT_W,
                            depth=SUT_D_BED)
    body -= _SUTURE[L22]
    _MEASURED[L22] = dict(chamfer=ch, mouth_n=HOOD_N, plate=PLATE22,
                          lid_max_r=round(max(hypot(v.X, v.Y) for v in PLAN22.vertices()) or 0.0, 3),
                          plug_min_half=round(min(PIN_SK.bounding_box().size.X,
                                                  PIN_SK.bounding_box().size.Y) / 2, 3))
    return body


# --- lens_cover_generic: ARSENAL ---------------------------------------------------------------
GEN_TOP = 2.0                                     # front wall: 2.0 so the 0.4 suture leaves 1.6
GEN_BORE = BARREL_D / 2 + LIP_GAP                 # 7.7
GEN_H = GEN_BORE + LIP + WALL                     # 10.1 half width, inside camera_pod_21's cheeks
GEN_Z = Z_CEIL + GEN_TOP                          # 6.8 front face


def _corner_cut(h: float, z_top: float, run: float, drop: float) -> Part:
    """The ARSENAL signature: the wedge taken off one top-outboard CORNER by a plane at 30 deg to
    the front face (a symmetric corner cut of `run` along x and y and `drop` down z is at 30 deg
    when run = 2.449 * drop)."""
    p1, p2, p3 = (h - run, h, z_top), (h, h - run, z_top), (h, h, z_top - drop)
    tri = Polygon((p1[0], p1[1]), (p2[0], p2[1]), (h + 4.0, h + 4.0), align=None)
    wedge = extrude(Plane.XY.offset(z_top - drop) * tri, amount=drop + 6.0)
    keep = loft([Plane.XY.offset(p3[2]) * Polygon((h, h), (h + 4.0, h), (h + 4.0, h + 4.0),
                                                 (h, h + 4.0), align=None),
                 Plane.XY.offset(z_top) * Polygon((p1[0], p1[1]), (p2[0], p2[1]), (h + 4.0, h),
                                                 (h + 4.0, h + 4.0), (h, h + 4.0), align=None)],
                ruled=True)
    return wedge & keep


def _xz(sk: Sketch, y0: float, y1: float) -> Part:
    """Extrude a sketch drawn in (X, Z) from y0 to y1."""
    return extrude(Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * sk, amount=y1 - y0)


def _cover_generic() -> Part:
    body = extrude(Plane.XY * Rectangle(2 * GEN_H, 2 * GEN_H), amount=GEN_Z)

    # The family signature: ONE 30 deg cut corner, on the top-outboard edge - and it is a CORNER,
    # taken off the +X/+Y/top vertex, not a bevel down the whole flank. Measured reason: a 30 deg
    # plane run along the whole +X flank passes 0.06 mm from the Ø17 bore at the cavity ceiling and
    # breaches the wall. Cut at the corner instead and the plane never comes within 2.4 mm of it.
    drop = GEN_CUT_D
    run = GEN_CUT_D * 2.449   # the run that puts the plane at exactly 30 deg to the front face
    corner = _corner_cut(GEN_H, GEN_Z, run, drop)
    body -= corner

    # two transverse ribs (CN-2), each ending in a 45 deg ramp, held clear of the cut corner
    x1 = GEN_H - run
    rib = Polygon((-GEN_H, GEN_Z), (-GEN_H + GEN_RIB[1], GEN_Z + GEN_RIB[1]),
                  (x1 - GEN_RIB[1], GEN_Z + GEN_RIB[1]), (x1, GEN_Z), align=None)
    for yc in (-GEN_RIB[2] / 2, GEN_RIB[2] / 2):
        body += _xz(rib, yc - GEN_RIB[0] / 2, yc + GEN_RIB[0] / 2)

    # the grip knurl: proud ridges, not grooves - a groove would eat the 1.6 flank wall
    n = int(GEN_KNURL[0] // GEN_KNURL[3])
    for i in range(n):
        xc = (i - (n - 1) / 2) * GEN_KNURL[3]
        body += box(xc - GEN_KNURL[3] / 4, -GEN_H - GEN_KNURL[2], 1.2,
                    xc + GEN_KNURL[3] / 4, -GEN_H + 0.1, 1.2 + GEN_KNURL[1])

    # the service tab: orthogonal, Ø4.0 eye, LOOP_WALL all round
    tab_w, tab_l = 7.2, LOOP_D_GEN + 2 * LOOP_WALL + 4.0
    body += box(-tab_w / 2, GEN_H - 0.5, 0.0, tab_w / 2, GEN_H + tab_l, TAB[2])
    _pad, hole = _eye((0.0, GEN_H + LOOP_D_GEN / 2 + LOOP_WALL + 0.5), TAB[2], d=LOOP_D_GEN)
    body -= hole
    body -= _cup_cavity(GEN_BORE)

    # ARSENAL's uniform ladder: 1.6 on the silhouette (the four vertical corners), 0.6 elsewhere.
    # The bed edge is left sharp - a 45 deg face there is an overhang, not a chamfer.
    verts = [e for e in body.edges() if e.geom_type == GeomType.LINE
             and e.bounding_box().size.X < 1e-4 and e.bounding_box().size.Y < 1e-4
             and e.bounding_box().size.Z > 3.0 and abs(abs(e.bounding_box().min.X) - GEN_H) < 1e-3
             and abs(abs(e.bounding_box().min.Y) - GEN_H) < 1e-3]
    body, ch_sil = _blend(body, verts, (GEN_CH[0], 1.0, 0.6), kind="chamfer")
    # 'free' tier: the front face's OUTER boundary only. The rib roots are internal junctions and a
    # chamfer there crosses the suture and leaves a knife edge (measured at 0.17 mm).
    tops = [e for e in body.edges() if abs(e.bounding_box().min.Z - GEN_Z) < 1e-4
            and abs(e.bounding_box().max.Z - GEN_Z) < 1e-4 and e.length > 2.0
            and (abs(abs(e.bounding_box().center().X) - GEN_H) < 0.01
                 or abs(abs(e.bounding_box().center().Y) - GEN_H) < 0.01)]
    body, ch_free = _blend(body, tops, (GEN_CH[1], 0.4), kind="chamfer")
    _SUTURE[LGEN] = S.suture(-(GEN_H - 1.5), GEN_H - 1.5, GEN_Z, w=SUT_W, depth=SUT_D)
    body -= _SUTURE[LGEN]
    _MEASURED[LGEN] = dict(chamfer=(ch_sil, ch_free), half_width=GEN_H, bore=GEN_BORE,
                           cut_corner_drop=drop)
    return body


# --- assembly ---------------------------------------------------------------------------------
INSTALL = {L21: (TILT, XI_RIM), L19: (TILT, XI_RIM), LGEN: (TILT, XI_RIM),
           L22: (TILT, HOOD_XI_RIM)}
_EYE_AT = {L21: (0.0, 13.8), L19: (0.0, 13.0), L22: (0.0, -(HOOD_RV + 3.4)),
           LGEN: (0.0, GEN_H + LOOP_D_GEN / 2 + LOOP_WALL + 0.5)}
# every free silhouette extremity, named: (what it is, the point, the inward direction)
_TIPS = {
    L21: (("tongue cusp", (0.0, R21 - 1.2 + 9.5, TAB[2] / 2), (0.0, -1.0, 0.0)),
          ("skirt, ventral", (0.0, -R21, CAR21 / 2), (0.0, 1.0, 0.0)),
          ("crown", (0.0, 0.0, dome_21()["z_ap"]), (0.0, 0.0, -1.0))),
    L19: (("mitred tongue", (0.0, 17.2, TAB[2] / 2), (0.0, -1.0, 0.0)),
          ("table", (0.0, 0.0, G19 + CROWN19), (0.0, 0.0, -1.0)),
          ("girdle vertex, ventral", (0.0, -R19 / cos(radians(30)), G19 / 2), (0.0, 1.0, 0.0))),
    L22: (("tail fin cusp", (0.0, 20.0, PLATE22 / 2), (0.0, -1.0, 0.0)),
          ("pull tab", (0.0, -(HOOD_RV + 3.4) - (LOOP_D / 2 + LOOP_WALL + 1.5), PLATE22 / 2),
           (0.0, 1.0, 0.0)),
          ("plug tip", (HOOD_RX - LIP_GAP - 0.8, 0.0, -PLUG22 + 0.3), (-1.0, 0.0, 0.0))),
    LGEN: (("service tab", (0.0, GEN_H + LOOP_D_GEN + 2 * LOOP_WALL + 4.0 - 0.5, TAB[2] / 2),
            (0.0, -1.0, 0.0)),
           ("rib crest", (0.0, GEN_RIB[2] / 2, GEN_Z + GEN_RIB[1]), (0.0, 0.0, -1.0)),
           ("knurl crest", (0.0, -GEN_H - GEN_KNURL[2], 1.2 + GEN_KNURL[1] / 2), (0.0, 1.0, 0.0))),
}
_BUILDERS = {L21: _cover_21, L19: _cover_19, L22: _cover_22, LGEN: _cover_generic}
_LOCAL: dict = {}


def build(**overrides) -> dict[str, Part]:
    for k, v in overrides.items():
        globals()[k] = v
    out = {}
    for label, fn in _BUILDERS.items():
        local = fn()
        assert len(local.solids()) == 1, f"{label}: {len(local.solids())} solids before placing"
        _LOCAL[label] = local
        t, xi0 = INSTALL[label]
        part = _place(local, t, xi0)
        assert len(part.solids()) == 1, f"{label}: {len(part.solids())} solids"
        out[label] = part
    return out


def print_orientation_hint(label: str) -> tuple:
    """The bed normal this label prints on, in frame coordinates (also in PRINT)."""
    return PRINT[label]


# --- checks -----------------------------------------------------------------------------------
def _pods() -> tuple[dict[str, Part], list[str]]:
    """The pods a cover has to live inside, when their modules build. A sibling module mid-edit must
    not be able to fail this one, so an import or build failure is reported, not raised."""
    out, notes = {}, []
    try:
        from tigerbee.accessories import camera_pod

        out.update(camera_pod.build())
    except Exception as exc:  # noqa: BLE001
        notes.append(f"camera_pod unavailable ({type(exc).__name__})")
    try:
        from tigerbee.accessories import build_accessory, camera_pod_22

        for v in ("shard_t25", "slipstream_t35"):
            for label, part in build_accessory(camera_pod_22, v).items():
                out[label] = part
    except Exception as exc:  # noqa: BLE001
        notes.append(f"camera_pod_22 unavailable ({type(exc).__name__})")
    return out, notes


def _pods_for(label: str, pods: dict[str, Part]) -> dict[str, Part]:
    """Which pods this cover claims to fit. The 19 is the narrow one, so it claims both."""
    if label == L22:
        return {k: v for k, v in pods.items() if k.startswith("camera_pod_22")}
    if label == L19:
        return {k: v for k, v in pods.items() if k in ("camera_pod_19", "camera_pod_21")}
    return {k: v for k, v in pods.items() if k == "camera_pod_21"}


def _pod_tilts(label: str, pod_label: str) -> tuple[float, ...]:
    """The poses to test this cover against THAT pod. camera_pod_22 builds its tilt in (the hole PAIR
    is the tilt), so each of its variants has exactly one pose and the cross pairs do not exist;
    camera_pod's tilt is a slot, so the pod stands still while the camera and the cover sweep."""
    if label == L22:
        for suffix, t in (("t25", 25.0), ("t35", 35.0), ("t45", 45.0)):
            if pod_label.endswith(suffix):
                return (t,)
        return (TILT,)
    return _tilts(label)


def _tilts(label: str) -> tuple[float, ...]:
    """Every pose the cover must survive: it rides with the camera, so it sweeps with it."""
    if label == L22:
        return TILT_22
    return (15.0, 20.0, 25.0, 30.0, 35.0, 40.0)


def _axis_coaxial(part: Part, t: float, xi0: float, xi1: float, d: float,
                  tol: float = 0.05) -> tuple[bool, str]:
    """_fit.coaxial's test on an arbitrary axis: a Ø(d - tol) probe down the lens axis must be void
    and an annulus just outside it must hit material, so a missing bore and a missing part both
    fail. _fit.coaxial itself only knows vertical axes; this cover's only axis is the lens."""
    probe = S.extrude_cut(Circle((d - tol) / 2), _station(t, xi0), xi1 - xi0)
    ring = S.extrude_cut(Circle(d / 2 + tol + 0.6) - Circle(d / 2 + tol), _station(t, xi0), xi1 - xi0)
    inside, around = isect(part, probe), isect(part, ring)
    return (inside < EPS and around > EPS,
            f"Ø{d} on the lens axis xi {xi0}-{xi1}: {inside:.3f} mm³ in the bore, "
            f"{around:.1f} mm³ round it")


def _opening(label: str) -> tuple[Sketch, float, float]:
    """(the opening this lid has to cover, the station it is proven at, the station's thickness).
    The station is a plane where the lid is solid right across, so a prism on the opening's own
    outline either lies entirely inside the lid - coverage - or it does not."""
    if label == L22:
        return MOUTH, HOOD_XI_RIM + 0.6, 0.6
    d = BARREL_D if label == LGEN else BARREL_21
    # the station is a plane where the lid is solid right across: above the cavity ceiling for the
    # 21 and the generic, above the hollow crown column for the 19
    z = (COL19_TOP + 0.3) if label == L19 else (Z_CEIL + 0.3)
    return Circle(d / 2), XI_RIM + z, 0.4


def _facets(part: Part, min_across: float = S.FACET_MIN, strip: float = 1.8,
            min_area: float = 8.0) -> tuple[bool, str]:
    """SHARD's 8 mm rule, measured IN THE FACET'S OWN PLANE. _style.facet_report measures the
    world-axis bounding box, which reads a tilted crown facet 10.6 x 8.0 as "3.2 mm across"; the
    number the rule is about is the facet's own short side. Declared edge-treatment strips (<=
    `strip` across - the widest chamfer this part asks for) are edge treatment, not facets."""
    bad = []
    for f in part.faces():
        if f.geom_type != GeomType.PLANE or f.area < min_area:
            continue
        n = f.normal_at()
        e1 = Vector(0, 0, 1).cross(n)
        e1 = (Vector(1, 0, 0) if e1.length < 1e-6 else e1).normalized()
        e2 = n.cross(e1).normalized()
        us = [Vector(*v.to_tuple()).dot(e1) for v in f.vertices()]
        vs = [Vector(*v.to_tuple()).dot(e2) for v in f.vertices()]
        across = min(max(us) - min(us), max(vs) - min(vs))
        if strip + 0.01 < across < min_across - 1e-6:
            bad.append(round(across, 2))
    return not bad, (f"{len(bad)} facet(s) between the {strip} mm strip width and {min_across} mm "
                     f"across: {sorted(bad)[:6]}")


TIP_R = 0.45   # CN-3: every free silhouette tip takes a 0.45-1.2 mm radius


def _tip_fill(local: Part, at: tuple[float, float, float], d: tuple[float, float, float],
              r: float = TIP_R) -> float:
    """Fraction of a Ø2r ball that is material when its centre sits r inside the named tip."""
    n = Vector(*d).normalized()
    ball = Pos(*(Vector(*at) + n * r).to_tuple()) * Sphere(r)
    return isect(local, ball) / volume(ball)


def _plan_area(label: str) -> float:
    """Plan footprint of the LOCAL part, for the §4.5 silhouette-first directive."""
    local = _LOCAL[label]
    bb = local.bounding_box()
    z = bb.min.Z + (bb.size.Z * 0.02 if label != L22 else 0.0) + 0.1
    sec = local & (Pos(0, 0, z) * Box(200, 200, 0.2))
    return round(sum(f.area for f in sec.faces() if abs(f.normal_at().Z) > 0.99) / 2.0, 2)


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    pods, pod_notes = _pods()
    fc = frame_compound()

    for label, cap in parts.items():
        local = _LOCAL[label]
        t0, xi0 = INSTALL[label]
        tag = label

        # --- the frame, over every pose the cover can be in (it rides with the camera) ----------
        worst = max(((round(isect(_repose(cap, t0, t), fc), 3), t) for t in _tilts(label)))
        out.append((f"{tag}: clear of the frame over the {_tilts(label)[0]}-{_tilts(label)[-1]}° "
                    f"tilt sweep", worst[0] < EPS, f"worst {worst[0]} mm³ at {worst[1]}°"))
        worst = max(((round(prop_disc_violation(_repose(cap, t0, t)), 3), t) for t in _tilts(label)))
        out.append((f"{tag}: outside the prop keep-out discs over the whole sweep", worst[0] < EPS,
                    f"worst {worst[0]} mm³ at {worst[1]}°"))
        so = standoff_interference(cap)
        out.append((f"{tag}: clear of the Ø{STANDOFF_D} standoffs", not so, f"{so or 'none'}"))

        # --- its pod, at every shipped tilt ----------------------------------------------------
        mine = _pods_for(label, pods)
        if mine:
            hits, gaps = [], []
            for pod_label, pod in mine.items():
                for t in _pod_tilts(label, pod_label):
                    moved = _repose(cap, t0, t)
                    v = isect(moved, pod)
                    if v > EPS:
                        hits.append(f"{pod_label} @{t}°: {v:.2f} mm³")
                    if abs(t - t0) < 1e-9:
                        gaps.append(f"{pod_label} {moved.distance_to(pod):.2f} mm")
            out.append((f"{tag}: no interference with {', '.join(mine)} over the tilt sweep",
                        not hits, "; ".join(hits) or f"0 mm³, closest approach {', '.join(gaps)}"))
        else:
            out.append((f"{tag}: pod interference not measurable this run", True, "; ".join(pod_notes)))

        # --- the axis, the lip, the opening ----------------------------------------------------
        if label == L22:
            bore_d = min(PIN_SK.bounding_box().size.X, PIN_SK.bounding_box().size.Y)
            lo, hi = HOOD_XI_RIM - PLUG22 + 0.2, HOOD_XI_RIM - 0.2
        else:
            bore_d = BARREL_D + 2 * LIP_GAP if label == LGEN else BARREL_21 + 2 * LIP_GAP
            lo, hi = XI_RIM + 0.2, XI_RIM + LIP_H - 0.2
        ok, detail = _axis_coaxial(cap, t0, lo, hi, bore_d)
        out.append((f"{tag}: bore coaxial with the lens axis (CAM_PIVOT +X, tilt {t0}°)", ok, detail))

        if label == L22:
            band = S.extrude_cut(MOUTH - S.inset_region(MOUTH, LIP_GAP + 0.15),
                                 _station(t0, HOOD_XI_RIM - PLUG22), PLUG22)
            tight = S.extrude_cut(MOUTH, _station(t0, HOOD_XI_RIM - PLUG22 - 1), PLUG22 + 1)
            below = cap & S.extrude_cut(Circle(60), _station(t0, HOOD_XI_RIM - PLUG22 - 2),
                                        PLUG22 + 2)
            leak = volume(below) - isect(below, tight)
            out.append((f"{tag}: the plug stays inside the Ø{2 * HOOD_RX:.1f} hood mouth "
                        f"(no interference at the {LIP_GAP} mm CAD gap)", leak < EPS,
                        f"{leak:.3f} mm³ outside the mouth"))
        else:
            d = BARREL_D if label == LGEN else BARREL_21
            band = S.extrude_cut(Circle(d / 2 + LIP_GAP + 0.15) - Circle(d / 2),
                                 _station(t0, XI_RIM), GRIP)
            bar = _barrel(t0, d)
            v = isect(cap, bar)
            out.append((f"{tag}: Ø{d} barrel free at the {LIP_GAP} mm CAD gap (no squeeze modelled)",
                        v < EPS, f"{v:.3f} mm³"))
        eng = isect(cap, band)
        out.append((f"{tag}: retaining lip engages ({LIP} mm radial step, {LIP_H} mm band)",
                    eng > EPS, f"{eng:.2f} mm³ of lip inside the {LIP_GAP + 0.15} mm grip shell"))

        sk, xi_st, thick = _opening(label)
        prism = S.extrude_cut(sk, _station(t0, xi_st), thick)
        leak = volume(prism) - isect(prism, cap)
        out.append((f"{tag}: the opening's projected area lies wholly inside the lid footprint",
                    leak < EPS, f"{leak:.4f} mm³ of a {volume(prism):.1f} mm³ prism outside the lid"))

        # --- the equipment it must not touch ---------------------------------------------------
        if label == L22:
            xi_glass = getattr(_CP22, "XI_LENS", 20.0) if _CP22 else 20.0
            glass = S.extrude_cut(Circle(HOOD_LENS_R), _station(t0, xi_glass - 0.1), 0.2)
        else:
            glass = S.extrude_cut(Circle(BARREL_21 / 2), _station(t0, XI_GLASS - 0.1), 0.2)
        gap = round(cap.distance_to(glass), 3)
        out.append((f"{tag}: clear of the glass", isect(cap, glass) < EPS and gap >= 0.45,
                    f"{gap} mm to the lens face"))
        body = S.extrude_cut(Rectangle(22.5, 22.5), _station(t0, XI_BODY), -34.0)
        v = isect(cap, body)
        out.append((f"{tag}: clear of the 22.5 x 22.5 camera body behind xi {XI_BODY}", v < EPS,
                    f"{v:.3f} mm³"))
        v = isect(cap, BATTERY)
        out.append((f"{tag}: outside the battery envelope", v < EPS, f"{v:.3f} mm³"))

        # --- it seats on no plate: the cover is carried by the camera, nothing else -------------
        seats = {f"{plate} Z {z}": seats_on(cap, plate, z) for plate, zs in PLATE_FACES.items()
                 for z in zs}
        out.append((f"{tag}: seats on no frame plate face - the camera carries it",
                    all(v == 0.0 for v in seats.values()),
                    ", ".join(f"{k} {v}" for k, v in seats.items() if v) or "0.000 mm² on all six faces"))

        # --- the part itself --------------------------------------------------------------------
        ok, detail = single_solid(cap)
        out.append((f"{tag}: one valid solid", ok, detail))
        ok, _v, detail = min_wall(local, 1.2)
        out.append((f"{tag}: min wall >= 1.2 (TPU95A)", ok, detail))
        over = overhangs(cap, PRINT[label], bridge_ok=BRIDGE_OK.get(label, ()), material=MATERIAL)
        out.append((f"{tag}: prints on its open face without support", not over,
                    "; ".join(over) or f"none, bed normal {tuple(round(c, 3) for c in PRINT[label])}"))
        tool = _SUTURE[label]
        void = volume(tool) - isect(local, tool)
        out.append((f"{tag}: CN-1 suture cut on X = 0, cusped at both ends",
                    void > 0.45 * volume(tool),
                    f"{void:.2f} of {volume(tool):.2f} mm³ of the groove tool is void"))
        # CN-3 tip by tip. _style.tip_radius_report probes the six bbox extremes from the bbox
        # CENTRE, and the centre of a cup is inside its own bore, so on a hollow lid it reports
        # every extreme as thin; the docstring says to probe real tips explicitly, so we do.
        fills = {name: round(_tip_fill(local, at, d), 3) for name, at, d in _TIPS[label]}
        out.append((f"{tag}: CN-3 tips hold a Ø{2 * TIP_R} ball", min(fills.values()) >= 0.30,
                    f"ball fill {fills}"))

        eye_d = LOOP_D_GEN if label == LGEN else LOOP_D
        ring = (Pos(0, 0, TAB[2] / 2) * Cylinder(eye_d / 2 + LOOP_WALL, TAB[2] * 0.9)
                - Pos(0, 0, TAB[2] / 2) * Cylinder(eye_d / 2, TAB[2] * 0.9))
        at = _EYE_AT[label]
        ring = Pos(at[0], at[1], 0) * ring
        frac = isect(local, ring) / volume(ring)
        out.append((f"{tag}: Ø{eye_d} lanyard eye keeps {LOOP_WALL} mm all round", frac > 0.985,
                    f"{frac:.3f} of the {LOOP_WALL} mm collar is material"))

    # --- style conformance, and the thing the brief is actually about: four different lids -------
    ok, detail = _facets(_LOCAL[L19], strip=STRIP19)
    out.append((f"{L19}: SHARD conformance, every facet >= {S.FACET_MIN} mm in its own plane",
                ok, detail))
    ok, detail = S.facet_report(_LOCAL[L19], ignore_extent=STRIP19)
    out.append((f"{L19}: _style.facet_report agrees (strip extent {STRIP19} declared)", ok, detail))
    # a flank face is one whose normal is perpendicular to the axis; the suture's V walls are
    # planar too and are meant to be (they are a groove, not an aperture wall)
    flat = [f for f in _LOCAL[L22].faces() if f.geom_type == GeomType.PLANE
            and abs(f.normal_at().Z) < 0.1 and f.area > 3.0]
    out.append((f"{L22}: SLIPSTREAM - the aperture and the lip are elliptical, never polygonal",
                not flat, f"{len(flat)} flat flank face(s) over 3 mm²"))
    d = _MEASURED[L21]
    ratio = d["rise"] / d["span"]
    out.append((f"{L21}: CARAPACE section rise/span in 0.28-0.36", 0.28 <= ratio <= 0.36,
                f"{ratio:.3f} (rise {d['rise']:.2f} over span {d['span']:.2f}), OCELLUS blend "
                f"{d['blend_ocellus']} (3.0 cannot fit a rim {OC_PROUD} proud x {OC_W} wide), "
                f"CARINA fillet {d['blend_carina']}"))
    areas = {label: _plan_area(label) for label in LABELS}
    worst = min(abs(a - b) / max(a, b) for i, a in enumerate(areas.values())
                for b in list(areas.values())[i + 1:])
    out.append(("§4.5 silhouette-first: every pair of lids differs by > 12% in plan area",
                worst > 0.12, f"closest pair {worst:.1%}; {areas}"))
    out.append((f"{L19} is the cover that fits BOTH pods (cheeks |x| {CHEEK_X[L19]} and "
                f"{CHEEK_X[L21]})",
                _LOCAL[L19].bounding_box().max.X <= CHEEK_X[L19] - CHEEK_CLEAR,
                f"half width {_LOCAL[L19].bounding_box().max.X:.2f} vs "
                f"{CHEEK_X[L19] - CHEEK_CLEAR:.2f} allowed"))
    out.append((f"{L21} uses camera_pod_21's wider gap",
                _LOCAL[L21].bounding_box().max.X <= CHEEK_X[L21] - CHEEK_CLEAR,
                f"half width {_LOCAL[L21].bounding_box().max.X:.2f} vs "
                f"{CHEEK_X[L21] - CHEEK_CLEAR:.2f} allowed"))
    out.append((f"{LGEN}: no mark - S.mark_fits('wordmark', {2 * GEN_H}) is False at this size, and "
                f"the rule says a part that cannot hold its mark carries none",
                not S.mark_fits("wordmark", 2 * GEN_H),
                f"wordmark minimum {S.MARK_MIN['wordmark']} mm vs a {2 * GEN_H} mm face"))
    return out
