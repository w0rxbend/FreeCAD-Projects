"""Named solid and mesh exports, with staged publication and content hashes."""

import hashlib
import json
import math
import platform
import re
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path
from typing import Any

from build123d import Compound, Face, Mesher, Shape, Unit, export_step, export_stl

from fpv_frame import __version__
from fpv_frame.drawing import export_drawings

FORMATS = ("step", "stl", "3mf", "svg", "freecad")
LINEAR_TOLERANCE_MM = 0.05
ANGULAR_TOLERANCE_RAD = 0.1


def _provenance() -> dict[str, Any]:
    """Record the executing software and source revision; never invent a revision."""
    commit = None
    dirty = None
    source = Path(__file__).resolve().parents[3]
    if shutil.which("git"):
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=source, capture_output=True, text=True
        )
        if revision.returncode == 0:
            commit = revision.stdout.strip()
            status = subprocess.run(
                ["git", "status", "--porcelain", "--", "."],
                cwd=source,
                capture_output=True,
                text=True,
            )
            dirty = bool(status.stdout.strip()) if status.returncode == 0 else None
    return {
        "project_version": __version__,
        "version": __version__,
        "python_version": platform.python_version(),
        "build123d_version": version("build123d"),
        "git_commit": commit,
        "git_dirty": dirty,
    }


def _named_parts(parts: Mapping[str, Shape[Any]]) -> dict[str, Shape[Any]]:
    result = {}
    for name, part in parts.items():
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name) or name == "fpv-frame":
            raise ValueError(f"Unsafe or reserved component name: {name!r}")
        if not part.solids() or not part.is_valid:
            raise ValueError(f"Component {name!r} has no valid solid geometry")
        result[name] = deepcopy(part)
        result[name].label = name
        result[name].parent = None
    return result


def _solid_exports(
    parts: Mapping[str, Shape[Any]],
    output: Path,
    formats: Sequence[str],
    include_assembly: bool,
    linear_tolerance: float,
    angular_tolerance: float,
) -> None:
    shapes = dict(parts)
    if include_assembly:
        shapes["fpv-frame"] = Compound(
            children=[deepcopy(p) for p in parts.values()], label="fpv-frame"
        )
    for format_name in formats:
        if format_name not in ("step", "stl", "3mf"):
            continue
        folder = output / format_name
        folder.mkdir()
        for name, shape in shapes.items():
            path = folder / f"{name}.{format_name}"
            if format_name == "step":
                if not export_step(shape, path, unit=Unit.MM, timestamp="2000-01-01T00:00:00"):
                    raise RuntimeError(f"STEP export failed: {name}")
            elif format_name == "stl":
                if not export_stl(
                    shape,
                    path,
                    tolerance=linear_tolerance,
                    angular_tolerance=angular_tolerance,
                    ascii_format=False,
                ):
                    raise RuntimeError(f"STL export failed: {name}")
            else:
                mesher = Mesher(unit=Unit.MM)
                members = list(parts.values()) if name == "fpv-frame" else [shape]
                for member in members:
                    solids = list(member.solids())
                    for index, solid in enumerate(solids):
                        solid.label = (
                            member.label if len(solids) == 1 else f"{member.label}_{index + 1}"
                        )
                    mesher.add_shape(
                        solids,
                        linear_deflection=linear_tolerance,
                        angular_deflection=angular_tolerance,
                    )
                mesher.write(path)


def _publish(stage: Path, output: Path) -> list[Path]:
    """Replace only files named by our previous manifest; preserve unrelated evidence."""
    previous = output / "manifest.json"
    old_paths = []
    if previous.exists():
        for item in json.loads(previous.read_text())["artifacts"]:
            path = Path(item["path"])
            if path.is_absolute() or ".." in path.parts or path.parts[0] not in FORMATS:
                raise ValueError("Previous export manifest contains an unsafe artifact path")
            old_paths.append(output / path)
    output.mkdir(parents=True, exist_ok=True)
    generated = sorted(path for path in stage.rglob("*") if path.is_file())
    new_paths = {output / path.relative_to(stage) for path in generated}
    for source in generated:
        target = output / source.relative_to(stage)
        target.parent.mkdir(parents=True, exist_ok=True)
        source.replace(target)
    for old in old_paths:
        if old not in new_paths:
            old.unlink(missing_ok=True)
    for format_name in FORMATS:
        folder = output / format_name
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return sorted(new_paths)


def export_artifacts(
    parts: Mapping[str, Shape[Any]],
    profiles: Mapping[str, Face],
    assembly: Compound,
    output: Path | str,
    formats: Sequence[str] = FORMATS,
    metadata: Mapping[str, Any] | None = None,
    *,
    include_assembly: bool = True,
    linear_tolerance: float | None = None,
    angular_tolerance: float | None = None,
) -> list[Path]:
    """Export individual parts and the frame; fail without publishing partial results.

    Mesh defaults are 0.05 mm linear and 0.1 radians angular. Explicit keywords
    override metadata parameters.manufacturing tolerances, which override defaults.
    The supplied assembly drives drawings; named physical parts drive all solid formats.
    FreeCAD is optional only when explicitly omitted from ``formats``.
    """
    selected = tuple(dict.fromkeys(formats))
    if not selected or set(selected) - set(FORMATS):
        raise ValueError(f"Choose one or more formats from {', '.join(FORMATS)}")
    if not parts:
        raise ValueError("At least one physical component is required")
    details = dict(metadata or {})
    manufacturing = details.get("parameters", {}).get("manufacturing", {})
    linear = (
        linear_tolerance
        if linear_tolerance is not None
        else manufacturing.get("linear_tolerance", LINEAR_TOLERANCE_MM)
    )
    angular = (
        angular_tolerance
        if angular_tolerance is not None
        else manufacturing.get("angular_tolerance", ANGULAR_TOLERANCE_RAD)
    )
    for value in (linear, angular):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise ValueError("Mesh tolerances must be finite positive numbers")
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Mesh tolerances must be finite positive numbers")
    named = _named_parts(parts)
    for name in profiles:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
            raise ValueError(f"Unsafe profile name: {name!r}")
    # Snapshot the input revision before our output/staging files can affect Git status.
    provenance = _provenance()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fpv-export-", dir=output.parent) as temporary:
        stage = Path(temporary)
        solid_formats = list(selected)
        if "freecad" in selected and "step" not in selected:
            solid_formats.append("step")
        _solid_exports(named, stage, solid_formats, include_assembly, linear, angular)
        if "svg" in selected:
            export_drawings(profiles, assembly, stage / "svg", include_assembly=include_assembly)
        if "freecad" in selected:
            from fpv_frame.export.freecad import convert_step

            targets = ["fpv-frame"] if include_assembly else list(named)
            for name in targets:
                convert_step(stage / f"step/{name}.step", stage / f"freecad/{name}.FCStd")
            if "step" not in selected:
                for path in (stage / "step").iterdir():
                    path.unlink()
                (stage / "step").rmdir()
        artifacts = [
            {
                "path": path.relative_to(stage).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(stage.rglob("*"))
            if path.is_file()
        ]
        manifest = {
            "schema_version": 1,
            "units": "mm",
            "formats": list(selected),
            "mesh": {
                "linear_tolerance_mm": linear,
                "angular_tolerance_rad": angular,
                "stl_binary": True,
            },
            "components": list(named),
            "metadata": {**provenance, **details},
            "artifacts": artifacts,
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return _publish(stage, output)
