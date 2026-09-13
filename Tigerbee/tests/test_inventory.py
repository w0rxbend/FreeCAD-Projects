"""Committed deliverables must stay tied to their source and exported geometry."""

import hashlib
import json

import pytest

from tigerbee import inventory
from tigerbee.models import PARTS
from tigerbee.protectors import PROTECTORS


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


@pytest.mark.parametrize("failure", ["missing", "modified", "source", "unlisted"])
def test_verify_detects_stale_or_incomplete_deliverables(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(inventory, "source_digest", lambda: "current")
    names = [f"parts/{name}.{suffix}" for name in PARTS for suffix in ("3mf", "stl", "FCStd")]
    names += [f"assembly/tigerbee-assembly.{suffix}" for suffix in ("3mf", "stl", "FCStd")]
    names += [
        f"accessories/{name}.{suffix}"
        for name in PROTECTORS
        for suffix in ("step", "stl", "3mf", "FCStd", "svg", "json")
    ]
    names += [
        "accessories/tigerbee-with-protectors.step",
        "accessories/tigerbee-with-protectors.FCStd",
    ]
    hashes = {}
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"original")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"source_sha256": "current", "files": hashes}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    assert inventory.verify_inventory(tmp_path) == len(names)
    if failure == "missing":
        (tmp_path / names[0]).unlink()
    elif failure == "modified":
        (tmp_path / names[0]).write_bytes(b"modified")
    elif failure == "source":
        monkeypatch.setattr(inventory, "source_digest", lambda: "changed")
    else:
        del hashes[names[0]]
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        inventory.verify_inventory(tmp_path)
