"""Side pods: the fairing under each wing of the top plate.

Seen from above each pod is a V that follows the wing out to its tip, so the body is widest
amidships and tapers to the nose and the tail. A row of shark teeth runs along its top
edge. It snaps onto the same four standoffs as Zhalo's side panel and keeps the same lifted
lower edge for the motor wires and the same USB gate.
"""

from dataclasses import replace

from zhalo import equipment as E
from zhalo.accessories import side_panel as base
from zhalo.accessories.kit import Accessory, P, belt, c_ring, face, lobe, mirror_x, poly, prism, prism_x, scallop

from shershen import profiles

SKIN = base.SKIN
APEX_R = 3.0
APEX = (profiles.WING_TIP[0] + profiles.WING_R - 0.6 - APEX_R, profiles.WING_TIP[1])  # 0.6 mm inside the wing edge
TOOTH_H = (4.5, 9.5)  # shortest tooth worth cutting, longest fang
TOOTH_PITCH = 7.0
TOOTH_TOP = base.Z1 - 2.2
KEEP = 1.5


def tooth_width(h: float) -> float:
    """Longer teeth are a little wider, but always steeper than 20 deg from vertical."""
    return 3.4 + 0.2 * h


B_F, B_R = base.B_F, base.B_R


def _teeth() -> list[tuple[float, float]]:
    """(station y, height) of every tooth: as long a fang as the wall under it allows, none over a clip."""
    out = []
    y = base.SLOPE_REAR[1][0]
    while y <= base.SLOPE_FRONT[1][0]:
        reach = tooth_width(TOOTH_H[1]) / 2
        edge = max(base._lower_edge(y + k * reach) for k in (-1.0, 0.0, 1.0))
        h = min(TOOTH_H[1], TOOTH_TOP - edge - KEEP)
        near_clip = any(abs(y - c) < base.R_OUT + reach + KEEP for c in (B_F[1], B_R[1]))
        if h >= TOOTH_H[0] and not near_clip:
            out.append((y, h))
        y += TOOTH_PITCH
    return out


def _belt(r: float, r_apex: float):
    n_r, b_r, apex, b_f, f = lobe(P.R, r), lobe(B_R, r), lobe(APEX, r_apex), lobe(B_F, r), lobe(P.F, r)
    rear = scallop(lobe(P.R, base.R_OUT), lobe(B_R, base.R_OUT), base.REAR_SAG) + (base.R_OUT - r)
    return face(belt([replace(n_r, link=rear), b_r, apex, b_f, f]))


def _plan():
    shell = _belt(base.R_OUT, APEX_R) - _belt(base.R_OUT - SKIN, APEX_R - SKIN)
    (x0, y0), (x1, y1) = P.R, P.F
    plan = shell - poly([(x0, y0 - 40), (x1, y1 + 40), (x1 - 60, y1 + 40), (x0 - 60, y0 - 40)])
    for c in (P.R, B_R, B_F, P.F):
        plan += c_ring(c, 180.0)
    return plan


def _right():
    wall = prism(_plan(), base.Z0, base.Z1)
    far, big, low = 80.0, 60.0, base.Z0 - 1.0
    (y0, _z0), (y1, z1) = base.SLOPE_FRONT
    wall -= prism_x(poly([(y0, low), (y1, z1), (far, z1), (far, low)]), -big, big)
    (y0, _z0), (y1, z1) = base.SLOPE_REAR
    wall -= prism_x(poly([(y0, low), (-far, low), (-far, z1), (y1, z1)]), -big, big)
    inboard = B_F[0]
    gap, gate, top = base.GAP_Y, base.GATE_W / 2, base.GATE_TOP
    wall -= prism_x(
        poly([(-gap, low), (gap, low), (gap, base.Z0 + base.GAP_H), (-gap, base.Z0 + base.GAP_H)], 2.0), inboard, big
    )
    gy = base.GATE_Y
    wall -= prism_x(poly([(gy - gate, low), (gy + gate, low), (gy + gate, top), (gy - gate, top)], 2.5), inboard, big)
    for y, h in _teeth():
        w = tooth_width(h)
        wall -= prism_x(poly([(y - w / 2, TOOTH_TOP), (y, TOOTH_TOP - h), (y + w / 2, TOOTH_TOP)], 0.5), 8.0, big)
    return wall


def build() -> list[Accessory]:
    right = _right()
    teeth = _teeth()
    fc = (E.FC_Z, E.FC_Z + E.FC_SIZE[2])
    own = [
        ("USB gate reaches past the flight controller", base.GATE_TOP >= fc[1], f"gate to Z {base.GATE_TOP:.1f}"),
        (
            "the pod stays under the wing",
            APEX[0] + APEX_R <= profiles.WING_TIP[0] + profiles.WING_R,
            f"pod to X {APEX[0] + APEX_R:.1f}, wing to X {profiles.WING_TIP[0] + profiles.WING_R:.1f}",
        ),
        ("shark teeth", len(teeth) >= 6, f"{len(teeth)} teeth"),
    ]
    notes = (
        "Push it on from outside: all four rings open inboard. Print it upside down, top edge on the bed, so the "
        "hooks, the lifted edge, the gate and the teeth are all open to the top."
    )
    out = []
    for side, part in (("right", right), ("left", mirror_x(right))):
        out.append(
            Accessory(
                f"side_pod_{side}",
                f"Side pod, {side}",
                part,
                bed=(0, 0, 1),
                notes=notes,
                checks=list(own),
                overhang=len(teeth) * 1.5,
                color="accent",
            )
        )
    return out
