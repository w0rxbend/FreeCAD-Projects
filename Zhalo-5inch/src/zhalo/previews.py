"""The PNGs under exports/renders/: what the README shows."""

from copy import deepcopy
from pathlib import Path

from build123d import Axis, Vector

from zhalo import accessories as A
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
    return done
