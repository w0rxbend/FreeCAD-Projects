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

Printable TPU/PETG accessories modelled in frame coordinates as installed; one module per accessory
(`_template.py` documents the contract, `_common.py`/`_fit.py` hold the print rules, equipment envelopes
and fit checks).

```sh
uv run python -m tigerbee accessories [--only ID ...] [--skip-freecad] [--no-preview]
uv run python scripts/verify_accessories.py [--only ID ...]
```

Output: `dist/accessories/{step,stl,3mf,freecad}/<label>.*` in print orientation (bed face on Z 0),
`dist/accessories/preview/<label>.png` and `<id>_installed.png`, `dist/accessories/manifest.json`
(material, volume, installed and printed bbox, every check with its measured value, mounting notes) and,
when nothing is excluded, `tigerbee_with_accessories.*` with every accessory installed. Every part is
checked for a single valid solid, zero interference with the frame, >= 0.2 mm to the Ø6 standoffs,
no material inside the prop keep-out discs (r 91.9) above Z 7, the landing plane, the battery envelope,
a flat bed face and support-free overhangs, plus the checks of its own spec.

| id | labels | material | interface | notes |
|---|---|---|---|---|
| (filled in by each accessory module) | | | | exclusive sets: gopro_mount / gps_mount; antenna_mast / tail_block(TOWER=True) |
