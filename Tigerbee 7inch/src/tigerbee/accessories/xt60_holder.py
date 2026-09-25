"""XT60 pigtail socket holder: standoff clip + braced pocket block, plug facing rearward."""

from build123d import Circle, Part, Plane, Pos, Rectangle, chamfer, extrude, fillet

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "xt60_holder"
TITLE = "XT60 pigtail holder"
MATERIAL = "TPU95A"
PRINT = {"xt60_holder_right": (0, 0, 1), "xt60_holder_left": (0, 0, 1)}
EXCLUSIVE = ()
ASSEMBLY_LABELS = ("xt60_holder_right",)  # install one side only; the pair is the left/right choice
MOUNTS = ("standoff_rear_arm_<side> Ø6 shaft over Z 22-33.8 (the clip, above the side panel's rear clip)",
          "plate_bottom top face Z 2 (the inboard post stands on it and takes the plug's pull)")
HARDWARE = ("none - 0.8 mm snap onto the Ø6 standoff; the XT60 socket presses in past the 1.0 mm lip",)
NOTES = (
    "Clips onto the rear-arm standoff above the side panel's rear clip (Z 22-33.8) and carries the XT60 "
    "socket on edge behind it, plug facing rearward. A post down the inboard face stands on plate_bottom "
    "(Z 2), so the holder cannot slide down the standoff and the plug's pull is taken by the bottom plate "
    "instead of the clip alone - no companion accessory is required. The socket is pushed in from the rear "
    "through the chamfered 1.0 mm lip; the battery leads leave through the arched window in the front wall "
    "and run forward to the stack. Pocket centred at x 22 (not 26) so the mated male plug stays clear of "
    "the rear prop keep-out; route the lead inboard behind the holder. Install one side only. Envelope "
    "(right) x 16.0-29.7 (the clip ring reaches past the block), y -28.5..-57.4, Z 2.0-33.8. Prints top "
    "face down; the pocket floor is an 8.7 mm bridge."
)

# --- parameters (mm) ------------------------------------------------------------------------
XT_W = 8.7    # XT60 housing thickness 8.15 + 0.275/side (pocket X)
XT_L = 16.2   # housing length (pocket Y, plug axis)
XT_H = 16.1   # housing height 15.6 + 0.25/side, socket on edge (pocket Z)
LIP = 1.0     # retaining rim on all four edges of the rear opening
LEAD_IN = 0.5  # 45 deg chamfer on the rear rim so the socket funnels in
WALL = 1.6
WALL_MIN = 1.2  # TPU minimum outside the retaining lip
SNAP = 0.8      # clip mouth = STANDOFF_D - SNAP = 5.2

BORE_D = D_CLIP_BORE           # 6.5 around the Ø6 standoff
CLIP_Z0, CLIP_Z1 = 22.0, 33.8  # above side_panels' rear clip (Z 9.2-21.5), 0.2 under plate_top
BLOCK_X0, BLOCK_X1 = 16.0, 28.0
BLOCK_Y0 = -38.6               # front face: 0.38 clear of the side-panel clip OD (y -38.22)
POST_X1 = 19.0                 # brace down to plate_bottom, x BLOCK_X0..POST_X1
POST_Y0, POST_Y1 = -40.2, -51.5
POST_FILLET = 1.5
WEB_X0 = 24.5                  # neck joining the clip ring to the block
WEB_CLEAR = 0.28               # web front edge outside the clip bore edge
FILLET_R = 1.0                 # outer corners; r1 keeps the rear rim 1.65 wide at the rear face
WIN_W, WIN_SPRING_Z = 6.0, 22.0  # lead window: width, arch centre (apex = + WIN_W/2)
STANDOFF = "standoff_rear_arm_right"
PLUG_L, PLUG_W, PLUG_H = 16.1, 8.5, 16.6  # mated male housing, fully outside the rear face

# --- derived extents (frame coords, right side) ----------------------------------------------
_AX, _AY = STANDOFF_XY[STANDOFF]
WEB_Y1 = _AY - BORE_D / 2 - WEB_CLEAR           # -36.903, 0.53 behind the Ø6 standoff surface
BLOCK_Y1 = BLOCK_Y0 - (WALL + XT_L + LIP)       # -57.4, rear face
BLOCK_Z1 = CLIP_Z1
BLOCK_Z0 = BLOCK_Z1 - (XT_H + 2 * WALL)         # 14.5
POCKET_X0, POCKET_X1 = (BLOCK_X0 + BLOCK_X1 - XT_W) / 2, (BLOCK_X0 + BLOCK_X1 + XT_W) / 2
POCKET_Y0, POCKET_Y1 = BLOCK_Y0 - WALL, BLOCK_Y0 - WALL - XT_L   # -40.2 .. -56.4
POCKET_Z0, POCKET_Z1 = BLOCK_Z0 + WALL, BLOCK_Z1 - WALL          # 16.1 .. 32.2
POCKET_XC, POCKET_ZC = (POCKET_X0 + POCKET_X1) / 2, (POCKET_Z0 + POCKET_Z1) / 2
# the window clears the front-inboard corner fillet (>= 1.2 of wall beside it) and stays inboard
# of the web, which stands in front of the block from Z 22 up
WIN_X1 = WEB_X0 - 0.15
WIN_X0 = WIN_X1 - WIN_W

# Bridge exemption for the pocket floor (which the lead window extends forward to the front face)
# and the 1.0 mm lip ledge above it, in PRINT coordinates: the part is turned over about X, so
# x_p = x - _XC, y_p = -y - _YC, z_p = BLOCK_Z1 - z.
_RING = c_clip((_AX, _AY), CLIP_Z0, CLIP_Z1 - CLIP_Z0, opening_deg=0.0, material=MATERIAL,
               bore_d=BORE_D, wall=WALL, snap=SNAP).bounding_box()
_XC = (BLOCK_X0 + max(BLOCK_X1, _RING.max.X)) / 2
_YC = -(BLOCK_Y1 + _RING.max.Y) / 2
_BRIDGE = ("box", POCKET_X0 - _XC - 1.0, -BLOCK_Y0 - _YC - 1.0, BLOCK_Z1 - POCKET_Z0 - 1.8,
           POCKET_X1 - _XC + 1.0, -BLOCK_Y1 - _YC + 1.0, BLOCK_Z1 - POCKET_Z0 + 0.4)
BRIDGE_OK = {f"{NAME}_right": (_BRIDGE,),
             f"{NAME}_left": (("box", -_BRIDGE[4], *_BRIDGE[2:4], -_BRIDGE[1], *_BRIDGE[5:]),)}


def _rim_opening() -> Part:
    """Rear aperture: the pocket inset by the 1.0 lip on all four edges."""
    return box(POCKET_X0 + LIP, BLOCK_Y1 - 1.0, POCKET_Z0 + LIP, POCKET_X1 - LIP, POCKET_Y1, POCKET_Z1 - LIP)


def _lead_window() -> Part:
    """Arched slot through the front wall: floor flush with the pocket floor so it prints as one
    bridge, top a Ø WIN_W arch (<= TPU arch limit 10) so nothing overhangs. The two leads leave the
    socket stacked (the XT60's bullets sit across its 15.6 mm face, which is vertical here)."""
    xc = (WIN_X0 + WIN_X1) / 2
    prof = (Pos(xc, (POCKET_Z0 + WIN_SPRING_Z) / 2) * Rectangle(WIN_W, WIN_SPRING_Z - POCKET_Z0)
            + Pos(xc, WIN_SPRING_Z) * Circle(WIN_W / 2))
    return extrude(Plane.XZ.offset(-BLOCK_Y0 - 0.5) * prof, amount=WALL + 1.0)


def _lip_region() -> Part:
    """The 1 mm rear rim - the only intentionally sub-1.2 mm feature (min-wall allowance)."""
    return box(BLOCK_X0, BLOCK_Y1, BLOCK_Z0, BLOCK_X1, POCKET_Y1, BLOCK_Z1)


def _block() -> Part:
    sk = Pos((BLOCK_X0 + BLOCK_X1) / 2, (BLOCK_Y0 + BLOCK_Y1) / 2) * Rectangle(BLOCK_X1 - BLOCK_X0,
                                                                               BLOCK_Y0 - BLOCK_Y1)
    # the front-outboard corner is left sharp because the web grows out of it
    corners = sk.vertices().filter_by(
        lambda v: not (abs(v.X - BLOCK_X1) < 1e-6 and abs(v.Y - BLOCK_Y0) < 1e-6))
    sk = fillet(corners, FILLET_R)
    return extrude(Plane.XY.offset(BLOCK_Z0) * sk, amount=BLOCK_Z1 - BLOCK_Z0)


def _post() -> Part:
    """Brace from the block down to the bottom plate: the holder's own Z stop."""
    sk = Pos((BLOCK_X0 + POST_X1) / 2, (POST_Y0 + POST_Y1) / 2) * Rectangle(POST_X1 - BLOCK_X0,
                                                                           POST_Y0 - POST_Y1)
    sk = fillet(sk.vertices().filter_by(lambda v: abs(v.Y - POST_Y1) < 1e-6), POST_FILLET)
    return extrude(Plane.XY.offset(Z_BOTTOM_TOP) * sk, amount=BLOCK_Z0 - Z_BOTTOM_TOP)


def build(**overrides) -> dict[str, Part]:
    holder = _block() + _post()
    holder += box(WEB_X0, BLOCK_Y0, CLIP_Z0, BLOCK_X1, WEB_Y1, CLIP_Z1)
    holder += c_clip((_AX, _AY), CLIP_Z0, CLIP_Z1 - CLIP_Z0, opening_deg=0.0, material=MATERIAL,
                     bore_d=BORE_D, wall=WALL, snap=SNAP)

    holder -= box(POCKET_X0, POCKET_Y1, POCKET_Z0, POCKET_X1, POCKET_Y0, POCKET_Z1)
    holder -= _rim_opening()
    holder -= _lead_window()

    rim = holder.edges().filter_by(
        lambda e: abs(e.bounding_box().min.Y - BLOCK_Y1) < 1e-6 and abs(e.bounding_box().max.Y - BLOCK_Y1) < 1e-6
        and POCKET_X0 <= e.bounding_box().min.X and e.bounding_box().max.X <= POCKET_X1
        and POCKET_Z0 <= e.bounding_box().min.Z and e.bounding_box().max.Z <= POCKET_Z1)
    holder = chamfer(rim, LEAD_IN)
    return pair(holder, NAME)


def _xt60_probe(sx: float = 1.0) -> Part:
    """8.4 x 16 x 15.5 socket body pushed fully back, its face flush with the block rear face."""
    return box(min(sx * (POCKET_XC - 4.2), sx * (POCKET_XC + 4.2)), BLOCK_Y1, POCKET_ZC - 7.75,
               max(sx * (POCKET_XC - 4.2), sx * (POCKET_XC + 4.2)), BLOCK_Y1 + 16.0, POCKET_ZC + 7.75)


def _plug_probe(sx: float = 1.0) -> Part:
    """The mated male housing sticking straight out of the rear face (worst case: no insertion depth)."""
    x0, x1 = sorted((sx * (POCKET_XC - PLUG_W / 2), sx * (POCKET_XC + PLUG_W / 2)))
    return box(x0, BLOCK_Y1 - PLUG_L, POCKET_ZC - PLUG_H / 2, x1, BLOCK_Y1, POCKET_ZC + PLUG_H / 2)


def _side_panel_parts() -> tuple[dict[str, Part], str]:
    """The real side panels when that module exists, else a probe for its rear clip (OD 9.7, Z 9.2-21.5)."""
    try:
        from tigerbee.accessories import side_panels
        return side_panels.build(), "side_panels.build()"
    except Exception:  # noqa: BLE001 - sibling module may not exist yet
        probe = {f"rear_clip_{s}": cylinder(sx * _AX, _AY, 9.2, 21.5, BORE_D + 2 * WALL)
                 for s, sx in (("right", 1.0), ("left", -1.0))}
        return probe, "rear-clip envelope probe (OD 9.7, Z 9.2-21.5)"


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    right, left = parts[f"{NAME}_right"], parts[f"{NAME}_left"]
    out = []

    hits = interference(right) + interference(left)
    out.append(("no frame interference", not hits, f"overlaps {hits or 'none'}"))

    for part, side, sx in ((right, "right", 1.0), (left, "left", -1.0)):
        ok, detail = coaxial(part, (sx * _AX, _AY), BORE_D, CLIP_Z0 + 0.01, CLIP_Z1 - 0.01)
        out.append((f"clip coaxial with standoff_rear_arm_{side}", ok, detail))
        probe = cylinder(sx * _AX, _AY, CLIP_Z0, CLIP_Z0 + 12.0, STANDOFF_D)
        gap = round(part.distance_to(probe), 4)
        out.append((f"Ø{STANDOFF_D} standoff probe clear of the {side} clip", isect(part, probe) < EPS
                    and abs(gap - STANDOFF_FIT) <= 0.05, f"{isect(part, probe):.3f} mm³, gap {gap}"))

    panels, source = _side_panel_parts()
    gap = min(right.distance_to(p) for p in panels.values())
    out.append(("clear of side_panels by >= 0.3", gap >= 0.3 - 1e-6, f"{gap:.3f} mm to {source}"))

    zmax = max(right.bounding_box().max.Z, left.bounding_box().max.Z)
    out.append((f"max Z <= {BLOCK_Z1}", zmax <= BLOCK_Z1 + 1e-6, f"{zmax:.3f}"))

    disc = prop_disc_violation(right) + prop_disc_violation(left)
    out.append(("outside the prop keep-out discs", disc < EPS, f"{disc:.3f} mm³"))

    plug = prop_disc_violation(_plug_probe(1.0)) + prop_disc_violation(_plug_probe(-1.0))
    edge = max_abs_x_at(BLOCK_Y1 - PLUG_L)
    out.append(("mated plug clear of the prop keep-out", plug < EPS,
                f"{plug:.3f} mm³; plug corner x {POCKET_XC + PLUG_W / 2:.2f} vs limit {edge:.2f} "
                f"at y {BLOCK_Y1 - PLUG_L:.1f}"))

    # the post lands on plate_bottom, so the holder cannot slide down the standoff
    contact = seats_on(right, "plate_bottom", Z_BOTTOM_TOP)
    out.append(("post seated on plate_bottom at Z 2", contact >= 25.0, f"{contact:.1f} mm² of contact"))

    socket = _xt60_probe()
    held = isect(right, socket)
    beyond = isect(right - _lip_region(), socket)
    out.append(("XT60 body fits the pocket (only the lip touches it)", beyond < EPS and held > 20.0,
                f"{held:.1f} mm³ captured by the lip, {beyond:.3f} mm³ elsewhere"))

    # the lead must have a way out of the pocket: a straight run from the socket's front face
    # through the front wall, clear of material
    lead = box(WIN_X0 + 0.25, POCKET_Y0, POCKET_Z0 + 0.2, WIN_X1 - 0.25, BLOCK_Y0 + 2.0, WIN_SPRING_Z - 0.3)
    out.append(("battery lead exits through the front wall", isect(right, lead) < EPS,
                f"{isect(right, lead):.3f} mm³ blocking a {WIN_W - 0.5:.1f} x "
                f"{WIN_SPRING_Z - 0.5 - POCKET_Z0:.1f} lead channel"))

    bed = sum(f.area for f in right.faces()
              if f.geom_type.name == "PLANE" and abs(f.center().Z - BLOCK_Z1) < 1e-4 and f.normal_at().Z > 0.999)
    out.append((f"bed contact at Z {BLOCK_Z1} >= 250 mm²", bed >= 250.0, f"{bed:.1f} mm²"))

    over = overhangs(right, PRINT[f"{NAME}_right"], bridge_ok=BRIDGE_OK[f"{NAME}_right"], material=MATERIAL)
    out.append(("no unsupported overhangs (pocket floor bridged)", not over, "; ".join(over) or "none"))

    out.append(("one solid per side", len(right.solids()) == 1 and len(left.solids()) == 1,
                f"{len(right.solids())} / {len(left.solids())}"))

    neck = box(WEB_X0 + 2.0, BLOCK_Y0, CLIP_Z0, WEB_X0 + 3.0, BLOCK_Y0 + 1.0, CLIP_Z1)
    out.append(("web solid between clip and block", abs(isect(right, neck) - neck.volume) < 1e-2,
                f"{isect(right, neck):.2f} of {neck.volume:.2f} mm³"))

    thin, worst, detail = ray_thickness(right, WALL_MIN, allow=(_lip_region(),))
    out.append((f"min wall >= {WALL_MIN} (the 1.0 rear lip is the only allowance)", not thin,
                f"thinnest {worst:.2f} mm - {detail}"))
    return out
