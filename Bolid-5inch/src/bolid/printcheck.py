"""Can it be printed: measured on the triangle mesh of a part lying on the bed.

bridges()  area of faces looking straight down that are not on the bed (they need a bridge)
overhang() area of faces leaning more than 50 deg from upright (they need support)
thinnest() share of the surface with less than a given thickness of material behind it,
           found by shooting a ray inwards from sample points
"""

import numpy as np


def mesh(part, tol: float = 0.08):
    v, t = part.tessellate(tol, 0.3)
    return np.array([(p.X, p.Y, p.Z) for p in v]), np.array(t, dtype=int)


def _normals(v, t):
    n = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
    a = np.linalg.norm(n, axis=1)
    ok = a > 1e-12
    n[ok] /= a[ok][:, None]
    return n, a / 2


def down_faces(part, limit_deg: float = 50.0) -> tuple[float, float]:
    """(bridge area, overhang area) in mm2."""
    v, t = mesh(part)
    n, area = _normals(v, t)
    lifted = v[t][:, :, 2].min(axis=1) > 0.3
    flat = (n[:, 2] < -0.985) & lifted
    steep = (n[:, 2] < -np.sin(np.radians(limit_deg))) & ~flat & lifted
    return float(area[flat].sum()), float(area[steep].sum())


def thinnest(part, wall: float, samples: int = 1200, seed: int = 3) -> float:
    """Share of the surface with less than `wall` of material behind it."""
    v, t = mesh(part, 0.12)
    n, area = _normals(v, t)
    keep = area > 1e-6
    t, n, area = t[keep], n[keep], area[keep]
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(t), size=min(samples, 4 * len(t)), p=area / area.sum())
    w = rng.dirichlet((2, 2, 2), size=len(pick))
    o = (v[t[pick, 0]] * w[:, :1] + v[t[pick, 1]] * w[:, 1:2] + v[t[pick, 2]] * w[:, 2:]) - n[pick] * 1e-4
    d = -n[pick]
    a, e1, e2 = v[t[:, 0]], v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]
    best = np.full(len(pick), np.inf)
    for i in range(0, len(pick), 48):
        oo, dd = o[i : i + 48, None], d[i : i + 48, None]
        p = np.cross(dd, e2[None])
        det = (e1[None] * p).sum(-1)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        s = oo - a[None]
        uu = (s * p).sum(-1) * inv
        q = np.cross(s, e1[None])
        vv = (dd * q).sum(-1) * inv
        tt = (e2[None] * q).sum(-1) * inv
        hit = ok & (uu >= -1e-9) & (vv >= -1e-9) & (uu + vv <= 1 + 1e-9) & (tt > 0.02)
        best[i : i + 48] = np.where(hit, tt, np.inf).min(axis=1)
    seen = np.isfinite(best)
    return float((best[seen] < wall).mean()) if seen.any() else 0.0
