# A4 scans compared with the saved FreeCAD geometry

Both reference JPEGs are 2480 × 3508 pixels, consistent with an A4 page at about
300 pixels/inch. The embedded Scan_1 JPEG in `Tigerbee.FCStd` is byte-for-byte
identical to `refs/Scan_1.jpeg`.

The saved image plane is **210 × 297.04 mm**, rotated **−0.47°**, with its center
at **(109.276, 155.109) mm**. The 0.04 mm height difference from nominal A4 is
approximately 0.013%; it cannot explain a 303-versus-330 mm wheelbase difference.
The comparison reverses this saved placement before projecting CAD into scan pixels.

## Overlays

- [Scan_1 and saved-FreeCAD-derived CAD](scan-1-cad-overlay.svg)
- [Scan_2 and its build123d traces](scan-2-cad-overlay.svg)
- [Detailed numerical results](a4-comparison.json)

Red is the original pen trace; blue is the CAD projection. The SVGs embed the
unaltered JPEGs and can be enlarged to inspect individual features.

| Part | Median CAD outer-boundary distance to ink | 95th percentile |
| --- | ---: | ---: |
| Arm type 1 | 0.19 mm | 0.38 mm |
| Arm type 2 | 0.17 mm | 0.36 mm |
| Camera-side plate | 0.31 mm | 0.93 mm |
| Rear plate, traced from Scan_2 | 0.00 mm | 0.17 mm |
| Top plate, traced from Scan_2 | 0.00 mm | 0.12 mm |

These are sampled, one-directional distances to a band of ink, not manufacturing
accuracy or complete shape equivalence. Pen tails also enlarge raster bounding
boxes. The maximum outer-boundary distance is approximately 1.20 mm on the
camera-side plate. Scan_2 results describe the fidelity of an image-derived trace;
they are not an independent validation against a physical part.

## Feature differences

- The saved camera-side plate has an approximately **15 × 15 mm central rounded
  rectangular opening** absent from Scan_1. It remains preserved in the original
  reconstruction; this difference is not a scale error.
- The rear-plate trace includes a **3 mm corner hole inferred by symmetry**, absent
  from Scan_2. Its inferred origin is recorded in the profile metadata.
- Some motor mounting marks are pen dots or short strokes rather than complete
  hole outlines. Their drawn boundaries cannot independently establish the CAD
  hole diameter or slot shape.
- Several Scan_2 cutouts were regularized using convex hulls. In particular, the
  small central cutouts on the rear plate need detailed review against the curved
  pen traces; close agreement of the outer boundary does not validate those cutouts.

`Tigerbee.FCStd` has three saved bodies: the two arms and camera-side plate.
The other two components are reconstructed from Scan_2 and have no original saved
FreeCAD body to compare against.

## Wheelbase conclusion

The unextended assembly built from the original arm profiles measures **302.592 mm
and 303.986 mm** between opposite motor-hole centers. The user's subsequent physical
measurement was **approximately 303–304 mm**, consistent with that reconstruction.
The product-photo 330 mm label is superseded; no arm extension is justified by it.
Local mounting offsets and root collisions remain separate unresolved assembly issues.

Reproduce: `uv run --group tracing python tools/compare_a4.py`.
