"""Command-line entry point for the parametric reconstruction workflow."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from fpv_frame.blueprint.calibration import calibrate_page
from fpv_frame.blueprint.measurements import inspect_sources
from fpv_frame.parameters.presets import PRESET_NAMES, get_preset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fpv-frame")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project reference directory")
    parser.add_argument("--preset", choices=PRESET_NAMES, default="default")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="Inspect original evidence and reconstruction assumptions")
    commands.add_parser("parameters", help="Print immutable engineering parameters as JSON")
    args = parser.parse_args(argv)
    try:
        params = get_preset(args.preset)
        if args.command == "parameters":
            result: object = asdict(params)
        else:
            sources = inspect_sources(args.root)
            size = sources["Scan_1.jpeg"]["size_px"]
            result = {
                "sources": sources,
                "confirmed_dimensions_mm": {
                    "arm_thickness": get_preset("reference").arm.thickness,
                    "plate_thickness": get_preset("reference").plates[0].thickness,
                },
                "page_calibration": asdict(calibrate_page((size[0], size[1]), (210, 297))),
                "scale_basis": "User-confirmed A4 tracing sheet; assumes full-page scan",
                "assembly_reference": "references/assembly/user-assembly.png",
                "status": "Reconstruction in progress; CAD and manufacturing gates pending",
            }
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError) as error:
        print(f"fpv-frame: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
