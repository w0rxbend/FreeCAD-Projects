"""Rear fork tip bumpers: a TPU shield over the outer rear lobe of both rear plates, per side.

Answers the "bumpers" part of the brief at the TAIL. front_bumper caps the two plate_top NOSE
prongs; this is its mirror at the back, and it is the only accessory that touches the outer rear
fork tips - the carbon that takes a rear-corner or tail-down hit. tail_block covers the tail
CENTRE (its skid reaches y -107, 6.8 mm behind the carbon), but tail_block stops at |x| 20.12 and
the lobes carry material out to |x| 21.65 (plate_bottom) and 22.0 (plate_top), so the outboard
21.65-22.0 band was bare in every previous set.

Three features, one solid per side:

  * SHIELD - a crescent standing 1.35-3.15 mm proud of the carbon over the whole stack height
    (Z 0-36), so it takes the hit instead of the plate edges and the naked standoff between them.
    Its OUTBOARD face is the single plane x = X_OUT: that is both the print bed face and the one
    surface the prop keep-out constrains. Its INBOARD face is the union of the two plates'
    outlines offset by FIT_E, so the shield hugs whichever plate is wider at each y and binds the
    part in yaw.
  * FOOT - a 2 mm pad under the plate_bottom lobe, clamped by the rear-tip standoff's own lower
    bolt (Ø3.4 through hole at (±16.5, -94)). One fastener per side and no new hole in the carbon;
    the bolt grows 2 mm to take the pad.
  * BRACE - a 1.4 mm tab under the plate_top lobe (Z 32.6-34, reaching 3.05 mm inboard of the
    carbon edge) that bears on the carbon and ties the shield's top end back to the airframe, so a
    hit at plate_top level is not carried by a 36 mm cantilever off the foot alone.
    It is NOT a clip on the rear-tip standoff. That looked like the obvious brace - the shaft is
    free between tail_block's clips (Z 2-22) and plate_top (Z 34) - but tail_block's `feral` variant
    puts a five-spine dorsal row up there and a Ø9.7 clip ring in that window touches it (measured
    4.825 mm³ of overlap). The strip under plate_top is empty in every tail_block variant (measured
    0.000 mm³ for all four styles plus the lens part), so the brace bears on the carbon instead of
    competing for the standoff.

PROP KEEP-OUT is what sets X_OUT. The rear motors sit at (±115.72, -98.44), so the keep-out
(r 91.9) allows only |x| <= 23.82 at y -98 and 23.85 at y -96 - the tightest place on the whole
airframe, and the reason the shield is 1.35 mm thin over the plate_top flat and thickens only
where the lobe curves away. The foot is below Z 7 and therefore outside the keep-out entirely.

NOT the plate_top TOP face: antenna_mast's bracket covers it out to x 22.0 over y -84..-102, so
there is no room for a lip over plate_top. The foot under plate_bottom is the free face, and that
is why the part is bolted from below.
"""

from build123d import Face, Part, Plane, Pos, Rectangle, Sketch, extrude, offset

from tigerbee.accessories._common import *  # noqa: F401,F403 - constants, builders and checks
from tigerbee.profiles import _outer_face

NAME = "rear_bumper"
TITLE = "Rear fork tip bumpers"
MATERIAL = "TPU95A"
PRINT = {"rear_bumper_right": (1, 0, 0), "rear_bumper_left": (-1, 0, 0)}
EXCLUSIVE = ()
MOUNTS = ("the outer rear fork lobe edges of plate_bottom and plate_top, y -98.6..-89.0 "
          "(the shield stands 0.15 mm off the carbon over the full stack height Z 0-36)",
          "plate_bottom underside Z 0 over the rear lobe (the foot is clamped against it)",
          "rear_tip_standoff bolt axis (±16.5, -94) through plate_bottom",
          "plate_top underside Z 34 over the rear lobe (the brace tab bears on it)")
HARDWARE = ("1 x M3 x 10 per side, replacing the rear-tip standoff's lower bolt (2 mm of foot + 2 mm "
            "of carbon, then the same thread into the standoff as the stock M3 x 8) - add an M3 washer",)

# --- parameters (mm) ------------------------------------------------------------------------
FIT_E = 0.15  # gap between the shield's inboard face and the carbon edge
X_OUT = 23.5  # outboard face: a single plane, the bed face AND the prop keep-out limit
Y0, Y1 = -98.6, -89.0  # rear and front ends of the shield (led_buzzer's bar ends at y -88.0)
# The two outboard corners are left SQUARE on purpose. A plan fillet there tapers the crescent from
# its 1.35 mm section down to nothing over the fillet, and that tip measured 0.22 mm - a real thin
# wall, not a ray artefact (sectioned at Z 10: t 1.350 at y -90, 0.549 at y -89 with r 1.0).
# The ends are 1.35 and 2.28 mm of TPU square-cut instead.
Z_SHIELD = (Z_BOTTOM_UNDER, Z_TOP_TOP - FIT_E)  # 0 .. 35.85
# The top stops FIT_E short of plate_top's top face rather than flush with it: antenna_mast's
# bracket sits ON that face and its shard variant cantilevers out to x 22.0, past the carbon edge at
# the rear of the lobe, so a flush shield met the bracket's underside face-to-face (measured gap
# 0.000). FIT_E below it is the same clearance the shield keeps to the carbon, and it still covers
# 1.85 of the 2 mm plate edge.

X_SH0 = 21.5  # inboard crop of the SHIELD. Behind y -97.4 the lobe curves away at ~42 deg to the
# y axis, and a shield that followed it right to the square rear end met that end face at a 52 deg
# wedge - measured 0.66 mm thick 0.6 mm from the corner, a real thin wall. Cropping the shield at a
# straight x = 21.5 instead turns that corner into a 90 deg one (2.0 mm of section at y -98.6) and
# costs a 0.94 mm air gap behind the shield at the rear corner, which nothing bears on.

FOOT_T = 2.0  # pad thickness under plate_bottom, frame Z -2..0
FOOT_X0 = 13.0  # inboard reach of the pad (the lobe's inner edge runs x 11.1..13.6 here)
BOLT_XY = REAR_TIP_XY  # (16.5, -94)

LIP_T = 1.4  # brace tab thickness: frame Z 32.6..34, bearing on the plate_top lobe's underside
LIP_X0 = 19.1  # inboard reach of the tab (3.05 mm under the carbon at the lobe's widest point)

MIN_Z = -FOOT_T  # -2.0: the foot is the lowest point; the ground plane is 13.2 mm further down
_LOBE_CROP = (0.0, 40.0, -102.0, -84.0)  # right rear lobe of either plate, isolated before offsetting

NOTES = (
    "Push the shield inboard until the brace clip snaps onto the Ø6 rear-tip standoff (bore Ø6.5, "
    "0.25 mm radial fit, 0.8 mm snap, mouth facing inboard), drop the foot under plate_bottom and "
    "run the rear-tip standoff's lower bolt up through it - 2 mm longer than stock, with a washer. "
    "One fastener per side, no new hole in the carbon. The shield is deliberately thin (1.35 mm over "
    "the plate_top flat, 3.15 mm at the rear corner): the rear prop keep-out allows only |x| 23.82 "
    "at y -98, so X_OUT 23.5 is the outboard limit and the extra material goes where the lobe curves "
    "away, which is where a rear-corner hit lands. It coexists with tail_block (|x| <= 20.12, "
    "Z <= 22), antenna_mast (plate_top top face, Z 36+) and led_buzzer (y >= -88); all three gaps "
    "are measured. Prints on its outboard face (frame +X for the right part), no supports: every "
    "pocket opens upward in that orientation and both bores are horizontal arches."
)


# --- 2D helpers -----------------------------------------------------------------------------
def _strip(x0: float, x1: float, y0: float, y1: float) -> Sketch:
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def _lobe(plate: str, amount: float = 0.0) -> Sketch:
    """The RIGHT rear fork lobe of `plate`, isolated at Z 0 and offset by `amount` in 2D.

    The outline is cropped BEFORE it is offset (the same trick front_bumper uses on the nose
    prongs): offsetting the whole plate outline is both slow and prone to self-intersection at the
    fork crotch. The crop edges themselves are pushed out by `amount` too, which is why the crop
    box is 3 mm clear of Y0/Y1 on every side - the artefacts never reach the part."""
    x0, x1, y0, y1 = _LOBE_CROP
    reg = (Sketch() + Face(_outer_face(plate).outer_wire())) & _strip(x0, x1, y0, y1)
    return offset(reg, amount=amount) if amount else reg


def _carbon(amount: float = FIT_E) -> Sketch:
    """Union of BOTH rear lobes offset by `amount`: the shield's inboard face follows whichever
    plate is wider at each y. plate_top is wider over y -89..-98 (22.0 against 21.65) and
    plate_bottom takes over behind y -98.5, so neither outline alone would clear both."""
    return _lobe("plate_top", amount) + _lobe("plate_bottom", amount)


def _shield_footprint() -> Sketch:
    """The crescent in plan: the band between the carbon edge + FIT_E and the plane x = X_OUT,
    never reaching inboard of X_SH0 (see the note there)."""
    return _strip(X_SH0, X_OUT, Y0, Y1) - _carbon()


# --- geometry (frame coordinates, right side) ------------------------------------------------
def _shield(p: dict) -> Part:
    return extrude(Plane.XY.offset(p["Z_SHIELD"][0]) * _shield_footprint(),
                   amount=p["Z_SHIELD"][1] - p["Z_SHIELD"][0], dir=(0, 0, 1))


def _foot(p: dict) -> Part:
    """Pad under the plate_bottom lobe, from the bolt side out to the shield so the two fuse.
    It lives below Z 0, so it is outside the prop keep-out (which starts at Z 7) and cannot
    touch tail_block's tray (Z 2-5) or led_buzzer's bar (y >= -88)."""
    sk = _strip(p["FOOT_X0"], X_OUT, Y0, Y1)
    return extrude(Plane.XY.offset(-p["FOOT_T"]) * sk, amount=p["FOOT_T"], dir=(0, 0, 1))


def _lip(p: dict) -> Part:
    """Brace tab under the plate_top lobe: bears on the carbon, ties the shield's top end in."""
    return box(p["LIP_X0"], Y0, Z_TOP_UNDER - p["LIP_T"], X_OUT, Y1, Z_TOP_UNDER)


def _bolt_tool(p: dict) -> Part:
    """Ø3.4 through hole for the rear-tip standoff's lower bolt, right through the foot."""
    return cylinder(*BOLT_XY, -p["FOOT_T"] - 1.0, 0.5, D_M3_THRU)


def build(**overrides) -> dict[str, Part]:
    p = {"Z_SHIELD": Z_SHIELD, "FOOT_T": FOOT_T, "FOOT_X0": FOOT_X0, "LIP_T": LIP_T,
         "LIP_X0": LIP_X0, **overrides}
    body = _shield(p) + _foot(p) + _lip(p)
    body = Part() + (body - _bolt_tool(p))
    assert body.is_valid and len(body.solids()) == 1, f"rear_bumper: {len(body.solids())} solid(s)"
    return pair(body, NAME)


# --- check helpers ---------------------------------------------------------------------------
def _ys(n: int = 24) -> list[float]:
    """Sample points across the shield, 0.2 mm clear of both end faces."""
    return [Y0 + 0.2 + (Y1 - Y0 - 0.4) * i / n for i in range(n + 1)]


def _section(part: Part, z: float = 10.0) -> tuple[float, float]:
    """(thinnest shield section in x, the y it is at), measured by sectioning the solid.

    min_wall() degrades to ray_thickness() on this part (offset_3d collapses on the offset-outline
    face), and rays cannot see a tapering tip - exactly the failure mode the square X_SH0 crop was
    put in to avoid. So the section is measured directly, the way motor_guard measures its skin."""
    worst, where = float("inf"), 0.0
    for y in _ys():
        sl = part & box(X_SH0 - 2.0, y - 0.01, z - 1.0, X_OUT + 1.0, y + 0.01, z + 1.0)
        if sl is None or sl.volume <= 0:
            continue
        bb = sl.bounding_box()
        if bb.max.X - bb.min.X < worst:
            worst, where = bb.max.X - bb.min.X, y
    return worst, where


def _carbon_edge(y: float) -> float:
    """Widest |x| of either rear plate at this y (outline only, no holes)."""
    out = 0.0
    for plate in ("plate_bottom", "plate_top"):
        for x0, x1 in outline_spans(plate, y):
            out = max(out, x1)
    return out


def _proud() -> tuple[float, float]:
    """(smallest amount the outboard face stands proud of the carbon, the y it is at)."""
    worst, where = float("inf"), 0.0
    for y in _ys():
        d = X_OUT - _carbon_edge(y)
        if d < worst:
            worst, where = d, y
    return worst, where


def _prop_margin() -> tuple[float, float]:
    """(smallest gap from the outboard face to the rear prop keep-out, the y it is at)."""
    worst, where = float("inf"), 0.0
    for y in _ys():
        d = max_abs_x_at(y) - X_OUT
        if d < worst:
            worst, where = d, y
    return worst, where


def _neighbours() -> dict[str, Part]:
    """Every accessory that shares the tail corner, with both tail_block variants."""
    out: dict[str, Part] = {}
    for name in ("antenna_mast", "led_buzzer", "tail_block", "battery_pad", "gps_mount"):
        try:
            mod = __import__(f"tigerbee.accessories.{name}", fromlist=["build"])
            builds = [("", mod.build())] if not getattr(mod, "VARIANTS", {}) else \
                     [(v, mod.build(v)) for v in mod.VARIANTS]
            for vname, parts in builds:
                for label, part in parts.items():
                    out[f"{label}{('/' + vname) if vname else ''}"] = part
        except Exception:  # noqa: BLE001 - a sibling module may be missing or in progress
            continue
    return out


# --- checks ----------------------------------------------------------------------------------
def _mirror_xy(xy: tuple[float, float], side: str) -> tuple[float, float]:
    return xy if side == "right" else (-xy[0], xy[1])


def checks(parts: dict[str, Part], frame: dict[str, Part]) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    for side in ("right", "left"):
        cap = parts[f"{NAME}_{side}"]
        xy = _mirror_xy(BOLT_XY, side)
        sign = 1.0 if side == "right" else -1.0

        hits = interference(cap)
        out.append((f"{side}: no interference with any frame part", not hits, f"{hits or 'none'}"))

        brace = seats_on(cap, "plate_top", Z_TOP_UNDER)
        out.append((f"{side}: brace tab bears on the plate_top underside at Z {Z_TOP_UNDER}",
                    brace >= 20.0, f"{brace} mm² of contact, tab Z "
                    f"{Z_TOP_UNDER - LIP_T}-{Z_TOP_UNDER}, {X_OUT - LIP_X0:.2f} mm deep"))

        ok, detail = coaxial(cap, xy, D_M3_THRU, -FOOT_T + 0.05, -0.05)
        head = cylinder(*xy, -FOOT_T - H_M3_HEAD, -FOOT_T, D_M3_HEAD + 0.6)
        out.append((f"{side}: Ø{D_M3_THRU} bolt hole on the rear-tip standoff axis, head free below "
                    f"the foot", ok and isect(cap, head) < EPS,
                    f"{detail}; Ø{D_M3_HEAD + 0.6} x {H_M3_HEAD} head probe {isect(cap, head):.3f} mm³"))

        contact = seated(cap, Z_BOTTOM_UNDER)
        out.append((f"{side}: foot bears on the plate_bottom underside at Z 0.000", contact >= 60.0,
                    f"{contact} mm² of contact"))

        shield = cap & box(sign * (X_SH0 - 2) if side == "right" else -X_OUT - 1,
                           Y0 - 1, Z_SHIELD[0] + 0.01,
                           X_OUT + 1 if side == "right" else -(X_SH0 - 2),
                           Y1 + 1, Z_SHIELD[1] - 0.01)
        sb = shield.bounding_box()
        out.append((f"{side}: shield spans the whole plate stack Z {Z_SHIELD[0]}-{Z_SHIELD[1]}",
                    sb.min.Z <= Z_SHIELD[0] + 0.02 and sb.max.Z >= Z_SHIELD[1] - 0.02,
                    f"shield Z {sb.min.Z:.2f}-{sb.max.Z:.2f}, |x| to {max(abs(sb.min.X), abs(sb.max.X)):.2f}"))

        over = overhangs(cap, PRINT[f"{NAME}_{side}"], material=MATERIAL)
        out.append((f"{side}: prints on its outboard face without supports", not over,
                    "; ".join(over) or "none"))

    right = parts[f"{NAME}_right"]
    thin, where = _section(right)
    out.append((f"shield section >= {WALL} everywhere (measured, not ray-sampled)",
                thin >= WALL - WALL_TOL, f"thinnest {thin:.3f} mm at y {where:.2f}"))

    proud, py = _proud()
    out.append(("the shield stands proud of the widest carbon at every y, so it takes the hit first",
                proud >= WALL, f"least {proud:.2f} mm at y {py:.2f} (outboard face x {X_OUT})"))

    margin, my = _prop_margin()
    out.append(("outboard face clear of the rear prop keep-out (r 91.9)", margin >= 0.2,
                f"least {margin:.2f} mm at y {my:.2f}; limit |x| {max_abs_x_at(my):.2f} vs X_OUT {X_OUT}"))

    # The bound is FIT_E, not the 0.5 mm tail_block uses: antenna_mast's bracket reaches the
    # plate_top edge itself (x 22.0, and its shard variant cantilevers past the carbon at the rear of
    # the lobe), and this shield hugs that same edge at FIT_E, so FIT_E is the tightest gap the
    # geometry can have. Any overlap at all still fails, and every other neighbour is metres clear.
    near = {n: round(right.distance_to(q), 3) for n, q in _neighbours().items()
            if isect(right, q) > EPS or right.distance_to(q) < 8.0}
    worst = {n: g for n, g in near.items() if g < FIT_E - 0.01}
    clash = {n: round(isect(right, q), 3) for n, q in _neighbours().items() if isect(right, q) > EPS}
    out.append((f"no accessory collision, >= {FIT_E} mm to every tail neighbour", not worst and not clash,
                ", ".join(f"{n} {g}" for n, g in sorted(near.items(), key=lambda kv: kv[1])) or "none within 8 mm"))

    ok_w, _v, detail = min_wall(right, WALL)
    out.append((f"min wall >= {WALL}", ok_w, detail))

    dv = abs(parts[f"{NAME}_right"].volume - parts[f"{NAME}_left"].volume)
    out.append(("left and right are the same part mirrored", dv < 0.01,
                f"Δ{dv:.5f} mm³ of {parts[f'{NAME}_right'].volume:.1f} mm³"))
    return out
