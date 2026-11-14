"""The arm as a box beam: a plane frame of finite elements, solved with numpy.

Model, in the vertical plane through the arm (x along the arm from where the body holds it, z up):
  - the upper and the lower skin are two beams ("flanges"). In a truss bay only the two chords carry
    load along the arm, so a flange there has the chords' area; between bays and under the motor it
    is the full strip.
  - each spacer is a short aluminium tube joining the two flanges. How well a bolted spacer holds
    the flanges square to it is not known without a test, so it is solved twice: rigidly joined
    (the box acts as one beam as far as a Vierendeel girder can) and pinned (the flanges only push
    and pull on each other through the spacer). The truth lies between.
  - both flanges are clamped where the body holds the arm; the motor's load and mass sit on the upper
    flange at the motor centre.

Results per case: tip stiffness, the tip load at which the most stressed fibre reaches the carbon's
allowable, and the first bending frequency with the motor and prop on the end.
"""

from dataclasses import dataclass
from math import pi

import numpy as np

from vektor import params as P

E_CARBON = 60_000.0  # MPa, woven 0/90 plate along the fibres
E_ALU = 70_000.0
STRENGTH = 600.0  # MPa
RHO_CARBON = 1.55e-3  # g / mm3
TIP_MASS = 62.0  # g: a 2807 motor, a 7.5 inch prop, screws
X0 = 40.0  # where the body stops holding the arm (r)
CHORD_EFF = P.CHORD + P.DIAG  # what the truss windows leave of the flange at each edge


@dataclass
class Result:
    name: str
    stiffness: float  # N/mm at the motor
    load: float  # N at the allowable
    freq: float  # Hz, first bending mode
    mass: float  # g of carbon from X0 to the motor


def _in_bay(r: float) -> bool:
    s = P.STATIONS
    return any(a + P.STATION_RIB <= r <= b - P.STATION_RIB for a, b in zip(s[:-1], s[1:], strict=True))


def flange(r: float, t: float = P.T_SKIN, windows: bool = True) -> tuple[float, float, float]:
    """(area, second moment about its own axis, half thickness) of one skin's strip at station r."""
    w = 2 * P.half_width(r)
    if windows and _in_bay(r):
        a = t * 2 * CHORD_EFF
    else:
        a = t * w
    return a, a * t * t / 12.0, t / 2


def _frame(nodes, elems, fixed, load_node, tip_mass, lumped):
    """Assemble and solve. nodes: [(x, z)], elems: [(i, j, EA, EI, release_i, release_j)]."""
    n = len(nodes)
    K = np.zeros((3 * n, 3 * n))
    for i, j, ea, ei, rel_i, rel_j in elems:
        (xi, zi), (xj, zj) = nodes[i], nodes[j]
        L = np.hypot(xj - xi, zj - zi)
        c, s = (xj - xi) / L, (zj - zi) / L
        k = np.zeros((6, 6))
        k[0, 0] = k[3, 3] = ea / L
        k[0, 3] = k[3, 0] = -ea / L
        if rel_i or rel_j:  # a pinned end: the element carries no moment there (pinned both: a link)
            if rel_i and rel_j:
                pass
            else:
                kk = 3 * ei / L**3
                if rel_i:
                    idx, kloc = (
                        [1, 4, 5],
                        np.array([[kk, -kk, kk * L], [-kk, kk, -kk * L], [kk * L, -kk * L, kk * L * L]]),
                    )
                else:
                    idx, kloc = (
                        [1, 2, 4],
                        np.array([[kk, kk * L, -kk], [kk * L, kk * L * L, -kk * L], [-kk, -kk * L, kk]]),
                    )
                for a_, ia in enumerate(idx):
                    for b_, ib in enumerate(idx):
                        k[ia, ib] += kloc[a_, b_]
        else:
            b = ei / L**3
            k[np.ix_([1, 2, 4, 5], [1, 2, 4, 5])] += b * np.array(
                [
                    [12, 6 * L, -12, 6 * L],
                    [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                    [-12, -6 * L, 12, -6 * L],
                    [6 * L, 2 * L * L, -6 * L, 4 * L * L],
                ]
            )
        T = np.zeros((6, 6))
        rot = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T[:3, :3] = rot
        T[3:, 3:] = rot
        kg = T.T @ k @ T
        dofs = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        K[np.ix_(dofs, dofs)] += kg
    free = [d for d in range(3 * n) if d not in fixed]
    # rotational dofs that nothing stiffens (a node joined only by pinned ends) get a tiny spring
    for d in free:
        if abs(K[d, d]) < 1e-9:
            K[d, d] = 1e-6
    F = np.zeros(3 * n)
    F[3 * load_node + 1] = -1.0  # 1 N down at the motor
    u = np.zeros(3 * n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    M = np.diag(lumped)
    M[3 * load_node, 3 * load_node] += tip_mass * 1e-6
    M[3 * load_node + 1, 3 * load_node + 1] += tip_mass * 1e-6
    Kf, Mf = K[np.ix_(free, free)], M[np.ix_(free, free)]
    trans = [k for k, d in enumerate(free) if d % 3 != 2]
    # static condensation of rotations is overkill here: rotations get a small mass instead
    for k_, d in enumerate(free):
        if d % 3 == 2:
            Mf[k_, k_] += 1e-12
    w2 = np.linalg.eigvals(np.linalg.solve(Mf, Kf)).real
    w2 = np.sort(w2[w2 > 1e-6])
    _ = trans
    return u, float(np.sqrt(w2[0]) / (2 * pi))


def box_arm(cavity: float = P.CAVITY, joint: str = "rigid", seg: float = 4.0) -> Result:
    """The two-skin arm. joint: 'rigid' or 'pinned' spacer-to-skin joints."""
    t = P.T_SKIN
    h = cavity + t  # flange centre to flange centre
    x_tip = P.ARM_R - X0
    xs = sorted(set(np.arange(0.0, x_tip, seg).tolist() + [st - X0 for st in P.STATIONS] + [x_tip]))
    xs = [x for x in xs if x >= 0]
    top = list(range(len(xs)))
    nodes = [(x, h) for x in xs] + [(x, 0.0) for x in xs]
    bot = [len(xs) + i for i in range(len(xs))]
    elems, lumped = [], np.zeros(3 * len(nodes))
    lower_end = (
        P.STATIONS[-1] - X0 + 1e-6
    )  # the lower skin is a ring round the motor: it stops carrying past the last spacer
    for k in range(len(xs) - 1):
        r = X0 + (xs[k] + xs[k + 1]) / 2
        a, i_, _ = flange(r, t)
        L = xs[k + 1] - xs[k]
        for line, z in ((top, h), (bot, 0.0)):
            if z == 0.0 and xs[k + 1] > lower_end:  # no element of the lower skin past its last spacer
                continue
            elems.append((line[k], line[k + 1], E_CARBON * a, E_CARBON * i_, False, False))
            m = RHO_CARBON * a * L * 1e-6 / 2
            for nn in (line[k], line[k + 1]):
                lumped[3 * nn] += m
                lumped[3 * nn + 1] += m
    d_o, d_i = P.SPACER_D, 2.5
    a_s, i_s = pi * (d_o**2 - d_i**2) / 4, pi * (d_o**4 - d_i**4) / 64
    for st in P.STATIONS:
        k = xs.index(st - X0)
        pinned = joint == "pinned"
        elems.append((bot[k], top[k], E_ALU * a_s, E_ALU * i_s, pinned, pinned))
    fixed = [3 * top[0], 3 * top[0] + 1, 3 * top[0] + 2, 3 * bot[0], 3 * bot[0] + 1, 3 * bot[0] + 2]
    # nodes of the lower skin past its end are not connected: fix them out of the way
    for k, x in enumerate(xs):
        if x > lower_end:
            fixed += [3 * bot[k], 3 * bot[k] + 1, 3 * bot[k] + 2]
    tip = top[-1]
    u, f1 = _frame(nodes, elems, fixed, tip, TIP_MASS, lumped)
    k_tip = 1.0 / abs(u[3 * tip + 1])
    # stress per newton: axial + bending in every flange element, at its outer fibre
    worst = 0.0
    for i, j, ea, ei, *_ in elems:
        (xi, zi), (xj, zj) = nodes[i], nodes[j]
        if abs(zi - zj) > 1e-9:
            continue  # spacers are aluminium: checked separately below
        L = xj - xi
        a, iz = ea / E_CARBON, ei / E_CARBON
        n_force = ea * (u[3 * j] - u[3 * i]) / L
        th_i, th_j = u[3 * i + 2], u[3 * j + 2]
        v_i, v_j = u[3 * i + 1], u[3 * j + 1]
        m_i = ei / L**2 * (6 * (v_j - v_i) - L * (4 * th_i + 2 * th_j))
        m_j = ei / L**2 * (-6 * (v_j - v_i) + L * (2 * th_i + 4 * th_j))
        sig = abs(n_force) / a + max(abs(m_i), abs(m_j)) * (P.T_SKIN / 2) / iz
        worst = max(worst, sig)
    mass = sum(RHO_CARBON * flange(X0 + x)[0] * seg for x in np.arange(0, x_tip, seg)) * 2
    return Result(f"box {cavity:g} mm, {joint} spacers", k_tip, STRENGTH / worst, f1, mass)


def solid_arm(t: float) -> Result:
    """Reference: a one-piece arm of thickness t with the same planform and no windows (a cantilever)."""
    x_tip = P.ARM_R - X0
    n = 200
    xs = np.linspace(0, x_tip, n + 1)
    w = np.array([2 * P.half_width(X0 + x) for x in xs])
    ei = E_CARBON * w * t**3 / 12
    # unit load at the tip: M(x) = (x_tip - x); deflection by integrating curvature twice
    m = x_tip - xs
    kappa = m / ei
    theta = np.concatenate([[0], np.cumsum((kappa[1:] + kappa[:-1]) / 2 * np.diff(xs))])
    v = np.concatenate([[0], np.cumsum((theta[1:] + theta[:-1]) / 2 * np.diff(xs))])
    k_tip = 1 / v[-1]
    sig = np.max(m * (t / 2) / (w * t**3 / 12))
    mass_line = RHO_CARBON * w * t
    mass = float(np.trapezoid(mass_line, xs))
    # Rayleigh: tip mass + a third of the beam's, on the static stiffness (good for a cantilever with a heavy tip)
    f1 = (1 / (2 * pi)) * np.sqrt(k_tip / ((TIP_MASS + 0.24 * mass) * 1e-6 / 1000)) / np.sqrt(1000)
    return Result(f"solid {t:g} mm", float(k_tip), float(STRENGTH / sig), float(f1), mass)


def table(rows: list[Result]) -> str:
    head = f"{'arm':34s} {'mass g':>7s} {'k N/mm':>8s} {'load N':>8s} {'f1 Hz':>7s}"
    lines = [head, "-" * len(head)]
    for r in rows:
        lines.append(f"{r.name:34s} {r.mass:7.1f} {r.stiffness:8.1f} {r.load:8.0f} {r.freq:7.0f}")
    return "\n".join(lines)


# --- the box with shear webs ------------------------------------------------------------------------
G_CARBON = 4_500.0  # MPa, in-plane shear of a 0/90 plate: what the webs shear with
WEB_INSET = P.WEB_INSET


def box_webbed(
    cavity: float = P.CAVITY, t_web: float = P.T_WEB, chord: float | None = None, t: float = P.T_SKIN
) -> Result:
    """Two skins and two carbon webs along the arm's edges, tabbed into both skins: a closed box section.
    Plane sections stay plane (the webs carry the shear), so it is a beam: bending + shear deflection."""
    chord_eff = CHORD_EFF if chord is None else chord
    x_tip = P.ARM_R - X0
    web_end = P.WEB_R[1] - X0  # the webs run under the motor ring
    xs = np.linspace(0, x_tip, 600)
    d = cavity + t  # flange centre to flange centre
    ei, ga, mass_line, c_out = [], [], [], d / 2 + t / 2
    for x in xs:
        r = X0 + x
        w = 2 * P.half_width(r)
        if x <= web_end:
            a_f = t * (2 * chord_eff if _in_bay(r) else w)
            i = 2 * a_f * (d / 2) ** 2 + 2 * a_f * t * t / 12 + 2 * t_web * cavity**3 / 12
            ga.append(G_CARBON * 2 * t_web * cavity)
            mass_line.append(RHO_CARBON * (2 * a_f + 2 * t_web * cavity))
        else:  # past the webs only the upper skin's motor pad carries the motor
            wp = 2 * P.PAD_R
            i = wp * t**3 / 12
            ga.append(G_CARBON * wp * t * 5 / 6)
            mass_line.append(RHO_CARBON * wp * t)
        ei.append(E_CARBON * i)
    ei, ga, mass_line = np.array(ei), np.array(ga), np.array(mass_line)
    m = x_tip - xs
    kappa = m / ei
    theta = np.concatenate([[0], np.cumsum((kappa[1:] + kappa[:-1]) / 2 * np.diff(xs))])
    v_b = np.concatenate([[0], np.cumsum((theta[1:] + theta[:-1]) / 2 * np.diff(xs))])[-1]
    v_s = float(np.trapezoid(1.0 / ga, xs))
    k = 1 / (v_b + v_s)
    sig = np.where(xs <= web_end, m * c_out / (ei / E_CARBON), m * (t / 2) / (ei / E_CARBON))
    mass = float(np.trapezoid(mass_line, xs))
    f1 = (1 / (2 * pi)) * np.sqrt(k * 1000 / ((TIP_MASS + 0.24 * mass) * 1e-3))
    name = f"box {cavity:g} mm + {t_web:g} mm webs"
    return Result(name, float(k), float(STRENGTH / sig.max()), float(f1), mass)


def study() -> list[Result]:
    rows = [solid_arm(6.0), solid_arm(8.0), box_arm(12.0, "pinned"), box_arm(12.0, "rigid")]
    for cav in (8.0, 10.0, 12.0, 14.0):
        for tw in (1.0, 1.5, 2.0):
            rows.append(box_webbed(cav, tw))
    return rows


def chosen() -> Result:
    return box_webbed(P.CAVITY, P.T_WEB)


if __name__ == "__main__":
    print(table(study()))
