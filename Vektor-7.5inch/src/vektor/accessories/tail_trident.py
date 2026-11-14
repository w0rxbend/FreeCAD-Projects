"""Tail trident: every antenna at the back of the quad, behind and above the props.

  - the analog VTX antenna: an SMA bulkhead through the head of a fin, leaning 25 deg back;
  - two receiver antennas (a diversity receiver's pair): two tubes leaning out 45 deg to either side,
    so they stand 90 deg apart, one polarisation covering the other's null;
  - under the fin, a cradle for the XT60 socket, mouth to the rear: the battery lead plugs in behind.

Two sleeves hold it on the rear standoffs; a bridge over the receiver joins them to the fin. The fin
stays under the battery plate where the plate is, and rises behind it.
"""

from build123d import Axis

from vektor import gear as G
from vektor.accessories.base import BORE, FIT, Accessory, P, box, cyl, poly, prism_x
from vektor.geometry import body_posts, soften

Z0 = P.Z_DECK + 0.2
SLEEVE_TOP = P.Z_TOP - 9.2  # the top 9 mm of the standoff belong to the side fairings' rings
FIN_X = 4.0  # half its thickness
HEAD = (7.0, -114.0, -100.0, 56.0, 66.0)  # half width, y0, y1, z0, z1 of the fin's head
SMA_D, SMA_TILT = 6.5, 25.0
RX_LEAN, RX_BACK = 45.0, 20.0
TUBE = (7.0, 4.2, 16.0)  # outer diameter, bore, length
XT60 = (15.8, 16.0, 8.3)


def _post():
    return [p for p in body_posts() if p[1] < -50 and p[0] > 0][0]


def _rx_tube(sx: int, bore: bool):
    od, d, length = TUBE
    t = cyl(0, 0, -6.0 if bore else -3.0, length + (4 if bore else 0), d if bore else od)
    t = t.rotate(Axis.X, RX_BACK).rotate(Axis.Y, sx * RX_LEAN)
    hx, y0, y1, z0, z1 = HEAD
    return t.translate((sx * (hx - 1.0), (y0 + y1) / 2, z1 - 3.0))


def build() -> list[Accessory]:
    px, py = _post()
    rx_back = P.RX_Y - G.RX[1] / 2 - 0.5  # the receiver ends here: nothing of the fin's foot ahead of it
    part = cyl(px, py, Z0, SLEEVE_TOP, 9.0) + cyl(-px, py, Z0, SLEEVE_TOP, 9.0)
    part += box(-px, py - 6.0, 28.0, px, py + 1.0, SLEEVE_TOP)  # the bridge, over the receiver
    fin = poly(
        [
            (py - 2.0, 28.0),
            (py - 2.0, P.Z_TOP - 0.4),
            (-97.5, P.Z_TOP - 0.4),
            (-100.0, 66.0),
            (-106.0, 66.0),
            (-114.0, 60.0),
            (-114.0, 40.0),
            (-104.0, Z0),
            (rx_back, Z0),
            (rx_back, 28.0),
        ]
    )
    part += prism_x(soften(fin, 1.5), -FIN_X, FIN_X)
    hx, y0, y1, z0, z1 = HEAD
    # the head: a swept-back wedge, not a block
    head = soften(poly([(y0, z0), (y1, z0), (y1 + 1.5, z1), (y0 - 2.5, z1 + 1.0)]), 1.5)
    part += prism_x(head, -hx, hx)
    for sx in (1, -1):
        part += _rx_tube(sx, False)
    # XT60 cradle under the fin: an open channel, mouth to the rear
    w, l, h = XT60[0] + 2 * FIT, XT60[1] + FIT, XT60[2] + 2 * FIT
    cy0 = -122.0
    part += box(-w / 2 - 1.6, cy0, Z0, w / 2 + 1.6, cy0 + l + 2.0, Z0 + 1.6 + h - 1.5)
    part -= box(-w / 2, cy0 - 1, Z0 + 1.6, w / 2, cy0 + l, Z0 + 1.6 + h + 2)
    # bores
    for sx in (1, -1):
        part -= _rx_tube(sx, True)
        part -= cyl(sx * px, py, Z0 - 1, SLEEVE_TOP + 1, BORE)
    sma = cyl(0, 0, -20, 20, SMA_D).rotate(Axis.X, SMA_TILT).translate((0, (y0 + y1) / 2, (z0 + z1) / 2))
    part -= sma
    own = [
        ("VTX antenna: SMA bulkhead, leaning back", True, f"{SMA_D:g} mm hole, {SMA_TILT:g} deg back"),
        (
            "two receiver antennas 90 deg apart",
            abs(2 * RX_LEAN - 90) < 1e-9,
            f"each {RX_LEAN:g} deg out, {RX_BACK:g} deg back",
        ),
        ("antennas above the props", z0 > P.PROP_Z[1], f"head from Z {z0:g}, blades to Z {P.PROP_Z[1]:g}"),
        ("XT60 cradle", True, f"{w:.1f} x {h:.1f} mm channel, mouth to the rear at Y {cy0:g}"),
    ]
    return [
        Accessory(
            "tail_trident",
            "Tail trident (VTX antenna, two RX antennas, XT60)",
            part,
            bed=(0, 0, -1),
            color="accent",
            checks=own,
            bridges=300.0,
            overhang=30.0,
            hardware="the VTX antenna's SMA nut; a zip tie over the XT60",
            notes=(
                "Print it standing, as it sits on the quad (the bridge over the receiver spans 28 mm), "
                "4 perimeters, 30 % infill. Slide the sleeves over the rear standoffs "
                "before the battery plate goes on. Push each receiver antenna's base into a tube."
            ),
        )
    ]
