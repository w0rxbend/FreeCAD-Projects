"""Real runtime integration: enable with FPV_TEST_FREECAD=1 when FreeCAD is installed."""

import json
import os
import zipfile

import pytest
from build123d import Box, Compound, Cylinder, Pos, import_step

from fpv_frame.export import export_artifacts


@pytest.mark.skipif(os.environ.get("FPV_TEST_FREECAD") != "1", reason="needs FreeCAD runtime")
def test_freecad_named_assembly_survives_save_and_reopen(tmp_path):
    parts = {
        "plate": Box(20, 30, 2) - Pos(2.17, 3.43, 0) * Cylinder(2.3, 2),
        "arm": Pos(40, 0, 3) * Box(10, 50, 5),
    }
    export_artifacts(parts, {}, Compound(children=list(parts.values())), tmp_path, ("freecad",))
    output = tmp_path / "freecad/fpv-frame.FCStd"
    assert zipfile.is_zipfile(output)
    report = json.loads(output.with_suffix(".reopen.json").read_text())
    assert report["status"] == "passed" and report["reopened"]
    assert report["solid_count"] == 2
    assert report["volume_mm3"] == pytest.approx(sum(p.volume for p in parts.values()))
    assert report["volume_relative_tolerance"] == 1e-10
    assert report["volume_absolute_tolerance_mm3"] == 1e-8
    assert report["maximum_volume_change_mm3"] < 1e-8
    assert {item["name"] for item in report["components"]} == {"arm", "plate"}
    assert not (tmp_path / "step").exists()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert "freecad/fpv-frame.reopen.json" in {item["path"] for item in manifest["artifacts"]}


@pytest.mark.skipif(os.environ.get("FPV_TEST_FREECAD") != "1", reason="needs FreeCAD runtime")
def test_real_frame_curved_components_survive_step_and_freecad(tmp_path):
    """Real curved parts exposed floating mass-property drift absent from box fixtures."""
    from fpv_frame.assembly import build_assembly
    from fpv_frame.parameters.presets import get_preset

    frame = build_assembly(get_preset("default"))
    export_artifacts(frame.parts, frame.profiles, frame.compound, tmp_path, ("step", "freecad"))
    imported = import_step(tmp_path / "step/fpv-frame.step")
    assert len(imported.solids()) == len(frame.parts) == 15
    assert imported.volume == pytest.approx(frame.compound.volume, rel=1e-9)
    report = json.loads((tmp_path / "freecad/fpv-frame.reopen.json").read_text())
    assert report["status"] == "passed" and report["reopened"]
    assert {item["name"] for item in report["components"]} == set(frame.parts)
    for item in report["components"]:
        assert item["solids"] == 1
        assert item["volume_mm3"] == pytest.approx(frame.parts[item["name"]].volume, rel=1e-9)
