"""Accessory registry: every module in this package whose name does not start with "_" is an
accessory and must follow the contract documented in `_template.py`.

    from tigerbee.accessories import discover_accessories, build_accessory, run_checks
    mods = discover_accessories()                     # {"camera_pod": <module>, ...}
    parts = build_accessory(mods["camera_pod"])       # {"camera_pod_21": Part, ...} installed
    results = run_checks(mods["camera_pod"], parts)   # [(name, passed, detail), ...]
"""

import importlib
import pkgutil
from types import ModuleType

from build123d import Part

from tigerbee.accessories import _fit as F

REQUIRED = ("NAME", "TITLE", "MATERIAL", "build", "checks")
OPTIONAL_DEFAULTS = {
    "PRINT": {},  # label -> bed normal (frame coords); missing labels print on their -Z face
    "EXCLUSIVE": (),  # accessory ids that cannot be installed together with this one
    "NOTES": "",  # mounting notes for the manifest (str, or {label: str})
    "MIN_Z": F.LANDING_Z,  # landing plane: lowest allowed Z of any part
    "ALLOWED_INTERFERENCE": {},  # label -> {frame_part: max mm^3} for intended press fits
    "OWN_PROP_DISC": {},  # label -> motor name whose disc the part may enter below OWN_DISC_Z_MAX
    "BATTERY_OK": False,  # True only for the battery pad (it lives inside the BATTERY envelope)
    "BRIDGE_OK": {},  # label -> tuple of ('box', x0, y0, z0, x1, y1, z1) in PRINT coords, see overhangs()
    "OVERHANG_SKIP": (),  # labels excluded from the generic overhang check (justify in NOTES)
    "ASSEMBLY_BUILD": {},  # build(**kwargs) used for the combined tigerbee_with_accessories assembly
}


def attr(mod: ModuleType, name: str):
    return getattr(mod, name, OPTIONAL_DEFAULTS[name])


def validate(mod: ModuleType) -> None:
    missing = [a for a in REQUIRED if not hasattr(mod, a)]
    assert not missing, f"{mod.__name__}: missing {missing}"
    assert mod.NAME == mod.__name__.rsplit(".", 1)[-1], f"{mod.__name__}: NAME must equal the module name"
    assert mod.MATERIAL in ("TPU95A", "PETG"), f"{mod.__name__}: MATERIAL {mod.MATERIAL!r}"


def discover_accessories(only: list[str] | None = None) -> dict[str, ModuleType]:
    """Import every public module of this package (or just `only`), validate the contract, key by NAME.
    With `only`, other modules are never imported, so a sibling's work in progress cannot break yours."""
    names = sorted(i.name for i in pkgutil.iter_modules(__path__) if not i.name.startswith("_"))
    if only:
        unknown = [n for n in only if n not in names]
        assert not unknown, f"unknown accessories {unknown}; available: {names}"
        names = [n for n in names if n in only]
    mods = {}
    for name in names:
        mod = importlib.import_module(f"{__name__}.{name}")
        validate(mod)
        mods[mod.NAME] = mod
    return mods


def build_accessory(mod: ModuleType, **overrides) -> dict[str, Part]:
    parts = mod.build(**overrides)
    assert isinstance(parts, dict) and parts, f"{mod.NAME}.build() must return a non-empty dict"
    for label, part in parts.items():
        assert isinstance(label, str) and isinstance(part, Part), f"{mod.NAME}: {label!r} -> {type(part)}"
        part.label = label
    return parts


def printed(mod: ModuleType, label: str, part: Part) -> Part:
    """Part re-oriented for printing (module hook orient_for_print(label, part), else PRINT[label],
    else the -Z face on the bed)."""
    from tigerbee.accessories._common import print_orientation
    if hasattr(mod, "orient_for_print"):
        p = mod.orient_for_print(label, part)
    else:
        p = print_orientation(part, attr(mod, "PRINT").get(label, (0, 0, -1)))
    p.label = label
    return p


def generic_checks(mod: ModuleType, parts: dict[str, Part]) -> list[tuple[str, bool, str]]:
    """Checks every accessory must pass, independent of its spec."""
    from tigerbee.accessories._common import BATTERY, overhangs
    out = []
    allowed = attr(mod, "ALLOWED_INTERFERENCE")
    own = attr(mod, "OWN_PROP_DISC")
    min_z = attr(mod, "MIN_Z")
    for label, part in parts.items():
        ok, detail = F.single_solid(part)
        out.append((f"{label}: one valid solid", ok, detail))
        hits = F.interference(part)
        bad = [(n, v) for n, v in hits if v > allowed.get(label, {}).get(n, 0.0)]
        out.append((f"{label}: no interference with the frame", not bad, f"overlaps {hits or 'none'}"))
        so = F.standoff_interference(part)
        out.append((f"{label}: clear of the Ø{F.STANDOFF_D} standoffs", not so, f"overlaps {so or 'none'}"))
        gaps = {n: d for n, d in F.distance_to_frame(part, near=1.0).items() if n.startswith("standoff")}
        close = {n: d for n, d in gaps.items() if d < F.STANDOFF_FIT - 0.05}
        out.append((f"{label}: >= {F.STANDOFF_FIT - 0.05} mm to every Ø{F.STANDOFF_D} standoff", not close, f"gaps {gaps or 'none nearby'}"))
        v = F.prop_disc_violation(part, exclude=(own.get(label),) if label in own else ())
        v_own = F.prop_disc_violation(part, z0=F.OWN_DISC_Z_MAX) if label in own else 0.0
        out.append((f"{label}: outside the prop keep-out discs above Z {F.PROP_Z0}", v + v_own < F.EPS,
                    f"{v:.3f} mm³ in neighbouring discs, {v_own:.3f} mm³ in own disc above Z {F.OWN_DISC_Z_MAX}"))
        bb = part.bounding_box()
        out.append((f"{label}: above the landing plane Z {min_z}", bb.min.Z >= min_z - 1e-6, f"min Z {bb.min.Z:.3f}"))
        if not attr(mod, "BATTERY_OK"):
            vb = F.isect(part, BATTERY)
            out.append((f"{label}: outside the battery envelope", vb < F.EPS, f"{vb:.3f} mm³"))
        p = printed(mod, label, part)
        pb = p.bounding_box()
        bed = [f for f in p.faces() if f.geom_type.name == "PLANE" and abs(f.center().Z) < 1e-3 and f.normal_at().Z < -0.999]
        bed_area = sum(f.area for f in bed)
        out.append((f"{label}: prints on a flat face at Z 0", abs(pb.min.Z) < 1e-6 and bed_area >= 5.0,
                    f"bed contact {bed_area:.1f} mm², printed bbox {pb.size.X:.1f} x {pb.size.Y:.1f} x {pb.size.Z:.1f}"))
        if label not in attr(mod, "OVERHANG_SKIP"):
            normal = attr(mod, "PRINT").get(label, (0, 0, -1))
            over = overhangs(part, normal, bridge_ok=attr(mod, "BRIDGE_OK").get(label, ()), material=mod.MATERIAL)
            out.append((f"{label}: no unsupported overhangs in print orientation", not over, "; ".join(over) or "none"))
    return out


def run_checks(mod: ModuleType, parts: dict[str, Part]) -> list[tuple[str, bool, str]]:
    """Generic checks followed by the module's own checks(parts, frame)."""
    results = generic_checks(mod, parts)
    for row in mod.checks(parts, F.frame_parts()):
        name, ok, detail = row
        results.append((name, bool(ok), str(detail)))
    return results


def __getattr__(name):
    if name == "CATALOG":
        return list(discover_accessories().values())
    raise AttributeError(name)
