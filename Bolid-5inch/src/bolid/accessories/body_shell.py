"""Body shell: the clean white skin round the bay, flush with the carbon's edge, from the camera to the
tail. It carries the camera between two cheeks, has racing gills on the flanks over the ESC, and ports
at its foot where the motor wires come in off the arms. Four sleeves slide it down the standoffs
before the top plate goes on: no screw shows."""

from build123d import Kind, offset

from bolid import gear as G
from bolid.accessories.base import BORE, FIT, Accessory, P, box, cyl, disc, mirror_x, poly, prism, prism_x
from bolid.geometry import clamp_outline, slot, soften

Z0, Z1 = P.Z_BAY + 0.2, P.Z_TOP - 0.2
WALL = 1.8
CHEEK = 2.4
SLEEVE = BORE + 2 * 1.6


def build() -> list[Accessory]:
    outer = offset(clamp_outline(), -0.2, kind=Kind.ARC)
    inner = offset(clamp_outline(), -0.2 - WALL, kind=Kind.ARC)
    part = prism(outer - inner, Z0, Z1)
    for x, y in P.STANDOFFS:  # sleeves, tied to the wall
        sx = 1 if x > 0 else -1
        part += cyl(x, y, Z0, Z1, SLEEVE)
        part += box(min(x, x + sx * 6.5), y - 2.0, Z0, max(x, x + sx * 6.5), y + 2.0, Z1) & prism(outer, Z0, Z1)
    # the camera's cheeks, from the front sleeves to the nose
    _x, py, pz = G.CAM_PIVOT
    x_in = G.CAMERA[0] / 2 + FIT + 0.15
    cheek = soften(poly([(P.STANDOFFS[0][1], Z0), (py + 9.0, Z0), (py + 9.0, Z1), (P.STANDOFFS[0][1], Z1)]), 1.0)
    right = prism_x(cheek, x_in, x_in + CHEEK)
    right -= prism_x(disc((py, pz), 2.3), x_in - 1, x_in + CHEEK + 1)
    part += right + mirror_x(right)
    part -= box(-x_in, P.STANDOFFS[0][1] + 3.0, Z0 - 1, x_in, 70.0, Z1 + 1)  # the camera's window, nose open
    # gills: four slanted slots each side, over the ESC
    for k in range(4):
        y0 = 10.0 - 7.0 * k
        g = slot((y0, 13.5), (y0 - 7.0, 20.5), 2.6)
        part -= prism_x(g, 15.0, 40.0)
        part -= prism_x(g, -40.0, -15.0)
    # wire ports at the foot, where each arm leaves the body
    for q in P.QUADS:
        cx, cy = P.on_arm(q, 26.0)
        part -= cyl(cx, cy, Z0 - 1, Z0 + 4.0, 13.0)
    for x, y in P.STANDOFFS:
        part -= cyl(x, y, Z0 - 1, Z1 + 1, BORE)
    for xy in P.MOTORS.values():  # sculpted where the props pass: the side scoops
        part -= G.keepout(xy)
    return [
        Accessory(
            "body_shell",
            "Body shell",
            part,
            color="shell",
            holds=("camera",),
            bridges=100.0,
            overhang=30.0,
            checks=[
                ("flush with the carbon", True, "outer face 0.2 mm inside the plates' edge"),
                ("no screw shows", True, "4 sleeves on the standoffs, held by the top plate"),
            ],
            hardware="the camera's two M2 side screws",
            notes=(
                "Print it standing on its foot, 3 perimeters (the wire ports bridge 13 mm). "
                "Slide it down the standoffs, then fit the top plate."
            ),
        )
    ]
