"""Reject disconnected, miscounted or non-solid manufacturing geometry."""

import pytest
from build123d import Box, Circle, Compound, Pos, Rectangle, extrude

from fpv_frame.validation.geometry import validate_profile, validate_solid


def test_closed_plate_with_hole_has_expected_area_volume_and_features() -> None:
    profile = Rectangle(20, 30) - Circle(2)
    validate_profile(profile, expected_holes=1)
    validate_solid(extrude(profile, amount=2))


def test_wrong_hole_count_is_fatal() -> None:
    with pytest.raises(ValueError, match="hole count"):
        validate_profile(Rectangle(20, 30), expected_holes=1)


def test_disconnected_profile_is_not_one_physical_part() -> None:
    profile = Compound(children=[Rectangle(10, 10), Pos(20, 0) * Rectangle(10, 10)])
    with pytest.raises(ValueError, match="one face"):
        validate_profile(profile)


def test_sheet_is_not_a_closed_solid() -> None:
    with pytest.raises(ValueError, match="one solid"):
        validate_solid(Rectangle(20, 30))


def test_multiple_solids_cannot_masquerade_as_one_part() -> None:
    with pytest.raises(ValueError, match="one solid"):
        validate_solid(Compound(children=[Box(1, 2, 3), Pos(10, 0) * Box(1, 2, 3)]))


def test_profile_must_be_in_the_manufacturing_xy_plane() -> None:
    with pytest.raises(ValueError, match="XY plane"):
        validate_profile(Pos(0, 0, 2) * Rectangle(20, 30))
