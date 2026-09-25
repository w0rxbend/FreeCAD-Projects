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
MOUNTS = ("arm_<corner> tip prism - the cavity slides up from below over the 5 mm carbon, "
          "arm underside Z 2 to the arm top face Z 7",
          "the Ø19 motor bolt circle at the motor centre (4 x M3 at 45 deg, 13.4 mm adjacent)")
HARDWARE = ("4 x M3 x 10 motor screws per guard, replacing the stock ones (2 mm of flange + 5 mm of "
            "carbon + 3 mm into the motor); heads run in the Ø6.6 channels",)

# --- parameters (mm, arm-local: root midpoint at (0, 0), motor at (0, L), carbon Z 0..5) ---
L = P.ROOT_TO_MOTOR  # 114.804
CLEARANCE = 0.25  # radial fit of the cavity on the carbon
WALL = 2.0  # skin wall (WALL_IMPACT); the outline offsets are CLEARANCE and CLEARANCE + WALL
FLANGE = 4.0  # solid slab under the arm, local Z -FLANGE..0
RIM_GAP = 0.2  # wall top below the carbon top face, so motor leads clear the rim
GROUND = GROUND_Z  # -15.2: the plane THIS variant stands on. A taller variant lowers it (see VARIANTS).
# DROP is DERIVED from it, never typed: the feet are the landing gear, so they have to reach the same
# plane as the deepest thing bolted under plate_bottom (led_buzzer's bar). At the old DROP 12 the feet
# stopped 5.2 mm short of it and the quad rested on a tripod of the tail bar plus the two FRONT feet,
# ~1.9 deg nose-up, driving every touchdown through the 2.0 mm TPU floor of the WS2812 groove.
DROP = P.Z_ARM - GROUND  # 17.2

# --- taller legs (see VARIANTS) -------------------------------------------------------------
# The stock leg is one ruled loft from the landing pad straight up to the skin outline: a rigid
# splayed skirt that puts the whole landing load into the four motor screws. The taller legs put a
# shaped section in between so the leg itself takes some of the hit.
LEG = "straight"  # "straight" | "sprung" | "bellows"
# Printing is foot-down, so a section that NARROWS going up is free - every layer lands on a bigger
# one - while one that widens is an overhang. Both compliant legs therefore neck down hard just above
# the pad and then open out to the skin over the rest of the run, which is also where the spring wants
# its thin section: low down, with the longest lever above it.
WAIST = (0.55, 0.80)  # sprung: waist section as a fraction of (FOOT width, FOOT length)
WAIST_AT = 0.26  # sprung: waist height as a fraction of the pad-to-flange run
BELLOWS_N = 2  # bellows: full narrow/wide cycles between the pad and the opening-out
BELLOWS_IN = 0.78  # bellows: narrow station as a fraction of the pad WIDTH (X only - see _leg)
BELLOWS_TOP = 0.72  # bellows: fraction of the run given to the folds before opening out to the skin
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

EXTENDED_GROUND = -22.0  # the plane arm_protector_feet + front_bumper_feet already stand on

# Every spec carries a "style": these are FUNCTIONAL variants (leg length and how it absorbs a
# landing), not style families, but _export.kits() reads `spec.get("style") or <variant name>` and
# hands the result to _style.style_of(), which raises on anything that is not one of the seven
# families. So each one declares the family it genuinely READS as - the plain lofted skirts are
# smooth and minimal, the necked leg is a swept form, the concertina is ribbed.
VARIANTS = {
    "stock": {"style": "nocturne", "notes": "the original landing gear: a rigid splayed skirt lofted straight from the "
                       "landing pad to the skin, standing on the standard airframe plane Z -15.2 "
                       "(15.2 mm under plate_bottom), coplanar with led_buzzer's bar. No travel - "
                       "the whole landing load goes into the four motor screws."},
    "tall": {"style": "nocturne", "params": {"GROUND": EXTENDED_GROUND},
             "notes": "the same rigid skirt 6.8 mm longer, standing on Z -22.0: 22 mm of ground "
                      "clearance for tall grass, gravel and furrows, and a deeper pocket for the "
                      "props on a nose-down arrival. No travel either, but it stands on EXACTLY the "
                      "plane front_bumper_feet uses, so those two can be mixed (arm_protector_feet "
                      "is still EXCLUSIVE with any motor_guard - both wrap the same arm tip)."},
    "sprung": {"style": "slipstream", "params": {"GROUND": EXTENDED_GROUND, "LEG": "sprung"},
               "notes": "an hourglass leg: the loft necks down to a 12 x 37 mm waist a third of the "
                        "way up, so the leg is a TPU leaf spring instead of a strut. It flexes "
                        "fore-aft (the waist is narrow across X, deep along Y, so it bends in the "
                        "arm's own plane and cannot fold sideways) and RETURNS - this is elastic "
                        "travel, not a crush, so it survives repeated hard landings."},
    "bellows": {"style": "arsenal", "params": {"GROUND": EXTENDED_GROUND, "LEG": "bellows"},
                "notes": "three concertina cycles between pad and skin. It compresses axially and "
                         "returns, with more travel than the waist and a softer initial rate, so it "
                         "takes the bump out of a fast descent. The folds are the sacrificial part: "
                         "after a genuinely bad arrival, check them for whitening and reprint the "
                         "guard rather than trusting a creased fold."},
}
ASSEMBLY_VARIANT = "stock"  # the combined assembly keeps the standard stance

# The deepest variant, because MIN_Z is a module-level floor the framework applies to every part of
# every variant: it says nothing may go BELOW this, not that anything touches it. Each variant's own
# feet are asserted coplanar on ITS plane by the rows in checks().
MIN_Z = EXTENDED_GROUND
ARMS = {f"motor_guard_{n.removeprefix('arm_')}": n for n in ARM_NAMES}
PRINT = {label: (0, 0, -1) for label in ARMS}
OWN_PROP_DISC = {label: arm.removeprefix("arm_") for label, arm in ARMS.items()}
# PRINT is (0, 0, -1), so print Z = local Z + DROP. Two bridged ceilings: the Ø6.6 head channels
# close at local Z HEAD_Z (an ordinary counterbore shoulder, 6.6 across), and with MOTOR_COLLAR the
# ring has a 0.2 mm relief over the carbon closing at local Z ARM_T.
def _bridges(drop: float) -> tuple:
    """The two bridged ceilings, in PRINT coordinates (print Z = local Z + drop), so they follow the
    variant's leg length. Declaring them once at the module's own DROP would leave every taller
    variant's four Ø6.6 head-channel shoulders (25.13 mm² apiece) reported as unsupported."""
    return (("box", -300.0, -300.0, drop + HEAD_Z - 0.1, 300.0, 300.0, drop + HEAD_Z + 0.1),
            ("box", -300.0, -300.0, drop + P.ARM_T - 0.1, 300.0, 300.0, drop + P.ARM_T + 0.1))


# Keyed by the base label AND by every "<base>__<variant>" label, because the framework looks the
# final label up first and only then falls back to the base one.
BRIDGE_OK = {label: _bridges(DROP) for label in ARMS}
BRIDGE_OK.update({f"{label}__{v}": _bridges(P.Z_ARM - (spec.get("params", {}).get("GROUND", GROUND)))
                  for label in ARMS for v, spec in VARIANTS.items()})
NOTES = (f"THE AIRFRAME'S LANDING GEAR: the pad underside is the ground plane at frame Z {GROUND_Z} "
         f"({DROP} mm below the arm underside, {-GROUND_Z} mm of ground clearance under plate_bottom), "
         "which is exactly the plane led_buzzer's bar stands on, so the quad rests level on four "
         "contact pads at the arm tips plus the tail bar - five coplanar points, not a tripod. "
         "The 2 mm flange slides BETWEEN the motor and the carbon, so the motor sits 2 mm higher and "
         "its screws grow from M3 x 8 to M3 x 10. "
         "Pushed straight up onto the arm tip from below - the cavity is open at the top and at the "
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

_PARAMS = ("CLEARANCE", "WALL", "FLANGE", "RIM_GAP", "GROUND", "START", "HEAD_D", "HEAD_Z", "BORE_D",
           "FOOT", "FOOT_R", "FOOT_Y", "MOTOR_COLLAR", "BELL_D", "COLLAR_GAP", "COLLAR_WALL",
           "COLLAR_H", "CONE_R0", "WIRE_GAP", "LEG", "WAIST", "WAIST_AT", "BELLOWS_N", "BELLOWS_IN",
           "BELLOWS_TOP")


def _params(**overrides) -> dict:
    p = {k: globals()[k] for k in _PARAMS}
    p.update(overrides)
    p["RIM"] = P.ARM_T - p["RIM_GAP"]  # 4.8: top of the skin, 0.2 below the carbon top face
    # The one number a builder retunes is GROUND, the plane the feet stand on; DROP follows from it.
    p["DROP"] = P.Z_ARM - p["GROUND"]
    assert p["DROP"] > p["FLANGE"] + 2.0, "the leg has no room between the pad and the flange"
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
    body += _leg(p, skin)

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


def _pad(p: dict, w: float = 1.0, l: float = 1.0) -> Face:
    """The landing pad outline, optionally scaled: the section every leg is built from."""
    ww, ll = p["FOOT"][0] * w, p["FOOT"][1] * l
    r = min(p["FOOT_R"], ww / 2 - 0.01, ll / 2 - 0.01)
    return _face(Pos(0, p["FOOT_Y"]) * fillet(Rectangle(ww, ll).vertices(), r))


def _leg(p: dict, skin: Face) -> Part:
    """The landing leg: pad plane up to the skin outline at the flange underside.

    `straight` is the original single ruled loft - a rigid splayed skirt that hands the whole landing
    load to the four motor screws. The other two put a shaped section low in the run so the leg itself
    takes part of the hit, and both keep the widening flanks long and shallow because printing is
    foot-down (narrowing upward is self-supporting, widening upward is an overhang).
    """
    drop, flange, mode = p["DROP"], p["FLANGE"], p["LEG"]
    z0, z1 = -drop, -flange
    run = z1 - z0
    pad = _pad(p)
    if mode == "straight":
        sections = [Pos(0, 0, z0) * pad, Pos(0, 0, z1) * skin]
    elif mode == "sprung":
        # One hourglass neck: a TPU leaf spring. The waist is pinched hard across X and only lightly
        # along Y, so its second moment is far smaller fore-aft than sideways and it bends in the
        # arm's own plane instead of folding out from under the quad.
        sections = [Pos(0, 0, z0) * pad,
                    Pos(0, 0, z0 + run * p["WAIST_AT"]) * _pad(p, *p["WAIST"]),
                    Pos(0, 0, z1) * skin]
    elif mode == "bellows":
        # Concertina: alternate narrow/wide stations pinched across X only. Pinching the 50 mm length
        # as well would put a ~52 deg flank on every fold and the part would need supports.
        n, top = p["BELLOWS_N"], p["BELLOWS_TOP"]
        sections = [Pos(0, 0, z0 + run * (i / (2 * n)) * top) * _pad(p, p["BELLOWS_IN"] if i % 2 else 1.0)
                    for i in range(2 * n + 1)]
        sections.append(Pos(0, 0, z1) * skin)
    else:
        raise ValueError(f"unknown LEG {mode!r}; expected straight, sprung or bellows")
    return loft(sections, ruled=True)


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


def build(variant: str = ASSEMBLY_VARIANT, **overrides) -> dict[str, Part]:
    global _EFFECTIVE
    spec = VARIANTS.get(variant) or {}
    p = _params(**{**spec.get("params", {}), **overrides})  # an explicit override still wins
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


def _lowest_point(part: Part) -> tuple[float, float, float]:
    """(z, x, y) of the part's lowest vertex: where it would touch the ground."""
    v = min(part.vertices(), key=lambda q: q.Z)
    return round(v.Z, 3), round(v.X, 2), round(v.Y, 2)


def _stance(plane: float) -> list[tuple[str, bool, str]]:
    """THE cross-module stance check: within ONE INSTALLABLE SET, everything that touches down is
    coplanar and nothing else reaches below that plane.

    The guards are the landing gear of the set they are in, so the comparison belongs here, and it
    is scoped the same way the combined assembly is: EXCLUSIVE is resolved FIRST, with motor_guard
    pinned as installed. That matters because the airframe has more than one legitimate stance - the
    extended-feet family (arm_protector_feet, which declares EXCLUSIVE = ("motor_guard",), together
    with front_bumper_feet) is deliberately coplanar 6.8 mm lower, and a module that can never be
    bolted on at the same time as these guards must not be measured against them. The plane is
    reported as a property of the set that was found, not asserted against one global constant.

    Only a member that DECLARES a MIN_Z below `plane` can possibly reach below it - every other
    module's own generic "above the landing plane" row already keeps it higher - so only those are
    built, which keeps the row complete without rebuilding the whole set.
    """
    import pkgutil  # noqa: PLC0415

    from tigerbee import accessories as A  # noqa: PLC0415, N812
    from tigerbee.accessories import attr, build_accessory, discover_accessories  # noqa: PLC0415
    deep, below, skipped, other_kit = {}, {}, [], []
    installed = [NAME]
    names = sorted(i.name for i in pkgutil.iter_modules(A.__path__) if not i.name.startswith("_"))
    for name in names:
        if name == NAME:
            continue
        # Import and validate one module at a time: a sibling still being written must be NAMED in
        # the row, not allowed to turn the whole comparison into a single import error.
        try:
            mod = discover_accessories([name])[name]
            mine = attr(mod, "EXCLUSIVE")
            if any(name in attr(discover_accessories([i])[i], "EXCLUSIVE") or i in mine for i in installed):
                other_kit.append(name)  # cannot be installed with these guards: a different stance
                continue
            installed.append(name)
            if attr(mod, "MIN_Z") >= plane - 1e-6:
                continue
            built = build_accessory(mod)
        except Exception as exc:  # noqa: BLE001
            skipped.append(f"{name} ({type(exc).__name__})")
            continue
        for label, part in built.items():
            z, x, y = _lowest_point(part)
            deep[label] = f"{z} at ({x}, {y})"
            if z < plane - 1e-6:
                below[label] = z
    set_plane = min([plane, *below.values()])
    return [("stance: in the installable set that includes these guards, nothing touches down below "
             "them", not below,
             f"set plane Z {set_plane} (the four feet are at Z {plane}); "
             + (f"also reaching it: {', '.join(f'{k} {v}' for k, v in deep.items())}"
                if deep else "no other member declares a MIN_Z below the feet")
             + (f"; BELOW THE FEET, so the quad would rest on a tripod: {below}" if below else "")
             + (f"; a different stance (EXCLUSIVE with this set): {', '.join(other_kit)}" if other_kit else "")
             + (f"; not checked (would not import or build): {', '.join(skipped)}" if skipped else ""))]


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

        # from the EFFECTIVE drop: checks() is handed base labels, so the table's base entry would
        # describe the stock leg however tall the variant being checked actually is
        over = overhangs(g, PRINT[label], bridge_ok=_bridges(p["DROP"]), material=MATERIAL)
        out.append((f"{label}: prints foot-down without support", not over, "; ".join(over) or "none"))

    shapes = [parts[label].wrapped for label in ARMS]
    distinct = all(not a.IsSame(b) for i, a in enumerate(shapes) for b in shapes[i + 1:])
    spread = max(volumes) - min(volumes)
    out.append(("four independent shapes", distinct and len(shapes) == 4, f"{len(shapes)} shapes"))
    out.append(("all four the same volume", spread < 1.0, f"spread {spread:.4f} mm³"))
    # A runaway-boolean guard, not a design limit, so the ceiling tracks the leg: the pad is 23 x 50,
    # so every extra mm of DROP can add at most ~1.15 cm³ of leg before something has gone wrong.
    vmax = 22000 + max(0.0, p["DROP"] - (P.Z_ARM - GROUND_Z)) * 1150
    out.append((f"volume 10-{vmax / 1000:.1f} cm³", 10000 <= volumes[0] <= vmax, f"{volumes[0] / 1000:.2f} cm³"))

    # --- the stance: the four feet are the airframe's landing gear ---------------------------
    lows = {label: _lowest_point(parts[label]) for label in ARMS}
    plane = P.Z_ARM - p["DROP"]
    off = {l: z for l, (z, _x, _y) in lows.items() if abs(z - plane) > 1e-6}
    out.append((f"all four feet stand on the ground plane Z {plane:.1f}", not off,
                "; ".join(f"{l} {z} at ({x}, {y})" for l, (z, x, y) in lows.items())))
    xs = {l: x for l, (_z, x, _y) in lows.items()}
    ys = {l: y for l, (_z, _x, y) in lows.items()}
    square = (min(xs.values()) < 0 < max(xs.values())) and (min(ys.values()) < 0 < max(ys.values()))
    out.append(("the four contact points straddle both axes (a level four-point stance, not a tripod)",
                square and len(lows) == 4,
                f"x {min(xs.values()):.1f}..{max(xs.values()):.1f}, y {min(ys.values()):.1f}..{max(ys.values()):.1f}"))
    out += _stance(plane)

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
