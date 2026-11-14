"""The aerodynamic figures the layout was chosen by. Plain geometry and momentum theory:
they compare layouts and size a battery, they do not replace a flight test.

  blockage()      share of a propeller's working area that has an arm or a finger of the base under it
  hull_clearance  gap between a blade tip and the widest point of the hull
  frontal_area()  what the body shows to the air from the side (it is the same from every side)
  hover_power()   ideal and expected electrical power to hover at a given all-up mass
"""

from math import pi, sqrt

from build123d import Axis, Vector
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo.outline import circle, face

from sfera import profiles, sizing

AIR = 1.225  # kg / m3
HUB_D = 40.0  # the middle of a propeller makes no thrust: what is under it does not count
FIGURE_OF_MERIT = 0.60  # a 7 inch propeller at hover
DRIVE_EFFICIENCY = 0.80  # motor and ESC


def disc_area() -> float:
    """Working area of one propeller, mm2."""
    return pi * (P.PROP_D**2 - HUB_D**2) / 4


def blockage() -> float:
    """Share of one propeller's working area with carbon under it."""
    motor = P.MOTORS["front_right"]
    annulus = face(circle(motor, P.PROP_D)) - face(circle(motor, HUB_D))
    arm = F.SHEETS["arm"]().outline.rotate(Axis.Z, P.ARM_ANGLE).translate(Vector(P.S[0], P.S[1], 0.0))
    under = (arm + profiles._base()) & annulus
    return sum(f.area for f in under.faces()) / disc_area()


def hull_clearance() -> float:
    from sfera.accessories import hull

    return sizing.MOTOR_R - P.PROP_D / 2 - hull.R_MAX


def frontal_area() -> dict[str, float]:
    """Side-on silhouette in cm2: the base with its bumper, the hull, the battery on top."""
    from sfera.accessories import bumper, hull

    base = 2 * bumper.NOSE_OUT * (P.Z_DECK + bumper.FLANGE_T)
    barrel = 2 * (hull.R_MAX * (hull.Z1 - hull.Z0) - hull.BULGE * hull.RISE)  # the three facets, both sides
    battery = E.BATTERY_SIZE[0] * (E.BATTERY_SIZE[2] + E.PAD_T)
    return {
        "base": base / 100,
        "hull": barrel / 100,
        "battery": battery / 100,
        "total": (base + barrel + battery) / 100,
    }


def hover_power(mass_kg: float) -> tuple[float, float]:
    """(ideal, expected electrical) watts to hover: momentum theory over the four discs."""
    thrust = mass_kg * 9.81
    area = 4 * pi * (P.PROP_D / 2000) ** 2
    ideal = thrust**1.5 / sqrt(2 * AIR * area)
    return ideal, ideal / FIGURE_OF_MERIT / DRIVE_EFFICIENCY


def drag(speed: float, cd: float = 0.8) -> float:
    """Newtons of body drag at `speed` m/s for a blunt barrel (Cd about 0.8)."""
    return 0.5 * AIR * speed**2 * frontal_area()["total"] / 1e4 * cd


def report() -> dict:
    return {
        "blockage_percent": round(100 * blockage(), 2),
        "hull_clearance_mm": round(hull_clearance(), 2),
        "rotor_free_radius_mm": round(sizing.MOTOR_R - P.PROP_D / 2, 1),
        "frontal_area_cm2": {k: round(v, 1) for k, v in frontal_area().items()},
        "drag_n_at_15_m_s": round(drag(15.0), 2),
        "hover_w": {f"{m:g} kg": [round(v) for v in hover_power(m)] for m in (1.5, 2.0, 2.5)},
    }


if __name__ == "__main__":
    import json

    print(json.dumps(report(), indent=1))
