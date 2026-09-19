# Blueprint reconstruction

The user made the drawings by placing A4 paper against the actual frame parts
and tracing them. Original JPEGs and byte-identical preserved copies are retained;
`references/source/SHA256SUMS` records their integrity. Source images must never
be overwritten by calibration or overlay generation.

The full-page interpretation maps 2480 × 3508 pixels onto 210 × 297 mm:
11.809524 px/mm horizontally and 11.811448 px/mm vertically. The isotropic
calibration uses 11.810486 px/mm. The disagreement is below 0.02%, with independent
nested 20/30.5 mm and repeated 30.5 mm mounting patterns supporting the scale.
Full-sheet coverage remains explicit; a cropped scan must not reuse this transform.

Independent observations are in `Scan_1.yaml` and `Scan_2.yaml`; reconciliation,
exact correspondences, transform residuals and feature identities are in
`combined.yaml`. All three are under `references/measurements`. The independent
analyst reports intentionally retain their original hypotheses. Later user
clarifications and accepted corrections supersede those hypotheses.

## Source coordinate mapping

The parts were laid out separately on the paper. Each part therefore needs its
own pixel-to-CAD transform. Applying one transform to an entire scan would turn
paper placement into false assembly coordinates.

Scan 1's body plate is the cross-scan master. Its lower stack pattern center is
at native pixel (1870.5, 1588.75). A small measured centerline tilt is removed
before exact bilateral symmetry is imposed. The global frame XY datum is then
derived from the four motor centers. Source Y points down; frame +Y points toward
the camera/front, toward decreasing source Y. +X is right and +Z is up.

The Scan 2 broad plate and long plate align in the same longitudinal direction
as the master. Earlier reversal speculation was disproved by shared hole fits.
Cross-scan RMS residuals are approximately 2.61 and 2.16 pixels (0.22/0.18 mm).
These are registration residuals, not proof of contour fit.

## Geometry interpretation

Scan 1 shows one camera/front plate and two differently oriented arm tracings.
Scan 2 shows the rear/bottom plate and the raised, perforated top deck. The user
assembly photo is preserved in `references/assembly/user-assembly.png`. Together
with matched hole groups it supports the overlapping lower clamp sandwich.

The arm's two root holes and root contour are handed. Only the motor paddle is
approximately longitudinally symmetric. A canonical arm must be reflected and
rotated, not independently redrawn four times. Root fastening coordinates must
come from the same interface used to cut the receiving plates.

The traced root envelope is approximately 38 × 31 mm. With the reconciled root
axes and four handed placements, that envelope intersects neighboring arms. The
canonical reconstruction therefore uses 35 × 29 mm, locally reducing the root
outline while retaining bolt axes, motor center, shaft and paddle dimensions.
This is an explicit engineering departure from the tracing, not additional source
measurement. The original observations remain in the measurement records; the
parameter evidence records the change and its need for physical confirmation.
Overlay residuals at these root edges must remain visible rather than being
excluded to improve a fit score.

Motor marks support approximately 19 mm opposite-hole spacing: a bolt circle
of diameter 19 mm has square side 19/√2 mm. A 19 mm square is incompatible with
the scan. This interpretation does not identify a particular motor catalogue part.

Hand-drawn centers have practical uncertainty of roughly 5–8 pixels; contour
observations roughly 12 pixels. Small asymmetry is corrected mathematically.
Missing symmetric hole marks must be explicitly identified when restored. A
rounded rectangular aperture is not evidence of an unobserved mating tab or panel.

The photo supports the order rear/bottom plate → arms → camera/front plate, with
the long deck raised on supports. User-confirmed 2/5/2 mm stock gives Z intervals
0–2, 2–7 and 7–9 mm. The top deck occupies 34–36 mm only under the provisional
H=25 mm face-clearance assumption. The photograph does not establish that height.

## Validation evidence

The overlay pipeline draws actual CAD edges over unchanged source images,
including datum axes, hole centers and shared interface centers. Diagnostic edges
are sampled at 0.25 mm or finer; manufacturing outlines must use the actual CAD
curves. Review must cover every component in both scans, not only the central
mounting pattern. A contour fit report must distinguish outline residuals from
critical-hole residuals and identify ambiguous manual marks.

Run `fpv-frame overlay scan-1` and `fpv-frame overlay scan-2` from the project
directory to generate both SVG/PNG overlays. The commands also write current
per-part transforms to `references/calibrated/registrations.json` and a fit report
with its parameter snapshot to `artifacts/reports/blueprint-fit.json`.

The quantitative outline metric is directed: sampled CAD exterior points are
compared with their nearest red source-ink pixel. It reports maximum and mean
distance in millimeters. Ink width makes that distance optimistic, and a nearby
unrelated stroke can become the nearest match. It does not establish that every
source contour was modeled, nor does it assess every internal cutout boundary.
Full-overlay visual review must therefore cover both exterior and internal features.

Circular-hole diagnostics compare observed centers with the nearest generated
circular center and report individual residuals separately from outlines. This
nearest-center operation does not prove feature identity, a one-to-one assignment,
or mechanical mating. Shared-interface correspondence and actual BREP bore-axis
checks provide that separate evidence. Registration RMS, drawing fit and mechanical
assembly clearance answer different questions and must not be substituted for
one another.
