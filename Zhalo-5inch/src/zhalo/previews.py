"""The PNGs under exports/renders/ and the gallery page that shows them all.

renders/*.png            the quad from several sides, the bare frame, the exploded frame, the cut sheet
renders/parts/*.png      every carbon part and every printed part on its own
renders/installed/*.png  every printed part in its place on the frame, the rest of the frame in carbon grey
GALLERY.md               all of the above on one page (next to exports/, so GitHub shows it)
"""

from copy import deepcopy
from pathlib import Path

from build123d import Axis, Vector

from zhalo import accessories as A
from zhalo import design
from zhalo import equipment as E
from zhalo import frame as F
from zhalo import params as P
from zhalo.render import Item, render

SIZE = (1600, 1200)
FRONT_ISO = ((1.0, 1.15, 0.8), (0, 0, 1), False)
REAR_ISO = ((0.9, -1.25, 0.7), (0, 0, 1), False)
LOW_FRONT = ((0.55, 1.3, 0.3), (0, 0, 1), False)


def _frame(color: str | None = None) -> list[Item]:
    return [Item(p, color or ("aluminium" if m == F.ALUMINIUM else "carbon")) for p, m in F.build().values()]


def _gear(skip: tuple[str, ...] = ()) -> list[Item]:
    return [Item(p, c, o, edges=o == 1.0) for n, (p, c, o) in E.build().items() if not n.startswith(skip)]


def _accessories() -> list[Item]:
    return [Item(p, a.color) for a in A.assembly() for p in (a.part, *a.instances)]


def _exploded() -> list[Item]:
    lift = {"plate_bottom": -26.0, "brace": -44.0, "arm": 0.0, "plate_mid": 24.0, "standoff": 42.0, "plate_top": 74.0}
    out = []
    for name, (part, material) in F.build().items():
        dz = next((v for k, v in lift.items() if name.startswith(k)), 0.0)
        out.append(
            Item(deepcopy(part).translate(Vector(0, 0, dz)), "aluminium" if material == F.ALUMINIUM else "carbon")
        )
    return out


def _cut_sheet() -> list[Item]:
    """The flat parts side by side, as a CNC shop would see them."""
    out, x = [], 0.0
    order = ("plate_bottom", "plate_top", "plate_mid", "arm", "brace")
    names = [n for n in order if n in F.SHEETS and (n != "brace" or P.BRACES)]
    for name in names + [n for n in F.SHEETS if n not in order]:
        solid = F.SHEETS[name]().solid()
        if name == "arm":
            solid = solid.rotate(Axis.Z, 90)
        bb = solid.bounding_box()
        out.append(Item(solid.translate(Vector(x - bb.min.X, -(bb.min.Y + bb.max.Y) / 2, 0)), "carbon"))
        x += bb.size.X + 12.0
    return out


def _montage(out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    accs = [a for a in A.build_all() if not a.name.endswith("_left")]
    tile, cols = (640, 480), 4
    rows = -(-len(accs) // cols)
    sheet = Image.new("RGB", (cols * tile[0], rows * tile[1]), "white")
    try:
        font = ImageFont.load_default(size=26)
    except TypeError:
        font = ImageFont.load_default()
    for i, acc in enumerate(accs):
        png = out / f"_tile_{acc.name}.png"
        render([Item(acc.part, acc.color)], png, "iso", size=tile)
        with Image.open(png) as im:
            sheet.paste(im.convert("RGB"), ((i % cols) * tile[0], (i // cols) * tile[1]))
        png.unlink()
        label = acc.name + (f"  x{acc.qty}" if acc.qty > 1 else "")
        ImageDraw.Draw(sheet).text(
            ((i % cols) * tile[0] + 16, (i // cols) * tile[1] + 12), label, fill=(30, 30, 30), font=font
        )
    sheet.save(out / "accessories.png", optimize=True)


UNDER = ((0.9, -1.1, -0.75), (0, 0, 1), False)
PART_SIZE = (1200, 900)


def _visible(color: str) -> str:
    """A colour that stands out against carbon: a dark TPU part is shown in the design's accent."""
    palette = design.colors()
    rgb = palette.get(color, palette["tpu"])
    if sum(rgb) / 3 >= 0.35:
        return color
    return "accent" if "accent" in palette else "highlight"


def _installed_view(parts) -> tuple:
    """Look at the part from its own corner of the quad; parts that live under the floor from below."""
    lo = [min(getattr(p.bounding_box().min, k) for p in parts) for k in "XYZ"]
    hi = [max(getattr(p.bounding_box().max, k) for p in parts) for k in "XYZ"]
    if hi[2] <= P.Z_ARM + 1e-6:
        return UNDER
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    sx = -1.0 if cx < -1.0 else 1.0
    sy = -1.0 if cy < -1.0 else 1.0
    return ((0.95 * sx, 1.2 * sy, 0.75), (0, 0, 1), False)


def render_parts(out: Path) -> dict[str, list[tuple[str, Path]]]:
    """One image per carbon part and per printed part, plus each printed part installed."""
    (out / "parts").mkdir(parents=True, exist_ok=True)
    (out / "installed").mkdir(parents=True, exist_ok=True)
    done: dict[str, list[tuple[str, Path]]] = {"carbon": [], "printed": [], "installed": []}
    for name, make in F.SHEETS.items():
        sheet = make()
        title = f"{name}, {sheet.thickness:g} mm" + (f", x{sheet.count}" if sheet.count > 1 else "")
        png = render([Item(sheet.solid(), "carbon")], out / "parts" / f"{name}.png", "iso", size=PART_SIZE)
        done["carbon"].append((title, png))
    scene = _frame() + _gear(("prop_", "battery"))
    frame_parts = list(F.parts().values())
    for acc in A.build_all():
        title = acc.title + (f", x{acc.qty}" if acc.qty > 1 else "")
        png = render([Item(acc.part, acc.color)], out / "parts" / f"{acc.name}.png", "iso", size=PART_SIZE)
        done["printed"].append((title, png))
        if acc.in_assembly:
            shown = [acc.part, *acc.instances]
            items = scene + [Item(p, _visible(acc.color)) for p in shown]
            png = render(
                items, out / "installed" / f"{acc.name}.png", _installed_view(shown), size=PART_SIZE, focus=frame_parts
            )
            done["installed"].append((title, png))
    return done


def write_gallery(out: Path, overview: list[Path], parts: dict[str, list[tuple[str, Path]]]) -> Path:
    """exports/GALLERY.md: every image on one page, two to a row."""
    root = out.parent

    def grid(entries: list[tuple[str, Path]]) -> list[str]:
        lines = ["| | |", "|---|---|"]
        for i in range(0, len(entries), 2):
            cells = [f"![{t}]({p.relative_to(root).as_posix()})<br>{t}" for t, p in entries[i : i + 2]]
            lines.append("| " + " | ".join(cells + [""] * (2 - len(cells))) + " |")
        return lines

    names = {
        "hero": "complete, front",
        "complete_rear": "complete, rear",
        "complete_top": "complete, top",
        "complete_side": "complete, side",
        "nose": "nose",
        "frame": "frame",
        "frame_top": "frame, top",
        "frame_exploded": "frame, exploded",
        "cut_sheet": "carbon parts as cut",
        "accessories": "all printed parts",
    }
    lines = [
        f"# {design.NAME}: gallery",
        "",
        "Every render of this design. The models themselves are in "
        "`cnc/` (carbon: DXF, STEP, STL), `print/` (TPU: STL, 3MF, STEP) and `assembly/` (STEP, STL, FreeCAD).",
        "",
    ]
    lines += ["## The quad", "", *grid([(names.get(p.stem, p.stem), p) for p in overview]), ""]
    analysis = sorted((root / "analysis").glob("*.png"))
    if analysis:
        lines += ["## Arm analysis", "", *grid([(p.stem.replace("_", " "), p) for p in analysis]), ""]
    lines += ["## Carbon parts", "", *grid(parts["carbon"]), ""]
    lines += ["## Printed parts", "", *grid(parts["printed"]), ""]
    lines += ["## Printed parts in place", "", *grid(parts["installed"]), ""]
    page = root / "GALLERY.md"
    page.write_text("\n".join(lines))
    return page


def render_all(out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    frame_parts = list(F.parts().values())
    props = [Item(E.prop(xy), "prop", 0.13, edges=False) for xy in P.MOTORS.values()]
    jobs = [
        ("hero", _frame() + _gear(("prop_",)) + _accessories() + props, FRONT_ISO, frame_parts, 0.8),
        ("complete_rear", _frame() + _gear(("prop_", "battery")) + _accessories(), REAR_ISO, frame_parts, 1.0),
        ("complete_top", _frame() + _gear(("prop_", "battery")) + _accessories(), "top", frame_parts, 1.0),
        ("complete_side", _frame() + _gear(("prop_", "battery")) + _accessories(), "side", frame_parts, 1.0),
        ("nose", _frame() + _gear(("prop_", "battery")) + _accessories(), LOW_FRONT, frame_parts, 1.9),
        ("frame", _frame(), FRONT_ISO, None, 1.0),
        ("frame_top", _frame(), "top", None, 1.0),
        ("frame_exploded", _exploded(), FRONT_ISO, None, 1.0),
        ("cut_sheet", _cut_sheet(), "top", None, 1.0),
    ]
    done = []
    for name, items, view, focus, zoom in jobs:
        done.append(render(items, out / f"{name}.png", view, size=SIZE, focus=focus, zoom=zoom))
    _montage(out)
    done.append(out / "accessories.png")
    parts = render_parts(out)
    write_gallery(out, done, parts)
    return done + [p for group in parts.values() for _t, p in group]
