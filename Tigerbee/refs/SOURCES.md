# Authoritative references

The user explicitly confirmed that **`Tigerbee.FCStd` is the latest valid source
of truth**, refined manually from the original scans. Preserve those refinements.

1. `Tigerbee.FCStd`: authoritative geometry, openings, hole positions, and nominal
   thicknesses for `Body` (camera plate, 3 mm), `Body001` (arm type 1, 5 mm), and
   `Body002` (arm type 2, 5 mm). Where Scan_1 differs, the FreeCAD geometry wins.
2. `Scan_2.jpeg`: near-1:1 A4 pen tracings for the rear and top plates, which are
   absent from the original FreeCAD document. These reconstructions remain provisional.
3. [Physical measurements](measurements.md): approximately 303–304 mm between
   opposite motor-hole centers, used to check overall assembly size.
4. `Scan_1.jpeg` and product photos: supporting historical and visual references.

The central approximately 15 × 15 mm rounded rectangular opening in the saved
camera plate is a valid user refinement. Its absence from the earlier pen trace
is not a defect to remove. The original FreeCAD document is preserved; build123d
reconstructs its saved solids and regression tests compare independent STEP baselines.
Manual 3MF files and `baseline/*.step` are derivative references, not newer authority.

## Product photos

`product/tiger-beetle-7inch-330mm.png` remains a useful visual reference for the
assembled frame. Its **330 mm label is superseded by the physical measurement**.
The same applies to image 06’s 295 mm label. Earlier 5 mm arm / 2.5 mm plate labels
remain assumptions; image 07 depicts other variants.

The unextended reconstruction measures 302.592 mm and 303.986 mm. It agrees with
the approximate physical reading, so no arm extension is applied. Remaining
mounting offsets and root collisions require assembly/interface investigation while
preserving the authoritative FreeCAD parts.

## Historical placement audit

The [arm-placement audit](analysis/placement-audit.json) tested swaps and face flips
of the original arms at the current outer clamp-hole pairs. Its six outward-facing
arrangements measured 302.54–304.04 mm. The audit was made while 330 mm was assumed
from the product photo; that target is now superseded. The collision findings
remain relevant: all arrangements had arm-root interference.

Reproduce with `uv run python tools/audit_placements.py`; inspect
`build/placement-audit.json`. The committed historical report retains its original
source hash and assumptions rather than being rewritten as current evidence.

## A4 comparison

The [registered scan/CAD comparison](analysis/a4-comparison.md) confirms that the
saved Scan_1 image plane is effectively A4. It also identifies local feature
differences, including the user-refined central plate opening absent from the
earlier pen trace. These differences do not override the latest FreeCAD geometry.

Geometry regression tests also compare each extracted profile's source hash with
`Tigerbee.FCStd`. Editing the authoritative document makes those checks fail until
profiles and independent STEP baselines are re-extracted and exports regenerated.
