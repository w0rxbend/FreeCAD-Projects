"""Printability measurements on a triangle mesh (numpy only).

overhangs()  how much surface faces the bed too steeply to print without support
thin_walls() how much surface has less than a given thickness of material behind it
"""

import numpy as np
from build123d import Part


def mesh(part: Part, tolerance: float = 0.06, angular: float = 0.25) -> tuple[np.ndarray, np.ndarray]:
    verts, tris = part.tessellate(tolerance, angular)
    return np.array([(v.X, v.Y, v.Z) for v in verts], dtype=float), np.array(tris, dtype=int)


def _normals_areas(v: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    length = np.linalg.norm(n, axis=1)
    ok = length > 1e-12
    n[ok] /= length[ok][:, None]
    return n, length / 2


def overhangs(part: Part, limit_deg: float = 50.0, bed_z: float = 0.25) -> tuple[float, float]:
    """(ceiling, slope) areas in mm2 for a part already lying on the bed.

    ceiling: faces pointing straight down above the bed (bridges or unsupported flats).
    slope:   faces leaning more than `limit_deg` from vertical, the part that needs support.
    """
    v, t = mesh(part)
    n, area = _normals_areas(v, t)
    z_min = v[t].min(axis=1)[:, 2]
    off_bed = z_min > bed_z
    ceiling = (n[:, 2] < -0.985) & off_bed
    slope = (n[:, 2] < -np.sin(np.radians(limit_deg))) & ~ceiling & off_bed
    return float(area[ceiling].sum()), float(area[slope].sum())


def thin_walls(part: Part, thickness: float, samples: int = 1500, seed: int = 7) -> tuple[float, float]:
    """(share of the surface with less than `thickness` behind it, thinnest wall seen).

    A ray is shot inwards from random surface points; the distance to the far side is the
    local wall thickness. Rays that start on a sliver next to an edge read short by nature,
    so the share is the meaningful number and the minimum is only a hint.
    """
    v, t = mesh(part, 0.1, 0.35)
    n, area = _normals_areas(v, t)
    keep = area > 1e-6
    t, n, area = t[keep], n[keep], area[keep]
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(t), size=min(samples, len(t) * 4), p=area / area.sum())
    w = rng.dirichlet((2.0, 2.0, 2.0), size=len(pick))
    origins = (v[t[pick, 0]] * w[:, :1] + v[t[pick, 1]] * w[:, 1:2] + v[t[pick, 2]] * w[:, 2:]) - n[pick] * 1e-4
    dirs = -n[pick]
    a, e1, e2 = v[t[:, 0]], v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]
    best = np.full(len(pick), np.inf)
    for i in range(0, len(pick), 64):  # Moller-Trumbore, a block of rays against every triangle
        o, d = origins[i : i + 64, None, :], dirs[i : i + 64, None, :]
        p = np.cross(d, e2[None])
        det = (e1[None] * p).sum(-1)
        good = np.abs(det) > 1e-12
        inv = np.where(good, 1.0 / np.where(good, det, 1.0), 0.0)
        s = o - a[None]
        u = (s * p).sum(-1) * inv
        q = np.cross(s, e1[None])
        w2 = (d * q).sum(-1) * inv
        dist = (e2[None] * q).sum(-1) * inv
        hit = good & (u >= -1e-9) & (w2 >= -1e-9) & (u + w2 <= 1 + 1e-9) & (dist > 0.02)
        best[i : i + 64] = np.where(hit, dist, np.inf).min(axis=1)
    seen = np.isfinite(best)
    if not seen.any():
        return 0.0, float("inf")
    return float((best[seen] < thickness).mean()), float(best[seen].min())
