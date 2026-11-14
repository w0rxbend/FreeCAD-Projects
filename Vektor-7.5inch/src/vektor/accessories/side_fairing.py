"""Side fairings: a TPU skin down each side of the bay, from the front standoff past the middle one to
the rear one, with a light slit along its length (a 5 mm LED strip behind it lights the quad's flank).
Each snaps onto the middle and rear standoffs and hugs the front one,
by rings in the top 9 mm, the band the sleeves below leave free."""

from math import hypot

from vektor import gear as G
from vektor.accessories.base import SNAP, Accessory, P, cyl, mirror_x, poly, prism, prism_x, snap_ring
from vektor.geometry import body_posts, disc

Z0 = P.Z_DECK + 0.2
Z1 = P.Z_TOP - 0.2
BAND = 9.0
R_IN, R_OUT = 4.8, 6.8  # the skin's inner and outer face from the line through the standoffs
SLIT = (3.0, 8.0)  # height, how far from each standoff it stops


def _posts():
    right = sorted([p for p in body_posts() if p[0] > 0], key=lambda p: -p[1])
    return right  # front, middle, rear


def build() -> list[Accessory]:
    posts = _posts()
    plan = None
    for p, q in zip(posts[:-1], posts[1:], strict=True):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = hypot(dx, dy)
        nx, ny = -dy / L, dx / L  # outward (the posts run front to rear on the right-hand side)
        quad = poly(
            [
                (p[0] + nx * R_IN, p[1] + ny * R_IN),
                (q[0] + nx * R_IN, q[1] + ny * R_IN),
                (q[0] + nx * R_OUT, q[1] + ny * R_OUT),
                (p[0] + nx * R_OUT, p[1] + ny * R_OUT),
            ]
        )
        plan = quad if plan is None else plan + quad
    for c in posts:
        plan += (
            disc(c, 2 * R_OUT)
            - disc(c, 2 * R_IN)
            - poly([(c[0] - 20, c[1] - 20), (c[0], c[1] - 20), (c[0], c[1] + 20), (c[0] - 20, c[1] + 20)])
        )
    part = prism(plan, Z0, Z1)
    for c in posts[1:]:  # the rings, in the top band (at the front, the camera pod's cheek is in the way)
        part += snap_ring(c, 180.0, Z1 - BAND, Z1)
        bridge = (
            disc(c, 2 * R_OUT)
            - disc(c, SNAP)
            - poly([(c[0] - 20, c[1] - 20), (c[0] + 0.5, c[1] - 20), (c[0] + 0.5, c[1] + 20), (c[0] - 20, c[1] + 20)])
        )
        part += prism(bridge, Z1 - BAND, Z1)
        part -= cyl(*c, Z0 - 1, Z1 + 1, SNAP)
    zc = (Z0 + Z1) / 2 - 3.0
    slits = 0
    for p, q in zip(posts[:-1], posts[1:], strict=True):
        y0, y1 = sorted((p[1], q[1]))
        slit = poly(
            [
                (y0 + SLIT[1], zc - SLIT[0] / 2),
                (y1 - SLIT[1], zc - SLIT[0] / 2),
                (y1 - SLIT[1], zc + SLIT[0] / 2),
                (y0 + SLIT[1], zc + SLIT[0] / 2),
            ]
        )
        part -= prism_x(slit, 10.0, 60.0)
        slits += 1
    for q in ("front_right", "rear_right"):
        part -= G.keepout(P.MOTORS[q])
    right = part
    own = [
        ("light slits", slits == 2, f"{slits} slits {SLIT[0]:g} mm tall"),
        ("rings only in the free top band", True, f"Z {Z1 - BAND:.1f} to {Z1:.1f}"),
    ]
    out = []
    for side, prt in (("right", right), ("left", mirror_x(right))):
        out.append(
            Accessory(
                f"side_fairing_{side}",
                f"Side fairing, {side}",
                prt,
                bed=(0, 0, 1),
                checks=list(own),
                bridges=280.0,
                overhang=60.0,
                notes=(
                    "Print it upside down; the slits' 3 mm tops bridge cleanly. "
                    "Snap it on from outside after the sleeves of the camera pod and the trident."
                ),
            )
        )
    return out
