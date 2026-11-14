"""Pictures of the quad: renders/ and GALLERY.md."""

from pathlib import Path

from build123d import Pos

from bolid import accessories as ACC
from bolid import gear as G
from bolid import geometry as GEO
from bolid.render import Item, render

OUT = Path(__file__).resolve().parents[2] / "exports" / "renders"


def _frame(explode: float = 0.0) -> list[Item]:
    items = []
    lift = {"plate_bottom": -2, "arm": -1, "plate_press": 0, "standoff": 1, "plate_top": 2}
    for name, (part, mat) in GEO.build().items():
        k = next(v for key, v in lift.items() if name.startswith(key))
        p = part.translate((0, 0, k * explode)) if explode else part
        items.append(Item(p, "carbon" if mat == "carbon" else "aluminium"))
    return items


def _accessories(explode: float = 0.0, faded: bool = False) -> list[Item]:
    items = []
    for a in ACC.assembly():
        for p in (a.part, *a.instances):
            items.append(Item(p.translate((0, 0, 3 * explode)) if explode else p, a.color, 0.35 if faded else 1.0))
    return items


def _gear(props: bool = True) -> list[Item]:
    items = []
    for name, (part, color, opacity) in G.build().items():
        if name.startswith("prop") and not props:
            continue
        items.append(Item(part, color, opacity, edges=not name.startswith("prop")))
    return items


def frame_renders() -> list[Path]:
    full = _frame() + _accessories() + _gear()
    shots = [
        (full, "hero.png", "front_iso", 1.0),
        (full, "complete_rear.png", "rear_iso", 1.0),
        (full, "complete_top.png", "top", 1.0),
        (full, "complete_side.png", "side", 1.0),
        (full, "low.png", "low", 1.0),
        (_frame() + _accessories() + _gear(False), "belly.png", "under", 1.0),
        (_frame(), "frame.png", "iso", 1.0),
        (_frame(), "frame_top.png", "top", 1.0),
        (_frame(14.0), "frame_exploded.png", "iso", 1.0),
    ]
    out = [render(items, OUT / name, view, zoom=zoom) for items, name, view, zoom in shots]
    # the tail: antennas, close up
    tail = [a.part for a in ACC.assembly() if a.name in ("rear_wing", "engine_cover")]
    out.append(render(full, OUT / "tail.png", "tail", zoom=1.0, focus=tail))
    nose = [a.part for a in ACC.assembly() if a.name in ("body_shell", "front_splitter")]
    out.append(render(full, OUT / "nose.png", "front_iso", zoom=1.0, focus=nose))
    return out


def cut_sheet() -> Path:
    items, x = [], 0.0
    for make in GEO.PLATES.values():
        plate = make()
        solid = plate.solid()
        bb = solid.bounding_box()
        copies = 1 if plate.count == 1 else min(plate.count, 8)
        for k in range(copies):
            dy = k * (bb.size.Y + 6)
            items.append(Item(Pos(x - bb.min.X, dy - bb.min.Y, 0) * solid, "carbon"))
        x += bb.size.X + 12
    return render(items, OUT / "cut_sheet.png", "top", size=(1800, 900))


def accessory_renders() -> list[Path]:
    out = []
    base = _frame() + _gear(False)
    for a in ACC.build_all():
        out.append(
            render(
                [Item(ACC.base.lay_on_bed(a.part, a.bed), a.color)],
                OUT / "parts" / f"{a.name}.png",
                "iso",
                size=(800, 600),
            )
        )
        if a.in_assembly:
            fade = [Item(i.part, i.color, 0.35, False) for i in base]
            out.append(
                render(
                    fade + [Item(p, a.color) for p in (a.part, *a.instances)],
                    OUT / "installed" / f"{a.name}.png",
                    "front_iso",
                    size=(1000, 750),
                    focus=[a.part, *a.instances] if a.qty == 1 else None,
                )
            )
    return out


def montage() -> Path:
    from PIL import Image

    files = sorted((OUT / "parts").glob("*.png"))
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 400, rows * 300), "white")
    for i, f in enumerate(files):
        with Image.open(f) as im:
            sheet.paste(im.resize((400, 300), Image.LANCZOS), ((i % cols) * 400, (i // cols) * 300))
    path = OUT / "accessories.png"
    sheet.save(path, optimize=True)
    return path


def gallery_md() -> Path:
    def img(rel, title):
        return f"### {title}\n\n![{title}](renders/{rel})\n"

    parts = [
        '# Bolid 5" — галерея\n',
        img("hero.png", "Зібраний, спереду"),
        img("complete_rear.png", "Ззаду"),
        img("tail.png", "Хвіст: антикрило з антенами, капот, стоп-сигнал"),
        img("nose.png", "Ніс: камера, сплітер"),
        img("complete_top.png", "Зверху"),
        img("complete_side.png", "Збоку"),
        img("low.png", "Низький ракурс"),
        img("belly.png", "Знизу: кожухи проводів, ковзанки"),
        img("frame.png", "Голий карбон"),
        img("frame_top.png", "Карбон зверху"),
        img("frame_exploded.png", "Розібраний: нижня плита, 4 промені, притискна плита, стійки, верхня плита"),
        img("cut_sheet.png", "Лист різки"),
        img("accessories.png", "Усі друковані деталі"),
        "## Кожна деталь на місці\n",
    ]
    for a in ACC.build_all():
        if a.in_assembly:
            parts.append(img(f"installed/{a.name}.png", a.title))
    path = OUT.parent / "GALLERY.md"
    path.write_text("\n".join(parts))
    return path


def render_all() -> list[Path]:
    out = frame_renders()
    out.append(cut_sheet())
    out += accessory_renders()
    out.append(montage())
    out.append(gallery_md())
    return out
