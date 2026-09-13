# 305 mm true-X design verification

The latest user specification replaces the previous 303.5 mm layout:
**305 mm wheelbase, 5 mm arms, 3 mm plates, 6 mm standoff outside diameter**.

| Requirement | Measured result |
| --- | --- |
| Opposite motor-bore diagonals | 305 / 305 mm |
| Diagonal intersection | Frame (0,0), perpendicular |
| Motor-center coordinates | (±107.833784131, ±107.833784131) mm |
| Four motor side spans | 215.667568262 mm each |
| Arm stock | 5 mm, all four arms |
| Plate stock | 3 mm, all three plates |
| Standoff outside diameter | 6 mm, all eight standoffs |
| Left/right solid reflection | Zero Boolean difference |
| Mounting-axis offsets | Below 0.000001 mm |
| Intersections and blocked fastener passages | None |
| Minimum structural mounting ligament | 2.295 mm (2 mm required) |
| Minimum nominal 7-inch propeller-disc gap | 37.868 mm |

See the [dimensioned motor diagram](../../exports/assembly/tigerbee-motor-layout.svg),
[assembled top view](../../exports/assembly/tigerbee-top.svg), and independent
[reimported STEP audit](305-step-audit.json). The audit records the final STEP
checksum and inspects its actual motor bores, plate thicknesses and standoff
surfaces. It also checks every intended opening, mating shaft passage and solid
reflection. The native export separately saves and reopens all six FCStd files.

## Geometry changes

Front/rear arm rotations are now 45°/135° with mirrored left copies. The original
motor pads, shafts and mounting-hole centers remain based on Tigerbee.FCStd and
the supplied 3MF files. Rounded local root relief gives 0.6 mm left/right separation
and sufficient transverse clearance between front/rear roots.

The new root-hole axes require local camera/rear front shoulder extensions of 5 mm.
The camera's overall width and length remain unchanged; the top plate outline
remains unchanged. All 31/32/30 camera/rear/top openings remain present. The plate
contours remain exactly mirrored, analytic and tangent at perimeter joins.

The user-specified stock thicknesses now apply to both standalone builds and the
assembly. The retained top underside Z=35 mm gives six 24 mm and two 32 mm standoffs.
Their 3.2 mm internal bore remains a modeled M3 clearance; detailed threads and
accessories are outside these five plate/arm designs.

All 136 tests, lint, formatting, types and package build passed. All 45 canonical
exports passed inventory verification; final top/isometric/component and motor
layout SVGs were rendered and inspected.
