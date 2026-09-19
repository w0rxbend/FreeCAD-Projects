"""50 deg rearward RX antenna mast bolted to the tail of the top plate."""

from math import cos, hypot, radians, sin, sqrt, tan

from build123d import (Align, Axis, Box, Circle, GeomType, Part, Plane, Polygon, Pos, Rectangle,
                       Vector, extrude, fillet)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "antenna_mast"
TITLE = "915 MHz antenna mast"
MATERIAL = "TPU95A"
PRINT = {"antenna_mast": (0, 0, -1)}  # bracket underside on the bed; the mast leans 50 deg
EXCLUSIVE = ()  # coexists with tail_block, which builds TOWER=False for the combined assembly
NOTES = ("Two M3 x 10 buttons replace the rear-tip standoff bolts and clamp the bracket onto "
         "plate_top; the bracket bridges the U-notch and carries the mast past the plate. "
         "The T-bar snaps into the head grooves (zip tie through the slots), the coax lies in "
         "the slit and drops through the mast foot into the top-plate notch. "
         "Departures from the sketch, each forced by a check: the nose is 32 wide at y -84 "
         "instead of 16 (a bracket that narrow seats on only ~267 mm2 of prong, not 300); the "
         "root sits at y -104 and the tongue runs to y -112, so the root ellipse and its r3 "
         "fillet clear the pack by 2.4 mm and still land on the bracket - trimming the root "
         "with a plane instead leaves a knife edge along the leaning rod; the bar grooves run "
         "the full 26 mm head because a 90 mm bar cannot enter a 22 mm pocket; the head is 15 "
         "wide, since at 12 the groove mouths come within 0.1 mm of the rounded corners.")

# --- parameters (mm, deg) --------------------------------------------------------------------
MAST_ANGLE = 50.0  # elevation of the mast above horizontal, leaning rearward
MAST_LEN = 36.0  # root plane to the head centre, along the mast axis
MAST_D = 8.0
ROOT_Y = -104.0  # mast axis crosses the bracket top face here; far enough back that
#                  the root ellipse and its fillet clear BATTERY without a trim cut
#                  (any plane trimming the leaning rod feathers out to a knife edge)
BRACKET_T = 2.5  # Z 36.0 (seated on plate_top) .. 38.5
BOLT_XY = REAR_TIP_XY  # (16.5, -94), mirrored: the rear-tip standoff axes
FRONT_X, FRONT_Y = 16.0, -84.0  # bracket nose (wider than the 8 of the first sketch: seating area)
WIDE_X, WIDE_Y0, WIDE_Y1 = 22.0, -87.0, -97.0  # full-width flanks over the two prongs
TAIL_X, TAIL_Y = 8.0, -112.0  # rearward tongue that carries the mast root and its fillet
EDGE_R = 3.0
ROOT_R = 3.0  # root fillet between the mast and the bracket top face
BATTERY_CLEAR = 2.0  # required gap from anything above the bracket to the BATTERY face

COAX_D = 3.6  # channel down the mast, opens through the foot into the top-plate U-notch
COAX_SLIT = 2.2  # insertion slit on the upper face of the mast
SLIT_LIP = 1.5  # material beside the slit; its tip tapers out at the surface, like a c_clip mouth

BAR_D, BAR_LIP = 4.0, 0.3  # BAR_LEN (90, 915 MHz T-bar) comes from _common
GROOVE_X = 2.9  # the grooves run the whole head: a 90 mm bar has to pass through
HEAD_W, HEAD_L, HEAD_T = 15.0, 26.0, 8.0  # X, along the bar, along the mast; 12 wide leaves
#                                           only 0.1 mm between a groove mouth and the corner
HEAD_TILT = 10.0  # tilt of the frame-facing face: without it its normal.Z is -0.766 (unprintable)
HEAD_R = 1.5
TIE_SLOT_L, TIE_SLOT_W, TIE_U = 3.0, 8.0, 8.0  # zip-tie slots, 2.0 mm rails beside them

DIPOLE = False  # extra Ø4 clip on the head rear face for a dipole half
DIPOLE_D, DIPOLE_LEN = 4.0, 12.0

Z0 = Z_TOP_TOP  # 36.0
Z1 = Z0 + BRACKET_T  # 38.5: bracket top, mast root plane

_DEFAULTS = dict(MAST_ANGLE=MAST_ANGLE, MAST_LEN=MAST_LEN, MAST_D=MAST_D, ROOT_Y=ROOT_Y,
                 BRACKET_T=BRACKET_T, FRONT_X=FRONT_X, FRONT_Y=FRONT_Y, WIDE_X=WIDE_X,
                 WIDE_Y0=WIDE_Y0, WIDE_Y1=WIDE_Y1, TAIL_X=TAIL_X, TAIL_Y=TAIL_Y, EDGE_R=EDGE_R,
                 ROOT_R=ROOT_R, COAX_D=COAX_D, COAX_SLIT=COAX_SLIT, SLIT_LIP=SLIT_LIP,
                 BAR_D=BAR_D, BAR_LIP=BAR_LIP, GROOVE_X=GROOVE_X, HEAD_W=HEAD_W, HEAD_L=HEAD_L,
                 HEAD_T=HEAD_T, HEAD_TILT=HEAD_TILT, HEAD_R=HEAD_R, TIE_SLOT_L=TIE_SLOT_L,
                 TIE_SLOT_W=TIE_SLOT_W, TIE_U=TIE_U, DIPOLE=DIPOLE, DIPOLE_D=DIPOLE_D,
                 DIPOLE_LEN=DIPOLE_LEN)


# --- mast frame ------------------------------------------------------------------------------
def _axes(p: dict) -> tuple[Vector, Vector, Vector, Vector]:
    """(root point A, mast direction D, bar direction B, mast 'up' V); D, B, V are orthonormal."""
    a = radians(p["MAST_ANGLE"])
    d = Vector(0, -cos(a), sin(a))  # up and rearward
    b = Vector(0, -sin(a), -cos(a))  # perpendicular to the mast in YZ, pointing down-rear
    return Vector(0, p["ROOT_Y"], Z0 + p["BRACKET_T"]), d, b, -b


def _mast_plane(p: dict, s: float) -> Plane:
    """Plane across the mast at distance s from the root; local x = frame X, local y = mast up."""
    a, d, _b, _v = _axes(p)
    return Plane(origin=a + d * s, x_dir=(1, 0, 0), z_dir=d)


def _head_plane(p: dict) -> Plane:
    """Section plane of the head at its upper end; local x = frame X, local y = mast direction,
    extruded along the bar. Cutting the grooves in this 2D section (instead of with 3D cylinder
    tools) keeps their faces plain cylinders, which the shared overhang check needs."""
    a, d, b, _v = _axes(p)
    return Plane(origin=a + d * p["MAST_LEN"] - b * (p["HEAD_L"] / 2), x_dir=(1, 0, 0), z_dir=b)


def _groove_depth(p: dict) -> float:
    """Distance of a bar-groove axis below the outer face that leaves BAR_LIP lips on both sides."""
    r = p["BAR_D"] / 2
    return sqrt(r ** 2 - (r - p["BAR_LIP"]) ** 2)


# --- pieces ----------------------------------------------------------------------------------
def _bracket(p: dict) -> Part:
    pts = [(p["FRONT_X"], p["FRONT_Y"]), (p["WIDE_X"], p["WIDE_Y0"]), (p["WIDE_X"], p["WIDE_Y1"]),
           (p["TAIL_X"], p["TAIL_Y"]), (-p["TAIL_X"], p["TAIL_Y"]), (-p["WIDE_X"], p["WIDE_Y1"]),
           (-p["WIDE_X"], p["WIDE_Y0"]), (-p["FRONT_X"], p["FRONT_Y"])]
    sk = fillet(Polygon(*pts, align=None).vertices(), p["EDGE_R"])
    return extrude(Plane.XY.offset(Z0) * sk, amount=p["BRACKET_T"], dir=(0, 0, 1))


def _mast_foot_drop(p: dict) -> float:
    """How far below the root plane the rod has to run so that Z 36 cuts it off completely."""
    return (p["BRACKET_T"] + p["MAST_D"] / 2 * cos(radians(p["MAST_ANGLE"])) + 0.5) / sin(radians(p["MAST_ANGLE"]))


def _rod(p: dict, d: float, s0: float, s1: float) -> Part:
    return extrude(_mast_plane(p, s0) * Circle(d / 2), amount=s1 - s0)


def _tilt_cutter(p: dict) -> Part:
    """Half space under the frame-facing face of the head. That face would point 50 deg down
    (normal.Z -0.766); tilting it HEAD_TILT towards the upper bar end brings every head normal
    back above the 45 deg limit. The coax channel and its slit stop on the same plane, so their
    ends are part of that face instead of two more unsupported ceilings."""
    a, d, b, _v = _axes(p)
    g = radians(p["HEAD_TILT"])
    n = b * -sin(g) + d * -cos(g)
    origin = a + d * (p["MAST_LEN"] - p["HEAD_T"] / 2)
    return Plane(origin=origin, x_dir=(1, 0, 0), z_dir=n) * Box(400, 400, 400, align=MIN_Z_ALIGN)


def _head(p: dict, grooves: bool = True) -> Part:
    t, w_top = tan(radians(p["HEAD_TILT"])), p["HEAD_T"] / 2
    w_bot = -(w_top + p["HEAD_L"] / 2 * t)  # deep enough that the tilted cut sweeps the whole face
    sec = Pos(0, (w_top + w_bot) / 2) * Rectangle(p["HEAD_W"], w_top - w_bot)
    sec = fillet(sec.vertices().filter_by(lambda q: q.Y > 0), p["HEAD_R"])
    if grooves:
        for x in (-p["GROOVE_X"], p["GROOVE_X"]):
            sec -= Pos(x, w_top - _groove_depth(p)) * Circle(p["BAR_D"] / 2)
    head = extrude(_head_plane(p) * sec, amount=p["HEAD_L"])
    return head - _tilt_cutter(p) - _tie_slots(p)


def _tie_slots(p: dict) -> Part:
    a, d, b, _v = _axes(p)
    tools = Part()
    for u in (-p["TIE_U"], p["TIE_U"]):
        origin = a + d * p["MAST_LEN"] + b * u
        tools += Plane(origin=origin, x_dir=(1, 0, 0), z_dir=d) * Box(p["TIE_SLOT_W"], p["TIE_SLOT_L"], 60)
    return tools


def _dipole_clip(p: dict) -> Part:
    a, d, b, _v = _axes(p)
    r_in = p["DIPOLE_D"] / 2 + FIT
    r_out = r_in + CLIP_WALL
    mouth = p["DIPOLE_D"] - MATERIALS[MATERIAL]["snap"]
    sk = (Circle(r_out) - Circle(r_in)) - Rectangle(r_out + 1, mouth, align=(Align.MIN, Align.CENTER)).rotate(Axis.Z, 90)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(abs(v.X) - mouth / 2) < 1e-6), MOUTH_FILLET)
    # started below the head's frame plane and trimmed on it, so its lower end is not a ceiling
    start = p["MAST_LEN"] - p["HEAD_T"] / 2 - 6.0
    origin = a + d * start + b * (p["HEAD_L"] / 2 + r_out - 1.0)
    clip = extrude(Plane(origin=origin, x_dir=(1, 0, 0), z_dir=d) * sk, amount=p["DIPOLE_LEN"] + 6.0)
    return clip - _tilt_cutter(p)


def _bolt_tools(p: dict) -> Part:
    z_top = Z0 + p["BRACKET_T"]
    tools = Part()
    for x in (BOLT_XY[0], -BOLT_XY[0]):
        tools += screw_hole((x, BOLT_XY[1]), z_top, D_M3_THRU, p["BRACKET_T"] + 2,
                            head_d=D_M3_HEAD_RECESS, head_h=1.0)
    return tools


def build(**overrides) -> dict[str, Part]:
    p = {**_DEFAULTS, **overrides}
    z1 = Z0 + p["BRACKET_T"]

    part = _bracket(p) + _rod(p, p["MAST_D"], -_mast_foot_drop(p), p["MAST_LEN"])
    # the only ellipse in the part is where the round mast cuts the flat bracket top
    root = [e for e in part.edges() if e.geom_type == GeomType.ELLIPSE and abs(e.center().Z - z1) < 1e-3]
    assert len(root) == 1, f"root edge selection found {len(root)} edges"
    for r in (p["ROOT_R"], 2.0, 1.2):
        try:
            part = part.fillet(r, root)
            break
        except Exception:  # noqa: BLE001 - OCCT can refuse the cylinder/plane blend
            continue
    part += _head(p)
    if p["DIPOLE"]:
        part += _dipole_clip(p)

    under_head = _tilt_cutter(p)
    channel = _rod(p, p["COAX_D"], -_mast_foot_drop(p), p["MAST_LEN"]) & under_head
    slit = extrude(_mast_plane(p, 0) * Rectangle(p["COAX_SLIT"], 12, align=(Align.CENTER, Align.MIN)),
                   amount=p["MAST_LEN"]) & under_head
    part -= channel + slit + _bolt_tools(p)
    part -= box(-60, -200, Z0 - 40, 60, 60, Z0)  # flat bed face: the mast foot stops at Z 36

    part = Part() + part  # the fillet/cut chain hands back a plain Solid
    part.label = NAME
    return {NAME: part}


def _above_bracket(part: Part) -> Part:
    """The mast: everything above the bracket top face."""
    return part - box(-60, -200, Z0 - 40, 60, 60, Z1)


def _thin_allowance(p: dict) -> tuple[Part, ...]:
    """The two intentionally thin features the wall check skips:
    1. the coax slit mouth - a straight slot through a round mast always tapers to a lip where it
       breaks the surface, exactly like a c_clip mouth;
    2. the 0.3 bar-groove lips, and only those: the band stops 1.6 short of the head corner, so
       the tight wall between a groove and that corner is still sampled.
    _thin_walls() states how thick the material is where each band ends."""
    half = p["COAX_SLIT"] / 2 + p["SLIT_LIP"]
    mouth = extrude(_mast_plane(p, -_mast_foot_drop(p)) * (Pos(0, 4.0) * Rectangle(2 * half, 8.0)),
                    amount=_mast_foot_drop(p) + p["MAST_LEN"])
    band = Sketch() + [Pos(x, p["HEAD_T"] / 2 - _groove_depth(p)) * Rectangle(p["BAR_D"] + 1.0, p["BAR_D"] + 2.0)
                       for x in (-p["GROOVE_X"], p["GROOVE_X"])]
    lips = extrude(_head_plane(p) * band, amount=p["HEAD_L"])
    return Part() + mouth, Part() + lips


def _groove_corner_wall(p: dict) -> float:
    """Material between a bar groove and the rounded head corner - the tightest wall in the head,
    and the one a flat 'HEAD_W/2 - GROOVE_X - r' estimate misses."""
    r_f, cx, cw = p["HEAD_R"], p["GROOVE_X"], p["HEAD_T"] / 2 - _groove_depth(p)
    fx, fw = p["HEAD_W"] / 2 - r_f, p["HEAD_T"] / 2 - r_f
    arc = [(fx + r_f * cos(radians(a)), fw + r_f * sin(radians(a))) for a in range(0, 91)]
    return min(hypot(x - cx, w - cw) for x, w in arc) - p["BAR_D"] / 2


def _thin_walls(p: dict) -> dict[str, float]:
    """Walls inside the two allowance bands, which the ray sampler therefore never measures,
    plus the two head walls that are tight by construction."""
    r, t = p["BAR_D"] / 2, tan(radians(p["HEAD_TILT"]))
    return {"between the grooves": 2 * p["GROOVE_X"] - p["BAR_D"],
            "groove to head corner": _groove_corner_wall(p),
            "under the groove": (p["HEAD_T"] / 2 - _groove_depth(p) - r) + (p["HEAD_T"] / 2 - p["HEAD_L"] / 2 * t),
            "zip-tie slot rail": p["HEAD_W"] / 2 - p["HEAD_R"] - p["TIE_SLOT_W"] / 2,
            "slit lip width": p["SLIT_LIP"],
            "mast tube wall": (p["MAST_D"] - p["COAX_D"]) / 2,
            "under the M3 recess": p["BRACKET_T"] - 1.0}


def _bar_ends(p: dict) -> list[Vector]:
    a, d, b, _v = _axes(p)
    centre = a + d * p["MAST_LEN"] + d * (p["HEAD_T"] / 2 - sqrt((p["BAR_D"] / 2) ** 2 - (p["BAR_D"] / 2 - p["BAR_LIP"]) ** 2))
    return [centre + b * (BAR_LEN / 2), centre - b * (BAR_LEN / 2)]


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    part, p = parts[NAME], _DEFAULTS
    mast = _above_bracket(part)
    out = []

    hits = interference(part)
    out.append(("no interference with the frame", not hits, f"{hits or 'none'}"))

    for side, x in (("right", BOLT_XY[0]), ("left", -BOLT_XY[0])):
        ok, detail = coaxial(part, (x, BOLT_XY[1]), D_M3_THRU, Z0, Z1)
        probe = isect(part, cylinder(x, BOLT_XY[1], Z0 - 1, Z1 + 1, 3.2))
        out.append((f"bolt hole coaxial with standoff_rear_tip_{side}, Ø3.2 probe clear",
                    ok and probe < EPS, f"{detail}; probe {probe:.4f} mm³"))

    contact = seated(part, Z0)
    out.append(("bracket seated on plate_top at Z 36.000", contact >= 300.0, f"{contact} mm² contact"))

    bb = part.bounding_box()
    out.append(("outline |x| <= 22.0 behind y -82", max(abs(bb.min.X), abs(bb.max.X)) <= WIDE_X + 1e-6,
                f"|x| max {max(abs(bb.min.X), abs(bb.max.X)):.3f}, y {bb.min.Y:.1f}..{bb.max.Y:.1f}"))

    disc = prop_disc_violation(part)
    out.append(("outside the prop keep-out discs", disc < EPS, f"{disc:.3f} mm³"))

    vb, gap = isect(mast, BATTERY), mast.distance_to(BATTERY)
    out.append((f"mast clear of the BATTERY envelope by >= {BATTERY_CLEAR} mm",
                vb < EPS and gap >= BATTERY_CLEAR, f"{vb:.3f} mm³, gap {gap:.3f} mm"))

    plates = [frame[n] for n in PLATE_FACES]
    ends = [(e, min(cylinder(e.X, e.Y, e.Z - 0.05, e.Z + 0.05, 0.1).distance_to(pl) for pl in plates))
            for e in _bar_ends(p)]
    out.append(("both T-bar ends >= 20 mm from every plate",
                all(g >= 20.0 for _e, g in ends),
                "; ".join(f"({e.X:.0f}, {e.Y:.1f}, {e.Z:.1f}) {g:.1f} mm" for e, g in ends)))

    out.append(_tail_block_check(mast))

    over = overhangs(mast, PRINT[NAME], cos_limit=0.72, material=MATERIAL)
    out.append(("mast self-supporting above Z 38.5 (no normal.Z < -0.72)", not over, "; ".join(over) or "none"))

    # min_wall()'s erode/dilate path is unreliable on this solid: OCCT sometimes refuses the
    # offset (min_wall then falls back to ray_thickness by itself) and sometimes returns a
    # collapsed shape that reads as a 2.5 cm3 "thin residual". Its ray sampler is exact here,
    # so call that directly and get the same answer every run.
    thin, _worst, wall_detail = ray_thickness(part, WALL, allow=_thin_allowance(p))
    out.append((f"min wall >= {WALL} outside the declared thin features", not thin, wall_detail))
    walls = _thin_walls(p)
    out.append((f"declared thin features rooted in >= {WALL} of material",
                min(walls.values()) >= WALL - 1e-6,
                ", ".join(f"{k} {v:.2f}" for k, v in walls.items())))
    return out


def _tail_block_check(mast: Part) -> tuple[str, bool, str]:
    """The mast is the alternative RX holder when the tail block is cut down to TOWER=False."""
    name = "clear of tail_block(TOWER=False) by >= 1.0 mm"
    try:
        from tigerbee.accessories import tail_block
        tb = Part() + list(tail_block.build(TOWER=False).values())
    except Exception as e:  # noqa: BLE001 - sibling module not written yet
        return name, True, f"tail_block unavailable ({type(e).__name__}), not checked"
    v, gap = isect(mast, tb), mast.distance_to(tb)
    return name, v < EPS and gap >= 1.0, f"{v:.3f} mm³, gap {gap:.3f} mm"
