# Supported equipment design envelopes

The clearance assessment uses configurable nominal envelopes. They are engineering
assumptions, not measurements or identification of the user's FC, ESC, camera,
mounts, connectors, cables, or other purchased hardware. Passing these checks
establishes fit only for these placed solids. Measure actual installed equipment,
including its protrusions and wiring, before using the result for hardware selection.

`EquipmentParameters` is immutable. Every listed size, spacing, keepout diameter,
and required gap can be changed in a derived preset. The user-confirmed carbon
thicknesses remain arm 5 mm and each of three plates 2 mm.

| Envelope | Baseline dimensions | Placement |
|---|---|---|
| ESC | 40 × 40 × 8 mm | Centered on central stack; 3 mm above camera plate upper face |
| FC | 40 × 40 × 8 mm | Same center; 3 mm above ESC upper face |
| Camera | 20 × 20 × 20 mm | Body centerline, 14 mm behind front tip datum; 2 mm above camera plate |
| Stack hardware, four | 5 mm outside diameter | Shared central stack hole axes; camera plate upper face to FC upper face |
| PCB mounting keepouts | 6 mm diameter | Cylindrical voids at the same shared central stack axes |

For the reference vertical stack the camera plate upper face is Z=9 mm, ESC spans
Z=12–20 mm, FC spans Z=23–31 mm, camera spans Z=11–31 mm, and the top plate lower
face is Z=34 mm. Placements recompute from frame dimensions; they are not fixed
world-coordinate offsets. The board templates require their full mounting keepouts
to remain inside their footprints, including when shared stack pitch is changed.

FC, ESC and camera require 0.2 mm minimum separation. Stack hardware permits zero
gap for intentional contact with its mounting plate; positive-volume overlap is
still rejected. Board keepouts provide 0.5 mm radial separation from the nominal
stack cylinders. These cylinders conservatively include their central volume;
they are clearance proxies, not manufacturing drawings for fasteners or spacers.

`design_equipment_envelopes(model, parameters)` creates these solids.
`validate_clearances(model, envelopes)` measures every equipment-to-frame and
equipment-to-equipment pair using solid distance and Boolean intersection, so
oversized footprints and insufficient top clearance fail on geometry. The
equipment shapes do not change the reconstructed carbon profiles or production
exports. Support details and exact purchase specifications require real hardware
dimensions.

Side panels are not applicable to this reconstruction: no side-panel part was
provided in the three scanned plate tracings. The photograph does not supply a
dimensioned side-panel profile, so no side panels are invented. Any added camera
side mounts need their own measured envelopes and clearance assessment.
