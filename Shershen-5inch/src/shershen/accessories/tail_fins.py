"""Tail: Zhalo's antenna mount with two canted fins.

The mount itself is unchanged (SMA at 40 deg, snap channel for a T antenna). The fins rise
from its back wall either side of the antenna, lean outwards and sweep back. They are mostly
there for the look; what they do in practice is flank the antenna base and the SMA joint.
Being TPU they fold in a crash and come back.
"""

from build123d import Axis, Vector
from zhalo.accessories import tail_mount as base
from zhalo.accessories.kit import Accessory, P, mirror_x, poly, prism_x

FIN_T = 2.4
FIN_X = 11.5  # centre of each fin where it leaves the wall
CANT = 12.0  # degrees outwards from vertical
ROOT_Z = 14.5  # the cant hinges about this height
Y0 = base.WALL_Y[0]  # rear face of the back wall
# fin outline as (y, z), upright: 45 deg under-edge, raked trailing edge, swept tip, clear of the plate above
OUTLINE = [
    (Y0 + 0.02, ROOT_Z),
    (Y0 - 9.5, ROOT_Z + 9.5),
    (Y0 - 18.5, 56.0),
    (Y0 - 13.5, 59.5),
    (Y0 - 1.0, 41.0),
    (Y0 - 1.0, base.SLEEVE_TOP),
    (Y0 + 0.02, base.SLEEVE_TOP),
]
WINDOW = [(Y0 - 3.8, 31.5), (Y0 - 9.2, 31.5), (Y0 - 9.6, 44.5)]


def _fin():
    """Right-hand fin: upright blade, then leaned outwards about its root."""
    blade = prism_x(poly(OUTLINE, 1.2), FIN_X - FIN_T / 2, FIN_X + FIN_T / 2)
    blade -= prism_x(poly(WINDOW, 1.0), FIN_X - FIN_T, FIN_X + FIN_T)
    hinge = Axis((FIN_X, 0, ROOT_Z), (0, 1, 0))
    return blade.rotate(hinge, CANT)


def build() -> list[Accessory]:
    mount = base.build()[0]
    fin = _fin()
    part = mount.part + fin + mirror_x(fin)
    tip = part.bounding_box().max
    top_x = FIN_X + (P.PROP_Z[1] - ROOT_Z) * 0.2126  # tan(12 deg): where a fin crosses the top of the prop band
    own = list(mount.checks) + [
        (
            "fins stand clear either side of the antenna",
            FIN_X - FIN_T / 2 > 9.5 / 2 + 3.0,
            f"fins from X {FIN_X - FIN_T / 2:.1f}, antenna nut to X {9.5 / 2:.1f}",
        ),
        (
            "fin height",
            tip.Z > P.Z_ROOF + 15,
            f"tips at Z {tip.Z:.1f}, deck at Z {P.Z_ROOF:.1f}; X {top_x:.1f} at prop height",
        ),
    ]
    return [
        Accessory(
            "tail_fins",
            "Tail: antenna mount with twin fins",
            part,
            checks=own,
            ceilings=mount.ceilings,
            overhang=mount.overhang + 25.0,
            hardware=mount.hardware,
            color="accent",
            notes=mount.notes,
        )
    ]


_ = Vector
