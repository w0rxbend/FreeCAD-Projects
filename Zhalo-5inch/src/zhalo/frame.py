"""The carbon parts (three plates, one arm used four times, one brace used twice), the
standoffs, and the assembled frame.

Every carbon part is a flat `Sheet`: an outline, round holes and windows in its own flat
coordinates plus a thickness. The same 2D face goes to the DXF for the CNC shop and is
extruded for the 3D model, so the two cannot drift apart.
"""

from dataclasses import dataclass, field, replace
from functools import lru_cache
from math import cos, hypot, radians, sin, sqrt

from build123d import Align, Axis, Compound, Cylinder, Face, Part, Plane, Pos, Vector, Wire, extrude, fillet

from zhalo import params as P
from zhalo.outline import (
    XY,
    belt,
    bite,
    chevron,
    circle,
    cross,
    face,
    lobe,
    mirrored,
    polygon,
    rounded_poly,
    rounded_rect,
    scallop,
    slot,
)

MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)
CARBON = "carbon"
ALUMINIUM = "aluminium"


@dataclass(frozen=True)
class Hole:
    name: str
    purpose: str
    x: float
    y: float
    d: float


@dataclass
class Sheet:
    name: str
    thickness: float
    outline: Face  # outer boundary only
    holes: list[Hole] = field(default_factory=list)
    windows: list[Wire] = field(default_factory=list)
    count: int = 1

    def face(self) -> Face:
        f = face(self.outline.outer_wire(), [*self.windows, *(circle((h.x, h.y), h.d) for h in self.holes)])
        return f

    def solid(self) -> Part:
        part = extrude(self.face(), amount=self.thickness)
        part.label = self.name
        return part


def _holes(name: str, purpose: str, points: list[XY], d: float = P.D_M3) -> list[Hole]:
    return [Hole(name, purpose, x, y, d) for x, y in points]


def _square(center: XY, pitch: float) -> list[XY]:
    h = pitch / 2
    return [(center[0] + sx * h, center[1] + sy * h) for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1))]


# --- hard points --------------------------------------------------------------------------
B_F, C_F = P.B, P.C
B_R, C_R = (P.B[0], -P.B[1]), (P.C[0], -P.C[1])
VTX_FRONT = (P.VTX_PITCH_LARGE / 2, P.VTX_BAY_Y + P.VTX_PITCH_LARGE / 2)  # (15.25, -30.75)
VTX_REAR = (P.VTX_PITCH_LARGE / 2, P.VTX_BAY_Y - P.VTX_PITCH_LARGE / 2)  # (15.25, -61.25)
WAIST_X = 23.0  # half-width of the sandwich between the legs (the ESC is 45.6 wide)
WAIST_Y = 22.0
NOSE = (9.0, 73.0)  # nose shoulder of the bottom plate: the nose ends at Y 79
STINGER_Y = -85.0
PRONG = (13.2, 75.5)  # tip of the top plate's camera fork: it ends at Y 78.9
FORK = ((0.0, 58.0), 9.4)  # the fork's round bottom
TAIL_NOTCH = ((0.0, -81.0), 9.0)


def _link(node, radius: float):
    return replace(node, link=radius)


# --- plates ---------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def bottom_plate() -> Sheet:
    r, leg = P.LOBE_R, P.LEG_R
    tail = lobe((0.0, STINGER_Y), 1.8)
    n_r = lobe(P.R, r)
    v_r = lobe(VTX_REAR, r)
    c_r, c_f = lobe(C_R, leg), lobe(C_F, leg)
    f, nose = lobe(P.F, r), lobe(NOSE, 6.0)
    # The front 30.5 VTX hole and the accessory hole A1 sit in the crotch between a leg and the
    # body, so they are not lobes of their own: the scallops run from lobe to leg tip past them.
    right = [
        n_r,
        _link(v_r, scallop(v_r, c_r, 8.5)),
        _link(c_r, scallop(c_r, c_f, C_R[0] + leg - WAIST_X)),
        _link(c_f, scallop(c_f, f, 5.0)),
        f,
        nose,
    ]
    tail = _link(tail, scallop(tail, n_r, 3.0))
    outline = face(belt(mirrored(right, bottom=tail)))
    holes = [
        *_holes("stack", "30.5 stack bolt, also clamps the arm roots", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + 28 mm standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
        *_holes("front_standoff", "35 mm standoff, camera mount", P.pair(P.F)),
        *_holes("rear_standoff", "35 mm standoff, antenna mount", P.pair(P.R)),
        *_holes("accessory", "optional 35 mm standoff / accessory", P.pair(P.A1)),
        *_holes("vtx_30p5", "analog VTX 30.5 x 30.5", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_LARGE)),
        *_holes("vtx_20", "analog VTX 20 x 20", _square((0, P.VTX_BAY_Y), P.VTX_PITCH_SMALL)),
        *_holes("nose", "nose bumper screw", [P.NOSE_HOLE]),
    ]
    windows = [
        rounded_rect((0, 0), 12, 12, 2.5),
        rounded_rect((0, P.VTX_BAY_Y), 10, 10, 2.0),
        chevron((0, 27.5), 8.5, 5.0, 4.4),
        chevron((0, 38.5), 8.5, 5.0, 4.4),
        rounded_rect((0, 56.5), 17, 10, 2.5),
        chevron((0, -70.5), 6.0, 4.0, 4.0, flip=True),
    ]
    return Sheet("plate_bottom", P.T_BOTTOM, outline, holes, windows)


@lru_cache(maxsize=1)
def mid_plate() -> Sheet:
    leg = P.LEG_R
    rr, fr, fl, rl = (lobe((sx * P.C[0], sy * P.C[1]), leg) for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1)))
    side = scallop(rr, fr, P.C[0] + leg - WAIST_X)
    end = scallop(fr, fl, P.C[1] + leg - WAIST_Y)
    nodes = [_link(rr, side), _link(fr, end), _link(fl, side), _link(rl, end)]
    outline = face(belt(nodes))
    holes = [
        *_holes("stack", "30.5 stack bolt", P.quad(P.S)),
        *_holes("arm_inner", "arm bolt + 28 mm standoff", P.quad(P.B)),
        *_holes("arm_outer", "arm bolt + nyloc", P.quad(P.C)),
    ]
    return Sheet("plate_mid", P.T_MID, outline, holes, [cross((0, 0), 13.0, 8.0, 2.0)])


CHEVRON_Y = (-54.0, -43.0, -32.0, -21.0, -10.0, 1.0, 12.0, 23.0, 34.0)
STRAP_SLOTS = [((sx * 14.5, sy * 13.0), 3.6, 22.0) for sx in (1, -1) for sy in (1, -1)]  # centre, w, l


@lru_cache(maxsize=1)
def top_plate() -> Sheet:
    r = P.LOBE_R
    n_r, b_r, al, b_f = lobe(P.R, r), lobe(B_R, r), lobe(P.AL, 4.4), lobe(B_F, r)
    a1, f, prong = lobe(P.A1, r), lobe(P.F, r), lobe(PRONG, 3.4)
    right = [
        _link(n_r, scallop(n_r, b_r, 6.5)),
        _link(b_r, scallop(b_r, al, 8.5)),
        _link(al, scallop(al, b_f, 8.5)),
        _link(b_f, scallop(b_f, a1, 5.5)),
        _link(a1, scallop(a1, f, 2.2)),
        f,
        prong,
    ]
    outline = face(belt(mirrored(right, top=bite(*FORK), bottom=bite(*TAIL_NOTCH))))
    holes = [
        *_holes("front_standoff", "35 mm standoff; GoPro mount front screws", P.pair(P.F)),
        *_holes("stack_standoff", "28 mm standoff", P.quad(P.B)),
        *_holes("rear_standoff", "35 mm standoff; GPS / XT60 mount screws", P.pair(P.R)),
        *_holes("accessory", "GoPro mount rear screws / optional standoff", P.pair(P.A1)),
        *_holes("side_accessory", "accessory lobe", P.pair(P.AL)),
    ]
    windows = [chevron((0, y), 8.5, 5.0, 4.4) for y in CHEVRON_Y]
    windows += [slot((x, y - l / 2 + w / 2), (x, y + l / 2 - w / 2), w) for (x, y), w, l in STRAP_SLOTS]
    return Sheet("plate_top", P.T_TOP, outline, holes, windows)


# --- arm ------------------------------------------------------------------------------------
ARM_GUIDE_R = 2.0  # radius of the guide circles the flanks are tangent to
LUG_FILLET = 4.0
PAD_FILLET = 9.0
ROOT_FILLET = 1.0


def arm_to_frame(u: float, v: float, quadrant: str = "front_right") -> XY:
    x, y = P.on_arm(u, v)
    return (x if "right" in quadrant else -x, y if "front" in quadrant else -y)


def frame_to_arm(x: float, y: float) -> XY:
    """Frame XY -> front-right arm coordinates (u, v)."""
    dx, dy = x - P.S[0], y - P.S[1]
    return dx * P.ARM_DIR[0] + dy * P.ARM_DIR[1], -dx * P.ARM_DIR[1] + dy * P.ARM_DIR[0]


def motor_bolts(center: XY, axis_deg: float = 0.0) -> list[XY]:
    """The four motor screws, 45 deg off the arm axis so the wires leave along the arm."""
    r = P.MOTOR_PATTERN / sqrt(2)
    return [
        (center[0] + r * cos(radians(axis_deg + 45 + 90 * k)), center[1] + r * sin(radians(axis_deg + 45 + 90 * k)))
        for k in range(4)
    ]


def motor_slots(center: XY, axis_deg: float = 0.0) -> list[Wire]:
    out = []
    for x, y in motor_bolts(center, axis_deg):
        ux, uy = (
            (x - center[0]) / hypot(x - center[0], y - center[1]),
            (y - center[1]) / hypot(x - center[0], y - center[1]),
        )
        h = P.MOTOR_SLOT / 2
        out.append(slot((x - ux * h, y - uy * h), (x + ux * h, y + uy * h), P.D_M3))
    return out


@lru_cache(maxsize=1)
def arm() -> Sheet:
    """Flat arm in its own coordinates: stack bolt at the origin, motor at (ARM_LEN, 0)."""
    length, hw, g = P.ARM_LEN, P.arm_half_width, ARM_GUIDE_R

    def guide(u: float, side: int, link: float = 0.0):
        return lobe((u, side * (hw(u) - g)), g, link)

    lug_v = -(hw(P.LUG_U) + P.LUG_OFFSET)
    nodes = [
        guide(-45, -1),
        guide(0, -1),
        guide(P.LUG_U - 9.5, -1, LUG_FILLET),
        lobe((P.LUG_U, lug_v), P.LUG_R, LUG_FILLET),
        guide(P.LUG_U + 9.5, -1),
        guide(P.ARM_NECK_U, -1, PAD_FILLET),
        lobe((length, 0), P.MOTOR_PAD_R, PAD_FILLET),
        guide(P.ARM_NECK_U, 1),
        guide(0, 1),
        guide(-45, 1),
    ]
    blank = face(belt(nodes))
    # The root: keep what lies in the front-right quadrant (the neighbours own the other three),
    # then open a slot round the stack bolt so the arm can be pulled out along its own axis.
    far = 400.0
    corners = ((P.ARM_GAP, P.ARM_GAP), (far, P.ARM_GAP), (far, far), (P.ARM_GAP, far))
    quadrant = face(polygon([frame_to_arm(*p) for p in corners]))
    stack_slot = face(slot((-45, 0), (0, 0), P.STACK_SLOT_W))
    root = (blank & quadrant) - stack_slot
    outline = _round_root(root.faces()[0])
    holes = [
        *_holes("arm_inner", "arm bolt + standoff", [(P.ARM_BOLT_U[0], 0)]),
        *_holes("arm_outer", "arm bolt + nyloc", [(P.ARM_BOLT_U[1], 0)]),
        *_holes("brace", "brace bolt", [(P.LUG_U, lug_v)]),
    ]
    pad = (length, 0)
    windows = [*motor_slots(pad), circle(pad, P.MOTOR_BORE_D)]
    for k in range(4):
        a = radians(90 * k)
        windows.append(_rotated_diamond((length + 10.2 * cos(a), 10.2 * sin(a)), 5.4, 6.6, 90 * k))
    return Sheet("arm", P.T_ARM, outline, holes, windows, count=4)


def _rotated_diamond(center: XY, radial: float, tangential: float, deg: float) -> Wire:
    a = radians(deg)
    ux, uy = cos(a), sin(a)
    x, y = center
    pts = [
        (x + ux * radial / 2, y + uy * radial / 2),
        (x - uy * tangential / 2, y + ux * tangential / 2),
        (x - ux * radial / 2, y - uy * radial / 2),
        (x + uy * tangential / 2, y - ux * tangential / 2),
    ]
    return rounded_poly(pts, 1.0)


def _round_root(f: Face) -> Face:
    """Break the sharp corners the quadrant cut leaves on the two root prongs."""
    sharp = [v for v in f.vertices() if v.X < 6.0 and _is_corner(f, v)]
    try:
        out = fillet(sharp, ROOT_FILLET)
        rounded = out.faces()[0] if hasattr(out, "faces") else out
        if rounded.is_valid and rounded.area > 0.9 * f.area:
            return rounded
    except Exception:  # noqa: BLE001 - OCCT refuses some corner sets; the sharp root is still valid
        pass
    return f


def _is_corner(f: Face, v) -> bool:
    edges = [
        e for e in f.edges() if any((Vector(v.X, v.Y, v.Z) - Vector(w.X, w.Y, w.Z)).length < 1e-6 for w in e.vertices())
    ]
    if len(edges) != 2:
        return False
    here = Vector(v.X, v.Y, v.Z)
    tangents = []
    for e in edges:
        t0, t1 = e.position_at(0), e.position_at(1)
        tangents.append(e.tangent_at(0) if (t0 - here).length < (t1 - here).length else e.tangent_at(1))
    return abs(tangents[0].cross(tangents[1]).Z) > 0.05


# --- brace ----------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def brace() -> Sheet:
    """Side brace between the lugs of the front and rear arm, flat along +Y, centred on the origin."""
    y_end, y_acc = P.LUG[1], P.BRACE_ACC_Y
    lo, a_lo, a_hi, hi = (
        lobe((0, -y_end), P.LUG_R),
        lobe((0, -y_acc), 4.3),
        lobe((0, y_acc), 4.3),
        lobe((0, y_end), P.LUG_R),
    )
    waist = scallop(lo, a_lo, 1.2)
    nodes = [_link(lo, waist), a_lo, _link(a_hi, waist), _link(hi, waist), a_hi, _link(a_lo, waist)]
    holes = [
        *_holes("lug", "bolt into the arm lug", [(0, -y_end), (0, y_end)]),
        *_holes("accessory", "skid / accessory", [(0, -y_acc), (0, y_acc)]),
    ]
    return Sheet("brace", P.T_BRACE, face(belt(nodes)), holes, [], count=2)


# --- standoffs and assembly -----------------------------------------------------------------
def standoff(height: float) -> Part:
    """Round M3 standoff standing on Z = 0."""
    return Cylinder(P.STANDOFF_OD / 2, height, align=MIN_Z) - Pos(0, 0, -1) * Cylinder(1.25, height + 2, align=MIN_Z)


def _placed(
    sheet: Sheet, z: float, angle: float = 0.0, at: XY = (0, 0), mirror_x: bool = False, mirror_y: bool = False
) -> Part:
    part = sheet.solid().rotate(Axis.Z, angle).translate(Vector(at[0], at[1], z))
    if mirror_x:
        part = part.mirror(Plane.YZ)
    if mirror_y:
        part = part.mirror(Plane.XZ)
    return part


@lru_cache(maxsize=1)
def build() -> dict[str, tuple[Part, str]]:
    """Every solid of the frame in its installed position: name -> (part, material)."""
    out: dict[str, tuple[Part, str]] = {
        "plate_bottom": (_placed(bottom_plate(), P.Z_BOTTOM), CARBON),
        "plate_mid": (_placed(mid_plate(), P.Z_MID), CARBON),
        "plate_top": (_placed(top_plate(), P.Z_TOP), CARBON),
    }
    for name in P.MOTORS:
        out[f"arm_{name}"] = (
            _placed(arm(), P.Z_ARM, P.ARM_ANGLE, P.S, mirror_x="left" in name, mirror_y="rear" in name),
            CARBON,
        )
    for side, sx in (("right", 1), ("left", -1)):
        out[f"brace_{side}"] = (_placed(brace(), P.Z_BRACE, at=(sx * P.LUG[0], 0)), CARBON)
    for name, (x, y, z0, h) in P.STANDOFFS.items():
        out[name] = (standoff(h).translate(Vector(x, y, z0)), ALUMINIUM)
    for name, (part, _m) in out.items():
        part.label = name
    return out


def parts() -> dict[str, Part]:
    return {name: part for name, (part, _m) in build().items()}


def compound() -> Compound:
    return Compound(children=list(parts().values()), label="zhalo_frame")


SHEETS = {"plate_bottom": bottom_plate, "plate_mid": mid_plate, "plate_top": top_plate, "arm": arm, "brace": brace}
