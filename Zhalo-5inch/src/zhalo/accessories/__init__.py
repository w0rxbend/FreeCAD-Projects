"""TPU accessories. Every module here (except `kit`) exposes `build() -> list[Accessory]`.

from zhalo import accessories
for acc in accessories.build_all():
    print(acc.name, accessories.check(acc))
"""

import importlib
from functools import lru_cache

from zhalo import checks as C
from zhalo import design, meshcheck
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo.accessories.kit import BED, WALL, Accessory, Row, lay_on_bed

MODULES = (
    "side_panel",
    "camera_mount",
    "nose_bumper",
    "arm_guard",
    "tail_mount",
    "gopro_mount",
    "gps_mount",
    "xt60_mount",
    "battery_pad",
    "cap_holder",
    "wire_clip",
    "brace_skid",
)
THIN = 0.9  # a wall the slicer would print as a single unsupported line


@lru_cache(maxsize=1)
def build_all() -> tuple[Accessory, ...]:
    out = []
    for name in MODULES:
        module = importlib.import_module(name if "." in name else f"zhalo.accessories.{name}")
        for acc in module.build():
            acc.module = name.rsplit(".", 1)[-1]
            acc.color = design.COLOR_OF.get(acc.name, acc.color)
            acc.part.label = acc.name
            out.append(acc)
    names = [a.name for a in out]
    assert len(names) == len(set(names)), f"duplicate accessory names: {names}"
    return tuple(out)


@lru_cache(maxsize=1)
def _obstacles() -> dict[str, object]:
    gear = E.build()
    out = {name: part for name, (part, _c, _o) in gear.items() if not name.startswith(("prop_", "camera"))}
    out["vtx_30p5"] = E._slab(E.VTX_LARGE_SIZE, E.VTX_Z, (0.0, P.VTX_BAY_Y))
    out["camera"] = E.camera_sweep()
    for name, xy in P.MOTORS.items():
        out[f"prop_{name}"] = E.prop_keepout(xy)
    return out


def check(acc: Accessory) -> list[Row]:
    """The checks every accessory has to pass, followed by its own."""
    part, rows = acc.part, []
    solids = len(part.solids())
    rows.append(("one valid solid", solids == 1 and part.is_valid, f"{solids} solid(s), {part.volume / 1000:.2f} cm3"))

    hits = {n: round(v, 2) for n, p in F.parts().items() if (v := C.overlap(part, p)) > C.EPS}
    rows.append(("does not cut into the frame", not hits, str(hits or "clear")))

    hits = {
        n: round(v, 2)
        for n, p in _obstacles().items()
        if not n.startswith(acc.holds) and (v := C.overlap(part, p)) > C.EPS
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
            f"{ceiling:.0f} mm2 of bridge (allowed {acc.ceilings:.0f}), {slope:.0f} mm2 of overhang "
            f"(allowed {acc.overhang:.0f})",
        )
    )

    share, thinnest = meshcheck.thin_walls(part, THIN)
    rows.append(
        (
            f"no walls under {THIN} mm",
            share <= 0.02,
            f"{share:.1%} of the surface, thinnest ray {thinnest:.2f} mm (walls are designed at {WALL} mm or more)",
        )
    )
    return rows + list(acc.checks)


def assembly() -> list[Accessory]:
    return [a for a in build_all() if a.in_assembly]
