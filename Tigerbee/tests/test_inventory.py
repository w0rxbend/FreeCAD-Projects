"""Committed deliverables must stay tied to their source and exported geometry."""

import hashlib
import json

import pytest

from tigerbee import inventory

# Frozen delivery contract, independent of model registries and verifier requirements.
DELIVERABLES = (
    "accessories/arm-type-1-protector-left.3mf",
    "accessories/arm-type-1-protector-left.FCStd",
    "accessories/arm-type-1-protector-left.json",
    "accessories/arm-type-1-protector-left.step",
    "accessories/arm-type-1-protector-left.stl",
    "accessories/arm-type-1-protector-left.svg",
    "accessories/arm-type-1-protector-right.3mf",
    "accessories/arm-type-1-protector-right.FCStd",
    "accessories/arm-type-1-protector-right.json",
    "accessories/arm-type-1-protector-right.step",
    "accessories/arm-type-1-protector-right.stl",
    "accessories/arm-type-1-protector-right.svg",
    "accessories/arm-type-2-protector-left.3mf",
    "accessories/arm-type-2-protector-left.FCStd",
    "accessories/arm-type-2-protector-left.json",
    "accessories/arm-type-2-protector-left.step",
    "accessories/arm-type-2-protector-left.stl",
    "accessories/arm-type-2-protector-left.svg",
    "accessories/arm-type-2-protector-right.3mf",
    "accessories/arm-type-2-protector-right.FCStd",
    "accessories/arm-type-2-protector-right.json",
    "accessories/arm-type-2-protector-right.step",
    "accessories/arm-type-2-protector-right.stl",
    "accessories/arm-type-2-protector-right.svg",
    "accessories/tigerbee-with-gopro-holder-isometric.svg",
    "accessories/tigerbee-with-gopro-holder-side.svg",
    "accessories/tigerbee-with-gopro-holder.FCStd",
    "accessories/tigerbee-with-gopro-holder.glb",
    "accessories/tigerbee-with-gopro-holder.json",
    "accessories/tigerbee-with-gopro-holder.step",
    "accessories/tigerbee-with-protectors-isometric.svg",
    "accessories/tigerbee-with-protectors-side.svg",
    "accessories/tigerbee-with-protectors.FCStd",
    "accessories/tigerbee-with-protectors.glb",
    "accessories/tigerbee-with-protectors.json",
    "accessories/tigerbee-with-protectors.step",
    "accessories/top-plate-gopro-holder.3mf",
    "accessories/top-plate-gopro-holder.FCStd",
    "accessories/top-plate-gopro-holder.json",
    "accessories/top-plate-gopro-holder.step",
    "accessories/top-plate-gopro-holder.stl",
    "accessories/top-plate-gopro-holder.svg",
    "assembly/assembly-report.json",
    "assembly/tigerbee-assembly.3mf",
    "assembly/tigerbee-assembly.FCStd",
    "assembly/tigerbee-assembly.glb",
    "assembly/tigerbee-assembly.step",
    "assembly/tigerbee-assembly.stl",
    "assembly/tigerbee-isometric.svg",
    "assembly/tigerbee-motor-layout.svg",
    "assembly/tigerbee-top.svg",
    "native-report.json",
    "parts/arm-type-1.3mf",
    "parts/arm-type-1.FCStd",
    "parts/arm-type-1.dxf",
    "parts/arm-type-1.json",
    "parts/arm-type-1.step",
    "parts/arm-type-1.stl",
    "parts/arm-type-1.svg",
    "parts/arm-type-2.3mf",
    "parts/arm-type-2.FCStd",
    "parts/arm-type-2.dxf",
    "parts/arm-type-2.json",
    "parts/arm-type-2.step",
    "parts/arm-type-2.stl",
    "parts/arm-type-2.svg",
    "parts/camera-plate.3mf",
    "parts/camera-plate.FCStd",
    "parts/camera-plate.dxf",
    "parts/camera-plate.json",
    "parts/camera-plate.step",
    "parts/camera-plate.stl",
    "parts/camera-plate.svg",
    "parts/rear-plate.3mf",
    "parts/rear-plate.FCStd",
    "parts/rear-plate.dxf",
    "parts/rear-plate.json",
    "parts/rear-plate.step",
    "parts/rear-plate.stl",
    "parts/rear-plate.svg",
    "parts/top-plate.3mf",
    "parts/top-plate.FCStd",
    "parts/top-plate.dxf",
    "parts/top-plate.json",
    "parts/top-plate.step",
    "parts/top-plate.stl",
    "parts/top-plate.svg",
)


def test_reject_stale_source_before_recording_native_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "source_digest", lambda: "current")
    assembly = tmp_path / "assembly"
    assembly.mkdir()
    (assembly / "assembly-report.json").write_text('{"source_sha256": "old"}')
    with pytest.raises(ValueError, match="stale"):
        inventory.write_inventory(tmp_path)
    assert not (tmp_path / "manifest.json").exists()


def test_reject_modified_step_before_recording_native_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "source_digest", lambda: "current")
    assembly = tmp_path / "assembly"
    assembly.mkdir()
    (assembly / "model.step").write_bytes(b"modified")
    (assembly / "assembly-report.json").write_text(
        json.dumps(
            {
                "source_sha256": "current",
                "file_sha256": {"model.step": hashlib.sha256(b"original").hexdigest()},
            }
        )
    )
    with pytest.raises(ValueError, match="changed since build"):
        inventory.write_inventory(tmp_path)


@pytest.fixture
def exported_inventory(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "source_digest", lambda: "current")
    hashes = {}
    for name in DELIVERABLES:
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"original")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"source_sha256": "current", "files": hashes}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return tmp_path, manifest


def test_verify_accepts_complete_delivery(exported_inventory):
    directory, _ = exported_inventory
    assert inventory.verify_inventory(directory) == 87


@pytest.mark.parametrize("failure", ["missing", "modified", "source"])
def test_verify_detects_stale_or_incomplete_deliverables(exported_inventory, monkeypatch, failure):
    directory, _ = exported_inventory
    path = directory / "parts/arm-type-1.step"
    if failure == "missing":
        path.unlink()
    elif failure == "modified":
        path.write_bytes(b"modified")
    else:
        monkeypatch.setattr(inventory, "source_digest", lambda: "changed")
    with pytest.raises(ValueError):
        inventory.verify_inventory(directory)


@pytest.mark.parametrize("name", DELIVERABLES)
def test_verify_rejects_export_deleted_from_disk_and_manifest(exported_inventory, name):
    directory, manifest = exported_inventory
    (directory / name).unlink()
    del manifest["files"][name]
    (directory / "manifest.json").write_text(json.dumps(manifest))

    with pytest.raises(ValueError) as error:
        inventory.verify_inventory(directory)
    assert str(error.value) == f"Required committed export missing from manifest: {name}"
