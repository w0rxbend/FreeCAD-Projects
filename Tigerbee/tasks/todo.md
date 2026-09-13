# Implementation tasks

- [x] Locked Python/build123d project, CLI, presets and export pipeline.
- [x] Preserve original FreeCAD/3MF sources and independent STEP baselines.
- [x] Reconstruct the original profiles explicitly for source regression checks.
- [x] Replace rear/top scan irregularities with nominal analytic geometry.
- [x] Mirror the camera CAD silhouette and preserve its refined openings.
- [x] Restore all accessory features with symmetric nominal geometry.
- [x] Share arm/plate/support coordinates; remove independent hole fitting.
- [x] Mirror matched arm pairs with equal nominal 303.5 mm motor diagonals.
- [x] Resolve root collisions and electronics fastener passages with rounded relief.
- [x] Check actual-solid symmetry, axes, passages, interference and mounting ligaments.
- [x] Check intended opening counts, tangent plate perimeters and 7-inch disc clearance.
- [x] Guard invalid parameter variants and mismatched CLI bore defaults.
- [x] Require passing actual-solid audit before every assembly export.
- [x] Finish canonical regeneration, native reopen and final export inventory audit.
- [x] Inspect final exported component and assembly views.
- [x] Run the full final test suite (108 tests) and package/lint/type checks.
- [ ] Verify GitHub Actions execution after the branch is pushed.

Physical production release remains a separate unresolved part of the overall
production-grade frame objective:

- [ ] Confirm rear/top stock thickness, vertical stack and purchased standoffs.
- [ ] Confirm bolt/nut and camera/end-bracket dimensions; model those accessories.
- [ ] Establish material/layup and machining tolerances.
- [ ] Validate manufactured fit and load performance.
