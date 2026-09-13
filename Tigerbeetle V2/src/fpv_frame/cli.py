"""Command-line entry point for the parametric reconstruction workflow."""

import argparse
import json
import sys
from dataclasses import asdict
from hashlib import sha256
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
    overlay = commands.add_parser("overlay", help="Overlay actual CAD profiles on a source scan")
    overlay.add_argument("scan", choices=("scan-1", "scan-2"))
    commands.add_parser("build", help="Build and mechanically validate the complete frame")
    commands.add_parser("validate", help="Run assembly topology, interface and fit gates")
    export = commands.add_parser("export", help="Export validated CAD and manufacturing profiles")
    export.add_argument(
        "--format", action="append", choices=("step", "stl", "3mf", "svg", "freecad")
    )
    export.add_argument("--part", help="One component name, or arm for the canonical arm")
    export.add_argument("--output", type=Path)
    drawing = commands.add_parser("drawing", help="Generate 1:1 profiles and assembly SVG views")
    drawing.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        params = get_preset(args.preset)
        if args.command == "parameters":
            result: object = asdict(params)
        elif args.command == "overlay":
            from fpv_frame.blueprint.workflow import write_diagnostics

            scan = "Scan_1" if args.scan == "scan-1" else "Scan_2"
            paths = write_diagnostics(params, args.root, scan)
            result = {"scan": scan, "files": [str(path) for path in paths]}
        elif args.command in ("build", "validate", "export", "drawing"):
            from fpv_frame.assembly import validate_assembly
            from fpv_frame.assembly.frame import build_assembly

            inspect_sources(args.root)
            model = build_assembly(params)
            report = validate_assembly(model)
            parameter_data = asdict(params)
            parameter_hash = sha256(json.dumps(
                parameter_data, sort_keys=True, separators=(",", ":"), allow_nan=False,
            ).encode()).hexdigest()
            report.update({"preset": args.preset, "parameters_hash": parameter_hash,
                           "parameters": parameter_data})
            report_dir = args.root / "artifacts/reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "assembly.json").write_text(json.dumps(report, indent=2) + "\n")
            result = report
            if args.command in ("export", "drawing"):
                from build123d import Compound

                from fpv_frame.export import export_artifacts

                parts, profiles = model.parts, model.profiles
                selection = getattr(args, "part", None)
                if selection:
                    if selection == "arm":
                        from fpv_frame.parts.arm import arm_profile, build_arm

                        parts, profiles = {"arm": build_arm(params)}, {"arm": arm_profile(params)}
                    elif selection in parts:
                        parts = {selection: parts[selection]}
                        profiles = {selection: profiles[selection]}
                    else:
                        raise ValueError(f"Unknown component: {selection}")
                formats = (
                    ("svg",)
                    if args.command == "drawing"
                    else tuple(args.format or ("step", "stl", "3mf", "svg", "freecad"))
                )
                metadata = {
                    "preset": args.preset,
                    "parameters": parameter_data,
                    "parameters_hash": parameter_hash,
                    "wheelbase_mm": model.layout.wheelbase,
                    "selection": selection,
                }
                default_output = args.root / "dist"
                if args.command == "drawing":
                    default_output = args.root / "artifacts/drawings"
                elif selection:
                    default_output = args.root / "dist/parts" / selection
                exported_paths = export_artifacts(
                    parts,
                    profiles,
                    model.compound if not selection else Compound(children=list(parts.values())),
                    args.output or default_output,
                    formats=formats,
                    metadata=metadata,
                    include_assembly=not bool(selection),
                )
                result = {"files": [str(path) for path in exported_paths], "validation": report}
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
                "status": (
                    "Parametric reconstruction; measured and assumed dimensions carry evidence"
                ),
            }
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(f"fpv-frame: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
