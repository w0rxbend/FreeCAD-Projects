# Independent calibration and blueprint review

STATUS: Review complete. Conditional calibration and shared XY interfaces withstand scrutiny; physical scale and Z assembly remain unverified. Detailed reconstruction under explicit, reversible assumptions is supported. Manufacturing/reference-identity approval is not supported by these scans alone.

FILES CHANGED: `.agent/handoffs/calibration-review.md` only. No commits; all source, measurements, code and other handoffs read-only.

RESULT: Both originals were visually inspected before independent numerical fitting. Three plates share convincing hole datums, with small residuals after separate rigid/similarity placement. The nested 20/30.5 mm interpretation is the strongest scale hypothesis. No physical annotation establishes absolute scale or stack order. Subsequent user confirmation establishes arms at 5 mm and plates at 2 mm; this supersedes the earlier thickness uncertainty. The workflow should continue with reviewed provisional parameters and honest uncertainty, without promoting assumptions to measured facts.

## MEASUREMENTS/DECISIONS

### Scale checks

Calculations below use native centers from the independent analyst files, with Euclidean distances recomputed independently. Reported decimals describe calculations, not scan accuracy. Approximate physical results are conditional on 11.8 px/mm.

| Scan 1 candidate | Four edge lengths, px | Mean pitch, px | Assumed pitch, mm | Implied scale, px/mm |
| --- | --- | --- | --- | --- |
| Upper inner square | 236.002, 235.002, 236.019, 236.008 | 235.758 | 20 | 11.7879 |
| Upper outer square | 361.001, 359.001, 360.022, 360.006 | 360.008 | 30.5 | 11.8035 |
| Lower repeated square | 359.000, 361.001, 362.001, 361.012 | 360.754 | 30.5 | 11.8280 |

The first two scales differ by 0.133%; their actual mean-pitch ratio is 1.5270, versus nominal 1.525. The existing rounded ratio 360/236 = 1.5254 is reasonable but should not imply precision beyond the raw centers. The repeated square differs from the outer square by 0.207%. These disagreements are much smaller than the analysts' 5–8 px center uncertainties. There is no evidence requiring anisotropic correction or independent part scaling. A4/300 dpi plausibility is corroboration only and does not add an independent physical measurement.

Motor A's four adjacent hole distances imply 13.22–13.81 mm; its two opposite-hole distances imply 19.179 and 18.998 mm. Motor B gives 13.22–13.64 mm adjacent and 18.877 and 19.116 mm opposite. This supports a provisional four-hole 19 mm bolt-circle diameter, rotated so holes form a square of side 19/sqrt(2) = 13.435 mm. A 19 mm **square side** implies a 26.870 mm circle and is decisively incompatible with these observations at the electronics scale. Motor brand/model compatibility remains unproven. No external motor notation was used as dimensional proof.

### Cross-scan registration

For each fit, P is an N×2 matrix of Scan 1 native (u,v) centers, Q is the corresponding Scan 2 centers, and Q_hat = s P R + t uses row vectors. Fit by centering, SVD of P_centered.T @ Q_centered, R = U @ Vh, s = sum(singular_values)/sum(P_centered**2), and t = mean(Q) - s mean(P) R. Both fits have determinant(R)=+1 and do not reverse/refelect the components.

Scan 1 broad region → Scan 2 broad plate:

- Correspondences: wing_tl→upper_left; wing_ml/mr→outer_upper_left/right; wing_ll/lr→outer_lower_left/right; wing_bl/br→shoulder_left/right; lower_inner_tl/tr/bl/br→square_upper_left/right/lower_left/right; lower_center_top/bottom→axis_upper/lower. Scan 1 names have the `plate_` prefix.
- 13 points; s=1.00261219; R=[[0.99989554,0.01445374],[-0.01445374,0.99989554]]; t=(-1165.79848,476.88814) px.
- RMS residual 2.599 px (~0.220 mm); maximum 4.973 px (~0.421 mm, upper axis mark).
- Translation-only fit also gives a modest maximum residual of ~0.770 mm; small relative rotation improves agreement substantially.

Scan 1 plate → Scan 2 long plate:

- Correspondences: tip_left/right→upper_tip_left/right; wing_tl/tr→middle_lobe_left/right; wing_bl/br→lower_lobe_left/right.
- 6 points across approximately 1,680 px longitudinal extent; s=1.00091778; R=[[0.99999463,-0.00327764],[0.00327764,0.99999463]]; t=(-29.86194,457.56290) px.
- RMS residual 2.161 px (~0.183 mm); maximum 3.234 px (~0.274 mm).

These are shared-feature registration residuals, NOT full CAD contour deviations or manufacturing tolerances. They provide strong evidence for common XY datums and same scale. They do not establish which plates contact, their vertical separation, bolt diameters or original front direction. Register each loose component separately; a single image-wide transform cannot assemble independently arranged parts.

### Concrete corrections and cautions

1. The standards handoff says the two broad regions align after orientation reversal. Their actual matching hole topology aligns in the **same image direction** with a small rotation/translation. Their narrow extensions point in opposite directions because these are different plates, not because one shared mounting region must be reversed.
2. Do not match similarly named large bores indiscriminately. The Scan 1 lower large-left opening maps to approximately (471.31,2094.87) in Scan 2: the small `extra_left` mark at (471,2092), not the large bore at (354,2093). The Scan 1 large-right maps to (897.38,2101.03), where no matching distinct mark is recorded. Scan 2 large bores at (354,2093)/(1016,2101) are another interface or feature family. Centers can coincide across different bore diameters, but diameters and roles must remain distinct.
3. Scan 2 broad plate's missing upper-right hole is predicted near the mirrored corner by the otherwise convincing registration. Symmetry restoration is reasonable provisional reconstruction, but must remain an explicit topology assumption. The unmatched small left mark may correspond to the Scan 1 left bore and therefore should not simply be erased as random drawing noise.
4. The two arm roots are not longitudinally symmetric. Their measured root-hole spans are ~13.394 and ~13.424 mm, while root slopes/contours have handedness. A single canonical arm with reflection and rotation can represent handed placements; imposing a symmetric root or using rotations alone requires further geometric review. Near-matching spans with plate outer-wing longitudinal pairs are evidence for a candidate attachment, not a proven assembled arm angle or root interlock.
5. The scans do not positively identify separate side/camera panels or mating tabs. Rounded rectangular apertures must not automatically generate fictitious matching parts. Architecture should support shared tab/slot objects where actual interfaces exist, without inventing them to satisfy example module names.

## ASSUMPTIONS

Reviewed and permissible for further implementation: nested pitches are provisionally 20/30.5 mm; the motor uses a provisional 19 mm opposite-hole spacing; intended plate bilateral symmetry overrides small ink asymmetry; all three plate feature groups share the registrations above. Choosing a front sign is a documented coordinate convention until actual front identity is established. User-confirmed thicknesses are arms 5 mm and plates 2 mm. Clearances, Z order and hardware assignments must be explicit engineering assumptions with their own status, never derived from page pixels.

## VALIDATION EXECUTED

- Read both original JPEGs with `view_image`, PLAN, both measurement files and all three independent analyst handoffs.
- Ran `.venv/bin/python` with `json`, `numpy` and `hashlib` for Euclidean anchor distances, motor adjacent/opposite distances, two independent least-squares similarity fits and original/source hash equality.
- Originals and preserved copies match: Scan 1 SHA256 `bf26be9035026002362046d18933f9032b9989aa3b0f0557132eea178eb3017e`; Scan 2 SHA256 `dc9a162303b5aac7b0e97a9b7a69105cf389d0419af6249525085e45f4241556`.
- No raster edits, physical measurements, CAD builds or assembly-fit tests were performed. No new standard claims were introduced.

## KNOWN LIMITATIONS / BLOCKERS

Pixel geometry plus a standards hypothesis cannot mathematically prove absolute size. Plan views contain no Z information. Thus detailed provisional CAD is feasible now, while a claim that it reproduces the original assembled physical frame and is ready for fabrication remains unsupported. This is not a reason to abandon parameter architecture, outlines, shared-hole interfaces, overlays or tooling.

The minimal decisive physical information is: (1) one named long hole-center distance, preferably the proposed 30.5 mm square, to fix scale; (2) an assembled side view or explicit stack order/plate separation (user has now confirmed arm stock 5 mm and plate stock 2 mm); (3) actual motor hole arrangement/diameter and arm attachment hardware; (4) confirmation of the few ambiguous/missing marks and the arm-root mating arrangement. Exact front nomenclature is lower priority than these fit dimensions. A single generic dimension cannot resolve all these independent uncertainties. Electronics/camera/propeller envelopes must also be specified or explicitly chosen before claiming compatibility with particular equipment.

## FOLLOW-UP TASKS

1. Reconciliation owner should record the conditional scale, explicit per-component registrations, topology assumptions and bore-role differences; correct the orientation-reversal statement without overwriting original independent observations.
2. Architecture/modeling can proceed from accepted provisional datums and interface contracts. Preserve uncertainty in parameters and generated reports, with manufacturing/reference approval distinguished from mathematical model validity.
3. Arm specialist should solve candidate two-hole attachments and inspect reflected canonical roots and possible collisions. Review root interlocks using profiles before freezing placements.
4. Overlay reviewer must evaluate actual generated curves against all component contours; the registration residuals here are not an overlay acceptance shortcut.
5. Obtain the listed physical information before asserting original-frame fit or treating manufacturing assumptions as verified specifications.
