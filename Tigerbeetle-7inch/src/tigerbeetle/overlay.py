"""The CAD drawn back onto the owner's tracings: the evidence that the model is their frame.

Black: the parts as modelled (outline, cut-outs, holes), mapped back onto each sheet with the
same transform the tracing was read with. Red: the original ink. Where the two lines run
together the model follows the tracing; the report gives the numbers.
"""

from pathlib import Path

import numpy as np

from tigerbeetle import model as M
from tigerbeetle import trace as T


def _page(points: np.ndarray, to_page, shift) -> np.ndarray:
    p = np.asarray(points) - np.asarray(shift)
    q = np.asarray(to_page) @ np.vstack([p.T, np.ones(len(p))])
    return q[:2].T


def _loops(part: M.Part2D) -> list[np.ndarray]:
    out = [part.outline, *part.windows]
    t = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    for h in part.holes:
        out.append(np.c_[h.x + h.d / 2 * np.cos(t), h.y + h.d / 2 * np.sin(t)])
    return out


def deviation(loops: list[np.ndarray], to_page, shift, ink: np.ndarray) -> np.ndarray:
    """Distance (mm) from points along the model's outline to the nearest red ink."""
    from scipy import ndimage as ndi

    dist = ndi.distance_transform_edt(~ink) * T.PX
    pts = _page(M.resample(loops[0], 0.5), to_page, shift)
    u, v = np.clip(pts[:, 0].astype(int), 0, ink.shape[1] - 1), np.clip(pts[:, 1].astype(int), 0, ink.shape[0] - 1)
    return dist[v, u]


def draw(out: Path) -> dict:
    from PIL import Image, ImageDraw

    data = M.data()
    jobs = {1: [], 2: []}
    plates = M.plates()
    jobs[1].append(
        (
            "camera_plate",
            _loops(plates["camera_plate"]),
            data["plates"]["camera_plate"]["to_page"],
            plates["camera_plate"].shift,
        )
    )
    jobs[2].append(
        (
            "bottom_plate",
            _loops(plates["bottom_plate"]),
            data["plates"]["bottom_plate"]["to_page"],
            plates["bottom_plate"].shift,
        )
    )
    jobs[2].append(
        ("top_plate", _loops(plates["top_plate"]), data["plates"]["top_plate"]["to_page"], plates["top_plate"].shift)
    )
    arm = M.arms()["front_right"][1]
    loops = _loops(arm)
    for tracing in ("arm_a", "arm_b"):
        jobs[1].append((tracing, loops, data["arm"]["to_page"][tracing], arm.shift))
    report = {}
    out.mkdir(parents=True, exist_ok=True)
    for scan, items in jobs.items():
        im = Image.open(T.ROOT / "references" / f"Scan_{scan}.jpeg").convert("RGB")
        ink = T._ink(scan)
        d = ImageDraw.Draw(im)
        for name, ls, to_page, shift in items:
            for loop in ls:
                pts = _page(np.vstack([loop, loop[:1]]), to_page, shift)
                d.line([tuple(p) for p in pts], fill=(0, 0, 0), width=3)
            dev = deviation(ls, to_page, shift, ink)
            report[name] = {
                "mean_mm": round(float(dev.mean()), 3),
                "p95_mm": round(float(np.percentile(dev, 95)), 3),
                "max_mm": round(float(dev.max()), 3),
            }
        im.thumbnail((1240, 1754))
        im.save(out / f"overlay_scan_{scan}.png")
    return report


if __name__ == "__main__":
    import json

    print(json.dumps(draw(T.ROOT / "exports" / "renders"), indent=1))
