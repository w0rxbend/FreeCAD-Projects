"""Accessory registry: every module in this package whose name does not start with "_" is an
accessory and must follow the contract documented in `_template.py`.

    from tigerbee.accessories import discover_accessories, build_accessory, run_checks
    mods = discover_accessories()                     # {"camera_pod": <module>, ...}
    parts = build_accessory(mods["camera_pod"])       # {"camera_pod_21": Part, ...} installed
    results = run_checks(mods["camera_pod"], parts)   # [(name, passed, detail), ...]

A module may also declare VARIANTS to ship several genuinely different style options of the same
accessory. Then it builds once per variant and every label carries the variant as a suffix:

    VARIANTS = {"shard": {"style": "shard"}, "carapace": {"style": "carapace", "material": "PETG"}}
    def build(variant="shard", **overrides) -> dict[str, Part]: ...   # returns BASE labels

    for v, parts in build_variants(mods["side_panels"]).items():      # {"shard": {...}, ...}
        run_checks(mods["side_panels"], parts, v)                     # labels "side_panel_right__shard"

checks() stays SHARED across variants and is handed the base labels, so the same fit assertions must
pass whatever the style does.
"""

import importlib
import pkgutil
from types import ModuleType

from build123d import Part

from tigerbee.accessories import _fit as F

REQUIRED = ("NAME", "TITLE", "MATERIAL", "build", "checks")
VARIANT_SEP = "__"  # final label = "<base label><SEP><variant>"; a base label may not contain it
OPTIONAL_DEFAULTS = {
    "VARIANTS": {},  # variant name -> {"style": <_style.STYLES key>, "params": {...build kwargs},
    #                  "material": "PETG"|"TPU95A", "print": {base_label: (nx, ny, nz)}, "notes": str}
    #                  Declaring it makes build() take a `variant=` keyword and emit one part set per
    #                  variant, labelled "<base>__<variant>". Leaving it {} keeps the old behaviour.
    "ASSEMBLY_VARIANT": None,  # which variant goes into tigerbee_with_accessories (default: the first)
    "PRINT": {},  # label -> bed normal (frame coords); missing labels print on their -Z face
    "EXCLUSIVE": (),  # accessory ids that cannot be installed together with this one
    "NOTES": "",  # mounting notes for the manifest (str, or {label: str})
    "MOUNTS": (),  # frame axes/faces this part mounts to, one string each (or {label: tuple})
    "HARDWARE": (),  # fasteners needed, "<count> x <size> <type> (<where>)" (or {label: tuple})
    "MIN_Z": F.LANDING_Z,  # landing plane: lowest allowed Z of any part
    "ALLOWED_INTERFERENCE": {},  # label -> {frame_part: max mm^3} for intended press fits
    "OWN_PROP_DISC": {},  # label -> motor name whose disc the part may enter below OWN_DISC_Z_MAX
    "BATTERY_OK": False,  # True only for the battery pad (it lives inside the BATTERY envelope)
    "BRIDGE_OK": {},  # label -> tuple of ('box', x0, y0, z0, x1, y1, z1) in PRINT coords, see overhangs()
    "OVERHANG_SKIP": (),  # labels excluded from the generic overhang check (justify in NOTES)
    "ASSEMBLY_BUILD": {},  # build(**kwargs) used for the combined tigerbee_with_accessories assembly
    "ASSEMBLY_LABELS": (),  # base labels that go into the combined assembly; () means all of them.
    #                 Declare it when a module's parts are ALTERNATIVES rather than a set - the two
    #                 camera pod sizes occupy the same space, and "install one side only" brackets
    #                 ship as a mirrored pair. The left-out labels are recorded in the manifest.
}


def attr(mod: ModuleType, name: str):
    return getattr(mod, name, OPTIONAL_DEFAULTS[name])


def base_label(label: str) -> str:
    """"side_panel_right__carapace" -> "side_panel_right". Every per-label module dict (PRINT,
    BRIDGE_OK, NOTES, ALLOWED_INTERFERENCE, OWN_PROP_DISC, OVERHANG_SKIP) may be keyed by either."""
    return label.split(VARIANT_SEP, 1)[0]


def variant_of(label: str) -> str:
    """"side_panel_right__carapace" -> "carapace"; "" for an unvariated label."""
    return label.split(VARIANT_SEP, 1)[1] if VARIANT_SEP in label else ""


def variants(mod: ModuleType) -> dict[str, dict]:
    """{} when the module declares none, which means exactly one unnamed build."""
    return dict(attr(mod, "VARIANTS"))


def variant_names(mod: ModuleType, only: str | list[str] | None = None) -> list[str]:
    """The variants to build. [""] means "the module has none, build it once". `only` filters, and
    asks loudly rather than silently building everything when the name is unknown."""
    vs = variants(mod)
    if not vs:
        return [""]
    names = list(vs)
    if only:
        want = [only] if isinstance(only, str) else list(only)
        hit = [n for n in names if n in want]
        assert hit, f"{mod.NAME}: unknown variant(s) {want}; available: {names}"
        return hit
    return names


def opt(mod: ModuleType, key: str, label: str, default=None):
    """A per-label optional dict, looked up by the FINAL label first and the base label second, so a
    module written before variants existed keeps working and a variant may still override one entry."""
    table = attr(mod, key)
    if label in table:
        return table[label]
    return table.get(base_label(label), default)


def label_meta(mod: ModuleType, key: str, label: str):
    """A descriptive attribute (NOTES, MOUNTS, HARDWARE) that a module may declare either once for
    the whole accessory or as a {label: value} table. Returns the value for this label; a table with
    no entry for the label (nor its base label) falls back to the OPTIONAL_DEFAULTS empty value."""
    table = attr(mod, key)
    if isinstance(table, dict):
        return opt(mod, key, label, OPTIONAL_DEFAULTS[key])
    return table


def mounts(mod: ModuleType, label: str) -> list[str]:
    """The frame axes and faces this label mounts to, as the manifest records them."""
    return list(label_meta(mod, "MOUNTS", label))


def hardware(mod: ModuleType, label: str) -> list[str]:
    """The fasteners this label needs, as the manifest records them."""
    return list(label_meta(mod, "HARDWARE", label))


def material_of(mod: ModuleType, variant: str = "") -> str:
    """The variant's material, else the module's. A style family may need PETG where the module's
    default is TPU (CARAPACE wants a gloss; FERAL wants TPU on anything leading a crash)."""
    spec = variants(mod).get(variant) or {}
    return spec.get("material", mod.MATERIAL)


def style_name(mod: ModuleType, variant: str = "") -> str:
    return (variants(mod).get(variant) or {}).get("style", "")


def validate(mod: ModuleType) -> None:
    missing = [a for a in REQUIRED if not hasattr(mod, a)]
    assert not missing, f"{mod.__name__}: missing {missing}"
    assert mod.NAME == mod.__name__.rsplit(".", 1)[-1], f"{mod.__name__}: NAME must equal the module name"
    assert mod.MATERIAL in ("TPU95A", "PETG"), f"{mod.__name__}: MATERIAL {mod.MATERIAL!r}"
    vs = variants(mod)
    for name, spec in vs.items():
        assert name and VARIANT_SEP not in name and name.isidentifier(), \
            f"{mod.__name__}: variant name {name!r} must be an identifier without {VARIANT_SEP!r}"
        assert isinstance(spec, dict), f"{mod.__name__}: VARIANTS[{name!r}] must be a dict"
        assert material_of(mod, name) in ("TPU95A", "PETG"), \
            f"{mod.__name__}: VARIANTS[{name!r}] material {spec.get('material')!r}"
        if spec.get("style"):
            from tigerbee.accessories._style import STYLES
            assert spec["style"] in STYLES, \
                f"{mod.__name__}: VARIANTS[{name!r}] style {spec['style']!r} not in {sorted(STYLES)}"
    av = attr(mod, "ASSEMBLY_VARIANT")
    assert av is None or av in vs, f"{mod.__name__}: ASSEMBLY_VARIANT {av!r} not in {sorted(vs)}"
    for key in ("MOUNTS", "HARDWARE"):
        table = attr(mod, key)
        assert table, f"{mod.__name__}: {key} must be declared (see _template.py) - the manifest " \
                      f"records what the part bolts to and what fasteners it needs"
        rows = [r for v in table.values() for r in v] if isinstance(table, dict) else list(table)
        assert rows and all(isinstance(r, str) and r.strip() for r in rows), \
            f"{mod.__name__}: {key} entries must be non-empty strings, got {rows!r}"


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


def build_accessory(mod: ModuleType, variant: str = "", **overrides) -> dict[str, Part]:
    """One variant's parts, keyed by their FINAL labels.

    A module with VARIANTS is called as build(variant=<name>, **VARIANTS[name]["params"], **overrides)
    and keeps returning its own BASE labels; the suffix is appended here, so PRINT/BRIDGE_OK/NOTES
    and the module's own checks() stay written against the base labels."""
    vs = variants(mod)
    if not vs:
        assert not variant, f"{mod.NAME} declares no VARIANTS, so variant={variant!r} is meaningless"
        parts = mod.build(**overrides)
    else:
        variant = variant or next(iter(vs))
        spec = vs[variant]
        parts = mod.build(variant=variant, **{**spec.get("params", {}), **overrides})
    assert isinstance(parts, dict) and parts, f"{mod.NAME}.build() must return a non-empty dict"
    out = {}
    for label, part in parts.items():
        assert isinstance(label, str) and isinstance(part, Part), f"{mod.NAME}: {label!r} -> {type(part)}"
        assert VARIANT_SEP not in label, f"{mod.NAME}: build() must return BASE labels, got {label!r}"
        final = f"{label}{VARIANT_SEP}{variant}" if variant else label
        part.label = final
        out[final] = part
    return out


def build_variants(mod: ModuleType, only: str | list[str] | None = None, **overrides) -> dict[str, dict[str, Part]]:
    """{variant name: {final label: Part}}; the key is "" for a module without VARIANTS."""
    return {v: build_accessory(mod, v, **overrides) for v in variant_names(mod, only)}


def printed(mod: ModuleType, label: str, part: Part) -> Part:
    """Part re-oriented for printing (module hook orient_for_print(label, part), else PRINT[label],
    else the -Z face on the bed)."""
    from tigerbee.accessories._common import print_orientation
    if hasattr(mod, "orient_for_print"):
        p = mod.orient_for_print(label, part)
    else:
        p = print_orientation(part, print_normal(mod, label))
    p.label = label
    return p


def print_normal(mod: ModuleType, label: str) -> tuple:
    """The bed normal for this label: VARIANTS[v]["print"] first (a style may choose its own bed
    normal - a domed CARAPACE shell prints apex-up, which is a different normal from its SHARD
    sibling), then PRINT, then the -Z face."""
    spec = variants(mod).get(variant_of(label)) or {}
    per_variant = spec.get("print") or {}
    base = base_label(label)
    if label in per_variant or base in per_variant:
        return tuple(per_variant.get(label, per_variant.get(base)))
    return tuple(opt(mod, "PRINT", label, (0, 0, -1)))


def generic_checks(mod: ModuleType, parts: dict[str, Part]) -> list[tuple[str, bool, str]]:
    """Checks every accessory must pass, independent of its spec."""
    from tigerbee.accessories._common import BATTERY, overhangs
    out = []
    min_z = attr(mod, "MIN_Z")
    for label, part in parts.items():
        allowed = {label: opt(mod, "ALLOWED_INTERFERENCE", label, {})}
        own = {label: opt(mod, "OWN_PROP_DISC", label)} if opt(mod, "OWN_PROP_DISC", label) else {}
        material = material_of(mod, variant_of(label))
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
        skip = attr(mod, "OVERHANG_SKIP")
        if label not in skip and base_label(label) not in skip:
            over = overhangs(part, print_normal(mod, label), bridge_ok=opt(mod, "BRIDGE_OK", label, ()),
                             material=material)
            out.append((f"{label}: no unsupported overhangs in print orientation", not over, "; ".join(over) or "none"))
    return out


def run_checks(mod: ModuleType, parts: dict[str, Part], variant: str = "") -> list[tuple[str, bool, str]]:
    """Generic checks (on the FINAL labels) followed by the module's own checks().

    The module's checks() is handed the parts dict keyed by its BASE labels, so ONE checks() serves
    every variant - which is exactly the guarantee wanted: whatever the style does, the same fit
    assertions must still pass. Its rows are prefixed with "[<variant>] " so the manifest and the
    verifier can tell two variants' rows apart. A variant-aware module may declare
    checks(parts, frame, variant=None) and it will be passed."""
    import inspect
    results = generic_checks(mod, parts)
    base = {base_label(label): part for label, part in parts.items()}
    try:
        takes_variant = "variant" in inspect.signature(mod.checks).parameters
    except (TypeError, ValueError):
        takes_variant = False
    rows = mod.checks(base, F.frame_parts(), variant=variant) if takes_variant else mod.checks(base, F.frame_parts())
    prefix = f"[{variant}] " if variant else ""
    for row in rows:
        name, ok, detail = row
        results.append((f"{prefix}{name}", bool(ok), str(detail)))
    return results


def __getattr__(name):
    if name == "CATALOG":
        return list(discover_accessories().values())
    raise AttributeError(name)
