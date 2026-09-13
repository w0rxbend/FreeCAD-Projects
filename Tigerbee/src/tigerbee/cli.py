"""Command-line builds for individual components and complete output sets."""

import argparse
from pathlib import Path

from tigerbee.models import PARTS, PartParameters


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List implemented components")
    build = commands.add_parser("build", help="Generate STEP, 3MF, STL, SVG, DXF and metadata")
    build.add_argument("part", nargs="?", choices=PARTS)
    build.add_argument("--all", action="store_true", help="Build every implemented component")
    build.add_argument("--output", type=Path, default=Path("build/parts"))
    build.add_argument("--thickness", type=float)
    build.add_argument("--mounting-hole-diameter", type=float, default=3.0)
    build.add_argument("--center-hole-diameter", type=float)
    arguments = parser.parse_args()
    if arguments.command == "list":
        print("\n".join(PARTS))
        return
    if bool(arguments.part) == arguments.all:
        parser.error("Choose one part or --all")
    from tigerbee.export import export_component

    parameters = PartParameters(
        thickness=arguments.thickness,
        mounting_hole_diameter=arguments.mounting_hole_diameter,
        center_hole_diameter=arguments.center_hole_diameter,
    )
    try:
        for name in PARTS if arguments.all else (arguments.part,):
            report = export_component(name, arguments.output, parameters)
            print(f"Built {name}: {report['volume_mm3']:.3f} mm³ -> {arguments.output}")
    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
