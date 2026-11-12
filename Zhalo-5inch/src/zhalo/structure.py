"""Structural sizing of an arm: a fast beam model for comparing shapes.

The arm is a cantilever from the edge of the sandwich (where the plates stop clamping it)
to the motor. Its section is a rectangle, thickness t, width w(x). Two tip loads matter:

  vertical  - thrust, a hard landing on an arm tip, a hit from above or below
  in-plane  - flying an arm into a gate, a branch or the ground at speed

For each the model gives the peak bending stress, the tip stiffness, the first natural
frequency with the motor and prop on the end, and the energy the arm stores before the
stress reaches the allowable somewhere. Crashes are energy events, so that last number is
the one that says how hard a hit the arm survives: it grows with the amount of material
AND with how evenly that material is stressed, which is why a tapered arm beats a
parallel one of the same weight.

Numbers are for a woven 0/90 carbon plate with the arm cut along the fibres. They compare
shapes reliably; as absolute values they are only as good as the plate (see MATERIAL).
The 3D finite-element check of the finished arm lives in `zhalo.fea`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from math import pi

import numpy as np


@dataclass(frozen=True)
class Material:
    """Woven 0/90 carbon/epoxy plate, 1 and 2 along the fibres, 3 through the thickness. MPa, g/mm3."""

    e1: float = 60_000.0  # in-plane modulus along either fibre direction
    e3: float = 8_000.0
    g12: float = 4_500.0  # in-plane shear: low for a 0/90 plate, about 17 000 with +-45 plies added
    g13: float = 3_500.0
    nu12: float = 0.05
    nu13: float = 0.30
    density: float = 1.55e-3
    strength: float = 600.0  # allowable bending stress along the fibres (veneer data sheets quote up to 880)
    shear: float = 60.0  # interlaminar shear strength


MATERIAL = Material()


@dataclass(frozen=True)
class Arm:
    """A cantilever arm: thickness, free length to the motor centre, and its width along that length."""

    name: str
    t: float
    length: float  # sandwich edge to motor centre
    width: Callable[[float], float]  # w(x), x from the sandwich edge
    pad: float = 14.0  # the last stretch under the motor is the pad: stiff, and not part of the beam
    tip_mass: float = 40.0  # motor, prop, screws; grams


@dataclass(frozen=True)
class Result:
    name: str
    mass: float  # g, free part of the beam (pad excluded)
    stress_v: float  # MPa per newton of vertical tip load, at the worst section
    stress_h: float  # MPa per newton of in-plane tip load
    where_v: float  # station of that worst section, mm from the sandwich edge
    where_h: float
    stiff_v: float  # N/mm at the motor
    stiff_h: float
    freq_v: float  # Hz
    freq_h: float
    load_v: float  # N at which the allowable stress is reached
    load_h: float
    energy_v: float  # J stored at that load
    energy_h: float
    twist: float  # N.mm per degree of twist at the motor
    evenness_v: float  # mean stress / peak stress along the beam, 1.0 = perfectly even
    evenness_h: float


def _torsion_factor(ratio):
    """Saint-Venant factor beta for a rectangle: J = beta * (long side) * (short side)^3."""
    r = np.maximum(ratio, 1.0)
    return (1 / 3) * (1 - 0.63 / r + 0.052 / r**5)


def analyse(arm: Arm, material: Material = MATERIAL, n: int = 600) -> Result:
    span = arm.length - arm.pad
    x = np.linspace(0.0, span, n)
    w = np.array([arm.width(v) for v in x])
    t = arm.t
    lever = arm.length - x  # bending moment per newton of tip load
    z_v, z_h = w * t**2 / 6, t * w**2 / 6  # section moduli
    i_v, i_h = w * t**3 / 12, t * w**3 / 12
    s_v, s_h = lever / z_v, lever / z_h
    trapz = np.trapezoid
    flex_v = trapz(lever**2 / (material.e1 * i_v), x)  # mm per newton at the motor (unit-load method)
    flex_h = trapz(lever**2 / (material.e1 * i_h), x)
    mass = material.density * trapz(w * t, x)

    def frequency(flex: float, inertia: np.ndarray) -> float:
        # Rayleigh: static deflection shape under the tip load, tip mass plus the beam's own share
        curvature = lever / (material.e1 * inertia)
        slope = np.concatenate([[0.0], np.cumsum((curvature[1:] + curvature[:-1]) / 2 * np.diff(x))])
        shape = np.concatenate([[0.0], np.cumsum((slope[1:] + slope[:-1]) / 2 * np.diff(x))])
        tip = shape[-1] + slope[-1] * arm.pad
        m_eff = arm.tip_mass + trapz(material.density * w * t * (shape / tip) ** 2, x)
        return float(np.sqrt(1 / flex / (m_eff * 1e-6)) / (2 * pi))  # N/mm over g -> rad/s via 1e-6 t

    long, short = np.maximum(w, t), np.minimum(w, t)
    gj = material.g12 * _torsion_factor(long / short) * long * short**3
    twist = 1 / trapz(1 / gj, x)  # N.mm per radian
    load_v, load_h = material.strength / s_v.max(), material.strength / s_h.max()
    return Result(
        name=arm.name,
        mass=float(mass),
        stress_v=float(s_v.max()),
        stress_h=float(s_h.max()),
        where_v=float(x[s_v.argmax()]),
        where_h=float(x[s_h.argmax()]),
        stiff_v=float(1 / flex_v),
        stiff_h=float(1 / flex_h),
        freq_v=frequency(flex_v, i_v),
        freq_h=frequency(flex_h, i_h),
        load_v=float(load_v),
        load_h=float(load_h),
        energy_v=float(0.5 * load_v**2 * flex_v / 1000),
        energy_h=float(0.5 * load_h**2 * flex_h / 1000),
        twist=float(twist * pi / 180),
        evenness_v=float(s_v.mean() / s_v.max()),
        evenness_h=float(s_h.mean() / s_h.max()),
    )


def tapered(root: float, neck: float, span: float, power: float = 1.0) -> Callable[[float], float]:
    """Width that falls from `root` at the sandwich edge to `neck` at the end of the beam.
    power 1 is a straight taper; below 1 the arm stays wide for longer and narrows late."""

    def width(x: float) -> float:
        s = min(max(x / span, 0.0), 1.0)
        return neck + (root - neck) * (1 - s) ** power

    return width


def table(results: list[Result], baseline: Result | None = None) -> str:
    """Side-by-side text table; every row after the baseline is followed by its change against it."""
    base = baseline or results[0]
    cols = ("mass", "F vert", "F side", "J vert", "J side", "k vert", "Hz vert", "Hz side", "twist")
    head = f"{'arm':<26}{cols[0]:>6}" + "".join(f"{c:>8}" for c in cols[1:])
    rows = [head, "-" * len(head)]
    for r in results:
        values = (r.load_v, r.load_h, r.energy_v, r.energy_h, r.stiff_v, r.freq_v, r.freq_h, r.twist)
        formats = ("8.0f", "8.0f", "8.2f", "8.2f", "8.1f", "8.0f", "8.0f", "8.0f")
        rows.append(f"{r.name:<26}{r.mass:>6.2f}" + "".join(f"{v:>{f}}" for v, f in zip(values, formats, strict=True)))
        if r is not base:
            ref = (
                base.load_v,
                base.load_h,
                base.energy_v,
                base.energy_h,
                base.stiff_v,
                base.freq_v,
                base.freq_h,
                base.twist,
            )
            change = "".join(f"{v / b - 1:>+8.0%}" for v, b in zip(values, ref, strict=True))
            rows.append(f"{'  vs ' + base.name:<26}{r.mass / base.mass - 1:>+6.0%}{change}")
    return "\n".join(rows)
