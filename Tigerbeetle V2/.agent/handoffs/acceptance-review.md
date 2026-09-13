# Independent acceptance review — final geometry and mechanical gates

STATUS: Geometry interpretation and overlay review accepted as an explicitly provisional engineering reconstruction. One runtime validation omission was reproduced, fixed by the root agent, and independently verified closed. All three added negative regressions passed independently after the test fixture correction. Full PLAN completion remains unproven until refreshed provenance and the separately owned clean-checkout/release audit are complete.

FILES CHANGED: This handoff only. No production code, reference, artifact, or test changes.

## Required findings and closure

1. **Prior purchased-standoff failure: closed.** `validation/manufacturing.py` uses the unchanged 1.5 mm carbon ligament rule for carbon and a separate 1.0 mm purchased hardware wall rule. All five existing validation reports record 1.0 mm standoff walls and carbon minima >=1.6757 mm for the top plate; no carbon threshold was weakened.
2. **Prior ignored arm gap: closed.** `validation/clearances.py` checks every one of the six actual arm pairs against `manufacturing.general_clearance`, rejects positive material intersections, and reports distances. The negative test with a 2 mm requested clearance exercises that path. Nominal measured minimum is 0.290853 mm for a required 0.2 mm gap.
3. **Prior front drawing orientation: closed.** `drawing/svg.py` now observes from +Y with +Z up; the export regression explicitly checks projection arguments. This matches the documented frame convention.
4. **New required runtime gate omission: closed.** `validate_assembly` checked part inventory but accepted an empty manufacturing profile inventory, skipping all profile and ligament checks while reporting success. Direct reproduction on the actual default assembly:

   ```python
   model = build_assembly(get_preset())
   report = validate_assembly(replace(model, profiles={}))
   # report['valid'] == True
   # report['manufacturing']['checked_wire_pairs'] == 0
   ```

   Plate constructors also lacked an expected-opening-count runtime check; the existing count assertions were tests only. Root implemented profile inventory equality, expected openings (camera 30, rear 32, top 30, arms 8, standoffs 1), and solid/profile extrusion volume consistency. This reviewer inspected the correction and independently ran the three new negative regressions: missing profile and missing opening passed, but the solid/profile regression failed before reaching validation with StopIteration while selecting a central wire by w.center().X. Root was notified to correct the test fixture selection. An independent direct reproduction selecting the first noncircular aperture confirms the new volume gate rejects a filled actual top-plate aperture with its original manufacturing profile: ValueError "scan2_long: solid volume differs from its manufacturing profile extrusion". Root corrected the selector to Face(wire).center().X and isolated modified compounds by deep-copying parts. Independent rerun: 3 passed, 10 deselected in 3.77 seconds. The production correction and all three targeted regressions are now verified.
5. **Artifact provenance refresh needed, not a geometric defect.** Existing five preset report hashes differ from the current parameter tree because `layout.evidence.reason` now links to `references/measurements/combined.yaml` instead of an internal handoff. No geometric parameter differs. Regenerate current report/manifest snapshots before asserting current-source release freshness.

## Actual visual review

Inspected `artifacts/overlays/Scan_1_overlay.png`, `Scan_2_overlay.png`, and `references/assembly/user-assembly.png` using image viewing. Reviewed every outer outline, visible circular feature, and internal aperture of both arm tracings and all three plates. No omitted component, reversed plate, missing repeated top-deck aperture family, or new critical mating-feature discrepancy was identified.

The Scan 1 camera plate follows the broad traced contour and hole groups closely. Its shoulder and nose transitions are deliberate smooth reconstructions; the nose diamond remains a cosmetic approximation to a hand-rounded mark. Scan 2 rear plate retains the four central reliefs, tail slots, and symmetric restoration of incompletely marked holes. Scan 2 long plate retains all six paired diagonal relief rows, front vertical pair, central aperture, shoulder apertures, and the open nose. Local lobe/neck smoothing differs visibly from the ink, but no required interface or topology is removed.

Arm roots have the most obvious mismatch. The code and documentation explicitly identify a 35 × 29 mm reconstructed envelope versus an approximately 38 × 31 mm tracing. This is an actual change to the reconstructed part, not a claim of scan noise or exact identity. It preserves canonical handedness, mounting axes, shaft, paddle and motor centers while avoiding the demonstrated four-arm overlap. PLAN explicitly says the blueprint must not be blindly traced and prioritizes shared interfaces and coherent physical assembly. That local departure is acceptable for the documented engineering reconstruction; it must remain visible in released overlays and must not be sold as an exact replacement-part match.

The source photo is consistent with the adopted bottom rear plate → arms → camera/front plate clamp, and a raised long deck. Perspective does not establish exact support lengths. The user confirms 2/5/2 mm stock. H=25 mm, the 19 mm motor bolt circle, fastener dimensions and the modified roots retain provisional evidence. These are known physical assumptions, not missing software features or reasons to halt implementation for more measurements.

Observed directed outline max / mean and circular-center maximum, in mm:

| Component | Outline maximum | Outline mean | Hole-center maximum |
|---|---:|---:|---:|
| Camera/front plate | 1.530 | 0.215 | 0.300 |
| Arm tracing A | 2.411 | 0.595 | 0.691 |
| Arm tracing B | 3.896 | 0.734 | 0.704 |
| Rear/bottom plate | 1.832 | 0.450 | 0.701 |
| Raised top plate | 2.826 | 0.544 | 0.471 |

These are the actual `blueprint-fit.json` values, not manufactured pass thresholds. Nearest red ink is a directed and optimistic metric; it does not prove missing-feature detection or one-to-one hole identity. Independent source registration and actual BREP bore checks supply separate interface evidence. Visual acceptance above covers the internal features that this metric omits.

Reviewed overlay SHA256 values:

- Scan 1 PNG: `9d5ad539a6780463e7abd384aec50f5826764acec58527d220c77a07359e702b`
- Scan 2 PNG: `f8e46a7dd29f1b007515ae5c3719e7da8ff3539779e30105c770969a8d10b545`
- Fit report snapshot: `ef60dda0281df39764ca0fefdc99aa68e84fc26ea28220cdd9fb2576f9eba5b2`

## Mechanical evidence and equipment scope

Read the actual assembly, geometry, interface, interference, symmetry, manufacturing and equipment validators and their negative tests. The reported 88 bore checks inspect actual circular BREP rims and cylinder witnesses through the material; an internal plugged bore is tested. Symmetry reflects actual solid material and measures differences both ways across nine comparisons. Interference examines all 105 component pairs, with a bounding-box broad phase and exact Boolean material intersections for candidates. These are substantive checks, not comparisons of duplicated input parameters.

The default assembly now supplies explicit FC, ESC, camera and four stack-hardware envelope solids. Board keepouts and hardware share the central stack axes. All equipment-to-frame and equipment-to-equipment pairs use solid distance and intersection. Oversized boards, oversized camera, and an inadequately lowered top deck have negative regressions. Existing reports record 3 mm frame gap for FC/ESC, 2 mm for camera, 0.5 mm board-to-stack clearance, and intentional hardware face contact at 0 mm.

These checks prove fit of the documented 40 × 40 × 8 mm board envelopes and 20 mm camera cube at their modeled placements. They do not qualify unspecified connectors, camera mounts, cabling or screw engagement. Documentation states this accurately. No dimensioned side-panel part exists among the supplied three plate tracings; leaving side panels not applicable rather than inventing them is supported. The photograph's camera mount would need its own dimensions if later added as a manufactured part.

## PLAN §75 evidence map within this review

| Requirement | Current evidence / disposition |
|---|---|
| Both scans analyzed/calibrated; reconciled measurements | Measurement files, A4 calibration and independent registration review, plus actual overlays support closure. Later A4/photo/user thickness evidence supersedes earlier uncertainty statements in historical handoffs. |
| One coordinate system | Shared layout and consistent +Y front/+Z up; corrected front SVG. |
| Primary geometry parametric | Immutable parameter tree, shared layout deformation and canonical arm geometry inspected; changed-datum and changed-stock tests exist. |
| Intended exact symmetry | Actual mirrored BREP validation and zero reported symmetric material difference. |
| Shared slots/tabs | No observed separate mating tab/slot component to invent; identified mounting interfaces are shared. |
| Mounting holes align; canonical arms | Actual bore witness checks, shared placements and one canonical arm with reflection/rotation. |
| Assembly fits; geometry and collision validation | Existing actual all-preset reports pass, runtime profile inventory/count omission above is now corrected and independently exercised. |
| Parametric regression passes | Five reports present, all valid; refreshed snapshots and root's live final suite remain needed. |
| Overlay review passes | Accepted above, with explicitly visible and documented engineering departures. |
| No unresolved critical adversarial defects | No unresolved critical geometric defect found after finding 4 correction and three passing negative regressions; other specialist reviews remain separate. |
| STEP/STL/3MF/FCStd/SVG | Integration report records 15 components, 84 artifacts, 34 SVGs and actual FreeCAD 1.1.3 save/reopen with 15 solids. All 84 current artifact byte sizes and SHA256 values were independently checked against the manifest; report-to-manifest hash matches. Export specialist owns geometry import/mesh/reopen execution details. |
| CI reproduces from clean checkout | Root/release specialist owns execution; not established by this geometry review. |
| Tagged releases publish complete CAD artifacts | Release specialist owns workflow and publishing audit; source files alone cannot prove a hosted release ran. |

FreeCAD integration reports maximum save/reopen volume change 2.18e-11 mm³, consistent with retained geometry. Existing metadata honestly reports a dirty worktree. A clean committed final build should replace that provenance for the release candidate. Byte-identical STEP/3MF archives are not established and must not be promised; deterministic geometry rebuild is a separate requirement.

VALIDATION EXECUTED: Read-only source/test/document/report inspection; all supplied generated overlay images and photo viewed; bounded empty-profile-inventory reproduction; independent all-five report/current-parameter comparison; export manifest/report and all 84 artifact size/hash verification. Did not duplicate the root's full test suite or export specialist's full model export job.

FOLLOW-UP: Root must refresh report/manifest provenance, and obtain the separately owned clean-checkout and release-workflow evidence before the full-goal completion claim.
