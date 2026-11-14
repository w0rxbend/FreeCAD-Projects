"""Vektor's printed parts. Every module exposes build() -> list[Accessory]."""

import importlib
from functools import lru_cache

from vektor.accessories.base import Accessory, check  # noqa: F401
from vektor.checks import overlap

MODULES = (
    "tail_trident",
    "camera_pod",
    "side_fairing",
    "motor_guard",
    "foot",
    "battery_pad",
    "gps_mount",
    "gopro_mount",
    "wire_grommet",
)


@lru_cache(maxsize=1)
def build_all() -> tuple:
    out = []
    for m in MODULES:
        for acc in importlib.import_module(f"vektor.accessories.{m}").build():
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
