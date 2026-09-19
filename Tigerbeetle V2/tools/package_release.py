#!/usr/bin/env python3
"""Validate a complete CAD build and package only its declared, checked artifacts."""

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fpv_frame.parameters.presets import PRESET_NAMES, get_preset

FORMATS = {"step": "STEP", "stl": "STL", "3mf": "3MF", "freecad": "FreeCAD", "svg": "SVG"}
PRESETS = PRESET_NAMES


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parameter_hash(parameters: object) -> str:
    serialized = json.dumps(parameters, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(serialized.encode()).hexdigest()


def validate_report(report: dict[str, Any], preset: str, metadata: dict[str, Any]) -> None:
    """Tie every report to today's preset and the selected report to the exported CAD."""
    if report.get("valid") is not True:
        raise ValueError(f"Assembly validation failed: {preset}")
    if report.get("preset") != preset:
        raise ValueError(f"Validation report preset differs from its filename: {preset}")
    parameters = report.get("parameters")
    if not parameters or report.get("parameters_hash") != parameter_hash(parameters):
        raise ValueError(f"Validation report parameter hash is missing or inconsistent: {preset}")
    if report["parameters_hash"] != parameter_hash(asdict(get_preset(preset))):
        raise ValueError(f"Validation report differs from current preset parameters: {preset}")
    if preset == metadata["preset"]:
        if parameters != metadata["parameters"]:
            raise ValueError("Validation report differs from the exported CAD parameters")
        if report.get("wheelbase_mm") != metadata["wheelbase_mm"]:
            raise ValueError("Validation report wheelbase differs from the exported CAD dimensions")


def checked_file(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in relative:
        raise ValueError(f"Unsafe artifact path: {relative!r}")
    result = root / path
    if result.is_symlink() or root.resolve() not in result.resolve().parents:
        raise ValueError(f"Artifact escapes its source directory: {relative}")
    if not result.is_file() or not result.stat().st_size:
        raise ValueError(f"Missing or empty artifact: {relative}")
    return result


def validated_exports(exports: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    manifest = json.loads(checked_file(exports, "manifest.json").read_text())
    if manifest.get("units") != "mm" or set(manifest.get("formats", [])) != set(FORMATS):
        raise ValueError("A release requires all five CAD formats in millimetres")
    components = manifest.get("components", [])
    if not components or len(set(components)) != len(components):
        raise ValueError("Missing or duplicate assembly components")
    files: dict[str, Path] = {}
    for item in manifest["artifacts"]:
        name = item["path"]
        if name in files or Path(name).parts[0] not in FORMATS:
            raise ValueError(f"Unexpected or duplicate export: {name}")
        path = checked_file(exports, name)
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise ValueError(f"Export checksum mismatch: {name}")
        files[name] = path
    required = {
        f"{fmt}/{name}.{fmt}"
        for fmt in ("step", "stl", "3mf")
        for name in (*components, "fpv-frame")
    }
    required.update(("freecad/fpv-frame.FCStd", "freecad/fpv-frame.reopen.json"))
    required.update(f"svg/assembly_{view}.svg" for view in ("top", "bottom", "front", "side"))
    required.update(
        f"svg/{name}{suffix}.svg" for name in components for suffix in ("", ".dimensioned")
    )
    if missing := required - files.keys():
        raise ValueError(f"Incomplete export inventory: {', '.join(sorted(missing))}")
    actual = {
        p.relative_to(exports).as_posix()
        for fmt in FORMATS
        for p in (exports / fmt).rglob("*")
        if p.is_file()
    }
    if actual != files.keys():
        raise ValueError("Unmanifested stale files exist in CAD export directories")
    reopened = json.loads(files["freecad/fpv-frame.reopen.json"].read_text())
    if reopened.get("status") != "passed" or reopened.get("reopened") is not True:
        raise ValueError("FreeCAD reopen verification did not pass")
    native_components = reopened.get("components", [])
    if (
        reopened.get("solid_count") != len(components)
        or len(native_components) != len(components)
        or {item.get("name") for item in native_components} != set(components)
        or any(item.get("solids") != 1 for item in native_components)
    ):
        raise ValueError("FreeCAD component inventory differs from the exported assembly")
    files["export-manifest.json"] = exports / "manifest.json"
    return manifest, files


def package_release(exports: Path, evidence: Path, parameters: Path, output: Path) -> Path:
    """Produce cad-artifacts and per-format release ZIPs; refuse stale destination reuse."""
    if output.exists():
        raise ValueError(f"Package output already exists; choose a fresh directory: {output}")
    manifest, files = validated_exports(exports)
    metadata = manifest.get("metadata", {})
    for key in ("project_version", "git_commit", "preset", "python_version", "build123d_version"):
        if not metadata.get(key):
            raise ValueError(f"Export metadata is missing {key}")
    if not metadata.get("parameters") or not metadata.get("wheelbase_mm"):
        raise ValueError("Export metadata must record parameters and primary dimensions")
    if metadata["preset"] not in PRESETS:
        raise ValueError("Export preset has no required validation report")
    if metadata.get("parameters_hash") != parameter_hash(metadata["parameters"]):
        raise ValueError("Export parameter hash is missing or inconsistent")
    parameter_data = json.loads(parameters.read_text())
    if parameter_data != metadata["parameters"]:
        raise ValueError("Parameters JSON differs from the exported CAD parameters")
    files["parameters.json"] = parameters
    for scan in ("Scan_1", "Scan_2"):
        for extension in ("svg", "png"):
            name = f"overlays/{scan}_overlay.{extension}"
            files[name] = checked_file(evidence, name)
    for preset in PRESETS:
        name = f"reports/validate-{preset}.json"
        report = checked_file(evidence, name)
        report_data = json.loads(report.read_text())
        validate_report(report_data, preset, metadata)
        if (
            preset == metadata["preset"]
            and report_data.get("component_count") != len(manifest["components"])
        ):
            raise ValueError("Validation report component count differs from the exported assembly")
        files[name] = report
    for path in sorted((evidence / "reports").rglob("*")):
        if path.is_file():
            name = path.relative_to(evidence).as_posix()
            files[name] = checked_file(evidence, name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fpv-package-", dir=output.parent) as temporary:
        stage = Path(temporary) / "package"
        bundle, release = stage / "cad-artifacts", stage / "release-assets"
        bundle.mkdir(parents=True)
        release.mkdir()
        for name, source in sorted(files.items()):
            target = bundle / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        inventory = [
            {"path": name, "bytes": (bundle / name).stat().st_size, "sha256": digest(bundle / name)}
            for name in sorted(files)
        ]
        release_manifest = {
            "schema_version": 1,
            "units": "mm",
            "metadata": metadata,
            "artifacts": inventory,
        }
        (bundle / "manifest.json").write_text(json.dumps(release_manifest, indent=2) + "\n")
        sums = "".join(
            f"{digest(path)}  {path.relative_to(bundle).as_posix()}\n"
            for path in sorted(bundle.rglob("*"))
            if path.is_file()
        )
        (bundle / "SHA256SUMS").write_text(sums)
        for source_dir, archive_dir in {
            **FORMATS,
            "overlays": "overlays",
            "reports": "reports",
            "parameters": "parameters",
        }.items():
            members = (
                [bundle / "parameters.json"]
                if source_dir == "parameters"
                else sorted((bundle / source_dir).rglob("*"))
            )
            with zipfile.ZipFile(release / f"{archive_dir}.zip", "w", zipfile.ZIP_DEFLATED) as z:
                for path in members:
                    if path.is_file():
                        relative = (
                            path.name
                            if source_dir == "parameters"
                            else path.relative_to(bundle / source_dir).as_posix()
                        )
                        info = zipfile.ZipInfo(f"{archive_dir}/{relative}", (2000, 1, 1, 0, 0, 0))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        info.external_attr = 0o100644 << 16
                        z.writestr(info, path.read_bytes())
        shutil.copyfile(bundle / "manifest.json", release / "manifest.json")
        (release / "SHA256SUMS").write_text(
            "".join(f"{digest(path)}  {path.name}\n" for path in sorted(release.iterdir()))
        )
        stage.rename(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", type=Path, default=Path("dist"))
    parser.add_argument("--evidence", type=Path, default=Path("artifacts"))
    parser.add_argument("--parameters", type=Path, default=Path("artifacts/parameters.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(package_release(args.exports, args.evidence, args.parameters, args.output))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"package_release: {error}\n")


if __name__ == "__main__":
    main()
