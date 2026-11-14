"""Printed accessories for the Tiger Beetle 7". Every module here exposes `build() -> list[Accessory]`.

They use the print rules and building blocks of `zhalo.accessories.kit` (TPU 95A fits, snap rings,
wall sizes) and are checked the same way the other frames' parts are: one solid, nothing cut into
the frame, clear of the electronics and the props, a flat face on the bed, no supports, no walls
too thin to print.
"""

import importlib
from functools import lru_cache

from zhalo import meshcheck
from zhalo.accessories.kit import BED, Accessory, Row, lay_on_bed
from zhalo.checks import overlap

from tigerbeetle import equipment as E
from tigerbeetle import frame as F

MODULES = ("camera_mount", "side_panel", "arm_guard", "nose_bumper", "foot", "battery_pad", "gopro_mount", "crown")
THIN = 0.9
EPS = 1e-3


@lru_cache(maxsize=1)
def build_all() -> tuple[Accessory, ...]:
    out = []
    for name in MODULES:
        module = importlib.import_module(f"tigerbeetle.accessories.{name}")
        for acc in module.build():
            acc.module = name
            acc.part.label = acc.name
            out.append(acc)
    names = [a.name for a in out]
    assert len(names) == len(set(names)), names
    return tuple(out)


@lru_cache(maxsize=1)
def obstacles() -> dict:
    out = {n: p for n, (p, _c, _o) in E.build().items() if not n.startswith(("prop_", "camera"))}
    out["camera"] = E.camera_sweep()
    for name, xy in F.motors().items():
        out[f"prop_{name}"] = E.prop_keepout(xy)
    return out


def check(acc: Accessory) -> list[Row]:
    part, rows = acc.part, []
    n = len(part.solids())
    rows.append(("one valid solid", n == 1 and part.is_valid, f"{n} solid(s), {part.volume / 1000:.2f} cm3"))
    placed = (part, *acc.instances)
    hits = {name: round(v, 2) for p in placed for name, fp in F.parts().items() if (v := overlap(p, fp)) > EPS}
    rows.append(("does not cut into the frame", not hits, str(hits or "clear")))
    hits = {
        name: round(v, 2)
        for p in placed
        for name, o in obstacles().items()
        if not name.startswith(acc.holds) and (v := overlap(p, o)) > EPS
    }
    rows.append(("clear of electronics, motors and prop discs", not hits, str(hits or "clear")))
    printed = lay_on_bed(part, acc.bed)
    bb = printed.bounding_box()
    contact = sum(
        f.area
        for f in printed.faces()
        if f.geom_type.name == "PLANE" and abs(f.center().Z) < 1e-4 and f.normal_at().Z < -0.999
    )
    rows.append(("rests on a flat face", contact >= 20.0, f"{contact:.0f} mm2 on the bed"))
    rows.append(
        (
            f"fits a {BED:.0f} mm bed",
            max(bb.size.X, bb.size.Y) <= BED,
            f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm",
        )
    )
    ceiling, slope = meshcheck.overhangs(printed)
    rows.append(
        (
            "prints without supports",
            ceiling <= acc.ceilings + 3.0 and slope <= acc.overhang + 3.0,
            f"{ceiling:.0f} mm2 of bridge (allowed {acc.ceilings:.0f}), "
            f"{slope:.0f} mm2 of overhang (allowed {acc.overhang:.0f})",
        )
    )
    share, thinnest = meshcheck.thin_walls(part, THIN)
    rows.append(
        (f"no walls under {THIN} mm", share <= 0.02, f"{share:.1%} of the surface, thinnest ray {thinnest:.2f} mm")
    )
    return rows + list(acc.checks)


def assembly() -> list[Accessory]:
    return [a for a in build_all() if a.in_assembly]


def clashes() -> list:
    placed = []
    for a in assembly():
        placed += [(a.name if i == 0 else f"{a.name}#{i + 1}", p) for i, p in enumerate((a.part, *a.instances))]
    out = []
    for i, (na, pa) in enumerate(placed):
        for nb, pb in placed[i + 1 :]:
            if (v := overlap(pa, pb)) > EPS:
                out.append([na, nb, round(v, 3)])
    return out
