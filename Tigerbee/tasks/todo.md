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
- [x] Record current mounting axes, Z stacks and equipment dimensions needed for hardware selection.
- [ ] Establish material/layup and machining tolerances.
- [ ] Validate manufactured fit and load performance.

## Arm protector / landing feet

- [x] Review five inspiration images and use actual current motor pads for fit.
- [x] Model separate type 1 / type 2 protectors and mirrored left copies.
- [x] Add 12 mm feet, flat coplanar supports and recessed motor screw access.
- [x] Add CLI, separate STEP/STL/3MF, fit reports and assembled preview.
- [x] Complete native reopening, visual review, 158 tests, lint/types and 75-output inventory.

## Top-plate GoPro holder

- [x] Inspect three inspiration images and actual front top-plate holes.
- [x] Model registered M3 base and adjustable M5 three-finger interface.
- [x] Verify carbon, bolt/tool access, mating finger sweep and captive nut fit.
- [x] Complete separate exports, native reopen, visual review, 175 tests and 87-output inventory.

## Reference fidelity and independent acceptance review

- [x] Compare the original four user images, saved tracing and current CAD with independent agents.
- [x] Restore both paired top side tabs with tangent R2/R1 geometry and nominal scan dimensions.
- [x] Verify four additions, zero removed material, all 30 openings retained and exact reflection.
- [x] Reject incomplete canonical delivery sets even when omitted files are absent from the manifest.
- [x] Require actual GoPro pivot bearing material and an unobstructed captive nut seat.
- [x] Finish 270 tests, canonical rebuild, 13 native reopen checks and the 20-solid exported assembly audit.

See the [current fidelity review](../refs/analysis/fidelity-review.md) for evidence
and the remaining equipment-dependent work. The full physical frame objective
remains open; this review verifies the current CAD deliverables.
