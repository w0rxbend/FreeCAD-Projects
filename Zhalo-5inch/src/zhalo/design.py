"""Which design the engine is building.

Zhalo is the default. A sibling project (Shershen) reuses this engine with its own carbon
profiles and accessories: it sets these values and replaces `frame.SHEETS` and
`accessories.MODULES` before anything is built.
"""

NAME = "Zhalo 5-inch"  # shown in the manifest
SLUG = "zhalo"  # file-name stem of the assemblies
DOCUMENT = "Zhalo-5inch"  # FreeCAD document name
EXTRA_COLORS: dict[str, tuple[float, float, float]] = {}  # render colour overrides, by material or colour key
BOM = None  # optional callable returning the bill of materials, for a design with other hardware
MASS_LIMIT = 130.0  # grams of carbon the frame check accepts
COLOR_OF: dict[str, str] = {}  # accessory name -> colour key, for parts reused from Zhalo in another palette


def colors() -> dict[str, tuple[float, float, float]]:
    from zhalo.render import COLORS

    return {**COLORS, **EXTRA_COLORS}
