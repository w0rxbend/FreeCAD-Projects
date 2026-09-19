"""Drop-on TPU caps over the two plate_top fork prong tips (left/right, no centre bridge)."""

from functools import lru_cache

from build123d import (Circle, Face, Part, Plane, Polygon, Pos, Rectangle, Sketch, Vector, extrude,
                       fillet, offset)

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks
from tigerbee.profiles import _outer_face

NAME = "front_bumper"
TITLE = "Front fork bumper caps"
MATERIAL = "TPU95A"
PRINT = {"front_bumper_right": (0, 1, 0), "front_bumper_left": (0, 1, 0)}
EXCLUSIVE = ()
NOTES = ("Press each cap down over a plate_top prong tip: the nose wrap flexes ~1.5 mm outward, the nib "
         "snaps under the rounded tip and the Ø6.4 hole drops over the front-tip standoff bolt head, which "
         "keys the cap fore/aft. Printed nose-down (frame +Y on the bed); skin, wall and nib then grow as "
         "vertical sheets off the nose. No centre bridge: it would sit in the camera FOV above 30° tilt.")

# --- parameters (mm) ------------------------------------------------------------------------
FIT_R = 0.25          # radial fit of the pocket round the prong outline
SKIN = 1.6            # top skin thickness (Z 36.0 seated -> 37.6)
WALL = 1.6            # outer wall thickness (prong outline +FIT_R .. +FIT_R+WALL)
WRAP_DEPTH = 3.35     # tip fit apex (y 114.666) -> nose front face y 118.0
BOLT_HEAD_D = 6.4     # clearance hole round the M3 button head on the standoff bolt
X_IN = 14.2           # inboard limit: 0.45 clear of the camera_pod cheeks (x <= 13.75)
SKIN_Y0 = 98.5        # rear end of the top skin (100 mm² of seated contact needs y0 <= 99.3)
SKIN_R = 1.0          # rounds the two rear corners of the skin
LEDGE = 1.0           # how far the skin overhangs the fork window edge (bolt-head web)
WALL_Y0 = 105.0       # rear end of the outer wall
NOSE_Y0 = 114.0       # the nose takes over from the wall here and wraps the tip
NIB_Y0, NIB_X = 112.5, (16.0, 21.0)  # the nib runs from the nose bottom (Z0) up to Z_NIB_TOP
NIB_CHAMFER = 0.4     # 45° lead-in on the nib's top-rear edge
FLARE = 1.8           # how far the nose stands proud of the wall at the front face
NOSE_R_OUT, NOSE_R_IN = 2.5, 1.5  # r_out is capped by the flare edge (tangent 3.86 of 4.40 mm)
Z0 = 31.8             # underside of wall and nose (the camera_pod channels end at Z 31.5)
Z_NOSE_TOP = 42.0
MIN_WALL_T = 1.5

Z_NIB_TOP = Z_TOP_UNDER - FIT_R  # 33.75: the nib's top face, 0.25 under the prong
_PRONG_CROP = (0.0, 40.0, 92.0, 125.0)  # right plate_top prong, isolated before offsetting


# --- 2D helpers ---------------------------------------------------------------------------
@lru_cache(maxsize=8)
def _prong(amount: float = 0.0) -> Sketch:
    """Right plate_top prong outline (x >= 0, y >= 92) offset by `amount` in 2D, at Z 0."""
    x0, x1, y0, y1 = _PRONG_CROP
    reg = (Sketch() + Face(_outer_face("plate_top").outer_wire())) & _strip(x0, x1, y0, y1)
    return offset(reg, amount=amount) if amount else reg


@lru_cache(maxsize=1)
def _fork_window() -> Sketch:
    """The open window between the two fork prongs (the face that contains the centre line)."""
    gap = _strip(-40, 40, FORK_CROTCH_Y + 1, PRONG_TIP_Y - 0.02) - (Sketch() + Face(_outer_face("plate_top").outer_wire()))
    return Sketch() + [f for f in gap.faces() if f.is_inside((0, 100, 0))]


def _strip(x0: float, x1: float, y0: float, y1: float) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _raise(sk: Sketch, z0: float, z1: float) -> Part:
    # dir is explicit: faces that come out of a 2D boolean can carry a -Z normal
    return extrude(Plane.XY.offset(z0) * sk, amount=z1 - z0, dir=(0, 0, 1))


def _max_x(sk: Sketch, y: float) -> float:
    return max(f.bounding_box().max.X for f in (sk & _strip(0, 60, y - 0.002, y + 0.002)).faces())


def _ahead_of(prong: Sketch, y: float) -> Sketch:
    """Half plane bounded by the line through the prong's outer edge at `y`, square to that edge and
    covering everything towards the tip."""
    x0, x1 = _max_x(prong, y - 1.0), _max_x(prong, y + 1.0)
    u = Vector(x1 - x0, 2.0).normalized()          # outer edge tangent, pointing at the tip
    a, w = Vector(_max_x(prong, y), y), Vector(-u.Y, u.X)
    return Polygon(*((a + w * s * 60 + u * d).to_tuple()[:2] for s, d in ((-1, 0), (1, 0), (1, 60), (-1, 60))),
                   align=None)


def _fillet_at(sk: Sketch, xy: tuple[float, float], r: float) -> Sketch:
    v = sk.vertices().filter_by(lambda p: abs(p.X - xy[0]) < 1e-6 and abs(p.Y - xy[1]) < 1e-6)
    assert len(v) == 1, f"expected one vertex at {xy}, found {len(v)}"
    for radius in (r, r * 0.75, r * 0.5):  # a shallow corner cannot take the nominal radius
        try:
            return fillet(v, radius)
        except ValueError:
            continue
    raise ValueError(f"cannot fillet {xy} at r {r}")


# --- geometry -----------------------------------------------------------------------------
def _pieces(**overrides) -> dict[str, tuple[Part, Sketch, float]]:
    """The four prisms the right cap is fused from: {name: (solid, footprint, height)}."""
    p = dict(FIT_R=FIT_R, SKIN=SKIN, WALL=WALL, WRAP_DEPTH=WRAP_DEPTH, X_IN=X_IN,
             BOLT_HEAD_D=BOLT_HEAD_D, SKIN_Y0=SKIN_Y0, WALL_Y0=WALL_Y0, NOSE_Y0=NOSE_Y0,
             FLARE=FLARE, LEDGE=LEDGE, **overrides)
    pocket = _prong(p["FIT_R"])                 # prong + fit: nothing below Z 36 may enter this
    outer = _prong(p["FIT_R"] + p["WALL"])      # outer face of the wall
    y_front = pocket.bounding_box().max.Y + p["WRAP_DEPTH"]   # 114.666 + 3.35

    # the skin overhangs the window edge by LEDGE so the bolt-head hole keeps a 1.5 mm web
    ledge = _prong(p["FIT_R"] + p["LEDGE"]) & _fork_window()
    skin_fp = (pocket + ledge) & _strip(0, 60, p["SKIN_Y0"], 200) & _strip(p["X_IN"], 60, 0, 200)
    for v in skin_fp.vertices().filter_by(lambda q: abs(q.Y - p["SKIN_Y0"]) < 1e-6):
        skin_fp = _fillet_at(skin_fp, (v.X, v.Y), SKIN_R)
    z_skin_top = Z_TOP_TOP + p["SKIN"]
    skin = _raise(skin_fp, Z_TOP_TOP, z_skin_top)
    skin -= cylinder(*FRONT_TIP_XY, Z_TOP_TOP - 1, z_skin_top + 1, p["BOLT_HEAD_D"])

    # the wall's rear end is cut square to the prong edge, so it ends in a 90° corner, not a wedge
    band = (outer - pocket) & _ahead_of(_prong(), p["WALL_Y0"]) & _strip(0, 60, 0, p["NOSE_Y0"])
    wall_fp = band - _fork_window()  # the band's inner leg lies in the window: drop it
    wall = _raise(wall_fp, Z0, z_skin_top)

    # nose: flat-fronted block wrapping the tip, its rear-outer corner picking up the wall's outer face
    x_back = max(_max_x(outer, y) for y in (p["NOSE_Y0"] - 1.0, p["NOSE_Y0"] - 0.5, p["NOSE_Y0"]))
    x_out = x_back + p["FLARE"]
    poly = Polygon((p["X_IN"], p["NOSE_Y0"]), (p["X_IN"], y_front), (x_out, y_front),
                   (x_back, p["NOSE_Y0"]), align=None)
    poly = _fillet_at(poly, (p["X_IN"], y_front), NOSE_R_IN)
    poly = _fillet_at(poly, (x_out, y_front), NOSE_R_OUT)
    nose_fp = poly - pocket
    nose = _raise(nose_fp, Z0, Z_NOSE_TOP)

    # snap nib: hooks under the prong tip; 45° lead-in on its rear top edge so it can be pressed on
    z_nib0, ch = Z0, NIB_CHAMFER
    nib_fp = Polygon((NIB_Y0, z_nib0), (y_front, z_nib0), (y_front, Z_NIB_TOP),
                     (NIB_Y0 + ch, Z_NIB_TOP), (NIB_Y0, Z_NIB_TOP - ch), align=None)
    nib = extrude(Plane(origin=(NIB_X[0], 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * nib_fp,
                  amount=NIB_X[1] - NIB_X[0], dir=(1, 0, 0))

    return {"skin": (skin, skin_fp, p["SKIN"]), "wall": (wall, wall_fp, z_skin_top - Z0),
            "nose": (nose, nose_fp, Z_NOSE_TOP - Z0), "nib": (nib, nib_fp, NIB_X[1] - NIB_X[0])}


def build(**overrides) -> dict[str, Part]:
    pieces = _pieces(**overrides)
    cap = pieces["skin"][0] + pieces["wall"][0] + pieces["nose"][0] + pieces["nib"][0]
    assert len(cap.solids()) == 1, f"front_bumper: {len(cap.solids())} solids"
    return pair(cap, NAME)


# --- checks -----------------------------------------------------------------------------------
def _pod() -> tuple[Part, str]:
    """The real camera_pod when its module is available, else a conservative envelope of it:
    cheeks x ±13.75 up to Z 33.8 plus the Ø10.5 C-channels on the front-tip standoffs to Z 31.5."""
    try:
        from tigerbee.accessories import camera_pod
        pod = None
        for part in camera_pod.build().values():
            pod = part if pod is None else pod + part
        return pod, "camera_pod module"
    except Exception:  # noqa: BLE001 - the sibling module need not exist yet
        env = box(-13.75, 78, 3, 13.75, 122.5, 33.8)
        for sx in (1, -1):
            env += cylinder(sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1], 9.2, 31.5, D_CLIP_BORE + 2 * CLIP_WALL)
        return env, "camera_pod envelope proxy"


def _mirror(part: Part, side: str) -> Part:
    return part if side == "right" else part.mirror(Plane.YZ)


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    out = []
    pieces = _pieces()
    pocket = _prong(FIT_R)
    y_front = pocket.bounding_box().max.Y + WRAP_DEPTH
    fit_ring = _raise((_prong(0.20) - _prong(-0.5)) & _strip(0, 60, 100, 112), Z0, Z_TOP_TOP)
    fit_band = _raise((_prong(0.30) - _prong(-0.5)) & _strip(0, 60, 100, 112), Z0, Z_TOP_TOP)
    nib_probe = _raise(_prong(0.20) & _strip(0, 60, 112, 200), Z_NIB_TOP, Z_TOP_TOP)
    head = cylinder(*FRONT_TIP_XY, Z_TOP_TOP, Z_TOP_TOP + H_M3_HEAD, D_M3_HEAD)
    web = (Pos(*FRONT_TIP_XY) * Circle(BOLT_HEAD_D / 2 + MIN_WALL_T)) - pieces["skin"][1]
    pod, pod_src = _pod()
    sweep = tilt_sweep(21, 0, 40)
    fov = [(t, fov_wedge(t)) for t in (15, 20, 30, 40)]

    for side in ("right", "left"):
        cap = parts[f"{NAME}_{side}"]
        hits = interference(cap)
        out.append((f"{side}: no frame interference", not hits, f"{hits or 'none'}"))
        contact = seated(cap, Z_TOP_TOP)
        out.append((f"{side}: skin seated on plate_top at Z 36.000", contact >= 100.0, f"{contact} mm² contact"))
        v = isect(cap, _mirror(fit_ring, side))
        out.append((f"{side}: prong fit >= +0.20 (slides on)", v < EPS, f"{v:.3f} mm³ inside outline +0.20"))
        v = isect(cap, _mirror(fit_band, side))
        out.append((f"{side}: prong fit <= +0.30 (wall hugs the prong)", v > EPS, f"{v:.3f} mm³ inside outline +0.30"))
        v = isect(cap, _mirror(nib_probe, side))
        out.append((f"{side}: nib clears the prong tip over Z {Z_NIB_TOP}-{Z_TOP_TOP}", v < EPS, f"{v:.3f} mm³"))
        v = isect(cap, _mirror(head, side))
        out.append((f"{side}: Ø{D_M3_HEAD} x {H_M3_HEAD} bolt head clear at ({FRONT_TIP_XY[0]}, {FRONT_TIP_XY[1]})",
                    v < EPS, f"{v:.3f} mm³"))
        v, d = isect(cap, pod), round(cap.distance_to(pod), 3)
        out.append((f"{side}: clear of camera_pod_21 by >= 0.3", v < EPS and d >= 0.3,
                    f"{v:.3f} mm³, gap {d} mm ({pod_src})"))
        v = isect(cap, sweep)
        out.append((f"{side}: outside the camera tilt sweep 0-40°", v < EPS, f"{v:.3f} mm³"))
        bad = [f"{t}°: {isect(cap, w):.3f} mm³" for t, w in fov if isect(cap, w) > EPS]
        out.append((f"{side}: outside the camera FOV wedges 15/20/30/40°", not bad, "; ".join(bad) or "0 mm³ at every tilt"))
        v = prop_disc_violation(cap)
        out.append((f"{side}: outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))
        v = isect(cap, BATTERY)
        out.append((f"{side}: outside the battery envelope", v < EPS, f"{v:.3f} mm³"))
        bed = sum(f.area for f in cap.faces() if f.geom_type == GeomType.PLANE
                  and f.normal_at().Y > 0.999 and abs(f.center().Y - y_front) < 1e-3)
        out.append((f"{side}: bed face at y {y_front:.1f} >= 60 mm²", bed >= 60.0, f"{bed:.1f} mm²"))
        over = overhangs(cap, PRINT[f"{NAME}_{side}"], material=MATERIAL)
        out.append((f"{side}: prints nose-down without supports", not over, "; ".join(over) or "none"))
        ok_w, _v, detail = min_wall(cap, MIN_WALL_T)
        out.append((f"{side}: min wall >= {MIN_WALL_T}", ok_w, detail))

    out.append((f"bolt-head hole web >= {MIN_WALL_T}", web is None or web.area < 1e-3,
                f"{0.0 if web is None else web.area:.3f} mm² of the Ø{BOLT_HEAD_D + 2 * MIN_WALL_T} "
                "collar falls outside the skin"))
    dv = abs(parts[f"{NAME}_right"].volume - parts[f"{NAME}_left"].volume)
    out.append(("left and right are the same part mirrored", dv < 0.01,
                f"Δ{dv:.5f} mm³ of {parts[f'{NAME}_right'].volume:.1f} mm³"))
    return out
