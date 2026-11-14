"""Bolid's printed parts. Every module exposes build() -> list[Accessory]."""

import importlib
from functools import lru_cache

from bolid.accessories.base import Accessory, check  # noqa: F401
from bolid.checks import overlap

MODULES = (
    "body_shell",
    "engine_cover",
    "tail_light",
    "rear_wing",
    "front_splitter",
    "arm_cover",
    "motor_skid",
    "battery_pad",
    "gopro_mount",
)


@lru_cache(maxsize=1)
def build_all() -> tuple:
    out = []
    for m in MODULES:
        for acc in importlib.import_module(f"bolid.accessories.{m}").build():
            acc.part.label = acc.name
            out.append(acc)
    return tuple(out)


def assembly() -> list:
    return [a for a in build_all() if a.in_assembly]


def clashes() -> list:
    placed = []
    for a in assembly():
        placed += [(a.name if i == 0 else f"{a.name}#{i + 1}", p) for i, p in enumerate((a.part, *a.instances))]
    return [
        [na, nb, round(v, 2)]
        for i, (na, pa) in enumerate(placed)
        for nb, pb in placed[i + 1 :]
        if (v := overlap(pa, pb)) > 1e-3
    ]
