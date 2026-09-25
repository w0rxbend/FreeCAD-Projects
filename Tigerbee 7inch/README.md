# Tigerbee 7" FPV frame

Parametric build123d model of a 7-inch frame with a **303.0 mm** wheelbase, reconstructed from
`Scan_1.jpeg` (two arms + mid plate) and `Scan_2.jpeg` (bottom and top plates). Three 2 mm carbon
plates, four 5 mm arms (one handed part, placed four times), eight M3 standoffs.

```sh
uv sync                              # Python 3.12, build123d 0.11
uv run python -m tigerbee            # build + export to dist/ (add --skip-freecad without FreeCAD)
uv run python scripts/verify.py      # geometry, clearance and round-trip checks
```

FreeCAD conversion uses `flatpak run --command=FreeCADCmd org.freecad.FreeCAD` (override with
`FREECAD_CMD`). Output: `dist/{step,stl,3mf,freecad}/tigerbee.*` (assembly) plus one file per part
in frame position, and `dist/manifest.json` (volumes, bboxes, every hole with its purpose).

Datum: origin = centre of the central 30.5 stack square, +X right, +Y front (camera), +Z up,
Z = 0 lower face of the bottom plate. Stack: bottom plate 0-2, arms 2-7, mid plate 7-9, top plate 34-36.

## Parameters (`src/tigerbee/params.py`)

| Name | Value | Note |
|---|---|---|
| `WHEELBASE` | 303.0 | primary; solves the arm length `ROOT_TO_MOTOR` = 114.804 (roots and plate holes never move) |
| `PLATE_T`, `ARM_T`, `TOP_CLEARANCE` | 2, 5, 25 | |
| `D_M3`, `D_M2` | 3.2, 2.2 | ISO 273 fine clearance |
| `D_STACK_NOTCH` | 3.4 | relief through the arm-root notch so the stack bolts pass bottom plate, arm, mid plate |
| `MOTOR_BOLT_CIRCLE` | 19.0 | as traced (4 x M3 at 45 deg, 13.4 mm adjacent); set 22.63 for 16x16 motors |
| `FWD_BAY_Y`, `FWD_25_OFFSET` | 61.5, +7.25 | forward bay on the mid plate |
| `REAR_BAY_Y`, `REAR_25_CENTER_Y` | -65.5, -73.0 | rear bay on the bottom plate |
| `SMA_XY`, `SMA_HOLE` | (0, -56.5), True | optional Ø6.5 antenna bulkhead in the top plate |

## Electronics mounting (`src/tigerbee/mounts.py`)

| Device | Pattern | Where | Headroom |
|---|---|---|---|
| ESC 4-in-1 + FC | 30.5 x 30.5 M3, centre (0, 0) | bottom plate + arm notches + mid plate | 25 mm above the mid plate |
| FC 20 x 20 M2 | 20 x 20, centre (0, 61.5) | mid plate forward bay (with 30.5 and Ø17.5 bore) | 25 mm |
| VTX (O4 / Avatar / HDZero) | 20 x 20 at (0, -65.5) and 25.5 x 25.5 at (0, -73.0), M2 | bottom plate rear bay; antenna via rear slots or SMA hole | 32 mm |
| VTX alternate | 25.5 x 25.5 at (0, 68.75), M2 | mid plate forward bay | 25 mm |

Added to the scanned parts: the front row of the rear 20 x 20, both 25.5 squares, the SMA hole, the
arm notch relief; the scanned 20 x 20 positions are drilled Ø2.2 instead of Ø3.2. Every added hole
keeps >= 2.5 mm of carbon to its neighbours and the plate edge (checked by `scripts/verify.py`).
The 25.5 squares are offset from the 20/30.5 centres because a concentric 25.5 would leave 0.8 mm
of web to the 30.5 holes.

## Accessories (`src/tigerbee/accessories/`)

Printable TPU/PETG accessories modelled in frame coordinates as installed; one module per
accessory (`_template.py` documents the contract, `_common.py`/`_fit.py` hold the print rules, equipment
envelopes and fit checks, `_style.py`/`_blender.py` the style vocabulary for modules that ship variants).
The set is whatever `src/tigerbee/accessories/*.py` holds; `manifest.json` lists what was built.

```sh
uv run python -m tigerbee accessories --assembly      # every accessory + the combined assembly
uv run python -m tigerbee accessories --only ID [--variant NAME] [--skip-freecad] [--no-preview]
uv run python scripts/verify_accessories.py [--only ID ...]
```

Output: `dist/accessories/{step,stl,3mf,freecad}/<label>.*`, every part in **print orientation** (bed
face on Z 0, bbox centred in XY), `preview/<label>.png` plus `<id>[_<variant>]_installed.png`, and
`dist/accessories/manifest.json` — per part its module, title, material, volume, installed and printed
bbox, print orientation, the frame faces and axes it mounts to, the fasteners it needs, and its own
checks with their measured values (`accessories.<id>.checks` carries the module's shared spec rows).
`manifest.volume_source` says which solid each volume was measured on; `manifest.kits` reconciles the
`_style` kit taste against what the modules actually build (`<id>:<variant>`, with `(fallback)` where
the kit had to borrow another style, and a bare `<id>` where the module ships a single build);
`manifest.assembly.builds` records the variant and any build override each assembly leaf was built
with, so a leaf that differs from its own part file says why; `manifest.assembly.file_notes` says
which assembly file is which.

**Generic checks, run on every part:** a single valid solid; zero interference with the frame; >= 0.2 mm
to the Ø6 standoffs; nothing inside the prop keep-out discs (r 91.9) above Z 7; nothing below the
module's landing plane; nothing inside the battery envelope; a flat bed face at Z 0; no unsupported
overhangs in print orientation. Four of those are per-module opt-outs, and each one is declared in the
module and measured in its own rows rather than waved through:

- `ALLOWED_INTERFERENCE` — `arm_sleeve` overlaps *its own arm* by design (a press fit); the allowance
  is per frame part and in mm³.
- `OWN_PROP_DISC` — `motor_guard` lives inside the disc of the prop it is bolted under, below Z 22.
- `BATTERY_OK` — `battery_pad` is what the battery sits on, so it is inside the envelope.
- `MIN_Z` — the default landing plane is `_fit.LANDING_Z` = −3.0, and the parts that *make* the
  stance opt out of it instead of respecting it.

**The stance.** The ground plane is a property of the installable set, not a global constant. In the
standard set it is `_fit.GROUND_Z` = **−15.2**, shared by exactly two parts: `motor_guard`'s four feet
(derived — `DROP` = 17.2 below the arm underside, so 15.2 mm of clearance under plate_bottom) and
`led_buzzer`'s bar, whose closed 10.4 mm WS2812 groove sets that depth. The quad stands level on five
coplanar contacts. The extended-feet family (`arm_protector_feet`, which is `EXCLUSIVE` with
`motor_guard`, together with `front_bumper_feet`) is deliberately coplanar 6.8 mm lower and defines its
own plane; in that set the LED bar is clear of the ground rather than load-bearing. What must hold in
**every** set is: everything that touches down is coplanar, and nothing else reaches below that plane.
`motor_guard.checks()` measures it for the set the guards are in (`EXCLUSIVE` resolved first, guards
pinned, so a part from the other stance is never measured against them), and
`manifest.assembly.checks` repeats it on whatever the combined assembly actually installs.

| id | title | mat. | mounts to | hardware | print | files (`<name>.{step,stl,3mf,FCStd}`) |
|---|---|---|---|---|---|---|
| `antenna_mast` | 915 MHz antenna mast | TPU | plate_top Z 36 rear prongs; rear-tip standoff axes (±16.5, -94) | 2 × M3×10 (replace the rear-tip bolts) + 1 zip tie | bracket underside down, mast leans 50° | `antenna_mast` |
| `arm_sleeve` | Arm shaft edge guard | TPU | arm shaft sides, arm-local y 40-84, up to Z 7 | none — 0.15 mm/side press fit | −Z down, 4 off | `arm_sleeve_{front,rear}_{left,right}` |
| `battery_pad` | Battery pad | TPU | plate_top Z 36, y −80…53.5; the 12 diagonal relief windows | none — strap 16/20/25 mm; optional 3.6 mm tie | rib side down (+Z normal) | `battery_pad` |
| `camera_pod` | Camera pod 19/21 mm | TPU | plate_mid Z 9 + its V-notches; front-tip standoffs (±19, 109) | 2 × M2 camera side screws (set the tilt) | nose (−Y) down; **fit one size** | `camera_pod_{19,21}` |
| `cap_holder` | Capacitor saddle | TPU | plate_bottom underside Z 0; Ø4.5 waist hole (±28, 0) | 1 × M3×8 + nut, 1 × 2.5 mm tie | −Z down; **fit one side** | `cap_holder_{left,right}` |
| `front_bumper` | Front fork bumper caps | TPU | plate_top prong tips; front-tip standoff bolt head | none — snap fit | nose (+Y) down, 2 off | `front_bumper_{left,right}` |
| `gopro_mount` | GoPro 3-finger mount | PETG | plate_top Z 36, y 56-96; Ø4.6 holes (±27.3, 91) and (±31.3, 63.5) | 4 × M3×10 + nyloc; M5 thumb screw + captive M5 nut | −Z down, nut-pocket bridge | `gopro_mount` |
| `gps_mount` | GPS mast and platform | PETG | plate_top Z 36 bridge y 58-74.5; Ø4.6 holes (±31.3, 63.5) | 2 × M3×8 + nyloc; 4 × M2×6 into the platform | −Z down | `gps_mount` |
| `led_buzzer` | LED / buzzer bar | TPU | plate_bottom underside Z 0; (0, −83.5) strap slot; rear_30p5_row | 2 × M3×8 self-tappers (or a zip tie) | −Z down | `led_buzzer` |
| `motor_guard` | Motor / arm-tip guard with landing foot — **the airframe's landing gear**: the pad underside is the ground plane Z −15.2, i.e. 15.2 mm of clearance under plate_bottom, and the 2 mm flange goes **between motor and carbon**, which is why the motor screws grow to M3×10 | TPU | arm tip prism Z 2-7; the Ø19 motor bolt circle | 4 × M3×10 motor screws **per guard** | −Z down, 4 off | `motor_guard_{front,rear}_{left,right}` |
| `rear_bumper` | Rear fork tip bumpers | TPU | outer rear fork lobe edges of both rear plates, y −98.6…−89; plate_bottom underside; rear-tip standoff Z 22.6-33.8 | 1 × M3×10 per side (replaces the rear-tip standoff's lower bolt) + washer | outboard (±X) face down, 2 off | `rear_bumper_{left,right}` |
| `side_panels` | FC/ESC side panels | PETG | front/rear arm-root standoffs; plate_mid Z 9; plate_top tabs Z 34 | none — 0.6 mm snap | −Z down; `shard` / `carapace` variants | `side_panel_{left,right}__{shard,carapace}` |
| `tail_block` | Tail VTX block | TPU | rear-tip standoffs Z 2-22; plate_bottom Z 2; rear_tail_axis (0, −91) | 1 × M3×8 self-tapper; 4 × M2×8 + 3 mm standoffs; SMA nut | −Z down, no supports; `fin` / `flat` variants | `tail_block__{fin,flat}` |
| `xt60_holder` | XT60 pigtail holder | TPU | rear-arm standoff Z 22-33.8; plate_bottom Z 2 | none — snap fit | top face down (bridged pocket floor); **fit one side** | `xt60_holder_{left,right}` |

### Mutually exclusive combinations

`tigerbee_with_accessories.{step,stl,3mf,FCStd}` and `preview/tigerbee_with_accessories_{iso,top,side}.png`
show one coherent set. What it leaves out, and why:

- **`gopro_mount` vs `gps_mount`** — both bolt to the same top-plate accessory holes at (±31.3, 63.5).
  The assembly installs `gopro_mount`; declared through `EXCLUSIVE` on both modules.
- **`camera_pod_21` vs `camera_pod_19`** — the two camera sizes occupy the same pod volume. The
  assembly fits the 21 mm pod.
- **`cap_holder`, `xt60_holder`** — mirrored pairs, one side is installed. The assembly takes the right-hand
  part of each. Both are printed and exported so either hand can be chosen.
- **`side_panels`** — `shard` and `carapace` are two looks of the same panel, so only one goes in
  (`ASSEMBLY_VARIANT = "shard"`).
- **`antenna_mast` + `tail_block`** coexist, but only with the `flat` variant of `tail_block` — its
  `fin` dipole blade and the mast's coax both want the plate_top U-notch. Both variants ship as their
  own files (`tail_block__fin`, `tail_block__flat`) and are checked and round-tripped separately;
  `ASSEMBLY_VARIANT = "flat"` picks the one that goes in.

The per-label choices come from each module's `ASSEMBLY_LABELS`, and every omission is recorded in
`manifest.json` under `assembly.excluded` and `assembly.alternatives_left_out`; how each installed
leaf was built is under `assembly.builds`.

`tigerbee_with_accessories.3mf` (named, watertight objects) and `.step` (a named assembly tree) are the
files to use. **The assembly `.stl` is reference geometry only, not printable**: STL has no object
concept, so all solids land in one mesh and parts that touch — sleeves on arms, guards on arm roots —
weld at shared vertices and leave non-manifold edges. Every per-part STL and 3MF is watertight; print
from those. `manifest.assembly.file_notes` says the same thing next to the file names.

`freecad/*.FCStd` are converted from the STEP files in the same run. `--skip-freecad` leaves them
untouched, which can make them older than the `step/stl/3mf` beside them; the run prints a warning and
`manifest.freecad.regenerated_this_run` records it, so always do the publishing run without that flag.

### Catalogue

<!-- catalogue:start -->

| id | what it is | material | parts | variants | mounts to | exclusive with |
|---|---|---|---|---:|---|---|
| `antenna_mast` | 915 MHz antenna mast | TPU95A | 3 | shard, chassis, nocturne | plate_top top face Z 36, rear fork prongs y -84..-104 (bri | rx_antenna_v_holder |
| `arm_protector_feet` | Arm-tip protector with landing feet | TPU95A | 2 | arsenal, feral | arm_<corner> tip prism - the pocket slides up from below o | motor_guard |
| `arm_sleeve` | Arm shaft edge guard sleeve | TPU95A | 20 | shard, carapace, vespid, gyroid, brutalist | arm_<corner> carbon shaft, both 5 mm side faces and the un | — |
| `battery_pad` | Battery pad | TPU95A | 3 | shard, arsenal, chassis | plate_top top face Z 36, y -80..53.5, outline inset 1.0 mm | — |
| `battery_strap_anchor` | Battery strap anchor + buckle keeper | PETG | 8 | brutalist, origami, filigree, vespid | plate_top top face Z 36 | gopro_mount, gps_mount |
| `callsign_plate` | Callsign / name plate | PETG | 5 | brutalist, origami, filigree, vespid, carapace | plate_top top face Z 36 (the whole underside seats on it) | — |
| `camera_damped_cradle` | Vibration-isolated camera cradle (19/21 mm, 5 deg / 15 deg) | TPU95A | 4 | t5_19, t5_21, t15_19, t15_21 | standoff_front_tip_left / _right Ø6 shafts (±19, 109), Z 1 | camera_pod, camera_pod_22, camera_standoff_sling, camera_detent_bracket, camera_hoop_guard |
| `camera_detent_bracket` | Camera detent bracket (5 deg indexed tilt, 19 / 21 / 22 mm) | PETG | 9 | cam19, cam21, cam22 | plate_mid top face Z 9 (the blade foot) | camera_pod, camera_pod_22, camera_damped_cradle, camera_standoff_sling, camera_hoop_guard |
| `camera_hoop_guard` | Nose-horn camera guard (19/21 mm, crushable horns ahead of the lens) | TPU95A | 2 | cam21, cam19 | plate_mid top face Z 9 (y 73-87, |x| 10.5-17.0) | camera_pod, camera_pod_22, camera_damped_cradle, camera_detent_bracket, camera_standoff_sling, camera_visor, front_bumper_feet |
| `camera_pod` | Camera pod (19 / 21 mm) | TPU95A | 14 | shard, slipstream, feral, chassis, brutalist, vespid, coral | plate_mid top face Z 9 (the pod rails sit on it) and its f | — |
| `camera_pod_22` | Hooded camera pod (22 mm Foxeer Mini Cat 3) | PETG | 3 | slipstream_t25, slipstream_t35, shard_t25 | plate_mid top face Z 9 (the ventral skirt seats on it) | camera_pod |
| `camera_standoff_sling` | Twin-ring standoff sling (19 / 21 / 22 mm) | TPU95A | 3 | t0, t10, t20 | standoff_front_tip_left / _right Ø6 shafts (±19, 109) thro | camera_pod, camera_pod_22, camera_damped_cradle, camera_detent_bracket, camera_hoop_guard |
| `camera_visor` | Camera visors / sun shades (19/21, 22 mm, generic barrels) | TPU95A | 12 | origami, vespid, filigree, brutalist | the camera's own Ø14.0 x 6.0 lens barrel (xi 10.0-16.0) on | — |
| `cap_holder` | Capacitor saddle (outboard L-bracket) | TPU95A | 2 | single | plate_bottom underside Z 0 (the tab seats on it) | — |
| `front_bumper` | Front fork bumper caps | TPU95A | 12 | shard, carapace, feral, brutalist, origami, coral | plate_top fork prong tip, top face Z 36 down to the unders | — |
| `front_bumper_feet` | Front bumper with landing feet | TPU95A | 3 | arsenal, chassis, feral | plate_mid UNDERSIDE Z 7 (the foot plate's seating face, bo | front_bumper, motor_guard |
| `front_bumper_skull_jaw` | Skull-jaw front bumper | TPU95A | 2 | full, lite | plate_top top face Z 36 over the front fork (seating plane | front_bumper |
| `gopro_mount` | GoPro / action-cam 3-finger mount | PETG | 1 | single | plate_top top face Z 36, y 56-96 (1250 mm² of bearing) | gps_mount |
| `gps_mount` | GPS mast and platform (front) | PETG | 1 | single | plate_top top face Z 36, bridge y 58-74.5, |x| <= 35.2 (83 | gopro_mount |
| `gps_tray` | GPS tray on splayed eyelet arms | PETG | 1 | single | plate_top top face Z 36 (both eyelet pads bear on it, eith | gopro_mount, gps_mount, front_bumper_skull_jaw, callsign_plate |
| `led_buzzer` | LED / buzzer bar | TPU95A | 1 | single | plate_bottom underside Z 0 (the seating face bears on it) | — |
| `lens_cover` | Lens covers (19/21, 22 mm pods, generic barrel) | TPU95A | 4 | single | the camera's own Ø14 x 6 lens barrel on the CAM_PIVOT (0,  | — |
| `motor_guard` | Motor / arm-tip guard with landing foot | TPU95A | 16 | stock, tall, sprung, bellows | arm_<corner> tip prism - the cavity slides up from below o | — |
| `motor_soft_mount` | Motor soft-mount (vibration-isolating washer plate) | TPU95A | 3 | brutalist, origami, filigree | the D19 motor bolt circle at the arm-tip motor centre (4 x | — |
| `prop_guard` | Half-ring prop guard (arm tip, CHASSIS hero) | TPU95A | 3 | chassis, shard, feral | the Ø19 motor bolt circle at the arm-tip motor centre (4 x | — |
| `prop_guard_ring` | Closed-ring prop guard (arm tip, full circle) | TPU95A | 3 | filigree, brutalist, origami | the Ø19 motor bolt circle at the arm-tip motor centre (4 x | prop_guard |
| `rear_bumper` | Rear fork tip bumpers | TPU95A | 2 | single | the outer rear fork lobe edges of plate_bottom and plate_t | — |
| `rx_antenna_v_holder` | V-mount dual RX antenna holder | TPU95A | 6 | chassis_64, chassis_44, shard_64, vespid, origami, filigree | plate_top top face Z 36, rear fork prongs y -88.5..-99.5 ( | antenna_mast |
| `side_panel_clip` | Clip-on side panels (9 styles) | TPU95A | 18 | long, double, angled, window_wing, brutalist, gyroid, filigree, origami, faceted_hook | standoff_front_arm_right / _left Ø6 shafts (±28.5283, 31.8 | side_panels |
| `side_panel_full` | Full-length side panels (4 styles) | TPU95A | 22 | slab, faceted, wrap, smooth, fairing, hull, segmented, canopy, finned, moulded, plated | standoff_front_arm_right / _left Ø6 shafts (±28.5283, 31.8 | side_panel_clip, side_panels, side_panel_system |
| `side_panel_system` | Side panel system (3-segment carcass + skins) | PETG | 90 | plain, carapace, bolted, clamped, captive | standoff_front_tip_left Ø6 shaft, 270 deg C-clip bore Ø6.5 | side_panels, xt60_holder |
| `side_panels` | FC/ESC side panels | PETG | 4 | shard, carapace | standoff_front_arm_right / _left Ø6 shafts (±28.528, 31.83 | — |
| `tail_block` | Tail VTX block | TPU95A | 7 | shard, carapace, feral, nocturne, flat, brutalist, gyroid | standoff_rear_tip_left / _right Ø6 shafts over Z 2-22 (cli | — |
| `wire_comb` | Wire comb / cable router | TPU95A | 20 | brutalist, origami, filigree, vespid | arm_front_right carbon shaft: both 5 mm flanks and the und | arm_sleeve |
| `xt60_holder` | XT60 pigtail holder | TPU95A | 2 | single | standoff_rear_arm_<side> Ø6 shaft over Z 22-33.8 (the clip | — |

<!-- catalogue:end -->
