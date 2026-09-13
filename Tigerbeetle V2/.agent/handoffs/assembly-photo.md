# Assembly photo review

STATUS: Independent interpretation complete. Three plate roles and a coherent vertical stack are identified; absolute top-deck height remains an engineering assumption.

FILES CHANGED: `.agent/handoffs/assembly-photo.md` only for this extension. `.agent/handoffs/calibration-review.md` updated separately to acknowledge user-confirmed thicknesses. No geometry or source files changed.

RESULT: The screenshot shows four coplanar arms clamped in a low central sandwich and a raised lattice deck on standoffs. The wide fork of the lattice deck is the camera/front end, visible in the foreground of the main screenshot. The narrow fork is the rear. The two remaining scanned plates extend in opposite directions from their shared central clamp region. Treating all three plates as one coextensive stack would be wrong.

## INPUTS AND SOURCE PRIORITY

- Current user screenshot: `/tmp/codex-clipboard-NWppFv.png`, visually inspected with `view_image`.
- Current user measurements, relayed by orchestrator: arms 5 mm, plates 2 mm. These are the authoritative stock thicknesses.
- Both current scan originals and prior independent center-registration calculations.
- Secondary family illustrations inspected read-only: `../Tigerbee/refs/product/product-03.png`, `product-04.png`, `product-05.png`, `product-06.png`; context from `../Tigerbee/refs/product/README.md` and `../Tigerbee/refs/mounting-interfaces.md`.

The sibling is another revision. Its CAD dimensions, 3 mm plates, nominal wheelbase, 24/32 mm supports, hole sizes and other equipment choices were NOT transferred. Product06 has additional advertised dimensions that do not establish dimensions of this V2. The screenshot alone occludes much of the central sandwich; the secondary views inform the probable layer order, not precise dimensions.

## MEASUREMENTS/DECISIONS

| Scanned component | Assembly role | Confidence and evidence |
| --- | --- | --- |
| Scan 2 long perforated plate | Raised top deck | High: distinctive paired diagonal cutouts and unequal open forks identify it directly in the screenshot. |
| Scan 1 main plate | Camera/front lower deck and upper arm-clamp plate | High for front identity and paired-hole registration; medium/high for position above arms, supported by secondary close views and family mounting schedule. Narrow three-lobe end lies under the wide camera fork. |
| Scan 2 broad plate | Rear lower deck and bottom arm-clamp plate | High for rear identity from three repeated strap openings and tail-tip pairing; medium/high for position below arms, supported by secondary views and family schedule. |
| Scan 1 arm observations | Canonical motor-arm geometry with handed placements | High motor-arm identity. Four assembly arms are visible. Root interlock/handedness still needs profile and collision review. |

Suggested global orientation: +Y toward the wide camera fork, matching decreasing native v in the registered plates; -Y toward the narrow rear fork. +Z up. Plate positions come from shared feature registration, not screenshot perspective dimensions.

Use Z=0 at the underside of the rear/bottom plate. With plate stock p=2 mm and arm stock a=5 mm, the supported provisional construction is:

| Part | Z interval, mm |
| --- | --- |
| Rear/bottom plate (Scan 2 broad) | 0 to p = 0–2 |
| All four arms | p to p+a = 2–7 |
| Camera/upper-clamp plate (Scan 1 main) | p+a to 2p+a = 7–9 |
| Top deck (Scan 2 long) | 2p+a+H to 3p+a+H = 9+H to 11+H |

H is the free face-to-face distance from camera plate top to top-deck underside. This expression does not assign H a measured value. The front clearance is H while the rear clearance above the bottom plate is H+a+p = H+7 mm. The central clamp material stack is p+a+p = 9 mm. At electronics axes outside arm material, the same 9 mm envelope contains two 2 mm plates separated by a 5 mm gap; fasteners must not crush that unsupported gap.

Eight candidate top-deck support axes are strongly supported by plate geometry: six short supports at the two camera-tip holes plus the front/rear outer-wing pairs; two longer supports at the rear-tail tips. Their clear body lengths follow from attachment faces:

- Six short supports: H.
- Two rear supports: H+a+p = H+7 mm.

Derive this difference from stock thickness. The sibling's 24/32 mm pair is tied to 3 mm plates and therefore must not be imported as V2's lengths. The numerical H choice remains independent of the difference.

All shared fasteners require a single axis owner. The four wing support axes also coincide with outer arm clamp axes; remaining inner arm clamp holes are separate retention axes. Registration proves XY agreement for the main paired supports; arm-root mapping still requires a canonical root fit. No screw length, thread engagement or fastener-head clearance follows merely from a Z interval.

## ASSUMPTIONS

- Assembly-family views faithfully describe this revision's plate order despite differences in cosmetic cutouts. The new screenshot is consistent with that order but does not expose every contact face.
- All arms share one thickness plane; there is no evidence for alternating crossed arm layers.
- No shims or deliberate root gaps are visible; planar carbon-to-carbon arm clamping is a provisional contact model.
- H, standoff outside diameter and threaded hardware details remain configurable engineering choices until measured/selected. The photo supplies no reliable calibration for them.
- Camera/end brackets are visible in the photo, but neither their detailed profile nor their complete mounting dimensions occurs in the two scans. Their physical existence is now established; exact reproduction cannot be derived from these views alone.

## VALIDATION EXECUTED

Visually compared distinctive fork/cutout shapes in both scans with the current screenshot and four secondary family views. Checked support-family interpretation against independent scan correspondences: Scan 1 camera tips/wing holes align to Scan 2 top-deck upper tips/middle and lower lobes; Scan 2 rear tip span ~389 px matches top-deck rear tip span ~389 px. Derived all Z intervals and the 7 mm support-length difference algebraically from current user stock values. No pixel-derived height or sibling CAD coordinate was used.

## KNOWN LIMITATIONS

The screenshot alone is insufficient to verify exact central contact order at every root. The proposed order has strong family-level corroboration and can serve as an explicit reconstruction decision, with mechanical review required before final acceptance. Absolute standoff height, camera/bracket envelopes, hardware grip/engagement and material strength are not established. Root-notch mating, bolt-head access and assembly interference must be validated on generated geometry, not inferred from visual resemblance.

## FOLLOW-UP TASKS

1. Preserve the current screenshot under project references with provenance; the `/tmp` path is transient (outside this agent's file ownership).
2. Architecture owner should encode `rear bottom → arms → camera clamp → standoffs → top` with shared faces and H-derived support families, using 2 mm plates and 5 mm arms.
3. Confirm or document a provisional H; expose it in parameters and dimensional drawings. Independent mechanical reviewer should check actual bracket/electronics clearance against the chosen value.
4. Continue canonical-arm/root assembly review and collision checking. Do not create independent front/rear root coordinates or shift parts by eye.
5. Treat exact brackets/accessory geometry as additional evidence-dependent work; identify primary frame completion separately from compatibility with unspecified devices.
