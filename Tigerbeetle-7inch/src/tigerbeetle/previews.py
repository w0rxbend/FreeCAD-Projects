"""exports/renders/: the quad from several sides, the frame, the cut sheet, the tracing overlays, every
part on its own and every printed part in place, and exports/GALLERY.md that shows them all."""

from copy import deepcopy
from pathlib import Path

from build123d import Axis, Vector
from zhalo.previews import FRONT_ISO, LOW_FRONT, PART_SIZE, REAR_ISO, SIZE, UNDER, _visible
from zhalo.render import Item, render

from tigerbeetle import accessories as A
from tigerbeetle import equipment as E
from tigerbeetle import export as X
from tigerbeetle import frame as F
from tigerbeetle import overlay


def _frame():
    return [Item(p, "aluminium" if m == F.ALUMINIUM else "carbon") for p, m in F.build().values()]


def _gear(skip=()):
    return [Item(p, c, o, edges=o == 1.0) for n, (p, c, o) in E.build().items() if not n.startswith(skip)]


def _accessories():
    return [Item(p, a.color) for a in A.assembly() for p in (a.part, *a.instances)]


def _exploded():
    lift = {"plate_bottom": -20.0, "arm": 0.0, "plate_camera": 22.0, "standoff": 40.0, "plate_top": 70.0}
    out = []
    for name, (part, m) in F.build().items():
        dz = next((v for k, v in lift.items() if name.startswith(k)), 0.0)
        out.append(Item(deepcopy(part).translate(Vector(0, 0, dz)), "aluminium" if m == F.ALUMINIUM else "carbon"))
    return out


def _cut_sheet():
    out, x = [], 0.0
    for name in X.SHEETS:
        solid = F.solid(X.sheet(name))
        if name == "arm":
            solid = solid.rotate(Axis.Z, 90)
        bb = solid.bounding_box()
        out.append(Item(solid.translate(Vector(x - bb.min.X, -(bb.min.Y + bb.max.Y) / 2, 0)), "carbon"))
        x += bb.size.X + 12.0
    return out


def _montage(out: Path) -> None:
    """All printed parts on one sheet."""
    from PIL import Image, ImageDraw, ImageFont

    accs = [a for a in A.build_all() if not a.name.endswith("_left")]
    tile, cols = (640, 480), 4
    rows = -(-len(accs) // cols)
    sheet = Image.new("RGB", (cols * tile[0], rows * tile[1]), "white")
    font = ImageFont.load_default(size=26)
    for i, acc in enumerate(accs):
        png = out / f"_tile_{acc.name}.png"
        render([Item(acc.part, acc.color)], png, "iso", size=tile)
        with Image.open(png) as im:
            sheet.paste(im.convert("RGB"), ((i % cols) * tile[0], (i // cols) * tile[1]))
        png.unlink()
        label = acc.name + (f"  x{acc.qty}" if acc.qty > 1 else "")
        ImageDraw.Draw(sheet).text(
            ((i % cols) * tile[0] + 12, (i // cols) * tile[1] + 10), label, fill="black", font=font
        )
    sheet.save(out / "accessories.png")


def render_all(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    fp = list(F.parts().values())
    props = [Item(E.prop(xy), "prop", 0.13, edges=False) for xy in F.motors().values()]
    full = _frame() + _gear(("prop_", "battery")) + _accessories()
    jobs = [
        ("hero", _frame() + _gear(("prop_",)) + _accessories() + props, FRONT_ISO, fp, 0.8),
        ("complete_rear", full, REAR_ISO, fp, 1.0),
        ("complete_top", full, "top", fp, 1.0),
        ("complete_side", full, "side", fp, 1.0),
        ("nose", full, LOW_FRONT, fp, 1.9),
        ("underside", full, UNDER, fp, 1.0),
        ("frame", _frame(), FRONT_ISO, None, 1.0),
        ("frame_top", _frame(), "top", None, 1.0),
        ("frame_exploded", _exploded(), FRONT_ISO, None, 1.0),
        ("cut_sheet", _cut_sheet(), "top", None, 1.0),
    ]
    done = [render(items, out / f"{n}.png", v, size=SIZE, focus=f, zoom=z) for n, items, v, f, z in jobs]
    fit = overlay.draw(out)
    done += [out / "overlay_scan_1.png", out / "overlay_scan_2.png"]
    _montage(out)
    done.append(out / "accessories.png")
    (out / "parts").mkdir(exist_ok=True)
    (out / "installed").mkdir(exist_ok=True)
    parts = {"carbon": [], "printed": [], "installed": []}
    for name in X.SHEETS:
        png = render([Item(F.solid(X.sheet(name)), "carbon")], out / "parts" / f"{name}.png", "iso", size=PART_SIZE)
        parts["carbon"].append((name.replace("_", " ") + (", x4" if name == "arm" else ""), png))
    scene = _frame() + _gear(("prop_", "battery"))
    for acc in A.build_all():
        title = acc.title + (f", x{acc.qty}" if acc.qty > 1 else "")
        parts["printed"].append(
            (title, render([Item(acc.part, acc.color)], out / "parts" / f"{acc.name}.png", "iso", size=PART_SIZE))
        )
        shown = [acc.part, *acc.instances]
        lo = min(p.bounding_box().min.Z for p in shown)
        view = UNDER if lo < 0 else ((0.95, 1.2, 0.75), (0, 0, 1), False)
        items = scene + [Item(p, _visible(acc.color)) for p in shown]
        parts["installed"].append(
            (title, render(items, out / "installed" / f"{acc.name}.png", view, size=PART_SIZE, focus=fp))
        )
    gallery(out, done, parts)
    return fit


def gallery(out: Path, overview, parts) -> Path:
    root = out.parent

    def grid(entries):
        lines = ["| | |", "|---|---|"]
        for i in range(0, len(entries), 2):
            cells = [f"![{t}]({p.relative_to(root).as_posix()})<br>{t}" for t, p in entries[i : i + 2]]
            lines.append("| " + " | ".join(cells + [""] * (2 - len(cells))) + " |")
        return lines

    lines = [
        "# Tiger Beetle 7-inch: gallery",
        "",
        "Every render of this frame. Models are in `cnc/`, `print/` and `assembly/`.",
        "",
    ]
    lines += ["## The quad", "", *grid([(p.stem.replace("_", " "), p) for p in overview]), ""]
    lines += ["## Carbon parts", "", *grid(parts["carbon"]), ""]
    lines += ["## Printed parts", "", *grid(parts["printed"]), ""]
    lines += ["## Printed parts in place", "", *grid(parts["installed"]), ""]
    page = root / "GALLERY.md"
    page.write_text("\n".join(lines))
    return page
