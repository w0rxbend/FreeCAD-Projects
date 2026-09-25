# Reference analysis — before CAD implementation

All four images in the recursively inspected project directory were opened and
visually inspected on 2026-09-25. PLAN.md is the complete supplied written plan.

| File | Classification | Observations |
| --- | --- | --- |
| `1000011984.jpg` | Physical hardware, underside | ESP32 DEVKIT V1 TYPEC label; two populated header rows; four corner mounting holes; connector at one short end. |
| `1000011986.jpg` | Physical hardware, component side | 30 pins (15 per side), ESP-32 metal shield, PCB antenna at opposite end from Type-C, CP2102-family bridge marking, EN and BOOT buttons beside USB. Manufacturer/revision cannot be established from visible markings. |
| `1000011987.jpg` | Physical hardware, LCD rear / wiring | Waveshare 1.28inch LCD Module 240×240, eight-way side-entry connector with installed loom, four brass mounting points; board is round with a tab. |
| `1000011988.jpg` | Physical hardware, LCD front | Circular glass, flat/tab at the ribbon end, protective film still attached; cable assembly visible. |

There are **no enclosure appearance, proportion, layout, or blueprint images** in
the supplied folder. No claimed reference-image silhouette is therefore possible.
The industrial design follows PLAN.md's prose: circular tilted face, smoothly
curved wedge/pod, quiet bezel, rounded base, concealed fasteners and rear USB.

## Coordinates

Millimetres. +X device right, +Y device rear, +Z upward. FRONT is the display
side (negative Y); BACK is USB-C side (positive Y). The display local axes are
u = +X, v = up the tilted face, n = outward toward the viewer. Rotate local
coordinates about +X by the face angle. The ESP32 is horizontal with USB toward
+Y and its antenna toward -Y. USB cutout comes from the connector transform.

## Authoritative dimensions and uncertainty

[Waveshare's official product documentation](https://docs.waveshare.net/1.28inch_LCD_Module/)
identifies SKU 19192, GC9A01, active display diameter 32.4 mm, overall module
40.4 × 37.5 mm, 240×240 resolution and eight SPI/power signals. These dimensions
are used without estimating scale from photographs.

No authoritative mechanical drawing for the exact ESP32 Type-C clone has been
identified. Do not substitute an Espressif DevKitC or micro-USB DOIT outline.
Provisional starting envelope: 55 × 28 × 1.6 mm; all connector positions,
heights, mounting-hole centres, diameter, pin projection and component heights
must be measured on the user's board. Likewise LCD stack thickness, rear
connector envelope, mounting-thread size and hole pattern need verification.
The CAD parameter definitions and measurement checklist distinguish these
assumptions from verified dimensions. The output is a complete nominal CAD
design; physical fit remains conditional on those measurements.

The official [dimensioned outline image](https://www.waveshare.com/img/devkit/LCD/1.28inch-LCD-Module/1.28inch-LCD-Module-details-size.jpg)
was subsequently retrieved and visually inspected as `refs/waveshare_dimensions.jpg`.
It confirms the 37.50 mm circular outline, 40.40 mm overall length and 14.28 mm
tab width (3.59 mm lower tab segment). It does not dimension hole centres or
thickness. `refs/waveshare_rear.jpg` was also inspected; despite the filename,
it is the official development-board wiring/use photograph, not another owned
hardware photo or an enclosure design reference. It confirms a flexible loom.

## Proposed arrangement and design assumptions

- 55° display plane from horizontal, circular bezel on a smooth lofted pod.
- Horizontal ESP32 on four base standoffs; header pins face downward with space
  for female jumper housings. EN/BOOT are accessible after removing the base.
- LCD behind the integral front bezel, retained from inside by a removable
  peripheral ring; connector and tab receive explicit clearance.
- Eight-wire harness routes through the side cavity to the downward headers;
  keep slack to separate base from shell during servicing.
- USB insertion direction +Y, rear opening projected from the board's actual
  connector location. A plug-overmould keepout is checked as well as the socket.
- Shell and base close with recessed underside screws into pilot-hole bosses;
  no front USB port. Small replaceable feet are purchased adhesive parts.
- Printed parts are nominal PETG, 0.4 mm nozzle, with assembly clearance exposed
  as a parameter. These are manufacturing choices, not measured hardware facts.
