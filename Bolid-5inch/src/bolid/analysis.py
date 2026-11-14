"""Why Bolid is shaped the way it is: two small studies, numbers only.

wheelbase_study()  how fast the quad can start a flip or a yaw as the motors move out, against how
                   close the props come to each other.
arm_study()        the arm as a cantilever from the plates' edge to the motor: a uniform arm against
                   a fully stressed taper (width following the bending moment).

Beam theory (Euler-Bernoulli), woven 0/90 carbon plate: E 60 GPa, strength 600 MPa, 1.55 g/cm3.
"""

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from bolid import params as P

E = 60_000.0  # MPa
STRENGTH = 600.0  # MPa
RHO = 1.55e-3  # g / mm3
TIP_MASS = 40.0  # g: a 2207 motor, a 5.1 inch prop, its nut and screws
MOTOR_MASS = 40.0
BODY_MASS = 520.0  # g: battery, electronics, camera, frame centre: what does not move with the wheelbase
BODY_I = 520.0 * (70.0**2 + 35.0**2) / 12  # g mm2 about a horizontal axis, a 70 x 35 block
ARM_LINE_MASS = 0.12  # g per mm of arm (6 mm carbon, ~13 mm wide on average)


@dataclass
class Arm:
    name: str
    mass: float  # g, the free length
    k_vertical: float  # N/mm at the motor
    k_side: float
    f_vertical: float  # N at the motor that brings the most loaded fibre to the strength
    f_side: float
    freq: float  # Hz, first bending mode with the motor on the tip
    weakest_u: float  # mm from the centre, where it breaks first under a side hit


def beam(name: str, width, t: float = P.T_ARM, n: int = 400) -> Arm:
    L = P.U_MOTOR
    u = np.linspace(P.U_CLAMP, L, n)
    b = np.array([width(x) for x in u])
    m = L - u  # moment arm of a tip load
    du = u[1] - u[0]
    iv, iside = b * t**3 / 12, t * b**3 / 12
    k_v = 1 / np.trapezoid(m**2 / (E * iv), dx=du)
    k_s = 1 / np.trapezoid(m**2 / (E * iside), dx=du)
    with np.errstate(divide="ignore"):
        fv = STRENGTH * b * t**2 / (6 * m)
        fs = STRENGTH * t * b**2 / (6 * m)
    mass = RHO * t * np.trapezoid(b, dx=du)
    freq = sqrt(k_v * 1000 / ((TIP_MASS + 0.24 * mass) / 1000)) / (2 * pi)  # N/m over kg
    i = int(np.argmin(fs[:-1]))
    return Arm(name, mass, k_v, k_s, float(fv[:-1].min()), float(fs[:-1].min()), freq, float(u[i]))


def arm_study() -> list[Arm]:
    rows = [beam(f"uniform {w:g} mm", lambda x, w=w: w) for w in (12.0, 14.0, 16.0, P.W_CLAMP)]
    rows.append(beam(f"taper {P.W_CLAMP:g} -> {P.W_MIN:g} mm (Bolid)", P.arm_width))
    rows.append(beam(f"taper {P.W_CLAMP:g} -> {P.W_MIN:g} mm, 5 mm thick", P.arm_width, t=5.0))
    return rows


def chosen() -> Arm:
    return beam("Bolid", P.arm_width)


@dataclass
class Wheelbase:
    wheelbase: float
    tip_gap: float
    flip: float  # relative angular acceleration about roll/pitch (Bolid = 1)
    yaw: float  # relative yaw inertia (Bolid = 1): less is snappier


def _flip_and_yaw(wb: float) -> tuple[float, float]:
    r = wb / 2
    lever = r / sqrt(2)  # each motor's distance from the roll axis
    arms = 4 * ARM_LINE_MASS * r**3 / 3
    i_roll = BODY_I + 4 * MOTOR_MASS * lever**2 + arms / 2
    i_yaw = BODY_MASS * (70.0**2 + 35.0**2) / 12 + 4 * MOTOR_MASS * r**2 + arms
    return lever / i_roll, i_yaw


def wheelbase_study() -> list[Wheelbase]:
    a0, y0 = _flip_and_yaw(P.WHEELBASE)
    rows = []
    for wb in (200.0, 205.0, 210.0, P.WHEELBASE, 220.0, 225.0, 230.0, 240.0):
        a, y = _flip_and_yaw(wb)
        rows.append(Wheelbase(wb, wb / sqrt(2) - P.PROP_D, a / a0, y / y0))
    return rows


def smallest_wheelbase() -> float:
    """The smallest wheelbase that keeps TIP_GAP_MIN between the tips."""
    return (P.PROP_D + P.TIP_GAP_MIN) * sqrt(2)


def tables() -> str:
    out = ["wheelbase  tip gap  flip accel  yaw inertia", "-" * 44]
    for w in wheelbase_study():
        out.append(f"{w.wheelbase:9.0f} {w.tip_gap:8.1f} {w.flip:11.2f} {w.yaw:12.2f}")
    out += ["", f"smallest wheelbase with {P.TIP_GAP_MIN:g} mm between tips: {smallest_wheelbase():.1f} mm", ""]
    head = f"{'arm (free length)':34s} {'g':>5s} {'k up':>6s} {'k side':>7s} {'F up':>6s} {'F side':>7s} {'f1 Hz':>6s}"
    out += [head, "-" * len(head)]
    for a in arm_study():
        out.append(
            f"{a.name:34s} {a.mass:5.1f} {a.k_vertical:6.1f} {a.k_side:7.1f} {a.f_vertical:6.0f} {a.f_side:7.0f}"
            f" {a.freq:6.0f}  breaks first at u {a.weakest_u:.0f}"
        )
    return "\n".join(out)


if __name__ == "__main__":
    print(tables())
