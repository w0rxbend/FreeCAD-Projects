# Authoritative references

The user confirmed these sources on 2026-09-13:

1. `product/tiger-beetle-7inch-330mm.png`: final and true target product, Tiger Beetle
   7-inch, **330 mm diagonal motor-center to opposite motor-center wheelbase**.
2. `Scan_1.jpeg`: authoritative component outlines for the two arm types and
   camera-side plate.
3. `Scan_2.jpeg`: authoritative component outlines for the rear and top plates.

These references apply together. Scanned pen outlines do not by themselves
establish exact hole diameters, physical scale, thickness, or vertical spacing.
Record inferred dimensions and resolve discrepancies with measured dimensions;
do not silently scale holes or distort an outline to force the wheelbase.

`Tigerbee.FCStd`, its manual 3MF exports, and `baseline/*.step` are prior manual
reconstructions. Their geometry is preserved as a regression baseline, but they
must be corrected if they conflict with the authoritative scans and final photo.

Product images 01–09 supply additional assembly context. Image 06's 295 mm
wheelbase is superseded and must not be used as the target. Its thickness labels
(5 mm arms, 2.5 mm plates) are provisional for the confirmed 330 mm variant.
Image 07 also advertises another variant; it is not dimension authority here.

Current unresolved conflict: the reconstruction and assumed mounting placements
produce diagonal wheelbases near 303 mm. Metric scan calibration and arm placement
need verification against the 330 mm target before changing the physical profiles.

## Placement audit

The reproducible [arm-placement audit](analysis/placement-audit.json) tests both
faces of both saved arm types, using two of each, at the current outer clamp-hole
pairs. Six arrangements place all four motors outward in their assigned quadrants.
Their diagonal wheelbases range from 302.54 to 304.04 mm; none reaches 330 mm.
All retain root collisions, with the current assembly attaining the smallest total
intersection volume (77.70 mm³, tied with another arrangement). Swapping the arm
types or flipping them does not resolve the discrepancy at these mounting pairs.

This audit does not establish scan scale or exclude different mounting-hole
choices or corrected reconstructions. Both JPEG files are 2480 × 3508 pixels
with 72-DPI tags; those tags cannot establish the intended physical scale.
A confirmed scale or measured part dimension is needed to reconcile the outlines
with the 330 mm specification.

Reproduce with `uv run python tools/audit_placements.py`; inspect
`build/placement-audit.json`. The recorded source hash ties this evidence to the
current profiles and placement code.
