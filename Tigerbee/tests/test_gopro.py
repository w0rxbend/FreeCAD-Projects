import pytest
from build123d import Circle, Plane, Pos, extrude

from tigerbee.gopro import GoProParameters, build_gopro_holder, mounting_centers
from tigerbee.models import build_part


def test_mounting_axes_follow_existing_front_accessory_bores():
    assert set(mounting_centers()) == {(-28, 58), (28, 58), (-27, 91), (27, 91)}


def test_holder_locates_in_plate_without_carbon_interference():
    holder = build_gopro_holder()
    carbon = build_part("top-plate").translate((0, 0, -3))
    assert holder.is_valid and len(holder.solids()) == 1
    assert (holder & carbon).volume < 1e-6
    assert holder.bounding_box().min.Z == pytest.approx(-2)
    assert holder.bounding_box().max.Z == pytest.approx(25.5)
    for x, y in mounting_centers():
        shaft = Pos(x, y, -10) * extrude(Circle(1.55), amount=30)
        assert (holder & shaft).volume < 1e-6
        driver = Pos(x, y, 2) * extrude(Circle(3.15), amount=40)
        assert (holder & driver).volume < 1e-6


def test_pivot_passes_through_all_three_fingers():
    holder = build_gopro_holder()
    shaft = extrude(Plane.YZ * Pos(74.5, 18) * Circle(2.6), amount=50, both=True)
    assert (holder & shaft).volume < 1e-6


def test_raised_variant_preserves_plate_interface():
    holder = build_gopro_holder(GoProParameters(axle_height=28))
    assert holder.bounding_box().max.Z == pytest.approx(35.5)
    assert (holder & build_part("top-plate").translate((0, 0, -3))).volume < 1e-6


@pytest.mark.parametrize("height", [10, 40, float("nan")])
def test_invalid_height_is_rejected(height):
    with pytest.raises(ValueError):
        build_gopro_holder(GoProParameters(axle_height=height))


@pytest.mark.parametrize("angle", [-15, 0, 15, 30, 45, 60])
def test_camera_fingers_can_engage_and_tilt(angle):
    from build123d import Axis, Rectangle

    holder = build_gopro_holder()
    # Independent nominal two-finger coupon: R7.5, 3 mm thickness and 6.2 mm pitch.
    face = (Circle(7.5) + Pos(0, 5.75) * Rectangle(15, 11.5)).faces()[0]
    coupon = None
    for x in (-4.6, 1.6):
        finger = Pos(x, 74.5, 18) * extrude(Plane.YZ * face, amount=3, dir=(1, 0, 0))
        coupon = finger if coupon is None else coupon + finger
    coupon = coupon.rotate(Axis((0, 74.5, 18), (1, 0, 0)), angle)
    assert (holder & coupon).volume < 1e-6


def test_export_reopens_as_separate_printable_component(tmp_path):
    from build123d import import_step

    from tigerbee.gopro_export import export_gopro_holder

    report = export_gopro_holder(tmp_path, preview=False)
    part = import_step(tmp_path / "top-plate-gopro-holder.step")
    assert part.is_valid and len(part.solids()) == 1
    assert part.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
    assert report["fit"]["passed"]
    assert report["mesh_validation"]["valid"]


def test_fit_audit_rejects_shifted_mount():
    from tigerbee.gopro_export import audit_holder

    with pytest.raises(ValueError, match="Holder fit failed"):
        audit_holder(build_gopro_holder().translate((1, 0, 0)), GoProParameters())


def test_m5_hex_nut_fits_captive_seat():
    from math import sqrt

    from build123d import RegularPolygon

    nut = Plane.YZ * Pos(74.5, 18) * RegularPolygon(8 / sqrt(3), 6, rotation=30)
    witness = Pos(7.1, 0, 0) * extrude(nut, amount=4, dir=(1, 0, 0))
    assert (build_gopro_holder() & witness).volume < 1e-6


def test_registration_bosses_have_printable_wall_thickness():
    from build123d import GeomType

    feet = [
        face
        for face in build_gopro_holder().faces().filter_by(Plane.XY)
        if abs(face.center().Z + 2) < 1e-6
    ]
    assert len(feet) == 4
    for face in feet:
        radii = [e.radius for e in face.edges() if e.geom_type == GeomType.CIRCLE]
        assert max(radii) - min(radii) >= 0.7


@pytest.mark.parametrize("removed", ["all-fingers", "middle-finger"])
def test_fit_audit_requires_actual_pivot_bearings(removed):
    from build123d import Box

    from tigerbee.gopro_export import audit_holder

    holder = build_gopro_holder()
    width = 100 if removed == "all-fingers" else 3
    holder -= Pos(0, 74.5, 55) * Box(width, 100, 100)
    assert holder.is_valid and len(holder.solids()) == 1
    with pytest.raises(ValueError, match="Holder fit failed"):
        audit_holder(holder, GoProParameters())


def test_fit_audit_requires_clear_captive_nut_seat():
    from math import sqrt

    from build123d import RegularPolygon

    from tigerbee.gopro_export import audit_holder

    holder = build_gopro_holder()
    # Close the hex pocket while retaining the original clear M5 axle passage.
    plug = RegularPolygon(8.4 / sqrt(3), 6, rotation=30) - Circle(2.75)
    holder += Pos(7, 74.5, 18) * extrude(Plane.YZ * plug, amount=4.2, dir=(1, 0, 0))
    assert holder.is_valid and len(holder.solids()) == 1
    with pytest.raises(ValueError, match="Holder fit failed"):
        audit_holder(holder, GoProParameters())


@pytest.mark.parametrize("height", [18, 30])
def test_pivot_audit_accepts_both_supported_height_limits(height):
    from tigerbee.gopro_export import audit_holder

    parameters = GoProParameters(axle_height=height)
    assert audit_holder(build_gopro_holder(parameters), parameters)["passed"]
