"""Side panels: a TPU skin along each side of the body, between the deck and the top plate.

It keeps grass, sand and prop wash debris out of the stack, takes the scuffs a side slide
would put on the electronics, and gives the frame its face. The panel snaps onto the four
standoffs of one side from outside, so it goes on and comes off a finished quad.

Shape, front to rear: a hook under the top plate at the front standoff, a wall past the stack,
and a second hook at the rear standoff. The wall stands on the deck only at its two clips:
between them its lower edge is lifted so the motor wires and the cooling air pass under it,
and a gate in the middle gives a USB plug a straight run to the flight controller.
Only the top band of the front and rear standoffs is used; what is below belongs to the
camera mount and the tail mount.
"""

from dataclasses import replace

from zhalo import equipment as E
from zhalo.accessories.kit import (
    CLIP_BORE,
    CLIP_WALL,
    PANEL_BAND,
    SEAT,
    WALL,
    Accessory,
    P,
    belt,
    c_ring,
    face,
    hexagon,
    honeycomb,
    lobe,
    mirror_x,
    poly,
    prism,
    prism_x,
    scallop,
)

SKIN = WALL
Z0 = P.Z_DECK + SEAT
Z1 = P.Z_TOP - SEAT
Z_HOOK = P.Z_TOP - PANEL_BAND  # underside of the two hooks

B_F, B_R = P.B, (P.B[0], -P.B[1])
R_OUT = CLIP_BORE / 2 + CLIP_WALL
REAR_SAG = 3.5  # how far the rear span bows in, to stay clear of the rear prop

# side-view features, as (y, z)
SLOPE_FRONT = ((B_F[1] + 7.0, Z0), (P.F[1] - 9.5, Z_HOOK))
SLOPE_REAR = ((B_R[1] - 7.0, Z0), (P.R[1] + 9.5, Z_HOOK))
GAP_H = 5.0  # lift of the lower edge between the stack clips: three 18 AWG motor wires per side
GAP_Y = B_F[1] - R_OUT - 1.0  # the gap ends 1 mm short of each clip
GATE_W = 15.0  # USB-C plug with its boot
GATE_Y = 0.0  # station of the gate: move it if your flight controller has its USB socket off-centre
GATE_TOP = E.FC_Z + E.FC_SIZE[2] + 0.6  # just above the flight controller
HEX_AF, HEX_RIB = 5.0, 2.22  # column pitch 6.25: a full column lands between the gate and each clip
HEX_KEEP = 1.5  # least TPU left round every cell


def _lower_edge(y: float) -> float:
    """Height of the panel's lower edge at station y."""
    for (y0, z0), (y1, z1) in (SLOPE_FRONT, SLOPE_REAR):
        if min(y0, y1) <= y <= max(y0, y1):
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    if abs(y - GATE_Y) <= GATE_W / 2:
        return GATE_TOP
    if abs(y) <= GAP_Y:
        return Z0 + GAP_H
    return Z0 if SLOPE_REAR[0][0] < y < SLOPE_FRONT[0][0] else Z_HOOK


def _cells() -> list[tuple[float, float]]:
    """Honeycomb cell centres (y, z): the whole grid, minus every cell that would crowd an edge or a clip."""
    half_w = HEX_AF / 3**0.5
    top = Z1 - HEX_KEEP - HEX_AF / 2
    out = []
    for y, z in honeycomb(SLOPE_REAR[1][0], SLOPE_FRONT[1][0], Z0, Z1 - HEX_KEEP, HEX_AF, HEX_RIB, origin=(0.0, top)):
        edge = max(_lower_edge(y + k * (half_w + HEX_KEEP)) for k in (-1.0, -0.5, 0.0, 0.5, 1.0)) + HEX_KEEP
        near_clip = any(abs(y - c) < R_OUT + half_w + HEX_KEEP for c in (B_F[1], B_R[1]))
        if z - HEX_AF / 2 >= edge and not near_clip:
            out.append((y, z))
    return out


def _belt(r: float):
    """The four clip circles as a belt of radius r; the rear span bows inwards like the top plate above it."""
    n_r, b_r, b_f, f = (lobe(c, r) for c in (P.R, B_R, B_F, P.F))
    rear = scallop(lobe(P.R, R_OUT), lobe(B_R, R_OUT), REAR_SAG) + (R_OUT - r)
    return face(belt([replace(n_r, link=rear), b_r, b_f, f]))


def _plan():
    """Plan view of the right-hand panel: a skin tangent to the four snap rings, then the rings."""
    shell = _belt(R_OUT) - _belt(R_OUT - SKIN)
    # the belt also closes along the inboard side; keep only what is outboard of the front-rear line
    (x0, y0), (x1, y1) = P.R, P.F
    plan = shell - poly([(x0, y0 - 40), (x1, y1 + 40), (x1 - 60, y1 + 40), (x0 - 60, y0 - 40)])
    for c in (P.R, B_R, B_F, P.F):
        plan += c_ring(c, 180.0)
    return plan


def _right():
    wall = prism(_plan(), Z0, Z1)
    far, big, low = 80.0, 60.0, Z0 - 1.0
    (y0, z0), (y1, z1) = SLOPE_FRONT
    wall -= prism_x(poly([(y0, low), (y1, z1), (far, z1), (far, low)]), -big, big)
    (y0, z0), (y1, z1) = SLOPE_REAR
    wall -= prism_x(poly([(y0, low), (-far, low), (-far, z1), (y1, z1)]), -big, big)
    inboard = B_F[0]  # the cuts below start here, so they cannot reach the snap rings of the other side
    wall -= prism_x(poly([(-GAP_Y, low), (GAP_Y, low), (GAP_Y, Z0 + GAP_H), (-GAP_Y, Z0 + GAP_H)], 2.0), inboard, big)
    wall -= prism_x(
        poly(
            [
                (GATE_Y - GATE_W / 2, low),
                (GATE_Y + GATE_W / 2, low),
                (GATE_Y + GATE_W / 2, GATE_TOP),
                (GATE_Y - GATE_W / 2, GATE_TOP),
            ],
            2.5,
        ),
        inboard,
        big,
    )
    for y, z in _cells():
        wall -= prism_x(hexagon((y, z), HEX_AF), 8.0, big)
    return wall


def build() -> list[Accessory]:
    right = _right()
    cells = _cells()
    notes = (
        "Push it on from outside: all four rings open inboard. Print it upside down, top edge on the bed: "
        "the hooks, the lifted edge and the gate are then open to the top and need no support. Optional: a "
        "2.5 mm zip tie round a ring and its standoff if you fly through branches."
    )
    fc = (E.FC_Z, E.FC_Z + E.FC_SIZE[2])
    own = [
        (
            "USB gate reaches past the flight controller",
            GATE_TOP >= fc[1],
            f"gate to Z {GATE_TOP:.1f}, FC Z {fc[0]:.1f}-{fc[1]:.1f}",
        ),
        (
            "hooks stay above the camera and tail mount sleeves",
            Z_HOOK >= P.Z_TOP - PANEL_BAND - 1e-9,
            f"hook underside Z {Z_HOOK:.1f}",
        ),
        ("honeycomb cells", len(cells) >= 8, f"{len(cells)} cells of {HEX_AF} mm"),
    ]
    out = []
    for side, part in (("right", right), ("left", mirror_x(right))):
        out.append(
            Accessory(
                f"side_panel_{side}",
                f"Side panel, {side}",
                part,
                bed=(0, 0, 1),
                notes=notes,
                ceilings=len(cells) * (HEX_AF / 3**0.5) * SKIN * 1.3,
                overhang=len(cells) * 0.8,
                checks=list(own),
            )
        )
    return out
