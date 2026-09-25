"""Rigid 3-finger GoPro / action-cam mount on the front top-plate accessory holes."""

import importlib
from math import sqrt

from build123d import (Axis, Circle, Part, Plane, Polygon, Pos, Rectangle, RectangleRounded,
                       RegularPolygon, extrude, fillet)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "gopro_mount"
TITLE = "GoPro / action-cam 3-finger mount"
MATERIAL = "PETG"
PRINT = {"gopro_mount": (0, 0, -1)}
EXCLUSIVE = ("gps_mount",)
MOUNTS = ("plate_top top face Z 36, y 56-96 (1250 mm² of bearing)",
          "Ø4.6 accessory holes (±27.3, 91) and (±31.3, 63.5)")
HARDWARE = ("4 x M3 x 10 button head + 4 x M3 nyloc nuts (heads in the Ø6.6 x 3 counterbores from "
            "above, nuts under the plate)",
            "1 x M5 thumb screw through the Ø5.5 axle + 1 x M5 nut (8.4 AF) captive in the +X "
            "finger pocket - the GoPro 3-finger hinge hardware")
NOTES = (
    "Bolts to the four Ø4.6 top-plate accessory holes (±27.3, 91) and (±31.3, 63.5) with M3 x 10 "
    "buttons (Ø6.6 x 3 counterbores from above, nyloc nuts under the plate); no registration bosses, "
    "the 0.6 mm bolt play locates it. Deviations from the catalog sketch, all forced by the required "
    "checks: the outline carries a Ø10 ear round every bolt (the Ø6.6 counterbore needs 1.7 mm of "
    "wall and would otherwise break out of a ±33.5/±30 trapezoid) and follows the plate edge back "
    "to y 56, so the envelope is x ±36.3 (at y 63.5) by y 56-96 and the base seats on 1250 mm² of "
    "plate_top; the camera window starts at y 83.5 instead of 92 because the 21 mm camera reaches "
    "Z 38.25 at 0 deg tilt and y 84.2 at Z 36 over its 0-40 deg sweep, and the finger feet end at "
    "y 81.5 (front flank leans 5.5 mm over 24 mm, 12.9 deg) so nothing cantilevers over that "
    "window. Root blends are 45 deg flares cut into the finger profile, not 3D fillets. Nut pocket "
    "ceiling is a 4.85 mm bridge (BRIDGE_OK)."
)

# --- parameters (mm) --------------------------------------------------------------------------
BASE_T = 5.0  # base plate: Z 36 (seated on plate_top) .. 41
BASE_Z0 = Z_TOP_TOP
BASE_Z1 = BASE_Z0 + BASE_T
OUTLINE = ((24.0, 56.0), (35.0, 61.0), (35.0, 68.0), (31.0, 88.0), (31.0, 95.0))  # right half, rear to front
CORNER_R = 4.0
EAR_R = 5.0  # ear round each bolt: 5.0 - CB_D/2 = 1.7 mm wall
JOIN_R = 1.5  # fillet where an ear meets the trapezoid

BOSS_H = 0.0  # no registration bosses (rev 2); the M3 buttons locate the part
BOLT_D = D_M3_THRU  # 3.4
CB_D, CB_H = 6.6, 3.0

WINDOW_X, WINDOW_Y = 12.0, 83.5  # camera window: |x| <= 12 forward of y 83.5
WINDOW_R = 2.0
LIGHT_XY = (22.0, 76.0)  # lightening windows at (+-22, 76)
LIGHT_W, LIGHT_L, LIGHT_R = 8.0, 14.0, 2.0

AXLE_H, AXLE_Y = 24.0, 80.0  # axle 24 above the base top -> Z 65
AXLE_Z = BASE_Z1 + AXLE_H
AXLE_D = 5.5
CROWN_R = 7.5
FINGER_Y0, FINGER_Y1 = 69.0, 81.5  # finger feet on the base top face
FINGER, GAP = 3.0, 3.2
FINGERS = ((-7.7, FINGER), (-1.5, FINGER), (4.7, FINGER + 3.5))  # (x0, width); +X finger holds the nut
NUT_AF, NUT_H = HEX_M5_AF, HEX_M5_H  # 8.4 AF x 4.2 M5 nut pocket
# 45 deg root flares fore/aft are cut into the 2D profile: a 3D fillet or chamfer at the finger
# roots makes OCCT's offset (and therefore min_wall) fail on this solid.
ROOT_R, SHOULDER_R = 1.0, 1.0

MIN_WALL = 1.5
BRIDGE_OK = {"gopro_mount": (("box", 5.5, -4.0, 23.0, 13.0, 9.0, 34.5),)}  # nut-pocket ceiling, print coords

_BOLTS = tuple(sorted((x, y) for x, y in hole_xy("top_accessory") if abs(x) > 1.0))


# --- 2D helpers -------------------------------------------------------------------------------
def _verts(sk, pred):
    return sk.vertices().filter_by(pred)


def _try_fillet(shape, edges, radii):
    for r in radii:
        if not r:
            return shape
        try:
            return type(shape)(shape.fillet(r, edges).wrapped)
        except Exception:  # noqa: BLE001 - radius too large for this geometry, try the next one
            continue
    return shape


def _base_sketch(p):
    right = list(p["OUTLINE"])
    poly = Polygon(*right, *[(-x, y) for x, y in reversed(right)], align=None)
    sk = fillet(poly.vertices(), p["CORNER_R"])
    for bx, by in _BOLTS:
        sk = sk + Pos(bx, by) * Circle(p["EAR_R"])
    # the union leaves one sharp vertex where each ear crosses the trapezoid edge
    joins = _verts(sk, lambda v: any(abs(((v.X - bx) ** 2 + (v.Y - by) ** 2) ** 0.5 - p["EAR_R"]) < 1e-4
                                     for bx, by in _BOLTS))
    if joins:
        sk = _try_fillet(sk, joins, (p["JOIN_R"], 0.8, 0.0))
    win_y1 = max(y for _x, y in _BOLTS) + p["EAR_R"] + 5
    sk = sk - Pos(0, (p["WINDOW_Y"] + win_y1) / 2) * Rectangle(2 * p["WINDOW_X"], win_y1 - p["WINDOW_Y"])
    corners = _verts(sk, lambda v: abs(v.Y - p["WINDOW_Y"]) < 1e-6 and abs(abs(v.X) - p["WINDOW_X"]) < 1e-6)
    if corners:
        sk = _try_fillet(sk, corners, (p["WINDOW_R"], 1.0, 0.0))
    lx, ly = p["LIGHT_XY"]
    for sx in (-1, 1):
        sk = sk - Pos(sx * lx, ly) * RectangleRounded(p["LIGHT_W"], p["LIGHT_L"], p["LIGHT_R"])
    return sk


def _finger_sketch(p):
    """Finger profile in the YZ plane: local x = frame Y, local y = frame Z."""
    y0, y1, zb = p["FINGER_Y0"], p["FINGER_Y1"], BASE_Z1
    ay, az, r = p["AXLE_Y"], AXLE_Z, p["CROWN_R"]
    f = p["ROOT_R"]
    trap = Polygon((y0 - f, zb), (y1 + f, zb), (y1, zb + f), (ay + r, az), (ay - r, az), (y0, zb + f),
                   align=None)
    sk = trap + Pos(ay, az) * Circle(r)
    sh = _verts(sk, lambda v: abs(v.Y - az) < 1e-6 and abs(abs(v.X - ay) - r) < 1e-4)
    if sh:
        sk = _try_fillet(sk, sh, (p["SHOULDER_R"], 0.5, 0.0))
    return sk


# --- build ------------------------------------------------------------------------------------
def build(**overrides) -> dict[str, Part]:
    p = {k: v for k, v in globals().items() if k.isupper()}
    p.update(overrides)

    part = extrude(Plane.XY.offset(BASE_Z0) * _base_sketch(p), amount=BASE_T)

    prof = _finger_sketch(p)
    for x0, w in p["FINGERS"]:
        part = part + extrude(Plane.YZ.offset(x0) * prof, amount=w)

    axle = Pos(p["AXLE_Y"], AXLE_Z) * Circle(p["AXLE_D"] / 2)
    part = part - extrude(Plane.YZ.offset(-30) * axle, amount=60)

    nx0, nw = p["FINGERS"][-1]
    nut = Pos(p["AXLE_Y"], AXLE_Z) * RegularPolygon(p["NUT_AF"] / sqrt(3), 6)
    part = part - extrude(Plane.YZ.offset(nx0 + nw - p["NUT_H"]) * nut, amount=p["NUT_H"] + 0.2)

    for bx, by in _BOLTS:
        part = part - cylinder(bx, by, BASE_Z0 - 1, BASE_Z1 + 1, p["BOLT_D"])
        part = part - cylinder(bx, by, BASE_Z1 - p["CB_H"], BASE_Z1 + 1, p["CB_D"])
    return {"gopro_mount": part}


# --- equipment probes -------------------------------------------------------------------------
def gopro_probe(tilt: float = 0.0) -> Part:
    """72 (X) x 34 (Y) x 51 body, bottom face 12 above the axle, centred on it; tilted lens-up."""
    body = box(-36, AXLE_Y - 17, AXLE_Z + 12, 36, AXLE_Y + 17, AXLE_Z + 12 + 51)
    return body.rotate(Axis((0, AXLE_Y, AXLE_Z), (1, 0, 0)), tilt) if tilt else body


def pack_probe() -> Part:
    """60 x 110 x 38 battery pack against the battery_pad front stop."""
    return box(-30, -58, 38.5, 30, 52, 76.5)


def _sibling(name: str) -> dict[str, Part]:
    try:
        return importlib.import_module(f"tigerbee.accessories.{name}").build()
    except Exception:  # noqa: BLE001 - sibling missing or work in progress
        return {}


# --- checks -----------------------------------------------------------------------------------
def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    m = parts["gopro_mount"]
    out: list[tuple[str, bool, str]] = []

    hits = interference(m)
    out.append(("no interference with any frame part", not hits, f"{hits or 'none'}"))

    bad = []
    for bx, by in _BOLTS:
        ok, detail = coaxial(m, (bx, by), BOLT_D, BASE_Z0 + 0.05, BASE_Z1 - CB_H - 0.05)
        v = isect(m, cylinder(bx, by, BASE_Z0 - 1, BASE_Z1 + 1, 3.2))
        if not ok or v > EPS:
            bad.append(f"({bx}, {by}): {detail}, Ø3.2 probe {v:.3f} mm³")
    out.append((f"Ø{BOLT_D} bores coaxial with the four top_accessory axes, Ø3.2 probes pass",
                not bad, "; ".join(bad) or f"{len(_BOLTS)} bores OK"))

    contact = seated(m, BASE_Z0)
    out.append(("base seated on plate_top at Z 36.000", contact >= 1200, f"{contact} mm² contact"))

    worst, over = -1e9, []
    for i in range(int(OUTLINE[0][1]), 98):
        y = float(i)
        sl = m & box(-45, y - 0.05, BASE_Z0 - 1, 45, y + 0.05, 80)
        if sl is None or not sl.volume:
            continue
        bb = sl.bounding_box()
        mx, lim = max(abs(bb.min.X), abs(bb.max.X)), max_abs_x_at(y)
        worst = max(worst, mx - lim)
        if mx > lim:
            over.append(f"y {y:.0f}: |x| {mx:.2f} > {lim:.2f}")
        if abs(y - 65) < 1e-6 and mx > 36.4:
            over.append(f"y 65: |x| {mx:.2f} > 36.4")
        if abs(y - 85) < 1e-6 and mx > 34.5:
            over.append(f"y 85: |x| {mx:.2f} > 34.5")
    disc = prop_disc_violation(m)
    out.append(("outline inside the prop keep-out at every 1 mm section", not over and disc < EPS,
                f"worst margin {-worst:.2f} mm, discs {disc:.3f} mm³" + (f"; {over}" if over else "")))

    vb = isect(m, BATTERY)
    out.append(("clear of the battery envelope", vb < EPS, f"{vb:.3f} mm³"))

    gaps = []
    for x0, w in FINGERS[:-1]:
        cx = x0 + w + GAP / 2
        v = isect(m, box(cx - GAP / 2, AXLE_Y - 20, BASE_Z1, cx + GAP / 2, AXLE_Y + 20, BASE_Z1 + 40))
        gaps.append(v)
    out.append((f"both {GAP} mm finger gaps clear", max(gaps) < EPS, f"{[round(v, 3) for v in gaps]} mm³"))

    nx0, nw = FINGERS[-1]
    probe = Pos(AXLE_Y, AXLE_Z) * RegularPolygon(8.0 / sqrt(3), 6)
    vn = isect(m, extrude(Plane.YZ.offset(nx0 + nw - 4.0) * probe, amount=4.0))
    out.append(("8.0 AF x 4 M5 nut fits the pocket", vn < EPS, f"{vn:.3f} mm³"))

    neighbours = {"mount": m, "pack": pack_probe(), **{f"frame:{n}": q for n, q in frame.items()}}
    for sib in ("battery_pad", "front_bumper", "camera_pod"):
        for label, q in _sibling(sib).items():
            if label in ("battery_pad", "camera_pod_21") or label.startswith("front_bumper"):
                neighbours[label] = q
    clash = []
    for tilt in (0.0, 30.0):
        g = gopro_probe(tilt)
        for n, q in neighbours.items():
            v = isect(g, q)
            if v > EPS:
                clash.append(f"{tilt:.0f}°/{n}: {v:.2f} mm³")
    checked = [n for n in neighbours if not n.startswith("frame:")]
    out.append(("GoPro body clears the frame, the mount and its neighbours at 0 and 30 deg",
                not clash, "; ".join(clash) or f"checked against {checked} + 15 frame parts"))

    cam = []
    for a in (0, 10, 20, 30, 40):
        v = isect(m, camera_envelope(21.0, tilt_deg=float(a)))
        if v > EPS:
            cam.append(f"{a}°: {v:.2f} mm³")
    for a in (15, 20, 30, 40):
        v = isect(m, fov_wedge(float(a)))
        if v > EPS:
            cam.append(f"fov {a}°: {v:.2f} mm³")
    out.append(("clear of the camera envelope 0-40 deg and its field of view", not cam,
                "; ".join(cam) or "0.000 mm³ at every pose"))

    ov = overhangs(m, PRINT["gopro_mount"], bridge_ok=BRIDGE_OK["gopro_mount"], material=MATERIAL)
    out.append(("printable base-down without supports", not ov, "; ".join(ov) or "none"))

    ok_w, _v, detail = min_wall(m, MIN_WALL)
    out.append((f"min wall >= {MIN_WALL}", ok_w, detail))

    vol = m.volume / 1000.0
    out.append(("volume 12-22 cm³", 12.0 <= vol <= 22.0, f"{vol:.2f} cm³"))
    return out
