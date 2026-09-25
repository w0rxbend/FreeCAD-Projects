"""Pedestal GPS tray on two splayed eyelet arms - the user's CAD reference, built for this frame.

Reference: refs/gps-pigtail-mount/reference-tray-pedestal-eyelets.png. A shallow tray with the
module's underside open straight through the floor, raised on a flared pedestal, carried by two
arms that sweep out and down to cylindrical eyelets, "GPS" in relief on the forward face and a
half-round cable channel beside the lettering.

WHERE IT MOUNTS, AND WHY THERE. The two Ø4.6 `top_accessory` holes at (±27.3, 91) on plate_top,
54.6 mm apart - the widest unclaimed pair on the frame, which is what makes the splayed arms of the
reference structural rather than decorative. It bridges the top plate's fork window, so the arms
land on the two prongs and the tray sits over the opening between them.

Forward rather than aft, which is the opposite of the usual "GPS goes on a tail mast" instinct, and
deliberately: on this airframe `tail_block` puts the VIDEO TRANSMITTER in the tail, and the VTX is
the loudest GPS interferer on a quad. Mounting forward puts ~185 mm between the patch and the VTX,
against ~40 mm on a tail mast. It also leaves the rear-tip bolt axes (±16.5, -94) free, which
`antenna_mast` and `rx_antenna_v_holder` both need - a GPS mount that took those would force the
pilot to choose between a fix and an RX antenna.

HEIGHT. The patch sits 14 mm above the carbon (pocket floor Z 50, the plate top face is Z 36). Carbon
fibre is conductive, so a ceramic patch lying on it is detuned and partly shadowed by its own ground
plane; lifting it clear of the weave and out of the top plate's near field is what the pedestal is
for. Higher would be better for the fix and worse for the leverage on two M3 bolts, so 10 mm is the
compromise - raise PEDESTAL_H if you fly with a mast in mind.

EXCLUSIVE with `gopro_mount`, which takes the same two holes, and with `gps_mount`, which is the
other GPS option on this frame (a mast and platform further aft on the Ø4.6 pair at (±31.3, 63.5));
installing two GPS mounts is not a configuration anyone wants.
"""

from build123d import RectangleRounded, Text

from tigerbee.accessories._common import *  # noqa: F401,F403

NAME = "gps_tray"
TITLE = "GPS tray on splayed eyelet arms"
MATERIAL = "PETG"
PRINT = {"gps_tray": (0, 0, -1)}  # eyelet/pedestal seating plane on the bed, tray opening up
EXCLUSIVE = ("gopro_mount", "gps_mount", "front_bumper_skull_jaw", "callsign_plate")
MOUNTS = ("plate_top top face Z 36 (both eyelet pads bear on it, either side of the fork window)",
          "Ø4.6 top_accessory holes (±27.3, 91), 54.6 mm apart")
HARDWARE = ("2 x M3 x 12 button head + 2 x M3 nyloc nuts (heads in the eyelets, nuts under the "
            "plate)",
            "optional 1 x 2.5 mm zip tie through the cable channel to strain-relieve the GPS lead")
NOTES = ("Bridges the top-plate fork window on the two Ø4.6 accessory holes. The patch sits 14 mm "
         "clear of the carbon; the floor is open so the module's own ground plane is not shadowed. "
         "Forward mounting puts the maximum distance between the patch and the tail-mounted VTX.")

# --- the GPS module the pocket is cut for -----------------------------------------------------
GPS_W = 25.0   # across the frame X
GPS_L = 25.0   # along the frame Y
GPS_H = 8.0    # body height; the pocket is this deep
GPS_FIT = 0.3  # per side

# --- the tray ---------------------------------------------------------------------------------
WALL_T = 2.0    # pocket wall
FLOOR_T = 2.0   # tray floor, the ring the module rests on
WINDOW_INSET = 3.0  # floor ring width: the open window is the pocket inset by this all round
TRAY_Y = 81.0   # tray centre, set back so it clears camera_visor and front_bumper

# --- the pedestal -----------------------------------------------------------------------------
PEDESTAL_H = 12.0  # plate top face to tray floor underside; also sets the patch height
PEDESTAL_FLARE = 2.0  # the base is this much wider per side than the tray above it
TRAY_R = 3.0          # plan corner radius of the tray

# --- the arms and eyelets ---------------------------------------------------------------------
EYE_XY = hole_xy("top_accessory", "plate_top")  # (±27.3, 91) and the others; filtered below
EYE_X = 27.3
EYE_Y = 91.0
EYE_OD = 9.5
EYE_H = 5.0
EYE_BORE = D_M3_THRU  # 3.4
ARM_W = 11.0  # arm width in Y: must REACH PAST the tray's rounded front corner, not
#               stop just short of it - a 9.0 arm left a 1.19 mm web at (12.9, 95.7, 48)
#               where its front face and the corner radius nearly met
ARM_T = 4.0   # arm thickness at the eyelet end

# --- the cable channel and the lettering ------------------------------------------------------
CABLE_D = 4.2      # half-round channel for the GPS lead
MARK_TEXT = "GPS"
MARK_H = 5.0       # cap height
MARK_RELIEF = 1.0  # how far the letters stand proud

Z_BASE = Z_TOP_TOP            # 36.0
Z_FLOOR = Z_BASE + PEDESTAL_H  # 44.0 tray floor underside
Z_POCKET = Z_FLOOR + FLOOR_T   # 46.0 the module's underside
Z_TOP = Z_POCKET + GPS_H       # 54.0 pocket wall top


def _dims(p: dict) -> tuple[float, float, float, float, float, float]:
    """(pocket w, pocket l, tray w, tray l, base w, base l) - every plan size derives from the
    module the pocket is cut for, so changing GPS_W/GPS_L moves the whole part consistently."""
    pw = p["GPS_W"] + 2 * p["GPS_FIT"]
    pl = p["GPS_L"] + 2 * p["GPS_FIT"]
    tw, tl = pw + 2 * p["WALL_T"], pl + 2 * p["WALL_T"]
    return pw, pl, tw, tl, tw + 2 * p["PEDESTAL_FLARE"], tl + 2 * p["PEDESTAL_FLARE"]


def _pedestal(p: dict) -> Part:
    """Flared plinth: a tapered extrusion from the wide seating footprint up to the tray outline,
    so the walls lean outward toward the plate the way the reference's do."""
    *_, bw, bl = _dims(p)
    taper = degrees(atan2(p["PEDESTAL_FLARE"], p["PEDESTAL_H"]))
    # The base radius is TRAY_R + FLARE, not TRAY_R: a tapered extrusion offsets the whole wire,
    # so a 3.0 base radius arrives at the top as 1.0 and the pedestal's corners then stand ~2 mm
    # proud of the tray above them - an unsupported lip, and the only sub-floor wall on the part.
    sk = Pos(0, p["TRAY_Y"], Z_BASE) * RectangleRounded(bw, bl, p["TRAY_R"] + p["PEDESTAL_FLARE"])
    return extrude(sk, amount=p["PEDESTAL_H"], taper=taper)


def _window(p: dict) -> Part:
    """The opening, cut through tray floor AND pedestal in one go after everything is fused: the
    patch needs sky beneath it, and a solid plinth would be dead weight bolted to a 7-inch nose."""
    pw, pl, *_ = _dims(p)
    w, l = pw - 2 * p["WINDOW_INSET"], pl - 2 * p["WINDOW_INSET"]
    return extrude(Pos(0, p["TRAY_Y"], Z_BASE - 1.0) * RectangleRounded(w, l, 3.0),
                   amount=p["PEDESTAL_H"] + p["FLOOR_T"] + 2.0)


def _tray(p: dict) -> Part:
    """Walled tray with the floor open: the module drops in and its underside sees sky, not PETG."""
    pw, pl, tw, tl, *_ = _dims(p)
    z_pocket = Z_BASE + p["PEDESTAL_H"] + p["FLOOR_T"]
    z_top = z_pocket + p["GPS_H"]
    body = extrude(Pos(0, p["TRAY_Y"], Z_BASE + p["PEDESTAL_H"]) * RectangleRounded(tw, tl, p["TRAY_R"]),
                   amount=p["FLOOR_T"] + p["GPS_H"])
    # square corners, not rounded: the module is square, and a rounded pocket either pinches its
    # corners or needs relief circles that eat the 2.0 mm wall down to 0.4
    pocket = extrude(Pos(0, p["TRAY_Y"], z_pocket) * Rectangle(pw, pl), amount=p["GPS_H"] + 1.0)
    return body - pocket


def _arm(p: dict, sign: int) -> Part:
    """One arm plus its eyelet. Drawn as a side profile in XZ and extruded in Y, so the sweep from
    the tall pedestal down to the short eyelet pad is explicit rather than a loft's guess."""
    _pw, _pl, tw, *_ = _dims(p)
    # Reference the arm's inner end to the pedestal's NARROWEST (top) half-width, not its base.
    # Against the base the arm's upper corner hung 1.5 mm outboard of the leaning wall and left an
    # unsupported web there - 12 rays at 1.12 mm, the only sub-floor material on the plain part.
    x_ped = sign * (tw / 2 - 1.0)
    xe = sign * p["EYE_X"]
    z_hi = Z_BASE + p["PEDESTAL_H"]
    prof = Polygon((x_ped, Z_BASE), (x_ped, z_hi), (xe, Z_BASE + p["EYE_H"]), (xe, Z_BASE),
                   align=None)
    arm = Pos(0, p["EYE_Y"], 0) * extrude(Plane.XZ * prof, amount=p["ARM_W"] / 2, both=True)
    eye = cylinder(xe, p["EYE_Y"], Z_BASE, Z_BASE + p["EYE_H"], p["EYE_OD"])
    return arm + eye


def _face_y(p: dict, z: float) -> float:
    """Y of the pedestal's forward face at height z. The flare leans the face outward going down,
    so anything cut into or standing out of it has to be placed against the face at its OWN z -
    a single nominal Y sinks the lettering at the bottom and floats it at the top."""
    *_, _bw, bl = _dims(p)
    frac = (z - Z_BASE) / p["PEDESTAL_H"]
    return p["TRAY_Y"] + bl / 2 - p["PEDESTAL_FLARE"] * frac


def _cable_channel(p: dict) -> Part:
    """Half-round groove across the forward face just under the tray lip, so the GPS lead turns
    down off the tray over a radius instead of a printed edge."""
    z = Z_BASE + p["PEDESTAL_H"] - p["CABLE_D"] / 2 - 0.8
    bar = Cylinder(p["CABLE_D"] / 2, 26.0, rotation=(0, 90, 0))
    return Pos(0, _face_y(p, z) + p["CABLE_D"] * 0.15, z) * bar


def _lettering(p: dict) -> Part:
    """`GPS` in relief low on the forward face, clear of the cable groove above it. Drawn in XZ and
    extruded toward -Y with its OUTER face set MARK_RELIEF proud of the leaning pedestal face."""
    z0 = Z_BASE + 1.3
    z = z0 + p["MARK_H"] / 2
    txt = Text(p["MARK_TEXT"], font_size=p["MARK_H"], align=(Align.CENTER, Align.CENTER))
    slab = extrude(Plane.XZ * txt, amount=p["MARK_RELIEF"] + 3.0)
    # against the face at the letters' BOTTOM edge, which is the most outboard point of the band:
    # referenced to the mid-height instead, the lean buries the lower half of every glyph
    return Pos(0, _face_y(p, z0) + p["MARK_RELIEF"], z) * slab


def build(**overrides) -> dict[str, Part]:
    p = {k: globals()[k] for k in
         ("GPS_W", "GPS_L", "GPS_H", "GPS_FIT", "WALL_T", "FLOOR_T", "WINDOW_INSET", "TRAY_Y",
          "PEDESTAL_H", "PEDESTAL_FLARE", "TRAY_R", "EYE_X", "EYE_Y", "EYE_OD", "EYE_H", "EYE_BORE",
          "ARM_W", "ARM_T", "CABLE_D", "MARK_TEXT", "MARK_H", "MARK_RELIEF")}
    unknown = set(overrides) - set(p)
    assert not unknown, f"unknown parameter(s): {sorted(unknown)}"
    p.update(overrides)

    part = _pedestal(p) + _tray(p) + _arm(p, +1) + _arm(p, -1)
    part -= _window(p)
    part -= _cable_channel(p)
    part += _lettering(p)
    for sign in (+1, -1):
        part -= cylinder(sign * p["EYE_X"], p["EYE_Y"], Z_BASE - 1.0,
                         Z_BASE + p["EYE_H"] + 1.0, p["EYE_BORE"])
    part = part.clean()
    if isinstance(part, Compound) and not isinstance(part, Part):
        part = Part() + part.solids()
    part.label = NAME
    return {NAME: part}


def _siblings() -> dict[str, Part]:
    """Accessories that share this end of the frame. A broken sibling must not make this check
    vacuous, so each import is reported rather than swallowed."""
    import importlib
    out: dict[str, Part] = {}
    for name in ("camera_pod", "camera_visor", "front_bumper_skull_jaw", "battery_pad",
                 "callsign_plate", "front_bumper"):
        if name in EXCLUSIVE:  # declared incompatible: never installed together, so never compared
            continue
        try:
            mod = importlib.import_module(f"tigerbee.accessories.{name}")
            for label, part in mod.build().items():
                out[f"{name}:{label}"] = part
        except Exception as exc:  # noqa: BLE001
            out[f"{name}:UNAVAILABLE"] = exc  # surfaced in the detail string
    return out


def _mark_band(p: dict) -> Part:
    """The label band, as a solid box 1 mm larger than the glyphs all round.

    min_wall's `allow` skips a ray whose START POINT is inside the declared solid, and a sample sits
    exactly ON the glyph surface, where is_inside is a coin toss - declaring the lettering itself
    caught only half its rays. A band around it catches them all. It hides nothing real: the
    pedestal wall behind this band is ~5 mm thick, so the only sub-floor material inside it is the
    relief itself."""
    lett = _lettering(p)
    if not MARK_TEXT or lett.volume <= 0:
        return Part()
    b = lett.bounding_box()
    return box(b.min.X - 1.0, b.min.Y - 1.0, b.min.Z - 1.0,
               b.max.X + 1.0, b.max.Y + 1.0, b.max.Z + 1.0)


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    part = parts[NAME]
    p = {k: globals()[k] for k in ("GPS_W", "GPS_L", "GPS_H", "GPS_FIT", "WALL_T", "FLOOR_T",
                                   "WINDOW_INSET", "TRAY_Y", "PEDESTAL_H", "PEDESTAL_FLARE",
                                   "TRAY_R",
                                   "EYE_X", "EYE_Y", "EYE_OD", "EYE_H", "CABLE_D", "MARK_H",
                                   "MARK_RELIEF", "MARK_TEXT")}
    out: list[tuple[str, bool, str]] = []

    # --- the two bolt axes are REAL frame holes, not invented ones ---------------------------
    real = {(round(abs(x), 2), round(y, 2)) for x, y in hole_xy("top_accessory", "plate_top")}
    out.append(("the eyelets sit on real top_accessory holes",
                (round(p["EYE_X"], 2), round(p["EYE_Y"], 2)) in real,
                f"({p['EYE_X']}, {p['EYE_Y']}) against {sorted(real)}"))
    for sign, hand in ((+1, "right"), (-1, "left")):
        ok, detail = coaxial(part, (sign * p["EYE_X"], p["EYE_Y"]), EYE_BORE,
                             Z_BASE, Z_BASE + p["EYE_H"])
        out.append((f"{hand} eyelet bore coaxial with top_accessory", ok, detail))

    # --- seating on the REAL top face, holes subtracted ---------------------------------------
    contact = seats_on(part, "plate_top", Z_TOP_TOP)
    out.append(("both eyelet pads bear on plate_top at Z 36", contact >= 150.0,
                f"{contact:.1f} mm² of true contact (holes and outline subtracted)"))

    # --- the rear... front discs are the tight ones back here ---------------------------------
    disc = prop_disc_violation(part)
    bb = part.bounding_box()
    out.append(("outside the front prop keep-out discs", disc < EPS,
                f"{disc:.4f} mm³ inside; widest |x| {max(abs(bb.min.X), abs(bb.max.X)):.2f} "
                f"at y {p['EYE_Y']}"))

    # --- the module the pocket exists for actually drops in -----------------------------------
    z_pocket = Z_BASE + p["PEDESTAL_H"] + p["FLOOR_T"]
    puck = box(-p["GPS_W"] / 2, p["TRAY_Y"] - p["GPS_L"] / 2, z_pocket,
               p["GPS_W"] / 2, p["TRAY_Y"] + p["GPS_L"] / 2, z_pocket + p["GPS_H"])
    clash = isect(part, puck)
    out.append((f"a {p['GPS_W']:.0f} x {p['GPS_L']:.0f} x {p['GPS_H']:.0f} module drops into the pocket",
                clash < EPS, f"{clash:.4f} mm³ of tray in the module's volume, "
                             f"{p['GPS_FIT']} mm designed fit per side"))
    # and the floor is genuinely open under it, so the patch is not sitting on a PETG plate
    win = box(-1.0, p["TRAY_Y"] - 1.0, z_pocket - p["FLOOR_T"] - 1.0,
              1.0, p["TRAY_Y"] + 1.0, z_pocket + 1.0)
    out.append(("the floor is open under the patch", isect(part, win) < EPS,
                f"{isect(part, win):.4f} mm³ of floor on the tray's centre axis"))

    # --- the height claim the docstring makes -------------------------------------------------
    out.append(("patch >= 12 mm clear of the carbon", z_pocket - Z_TOP_TOP >= 12.0,
                f"pocket floor Z {z_pocket:.1f}, plate top face Z {Z_TOP_TOP:.1f}: "
                f"{z_pocket - Z_TOP_TOP:.1f} mm"))

    # --- the lettering is legible and not a thin-wall trap -------------------------------------
    plain = build(MARK_TEXT="")[NAME]
    relief_vol = part.volume - plain.volume
    out.append((f"'{MARK_TEXT}' stands {p['MARK_RELIEF']} mm proud and is real material",
                relief_vol > 15.0, f"{relief_vol:.1f} mm³ of relief"))

    # --- no collision with the accessories that share this end --------------------------------
    hits, missing = [], []
    for name, other in _siblings().items():
        if isinstance(other, Exception):
            missing.append(f"{name} ({type(other).__name__})")
            continue
        v = isect(part, other)
        if v > EPS:
            hits.append(f"{name} {v:.3f} mm³")
    out.append(("clear of the front accessories it shares the nose with", not hits,
                f"overlaps {hits or 'none'}" + (f"; NOT CHECKED: {missing}" if missing else "")))

    # --- the camera must not see it, at any tilt ----------------------------------------------
    worst = max((isect(part, fov_wedge(t)) for t in range(0, 41, 5)), default=0.0)
    out.append(("outside the camera field of view over tilt 0-40 deg", worst < EPS,
                f"worst {worst:.4f} mm³ in the FOV wedge"))

    # The embossed glyphs are 0.8 mm of relief on ~0.9 mm strokes: thin BY DESIGN, the way a
    # moulded label is, and the only such feature on the part. Declared, not waived - everything
    # outside this envelope is still held to the full floor.
    # Measured by ray sampling rather than min_wall's offset path, DELIBERATELY. OCCT erodes this
    # shape - a thin-walled tray over an open tapered plinth - from 12305 mm³ to 0.7 mm³, so the
    # opening's residual is the whole part and says nothing. The collapse is silent: erode() returns
    # a valid solid, just a nonsensical one, so min_wall never falls back on its own.
    band = _mark_band(p)
    floor = MATERIALS[MATERIAL]["wall"]
    thin, worst, wall_detail = ray_thickness(part, floor,
                                             allow=(band,) if band.volume > 0 else ())
    ok_wall = not thin
    out.append((f"min wall >= {floor} outside the declared label band", ok_wall, wall_detail))
    return out
