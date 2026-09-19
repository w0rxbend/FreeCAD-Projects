"""Every round hole of the three plates, by name (section 3 of the spec).

Scanned holes are kept; `new=True` marks additions for FC/ESC/VTX mounting.
"""

from dataclasses import dataclass

from tigerbee import params as P

BOTTOM, MID, TOP = "plate_bottom", "plate_mid", "plate_top"


@dataclass(frozen=True)
class Hole:
    name: str
    purpose: str
    x: float
    y: float
    d: float
    plates: tuple[str, ...]
    through_arm: bool = False  # bolt also passes the arm layer (root hole / notch relief)
    new: bool = False


def pair(name, purpose, x, y, d, plates, **kw) -> list[Hole]:
    return [Hole(name, purpose, s * x, y, d, tuple(plates), **kw) for s in (-1, 1)]


def square(name, purpose, cx, cy, pitch, d, plates, **kw) -> list[Hole]:
    h = pitch / 2
    return [Hole(name, purpose, cx + sx * h, cy + sy * h, d, tuple(plates), **kw)
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _arm_axes() -> list[Hole]:
    outer, inner = P.root_holes()
    holes = []
    for end, arm in (("front", "arm_front_right"), ("rear", "arm_rear_right")):
        placement = P.ARM_PLACEMENTS[arm]
        for kind, local, plates in (("outer", outer, (BOTTOM, MID, TOP)), ("inner", inner, (BOTTOM, MID))):
            x, y = P.place(*local, placement)
            holes += pair(f"{end}_arm_{kind}", f"{end} arm clamp bolt" + (" + standoff" if kind == "outer" else ""),
                          x, y, P.D_M3, plates, through_arm=True)
    return holes


HOLES: list[Hole] = [
    *_arm_axes(),
    *square("stack_30p5", "FC/ESC 30.5x30.5 M3", 0, 0, P.PITCH_30, P.D_M3, (BOTTOM, MID), through_arm=True),
    *pair("front_tip_standoff", "25 mm standoff, camera fork", *P.FRONT_TIP, P.D_M3, (MID, TOP)),
    *pair("rear_tip_standoff", "32 mm standoff, tail", *P.REAR_TIP, P.D_M3, (BOTTOM, TOP)),
    # r = 18 diamond: 25.5 pattern rotated 45 deg / sandwich fasteners (plate-only feature)
    *[Hole("center_25p5_diamond", "25.5 diamond / sandwich bolt", x, y, P.D_M3, (BOTTOM,))
      for x, y in ((0, 18), (0, -18), (18, 0), (-18, 0))],
    *[Hole("center_25p5_diamond", "relief over the bottom-plate bolt", x, y, P.D_RELIEF_MID, (MID,))
      for x, y in ((0, 18), (0, -18), (18, 0), (-18, 0))],
    # bottom plate
    *pair("waist_accessory", "accessory", 28.0, 0, P.D_ACC_BOTTOM, (BOTTOM,)),
    *pair("rear_20", "VTX 20x20 M2 (rear row)", 10.0, P.REAR_BAY_Y - 10, P.D_M2, (BOTTOM,)),
    *pair("rear_20", "VTX 20x20 M2 (front row)", 10.0, P.REAR_BAY_Y + 10, P.D_M2, (BOTTOM,), new=True),
    *square("rear_25p5", "VTX 25.5x25.5 M2 (O4/Avatar)", 0, P.REAR_25_CENTER_Y, P.PITCH_25, P.D_M2, (BOTTOM,), new=True),
    *pair("rear_30p5_row", "accessory row (TPU antenna/LED mount)", 15.25, -81.0, P.D_M3, (BOTTOM,)),
    Hole("rear_tail_axis", "accessory", 0, -91.0, P.D_M3, (BOTTOM,)),
    # mid plate
    *square("fwd_30p5", "FC 30.5 alt / analog VTX / RX carrier", 0, P.FWD_BAY_Y, P.PITCH_30, P.D_M3, (MID,)),
    *square("fwd_20", "FC 20x20 M2 (also 20x20 VTX)", 0, P.FWD_BAY_Y, P.PITCH_20, P.D_M2, (MID,)),
    *square("fwd_25p5", "VTX 25.5x25.5 M2 alternate", 0, P.FWD_BAY_Y + P.FWD_25_OFFSET, P.PITCH_25, P.D_M2, (MID,), new=True),
    Hole("fwd_bore", "cable/connector relief", 0, P.FWD_BAY_Y, 17.5, (MID,)),
    # top plate
    Hole("top_accessory", "GPS/antenna/TPU", 0, 68.0, P.D_ACC_TOP, (TOP,)),
    *pair("top_accessory", "GPS/antenna/TPU", 27.3, 91.0, P.D_ACC_TOP, (TOP,)),
    *pair("top_accessory", "GPS/antenna/TPU", 31.3, 63.5, P.D_ACC_TOP, (TOP,)),
    *([Hole("sma", "SMA/RP-SMA bulkhead above the rear VTX bay", *P.SMA_XY, P.D_SMA, (TOP,), new=True)]
      if P.SMA_HOLE else []),
]

PATTERNS = {
    "stack_30p5": {"center": [0, 0], "pitch": P.PITCH_30, "screw": "M3"},
    "fwd_30p5": {"center": [0, P.FWD_BAY_Y], "pitch": P.PITCH_30, "screw": "M3"},
    "fwd_20": {"center": [0, P.FWD_BAY_Y], "pitch": P.PITCH_20, "screw": "M2"},
    "fwd_25p5": {"center": [0, P.FWD_BAY_Y + P.FWD_25_OFFSET], "pitch": P.PITCH_25, "screw": "M2"},
    "rear_20": {"center": [0, P.REAR_BAY_Y], "pitch": P.PITCH_20, "screw": "M2"},
    "rear_25p5": {"center": [0, P.REAR_25_CENTER_Y], "pitch": P.PITCH_25, "screw": "M2"},
}


def holes_for(plate: str) -> list[Hole]:
    return [h for h in HOLES if plate in h.plates]


def hole_rows() -> list[dict]:
    return [{"name": h.name, "purpose": h.purpose, "x": round(h.x, 4), "y": round(h.y, 4), "d": h.d,
             "plates": list(h.plates), "through_arm": h.through_arm, "new": h.new} for h in HOLES]
