"""Extract provisional Scan_2 profiles; run with `uv run --group tracing`.

Coordinates use the A4 scan width as an inferred scale. Circular marks become
nominal holes, and the missing upper-right clamp hole is mirrored explicitly.
Review the generated profiles against the scan before accepting measurements.
"""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def trace() -> None:
    source = ROOT / "refs/Scan_2.jpeg"
    image = cv2.imread(str(source))
    blue, green, red = cv2.split(image.astype(np.int16))
    mask = ((red - green > 25) & (red - blue > 15) & (red < 245)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    scale = 210 / image.shape[1]
    outlines = sorted(
        (i for i, c in enumerate(contours) if cv2.contourArea(c) > 500_000),
        key=lambda i: cv2.boundingRect(contours[i])[0],
    )
    # Each outline has both sides of the pen stroke. Use the interior side.
    interiors = [i for i in outlines if hierarchy[0][i][3] != -1]
    for name, outline, origin in zip(
        ("rear-plate", "top-plate"), interiors, ((685, 2100), (1845, 1900)), strict=True
    ):

        def xy(point: np.ndarray, origin: tuple[int, int] = origin) -> list[float]:
            return [
                round((point[0] - origin[0]) * scale, 6),
                round((origin[1] - point[1]) * scale, 6),
            ]

        def spline(contour: np.ndarray) -> dict:
            simplified = cv2.approxPolyDP(contour, 3, True).reshape(-1, 2)
            points = []
            # Extra points along straight sections prevent interpolation overshoot.
            for a, b in zip(simplified, np.roll(simplified, -1, axis=0), strict=True):
                count = max(1, int(np.ceil(np.linalg.norm(b - a) / 20)))
                points.extend(xy(a + (b - a) * step / count) for step in range(count))
            return {"kind": "spline", "points": points}

        loops = [{"outer": True, "segments": [spline(contours[outline])]}]
        for i, contour in enumerate(contours):
            if hierarchy[0][i][3] != outline:
                continue
            x, y, width, height = cv2.boundingRect(contour)
            if width < 12 or height < 12 or cv2.contourArea(contour) < 100:
                continue
            if max(width, height) < 65:
                segment = {
                    "kind": "circle",
                    "center": xy(np.array([x + (width - 1) / 2, y + (height - 1) / 2])),
                    "radius": 2.5 if max(width, height) >= 45 else 1.5,
                }
            else:
                # Open pen strokes and scribbles inside a cutout are measurement
                # noise. All these cutouts have a convex intended boundary.
                segment = spline(cv2.convexHull(contour))
            loops.append({"outer": False, "segments": [segment]})
        if name == "rear-plate":
            loops.append(
                {
                    "outer": False,
                    "segments": [
                        {
                            "kind": "circle",
                            "center": xy(np.array([2 * origin[0] - 350, 1719])),
                            "radius": 1.5,
                        }
                    ],
                }
            )
        data = {
            "part": name,
            "source": "refs/Scan_2.jpeg",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "status": "provisional-scan",
            "thickness": 2.5,
            "scan_mm_per_pixel": scale,
            "scan_origin_px": origin,
            "assumptions": [
                "A4 width 210 mm; scale unverified",
                "3/5 mm nominal holes",
                "2.5 mm thickness inferred from earlier variant; unconfirmed for 330 mm frame",
                "Convex hull repairs cutout pen gaps",
                "Rear plate missing corner hole mirrored from opposite side",
            ],
            "loops": loops,
        }
        path = ROOT / "src/tigerbee/profiles" / f"{name}.json"
        path.write_text(json.dumps(data, indent=2) + "\n")
        print(name, "openings", len(loops) - 1)


if __name__ == "__main__":
    trace()
