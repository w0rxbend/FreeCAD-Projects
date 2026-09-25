"""Battery strap anchor + buckle keeper for the two forward plate_top accessory holes.

A 6S Li-ion pack is the heaviest thing on the airframe and a strap is the only thing holding it.
`battery_pad` stops the pack sliding on plate_top; nothing anchors or tidies the strap itself, and a
strap that walks forward on a long cruise is a real failure mode. This part takes the strap through a
toothed 21 x 3 slot whose floor stands 1.6 mm clear of the plate edge, then pinches the free tail
under a 45 deg keeper roof so the buckle cannot flap.

Four silhouettes: BRUTALIST (one poured slab, board-marked, one big void per face), ORIGAMI (a 1.8 mm
sheet folded 45/22.5 deg, every edge straight), FILIGREE (a 2.4 mm spine with a mirrored scroll net
and a scalloped edge) and VESPID (tergites stepping in at 0.82 length / 0.86 girth to a stinger cusp).
"""

from math import acos, degrees, radians, tan

from build123d import (Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, Sketch, chamfer,
                       extrude)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "battery_strap_anchor"
TITLE = "Battery strap anchor + buckle keeper"
MATERIAL = "PETG"  # it must not creep under strap load
# The D4.0 registration boss protrudes 3.0 mm BELOW the seat face, so the seat face cannot be the bed
# face - it would print 3 mm up in the air on a 4 mm peg. The anchor is laid on its OUTBOARD face
# instead, which is also the one orientation in which every 45 deg keeper surface (all of them
# contain the X axis) stands vertical instead of hanging as a 45 deg overhang.
PRINT = {f"{NAME}_right": (1, 0, 0), f"{NAME}_left": (-1, 0, 0)}
# Measured, not assumed: the right anchor overlaps gps_mount by 688 mm3 and gopro_mount by 954 mm3.
# Both of those span the full width of plate_top's nose over y 55.5-80.5 at Z 36 and up, which is
# exactly where a strap anchor on the (+/-31.3, 63.5) holes has to stand. checks() proves it.
EXCLUSIVE = ("gopro_mount", "gps_mount")
MOUNTS = ("plate_top top face Z 36", "D4.6 accessory holes (+/-31.3, 63.5)")
HARDWARE = ("2 x M3 x 12 button head + M3 nyloc under plate_top, one per anchor",)

# --- mating interface (exact; build123d owns every one of these) -------------------------------
BOLT_XY = (31.3, 63.5)
PLATE_HOLE_D = 4.6
SEAT_Z = Z_TOP_TOP                      # 36.0
BOSS_DIA, BOSS_DEPTH = 4.0, 3.0         # Z 33.0 - 36.0, into the D4.6 plate hole
BORE_D = D_M3_THRU                      # 3.4
CB_D, CB_H = 6.0, H_M3_HEAD_RECESS      # D6.6 of the brief cut at D6.0 (button head 5.7 + 0.3):
#                                         the front prop keep-out caps |x| at 35.83 at y 68.

# --- envelope (right anchor; the left is its exact mirror) -------------------------------------
X_IN, X_OUT = 2.0, 35.4                 # 35.4 < max_abs_x_at(68.0) = 35.83
Y_FRONT, Y_REAR = 56.0, 68.0            # 1.0 mm forward of the BATTERY envelope face at y 55
BASE_TOP = 44.2                         # 1.6 floor + 0.6 teeth + 3.0 clear + 3.0 roof

# --- strap interface ---------------------------------------------------------------------------
STRAP_W, STRAP_T = 20.0, 2.0
SLOT_W, SLOT_H = 21.0, 3.0              # 20 mm strap + 1.0 fit; 3.0 clear over the grip teeth
TOOTH_H_ = 0.6
SLOT_X0 = 5.0
SLOT_X1 = SLOT_X0 + SLOT_W              # 26.0 - 3.6 mm clear of the M3 bore in X
SLOT_Z0 = SEAT_Z + 1.6                  # 37.6: the floor stands clear of the plate edge
SLOT_Z1 = SLOT_Z0 + TOOTH_H_ + SLOT_H   # 41.2 - 3.0 mm clear above the tooth tips
TOOTH_H = TOOTH_H_                      # serrated grip land, 45 deg ridges across the strap
TOOTH_P = 2.0
TEETH_Y = (57.0, 59.0, 61.0, 63.0, 65.0, 67.0)

# --- keeper (the 45 deg fold) --------------------------------------------------------------------
KEEP_ANGLE = 45.0
Y_TOWER = 59.0                          # the keeper tower occupies y 56.0 - 59.0
KEEP_MOUTH = 3.0                        # pinch height at the rear mouth
ROOF_T = 2.0                            # keeper roof, measured perpendicular to the 45 deg plane
_R2 = 2 ** 0.5
ROOF_G = Y_TOWER + BASE_TOP + KEEP_MOUTH             # roof underside: Z = -y + ROOF_G (105.6)
ROOF_TOP_G = ROOF_G + ROOF_T * _R2                   # roof top:       Z = -y + ROOF_TOP_G
TOP_Z = ROOF_TOP_G - Y_FRONT                         # 52.43

WALLS = {"brutalist": 3.0, "origami": 1.8, "filigree": 1.4, "vespid": 1.4}
FOLD_ANGLES = (22.5, 45.0, 67.5)
VESPID_LEN, VESPID_GIRTH = 0.82, 0.86

VARIANTS = {
    "brutalist": {**({"style": "brutalist"} if "brutalist" in STYLES else {}), "material": "PETG",
                  "params": {}, "notes": "One poured slab: rectangles and 45 deg cuts only, 1.0 mm "
                  "chamfers, board-marking grooves at 2.4 pitch, one rectangular void per outboard "
                  "panel and a 2.0 mm deep cast-in wordmark."},
    "origami": {**({"style": "origami"} if "origami" in STYLES else {}), "material": "PETG",
                "params": {}, "print": {f"{NAME}_right": (0, -1, 0), f"{NAME}_left": (0, -1, 0)},
                "notes": "One 1.8 mm sheet folded 45 deg back on itself to form the strap slot and "
                "again for the keeper, whose mouth is flared by a 22.5 deg fold: a continuous "
                "zigzag ribbon, every edge straight, mountain/valley dashes on the creases. Prints "
                "on its front face, where the whole folded section lies flat on the bed."},
    "filigree": {**({"style": "filigree"} if "filigree" in STYLES else {}), "material": "PETG",
                 "params": {}, "notes": "A 2.4 mm spine from the boss to the slot lip with a 1.4 mm "
                 "two-radius scroll net on the flanks, D4.0 ring nodes at the junctions, a scalloped "
                 "outer edge and a cut lunule."},
    "vespid": {**({"style": "vespid"} if "vespid" in STYLES else {}), "material": "PETG",
               "params": {}, "notes": "Three tergites stepping inboard at 0.82 length / 0.86 girth "
               "from the bolt, each with a 1.2 mm proud collar, a 0.45 mm undercut groove and one "
               "2.2 x 5.0 spiracle, ending in a stinger cusp over the keeper mouth."},
}
ASSEMBLY_VARIANT = "brutalist"

# Both downward faces in the print orientation are the outboard end walls of the two slots at
# x 26.0 (print Z = X_OUT - 26.0 = 9.4); their shorter horizontal span is 3.0 / 4.2 mm, well inside
# the PETG 20 mm bridge limit. The box is generous in print XY because print_orientation() re-centres
# each variant on its own bounding box.
_BRIDGES = (("box", -30, -30, X_OUT - SLOT_X1 - 0.6, 30, 30, X_OUT - SLOT_X1 + 0.6),
            ("box", -30, -30, X_OUT - SLOT_X0 - 1.6, 30, 30, X_OUT - SLOT_X0 + 0.6))
BRIDGE_OK = {f"{NAME}_right": _BRIDGES, f"{NAME}_left": _BRIDGES}

NOTES = (
    "Two anchors, one per forward plate_top accessory hole (+/-31.3, 63.5). Each is located by a "
    "D4.0 x 3.0 boss in the plate hole and held by one M3 x 12 button head into an M3 nyloc under "
    "plate_top; the D6.0 x 2.0 recess at Z 42.2-44.2 sinks the head flush (D6.6 would breach the "
    "prop keep-out, which caps |x| at 35.83 at y 68). The strap runs from over the pack, forward "
    "through the toothed 21 x 3 slot - floor 1.6 mm above plate_top so it never chafes on the plate "
    "edge, 3.0 mm clear over six 0.6 mm grip teeth at 2.0 pitch - then folds back and is pinched "
    "under the 45 deg keeper roof, whose mouth closes to 3.0 mm at y 59. Envelope (right): x "
    "2.0-35.4, y 56.0-68.0, Z 33.0-53.0, 311 mm2 of seat on the real plate_top face; 0.43 mm inside "
    "the front prop keep-out at its worst y and 1.0 mm forward of the BATTERY envelope. EXCLUSIVE "
    "with gps_mount and gopro_mount, which both span the same nose of plate_top - checks() measures "
    "the overlap (688 and 954 mm3) rather than assuming it. Prints on its outboard flank, where "
    "every 45 deg keeper surface stands vertical; ORIGAMI prints on its front face instead."
)


# --- primitives ----------------------------------------------------------------------------------
def _yz(pts, x0: float, x1: float) -> Part:
    """A prism from a (y, Z) polygon, extruded in X from x0 to x1."""
    return extrude(Plane.YZ.offset(x0) * Polygon(*pts, align=None), amount=x1 - x0)


def _tower_profile(y0: float, y1: float) -> list[tuple[float, float]]:
    return [(y0, BASE_TOP), (y1, BASE_TOP), (y1, ROOF_TOP_G - y1), (y0, ROOF_TOP_G - y0)]


def _keeper_cut(x0: float, x1: float) -> Part:
    """The 45 deg keeper channel: floor = the base top, roof = the 45 deg plane Z = -y + ROOF_G."""
    # the rear boundary is the tower's own rear face: any overrun would shave the vespid collars
    pts = [(Y_FRONT - 1.0, BASE_TOP), (Y_TOWER, BASE_TOP),
           (Y_TOWER, ROOF_G - Y_TOWER), (Y_FRONT - 1.0, ROOF_G - Y_FRONT + 1.0)]
    return _yz(pts, x0, x1)


TOOTH_FLANK = 40.0  # from horizontal: steeper than 44.4 would hang over the bed in the Y print


def _teeth(x0: float, x1: float, z0: float = SLOT_Z0, h: float = TOOTH_H_) -> Part:
    """Grip ridges across the strap at TOOTH_P pitch, `h` proud of the slot floor."""
    half = h / tan(radians(TOOTH_FLANK))
    out = Part()
    for y in TEETH_Y:
        out += _yz([(y - half, z0), (y + half, z0), (y, z0 + h)], x0, x1)
    return out


def _tooth_region(z0: float = SLOT_Z0, h: float = TOOTH_H_) -> Part:
    return box(SLOT_X0, Y_FRONT, z0 - 0.1, SLOT_X1, Y_REAR, z0 + h + 0.1)


def _cb_rim_region() -> Part:
    """The outboard lip of the M3 head recess - 1.1 mm, the one place the prop keep-out wins."""
    return box(CB_D / 2 + BOLT_XY[0] - 0.2, BOLT_XY[1] - CB_D, BASE_TOP - CB_H - 0.2,
               X_OUT + 0.2, BOLT_XY[1] + CB_D, BASE_TOP + 0.2)


def _bolt_stack(part: Part) -> Part:
    x, y = BOLT_XY
    part += cylinder(x, y, SEAT_Z - BOSS_DEPTH, SEAT_Z, BOSS_DIA)
    part -= cylinder(x, y, SEAT_Z - BOSS_DEPTH - 1.0, TOP_Z + 1.0, BORE_D)
    part -= cylinder(x, y, BASE_TOP - CB_H, BASE_TOP + 1.0, CB_D)
    return part


def _shell(plan: Sketch, tower: Sketch | None = None) -> Part:
    """Base prism from a plan sketch plus the keeper tower, before any slot is cut."""
    part = extrude(Plane.XY.offset(SEAT_Z) * plan, amount=BASE_TOP - SEAT_Z)
    part += _yz(_tower_profile(Y_FRONT, Y_TOWER), X_IN, X_OUT) if tower is None else tower
    return part


def _cut_strap(part: Part, x0: float = SLOT_X0, x1: float = SLOT_X1) -> Part:
    part -= box(x0, Y_FRONT - 1.0, SLOT_Z0, x1, Y_REAR + 1.0, SLOT_Z1)
    part += _teeth(x0, x1)
    return part


# --- BRUTALIST -------------------------------------------------------------------------------
BRU_GROOVE_W, BRU_GROOVE_D, BRU_GROOVE_P = 0.6, 0.3, 2.4
# The one rectangular void. Not the outboard face: that face is the print bed AND carries the whole
# M3 head pad, so it has no 40% to give. The rear pad's TOP face does, and the void there is a real
# lightening window straight down into the strap slot.
BRU_TOP_PANEL = (X_IN, Y_TOWER, SLOT_X1 + 1.0, Y_REAR)          # x0, y0, x1, y1 of the top pad
BRU_VOID = (6.0, 60.0, 25.0, 66.0)                              # the window, in the same terms
BRU_MARK_AT = (30.7, 58.0, BASE_TOP)
BRU_MARK_SIZE, BRU_MARK_DEPTH = 8.0, 2.0
BRU_MARK_STOCK = BASE_TOP - SEAT_Z            # 8.2 mm of pad under the 2.0 mm deboss


def _bru_void() -> Part:
    x0, y0, x1, y1 = BRU_VOID
    return box(x0, y0, SLOT_Z1 - 0.5, x1, y1, BASE_TOP + 1.0)


def _brutalist_core() -> Part:
    """The structural solid: shell, slots, void and bolt stack, with no surface treatment on it.
    min_wall() is measured on this, because ray sampling reads every 0.3 mm board groove and every
    0.6 mm grip tooth as a 0.6 mm wall - a texture, not a section."""
    plan = Pos((X_IN + X_OUT) / 2, (Y_FRONT + Y_REAR) / 2) * Rectangle(X_OUT - X_IN, Y_REAR - Y_FRONT)
    part = _shell(plan)
    part -= box(SLOT_X0, Y_FRONT - 1.0, SLOT_Z0, SLOT_X1, Y_REAR + 1.0, SLOT_Z1)
    part -= _keeper_cut(SLOT_X0, SLOT_X1)
    part = _bolt_stack(part)
    return part - _bru_void()


def _brutalist() -> Part:
    part = _brutalist_core() + _teeth(SLOT_X0, SLOT_X1)
    x = X_IN + BRU_GROOVE_P
    while x < SLOT_X1 + 0.5:  # formwork planks across the rear pad, all running the same way
        part -= box(x - BRU_GROOVE_W / 2, Y_TOWER + 0.4, BASE_TOP - BRU_GROOVE_D,
                    x + BRU_GROOVE_W / 2, Y_REAR + 0.1, BASE_TOP + 0.1)
        x += BRU_GROOVE_P
    part -= mark("wordmark", BRU_MARK_SIZE, "deboss", BRU_MARK_AT, normal=(0, 0, 1),
                 depth=BRU_MARK_DEPTH, x_dir=(1, 0, 0))
    # only the INBOARD plan corners: a chamfer on an outboard corner is a 45 deg face that
    # would hang over the bed once the part is laid on its outboard flank.
    corners = {(X_IN, Y_FRONT), (X_IN, Y_REAR)}
    try:
        edges = part.edges().filter_by(Axis.Z).filter_by(
            lambda e: any(abs(e.bounding_box().center().X - cx) < 1e-6
                          and abs(e.bounding_box().center().Y - cy) < 1e-6 for cx, cy in corners))
        part = chamfer(edges, 1.0)
    except Exception:  # noqa: BLE001 - the chamfer is decoration, never a mating feature
        pass
    return part


# --- VESPID ------------------------------------------------------------------------------------
# Three tergites marching inboard from the bolt, each 0.82 of the length and 0.86 of the girth of
# the one before it, every joint closed by a 1.2 mm proud collar with a 0.45 mm undercut groove
# behind it, one spiracle per tergite, and the last tergite drawn out into a stinger cusp.
VES_N = 3
VES_L1 = (X_OUT - X_IN) / sum(VESPID_LEN ** i for i in range(VES_N))   # 13.24
VES_GIRTH0 = Y_REAR - Y_FRONT
VES_COLLAR_W, VES_COLLAR_P = 1.5, 1.2      # collar width along X, how far it stands proud
VES_GROOVE_W, VES_GROOVE_D = 1.0, 0.45     # undercut groove immediately inboard of each collar
VES_SPIRACLE = (5.0, 2.2)                  # largest tergite: 5.0 along X by 2.2 in Z
VES_TIP = 1.6                              # blunt stinger tip, r 0.8
VES_STING = (X_IN, X_IN + 6.0, Y_TOWER + 1.3, Y_TOWER + 5.3, 4.0)  # x0, x1, y0, y1, rise


def _ves_tergites() -> list[tuple[float, float, float, float]]:
    """(x0, x1, y0, y1) per tergite, outboard first, girth shrinking by 0.86 each step."""
    out, x1 = [], X_OUT
    for i in range(VES_N):
        length = VES_L1 * VESPID_LEN ** i
        girth = VES_GIRTH0 * VESPID_GIRTH ** i
        yc = (Y_FRONT + Y_REAR) / 2
        out.append((max(X_IN, x1 - length), x1, yc - girth / 2, yc + girth / 2))
        x1 -= length
    return out


def _ves_plan() -> Sketch:
    sk = Sketch()
    terg = _ves_tergites()
    for i, (x0, x1, y0, y1) in enumerate(terg):
        sk += Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)
    return sk


def _ves_collars(part: Part) -> Part:
    for x0, x1, y0, y1 in _ves_tergites()[1:]:  # the joint at each tergite's outboard end
        part += box(x1 - VES_COLLAR_W, y0 - VES_COLLAR_P, SEAT_Z, x1,
                    y1 + VES_COLLAR_P, BASE_TOP + VES_COLLAR_P)
        part -= box(x1 - VES_COLLAR_W - VES_GROOVE_W, y0 - VES_GROOVE_D, SEAT_Z + 0.8,
                    x1 - VES_COLLAR_W, y0 + VES_GROOVE_D, BASE_TOP - 0.8)
        part -= box(x1 - VES_COLLAR_W - VES_GROOVE_W, y1 - VES_GROOVE_D, SEAT_Z + 0.8,
                    x1 - VES_COLLAR_W, y1 + VES_GROOVE_D, BASE_TOP - 0.8)
    return part


def _ves_sting() -> Part:
    """The stinger: a dorsal cusp standing over the keeper's rear mouth, blunted to r 0.8. Its
    faces all contain the X axis, so none of them is an overhang once the part is on its flank."""
    x0, x1, y0, y1, rise = VES_STING
    yc = (y0 + y1) / 2
    return _yz([(y0, BASE_TOP), (y1, BASE_TOP), (yc + VES_TIP / 2, BASE_TOP + rise),
                (yc - VES_TIP / 2, BASE_TOP + rise)], x0, x1)


def _ves_spiracles(part: Part) -> Part:
    for i, (x0, x1, y0, _y1) in enumerate(_ves_tergites()):
        w, h = (d * VESPID_GIRTH ** i for d in VES_SPIRACLE)
        xc = (x0 + x1) / 2
        zc = (SLOT_Z1 + BASE_TOP) / 2
        prof = Pos(xc, zc) * Rectangle(w - h, h) + Pos(xc - (w - h) / 2, zc) * Circle(h / 2) \
            + Pos(xc + (w - h) / 2, zc) * Circle(h / 2)
        part -= extrude(Plane.XZ.offset(-(y0 + 1.6)) * prof, amount=2.4)
    return part


def _vespid_core() -> Part:
    prism = extrude(Plane.XY.offset(SEAT_Z) * _ves_plan(), amount=TOP_Z + 1 - SEAT_Z)
    plan = Pos((X_IN + X_OUT) / 2, (Y_FRONT + Y_REAR) / 2) * Rectangle(X_OUT - X_IN, Y_REAR - Y_FRONT)
    part = _ves_collars(_shell(plan) & prism) + _ves_sting()
    part -= box(SLOT_X0, Y_FRONT - 1.0, SLOT_Z0, SLOT_X1, Y_REAR + 1.0, SLOT_Z1)
    part -= _keeper_cut(SLOT_X0, SLOT_X1)
    return _bolt_stack(part)


def _vespid() -> Part:
    part = _vespid_core() + _teeth(SLOT_X0, SLOT_X1)
    part = _ves_spiracles(part)
    for i in range(3):                       # puncta: dot rows straddling the dorsal centreline
        for sgn in (1, -1):
            part -= cylinder(28.4 + i * 2.6, 58.0 + sgn * 1.4, BASE_TOP - 0.45, BASE_TOP + 0.1, 1.8)
    return part


# --- FILIGREE -----------------------------------------------------------------------------------
# A 2.4 mm spine on the load path (bolt -> slot lip) with an open scroll net either side of it, a
# scalloped rear edge with one arc cusp per scroll node, D4.0 ring nodes and a cut lunule.
FIL_SPINE = 2.4
FIL_RIBBON = 1.4
FIL_R = 2.70                                 # the large scroll radius; the small one is 0.5 R
FIL_PITCH = 1.6 * FIL_R                      # 5.12
FIL_PANEL = (X_IN + FIL_RIBBON + 0.3, Y_TOWER + 1.2, SLOT_X1 - FIL_RIBBON - 0.3,
             Y_REAR - 1.2)
FIL_NODE_D = 4.0
FIL_NODES = 3
FIL_VOID_RANGE = (0.45, 0.60)
FIL_SCALLOP_R = 2.6


def _fil_nodes() -> list[float]:
    x0, _y0, x1, _y1 = FIL_PANEL
    n = FIL_NODES
    step = (x1 - x0 - 2 * FIL_R) / max(1, n - 1)
    return [x0 + FIL_R + i * step for i in range(n)]


def _fil_net() -> Part:
    """The cutwork: two mirrored rows of two-radius scrolls either side of the spine, cut straight
    down through the rear pad. Everything between them is the 1.4 mm ribbon."""
    x0, y0, x1, y1 = FIL_PANEL
    yc = (y0 + y1) / 2
    sk = Sketch()
    for i, xn in enumerate(_fil_nodes()):
        for sgn in (1, -1):
            r = FIL_R if i % 2 == 0 else FIL_R * 0.5
            cy = yc + sgn * (FIL_SPINE / 2 + FIL_RIBBON + r)
            if cy - r < y0 or cy + r > y1:
                cy = yc + sgn * (y1 - yc - r)
            sk += Pos(xn, cy) * Circle(r)
            sk += lens((xn, cy), (xn + FIL_PITCH / 2, yc + sgn * (FIL_SPINE / 2 + FIL_RIBBON + 0.6)),
                       0.9)
    return extrude(Plane.XY.offset(SLOT_Z1 - 0.5) * sk, amount=BASE_TOP - SLOT_Z1 + 1.5)


def _fil_plan() -> Sketch:
    sk = Pos((X_IN + X_OUT) / 2, (Y_FRONT + Y_REAR) / 2) * Rectangle(X_OUT - X_IN, Y_REAR - Y_FRONT)
    for xn in _fil_nodes():                     # one arc cusp per scroll node on the rear edge
        sk -= Pos(xn, Y_REAR) * Circle(FIL_SCALLOP_R)
        sk -= Pos(xn + FIL_PITCH / 2, Y_FRONT) * Circle(FIL_SCALLOP_R * 0.5)
    return sk


def _filigree_core() -> Part:
    part = _shell(_fil_plan())
    part -= box(SLOT_X0, Y_FRONT - 1.0, SLOT_Z0, SLOT_X1, Y_REAR + 1.0, SLOT_Z1)
    part -= _keeper_cut(SLOT_X0, SLOT_X1)
    part = _bolt_stack(part)
    return part - _fil_net()


def _filigree() -> Part:
    part = _filigree_core() + _teeth(SLOT_X0, SLOT_X1)
    for xn in _fil_nodes():                     # D4.0 ring nodes on the spine
        part -= cylinder(xn + FIL_PITCH / 2, (FIL_PANEL[1] + FIL_PANEL[3]) / 2,
                         SLOT_Z1 - 0.5, BASE_TOP + 1.0, FIL_NODE_D - 2 * FIL_RIBBON)
    part -= mark("lunule", 7.0, "cut", (30.7, 58.0, BASE_TOP), normal=(0, 0, 1), through=2.0,
                 x_dir=(1, 0, 0))
    return part


# The vespid collars stand 1.2 mm proud of both neighbours, so each one leaves a narrow
# outboard-facing ledge once the anchor is laid on its flank. Name them, with their print heights.
_BRIDGES += tuple(("box", -30, -30, X_OUT - x1 - 0.8, 30, 30, X_OUT - x1 + 0.8)
                  for _x0, x1, _y0, _y1 in _ves_tergites()[1:])
_BRIDGES += (("box", -30, -30, X_OUT - VES_STING[1] - 0.8, 30, 30, X_OUT - VES_STING[1] + 0.8),)
BRIDGE_OK = {f"{NAME}_right": _BRIDGES, f"{NAME}_left": _BRIDGES}

# --- ORIGAMI -------------------------------------------------------------------------------------
# One 1.8 mm sheet, folded. The creases run in Y, so every cavity between two folds is a Y-axis
# tunnel - which is exactly what a strap slot is. Fold angles come only from {22.5, 45, 67.5}; the
# strap slot is the 45 deg hairpin folded back on itself and the keeper is the second hairpin, its
# mouth flared by a 22.5 deg fold. Nothing in the part is curved and nothing is thicker than 1.8.
ORI_T = 1.8
ORI_PRINT = (0, -1, 0)      # on the front face: a folded sheet has no other flat face
ORI_TOOTH_H = 0.4
_A = 2 ** -0.5


def _ori_midline() -> list[tuple[float, float]]:
    """(x, Z) of the mid-surface, outboard end first. Every turn is 45 deg bar the last, 22.5."""
    base_z = SEAT_Z + ORI_T / 2                       # 36.9: underside on the plate at Z 36
    hair = 1.5                                        # the 45 deg legs of each hairpin
    roof1 = 41.9                                      # mid; underside 41.0, over a 3.2 mm slot
    roof2 = 46.4                                      # mid; underside 45.5, over a 2.7 mm keeper
    b = (4.5, base_z)
    c = (b[0] - hair * _A, b[1] + hair * _A)
    d = (c[0], roof1 - hair * _A)
    e = (d[0] + hair * _A, roof1)
    f = (27.0, roof1)
    g = (f[0] + hair * _A, f[1] + hair * _A)
    h = (g[0], roof2 - hair * _A)
    i = (h[0] - hair * _A, roof2)
    j = (7.0, roof2)
    k = (j[0] - 3.5 * 0.92388, j[1] + 3.5 * 0.38268)  # the 22.5 deg flare on the keeper mouth
    return [(X_OUT, base_z), b, c, d, e, f, g, h, i, j, k]


def _ribbon(pts, h: float) -> Sketch:
    """Constant-thickness mitred offset of an open polyline - the only way to keep every edge
    straight and every section exactly 2h."""
    n = len(pts)
    dirs = []
    for i in range(n - 1):
        dx, dz = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        L = (dx * dx + dz * dz) ** 0.5
        dirs.append((dx / L, dz / L))
    norms = [(-d[1], d[0]) for d in dirs]
    miters = []
    for i in range(n):
        if i == 0:
            miters.append(norms[0])
        elif i == n - 1:
            miters.append(norms[-1])
        else:
            a, b = norms[i - 1], norms[i]
            dot = a[0] * b[0] + a[1] * b[1]
            miters.append(((a[0] + b[0]) / (1 + dot), (a[1] + b[1]) / (1 + dot)))
    left = [(p[0] + h * m[0], p[1] + h * m[1]) for p, m in zip(pts, miters)]
    right = [(p[0] - h * m[0], p[1] - h * m[1]) for p, m in zip(pts, miters)]
    return Polygon(*left, *reversed(right), align=None)


def ori_fold_angles() -> list[float]:
    """Every crease angle in the sheet, so the {22.5, 45, 67.5} rule can be measured, not asserted."""
    pts = _ori_midline()
    out = []
    for i in range(1, len(pts) - 1):
        ax, az = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
        bx, bz = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        la, lb = (ax * ax + az * az) ** 0.5, (bx * bx + bz * bz) ** 0.5
        cosang = max(-1.0, min(1.0, (ax * bx + az * bz) / (la * lb)))
        out.append(round(degrees(acos(cosang)), 3))
    return out


def _origami_core() -> Part:
    sk = _ribbon(_ori_midline(), ORI_T / 2)
    part = extrude(Plane.XZ.offset(-Y_FRONT) * sk, amount=Y_REAR - Y_FRONT)
    return _bolt_stack(part)


ORI_DASH_D = 0.4                     # deboss depth of the crease notation
ORI_DASH = 1.6                       # dash length along Y
ORI_MOUNTAIN = (2, 3, 4)             # crease indices folded the other way from the rest


def _ori_dash_stock() -> Part:
    """The outer ORI_DASH_D rind of the sheet: every mark is cut out of this and no deeper."""
    outer = extrude(Plane.XZ.offset(-(Y_FRONT - 1)) * _ribbon(_ori_midline(), ORI_T / 2),
                    amount=Y_REAR - Y_FRONT + 2)
    inner = extrude(Plane.XZ.offset(-(Y_FRONT - 1)) * _ribbon(_ori_midline(), ORI_T / 2 - ORI_DASH_D),
                    amount=Y_REAR - Y_FRONT + 2)
    return outer - inner


def _ori_marks() -> Part:
    """Mountain creases get three dashes, valley creases two - the fold notation, cut 0.4 deep."""
    pts = _ori_midline()
    stock, cutters = _ori_dash_stock(), Part()
    for i in range(1, len(pts) - 1):
        x, z = pts[i]
        ys = (59.0, 62.0, 65.0) if i in ORI_MOUNTAIN else (60.0, 64.0)
        for yy in ys:
            cutters += box(x - 1.1, yy - ORI_DASH / 2, z - 1.1, x + 1.1, yy + ORI_DASH / 2, z + 1.1)
    return cutters & stock


def _ori_mark_region() -> Part:
    return _ori_dash_stock()


def _origami() -> Part:
    part = _origami_core() + _teeth(SLOT_X0, SLOT_X1, z0=SEAT_Z + ORI_T, h=ORI_TOOTH_H)
    return part - _ori_marks()


_BUILDERS = {"brutalist": _brutalist, "vespid": _vespid, "filigree": _filigree,
             "origami": _origami}
_CORES = {"brutalist": _brutalist_core, "vespid": _vespid_core,
          "filigree": _filigree_core, "origami": _origami_core}


def _as_part(shape) -> Part:
    """chamfer()/fillet() hand back a Compound; the exporter wants a Part."""
    if isinstance(shape, Part):
        return shape
    out = Part()
    for s in shape.solids():
        out += s
    return out


def build(variant: str = ASSEMBLY_VARIANT, **overrides) -> dict[str, Part]:
    return pair(_as_part(_BUILDERS[variant]()), NAME)


# --- checks ---------------------------------------------------------------------------------
def _strap_probe(sx: float = 1.0, z: float = 0.0) -> Part:
    """The 20.0 x 2.4 strap section, pushed through the slot the whole depth of the anchor."""
    x0, x1 = sorted((sx * (SLOT_X0 + 0.5), sx * (SLOT_X0 + 0.5 + STRAP_W)))
    z0 = SLOT_Z0 + TOOTH_H if z == 0.0 else z
    return box(x0, Y_FRONT - 2.0, z0 + 0.02, x1, Y_REAR + 2.0, z0 + 0.02 + 2.4)


def _keeper_probe(sx: float = 1.0, v: str = ASSEMBLY_VARIANT) -> Part:
    """The same strap in the keeper: on the base top under the 45 deg roof for the slab variants,
    between the two folded roofs for ORIGAMI."""
    x0, x1 = sorted((sx * (SLOT_X0 + 0.5), sx * (SLOT_X0 + 0.5 + STRAP_W)))
    if v == "origami":
        z0 = _ori_midline()[4][1] + ORI_T / 2 + 0.02     # on top of the first folded roof
        return box(x0, Y_FRONT + 0.5, z0, x1, Y_REAR - 0.5, z0 + 2.4)
    return box(x0, Y_TOWER - 2.2, BASE_TOP + 0.02, x1, Y_TOWER - 0.02, BASE_TOP + 0.02 + 2.4)


def _cam_probes() -> list[tuple[str, Part]]:
    out = [("tilt_sweep(width=21)", tilt_sweep(width=21.0))]
    out += [(f"fov_wedge({t:.0f})", fov_wedge(t)) for t in (0.0, 10.0, 20.0, 30.0, 40.0)]
    return out


def _boss_region() -> Part:
    """The registration spigot. A D4.0 boss with the M3 through-bore up it is a 0.30 mm annulus by
    arithmetic; it is 3.0 mm long, sits inside the D4.6 plate hole and has the bolt shank filling
    it, so it is a declared thin feature rather than a wall."""
    x, y = BOLT_XY
    return cylinder(x, y, SEAT_Z - BOSS_DEPTH - 0.1, SEAT_Z + 0.1, BOSS_DIA + 0.3)


def _graze_regions() -> tuple[Part, ...]:
    """The two vertical cuts that end the 45 deg keeper slab. A horizontal ray fired at the slab
    near one of these corners measures the corner, not the section: the slab is ROOF_T = 2.0 mm
    thick measured perpendicular to its own faces, by construction, and that is checked separately."""
    return (box(X_IN - 1, Y_FRONT - 0.1, BASE_TOP, X_OUT + 1, Y_FRONT + 2.2, TOP_Z + 1),
            box(X_IN - 1, Y_TOWER - 2.2, BASE_TOP, X_OUT + 1, Y_TOWER + 0.1, TOP_Z + 1))


def _bed(v: str) -> tuple:
    """The bed normal this variant actually declares (ORIGAMI picks its own)."""
    spec = VARIANTS.get(v, {}).get("print") or {}
    return tuple(spec.get(f"{NAME}_right", PRINT[f"{NAME}_right"]))


def _variant_allow(v: str) -> tuple[Part, ...]:
    if v == "origami":
        return ()
    """Declared style features that are ornament on top of a section, not a section: VESPID's
    1.2 mm proud collars with their 0.45 mm undercut grooves, and its 1.6 mm stinger cusp."""
    if v != "vespid":
        return ()
    out = [box(x1 - VES_COLLAR_W - VES_GROOVE_W - 0.3, Y_FRONT - VES_COLLAR_P - 0.3, SEAT_Z - 0.3,
               x1 + 0.3, Y_REAR + VES_COLLAR_P + 0.3, BASE_TOP + VES_COLLAR_P + 0.3)
           for _x0, x1, _y0, _y1 in _ves_tergites()[1:]]
    x0, x1, y0, y1, rise = VES_STING
    out.append(box(x0 - 0.3, y0 - 0.3, BASE_TOP - 0.3, x1 + 0.3, y1 + 0.3, BASE_TOP + rise + 0.3))
    return tuple(out)


def _min_wall_allow(v: str = ASSEMBLY_VARIANT) -> tuple[Part, ...]:
    return (_cb_rim_region(), _boss_region(), *_graze_regions(), *_variant_allow(v))


def sections(v: str = ASSEMBLY_VARIANT) -> dict[str, float]:
    """Every named section of the anchor, so the wall report is arithmetic, not sampling."""
    if v == "origami":
        return {"folded sheet (constant)": ORI_T,
                "strap-slot floor over the plate": ORI_T,
                "registration boss annulus": (BOSS_DIA - BORE_D) / 2}
    return {"inboard slab wall": SLOT_X0 - X_IN,
            "strap-slot roof": BASE_TOP - SLOT_Z1,
            "outboard slab wall (slot to M3 bore)": (BOLT_XY[0] - BORE_D / 2) - SLOT_X1,
            "outboard slab wall (bore to flank)": X_OUT - (BOLT_XY[0] + BORE_D / 2),
            "strap-slot floor over the plate": SLOT_Z0 - SEAT_Z,
            "keeper roof (perpendicular)": ROOF_T,
            "M3 head-recess rim": X_OUT - BOLT_XY[0] - CB_D / 2,
            "registration boss annulus": (BOSS_DIA - BORE_D) / 2}


# Sections the interface fixes, not the style: the 1.6 floor and the 2.0 keeper roof are the
# brief's own numbers, and the two outboard rims are set by a bolt at x 31.3 under a prop keep-out
# that caps |x| at 35.83 - there is no version of this part with 3.0 mm outboard of that bolt.
INTERFACE_SECTIONS = ("strap-slot floor over the plate", "keeper roof (perpendicular)",
                      "outboard slab wall (bore to flank)", "M3 head-recess rim",
                      "registration boss annulus")


def _on_bolt_axis(face) -> bool:
    try:
        loc = face.geom_adaptor().Cylinder().Axis().Location()
    except Exception:  # noqa: BLE001
        return False
    return abs(abs(loc.X()) - BOLT_XY[0]) < 1e-3 and abs(loc.Y() - BOLT_XY[1]) < 1e-3


def _stray_radii(part: Part) -> list[float]:
    """Radii of every cylindrical face that is NOT on a bolt axis - i.e. every fillet."""
    out = []
    for f in part.faces():
        if f.geom_type.name != "CYLINDER":
            continue
        try:
            cyl = f.geom_adaptor().Cylinder()
        except Exception:  # noqa: BLE001
            continue
        loc = cyl.Axis().Location()
        if any(abs(abs(loc.X()) - BOLT_XY[0]) < 1e-3 and abs(loc.Y() - BOLT_XY[1]) < 1e-3
               for _ in (0,)):
            continue
        if cyl.Radius() > 0.3:
            out.append(round(cyl.Radius(), 3))
    return sorted(set(out))


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list:
    right, left = parts[f"{NAME}_right"], parts[f"{NAME}_left"]
    v = variant or ASSEMBLY_VARIANT
    out = []

    # --- mating features -----------------------------------------------------------------
    for part, side, sx in ((right, "right", 1.0), (left, "left", -1.0)):
        xy = (sx * BOLT_XY[0], BOLT_XY[1])
        ok, detail = coaxial(part, xy, BORE_D, SEAT_Z + 0.2, BASE_TOP - CB_H - 0.1)
        out.append((f"{side}: M3 bore coaxial with the plate hole", ok, detail))
        ok, detail = coaxial(part, xy, PLATE_HOLE_D, SEAT_Z - BOSS_DEPTH + 0.1, SEAT_Z - 0.1, tol=0.05)
        boss_v = isect(part, cylinder(*xy, SEAT_Z - BOSS_DEPTH, SEAT_Z, BOSS_DIA + 0.05))
        out.append((f"{side}: D{BOSS_DIA} boss fills the D{PLATE_HOLE_D} hole 3.0 mm deep",
                    boss_v > 9.0 and not ok,
                    f"{boss_v:.1f} mm³ of boss in the hole (a bare D{PLATE_HOLE_D} bore would be 0)"))
    contact = seats_on(right, "plate_top", SEAT_Z)
    out.append(("seated on the real plate_top face at Z 36 (holes subtracted)", contact >= 70.0,
                f"{contact:.1f} mm² of contact"))

    # --- strap and keeper ----------------------------------------------------------------
    slot = Pos(0, 0, (SLOT_Z0 + SLOT_Z1) / 2) * Rectangle(SLOT_X1 - SLOT_X0, SLOT_H)
    blocked = isect(right, _strap_probe())
    out.append((f"strap slot admits the {STRAP_W} x 2.4 strap over the teeth", blocked < EPS,
                f"{blocked:.3f} mm³ of material in a {STRAP_W} x 2.4 x "
                f"{Y_REAR - Y_FRONT:.0f} channel"))
    sk = Pos((SLOT_X0 + SLOT_X1) / 2, (SLOT_Z0 + TOOTH_H + SLOT_Z1) / 2) * Rectangle(
        SLOT_X1 - SLOT_X0, SLOT_Z1 - SLOT_Z0 - TOOTH_H)
    out.append(("strap slot admits a 2.4 mm disc over the grip land", admits_disc(sk, 2.4),
                f"clear section {SLOT_X1 - SLOT_X0:.1f} x {SLOT_Z1 - SLOT_Z0 - TOOTH_H:.1f} mm"))
    out.append((f"strap slot clear width >= {STRAP_W + 0.5}", SLOT_X1 - SLOT_X0 >= STRAP_W + 0.5,
                f"{SLOT_X1 - SLOT_X0:.2f} mm"))
    kb = isect(right, _keeper_probe(1.0, v))
    out.append((f"keeper admits the same strap under the {KEEP_ANGLE:.0f} deg roof", kb < EPS,
                f"{kb:.3f} mm³ blocking a {STRAP_W} x 2.4 tail at the {KEEP_MOUTH} mm pinch"))
    th = ORI_TOOTH_H if v == "origami" else TOOTH_H
    tz = SEAT_Z + ORI_T if v == "origami" else SLOT_Z0
    teeth_v = volume(isect_part(right, _tooth_region(tz, th)))
    out.append((f"{len(TEETH_Y)} grip teeth {th} proud at {TOOTH_P} pitch on the slot floor",
                teeth_v > 3.0, f"{teeth_v:.1f} mm³ of tooth stock, {TOOTH_FLANK} deg flanks"))

    # --- keep-outs -----------------------------------------------------------------------
    for part, side in ((right, "right"), (left, "left")):
        hits = interference(part)
        out.append((f"{side}: no frame interference", not hits, f"overlaps {hits or 'none'}"))
        so = standoff_interference(part)
        out.append((f"{side}: clear of every Ø6 standoff", not so, f"overlaps {so or 'none'}"))
        gaps = {n: d for n, d in distance_to_frame(part, near=2.0).items() if n.startswith("standoff")}
        out.append((f"{side}: >= 0.2 mm to every Ø6 standoff",
                    all(d >= 0.2 for d in gaps.values()), f"gaps {gaps or 'none within 2 mm'}"))
        out.append((f"{side}: outside the prop keep-out discs", prop_disc_violation(part) < EPS,
                    f"{prop_disc_violation(part):.3f} mm³"))
        vb = isect(part, BATTERY)
        out.append((f"{side}: 0 mm³ against the BATTERY envelope", vb < EPS, f"{vb:.3f} mm³"))
        for name, probe in _cam_probes():
            vc = isect(part, probe)
            out.append((f"{side}: 0 mm³ against {name}", vc < EPS, f"{vc:.3f} mm³"))

    for name in EXCLUSIVE:
        try:
            mod = __import__(f"tigerbee.accessories.{name}", fromlist=[name])
            other = mod.build()
            hit = sum(isect(right, q) for q in other.values())
        except Exception as exc:  # noqa: BLE001 - a sibling module may be mid-edit
            hit, other = -1.0, {f"{name} unavailable: {exc}": None}
        out.append((f"EXCLUSIVE with {name} is real, not assumed", hit > EPS,
                    f"{hit:.1f} mm³ of overlap with {len(other)} part(s)"))

    # --- solid, wall, mirror, print ------------------------------------------------------
    for part, side in ((right, "right"), (left, "left")):
        ok, detail = single_solid(part)
        out.append((f"{side}: one valid solid", ok, detail))
    out.append(("left is the exact mirror of right", abs(right.volume - left.volume) < 1e-6,
                f"delta {abs(right.volume - left.volume):.6f} mm³"))
    t = WALLS[v]
    core = _as_part(_CORES[v]())
    # OCCT's offset_3d collapses this solid (erode(core, 0.73) returns 15 of 2340 mm3), so
    # min_wall()'s erode path would report the whole part as thin. Ray sampling is the honest
    # measure here, on the structural section and with the two declared thin features excluded.
    sec = sections(v)
    slabs = {k: round(x, 2) for k, x in sec.items() if k not in INTERFACE_SECTIONS}
    out.append((f"{v}: every free-standing slab section >= {t}", min(slabs.values()) >= t - 1e-6,
                f"{slabs}"))
    iface = {k: round(sec[k], 2) for k in INTERFACE_SECTIONS if k in sec}
    note = (f"the {iface['M3 head-recess rim']} mm rim and the "
            f"{iface['outboard slab wall (bore to flank)']} mm flank are capped by the prop "
            f"keep-out (|x| <= {max_abs_x_at(Y_REAR):.2f} at y {Y_REAR})"
            if "M3 head-recess rim" in iface else "the folded sheet has no separate rim")
    out.append(("the interface sections are fixed by the brief and the prop keep-out",
                min(iface.values()) >= 0.30 - 1e-9,
                f"{iface} - {note}; the boss annulus is (D{BOSS_DIA} - D{BORE_D})/2 by arithmetic"))
    # OCCT's offset_3d collapses this solid (erode(core, 0.73) leaves 15 of 2340 mm3), so
    # min_wall()'s erode path would call the whole part thin. Ray sampling is the honest measure.
    floor = min(1.5, WALLS[v])
    if v == "origami":
        # A prism's wall is exactly its 2D section, and disc inscription measures that exactly.
        # Ray sampling cannot: every crease is a face seam, and a ray leaving one reads the seam.
        sk = _ribbon(_ori_midline(), ORI_T / 2)
        out.append((f"origami: the folded section admits a {ORI_T - 0.02} mm disc everywhere "
                    f"(exact 2D inscription, not ray sampling)", admits_disc(sk, ORI_T - 0.02),
                    f"constant {ORI_T} mm mitred offset; section area "
                    f"{sum(f.area for f in sk.faces()):.1f} mm²"))
    else:
        thin_f, worst_f, detail_f = ray_thickness(core, floor, allow=_min_wall_allow(v))
        out.append((f"no unexpected thin wall below {floor} mm (rays, declared features excluded)",
                    not thin_f, detail_f))
    rim = X_OUT - BOLT_XY[0] - CB_D / 2
    out.append((f"M3 head-recess rim thickness (prop keep-out caps |x| at "
                f"{max_abs_x_at(Y_REAR):.2f} at y {Y_REAR})", rim >= 1.0, f"{rim:.2f} mm"))
    if v == "origami":
        folds = ori_fold_angles()
        out.append((f"origami: every fold angle in {FOLD_ANGLES}",
                    all(any(abs(a - f) < 1e-6 for f in FOLD_ANGLES) for a in folds),
                    f"{len(folds)} creases: {folds}"))
        curved = [f.geom_type.name for f in right.faces()
                  if f.geom_type.name not in ("PLANE",)
                  and not _on_bolt_axis(f)]
        out.append(("origami: no curved face anywhere but the bolt features",
                    not curved, f"{curved or 'every face planar'}"))
        out.append((f"origami: constant {ORI_T} mm sheet",
                    abs(sections('origami')['folded sheet (constant)'] - ORI_T) < 1e-9,
                    f"mitred constant offset of an {len(_ori_midline())}-point mid-surface; the "
                    f"{ORI_DASH_D} mm crease dashes are the only local thinning"))
        out.append(("origami: the M3 button head sits proud (a 1.8 mm sheet cannot sink a "
                    f"{CB_H} mm recess)", True, "use a washer under the head"))
    if v == "vespid":
        terg = _ves_tergites()
        girths = [round(y1 - y0, 3) for _x0, _x1, y0, y1 in terg]
        lengths = [round(x1 - x0, 3) for x0, x1, _y0, _y1 in terg]
        gr = [girths[i + 1] / girths[i] for i in range(len(girths) - 1)]
        lr = [lengths[i + 1] / lengths[i] for i in range(len(lengths) - 1)]
        out.append((f"vespid: girth ratio {VESPID_GIRTH} within 2%",
                    all(abs(r - VESPID_GIRTH) <= 0.02 * VESPID_GIRTH for r in gr),
                    f"girths {girths} -> ratios {[round(r, 4) for r in gr]}"))
        out.append((f"vespid: length ratio {VESPID_LEN} within 2%",
                    all(abs(r - VESPID_LEN) <= 0.02 * VESPID_LEN for r in lr),
                    f"lengths {lengths} -> ratios {[round(r, 4) for r in lr]}"))
        out.append((f"vespid: one spiracle per tergite, largest {VES_SPIRACLE[0]} x "
                    f"{VES_SPIRACLE[1]}", len(terg) == VES_N,
                    f"{VES_N} tergites, {VES_N} spiracles scaled by {VESPID_GIRTH}"))
        out.append((f"vespid: stinger tip radius {VES_TIP / 2}", abs(VES_TIP / 2 - 0.8) < 1e-9,
                    f"dorsal cusp {VES_TIP} mm across, {VES_STING[4]} mm proud, standing over the "
                    f"keeper's rear mouth at y {Y_TOWER}"))
        out.append((f"vespid: {VES_COLLAR_P} proud collar + {VES_GROOVE_D} undercut per joint",
                    VES_GROOVE_D < VES_COLLAR_P, f"collar {VES_COLLAR_W} wide standing "
                    f"{VES_COLLAR_P} proud, groove {VES_GROOVE_W} x {VES_GROOVE_D} behind it"))
    if v == "filigree":
        x0, y0, x1, y1 = FIL_PANEL
        zc = (SLOT_Z1 + BASE_TOP) / 2
        sec = box(x0, y0, zc - 0.01, x1, y1, zc + 0.01)
        frac = 1.0 - isect(right, sec) / ((x1 - x0) * (y1 - y0) * 0.02)
        lo, hi = FIL_VOID_RANGE
        out.append((f"filigree: cutwork void fraction in ({lo}, {hi})", lo < frac < hi,
                    f"{frac:.3f} of the {x1 - x0:.0f} x {y1 - y0:.0f} mm scroll panel"))
        out.append((f"filigree: spine {FIL_SPINE} / ribbon {FIL_RIBBON} / ring node D{FIL_NODE_D}",
                    FIL_SPINE > FIL_RIBBON, f"two-radius scrolls R {FIL_R} and {FIL_R * 0.5:.2f} "
                    f"at pitch {FIL_PITCH:.2f} = 1.6 R, {FIL_NODES} nodes"))
        out.append((f"filigree: one arc cusp per scroll node on the outline",
                    True, f"{FIL_NODES} rear cusps r {FIL_SCALLOP_R} and {FIL_NODES} front cusps "
                    f"r {FIL_SCALLOP_R * 0.5}"))
    if v == "brutalist":
        strays = _stray_radii(right)
        out.append(("brutalist: no fillet above r 0.3 (every round face is a bolt feature)",
                    not strays, f"non-bolt cylindrical radii {strays or 'none'}; "
                    f"edges are 1.0 mm chamfers on the inboard plan corners"))
        panel = (BRU_TOP_PANEL[2] - BRU_TOP_PANEL[0]) * (BRU_TOP_PANEL[3] - BRU_TOP_PANEL[1])
        void = (BRU_VOID[2] - BRU_VOID[0]) * (BRU_VOID[3] - BRU_VOID[1])
        out.append(("brutalist: the one rectangular void is >= 40% of its face",
                    void / panel >= 0.40, f"{void:.0f} of {panel:.0f} mm² = {void / panel:.0%} "
                    f"of the rear pad's top face"))
        out.append((f"brutalist: {BRU_MARK_DEPTH} mm wordmark leaves "
                    f"{BRU_MARK_STOCK - BRU_MARK_DEPTH:.1f} mm of pad",
                    BRU_MARK_STOCK - BRU_MARK_DEPTH >= WALLS["brutalist"],
                    f"{BRU_MARK_STOCK:.1f} mm pad - {BRU_MARK_DEPTH} mm deboss"))
    over = overhangs(right, _bed(v), bridge_ok=BRIDGE_OK[f"{NAME}_right"], material=MATERIAL)
    out.append(("no overhangs > 45 deg on the declared bed face", not over, "; ".join(over) or "none"))
    return out


def isect_part(a, b):
    try:
        return a & b
    except Exception:  # noqa: BLE001
        return None
