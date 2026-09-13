# Authoritative references

Use the physical frame as dimension authority:

1. [Physical measurements](measurements.md): approximately **303–304 mm** between
   opposite motor-hole centers, confirmed by the user with the frame in hand.
2. `Scan_1.jpeg`: near-1:1 A4 pen tracings of the two arm types and camera-side plate.
3. `Scan_2.jpeg`: near-1:1 A4 pen tracings of the rear and top plates.

The user confirmed that the scans were drawn around the actual parts with a pen;
minor tracing errors are expected. Exact hole diameters, pitches, thicknesses,
and vertical spacing require separate measurements. Preserve their provenance.

`Tigerbee.FCStd`, manual 3MF exports, and `baseline/*.step` are prior reconstructions.
They provide regression baselines subordinate to physical measurements and scans.

## Product photos

`product/tiger-beetle-7inch-330mm.png` remains a useful visual reference for the
assembled frame. Its **330 mm label is superseded by the physical measurement**.
The same applies to image 06’s 295 mm label. Earlier 5 mm arm / 2.5 mm plate labels
remain assumptions; image 07 depicts other variants.

The unextended reconstruction measures 302.592 mm and 303.986 mm. It agrees with
the approximate physical reading, so no arm extension is applied. Remaining
mounting offsets and root collisions require local interface corrections.

## Historical placement audit

The [arm-placement audit](analysis/placement-audit.json) tested swaps and face flips
of the original arms at the current outer clamp-hole pairs. Its six outward-facing
arrangements measured 302.54–304.04 mm. The audit was made while 330 mm was assumed
from the product photo; that target is now superseded. The collision findings
remain relevant: all arrangements had arm-root interference.

Reproduce with `uv run python tools/audit_placements.py`; inspect
`build/placement-audit.json`. The committed historical report retains its original
source hash and assumptions rather than being rewritten as current evidence.

## A4 comparison

The [registered scan/CAD comparison](analysis/a4-comparison.md) confirms that the
saved Scan_1 image plane is effectively A4. It also identifies local feature
differences, including a central plate opening absent from the original pen trace.
