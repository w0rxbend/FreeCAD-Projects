# Arm-root containment correction

The user identified exposed arm bases in the assembly SVG and supplied close-up
photos of the lower clamp sandwich. The previous symmetry, coaxiality and solid
interference checks did not detect this: a symmetric root can still protrude
outside the plates without colliding with another component.

The root envelope is the intersection of the **filled outer silhouettes** of the
camera and rear plates. Internal plate openings do not define that envelope.
The base region starts 2 mm beyond the motor-facing rim of the innermost clamp
bore and extends toward the frame center. The outer clamp pad and shaft entry
remain outside this base region. This avoids either accepting the exposed root as part of the shaft
or clipping the entire free shaft to the narrow plates.

The correction trims the arm bases to that envelope and blends the new boundary
into the retained shaft. Plate contours, all mounting axes, motor patterns,
305 mm square-X placement and the confirmed 5/3/6 mm dimensions are preserved.

The rear correction uses a 0.2 mm outline inset, R0.3 tangent blends and a local
transition datum Y = −115 mm. The innermost rear bore defines the audited base
limit at local Y = −115.949156 mm. The original profile remains exactly unchanged
for Y ≥ −114 mm, including the outer mounting pad and the entire free shaft.
Front arms already satisfy the base containment requirement and are unchanged.

| Check | Before | After |
| --- | --- | --- |
| Rear base outside both-plate envelope, per arm | 51.815 mm² | 0 mm² |
| Front base outside envelope, per arm | 0 mm² | 0 mm² |
| Rear transition minimum width | — | 18.075 mm (18 mm required) |
| Minimum structural mounting ligament | 2.295 mm | 2.295 mm |
| All plate and front-arm solid differences | — | 0 mm³ |
| Protected rear shaft solid differences | — | 0 mm³ |
| Opposite motor diagonals | 305 / 305 mm | 305 / 305 mm |

See the [before/after contour overlay](arm-root-fit.svg),
[before audit](root-containment-before.json) and [final STEP audit](305-step-audit.json).
The overlay shows the actual lower-stack outlines from the old and regenerated
STEP files: blue camera plate, gray rear plate, orange front arms, violet rear arms.
Intentional rear-plate tabs with large holes remain outside the camera waist.

The before STEP is recoverable from commit `66c3344` at
`Tigerbee/exports/assembly/tigerbee-assembly.step`; its SHA-256 is recorded in the
before audit. The final audit records the regenerated STEP checksum and exact
Boolean comparisons of the preserved components.

All 146 tests passed, including symmetric protrusion rejection, actual bore-based
containment, all eight arm openings, tangent joins, 152 transition cross-sections
and preservation of the source shaft. Ruff, mypy and the package build passed.
All 45 canonical outputs were verified; all six FreeCAD documents were saved and
reopened. Exported top/isometric/arm views and the comparison overlay were inspected.
