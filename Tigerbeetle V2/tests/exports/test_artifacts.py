import hashlib
import json
import struct
import xml.etree.ElementTree as ET
import zipfile

import pytest
from build123d import Box, Compound, Face, Pos, Wire, import_step

from fpv_frame.export import export_artifacts


@pytest.fixture
def fixture_frame():
    parts = {"plate": Box(20, 30, 2), "arm": Pos(40, 0, 3) * Box(10, 50, 5)}
    profiles = {"plate": Face(Wire.make_circle(10), [Wire.make_circle(2)])}
    return parts, profiles, Compound(children=list(parts.values()))


def test_step_stl_3mf_roundtrip_and_manifest(tmp_path, fixture_frame):
    parts, profiles, assembly = fixture_frame
    outputs = export_artifacts(parts, profiles, assembly, tmp_path, ("step", "stl", "3mf"))
    step = import_step(tmp_path / "step/fpv-frame.step")
    assert len(step.solids()) == 2
    assert step.volume == pytest.approx(assembly.volume)
    content = (tmp_path / "step/fpv-frame.step").read_text()
    assert "plate" in content and "arm" in content
    assert "MILLI" in content
    stl = (tmp_path / "stl/fpv-frame.stl").read_bytes()
    triangles = struct.unpack_from("<I", stl, 80)[0]
    assert triangles > 0 and len(stl) == 84 + triangles * 50
    with zipfile.ZipFile(tmp_path / "3mf/fpv-frame.3mf") as archive:
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
    assert model.attrib["unit"] == "millimeter"
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    names = {obj.attrib.get("name") for obj in model.findall(".//m:object", ns)}
    assert {"plate", "arm"} <= names
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["units"] == "mm"
    assert manifest["mesh"]["linear_tolerance_mm"] == 0.05
    for artifact in manifest["artifacts"]:
        path = tmp_path / artifact["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]
    assert tmp_path / "manifest.json" in outputs


def test_svg_true_scale_and_analytic_circles(tmp_path, fixture_frame):
    export_artifacts(*fixture_frame, tmp_path, ("svg",))
    svg = ET.parse(tmp_path / "svg/plate.svg").getroot()
    bounds = list(map(float, svg.attrib["viewBox"].split()))
    assert float(svg.attrib["width"].removesuffix("mm")) == pytest.approx(bounds[2])
    assert float(svg.attrib["height"].removesuffix("mm")) == pytest.approx(bounds[3])
    text = (tmp_path / "svg/plate.svg").read_text()
    assert "circle" in text or " A " in text
    dimensioned = (tmp_path / "svg/plate.dimensioned.svg").read_text()
    assert "20.00 mm" in dimensioned and "DATUM" in dimensioned
    for view in ("top", "bottom", "front", "side"):
        assert (tmp_path / f"svg/assembly_{view}.svg").is_file()


def test_front_drawing_observes_frame_from_positive_y(tmp_path, fixture_frame, monkeypatch):
    """The documented frame front is +Y, with +Z up in the front projection."""
    cameras = []
    original = Compound.project_to_viewport

    def record_projection(self, viewport_origin, viewport_up, **kwargs):
        cameras.append((viewport_origin, viewport_up))
        return original(self, viewport_origin, viewport_up, **kwargs)

    monkeypatch.setattr(Compound, "project_to_viewport", record_projection)
    export_artifacts(*fixture_frame, tmp_path, ("svg",))
    assert ((0, 1000, 0), (0, 0, 1)) in cameras
    assert ((0, -1000, 0), (0, 0, 1)) not in cameras


def test_reexport_removes_stale_generated_outputs_only(tmp_path, fixture_frame):
    report = tmp_path / "review.txt"
    report.write_text("retain validation evidence")
    export_artifacts(*fixture_frame, tmp_path, ("step", "stl"))
    export_artifacts(*fixture_frame, tmp_path, ("svg",))
    assert not (tmp_path / "step").exists()
    assert not (tmp_path / "stl").exists()
    assert report.read_text() == "retain validation evidence"


@pytest.mark.parametrize("formats", [("banana",), ()])
def test_rejects_invalid_format_before_writing(tmp_path, fixture_frame, formats):
    with pytest.raises(ValueError):
        export_artifacts(*fixture_frame, tmp_path, formats)
    assert not list(tmp_path.iterdir())


def test_selected_part_omits_aggregate_and_preserves_input_tree(tmp_path, fixture_frame):
    parts, profiles, assembly = fixture_frame
    children_before = tuple(assembly.children)
    labels_before = [part.label for part in parts.values()]
    export_artifacts(parts, profiles, assembly, tmp_path, ("step", "svg"), include_assembly=False)
    assert not (tmp_path / "step/fpv-frame.step").exists()
    assert not list((tmp_path / "svg").glob("assembly_*.svg"))
    assert (tmp_path / "step/arm.step").exists()
    assert tuple(assembly.children) == children_before
    assert [part.label for part in parts.values()] == labels_before


def test_metadata_tolerances_reach_real_mesher(tmp_path):
    from build123d import Cylinder

    cylinder = Cylinder(10, 5)
    parts = {"round": cylinder}
    frame = Compound(children=[cylinder])
    fine = tmp_path / "fine"
    coarse = tmp_path / "coarse"
    for output, tolerance in ((fine, 0.01), (coarse, 0.8)):
        export_artifacts(
            parts,
            {},
            frame,
            output,
            ("stl",),
            metadata={
                "parameters": {
                    "manufacturing": {
                        "linear_tolerance": tolerance,
                        "angular_tolerance": tolerance,
                    }
                },
                "preset": "test",
            },
        )
    fine_mesh = (fine / "stl/round.stl").read_bytes()
    coarse_mesh = (coarse / "stl/round.stl").read_bytes()
    assert struct.unpack_from("<I", fine_mesh, 80)[0] > struct.unpack_from("<I", coarse_mesh, 80)[0]
    manifest = json.loads((coarse / "manifest.json").read_text())
    assert manifest["mesh"]["linear_tolerance_mm"] == 0.8
    assert manifest["metadata"]["preset"] == "test"
    assert manifest["metadata"]["build123d_version"].startswith("0.11.")
    assert manifest["metadata"]["python_version"]
    assert manifest["metadata"]["version"]
    assert manifest["metadata"]["project_version"] == manifest["metadata"]["version"]


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_invalid_mesh_tolerance_writes_nothing(tmp_path, fixture_frame, bad):
    with pytest.raises(ValueError, match="finite positive"):
        export_artifacts(*fixture_frame, tmp_path, ("stl",), linear_tolerance=bad)
    assert not list(tmp_path.iterdir())


def test_failed_generation_preserves_existing_exports(tmp_path, fixture_frame, monkeypatch):
    import fpv_frame.export.artifacts as module

    export_artifacts(*fixture_frame, tmp_path, ("step",))
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    def fail(*args, **kwargs):
        raise RuntimeError("deliberate exporter failure")

    monkeypatch.setattr(module, "export_stl", fail)
    with pytest.raises(RuntimeError, match="deliberate"):
        export_artifacts(*fixture_frame, tmp_path, ("step", "stl"))
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


@pytest.mark.parametrize("source_dirty", [False, True])
def test_source_provenance_precedes_export_writes(
    tmp_path, fixture_frame, monkeypatch, source_dirty
):
    """Generated staging files must not turn a clean source revision into a dirty one."""
    import fpv_frame.export.artifacts as module

    output = tmp_path / "new-parent" / "dist"
    snapshots = []

    def snapshot():
        assert not output.parent.exists()
        snapshots.append(source_dirty)
        return {"git_commit": "source-revision", "git_dirty": source_dirty}

    monkeypatch.setattr(module, "_provenance", snapshot)
    export_artifacts(*fixture_frame, output, ("step",))
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["metadata"]["git_commit"] == "source-revision"
    assert manifest["metadata"]["git_dirty"] is source_dirty
    assert snapshots == [source_dirty]
