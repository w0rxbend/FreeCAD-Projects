"""2D profile tools: the scalloped "bee" outline and the cutouts.

A plate outline is a belt stretched round circles, walked counter-clockwise:

  lobe  - the belt passes round the outside of the circle (a rounded ear, usually with a bolt in it)
  bite  - the circle lies outside the plate and the belt follows its inner side (a waist or a notch)

Two neighbours are joined by their common tangent line, or, when the first one names a
`link` radius, by a concave arc of that radius tangent to both lobes (a scallop). The result
is made of true lines and arcs only, so the DXF a CNC shop receives has no faceted curves.
"""

from dataclasses import dataclass, replace
from math import atan2, cos, hypot, pi, sin, sqrt

from build123d import Edge, Face, Vector, Wire

XY = tuple[float, float]
TAU = 2 * pi


@dataclass(frozen=True)
class Node:
    x: float
    y: float
    r: float
    link: float = 0.0  # 0: straight tangent to the next node; > 0: concave arc of this radius
    concave: bool = False

    @property
    def c(self) -> XY:
        return (self.x, self.y)

    @property
    def sign(self) -> float:
        return -1.0 if self.concave else 1.0


def lobe(p: XY, r: float, link: float = 0.0) -> Node:
    return Node(p[0], p[1], r, link)


def bite(p: XY, r: float) -> Node:
    return Node(p[0], p[1], r, 0.0, True)


def scallop(a: Node, b: Node, sag: float) -> float:
    """Link radius for a concave arc between lobes a and b that dips `sag` mm below the straight
    belt (their common tangent line). sag = 0 would be the straight edge itself."""
    assert sag > 0
    d = hypot(b.x - a.x, b.y - a.y)
    line = _join(replace(a, link=0.0), b)
    n = _unit((line[0][0] - a.x, line[0][1] - a.y))  # outward normal of the straight belt

    def dip(radius: float) -> float:
        _p0, _p1, q = _join(replace(a, link=radius), b)
        return a.r + radius - ((q[0] - a.x) * n[0] + (q[1] - a.y) * n[1])

    lo, hi = max((d - a.r - b.r) / 2, 0.0) + 1e-6, 1e4
    assert dip(lo) >= sag, f"scallop of {sag} mm is deeper than the {dip(lo):.2f} mm this span allows"
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if dip(mid) > sag else (lo, mid)
    return (lo + hi) / 2


def _unit(v: XY) -> XY:
    n = hypot(*v)
    return v[0] / n, v[1] / n


def _join(a: Node, b: Node):
    """(p_out on a, p_in on b, arc centre | None) for the piece of belt from a to b."""
    d = hypot(b.x - a.x, b.y - a.y)
    u = ((b.x - a.x) / d, (b.y - a.y) / d)
    right = (u[1], -u[0])
    if a.link > 0:
        assert not a.concave and not b.concave, "arc links join two lobes"
        ra, rb = a.r + a.link, b.r + a.link
        assert ra + rb >= d - 1e-9, f"link radius {a.link} too small to span {d:.2f} between {a.c} and {b.c}"
        x = (ra * ra - rb * rb + d * d) / (2 * d)
        h = sqrt(max(ra * ra - x * x, 0.0))
        q = (a.x + x * u[0] + h * right[0], a.y + x * u[1] + h * right[1])
        ua, ub = _unit((q[0] - a.x, q[1] - a.y)), _unit((q[0] - b.x, q[1] - b.y))
        return (a.x + a.r * ua[0], a.y + a.r * ua[1]), (b.x + b.r * ub[0], b.y + b.r * ub[1]), q
    s = (a.sign * a.r - b.sign * b.r) / d
    assert abs(s) < 1, f"no common tangent between {a.c} and {b.c}"
    c = sqrt(1 - s * s)
    n = (right[0] * c + u[0] * s, right[1] * c + u[1] * s)
    return (
        (a.x + a.sign * a.r * n[0], a.y + a.sign * a.r * n[1]),
        (b.x + b.sign * b.r * n[0], b.y + b.sign * b.r * n[1]),
        None,
    )


def _arc(center: XY, r: float, a0: float, sweep: float) -> Edge:
    """Arc from angle a0 over a signed sweep (positive = counter-clockwise)."""
    pts = [(center[0] + r * cos(a0 + sweep * t), center[1] + r * sin(a0 + sweep * t)) for t in (0, 0.5, 1)]
    return Edge.make_three_point_arc(*(Vector(*p) for p in pts))


def belt(nodes: list[Node]) -> Wire:
    joins = [_join(n, nodes[(i + 1) % len(nodes)]) for i, n in enumerate(nodes)]
    edges: list[Edge] = []
    for i, node in enumerate(nodes):
        p_in, (p_out, p_next, q) = joins[i - 1][1], joins[i]
        if node.r > 1e-9:
            a_in, a_out = (atan2(p[1] - node.y, p[0] - node.x) for p in (p_in, p_out))
            sweep = ((a_out - a_in) * node.sign) % TAU
            if 1e-7 < sweep < TAU - 1e-7:
                assert sweep < 1.9 * pi, f"node {node.c} wraps {sweep:.2f} rad: nodes out of order?"
                edges.append(_arc(node.c, node.r, a_in, sweep * node.sign))
        if q is None:
            if hypot(p_next[0] - p_out[0], p_next[1] - p_out[1]) > 1e-7:
                edges.append(Edge.make_line(Vector(*p_out), Vector(*p_next)))
        else:
            a0, a1 = (atan2(p[1] - q[1], p[0] - q[0]) for p in (p_out, p_next))
            edges.append(_arc(q, node.link, a0, -((a0 - a1) % TAU)))
    return Wire(edges)


def mirrored(
    right: list[Node], top: Node | None = None, bottom: Node | None = None, bottom_link: float = 0.0
) -> list[Node]:
    """Whole outline from its right half, listed from the tail (-Y) to the nose (+Y).

    `top` / `bottom` are optional nodes on the centre line. The last right-hand node's link
    is used on both sides of `top` (or straight across the centre line); `bottom.link`
    (or `bottom_link`) does the same at the tail.
    """
    seq = ([bottom] if bottom else []) + list(right)
    if top:
        seq.append(replace(top, link=right[-1].link))
    for j in range(len(right) - 1, -1, -1):
        link = right[j - 1].link if j > 0 else (bottom.link if bottom else bottom_link)
        seq.append(replace(right[j], x=-right[j].x, link=link))
    return seq


# --- cutouts ---------------------------------------------------------------------------------
def circle(p: XY, d: float) -> Wire:
    """Round hole as two half arcs: a single full-circle edge has a seam some DXF readers dislike."""
    r = d / 2
    return Wire([_arc(p, r, 0.0, pi), _arc(p, r, pi, pi)])


def slot(p0: XY, p1: XY, w: float) -> Wire:
    """Stadium of width w round the segment p0-p1."""
    return belt([lobe(p0, w / 2), lobe(p1, w / 2)])


def rounded_poly(points: list[XY], r: float) -> Wire:
    """Polygon (counter-clockwise) with every corner rounded to radius r, concave corners included."""
    n = len(points)
    edges: list[Edge] = []
    cuts = []
    for i, p in enumerate(points):
        a, b = points[i - 1], points[(i + 1) % n]
        ua, ub = _unit((a[0] - p[0], a[1] - p[1])), _unit((b[0] - p[0], b[1] - p[1]))
        cos_t = ua[0] * ub[0] + ua[1] * ub[1]
        half = sqrt((1 - cos_t) / 2)  # sin of half the corner angle
        t = r * sqrt(max(1 - half * half, 0.0)) / half  # corner to tangent point
        bis = _unit((ua[0] + ub[0], ua[1] + ub[1]))
        c = (p[0] + bis[0] * r / half, p[1] + bis[1] * r / half)
        cuts.append(((p[0] + ua[0] * t, p[1] + ua[1] * t), (p[0] + ub[0] * t, p[1] + ub[1] * t), c))
    for i, (t_in, t_out, c) in enumerate(cuts):
        a0, a1 = (atan2(q[1] - c[1], q[0] - c[0]) for q in (t_in, t_out))
        sweep = (a1 - a0 + pi) % TAU - pi  # the short way round: convex corners +, concave -
        edges.append(_arc(c, r, a0, sweep))
        nxt = cuts[(i + 1) % n][0]
        if hypot(nxt[0] - t_out[0], nxt[1] - t_out[1]) > 1e-7:
            edges.append(Edge.make_line(Vector(*t_out), Vector(*nxt)))
    return Wire(edges)


def rounded_rect(center: XY, w: float, h: float, r: float) -> Wire:
    x, y = center
    return rounded_poly(
        [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], r
    )


def chevron(center: XY, half_span: float, sweep: float, stroke: float, r: float = 1.0, flip: bool = False) -> Wire:
    """A "V" window pointing +Y (or -Y when flipped): the bee's stripes."""
    x, y = center
    s = -1.0 if flip else 1.0
    pts = [
        (x - half_span, y - s * (sweep / 2 + stroke / 2)),
        (x, y + s * (sweep / 2 - stroke / 2)),
        (x + half_span, y - s * (sweep / 2 + stroke / 2)),
        (x + half_span, y - s * (sweep / 2 - stroke / 2)),
        (x, y + s * (sweep / 2 + stroke / 2)),
        (x - half_span, y - s * (sweep / 2 - stroke / 2)),
    ]
    return rounded_poly(pts, r)


def cross(center: XY, reach: float, width: float, r: float = 1.5) -> Wire:
    x, y = center
    a, w = reach, width / 2
    pts = [(w, -a), (w, -w), (a, -w), (a, w), (w, w), (w, a), (-w, a), (-w, w), (-a, w), (-a, -w), (-w, -w), (-w, -a)]
    return rounded_poly([(x + px, y + py) for px, py in pts], r)


def diamond(center: XY, w: float, h: float, r: float = 0.8) -> Wire:
    x, y = center
    return rounded_poly([(x + w / 2, y), (x, y + h / 2), (x - w / 2, y), (x, y - h / 2)], r)


def face(outer: Wire, inner: list[Wire] = ()) -> Face:
    f = Face(outer, list(inner))
    assert f.is_valid and f.area > 0
    return f
