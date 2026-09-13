# Implementation tasks

- [x] Locked Python/build123d project, CLI, presets and export pipeline.
- [x] Preserve original FreeCAD/3MF sources and independent STEP baselines.
- [x] Reconstruct the original profiles explicitly for source regression checks.
- [x] Replace rear/top scan irregularities with nominal analytic geometry.
- [x] Mirror the camera CAD silhouette and preserve its refined openings.
- [x] Restore all accessory features with symmetric nominal geometry.
- [x] Share arm/plate/support coordinates; remove independent hole fitting.
- [x] Mirror matched arm pairs with a square true-X motor layout and perpendicular 305 mm diagonals.
- [x] Resolve root collisions and electronics fastener passages with rounded relief.
- [x] Trim exposed arm bases to the common lower clamp envelope with tangent shaft transitions.
- [x] Reject root protrusions using actual plate and arm geometry; inspect the lower stack overlay.
- [x] Check actual-solid symmetry, axes, passages, interference and mounting ligaments.
- [x] Check intended opening counts, tangent plate perimeters and 7-inch disc clearance.
- [x] Guard invalid parameter variants and mismatched CLI bore defaults.
- [x] Require passing actual-solid audit before every assembly export.
- [x] Finish canonical regeneration, native reopen and final export inventory audit.
- [x] Inspect final exported component and assembly views.
- [x] Run the full final test suite (146 tests) and package/lint/type checks.
- [ ] Verify GitHub Actions execution after the branch is pushed.

Physical production release remains a separate unresolved part of the overall
production-grade frame objective:

- [x] Apply user-confirmed plate stock 3 mm, arm stock 5 mm and standoff outside diameter 6 mm.
- [x] Retain top underside Z=35 mm and derive six 24 mm/two 32 mm standoffs.
- [ ] Confirm bolt/nut and camera/end-bracket dimensions; model those accessories.
- [ ] Establish material/layup and machining tolerances.
- [ ] Validate manufactured fit and load performance.
