# Symmetric design verification

This revision addresses the user's visual review of `top-plate.svg`,
`rear-plate.svg` and `tigerbee-top.svg`. Tigerbee.FCStd and the supplied arm/camera
3MF files remain the higher-priority design foundation; Scan_2 informs missing
plates. The original reference files are unchanged.

## Changes and measured results

| Check | Previous assembly | Refined assembly |
| --- | --- | --- |
| Opposite motor diagonals | 302.592 / 303.986 mm | 303.5 / 303.5 mm |
| Largest mounting offset | 0.753 mm | Below 0.000001 mm |
| Positive-volume intersections | 77.705 mm³ total | None |
| Complete solid reflection | Asymmetric plate/arm geometry | Zero Boolean difference for plates, arm pairs and standoff pairs |
| Smallest nominal 7-inch disc gap | 4.420 mm | 5.127 mm |
| Smallest structural mounting ligament | Not an acceptance gate | 2.019 mm (2 mm minimum) |

The independent [STEP reimport audit](refined-step-audit.json) uses actual reopened
solids and the declared fastener axes. It verifies all 15 components, continuous
shaft passages across every traversed layer, opening counts, reflection,
interference and dimensions. It does not merely repeat the model's nominal
coordinate calculations. Generated FreeCAD documents are separately saved and
reopened; see [native report](../../exports/native-report.json).

The camera outline follows the mirrored FreeCAD foundation: approximately
0.0985% symmetric-difference area relative to the reference outer envelope and
0.0694 mm maximum sampled boundary deviation before mounting changes. Its
15 × 15 mm R2 square, 18.5 mm round opening and strap-opening dimensions are retained.
Rear/top contours use nominal lines and tangent circular radii. All accessory
features are retained, with 31/32/30 internal openings for camera/rear/top.
The rear gains the counterpart of one originally unmatched accessory hole.

Both arm designs retain their saved motor pads and shafts. Root edits provide
0.6 mm center separation and R2 electronics clearance scallops with tangent
junction fillets. Root-hole centers remain based on the supplied CAD; structural
bores are normalized to 3.2 mm throughout the mating stack.

The current component SVGs and assembly top/isometric SVGs were rendered and
inspected after regeneration. Component reports and native metadata include
nominal dimensions; source/output hashes bind all canonical files together.

## Scope of the evidence

These results establish nominal geometry and CAD assembly fit. The two 2.5 mm
plates, top underside Z=35 mm and simplified standoffs remain design assumptions.
Hardware/accessory dimensions, material and machining tolerances, and manufactured
fit/load validation remain unresolved for a physical production release.
