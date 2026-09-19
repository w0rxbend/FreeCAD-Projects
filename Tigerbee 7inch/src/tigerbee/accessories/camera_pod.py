"""Front slide-on U-pod for a 19 or 21 mm FPV camera on the mid-plate nose."""

from copy import deepcopy

from build123d import Circle, Edge, GeomType, Part, Plane, Polygon, Pos, SlotArc, extrude

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks

NAME = "camera_pod"
TITLE = "Camera pod (19 / 21 mm)"
MATERIAL = "TPU95A"
PRINT = {"camera_pod_21": (0, -1, 0), "camera_pod_19": (0, -1, 0)}
EXCLUSIVE = ()
NOTES = ("Slides on from the front: the pod is pushed rearwards (-Y) over the Ø6 front-tip standoffs, "
         "which snap through the 5.2 mm mouths, until the nose nubs drop into the mid-plate V-notches and "
         "the rails sit on plate_mid; it comes off the same way, forwards. Tilt is set by the camera's own "
         "M2 side screws - pivot hole plus a 15-40° arc slot; the cable leaves through the open top of the "
         "backplate. No brow bar: anything ahead of the lens sits in the FOV. The pod must come off before "
         "a 25.5 mm-pattern board can be fitted in the forward bay (its rear screws are at y 81.5).")

# --- parameters (mm) ------------------------------------------------------------------------
CAM_W = 21.0          # the two shipped widths are CAM_W 21 and 19; nothing else changes
CAM_H = 22.0
CAM_D = 24.0
PIVOT_Y, PIVOT_Z = CAM_PIVOT[1], CAM_PIVOT[2]   # (0, 100, 27)
TILT_RANGE = (15.0, 40.0)
TILT_MARGIN = 1.0     # the arc slot runs 1 deg beyond each end so the end poses are not tangent
CHEEK = 3.0
CHANNEL_TOP = 31.5    # 0.3 below the front_bumper lip
CHANNEL_WALL = 1.7    # OD 9.9: printed on its back the channel is an arch just inside the TPU limit
CHANNEL_Z0 = Z_MID_TOP + 0.2
MOUTH_DEG = 270.0     # the mouth opens towards -Y: the pod is pushed on from the front (-Y) and
SNAP = 0.8            # pulled off forwards (+Y); mouth = STANDOFF_D - SNAP = 5.2
CHIN = True
FIT = 0.25

FLOOR_Y0, FLOOR_Y1 = 80.5, 116.0    # clear of the fwd_30p5 heads at y 76.75 and of a 36 mm board at y 61.5
FLOOR_Z1 = 13.0                     # 4 mm rails: the pod's only bending stiffness at the floor
CB_REAR_Y1 = 86.0                   # rear crossbar y 80.5-86 (no slot nub - the slot at (0, 82.5) stays free)
CB_FRONT_Y0 = 112.0
WALL_X = 15.75                      # backplate half-width: 0.25 clear of the Ø6 standoffs on the way off
WALL_DEEP = 88.5                    # depth outboard of the camera
WALL_SHALLOW = 84.8                 # depth in front of it: the body's rear face at 0 deg is at y 85.75
WIN_Z0 = 22.4                       # above this the backplate is open across the camera: its rear-top
                                    # corner swings back to y 81.85 and the cable leaves through here
CAM_PAD = 0.3                       # backplate opening half-width = CAM_W/2 + FIT + CAM_PAD
CHEEK_Y0, CHEEK_Y1, CHEEK_TOP = 84.0, 114.0, 33.8
DIAMOND_Y, DIAMOND_Z = 91.0, 20.0   # lightening window 9 (Y) x 6 (Z): long axis along the print vertical
DIAMOND_YL, DIAMOND_ZL = 9.0, 6.0
SLOT_R, SLOT_W = 6.0, D_M2_THRU     # the second camera screw sits 6 mm behind the pivot at 0 deg
POST_Y0, POST_Y1, POST_TOP = 114.0, 122.5, 38.0
POST_RAMP_Y = 118.6                 # ramp (114, 33.8) -> (118.6, 38): 42 deg, so not an overhang
CHIN_Y0, CHIN_Y1, CHIN_Z0, CHIN_Z1 = 116.5, 122.5, 6.0, 20.0
CHIN_CHAMFER = 1.1                  # rear face y = CHIN_Y0 + 1.1 (9 - Z) below Z 9
NUB_X, NUB_XW, NUB_Y0, NUB_YL = 10.2, 3.0, 110.0, 3.0
NUB_Z0 = 7.5                        # 3.0 x 1.5 rear face = 4.5 mm2, below the overhang check's 5 mm2:
                                    # a chamfer instead would taper to a knife edge at Z 9
WEB_X, WEB_Y0, WEB_Y1, WEB_CH = 16.0, 103.0, 113.5, 4.0  # cheek -> channel web, inboard of the mouth
WEB_FLARE = (19.5, 109.0)           # corridor (x 16.4-21.6) and clear of the M2 screw heads (y < 102.1);
                                    # ahead of y 109 the standoff never passes, so the web flares out

_ENV_Y0, _ENV_Z0, _ENV_Z1 = FLOOR_Y0, CHIN_Z0, POST_TOP  # printed: X = x, Y = (Z0+Z1)/2 - z, Z = y - Y0


def _print_box(x0, y0, z0, x1, y1, z1, pad=1.0):
    """Frame-coordinate box -> a bridge_ok ('box', ...) in PRINT coordinates (bed = the y 80.5 face)."""
    yc = (_ENV_Z0 + _ENV_Z1) / 2
    return ("box", x0 - pad, yc - z1 - pad, y0 - _ENV_Y0 - pad, x1 + pad, yc - z0 + pad, y1 - _ENV_Y0 + pad)


# chin rear face (a bridge between the two posts) and the front crossbar's rear face
_BRIDGES = (_print_box(-13.75, CHIN_Y0, Z_MID_TOP, 13.75, CHIN_Y0, CHIN_Z1),
            _print_box(-13.75, CB_FRONT_Y0, Z_MID_TOP, 13.75, CB_FRONT_Y0, FLOOR_Z1))
BRIDGE_OK = {"camera_pod_21": _BRIDGES, "camera_pod_19": _BRIDGES}


# --- geometry -------------------------------------------------------------------------------
def _yz(sk, x0: float, x1: float) -> Part:
    """Extrude a sketch drawn in (Y, Z) from x0 to x1."""
    return extrude(Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * sk, amount=x1 - x0, dir=(1, 0, 0))


def _mirror(part: Part) -> Part:
    return part.mirror(Plane.YZ)


def _both(part: Part) -> Part:
    return part + _mirror(part)


def _side(x_cheek: float) -> Part:
    """C-channel round the right front-tip standoff, webbed back to the cheek on its inboard side."""
    cx, cy = FRONT_TIP_XY
    chan = c_clip((cx, cy), CHANNEL_Z0, CHANNEL_TOP - CHANNEL_Z0, opening_deg=MOUTH_DEG,
                  bore_d=D_CLIP_BORE, wall=CHANNEL_WALL, snap=SNAP)
    plan = Polygon((x_cheek, WEB_Y0), (WEB_X, WEB_Y0 + WEB_CH), (WEB_X, WEB_FLARE[1]),
                   (WEB_FLARE[0], WEB_Y1), (x_cheek, WEB_Y1), align=None)
    web = extrude(Plane.XY.offset(CHANNEL_Z0) * plan, amount=CHANNEL_TOP - CHANNEL_Z0)
    return (chan + web) - cylinder(cx, cy, CHANNEL_Z0 - 1, CHANNEL_TOP + 1, D_CLIP_BORE)


def _nubs() -> Part:
    return _both(box(NUB_X - NUB_XW / 2, NUB_Y0, NUB_Z0, NUB_X + NUB_XW / 2, NUB_Y0 + NUB_YL, Z_MID_TOP))


def _cheek_cuts(x_out: float) -> Part:
    """Diamond lightening window, pivot hole and the tilt arc slot, cut through both cheeks."""
    dy, dz = DIAMOND_YL / 2, DIAMOND_ZL / 2
    diamond = Polygon((DIAMOND_Y - dy, DIAMOND_Z), (DIAMOND_Y, DIAMOND_Z + dz),
                      (DIAMOND_Y + dy, DIAMOND_Z), (DIAMOND_Y, DIAMOND_Z - dz), align=None)
    pivot = Pos(PIVOT_Y, PIVOT_Z) * Circle(D_M2_THRU / 2)
    a0, a1 = 180 + TILT_RANGE[0] - TILT_MARGIN, 180 + TILT_RANGE[1] + TILT_MARGIN
    arc = Edge.make_circle(SLOT_R, Plane.XY, start_angle=a0, end_angle=a1)
    slot = Pos(PIVOT_Y, PIVOT_Z) * SlotArc(arc=arc, height=SLOT_W)
    return _yz(diamond + pivot + slot, -x_out, x_out)  # never wider than the cheeks: the backplate
    # reaches x 15.75 and a cut past x_out would leave a 1 mm sliver outboard of it


def _pod(cam_w: float) -> Part:
    x_in = cam_w / 2 + FIT
    x_out = x_in + CHEEK

    floor = _both(box(x_in, FLOOR_Y0, Z_MID_TOP, x_out, FLOOR_Y1, FLOOR_Z1))
    floor += box(-x_out, FLOOR_Y0, Z_MID_TOP, x_out, CB_REAR_Y1, FLOOR_Z1)
    floor += box(-x_out, CB_FRONT_Y0, Z_MID_TOP, x_out, FLOOR_Y1, FLOOR_Z1)

    # backplate: deep outboard of the camera, shallow and then open where the camera tilts back
    cx = x_in + CAM_PAD
    wall = box(-WALL_X, FLOOR_Y0, Z_MID_TOP, WALL_X, WALL_DEEP, CHEEK_TOP)
    wall -= box(-cx, WALL_SHALLOW, Z_MID_TOP - 1, cx, WALL_DEEP + 1, CHEEK_TOP + 1)
    wall -= box(-cx, FLOOR_Y0 - 1, WIN_Z0, cx, WALL_DEEP + 1, CHEEK_TOP + 1)

    cheeks = _both(box(x_in, CHEEK_Y0, Z_MID_TOP, x_out, CHEEK_Y1, CHEEK_TOP))

    post_prof = Polygon((POST_Y0, Z_MID_TOP), (POST_Y1, Z_MID_TOP), (POST_Y1, POST_TOP),
                        (POST_RAMP_Y, POST_TOP), (POST_Y0, CHEEK_TOP), align=None)
    posts = _both(_yz(post_prof, x_in, x_out))

    pod = floor + wall + cheeks + posts + _both(_side(x_out)) + _nubs()

    if CHIN:
        y_low = CHIN_Y0 + CHIN_CHAMFER * (Z_MID_TOP - CHIN_Z0)
        chin_prof = Polygon((CHIN_Y0, CHIN_Z1), (CHIN_Y0, Z_MID_TOP), (y_low, CHIN_Z0),
                            (CHIN_Y1, CHIN_Z0), (CHIN_Y1, CHIN_Z1), align=None)
        pod += _yz(chin_prof, -x_out, x_out)

    pod -= _cheek_cuts(x_out)
    assert len(pod.solids()) == 1, f"camera_pod {cam_w}: {len(pod.solids())} solids"
    return pod


def build(**overrides) -> dict[str, Part]:
    for k, v in overrides.items():
        globals()[k] = v
    return {f"camera_pod_{int(w)}": _pod(w) for w in (21.0, 19.0)}


# --- checks ---------------------------------------------------------------------------------
def _cheeks_only(cam_w: float) -> Part:
    """Just the two cheeks (with their cuts): what an M2 side screw has to pass through."""
    x_in = cam_w / 2 + FIT
    x_out = x_in + CHEEK
    return _both(box(x_in, CHEEK_Y0, Z_MID_TOP, x_out, CHEEK_Y1, CHEEK_TOP)) - _cheek_cuts(x_out)


def _screw_probe(tilt: float) -> Part:
    """Ø2.4 x 30 along X through the camera's second side-screw hole at this tilt."""
    from math import cos, radians, sin
    y = PIVOT_Y - SLOT_R * cos(radians(tilt))
    z = PIVOT_Z - SLOT_R * sin(radians(tilt))
    return _yz(Pos(y, z) * Circle(D_M2_THRU / 2), -15, 15)


def _neighbours() -> tuple[Part | None, list[str]]:
    """Union of the accessories that live in front of the lens, when their modules build."""
    part, seen = None, []
    for mod_name in ("front_bumper", "gopro_mount", "gps_mount"):
        try:
            mod = __import__(f"tigerbee.accessories.{mod_name}", fromlist=["build"])
            for label, other in mod.build().items():
                part = deepcopy(other) if part is None else part + other
                seen.append(label)
        except Exception as exc:  # noqa: BLE001 - a sibling module may be missing or mid-edit
            seen.append(f"{mod_name}: unavailable ({type(exc).__name__})")
    return part, seen


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    out = []
    nbr, nbr_seen = _neighbours()
    fc = frame_compound()
    plate_mid = frame["plate_mid"]

    for label, pod in parts.items():
        cam_w = float(label.rsplit("_", 1)[1])
        x_in, x_out = cam_w / 2 + FIT, cam_w / 2 + FIT + CHEEK

        hits = interference(pod)
        out.append((f"{label}: no frame interference", not hits, f"{hits or 'none'}"))

        for side, sx in (("right", 1.0), ("left", -1.0)):
            xy = (sx * FRONT_TIP_XY[0], FRONT_TIP_XY[1])
            ok, detail = coaxial(pod, xy, D_CLIP_BORE, Z_MID_TOP + 0.5, CHANNEL_TOP - 0.5)
            out.append((f"{label}: {side} channel bore coaxial with standoff_front_tip_{side}", ok, detail))
            probe = cylinder(*xy, Z_MID_TOP + 0.2, CHANNEL_TOP, STANDOFF_D)
            gap = round(pod.distance_to(probe), 4)
            out.append((f"{label}: {side} channel {STANDOFF_FIT} from the Ø{STANDOFF_D} standoff",
                        abs(gap - STANDOFF_FIT) <= 0.05 and isect(pod, probe) < EPS, f"gap {gap} mm"))

        worst = max((round(isect(Pos(0, d, 0) * pod, fc), 3), d) for d in range(0, 31))
        out.append((f"{label}: slides off forwards (0-30 mm in +Y) without touching the frame",
                    worst[0] < EPS, f"worst {worst[0]} mm³ at +{worst[1]} mm"))

        contact = seated(pod, Z_MID_TOP)
        out.append((f"{label}: rails seated on plate_mid at Z 9.000", contact >= 150.0, f"{contact} mm² contact"))

        nubs = _nubs()
        v, d = isect(nubs, plate_mid), round(nubs.distance_to(plate_mid), 3)
        out.append((f"{label}: nose nubs free in the V-notches", v < EPS and d >= 0.2, f"{v:.3f} mm³, gap {d} mm"))

        heads = _both(cylinder(15.25, 76.75, Z_MID_TOP, Z_MID_TOP + 3.0, D_M3_HEAD))
        v = isect(pod, heads)
        out.append((f"{label}: clears the fwd_30p5 M3 heads at (±15.25, 76.75)", v < EPS, f"{v:.3f} mm³"))
        board = box(-18, 43.5, Z_MID_TOP, 18, 79.5, Z_MID_TOP + 8)
        v = isect(pod, board)
        out.append((f"{label}: clears a 36 x 36 x 8 board at (0, 61.5)", v < EPS, f"{v:.3f} mm³"))

        v = isect(pod, tilt_sweep(cam_w, 0, 40))
        out.append((f"{label}: clear of the camera tilt sweep 0-40°", v < EPS, f"{v:.3f} mm³"))
        bad_pod, bad_frame = [], []
        for a in (0, 10, 20, 30, 40):
            env = camera_envelope(cam_w, CAM_H, CAM_D, tilt_deg=a)
            if isect(pod, env) > EPS:
                bad_pod.append(f"{a}°: {isect(pod, env):.2f}")
            hit = interference(env)
            if hit:
                bad_frame.append(f"{a}°: {hit}")
        out.append((f"{label}: camera envelope 0/10/20/30/40° clear of the pod", not bad_pod, "; ".join(bad_pod) or "0 mm³"))
        out.append((f"{label}: camera envelope 0/10/20/30/40° clear of the frame", not bad_frame,
                    "; ".join(bad_frame) or "none"))

        cheeks = _cheeks_only(cam_w)
        inside = {t: round(isect(_screw_probe(t), cheeks), 3) for t in (15, 20, 30, 40)}
        outside = {t: round(isect(_screw_probe(t), cheeks), 3) for t in (10, 45)}
        out.append((f"{label}: M2 screw runs free over the {TILT_RANGE[0]}-{TILT_RANGE[1]}° slot",
                    all(v < EPS for v in inside.values()), f"{inside}"))
        out.append((f"{label}: slot ends stop the screw outside the range", all(v > EPS for v in outside.values()),
                    f"{outside}"))

        targets = pod if nbr is None else pod + nbr
        fov = {t: round(isect(targets, fov_wedge(t, cam_w)), 3) for t in (15, 20, 30, 40)}
        out.append((f"{label}: nothing in the camera FOV at 15/20/30/40°", all(v < EPS for v in fov.values()),
                    f"{fov}; against {', '.join(nbr_seen) or 'pod only'}"))

        chan = pod & _both(cylinder(*FRONT_TIP_XY, 0, 60, D_CLIP_BORE + 2 * CHANNEL_WALL + 0.2))
        z_chan = chan.bounding_box().max.Z
        low = pod & box(-x_out, CHEEK_Y0, 0, x_out, POST_Y0, 60)
        z_low = low.bounding_box().max.Z
        z_max = pod.bounding_box().max.Z
        out.append((f"{label}: channels ≤ {CHANNEL_TOP}, cheeks ≤ {CHEEK_TOP} behind y {POST_Y0}, top ≤ {POST_TOP}",
                    z_chan <= CHANNEL_TOP + 1e-6 and z_low <= CHEEK_TOP + 1e-6 and z_max <= POST_TOP + 1e-6,
                    f"channel {z_chan:.3f}, cheek {z_low:.3f}, max {z_max:.3f}"))

        v = prop_disc_violation(pod)
        out.append((f"{label}: outside the prop keep-out discs", v < EPS, f"{v:.3f} mm³"))
        v = isect(pod, BATTERY)
        out.append((f"{label}: outside the battery envelope", v < EPS, f"{v:.3f} mm³"))
        ok, detail = single_solid(pod)
        out.append((f"{label}: one solid", ok, detail))

        bed = sum(f.area for f in pod.faces() if f.geom_type == GeomType.PLANE
                  and f.normal_at().Y < -0.999 and abs(f.center().Y - FLOOR_Y0) < 1e-3)
        out.append((f"{label}: bed face at y {FLOOR_Y0} ≥ 500 mm²", bed >= 500.0, f"{bed:.1f} mm²"))
        over = overhangs(pod, PRINT[label], bridge_ok=BRIDGE_OK[label], material=MATERIAL)
        out.append((f"{label}: prints on its back without supports", not over, "; ".join(over) or "none"))
        ok, _v, detail = min_wall(pod, WALL)
        out.append((f"{label}: min wall ≥ {WALL}", ok, detail))
        vol = pod.volume / 1000.0
        out.append((f"{label}: volume 12-24 cm³", 12.0 <= vol <= 24.0, f"{vol:.2f} cm³"))

    a, b = (parts["camera_pod_21"].bounding_box(), parts["camera_pod_19"].bounding_box())
    same = max(abs(a.min.Y - b.min.Y), abs(a.max.Y - b.max.Y), abs(a.min.Z - b.min.Z), abs(a.max.Z - b.max.Z))
    out.append(("both widths share the same Y/Z envelope", same < 0.01, f"Δ {same:.4f} mm, X {a.size.X} vs {b.size.X}"))
    return out
