"""Side panels: four TPU skins, a front and a rear one on each side, between the deck and the top plate.

Each snaps onto three standoffs from outside. The stack bay between them stays open: that
is where the motor wires come in and the flight controller's USB socket is reached.

The front panel covers the VTX bay and runs on past the nose standoff as a horn; the rear
panel covers the companion computer and runs on past the tail standoff as a fin beside its
plugs. The face is paint: slots that run down from the top edge like drips (they are also
the vents), and the frame's name sunk 0.7 mm into the rear panels.
"""

from dataclasses import replace
from math import hypot

from zhalo.accessories.kit import (
    CLIP_BORE,
    CLIP_WALL,
    SEAT,
    Accessory,
    P,
    belt,
    c_ring,
    disc,
    face,
    lobe,
    mirror_x,
    poly,
    polygon,
    prism,
    prism_x,
    scallop,
)
from zhalo.outline import slot

from zvir import profiles, sizing

SKIN = 2.0
Z0 = P.Z_DECK + SEAT
Z1 = P.Z_TOP - SEAT
R_OUT = CLIP_BORE / 2 + CLIP_WALL
FRONT = (profiles.B_F, profiles.MID_F, sizing.NOSE)  # counter-clockwise: up the right-hand side
REAR = (P.R, profiles.MID_R, profiles.B_R)
REAR_SAG = 3.4  # the rear panel bows in between the tail and the mid standoff: the rear prop passes there
BLADE = 22.0  # how far the horn and the fin run on past their standoff
BLADE_TIP = 3.5  # height left at their tip

DRIP_W = 3.2
DRIP_PITCH = 6.4
DRIP_TOP = Z1 - 3.0
DRIP_LEN = (9.0, 20.0, 12.0, 25.0, 7.0, 16.0, 23.0, 10.0, 18.0, 13.0)  # they repeat in this order
KEEP = 1.8  # least TPU left between a drip and a snap ring

TAG = "ZVIR"
TAG_DEPTH = 0.7
TAG_H = 15.0
TAG_Z = Z0 + 4.0
TAG_SLANT = 0.18
TAG_Y = -95.0  # middle of the tag, between the tail and the mid standoff
TAG_STROKE = 3.0
TAG_GAP = 2.6


def _glyph(ch: str) -> tuple[float, list, list]:
    """(advance width, outline, hole or []) of a letter in a box TAG_H tall, stroke TAG_STROKE."""
    h, t, w = TAG_H, TAG_STROKE, 11.0
    if ch == "Z":
        d = 4.2
        return w, [(0, h), (w, h), (w, h - t), (d, t), (w, t), (w, 0), (0, 0), (0, t), (w - d, h - t), (0, h - t)], []
    if ch == "V":
        return w, [(0, h), (t + 0.4, h), (w / 2, 3.6), (w - t - 0.4, h), (w, h), (w / 2 + 1.9, 0), (w / 2 - 1.9, 0)], []
    if ch == "I":
        return t, [(0, 0), (t, 0), (t, h), (0, h)], []
    if ch == "R":
        outer = [(0, 0), (t, 0), (t, 5.8), (4.4, 5.8), (7.4, 0), (w, 0), (7.6, 6.2), (w, 7.6), (w, h), (0, h)]
        return w, outer, [(t, 8.6), (w - t, 8.6), (w - t, h - t), (t, h - t)]
    raise ValueError(ch)


def _tag_faces(reads_forward: bool) -> list:
    """The letters as faces in (y, z). On the right-hand panel the tag reads towards the nose, on the left
    one towards the tail, so that it reads left to right from outside on both."""
    glyphs = [_glyph(ch) for ch in TAG]
    total = sum(g[0] for g in glyphs) + TAG_GAP * (len(glyphs) - 1)
    out, s0 = [], -total / 2
    for width, outer, hole in glyphs:

        def at(p, s0=s0):
            s = s0 + p[0] + TAG_SLANT * (p[1] - TAG_H / 2)
            return (TAG_Y + s if reads_forward else TAG_Y - s, TAG_Z + p[1])

        out.append(face(polygon([at(p) for p in outer]), [polygon([at(p) for p in hole])] if hole else []))
        s0 += width + TAG_GAP
    return out


def _loop(points, r: float, sag: float):
    nodes = [lobe(c, r) for c in points]
    if sag:
        link = scallop(lobe(points[0], R_OUT), lobe(points[1], R_OUT), sag) + (R_OUT - r)
        nodes[0] = replace(nodes[0], link=link)
    return face(belt(nodes))


def _inboard(points):
    """Everything inboard of the line through the first and the last standoff."""
    (x0, y0), (x1, y1) = points[0], points[-1]
    d = hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    a, b = (x0 - 60 * ux, y0 - 60 * uy), (x1 + 60 * ux, y1 + 60 * uy)
    return poly([a, b, (b[0] - 80 * uy, b[1] + 80 * ux), (a[0] - 80 * uy, a[1] + 80 * ux)])


def _band(points, depth: float, sag: float):
    """The outer `depth` of the skin, in plan."""
    return (_loop(points, R_OUT, sag) - _loop(points, R_OUT - depth, sag)) - _inboard(points)


def _blade(points, forward: bool):
    """Plan of the strip that runs on past the end standoff, in line with the skin that reaches it."""
    (cx, cy), (px, py) = (points[-1], points[-2]) if forward else (points[0], points[1])
    d = hypot(cx - px, cy - py)
    ux, uy = (cx - px) / d, (cy - py) / d
    nx, ny = (uy, -ux) if forward else (-uy, ux)  # outboard
    r0, r1 = R_OUT - SKIN, R_OUT
    quad = [
        (cx + nx * r0, cy + ny * r0),
        (cx + nx * r1, cy + ny * r1),
        (cx + nx * r1 + ux * BLADE, cy + ny * r1 + uy * BLADE),
        (cx + nx * r0 + ux * BLADE, cy + ny * r0 + uy * BLADE),
    ]
    return poly(quad if forward else quad[::-1])


def _drips(points, limit: float, skip: tuple[float, float] | None = None) -> list[tuple[float, float]]:
    """(station y, length) of every drip between the first and the last ring of a panel."""
    ys = sorted(c[1] for c in points)
    n = int((ys[-1] - ys[0]) / DRIP_PITCH)
    start = (ys[0] + ys[-1]) / 2 - n * DRIP_PITCH / 2
    out = []
    for k in range(n + 1):
        y = start + k * DRIP_PITCH
        if any(abs(y - c) < R_OUT + DRIP_W / 2 + KEEP for c in ys):
            continue
        length = DRIP_LEN[k % len(DRIP_LEN)]
        if skip and skip[0] - DRIP_W <= y <= skip[1] + DRIP_W:
            length = min(length, limit)
        out.append((y, length))
    return out


def _panel(points, sag: float, forward_blade: bool, drips):
    plan = _band(points, SKIN, sag) + _blade(points, forward_blade)
    for c in points:  # the skin is thicker than a ring's wall: clear the standoff, then add the ring
        plan -= disc(c, CLIP_BORE)
    for c in points:
        plan += c_ring(c, 180.0)
    wall = prism(plan, Z0, Z1)
    # the blade: its top edge stays level, its lower edge rises to the tip
    end = points[-1][1] if forward_blade else points[0][1]
    s = 1.0 if forward_blade else -1.0
    y0, y1 = end + s * (R_OUT + 0.5), end + s * (BLADE + 1.0)
    rise = (Z1 - BLADE_TIP - Z0) / (BLADE - R_OUT - 0.5)
    cut = [(y0, Z0 - 1.0), (y0, Z0), (y1, Z0 + rise * abs(y1 - y0)), (y1, Z0 - 1.0)]
    wall -= prism_x(poly(cut if forward_blade else cut[::-1]), 8.0, 70.0)
    r = DRIP_W / 2
    for y, length in drips:
        wall -= prism_x(face(slot((y, DRIP_TOP - length + r), (y, DRIP_TOP - r), DRIP_W)), 8.0, 70.0)
    return wall


def _tag(reads_forward: bool):
    """The cutter that sinks the tag into the right-hand rear panel (mirror it for the left one)."""
    band = prism(_band(REAR, TAG_DEPTH, REAR_SAG), Z0, Z1)
    out = None
    for f in _tag_faces(reads_forward):
        piece = prism_x(f, 8.0, 70.0) & band
        out = piece if out is None else out + piece
    return out


def build() -> list[Accessory]:
    tag_span = (TAG_Y - 26.0, TAG_Y + 26.0)
    front_drips = _drips(FRONT, 99.0)
    rear_drips = _drips(REAR, Z1 - 3.0 - (TAG_Z + TAG_H) - 2.5, tag_span)
    front = _panel(FRONT, 0.0, True, front_drips)
    rear = _panel(REAR, REAR_SAG, False, rear_drips)
    parts = {
        "panel_front_right": front,
        "panel_front_left": mirror_x(front),
        "panel_rear_right": rear - _tag(True),
        "panel_rear_left": mirror_x(rear - _tag(False)),
    }
    notes = (
        "Push it on from outside: all three rings open inboard. Print it upside down, top edge on the bed, so the "
        "drips and the blade need no support. The stack bay between the front and the rear panel stays open."
    )
    out = []
    for name, part in parts.items():
        end, side = name.split("_")[1:]
        drips = front_drips if end == "front" else rear_drips
        own = [
            (
                "drips",
                len(drips) >= 6,
                f"{len(drips)} slots, {DRIP_W:g} mm wide, {min(d[1] for d in drips):g} to "
                f"{max(d[1] for d in drips):g} mm long",
            )
        ]
        if end == "rear":
            own.append(
                (
                    f'"{TAG}" sunk into the skin',
                    SKIN - TAG_DEPTH >= 1.2,
                    f"{TAG_DEPTH} mm deep, {SKIN - TAG_DEPTH:.1f} mm left",
                )
            )
        out.append(
            Accessory(
                name,
                f"Side panel, {end} {side}",
                part,
                bed=(0, 0, 1),
                notes=notes,
                checks=own,
                ceilings=len(drips) * 1.2 + (32.0 if end == "rear" else 0.0),
                overhang=len(drips) * 3.6 + (10.0 if end == "rear" else 0.0),
            )
        )
    return out
