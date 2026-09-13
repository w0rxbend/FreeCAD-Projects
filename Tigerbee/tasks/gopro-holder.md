# Top-plate GoPro holder

Fit a separately exported three-finger GoPro-style holder to the existing front
four Ø5 mm accessory holes on the current top plate, above the FPV-camera region.
The three supplied images inform the form, not the dimensions. No carbon changes.

## Design

- Derive actual mounting axes from top-plate circular BRep edges: X=±28 at Y=58,
  X=±27 at Y=91 mm. Holder center Y=74.5 mm; forward is +Y.
- Four M3 clearance bores Ø3.3; integral Ø4.8 registration bosses engage 2 mm into
  the existing Ø5 mm carbon holes. External washers/nuts underneath; no printed threads.
- Low mount: 5 mm base, pitch axle 18 mm above the top-plate surface. Adjustable
  axle height parameter for raised alternatives. Standard camera-side two fingers.
- Three mounting fingers: 3 mm thickness, 3.2 mm gaps, R7.5 crowns, Ø5.5 axle.
  Outer right finger includes an outward extension for an 8.4 mm AF / 4.2 mm deep
  captive M5 hex nut seat. The mating gap coordinates remain centered at X=0.
- Nominal finger dimensions follow the author's dimensioned reference drawing:
  https://jackw01.github.io/assets/projects/modularmounts-GoPro%20Profile.pdf
  This is a compatible community design, not an official GoPro tolerance standard.
- One connected holder, independent STEP/STL/3MF/FCStd and illustrated previews.
  Combined preview locates it on the actual top surface, Z=38 mm by default.

## Verification

Actual holes, counterbore tool access, locating boss clearance, bilateral base,
GoPro mating coupon engagement and pitch sweep, source frame interference, STEP
round trip, watertight mesh and native reopen must pass. The regular FPV camera
and exact GoPro body are not present in the source CAD; body-specific clearance
and printed fit remain explicit physical checks.

Review corrected the initial M4 concept to M3: Ø3.3 bores inside Ø4.8 bosses
leave 0.75 mm radial walls, compared with the unprintably thin 0.25 mm of the
initial concept. A failing geometry test demonstrated that defect before the fix.
Counterbores are Ø6.6 × 3 mm deep for M3 head/tool access.

## Final evidence

- 175 tests pass, including 17 dedicated holder tests. Ruff lint/format, mypy and
  distribution build pass. Native export reopens one holder solid and the
  20-solid combined preview; the inventory verifies 87 committed outputs.
- Holder dimensions: 68 × 45 × 27.5 mm including registration bosses;
  solid CAD volume 16072.305 mm³ (not a slicer infill or mass estimate).
- All four axes exactly follow the plate circles. Measured boss radial walls
  are 0.75 mm; the plate/boss radial allowance is 0.1 mm.
- Zero interference with carbon, four bolt shafts/tools and the M5 pivot.
  Sixteen nominal two-finger positions from −15° to 60° in 5° increments clear.
- Independent STL audit: 11008 triangles, one connected closed mesh, no winding,
  boundary, nonmanifold or degenerate faces.
- Independent STEP audit: bilateral base difference 0 mm³; all 19 existing frame
  and foot solids preserved; the placed standalone holder and assembled holder
  have zero Boolean symmetric difference. Whole-compound subtraction at contacting
  solids was inconclusive, so the final comparison checks each imported solid.
- [Export audit with hashes](../refs/analysis/gopro-holder-export-audit.json) and
  [actual CAD preview](../refs/analysis/gopro-holder-preview.png) record the result.

Physical camera-body clearance, printed fit and strength are not qualified by
these CAD checks. Use a metal M5 nut; the printed hex seat is not a thread.
