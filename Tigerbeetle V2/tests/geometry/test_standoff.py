import math

import pytest
from build123d import Face, GeomType, Part

from fpv_frame.parameters.hardware import HardwareParameters
from fpv_frame.parts.standoff import build_standoff, standoff_profile


@pytest.mark.parametrize("outer,bore,height", [(5, 3, 25), (5, 3, 32), (7, 4, 18)])
def test_standoff_is_one_valid_annulus_with_an_open_axial_bore(outer, bore, height):
    hardware = HardwareParameters(bolt_diameter=bore, standoff_outer_diameter=outer)
    profile = standoff_profile(hardware)
    part = build_standoff(hardware, height)
    assert isinstance(profile, Face) and profile.is_valid
    assert isinstance(part, Part) and part.is_valid
    assert len(profile.inner_wires()) == 1
    bore_edge = profile.inner_wires()[0].edges()[0]
    assert bore_edge.geom_type == GeomType.CIRCLE
    assert bore_edge.radius == pytest.approx(bore / 2)
    assert profile.center().Z == pytest.approx(0)
    assert len(part.solids()) == 1
    expected_area = math.pi * (outer**2 - bore**2) / 4
    assert profile.area == pytest.approx(expected_area)
    assert part.volume == pytest.approx(expected_area * height)
    bounds = part.bounding_box()
    assert bounds.min.Z == pytest.approx(0)
    assert bounds.max.Z == pytest.approx(height)
    assert bounds.size.X == pytest.approx(outer)
    assert bounds.size.Y == pytest.approx(outer)
    assert not part.is_inside((0, 0, height / 2))
    assert part.is_inside(((outer + bore) / 4, 0, height / 2))


@pytest.mark.parametrize("height", [0, -1, float("nan"), float("inf"), True])
def test_standoff_rejects_invalid_height(height):
    with pytest.raises(ValueError):
        build_standoff(HardwareParameters(), height)
