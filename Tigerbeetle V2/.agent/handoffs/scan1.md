# Scan 1 independent analysis handoff

STATUS: Complete for independent observation; calibration remains provisional.

FILES CHANGED:
- `references/measurements/Scan_1.yaml` (JSON-compatible YAML)
- `.agent/handoffs/scan1.md`

RESULT:
Scan 1 contains two separate long arm profiles, oppositely oriented on the page, and one body plate with bilateral intent. Original image is unchanged. No physical dimension, orientation label, thickness, scale bar or reliable resolution unit appears in this evidence. Do not infer assembly placement from layout on paper.

MEASUREMENTS/DECISIONS:
- Native image 2480 x 3508 px; SHA256 `bf26be9035026002362046d18933f9032b9989aa3b0f0557132eea178eb3017e`.
- All coordinates in YAML are native image pixels (+u right, +v down). Red-ink bounding box centers within visually selected feature windows; typical reporting uncertainty +/-6 px. Pixel values are observations, not primary CAD parameters.
- Body plate: 22 small hole outlines, five larger round openings, two rounded rectangles, one diamond/teardrop opening.
- Upper nested squares have approximately 236 px and 360 px pitch. Ratio 1.525 is consistent with a candidate 20 mm / 30.5 mm pair, both yielding approximately 11.8 px/mm. Lower square repeats approximately 360 px. This supports a hypothesis, not an accepted physical calibration.
- Both arm motor marks give approximately 160 px square pitch. Under that plate scale this implies approximately 13.6 mm; imposing a 16 mm or 19 mm square silently would be contradictory. Investigate motor pattern interpretation/source scaling.
- Each arm has two diagonal root marks. Root-hole slopes differ after rotating the motor ends into the same direction, supporting possible handedness. Their root outlines also differ; do not force longitudinal arm symmetry or identical rotation-only copies without reconciliation. A canonical arm with mathematical mirroring remains a candidate.
- Plate is nearly bilaterally symmetric, but longitudinal fore/aft symmetry is unsupported. No global front datum accepted here.

ASSUMPTIONS:
- Red ink depicts component boundaries/features; filled arm dots are candidate holes, with low semantic confidence.
- Narrow plate end may be front; only a hypothesis.
- Stated mm standards are candidates requiring the standards analyst and independent calibration reviewer.

VALIDATION EXECUTED:
- Inspected original through `view_image`.
- `file`, `identify -verbose` checked native image size and metadata (Units: Undefined).
- SHA256 checked source integrity.
- Native RGB red-ink windows measured without modifying or writing an image.
- Parsed measurement file with Python JSON parser and checked feature centers within native image bounds; JSON syntax is valid YAML 1.2.

KNOWN LIMITATIONS:
Ink does not establish fit, exact manufactured hole centers, material, thickness or absolute scale. No derived image/overlay is produced in this observation-only assignment. Pillow unavailable in system Python; ImageMagick provided equivalent read-only raster measurement. Full source analysis inspected ONLY Scan_1.jpeg, intentionally independent of Scan_2.

FOLLOW-UP TASKS:
1. Reconcile both scan reports while preserving contradictory evidence.
2. Have standards/calibration reviewer assess nested patterns, motor marks and possible scale differences.
3. Resolve arm handedness, root interlock and which plate features receive those fasteners.
4. Obtain a physical anchor if independent evidence cannot establish absolute scale. Do not pass manufacturing calibration with estimated scale alone.
5. Resolve thickness/clearances and front/up orientation before dependent detailed geometry.
