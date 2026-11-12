"""Skirts: the side panels of Strila.

Zhalo's panel with its own face: instead of a honeycomb, a row of upright slots ("gills")
whose length follows the lower edge, so they are long beside the stack and short over the
USB gate and along the two hooks. Same four snap rings, same lifted edge for the motor
wires, same gate.
"""

from zhalo import equipment as E
from zhalo.accessories import side_panel as base
from zhalo.accessories.kit import Accessory, face, mirror_x, poly, prism, prism_x
from zhalo.outline import slot

GILL_W = 3.0
GILL_PITCH = 6.0
GILL_H = (5.0, 13.0)  # shortest worth cutting, longest
GILL_TOP = base.Z1 - 2.2
KEEP = 1.8

B_F, B_R = base.B_F, base.B_R


def _gills() -> list[tuple[float, float]]:
    """(station y, lower end z) of every gill."""
    out = []
    y = base.SLOPE_REAR[1][0] + GILL_PITCH / 2
    while y <= base.SLOPE_FRONT[1][0]:
        edge = max(base._lower_edge(y + k * GILL_W / 2) for k in (-1.0, 0.0, 1.0))
        z0 = max(edge + KEEP, GILL_TOP - GILL_H[1])
        near_clip = any(abs(y - c) < base.R_OUT + GILL_W / 2 + KEEP for c in (B_F[1], B_R[1]))
        if GILL_TOP - z0 >= GILL_H[0] and not near_clip:
            out.append((y, z0))
        y += GILL_PITCH
    return out


def _right():
    wall = prism(base._plan(), base.Z0, base.Z1)
    far, big, low = 80.0, 60.0, base.Z0 - 1.0
    (y0, _z0), (y1, z1) = base.SLOPE_FRONT
    wall -= prism_x(poly([(y0, low), (y1, z1), (far, z1), (far, low)]), -big, big)
    (y0, _z0), (y1, z1) = base.SLOPE_REAR
    wall -= prism_x(poly([(y0, low), (-far, low), (-far, z1), (y1, z1)]), -big, big)
    inboard = B_F[0]
    gap, gate, top, gy = base.GAP_Y, base.GATE_W / 2, base.GATE_TOP, base.GATE_Y
    lifted = base.Z0 + base.GAP_H
    wall -= prism_x(poly([(-gap, low), (gap, low), (gap, lifted), (-gap, lifted)], 2.0), inboard, big)
    wall -= prism_x(poly([(gy - gate, low), (gy + gate, low), (gy + gate, top), (gy - gate, top)], 2.5), inboard, big)
    r = GILL_W / 2
    for y, z0 in _gills():
        wall -= prism_x(face(slot((y, z0 + r), (y, GILL_TOP - r), GILL_W)), 8.0, big)
    return wall


def build() -> list[Accessory]:
    right = _right()
    gills = _gills()
    fc_top = E.FC_Z + E.FC_SIZE[2]
    own = [
        ("USB gate reaches past the flight controller", base.GATE_TOP >= fc_top, f"gate to Z {base.GATE_TOP:.1f}"),
        ("gills", len(gills) >= 8, f"{len(gills)} slots, {GILL_W:g} mm wide"),
    ]
    notes = (
        "Push it on from outside: all four rings open inboard. Print it upside down, top edge on the bed, so the "
        "hooks, the lifted edge, the gate and the gills are all open to the top."
    )
    out = []
    for side, part in (("right", right), ("left", mirror_x(right))):
        out.append(
            Accessory(
                f"skirt_{side}",
                f"Skirt (side panel), {side}",
                part,
                bed=(0, 0, 1),
                notes=notes,
                checks=list(own),
                ceilings=len(gills) * 1.0,
                overhang=len(gills) * 3.0,
                color="accent",
            )
        )
    return out
