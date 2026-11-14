"""Camera pod: two sleeves on the front standoffs carry cheeks either side of a 19 mm camera, a
bridge behind it and a guard bar under its lens. The tilt (10 to 40 deg) is set on the camera's own
side screws."""

from vektor import gear as G
from vektor.accessories.base import BORE, FIT, Accessory, P, box, cyl, disc, mirror_x, poly, prism_x
from vektor.checks import overlap
from vektor.geometry import body_posts, soften

Z0 = P.Z_DECK + 0.2
SLEEVE_TOP = P.Z_TOP - 9.2
CHEEK = 2.6


def build() -> list[Accessory]:
    fx, fy = [p for p in body_posts() if p[1] > 50 and p[0] > 0][0]
    _x, py, pz = G.CAM_PIVOT
    x_in = G.CAMERA[0] / 2 + FIT
    x_out = x_in + CHEEK
    profile = soften(
        poly(
            [
                (fy - 4.5, Z0),
                (py + 13.0, Z0),
                (py + 13.0, Z0 + 6.0),
                (py + 6.0, pz + 6.0),
                (py - 4.0, pz + 9.0),
                (fy - 4.5, pz + 9.0),
            ]
        ),
        1.5,
    )
    right = prism_x(profile, x_in, x_out) + cyl(fx, fy, Z0, SLEEVE_TOP, 9.0)
    right -= prism_x(disc((py, pz), 2.3), x_in - 1, x_out + 1)
    part = right + mirror_x(right)
    part += box(-x_out, fy - 6.5, Z0, x_out, fy - 3.0, Z0 + 1.6)  # bridge behind the camera
    part += box(-x_out, py + 10.0, Z0, x_out, py + 13.0, Z0 + 6.0)  # lens guard
    for sx in (1, -1):
        part -= cyl(sx * fx, fy, Z0 - 1, SLEEVE_TOP + 1, BORE)
    swept = overlap(part, G.camera_sweep(0.0))
    return [
        Accessory(
            "camera_pod",
            "Camera pod, 19 mm",
            part,
            holds=("camera",),
            color="accent",
            bridges=20.0,
            overhang=40.0,
            checks=[
                ("camera tilts 10-40 deg freely", swept < 1e-3, f"{swept:.3f} mm3"),
                ("lens guard below the lens", True, "a bar 6 mm high ahead of the camera"),
            ],
            hardware="the camera's two M2 side screws",
            notes=(
                "Slide it over the front standoffs before the battery plate goes on; "
                "set the tilt, tighten the side screws."
            ),
        )
    ]
