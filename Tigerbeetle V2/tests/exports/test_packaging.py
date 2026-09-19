"""Release integrity tests do not require launching a second CAD runtime."""

import hashlib
import importlib.util
import json
import zipfile
from dataclasses import asdict
from pathlib import Path

import pytest

from fpv_frame.parameters.presets import get_preset

spec = importlib.util.spec_from_file_location(
    "package_release", Path(__file__).resolve().parents[2] / "tools/package_release.py"
)
assert spec and spec.loader
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


@pytest.fixture
def release_input(tmp_path):
    exports, evidence = tmp_path / "exports", tmp_path / "evidence"
    components = ["plate", "arm"]
    names = [
        f"{fmt}/{name}.{fmt}"
        for fmt in ("step", "stl", "3mf")
        for name in (*components, "fpv-frame")
    ]
    names += ["freecad/fpv-frame.FCStd", "freecad/fpv-frame.reopen.json"]
    names += [f"svg/{name}{suffix}.svg" for name in components for suffix in ("", ".dimensioned")]
    names += [f"svg/assembly_{view}.svg" for view in ("top", "bottom", "front", "side")]
    artifacts = []
    for name in names:
        path = exports / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({
                "status": "passed", "reopened": True,
                "solid_count": len(components),
                "components": [{"name": component, "solids": 1} for component in components],
            })
            if name.endswith(".reopen.json")
            else f"fixture {name}"
        )
        artifacts.append(
            {
                "path": name,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    metadata = {
        "project_version": "0.1.0",
        "git_commit": "a" * 40,
        "preset": "reference",
        "python_version": "3.12.1",
        "build123d_version": "0.11.0",
        "wheelbase_mm": 230,
        "parameters": asdict(get_preset("reference")),
    }
    metadata["parameters_hash"] = hashlib.sha256(
        json.dumps(metadata["parameters"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    (exports / "manifest.json").write_text(
        json.dumps(
            {
                "units": "mm",
                "formats": list(packaging.FORMATS),
                "components": components,
                "metadata": metadata,
                "artifacts": artifacts,
            }
        )
    )
    for scan in ("Scan_1", "Scan_2"):
        for extension in ("png", "svg"):
            path = evidence / f"overlays/{scan}_overlay.{extension}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture overlay")
    for preset in packaging.PRESETS:
        path = evidence / f"reports/validate-{preset}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        preset_parameters = asdict(get_preset(preset))
        path.write_text(json.dumps({
            "valid": True,
            "preset": preset,
            "wheelbase_mm": metadata["wheelbase_mm"],
            "component_count": len(components),
            "parameters": preset_parameters,
            "parameters_hash": hashlib.sha256(json.dumps(
                preset_parameters, sort_keys=True, separators=(",", ":"),
            ).encode()).hexdigest(),
        }))
    parameters = evidence / "parameters.json"
    parameters.write_text(json.dumps(metadata["parameters"]))
    return exports, evidence, parameters, tmp_path / "package"


def test_complete_package_has_checksummed_inventory_and_format_archives(release_input):
    output = packaging.package_release(*release_input)
    bundle, release = output / "cad-artifacts", output / "release-assets"
    for root in (bundle, release):
        for line in (root / "SHA256SUMS").read_text().splitlines():
            checksum, name = line.split("  ", 1)
            assert hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum
    assert {p.name for p in release.glob("*.zip")} == {
        "STEP.zip",
        "STL.zip",
        "3MF.zip",
        "FreeCAD.zip",
        "SVG.zip",
        "overlays.zip",
        "reports.zip",
        "parameters.zip",
    }
    with zipfile.ZipFile(release / "STEP.zip") as archive:
        assert "STEP/fpv-frame.step" in archive.namelist()
    with pytest.raises(ValueError, match="already exists"):
        packaging.package_release(*release_input)


@pytest.mark.parametrize(
    "missing",
    ["step/fpv-frame.step", "freecad/fpv-frame.FCStd", "svg/arm.dimensioned.svg", "3mf/plate.3mf"],
)
def test_missing_required_export_rejected_even_if_removed_from_manifest(release_input, missing):
    exports, _, _, output = release_input
    (exports / missing).unlink()
    path = exports / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["artifacts"] = [item for item in manifest["artifacts"] if item["path"] != missing]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Incomplete export inventory"):
        packaging.package_release(*release_input)
    assert not output.exists()


def test_changed_cad_checksum_prevents_packaging(release_input):
    (release_input[0] / "step/plate.step").write_text("tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        packaging.package_release(*release_input)


def test_stale_unmanifested_cad_prevents_packaging(release_input):
    (release_input[0] / "step/old.step").write_text("stale")
    with pytest.raises(ValueError, match="stale"):
        packaging.package_release(*release_input)


def test_failed_preset_prevents_packaging(release_input):
    (release_input[1] / "reports/validate-tolerance_test.json").write_text('{"valid":false}')
    with pytest.raises(ValueError, match="validation failed"):
        packaging.package_release(*release_input)


def test_mismatched_parameter_snapshot_prevents_packaging(release_input):
    release_input[2].write_text('{"arm":{"thickness":3}}')
    with pytest.raises(ValueError, match="differs"):
        packaging.package_release(*release_input)


def test_missing_scan_overlay_prevents_packaging(release_input):
    (release_input[1] / "overlays/Scan_2_overlay.png").unlink()
    with pytest.raises(ValueError, match="Missing"):
        packaging.package_release(*release_input)


def test_manifest_cannot_read_outside_export_root(release_input):
    exports = release_input[0]
    path = exports / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["artifacts"][0]["path"] = "step/../../private.step"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Unsafe"):
        packaging.package_release(*release_input)


@pytest.mark.parametrize("field", ["preset", "parameters", "parameters_hash"])
def test_validation_report_without_identity_prevents_packaging(release_input, field):
    path = release_input[1] / "reports/validate-default.json"
    report = json.loads(path.read_text())
    del report[field]
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="Validation report"):
        packaging.package_release(*release_input)


def test_report_from_another_preset_prevents_packaging(release_input):
    reports = release_input[1] / "reports"
    (reports / "validate-default.json").write_bytes(
        (reports / "validate-reference.json").read_bytes()
    )
    with pytest.raises(ValueError, match="preset"):
        packaging.package_release(*release_input)


def test_stale_parameters_with_internally_consistent_hash_prevent_packaging(release_input):
    path = release_input[1] / "reports/validate-tolerance_test.json"
    report = json.loads(path.read_text())
    report["parameters"]["arm"]["thickness"] = 1
    report["parameters_hash"] = hashlib.sha256(json.dumps(
        report["parameters"], sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="current preset"):
        packaging.package_release(*release_input)


@pytest.mark.parametrize("replacement", [None, "outdated"])
def test_export_parameter_hash_must_match_its_snapshot(release_input, replacement):
    path = release_input[0] / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["metadata"]["parameters_hash"] = replacement
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Export parameter hash"):
        packaging.package_release(*release_input)


def test_export_must_match_its_validated_preset(release_input):
    path = release_input[0] / "manifest.json"
    manifest = json.loads(path.read_text())
    metadata = manifest["metadata"]
    metadata["parameters"]["arm"]["thickness"] = 1
    metadata["parameters_hash"] = hashlib.sha256(json.dumps(
        metadata["parameters"], sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    path.write_text(json.dumps(manifest))
    release_input[2].write_text(json.dumps(metadata["parameters"]))
    with pytest.raises(ValueError, match="exported CAD parameters"):
        packaging.package_release(*release_input)


def test_export_dimensions_must_match_validation(release_input):
    path = release_input[0] / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["metadata"]["wheelbase_mm"] += 1
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="wheelbase"):
        packaging.package_release(*release_input)


def test_export_component_count_must_match_validation(release_input):
    path = release_input[1] / "reports/validate-reference.json"
    report = json.loads(path.read_text())
    report["component_count"] += 1
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="component count"):
        packaging.package_release(*release_input)


def test_native_reopen_inventory_must_match_export_inventory(release_input):
    exports = release_input[0]
    path = exports / "freecad/fpv-frame.reopen.json"
    report = json.loads(path.read_text())
    report["components"][0]["name"] = "missing_plate"
    path.write_text(json.dumps(report))
    manifest_path = exports / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for item in manifest["artifacts"]:
        if item["path"] == "freecad/fpv-frame.reopen.json":
            item["bytes"] = path.stat().st_size
            item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="FreeCAD component inventory"):
        packaging.package_release(*release_input)
