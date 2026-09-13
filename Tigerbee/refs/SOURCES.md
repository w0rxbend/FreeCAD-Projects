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
