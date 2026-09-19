"""TPU arm-tip protector with an integral landing foot, retained by the four motor screws."""

from copy import deepcopy

from build123d import (Circle, Compound, Cone, Face, Part, Pos, Rectangle, Vertex, extrude, fillet,
                       loft, offset)
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

from tigerbee import params as P
from tigerbee import profiles
from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "motor_guard"
TITLE = "Motor / arm-tip guard with landing foot"
MATERIAL = "TPU95A"
EXCLUSIVE = ()

# --- parameters (mm, arm-local: root midpoint at (0, 0), motor at (0, L), carbon Z 0..5) ---
L = P.ROOT_TO_MOTOR  # 114.804
CLEARANCE = 0.25  # radial fit of the cavity on the carbon
WALL = 2.0  # skin wall (WALL_IMPACT); the outline offsets are CLEARANCE and CLEARANCE + WALL
FLANGE = 4.0  # solid slab under the arm, local Z -FLANGE..0
RIM_GAP = 0.2  # wall top below the carbon top face, so motor leads clear the rim
DROP = 12.0  # foot underside, local Z -DROP (frame -10)
START = L - 30.0  # 84.804: rear end of the guard, on the 12 mm shaft
HEAD_D = 6.6  # M3 button-head channel
HEAD_Z = -2.0  # head bears here: 2 mm of flange above it
BORE_D = 9.0  # shaft / circlip relief under the motor
# 23 wide per spec; 50 long rather than 47 so the pad keeps a 1.97 mm web ahead of the diamond
# window - at 47 the window's rounded front vertex would sit 0.47 mm from the pad edge.
FOOT = (23.0, 50.0)
FOOT_R = 6.0
FOOT_Y = L - 3.0
MOTOR_COLLAR = False  # ring around the 2807 bell (inside its OWN prop disc, below Z 22)
BELL_D = 35.0
COLLAR_GAP = 1.0  # ID = BELL_D + 2 x COLLAR_GAP = 37
COLLAR_WALL = 2.0  # OD 41
COLLAR_H = 8.0
CONE_R0 = 9.0  # flare base radius at the pad underside; see _collar()
WIRE_GAP = 10.0  # opening in the collar on the root side for the motor leads

MIN_Z = P.Z_ARM - DROP  # -10: the feet are the lowest point of the airframe
ARMS = {f"motor_guard_{n.removeprefix('arm_')}": n for n in ARM_NAMES}
PRINT = {label: (0, 0, -1) for label in ARMS}
OWN_PROP_DISC = {label: arm.removeprefix("arm_") for label, arm in ARMS.items()}
# PRINT is (0, 0, -1), so print Z = local Z + DROP. Two bridged ceilings: the Ø6.6 head channels
# close at local Z HEAD_Z (an ordinary counterbore shoulder, 6.6 across), and with MOTOR_COLLAR the
# ring has a 0.2 mm relief over the carbon closing at local Z ARM_T.
BRIDGE_OK = {label: (("box", -300.0, -300.0, DROP + HEAD_Z - 0.1, 300.0, 300.0, DROP + HEAD_Z + 0.1),
                     ("box", -300.0, -300.0, DROP + P.ARM_T - 0.1, 300.0, 300.0, DROP + P.ARM_T + 0.1))
             for label in ARMS}
NOTES = ("Pushed straight up onto the arm tip from below - the cavity is open at the top and at the "
         "rear, and the carbon is a prism, so nothing has to slide past the paddle. Retained by the "
         "four motor screws: M3 x 10 (2 mm of flange + 5 mm of carbon + 3 mm into the motor), heads "
         "in the Ø6.6 channels. Leads run on the carbon over the 4.8 mm rim and out of the open rear "
         "end. min wall is measured across the skin ring; the 2.0 mm counterbore shoulders over the "
         "screw heads are intentional. Two webs are set by the Ø19 bolt circle rather than by WALL "
         "and are held to the 1.2 mm TPU floor: 1.70 mm between the Ø9 shaft relief and the Ø6.6 head "
         "channels, and 1.48 mm of landing pad beside them; both are checked explicitly. "
         "build(MOTOR_COLLAR=True) adds a Ø41 ring round the 2807 bell on a "
         "34 deg flare (frame Z 6.8-14.8, inside its own prop disc only). Verify P.MOTOR_BOLT_CIRCLE "
         "(Ø19 modelled, 13.4 mm adjacent) against the physical motor before printing.")

_PARAMS = ("CLEARANCE", "WALL", "FLANGE", "RIM_GAP", "DROP", "START", "HEAD_D", "HEAD_Z", "BORE_D",
           "FOOT", "FOOT_R", "FOOT_Y", "MOTOR_COLLAR", "BELL_D", "COLLAR_GAP", "COLLAR_WALL",
           "COLLAR_H", "CONE_R0", "WIRE_GAP")


def _params(**overrides) -> dict:
    p = {k: globals()[k] for k in _PARAMS}
    p.update(overrides)
    p["RIM"] = P.ARM_T - p["RIM_GAP"]  # 4.8: top of the skin, 0.2 below the carbon top face
    return p


# checks() must measure the geometry that build() actually produced, not the module defaults,
# so build() records the effective parameter set here.
_EFFECTIVE: dict | None = None


# --- 2D helpers ---------------------------------------------------------------------------
def _face(shape) -> Face:
    f = shape if isinstance(shape, Face) else shape.faces()[0]
    return f if f.normal_at().Z > 0 else -f


def _off(face: Face, d: float) -> Face:
    """2D offset of the arm outline, rebuilt as NURBS.

    `offset()` leaves Geom_OffsetCurve edges; every face built on one is silently dropped by the
    STEP writer, so the part arrives in FreeCAD as loose faces instead of a solid. The conversion
    is area-preserving (1245.023 mm² either way for the skin).
    """
    off = _face(offset(_face(face), amount=d))
    return _face(Face(BRepBuilderAPI_NurbsConvert(off.wrapped, True).Shape()))


def _crop(face: Face, y0: float) -> Face:
    """Keep the part of the face forward of y0 (the guard covers the tip only)."""
    return _face(face & (Pos(0, y0 + 150) * Rectangle(400, 300)))


def _col(x: float, y: float, z0: float, z1: float, d: float) -> Part:
    return cylinder(x, y, z0, z1, d)


def _diamond_face() -> Face:
    cy, hw, hh = L + P.DIAMOND_OFFSET, P.DIAMOND_W / 2, P.DIAMOND_H / 2
    return _face(Face(profiles._rounded_polygon(((0, cy + hh), (hw, cy), (0, cy - hh), (-hw, cy)),
                                                P.DIAMOND_FILLET)))  # the wire runs clockwise


# --- the part, in arm-local coordinates -----------------------------------------------------
def _guard(p: dict) -> Part:
    base = Face(profiles._outline(L))
    pocket = _crop(_off(base, p["CLEARANCE"]), p["START"])
    skin = _crop(_off(base, p["CLEARANCE"] + p["WALL"]), p["START"])
    rim, flange, drop = p["RIM"], p["FLANGE"], p["DROP"]

    body = extrude(Pos(0, 0, -flange) * skin, amount=flange + rim)
    body -= extrude(pocket, amount=rim + 1)  # cavity open at the top and at y = START

    # the pad must sit forward of the skin's rear edge, or the loft would overhang rearwards
    assert p["FOOT_Y"] - p["FOOT"][1] / 2 >= p["START"], "FOOT reaches behind START"
    foot = _face(Pos(0, p["FOOT_Y"]) * fillet(Rectangle(*p["FOOT"]).vertices(), p["FOOT_R"]))
    body += loft([Pos(0, 0, -drop) * foot, Pos(0, 0, -flange) * skin], ruled=True)

    if p["MOTOR_COLLAR"]:
        body += _collar(p, pocket)

    tools = []
    for bx, by in profiles.motor_bolts(L):
        tools.append(_col(bx, by, -drop - 1, 0.01, D_M3_THRU))
        tools.append(_col(bx, by, -drop - 1, p["HEAD_Z"], p["HEAD_D"]))
    tools.append(_col(0, L, -flange, 0.01, p["BORE_D"]))
    # the diamond window stops at the flange top: above it the cavity is already open, and the
    # collar ring (ID 37) reaches out to where the window's front vertex would notch it.
    tools.append(extrude(Pos(0, 0, -drop - 1) * _diamond_face(), amount=drop + 1.01))
    body = body - Compound(children=tools)  # one boolean; Part.cut() would return a bare Solid
    assert body.is_valid and len(body.solids()) == 1, f"guard: {len(body.solids())} solid(s)"
    return body


def _collar(p: dict, pocket: Face) -> Part:
    """Ring round the motor bell on a conical flare, with a lead gap on the root side.

    The flare is a cone rather than a loft off the skin outline: a ruled loft between a 57 mm long
    outline and a Ø41 circle skews badly and produces near-horizontal patches. The cone starts on
    the pad plane (Z -DROP) at CONE_R0, small enough to stay buried in the foot, and only emerges
    from the body around Z -7; running it the full height keeps its flank at 34 deg from vertical
    instead of the 42 deg a flange-height cone would need.
    """
    r_in = p["BELL_D"] / 2 + p["COLLAR_GAP"]
    r_out = r_in + p["COLLAR_WALL"]
    rim, drop = p["RIM"], p["DROP"]
    ring = extrude(Pos(0, L, rim) * (Circle(r_out) - Circle(r_in)), amount=p["COLLAR_H"])
    cone = Pos(0, L, -drop) * Cone(p["CONE_R0"], r_out, drop + rim, align=MIN_Z_ALIGN)
    lead = extrude(Pos(0, L - (r_out + 1) / 2, -drop) * Rectangle(p["WIRE_GAP"], r_out + 1),
                   amount=drop + rim + p["COLLAR_H"])
    # 0.2 mm relief where the carbon crosses the ring; everywhere else the ring stands on the cone
    return ((ring + cone) - lead - extrude(pocket, amount=P.ARM_T)).clean()


def build(**overrides) -> dict[str, Part]:
    global _EFFECTIVE
    p = _params(**overrides)
    _EFFECTIVE = p
    local = _guard(p)
    return {label: place_arm(deepcopy(local), P.ARM_PLACEMENTS[arm]) for label, arm in ARMS.items()}


# --- checks -----------------------------------------------------------------------------------
def _min_local_y(part: Part, arm: str) -> float:
    """Rearmost point of a placed copy, back in arm-local y."""
    pl = P.ARM_PLACEMENTS[arm]
    o = Vector(*P.place(0, 0, pl), 0)
    ey = Vector(*P.place(0, 1, pl), 0) - o
    return min((Vector(v.X, v.Y, 0) - o).dot(ey) for v in part.vertices())


def _skin_min_wall(p: dict, n: int = 320) -> tuple[float, tuple[float, float]]:
    """Thinnest point of the skin ring, measured from its outer wire to the cavity wire. The walls
    are prismatic, so this 2D measurement is the 3D wall; OCCT's 3D offset cannot erode this
    outline, so min_wall()'s erode/dilate is unusable here."""
    base = Face(profiles._outline(L))
    cavity = _crop(_off(base, p["CLEARANCE"]), p["START"]).outer_wire()
    skin = _crop(_off(base, p["CLEARANCE"] + p["WALL"]), p["START"]).outer_wire()
    worst, where = float("inf"), (0.0, 0.0)
    for i in range(n):
        pt = skin.position_at(i / n)
        if abs(pt.Y - p["START"]) < 0.05:  # the rear face is an opening, not a wall
            continue
        d = cavity.distance_to(Vertex(pt.X, pt.Y, 0))
        if d < worst:
            worst, where = d, (round(pt.X, 2), round(pt.Y, 2))
    return worst, where


def _pad_web(p: dict) -> float:
    """Narrowest strip of landing pad left beside the diamond window and the head channels."""
    pad = _face(Pos(0, p["FOOT_Y"]) * fillet(Rectangle(*p["FOOT"]).vertices(), p["FOOT_R"])).outer_wire()
    holes = [_diamond_face().outer_wire()]
    holes += [_face(Pos(bx, by) * Circle(p["HEAD_D"] / 2)).outer_wire()
              for bx, by in profiles.motor_bolts(L)]
    return min(pad.distance_to(h) for h in holes)


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    p = _EFFECTIVE if _EFFECTIVE is not None else _params()
    rim, drop, collar = p["RIM"], p["DROP"], p["MOTOR_COLLAR"]
    out: list[tuple[str, bool, str]] = []
    base = Face(profiles._outline(L))
    loose = extrude(Pos(0, 0, 0.5) * _off(base, p["CLEARANCE"] - 0.05), amount=4.0)  # +0.20: must fit
    tight = extrude(Pos(0, 0, 0.5) * _off(base, p["CLEARANCE"] + 0.05), amount=4.0)  # +0.30: must bite
    bell = _col(0, L, P.ARM_T, 20.0, p["BELL_D"] + 1.6)  # local Z 5..20 = frame 7..22

    volumes = []
    for label, arm in ARMS.items():
        g = parts[label]
        pl = P.ARM_PLACEMENTS[arm]
        volumes.append(g.volume)

        hits = interference(g)
        out.append((f"{label}: clear of the arm and every frame part", not hits, f"{hits or 'none'}"))

        v_loose = isect(g, place_arm(deepcopy(loose), pl))
        v_tight = isect(g, place_arm(deepcopy(tight), pl))
        out.append((f"{label}: cavity clears the carbon by {p['CLEARANCE']}", v_loose < EPS and v_tight > EPS,
                    f"+0.20 probe {v_loose:.3f} mm³, +0.30 probe {v_tight:.2f} mm³"))

        for i, (bx, by) in enumerate(profiles.motor_bolts(L)):
            xy = P.place(bx, by, pl)
            # the Ø3.4 shank bore is the shoulder over the head channel: local Z HEAD_Z..0
            ok, detail = coaxial(g, xy, D_M3_THRU, P.Z_ARM + p["HEAD_Z"] + 0.05, P.Z_ARM - 0.05)
            out.append((f"{label}: bolt {i} coaxial with the motor axis", ok, detail))
            shank = _col(*xy, P.Z_ARM - 12, P.Z_ARM + 8, 3.2)
            head = _col(*xy, P.Z_ARM - 5, P.Z_ARM + p["HEAD_Z"], D_M3_HEAD)
            out.append((f"{label}: bolt {i} shank and head free", isect(g, shank) < EPS and isect(g, head) < EPS,
                        f"shank {isect(g, shank):.3f}, head {isect(g, head):.3f} mm³"))

        win = _col(*P.place(0, L + P.DIAMOND_OFFSET, pl), P.Z_ARM - drop - 1, P.Z_ARM + 0.5, 4.0)
        v_win = isect(g, win)
        out.append((f"{label}: diamond window open through the flange and the foot", v_win < EPS, f"{v_win:.3f} mm³"))

        y0 = _min_local_y(g, arm)
        out.append((f"{label}: rear end at local y {p['START']:.3f}", abs(y0 - p["START"]) <= 0.05, f"{y0:.3f}"))

        zmax = g.bounding_box().max.Z
        limit = P.Z_ARM + rim + (p["COLLAR_H"] if collar else 0.0)
        out.append((f"{label}: max Z <= {limit:.1f}", zmax <= limit + 1e-6, f"{zmax:.3f}"))

        own = OWN_PROP_DISC[label]
        v_near = prop_disc_violation(g, exclude=(own,))
        out.append((f"{label}: outside the neighbouring prop discs", v_near < EPS, f"{v_near:.3f} mm³"))
        # without the collar nothing may sit in the own disc either; with it, only below Z 22
        z_own = OWN_DISC_Z_MAX if collar else PROP_Z0
        v_own = prop_disc_violation(g, z0=z_own)
        out.append((f"{label}: own prop disc clear above Z {z_own}", v_own < EPS, f"{v_own:.3f} mm³"))

        v_bell = isect(g, place_arm(deepcopy(bell), pl))
        out.append((f"{label}: clear of the Ø{p['BELL_D'] + 1.6} motor bell above Z 7", v_bell < EPS, f"{v_bell:.3f} mm³"))

        over = overhangs(g, PRINT[label], bridge_ok=BRIDGE_OK[label], material=MATERIAL)
        out.append((f"{label}: prints foot-down without support", not over, "; ".join(over) or "none"))

    shapes = [parts[label].wrapped for label in ARMS]
    distinct = all(not a.IsSame(b) for i, a in enumerate(shapes) for b in shapes[i + 1:])
    spread = max(volumes) - min(volumes)
    out.append(("four independent shapes", distinct and len(shapes) == 4, f"{len(shapes)} shapes"))
    out.append(("all four the same volume", spread < 1.0, f"spread {spread:.4f} mm³"))
    out.append(("volume 10-22 cm³", 10000 <= volumes[0] <= 22000, f"{volumes[0] / 1000:.2f} cm³"))

    thin, where = _skin_min_wall(p)
    out.append((f"skin min wall >= {WALL_IMPACT}", thin >= WALL_IMPACT - WALL_TOL,
                f"{thin:.3f} mm at local {where}"))

    # The two webs the skin check cannot see. Both are fixed by the Ø19 bolt circle and the Ø6.6
    # head channels, not by WALL, so they are held to the 1.2 mm TPU floor rather than WALL_IMPACT.
    floor = MATERIALS[MATERIAL]["wall"]
    web = P.MOTOR_BOLT_CIRCLE / 2 - p["HEAD_D"] / 2 - p["BORE_D"] / 2
    out.append((f"flange web, Ø{p['BORE_D']} relief to head channel >= {floor}", web >= floor - 1e-6,
                f"{web:.3f} mm"))
    pad_web = _pad_web(p)
    out.append((f"landing pad web round its openings >= {floor}", pad_web >= floor - 1e-6, f"{pad_web:.3f} mm"))

    if collar:
        r_in = p["BELL_D"] / 2 + p["COLLAR_GAP"]
        ring = extrude(Pos(0, L, rim) * (Circle(r_in + p["COLLAR_WALL"]) - Circle(r_in)), amount=p["COLLAR_H"])
        ok_c, _vc, detail_c = min_wall(ring, WALL_IMPACT)
        out.append((f"collar min wall >= {WALL_IMPACT}", ok_c, detail_c))
    return out
