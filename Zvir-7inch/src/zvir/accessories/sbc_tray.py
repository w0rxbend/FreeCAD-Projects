"""Tray for the companion computer: a TPU frame on the deck with four posts under the board.

Two versions of one part: for the credit-card boards (Raspberry Pi 3/4/5, Radxa ROCK 3C/4C+/5C,
58 x 49 mm holes) and for the Zero-size ones (58 x 23). The board is screwed into the posts;
the tray is screwed to the deck. TPU between the two keeps the frame's vibration out of the
SD card and the camera connector.
"""

from zhalo import checks as C
from zhalo import frame as F
from zhalo.accessories.kit import D_M3_FREE, Accessory, P, cylinder, poly, prism

from zvir import payload, profiles

FLOOR_T = 1.6
POST_D = 7.0
PILOT = 2.1  # an M2.5 screw cuts its own thread
RIM = 4.5  # the floor reaches this far past the hole pattern
BAR = 9.0  # width of the floor's four sides
Z0 = P.Z_DECK


def _tray(pattern):
    holes = payload.sbc_holes(pattern)
    ys = sorted({h[1] for h in holes})
    half = max(pattern[0] / 2 + POST_D / 2, abs(profiles.TRAY_SCREWS[0][0]) + D_M3_FREE / 2 + 2.3)
    y0, y1 = ys[0] - RIM, ys[-1] + RIM
    part = prism(poly([(-half, y0), (half, y0), (half, y1), (-half, y1)], 3.5), Z0, Z0 + FLOOR_T)
    inner = min(pattern[0] / 2 - POST_D / 2, abs(profiles.TRAY_SCREWS[0][0]) - D_M3_FREE / 2) - 2.3
    part -= prism(
        poly([(-inner, y0 + BAR), (inner, y0 + BAR), (inner, y1 - BAR), (-inner, y1 - BAR)], 3.0), Z0 - 1, Z0 + 5
    )
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
        (
            "the board fits the bay with its plugs to the tail",
            not hits,
            str(hits or "clear of every plate and standoff"),
        ),
        ("tray screw heads clear the board", head >= 1.0, f"{head:.1f} mm between an M3 button head and the board"),
        ("room above the board", room >= 8.0, f"{room:.1f} mm from the USB block to the top plate, for a fan or a HAT"),
    ]
    hardware = "2x M3x6 + nut (tray to the deck), 4x M2.5x6 self-tapping (board to the posts)"
    return [
        Accessory(
            "sbc_tray",
            "Companion-computer tray, 58 x 49 mm boards",
            _tray(payload.SBC_HOLES),
            holds=("sbc",),
            checks=own,
            hardware=hardware,
            notes="For Raspberry Pi 3/4/5 and Radxa ROCK 3C/4C+/5C. SD card to the front, USB and Ethernet aft.",
        ),
        Accessory(
            "sbc_tray_zero",
            "Companion-computer tray, 58 x 23 mm boards",
            _tray(payload.ZERO_HOLES),
            holds=("sbc",),
            in_assembly=False,
            checks=own[1:2],
            hardware=hardware,
            notes="For Raspberry Pi Zero 2 W and Radxa Zero 3. It uses the same two deck screws.",
        ),
    ]
