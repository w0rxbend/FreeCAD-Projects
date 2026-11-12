"""Camera mount: two sleeves on the front standoffs carrying a cheek on each side of the camera.

The camera hangs on its own two M2 side screws through the cheeks, so the up-tilt is set by
hand and held by the screws clamping TPU against the camera body. The sleeves stop below
the top band of the standoffs, which is left to the side-panel hooks.
"""

from zhalo import checks as C
from zhalo import equipment as E
from zhalo.accessories.kit import (
    D_M2_FREE,
    FIT,
    SLEEVE_BORE,
    SLEEVE_OD,
    SLEEVE_TOP,
    Accessory,
    P,
    box,
    cylinder,
    disc,
    mirror_x,
    poly,
    prism_x,
)

CHEEK_T = 2.6
FLOOR_T = 1.6
Z0 = P.Z_ARM  # stands on the bottom plate
Y_REAR, Y_FRONT = P.F[1] - SLEEVE_OD / 2, E.CAM_PIVOT[1] + 7.0
FLOOR_WINDOW = 11.0  # square opening under the camera: less weight, and the plate window stays open


def _mount(cam: E.Camera):
    px, py, pz = E.CAM_PIVOT
    x_in = cam.width / 2 + FIT
    x_out = x_in + CHEEK_T
    # cheek seen from the side: a rounded plate with its nose just ahead of the side screw
    profile = poly(
        [
            (Y_REAR, Z0),
            (Y_FRONT - 2.0, Z0),
            (Y_FRONT, Z0 + 8.0),
            (Y_FRONT, pz + 5.0),
            (py + 1.0, SLEEVE_TOP),
            (Y_REAR, SLEEVE_TOP),
        ],
        2.0,
    )
    right = prism_x(profile, x_in, x_out) + cylinder(*P.F, Z0, SLEEVE_TOP, SLEEVE_OD)
    right -= prism_x(disc((py, pz), D_M2_FREE), x_in - 1, x_out + 1)
    floor = box(-x_out, Y_REAR, Z0, x_out, Y_FRONT - 2.0, Z0 + FLOOR_T)
    floor -= box(-FLOOR_WINDOW / 2, py - 9.0, Z0 - 1, FLOOR_WINDOW / 2, py + 2.0, Z0 + FLOOR_T + 1)
    body = right + mirror_x(right) + floor
    for sx in (1, -1):
        body -= cylinder(sx * P.F[0], P.F[1], Z0 - 1, SLEEVE_TOP + 1, SLEEVE_BORE)
    return body, x_in, x_out


def _accessory(cam: E.Camera, tag: str, in_assembly: bool) -> Accessory:
    part, x_in, x_out = _mount(cam)
    px, py, pz = E.CAM_PIVOT
    lo, hi = E.CAM_TILT_RANGE
    swept = C.overlap(part, E.camera_sweep(cam, grow=0.0))
    probe = prism_x(disc((py, pz), 1.8), -x_out - 1, x_out + 1)
    screw = C.overlap(part, probe)
    gap = P.F[0] - SLEEVE_BORE / 2 - x_in
    own = [
        (
            f"{cam.name} camera swings {lo:.0f}-{hi:.0f} deg without touching the mount",
            swept < C.EPS,
            f"{swept:.3f} mm3",
        ),
        (
            "side screw holes are on the tilt axis",
            screw < C.EPS,
            f"{screw:.3f} mm3 in a 1.8 mm pin through both cheeks",
        ),
        ("TPU left between the camera and each standoff", gap >= 1.5, f"{gap:.2f} mm"),
    ]
    return Accessory(
        f"camera_mount_{tag}",
        f"Camera mount, {cam.name}",
        part,
        holds=("camera",),
        in_assembly=in_assembly,
        hardware="2x M2x5 (the camera's own side screws)",
        checks=own,
        ceilings=6.0,
        overhang=8.0,
        notes=(
            "Slide the two sleeves over the front standoffs before the top plate goes on. Set the tilt, then "
            "tighten the camera's side screws. Tilt range 15-45 deg."
        ),
    )


def build() -> list[Accessory]:
    return [_accessory(E.CAM_MICRO, "19", True), _accessory(E.CAM_MINI, "22", False)]
