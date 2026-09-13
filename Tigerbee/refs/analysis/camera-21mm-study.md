# Camera width feasibility: 21 mm

The user confirmed **21 mm camera width**. Height, depth, lens, side screw and
rotation-axis location remain unknown. This study measures nominal space in the
existing assembly; it does not qualify an actual camera or release a camera mount.
The [measurement data](camera-21mm-study.json) records all 15 frame components for
each witness and the source hashes.

## Measured frame interface

The imported [assembly STEP](../../exports/assembly/tigerbee-assembly.step) has
front standoffs at X=±19.25, Y=108.75, outside diameter 6, from Z=11 to Z=35.
Their inner gap is 32.5 mm. A centered 21 mm wide camera leaves 5.75 mm on each
side to the bare standoffs. The local plate face separation is 24 mm. The top
plate has an open nose, so this separation is not a uniform enclosing box.

STEP SHA-256:
`1a748b0d2acc827e48a3c57b25e848286e99167b951d612f68349e01b2468467`.
Generator source digest:
`a1e30632d60af4c03554778b027f937121861a970cf15f276f901cbebb30632a`.
This identifies the STEP inspected before the subsequent user-requested export
regeneration, with baseline repository commit `cad6a21`. A re-export can change
the STEP bytes; the geometry source digest was independently checked unchanged
while the new exports were being generated.

## Hypothetical body study

For exploration only, a **21 × 21 × 21 mm cube** was centered at X=0, Y=108.75
and rotated around its central X axis. Only its width comes from the user.
The cube has no lens, cable, side screws or other protrusions. Sampled rotations
were −45, −30, −20, −10, 0, 10, 20, 30 and 45 degrees, at Z=23 and Z=27.
These are discrete collision measurements, not a continuous sweep guarantee.

| Cube center Z | Rotation X | Lower camera plate distance | Lower plate overlap volume | Top plate distance |
| ---: | ---: | ---: | ---: | ---: |
| 23 | 0° | 1.5000 mm | 0 mm³ | 3.8079 mm |
| 23 | 10° | 0 mm | 1.0400 mm³ | 3.5342 mm |
| 23 | 30° | 0 mm | 99.7561 mm³ | 3.5000 mm |
| 23 | 45° | 0 mm | 121.3801 mm³ | 3.5000 mm |
| 27 | 0° | 5.5000 mm | 0 mm³ | 3.5000 mm |
| 27 | 10° | 3.8362 mm | 0 mm³ | 3.5000 mm |
| 27 | 30° | 1.6567 mm | 0 mm³ | 3.5000 mm |
| 27 | 45° | 1.1508 mm | 0 mm³ | 3.5000 mm |

At Z=27 the hypothetical cube has no interference with any of the 15 frame
components at the sampled angles. Its bare-standoff clearance remains 5.75 mm.
The Z=23 placement collides with the lower plate at some sampled angles. Thus a
higher pivot is worth investigating once the camera drawing is available; it
does not require changing the carbon outline just to evaluate this envelope.
Neither result establishes the actual camera's usable tilt range.

## Bracket space and remaining design work

Two cylindrical sleeve witnesses, each outside diameter 10, inside diameter 6.3
and height 20, were centered on the front standoffs at Z=23. Both clear the plate
faces by 2 mm and the standoff surface radially by 0.15 mm in nominal CAD. Their
inward surfaces reach X=±14.25. These dimensions demonstrate space for mounting
material; they are not a fit or print-tolerance specification.

A symmetric bracket could place nominal camera-facing surfaces at X=±10.75
(21.5 mm opening), leaving 0.25 mm per side around the stated 21 mm width before
any compression, manufacturing tolerance or screw clamping is considered.
Three-millimeter side tabs would end at X=±13.75 and need connecting material to
the sleeves. All these bracket dimensions are proposed assumptions, not measured
camera features.

Independent loose sleeves can rotate and slide. They need an explicit retention
and antirotation arrangement before they can constitute a usable mount. A joined
cradle is one candidate; its crossbar must be checked against the actual rear
camera body and cable throughout the selected tilt range. No sleeves or cradle
were added to the assembly or exported as manufacturing parts.

The next actual camera-mount model needs the camera height/depth, side-hole
position and thread, lens projection, rear cable exit and requested tilt range.
These determine the pivot, tab slots or holes, screw access and retention.
