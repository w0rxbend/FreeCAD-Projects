"""Cargo deck and release: what the load is fastened to.

  cargo_plate  a PETG disc under the base, bolted up into the four stack standoffs. It carries a
               15 mm grid of captive M3 nuts (the middle four make a 30.5 mm square) and four
               slots for two straps at right angles. A load is bolted to it, strapped to it, or
               hung from the release.
  cargo_hook   a servo release for a slung load. The load's ring sits between two jaws on a 3 mm
               steel pin; a 9 g servo pulls the pin. The jaws carry the load, the servo only
               moves the pin, so a small servo is enough.

Everything hangs inside the 88 mm circle no propeller reaches, under the centre of thrust.
"""

from math import hypot, radians, sin

from build123d import Axis, Vector
from zhalo import checks as C
from zhalo.accessories.kit import (
    D_M3_FREE,
    D_M3_HEAD,
    M3_NUT_AF,
    Accessory,
    P,
    cylinder,
    disc,
    hex_pocket,
    poly,
    prism,
    prism_x,
    prism_y,
)
from zhalo.outline import circle, face, slot

from sfera import payload as L

PETG = "PETG"
PLATE_R = 48.0
PLATE_T = 4.0
GAP = 2.0  # the plate hangs this far under the base, clear of the stack bolts' heads
BOSS_D = 11.0
HEAD_RECESS = 2.2
PITCH = 15.0
NUT_DEPTH = 2.6
STRAP = (40.0, 24.0, 4.0)  # each strap slot: distance from the centre, length, width
Z_TOP = L.CARGO_Z + PLATE_T


def grid() -> list[tuple[float, float]]:
    """Where the captive nuts are."""
    out = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            if abs(i) == 2 and abs(j) == 2:  # the plate's own four bolts are there
                continue
            if hypot(i, j) * PITCH > PLATE_R - 4.0 or (abs(i) == 3 or abs(j) == 3):
                continue
            x, y = i * PITCH, j * PITCH
            if abs(i) == 1 and abs(j) == 1:  # the middle four: a 30.5 mm square, like a flight-controller stack
                x, y = i * P.STACK_PITCH / 2, j * P.STACK_PITCH / 2
            out.append((x, y))
    return out


def _plate():
    part = prism(face(circle((0.0, 0.0), 2 * PLATE_R)), L.CARGO_Z, Z_TOP)
    for xy in P.quad(P.B):
        part += cylinder(*xy, Z_TOP - 0.01, 0.0, BOSS_D)
    for xy in P.quad(P.B):
        part -= cylinder(*xy, L.CARGO_Z - 1, 1, D_M3_FREE)
        part -= cylinder(*xy, L.CARGO_Z - 1, L.CARGO_Z + HEAD_RECESS, D_M3_HEAD)
    for xy in grid():
        part -= cylinder(*xy, L.CARGO_Z - 1, Z_TOP + 1, D_M3_FREE)
        part -= hex_pocket(xy, Z_TOP - NUT_DEPTH, Z_TOP + 1, M3_NUT_AF)
    r, length, w = STRAP
    h = (length - w) / 2
    for s in (1, -1):
        part -= prism(face(slot((s * r, -h), (s * r, h), w)), L.CARGO_Z - 1, Z_TOP + 1)
        part -= prism(face(slot((-h, s * r), (h, s * r), w)), L.CARGO_Z - 1, Z_TOP + 1)
    return part


# --- release ---------------------------------------------------------------------------------------
FLANGE_T = 4.0
FLANGE = (-21.0, 36.0, -31.0, 8.0)  # x0, x1, y0, y1
MOUNTS = [(-15.0, 0.0), (30.0, 0.0)]  # two nuts of the plate's grid
SERVO_X = 22.0  # the shaft's station; the case runs back from there towards the jaws
SERVO_Z = L.CARGO_Z - FLANGE_T - L.SERVO_BODY[1] / 2 - 0.6
EAR_Y = -(L.HORN_S[0] + L.HORN_S[1]) / 2 + L.SERVO_EAR_S  # puts the horn in the plane of the pin
WALL_T = 3.0
PIN_Z = SERVO_Z - L.HORN_R  # the horn hangs straight down at rest, its link hole level with the pin
PIN_D = 3.0
JAW = (2.0, 5.0, 7.0)  # each jaw: inner face, outer face (distance from the middle), half-width along Y
SWING = 35.0  # degrees the servo turns either side of straight down
ENGAGED = 3.0  # how far the pin sits in the far jaw


def _servo():
    return L.servo_upright().rotate(Axis.X, -90.0).translate(Vector(SERVO_X, EAR_Y, SERVO_Z))


def _hook():
    x0, x1, y0, y1 = FLANGE
    top = L.CARGO_Z
    part = prism(poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 3.0), top - FLANGE_T, top)
    inner, outer, half = JAW
    jaw = poly([(-half, PIN_Z), (half, PIN_Z), (half, top - FLANGE_T + 0.01), (-half, top - FLANGE_T + 0.01)]) + disc(
        (0.0, PIN_Z), 2 * half
    )
    for s in (1, -1):
        part += prism_x(jaw, min(s * inner, s * outer), max(s * inner, s * outer))
    part -= prism_x(disc((0.0, PIN_Z), PIN_D + 0.3), -outer - 1, outer + 1)
    # the servo hangs between two legs of a wall; its ears screw onto them
    l, w, _h = L.SERVO_BODY
    sx1 = SERVO_X + L.SERVO_SHAFT_BACK + 0.2
    sx0 = sx1 - l - 0.4
    bottom = SERVO_Z - w / 2
    xc = SERVO_X + L.SERVO_SHAFT_BACK - l / 2
    span = L.SERVO_EARS[0] / 2 + 1.8
    wall = poly(
        [
            (xc - span, bottom),
            (xc + span, bottom),
            (xc + span, top - FLANGE_T + 0.01),
            (xc - span, top - FLANGE_T + 0.01),
        ]
    )
    wall -= poly([(sx0, bottom - 5), (sx1, bottom - 5), (sx1, top - FLANGE_T + 0.02), (sx0, top - FLANGE_T + 0.02)])
    part += prism_y(wall, EAR_Y - WALL_T, EAR_Y)
    for s in (1, -1):
        part -= prism_y(disc((xc + s * L.SERVO_HOLES / 2, SERVO_Z), 1.7), EAR_Y - WALL_T - 1, EAR_Y + 1)
    for xy in MOUNTS:
        part -= cylinder(*xy, top - FLANGE_T - 1, top + 1, D_M3_FREE)
        part -= cylinder(*xy, top - FLANGE_T - 1, top - FLANGE_T + 1.6, D_M3_HEAD)
    return part


def build() -> list[Accessory]:
    plate, hook, servo = _plate(), _hook(), _servo()
    nuts = grid()
    reach = max(hypot(*xy) for xy in nuts)
    under = PLATE_T - NUT_DEPTH
    plate_checks = [
        (
            "captive nuts",
            len(nuts) >= 20,
            f"{len(nuts)} M3 nuts on a {PITCH:g} mm grid, a 30.5 mm square in the middle",
        ),
        ("PETG under every nut", under >= 1.2, f"{under:.1f} mm"),
        (
            "the load hangs where no propeller blows",
            reach + 45.0 < L.SHADOW_R * 2**0.5,
            f"rotor-free circle R {L.SHADOW_R:.1f} mm, plate R {PLATE_R:g}",
        ),
        (
            "the plate's bolts are in the grid's gaps",
            all(hypot(x - bx, y - by) > 9.0 for x, y in nuts for bx, by in P.quad(P.B)),
            "clear",
        ),
    ]
    stroke = 2 * L.HORN_R * sin(radians(SWING))
    need = 2 * JAW[0] + ENGAGED + 1.0
    shared = C.overlap(hook, servo)
    pin = prism_x(disc((0.0, PIN_Z), PIN_D), -JAW[1] - 2, JAW[1] + 2)
    hook_checks = [
        ("servo case hangs between the wall's legs", shared < C.EPS, f"{shared:.3f} mm3 shared with the servo"),
        (
            "pin passes both jaws",
            C.overlap(hook, pin) < C.EPS,
            f"{PIN_D:g} mm pin, {2 * JAW[0]:g} mm slot for the load's ring",
        ),
        ("the servo's stroke pulls the pin clear", stroke >= need, f"stroke {stroke:.1f} mm, needed {need:.1f} mm"),
        ("mounts on two nuts of the cargo plate", all(xy in nuts for xy in MOUNTS), f"at {MOUNTS}"),
        (
            "hangs above the feet",
            PIN_Z - JAW[2] > L.FEET_Z + 15.0,
            f"jaws to Z {PIN_Z - JAW[2]:.1f}, feet Z {L.FEET_Z:g}",
        ),
    ]
    return [
        Accessory(
            "cargo_plate",
            "Cargo plate",
            plate,
            material=PETG,
            color="petg",
            holds=("cargo",),
            checks=plate_checks,
            ceilings=4 * 32.0,
            overhang=8.0,
            hardware=f"4x M3x20 (replace the inner arm bolts), {len(nuts)}x M3 nut",
            notes=(
                "PETG or ASA, 4 perimeters, 40 % infill. Press an M3 nut into every pocket before the plate goes on: "
                "they are then held between the plate and the base. Bolt a load on from below, or strap it "
                "through the four slots."
            ),
        ),
        Accessory(
            "cargo_hook",
            "Cargo release (servo hook)",
            hook,
            bed=(0, 0, 1),
            material=PETG,
            color="petg",
            holds=("cargo",),
            in_assembly=False,
            checks=hook_checks,
            ceilings=8.0,
            overhang=18.0,
            hardware="2x M3x8 into the plate's nuts, 9 g servo with its screws, 3 mm x 30 mm steel pin, 1 mm wire link",
            notes=(
                "PETG or ASA, flange on the bed. The servo drops in between the two legs, shaft outwards. Link the "
                "horn's outer hole to the pin with a Z-bend of 1 mm wire. Hang the load's ring between the jaws "
                "and push the pin through; the servo pulls it to let go."
            ),
        ),
    ]
