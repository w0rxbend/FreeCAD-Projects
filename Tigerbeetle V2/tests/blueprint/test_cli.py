"""The installed command exposes evidence without silently accepting damaged inputs."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_inspect_reports_native_sources_and_confirmed_thicknesses() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "fpv_frame.cli", "--root", str(ROOT), "inspect"],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report["sources"]["Scan_1.jpeg"]["size_px"] == [2480, 3508]
    assert report["confirmed_dimensions_mm"] == {"arm_thickness": 5, "plate_thickness": 2}
    assert report["page_calibration"]["pixels_per_mm"] > 11.8


def test_inspect_missing_evidence_has_nonzero_exit(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "fpv_frame.cli", "--root", str(tmp_path), "inspect"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "missing" in result.stderr


@pytest.mark.parametrize("command", ["build", "validate", "export", "drawing", "overlay"])
def test_geometry_commands_reject_missing_evidence(tmp_path: Path, command: str) -> None:
    arguments = [command, "scan-1"] if command == "overlay" else [command]
    result = subprocess.run(
        [sys.executable, "-m", "fpv_frame.cli", "--root", str(tmp_path), *arguments],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "missing" in result.stderr
    assert not (tmp_path / "dist").exists()
