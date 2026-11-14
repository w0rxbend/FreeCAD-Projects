"""The decisions taken on top of the traced geometry. Everything here is written down, so it can be
checked against the frame in hand and changed.

The traced shapes (data/reconstruction.json, from `trace.py`) give each part's outline and cut-outs
to about 0.3 mm. On top of that:

  - frame datum: the centre of the 30.5 mm stack square is the origin, +Y towards the camera;
  - every round hole is an exact circle. A pen cannot reach the edge of a small hole, so a hole
    traces smaller than it is: an M3 clearance hole (3.2 mm) traces as 2.6-2.8 mm. Every hole that
    traces under 3.4 mm is taken as M3; a bigger hole is its traced size plus PEN;
  - holes that sit on the same axis in two or three plates are one bolt: they get one position,
    the mean of what each plate shows;
  - pairs of holes within 0.7 mm of a standard board pattern (20, 25.5, 30.5 mm) are put on it;
  - the arm is placed so its two root holes land on the two holes the plates give for them;
  - thicknesses: plates 2 mm, arms 5 mm (V2's notes record the owner confirming this; the first
    Tigerbee attempt says 3 mm plates, so it is a parameter), 25 mm between the camera plate and the
    top plate (not measurable from the scans; the old projects assumed the same).
"""

import json
from dataclasses import dataclass, field, replace
from functools import lru_cache
from itertools import combinations
from math import atan2, cos, degrees, hypot, pi, radians, sin, sqrt
from pathlib import Path

import numpy as np

DATA = Path(__file__).with_name("data") / "reconstruction.json"
M3 = 3.2
PEN = 0.5  # how much smaller in diameter a round hole traces than it is
M3_TRACED_BELOW = 3.4
PATTERNS = (20.0, 25.5, 30.5)
SNAP = 0.7
SAME_AXIS = 1.6  # mm: holes of two plates closer than this are taken as one bolt
STACK = 30.5
ARM_GAP = 0.1  # each root stops this far short of the centre line: 0.2 mm between neighbours
STACK_RELIEF = 3.4  # the stack bolt runs in the fork of the arm root; the tracing's fork is 0.4 mm too tight for it

T_PLATE = 2.0
T_ARM = 5.0
TOP_GAP = 25.0
Z_BOTTOM = 0.0
Z_ARM = Z_BOTTOM + T_PLATE  # 2
Z_CAMERA = Z_ARM + T_ARM  # 7: the camera plate lies on the arms
Z_TOP = Z_CAMERA + T_PLATE + TOP_GAP  # 34
STANDOFF_OD = 5.0  # not traced: round M3 standoffs; the old projects used 5 or 6
RESAMPLE = 1.0  # mm between the points a spline is drawn through

XY = tuple[float, float]


@dataclass
class Hole:
    x: float
    y: float
    d: float
    traced: float  # the diameter the tracing shows (after the mirror averaging)
    group: str = ""  # which bolt it belongs to, once matched across plates
    spread: float = 0.0  # how far apart the plates put this bolt before it was given one position


@dataclass
class Part2D:
    name: str
    outline: np.ndarray  # closed, counter-clockwise, frame mm
    windows: list[np.ndarray] = field(default_factory=list)
    holes: list[Hole] = field(default_factory=list)
    thickness: float = T_PLATE
    shift: tuple[float, float] = (0.0, 0.0)  # added to the traced coordinates to put the part on the frame datum
    reliefs: list[tuple[float, float, float]] = field(default_factory=list)  # (x, y, d) bites taken out of the edge
    cuts: list[np.ndarray] = field(default_factory=list)  # polygons taken off the part


@lru_cache(maxsize=1)
def data() -> dict:
    return json.loads(DATA.read_text())


# --- contour helpers --------------------------------------------------------------------------------
def area(c: np.ndarray) -> float:
    x, y = c[:, 0], c[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def centroid(c: np.ndarray) -> np.ndarray:
    x, y = c[:, 0], c[:, 1]
    cross = x * np.roll(y, -1) - np.roll(x, -1) * y
    a = cross.sum() / 2
    return np.array([((x + np.roll(x, -1)) * cross).sum() / (6 * a), ((y + np.roll(y, -1)) * cross).sum() / (6 * a)])


def roundness(c: np.ndarray) -> tuple[float, np.ndarray, float]:
    """(how circular, centre, equivalent diameter): area over the circle through the farthest point."""
    m = centroid(c)
    a = abs(area(c))
    r = np.hypot(*(c - m).T).max()
    return a / (pi * r * r), m, 2 * sqrt(a / pi)


def resample(c: np.ndarray, step: float = RESAMPLE) -> np.ndarray:
    """Points evenly spaced along a closed contour (the first point is not repeated)."""
    c = np.vstack([c, c[:1]])
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    n = max(int(s[-1] / step), 12)
    t = np.linspace(0, s[-1], n, endpoint=False)
    return np.c_[np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])]


def ccw(c: np.ndarray) -> np.ndarray:
    return c if area(c) > 0 else c[::-1]


# --- plates -----------------------------------------------------------------------------------------------
def _split(contours) -> tuple[np.ndarray, list[np.ndarray], list[tuple[np.ndarray, float]]]:
    """(outline, windows, round holes as (centre, traced diameter)) of one traced part."""
    cs = [np.asarray(c) for c in contours]
    outline = max(cs, key=lambda c: abs(area(c)))
    windows, holes = [], []
    for c in cs:
        if c is outline:
            continue
        k, m, d = roundness(c)
        # a small mark is a hole even when it is not round: a pen dot, or two dots the mirror averaging joined
        if (k > 0.86 and d < 20.0) or (d < 5.0 and k > 0.45):
            holes.append((m, d))
        else:
            windows.append(c)
    return outline, windows, holes


def _rows(holes, half: float, tol: float = 1.0) -> list[float]:
    """Y of every symmetric pair of holes at |x| = half."""
    return sorted({round(float(m[1]), 3) for m, _d in holes if abs(abs(m[0]) - half) < tol and m[0] > 0})


def _stack_y(holes, pick) -> float:
    """Y of the centre of a 30.5 square of holes; `pick` chooses among several."""
    rows = _rows(holes, STACK / 2)
    found = [(a + b) / 2 for a, b in combinations(rows, 2) if abs(abs(a - b) - STACK) < 1.2]
    assert found, f"no 30.5 mm square among rows {rows}"
    return pick(found)


def _raw_plate(name: str, dy: float) -> Part2D:
    outline, windows, holes = _split(data()["plates"][name]["contours"])
    shift = np.array([0.0, dy])
    return Part2D(
        name,
        ccw(outline + shift),
        [ccw(w + shift) for w in windows],
        [Hole(float(m[0]), float(m[1] + dy), 0.0, float(d)) for m, d in holes],
        shift=(0.0, float(dy)),
    )


def _match_shift(moving, fixed, search=(-15.0, 15.0)) -> float:
    """The shift along Y that puts most holes of `moving` on holes of `fixed`."""
    best = (0, 0.0)
    for dy in np.arange(search[0], search[1], 0.05):
        hits = [min(hypot(m.x - f.x, m.y + dy - f.y) for f in fixed) for m in moving]
        n = sum(h < SAME_AXIS for h in hits)
        score = (n, -sum(h for h in hits if h < SAME_AXIS))
        if score > best[:2] if len(best) > 2 else n > best[0]:
            best = (n, -sum(h for h in hits if h < SAME_AXIS), float(dy))
    return best[-1]


def _snap_patterns(holes: list[Hole]) -> None:
    """Put pairs of holes that are within SNAP of a standard pattern exactly on it, and the rows of a
    square of such holes exactly the pattern apart."""
    for h in holes:
        for p in PATTERNS:
            if abs(abs(h.x) - p / 2) < SNAP:
                h.x = float(np.sign(h.x) * p / 2)
    for p in PATTERNS:
        on = [h for h in holes if abs(abs(h.x) - p / 2) < 1e-9]
        ys = sorted({round(h.y, 3) for h in on})
        for a, b in combinations(ys, 2):
            if abs(abs(b - a) - p) < SNAP:
                mid = (a + b) / 2
                for h in on:
                    if abs(h.y - a) < 1e-3:
                        h.y = mid - p / 2
                    elif abs(h.y - b) < 1e-3:
                        h.y = mid + p / 2


def _size(traced: float) -> float:
    return M3 if traced < M3_TRACED_BELOW else round(traced + PEN, 1)


@lru_cache(maxsize=1)
def plates() -> dict[str, Part2D]:
    """The three plates in frame coordinates, holes matched across them."""
    cam0 = _raw_plate("camera_plate", 0.0)
    bot0 = _raw_plate("bottom_plate", 0.0)
    top0 = _raw_plate("top_plate", 0.0)
    # the stack: the rear-most 30.5 square of the camera plate, the front-most of the bottom plate
    cam = _raw_plate("camera_plate", -_stack_y([(np.array([h.x, h.y]), h.traced) for h in cam0.holes], min))
    bot = _raw_plate("bottom_plate", -_stack_y([(np.array([h.x, h.y]), h.traced) for h in bot0.holes], max))
    top = _raw_plate("top_plate", _match_shift(top0.holes, cam.holes + bot.holes))
    out = {"bottom_plate": bot, "camera_plate": cam, "top_plate": top}
    # one bolt, one axis: cluster the holes of all three plates
    every = [(n, h) for n, p in out.items() for h in p.holes]
    groups: list[list[tuple[str, Hole]]] = []
    for n, h in every:
        for g in groups:
            if any(hypot(h.x - o.x, h.y - o.y) < SAME_AXIS and n != on for on, o in g) and n not in {x for x, _ in g}:
                g.append((n, h))
                break
        else:
            groups.append([(n, h)])
    for i, g in enumerate(groups):
        x = float(np.mean([h.x for _n, h in g]))
        y = float(np.mean([h.y for _n, h in g]))
        spread = max((hypot(a.x - b.x, a.y - b.y) for (_n, a), (_m, b) in combinations(g, 2)), default=0.0)
        if abs(x) < 0.8:
            x = 0.0
        has_m3 = any(_size(h.traced) == M3 for _n, h in g)
        for _n, h in g:
            # each plate keeps its own hole size (a plate may have a bigger hole than its neighbour);
            # a mark just over the M3 line on a bolt that is M3 elsewhere is two pen dots the mirror
            # averaging joined, not a bigger hole
            d = _size(h.traced)
            if d > M3 and has_m3 and h.traced < 4.4:
                d = M3
            h.x, h.y, h.d, h.group, h.spread = x, y, d, f"g{i}", spread
    # the plates are mirror images of themselves: make the matched pairs exact
    for p in out.values():
        for h in p.holes:
            twin = min((o for o in p.holes if o is not h), key=lambda o: hypot(o.x + h.x, o.y - h.y), default=None)
            if twin is not None and h.x > 0 and hypot(twin.x + h.x, twin.y - h.y) < SAME_AXIS:
                x, y = (h.x - twin.x) / 2, (h.y + twin.y) / 2
                h.x, h.y, twin.x, twin.y = x, y, -x, y
        _snap_patterns(p.holes)
    # the stack itself is the datum
    for p in out.values():
        for h in p.holes:
            if abs(abs(h.x) - STACK / 2) < 1e-6 and abs(abs(h.y) - STACK / 2) < SNAP + 0.5:
                h.y = float(np.sign(h.y) * STACK / 2)
    return out


def bolts() -> dict[str, list[tuple[str, Hole]]]:
    """group -> the plates it passes and the hole in each."""
    out: dict[str, list] = {}
    for n, p in plates().items():
        for h in p.holes:
            out.setdefault(h.group, []).append((n, h))
    return out


# --- arm ----------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def arm_local() -> Part2D:
    """The arm in its own frame: motor centre at the origin, +X towards the root. Motor holes made a
    square about the arm's axis; root holes as traced (they are replaced by the plates' in `arms()`)."""
    outline, windows, holes = _split(data()["arm"]["contours"])
    bore = min(holes, key=lambda t: hypot(*t[0]))
    motor = [t for t in holes if t is not bore and hypot(*t[0]) < 15.0]
    root = [t for t in holes if t[0][0] > 80.0]
    # windows the averaging left as tiny slivers are not cut-outs
    windows = [w for w in windows if abs(area(w)) > 4.0]
    h = float(np.mean([abs(c) for m, _d in motor for c in m]))
    out = Part2D("arm", ccw(outline - bore[0]), [ccw(w - bore[0]) for w in windows], [], T_ARM, shift=tuple(-bore[0]))
    out.holes.append(Hole(0.0, 0.0, _size(bore[1]) if bore[1] >= M3_TRACED_BELOW else 7.0, bore[1], "motor_bore"))
    for sx in (1, -1):
        for sy in (1, -1):
            out.holes.append(Hole(sx * h, sy * h, M3, float(np.mean([d for _m, d in motor])), "motor"))
    for m, d in sorted(root, key=lambda t: t[0][0]):
        out.holes.append(Hole(float(m[0] - bore[0][0]), float(m[1] - bore[0][1]), M3, d, "root"))
    return out


@dataclass(frozen=True)
class Placement:
    angle: float  # degrees, arm frame -> frame
    x: float
    y: float
    mirror: bool  # arm flipped over (its Y negated) before the rotation

    def apply(self, pts: np.ndarray) -> np.ndarray:
        p = np.asarray(pts, dtype=float).copy()
        if self.mirror:
            p[:, 1] = -p[:, 1]
        a = radians(self.angle)
        R = np.array([[cos(a), -sin(a)], [sin(a), cos(a)]])
        return p @ R.T + [self.x, self.y]


def _root_pairs() -> dict[str, tuple[Hole, Hole]]:
    """The two plate holes each right-hand arm root bolts through: the pairs of holes, outboard of the
    stack, about 13.8 mm apart, one pair ahead of the stack and one behind it."""
    cam = plates()["camera_plate"]
    cand = [h for h in cam.holes if h.x > 20.0 and abs(h.y) < 45.0 and h.d < 3.3]
    pairs = sorted(
        ((a, b) for a, b in combinations(cand, 2) if 12.5 < hypot(a.x - b.x, a.y - b.y) < 15.0),
        key=lambda ab: -(ab[0].y + ab[1].y),
    )
    assert len(pairs) >= 2, pairs
    return {"front_right": pairs[0], "rear_right": pairs[-1]}


@lru_cache(maxsize=1)
def arms() -> dict[str, tuple[Placement, Part2D]]:
    """Each of the four arms: how the one arm part is placed, and the part with its root holes on the plates'."""
    arm = arm_local()
    root = [h for h in arm.holes if h.group == "root"]
    A = np.array([[h.x, h.y] for h in root])
    out = {}
    for quad, (p, q) in _root_pairs().items():
        F = np.array([[p.x, p.y], [q.x, q.y]])
        best = None
        for mirror in (False, True):
            for order in (F, F[::-1]):
                a = A.copy()
                if mirror:
                    a[:, 1] = -a[:, 1]
                va, vf = a[1] - a[0], order[1] - order[0]
                ang = atan2(vf[1], vf[0]) - atan2(va[1], va[0])
                pl = Placement(degrees(ang), 0.0, 0.0, mirror)
                moved = pl.apply(A)
                off = order.mean(0) - moved.mean(0)
                pl = replace(pl, x=float(off[0]), y=float(off[1]))
                motor = pl.apply(np.zeros((1, 2)))[0]
                sy = 1 if quad.startswith("front") else -1
                if motor[0] <= 0 or motor[1] * sy <= 0:
                    continue
                score = _clash_score(pl, arm) - 1000.0 * _root_held(pl, arm)
                if best is None or score < best[0]:
                    best = (score, pl)
        assert best is not None, quad
        pl = best[1]
        local = replace(arm, holes=[h for h in arm.holes if h.group != "root"])
        inv = _inverse(pl)
        for fh in (p, q):
            lx, ly = inv(np.array([[fh.x, fh.y]]))[0]
            local.holes.append(Hole(float(lx), float(ly), M3, fh.traced, f"root:{fh.group}"))
        out[quad] = (pl, local)
    # Both placements put the stack bolt at the same point of the arm (they agree to 0.1 mm, which is
    # the best evidence that the placement is right). The arm gets one relief there.
    pts = [
        _inverse(pl)(np.array([[STACK / 2, STACK / 2 if q.startswith("front") else -STACK / 2]]))[0]
        for q, (pl, _p) in out.items()
    ]
    x, y = np.mean(pts, axis=0)
    # the root tips of the left and right arm meet on the centre line: trim both placements' share of it
    far = 500.0
    beyond = np.array([[-far, -far], [ARM_GAP, -far], [ARM_GAP, far], [-far, far]])
    cuts = [_inverse(pl)(beyond) for pl, _p in out.values()]
    for q, (pl, part) in out.items():
        out[q] = (pl, replace(part, reliefs=[(float(x), float(y), STACK_RELIEF)], cuts=cuts))
    return out


def _inverse(pl: Placement):
    def f(pts):
        p = np.asarray(pts, dtype=float) - [pl.x, pl.y]
        a = -radians(pl.angle)
        R = np.array([[cos(a), -sin(a)], [sin(a), cos(a)]])
        p = p @ R.T
        if pl.mirror:
            p[:, 1] = -p[:, 1]
        return p

    return f


def inside(poly: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Which points lie inside a closed polygon (even-odd rule)."""
    pts = np.atleast_2d(pts)
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x0, y0 = poly[:, 0][None], poly[:, 1][None]
    x1, y1 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    crosses = ((y0 > y) != (y1 > y)) & (x < (x1 - x0) * (y - y0) / (y1 - y0 + 1e-12) + x0)
    return crosses.sum(axis=1) % 2 == 1


def _root_held(pl: Placement, arm: Part2D) -> float:
    """Share of the arm's root (its last 40 mm) that lies between both lower plates: an arm is clamped there."""
    p = plates()
    root = pl.apply(arm.outline[arm.outline[:, 0] > arm.outline[:, 0].max() - 40.0])
    return float((inside(p["camera_plate"].outline, root) & inside(p["bottom_plate"].outline, root)).mean())


def _clash_score(pl: Placement, arm: Part2D) -> float:
    """How badly a candidate placement fits: arm material over the stack bolt, and over its mirror twin."""
    poly = pl.apply(arm.outline)
    stack = np.array([(STACK / 2, s * STACK / 2) for s in (1, -1)])
    bad = float(inside(poly, stack).sum()) * 1000.0
    twin = poly.copy()
    twin[:, 0] = -twin[:, 0]
    bad += float(inside(twin, poly).sum())
    return bad
