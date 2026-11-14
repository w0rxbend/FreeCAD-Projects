"""Side panels for the Tiger family, on the two stack standoffs of each side, to swap for the skirt.

  honeycomb   TPU skin with a honeycomb over the stack: the most air
  armor       TPU skin, no openings, with raised tiger stripes: for dust, sand and crashes
  composite   a TPU frame that holds a 1.5 mm carbon insert with tiger-stripe cut-outs:
              stiff and light, the carbon is cut from cnc/panel_insert_carbon_1.5mm.dxf
  led         the same frame with a clear 1.5 mm polycarbonate insert: stick a 5 mm LED strip
              behind it and the side of the quad glows

All of them are flat skins along the chord between the two arm standoffs of one side, snapped on
with the same two rings as the vented panel, and all leave the same lifted edge for the motor wires.
They are drawn in a local frame: x along the chord from the rear standoff, y inboard, z up.
"""

from math import atan2, cos, degrees, hypot, radians, sin

from build123d import Axis

from zhalo.accessories.kit import (
    CLIP_BORE,
    CLIP_WALL,
    SEAT,
    WALL,
    Accessory,
    P,
    box,
    c_ring,
    cylinder,
    hexagon,
    honeycomb,
    mirror_x,
    poly,
    prism,
    prism_y,
)

R_OUT = CLIP_BORE / 2 + CLIP_WALL
Z0 = P.Z_DECK + SEAT
Z1 = P.Z_TOP - SEAT
GAP_H = 5.0  # the lifted lower edge in the middle: the motor wires come in there

SKIN = WALL
INSERT_T = 1.5
GAP = 0.1  # between the insert and the TPU that holds it
LIP_T, LIP = 1.0, 1.4  # the lip behind the insert's edge: thickness, how far it reaches over the insert
RAIL_H = 1.6
END = 7.0  # the window starts this far from each standoff
OVERLAP = 2.0  # the insert reaches this far past the window on every side
STRIPE_PITCH, STRIPE_W, STRIPE_LEAN = 6.5, 2.8, 6.0
HEX, HEX_RIB = 4.0, 1.6


def chord():
    """(rear standoff, angle of the chord in degrees, its length)."""
    r = (P.B[0], -P.B[1])
    f = P.B
    return (r[0], r[1]), degrees(atan2(f[1] - r[1], f[0] - r[0])), hypot(f[0] - r[0], f[1] - r[1])


def _place(local):
    a, ang, _length = chord()
    return local.rotate(Axis.Z, ang).translate((a[0], a[1], 0))


def _window() -> tuple[float, float, float, float]:
    _a, _ang, length = chord()
    # the rail above the insert has to fit under the top plate
    return END, length - END, Z0 + GAP_H + 4.0, Z1 - OVERLAP - GAP - RAIL_H - 0.3


def _skin(length: float, y0: float = -R_OUT, y1: float = -(R_OUT - SKIN)):
    return box(0.0, y0, Z0, length, y1, Z1)


def _clips(local):
    """Place the local body, clear the two standoffs and add the snap rings."""
    a, _ang, length = chord()
    part = _place(local)
    ends = [(P.B[0], -P.B[1]), P.B]
    for c in ends:
        part -= cylinder(*c, Z0 - 1, Z1 + 1, CLIP_BORE)
    for c in ends:
        part += prism(c_ring(c, 180.0), Z0, Z1)
    return part


def _wire_gap(length: float):
    return box(6.0, -R_OUT - 2, Z0 - 1, length - 6.0, 1.0, Z0 + GAP_H)


def _stripes(u0, u1, z0, z1, keep: float = 2.0):
    """Tiger stripes as parallelograms leaning back, in the (x, z) plane."""
    out = []
    n = int((u1 - u0 - 2 * keep - STRIPE_LEAN) / STRIPE_PITCH)
    s0 = (u0 + u1) / 2 - (n - 1) * STRIPE_PITCH / 2 + STRIPE_LEAN / 2
    for k in range(n):
        s = s0 + k * STRIPE_PITCH
        w = STRIPE_W * (1.0 if k % 2 else 0.7)  # alternate thick and thin, like a tiger's coat
        out.append(
            poly(
                [
                    (s - w / 2, z0 + keep),
                    (s + w / 2, z0 + keep),
                    (s + w / 2 - STRIPE_LEAN, z1 - keep),
                    (s - w / 2 - STRIPE_LEAN, z1 - keep),
                ],
                0.8,
            )
        )
    return out


def honeycomb_panel():
    _a, _ang, length = chord()
    u0, u1, _z0, _z1 = _window()
    z0, z1 = Z0 + GAP_H + 1.5, Z1 - 1.8  # the honeycomb uses the whole height above the wire gap
    body = _skin(length) - _wire_gap(length)
    cells = honeycomb(u0, u1, z0, z1, HEX, HEX_RIB, origin=((u0 + u1) / 2, (z0 + z1) / 2))
    for c in cells:
        body -= prism_y(hexagon(c, HEX), -R_OUT - 1, 0.0)
    return _clips(body), len(cells)


def armor_panel():
    _a, _ang, length = chord()
    u0, u1, z0, z1 = _window()
    body = _skin(length) - _wire_gap(length)
    stripes = _stripes(u0, u1, z0 - 2, z1 + 1)
    for s in stripes:
        body += prism_y(s, -R_OUT - 0.8, -R_OUT + 0.01)
    return _clips(body), len(stripes)


def composite_frame():
    """The TPU frame: the skin with a window, a rail above and below the insert, a lip behind its edges."""
    _a, _ang, length = chord()
    u0, u1, z0, z1 = _window()
    i_y1 = -(R_OUT - SKIN) + GAP + INSERT_T
    body = _skin(length) - _wire_gap(length)
    body -= box(u0, -R_OUT - 1, z0, u1, 0.0, z1)
    lip_y = (i_y1 + GAP, i_y1 + GAP + LIP_T)
    for zi, sign in ((z1 + OVERLAP, 1), (z0 - OVERLAP, -1)):
        rail_z = (zi + GAP, zi + GAP + RAIL_H) if sign > 0 else (zi - GAP - RAIL_H, zi - GAP)
        body += box(u0 - OVERLAP, -(R_OUT - SKIN) - 0.01, rail_z[0], u1 + OVERLAP, lip_y[1], rail_z[1])
        lip_z = (zi - LIP, zi + GAP) if sign > 0 else (zi - GAP, zi + LIP)
        body += box(u0 - OVERLAP, lip_y[0], lip_z[0], u1 + OVERLAP, lip_y[1], lip_z[1])
    return _clips(body)


def insert(cut: bool):
    """The flat insert in its place: carbon with stripes cut out, or clear polycarbonate."""
    u0, u1, z0, z1 = _window()
    y0 = -(R_OUT - SKIN) + GAP
    outline = poly(
        [
            (u0 - OVERLAP + GAP, z0 - OVERLAP),
            (u1 + OVERLAP - GAP, z0 - OVERLAP),
            (u1 + OVERLAP - GAP, z1 + OVERLAP),
            (u0 - OVERLAP + GAP, z1 + OVERLAP),
        ],
        1.5,
    )
    stripes = _stripes(u0, u1, z0, z1) if cut else []
    for s in stripes:
        outline -= s
    return _place(prism_y(outline, y0, y0 + INSERT_T)), len(stripes)


def build() -> list[Accessory]:
    a, ang, length = chord()
    outward = (sin(radians(ang)), -cos(radians(ang)), 0.0)  # the insert lies on the bed on its outer face
    honey, cells = honeycomb_panel()
    armor, stripes = armor_panel()
    frame = composite_frame()
    carbon, cut = insert(True)
    clear, _ = insert(False)
    notes_frame = (
        "Press the insert into the frame from inside (the TPU stretches over its edges), then push the panel on "
        "from outside like the vented one. Print it lying on its outer face."
    )
    u0, u1, _z0, _z1 = _window()
    lip_area = 2 * (u1 - u0 + 2 * OVERLAP) * LIP
    out = []
    variants = [
        (
            "panel_honeycomb",
            "Side panel, honeycomb",
            honey,
            "tpu",
            [("cells", cells >= 12, f"{cells} hex cells of 5 mm")],
            "TPU 95A",
            (0, 0, 1),
        ),
        (
            "panel_armor",
            "Side panel, armor",
            armor,
            "accent",
            [("tiger stripes", stripes >= 3, f"{stripes} raised stripes")],
            "TPU 95A",
            (0, 0, 1),
        ),
        (
            "panel_frame",
            "Composite side panel, TPU frame",
            frame,
            "tpu",
            [("holds a 1.5 mm insert", True, f"{LIP} mm lips top and bottom")],
            "TPU 95A",
            outward,
        ),
        (
            "panel_insert_carbon",
            "Composite side panel, carbon insert (CNC)",
            carbon,
            "carbon",
            [("stripes cut out", cut >= 3, f"{cut} stripes")],
            "Carbon 1.5 mm",
            outward,
        ),
        (
            "panel_insert_clear",
            "LED side panel, clear insert (CNC or laser)",
            clear,
            "prop",
            [("light passes", True, "clear polycarbonate, 5 mm LED strip behind it")],
            "Polycarbonate 1.5 mm",
            outward,
        ),
    ]
    for name, title, part, color, checks, material, bed in variants:
        out.append(
            Accessory(
                name,
                title,
                part,
                bed=bed,
                qty=2,
                instances=(mirror_x(part),),
                in_assembly=False,
                checks=checks,
                color=color,
                material=material,
                # the frame's two lips reach 1.4 mm over the window: a short cantilever, not a bridge to support
                ceilings=lip_area + 60.0 if "frame" in name else 80.0,
                overhang=100.0 if "frame" in name else 60.0,
                notes=notes_frame
                if "frame" in name
                else (
                    "Cut from a flat sheet; one per side (the same part, turned over)."
                    if "insert" in name
                    else "Swap for the vented panel."
                ),
            )
        )
    return out
