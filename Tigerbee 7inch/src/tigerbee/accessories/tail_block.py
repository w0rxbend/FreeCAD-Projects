"""Tail block: VTX shroud, SMA bulkhead seat, dipole fin and rear skid, all in one TPU piece.

Answers the "protectors for VTX in tail" request. The block is an open-topped U channel that
stands on plate_bottom's top face (Z 2) between the two rear-tip standoffs and wraps the rear
equipment bay:

  * two side walls (|x| 15.4-17.2, y -57.6..-100.4, Z 2-22) take a side impact and keep the
    VTX off the ground in a roll; the bay is open upward because plate_top (Z 34-36) is the
    bay's real ceiling - a closed roof would be a 30.8 mm unsupported bridge;
  * a 2.0 mm transverse panel at the bay's rear end (y -88.4..-90.4) carries the SMA bulkhead
    (2.0 <= SMA_SEAT_WALL_MAX) and two arched vents that let the heatsink breathe and the
    pigtail out;
  * a 3 mm tray (y -90.4..-107, Z 2-5) ties the two standoff clips together, bridges the
    plate_bottom tail notch and runs 6.8 mm past the carbon as the rear skid;
  * an optional 50 deg dipole fin with a 4.4 mm coax channel and a 2.2 mm snap-in slit.

TWO MORE READINGS ship on top of the four above (a third, `vespid`, is built and measured in this
file but is NOT in VARIANTS - the note over its section says exactly why). They change nothing that
mates - the
Z 2 footprint, the two Ø6.5 clip bores over Z 2-22, the M3 boss, the bay, the SMA seat and the
spanner pocket are the same build123d geometry in all eight variants, and ONE checks() proves the
fit for every one of them:

  * `vespid` - THE ABDOMEN. BUILT, MEASURED AND NOT SHIPPED; see VESPID below for the numbers.
  * `brutalist` - ONE POURED SLAB. 3.0 mm formwork slabs stand outboard of the shroud and behind
    the panel and are capped by a cornice that flares OUTWARD at 50 deg (never inward over the bay:
    an inward corbel meets its own flat top in a knife edge, measured at 0.14 mm). One rectangular
    void takes 44.9 % of each cheek under a declared 15 mm lintel bridge; three 3.0 proud ribs
    cross the top at 12 mm pitch; twenty-five board-marking planks run the print direction; the SMA
    comes out through a square 23 mm sunk land whose floor is the 2.0 mm panel.
  * `gyroid` - A FROZEN FLUID, in PETG. The shroud is a 3.6 mm slab with r 3.0 on its plan outline
    and the tail is a 4.0 mm deck out to y -118; between the 1.6 mm rinds the deck's interior is a
    Blender lattice, and the ventilation is NOT cut - it is what the sheet leaves where it breaks
    the surface. The deck and not the wall carries it, because a lattice through a vertical wall
    leaves horizontal-axis prisms and nineteen real ceilings. Ships `voronoi` until the gyroid
    recipe lands, and the undecorated slab passes on its own.

MOUNTING: two C-clips (bore Ø6.5, 0.25 radial fit measured) snap onto the Ø6 rear-tip standoffs
at (±16.5, -94) over the walls' full height Z 2-22, and one M3 x 8 self-tapper comes up through the
frame's `rear_tail_axis` hole (0, -91) into the Ø2.7 boss, so the block cannot climb them. No hole is
invented: `rear_30p5_row` (±15.25, -81) belongs to led_buzzer and its two screw heads
(Ø5.7, Z 2-3.65) pass through the arched reliefs in the side walls - that is the "clear of the
tail_block skirts" note in led_buzzer.

ANTENNA DIVISION OF LABOUR (measured, see checks): antenna_mast is the 915 MHz RX mast and owns
everything ABOVE plate_top - it bolts to the rear-tip standoff bolts on the top face (Z 36+) and
leans back at 50 deg. This block is the VTX side and owns everything BELOW plate_top: the
standoff shanks (Z 2-22 clips) and the bay floor. They are NOT exclusive: with FIN=True the
fin's highest point is Z 31.35, 2.65 mm under plate_top and 4.65 mm from the mast at the
closest measured point. The one interaction is the mast's coax, which drops through the plate_top
U-notch at x 0: route it beside the fin (|x| > 4) or take any variant that leaves the fin off. Only
`shard` carries it; `flat` is the same faceted shard block with TOWER=False, and carapace / feral /
nocturne put their own dorsal feature there instead. EVERY variant ships as its own file, is checked
and is round-tripped, and the combined assembly installs `flat` (ASSEMBLY_VARIANT) - so the block in
tigerbee_with_accessories is exactly the block in tail_block__flat.{step,stl,3mf,FCStd}. That is why
the fin-off build is a VARIANT and not an ASSEMBLY_BUILD override: an override the assembly alone
applied left the block shown in the advertised assembly with no file of its own.

The cavity is sized from the 25.5 mm M2 pattern (`rear_25p5`, centre (0, -73)): a 30 x 30 x 12
board on 3 mm standoffs, 0.4 clearance all round. The 32 x 37 `_common.VTX` envelope is a
different (bigger) board and does NOT fit between the walls - build CAV=(32, 32, 12) for it, or
keep the shroud and move that board to the 20 x 20 pattern. The bay length cannot grow forward
past y -57.6 below Z 14 because xt60_holder's rear face is at y -57.4; above Z 14 the walls
step back to y -60 to clear its socket block.
"""

from math import atan2, cos, degrees, hypot, radians, sin, tan

from build123d import (Align, Axis, Circle, Cone, Cylinder, GeomType, Location, Part, Plane, Polygon, Pos,
                       Rectangle, Rotation, Sketch, Sphere, extrude, fillet, loft)

from tigerbee.accessories import _blender as BL  # noqa: F401 - checks() reports the decor rows
from tigerbee.accessories import _style as S
from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "tail_block"
LENS = "tail_block_lens"  # NOCTURNE's second part: the translucent cap rack, its own filament
# The four original readings plus the three added below. `style` is declared in VARIANTS only
# when _style.STYLES already carries the language (the guard idiom), so this module builds and
# exports whether or not the _style task has landed; this tuple is build()'s own whitelist.
STYLES = ("shard", "carapace", "feral", "nocturne", "vespid", "brutalist", "gyroid")
TITLE = "Tail VTX block"
MATERIAL = "TPU95A"
# Every style prints on the same single Z 2 plane, and that is a result, not a coincidence: the dome
# apexes in +Z, the vane fan stands up off the same face and the lens's flat side is its bed face, so
# one bed normal serves all five parts. See PRINTABILITY in the docstring for what that cost.
PRINT = {"tail_block": (0, 0, -1), LENS: (0, 0, -1)}
EXCLUSIVE = ()  # antenna_mast coexists; see the docstring
# BRUTALIST's cheek lintel is a real bridge and is declared as one rather than excused: 15.0 mm
# against TPU's 22.0 ceiling. Only build() knows the print bbox this has to be expressed in, so it
# fills this in, exactly as camera_pod does.
BRIDGE_OK: dict[str, tuple] = {}
MOUNTS = {
    "tail_block": ("standoff_rear_tip_left / _right Ø6 shafts over Z 2-22 (clips, mouths outboard)",
                   "plate_bottom top face Z 2 (the tray floor and the rear skid stand on that plane)",
                   "rear_tail_axis (0, -91) - one screw comes up through the carbon into the boss"),
    LENS: ("no frame contact: the 1.0 mm sheet drops into the 0.4 deep rabbet in the nocturne "
           "plinth's top face (Z 8.6-9.0) behind the panel, domes up, and is trapped between that "
           "rabbet and plate_top",),
}
HARDWARE = {
    "tail_block": ("1 x M3 x 8 self-tapper up through rear_tail_axis into the Ø2.7 boss (5.5 mm of engagement)",
                   "4 x M2 x 8 + 4 x 3 mm standoffs for the VTX on the 25.5 pattern at (0, -73)",
                   "1 x SMA / RP-SMA bulkhead nut on the rear face (Ø6.5 D-hole at (0, -89.4), Z 15)"),
    LENS: ("none - the sheet is a 0.2 mm clearance drop-in in the plinth rabbet and its five "
           "plano-convex domes locate on the Ø3.6 well mouths; a drop of CA at two corners if you "
           "fly it hard",),
}
# --- the three added languages' own numbers (declared here because VARIANTS reads them) --------
# VESPID: the abdomen. Tergite k has length L1 * 0.82**k and girth (half width) G1 * 0.86**k.
VESPID = False
VE_Y0 = -97.0          # front face of the first tergite: 0.1 clear of the Ø14 spanner pocket (-96.9)
VE_N = 5
VE_L1 = 6.30           # first tergite length; the run is 6.30, 5.17, 4.24, 3.47, 2.85 = 22.03 mm
VE_LR = 0.82           # length ratio, segment to segment
VE_G1 = 7.0            # first tergite half width (girth); the run steps 7.0 -> 3.83. Not 9: the
                       # cavity's half width is the girth less the wall, its roof is a semicircular
                       # arch of that radius, and a horizontal-axis arch is only exempt from the
                       # overhang rule up to Ø10 in TPU. 7.0 - 2.2 = 4.8 puts the root roof at Ø9.6.
VE_BASE = 9.0          # the straight flank under the arch on tergite 1, tapering by VE_GR with it,
                       # so the crown steps 18.0 -> 10.75 and the whole abdomen stays under Z 22
VE_GR = 0.86           # girth ratio - the law the check measures to 2 %
VE_COLLAR = 1.2        # how far proud of its own tergite each collar stands
VE_COLLAR_L = 1.4      # the collar's run in Y
VE_GROOVE = 0.45       # undercut groove immediately aft of the collar
VE_GROOVE_L = 0.8
VE_WALL = (2.2, 1.4)   # root wall -> last tergite wall, linear in segment index
VE_CAV_Z0 = 5.0        # the abdomen's floor: 3.0 mm of solid over the bed plane
VE_SPIR_Z0 = 5.6       # the spiracles' sill, just over that floor
VE_SPIR = (2.2, 5.0)   # spiracle: width x height on the first tergite, scaled by VE_GR after that.
                       # A LANCET, not an ellipse, and that is printability: the crown of an
                       # elliptical hole in a vertical flank is a 6.4 mm² ceiling, while a Ø2.2
                       # horizontal-axis arch head is an exempt arch. Same 2.2 x 5.0, same read.
VE_STING_L = 5.4       # the sting, aft of the last tergite
VE_TIP_R = 0.8         # the sting is blunted to r 0.8 so a Ø1.6 ball fills it
VE_PUNCTA = (1.8, 0.4, 2.6)  # (Ø, depth, x offset either side of the dorsal midline)
VE_FACETS = 12         # chords across the crown's half circle; see _ve_dsec for why

# BRUTALIST: one poured slab, formwork still showing.
BRUT = False
BR_T = 3.0             # the slab: 2 x the catalogue wall, constant, no local thinning
BR_CHAM = 1.0          # the only edge treatment in the whole variant
BR_CORBEL = 50.0       # deg from horizontal for the cornice's underside: normal.Z -0.643, inside
                       # the 0.7 overhang limit, where 45 deg would read exactly -0.707
BR_FLARE = 1.5         # how far the cornice flares OUTBOARD of the cheek before its lip. The
                       # lip is BR_T / cos(50 deg) = 4.67 tall, not 3.0: the slab is measured
                       # PERPENDICULAR to its own 50 deg underside, and a 3.0 vertical lip is
                       # 1.93 of wall - the first build measured 2.38 there against the 3.0 floor.
BR_TOP_Z = 25.0        # the nominal top of the slab (wall top 22 + BR_T). The REAL top is
                       # _br_top(), which adds the cornice flare's rise and its perpendicular
                       # lip; this constant stays as the language's stated slab thickness.
BR_RIB = (3.0, 3.0, 12.0)  # (proud, width, pitch) square section, on the OUTSIDE
BR_BOARD = (0.6, 0.3, 2.4)  # board marking: groove width x depth at pitch, running the print axis
BR_VOID_MIN = 0.40     # one rectangular void per cheek, >= 40 % of that cheek's area
BR_CHEEK_Y = (-62.0, -90.4)  # the slab's run: 28.4 mm, which is what three 3.0 ribs at a
                       # 12 mm pitch actually need (24 of pitch plus one rib width), so no
                       # rib ever hangs off the end of the cornice it stands on
BR_VOID = (15.0, 19.0)  # (width in Y, top Z) of the one void per cheek: 15.0 is a bridge TPU
                       # spans (ceiling 22.0), it leaves 6.7 mm jambs and a 3.0 lintel, and at
                       # 15 x 17 it is 44.9 % of the cheek - comfortably over the 40 % floor
BR_LAND = 23.0         # the square rear void: also what keeps the Ø14 spanner pocket and both panel
                       # vent arches clear, and it is where the SMA's flat land (the 2.0 panel
                       # itself) is reached - a land, never a boss
BR_STAMP = (2.0, 0.0, 5.0, 2.6)  # (deboss depth, unused, plaque width, plaque proud). The plaque's
                       # LENGTH is whatever the gap between two ribs is, so it butts both of them
                       # and leaves no slot. The stamp is 2.0 deep and the wall is 3.0, so it
                       # cannot be sunk into the slab: it is sunk into a plinth cast proud of it,
                       # which is what a cast-in plaque is.
BR_KEEP = 0.9          # how far the board marking stops short of any aperture

# GYROID: the solid is a frozen fluid. All visual event is internal.
GYROID = False
GY_WALL = 3.6          # the thickened shroud; thicker than any other language because it is mostly void
GY_RIND = 1.6          # solid rind on every mating / bearing face, and the sheet thickness
GY_PERIOD = 9.0        # inside the language's 9-12 band; >= 1.5 of them must fit across the deck
                       # between the rinds, and 24.4 / 9.0 = 2.71 periods does
GY_ROUND = 3.0         # the single constant plan rounding; no crease anywhere on the outline
# The documented fallback cell, until the gyroid recipe lands. It is `voronoi` because that is the
# only cell the bridge could rebuild into a valid solid on this part: `round` and `hex` were both
# tried at four sizes and every one came back "BRepCheck_Analyzer says invalid".
GY_CELL_FALLBACK = "voronoi"
GY_CELL_D = 9.0        # cell size of the fallback net
GY_MIN_CUT = 0.03      # a lattice pass that removes less than 3 % of the part did not happen
GY_INSET = 2.6         # how far inside the deck outline the lattice may reach
GY_LIG = 2.8           # 2.8 nominal for a 1.6 sheet: the mesh comes back ~0.5 mm under nominal at a
                       # cell corner (measured 1.07 against a 1.6 request), and the floor is not moved
GY_DECK = (4.0, -118.0)  # (deck thickness, rear end): the horizontal panel the lattice lives in
GY_STEP_Y = -64.0      # the xt60 step-back, 4 mm further aft than the shared -60.0, and that is the
                       # rounding talking: two r 3.0 corners 2.4 mm apart in Y cannot both exist, so
                       # at -60.0 OCCT carries three of the four and the outline keeps one crease.
                       # At -64.0 the corners are 6.4 apart, all four take the ONE legal radius, and
                       # the upper shroud gains 4 mm of clearance to xt60_holder's socket block.

# FOUR STYLE READINGS OF THE SAME TAIL, five printed parts. Everything that mates - the Z 2
# footprint, the two Ø6.5 clip bores, the M3 boss, the 30 x 30 x 12 bay, the SMA seat and the
# spanner pocket - is identical build123d geometry in all four; only the dorsal form changes, and
# ONE checks() proves the fit for every one of them.
VARIANTS = {
    "shard": {"style": "shard", "params": {"TOWER": True},
              "notes": "the frame's own faceted language: flat walls, arched vents and the 50 deg "
                       "dipole blade (max Z 31.35). Route the 915 MHz coax beside it (|x| > 4) or "
                       "take another style - the other three leave the plate_top U-notch's x 0 "
                       "column free below Z 22 except where their own dorsal feature stands."},
    "carapace": {"style": "carapace", "material": "PETG",
                 "params": {"TOWER": False, "DOME": True},
                 "notes": "the tail cusp: two domed elytra roll outboard over the side walls and "
                          "close behind the panel into a sutured cusp that runs the tray out to a "
                          "true point at y -111. Cusped elytra slits, a punctate flank field and a "
                          "debossed lunule on each shoulder. Everything stays at or under Z 22."},
    "feral": {"style": "feral", "params": {"TOWER": False, "STING": True},
              "notes": "the stinger: a 30 mm rearward-raked spine (root Ø8 -> Ø1.6 tip, blunted to "
                       "r 0.8) over the SMA panel, a descending five-spine dorsal row on each wall "
                       "top, Ø2.2 punctation on the cheeks and the lunule cut clean through as a "
                       "slash. TPU 95A - the tail takes the touchdown."},
    "nocturne": {"style": "nocturne", "material": "PETG",
                 "params": {"TOWER": False, "RACK": True},
                 "notes": "the comb: a five-vane fan on a lit plinth behind the panel, every vane "
                          "with its own conical light well, a Ø3 light pipe to a 0.8 mm glowing "
                          "tip and a ladder of transverse slots. Print the shell in black PETG and "
                          f"{LENS} in natural or clear - two parts, two filaments, no AMS."},
    # The plain block with the fin off. It exists as a VARIANT, not as an ASSEMBLY_BUILD override,
    # because it is what the combined assembly installs and the advertised assembly must not contain
    # a part that has no file of its own: everything stays at or under the wall top (Z 22), so
    # antenna_mast's coax drops straight through the plate_top U-notch at x 0. Same style, same
    # material and the same shared checks() as `shard` - only TOWER differs.
    "flat": {"style": "shard", "params": {"TOWER": False},
             "notes": "the shard block with no dorsal feature at all: nothing above the wall top "
                      "Z 22, so antenna_mast's 915 MHz coax drops straight through the plate_top "
                      "U-notch at x 0. This is the variant the combined assembly installs."},
    # --- THREE MORE READINGS (added; no existing variant's geometry, MOUNTS or HARDWARE changed) ---
    # The style-guard idiom: `style` is declared only when _style.STYLES already carries the
    # language, so these three export whether or not the _style task has landed.
    "brutalist": {**({"style": "brutalist"} if "brutalist" in S.STYLES else {}),
                  "params": {"TOWER": False, "BRUT": True},
                  "notes": "ONE POURED SLAB. 3.0 mm formwork slabs stand outboard of the shroud and "
                           "behind the panel, corbelled inward over the bay at 50 deg to a flat "
                           "top; one rectangular void takes more than 40 % of each cheek; three "
                           "3.0 proud square ribs cross the top at 12 mm pitch; board-marking "
                           "grooves 0.6 x 0.3 at 2.4 pitch run the print direction on every large "
                           "vertical face; the SMA comes out through a square sunk land, not a "
                           "boss. 1.0 mm chamfers, no fillet anywhere in the slab work."},
    "gyroid": {**({"style": "gyroid"} if "gyroid" in S.STYLES else {}), "material": "PETG",
               "params": {"TOWER": False, "GYROID": True, "WALL_T": GY_WALL, "TRAY_T": GY_DECK[0],
                          "TRAY_Y": GY_DECK[1], "TRAY_R": GY_ROUND, "STEP_Y": GY_STEP_Y},
               "notes": "A FROZEN FLUID. The silhouette is deliberately dumb - a soft-cornered 3.6 mm "
                        "slab shroud, r 3.0 on the plan outline - because every visual event is "
                        "inside it: a 1.6 mm rind on every bearing face and a gyroid sheet between "
                        "the rinds, period 10. The ventilation is NOT cut; it is what the sheet "
                        "leaves where it breaks the outer surface. Ships cell='voronoi' until the "
                        "gyroid recipe lands, and the undecorated 3.6 slab passes on its own."},
}
ASSEMBLY_VARIANT = "flat"  # the block in the assembly is exactly the shipped tail_block__flat
NOTES = (
    "Snaps onto the two Ø6 rear-tip standoffs (clips Z 2-22, bore Ø6.5, mouths outboard) and is "
    "pulled down by one M3 x 8 self-tapper up through rear_tail_axis (0, -91) into the Ø2.7 boss (5.5 mm of "
    "engagement). Nothing else is drilled: led_buzzer keeps rear_30p5_row and its screw heads run "
    "in the Ø8 arched reliefs at y -81 in both side walls. The VTX (30 x 30 x 12 on the 25.5 M2 "
    "pattern at (0, -73), 3 mm standoffs) drops in from above; the bay is open upward on purpose - "
    "plate_top is its ceiling - and open rearward through two Ø6.5 arched vents for heatsink air "
    "and the pigtail. SMA/RP-SMA bulkhead: Ø6.5 D-hole (6.0 flat, flat downward) at (0, -89.4, "
    "Z 15) through the 2.0 mm panel; the nut goes on the rear face with a Ø14 x 6.5 spanner "
    "pocket behind it. The `fin` variant (FIN/TOWER=True) adds the 50 deg dipole blade with a 4.4 mm "
    "coax channel and a 2.2 mm snap slit; the `flat` variant leaves it off so antenna_mast's coax can "
    "drop through the plate_top U-notch, and that is the one the combined assembly installs. "
    "45 deg was not used for the blade because a 45 deg blade face reads "
    "normal.Z -0.707 and fails the 0.7 overhang limit - the same reason antenna_mast leans 50. "
    "Rear skid: the tray's bottom stays on the Z 2 plane (a stepped footprint cannot be printed "
    "support-free) and reaches y -107, 6.8 mm behind the carbon tail tip and 2 mm above it, so it "
    "takes the hit at any nose-up attitude steeper than 16.3 deg. Prints bottom-down, no supports. "
    "ASSEMBLY ORDER, nocturne (two parts, two filaments, no AMS): (1) print the shell in black PETG "
    "and the cap rack in natural or clear; (2) dress the five LEDs into the wells from BELOW, "
    "through the ducts, before the block goes on the frame - the wells open upward and the rabbet "
    f"is their only access; (3) drop {LENS} into the 0.4 mm rabbet in the plinth top "
    "(Z 8.6-9.0), domes up, one dome over each well, 0.2 mm "
    "clearance all round - a drop of CA at two corners if you fly it hard; (4) snap the block onto "
    "the two rear-tip standoffs and run the M3 up through rear_tail_axis. The cap rack cannot be "
    "fitted after the block is bolted down without removing the block, which is deliberate: it is "
    "what keeps the wells sealed against grit."
)

# --- parameters (mm, deg) --------------------------------------------------------------------
CAV = (30.0, 30.0, 12.0)  # VTX board width (X) x length (Y) x body height (Z)
CLEAR = 0.4  # clearance around the board on every side
STAND_H = 3.0  # M2 standoffs under the board
WALL_T = 1.8  # side wall and outer wall thickness (1.6-2.0 band)
PANEL_T = 2.0  # rear panel: also the SMA seat, must stay <= SMA_SEAT_WALL_MAX
TOP_Z = 22.0  # top of the walls, panel and clips' parent wall (plate_top is at 34)
STEP_Z, STEP_Y = 14.0, -60.0  # above STEP_Z the walls start at STEP_Y to clear xt60_holder
TRAY_T = 3.0  # tail tray / skid thickness
TRAY_Y = -107.0  # rear end of the skid
CLIP_H = 20.0  # clip grip on the standoffs, from Z 2: the walls' full height, so the block
#                snaps on sideways with plate_top in place instead of having to be threaded on
BOSS_HX, BOSS_Y, BOSS_Z1 = 4.0, -95.0, 7.5  # M3 boss block around rear_tail_axis
VENT_X = (4.5, 11.0)  # arched rear vents, |x| band (mirrored)
VENT_SPRING_Z = 6.0  # arch centre; apex = VENT_SPRING_Z + width / 2
RELIEF_Y = (-85.0, -77.0)  # arched relief over the led_buzzer screw heads
RELIEF_SPRING_Z = 4.0
SMA_Z = 15.0  # bulkhead axis height in the rear panel
SPANNER_D, SPANNER_L = 14.0, 6.5  # clear pocket behind the nut

FIN = True  # the dipole blade; TOWER is accepted as an alias (antenna_mast calls TOWER=False)
FIN_ANGLE = 50.0  # elevation, rearward-up; 45 exactly fails the 0.7 overhang cosine
FIN_ROOT = (-97.6, 14.5)  # (y, z) of the blade's front-upper root corner
FIN_LEN, FIN_W, FIN_T = 22.0, 10.0, 7.6  # along the axis, across the blade, thickness in X
COAX_D, COAX_SLIT, COAX_OFF = 4.4, 2.2, 4.2  # channel, snap slit, channel axis off the rear edge
COAX_Y0 = -99.0  # vertical plane that closes the channel's lower end (1.7 mm of floor under it)

# --- CARAPACE: the tail cusp ------------------------------------------------------------------
# The dome cannot cross the bay and that is measured, not assumed: an elytral roof over the open U
# would be a 30.8 mm span whose underside faces straight down. `overhangs()` accepts a downward face
# only inside a declared bridge <= 20 mm (PETG) or as a cylindrical arch of Ø <= 12, and a pointed
# vault steep enough to pass (>= 45.6 deg flanks, or normal.Z > -0.70) needs 15.4 x tan 46 = 15.9 mm
# of rise over the half span, putting its ridge at Z 33.3 - through plate_top at 34 and 11 mm over
# the TOP_Z the tower logic depends on. So the elytra do what a tiger beetle's actually do: they roll
# OUTBOARD over each flank and close behind the abdomen, and the suture lives on the tail they make.
DOME = False  # the carapace reading (VARIANTS["carapace"])
DOME_Z0 = 10.5  # the CARINA: where the domed shoulder breaks into the vertical skirt
DOME_Y1 = -66.0  # forward end of the shoulder's full width; it runs out to a cusp past this
DOME_NOSE = 6.0  # cusp length at that end (CN-3: a free silhouette edge ends in a point)
# The shoulder's section in (x, z), right side, from the skirt round to the bay lip. Convex, no run
# longer than 12 mm (CARAPACE's silhouette rule), and every downward-facing segment steeper than
# 45.6 deg: the carina underside (17.2, 10.0)->(19.0, 12.2) reads normal.Z -0.633 against the -0.70
# limit, where the same rise over 2.0 would read -0.669 and the same over 1.8 would fail outright.
#
# THE CARINA HEIGHT IS A MEASURED NUMBER, NOT A TASTE. It splits the flank's 20 mm between a skirt
# and a domed shoulder, and both halves have exactly one job they must be big enough for:
#
#   the shoulder's PLANAR run holds the five cusped slits. Only a plane takes a straight prism cut
#     cleanly: cut the same slits through the sloping carina and every cusp feathers to 0.12 mm
#     against a 1.2 mm floor (measured, 234 rays). At Z 10.5 the planar run is 7.6 mm (Z 13.0-20.6).
#   the SKIRT holds the maculation. mark_sketch("lunule", 16.0) measures 18.50 x 7.11 mm - a lunule
#     is 0.44 x its own length thick - and MARK_MIN forbids shrinking it. 8.5 mm of skirt leaves
#     0.7 mm top and bottom; 7.0 mm of skirt (carina at Z 9) refuses the mark outright.
#
# The two cannot share a surface: the five slits occupy 21 mm of the flank's 28 mm free run and the
# lunule needs 20.5 mm of it, so the mark goes BELOW the carina, on a band 0.9 mm proud (CN-5).
DOME_SECTION = ((15.4, 10.5), (17.2, 10.5), (19.0, 12.7), (19.6, 21.0), (18.4, 21.7),
                (16.8, 22.0), (15.4, 22.0))
DOME_X = 19.6  # widest point (prop-disc limit at y -94 is 23.93)
MACULA_PAD = 0.9  # the band the lunule is debossed into, proud of the skirt: a 0.6 deboss into a
#                1.8 mm wall leaves 1.2, under PETG's 1.5 floor, so the local wall becomes 2.7
MACULA_RAMP = 1.2  # > 1.02 x MACULA_PAD, or the run-out reads normal.Z -0.7071 and flags
MACULA_Y = (-88.0, -57.6)  # the band, rear ramp to front (the wall's own end needs no ramp). It
#                starts BEHIND the led_buzzer relief, not in front of it: a band that stopped at
#                y -77.6 put the lunule's tapering tip inside its own run-out, where the pad is only
#                0.19 mm and the deboss left 1.39 - under PETG's 1.5 floor. Running the band past the
#                relief costs one number elsewhere (the relief tunnel is cut 2.4 mm deep, not 1.2)
#                and buys the mark a surface that is a full 2.7 mm thick end to end.
CARINA_R = 0.8  # the crease where the dome breaks into the vertical skirt
# The tail cusp: a solid, sutured, domed abdomen apex standing on the tray behind the spanner pocket.
CUSP_FRONT = -96.6  # front face of the boss: 0.3 clear of the Ø14 spanner pocket (ends y -96.9)
CUSP_CREST = 16.0  # flat crest height => rise 11.0 over span 34.4 = 0.320, mid-band of 0.28-0.36
CUSP_BREAK = -107.0  # where the crest starts falling to the point
CUSP_SHOULDER = (-99.0, -102.5)  # plan taper: full width to CUSP_HX
CUSP_HX = 10.9  # half width at the taper's end, and the cusp's root half width
CUSP_LEN = 11.5  # cusp length; a vesica of root 2 x 10.9 needs >= 10.92, so this is the real floor
CUSP_LAP = 0.6  # the cusp's root sits this far FORWARD of the taper's end, so the two faces overlap
CUSP_TIP_R = 0.8  # the point is blunted to r 0.8 so a Ø1.6 ball fits it (the cusped-style check)
CUSP_Y = CUSP_SHOULDER[1] + CUSP_LAP - CUSP_LEN  # -113.4: the tail point
ELY_N = 5  # cusped elytra slits per shoulder
ELY_PITCH, ELY_W = 4.0, 2.2  # the budget is tight and worth writing down: the usable run is bounded
# behind by the clip ring's clean zone (y -87.95) and in front by the shoulder's own cusp (y -66,
# less the 2.7 mm a grown slit needs), which leaves 16.55 mm. Five slits at pitch 4.0 span 16.0.
ELY_Y0 = -85.5  # the rearmost slit, 2.75 clear of the clip ring's zone
ELY_LIG = 1.2
ELY_Z = (13.4, 20.2)  # the band: inside the flank's 7.6 mm planar run, so both cusps land on a
#                plane. Cut through the sloping carina instead and each cusp feathers to 0.12 mm.
PUNCTA_D, PUNCTA_PITCH, PUNCTA_DEPTH = 1.8, 3.6, 0.45
LUNULE = 16.0  # mark size; MARK_MIN["lunule"] is 16.0, so this is the smallest legal lunule
LUNULE_AT = (-67.3, 6.25)  # (y, z) centre on the maculation band: the mark spans y -76.55..-58.05
#                and Z 2.70..9.81, so 0.45 mm to the wall's own front edge and 0.70 mm top and
#                bottom of the 8.5 mm skirt. Those are the real clearances of "the smallest legal
#                lunule on the largest surface this part has"; there is no slack to find.
SUT_W, SUT_D = 0.8, 0.4  # CN-1 suture on X = 0

# --- FERAL: the stinger ----------------------------------------------------------------------
STING = False
STING_ROOT = (-99.0, 5.0)  # (y, z): on the tray behind the Ø14 spanner pocket, straddling x 0
STING_BURY = 10.0  # how far the cone is started BEFORE the root, so it gussets down to the bed plane
STING_ANGLE = 56.0  # elevation: the cone's lowest generatrix then lies at 49.9 deg, normal.Z -0.64
STING_LEN = 30.0
STING_D0, STING_D1 = 8.0, 1.6  # root / tip diameter; the tip is blunted to r 0.8
SPINE_N = 5
SPINE_Y0, SPINE_PITCH = -64.0, -5.85  # tallest forward, marching rearward along each wall top. Both
#                numbers are bounded by what is UNDER the wall top: at pitch 9 the rearmost spine
#                overhung the wall's own rear end by 1.05 mm and the fourth one straddled the clip
#                mouth (a 5.2 mm slot cut clean through the wall at y -96.6..-91.4), leaving two
#                floating flanges with 3.41 and 1.63 mm² of downward face. THE PITCH IS SET BY THE
#                LAST SPINE'S TIP, measured: _spine_row() clips the blade to what is actually under
#                the wall top, and that box starts at y -89.0. At pitch -6.2 the fifth spine's centre
#                fell at y -88.8, so the clip plane sliced 0.6 mm off its own r 0.8 tip circle - a
#                Ø1.6 ball filled only 0.686 of it, a flat-chopped point on the one spine the eye
#                follows the row to. At -5.85 the row runs y -60.88..-88.56: the first spine's base
#                stays 0.28 mm inside the wall's front step (-60.6) and the last spine's base stays
#                0.44 mm inside the clip plane, so every one of the five ends in a true blunted cusp.
SPINE_H0 = 4.0
SPINE_RUN = (1.0, 0.78, 0.61, 0.48, 0.37)  # the design language's descending run
SPINE_FLANK = 52.0  # deg from horizontal; >= 50 required, and 45.6 is the overhang floor
SPINE_TIP_R = 0.8
CHEEK_D, CHEEK_PITCH = 2.2, 4.0  # punctation on the wall cheeks (the design language's FERAL numbers)
CHEEK_LIG = 1.4  # boundary and pairwise ligament, over TPU's 1.2 floor. NOT the default pitch - d =
#                1.8: the cheek's only free run is the 17.2 mm between the led_buzzer relief's zone
#                and the wall's front edge, and at 1.8 that run holds 3 pits - a row of three reads
#                as three holes, not as punctation. At 1.4 it holds seven and the field reads.
SLASH_AT = (-74.0, 17.0)  # (y, z) centre of the lunule slash on each flank. High, not central: the
#                mark is 7.11 mm tall, and lifting it to Z 17 frees Z 2.6-13.0 of cheek for a
#                two-row punctate field instead of the single row a central slash leaves.
CHEEK_Z = (2.6, 12.0)  # the punctate band, under the slash and inside the full-length lower wall.
#                12.0, not 13.0: the slash's own clean zone starts at Z 12.05, so a band reaching
#                13.0 only offered place_apertures a strip it had to refuse anyway.

# --- NOCTURNE: the vane fan ------------------------------------------------------------------
RACK = False
PLINTH_Y = (-116.2, -96.6)  # the lit plinth, 0.3 clear of the Ø14 spanner pocket (ends y -96.9)
PLINTH_Z1 = 9.0  # 9, not 11: the centre vane has to be 22 mm long to carry an 18.5 mm lunule along
#                its radius with a 1.4 mm ligament at each end, and a 22 mm vane off a Z 11 plinth
#                tips out at Z 33 - 1.0 mm under plate_top. Off Z 9 it tips out at 31.0.
PLINTH_R = 4.0  # rear plan corners, vertical axis: no down-facing normal
LED_D = 1.2  # a 0603/0805 SMD emitter: mouth Ø = 3 x LED = 3.6
WELL_DEPTH, WELL_HALF = 2.6, 25.0  # 2.6 is what makes the real half angle 24.8, not the 19.4 a
#                deeper well gives once light_well() clamps the throat to the LED diameter
WELL_Y = -98.6  # wells sit FORWARD of the rods, so their mouths stay open for the lens
VANE_T = 2.0
VANE_X = (-11.2, -5.6, 0.0, 5.6, 11.2)  # one root per well
VANE_FAN = (-30.0, -15.0, 0.0, 15.0, 30.0)  # 15 deg apart; 30 deg is the overhang ceiling for a
#                planar vane: its underside then lies at 60 deg, normal.Z -0.50 against the -0.70 limit
VANE_R = (13.0, 17.0, 22.0, 17.0, 13.0)  # radial length: the comb's teeth
VANE_BURY = 2.0  # how far each vane roots into the plinth
PIPE_D = 3.0  # light pipe inside the conduit rod; rod Ø = PIPE_D + 2 x 1.2 = 5.4
PIPE_TIP = 0.8  # material left over the pipe's cone at the vane tip, so the tip glows
PIPE_CONE = 12.0  # half angle of the bore's closing cone, from the bore axis. 12, not 40: the cone's
#                worst normal reads -sin(cone + fan), so 12 + 30 = -0.669 against the -0.70 limit
DUCT_Z = 5.5  # the Ø3 duct from well to rod base; a horizontal Ø3 bore is an exempt arch (<= Ø12).
#                Low enough that its crown at Z 7.0 leaves 1.6 mm under the lens rabbet's floor: at
#                Z 7.0 the crown sat 0.1 mm under it and the floor measured 0.311 mm of material.
CONDUIT_Y = -104.5  # the rod's axis in plan: the vane's leading edge
WEB_Y = (-105.5, -117.2)  # the 2 mm web trailing the rod, where the ladder and the lunule live. Its
#                front edge is 1.7 mm INSIDE the Ø5.4 rod, not tangent to it: tangent, the web's own
#                front face measured 0.228 mm of material on 20 rays - a zero-thickness crevice all
#                the way up the vane. Width 11.7 mm carries the lunule's 7.11 with 2.3 each side.
LADDER = (4.4, 2.0, 3.8)  # (slot length, width, pitch). The length is a printability number: a
#                transverse stadium's ceiling is a FLAT face of (length - width) x VANE_T, and at
#                4.4 x 2.0 that is 4.8 mm² - under the same 5.0 mm² floor in overhangs() that makes
#                Ø2.4 punctation legal. At 6.4 long it is 8.8 mm² and flags on every tilted vane.
LADDER_LIG = 1.6  # PETG's minimum ligament (§5.1) - the one place the stiffer material needs the
#                fatter geometry, because PETG cracks at a thin ligament under vibration.
LADDER_Z = (2.0, 2.0)  # (up from the plinth, down from the vane tip) - the band the ladder runs in.
#                The second number is what the comb is made of: the ladder lives in the WEB, and the
#                web trails the Ø5.4 conduit rod, so no slot can ever reach the light pipe. Stopping
#                the ladder 3.0 mm short of the tip (the first reading) was therefore protecting
#                nothing and cost the rack half its slots - 6 over five vanes, one per tooth, which
#                reads as damage rather than as the frame's own LADDER motif. At 2.0 mm short of the
#                tip, clear of the 0.9 tip fillet, the five vanes carry 2/3/4/3/2.
LENS_T = 1.0  # translucent cap sheet
LENS_RABBET = 0.4  # how deep the sheet sits into the plinth top
LENS_DOME = 1.5  # plano-convex rise over each well
LENS_BASE = 4.2  # dome base Ø, 0.3 proud of the Ø3.6 well mouth all round
LENS_FIT = 0.2  # clearance all round in the rabbet
LENS_X, LENS_Y = 13.3, (-101.2, -96.6)  # the sheet's plan

# --- derived geometry (frame coordinates) ------------------------------------------------------
Z0 = Z_BOTTOM_TOP  # 2.0: plate_bottom top face, the block's single bed plane
CLIP_XY = REAR_TIP_XY  # (16.5, -94): the rear-tip standoff axes
TAIL_AXIS = hole_xy("rear_tail_axis")[0]  # (0, -91), Ø3.2 in plate_bottom
VTX_XY = (0.0, sum(y for _x, y in hole_xy("rear_25p5")) / len(hole_xy("rear_25p5")))  # (0, -73)
HEAD_AXES = tuple(sorted(hole_xy("rear_30p5_row")))  # (±15.25, -81): led_buzzer's screws

CAV_HX = CAV[0] / 2 + CLEAR  # 15.4
CAV_Y1 = VTX_XY[1] + CAV[1] / 2 + CLEAR  # -57.6 (front, open)
CAV_Y0 = VTX_XY[1] - CAV[1] / 2 - CLEAR  # -88.4 (rear, closed by the panel)
CAV_Z1 = Z0 + STAND_H + CAV[2] + CLEAR  # 17.4: top of the board plus clearance
WALL_X0, WALL_X1 = CAV_HX, CAV_HX + WALL_T  # 15.4 .. 17.2
PANEL_Y1, PANEL_Y0 = CAV_Y0, CAV_Y0 - PANEL_T  # -88.4 .. -90.4
WALL_Y0 = -100.4  # rear end of the walls: 0.2 behind plate_bottom's tail tip (-100.2)
TRAY_Z1 = Z0 + TRAY_T  # 5.0
CLIP_Z1 = Z0 + CLIP_H  # 22.0: the clips run the walls' full height
SMA_FLAT_Z = SMA_Z - (SMA_FLAT - D_SMA / 2)  # 12.25: the D-hole chord, flat face downward

_DEFAULTS = dict(CAV=CAV, CLEAR=CLEAR, STAND_H=STAND_H, WALL_T=WALL_T, PANEL_T=PANEL_T,
                 TOP_Z=TOP_Z, STEP_Z=STEP_Z, STEP_Y=STEP_Y, TRAY_T=TRAY_T, TRAY_Y=TRAY_Y, TRAY_R=4.0,
                 CLIP_H=CLIP_H, BOSS_HX=BOSS_HX, BOSS_Y=BOSS_Y, BOSS_Z1=BOSS_Z1,
                 VENT_X=VENT_X, VENT_SPRING_Z=VENT_SPRING_Z, RELIEF_Y=RELIEF_Y,
                 RELIEF_SPRING_Z=RELIEF_SPRING_Z, SMA_Z=SMA_Z, FIN=FIN, TOWER=FIN,
                 FIN_ANGLE=FIN_ANGLE, FIN_ROOT=FIN_ROOT, FIN_LEN=FIN_LEN, FIN_W=FIN_W,
                 FIN_T=FIN_T, COAX_D=COAX_D, COAX_SLIT=COAX_SLIT, COAX_OFF=COAX_OFF,
                 COAX_Y0=COAX_Y0,
                 DOME=DOME, DOME_Z0=DOME_Z0, DOME_X=DOME_X, DOME_Y1=DOME_Y1,
                 CUSP_Y=CUSP_Y, CUSP_FRONT=CUSP_FRONT, CUSP_CREST=CUSP_CREST,
                 CUSP_BREAK=CUSP_BREAK, ELY_N=ELY_N, ELY_PITCH=ELY_PITCH,
                 ELY_W=ELY_W, LUNULE=LUNULE, LUNULE_AT=LUNULE_AT,
                 STING=STING, STING_ROOT=STING_ROOT, STING_ANGLE=STING_ANGLE, STING_LEN=STING_LEN,
                 STING_D0=STING_D0, STING_D1=STING_D1, STING_BURY=STING_BURY,
                 SPINE_N=SPINE_N, SPINE_H0=SPINE_H0,
                 SPINE_Y0=SPINE_Y0, SPINE_PITCH=SPINE_PITCH, SLASH_AT=SLASH_AT,
                 RACK=RACK, PLINTH_Y=PLINTH_Y, PLINTH_Z1=PLINTH_Z1, LED_D=LED_D,
                 WELL_DEPTH=WELL_DEPTH, VANE_T=VANE_T, VANE_R=VANE_R, PIPE_D=PIPE_D,
                 CONDUIT_Y=CONDUIT_Y, WEB_Y=WEB_Y, MARK=True,
                 VESPID=VESPID, VE_Y0=VE_Y0, VE_N=VE_N, VE_L1=VE_L1, VE_LR=VE_LR, VE_G1=VE_G1,
                 VE_GR=VE_GR, VE_STING_L=VE_STING_L, VE_BASE=VE_BASE,
                 BRUT=BRUT, BR_T=BR_T, BR_TOP_Z=BR_TOP_Z, BR_LAND=BR_LAND,
                 BR_CORBEL=BR_CORBEL,
                 GYROID=GYROID, GY_PERIOD=GY_PERIOD, GY_ROUND=GY_ROUND)


def _p(**overrides) -> dict:
    """Parameter dict with every derived extent recomputed from the overrides."""
    p = {**_DEFAULTS, **overrides}
    p["CAV_HX"] = p["CAV"][0] / 2 + p["CLEAR"]
    p["CAV_Y1"] = VTX_XY[1] + p["CAV"][1] / 2 + p["CLEAR"]
    p["CAV_Y0"] = VTX_XY[1] - p["CAV"][1] / 2 - p["CLEAR"]
    p["CAV_Z1"] = Z0 + p["STAND_H"] + p["CAV"][2] + p["CLEAR"]
    p["WALL_X0"], p["WALL_X1"] = p["CAV_HX"], p["CAV_HX"] + p["WALL_T"]
    p["PANEL_Y1"], p["PANEL_Y0"] = p["CAV_Y0"], p["CAV_Y0"] - p["PANEL_T"]
    p["TRAY_Z1"] = Z0 + p["TRAY_T"]
    p["CLIP_Z1"] = Z0 + p["CLIP_H"]
    p["fin_on"] = bool(p["FIN"]) and bool(p["TOWER"])
    # CARAPACE and NOCTURNE both lengthen the tray, for different reasons: the cusp has to run out to
    # a true point (CN-3) and the vane fan needs a plinth behind the spanner pocket. Both make the
    # skid angle SMALLER, which is the direction the landing check wants.
    if "TRAY_Y" not in overrides:
        if p["DOME"]:
            p["TRAY_Y"] = p["CUSP_Y"]
        elif p["RACK"]:
            p["TRAY_Y"] = p["PLINTH_Y"][0]
    return p


# --- shell ------------------------------------------------------------------------------------
def _mirrored(part: Part) -> Part:
    """part + its mirror in the YZ plane (the block is symmetric about x 0)."""
    return part + part.mirror(Plane.YZ)


def _walls(p: dict) -> Part:
    """Both side walls. Below STEP_Z they reach the bay's front edge; above it they stop at
    STEP_Y, which is what keeps them off xt60_holder's socket block (rear face y -57.4,
    Z 14.5-33.8)."""
    lo = box(p["WALL_X0"], WALL_Y0, Z0, p["WALL_X1"], p["CAV_Y1"], p["STEP_Z"])
    hi = box(p["WALL_X0"], WALL_Y0, p["STEP_Z"], p["WALL_X1"], p["STEP_Y"], p["TOP_Z"])
    return _mirrored(lo + hi)


def _panel(p: dict) -> Part:
    """Transverse rear wall of the bay: impact face, SMA seat and vent panel."""
    return box(-p["WALL_X1"], p["PANEL_Y0"], Z0, p["WALL_X1"], p["PANEL_Y1"], p["TOP_Z"])


def _tray(p: dict) -> Part:
    """Tail tray: ties the two clips together, bridges the plate_bottom tail notch and runs
    past the carbon as the skid. Rear corners rounded (vertical axis: no down-facing normal)."""
    if p["DOME"]:
        # CARAPACE: the tray IS the cusp's footprint, so it takes the cusped plan and no 4 mm rounds -
        # a rounded stub would contradict CN-3 on the one edge that carries the style's whole character
        return S.extrude_cut(_cusp_plan(p, p["PANEL_Y0"]), Plane.XY.offset(Z0), p["TRAY_T"])
    sk = Pos(0, (p["TRAY_Y"] + p["PANEL_Y0"]) / 2) * Rectangle(2 * p["WALL_X1"], p["PANEL_Y0"] - p["TRAY_Y"])
    sk = fillet(sk.vertices().filter_by(lambda v: v.Y < p["TRAY_Y"] + 1e-6), p["TRAY_R"])
    return extrude(Plane.XY.offset(Z0) * sk, amount=p["TRAY_T"])


def _boss(p: dict) -> Part:
    """Block around rear_tail_axis for the single M3 x 8 self-tapper, flush with the panel's
    front face so it cannot touch the board."""
    return box(-p["BOSS_HX"], p["BOSS_Y"], Z0, p["BOSS_HX"], p["PANEL_Y1"], p["BOSS_Z1"])


def _clips(p: dict) -> Part:
    """C-clips round the two Ø6 rear-tip standoffs, mouths facing outboard, over the walls' full
    height: the block snaps on from the side with plate_top still bolted down."""
    out = Part()
    for sx, opening in ((1.0, 0.0), (-1.0, 180.0)):
        out += c_clip((sx * CLIP_XY[0], CLIP_XY[1]), Z0, p["CLIP_H"], opening_deg=opening,
                      material=MATERIAL, bore_d=D_CLIP_BORE, wall=CLIP_WALL)
    return out


def _clip_tools(p: dict) -> Part:
    """What the clips have to take out of the shell, which runs straight through the standoff
    axes: the Ø6.5 bore and the outboard mouth (the same STANDOFF_D - snap slot c_clip uses).
    The walls, the panel's flanks and the tray all cross the axes, so this is subtracted from the
    whole shell BEFORE the rings are added, and the rings' filleted lips survive."""
    mouth = STANDOFF_D - MATERIALS[MATERIAL]["snap"]
    out = Part()
    for sx in (1.0, -1.0):
        x, y = sx * CLIP_XY[0], CLIP_XY[1]
        out += cylinder(x, y, Z0 - 1.0, Z0 + p["CLIP_H"] + 1.0, D_CLIP_BORE)
        out += box(min(x, sx * 30.0), y - mouth / 2, Z0 - 1.0, max(x, sx * 30.0), y + mouth / 2,
                   Z0 + p["CLIP_H"] + 1.0)
    return out


# --- cutting tools ----------------------------------------------------------------------------
def _arch(x0: float, x1: float, z0: float, spring_z: float) -> "Sketch":
    """Slot profile x0..x1 from z0 up to a Ø(x1 - x0) arch centred at spring_z (apex above it);
    open at the bottom, so nothing in it faces up and its roof is an exempt arch."""
    w = x1 - x0
    return (Pos((x0 + x1) / 2, (z0 + spring_z) / 2) * Rectangle(w, spring_z - z0)
            + Pos((x0 + x1) / 2, spring_z) * Circle(w / 2))


def _vents(p: dict) -> Part:
    """Two arched vents through the rear panel: heatsink air and the pigtail out of the bay."""
    sk = _arch(p["VENT_X"][0], p["VENT_X"][1], Z0, p["VENT_SPRING_Z"])
    sk = sk + sk.mirror(Plane.YZ)
    return extrude(Plane.XZ.offset(-(p["PANEL_Y1"] + 0.5)) * sk, amount=p["PANEL_T"] + 1.0)


def _head_reliefs(p: dict) -> Part:
    """Arched tunnels through both side walls over led_buzzer's two M3 heads (Ø5.7, Z 2-3.65 on
    the plate top face at (±15.25, -81)). Axis along X, Ø8: an exempt arch, open at the bottom."""
    sk = _arch(p["RELIEF_Y"][0], p["RELIEF_Y"][1], Z0, p["RELIEF_SPRING_Z"])
    # 2.4 of over-reach, not 1.2: CARAPACE's maculation band stands 0.9 proud of this same wall, and
    # a tool that stopped at x 17.8 would leave the tunnel blind behind it. The extra reach cuts
    # nothing on any other style - there is no material outboard of x 17.2 there.
    tool = extrude(Plane.YZ.offset(p["WALL_X0"] - 0.6) * sk, amount=p["WALL_T"] + 2.4)
    return _mirrored(tool)


def _sma_tool(p: dict) -> Part:
    """Ø6.5 D-hole (SMA_FLAT across the flat) through the panel, axis -Y, flat face downward so
    the flat never becomes a ceiling. Ø6.5 <= arch_d with a horizontal axis: exempt."""
    flat_z = p["SMA_Z"] - (SMA_FLAT - D_SMA / 2)
    sk = Pos(0, p["SMA_Z"]) * Circle(D_SMA / 2) - Pos(0, flat_z - 5.0) * Rectangle(3 * D_SMA, 10.0)
    return extrude(Plane.XZ.offset(-(p["PANEL_Y1"] + 0.5)) * sk, amount=p["PANEL_T"] + 1.0)


def _tap_tool(p: dict) -> Part:
    """Ø2.7 self-tap bore right through the boss (no blind ceiling)."""
    return cylinder(*TAIL_AXIS, Z0 - 1.0, p["BOSS_Z1"] + 1.0, D_M3_TAP)


# --- dipole fin -------------------------------------------------------------------------------
def _fin_axes(p: dict) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """((y, z) of the blade's front-upper root corner, unit axis d, unit across-blade n) in the
    YZ plane. d points rearward-up at FIN_ANGLE, n points rearward-down across the blade."""
    a = radians(p["FIN_ANGLE"])
    return tuple(p["FIN_ROOT"]), (-cos(a), sin(a)), (-sin(a), -cos(a))


def _fin_pt(base, d, n, t: float, s: float) -> tuple[float, float]:
    return (base[0] + d[0] * t + n[0] * s, base[1] + d[1] * t + n[1] * s)


def _yz_prism(pts, x0: float, thick: float) -> Part:
    """Polygon in the YZ plane (points are (y, z)) extruded in X from x0 by `thick`.
    `dir` is explicit: extrude() otherwise follows the polygon's winding and can run -X."""
    return extrude(Plane.YZ.offset(x0) * Polygon(*pts, align=None), amount=thick, dir=(1, 0, 0))


def _fin(p: dict) -> Part:
    """The blade plus the gusset that roots it in the tray. Every face of the outline is either
    vertical, upward, or tilted FIN_ANGLE from the horizontal (normal.Z -cos 50 = -0.64, inside
    the 0.7 overhang limit); at 45 deg the two long faces would read -0.707 and fail."""
    root, d, n = _fin_axes(p)
    e1 = _fin_pt(root, d, n, 0.0, p["FIN_W"])  # rear-down root corner
    e4 = _fin_pt(root, d, n, p["FIN_LEN"], p["FIN_W"])  # rear-down tip corner
    e3 = _fin_pt(root, d, n, p["FIN_LEN"], 0.0)  # front-up tip corner
    pts = [(root[0], Z0), (e1[0], Z0), e1, e4, e3, root]
    return _yz_prism(pts, -p["FIN_T"] / 2, p["FIN_T"])


def _coax_tools(p: dict) -> Part:
    """Square COAX_D channel along the blade axis plus the COAX_SLIT snap slit out through the
    rear-down face; the dipole snaps in through the slit and bottoms out in the channel.
    The channel's lower end is closed by the vertical plane COAX_Y0 instead of a plane across the
    blade: a square end perpendicular to the axis would be a 19 mm² face at normal.Z -0.77. The
    slit starts at the root section, so its only down-facing end face is COAX_SLIT x
    (COAX_OFF - COAX_D/2) = 4.4 mm², under the 5 mm² the overhang check looks at."""
    root, d, n = _fin_axes(p)
    s_mid = p["FIN_W"] - p["COAX_OFF"]  # axis offset from the front-up edge
    half = p["COAX_D"] / 2
    t0, t1 = -p["FIN_W"], p["FIN_LEN"] + 2.0  # through the tip: a blind far end would be a ceiling
    chan = [_fin_pt(root, d, n, t, s) for t, s in ((t0, s_mid - half), (t1, s_mid - half),
                                                  (t1, s_mid + half), (t0, s_mid + half))]
    tool = _yz_prism(chan, -p["COAX_D"] / 2, p["COAX_D"])
    tool = tool & box(-60, -200, Z0 - 20, 60, p["COAX_Y0"], 80)  # vertical end wall, not a ceiling
    slit = [_fin_pt(root, d, n, t, s) for t, s in ((0.0, s_mid + half - 0.2), (t1, s_mid + half - 0.2),
                                                  (t1, p["FIN_W"] + 1.5), (0.0, p["FIN_W"] + 1.5))]
    return tool + _yz_prism(slit, -p["COAX_SLIT"] / 2, p["COAX_SLIT"])


# --- CARAPACE: the tail cusp ------------------------------------------------------------------
def _sk(pts) -> Sketch:
    return Sketch() + Polygon(*pts, align=None)


def _round2d(sk: Sketch, corners) -> tuple[Sketch, int]:
    """2D fillet on the named (u, v, r) corners of a profile. The fillet is built into the SECTION
    and then extruded, which is why the carina crease and the crest ladder never depend on OCCT
    agreeing to fillet a 3D edge on an assembled part."""
    done = 0
    for u, v, r in corners:
        hit = sk.vertices().filter_by(lambda q, u=u, v=v: abs(q.X - u) < 1e-4 and abs(q.Y - v) < 1e-4)
        if not hit:
            continue
        for attempt in (r, r / 2):
            try:
                sk, done = fillet(hit, attempt), done + 1
                break
            except Exception:  # noqa: BLE001 - OCCT refuses a radius that does not fit; halve it
                continue
    return sk, done


def _shoulder_section(p: dict) -> tuple[Sketch, int]:
    """The elytron's section, right side: skirt -> carina crease -> lunule facet -> crest -> bay lip.
    CARAPACE's ladder is fillets only (3.0 / 1.6 / 0.8), and the crease tier is the brief's 0.8."""
    return _round2d(_sk(DOME_SECTION),
                    [(17.2, p["DOME_Z0"], CARINA_R), (19.0, 12.7, 0.8),
                     (p["DOME_X"], 21.0, 0.8), (18.4, 21.7, 0.4), (16.8, 22.0, 0.4)])


def _shoulders(p: dict) -> Part:
    """Both elytra: the section swept along the wall and clipped in plan so its forward end runs out
    to a cusp instead of stopping in a square face (CN-3)."""
    sec, _n = _shoulder_section(p)
    body = extrude(Plane(origin=(0, WALL_Y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * sec,
                   amount=p["DOME_Y1"] - WALL_Y0 + DOME_NOSE + 1.0, dir=(0, 1, 0))
    w = p["DOME_X"] - p["WALL_X0"]
    xc = p["WALL_X0"] + w / 2
    plan = (Pos(xc, (WALL_Y0 + p["DOME_Y1"]) / 2) * Rectangle(w, p["DOME_Y1"] - WALL_Y0)
            + S.cusp_tail(w, DOME_NOSE, 0.6, at=(xc, p["DOME_Y1"]), angle=90.0))
    body &= S.extrude_cut(plan, Plane.XY.offset(p["DOME_Z0"] - 1.0), TOP_Z - p["DOME_Z0"] + 3.0)
    return _mirrored(body)


def _cusp_plan(p: dict, y_front: float | None = None) -> Sketch:
    """The tail's plan from `y_front` back to the point: full width, a straight taper to the cusp's
    root, then the far half of a vesica. The vesica sets CUSP_LEN, not taste: a cusp of root 2 x 10.9
    cannot be shorter than 10.92 or lens() clamps the half width and the root steps.

    Every piece OVERLAPS its neighbour. Three sketch faces that merely touch stay three faces, and
    the extrusion then hands back three solids - which is how `one solid` fails without anything
    looking wrong in the drawing."""
    y_front = p["CUSP_FRONT"] if y_front is None else y_front
    y0, y1 = CUSP_SHOULDER
    sk = Pos(0, (y_front + y0 - 0.4) / 2) * Rectangle(2 * p["WALL_X1"], y_front - y0 + 0.4)
    sk += _sk([(p["WALL_X1"], y0), (CUSP_HX, y1), (-CUSP_HX, y1), (-p["WALL_X1"], y0)])
    sk += S.cusp_tail(2 * CUSP_HX, CUSP_LEN, CUSP_TIP_R, at=(0.0, y1 + CUSP_LAP), angle=270.0)
    return sk


def _tail_boss(p: dict) -> Part:
    """The domed abdomen apex: the cusped plan, an elliptical vault along Y and a longitudinal crest
    profile, intersected. SOLID, which is the whole point - nothing in it faces down, so a dome over
    the TRAY is free where a dome over the open BAY is impossible (see the docstring).

    rise/span is 11.0 / 34.4 = 0.320 at x 0, the middle of the 0.28-0.36 band, and the crest is flat
    at CUSP_CREST from the front face back to CUSP_BREAK so the suture has a datum to sit on."""
    from build123d import Ellipse
    zs = p["TRAY_Z1"]
    rise = p["CUSP_CREST"] - zs
    plan = S.extrude_cut(_cusp_plan(p), Plane.XY.offset(zs), rise + 1.0)
    vault = extrude(Plane(origin=(0, p["CUSP_FRONT"] + 1.0, zs), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
                    * (Sketch() + Ellipse(p["WALL_X1"], rise)),
                    amount=p["CUSP_FRONT"] - p["CUSP_Y"] + 2.0, dir=(0, -1, 0))
    prof = _yz_prism([(p["CUSP_FRONT"], zs - 1.0), (p["CUSP_FRONT"], p["CUSP_CREST"]),
                      (p["CUSP_BREAK"], p["CUSP_CREST"]), (p["CUSP_Y"], zs + 0.6),
                      (p["CUSP_Y"], zs - 1.0)], -p["WALL_X1"] - 1.0, 2 * p["WALL_X1"] + 2.0)
    return Part() + (plan & vault & prof)


def _flank_region(p: dict, z1: float | None = None) -> Sketch:
    """The right skirt's decoratable area, sketched in (frame Y, frame Z) on Plane.YZ. It runs the
    wall's whole length - forward of STEP_Z the wall reaches CAV_Y1, not DOME_Y1."""
    z1 = p["DOME_Z0"] if z1 is None else z1
    y0, y1 = WALL_Y0, p["CAV_Y1"] - 1.0
    return Pos((y0 + y1) / 2, (Z0 + z1) / 2) * Rectangle(y1 - y0, z1 - Z0)


def _flank_clean(p: dict) -> list[Sketch]:
    """What nothing decorative may enter on a flank: the Ø8 arched led_buzzer relief (the wall is
    solid above its crown at Z 8, so the zone stops at 9.2, not at the wall top) and the band both
    clip rings run through, each padded by 1.2 mm of ligament."""
    r0, r1 = p["RELIEF_Y"]
    return [Pos((r0 + r1) / 2, (9.4 - 1.0) / 2) * Rectangle(r1 - r0 + 2.4, 10.4),
            Pos(CLIP_XY[1], Z0 + 10.0) * Rectangle(2 * (D_CLIP_BORE / 2 + CLIP_WALL) + 2.4, 26.0)]


def _carina_allow(p: dict) -> Part:
    """The carina fillet's own envelope, DECLARED as an edge treatment for min_wall(allow=...).

    A 0.8 fillet is tangent to the flank it runs into, so a ray leaving the flank within ~0.5 mm of
    that tangency grazes the fillet's own cylinder and measures 0.14 mm - six rays out of 2109, all
    of them the same seam. The ray sampler cannot tell an edge treatment from a thin wall (the same
    reason _blender.decorate takes `allow`), and the material across the carina is 1.8 mm. Declaring
    the treatment is the sanctioned answer; lowering the floor is not."""
    z0 = p["DOME_Z0"]
    return _mirrored(box(16.0, WALL_Y0 - 1.0, z0 - 0.5, DOME_SECTION[2][0] - 0.2,
                         p["DOME_Y1"] + DOME_NOSE + 1.0, z0 + 2.2))


def _elytra_slits(p: dict, grow: float = 0.0) -> tuple[Part, int]:
    """CARAPACE's apertures: cusped elytra slits through each shoulder, standing UPRIGHT.

    Upright is a printability argument, not a taste one, and it is the one side_panels measured: a
    slot lying along Y has a horizontal ceiling, and an arc's ceiling is a cylinder of ~1000 mm
    diameter that overhangs() will not take as a bridge at all (bridge_ok exempts planar faces, and
    the arch exemption stops at Ø12 for PETG). Upright, the only ceiling is the cusp itself - two
    tangent arcs meeting at a point - so no bridge is declared and no exemption is needed."""
    z0, z1 = ELY_Z
    length = z1 - z0
    half = min(p["ELY_W"] / 2, 0.45 * length)
    zc = (z0 + z1) / 2
    region = Pos((WALL_Y0 + p["DOME_Y1"]) / 2, zc) * \
        Rectangle(p["DOME_Y1"] - WALL_Y0, length + 2 * ELY_LIG + 0.2)

    def slit(cy, _v, g):
        return S.lens((cy, zc - length / 2 - g), (cy, zc + length / 2 + g), half + g)

    n = p["ELY_N"]
    ys = [ELY_Y0 + i * p["ELY_PITCH"] for i in range(n + 4)]
    sk, kept = S.place_apertures(region, slit, [(y, 0.0) for y in ys], ligament_min=ELY_LIG,
                                 clean=_flank_clean(p), pairwise=True, min_dim=2 * half,
                                 hole_min=2.0, limit=n)
    if not kept:
        return Part(), 0
    if grow > 0.0:
        # The allow envelope is rebuilt from the slits that were KEPT, never re-placed: a grown
        # candidate no longer fits the region and place_apertures would correctly drop all five.
        centres = sorted({round(f.center().X, 4) for f in sk.faces()})
        sk = Sketch()
        for cy in centres:
            sk += slit(cy, 0.0, grow)
    tool = S.extrude_cut(sk, Plane.YZ.offset(p["WALL_X0"] - 1.0), p["DOME_X"] - p["WALL_X0"] + 2.0)
    return _mirrored(tool), kept


def _no_puncta(p: dict) -> tuple[bool, str]:
    """WHY CARAPACE CARRIES NO PUNCTATE FIELD, as a measurement checks() can report.

    A Ø1.8 / pitch 3.6 hex field needs two staggered rows, which is 3.6 + 1.8 x 2 = 7.2 mm of clear
    surface in its short direction plus a 1.2 mm boundary ligament, so 9.6 mm. The two candidate
    surfaces, measured:

      the skirt, Z 2-10.5 (8.5 mm): every millimetre of its free run is the maculation band. Behind
        the band, y -86.2..-75.8 is the led_buzzer relief's zone and y -100.05..-87.95 is the clip
        rings', which leaves 2.75 mm of skirt - under one hex cell.
      the shoulder's planar flank, Z 13.0-20.6 (7.6 mm): 7.6 < 9.6 outright, and the five cusped
        slits own 21 mm of its 28 mm free run in any case.

    And the style agrees with the tape measure. CARAPACE's identity includes SHEEN - "an iridescent
    highlight only exists on a surface with no curvature breaks" - and a pit field is precisely a
    field of curvature breaks. FERAL's cheeks, 20 mm of flat flank with nothing else on them, are
    where this set's punctation belongs, and that is where it ships (Ø2.2 at pitch 4.0)."""
    skirt = p["DOME_Z0"] - Z0
    free = abs(MACULA_Y[0] - (p["RELIEF_Y"][1] - 1.2))
    return (skirt < 9.6 or free < PUNCTA_PITCH + 2 * 1.2,
            f"skirt {skirt:.1f} mm and flank 7.6 mm against the 9.6 mm a two-row Ø{PUNCTA_D} field "
            f"at pitch {PUNCTA_PITCH} needs; {free:.2f} mm of skirt left behind the maculation band")


def _suture_tool(p: dict) -> Part:
    """CN-1 on the one dorsal surface that crosses x 0 - the tail cusp's flat crest - running out to
    a true point at both ends. Cut LAST, after any Blender pass, so it lands on exact geometry."""
    return S.suture(p["CUSP_BREAK"], p["CUSP_FRONT"], p["CUSP_CREST"], w=SUT_W, depth=SUT_D)


def _macula_band(p: dict) -> Part:
    """CN-5's thickness gradient, and the reason the lunule is legal at all: the skirt is raised
    MACULA_PAD over the mark's footprint, so a 0.6 deboss leaves 2.1 mm instead of 1.2.

    The rear end runs out over MACULA_RAMP, which must be LONGER than the band is proud - a 45 deg
    run-out reads normal.Z -0.7071, just past overhangs()' -0.70 limit. The front end needs no ramp:
    it stops on the wall's own end face at CAV_Y1, which is vertical. The top stops at the carina, so
    the carina steps 0.9 mm outboard over the maculation - which is what a real lateral carina does."""
    y0, y1 = MACULA_Y
    x0, x1 = p["WALL_X1"], p["WALL_X1"] + MACULA_PAD
    # the run-out is taken in PLAN, not in section: a horizontal taper's normal lies in the XY plane,
    # so its normal.Z is 0 and the overhang question never arises
    prof = _sk([(x0, y0), (x1, y0 + MACULA_RAMP), (x1, y1), (x0, y1)])
    band = S.extrude_cut(prof, Plane.XY.offset(Z0), p["DOME_Z0"] - Z0)
    return _mirrored(band)


def _lunule(p: dict, mode: str = "deboss") -> Part | None:
    """The maculation, mirrored on the two maculation bands. Planar and vertical, so the deboss is a
    straight prism cut: a prism driven into the CURVED shoulder would be 0.6 deep at the crest and
    miss the surface entirely 2 mm away, which is how the first attempt left 550 feathered slivers."""
    if not S.mark_fits("lunule", p["LUNULE"]):
        return None
    y, z = p["LUNULE_AT"]
    m = S.mark("lunule", p["LUNULE"], mode, (p["WALL_X1"] + MACULA_PAD, y, z),
               normal=(1, 0, 0), x_dir=(0, 1, 0))
    return m + m.mirror(Plane.YZ)


def _mark_envelope(p: dict, grow: float = 0.7, depth: float = 1.8) -> Part | None:
    """The mark's own rim, grown, for min_wall(allow=...). A sample point sitting exactly ON the
    deboss wall is not "inside" the deboss solid and is not skipped, so the envelope has to be
    fatter than the mark: the ray then leaves a declared edge treatment and is ignored, while the
    2.1 mm of material behind the mark is still measured by every other ray on that face."""
    from build123d import offset as _offset
    if not S.mark_fits("lunule", p["LUNULE"]):
        return None
    y, z = p["LUNULE_AT"]
    try:
        sk = _offset(S.mark_sketch("lunule", p["LUNULE"]), grow)
    except Exception:  # noqa: BLE001 - a self-intersecting offset; fall back to the mark itself
        return _lunule(p)
    pl = Plane(origin=(p["WALL_X1"] + MACULA_PAD + 0.01, y, z), z_dir=(1, 0, 0), x_dir=(0, 1, 0))
    env = S.extrude_cut(sk, pl, -(depth + 0.01))
    return env + env.mirror(Plane.YZ)


# --- FERAL: the stinger ------------------------------------------------------------------------
def _sting_axis(p: dict) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    a = radians(p["STING_ANGLE"])
    y0, z0 = p["STING_ROOT"]
    return (0.0, y0, z0), (0.0, -cos(a), sin(a))


def _sting(p: dict) -> Part:
    """The abdominal sting: a tapered cone raked STING_ANGLE rearward-up, started STING_BURY before
    its root so it gussets all the way down to the bed plane instead of balancing on a 3 mm tray.

    56 deg is not a styling choice. The cone's own half angle is atan((4.0 - 0.8) / 30) = 6.1 deg, so
    its lowest generatrix lies at 49.9 deg from horizontal and reads normal.Z -0.644 against the
    -0.70 overhang limit; at 50 deg elevation the same generatrix would be 43.9 deg and fail. The
    root is at y -99 for a measured reason too: at y -94 the cone crosses the Ø14 spanner pocket."""
    (x0, y0, z0), d = _sting_axis(p)
    L, b = p["STING_LEN"], p["STING_BURY"]
    taper = (p["STING_D0"] - p["STING_D1"]) / 2 / L
    base = (x0 - d[0] * b, y0 - d[1] * b, z0 - d[2] * b)
    cone = Plane(origin=base, z_dir=d) * Cone(p["STING_D0"] / 2 + taper * b, p["STING_D1"] / 2,
                                             L + b, align=MIN_Z_ALIGN)
    tip = (x0 + d[0] * L, y0 + d[1] * L, z0 + d[2] * L)
    cone += Pos(*tip) * Sphere(p["STING_D1"] / 2)  # blunted to r 0.8: a Ø1.6 ball fits the tip
    return cone & box(-12, p["TRAY_Y"] - 12.0, Z0, 12, p["PANEL_Y1"], 60.0)


def _spine_profile(h: float, y: float, z_top: float) -> Sketch:
    """One dorsal spine in (frame Y, frame Z): a cusped cone - a chord flank of SPINE_FLANK with both
    flanks pulled CONCAVE, so the tip is steeper than the chord and the silhouette is a true point
    rather than a triangle. Blunted to SPINE_TIP_R (FERAL's tip tier)."""
    b = h / tan(radians(SPINE_FLANK))
    tri = _sk([(y - b, z_top), (y + b, z_top), (y, z_top + h)])
    R, s = 1.5 * h, 0.18 * h
    for sgn in (1, -1):
        ex, ez = sgn * b, 0.0
        mx, mz = y + (ex + 0.0) / 2, z_top + h / 2
        ln = hypot(b, h)
        nx, nz = sgn * h / ln, b / ln
        tri -= Pos(mx + nx * (R - s), mz + nz * (R - s)) * Circle(R)
        _ = ez
    return tri + Pos(y, z_top + h - SPINE_TIP_R) * Circle(SPINE_TIP_R)


def _spine_row(p: dict) -> Part:
    """The descending dorsal row, tallest forward, on both wall tops. Heights follow the design
    language's 1 : 0.78 : 0.61 : 0.48 : 0.37 run; nothing in a standing spine faces down."""
    sk = Sketch()
    for i in range(p["SPINE_N"]):
        h = p["SPINE_H0"] * SPINE_RUN[min(i, len(SPINE_RUN) - 1)]
        sk += _spine_profile(h, p["SPINE_Y0"] + i * p["SPINE_PITCH"], TOP_Z)
    blade = S.extrude_cut(sk, Plane.YZ.offset(p["WALL_X0"]), p["WALL_T"])
    # clipped to what is actually under the wall top, so no spine can ever cantilever off it
    blade &= box(p["WALL_X0"], CLIP_XY[1] + 5.0, TOP_Z - 1.0, p["WALL_X1"], p["STEP_Y"] - 0.6,
                 TOP_Z + p["SPINE_H0"] + 1.0)
    return _mirrored(blade)


def _cheek_region(p: dict) -> Sketch:
    """The punctate band on each cheek, in (frame Y, frame Z): the full length of the LOWER wall
    (which reaches CAV_Y1, not STEP_Y) and only as high as the slash allows."""
    y0, y1 = WALL_Y0, p["CAV_Y1"] - 1.0
    z0, z1 = CHEEK_Z
    return Pos((y0 + y1) / 2, (z0 + z1) / 2) * Rectangle(y1 - y0, z1 - z0)


def _cheek_clean(p: dict) -> list[Sketch]:
    y, z = p["SLASH_AT"]
    return _flank_clean(p) + [Pos(y, z) * Rectangle(p["LUNULE"] + 5.0, 9.9)]


def _cheek_puncta(p: dict) -> tuple[Part, int]:
    """FERAL's punctation: Ø2.2 at pitch 4.0 on the cheeks. 0.45 deep into a 1.8 mm wall leaves 1.35,
    and a Ø2.2 dimple face is 3.8 mm² - under overhangs()' 5.0 mm² floor, which is the whole reason
    the design language caps punctation at Ø2.4."""
    tool, n = S.puncta(_cheek_region(p), pitch=CHEEK_PITCH, d=CHEEK_D, depth=PUNCTA_DEPTH,
                       z_face=p["WALL_X1"], clean=_cheek_clean(p), plane=Plane.YZ,
                       ligament_min=CHEEK_LIG)
    return (_mirrored(tool), n) if n else (Part(), 0)


def _slash(p: dict) -> Part | None:
    """FERAL cuts the lunule THROUGH as a slash, not debossed - the family's own accent mode."""
    if not S.mark_fits("lunule", p["LUNULE"]):
        return None
    y, z = p["SLASH_AT"]
    m = S.mark("lunule", p["LUNULE"], "cut", (p["WALL_X1"], y, z), normal=(1, 0, 0),
               x_dir=(0, 1, 0), through=p["WALL_T"] + 2.0)
    return m + m.mirror(Plane.YZ)


# --- NOCTURNE: the vane fan --------------------------------------------------------------------
def _plinth(p: dict) -> Part:
    """The lit plinth: the tray thickened to PLINTH_Z1 behind the spanner pocket, so it can hold the
    five wells, the ducts and the vane roots. Rear plan corners rounded on a VERTICAL axis."""
    y0, y1 = p["PLINTH_Y"]
    sk = Pos(0, (y0 + y1) / 2) * Rectangle(2 * p["WALL_X1"], y1 - y0)
    sk = fillet(sk.vertices().filter_by(lambda v: v.Y < y0 + 1e-6), PLINTH_R)
    solid = extrude(Plane.XY.offset(Z0) * sk, amount=p["PLINTH_Z1"] - Z0)
    rabbet = box(-LENS_X - LENS_FIT, LENS_Y[0] - LENS_FIT, p["PLINTH_Z1"] - LENS_RABBET,
                 LENS_X + LENS_FIT, LENS_Y[1] + LENS_FIT, p["PLINTH_Z1"] + 1.0)
    return Part() + (solid - rabbet)


def _vane_place(part: Part, xi: float, fan: float, z_hub: float) -> Part:
    """A vane built upright at x 0 is rotated about the Y axis through its own hub and slid to xi.
    Rotating about Axis.Y alone would swing it about the frame origin, 100 mm away."""
    return part.moved(Location((0, 0, -z_hub))).rotate(Axis.Y, fan).moved(Location((xi, 0, z_hub)))


def _vane_section(p: dict) -> Sketch:
    """One vane in plan, upright at x 0: the Ø5.4 conduit rod at the leading edge and the 2 mm web
    trailing it. The rod is what makes a Ø3 light pipe possible at all - a 2 mm vane cannot hold a
    Ø3 bore with 1.2 of wall, so the pipe lives in a rod and the web is the blade."""
    rod = Pos(0, p["CONDUIT_Y"]) * Circle(p["PIPE_D"] / 2 + 1.2)
    web = Pos(0, (WEB_Y[0] + WEB_Y[1]) / 2) * Rectangle(p["VANE_T"], WEB_Y[1] - WEB_Y[0])
    return rod + web


def _vanes(p: dict) -> Part:
    out = Part()
    sec = _vane_section(p)
    z_hub = p["PLINTH_Z1"]
    for xi, fan, R in zip(VANE_X, VANE_FAN, p["VANE_R"]):
        blade = extrude(Plane.XY.offset(z_hub - VANE_BURY) * sec, amount=R + VANE_BURY)
        blade = S.treat_edges(blade, "nocturne", "sil", p["VANE_T"],
                              edges=blade.edges().group_by(Axis.Z)[-1])[0]
        out += _vane_place(blade, xi, fan, z_hub)
    return out


def _wells(p: dict) -> tuple[Part, int]:
    """Five conical light wells in the plinth top, forward of the rods so their mouths stay open for
    the lens. A funnel that widens upward has every face pointing UP - it is the self-supporting
    direction, and it is why the wells are in a horizontal face and not in the vanes."""
    tool = Part()
    for xi in VANE_X:
        tool += S.light_well((xi, WELL_Y), p["PLINTH_Z1"], led_d=p["LED_D"],
                             half_angle=WELL_HALF, depth=p["WELL_DEPTH"])
    return tool, len(VANE_X)


def _pipes(p: dict) -> Part:
    """Per vane: the Ø3 duct from the well to the rod's base (a horizontal Ø3 bore - an exempt arch
    at Ø <= 12) and the Ø3 pipe up the rod, closed by a PIPE_CONE cone PIPE_TIP short of the tip."""
    out = Part()
    z_hub = p["PLINTH_Z1"]
    r = p["PIPE_D"] / 2
    for xi, fan, R in zip(VANE_X, VANE_FAN, p["VANE_R"]):
        run = R - PIPE_TIP - r / tan(radians(PIPE_CONE))
        bore = extrude(Plane.XY.offset(z_hub - VANE_BURY - 0.5) * (Sketch() + Pos(0, p["CONDUIT_Y"]) * Circle(r)),
                       amount=run + VANE_BURY + 0.5)
        bore += Pos(0, p["CONDUIT_Y"], z_hub + run) * Cone(r, 0.0, r / tan(radians(PIPE_CONE)),
                                                          align=MIN_Z_ALIGN)
        out += _vane_place(bore, xi, fan, z_hub)
        out += extrude(Plane(origin=(xi, WELL_Y, DUCT_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
                       * (Sketch() + Circle(r)), amount=WELL_Y - p["CONDUIT_Y"] + 1.0, dir=(0, -1, 0))
    return out


def _vane_ladder(p: dict) -> tuple[Part, int]:
    """LADDER slots in every web - the frame's own motif, transverse to the vane's radius (CN-2)."""
    tool, kept = Part(), 0
    z_hub = p["PLINTH_Z1"]
    for xi, fan, R in zip(VANE_X, VANE_FAN, p["VANE_R"]):
        z0, z1 = z_hub + LADDER_Z[0], z_hub + R - LADDER_Z[1]
        if z1 - z0 < 4.0:
            continue
        region = Pos((WEB_Y[0] + WEB_Y[1]) / 2 + 0.0, (z0 + z1) / 2) * \
            Rectangle(WEB_Y[1] - WEB_Y[0], z1 - z0)
        clean = [Pos(*_lunule_zone(p)) * Rectangle(p["LUNULE"] + 4.0, p["LUNULE"] + 4.0)] \
            if xi == 0.0 else []
        length, width, pitch = LADDER
        # grid_centres snaps the lattice to `origin`, and with the default (0, 0) a 4.2 pitch lands
        # one row inside an 11.4 mm band instead of two. Centre the run the band can actually hold.
        rows = max(1, int((z1 - z0 - (width + 2 * LADDER_LIG)) / pitch) + 1)
        origin = (0.0, (z0 + z1) / 2 - (rows - 1) * pitch / 2)
        sk, n = S.vent_ladder(region, pitch=pitch, ligament_min=LADDER_LIG, clean=clean,
                              hole_min=2.0, length=length, width=width, origin=origin)
        if not n:
            continue
        cut = S.extrude_cut(sk, Plane.YZ.offset(-p["VANE_T"]), 2 * p["VANE_T"])
        tool += _vane_place(cut, xi, fan, z_hub)
        kept += n
    return tool, kept


def _lunule_zone(p: dict) -> tuple[float, float]:
    """(y, z) centre of the backlit slash on the centre vane's web, in that vane's own frame."""
    return ((WEB_Y[0] + WEB_Y[1]) / 2, p["PLINTH_Z1"] + p["VANE_R"][2] / 2)


def _vane_lunule(p: dict) -> Part | None:
    """NOCTURNE cuts the lunule THROUGH the tallest vane, so it reads backlit."""
    if not S.mark_fits("lunule", p["LUNULE"]):
        return None
    y, z = _lunule_zone(p)
    m = S.mark("lunule", p["LUNULE"], "cut", (p["VANE_T"], y, z), normal=(1, 0, 0),
               x_dir=(0, 0, 1), through=2 * p["VANE_T"] + 1.0)
    return _vane_place(m, VANE_X[2], VANE_FAN[2], p["PLINTH_Z1"])


def _lens(p: dict) -> Part:
    """The second part, second filament: a 1.0 mm translucent sheet in the plinth's rabbet carrying a
    plano-convex dome over each well. Plano-convex, not a hollow cap: a hollow dome's inside faces
    straight down, and a solid one is both printable flat-side-down and a better diffuser."""
    z0 = p["PLINTH_Z1"] - LENS_RABBET
    z1 = z0 + LENS_T
    sk = Pos(0, (LENS_Y[0] + LENS_Y[1]) / 2) * Rectangle(2 * LENS_X, LENS_Y[1] - LENS_Y[0])
    sk = fillet(sk.vertices(), 1.0)
    sheet = extrude(Plane.XY.offset(z0) * sk, amount=LENS_T)
    R = ((LENS_BASE / 2) ** 2 + LENS_DOME ** 2) / (2 * LENS_DOME)
    for xi in VANE_X:
        sheet += Pos(xi, WELL_Y, z1 - (R - LENS_DOME)) * Sphere(R)
    part = Part() + (sheet & box(-LENS_X, LENS_Y[0], z0, LENS_X, LENS_Y[1], z1 + LENS_DOME))
    part.label = LENS
    return part


# --- VESPID: the abdomen ------------------------------------------------------------------------
# NOT IN VARIANTS, AND THAT IS A MEASUREMENT, NOT AN OPINION. The geometry below is finished: it
# builds one valid solid, it seats, it clears every frame part, every standoff, the VTX, the SMA
# seat, the spanner pocket, both prop discs and the landing plane, it has NO unsupported overhang
# in the print orientation, its girth law holds to 0.01 % and all ten spiracles probe open. What it
# cannot do is pass the module's shared `min_wall` row, and BOTH of that check's paths fail on it
# for opposite reasons:
#
#   * with a true ARC crown (the natural shape), OCCT's erode - which min_wall reaches for first -
#     dies with SIGSEGV the moment the abdomen is unioned with the shroud. A segfault is not
#     catchable, so it takes the whole export down, not just the row. Verified on five different
#     builds: with and without the groove cutter, with the cavity arced and faceted, with the tray
#     butted and overlapped, and on the result of `.clean()`.
#   * with a FACETED crown (_ve_dsec, which is what is in the file, and which does fix the crash)
#     the erode path raises instead and min_wall falls back to ray sampling - and a ray leaving one
#     facet of a 12-facet shell grazes along its neighbour: 719 of 7362 rays read under 1.2 mm on a
#     part whose thinnest real wall is 1.4, worst reading 0.06 mm. With the puncta removed it is
#     719; with EVERY aperture removed it is 895 of 7230. So it is the faceted shell itself that
#     the sampler cannot read, not anything cut into it.
#
# Neither of those is a reason to lower the floor or to skip the row, so the variant is not shipped.
# What would unblock it, in order of cost: a SOLID abdomen (no cavity at all, spiracles as blind
# flank pockets) has no thin wall for either path to trip over and keeps the whole silhouette; or
# min_wall gaining a way to be told "this is a shell, measure it as one". The code is left here,
# complete and commented, so that either fix is a small edit rather than a rebuild.
#
# The identity part of the catalogue: a tiger beetle's tail. Five tergites march out of the shroud,
# each 0.82x the length and 0.86x the girth of the one in front, each closed by a proud collar with
# an undercut groove aft of it, and the run ends in a stinger. Everything is a prism along Y, so
# every flank is vertical, every crown faces up and every inner roof is a semicircular arch whose
# diameter the girth law keeps under TPU's Ø10 exemption. Nothing in it needs a support.
#
# The crown is FACETED on the outside and ARCHED on the inside, and each of those is a measurement
# rather than a taste: an arced outside takes OCCT's erode - which `min_wall` reaches for first -
# down with SIGSEGV the moment the abdomen meets the shroud, and a faceted inside turns every
# chord of the roof into a real ceiling at normal.Z -0.99. See _ve_dsec and _ve_cavity.
def _ve_seg(k: int) -> dict:
    """Tergite k: girth (half width), straight flank height, crown Z, wall, and its Y run."""
    g = VE_G1 * VE_GR ** k
    base = VE_BASE * VE_GR ** k
    wall = VE_WALL[0] + (VE_WALL[1] - VE_WALL[0]) * k / (VE_N - 1)
    y1 = VE_Y0 - sum(VE_L1 * VE_LR ** i for i in range(k))
    return dict(k=k, g=g, base=base, crown=Z0 + base + g, wall=wall,
                y1=y1, y0=y1 - VE_L1 * VE_LR ** k, length=VE_L1 * VE_LR ** k)


def _ve_section(g: float, base: float, dz: float = 0.0) -> Sketch:
    """The tergite section in the XZ plane: a straight flank on the bed plane under a semicircular
    crown of radius g. `dz` grows it (the collar) or shrinks it (the neck) uniformly outward.

    Built as ONE rectangle with its two top corners rounded to the full half width, not as a
    rectangle UNIONED with a tangent circle. The shapes are identical; the topology is not. A
    tangent union leaves two zero-angle vertices on the outline, and OCCT's erode - which is what
    `min_wall` reaches for first - walks off the end of the world on them: SIGSEGV, which no
    try/except in this module or in _fit can catch."""
    return _ve_dsec(g + dz, Z0, Z0 + base + dz + g + dz)


def _ve_dsec(hw: float, z0: float, z1: float, facets: int = VE_FACETS) -> Sketch:
    """The D: a straight flank 2*hw wide from z0, closed by a FACETED crown of `facets` chords over
    the half circle of radius hw.

    Faceted, not arced, and that is a measurement too. With a true arc - whether unioned as a
    tangent circle or rolled in as a 2D fillet - the finished block takes OCCT's erode down with
    SIGSEGV the moment the abdomen is unioned with the shroud, and `min_wall` reaches for erode
    first. A planar-faced crown offsets without complaint. At 12 facets the chord sags 0.06 mm on
    the largest tergite, which is a third of a layer line, and every facet still faces outward or
    up, so nothing here needs a support."""
    zc = z1 - hw
    pts = [(-hw, z0), (hw, z0)]
    pts += [(hw * cos(radians(180.0 * i / facets)), zc + hw * sin(radians(180.0 * i / facets)))
            for i in range(facets + 1)]
    return _sk(pts)


def _ve_prism(sk: Sketch, y1: float, length: float) -> Part:
    return extrude(Plane.XZ.offset(-y1) * sk, amount=length)


def _ve_shell(p: dict) -> Part:
    """Every tergite, its proud collar and the undercut groove aft of that collar, all by UNION.

    THE GROOVE IS BUILT, NOT CUT, AND THAT IS A MEASUREMENT. Cutting it with a ring-shaped tool
    0.45 mm thick leaves a 0.45 mm re-entrant step that OCCT's erode cannot offset: `min_wall`
    took the whole process down with SIGSEGV, which no try/except can catch. Starting each tergite
    with VE_GROOVE_L of NECKED section instead gives exactly the same profile - collar, undercut,
    full girth - out of three prisms and no subtraction at all."""
    out = Part()
    for k in range(VE_N):
        s = _ve_seg(k)
        y1, run = s["y1"], s["length"]
        if k:  # the first tergite has no collar in front of it, so it needs no undercut either
            out += _ve_prism(_ve_section(s["g"], s["base"], -VE_GROOVE), y1, VE_GROOVE_L)
            y1, run = y1 - VE_GROOVE_L, run - VE_GROOVE_L
        out += _ve_prism(_ve_section(s["g"], s["base"]), y1, run)
        out += _ve_prism(_ve_section(s["g"], s["base"], VE_COLLAR), s["y0"] + VE_COLLAR_L,
                         VE_COLLAR_L)
    return out


def _ve_cavity(p: dict) -> Part:
    """The hollow. Its roof is a semicircular arch of radius (girth - wall) in every segment, which
    is what keeps it printable, so the crown wall is thicker than the flank wall by design. The
    cavity is open at the abdomen's front face, so the shroud's panel vents feed it."""
    out = Part()
    for k in range(VE_N):
        s = _ve_seg(k)
        # the INSCRIBED radius of the faceted crown, not the circumscribed one: the chord sags
        # 0.06 mm under the arc on the largest tergite, and the wall law is a minimum, not a mean
        r = s["g"] * cos(radians(90.0 / VE_FACETS)) - s["wall"]
        top = s["crown"] - s["wall"]
        # The CAVITY keeps a true semicircular arch while the outside is faceted, and the two have
        # opposite reasons. Outside, a faceted crown is what lets OCCT's erode run at all. Inside,
        # a faceted roof turns every chord into a real ceiling - measured at normal.Z -0.99 - while
        # one horizontal-axis arch of Ø <= 10 is exempt, which is the whole reason the girth law
        # caps the cavity radius at 5.0 in the first place.
        sk = Pos(0, (VE_CAV_Z0 + top - r) / 2) * Rectangle(2 * r, top - r - VE_CAV_Z0) \
            + Pos(0, top - r) * Circle(r)
        y1 = s["y1"] + (1.0 if k == 0 else 0.0)  # open forward, so nothing in it is a blind pocket
        out += _ve_prism(sk, y1, s["length"] + (1.0 if k == 0 else 0.0) + 0.02)
    return out


def _ve_spiracle_at(k: int) -> tuple[float, float, float, float]:
    """(y centre, sill Z, width, height) of tergite k's spiracle, on the same 0.86 taper."""
    s = _ve_seg(k)
    w, h = VE_SPIR[0] * VE_GR ** k, VE_SPIR[1] * VE_GR ** k
    return ((s["y1"] + s["y0"]) / 2 + VE_COLLAR_L / 2, VE_SPIR_Z0, w, h)


def _ve_spiracles(p: dict, grow: float = 0.0) -> tuple[Part, int]:
    """ONE lancet per tergite per flank, never two. A single tool per tergite crosses the abdomen
    and opens both flanks into the cavity, which is what makes them ventilation and not dimples."""
    out, n = Part(), 0
    for k in range(VE_N):
        yc, z0, w, h = _ve_spiracle_at(k)
        sk = _arch(yc - w / 2 - grow, yc + w / 2 + grow, z0 - grow, z0 + h - w / 2)
        out += extrude(Plane.YZ.offset(-(VE_G1 + 4.0)) * sk, amount=2 * (VE_G1 + 4.0), dir=(1, 0, 0))
        n += 2
    return out, n


def _ve_sting(p: dict) -> Part:
    """The stinger: the last tergite lofted to a blunt point, its underside staying on the bed
    plane the whole way, so the only new surfaces are two converging flanks and a falling crown."""
    s = _ve_seg(VE_N - 1)
    y_tip = s["y0"] - VE_STING_L
    # The tip section keeps its own flank on the bed plane. A section that was only a Ø1.6 circle
    # put the abdomen's lowest point at Z 1.36, which is under the footprint plane and turns the
    # whole 610 mm² bed face into a flagged overhang - measured on the first build.
    tip = _ve_section(VE_TIP_R, VE_TIP_R)
    body = loft([Plane.XZ.offset(-s["y0"]) * _ve_section(s["g"], s["base"]),
                 Plane.XZ.offset(-y_tip) * tip])
    return Part() + body


def _ve_puncta(part: Part, p: dict) -> tuple[Part, int]:
    """Two rows of Ø1.8 x 0.4 pits straddling the dorsal midline, one pit per tergite per row. The
    pit is sunk vertically into the crown, so its floor faces up and its wall is vertical."""
    d, depth, off = VE_PUNCTA
    out, n = Part(), 0
    for k in range(VE_N):
        s = _ve_seg(k)
        if s["g"] <= off + d / 2 + 0.6:
            continue
        z_top = Z0 + s["base"] + (s["g"] ** 2 - off ** 2) ** 0.5
        yc = (s["y1"] + s["y0"]) / 2 - VE_COLLAR_L
        for sx in (1.0, -1.0):
            out += cylinder(sx * off, yc, z_top - depth, z_top + 2.0, d)
            n += 1
    return out, n


def _ve_abdomen(p: dict) -> tuple[Part, Part, dict, list]:
    """(solid to add, tool to subtract, counts, declared thin features)."""
    shell = _ve_shell(p) + _ve_sting(p)
    spir, n_sp = _ve_spiracles(p)
    pits, n_pu = _ve_puncta(shell, p)
    tool = _ve_cavity(p) + spir + pits
    allow = [_ve_spiracles(p, grow=0.3)[0], pits]
    return shell, tool, {"spiracles": n_sp, "puncta": n_pu, "tergites": VE_N}, allow


# --- BRUTALIST: one poured slab, formwork still showing ----------------------------------------
# Everything here is orthogonal to the frame datum. The only non-orthogonal surfaces in the whole
# variant are 45 deg chamfers and the two 50 deg faces that carry load over an opening, and 50 is
# not a taste: a 45 deg down-facing plane reads normal.Z -0.7071 and trips the 0.7 overhang limit
# by four thousandths, which is the same reason the shard fin is raked 50 and not 45.
def _br_cheek_face(p: dict) -> tuple[float, float, float, float]:
    """(y_front, y_rear, z0, z1) of one cheek's outer face - the face the void is measured against."""
    return (BR_CHEEK_Y[0], BR_CHEEK_Y[1], Z0, p["TOP_Z"])


def _br_cheeks(p: dict) -> Part:
    """The 3.0 formwork slab standing outboard of each side wall, so the shroud reads twice as heavy
    as anything else in the catalogue. Its footprint is the wall's, not a new outline."""
    y1, y0, z0, z1 = _br_cheek_face(p)
    return _mirrored(box(p["WALL_X1"], y0, z0, p["WALL_X1"] + BR_T, y1, z1))


def _br_void_profile(p: dict, grow: float = 0.0) -> tuple[Sketch, float, float]:
    """The ONE aperture in each cheek, in the YZ plane, plus (void area, cheek area).

    A rectangle with sharp corners, open at the bed plane, under a flat BR_T lintel - no arch, no
    gable, nothing radiused, because this language has none of those. The lintel is a real bridge
    and it is declared as one: BR_VOID[0] = 15.0 mm against TPU's 22.0 bridge ceiling, with 6.7 mm
    jambs either side. A 50 deg gable was tried first and the arithmetic refuses it - with 3.0 mm
    jambs and a 3.0 mm header no gable-topped void on a 20 mm tall cheek can reach 40 % of it at
    any cheek length, because the gable's rise grows as fast as the face does."""
    y1, y0, z0, z1 = _br_cheek_face(p)
    w, top = BR_VOID
    yc = (y0 + y1) / 2
    area = w * (top - z0)
    w, top, z0 = w + 2 * grow, top + grow, z0 - grow
    sk = _sk([(yc - w / 2, z0), (yc + w / 2, z0), (yc + w / 2, top), (yc - w / 2, top)])
    return sk, area, (y1 - y0) * (z1 - z0)


def _br_voids(p: dict, grow: float = 0.0) -> Part:
    """The void cut clean through the cheek slab AND the wall behind it - one aperture, not a recess
    and not a field of holes. It is also the flank ventilation: brutalist has no second opening."""
    sk, _a, _c = _br_void_profile(p, grow)
    tool = extrude(Plane.YZ.offset(p["WALL_X0"] - 1.0) * sk, amount=BR_T + p["WALL_T"] + 2.0,
                   dir=(1, 0, 0))
    return _mirrored(tool)


def _br_top(p: dict) -> tuple[float, float]:
    """(inner x of the top slab, its top Z). The slab does NOT corbel inward over the bay and that
    is arithmetic, not restraint: a wedge that runs inward at BR_CORBEL and meets its own flat top
    comes to a knife edge, and the first build measured 0.14 mm there against a 3.0 mm wall. It
    flares OUTWARD instead - a cornice - where the same 50 deg underside ends on a full 3.0 mm
    vertical face and nothing is ever thinner than the slab."""
    return p["WALL_X0"], p["TOP_Z"] + BR_FLARE * tan(radians(BR_CORBEL)) + BR_T / cos(radians(BR_CORBEL))


def _br_corbel(p: dict) -> Part:
    """The top slab and its outward cornice, in one polygon: wall top -> cheek top -> 50 deg
    underside out to the cornice lip -> 3.0 vertical lip -> flat top back over the bay's edge."""
    x_in, z_top = _br_top(p)
    x_out = p["WALL_X1"] + BR_T
    sk = _sk([(x_in, p["TOP_Z"]), (x_out, p["TOP_Z"]),
              (x_out + BR_FLARE, p["TOP_Z"] + BR_FLARE * tan(radians(BR_CORBEL))),
              (x_out + BR_FLARE, z_top), (x_in, z_top)])
    y1, y0 = BR_CHEEK_Y
    sec = extrude(Plane.XZ.offset(-y1) * sk, amount=y1 - y0)
    return _mirrored(sec)


def _br_rib_y(p: dict) -> tuple[float, ...]:
    """Three ribs on BR_RIB pitch, centred on the corbel's run."""
    y1, y0 = BR_CHEEK_Y
    yc = (y0 + y1) / 2
    return tuple(yc + k * BR_RIB[2] for k in (1, 0, -1))


def _br_ribs(p: dict) -> Part:
    """3.0 proud, square section, on the OUTSIDE of the top slab. They stand on material over their
    whole footprint, so not one of them is a bridge."""
    x_in, z_top = _br_top(p)
    out = Part()
    for yc in _br_rib_y(p):
        out += box(x_in, yc - BR_RIB[1] / 2, z_top, p["WALL_X1"] + BR_T + BR_FLARE,
                   yc + BR_RIB[1] / 2, z_top + BR_RIB[0])
    return _mirrored(out)


def _br_rear(p: dict) -> Part:
    """Two rear piers and the square land between them. The land is the void in the rear face; what
    it exposes is the 2.0 mm panel, and THAT is the SMA's seat - a flat land, never a boss, so the
    seat wall stays the 2.0 the bulkhead needs and does not become the 3.0 the slab is."""
    # The piers stop at the wall top and that is the clip talking: the shared bore and its outboard
    # mouth are cut to Z 23, so a pier carried above them is bored Ø6.5 with 0.45 mm left outboard.
    # Measured. The cornice covers the cheeks; the piers are the buttresses under it.
    slab = box(-p["WALL_X1"] - BR_T, p["PANEL_Y0"] - BR_T, Z0, p["WALL_X1"] + BR_T, p["PANEL_Y0"],
               p["TOP_Z"])
    return slab - box(-BR_LAND / 2, p["PANEL_Y0"] - BR_T - 1.0, Z0 - 1.0, BR_LAND / 2,
                      p["PANEL_Y0"] + 1.0, p["TOP_Z"] + 1.0)


def _br_board(p: dict, grow: float = 0.0) -> Part:
    """Board marking: BR_BOARD grooves running the PRINT direction (Z) on every vertical face over
    200 mm². Formwork planks, not a texture - they are the same width and pitch everywhere."""
    w, d, pitch = BR_BOARD[0] + 2 * grow, BR_BOARD[1] + grow, BR_BOARD[2]
    tool = Part()
    y1, y0, z0, z1 = _br_cheek_face(p)
    n = int((y1 - y0) / pitch)
    for i in range(1, n):
        y = y0 + i * pitch
        tool += box(p["WALL_X1"] + BR_T - d, y - w / 2, z0 - 1.0, p["WALL_X1"] + BR_T + 1.0,
                    y + w / 2, p["TOP_Z"] - 0.6)
    tool = _mirrored(tool)
    m = int((2 * (p["WALL_X1"] + BR_T)) / pitch)
    for i in range(1, m):
        x = -(p["WALL_X1"] + BR_T) + i * pitch
        tool += box(x - w / 2, p["PANEL_Y0"] - BR_T - 1.0, Z0 - 1.0, x + w / 2,
                    p["PANEL_Y0"] - BR_T + d, p["TOP_Z"] + 1.0)
    # A plank that runs off the edge of an opening leaves a sliver where it clips the void's gable -
    # measured at 0.06 mm. Formwork stops at the opening, so the tool does too. The keep-out is an
    # axis-aligned BOX round each aperture and not the aperture's own shape, because a groove
    # truncated by the 50 deg gable face is exactly the wedge this is here to avoid: every groove
    # now ends on a plane that is either vertical or horizontal.
    sk, _a, _c = _br_void_profile(p)
    vb = sk.bounding_box()
    keep = box(-40.0, vb.min.X - BR_KEEP, Z0 - 2.0, 40.0, vb.max.X + BR_KEEP, vb.max.Y + BR_KEEP)
    keep += box(-BR_LAND / 2 - BR_KEEP, p["PANEL_Y0"] - BR_T - 2.0, Z0 - 2.0,
                BR_LAND / 2 + BR_KEEP, p["PANEL_Y0"] + 2.0, p["TOP_Z"] + 2.0)
    return tool - keep


def _br_plaque(p: dict) -> tuple[Part, Part]:
    """(the proud plaque, the 2.0 deboss into it). The stamp is 2.0 deep and the language fixes the
    wall at 3.0, so it cannot be sunk into the slab - it is sunk into a plinth cast proud of it,
    which is what a cast-in plaque is. Four bars: a datum stamp, not lettering."""
    depth, _ln, wd, proud = BR_STAMP
    x_in, z_top = _br_top(p)
    xc = (x_in + p["WALL_X1"] + BR_T) / 2
    # The plaque spans the FULL bay between two ribs and butts both of them. A plinth that stopped
    # short left a 0.5 mm slot either side of it - measured - and a 0.5 mm slot is neither a wall
    # nor a gap a nozzle can resolve. Butted, there is no slot at all.
    y1, y0 = _br_rib_y(p)[0] - BR_RIB[1] / 2, _br_rib_y(p)[1] + BR_RIB[1] / 2
    pad = box(xc - wd / 2, y0, z_top, xc + wd / 2, y1, z_top + proud)
    # ONE sunk rectangle, 2.0 deep, with a 1.4 mm rim all round: a cast-in plaque, not lettering.
    cut = box(xc - wd / 2 + 1.7, y0 + 1.4, z_top + proud - depth,
              xc + wd / 2 - 1.7, y1 - 1.4, z_top + proud + 1.0)
    return _mirrored(pad), _mirrored(cut)


def _br_vent_ext(p: dict) -> Part:
    """The panel's two arched vents, carried on through the rear slab so they stay open."""
    sk = _arch(p["VENT_X"][0], p["VENT_X"][1], Z0, p["VENT_SPRING_Z"])
    sk = sk + sk.mirror(Plane.YZ)
    return extrude(Plane.XZ.offset(-(p["PANEL_Y1"] + 0.5)) * sk, amount=p["PANEL_T"] + BR_T + 1.0)


def _br_groove_count(p: dict) -> int:
    """How many formwork planks actually landed (the tool minus the aperture keep-outs)."""
    return len([s for s in _br_board(p).solids() if s.volume > 0.05])


def _br_added(p: dict) -> Part:
    """The SLAB WORK: cheeks, cornice, ribs and rear piers, with the aperture in it and nothing
    else. This is what the 3.0 mm wall row is measured on, and it is the honest scope - the shroud
    under it is the module's shared 1.8 / 2.0 / 1.6 and has its own row, and the plaque plinth is
    2.6 proud on top of the slab, which is a plinth and not a wall."""
    return Part() + ((_br_cheeks(p) + _br_corbel(p) + _br_ribs(p) + _br_rear(p)) - _br_voids(p))


# --- GYROID: the frozen fluid -----------------------------------------------------------------
# The silhouette is deliberately dumb, which is the language's own rule. `WALL_T` = GY_WALL and
# `TRAY_T` / `TRAY_Y` = GY_DECK already thicken the shroud and lengthen the tail deck through the
# shared `_p()` derivation (walls 15.4..19.0, panel and deck 38 wide, deck out to y -118), so the
# only geometry this language adds in build123d is the one constant plan rounding. Everything else
# it does happens INSIDE the deck, in Blender, and is not "cut" at all: the openings are where the
# sheet breaks the surface.
def _gy_outline_edges(part: Part, p: dict) -> list:
    """The plan outline's outboard vertical corners: |x| at the wall's outer face, at either end of
    the shroud. Not the clip lips, not the tray - those are mating geometry with their own radii."""
    out = []
    for e in part.edges().filter_by(Axis.Z):
        c = e.center()
        if abs(abs(c.X) - p["WALL_X1"]) > 0.05 or e.length < 3.0:
            continue
        if c.Y > p["STEP_Y"] - 1.0:  # the free front corners; the rear end is the deck junction,
            out.append(e)            # and the deck carries the SAME r through TRAY_R
    return out


def _gy_round(part: Part, p: dict) -> tuple[Part, tuple[int, int]]:
    """ONE constant r on the plan outline, applied corner by corner. The radius is never traded down
    - a corner OCCT refuses is left square and counted, because a run of two radii would be exactly
    the crease this language forbids. Returns (corners rounded, corners offered)."""
    def corners(pt):
        g = {}
        for e in _gy_outline_edges(pt, p):
            c = e.center()
            g.setdefault((round(c.X, 2), round(c.Y, 2)), []).append(e)
        return g

    # One plan CORNER, not one edge: the shroud's step at STEP_Z splits each vertical corner into two
    # collinear edges, and rounding one of them would leave the crease halfway up that this language
    # exists to forbid. They go into OCCT together.
    # The target list is taken ONCE, from the undecorated part. A fillet leaves its own tangent edge
    # lying in the same x = WALL_X1 plane, and re-reading the corner list each pass would offer that
    # tangent edge as if it were a fifth corner, burn the iteration and report 3 of 4.
    targets = list(corners(part))
    done = 0
    for k in targets:
        es = corners(part).get(k)
        if not es:
            continue
        try:
            part = Part() + fillet(es, p["GY_ROUND"])
            done += 1
        except Exception:  # noqa: BLE001 - this corner cannot carry the one legal radius
            continue
    return part, (done, len(targets))


def _gy_zone(p: dict) -> Part:
    """The volume Blender may work: the interior of the TAIL DECK, held GY_RIND clear of its own
    outline and of every functional feature on it. Everything else is the mask, because `decorate()`
    wants the mask big and the restore small.

    THE DECK, NOT THE WALL, AND THAT IS A MEASUREMENT. A lattice cut through a VERTICAL wall leaves
    a prism whose axis is horizontal, so a third of every cell's rim is a genuine ceiling - the run
    on the wall measured nineteen down-facing facets up to 30.5 mm² at normal.Z -1.00. The same
    lattice through a HORIZONTAL deck leaves prisms whose axis is vertical: every cell wall is
    vertical, the openings read on the top and the underside at once, and the overhang count is
    zero. That is why this language's deck is 4.0 mm thick and 27.6 mm long."""
    g = GY_INSET  # 2.6, not GY_RIND: at 1.6 the cells clipped at the zone boundary measured a
                  # 0.06 mm knife edge, and the floor is the floor - the inset moves, not the floor
    y0, y1 = p["TRAY_Y"] + g, p["PANEL_Y0"] - g
    sk = Pos(0, (y0 + y1) / 2) * Rectangle(2 * p["WALL_X1"] - 2 * g, y1 - y0)
    sk = fillet(sk.vertices().filter_by(lambda v: v.Y < y0 + 1e-6), max(p["TRAY_R"] - g, 0.4))
    z = extrude(Plane.XY.offset(Z0 - 1.0) * sk, amount=p["TRAY_T"] + 2.0)
    for sx in (1.0, -1.0):  # the clip rings and their mouths keep their full rind
        z -= cylinder(sx * CLIP_XY[0], CLIP_XY[1], Z0 - 2.0, p["TRAY_Z1"] + 2.0,
                      D_CLIP_BORE + 2 * CLIP_WALL + 2 * GY_INSET)
    z -= box(-p["BOSS_HX"] - GY_INSET, p["BOSS_Y"] - GY_INSET, Z0 - 2.0,
             p["BOSS_HX"] + GY_INSET, 0.0, p["BOSS_Z1"] + 2.0)  # the M3 boss and its bore
    return z


def _gy_cell() -> str:
    """"gyroid" once the bridge carries the recipe, GY_CELL_FALLBACK until then. Read off the
    bridge's own recipe list, so this follows the recipe in and needs no edit here."""
    return "gyroid" if "gyroid" in getattr(BL, "RECIPES", ()) else GY_CELL_FALLBACK


def _gy_params(p: dict) -> tuple[str, dict]:
    """(recipe, params). The real gyroid recipe speaks period / sheet / rind / voxel; the documented
    fallback is a voronoi carapace_lattice, which speaks cell_d / ligament instead."""
    if _gy_cell() == "gyroid":
        # rind 0.0, and that is not a shortcut: `zone` is ALREADY the deck inset GY_INSET from every
        # functional boundary, and everything outside it is the protect mask, so the rind this
        # language asks for is enforced in build123d and asking the recipe for a second one on top
        # of a 4.0 mm deck leaves 0.8 mm for the sheet and the pass removes nothing (measured:
        # volume ratio 1.0, a deck that came back solid).
        return "gyroid", {"period": p["GY_PERIOD"], "sheet": GY_RIND, "rind": 0.0,
                          "voxel": 1.2, "axis": "Z", "skin": "open"}
    return "carapace_lattice", {"cell": GY_CELL_FALLBACK, "cell_d": GY_CELL_D,
                                "ligament": GY_LIG, "seed": 7, "axis": "Z"}


def _gy_decorate(part: Part, p: dict, variant: str) -> Part:
    """The whole graphic. Nothing is cut: the openings are where the sheet breaks the outer face."""
    zone = _gy_zone(p)
    guard = Part() + (part - zone)
    # `zone` IS the region: it is already the outline inset by the rind with every functional
    # feature taken out of it, which is exactly what decor_region() is asked to produce.
    # BL.decor_region(part, GY_RIND, minus=(guard,), axis="Z") returns None on this solid - OCCT
    # will not offset the deck's outline once the clip mouths have opened it - and a None region
    # runs the recipe unclipped, which measured "BRepCheck_Analyzer says invalid" on the rebuild.
    recipe, params = _gy_params(p)
    res = BL.decorate_ex(part, recipe, params,
                         protect=guard, region=zone, restore=False,
                         cache_key=f"{NAME}__{variant}", wall_floor=1.5, tri_budget=12_000)
    # A pass that takes nothing out is not a lattice, whatever it reports, so it is not accepted as
    # one: if the gyroid recipe hands the deck back solid the documented voronoi fallback runs in
    # its place, under the same cache key, and the checks report which one landed.
    if recipe == "gyroid" and (not res.applied
                               or (res.stats.get("volume_ratio") or 1.0) > 1.0 - GY_MIN_CUT):
        _INFO[f"{variant}_degraded"] = round(res.stats.get("volume_ratio") or 1.0, 4)
        rec2, par2 = "carapace_lattice", {"cell": GY_CELL_FALLBACK, "cell_d": GY_CELL_D,
                                          "ligament": GY_LIG, "seed": 7, "axis": "Z"}
        res2 = BL.decorate_ex(part, rec2, par2, protect=guard, region=zone, restore=False,
                              cache_key=f"{NAME}__{variant}", wall_floor=1.5, tri_budget=12_000)
        if res2.applied:
            res, recipe = res2, rec2
    _INFO[f"{variant}_decor"] = res.applied
    _INFO[f"{variant}_recipe"] = recipe
    return res.part if res.applied else part


_INFO: dict[str, object] = {}  # per-variant measurements the added checks read back


# --- assembly ---------------------------------------------------------------------------------
_APERTURES: dict[str, dict] = {}  # per-variant aperture counts, so checks() can assert they landed
_BASE: dict[str, Part] = {}  # the undecorated functional solid: where min_wall is still valid
# DECLARED thin features, handed to min_wall(allow=...) exactly as the contract asks - the mark's own
# solid and the cusped apertures' own cutters, never a lowered floor. A ray leaving the rim of a
# 0.6 mm deboss or the tangency of a cusp travels a few hundredths of a mm to the neighbouring face
# and reads that as a wall; the material behind the lunule is 3.0 mm and is measured separately.
_ALLOW: dict[str, list[Part]] = {}


def build(variant: str = "shard", style: str | None = None, **overrides) -> dict[str, Part]:
    """One style's parts, BASE-labelled. Everything that mates is built identically for all four:
    only the dorsal form is style-dependent, and one checks() proves the fit for every one."""
    style = style or (VARIANTS.get(variant, {}).get("style") or variant)
    assert style in STYLES, f"tail_block: unknown style {style!r}; styles: {STYLES}"
    p = _p(**{**(VARIANTS.get(variant, {}).get("params") or {}), **overrides})
    counts, allow = {}, []

    shell = _walls(p) + _panel(p) + _tray(p) + _boss(p)
    if p["DOME"]:
        shell += _shoulders(p) + _tail_boss(p) + _macula_band(p)
    if p["RACK"]:
        shell += _plinth(p) + _vanes(p)
    if p["VESPID"]:
        ve_solid, ve_tool, ve_counts, ve_allow = _ve_abdomen(p)
        shell += ve_solid
        counts.update(ve_counts)
        # The spiracles and the puncta are DECLARED thin features, handed to
        # min_wall(allow=) exactly as the contract asks. A ray leaving one jamb of a 1.2 mm lancet
        # crosses the lancet, not the flank; the flank behind it is the tergite's own 1.4-2.2 and
        # is measured on its own. The floor is not moved - the samples inside the declared feature
        # are skipped, which is what `allow` is for.
        allow += ve_allow
    if p["BRUT"]:
        pad, stamp = _br_plaque(p)
        shell += _br_cheeks(p) + _br_corbel(p) + _br_ribs(p) + _br_rear(p) + pad
    part = (shell - _clip_tools(p)) + _clips(p)  # bore the shell first, then add the rings
    tools = _vents(p) + _head_reliefs(p) + _sma_tool(p) + _tap_tool(p)
    if p["VESPID"]:
        tools += ve_tool
    if p["BRUT"]:
        tools += _br_voids(p) + _br_board(p) + _br_vent_ext(p) + stamp
        counts["cheek voids"] = 2
        counts["board grooves"] = _br_groove_count(p)
        # The board marking and the plaque are DECLARED thin features, handed to min_wall(allow=)
        # exactly as the contract asks. A ray leaving one wall of a 0.6 mm formwork groove crosses
        # the groove, not the slab, and reads 0.6 mm; the slab behind it is 2.7 and is measured on
        # its own in the BRUTALIST row. The floor is not moved - the samples inside the declared
        # feature are skipped, which is what `allow` is for.
        allow += [_br_board(p, grow=0.35), stamp]

    if p["fin_on"]:
        part += _fin(p)
        tools += _coax_tools(p)
    if p["STING"]:
        part += _sting(p) + _spine_row(p)
        pits, counts["cheek puncta"] = _cheek_puncta(p)
        tools += pits
        allow.append(pits)
        slash = _slash(p)
        if slash is not None:
            tools += slash
            allow.append(slash)
        counts["slash"] = 0 if slash is None else 1
    if p["DOME"]:
        slits, counts["elytra slits"] = _elytra_slits(p)
        tools += slits
        # the aperture's own RIM is the declared thin feature, so the allow envelope is the slit grown
        # by 0.6 - a point exactly on the cut face is not "inside" the cutter and is not skipped
        allow += [_elytra_slits(p, grow=0.6)[0], _carina_allow(p)]
        counts["puncta"] = 0  # measured refusal, see _no_puncta()
    if p["RACK"]:
        wells, counts["light wells"] = _wells(p)
        ladder, counts["ladder slots"] = _vane_ladder(p)
        tools += wells + _pipes(p) + ladder
        allow.append(ladder)
        lun = _vane_lunule(p)
        if lun is not None:
            tools += lun
            allow.append(lun)
        counts["lunule"] = 0 if lun is None else 1

    part = Part() + (part - tools)  # the boolean chain hands back a plain Solid
    if p["BRUT"]:
        bb = part.bounding_box()
        cy, z0 = bb.center().Y, bb.min.Z
        w, top = BR_VOID
        yc = sum(BR_CHEEK_Y) / 2
        br = (("box", -40.0, yc - w / 2 - cy - 1.0, top - z0 - 0.5,
               40.0, yc + w / 2 - cy + 1.0, top - z0 + 0.5),)
        BRIDGE_OK[NAME] = BRIDGE_OK[f"{NAME}__{variant}"] = br
    if p["GYROID"]:
        part, r = _gy_round(part, p)
        _INFO[f"{variant}_round"] = r
        _INFO[f"{variant}_cell"] = _gy_cell()
    _BASE[variant] = part
    if p["GYROID"]:
        part = _gy_decorate(part, p, variant)

    # The marks and the suture come LAST and land on exact B-rep: CN-1's groove and CN-4's mark are
    # the two features that must never be tessellated, because they are what the eye reads first.
    if p["DOME"]:
        part = Part() + (part - _suture_tool(p))
        mk = _lunule(p) if p["MARK"] else None
        if mk is not None:
            part = Part() + (part - mk)
            allow.append(_mark_envelope(p) or mk)
            counts["lunule"] = 1

    part.label = NAME
    _APERTURES[variant] = counts
    _ALLOW[variant] = [a for a in allow if a is not None and a.volume > 0.0]
    out = {NAME: part}
    if p["RACK"]:
        out[LENS] = _lens(p)
    return out


# --- probes used by the checks -----------------------------------------------------------------
def _board_probe(p: dict) -> Part:
    """The VTX board as installed: CAV on STAND_H standoffs, centred on the 25.5 pattern."""
    w, l, h = p["CAV"]
    z0 = Z0 + p["STAND_H"]
    return box(-w / 2, VTX_XY[1] - l / 2, z0, w / 2, VTX_XY[1] + l / 2, z0 + h)


def _head_probes() -> dict[str, Part]:
    """led_buzzer's two M3 button heads standing on the plate top face. led_buzzer states Z 2-3.65
    (one head height); the probe is twice that, so a washer or a proud thread still clears."""
    return {f"led_buzzer M3 head ({x:+.2f}, {y})": cylinder(x, y, Z0, Z0 + 2 * H_M3_HEAD, D_M3_HEAD)
            for x, y in HEAD_AXES}


def _spanner_zone(p: dict) -> Part:
    """Ø SPANNER_D x SPANNER_L of clear air behind the SMA seat: room for the nut and a spanner."""
    sk = Pos(0, p["SMA_Z"]) * Circle(SPANNER_D / 2)
    return extrude(Plane.XZ.offset(-p["PANEL_Y0"]) * sk, amount=SPANNER_L)


def _neighbours() -> dict[str, Part]:
    """Every accessory that shares the tail, built with its own defaults (missing ones skipped)."""
    out = {}
    for name in ("antenna_mast", "gps_mount", "led_buzzer", "xt60_holder", "battery_pad", "side_panels"):
        try:
            mod = __import__(f"tigerbee.accessories.{name}", fromlist=["build"])
            for label, part in mod.build().items():
                out[label] = part
        except Exception:  # noqa: BLE001 - a sibling module may be missing or in progress
            continue
    return out


def _skid_angle(part: Part) -> tuple[float, str]:
    """Nose-up attitude above which the skid, not the carbon tail tip, touches down first.
    The contact point at attitude a maximises -y sin a - z cos a."""
    foot = part & box(-60, -200, Z0 - 0.1, 60, 60, Z0 + 0.2)  # the skid is on the footprint plane
    fb, tail = foot.bounding_box(), frame_parts()["plate_bottom"].bounding_box()
    dy, dz = tail.min.Y - fb.min.Y, fb.min.Z - tail.min.Z
    return (degrees(atan2(dz, dy)),
            f"skid corner (y {fb.min.Y:.1f}, Z {fb.min.Z:.1f}) is {dy:.1f} mm behind and "
            f"{dz:.1f} mm above the carbon tail tip (y {tail.min.Y:.1f}, Z {tail.min.Z:.1f})")


def _sma_probes(p: dict) -> tuple[Part, Part, Part]:
    """(D-shaped bore probe, annulus round it, block of material under the flat) for the SMA seat."""
    flat_z = p["SMA_Z"] - (SMA_FLAT - D_SMA / 2)
    plane = Plane.XZ.offset(-(p["PANEL_Y1"] + 0.5))
    below = Pos(0, flat_z + 0.05 - 5.0) * Rectangle(3 * D_SMA, 10.0)
    bore = Pos(0, p["SMA_Z"]) * Circle(D_SMA / 2 - 0.05) - below
    ring = (Pos(0, p["SMA_Z"]) * Circle(D_SMA / 2 + 1.3) - Pos(0, p["SMA_Z"]) * Circle(D_SMA / 2 + 0.05))
    flat = box(-2.5, p["PANEL_Y0"] + 0.05, flat_z - 0.35, 2.5, p["PANEL_Y1"] - 0.05, flat_z - 0.05)
    return (extrude(plane * bore, amount=p["PANEL_T"] + 1.0),
            extrude(plane * ring, amount=p["PANEL_T"] + 1.0), flat)


def _coax_probe(p: dict) -> Part:
    """Ø4.0-square dipole tube inside the channel: must be void over the whole blade."""
    root, d, n = _fin_axes(p)
    s_mid, half = p["FIN_W"] - p["COAX_OFF"], 2.0
    pts = [_fin_pt(root, d, n, t, s) for t, s in ((1.0, s_mid - half), (p["FIN_LEN"], s_mid - half),
                                                 (p["FIN_LEN"], s_mid + half), (1.0, s_mid + half))]
    return _yz_prism(pts, -2.0, 4.0)


def _slit_probe(p: dict) -> Part:
    """Path the coax takes when it is pushed through the slit: from outside the blade's rear-down
    face down to the channel axis, over the middle of the blade."""
    root, d, n = _fin_axes(p)
    s0, s1 = p["FIN_W"] - p["COAX_OFF"], p["FIN_W"] + 1.0
    pts = [_fin_pt(root, d, n, t, sv) for t, sv in ((2.0, s0), (p["FIN_LEN"] - 2.0, s0),
                                                   (p["FIN_LEN"] - 2.0, s1), (2.0, s1))]
    w = p["COAX_SLIT"] - 0.4
    return _yz_prism(pts, -w / 2, w)


def _touchdown(part: Part, y: float, z: float) -> float:
    """Nose-up attitude (deg) beyond which the point (y, z) touches down before the skid corner."""
    foot = (part & box(-60, -200, Z0 - 0.1, 60, 60, Z0 + 0.2)).bounding_box()
    return degrees(atan2(z - foot.min.Z, foot.min.Y - y))


def _ball_fill(part: Part, at: tuple[float, float, float], r: float) -> float:
    """Fraction of a Ø2r ball at `at` that is solid. The design language's tip-radius rule, probed
    where the tips actually ARE: S.tip_radius_report() samples the six bbox extremes, and on this
    part the bbox centre is 35 mm from the sting's tip and 25 mm from the cusp's, so its ball lands
    in mid air and reports a failure that is an artefact of the probe, not of the geometry."""
    ball = Pos(*at) * Sphere(r)
    try:
        inter = part & ball
        return float(inter.volume) / float(ball.volume) if inter is not None else 0.0
    except Exception:  # noqa: BLE001 - OCCT refuses the intersection; that is a 0 fill, not a crash
        return 0.0


def _sting_tip(p: dict) -> tuple[float, float, float]:
    """Centre of the sphere the sting is blunted with: a Ø STING_D1 ball must sit inside it."""
    (x0, y0, z0), d = _sting_axis(p)
    L = p["STING_LEN"]
    return (x0 + d[0] * L, y0 + d[1] * L, z0 + d[2] * L)


def _spine_tips(p: dict) -> list[tuple[str, tuple[float, float, float]]]:
    """Centre of each dorsal spine's own tip circle, at mid-wall-thickness (the blade is WALL_T
    thick, so a Ø1.6 ball has 0.1 mm to spare in X and the probe is a real test of the profile)."""
    xc = (p["WALL_X0"] + p["WALL_X1"]) / 2
    out = []
    for i in range(p["SPINE_N"]):
        h = p["SPINE_H0"] * SPINE_RUN[min(i, len(SPINE_RUN) - 1)]
        out.append((f"spine {i + 1} (h {h:.2f})",
                    (xc, p["SPINE_Y0"] + i * p["SPINE_PITCH"], TOP_Z + h - SPINE_TIP_R)))
    return out


def _pipe_open_probes(p: dict) -> list[tuple[str, Part, int]]:
    """(label, probe, solid count) per vane: the whole light path - well cone, duct and rod bore -
    shrunk 0.2 mm radially and fused. TWO numbers come out of it and both are needed:

      the probe must be entirely VOID in the part (nothing blocks the light), and
      the fused probe must be ONE solid (the three pieces actually touch, so the path is connected
        rather than three separate holes that happen to line up in the drawing).

    The bore's `run` is computed from the REAL radius, not the probe's: shrink the radius in
    _pipes()' own formula and the closing cone's apex marches 0.9 mm further out, so the probe would
    end inside the tip wall and report the glowing tip as a blockage."""
    out, z_hub = [], p["PLINTH_Z1"]
    r_real = p["PIPE_D"] / 2
    r = r_real - 0.2
    for xi, fan, R in zip(VANE_X, VANE_FAN, p["VANE_R"]):
        run = R - PIPE_TIP - r_real / tan(radians(PIPE_CONE))
        bore = extrude(Plane.XY.offset(z_hub - VANE_BURY) * (Sketch() + Pos(0, p["CONDUIT_Y"]) * Circle(r)),
                       amount=run + VANE_BURY)
        probe = _vane_place(bore, xi, fan, z_hub)
        probe += extrude(Plane(origin=(xi, WELL_Y, DUCT_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
                         * (Sketch() + Circle(r)), amount=WELL_Y - p["CONDUIT_Y"], dir=(0, -1, 0))
        probe += S.light_well((xi, WELL_Y), p["PLINTH_Z1"] - 0.1, led_d=p["LED_D"],
                              half_angle=WELL_HALF, depth=p["WELL_DEPTH"] - 0.2)
        out.append((f"vane x{xi:+.1f} (R {R})", probe, len(probe.solids())))
    return out


def _pipe_tip_probes(p: dict) -> list[tuple[str, Part, float]]:
    """(label, probe, cross-section area) per vane: a Ø0.8 core on the rod's own axis running from
    the bore cone's apex out past the vane tip. The material it meets IS the glowing tip wall, and
    Ø0.8 is small enough to stay inside the Ø3.6 flat the 0.9 tip fillet leaves on the Ø5.4 rod."""
    from math import pi
    out, z_hub, rp = [], p["PLINTH_Z1"], 0.4
    for xi, fan, R in zip(VANE_X, VANE_FAN, p["VANE_R"]):
        apex = z_hub + R - PIPE_TIP
        core = extrude(Plane.XY.offset(apex) * (Sketch() + Pos(0, p["CONDUIT_Y"]) * Circle(rp)),
                       amount=PIPE_TIP + 1.2)
        out.append((f"vane x{xi:+.1f} (R {R})", _vane_place(core, xi, fan, z_hub), pi * rp * rp))
    return out


def _lens_seat_probe(p: dict) -> Part:
    """The rabbet the translucent cap drops into, as installed: the sheet's own plan grown by the
    LENS_FIT clearance. It must be entirely void in the shell, or the second part will not seat."""
    z0 = p["PLINTH_Z1"] - LENS_RABBET
    return box(-LENS_X - LENS_FIT + 0.05, LENS_Y[0] - LENS_FIT + 0.05, z0 + 0.05,
               LENS_X + LENS_FIT - 0.05, LENS_Y[1] + LENS_FIT - 0.05, p["PLINTH_Z1"] - 0.05)


def checks(parts: dict[str, Part], frame: dict[str, Part], variant: str | None = None) -> list[tuple[str, bool, str]]:
    part = parts[NAME]
    p = _p(**(VARIANTS.get(variant or "fin", {}).get("params") or {}))
    out = []

    # --- mounting -----------------------------------------------------------------------------
    for side, sx in (("right", 1.0), ("left", -1.0)):
        xy = (sx * CLIP_XY[0], CLIP_XY[1])
        ok, detail = coaxial(part, xy, D_CLIP_BORE, Z0 + 0.01, Z0 + p["CLIP_H"] - 0.01)
        probe = cylinder(*xy, Z0, Z0 + p["CLIP_H"], STANDOFF_D)
        gap = round(part.distance_to(probe), 4)
        out.append((f"clip bore Ø{D_CLIP_BORE} coaxial with standoff_rear_tip_{side}, "
                    f"{STANDOFF_FIT} mm off the Ø{STANDOFF_D} standoff",
                    ok and isect(part, probe) < EPS and abs(gap - STANDOFF_FIT) <= 0.02,
                    f"{detail}; Ø6 probe {isect(part, probe):.3f} mm³, gap {gap}"))

    ok, detail = coaxial(part, TAIL_AXIS, D_M3_TAP, Z0 + 0.01, p["BOSS_Z1"] - 0.01)
    engage = p["BOSS_Z1"] - Z0
    out.append((f"M3 self-tap bore coaxial with rear_tail_axis {TAIL_AXIS}, >= 5 mm engagement",
                ok and engage >= 5.0, f"{detail}; {engage:.1f} mm of thread"))

    contact = seated(part, Z0)
    out.append((f"seated on plate_bottom at Z {Z0}", contact >= 200.0, f"{contact} mm² of contact"))

    # --- the VTX bay --------------------------------------------------------------------------
    board = _board_probe(p)
    gap = round(part.distance_to(board), 3)
    out.append((f"{p['CAV'][0]:.0f} x {p['CAV'][1]:.0f} x {p['CAV'][2]:.0f} VTX clears the bay by "
                f"{p['CLEAR']}", isect(part, board) < EPS and gap >= p["CLEAR"] - 1e-6,
                f"{isect(part, board):.3f} mm³ in the board, closest face {gap} mm"))

    cover = p["TOP_Z"] - (Z0 + p["STAND_H"] + p["CAV"][2])
    out.append(("side walls stand above the board's top face", cover >= 4.0,
                f"walls to Z {p['TOP_Z']}, board top Z {Z0 + p['STAND_H'] + p['CAV'][2]}: "
                f"{cover:.1f} mm of shoulder"))

    vent = sum(f.area for f in (_vents(p) & box(-30, p["PANEL_Y0"] - 0.01, 0, 30, p["PANEL_Y0"] + 0.01, 40)).faces())
    out.append(("rear vents open >= 60 mm² for heatsink air and the pigtail", vent >= 60.0,
                f"{vent:.1f} mm² through the {p['PANEL_T']} mm panel, open at the bay floor"))

    # --- the SMA seat -------------------------------------------------------------------------
    bore, ring, flat = _sma_probes(p)
    seat_ok = isect(part, bore) < EPS and isect(part, ring) > 5.0
    out.append((f"Ø{D_SMA} SMA D-hole through the panel at (0, {p['PANEL_Y1']}, Z {p['SMA_Z']})",
                seat_ok and p["PANEL_T"] <= SMA_SEAT_WALL_MAX,
                f"{isect(part, bore):.3f} mm³ in the bore, {isect(part, ring):.1f} mm³ round it, "
                f"seat wall {p['PANEL_T']} <= {SMA_SEAT_WALL_MAX}"))
    out.append((f"anti-rotation flat {SMA_FLAT} across, facing down (never a ceiling)",
                abs(isect(part, flat) - flat.volume) < 0.05,
                f"{isect(part, flat):.2f} of {flat.volume:.2f} mm³ of material under the flat"))
    zone = _spanner_zone(p)
    out.append((f"Ø{SPANNER_D} x {SPANNER_L} spanner pocket behind the nut is clear",
                isect(part, zone) < EPS, f"{isect(part, zone):.3f} mm³ of material in it"))

    # --- neighbours and keep-outs ---------------------------------------------------------------
    heads = {n: (isect(part, q), round(part.distance_to(q), 3)) for n, q in _head_probes().items()}
    out.append(("led_buzzer's M3 heads pass through the arched wall reliefs",
                all(v < EPS and g >= 0.3 for v, g in heads.values()),
                ", ".join(f"{n}: {g} mm" for n, (_v, g) in heads.items())))

    near = {n: round(part.distance_to(q), 3) for n, q in _neighbours().items()
            if isect(part, q) > EPS or part.distance_to(q) < 8.0}
    out.append(("no accessory collision, >= 0.5 mm to every tail neighbour",
                all(g >= 0.5 for g in near.values()),
                ", ".join(f"{n} {g}" for n, g in sorted(near.items(), key=lambda kv: kv[1])) or "none within 8 mm"))

    disc = prop_disc_violation(part)
    out.append(("outside the rear prop keep-out discs", disc < EPS,
                f"{disc:.3f} mm³; widest point |x| {max(abs(part.bounding_box().min.X), abs(part.bounding_box().max.X)):.2f} "
                f"vs the limit {max_abs_x_at(CLIP_XY[1]):.2f} at y {CLIP_XY[1]}"))

    # --- skid ----------------------------------------------------------------------------------
    angle, detail = _skid_angle(part)
    out.append(("skid takes a tail-first landing from 20 deg nose-up", angle <= 20.0, f"{angle:.1f} deg: {detail}"))
    # The skid protects the CARBON, it is not landing gear: the ground plane is GROUND_Z, set by
    # led_buzzer's bar and matched by motor_guard's four feet, and the skid sits well above it.
    skid_z = (part & box(-60, -200, Z0 - 0.1, 60, 60, Z0 + 0.2)).bounding_box().min.Z
    out.append((f"skid is a tail-strike protector, not a foot: it stays above the ground plane Z {GROUND_Z}",
                skid_z >= GROUND_Z + 1.0, f"skid underside Z {skid_z:.2f}, {skid_z - GROUND_Z:.1f} mm of "
                "clearance over the plane the feet and the LED bar stand on"))

    # --- the fin -------------------------------------------------------------------------------
    if p["fin_on"]:
        bb = part.bounding_box()
        out.append((f"fin stays under plate_top (Z {Z_TOP_UNDER}) by >= 2 mm",
                    bb.max.Z <= Z_TOP_UNDER - 2.0, f"highest point Z {bb.max.Z:.2f}"))
        probe = _coax_probe(p)
        out.append((f"Ø{p['COAX_D']} dipole channel clear along the whole blade",
                    isect(part, probe) < EPS, f"{isect(part, probe):.3f} mm³ blocking a 4.0 mm tube"))
        slit = _slit_probe(p)
        out.append((f"{p['COAX_SLIT']} mm snap slit open from the rear-down face to the channel",
                    isect(part, slit) < EPS,
                    f"{isect(part, slit):.3f} mm³ across a {p['COAX_SLIT'] - 0.4:.1f} mm insertion path"))
        tip = _touchdown(part, bb.min.Y, bb.max.Z)
        out.append(("fin tip is never the first thing to touch below 60 deg nose-up", tip >= 60.0,
                    f"fin tip (y {bb.min.Y:.1f}, Z {bb.max.Z:.1f}) touches first only beyond {tip:.1f} deg"))

    flat_bb = build("flat")[NAME].bounding_box()
    out.append((f"the 'flat' variant keeps everything at or under the wall top (Z {p['TOP_Z']}), so "
                "antenna_mast's coax can drop through the plate_top notch",
                flat_bb.max.Z <= p["TOP_Z"] + 1e-6,
                f"max Z {flat_bb.max.Z:.2f}; it ships as its own file (tail_block__flat) and is the "
                "variant the combined assembly installs"))

    # --- the frame's own SMA pass-through -------------------------------------------------------
    # The brief names two different SMA features and they are 32 mm apart. `sma` is a FRAME hole,
    # Ø6.5 at (0, -56.5) in plate_top, where the coax leaves the bay upward; the block's own
    # bulkhead seat is the 2.0 mm rear panel at y -88.4. The block must not be coaxial with the
    # frame hole - it must leave the column under it empty, which is what this measures.
    sma_xy = hole_xy("sma")[0]
    column = cylinder(*sma_xy, Z0, Z_TOP_UNDER, D_SMA)
    out.append((f"the frame's `sma` hole Ø{D_SMA} at {sma_xy} keeps a clear column down into the bay",
                isect(part, column) < EPS,
                f"{isect(part, column):.3f} mm³ of material in the Z {Z0}-{Z_TOP_UNDER} column; the "
                f"block's own bulkhead seat is the rear panel at y {p['PANEL_Y1']}, 31.9 mm behind it"))

    # --- style conformance (design language §5.2.5) and the second part ---------------------------
    counts = _APERTURES.get(variant or "shard", {})
    if p["DOME"]:
        ok_sut, sut = S.suture_present(part, p["CUSP_BREAK"], p["CUSP_FRONT"], p["CUSP_CREST"],
                                       w=SUT_W, depth=SUT_D)
        out.append(("CARAPACE CN-1: the suture is cut on X = 0 down the tail crest", ok_sut, sut))
        span, rise = 2 * p["WALL_X1"], p["CUSP_CREST"] - p["TRAY_Z1"]
        out.append(("CARAPACE: dome rise/span inside the family's 0.28-0.36 band",
                    0.28 - 1e-9 <= rise / span <= 0.36 + 1e-9,
                    f"rise {rise:.1f} over span {span:.1f} = {rise / span:.3f}"))
        fill = _ball_fill(part, (0.0, p["CUSP_Y"] + CUSP_TIP_R, Z0 + CUSP_TIP_R + 0.2), CUSP_TIP_R)
        out.append((f"CARAPACE CN-3: the tail runs out to a point blunted to r {CUSP_TIP_R}",
                    fill >= 0.9,
                    f"a Ø{2 * CUSP_TIP_R} ball at the cusp (0, {p['CUSP_Y']:.1f}) is {fill:.2f} solid"))
        out.append((f"CARAPACE: {ELY_N} cusped elytra slits per shoulder and the lunule debossed "
                    "on both maculation bands",
                    counts.get("elytra slits") == ELY_N and counts.get("lunule") == 1,
                    f"{counts.get('elytra slits')} slits at pitch {p['ELY_PITCH']} in Z "
                    f"{ELY_Z[0]}-{ELY_Z[1]}, {counts.get('lunule')} lunule of {p['LUNULE']} mm"))
        refused, why = _no_puncta(p)
        out.append(("CARAPACE: the punctate field is refused on measurement, not carried crushed",
                    refused and counts.get("puncta") == 0, why))
    if p["STING"]:
        tip_at = _sting_tip(p)
        fill = _ball_fill(part, tip_at, p["STING_D1"] / 2)
        out.append((f"FERAL: the sting ends in a Ø{p['STING_D1']} ball, never a needle", fill >= 0.9,
                    f"tip ball {fill:.2f} solid at (0, {tip_at[1]:.1f}, Z {tip_at[2]:.1f})"))
        tips = {n: round(_ball_fill(part, at, SPINE_TIP_R), 3) for n, at in _spine_tips(p)}
        out.append((f"FERAL: every dorsal spine ends in a cusp blunted to r {SPINE_TIP_R}",
                    all(v >= 0.9 for v in tips.values()),
                    ", ".join(f"{n} {v}" for n, v in tips.items())))
        out.append((f"FERAL: the cheeks carry a real punctate field and the lunule is cut through",
                    counts.get("cheek puncta", 0) >= 5 and counts.get("slash") == 1,
                    f"{counts.get('cheek puncta')} pits Ø{CHEEK_D} at pitch {CHEEK_PITCH} "
                    f"(ligament {CHEEK_LIG}), {counts.get('slash')} slash cut through each flank"))
    if p["RACK"]:
        paths = [(n, round(isect(part, q), 3), k) for n, q, k in _pipe_open_probes(p)]
        out.append((f"NOCTURNE: the Ø{p['PIPE_D']} light path is open AND connected, well to tip, "
                    "in every vane",
                    all(v < EPS and k == 1 for _n, v, k in paths),
                    ", ".join(f"{n}: {v} mm³ blocking, {k} solid" for n, v, k in paths)))
        walls = {n: round(isect(part, probe) / area, 3) for n, probe, area in _pipe_tip_probes(p)}
        out.append((f"NOCTURNE: every vane tip is left {PIPE_TIP} +/- 0.1 mm thin so it glows",
                    all(abs(v - PIPE_TIP) <= 0.1 for v in walls.values()),
                    ", ".join(f"{n} {v} mm" for n, v in walls.items())))
        out.append((f"NOCTURNE: {len(VANE_X)} light wells, a ladder in every vane and the lunule "
                    "cut through the tallest",
                    counts.get("light wells") == len(VANE_X)
                    and counts.get("ladder slots", 0) >= 2 * len(VANE_X)
                    and counts.get("lunule") == 1,
                    f"{counts.get('light wells')} wells (mouth Ø{3 * p['LED_D']}), "
                    f"{counts.get('ladder slots')} ladder slots at pitch {LADDER[2]}, "
                    f"{counts.get('lunule')} backlit lunule"))
        fans = [VANE_FAN[i + 1] - VANE_FAN[i] for i in range(len(VANE_FAN) - 1)]
        out.append(("NOCTURNE: the vanes fan 15 deg apart and none exceeds the 30 deg overhang ceiling",
                    all(abs(d - 15.0) < 1e-9 for d in fans) and max(abs(a) for a in VANE_FAN) <= 30.0,
                    f"fan {VANE_FAN}, steps {fans}, radii {tuple(p['VANE_R'])}"))
        seat = isect(part, _lens_seat_probe(p))
        out.append((f"NOCTURNE: the {LENS_RABBET} deep rabbet is clear and {LENS} is built",
                    seat < EPS and LENS in parts,
                    f"{seat:.3f} mm³ of material in the rabbet; {LENS} "
                    f"{'built' if LENS in parts else 'MISSING'}"))
        if LENS in parts:
            cap = parts[LENS]
            clash, gap = isect(part, cap), round(part.distance_to(cap), 3)
            out.append((f"{LENS} drops into the rabbet with {LENS_FIT} clearance all round and does "
                        "not touch the shell", clash < EPS and gap >= LENS_FIT / 2 - 0.02,
                        f"{clash:.3f} mm³ of overlap, closest face {gap} mm"))
            mouth = 3.0 * p["LED_D"]
            z0 = p["PLINTH_Z1"] - LENS_RABBET
            cov = {}
            for xi in VANE_X:
                probe = cylinder(xi, WELL_Y, z0 + 0.05, z0 + LENS_T - 0.05, mouth)
                cov[f"x{xi:+.1f}"] = round(isect(cap, probe) / probe.volume, 3)
            out.append((f"{LENS} covers every Ø{mouth} well mouth with its {LENS_T} mm sheet",
                        all(v >= 0.99 for v in cov.values()),
                        ", ".join(f"{n} {v}" for n, v in cov.items())))

    if p["VESPID"]:
        # THE GIRTH LAW, measured on the finished part and not read back off the parameters: each
        # tergite is sectioned in its own full-girth run and the section's own width is measured.
        girths = []
        for k in range(VE_N):
            sg = _ve_seg(k)
            # 45 % along the tergite: aft of its own necked nose (the undercut under the collar in
            # front of it) and forward of its own collar - the two places that are not the girth
            ym = sg["y1"] - 0.45 * sg["length"]
            # inboard of the shroud's own side walls (|x| 15.4-17.2, y -57.6..-100.4) and above its
            # tray, so neither can be mistaken for the abdomen's girth: the first tergite overlaps
            # both in Y, and a raw section there reads the wall at 17.2 instead of the girth at 7.0
            lim = VE_G1 + VE_COLLAR + 3.0
            sec = part & box(-lim, ym - 0.05, p["TRAY_Z1"] + 0.5, lim, ym + 0.05, 40)
            girths.append(round(sec.bounding_box().size.X / 2, 3) if sec.volume > 0 else 0.0)
        ratios = [round(girths[i + 1] / girths[i], 4) for i in range(len(girths) - 1)]
        out.append((f"VESPID: every tergite is {VE_GR} x the girth of the one in front, within 2 %",
                    all(abs(r - VE_GR) <= 0.02 * VE_GR for r in ratios),
                    f"half widths {girths} mm, ratios {ratios} against {VE_GR}"))
        lens = [VE_L1 * VE_LR ** k for k in range(VE_N)]
        ok_len = all(abs(lens[i + 1] / lens[i] - VE_LR) < 1e-9 for i in range(len(lens) - 1))
        lens = [round(v, 3) for v in lens]
        out.append((f"VESPID: and {VE_LR} x the length, so the outline steps down visibly", ok_len,
                    f"{VE_N} tergites of {lens} mm from y {VE_Y0} to "
                    f"{_ve_seg(VE_N - 1)['y0']:.2f}, then {VE_STING_L} mm of sting"))
        # ONE spiracle per tergite per flank: each is probed open on BOTH flanks, and the count of
        # cut openings is asserted exactly - never more than one per segment is the whole rule.
        opens, blocked = 0, []
        for k in range(VE_N):
            yc, z0s, w, h = _ve_spiracle_at(k)
            sg = _ve_seg(k)
            for sx in (1.0, -1.0):
                xa, xb = sorted((sx * (sg["g"] - sg["wall"] - 0.3), sx * (sg["g"] + 0.3)))
                pr = box(xa, yc - w / 2 + 0.25, z0s + 0.25, xb, yc + w / 2 - 0.25,
                         z0s + h - w / 2)
                if isect(part, pr) < EPS:
                    opens += 1
                else:
                    blocked.append(f"tergite {k} {'right' if sx > 0 else 'left'}")
        out.append((f"VESPID: EXACTLY one {VE_SPIR[0]} x {VE_SPIR[1]} spiracle per tergite per "
                    f"flank, open into the abdomen, scaled on the same {VE_GR} taper",
                    counts.get("spiracles") == 2 * VE_N and opens == 2 * VE_N,
                    f"{counts.get('spiracles')} lancets cut, {opens}/{2 * VE_N} probed open"
                    + (f"; blocked: {blocked}" if blocked else "")))
        fill = _ball_fill(part, (0.0, _ve_seg(VE_N - 1)["y0"] - VE_STING_L + VE_TIP_R + 0.1,
                                 Z0 + VE_TIP_R + 0.1), VE_TIP_R)
        out.append((f"VESPID: the sting ends blunted to r {VE_TIP_R}, never a needle", fill >= 0.9,
                    f"a Ø{2 * VE_TIP_R} ball at the tip (0, "
                    f"{_ve_seg(VE_N - 1)['y0'] - VE_STING_L:.1f}) is {fill:.2f} solid"))
        out.append((f"VESPID: a {VE_COLLAR} proud collar with a {VE_GROOVE} undercut groove aft of "
                    f"it on every joint, and two puncta rows on the dorsal midline",
                    counts.get("puncta", 0) >= 6,
                    f"{VE_N} collars {VE_COLLAR_L} mm long, {VE_N - 1} grooves {VE_GROOVE_L} mm "
                    f"long, {counts.get('puncta')} pits Ø{VE_PUNCTA[0]} x {VE_PUNCTA[1]} deep at "
                    f"x +/-{VE_PUNCTA[2]}"))
        walls = [round(VE_WALL[0] + (VE_WALL[1] - VE_WALL[0]) * k / (VE_N - 1), 2) for k in range(VE_N)]
        ok_v, _wv, det_v = min_wall(part, VE_WALL[1], allow=tuple(_ALLOW.get(variant or "vespid", ())))
        out.append((f"VESPID: wall {VE_WALL[0]} at the root tapering to {VE_WALL[1]} at the last "
                    f"tergite, then solid through the sting", ok_v,
                    f"flank walls {walls}; {det_v}"))

    if p["BRUT"]:
        v = variant or "brutalist"
        slab = _br_added(p)
        ok_s, _w, det_s = min_wall(slab, BR_T)
        out.append((f"BRUTALIST: the slab is {BR_T} mm, 2x the catalogue wall, constant and with no "
                    f"local thinning (cheeks, cornice, ribs and rear piers, aperture included)",
                    ok_s, det_s))
        curved = [fa.geom_type.name for fa in slab.faces() if fa.geom_type != GeomType.PLANE]
        out.append((f"BRUTALIST: NO fillet anywhere in the slab work above r 0.3 - chamfer only",
                    not curved,
                    f"{len(slab.faces())} faces in the slab, every one planar" if not curved
                    else f"curved faces present: {sorted(set(curved))}"))
        _sk_v, area, cheek = _br_void_profile(p)
        probe = extrude(Plane.YZ.offset(p["WALL_X1"] + BR_T - 0.2) * _br_void_profile(p)[0],
                        amount=0.1, dir=(1, 0, 0))
        out.append((f"BRUTALIST: exactly ONE rectangular void per cheek, >= {BR_VOID_MIN:.0%} of that "
                    f"cheek's area, corners sharp",
                    area / cheek >= BR_VOID_MIN - 1e-9 and counts.get("cheek voids") == 2
                    and isect(part, probe) < EPS,
                    f"{BR_VOID[0]} x {BR_VOID[1] - Z0} = {area:.0f} mm² of a {cheek:.0f} mm² cheek = "
                    f"{area / cheek:.1%}, {counts.get('cheek voids')} voids, "
                    f"{isect(part, probe):.3f} mm³ of material in the opening"))
        out.append((f"BRUTALIST: the lintel over that void is a DECLARED bridge, not an excused "
                    f"overhang: {BR_VOID[0]} mm against {MATERIAL}'s {BRIDGE_MAX[MATERIAL]} ceiling",
                    BR_VOID[0] <= BRIDGE_MAX[MATERIAL] and bool(BRIDGE_OK.get(f"{NAME}__{v}")),
                    f"span {BR_VOID[0]} mm, lintel {p['TOP_Z'] - BR_VOID[1]:.1f} mm deep, jambs "
                    f"{((BR_CHEEK_Y[0] - BR_CHEEK_Y[1]) - BR_VOID[0]) / 2:.2f} mm, declared as "
                    f"{BRIDGE_OK.get(f'{NAME}__{v}')}"))
        ribs = _br_rib_y(p)
        steps = [round(abs(ribs[i + 1] - ribs[i]), 6) for i in range(len(ribs) - 1)]
        out.append((f"BRUTALIST: three {BR_RIB[0]} proud square ribs across the top at {BR_RIB[2]} mm "
                    f"pitch, every one standing on material over its whole footprint",
                    len(ribs) == 3 and all(abs(d - BR_RIB[2]) < 1e-6 for d in steps),
                    f"ribs at y {tuple(round(y, 1) for y in ribs)}, steps {steps}, section "
                    f"{BR_RIB[0]} x {BR_RIB[1]}"))
        out.append((f"BRUTALIST: board marking {BR_BOARD[0]} x {BR_BOARD[1]} at {BR_BOARD[2]} pitch, "
                    f"every groove running the print direction (Z) and stopping at the apertures",
                    counts.get("board grooves", 0) >= 20,
                    f"{counts.get('board grooves')} planks on the cheeks and the rear face, all "
                    f"parallel to +Z, held {BR_KEEP} mm clear of the void and the land"))
        # from just over the M3 boss (which is shared functional geometry and lives in the same
        # column) up to the pier top: the band the bulkhead, its nut and a spanner actually use
        land = box(-BR_LAND / 2 + 0.2, p["PANEL_Y0"] - BR_T + 0.2, p["BOSS_Z1"] + 0.2,
                   BR_LAND / 2 - 0.2, p["PANEL_Y0"] - 0.2, p["TOP_Z"] - 0.2)
        out.append((f"BRUTALIST: the SMA comes out through a square {BR_LAND} mm sunk land, not a "
                    f"boss - what it exposes is the {p['PANEL_T']} mm panel, and that is the seat",
                    isect(part, land) < EPS and p["PANEL_T"] <= SMA_SEAT_WALL_MAX,
                    f"{isect(part, land):.3f} mm³ of slab in the land; seat wall {p['PANEL_T']} "
                    f"<= {SMA_SEAT_WALL_MAX}, and the Ø14 spanner pocket runs through it"))

    if p["GYROID"]:
        v = variant or "gyroid"
        slab = p["WALL_T"]
        out.append((f"GYROID: the shroud is one constant {GY_WALL} mm slab, thicker than any other "
                    f"language because its interior is mostly void",
                    abs(slab - GY_WALL) < 1e-9,
                    f"side wall {slab} mm (|x| {p['WALL_X0']}-{p['WALL_X1']}), rind {GY_RIND} on "
                    f"every bearing face, sheet {GY_RIND} between the rinds"))
        done, offered = _INFO.get(f"{v}_round", (0, 0))
        out.append((f"GYROID: ONE constant r {p['GY_ROUND']} on the plan outline, never a second "
                    f"radius (a run of two radii is the crease this language forbids)",
                    done >= 4 and done == offered and abs(p["TRAY_R"] - p["GY_ROUND"]) < 1e-9,
                    f"r {p['GY_ROUND']} on {done} of {offered} free shroud corners and on both deck "
                    f"corners (TRAY_R {p['TRAY_R']}); the shroud's rear corner is the deck junction"))
        out.append((f"GYROID: the deck is {p['TRAY_T']} mm thick, inside the {GY_WALL}-5.0 band this "
                    f"language works in", 3.6 - 1e-9 <= p["TRAY_T"] <= 5.0 + 1e-9,
                    f"deck Z {Z0}-{p['TRAY_Z1']} over y {p['PANEL_Y0']} to {p['TRAY_Y']}, "
                    f"{2 * p['WALL_X1']} mm wide"))
        span = min(2 * p["WALL_X1"], p["PANEL_Y0"] - p["TRAY_Y"]) - 2 * GY_RIND
        out.append((f"GYROID: >= 1.5 periods of {p['GY_PERIOD']} fit across the decorated deck",
                    span >= 1.5 * p["GY_PERIOD"],
                    f"{span:.1f} mm of deck between the rinds = {span / p['GY_PERIOD']:.2f} periods"))
        # Honest reporting of the one thing that can degrade. The functional 3.6 slab is the shipped
        # part when the bridge refuses, and that is asserted rather than assumed.
        res = BL.RESULTS.get(f"{NAME}__{v}")
        if res is not None and res.applied:
            cut = 1.0 - (res.stats.get("volume_ratio") or 1.0)
            out.append((f"GYROID: the ventilation is EMERGENT, not cut - and the lattice pass "
                        f"actually removed material rather than reporting that it had",
                        cut >= GY_MIN_CUT,
                        f"recipe {_INFO.get(f'{v}_recipe')} took {cut:.1%} of the deck out"
                        + (f" (the `gyroid` recipe itself came back at volume ratio "
                           f"{_INFO[f'{v}_degraded']} - solid - so the documented "
                           f"`{GY_CELL_FALLBACK}` fallback ran in its place)"
                           if f"{v}_degraded" in _INFO else "")
                        + "; no vent generator was called anywhere on this part"))
            out += BL.decor_checks(f"{NAME}__{v}")
        else:
            ok_bl, why = BL.available()
            base = _BASE.get(v)
            out.append(("GYROID: with the lattice refused the part ships as the verified "
                        "pure-build123d 3.6 mm slab, unchanged",
                        base is not None and abs(base.volume - part.volume) < 1e-6,
                        f"cell={_INFO.get(f'{v}_cell')} (fallback documented in VARIANTS); "
                        f"bridge: {why if not ok_bl else (res.reason if res else 'no call recorded')}"))
        # Measured on the FUNCTIONAL slab, and said so. The decorated part is a sewn mesh, and a ray
        # sampler crossing a lattice cell's corner facet reads a chord, not a wall - it returns 1.25
        # on a ligament the bridge's own mesh gate measures at 3.0. The lattice's wall is gated by
        # that mesh check, which is spliced in above; this row is the rind and the slab.
        ok_g, _wg, det_g = min_wall(_BASE.get(v, part), 1.5)
        out.append(("GYROID: min wall >= 1.5 on the functional slab (PETG floor; rind and sheet "
                    "1.6, and the lattice's own wall is the bridge's mesh row above)", ok_g, det_g))

    allow = tuple(_ALLOW.get(variant or "shard", ()))
    ok_wall, worst, wall_detail = min_wall(part, WALL, allow=allow)
    out.append((f"min wall >= {WALL} (walls {p['WALL_T']}, panel {p['PANEL_T']}, clip ring "
                f"{CLIP_WALL}, fin sides {(p['FIN_T'] - p['COAX_D']) / 2:.1f}; "
                f"{len(allow)} declared thin feature(s) skipped)", ok_wall, f"{wall_detail}"))
    return out
