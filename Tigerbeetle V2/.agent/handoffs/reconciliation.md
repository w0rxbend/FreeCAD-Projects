# Cross-scan reconciliation handoff

STATUS: Complete for proposed observation reconciliation, component correspondence and calibrated physical scale. User subsequently confirmed A4 physical tracing provenance; XY scale is now accepted at high confidence under full-page/no-resize assumptions. User-confirmed thicknesses are known inputs.

FILES CHANGED:
- `references/measurements/combined.yaml` (JSON-compatible YAML)
- `.agent/handoffs/reconciliation.md`

RESULT: Three mutually registered plates, one canonical handed arm family, nine shared interface groups and explicit pixel-to-pixel similarities are available for architecture and geometry implementation. Original independent measurements and JPEGs remain unchanged.

MEASUREMENTS/DECISIONS:
- Scan 1 body → Scan 2 broad: `q=(1.002590688+0.014779536i)*p+(-1165.506411+476.020526i)`, 14 explicit feature correspondences, RMS 2.611 px, max 5.010 px. Same longitudinal direction; the standards handoff's reversal interpretation is contradicted by the complete hole constellation.
- Scan 1 body → Scan 2 long: `q=(1.000912406−0.003280649i)*p+(-29.861943+457.562899i)`, six correspondences, RMS 2.161 px, max 3.234 px.
- Here `p=u+i*v` and `q=target_u+i*target_v`, with native image coordinates. Each component has an independent page placement; never apply one whole-scan transform.
- Broad tail-tip versus long lower-tip centers were excluded from both fits. Mapping both back into the body master gives independent residuals 4.152 and 4.718 px, supporting the same three-plate registration.
- Arm A → B: `q=(1.003040214+0.000934276i)*conj(p)+(561.749388+3497.189850i)`, seven motor/root correspondences, RMS 4.122 px, max 7.767 px. The conjugation is essential: opposite handedness is supported; pure rotation copies do not reproduce the root-hole slope. Preserve an asymmetric root and generate reflected counterparts.
- Mean square pitches: upper inner 235.758 px, upper outer 360.008 px, lower outer 360.754 px. The corresponding 20/30.5/30.5 mm hypotheses yield 11.787897, 11.803529 and 11.827994 px/mm. Select the upper-outer 30.5 hypothesis explicitly as provisional scale 11.803529 px/mm; the other patterns are checks, not silently averaged anchors.
- Motor A/B mean square sides at provisional scale: 13.492/13.430 mm. Mean opposite-hole distances: 19.083/18.991 mm. A 19 mm bolt-circle/opposite-hole hypothesis fits; a 19 mm square does not. Manufacturer compatibility remains unconfirmed.
- Arm A local datum is midpoint of root marks; +Y points to motor center. Root holes are approximately (−62.859,+47.894), (+62.859,−47.894) px; motor is (0,1354.213) px. Arm B gives mirrored root chirality and root-to-motor length 1365.132 px. Root pitches 158.051/158.405 px differ only a few pixels from the candidate body outer vertical bolt pairs. Reconcile to a shared engineering interface within observation uncertainty; do not scale arms during assembly to force a fit.
- `engineering_interface_groups` identifies front tip, front outer/inner arm, rear inner/outer arm, rear tip, central square, central axial and central inner lateral hole groups by their exact source feature IDs.
- Scan 2 broad `extra_left` is supported as a counterpart of Scan 1 `plate_lower_large_left`; its right counterpart remains absent in Scan 2. The first broad upper-right perimeter hole is also absent. Missing marks remain explicit topology decisions, not silently added holes.
- User supplied 5 mm arms and 2 mm plates through orchestrator; recorded as known user dimensions.
- Inspected assembled user photograph `/tmp/codex-clipboard-NWppFv.png`: the lattice/long profile is the raised top deck; its large open fork is the camera/front end. This supports +Y toward smaller scan-native v. The other two plates occupy the lower arm/body region. Dedicated photo reviewer owns exact Z sandwich inference; occluded relationships are not resolved here.

ASSUMPTIONS: The nested electronics standard is a plausible physical-scale hypothesis, not a measured identification. Hole-center correspondences are much stronger than pen diameters. Bilateral nominal symmetry is supported; fore/aft plate symmetry is not. Z stack, actual bores, motor compatibility, hardware and clearance envelopes remain independent engineering inputs.

VALIDATION EXECUTED: Read PLAN and independent scan/standards handoffs; visually inspected both original scans and assembled photo; computed least-squares similarities with standard-library complex arithmetic; re-parsed combined output; reproduced every fit residual from serialized coefficients within 3e−6 px; rechecked immutable source SHA256 hashes; confirmed 5/2 mm user dimensions and the initial provisional flag; after A4 update, verified selected scale equals geometric mean of page-axis scales and manufacturing-calibration=true refers only to XY scale. No geometry was generated in this bounded task.

KNOWN LIMITATIONS: Fit digits allow deterministic transforms, not micrometer precision. Centers typically carry ±5–8 px uncertainty; contour error is greater. Photograph is not a metric calibration image. Shared axes do not prove equal bore diameters or stack order. Original scan observations are preserved, including uncertainties.

FOLLOW-UP TASKS:
1. Architecture owner accepts one global geometric-center datum and mathematically idealized interface positions using these registered observations.
2. Calibration/photo reviewer reviews scale and exact layer order; A4 page calibration is accepted; full-page/no-crop assumptions remain explicit.
3. Geometry agents build canonical half-profiles and one mirrored arm family, then produce overlays against all five source component drawings.
4. Explicitly resolve missing broad holes, ambiguous top axial cutout lower edge and arm root notch contour. Confirm bolt diameters and required envelopes.

## Subsequent user A4 provenance update (supersedes standard-only scale above)

User confirmed both scans were made from A4 tracing paper placed against actual frame parts. The sheet is an independent physical anchor. Horizontal scale is 2480/210 = 11.80952381 px/mm; vertical scale is 3508/297 = 11.81144781 px/mm. Selected isotropic geometric mean is 11.81048577130682 px/mm. Axis mismatch is only 0.0163 percent, and all independent nested/repeated pattern checks agree within pen uncertainty. `calibration.selected_scale` is now authoritative; the earlier standard-only scale is retained as historical evidence. Full-page extent, no material crop/padding and no component resize are explicit high-confidence assumptions. Manufacturing calibration flag is true for accepted XY reference scale; overall manufacturing readiness remains unproven. All dependent calibrated motor measurements and anchor residuals were recomputed. No additional physical XY dimension is needed to start calibrated geometry.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

The explicit A4 update above supersedes the initial standards-only scale. Later analytical layout, root correction and full overlay review are recorded in the linked reconstruction and acceptance documents.
