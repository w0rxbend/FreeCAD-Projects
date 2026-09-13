"""Command-line builds for individual components and complete output sets."""

import argparse
from pathlib import Path

from tigerbee.models import DEFAULT_PARAMETERS, PARTS
from tigerbee.presets import PRESETS, part_parameters


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List implemented components")
    native = commands.add_parser("native", help="Generate and verify native FreeCAD documents")
    native.add_argument("--directory", type=Path, default=Path("exports"))
    verify = commands.add_parser(
        "verify-exports", help="Check committed CAD files against their sources"
    )
    verify.add_argument("--directory", type=Path, default=Path("exports"))
    assembly = commands.add_parser(
        "assembly", help="Build the symmetric frame and audit geometric fit"
    )
    assembly.add_argument("--top-z", type=float, default=35.0)
    assembly.add_argument("--output", type=Path, default=Path("exports/assembly"))
    assembly.add_argument(
        "--require-fit", action="store_true", help="Fail on unresolved assembly fit"
    )
    build = commands.add_parser("build", help="Generate STEP, 3MF, STL, SVG, DXF and metadata")
    build.add_argument("part", nargs="?", choices=PARTS)
    build.add_argument("--all", action="store_true", help="Build every implemented component")
    build.add_argument("--preset", choices=PRESETS, default="frame")
    build.add_argument("--output", type=Path, default=Path("exports/parts"))
    build.add_argument("--thickness", type=float)
    build.add_argument(
        "--mounting-hole-diameter",
        type=float,
        default=DEFAULT_PARAMETERS.mounting_hole_diameter,
    )
    build.add_argument("--center-hole-diameter", type=float)
    build.add_argument("--length-extension", type=float, default=0.0)
    arguments = parser.parse_args()
    if arguments.command == "list":
        print("\n".join(PARTS))
        return
    if arguments.command == "native":
        from tigerbee.native import export_native

        try:
            reports = export_native(arguments.directory)
        except (ValueError, RuntimeError) as error:
            parser.exit(1, f"Native export failed: {error}\n")
        for report in reports:
            print(f"Verified {report['file']}: {report['solids']} solids")
        return
    if arguments.command == "verify-exports":
        from tigerbee.inventory import verify_inventory

        try:
            count = verify_inventory(arguments.directory)
        except (ValueError, OSError) as error:
            parser.exit(1, f"Export verification failed: {error}\n")
        print(f"Verified {count} committed outputs against the current CAD sources")
        return
    if arguments.command == "assembly":
        from tigerbee.export import export_frame

        try:
            report = export_frame(arguments.output, arguments.top_z, arguments.require_fit)
        except (ValueError, RuntimeError) as error:
            parser.exit(1, f"Assembly failed: {error}\n")
        wheelbases = ", ".join(f"{value:.2f}" for value in report["diagonal_wheelbases_mm"])
        print(f"Built assembly: wheelbases {wheelbases} mm -> {arguments.output}")
        print(f"Fit status: {report['status']}; see assembly-report.json for measured checks.")
        return
    if bool(arguments.part) == arguments.all:
        parser.error("Choose one part or --all")
    from tigerbee.export import export_component

    try:
        for name in PARTS if arguments.all else (arguments.part,):
            parameters = part_parameters(
                name,
                arguments.preset,
                thickness=arguments.thickness,
                mounting_hole_diameter=arguments.mounting_hole_diameter,
                center_hole_diameter=arguments.center_hole_diameter,
                length_extension=arguments.length_extension,
            )
            report = export_component(name, arguments.output, parameters)
            print(f"Built {name}: {report['volume_mm3']:.3f} mm³ -> {arguments.output}")
    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
