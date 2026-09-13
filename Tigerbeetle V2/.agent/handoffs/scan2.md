# Scan 2 analyst handoff

STATUS: Independent analysis complete; absolute calibration and physical topology unresolved.

FILES CHANGED: `references/measurements/Scan_2.yaml`, `.agent/handoffs/scan2.md` only.

RESULT: Two separate planar plate profiles identified. Broad plate contains four quadrant cutouts, three rounded rectangular axial slots and 23 visible circular/C-shaped marks. Long plate contains six paired diagonal cutout rows, upper paired polygon and longitudinal cutouts, an ambiguous axial cutout, and 13 circular marks. Candidate bottom/top roles remain provisional. No dimensions, scale bar or orientation labels are visible.

MEASUREMENTS/DECISIONS: Native image is 2480×3508 pixels. Source SHA256 is `dc9a162303b5aac7b0e97a9b7a69105cf389d0419af6249525085e45f4241556`. All geometry observations remain source pixels. Broad-plate inner four-hole square pitch is approximately 362 px (edge observations 364, 358, 362, 363 px), with about 8 px practical uncertainty. Candidate 20 mm or 30.5 mm standards imply different scales; neither is confirmed. Paired features show probable bilateral symmetry with mild centerline drift; no fore/aft symmetry assumed. Full feature centers/bounds and metadata are in the YAML (JSON-compatible YAML 1.2).

ASSUMPTIONS: Components were drawn separately and their positions on the page are not assembly positions. Circular marks are candidate bores; ink widths are not exact diameters. Repeated paired contours suggest design symmetry. Plate functions, face directions, physical lengths/thicknesses and manufacturing tolerances are unknown.

VALIDATION EXECUTED: Inspected Scan_2.jpeg with view_image at default and original resolution. Parsed JPEG SOF dimensions using standard-library Python and verified `file` output. Read plan sections on independent analysis, pixel calibration, confidence and handoff contracts. Used ImageMagick read-only RGB extraction with red-stroke connected components to support visually identified feature bounds; did not trace profiles or generate CAD. Parsed output as JSON/YAML-compatible data and verified all geometric observations carry source/confidence/method metadata; all feature centers/bounds lie within source image dimensions. Source SHA256 rechecked unchanged. Initial Pillow metadata attempt failed because Pillow is unavailable; replaced with successful JPEG header parsing and ImageMagick.

KNOWN LIMITATIONS: Absolute calibration cannot be accepted from Scan 2 alone. Source aspect ratio does not prove A4 paper or 300 dpi. A missing upper-right broad-plate hole, unmatched small left-center mark, oversketched lower-right square-pattern bore, and crossing strokes in long-plate upper axial cutout need independent review. No visible thickness or stack order. These observations cannot yet establish a manufacturing-safe assembly.

FOLLOW-UP TASKS: Reconcile with Scan 1; compare standard hypotheses against independent anchors; identify actual plate roles/orientation; resolve missing/asymmetric hole marks and central cutout topology. If no independent anchor resolves scale, obtain a measured distance between the broad plate square-pattern hole centers and required material thicknesses. Keep physical dimension fields unknown until evidence is accepted by integration.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

Later A4 provenance, cross-scan registration and photo review supersede the initial unresolved scale and plate-role status. Missing/asymmetric ink marks remain preserved evidence.
