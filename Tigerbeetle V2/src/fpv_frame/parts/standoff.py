"""Independent tubular hardware geometry in local XY with its lower face at Z=0."""

from build123d import Face, Part, Wire, extrude

from fpv_frame.parameters._validation import positive
from fpv_frame.parameters.hardware import HardwareParameters


def standoff_profile(hardware: HardwareParameters) -> Face:
    """Return the nominal annular profile; plate hole allowances do not apply here."""
    return Face(
        Wire.make_circle(hardware.standoff_outer_diameter / 2),
        [Wire.make_circle(hardware.bolt_diameter / 2)],
    )


def build_standoff(hardware: HardwareParameters, height: float) -> Part:
    """Extrude one open-bore standoff; assembly placement is the caller's concern."""
    positive("standoff height", height)
    return extrude(standoff_profile(hardware), amount=height, dir=(0, 0, 1))
