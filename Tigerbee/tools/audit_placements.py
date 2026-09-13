"""Reproduce the arm-placement audit without changing model geometry.

Run: uv run python tools/audit_placements.py
Results: build/placement-audit.json
"""

import json
from itertools import combinations, product
from math import dist
from pathlib import Path

from build123d import Plane

from tigerbee.assembly import (
    CLAMP_CENTER_Y,
    MountFit,
    fit_mounts,
    interference_report,
    locate,
    mounting_holes,
    ordered,
)
from tigerbee.inventory import source_digest
from tigerbee.models import build_part

platefit = MountFit(0, (0, -CLAMP_CENTER_Y), 0)
holes = ordered([platefit.apply(p) for p in mounting_holes("camera-plate") if abs(p[0]) > 25])
slots = [("FR", 1, True), ("FL", -1, True), ("RL", -1, False), ("RR", 1, False)]
candidates = []
for label, side, front in slots:
    slot = []
    for kind, flip in product(("arm-type-1", "arm-type-2"), (False, True)):
        source = [(-x if flip else x, y) for x, y in mounting_holes(kind)]
        target = [p for p in holes if p[0] * side > 0 and (p[1] > 0) == front]
        fits = [fit_mounts(source, target), fit_mounts(source, target[::-1])]
        fits = [f for f in fits if f.translation[0] * side > 0 and (f.translation[1] > 0) == front]
        if not fits:
            continue
        fit = fits[0]
        part = build_part(kind)
        if flip:
            part = part.mirror(Plane.YZ)
        slot.append((kind, flip, fit, locate(part, fit, 2.5, label)))
    candidates.append(slot)
pairvol = {}
for i, j in combinations(range(4), 2):
    for a, b in product(range(len(candidates[i])), range(len(candidates[j]))):
        collisions = interference_report([candidates[i][a][3], candidates[j][b][3]])
        pairvol[i, j, a, b] = sum(c["volume_mm3"] for c in collisions)
rows = []
for selection in product(*(range(len(c)) for c in candidates)):
    chosen = [candidates[i][a] for i, a in enumerate(selection)]
    if sum(c[0] == "arm-type-1" for c in chosen) != 2:
        continue
    volume = sum(pairvol[i, j, selection[i], selection[j]] for i, j in combinations(range(4), 2))
    wheelbases = [
        dist(chosen[i][2].translation, chosen[j][2].translation) for i, j in ((0, 2), (1, 3))
    ]
    rows.append(
        {
            "assignment": [(c[0], c[1]) for c in chosen],
            "interference_mm3": volume,
            "wheelbases_mm": wheelbases,
            "max_hole_error_mm": max(c[2].max_error for c in chosen),
        }
    )
rows.sort(key=lambda row: (row["interference_mm3"], row["max_hole_error_mm"]))
report = {
    "source_sha256": source_digest(),
    "target_wheelbase_mm": 330,
    "slot_order": [slot[0] for slot in slots],
    "assignment_fields": ["arm_type", "mirrored_about_YZ"],
    "scope": (
        "Two of each saved arm type, either face up, fixed existing outer clamp-hole pairs, "
        "motors facing outward in their assigned quadrant"
    ),
    "limitation": (
        "Does not establish scan scale or test different mounting-hole pairs, "
        "plate placements, or modified profiles"
    ),
    "scan_metadata": (
        "Both JPEGs are 2480 x 3508 pixels with 72 DPI tags; "
        "those tags do not establish physical scale"
    ),
    "candidates": rows,
}
output = Path("build/placement-audit.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2) + "\n")
print(f"Audited {len(rows)} arrangements -> {output}")
