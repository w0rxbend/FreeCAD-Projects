# FPV standards analyst handoff

STATUS: Analysis complete; physical dimensions remain hypotheses pending reconciliation or measurement.

FILES CHANGED: `.agent/handoffs/standards.md` only.

RESULT: The best independent scale hypothesis is a nested 20 mm / 30.5 mm electronics pattern in Scan 1's right-hand plate. Manufacturer documentation establishes that these patterns exist, but cannot establish that this unidentified frame uses them. No thickness or assembly height can be recovered from these plan views.

## Measurements / decisions

Both source files are 2480 × 3508 pixels. `file` and a JPEG APP-segment inspection find only EXIF orientation, with no physical-resolution anchor. Their aspect ratio and pixel dimensions are consistent with an A4 page at 300 dpi; this is a weak supporting hypothesis, not calibration evidence by itself. A hypothetical 300 dpi scale is 11.811 pixels/mm.

Independent visual observations (approximate; figures below use the rendered 1335 × 1888 image for locating features, not authoritative native-pixel measurements):

| Candidate | Observation | Inferred dimension | Confidence / alternatives |
| --- | --- | --- | --- |
| Scan 1 plate inner square | Centers around (940,400), (1067,400), (940,527), (1067,527); ~127 px side | 20 mm if this is a mini electronics mount | Medium; could be a nonstandard mounting pattern |
| Scan 1 plate outer square | Centers around (907,367), (1101,367), (907,560), (1101,560); ~194 px side | 30.5 mm if this is a full-size electronics mount | Medium; nested ratio 127/194 ≈ 0.655 closely matches 20/30.5 ≈ 0.656 |
| Scan 1 plate second square | Centers around (910,758), (1103,758), (910,953), (1103,953) | Another ~30.5 mm square under the same scale | Medium; repeated independent geometry supports uniform scan scale |
| Scan 2 left plate square | Centers around (272,1030), (467,1031), (273,1224), (467,1227) | Another ~30.5 mm square | Medium; connects scales between scans if the physical patterns are shared |
| Scan 1 arm motor holes | About 85–88 px adjacent spacing; about 120–123 px diagonally opposite | Adjacent spacing ~13.4–13.9 mm and opposite spacing ~19 mm under electronics calibration | Low; MUST distinguish square side from diameter/opposite-hole spacing |
| Source page dimensions | 2480 × 3508 px | Approximately 210 × 297 mm at 300 dpi | Estimated; no metadata proves page size or scanner scale |

These approximate observations independently suggest ~11.8 native pixels/mm. A calibration agent should extract native-pixel centers and residuals before recording a numerical transform. Do not silently average incompatible anchors.

## Verified primary manufacturer sources

Accessed 2026-09-13. These document actual products; none identifies the scanned frame.

- [SpeedyBee F405 V4 stack](https://www.speedybee.com/speedybee-f405-v4-bls-55a-30x30-fc-esc-stack/): mounting pitch 30.5 × 30.5 mm, board mounting holes 4 mm. The ESC envelope is 45.6 × 44 × 8 mm, demonstrating that mounting pitch is not the electronics clearance envelope. Board holes accommodating isolation hardware do not prescribe carbon-frame hole diameter.
- [SpeedyBee F405 Mini stack](https://www.speedybee.com/speedybee-f405-mini-bls-35a-20x20-stack/): 20 × 20 mm mounting, 3.5 mm board holes, compatible with M2 or M3 screws and silicone grommets. Consequently a 20 mm pitch does not uniquely identify frame fastener size.
- [iFlight XING2 2207](https://iflight-rc.eu/en-se/products/xing2-2207-2-6s-fpv-motor): manufacturer specifies `16*16 φ3mm` mounting and supplied M3 screws. Its motor envelope is Ø29 × 19.25 mm. Treat the prose mounting notation cautiously until an actual drawing establishes coordinate meaning.
- [iFlight XING 2806.5](https://shop.iflight.com/xing-x2806-5-fpv-nextgen-motor-pro1001): manufacturer specifies `19*19 φ3mm` mounting and M3 screws. This establishes a plausible 19 mm family, not the measured motor or the distinction between adjacent and opposite holes. The linked product image inspected was a photograph, not a dimensioned drawing; no dimensional drawing was verified during this task.
- [iFlight AOS UL7 V5](https://iflight-rc.eu/en-gb/products/aos-ul7-v5-fpv-frame-kit): an actual frame offering several electronics pitches, 16/19 mm motor mounting, 3 mm arms, and 2 mm top/bottom/side plates. These are examples of one design, not a universal material-thickness standard. The page itself mixes rounded `30*30` text with `30.5x30.5` descriptive text, illustrating why informal product labels should not override dimensioned evidence.

## Component identity and interfaces

- Scan 1 contains two long motor-arm-like profiles and one body plate; the central circular hole plus four small surrounding marks make the arm interpretation high confidence. Two drawings do not prove four distinct arm designs, nor do apparent root-profile differences prove they are identical. Reconciliation must test reversal/reflection and preserve residual differences for review.
- Scan 2 contains two body-plate-like profiles. The broad portion of its left plate shares mounting geometry with the broad end of Scan 1's right plate after orientation reversal. The long perforated right-hand profile is a plausible top plate, but its exact physical role and Z placement are unconfirmed.
- No isolated vertical side panel or camera plate is positively identified. Rectangular openings in these horizontal profiles may be strap passages or weight-relief cutouts; calling every opening a tab slot and inventing matching parts would be unsupported.
- Front/rear cannot be established from outline shapes alone. An assembly photograph or original part names would resolve this better than convention.

## Assumptions and limits

The 20/30.5 pair is a strong scale *candidate*, not a known physical dimension. Different intended patterns or a scaled print could produce similar outlines. A frame-specific ruler measurement is still the decisive validation.

Motor mounting is a critical trap: a square of side 19 mm has opposite-hole distance 26.87 mm. A four-hole circle of diameter 19 mm, rotated 45 degrees, has square side 13.435 mm. At the electronics-derived scale the scan visually supports the latter geometry. Do not force the raster to a 19 mm square, and do not declare compatibility with a particular motor without a dimensioned manufacturer drawing or physical bolt-center measurement. Alternatives include another pattern size, drawing omissions/oversize marks, or unequal scaling; analyze residuals before choosing.

Red pen stroke width, small filled marks, and hand-drawn circles make hole diameter a much weaker anchor than center-to-center distances. No M2/M3 assignment is confirmed. Carbon thickness, standoff height, arm sandwich order, fastener head clearance, press-nut dimensions, camera envelope, propeller diameter and wheelbase require physical information or explicit design assumptions.

## Validation executed

- Read both original JPEGs visually, independently of scan analyst findings.
- Read the plan, especially calibration, mechanical standards, task/handoff contracts and integration gates.
- Verified native JPEG dimensions and inspected EXIF APP data with Python standard library; no source files changed.
- Browsed manufacturer product pages for the dimensions cited above.
- Attempted a manufacturer motor illustration lookup; downloaded and inspected an image, found it was a product photo, and did not claim it proved dimensional geometry.

KNOWN LIMITATIONS: No authoritative physical frame dimensions supplied; no motor dimension drawing verified; visual coordinate estimates intentionally coarse.

FOLLOW-UP TASKS:

1. Independently reconcile native-pixel nested-pattern centers, repeated body holes and motor-hole diagonals; compute separate anchor scales and errors.
2. Obtain at least one long physical center-to-center distance or actual board/motor specification matching these parts.
3. Confirm individual material thicknesses and assembled plate separation/arm sandwich order, ideally from a side-view photograph with measurements.
4. Preserve provisional parameters and manufacturing assumptions explicitly until confirmed; passing CAD geometry tests cannot prove those assumptions describe the source frame.
