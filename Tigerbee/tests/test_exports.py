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
