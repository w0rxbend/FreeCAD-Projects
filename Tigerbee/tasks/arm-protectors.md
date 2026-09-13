# Arm protector / landing feet

## Requested outcome

Add separately exported protectors that fit the current 5 mm arms and act as
standing feet. The five supplied images are inspiration, not dimensional sources.
Use the actual type 1 and type 2 motor pad geometry; mirror each for the left side.
Keep the 305 mm frame geometry intact.

## Initial design dimensions

- TPU candidate, retained by all four existing motor mounting slots.
- 12 mm projection below the arm: 9 mm nominal lower-plate ground clearance.
- 0.25 mm radial pocket clearance; 2 mm perimeter wall.
- Wall ends 0.2 mm below the upper carbon surface, leaving motor seating exposed.
- 2 mm bottom mounting flange; recessed channels give access to screw heads.
- Rounded source-following bumper and tapered foot, with a flat contact surface.
- Preserve the complete source motor slot travel, center shaft opening and tip window.
- Export four named independent STEP / STL / 3MF / FCStd components, CAD previews,
  parameters/fit reports and an assembled preview with four coplanar feet.

Dimensions above are editable design choices; printing tolerance and screw length
require a physical fit check. Added bolt grip is 2 mm; motor thread engagement must
be measured before selecting replacement screws.

## Acceptance evidence

- One valid solid and watertight mesh per exported protector; STEP round trip.
- No interference with actual arms, plates or standoffs in the assembled preview.
- Actual motor openings and recessed screw-head access unobstructed.
- Pairwise mirror symmetry; four ground faces at a common Z, clear below the frame.
- Regenerable CLI, native save/reopen and source/output hashes.
- Visual inspection of isolated parts and assembled views; full repository checks.

## Verified nominal geometry

| Measurement | Type 1 | Type 2 |
| --- | ---: | ---: |
| Solid volume (mm³; slicer infill not applied) | 9172.255 | 8988.579 |
| Flat ground contact area (mm²) | 507.329 | 492.397 |
| Carbon interference (mm³) | 0 | 0 |
| Source opening obstruction (mm³) | 0 | 0 |
| Screw head access obstruction (mm³) | 0 | 0 |
| Exported left/right reflection difference (mm³) | 0 | 0 |

All four assembled feet have Z=-12 mm in the arm datum and Z=-9 mm in the
frame datum, within 1e-6 mm numerical tolerance. The original frame STEP and the
regenerated frame STEP have zero Boolean symmetric difference. The original
305 mm motor diagonals therefore remain intact.

The STEP exporter reimports and compares every standalone solid; 3MF validation
checks closed manifold topology, connectedness and winding. The complete preview
has 19 solids and no protector/frame or protector/protector volumetric collisions.
Native conversion saves and reopens all four separate FCStd files and the preview.

The actual CAD preview is [here](../refs/analysis/arm-protectors-preview.png).
No fixed material mass is claimed: solid volume, TPU choice and slicer infill
must be distinguished. No physical impact or printed-fit qualification was performed.

Final checks: 158 full-suite tests passed; after the orthographic SVG camera fix,
all 12 accessory tests passed again. Ruff lint/format, mypy and distribution build
passed. The final inventory verifies 75 outputs. Independent binary STL audits
found one closed, consistently wound mesh per protector (8216 triangles for type 1,
8774 for type 2), with no boundary, nonmanifold or degenerate triangles.
