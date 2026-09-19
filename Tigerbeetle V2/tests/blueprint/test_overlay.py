from pathlib import Path

import pytest

from fpv_frame.blueprint.workflow import reference_overlays
from fpv_frame.parameters.presets import get_preset

ROOT = Path(__file__).resolve().parents[2]


def test_every_traced_component_has_a_separate_registered_cad_overlay():
    scans = reference_overlays(get_preset(), ROOT)
    assert [p.name for p in scans["Scan_1"]] == ["scan1_body", "arm_a", "arm_b"]
    assert [p.name for p in scans["Scan_2"]] == ["scan2_broad", "scan2_long"]
    for arm, pixel_motor in zip(scans["Scan_1"][1:], ((490, 767), (1050, 2735)), strict=True):
        assert arm.calibration.to_pixels((0, 115)) == pytest.approx(pixel_motor, abs=10)
    # The matching central stack datum is on separate sheets, not page-position assembled.
    body, broad = scans["Scan_1"][0], scans["Scan_2"][0]
    assert body.calibration.to_pixels((0, 0))[0] > 1800
    assert broad.calibration.to_pixels((0, 0))[0] < 800
