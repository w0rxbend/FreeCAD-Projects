"""Head: camera mount and nose bumper in one piece, shaped as a hornet's jaws.

Inside it is Zhalo's camera cradle (two sleeves on the front standoffs, a cheek each side
of the camera, tilt on the camera's own M2 screws). Outside, a wall wraps the nose from
both standoffs and stops short of the centre line, leaving a gap the lens swings through.
The wall stands ahead of the carbon, so it is what meets a wall or a branch first.
"""

from zhalo import checks as C
from zhalo import equipment as E
from zhalo.accessories import camera_mount as cradle
from zhalo.accessories.kit import (
    SLEEVE_BORE,
    SLEEVE_OD,
    SLEEVE_TOP,
    Accessory,
    P,
    box,
    cylinder,
    hull,
    poly,
    prism,
    prism_x,
)

JAW_T = 2.4
NOSE = ((9.5, 76.5), 6.0)  # nose corners of the jaw, as (centre, radius)
LENS_MARGIN = 2.0  # each side of the lens in the gap between the jaws
SNARL = ((P.F[1] + 4.0, SLEEVE_TOP), (NOSE[0][1] + NOSE[1], 15.0))  # top edge, sloping down to the tips
WINDOW = ((61.5, 7.5), (69.5, 7.5), (61.5, 19.5))  # truss window in each jaw, as (y, z)
Z0 = cradle.Z0


def _wrap(shrink: float):
    (nx, ny), nr = NOSE
    r = SLEEVE_OD / 2
    return hull(
        [
            ((P.F[0], P.F[1]), r - shrink),
            ((nx, ny), nr - shrink),
            ((-nx, ny), nr - shrink),
            ((-P.F[0], P.F[1]), r - shrink),
        ]
    )


def _head(cam: E.Camera):
    body, _x_in, x_out = cradle._mount(cam)
    far = 60.0
    front = box(-far, P.F[1], Z0 - 1, far, 120, 60)
    jaw = prism(_wrap(0.0), Z0, SLEEVE_TOP) - prism(_wrap(JAW_T), Z0 - 1, SLEEVE_TOP + 1)
    gap = cam.lens_d / 2 + LENS_MARGIN
    jaw = (jaw & front) - box(-gap, P.F[1], Z0 - 1, gap, 120, 60)
    floor = prism(_wrap(0.0), Z0, Z0 + cradle.FLOOR_T) & front
    floor -= box(
        -cradle.FLOOR_WINDOW / 2, E.CAM_PIVOT[1] - 9.0, Z0 - 1, cradle.FLOOR_WINDOW / 2, E.CAM_PIVOT[1] + 2.0, Z0 + 5
    )
    part = body + jaw + floor
    (y0, z0), (y1, z1) = SNARL
    part -= prism_x(poly([(y0, z0), (y1, z1), (y1 + 20, z1), (y1 + 20, z0 + 20), (y0, z0 + 20)]), -far, far)
    for sx in (1, -1):
        x0, x1 = (x_out + 0.6, far) if sx > 0 else (-far, -x_out - 0.6)
        part -= prism_x(poly(list(WINDOW), 1.0), x0, x1)
        part -= cylinder(sx * P.F[0], P.F[1], Z0 - 1, SLEEVE_TOP + 1, SLEEVE_BORE)
    return part, gap


def _accessory(cam: E.Camera, tag: str, in_assembly: bool) -> Accessory:
    part, gap = _head(cam)
    lo, hi = E.CAM_TILT_RANGE
    swept = C.overlap(part, E.camera_sweep(cam, grow=0.0))
    reach = NOSE[0][1] + NOSE[1]
    carbon = max(F_NOSE)
    own = [
        (
            f"{cam.name} camera swings {lo:.0f}-{hi:.0f} deg without touching the head",
            swept < C.EPS,
            f"{swept:.3f} mm3",
        ),
        ("lens gap", gap >= cam.lens_d / 2 + 1.5, f"{2 * gap:.1f} mm for a {cam.lens_d:.0f} mm lens"),
        (
            "the jaws stand ahead of the carbon",
            reach >= carbon + 2.0,
            f"jaws to Y {reach:.1f}, carbon to Y {carbon:.1f}",
        ),
    ]
    return Accessory(
        f"head_{tag}",
        f"Head: camera mount and bumper, {cam.name}",
        part,
        holds=("camera",),
        in_assembly=in_assembly,
        hardware="2x M2x5 (the camera's own side screws)",
        checks=own,
        ceilings=6.0,
        overhang=12.0,
        color="accent",
        notes=(
            "Slide the two sleeves over the front standoffs before the top plate goes on. Set the tilt, then "
            "tighten the camera's side screws. Tilt range 15-45 deg."
        ),
    )


def _carbon_nose() -> tuple[float, float]:
    from shershen import profiles

    return profiles.FANG[1] + 2.6, profiles.MANDIBLE[1] + 2.6


F_NOSE = _carbon_nose()


def build() -> list[Accessory]:
    return [_accessory(E.CAM_MICRO, "19", True), _accessory(E.CAM_MINI, "22", False)]
