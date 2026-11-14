"""Tray for a Zero-size companion computer: a TPU frame across the rear bay with four posts.

For the 65 x 30 mm boards with 58 x 23 mm holes: Raspberry Pi Zero and Zero 2 W, Radxa Zero,
Zero 3W and 3E. The board is screwed into the posts, the tray to the deck; the TPU between
the two keeps the frame's vibration out of the SD card.
"""

from zhalo import checks as C
from zhalo import frame as F
from zhalo.accessories.kit import D_M3_FREE, Accessory, P, cylinder, poly, prism

from sfera import payload, profiles

FLOOR_T = 1.6
POST_D = 7.0
PILOT = 2.1  # an M2.5 screw cuts its own thread
RIM = 4.5
Z0 = P.Z_DECK


def _rect(x0, y0, x1, y1, r):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)


def _tray():
    holes = payload.sbc_holes()
    xs, ys = sorted({abs(h[0]) for h in holes}), sorted({h[1] for h in holes})
    x1, y0, y1 = xs[-1] + RIM, ys[0] - RIM, ys[-1] + RIM
    part = prism(_rect(-x1, y0, x1, y1, 3.0), Z0, Z0 + FLOOR_T)
    sx = abs(profiles.TRAY_SCREWS[0][0])
    inner = sx - D_M3_FREE / 2 - 2.3
    part -= prism(_rect(-inner, y0 + 7.0, inner, y1 - 7.0, 2.5), Z0 - 1, Z0 + 5)
    a, b = sx + D_M3_FREE / 2 + 2.3, xs[-1] - POST_D / 2 - 2.0
    for s in (1, -1):
        part -= prism(_rect(min(s * a, s * b), y0 + 7.0, max(s * a, s * b), y1 - 7.0, 2.5), Z0 - 1, Z0 + 5)
    for xy in holes:
        part += cylinder(*xy, Z0 + FLOOR_T - 0.01, payload.SBC_Z, POST_D)
    for xy in holes:
        part -= cylinder(*xy, Z0 - 1, payload.SBC_Z + 1, PILOT)
    for xy in profiles.TRAY_SCREWS:
        part -= cylinder(*xy, Z0 - 1, Z0 + FLOOR_T + 1, D_M3_FREE)
    return part


def build() -> list[Accessory]:
    board = payload.sbc()
    hits = {n: round(v, 2) for n, p in F.parts().items() if (v := C.overlap(board, p)) > C.EPS}
    head = payload.SBC_Z - (Z0 + FLOOR_T) - 1.7
    room = P.Z_TOP - payload.SBC_TOP
    own = [
        ("the board fits across the rear bay", not hits, str(hits or "clear of every plate and standoff")),
        ("tray screw heads clear the board", head >= 1.0, f"{head:.1f} mm between an M3 button head and the board"),
        ("room above the board", room >= 15.0, f"{room:.1f} mm to the top plate: the battery lead passes over it"),
    ]
    return [
        Accessory(
            "sbc_tray",
            "Companion-computer tray (Zero size)",
            _tray(),
            holds=("sbc",),
            checks=own,
            hardware="2x M3x6 + nut (tray to the deck), 4x M2.5x6 self-tapping (board to the posts)",
            notes="For Raspberry Pi Zero / Zero 2 W and Radxa Zero / Zero 3W / 3E (58 x 23 mm holes), across the bay.",
        )
    ]
