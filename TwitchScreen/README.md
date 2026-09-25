# TwitchScreen enclosure

Parametric FreeCAD enclosure for the photographed **30-pin ESP32 DevKit V1
Type-C** and **Waveshare 1.28inch LCD Module**, based on `PLAN.md`.

The circular face tilts 55° from horizontal. A warm-coloured pod meets a dark
removable base; all fasteners are concealed from the front. USB-C faces the rear.
Nominal envelope: **64 × 86 × 77.5 mm**, before adhesive feet.

The supplied folder contained four hardware photographs and no enclosure concept
images. The exterior therefore follows the written pod/wedge design brief.
See [reference analysis](docs/reference_analysis.md) and the
[measurement checklist](docs/measurement_checklist.md). Clone dimensions and
LCD thickness/connector dimensions remain provisional and editable.

## Deliverables

| Use | File |
| --- | --- |
| Editable master | [TwitchScreen.FCStd](output/freecad/TwitchScreen.FCStd) |
| Open with parametric code loaded | [TwitchScreen.FCMacro](TwitchScreen.FCMacro) |
| CAD interchange assembly | [TwitchScreen_assembly.step](output/step/TwitchScreen_assembly.step) |
| Arranged printable parts | [print_plate.3mf](output/3mf/print_plate.3mf) |
| Individual printable meshes | [shell.stl](output/stl/shell.stl), [base.stl](output/stl/base.stl), [lcd_retainer.stl](output/stl/lcd_retainer.stl) |
| Rendered overview | [front](output/preview/01_front_hero.png), [rear USB](output/preview/02_rear_usb.png), [section](output/preview/05_section.png), [exploded](output/preview/06_exploded.png) |

Every printed part also has an individual STEP, 3MF and FCStd under `output/`.
STEP/FCStd preserve assembly coordinates. Individual STL/3MF files are rotated
into print orientation and placed on Z=0. The combined print plate contains
only three printed parts with 10 mm spacing. Files named `assembly_view_only`
include electronics reference shapes and are for inspection, not slicing.
Preview PNGs and the Blender scene are in `output/preview/`.

## Rebuild and verify

Uses the installed FreeCAD 1.1.3 Flatpak and Blender 5.2. No third-party FreeCAD
workbench is required. From this directory:

```sh
flatpak run --command=FreeCADCmd org.freecad.FreeCAD -c 'import sys; sys.path.insert(0,"scripts"); import export_project; export_project.main()'
uv run --with trimesh --with numpy --with networkx python scripts/verify_exports.py
flatpak run --command=FreeCADCmd org.freecad.FreeCAD -c 'import sys; sys.path.insert(0,"scripts"); import verify_assembly, verify_walls; verify_assembly.main(); verify_walls.main()'
blender -b --threads 8 --python scripts/render_previews.py
python scripts/package_project.py
```

If using a native FreeCAD installation, replace the Flatpak command prefix
with its `FreeCADCmd` executable. For interactive editing, run the supplied
macro from FreeCAD's Macro menu; keep it beside `scripts/` and `parameters.json`.
FCStd includes saved BRep shapes and can be inspected without the script, but
the feature proxies require the local geometry module to recompute.

`output/reports/geometry_validation.json` records exact solid checks, hardware
interference, rear-port position, mesh-volume comparison and STEP/FCStd reopen
checks. `mesh_validation.json` independently checks the written STL/3MF meshes
for closed surfaces, orientation, connectedness, dimensions and print placement.
`assembly_validation.json` covers screw-head envelopes, component insertion and
base extraction at sampled positions, editable-parameter recompute, and reopening
all native files. `wall_validation.json` records 695 exact surface-distance
samples; the minimum is the intended 1.5 mm bezel seat. These checks establish
nominal CAD validity, not physical fit or a tested print.

## Printing and assembly

Three printed parts: shell, base, LCD retainer. Suggested starting settings:
PETG, 0.4 mm nozzle, 0.2 mm layers, four perimeters, five top/bottom layers and
20–30% infill. These are starting settings, not a tested printer profile.

The shell is supplied face-down; use supports for internal screw bosses and
inspect the rear USB roof in your slicer. Keep support interfaces away from
the LCD seat. The base prints underside-down, with its posts upward. The
retainer prints flat. A brim can help the shell's narrow first-layer annulus.
The plate is about 197 × 89 mm before brim/support expansion.

Additional parts: the two electronic boards and supplied eight-wire loom;
four M2 × 6 mm pan-head screws (Ø3.8 mm heads) for the ESP32, four M2.5 × 8 mm low-profile
pan-head screws for the base, two M2 × 5 mm pan-head screws for the retainer,
and four Ø8 × approximately 1.5 mm adhesive rubber feet. Screw heads must fit
the model's recesses (base Ø5.2 mm × 1.3 mm deep). Pilot holes are intended for
carefully formed plastic threads; verify fit on a coupon before committing.

1. Remove the LCD protective film. Seat the LCD from inside the shell, with its
   tab down and rear connector up. The glass rests behind the bezel, with the
   active area unobstructed.
2. Fit the retaining ring behind the PCB, aligning the connector notch and tab
   relief. Tighten the two M2 screws lightly and evenly into the shell bosses.
3. Fix the ESP32 onto the four base posts. Its USB-C connector points toward
   +Y (rear); the PCB antenna points toward -Y (front). Connect the LCD loom to
   the appropriate GPIOs using your firmware's pin mapping.
4. Route wires through the side cavity, away from screw posts, antenna and glass.
   Leave a service loop so the base can be lowered before disconnecting wires.
5. Seat the locating lip and close the four underside base screws. Check cable
   insertion from the rear. EN/BOOT are reached by removing the base.
6. Attach the four feet in the shallow underside recesses.

No firmware, mains-power circuit, battery, or undocumented touch-screen variant
is part of this mechanical project. Hardware representations are fit envelopes,
not detailed manufacturer CAD. Physical assembly and print tolerances must be
confirmed against the actual boards using the measurement checklist.
The single rounded `cable_route` body is a Ø4.4 mm reserved corridor for the
eight-wire loom, not one thick wire or an electrical pin-mapping diagram.
