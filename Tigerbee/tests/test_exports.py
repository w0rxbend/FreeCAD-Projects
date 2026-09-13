import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pytest
from build123d import import_step

from tigerbee.export import export_component
from tigerbee.models import build_part


def test_exports_reopen_and_record_parameters(tmp_path):
    manifest = export_component("arm-type-1", tmp_path)
    actual = import_step(tmp_path / "arm-type-1.step")
    expected = build_part("arm-type-1")
    assert actual.is_valid
    assert actual.volume == pytest.approx(expected.volume, abs=1e-5)
    assert (actual - expected).volume < 1e-4
    with ZipFile(tmp_path / "arm-type-1.3mf") as archive:
        assert archive.testzip() is None
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        assert model.get("unit") == "millimeter"
        assert len(model.findall(".//{*}triangle")) > 0
    svg = ET.parse(tmp_path / "arm-type-1.svg")
    assert svg.getroot().tag.endswith("svg")
    saved = json.loads((tmp_path / "arm-type-1.json").read_text())
    assert saved == manifest
    assert saved["parameters"]["thickness"] == 5
    assert saved["units"] == "mm"
    assert saved["valid"] is True
    assert saved["mesh_validation"]["valid"]
    assert saved["authoritative_geometry_source"] == "Tigerbee.FCStd"
    assert saved["reference_status"] == "symmetric-design-derived-from-reference"


@pytest.mark.parametrize("name", ["arm-type-2", "camera-plate", "rear-plate", "top-plate"])
def test_every_component_export_is_valid(name, tmp_path):
    report = export_component(name, tmp_path)
    reopened = import_step(tmp_path / f"{name}.step")
    assert reopened.is_valid
    assert len(reopened.solids()) == 1
    assert reopened.volume == pytest.approx(report["volume_mm3"], abs=1e-3)
    assert report["mesh_validation"]["valid"]


def test_cli_default_bores_match_assembly_components(tmp_path, monkeypatch):
    import sys

    from tigerbee.cli import main
    from tigerbee.models import DEFAULT_PARAMETERS

    monkeypatch.setattr(
        sys, "argv", ["tigerbee", "build", "camera-plate", "--output", str(tmp_path)]
    )
    main()
    saved = json.loads((tmp_path / "camera-plate.json").read_text())
    assert (
        saved["parameters"]["mounting_hole_diameter"] == DEFAULT_PARAMETERS.mounting_hole_diameter
    )
    assert saved["parameters"]["mounting_hole_diameter"] == 3.2


def test_failed_geometry_cannot_be_exported_without_optional_fit_flag(tmp_path, monkeypatch):
    from tigerbee import assembly
    from tigerbee.export import export_frame

    monkeypatch.setattr(
        assembly,
        "build_assembly",
        lambda params: (
            None,
            {"geometry_audit": {"passed": False, "issues": ["blocked shaft passage"]}},
        ),
    )
    with pytest.raises(ValueError, match="blocked shaft passage"):
        export_frame(tmp_path)
    assert not list(tmp_path.iterdir())


def test_scan_provenance_does_not_describe_current_manufacturing_geometry(tmp_path):
    from tigerbee.models import profile_data

    report = export_component("rear-plate", tmp_path)
    historical = profile_data("rear-plate")["assumptions"]
    assert report["reference_assumptions"] == historical
    assert not set(historical).intersection(report["assumptions"])
    assert any("3.2 mm" in note for note in report["assumptions"])


def test_custom_camera_diameter_is_recorded_in_effective_design_dimensions(tmp_path):
    from build123d import GeomType

    from tigerbee.models import PartParameters

    report = export_component("camera-plate", tmp_path, PartParameters(center_hole_diameter=19))
    actual = import_step(tmp_path / "camera-plate.step")
    circles = actual.edges().filter_by(GeomType.CIRCLE)
    assert any(edge.radius == pytest.approx(9.5) for edge in circles)
    assert report["design_dimensions_mm"]["camera_round_diameter"] == 19
