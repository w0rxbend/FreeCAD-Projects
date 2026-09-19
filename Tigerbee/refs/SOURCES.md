# Reference authority and design intent

The user's latest clarification ranks **Tigerbee.FCStd and the three supplied
3MF files above the pen scans**:

1. `Tigerbee.FCStd` and `Tigerbee-Arm (type 1).3mf`,
   `Tigerbee-Arm (type 2).3mf`, `Tigerbee-Base plate (camera side).3mf` define the
   arm and camera-plate design foundation. The FreeCAD solids supply analytic
   curves and nominal thicknesses: arms 5 mm, camera plate 3 mm. The supplied
   meshes independently carry those same thicknesses and matching overall bounds.
2. `Scan_2.jpeg` supplies the rear/top plates absent from those CAD files.
   Its pen irregularities are replaced by analytic, symmetric nominal features.
3. The latest [confirmed design dimensions](measurements.md) specify a 305 mm
   true X, 5 mm arms, 3 mm plates and 6 mm standoff outside diameter. These supersede
   the earlier approximate 303–304 mm reading and all photo wheelbase labels.
4. `Scan_1.jpeg` and product photos support interpretation of the design and assembly.

The user also explicitly requested ideal symmetry, fixed parametric dimensions,
and exact assembly interfaces. Accordingly the generated design is a refinement
of these references, not an exact reproduction of their asymmetries. Camera
openings include the valid 15 × 15 mm R2 central opening added in FreeCAD.
Arm motor pads, shafts, root-hole geometry and thicknesses remain based on the
saved CAD; left/right pairs are mirrored and interfering root tips receive a
small, explicit relief. Shared plate holes derive from the actual placed arm
bores rather than independent fits to drawings.

The original FreeCAD, 3MF, scan and baseline STEP files are preserved. Reference
reconstruction tests still verify the saved FreeCAD geometry independently of the
refined design. The generated `exports/` files are the current design deliverables.

The historical A4 comparison, registered overlays and old placement audit are
historical diagnostics, not design authority or acceptance gates. They are not
required to build or validate the refined frame.
